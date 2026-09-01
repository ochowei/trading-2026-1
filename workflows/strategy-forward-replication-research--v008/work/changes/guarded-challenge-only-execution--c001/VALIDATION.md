# Validation

## Evidence and challenge method

This draft is supported by a provider-free repository capability review. The current v008
qualification coordinator can resolve a registered plan, verify exact formal snapshots and
trial-registry observations, and project canonical returns onto frozen Evaluation sessions. The
public CLI exposes plan and screen operations but no independent guarded challenge-only producer.

The review also found that v008 permits method targets whose names and output gates are frozen
without a complete executable calculation contract. Seed plus omission percentage does not uniquely
define missed-entry selection and ledger handling; an adverse-fill identity plus a boolean output
gate does not uniquely define the fill transform. Those gaps must be resolved prospectively before
implementation or study execution. No S003 outcome metric was needed to identify them.

Validation required before a replacement version containing this accepted change can be released:

1. Specify a strict versioned executable challenge-method schema covering every required semantic
   field and prove preregistration rejects omissions or unknown implementations.
2. Prototype provider-free plan-bound resolution and exact Evaluation role projection with only
   synthetic observations, results, manifests, and data blobs.
3. Demonstrate deterministic artifacts for all nine method classes, including fully specified
   missed-entry and adverse-fill transforms, without caller-supplied observed values.
4. Demonstrate dry-run zero mutation; non-dry-run all-or-nothing publication; exact retry
   idempotence; injected rollback/recovery; and collision/conflict rejection.
5. Demonstrate fail-closed handling of missing/duplicate observations, mixed generations,
   fingerprint/policy/workflow drift, Development/quarantine/warmup leakage, incomplete sessions,
   provider access, definition execution, registry writes, and implicit screen invocation.
6. Run relevant qualification, registry, result-schema, research-data, workflow-authoring,
   terminal-evidence, and CLI regression tests plus Ruff and complete workflow validation.

Acceptance records the required behavioral boundary, not implementation or release readiness. No
challenge execution, study transition, or outcome authority is created by this decision.

## Interaction with other accepted changes

This change is intended for v009 together with accepted v008/C002 categorized result-layout
migration and v008/C003 Workflow Release Activation. C002 changes the canonical destination of the
new challenge artifacts but not their identities or semantics. C003 changes workflow release
authority but grants no challenge execution authority. The combined v009 draft must preserve all
three boundaries and their independent release conditions.

## Remaining uncertainty

The exact executable schemas and registered implementations for all challenge methods remain a
release-readiness requirement. Study-specific method parameters may vary, but v009 must require
them to be complete, versioned, digest-bound, human-approved before outcome inspection, and
deterministically executable without defaults. In particular, candidate ordering, rounding, and
no-replacement behavior for missed-entry evidence and the exact canonical adverse-fill transform
must be frozen by the study. The selected version is v009 and its Phase 6 contract is
`docs/historical-qualification-and-shadow-v009.md`; command spelling and transaction encoding may
remain implementation details only if they preserve the accepted behavioral boundary.

Until the change is implemented, validated in the complete v009 draft, explicitly approved for
release, and made active under the applicable bootstrap rule, v008 remains authoritative and no
study gains new challenge-only authority.

## Post-acceptance implementation evidence (2026-09-01)

This evidence was produced after the acceptance/evolution decision and does not retroactively turn
that decision into implementation evidence. The v009 draft now contains the independent guarded
operation in `src/trading/workflow/challenge_execution.py` and the public
`trading qualification challenge run-study` command. The fixed-route compiler requires exact
`fixed-challenge-v1` method contracts for all nine methods; the operation verifies exact family
manifests, formal offline observations, definition fingerprints, policy set, workflow provenance,
common data generation, and complete Evaluation role projection before publishing nine distinct
content-addressed artifacts plus one manifest.

Provider-free synthetic coverage demonstrates dry-run zero publication, deterministic atomic
publication, exact retry idempotence, injected rename failure without a visible partial set,
terminal manifest recomputation, collision rejection, and workflow-provenance drift rejection.
Repository validation completed with:

- `uv run pytest -q tests/test_challenge_execution.py`: 4 passed;
- the affected qualification/workflow/terminal/result/path suites: 187 passed;
- `uv run pytest -m "not slow" -q`: 764 passed, 770 deselected;
- `uv run pytest -m legacy_conformance -n auto -q`: 811 passed;
- `uv run ruff check ...` and `uv run ruff format --check ...`: passed;
- `uv run trading workflow validate --all`: passed; and
- `uv run trading policy validate --all`: passed.

No provider was contacted, no study outcome was inspected, no registry or study state was mutated,
and this validation does not release or activate v009.
