# Submission draft bullets

## Thesis

- Overnight rToken moves can mix company information, broad-market repricing,
  and thin-market noise. NightBasis Desk separates those explanations by
  comparing the observed move with a frozen factor-model fair value and
  point-in-time company evidence.
- The product is deliberately a research desk, not an autonomous trading
  strategy: it produces an auditable label, reason, factor attribution, source
  record, and memo at four overnight snapshots.

## Target user and product value

- Target user: a crypto-native trader or risk operator monitoring tokenized US
  equities outside US cash-market hours.
- Value: replace an unexplained overnight percentage move with a reproducible
  answer to three questions—what moved, what public evidence existed at that
  time, and why the Desk stood down.

## Validation

- The frozen core universe is rNVDA, rTSLA, rAAPL, and rGOOGL; rQQQ/rSPY and
  BTC/ETH are explanatory factors only and are never traded.
- The price-only control was frozen before the OOS read under hash
  `0898cca4374ae68dfbc85ae73138f710539d314800de8548d3b37f28fd0ba5a0`.
  It lost money in both IS and provisional OOS even after assuming only 15 bps
  per side: -0.0702% IS with Sharpe -1.58, and -0.1595% provisional OOS with
  Sharpe -5.57 through 2026-09-11. It was not retuned.
- That failed control is published as negative evidence: price residuals alone
  were not strong enough to justify an executable alpha claim, which is why the
  product was narrowed to information extraction and signal explanation.
- Three locked real-date fixtures test distinct desk states: a flat rGOOGL
  night, Alphabet's material 8-K session, and a large rTSLA decline with no
  qualifying Tesla SEC/IR event in the bounded window. All 12 snapshot records
  validate against the Desk schema and replay offline in under five minutes.

## Role of the LLM

- The frozen LLM contract reads only company evidence timestamped at or before
  each snapshot and returns temperature-zero JSON: qualifying event, direction,
  materiality, confidence, novelty gate, signed information, and explanation.
  The offline fixtures use disclosed `human-v1` cached JSON under that same
  schema; they do not pretend a live model call occurred.
- `signed_info = direction × materiality × confidence`; novelty is a gate, not
  a multiplier. The LLM does not see future snapshots, select securities, set
  thresholds, size positions, or place trades.
- Deterministic Python code owns price calculations, quality and timing checks,
  labels, reasons, and the final no-trade memo.

## Take on AI trading

- AI is most credible here as a structured evidence layer, not an unaccountable
  stock picker. Every statement must trace to a timestamped source, every model
  output must be cached and reproducible, and deterministic rules must be able
  to reject the AI's interpretation.
- A useful AI trading system should publish negative controls and stand down
  when evidence and price disagree. NightBasis Desk demonstrates that discipline
  explicitly: all three fixtures end with **no trade**.
