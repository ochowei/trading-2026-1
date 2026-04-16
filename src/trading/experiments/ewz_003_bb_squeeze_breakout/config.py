"""
EWZ-003: BB Squeeze Breakout → Acute Panic Reversal (策略轉向)
(EWZ 布林帶擠壓突破 → 急跌恐慌反轉)

Att1: BB(20,2.0) + 30th pct squeeze + SMA(50) + TP+4.5%/SL-4.0%/20天 + cooldown 12
  → Part A Sharpe 0.03 (WR 50%, 16訊號), Part B Sharpe -0.69 (WR 20%, 5訊號)
  → 失敗：EWZ 突破後頻繁反轉，Part A 8 停損 vs 7 達標

Att2: 25th pct squeeze + TP+3.5%/SL-5.0%/20天 + cooldown 15
  → Part A Sharpe -0.04 (WR 57.1%, 14訊號), Part B Sharpe -0.39 (WR 40%, 5訊號)
  → 仍失敗：寬 SL 讓更多交易存活但虧損更大，TP 降低壓縮利潤

結論：BB Squeeze Breakout 不適合 EWZ。巴西 ETF 的突破受宏觀事件驅動，
持續性不足。策略轉向均值回歸的 2 日急跌恐慌反轉。

Att3（策略轉向）: 2日急跌 ≤ -3.5% + WR(10)≤-70 + ClosePos≥35% + ATR>1.1
  + TP+5%/SL-4%/15天 + cooldown 10天
  → Part A Sharpe 0.02 (WR 46.2%, 13訊號, 累計 -0.03%), Part B Sharpe 2.35 (WR 100%, 4訊號)
  → 失敗：Part A WR 僅 46.2%（6勝7負），2日急跌在延長下跌趨勢中（COVID、升息）
    捕捉到不會反轉的恐慌，Part B 表現好但樣本太小（4筆）且 A/B 嚴重不平衡

整體結論：EWZ-003 三次迭代均未超越 EWZ-002 Att3（min Sharpe 0.34）。
- BB Squeeze 突破不適合 EWZ（宏觀事件驅動的突破無法持續）
- 2日急跌不如 10日高點回檔+WR(10)≤-80 精確（過多假訊號）
- EWZ-002 的 pullback+WR+ATR+ClosePos+非對稱出場 仍為最佳框架
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWZ003Config(ExperimentConfig):
    """EWZ-003 急跌恐慌反轉參數"""

    # 2日急跌
    decline_2d_threshold: float = -0.035  # 2日累計跌幅 ≤ -3.5%

    # Williams %R（放寬門檻，2日急跌是主要過濾）
    wr_period: int = 10
    wr_threshold: float = -70.0  # WR(10) ≤ -70

    # 收盤位置過濾（日內反轉確認）
    close_position_threshold: float = 0.35

    # 波動率自適應過濾器
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.1  # ATR(5)/ATR(20) > 1.1

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> EWZ003Config:
    return EWZ003Config(
        name="ewz_003_bb_squeeze_breakout",
        experiment_id="EWZ-003",
        display_name="EWZ Acute Panic Reversal",
        tickers=["EWZ"],
        data_start="2010-01-01",
        profit_target=0.050,  # +5.0%（反彈動能充足，同 EWZ-002）
        stop_loss=-0.040,  # -4.0%
        holding_days=15,  # 急跌反彈較快，縮短持倉
    )
