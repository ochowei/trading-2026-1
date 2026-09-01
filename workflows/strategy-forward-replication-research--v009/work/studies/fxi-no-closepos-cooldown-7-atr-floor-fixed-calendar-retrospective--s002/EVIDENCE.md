# Evidence: FXI No-ClosePos Cooldown-7 ATR-Floor Fixed-Calendar Retrospective Study

## Execution record

### Development authorization and execution boundary

- The preregistered owner `ochowei@gmail.com` authorized Development at
  `2026-09-01T07:08:03.802490Z`. The add-only authorization is
  `DEVELOPMENT_AUTHORIZATION.json`, SHA-256
  `4e922b8015a3d2d3be47360efce6bafcf06208646b3a90eb174df088472fd4b6`.
- Authorization was limited to outcome-relevant Development under this exact
  `fixed-calendar-retrospective` study. It granted no candidate-freeze, Evaluation, replay,
  Shadow, broker, position, or order authority.
- All six observations used the active v009 release, composite policy-set identity
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`, immutable FXI data
  cutoff `2018-12-31`, shared data blob
  `1b3ed72b292351029e5c1fea705fc87dda61be7e6f94b4ca039e1218f1b8f70a`, and formal `offline`
  run mode. The provider-backed snapshot refresh used the isolated cache generation
  `.cache/workflow-studies/v009-s002-development-market-data`; the other five definitions reused
  that exact eligible full-refresh generation.
- Execution was orchestrated from Git commit
  `551b88c4a70315f41436abe90fdea1a98b02b032`. Each formal result retains the complete
  orchestration/source snapshot required to reproduce that observation.

### Complete-family Development observations

All six preregistered family members produced one valid, succeeded formal observation. The table
reports canonical base/stress net metrics; returns and drawdowns are decimal ratios.

| Role / identity | Observation | Completed trades | Base return / PF / Sharpe / MDD | Stress return / PF / MDD |
| --- | --- | ---: | --- | --- |
| candidate — `no-closepos-cooldown-7-robustness` | `b591311b93854000b5bccfb56002a5be` | 21 | `0.3107058545` / `1.7602781394` / `0.6737984034` / `-0.1470874663` | `0.2255205616` / `1.5332675680` / `-0.1538851563` |
| baseline — `pullback-wr-baseline` | `beca8e508834460cbd5b25f08c2c9a57` | 27 | `0.1934176953` / `1.3437695571` / `0.4089620790` / `-0.1806953338` | `0.0946350957` / `1.1634701896` / `-0.2014033734` |
| reference — `no-closepos-atr-floor-candidate` | `fc3b205d7e7a43619f47f84fba3e678f` | 19 | `0.2731814471` / `1.7395299997` / `0.6756296723` / `-0.1470874663` | `0.1980781660` / `1.5183969216` / `-0.1538851563` |
| reference — `s002-closepos-reference` | `4a91cbca12ba4b28bc167b0e66f4d063` | 10 | `0.1096797089` / `1.4882435474` / `0.3330642003` / `-0.1259878590` | `0.0747320456` / `1.3190567868` / `-0.1301747156` |
| robustness — `no-closepos-atr-floor-1p10-robustness` | `7e67b9842c324b50afe470932fdbe6a7` | 17 | `0.0797313560` / `1.2068333907` / `0.2641817884` / `-0.1907048302` | `0.0225629547` / `1.0562468479` / `-0.1997198933` |
| robustness — `no-closepos-delay-one-session-robustness` | `51ab82adde6e4c5cb7cd4ac39c4270ef` | 18 | `-0.0988058758` / `0.7698623845` / `-0.1542581737` / `-0.2507010804` | `-0.1492480598` / `0.6680598994` / `-0.2625944817` |

The authoritative Development gate retains every complete trial ID, definition fingerprint,
source hash, manifest/snapshot identity, observation identity, result path and checksum. It is:

- `results/workflows/strategy-forward-replication-research--v009/fxi-no-closepos-cooldown-7-atr-floor-fixed-calendar-retrospective--s002/development/development-gate.json`
- SHA-256 `e21607596b930dba8cb3ef139ee84e3a567c78d176e2d39ed7b748b79d7a7533`

### Frozen Development eligibility result

The sole seven-session-cooldown selection candidate completed 21 canonical trades across four
Development years. It passed the minimum-20-trades, positive base/stress return, base/stress
profit-factor, stress-drawdown, traded-years, and complete-family-validity gates. The two
non-completed raw signals were explicit `position_already_open` suppressions; no unavailable
decision, unfilled entry, or open candidate remained.

Development therefore produced one eligible candidate. The exact outcome-derived selection is
`results/workflows/strategy-forward-replication-research--v009/fxi-no-closepos-cooldown-7-atr-floor-fixed-calendar-retrospective--s002/development/development-selection.json`,
SHA-256 `7b46c57f74a6f87c815b2c98acc70b62f34f1248eb4c2c8d9ca81b54a2f35196`.
It contains only the selected candidate, distinct family baseline, and ordered complete family
with their source identities, trial IDs, and definition fingerprints.

### Candidate freeze and provider-free readiness

- The preregistered owner `ochowei@gmail.com` separately approved the exact Development selection
  at `2026-09-01T07:17:17.066914Z`. The guarded freeze created `CANDIDATE_FREEZE.json`, SHA-256
  `071c20f6ca3640d18c83b1f642f8550612c41bf0184a6993bff6bcd02b34c0c1`.
- The freeze binds the seven-session-cooldown candidate, distinct baseline, all six ordered family
  members, frozen trial budget, preregistration, Development authorization, workflow release, and
  hypothesis/plan/specification digests. Its scope explicitly grants no Evaluation, Shadow,
  broker, or order authority.
- The exact-study provider-free compiler and `register-study --dry-run` reproduced six frozen
  family trials under `fixed-calendar-retrospective` and derived plan identity
  `retrospective-plan-9f08e2a00cfe3632acafdc6a76075ebdc84b5975ed69284fc5cff83cc6503c72`.
  The dry-run did not mutate either registry.

- The preregistered owner separately authorized registry registration at
  `2026-09-01T07:19:16.583747Z` with the exact disclosed statement that S002 was designed after
  S001 Development outcomes were observed, prior FXI research may have inspected 2020-2025, and
  all evidence is `known-contaminated` retrospective evidence without prospective-promotion or
  live-trading authority.
- The guarded atomic registration appended historical plan
  `retrospective-plan-c38e1fbe354068c8a161381583f7538b228ba1a4181ff258bef650b1917111a8`.
  Its registry event hash is
  `88726ef637884627c219a5f4ce5f42d942d46735db4c8602896a6e66b35dd56e`; the verified local
  registry/head checksums are
  `578ee961d25e894bd55d7d84f258d3a46a30148acf40a4ecb235f0b4dec62285` and
  `418f192b86a7759fe1b285ea210cf7c94c4a1ac56d383f2a3c417c591b2ebd8a`.

At the frozen-readiness checkpoint, no Evaluation observation, challenge artifact, qualification
screen, or replay artifact existed. Evaluation proceeded only after the separate authorization
recorded below.

### Fixed Historical Evaluation observations and challenge dry-run

- The preregistered owner separately authorized fixed 2020-2024 Historical Evaluation before the
  first Evaluation snapshot. The authority was limited to immutable Evaluation snapshots and
  formal observations; it granted no 2025 replay, Shadow, broker, position, order, or live
  authority.
- All six formal Evaluation observations use data cutoff `2024-12-31`, shared immutable FXI data
  blob `3a28c034baad3cad095a4baff6295500e1448ba6e1177a118f0cca2d0419fa8e`, the exact frozen
  definition fingerprints, composite v009 policy set, and `offline` run mode. The provider-backed
  refresh used `.cache/workflow-studies/v009-s002-evaluation-market-data`; five definitions reused
  the same eligible full-refresh generation.

| Role / identity | Snapshot | Observation | Result SHA-256 |
| --- | --- | --- | --- |
| candidate — `no-closepos-cooldown-7-robustness` | `1b4f89fc896c136dca9677a75cec5401d4342dc861af738d3ebc2382860d998b` | `007483220f604bb2b13bf8cd853c3611` | `d6637154d2a70a2ea53c65b38eb667b02ee86c5710c30e7e7e39dbad0a21bbe4` |
| baseline — `pullback-wr-baseline` | `b61abc07c82759799c65c4b3b233524cdaa41439a450fa473cf375ad2604cf38` | `d308bd66f73d4d69ae733ace213289be` | `85a8ba715018716c834dc0cf0c511b2ede34194c7f27a0ce93ec5eb3ee03f4db` |
| reference — `no-closepos-atr-floor-candidate` | `50ed8598ddb68244a39ffe7e8a6a86b529db1c677c76b709fc16e615c37b80ec` | `200c95e1ebac4992b503ff889364c445` | `61f6004c8cf71bbddbc899b55f752a91730c029d56e3a45a00ab20648276ec05` |
| reference — `s002-closepos-reference` | `375305110646174306fba2704a9160223cdde37f8383bc10720f9553935098dd` | `02913714382f4dd187a2a8f9302fc5bd` | `12a248ab3bb93fb7584cf6b936f5bea1cbec2610e3422b37a7930ea1ce63f5ba` |
| robustness — `no-closepos-atr-floor-1p10-robustness` | `76e4935dbe4a520db93329020f7e2caf9bbefbf7623c9d57f176377853eb5781` | `7a0aca26afd2433982a2e30edfe7fe47` | `0fde479ca439830372fe7093aebb44b71a7c6547fe104499a4569a659936f506` |
| robustness — `no-closepos-delay-one-session-robustness` | `3c038a1357b12b2bae931b6bef4f0e21e0952e5ddf5ca525310952d8cab8628d` | `cadf105fd3c0458c82455df7623a79d7` | `c61f21df51e3cc1f211f437e143e63cb269a1423b2a69b293fe0e6a0882b6fc4` |

- The independent challenge-only dry-run resolved exactly one successful/valid observation for
  each frozen member, verified the common data generation and exact 2020-2024 role projection,
  and validated all nine frozen challenge methods without mutation. Its prospective publication
  namespace is
  `fixed-historical-evaluation-challenges/challenges-58b12e201af9edeaeef08e9fcef50d2b90830faf7e2a0967e1c4d83b477344cb/`.
- After separate challenge-only publication authority, the guarded operation atomically published
  exactly nine distinct content-addressed artifacts plus `MANIFEST.json` in that namespace. The
  manifest SHA-256 is
  `fdbc9e2ae14448376f67909e70052ccbc5b83b2bfc89110ba4415ca19410254b` and binds publication ID
  `challenges-58b12e201af9edeaeef08e9fcef50d2b90830faf7e2a0967e1c4d83b477344cb`, exact study,
  qualification plan, preregistration, specification, Development authorization, and candidate
  freeze.
- The manifest records `observed=true` for cash, family baseline, market regimes, missed entries,
  parameter perturbation, and random entry. It records `observed=false` for delayed entry, higher
  costs, and worse fills. These are immutable challenge observations; the operator does not assign
  the study outcome.

### Qualification-screen fail-closed result

- After separate qualification-screen authority, the guarded screen was invoked against historical
  plan `retrospective-plan-c38e1fbe354068c8a161381583f7538b228ba1a4181ff258bef650b1917111a8`
  and the six exact Evaluation snapshots recorded above. It stopped before any qualification-
  registry mutation with `qualification error: candidate holding period exceeds the frozen
  dependency`.
- The frozen specification declares `execution_lag_sessions=1`,
  `maximum_holding_sessions=20`, and `dependency_sessions=21`. The frozen FXI definition and its
  explicit unit test implement time expiry at the open after twenty complete post-entry holding
  sessions: signal session + one-session entry lag + twenty complete holding sessions + the next
  session's open. The actual signal-to-outcome dependency is therefore 22 sessions.
- Two selected-candidate Evaluation trades exercised that exact boundary: signals `2023-06-21`
  and `2023-12-05` entered on the next session and exited by `time_expiry` 21 market-session
  offsets after entry. All target/stop exits were within 20 offsets. The screen correctly rejected
  the mismatch between the immutable candidate evidence and the underspecified frozen dependency.
- Read-only verification after the rejection found exactly one qualification-registry event and
  unchanged registry SHA-256
  `578ee961d25e894bd55d7d84f258d3a46a30148acf40a4ecb235f0b4dec62285`.
  No screen result, disposition, replay artifact, Shadow evidence, broker access, position action,
  or order was created.

## Deviations and missing evidence

- The first attempt to execute the candidate against S001's 2018 snapshot was rejected before
  strategy execution because that old manifest's complete definition blob did not match the
  current exact orchestration sources. The fail-closed rejection created no result and no formal
  trial-registry observation. The operator did not weaken exact binding or reuse the stale
  manifest.
- The first current-source snapshot refresh could not reach the provider inside the restricted
  network sandbox. The identical maintained CLI operation was retried with approved network
  access and succeeded; the remaining five snapshots reused the isolated verified cache
  generation. This was an operational recovery, not a change to definitions, calendar, policies,
  costs, thresholds, or selection rules.
- The refreshed provider generation has data-blob SHA-256
  `1b3ed72b292351029e5c1fea705fc87dda61be7e6f94b4ca039e1218f1b8f70a`, rather than S001's
  `8daa14877bba5425705061a64cf39950e354fd51cbc9c1280ff8f666d0eaf48b`. This reflects the new
  immutable full refresh at the same frozen cutoff. It caused only small numerical revisions and
  did not change the candidate's 21 completed trades or any Development gate decision.
- No Development, Evaluation-observation, or challenge-publication evidence is missing. The
  qualification screen was attempted and failed closed because the preregistered dependency was
  one session too short; replay evidence remains absent and was not authorized.
- Correcting `dependency_sessions` from 21 to 22 is a research-design change. The operator did not
  edit the preregistered `HYPOTHESIS.md`, `PLAN.md`, or `QUALIFICATION_SPEC.json`, did not weaken
  the screen validator, and did not reinterpret the candidate's frozen expiry semantics. Under the
  workflow governance rule, S002 cannot continue and any corrected attempt must be a new study
  linked back through `revisits`.
