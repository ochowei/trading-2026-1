# Trading Research

This context defines the shared language used to research, validate, and operate daily-bar trading strategies.

## Market Data

**Adjusted Daily Bar**:
A daily OHLCV observation whose prices reflect the provider's split and distribution adjustments. It is the only market-data series supported by the first cache version.
_Avoid_: Raw bar, intraday bar, adjusted close only

**Market Data Requirement**:
A research definition's declaration of one primary or auxiliary market-data series and the history needed before execution begins.
_Avoid_: Runtime download, optional ticker, hidden detector dependency

**Market Data Declaration**:
The complete preregistered set of market-data requirements for one experiment execution, with exactly one primary series and any explicitly governed auxiliary series.
_Avoid_: A single ticker setting, an inferred detector dependency, a runtime download request

**Observation Coverage Policy**:
A market-data requirement's explicit rule for validating observation dates: primary series use complete XNYS sessions, while auxiliary series may opt into sparse provider-observation coverage when their availability policy governs as-of alignment.
_Avoid_: An inferred exchange calendar, an implicit forward fill, a freshness guarantee

**Decision Session Sequence**:
The ordered primary-session decisions for one research execution against which auxiliary observations are evaluated for information availability.
_Avoid_: Provider response order, cache row order, an unbounded future observation

**Signal Decision Time**:
The cutoff at which all information used to produce a strategy signal must already have been available.
_Avoid_: Bar date, order time, data download time

**Availability Policy**:
A market data requirement's preregistered rule for when an observation becomes usable and how much observation lag is acceptable relative to signal decision time.
_Avoid_: Forward fill, matching date, provider timestamp assumption

**Observation Lag**:
The elapsed trading-session distance between the primary decision session and the most recent auxiliary observation available under its availability policy.
_Avoid_: Indicator lookback, data download delay

**Market Data Bundle**:
The complete, read-only collection of declared market-data series supplied to a research definition for one execution.
_Avoid_: Data cache, detector-owned download

**Data-Access Migration Parity**:
The requirement that moving an experiment from hidden downloads to a declared market-data bundle preserve its signals, indicators, and trades on the same research data snapshot except for explicitly explained corrections.
_Avoid_: Similar aggregate performance, successful execution

**Provider Boundary**:
The single system boundary where externally sourced market data may be obtained; research logic consumes declared observations instead of contacting an external provider.
_Avoid_: Detector download, strategy-owned data access, cache as provider

**Direct Data-Access Bypass**:
Any experiment-owned path that obtains market data outside its declared research-data bundle, including a hidden provider call or an indirect legacy reader.
_Avoid_: A declared market-data requirement, an offline bundle read

**Legacy Market-Data Allowlist**:
The temporary, explicitly identified set of unmigrated data-access bypasses that may remain historical compatibility evidence during migration.
_Avoid_: Permanent exemption, qualification approval, new-entry authorization

**Monotonic Allowlist Shrink**:
The migration rule that a legacy allowlist may retain or remove an existing identity but may never add or rename one to conceal a new bypass.
_Avoid_: Mutable exception list, bypass inventory refresh

**Market Data Cache**:
A disposable, current working copy of externally sourced market data used to avoid repeated retrieval. It may be refreshed or rebuilt and is not evidence that a research result can be reproduced.
_Avoid_: Research data snapshot, source of truth

**Quarantined Market Data**:
A cache artifact removed from normal use after validation failure and retained only for diagnosis until a clean replacement is published.
_Avoid_: Research data blob, stale market data

**Research Data Snapshot**:
An immutable, identified market dataset retained so that a research result can be reproduced against the same observations.
_Avoid_: Cache, latest data

**Research Data Blob**:
An immutable market-data artifact identified by its content digest and shared by every snapshot that contains the same observations.
_Avoid_: Per-experiment data copy, cache file

**Orphaned Research Data Blob**:
A research data blob that is not referenced by any retained snapshot manifest and is therefore eligible for explicit garbage collection.
_Avoid_: Old blob, stale cache

**Snapshot Manifest**:
An immutable record that identifies every research data blob and its source context required to reproduce a persisted research result.
_Avoid_: Cache metadata, latest-data marker

**Snapshot Bundle**:
A portable package containing a snapshot manifest and every research data blob it references, used to archive or transfer reproducible research without external storage.
_Avoid_: Cache archive, result export

**Fresh Market Data**:
Market data that includes the most recent completed trading session required by the requested operation.
_Avoid_: Available data, cached data

