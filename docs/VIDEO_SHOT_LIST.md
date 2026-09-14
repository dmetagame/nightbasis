# 120-second demo video shot list

Target length: exactly 2:00. Record at 1080p or higher with a large terminal
font. Hide notifications, account identifiers, balances, and browser profiles.

| Time | Picture | Voiceover / on-screen point |
| --- | --- | --- |
| 0:00–0:12 | Title card: **NightBasis Desk** and **AI Trading Desk → Information Extraction & Signal Generation** | “rTokens trade after the US cash close, when a real company event and a thin-market move can look alike. NightBasis Desk explains the difference—and knows when to say no trade.” |
| 0:12–0:25 | README: one-liner, four-name book, three-fixture table | “The book is fixed to rNVDA, rTSLA, rAAPL, and rGOOGL. Factors explain price; they are never traded. The demo uses exactly three real-date fixtures.” |
| 0:25–0:34 | Terminal at repository root; run `make demo-replay` | “One offline command replays twelve point-in-time snapshots in about five hundredths of a second. There is no network call and no order path.” |
| 0:34–0:54 | Scroll to the material-news rGOOGL transcript; highlight session start, event ID, and signed information | “For the session starting July 22 at 16:15 Eastern, Alphabet's 8-K was already available at 16:01. It reported $119.8 billion revenue, $24.8 billion Cloud revenue, a 34 percent operating margin, and $9.11 diluted EPS. The frozen event direction is positive and signed information is 0.855.” |
| 0:54–1:09 | Pause on the rGOOGL 16:30 row; enlarge `y=-0.01965412`, `reason=event_price_direction_conflict`, and `kill_fired=false` | “But rGOOGL was already down 1.97 percent at 16:30, then 5.14 percent at 20:00 and 7.09 percent by 08:30. The evidence and tape conflict. The Desk does not flip the event direction: stand down, no trade.” |
| 1:09–1:25 | Show the rTSLA 08:30 transcript row; highlight `y=-0.02639932`, `z=1.235711`, and the reason | “Tesla fell 2.64 percent with no qualifying SEC or IR event in the bounded feed. Its exact residual z is 1.235711—not 1.25—so it stays below the washout threshold: stand down, no trade.” |
| 1:25–1:45 | Open `reports/price-only-metrics.md`; highlight IS and provisional OOS rows plus weekend count | “The frozen price-only control lost money. IS Sharpe was minus 1.58 at 15 basis points per side and minus 2.96 at 25. Provisional OOS Sharpe was minus 5.57 at 15. Twenty-six weekend nights produced zero entries. We published the failure and did not retune.” |
| 1:45–1:54 | Show the Playbook mirror caption: **Negative control. Not the shipped product.** | “The Bitget Playbook version is a price-only mirror for validation. It is explicitly a negative control, not the shipped product.” |
| 1:54–2:00 | End card: **Evidence first. No forced alpha. No trade means no trade.** and `[REPO_URL]` | “NightBasis Desk: evidence first, no forced alpha. Code, fixtures, transcripts, and tests are public at this repository.” |

## Recording checks

- [ ] Replace `[REPO_URL]` on the end card with the public repository URL.
- [ ] Keep the terminal output on the material-news fixture long enough to read
      the 16:30 conflict.
- [ ] Show Tesla's full `1.235711`; do not visually round it to 1.25.
- [ ] Keep the loss-making metric rows visible while saying “did not retune.”
- [ ] Do not show Playbook deployment, live orders, credentials, account IDs, or
      balances.
- [ ] Export at or under 120 seconds.
