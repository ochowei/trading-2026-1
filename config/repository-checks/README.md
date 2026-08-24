# Repository checks

This directory contains tracked configuration and executable checks that enforce repository-wide
architecture contracts. These checks are active CI inputs, not archived implementation material.

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
uv run pytest -q tests/test_legacy_experiment_inventory.py
```

Any failure blocks the change until the legacy archive and its inventory satisfy the closed-set
contract.
