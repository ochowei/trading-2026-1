"""
CIBR BB 下軌均值回歸配置 (CIBR BB Lower Band Mean Reversion Config)

不同於 CIBR-003 的 BB Squeeze Breakout（買在上軌突破），本實驗在 BB 下軌
觸及時買入（均值回歸方向）。相較於 CIBR-002 的固定回檔門檻，BB 下軌是
統計自適應門檻——根據近期波動度自動調整進場深度。

核心假說：BB(20,2.0) 下軌在 1.53% 日波動的 CIBR 上可能優於固定 4% 回檔，
因為低波動期需要更淺門檻、高波動期需要更深門檻，BB 自動適應這個差異。

SIVR-013 在 2-3% vol 上測試 BB 下軌失敗（熊市反覆觸及），但 CIBR 1.53% vol
遠低於 SIVR，且搭配 ATR>1.15+ClosePos 品質過濾應可抑制持續性熊市假訊號。

Att1: BB(20,2.0) 下軌 + WR(10)≤-80 + ClosePos≥40% + ATR>1.15
      → Part A 0.27/Part B 4.38, min 0.27 (+17% vs CIBR-002)
Att2: BB(20,1.5) 較寬下軌 → 品質稀釋（+訊號含停損），撤回
Att3: 移除 ClosePos 過濾 → Part A 0.09/Part B 0.02（品質崩壞，15訊號含5停損），
      確認 ClosePos 在 BB 框架中不可或缺。最終保留 Att1 配置。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBRBBLowerMRConfig(ExperimentConfig):
    """CIBR BB 下軌均值回歸參數"""

    # BB 參數
    bb_period: int = 20
    bb_std: float = 2.0

    # 品質過濾
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15

    cooldown_days: int = 8


def create_default_config() -> CIBRBBLowerMRConfig:
    return CIBRBBLowerMRConfig(
        name="cibr_007_bb_lower_mr",
        experiment_id="CIBR-007",
        display_name="CIBR BB Lower Band Mean Reversion",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%
        holding_days=18,
    )
