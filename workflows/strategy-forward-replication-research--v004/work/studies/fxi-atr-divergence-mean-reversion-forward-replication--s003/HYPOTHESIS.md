# Hypothesis: FXI ATR-Divergence Mean-Reversion Forward Replication

## Claim

For completed XNYS sessions after the frozen 2026 quarantine, an `FXI` capitulation
mean-reversion rule that combines a bounded volatility-acceleration state with an `FXI`-versus-
`ASHR` divergence floor will produce more reliable next-open reversals than a distinct simple
pullback-and-Williams-%R family baseline.

The sole selection candidate requires all of the following after a completed session: the adjusted
close is 5% through 12% below the rolling ten-session adjusted high; Williams %R(10) is at or below
-80; close position within the session range is at least 40%; ATR(5)/ATR(20) is strictly above
1.05 and at or below 1.35; and the twenty-session `FXI` return minus the twenty-session `ASHR`
return is at least -8%. Entry is at the next XNYS open. The candidate exits through a +5.5% Day
limit target, a -5.0% GTC stop-market, or the open after twenty completed holding sessions, using
the pinned canonical execution policy and pessimistic same-session ordering.

Support requires the candidate to pass every frozen Development and five-fold prospective
Historical gate, exceed the simple baseline on base-net daily-equity Sharpe by at least 0.10,
retain at least 90% of the baseline's base-net compounded return, and avoid worse stress maximum
drawdown. The ATR ceiling and ASHR gate must each be binding often enough for direct assessment;
a non-binding compound filter does not support the claim.

## Decision relevance

This study converts legacy FXI research context into a new workflow-native identity without
modifying or qualifying any package under `src/trading/experiments/`. Legacy results through
2025-12-31 informed the fixed candidate and are Development context only. They are not Historical,
Shadow, or qualification evidence.

The study asks whether the predeclared compound structure survives a genuinely forward evaluation.
It does not ask which legacy FXI experiment was best, does not reopen a parameter search, and does
not permit WR(14), RSI, trend, gap, BB-width, CNY, VIX, or another auxiliary filter to replace the
candidate. Passing Historical evidence grants only `shadow-eligible`; it never authorizes broker
access, orders, Active status, or a profit claim.

The design is intentionally long-horizon. All 2026 sessions before preregistration are quarantined,
and the five prospective Historical folds are 2027 through 2031. This future-only boundary is
required because legacy FXI selection history is incomplete and 2019-2025 outcomes have already
influenced the design.

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
4. Across Historical folds, fewer than five accepted entries are uniquely excluded by the ATR
   ceiling or fewer than five are uniquely excluded by the ASHR gate, or either filter is binding
   in fewer than three annual folds. Complete but non-binding evidence is `fail`, not
   `insufficient-evidence`.
5. Either frozen ASHR-floor perturbation, the ATR-ceiling perturbation, the eighteen-session holding
   perturbation, adverse costs/worse fills, missed entries, or another required robustness
   challenge reverses the claimed direction or violates a frozen v004 risk gate.
6. An unavailable or stale `ASHR` decision produces a signal, candidate, or trade; primary and
   auxiliary session alignment differs; a trial is hidden; a partial ranking is produced; or any
   Development, Historical, or Shadow outcome contaminates design or selection.

Missing, stale, corrupt, conflicting, non-replayable, incorrectly policy-bound, or incomplete
identity/evidence is `indeterminate`, never favorable. `insufficient-evidence` is permitted only at
an open prospective Shadow checkpoint under the pinned workflow.
