"""ACWI distinct mid-month family baseline."""

from datetime import date
from pathlib import Path

from trading.research_definitions.monthly_calendar import (
    MonthlyCalendarResearchDefinition,
    MonthlyCalendarTrialConfig,
)

DEFINITION = MonthlyCalendarResearchDefinition(
    identity="acwi-turn-of-month/enter-session-ten-hold-five",
    result_name="acwi-turn-of-month--enter-session-ten-hold-five",
    family="acwi-turn-of-month",
    hypothesis="A tenth-session monthly exposure is the distinct simple family baseline.",
    config=MonthlyCalendarTrialConfig(
        ticker="ACWI",
        history_start=date(2008, 3, 28),
        research_start=date(2009, 1, 1),
        holding_sessions=5,
        entry_kind="session-ordinal",
        session_ordinal=10,
    ),
    source_path=Path(__file__),
)
