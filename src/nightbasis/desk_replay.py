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
FIXTURE_IDS = (
    "flat-rgoogl-2026-08-14",
    "material-news-rgoogl-2026-07-23",
    "large-move-no-event-rtsla-2026-06-23",
)
WASHOUT_Z = 1.25
INCOMPLETE_SIGNED_INFO = 0.65
PRICED_MOVE = 0.01
MIN_COVERAGE = 0.80
MAX_SPREAD_PROXY_BPS = 20.0
REASON_ENUM = (
    "priced_event_move_agrees",
    "incomplete_material_event",
    "uninformed_washout",
    "event_price_direction_conflict",
    "event_below_information_threshold",
    "event_conditions_not_met",
    "uninformed_but_below_washout",
    "no_qualifying_event_nonnegative_move",
    "washout_weeknight_gate_failed",
    "data_quality_kill",
    "event_timing_kill",
    "event_score_kill",
)


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
) -> tuple[str, str, list[str]]:
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
        reason = "event_timing_kill" if not event_timestamp_valid else "data_quality_kill"
        return "stand_down", reason, kill_reasons

    has_event = bool(score["qualifying_event"])
    y = price["y"]
    if has_event and score["signed_info"] >= INCOMPLETE_SIGNED_INFO and abs(y) < PRICED_MOVE:
        return "incomplete", "incomplete_material_event", []
    direction_agrees = y != 0 and score["direction"] != 0 and (y > 0) == (score["direction"] > 0)
    if has_event and abs(y) >= PRICED_MOVE and direction_agrees:
        return "priced", "priced_event_move_agrees", []
    if not has_event and y < 0 and price["z"] >= WASHOUT_Z and weeknight:
        return "washout", "uninformed_washout", []
    if has_event and abs(y) >= PRICED_MOVE and not direction_agrees:
        return "stand_down", "event_price_direction_conflict", []
    if has_event and score["signed_info"] < INCOMPLETE_SIGNED_INFO and abs(y) < PRICED_MOVE:
        return "stand_down", "event_below_information_threshold", []
    if has_event:
        return "stand_down", "event_conditions_not_met", []
    if y < 0 and price["z"] < WASHOUT_Z:
        return "stand_down", "uninformed_but_below_washout", []
    if y < 0 and not weeknight:
        return "stand_down", "washout_weeknight_gate_failed", []
    return "stand_down", "no_qualifying_event_nonnegative_move", []


def build_memo(
    label: str,
    reason: str,
    price: dict[str, Any] | None,
    score: dict[str, Any],
    kill_reasons: list[str],
) -> str:
    if kill_reasons:
        detail = f"Hard kill fired: {', '.join(kill_reasons)}."
    elif reason == "event_price_direction_conflict":
        detail = (
            f"Qualifying event direction={score['direction']:+d} conflicts with "
            f"y={price['y']:.6f}."
        )
    elif reason == "uninformed_but_below_washout":
        detail = (
            f"No qualifying event; y={price['y']:.6f} and z={price['z']:.6f} "
            f"is below {WASHOUT_Z:.2f}."
        )
    elif reason == "no_qualifying_event_nonnegative_move":
        detail = f"No qualifying event and y={price['y']:.6f} is nonnegative."
    else:
        detail = score["rationale"]
    return f"{label} / {reason}. {detail} No trade instruction produced."


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
        label, reason, kill_reasons = "stand_down", "event_score_kill", score_errors
    else:
        weeknight = fixture["market"][symbol]["session_quality"]["kind"] == "weeknight"
        label, reason, kill_reasons = deterministic_label(
            price, quality, score, event_timestamp_valid, weeknight
        )

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
        "reason": reason,
        "kill_criteria": {
            "killed": bool(kill_reasons),
            "reasons": kill_reasons,
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
        "memo": build_memo(label, reason, price, score, kill_reasons),
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


def render_transcript(records: list[dict[str, Any]]) -> str:
    first = records[0]
    lines = [
        f"fixture={first['fixture_id']} symbol={first['symbol']} "
        f"session_start={first['session_start_et']}"
    ]
    for record in records:
        event_ids = [item["event_id"] for item in record["event_json"]["items"]]
        event_id = ",".join(event_ids) if event_ids else "none"
        price = record["price_state"]
        lines.append(
            f"t={record['snapshot']['name']} "
            f"y={price['y']:.8f} "
            f"z={price['z']:.6f} "
            f"signed_info={record['llm']['signed_info']:.3f} "
            f"event_id_or_none={event_id} "
            f"label={record['label']} "
            f"reason={record['reason']} "
            f"kill_fired={str(record['kill_criteria']['killed']).lower()} "
            f"memo={json.dumps(record['memo'])}"
        )
    return "\n".join(lines)


def render_reason_matrix(groups: list[list[dict[str, Any]]]) -> str:
    headers = [group[0]["fixture_id"] for group in groups]
    lines = [
        "# Frozen reason matrix",
        "",
        "| Snapshot ET | " + " | ".join(headers) + " |",
        "| --- | " + " | ".join("---" for _ in headers) + " |",
    ]
    for index, snapshot in enumerate(SNAPSHOT_ORDER):
        reasons = [f"`{group[index]['reason']}`" for group in groups]
        lines.append(f"| {snapshot} | " + " | ".join(reasons) + " |")
    return "\n".join(lines) + "\n"


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
    parser.add_argument("--all", action="store_true", help="Replay exactly the three frozen fixtures")
    parser.add_argument("--fixture-root", type=Path, default=Path("fixtures/desk"))
    parser.add_argument("--transcript-dir", type=Path)
    parser.add_argument("--reason-matrix", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.all:
        groups = []
        transcripts = []
        for fixture_id in FIXTURE_IDS:
            fixture_dir = args.fixture_root / fixture_id
            records = replay(
                fixture_dir / "raw-input.json",
                fixture_dir / "event-score-human-v1.json",
                args.prompt,
            )
            groups.append(records)
            transcript = render_transcript(records)
            transcripts.append(transcript)
            if args.transcript_dir:
                args.transcript_dir.mkdir(parents=True, exist_ok=True)
                (args.transcript_dir / f"{fixture_id}.txt").write_text(transcript + "\n")
        if args.reason_matrix:
            args.reason_matrix.parent.mkdir(parents=True, exist_ok=True)
            args.reason_matrix.write_text(render_reason_matrix(groups))
        print("\n\n".join(transcripts))
    else:
        records = replay(args.fixture, args.cache, args.prompt)
        print(render_transcript(records))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
