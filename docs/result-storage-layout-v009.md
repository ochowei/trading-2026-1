# Categorized Result Storage and Path Migration

## Scope

This document defines the canonical tracked result namespaces introduced for the v009 workflow
boundary. It changes repository storage and path resolution only. It does not change a research
definition, study design, observation, metric, gate, outcome, or authority.

For v009 and later, the destination paths and registry location in this document replace only the
superseded flat `results/` path literals in older normative dependencies. Every non-path rule in
those dependencies remains in force. Released v008 and earlier versions retain their original
dependency bytes and use the compatibility resolver for moved tracked artifacts.

## Canonical namespaces

New tracked writers publish only to these purpose-owned paths:

| Artifact class | Canonical path |
| --- | --- |
| Workflow-native trial artifact | `results/research-trials/<family>/<trial>/...` |
| Retained legacy experiment result | `results/experiment-results/<experiment>/...` |
| Parity-linked migration evidence | `results/migration-evidence/<experiment>/...` |
| Workflow study evidence | `results/workflows/<workflow>--vNNN/<study>/<stage>/...` |
| Pre-freeze research evidence | `results/evidence/research/<sha256>.md` |
| Qualification evidence snapshot | `results/evidence/qualification/<sha256>.json` |
| Shared tracked registry | `results/registries/<registry>.json` |

Pure historical legacy runs that have no formal observation, workflow reference, or canonical
latest responsibility belong under `legacy/results/<experiment>/history/`.

## Historical path compatibility

`results/registries/path-migrations.json` is the only compatibility authority for a tracked result
that moved from an exact historical repository-relative path. Each schema-1 entry records:

- the exact old and new repository-relative paths;
- the pre-migration SHA-256;
- the artifact class; and
- the migration version.

The registry is append-only. Validation rejects unsafe paths, duplicate old or new paths, mappings
whose source and destination are equal, chains, cycles, missing destinations, and destination bytes
whose digest differs from the recorded SHA-256.

A historical read follows this algorithm:

1. Use the exact requested path when it exists.
2. Otherwise require exactly one migration entry for that old path.
3. Resolve the entry directly to its one canonical destination.
4. Require the destination to exist and match the recorded digest.
5. Fail closed on every other condition.

Callers may not use basename search, directory aliases, mutable `latest` pointers, or caller-supplied
substitutions to repair a frozen path. Released workflow and frozen study files are never rewritten
just because a referenced artifact moved.

## Publication and retention

The migration writer must verify every source digest, publish or move the byte-identical
destination, verify it again, append the complete mapping registry atomically, and only then remove
the old source. The operation rejects partial inventories and destination collisions. A retry is
valid only when the destination bytes and existing registry entry exactly match the requested
mapping.

Garbage collection treats migration entries and their destinations as references. Fresh-checkout
validation must resolve every migrated historical path using only tracked repository state. New
writers must never return to a superseded flat namespace.

## Authority boundary

Path migration does not authorize study execution, outcome inspection, qualification, release,
broker access, or trading. Missing or corrupt compatibility evidence keeps affected studies paused
and blocks release until the same exact bytes are restored or the study receives a separate valid
impact disposition.
