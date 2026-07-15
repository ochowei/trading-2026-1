# Followup Backtest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:test-driven-development` for every
> task and `superpowers:verification-before-completion` before reporting success. Execute inline with
> `superpowers:executing-plans` unless the user explicitly authorizes subagent delegation. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `uv run trading followup-backtest [--days N]`, driven directly by the current
`followup.STRATEGIES`, with exact completed-session boundaries, preserved indicator/cooldown history,
open-position mark-to-market, and a USD 100,000 equal-weight strategy-sleeve portfolio ledger.

**Architecture:** Keep `followup.py` as the sole strategy-selection source and preserve its existing
60-session report. Add `followup_backtest.py` for structured orchestration, sleeve accounting,
portfolio metrics, and rendering. Extend the two execution-model backtesters with an opt-in
`preserve_open_positions` mode whose default is backward compatible.

**Tech Stack:** Python 3.11, argparse, dataclasses, pandas, NumPy, pytest, Ruff, uv.

## Global Constraints

- Work only on the current `dev-A` branch.
- Preserve all existing user changes; inspect `git status` before each task.
- Do not modify any file under `pm/`.
- Do not commit, push, or create a PR.
- Write each failing test before its implementation.
- Tests must use deterministic fixtures and must not download live data.
- `uv run trading followup` must retain its 60-session default and Firstrade output behavior.
- `src/trading/followup.py::STRATEGIES` remains the only selected-strategy list.
- `--days` defaults to 126 and accepts positive integers only.
- Strategy and portfolio calculations must return structured values independently of stdout.
- Update README and CLAUDE.md with every user-visible code or architecture change.

---

## Target File Structure

- Create `src/trading/followup_backtest.py`: result dataclasses, data preparation, strategy/sleeve
  evaluation, portfolio aggregation, and CLI text renderer.
- Modify `src/trading/followup.py`: allow deterministic clock injection in the existing incomplete-bar
  helper without changing default callers.
- Modify `src/trading/core/execution_backtester.py`: opt-in open-position preservation.
- Modify `src/trading/experiments/gld_003_trailing_stop/trailing_backtester.py`: matching trailing-stop
  open-position preservation.
- Modify `src/trading/cli.py`: reusable parser, positive integer type, command registration/dispatch.
- Modify `pyproject.toml` and `uv.lock`: add pytest as a dev dependency.
- Create `tests/conftest.py`: deterministic OHLCV fixture builders and fake strategy components.
- Create `tests/test_followup_backtest_cli.py`: CLI parsing, dispatch, and followup regression tests.
- Create `tests/test_followup_backtest_data.py`: completed bars, exact N sessions, warmup, cooldown,
  strategy discovery, and failure behavior.
- Create `tests/test_execution_open_positions.py`: standard and trailing execution end-boundary tests.
- Create `tests/test_followup_backtest_ledger.py`: sleeve and portfolio accounting tests.
- Modify `README.md`: command usage, metrics, and assumptions.
- Modify `CLAUDE.md`: development commands and architecture overview.

---

### Task 1: Establish deterministic pytest and CLI parsing seams

**Files:**

- Modify: `pyproject.toml:25-28`
- Modify: `uv.lock`
- Modify: `src/trading/cli.py:83-155`
- Create: `tests/test_followup_backtest_cli.py`

**Interfaces:**

- Produces: `positive_int(value: str) -> int`
- Produces: `build_parser() -> argparse.ArgumentParser`
- Changes: `main(argv: list[str] | None = None) -> None`
- CLI namespace: `command == "followup-backtest"`, `days: int`

- [ ] **Step 1: Add pytest to the dev dependency group**

Edit `pyproject.toml` to make the dev group exactly:

```toml
[dependency-groups]
dev = [
    "pytest>=8.3",
    "ruff>=0.9",
]
```

Run:

```bash
uv lock
```

Expected: `uv.lock` resolves pytest and its transitive dependencies without changing runtime
dependencies.

- [ ] **Step 2: Write failing parser tests**

Create `tests/test_followup_backtest_cli.py` with these initial tests:

```python
import pytest

from trading.cli import build_parser


def test_followup_backtest_defaults_to_126_days() -> None:
    args = build_parser().parse_args(["followup-backtest"])
    assert args.command == "followup-backtest"
    assert args.days == 126


def test_followup_backtest_accepts_180_days() -> None:
    args = build_parser().parse_args(["followup-backtest", "--days", "180"])
    assert args.days == 180


@pytest.mark.parametrize("value", ["0", "-1", "1.5", "abc"])
def test_followup_backtest_rejects_non_positive_integer(value: str) -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(["followup-backtest", "--days", value])
    assert exc_info.value.code == 2


def test_followup_backtest_rejects_missing_days_value() -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(["followup-backtest", "--days"])
    assert exc_info.value.code == 2


def test_followup_parser_keeps_existing_followup_command() -> None:
    args = build_parser().parse_args(["followup"])
    assert args.command == "followup"
    assert not hasattr(args, "days")
```

- [ ] **Step 3: Run the parser tests and confirm RED**

Run:

```bash
uv run pytest tests/test_followup_backtest_cli.py -q
```

Expected: collection fails because `build_parser` does not exist.

- [ ] **Step 4: Extract the parser and add strict positive-integer validation**

Refactor `src/trading/cli.py` so parser construction is separate from dispatch:

```python
def positive_int(value: str) -> int:
    """Parse a strictly positive integer for argparse."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="量化交易實驗框架 (Quantitative Trading Experiment Framework)",
        prog="trading",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="列出所有實驗 (List all experiments)")

    run_p = sub.add_parser("run", help="執行實驗 (Run experiment(s))")
    run_p.add_argument("experiment", nargs="?", help="實驗名稱 (Experiment name)")
    run_p.add_argument("--all", action="store_true", help="執行全部實驗 (Run all experiments)")

    sub.add_parser("followup", help="產生跟單訊號報告 (Generate Firstrade trading signals)")

    followup_backtest_p = sub.add_parser(
        "followup-backtest",
        help="回測目前跟單策略組合 (Backtest current followup portfolio)",
    )
    followup_backtest_p.add_argument(
        "--days",
        type=positive_int,
        default=126,
        help="完整交易日數 (Completed trading sessions, default: 126)",
    )

    cmp_p = sub.add_parser("compare", help="比較實驗結果 (Compare experiment results)")
    cmp_p.add_argument(
        "experiments", nargs="+", help="要比較的實驗名稱 (Experiment names to compare)"
    )

    analyze_p = sub.add_parser(
        "analyze", help="滾動窗口績效分析 (Rolling window performance analysis)"
    )
    analyze_p.add_argument("experiment", help="實驗名稱 (Experiment name)")
    analyze_p.add_argument(
        "--window-years",
        type=int,
        default=2,
        help="窗口大小（年）(Window size in years, default: 2)",
    )
    analyze_p.add_argument(
        "--step-months",
        type=int,
        default=6,
        help="步進（月）(Step size in months, default: 6)",
    )

    sub.add_parser(
        "sync-docs",
        help="檢查 Markdown 文件與 latest.json 是否同步 (Check docs against latest.json)",
    )
    sub.add_parser("freshness", help="檢查知識新鮮度 (Check knowledge freshness)")
    return parser


def main(argv: list[str] | None = None) -> None:
    """CLI main entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "list":
        cmd_list(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "followup":
        from trading.followup import run_followup

        run_followup()
    elif args.command == "compare":
        cmd_compare(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "sync-docs":
        cmd_sync_docs(args)
    elif args.command == "freshness":
        from trading.core.freshness import check_freshness

        check_freshness()
    else:
        parser.print_help()
        raise SystemExit(0)
```

