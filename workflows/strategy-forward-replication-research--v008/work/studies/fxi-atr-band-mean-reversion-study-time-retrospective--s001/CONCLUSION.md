# Conclusion: FXI ATR-Band Mean-Reversion Study-Time Retrospective Evaluation

## Outcome

`fail` / `development-selection-failed` / `development`

The frozen six-trial Development family produced no eligible candidate. The sole selectable
candidate completed 14 trades, below the preregistered minimum of 20. Under the pinned v008
study-time retrospective mapping, this is a complete Development gate failure rather than
`insufficient-evidence` or an integrity-driven `indeterminate` result.

## Evidence trace

- `PREREGISTRATION.json` SHA-256
  `fc40e8cb8aaac2ca99e3abed21fcbb7e6af2d45dff9141312faf3b6c677ea857` freezes the
  hypothesis, plan, qualification specification, route, workflow, and human approval.
- `DEVELOPMENT_AUTHORIZATION.json` SHA-256
  `4db201bc337712ffd17c1e7d7aac0186672529bf53b95e3a1c25ca1fc6abe832` limits authority to
  Development and identifies the approved operator.
- The tracked Development gate at
  `results/study-evidence/fxi-atr-band-mean-reversion-study-time-retrospective--s001/development-gate.json`,
  SHA-256 `c247a6e6807be7dae930e0287ef2df2c99939b20252db6ff620a4d7ed46605e3`, records all six
  valid family observations. The candidate passed the traded-years, return, profit-factor,
  drawdown, and complete-family gates but failed `completed_trades >= 20` with 14 trades.
- Qualification-absence evidence SHA-256
  `7ce55dc19227a6093b28ad5236e129d01df2d33029b138423a45eb442d15e8fe` matches the current
  authoritative registry head and confirms that no qualification plan or screen exists for this
  study. No `CANDIDATE_FREEZE.json` exists.
- `TERMINAL_EVIDENCE.json` SHA-256
  `a90846627cf90d106e2846caecef9ae52b44728cfc635477543367bb2fb19275` replays successfully
  for exactly `fail` / `development-selection-failed` / `development` with current-registry
  verification enabled.

## Limitations and follow-up

This decision stops at the 2015-2019 Development stage. It does not inspect or characterize the
preregistered 2021-2025 retrospective Evaluation period and therefore provides no retrospective
support finding. The lineage retains its disclosed `known-contaminated` classification and
incomplete legacy selection history.

This failed research round creates no candidate-freeze, Shadow, activation, broker, order, or
live-trading authority. Any revised mean-reversion definition requires a new preregistered study;
any promotion claim additionally requires later unused `verified-clean` evidence.
