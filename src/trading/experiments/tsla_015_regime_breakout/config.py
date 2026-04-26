"""
TSLA-015: Multi-Week Regime-Aware BB Squeeze Breakout 配置
TSLA Multi-Week Regime-Aware BB Squeeze Breakout Configuration

策略方向：將「多週期 regime 過濾」（trend regime + vol regime）疊加於 TSLA-009 Att2
BB Squeeze Breakout 之上，直接回應 TSLA-013 提出的跨資產假設：
    "breakout strategies on high-vol stocks may require regime-level filters
    (vol state, multi-week trend regime) rather than T-1/T-2 single-day filters"
（TSLA-013 三次迭代驗證 single-day 過濾器系統性失敗）

基礎（同 TSLA-009 Att2，當前最佳 min(A,B) 0.40）：
- BB(20, 2.0) + 60 日 30th 百分位擠壓 + Close > Upper BB + Close > SMA(50)
- 冷卻 10 天，TP+10%/SL-7%/20d，0.15% 滑價（高 vol 個股）

TSLA-015 新增 regime 過濾：
1. **多週期趨勢 regime**：SMA(20) > SMA(60)（確認多週上升趨勢主導）
   - 預期過濾：2019-2020 chop 早期假突破、2022 bear market false breakouts、
     2023 chop 中段反彈
   - 預期保留：2020 COVID recovery（4-6 月趨勢 SMA 已轉正）、
     2021 bubble run-up、2024-2025 AI bull
2. **多週期波動 regime**：ATR(20) ≤ ATR(60) × 1.40（避免極端 vol 擴張期）
   - 預期過濾：2020-03 / 2022-05 / 2022-09 極端波動期（ATR(20) > 1.4×ATR(60)）
   - 保留正常 vol breakouts

================================================================================
基準：TSLA-009 Att2（已執行驗證 2026-04-26）
================================================================================
- Part A: 17 訊號, WR 58.8%, 累計 +64.01%, Sharpe 0.40
- Part B: 6 訊號, WR 66.7%, 累計 +26.25%, Sharpe 0.53
- min(A,B) 0.40, A/B cum gap 59%（>30% 目標），A/B 訊號比 2.83:1（>1.5:1 目標）

目標：Sharpe > 0.40，A/B cum gap < 30%，A/B 訊號比 < 1.5:1

================================================================================
Att1 baseline 參數
================================================================================
- 同 TSLA-009 Att2 進場 + SMA(20) > SMA(60) + ATR(20) ≤ 1.40 × ATR(60)
- TP+10% / SL-7% / 20d / cd 10d
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSLA015Config(ExperimentConfig):
    """TSLA-015 Multi-Week Regime-Aware BB Squeeze Breakout 參數"""

    # === BB Squeeze Breakout 基礎（同 TSLA-009 Att2）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10

    # === 多週期趨勢 regime 過濾 ===
    # SMA 短週期：20 日（約 4 週）
    # SMA 長週期：60 日（約 12 週）
    # 條件：SMA(short) > SMA(long)
    sma_regime_short: int = 20
    sma_regime_long: int = 60

    # === 多週期波動 regime 過濾 ===
    # 短週期 ATR：20 日
    # 長週期 ATR：60 日
    # 條件：ATR(short) ≤ ATR(long) * vol_regime_max_ratio
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.40


def create_default_config() -> TSLA015Config:
    """建立預設配置（Att1 baseline）"""
    return TSLA015Config(
        name="tsla_015_regime_breakout",
        experiment_id="TSLA-015",
        display_name="TSLA Multi-Week Regime-Aware BB Squeeze Breakout",
        tickers=["TSLA"],
        data_start="2018-01-01",
        profit_target=0.10,
        stop_loss=-0.07,
        holding_days=20,
    )
