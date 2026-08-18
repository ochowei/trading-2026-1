"""Sole FXI no-ClosePos ATR-floor mean-reversion selection candidate."""

from datetime import date
from pathlib import Path

from trading.research_definitions.fxi_mean_reversion import (
    FXIMeanReversionResearchDefinition,
    FXIMeanReversionTrialConfig,
)

DEFINITION = FXIMeanReversionResearchDefinition(
    identity=("fxi-no-closepos-atr-floor-mean-reversion/no-closepos-atr-floor-candidate"),
    result_name=("fxi-no-closepos-atr-floor-mean-reversion--no-closepos-atr-floor-candidate"),
    family="fxi-no-closepos-atr-floor-mean-reversion",
    hypothesis=(
        "Removing the secondary ClosePos confirmation while retaining the FXI ATR floor "
        "improves sample coverage without weakening frozen eligibility gates."
    ),
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
        close_position_threshold=None,
        atr_short_period=5,
        atr_long_period=20,
        atr_ratio_floor=1.05,
        atr_ratio_ceiling=None,
    ),
    source_path=Path(__file__),
)
