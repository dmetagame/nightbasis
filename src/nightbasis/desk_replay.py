"""Offline, deterministic NightBasis Desk replay. This module never trades."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
from typing import Any


SNAPSHOT_ORDER = ("16:30", "20:00", "00:00", "08:30")
WASHOUT_Z = 1.25
INCOMPLETE_SIGNED_INFO = 0.65
PRICED_MOVE = 0.01
MIN_COVERAGE = 0.80
MAX_SPREAD_PROXY_BPS = 20.0


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def content_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256_bytes(payload)


def snapshot_as_of(session_start: dt.datetime, name: str) -> dt.datetime:
    hour, minute = (int(part) for part in name.split(":"))
    day = session_start.date() if name in {"16:30", "20:00"} else session_start.date() + dt.timedelta(days=1)
    return dt.datetime.combine(day, dt.time(hour, minute), session_start.tzinfo)


def eligible_events(fixture: dict[str, Any], as_of: dt.datetime) -> list[dict[str, Any]]:
    return [
        event
        for event in fixture["event_retrieval"]["items"]
        if dt.datetime.fromisoformat(event["published_at_et"]) <= as_of
    ]


def expected_cache_key(
    prompt_sha256: str,
    fixture: dict[str, Any],
    symbol: str,
    as_of_et: str,
    events: list[dict[str, Any]],
) -> str:
    return content_hash(
        {
            "prompt_sha256": prompt_sha256,
            "fixture_sha256": fixture["fixture_sha256"],
            "symbol": symbol,
            "as_of_et": as_of_et,
            "event_ids": [event["event_id"] for event in events],
        }
    )


def validate_event_score(
    score: dict[str, Any], expected_key: str, symbol: str, as_of_et: str
) -> list[str]:
    reasons = []
    required = {
        "schema_version",
        "prompt_version",
        "scorer_version",
        "temperature",
        "symbol",
        "as_of_et",
        "qualifying_event",
        "direction",
        "materiality",
        "confidence",
        "novelty_gate",
        "signed_info",
        "event_ids",
        "rationale",
        "cache_key",
    }
    if set(score) != required:
        reasons.append("event_score_schema_invalid")
        return reasons
    if score["cache_key"] != expected_key:
        reasons.append("event_score_cache_key_invalid")
    if score["symbol"] != symbol:
        reasons.append("event_score_symbol_invalid")
    if score["as_of_et"] != as_of_et:
        reasons.append("event_score_as_of_invalid")
    if score["prompt_version"] != "event_score_v1":
        reasons.append("event_score_prompt_version_invalid")
    if score["temperature"] != 0:
        reasons.append("event_score_temperature_invalid")
    if score["direction"] not in {-1, 0, 1}:
        reasons.append("event_score_direction_invalid")
    if not 0 <= score["materiality"] <= 1 or not 0 <= score["confidence"] <= 1:
        reasons.append("event_score_range_invalid")
    expected_signed = score["direction"] * score["materiality"] * score["confidence"]
    if not math.isclose(score["signed_info"], expected_signed, abs_tol=1e-12):
        reasons.append("event_score_signed_info_invalid")
    return reasons


def factor_choice(fixture: dict[str, Any]) -> str | None:
    market = fixture["market"]
    if market["RQQQUSDT"]["session_quality"]["usable"]:
        return "RQQQUSDT"
    if market["RSPYUSDT"]["session_quality"]["usable"]:
        return "RSPYUSDT"
    return None


def log_move(fixture: dict[str, Any], symbol: str, snapshot: str) -> float | None:
    instrument = fixture["market"][symbol]
    anchor = instrument["session_anchor_16_15"]
    bar = instrument["snapshots"][snapshot]
    if not anchor or not bar or anchor["open"] <= 0 or bar["open"] <= 0:
        return None
    return math.log(bar["open"] / anchor["open"])


def quality_state(fixture: dict[str, Any], symbol: str, equity_factor: str | None) -> dict[str, Any]:
    session = fixture["market"][symbol]["session_quality"]
    spread = session["spread_proxy_bps"]
    return {
        "volume_positive": session["volume"] > 0,
        "coverage": session["coverage"],
        "coverage_pass": session["coverage"] >= MIN_COVERAGE,
        "spread_proxy_bps": spread,
        "spread_pass": spread is not None and spread <= MAX_SPREAD_PROXY_BPS,
        "equity_factor": equity_factor,
        "factor_pass": equity_factor is not None,
    }


def compute_price_state(
    fixture: dict[str, Any], symbol: str, snapshot: str, equity_factor: str
) -> dict[str, Any] | None:
    y = log_move(fixture, symbol, snapshot)
    equity = log_move(fixture, equity_factor, snapshot)
    btc = log_move(fixture, "BTCUSDT", snapshot)
    eth = log_move(fixture, "ETHUSDT", snapshot)
    if any(value is None for value in (y, equity, btc, eth)):
        return None
    model = fixture["frozen_models"][f"{symbol}:weeknight"]
    beta = model["coefficients"]
    contributions = {
        "intercept": beta[0],
        "equity": beta[1] * equity,
        "btc": beta[2] * btc,
        "eth": beta[3] * eth,
    }
    contributions["sum"] = sum(contributions.values())
    scale = model["residual_scale"]
    instrument = fixture["market"][symbol]
    return {
        "anchor_price": instrument["session_anchor_16_15"]["open"],
        "snapshot_price": instrument["snapshots"][snapshot]["open"],
        "y": y,
        "m_hat": contributions["sum"],
        "z": (y - contributions["sum"]) / scale,
        "residual_scale": scale,
        "factor_contributions": contributions,
    }


def deterministic_label(
    price: dict[str, Any] | None,
    quality: dict[str, Any],
    score: dict[str, Any],
    event_timestamp_valid: bool,
    weeknight: bool,
) -> tuple[str, list[str]]:
    kill_reasons = []
    if price is None:
        kill_reasons.append("snapshot_or_factor_bar_missing")
    if not quality["volume_positive"]:
        kill_reasons.append("zero_session_volume")
    if not quality["coverage_pass"]:
        kill_reasons.append("coverage_below_80pct")
    if not quality["spread_pass"]:
        kill_reasons.append("spread_proxy_above_20bps_or_missing")
    if not quality["factor_pass"]:
        kill_reasons.append("equity_factor_unavailable")
    if not event_timestamp_valid:
        kill_reasons.append("future_event_present")
    if kill_reasons:
        return "stand_down", kill_reasons

    has_event = bool(score["qualifying_event"])
    y = price["y"]
    if has_event and score["signed_info"] >= INCOMPLETE_SIGNED_INFO and abs(y) < PRICED_MOVE:
        return "incomplete", []
    direction_agrees = y != 0 and score["direction"] != 0 and (y > 0) == (score["direction"] > 0)
    if has_event and abs(y) >= PRICED_MOVE and direction_agrees:
        return "priced", []
    if not has_event and y < 0 and price["z"] >= WASHOUT_Z and weeknight:
        return "washout", []
    return "stand_down", ["no_label_rule_matched"]


def build_record(
    fixture: dict[str, Any],
    cache: dict[str, Any],
    prompt_sha256: str,
    snapshot: str,
) -> dict[str, Any]:
    symbol = fixture["focus_symbol"]
    session_start = dt.datetime.fromisoformat(cache["session_start_et"])
    as_of = snapshot_as_of(session_start, snapshot)
    as_of_text = as_of.isoformat()
    events = eligible_events(fixture, as_of)
    score = next(item for item in cache["scores"] if item["as_of_et"] == as_of_text)
    cache_key = expected_cache_key(prompt_sha256, fixture, symbol, as_of_text, events)
    score_errors = validate_event_score(score, cache_key, symbol, as_of_text)
    event_ids = [event["event_id"] for event in events]
    event_timestamp_valid = all(dt.datetime.fromisoformat(event["published_at_et"]) <= as_of for event in events)
    event_timestamp_valid = event_timestamp_valid and score["event_ids"] == event_ids
    event_timestamp_valid = event_timestamp_valid and (
        not score["qualifying_event"] or bool(events)
    )
    equity = factor_choice(fixture)
    quality = quality_state(fixture, symbol, equity)
    price = compute_price_state(fixture, symbol, snapshot, equity) if equity else None
    if score_errors:
        label, reasons = "stand_down", score_errors
    else:
        weeknight = fixture["market"][symbol]["session_quality"]["kind"] == "weeknight"
        label, reasons = deterministic_label(price, quality, score, event_timestamp_valid, weeknight)

    event_items = []
    for event in events:
        event_items.append(
            {
                "event_id": event["event_id"],
                "published_at_et": event["published_at_et"],
                "source_name": event["source_name"],
                "url": event["url"],
                "headline": event["headline"],
                "raw_excerpt": event["raw_excerpt"],
                "content_sha256": content_hash(event),
            }
        )
    source_bar = fixture["market"][symbol]["snapshots"][snapshot]
    return {
        "schema_version": "1.0.0",
        "record_id": f"{fixture['fixture_id']}:{symbol}:{snapshot}",
        "fixture_id": fixture["fixture_id"],
        "session_date_et": fixture["session_date_et"],
        "session_start_et": cache["session_start_et"],
        "symbol": symbol,
        "snapshot": {
            "name": snapshot,
            "as_of_et": as_of_text,
            "source_bar_timestamp_ms": source_bar["ts"],
        },
        "price_state": price,
        "quality": quality,
        "event_json": {
            "window_start_et": fixture["event_retrieval"]["window_start_et"],
            "as_of_et": as_of_text,
            "items": event_items,
            "retrieval_scope": fixture["event_retrieval"]["scope"],
        },
        "llm": {
            "prompt_version": score["prompt_version"],
            "model": score["scorer_version"],
            "temperature": score["temperature"],
            "cache_key": score["cache_key"],
            "direction": score["direction"],
            "materiality": score["materiality"],
            "confidence": score["confidence"],
            "signed_info": score["signed_info"],
            "novelty_gate": score["novelty_gate"],
            "explanation": score["rationale"],
        },
        "label": label,
        "kill_criteria": {
            "killed": label == "stand_down",
            "reasons": reasons,
            "checks": {
                "schema_valid": not score_errors,
                "snapshot_present": price is not None,
                "coverage_pass": quality["coverage_pass"],
                "spread_pass": quality["spread_pass"],
                "factor_pass": quality["factor_pass"],
                "event_timestamps_valid": event_timestamp_valid,
                "llm_json_valid": not score_errors,
            },
        },
        "memo": f"{label}: {'; '.join(reasons) if reasons else score['rationale']} No trade instruction produced.",
    }


def replay(fixture_path: Path, cache_path: Path, prompt_path: Path) -> list[dict[str, Any]]:
    fixture = json.loads(fixture_path.read_text())
    cache = json.loads(cache_path.read_text())
    if cache["fixture_sha256"] != fixture["fixture_sha256"]:
        raise RuntimeError("Event cache does not match fixture hash")
    prompt_sha256 = sha256_file(prompt_path)
    if cache["prompt_sha256"] != prompt_sha256:
        raise RuntimeError("Event cache does not match frozen prompt hash")
    return [build_record(fixture, cache, prompt_sha256, snapshot) for snapshot in SNAPSHOT_ORDER]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("fixtures/desk/material-news-rgoogl-2026-07-23/raw-input.json"),
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=Path("fixtures/desk/material-news-rgoogl-2026-07-23/event-score-human-v1.json"),
    )
    parser.add_argument("--prompt", type=Path, default=Path("prompts/event_score_v1.txt"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = replay(args.fixture, args.cache, args.prompt)
    print(json.dumps(records, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
