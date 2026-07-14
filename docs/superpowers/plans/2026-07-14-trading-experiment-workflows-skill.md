# Trading Experiment Workflows Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create one project-local Codex skill that faithfully exposes all eight workflows currently stored in `.claude/commands/`.

**Architecture:** Keep `SKILL.md` as a concise natural-language router and place each detailed workflow in a same-named file under `references/`. Preserve trading rules and outputs while replacing Claude command mechanics with Codex-native reference routing.

**Tech Stack:** Markdown Agent Skills, YAML UI metadata, Python skill-creator validation scripts, Git.

## Global Constraints

- Work only on branch `codex/convert-claude-commands-skill`.
- Create the skill at `.codex/skills/trading-experiment-workflows/`.
- Keep `.claude/commands/` unchanged.
- Treat `CLAUDE.md` as the authoritative project rules file.
- Preserve source workflow order, thresholds, stopping conditions, mutation boundaries, and output contracts.
- Do not alter trading code, run backtests, or update experiment results during skill conversion.
- Keep `SKILL.md` under 500 lines and load detailed workflows only when selected.

---

### Task 1: Establish the RED baseline

**Files:**
- Read: `.claude/commands/pre-experiment-research.md`
- Record evidence in the implementation session; do not add a repository artifact.

**Interfaces:**
- Consumes: a fresh agent with repository access but without the proposed skill path.
- Produces: a baseline report listing which required workflow elements were omitted or performed incorrectly.

- [ ] **Step 1: Run a fresh-context baseline scenario**

Use this exact task without mentioning `.claude/commands/` or the proposed skill:

```text
Prepare pre-experiment research for GLD in this repository. Do not modify files. Return the research brief you believe is appropriate, and list the files and commands you used.
```

- [ ] **Step 2: Compare the response with the source contract**

Check for all eight required brief sections, the `CLAUDE.md` reading order, `uv run trading freshness`, the four volatility categories, the six-month freshness warning, and the read-only boundary. Record at least one concrete omission or divergence to establish RED. If the baseline happens to satisfy every item, repeat with this exact routing scenario:

```text
Rebuild the followup strategy list for every asset in this repository. Explain the safe execution order before making changes, but do not modify files in this evaluation.
```

The expected baseline divergence is failure to discover the sequential per-asset evaluate-best contract or its qualification reporting requirements.

### Task 2: Initialize and implement the skill

**Files:**
- Create: `.codex/skills/trading-experiment-workflows/SKILL.md`
- Create: `.codex/skills/trading-experiment-workflows/agents/openai.yaml`
- Create: `.codex/skills/trading-experiment-workflows/references/evaluate-best.md`
- Create: `.codex/skills/trading-experiment-workflows/references/launch-new-asset.md`
- Create: `.codex/skills/trading-experiment-workflows/references/new-experiment.md`
- Create: `.codex/skills/trading-experiment-workflows/references/pre-experiment-research.md`
- Create: `.codex/skills/trading-experiment-workflows/references/rebuild-followup.md`
- Create: `.codex/skills/trading-experiment-workflows/references/run-experiment.md`
- Create: `.codex/skills/trading-experiment-workflows/references/update-experiment-docs.md`
- Create: `.codex/skills/trading-experiment-workflows/references/validate-experiment.md`

**Interfaces:**
- Consumes: natural-language requests about this repository's experiment lifecycle.
- Produces: exactly one selected workflow reference, with nested loading only when that workflow explicitly delegates to another.

- [ ] **Step 1: Initialize the skill skeleton**

Run:

```bash
python3 /Users/william/.codex/skills/.system/skill-creator/scripts/init_skill.py trading-experiment-workflows \
  --path .codex/skills \
  --resources references \
  --interface 'display_name=Trading Experiment Workflows' \
  --interface 'short_description=Run this repository’s trading experiment workflows' \
  --interface 'default_prompt=Use $trading-experiment-workflows to manage a trading experiment workflow in this repository.'
```

Expected: the skill directory, `SKILL.md`, `agents/openai.yaml`, and an empty `references/` directory are created.

