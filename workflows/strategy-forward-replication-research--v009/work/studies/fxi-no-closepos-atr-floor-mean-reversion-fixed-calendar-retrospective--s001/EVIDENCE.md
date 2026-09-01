# Evidence: FXI No-ClosePos ATR-Floor Mean-Reversion Fixed-Calendar Retrospective Study

## Execution record

### Development authorization and execution boundary

- The preregistered owner `ochowei@gmail.com` authorized Development at
  `2026-09-01T06:17:18.595089Z`. The add-only authorization is
  `DEVELOPMENT_AUTHORIZATION.json`, SHA-256
  `25a3a5cc812e62ef6f23a06a7902bc757fa335eef585ac109b5f582a4c8d7013`.
- Authorization was limited to outcome-relevant Development under this exact
  `fixed-calendar-retrospective` study. It granted no candidate-freeze, Evaluation, replay,
  Shadow, broker, position, or order authority.
- All six observations used the active v009 release, composite policy-set identity
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`, immutable FXI data
  cutoff `2018-12-31`, shared data blob
  `8daa14877bba5425705061a64cf39950e354fd51cbc9c1280ff8f666d0eaf48b`, and formal `offline`
  run mode. The provider-backed snapshot refresh used the isolated cache generation
  `.cache/workflow-studies/v009-s001-development-market-data`; no active/default cache was
  replaced.
- Execution was orchestrated from Git commit
  `ec1661fd54755bb58e265bb9643d78c83bcdda8a`. Each formal result retains the complete
  orchestration/source snapshot required to reproduce that observation.

### Complete-family Development observations

All six preregistered family members produced one valid, succeeded formal observation. The table
reports canonical base/stress net metrics; returns and drawdowns are decimal ratios.

| Role / identity | Observation | Completed trades | Base return / PF / Sharpe / MDD | Stress return / PF / MDD |
| --- | --- | ---: | --- | --- |
| candidate — `no-closepos-atr-floor-candidate` | `10fddde648f2413d8a7723bca7f8e15f` | 19 | `0.2731811061` / `1.7395286630` / `0.6756305090` / `-0.1470870324` | `0.1980778451` / `1.5183958158` / `-0.1538847258` |
| baseline — `pullback-wr-baseline` | `310d3c6092e14996b0ca1f7b7cb7ac57` | 27 | `0.1934176939` / `1.3437697133` / `0.4089627584` / `-0.1806951462` | `0.0946350944` / `1.1634702554` / `-0.2014031906` |
| robustness — `s002-closepos-reference` | `7e34f4d6859b43799b345836a9a8c7f2` | 10 | `0.1096797089` / `1.4882435474` / `0.3330648057` / `-0.1259877658` | `0.0747320456` / `1.3190567868` / `-0.1301746229` |
| robustness — `no-closepos-atr-floor-1p10-robustness` | `06f68619c36d4102961158110b1ac055` | 17 | `0.0797310022` / `1.2068323832` / `0.2641812084` / `-0.1907044184` | `0.0225626196` / `1.0562459904` / `-0.1997194862` |
| robustness — `no-closepos-cooldown-7-robustness` | `b7bc663434bc4ec5b12b62f6317699e6` | 21 | `0.3107052181` / `1.7602757152` / `0.6737991914` / `-0.1470870324` | `0.2255199665` / `1.5332656078` / `-0.1538847258` |
| robustness — `no-closepos-delay-one-session-robustness` | `c2f79f6905d74fbfab8be2dcce1e6cc0` | 18 | `-0.0988055473` / `0.7698629974` / `-0.1542581208` / `-0.2507008881` | `-0.1492477497` / `0.6680603892` / `-0.2625942924` |

The authoritative Development gate retains every complete trial ID, definition fingerprint,
source hash, manifest/snapshot identity, observation identity, result path and checksum. It is:

- `results/workflows/strategy-forward-replication-research--v009/fxi-no-closepos-atr-floor-mean-reversion-fixed-calendar-retrospective--s001/development/development-gate.json`
- SHA-256 `65cdf88b2666e53c2f48f5e9c7acbbbca0971a0a9df8ca0a9191cc9e5b3a7f4d`

### Frozen Development eligibility result

The sole selection candidate completed 19 canonical trades across four Development years. It
passed the positive base/stress return, base/stress profit-factor, stress-drawdown, traded-years,
and complete-family-validity gates, but failed the preregistered minimum of 20 completed trades.
Because eligibility is a conjunction and robustness definitions cannot substitute for the sole
selection candidate, Development produced no eligible candidate and no selection JSON.

No `CANDIDATE_FREEZE.json`, qualification plan, qualification screen, Evaluation observation,
challenge artifact, or replay artifact was created. The operator does not assign the terminal
outcome; that judgment remains reserved for independent review.

### Current-head qualification absence and terminal linkage

- The preregistered qualification registry was initialized as an empty verified registry solely
  to materialize its authoritative absence proof. It contains zero events and therefore no plan
  or screen for this study.
- The current-head content-addressed absence snapshot is
  `results/evidence/qualification/f3ef0e023effd0f9ae11540b48c8d03ef548e52d67a79f1a31fca27b9ad8f791.json`;
  its filename and SHA-256 are both
  `f3ef0e023effd0f9ae11540b48c8d03ef548e52d67a79f1a31fca27b9ad8f791`.
- `TERMINAL_EVIDENCE.json` links the exact preregistration, qualification spec, Development
  authorization, Development gate, and current-head absence snapshot. Its SHA-256 before the
  review transition is `074491812ac70250a3845a3475dc6360a850c874f8d05942da7a3446c7d14256`.
- `CONCLUSION.md` remains untouched for the independent reviewer.

## Deviations and missing evidence

- The first guarded transition attempt rejected the command before any Development outcome was
  inspected because the transition layer recognized the older structured route capability but
  omitted v009's `fixed-calendar-retrospective-v1` capability. No lifecycle or evidence mutation
  occurred. The route recognition was corrected in `src/trading/workflow/studies.py`, and the
  first-Development authorization test was expanded to cover both structured routes before the
  guarded transition was retried successfully.
- The first snapshot refresh could not reach the provider inside the restricted network sandbox.
  The identical maintained CLI operation was retried with approved network access and succeeded;
  the remaining five snapshots reused the isolated verified cache generation. This was an
  operational recovery, not an outcome-relevant change to data, definitions, calendar, costs,
  thresholds, or selection rules.
- Appending the six valid observations exposed a pre-existing result-layout migration problem:
  the v009 migration-time digest for the shared trial registry still terminated at the active,
  append-only registry path, so a legitimate append made two frozen v008 studies report digest
  drift during repository-wide validation. The exact migration-time bytes were recovered from the
  current Git base and retired through the already-supported byte-identical v010 second hop at
  `results/registries/history/trial_registry--716e101f6d1aa2273760677f850d0e3b375da5ffc22d18545fe65411426eb778.json`.
  The active categorized registry was then restored byte-for-byte with this study's observations.
  Historical flat-path readers now resolve the immutable old bytes, current readers resolve the
  active append-only registry, and full workflow control-state validation returned `N05`.
- The fixed 2014 Development year contained no completed candidate trade. This is observed study
  evidence, not missing data: the formal snapshot covers the frozen cutoff, and the candidate's
  retained signal funnel records 21 raw signals, two explicit `position_already_open`
  suppressions, 19 completed trades, and no unavailable decision, unfilled entry, or open
  candidate.
- No outcome evidence is missing for the terminal Development checkpoint. Later-stage evidence is
  absent by design because the failed eligibility conjunction legally stops advancement before
  candidate freeze.
