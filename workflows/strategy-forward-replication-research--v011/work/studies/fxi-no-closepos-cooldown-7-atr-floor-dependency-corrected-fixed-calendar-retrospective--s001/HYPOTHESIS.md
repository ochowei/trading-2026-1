# Hypothesis: FXI No-ClosePos Cooldown-7 ATR-Floor Dependency-Corrected Fixed-Calendar Retrospective Study

## Claim

Using only the workflow-owned 2014-2018 Development interval, shortening the accepted-signal
cooldown from ten completed XNYS sessions to seven will allow the otherwise unchanged FXI
no-ClosePos ATR-floor mean-reversion candidate to satisfy the minimum of 20 completed trades
without weakening the frozen base/stress return, profit-factor, traded-year, drawdown, or
complete-family gates. If selected, that exact candidate will then pass every fixed 2020-2024
Historical Evaluation gate, all nine registered `fixed-challenge-v1` methods, and the complete
2025 retrospective execution replay.

The sole selection candidate requires all of the following after a completed XNYS session:

- adjusted close is inclusively between 5% and 12% below the inclusive rolling ten-session
  adjusted high;
- Williams %R(10) is at or below -80; and
- simple `ATR(5)/ATR(20)` is strictly above 1.05, with no ATR ceiling or ClosePos entry filter.

Entry is at the next completed XNYS session open. Exit is through the frozen +5.5% Day limit
target, -5.0% GTC stop-market, or the open after twenty completed holding sessions. Accepted
signals observe the revised seven-session cooldown. Every other signal, execution, cost, gap,
same-session ambiguity, unfilled-order, and isolated-sleeve rule remains identical to the v009/S001
candidate and comes only from the v011 policy set.

## Decision relevance

v009/S001 failed for exactly one reason: its ten-session-cooldown candidate completed 19 trades
rather than the required 20. It otherwise passed the positive base/stress return, base/stress
profit-factor, four-traded-year, stress-drawdown, and complete-family gates. In the same complete
v009/S001 family, the already-frozen seven-session-cooldown definition completed 21 trades, with
base return/profit factor `0.3107052181` / `1.7602757152` and stress return/profit factor
`0.2255199665` / `1.5332656078`. The ten-session candidate produced lower corresponding values of
`0.2731811061` / `1.7395286630` and `0.1980778451` / `1.5183958158`.

This successor study therefore changes one decision variable only relative to v009/S001: cooldown
10 to cooldown 7. The former v009/S001 candidate is retained as a non-selectable reference; the
baseline and all other robustness definitions remain frozen. The adjustment tests whether
admitting the two additional opportunities is enough to cross the trade-count gate while
preserving quality, rather than loosening the trade-count threshold or searching a new family.

v009/S001 Development and v009/S002 Development, Evaluation, and challenge outcomes are all known.
v009/S002 established 21 completed Development trades but its screen failed closed because the
preregistered qualification envelope omitted the next-open expiry session. v009/S003 corrected
only the derived execution envelope from a maximum 20-session entry-to-exit span and 21-session
signal-to-outcome dependency to 21 and 22 respectively; it reached candidate freeze but remained
paused before qualification-plan registration because v009/S002 still held the family lock.

This v011 successor changes no strategy, family, calendar, cost, gate, challenge, or outcome rule
relative to v009/S003. It restarts the exact dependency-corrected design under the active v011
shared qualification authority, after the v009/S002 plan received its separate administrative
closure. The strategy still completes exactly twenty post-entry holding sessions before a
time-expiry exit at the following open.

The study is therefore classified `known-contaminated`, with incomplete trial and prior-selection
history. A complete pass can produce only `retrospectively-supported`; it cannot establish
independent confirmation or create Shadow, activation, broker, order, position, or live authority.

## Falsification conditions

The claim is falsified with `fail` when complete, reproducible evidence establishes any of the
following:

1. The seven-session-cooldown candidate completes fewer than 20 trades, trades in fewer than three
   Development years, has non-positive base or stress compounded return, base profit factor at or
   below 1.1, stress profit factor at or below 1.0, stress drawdown worse than 20%, or lacks one
   valid observation for any member of the frozen six-member family.
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
`indeterminate`, not `fail`. `insufficient-evidence` is prohibited because every v011 interval is
already complete and fixed.
