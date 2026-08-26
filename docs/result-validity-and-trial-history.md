# Result validity and trial history

> **Retirement notice (2026-08-26):** Legacy experiment execution, refresh, ranking, registry seed,
> and result publication are retired. All final retained legacy results now live under
> `legacy/results/` as read-only diagnostics. The schema and historical rules below remain useful
> for interpreting archived bytes, but they do not authorize new legacy research. See
> [legacy-experiment-retirement-v010.md](legacy-experiment-retirement-v010.md).

Phase 3 adds a result contract on top of the immutable data and research-definition evidence
introduced in Phase 2. A result records one execution/observation of a registered trial; it is not evidence merely
because a JSON file exists.

## Result schema

Schema version 3 preserves the existing Part A / Part B / Part C payload and adds explicit
reproducibility fields:

- `validity`: recomputed status and reasons;
- `data_snapshot_id`, `data_snapshot_manifest`, and `data_cutoff`;
- `definition_snapshot_id` and semantic `definition_fingerprint`;
- `development_summary`, `historical_stability_folds`, `shadow_evidence`, and `live_evidence`;
- `legacy_period_results`, which keeps older Part A / Part B / Part C names available to readers.
- `canonical_sleeve_evidence`, containing separate raw signals and raw candidates,
  gross/base-net/stress-net daily equity, cost policies, metrics, and signal/trade parity.
- workflow-native formal results also carry `metadata.observation_provenance`: canonical argv,
  working directory, exact workflow release/definition and composite policy-set identities,
  complete Git HEAD, and content-addressed exact orchestration source bytes. This field is produced
  by the workflow-native CLI boundary; legacy and ordinary experiment results are not assigned
  synthetic workflow provenance.

The current statuses are:

| Status | Meaning | Qualifiable for ranking? |
| --- | --- | --- |
| `valid` | Complete result, verified snapshot, and current semantic definition | Yes |
| `data-stale` | The referenced snapshot is older than the latest completed session | No |
| `definition-stale` | The result’s semantic definition fingerprint is not current | No |
| `unreproducible` | Evidence is missing, corrupt, inconsistent, or the result is incomplete | No |
| `legacy` | Old result or schema-v2 result without canonical sleeve evidence | No |
| `migration-pending` | Fresh migration-mode evidence awaiting separate requalification | No |

Validity is derived read-only from the result and its referenced immutable manifest. A missing or
corrupt snapshot is never silently refreshed, and an old result is never given a synthetic
snapshot identity. Legacy files remain readable for diagnostics and migration, but cannot be
promoted to `valid` without a new formal execution. A schema-v3 result is `unreproducible` when the
current experiment definition cannot be resolved; absence of a comparison identity never fails
open.

The semantic definition fingerprint intentionally ignores comments, formatting, and only those
reporting-only symbols explicitly declared by the experiment at definition capture. Names such as
`render_*` or `format_report` are not trusted implicitly. Exact source and the declaration are still
retained in the definition blob. A declaration is applied only when the symbol is unambiguous and
is not referenced by retained outcome code; uncertain dependencies remain part of the fingerprint.
Changes to thresholds, signal logic, execution rules,
dependencies, or other behavior-affecting code produce a new fingerprint and invalidate only the
affected definition lineage.

## Retired publication and latest-result rules

Before terminal retirement, `ResearchRunCoordinator` applied these boundaries:

- a successful formal `online` run wrote a schema-v3 historical result and atomically advanced
  the now-archived `<experiment>/latest.json`;
- a successful formal `offline` run writes only a historical result;
- a successful formal `migration` run requires passing fixed-snapshot parity and writes only an
  immutable `<snapshot_id>.migration-result.json` envelope marked `migration-pending`;
- `ephemeral` runs do not write result files or trial-registry observations;
- failed, partial, and failed-publication formal attempts are retained as failed trial
  observations, while incomplete results are never published as successful results;
- the legacy `--legacy` path writes historical legacy evidence only and never advances
  `latest.json`.

There is no writable or authorization-capable legacy result root. `legacy/results/` is read-only;
comparison, an explicit result-status query, and `result status --all` may inspect it. Freshness,
evaluation/ranking, followup new entries, Shadow/Active, qualification, and formal evidence
verification never use archived results.

