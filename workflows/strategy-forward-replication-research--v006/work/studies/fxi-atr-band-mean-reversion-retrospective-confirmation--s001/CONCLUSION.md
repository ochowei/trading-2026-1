# Conclusion: FXI ATR-Band Mean-Reversion Retrospective Confirmation

## Outcome

`indeterminate`

The required retrospective qualification screen did not compute or persist the frozen metrics,
gate results, selection adjustment, robustness evidence, or non-promotional disposition. No
complete performance gate can therefore be judged as passing or failing. This closed completed-data
checkpoint does not permit `insufficient-evidence`; under the preregistered v006 rules, the missing
and unverifiable required screen evidence is `indeterminate`.

## Evidence trace

- `PREREGISTRATION.json` pins `HYPOTHESIS.md`, `PLAN.md`, and
  `strategy-forward-replication-research@v006`; their SHA-256 identities validate exactly.
- `CANDIDATE_FREEZE.json` records human approval by `ochowei@gmail.com`, the selected candidate,
  distinct baseline, complete six-trial family, composite policy set, and the 2010-2014
  `retrospective-confirmatory` boundary classified `provenance-unknown`.
- Qualification plan
  `retrospective-plan-cd1888d05e1f5ff1274d433d0559bb9d506995938511f54c90053e2e7eff3fb1`
  freezes the exact retrospective checkpoint and six trial IDs. Its Development, warmup, and
  Evaluation inventories are unique, chronological, and pairwise disjoint.
- All six referenced manifests verify, and every frozen trial has exactly one succeeded, valid,
  offline observation. Their snapshot, definition, result, workflow-release, policy-set, Git, and
  checksum identities match `EVIDENCE.md`.
- The qualification registry has SHA-256
  `00ab9180531b37dc6eaa84bc7095fa41936bdedd92c51d8faa9ac7e6497fcb3a` and contains only the
  registered plan. It contains no `historical_screen` event, gate result, or disposition.
- The pinned verifier `src/trading/core/qualification.py`, SHA-256
  `bd3f820b42e1ce34cf6efa681e54b5f34d8be1014c7a04584b06d7d9d2b75762`, rejects incomplete
  selection history through `forward_selection_epoch` only and does not consume the plan's valid
  `retrospective_selection_checkpoint`. The recorded screen attempt consequently stopped before
  computation with `selection adjustment rejects incomplete trial registry history`.
- Because no complete gate failed, `fail` is unsupported. Because no complete screen passed,
  `pass` is unsupported. The frozen rules explicitly map missing or unverifiable required evidence
  to `indeterminate`.

## Limitations and follow-up

The unscreened trial observations do not support a strategy-performance conclusion. This study is
neither `retrospectively-supported` nor `retrospective-screen-failed` and grants no Historical,
Shadow, activation, order, or live-trading authority.

Repairing the pinned verifier and rerunning this study after exposure of the 2010-2014 outcomes
would change outcome-relevant orchestration after inspection. Those sessions cannot be reused as
confirmatory evidence for a changed lineage. The separate v004/S004 plan for sealed 2027-2031 clean
Historical Evaluation remains unchanged.

Open a workflow-authoring change to require provider-free end-to-end release validation from
retrospective plan registration through family-wise selection adjustment when prior selection
history is incomplete. Handle the verifier correction as a separate implementation change; do not
use it to repair this completed study retrospectively.
