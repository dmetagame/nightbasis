# NightBasis Desk: judge-facing replay

This human view summarizes the same frozen records as the machine transcripts.
Percentages are cumulative log returns from the 16:15 ET anchor. Every outcome
is explanatory and explicitly produces no trade.

## Flat night — rGOOGL, 2026-08-14

- Price path: 16:30 **-0.009%**; 20:00 **-0.009%**; 00:00 **+0.009%**;
  08:30 **+0.251%**.
- Evidence: no qualifying event was present in the frozen point-in-time cache.
- Read: the two negative snapshots had residual z-scores of 0.243097 and
  0.308837, both below 1.25; the later moves were nonnegative, so the Desk stood
  down. **No trade.**

## Material news — rGOOGL, session starting 2026-07-22

- Price path: 16:30 **-1.965%**; 20:00 **-5.138%**; 00:00 **-4.407%**;
  08:30 **-7.089%**.
- Evidence available before the first snapshot: Alphabet's 8-K was accepted at
  16:01 ET and reported **$119.8B revenue (+24% YoY), $24.8B Cloud revenue
  (+82%), a 34% operating margin, and $9.11 diluted EPS**. The frozen event score
  is positive with `signed_info=0.855`.
- Read: the positive event direction conflicts with the negative observed move
  at every snapshot, so the reason is `event_price_direction_conflict`. **No
  trade.** No hard kill fired.

## Large move without a qualifying company event — rTSLA, 2026-06-23

- Price path: 16:30 **-0.038%**; 20:00 **-0.214%**; 00:00 **-1.253%**;
  08:30 **-2.640%**.
- Evidence: the bounded Tesla SEC and IR event window contained no qualifying
  company event; this is not a claim that no macro, analyst, or social news
  existed.
- Read: even at 08:30, the exact residual is `z=1.235711`, below the frozen 1.25
  washout threshold, so the reason remains `uninformed_but_below_washout`.
  **No trade.**

Machine transcripts:

- `reports/replay-transcripts/flat-rgoogl-2026-08-14.txt`
- `reports/replay-transcripts/material-news-rgoogl-2026-07-23.txt`
- `reports/replay-transcripts/large-move-no-event-rtsla-2026-06-23.txt`
