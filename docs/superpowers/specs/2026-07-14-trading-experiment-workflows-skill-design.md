# Trading Experiment Workflow Skills Design

## Goal

Convert the eight workflows in `.claude/commands/` into eight independently discoverable project-local Codex skills without changing their trading rules, qualification thresholds, validation order, or required outputs.

## Location and branch

- Branch: `codex/convert-claude-commands-skill`
- Skills root: `.agents/skills/`
- Pull request: `#146`
- The skills remain version-controlled with this repository and are not installed globally.

## Structure

Create one skill folder per original command:

```text
.agents/skills/
├── evaluate-best/
├── launch-new-asset/
├── new-experiment/
├── pre-experiment-research/
├── rebuild-followup/
├── run-experiment/
├── update-experiment-docs/
└── validate-experiment/
```

Each folder contains a self-contained `SKILL.md` and `agents/openai.yaml`. Put the converted workflow directly in its `SKILL.md`; each workflow is below the 500-line limit and needs no extra reference layer. Remove the `trading-experiment-workflows` router so the catalog contains exactly the eight actionable entries.

Cross-workflow delegation uses explicit skill names:

- `rebuild-followup` invokes `$evaluate-best` sequentially for each ticker.
- `run-experiment` invokes `$update-experiment-docs` only after user confirmation.
- `launch-new-asset` directs existing assets to `$new-experiment`.

## Conversion rules

Preserve each source command's ordered steps, stopping conditions, thresholds, output fields, confirmation gates, and mutation boundaries. Apply only these Codex adaptations:

- Interpret the user's natural-language request instead of `$ARGUMENTS`.
- Resolve experiment IDs and module names using repository files or `uv run trading list`.
- Replace Claude slash-command and Skill-tool calls with explicit `$skill-name` delegation.
- Resolve asset documents as `src/trading/experiments/EXPERIMENTS_<TICKER>.md` rather than using a four-asset hard-coded map.
- Keep sequential execution where workflows share files, especially `rebuild-followup`.
- Require reading `CLAUDE.md` before executing every workflow.

## Triggering and interface

Each skill name matches the original command filename, such as `evaluate-best` and `rebuild-followup`. Each description contains only that workflow's triggering conditions, without angle-bracket placeholders, so explicit `$skill-name` invocation and narrow implicit matching both work. Each `agents/openai.yaml` provides a matching display name, short description, and default prompt.

Codex uses `$evaluate-best`-style skill invocation. These are not Claude-style `/evaluate-best` slash commands.

## Validation

Follow skill-authoring RED/GREEN verification:

1. Use the user's observed catalog state and a fresh-session catalog check to establish RED: `$evaluate-best` and `$rebuild-followup` are absent while only the router exists.
2. Convert, validate, and catalog-test one skill at a time before creating the next.
3. Run `quick_validate.py` on all eight skill folders.
4. Assert that `.agents/skills` contains exactly the eight expected project skills and no `trading-experiment-workflows` router.
5. Check that every source command maps to one `SKILL.md` and no `$ARGUMENTS`, Claude slash invocation, or Skill-tool syntax remains.
6. Forward-test `$evaluate-best`, `$rebuild-followup`, and one implicit natural-language request in fresh sessions without supplying filesystem paths or allowing project mutations.
7. Run project lint/format checks, inspect the final diff, and obtain independent review before pushing to PR #146.

## Scope

This revision changes only repository Codex skills and their design/plan documentation. It keeps `.claude/commands/` unchanged, does not alter trading code, does not run backtests, and does not change experiment documentation.
