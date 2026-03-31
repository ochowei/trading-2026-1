"""
XBI-004: 回檔範圍收窄 + 長冷卻 均值回歸配置
(XBI Capped Pullback + Extended Cooldown Mean Reversion Config)

相比 XBI-001（10日回檔 8-20% + TP +3.5% / SL -5.0% / 15天 / 冷卻10天）：
- 回檔上限 15%（vs 20%）：過濾極端熊市訊號（>15% 回檔恢復率低）
- 冷卻 15天（vs 10天）：避免熊市連續進場（2021 Feb-Mar, 2022 Apr, 2023 Sep-Oct）
- 持倉 15天（同 XBI-001）：避免寬持倉使邊界交易觸及停損

三次嘗試紀錄：
- Att1: 20日回看+10-20%+TP4.0%+冷卻12 → Part A 0.02 / Part B 0.23（FAIL）
- Att2: 10日+8-15%+冷卻15+20天持倉 → Part A 0.04 / Part B 0.44（A/B 失衡）
- Att3: 同 Att2 改 15天持倉 → Part A 0.05 / Part B 0.44（A/B 失衡，最終版）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBICappedCooldownConfig(ExperimentConfig):
    """XBI 回檔範圍收窄 + 長冷卻參數"""

    # 進場指標
    pullback_lookback: int = 10
    pullback_threshold: float = -0.08  # 回檔 ≥ 8%（同 XBI-001）
    pullback_upper: float = -0.15  # 回檔上限 15%（vs 20%，過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80 (超賣)
    cooldown_days: int = 15


def create_default_config() -> XBICappedCooldownConfig:
    return XBICappedCooldownConfig(
        name="xbi_004_capped_cooldown",
        experiment_id="XBI-004",
        display_name="XBI Capped Pullback + Extended Cooldown Mean Reversion",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 XBI-001）
        stop_loss=-0.050,  # -5.0%（非對稱寬停損，維持 XBI-001）
        holding_days=15,  # 15 天（同 XBI-001）
    )
