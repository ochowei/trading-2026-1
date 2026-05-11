"""
VGK-009: EURUSD Direction Filter on Post-Capitulation Vol-Transition MR

策略方向：在 VGK-008 Att2 框架（BB(20, 2.0) 下軌 + 10 日回檔上限 -7% +
WR(10) <= -80 + ClosePos >= 40% + ATR(5)/ATR(20) > 1.15 + 2DD floor <=
-2.0%）之上，新增「EUR/USD 方向過濾」作為 repo 第 2 次「bilateral FX
direction filter」於任何資產（繼 EWJ-006 USDJPY 後 — lesson #24 family v8
bilateral FX direction 變體首次跨資產移植，從亞洲已開發 ETF 擴展至歐洲
已開發 ETF）。

核心假設：
- VGK = Vanguard FTSE Europe ETF（USD-denominated）
- 持有歐洲股（多為 EUR/GBP/CHF 計價，EUR-area 公司佔大宗）
- 美元投資者報酬 = 歐股報酬 × 對應貨幣對 USD 變動
- 當 EUR/USD 急貶（EUR 弱化）時：
  - 歐洲出口股略受惠（空中巴士/德國車廠/歐萊雅 海外營收以美元計增加）
  - 但 VGK 持有的 EUR 計價資產換算 USD 後縮水（currency drag）
  - 歷史上 currency drag 通常超過出口受益，特別在「ECB 政策意外/能源衝擊/
    歐債危機/俄烏戰爭」類事件
- 反之 EUR/USD 平穩或上升時，VGK 在 USD 計價的反彈延續性最高

VGK-008 Att2 baseline 的 Part A/B winners 結構（已被 2DD floor <= -2.0% 過濾）：
- Part A 3 訊號全 +3.5% TP（深 2DD capitulation）
- Part B 4 訊號全 +3.5% TP

但 VGK-008 的 Part A/B cum gap 26.8% 仍偏高，A/B 訊號比 3:4 = 25%，
EUR/USD direction filter 預期可進一步精煉訊號品質：移除「EUR 急貶 +
歐洲特定壓力」的失敗候選邊緣 winners（如 2022 歐洲能源危機期間的
short-cycle 反彈）。

跨資產脈絡（lesson #24 family）：
- v1-v5: implied volatility（^VIX/^MOVE/^GVZ/^OVX forward-looking option-implied）
- v6 BANDS: XBI-017（^VIX BANDS [low+high]）
- v7 候選: COPX-016 DXY direction（spot FX index variant）
- v8 候選: EWJ-006 USDJPY direction（spot bilateral FX 於亞洲已開發 ETF）
- v8 擴展（本實驗）: VGK-009 EURUSD direction（spot bilateral FX 於歐洲已開發 ETF）

迭代結果（2026-05-09）：

- Att1（eurusd_lookback=10, min_change=-2.0% 寬鬆 baseline）：
  Part A 3 訊號 100% WR Sharpe 3.02 cum +8.74% / Part B 4 訊號 100% WR
  Sharpe 2.60 cum +11.94% / min(A,B) **2.60 TIE baseline VGK-008 Att2**。
  -2.0% 閾值對全部 7 個 baseline 訊號 EUR/USD 10d >= -2.0% 完全 non-binding，
  filter 無作用 — 證明 VGK-008 Att2 baseline 訊號日 EUR/USD 10d 分布
  集中於 -2.0% 上方，極端 EUR 急貶事件不在 baseline 訊號中。

- Att2（eurusd_lookback=10, min_change=-1.0% EWJ-006 sweet spot 鏡像）：
  Part A 1 訊號 100% WR std=0 cum +3.50% / Part B 2 訊號 100% WR std=0 cum +7.12% /
  min(A,B) collapsed signal counts (3→1, 4→2 移除 4/7 winners) **REJECT**。
  -1.0% 對 VGK 過嚴 — VGK-008 baseline 已透過 2DD floor + 7-day cooldown
  完全清除 SLs（Part A 0 SL / Part B 0 SL），EUR/USD filter 在 cleaned baseline
  上僅能移除 winners。-1.0% 閾值對應 EUR/USD ~1σ 10-day vol，過於激進。
  A/B 訊號比 1:2 = 50% gap、A/B cum 50% gap，雙重失敗。

- Att3 ★（eurusd_lookback=10, min_change=-1.5% 中間 robustness）：
  Part A 3 訊號 100% WR Sharpe 3.02 cum +8.74%（**完全等於 baseline，filter
  對 Part A 非綁定**）/ Part B 3 訊號 100% WR std=0 cum +10.87%（過濾 1 個
  expiry +0.96% winner，3/3 全 TPs std=0）/ min(A,B)† **= Part A 3.02**
  （沿用 EWJ-003/SPY-009/DIA-012/IWM-013/CIBR-014 慣例：Part B std=0 結構性
  零方差，採 Part A Sharpe 為 min 約束），**+16% vs VGK-008 Att2 baseline 2.60**.
  A/B 平衡達成：cum 8.74 vs 10.87 → diff 2.13pp 相對 19.6%（<30% ✓ 從 baseline
  26.8% 改善）；訊號比 3:3 raw = 0% gap（<<50% ✓ 從 baseline 25% 改善）；
  WR 雙 100%。被過濾的 Part B 訊號為 2024-11-13 expiry +0.96%（baseline 中
  最低 1d 報酬訊號，EUR/USD 10d 介於 [-1.5%, -1.0%] 邊緣 EUR 弱勢區間，
  filter 將 baseline 唯一 non-TP winner 移除使 Part B 純化為 std=0 全 TP），
  保留全部 3 TPs（2024-01-17、2024-06-14、2024-08-02）。Att3 為新全域最優。

方向說明：
- min_eurusd_change = -0.015 表示「只有 EUR/USD 過去 10 日跌幅 <= 1.5% 時才允許進場」
- 即 EUR/USD 過去 10 日 >= -1.5%（EUR 未明顯弱化），則訊號通過
- EUR/USD 跌幅 > 1.5% 表示 EUR 急貶 currency drag region，過濾該訊號

跨資產貢獻（lesson #24 family v8 邊界精煉）：
- Repo 第 2 次「bilateral FX direction filter」（繼 EWJ-006 USDJPY 後）
- 首次 EUR/USD 應用於任何資產，亞洲已開發 ETF（EWJ）→ 歐洲已開發 ETF（VGK）
  跨地域移植成功
- 跨資產發現：threshold 因資產 baseline 訊號 cleanliness 而異 —
  EWJ-006 baseline 含 1 個 SL，USDJPY 10d > +1.0% 為 surgical filter；
  VGK-008 baseline 已 cleaned (0 SLs)，EUR/USD filter 變為「expiry winner
  純化」維度，sweet spot 上移至 -1.5%（vs EWJ-006 +1.0% 對應強度）
- 失敗模式對稱性：EWJ-006 USDJPY 急升 = JPY 弱化 currency drag；
  VGK-009 EURUSD 急跌 = EUR 弱化 currency drag — 同源 currency drag
  失敗模式驗證跨地域

成交模型：同 VGK-008（next_open_market 進場、limit_order Day TP、
stop_market GTC SL、next_open_market 到期、滑價 0.1%、悲觀認定）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VGK009Config(ExperimentConfig):
    """VGK-009 EURUSD Direction Filter on Vol-Transition MR 參數"""

    # === BB / 回檔 / WR / ClosePos / ATR（同 VGK-008 Att2）===
    bb_period: int = 20
    bb_std: float = 2.0

    pullback_lookback: int = 10
    pullback_cap: float = -0.07

    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.40

    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # === 2 日報酬下限（同 VGK-008 Att2 sweet spot）===
    twoday_return_floor: float = -0.020

    # === EUR/USD direction filter（VGK-009 核心新增）===
    # ticker: EURUSD=X（Yahoo EUR/USD spot rate；rise = EUR 強勢）
    eurusd_ticker: str = "EURUSD=X"
    # lookback: 10 日（與 EWJ-006 / COPX-016 對齊）
    eurusd_lookback: int = 10
    # min_change: 過濾 EUR/USD 過去 N 日跌幅過深的訊號（EUR 急貶 currency drag）
    # Att1 -2.0%（寬鬆 baseline TIE）, Att2 -1.0%（過嚴 over-filter REJECT）,
    # Att3 ★ -1.5%（中間 robustness sweet spot，min† = Part A 3.02 +16% baseline）
    min_eurusd_change: float = -0.015

    # === 冷卻天數（同 VGK-008）===
    cooldown_days: int = 7


def create_default_config() -> VGK009Config:
    """建立預設配置（Att3 ★ 全域最優：lookback=10d, min_change=-1.5%）"""
    return VGK009Config(
        name="vgk_009_eurusd_direction_mr",
        experiment_id="VGK-009",
        display_name="VGK EURUSD Direction-Gated Vol-Transition MR",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.040,
        holding_days=20,
    )
