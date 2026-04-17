"""
EWJ-004: Relative Strength Momentum Pullback (EWJ 相對強度動量回調)

策略理念：EWJ（日本 ETF）為發達市場單一國家 ETF，日本相對其他 DM 市場
的超額表現由 BOJ 政策分歧、日圓匯率、出口商獲利週期驅動。測試 EWT-007
成功的 RS 動量框架是否可套用至 DM 單一國家 ETF（EWT 為 EM 週期性例外）。

Cross-asset lesson #25 確認 RS 動量在 EM 單一國家 ETF（INDA/EWZ/FXI）全面失敗，
但 EWT 的半導體週期性驅動使其例外成功。EWJ 作為 DM 代表，測試 RS 框架的
適用性邊界。

參考實驗：EWT-007（RS vs EEM 成功 min 0.42），NVDA-006（RS vs SMH）。
本實驗為 EWJ 首次嘗試 RS 動量策略，使用 EFA（iShares MSCI EAFE，日本佔 ~22%）
作為參考基準，捕捉日本在發達市場（非美）中的超額表現。

Att1: EFA ref, RS>=2%, pullback 1.5-4%, TP+3.5%/SL-4.0%/20d, cd10, SMA(50)
  → Part A 0.15 (10訊號, WR 60.0%, +4.49%), Part B 0.47 (4訊號, WR 75.0%, +5.96%)
  → min(A,B) 0.15 ✗ 遠低於 EWJ-003 的 0.60。Part A 2 停損 2 到期訊號品質差

Att2: EFA ref, RS>=3%, pullback 2-5%, TP+3.5%/SL-4.0%/20d, cd10, SMA(200) 趨勢過濾
  → Part A 0.12 (5訊號, WR 60.0%, +1.97%), Part B 0.24 (3訊號, WR 66.7%, +2.37%)
  → min(A,B) 0.12 ✗ 收緊 RS+SMA(200) 進一步壓縮訊號數而非提升品質

Att3: SPY ref, RS>=3%, pullback 2-5%, TP+3.5%/SL-4.0%/20d, cd10, SMA(50)
  → Part A 0.37 (7訊號, WR 71.4%, +8.73%), Part B -0.24 (6訊號, WR 50.0%, -5.43%)
  → min(A,B) -0.24 ✗ A/B 嚴重不對稱（Part B 50% WR, 5/6 Part B 訊號集中在
  2025 年日圓急貶衝擊期，RS 反轉訊號失效）

結論：RS 動量（EWJ vs EFA/SPY）在 EWJ 上全面失敗。三次嘗試 min(A,B) 最佳
僅 0.15（Att1），遠低於 EWJ-003 的 0.60。根因：日本的相對強度由**事件驅動**
（BOJ 政策轉向、日圓套息交易解除、出口商獲利週期），而非結構性因素——
與 EWT 的半導體週期性驅動不同。確認跨資產教訓 #25 擴展至**發達市場單一國家 ETF**：
RS 動量僅適用於具有持續週期性結構優勢的資產（半導體週期 EWT、個股 TSM/NVDA），
不適用於政策/匯率驅動的單一國家 ETF（無論 DM 或 EM）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWJ004Config(ExperimentConfig):
    """EWJ-004 相對強度動量回調策略參數"""

    reference_ticker: str = "SPY"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.03  # EWJ - SPY 20日報酬差 >= 3%
    pullback_lookback: int = 5
    pullback_min: float = 0.02  # 5日高點回撤 >= 2%
    pullback_max: float = 0.05  # 5日高點回撤 <= 5%
    cooldown_days: int = 10


def create_default_config() -> EWJ004Config:
    return EWJ004Config(
        name="ewj_004_rs_momentum",
        experiment_id="EWJ-004",
        display_name="EWJ Relative Strength Momentum Pullback",
        tickers=["EWJ"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（EWJ 甜蜜點）
        stop_loss=-0.040,  # -4.0%
        holding_days=20,
    )
