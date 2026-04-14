"""
FXI-003: Volatility-Adaptive Mean Reversion
(FXI 波動率自適應均值回歸)

FXI-001 回檔+WR 均值回歸 WR 僅 47%，無法區分恐慌急跌（好訊號）與慢磨下跌（壞訊號）。
FXI-002 BB Squeeze 突破在 Part A 失敗（min -0.07 < FXI-001 -0.05），中國宏觀驅動假突破過多。

本實驗保留 FXI-001 的 pullback+WR 基礎架構，加入：
1. ATR(5)/ATR(20) 波動率急升過濾——只在恐慌急跌時進場
2. ClosePos ≥ 35% 反轉確認——確保訊號日有止跌跡象

參考：
- IWM-011 (1.5-2% vol): ATR > 1.10 → min +67.7%
- COPX-007 (2.25% vol): ATR > 1.05 → min +28.6%
- FXI ~2.0% vol → ATR > 1.10（偏保守，先求品質）

Att1: 回檔≥7% + WR≤-80 + ATR>1.10 + ClosePos≥35% + TP4.0%/SL-4.5%/15天
  → Part A 0.32 (17訊號, WR 70.6%), Part B -0.07 (2訊號, WR 50.0%)
  問題：Part B 僅 2 訊號（A/B 3.4:1），ATR>1.10 過嚴過濾 2024-2025 溫和行情

Att2: 降 ATR 門檻至 1.05（匹配 COPX-007）
  → Part A 0.28 (20訊號, WR 70.0%), Part B -0.07 (2訊號, WR 50.0%)
  問題：Part B 仍僅 2 訊號，2024-2025 復甦行情中 ATR spike 極少

Att3: 移除 ATR 過濾，僅保留 ClosePos≥35%（類似 IWM-005/XBI-005 的反轉確認）
  → Part A 0.07 (31訊號, WR 58.1%), Part B 0.10 (6訊號, WR 50.0%) ★
  改善：min(A,B) 0.07 > FXI-001 -0.05，兩期均正
  A/B 累計報酬差：4.15pp，頻率比 2.07:1（可接受）

Final: 選擇 Att3（ClosePos only）— min(A,B) 0.07 且兩期均正 Sharpe
  ATR 過濾在 Part A 效果極佳但 Part B 訊號不足，ClosePos 是 A/B 平衡的最佳折衷
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI003Config(ExperimentConfig):
    """FXI-003 波動率自適應均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥7%（與 FXI-001 一致）

    # Williams %R
    wr_period: int = 10
    wr_threshold: float = -80.0

    # ATR 波動率過濾
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 0.0  # Att3: disabled (0 = no ATR filter)

    # ClosePos 反轉確認
    closepos_threshold: float = 0.35  # Close 在日內區間 35% 以上

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> FXI003Config:
    return FXI003Config(
        name="fxi_003_vol_adaptive_mr",
        experiment_id="FXI-003",
        display_name="FXI Vol-Adaptive Mean Reversion",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.040,  # +4.0%（FXI 2.0% vol 均值回歸目標）
        stop_loss=-0.045,  # -4.5%（MR 需較寬 SL 容忍回測）
        holding_days=15,
    )
