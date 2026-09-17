# NightBasis Desk

An evidence-first desk that explains overnight rToken moves and knows when to
say no trade.

Public materials: https://github.com/dmetagame/nightbasis

Primary live demo: https://nightbasis.vercel.app

GitHub Pages is an optional deployment path; no Pages mirror is currently published.

Local demo: `make site`, then open the URL printed by Vite. The site lives in
[`web/`](web/) and does not change the frozen Python research replay.

## What NightBasis Desk is

NightBasis Desk explains whether an overnight rToken move looks supported by
company information or disconnected from the available evidence. It combines a
frozen price-only factor model with point-in-time event extraction, then emits an
auditable label, reason, and memo. It does not place orders or issue trade
instructions.

| Fixture | Three-sentence judge read |
| --- | --- |
| Flat — rGOOGL, 2026-08-14 | rGOOGL moved -0.009%, -0.009%, +0.009%, and +0.251% at the four snapshots, with no qualifying event. The two negative snapshots remained below the frozen washout threshold, while the later moves were nonnegative. NightBasis Desk stood down: no trade. |
| Material news — rGOOGL, session starting 2026-07-22 | Alphabet's 16:01 ET 8-K reported $119.8B revenue (+24% YoY), $24.8B Cloud revenue (+82%), a 34% operating margin, and $9.11 diluted EPS. The event scored `signed_info=0.855`, but rGOOGL moved -1.965%, -5.138%, -4.407%, and -7.089%, producing `event_price_direction_conflict`. NightBasis Desk stood down: no trade. |
| No qualifying company event — rTSLA, 2026-06-23 | The bounded Tesla SEC and IR feed contained no qualifying event, while rTSLA moved -0.038%, -0.214%, -1.253%, and -2.640%. At 08:30, the residual was `z=1.235711`, below the frozen 1.25 washout threshold. NightBasis Desk stood down: no trade. |

Run the complete offline replay:

```bash
make demo-replay
```

The command uses exactly the three frozen fixtures, retains the machine
transcripts, and performs no network or execution action.

## Frozen negative control

The price-only control was frozen before its OOS read:
`0898cca4374ae68dfbc85ae73138f710539d314800de8548d3b37f28fd0ba5a0`
(commit `c92b9bd`). We did not retune it after it lost money.

- IS: 79 calendar days, 7 traded days, 10 trades; Sharpe -1.58 at 15 bps per
  side and -2.96 at 25 bps per side.
- Provisional OOS: 23 observed calendar days, 3 traded days, 5 trades; Sharpe
  -5.57 at 15 bps per side.
- Weekend rule: 26 eligible nights and 0 entries.

The failed control is evidence for the product decision: NightBasis ships as an
information-extraction and signal-explanation desk, not executable alpha.

The historical control report retains the Alpha-track wording from its original
checkpoint. The current submission is **AI Trading Desk / Information Extraction
& Signal Generation**; the later Desk relock supersedes that historical wording.

## Materials

- [Read the judge-facing replay](reports/judge-replay.md)
- [Inspect the frozen price-only metrics](reports/price-only-metrics.md)
- [Review the submission draft](docs/SUBMISSION_DRAFT.md)
- [Copy the final form pack](docs/SUBMISSION_FINAL.md)
- [Follow the Playbook mirror recipe](docs/PLAYBOOK_MIRROR.md)
- [Watch the subtitled 110-second demo](web/demo/desk-walkthrough.mp4)
- [Read the voiceover](web/demo/VOICEOVER.txt)
- [Inspect the actual shot timings](web/demo/SHOT_LOG.md)
- [Review the pre-submission audit](docs/PRE_SUBMIT_AUDIT.md)
- [Publish the repository and tags](docs/PUBLISH_COMMANDS.md)
- [Run the GitHub publish checklist](docs/GITHUB_PUBLISH_CHECKLIST.md)
- [Review the secret scan](docs/SECRETS_SCAN.md)
- [Complete the human handoff](docs/WHAT_YOU_DO_NEXT.md)
- [Read the MIT license](LICENSE)

Playbook screenshots are still pending. The mirror recipe is available above;
screenshots will be added to `reports/playbook/` after capture.
