"""
XBI-018: XBI-XLV Cross-Asset Divergence Filter on VIX Bands MR

策略方向（cross-asset divergence regime gate, lesson #20 v3 family）：
    在 XBI-017 Att1 完整框架（min(A,B) 0.64，repo 第 1 次 lesson #24 family
    BANDS 變體）之上，新增第 7 條件：
    **XBI 過去 N 日報酬 - XLV 過去 N 日報酬 <= max_rs_excess**
    （XBI-XLV N 日相對強度上限 cap）。

    **Repo 第 1 次 lesson #20 v3 cross-asset divergence regime gate 應用於 XBI**
    ——既往 lesson #20 v3 跨資產驗證涵蓋 EWZ/INDA/EWT/NVDA/TLT/COPX/USO，但
    XBI sub-sector vs sector parent (XLV) 配對為 repo 首次嘗試。

================================================================================
動機（Motivation）：XBI-017 Att1 殘餘 SL 結構分析
================================================================================
XBI-017 Att1 經 ^VIX BANDS 過濾後仍存留：
- Part A: 1 SL（VIX 落於極端帶 < 17 或 > 22，VIX BANDS 無法捕捉）
- Part B: 1 SL（同上，VIX BANDS 無法捕捉）

兩筆 SL 的 ^VIX dimension 已被 XBI-017 過濾（複數 winners 仍位於極端帶內），
故 ^VIX 不再是有效的 surgical separator。需要正交維度——cross-asset divergence
為 repo 多資產驗證之有效正交維度（lesson #20 v3）。

**結構性假設（XBI-XLV 配對）**：
    XBI（small/mid-cap biotech）vs XLV（broad healthcare 大盤股 + 設備 + 服務 +
    pharma + 部分 biotech）：
    - 當 XBI 過去 N 日相對 XLV 強勢（rs > 閾值，sub-sector 跑贏 sector parent），
      訊號日的 capitulation 訊號更可能為「XBI sub-sector rally exhaustion 中段」
      而非「XBI 隔離型 dip」；filter 過濾此類訊號可移除 rally-exhaustion 失敗模式
    - 當 XBI 相對 XLV 持平或弱勢（rs <= 閾值），dip 為 sub-sector 同步調整或
      XBI-specific 相對弱勢的反彈機會（healthcare sector 仍健康提供支撐）

**跨資產類比（既往 cross-asset divergence 成功模式）**：
| 資產 (target)  | Anchor   | Lookback | RS direction | Threshold      |
|----------------|----------|----------|--------------|----------------|
| INDA-012       | EEM      | 60d      | CAP <=       | +5.0%          |
| EWZ-009        | EEM      | 10d      | CAP <=       | +2.5pp         |
| NVDA-021       | QQQ      | 20d      | CAP <=       | +3.0%          |
| EWT-010        | EEM      | 20d+60d  | CAP <= AND   | +3.0pp + 5.0pp |
| TLT-014        | SPY      | 20d      | (varied)     | (varied)       |
| TSLA-017       | QQQ      | 20d      | (varied)     | (varied)       |
| **XBI-018** ★  | **XLV**  | 20d/60d  | CAP <=       | **+3.0% TBD**  |

XBI vs XLV 結構性類比 NVDA vs QQQ（sub-component vs broader index）：
- NVDA 在 QQQ 內為單一 high-vol 個股；NVDA-QQQ rally exhaustion = 個股漲多 vs 大盤
- XBI 在 XLV 內為 small-cap biotech 子類；XBI-XLV rally exhaustion = 子類漲多 vs 父類

================================================================================
迭代計畫（三次）
================================================================================
- Att1: rs_lookback=20, max_rs_excess=+3% （NVDA-021 直接移植 sub-component 維度）
- Att2: rs_lookback=60, max_rs_excess=+5% （INDA-012 中長期 lookback 維度）
- Att3: 雙 lookback AND combination 20d <= +3% AND 60d <= +5% （EWT-010 直接移植）

================================================================================
基準對照（XBI-017 Att1 ★ 2026-05-04 全域最優）
================================================================================
- Part A: 11 訊號, WR 90.9%, 累計 +41.00%, Sharpe 3.12, MDD -4.62%
- Part B:  6 訊號, WR 83.3%, 累計 +12.71%, Sharpe 0.64
- min(A,B) 0.64
- A/B 年化 cum 7.10%/yr vs 6.16%/yr（gap 13.2%）
- A/B 年化訊號比 2.2:3.0/yr（gap 26.7%）

驗收目標：min(A,B) > 0.64（XBI 全域最優突破），維持 A/B 平衡
（年化 cum diff < 30%、訊號比 gap < 50%）。

================================================================================
跨資產貢獻（預期）
================================================================================
- repo 首次 lesson #20 v3 cross-asset divergence regime gate 應用於 XBI
- repo 首次 sub-sector ETF (XBI) vs sector parent ETF (XLV) 配對
- 擴展 lesson #20 v3 family v3：sector-level sub/parent 配對維度
  （既有為 country-EM、stock-index、commodity-commodity 配對）
- 完整 lesson family 三維正交應用於 XBI：
    - lesson #22 vol-stability gate (XBI-015)
    - lesson #24 implied-vol BANDS (XBI-017)
    - lesson #20 v3 cross-asset divergence (XBI-018)

成交模型：next_open_market 進場 + 0.1% 滑價 + 悲觀認定（同 XBI-017）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI018Config(ExperimentConfig):
    """XBI-018 XBI-XLV Cross-Asset Divergence Filter on VIX Bands MR 參數"""

    # === 進場指標（同 XBI-017 / XBI-015 Att2）===
    pullback_lookback: int = 10
    pullback_threshold: float = -0.08
    pullback_upper: float = -0.20
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.35

    # === 多週期波動 regime gate（同 XBI-015 Att2 / XBI-017）===
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.10
    use_vol_regime: bool = True

    # === ^VIX BANDS regime gate（同 XBI-017 Att1）===
    vix_ticker: str = "^VIX"
    vix_low_threshold: float = 17.0
    vix_high_threshold: float = 22.0
    use_vix_bands: bool = True

    # === XBI-018 核心新增：XBI-XLV cross-asset divergence cap ===
    # XLV (Health Care Select Sector SPDR) 為 broad healthcare sector parent
    xlv_ticker: str = "XLV"
    # 短 lookback（NVDA-021 移植維度）
    rs_lookback_short: int = 20
    max_rs_excess_short: float = 0.03  # 20d: XBI - XLV <= +3%
    # 長 lookback（INDA-012 移植維度，Att2/Att3 啟用）
    rs_lookback_long: int = 60
    max_rs_excess_long: float = 0.05  # 60d: XBI - XLV <= +5%
    # 維度開關：
    #   Att1（REJECT min 0.52）：use_short=True,  use_long=False
    #     20d/+3% NVDA-021 港，過濾 winners 但 1 Part B SL 殘留
    #   Att2：use_short=False, use_long=True
    #     60d/+5% INDA-012 港，測試中長期 outperformance 維度
    #   Att3：use_short=True,  use_long=True  （AND combo, EWT-010 移植）
    use_rs_short: bool = False
    use_rs_long: bool = True

    cooldown_days: int = 10


def create_default_config() -> XBI018Config:
    """預設配置（Att1：20d lookback, max_rs_excess +3%, 移植 NVDA-021 維度）"""
    return XBI018Config(
        name="xbi_018_xbi_xlv_divergence_mr",
        experiment_id="XBI-018",
        display_name="XBI XBI-XLV Cross-Asset Divergence Filter on VIX Bands MR",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.050,
        holding_days=15,
    )