When moving the existing parser code into `build_parser`, include every existing subcommand and
argument unchanged; do not leave duplicate parser construction in `main`.

- [ ] **Step 5: Run parser tests and confirm GREEN**

Run:

```bash
uv run pytest tests/test_followup_backtest_cli.py -q
```

Expected: 7 tests pass.

- [ ] **Step 6: Verify parser style and preserve the working tree**

Run:

```bash
uv run ruff check src/trading/cli.py tests/test_followup_backtest_cli.py
uv run ruff format --check src/trading/cli.py tests/test_followup_backtest_cli.py
git status --short
```

Expected: Ruff passes; only Task 1 files plus the approved spec/plan are changed. Do not commit.

---

### Task 2: Preserve genuinely open execution-model positions

**Files:**

- Modify: `src/trading/core/execution_backtester.py:55-338`
- Modify: `src/trading/experiments/gld_003_trailing_stop/trailing_backtester.py:36-316`
- Create: `tests/test_execution_open_positions.py`

**Interfaces:**

- Changes: `ExecutionModelBacktester.run(df, *, preserve_open_positions=False) -> dict`
- Changes: `TrailingStopBacktester.run(df, *, preserve_open_positions=False) -> dict`
- Produces result keys: `open_positions: list[dict]`, `open_count: int`
- Preserves: existing `run(df)` results and fallback expiry behavior

- [ ] **Step 1: Write the standard execution open-position tests**

Create `tests/test_execution_open_positions.py`:

```python
from dataclasses import replace

import pandas as pd

from trading.core.base_config import ExperimentConfig
from trading.core.execution_backtester import ExecutionModelBacktester
from trading.experiments.gld_003_trailing_stop.trailing_backtester import TrailingStopBacktester


def execution_config() -> ExperimentConfig:
    return ExperimentConfig(
        name="fixture",
        tickers=["FIX"],
        profit_target=0.10,
        stop_loss=-0.10,
        holding_days=3,
    )


def unfinished_frame() -> pd.DataFrame:
    index = pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07"])
    return pd.DataFrame(
        {
            "Open": [100.0, 101.0, 102.0],
            "High": [101.0, 103.0, 104.0],
            "Low": [99.0, 100.0, 101.0],
            "Close": [100.0, 102.0, 103.0],
            "Volume": [1000, 1000, 1000],
            "Signal": [True, False, False],
        },
        index=index,
    )


def test_execution_backtester_preserves_open_position() -> None:
    result = ExecutionModelBacktester(execution_config(), slippage_pct=0.001).run(
        unfinished_frame(), preserve_open_positions=True
    )
    assert result["trades"] == []
    assert result["open_count"] == 1
    position = result["open_positions"][0]
    assert position["status"] == "open"
    assert position["entry_date"] == "2026-01-06"
    assert position["valuation_date"] == "2026-01-07"
    assert position["mark_price"] == 103.0
    assert position["holding_days"] == 1


def test_execution_backtester_default_remains_backward_compatible() -> None:
    result = ExecutionModelBacktester(execution_config(), slippage_pct=0.001).run(
        unfinished_frame()
    )
    assert "open_positions" not in result
    assert result["trades"][0]["exit_type"] == "time_expiry"


def test_final_day_signal_is_unfilled_not_open() -> None:
    df = unfinished_frame()
    df["Signal"] = [False, False, True]
    result = ExecutionModelBacktester(execution_config()).run(
        df, preserve_open_positions=True
    )
    assert result["open_count"] == 0
    assert result["unfilled_count"] == 1


def test_trailing_backtester_reports_current_trailing_state() -> None:
    config = replace(execution_config(), profit_target=0.20)
    result = TrailingStopBacktester(
        config,
        slippage_pct=0.001,
        trail_activation_pct=0.01,
        trail_distance_pct=0.05,
    ).run(unfinished_frame(), preserve_open_positions=True)
    position = result["open_positions"][0]
    assert position["trail_activated"] is True
    assert position["current_stop"] > position["initial_stop"]
```

- [ ] **Step 2: Run open-position tests and confirm RED**

Run:

```bash
uv run pytest tests/test_execution_open_positions.py -q
```

Expected: `TypeError` because `preserve_open_positions` is not accepted.

- [ ] **Step 3: Add opt-in open-position handling to the standard backtester**

Change the signature and initialize the opt-in collection:

```python
def run(self, df: pd.DataFrame, *, preserve_open_positions: bool = False) -> dict:
    signal_indices = df.index[df["Signal"]].tolist()
    if not signal_indices:
        result = self._empty_result()
        if preserve_open_positions:
            result.update({"open_positions": [], "open_count": 0})
        return result

    trades: list[dict] = []
    open_positions: list[dict] = []
    unfilled_signals: list[dict] = []
```

In the no-real-expiry-data branch, preserve instead of fabricating an exit:

```python
if after_hold.empty and preserve_open_positions:
    valuation_date = df.index[-1]
    mark_price = float(df.iloc[-1]["Close"])
    current_holding_days = max(0, len(df.loc[df.index > entry_date]))
    open_positions.append(
        {
            "status": "open",
            "date": signal_date.strftime("%Y-%m-%d"),
            "entry_date": entry_date.strftime("%Y-%m-%d"),
            "entry": round(float(entry_price), 6),
            "target_price": round(float(target_price), 6),
            "initial_stop": round(float(stop_price), 6),
            "current_stop": round(float(stop_price), 6),
            "holding_days": current_holding_days,
            "valuation_date": valuation_date.strftime("%Y-%m-%d"),
            "mark_price": round(mark_price, 6),
            "unrealized_return_pct": round((mark_price / entry_price - 1) * 100, 6),
        }
    )
    continue
```

