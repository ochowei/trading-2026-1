"""
CIBR-004 Att2: 動量強化均值回歸配置 (Momentum-Enhanced Mean Reversion)

Att1 (RSI(2) 框架) 失敗分析：
- Part A Sharpe -0.19, Part B 1.44 → RSI(2) 在板塊 ETF 上嚴重市場狀態依賴
- 5/9 Part A 訊號在持續性熊市中觸發停損（COVID、2021-2022 科技股拋售）
- 確認 cross-asset lesson #27 擴展到美國板塊 ETF（不僅限非美國 ETF）

Att2 策略轉向：
在 CIBR-002 已驗證的 pullback+WR 框架上，加入 2日急跌過濾以提升訊號品質。
- 2日急跌 <= -1.5% 作為短期動量崩潰確認（確保捕捉急跌恐慌而非慢磨下跌）
- TP 提高至 +4.0%（非對稱出場，CIBR-002 的 +3.5% 可能壓縮贏利空間）
- 持倉縮短至 15天（減少到期虧損曝露，參考 EWT-006/INDA-005 成功案例）

設計邏輯：
- 回檔 >= 4%：沿用 CIBR-002 的 2.6σ 門檻
- WR(10) <= -80：跨資產通用超賣指標
- ClosePos >= 40%：日內反轉確認
- ATR(5)/ATR(20) > 1.15：CIBR-002 已驗證
- 2日跌幅 <= -1.5%：新增動量崩潰確認（1.0σ 相對 CIBR 1.53% vol）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR004Config(ExperimentConfig):
    """CIBR-004 Att2 動量強化均值回歸參數"""

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
    decline_threshold: float = -0.015  # 2日跌幅 >= 1.5%

    cooldown_days: int = 8


def create_default_config() -> CIBR004Config:
    return CIBR004Config(
        name="cibr_004_rsi2_vol_adaptive",
        experiment_id="CIBR-004",
        display_name="CIBR Momentum-Enhanced Mean Reversion",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.04,  # +4.0%（非對稱出場，vs CIBR-002 的 +3.5%）
        stop_loss=-0.04,  # -4.0%
        holding_days=15,  # 15天（vs CIBR-002 的 18天）
    )
