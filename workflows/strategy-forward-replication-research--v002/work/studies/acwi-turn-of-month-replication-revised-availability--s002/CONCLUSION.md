# Conclusion: ACWI Turn-of-Month Replication — Corrected Availability

## Outcome

`indeterminate`

## Evidence trace

The study was validly preregistered and reached `awaiting-review`. The pinned workflow definition,
hypothesis, and plan SHA-256 values match `PREREGISTRATION.json`, and all four reported Development
result SHA-256 values match the immutable result files. Each associated snapshot independently
passes `trading data verify`, is capped at `2020-12-31`, and preserves its exact data, definition,
policy-set, and canonical-sleeve identities.

Direct recomputation from canonical completed trades confirms 143 trades for each candidate and the
reported decisive stress-gate failures:

- `enter-minus-two-hold-five`: stress return `-25.0062%`, profit factor `0.8073`, maximum drawdown
  `-43.8624%`;
- `enter-minus-one-hold-five`: stress return `-15.4597%`, profit factor `0.8881`, maximum drawdown
  `-38.6175%`;
- `enter-month-end-hold-five`: stress return `-17.1307%`, profit factor `0.8692`, maximum drawdown
  `-42.2878%`.

Those complete Development metrics would otherwise trigger the frozen no-eligible-candidate
`fail` stopping rule without Historical inspection. However, the frozen plan also requires every
formal observation to record its exact workflow/orchestration identity and execution command. The
study evidence, result artifacts, and definition snapshots do not preserve the execution command or
an observation-level binding demonstrating that each run resolved the pinned v002 workflow release.
Because the hypothesis assigns missing identity or reproducibility evidence to `indeterminate`, the
numerical failure cannot override that integrity rule.

## Limitations and follow-up

No 2021-or-later Historical outcome was inspected, and the intentionally absent Historical and
robustness evidence is not an evidence gap because Development reached its stopping condition. The
failed pre-repair M-2 attempt remains visible as an immutable failed semantic fingerprint within the
trial budget. The evidence summary's concentration statement is also ambiguous for stress results:
recomputation gives positive-profit concentration above 50% for M-2 and M0, reinforcing numerical
ineligibility but not curing the identity defect.

Advancement stops and this study confers no `shadow-eligible`, activation, or trading authority. If
already-existing immutable command and workflow-binding evidence can be located, it may be assessed
without recreating evidence; otherwise this terminal `indeterminate` result stands. Any newly
produced evidence requires a new study with an exact `revisits` link. Separately, the workflow
authoring process should clarify whether the Development positive-profit concentration gate is
evaluated under base, stress, or both scenarios.