Before every opt-in return, attach:

```python
if preserve_open_positions:
    result["open_positions"] = open_positions
    result["open_count"] = len(open_positions)
```

Do not add these keys when `preserve_open_positions` is false. Keep all existing aggregate metrics
based on completed `trades` only.

- [ ] **Step 4: Add matching trailing-stop preservation**

Apply the same signature, empty result, collection, and return-key pattern to
`TrailingStopBacktester`. Its open record must use the state already calculated by its holding loop:

```python
open_positions.append(
    {
        "status": "open",
        "date": signal_date.strftime("%Y-%m-%d"),
        "entry_date": entry_date.strftime("%Y-%m-%d"),
        "entry": round(float(entry_price), 6),
        "target_price": round(float(target_price), 6),
        "initial_stop": round(float(initial_stop_price), 6),
        "current_stop": round(float(current_stop), 6),
        "holding_days": max(0, len(df.loc[df.index > entry_date])),
        "valuation_date": df.index[-1].strftime("%Y-%m-%d"),
        "mark_price": round(float(df.iloc[-1]["Close"]), 6),
        "unrealized_return_pct": round(
            (float(df.iloc[-1]["Close"]) / entry_price - 1) * 100, 6
        ),
        "trail_activated": trail_activated,
        "highest_price": round(float(highest_price), 6),
        "trail_activation_pct": self.trail_activation_pct,
        "trail_distance_pct": self.trail_distance_pct,
    }
)
```

- [ ] **Step 5: Run the focused execution tests and regress existing defaults**

Run:

```bash
uv run pytest tests/test_execution_open_positions.py -q
uv run trading run ewt_001_pullback_wr_reversal --help
```

Expected: tests pass; existing CLI parsing still accepts the experiment name. No live strategy run is
required in this task.

- [ ] **Step 6: Run Ruff for changed execution files**

Run:

```bash
uv run ruff check src/trading/core/execution_backtester.py src/trading/experiments/gld_003_trailing_stop/trailing_backtester.py tests/test_execution_open_positions.py
uv run ruff format --check src/trading/core/execution_backtester.py src/trading/experiments/gld_003_trailing_stop/trailing_backtester.py tests/test_execution_open_positions.py
```

Expected: both commands pass. Do not commit.

---

### Task 3: Build completed-session preparation with full-history signals

**Files:**

- Modify: `src/trading/followup.py:191-213`
- Create: `src/trading/followup_backtest.py`
- Create: `tests/conftest.py`
- Create: `tests/test_followup_backtest_data.py`

**Interfaces:**

- Changes: `_drop_incomplete_bar(df, *, now_et=None) -> pd.DataFrame`
- Produces: `StrategyInput`, `StrategyBacktestResult`, `FollowupBacktestResult` dataclasses
- Produces: `run_followup_backtest(days=126, *, strategy_definitions=None, get_experiment_fn=None,
  fetcher_factory=DataFetcher, now_et=None) -> FollowupBacktestResult`
- Reads: `followup.STRATEGIES` at call time when `strategy_definitions is None`

- [ ] **Step 1: Add reusable deterministic fixtures**

Create `tests/conftest.py`:

```python
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd
import pytest

from trading.core.base_config import ExperimentConfig


@pytest.fixture
def make_ohlcv() -> Callable[[int, str], pd.DataFrame]:
    def factory(rows: int, start: str = "2025-01-02") -> pd.DataFrame:
        index = pd.bdate_range(start, periods=rows)
        close = pd.Series(range(100, 100 + rows), index=index, dtype=float)
        return pd.DataFrame(
            {
                "Open": close - 0.25,
                "High": close + 1.0,
                "Low": close - 1.0,
                "Close": close,
                "Volume": 1000,
            },
            index=index,
        )

    return factory


@dataclass
class FakeDetector:
    cooldown_days: int = 0

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        result["SMA_3"] = result["Close"].rolling(3).mean()
        return result

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        raw = result.get("RawSignal", pd.Series(False, index=result.index)).fillna(False)
        accepted = pd.Series(False, index=result.index)
        last_position: int | None = None
        for position, is_signal in enumerate(raw.astype(bool)):
            if not is_signal:
                continue
            if last_position is None or position - last_position > self.cooldown_days:
                accepted.iloc[position] = True
                last_position = position
        result["Signal"] = accepted
        return result


class FakeBacktester:
    def run(self, df: pd.DataFrame, *, preserve_open_positions: bool = False) -> dict:
        assert preserve_open_positions is True
        return {
            "trades": [],
            "open_positions": [],
            "open_count": 0,
            "unfilled_signals": [],
            "unfilled_count": 0,
            "execution_model": {"entry_mode": "fixture"},
        }


class FakeStrategy:
    def __init__(self, ticker: str, detector: FakeDetector | None = None):
        self.ticker = ticker
        self.detector = detector or FakeDetector()

    def create_config(self) -> ExperimentConfig:
        return ExperimentConfig(name="fixture", tickers=[self.ticker], data_start="2020-01-01")

    def create_detector(self) -> FakeDetector:
        return self.detector

    def create_backtester(self, config: ExperimentConfig) -> FakeBacktester:
        return FakeBacktester()
```

- [ ] **Step 2: Write failing data-boundary and dynamic-strategy tests**

Create `tests/test_followup_backtest_data.py` with tests that use the fixtures above:

