"""Primary US trading-session calendar used by Phase 1 market data."""

from __future__ import annotations

from datetime import date, datetime

import exchange_calendars as exchange_calendars
import pandas as pd

_CALENDAR_START = "1900-01-01"
_CALENDAR_END = "2100-12-31"
_DECISION_BUFFER = pd.Timedelta(minutes=30)


class PrimaryUSSessionCalendar:
    """XNYS sessions and each session's actual close plus a 30-minute buffer."""

    def __init__(self) -> None:
        self._calendar = exchange_calendars.get_calendar(
            "XNYS",
            start=_CALENDAR_START,
            end=_CALENDAR_END,
        )

    def sessions_in_range(self, start: date, end: date) -> pd.DatetimeIndex:
        if start > end:
            return pd.DatetimeIndex([])
        return self._calendar.sessions_in_range(start, end).normalize()

    def session_on_or_before(self, value: date) -> date:
        return self._calendar.date_to_session(value, direction="previous").date()

    def session_on_or_after(self, value: date) -> date:
        return self._calendar.date_to_session(value, direction="next").date()

    def session_offset(self, value: date, offset: int) -> date:
        anchor = self._calendar.date_to_session(value, direction="previous")
        return self._calendar.session_offset(anchor, offset).date()

    def session_distance(self, older: date, newer: date) -> int:
        older_session = self._calendar.date_to_session(older, direction="previous")
        newer_session = self._calendar.date_to_session(newer, direction="previous")
        if newer_session < older_session:
            raise ValueError("newer session precedes older session")
        return self._calendar.sessions_distance(older_session, newer_session) - 1

    def decision_time(self, session: date) -> datetime:
        """Return the actual XNYS close plus the conservative publication buffer."""
        session_label = self._calendar.date_to_session(session, direction="none")
        return (self._calendar.session_close(session_label) + _DECISION_BUFFER).to_pydatetime()

    def latest_completed_session(self, now: datetime) -> date:
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        now_utc = pd.Timestamp(now).tz_convert("UTC")
        candidate = self._calendar.date_to_session(now_utc.date(), direction="previous")
        if candidate.date() != now_utc.date():
            return candidate.date()
        decision_cutoff = pd.Timestamp(self.decision_time(candidate.date()))
        if now_utc >= decision_cutoff:
            return candidate.date()
        return self._calendar.session_offset(candidate, -1).date()
