# Evidence: FXI ATR-Band Mean-Reversion Retrospective Confirmation

## Execution record

### Authority and lifecycle

The human owner had already established the stable identity `ochowei@gmail.com` for this study and,
immediately after preregistration, explicitly approved the next stated action: preparation and
approval of the new v006 candidate freeze. The guarded workflow CLI moved v006/S001 from
`preregistered` to `running` under researcher identity
`codex-primary-researcher-fxi-mean-reversion`.

The authorization covered only provider-free definition capture and the candidate-family freeze.
It did not authorize market-data refresh, a market-data snapshot, qualification-plan registration,
formal execution, a retrospective screen, outcome inspection, Shadow, broker access, or orders.

### Definition capture and trial-family freeze

All six preregistered workflow-native definitions were recaptured provider-free against
`strategy-forward-replication-research@v006` and composite policy set
`cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`.
The semantic fingerprints exactly match the preregistered family; the new content-addressed
definition snapshot IDs differ from the v005 lineage snapshots because they capture the current
exact Git/source context. Provider-free definition and policy tests passed: `12 passed`.

The append-only trial registry contains exactly six family trials, each with status `registered`
and zero observations. Its SHA-256 is
`beabc8dfc2ee33e0e628760d8b111bc4ab0a4507e02ef571e01e0a77dc50973a`.

The approved freeze is `CANDIDATE_FREEZE.json`. It pins the v006 preregistration, workflow release,
exact workflow definition, source Git HEAD, v005/S001 and v004/S004 lineage without importing prior
approval, selected candidate, distinct baseline, complete six-trial family, new definition snapshot
IDs, policy set, retrospective boundary, and explicit no-outcome authorization scope.

### Retrospective qualification-plan registration

Human owner `ochowei@gmail.com` explicitly approved registration of the frozen retrospective
qualification plan while prohibiting refresh and outcome-relevant work. The production CLI
registered exactly one plan at current UTC time without market-data provider access:

- plan ID:
  `retrospective-plan-cd1888d05e1f5ff1274d433d0559bb9d506995938511f54c90053e2e7eff3fb1`;
- created at: `2026-08-13T11:20:25.602613Z`;
- local append-only event ID:
  `historical-plan:retrospective-plan-cd1888d05e1f5ff1274d433d0559bb9d506995938511f54c90053e2e7eff3fb1`;
- event hash: `d548b5fb4f39546920113d7a63aec3c051f325db6cb6a3598104e9b73e141411`;
- local registry path: `state/qualification-registry.json`; its one-event post-registration
  SHA-256 was `00ab9180531b37dc6eaa84bc7095fa41936bdedd92c51d8faa9ac7e6497fcb3a`.

The plan binds selected trial
`697276adf91be9547c38d9197277c97b2c6fdfdb97b2d4c4975e2f325632e674`,
distinct baseline trial
`c3c04fd0bcb59ca8ecb250d8fd37e1ed68caa13233c1656d1be3381254918e8c`,
all six frozen family trials, semantic definition fingerprint
`6aa709255f84591960793dc744cbdfaaf3d6652ef9287581a89ace4765521456`,
`retrospective-confirmatory`, `provenance-unknown`, and a current-time
`retrospective_selection_checkpoint` that records prior selection history as incomplete.

The explicit role calendar was verified programmatically after persistence:

| Role | Sessions | First | Last |
| --- | ---: | --- | --- |
| Development context | 2,766 | 2015-01-02 | 2025-12-31 |
| Warmup only | 252 | 2009-01-02 | 2009-12-31 |
| Retrospective Evaluation | 1,258 | 2010-01-04 | 2014-12-31 |

Each inventory is chronological and unique; all three are pairwise disjoint. Development covers
the eleven complete consecutive years 2015-2025, warmup covers 2009 and ends before Evaluation,
and Evaluation contains five complete annual XNYS folds for 2010-2014. The plan freezes holding
20, execution lag 1, dependency 21, embargo 1, stress drawdown limit 20%, random seed `20260813`,
1,000 random samples, 1,000 bootstrap repetitions, and 20-session blocks. Focused qualification,
workflow, CLI, registry, and result-schema verification passed: `55 passed`.

### Authorized retrospective refresh and snapshots

Human owner `ochowei@gmail.com` explicitly authorized the frozen retrospective outcome-relevant
stage: one 2014-12-31-cutoff full refresh, snapshots for exactly the six frozen trials, formal
offline runs, and the qualification screen. The authorization prohibited tuning, reranking, and
expanding the trial family.

