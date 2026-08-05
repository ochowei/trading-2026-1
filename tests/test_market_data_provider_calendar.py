from datetime import UTC, date, datetime

import pandas as pd

from trading.market_data import (
    MarketDataSeries,
    PrimaryUSSessionCalendar,
    YahooFinanceProvider,
)


def test_yahoo_provider_requests_only_auto_adjusted_daily_data(monkeypatch) -> None:
    columns = pd.MultiIndex.from_product([["Open", "High", "Low", "Close", "Volume"], ["SPY"]])
    raw = pd.DataFrame(
        [[10.0, 12.0, 9.0, 11.0, 100.0]],
        index=pd.to_datetime(["2026-08-03"]),
        columns=columns,
    )
    captured = {}

    def fake_download(symbol, **kwargs):
        captured.update(symbol=symbol, **kwargs)
        return raw

    monkeypatch.setattr("trading.market_data.provider.yf.download", fake_download)

    result = YahooFinanceProvider().fetch(
        MarketDataSeries.yahoo_adjusted_daily("SPY"),
        start=date(2026, 8, 3),
        end=date(2026, 8, 3),
    )

    assert captured == {
        "symbol": "SPY",
        "progress": False,
        "auto_adjust": True,
        "interval": "1d",
        "threads": False,
        "start": "2026-08-03",
        "end": "2026-08-04",
    }
    assert list(result.columns) == ["Open", "High", "Low", "Close", "Volume"]


def test_yahoo_full_refresh_uses_max_period_and_applies_inclusive_cutoff(monkeypatch) -> None:
    raw = pd.DataFrame(
        {
            "Open": [10.0, 11.0],
            "High": [12.0, 13.0],
            "Low": [9.0, 10.0],
            "Close": [11.0, 12.0],
            "Volume": [100.0, 200.0],
        },
        index=pd.to_datetime(["2026-08-03", "2026-08-04"]),
    )
    captured = {}

    def fake_download(symbol, **kwargs):
        captured.update(symbol=symbol, **kwargs)
        return raw

    monkeypatch.setattr("trading.market_data.provider.yf.download", fake_download)

    result = YahooFinanceProvider().fetch(
        MarketDataSeries.yahoo_adjusted_daily("SPY"),
        start=None,
        end=date(2026, 8, 3),
    )

    assert captured == {
        "symbol": "SPY",
        "progress": False,
        "auto_adjust": True,
        "interval": "1d",
        "threads": False,
        "period": "max",
    }
    assert list(result.index) == [pd.Timestamp("2026-08-03")]


def test_primary_us_session_cutoff_is_conservative() -> None:
    calendar = PrimaryUSSessionCalendar()

    assert calendar.latest_completed_session(datetime(2026, 8, 5, 20, 29, tzinfo=UTC)) == date(
        2026, 8, 4
    )
    assert calendar.latest_completed_session(datetime(2026, 8, 5, 20, 30, tzinfo=UTC)) == date(
        2026, 8, 5
    )
    assert date(2026, 7, 3) not in {
        item.date() for item in calendar.sessions_in_range(date(2026, 7, 2), date(2026, 7, 6))
    }
    # Unlike US federal offices, NYSE does not observe a Saturday New Year on Friday.
    assert date(2021, 12, 31) in {
        item.date() for item in calendar.sessions_in_range(date(2021, 12, 30), date(2022, 1, 3))
    }


def test_primary_us_calendar_covers_historical_emergency_closures() -> None:
    calendar = PrimaryUSSessionCalendar()

    sessions = {
        item.date() for item in calendar.sessions_in_range(date(2001, 9, 10), date(2001, 9, 17))
    }

    assert sessions == {date(2001, 9, 10), date(2001, 9, 17)}


def test_primary_us_cutoff_uses_the_actual_early_close() -> None:
    calendar = PrimaryUSSessionCalendar()

    assert calendar.latest_completed_session(datetime(2026, 11, 27, 18, 29, tzinfo=UTC)) == date(
        2026, 11, 25
    )
    assert calendar.latest_completed_session(datetime(2026, 11, 27, 18, 30, tzinfo=UTC)) == date(
        2026, 11, 27
    )
