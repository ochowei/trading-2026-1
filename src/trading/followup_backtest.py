"""Structured backtest for the current followup strategy portfolio."""

from __future__ import annotations

import math
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import date as date_type
from datetime import datetime
from typing import Any, TextIO

import numpy as np
import pandas as pd

from trading.core.data_fetcher import DataFetcher
from trading.experiments import get_experiment
from trading.followup import _drop_incomplete_bar

DEFAULT_DAYS = 126
INITIAL_CAPITAL = 100_000.0


@dataclass(frozen=True)
class DailyEquityPoint:
    date: pd.Timestamp
    equity: float
    cash: float
    position_value: float
    daily_return: float | None
    drawdown: float
    utilization: float
    open_positions: int


@dataclass
class TradeRecord:
    status: str
    signal_date: str
    entry_date: str | None = None
    exit_date: str | None = None
    entry_price: float | None = None
    exit_price: float | None = None
    mark_price: float | None = None
    quantity: float = 0.0
    return_pct: float | None = None
    exit_type: str | None = None
    reason: str | None = None


@dataclass
class StrategyBacktestResult:
    experiment_name: str
    label: str
    ticker: str
    requested_days: int
    sleeve_initial_cash: float
    period_start: pd.Timestamp | None = None
    period_end: pd.Timestamp | None = None
    evaluation_rows: int = 0
    warmup_rows: int = 0
    missing_sessions: int = 0
    signal_count: int = 0
    completed_count: int = 0
    open_count: int = 0
    unfilled_count: int = 0
    skipped_count: int = 0
    win_rate: float | None = None
    cumulative_return: float | None = None
    avg_trade_return: float | None = None
    sharpe_ratio: float | None = None
    max_drawdown: float | None = None
    final_equity: float | None = None
    trades: list[TradeRecord] = field(default_factory=list)
    daily_equity: list[DailyEquityPoint] = field(default_factory=list)
    execution_model: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class PortfolioBacktestResult:
    initial_equity: float
    final_equity: float
    total_return: float
    annualized_return: float | None
    annualized_volatility: float | None
    sharpe_ratio: float | None
    max_drawdown: float
    average_utilization: float
    maximum_utilization: float
    maximum_open_positions: int
    daily_equity: list[DailyEquityPoint]


@dataclass
class FollowupBacktestResult:
    requested_days: int
    calendar: tuple[pd.Timestamp, ...]
    strategies: list[StrategyBacktestResult]
    portfolio: PortfolioBacktestResult | None
    warnings: list[str] = field(default_factory=list)
    requested_start: pd.Timestamp | None = None

    @property
    def all_failed(self) -> bool:
        return bool(self.strategies) and all(item.error is not None for item in self.strategies)

    @property
    def partial_failure(self) -> bool:
        failures = sum(item.error is not None for item in self.strategies)
        return 0 < failures < len(self.strategies)


@dataclass
class _StrategyInput:
    experiment_name: str
    label: str
    ticker: str
    has_trailing_stop: bool
    strategy: Any | None = None
    config: Any | None = None
    detector: Any | None = None
    backtester: Any | None = None
    frame: pd.DataFrame | None = None
    error: str | None = None


def compute_equity_metrics(equity: pd.Series) -> dict[str, float | None]:
    """Calculate path-dependent return and risk metrics from daily equity."""
    values = equity.astype(float)
    if values.empty:
        return {
            "initial_equity": None,
            "final_equity": None,
            "total_return": None,
            "annualized_return": None,
            "annualized_volatility": None,
            "sharpe_ratio": None,
            "max_drawdown": None,
        }

    initial = float(values.iloc[0])
    final = float(values.iloc[-1])
    total_return = (final - initial) / initial if initial > 0 else None
    observations = len(values) - 1
    annualized_return = (
        (final / initial) ** (252 / observations) - 1
        if observations > 0 and initial > 0 and final > 0
        else None
    )
    daily_returns = values.pct_change().dropna()
    daily_std = float(daily_returns.std(ddof=1)) if len(daily_returns) > 1 else 0.0
    annualized_volatility = daily_std * math.sqrt(252) if daily_std > 0 else None
    sharpe = float(daily_returns.mean()) / daily_std * math.sqrt(252) if daily_std > 0 else None
    drawdown = values / values.cummax() - 1
    return {
        "initial_equity": initial,
        "final_equity": final,
        "total_return": total_return,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "sharpe_ratio": sharpe,
        "max_drawdown": float(drawdown.min()),
    }


