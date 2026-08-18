# Hypothesis: FXI Volume-Stratified ATR-Floor Mean-Reversion Study-Time Retrospective Evaluation

## Claim

Across complete 2015-2019 Development evidence, removing the upper bound from the S001 ATR band
while retaining its lower volatility-acceleration bound will produce an eligible FXI candidate with
at least twenty completed trades. Across the five complete XNYS annual Evaluation folds from 2021
through 2025, that frozen candidate will then pass every v008 shared screen gate and all nine
required challenges without relying on a small number of unusually high-volume events.

The sole selection candidate requires all of the following after a completed session:

- adjusted close is inclusively between 5% and 12% below the inclusive rolling ten-session
  adjusted high;
- Williams %R(10) is at or below -80;
- close position within the completed session range is at least 40%; and
- simple `ATR(5)/ATR(20)` is strictly above 1.05, with no ATR ceiling.

Entry is at the next completed XNYS session open. The candidate exits through a +5.5% Day limit
target, a -5.0% GTC stop-market, or the open after twenty completed holding sessions, and accepted
signals observe a ten-session cooldown. All order timing, fill, gap, same-session ambiguity,
unfilled-order, cost, and isolated-sleeve behavior comes from the exact v008 policy set; this study
does not restate or override it.

Volume is not an entry filter. It cannot accept or reject a signal, alter cooldown or position
conflicts, affect Development eligibility or candidate ranking, or create a replacement candidate.
It is used only after the candidate is frozen as a preregistered `market-regimes` stability and
concentration challenge. Each completed candidate trade is assigned the volume percentile of its
signal session against the preceding 252 completed sessions, excluding the signal session, and is
classified into low, normal, or high volume. Support requires complete provider-free feature
coverage, meaningful representation in at least two terciles, no single tercile dominating trades
or positive profit, and positive chained base and stress returns after the already-accepted
high-volume trades are replaced by cash intervals without rerunning signal acceptance.

## Decision relevance

This study revisits the completed
`strategy-forward-replication-research@v008/S001`, whose exact path is
`workflows/strategy-forward-replication-research--v008/work/studies/fxi-atr-band-mean-reversion-study-time-retrospective--s001`.
S001 ended `fail / development-selection-failed / development` because its sole candidate completed
14 Development trades, below the frozen minimum of 20. Its other Development eligibility gates
passed; this successor therefore tests a preregistered sample-coverage change, not a post hoc claim
that S001 return or profit factor was negative. S001 remains immutable.

The cross-asset prohibition on volume as a primary entry filter is binding. This study asks whether
the ATR-floor rule is stable across volume environments, not whether volume can improve signal
selection. A passing study may record only `retrospectively-supported`; it cannot create Shadow,
`shadow-eligible`, activation, Active, broker, order, or live-trading authority. Any promotion
attempt requires a separately preregistered successor with later unused `verified-clean` evidence.

The 2021-2025 interval is fixed as `known-contaminated`, and both trial history and prior-selection
history are disclosed as incomplete. Repository FXI context lacks freshness metadata, while most
cross-asset rules were last validated through 2025-12-31 and are more than six months old at draft
preparation. These limitations are frozen disclosures, not grounds to relabel evidence or refresh
outcomes during planning.

## Falsification conditions

The claim is falsified with `fail` when complete, reproducible evidence establishes any of the
following:

1. Development produces no eligible candidate within the six-member family, including if the sole
   selectable ATR-floor candidate completes fewer than 20 trades across fewer than three
   Development years, fails the frozen return/profit-factor/drawdown gates, or any required family
   observation is invalid. No other member may replace it.
2. Across Evaluation, the candidate completes fewer than 20 trades, trades fewer than three folds,
   has fewer than 60% positive traded folds, produces non-positive chained base or stress return,
   has base profit factor at or below 1.1, has stress profit factor at or below 1.0, or exceeds 20%
   stress maximum drawdown.
3. Any annual fold contributes more than 50% of completed trades or base-net positive profit;
   candidate base return does not exceed cash or the 90th percentile exposure-matched random
   return; candidate base daily-equity Sharpe is less than baseline plus 0.10; or complete-family
   block-bootstrap selection confidence is below 90%.
4. The volume feature is not reproducible from the one frozen OHLCV generation for every completed
   candidate trade; fewer than two terciles each contain at least five completed trades across at
   least two Evaluation folds; any tercile contributes more than 50% of completed trades or
   base-net positive profit; or replacing high-tercile accepted trades with cash intervals makes
   chained base or stress compounded return non-positive.
5. The ATR-floor 1.10 or hold-18 perturbation, delayed entry, higher costs, canonical adverse fills,
   deterministic missed entries, or annual/volume market-regime evidence fails its frozen typed
   gate. The exact S001 ATR-band member is a non-selectable robustness reference and cannot become
   the candidate.
6. Volume affects signal acceptance, ranking, entry, cooldown, or family selection; a session
   changes role; Evaluation outcome is used to tune or rerank; a hidden or seventh trial is
   introduced; partial ranking is produced; or retrospective evidence is represented as promotion
   or live authority.

Missing, stale, corrupt, conflicting, incorrectly policy-bound, cross-generation, role-leaking, or
non-replayable evidence is `indeterminate`, not favorable. `insufficient-evidence` is unavailable
for this fixed completed-data checkpoint; too few trades, folds, or covered volume strata are
complete frozen gate failures.
