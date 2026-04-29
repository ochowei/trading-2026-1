"""
IWM BB 下軌 + 回檔上限混合進場配置 (IWM-012) — 三次迭代全部失敗

動機：IWM-011 Att2（min(A,B) Sharpe 0.52）為 IWM 全域最佳，使用 RSI(2)+2DD+
ClosePos+ATR 框架。本實驗測試 BB-lower hybrid mode（cross-asset port from
EWJ-003 / VGK-007 / EWZ-006 / EWT-008 / CIBR-008 / EEM-012 successful pattern）
是否在 IWM 1.5-2% vol（位於混合模式已驗證有效邊界 [1.12%, 1.75%] 中段）上有效。

**Repo 首次將 BB-lower hybrid mode 應用至小型股寬基 ETF**（前驗證集中於非美
寬基（VGK/EWJ）、EM 寬基（EEM）、單一國家 EM（EWZ/EWT）、美國板塊（CIBR））。

========================================================================
三次迭代結果（2026-04-25，成交模型 0.1% slippage，隔日開盤市價進場）：
========================================================================

Att1（失敗）：BB(20, 2.0) + 10d cap -10% + WR(10)≤-80 + ClosePos≥0.40
              + ATR(5)/ATR(20) > 1.10 + cd 8 + TP+4%/SL-4.25%/20d
  Part A: 7 訊號 WR 57.1% Sharpe **0.23** cum +5.55%
  Part B: 3 訊號 WR 66.7% Sharpe 0.31 cum +3.46%
  min(A,B) **0.23**（-56% vs IWM-011 Att2 的 0.52）
  失敗分析：BB(20, 2.0) 在 IWM 1.5-2% vol 上需要 ~3-4% 偏離均值才觸發，
  比 IWM-011 RSI(2)+2DD ≤ -2.5% 框架嚴格。捕捉到 7 訊號（vs IWM-011 的 10），
  缺少了 5 個 IWM-011 winners（2019-10-02 / 2020-02-28 COVID / 2020-09-21 /
  2022-05-10 / 2022-09-23 — 這些是「淺超賣 + 急跌 + 反轉」的 RSI(2) 經典訊號，
  但未達到 BB(20, 2.0) 下軌深度），同時新增 2 個 winners（2020-09-11 /
  2020-10-30 — 大盤 BB 下軌觸及訊號）。SL 全部保留（-4.35% × 2 + -1.38%
  expiry × 1 = 同 IWM-011），淨效應為移除過多贏家。

Att2（失敗）：放寬 BB 至 1.5σ（參考 EWZ-006 1.75% vol 配置）
  Part A: 12 訊號 WR 58.3% Sharpe **0.20** cum +8.63%
  Part B: 6 訊號 WR 66.7% Sharpe 0.24 cum +5.01%
  min(A,B) **0.20**（更差於 Att1）
  失敗分析：BB 1.5σ 過鬆，新增 5 個 Part A 訊號中包含 3 SLs（2020-01-27
  pre-COVID -4.35%、2022-05-06 Fed pivot -4.35%、2022-12-16 仍為 winner）；
  Part B 新增 3 訊號中含 2 SLs（2025-03-11 -4.35%、2024-12-20 expiry +2.04%）。
  WR 從 Att1 的 57.1%/66.7% 下降至 58.3%/66.7%，新訊號品質低於原訊號。
  EWZ 用 1.5σ 成功是因為 EWZ 1.75% vol 較高，1.5σ 等同 IWM 2.0σ 的距離；
  IWM 1.5-2% vol 用 1.5σ 過鬆。

Att3（失敗）：回到 BB(20, 2.0) + 收緊 ClosePos≥0.50 + ATR > 1.15
  Part A: 2 訊號 WR 50% Sharpe 0.49 cum +2.56%（樣本過少）
  Part B: 3 訊號 WR 66.7% Sharpe 0.31 cum +3.46%
  min(A,B) **0.31**（樣本過稀疏，Part A 0.4/yr 統計信心不足）
  失敗分析：收緊雙重品質過濾器將 Part A 訊號從 7 縮至 2（0.4/yr），失去
  統計顯著性。雖 Sharpe 數字升至 0.49 但僅 2 個訊號（1 winner + 1 expiry），
  CIBR-008 的 ATR>1.15 + ClosePos≥0.40 配置在 IWM 上過嚴。

========================================================================
最終配置（Att3）：BB(20, 2.0) + 10d cap -10% + WR(10)≤-80 + ClosePos≥0.50
                  + ATR(5)/ATR(20) > 1.15 + cd 8 + TP+4%/SL-4.25%/20d
========================================================================

跨資產失敗根因（結構性）：
1. **訊號集差異**：IWM RSI(2)<10 + 2DD≤-2.5% 框架捕捉「淺超賣急跌反轉」，
   多數訊號未達 BB(20, 2.0) 下軌深度；BB-lower 框架捕捉「絕對深度回檔」，
   兩者訊號集**互補但不重疊**，BB-lower 集合的 WR/Sharpe 結構性低於 RSI(2)
2. **小型股動態**：IWM 為 Russell 2000 小型股寬基，個股事件驅動加總使板塊
   級 BB 下軌觸及包含過多事件雜訊（如 2020-01 pre-COVID、2022-05 Fed pivot
   恐懼期），有別於 VGK/EWJ 發達市場、EWZ/EWT 單一國家 EM、CIBR 美國板塊
   等市場結構
3. **ATR>1.10 在 IWM 與其他資產的角色不同**：IWM-011 中 ATR>1.10 過濾「慢磨
   下跌假訊號」並提升至 0.52；本實驗中 ATR>1.10 在 BB-lower 訊號集上保留所有
   原 SL（無選擇性提升）

擴展 cross-asset lesson #52 / lesson #16 邊界：
- BB-lower hybrid mode 已驗證有效：non-US developed broad（VGK/EWJ）、EM
  broad（EEM）、commodity-driven single-country EM（EWZ）、semiconductor-driven
  single-country EM（EWT）、US sector（CIBR）
- BB-lower hybrid mode 已驗證失效（vol 邊界外）：US biotech sector ETF（XBI 2.0%
  超出邊界）、India ETF（INDA 0.97% 低於邊界）
- BB-lower hybrid mode 已驗證失效（vol 邊界內但結構不適）：**US small-cap
  broad ETF（IWM 1.5-2% 在邊界內但失敗）** — 驗證 [1.12%, 1.75%] vol 為
  必要非充分條件，asset 結構（個股事件驅動加總 vs 真正寬基或集中度高的 ETF）
  亦為關鍵變項。**新邊界規則**：BB-lower hybrid 適用「結構性集中或真正寬基」
  ETF，不適用個股事件驅動加總的小型股寬基（IWM 為首例驗證資料點）

IWM 全域最優仍為 IWM-011 Att2（min 0.52）。本實驗為 cross-asset 失敗驗證，
記錄為 IWM 第 7 種失敗策略類型（前 6 種：Pullback+WR、BB Squeeze 突破、
趨勢回調 SMA、IWM/SPY 相對強度配對、回檔範圍結構過濾、深 RSI(2) 進場）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM012Config(ExperimentConfig):
    """IWM-012 BB 下軌 + 回檔上限混合進場參數"""

    # BB 參數（Att3 回到 2.0σ + 收緊 ClosePos + ATR > 1.15）
    # Att1 BB(20, 2.0) + cap -10% + ClosePos≥0.40 + ATR>1.10 → min 0.23 FAIL
    # Att2 BB(20, 1.5) + cap -10% + ClosePos≥0.40 + ATR>1.10 → min 0.20 FAIL
    # Att3 BB(20, 2.0) + cap -10% + ClosePos≥0.50 + ATR>1.15 → 收緊品質過濾
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離（10日高點回檔上限）
    pullback_lookback: int = 10
    pullback_cap: float = -0.10  # 回檔上限 10%（~5-7σ for 1.5-2% vol）

    # 品質過濾（Att3 收緊：ClosePos→0.50、ATR→1.15）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.50  # Att3 收緊（IWM-011 為 0.40）
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15  # Att3 收緊（IWM-011 為 1.10，CIBR-008 用 1.15）

    cooldown_days: int = 8


def create_default_config() -> IWM012Config:
    return IWM012Config(
        name="iwm_012_bb_lower_pullback_cap",
        experiment_id="IWM-012",
        display_name="IWM BB Lower Band + Pullback Cap Hybrid",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.04,  # +4.0%（同 IWM-011）
        stop_loss=-0.0425,  # -4.25%（同 IWM-011 甜蜜點）
        holding_days=20,
    )
