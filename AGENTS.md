# AGENTS.md

## Repository purpose

This repository is a modular quantitative-trading research platform. It develops and compares
daily-bar strategies, validates them across in-sample, out-of-sample, and live periods, and turns
qualified experiments into manual Firstrade followup reports.

## Start here

Read [CLAUDE.md](CLAUDE.md) completely before working in this repository. It is the canonical
source for project rules, required documentation updates, and commands. Use
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) as the canonical repository map and file-ownership
guide. Keep details in those documents instead of duplicating them in this router.

## Task router

Use the matching repository skill for these workflows:

| Task | Skill |
|---|---|
| Research an asset before experiment design | `trading-pre-experiment-research` |
| Create the first experiment for a new ticker | `trading-launch-new-asset` |
| Create the next experiment for an existing ticker | `trading-new-experiment` |
| Run an experiment and analyze rolling stability | `trading-run-experiment` |
| Validate an experiment comprehensively | `trading-validate-experiment` |
| Synchronize experiment results and documentation | `trading-update-experiment-docs` |
| Rank one asset's experiments or update followup | `trading-evaluate-best` |
| Rebuild the complete followup strategy list | `trading-rebuild-followup` |
| Review, create, version, or release a repository research workflow | `trading-author-workflow` |
| Start, preregister, run, pause, or submit a workflow study for review | `trading-operate-workflow` |
| Independently assess evidence and conclude a workflow study | `trading-evaluate-study` |

For ordinary code changes, bug fixes, and reviews that do not match a skill, inspect the relevant
implementation and tests directly while following [CLAUDE.md](CLAUDE.md).

## Core entry points

- `src/trading/cli.py`: command-line interface and command dispatch
- `src/trading/core/`: shared data, strategy, backtest, analysis, and result infrastructure
- `src/trading/experiments/`: auto-discovered experiment packages and per-asset overviews
- `src/trading/followup.py`: selected strategies and manual order-report generation
- `src/trading/followup_backtest.py`: portfolio-level followup simulation
- `tests/`: automated tests for shared and followup behavior

## Non-negotiable guardrails

- Keep code and its related documentation synchronized.
- When adding, removing, moving, renaming, or repurposing a tracked file or directory, update
  `docs/ARCHITECTURE.md` in the same change. Also update it for new repeated file patterns, public
  entry points, generated artifacts, or local-only data boundaries. Routine additions that already
  fit a documented pattern do not need per-instance entries.
- Do not edit `pm/` unless the user explicitly designates the task as `HUMAN_PM_HELPER`.
- Use the required execution model for every non-grandfathered experiment.
- Preserve the freshness metadata when changing experiment context or cross-asset lessons.
