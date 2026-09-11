"""Audit Bitget rToken history before strategy development begins.

Historical Reality order books are whitelist-gated. This audit therefore keeps
observed live quoted spread separate from an OHLC-based Corwin-Schultz spread
proxy used to screen historical overnight sessions.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
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
MIN_REQUEST_INTERVAL_SECONDS = 0.125  # 8 requests/sec, below documented 20/sec/IP.

TRADABLE_SYMBOLS = (
    "RAAPLUSDT",
    "RAMDUSDT",
    "RCRCLUSDT",
    "RCVXUSDT",
    "RGOOGLUSDT",
    "RINTCUSDT",
    "RMETAUSDT",
    "RMRVLUSDT",
    "RMSTRUSDT",
    "RMUUSDT",
    "RNVDAUSDT",
    "RORCLUSDT",
    "ROXYUSDT",
    "RTSLAUSDT",
    "RXOMUSDT",
)
FACTOR_SYMBOLS = ("RSPYUSDT", "RQQQUSDT")

# NYSE full-day closures inside the native rToken history available at audit.
NYSE_HOLIDAYS_2026 = {
    dt.date(2026, 6, 19),
    dt.date(2026, 7, 3),
    dt.date(2026, 9, 7),
}
NYSE_EARLY_CLOSES_2026 = {dt.date(2026, 7, 2): dt.time(13, 0)}


def median(values: Iterable[float]) -> float | None:
    values = list(values)
    return statistics.median(values) if values else None


def iso_from_ms(value: int) -> str:
    return dt.datetime.fromtimestamp(value / 1000, UTC).isoformat()


def get_json(path: str, params: dict[str, Any], attempts: int = 5) -> dict[str, Any]:
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
    # Keep every response below the 100-row endpoint limit. One hour overlap is
    # intentional; rows are deduplicated by timestamp after collection.
    step_ms = 99 * 60 * 60 * 1000
    chunks: list[tuple[int, int]] = []
    cursor = start_ms
    while cursor < end_ms:
        chunk_end = min(cursor + step_ms, end_ms)
        chunks.append((cursor, chunk_end))
        cursor = chunk_end
    return chunks


def fetch_hourly_history(symbols: Iterable[str], start_ms: int, end_ms: int) -> dict[str, list[dict[str, float]]]:
    jobs = [(symbol, left, right) for symbol in symbols for left, right in history_chunks(start_ms, end_ms)]

    def fetch(job: tuple[str, int, int]) -> tuple[str, list[list[str]]]:
        symbol, left, right = job
        payload = get_json(
            "/api/v3/market/history-candles",
            {
                "category": "SPOT",
                "symbol": symbol,
                "interval": "1H",
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


def session_windows(start: dt.date, end: dt.date, now: dt.datetime) -> list[tuple[dt.date, dt.datetime, dt.datetime]]:
    dates = trading_dates(start - dt.timedelta(days=7), end)
    windows = []
    for index in range(1, len(dates)):
        target = dates[index]
        if target < start:
            continue
        previous = dates[index - 1]
        close_time = NYSE_EARLY_CLOSES_2026.get(previous, dt.time(16, 0))
        left = dt.datetime.combine(previous, close_time, NY).astimezone(UTC)
        right = dt.datetime.combine(target, dt.time(9, 30), NY).astimezone(UTC)
        if right <= now:
            windows.append((target, left, right))
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
    windows: list[tuple[dt.date, dt.datetime, dt.datetime]],
    ticker_samples: list[dict[str, float]],
    launch_ms: int,
    spread_limit_bps: float,
) -> tuple[dict[str, Any], set[str]]:
    positive = [bar for bar in bars if bar["volume"] > 0]
    first_live = iso_from_ms(int(positive[0]["ts"])) if positive else None
    sessions: list[dict[str, Any]] = []
    usable_dates: set[str] = set()

    for target, left, right in windows:
        if right.timestamp() * 1000 < launch_ms:
            continue
        selected = bars_in_window(bars, left, right)
        expected = max(1, round((right - left).total_seconds() / 3600))
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
        "Historical spread is a Corwin-Schultz OHLC estimate, not an observed order-book spread. "
        "Median quoted spread and platform turnover are repeated live ticker snapshots.",
        "",
        "| Symbol | First live volume | Zero-volume sessions | Usable sessions | Median platform turnover (24h) | Median quoted spread | Historical spread proxy | Eligible |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | :---: |",
    ]
    for item in report["tradables"]:
        first = item["first_live_volume_at"][:10] if item["first_live_volume_at"] else "n/a"
        lines.append(
            f"| {item['symbol']} | {first} | {item['zero_volume_fraction']:.1%} | "
            f"{item['usable_sessions']} | ${format_number(item['median_live_platform_turnover_24h'], 0)} | "
            f"{format_number(item['median_live_quoted_spread_bps'])} bps | "
            f"{format_number(item['median_historical_spread_proxy_bps'])} bps | "
            f"{'yes' if item['eligible'] else 'no'} |"
        )
    lines.extend(
        [
            "",
            f"**Eligible book:** {', '.join(report['eligible_book']) if report['eligible_book'] else 'none'}",
            "",
            f"**Eligible tradables:** {len(report['eligible_book'])} / {report['thresholds']['min_eligible_assets']} required",
            "",
            f"**Common usable sessions:** {report['split']['common_usable_sessions']}",
            "",
            f"**Audit result:** {report['status']}",
            "",
        ]
    )
    if report["split"].get("is_start"):
        lines.append(
            f"Provisional split from audited sessions: IS `{report['split']['is_start']}` through "
            f"`{report['split']['is_end']}` ({report['split']['is_sessions']} sessions); OOS "
            f"`{report['split']['oos_start']}` through `{report['split']['oos_end']}` "
            f"({report['split']['oos_sessions']} sessions)."
        )
    else:
        lines.append(f"No valid split: {report['split']['reason']}")
    lines.extend(["", "## Factor-only instruments", ""])
    for item in report["factors"]:
        lines.append(
            f"- `{item['symbol']}`: {item['usable_sessions']} usable sessions; "
            f"{item['zero_volume_fraction']:.1%} zero-volume sessions."
        )
    lines.append("")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> dict[str, Any]:
    now = dt.datetime.now(UTC)
    start = dt.date.fromisoformat(args.start)
    end = min(dt.date.fromisoformat(args.end) if args.end else now.date(), now.date())
    symbols = TRADABLE_SYMBOLS + FACTOR_SYMBOLS
    instruments = fetch_instruments()

    missing = [symbol for symbol in symbols if symbol not in instruments]
    if missing:
        raise RuntimeError(f"Missing instruments: {missing}")
    invalid = [
        symbol
        for symbol in symbols
        if instruments[symbol].get("isReality") != "yes" or instruments[symbol].get("status") != "online"
    ]
    if invalid:
        raise RuntimeError(f"Not online Reality instruments: {invalid}")

    start_ms = int(dt.datetime.combine(start, dt.time(0), UTC).timestamp() * 1000)
    end_ms = int(now.timestamp() * 1000)
    histories = fetch_hourly_history(symbols, start_ms, end_ms)
    tickers = fetch_ticker_samples(symbols, args.ticker_samples, args.ticker_interval)
    windows = session_windows(start, end, now)

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

    eligible = []
    for symbol in TRADABLE_SYMBOLS:
        item = reports[symbol]
        item["eligible"] = bool(
            item["usable_sessions"] >= args.min_usable_sessions
            and item["zero_volume_fraction"] <= args.max_zero_volume_fraction
            and (item["median_live_platform_turnover_24h"] or 0) >= args.min_platform_turnover
            and (item["median_live_quoted_spread_bps"] or math.inf) <= args.spread_limit_bps
        )
        if item["eligible"]:
            eligible.append(symbol)

    for symbol in FACTOR_SYMBOLS:
        reports[symbol]["eligible"] = None

    common_dates: list[str] = []
    if eligible:
        for target, _, _ in windows:
            date_text = target.isoformat()
            required = math.ceil(0.80 * len(eligible))
            tradable_coverage = sum(date_text in usable[symbol] for symbol in eligible) >= required
            factors_available = all(date_text in usable[symbol] for symbol in FACTOR_SYMBOLS)
            if tradable_coverage and factors_available:
                common_dates.append(date_text)

    breadth_passes = len(eligible) >= args.min_eligible_assets
    history_passes = len(common_dates) >= args.min_total_sessions and len(common_dates) > args.oos_sessions
    if breadth_passes and history_passes:
        oos_start_index = len(common_dates) - args.oos_sessions
        split = {
            "common_usable_sessions": len(common_dates),
            "is_start": common_dates[0],
            "is_end": common_dates[oos_start_index - 1],
            "is_sessions": oos_start_index,
            "oos_start": common_dates[oos_start_index],
            "oos_end": common_dates[-1],
            "oos_sessions": args.oos_sessions,
        }
        status = "PASS"
    else:
        failures = []
        if not breadth_passes:
            failures.append(f"eligible tradables {len(eligible)} < {args.min_eligible_assets}")
        if not history_passes:
            failures.append(
                f"common usable sessions {len(common_dates)} < {args.min_total_sessions} "
                f"with {args.oos_sessions} OOS sessions required"
            )
        split = {
            "common_usable_sessions": len(common_dates),
            "reason": "; ".join(failures),
        }
        status = "FAIL"

    return {
        "generated_at": now.isoformat(),
        "status": status,
        "definitions": {
            "session": "Previous NYSE close through 09:30 ET of the target NYSE session",
            "zero_volume_fraction": "Fraction of post-launch completed overnight sessions with aggregate API candle volume equal to zero",
            "median_turnover": "Median platformTurnover24h across repeated live ticker snapshots",
            "median_spread": "Median top-of-book quoted spread across repeated live ticker snapshots",
            "historical_spread_proxy": "Median Corwin-Schultz estimate from 1H OHLC bars; not observed bid/ask",
            "usable_session": f">=80% hourly coverage, nonzero aggregate volume, historical spread proxy <= {args.spread_limit_bps} bps",
        },
        "thresholds": {
            "min_usable_sessions_per_symbol": args.min_usable_sessions,
            "max_zero_volume_fraction": args.max_zero_volume_fraction,
            "min_live_platform_turnover_24h": args.min_platform_turnover,
            "max_live_quoted_spread_bps": args.spread_limit_bps,
            "min_eligible_assets": args.min_eligible_assets,
            "min_common_usable_sessions": args.min_total_sessions,
            "oos_sessions": args.oos_sessions,
        },
        "eligible_book": eligible,
        "split": split,
        "tradables": [reports[symbol] for symbol in TRADABLE_SYMBOLS],
        "factors": [reports[symbol] for symbol in FACTOR_SYMBOLS],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2026-06-02")
    parser.add_argument("--end")
    parser.add_argument("--output", type=Path, default=Path("reports/data-audit.json"))
    parser.add_argument("--markdown", type=Path, default=Path("reports/data-audit.md"))
    parser.add_argument("--ticker-samples", type=int, default=12)
    parser.add_argument("--ticker-interval", type=float, default=2.0)
    parser.add_argument("--spread-limit-bps", type=float, default=20.0)
    parser.add_argument("--min-platform-turnover", type=float, default=50_000.0)
    parser.add_argument("--max-zero-volume-fraction", type=float, default=0.10)
    parser.add_argument("--min-usable-sessions", type=int, default=60)
    parser.add_argument("--min-eligible-assets", type=int, default=12)
    parser.add_argument("--min-total-sessions", type=int, default=60)
    parser.add_argument("--oos-sessions", type=int, default=30)
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
