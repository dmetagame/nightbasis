# Project State

> Living handoff for Codex sessions. Read this file before working. Do not put
> secrets or raw credential-bearing values here.

Last updated: `2026-09-11T16:15:28+01:00`
Status: `BLOCKED AT DAY-1 DATA GATE`
Active objective: Resolve or accept the failed NightBasis data audit before any downstream strategy work.

## Workspace

- Repository: local Git repository; no remote configured
- Worktree: `/home/rouma/projects/nightbasis`
- Branch: `main`
- Implementation checkpoint: `0b826c136674f9c3a9965dfa9a2ca77830bf59d2`
- Protected releases/artifacts: none

## Constraints

- Day-1 audit only; do not build the LLM pipeline, Agent Hub demo, or submission prose until `audit-data` passes.
- `rSPY` and `rQQQ` are factor-only instruments and can never enter the tradable eligible book.
- Determine IS/OOS boundaries from sessions with nonzero volume and usable spread; do not assume calendar ranges.
- Historical Reality order books/fills are whitelist-gated. Never mislabel an OHLC spread estimate as observed bid/ask.
- Long/flat only; the later strategy term is “buy uninformed washout.”
- Python is authoritative for news features; the eventual Playbook mirror is price-only.
- The future information feature is `direction * materiality * confidence`; novelty is a gate, not a multiplier.
- Future performance classification must use the accepted two-bar submit-as-alpha / submit-as-research / kill policy; OOS Sharpe 1.0 is aspirational, not a hard eligibility rule.

## Current Context

- Candidate tradables: `rAAPL`, `rAMD`, `rCRCL`, `rCVX`, `rGOOGL`, `rINTC`, `rMETA`, `rMRVL`, `rMSTR`, `rMU`, `rNVDA`, `rORCL`, `rOXY`, `rTSLA`, `rXOM`.
- Factors: `rSPY`, `rQQQ`; future cross-asset factors also include BTC and ETH.
- Public UTA v3 supplies instruments, historical OHLCV/turnover, live platform turnover, and best bid/ask.
- Historical session spread is screened with a labeled Corwin-Schultz OHLC proxy; live ticker snapshots provide observed median quoted spread.

## Work Completed

- Initialized the repository and minimal standard-library audit package.
- Added `src/nightbasis/audit_data.py` and deterministic unit coverage for pagination, flat-price spread, and the Juneteenth calendar closure.
- Generated `reports/data-audit.json` and `reports/data-audit.md` from live public Bitget UTA data.
- Enforced a 12-symbol breadth gate, 60 usable-session history gate, and factor availability for both `rSPY` and `rQQQ`.

## Verification

| Check | Result | Evidence/date |
| --- | --- | --- |
| Git/GitHub | blocked | Local repo initialized; no remote; `gh auth status` reports expired authentication, 2026-09-11 |
| Unit tests | passed | `PYTHONPATH=src python3 -m unittest discover -s tests -v` → 3/3 passed, 2026-09-11 |
| Static compilation | passed | `python3 -m compileall -q src tests`, 2026-09-11 |
| Live data audit | failed as designed | 4/12 required tradables eligible; 55/60 required common usable sessions; command exited 2, 2026-09-11 |
| Report integrity | passed | JSON asserts `FAIL`, 4 eligible symbols, and 55 common sessions; `git diff --check` passed, 2026-09-11 |

## Risks And Blockers

- GitHub backup is blocked until authentication is refreshed and a remote is configured.
- Historical spread is necessarily an estimator without Reality data whitelist access.
- Only `rAAPL`, `rGOOGL`, `rNVDA`, and `rTSLA` have at least 60 usable sessions under the locked filters.
- The common calendar falls to 55 sessions when both factor-only instruments are required; `rSPY` itself has only 57 usable sessions.
- No IS/OOS boundary is valid under the gate. Do not proceed to the LLM, Playbook, Agent Hub demo, or submission layers.

## Next Actions

1. Decide whether to obtain whitelisted historical spread data, change the historical spread proxy/coverage definition with methodological justification, or abandon NightBasis as alpha.
2. Rerun the same audit after any approved methodology change; downstream work remains prohibited until status is `PASS`.

## Session Handoff

- Inspect `reports/data-audit.md` and the per-session evidence in `reports/data-audit.json`.
- The current audit status is `FAIL`; do not proceed past Day 1.

## Change Log

| Timestamp | Session/agent | Event | Result |
| --- | --- | --- | --- |
| 2026-09-11T15:16:29+01:00 | Codex | Initialized NightBasis Day-1 audit | Implementation in progress; remote/auth blockers recorded |
| 2026-09-11T16:15:28+01:00 | Codex | Completed strict live data audit | Failed: 4/12 eligible tradables and 55/60 common usable sessions; downstream work blocked |
| 2026-09-11T16:15:28+01:00 | Codex | Created local Day-1 checkpoint | Commit `0b826c1`; push unavailable because no remote is configured and GitHub auth is expired |
