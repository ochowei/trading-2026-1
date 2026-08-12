"""Revised-availability XLF pullback baseline without the MOVE gate."""

from datetime import date
from pathlib import Path

from trading.research_definitions.rate_volatility_pullback import (
    RateVolatilityPullbackResearchDefinition,
    RateVolatilityPullbackTrialConfig,
)

DEFINITION = RateVolatilityPullbackResearchDefinition(
    identity=(
        "xlf-rate-volatility-conditioned-pullback-revised-availability/ungated-pullback-baseline"
    ),
    result_name=(
        "xlf-rate-volatility-conditioned-pullback-revised-availability--ungated-pullback-baseline"
    ),
    family="xlf-rate-volatility-conditioned-pullback-revised-availability",
    hypothesis="The ungated XLF pullback is the distinct simple family baseline.",
    config=RateVolatilityPullbackTrialConfig(
        ticker="XLF",
        history_start=date(1998, 12, 22),
        research_start=date(2000, 1, 3),
        holding_sessions=10,
        entry_lag_sessions=1,
        pullback_lookback=10,
        pullback_threshold=-0.04,
        bollinger_lookback=20,
        bollinger_stddevs=2.0,
    ),
    source_path=Path(__file__),
)