**Stale Market Data**:
Market data that does not include the most recent completed trading session required by the requested operation, even when the available observations are otherwise valid.
_Avoid_: Invalid data, missing data

**Offline Research Run**:
An explicitly requested research operation that accepts stale market data and records its actual cutoff instead of claiming current-data coverage.
_Avoid_: Fallback run, normal research run

**Persisted Research Result**:
A reproducible experiment outcome saved with a snapshot manifest and eligible for comparison, documentation, qualification, or followup decisions.
_Avoid_: Console output, ephemeral result

**Valid Research Result**:
A persisted research result whose market-data coverage satisfies its intended decision and whose research-definition fingerprint matches the definition being evaluated.
_Avoid_: Latest result, existing result

**Latest Research Result**:
The most recent successful online persisted research result that was valid when published. It remains historical evidence but may later become data-stale or definition-stale.
_Avoid_: Last attempted run, offline result, necessarily valid result

**Data-Stale Result**:
A persisted research result whose snapshot does not satisfy the market-data coverage required by its intended decision.
_Avoid_: Definition-stale result, invalid JSON

**Definition-Stale Result**:
A persisted research result produced by a strategy or execution definition that does not match the definition currently being evaluated.
_Avoid_: Data-stale result, old result

**Unreproducible Research Result**:
A persisted research result whose referenced immutable evidence is missing or corrupted and cannot be reconstructed from the currently available snapshot store or bundle.
_Avoid_: Data-stale result, failed experiment

**Ephemeral Research Run**:
An explicitly requested diagnostic experiment execution that neither creates a snapshot nor changes persisted research results.
_Avoid_: Draft result, latest result

**Snapshot-Eligible Market Data**:
A fully refreshed adjusted daily-bar series whose observations share one provider adjustment generation and may therefore be captured in a new research data snapshot.
_Avoid_: Incrementally updated cache, fresh-enough followup data

## Research Definitions

**Experiment Family**:
A declared lineage of experiment trials that share a baseline hypothesis or signal structure and therefore contribute to the same selection history.
_Avoid_: Asset, directory prefix, renamed independent idea

**Experiment Trial**:
One permanently registered research-definition fingerprint evaluated as a formal variant within an experiment family; later observations on new data do not erase or duplicate the trial.
_Avoid_: Command run, result file, ephemeral run

**Experiment Trial Registry**:
The append-only research history that retains every formal experiment trial, including failed or removed variants, and links it to its family, hypothesis, snapshots, and observations.
_Avoid_: Experiment directory listing, latest-results index

**Selection-Adjusted Confidence**:
The confidence that a selected experiment trial's observed advantage remains after reproducing the family-level process that selected the best result from all registered trials.
_Avoid_: Raw p-value, Sharpe ranking, unadjusted confidence

**Family Baseline**:
The preregistered experiment trial or non-strategy alternative against which an experiment family's claimed improvement is evaluated.
_Avoid_: Worst trial, retrospectively chosen comparator

**Exposure-Matched Random-Entry Benchmark**:
A randomized comparator that preserves an experiment trial's instrument, trade count, entry-season distribution, and holding exposure while removing its signal timing.
_Avoid_: Buy-and-hold, cash benchmark, shuffled returns

**Research Definition**:
The resolved strategy, signal, execution, and computational inputs whose semantics determine an experiment outcome.
_Avoid_: Experiment name, source file, display configuration

**Snapshot-Aware Experiment**:
An experiment that declares all outcome-relevant market-data dependencies before execution and consumes only the verified immutable data supplied for that run.
_Avoid_: Experiment with a cache, experiment with a hidden auxiliary download

**Legacy/Unmigrated Experiment**:
An experiment that has not yet adopted the snapshot-aware contract and therefore remains historical compatibility evidence until a new definition is formally evaluated.
_Avoid_: Current qualified experiment, automatically grandfathered strategy

**Research-Definition Fingerprint**:
A semantic identity for a research definition that ignores non-behavioral source changes and conservatively changes whenever outcome-relevant behavior may have changed.
_Avoid_: Git commit, raw file hash, experiment version

**Research Definition Snapshot**:
An immutable, identified collection of the resolved configuration, outcome-relevant source content, runtime context, and dependency versions needed to reconstruct a research definition, including uncommitted content.
_Avoid_: Git commit, fingerprint, source backup

## Strategy Execution

**Strategy Sleeve**:
The capital and position boundary assigned to one active strategy, isolated from every other strategy sleeve.
_Avoid_: Signal, experiment, ticker allocation

