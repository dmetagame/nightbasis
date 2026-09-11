import datetime as dt
import json
import unittest
from pathlib import Path

from nightbasis.audit_data import IS_END, IS_START
from nightbasis.desk_fixtures import FIXTURES, INSTRUMENTS, SNAPSHOTS, build_fixture
from nightbasis.price_backtest import load_audit, load_snapshot


ROOT = Path(__file__).resolve().parents[1]


class DeskFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot_path = ROOT / "data/market-snapshot.json.gz"
        cls.audit_path = ROOT / "reports/data-audit.json"
        cls.snapshot = load_snapshot(cls.snapshot_path)
        cls.audit = load_audit(cls.audit_path)
        cls.freeze = json.loads((ROOT / "reports/price-only-freeze.json").read_text())

    def test_fixture_dates_are_is_only(self):
        for definition in FIXTURES:
            day = dt.date.fromisoformat(definition["session_date_et"])
            self.assertGreaterEqual(day, IS_START)
            self.assertLessEqual(day, IS_END)

    def test_fixture_has_every_market_snapshot(self):
        for definition in FIXTURES:
            payload = build_fixture(
                definition,
                self.snapshot,
                self.audit,
                self.freeze,
                self.snapshot_path,
                self.audit_path,
            )
            self.assertEqual(set(payload["market"]), set(INSTRUMENTS))
            for instrument in payload["market"].values():
                self.assertIsNotNone(instrument["session_anchor_16_15"])
                self.assertEqual(set(instrument["snapshots"]), {row[0] for row in SNAPSHOTS})
                self.assertTrue(all(bar is not None for bar in instrument["snapshots"].values()))

    def test_material_fixture_event_precedes_first_snapshot(self):
        definition = next(item for item in FIXTURES if item["scenario"] == "material_news")
        event = definition["event_retrieval"]["items"][0]
        published = dt.datetime.fromisoformat(event["published_at_et"])
        first_snapshot = dt.datetime.fromisoformat("2026-07-22T16:30:00-04:00")
        self.assertLess(published, first_snapshot)


if __name__ == "__main__":
    unittest.main()