The first candidate snapshot invocation stopped before provider refresh or artifact publication
because the active cache generation had a later cutoff:

```text
research error: refresh cutoff 2014-12-31 precedes active cache cutoff 2025-12-31
```

The existing 2025 cache was preserved without deletion. It was moved aside, one actual full
refresh was performed for the selected candidate, and the other five snapshots used
`--reuse-full-refresh` without provider access. The resulting 2014 cache was retained separately
as `.cache/market-data-v006-s001-2014`, and the original 2025 cache was restored as the active
cache. This cache handling changed no tracked source, definition, plan, trial, or result.

All six verified manifests bind the same primary FXI data blob
`421b8f092b9400b79b13b71e6eadb1a4df12ef1f6def7ae724e6b0b3041ecb58`, 2,576 rows,
history start 2009-01-02, cutoff 2014-12-31, and full-refresh timestamp
`2026-08-14T02:15:19.712040Z`. The candidate manifest binds definition snapshot
`1eabd5db7c761d44744d8348ce439768eeef4b5ea993bffba4775b5743c42d90` and the frozen semantic
fingerprint `6aa709255f84591960793dc744cbdfaaf3d6652ef9287581a89ace4765521456`.

The production snapshot commands used the exact identities below; only the first command accessed
the provider after the earlier fail-closed cache diagnostic:

```text
uv run trading research snapshot fxi-atr-band-mean-reversion-retrospective/atr-band-candidate --workflow workflows/strategy-forward-replication-research--v006 --decision 2014-12-31
uv run trading research snapshot fxi-atr-band-mean-reversion-retrospective/atr-ceiling-1p30-robustness --workflow workflows/strategy-forward-replication-research--v006 --decision 2014-12-31 --reuse-full-refresh
uv run trading research snapshot fxi-atr-band-mean-reversion-retrospective/atr-floor-1p10-robustness --workflow workflows/strategy-forward-replication-research--v006 --decision 2014-12-31 --reuse-full-refresh
uv run trading research snapshot fxi-atr-band-mean-reversion-retrospective/delay-one-session-robustness --workflow workflows/strategy-forward-replication-research--v006 --decision 2014-12-31 --reuse-full-refresh
uv run trading research snapshot fxi-atr-band-mean-reversion-retrospective/hold-18-robustness --workflow workflows/strategy-forward-replication-research--v006 --decision 2014-12-31 --reuse-full-refresh
uv run trading research snapshot fxi-atr-band-mean-reversion-retrospective/pullback-wr-baseline --workflow workflows/strategy-forward-replication-research--v006 --decision 2014-12-31 --reuse-full-refresh
```

The candidate's v006 freeze was created before the canonical merge at Git HEAD
`41935feee33a11bab7622669bd160dbb458f6ddf` and recorded definition snapshot
`f31701169b32bfe2cee41770e01eb9e889b0e673c7b8533a386e7250b3b259ab`. The execution-time
recapture is `1eabd5db7c761d44744d8348ce439768eeef4b5ea993bffba4775b5743c42d90` at Git HEAD
`fe31dbe6dca33e9eb90be922f7399afc2510a2e6`. A provider-free comparison of the decoded
definition payloads after removing only `.git_context` produced the same SHA-256
`09783833f8fd9f735be8e7211bf9bcf4d5858318a2b8d0c73d650e708ccbd3e4`; the semantic fingerprint
also remained exact. This is Git-context provenance movement, not semantic definition drift.

### Formal offline observations

Exactly six formal offline runs completed successfully. Each result is valid, binds Git HEAD
`fe31dbe6dca33e9eb90be922f7399afc2510a2e6`, v006 release SHA-256
`f58d60322e8a975c7d2c73bcf22fbe947f31806d35cbc5d363b593e0036e0a10`, workflow SHA-256
`6b786b506d49a3e02dd88b63171e3697f74be1084ece2764d8c0123dafe78af8`, policy-set identity
`cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`, canonical argv, and
content-addressed maintained orchestration bytes.

Every result embeds its exact canonical `trading research run IDENTITY --workflow ... --manifest
... --offline` argv in `metadata.observation_provenance.canonical_argv`; the immutable paths and
hashes are listed below.

