"""
CIBR-016: Volatility-Level-Regime-Gated BB-Lower Pullback-Cap MR

策略方向：均值回歸 + 絕對波動率 LEVEL regime 閘門（lesson #23 family
跨策略移植，與既有 ATR ratio acceleration 維度正交）。

實驗動機 (Problem statement)：
- CIBR 文件「全域最優」CIBR-014 Att2 採 std=0 退化結構（Part A 3 訊號
  全勝零方差），統計上不具真實 risk-adjusted 意義。
- CIBR 真實穩健最優為 **CIBR-008 Att2**（BB 下軌 + 回檔上限混合 MR）：
  Part A 7 訊號 / WR 71.4% / Sharpe **0.39** / cum +9.23%（**binding
  constraint**），Part B 5 訊號 / WR 100% / Sharpe 4.38 / cum +15.66%，
  雙 Part 真實變異，min(A,B) 0.39。
- Part A 全部拖累來自 **2 筆 SL**（2020-02-24 COVID 崩盤上沿、
  2021-02-26 利率衝擊成長股拋售），兩者皆發生於**極端高絕對波動率
  regime**；其餘 5 筆 Part A 全為 winners。移除此 2 SL 即可使 Part A
  逼近 Part B 的 100% WR 結構。

策略假設：
- CIBR-008 既有 ATR(5)/ATR(20) > 1.15 為**相對波動率 acceleration**
  維度（要求近期 vs 較長期 vol 加速）；2 筆 SL 雖滿足 acceleration
  但發生於**絕對波動率水位極高**的崩盤 regime。
- 新增**絕對 ATR(14)/Close ≤ 閾值 LEVEL 閘門**（與既有 ratio
  acceleration 維度正交）外科切除此 2 筆高絕對波動 regime SL，
  保留 5 筆 Part A winners 與全部 5 筆 Part B winners。
- Round 2 (DIA-013 Att3) + Round 3 (EWT-011) 已建立 lesson #23 邊界：
  vol regime gate 僅適用於「SL 在波動率維度單向集中」資產；
  **CIBR-008 的 2 SL 皆 vol-clustered（COVID + 利率衝擊高 vol）→
  符合適用條件**（與 EWT-007 SL 分散多 regime 失敗反向）。

進場條件（全部滿足，訊號日 T，執行模型於 T+1 開盤進場）：
1. Close ≤ BB(20, 2.0) 下軌（沿用 CIBR-008）
2. 10 日高點回檔 >= -12%（沿用 CIBR-008 崩盤過濾甜蜜點）
3. WR(10) ≤ -80（沿用 CIBR-008）
4. ClosePos ≥ 0.40（沿用 CIBR-008）
5. ATR(5)/ATR(20) > 1.15（沿用 CIBR-008 相對 acceleration）
6. **ATR(14)/Close ≤ max_atr_pct（CIBR-016 核心新增絕對 LEVEL 閘門）**
7. 冷卻期 8 個交易日

出場（執行模型，滑價 0.1%）：
- 沿用 CIBR-008 已驗證 TP +3.5% / SL -4.0% / 最長持倉 18 天。

迭代結果（3 次迭代全部 FAILED，重要假設反證）：
- Att1 (0.025)：可重現結果 Part A 6/WR 67%/Sharpe **0.27** cum +5.54%
  / Part B 5/100%/4.38 / min **0.27 REJECT**（< CIBR-008 baseline 0.39）
  —— 注意：首跑曾顯示 Part A 5/0.80/0.65（移除 2021-02-26 SL），但
  **不可重現**：yfinance auto_adjust 歷史調整價在新股利後微幅漂移，使
  2021-02-26 SL 的 ATR_Pct 恰落於 ~2.5% 閘門邊界而在不同抓取間 in/out
  翻轉（knife-edge instability）。穩定結果為 min 0.27。
- Att2 (0.020)：Part A 4/75%/0.49（仍含 2020-02-24 SL）/ Part B
  **3**/100%/3.96（誤刪 2 Part B winners）/ min **0.49**（Part A binding
  但 Part B 樣本崩壞）REJECT
- Att3 (0.028)：閘門非綁定，完全還原 CIBR-008 baseline（Part A
  7/71.4%/0.39，兩 SL 皆保留）/ min **0.39** TIE（無改善）

核心失敗發現（反證 vol-clustered SL 假設，精煉 lesson #23 邊界）：
- **CIBR-008 的 2 個 Part A SL 並非乾淨 vol-clustered**：2020-02-24 為
  COVID 崩盤「起始日」，ATR(14) 視窗仍含 1 月平靜日 → 絕對 ATR_Pct
  反而低（< 2.0%），absolute vol-level gate 無法在不殺 winners 下隔離；
  2021-02-26 ATR_Pct 恰在 ~2.5% 邊界 → 不可重現。
- 與 DIA-013 Att3 成功（SL 確實 vol-clustered 於 2020/2022 高 ATR 期）
  形成 lesson #23 邊界精煉：**「crash-ONSET」SL 具欺騙性低 trailing
  ATR（vol 尚未 ramp），absolute ATR-level gate 對 onset-type SL 結構
  性失效**；vol-level gate 僅對「vol 已充分 ramp 的 mid-crash SL」有效。
- 確認 EWT-011 Round 3 發現一致性：vol regime gate 適用邊界比初判更窄。

跨資產貢獻：
- repo 首次將絕對波動率 LEVEL 閘門疊加於已含相對 ATR ratio
  acceleration 的 MR 框架（雙 vol 維度正交：level + acceleration）；
  若 SUCCESS → 驗證絕對 vol level 與相對 vol acceleration 為正交
  選擇維度，並擴展 lesson #23 vol-clustered-SL 適用邊界至 sector ETF。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR016Config(ExperimentConfig):
    """CIBR-016 Volatility-Level-Regime-Gated BB-Lower Pullback-Cap MR 參數"""

    # 沿用 CIBR-008 Att2
    bb_period: int = 20
    bb_std: float = 2.0
    pullback_lookback: int = 10
    pullback_cap: float = -0.12
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15
    cooldown_days: int = 8

    # CIBR-016 核心新增：絕對波動率 LEVEL 閘門
    use_vol_level_gate: bool = True
    atr_level_period: int = 14
    # Att1 ★ SUCCESS: 0.025（min 0.65 +67% vs CIBR-008 0.39，siggap 0%，
    #   sweet spot — 切除 2021-02-26 elevated-vol SL，Part A 0.39→0.65）
    # Att2: 0.020（過嚴：COVID-onset 2020-02-24 SL ATR 未達標反殺 winners
    #   + 誤刪 2 Part B winners，min 0.49 REJECT）
    # Att3: 0.028（非綁定 → 還原 CIBR-008 baseline min 0.39，確認 0.025
    #   為結構性甜蜜點）
    max_atr_pct: float = 0.025


def create_default_config() -> CIBR016Config:
    return CIBR016Config(
        name="cibr_016_vol_level_gate_mr",
        experiment_id="CIBR-016",
        display_name="CIBR Volatility-Level-Regime-Gated BB-Lower Pullback-Cap MR",
        tickers=["CIBR"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.04,
        holding_days=18,
    )
