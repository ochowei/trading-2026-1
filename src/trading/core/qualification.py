"""Historical qualification and prospective Shadow domain contracts."""

from __future__ import annotations

import hashlib
import math
import random
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from decimal import Decimal

import pandas as pd

from trading.core.accounting import (
    canonical_json_bytes,
    decimal_text,
    parse_timestamp,
    timestamp_text,
    to_decimal,
)
from trading.core.sleeve_engine import (
    DEFAULT_BASE_COST_POLICY,
    DEFAULT_STRESS_COST_POLICY,
    CandidateTrade,
    CanonicalSleeveInput,
    ExecutionCostPolicy,
    SleeveTrade,
    evaluate_canonical_sleeve_input,
    validate_cost_scenario_policies,
)
from trading.market_data.contracts import SessionCalendar

HISTORICAL_QUALIFICATION_GATE_NAMES = (
    "completed_trades",
    "traded_folds",
    "positive_traded_folds",
    "aggregate_cumulative_return",
    "aggregate_profit_factor",
    "stress_cumulative_return",
    "stress_profit_factor",
    "stress_drawdown",
    "trade_fold_concentration",
    "profit_fold_concentration",
    "cash_benchmark",
    "family_baseline_benchmark",
    "random_entry_benchmark",
    "selection_adjusted_confidence",
)

SHADOW_ACTIVATION_GATE_NAMES = (
    "shadow_identity",
    "definition_unchanged",
    "activation_checkpoint",
    "completed_sessions",
    "completed_trades",
    "prospective_cumulative_return",
    "prospective_profit_factor",
    "stress_cumulative_return",
    "stress_profit_factor",
    "stress_drawdown",
    "critical_drift",
)


@dataclass(frozen=True, slots=True)
class HistoricalScreenThresholds:
    """Preregistered gates for one Historical Stability Screen."""

    minimum_development_years: int = 3
    minimum_evaluation_folds: int = 5
    minimum_completed_trades: int = 20
    minimum_traded_folds: int = 3
    minimum_positive_fold_rate: Decimal = Decimal("0.60")
    minimum_cumulative_return: Decimal = Decimal("0")
    minimum_profit_factor: Decimal = Decimal("1.10")
    minimum_stress_cumulative_return: Decimal = Decimal("0")
    minimum_stress_profit_factor: Decimal = Decimal("1")
    maximum_fold_concentration: Decimal = Decimal("0.50")
    selection_confidence: Decimal = Decimal("0.90")


@dataclass(frozen=True, slots=True)
class HistoricalBenchmarkPolicy:
    """Frozen cash, family-baseline, and random-entry benchmark identity."""

    family_baseline_trial_id: str
    random_seed: int
    random_samples: int


@dataclass(frozen=True, slots=True)
class SelectionAdjustmentPolicy:
    """Frozen family-wise block-bootstrap sampling policy."""

    repetitions: int
    block_sessions: int


@dataclass(frozen=True, slots=True)
class ForwardSelectionEpoch:
    """Frozen future-only trial universe that bounds incomplete legacy selection history."""

    started_at: datetime
    selected_trial_id: str
    included_trial_ids: tuple[str, ...]
    prior_selection_history_incomplete: bool


@dataclass(frozen=True, slots=True)
class EvaluationFold:
    """One annual outcome interval and its dependency-safe signal window."""

    fold_id: str
    evaluation_year: int
    outcome_start: date
    outcome_end: date
    signal_start: date
    signal_end: date

    def contains_signal(self, signal_date: date) -> bool:
        return self.signal_start <= signal_date <= self.signal_end


@dataclass(frozen=True, slots=True)
class HistoricalQualificationPlan:
    """Frozen dates and thresholds established before evaluation outcomes."""

    plan_id: str
    experiment_family: str
    definition_fingerprint: str
    created_at: datetime
    development_years: tuple[int, ...]
    evaluation_sessions: tuple[date, ...]
    folds: tuple[EvaluationFold, ...]
    maximum_holding_sessions: int
    execution_lag_sessions: int
    dependency_sessions: int
    embargo_sessions: int
    stress_drawdown_limit: Decimal
    base_cost_policy: ExecutionCostPolicy
    stress_cost_policy: ExecutionCostPolicy
    thresholds: HistoricalScreenThresholds
    benchmarks: HistoricalBenchmarkPolicy
    selection_adjustment: SelectionAdjustmentPolicy
    forward_selection_epoch: ForwardSelectionEpoch | None = None


@dataclass(frozen=True, slots=True)
class HistoricalFoldEvidence:
    """Decision evidence for one visible annual evaluation fold."""

    fold_id: str
    evaluation_year: int
    signal_count: int
    candidate_count: int
    completed_trades: int
    cumulative_return: float
    stress_cumulative_return: float
    stress_max_drawdown: float
    gross_profit: float
    gross_loss: float
    stress_gross_profit: float
    stress_gross_loss: float

    @property
    def visible(self) -> bool:
        return True

    @property
    def traded(self) -> bool:
        return self.completed_trades > 0

    @property
    def positive(self) -> bool:
        return self.traded and self.cumulative_return > 0


@dataclass(frozen=True, slots=True)
class QualificationGate:
    """One frozen threshold and its observed pass/fail result."""

    name: str
    passed: bool
    actual: str
    threshold: str


@dataclass(frozen=True, slots=True)
class HistoricalBenchmarkEvidence:
    """Cash and preregistered family-baseline outcomes for one screen."""

    cash_return: float
    family_baseline_return: float
    random_entry_samples: tuple[ExposureMatchedRandomSample, ...]

    @property
    def random_entry_returns(self) -> tuple[float, ...]:
        return tuple(sample.cumulative_return for sample in self.random_entry_samples)


@dataclass(frozen=True, slots=True)
class ExposureMatchedRandomSample:
    """One deterministic random-entry path preserving observed exposure shape."""

    sample_index: int
    cumulative_return: float
    completed_trades: int
    entry_months: tuple[int, ...]
    holding_sessions: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class HistoricalScreenResult:
    """Historical evidence that may qualify only for prospective Shadow."""

    plan_id: str
    folds: tuple[HistoricalFoldEvidence, ...]
    aggregate: HistoricalAggregateEvidence
    benchmarks: HistoricalBenchmarkEvidence
    selection_adjustment: SelectionAdjustmentResult
    gates: tuple[QualificationGate, ...]
    passed: bool
    disposition: str


@dataclass(frozen=True, slots=True)
class HistoricalAggregateEvidence:
    """Auditable aggregate metrics used by the historical gates."""

    completed_trades: int
    traded_folds: int
    positive_traded_fold_rate: float
    cumulative_return: float
    profit_factor: str
    stress_cumulative_return: float
    stress_profit_factor: str
    stress_max_drawdown: float
    trade_fold_concentration: float
    profit_fold_concentration: float


@dataclass(frozen=True, slots=True)
class SelectionAdjustmentResult:
    """Family-wise block-bootstrap confidence for one selected trial."""

    selected_trial_id: str
    included_trial_ids: tuple[str, ...]
    observed_mean_excess_return: Decimal
    adjusted_confidence: Decimal
    repetitions: int
    block_sessions: int
    passed: bool


@dataclass(frozen=True, slots=True)
class DailyExcessReturn:
    """One family-trial excess return attributed to an exact market session."""

    session: date
    value: float


