# Validation

## Evidence and challenge method

Review of PR #169 and its focused tests verified canonical argv capture,
workflow/release/policy binding, complete Git HEAD capture, exact source-byte hashing, defensive
result persistence, and exclusion from legacy identities. Confirm all v002 terminal hashes and
indexes remain unchanged.

For the replacement draft and prepared release, run policy validation, workflow synchronization and full workflow
validation, focused workflow/policy/research-definition tests, the legacy inventory guard, Ruff
lint and format checks, and `git diff --check`. Also verify that changing either normative document
without superseding v002 fails closed, while the prepared v003 transition pins the updated digests
and validates cleanly.

## Interaction with other accepted changes

No other v002 change record exists. The replacement draft must cite only this accepted change and
must carry forward the complete v002 contract without unrelated behavioral edits.

## Remaining uncertainty

Canonical merge remains required before v003 becomes effective. A prepared release on this branch
is not authority to run a study, inspect outcomes, activate a strategy, or trade.
