# Hypothesis: XLF Rate-Volatility-Conditioned Pullback Revised Availability Research

## Claim

For completed XNYS sessions from 2000 onward, an `XLF` pullback defined by both (a) an adjusted
close at or below its 20-session Bollinger lower band using two sample standard deviations and
(b) a ten-session adjusted-close return at or below -4% has higher-quality ten-session mean
reversion when the most recently available `^MOVE` observation has not accelerated by more than a
predeclared three-session cap.

The Development candidate family contains exactly three caps: +3, +5, and +7 MOVE index points.
The mechanism claim is supported only if one complete candidate is Development-eligible, exceeds
the distinct ungated pullback baseline by at least 0.25 base-net daily-equity Sharpe, is selected
without inspecting Historical outcomes, and the frozen candidate passes every Historical and
robustness gate. All candidates must bind the same exact XLF Development data blob, and all gated
candidates must bind the same exact MOVE Development data blob.

## Decision relevance

This replacement revisits S001 only because S001's frozen 1998-12-16 requirement preceded Yahoo's
first XLF observation on 1998-12-22. S001 produced no result, metric, trial-registry observation,
ranking, candidate freeze, or Historical outcome. S002 decides whether the same bounded
rate-volatility mechanism should advance from Development to a frozen XLF candidate eligible for
prospective Shadow observation using corrected availability and one common data generation.

A passing Historical screen grants only `shadow-eligible`; it does not authorize live trading,
broker access, orders, or Active status. Failure stops this research round and does not permit cap
expansion, gate relaxation, or reuse of the 2021-2025 Historical folds for a repaired candidate.

## Falsification conditions

The claim is falsified and the round stops with `fail` if any of the following complete and
reproducible conditions occurs:

1. No one of the three Development candidates satisfies every frozen eligibility and risk gate
   within `maximum_trials=6`.
2. The selected candidate's Development base-net daily-equity Sharpe does not exceed the ungated
   baseline by at least 0.25.
3. The frozen candidate fails any required 2021-2025 Historical gate, including completed-trade,
   fold, return, profit-factor, drawdown, concentration, selection-adjustment, baseline,
   random-entry, or robustness requirements.
4. A required adverse execution, missed-order, delayed-entry, cap-perturbation, or market-regime
   challenge falsifies a frozen gate.
5. Trial-budget exhaustion, partial candidate availability, unequal required common-series blob
   identities, or contaminated/invalid evidence prevents a complete candidate ranking.

Missing, stale, corrupt, conflicting, non-replayable, or incorrectly bound evidence is
`indeterminate`, not favorable. `insufficient-evidence` is available only during a properly
registered prospective Shadow stage under the v003 rules.
