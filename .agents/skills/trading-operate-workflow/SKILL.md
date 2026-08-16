---
name: trading-operate-workflow
description: Start, preregister, run, pause, resume, cancel, and submit repository workflow studies for independent review. Use when creating a study under an active version in `workflows/`, advancing its frozen `PLAN.md` through workflow stages, routing stage work to existing `trading-*` skills, or recording exact evidence. Do not author workflow definitions, change a preregistered hypothesis or plan, or decide study outcomes.
---

# Operate Trading Workflows

Read `CLAUDE.md` and
`.agents/skills/trading-author-workflow/references/workflow-authoring-contract.md` completely before
starting. Read `workflows/README.md`, the exact released workflow version, and the study when one
already exists.

## Orient first

Resolve whether the user wants to start, preregister, run, pause, resume, cancel, or submit a study
for review. Inspect the current lifecycle state and run:

```bash
uv run trading workflow validate <study-or-version-path>
```

Do not operate a draft workflow version. Do not silently move a study to another workflow version.
Treat the workflow as the procedure definition and the study as one execution instance pinned to
that exact version.

Resolve and verify every policy pin from the workflow release before preregistration. New formal
trial source belongs under `src/trading/research_definitions/`, never the closed
`src/trading/experiments/` inventory. Formal evidence must include the composite policy-set identity
and the immutable Research Definition Snapshot identity.

## Start a study

Search the active version, generated index, repository references, and Git history for similar
studies before creating another. Confirm the research question, concise study slug, title, stable
creator identity, required route for capability-scoped releases, and optional exact `revisits`
path. Then run:

```bash
uv run trading workflow study init <active-version-path> \
  --slug <study-slug> --title <title> --created-by <identity> \
  --route <clean-historical|retrospective-confirmatory|study-time-retrospective>
```

Add `--revisits workflows/.../<prior-study>--sNNN` when restarting or revisiting prior research.
Let the CLI allocate the next never-reused local `Sxxx`.

Study IDs are scoped to the exact workflow version, not to the workflow family or research
lineage. Determine numbering only from studies already present under the target version and never
predict an ID from a prior version. The first study under a replacement version is `S001` even when
it revisits `S003` from the superseded version; preserve that lineage only through the exact
`revisits` path. Prefer saying “the next CLI-allocated study” before initialization, then report the
ID returned by the CLI. Never use a research-round ordinal such as “fourth attempt” as an `Sxxx`.

## Prepare and preregister

Guide the user through unresolved hypothesis and plan decisions one at a time. Complete
`HYPOTHESIS.md` and `PLAN.md` with falsifiable claims, exact inputs, frozen stage mapping, metrics,
outcome rules, deviations, and stopping rules. For a capability-scoped release, also complete the
generated `QUALIFICATION_SPEC.json`: exact route, repository-relative registries, provenance,
whole-year calendars and warmup bounds, complete family/roles/source hashes, shared sources,
composite policy-set release/config identities, base/stress costs, immutable snapshot/formal-
observation semantics, execution and benchmark budgets, and distinct typed challenge
identities/targets/gates. Keep
`EVIDENCE.md` and `CONCLUSION.md` untouched.

Show the complete frozen summary and obtain explicit human approval with a stable identity before:

```bash
uv run trading workflow study preregister <study-path> --approved-by <human-id>
```

Never modify `HYPOTHESIS.md` or `PLAN.md` after preregistration. Cancel the study and create a new
one with `revisits` when the research design must change.

## Execute the frozen plan

Start or resume only through the CLI:

```bash
uv run trading workflow study transition <study-path> --to running --by <identity>
```

For the first capability-scoped Development transition, obtain a separate current human stage
authorization from the preregistered owner and include it explicitly:

```bash
uv run trading workflow study transition <study-path> --to running --by <identity> \
  --approved-by <human-id>
```

This authorizes Development only. It does not authorize Evaluation, Shadow, broker access, or
orders. After Development has produced the preregistered complete family and selection, prepare an
outcome-derived JSON object containing exactly `selected_candidate`, `family_baseline`, and
`complete_family`. Each family member contains `source_identity`, `trial_id`, and
`definition_fingerprint`; do not add approval times, identities, digests, or scope fields. Obtain
the preregistered human owner's separate candidate-freeze approval and run:

```bash
uv run trading workflow study freeze-candidate <study-path> \
  --selection <development-selection.json> --approved-by <human-id>
```

The guarded command supplies the current time and exact study digests and writes
`CANDIDATE_FREEZE.json` add-only. Never hand-author, backdate, replace, or repair that file. For a
capability-scoped clean or retrospective route, first compile provider-free with the exact-study
path; only after separate explicit authority for the registered Evaluation operation may the same
public path mutate registries:

```bash
uv run trading qualification plan register-study --study <study-path> --dry-run
uv run trading qualification plan register-study --study <study-path> \
  --approved-by <human-id> --contamination-declaration <exact-declaration>
```

Do not use generic `qualification plan register` for these studies. Do not execute any
outcome-relevant stage merely because preregistration, Development authorization, candidate freeze,
or a dry-run exists; each authority remains narrow and stage-specific.

Follow the pinned `WORKFLOW.md` stage order and gates. For each stage, use the matching repository
skill from `AGENTS.md`; do not duplicate experiment research, creation, execution, validation, or
ranking logic inside this skill. Record exact immutable manifests, snapshot IDs, complete commit
SHAs, checksums, commands, failures, and declared deviations in `EVIDENCE.md`.

Do not repair an unfavorable result, weaken a gate, reinterpret an outcome, or omit missing
evidence. Never store private ledger data, broker exports, holdings, credentials, or raw private
trading data under `workflows/`.

## Pause, resume, or cancel

Pause or cancel with a concrete reason:

```bash
uv run trading workflow study transition <study-path> --to paused \
  --by <identity> --reason <reason>
uv run trading workflow study transition <study-path> --to cancelled \
  --by <identity> --reason <reason>
```

Resume a paused study only when the frozen plan remains valid. If its workflow version has ceased
to be active, remain paused or cancelled unless the version-impact decision explicitly permits a
new study under the replacement version.

## Submit for independent review

When every planned stage has reached a recorded terminal result, finish `EVIDENCE.md`, leave
`CONCLUSION.md` unchanged, and run:

```bash
uv run trading workflow study transition <study-path> \
  --to awaiting-review --by <identity>
```

Stop there. Use `trading-evaluate-study` for judgment and completion. If a reviewer returns the
study, record the reason while transitioning back to `running`; add only evidence allowed by the
frozen plan.

For `study-time-retrospective`, record and submit the exact terminal evidence package required by
the pinned workflow, but do not infer its terminal outcome. The operator never turns missing or
unverifiable fixed-checkpoint evidence into `insufficient-evidence`; the independent reviewer
applies the released fixed mapping.

## Finish

Run sync and full validation after every mutation. Report the pinned workflow version, study ID,
current state, commands and worker skills used, exact new evidence, deviations, and the next legal
action. Never claim an awaiting-review study has passed or failed.
