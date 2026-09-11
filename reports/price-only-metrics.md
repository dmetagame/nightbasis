# NightBasis Price-Only Backtest

Generated from the committed IS freeze `0898cca4374ae68dfbc85ae73138f710539d314800de8548d3b37f28fd0ba5a0`.
The model and entry thresholds were frozen before the OOS command was run.

## Strategy-day recount

The frozen core-only book has **83 usable strategy nights** in the audited data:
**57 weeknights** and **26 weekend/US-holiday nights**. Factors are never
tradable. Weeknights require usable rQQQ or rSPY; weekend/holiday nights require
both BTC and ETH. A failed session is retained as a zero-return calendar day.

## Frozen price-only rule

- Book: rNVDA, rTSLA, rAAPL, rGOOGL.
- Weeknight fair value: per-name IS ridge on rQQQ (rSPY fallback), BTC, and ETH
  returns from 16:15 ET to 00:00 ET.
- Weekend/holiday fair value: the frozen intercept and BTC/ETH coefficients from
  each name's IS weeknight model. This avoids fitting separate models on only
  1-8 exact-anchor weekend observations per name.
- Residual score: `(fair return - observed rToken return) / frozen residual scale`.
- Entry: long at 00:00 ET only when fair return is positive and z >= 1.0 on a
  weeknight. Weekend/holiday requires z >= 1.5 and observed return >= 0, so no
  washout entry is possible. Exit is 09:00 ET.
- Position weight: 4% NAV per name. Returns deduct the stated cost on both entry
  and exit.

## Flat-inclusive results

OOS is provisional through 2026-09-11. The ledger contains all 30 frozen OOS
dates, with 2026-09-12 through 2026-09-18 marked `pending`, not flat.

| Period | Cost/side | Observed days | Flat / traded / pending | Trades | Total return | Sharpe | Sortino | Max DD | Win rate | Round-trip turnover |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| IS | 15 bps | 79 | 72 / 7 / 0 | 10 | -0.0702% | -1.58 | -2.03 | -0.0978% | 50% | 0.80x NAV |
| IS | 25 bps | 79 | 72 / 7 / 0 | 10 | -0.1502% | -2.96 | -3.32 | -0.1502% | 40% | 0.80x NAV |
| IS | 37.5 bps | 79 | 72 / 7 / 0 | 10 | -0.2500% | -3.96 | -4.08 | -0.2500% | 20% | 0.80x NAV |
| OOS provisional | 15 bps | 23 | 20 / 3 / 7 | 5 | -0.1595% | -5.57 | -5.46 | -0.1595% | 20% | 0.40x NAV |
| OOS provisional | 25 bps | 23 | 20 / 3 / 7 | 5 | -0.1995% | -5.76 | -5.62 | -0.1995% | 0% | 0.40x NAV |
| OOS provisional | 37.5 bps | 23 | 20 / 3 / 7 | 5 | -0.2494% | -5.89 | -5.74 | -0.2494% | 0% | 0.40x NAV |

The executable sample contains 176 usable weeknight name-sessions across 44 IS
dates and 13 weekend/holiday name-sessions across 12 IS dates. Through the
provisional OOS cutoff it contains 52 usable weeknight name-sessions across 13
dates and 11 weekend/holiday name-sessions across 9 dates. All 15 IS/OOS trades
were weeknight entries; the weekend rule generated no entries.

## Readout

The frozen price-only mirror fails the submit-as-research performance bar: it is
negative in IS and provisional OOS even at the 15 bps stress case, and the OOS
base-cost win rate is zero. Sharpe decay is not meaningful because IS Sharpe is
already negative. A 30-calendar-day rolling OOS Sharpe is also unavailable until
the seven pending dates are observed.

This is evidence against price residuals alone, not a post-OOS authorization to
retune them. The project remains titled and tracked as Alpha Factory / After-Hours
Information Pricing; no Desk retitle or LLM implementation is made in this
checkpoint.
