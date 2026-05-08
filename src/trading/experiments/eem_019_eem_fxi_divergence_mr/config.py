"""
EEM-019: EEM-FXI Cross-Asset Divergence Filter on Vol-Transition MR

策略方向（pair-divergence as macro regime gate）：
- 在 EEM-014 Att2 完整框架（BB(20,2.0) 下軌 + 10d 回檔上限 -7% + WR(10)<=-85 +
  ClosePos>=40% + ATR(5)/ATR(20)>1.10 + 2DD floor <= -0.5%, TP+3%/SL-3%/20d/cd10）之上，
  新增 **EEM vs FXI 相對強度（N 日報酬差）上限** 作為 cross-asset
  pair-divergence regime gate。

- FXI = iShares China Large-Cap ETF（中國大型股寬基），中國權重佔 EEM ~30%
  為 EEM 最大單一國家組成。
- 假設：當 EEM 過去 N 日相對 FXI 大幅強勢（rel_Nd > 閾值），中國分量已劣後 EM
  整體，可能反映「China-specific 結構性疲弱潛伏」（未完全反映於 broad EM 訊號日
  但隔日續跌風險升高）；當 EEM 與 FXI 同步下跌或 FXI 仍強勢，訊號為「broad EM
  同步 capitulation」更可能反彈。

跨資產脈絡（lesson #20 v3 cross-asset divergence regime gate family）：
- TLT-014 Att3 ✓（TLT-SPY 20d floor -4%，rate ETF + MR 框架）
- TSLA-017 Att3 ✓（TSLA-QQQ 20d floor -0.5%，AI 個股 + BB Squeeze breakout）
- INDA-012 Att1 ✓（INDA-EEM 60d ceiling +5%，單國 EM vs 寬基 EM peer）
- EWZ-009 Att1 ✓（EWZ-EEM 10d ceiling +2.5%，單國 EM vs 寬基 EM peer）
- NVDA-021 Att2 ✓（NVDA-QQQ 20d ceiling +3%，AI mega-cap + MBPC）
- COPX-014 ✗（COPX-GLD，商品/礦業 ETF + BB Squeeze）
- USO-026 ✗（USO-XLE，commodity ETF + MR）
- EEM-017 ✗（EEM-EFA，broad-EM-vs-broad-DM 對稱 ETF anchor）
- 本實驗（EEM-019）：**首次 broad-EM-vs-single-country sub-component anchor 變體**
  （EEM 為 broad EM、FXI 為 EEM 內 ~30% 權重的 single-country 主導成分）

EEM-014 Att2 baseline 殘餘 SL 結構（從 EEM-017 / EEM-018 trade-level 文件）：
- Part A 2021-07-08：DiDi ADR 監管衝擊（中國特定，FXI 同步崩盤但深度更甚）
  → 預期 EEM_10d - FXI_10d > 0（EEM 受影響但 FXI 受影響更深）
- Part A 2021-11-30：Omicron 恐慌淺幅震盪（broad risk-off，非中國驅動）
  → 預期 EEM_10d - FXI_10d 接近 0（同步反應）— 此 SL 已被 EEM-014 2DD floor 過濾
- Part B 2025-11-19：美中貿易摩擦升溫（典型中國驅動 EM-specific）
  → 預期 EEM_10d - FXI_10d > 0（FXI 提前下跌，EEM 滯後）

EEM-014 baseline TPs（broad EM/risk-off rebound）：
- 多在 EEM 與 FXI 同步深跌期（COVID 復甦、QT 修正等），EEM_10d ≈ FXI_10d
  或 FXI 略弱於 EEM（FXI 流動性低 + 政策不確定使下跌幅度更大）
- 預期 EEM_10d - FXI_10d 廣泛分布於 [+5%, -10%] 區間（rel_diff 集中於正/中性）

EEM-019 過濾方向：**ceiling**（require EEM_Nd - FXI_Nd <= max_rel_return）
- 排除「EEM 大幅強於 FXI」的 China-specific 結構性疲弱潛伏訊號
- 保留「EEM 與 FXI 同步下跌」或「FXI 仍強於 EEM」的 broad capitulation 訊號

迭代設計（基於 EEM-014 baseline 5 + 4 = 9 訊號樣本）：
- Att1: lookback=10d, max_rel_return=+5.0%（modest baseline，先驗證 filter 方向）
- Att2: 視 Att1 結果調整 threshold（更緊或更寬）
- Att3: 進一步精煉（調整 lookback 或 threshold）

成交模型：同 EEM-014（next_open_market 進場、limit_order Day TP、stop_market GTC SL、
next_open_market 到期、滑價 0.1%、悲觀認定）

關鍵風險：
- EEM-014 baseline 訊號樣本量少（5 + 4 = 9 訊號），任何 filter 過嚴皆可能崩壞
  統計顯著性
- FXI 起始日約 2004-10，數據可用性對於 2010+ 的 EEM 訊號完整覆蓋
- Cooldown chain shift（lesson #19）：filter 過濾任何 baseline 訊號可能解除 cooldown
  鎖定釋放新訊號，可能引入新 SL（EEM-016/EEM-017 失敗主因之一）
- 若 SLs 在 EEM-FXI divergence 上分布過淺（與 TPs 重疊），filter 將反向選擇

跨資產貢獻（預期，待驗證）：
- repo 第 9 次 cross-asset divergence regime gate 應用
- repo 首次 broad-EM-vs-single-country sub-component anchor 變體
  （既有 v6 BANDS / v7 DXY / v8 USDJPY direction / v9 broad-vs-broad EFA 失敗 / EWZ-EEM 成功）
- 探索假設：若 anchor 為「target 內最大權重子集」（FXI 佔 EEM ~30%），
  divergence 維度可能反映「sub-component-specific weakness lurking」
  → 與 EWZ-EEM（broad benchmark anchor）方向結構一致但機制相反
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM019Config(ExperimentConfig):
    """EEM-019 EEM-FXI Cross-Asset Divergence Filter on Vol-Transition MR 參數"""

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

    # === EEM-FXI cross-asset divergence filter（EEM-019 核心新增）===
    # ticker：FXI = iShares China Large-Cap ETF（EEM 內 ~30% 權重的最大單一國家成分）
    fxi_ticker: str = "FXI"
    # lookback：起步 10d 與 EWZ-009（EWZ-EEM 10d 成功）一致，
    # 後續 Att 視結果調整至 5d/20d
    rel_lookback: int = 10
    # max_rel_return：require EEM_Nd - FXI_Nd <= max_rel_return（ceiling/cap 方向）
    # 排除「EEM 大幅強於 FXI」的 China-specific 結構性疲弱潛伏訊號
    #
    # 迭代設計：
    # Att1: max_rel_return=+0.05（modest baseline +5%）— 先驗證 filter 方向
    # Att2/3: 視 Att1 結果決定（收緊至 +3%/+2% 或放寬至 +7%）
    max_rel_return: float = 0.05

    cooldown_days: int = 10


def create_default_config() -> EEM019Config:
    """建立預設配置（Att1: lookback=10d, max_rel_return=+5.0%）"""
    return EEM019Config(
        name="eem_019_eem_fxi_divergence_mr",
        experiment_id="EEM-019",
        display_name="EEM EEM-FXI Divergence-Gated Vol-Transition MR",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.030,
        holding_days=20,
    )