def _candidate_record(candidate: dict[str, Any], status: str) -> TradeRecord:
    return TradeRecord(
        status=status,
        signal_date=candidate["date"],
        entry_date=candidate.get("entry_date"),
        exit_date=candidate.get("exit_date"),
        entry_price=float(candidate["entry"]) if candidate.get("entry") is not None else None,
        exit_price=float(candidate["exit"]) if candidate.get("exit") is not None else None,
        mark_price=(
            float(candidate["mark_price"]) if candidate.get("mark_price") is not None else None
        ),
        return_pct=(
            float(candidate["return_pct"]) / 100
            if candidate.get("return_pct") is not None
            else (
                float(candidate["unrealized_return_pct"]) / 100
                if candidate.get("unrealized_return_pct") is not None
                else None
            )
        ),
        exit_type=candidate.get("exit_type"),
    )


def simulate_strategy_sleeve(
    calendar: tuple[pd.Timestamp, ...],
    frame: pd.DataFrame,
    raw_result: dict[str, Any],
    initial_cash: float,
) -> tuple[list[TradeRecord], list[DailyEquityPoint]]:
    """Apply one-cash-sleeve allocation to independently simulated trade candidates."""
    candidates: list[dict[str, Any]] = []
    for trade in raw_result.get("trades", []):
        candidates.append({**trade, "candidate_status": "completed"})
    for trade in raw_result.get("open_positions", []):
        candidates.append({**trade, "candidate_status": "open"})
    candidates.sort(key=lambda item: (item["entry_date"], item["date"]))

    records = [
        TradeRecord(
            status="unfilled",
            signal_date=item["date"],
            reason=item.get("reason", "no_next_day_data"),
        )
        for item in raw_result.get("unfilled_signals", [])
    ]
    entries_by_date: dict[pd.Timestamp, list[dict[str, Any]]] = {}
    for candidate in candidates:
        entries_by_date.setdefault(pd.Timestamp(candidate["entry_date"]), []).append(candidate)

    close_by_date = frame["Close"].reindex(pd.DatetimeIndex(calendar)).ffill()
    cash = float(initial_cash)
    active: tuple[dict[str, Any], TradeRecord] | None = None
    points: list[DailyEquityPoint] = []
    running_peak = initial_cash
    previous_equity: float | None = None

    for date in calendar:
        date = pd.Timestamp(date)
        if active is not None:
            candidate, record = active
            if (
                candidate.get("exit_type") == "time_expiry"
                and pd.Timestamp(candidate["exit_date"]) == date
            ):
                cash = record.quantity * float(candidate["exit"])
                active = None

        for candidate in entries_by_date.get(date, []):
            if active is not None or cash <= 0:
                skipped = _candidate_record(candidate, "skipped_insufficient_cash")
                skipped.reason = "insufficient_cash"
                records.append(skipped)
                continue
            record = _candidate_record(candidate, candidate["candidate_status"])
            record.quantity = cash / float(candidate["entry"])
            cash = 0.0
            records.append(record)
            active = (candidate, record)

        if active is not None:
            candidate, record = active
            exit_date = candidate.get("exit_date")
            if (
                candidate.get("exit_type") != "time_expiry"
                and exit_date is not None
                and pd.Timestamp(exit_date) == date
            ):
                cash = record.quantity * float(candidate["exit"])
                active = None

        if active is None:
            position_value = 0.0
        else:
            candidate, record = active
            mark = close_by_date.loc[date]
            if pd.isna(mark):
                mark = candidate["entry"]
            position_value = record.quantity * float(mark)
            if record.status == "open":
                record.mark_price = float(mark)
                record.return_pct = float(mark) / float(candidate["entry"]) - 1

        equity = cash + position_value
        running_peak = max(running_peak, equity)
        daily_return = equity / previous_equity - 1 if previous_equity else None
        drawdown = equity / running_peak - 1 if running_peak else 0.0
        utilization = position_value / equity if equity else 0.0
        points.append(
            DailyEquityPoint(
                date=date,
                equity=equity,
                cash=cash,
                position_value=position_value,
                daily_return=daily_return,
                drawdown=drawdown,
                utilization=utilization,
                open_positions=int(active is not None),
            )
        )
        previous_equity = equity

    records.sort(key=lambda item: item.signal_date)
    return records, points


