---
name: trading-experiment-workflows
description: Use when researching, creating, launching, running, validating, documenting, comparing, or selecting trading experiments in this repository, including rebuilding the followup strategy list.
---

# Trading Experiment Workflows

## Overview

Route trading-experiment lifecycle requests to the repository's established workflow. Keep detailed procedures in references so only the selected workflow enters context.

## Route the request

1. Read `CLAUDE.md` before taking action.
2. Select exactly one primary workflow from the table.
3. Read the selected reference completely before acting.
4. Load another reference only when the selected workflow explicitly delegates to it.
5. Treat direct user instructions as higher priority than the workflow.

| User intent | Read |
|---|---|
| Research an asset before proposing an experiment | [references/pre-experiment-research.md](references/pre-experiment-research.md) |
| Create the next experiment for an existing asset | [references/new-experiment.md](references/new-experiment.md) |
| Launch the first experiment for a new asset | [references/launch-new-asset.md](references/launch-new-asset.md) |
| Run a backtest and summarize stability/results | [references/run-experiment.md](references/run-experiment.md) |
| Validate an experiment comprehensively | [references/validate-experiment.md](references/validate-experiment.md) |
| Synchronize experiment documentation with results | [references/update-experiment-docs.md](references/update-experiment-docs.md) |
| Rank an asset's experiments and update followup when qualified | [references/evaluate-best.md](references/evaluate-best.md) |
| Rebuild the entire followup strategy list | [references/rebuild-followup.md](references/rebuild-followup.md) |

## Shared rules

- Infer ticker, experiment ID, module name, and strategy concept from the user's request. Ask only when required input is missing or ambiguous.
- Resolve experiment IDs and module names from `uv run trading list` and the relevant `EXPERIMENTS_<TICKER>.md`; do not guess.
- Resolve asset documentation as `src/trading/experiments/EXPERIMENTS_<TICKER>.md` and verify the file exists.
- Preserve read-only boundaries and confirmation gates stated by the selected workflow.
- Never fabricate backtest results, freshness dates, or metrics.
- Keep code and documentation synchronized as required by `CLAUDE.md`.
