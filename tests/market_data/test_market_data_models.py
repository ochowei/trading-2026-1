from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from trading.market_data import (
    MarketDataReader,
    MarketDataSeries,
    PrimaryUSSessionCalendar,
    RefreshKind,
    SessionCalendar,
    SignalDecisionTime,
    decode_symbol,
    encode_symbol,
)


class FakeMarketDataReader:
    def get(self, series, *, start, end):
        return None


@pytest.mark.parametrize("symbol", ["^VIX", "BRK-B", "BTC-USD", "台積電.TW"])
def test_filesystem_symbol_encoding_is_safe_and_round_trips(symbol: str) -> None:
    encoded = encode_symbol(symbol)

    assert encoded.startswith("v1-")
    assert all(character.isalnum() or character in "-_" for character in encoded)
    assert decode_symbol(encoded) == symbol


def test_market_data_series_supports_only_phase_one_contract() -> None:
    series = MarketDataSeries.yahoo_adjusted_daily("^VIX")

    assert series.provider == "yahoo"
    assert series.symbol == "^VIX"
    assert series.interval == "1d"
    assert series.adjustment_policy == "auto_adjusted"

    with pytest.raises(ValueError, match="Phase 1"):
        MarketDataSeries(
            provider="other",
            symbol="SPY",
            interval="1h",
            adjustment_policy="raw",
        )


def test_signal_decision_time_uses_actual_early_close_cutoff() -> None:
    calendar = PrimaryUSSessionCalendar()
    session = date(2026, 11, 27)

    decision = SignalDecisionTime.for_primary_session(session, calendar=calendar)

    assert decision.decided_at.astimezone(ZoneInfo("America/New_York")).strftime("%H:%M") == "13:30"
    with pytest.raises(ValueError, match="session cutoff"):
        SignalDecisionTime(
            session,
            datetime(2026, 11, 27, 13, 29, tzinfo=ZoneInfo("America/New_York")),
        )


def test_market_data_domain_contracts_are_shared_and_structural() -> None:
    assert RefreshKind("incremental") is RefreshKind.INCREMENTAL
    assert RefreshKind("full") is RefreshKind.FULL
    assert isinstance(PrimaryUSSessionCalendar(), SessionCalendar)
    assert isinstance(FakeMarketDataReader(), MarketDataReader)
