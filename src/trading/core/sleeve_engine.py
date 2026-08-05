"""Canonical capital-constrained execution for one strategy sleeve."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import date

import pandas as pd

CANONICAL_SLEEVE_ENGINE_VERSION = "canonical-sleeve-v1"


@dataclass(frozen=True, slots=True)
class ExecutionCostPolicy:
    """Preregistered per-side slippage and fee assumptions in basis points."""

    entry_slippage_bps: float = 0.0
    exit_slippage_bps: float = 0.0
    fee_bps_per_side: float = 0.0

    def __post_init__(self) -> None:
        if (
            min(
                self.entry_slippage_bps,
                self.exit_slippage_bps,
                self.fee_bps_per_side,
            )
            < 0
        ):
            raise ValueError("execution costs cannot be negative")

    @property
    def entry_slippage_rate(self) -> float:
        return self.entry_slippage_bps / 10_000

    @property
    def exit_slippage_rate(self) -> float:
        return self.exit_slippage_bps / 10_000

    @property
    def fee_rate(self) -> float:
        return self.fee_bps_per_side / 10_000


DEFAULT_BASE_COST_POLICY = ExecutionCostPolicy(
    entry_slippage_bps=5.0,
    exit_slippage_bps=5.0,
    fee_bps_per_side=1.0,
)
DEFAULT_STRESS_COST_POLICY = ExecutionCostPolicy(
    entry_slippage_bps=20.0,
    exit_slippage_bps=20.0,
    fee_bps_per_side=2.0,
)


@dataclass(frozen=True, slots=True)
class CandidateTrade:
    """One raw strategy trade candidate before sleeve-capital constraints."""

    signal_date: date
    entry_date: date
    entry_price: float
    exit_date: date | None = None
    exit_price: float | None = None
    exit_type: str | None = None


@dataclass(slots=True)
class SleeveTrade:
    """One candidate's canonical execution outcome."""

    signal_date: date
    entry_date: date
    entry_price: float
    exit_date: date | None
    exit_price: float | None
    exit_type: str | None
    status: str
    quantity: float = 0.0
    reason: str | None = None
    executed_entry_price: float | None = None
    executed_exit_price: float | None = None
    entry_fee: float = 0.0
    exit_fee: float = 0.0
    total_fees: float = 0.0


@dataclass(frozen=True, slots=True)
class DailySleevePoint:
    """End-of-session state for one isolated strategy sleeve."""

    date: pd.Timestamp
    equity: float
    cash: float
    position_value: float
    daily_return: float | None
    drawdown: float
    utilization: float
    open_positions: int


@dataclass(frozen=True, slots=True)
class SleeveSimulation:
    """Canonical executions and the resulting daily sleeve-equity path."""

    initial_capital: float
    trades: tuple[SleeveTrade, ...]
    daily_equity: tuple[DailySleevePoint, ...]
    raw_candidates: tuple[CandidateTrade, ...]

    @property
    def final_equity(self) -> float:
        return self.daily_equity[-1].equity if self.daily_equity else self.initial_capital


@dataclass(frozen=True, slots=True)
class CostScenarioResults:
    """Gross, base-net, and stress-net paths for identical raw candidates."""

    gross: SleeveSimulation
    base_net: SleeveSimulation
    stress_net: SleeveSimulation
    base_policy: ExecutionCostPolicy
    stress_policy: ExecutionCostPolicy


@dataclass(frozen=True, slots=True)
class SleeveMetrics:
    """Path-dependent return and risk metrics from daily sleeve equity."""

    initial_equity: float
    final_equity: float
    total_return: float
    annualized_return: float | None
    annualized_volatility: float | None
    sharpe_ratio: float | None
    max_drawdown: float


@dataclass(frozen=True, slots=True)
class ParityDifference:
    """One classified difference between legacy and canonical behavior."""

    scope: str
    classification: str
    reason: str
    signal_date: date | None = None


@dataclass(frozen=True, slots=True)
class TradeParityComparison:
    """Legacy candidate values beside one canonical execution outcome."""

    signal_date: date
    legacy_entry_price: float | None
    legacy_exit_price: float | None
    canonical_status: str
    canonical_executed_entry_price: float | None
    canonical_executed_exit_price: float | None
    canonical_quantity: float
    canonical_total_fees: float


