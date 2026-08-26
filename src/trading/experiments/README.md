# Historical import facade

This directory is `legacy-compat`, not an active research extension point. `__init__.py` extends the
package search path to repository-root `legacy/experiments/` so frozen imports such as
`trading.experiments.spy_007_trend_pullback` remain reproducible.

Do not add modules, packages, templates, or research identities here. New formal research belongs
under `trading.research_definitions` and requires a released workflow plus a preregistered study.
The repository ownership check permits only this README and the historical `__init__.py` facade.