def build_portfolio_result(
    calendar: tuple[pd.Timestamp, ...],
    strategies: list[StrategyBacktestResult],
    sleeve_cash: float,
) -> PortfolioBacktestResult:
    """Sum successful sleeve paths and retain failed sleeves as cash."""
    failed_sleeves = sum(item.error is not None for item in strategies)
    maps = {
        index: {point.date: point for point in item.daily_equity}
        for index, item in enumerate(strategies)
        if item.error is None
    }
    points: list[DailyEquityPoint] = []
    running_peak = sleeve_cash * len(strategies)
    previous_equity: float | None = None
    for date in calendar:
        cash = failed_sleeves * sleeve_cash
        position_value = 0.0
        open_positions = 0
        for index, item in enumerate(strategies):
            if item.error is not None:
                continue
            sleeve_point = maps[index][pd.Timestamp(date)]
            cash += sleeve_point.cash
            position_value += sleeve_point.position_value
            open_positions += sleeve_point.open_positions
        equity = cash + position_value
        running_peak = max(running_peak, equity)
        points.append(
            DailyEquityPoint(
                date=pd.Timestamp(date),
                equity=equity,
                cash=cash,
                position_value=position_value,
                daily_return=equity / previous_equity - 1 if previous_equity else None,
                drawdown=equity / running_peak - 1 if running_peak else 0.0,
                utilization=position_value / equity if equity else 0.0,
                open_positions=open_positions,
            )
        )
        previous_equity = equity

    metrics = compute_equity_metrics(pd.Series([point.equity for point in points]))
    return PortfolioBacktestResult(
        initial_equity=float(metrics["initial_equity"]),
        final_equity=float(metrics["final_equity"]),
        total_return=float(metrics["total_return"]),
        annualized_return=metrics["annualized_return"],
        annualized_volatility=metrics["annualized_volatility"],
        sharpe_ratio=metrics["sharpe_ratio"],
        max_drawdown=float(metrics["max_drawdown"]),
        average_utilization=float(np.mean([point.utilization for point in points])),
        maximum_utilization=max(point.utilization for point in points),
        maximum_open_positions=max(point.open_positions for point in points),
        daily_equity=points,
    )


def _make_strategy_result(
    item: _StrategyInput, days: int, sleeve_cash: float
) -> StrategyBacktestResult:
    return StrategyBacktestResult(
        experiment_name=item.experiment_name,
        label=item.label,
        ticker=item.ticker,
        requested_days=days,
        sleeve_initial_cash=sleeve_cash,
        error=item.error,
    )


def _normalize_start(
    start: date_type | datetime | pd.Timestamp | str | None,
) -> pd.Timestamp | None:
    """Normalize a supported start value to a timezone-naive calendar date."""
    if start is None:
        return None
    if isinstance(start, str):
        try:
            parsed = date_type.fromisoformat(start)
        except ValueError as exc:
            raise ValueError("start must be a date in YYYY-MM-DD format") from exc
        if parsed.isoformat() != start:
            raise ValueError("start must be a date in YYYY-MM-DD format")
        timestamp = pd.Timestamp(parsed)
    elif isinstance(start, (date_type, datetime, pd.Timestamp)):
        timestamp = pd.Timestamp(start)
    else:
        raise ValueError("start must be a date in YYYY-MM-DD format")
    if pd.isna(timestamp):
        raise ValueError("start must be a date in YYYY-MM-DD format")
    if timestamp.tzinfo is not None:
        timestamp = timestamp.tz_localize(None)
    return timestamp.normalize()