```python
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from conftest import FakeDetector, FakeStrategy
from trading.followup import _drop_incomplete_bar
from trading.followup_backtest import run_followup_backtest


NY = ZoneInfo("America/New_York")


class FakeFetcher:
    frames: dict[str, pd.DataFrame] = {}

    def __init__(self, start: str):
        self.start = start

    def fetch_all(self, tickers: list[str]) -> dict[str, pd.DataFrame]:
        return {ticker: self.frames[ticker].copy() for ticker in tickers if ticker in self.frames}


def definition(name: str, ticker: str) -> dict[str, str | bool]:
    return {
        "experiment_name": name,
        "label": name.upper(),
        "ticker": ticker,
        "has_trailing_stop": False,
    }


def test_drop_incomplete_bar_uses_injected_new_york_clock(make_ohlcv) -> None:
    frame = make_ohlcv(2)
    frame.index = pd.to_datetime(["2026-07-14", "2026-07-15"])
    before_close = datetime(2026, 7, 15, 16, 0, tzinfo=NY)
    after_buffer = datetime(2026, 7, 15, 16, 30, tzinfo=NY)
    assert len(_drop_incomplete_bar(frame, now_et=before_close)) == 1
    assert len(_drop_incomplete_bar(frame, now_et=after_buffer)) == 2


def test_evaluation_uses_exactly_last_n_completed_sessions(make_ohlcv) -> None:
    FakeFetcher.frames = {"AAA": make_ohlcv(10)}
    result = run_followup_backtest(
        days=5,
        strategy_definitions=[definition("alpha", "AAA")],
        get_experiment_fn=lambda name: FakeStrategy("AAA"),
        fetcher_factory=FakeFetcher,
        now_et=datetime(2026, 7, 15, 17, 0, tzinfo=NY),
    )
    assert len(result.calendar) == 5
    assert result.calendar == tuple(FakeFetcher.frames["AAA"].index[-5:])


def test_indicators_and_cooldown_are_computed_before_slice(make_ohlcv) -> None:
    frame = make_ohlcv(8)
    frame["RawSignal"] = [False, False, False, True, False, True, False, False]
    FakeFetcher.frames = {"AAA": frame}
    strategy = FakeStrategy("AAA", FakeDetector(cooldown_days=3))
    result = run_followup_backtest(
        days=4,
        strategy_definitions=[definition("alpha", "AAA")],
        get_experiment_fn=lambda name: strategy,
        fetcher_factory=FakeFetcher,
    )
    strategy_result = result.strategies[0]
    assert strategy_result.signal_count == 0
    assert strategy_result.evaluation_rows == 4
    assert strategy_result.warmup_rows == 4


def test_strategy_definitions_are_read_at_call_time(monkeypatch, make_ohlcv) -> None:
    FakeFetcher.frames = {"NEW": make_ohlcv(4)}
    monkeypatch.setattr(
        "trading.followup.STRATEGIES", [definition("newest", "NEW")]
    )
    result = run_followup_backtest(
        days=3,
        get_experiment_fn=lambda name: FakeStrategy("NEW"),
        fetcher_factory=FakeFetcher,
    )
    assert [item.experiment_name for item in result.strategies] == ["newest"]


def test_one_ticker_failure_is_reported_and_other_strategy_continues(make_ohlcv) -> None:
    FakeFetcher.frames = {"GOOD": make_ohlcv(5)}
    definitions = [definition("bad", "BAD"), definition("good", "GOOD")]
    result = run_followup_backtest(
        days=3,
        strategy_definitions=definitions,
        get_experiment_fn=lambda name: FakeStrategy("BAD" if name == "bad" else "GOOD"),
        fetcher_factory=FakeFetcher,
    )
    assert result.strategies[0].error == "Failed to fetch BAD data"
    assert result.strategies[1].error is None
    assert result.partial_failure is True
```

- [ ] **Step 3: Run data tests and confirm RED**

Run:

```bash
uv run pytest tests/test_followup_backtest_data.py -q
```

Expected: import failure because `trading.followup_backtest` does not exist and the clock argument is
not accepted.

- [ ] **Step 4: Make the existing completed-bar helper injectable**

Change only the signature and clock assignment in `followup.py`:

```python
def _drop_incomplete_bar(
    df: pd.DataFrame, *, now_et: datetime | None = None
) -> pd.DataFrame:
    """Drop today's bar before the New York 16:30 completion buffer."""
    if df.empty:
        return df

    now_et = now_et or datetime.now(_NY_TZ)
```

Leave `_run_single_strategy` calling `_drop_incomplete_bar(df)` with no argument, preserving current
behavior.

- [ ] **Step 5: Create the structured data model and orchestration skeleton**

Start `src/trading/followup_backtest.py` with these concrete public types:

```python
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pandas as pd

from trading.core.data_fetcher import DataFetcher
from trading.experiments import get_experiment


DEFAULT_DAYS = 126
INITIAL_CAPITAL = 100_000.0


@dataclass
class StrategyInput:
    experiment_name: str
    label: str
    ticker: str
    has_trailing_stop: bool
    strategy: Any | None = None
    config: Any | None = None
    detector: Any | None = None
    backtester: Any | None = None
    primary_frame: pd.DataFrame | None = None
    error: str | None = None


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

    @property
    def all_failed(self) -> bool:
        return bool(self.strategies) and all(item.error is not None for item in self.strategies)

    @property
    def partial_failure(self) -> bool:
        failures = sum(item.error is not None for item in self.strategies)
        return 0 < failures < len(self.strategies)
```

Add private `StrategyInput` fields for definition, loaded strategy/config/detector/backtester, and
primary frame. Implement this exact signature:

```python
def run_followup_backtest(
    days: int = DEFAULT_DAYS,
    *,
    strategy_definitions: Sequence[dict[str, str | bool]] | None = None,
    get_experiment_fn: Callable[[str], Any] | None = None,
    fetcher_factory: Callable[..., DataFetcher] = DataFetcher,
    now_et: datetime | None = None,
) -> FollowupBacktestResult:
```

Its body performs these steps in order, with `experiment_loader = get_experiment_fn or
get_experiment` before loading definitions:

1. Convert `strategy_definitions` to a new list; when it is `None`, import `trading.followup` inside
   the function and copy `followup.STRATEGIES` at call time.
2. Reject an empty list by returning an empty result with warning `No followup strategies configured`.
3. Load every experiment and config, recording a per-strategy error if loading fails.
4. Create one `DataFetcher` from the earliest successfully loaded `config.data_start`; download all
   unique primary tickers once.
5. Slice each primary frame at its own `config.data_start`, call `_drop_incomplete_bar`, and choose the
   first successful definition's last `days` dates as the canonical calendar.
6. Compute indicators and signals on the full sliced history; validate boolean-convertible `Signal`.
7. Intersect with the canonical calendar only after full-history detection.
8. Call `backtester.run(evaluation_frame, preserve_open_positions=True)`.
9. Populate raw counts and execution metadata; Task 4 replaces the interim cash-only daily
   result with sleeve simulation.
10. Catch per-strategy fetch, indicator, signal, and backtester failures into `error` and continue.

For Task 3's temporary cash-only result, produce one `DailyEquityPoint` per canonical date with cash
and equity equal to the sleeve allocation. This is a complete intermediate implementation that Task
4 replaces with the approved sleeve event ledger.

- [ ] **Step 6: Run the data tests and confirm GREEN**

Run:

```bash
uv run pytest tests/test_followup_backtest_data.py -q
```

