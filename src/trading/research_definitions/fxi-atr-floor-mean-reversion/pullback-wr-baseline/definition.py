"""Distinct simple FXI pullback and Williams-%R family baseline."""

from datetime import date
from pathlib import Path

from trading.research_definitions.fxi_mean_reversion import (
    FXIMeanReversionResearchDefinition,
    FXIMeanReversionTrialConfig,
)

DEFINITION = FXIMeanReversionResearchDefinition(
    identity="fxi-atr-floor-mean-reversion/pullback-wr-baseline",
    result_name="fxi-atr-floor-mean-reversion--pullback-wr-baseline",
    family="fxi-atr-floor-mean-reversion",
    hypothesis="A simple pullback and Williams-%R rule is the distinct FXI family baseline.",
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
    ),
    source_path=Path(__file__),
)
