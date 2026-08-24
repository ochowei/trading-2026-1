"""
CIBR-004 Att3: 動量強化均值回歸配置 (Momentum-Enhanced Mean Reversion)

Att1 (RSI(2) 框架) 失敗：Part A -0.19, Part B 1.44 → RSI(2) 在板塊 ETF 嚴重市場狀態依賴
Att2 (pullback+WR + 2d-decline -1.5% + TP 4.0% + 15d) 失敗：
  - TP +4.0% 反效果：3 筆交易從達標變為到期（+2.77%, +3.59%, +2.81%）
  - 2日跌幅 -1.5% 非綁定：16 訊號數與 CIBR-002 相同

Att3 調整：
1. 2日跌幅門檻加嚴至 -2.0%（1.3σ，真正過濾非恐慌訊號）
2. TP 回歸 +3.5%（CIBR-002 已驗證，+4.0% 反效果）
3. SL 放寬至 -4.5%（給予更多呼吸空間，部分停損交易可能恢復）
4. 持倉 18天（CIBR-002 已驗證，15天轉贏為到期）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR004Config(ExperimentConfig):
    """CIBR-004 Att3 動量強化均值回歸參數"""

    # 進場條件：回檔+WR（沿用 CIBR-002）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.04  # 回檔 >= 4%

    wr_period: int = 10
    wr_threshold: float = -80.0  # WR <= -80

    close_pos_threshold: float = 0.40  # ClosePos >= 40%

    # 波動率過濾（沿用 CIBR-002）
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15

    # 2日急跌過濾（新增）
    decline_lookback: int = 2
    decline_threshold: float = -0.02  # 2日跌幅 >= 2.0%

    cooldown_days: int = 8


def create_default_config() -> CIBR004Config:
    return CIBR004Config(
        name="cibr_004_rsi2_vol_adaptive",
        experiment_id="CIBR-004",
        display_name="CIBR Momentum-Enhanced Mean Reversion",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,  # +3.5%（回歸 CIBR-002 驗證值）
        stop_loss=-0.045,  # -4.5%（放寬 SL，給予恢復空間）
        holding_days=18,  # 18天（回歸 CIBR-002 驗證值）
    )
