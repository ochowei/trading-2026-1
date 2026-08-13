# Hypothesis: FXI ATR-Band Mean-Reversion Forward Replication

## Claim

For completed XNYS sessions after the frozen 2026 quarantine, an `FXI` capitulation
mean-reversion rule whose only incremental regime mechanism is a bounded
`ATR(5)/ATR(20)` state will produce more reliable next-open reversals than a distinct simple
pullback-and-Williams-%R family baseline.

The sole selection candidate requires all of the following after a completed session: the adjusted
close is 5% through 12% below the rolling ten-session adjusted high; Williams %R(10) is at or below
-80; close position within the session range is at least 40%; and simple `ATR(5)/ATR(20)` is
strictly above 1.05 and at or below 1.35. Entry is at the next XNYS open. The candidate exits
through a +5.5% Day limit target, a -5.0% GTC stop-market, or the open after twenty completed
holding sessions, using the pinned canonical execution policy and pessimistic same-session
ordering.

Support requires the candidate to pass every frozen Development and five-fold prospective
Historical gate, exceed the simple baseline on base-net daily-equity Sharpe by at least 0.10,
retain at least 90% of the baseline's base-net compounded return, and avoid worse stress maximum
drawdown. The lower and upper sides of the ATR band must each be independently binding under the
frozen counterfactual definition; an effectively one-sided or non-binding ATR band does not
support the claim.

## Decision relevance

This study is a new workflow-native research round that explicitly revisits, but does not modify,
revive, rerun, or replace,
`strategy-forward-replication-research@v004/S003`. S003 remains terminal `fail` with its original
preregistration, evidence, conclusion, completion record, source identities, and trial history.
All FXI and ASHR results viewed through 2025-12-31, including S003, are contaminated Development
context only. They are not Historical, Shadow, or qualification evidence.

The patch is deliberately minimal and deletion-only: it removes the non-binding ASHR gate and
auxiliary dependency while retaining S003's predeclared FXI pullback, Williams-%R, ClosePos, ATR
band, exit, cooldown, and execution constants unchanged. No replacement threshold is fitted from
S003 trades, and no post-2025 outcome informs the definition. The design is therefore transparent
Development-informed follow-up, not a repair of S003 and not a claim that S003 passed.

The study asks whether the bounded FXI volatility-acceleration mechanism can stand on its own in a
new immutable family. It does not reopen an ASHR threshold search, choose between multiple ASHR
formulations, or permit CNY, VIX, EEM, trend, gap, BB-width, oscillator-hook, or another auxiliary
filter to enter the candidate. Passing Historical evidence grants only `shadow-eligible`; it never
authorizes broker access, orders, Active status, or a profit claim.

All 2026 sessions before preregistration remain quarantined and unused. The five prospective
Historical folds remain 2027 through 2031. This future-only boundary is required because 2015-2025
FXI/ASHR outcomes have influenced the design and legacy selection history is incomplete.

## Falsification conditions

The claim is falsified with `fail` if any complete and reproducible condition below occurs:

1. The sole candidate is not Development-eligible within `maximum_trials=6`, including failure to
   complete at least 30 trades across at least ten traded calendar years.
2. On Development or Historical evidence, candidate base-net compounded return is below 90% of
   baseline, candidate base-net daily-equity Sharpe is less than baseline plus 0.10, or candidate
   stress maximum drawdown is worse than baseline or exceeds 20%.
3. The candidate fails any required return, profit-factor, completed-trade, traded-fold,
   positive-fold, concentration, cash, random-entry, family-wise selection-adjustment, or
   market-regime gate.
4. In Development, the ATR floor does not uniquely suppress at least five otherwise-candidate-
   eligible entries across at least three calendar years, the ATR ceiling does not do the same, or
   the complete ATR band does not uniquely suppress at least ten core-baseline-eligible entries
   across at least five calendar years. In Historical Evaluation, either side uniquely suppresses
   fewer than two entries across fewer than two annual folds, or the complete band uniquely
   suppresses fewer than five entries across fewer than three annual folds. Complete but
   non-binding evidence is `fail`, not `insufficient-evidence`.
5. Either frozen ATR perturbation, the eighteen-session holding perturbation, one-session delayed
   entry, adverse costs/worse fills, missed entries, or another required robustness challenge
   reverses the claimed direction or violates a frozen v004 risk gate.
6. A hidden trial, partial ranking, cross-role position, data-role reassignment, stale or invalid
   source/data identity, or any 2026 quarantine, Historical, or Shadow contamination affects design
   or selection.

Missing, stale, corrupt, conflicting, non-replayable, incorrectly policy-bound, or incomplete
identity/evidence is `indeterminate`, never favorable. `insufficient-evidence` is permitted only at
an open prospective Shadow checkpoint under the pinned workflow.