Expected: completed-bar, exact-window, warmup/cooldown, dynamic strategy, and partial failure tests
pass.

- [ ] **Step 7: Run focused Ruff checks**

Run:

```bash
uv run ruff check src/trading/followup.py src/trading/followup_backtest.py tests/conftest.py tests/test_followup_backtest_data.py
uv run ruff format --check src/trading/followup.py src/trading/followup_backtest.py tests/conftest.py tests/test_followup_backtest_data.py
```

Expected: both pass. Do not commit.

---

### Task 4: Implement the strategy-sleeve ledger and open-position MTM

**Files:**

- Modify: `src/trading/followup_backtest.py`
- Create: `tests/test_followup_backtest_ledger.py`

**Interfaces:**

- Produces: `compute_equity_metrics(equity: pd.Series) -> dict[str, float | None]`
- Produces: `simulate_strategy_sleeve(calendar, frame, raw_result, initial_cash) ->
  tuple[list[TradeRecord], list[DailyEquityPoint]]`
- Consumes: completed trades, open positions, and unfilled signals from each selected backtester
- Produces statuses: `completed`, `open`, `unfilled`, `skipped_insufficient_cash`

- [ ] **Step 1: Write failing known-ledger tests**

Create `tests/test_followup_backtest_ledger.py`:

```python
import math

import pandas as pd

from trading.followup_backtest import compute_equity_metrics, simulate_strategy_sleeve


def ledger_frame() -> pd.DataFrame:
    index = pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08"])
    return pd.DataFrame(
        {
            "Open": [10.0, 10.0, 11.0, 12.0],
            "High": [10.5, 11.0, 12.0, 13.0],
            "Low": [9.5, 9.5, 10.0, 11.0],
            "Close": [10.0, 11.0, 12.0, 12.0],
            "Volume": 1000,
        },
        index=index,
    )


def test_open_position_is_marked_to_market_but_not_counted_as_completed() -> None:
    frame = ledger_frame()
    raw = {
        "trades": [],
        "open_positions": [
            {
                "status": "open",
                "date": "2026-01-05",
                "entry_date": "2026-01-06",
                "entry": 10.0,
                "valuation_date": "2026-01-08",
                "mark_price": 12.0,
                "unrealized_return_pct": 20.0,
            }
        ],
        "unfilled_signals": [],
    }
    trades, points = simulate_strategy_sleeve(tuple(frame.index), frame, raw, 1000.0)
    assert trades[0].status == "open"
    assert trades[0].quantity == 100.0
    assert points[-1].equity == 1200.0
    assert points[-1].cash == 0.0


def test_overlapping_signal_is_skipped_without_borrowing() -> None:
    frame = ledger_frame()
    raw = {
        "trades": [
            {
                "date": "2026-01-05",
                "entry_date": "2026-01-06",
                "exit_date": "2026-01-08",
                "entry": 10.0,
                "exit": 12.0,
                "return_pct": 20.0,
                "exit_type": "target",
            },
            {
                "date": "2026-01-06",
                "entry_date": "2026-01-07",
                "exit_date": "2026-01-08",
                "entry": 11.0,
                "exit": 12.0,
                "return_pct": 9.090909,
                "exit_type": "target",
            },
        ],
        "open_positions": [],
        "unfilled_signals": [],
    }
    trades, points = simulate_strategy_sleeve(tuple(frame.index), frame, raw, 1000.0)
    assert [trade.status for trade in trades] == [
        "completed",
        "skipped_insufficient_cash",
    ]
    assert points[-1].equity == 1200.0
    assert all(point.cash >= 0 for point in points)


def test_known_equity_metrics_include_max_drawdown() -> None:
    metrics = compute_equity_metrics(pd.Series([100.0, 120.0, 90.0, 108.0]))
    assert metrics["total_return"] == 0.08
    assert metrics["max_drawdown"] == -0.25
    assert metrics["final_equity"] == 108.0
    assert math.isfinite(metrics["annualized_volatility"])
    assert math.isfinite(metrics["sharpe_ratio"])
```

- [ ] **Step 2: Run ledger tests and confirm RED**

Run:

```bash
uv run pytest tests/test_followup_backtest_ledger.py -q
```

Expected: missing `compute_equity_metrics` and `simulate_strategy_sleeve`.

- [ ] **Step 3: Implement daily equity metrics**

Add:

```python
import math
import numpy as np


def compute_equity_metrics(equity: pd.Series) -> dict[str, float | None]:
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
    total_return = final / initial - 1 if initial > 0 else None
    observations = len(values) - 1
    annualized_return = (
        (final / initial) ** (252 / observations) - 1
        if observations > 0 and initial > 0 and final > 0
        else None
    )
    daily_returns = values.pct_change().dropna()
    daily_std = float(daily_returns.std(ddof=1)) if len(daily_returns) > 1 else 0.0
    annualized_volatility = daily_std * math.sqrt(252) if daily_std > 0 else None
    sharpe = (
        float(daily_returns.mean()) / daily_std * math.sqrt(252)
        if daily_std > 0
        else None
    )
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
```

Do not round inside core calculations; round only in text rendering.

- [ ] **Step 4: Implement sleeve event ordering and fractional sizing**

`simulate_strategy_sleeve` must:

1. Convert raw completed and open records to entry candidates sorted by `(entry_date, signal_date)`.
2. Convert raw unfilled signals directly to `TradeRecord(status="unfilled")`.
3. On each calendar date, close `time_expiry` candidates before entries; process other exits after
   entries.
4. On an accepted entry, set `quantity = cash / entry_price` and cash to zero.
5. When a position exists at another candidate's entry open, append
   `skipped_insufficient_cash` without changing cash or position.
6. At the close, mark an open quantity with that date's close; forward-fill only for valuation when
   the ticker is missing a canonical session.
7. Append a `DailyEquityPoint` using unrounded cash, position value, return, drawdown, utilization,
   and open count.
8. Return `TradeRecord` objects in signal-date order and daily points in calendar order.

Use these exact event predicates:

```python
def is_open_exit(candidate: dict[str, Any], date: pd.Timestamp) -> bool:
    return (
        candidate.get("exit_type") == "time_expiry"
        and pd.Timestamp(candidate["exit_date"]) == date
    )


def is_intraday_exit(candidate: dict[str, Any], date: pd.Timestamp) -> bool:
    return (
        candidate.get("exit_type") != "time_expiry"
        and candidate.get("exit_date") is not None
        and pd.Timestamp(candidate["exit_date"]) == date
    )
```

