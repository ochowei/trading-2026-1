"""
FXI-011: Connor's RSI (CRSI) Mean Reversion

Tests Connor's composite oscillator on FXI to address structural A/B imbalance
of FXI-005 (Part A 26 signals/Sharpe 0.38 vs Part B 5 signals/Sharpe 1.61,
cumulative diff 62.5%, signal count diff 80.7%).

CRSI = mean of:
  (1) RSI(3) - short-term momentum
  (2) Streak_RSI(2) - RSI of consecutive up/down day streak (persistence axis)
  (3) PercentRank(1d return, 100d) - relative magnitude vs recent history

Hypothesis: streak component differentiates flush-then-bounce from continuation,
addressing FXI's policy-driven slow-melt failure mode that defeated WR(10) /
RSI(5) / Stoch / BB Lower MR. PercentRank adds historical context that tames
the 2024-2025 stimulus regime (otherwise quiet) while preserving 2019-2023
pullbacks. CRSI never tested in this repo.

Att1: CRSI <= 10 + PB 4-12% + ClosePos + ATR + cd10
  Result: Part A 6 signals (3W/3L) Sharpe 0.01 / Part B 2/2 Sharpe 4.14.
  Failure: CRSI <= 10 stacked on PB+ATR filter is over-restrictive — Part A
  retains only 23% of FXI-005's signal flow and the surviving set has 50% WR.

Att2: CRSI <= 20 + PB 4-12% + ClosePos, no ATR
  Result: Part A 16 signals 56.2% WR Sharpe 0.12 / Part B 4/4 100% WR
  Sharpe 5.36. Failure: CRSI <= 20 alone is *worse* than FXI-005's WR(10)
  for Part A — CRSI filter removed 8 wins but only 2 losses (CRSI dis-favors
  the 1-day-flush wins that FXI-005 captures via WR).

Att3 (current default): FXI-005 framework + CRSI <= 25 as additional filter
  Result: Part A 18 signals 55.6% WR Sharpe 0.17 / Part B 3/3 100% WR
  Sharpe 4.74. Failure: CRSI as additional filter REMOVED MORE WINNERS THAN
  LOSERS in Part A (Part A signals 26→18 = 31% reduction; wins 17→10 = 41%
  reduction). The structural reason: FXI's profitable mean reversion signals
  are sharp 1-2 day flushes (high CRSI because RSI(3) momentum spikes back
  fast and streak length is only -1 or -2); slow-melt continuations have
  low CRSI but FXI-005's WR(10)+ATR already filters most of them. CRSI
  thus dis-favors exactly the signal type FXI rewards.

**Verdict: 3 iterations all failed vs FXI-005 min(A,B) 0.38.**
**Cross-asset lesson**: CRSI as standalone or additional filter on policy-
driven single-country EM ETFs penalizes single-day flush signals (the very
signals MR rewards). Adds 6th failed strategy type to FXI list (after BB
Squeeze, RSI(5), BB Lower MR, RS momentum, Stoch, Failed Breakdown,
Gap-Down Capitulation, NR7 — actually 9th now). FXI-005 remains global
optimum (10→11 experiments, 30+ attempts).
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI011Config(ExperimentConfig):
    """FXI-011 Connor's RSI mean reversion parameters"""

    # Pullback parameters (FXI-005 framework: PB 5-12%)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.05  # 10d high pullback >= 5%
    pullback_cap: float = -0.12  # Cap at 12% (FXI crash isolation)

    # Williams %R primary oversold (FXI-005 sweet spot)
    wr_period: int = 10
    wr_threshold: float = -80.0

    # Connor's RSI parameters (additional persistence filter)
    crsi_rsi_period: int = 3
    crsi_streak_period: int = 2
    crsi_rank_period: int = 100
    crsi_threshold: float = 25.0  # CRSI <= 25 (loose, additional filter only)

    # Close position filter (intraday reversal confirmation)
    close_position_threshold: float = 0.4

    # ATR volatility filter (FXI-005 sweet spot)
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05

    # Cooldown
    cooldown_days: int = 10


def create_default_config() -> FXI011Config:
    return FXI011Config(
        name="fxi_011_connors_rsi_mr",
        experiment_id="FXI-011",
        display_name="FXI Connor's RSI Mean Reversion",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.055,  # FXI-005 sweet spot
        stop_loss=-0.050,
        holding_days=20,
    )
