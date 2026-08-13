"""Distinct fixed-ten-session baseline for the XLF exit study."""

from datetime import date
from pathlib import Path

from trading.research_definitions.profit_protection_pullback import (
    ProfitProtectionPullbackResearchDefinition,
    ProfitProtectionPullbackTrialConfig,
)

DEFINITION = ProfitProtectionPullbackResearchDefinition(
    identity="xlf-close-armed-profit-protection-pullback/fixed-ten-session-baseline",
    result_name="xlf-close-armed-profit-protection-pullback--fixed-ten-session-baseline",
    family="xlf-close-armed-profit-protection-pullback",
    hypothesis="The fixed ten-session XLF pullback is the distinct simple family baseline.",
    config=ProfitProtectionPullbackTrialConfig(
        ticker="XLF",
        history_start=date(2002, 11, 13),
        research_start=date(2004, 1, 2),
        holding_sessions=10,
        entry_lag_sessions=1,
        pullback_lookback=10,
        pullback_threshold=-0.04,
        bollinger_lookback=20,
        bollinger_stddevs=2.0,
    ),
    source_path=Path(__file__),
)
