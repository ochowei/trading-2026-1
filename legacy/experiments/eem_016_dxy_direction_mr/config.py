"""
EEM-016: DXY Direction Filter on Post-Capitulation Vol-Transition MR

策略方向：在 EEM-014 Att2 框架（BB(20,2.0) 下軌 + 回檔上限 -7% + WR(10)<=-85 +
ClosePos>=40% + ATR(5)/ATR(20)>1.10 + 2DD floor <= -0.5%）之上，新增「DXY
方向過濾」（USD 強弱 regime gate）。repo 第二次 DXY direction filter，第一次
為 COPX-016（Part A 290% 改善但 Part B 結構性 non-binding，min(A,B) TIE
baseline）。

核心假設：
- EEM = iShares MSCI Emerging Markets ETF（USD-denominated）
- 持有新興市場各國股票（local currency 計價），美元投資者報酬 = 標的報酬 ×
  匯率變動
- 當 DXY 急升（USD 全球性強勢）時：
  - 新興市場資金外流（capital flight to USD assets）
  - USD 計價 EM 主權/企業債負擔加重 → 信用風險溢價上升
  - 商品價格疲弱（強 USD 壓抑大宗商品）→ EM 出口商承壓
  - 中美貿易摩擦時 USD 通常強勢，China-heavy EEM 雙重承壓
- 反之 DXY 平穩或下跌時，EEM MR 訊號的反轉延續性最高

EEM-014 Att2 baseline 殘餘 SL（已通過 2DD floor 過濾後）：
- 2021-07-08：DiDi ADR 監管衝擊（中國特定，DXY 反應較弱）
- 2025-11-19：美中貿易摩擦升溫（典型 risk-off，DXY 應強勢）

預期 DXY 過濾效果：
- 2025-11-19 Part B SL 預期 DXY 10d > 0%（risk-off USD bid）→ 可被過濾
- TPs 多在 DXY 穩定/下跌期（risk-on，capital flow into EM）→ 應被保留
- 部分 winners 可能伴隨 DXY 中性 region

跨資產脈絡（lesson #24 family + 跨資產 divergence regime gate）：
- v1-v5: implied volatility（^VIX/^MOVE/^GVZ/^OVX forward-looking option-implied）
- v6 BANDS: XBI-017（^VIX BANDS）
- v7: COPX-016 DXY direction（spot FX index variant，PARTIAL：Part A +65%
  但 Part B 結構性無法改善，min(A,B) TIE baseline）
- v8: EWJ-006 USDJPY direction（spot bilateral FX 變體於日本 ETF，min 0.70→2.37
  +239%）
- **v9 候選（本實驗）**：DXY direction 應用於 broad EM ETF（first time）

迭代設計：
- Att1（lookback=10, max_change=+1.5%）：寬鬆起點，先驗證 filter 大致方向
- Att2（lookback=10, max_change=+1.0%）：medium，與 EWJ-006 sweet spot 一致
- Att3（lookback=10, max_change=+0.5%）：strict，與 COPX-016 sweet spot 一致

成交模型：同 EEM-014（next_open_market 進場、limit_order Day TP、
stop_market GTC SL、next_open_market 到期、滑價 0.1%、悲觀認定）

關鍵風險：
- EEM-014 baseline 訊號樣本量少（5 + 4 = 9 訊號），任何 filter 過嚴
  即可能崩壞統計顯著性
- COPX-016 顯示 DXY filter 對「Part B 訊號數 < 3」資產結構性 non-binding；
  EEM Part B 為 4 訊號，介於危險邊界
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM016Config(ExperimentConfig):
    """EEM-016 DXY Direction Filter on Vol-Transition MR 參數"""

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

    # === DXY direction filter（EEM-016 核心新增）===
    # ticker：DX-Y.NYB（Yahoo DXY index；rise = USD 強勢）
    dxy_ticker: str = "DX-Y.NYB"
    # lookback：起步 10d 與 COPX-016 / EWJ-006 一致
    dxy_lookback: int = 10
    # 三次迭代探索（max=cap、min=floor 雙方向）：
    # Att1 max <= +1.5%（cap，寬鬆）：min(A,B) 0.34（-39%）— Part B 流失 1 winner
    # Att2 max <= +1.0%（cap，醫學）：min(A,B) 0.00（崩壞）— Part B 流失 2 winners
    #                                                    僅留 SL
    # Att3 min >= -1.0%（floor，反向）：要求 DXY 10d 不大幅貶值，過濾 USD weakness regime
    #
    # filter_mode："max"（cap，filter when USD too strong）|
    #              "min"（floor，filter when USD too weak）
    filter_mode: str = "min"
    max_dxy_change: float = 0.010
    min_dxy_change: float = -0.010

    cooldown_days: int = 10


def create_default_config() -> EEM016Config:
    """建立預設配置（Att1 寬鬆起點：lookback=10d, max_change=+1.5%）"""
    return EEM016Config(
        name="eem_016_dxy_direction_mr",
        experiment_id="EEM-016",
        display_name="EEM DXY Direction-Gated Vol-Transition MR",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.030,
        holding_days=20,
    )
