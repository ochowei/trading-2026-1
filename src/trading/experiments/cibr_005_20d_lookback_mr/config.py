"""
CIBR 20日回看窗口均值回歸配置 (CIBR 20-Day Lookback Mean Reversion Config)

基於 CIBR-002 Att3（當前最佳），結構性變更回看窗口：
- 回看窗口：10日 → 20日（捕捉更長期的回檔模式）
- 回檔門檻：4% → 6%（更寬窗口需更深門檻維持訊號品質，~3.9σ）
- WR 週期：10 → 14（匹配更長回看窗口）
- 持倉：18 → 15天（縮短到期曝露）
- 保留 ATR>1.15 + ClosePos>=40% 過濾（已驗證有效）

假說：20日回看窗口可捕捉緩慢發展的回檔，可能改善 Part A 績效（較平靜市場），
同時加深回檔門檻維持訊號品質。

跨資產參考：GLD-012（20日回看+3%，vol 1.2%）成功，
CIBR vol 1.53% 接近 GLD，20日回看有合理依據。

Att1: 20日回看+6%+WR(14)+持倉15天 → Part A 0.32/Part B 0.26，min 0.26 ★ Final
     min(A,B) 改善 +13%（0.23→0.26），Part A 大幅改善（+39%）
     Part B 有 2 筆到期交易（+0.84%, -0.09%），A/B 訊號比 2.0:1
Att2: 持倉恢復 18天 → Part A 0.18/Part B 0.40，min 0.18
     Part B 改善（到期報酬提升），但 Part A 惡化（冷卻鏈序改變引入一筆額外停損）
Att3: 回檔門檻加深至 7%（~4.6σ）+ 持倉 15天 → Part A 0.55/Part B 0.12，min 0.12
     過深門檻將 Part B 訊號減至 5 筆，A/B 失衡 2.6:1
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR20DLookbackMRConfig(ExperimentConfig):
    """CIBR 20日回看窗口均值回歸參數"""

    # 進場指標
    pullback_lookback: int = 20  # 20日回看（vs CIBR-002 的 10日）
    pullback_threshold: float = -0.06  # 回檔 >=6%（20日窗口需更深門檻，~3.9σ）
    wr_period: int = 14  # WR(14)，匹配更長回看窗口
    wr_threshold: float = -80.0  # Williams %R <= -80 (超賣)
    close_pos_threshold: float = 0.40  # 收盤位置 >= 40%（日內反轉確認）
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15  # ATR(5)/ATR(20) > 1.15
    cooldown_days: int = 8


def create_default_config() -> CIBR20DLookbackMRConfig:
    return CIBR20DLookbackMRConfig(
        name="cibr_005_20d_lookback_mr",
        experiment_id="CIBR-005",
        display_name="CIBR 20-Day Lookback Mean Reversion",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%
        holding_days=15,  # 15天（Att1: Part A 最佳）
    )
