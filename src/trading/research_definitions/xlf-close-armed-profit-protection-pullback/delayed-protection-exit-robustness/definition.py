"""Delayed-exit robustness definition for the XLF profit-protection study."""

from datetime import date
from pathlib import Path

from trading.research_definitions.profit_protection_pullback import (
    ProfitProtectionPullbackResearchDefinition,
    ProfitProtectionPullbackTrialConfig,
)

DEFINITION = ProfitProtectionPullbackResearchDefinition(
    identity="xlf-close-armed-profit-protection-pullback/delayed-protection-exit-robustness",
    result_name="xlf-close-armed-profit-protection-pullback--delayed-protection-exit-robustness",
    family="xlf-close-armed-profit-protection-pullback",
    hypothesis="One additional session of exit delay must not reverse the protection claim.",
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
        arm_return=0.02,
        floor_return=0.005,
        protection_exit_lag_sessions=2,
    ),
    source_path=Path(__file__),
)