**Active Strategy**:
The single strategy authorized to propose new live orders for an instrument.
_Avoid_: Best experiment, research candidate, strategy with an open legacy position

**Legacy Active Strategy**:
A strategy authorized by the superseded qualification model that may manage an existing actual position but must pass current qualification before proposing a new position.
_Avoid_: Active strategy, shadow strategy, automatically grandfathered strategy

**Shadow Strategy**:
A historically qualified strategy with a frozen research definition that produces paper proposals and simulated executions on prospective data but is not authorized to create actual positions.
_Avoid_: Active strategy, backtest candidate, reduced-size live strategy

**Shadow Registration**:
The formal event that binds a historically qualified trial to one frozen research definition, prospective start time, and preregistered activation checkpoint and thresholds.
_Avoid_: Part C start, historical qualification date, paper-trading toggle

**Shadow Restart**:
A new Shadow registration required after an outcome-relevant definition change; prior prospective evidence remains historical but is never carried into the new registration.
_Avoid_: Evidence reset, continued Shadow, fingerprint update

**Shadow Paper Proposal**:
A non-actionable strategy instruction recorded after Shadow registration and evaluated only through canonical simulated execution.
_Avoid_: Proposed order, broker order, historical signal

**Canonical Simulated Fill**:
A Shadow execution produced by the same frozen position and cost policies used for canonical research, without asserting that a broker transaction occurred.
_Avoid_: Confirmed fill, assumed fill, backfilled trade

**Frozen Research Definition**:
A research definition that cannot change during a prospective observation period without restarting that period under a new identity.
_Avoid_: Current source code, parameter family, mutable candidate

**Prospective Evidence**:
Observations produced after a research definition was frozen and before its outcomes were available for design or selection.
_Avoid_: Recent backtest, Part B, rerun historical data

**Legacy Period Result**:
A retained Part A, Part B, or Part C outcome produced under the superseded fixed-period model and available for historical inspection but not current qualification.
_Avoid_: Historical stability fold, shadow evidence, live evidence

**Live Evidence**:
Confirmed execution and strategy-sleeve observations accumulated by an active strategy after activation.
_Avoid_: Part C backtest, shadow evidence, recent historical result

**Predictive Drift Envelope**:
The immutable, pre-activation expectation contract for performance, signal, execution, utilization,
and concentration metrics. It includes the historical-fold and Shadow source identities, Decimal
thresholds, sampling policy, fixed checkpoint schedule, and the strategy-definition fingerprint.
Thresholds and source identities cannot be edited after the envelope is activation-bound.
_Avoid_: Live-tuned threshold, confidence interval selected after a breach, arbitrary loss count

**Frozen Activation Expectations**:
The complete set of predictive envelope thresholds, hard-guard kinds, source identities, and
checkpoint policy captured before an Active lifecycle transition and referenced by every later
observation and recovery decision.
_Avoid_: Current configuration, mutable monitoring settings, operator override

**Performance Drift**:
An adverse departure of realized strategy-sleeve returns or drawdown metrics from the frozen
performance expectation.
_Avoid_: Any individual loss, revised backtest result

**Signal Drift**:
An adverse departure in signal frequency, direction, timing, or conditional hit behavior from
the frozen signal expectation.
_Avoid_: A skipped proposal caused by a ledger or position guard

**Execution Drift**:
An adverse departure in confirmed-fill slippage, fill rate, costs, or execution timing from the
frozen execution expectation. It is based on confirmed ledger evidence, never an assumed fill.
_Avoid_: Paper fill, broker quote, estimated order price

**Utilization Drift**:
An adverse departure in sleeve capital or holding utilization from the frozen portfolio policy.
_Avoid_: Managed account buying power, unallocated reserve

**Concentration Drift**:
An adverse departure in instrument, sleeve, fold, or correlated exposure concentration from the
frozen portfolio expectation.
_Avoid_: A single profitable trade, equal sleeve allocation itself

**Activation Checkpoint**:
A pre-scheduled evaluation of whether a shadow strategy has accumulated the required prospective duration, completed trades, performance, risk, and drift evidence for active trading.
_Avoid_: Best-performing date, manual promotion opportunity

**Healthy Strategy**:
An active strategy whose preregistered performance, signal, execution, and portfolio monitors remain within their expected ranges.
_Avoid_: Profitable strategy, strategy without alerts