def run_followup_backtest(
    days: int = DEFAULT_DAYS,
    *,
    start: date_type | datetime | pd.Timestamp | str | None = None,
    strategy_definitions: Sequence[dict[str, str | bool]] | None = None,
    get_experiment_fn: Callable[[str], Any] | None = None,
    fetcher_factory: Callable[..., DataFetcher] = DataFetcher,
    now_et: datetime | None = None,
) -> FollowupBacktestResult:
    """Evaluate current followup strategies and return structured sleeve/portfolio results."""
    if days <= 0:
        raise ValueError("days must be a positive integer")
    requested_start = _normalize_start(start)
    if strategy_definitions is None:
        from trading import followup

        definitions = list(followup.STRATEGIES)
    else:
        definitions = list(strategy_definitions)
    if not definitions:
        return FollowupBacktestResult(
            requested_days=days,
            calendar=(),
            strategies=[],
            portfolio=None,
            warnings=["No followup strategies configured"],
            requested_start=requested_start,
        )

    loader = get_experiment_fn or get_experiment
    inputs: list[_StrategyInput] = []
    for definition in definitions:
        item = _StrategyInput(
            experiment_name=str(definition["experiment_name"]),
            label=str(definition["label"]),
            ticker=str(definition["ticker"]),
            has_trailing_stop=bool(definition["has_trailing_stop"]),
        )
        try:
            item.strategy = loader(item.experiment_name)
            item.config = item.strategy.create_config()
            item.detector = item.strategy.create_detector()
            item.backtester = item.strategy.create_backtester(item.config)
        except Exception as exc:
            item.error = f"{item.experiment_name}: strategy load failed: {exc}"
        inputs.append(item)

    loaded = [item for item in inputs if item.error is None]
    data: dict[str, pd.DataFrame] = {}
    if loaded:
        tickers = list(dict.fromkeys(item.ticker for item in loaded))
        for ticker in tickers:
            ticker_start = min(
                str(item.config.data_start) for item in loaded if item.ticker == ticker
            )
            fetched = fetcher_factory(start=ticker_start).fetch_all([ticker])
            if ticker in fetched:
                data[ticker] = fetched[ticker]

    for item in loaded:
        if item.ticker not in data:
            item.error = f"Failed to fetch {item.ticker} data"
            continue
        frame = data[item.ticker].loc[str(item.config.data_start) :].copy()
        item.frame = _drop_incomplete_bar(frame, now_et=now_et)
        if item.frame.empty:
            item.error = f"Failed to fetch {item.ticker} data"

    reference = next(
        (item for item in inputs if item.error is None and item.frame is not None), None
    )
    sleeve_cash = INITIAL_CAPITAL / len(inputs)
    if reference is None:
        results = [_make_strategy_result(item, days, sleeve_cash) for item in inputs]
        return FollowupBacktestResult(
            requested_days=days,
            calendar=(),
            strategies=results,
            portfolio=None,
            requested_start=requested_start,
        )

    available_dates = reference.frame.index
    warnings: list[str] = []
    earliest_available = _normalize_start(pd.Timestamp(available_dates[0]))
    latest_available = _normalize_start(pd.Timestamp(available_dates[-1]))
    if requested_start is None:
        selected_dates = available_dates[-days:]
    else:
        if requested_start < earliest_available:
            warnings.append(
                f"Requested start {requested_start:%Y-%m-%d} precedes earliest available "
                f"completed session {earliest_available:%Y-%m-%d}; using "
                f"{earliest_available:%Y-%m-%d}"
            )
        eligible_dates = [
            value
            for value in available_dates
            if _normalize_start(pd.Timestamp(value)) >= requested_start
        ]
        selected_dates = eligible_dates[:days]
    calendar = tuple(pd.Timestamp(value) for value in selected_dates)
    if not calendar:
        results = [_make_strategy_result(item, days, sleeve_cash) for item in inputs]
        warnings.append(
            f"Requested start {requested_start:%Y-%m-%d} is after the last available "
            f"completed session {latest_available:%Y-%m-%d}"
        )
        return FollowupBacktestResult(
            requested_days=days,
            calendar=(),
            strategies=results,
            portfolio=None,
            warnings=warnings,
            requested_start=requested_start,
        )
    if len(calendar) < days:
        if requested_start is None:
            warnings.append(
                f"Requested {days} completed sessions; available {len(calendar)} "
                f"from {calendar[0]:%Y-%m-%d} to {calendar[-1]:%Y-%m-%d}"
            )
        else:
            warnings.append(
                f"Requested {days} completed sessions from "
                f"{requested_start:%Y-%m-%d}; available {len(calendar)} "
                f"from {calendar[0]:%Y-%m-%d} to {calendar[-1]:%Y-%m-%d}"
            )

    results: list[StrategyBacktestResult] = []
    calendar_index = pd.DatetimeIndex(calendar)
    for item in inputs:
        result = _make_strategy_result(item, days, sleeve_cash)
        if item.error is not None or item.frame is None:
            results.append(result)
            continue
        try:
            indicated = item.detector.compute_indicators(item.frame.copy())
            signaled = item.detector.detect_signals(indicated)
            if "Signal" not in signaled:
                raise ValueError("detector did not return Signal column")
            signaled = signaled.copy()
            signaled["Signal"] = signaled["Signal"].fillna(False).astype(bool)
            evaluation_index = signaled.index.intersection(calendar_index)
            evaluation = signaled.loc[evaluation_index].copy()
            result.period_start = calendar[0]
            result.period_end = calendar[-1]
            result.evaluation_rows = len(evaluation)
            result.warmup_rows = max(0, len(signaled.loc[: calendar[0]]) - 1)
            result.missing_sessions = len(calendar) - len(evaluation)
            if result.missing_sessions:
                result.warnings.append(
                    f"{item.ticker}: missing {result.missing_sessions} canonical sessions"
                )
            result.signal_count = int(evaluation["Signal"].sum())
            raw = item.backtester.run(evaluation, preserve_open_positions=True)
            trades, points = simulate_strategy_sleeve(calendar, evaluation, raw, sleeve_cash)
            completed = [trade for trade in trades if trade.status == "completed"]
            completed_returns = [
                trade.return_pct for trade in completed if trade.return_pct is not None
            ]
            equity = pd.Series([point.equity for point in points])
            metrics = compute_equity_metrics(equity)
            result.completed_count = len(completed)
            result.open_count = sum(trade.status == "open" for trade in trades)
            result.unfilled_count = sum(trade.status == "unfilled" for trade in trades)
            result.skipped_count = sum(
                trade.status == "skipped_insufficient_cash" for trade in trades
            )
            result.win_rate = (
                sum(value > 0 for value in completed_returns) / len(completed_returns)
                if completed_returns
                else None
            )
            result.avg_trade_return = (
                float(np.mean(completed_returns)) if completed_returns else None
            )
            result.cumulative_return = metrics["total_return"]
            result.sharpe_ratio = metrics["sharpe_ratio"]
            result.max_drawdown = metrics["max_drawdown"]
            result.final_equity = metrics["final_equity"]
            result.trades = trades
            result.daily_equity = points
            result.execution_model = raw.get("execution_model", {})
        except Exception as exc:
            result.error = f"{item.experiment_name}: evaluation failed: {exc}"
        results.append(result)

    portfolio = build_portfolio_result(calendar, results, sleeve_cash)
    return FollowupBacktestResult(
        requested_days=days,
        calendar=calendar,
        strategies=results,
        portfolio=portfolio,
        warnings=warnings,
        requested_start=requested_start,
    )


