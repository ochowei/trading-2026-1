"""SCHD two-session down-streak mean-reversion trial."""

from datetime import date
from pathlib import Path

from trading.research_definitions.daily_bar import (
    DailyBarResearchDefinition,
    DailyBarTrialConfig,
)

DEFINITION = DailyBarResearchDefinition(
    identity="schd-down-streak-reversion/two-down",
    result_name="schd-down-streak-reversion--two-down",
    family="schd-down-streak-reversion",
    hypothesis="SCHD rebounds after consecutive down closes under frozen costs.",
    config=DailyBarTrialConfig(
        ticker="SCHD",
        history_start=date(2022, 1, 1),
        research_start=date(2023, 1, 1),
        signal_kind="down-streak",
        consecutive_down_sessions=2,
        holding_sessions=5,
    ),
    source_path=Path(__file__),
)