An accepted open candidate remains in the final records with its last mark and unrealized return.

- [ ] **Step 5: Replace temporary cash-only strategy results**

In `run_followup_backtest`, call `simulate_strategy_sleeve`, then populate:

```python
completed = [trade for trade in trades if trade.status == "completed"]
open_trades = [trade for trade in trades if trade.status == "open"]
unfilled = [trade for trade in trades if trade.status == "unfilled"]
skipped = [trade for trade in trades if trade.status == "skipped_insufficient_cash"]
returns = [trade.return_pct for trade in completed if trade.return_pct is not None]
equity = pd.Series([point.equity for point in points], index=[point.date for point in points])
metrics = compute_equity_metrics(equity)

strategy_result.completed_count = len(completed)
strategy_result.open_count = len(open_trades)
strategy_result.unfilled_count = len(unfilled)
strategy_result.skipped_count = len(skipped)
strategy_result.win_rate = (
    sum(value > 0 for value in returns) / len(returns) if returns else None
)
strategy_result.avg_trade_return = float(np.mean(returns)) / 100 if returns else None
strategy_result.cumulative_return = metrics["total_return"]
strategy_result.sharpe_ratio = metrics["sharpe_ratio"]
strategy_result.max_drawdown = metrics["max_drawdown"]
strategy_result.final_equity = metrics["final_equity"]
strategy_result.trades = trades
strategy_result.daily_equity = points
```

- [ ] **Step 6: Run ledger and data tests together**

Run:

```bash
uv run pytest tests/test_followup_backtest_ledger.py tests/test_followup_backtest_data.py -q
```

Expected: all pass.

- [ ] **Step 7: Run focused Ruff checks**

Run:

```bash
uv run ruff check src/trading/followup_backtest.py tests/test_followup_backtest_ledger.py
uv run ruff format --check src/trading/followup_backtest.py tests/test_followup_backtest_ledger.py
```

Expected: both pass. Do not commit.

---

### Task 5: Aggregate equal-weight sleeves into portfolio results

**Files:**

- Modify: `src/trading/followup_backtest.py`
- Modify: `tests/test_followup_backtest_ledger.py`
- Modify: `tests/test_followup_backtest_data.py`

**Interfaces:**

- Produces: `build_portfolio_result(calendar: tuple[pd.Timestamp, ...], strategies:
  list[StrategyBacktestResult], sleeve_cash: float) -> PortfolioBacktestResult`
- Includes failed sleeves as cash for every canonical date
- Produces utilization and concurrency metrics from daily ledger state

- [ ] **Step 1: Add failing portfolio aggregation tests**

Append to `tests/test_followup_backtest_ledger.py`:

```python
from trading.followup_backtest import (
    DailyEquityPoint,
    StrategyBacktestResult,
    build_portfolio_result,
)


def point(date: str, equity: float, cash: float, position: float, open_count: int):
    return DailyEquityPoint(
        date=pd.Timestamp(date),
        equity=equity,
        cash=cash,
        position_value=position,
        daily_return=None,
        drawdown=0.0,
        utilization=position / equity if equity else 0.0,
        open_positions=open_count,
    )


def strategy_result(name: str, points: list[DailyEquityPoint], error: str | None = None):
    return StrategyBacktestResult(
        experiment_name=name,
        label=name.upper(),
        ticker=name.upper(),
        requested_days=2,
        sleeve_initial_cash=500.0,
        daily_equity=points,
        error=error,
    )


def test_portfolio_sums_sleeves_and_known_drawdown() -> None:
    calendar = tuple(pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07"]))
    first = strategy_result(
        "a",
        [
            point("2026-01-05", 500, 500, 0, 0),
            point("2026-01-06", 600, 0, 600, 1),
            point("2026-01-07", 450, 0, 450, 1),
        ],
    )
    second = strategy_result("b", [], error="download failed")
    result = build_portfolio_result(calendar, [first, second], sleeve_cash=500.0)
    assert result.initial_equity == 1000.0
    assert result.final_equity == 950.0
    assert result.total_return == -0.05
    assert result.max_drawdown == pytest.approx(150 / 1100 * -1)
    assert result.maximum_open_positions == 1
    assert result.daily_equity[-1].cash == 500.0


def test_same_day_strategy_entries_have_independent_equal_sleeves() -> None:
    # Use two successful sleeve paths with zero cash and equal position value on day two.
    calendar = tuple(pd.to_datetime(["2026-01-05", "2026-01-06"]))
    points = [
        point("2026-01-05", 500, 500, 0, 0),
        point("2026-01-06", 500, 0, 500, 1),
    ]
    result = build_portfolio_result(
        calendar,
        [strategy_result("a", points), strategy_result("b", points)],
        sleeve_cash=500.0,
    )
    assert result.daily_equity[-1].position_value == 1000.0
    assert result.daily_equity[-1].cash == 0.0
    assert result.maximum_open_positions == 2
    assert result.maximum_utilization == 1.0
```

Import pytest in this file for `pytest.approx`.

Append to the data tests:

```python
def test_insufficient_history_warns_with_actual_range(make_ohlcv) -> None:
    FakeFetcher.frames = {"AAA": make_ohlcv(3)}
    result = run_followup_backtest(
        days=5,
        strategy_definitions=[definition("alpha", "AAA")],
        get_experiment_fn=lambda name: FakeStrategy("AAA"),
        fetcher_factory=FakeFetcher,
    )
    assert len(result.calendar) == 3
    assert any("requested 5" in warning and "available 3" in warning for warning in result.warnings)
```

- [ ] **Step 2: Run the new tests and confirm RED**

Run:

```bash
uv run pytest tests/test_followup_backtest_ledger.py tests/test_followup_backtest_data.py -q
```

Expected: missing `build_portfolio_result` and missing insufficient-history warning.

- [ ] **Step 3: Implement portfolio aggregation**

For every canonical date:

```python
successful_by_name = {
    item.experiment_name: {point.date: point for point in item.daily_equity}
    for item in strategies
    if item.error is None
}
failed_sleeves = sum(item.error is not None for item in strategies)

cash = failed_sleeves * sleeve_cash
position_value = 0.0
open_positions = 0
for item in strategies:
    if item.error is not None:
        continue
    sleeve_point = successful_by_name[item.experiment_name][date]
    cash += sleeve_point.cash
    position_value += sleeve_point.position_value
    open_positions += sleeve_point.open_positions
equity = cash + position_value
```

Derive daily return, running peak/drawdown, and utilization from unrounded totals. Call
`compute_equity_metrics` for total return, annualized return/volatility, Sharpe, maximum drawdown,
and final value. Average/max utilization and max open positions come from daily points.