@dataclass(frozen=True, slots=True)
class ParityReport:
    """Signal and execution differences for a canonical migration."""

    signal_differences: tuple[ParityDifference, ...]
    trade_differences: tuple[ParityDifference, ...]
    trade_comparisons: tuple[TradeParityComparison, ...]

    @property
    def has_unclassified_differences(self) -> bool:
        return any(
            item.classification == "unclassified"
            for item in (*self.signal_differences, *self.trade_differences)
        )


@dataclass(frozen=True, slots=True)
class CanonicalSleeveEvaluation:
    """Decision-grade sleeve evidence shared by research and followup."""

    raw_signals: tuple[date, ...]
    raw_candidates: tuple[CandidateTrade, ...]
    scenarios: CostScenarioResults
    gross_metrics: SleeveMetrics
    base_net_metrics: SleeveMetrics
    stress_net_metrics: SleeveMetrics
    ranking_metrics: SleeveMetrics
    parity_report: ParityReport


@dataclass(frozen=True, slots=True)
class CanonicalSleeveInput:
    """Typed raw research input consumed by the shared sleeve evaluator."""

    calendar: tuple[pd.Timestamp, ...]
    close_prices: pd.Series
    candidates: tuple[CandidateTrade, ...]
    raw_signals: tuple[date, ...]
    legacy_signals: tuple[date, ...]
    legacy_candidates: tuple[CandidateTrade, ...]
    initial_capital: float = 1.0


class CanonicalSleeveEngine:
    """Apply one-position and isolated-capital policy to raw candidates."""

    def __init__(
        self,
        *,
        initial_capital: float = 1.0,
        cost_policy: ExecutionCostPolicy | None = None,
    ) -> None:
        if initial_capital <= 0:
            raise ValueError("initial_capital must be positive")
        self.initial_capital = float(initial_capital)
        self.cost_policy = cost_policy or ExecutionCostPolicy()

    def run(
        self,
        *,
        calendar: Sequence[pd.Timestamp],
        close_prices: pd.Series,
        candidates: Sequence[CandidateTrade],
    ) -> SleeveSimulation:
        """Simulate candidates without borrowing, pyramiding, or rebalancing."""
        sessions = tuple(pd.Timestamp(value).normalize() for value in calendar)
        ordered = tuple(sorted(candidates, key=lambda item: (item.entry_date, item.signal_date)))
        entries: dict[pd.Timestamp, list[CandidateTrade]] = {}
        for candidate in ordered:
            entries.setdefault(pd.Timestamp(candidate.entry_date), []).append(candidate)

        marks = close_prices.reindex(pd.DatetimeIndex(sessions)).ffill()
        cash = self.initial_capital
        active: tuple[CandidateTrade, SleeveTrade] | None = None
        trades: list[SleeveTrade] = []
        points: list[DailySleevePoint] = []
        running_peak = self.initial_capital
        previous_equity: float | None = None

        for session in sessions:
            if active is not None:
                candidate, record = active
                if candidate.exit_type == "time_expiry" and _is_exit_session(candidate, session):
                    cash = _exit_proceeds(candidate, record, self.cost_policy)
                    active = None

            for candidate in entries.get(session, []):
                record = SleeveTrade(
                    signal_date=candidate.signal_date,
                    entry_date=candidate.entry_date,
                    entry_price=float(candidate.entry_price),
                    exit_date=candidate.exit_date,
                    exit_price=candidate.exit_price,
                    exit_type=candidate.exit_type,
                    status="open",
                )
                if active is not None:
                    record.status = "skipped"
                    record.reason = "position_already_open"
                    trades.append(record)
                    continue
                executed_entry = candidate.entry_price * (1 + self.cost_policy.entry_slippage_rate)
                record.executed_entry_price = executed_entry
                record.quantity = cash / (executed_entry * (1 + self.cost_policy.fee_rate))
                record.entry_fee = record.quantity * executed_entry * self.cost_policy.fee_rate
                record.total_fees = record.entry_fee
                cash = 0.0
                trades.append(record)
                active = (candidate, record)

            if active is not None:
                candidate, record = active
                if candidate.exit_type != "time_expiry" and _is_exit_session(candidate, session):
                    cash = _exit_proceeds(candidate, record, self.cost_policy)
                    active = None

            position_value = 0.0
            if active is not None:
                candidate, record = active
                mark = marks.loc[session]
                position_value = record.quantity * (
                    float(mark) if not pd.isna(mark) else candidate.entry_price
                )

            equity = cash + position_value
            running_peak = max(running_peak, equity)
            points.append(
                DailySleevePoint(
                    date=session,
                    equity=equity,
                    cash=cash,
                    position_value=position_value,
                    daily_return=(
                        equity / previous_equity - 1 if previous_equity is not None else None
                    ),
                    drawdown=equity / running_peak - 1,
                    utilization=position_value / equity if equity else 0.0,
                    open_positions=int(active is not None),
                )
            )
            previous_equity = equity

        trades.sort(key=lambda item: item.signal_date)
        return SleeveSimulation(
            initial_capital=self.initial_capital,
            trades=tuple(trades),
            daily_equity=tuple(points),
            raw_candidates=ordered,
        )


