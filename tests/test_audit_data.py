import datetime as dt
import unittest

from nightbasis.audit_data import UTC, corwin_schultz_spread_bps, history_chunks, session_windows


class AuditDataTests(unittest.TestCase):
    def test_history_chunks_stay_inside_99_hours(self):
        chunks = history_chunks(0, 250 * 60 * 60 * 1000)
        self.assertEqual(len(chunks), 3)
        self.assertTrue(all(right - left <= 99 * 60 * 60 * 1000 for left, right in chunks))

    def test_flat_bars_have_zero_spread_proxy(self):
        bar = {"high": 100.0, "low": 100.0}
        self.assertEqual(corwin_schultz_spread_bps(bar, bar), 0.0)

    def test_juneteenth_is_not_a_target_session(self):
        now = dt.datetime(2026, 6, 23, 12, tzinfo=UTC)
        dates = {item[0] for item in session_windows(dt.date(2026, 6, 17), dt.date(2026, 6, 23), now)}
        self.assertNotIn(dt.date(2026, 6, 19), dates)
        self.assertIn(dt.date(2026, 6, 22), dates)


if __name__ == "__main__":
    unittest.main()

