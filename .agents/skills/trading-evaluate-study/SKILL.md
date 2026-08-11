---
name: trading-evaluate-study
description: Independently review evidence for an `awaiting-review` repository workflow study, assess it against the preregistered hypothesis, plan, pinned workflow version, and frozen outcome rules, write its conclusion, and prepare a terminal outcome. Use when deciding pass, fail, insufficient-evidence, or indeterminate after execution is finished. Do not execute experiments, gather or repair evidence, change frozen plans, or author workflow changes.
---

# Evaluate Trading Studies

Read `CLAUDE.md` and
`.agents/skills/trading-author-workflow/references/workflow-authoring-contract.md` completely before
starting. Read the exact study, `PREREGISTRATION.json`, pinned released workflow, and every evidence
artifact needed for the declared outcome rules.

## Enforce the review boundary

Require study status `awaiting-review` and begin with:

```bash
uv run trading workflow validate <study-path>
```

Remain read-only while assessing evidence. Do not invoke experiment-running skills or commands,
fill evidence gaps, modify `HYPOTHESIS.md`, `PLAN.md`, or `EVIDENCE.md`, or substitute mutable
`latest` references for frozen identities. If execution is incomplete, report the exact gap and
hand the study back to `trading-operate-workflow` without choosing a favorable outcome.

## Evaluate against frozen rules

Trace every claim to the preregistered plan and exact evidence. Check stage completion, prohibited
deviations, missing identities, selection effects, invalidated assumptions, and the workflow's
definitions of:

- `pass`
- `fail`
- `insufficient-evidence`
- `indeterminate`

Use `insufficient-evidence` when required evidence is absent or unusable. Use `indeterminate` when
valid evidence exists but the frozen rules cannot distinguish pass from fail. Do not weaken gates
or repair the study retrospectively.

## Confirm and record the conclusion

Prepare a concise proposed outcome, evidence trace, limitations, and follow-up implications. Ask
the user to confirm this research-validity decision and obtain a stable reviewer identity before
writing `CONCLUSION.md` or completing the study.

After confirmation, write only `CONCLUSION.md`, then run:

```bash
uv run trading workflow study complete <study-path> \
  --outcome <pass|fail|insufficient-evidence|indeterminate> \
  --reviewed-by <identity>
uv run trading workflow validate --all
```

The command generates `COMPLETION.json`, freezing preregistration, evidence, conclusion, outcome,
time, and reviewer identity. Never edit completed artifacts. New evidence requires a new study,
linked with `revisits` when appropriate.

## Route process defects correctly

When evidence exposes a defect in the workflow rather than the study, finish the study according
to its frozen rules and recommend `trading-author-workflow` to open a change. Do not edit the active
workflow or create a change from this skill.

## Finish

Report the study ID, pinned workflow version, validated evidence identities, confirmed outcome,
limitations, completion validation, and any separately recommended workflow change. Distinguish a
completed study result from downstream promotion or trading authorization.