Call `build_portfolio_result` from `run_followup_backtest` whenever a nonempty canonical calendar
exists. Failed sleeves stay at their initial cash allocation for the whole period.

- [ ] **Step 4: Add exact warnings and errors**

Use stable English messages so tests and users receive clear output:

```python
f"Requested {days} completed sessions; available {len(calendar)} from {start:%Y-%m-%d} to {end:%Y-%m-%d}"
f"{ticker}: missing {missing_count} canonical sessions"
f"Failed to fetch {ticker} data"
f"{experiment_name}: indicator calculation failed: {exc}"
f"{experiment_name}: signal detection failed: {exc}"
f"{experiment_name}: backtest failed: {exc}"
```

Do not suppress the originating strategy error. An empty strategy list returns no portfolio and a
`No followup strategies configured` warning. If all downloads fail, return no calendar and no
portfolio.

- [ ] **Step 5: Run all deterministic core tests**

Run:

```bash
uv run pytest tests/test_execution_open_positions.py tests/test_followup_backtest_data.py tests/test_followup_backtest_ledger.py -q
```

Expected: all pass.

- [ ] **Step 6: Run focused Ruff checks**

Run:

```bash
uv run ruff check src/trading/followup_backtest.py tests/test_followup_backtest_data.py tests/test_followup_backtest_ledger.py
uv run ruff format --check src/trading/followup_backtest.py tests/test_followup_backtest_data.py tests/test_followup_backtest_ledger.py
```

Expected: both pass. Do not commit.

---

### Task 6: Separate rendering from calculation and wire the CLI

**Files:**

- Modify: `src/trading/followup_backtest.py`
- Modify: `src/trading/cli.py`
- Modify: `tests/test_followup_backtest_cli.py`

**Interfaces:**

- Produces: `render_followup_backtest(result, *, output=sys.stdout) -> None`
- Produces: `cmd_followup_backtest(args: argparse.Namespace) -> None`
- CLI exit: zero for full/partial result; one for empty strategies or all failures

- [ ] **Step 1: Write failing rendering and dispatch tests**

Append to `tests/test_followup_backtest_cli.py`:

```python
from argparse import Namespace
from io import StringIO

import pandas as pd

from trading.followup_backtest import (
    FollowupBacktestResult,
    PortfolioBacktestResult,
    StrategyBacktestResult,
    render_followup_backtest,
)


def minimal_result(days: int = 126) -> FollowupBacktestResult:
    strategy = StrategyBacktestResult(
        experiment_name="alpha",
        label="ALPHA-001",
        ticker="AAA",
        requested_days=days,
        sleeve_initial_cash=100000.0,
        signal_count=1,
        completed_count=1,
        open_count=0,
        win_rate=1.0,
        cumulative_return=0.10,
        avg_trade_return=0.10,
        sharpe_ratio=1.5,
        max_drawdown=-0.02,
        final_equity=110000.0,
    )
    portfolio = PortfolioBacktestResult(
        initial_equity=100000.0,
        final_equity=110000.0,
        total_return=0.10,
        annualized_return=0.21,
        annualized_volatility=0.12,
        sharpe_ratio=1.5,
        max_drawdown=-0.02,
        average_utilization=0.40,
        maximum_utilization=1.0,
        maximum_open_positions=1,
        daily_equity=[],
    )
    return FollowupBacktestResult(
        requested_days=days,
        calendar=tuple(pd.to_datetime(["2026-01-05", "2026-01-06"])),
        strategies=[strategy],
        portfolio=portfolio,
    )


def test_renderer_prints_strategy_and_portfolio_metrics() -> None:
    output = StringIO()
    render_followup_backtest(minimal_result(), output=output)
    text = output.getvalue()
    assert "ALPHA-001" in text
    assert "AAA" in text
    assert "Portfolio total return" in text
    assert "+10.00%" in text
    assert "Final asset value" in text


def test_cli_dispatch_passes_180_days(monkeypatch) -> None:
    captured = {}

    def fake_run(days: int) -> FollowupBacktestResult:
        captured["days"] = days
        return minimal_result(days)

    monkeypatch.setattr("trading.followup_backtest.run_followup_backtest", fake_run)
    monkeypatch.setattr("trading.followup_backtest.render_followup_backtest", lambda result: None)
    from trading.cli import main

    main(["followup-backtest", "--days", "180"])
    assert captured["days"] == 180


def test_cli_exits_one_when_all_strategies_fail(monkeypatch) -> None:
    failed = FollowupBacktestResult(
        requested_days=126,
        calendar=(),
        strategies=[
            StrategyBacktestResult(
                experiment_name="bad",
                label="BAD",
                ticker="BAD",
                requested_days=126,
                sleeve_initial_cash=100000.0,
                error="Failed to fetch BAD data",
            )
        ],
        portfolio=None,
    )
    monkeypatch.setattr("trading.followup_backtest.run_followup_backtest", lambda days: failed)
    monkeypatch.setattr("trading.followup_backtest.render_followup_backtest", lambda result: None)
    from trading.cli import main

    with pytest.raises(SystemExit) as exc_info:
        main(["followup-backtest"])
    assert exc_info.value.code == 1


def test_existing_followup_dispatch_is_unchanged(monkeypatch) -> None:
    called = []
    monkeypatch.setattr("trading.followup.run_followup", lambda: called.append(True))
    from trading.cli import main

    main(["followup"])
    assert called == [True]
```

- [ ] **Step 2: Run CLI tests and confirm RED**

Run:

```bash
uv run pytest tests/test_followup_backtest_cli.py -q
```

Expected: renderer and dispatch tests fail because they are not implemented.

- [ ] **Step 3: Implement the renderer**

`render_followup_backtest` must use only the supplied result and output stream. It must print:

- requested and actual period;
- portfolio initial/final value, total/annualized return, annualized volatility, Sharpe, maximum
  drawdown, average/maximum utilization, and maximum open positions;
- every strategy's experiment name, ticker, actual dates, signals, completed/open/unfilled/skipped
  counts, win rate, cumulative return, average trade return, Sharpe, maximum drawdown, warnings/errors;
- every trade's status, signal/entry/exit dates, entry/exit/mark prices, quantity, return, exit type,
  and reason when present; and
- a notice that open trades are MTM and excluded from realized win rate.

Use helpers with these exact unavailable/percentage semantics:

```python
def _format_percent(value: float | None, *, signed: bool = False) -> str:
    if value is None:
        return "N/A"
    return f"{value:+.2%}" if signed else f"{value:.2%}"


def _format_ratio(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.2f}"
```

