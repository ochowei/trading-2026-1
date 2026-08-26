# Repository checks

This directory contains tracked configuration and executable checks that enforce repository-wide
architecture contracts. These checks are active CI inputs, not archived implementation material.

## Path ownership

`path-ownership.json` is the executable projection of the ownership and status boundaries defined
in `docs/ARCHITECTURE.md`. It classifies the public children of `.agents/`, `docs/`, `results/`,
`src/trading/`, and `tests/` as `active`, `shared`, `legacy-compat`, `legacy-archive`,
`version-pinned`, or `local-only`.

Each rule records a path pattern, canonical owner, whether new content is allowed, and a reason.
`check_path_ownership.py` rejects unknown statuses, missing required paths or owners, duplicate or
overlapping matches, unclassified public paths, and additions to closed compatibility directories.
Do not weaken the registry to make an ownership violation pass; update the architecture and the
registry together when a path genuinely changes responsibility.

Run the check and its contract tests with:

```bash
uv run python config/repository-checks/check_path_ownership.py
uv run pytest -q tests/repository_checks/test_path_ownership.py
```

## Legacy experiment inventory

`legacy-experiment-inventory.json` records the closed set of legacy experiment package identities.
`check_legacy_experiment_inventory.py` compares that baseline with importable packages under
`legacy/experiments/`.

The inventory may only shrink. Update it when an existing legacy experiment package is permanently
removed: delete the package and remove its identity from the inventory in the same change. This
makes retirement irreversible because restoring that identity later will be rejected as a new
legacy experiment.

Do not update the inventory to:

- add a new experiment identity;
- permit a renamed replacement for an existing identity; or
- automatically copy the current directory scan into the baseline.

Keep `packages` as sorted, unique, non-empty strings and leave `schema_version` unchanged unless the
checker and its tests deliberately introduce a new schema.

After changing the package archive or inventory, run:

```bash
uv run python config/repository-checks/check_legacy_experiment_inventory.py
uv run pytest -q tests/legacy/test_legacy_experiment_inventory.py
```

Any failure blocks the change until the legacy archive and its inventory satisfy the closed-set
contract.

## Market-data boundary

`check_experiment_market_data_access.py` enforces permanent zero tolerance for experiment code that
bypasses the declared market-data boundary. It rejects direct yfinance use, known indirect legacy
data-access paths, and runtime yfinance imports outside `src/trading/market_data/provider.py`.

The temporary Phase 9 bypass allowlist was retired after reaching zero entries. Do not recreate an
allowlist to admit a new exception; migrate the caller to the declared market-data boundary instead.

Run the check and its tests with:

```bash
uv run python config/repository-checks/check_experiment_market_data_access.py
uv run pytest -q tests/market_data/test_market_data_migration_policy.py
```
