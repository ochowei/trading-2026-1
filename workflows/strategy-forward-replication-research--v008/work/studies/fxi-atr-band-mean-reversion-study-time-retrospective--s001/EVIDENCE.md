# Evidence: FXI ATR-Band Mean-Reversion Study-Time Retrospective Evaluation

## Execution record

### Development authority and boundary

- The guarded transition to `running` created `DEVELOPMENT_AUTHORIZATION.json` at
  `2026-08-17T01:50:02.081872Z`, approved by `ochowei@gmail.com` and operated by
  `codex-primary-researcher-fxi-mean-reversion`.
- Authorization SHA-256:
  `4db201bc337712ffd17c1e7d7aac0186672529bf53b95e3a1c25ca1fc6abe832`.
- Authorization scope is Development only. No Evaluation, Shadow, broker, or order authority was
  used.
- Execution Git HEAD: `db3c53c9c1e681892562454d08e7164b0f70b435`.
- Composite policy-set identity:
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`.
- Every formal snapshot used decision session and data cutoff `2019-12-31`; every formal run used
  `trading research run ... --offline`. No 2021-2025 Evaluation result was generated or inspected.

### Complete six-member Development family

All six manifests passed `trading data verify`. All six formal observations succeeded with
`validity_status=valid`. Profit factors below are recomputed from completed canonical-sleeve net
fills as total positive net P&L divided by absolute total negative net P&L.

| Identity | Trial ID | Snapshot / definition fingerprint | Completed trades / traded years | Base return / PF / Sharpe / MDD | Stress return / PF / MDD |
| --- | --- | --- | --- | --- | --- |
| `fxi-atr-band-mean-reversion/atr-band-candidate` | `2492dd0b2de348ee341a94a79256b280fb7ca8519996e6b69450fae7d6b8b315` | `2591e691d999453069ac14da9ebc4ee02668689b2301da42ee17976e071f515c` / `7ddf006e5ceb595659b1aacfb135c06244f581b1135cc10c567d8737d3d74b77` | 14 / 2015-2019 | 13.9412% / 1.5049 / 0.3283 / -14.1297% | 8.9493% / 1.3086 / -16.2217% |
| `fxi-atr-band-mean-reversion/pullback-wr-baseline` | `3462f2c46c8d2e23f4bc4c6bd6bfa42d728f3dce0f5002b81e5369505cefdfdc` | `764bd2b5d0ff949c17e60f0f18c9471dcb495eeb7d4240f44eb803fee79dd848` / `0befd904a62c296b734d296fda87566e449940cd11fbba5bae59b4168789b0f8` | 33 / 2015-2019 | 24.0960% / 1.3500 / 0.4064 / -18.3596% | 11.6597% / 1.1665 / -21.8113% |
| `fxi-atr-band-mean-reversion/atr-floor-1p10-robustness` | `a380a5b680d85cf1b4213e56a3f3fba5cbda01324f99abd8338e9221cdbd5262` | `89d960fb46a02226a11085976147ee86970c4ee4be19fbaa4c0aef4e05f0cfb9` / `1cf546efa3f158bf6d5d0a25fce01d1e31cd1f2b4d3682ffc13d99047edd6db1` | 13 / 2015-2019 | 9.3347% / 1.3381 / 0.2468 / -11.5434% | 4.8796% / 1.1683 / -13.8362% |
| `fxi-atr-band-mean-reversion/atr-ceiling-1p30-robustness` | `7eb0da5535e4b6328b81dd1343bf10da30a26c6b18253c561f120cd95b6afe3e` | `db175eb9986260dd7fbe7d8d5deb4cf95bbe5ac2bd9457c7373c19afc57196ac` / `c89252011a8c2a2f63af70a29ef10c9c4f2307acf2ef8f1035ebfc36eed1c90c` | 14 / 2015-2019 | 13.9412% / 1.5049 / 0.3283 / -14.1297% | 8.9493% / 1.3086 / -16.2217% |
| `fxi-atr-band-mean-reversion/hold-18-robustness` | `7366c663e42250f59297a3b2586926919f7ab9b7880157834ca57153d6c0b022` | `53edd21b747da2e8a8a0745c2c7d2f14b5531d8288896af5c5e0311a9975cd16` / `0c45c30dde995693f971c90e67e1a8a883b6ad9ae26417d69e49ddc51885bcb2` | 14 / 2015-2019 | 10.2149% / 1.3876 / 0.2594 / -14.1297% | 5.3863% / 1.1940 / -15.6370% |
| `fxi-atr-band-mean-reversion/delay-one-session-robustness` | `da05516060207d5ea963490dc11a38ba31b901143d639355233a5decb51a2a7c` | `6bdb0a8284cd4d592d46426b293be252e2940b108c2b097e717ff45abaebec72` / `fd9bc77a7bc6f77679fd44f6535aaf833161bbe7ad8c3c5bb4178fb59382401d` | 14 / 2015-2019 | 12.7090% / 1.4519 / 0.3295 / -16.0777% | 7.7711% / 1.2634 / -18.4602% |

Exact candidate evidence:

- Manifest:
  `results/fxi-atr-band-mean-reversion--atr-band-candidate/2591e691d999453069ac14da9ebc4ee02668689b2301da42ee17976e071f515c.snapshot.json`,
  file SHA-256 `25381209b8c94171ac2ca1852aead48bf4b38578a22bc5bac100ba94917fd5aa`.
- Result:
  `results/fxi-atr-band-mean-reversion--atr-band-candidate/20260817_015406_763994_offline_592d2b9be6b94919969ff4513265bea6.json`,
  SHA-256 `899cdf4f5b3d7d4813e3399c557143c5ec45452ec410cfc13a70d13b609b083c`.
- Trial-registry observation ID: `52002f72015146c98c4f114ef8ac5672`, observed at
  `2026-08-17T01:54:06.786677Z`.

Exact baseline evidence:

- Manifest:
  `results/fxi-atr-band-mean-reversion--pullback-wr-baseline/764bd2b5d0ff949c17e60f0f18c9471dcb495eeb7d4240f44eb803fee79dd848.snapshot.json`,
  file SHA-256 `ca126edf2a50e0efa04b9d359149cffc849f4268e632a2a53b99b2bc917324bd`.
- Result:
  `results/fxi-atr-band-mean-reversion--pullback-wr-baseline/20260817_015408_555159_offline_5406a64c71084145b4793fe1c9c918cf.json`,
  SHA-256 `028350a69fd2e84060eeaeaf0235fd22b5ef67f09da2037a110778b1cce7e553`.
- Trial-registry observation ID: `fdf6907fa49d44d5aaddb4cf9d99be60`, observed at
  `2026-08-17T01:54:08.578796Z`.

Exact robustness evidence:

- ATR floor manifest/result SHA-256:
  `0ceb0dd9d69361ca815453bae54943f50277982a4deb132694792369040088a0` /
  `a8aa69c81a2352249b162c441380e069db5db5edb4a10b46856fe80352d2c589`;
  observation `81e1a5ec1ed14c0e9e05869d571a9171`.
- ATR ceiling manifest/result SHA-256:
  `1072b05a20a69be59d64fc2fb064869ef80389fb438e680ec7ec3d0bcc3516ce` /
  `3f5213fd11d9178c8305e2fbfe1c4498895fa7395db45d6ec02399a1f8e92184`;
  observation `247c10a7435d48cb8c31d51c071247c0`.
- Hold-18 manifest/result SHA-256:
  `df817d04ff9378224f844df491d437670fdb3c43e153bb449c2228064bc87947` /
  `3dcbc154805461ca82f24c3bda9fe9e77e5272047c9cc6a85fe5fd40585ed9c9`;
  observation `b2dcea3664b842d997a6ecf41cbd39c5`.
- Delayed-entry manifest/result SHA-256:
  `722fc1af999ac4004ac7914dbfe3dbd465f7963476bcbb2a5beb7b6cff8c3242` /
  `3929e073fb6dd5eaba4cc439f04a00863ca861efbc86cf238472e4a4fd3e9b94`;
  observation `d60131a951514e71b6d76df07ebb45db`.

### Frozen Development eligibility result

The sole selection candidate fails the preregistered eligibility conjunction because it completed
14 trades, below the minimum of 20. It otherwise traded all five Development years, had positive
base and stress return, base profit factor above 1.1, stress profit factor above 1.0, stress
maximum drawdown within 20%, and a valid complete-family observation inventory.

No eligible candidate is selected. No `CANDIDATE_FREEZE.json`, qualification plan, qualification
screen, Evaluation snapshot, Evaluation result, or terminal conclusion was created. The operator
does not assign a terminal outcome; the released workflow reserves that judgment for independent
review after exact Development-gate and current-head qualification-absence evidence are prepared.

## Deviations and missing evidence

- A first full-refresh snapshot attempt at Development cutoff `2019-12-31` was rejected before
  provider access because the active cache cutoff was `2025-12-31`; no manifest or formal
  observation was created.
- A reuse attempt was then rejected because the active generation cutoff did not exactly equal the
  Development decision session; no manifest or formal observation was created.
- To preserve both cache monotonicity and the exact Development cutoff, the three exact FXI cache
  files for the 2025 generation were moved to a temporary directory, the maintained CLI created a
  separate full-refresh generation through `2019-12-31`, the remaining definitions reused that
  generation, and an exit trap restored the original files. A final `trading data status FXI`
  confirmed the original `2025-12-31` cutoff, full-refresh timestamp
  `2026-08-13T03:41:20.659745Z`, and checksum
  `d050c3ccaaf98a4b420c11b078c7622fa6f63e491168092463bae3c6b9cfdd9e`.
- The sandboxed provider call failed DNS resolution and produced no data or artifact. The identical
  maintained-CLI operation was retried with approved network access and succeeded. This is an
  operational recovery, not an outcome-relevant plan change.
- Development-gate evidence was prepared at
  `results/study-evidence/fxi-atr-band-mean-reversion-study-time-retrospective--s001/development-gate.json`,
  SHA-256 `c247a6e6807be7dae930e0287ef2df2c99939b20252db6ff620a4d7ed46605e3`.
- The current authoritative qualification registry had no plan or screen for this study. Its
  canonical absence snapshot is
  `results/qualification-evidence/7ce55dc19227a6093b28ad5236e129d01df2d33029b138423a45eb442d15e8fe.json`,
  with matching content identity
  `7ce55dc19227a6093b28ad5236e129d01df2d33029b138423a45eb442d15e8fe`.
- `TERMINAL_EVIDENCE.json` links the frozen study, Development gate, and current-head absence
  snapshot; SHA-256
  `a90846627cf90d106e2846caecef9ae52b44728cfc635477543367bb2fb19275`.
  The terminal validator accepted it with `require_current_registry=true`. These canonical
  artifacts must be added to the Git index before completion can pass fresh-clone retention
  checks. `CONCLUSION.md` remains untouched.