def evaluate_cost_scenarios(
    *,
    calendar: Sequence[pd.Timestamp],
    close_prices: pd.Series,
    candidates: Sequence[CandidateTrade],
    initial_capital: float,
    base_policy: ExecutionCostPolicy,
    stress_policy: ExecutionCostPolicy,
) -> CostScenarioResults:
    """Run gross, base-net, and stress-net paths against identical candidates."""
    validate_cost_scenario_policies(base_policy, stress_policy)
    common = {
        "calendar": calendar,
        "close_prices": close_prices,
        "candidates": candidates,
    }
    return CostScenarioResults(
        gross=CanonicalSleeveEngine(initial_capital=initial_capital).run(**common),
        base_net=CanonicalSleeveEngine(
            initial_capital=initial_capital,
            cost_policy=base_policy,
        ).run(**common),
        stress_net=CanonicalSleeveEngine(
            initial_capital=initial_capital,
            cost_policy=stress_policy,
        ).run(**common),
        base_policy=base_policy,
        stress_policy=stress_policy,
    )


def evaluate_canonical_sleeve(
    *,
    calendar: Sequence[pd.Timestamp],
    close_prices: pd.Series,
    candidates: Sequence[CandidateTrade],
    initial_capital: float,
    base_policy: ExecutionCostPolicy,
    stress_policy: ExecutionCostPolicy,
    legacy_candidates: Sequence[CandidateTrade],
    raw_signals: Sequence[date] | None = None,
    legacy_signals: Sequence[date] | None = None,
) -> CanonicalSleeveEvaluation:
    """Evaluate one candidate stream under the canonical base-net ranking policy."""
    scenarios = evaluate_cost_scenarios(
        calendar=calendar,
        close_prices=close_prices,
        candidates=candidates,
        initial_capital=initial_capital,
        base_policy=base_policy,
        stress_policy=stress_policy,
    )
    gross_metrics = _simulation_metrics(scenarios.gross)
    base_net_metrics = _simulation_metrics(scenarios.base_net)
    stress_net_metrics = _simulation_metrics(scenarios.stress_net)
    canonical_signal_dates = tuple(
        raw_signals
        if raw_signals is not None
        else (candidate.signal_date for candidate in candidates)
    )
    return CanonicalSleeveEvaluation(
        raw_signals=canonical_signal_dates,
        raw_candidates=tuple(candidates),
        scenarios=scenarios,
        gross_metrics=gross_metrics,
        base_net_metrics=base_net_metrics,
        stress_net_metrics=stress_net_metrics,
        ranking_metrics=base_net_metrics,
        parity_report=build_parity_report(
            legacy_candidates=legacy_candidates,
            canonical=scenarios.base_net,
            legacy_signals=legacy_signals,
            canonical_signals=canonical_signal_dates,
        ),
    )