- [ ] **Step 2: Replace the generated router**

Write `SKILL.md` with only `name` and `description` frontmatter. The description must start with `Use when` and cover research, experiment creation or launch, backtest execution, validation, documentation synchronization, best-strategy selection, and followup rebuilding in this repository. The body must require reading `CLAUDE.md`, map each user intent to one reference filename, require reading the selected reference completely, and forbid loading unrelated references.

- [ ] **Step 3: Convert the eight source commands**

For each `.claude/commands/<name>.md`, create `references/<name>.md` and preserve its ordered procedure and output contract. Apply these exact mechanical adaptations:

```text
$ARGUMENTS                         -> infer the target from the user's request; ask only when required information is absent
/evaluate-best <TICKER>           -> read and execute references/evaluate-best.md for that ticker
/new-experiment                   -> direct the user to the new-experiment workflow
Skill tool invocation             -> direct execution of the linked reference workflow
four-item ticker/document mapping -> src/trading/experiments/EXPERIMENTS_<TICKER>.md, verified to exist
```

Retain sequential processing in `rebuild-followup.md`. Retain confirmation before scaled-parameter implementation in `launch-new-asset.md`. Retain the read-only boundary in `pre-experiment-research.md`.

- [ ] **Step 4: Verify interface metadata**

Read `agents/openai.yaml` and confirm it contains exactly the chosen `display_name`, `short_description`, and `default_prompt`, with no icons or brand fields.

- [ ] **Step 5: Commit the implementation**

```bash
git add .codex/skills/trading-experiment-workflows
git commit -m "feat: add Codex trading experiment workflows skill"
```

### Task 3: Validate and forward-test the skill

**Files:**
- Validate: `.codex/skills/trading-experiment-workflows/SKILL.md`
- Validate: `.codex/skills/trading-experiment-workflows/agents/openai.yaml`
- Validate: `.codex/skills/trading-experiment-workflows/references/*.md`

**Interfaces:**
- Consumes: the completed project-local skill.
- Produces: validator output, static conversion checks, and GREEN forward-test evidence.

- [ ] **Step 1: Run the official validator**

Run `quick_validate.py` in an environment containing PyYAML. If the project environment lacks PyYAML, use an ephemeral `uvx --with pyyaml` invocation without changing project dependencies:

```bash
UV_CACHE_DIR=/tmp/uv-cache uvx --with pyyaml python \
  /Users/william/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .codex/skills/trading-experiment-workflows
```

Expected: `Skill is valid!`

- [ ] **Step 2: Run static conversion checks**

```bash
test "$(find .codex/skills/trading-experiment-workflows/references -type f -name '*.md' | wc -l | tr -d ' ')" = "8"
! rg -n '\$ARGUMENTS|Skill tool|/evaluate-best|/new-experiment' .codex/skills/trading-experiment-workflows
git diff --check HEAD^ HEAD
```

Expected: all commands exit successfully and the search prints no matches.

- [ ] **Step 3: Run the GREEN read-only scenario**

Give a fresh agent this exact task with the completed skill available:

```text
Use $trading-experiment-workflows at .codex/skills/trading-experiment-workflows to prepare pre-experiment research for GLD. Do not modify files. Explain which workflow reference you selected and return the required brief.
```

Expected: it selects only `pre-experiment-research.md`, respects the read-only constraint, and returns all eight brief sections.

- [ ] **Step 4: Run the GREEN mutation-plan scenario without writes**

Give a fresh agent this exact task:

```text
Use $trading-experiment-workflows at .codex/skills/trading-experiment-workflows to explain how you would rebuild followup for all assets. This is an evaluation: do not modify files or run backtests. State the required execution order and final validations.
```

Expected: it selects `rebuild-followup.md`, routes sequentially through `evaluate-best.md`, and includes lint, format, followup execution, count verification, and changes-versus-previous reporting.

- [ ] **Step 5: Inspect repository state**

```bash
git status --short --branch
git log -3 --oneline --decorate
```

Expected: the named feature branch is checked out, the implementation commit is present, and no unrelated files are changed.