**Watch Strategy**:
An active strategy with a non-critical or not-yet-persistent drift indication that remains authorized for new positions under heightened monitoring.
_Avoid_: Paused strategy, manually suspected strategy

**Paused Strategy**:
An active strategy barred from proposing new positions after a critical or persistent drift breach while remaining responsible for existing actual positions.
_Avoid_: Retiring strategy, rejected experiment, closed position

**Hard Guard**:
A deterministic data, ledger, reconciliation, execution, or stress-risk breach that immediately
blocks new BUY authorization. A hard guard does not wait for a scheduled checkpoint or statistical
persistence and must be cleared by fresh verified evidence.
_Avoid_: Watch warning, discretionary concern, ordinary single loss

**Drift Health Overlay**:
The Phase 8 Healthy/Watch/Paused state projected on top of the Phase 7 lifecycle. It governs new
risk while Phase 7 Active/Retiring ownership and qualification state remains authoritative for
position ownership and lifecycle transitions.
_Avoid_: Replacing Active with lifecycle Paused, retirement, manual status flag

**Scheduled Checkpoint**:
A fixed completed-XNYS-session evaluation date derived from the frozen activation expectations.
The checkpoint ordinal, session, observations, and result are replayed deterministically and cannot
be moved by editing a state field.
_Avoid_: Ad-hoc review date, latest available bar, manual unpause

**Persistent Watch**:
Watch evidence at two consecutive scheduled checkpoints under the same frozen envelope, which
deterministically transitions the drift health overlay to Paused.
_Avoid_: Two arbitrary alerts, one loss, operator suspicion

**Recovery Checkpoint**:
A preregistered evaluation that determines whether a paused strategy has accumulated sufficient new evidence to resume proposing positions.
_Avoid_: Manual unpause, parameter adjustment

**Normal Recovery**:
The fail-closed recovery gate for a non-integrity pause: at least 126 later sessions, six completed
Shadow trades, all hard guards cleared, and two consecutive scheduled checkpoints in the normal
envelope. It may only append a replayable recovery event.
_Avoid_: Direct state edit, threshold relaxation, one profitable trade

**Data/Ledger-Only Recovery**:
The expedited recovery gate for pauses caused solely by data, ledger, or reconciliation integrity
guards. It requires completed reconciliation, two distinct clean checks after the pause, and no
active hard guard; it does not waive a performance, signal, execution, utilization, concentration,
or stress-risk pause.
_Avoid_: Strategy-trade recovery, manual acknowledgement

**New Trial Caused by Definition Change**:
A new Experiment Trial and new Shadow registration required when the outcome-relevant strategy or
execution definition fingerprint changes. Previous live or Shadow evidence cannot be carried into
the changed definition.
_Avoid_: Threshold update, in-place trial mutation, recovery

**Historical Stability Screen**:
A retrospective qualification gate that evaluates one frozen research definition across non-overlapping chronological folds without claiming that repeatedly inspected history is prospective evidence.
_Avoid_: Prospective validation, rolling-window chart, activation evidence

**Historical Qualification Plan**:
A preregistered screen identity that freezes the development period, evaluation folds, dependency purge and embargo, benchmark policy, and pass thresholds before evaluation outcomes are observed.
_Avoid_: Backtest options, adaptive gate, post-hoc screen

**Forward Selection Epoch**:
A future-only qualification boundary that freezes one selected trial, its family baseline, and the complete family trial universe before any included evaluation outcome exists. Previously incomplete selection history remains disclosed, and any later family trial invalidates the epoch.
_Avoid_: Cleared selection history, retroactive trial inventory, rolling candidate set

**Evaluation Fold**:
A non-overlapping chronological outcome interval in a historical stability screen, separated as needed so adjacent folds do not share trade outcomes.
_Avoid_: Training period, overlapping rolling window

**Stress Drawdown Limit**:
The maximum strategy-sleeve drawdown preregistered before a qualification screen or prospective observation period begins.
_Avoid_: Observed maximum drawdown, adjustable stop-loss

**Fold Concentration**:
The share of a historical stability screen's trades or profits attributable to one evaluation fold.
_Avoid_: Portfolio concentration, ticker allocation

**Live Drift**:
A preregistered, evidence-based departure of an active strategy's performance, signal, execution, or portfolio behavior from the range established before activation.
_Avoid_: Any loss, market opinion, post-hoc concern

**Retiring Strategy**:
A formerly active strategy that remains the owner of its ledger-linked actual position and may manage that position to verified flat closure but cannot propose a new position.
_Avoid_: Active strategy, rejected experiment

