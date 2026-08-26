# Documentation status and routing

Use this page to choose current operational guidance without rewriting documents whose exact bytes
are pinned by released workflows. `docs/ARCHITECTURE.md` remains the canonical repository map;
`config/repository-checks/path-ownership.json` is its executable path-status projection.

## Status vocabulary

| Status | Meaning |
|---|---|
| Current | Maintained guidance for current repository behavior. |
| Version-pinned | Immutable dependency retained for an exact workflow version; it may describe an older interface. |
| Compatibility | Maintained only for explicit read-only, migration, or fail-closed behavior. |
| Historical | Implementation context, not current instructions. |
| Retired | The documented operation no longer has execution authority. |

## Current entry points

| Need | Read first |
|---|---|
| Repository layout and ownership | `ARCHITECTURE.md` |
| Workflow and study operation | Repository-root `workflows/README.md` and the active `trading-*` skills |
| Workflow-native research execution | `reproducibility-v008.md` plus the exact released workflow selected by the study |
| Current qualification compilation | `historical-qualification-and-shadow-v008.md` and the exact study `QUALIFICATION_SPEC.json` |
| Legacy archive inspection | Repository-root `legacy/README.md` and `legacy-experiment-retirement-v010.md` |
| Result namespaces | Repository-root `results/README.md` |

## Version-pinned documents with retired examples

The following unversioned paths remain unchanged because released workflows pin their exact bytes:

| Document | Current interpretation |
|---|---|
| `reproducibility.md` | Older normative dependency. Its `trading run` and `data snapshot --experiment` examples are retired; new formal runs use `trading research`. |
| `historical-qualification-and-shadow.md` | Older qualification dependency. Its `--experiment` registration example is retired; new registration uses workflow-native `--research` or `register-study`. |
| `result-validity-and-trial-history.md` | Older result dependency. Its top-level legacy CLI spellings are retired; read-only archive diagnostics use `trading legacy ...`. |

Do not edit these files merely to update command examples. Behavioral changes require a versioned
successor selected by a new workflow version.

## Historical material

`superpowers/specs/` and `superpowers/plans/` preserve earlier designs and implementation plans.
They may contain imperative language, obsolete paths, or completed migration instructions and must
not be treated as current work orders.
