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

## Deviations and missing evidence

- No outcome-relevant or semantic deviation occurred.
- The first provider-free recapture diagnostic referenced the snapshot digest at the wrong object
  level and raised `AttributeError`; correcting the inspection to `snapshot.blob.digest` produced
  the exact captures above. It wrote no artifact and accessed no outcome.
- Market-data refresh, market-data snapshots, manifests, formal observations, metrics, ranking,
  screen, retrospective disposition, and independent conclusion remain absent by authorization
  boundary.
