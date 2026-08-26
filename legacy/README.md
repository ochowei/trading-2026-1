# Legacy archive

This repository-level archive preserves retired source material that remains useful for inspection
or reproducibility. It is not an extension point for new research.

## Experiments

`experiments/` contains the closed `ticker_NNN_description` experiment inventory. The physical
packages live outside the installable `src/` tree, but a repository checkout keeps their historical
`trading.experiments.<experiment_name>` import identities for read-only diagnostics, reproducibility,
and fail-closed exit handling of any pre-existing positions.

Legacy research execution is retired. `trading legacy run`, `analyze`, `followup-backtest`,
`result evaluate`, `result registry seed`, and `data snapshot --experiment` reject every request.
Former top-level `list`, `run`, `followup-backtest`, `compare`, `result`, `analyze`, and `sync-docs`
spellings have been removed; argparse rejects them. Read-only archive inspection uses the explicit
`trading legacy ...` namespace.
The compatibility imports do not authorize new execution, observation, ranking, qualification,
promotion, or result publication.

Do not add or rename an experiment package here. New outcome-relevant research belongs under a
released workflow and `src/trading/research_definitions/`.

`experiment-overviews/` contains the archived `EXPERIMENTS_<TICKER>.md` tables and AI context that
formerly lived in the installable package tree. They are historical navigation and evidence only;
new workflow studies record their own plans, evidence, and conclusions instead of extending these
overviews.

`templates/experiment/` preserves the former legacy package template for historical inspection. It
is intentionally outside both the installable package tree and the auto-discovery path and must not
be used to create a new research identity.

## Results

`results/` preserves every retired legacy result class: the last retained `latest.json` files,
immutable snapshot manifests, retained formal run payloads, older legacy-schema results,
superseded result-directory names, and explicitly unreferenced historical runs under
`<experiment>/history/`. These files are read-only archival records.

Diagnostic comparison and explicit result-status queries may read an archived `latest.json`.
Archived results never participate in freshness, experiment evaluation or ranking, new followup
entries, Shadow/Active authorization, qualification, or formal evidence verification. No writer may
create or update a legacy result. Existing followup positions may use frozen strategy compatibility
only to produce fail-closed exit handling; retirement must never open or promote a new position.

Historical references to the former flat or `results/experiment-results/` paths resolve through
`results/registries/path-migrations.json`. The v010 retirement adds at most one byte-identical,
SHA-256-verified hop after a v009 categorized mapping and fails closed on drift, missing terminal
bytes, cycles, or longer chains.

The related identity is recorded for historical navigation, not as a claim that the archived result
has the same semantics as the final package occupying that numbered identity.

## Archived agent workflows

`claude/commands/` and `agent-skills/` preserve the former Claude command definitions and their
matching Codex skills for the closed legacy experiment workflow. They are archival copies only and
are intentionally outside the active `.claude/` and `.agents/skills/` discovery paths. New research
must use a released workflow and `trading-operate-workflow`.

### Superseded result-directory names

| Archived result directory | Related archived identity or disposition |
|---|---|
| `copx_002_drawdown_wr` | `copx_002_deep_drawdown` (COPX-002) |
| `dia_005_tighter_sl` | `dia_005_extreme_entry` (DIA-005) |
| `gld_mean_reversion` | `gld_001_mean_reversion` (GLD-001) |
| `gld_optimized_exit` | `gld_002_optimized_exit` (GLD-002) |
| `gld_trailing_stop` | `gld_003_trailing_stop` (GLD-003) |
| `iwm_005_short_hold` | `iwm_005_shorter_hold` (IWM-005) |
| `iwm_005_short_holding` | `iwm_005_shorter_hold` (IWM-005) |
| `soxl_006_optimized_exit` | `soxl_006_selective_oversold` (SOXL-006) |
| `soxl_006_wr_capped_drawdown` | `soxl_006_selective_oversold` (SOXL-006) |
| `tlt_004_breakout_trend` | `tlt_004_bb_squeeze_breakout` (TLT-004) |
| `tqqq_cap_gentle_entry` | `tqqq_009_cap_gentle_entry` (TQQQ-009) |
| `tqqq_cap_relaxed_entry` | `tqqq_002_cap_relaxed_entry` (TQQQ-002) |
| `tqqq_capitulation` | `tqqq_001_capitulation` (TQQQ-001) |
| `tsla_005_momentum_recovery` | `tsla_005_bb_squeeze_breakout` (TSLA-005) |
| `xbi_002_deep_pullback_wr` | Retired XBI-002 attempt-only result; no package remains in the closed inventory. |
