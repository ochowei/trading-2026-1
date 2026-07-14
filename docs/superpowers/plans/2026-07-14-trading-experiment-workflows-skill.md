# Standalone Trading Experiment Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single router with eight independently discoverable repository skills matching the original Claude command names.

**Architecture:** Move each already-converted workflow from the router's `references/` directory into its own self-contained `SKILL.md`. Give every skill narrow trigger metadata and UI metadata, validate each before creating the next, then remove the obsolete router.

**Tech Stack:** Markdown Agent Skills, YAML UI metadata, Python skill-creator validation scripts, Git.

## Global Constraints

- Work only on branch `codex/convert-claude-commands-skill` and update PR `#146`.
- Create each manifest skill under its exact `.agents/skills/<name>/` directory so Codex discovers it from the repository root.
- Keep `.claude/commands/` unchanged.
- Preserve workflow order, thresholds, stopping conditions, mutation boundaries, confirmation gates, and output contracts.
- Require every workflow to read `CLAUDE.md` before acting.
- Replace cross-workflow links with `$evaluate-best`, `$new-experiment`, or `$update-experiment-docs` as applicable.
- Do not alter trading code, run backtests, or update experiment results.
- Validate and catalog-test each skill before creating the next.

## Skill manifest

| Skill | Display name | Short description | Trigger description |
|---|---|---|---|
| `evaluate-best` | Evaluate Best Experiments | Rank one asset’s experiments for trading followup | Use when ranking experiments for one asset, checking followup qualification, or updating that asset's entry in `src/trading/followup.py`. |
| `launch-new-asset` | Launch New Asset | Create the first experiment for a new trading asset | Use when creating the first experiment and experiment documentation for a ticker that has no existing experiments. |
| `new-experiment` | New Trading Experiment | Create the next experiment for an existing asset | Use when creating the next numbered trading experiment for an asset that already has experiments. |
| `pre-experiment-research` | Pre-Experiment Research | Research an asset before designing an experiment | Use when gathering read-only asset context, prior results, prohibited approaches, parameter coverage, and freshness before experiment design. |
| `rebuild-followup` | Rebuild Trading Followup | Rebuild followup strategies across every experiment asset | Use when rebuilding the entire `STRATEGIES` list in `src/trading/followup.py` across all assets. |
| `run-experiment` | Run Trading Experiment | Run and summarize a trading experiment backtest | Use when running one trading experiment, analyzing rolling stability, and summarizing its latest results. |
| `update-experiment-docs` | Update Experiment Docs | Sync experiment documentation with backtest results | Use when synchronizing an asset's experiment overview document and AI context with existing backtest results. |
| `validate-experiment` | Validate Trading Experiment | Validate code, results, and docs for one experiment | Use when comprehensively validating one experiment's code style, registration, backtest, metrics, documentation, and execution model. |

---

### Task 1: Establish the catalog RED baseline

**Files:**
- Read: `.agents/skills/trading-experiment-workflows/SKILL.md`

**Interfaces:**
- Consumes: a fresh agent's startup skill catalog.
- Produces: evidence that only `trading-experiment-workflows` exists and `$evaluate-best` / `$rebuild-followup` are absent.

- [ ] **Step 1: Run the exact fresh-context catalog test**

```text
Without searching the filesystem, report whether these exact skills are present in your startup catalog: trading-experiment-workflows, evaluate-best, rebuild-followup.
```

Expected RED: `trading-experiment-workflows` is present; `evaluate-best` and `rebuild-followup` are absent.

### Task 2: Create and validate all eight standalone skills sequentially

**Files:**
- Create: `.agents/skills/evaluate-best/`, `.agents/skills/launch-new-asset/`, `.agents/skills/new-experiment/`, `.agents/skills/pre-experiment-research/`
- Create: `.agents/skills/rebuild-followup/`, `.agents/skills/run-experiment/`, `.agents/skills/update-experiment-docs/`, `.agents/skills/validate-experiment/`
- Move each same-named file from `.agents/skills/trading-experiment-workflows/references/` into the target folder as `SKILL.md`

