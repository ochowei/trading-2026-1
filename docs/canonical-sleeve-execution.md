# Canonical strategy-sleeve execution

Phase 4 provides one capital-constrained execution path for formal research evaluation and
`followup-backtest`. Strategy detectors and legacy backtesters still produce candidate trades;
`CanonicalSleeveEngine` decides which candidates one isolated sleeve can actually fund and turns
those executions into a daily equity ledger. Both formal research and followup construct a typed
`CanonicalSleeveInput` and call the same evaluator.

## Capital and position policy

Each strategy sleeve starts with declared capital. Research uses normalized capital `1.0`; the
followup portfolio assigns an equal fixed cash amount to each sleeve. Quantities may be fractional.
The engine:

- permits at most one open position;
- invests only that sleeve's available cash;
- never borrows or transfers capital between sleeves;
- never pyramids or rebalances during the evaluation interval;
- records an overlapping candidate as `skipped` with reason `position_already_open`.

The end-of-session ledger records cash, marked position value, equity, daily return, drawdown,
utilization, and open-position count. Drawdown and ranking metrics are anchored to initial sleeve
capital, so first-session execution costs cannot disappear from risk statistics.

## Event ordering

For each canonical session the engine applies this deterministic order:

1. process a scheduled `time_expiry` exit, allowing the released cash to fund a new entry;
2. process candidate entries in entry-date and signal-date order, skipping them while a position is
   open;
3. process non-expiry exits such as target or stop events;
4. mark any remaining position to the adjusted close and publish the daily ledger point.

An exit is `completed` only after its exit event is processed. A candidate whose declared exit lies
beyond the evaluation calendar remains `open` and is marked to market.

## Cost scenarios and ranking

Every research definition fingerprints a base and a strictly adverse stress policy. The current
defaults, expressed per side, are:

| Scenario | Entry slippage | Exit slippage | Fee |
| --- | ---: | ---: | ---: |
| Base | 5 bps | 5 bps | 1 bp |
| Stress | 20 bps | 20 bps | 2 bps |

The same candidate stream is run as gross, base-net, and stress-net. Entry quantity includes entry
slippage and fees, while exit cash includes exit slippage and fees. Formal ranking uses only the
base-net Sharpe calculated from the canonical daily equity path; gross and stress-net remain
evidence rather than alternate ranking choices.

Candidate prices retain the order-type, trigger, and event-order semantics produced by the
experiment backtester, but must be gross of slippage and fees. Followup creates a copy of each legacy
backtester and sets its `slippage_pct` to zero while producing candidates; the original backtester is
not mutated. Formal research runners have the same gross-candidate contract. The canonical policy is
therefore the only cost layer applied to gross/base/stress scenarios. Changing candidate construction
or a cost policy requires a new definition fingerprint.

## Result evidence and parity

Result schema version 3 requires `canonical_sleeve_evidence` containing:

- engine version and normalized initial capital;
- explicit base and stress cost policies;
- raw signal diagnostics and raw candidate-trade diagnostics in separate fields;
- gross, base-net, and stress-net trades, daily equity, and metrics;
- signal-level and trade-level parity differences;
- `ranking_scenario: base_net`.

Schema-v2 Phase 3 results remain readable as `legacy` but cannot qualify or rank. An unknown engine
version or incomplete scenario evidence makes a schema-v3 result unreproducible.

Parity compares signal dates separately from complete candidate-trade details. Differences caused
by the one-position policy are classified as `intentional_policy_difference` with reason
`position_already_open`; missing or changed signals/trades remain `unclassified` and must be
resolved before relying on the migration.

For formal research, `run_with_bundle` returns `canonical_sleeve_input`, not precomputed canonical
evidence. `ResearchRunCoordinator` loads the frozen definition's base/stress policies, runs the
shared evaluator, serializes the result, and removes the non-JSON input before publication. A runner
cannot substitute a self-reported canonical path or a different cost policy.
Trade comparisons retain legacy candidate prices beside canonical status, executed prices,
fractional quantity, and fees. Base-net fill/fee differences are classified as the intentional
`execution_cost_policy` difference; status, missing trade, or fill mismatches remain unclassified.

## Intentional differences from legacy Part A/B/C

The following changes are expected and explicitly retained in parity or legacy evidence:

- independently simulated overlapping trades no longer increase sleeve exposure;
- independently compounded trade returns no longer determine ranking;
- open positions affect daily equity and drawdown but are not completed trades;
- base-net metrics include preregistered costs, with gross and adverse stress paths reported
  separately;
- same-session entry/exit behavior follows the canonical event order above.

Legacy Part A/B/C payloads remain available for historical inspection. They are not substituted for
canonical daily-equity metrics and cannot grant current qualification.
