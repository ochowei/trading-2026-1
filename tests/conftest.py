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
            if is_signal and (
                last_position is None or position - last_position > self.cooldown_days
            ):
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
