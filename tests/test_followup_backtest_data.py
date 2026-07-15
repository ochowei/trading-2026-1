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
    )
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
    assert result.strategies[0].signal_count == 0
    assert result.strategies[0].warmup_rows == 4


def test_strategy_definitions_are_read_at_call_time(monkeypatch, make_ohlcv) -> None:
    FakeFetcher.frames = {"NEW": make_ohlcv(4)}
    monkeypatch.setattr("trading.followup.STRATEGIES", [definition("newest", "NEW")])
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


def test_insufficient_history_warns_with_actual_range(make_ohlcv) -> None:
    FakeFetcher.frames = {"AAA": make_ohlcv(3)}
    result = run_followup_backtest(
        days=5,
        strategy_definitions=[definition("alpha", "AAA")],
        get_experiment_fn=lambda name: FakeStrategy("AAA"),
        fetcher_factory=FakeFetcher,
    )
    assert len(result.calendar) == 3
    assert any("Requested 5" in warning and "available 3" in warning for warning in result.warnings)


def test_primary_tickers_are_downloaded_in_isolated_calls(make_ohlcv) -> None:
    class RecordingFetcher(FakeFetcher):
        calls: list[list[str]] = []

        def fetch_all(self, tickers: list[str]) -> dict[str, pd.DataFrame]:
            self.calls.append(tickers)
            return super().fetch_all(tickers)

    RecordingFetcher.frames = {"AAA": make_ohlcv(5), "BBB": make_ohlcv(5)}
    run_followup_backtest(
        days=3,
        strategy_definitions=[definition("alpha", "AAA"), definition("beta", "BBB")],
        get_experiment_fn=lambda name: FakeStrategy("AAA" if name == "alpha" else "BBB"),
        fetcher_factory=RecordingFetcher,
    )
    assert RecordingFetcher.calls == [["AAA"], ["BBB"]]
