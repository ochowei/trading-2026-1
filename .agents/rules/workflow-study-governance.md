# Workflow Study Governance

This is the canonical shared lifecycle and authority reference for repository workflow study
operators and independent reviewers.

## Identity and pinning

A workflow is a versioned procedure. A study is one execution instance pinned to one exact released
workflow version. Create and preregister new studies only under the active version; never operate a
draft, silently move a study to another version, or edit released workflow bytes.

Study IDs are local to the exact workflow version. Let the CLI allocate the next never-reused
`Sxxx`; cross-version continuity uses an exact repository-relative `revisits` path, never a carried
or predicted ID.

## Lifecycle

Use guarded CLI transitions for:

```text
draft -> preregistered -> running -> awaiting-review -> completed
                           |  ^             |
                           v  |             -> running
                         paused

draft/preregistered/running/paused -> cancelled
```

Require concrete reasons for pause, cancellation, or reviewer return. `completed` and `cancelled`
are terminal. A reviewer may return `awaiting-review -> running` only without changing the frozen
design.

## Frozen design and authority

Before preregistration, complete a falsifiable `HYPOTHESIS.md` and exact `PLAN.md`, then obtain
explicit current human approval with a stable identity. The guarded command generates
`PREREGISTRATION.json` with current time and exact workflow/hypothesis/plan digests. Never backdate
or hand-author it.

After preregistration, never modify the hypothesis or plan. A design change requires cancellation
and a new study linked through `revisits`.

Authority is stage-specific. Preregistration does not authorize Development; Development does not
authorize candidate freeze; candidate freeze does not authorize Evaluation, Shadow, broker access,
orders, or live trading. Use every additional approval required by the pinned workflow and policy
set. Never infer broader authority from a dry-run or existing artifact.

## Operator and reviewer separation

The operator follows the frozen plan, invokes the routed repository skills, and records exact
evidence. The operator never chooses or writes an outcome. When evidence is complete, the operator
submits `awaiting-review` and stops.

The independent reviewer remains read-only while assessing evidence against the preregistered
hypothesis, plan, pinned workflow, and frozen outcome mapping. The reviewer does not execute work,
repair evidence, or change frozen files. After explicit human confirmation with a stable reviewer
identity, the reviewer may write only `CONCLUSION.md` and use the guarded completion command.

Completion generates immutable `COMPLETION.json` binding preregistration, evidence, conclusion,
outcome, time, and reviewer identity. Use only the outcomes and typed fields authorized by the
pinned workflow. Never edit completed artifacts.

## Evidence and privacy

Formal evidence uses exact repository-relative paths, immutable manifest/snapshot IDs, complete
commit SHAs, checksums, workflow/policy identities, and Research Definition Snapshot identities.
Mutable `latest`, filenames, timestamps, or caller assertions cannot substitute for frozen
evidence.

Missing, stale, corrupt, conflicting, incorrectly bound, or non-replayable evidence fails closed
under the pinned workflow's outcome rules. Do not hide failed trials, weaken gates, tune after
outcome inspection, omit deviations, or manufacture replacement evidence.

Never store credentials, broker exports, holdings, private ledgers, or raw private trading data
under `workflows/`.

## Version boundaries

Before an active workflow version is superseded or retired, every unfinished study must reach a
safe `paused`, `completed`, or `cancelled` state. Never move or overwrite the old study. Authoring
impact analysis decides whether paused research continues, restarts, or closes; any later effort is
a new study under the target version with an exact `revisits` link.

Run workflow sync and full validation after every mutation.