**Interfaces:**
- Consumes: one converted workflow reference and its row in the skill manifest.
- Produces: one catalog-discoverable skill with the same workflow and matching UI metadata.

For each manifest row in order, complete every step and validator before starting the next row.

- [ ] **Step 1: Initialize the current skill**

Run these commands in order, completing Steps 2 and 3 after each command before running the next:

```bash
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/init_skill.py evaluate-best --path .agents/skills --interface 'display_name=Evaluate Best Experiments' --interface 'short_description=Rank one asset’s experiments for trading followup' --interface 'default_prompt=Use $evaluate-best to rank one asset’s experiments and update followup when qualified.'
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/init_skill.py launch-new-asset --path .agents/skills --interface 'display_name=Launch New Asset' --interface 'short_description=Create the first experiment for a new trading asset' --interface 'default_prompt=Use $launch-new-asset to create the first experiment for a new asset.'
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/init_skill.py new-experiment --path .agents/skills --interface 'display_name=New Trading Experiment' --interface 'short_description=Create the next experiment for an existing asset' --interface 'default_prompt=Use $new-experiment to create the next experiment for an existing asset.'
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/init_skill.py pre-experiment-research --path .agents/skills --interface 'display_name=Pre-Experiment Research' --interface 'short_description=Research an asset before designing an experiment' --interface 'default_prompt=Use $pre-experiment-research to prepare a read-only asset research brief.'
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/init_skill.py rebuild-followup --path .agents/skills --interface 'display_name=Rebuild Trading Followup' --interface 'short_description=Rebuild followup strategies across every experiment asset' --interface 'default_prompt=Use $rebuild-followup to rebuild followup strategies for all assets.'
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/init_skill.py run-experiment --path .agents/skills --interface 'display_name=Run Trading Experiment' --interface 'short_description=Run and summarize a trading experiment backtest' --interface 'default_prompt=Use $run-experiment to run and summarize one trading experiment.'
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/init_skill.py update-experiment-docs --path .agents/skills --interface 'display_name=Update Experiment Docs' --interface 'short_description=Sync experiment documentation with backtest results' --interface 'default_prompt=Use $update-experiment-docs to synchronize experiment documentation with results.'
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/init_skill.py validate-experiment --path .agents/skills --interface 'display_name=Validate Trading Experiment' --interface 'short_description=Validate code, results, and docs for one experiment' --interface 'default_prompt=Use $validate-experiment to comprehensively validate one trading experiment.'
```

Expected: the skill folder, generated `SKILL.md`, and `agents/openai.yaml` exist.

- [ ] **Step 2: Replace the generated body with the converted workflow**

Move the current same-named router reference into the initialized skill folder as `SKILL.md`. Prepend the exact `name` and `Trigger description` from the manifest as the only frontmatter fields, then add `Read CLAUDE.md completely before starting this workflow.` immediately after the title. For example, `evaluate-best` begins:

```yaml
---
name: evaluate-best
description: Use when ranking experiments for one asset, checking followup qualification, or updating that asset's entry in `src/trading/followup.py`.
---
```

Apply these exact cross-skill substitutions:

```text
[evaluate-best workflow](evaluate-best.md)                 -> `$evaluate-best`
[new-experiment workflow](new-experiment.md)               -> `$new-experiment`
[update-experiment-docs workflow](update-experiment-docs.md) -> `$update-experiment-docs`
[run-experiment workflow](run-experiment.md)               -> `$run-experiment`
```

- [ ] **Step 3: Validate the current skill before continuing**

```bash
validate_skill() {
  UV_CACHE_DIR=/tmp/uv-cache UV_TOOL_DIR=/tmp/uv-tools uvx --with pyyaml python \
    /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$1"
}

validate_skill .agents/skills/evaluate-best
validate_skill .agents/skills/launch-new-asset
validate_skill .agents/skills/new-experiment
validate_skill .agents/skills/pre-experiment-research
validate_skill .agents/skills/rebuild-followup
validate_skill .agents/skills/run-experiment
validate_skill .agents/skills/update-experiment-docs
validate_skill .agents/skills/validate-experiment
```

