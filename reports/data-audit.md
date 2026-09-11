# NightBasis Day-1 Data Audit

Generated: `2026-09-11T20:40:17.594301+00:00`

Observed market data ends at `2026-09-11`; the frozen OOS window ends at `2026-09-18`. Future days are counted in the frozen daily-return calendar but are not treated as observed.

Historical spread is a Corwin-Schultz estimate from 15-minute OHLC, not an observed order-book spread. Median quoted spread and platform turnover are repeated live ticker snapshots.

| Tier | Symbol | First live volume | Zero-volume sessions | Usable sessions | Median platform turnover (24h) | Median quoted spread | Historical spread proxy |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| core | RNVDAUSDT | 2026-04-23 | 1.0% | 82 | $425,233 | 0.92 bps | 2.26 bps |
| core | RTSLAUSDT | 2026-06-01 | 1.0% | 66 | $79,819 | 0.82 bps | 1.57 bps |
| core | RAAPLUSDT | 2026-06-01 | 1.0% | 67 | $171,274 | 2.11 bps | 1.07 bps |
| core | RGOOGLUSDT | 2026-06-01 | 1.0% | 67 | $938,703 | 5.32 bps | 1.11 bps |
| add | RAMDUSDT | 2026-06-02 | 1.0% | 67 | $3,866,121 | 3.69 bps | 2.41 bps |
| add | RCVXUSDT | 2026-06-09 | 17.0% | 50 | $994,012 | 41.99 bps | 0.00 bps |
| add | ROXYUSDT | 2026-06-10 | 17.2% | 51 | $12,792,639 | 27.68 bps | 0.00 bps |
| add | RMETAUSDT | 2026-06-01 | 2.0% | 65 | $400,037 | 8.34 bps | 1.72 bps |

**Strategy days, core + add:** 83

- Weeknight: 57
- Weekend/holiday: 26

**Strategy days, core only:** 83

- Weeknight: 57
- Weekend/holiday: 26

**Incremental days supplied by add tier:** 0

**IS daily-return calendar:** 79 days (`2026-06-02` through `2026-08-19`)

**OOS daily-return calendar:** 30 days (`2026-08-20` through `2026-09-18`); 23 observed and 7 future as of audit

**Recommendation:** `core-only` — The add tier supplies only 0 unique strategy days; it does not improve calendar coverage and adds execution/model-selection complexity.

**Audit result:** PASS


## Factor-only instruments

- `RQQQUSDT` (primary equity factor): 65 raw usable sessions; 4.9% zero-volume sessions.
- `RSPYUSDT` (fallback equity factor): 61 raw usable sessions; 8.8% zero-volume sessions.
- `BTCUSDT` (supplementary crypto factor): 102 raw usable sessions; 0.0% zero-volume sessions.
- `ETHUSDT` (supplementary crypto factor): 102 raw usable sessions; 0.0% zero-volume sessions.
