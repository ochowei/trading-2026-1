# Hypothesis: XLF Rate-Volatility-Conditioned Pullback Research

## Claim

For completed XNYS sessions from 2000 onward, an `XLF` pullback defined by both (a) an adjusted
close at or below its 20-session Bollinger lower band using two sample standard deviations and
(b) a ten-session adjusted-close return at or below -4% has higher-quality ten-session mean
reversion when the most recently available `^MOVE` observation has not accelerated by more than a
predeclared three-session cap.

The Development candidate family contains exactly three caps: +3, +5, and +7 MOVE index points.
The mechanism claim is supported only if one complete candidate is Development-eligible, exceeds
the distinct ungated pullback baseline by at least 0.25 base-net daily-equity Sharpe, is selected
without inspecting Historical outcomes, and the frozen candidate subsequently passes every
Historical and robustness gate.

## Decision relevance

This study decides whether a bounded rate-volatility gate should advance from a cross-asset lesson
into a frozen XLF candidate eligible for prospective Shadow observation. A passing Historical
screen grants only `shadow-eligible`; it does not authorize live trading, broker access, orders, or
Active status. Failure stops this research round and does not permit threshold expansion or reuse
of the 2021-2025 Historical folds for a repaired candidate.

The study is related to the legacy XLU/TLT implied-volatility lessons only as design provenance.
It does not mutate, rank against, or inherit any legacy experiment identity or outcome.

## Falsification conditions

The claim is falsified and the round stops with `fail` if any of the following complete and
reproducible conditions occurs:

1. No one of the three Development candidates satisfies all frozen Development eligibility and
   risk gates within `maximum_trials=6`.
2. The selected candidate's Development base-net daily-equity Sharpe does not exceed the ungated
   baseline by at least 0.25.
3. The frozen candidate fails any required 2021-2025 Historical gate, including completed-trade,
   fold, return, profit-factor, stress-drawdown, concentration, family-wise selection-adjustment,
   baseline, random-entry, or robustness requirements.
4. A required adverse execution, missed-order, delayed-entry, parameter-perturbation, or market-
   regime challenge falsifies a frozen gate.
5. Trial budget exhaustion, hidden/invalid candidate evidence, partial ranking, or contamination
   prevents the complete candidate family from being evaluated.

Missing, stale, corrupt, conflicting, non-replayable, or incorrectly bound identity/evidence is
`indeterminate`, not a favorable result. Shadow evidence that has not yet reached the frozen
minimum duration or fill count may be `insufficient-evidence` only after a passing Historical
screen and prospective registration.