def evaluate_canonical_sleeve_input(
    sleeve_input: CanonicalSleeveInput,
    *,
    base_policy: ExecutionCostPolicy,
    stress_policy: ExecutionCostPolicy,
) -> CanonicalSleeveEvaluation:
    """Run one typed research/followup input through canonical sleeve evaluation."""
    return evaluate_canonical_sleeve(
        calendar=sleeve_input.calendar,
        close_prices=sleeve_input.close_prices,
        candidates=sleeve_input.candidates,
        initial_capital=sleeve_input.initial_capital,
        base_policy=base_policy,
        stress_policy=stress_policy,
        legacy_candidates=sleeve_input.legacy_candidates,
        raw_signals=sleeve_input.raw_signals,
        legacy_signals=sleeve_input.legacy_signals,
    )


def compute_daily_equity_metrics(
    equity: Sequence[float],
    *,
    initial_equity: float,
) -> SleeveMetrics:
    """Calculate ranking metrics from a canonical daily sleeve-equity path."""
    if initial_equity <= 0:
        raise ValueError("initial_equity must be positive")
    values = pd.Series(equity, dtype=float)
    if values.empty:
        return SleeveMetrics(
            initial_equity=initial_equity,
            final_equity=initial_equity,
            total_return=0.0,
            annualized_return=None,
            annualized_volatility=None,
            sharpe_ratio=None,
            max_drawdown=0.0,
        )

    final = float(values.iloc[-1])
    total_return = (final - initial_equity) / initial_equity
    anchored = pd.concat(
        [pd.Series([initial_equity], dtype=float), values],
        ignore_index=True,
    )
    observations = len(values)
    annualized_return = (
        (final / initial_equity) ** (252 / observations) - 1
        if observations > 0 and final > 0
        else None
    )
    daily_returns = anchored.pct_change().dropna()
    daily_std = float(daily_returns.std(ddof=1)) if len(daily_returns) > 1 else 0.0
    annualized_volatility = daily_std * math.sqrt(252) if daily_std > 0 else None
    sharpe_ratio = (
        float(daily_returns.mean()) / daily_std * math.sqrt(252) if daily_std > 0 else None
    )
    drawdown = anchored / anchored.cummax() - 1
    return SleeveMetrics(
        initial_equity=initial_equity,
        final_equity=final,
        total_return=total_return,
        annualized_return=annualized_return,
        annualized_volatility=annualized_volatility,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=float(drawdown.min()),
    )


