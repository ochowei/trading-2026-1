"""
EWJ-006: USDJPY Direction Filter on Post-Capitulation Vol-Transition MR

策略方向：在 EWJ-005 Att2 框架（BB(20,1.5) 下軌 + 回檔上限 7% + WR + ClosePos +
ATR>1.15 + 1d floor <= -0.5%）之上，新增「USDJPY 方向過濾」作為 repo 首次「JPY
direction filter」於任何資產（既有 lesson #24 family v6 皆使用 ^VIX / ^MOVE /
^GVZ / ^OVX implied vol；COPX-016 首試 DXY spot FX；本實驗為 spot JPY direction
變體 — repo 首次將 USDJPY 作為 macro regime indicator）。

核心假設（少數派、未在 repo 中測試）：
- EWJ = iShares MSCI Japan ETF（USD-denominated）
- 持有日股（JPY 計價），美元投資者報酬 = 日股報酬 × JPY/USD 匯率變動
- 當 USDJPY 急升（JPY rapidly weakening）時：
  - 出口股利好（豐田/Sony/任天堂海外營收增加）→ Nikkei 在 JPY 計價可能上漲
  - 但 EWJ 持有的 JPY 計價資產換算 USD 後縮水（currency drag）
  - 歷史上 currency drag 通常超過出口受益，特別在「BoJ 政策意外 / 殖利率衝擊」
    類事件（如 2022-09-01 BoJ pivot 失敗、2023-08-03 yield surge）
- 反之 USDJPY 平穩或下降時，EWJ 在 USD 計價的反彈延續性最高

EWJ-005 Att2 baseline 的 Part A 殘餘 SL（1d floor 1d <= -0.5% 過濾後）：
- 2022-09-01 SL：BoJ 守住 YCC，JPY 24 年新低，USDJPY 在 130 → 145 急升 region
- 2023-08-03 SL（已被 1d floor -0.49% 過濾）：殖利率飆升 + JPY 弱勢，
  USDJPY 上升

預期 USDJPY 10d 變化：
- 2022-09-01 訊號日附近 USDJPY 10d 通常 > +2%（JPY 急貶 region）
- Part A winners 多在 USDJPY 平穩或弱勢 region（2020-2021 USDJPY 在 100-110）
- 過濾「USDJPY 急升」訊號可移除 BoJ 政策衝擊類 SL

跨資產脈絡（lesson #24 family）：
- v1-v5: implied volatility（^VIX/^MOVE/^GVZ/^OVX forward-looking option-implied）
- v6 BANDS: XBI-017（^VIX BANDS [low+high]）
- v7 候選: COPX-016 DXY direction（spot FX index variant）
- v8 候選（本實驗）: USDJPY direction（spot bilateral FX variant 於日本 ETF）

迭代結果：
- Att1（usdjpy_lookback=10, max_change=+2.0%）：Part A 8 訊號 100% WR Sharpe
  **2.19** cum +19.62% MDD -3.99% / Part B 3 訊號 100% WR std=0 cum +10.87% /
  min(A,B)† **2.19**（+213% vs EWJ-005 Att2 baseline 0.70）。USDJPY 10d > +2.0%
  過濾的 Part A 失敗訊號（含 2022-09-01 BoJ pivot SL）成功移除；副作用為過濾
  2024-04-17 BoJ-anticipation Part B winner（10d JPY 急貶 region）。

- Att2 ★（usdjpy_lookback=10, max_change=+1.0%）：Part A 7 訊號 100% WR Sharpe
  **2.37** cum +19.31% MDD -3.99% / Part B 3 訊號 100% WR std=0 cum +10.87% /
  min(A,B)† **2.37**（+239% vs baseline，Att1 比較 +8% Sharpe）。**新全域最優**。
  +1.0% 收緊過濾 1 個 Part A 邊緣 winner（USDJPY 10d ∈ (+1.0%, +2.0%]，Sharpe 提升
  due to 變異降低；保留全部 Part B winners。

- Att3（usdjpy_lookback=10, max_change=+0.5%）：Part A 5 訊號 100% WR Sharpe
  **2.31** cum +12.24% / Part B 2 訊號 100% WR std=0 cum +7.12% / min(A,B)† **2.31**
  （-3% vs Att2，過緊）。-0.5% 移除 2 個 Part A winners + 1 個 Part B winner
  (2024-06-13 USDJPY 10d ∈ (+0.5%, +1.0%])，確認 +1.0% 為甜蜜點。

跨資產貢獻：
- **Repo 首次「USDJPY (USD/JPY spot rate) direction filter」於任何資產**
- Lesson #24 family v1-v6 皆 implied vol（^VIX/^MOVE/^GVZ/^OVX forward-looking
  option-implied）；v7 候選 COPX-016 DXY spot FX index；本實驗為 v8 候選
  bilateral FX direction 於單一國家 ETF
- 確認 BoJ 政策衝擊類失敗模式（2022-09-01 YCC 守成、2023-08-03 殖利率衝擊）
  在 USDJPY 10d 維度具區分力（USDJPY 10d > +1.0% 訊號 = 急貶 currency drag region）

成交模型：同 EWJ-005（next_open_market 進場、limit_order Day TP、
stop_market GTC SL、next_open_market 到期、滑價 0.1%、悲觀認定）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWJ006Config(ExperimentConfig):
    """EWJ-006 USDJPY Direction Filter on Vol-Transition MR 參數"""

    # === BB / 回檔 / WR / ClosePos / ATR（同 EWJ-005 Att2）===
    bb_period: int = 20
    bb_std: float = 1.5

    pullback_lookback: int = 10
    pullback_cap: float = -0.07

    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15

    # === Capitulation strength filter（同 EWJ-005 Att2 甜蜜點）===
    # 1d floor <= -0.5%
    capitulation_mode: str = "1d_floor"
    capitulation_threshold: float = -0.005

    # === USDJPY direction filter（EWJ-006 核心新增）===
    # ticker：JPY=X（Yahoo USD/JPY rate；rise = JPY 弱化）
    usdjpy_ticker: str = "JPY=X"
    # lookback：起步 10d 與 COPX-016 一致；5d 可能太短捕捉不到 BoJ 政策衝擊
    usdjpy_lookback: int = 10
    # max change：Att1 +2.0%（min 2.19）；Att2 ★ +1.0%（min 2.37）；Att3 +0.5%
    # 過緊（min 2.31，過濾 1 Part B winner）。Att2 為甜蜜點。
    max_usdjpy_change: float = 0.010

    cooldown_days: int = 7


def create_default_config() -> EWJ006Config:
    """建立預設配置（Att2 ★ 甜蜜點：lookback=10d, max_change=+1.0%）"""
    return EWJ006Config(
        name="ewj_006_usdjpy_direction_mr",
        experiment_id="EWJ-006",
        display_name="EWJ USDJPY Direction-Gated Vol-Transition MR",
        tickers=["EWJ"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.040,
        holding_days=20,
    )
