# Evidence: FXI Volume-Stratified ATR-Floor Mean-Reversion Study-Time Retrospective Evaluation

## Execution record

### Development authority and boundary

- The guarded transition to `running` created `DEVELOPMENT_AUTHORIZATION.json` at
  `2026-08-17T09:21:29.041266Z`, approved by `ochowei@gmail.com` and operated by
  `codex-primary-researcher-fxi-mean-reversion`.
- Authorization SHA-256:
  `ec61f9275d530003efd0f810553bb13adeb6f9ee251aee2cddeb7bf768069f1c`.
- Authorization scope was Development only. No Evaluation, volume challenge, Shadow, broker, or
  order authority was used.
- Execution Git HEAD: `54075ef47013d5bc13c88e25ab5519a5a0b43a6c`.
- Composite policy-set identity:
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`.
- Every formal snapshot used decision session and data cutoff `2019-12-31`; all six manifests
  reference data blob SHA-256
  `9edb4f9a48dbc8a70b2dc89131fa355a1ce51763179c5bbcb2bf7b303d50bbde`.
- The maintained `trading research run <identity> --manifest <path> --offline` path produced every
  formal observation. No 2021-2025 Evaluation result was generated or inspected.

### Complete six-member Development family

All six manifests passed maintained manifest verification. All six formal observations succeeded
with `validity_status=valid`. Profit factors below are recomputed from completed canonical-sleeve
net fills as total positive net P&L divided by absolute total negative net P&L.

| Identity | Trial ID | Snapshot / definition fingerprint | Completed trades / traded years | Base return / PF / Sharpe / MDD | Stress return / PF / MDD |
| --- | --- | --- | --- | --- | --- |
| `fxi-atr-floor-mean-reversion/atr-floor-candidate` | `0290ddaa50cdb3f0596aaa1a83c738356c232a1fc61280e7eb6d6a6723eaef10` | `39af03d9db7f6cbd1880bac25871343c0510de9cebdd8addd6850022ea980c76` / `37095d89d34c193191e019fbac20abc16358d17d55565002be31d1e1ae8ce143` | 15 / 2015-2019 | 21.2019% / 1.7354 / 0.4531 / -12.5988% | 15.5216% / 1.5131 / -13.0175% |
| `fxi-atr-floor-mean-reversion/pullback-wr-baseline` | `e1c657d8f9ecf042640040284030478279f5e2c5d1bfa3b726659d5fd1edfe03` | `15e3748880ec3180447b72a92e83fee8545a2e6bb0464ce9dc9ca540fc132184` / `57ea269dd3f2445ed5efcacfb354f45f708fbc85da5eef36440c5843b82ab4d1` | 33 / 2015-2019 | 24.0960% / 1.3500 / 0.4064 / -18.3596% | 11.6597% / 1.1665 / -21.8112% |
| `fxi-atr-floor-mean-reversion/s001-atr-band-reference` | `fd54b0c430d9755e091011763ae6393cb2e58ca47c0e26a03bd646c851ad82e0` | `263625bffeb0ac8016759f6cda87c0346e886ba93bb1e3570b9b412da2e227f6` / `5978f1355d8692e2265d1543fc8e5287f47f6385be07feee0d6d0cd9b0a4842a` | 14 / 2015-2019 | 13.9413% / 1.5049 / 0.3283 / -14.1298% | 8.9493% / 1.3086 / -16.2217% |
| `fxi-atr-floor-mean-reversion/atr-floor-1p10-robustness` | `e298485ac30ce421fdc9ed53b2620626a011282bc8d3b9450e532c477ecea9c0` | `d368a7f6873bf06c27bfa14a38845d4878625f918ac0031db702fc35d10586c9` / `4bacf4ca6024dd8bde71c0180fcf84e408f001997939159ac29869498c43ba8e` | 15 / 2015-2019 | 21.2019% / 1.7354 / 0.4606 / -10.6891% | 15.5216% / 1.5131 / -11.1250% |
| `fxi-atr-floor-mean-reversion/hold-18-robustness` | `8a112b7b7ad6cb8da011504f0fee12ffbd968c8ea9db37b3d8e1c3f948ccc7b3` | `be240abecb116c5c87b219e47837d8c9375b28372a2670fc9cb210ec9521b6b5` / `664ad39a0f7f4441f514fa80d3d8b9efcb4280f2520cfad10d56ec061f8532ee` | 15 / 2015-2019 | 16.4522% / 1.5266 / 0.3710 / -12.5988% | 10.9945% / 1.3377 / -13.0175% |
| `fxi-atr-floor-mean-reversion/delay-one-session-robustness` | `a613179d6fa6162dd6f890fdb923e174b9eb9cd07925b26cfba46565f5610f55` | `330d3f4da992eb1ae742a4e15c1ae1aae9f16eda353d3c2bd05e6079a3b4ef76` / `700143936579885229526bb40be55e71a95e4dbb96de2e7da0dbdaf1c0cbaaea` | 15 / 2015-2019 | 2.2535% / 1.0733 / 0.0947 / -19.0148% | -2.5388% / 0.9217 / -21.5653% |

Exact candidate evidence:

- Manifest:
  `results/fxi-atr-floor-mean-reversion--atr-floor-candidate/39af03d9db7f6cbd1880bac25871343c0510de9cebdd8addd6850022ea980c76.snapshot.json`,
  file SHA-256 `66542eac667abc4ce0b14196846255d28199f33e2931f07a8a7c6ada04b9435c`.
- Result:
  `results/fxi-atr-floor-mean-reversion--atr-floor-candidate/20260817_094507_541417_offline_d8ea8540298148089a9277eea13bee8d.json`,
  SHA-256 `42fae774719bc520d4b3eb7e8bdaabee9a817eef7c55aca75c8ac54d26720c4b`.
- Trial-registry observation ID: `b9a007c4fd424d1cb9683463b6af54ed`, observed at
  `2026-08-17T09:45:07.562242Z`.

Exact baseline evidence:

- Manifest:
  `results/fxi-atr-floor-mean-reversion--pullback-wr-baseline/15e3748880ec3180447b72a92e83fee8545a2e6bb0464ce9dc9ca540fc132184.snapshot.json`,
  file SHA-256 `e1c4304481f1ef9b85e5e845c4b3aef0839daa8626ca35298f18810770341603`.
- Result:
  `results/fxi-atr-floor-mean-reversion--pullback-wr-baseline/20260817_094509_090692_offline_e82b0953abdd49f78142d2d216abed9d.json`,
  SHA-256 `c6701ea7f9721804ed93baaeaf4ea8f7a069ad8f3e469ca1bfcd9291a2ca170f`.
- Trial-registry observation ID: `75c68c84cc74414bbc1ad3220c79c230`, observed at
  `2026-08-17T09:45:09.112130Z`.

Exact robustness evidence, in frozen family order:

- S001 ATR-band reference manifest/result SHA-256:
  `61e3ad72c86c65f5d9192717e5597926ef1ea5774c3bc242a5e27b32a7a39504` /
  `8c2c2a3689281f83e30e651ee308bce3a32a5e6fa9f23e0cc2f1b7fa7442e639`;
  observation `0cc6c36ac64144f3b4d1427ab73242ab`.
- ATR-floor 1.10 manifest/result SHA-256:
  `5f7ce500ff06a7433e8f4697aad8d89400b96f4bbbf25107be195cb2ef83d2d7` /
  `f05f17e5f68dd9bc8abd6035f252ee669eda6059102f4f8ddbdc39ec66ec2dc7`;
  observation `2e1e4565a878442c95717a4e712d2b81`.
- Hold-18 manifest/result SHA-256:
  `05ad4d0020baedd3af700a244d9c61d9ed5de96376f0ad63f5ba01713e64c15f` /
  `d5746d7b6faa0bbb179ca84ec60ad1ac889d3599b6458775a86f540a70a1091a`;
  observation `33f12fa143f54dbe8e2f5f02409cd6ee`.
- Delayed-entry manifest/result SHA-256:
  `24d35af1afca8f312c8ff21ed57804d289d7e372f0f63f1936be0605a728b07b` /
  `5ea5ccbab3e626fda86b7c79fc39fa4beab8c65736322d1a34bf3bb8c8b4bd4c`;
  observation `0a148b322c1e45bbb6f1ea56b03e381a`.

### Frozen Development eligibility result

The sole selection candidate fails the preregistered eligibility conjunction because it completed
15 trades, below the minimum of 20. It otherwise traded all five Development years, had positive
base and stress return, base profit factor above 1.1, stress profit factor above 1.0, stress
maximum drawdown within 20%, and a valid complete-family observation inventory. Removing the S001
ATR ceiling therefore added only one completed Development trade relative to the S001 reference's
14 and did not cure the preregistered sample-size failure.

No eligible candidate is selected. No `CANDIDATE_FREEZE.json`, qualification plan, qualification
screen, Evaluation snapshot, Evaluation result, volume-tercile challenge, or terminal conclusion
was created. The operator does not assign a terminal outcome; the released workflow reserves that
judgment for independent review after exact Development-gate and current-head
qualification-absence evidence are prepared.

## Deviations and missing evidence

- The sandboxed full-refresh provider call failed DNS resolution and produced no data, manifest, or
  formal observation. The identical maintained-CLI operation was retried with approved network
  access and succeeded. This was an operational recovery, not an outcome-relevant plan change.
- To preserve both cache monotonicity and the exact Development cutoff, the three exact FXI cache
  files for the active 2025 generation were moved to a temporary directory, the maintained CLI
  created a separate full-refresh generation through `2019-12-31`, the other five definitions
  reused that generation, and an exit trap restored the original files. A final active-cache check
  confirmed cutoff `2025-12-31`, full-refresh timestamp `2026-08-13T03:41:20.659745Z`, and checksum
  `d050c3ccaaf98a4b420c11b078c7622fa6f63e491168092463bae3c6b9cfdd9e`.
- Development-gate evidence is
  `results/study-evidence/fxi-volume-stratified-atr-floor-mean-reversion-study-time-retrospective--s002/development-gate.json`,
  SHA-256 `ece8bf26de64fe839628771b8cb008cc60067710ad672735ab383b1c8ac07da6`.
- The current authoritative qualification registry had no plan or screen for this study. Its
  canonical absence snapshot is
  `results/qualification-evidence/7ce55dc19227a6093b28ad5236e129d01df2d33029b138423a45eb442d15e8fe.json`,
  with matching content identity
  `7ce55dc19227a6093b28ad5236e129d01df2d33029b138423a45eb442d15e8fe`.
- `TERMINAL_EVIDENCE.json` links the frozen study, Development gate, and current-head absence
  snapshot; SHA-256
  `5651a04887e225f015103645b53d601516851b5ce5b15c97931dc64482779668`.
  `CONCLUSION.md` remains untouched.
