import unittest

from nightbasis.price_backtest import fit_ridge, make_trade, max_drawdown, metrics, predict, robust_scale


class PriceBacktestTests(unittest.TestCase):
    def test_ridge_recovers_simple_relation(self):
        rows = [
            {"features": [1.0, value], "observed_return": 0.01 + 2 * value}
            for value in (-0.02, -0.01, 0.0, 0.01, 0.02)
        ]
        coefficients = fit_ridge(rows)
        self.assertAlmostEqual(predict(coefficients, [1.0, 0.015]), 0.04, places=4)

    def test_robust_scale_is_positive(self):
        self.assertGreater(robust_scale([0.0, 0.0, 0.0]), 0)

    def test_max_drawdown(self):
        self.assertAlmostEqual(max_drawdown([0.1, -0.2, 0.05]), -0.2)

    def test_metrics_include_flat_days(self):
        daily = [
            {"status": "flat", "return": 0.0},
            {"status": "traded", "return": 0.01},
            {"status": "pending", "return": None},
        ]
        result = metrics(daily, [])
        self.assertEqual(result["calendar_days_observed"], 2)
        self.assertEqual(result["flat_days"], 1)
        self.assertEqual(result["pending_days"], 1)

    def test_weekend_rule_blocks_washout_and_applies_round_trip_cost(self):
        model = {"coefficients": [0.02, 0.0, 0.0], "residual_scale": 0.005}
        washout = {
            "usable": True,
            "date": "2026-06-06",
            "kind": "weekend_or_holiday",
            "symbol": "RNVDAUSDT",
            "factor_choice": "BTC_ETH",
            "features": [1.0, 0.0, 0.0],
            "observed_return": -0.01,
            "exit_return": 0.01,
        }
        self.assertIsNone(make_trade(washout, model, 25.0))

        continuation = dict(washout, observed_return=0.005)
        trade = make_trade(continuation, model, 25.0)
        self.assertIsNotNone(trade)
        self.assertAlmostEqual(
            trade["net_trade_return"],
            2.718281828459045**0.01 - 1 - 0.005,
        )


if __name__ == "__main__":
    unittest.main()
