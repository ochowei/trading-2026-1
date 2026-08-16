# Reproducibility Addendum for Workflow v008

This normative addendum is selected by `strategy-forward-replication-research@v008`. It extends
`docs/reproducibility.md` without changing the bytes or meaning pinned by earlier workflow
releases. If the two documents conflict for a v008 study, execution stops as `indeterminate` until
the workflow-level conflict is resolved through a new version.

## Structured study identity

Every v008-capability study chooses exactly one route at initialization and preregistration:
`clean-historical`, `retrospective-confirmatory`, or `study-time-retrospective`. Preregistration
pins one complete `QUALIFICATION_SPEC.json` for all three routes. The spec fixes repository-relative
registry identities, evidence classification and justification, complete family/source/shared
runtime inventory, roles, trial budget, selection-history disclosures, execution dependencies,
benchmarks, typed challenge identities/targets/gates, whole-year Development/quarantine/Evaluation
calendars, and exact warmup bounds. It also machine-freezes the composite policy-set identity and
all four release/config digests, explicit base/stress per-side costs, and the supported immutable
snapshot/formal-observation contract (definition binding, coverage, cutoff, exact offline run mode,
outcome/validity status, and observation-time floor).

The spec does not pretend to contain a precomputed exchange-session list. Before any registry
mutation, the provider-free exact-study compiler combines those frozen calendar inputs with the
pinned released market/session policy and deterministically derives exact XNYS Development,
warmup, quarantine, and Evaluation session inventories. The resulting qualification plan freezes
those exact sessions and must be reproducible on reload. Caller-supplied alternative dates,
families, hashes, budgets, roles, or registry identities are rejected.

## Human authority chain

Preregistration alone does not authorize outcome-relevant Development. The first transition into
Development creates an add-only `DEVELOPMENT_AUTHORIZATION.json` containing the exact study path,
route, preregistration digest, current authorization time, stable human approver, operator, and a
narrow scope that excludes Evaluation, Shadow, broker, and order authority.

Evaluation additionally requires a human-approved `CANDIDATE_FREEZE.json`. Its stable approver,
approval time, narrow authorization scope, exact study identity, preregistration/spec/plan links,
selected candidate, distinct baseline, and complete frozen family are part of the frozen bytes.
It is created only by the guarded current-time `workflow study freeze-candidate` writer from an
outcome-derived selection object containing exactly the selected candidate, baseline, and ordered
complete family. The caller cannot provide approval time, scope, identity, digest, or trial-budget
fields; the writer is add-only and permits only an exact idempotent retry.
The exact-study qualification identity pins both candidate-freeze and Development-authorization
digests. A caller's current operation approval and contamination declaration are separate durable
facts; neither substitutes for the stage authorization or candidate-freeze approval.

## Tracked terminal evidence

Mutable runtime registries and local result files cannot by themselves support a terminal study
decision. Qualification registry/checkpoint snapshots are add-only, content-addressed, and tracked
at `results/qualification-evidence/<sha256>.json`. Development gates, challenge manifests, and
distinct challenge evidence artifacts are tracked under `results/study-evidence/**`. Workflow
validation requires referenced worktree bytes to equal their Git-index blobs. Publication and
replay must remain valid after Git GC and from a fresh clone. Completion verifies this condition
before writing any terminal study state.

Terminal evidence binds the exact study, route, preregistration, qualification spec, Development
authorization, candidate freeze when present, qualification plan/screen or authoritative absence
snapshot, and every required challenge artifact. Qualification snapshots replay through the
authoritative hash-chain/checkpoint reader. Typed gate results are recomputed from evidence;
manifest-level `passed` assertions are not authority. Later append-only registry events do not
change an already content-addressed terminal snapshot.
Qualification plans persist the frozen repository-relative trial and qualification registry
identities separately from operational absolute paths. Terminal and fresh-clone replay require
exact equality with those relative identities; path-suffix matching and lookalike checkout roots
are not authority.

## Lifecycle and compatibility

Pinned reference dependencies remain byte-stable and digest-checked after a release becomes
superseded or retired. The root workflow registry alone determines whether a version may initialize
new studies. Compatibility adapters may compile only the exact canonical legacy identity they name;
path suffixes, copied repositories, or caller-selected lookalikes are not accepted. Compatibility
does not migrate authority, alter legacy plan identities, or authorize outcome-relevant work.
