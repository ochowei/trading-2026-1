"""
FXI-008: Stochastic Oscillator %K/%D Crossover Mean Reversion

New strategy direction: replace WR(10) level-only oversold confirmation with
Stochastic Oscillator %K/%D crossover (true reversal confirmation).

Motivation: FXI-005 Att3 has Part A/B signal imbalance 26:5 (5.2:1, exceeds
the 3:1 danger threshold per cross_asset_lesson #8). Part A (2019-2023 China
bear) produces many low-quality signals; Part B (2024-2025 stimulus rally)
produces fewer high-quality signals. WR ≤ -80 is a level indicator that fires
repeatedly during continuous declines. Stochastic %K > %D requires short-term
momentum to actually turn up, which should filter out "still falling" signals.

Stochastic is NOT currently used in the repo — this explores a genuinely
under-utilized indicator direction (classic mean-reversion oscillator).

Att1: %K(14,3) <= 25 AND %K > %D (bullish cross in oversold zone)
      + pullback 5-12% + ClosePos >= 40% + ATR > 1.05 + cd10
      Exit: TP +5.5%, SL -5.0%, 20d hold
      RESULT: Part A Sharpe 0.16 (15 sig, 60% WR), Part B 4.22 (3 sig, 100% WR).
      min(A,B) 0.16 (WORSE vs FXI-005's 0.38). %K>%D crossover is too late —
      the bounce has already completed by the time it triggers. Part A quality
      drops (WR 60% vs 65.4%, avg ret 0.82% vs 2.11%) and Part B shrinks 5->3.

Att2: Replace WR(10)<=-80 with Stoch %K(14,3) <= 20 (slightly stricter
      level-based oversold, no crossover requirement). Tests whether the
      smoothed %K is a better oversold indicator than WR(10).
      RESULT: Part A Sharpe 0.34 (22 sig, 63.6% WR), Part B 1.49 (4 sig,
      75% WR). min(A,B) 0.34 (CLOSE but below FXI-005's 0.38). Stoch %K(14,3)
      removes 4 Part A signals vs WR(10), doesn't raise per-trade quality
      enough. A/B ratio still ~5.5:1.

Att3: Dual oscillator confirmation — WR(10)<=-80 AND Stoch %K(14,3)<=20.
      Short-term (10-period raw) + medium-term smoothed (14,3) oversold
      agreement. Keeps FXI-005's ClosePos/ATR/cooldown/exit.
      RESULT: Part A Sharpe 0.37 (20 sig, 65% WR), Part B 1.49 (4 sig,
      75% WR). min(A,B) 0.37 — best of the three iterations but still
      -0.01 short of FXI-005's 0.38. Dual oscillator removes 6 Part A
      signals vs FXI-005 (26->20) but also trims 1 Part B signal.
      Per-signal quality improves slightly (avg ret 1.77% vs FXI-005's
      2.11%), not enough to compensate for signal loss.

Final conclusion: all three iterations fail to beat FXI-005. Stochastic
Oscillator direction explored — confirms for FXI that (a) %K>%D crossover
is too late (price already bounced), (b) Stoch %K level alone is weakly
redundant with WR(10), (c) dual-oscillator intersection yields marginal
quality gain that doesn't overcome signal-count loss. FXI-005 remains
global-optimum. A/B signal imbalance (~5:1) is structural — driven by
2019-2023 China bear market producing many pullbacks vs 2024-2025
stimulus rally producing few, not fixable via oscillator-type changes.
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI008Config(ExperimentConfig):
    """FXI-008 Stochastic %K/%D crossover mean reversion parameters"""

    # Pullback (same as FXI-005 Att3)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.05
    pullback_cap: float = -0.12

    # Williams %R (retained for dual-oscillator confirmation in Att3)
    wr_period: int = 10
    wr_threshold: float = -80.0

    # Stochastic Oscillator %K(14,3) with %D(3) smoothing
    stoch_k_period: int = 14
    stoch_k_smooth: int = 3
    stoch_d_period: int = 3
    stoch_k_threshold: float = 20.0  # Oversold zone

    # Close position reversal confirmation (retained from FXI-005)
    close_position_threshold: float = 0.4

    # ATR volatility spike filter (retained from FXI-005)
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05

    cooldown_days: int = 10


def create_default_config() -> FXI008Config:
    return FXI008Config(
        name="fxi_008_stochastic_mr",
        experiment_id="FXI-008",
        display_name="FXI Stochastic %K/%D Crossover MR",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.055,
        stop_loss=-0.050,
        holding_days=20,
    )
