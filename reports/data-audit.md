# NightBasis Day-1 Data Audit

Generated: `2026-09-11T15:12:50.480401+00:00`

Historical spread is a Corwin-Schultz OHLC estimate, not an observed order-book spread. Median quoted spread and platform turnover are repeated live ticker snapshots.

| Symbol | First live volume | Zero-volume sessions | Usable sessions | Median platform turnover (24h) | Median quoted spread | Historical spread proxy | Eligible |
| --- | --- | ---: | ---: | ---: | ---: | ---: | :---: |
| RAAPLUSDT | 2026-06-01 | 0.0% | 63 | $309,506 | 1.19 bps | 4.20 bps | yes |
| RAMDUSDT | 2026-06-01 | 0.0% | 49 | $3,858,052 | 3.60 bps | 6.58 bps | no |
| RCRCLUSDT | 2026-06-01 | 0.0% | 49 | $886,518 | 9.58 bps | 14.50 bps | no |
| RCVXUSDT | 2026-06-01 | 0.0% | 52 | $2,212,888 | 1.88 bps | 1.59 bps | no |
| RGOOGLUSDT | 2026-06-01 | 0.0% | 63 | $206,606 | 1.46 bps | 4.34 bps | yes |
| RINTCUSDT | 2026-06-01 | 0.0% | 40 | $2,199,429 | 1.94 bps | 12.11 bps | no |
| RMETAUSDT | 2026-06-01 | 0.0% | 56 | $1,115,314 | 3.61 bps | 4.52 bps | no |
| RMRVLUSDT | 2026-06-01 | 0.0% | 39 | $599,795 | 8.11 bps | 9.77 bps | no |
| RMSTRUSDT | 2026-06-01 | 0.0% | 46 | $1,186,163 | 5.90 bps | 13.19 bps | no |
| RMUUSDT | 2026-06-01 | 0.0% | 43 | $400,199 | 2.89 bps | 11.32 bps | no |
| RNVDAUSDT | 2026-06-01 | 0.0% | 66 | $412,610 | 0.91 bps | 7.55 bps | yes |
| RORCLUSDT | 2026-06-01 | 0.0% | 53 | $682,818 | 12.36 bps | 7.17 bps | no |
| ROXYUSDT | 2026-06-01 | 0.0% | 51 | $7,152,172 | 1.65 bps | 2.72 bps | no |
| RTSLAUSDT | 2026-06-01 | 0.0% | 67 | $95,740 | 1.78 bps | 4.64 bps | yes |
| RXOMUSDT | 2026-06-01 | 0.0% | 50 | $433,283 | 2.43 bps | 2.85 bps | no |

**Eligible book:** RAAPLUSDT, RGOOGLUSDT, RNVDAUSDT, RTSLAUSDT

**Eligible tradables:** 4 / 12 required

**Common usable sessions:** 55

**Audit result:** FAIL

No valid split: eligible tradables 4 < 12; common usable sessions 55 < 60 with 30 OOS sessions required

## Factor-only instruments

- `RSPYUSDT`: 57 usable sessions; 0.0% zero-volume sessions.
- `RQQQUSDT`: 65 usable sessions; 0.0% zero-volume sessions.
