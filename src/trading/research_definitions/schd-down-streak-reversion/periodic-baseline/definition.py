"""SCHD unconditioned periodic-exposure family baseline."""

from datetime import date
from pathlib import Path

from trading.research_definitions.daily_bar import (
    DailyBarResearchDefinition,
    DailyBarTrialConfig,
)

DEFINITION = DailyBarResearchDefinition(
    identity="schd-down-streak-reversion/periodic-baseline",
    result_name="schd-down-streak-reversion--periodic-baseline",
    family="schd-down-streak-reversion",
    hypothesis="Unconditioned five-session SCHD exposure is the simple family comparator.",
    config=DailyBarTrialConfig(
        ticker="SCHD",
        history_start=date(2022, 1, 1),
        research_start=date(2023, 1, 1),
        signal_kind="periodic-baseline",
        holding_sessions=5,
    ),
    source_path=Path(__file__),
)