| Frozen trial | Trial ID | Snapshot ID | Manifest SHA-256 | Result file | Result SHA-256 | Observation ID |
| --- | --- | --- | --- | --- | --- | --- |
| `atr-band-candidate` | `697276adf91be9547c38d9197277c97b2c6fdfdb97b2d4c4975e2f325632e674` | `ef53df95e92f2f862f0985dce2916239cfcf0947849a57af7a074b85c7666d93` | `5cf62b5cfe2477df8249658f7af34aaaaaea7bb670a283c12a9e1d2c0687639b` | `results/fxi-atr-band-mean-reversion-retrospective--atr-band-candidate/20260814_021641_365555_offline_df8279f1117246b8b7a4a8c4ddf0a474.json` | `1f84237071851d7300cf73e1d8607548897f6123c70d07937f0f5d3db13ca8cc` | `97578a8d98a944b8a02a2238bad16cdf` |
| `atr-ceiling-1p30-robustness` | `059dc99759003284f0df05cbf092c6464eaa6128a0e5468150b169fc8e95b603` | `d5e6025bc4f5436401c3a6e67a1395ab9cdbfc749ac8726b993b3a798088e764` | `48dcfd5ad416e8a3d1c18a8dcc91d4aa1d1b32deb600f43a8e40c38f7a187b98` | `results/fxi-atr-band-mean-reversion-retrospective--atr-ceiling-1p30-robustness/20260814_021658_385324_offline_38d5713019244efdae2201f1d039f4cd.json` | `fb61c251c1b00dcd28a3a83e462d3221f0da3cce4ec2ba35540f0957ea7f4e32` | `1dbf4d48b74d4088a7ec92e795db960e` |
| `atr-floor-1p10-robustness` | `fac88cfbaf5068fff2795699fd7f3be10534bcec95c6c0d7f03b3aab91e99ba9` | `73f57dfcc86411b43c4fc7c3efe02d5ab2b8952c0690a8573d9064803e8eb192` | `341ebf42d2e2ce0bec282f0b5ef0e9fcaf78f82fa9df2a6875b5b56e930e8170` | `results/fxi-atr-band-mean-reversion-retrospective--atr-floor-1p10-robustness/20260814_021659_749793_offline_b2b6ad056ba1465f97959b12877724bb.json` | `ea497ad3a5d1adb06adefbc9f587b3a2be1f34d5856895e21192a2854cdd28d7` | `883fe36f603d4cd09dd90719ed178066` |
| `delay-one-session-robustness` | `651f6fa0a12c88b6d45a0ec6b55d917a5a239f38ac1371da9a67e9fe3b71a504` | `88becb5be9a90a6dd84ebeb1b7a0933bf844490b391450d87f8661accbf05fcd` | `4445cfd9c0daa3ff15f437f452ddb9eac65face85ddf2639822ca23d0ff4b9b3` | `results/fxi-atr-band-mean-reversion-retrospective--delay-one-session-robustness/20260814_021701_100395_offline_b2a4709ff078428dab5f1e256cade822.json` | `28a42fd8d7726f4f58556346c7cd501836250540cba416678bebb26dcdae3dd6` | `54c971d680024085a097856e1d37d9bd` |
| `hold-18-robustness` | `ac5b1d5ec5e4db18d69a1a743449d69888a00d4c4c6fc6b57e0230fbfe04f145` | `43e6fea51e9f86d62f7ab8f9219012293d8bf138584f7b9eb4d789064178694e` | `0f4336949ba4487c858c2f05b3e8d7bbb1d8225f7891006d016fb9dd217a6f22` | `results/fxi-atr-band-mean-reversion-retrospective--hold-18-robustness/20260814_021702_466119_offline_38a34532bf2b49f796050ef5d37cd495.json` | `5702c407e4bd4b5947342a5913c11ffd45f4aed4a3d83747d0b3b9e240486328` | `1cc9508e777a48cdbd8d06dced9c7a7b` |
| `pullback-wr-baseline` | `c3c04fd0bcb59ca8ecb250d8fd37e1ed68caa13233c1656d1be3381254918e8c` | `37232c8733a42f5a6343a27c78833f7c551e5595a729d4a048720be10de0fdcb` | `cf95ae3f1c3ed320a7de0557f70e27a728ac74ebc4f69de81d4d97ef9600a66a` | `results/fxi-atr-band-mean-reversion-retrospective--pullback-wr-baseline/20260814_021703_870965_offline_816aa70566254c4fa00891f6bb71fb25.json` | `445efb6808e1ec14aa60296c01ae9b3d6aa5fd70fb3dad7119d91cdf226b29fe` | `cf0cfa0facac4093b1bf7ad1da6ac6c3` |

The append-only trial registry now has SHA-256
`bea263875fe42c4453bf3858bff2a8a837883622558fa03d4d68fa57c32d5db1`. The frozen family remains
exactly six trials; each has exactly one succeeded, valid, offline observation. No tuning,
reranking, baseline replacement, or seventh trial occurred.