Do not recompute metrics inside the renderer.

- [ ] **Step 4: Wire CLI dispatch**

Add:

```python
def cmd_followup_backtest(args: argparse.Namespace) -> None:
    from trading.followup_backtest import render_followup_backtest, run_followup_backtest

    result = run_followup_backtest(days=args.days)
    render_followup_backtest(result)
    if not result.strategies or result.all_failed:
        raise SystemExit(1)
```

And dispatch before `compare`:

```python
elif args.command == "followup-backtest":
    cmd_followup_backtest(args)
```

A partial failure does not raise because `all_failed` is false.

- [ ] **Step 5: Run CLI and all deterministic tests**

Run:

```bash
uv run pytest tests -q
```

Expected: all tests pass with no network access.

- [ ] **Step 6: Verify help output**

Run:

```bash
uv run trading followup-backtest --help
uv run trading followup-backtest --days 0
```

Expected: help shows default 126; invalid input exits 2 and says `must be a positive integer`.

---

### Task 7: Synchronize documentation and protect existing followup behavior

**Files:**

- Modify: `README.md`
- Modify: `CLAUDE.md:60-114`
- Modify: `tests/test_followup_backtest_cli.py`

**Interfaces:**

- Documents the exact approved USD 100,000 sleeve model and MTM semantics
- Documents `followup-backtest` without changing experiment documentation

- [ ] **Step 1: Strengthen the followup regression test**

Add a test that statically and behaviorally protects the 60-session default:

```python
def test_existing_followup_lookback_remains_60() -> None:
    from trading.followup import LOOKBACK_TRADING_DAYS

    assert LOOKBACK_TRADING_DAYS == 60
```

Run:

```bash
uv run pytest tests/test_followup_backtest_cli.py::test_existing_followup_lookback_remains_60 -q
```

Expected: pass before documentation changes.

- [ ] **Step 2: Add README usage and assumptions**

Add a `Followup Backtest` section after Quick Start containing both commands and these exact facts:

````markdown
## Followup Backtest

```bash
uv run trading followup-backtest             # last 126 completed trading sessions
uv run trading followup-backtest --days 180  # last 180 completed trading sessions
```

The command reads the current `STRATEGIES` entries from `src/trading/followup.py`; it does not keep a
second strategy list. It starts with a normalized USD 100,000 portfolio split equally into fixed
strategy sleeves. Sleeves use fractional shares, do not borrow or rebalance across strategies, and
keep failed-strategy allocations in cash.

Signals and execution retain each experiment's current backtester, including next-open fills,
slippage, stops, targets, expiry, pessimistic intrabar handling, and trailing stops. Open positions at
the period end are marked to the last completed adjusted close. Open MTM affects equity return and
drawdown but is excluded from completed-trade win rate and average trade return.
````

- [ ] **Step 3: Update CLAUDE.md commands and architecture**

Add under the existing followup command:

```bash
# 回測目前跟單策略組合（預設最近 126 個完整交易日）
uv run trading followup-backtest

# 自訂完整交易日數
uv run trading followup-backtest --days 180
```

Add to the architecture tree:

```text
├── followup_backtest.py         # 跟單策略等權袖套回測、每日 equity 與結構化報告
```

Do not edit any `EXPERIMENTS_*.md` or `pm/` file because strategy definitions/results are unchanged.

- [ ] **Step 4: Verify docs and source remain synchronized**

Run:

```bash
rg -n "followup-backtest|126|180|100,000|mark" README.md CLAUDE.md
git diff --check
git status --short
```

Expected: both docs mention the new command and approved assumptions; no `pm/` path appears in status.

---

### Task 8: Full verification, 126/180 validation, and final handoff

**Files:**

- Verify all modified files; make only fixes required by failing checks.

**Interfaces:**

- Confirms deterministic correctness, backward compatibility, lint, formatting, and live-mode behavior

- [ ] **Step 1: Run the complete deterministic test suite**

Run:

```bash
uv run pytest tests -q
```

Expected: all tests pass; none access live network data.

- [ ] **Step 2: Run required lint and format checks**

Run:

```bash
uv run ruff check src/
uv run ruff format --check src/
```

Expected: zero lint errors and zero files requiring formatting.

- [ ] **Step 3: Run test-file lint as an additional check**

Run:

```bash
uv run ruff check tests/
uv run ruff format --check tests/
```

Expected: both pass.

- [ ] **Step 4: Verify invalid CLI input and existing followup dispatch**

Run:

```bash
uv run trading followup-backtest --days 0
uv run pytest tests/test_followup_backtest_cli.py::test_existing_followup_dispatch_is_unchanged tests/test_followup_backtest_cli.py::test_existing_followup_lookback_remains_60 -q
```

Expected: invalid input exits 2 with a clear message; both regression tests pass.

- [ ] **Step 5: Run live 126-session validation**

Run:

```bash
uv run trading followup-backtest
```

Expected when market data is reachable: the header reports requested 126 completed sessions, the
actual portfolio range contains 126 canonical dates unless an explicit insufficient-data warning is
printed, every current `STRATEGIES` entry is present as success/error, and portfolio metrics/final
value are printed. Capture the actual range, strategy success/failure count, open count, total return,
and final asset value for the handoff.

If live download is unavailable, do not treat deterministic tests as live validation. Record the
network/data error explicitly and retain the successful fixture-based 126-day validation.

- [ ] **Step 6: Run live 180-session validation**

Run:

```bash
uv run trading followup-backtest --days 180
```

Expected when market data is reachable: the header reports requested 180 completed sessions and the
same reporting guarantees as Step 5. Capture the actual range and summary metrics separately.

- [ ] **Step 7: Perform final diff and scope review**

Run:

```bash
git diff --check
git diff --stat
git status --short --branch
git diff --name-only
```

Expected: only the files named in this plan plus the approved design/plan are changed; no `pm/` file,
commit, push, or PR exists.

- [ ] **Step 8: Report results without committing**

The final response must include:

- the approved equal-weight sleeve model and why it was chosen;
- every changed file;
- both CLI forms;
- deterministic pytest totals and required Ruff results;
- actual 126-day and 180-day validation ranges/results, or explicit live-data blockers;
- remaining limitations: fractional-share normalization, zero commissions, MTM without liquidation
  slippage, no inherited pre-period positions, and detector-defined auxiliary-data fallbacks; and
- confirmation that `pm/` was untouched and no commit/push/PR was created.

Do not stage or commit the files.