@dataclass(frozen=True, slots=True)
class ShadowActivationPolicy:
    """Prospective thresholds frozen at formal Shadow registration."""

    minimum_completed_sessions: int = 252
    minimum_completed_trades: int = 12
    minimum_cumulative_return: Decimal = Decimal("0")
    minimum_profit_factor: Decimal = Decimal("1")
    minimum_stress_cumulative_return: Decimal = Decimal("0")
    minimum_stress_profit_factor: Decimal = Decimal("1")
    stress_drawdown_limit: Decimal = Decimal("0.20")


@dataclass(frozen=True, slots=True)
class ShadowRegistration:
    """Formal boundary after which observations may become prospective evidence."""

    shadow_id: str
    trial_id: str
    historical_plan_id: str
    experiment_family: str
    definition_fingerprint: str
    definition_snapshot_id: str
    definition_snapshot_byte_count: int
    prospective_start: datetime
    activation_checkpoint: date
    activation_policy: ShadowActivationPolicy
    base_cost_policy: ExecutionCostPolicy
    stress_cost_policy: ExecutionCostPolicy
    prior_shadow_id: str | None = None
    status: str = "shadow"


@dataclass(frozen=True, slots=True)
class ShadowPaperProposal:
    """One deterministic non-actionable proposal observed after registration."""

    proposal_id: str
    shadow_id: str
    signal_date: date
    entry_date: date
    action: str = "BUY"


@dataclass(frozen=True, slots=True)
class CanonicalSimulatedFill:
    """One completed canonical Shadow execution linked to its paper proposal."""

    proposal_id: str
    quantity: float
    executed_entry_price: float
    executed_exit_price: float
    pnl: float


@dataclass(frozen=True, slots=True)
class ShadowEvidence:
    """Prospective-only sessions, proposals, and canonical simulated fills."""

    shadow_id: str
    definition_fingerprint: str
    as_of: date
    data_cutoff: date
    completed_sessions: int
    paper_proposals: tuple[ShadowPaperProposal, ...]
    simulated_fills: tuple[CanonicalSimulatedFill, ...]
    cumulative_return: float
    profit_factor: str
    stress_cumulative_return: float
    stress_profit_factor: str
    stress_max_drawdown: float
    critical_drift: bool


@dataclass(frozen=True, slots=True)
class ShadowActivationEvaluation:
    """A preregistered checkpoint result that never performs live cutover."""

    shadow_id: str
    gates: tuple[QualificationGate, ...]
    eligible: bool
    disposition: str

    @property
    def authorized_for_live_orders(self) -> bool:
        """Phase 6 can recommend activation but never performs Phase 7 cutover."""
        return False


class ShadowRestartRequired(RuntimeError):
    """The frozen definition changed and prospective evidence must restart."""


def build_historical_qualification_plan(
    *,
    experiment_family: str,
    definition_fingerprint: str,
    sessions: tuple[date, ...],
    evaluation_years: tuple[int, ...],
    maximum_holding_sessions: int,
    execution_lag_sessions: int,
    dependency_sessions: int,
    embargo_sessions: int,
    stress_drawdown_limit: Decimal | int | str,
    family_baseline_trial_id: str,
    random_seed: int,
    random_samples: int,
    bootstrap_repetitions: int,
    bootstrap_block_sessions: int,
    created_at: datetime,
    thresholds: HistoricalScreenThresholds | None = None,
    base_cost_policy: ExecutionCostPolicy = DEFAULT_BASE_COST_POLICY,
    stress_cost_policy: ExecutionCostPolicy = DEFAULT_STRESS_COST_POLICY,
    forward_selection_epoch: ForwardSelectionEpoch | None = None,
) -> HistoricalQualificationPlan:
    """Freeze annual folds with explicit purge and embargo signal exclusions."""
    if not experiment_family.strip() or not definition_fingerprint.strip():
        raise ValueError("historical plan requires family and definition identity")
    if created_at.tzinfo is None:
        raise ValueError("historical plan clock must be timezone-aware")
    if (
        min(
            maximum_holding_sessions,
            execution_lag_sessions,
            dependency_sessions,
            embargo_sessions,
        )
        < 0
    ):
        raise ValueError("purge and embargo sessions cannot be negative")
    if dependency_sessions < maximum_holding_sessions + execution_lag_sessions:
        raise ValueError("purge must cover holding and execution dependencies")
    if embargo_sessions < execution_lag_sessions:
        raise ValueError("embargo must cover the execution dependency")
    if not family_baseline_trial_id.strip():
        raise ValueError("historical plan requires a preregistered family baseline")
    if random_samples <= 0 or bootstrap_repetitions <= 0 or bootstrap_block_sessions <= 0:
        raise ValueError("historical benchmark sample counts must be positive")
    ordered_sessions = tuple(sorted(set(sessions)))
    if not ordered_sessions:
        raise ValueError("historical plan requires evaluation sessions")
    years = tuple(sorted(set(evaluation_years)))
    gate = thresholds or HistoricalScreenThresholds()
    validate_historical_thresholds(gate)
    validate_cost_scenario_policies(base_cost_policy, stress_cost_policy)
    if len(years) < gate.minimum_evaluation_folds:
        raise ValueError("historical plan requires at least five annual evaluation folds")
    development_years = tuple(
        sorted({item.year for item in ordered_sessions if item.year < years[0]})
    )
    if len(development_years) < gate.minimum_development_years:
        raise ValueError("historical plan requires at least three development years")
    required_development_years = tuple(range(years[0] - gate.minimum_development_years, years[0]))
    if not set(required_development_years).issubset(development_years):
        raise ValueError("historical plan requires consecutive development years")
    for year in required_development_years:
        _validate_annual_coverage(ordered_sessions, year, "development")
    if years != tuple(range(years[0], years[-1] + 1)):
        raise ValueError("historical evaluation folds must be consecutive annual periods")
    folds: list[EvaluationFold] = []
    for year in years:
        annual = tuple(item for item in ordered_sessions if item.year == year)
        _validate_annual_coverage(ordered_sessions, year, "evaluation")
        if len(annual) <= dependency_sessions + embargo_sessions:
            raise ValueError(f"evaluation year {year} has insufficient sessions")
        folds.append(
            EvaluationFold(
                fold_id=f"fold-{year}",
                evaluation_year=year,
                outcome_start=annual[0],
                outcome_end=annual[-1],
                signal_start=annual[embargo_sessions],
                signal_end=annual[-(dependency_sessions + 1)],
            )
        )
    if created_at.astimezone(UTC).date() >= folds[0].outcome_start:
        raise ValueError("historical plan must be frozen before evaluation outcomes begin")
    drawdown_limit = to_decimal(
        stress_drawdown_limit,
        "stress_drawdown_limit",
        allow_negative=False,
    )
    benchmarks = HistoricalBenchmarkPolicy(
        family_baseline_trial_id=family_baseline_trial_id,
        random_seed=random_seed,
        random_samples=random_samples,
    )
    selection_adjustment = SelectionAdjustmentPolicy(
        repetitions=bootstrap_repetitions,
        block_sessions=bootstrap_block_sessions,
    )
    if forward_selection_epoch is not None:
        _validate_forward_selection_epoch(
            forward_selection_epoch,
            created_at=created_at.astimezone(UTC),
            family_baseline_trial_id=family_baseline_trial_id,
        )
    payload = {
        "schema_version": 1,
        "experiment_family": experiment_family,
        "definition_fingerprint": definition_fingerprint,
        "created_at": timestamp_text(created_at.astimezone(UTC)),
        "development_years": list(development_years),
        "evaluation_sessions": [
            session.isoformat() for session in ordered_sessions if session.year in years
        ],
        "folds": [
            {
                "fold_id": fold.fold_id,
                "evaluation_year": fold.evaluation_year,
                "outcome_start": fold.outcome_start.isoformat(),
                "outcome_end": fold.outcome_end.isoformat(),
                "signal_start": fold.signal_start.isoformat(),
                "signal_end": fold.signal_end.isoformat(),
            }
            for fold in folds
        ],
        "dependency_sessions": dependency_sessions,
        "embargo_sessions": embargo_sessions,
        "maximum_holding_sessions": maximum_holding_sessions,
        "execution_lag_sessions": execution_lag_sessions,
        "stress_drawdown_limit": decimal_text(drawdown_limit, "stress_drawdown_limit"),
        "cost_policies": _cost_policy_payload(base_cost_policy, stress_cost_policy),
        "thresholds": _threshold_payload(gate),
        "benchmarks": {
            "family_baseline_trial_id": benchmarks.family_baseline_trial_id,
            "random_seed": benchmarks.random_seed,
            "random_samples": benchmarks.random_samples,
        },
        "selection_adjustment": {
            "repetitions": selection_adjustment.repetitions,
            "block_sessions": selection_adjustment.block_sessions,
        },
    }
    if forward_selection_epoch is not None:
        payload["forward_selection_epoch"] = _forward_selection_epoch_payload(
            forward_selection_epoch
        )
    plan_id = "historical-plan-" + hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    return HistoricalQualificationPlan(
        plan_id=plan_id,
        experiment_family=experiment_family,
        definition_fingerprint=definition_fingerprint,
        created_at=created_at.astimezone(UTC),
        development_years=development_years,
        evaluation_sessions=tuple(session for session in ordered_sessions if session.year in years),
        folds=tuple(folds),
        maximum_holding_sessions=maximum_holding_sessions,
        execution_lag_sessions=execution_lag_sessions,
        dependency_sessions=dependency_sessions,
        embargo_sessions=embargo_sessions,
        stress_drawdown_limit=drawdown_limit,
        base_cost_policy=base_cost_policy,
        stress_cost_policy=stress_cost_policy,
        thresholds=gate,
        benchmarks=benchmarks,
        selection_adjustment=selection_adjustment,
        forward_selection_epoch=forward_selection_epoch,
    )


