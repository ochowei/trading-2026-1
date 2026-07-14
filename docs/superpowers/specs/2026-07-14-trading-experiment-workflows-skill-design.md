# Trading Experiment Workflows Skill Design

## Goal

Convert the eight workflows in `.claude/commands/` into one project-local Codex skill without changing their trading rules, qualification thresholds, validation order, or required outputs.

## Location and branch

- Branch: `codex/convert-claude-commands-skill`
- Skill: `.codex/skills/trading-experiment-workflows/`
- The skill remains version-controlled with this repository and is not installed globally.

## Structure

Use a small router in `SKILL.md` and keep each workflow in a separate file under `references/`:

```text
.codex/skills/trading-experiment-workflows/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── evaluate-best.md
    ├── launch-new-asset.md
    ├── new-experiment.md
    ├── pre-experiment-research.md
    ├── rebuild-followup.md
    ├── run-experiment.md
    ├── update-experiment-docs.md
    └── validate-experiment.md
```

`SKILL.md` identifies the requested operation, reads only the matching reference, and follows `CLAUDE.md` as the authoritative project rule source. A workflow may load another reference when it explicitly delegates to that workflow, such as rebuilding followup using evaluate-best.

## Conversion rules

Preserve the source command's ordered steps, stopping conditions, thresholds, output fields, and mutation boundaries. Adapt only Claude-command-specific mechanics:

- Interpret the user's natural-language request instead of `$ARGUMENTS`.
- Resolve experiment IDs and module names using repository files or `uv run trading list`.
- Replace slash-command or Skill-tool invocation with a direct link to the corresponding reference workflow.
- Resolve an asset document as `src/trading/experiments/EXPERIMENTS_<TICKER>.md` rather than limiting support to a hard-coded four-asset map.
- Keep sequential execution where shared files could conflict, especially `rebuild-followup`.
- Do not duplicate the full project rules from `CLAUDE.md`; instruct Codex to read it first.

## Triggering and interface

Name the skill `trading-experiment-workflows`. Its description will cover research, creation, launch, execution, validation, documentation updates, best-strategy evaluation, and followup rebuilding for this repository. `agents/openai.yaml` will expose a concise display name, description, and default prompt generated from the completed skill.

## Validation

Follow skill-authoring RED/GREEN verification:

1. Run a baseline routing scenario without exposing the new skill and record missing project-specific behavior.
2. Initialize the skill using `skill-creator` tooling.
3. Run `quick_validate.py` on the completed folder.
4. Check that every source command maps to exactly one reference and that no Claude-only `$ARGUMENTS` or slash-command invocation remains.
5. Forward-test representative read-only and mutating scenarios with the new skill available, without allowing the test to modify live project files.
6. Inspect the final diff and repository status.

## Scope

This change creates only the Codex skill and its design documentation. It does not delete or edit `.claude/commands/`, alter trading code, run backtests, or change experiment documentation.
