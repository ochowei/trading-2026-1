# Legacy archive

This repository-level archive preserves retired source material that remains useful for inspection
or reproducibility. It is not an extension point for new research.

## Experiments

`experiments/` contains the closed `ticker_NNN_description` experiment inventory. The physical
packages live outside the installable `src/` tree, but a repository checkout keeps their historical
`trading.experiments.<experiment_name>` import identities and legacy CLI execution available.

Do not add or rename an experiment package here. New outcome-relevant research belongs under a
released workflow and `src/trading/research_definitions/`.

## Results

`results/` preserves legacy-schema `latest.json` files for the closed experiment inventory,
superseded result-directory names that no longer match a discoverable identity, and explicitly
unreferenced historical runs under `<experiment>/history/`. These files are read-only archival
records. Diagnostic comparison, explicit result-status queries, and documentation checks may fall
back to a legacy latest file when the categorized canonical result store has no current result.

Archive fallback never participates in freshness, experiment evaluation or ranking, followup,
Shadow/Active authorization, qualification, or formal evidence verification. All result writers
publish only under repository-root `results/`; they never create or update this archive. When both
locations contain the same latest identity, the canonical result wins and diagnostics report the
duplicate. Files under `history/` are navigation-only and never participate in fallback.

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
