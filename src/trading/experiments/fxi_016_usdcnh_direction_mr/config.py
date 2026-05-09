"""
FXI-016: USDCNH Direction Filter on FXI-ASHR Cross-Asset Divergence MR

策略方向：在 FXI-015 Att2 框架（pullback + WR + ClosePos + ATR ratio BAND
[1.05, 1.35] + FXI-ASHR 20d Div >= -8%）之上，新增「USDCNH 方向過濾」作為
repo 首次「USDCNH (offshore yuan)」direction filter 於任何資產，與 EWJ-006
USDJPY direction filter 平行（lesson #24 family v8 候選 bilateral FX
direction 變體擴展至 China）。

核心假設（少數派、未在 repo 中測試）：
- FXI = iShares China Large-Cap ETF（USD-denominated H 股）
- USDCNH = USD vs offshore Chinese Yuan（離岸人民幣）
- 當 USDCNH 急升（CNH 急貶）時：
  - 中國資本外流訊號（外資撤離、地緣政治壓力、貨幣政策歧異）
  - PBoC 介入若失敗則 risk-off 加劇 → FXI capitulation 訊號的反彈延續性受抑
  - 歷史 BoJ-equivalent shock：2015-08 PBoC 中間價改革、2018-2019 貿易戰、
    2022 Q3-Q4 zero-COVID 末期、2023 H2 房地產危機
- 反之 USDCNH 平穩或降（CNH 強勢）= 中國資金面寬鬆 → FXI MR 反彈延續性高

FXI-015 Att2 baseline 之 Part A 殘餘 2 SLs（2022-03-02 已被 ASHR div 過濾）：
- 2021-11-03 SL: Evergrande 違約 + 監管打壓持續，CNH 同期承壓
- 2023-02-06 SL: Spy balloon + 中美緊張、reopening 失望，CNH 走弱

預期 USDCNH 10d 變化（trade-level 假設驗證將揭示）：
- 殘餘 SLs 訊號日附近 USDCNH 10d 通常 > +1%（CNH 急貶 region）
- TPs 多在 USDCNH 平穩或弱勢 region
- 過濾「USDCNH 急升」訊號可移除「資本外流加劇 + capitulation 失敗」類 SL

跨資產脈絡（lesson #24 family v8 變體擴展）：
- v1-v5: implied volatility（^VIX/^MOVE/^GVZ/^OVX/^VXN forward-looking
  option-implied）
- v6 BANDS: XBI-017（^VIX BANDS [low+high]）
- v7: COPX-016 DXY direction（spot FX index variant）
- v8: EWJ-006 USDJPY direction（spot bilateral FX variant 於日本 ETF）★ 成功
- v8 (本實驗 FXI-016): USDCNH direction（spot bilateral FX variant 於中國
  H-share ETF）—— 與 EWJ-006 結構平行：
  - 同為「USD 計價單一國家 ETF + 該國貨幣 vs USD」
  - 同為「貨幣急貶 = currency drag + 政策衝擊風險」
  - threshold 預期 ~+1% 為 sweet point（與 EWJ-006 +1% 對齊）

迭代結果（全部 REJECT vs FXI-015 Att2 baseline 1.21）：
- Att1（lookback=10d, max_change=+1.0% EWJ-006 sweet spot 直接移植）：
  Part A 12 訊號 / WR 75.0% / Sharpe **0.56** cum +33.72%（vs baseline
  18/88.9%/1.21/+102.32%，**-54% Sharpe，-66% cum**）/ Part B **5 訊號完全不變**
  / min(A,B) **0.56** REJECT — +1.0% 過嚴過濾 6 Part A 訊號（多為 winners
  集中於 2020 COVID 反彈早期 + 2022 reopening 期 USDCNY 同期上升 region）
- Att2（max_change=+2.0% looser）：Part A 14 訊號 / WR 78.6% / Sharpe **0.69**
  cum +48.82% / Part B 5 訊號不變 / min(A,B) **0.69** REJECT — 仍移除 4
  Part A 訊號 cum 102→49%，閾值放寬未恢復品質
- Att3（max_change=+5.0% near non-binding diagnostic）：Part A **18 訊號**
  cum +102.30% Sharpe **1.21**（**完全等於 FXI-015 Att2 baseline**）/
  Part B 5 訊號不變 / min(A,B) **1.21** TIE baseline — 確認 filter 在
  +5.0% 結構性非綁定，框架正確接線、底層問題為 USDCNY 維度缺乏選擇力

核心失敗發現（lesson #24 family v8 邊界擴展，repo 首次否決 USDCNY direction
filter 假設）：
1. **USDCNY (onshore) ≠ USDCNH (offshore) 結構性差異**：Yahoo CNH=X / USDCNH=X
   無歷史數據（僅 1 row），CNY=X 為 PBoC daily fix 管理 ±2% 區間，反映 CNY
   方向但比離岸 CNH 對「資本外流壓力」訊號弱化；EWJ-006 USDJPY 為自由浮動
   貨幣（JPY 直接反映 BoJ 政策意外），而 CNY 為「有管理浮動」，PBoC 容忍區
   間限制了 USDCNY direction 維度的訊號強度
2. **FXI capitulation 結構與 USDCNY 走勢部分同步**：FXI MR 訊號日多發生於
   risk-off + 中國資金面寬鬆等 PBoC 介入 region，CNY 短期同步走弱（資本面）
   但中期回穩；over-tight USDCNY cap 同時過濾 winners + losers 反向選擇力弱
3. **EWJ-006 USDJPY 跨資產假設於中國資產失敗**：EWJ-006 USDJPY +1%
   sweet spot 移植至 FXI 結構性失敗，根因為 (a) 貨幣自由度（自由浮動 vs
   管理浮動）、(b) 該國央行政策反應函數（BoJ 政策意外 vs PBoC 介入維穩），
   雙重結構差異使 bilateral FX direction filter 不通用
4. **新跨資產規則（lesson #24 family v8 邊界）**：bilateral FX direction
   filter 適用條件 = 「該國央行為自由浮動匯率制度 + 政策意外為主要驅動因子」；
   PBoC 管理浮動下 CNY 維度訊號弱化，USDCNY filter 結構性失敗

跨資產脈絡（lesson #24 family v8 變體擴展）：
- v1-v5: implied volatility（^VIX/^MOVE/^GVZ/^OVX/^VXN forward-looking
  option-implied）
- v6 BANDS: XBI-017（^VIX BANDS [low+high]）
- v7: COPX-016 DXY direction（spot FX index variant，partial）
- v8: EWJ-006 USDJPY direction（spot bilateral FX 自由浮動 ✓）
- v8 (FXI-016 本實驗): USDCNY direction（spot bilateral FX 管理浮動 ✗）—
  與 EWJ-006 結構平行但失敗，定義 v8 適用邊界

成交模型：同 FXI-015（next_open_market 進場、limit_order Day TP、
stop_market GTC SL、next_open_market 到期、滑價 0.1%、悲觀認定）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI016Config(ExperimentConfig):
    """FXI-016 USDCNH Direction Filter on Cross-Asset Divergence MR 參數"""

    # === Pullback / WR / ClosePos / ATR BAND（同 FXI-014 Att2）===
    pullback_lookback: int = 10
    pullback_threshold: float = -0.05
    pullback_cap: float = -0.12

    wr_period: int = 10
    wr_threshold: float = -80.0

    close_position_threshold: float = 0.4

    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_floor: float = 1.05
    atr_ratio_ceiling: float = 1.35

    # === FXI-ASHR Cross-Asset Divergence Filter（同 FXI-015 Att2 甜蜜點）===
    anchor_ticker: str = "ASHR"
    rel_lookback: int = 20
    min_rel_return: float = -0.08

    # === USDCNY direction filter（FXI-016 核心新增）===
    # ticker：CNY=X（Yahoo USD/CNY onshore rate；rise = CNY 弱化）
    # Note：實際使用 onshore CNY 因 Yahoo 之 CNH=X / USDCNH=X 無歷史數據；
    # CNY 為 PBoC 管理 daily fix（±2% 區間），CNH 為離岸自由浮動。
    # CNY 仍能反映 USDCNH 中期方向，惟急漲幅度可能略小。
    usdcnh_ticker: str = "CNY=X"
    # lookback：起步 10d（與 EWJ-006 / COPX-016 一致；5d 噪聲過大、
    # 60d 難以反映 BoJ-equivalent 政策衝擊時間尺度）
    usdcnh_lookback: int = 10
    # max change：Att1 +1.0%（EWJ-006 sweet spot port，REJECT min 0.56）/
    # Att2 +2.0%（looser，REJECT min 0.69 — 過濾 4 Part A 訊號 cum 102→49%）/
    # Att3 +5.0%（near non-binding，diagnostic）。
    max_usdcnh_change: float = 0.050

    cooldown_days: int = 10


def create_default_config() -> FXI016Config:
    return FXI016Config(
        name="fxi_016_usdcnh_direction_mr",
        experiment_id="FXI-016",
        display_name="FXI USDCNH Direction-Gated Cross-Asset Divergence MR",
        tickers=["FXI"],
        data_start="2014-01-01",
        profit_target=0.055,
        stop_loss=-0.050,
        holding_days=20,
    )
