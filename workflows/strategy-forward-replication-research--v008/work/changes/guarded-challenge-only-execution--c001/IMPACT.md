# Impact

## Rules and artifacts affected

This change affects structured qualification-spec readiness, plan-to-observation binding,
Evaluation role projection, challenge stage authority, required challenge evidence, atomic
publication, terminal replay inputs, stopping rules, and provider/registry prohibitions. These are
workflow-level research-validity and authority changes, so they require an accepted change record
and a complete replacement workflow version; they cannot be applied as a v008 erratum.

Expected implementation work belongs outside `workflows/`: a challenge method registry and strict
schemas; plan-bound observation/result/manifest resolution; provider-free canonical-evidence and
market-data role projection; a challenge-only coordinator and CLI; content-addressed evidence and
manifest codecs; locking, transaction/recovery, and duplicate guards; workflow/spec/terminal
validators; synthetic fixtures; and CLI, Phase 6, reproducibility, and architecture documentation.
No code, test fixture, result, observation, registry, or market-data blob belongs in the change
record itself.

The replacement workflow must pin a new normative Phase 6 contract that defines the executable
challenge-spec schema and publication/replay boundary. Existing v008 technical dependencies and
artifact schemas keep their historical meaning; they are not silently reinterpreted.

## Existing studies and hypotheses

- `strategy-forward-replication-research@v008/S003` is `continue-on-v008`. This prospective change
  does not modify its frozen hypothesis, plan, qualification spec, candidate freeze, observations,
  registries, evidence, status, or authority. It does not authorize S003 challenge execution and
  does not retroactively supply missing method semantics.
- Completed v008/S001 and v008/S002 remain immutable and retain their existing outcomes,
  dispositions, evidence classifications, and authority.
- Before a replacement version can supersede v008, every unfinished v008 study must be in a safe
  `paused`, `completed`, or `cancelled` state. This change does not perform that transition.
- The next CLI-allocated study under a released replacement version starts with that version's
  local study numbering and must independently preregister a complete executable challenge spec.
  Cross-version continuity uses only an exact `revisits` path; no v008 study ID or evidence is
  migrated implicitly.

## Compatibility and migration risk

Existing registered plans, observations, screens, terminal evidence, and challenge artifacts keep
their exact identities and validation rules. The new command must refuse legacy or v008 plans that
do not pin the complete executable method contract; compatibility must not invent defaults or map
an old method name to new semantics. Old broad formal results may remain valid source evidence, but
only a newly governed operation may create a role projection and it cannot alter the source bytes.

The principal scientific risks are outcome-dependent method completion, allowing excluded roles
to affect Evaluation metrics, mismatching a plan with a convenient observation, and treating a
self-reported boolean as challenge evidence. The principal operational risks are accidental
provider access, definition reruns, partial publication, registry mutation, screen coupling,
duplicate execution, and recovery against changed inputs.

Release validation must demonstrate that the challenge-only coordinator cannot call the screen
coordinator, provider, refresh, research execution, or registry writers, including through injected
failure paths. It must also demonstrate exact retry idempotence, full rollback, fresh-clone replay,
content-addressed artifact verification, and rejection of any under-specified or unregistered
method identity.
