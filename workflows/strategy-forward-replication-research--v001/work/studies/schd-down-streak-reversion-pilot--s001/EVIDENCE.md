# Evidence: SCHD Down-Streak Mean-Reversion Governance Pilot

## Execution record

### Governance and preregistration

- Study identity: `strategy-forward-replication-research@v001/S001`.
- Execution agent: `codex-primary-execution-agent`; human owner and approver:
  `ochowei@gmail.com`.
- Base repository commit: `7edc3a258e2aa45d17d4ded64b1dd094b5229678` (complete SHA).
- Workflow release: `strategy-forward-replication-research@v001`; `RELEASE.json` SHA-256
  `db463628c6174934b4e342031466afce9d543a18e4af5b9c0b6cfe8e604b8896`.
- Composite policy-set identity:
  `4ade828a43e2cfab97b2933c5722107cf00ccf27c3a90c92b60c19b67f511189`.
- Policy release identities and `RELEASE.json` SHA-256 values:
  `us-equity-market@v001` / `7df1e266aa72ccfaca3efa3e490ad6234f300bb0bfc4e31b3dd3c85ab93de542`;
  `firstrade-manual-trading@v001` / `0b40404f668dc1bfb15e21558bbdc221f68742093d0ecc99856be9f0031470d9`;
  `canonical-execution@v001` / `e6a745aeb4d7bdbad6ed53f25ff5a41fed0a447200edf51b545c7163d5d50925`;
  `portfolio-risk@v001` / `63e565e6eebbfe55dc9ffb4914af28706d6164a029447fcc52f8825d5da57b69`.
- Preregistration artifact: `PREREGISTRATION.json`, SHA-256
  `5ac178bc3c5f1f33dab1a887dcf74a417ba0d6d6a9e1b0b65d738c44fb2d54ba`;
  frozen hypothesis SHA-256 `ac3fa9d662558d46edad1d74a706f701903cf2ff8f012bab9d6fe7106d240471`;
  frozen plan SHA-256 `dcba93005ba99a4a8d6c151f3863c876c86e444b967477bce8e9c5282d661e18`.
- Preregistered at `2026-08-12T06:01:06.205985Z` by `ochowei@gmail.com`; transitioned to
  `running` at `2026-08-12T06:01:06.798186Z` by `codex-primary-execution-agent`.
- The execution worktree was intentionally dirty because Phase 2 adds the workflow-native runtime,
  definitions, tests, documentation, study, and results without committing. The immutable Research
  Definition Snapshots below contain the exact outcome-relevant source bytes; the base commit above
  anchors all other tracked repository content. No `pm/` path changed.

Commands:

```text
uv run trading workflow study preregister workflows/strategy-forward-replication-research--v001/work/studies/schd-down-streak-reversion-pilot--s001 --approved-by ochowei@gmail.com
uv run trading workflow study transition workflows/strategy-forward-replication-research--v001/work/studies/schd-down-streak-reversion-pilot--s001 --to running --by codex-primary-execution-agent
```

### Authoritative Development observations

All three observations use the same immutable SCHD market-data blob SHA-256
`811661a1b18dde967c0d62140f282b6f7f754f642f9f7ad9cf0f707535b427e2` (3,570 rows,
308,894 bytes), cutoff `2025-12-31`.

- `schd-down-streak-reversion/two-down`: trial
  `efebe5117e35b66c23cabf2bc06d0e3ce10840c70c3115665689d2f92e7bfd48`, observation
  `37a55c03c02246beabe00bbda88d4716`, definition fingerprint
  `f7a1025baad00aa4f71e27f9d9a81f3a43eb1579299fdb5d0437cde3051fb18a`, definition blob
  `aa4e6de0466e26aec2fd5b34d4e4f5aeb52fb497100e6c013f005fa5cf415962`.
  Snapshot `f211c66533acdfd44cf769d4f30077a205d581fd84ab38527ffb96ee72e50b70` at
  `results/schd-down-streak-reversion--two-down/f211c66533acdfd44cf769d4f30077a205d581fd84ab38527ffb96ee72e50b70.snapshot.json`,
  manifest SHA-256 `ab3e837ddb8c45bc65d957fcce34138024aed5205c4a3dfff5a2b87d0b7fec82`.
  Result at
  `results/schd-down-streak-reversion--two-down/20260812_060714_213104_offline_e08466698ef04d418672bab3ab42036f.json`,
  SHA-256 `2f4f73a67c67b28a9da7e8384a6811f0cbf16b1b60f29bcd7dfaa6de1951e6b1`.
- `schd-down-streak-reversion/three-down`: trial
  `a8e4f39b2e405d27df8e947eb48feeb940d22d19a7b62783a67a8fdec2731a49`, observation
  `54ce44f5517545ffb2587565053f4eae`, definition fingerprint
  `feb06e3eb55c03f01cd32913b02fb07aad467061835c5134b3a81bf6209972a2`, definition blob
  `fc276bfa51b31df3520aede908aab4962d468ede3fe2471de9d95f07536f1dfc`.
  Snapshot `67f48f24898ea7f4ee50a5d759ac1c049ce2b24d7a6f0d82745946f411601d6b` at
  `results/schd-down-streak-reversion--three-down/67f48f24898ea7f4ee50a5d759ac1c049ce2b24d7a6f0d82745946f411601d6b.snapshot.json`,
  manifest SHA-256 `330b9986de1c5bb9875d969d756412d4d1e89f02595276bb696952572aa351f3`.
  Result at
  `results/schd-down-streak-reversion--three-down/20260812_060718_415505_offline_e6120109318a469f9db4bab87036899f.json`,
  SHA-256 `ac583c9d33b0cad3dbb12e92cbe45c1a5a4b5eca6ad9bfcbd99dd7f984fc5ab7`.
