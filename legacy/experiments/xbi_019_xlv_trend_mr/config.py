"""
XBI-019: XLV Sector Parent Trend Filter on VIX Bands MR

策略方向（cross-asset trend regime gate）：
    在 XBI-017 Att1 完整框架（min(A,B) 0.64，repo 第 1 次 lesson #24 family
    BANDS 變體）之上，新增第 7 條件：
    **XLV 過去 N 日報酬 >= min_xlv_return**
    （sector parent ETF 自身動能方向過濾，非相對強度）。

    與 XBI-018 之區分（XBI-019 vs XBI-018）：
        - XBI-018: XBI-XLV **相對強度** divergence（lesson #20 v3 family）
          → Att1/Att2/Att3 均失敗（CAP 極性錯誤、FLOOR 過度傷害 Part A）
        - XBI-019: XLV **自身動能方向**（absolute momentum direction）
          → 結構性正交：不依賴 XBI 相對 XLV 表現，而是 XLV 本身是否在
            broad healthcare sector 範圍內處於健康狀態

    XBI AI_CONTEXT 明確假設：
        「sub-sector 配對 sector parent 的 RS divergence 可能需搭配「parent
         sector trend filter」（XLV 趨勢健康時才允許 XBI MR 進場）方可繞過
         broad correction recovery 與 persistent decline 重疊問題」
    XBI-019 直接驗證此假設。

================================================================================
動機（Motivation）：XBI-017 Att1 殘餘 SL 結構分析（重新審視）
================================================================================
XBI-017 Att1 Part B 1 SL（2025-03-31，Trump healthcare-related tariff fears）：
    - 該日 ^VIX > 22（高 VIX 帶，BANDS 過 → 訊號通過）
    - 但 broad healthcare sector（XLV）同時處於明顯下跌（tariff sentiment
      使整個 healthcare sector weak）
    - 導致 XBI biotech-specific dip + healthcare-wide selloff 雙重壓力
    - dip-buy 失敗為「persistent sector-wide decline」而非「isolated MR」

對照 XBI-017 Att1 Part A 高 VIX (>22) winners（broad panic V-bounce 類）：
    - 2020-05-13 (W): VIX 35.3, COVID broad capitulation V-bounce
      → XLV 此時亦在 V-bounce（broad market 同步），XLV 10d 可能 >0
    - 2022-05-12 (W): VIX 31.8, 2022 bear V-bounce
      → XLV 此時可能仍下跌但已接近底部
    - 2024-12-19 (W): VIX 24.1, 中性高 VIX
    - 2025-05-07 (W): VIX 23.5, 中性高 VIX

**核心假說**：
    高 VIX 帶內 XBI dip-buy 訊號之 winner vs loser 區分維度為 **XLV 自身動能方向**：
        - XLV 10d return >= -X%: broad healthcare sector 仍健康／已開始反彈
          → XBI dip 為 systematic V-bounce 機會，MR 成功
        - XLV 10d return < -X%: broad healthcare sector 持續弱勢
          → XBI dip 為 sector-wide persistent decline，MR 失敗（如 2025-03-31）

    低 VIX 帶內 XBI dip-buy 訊號（biotech isolated dip）：
        - 此 regime 中 XLV 10d return 通常為小正值或小負值（broad market calm）
        - filter 應對此區間非綁定，不傷害 winners

================================================================================
迭代計畫（三次）
================================================================================
- Att1: XLV 10d return >= -3.0% （middle threshold 起點）
- Att2: XLV 10d return >= -1.5% （strict，過濾 mild XLV weakness 訊號）
- Att3: XLV 10d return >= -5.0% （lenient，只過濾 severe XLV decline）

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
- repo 首次「sector parent absolute momentum direction」過濾器於任何資產
- 與 lesson #20 v3 cross-asset divergence（相對強度）正交：本實驗為
  「sector parent 自身 absolute trend」維度
- 跨資產假設（待驗證）：sub-sector ETF（XBI/KRE/IGV/SOXX）+ sector parent
  absolute momentum direction filter 可能為獨立有效維度

成交模型：next_open_market 進場 + 0.1% 滑價 + 悲觀認定（同 XBI-017）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI019Config(ExperimentConfig):
    """XBI-019 XLV Sector Parent Trend Filter on VIX Bands MR 參數"""

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

    # === XBI-019 核心新增：XLV 自身動能方向過濾 ===
    # XLV (Health Care Select Sector SPDR) 為 broad healthcare sector parent
    # 迭代紀錄：
    #   Att1（min_xlv_return=-3.0%, FLOOR）：Part A 5/80%/1.97 / Part B 4/75%/0.36（SL 仍存）
    #     min(A,B) 0.36 REJECT — 2025-03-31 XLV 10d > -3% 過 filter，filter 移除
    #     Part A 多筆 winners（broad-panic XLV deeply down 區），方向錯誤
    #   Att2（min_xlv_return=-1.5%, FLOOR strict）：Part A 4/75%/1.71 / Part B 同 Att1
    #     min(A,B) 0.36 REJECT — 2025-03-31 XLV 10d > -1.5% 仍過，FLOOR 無 surgical
    #     selectivity，加嚴僅進一步傷害 Part A
    #   Att3（regime-conditional）：低 VIX 段沿用 XBI-017 BANDS（biotech isolated dip）；
    #     高 VIX 段加 XLV 10d <= max_xlv_return_panic（要求 XLV 已深度下跌至 panic
    #     V-bounce 預備區，過濾「VIX 高但 XLV 早期下跌」的 sector-specific
    #     persistent decline 訊號如 2025-03-31）
    xlv_ticker: str = "XLV"
    xlv_lookback: int = 10
    # FLOOR 直接過濾（Att1/Att2 試驗）
    min_xlv_return: float = -0.015
    use_xlv_trend: bool = False
    # Regime-conditional CAP（Att3 ★）
    # 高 VIX 帶內：要求 XLV 10d return <= max_xlv_return_panic
    # （broad market 已 deeply 下跌至 V-bounce 預備區）
    use_xlv_panic_gate: bool = True
    max_xlv_return_panic: float = -0.020

    cooldown_days: int = 10


def create_default_config() -> XBI019Config:
    """預設配置（Att3 ★：regime-conditional XLV gate
    - 低 VIX 帶（<= 17）沿用 XBI-017 BANDS（biotech isolated dip 不需 XLV 確認）
    - 高 VIX 帶（> 22）加 XLV 10d <= -2.0% panic V-bounce 預備條件
    """
    return XBI019Config(
        name="xbi_019_xlv_trend_mr",
        experiment_id="XBI-019",
        display_name="XBI XLV Sector Parent Trend Filter on VIX Bands MR",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.050,
        holding_days=15,
        use_xlv_trend=False,
        use_xlv_panic_gate=True,
        max_xlv_return_panic=-0.020,
    )
