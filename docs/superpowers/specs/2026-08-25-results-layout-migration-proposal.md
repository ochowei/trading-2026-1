# Results Layout Migration Proposal

## Summary

Physically reorganize the 134 tracked artifacts currently stored directly under `results/` into
purpose-owned subtrees while preserving every artifact byte and historical reference through one
tracked, append-only path-migration registry.

This is a repository-storage migration. It does not change any study hypothesis, plan, research
definition, market data, observation, metric, gate, outcome, or authority.

## Target layout

```text
results/
├── workflows/<workflow>--vNNN/<study>/<stage>/
├── research-trials/<family>/<trial>/
├── experiment-results/<experiment>/
├── migration-evidence/<experiment>/
├── evidence/{research,qualification}/
└── registries/{trial_registry.json,path-migrations.json}
```

Pure legacy historical run files that have no formal observation or workflow reference move to
`legacy/results/<experiment>/history/` instead of remaining in the canonical result store.

## Frozen migration inventory

The dry-run inventory contains 134 source artifacts and has no unmapped source or destination
collision:

| Destination class | Artifact count |
| --- | ---: |
| `results/research-trials/` | 71 |
| `results/experiment-results/` | 36 |
| `results/migration-evidence/` | 12 |
| `results/workflows/` | 7 |
| `results/evidence/` | 2 |
| `results/registries/` | 1 |
| `legacy/results/*/history/` | 5 |

The guarded migration writer must enumerate every individual source and destination in
`results/registries/path-migrations.json`. Each entry contains the old repository-relative path,
new repository-relative path, exact pre-migration SHA-256, artifact class, and migration version.
The registry is append-only, rejects duplicate old or new paths, rejects cycles and traversal,
and verifies destination bytes before the old path is removed.

## Compatibility and canonical resolution

Historical workflow and trial artifacts remain immutable. Callers resolving an exact frozen old
path must use the repository result-path resolver:

1. If the exact path exists, use it.
2. Otherwise resolve exactly one tracked migration entry.
3. Require the resolved destination to exist and match the frozen SHA-256.
4. Reject missing, conflicting, chained, cyclic, untracked, or digest-drifted mappings.

New writers publish only to the categorized target layout. Readers continue to accept explicit
manifest paths and use the resolver for historical paths. The migration registry never turns a
mutable `latest.json` into formal evidence and cannot substitute one artifact for another.

## Required implementation changes

- Add typed path-migration parsing, validation, and resolution under `src/trading/research_data/`.
- Route result, snapshot, migration, trial-registry, research-evidence, qualification-evidence,
  Development/challenge evidence, freshness, diagnostics, and GC paths through the categorized
  layout and compatibility resolver.
- Update CLI defaults and generated commands to emit categorized canonical paths.
- Preserve frozen workflow study files; do not rewrite completed or preregistered artifacts.
- Update architecture and reproducibility documentation plus repository ignore/retention rules.
- Add migration, resolver, writer, fresh-checkout, checksum-drift, cycle, collision, and historical
  study-validation tests.

## Validation and acceptance

The migration is acceptable only when:

- all 134 pre-migration SHA-256 values equal their post-migration destination bytes;
- no old tracked artifact remains outside the migration registry and no destination is duplicated;
- historical v001-v008 studies validate without modifying their frozen files;
- the paused v008/S003 study validates with the same preregistration, candidate freeze, plan,
  family, observation, and evidence identities;
- result diagnostics, formal snapshot verification, trial-registry replay, qualification evidence,
  workflow validation, Ruff, and the full relevant test suite pass; and
- a fresh-checkout-style verification can resolve every migrated historical path without private
  runtime state.

Release or study resumption requires separate authority after validation. This proposal does not
authorize either action.