**No-New-Entry Mode**:
A reversible followup operating state that blocks every new position while preserving verified ledger history and management of existing actual positions.
_Avoid_: Shutdown, ledger reset, strategy rejection

**Followup Lifecycle Registry**:
The append-only authority that records each followup strategy's operational status and the global no-new-entry state used by order authorization.
_Avoid_: Followup report, qualification registry, strategy list

**Followup Data Bundle Identity**:
The deterministic SHA-256 identity of the validated primary frame, every declared and availability-aligned auxiliary frame, the data cutoff, and the alignment policy used for one followup evaluation.
_Avoid_: Data cutoff, result snapshot ID, cache checksum

**Skipped Signal**:
A detected strategy signal that is recorded but not submitted for execution because its strategy sleeve cannot accept a new position under the active position policy.
_Avoid_: Unfilled order, rejected strategy, missing signal

**Position Policy**:
The explicit rules governing how a strategy sleeve opens, adds to, and closes positions. The default policy permits at most one open position and does not pyramid.
_Avoid_: Entry signal, allocation policy

**Execution Cost Policy**:
The preregistered assumptions for slippage, fees, fill behavior, and other execution costs applied consistently across research and shadow simulation.
_Avoid_: Confirmed execution cost, post-hoc adjustment

**Stress-Cost Scenario**:
A preregistered adverse execution-cost variant used to test whether a strategy's expected advantage survives worse fills than its base execution cost policy.
_Avoid_: Worst historical trade, live drift, arbitrary penalty

**Allocation Policy**:
The portfolio-level rules assigning capital to strategy sleeves independently of the strategies that generate signals.
_Avoid_: Position policy, strategy definition

**Equal Sleeve Allocation**:
The canonical allocation policy that assigns equal initial capital to isolated strategy sleeves, does not lend or transfer capital between them, and does not rebalance during evaluation.
_Avoid_: Equal risk, equal position count

**Followup Universe**:
The declared set of instrument slots for which managed capital is reserved and strategies may progress through the followup lifecycle.
_Avoid_: Active strategies, all experiments, brokerage holdings

**Managed Capital**:
The user-designated portion of brokerage capital governed by the followup allocation and execution ledger, excluding unrelated holdings and cash.
_Avoid_: Account equity, backtest capital, buying power

**Sleeve Capital**:
The isolated share of managed capital reserved for one instrument slot in the followup universe, whether its strategy is active or held as cash.
_Avoid_: Available account cash, position market value, transferable balance

**Allocation Epoch**:
A declared interval during which the followup universe and its sleeve-capital assignments remain fixed.
_Avoid_: Rebalance date, strategy activation, experiment period

**Unallocated Reserve**:
Managed capital not assigned to a strategy sleeve in the current allocation epoch and unavailable for opportunistic borrowing by active sleeves.
_Avoid_: Sleeve cash, account buying power, idle position value

**Volatility-Weighted Allocation**:
An alternative allocation policy that sizes strategy sleeves from lagged volatility estimates and must be evaluated separately from equal sleeve allocation.
_Avoid_: Risk parity, strategy improvement

## Manual Trading

**Proposed Order**:
A strategy-generated instruction offered for manual review that has not been asserted as submitted or filled.
_Avoid_: Order, trade, position

**Proposal ID**:
The stable identity of one proposed order across repeated followup runs, used to link its execution events and prevent duplicate manual action.
_Avoid_: Report row number, broker order ID, run ID

**Confirmed Fill**:
A user-recorded execution reported by the broker that changes actual cash or position state.
_Avoid_: Signal, proposed order, assumed fill

**Manual Execution Ledger**:
The authoritative local record of confirmed manual trading events from which actual positions are derived.
_Avoid_: Backtest trades, order report, inferred positions

**Execution Event**:
An immutable ledger entry recording a submitted, filled, partially filled, cancelled, fee, or corrective manual trading occurrence.
_Avoid_: Mutable order row, current position

**Ledger Integrity**:
The verified continuity and accounting consistency of the manual execution ledger's append-only event chain.
_Avoid_: File existence, successful CSV parsing, broker authentication

**Position View**:
A disposable projection of actual positions derived by replaying execution events.
_Avoid_: Manual execution ledger, editable position source

**Actual Position**:
A position derived from confirmed fills in the manual execution ledger rather than from strategy simulation.
_Avoid_: Open backtest trade, proposed position, expected position
