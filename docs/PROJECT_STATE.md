# Project State

> Living handoff for Codex sessions. Read this file before working. Do not put
> secrets or raw credential-bearing values here.

Last updated: `2026-09-11T21:53:29+01:00`
Status: `ALPHA ACTIVE; PRICE-ONLY BASELINE FAILED PROVISIONAL OOS`
Active objective: Preserve the failed price-only control and decide the next Alpha experiment without OOS retuning.

## Workspace

- Repository: local Git repository; no remote configured
- Worktree: `/home/rouma/projects/nightbasis`
- Branch: `main`
- Latest substantive checkpoint: `e5f3456d3d0858140df8758e79e7eeae3abb1249` (provisional OOS artifacts); IS freeze checkpoint: `c92b9bd776ce43cf71d94ba90d3db23622b4395c`
- Protected releases/artifacts: none

## Constraints

- Do not build the LLM pipeline until the price-only ledger exists.
- `rQQQ` is the primary equity factor and `rSPY` is fallback; either may make a name-session usable. BTC and ETH are supplementary factors. None is tradable.
- Frozen split: IS 2026-06-02 through 2026-08-19; OOS 2026-08-20 through 2026-09-18. Keep all calendar days, including flat days, in daily returns.
- Weekend/US-holiday nights use BTC+ETH-only fair value, require z >= 1.5, and prohibit washout entries. Weeknights require rQQQ or rSPY and use the locked z entry. Long/flat only.
- Historical Reality order books/fills are whitelist-gated. Never mislabel an OHLC spread estimate as observed bid/ask.
- Long/flat only; the later strategy term is “buy uninformed washout.”
- Python is authoritative for news features; the eventual Playbook mirror is price-only.
- The future information feature is `direction * materiality * confidence`; novelty is a gate, not a multiplier.
- Future performance classification must use the accepted two-bar submit-as-alpha / submit-as-research / kill policy; OOS Sharpe 1.0 is aspirational, not a hard eligibility rule.

## Current Context

- Frozen core: `rNVDA`, `rTSLA`, `rAAPL`, `rGOOGL`.
- Frozen add tier: `rAMD`, `rCVX`, `rOXY`, `rMETA`.
- Out unless newly audited: `rORCL`, `rCRCL`, `rMRVL`, `rINTC`, `rMSTR`, `rMU`, `rXOM`.
- Public UTA v3 supplies instruments, historical OHLCV/turnover, live platform turnover, and best bid/ask.
- Historical session spread is screened with a labeled Corwin-Schultz OHLC proxy; live ticker snapshots provide observed median quoted spread.

## Work Completed

- Initialized the repository and minimal standard-library audit package.
- Added `src/nightbasis/audit_data.py` and deterministic unit coverage for pagination, flat-price spread, and the Juneteenth calendar closure.
- Generated `reports/data-audit.json` and `reports/data-audit.md` from live public Bitget UTA data.
- Replaced the superseded internal gate with the frozen core/add book, either-factor rule, exact 16:15–09:00 ET window, and flat-inclusive calendar split.
- Re-audited with 15-minute candles. Core+add and core-only each provide 57 strategy days; add contributes zero unique days. Recommended core-only.
- Recounted calendar nights under the weekend rule: core-only has 83 strategy days (57 weeknight, 26 weekend/holiday), so the Alpha continuation gate passes.
- Persisted the exact public Bitget input snapshot at `data/market-snapshot.json.gz` (SHA-256 `1b799416618665318eab340eeaaa2ff96ba3c068068ad9ef25dfc4eb84226ec6`).
- Implemented `src/nightbasis/price_backtest.py`: exact-anchor price-only fair value, long/flat execution, flat-inclusive daily ledgers, and 15/25/37.5 bps-per-side cost scenarios.
- Froze the IS model and thresholds in `reports/price-only-freeze.json` before any OOS read. Internal freeze hash: `0898cca4374ae68dfbc85ae73138f710539d314800de8548d3b37f28fd0ba5a0`.
- IS at the 25 bps-per-side base case: 79 calendar days, 72 flat, 7 traded, 10 trades, -0.1502% total return, Sharpe -2.96, Sortino -3.32, max drawdown -0.1502%. This price-only baseline is weak; it remains frozen so the OOS test is honest.
- Ran the first OOS read with no refit. Through 2026-09-11 the base case has 23 observed calendar days, 20 flats, 3 traded days, 5 trades, -0.1995% total return, Sharpe -5.76, Sortino -5.62, max drawdown -0.1995%, and 0% win rate. Seven future dates remain pending.
- Wrote `reports/price-only-metrics.md` with the audit recount and all IS/OOS cost scenarios. The price-only baseline fails the research bar even at 15 bps per side; this checkpoint does not retitle the locked Alpha track.

