# NightBasis Day-1 Data Audit

Generated: `2026-09-11T19:57:52.772411+00:00`

Observed market data ends at `2026-09-11`; the frozen OOS window ends at `2026-09-18`. Future days are counted in the frozen daily-return calendar but are not treated as observed.

Historical spread is a Corwin-Schultz estimate from 15-minute OHLC, not an observed order-book spread. Median quoted spread and platform turnover are repeated live ticker snapshots.

| Tier | Symbol | First live volume | Zero-volume sessions | Usable sessions | Median platform turnover (24h) | Median quoted spread | Historical spread proxy |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| core | RNVDAUSDT | 2026-04-23 | 0.0% | 57 | $408,012 | 1.15 bps | 2.46 bps |
| core | RTSLAUSDT | 2026-06-01 | 0.0% | 57 | $79,399 | 2.74 bps | 2.08 bps |
| core | RAAPLUSDT | 2026-06-01 | 0.0% | 57 | $120,657 | 0.60 bps | 1.35 bps |
| core | RGOOGLUSDT | 2026-06-01 | 0.0% | 57 | $932,134 | 3.84 bps | 1.59 bps |
| add | RAMDUSDT | 2026-06-02 | 0.0% | 57 | $3,866,121 | 3.49 bps | 2.43 bps |
| add | RCVXUSDT | 2026-06-09 | 0.0% | 50 | $994,012 | 34.64 bps | 0.00 bps |
| add | ROXYUSDT | 2026-06-10 | 0.0% | 51 | $12,792,639 | 24.42 bps | 0.00 bps |
| add | RMETAUSDT | 2026-06-01 | 0.0% | 57 | $399,915 | 10.81 bps | 1.90 bps |

**Strategy days, core + add:** 57

**Strategy days, core only:** 57

**Incremental days supplied by add tier:** 0

**IS daily-return calendar:** 79 days (`2026-06-02` through `2026-08-19`)

**OOS daily-return calendar:** 30 days (`2026-08-20` through `2026-09-18`); 23 observed and 7 future as of audit

**Recommendation:** `core-only` — The add tier supplies only 0 unique strategy days; it does not improve calendar coverage and adds execution/model-selection complexity.

**Audit result:** DESK_CONTINGENCY


## Factor-only instruments

- `RQQQUSDT` (primary equity factor): 57 raw usable sessions; 0.0% zero-volume sessions.
- `RSPYUSDT` (fallback equity factor): 57 raw usable sessions; 0.0% zero-volume sessions.
- `BTCUSDT` (supplementary crypto factor): 71 raw usable sessions; 0.0% zero-volume sessions.
- `ETHUSDT` (supplementary crypto factor): 71 raw usable sessions; 0.0% zero-volume sessions.
