# Hypothesis: XLF Gap-Safe Rate-Volatility-Conditioned Pullback Research

## Claim

For completed XNYS sessions from 2004 onward, an `XLF` pullback defined by both (a) an adjusted
close at or below its 20-session Bollinger lower band using two sample standard deviations and
(b) a ten-session adjusted-close return at or below -4% has higher-quality ten-session mean
reversion when the most recently available `^MOVE` observation has not accelerated by more than a
predeclared three-session point cap.

The Development candidate family contains exactly the +3, +5, and +7 MOVE caps. Every candidate
uses publication-lag-safe backward-as-of alignment and the v004 explicit `mark_unavailable`
contract: an observation older than the frozen three-session maximum remains audit evidence but
cannot produce a signal, candidate, or trade. Support requires one complete candidate to pass all
Development gates, exceed the distinct ungated baseline by at least 0.25 base-net daily-equity
Sharpe, be selected without Historical inspection, and subsequently pass every frozen Historical
and robustness gate.

## Decision relevance

This study decides whether the gap-safe rate-volatility mechanism merits a single frozen XLF
candidate eligible for prospective Shadow observation. It revisits the exact cancelled v003 S003
study only because that study stopped before execution when three Development decisions exceeded
its immutable auxiliary maximum lag. S003 produced no formal run, metric, ranking, candidate
freeze, or Historical outcome; its availability inventory is design provenance rather than a
candidate outcome.

A passing Historical screen grants only `shadow-eligible`. It never authorizes broker access,
orders, live trading, automatic submission, Active status, or a profit claim. A failed or
indeterminate round cannot be repaired by loosening the lag boundary, reclassifying unavailable
sessions, expanding the trial budget, or reusing viewed Historical evidence for a modified
candidate.

## Falsification conditions

The claim is falsified with `fail` if any complete and reproducible condition below occurs:

1. No one of the three Development candidates satisfies every frozen eligibility and risk gate
   within `maximum_trials=6`.
2. The selected candidate's Development base-net daily-equity Sharpe does not exceed the distinct
   ungated baseline by at least 0.25.
3. The frozen candidate fails any required 2021–2025 Historical gate, including completed-trade,
   fold, return, profit-factor, stress-drawdown, concentration, baseline, random-entry,
   family-wise selection-adjustment, or robustness requirements.
4. A required cap perturbation, delayed-entry, adverse-cost/worse-fill, missed-entry, or market-
   regime challenge falsifies a frozen gate.
5. Trial-budget exhaustion, hidden or invalid candidate evidence, partial ranking, contamination,
   unavailable-decision leakage, or unequal required common-series identities prevents a complete
   candidate-family evaluation.

Missing, stale, corrupt, conflicting, non-replayable, incorrectly policy-bound, or incomplete
identity/evidence is `indeterminate`, never a favorable result. `insufficient-evidence` is
permitted only at an open prospective Shadow checkpoint after a passing Historical screen, as
defined by the pinned workflow.
