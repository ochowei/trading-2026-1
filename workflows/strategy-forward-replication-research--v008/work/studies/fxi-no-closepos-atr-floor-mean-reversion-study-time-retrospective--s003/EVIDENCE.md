# Evidence: FXI No-ClosePos ATR-Floor Mean-Reversion Study-Time Retrospective Evaluation

## Execution record

### Development authority and boundary

- The guarded transition to `running` created `DEVELOPMENT_AUTHORIZATION.json` at
  `2026-08-18T04:25:24.143277Z`, approved by `ochowei@gmail.com` and operated by
  `codex-primary-researcher-fxi-mean-reversion`.
- Development authorization SHA-256:
  `c7ae9d0398366b4ebfe43ed4c555c26a0374ff883f0296d4bcc107049f8defb0`.
- Authorization and every observation were limited to complete 2015-2019 Development data. No
  2021-2025 Evaluation result, qualification plan/screen, Shadow evidence, broker action, or order
  authority was generated or inspected.
- Execution Git HEAD recorded by every formal observation:
  `74d4197bfc9a81d053068b5552dd20c73fe9c6bc`.
- Composite policy-set identity:
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`.

### Isolated historical cache and immutable snapshots

The first default-cache snapshot attempt failed closed before publication because its requested
2019-12-31 cutoff preceded the monotonic active cache cutoff of 2025-12-31. It produced no snapshot,
result, registry observation, or inspected outcome. The maintained snapshot CLI was then extended
with an explicit disposable `--cache-root` option so this historical Development capture could use
an isolated cache without reading, downgrading, moving, or overwriting the active cache.

- Exact maintained CLI SHA-256: `fbe20a0bbbe419f361e80dc350808d583279ca8680ea4c1dc16246221406368e`.
- Updated market-data contract SHA-256:
  `b60cc1098306d5ecfd91e8a1874cc903e52f04546e26187a96c6e5f329a8987f`.
- Provider-free CLI, cache, definition, and registry checks: 48 tests passed; Ruff check and format
  check passed.
- The candidate snapshot performed one full refresh only through `2019-12-31` in
  `.cache/workflow-studies/s003-development-market-data`. The other five snapshots used that same
  isolated root with `--reuse-full-refresh` and did not call the provider.
- All six manifests passed `trading data verify`, use decision/data cutoff `2019-12-31`, and bind
  common data blob SHA-256
  `9419a451c5494390f25ded462bd5cb3c9673c930b7a04005667d423f8c89eb2b`.

### Complete six-member Development family

Every maintained `trading research run <identity> --workflow
workflows/strategy-forward-replication-research--v008 --manifest <exact-path> --offline` observation
succeeded with `validity_status=valid`. The complete exact manifest/result/observation identities,
file SHA-256 values, source hashes, and profit-factor method are frozen in the Development gate.

| Identity | Trial ID | Snapshot / definition fingerprint | Completed trades / traded years | Base return / PF / Sharpe / MDD | Stress return / PF / MDD |
| --- | --- | --- | --- | --- | --- |
| `fxi-no-closepos-atr-floor-mean-reversion/no-closepos-atr-floor-candidate` | `5f6b3693d559ab3f7e8cf4bf4dfc4fa22e6f79a10212c1a864bd98347a2793fa` | `d77fe5c47b3b76ea513a18f1f6fd8b2317cae99fe4cdcf4dd199637ba90c79df` / `84306c97f43a475c75d9bf348b19b1976b4a1b5d3e2e46dcb7813331a429dc34` | 25 / 2015-2019 | 32.3901% / 1.6431 / 0.6097 / -14.7087% | 22.2114% / 1.4314 / -15.3885% |
| `fxi-no-closepos-atr-floor-mean-reversion/pullback-wr-baseline` | `1be74640289ca88f39991bbdc961418b0cee94ffe92afce6efcd6833fb7b1c76` | `6b5df850ddd660b14012b50c5686e4edaf75ea6f027a3c99439003bee4d7537a` / `d60e82c6076bd89b910afd56434364a8717947aba23c743bd03d9a7158060131` | 33 / 2015-2019 | 24.0960% / 1.3500 / 0.4064 / -18.3597% | 11.6596% / 1.1665 / -21.8113% |
| `fxi-no-closepos-atr-floor-mean-reversion/s002-closepos-reference` | `ce521d386544d3293cd8f8a973888942d06d6cafc89a373900656fbedff60857` | `f4608266f282f491a6ec26a0a209e4dd2496c750b53a9648ff0ef182065306a9` / `5f902af3dede1558af3d25a151f8fb56992f2a662d18ace69590f87202ac0f8a` | 15 / 2015-2019 | 21.2018% / 1.7354 / 0.4531 / -12.5988% | 15.5216% / 1.5131 / -13.0175% |
| `fxi-no-closepos-atr-floor-mean-reversion/no-closepos-atr-floor-1p10-robustness` | `76a5ec4c00363266c84c5aa6f814187eb33ceaccfc4e1025d727c0304d1b733f` | `caadc3a7cbc4f794d3a6eafd4fb30a66ee3a564f1c8eb543168fda0cf88bc82f` / `4824bdc6040b61362f7ee474dbb433ac54fd6d4a01961cad6b3974f3b8a3f0c3` | 22 / 2015-2019 | 2.4202% / 1.0441 / 0.0984 / -19.0705% | -4.5422% / 0.9194 / -19.9720% |
| `fxi-no-closepos-atr-floor-mean-reversion/no-closepos-cooldown-7-robustness` | `552ac20bb3b1a9fb5c5bd8ccfca90d51b2a2178b98c5e3677e1b9f4cbe37d50c` | `6631454a1587ba4d9e8be7e5a93f84cf240752010f2171808880f6be9813129a` / `af7b50d6949168d9ac2e4fe63743ed5d1f0539bd086b78cd4ac943bf72fdf577` | 29 / 2015-2019 | 49.6666% / 1.9035 / 0.7654 / -14.7087% | 36.4025% / 1.6486 / -15.3885% |
| `fxi-no-closepos-atr-floor-mean-reversion/no-closepos-delay-one-session-robustness` | `f8f67ddd9061b04d4ff9bce38f1c5a807400821fb27ba5b0eadd376431ead730` | `46ea58e623ee57b5ee59b50e93e79840222e57993f6fa2a7e88de937f0e334f1` / `c0e4a6b7bccff12c63e62b2bf06e96d3222ae693536f32df547a092ede0e8516` | 24 / 2015-2019 | -2.9260% / 0.9400 / 0.0111 / -25.0701% | -10.1022% / 0.8018 / -26.2594% |

### Candidate eligibility and signal funnel

The sole selectable candidate passed every frozen Development eligibility gate: 25 completed
trades across all five Development years, positive base/stress compounded return, base profit
factor above 1.1, stress profit factor above 1.0, stress maximum drawdown below 20%, and six valid
complete-family observations.

The provider-free candidate funnel contains ordered identities and a canonical-payload SHA-256 at
every stage:

| Stage | Count | Payload SHA-256 |
| --- | ---: | --- |
| `completed-decision-sessions` | 1236 | `b9393d6fe7f0bbd9207d3b3ff9551837eed75cb5bff913b46574126c09d62a07` |
| `inclusive-pullback` | 207 | `aa1c77ed05db0d89071f0d9d44b02aa7508fa74a2f5c4b7c00741f56da7a2c2e` |
| `williams-r` | 140 | `e34e650a712c4e63d355bc8f064a65f4d11c2aec72117ad3bb433c79b9151940` |
| `atr-floor` | 81 | `2b1dcc1286382e656c4c03554512bd40f72cc21668eadc500a45d6cb85895581` |
| `cooldown` | 27 | `8e83e8c8a806930aa166af11fa8f2273abba9ceabe88b96cfb10769050b5637e` |
| `position-conflict` | 25 | `3dfd94e310656aa4d0c2583f3f428176614f0c3ef51928850a42426cc6457ed4` |
| `executable-entry` | 25 | `57a2da13eadfe64d8633dc5c025639aa18dc3b2ef8ede221edb5f5503fb74406` |
| `completed-trade` | 25 | `da17c1663bafa7fca5a57a294a04d3004c00a8584d8e3d37e852a4c5912a6492` |

The funnel retains 54 cooldown suppressions, two canonical `position_already_open` conflicts, no
unfilled entries, and no open candidate. The exact S002 reference diagnostic identifies 45
pullback+WR+ATR-floor dates excluded only by its fixed `ClosePos >= 0.40` threshold; it had no
selection effect.

### Frozen Development artifacts

- Development gate:
  `results/study-evidence/fxi-no-closepos-atr-floor-mean-reversion-study-time-retrospective--s003/development-gate.json`,
  SHA-256 `f95b8cfc16d9e28e8173781ca80f7dd6bc0aba75f8d00e7d63c7694d7491f1a7`.
- Outcome-derived selection input:
  `results/study-evidence/fxi-no-closepos-atr-floor-mean-reversion-study-time-retrospective--s003/development-selection.json`,
  SHA-256 `966c6618415872db5a14b275f24ac70e7323d7034193da7b093ed664c7e37e1e`.
- The selection input contains exactly `selected_candidate`, `family_baseline`, and ordered
  `complete_family`; each member contains only `source_identity`, `trial_id`, and
  `definition_fingerprint`. It is explicitly `not-approved-not-frozen`.
- Trial registry SHA-256 after the six formal observations:
  `59968f1e610521c9fba66917841a6242871bbfa87a994a85fd54be0cc36d5d92`.

## Deviations and missing evidence

- Operational deviation: the default active cache could not legally move backward from 2025 to
  the frozen 2019 Development cutoff. The isolated-cache CLI path described above resolved this
  without changing data, strategy, family, thresholds, selection rules, or outcome semantics. The
  failed first attempt produced no formal artifact or outcome.
- No `CANDIDATE_FREEZE.json` exists. Candidate freeze requires separate current-time owner approval
  and was not authorized or attempted.
- No qualification plan, registry mutation, Evaluation snapshot/result, challenge artifact,
  terminal evidence, Shadow evidence, completion, broker access, or order action exists for S003.
- Evaluation and all later-stage evidence remain intentionally missing because only Development
  was authorized.
