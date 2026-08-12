# Plan: XLF Rate-Volatility-Conditioned Pullback Publication-Lag-Safe Research

## Inputs and frozen identities

### Governance and provenance

- Workflow: `strategy-forward-replication-research@v003`; release SHA-256
  `9c5a554751a70d6c286fa0ca938ee171cc5da81d2e683d29b11ba06579aad183`; workflow SHA-256
  `11cebc16588c2feae2637128b4b18a015d0de65507ee47096ae0a3e8aec0370f`.
- Composite policy set: `4ade828a43e2cfab97b2933c5722107cf00ccf27c3a90c92b60c19b67f511189`.
- Owner/approver: `ochowei@gmail.com`; researcher: `codex-primary-researcher-xlf-s003`.
- Exact revisit: `workflows/strategy-forward-replication-research--v003/work/studies/xlf-rate-volatility-conditioned-pullback-revised-availability--s002`.
- S001 and S002 availability failures are provenance only. No outcome from either study was viewed.

### Market data and roles

- Primary XLF and auxiliary MOVE are Yahoo auto-adjusted daily data required from 2002-11-13.
  XLF uses complete XNYS coverage; MOVE uses provider-observation coverage.
- MOVE publication time is unknown. Decisions use backward-as-of observations after one XNYS
  publication-lag session, with maximum observation lag three sessions. Yahoo's verified first MOVE
  observation is 2002-11-12, one session before the common decision boundary.
- Warmup only: 2002-11-13 through 2003-12-31. Development: 2004-01-02 through 2020-12-31.
  Historical: annual folds 2021–2025. Pre-registration 2026 sessions are quarantined; Shadow is
  prospective only after passing Historical evidence and current-time registration.
- Every segment has 21 initial warmup-only primary sessions and 11 final purged signal sessions.
  No position crosses a role or annual fold.

### Trial inventory and execution

`maximum_trials=6`: three MOVE cap candidates (+3, +5, +7), one distinct ungated pullback baseline,
and two deterministic post-selection robustness definitions (selected cap minus one point and
selected cap with entry delayed to `t+2`). The four permanent selection identities use family
`xlf-rate-volatility-conditioned-pullback-publication-lag-safe`; the robustness identities are
materialized only after selection and cannot win. S001/S002 identities remain unchanged.

Signal at completed `t`: XLF close <= 20-session mean minus 2.0 sample standard deviations and
ten-session adjusted-close return <= -4%. Gated definitions additionally require backward-as-of
MOVE three-decision-session change <= their cap. Entry is `t+1` open and exit is the open ten
completed sessions later. The canonical isolated sleeve has capital 1.0, fractional quantity, one
position, no leverage or pyramiding, and released canonical base/stress costs.

## Method and stages

Preregister before any S003 refresh, snapshot, run, metric, result inspection, or ranking. After
explicit Development advancement, cap-3 performs the sole full refresh through 2020-12-31. Cap-5,
cap-7, and baseline use `--reuse-full-refresh`. Before execution, all manifests must verify; all four
must share one XLF blob and all gated manifests one MOVE blob. Any mismatch or availability failure
stops without a run or partial ranking.

A candidate is Development-eligible only with at least 30 completed base-net trades across ten
traded years, base return > 0, base profit factor > 1.1, stress return > 0, stress profit factor >
1.0, stress maximum drawdown <= 15%, no integrity difference, and base-net daily-equity Sharpe at
least 0.25 above baseline. Rank every eligible candidate by Sharpe, ties cap-3 then cap-5 then cap-7.
No eligible candidate is `fail`. Persist the complete set and obtain owner approval before freeze.

Historical evaluates only the frozen candidate, baseline, and two robustness definitions on
2021–2025 annual folds. Challenges are cash; baseline; 1,000 exposure-matched random entries;
family-wise 20-session block bootstrap over all candidates; cap-minus-one; delayed entry;
stress/worse fills; deterministic 10% missed entries; and annual regimes. Randomized challenges use
seed `20260812`. Only a passing screen permits prospective Shadow registration; Shadow requires at
least 252 completed sessions and 12 simulated fills.

## Metrics and outcome rules

Historical gates are conjunctive: five complete folds; at least 20 trades; at least three traded
folds; at least 60% positive traded folds; base return > 0 and profit factor > 1.1; stress return >
0 and profit factor > 1.0; stress drawdown <= 15%; no fold over 50% of trades or positive profit;
Sharpe advantage >= 0.25; return above cash, baseline, and the 90th-percentile random entry;
family-wise confidence >= 90%; and no required challenge with failed stress/risk/integrity gates.

`pass` grants only `shadow-eligible`; `fail` follows a complete failed Development/Historical gate
or trial exhaustion; `indeterminate` follows unverifiable identity/data/source/policy/provenance or
gate evidence; `insufficient-evidence` is limited to an eligible prospective Shadow checkpoint.

## Deviations and stopping rules

After preregistration, do not change availability, data roles, inventory, trial budget, formulas,
thresholds, snapshot-reuse procedure, common-blob equality, baseline, costs, execution, gates,
seeds, or outcome rules. Any such change requires cancellation and a new exact revisit.

Pause on incomplete data, unequal blobs, digest drift, invalid manifests, missing source bytes,
provenance/parity mismatch, or partial availability. Terminate when no Development candidate is
eligible, the budget is exhausted, a Historical/Shadow gate fails, evidence is unrecoverable, or
the owner stops the study. Never repair an unfavorable result, hide a trial, loosen gates, or use
Historical/Shadow outcomes to redesign candidates.
