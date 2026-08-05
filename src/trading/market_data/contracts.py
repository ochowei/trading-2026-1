"""Shared structural contracts and vocabularies for market-data access."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol, runtime_checkable

import pandas as pd

if TYPE_CHECKING:
    from trading.market_data.models import MarketDataSeries


class RefreshKind(StrEnum):
    """A cache refresh operation's historical scope."""

    INCREMENTAL = "incremental"
    FULL = "full"


@runtime_checkable
class SessionCalendar(Protocol):
    """Primary-session calculations required by market-data components."""

    def sessions_in_range(self, start: date, end: date) -> pd.DatetimeIndex: ...

    def session_on_or_before(self, value: date) -> date: ...

    def session_on_or_after(self, value: date) -> date: ...

    def session_offset(self, value: date, offset: int) -> date: ...

    def session_distance(self, older: date, newer: date) -> int: ...

    def decision_time(self, session: date) -> datetime: ...

    def latest_completed_session(self, now: datetime) -> date: ...


@runtime_checkable
class MarketDataReader(Protocol):
    """Compatibility boundary needed by legacy primary-ticker callers."""

    def get(
        self,
        series: MarketDataSeries,
        *,
        start: date | None,
        end: date | None,
    ) -> pd.DataFrame: ...
