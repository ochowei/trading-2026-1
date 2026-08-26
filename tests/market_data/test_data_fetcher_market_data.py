from datetime import date

import pandas as pd

from trading.core.data_fetcher import DataFetcher


class FakeMarketDataService:
    def __init__(self, frame: pd.DataFrame):
        self.frame = frame
        self.calls = []

    def get(self, series, *, start, end):
        self.calls.append((series, start, end))
        return self.frame.copy()


def test_data_fetcher_keeps_normalized_fetch_all_contract(make_ohlcv) -> None:
    frame = make_ohlcv(3)
    service = FakeMarketDataService(frame)

    fetched = DataFetcher(
        start="2025-01-02",
        end="2025-01-06",
        market_data_service=service,
    ).fetch_all(["SPY"])

    assert list(fetched) == ["SPY"]
    pd.testing.assert_frame_equal(fetched["SPY"], frame)
    series, start, end = service.calls[0]
    assert series.symbol == "SPY"
    assert start == date(2025, 1, 2)
    # DataFetcher preserves yfinance's historical exclusive-end contract.
    assert end == date(2025, 1, 5)


def test_data_fetcher_isolates_one_ticker_failure(make_ohlcv) -> None:
    class PartiallyFailingService(FakeMarketDataService):
        def get(self, series, *, start, end):
            if series.symbol == "BAD":
                raise RuntimeError("unavailable")
            return self.frame.copy()

    fetched = DataFetcher(
        start="2025-01-02",
        market_data_service=PartiallyFailingService(make_ohlcv(2)),
    ).fetch_all(["BAD", "GOOD"])

    assert list(fetched) == ["GOOD"]


def test_data_fetcher_preserves_supported_period_slicing(make_ohlcv) -> None:
    frame = make_ohlcv(10)
    service = FakeMarketDataService(frame)

    fetched = DataFetcher(period="5d", market_data_service=service).fetch_all(["SPY"])

    pd.testing.assert_frame_equal(fetched["SPY"], frame.tail(5))
    _, start, end = service.calls[0]
    assert start is None
    assert end is None


def test_data_fetcher_rejects_unknown_period_without_network(make_ohlcv) -> None:
    service = FakeMarketDataService(make_ohlcv(3))

    fetched = DataFetcher(period="forever", market_data_service=service).fetch_all(["SPY"])

    assert fetched == {}
    assert service.calls == []
