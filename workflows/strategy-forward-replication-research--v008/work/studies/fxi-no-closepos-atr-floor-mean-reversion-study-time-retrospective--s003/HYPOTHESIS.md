# Hypothesis: FXI No-ClosePos ATR-Floor Mean-Reversion Study-Time Retrospective Evaluation

## Claim

Across complete 2015-2019 Development evidence, retaining the FXI pullback, Williams %R, and
open-ended ATR-floor mechanism while removing the secondary `ClosePos >= 0.40` confirmation will
produce an eligible sole selection candidate with at least twenty completed trades. If and only if
that candidate is Development-eligible, it will then pass every v008 shared screen gate and all
nine required challenges across the five complete 2021-2025 XNYS annual Evaluation folds without
relying on a small number of unusually high-volume events.

The sole selection candidate requires all of the following after a completed session:

- adjusted close is inclusively between 5% and 12% below the inclusive rolling ten-session
  adjusted high;
- Williams %R(10) is at or below -80; and
- simple `ATR(5)/ATR(20)` is strictly above 1.05, with no ATR ceiling.

The candidate has no ClosePos entry condition. Entry is at the next completed XNYS session open.
It exits through a +5.5% Day limit target, a -5.0% GTC stop-market, or the open after twenty
completed holding sessions, and accepted signals observe a ten-session cooldown. All order timing,
fill, gap, same-session ambiguity, unfilled-order, cost, and isolated-sleeve behavior comes from the
exact v008 policy set; this study does not restate or override it.

Volume is not an entry filter. It cannot accept or reject a signal, alter cooldown or
existing-position conflicts, affect Development eligibility or candidate ranking, or create a
replacement candidate. It is used only after candidate freeze as a preregistered `market-regimes`
stability and concentration challenge. Each completed candidate trade is assigned the volume
percentile of its signal session against the preceding 252 completed sessions, excluding the
signal session, using the fixed mid-rank formula `(L + 0.5 * E) / 252`. Support requires complete
provider-free feature coverage, meaningful representation in at least two terciles, no single
tercile dominating trades or positive profit, and positive chained base and stress returns after
the already-accepted high-volume trade intervals are replaced by cash without admitting
replacement signals.

## Decision relevance

This study is the CLI-allocated successor to completed
`strategy-forward-replication-research@v008/S002`, whose exact path is
`workflows/strategy-forward-replication-research--v008/work/studies/fxi-volume-stratified-atr-floor-mean-reversion-study-time-retrospective--s002`.
S002 ended `fail / development-selection-failed / development` because its sole selectable
ClosePos-gated ATR-floor candidate completed 15 Development trades, below the frozen minimum of
20. The candidate otherwise traded all five Development years and passed the frozen base/stress
return, profit-factor, stress-drawdown, and complete-family validity gates. The S001 ATR-band
reference completed 14 trades; ATR floor 1.10 and hold 18 both remained at 15 trades; and the
distinct pullback/Williams-%R baseline completed 33 trades while exceeding the successor's 20%
stress-drawdown limit. S001 and S002 remain immutable.

This successor therefore tests one preregistered mechanism-level change: whether removing the
secondary ClosePos confirmation, while retaining the ATR floor, resolves the binding sample-size
failure. It does not repeat ATR-ceiling removal, ATR 1.00/1.05 tuning, or holding 18/20 tuning as
the research question. A provider-free Development signal funnel will localize attrition without
changing the candidate, ranking, or gates. The exact S002 candidate remains a non-selectable
reference, and no robustness member may replace the failed sole candidate.

The 2021-2025 interval remains `known-contaminated`, with `trial_history_complete=false` and
`prior_selection_history_incomplete=true`. S001/S002 evidence is Development context and research
motivation, not clean validation. A passing study may record only `retrospectively-supported`; it
cannot create Shadow, `shadow-eligible`, activation, Active, broker, order, or live-trading
authority. Any promotion attempt requires a separately preregistered successor with later unused
`verified-clean` evidence.

The 2026-08-18 freshness check reports that most cross-asset rules and the FXI context are based on
data through 2025-12-31, about eight months old. These are frozen stale-context disclosures, not
grounds to refresh or inspect outcomes during planning.

## Falsification conditions

The claim is falsified with `fail` when complete, reproducible evidence establishes any of the
following:

1. Development produces no eligible candidate within the six-member family, including if the sole
   selectable no-ClosePos candidate completes fewer than 20 trades across fewer than three
   Development years, fails the frozen return/profit-factor/drawdown gates, or any required family
   observation is invalid. The baseline, exact S002 reference, cooldown perturbation, ATR
   perturbation, and delayed-entry member cannot replace it.
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
   base-net positive profit; or replacing high-tercile accepted-trade intervals with cash makes
   chained base or stress compounded return non-positive.
5. The no-ClosePos ATR-floor 1.10 or cooldown-7 perturbation, delayed entry, higher costs,
   canonical adverse fills, deterministic missed entries, or annual/volume market-regime evidence
   fails its frozen typed gate. The exact S002 ClosePos-gated member is identity-binding and
   diagnostic only.
6. The Development funnel cannot be replayed from frozen indicator, raw-signal, raw-candidate, and
   canonical-sleeve evidence; uses an unregistered threshold; changes ranking or eligibility; or
   omits cooldown suppression, position conflict, executable entry, or completed-trade stages.
7. Volume affects signal acceptance, ranking, entry, cooldown, or family selection; a session
   changes role; Evaluation outcome is used to tune or rerank; a hidden or seventh trial is
   introduced; partial ranking is produced; or retrospective evidence is represented as promotion
   or live authority.

Missing, stale, corrupt, conflicting, incorrectly policy-bound, cross-generation, role-leaking, or
non-replayable evidence is `indeterminate`, not favorable. `insufficient-evidence` is unavailable
for this fixed completed-data checkpoint; too few trades, folds, or covered volume strata are
complete frozen gate failures.
