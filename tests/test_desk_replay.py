import copy
import datetime as dt
import json
import unittest
from pathlib import Path

from nightbasis.desk_replay import (
    REASON_ENUM,
    SNAPSHOT_ORDER,
    deterministic_label,
    eligible_events,
    render_reason_matrix,
    render_transcript,
    replay,
)


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "prompts/event_score_v1.txt"
FIXTURE_ROOT = ROOT / "fixtures/desk"


def good_quality():
    return {
        "volume_positive": True,
        "coverage_pass": True,
        "spread_pass": True,
        "factor_pass": True,
    }


def score(qualifying=False, direction=0, signed_info=0.0):
    return {
        "qualifying_event": qualifying,
        "direction": direction,
        "signed_info": signed_info,
    }


class DeskReplayTests(unittest.TestCase):
    def replay_fixture(self, fixture_id):
        directory = FIXTURE_ROOT / fixture_id
        return replay(
            directory / "raw-input.json",
            directory / "event-score-human-v1.json",
            PROMPT,
        )

    def test_locked_matrix_is_all_stand_down(self):
        fixture_ids = (
            "flat-rgoogl-2026-08-14",
            "material-news-rgoogl-2026-07-23",
            "large-move-no-event-rtsla-2026-06-23",
        )
        for fixture_id in fixture_ids:
            records = self.replay_fixture(fixture_id)
            self.assertEqual([row["snapshot"]["name"] for row in records], list(SNAPSHOT_ORDER))
            self.assertEqual([row["label"] for row in records], ["stand_down"] * 4)

    def test_news_records_carry_locked_session_start(self):
        records = self.replay_fixture("material-news-rgoogl-2026-07-23")
        self.assertTrue(
            all(row["session_start_et"] == "2026-07-22T16:15:00-04:00" for row in records)
        )

    def test_frozen_reason_matrix(self):
        fixture_ids = (
            "flat-rgoogl-2026-08-14",
            "material-news-rgoogl-2026-07-23",
            "large-move-no-event-rtsla-2026-06-23",
        )
        groups = [self.replay_fixture(fixture_id) for fixture_id in fixture_ids]
        self.assertEqual(
            [[row["reason"] for row in group] for group in groups],
            [
                [
                    "uninformed_but_below_washout",
                    "uninformed_but_below_washout",
                    "no_qualifying_event_nonnegative_move",
                    "no_qualifying_event_nonnegative_move",
                ],
                ["event_price_direction_conflict"] * 4,
                ["uninformed_but_below_washout"] * 4,
            ],
        )
        self.assertTrue(all(row["reason"] in REASON_ENUM for group in groups for row in group))
        self.assertIn("# Frozen reason matrix", render_reason_matrix(groups))

    def test_news_1630_attribution_has_no_hard_kill(self):
        row = self.replay_fixture("material-news-rgoogl-2026-07-23")[0]
        self.assertAlmostEqual(row["llm"]["signed_info"], 0.855)
        self.assertEqual(row["reason"], "event_price_direction_conflict")
        self.assertFalse(row["kill_criteria"]["killed"])
        self.assertEqual(row["kill_criteria"]["reasons"], [])
        self.assertTrue(all(row["kill_criteria"]["checks"].values()))

    def test_tesla_0830_is_exactly_below_washout(self):
        row = self.replay_fixture("large-move-no-event-rtsla-2026-06-23")[-1]
        self.assertAlmostEqual(row["price_state"]["z"], 1.2357, places=4)
        self.assertLess(row["price_state"]["z"], 1.25)
        self.assertEqual(row["reason"], "uninformed_but_below_washout")

    def test_transcript_has_required_attribution_fields(self):
        text = render_transcript(self.replay_fixture("flat-rgoogl-2026-08-14"))
        for field in ("t=", "y=", "z=", "signed_info=", "event_id_or_none=", "label=", "reason=", "memo="):
            self.assertIn(field, text)

    def test_each_snapshot_uses_only_its_own_point_in_time_inputs(self):
        records = self.replay_fixture("material-news-rgoogl-2026-07-23")
        first = records[0]
        self.assertEqual(first["snapshot"]["as_of_et"], "2026-07-22T16:30:00-04:00")
        self.assertAlmostEqual(first["price_state"]["snapshot_price"], 341.99)
        self.assertTrue(
            all(
                dt.datetime.fromisoformat(item["published_at_et"])
                <= dt.datetime.fromisoformat(first["snapshot"]["as_of_et"])
                for item in first["event_json"]["items"]
            )
        )

    def test_future_event_is_excluded(self):
        fixture = json.loads(
            (FIXTURE_ROOT / "material-news-rgoogl-2026-07-23/raw-input.json").read_text()
        )
        future_fixture = copy.deepcopy(fixture)
        future_fixture["event_retrieval"]["items"][0]["published_at_et"] = (
            "2026-07-22T16:31:00-04:00"
        )
        as_of = dt.datetime.fromisoformat("2026-07-22T16:30:00-04:00")
        self.assertEqual(eligible_events(future_fixture, as_of), [])

    def test_label_policy_boundaries_and_precedence(self):
        quality = good_quality()
        self.assertEqual(
            deterministic_label(
                {"y": 0.005, "z": 0.0}, quality, score(True, 1, 0.65), True, True
            )[0],
            "incomplete",
        )
        self.assertEqual(
            deterministic_label(
                {"y": -0.01, "z": 0.0}, quality, score(True, -1, -0.8), True, True
            )[0],
            "priced",
        )
        self.assertEqual(
            deterministic_label(
                {"y": -0.01, "z": 1.25}, quality, score(), True, True
            )[0],
            "washout",
        )
        failed_quality = {**quality, "coverage_pass": False}
        self.assertEqual(
            deterministic_label(
                {"y": -0.01, "z": 2.0}, failed_quality, score(), True, True
            )[0],
            "stand_down",
        )

    def test_washout_is_weeknight_only(self):
        label, reason, kill_reasons = deterministic_label(
            {"y": -0.01, "z": 2.0}, good_quality(), score(), True, False
        )
        self.assertEqual(label, "stand_down")
        self.assertEqual(reason, "washout_weeknight_gate_failed")
        self.assertEqual(kill_reasons, [])


if __name__ == "__main__":
    unittest.main()
