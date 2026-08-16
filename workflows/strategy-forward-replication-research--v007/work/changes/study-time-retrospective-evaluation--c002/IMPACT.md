# Impact

## Rules and artifacts affected

This change affects workflow purpose and decisions, entry conditions, route selection, stage order,
data-role calendars, candidate freeze, retrospective screen requirements, terminal outcomes,
successor-study lineage, promotion boundaries, required evidence, stopping rules, and explanatory
documentation. It requires a replacement workflow version and a new versioned Phase 6 normative
contract; it cannot be implemented as a v007 erratum.

Expected implementation work includes qualification plan/schema terminology, explicit
retrospective calendars, frozen selection boundaries, public registration/screen coordination,
status projection, Shadow-source rejection, CLI help, provider-free replay, trial-registry checks,
workflow validators, and end-to-end tests. Code, tests, registries, and formal results remain in
their authoritative repository locations and are not copied into `workflows/`.

The version companion `STAGES_AND_OUTCOMES.md` is explanatory, not normative. It must remain
semantically consistent with the complete replacement `WORKFLOW.md`; conflicts fail authoring
review in favor of `WORKFLOW.md`. Moving the guide requires architecture/link updates and a pointer
at the old docs path, not a second maintained copy. Release evidence and validators must pin and
verify its exact bytes so a released companion cannot drift even though it does not define
behavior.

## Existing studies and hypotheses

- There are no unfinished studies under v007.
- `strategy-forward-replication-research@v004/S004` remains `continue-on-v004`, paused with its
  already preregistered 2015-2025 Development, 2026 quarantine, and 2027-2031 clean Historical
  boundary. C002 does not convert it to retrospective, migrate it, alter its frozen plan, or
  authorize outcome access.
- Completed v006/S001 remains terminal `indeterminate`; its exposed 2010-2014 outcomes remain
  Development context and cannot be reused as confirmation.
- All other completed or cancelled studies remain immutable. A replacement workflow does not
  reinterpret their outcomes, dispositions, or authority.

The next CLI-allocated study under a released replacement version may choose the study-time route.
If it revisits earlier research, it must record the exact prior study path and independently freeze
its own data roles, family, candidate, gates, approvals, and evidence.

## Compatibility and migration risk

Existing v007 plan, registry, screen, and status payloads must preserve their exact identities and
meaning. The new route needs an explicit discriminator; reload must not infer it from dates or
silently convert an old retrospective-confirmatory plan. Existing retrospective dispositions
remain non-promotional, and existing verified-clean Historical screens remain the only eligible
source class for Shadow.

The primary scientific risks are disguised in-sample reuse, choosing the retrospective window
after seeing outcomes, incomplete family history, repeated trial expansion, and interpreting a
retrospective pass as qualification. The primary operational risks are running Development before
preregistration, allowing outcome inspection before candidate freeze, permitting partial ranking,
or letting status projection map `retrospectively-supported` to `shadow-eligible`.

Release validation must prove both the positive study-time route and fail-closed rejection of role
overlap, late freeze, post-boundary trials, classification upgrade, plan/screen identity mismatch,
retrospective-sourced Shadow registration, and historical `insufficient-evidence`. Human-readable
labels must consistently distinguish outcome (`pass`) from disposition
(`retrospectively-supported`) and authority (none beyond the completed research conclusion).
Development failure must remain distinguishable as `development-selection-failed`; it cannot
project a retrospective-screen disposition when no plan or screen exists.