def evaluate_historical_stability_screen(
    plan: HistoricalQualificationPlan,
    *,
    strategy_input: CanonicalSleeveInput,
    family_baseline_trial_id: str,
    family_baseline_input: CanonicalSleeveInput,
    family_baseline_verifier: Callable[[str, CanonicalSleeveInput], None],
    selection_adjustment: SelectionAdjustmentResult,
    base_policy: ExecutionCostPolicy,
    stress_policy: ExecutionCostPolicy,
) -> HistoricalScreenResult:
    """Evaluate annual folds without allowing historical evidence to become Active."""
    if base_policy != plan.base_cost_policy or stress_policy != plan.stress_cost_policy:
        raise ValueError("historical screen cost policies differ from its frozen plan")
    if family_baseline_trial_id != plan.benchmarks.family_baseline_trial_id:
        raise ValueError("historical screen family baseline differs from its frozen plan")
    family_baseline_verifier(family_baseline_trial_id, family_baseline_input)
    if (
        selection_adjustment.repetitions != plan.selection_adjustment.repetitions
        or selection_adjustment.block_sessions != plan.selection_adjustment.block_sessions
    ):
        raise ValueError("historical screen selection adjustment policy differs from its plan")
    if (
        len(set(selection_adjustment.included_trial_ids))
        != len(selection_adjustment.included_trial_ids)
        or selection_adjustment.selected_trial_id not in selection_adjustment.included_trial_ids
        or plan.benchmarks.family_baseline_trial_id not in selection_adjustment.included_trial_ids
        or selection_adjustment.passed
        != (selection_adjustment.adjusted_confidence >= plan.thresholds.selection_confidence)
    ):
        raise ValueError("historical screen selection adjustment evidence is inconsistent")
    folds = _evaluate_folds(
        plan,
        strategy_input,
        base_policy=base_policy,
        stress_policy=stress_policy,
    )
    baseline_folds = _evaluate_folds(
        plan,
        family_baseline_input,
        base_policy=base_policy,
        stress_policy=stress_policy,
    )
    cumulative_return = _compound_return(fold.cumulative_return for fold in folds)
    baseline_return = _compound_return(fold.cumulative_return for fold in baseline_folds)
    random_samples = _evaluate_random_entry_benchmark(
        plan,
        strategy_input,
        base_policy=base_policy,
        stress_policy=stress_policy,
    )
    random_threshold = _percentile(
        tuple(sample.cumulative_return for sample in random_samples),
        0.90,
    )
    completed_trades = sum(fold.completed_trades for fold in folds)
    traded_folds = sum(fold.traded for fold in folds)
    positive_folds = sum(fold.positive for fold in folds)
    positive_rate = positive_folds / traded_folds if traded_folds else 0.0
    gross_profit = sum(fold.gross_profit for fold in folds)
    gross_loss = sum(fold.gross_loss for fold in folds)
    profit_factor = gross_profit / gross_loss if gross_loss else (math.inf if gross_profit else 0.0)
    stress_cumulative_return = _compound_return(fold.stress_cumulative_return for fold in folds)
    stress_gross_profit = sum(fold.stress_gross_profit for fold in folds)
    stress_gross_loss = sum(fold.stress_gross_loss for fold in folds)
    stress_profit_factor = (
        stress_gross_profit / stress_gross_loss
        if stress_gross_loss
        else (math.inf if stress_gross_profit else 0.0)
    )
    stress_drawdown = min((fold.stress_max_drawdown for fold in folds), default=0.0)
    trade_concentration = (
        max((fold.completed_trades for fold in folds), default=0) / completed_trades
        if completed_trades
        else 0.0
    )
    profit_concentration = (
        max((fold.gross_profit for fold in folds), default=0.0) / gross_profit
        if gross_profit
        else 0.0
    )
    thresholds = plan.thresholds
    gates = (
        _gate(
            "completed_trades",
            completed_trades >= thresholds.minimum_completed_trades,
            completed_trades,
            thresholds.minimum_completed_trades,
        ),
        _gate(
            "traded_folds",
            traded_folds >= thresholds.minimum_traded_folds,
            traded_folds,
            thresholds.minimum_traded_folds,
        ),
        _gate(
            "positive_traded_folds",
            _decimal(positive_rate) >= thresholds.minimum_positive_fold_rate,
            positive_rate,
            thresholds.minimum_positive_fold_rate,
        ),
        _gate(
            "aggregate_cumulative_return",
            _decimal(cumulative_return) > thresholds.minimum_cumulative_return,
            cumulative_return,
            thresholds.minimum_cumulative_return,
        ),
        _gate(
            "aggregate_profit_factor",
            math.isinf(profit_factor) or _decimal(profit_factor) > thresholds.minimum_profit_factor,
            profit_factor,
            thresholds.minimum_profit_factor,
        ),
        _gate(
            "stress_cumulative_return",
            _decimal(stress_cumulative_return) > thresholds.minimum_stress_cumulative_return,
            stress_cumulative_return,
            thresholds.minimum_stress_cumulative_return,
        ),
        _gate(
            "stress_profit_factor",
            math.isinf(stress_profit_factor)
            or _decimal(stress_profit_factor) > thresholds.minimum_stress_profit_factor,
            stress_profit_factor,
            thresholds.minimum_stress_profit_factor,
        ),
        _gate(
            "stress_drawdown",
            _decimal(stress_drawdown) >= -plan.stress_drawdown_limit,
            stress_drawdown,
            -plan.stress_drawdown_limit,
        ),
        _gate(
            "trade_fold_concentration",
            _decimal(trade_concentration) <= thresholds.maximum_fold_concentration,
            trade_concentration,
            thresholds.maximum_fold_concentration,
        ),
        _gate(
            "profit_fold_concentration",
            _decimal(profit_concentration) <= thresholds.maximum_fold_concentration,
            profit_concentration,
            thresholds.maximum_fold_concentration,
        ),
        _gate("cash_benchmark", cumulative_return > 0, cumulative_return, 0),
        _gate(
            "family_baseline_benchmark",
            cumulative_return > baseline_return,
            cumulative_return - baseline_return,
            0,
        ),
        _gate(
            "random_entry_benchmark",
            cumulative_return > random_threshold,
            cumulative_return,
            random_threshold,
        ),
        _gate(
            "selection_adjusted_confidence",
            selection_adjustment.passed,
            selection_adjustment.adjusted_confidence,
            thresholds.selection_confidence,
        ),
    )
    passed = all(gate.passed for gate in gates)
    return HistoricalScreenResult(
        plan_id=plan.plan_id,
        folds=folds,
        aggregate=HistoricalAggregateEvidence(
            completed_trades=completed_trades,
            traded_folds=traded_folds,
            positive_traded_fold_rate=positive_rate,
            cumulative_return=cumulative_return,
            profit_factor="Infinity" if math.isinf(profit_factor) else str(profit_factor),
            stress_cumulative_return=stress_cumulative_return,
            stress_profit_factor=(
                "Infinity" if math.isinf(stress_profit_factor) else str(stress_profit_factor)
            ),
            stress_max_drawdown=stress_drawdown,
            trade_fold_concentration=trade_concentration,
            profit_fold_concentration=profit_concentration,
        ),
        benchmarks=HistoricalBenchmarkEvidence(
            cash_return=0.0,
            family_baseline_return=baseline_return,
            random_entry_samples=random_samples,
        ),
        selection_adjustment=selection_adjustment,
        gates=gates,
        passed=passed,
        disposition="shadow-eligible" if passed else "historical-screen-failed",
    )


