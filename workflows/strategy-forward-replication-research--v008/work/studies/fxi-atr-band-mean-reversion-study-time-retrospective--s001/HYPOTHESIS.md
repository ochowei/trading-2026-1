# Hypothesis: FXI ATR-Band Mean-Reversion Study-Time Retrospective Evaluation

## Claim

Across the five complete XNYS annual folds from 2021 through 2025, a bounded-volatility FXI
mean-reversion rule will produce more reliable next-open reversals than a distinct simple
pullback-and-Williams-%R family baseline.

The sole selection candidate requires all of the following after a completed session:

- adjusted close is between 5% and 12% below the inclusive rolling ten-session adjusted high;
- Williams %R(10) is at or below -80;
- close position within the session range is at least 40%; and
- simple `ATR(5)/ATR(20)` is strictly above 1.05 and at or below 1.35.

Entry is at the next completed XNYS session open. The candidate exits through a +5.5% Day limit
target, a -5.0% GTC stop-market, or the open after twenty completed holding sessions. The pinned
canonical execution policy resolves gaps, unfilled orders, and same-session target/stop ambiguity
with pessimistic ordering. No trend-direction, volume, oscillator-confirmation, gap-down, currency,
or mutable regime filter is allowed.

Support requires all frozen shared screen gates and all nine required challenge gates to pass.
In addition, candidate base-net daily-equity Sharpe must exceed the family baseline by at least
0.10, candidate base-net compounded return must retain at least 90% of baseline, and candidate
stress maximum drawdown must be no worse than baseline. The ATR floor and ceiling must each be
independently binding: each side must suppress at least two otherwise-candidate-eligible decisions
across at least two Evaluation folds, and the complete band must suppress at least five
baseline-eligible decisions across at least three folds.

## Decision relevance

This study revisits the completed `indeterminate`
`strategy-forward-replication-research@v006/S001`. It does not repair, rerun, or reinterpret that
study, and it does not alter the paused `strategy-forward-replication-research@v004/S004` clean
Historical design.

The decision is whether this exact bounded-ATR mean-reversion family remains historically credible
enough to retain as a non-promotional research lead. A passing study may record only
`retrospectively-supported`; it cannot create `shadow-eligible`, `activation-eligible`, Active,
broker, order, or live-trading authority. A complete failure retires this research round. An
indeterminate result preserves uncertainty without manufacturing evidence. Any future promotion
attempt requires a separately preregistered successor with later unused `verified-clean` evidence.

Repository FXI summaries and cross-asset lessons are based primarily on data through 2025-12-31,
approximately eight months old at draft preparation. The staleness is disclosed rather than
silently refreshed. The 2021-2025 interval is fixed as `known-contaminated`: legacy research and
the prior lineage may have inspected or been influenced by those outcomes. This study therefore
asks only for an honest terminal retrospective conclusion, never a clean-validation claim.

## Falsification conditions

The claim is falsified with `fail` when complete, reproducible evidence establishes any of the
following:

1. Development produces no eligible candidate within the six-member frozen family and trial
   budget, or the selected candidate, distinct baseline, complete family, source inventory, or
   current-time retrospective selection checkpoint differs from preregistration.
2. Across the five Evaluation folds, the candidate completes fewer than 20 trades, trades fewer
   than three folds, has fewer than 60% positive traded folds, produces non-positive chained base
   or stress return, has base profit factor at or below 1.1, has stress profit factor at or below
   1.0, or exceeds 20% stress maximum drawdown.
3. Any fold contributes more than 50% of completed trades or positive profit; candidate base return
   does not exceed cash or the 90th percentile exposure-matched random return; or complete-family
   block-bootstrap selection confidence is below 90%.
4. Candidate base return is below 90% of baseline, candidate base daily-equity Sharpe is less than
   baseline plus 0.10, or candidate stress drawdown is worse than baseline.
5. Either ATR-bound perturbation is non-binding, the eighteen-session holding or delayed-entry
   perturbation reverses the claim, or higher costs, worse fills, deterministic missed entries, or
   annual market-regime evidence fails its frozen challenge gate.
6. A session changes role, an Evaluation outcome is used to tune or rerank the family, a hidden or
   seventh trial is introduced, partial ranking is produced, or a retrospective result is
   represented as promotion or live authority.

Missing, stale, corrupt, conflicting, incorrectly policy-bound, role-leaking, or non-replayable
evidence is `indeterminate`, not favorable. `insufficient-evidence` is unavailable for this fixed
completed-data checkpoint; insufficient trades or folds are complete gate failures.