`latest.json` is therefore a convenience pointer, not a qualification decision. Ranking and
follow-up selection use only complete, successful, current-definition, current-data results.
The coordinator generates canonical evidence from the runner's typed raw input and verifies its
engine and cost policies against the exact frozen definition before publication.
For workflow-native execution, the CLI supplies observation provenance before the runner is
invoked, and the coordinator defensively copies it into the persisted historical result. The
historical result file remains local-only unless repository policy explicitly retains it; tracked
snapshot manifests, trial-registry observations, and study evidence refer to its exact path and
SHA-256 identity instead of copying mutable result content into the workflow directory.
Validity also recomputes every scenario's metrics from its persisted daily-equity ledger; a changed
Sharpe, return, volatility, or drawdown without the matching path is unreproducible.
The coordinator records a successful formal observation before advancing `latest.json`; a registry
failure leaves the previous latest pointer unchanged. Formal execution also requires the current
exact definition reference to match the manifest, while read-only validity compares semantic
fingerprints so reporting-only exact changes do not invalidate historical outcomes.
If advancing `latest.json` fails after a complete execution, the reproducible historical result and
its successful execution observation remain audit evidence, and a separate failed-publication
observation is appended; the previous latest pointer remains unchanged.

## Read-only diagnostics and evaluation

Use these commands to inspect validity without refreshing data or writing result state:

```bash
uv run trading result status <experiment_name>
uv run trading result status --all
uv run trading compare <experiment_a> <experiment_b>
uv run trading freshness
```

Explicit asset evaluation fully refreshes every retained data declaration, publishes a new snapshot
with the current exact definition and latest completed decision session, and reruns every stale
candidate before ranking. If any candidate cannot
be refreshed, is legacy/unreproducible, or remains stale, the evaluation exits without a partial
ranking. The current Phase 3 CLI can refresh only experiments that already expose the Phase 2
snapshot-aware seams and have a prepared manifest; it does not migrate the existing detector
batch in place.

Complete candidate ranking uses the canonical base-net daily-equity Sharpe. Schema-v2 and legacy
Part B metrics remain inspectable but cannot act as a ranking fallback. The execution contract is
documented in [canonical-sleeve-execution.md](canonical-sleeve-execution.md).

The repository's followup-ranking and experiment-documentation workflows invoke the same read-only
status gate before consuming metrics. Any non-`valid` candidate blocks complete followup ranking,
and stale, legacy, or unreproducible results cannot update experiment documentation.

Phase 6 projects its verified local lifecycle registry into `development_summary`,
`historical_stability_folds`, and `shadow_evidence` without changing schema version 3. Validity
rejects incomplete fold records, plan/fold identity mismatches, definition changes inside Shadow,
historical evidence claiming Active status, Shadow registration without all historical gates,
incomplete qualification policies or prospective metrics, cost-policy or lineage conflicts, any
non-empty Phase 6 live evidence, and any Shadow payload claiming authorization for live orders.
The qualification lifecycle is documented in
[historical-qualification-and-shadow.md](historical-qualification-and-shadow.md).

```bash
# retired: uv run trading result evaluate SPY
```

## Append-only trial registry

`results/registries/trial_registry.json` is an append-only, atomically updated registry. A formal
trial is
identified by the pair `(experiment_family, semantic_definition_fingerprint)`, so repeated runs
of the same definition add observations while a new semantic fingerprint starts a new trial.
Snapshot-aware experiments must declare their stable family and optional hypothesis with
`declare_experiment_trial`; the experiment package name is not used as an implicit family.
Observations retain snapshot identity, result path, run mode, outcome, validity, and failure
reason. Removal is represented by a tombstone; failed trials and deleted result files are not
forgotten.

`ExperimentTrialRegistry.has_valid_observation()` is the requalification boundary used by the
followup Shadow/Active verifiers. It accepts only a successful formal `online` or `offline`
observation marked `valid`; the migration envelope's `migration-pending` observation never counts.

The registry uses a lock file and atomic replacement. Malformed or conflicting state fails closed.
Legacy entries can be explicitly seeded for discoverable pre-Phase-3 experiments:

```bash
# retired: uv run trading result registry seed
```

Seeded legacy entries are marked with incomplete selection history. They are migration inventory,
not qualification evidence, and are not silently merged into formal trials.
