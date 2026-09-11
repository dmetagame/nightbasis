# NightBasis Desk Record v1

Track: **AI Trading Desk**

Sub-theme: **Information Extraction & Signal Generation**

The record is an explanatory snapshot, not an order or executable alpha policy.
One record is emitted for each core rToken at 16:30, 20:00, 00:00, and 08:30 ET.
The canonical machine contract is `schemas/desk-record.schema.json`.

## Price fields

For snapshot time `t`, using the 16:15 ET session anchor:

- `y = log(rToken_price_t / rToken_price_16:15)`
- `m_hat = intercept + beta_equity*x_equity + beta_btc*x_btc + beta_eth*x_eth`
- `z = (y - m_hat) / frozen_residual_scale`

Each `x` is the matching factor log return from 16:15 to `t`. The record exposes
the intercept and each factor contribution separately; their sum must equal
`m_hat`. rQQQ is primary and rSPY is fallback on weeknights. BTC and ETH are the
only weekend/US-holiday factors. Factors are never tradable.

The coefficients and scale come unchanged from the published price-only control
(freeze `0898cca4374ae68dfbc85ae73138f710539d314800de8548d3b37f28fd0ba5a0`,
commit `c92b9bd`). Applying that same explanatory model at intermediate snapshots
does not create a new trading policy.

## Labels

- `priced`: the observed move is broadly commensurate with the extracted event.
- `incomplete`: a material, directional event is present but the price response
  appears incomplete relative to the evidence and factor context.
- `washout`: a large adverse residual lacks a qualifying material event in the
  bounded event feed.
- `stand_down`: data quality, event timing, conflicting evidence, or invalid LLM
  output prevents a defensible classification.

These semantics were specified from the product thesis and IS fixtures. OOS data
was not used to select fixture dates, labels, or prompt language.

## Deterministic kill criteria

The record must use `stand_down` when any required snapshot is absent, session
volume is zero, coverage is below 80%, the labeled Corwin-Schultz spread proxy is
above 20 bps, required factors fail, an event timestamp is later than the desk
snapshot, the record fails schema validation, or cached LLM JSON is invalid.
Historical spread remains explicitly labeled as an OHLC proxy, not observed
bid/ask.

The eventual LLM receives only event material available by `as_of_et`. It will
run with a versioned frozen prompt, temperature zero, and a content-addressed
cache. It may explain and assign one of the four labels. It may not size, route,
or place an order.

## Locked replay fixtures

All three sessions are inside IS (2026-06-02 through 2026-08-19), and every
requested focus-symbol snapshot exists in the frozen Bitget data.

| Scenario | Session date | Focus | 16:15 anchor | 16:30 | 20:00 | 00:00 | 08:30 | Move to 00:00 | Coverage | CS spread proxy |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Flat night | 2026-08-14 | rGOOGL | 346.370 | 346.339 | 346.340 | 346.400 | 347.240 | +0.0087% | 100% | 0.81 bps |
| Material news | 2026-07-23 | rGOOGL | 348.778 | 341.990 | 331.310 | 333.740 | 324.910 | -4.3116% | 100% | 3.74 bps |
| Large move, no qualifying company event | 2026-06-23 | rTSLA | 404.354 | 404.200 | 403.489 | 399.320 | 393.819 | -1.2449% | 100% | 2.42 bps |

The material-news fixture contains Alphabet's July 22 earnings 8-K, accepted at
16:01:36 ET before the first desk snapshot. Its raw event object records revenue
of $119.8B (+24% YoY), Cloud revenue of $24.8B (+82%), 34% operating margin, and
$9.11 diluted EPS, sourced from the SEC-hosted Exhibit 99.1.

“No qualifying company event” is deliberately bounded: the fixture found no
Tesla SEC filing or Tesla IR press release between 16:00 ET June 22 and 08:30 ET
June 23. It does not claim that no analyst, macro, social, or general-market news
existed.

## Raw inputs

- `fixtures/desk/flat-rgoogl-2026-08-14/raw-input.json`
- `fixtures/desk/material-news-rgoogl-2026-07-23/raw-input.json`
- `fixtures/desk/large-move-no-event-rtsla-2026-06-23/raw-input.json`
- `fixtures/desk/manifest.json`

Each fixture contains exact 15-minute OHLCV/turnover bars for the four core names
and four factors at the 16:15 anchor plus all four desk snapshots, session-quality
evidence, the unchanged frozen model, bounded event retrieval, source hashes, and
a content hash for the fixture itself.
