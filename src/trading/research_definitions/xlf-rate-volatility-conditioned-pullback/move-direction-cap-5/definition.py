"""XLF pullback trial with a five-point MOVE direction cap."""

from datetime import date
from pathlib import Path

from trading.research_definitions.rate_volatility_pullback import (
    RateVolatilityPullbackResearchDefinition,
    RateVolatilityPullbackTrialConfig,
)

DEFINITION = RateVolatilityPullbackResearchDefinition(
    identity="xlf-rate-volatility-conditioned-pullback/move-direction-cap-5",
    result_name="xlf-rate-volatility-conditioned-pullback--move-direction-cap-5",
    family="xlf-rate-volatility-conditioned-pullback",
    hypothesis="XLF pullbacks improve when backward-as-of MOVE acceleration is capped.",
    config=RateVolatilityPullbackTrialConfig(
        ticker="XLF",
        history_start=date(1998, 12, 16),
        research_start=date(2000, 1, 3),
        holding_sessions=10,
        entry_lag_sessions=1,
        pullback_lookback=10,
        pullback_threshold=-0.04,
        bollinger_lookback=20,
        bollinger_stddevs=2.0,
        move_ticker="^MOVE",
        move_change_sessions=3,
        move_change_cap=5.0,
    ),
    source_path=Path(__file__),
)