def evaluate_family_selection_adjustment(
    plan: HistoricalQualificationPlan,
    *,
    selected_trial_id: str,
    trial_registry_state: Mapping[str, object],
    trial_daily_excess_returns: dict[str, tuple[DailyExcessReturn, ...]],
) -> SelectionAdjustmentResult:
    """Reproduce family selection with a deterministic block-bootstrap max statistic."""
    raw_trials = trial_registry_state.get("trials")
    if not isinstance(raw_trials, list):
        raise ValueError("selection adjustment requires a verified trial registry")
    family_trials = []
    for trial in raw_trials:
        if not isinstance(trial, Mapping):
            raise ValueError("selection adjustment trial registry is malformed")
        if trial.get("experiment_family") != plan.experiment_family:
            continue
        if trial.get("legacy") is True or trial.get("selection_history_incomplete") is True:
            raise ValueError("selection adjustment cannot use incomplete family trial history")
        trial_id = trial.get("trial_id")
        if not isinstance(trial_id, str) or not trial_id:
            raise ValueError("selection adjustment trial identity is malformed")
        family_trials.append(trial_id)
    registered = tuple(sorted(set(family_trials)))
    if len(registered) != len(family_trials) or not registered:
        raise ValueError("registered family trial identities must be unique and non-empty")
    if selected_trial_id not in registered:
        raise ValueError("selected trial is absent from its registered family")
    if plan.benchmarks.family_baseline_trial_id not in registered:
        raise ValueError("preregistered family baseline is absent from the trial family")
    history_incomplete = trial_registry_state.get("selection_history_incomplete") is not False
    epoch = plan.forward_selection_epoch
    if epoch is not None and epoch.prior_selection_history_incomplete is not history_incomplete:
        raise ValueError("forward selection epoch history disclosure differs from the registry")
    if history_incomplete:
        if epoch is None or not epoch.prior_selection_history_incomplete:
            raise ValueError("selection adjustment rejects incomplete trial registry history")
        if registered != epoch.included_trial_ids:
            raise ValueError("forward selection epoch trial universe changed after registration")
        if selected_trial_id != epoch.selected_trial_id:
            raise ValueError("selected trial differs from the forward selection epoch")
        for trial in raw_trials:
            if (
                not isinstance(trial, Mapping)
                or trial.get("experiment_family") != plan.experiment_family
            ):
                continue
            registered_at = trial.get("first_registered_at")
            if not isinstance(registered_at, str):
                raise ValueError("forward selection epoch requires trial registration timestamps")
            if parse_timestamp(registered_at) > epoch.started_at:
                raise ValueError(
                    "forward selection epoch contains a trial registered after it began"
                )
    if set(trial_daily_excess_returns) != set(registered):
        raise ValueError("selection adjustment requires evidence for every registered family trial")
    lengths = {len(trial_daily_excess_returns[trial_id]) for trial_id in registered}
    if len(lengths) != 1:
        raise ValueError("family trial return series must cover identical sessions")
    observation_count = lengths.pop()
    block_sessions = plan.selection_adjustment.block_sessions
    if observation_count < block_sessions:
        raise ValueError("family trial return series is shorter than the bootstrap block")
    series: dict[str, tuple[float, ...]] = {}
    common_sessions: tuple[date, ...] | None = None
    for trial_id in registered:
        observations = trial_daily_excess_returns[trial_id]
        sessions = tuple(observation.session for observation in observations)
        if sessions != tuple(sorted(set(sessions))):
            raise ValueError("family trial return sessions must be unique and chronological")
        if common_sessions is None:
            common_sessions = sessions
        elif sessions != common_sessions:
            raise ValueError("family trial return series must cover identical sessions")
        if sessions != plan.evaluation_sessions:
            raise ValueError(
                "family trial return series must exactly cover frozen evaluation folds"
            )
        values = tuple(float(observation.value) for observation in observations)
        if any(not math.isfinite(value) for value in values):
            raise ValueError("family trial returns must be finite")
        series[trial_id] = values
    observed = sum(series[selected_trial_id]) / observation_count
    centered = {
        trial_id: tuple(value - (sum(values) / observation_count) for value in values)
        for trial_id, values in series.items()
    }
    seed = int(
        hashlib.sha256(f"{plan.plan_id}:selection-adjustment".encode()).hexdigest()[:16],
        16,
    )
    generator = random.Random(seed)
    exceedances = 0
    for _ in range(plan.selection_adjustment.repetitions):
        indices: list[int] = []
        while len(indices) < observation_count:
            start = generator.randrange(observation_count)
            indices.extend((start + offset) % observation_count for offset in range(block_sessions))
        sampled = indices[:observation_count]
        maximum = max(
            sum(centered[trial_id][index] for index in sampled) / observation_count
            for trial_id in registered
        )
        if maximum >= observed:
            exceedances += 1
    repetitions = plan.selection_adjustment.repetitions
    confidence = Decimal(repetitions - exceedances) / Decimal(repetitions + 1)
    return SelectionAdjustmentResult(
        selected_trial_id=selected_trial_id,
        included_trial_ids=registered,
        observed_mean_excess_return=Decimal(str(observed)),
        adjusted_confidence=confidence,
        repetitions=repetitions,
        block_sessions=block_sessions,
        passed=confidence >= plan.thresholds.selection_confidence,
    )


