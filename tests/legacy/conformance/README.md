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

Only remove a parametrized identity when the same change validly removes it from the closed legacy
inventory. Do not add a new identity here.
