# Legacy conformance tests

This directory contains the exhaustive replay matrix for the closed legacy experiment inventory.
It is active compatibility coverage, not an extension point for new research identities.

Every case is marked `legacy_conformance`. The fixed representative cases are also marked
`legacy_smoke`; all remaining cases are marked `slow`. Run the fast repository regression with:

```bash
uv run pytest -m "not slow"
```

Run the complete matrix, preferably in parallel, with:

```bash
uv run pytest -m legacy_conformance -n auto
```

The fast pull-request suite always includes 10 representative Auxiliary experiments (20 tests).
Full Auxiliary CI runs after `main` pushes, weekly on Monday at 09:00 UTC, on manual dispatch, or
when a pull request receives the `full-auxiliary-conformance` label. Primary retains its relevant
path-triggered pull-request run and daily schedule.

Only remove a parametrized identity when the same change validly removes it from the closed legacy
inventory. Do not add a new identity here.
