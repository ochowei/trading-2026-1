# Conclusion: FXI Volume-Stratified ATR-Floor Mean-Reversion Study-Time Retrospective Evaluation

## Outcome

`fail` / `development-selection-failed` / `development`

The frozen six-trial Development family produced no eligible candidate. The sole selectable
ATR-floor candidate completed 15 trades, below the preregistered minimum of 20. It passed the
traded-years, base/stress return, base/stress profit-factor, stress-drawdown, and complete-family
validity gates, so this is specifically a sample-size failure rather than a negative-return or
profit-factor failure. Removing the S001 ATR ceiling added only one completed trade relative to the
14-trade S001 reference and did not cure the frozen eligibility failure.

Under the pinned v008 study-time retrospective mapping, a complete and trustworthy Development
gate failure is `fail` / `development-selection-failed` / `development`; it is neither
`insufficient-evidence` nor an integrity-driven `indeterminate` result. The 33-trade family
baseline and all robustness members are non-selectable and cannot replace the failed candidate.

## Evidence trace

- `PREREGISTRATION.json` SHA-256
  `b138b6bb8620ea7daf3f354b127dd91d4c1481f5e146cec0f4137e3f0e775b86` freezes the
  hypothesis, plan, qualification specification, route, workflow, lineage, and human approval.
- `DEVELOPMENT_AUTHORIZATION.json` SHA-256
  `ec61f9275d530003efd0f810553bb13adeb6f9ee251aee2cddeb7bf768069f1c` limits authority to
  Development and identifies the approved operator.
- The tracked Development gate at
  `results/study-evidence/fxi-volume-stratified-atr-floor-mean-reversion-study-time-retrospective--s002/development-gate.json`,
  SHA-256 `ece8bf26de64fe839628771b8cb008cc60067710ad672735ab383b1c8ac07da6`, records all six
  valid family observations, the exhausted six-trial budget, and the candidate's sole failed gate:
  `completed_trades >= 20`, observed 15.
- Qualification-absence evidence SHA-256
  `7ce55dc19227a6093b28ad5236e129d01df2d33029b138423a45eb442d15e8fe` matches the current
  authoritative registry head and confirms that no qualification plan or screen exists for this
  study. No `CANDIDATE_FREEZE.json` exists.
- `TERMINAL_EVIDENCE.json` SHA-256
  `5651a04887e225f015103645b53d601516851b5ce5b15c97931dc64482779668` replays successfully
  for exactly `fail` / `development-selection-failed` / `development` with current-registry
  verification enabled.

## Limitations and follow-up

This decision stops at the 2015-2019 Development stage. It does not inspect or characterize the
preregistered 2021-2025 retrospective Evaluation period, including the volume-tercile stability
challenge, and therefore provides no retrospective support finding. The lineage retains its
disclosed `known-contaminated` classification, incomplete trial history, and incomplete prior
selection history.

This failed research round creates no candidate freeze, Shadow, activation, broker, order, or
live-trading authority. Any revised mean-reversion definition requires a new preregistered study;
any promotion claim additionally requires later unused `verified-clean` evidence.
