"""Audit Bitget rToken history before strategy development begins.

Historical Reality order books are whitelist-gated. This audit therefore keeps
observed live quoted spread separate from an OHLC-based Corwin-Schultz spread
proxy used to screen historical overnight sessions.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import gzip
import hashlib
import json
import math
import statistics
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo


API_BASE = "https://api.bitget.com"
NY = ZoneInfo("America/New_York")
UTC = dt.timezone.utc
REQUEST_LOCK = threading.Lock()
NEXT_REQUEST_AT = 0.0
MIN_REQUEST_INTERVAL_SECONDS = 0.15  # Conservative global cap after observed 429s.

CORE_SYMBOLS = (
    "RNVDAUSDT",
    "RTSLAUSDT",
    "RAAPLUSDT",
    "RGOOGLUSDT",
)
ADD_SYMBOLS = ("RAMDUSDT", "RCVXUSDT", "ROXYUSDT", "RMETAUSDT")
TRADABLE_SYMBOLS = CORE_SYMBOLS + ADD_SYMBOLS
EQUITY_FACTOR_SYMBOLS = ("RQQQUSDT", "RSPYUSDT")
CRYPTO_FACTOR_SYMBOLS = ("BTCUSDT", "ETHUSDT")
FACTOR_SYMBOLS = EQUITY_FACTOR_SYMBOLS + CRYPTO_FACTOR_SYMBOLS
IS_START = dt.date(2026, 6, 2)
IS_END = dt.date(2026, 8, 19)
OOS_START = dt.date(2026, 8, 20)
OOS_END = dt.date(2026, 9, 18)

# NYSE full-day closures inside the native rToken history available at audit.
NYSE_HOLIDAYS_2026 = {
    dt.date(2026, 6, 19),
    dt.date(2026, 7, 3),
    dt.date(2026, 9, 7),
}
BAR_MINUTES = 15


def median(values: Iterable[float]) -> float | None:
    values = list(values)
    return statistics.median(values) if values else None


def iso_from_ms(value: int) -> str:
    return dt.datetime.fromtimestamp(value / 1000, UTC).isoformat()


def get_json(path: str, params: dict[str, Any], attempts: int = 8) -> dict[str, Any]:
    global NEXT_REQUEST_AT
    url = f"{API_BASE}{path}?{urllib.parse.urlencode(params)}"
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with REQUEST_LOCK:
                delay = NEXT_REQUEST_AT - time.monotonic()
                if delay > 0:
                    time.sleep(delay)
                NEXT_REQUEST_AT = time.monotonic() + MIN_REQUEST_INTERVAL_SECONDS
            request = urllib.request.Request(url, headers={"User-Agent": "nightbasis-audit/0.1"})
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.load(response)
            if payload.get("code") != "00000":
                raise RuntimeError(f"Bitget error for {url}: {payload}")
            return payload
        except (OSError, TimeoutError, urllib.error.URLError, RuntimeError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                retry_after = 0.0
                if isinstance(exc, urllib.error.HTTPError) and exc.code == 429:
                    retry_after = float(exc.headers.get("Retry-After", 2.0))
                time.sleep(max(retry_after, 0.5 * (2**attempt)))
    raise RuntimeError(f"Request failed after {attempts} attempts: {url}") from last_error


def fetch_instruments() -> dict[str, dict[str, Any]]:
    payload = get_json("/api/v3/market/instruments", {"category": "SPOT"})
    return {item["symbol"].upper(): item for item in payload["data"]}


def history_chunks(start_ms: int, end_ms: int) -> list[tuple[int, int]]:
    # Keep every response below the 100-row endpoint limit. One bar overlap is
    # intentional; rows are deduplicated by timestamp after collection.
    step_ms = 99 * BAR_MINUTES * 60 * 1000
    chunks: list[tuple[int, int]] = []
    cursor = start_ms
    while cursor < end_ms:
        chunk_end = min(cursor + step_ms, end_ms)
        chunks.append((cursor, chunk_end))
        cursor = chunk_end
    return chunks


def fetch_history(symbols: Iterable[str], start_ms: int, end_ms: int) -> dict[str, list[dict[str, float]]]:
    jobs = [(symbol, left, right) for symbol in symbols for left, right in history_chunks(start_ms, end_ms)]

    def fetch(job: tuple[str, int, int]) -> tuple[str, list[list[str]]]:
        symbol, left, right = job
        payload = get_json(
            "/api/v3/market/history-candles",
            {
                "category": "SPOT",
                "symbol": symbol,
                "interval": "15m",
                "startTime": left,
                "endTime": right,
                "type": "market",
                "limit": 100,
            },
        )
        return symbol, payload["data"]

    raw: dict[str, dict[int, dict[str, float]]] = defaultdict(dict)
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for symbol, rows in pool.map(fetch, jobs):
            for row in rows:
                if len(row) < 7:
                    continue
                ts = int(row[0])
                raw[symbol][ts] = {
                    "ts": float(ts),
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": float(row[5] or 0),
                    "turnover": float(row[6] or 0),
                }
    return {symbol: [rows[key] for key in sorted(rows)] for symbol, rows in raw.items()}


def fetch_ticker_samples(symbols: Iterable[str], samples: int, interval_seconds: float) -> dict[str, list[dict[str, float]]]:
    wanted = set(symbols)
    result: dict[str, list[dict[str, float]]] = defaultdict(list)
    for index in range(samples):
        payload = get_json("/api/v3/market/tickers", {"category": "SPOT"})
        for item in payload["data"]:
            symbol = item.get("symbol", "").upper()
            if symbol not in wanted:
                continue
            bid = float(item.get("bid1Price") or 0)
            ask = float(item.get("ask1Price") or 0)
            mid = (bid + ask) / 2 if bid > 0 and ask > 0 else 0
            result[symbol].append(
                {
                    "spread_bps": ((ask - bid) / mid * 10_000) if mid else math.inf,
                    "platform_turnover_24h": float(item.get("platformTurnover24h") or 0),
                }
            )
        if index + 1 < samples:
            time.sleep(interval_seconds)
    return result


def write_snapshot(
    path: Path,
    captured_at: dt.datetime,
    instruments: dict[str, dict[str, Any]],
    histories: dict[str, list[dict[str, float]]],
) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "captured_at": captured_at.isoformat(),
        "bar_interval": "15m",
        "source": f"{API_BASE}/api/v3/market/history-candles",
        "instruments": {symbol: instruments[symbol] for symbol in histories},
        "bars": histories,
    }
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(payload, handle, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_trading_date(day: dt.date) -> bool:
    return day.weekday() < 5 and day not in NYSE_HOLIDAYS_2026


def trading_dates(start: dt.date, end: dt.date) -> list[dt.date]:
    dates = []
    cursor = start
    while cursor <= end:
        if is_trading_date(cursor):
            dates.append(cursor)
        cursor += dt.timedelta(days=1)
    return dates


def session_windows(start: dt.date, end: dt.date, now: dt.datetime) -> list[tuple[dt.date, dt.datetime, dt.datetime, str]]:
    windows = []
    target = start
    while target <= end:
        previous = target - dt.timedelta(days=1)
        left = dt.datetime.combine(previous, dt.time(16, 15), NY).astimezone(UTC)
        right = dt.datetime.combine(target, dt.time(9, 0), NY).astimezone(UTC)
        if right <= now:
            kind = "weeknight" if is_trading_date(previous) and is_trading_date(target) else "weekend_or_holiday"
            windows.append((target, left, right, kind))
        target += dt.timedelta(days=1)
    return windows


def corwin_schultz_spread_bps(previous: dict[str, float], current: dict[str, float]) -> float | None:
    if min(previous["low"], current["low"]) <= 0:
        return None
    beta = math.log(previous["high"] / previous["low"]) ** 2 + math.log(current["high"] / current["low"]) ** 2
    high_two = max(previous["high"], current["high"])
    low_two = min(previous["low"], current["low"])
    gamma = math.log(high_two / low_two) ** 2
    denominator = 3 - 2 * math.sqrt(2)
    alpha = (math.sqrt(2 * beta) - math.sqrt(beta)) / denominator - math.sqrt(gamma / denominator)
    alpha = max(0.0, alpha)
    spread = 2 * (math.exp(alpha) - 1) / (1 + math.exp(alpha))
    return spread * 10_000


def bars_in_window(bars: list[dict[str, float]], left: dt.datetime, right: dt.datetime) -> list[dict[str, float]]:
    left_ms = left.timestamp() * 1000
    right_ms = right.timestamp() * 1000
    return [bar for bar in bars if left_ms <= bar["ts"] < right_ms]


def audit_symbol(
    symbol: str,
    bars: list[dict[str, float]],
    windows: list[tuple[dt.date, dt.datetime, dt.datetime, str]],
    ticker_samples: list[dict[str, float]],
    launch_ms: int,
    spread_limit_bps: float,
) -> tuple[dict[str, Any], set[str]]:
    positive = [bar for bar in bars if bar["volume"] > 0 and bar["ts"] >= launch_ms]
    first_live = iso_from_ms(int(positive[0]["ts"])) if positive else None
    sessions: list[dict[str, Any]] = []
    usable_dates: set[str] = set()

    for target, left, right, kind in windows:
        if right.timestamp() * 1000 < launch_ms:
            continue
        selected = bars_in_window(bars, left, right)
        expected = max(1, round((right - left).total_seconds() / (BAR_MINUTES * 60)))
        coverage = len(selected) / expected
        volume = sum(row["volume"] for row in selected)
        turnover = sum(row["turnover"] for row in selected)
        spread_estimates = [
            value
            for value in (
                corwin_schultz_spread_bps(selected[index - 1], selected[index])
                for index in range(1, len(selected))
            )
            if value is not None
        ]
        spread_proxy = median(spread_estimates)
        usable = bool(
            coverage >= 0.80
            and volume > 0
            and spread_proxy is not None
            and spread_proxy <= spread_limit_bps
        )
        date_text = target.isoformat()
        if usable:
            usable_dates.add(date_text)
        sessions.append(
            {
                "date": date_text,
                "kind": kind,
                "coverage": coverage,
                "volume": volume,
                "turnover": turnover,
                "spread_proxy_bps": spread_proxy,
                "usable": usable,
            }
        )

    observed_sessions = len(sessions)
    zero_volume_sessions = sum(item["volume"] <= 0 for item in sessions)
    quote_spreads = [item["spread_bps"] for item in ticker_samples if math.isfinite(item["spread_bps"])]
    platform_turnovers = [item["platform_turnover_24h"] for item in ticker_samples]
    report = {
        "symbol": symbol,
        "first_live_volume_at": first_live,
        "observed_sessions": observed_sessions,
        "zero_volume_sessions": zero_volume_sessions,
        "zero_volume_fraction": zero_volume_sessions / observed_sessions if observed_sessions else 1.0,
        "usable_sessions": len(usable_dates),
        "median_session_turnover": median(item["turnover"] for item in sessions if item["volume"] > 0),
        "median_historical_spread_proxy_bps": median(
            item["spread_proxy_bps"] for item in sessions if item["spread_proxy_bps"] is not None
        ),
        "median_live_platform_turnover_24h": median(platform_turnovers),
        "median_live_quoted_spread_bps": median(quote_spreads),
        "sessions": sessions,
    }
    return report, usable_dates


def format_number(value: float | None, digits: int = 2) -> str:
    return "n/a" if value is None else f"{value:,.{digits}f}"


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# NightBasis Day-1 Data Audit",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        f"Observed market data ends at `{report['observed_through']}`; the frozen OOS window ends "
        f"at `{report['split']['oos_end']}`. Future days are counted in the frozen daily-return "
        "calendar but are not treated as observed.",
        "",
        "Historical spread is a Corwin-Schultz estimate from 15-minute OHLC, not an observed "
        "order-book spread. Median quoted spread and platform turnover are repeated live ticker snapshots.",
        "",
        "| Tier | Symbol | First live volume | Zero-volume sessions | Usable sessions | Median platform turnover (24h) | Median quoted spread | Historical spread proxy |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in report["tradables"]:
        first = item["first_live_volume_at"][:10] if item["first_live_volume_at"] else "n/a"
        lines.append(
            f"| {item['tier']} | {item['symbol']} | {first} | {item['zero_volume_fraction']:.1%} | "
            f"{item['usable_sessions']} | ${format_number(item['median_live_platform_turnover_24h'], 0)} | "
            f"{format_number(item['median_live_quoted_spread_bps'])} bps | "
            f"{format_number(item['median_historical_spread_proxy_bps'])} bps |"
        )
    lines.extend(
        [
            "",
            f"**Strategy days, core + add:** {report['strategy_days']['core_plus_add']}",
            "",
            f"- Weeknight: {report['strategy_days']['core_plus_add_weeknight']}",
            f"- Weekend/holiday: {report['strategy_days']['core_plus_add_weekend_or_holiday']}",
            "",
            f"**Strategy days, core only:** {report['strategy_days']['core_only']}",
            "",
            f"- Weeknight: {report['strategy_days']['core_only_weeknight']}",
            f"- Weekend/holiday: {report['strategy_days']['core_only_weekend_or_holiday']}",
            "",
            f"**Incremental days supplied by add tier:** {report['strategy_days']['incremental_add_days']}",
            "",
            f"**IS daily-return calendar:** {report['split']['is_days_including_flats']} days "
            f"(`{report['split']['is_start']}` through `{report['split']['is_end']}`)",
            "",
            f"**OOS daily-return calendar:** {report['split']['oos_days_including_flats']} days "
            f"(`{report['split']['oos_start']}` through `{report['split']['oos_end']}`); "
            f"{report['split']['oos_days_observed']} observed and {report['split']['oos_days_future']} future as of audit",
            "",
            f"**Recommendation:** `{report['recommendation']['choice']}` — {report['recommendation']['reason']}",
            "",
            f"**Audit result:** {report['status']}",
            "",
        ]
    )
    lines.extend(["", "## Factor-only instruments", ""])
    for item in report["factors"]:
        lines.append(
            f"- `{item['symbol']}` ({item['factor_role']}): {item['usable_sessions']} raw usable sessions; "
            f"{item['zero_volume_fraction']:.1%} zero-volume sessions."
        )
    lines.append("")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> dict[str, Any]:
    now = dt.datetime.now(UTC)
    start = IS_START
    requested_end = OOS_END
    observed_end = min(requested_end, now.astimezone(NY).date())
    symbols = TRADABLE_SYMBOLS + FACTOR_SYMBOLS
    instruments = fetch_instruments()

    missing = [symbol for symbol in symbols if symbol not in instruments]
    if missing:
        raise RuntimeError(f"Missing instruments: {missing}")
    reality_symbols = set(TRADABLE_SYMBOLS + EQUITY_FACTOR_SYMBOLS)
    invalid = [symbol for symbol in symbols if instruments[symbol].get("status") != "online"]
    invalid.extend(symbol for symbol in reality_symbols if instruments[symbol].get("isReality") != "yes")
    if invalid:
        raise RuntimeError(f"Invalid or offline instruments: {sorted(set(invalid))}")

    fetch_start = start - dt.timedelta(days=7)
    start_ms = int(dt.datetime.combine(fetch_start, dt.time(0), UTC).timestamp() * 1000)
    end_ms = int(now.timestamp() * 1000)
    histories = fetch_history(symbols, start_ms, end_ms)
    # The main fetch begins one week before IS, which is sufficient for every
    # frozen tradable except any instrument launched earlier. Fetch only those
    # short early segments so "first live volume" is not a fetch-window artifact.
    for symbol in TRADABLE_SYMBOLS:
        launch_ms = int(instruments[symbol]["launchTime"])
        if launch_ms < start_ms:
            early = fetch_history((symbol,), launch_ms, start_ms).get(symbol, [])
            combined = {int(bar["ts"]): bar for bar in early + histories.get(symbol, [])}
            histories[symbol] = [combined[key] for key in sorted(combined)]
    snapshot_sha256 = write_snapshot(args.snapshot, now, instruments, histories)
    tickers = fetch_ticker_samples(symbols, args.ticker_samples, args.ticker_interval)
    windows = session_windows(start, observed_end, now)

    reports: dict[str, dict[str, Any]] = {}
    usable: dict[str, set[str]] = {}
    for symbol in symbols:
        item, dates = audit_symbol(
            symbol,
            histories.get(symbol, []),
            windows,
            tickers.get(symbol, []),
            int(instruments[symbol]["launchTime"]),
            args.spread_limit_bps,
        )
        item["launch_at"] = iso_from_ms(int(instruments[symbol]["launchTime"]))
        reports[symbol] = item
        usable[symbol] = dates

    equity_factor_dates = usable["RQQQUSDT"] | usable["RSPYUSDT"]
    crypto_factor_dates = usable["BTCUSDT"] & usable["ETHUSDT"]
    date_kind = {target.isoformat(): kind for target, _, _, kind in windows}
    permitted_factor_dates = {
        date_text
        for date_text, kind in date_kind.items()
        if (kind == "weeknight" and date_text in equity_factor_dates)
        or (kind == "weekend_or_holiday" and date_text in crypto_factor_dates)
    }
    for symbol in TRADABLE_SYMBOLS:
        raw_dates = usable[symbol]
        final_dates = raw_dates & permitted_factor_dates
        reports[symbol]["raw_usable_sessions"] = len(raw_dates)
        reports[symbol]["usable_sessions"] = len(final_dates)
        reports[symbol]["tier"] = "core" if symbol in CORE_SYMBOLS else "add"
        for session in reports[symbol]["sessions"]:
            session["raw_usable"] = session["usable"]
            factor_available = session["date"] in permitted_factor_dates
            session["factor_available"] = factor_available
            session["usable"] = session["raw_usable"] and factor_available
        usable[symbol] = final_dates

    factor_roles = {
        "RQQQUSDT": "primary equity factor",
        "RSPYUSDT": "fallback equity factor",
        "BTCUSDT": "supplementary crypto factor",
        "ETHUSDT": "supplementary crypto factor",
    }
    for symbol in FACTOR_SYMBOLS:
        reports[symbol]["factor_role"] = factor_roles[symbol]

    core_dates = set().union(*(usable[symbol] for symbol in CORE_SYMBOLS))
    add_dates = set().union(*(usable[symbol] for symbol in ADD_SYMBOLS))
    strategy_dates = core_dates | add_dates
    incremental_add_dates = add_dates - core_dates
    weeknight_strategy_dates = {day for day in strategy_dates if date_kind[day] == "weeknight"}
    weekend_strategy_dates = {day for day in strategy_dates if date_kind[day] == "weekend_or_holiday"}
    core_weeknight_dates = {day for day in core_dates if date_kind[day] == "weeknight"}
    core_weekend_dates = {day for day in core_dates if date_kind[day] == "weekend_or_holiday"}
    healthy_adds = [symbol for symbol in ADD_SYMBOLS if reports[symbol]["usable_sessions"] >= 30]
    if len(healthy_adds) >= 3 and len(incremental_add_dates) >= 3:
        recommendation = {
            "choice": "keep-add",
            "reason": (
                f"{len(healthy_adds)} add-tier names each provide at least 30 usable sessions; "
                f"the tier contributes {len(incremental_add_dates)} unique strategy days and broadens cross-sectional choice."
            ),
        }
    else:
        recommendation = {
            "choice": "core-only",
            "reason": (
                f"The add tier supplies only {len(incremental_add_dates)} unique strategy days; "
                "it does not improve calendar coverage and adds execution/model-selection complexity."
            ),
        }

    is_days = (IS_END - IS_START).days + 1
    oos_days = (OOS_END - OOS_START).days + 1
    observed_oos_end = min(observed_end, OOS_END)
    observed_oos_days = max(0, (observed_oos_end - OOS_START).days + 1)
    split = {
        "is_start": IS_START.isoformat(),
        "is_end": IS_END.isoformat(),
        "is_days_including_flats": is_days,
        "oos_start": OOS_START.isoformat(),
        "oos_end": OOS_END.isoformat(),
        "oos_days_including_flats": oos_days,
        "oos_days_observed": observed_oos_days,
        "oos_days_future": oos_days - observed_oos_days,
    }
    status = "PASS" if len(strategy_dates) >= args.min_strategy_days else "DESK_CONTINGENCY"

    return {
        "generated_at": now.isoformat(),
        "status": status,
        "definitions": {
            "session": "16:15 ET after the previous NYSE session through 09:00 ET of the target NYSE session",
            "zero_volume_fraction": "Fraction of post-launch completed overnight sessions with aggregate API candle volume equal to zero",
            "median_turnover": "Median platformTurnover24h across repeated live ticker snapshots",
            "median_spread": "Median top-of-book quoted spread across repeated live ticker snapshots",
            "historical_spread_proxy": "Median Corwin-Schultz estimate from 15m OHLC bars; not observed bid/ask",
            "usable_session": f">=80% 15m-bar coverage, nonzero aggregate volume, and historical spread proxy <= {args.spread_limit_bps} bps; weeknights additionally require rQQQ or rSPY, weekend/holiday nights require BTC and ETH",
            "daily_returns": "Every calendar day in the frozen split is retained; days without a position have zero strategy return",
        },
        "thresholds": {
            "min_coverage": 0.80,
            "max_historical_spread_proxy_bps": args.spread_limit_bps,
            "min_strategy_days": args.min_strategy_days,
        },
        "observed_through": observed_end.isoformat(),
        "market_snapshot": {"path": str(args.snapshot), "sha256": snapshot_sha256},
        "frozen_book": {
            "core": list(CORE_SYMBOLS),
            "add": list(ADD_SYMBOLS),
            "factors": list(FACTOR_SYMBOLS),
        },
        "strategy_days": {
            "core_plus_add": len(strategy_dates),
            "core_plus_add_weeknight": len(weeknight_strategy_dates),
            "core_plus_add_weekend_or_holiday": len(weekend_strategy_dates),
            "core_only": len(core_dates),
            "core_only_weeknight": len(core_weeknight_dates),
            "core_only_weekend_or_holiday": len(core_weekend_dates),
            "incremental_add_days": len(incremental_add_dates),
            "core_plus_add_is": sum(IS_START.isoformat() <= day <= IS_END.isoformat() for day in strategy_dates),
            "core_plus_add_oos_observed": sum(OOS_START.isoformat() <= day <= observed_end.isoformat() for day in strategy_dates),
        },
        "split": split,
        "recommendation": recommendation,
        "tradables": [reports[symbol] for symbol in TRADABLE_SYMBOLS],
        "factors": [reports[symbol] for symbol in FACTOR_SYMBOLS],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reports/data-audit.json"))
    parser.add_argument("--markdown", type=Path, default=Path("reports/data-audit.md"))
    parser.add_argument("--snapshot", type=Path, default=Path("data/market-snapshot.json.gz"))
    parser.add_argument("--ticker-samples", type=int, default=12)
    parser.add_argument("--ticker-interval", type=float, default=2.0)
    parser.add_argument("--spread-limit-bps", type=float, default=20.0)
    parser.add_argument("--min-strategy-days", type=int, default=60)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.markdown.write_text(markdown_report(report))
    print(markdown_report(report))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