## Verification

| Check | Result | Evidence/date |
| --- | --- | --- |
| Git/GitHub | blocked | Local repo initialized; no remote; `gh auth status` reports expired authentication, 2026-09-11 |
| Unit tests | passed | `PYTHONPATH=src python3 -m unittest discover -s tests -v` → 3/3 passed, 2026-09-11 |
| Static compilation | passed | `python3 -m compileall -q src tests`, 2026-09-11 |
| Superseded first audit | superseded | Prior 12-name/intersection gate was replaced by user instruction, 2026-09-11 |
| Amended re-audit | contingency triggered | 57 core+add strategy days; 57 core-only; 79 IS and 30 OOS calendar days including flats; only 23 OOS days observable on 2026-09-11 |
| Re-audit tests | passed | 4/4 unit tests, static compilation, JSON assertions, and `git diff --check`, 2026-09-11 |
| Weekend-rule audit | passed | 83 core-only strategy days: 57 weeknight + 26 weekend/holiday; 79 IS and 30 OOS calendar days including flats, 2026-09-11 |
| Price-only unit/static checks | passed | 9/9 tests, `compileall`, and `git diff --check`, 2026-09-11 |
| IS freeze | completed | Thresholds/models frozen with hash `0898cca...`; OOS not read, 2026-09-11 |
| Provisional OOS | failed price-only research bar | At 25 bps/side: 23 observed days, 20 flat, 5 trades, -0.1995% return, Sharpe -5.76; 7 dates pending, 2026-09-11 |
| Git checkpoint | local only | IS freeze `c92b9bd`; provisional OOS `e5f3456`; no remote configured and GitHub authentication expired, 2026-09-11 |

## Risks And Blockers

- GitHub backup is blocked until authentication is refreshed and a remote is configured.
- Historical spread is necessarily an estimator without Reality data whitelist access.
- The earlier 57-day contingency is superseded: it omitted BTC/ETH-only weekend/holiday nights. The corrected count is 83 and Alpha remains active.
- Seven OOS calendar days (2026-09-12 through 2026-09-18) are future relative to the audit and were not fabricated as observed data.
- OOS has only 23 observable calendar days as of 2026-09-11; the remaining seven must not be fabricated.
- The price-only rule is negative in both IS and provisional OOS at every specified cost. It must remain a frozen control, not be tuned after this read.
- A 30-calendar-day rolling OOS Sharpe and final two-bar classification are unavailable until 2026-09-18 data is captured.

## Next Actions

1. Keep the Alpha Factory / After-Hours Information Pricing title; do not retune against provisional OOS.
2. On user direction, either implement the pre-specified information feature as a distinct Alpha experiment or wait to refresh the seven pending OOS dates.
3. Configure a remote and refresh GitHub CLI authentication before claiming remote backup.

## Session Handoff

- Inspect `reports/data-audit.md` and the per-session evidence in `reports/data-audit.json`.
- The weekend-aware audit is `PASS`; continue only with the ordered price-only/freeze/OOS tasks.

## Change Log

| Timestamp | Session/agent | Event | Result |
| --- | --- | --- | --- |
| 2026-09-11T15:16:29+01:00 | Codex | Initialized NightBasis Day-1 audit | Implementation in progress; remote/auth blockers recorded |
| 2026-09-11T16:15:28+01:00 | Codex | Completed strict live data audit | Failed: 4/12 eligible tradables and 55/60 common usable sessions; downstream work blocked |
| 2026-09-11T16:15:28+01:00 | Codex | Created local Day-1 checkpoint | Commit `0b826c1`; push unavailable because no remote is configured and GitHub auth is expired |
| 2026-09-11T21:03:22+01:00 | Codex | Completed amended 15-minute re-audit | 57 strategy days triggers Desk contingency; core-only recommended; no downstream work started |
| 2026-09-11T21:03:22+01:00 | Codex | Created local re-audit checkpoint | Commit `10daa75`; push unavailable because no remote is configured and GitHub auth is expired |
| 2026-09-11T21:45:06+01:00 | Codex | Applied weekend/holiday rule and persisted market snapshot | PASS: 83 core-only strategy days; Alpha contingency overridden |
| 2026-09-11T21:51:19+01:00 | Codex | Implemented and froze price-only IS baseline | Freeze `0898cca...`; base-cost IS Sharpe -2.96; OOS remains unread |
| 2026-09-11T21:53:29+01:00 | Codex | Ran first no-refit OOS evaluation | Price-only baseline fails provisionally at all costs; seven dates pending; Alpha title retained |
| 2026-09-11T21:53:29+01:00 | Codex | Created local OOS checkpoint | Commit `e5f3456`; push unavailable because no remote is configured and GitHub auth is expired |