def _format_percent(value: float | None, *, signed: bool = False) -> str:
    if value is None:
        return "N/A"
    return f"{value:+.2%}" if signed else f"{value:.2%}"


def _format_ratio(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.2f}"


def _format_date(value: pd.Timestamp | None) -> str:
    return "N/A" if value is None else value.strftime("%Y-%m-%d")


def render_followup_backtest(
    result: FollowupBacktestResult, *, output: TextIO | None = None
) -> None:
    """Render a structured followup backtest without performing calculations."""
    output = output or sys.stdout
    print("\nFOLLOWUP BACKTEST REPORT", file=output)
    print(f"Requested completed sessions: {result.requested_days}", file=output)
    if result.requested_start is not None:
        print(f"Requested start: {result.requested_start:%Y-%m-%d}", file=output)
    if result.calendar:
        print(
            f"Actual period: {result.calendar[0]:%Y-%m-%d} ~ "
            f"{result.calendar[-1]:%Y-%m-%d} ({len(result.calendar)} sessions)",
            file=output,
        )
    for warning in result.warnings:
        print(f"[WARNING] {warning}", file=output)

    if result.portfolio is not None:
        portfolio = result.portfolio
        print("\nPortfolio Summary", file=output)
        print(f"Initial equity: ${portfolio.initial_equity:,.2f}", file=output)
        print(f"Final asset value: ${portfolio.final_equity:,.2f}", file=output)
        print(
            f"Portfolio total return: {_format_percent(portfolio.total_return, signed=True)}",
            file=output,
        )
        print(
            f"Annualized return: {_format_percent(portfolio.annualized_return, signed=True)}",
            file=output,
        )
        print(
            f"Annualized volatility: {_format_percent(portfolio.annualized_volatility)}",
            file=output,
        )
        print(f"Sharpe ratio: {_format_ratio(portfolio.sharpe_ratio)}", file=output)
        print(f"Maximum drawdown: {_format_percent(portfolio.max_drawdown)}", file=output)
        print(
            f"Capital utilization (average / max): "
            f"{_format_percent(portfolio.average_utilization)} / "
            f"{_format_percent(portfolio.maximum_utilization)}",
            file=output,
        )
        print(
            f"Maximum simultaneous positions: {portfolio.maximum_open_positions}",
            file=output,
        )

    for strategy in result.strategies:
        print(
            f"\n{strategy.label} — {strategy.ticker} ({strategy.experiment_name})",
            file=output,
        )
        if strategy.error is not None:
            print(f"[ERROR] {strategy.error}", file=output)
            continue
        print(
            f"Period: {_format_date(strategy.period_start)} ~ "
            f"{_format_date(strategy.period_end)} "
            f"({strategy.evaluation_rows} available sessions)",
            file=output,
        )
        print(
            f"Signals: {strategy.signal_count}; completed: {strategy.completed_count}; "
            f"open: {strategy.open_count}; unfilled: {strategy.unfilled_count}; "
            f"skipped (cash): {strategy.skipped_count}",
            file=output,
        )
        print(
            f"Win rate: {_format_percent(strategy.win_rate)}; "
            f"cumulative return: {_format_percent(strategy.cumulative_return, signed=True)}; "
            f"average completed trade: "
            f"{_format_percent(strategy.avg_trade_return, signed=True)}",
            file=output,
        )
        print(
            f"Sharpe: {_format_ratio(strategy.sharpe_ratio)}; "
            f"maximum drawdown: {_format_percent(strategy.max_drawdown)}",
            file=output,
        )
        for warning in strategy.warnings:
            print(f"[WARNING] {warning}", file=output)
        for trade in strategy.trades:
            print(
                f"  {trade.status}: signal={trade.signal_date} "
                f"entry={trade.entry_date or 'N/A'} exit={trade.exit_date or 'N/A'} "
                f"entry_px={trade.entry_price if trade.entry_price is not None else 'N/A'} "
                f"exit_px={trade.exit_price if trade.exit_price is not None else 'N/A'} "
                f"mark_px={trade.mark_price if trade.mark_price is not None else 'N/A'} "
                f"qty={trade.quantity:.6f} return={_format_percent(trade.return_pct, signed=True)} "
                f"type={trade.exit_type or 'N/A'} reason={trade.reason or 'N/A'}",
                file=output,
            )

    print(
        "\nOpen positions are marked to the last completed adjusted close and excluded "
        "from completed-trade win rate and average trade return.",
        file=output,
    )
