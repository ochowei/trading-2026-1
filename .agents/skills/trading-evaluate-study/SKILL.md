---
name: trading-evaluate-study
description: Independently review evidence for an `awaiting-review` repository workflow study, assess it against the preregistered hypothesis, plan, pinned workflow version, and frozen outcome rules, write its conclusion, and prepare a terminal outcome. Use when deciding pass, fail, insufficient-evidence, or indeterminate after execution is finished. Do not execute experiments, gather or repair evidence, change frozen plans, or author workflow changes.
---

# Evaluate Trading Studies

Read `CLAUDE.md` and `.agents/rules/workflow-study-governance.md` completely before starting. Read
the exact study, `PREREGISTRATION.json`, pinned released workflow, and every evidence artifact needed
for the declared outcome rules. Do not load workflow creation, evolution, removal, or
release-preparation references unless the user separately asks to author a workflow change.

## Enforce the review boundary

Require study status `awaiting-review` and begin with:

```bash
uv run trading workflow version state <exact-version-path> --json
uv run trading workflow validate <study-path>
```

Use the exact-version query for repository awareness, not as a new outcome rule. Stop on `invalid`.
Report `indeterminate` without inferring absent safety evidence. A prepared successor or open safety
assessment does not block read-only review, administrative reviewer return, or completion under the
already frozen plan, but it does block later outcome-relevant operator work after a return.

Remain read-only while assessing evidence. Do not invoke experiment-running skills or commands,
fill evidence gaps, modify `HYPOTHESIS.md`, `PLAN.md`, or `EVIDENCE.md`, or substitute mutable
`latest` references for frozen identities. If execution is incomplete, report the exact gap and use
the guarded `awaiting-review -> running` transition only after explicit user confirmation, with the
stable reviewer identity and a concrete reason. Without that authority, remain read-only and
propose the return. This is only an administrative return; hand the study back to
`trading-operate-workflow` and do not execute or repair evidence. The operator must re-establish
G-FAMILY before doing outcome-relevant work. Do not choose a favorable outcome.

## Evaluate against frozen rules

Trace every claim to the preregistered plan and exact evidence. Check stage completion, prohibited
deviations, missing identities, selection effects, invalidated assumptions, and the workflow's
definitions of:

- `pass`
- `fail`
- `insufficient-evidence`
- `indeterminate`

Apply the exact pinned workflow's mapping rather than a generic preference. `insufficient-evidence`
is available only when that workflow explicitly permits it for an open, still-accumulating
prospective checkpoint. For a v008 `study-time-retrospective` fixed completed-data checkpoint,
missing, conflicting, or unverifiable required evidence is `indeterminate`, not
`insufficient-evidence`; do not gather or repair evidence retrospectively.

For that v008 route the only valid terminal tuples are:

- `pass` / `retrospectively-supported` / `retrospective-evaluation`;
- `fail` / `development-selection-failed` / `development`;
- `fail` / `retrospective-screen-failed` / `retrospective-evaluation`; or
- `indeterminate` / no disposition / the exact stage where the decision became indeterminate.

Recompute and replay the tracked terminal package through the repository validator. Do not treat a
manifest assertion, mutable registry head, untracked file, absolute-path lookalike, or missing
terminal identity as evidence authority.

## Confirm and record the conclusion

Prepare a concise proposed outcome, evidence trace, limitations, and follow-up implications. Ask
the user to confirm this research-validity decision and obtain a stable reviewer identity before
writing `CONCLUSION.md` or completing the study.

After confirmation, write only `CONCLUSION.md`, then run:

```bash
uv run trading workflow study complete <study-path> \
  --outcome <pass|fail|insufficient-evidence|indeterminate> \
  --reviewed-by <identity> \
  --disposition <workflow-defined-disposition> \
  --decision-stage <workflow-defined-stage>
uv run trading workflow validate --all
```

For v008 `study-time-retrospective`, omit `--disposition` only for `indeterminate`; always supply
`--decision-stage`. Older routes that do not define these typed fields must continue to omit them.

The command generates `COMPLETION.json`, freezing preregistration, evidence, conclusion, outcome,
time, and reviewer identity. Never edit completed artifacts. New evidence requires a new study,
linked with `revisits` when appropriate.

## Route process defects correctly

When evidence exposes a defect in the workflow rather than the study, finish the study according
to its frozen rules and recommend `trading-author-workflow` to open a change. Do not edit the active
workflow or create a change from this skill.

## Finish

Report the study ID, pinned workflow version, exact control-state result, validated evidence
identities, confirmed outcome, limitations, completion validation, and any separately recommended
workflow change. Distinguish a completed study result from downstream promotion or trading
authorization.