### Qualification screen terminal result

The guarded screen was invoked with plan
`retrospective-plan-cd1888d05e1f5ff1274d433d0559bb9d506995938511f54c90053e2e7eff3fb1`, the exact v006
workflow path, and one `IDENTITY=MANIFEST` binding for every frozen trial above. It stopped before
screen computation or registry append with:

```text
uv run trading qualification screen run --plan-id retrospective-plan-cd1888d05e1f5ff1274d433d0559bb9d506995938511f54c90053e2e7eff3fb1 --workflow workflows/strategy-forward-replication-research--v006 --trial fxi-atr-band-mean-reversion-retrospective/atr-band-candidate=results/fxi-atr-band-mean-reversion-retrospective--atr-band-candidate/ef53df95e92f2f862f0985dce2916239cfcf0947849a57af7a074b85c7666d93.snapshot.json --trial fxi-atr-band-mean-reversion-retrospective/atr-ceiling-1p30-robustness=results/fxi-atr-band-mean-reversion-retrospective--atr-ceiling-1p30-robustness/d5e6025bc4f5436401c3a6e67a1395ab9cdbfc749ac8726b993b3a798088e764.snapshot.json --trial fxi-atr-band-mean-reversion-retrospective/atr-floor-1p10-robustness=results/fxi-atr-band-mean-reversion-retrospective--atr-floor-1p10-robustness/73f57dfcc86411b43c4fc7c3efe02d5ab2b8952c0690a8573d9064803e8eb192.snapshot.json --trial fxi-atr-band-mean-reversion-retrospective/delay-one-session-robustness=results/fxi-atr-band-mean-reversion-retrospective--delay-one-session-robustness/88becb5be9a90a6dd84ebeb1b7a0933bf844490b391450d87f8661accbf05fcd.snapshot.json --trial fxi-atr-band-mean-reversion-retrospective/hold-18-robustness=results/fxi-atr-band-mean-reversion-retrospective--hold-18-robustness/43e6fea51e9f86d62f7ab8f9219012293d8bf138584f7b9eb4d789064178694e.snapshot.json --trial fxi-atr-band-mean-reversion-retrospective/pullback-wr-baseline=results/fxi-atr-band-mean-reversion-retrospective--pullback-wr-baseline/37232c8733a42f5a6343a27c78833f7c551e5595a729d4a048720be10de0fdcb.snapshot.json
```

```text
qualification error: selection adjustment rejects incomplete trial registry history
```

The qualification registry still contains exactly the original `historical_plan` event and has
unchanged SHA-256 `00ab9180531b37dc6eaa84bc7095fa41936bdedd92c51d8faa9ac7e6497fcb3a`;
there is no `historical_screen` event or partial disposition.

Read-only diagnosis found a frozen verifier incompatibility. The registered v006 plan correctly
contains `retrospective_selection_checkpoint`, `prior_selection_history_incomplete=true`, the exact
six included trial IDs, and the selected trial. The pinned selection-adjustment implementation in
`src/trading/core/qualification.py` checks incomplete history only against
`forward_selection_epoch` and does not consume the retrospective checkpoint. Its current SHA-256
is still the preregistered `bd3f820b42e1ce34cf6efa681e54b5f34d8be1014c7a04584b06d7d9d2b75762`.

No source repair or second screen was attempted. Once the 2010-2014 results had been exposed,
changing this PLAN-pinned outcome-relevant verifier and rerunning would create source drift after
outcome inspection. The frozen stopping rule therefore requires fail-closed handling for
qualification-plan incompatibility. The operator records this as the terminal execution result
without deciding the study outcome; independent review must assess the evidence under the frozen
`indeterminate` rule.

## Deviations and missing evidence

- No strategy, family, parameter, baseline, data-role, threshold, seed, challenge, outcome-rule,
  or semantic-definition deviation occurred.
- The first provider-free recapture diagnostic referenced the snapshot digest at the wrong object
  level and raised `AttributeError`; correcting the inspection to `snapshot.blob.digest` produced
  the exact captures above. It wrote no artifact and accessed no outcome.
- The first candidate snapshot attempt was blocked by the monotonic active-cache cutoff before
  provider access or artifact creation. The preserved-cache procedure then produced the one
  authorized full refresh and six manifests.
- Six formal observations are present. The required qualification screen and retrospective
  disposition are absent because the pinned verifier rejected the registered retrospective
  checkpoint before computation or append. No partial ranking, manual gate result, or replacement
  evidence was created.
- Independent conclusion remains absent and `CONCLUSION.md` is unchanged.
