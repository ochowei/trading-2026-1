# Hypothesis: XLF Close-Armed Profit-Protection Pullback Research

## Claim

For completed XNYS sessions from 2004 onward, the ungated `XLF` pullback entry used by the
predecessor S001 can achieve better downside protection without materially sacrificing return when
its fixed ten-session exit is augmented by one predeclared close-armed profit-protection state.

The entry remains exactly: adjusted close at or below the 20-session Bollinger lower band using two
sample standard deviations and ten-session adjusted-close return at or below -4%, followed by
market entry at the next XNYS open. The only selection candidate arms after a completed post-entry
close reaches +2.0% relative to the observed entry open. After arming, the first strictly later
completed close at or below +0.5% relative to that entry causes market exit at the next XNYS open.
Absent that event, the position exits at the same fixed ten-session expiry as the baseline.

Support requires the candidate, relative to the distinct fixed-ten-session baseline, to retain at
least 90% of base-net compounded return, improve base-net daily-equity Sharpe by at least 0.10, and
reduce stress maximum drawdown by at least 15% on both Development and the untouched 2021-2025
Historical Evaluation, while passing every other frozen v004 gate. The protection mechanism must
also engage often enough for a direct paired assessment; a non-binding mechanism does not support
the claim.

## Decision relevance

This study directly revisits
`workflows/strategy-forward-replication-research--v004/work/studies/xlf-rate-volatility-conditioned-pullback-gap-safe--s001`.
It preserves S001's ungated XLF entry, next-open execution, ten-session maximum holding period,
canonical sleeve, and exact v004 policy set, but asks a new exit-only question. It does not reuse,
remove, or tune a MOVE cap; it declares no auxiliary series. It does not select h4, h6, h8, any
postmortem horizon, any best cohort, or any trade-level exception.

The single +2.0%/+0.5% candidate is fixed ex ante. The +2.0% arming level is one-half of the frozen
-4% pullback magnitude, and the +0.5% floor is a simple cost-covering buffer above the 44 bps
strictly adverse round-trip friction. The floor is fixed to entry and never trails a running high.
The symmetric +1.5% and +2.5% arming definitions and one-session delayed protection exit are
robustness-only challenges; they can falsify the candidate but cannot win or replace it.

A passing Historical screen grants only `shadow-eligible`. It does not authorize broker access,
orders, live trading, automatic submission, Active status, or a profit claim.

## Falsification conditions

The claim is falsified with `fail` if any complete and reproducible condition below occurs:

1. The sole candidate is not Development-eligible within `maximum_trials=5`, including failure to
   complete at least 30 trades across at least ten traded calendar years or to produce at least ten
   protection exits across at least five calendar years.
2. On Development or Historical evidence, candidate base-net compounded return is below 90% of
   baseline, candidate base-net daily-equity Sharpe is less than baseline plus 0.10, or candidate
   stress maximum drawdown exceeds 85% of baseline stress maximum drawdown.
3. On trades where protection fires, the aggregate paired base-net advantage versus holding the
   identical entry to baseline expiry is non-positive in Development, or is not positive in at
   least 60% of Historical folds containing a protection exit.
4. The candidate fails any required return, profit-factor, drawdown, completed-trade, traded-fold,
   positive-fold, concentration, cash, random-entry, family-wise selection-adjustment, or
   market-regime gate.
5. Fewer than five Historical protection exits occur across at least three annual folds. Complete
   but non-binding Historical evidence is `fail`, not `insufficient-evidence`.
6. Either arming perturbation, delayed protection exit, adverse-cost/worse-fill, missed-entry, or
   other required robustness challenge reverses the claimed direction or violates a frozen v004
   risk gate.
7. Candidate and baseline accepted-entry cohorts differ, the ten-session occupation lock leaks,
   an intrabar or same-session optimistic fill is inferred, a trial is hidden, a partial ranking is
   produced, or any Development, Historical, or Shadow outcome contaminates design or selection.

Missing, stale, corrupt, conflicting, non-replayable, incorrectly policy-bound, or incomplete
identity/evidence is `indeterminate`, never favorable. `insufficient-evidence` is permitted only at
an open prospective Shadow checkpoint under the pinned workflow.
