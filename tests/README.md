# Test ownership and placement

New tests must be placed in the responsibility directory that owns the behavior:

| Directory | Responsibility |
|---|---|
| `workflow/` | New workflow authoring, study, qualification, and terminal-review behavior. |
| `research/` | Workflow-native definitions, reproducibility, runs, results, and registries. |
| `legacy/` | Historical imports, archived diagnostics, and fail-closed legacy commands. |
| `operations/` | Ledger, followup, qualification lifecycle, sleeve, and drift operations. |
| `market_data/` | Provider, cache, validation, coverage, and migration boundaries. |
| `policies/` | Policy resolution and exact conformance tests. |
| `repository_checks/` | Executable repository architecture contracts. |

Existing root `test_*.py` files are deliberate compatibility exceptions. Released workflow studies
refer to many of their paths or exact historical bytes, so organizational cleanup must not move
them. They retain their current paths while behavior evolves normally. Do not add new root test
files; use the owning directory above.