- `schd-down-streak-reversion/periodic-baseline`: trial
  `dace5b8f44c9e8e3d23a15261556486fcb664d9fe014dcb11bf3e38a20716517`, observation
  `974184e14ab4476ebab3c0f439c0d387`, definition fingerprint
  `7f2f4d0eb2c0e75157870feb761c7aeeab6d79dfc5af5251dece47fe75fb0d8b`, definition blob
  `405e37561be27d154390e947606a22f026f948ed14c48ffece08a756446382d8`.
  Snapshot `330dfe2f7ab607df51effd875a265ace65bf891d37334ccdb8ed1ee0c6ce2f62` at
  `results/schd-down-streak-reversion--periodic-baseline/330dfe2f7ab607df51effd875a265ace65bf891d37334ccdb8ed1ee0c6ce2f62.snapshot.json`,
  manifest SHA-256 `63b3c9223dd02b3af26875dab97a4a09402a0c4f5cbe89297309b21d5d79fda2`.
  Result at
  `results/schd-down-streak-reversion--periodic-baseline/20260812_060722_659029_offline_36cd1be1af8146a2bb73b7686b538c28.json`,
  SHA-256 `d5b11a9f483a816690a0ad2ee29926beb0e3d39bf144cde13919827537458212`.

Exact formal execution commands:

```text
uv run trading research run schd-down-streak-reversion/two-down --workflow workflows/strategy-forward-replication-research--v001 --manifest results/schd-down-streak-reversion--two-down/f211c66533acdfd44cf769d4f30077a205d581fd84ab38527ffb96ee72e50b70.snapshot.json --offline
uv run trading research run schd-down-streak-reversion/three-down --workflow workflows/strategy-forward-replication-research--v001 --manifest results/schd-down-streak-reversion--three-down/67f48f24898ea7f4ee50a5d759ac1c049ce2b24d7a6f0d82745946f411601d6b.snapshot.json --offline
uv run trading research run schd-down-streak-reversion/periodic-baseline --workflow workflows/strategy-forward-replication-research--v001 --manifest results/schd-down-streak-reversion--periodic-baseline/330dfe2f7ab607df51effd875a265ace65bf891d37334ccdb8ed1ee0c6ce2f62.snapshot.json --offline
```

The complete frozen gate calculation is
`results/schd-down-streak-reversion--development-gate/s001.json`, SHA-256
`a59c41e54769ff9f1f6d30f8c67f2658b48863f226656cbed6623c3e9997cc7e`. It records
Development `fail`: neither candidate is eligible and the monotonic claim fails. The frozen stopping
rule therefore prohibits materializing robustness-only trials or inspecting quarantine/Evaluation
outcomes. The retained trial-registry SHA-256 after all observations is
`4588ad31739b6ffec54f3d40d50de42c5a07e84dff37ad16392d315ebd65f69a`.

## Deviations and missing evidence

The initial three snapshot commands refreshed Yahoo independently. Although each had the same 3,570
sessions and cutoff, provider serialization differed by up to approximately `0.00001` dollars and
produced distinct data blobs: `eb4ce30d935580b94c2dde68f77d8e278973c742e91412cb6e17c2f087a66890`
for `two-down`, `8d157816e47bd0ba93fc6cb82d9e8ecb6d85cd556fec6a3d7b7dcd9a718a59cf`
for `three-down`, and `811661a1b18dde967c0d62140f282b6f7f754f642f9f7ad9cf0f707535b427e2`
for the baseline. Those observations remain visible in `results/trial_registry.json` but were not
ranked. Their result SHA-256 values are respectively
`63b7897e155e0fb2bff444d9aa66d1ee6e5a5895097d5efe7cb4348f68ade5ae`,
`3212fec7658071d9855dfc176654b7f33c685e6ec7cf97594df109919173a113`, and
`34cd48927d59b3bbd36cf8dba10ef201ca6df9a7a1ab13c502fda3f1dda59cef`.

This was repaired without changing any frozen semantics: all three definitions were recaptured from
the final full-refresh cache generation and rerun against the single shared immutable data blob
listed above. Each semantic fingerprint remained unchanged, so the repair added observations, not
trials; `maximum_trials=5` remains respected with three materialized trials.

Snapshot verification initially exposed an implementation defect: definition capture included the
composite `policy_set` in its semantic fingerprint, while the byte verifier omitted that field.
The maintained verifier now includes `policy_set`, and a capture-to-load regression test covers the
case. No released workflow or policy artifact was modified, so no workflow change record was
required. There is no missing evidence, broker interaction, order submission, live-trading
authorization, 2026 quarantine inspection, or 2027+ Evaluation inspection.
