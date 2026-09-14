# NightBasis Desk

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

- [Read the judge-facing replay](reports/judge-replay.md)
- [Review the submission draft](docs/SUBMISSION_DRAFT.md)
- [Run the GitHub publish checklist](docs/GITHUB_PUBLISH_CHECKLIST.md)
