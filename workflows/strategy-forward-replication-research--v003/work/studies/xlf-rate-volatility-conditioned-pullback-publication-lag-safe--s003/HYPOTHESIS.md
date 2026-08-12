# Hypothesis: XLF Rate-Volatility-Conditioned Pullback Publication-Lag-Safe Research

## Claim

For completed XNYS sessions from 2004 onward, an `XLF` pullback defined by both (a) an adjusted
close at or below its 20-session Bollinger lower band using two sample standard deviations and
(b) a ten-session adjusted-close return at or below -4% has higher-quality ten-session mean
reversion when the most recently available `^MOVE` observation has not accelerated by more than a
predeclared three-session cap.

The Development family contains exactly the +3, +5, and +7 MOVE caps. Support requires one complete
candidate to pass every Development gate, exceed the distinct ungated baseline by at least 0.25
base-net daily-equity Sharpe, be selected without Historical inspection, and then pass all frozen
Historical and robustness gates. All definitions must use the same exact common-series data blobs.

## Decision relevance

This replacement revisits S002 because Yahoo MOVE begins on 2002-11-12. S003 starts the common
decision history on 2002-11-13, so the first MOVE observation can satisfy the frozen one-session
publication lag, and reserves the remainder of 2002 plus all of 2003 for warmup. S001 and S002
produced no formal run, metric, ranking, candidate freeze, trial-registry observation, or Historical
outcome; their immutable availability evidence remains provenance only.

The study decides whether the same bounded rate-volatility mechanism merits a frozen XLF candidate
for prospective Shadow. Passing grants only `shadow-eligible`, never broker access, orders, live
authorization, or Active status.

## Falsification conditions

The claim is falsified with `fail` if no candidate passes all Development gates within
`maximum_trials=6`, the selected candidate lacks the 0.25 Sharpe advantage, any complete Historical
or robustness gate fails, or the complete family cannot be ranked because of trial exhaustion or
invalid common-data evidence. Missing, stale, conflicting, corrupt, non-replayable, or incorrectly
bound evidence is `indeterminate`. `insufficient-evidence` is permitted only in a registered
prospective Shadow checkpoint under v003.
