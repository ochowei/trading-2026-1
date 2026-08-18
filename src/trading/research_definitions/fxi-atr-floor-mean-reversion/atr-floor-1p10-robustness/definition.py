"""FXI ATR-floor robustness challenge with a stricter 1.10 floor."""

from datetime import date
from pathlib import Path

from trading.research_definitions.fxi_mean_reversion import (
    FXIMeanReversionResearchDefinition,
    FXIMeanReversionTrialConfig,
)

DEFINITION = FXIMeanReversionResearchDefinition(
    identity="fxi-atr-floor-mean-reversion/atr-floor-1p10-robustness",
    result_name="fxi-atr-floor-mean-reversion--atr-floor-1p10-robustness",
    family="fxi-atr-floor-mean-reversion",
    hypothesis="The FXI candidate remains viable with a stricter ATR-ratio floor of 1.10.",
    config=FXIMeanReversionTrialConfig(
        ticker="FXI",
        history_start=date(2013, 11, 6),
        research_start=date(2015, 1, 2),
        holding_sessions=20,
        entry_lag_sessions=1,
        pullback_lookback=10,
        pullback_threshold=-0.05,
        pullback_cap=-0.12,
        wr_period=10,
        wr_threshold=-80.0,
        cooldown_sessions=10,
        profit_target=0.055,
        stop_loss=-0.05,
        close_position_threshold=0.4,
        atr_short_period=5,
        atr_long_period=20,
        atr_ratio_floor=1.10,
        atr_ratio_ceiling=None,
    ),
    source_path=Path(__file__),
)