def _validate_forward_selection_epoch(
    epoch: ForwardSelectionEpoch,
    *,
    created_at: datetime,
    family_baseline_trial_id: str,
) -> None:
    if epoch.started_at.tzinfo is None or epoch.started_at.astimezone(UTC) != created_at:
        raise ValueError("forward selection epoch must start with the qualification plan")
    included = epoch.included_trial_ids
    if included != tuple(sorted(set(included))) or not included:
        raise ValueError("forward selection epoch trial identities must be sorted and unique")
    if not epoch.selected_trial_id.strip() or epoch.selected_trial_id not in included:
        raise ValueError("forward selection epoch must include its selected trial")
    if family_baseline_trial_id not in included:
        raise ValueError("forward selection epoch must include its family baseline")
    if epoch.selected_trial_id == family_baseline_trial_id:
        raise ValueError("forward selection epoch baseline must differ from the selected trial")


def _forward_selection_epoch_payload(epoch: ForwardSelectionEpoch) -> dict[str, object]:
    return {
        "started_at": timestamp_text(epoch.started_at.astimezone(UTC)),
        "selected_trial_id": epoch.selected_trial_id,
        "included_trial_ids": list(epoch.included_trial_ids),
        "prior_selection_history_incomplete": epoch.prior_selection_history_incomplete,
    }


def register_shadow(
    plan: HistoricalQualificationPlan,
    screen: HistoricalScreenResult,
    *,
    trial_id: str,
    definition_snapshot_id: str,
    definition_snapshot_byte_count: int,
    registered_at: datetime,
    activation_checkpoint: date,
) -> ShadowRegistration:
    """Create a deterministic Shadow identity only from passing historical evidence."""
    if screen.plan_id != plan.plan_id:
        raise ValueError("historical screen does not belong to the qualification plan")
    if not screen.passed or screen.disposition != "shadow-eligible":
        raise ValueError("only a passing historical screen can register Shadow")
    if screen.selection_adjustment.selected_trial_id != trial_id:
        raise ValueError("Shadow trial does not match the selected historical trial")
    if not definition_snapshot_id.strip() or definition_snapshot_byte_count <= 0:
        raise ValueError("Shadow requires an immutable definition snapshot")
    if registered_at.tzinfo is None:
        raise ValueError("Shadow registration clock must be timezone-aware")
    registered_at = registered_at.astimezone(UTC)
    if registered_at.date() <= plan.folds[-1].outcome_end:
        raise ValueError("Shadow registration must follow completed historical outcomes")
    if activation_checkpoint <= registered_at.date():
        raise ValueError("activation checkpoint must be after Shadow registration")
    activation_policy = ShadowActivationPolicy(
        stress_drawdown_limit=plan.stress_drawdown_limit,
    )
    payload = {
        "schema_version": 1,
        "trial_id": trial_id,
        "historical_plan_id": plan.plan_id,
        "experiment_family": plan.experiment_family,
        "definition_fingerprint": plan.definition_fingerprint,
        "definition_snapshot_id": definition_snapshot_id,
        "definition_snapshot_byte_count": definition_snapshot_byte_count,
        "prospective_start": timestamp_text(registered_at),
        "activation_checkpoint": activation_checkpoint.isoformat(),
        "activation_policy": {
            "minimum_completed_sessions": activation_policy.minimum_completed_sessions,
            "minimum_completed_trades": activation_policy.minimum_completed_trades,
            "minimum_cumulative_return": decimal_text(
                activation_policy.minimum_cumulative_return,
                "minimum_cumulative_return",
            ),
            "minimum_profit_factor": decimal_text(
                activation_policy.minimum_profit_factor,
                "minimum_profit_factor",
            ),
            "minimum_stress_cumulative_return": decimal_text(
                activation_policy.minimum_stress_cumulative_return,
                "minimum_stress_cumulative_return",
            ),
            "minimum_stress_profit_factor": decimal_text(
                activation_policy.minimum_stress_profit_factor,
                "minimum_stress_profit_factor",
            ),
            "stress_drawdown_limit": decimal_text(
                activation_policy.stress_drawdown_limit,
                "stress_drawdown_limit",
            ),
        },
        "cost_policies": _cost_policy_payload(
            plan.base_cost_policy,
            plan.stress_cost_policy,
        ),
    }
    shadow_id = "shadow-" + hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    return ShadowRegistration(
        shadow_id=shadow_id,
        trial_id=trial_id,
        historical_plan_id=plan.plan_id,
        experiment_family=plan.experiment_family,
        definition_fingerprint=plan.definition_fingerprint,
        definition_snapshot_id=definition_snapshot_id,
        definition_snapshot_byte_count=definition_snapshot_byte_count,
        prospective_start=registered_at,
        activation_checkpoint=activation_checkpoint,
        activation_policy=activation_policy,
        base_cost_policy=plan.base_cost_policy,
        stress_cost_policy=plan.stress_cost_policy,
    )


def restart_shadow_registration(
    prior: ShadowRegistration,
    plan: HistoricalQualificationPlan,
    screen: HistoricalScreenResult,
    *,
    trial_id: str,
    definition_snapshot_id: str,
    definition_snapshot_byte_count: int,
    registered_at: datetime,
    activation_checkpoint: date,
) -> ShadowRegistration:
    """Start a new qualified Shadow identity without carrying prior evidence forward."""
    if plan.definition_fingerprint == prior.definition_fingerprint:
        raise ValueError("Shadow restart requires an outcome-relevant definition change")
    if registered_at.tzinfo is None or registered_at.astimezone(UTC) <= prior.prospective_start:
        raise ValueError("Shadow restart must occur after the prior registration")
    candidate = register_shadow(
        plan,
        screen,
        trial_id=trial_id,
        definition_snapshot_id=definition_snapshot_id,
        definition_snapshot_byte_count=definition_snapshot_byte_count,
        registered_at=registered_at,
        activation_checkpoint=activation_checkpoint,
    )
    identity = {
        "schema_version": 1,
        "prior_shadow_id": prior.shadow_id,
        "registration_id": candidate.shadow_id,
    }
    shadow_id = "shadow-" + hashlib.sha256(canonical_json_bytes(identity)).hexdigest()
    return replace(
        candidate,
        shadow_id=shadow_id,
        prior_shadow_id=prior.shadow_id,
    )


