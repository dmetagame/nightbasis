# NightBasis Desk — final submission copy

Each section below is a copy-paste block for the submission form.

## Project name

```text
NightBasis Desk
```

## Track / sub-theme

```text
AI Trading Desk → Information Extraction & Signal Generation
```

## Public materials URL

```text
Primary live demo: https://nightbasis.vercel.app
Research repository and materials: https://github.com/dmetagame/nightbasis
```

## Thesis

```text
Overnight rToken moves can mix company information, broad-market repricing, and thin-market noise. NightBasis Desk compares each move with a frozen factor-model fair value and company evidence available at that exact snapshot. It produces an auditable label, reason, source record, and memo—and explicitly says no trade when the evidence does not support a defensible interpretation.
```

## Target user and product value

```text
NightBasis Desk is for crypto-native traders and risk operators monitoring tokenized US equities outside US cash-market hours. It turns an unexplained overnight percentage move into a reproducible answer to three questions: what moved, what public evidence existed at that time, and why the Desk stood down. The shipped product explains signals; it does not place orders or claim profitable alpha.
```

## Validation data and key metrics

```text
The frozen core book is rNVDA, rTSLA, rAAPL, and rGOOGL. rQQQ is the primary equity factor, rSPY is the fallback, and BTC/ETH are supplementary factors; factors are never traded.

The price-only negative control was frozen before the OOS read under hash 0898cca4374ae68dfbc85ae73138f710539d314800de8548d3b37f28fd0ba5a0 (commit c92b9bd). We did not retune it after seeing the losses.

IS: 79 calendar days, 7 traded days, 10 trades. Sharpe was −1.58 at 15 bps per side and −2.96 at 25 bps per side.

Provisional OOS through 2026-09-11: 23 observed calendar days, 3 traded days, 5 trades. Sharpe was −5.57 at 15 bps per side.

Weekend rule: 26 nights and 0 entries.

The failed control is published as negative evidence. It showed that price residuals alone were not strong enough for an executable alpha claim, so NightBasis was narrowed to an information-extraction and signal-explanation desk.

Three locked real-date fixtures provide 12 point-in-time focus snapshots, all stand_down under the frozen rules:

1. Flat rGOOGL session, 2026-08-14.
2. rGOOGL session_start 2026-07-22T16:15:00-04:00: Alphabet 8-K accepted at 16:01 ET, accession sec-0001652044-26-000066. The event score is signed_info=0.855 with direction=+1, while rGOOGL moved −1.97% at 16:30, −5.14% at 20:00, and −7.09% at 08:30. The reason is event_price_direction_conflict; no trade.
3. rTSLA, 2026-06-23: no qualifying Tesla SEC/IR event in the bounded window. At 08:30, y=−2.64% and z=1.236, below the frozen 1.25 washout threshold. The reason is uninformed_but_below_washout; no trade.

The offline replay completes in about 0.05 seconds. The latest verification passed 22 tests and validated all 12 records.
```

## Progress

```text
Complete: public Bitget rToken data audit; frozen price-only negative control; flat-inclusive IS and provisional OOS ledgers; frozen event_score_v1 prompt; temperature-zero human-v1 cached fixture scores; deterministic point-in-time labeler and reason enum; three locked real-date fixtures; 12 machine-readable records; human judge replay; offline Make demo; schemas; tests; secret scan; and publication checklist.

Not built by design: order routing, executable alpha, live Agent Hub orders, a fourth fixture, or any post-OOS retuning.
```

## Deliverables

```text
- Production NightBasis Desk web demo hosted at the domain root on Vercel.
- Public repository with reproducible source, frozen inputs, schemas, tests, and documentation.
- make demo-replay: offline replay of exactly three fixtures and four focus snapshots per fixture.
- Machine transcripts exposing t, y, z, signed_info, event ID, label, reason, kill state, and memo.
- Judge-facing replay with percentage moves, timestamped 8-K facts, and explicit no-trade decisions.
- Frozen negative-control metrics and daily/trade ledgers at 15/25/37.5 bps per side.
- Price-only Bitget Playbook mirror recipe and screenshot checklist, explicitly labeled as a negative control rather than the shipped product.
- Subtitled 110-second judge walkthrough, matching voiceover text, and actual shot log in web/demo/.
```

Playbook screenshots are pending human capture; the recipe is delivered, but
`reports/playbook/` is not yet an available submission artifact.

## Role of the LLM

```text
The frozen LLM contract reads only company evidence timestamped at or before each snapshot and returns structured JSON: qualifying event, direction, materiality, confidence, novelty gate, signed information, and explanation. signed_info = direction × materiality × confidence; novelty is a gate, not a multiplier.

The fixture outputs are disclosed human-v1 caches conforming to the frozen event_score_v1 schema, with temperature 0. They do not pretend that a live model call occurred. The LLM does not see future snapshots, choose stocks, set thresholds, size positions, or trade. Deterministic Python owns price calculations, quality and timing checks, labels, reasons, and the final no-trade memo.
```

## Take on AI trading

```text
AI trading is most credible when AI structures messy evidence instead of acting as an unaccountable stock picker. Every claim should trace to a timestamped source, every model output should be reproducible, and deterministic controls should be able to reject the AI's interpretation. A serious system must publish negative controls and stand down when evidence and price disagree. NightBasis Desk demonstrates that discipline: all three locked fixtures end with no trade.
```

## Exact X post

```text
NightBasis Desk explains overnight rToken moves with point-in-time company evidence and a frozen factor baseline. It exposes conflicts and says “no trade” instead of forcing alpha. Three real-date fixtures. Replay: https://nightbasis.vercel.app/desk #BitgetHackathon @Bitget_AI
```

With X's link treatment, this post remains within the documented
[280-character standard composer](https://help.x.com/en/using-x/how-to-post)
because X [counts the shortened URL as 23 characters](https://help.x.com/en/using-x/how-to-post-a-link):
266 effective characters.

## X post URL

```text

```

## Materials index

```text
README.md
LICENSE
docs/SECRETS_SCAN.md
docs/SUBMISSION_DRAFT.md
docs/SUBMISSION_FINAL.md
docs/PLAYBOOK_MIRROR.md
docs/VIDEO_SHOT_LIST.md
docs/PUBLISH_COMMANDS.md
docs/GITHUB_PUBLISH_CHECKLIST.md
docs/WHAT_YOU_DO_NEXT.md
docs/PRE_SUBMIT_AUDIT.md
web/demo/desk-walkthrough.mp4
web/demo/VOICEOVER.txt
web/demo/VOICEOVER.ass
web/demo/SHOT_LOG.md
reports/judge-replay.md
reports/reason-matrix.md
reports/price-only-metrics.md
reports/price-only-freeze.json
reports/price-only-is-daily.csv
reports/price-only-is-trades.csv
reports/price-only-oos-daily.csv
reports/price-only-oos-trades.csv
reports/replay-transcripts/flat-rgoogl-2026-08-14.txt
reports/replay-transcripts/material-news-rgoogl-2026-07-23.txt
reports/replay-transcripts/large-move-no-event-rtsla-2026-06-23.txt
prompts/event_score_v1.txt
schemas/event-score.schema.json
schemas/desk-record.schema.json
src/nightbasis/desk_replay.py
tests/test_desk_replay.py
```
