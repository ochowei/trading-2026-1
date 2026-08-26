# Tracked Research-Evidence Preservation

Pre-freeze Markdown evidence referenced by an immutable `CANDIDATE_FREEZE.json` is stored only at
`results/evidence/research/<sha256>.md`. The filename is the SHA-256 of the exact file bytes; there
is no mutable alias or second maintained copy. `src/trading/research_data/evidence.py` owns
add-only publication and digest-based resolution. Existing content is never overwritten, and a
digest mismatch fails closed.

`trading workflow validate --all` scans candidate-freeze references and verifies that the
canonical artifact exists, is present in the Git index, and matches its pinned digest. A file that
only exists as an untracked working-tree artifact is rejected. Release-readiness regression uses a
real temporary Git index, commits the artifact, runs Git GC, makes a fresh clone, and repeats the
validation. Consequently the evidence path does not depend on unreachable Git objects, local
caches, reflogs, or the originating worktree. Referenced artifacts are permanent repository
evidence: cleanup and garbage-collection tooling must exclude them, and deletion or byte changes
require validation to fail.

This document explains the preservation implementation selected by v008. The complete
behavioral rules are self-contained in v008 `WORKFLOW.md` and its versioned Phase 6 normative
dependency. This reference does not modify any already released workflow version.

## Frozen qualification publication

Complete-family preparation and qualification-plan registration are one recoverable operation.
The coordinator first persists an exact journal containing the frozen plan payload, all
outcome-free family registrations, current timestamp, and both registry paths. It then performs
idempotent registry writes under a serialized transaction lock. A process or second-write failure
leaves the journal as an explicit incomplete commit decision; the next retry must finish those
same bytes before any different operation can proceed. It may not silently accept a half-published
family or replace the prepared plan. Normal public retry performs this recovery before reading a
new clock value and requires the same study, both registry paths, human approver, and contamination
declaration. The exact family-universe check and qualification-plan append run while the trial
registry lock is still held, so a concurrent family mutation cannot interleave at the commit
boundary.

High-risk public compilation accepts an exact study path rather than caller-supplied family,
calendar, source-hash, trial-budget, candidate, or baseline values. Every v008 capability-scoped
route pins a structured `QUALIFICATION_SPEC.json` at preregistration and candidate freeze. The
compiler also pins the preregistration, plan, add-only Development authorization, human-approved
candidate freeze, workflow release, policy set, family source, shared runtime, definition
fingerprint, and trial-registry selection-boundary identities.
The candidate freeze itself is produced add-only by the guarded current-time workflow command from
an exact three-field Development selection object; callers cannot author approval time, scope,
identity, digest, or budget fields. Plans preserve exact repository-relative registry identities
separately from operational paths so fresh-clone replay never relies on path-suffix matching.

Each study-time preregistration pins the authoritative trial- and qualification-registry
repository-relative identities. Terminal retrospective decisions do not rely on a mutable local
registry head alone. They publish the exact registry bytes, its pinned source identity, and head
checkpoint as one tracked,
`results/evidence/qualification/<sha256>.json` snapshot. Resolution verifies outer and inner
digests, replays the original hash chain and checkpoint through `QualificationRegistry`, and then
selects the exact frozen plan and sole canonical `historical-screen:<plan-id>` event; duplicate or
noncanonical plan/screen events fail closed. A Development terminal failure must instead link a
snapshot of the same preregistered registry proving that the study has no plan or screen. At
publication, the resolved registry path must equal repository root plus its declared frozen source
identity; path and identity cannot be supplied independently. At Development completion, the
absence snapshot must equal the current local registry/checkpoint head. Completion and public plan
registration hold the same study-registration lock; the compiler re-reads the freeze and rejects a
completed study after acquiring that lock, while completion rejects a pending transaction journal.
Later
fresh-clone validation replays the tracked terminal snapshot without requiring private runtime
state. Qualification snapshots must use `results/evidence/qualification/<sha256>.json`;
Development gates, challenge manifests, and distinct challenge artifacts must use the owning
`results/workflows/<workflow>--vNNN/<study>/<stage>/**` namespace. All must be present in the Git
index and remain replayable after Git GC
and a fresh clone. The repository `.gitignore` explicitly unignores these canonical namespaces.
“Present in the Git index” means the staged blob bytes equal the bytes whose digest is pinned; path
membership alone is insufficient. Study completion performs this tracked/replayable check before
writing `COMPLETION.json` or terminal README state, so a rejected completion cannot leave a false
completed record behind.

Historical v008 and earlier artifacts retain their frozen old path strings. The v009 storage
boundary resolves those strings only through the tracked, one-hop, digest-bound
`results/registries/path-migrations.json`; it never rewrites completed or preregistered study bytes.
