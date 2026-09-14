# Bitget Playbook mirror

> **Negative control. Not the shipped product.**

This recipe mirrors only the frozen price-only control. It excludes news,
event scores, Desk labels, and execution. Python artifacts in this repository
remain authoritative for the published control and all information features.

Freeze:
`0898cca4374ae68dfbc85ae73138f710539d314800de8548d3b37f28fd0ba5a0`
(commit `c92b9bd`). Do not optimize or retune the generated strategy.

## Natural-language strategy

Paste this into a new logged-in Bitget Playbook strategy:

```text
Create a price-only backtest for rNVDA, rTSLA, rAAPL, and rGOOGL. These are the only tradable instruments. Use rQQQ as the primary equity factor, rSPY only as its fallback, and BTC plus ETH as supplementary factors; never trade any factor.

For each US weeknight, measure every return from the 16:15 ET anchor to 00:00 ET. Estimate each rToken's fair return from the frozen relationship to the usable equity factor, BTC, and ETH. Define residual z as (fair return minus observed rToken return) divided by the frozen residual scale.

At 00:00 ET, enter long only when fair return is positive and residual z is at least 1.0. Allocate 4% of NAV per qualifying name. Stay flat otherwise. Exit every position at 09:00 ET.

For weekends and US holidays, use BTC and ETH only. Require residual z of at least 1.5, positive fair return, and observed rToken return greater than or equal to zero. Never enter a weekend washout after a negative observed move.

Charge 25 basis points per side: 25 bps at entry and 25 bps at exit. Keep unusable and no-entry calendar days as flat zero-return days. Do not short, rebalance, optimize parameters, add names, use news, or place live orders.
```

## Click sequence

Playbook labels may vary slightly by release; preserve the values below rather
than substituting a nearby instrument or rule.

1. Open Bitget Playbook while logged in and select **Create strategy** or the
   equivalent new-strategy action.
2. Choose the natural-language strategy workflow.
3. Paste the complete strategy block above and generate the draft.
4. Review the parsed universe. It must show only rNVDA, rTSLA, rAAPL, and
   rGOOGL as tradable. rQQQ, rSPY, BTC, and ETH must remain factors only.
5. Review the schedule: decision and entry at 00:00 ET, exit at 09:00 ET,
   long/flat only.
6. Review the conditions: weeknight z at least 1.0; weekend/holiday z at least
   1.5; positive fair value; no weekend entry after a negative observed move.
7. Set transaction cost to 25 bps per side. Disable slippage optimization,
   parameter search, auto-tuning, and live deployment if those options appear.
8. Set the comparison window to 2026-06-02 through 2026-09-11, the last
   observed date in the frozen provisional report. Keep 2026-08-19 as the IS
   boundary; do not use later nights to fit rules.
9. Run the backtest and capture the requested screens. Differences from the
   Python metrics must be described as Playbook data/model differences, never
   repaired by changing the frozen rules.
10. Do not select **Deploy**, **Trade**, or any live/paper order action. If
    Playbook cannot express a locked condition or rToken, capture that limitation
    and stop rather than substituting a different rule or name.

## Screenshot checklist

- [ ] Strategy overview showing the four-name tradable universe.
- [ ] Factor/rule view showing rQQQ primary, rSPY fallback, BTC, and ETH as
      non-tradable inputs.
- [ ] Entry/exit view showing 00:00 ET entry, 09:00 ET exit, and long/flat only.
- [ ] Threshold view showing weeknight 1.0, weekend/holiday 1.5, and the weekend
      nonnegative-observed-return gate.
- [ ] Cost view showing 25 bps per side.
- [ ] Equity curve for the fixed comparison window.
- [ ] Metrics panel, including negative results if reproduced.
- [ ] Final screenshot or slide carrying this exact caption:

> **Negative control. Not the shipped product.**

Store the screenshots in `reports/playbook/`. Do not add credentials, account
identifiers, balances, or unrelated portfolio information to the captures.