def build_shadow_evidence(
    registration: ShadowRegistration,
    *,
    current_definition_fingerprint: str,
    sleeve_input: CanonicalSleeveInput,
    as_of: date,
    completed_through: date,
    observed_at: datetime,
    session_calendar: SessionCalendar,
    base_policy: ExecutionCostPolicy,
    stress_policy: ExecutionCostPolicy,
    critical_drift: bool,
) -> ShadowEvidence:
    """Run prospective candidates through canonical simulated execution."""
    if (
        base_policy != registration.base_cost_policy
        or stress_policy != registration.stress_cost_policy
    ):
        raise ValueError("Shadow cost policies differ from its frozen registration")
    if current_definition_fingerprint != registration.definition_fingerprint:
        raise ShadowRestartRequired("outcome-relevant definition changed; Shadow must restart")
    if as_of <= registration.prospective_start.date():
        raise ValueError("Shadow evidence must be observed after formal registration")
    if observed_at.tzinfo is None:
        raise ValueError("Shadow evidence observation clock must be timezone-aware")
    trusted_cutoff = session_calendar.latest_completed_session(observed_at)
    if completed_through != trusted_cutoff or as_of > completed_through:
        raise ValueError("Shadow evidence cutoff is not a completed market session")
    expected_sessions = tuple(
        timestamp.date()
        for timestamp in session_calendar.sessions_in_range(
            registration.prospective_start.date(),
            as_of,
        )
        if timestamp.date() > registration.prospective_start.date()
    )
    calendar = tuple(
        session
        for session in sleeve_input.calendar
        if registration.prospective_start.date() < pd.Timestamp(session).date() <= as_of
    )
    if tuple(pd.Timestamp(session).date() for session in calendar) != expected_sessions:
        raise ValueError("Shadow evidence calendar differs from trusted completed sessions")
    candidates = tuple(
        candidate
        for candidate in sleeve_input.candidates
        if registration.prospective_start.date() < candidate.signal_date <= as_of
    )
    if any(
        candidate.exit_date is not None and candidate.exit_date > as_of for candidate in candidates
    ):
        raise ValueError("Shadow candidate exit occurs after the evidence cutoff")
    raw_signals = tuple(
        signal
        for signal in sleeve_input.raw_signals
        if registration.prospective_start.date() < signal <= as_of
    )
    legacy_signals = tuple(
        signal
        for signal in sleeve_input.legacy_signals
        if registration.prospective_start.date() < signal <= as_of
    )
    legacy_candidates = tuple(
        candidate
        for candidate in sleeve_input.legacy_candidates
        if registration.prospective_start.date() < candidate.signal_date <= as_of
    )
    evaluation = evaluate_canonical_sleeve_input(
        CanonicalSleeveInput(
            calendar=calendar,
            close_prices=sleeve_input.close_prices.reindex(pd.DatetimeIndex(calendar)),
            candidates=candidates,
            raw_signals=raw_signals,
            legacy_signals=legacy_signals,
            legacy_candidates=legacy_candidates,
            initial_capital=sleeve_input.initial_capital,
        ),
        base_policy=base_policy,
        stress_policy=stress_policy,
    )
    proposals = tuple(_shadow_proposal(registration, candidate) for candidate in candidates)
    proposals_by_identity = {
        (candidate.signal_date, candidate.entry_date): proposal
        for candidate, proposal in zip(candidates, proposals, strict=True)
    }
    if len(proposals_by_identity) != len(proposals):
        raise ValueError("Shadow candidates contain duplicate proposal terms")
    fills: list[CanonicalSimulatedFill] = []
    pnl_values: list[float] = []
    for trade in evaluation.scenarios.base_net.trades:
        if trade.status != "completed":
            continue
        proposal = proposals_by_identity.get((trade.signal_date, trade.entry_date))
        if proposal is None:
            raise ValueError("canonical Shadow fill has no paper proposal")
        if trade.executed_entry_price is None or trade.executed_exit_price is None:
            raise ValueError("canonical Shadow fill lacks executed prices")
        pnl = _trade_pnl(trade)
        pnl_values.append(pnl)
        fills.append(
            CanonicalSimulatedFill(
                proposal_id=proposal.proposal_id,
                quantity=trade.quantity,
                executed_entry_price=trade.executed_entry_price,
                executed_exit_price=trade.executed_exit_price,
                pnl=pnl,
            )
        )
    gross_profit = sum(value for value in pnl_values if value > 0)
    gross_loss = abs(sum(value for value in pnl_values if value < 0))
    profit_factor = gross_profit / gross_loss if gross_loss else (math.inf if gross_profit else 0.0)
    stress_pnl_values = [
        _trade_pnl(trade)
        for trade in evaluation.scenarios.stress_net.trades
        if trade.status == "completed"
    ]
    stress_gross_profit = sum(value for value in stress_pnl_values if value > 0)
    stress_gross_loss = abs(sum(value for value in stress_pnl_values if value < 0))
    stress_profit_factor = (
        stress_gross_profit / stress_gross_loss
        if stress_gross_loss
        else (math.inf if stress_gross_profit else 0.0)
    )
    return ShadowEvidence(
        shadow_id=registration.shadow_id,
        definition_fingerprint=registration.definition_fingerprint,
        as_of=as_of,
        data_cutoff=completed_through,
        completed_sessions=len(calendar),
        paper_proposals=proposals,
        simulated_fills=tuple(fills),
        cumulative_return=evaluation.base_net_metrics.total_return,
        profit_factor="Infinity" if math.isinf(profit_factor) else str(profit_factor),
        stress_cumulative_return=evaluation.stress_net_metrics.total_return,
        stress_profit_factor=(
            "Infinity" if math.isinf(stress_profit_factor) else str(stress_profit_factor)
        ),
        stress_max_drawdown=evaluation.stress_net_metrics.max_drawdown,
        critical_drift=critical_drift,
    )


def evaluate_shadow_activation(
    registration: ShadowRegistration,
    evidence: ShadowEvidence,
    *,
    current_definition_fingerprint: str | None,
) -> ShadowActivationEvaluation:
    """Evaluate prospective gates without automatically making a strategy Active."""
    definition_matches = (
        current_definition_fingerprint is not None
        and current_definition_fingerprint == registration.definition_fingerprint
        and evidence.definition_fingerprint == registration.definition_fingerprint
    )
    policy = registration.activation_policy
    profit_factor = (
        math.inf if evidence.profit_factor == "Infinity" else float(evidence.profit_factor)
    )
    gates = (
        _gate(
            "shadow_identity",
            evidence.shadow_id == registration.shadow_id,
            evidence.shadow_id,
            registration.shadow_id,
        ),
        _gate(
            "definition_unchanged",
            definition_matches,
            current_definition_fingerprint or "missing",
            registration.definition_fingerprint,
        ),
        _gate(
            "activation_checkpoint",
            evidence.as_of >= registration.activation_checkpoint,
            evidence.as_of,
            registration.activation_checkpoint,
        ),
        _gate(
            "completed_sessions",
            evidence.completed_sessions >= policy.minimum_completed_sessions,
            evidence.completed_sessions,
            policy.minimum_completed_sessions,
        ),
        _gate(
            "completed_trades",
            len(evidence.simulated_fills) >= policy.minimum_completed_trades,
            len(evidence.simulated_fills),
            policy.minimum_completed_trades,
        ),
        _gate(
            "prospective_cumulative_return",
            _decimal(evidence.cumulative_return) > policy.minimum_cumulative_return,
            evidence.cumulative_return,
            policy.minimum_cumulative_return,
        ),
        _gate(
            "prospective_profit_factor",
            math.isinf(profit_factor) or _decimal(profit_factor) > policy.minimum_profit_factor,
            profit_factor,
            policy.minimum_profit_factor,
        ),
        _gate(
            "stress_cumulative_return",
            _decimal(evidence.stress_cumulative_return) > policy.minimum_stress_cumulative_return,
            evidence.stress_cumulative_return,
            policy.minimum_stress_cumulative_return,
        ),
        _gate(
            "stress_profit_factor",
            (
                evidence.stress_profit_factor == "Infinity"
                or _decimal(float(evidence.stress_profit_factor))
                > policy.minimum_stress_profit_factor
            ),
            evidence.stress_profit_factor,
            policy.minimum_stress_profit_factor,
        ),
        _gate(
            "stress_drawdown",
            _decimal(evidence.stress_max_drawdown) >= -policy.stress_drawdown_limit,
            evidence.stress_max_drawdown,
            -policy.stress_drawdown_limit,
        ),
        _gate("critical_drift", not evidence.critical_drift, evidence.critical_drift, False),
    )
    eligible = all(gate.passed for gate in gates)
    if evidence.shadow_id != registration.shadow_id:
        disposition = "shadow-evidence-conflict"
    elif not definition_matches:
        disposition = "shadow-restart-required"
    elif eligible:
        disposition = "activation-eligible"
    elif evidence.critical_drift:
        disposition = "shadow-blocked"
    else:
        disposition = "shadow-insufficient-evidence"
    return ShadowActivationEvaluation(
        shadow_id=registration.shadow_id,
        gates=gates,
        eligible=eligible,
        disposition=disposition,
    )


