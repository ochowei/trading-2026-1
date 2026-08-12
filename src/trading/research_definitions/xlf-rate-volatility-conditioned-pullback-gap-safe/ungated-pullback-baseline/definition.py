"""Gap-safe XLF pullback family baseline without the MOVE gate."""

from datetime import date
from pathlib import Path

from trading.research_definitions.rate_volatility_pullback import (
    RateVolatilityPullbackTrialConfig,
)
from trading.research_definitions.rate_volatility_pullback_gap_safe import (
    GapSafeRateVolatilityPullbackResearchDefinition,
)

DEFINITION = GapSafeRateVolatilityPullbackResearchDefinition(
    identity="xlf-rate-volatility-conditioned-pullback-gap-safe/ungated-pullback-baseline",
    result_name="xlf-rate-volatility-conditioned-pullback-gap-safe--ungated-pullback-baseline",
    family="xlf-rate-volatility-conditioned-pullback-gap-safe",
    hypothesis="The ungated XLF pullback is the distinct simple gap-safe family baseline.",
    config=RateVolatilityPullbackTrialConfig(
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
