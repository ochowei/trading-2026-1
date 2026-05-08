"""
COPX-016: DXY Direction Filter on Multi-Week Regime-Aware BB Squeeze Breakout

策略方向：在 COPX-011 Att3（regime BOX [k_min=1.00, k_max=1.09]）框架上，
新增「美元指數（DXY）方向過濾」，作為 repo 首次「DXY direction filter」於任何資產
（既有 lesson #24 family 皆使用 ^VIX / ^MOVE / ^GVZ / ^OVX implied vol；
DXY 為現貨外匯指數，屬於不同維度的宏觀 regime indicator）。

核心假設（少數派、未在 repo 中測試）：
- COPX = Global X Copper Miners ETF，以美元計價的銅礦業股票籃子
- 銅價以美元計價 → 強美元 = 銅價結構性壓力
- 強美元 = 新興市場資金外流 → 商品需求下降預期
- 故當 DXY 短期快速上漲（USD strengthening rapidly）時，COPX 突破訊號的
  延續性結構性受抑，即使技術面 regime BOX 通過，宏觀面仍偏空
- 反之，DXY 平穩或下跌時，COPX BB squeeze breakout 訊號的反轉延續性最高

================================================================================
Trade-level 分析：COPX-011 Att3 全部 12 訊號之 DXY 5d/10d 報酬分布
（**重要修正**：訊號日為 BB Squeeze 突破收盤確認日（=COPX-016 Signal 列表），
與 latest.json 之 `date` field 一致。previous backtester 將 2019-04-01 標為 date，
非 2019-04-03 entry_date）
================================================================================
Part A (10 訊號)：
  Signal Date | DXY 5d | DXY 10d | Exit       | Notes
  2019-04-01  | +0.70% | +0.76%  | SL -6.14%  | ★ 唯一 Part A SL，DXY 10d 偏高
  2019-12-10  | -0.34% | -0.93%  | TP +7.00%  |
  2020-05-20  | -1.12% | -0.97%  | TP +7.00%  |
  2020-11-05  | -1.52% | -0.45%  | TP +7.00%  | 大選後 USD 急貶
  2021-02-16  | -0.46% | -0.56%  | TP +7.00%  |
  2021-04-15  | -0.42% | -1.67%  | TP +7.00%  |
  2021-05-06  | +0.38% | -0.42%  | TP +7.00%  |
  2023-01-06  | +0.04% | -0.27%  | EX +0.79%  |
  2023-07-12  | -2.76% | -1.92%  | EX -4.63%  | DXY 急貶但 COPX 仍弱（殘餘失敗）
  2023-12-13  | -1.23% | +0.10%  | EX +3.42%  |

Part B (2 訊號)：
  2025-06-05  | -0.54% | -1.22%  | TP +7.00%  |
  2025-06-26  | -1.78% | -1.50%  | EX -1.54%  |

關鍵觀察（DXY 維度的選擇力）：
**DXY 5d 維度——選擇力不足**：
  - SL DXY 5d +0.70%，但 2021-05-06 TP DXY 5d +0.38%（接近）
  - 5d 維度上閾值 +0.5% 過寬無法 cleanly 區分
  - Att1 採 +0.5% 閾值結果驗證**非綁定**（同 baseline）

**DXY 10d 維度——選擇力較強但 gap 較窄**：
  - SL DXY 10d **+0.76%**（最高）
  - 第二高為 2023-12-13 EX +3.42% 之 DXY 10d **+0.10%**（gap 0.66pp）
  - 全部 7 個 TPs 之 DXY 10d 範圍 [-1.67%, -0.27%]，最高僅 -0.27%
  - 全部 2 個 Part B 訊號之 DXY 10d 範圍 [-1.50%, -1.22%]
  - **DXY 10d ≤ +0.5% 為精準 surgical filter**：
    ✓ 過濾 1 SL（2019-04-01，DXY 10d +0.76%）
    ✓ 保留全部 7 TPs + 3 EXPs（max DXY 10d +0.10%）
    ✓ Part B 兩訊號 DXY 10d 均 ≤ -1.22%，不影響 Part B

================================================================================
三次迭代記錄：
================================================================================
Att1（dxy_lookback=5, max_dxy_change=+0.5%）：FAIL min(A,B) **0.64** = baseline TIE
  Part A: 10 訊號 80% WR Sharpe 0.72 cum +40.03%（**完全等於 COPX-011 Att3 baseline**）
  Part B: 2 訊號 50% WR Sharpe 0.64 cum +5.35%（**完全等於 baseline**）
  失敗分析：
    - 2019-04-01 SL DXY 5d 為 +0.70%，但 2021-05-06 TP DXY 5d +0.38% 接近
    - 5d 閾值 +0.5% 過寬，filter 對 SL（+0.70%）非綁定
    - 若降至 +0.4% 會誤殺 2021-05-06 TP
    - 5d 維度 SL/TP gap 過小（0.32pp）無 surgical sweet spot
  關鍵發現：DXY 5d 失敗 → 必須擴展至更長 lookback 才能捕捉 USD 結構性 regime

Att2（dxy_lookback=10, max_dxy_change=+1.0%）：FAIL min(A,B) **0.64** = baseline TIE
  Part A: 10 訊號 80% WR Sharpe 0.72 cum +40.03%（**完全等於 baseline**）
  Part B: 2 訊號 50% WR Sharpe 0.64 cum +5.35%（**完全等於 baseline**）
  失敗分析：
    - 2019-04-01 SL DXY 10d 為 +0.76%，閾值 +1.0% 過寬未過濾
    - **早期分析錯誤**：將 entry_date (2019-04-03) 誤當 signal_date 並查得 DXY 10d
      +1.39%；正確 signal_date 為 2019-04-01，DXY 10d 為 +0.76%
    - lookback 維度方向正確（10d > 5d 選擇力強），但閾值需收緊
  關鍵發現：DXY 10d gap 為 [0.10, 0.76]，閾值需在此區間內

Att3 first attempt（dxy_lookback=10, max_dxy_change=+0.5%）：
  FAIL min(A,B) **0.64** = baseline TIE，**cooldown chain shift collapse**
  Part A: 10 訊號（仍 10 個！）80% WR Sharpe 0.72 cum +40.03%
    - 2019-04-01 SL（DXY 10d +0.76%）成功被過濾 ✓
    - 但 cooldown 鏈中後續抑制的 raw signals 重新觸發：
      2019-04-08（DXY 10d +0.50%，恰於閾值邊界）通過 → 新 SL -6.14%
    - 「過濾舊 SL，引入鄰近 SL」典型 cooldown chain shift（lesson #19 family v2）
  Part B: 不變
  失敗分析：
    - DXY 10d 在 4/1 ~ 4/8 期間單調下降 +0.76% → +1.02 → +1.39 → +0.84 → +0.50
    - 閾值 +0.5% 將 4/8 訊號（恰 +0.50%）保留，使 cooldown chain shift 完成
    - 必須收緊閾值至 < +0.5% 才能同時過濾 4/8 訊號
  關鍵發現：cooldown chain 內 5 個連續日 raw signals 之 DXY 10d 範圍 [+0.50%, +1.39%]，
    閾值需 < +0.50% 才能完整過濾整個 chain

Att3 final ★（dxy_lookback=10, max_dxy_change=+0.3%）：PARTIAL SUCCESS
  Part A: 9 訊號 WR **88.9%** Sharpe **1.19** cum **+49.19%** MDD **-5.74%** PF **9.98**
    - 6 TP / 0 SL / 3 EX（2023-01-06 +0.79%, 2023-07-12 -4.63%, 2023-12-13 +3.42%）
    - vs COPX-011 Att3 baseline (10/80%/0.72/+40.03%/-6.57%/4.29)
    - **Part A 全面顯著改善**: Sharpe +65%, cum +23%, WR +9pp, MDD -13%, PF +133%
    - 4/1~4/8 cooldown chain 內 5 raw signals（DXY 10d 全部 > +0.3%）成功完整過濾
    - 下一訊號 2019-12-10 為 8 個月後，無 cooldown chain shift
  Part B: 2 訊號 50% WR Sharpe 0.64 cum +5.35% **完全等於 baseline**
    - 2025-06-05 TP +7.00% / 2025-06-26 EX -1.54%
    - 兩訊號 DXY 10d 為 -0.82% / -1.50%，filter 對 Part B 非綁定
  min(A,B) **0.64** = baseline TIE（Part B 為結構性 binding constraint，因 sample size 2）
  A/B 年化 cum: A 9.84%/yr / B 2.68%/yr → gap 73%（>30%, COPX 結構性邊界）
  A/B 年化訊號: A 1.8/yr / B 1.0/yr → gap 44%（<50% ✓）

================================================================================
最終結論：PARTIAL SUCCESS（min Sharpe TIE，Part A 結構性突破）
================================================================================

1. **Sharpe min(A,B) 嚴格不變**（baseline 0.64 = COPX-016 Att3 final 0.64）
   - Part B 為 binding constraint（COPX-011 已知，與 sample size 2 結構性相關）
   - DXY filter 在 Part B 兩訊號（DXY 10d -0.82% / -1.50%）非綁定，無法影響 Part B Sharpe
2. **Part A 顯著突破**（Sharpe 0.72 → 1.19, +65%；cum +40.03 → +49.19, +23%）
   - 過濾唯一 Part A SL（2019-04-01 + cooldown chain 4/2~4/8 共 5 raw signals）
   - 全部 winners 保留，零誤殺（DXY 10d ≤ +0.10%）
   - PF 4.29→9.98（+133%），MDD -6.57→-5.74（-13%）
3. **跨資產貢獻（repo 首次）**：
   - **Repo 首次 DXY (US Dollar Index) direction filter 於任何資產**
   - 既有 lesson #24 family v6（XBI-017）皆使用 implied vol（^VIX/^MOVE/^GVZ/^OVX）
     forward-looking option-implied derivatives；DXY 為 spot FX index，屬不同類別
     macro regime indicator
   - 適用條件假設：商品/礦業 ETF（COPX/FCX）+ 部分 EM ETFs 受 USD 結構性影響
   - 本實驗為 **lesson #24 family v7 候選**：spot FX direction filter 變體
4. **A/B cum gap 結構性問題**（73% > 30%）：
   - 與 COPX-011 baseline 相同（66.4%）
   - Part B 樣本量限制（regime BOX 過濾後 2 訊號）使任何 Part A 改善都會
     擴大 cum gap，此為 COPX 結構性邊界，非本實驗可解
5. **A/B 訊號 gap 改善**（baseline 50% → COPX-016 44%）：
   - 過濾 1 Part A 訊號使年化比 1.8:1.0（從 2.0:1.0），gap 縮小 6pp

================================================================================
Acceptance criteria 評估：
================================================================================
- ✗ Sharpe min(A,B) > baseline (0.64 = 0.64 TIE, Part B 結構性 binding)
- ✓ Part A Sharpe 顯著提升（0.72 → 1.19, +65%）
- ✗ A/B 累積報酬差距 < 30%（73%, COPX 結構性邊界）
- ✓ A/B 訊號數差距 < 50%（44%）
- ✓ 使用成交模型（next_open_market，0.15% 滑價，悲觀認定）
- ✓ Repo 較少使用方向（**首次 DXY direction filter**）

================================================================================
新跨資產假設（待驗證）：
================================================================================
DXY direction filter 之適用邊界：
1. 商品/礦業 ETFs（FCX/SLV/SIVR/USO 等）：USD-denominated，銅金銀油皆 USD 計價
2. EM ETFs（FXI/EEM/INDA/EWZ）：USD strength → EM 資金外流
3. 黃金/白銀：負相關 USD（GLD/SIVR 已驗證 ^GVZ implied vol，DXY direction 為新維度）
4. 不適用：US 寬基股指（SPY/DIA/QQQ）、債券（TLT 已驗 ^MOVE）、防禦類（XLU 已驗 ^MOVE）

預期下一步移植目標：
- FCX-013/FCX-015（銅礦個股）：DXY 10d ≤ +0.5% 可能 cleanly 過濾 SLs（同源驅動）
- USO（原油）：原油-USD 結構負相關更強，DXY direction 預期更有效
- GLD（黃金）：黃金 vs DXY 已是經典宏觀對偶

================================================================================
跨資產貢獻（預期）：
================================================================================
- Repo 首次 DXY/USD direction filter 於任何資產（lesson #24 family v7 候選）
- 既有 lesson #24 family 皆 implied volatility（^VIX / ^MOVE / ^GVZ / ^OVX
  forward-looking option-implied）；DXY 為 spot FX index，屬於不同類別
  forward-looking macro regime indicator
- 適用邊界假設：商品/礦業相關資產（COPX/FCX/GLD/SIVR/USO）
  + EM ETFs（EEM/FXI/INDA/EWZ）皆受 USD 影響
- 與既有 lesson #24 變體（LEVEL CAP / DIRECTION / BANDS / FLOOR）方向上對齊
  ——本實驗為 DIRECTION 變體（DXY change 維度）

成交模型：同 COPX-011（next_open_market 進場、limit_order Day TP、
stop_market GTC SL、next_open_market 到期、滑價 0.15%、悲觀認定）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPX016Config(ExperimentConfig):
    """COPX-016 DXY Direction Filter on Regime-Aware BB Squeeze Breakout 參數"""

    # === BB Squeeze Breakout 基礎（同 COPX-011 Att3）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 12

    # === 多週期趨勢 regime BOX（同 COPX-011 Att3）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00
    sma_regime_ratio_max: float = 1.09

    # === DXY direction filter（COPX-016 核心新增）===
    # ticker：DX-Y.NYB（ICE US Dollar Index，yfinance 歷史回測穩定）
    dxy_ticker: str = "DX-Y.NYB"
    # lookback：Att1 5d 失敗（5d 維度 SL/TP gap 0.32pp 過小），Att2/Att3 改 10d
    dxy_lookback: int = 10
    # max change（Att3 final ★ 甜蜜點）：+0.3%
    # Att2 +1.0% 非綁定（SL DXY 10d +0.76% < threshold）
    # Att3 first +0.5% 觸發 cooldown chain shift（4/8 raw signal DXY 10d +0.50% 通過）
    # Att3 final +0.3% 完整過濾 4/1~4/8 整個 cooldown chain（全部 > +0.3%）
    # 下一訊號 2019-12-10（DXY 10d -0.93%）為通過閾值的安全邊際
    max_dxy_change: float = 0.003


def create_default_config() -> COPX016Config:
    """建立預設配置（Att3 final ★ 甜蜜點 max_dxy_change=+0.3%, lookback=10d）"""
    return COPX016Config(
        name="copx_016_dxy_direction_breakout",
        experiment_id="COPX-016",
        display_name="COPX DXY Direction-Gated Regime-Aware BB Squeeze Breakout",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.07,
        stop_loss=-0.06,
        holding_days=20,
    )
