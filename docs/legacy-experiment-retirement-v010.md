# Legacy Experiment Retirement v010

## Decision

The legacy experiment research system is terminally retired. Its source inventory and final
artifacts remain inspectable for reproducibility, but no public command may execute a legacy
experiment, inspect new outcomes, publish a result, refresh a candidate, change legacy trial
inventory, qualify or promote a legacy strategy, or use an archived result to authorize a new
position.

New outcome-relevant research uses a released workflow, exact released policies, a preregistered
Study, and a permanent definition under `src/trading/research_definitions/`.

## Retired public operations

The following commands remain parseable only to return the same fail-closed retirement error:

| Command | Retired capability |
|---|---|
| `trading legacy run` in every mode | Legacy online, offline, ephemeral, and migration execution. |
| `trading legacy analyze` | Rolling outcome analysis of a legacy strategy. |
| `trading legacy followup-backtest` | New portfolio backtests of the legacy followup set. |
| `trading result evaluate` | Data refresh, rerun, and candidate ranking. |
| `trading result registry seed` | Mutation of the legacy trial inventory. |
| `trading data snapshot --experiment` | Definition capture and snapshot preparation for a legacy experiment. |
| `trading legacy sync-docs` | Mutation of frozen legacy experiment result documentation. |
| `trading followup-state init`, `resume`, `shadow`, `activate` | Initialization or expansion of legacy new-entry authority. |

`trading legacy list`, `trading legacy compare`, and `trading legacy result status` remain read-only
archive diagnostics. Their former top-level spellings are deprecated compatibility aliases for at
least one release cycle and add only a stderr warning.
They do not restore authority or make an archived result qualifiable.

## Result archive

The former `results/experiment-results/<experiment>/` tree is removed. Its final 36 tracked
artifacts are preserved byte-for-byte under `legacy/results/<experiment>/`:

- the last retained `latest.json` values;
- immutable snapshot manifests;
- explicitly retained formal online/offline result payloads; and
- migration-preparation snapshots that never became current results.

`legacy/results/` is read-only. No code path may create or update a file there. Archived results are
not inputs to freshness, evaluation, ranking, qualification, Shadow, Active promotion, formal
evidence verification, or followup new-entry authorization.

## Historical path compatibility

The v009 migration registry remains append-only. Every original v009 entry is preserved unchanged.
For each artifact retired from `results/experiment-results/`, v010 appends one mapping from that
categorized path to the exact archived path with the same SHA-256 and artifact class.

Schema 2 resolution permits no more than two hops:

```text
historical flat results path
    -- v009, SHA-256 fixed --> results/experiment-results/<experiment>/<artifact>
    -- v010, same SHA-256 --> legacy/results/<experiment>/<artifact>
```

A direct request for the former categorized path uses only the v010 hop. Resolution fails closed
when a chain exceeds two hops, contains a cycle, changes digest, lacks a unique mapping, has no
terminal file, or finds terminal bytes that differ from the recorded SHA-256. Frozen workflow,
Study, result, and registry bytes are not rewritten to replace their historical path strings.

## Followup and open-position safety

Retirement removes new-entry authority; it does not abandon an already open manual position.
Checkout-only strategy compatibility may remain available to calculate or report an exit for a
position whose ownership is already recorded in the verified manual ledger. Archived results can
never make `result_valid` true, so a missing or inconsistent lifecycle/result state remains
no-new-entry.

Existing followup lifecycle state may be inspected, paused, moved into retirement, and completed
only after the verified ledger is flat. Initialization, resume, Shadow registration, and Active
promotion are rejected.

## Invariants

- `results/experiment-results/` does not exist and must not be recreated.
- `legacy/results/` is terminal and read-only.
- The legacy package inventory remains closed; source compatibility is not an execution authority.
- No legacy command writes results, snapshots, observations, rankings, qualification evidence, or
  lifecycle promotion state.
- Archived `latest.json` is a diagnostic convenience, not current evidence.
- Workflow-native research and its canonical `results/` namespaces are unaffected.
- Retirement does not authorize broker access, orders, Study execution, workflow release, or any
  outcome decision.

## Verification

Repository verification must cover:

1. all v009 and v010 path mappings resolving to exact tracked terminal bytes;
2. absence of `results/experiment-results/`;
3. fail-closed behavior for every retired CLI operation and legacy result writer;
4. read-only archive status and comparison behavior;
5. workflow validation without changes to frozen workflow or Study files; and
6. Ruff, focused result/path/CLI tests, and the full test suite.
