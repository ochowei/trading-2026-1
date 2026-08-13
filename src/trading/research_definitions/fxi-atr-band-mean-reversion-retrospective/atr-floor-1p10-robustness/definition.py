"""Retrospective FXI ATR-band challenge with a stricter 1.10 floor."""

from datetime import date
from pathlib import Path

from trading.research_definitions.fxi_mean_reversion import (
    FXIMeanReversionResearchDefinition,
    FXIMeanReversionTrialConfig,
)

DEFINITION = FXIMeanReversionResearchDefinition(
    identity="fxi-atr-band-mean-reversion-retrospective/atr-floor-1p10-robustness",
    result_name="fxi-atr-band-mean-reversion-retrospective--atr-floor-1p10-robustness",
    family="fxi-atr-band-mean-reversion-retrospective",
    hypothesis="The retrospective candidate remains viable with an ATR floor of 1.10.",
    config=FXIMeanReversionTrialConfig(
        ticker="FXI",
        history_start=date(2009, 1, 2),
        research_start=date(2010, 1, 4),
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
        atr_ratio_ceiling=1.35,
    ),
    source_path=Path(__file__),
)
