# Validation

## Evidence and challenge method

The independent S001 review compared v001 `WORKFLOW.md`, version metadata, and `RELEASE.json` and
confirmed the four role mismatches. Validation for v002 must prove that every dependency described
as normative has an exact release digest, that release validation fails on digest drift, and that
formal observation verification fails when a declared outcome-relevant orchestration identity is
missing or changed. A fixed-snapshot capture-to-load-to-run test must demonstrate provider-free
replay with unchanged results.

## Interaction with other accepted changes

No other v001 changes exist. This change preserves the exact four policy pins and does not adopt a
new policy release.

## Remaining uncertainty

The minimal maintainable orchestration capture boundary must be selected during v002
implementation without absorbing irrelevant CLI presentation code. Release approval must not be
requested until focused tests, the full suite, policy/workflow validation, legacy inventory guard,
Ruff, and digest-drift challenges pass.
