"""Build immutable, IS-only raw inputs for NightBasis Desk replay fixtures."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

from nightbasis.price_backtest import (
    bar_maps,
    load_audit,
    load_snapshot,
    sha256_file,
    timestamp_ms,
)


SNAPSHOTS = (
    ("16:30", dt.time(16, 30), -1),
    ("20:00", dt.time(20, 0), -1),
    ("00:00", dt.time(0, 0), 0),
    ("08:30", dt.time(8, 30), 0),
)

INSTRUMENTS = {
    "RNVDAUSDT": "tradable",
    "RTSLAUSDT": "tradable",
    "RAAPLUSDT": "tradable",
    "RGOOGLUSDT": "tradable",
    "RQQQUSDT": "factor_primary",
    "RSPYUSDT": "factor_fallback",
    "BTCUSDT": "factor_crypto",
    "ETHUSDT": "factor_crypto",
}

FIXTURES: tuple[dict[str, Any], ...] = (
    {
        "fixture_id": "flat-rgoogl-2026-08-14",
        "scenario": "flat_night",
        "session_date_et": "2026-08-14",
        "selection_partition": "OOS_CALENDAR_EVALUATION_ONLY",
        "focus_symbol": "RGOOGLUSDT",
        "selection_basis": "Smallest absolute 16:15-to-00:00 focus-name move among usable exact-anchor IS observations.",
        "event_retrieval": {
            "window_start_et": "2026-08-13T16:00:00-04:00",
            "window_end_et": "2026-08-14T08:30:00-04:00",
            "scope": ["SEC company filings", "Alphabet investor relations"],
            "items": [],
            "absence_note": "No fixture event is asserted; this is not proof that no public information existed.",
        },
    },
    {
        "fixture_id": "material-news-rgoogl-2026-07-23",
        "scenario": "material_news",
        "session_date_et": "2026-07-23",
        "selection_partition": "IS",
        "focus_symbol": "RGOOGLUSDT",
        "selection_basis": "Alphabet earnings 8-K was public before the first desk snapshot and the focus rToken made a large IS move.",
        "event_retrieval": {
            "window_start_et": "2026-07-22T16:00:00-04:00",
            "window_end_et": "2026-07-23T08:30:00-04:00",
            "scope": ["SEC EDGAR"],
            "items": [
                {
                    "event_id": "sec-0001652044-26-000066",
                    "symbols": ["RGOOGLUSDT"],
                    "published_at_et": "2026-07-22T16:01:36-04:00",
                    "source_type": "sec_8k_exhibit_99_1",
                    "source_name": "SEC EDGAR",
                    "url": "https://www.sec.gov/Archives/edgar/data/1652044/000165204426000066/googexhibit991q22026.htm",
                    "headline": "Alphabet Announces Second Quarter 2026 Results",
                    "raw_excerpt": "Alphabet revenues increased 24% to $119.8 billion; Google Cloud revenues increased 82% to $24.8 billion.",
                    "structured_facts": {
                        "alphabet_revenue_usd_billions": 119.8,
                        "alphabet_revenue_yoy_pct": 24.0,
                        "google_cloud_revenue_usd_billions": 24.8,
                        "google_cloud_revenue_yoy_pct": 82.0,
                        "operating_margin_pct": 34.0,
                        "diluted_eps_usd": 9.11,
                    },
                }
            ],
        },
    },
    {
        "fixture_id": "large-move-no-event-rtsla-2026-06-23",
        "scenario": "large_move_no_qualifying_news",
        "session_date_et": "2026-06-23",
        "selection_partition": "IS",
        "focus_symbol": "RTSLAUSDT",
        "selection_basis": "Large usable IS rToken move with no qualifying company filing or IR release inside the frozen after-hours event window.",
        "event_retrieval": {
            "window_start_et": "2026-06-22T16:00:00-04:00",
            "window_end_et": "2026-06-23T08:30:00-04:00",
            "scope": ["SEC company filings", "Tesla investor-relations press releases"],
            "items": [],
            "absence_note": "No qualifying company event was found in the stated sources/window; this is a bounded feed result, not a universal no-news claim.",
            "source_evidence": [
                {
                    "source_name": "SEC EDGAR Tesla filing directory",
                    "url": "https://www.sec.gov/Archives/edgar/data/1318605/",
                    "observation": "The directory shows no Tesla filing accepted within the fixture window.",
                },
                {
                    "source_name": "Tesla Investor Relations press releases",
                    "url": "https://ir.tesla.com/press",
                    "observation": "No Tesla IR release is listed within the fixture window.",
                },
            ],
        },
    },
)


def canonical_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def audit_session(audit: dict[str, Any], symbol: str, date_text: str) -> dict[str, Any] | None:
    for group in ("tradables", "factors"):
        for item in audit[group]:
            if item["symbol"] == symbol:
                return next((row for row in item["sessions"] if row["date"] == date_text), None)
    return None


def raw_bar(bar: dict[str, Any] | None) -> dict[str, Any] | None:
    if bar is None:
        return None
    return {
        "ts": int(float(bar["ts"])),
        "open": float(bar["open"]),
        "high": float(bar["high"]),
        "low": float(bar["low"]),
        "close": float(bar["close"]),
        "volume": float(bar["volume"]),
        "turnover": float(bar["turnover"]),
    }


def build_fixture(
    definition: dict[str, Any],
    snapshot: dict[str, Any],
    audit: dict[str, Any],
    freeze: dict[str, Any],
    snapshot_path: Path,
    audit_path: Path,
) -> dict[str, Any]:
    day = dt.date.fromisoformat(definition["session_date_et"])
    date_text = day.isoformat()
    maps = bar_maps(snapshot)
    market: dict[str, Any] = {}
    for symbol, role in INSTRUMENTS.items():
        anchor_stamp = timestamp_ms(day - dt.timedelta(days=1), dt.time(16, 15))
        bars = {}
        for name, clock, day_offset in SNAPSHOTS:
            stamp = timestamp_ms(day + dt.timedelta(days=day_offset), clock)
            bars[name] = raw_bar(maps[symbol].get(stamp))
        market[symbol] = {
            "role": role,
            "session_quality": audit_session(audit, symbol, date_text),
            "session_anchor_16_15": raw_bar(maps[symbol].get(anchor_stamp)),
            "snapshots": bars,
        }

    focus = definition["focus_symbol"]
    anchor_bar = market[focus]["session_anchor_16_15"]
    if anchor_bar is None:
        raise RuntimeError(f"Missing 16:15 ET anchor for {definition['fixture_id']}")
    midnight = market[focus]["snapshots"]["00:00"]
    if midnight is None:
        raise RuntimeError(f"Missing 00:00 ET focus bar for {definition['fixture_id']}")

    payload = {
        "fixture_version": "1.0.0",
        **definition,
        "source_integrity": {
            "market_snapshot_captured_at": snapshot["captured_at"],
            "market_snapshot_sha256": sha256_file(snapshot_path),
            "audit_sha256": sha256_file(audit_path),
            "price_control_freeze_sha256": freeze["freeze_sha256"],
            "price_control_commit": "c92b9bd776ce43cf71d94ba90d3db23622b4395c",
        },
        "session_anchor": {"name": "16:15", "bar": anchor_bar},
        "focus_move_to_midnight": midnight["open"] / anchor_bar["open"] - 1.0,
        "frozen_models": freeze["models"],
        "market": market,
    }
    payload["fixture_sha256"] = canonical_hash(payload)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=Path("data/market-snapshot.json.gz"))
    parser.add_argument("--audit", type=Path, default=Path("reports/data-audit.json"))
    parser.add_argument("--freeze", type=Path, default=Path("reports/price-only-freeze.json"))
    parser.add_argument("--output", type=Path, default=Path("fixtures/desk"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshot = load_snapshot(args.snapshot)
    audit = load_audit(args.audit)
    freeze = json.loads(args.freeze.read_text())
    if freeze["snapshot_sha256"] != sha256_file(args.snapshot):
        raise RuntimeError("Frozen control and market snapshot hashes differ")
    if freeze["audit_sha256"] != sha256_file(args.audit):
        raise RuntimeError("Frozen control and audit hashes differ")

    manifest = {"fixture_version": "1.0.0", "fixtures": []}
    for definition in FIXTURES:
        payload = build_fixture(definition, snapshot, audit, freeze, args.snapshot, args.audit)
        directory = args.output / definition["fixture_id"]
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "raw-input.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        manifest["fixtures"].append(
            {
                "fixture_id": definition["fixture_id"],
                "scenario": definition["scenario"],
                "session_date_et": definition["session_date_et"],
                "focus_symbol": definition["focus_symbol"],
                "path": str(path),
                "fixture_sha256": payload["fixture_sha256"],
            }
        )
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
