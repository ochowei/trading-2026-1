"""
FXI-003: BB Squeeze Breakout
(FXI 布林帶擠壓突破)

FXI 前 2 個實驗均為均值回歸策略，最佳 min(A,B) Sharpe 0.33。
本實驗嘗試完全不同的策略類型：BB 擠壓突破。

設計理據：
- FXI 日波動 ~2.0%，位於 BB Squeeze 對高流動 ETF 有效的範圍（1.5-2.0%）
- 中國大型股 ETF 受政策驅動（刺激方案、監管鬆綁），波動率壓縮後常有方向性突破
- 跨資產教訓 #18 警告單一國家 EM ETF 突破可能失敗（INDA/EWT 驗證），但 FXI 未實測
- 參數參考 EEM-005 Att2 框架，按 FXI 波動度 (2.0% vs EEM 1.17%) 縮放

Att1: BB(20,2.0) + 30th pct squeeze + SMA(50) + TP5.0%/SL4.0%/15天 + cooldown 10
  → Part A -0.15 (18訊號, WR 33.3%), Part B 0.28 (10訊號, WR 60.0%)
  問題：Part A 44% SL 率，TP 5.0% 偏高（多筆 +3.68%/+4.08% 未達標），嚴重市場狀態依賴

Att2★: 降 TP 至 3.5% + 寬 SL -5.0% + 延長持倉至 20 天（轉換 expiry → TP hit）
  → Part A -0.12 (18訊號, WR 50.0%), Part B 0.14 (10訊號, WR 60.0%)
  改善 WR 33→50% 但寬 SL 增加損失，Part A 累計仍為負，min(A,B) -0.12

Att3: 收緊擠壓至 20th pct + TP 4.0%/SL -3.5%/15天 + cooldown 15
  → Part A -0.30 (17訊號, WR 29.4%), Part B 0.28 (7訊號, WR 57.1%)
  緊 SL 導致 59% SL 率，更差

結論：BB Squeeze 突破在 FXI 三次迭代均失敗，確認跨資產教訓 #18：
  單一國家 EM ETF（INDA/EWT/FXI）BB Squeeze 突破存在嚴重市場狀態依賴，
  2019-2023 中國熊市產生過多假突破。FXI-002 均值回歸 (0.33) 仍為最佳。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI003Config(ExperimentConfig):
    """FXI-003 BB 擠壓突破參數"""

    # 布林帶參數
    bb_period: int = 20
    bb_std: float = 2.0

    # 擠壓偵測
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30  # 30th percentile
    bb_squeeze_recent_days: int = 5

    # 趨勢確認
    sma_trend_period: int = 50

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> FXI003Config:
    return FXI003Config(
        name="fxi_003_bb_squeeze_breakout",
        experiment_id="FXI-003",
        display_name="FXI BB Squeeze Breakout",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（Att2★ 最佳迭代）
        stop_loss=-0.050,  # -5.0%
        holding_days=20,
    )
