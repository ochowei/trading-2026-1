# Proposal

## Current problem

The v004 workflow correctly prevents data that influenced design, selection, thresholds, or
interpretation from being relabeled as clean Historical Evaluation. When an asset has incomplete
legacy selection history, a valid Historical screen therefore requires a future-only Forward
Selection Epoch and five later complete annual folds.

That protection creates a practical evidence gap. A newly frozen workflow-native candidate may be
fully reproducible and testable over many completed historical years, yet v004 has no formal label
or bounded stage for a preregistered retrospective challenge using data whose clean-holdout status
is unknown or known to be contaminated. Teams must either call all such analysis Development or
wait five years before obtaining any post-freeze challenge result. Calling the old data Historical
would overstate its evidentiary role; treating all completed-data analysis as informal loses useful
falsification evidence and encourages inconsistent local exceptions.

The problem applies across assets. It must not be solved by declaring every asset unpolluted,
ignoring incomplete trial history, or assuming that a researcher who avoids legacy documents has
restored an unseen outcome.

## Proposed workflow change

Create `strategy-forward-replication-research@v005` as a complete replacement for v004 and add an
optional `retrospective-confirmatory` checkpoint after candidate freeze and before clean Historical
qualification. Every asset may opt into the checkpoint. A study must first classify every proposed
evaluation period through an asset-specific clean-evidence audit:

- `verified-clean`: append-only evidence establishes that the outcomes did not influence strategy
  family choice, parameters, thresholds, selection, or interpretation, and the relevant trial
  history is complete;
- `known-contaminated`: evidence establishes that the outcomes influenced research; or
- `provenance-unknown`: cleanliness cannot be demonstrated, including incomplete legacy selection
  history.

Only `verified-clean` periods may enter Historical Evaluation. `known-contaminated` and
`provenance-unknown` periods may be used only as Development context or in the new retrospective
checkpoint. The default is fail closed: absence of clean evidence is `provenance-unknown`, never
`verified-clean`. The classification and exact session inventory must be frozen before checkpoint
outcome inspection and may not be improved after seeing results.

The retrospective checkpoint must preregister and freeze the exact candidate, distinct simpler
family baseline, finite positive trial budget, complete trial inventory, annual non-overlapping
folds, warmup, purge, embargo, execution dependencies, canonical sleeve, base and strictly adverse
stress costs, seeds, thresholds, stopping rules, and challenge set. Its minimum challenges mirror
Historical rigor: cash, baseline, exposure-matched random entries, family-wise selection
adjustment, parameter perturbations, delayed entry, worse costs/fills, missed entries, fold and
profit concentration, and relevant market regimes. Exact workflow, policy, data, definition,
manifest, result, provenance, and replay identities remain mandatory.

Passing the checkpoint records the bounded evidence status `retrospectively-supported`. It is not
`shadow-eligible`, `activation-eligible`, Active, Historical validation, a clean holdout, or live
authority. Failing a complete frozen checkpoint terminates that candidate for the study. Missing or
unverifiable evidence is `indeterminate`. If a retrospective outcome is used to alter a definition,
baseline, threshold, or interpretation, the changed research requires a new trial or study and the
viewed periods become Development context for that lineage.

A `retrospectively-supported` candidate may retain its exact frozen identity while waiting for a
separately registered, future-only Historical Evaluation. It may become `shadow-eligible` only
after satisfying every unchanged clean Historical gate. The retrospective result cannot satisfy,
offset, shorten, or waive any Historical fold, trade, benchmark, selection-adjustment, robustness,
or integrity requirement.

The replacement must also provide workflow-native registration and screen boundaries for
`src/trading/research_definitions/` identities. Neither retrospective nor Historical operation may
depend on the closed legacy `src/trading/experiments/` registry. Registration must resolve exact
research-definition and family-trial identities without accepting caller assertions or backdated
timestamps.

## Expected effect

All assets can obtain a formally governed, reproducible falsification result from completed data
without pretending that legacy exposure has been erased. Assets with demonstrably clean holdouts
retain the direct Historical path. Assets with contaminated or unknown provenance gain an honest
intermediate evidence status while still requiring future-only Historical evidence before Shadow.

The change also closes the current workflow-native qualification tooling gap. It grants no study
approval, outcome, Shadow registration, broker access, order authority, release authority, or
permission to inspect quarantined data.
