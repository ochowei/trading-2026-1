# Legacy archive

This repository-level archive preserves retired source material that remains useful for inspection
or reproducibility. It is not an extension point for new research.

## Experiments

`experiments/` contains the closed `ticker_NNN_description` experiment inventory. The physical
packages live outside the installable `src/` tree, but a repository checkout keeps their historical
`trading.experiments.<experiment_name>` import identities and legacy CLI execution available.

Do not add or rename an experiment package here. New outcome-relevant research belongs under a
released workflow and `src/trading/research_definitions/`.
