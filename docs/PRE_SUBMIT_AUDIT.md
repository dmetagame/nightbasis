# NightBasis pre-submission audit

Audit date: 2026-09-17. Starting commit: `a25bacd4ea2531c0292ebf2f6f991ea28552dd75`, clean `main` tracking `origin/main`.

Submission: **AI Trading Desk / Information Extraction & Signal Generation**.
Deadline supplied for this audit: **2026-09-21 23:59 UTC+8**; retain the earlier 18:00 safety target.

Phase A inspected the live site, repository, history, and tests without changing product or research files. Its only documentation output is this report. Phase B is restricted to the documented URL/materials failures below. No research-number mismatch was found.

## Phase A results

**14 PASS / 2 FAIL / 0 WARN across the 16 numbered items.** Additional verification limitations and human actions are listed separately.

| # | Item | Phase A | Evidence |
| --- | --- | --- | --- |
| 1 | Public repository, README, MIT, no auth wall | PASS | Unauthenticated GitHub HTML and API return 200; API reports `private=false`, `visibility=public`, default branch `main`, license `MIT`. README covers purpose, fixtures, offline demo, frozen control and materials. |
| 2 | Four public routes | PASS | Curl and Chromium return 200 on `/`, `/desk`, `/method`, `/motion`, without login. Each title is `NightBasis Desk — Evidence before action`. |
| 3 | Old alias and primary URL | PASS | Legacy `https://web-zeta-two-67.vercel.app` returns 200 directly, with zero redirects. It remains an alias; it is not advertised as the primary host anywhere in the tracked repository at audit start. Primary docs point to `https://nightbasis.vercel.app`. |
| 4 | Replay, tests, schemas, labels | PASS | `make demo-replay` passes; 22/22 unit tests pass. All 12 freshly constructed records validate with jsonschema 4.26.0, `Draft202012Validator`, and `FormatChecker`; all remain `stand_down`. |
| 5 | Identical full freeze hash | PASS | README, live Method page at both widths, site source, and freeze JSON all contain the full hash below. Freeze JSON is byte-identical to commit `c92b9bd`. |
| 6 | Secret scan of tracked history | PASS | All reachable local refs: 39 commits, 182 unique file blobs, 9,781,251 bytes; no sensitive filenames or credential-pattern matches. Compressed market JSON was also decompressed for scanning. No secret values printed. See scope below. |
| 7 | Current submission track | PASS | `docs/SUBMISSION_FINAL.md` explicitly says `AI Trading Desk → Information Extraction & Signal Generation`. It does not submit under the former Alpha track. |
| 8 | Judge video | PASS | `web/demo/desk-walkthrough.mp4`: 110.000 seconds, 1,280,151 bytes, 1280×720, H.264, yuv420p, 30fps; within the requested 90–150 seconds. |
| 9 | X draft tags and live URL | FAIL | Required tag and mention are present, but the draft links only to GitHub. Replace its destination with the live Desk URL. |
| 10 | Research numbers versus site | PASS | Live Overview/Method show IS −1.58 at 15 bps, 79 days/10 trades, provisional OOS −5.57, weekend 0/26. All 12 `research.ts` snapshots match machine transcripts for y, z, signed info, label and reason. Signed info remains 0.855; Tesla remains exactly 1.235711, conventionally displayed to three decimals as 1.236. |
| 11 | No profitable-alpha or live-order claim | PASS | Site copy describes explanatory replay, failed price-only alpha, and no-trade verdicts. Desk integrity panel says `Execution: none`; source inspection found no claim of profitable shipped alpha or live order routing. |
| 12 | Negative-control honesty | PASS | Overview explicitly says the alpha failed and was not retuned. Method says price-only alpha was closed; the control stayed negative. README distinguishes the failed control from the shipped Desk. |
| 13 | Live GOOGL and Tesla reads | PASS | Browser clicks reproduce the values and reasons below at both widths, with normal and reduced motion. Autoplay is paused before clock selection. |
| 14 | Responsive quality and console | PASS | Complete repeat run: 16 route/width/motion combinations, no console or page errors. At top/middle/bottom, document width equals 1280 or 390. Clocks are at least 44px high; Desktop/Mobile Desk clock interaction succeeds. See initial-run caveat below. |
| 15 | Reduced motion | PASS | All four routes render without crashing at both widths; no Lenis class and zero pin spacers. Replay clocks remain usable. |
| 16 | README/submission links and materials | FAIL | README advertises an optional Pages mirror that returns 404. Submission materials index lists nonexistent `reports/playbook/`. The handoff still says to record the now-completed video and claims current `gh` authentication. Other relative Markdown links resolve. X help links return 403 to curl: verification warning, not proven deleted pages. |