def build_parity_report(
    *,
    legacy_candidates: Sequence[CandidateTrade],
    canonical: SleeveSimulation,
    legacy_signals: Sequence[date] | None = None,
    canonical_signals: Sequence[date] | None = None,
) -> ParityReport:
    """Classify signal and trade differences introduced by canonical execution."""
    legacy_signal_counts = Counter(
        legacy_signals
        if legacy_signals is not None
        else (item.signal_date for item in legacy_candidates)
    )
    canonical_signal_counts = Counter(
        canonical_signals
        if canonical_signals is not None
        else (item.signal_date for item in canonical.raw_candidates)
    )
    signal_differences: list[ParityDifference] = []
    for signal_date, count in (legacy_signal_counts - canonical_signal_counts).items():
        signal_differences.extend(
            ParityDifference(
                scope="signal",
                classification="unclassified",
                reason="missing_from_canonical_candidates",
                signal_date=signal_date,
            )
            for _ in range(count)
        )
    for signal_date, count in (canonical_signal_counts - legacy_signal_counts).items():
        signal_differences.extend(
            ParityDifference(
                scope="signal",
                classification="unclassified",
                reason="missing_from_legacy_candidates",
                signal_date=signal_date,
            )
            for _ in range(count)
        )

    legacy_trades = Counter(_candidate_identity(item) for item in legacy_candidates)
    canonical_trades = Counter(
        _sleeve_trade_identity(item) for item in canonical.trades if item.status != "skipped"
    )
    skipped_trades = Counter(
        _sleeve_trade_identity(item) for item in canonical.trades if item.status == "skipped"
    )
    trade_differences: list[ParityDifference] = []
    for identity, count in (legacy_trades - canonical_trades).items():
        intentional_count = min(count, skipped_trades[identity])
        trade_differences.extend(
            ParityDifference(
                scope="trade",
                classification="intentional_policy_difference",
                reason="position_already_open",
                signal_date=identity[0],
            )
            for _ in range(intentional_count)
        )
        trade_differences.extend(
            ParityDifference(
                scope="trade",
                classification="unclassified",
                reason="missing_from_canonical_trades",
                signal_date=identity[0],
            )
            for _ in range(count - intentional_count)
        )
    for identity, count in (canonical_trades - legacy_trades).items():
        trade_differences.extend(
            ParityDifference(
                scope="trade",
                classification="unclassified",
                reason="missing_from_legacy_trades",
                signal_date=identity[0],
            )
            for _ in range(count)
        )

    legacy_matches: dict[tuple[object, ...], list[CandidateTrade]] = {}
    for candidate in legacy_candidates:
        legacy_matches.setdefault(_candidate_identity(candidate), []).append(candidate)
    trade_comparisons: list[TradeParityComparison] = []
    for trade in canonical.trades:
        matches = legacy_matches.get(_sleeve_trade_identity(trade), [])
        legacy = matches.pop(0) if matches else None
        trade_comparisons.append(
            TradeParityComparison(
                signal_date=trade.signal_date,
                legacy_entry_price=legacy.entry_price if legacy is not None else None,
                legacy_exit_price=legacy.exit_price if legacy is not None else None,
                canonical_status=trade.status,
                canonical_executed_entry_price=trade.executed_entry_price,
                canonical_executed_exit_price=trade.executed_exit_price,
                canonical_quantity=trade.quantity,
                canonical_total_fees=trade.total_fees,
            )
        )
        if legacy is None or trade.status == "skipped":
            continue
        if (
            trade.executed_entry_price != legacy.entry_price
            or trade.executed_exit_price != legacy.exit_price
            or trade.total_fees > 0
        ):
            trade_differences.append(
                ParityDifference(
                    scope="trade",
                    classification="intentional_policy_difference",
                    reason="execution_cost_policy",
                    signal_date=trade.signal_date,
                )
            )
        expected_status = "open" if legacy.exit_date is None else "completed"
        if trade.status != expected_status:
            trade_differences.append(
                ParityDifference(
                    scope="trade",
                    classification="unclassified",
                    reason="execution_status_mismatch",
                    signal_date=trade.signal_date,
                )
            )
    return ParityReport(
        signal_differences=tuple(signal_differences),
        trade_differences=tuple(trade_differences),
        trade_comparisons=tuple(trade_comparisons),
    )


def serialize_canonical_sleeve_evidence(
    evaluation: CanonicalSleeveEvaluation,
) -> dict[str, object]:
    """Return JSON-safe canonical evidence for a versioned research result."""
    scenarios = evaluation.scenarios
    return {
        "engine_version": CANONICAL_SLEEVE_ENGINE_VERSION,
        "ranking_scenario": "base_net",
        "initial_capital": scenarios.gross.initial_capital,
        "cost_policies": {
            "base": asdict(scenarios.base_policy),
            "stress": asdict(scenarios.stress_policy),
        },
        "raw_signals": [signal.isoformat() for signal in evaluation.raw_signals],
        "raw_candidates": [
            _candidate_payload(candidate) for candidate in evaluation.raw_candidates
        ],
        "scenarios": {
            "gross": _scenario_payload(scenarios.gross, evaluation.gross_metrics),
            "base_net": _scenario_payload(
                scenarios.base_net,
                evaluation.base_net_metrics,
            ),
            "stress_net": _scenario_payload(
                scenarios.stress_net,
                evaluation.stress_net_metrics,
            ),
        },
        "parity": {
            "signal_differences": [
                _difference_payload(item) for item in evaluation.parity_report.signal_differences
            ],
            "trade_differences": [
                _difference_payload(item) for item in evaluation.parity_report.trade_differences
            ],
            "trade_comparisons": [
                _trade_comparison_payload(item)
                for item in evaluation.parity_report.trade_comparisons
            ],
            "has_unclassified_differences": (evaluation.parity_report.has_unclassified_differences),
        },
    }


def _is_exit_session(candidate: CandidateTrade, session: pd.Timestamp) -> bool:
    return candidate.exit_date is not None and pd.Timestamp(candidate.exit_date) == session


