# Hypothesis: FXI No-ClosePos ATR-Floor Mean-Reversion Fixed-Calendar Retrospective Study

## Claim

Using only the workflow-owned 2014-2018 Development interval, the frozen six-member FXI
no-ClosePos ATR-floor mean-reversion family will produce one eligible selected candidate. The
selected candidate will then pass every fixed 2020-2024 Historical Evaluation gate, all nine
registered `fixed-challenge-v1` methods, and the complete 2025 retrospective execution replay.

The sole selection candidate requires all of the following after a completed XNYS session:

- adjusted close is inclusively between 5% and 12% below the inclusive rolling ten-session
  adjusted high;
- Williams %R(10) is at or below -80; and
- simple `ATR(5)/ATR(20)` is strictly above 1.05, with no ATR ceiling or ClosePos entry filter.

Entry is at the next completed XNYS session open. Exit is through the frozen +5.5% Day limit
target, -5.0% GTC stop-market, or the open after twenty completed holding sessions. Accepted
signals observe a ten-session cooldown. Exact order timing, fill, gap, same-session ambiguity,
unfilled-order, cost, and isolated-sleeve behavior comes only from the v009 policy set.

## Decision relevance

This study is the v009 successor to the paused
`strategy-forward-replication-research@v008/S003` study at
`workflows/strategy-forward-replication-research--v008/work/studies/fxi-no-closepos-atr-floor-mean-reversion-study-time-retrospective--s003`.
It does not resume, migrate, or reinterpret S003. S003 showed that the candidate was eligible on
2015-2019 Development data, but that result does not establish eligibility on v009's different
fixed 2014-2018 Development interval.

The new study addresses the v006-v008 governance failures directly: it uses the v009 exact
selection boundary, workflow-owned calendar, complete family, tracked evidence namespaces, fully
registered executable challenge contracts, independent challenge-only publication, and fixed
2025 replay. Previous FXI outcomes remain disclosed research context rather than fresh evidence.

The 2020-2024 Evaluation and 2025 replay are classified `known-contaminated` because prior FXI and
legacy research may have inspected or been influenced by those completed periods. Trial history
and prior selection history remain incomplete. Even a complete pass can produce only
`retrospectively-supported`; it cannot create Shadow, activation, broker, order, or live authority.

## Falsification conditions

The claim is falsified with `fail` when complete, reproducible evidence establishes any of the
following:

1. The six-member 2014-2018 Development family produces no eligible sole candidate. Eligibility
   requires at least 20 completed trades across at least three Development years, positive base
   and stress compounded return, base profit factor above 1.1, stress profit factor above 1.0,
   stress maximum drawdown no worse than 20%, and one valid observation for every family member.
2. Fixed 2020-2024 Evaluation produces fewer than 20 completed trades, fewer than three traded
   folds, fewer than 60% positive traded folds, non-positive base or stress return, base profit
   factor at or below 1.1, stress profit factor at or below 1.0, stress drawdown worse than 20%,
   excessive fold concentration, or complete-family selection confidence below 90%.
3. Any of the nine frozen challenge artifacts evaluates its typed `passed = true` gate as false.
   The family baseline, random-entry benchmark, parameter variants, delayed entry, higher costs,
   worse fills, missed entries, and calendar-quarter regimes may only challenge the selected
   candidate; none may replace it.
4. The fixed 2025 replay omits any expected session, completes fewer than 12 simulated fills, has
   non-positive base or stress return, has base or stress profit factor at or below 1.0, breaches
   the 20% stress drawdown limit, or fails the historical critical-drift replay.

Missing, conflicting, stale, incorrectly bound, or non-replayable identity, approval, calendar,
policy, registry, observation, challenge, or replay evidence produces stage-identified
`indeterminate`, not `fail`. `insufficient-evidence` is prohibited because every v009 interval is
already complete and fixed.
