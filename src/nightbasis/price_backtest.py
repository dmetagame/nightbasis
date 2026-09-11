"""Frozen price-only NightBasis fair-value backtest.

Workflow:
1. ``fit-is`` reads only IS-dated observations, writes the IS ledger/metrics,
   and freezes model coefficients plus immutable thresholds.
2. Commit the freeze artifact.
3. ``run-oos`` loads that artifact without refitting and writes the observed
   OOS ledger/metrics. Future OOS dates remain pending, never synthetic flats.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable

from nightbasis.audit_data import (
    CORE_SYMBOLS,
    IS_END,
    IS_START,
    NY,
    OOS_END,
    OOS_START,
    UTC,
    is_trading_date,
)


DECISION_TIME = dt.time(0, 0)
ENTRY_POSITION_WEIGHT = 0.04
WEEKNIGHT_Z = 1.0
WEEKEND_Z = 1.5
RIDGE_LAMBDA = 1e-6
COSTS_PER_SIDE_BPS = (15.0, 25.0, 37.5)
BASE_COST_BPS = 25.0


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_snapshot(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def load_audit(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def date_range(start: dt.date, end: dt.date) -> Iterable[dt.date]:
    cursor = start
    while cursor <= end:
        yield cursor
        cursor += dt.timedelta(days=1)


def night_kind(day: dt.date) -> str:
    previous = day - dt.timedelta(days=1)
    return "weeknight" if is_trading_date(previous) and is_trading_date(day) else "weekend_or_holiday"


def timestamp_ms(day: dt.date, clock: dt.time) -> int:
    return int(dt.datetime.combine(day, clock, NY).astimezone(UTC).timestamp() * 1000)


def bar_maps(snapshot: dict[str, Any]) -> dict[str, dict[int, dict[str, float]]]:
    return {
        symbol: {int(float(row["ts"])): row for row in rows}
        for symbol, rows in snapshot["bars"].items()
    }


def exact_open(bars: dict[int, dict[str, float]], timestamp: int) -> float | None:
    row = bars.get(timestamp)
    if not row:
        return None
    value = float(row["open"])
    return value if value > 0 else None


def log_return(start: float | None, end: float | None) -> float | None:
    if start is None or end is None or start <= 0 or end <= 0:
        return None
    return math.log(end / start)


def audit_maps(audit: dict[str, Any]) -> tuple[dict[str, dict[str, bool]], dict[str, dict[str, bool]]]:
    tradables = {
        item["symbol"]: {session["date"]: bool(session["usable"]) for session in item["sessions"]}
        for item in audit["tradables"]
        if item["symbol"] in CORE_SYMBOLS
    }
    factors = {
        item["symbol"]: {session["date"]: bool(session["usable"]) for session in item["sessions"]}
        for item in audit["factors"]
    }
    return tradables, factors


def build_observations(
    snapshot: dict[str, Any],
    audit: dict[str, Any],
    start: dt.date,
    end: dt.date,
) -> list[dict[str, Any]]:
    maps = bar_maps(snapshot)
    tradable_usable, factor_usable = audit_maps(audit)
    observations: list[dict[str, Any]] = []

    for day in date_range(start, end):
        date_text = day.isoformat()
        previous = day - dt.timedelta(days=1)
        kind = night_kind(day)
        start_ts = timestamp_ms(previous, dt.time(16, 15))
        decision_ts = timestamp_ms(day, DECISION_TIME)
        exit_ts = timestamp_ms(day, dt.time(9, 0))

        factor_choice: str | None = None
        if kind == "weeknight":
            if factor_usable.get("RQQQUSDT", {}).get(date_text, False):
                factor_choice = "RQQQUSDT"
            elif factor_usable.get("RSPYUSDT", {}).get(date_text, False):
                factor_choice = "RSPYUSDT"
        else:
            btc_ok = factor_usable.get("BTCUSDT", {}).get(date_text, False)
            eth_ok = factor_usable.get("ETHUSDT", {}).get(date_text, False)
            if btc_ok and eth_ok:
                factor_choice = "BTC_ETH"

        def factor_return(symbol: str) -> float | None:
            return log_return(exact_open(maps[symbol], start_ts), exact_open(maps[symbol], decision_ts))

        btc_return = factor_return("BTCUSDT")
        eth_return = factor_return("ETHUSDT")
        equity_return = factor_return(factor_choice) if factor_choice and factor_choice != "BTC_ETH" else None

        for symbol in CORE_SYMBOLS:
            target_start = exact_open(maps[symbol], start_ts)
            target_decision = exact_open(maps[symbol], decision_ts)
            target_exit = exact_open(maps[symbol], exit_ts)
            observed_return = log_return(target_start, target_decision)
            exit_return = log_return(target_decision, target_exit)
            usable = bool(
                tradable_usable.get(symbol, {}).get(date_text, False)
                and factor_choice
                and btc_return is not None
                and eth_return is not None
                and observed_return is not None
                and exit_return is not None
                and (kind != "weeknight" or equity_return is not None)
            )
            features = (
                [1.0, equity_return, btc_return, eth_return]
                if kind == "weeknight" and usable
                else [1.0, btc_return, eth_return]
                if kind == "weekend_or_holiday" and usable
                else None
            )
            observations.append(
                {
                    "date": date_text,
                    "kind": kind,
                    "symbol": symbol,
                    "usable": usable,
                    "factor_choice": factor_choice,
                    "features": features,
                    "observed_return": observed_return,
                    "exit_return": exit_return,
                }
            )
    return observations


def solve_linear(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [row[:] + [vector[index]] for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-15:
            raise ValueError("Singular regression system")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            multiple = augmented[row][column]
            augmented[row] = [
                value - multiple * base for value, base in zip(augmented[row], augmented[column])
            ]
    return [augmented[index][-1] for index in range(size)]


def fit_ridge(rows: list[dict[str, Any]]) -> list[float]:
    width = len(rows[0]["features"])
    matrix = [[0.0] * width for _ in range(width)]
    vector = [0.0] * width
    for row in rows:
        features = row["features"]
        target = row["observed_return"]
        for left in range(width):
            vector[left] += features[left] * target
            for right in range(width):
                matrix[left][right] += features[left] * features[right]
    for index in range(1, width):
        matrix[index][index] += RIDGE_LAMBDA
    matrix[0][0] += 1e-12
    return solve_linear(matrix, vector)


def predict(coefficients: list[float], features: list[float]) -> float:
    return sum(coefficient * feature for coefficient, feature in zip(coefficients, features))


def robust_scale(values: list[float]) -> float:
    center = statistics.median(values)
    mad = statistics.median(abs(value - center) for value in values)
    scaled = 1.4826 * mad
    if scaled > 1e-8:
        return scaled
    fallback = statistics.stdev(values) if len(values) > 1 else 0.0
    return max(fallback, 1e-6)


def fit_models(observations: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    models: dict[str, dict[str, Any]] = {}
    for symbol in CORE_SYMBOLS:
        rows = [
            row
            for row in observations
            if row["symbol"] == symbol and row["kind"] == "weeknight" and row["usable"]
        ]
        if len(rows) < 10:
            raise RuntimeError(f"Insufficient IS weeknight rows for {symbol}: {len(rows)}")
        coefficients = fit_ridge(rows)
        residuals = [row["observed_return"] - predict(coefficients, row["features"]) for row in rows]
        scale = robust_scale(residuals)
        models[f"{symbol}:weeknight"] = {
            "coefficients": coefficients,
            "residual_scale": scale,
            "training_rows": len(rows),
            "derivation": "IS weeknight ridge",
        }
        models[f"{symbol}:weekend_or_holiday"] = {
            "coefficients": [coefficients[0], coefficients[2], coefficients[3]],
            "residual_scale": scale,
            "training_rows": 0,
            "derivation": "BTC/ETH coefficients and scale inherited from frozen IS weeknight model",
        }
    return models


def make_trade(row: dict[str, Any], model: dict[str, Any], cost_bps: float) -> dict[str, Any] | None:
    if not row["usable"]:
        return None
    fair = predict(model["coefficients"], row["features"])
    scale = model["residual_scale"]
    z_score = (fair - row["observed_return"]) / scale
    threshold = WEEKNIGHT_Z if row["kind"] == "weeknight" else WEEKEND_Z
    no_weekend_washout = row["kind"] != "weekend_or_holiday" or row["observed_return"] >= 0
    enter = fair > 0 and z_score >= threshold and no_weekend_washout
    if not enter:
        return None
    gross_return = math.exp(row["exit_return"]) - 1
    net_return = gross_return - 2 * cost_bps / 10_000
    return {
        "date": row["date"],
        "kind": row["kind"],
        "symbol": row["symbol"],
        "factor_choice": row["factor_choice"],
        "fair_return": fair,
        "observed_return": row["observed_return"],
        "z_score": z_score,
        "gross_trade_return": gross_return,
        "cost_per_side_bps": cost_bps,
        "net_trade_return": net_return,
        "position_weight": ENTRY_POSITION_WEIGHT,
        "portfolio_contribution": ENTRY_POSITION_WEIGHT * net_return,
    }


def build_ledger(
    observations: list[dict[str, Any]],
    models: dict[str, dict[str, Any]],
    start: dt.date,
    end: dt.date,
    cost_bps: float,
    observed_through: dt.date,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    trades = []
    by_date: dict[str, list[dict[str, Any]]] = {}
    for row in observations:
        trade = make_trade(row, models[f"{row['symbol']}:{row['kind']}"], cost_bps)
        if trade:
            trades.append(trade)
            by_date.setdefault(row["date"], []).append(trade)

    daily = []
    for day in date_range(start, end):
        text = day.isoformat()
        if day > observed_through:
            daily.append({"date": text, "status": "pending", "return": None, "trades": None, "gross_exposure": None})
            continue
        day_trades = by_date.get(text, [])
        daily.append(
            {
                "date": text,
                "status": "traded" if day_trades else "flat",
                "return": sum(item["portfolio_contribution"] for item in day_trades),
                "trades": len(day_trades),
                "gross_exposure": len(day_trades) * ENTRY_POSITION_WEIGHT,
            }
        )
    return daily, trades


def max_drawdown(returns: list[float]) -> float:
    equity = 1.0
    peak = 1.0
    worst = 0.0
    for value in returns:
        equity *= 1 + value
        peak = max(peak, equity)
        worst = min(worst, equity / peak - 1)
    return worst


def metrics(daily: list[dict[str, Any]], trades: list[dict[str, Any]]) -> dict[str, Any]:
    observed = [row for row in daily if row["return"] is not None]
    returns = [float(row["return"]) for row in observed]
    count = len(returns)
    mean = statistics.mean(returns) if returns else 0.0
    volatility = statistics.stdev(returns) if len(returns) > 1 else 0.0
    downside = math.sqrt(sum(min(value, 0.0) ** 2 for value in returns) / count) if count else 0.0
    total = math.prod(1 + value for value in returns) - 1 if returns else 0.0
    annualized = (1 + total) ** (365 / count) - 1 if count and total > -1 else -1.0
    trade_returns = [item["net_trade_return"] for item in trades]
    return {
        "calendar_days_observed": count,
        "flat_days": sum(row["status"] == "flat" for row in observed),
        "traded_days": sum(row["status"] == "traded" for row in observed),
        "pending_days": sum(row["status"] == "pending" for row in daily),
        "total_return": total,
        "annualized_return": annualized,
        "annualized_volatility": volatility * math.sqrt(365),
        "sharpe": mean / volatility * math.sqrt(365) if volatility else None,
        "sortino": mean / downside * math.sqrt(365) if downside else None,
        "max_drawdown": max_drawdown(returns),
        "trade_count": len(trades),
        "win_rate": sum(value > 0 for value in trade_returns) / len(trade_returns) if trade_returns else None,
        "round_trip_turnover_nav": 2 * ENTRY_POSITION_WEIGHT * len(trades),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def fit_is(args: argparse.Namespace) -> int:
    snapshot = load_snapshot(args.snapshot)
    audit = load_audit(args.audit)
    observations = build_observations(snapshot, audit, IS_START, IS_END)
    models = fit_models(observations)
    daily, trades = build_ledger(observations, models, IS_START, IS_END, BASE_COST_BPS, IS_END)
    freeze = {
        "created_at": dt.datetime.now(UTC).isoformat(),
        "snapshot_sha256": sha256_file(args.snapshot),
        "audit_sha256": sha256_file(args.audit),
        "book": list(CORE_SYMBOLS),
        "factors": {"weeknight": ["RQQQUSDT", "RSPYUSDT", "BTCUSDT", "ETHUSDT"], "weekend_or_holiday": ["BTCUSDT", "ETHUSDT"]},
        "split": {"is_start": IS_START.isoformat(), "is_end": IS_END.isoformat(), "oos_start": OOS_START.isoformat(), "oos_end": OOS_END.isoformat()},
        "thresholds": {
            "decision_time_et": DECISION_TIME.isoformat(),
            "exit_time_et": "09:00:00",
            "weeknight_z": WEEKNIGHT_Z,
            "weekend_z": WEEKEND_Z,
            "weekend_observed_return_floor": 0.0,
            "fair_return_floor": 0.0,
            "position_weight": ENTRY_POSITION_WEIGHT,
            "costs_per_side_bps": list(COSTS_PER_SIDE_BPS),
            "base_cost_per_side_bps": BASE_COST_BPS,
            "ridge_lambda": RIDGE_LAMBDA,
        },
        "models": models,
    }
    freeze_without_hash = json.dumps(freeze, sort_keys=True, separators=(",", ":")).encode()
    freeze["freeze_sha256"] = hashlib.sha256(freeze_without_hash).hexdigest()
    write_json(args.freeze, freeze)
    write_csv(args.is_daily, daily)
    write_csv(args.is_trades, trades)
    scenarios = {}
    for cost in COSTS_PER_SIDE_BPS:
        scenario_daily, scenario_trades = build_ledger(observations, models, IS_START, IS_END, cost, IS_END)
        scenarios[str(cost)] = metrics(scenario_daily, scenario_trades)
    is_result = {"period": "IS", "cost_scenarios": scenarios}
    write_json(args.is_metrics, is_result)
    print(json.dumps({"freeze": str(args.freeze), "freeze_sha256": freeze["freeze_sha256"], "is_metrics": is_result}, indent=2))
    return 0


def run_oos(args: argparse.Namespace) -> int:
    snapshot = load_snapshot(args.snapshot)
    audit = load_audit(args.audit)
    freeze = json.loads(args.freeze.read_text())
    if freeze["snapshot_sha256"] != sha256_file(args.snapshot):
        raise RuntimeError("Snapshot hash differs from frozen IS artifact")
    if freeze["audit_sha256"] != sha256_file(args.audit):
        raise RuntimeError("Audit hash differs from frozen IS artifact")
    captured = dt.datetime.fromisoformat(snapshot["captured_at"]).astimezone(NY).date()
    observed_through = min(captured, OOS_END)
    observations = build_observations(snapshot, audit, OOS_START, observed_through)
    results: dict[str, Any] = {
        "period": "OOS_PROVISIONAL" if observed_through < OOS_END else "OOS_FINAL",
        "observed_through": observed_through.isoformat(),
        "freeze_sha256": freeze["freeze_sha256"],
        "cost_scenarios": {},
    }
    for cost in COSTS_PER_SIDE_BPS:
        daily, trades = build_ledger(observations, freeze["models"], OOS_START, OOS_END, cost, observed_through)
        results["cost_scenarios"][str(cost)] = metrics(daily, trades)
        if cost == BASE_COST_BPS:
            write_csv(args.oos_daily, daily)
            write_csv(args.oos_trades, trades)
    write_json(args.oos_metrics, results)
    print(json.dumps(results, indent=2))
    return 0


def common_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--snapshot", type=Path, default=Path("data/market-snapshot.json.gz"))
    parser.add_argument("--audit", type=Path, default=Path("reports/data-audit.json"))
    parser.add_argument("--freeze", type=Path, default=Path("reports/price-only-freeze.json"))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    fit = subparsers.add_parser("fit-is")
    common_parser(fit)
    fit.add_argument("--is-daily", type=Path, default=Path("reports/price-only-is-daily.csv"))
    fit.add_argument("--is-trades", type=Path, default=Path("reports/price-only-is-trades.csv"))
    fit.add_argument("--is-metrics", type=Path, default=Path("reports/price-only-is-metrics.json"))
    oos = subparsers.add_parser("run-oos")
    common_parser(oos)
    oos.add_argument("--oos-daily", type=Path, default=Path("reports/price-only-oos-daily.csv"))
    oos.add_argument("--oos-trades", type=Path, default=Path("reports/price-only-oos-trades.csv"))
    oos.add_argument("--oos-metrics", type=Path, default=Path("reports/price-only-oos-metrics.json"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return fit_is(args) if args.command == "fit-is" else run_oos(args)


if __name__ == "__main__":
    raise SystemExit(main())