def validate_cost_scenario_policies(
    base_policy: ExecutionCostPolicy,
    stress_policy: ExecutionCostPolicy,
) -> None:
    base = (
        base_policy.entry_slippage_bps,
        base_policy.exit_slippage_bps,
        base_policy.fee_bps_per_side,
    )
    stress = (
        stress_policy.entry_slippage_bps,
        stress_policy.exit_slippage_bps,
        stress_policy.fee_bps_per_side,
    )
    if any(
        stress_value < base_value for base_value, stress_value in zip(base, stress, strict=True)
    ):
        raise ValueError("stress cost policy cannot be less adverse than base policy")
    if stress == base:
        raise ValueError("stress cost policy must be more adverse than base policy")


def _candidate_identity(candidate: CandidateTrade) -> tuple[object, ...]:
    return (
        candidate.signal_date,
        candidate.entry_date,
        candidate.entry_price,
        candidate.exit_date,
        candidate.exit_price,
        candidate.exit_type,
    )


def _sleeve_trade_identity(trade: SleeveTrade) -> tuple[object, ...]:
    return (
        trade.signal_date,
        trade.entry_date,
        trade.entry_price,
        trade.exit_date,
        trade.exit_price,
        trade.exit_type,
    )


def _simulation_metrics(simulation: SleeveSimulation) -> SleeveMetrics:
    return compute_daily_equity_metrics(
        [point.equity for point in simulation.daily_equity],
        initial_equity=simulation.initial_capital,
    )


def _candidate_payload(candidate: CandidateTrade) -> dict[str, object]:
    return {
        "signal_date": candidate.signal_date.isoformat(),
        "entry_date": candidate.entry_date.isoformat(),
        "entry_price": candidate.entry_price,
        "exit_date": candidate.exit_date.isoformat() if candidate.exit_date else None,
        "exit_price": candidate.exit_price,
        "exit_type": candidate.exit_type,
    }


def _scenario_payload(
    simulation: SleeveSimulation,
    metrics: SleeveMetrics,
) -> dict[str, object]:
    return {
        "metrics": asdict(metrics),
        "trades": [
            {
                "signal_date": trade.signal_date.isoformat(),
                "entry_date": trade.entry_date.isoformat(),
                "entry_price": trade.entry_price,
                "exit_date": trade.exit_date.isoformat() if trade.exit_date else None,
                "exit_price": trade.exit_price,
                "exit_type": trade.exit_type,
                "status": trade.status,
                "quantity": trade.quantity,
                "reason": trade.reason,
                "executed_entry_price": trade.executed_entry_price,
                "executed_exit_price": trade.executed_exit_price,
                "entry_fee": trade.entry_fee,
                "exit_fee": trade.exit_fee,
                "total_fees": trade.total_fees,
            }
            for trade in simulation.trades
        ],
        "daily_equity": [
            {
                **asdict(point),
                "date": point.date.date().isoformat(),
            }
            for point in simulation.daily_equity
        ],
    }


def _difference_payload(difference: ParityDifference) -> dict[str, object]:
    return {
        "scope": difference.scope,
        "classification": difference.classification,
        "reason": difference.reason,
        "signal_date": (difference.signal_date.isoformat() if difference.signal_date else None),
    }


def _trade_comparison_payload(
    comparison: TradeParityComparison,
) -> dict[str, object]:
    return {
        **asdict(comparison),
        "signal_date": comparison.signal_date.isoformat(),
    }


def _exit_price(candidate: CandidateTrade) -> float:
    if candidate.exit_price is None:
        raise ValueError("completed candidate requires exit_price")
    return float(candidate.exit_price)


def _exit_proceeds(
    candidate: CandidateTrade,
    record: SleeveTrade,
    policy: ExecutionCostPolicy,
) -> float:
    executed_exit = _exit_price(candidate) * (1 - policy.exit_slippage_rate)
    record.executed_exit_price = executed_exit
    exit_value = record.quantity * executed_exit
    exit_fee = exit_value * policy.fee_rate
    record.exit_fee = exit_fee
    record.total_fees += exit_fee
    record.status = "completed"
    return exit_value - exit_fee
