from datetime import date

from trading.market_data import AvailabilityPolicy, MarketDataSeries
from trading.market_data.calendar import PrimaryUSSessionCalendar


def test_us_equity_market_v001_matches_executable_market_boundary() -> None:
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cutoff = PrimaryUSSessionCalendar().decision_time(date(2026, 8, 11))

    assert (series.provider, series.interval, series.adjustment_policy) == (
        "yahoo",
        "1d",
        "auto_adjusted",
    )
    assert (cutoff.hour, cutoff.minute) == (20, 30)
    assert AvailabilityPolicy().publication_lag_sessions == 1
