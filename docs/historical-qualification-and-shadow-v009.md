# Guarded challenge-only Phase 6 contract (v009)

This normative Phase 6 extension is selected only by
`strategy-forward-replication-research@v009`. The unchanged route, calendar, screen, terminal,
Shadow, and compatibility rules remain pinned to
`docs/historical-qualification-and-shadow-v008.md`; the complete behavioral authority remains the
v009 `WORKFLOW.md`. This document defines the new executable challenge and publication boundary.

## Preregistration-ready challenge contract

Every one of the nine required challenges freezes a complete executable contract in
`QUALIFICATION_SPEC.json` before outcome-relevant Development execution. A name, seed, percentage,
target identity, gate, or evidence identity alone is insufficient. Each contract binds:

- the challenge ID, contract schema version, registered implementation ID/version, implementation
  source identity and digest, and exact input/output schema identities;
- ordered source roles and identities, exact Evaluation projection rules, allowed dependency-only
  roles, required raw fields, algorithms, parameters, seeds, sample counts, rounding, tie handling,
  event transforms, cost/fill ordering, ledger interaction, output metrics, and failure conditions;
- the typed gate, exact benchmark/trial/method target, unique evidence identity, and all values
  needed to recompute the observed metric without a provider or caller interpretation; and
- a stable human preregistration approver and approval time through the enclosing preregistration
  and its frozen digest.

Unknown implementations, omitted fields, implicit defaults, mutable aliases, caller-provided
observed values, or a contract whose digest cannot be reproduced fail before preregistration.
Study-specific parameters may differ only when the registered schema permits them and the exact
values are frozen before outcome inspection.

For `missed-entries`, the contract additionally freezes the eligible-entry universe, canonical
ordering key and direction, selection algorithm, percentage-to-count rounding, seed, tie handling,
whether zero selected entries is allowed, and without-replacement ledger behavior. For
`worse-fills`, it freezes the exact entry and exit transforms, tick/precision rounding, gap and
intrabar-ambiguity handling, fee/slippage order, unavailable-price behavior, unfilled behavior,
and any effect on later positions or capital. No implementation may infer these semantics from a
method label.

## Exact source observation set and role projection

The challenge operation accepts only an exact repository study path, the plan ID frozen for that
study, and the exact family manifest inputs required by the registered plan. It resolves the
released workflow, route, preregistration, plan, qualification spec, Development authorization,
candidate freeze, policy set, selected candidate, distinct baseline, ordered complete family,
trial budget, source identities, definition fingerprints, and all frozen digests from authoritative
registries. Caller aliases, mutable `latest`, filenames, dates, or observation time never establish
identity.

For each family member, the operation resolves exactly one successful, valid formal Evaluation
observation matching the frozen trial, snapshot, result, manifest, offline run mode, and complete
Evaluation session inventory. Missing or duplicate matches, incomplete sessions, mixed run modes,
policy/workflow/fingerprint drift, or different data generations fail closed.

All family observations must share one verified frozen data generation. The operation creates or
resolves a content-addressed role projection over exactly the registered Evaluation sessions. The
projection records source observation/result/manifest/data-generation identities and the excluded
Development, quarantine, and warmup inventories. Excluded roles may supply only dependencies
explicitly allowed by the frozen method. They cannot contribute signals, accepted candidates,
positions, fills, cooldown, P&L, capital, benchmark samples, or metrics. Source observations remain
immutable and are never rewritten or relabelled.

## Independent guarded operation

The public operation is equivalent to:

```text
trading qualification challenge run-study --study <path> --plan-id <id> [exact family manifests] [--dry-run]
```

The spelling and module layout may differ, but the operation must have independent challenge-only
authority. It must not call the qualification screen coordinator, refresh or obtain provider data,
execute a research definition, create a trial observation, mutate trial or qualification
registries, create terminal evidence, transition a study, or authorize Shadow, activation, broker,
order, or live behavior.

`--dry-run` performs every identity, contract, source, projection, path, duplicate, and collision
check and prints the deterministic publication plan without creating or mutating artifacts,
registries, observations, or journals.

## Atomic publication and replay

A non-dry-run evaluates each frozen challenge method at most once from the verified role
projections and publishes exactly nine distinct content-addressed challenge artifacts plus one
manifest under `results/workflows/<workflow>--vNNN/<study>/<stage>/**`. Each artifact binds the
study, preregistration, spec, candidate freeze, plan, workflow, policy set, implementation, source
observations/results/manifests, common data generation, exact Evaluation sessions, metric, observed
value, typed gate, and sufficient raw values for provider-free recomputation. The manifest may
index these artifacts but cannot substitute a self-reported `observed` or `passed` value.

Publication takes a bounded study/plan lock, stages every file in the destination filesystem,
verifies final content-addressed identities, and commits the complete set atomically. A failure
leaves no newly visible partial set. An exact retry is idempotent. Partial, conflicting, duplicate,
differently bound, or previously executed challenges fail closed. Recovery may complete only an
already committed exact publication decision and rejects changed inputs.

## Release readiness

v009 must not be released until provider-free synthetic tests demonstrate complete contract
rejection, exact observation resolution, role isolation, deterministic nine-artifact output,
dry-run zero mutation, atomic rollback/recovery, exact retry idempotence, collision rejection, and
failure on provider, definition-execution, registry-writer, or screen-coordinator access. The CLI,
Phase 6, reproducibility, result-layout, and architecture documentation must match the implemented
schema and paths. No study outcome is inspected to satisfy release readiness.