Full frozen hash:
`0898cca4374ae68dfbc85ae73138f710539d314800de8548d3b37f28fd0ba5a0`.

## Live replay evidence

| Fixture / snapshot | y on screen | Residual z | Signed info / direction | Reason | Verdict |
| --- | --- | --- | --- | --- | --- |
| Material filing / 16:30 | −1.965% | −3.494552 | 0.855 / +1 | `event_price_direction_conflict` | No trade |
| Uninformed move / 08:30 | −2.640% | 1.235711 | 0.000 / no qualifying event | `uninformed_but_below_washout` | No trade |

The GOOGL evidence remains the 16:01 ET filing, accession `sec-0001652044-26-000066`. Its direction is not inferred from the negative tape. Tesla's exact residual remains below 1.25.

## Verification commands and scope

- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: 22 passed in 0.606s.
- `make demo-replay`: passes; regenerated reports remain byte-identical in Git.
- `cd web && npm run build:static`: passes, 2287 Vite modules.
- Schema validation used an isolated temporary environment because system jsonschema 3.2.0 does not implement Draft 2020-12. No project dependency was changed.
- Browser visits were unauthenticated, with 1280×900 and 390×844 viewports, normal and forced reduced motion. One initial `/desk` visit timed out locating the fixture tab; a full repeat completed successfully with no console errors. Cause of the initial failure was not established.
- Secret checks covered filenames and private-key headers, provider/GitHub/Slack tokens, AWS/Google keys, JWTs, credential-bearing URLs, and literal credential assignments across reachable tracked-file history. This is a pattern-based scan, not a proof that arbitrary unlabeled strings cannot be secrets. Unreachable Git objects and credentials outside the repository were not inspected.
- GitHub CLI's saved authentication is invalid. Public access checks used no credentials; ordinary Git HTTPS pushes have worked independently in prior checkpoints.

## Phase B plan

1. Fix item 9: replace the X draft's GitHub-only URL with the live demo URL, retaining the required tag and mention.
2. Fix item 16: remove the dead Pages link; list only existing submitted materials; link the completed subtitled video, narration and shot log; clearly mark Playbook screenshots as a pending human deliverable; reconcile handoff copy.
3. Refresh the secrets-scan documentation with this audit's tracked-history scope.
4. Recheck failed items, replay, whitespace and protected-path diff. No product source, GSAP, research, fixtures, labels, freeze or numbers may change.

## Remaining human actions / warnings

- Playbook screenshots have not been captured; `reports/playbook/` does not exist. The recipe exists, but screenshots are not delivered yet.
- The X post URL field is blank. Posting and form submission were not performed by this audit.
- The two external X help citations return HTTP 403 to automated requests. Their accessibility in a normal logged-in browser is unverified.
- The protected historical `reports/price-only-metrics.md` ends with the old Alpha-track label from that checkpoint. Its numerical results match the site; current submission materials must explain that the Desk relock supersedes that historical track statement. The protected report must not be rewritten.
- OOS remains the disclosed provisional 23-day read through 2026-09-11. This audit does not extend it or fabricate observations for the seven originally pending dates.

## Phase B result

**Final: 15 PASS / 0 FAIL / 1 WARN across the 16 numbered items.** Items 1–15 now pass. Item 16 is WARN only because the two retained external X help citations return 403 to automated requests; no broken repository-material link remains.

| Original failure | Permitted fix | Recheck |
| --- | --- | --- |
| 9 — GitHub-only X destination | X draft now links to `https://nightbasis.vercel.app/desk`; wording matches the web replay | PASS: target returns 200; required hashtag and mention retained; 266 effective characters with the existing 23-character URL accounting |
| 16 — dead Pages URL | Removed the 404 mirror advertisement from README | PASS: Vercel remains primary; no nonexistent mirror is advertised |
| 16 — nonexistent/incomplete materials and stale handoff | Removed pending `reports/playbook/` from the available-materials index; added the completed video, caption source, narration, shot log and audit; clarified pending screenshot capture and current CLI auth status | PASS for local materials: 31/31 index entries exist, all relative Markdown links resolve; historical Alpha wording explained without modifying protected reports |

Final replay recheck passes. `git diff --check` passes. Diff against the starting commit is empty for `src/nightbasis`, `fixtures`, `web/src/data/research.ts`, all `reports`, `schemas`, `prompts`, and `data`. No website source, build configuration, animation, or executable policy was changed.

Files changed for this audit: `README.md`, `docs/SUBMISSION_FINAL.md`, `docs/WHAT_YOU_DO_NEXT.md`, `docs/SECRETS_SCAN.md`, this audit, and the required `docs/PROJECT_STATE.md` handoff.
