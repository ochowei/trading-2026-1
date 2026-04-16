"""
CIBR-006: Cybersecurity Sector RS Momentum Pullback 配置

網路安全板塊相對強度動量策略：在 CIBR 相對 SPY 顯示強勢時，買入 CIBR 短期回調。
靈感來源：SOXL-010（板塊 RS 動量回調，min 0.70）、EWT-007（RS 動量 EWT vs EEM，min 0.42）

CIBR 特性：
- 日波動約 1.53%（非槓桿 ETF），vs SOXL ~5%（3x 槓桿）
- 網路安全板塊 ETF，追蹤 PANW/CRWD/FTNT/ZS 等
- 與 QQQ 高度相關（同為 NASDAQ 科技），改用 SPY 以增大 RS 差異

Att1: CIBR vs QQQ, RS>=3%, 5d pullback 3-8%, SMA(50)
  → Part A 5 訊號, Sharpe -0.85 / Part B 0 訊號
  失敗原因：CIBR-QQQ 相關性太高，3% RS 門檻幾乎無法觸發
Att2: 改用 SPY 基準, RS>=2%, 10d pullback 2-8%, 移除 SMA 趨勢
  → Part A 28 訊號 WR 42.9% Sharpe -0.22 / Part B 5 訊號 Sharpe -0.11
  失敗原因：無趨勢+無品質過濾，2022 熊市大量假訊號，A/B 訊號比 5.6:1
Att3: 加入 ATR>1.15+ClosePos>=40%+SMA(50)，回調最低 3%
  改進邏輯：用 CIBR-002 已驗證的品質過濾器篩選高品質 RS 動量回調訊號
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBRRSMomentumConfig(ExperimentConfig):
    """CIBR 板塊 RS 動量回調策略專屬參數"""

    # 基準標的 (Benchmark)
    benchmark_ticker: str = "SPY"

    # 相對強度參數 (Relative strength)
    relative_strength_period: int = 10
    relative_strength_min: float = 0.02  # CIBR 10d return - SPY 10d return >= 2%

    # 回調參數 (Pullback from recent high)
    pullback_lookback: int = 10
    pullback_min: float = 0.03  # 最小回調 3%（過濾噪音）
    pullback_max: float = 0.08  # 最大回調 8%

    # 品質過濾（借用 CIBR-002 驗證有效的過濾器）
    use_atr_filter: bool = True
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15  # ATR(5)/ATR(20) > 1.15
    use_closepos_filter: bool = True
    close_pos_threshold: float = 0.40  # 收盤位置 >= 40%

    # 趨勢確認 (Trend confirmation)
    use_sma_trend: bool = True
    sma_trend_period: int = 50

    # 冷卻期 (Cooldown)
    cooldown_days: int = 8

    # 成交模型 (Execution model)
    slippage_pct: float = 0.001


def create_default_config() -> CIBRRSMomentumConfig:
    return CIBRRSMomentumConfig(
        name="cibr_006_rs_momentum_pullback",
        experiment_id="CIBR-006",
        display_name="CIBR Cybersecurity Sector RS Momentum Pullback",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%
        holding_days=18,  # 18 天
    )