def _shadow_proposal(
    registration: ShadowRegistration,
    candidate: CandidateTrade,
) -> ShadowPaperProposal:
    payload = {
        "schema_version": 1,
        "shadow_id": registration.shadow_id,
        "signal_date": candidate.signal_date.isoformat(),
        "entry_date": candidate.entry_date.isoformat(),
        "action": "BUY",
    }
    proposal_id = "shadow-proposal-" + hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    return ShadowPaperProposal(
        proposal_id=proposal_id,
        shadow_id=registration.shadow_id,
        signal_date=candidate.signal_date,
        entry_date=candidate.entry_date,
    )


def _evaluate_folds(
    plan: HistoricalQualificationPlan,
    sleeve_input: CanonicalSleeveInput,
    *,
    base_policy: ExecutionCostPolicy,
    stress_policy: ExecutionCostPolicy,
) -> tuple[HistoricalFoldEvidence, ...]:
    evidence: list[HistoricalFoldEvidence] = []
    session_dates = tuple(pd.Timestamp(session).date() for session in sleeve_input.calendar)
    session_index = {session: index for index, session in enumerate(session_dates)}
    for fold in plan.folds:
        candidates = tuple(
            candidate
            for candidate in sleeve_input.candidates
            if fold.contains_signal(candidate.signal_date)
        )
        for candidate in candidates:
            if candidate.exit_date is None or candidate.exit_date > fold.outcome_end:
                raise ValueError(
                    f"candidate {candidate.signal_date} lacks a complete exit inside {fold.fold_id}"
                )
            try:
                signal_index = session_index[candidate.signal_date]
                entry_index = session_index[candidate.entry_date]
                exit_index = session_index[candidate.exit_date]
            except KeyError as exc:
                raise ValueError("candidate dependency dates are absent from the calendar") from exc
            if entry_index - signal_index > plan.execution_lag_sessions:
                raise ValueError("candidate execution lag exceeds the frozen dependency")
            if exit_index - entry_index > plan.maximum_holding_sessions:
                raise ValueError("candidate holding period exceeds the frozen dependency")
        calendar = tuple(
            session
            for session in sleeve_input.calendar
            if fold.outcome_start <= pd.Timestamp(session).date() <= fold.outcome_end
        )
        close_prices = sleeve_input.close_prices.reindex(pd.DatetimeIndex(calendar))
        raw_signals = tuple(
            signal for signal in sleeve_input.raw_signals if fold.contains_signal(signal)
        )
        legacy_signals = tuple(
            signal for signal in sleeve_input.legacy_signals if fold.contains_signal(signal)
        )
        legacy_candidates = tuple(
            candidate
            for candidate in sleeve_input.legacy_candidates
            if fold.contains_signal(candidate.signal_date)
        )
        evaluation = evaluate_canonical_sleeve_input(
            CanonicalSleeveInput(
                calendar=calendar,
                close_prices=close_prices,
                candidates=candidates,
                raw_signals=raw_signals,
                legacy_signals=legacy_signals,
                legacy_candidates=legacy_candidates,
                initial_capital=sleeve_input.initial_capital,
            ),
            base_policy=base_policy,
            stress_policy=stress_policy,
        )
        completed = tuple(
            trade for trade in evaluation.scenarios.base_net.trades if trade.status == "completed"
        )
        pnl = tuple(_trade_pnl(trade) for trade in completed)
        stress_completed = tuple(
            trade for trade in evaluation.scenarios.stress_net.trades if trade.status == "completed"
        )
        stress_pnl = tuple(_trade_pnl(trade) for trade in stress_completed)
        evidence.append(
            HistoricalFoldEvidence(
                fold_id=fold.fold_id,
                evaluation_year=fold.evaluation_year,
                signal_count=len(raw_signals),
                candidate_count=len(candidates),
                completed_trades=len(completed),
                cumulative_return=evaluation.base_net_metrics.total_return,
                stress_cumulative_return=evaluation.stress_net_metrics.total_return,
                stress_max_drawdown=evaluation.stress_net_metrics.max_drawdown,
                gross_profit=sum(value for value in pnl if value > 0),
                gross_loss=abs(sum(value for value in pnl if value < 0)),
                stress_gross_profit=sum(value for value in stress_pnl if value > 0),
                stress_gross_loss=abs(sum(value for value in stress_pnl if value < 0)),
            )
        )
    return tuple(evidence)


def _evaluate_random_entry_benchmark(
    plan: HistoricalQualificationPlan,
    sleeve_input: CanonicalSleeveInput,
    *,
    base_policy: ExecutionCostPolicy,
    stress_policy: ExecutionCostPolicy,
) -> tuple[ExposureMatchedRandomSample, ...]:
    calendar = tuple(pd.Timestamp(session).normalize() for session in sleeve_input.calendar)
    session_dates = tuple(session.date() for session in calendar)
    session_index = {session: index for index, session in enumerate(session_dates)}
    candidates = tuple(
        candidate
        for candidate in sleeve_input.candidates
        if any(fold.contains_signal(candidate.signal_date) for fold in plan.folds)
    )
    target_completed = sum(
        fold.completed_trades
        for fold in _evaluate_folds(
            plan,
            sleeve_input,
            base_policy=base_policy,
            stress_policy=stress_policy,
        )
    )
    exposures: list[tuple[CandidateTrade, int, int, EvaluationFold]] = []
    for candidate in candidates:
        if candidate.exit_date is None:
            raise ValueError("random-entry benchmark requires complete candidate exits")
        try:
            signal_index = session_index[candidate.signal_date]
            entry_index = session_index[candidate.entry_date]
            exit_index = session_index[candidate.exit_date]
        except KeyError as exc:
            raise ValueError(
                "candidate exposure dates are absent from the evaluation calendar"
            ) from exc
        fold = next(item for item in plan.folds if item.contains_signal(candidate.signal_date))
        exposures.append(
            (
                candidate,
                entry_index - signal_index,
                exit_index - entry_index,
                fold,
            )
        )
    generator = random.Random(plan.benchmarks.random_seed)
    samples: list[ExposureMatchedRandomSample] = []
    for sample_index in range(plan.benchmarks.random_samples):
        randomized: list[CandidateTrade] = []
        holding_sessions: list[int] = []
        for candidate, entry_lag, holding, fold in exposures:
            eligible = [
                index
                for index, session in enumerate(session_dates)
                if fold.contains_signal(session)
                and session.month == candidate.signal_date.month
                and index + entry_lag + holding < len(session_dates)
                and session_dates[index + entry_lag + holding] <= fold.outcome_end
            ]
            if not eligible:
                raise ValueError(
                    f"random-entry benchmark cannot preserve exposure for {candidate.signal_date}"
                )
            random_signal_index = generator.choice(eligible)
            random_entry_index = random_signal_index + entry_lag
            random_exit_index = random_entry_index + holding
            signal_date = session_dates[random_signal_index]
            entry_date = session_dates[random_entry_index]
            exit_date = session_dates[random_exit_index]
            randomized.append(
                CandidateTrade(
                    signal_date=signal_date,
                    entry_date=entry_date,
                    entry_price=_close_price(sleeve_input.close_prices, entry_date),
                    exit_date=exit_date,
                    exit_price=_close_price(sleeve_input.close_prices, exit_date),
                    exit_type=candidate.exit_type,
                )
            )
            holding_sessions.append(holding)
        randomized_input = CanonicalSleeveInput(
            calendar=sleeve_input.calendar,
            close_prices=sleeve_input.close_prices,
            candidates=tuple(randomized),
            raw_signals=tuple(candidate.signal_date for candidate in randomized),
            legacy_signals=tuple(candidate.signal_date for candidate in randomized),
            legacy_candidates=tuple(randomized),
            initial_capital=sleeve_input.initial_capital,
        )
        randomized_folds = _evaluate_folds(
            plan,
            randomized_input,
            base_policy=base_policy,
            stress_policy=stress_policy,
        )
        completed = sum(fold.completed_trades for fold in randomized_folds)
        if completed != target_completed:
            raise ValueError("random-entry benchmark could not preserve completed trade count")
        samples.append(
            ExposureMatchedRandomSample(
                sample_index=sample_index,
                cumulative_return=_compound_return(
                    fold.cumulative_return for fold in randomized_folds
                ),
                completed_trades=completed,
                entry_months=tuple(sorted(candidate.signal_date.month for candidate in randomized)),
                holding_sessions=tuple(sorted(holding_sessions)),
            )
        )
    return tuple(samples)


