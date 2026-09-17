# Desk walkthrough — replacement take

Source: https://nightbasis.vercel.app/desk

Recorded from fresh Playwright Chromium visits on 2026-09-17. Autoplay was paused before any clock was selected; every captured state was reached with an actual fixture/clock click. No values, labels, reasons, fixtures, or source files were changed.

Capture uses lossless 1280×720 PNG frames assembled into a silent, 30 fps H.264/yuv420p MP4 with fast-start metadata. The holds below are the final video's timeline, not wall-clock browser capture time. This is an edited walkthrough with clean cuts between clicked states.

For readability, temporary browser-only CSS widens the evidence column and reduces panel spacing at 100% scale. All evidence remains present. A three-second opening question overlays only the header. Neither adjustment is deployed or written into the site's source.

| Video interval | Fixture / selected clock | Hold | Observed move on screen | Evidence and verdict |
| --- | --- | --- | --- | --- |
| 00:00–00:03 | Material filing · 16:30 | 3s | −1.965% | Opening question; replay paused; No trade |
| 00:03–00:10 | Material filing · 16:30 | 7s | −1.965% | Question removed; stationary opening view |
| 00:10–00:33 | Material filing · 16:30 | 23s | −1.965% | Signed info 0.855; direction +1; 8-K accepted 16:01 ET; event_price_direction_conflict; No trade |
| 00:33–00:40 | Material filing · 20:00 | 7s | −5.138% | Same signed info, direction, conflict reason, and No trade |
| 00:40–00:47 | Material filing · 00:00 | 7s | −4.407% | Same signed info, direction, conflict reason, and No trade |
| 00:47–00:55 | Material filing · 08:30 | 8s | −7.089% | Same signed info, direction, conflict reason, and No trade |
| 00:55–01:00 | Uninformed move · 16:30 | 5s | −0.038% | Tesla; z 0.376121; uninformed_but_below_washout; No trade |
| 01:00–01:05 | Uninformed move · 20:00 | 5s | −0.214% | z 0.348336; same reason and No trade |
| 01:05–01:10 | Uninformed move · 00:00 | 5s | −1.253% | z −1.040159; same reason and No trade |
| 01:10–01:46 | Uninformed move · 08:30 | 36s | −2.640% | Full z 1.235711; below 1.25; uninformed_but_below_washout; No trade |
| 01:46–01:50 | Uninformed move · 08:30 | 4s | −2.640% | Identical frozen closing frame; hard cut |

The opening view and the main 16:30 hold use the same fresh clicked state; there is no fabricated click animation at 00:10. The final Tesla state remains uninterrupted for 40 seconds. “1.236” is the spoken three-decimal reading of the full on-screen value, never a replacement value or a qualifying washout.

## Voiceover cues

Read the eight paragraphs of `VOICEOVER.txt` starting at 00:00, 00:10, 00:33, 00:40, 00:47, 00:55, 01:10, and 01:35 respectively. Leave the final four seconds silent.

## Verification

- ffprobe: 110.000 seconds; 1,142,650 bytes; 1280×720; H.264; yuv420p; 30/1 fps; silent.
- Full MP4 decode passed. Encoded frames at 00:15 and 01:20 were visually reviewed at native size: both critical evidence sets are readable together.
- `make demo-replay` passed; no changes to Python, fixtures, control reports, or `web/src/data/research.ts`.
- Narration: 159 words. No fourth fixture. No stock music, cursor effects, or terminal footage.
