# Test ownership and placement

New tests must be placed in the responsibility directory that owns the behavior:

| Directory | Responsibility |
|---|---|
| `workflow/` | New workflow authoring, study, qualification, and terminal-review behavior. |
| `research/` | Workflow-native definitions, reproducibility, runs, results, and registries. |
| `legacy/` | Historical imports, archived diagnostics, and fail-closed legacy commands. |
| `legacy/conformance/` | Exhaustive frozen-inventory replay, split into fast smoke and slow full-matrix cases. |
| `operations/` | Ledger, followup, qualification lifecycle, sleeve, and drift operations. |
| `market_data/` | Provider, cache, validation, coverage, and migration boundaries. |
| `policies/` | Policy resolution and exact conformance tests. |
| `repository_checks/` | Executable repository architecture contracts. |

Existing root `test_*.py` files are deliberate compatibility exceptions. Released workflow studies
refer to many of their paths or exact historical bytes, so organizational cleanup must not move
them. They retain their current paths while behavior evolves normally. Do not add new root test
files; use the owning directory above.

## Test tiers

The default development and pull-request suite includes every non-slow test plus 41 fixed legacy
smoke cases:

```bash
uv run pytest -m "not slow"
```

The complete 811-case legacy replay matrix remains available locally:

```bash
uv run pytest -m legacy_conformance -n auto
```

CI runs the complete Primary matrix for relevant shared-runtime pull requests, every `main` push,
daily at 09:00 UTC, and manual dispatch. Every pull request gets the 20 Auxiliary smoke tests; the
complete 240-case Auxiliary matrix runs only after a `main` push, weekly on Monday at 09:00 UTC,
manual dispatch, or when a pull request receives the `full-auxiliary-conformance` label.

Do not replace the full matrix with the smoke set when changing legacy strategies, shared strategy
or bundle execution, market data, research data, or pinned execution/sleeve implementations.