def _trade_pnl(trade: SleeveTrade) -> float:
    if trade.executed_entry_price is None or trade.executed_exit_price is None:
        raise ValueError("completed canonical trade lacks executed prices")
    entry_cost = trade.quantity * trade.executed_entry_price + trade.entry_fee
    exit_value = trade.quantity * trade.executed_exit_price - trade.exit_fee
    return exit_value - entry_cost


def _close_price(prices: pd.Series, session: date) -> float:
    try:
        value = prices.loc[pd.Timestamp(session)]
    except KeyError as exc:
        raise ValueError(f"random-entry benchmark lacks a close for {session}") from exc
    if pd.isna(value):
        raise ValueError(f"random-entry benchmark close is missing for {session}")
    return float(value)


def _percentile(values: tuple[float, ...], probability: float) -> float:
    if not values:
        raise ValueError("random-entry benchmark requires at least one sample")
    ordered = sorted(values)
    index = max(0, math.ceil(probability * len(ordered)) - 1)
    return ordered[index]


def _compound_return(values) -> float:
    equity = 1.0
    for value in values:
        equity *= 1.0 + value
    return equity - 1.0


def _decimal(value: float) -> Decimal:
    return Decimal(str(value))


def _gate(name: str, passed: bool, actual: object, threshold: object) -> QualificationGate:
    return QualificationGate(
        name=name,
        passed=passed,
        actual=str(actual),
        threshold=str(threshold),
    )


def _threshold_payload(thresholds: HistoricalScreenThresholds) -> dict[str, object]:
    return {
        "minimum_development_years": thresholds.minimum_development_years,
        "minimum_evaluation_folds": thresholds.minimum_evaluation_folds,
        "minimum_completed_trades": thresholds.minimum_completed_trades,
        "minimum_traded_folds": thresholds.minimum_traded_folds,
        "minimum_positive_fold_rate": decimal_text(
            thresholds.minimum_positive_fold_rate,
            "minimum_positive_fold_rate",
        ),
        "minimum_cumulative_return": decimal_text(
            thresholds.minimum_cumulative_return,
            "minimum_cumulative_return",
        ),
        "minimum_profit_factor": decimal_text(
            thresholds.minimum_profit_factor,
            "minimum_profit_factor",
        ),
        "minimum_stress_cumulative_return": decimal_text(
            thresholds.minimum_stress_cumulative_return,
            "minimum_stress_cumulative_return",
        ),
        "minimum_stress_profit_factor": decimal_text(
            thresholds.minimum_stress_profit_factor,
            "minimum_stress_profit_factor",
        ),
        "maximum_fold_concentration": decimal_text(
            thresholds.maximum_fold_concentration,
            "maximum_fold_concentration",
        ),
        "selection_confidence": decimal_text(
            thresholds.selection_confidence,
            "selection_confidence",
        ),
    }


def _cost_policy_payload(
    base: ExecutionCostPolicy,
    stress: ExecutionCostPolicy,
) -> dict[str, object]:
    def scenario(policy: ExecutionCostPolicy) -> dict[str, float]:
        return {
            "entry_slippage_bps": policy.entry_slippage_bps,
            "exit_slippage_bps": policy.exit_slippage_bps,
            "fee_bps_per_side": policy.fee_bps_per_side,
        }

    return {"base": scenario(base), "stress": scenario(stress)}


def validate_historical_thresholds(thresholds: HistoricalScreenThresholds) -> None:
    minimums = {
        "minimum_development_years": (thresholds.minimum_development_years, 3),
        "minimum_evaluation_folds": (thresholds.minimum_evaluation_folds, 5),
        "minimum_completed_trades": (thresholds.minimum_completed_trades, 20),
        "minimum_traded_folds": (thresholds.minimum_traded_folds, 3),
    }
    for name, (actual, floor) in minimums.items():
        if actual < floor:
            raise ValueError(f"{name} cannot be weaker than the Phase 6 specification")
    decimal_floors = {
        "minimum_positive_fold_rate": (
            thresholds.minimum_positive_fold_rate,
            Decimal("0.60"),
        ),
        "minimum_cumulative_return": (
            thresholds.minimum_cumulative_return,
            Decimal("0"),
        ),
        "minimum_profit_factor": (
            thresholds.minimum_profit_factor,
            Decimal("1.10"),
        ),
        "minimum_stress_cumulative_return": (
            thresholds.minimum_stress_cumulative_return,
            Decimal("0"),
        ),
        "minimum_stress_profit_factor": (
            thresholds.minimum_stress_profit_factor,
            Decimal("1"),
        ),
        "selection_confidence": (
            thresholds.selection_confidence,
            Decimal("0.90"),
        ),
    }
    for name, (actual, floor) in decimal_floors.items():
        if not actual.is_finite() or actual < floor:
            raise ValueError(f"{name} cannot be weaker than the Phase 6 specification")
    if (
        not thresholds.maximum_fold_concentration.is_finite()
        or thresholds.maximum_fold_concentration <= 0
        or thresholds.maximum_fold_concentration > Decimal("0.50")
    ):
        raise ValueError(
            "maximum_fold_concentration cannot be weaker than the Phase 6 specification"
        )
    if thresholds.minimum_positive_fold_rate > 1 or thresholds.selection_confidence > 1:
        raise ValueError("qualification rates and confidence cannot exceed one")


def _validate_annual_coverage(sessions: tuple[date, ...], year: int, label: str) -> None:
    annual = tuple(session for session in sessions if session.year == year)
    if (
        len(annual) < 240
        or annual[0].month != 1
        or annual[-1].month != 12
        or (annual[-1] - annual[0]).days < 350
    ):
        raise ValueError(f"{label} year {year} is not a complete annual period")
