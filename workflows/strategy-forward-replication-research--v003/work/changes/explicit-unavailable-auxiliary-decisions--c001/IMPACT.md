# Impact

## Rules and artifacts affected

The replacement workflow must add the opt-in unavailable-decision rule to entry conditions,
Development evidence, invariants, indeterminate behavior, version boundaries, and shared technical
links. `AvailabilityPolicy`, auxiliary alignment, immutable manifest encoding, workflow-native
definition runtime, reproducibility/market-data documentation, and tests are affected. Released
v003 WORKFLOW/RELEASE and policies remain untouched.

## Existing studies and hypotheses

- S001: `cancelled`; no disposition required.
- S002: `cancelled`; no disposition required.
- S003: `cancelled`; no disposition required.

No unfinished v003 study remains. The next CLI-allocated XLF study is `restart-on-v004` and must be
created under v004 with an exact `revisits` path to v003 S003 only after v004 becomes canonically
active. Because v004 has no studies, its first allocated ID will be `S001`.
No hypothesis, plan, result, or terminal artifact is moved or overwritten.

## Compatibility and migration risk

Default wire and runtime behavior remain `fail`, omitted from canonical bytes for compatibility.
Only a newly preregistered definition may select `mark_unavailable`, producing a new definition
fingerprint and manifest identity. The main risk is accidentally allowing an unavailable row into
signals; tests must demonstrate exact suppression and preservation of lag audit columns. A change
to unavailable-session treatment requires a new study and workflow version.
