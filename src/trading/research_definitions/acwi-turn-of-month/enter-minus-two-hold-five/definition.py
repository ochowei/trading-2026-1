"""ACWI turn-of-month candidate entering at the M-2 open."""

from datetime import date
from pathlib import Path

from trading.research_definitions.monthly_calendar import (
    MonthlyCalendarResearchDefinition,
    MonthlyCalendarTrialConfig,
)

DEFINITION = MonthlyCalendarResearchDefinition(
    identity="acwi-turn-of-month/enter-minus-two-hold-five",
    result_name="acwi-turn-of-month--enter-minus-two-hold-five",
    family="acwi-turn-of-month",
    hypothesis="ACWI has a net turn-of-month cash-flow effect around the M-2 open.",
    config=MonthlyCalendarTrialConfig(
        ticker="ACWI",
        history_start=date(2008, 3, 28),
        research_start=date(2009, 1, 1),
        holding_sessions=5,
        entry_kind="month-end-offset",
        month_end_offset=-2,
    ),
    source_path=Path(__file__),
)