Expected: `Skill is valid!`

Also verify the generated metadata contains exactly `display_name`, `short_description`, and `default_prompt` from the manifest/current command.

### Task 3: Remove the obsolete router

**Files:**
- Delete: `.agents/skills/trading-experiment-workflows/SKILL.md`
- Delete: `.agents/skills/trading-experiment-workflows/agents/openai.yaml`
- Delete: empty `.agents/skills/trading-experiment-workflows/` directories

**Interfaces:**
- Consumes: eight validated standalone skills and an empty router references directory.
- Produces: exactly eight project skill folders with no duplicate router trigger.

- [ ] **Step 1: Verify all workflow content moved successfully**

```bash
test "$(find .agents/skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')" = "9"
test ! -n "$(find .agents/skills/trading-experiment-workflows/references -type f -name '*.md' -print)"
```

Expected: eight standalone skills plus the router exist, and no reference workflow remains.

- [ ] **Step 2: Delete router metadata and instructions**

After deletion, assert:

```bash
test ! -e .agents/skills/trading-experiment-workflows
test "$(find .agents/skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')" = "8"
```

### Task 4: Verify discovery, parity, and project health

**Files:**
- Validate: `.agents/skills/*/SKILL.md`
- Validate: `.agents/skills/*/agents/openai.yaml`
- Confirm unchanged: `.claude/commands/*.md`

**Interfaces:**
- Consumes: all eight completed standalone skills.
- Produces: catalog, explicit invocation, implicit invocation, static, lint, format, and review evidence.

- [ ] **Step 1: Run all static checks**

```bash
expected='evaluate-best launch-new-asset new-experiment pre-experiment-research rebuild-followup run-experiment update-experiment-docs validate-experiment'
actual="$(find .agents/skills -mindepth 2 -maxdepth 2 -name SKILL.md -exec dirname {} \; | xargs -n1 basename | sort | tr '\n' ' ' | sed 's/ $//')"
test "$actual" = "$expected"
! rg -n '\$ARGUMENTS|Skill tool|(^|[[:space:]`(])/(evaluate-best|launch-new-asset|new-experiment|pre-experiment-research|rebuild-followup|run-experiment|update-experiment-docs|validate-experiment)([[:space:]`]|$)' .agents/skills
git diff --quiet origin/main -- .claude/commands
git diff --check origin/main
```

Expected: all commands exit `0` and the syntax scan prints no matches.

- [ ] **Step 2: Run fresh-session catalog GREEN**

```text
Without searching the filesystem, report whether these exact skills are present in your startup catalog: trading-experiment-workflows, evaluate-best, rebuild-followup, run-experiment, validate-experiment.
```

Expected: the four standalone skills are present and `trading-experiment-workflows` is absent.

- [ ] **Step 3: Run the explicit evaluate-best forward test without writes**

```text
Use $evaluate-best to explain how you would rank GLD experiments and decide whether the winner belongs in followup. This is an evaluation: do not modify files or run backtests.
```

Expected: it states the ranking order, all six qualification gates, existing-results behavior, and the rule that `followup.py` changes only when the best experiment qualifies.

- [ ] **Step 4: Run the explicit rebuild-followup forward test without writes**

```text
Use $rebuild-followup to explain the required rebuild order and qualification gates. This is an evaluation: do not modify files or run backtests.
```

Expected: it delegates sequentially to `$evaluate-best` and includes final lint, format, followup execution, strategy-count, and changes-versus-previous validation.

- [ ] **Step 5: Run the implicit research forward test without writes**

```text
Prepare the read-only pre-experiment research brief for GLD in this repository. State the selected skill and do not modify files.
```

Expected: implicit invocation selects `pre-experiment-research` and returns all eight brief sections without modifying files.

- [ ] **Step 6: Run project verification and review**

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check src/
UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check src/
git status --short --branch
```

Expected: Ruff reports no errors, 1708 files formatted, and only intended skill/plan changes remain before commit.

Request independent review against the updated design, fix all Critical/Important issues, then commit and push the branch to update PR `#146`.
