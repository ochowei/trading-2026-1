"""
EEM-017: EEM-EFA Cross-Asset Relative Strength Divergence Filter on Vol-Transition MR

策略方向：在 EEM-014 Att2 框架（BB(20,2.0) 下軌 + 回檔上限 -7% + WR(10)<=-85 +
ClosePos>=40% + ATR(5)/ATR(20)>1.10 + 2DD floor <= -0.5%）之上，新增「EEM-EFA
10 日相對強度發散」過濾器（EM vs DM peer divergence regime gate），用以排除
「EM-specific 結構性疲弱」失敗模式。

跨資產脈絡（lesson #20 v3 cross-asset divergence regime gate family）：
- INDA-012 Att1：INDA-EEM 60d <= +5%（單國 EM vs 寬基 EM peer，rally exhaustion）
- EWZ-009 Att1：EWZ-EEM 10d <= +2.5pp（單國 EM vs 寬基 EM peer，rally exhaustion）
- TLT-014 Att3：TLT 20d - SPY 20d >= -4%（rate-vs-equity divergence floor）
- TSLA-017 Att3：TSLA 20d - QQQ 20d >= -0.5%（mega-cap vs sector benchmark floor）
- EWJ-006 Att2：USDJPY 10d <= +1.0%（FX direction）
- 本實驗（EEM-017）：**首次 broad EM (EEM) vs broad DM (EFA) divergence floor**
  作為 lesson #20 v3 v9 候選變體（broad-EM-vs-broad-DM 對稱類別）

核心假設：
- EEM = iShares MSCI Emerging Markets ETF（broad EM）
- EFA = iShares MSCI EAFE ETF（broad developed markets ex-US，DM peer）
- 兩者皆為非美元發達 / 新興市場 USD-denominated 寬基 ETF
- 當 EEM 大幅劣後 EFA（10 日 EEM 報酬 - EFA 報酬 << 0）時：
  - EM-specific 結構性疲弱（中國政策、貿易摩擦、EM 特定貨幣危機等）
  - 此類 EM-specific 衝擊往往持續多日，MR 訊號的反彈延續性結構性下降
- 當 EEM 與 EFA 同步下跌時：
  - 全球 risk-off 同步修正（rates / Fed / 通膨等共同因子）
  - MR 訊號的反彈延續性較高（broad capitulation rebound）

EEM-014 Att2 baseline 殘餘 SL 結構：
- 2021-07-08：DiDi ADR 監管衝擊（中國特定，EFA 無同類衝擊）→ 預期 EEM-EFA 10d 大幅負值
- 2025-11-19：美中貿易摩擦升溫（EM-specific，EFA 反應有限）→ 預期 EEM-EFA 10d 大幅負值
TPs 多在 broad market correction 中（EFA 同步下跌），EEM-EFA 10d divergence 較淺

EEM-017 過濾方向：**floor**（require EEM 10d - EFA 10d >= min_rel_diff）
- 排除「EEM 大幅劣後 EFA」的 EM-specific 結構性疲弱訊號
- 保留「EEM 與 EFA 同步下跌」的 broad capitulation 訊號

迭代設計（基於 EEM-014 baseline 5 + 4 = 9 訊號樣本量）：
- Att1（lookback=10, min_rel_diff=-3.0%）：mid threshold，先驗證 filter 大致方向
- Att2（lookback=10, min_rel_diff=-2.0%）：tighter，預期過濾更多 EM-specific SL
- Att3（lookback=10, min_rel_diff=-4.0%）：looser，robustness check

成交模型：同 EEM-014（next_open_market 進場、limit_order Day TP、
stop_market GTC SL、next_open_market 到期、滑價 0.1%、悲觀認定）

關鍵風險：
- EEM-014 baseline 訊號樣本量少（5 + 4 = 9 訊號），任何 filter 過嚴
  即可能崩壞統計顯著性
- EFA 起始日約 2001-08，數據可用性對於 2010+ 的 EEM 訊號完整覆蓋
- 若 SL 在 EEM-EFA divergence 上分布過淺（與 TPs 重疊），filter 將反向選擇
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM017Config(ExperimentConfig):
    """EEM-017 EEM-EFA Cross-Asset Divergence Filter on Vol-Transition MR 參數"""

    # === BB / 回檔 / WR / ClosePos / ATR（同 EEM-014 Att2）===
    bb_period: int = 20
    bb_std: float = 2.0

    pullback_lookback: int = 10
    pullback_cap: float = -0.07

    wr_period: int = 10
    wr_threshold: float = -85.0
    close_position_threshold: float = 0.40

    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.10

    # === 2DD floor（同 EEM-014 Att2 甜蜜點）===
    twoday_return_floor: float = -0.005

    # === EEM-EFA cross-asset divergence filter（EEM-017 核心新增）===
    # ticker：EFA = iShares MSCI EAFE（broad developed markets ex-US）
    efa_ticker: str = "EFA"
    # lookback：起步 10d 與 EWZ-009 / EWJ-006 一致
    rel_lookback: int = 5
    # filter_mode："min"（floor，require RelDiff >= min_rel_diff，過濾「EEM 大幅劣後」）|
    #              "max"（cap，require RelDiff <= max_rel_diff，過濾「EEM 未大幅劣後」）
    #
    # 迭代設計：
    # Att1 min_rel_diff=-0.030（floor -3.0%，預期過濾 EM-specific 壓力訊號）
    #   → FAIL min(A,B) 0.34 vs baseline 0.56：filter 移除 winners 多於 SLs
    #     發現：SLs 為「首日新鮮 EM 壓力」（10d divergence 尚淺），TPs 為「資本投降中後段」
    #     （10d divergence 深 EEM 劣後）→ 方向需反轉
    # Att2 max_rel_diff=-0.010（cap -1.0%，反向：require EEM 已大幅劣後 EFA）
    #   → 預期保留資本投降中後段 TPs，過濾首日新鮮壓力 SLs
    # Att3 待 Att2 結果決定：cap 進一步收緊或放寬，或改 5d/20d lookback
    filter_mode: str = "min"
    min_rel_diff: float = -0.020
    max_rel_diff: float = -0.010

    cooldown_days: int = 10


def create_default_config() -> EEM017Config:
    """建立預設配置（Att1: lookback=10d, min_rel_diff=-3.0%）"""
    return EEM017Config(
        name="eem_017_eem_efa_divergence_mr",
        experiment_id="EEM-017",
        display_name="EEM EEM-EFA Divergence-Gated Vol-Transition MR",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.030,
        holding_days=20,
    )
