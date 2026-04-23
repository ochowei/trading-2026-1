"""
TLT Yield-Velocity-Gated Mean Reversion 配置 (TLT-009)

實驗動機（repo 首次使用外部 Treasury yield 數據作為 regime 過濾器）：
- TLT-007 Att2 為當前最佳（Part A Sharpe 0.12、Part B Sharpe 0.65、min(A,B) 0.12），
  BB(20, 2) 寬度 / Close < 5% 作為 regime gate 成功過濾 2022 升息期大部分訊號
- BB 寬度為**實現波動率的 backward-looking 指標**，滯後於 Fed rate shock（利率
  變動領先 TLT 價格反應 1-3 天）。在 2024-2025 高利率高原期，Fed 政策 surprise
  仍偶爾造成 TLT 短期虧損，BB 寬度未必來得及上升到 5% 以上過濾這些訊號
- 10Y Treasury yield (^TNX) 是 TLT 價格的**機械性 forward-looking 驅動因子**：
  TLT = 20+ yr Treasury ETF，price ≈ −duration × Δyield。^TNX 短期急升
  （rate shock）先於 TLT 下跌發生，因此 10 日 ^TNX 變化可作為「前瞻性 Fed
  rate-shock 偵測器」

嘗試方向：**10Y yield velocity gate（^TNX N 日變化 ≤ 閾值）**。
核心思想：
- 2022 升息期：^TNX 從 1.5% → 4.8%（累計 +330bps），10 日變化經常 > +25bps
  （中位數 +12bps，90th percentile +35bps）
- 2024-2025 高原期：^TNX 穩定在 3.5-4.5%，10 日變化中位數 0bps、90th percentile
  +20bps
- 設 10 日 ^TNX 變化 ≤ +0.15（15bps）為 calm rate regime 門檻：
  移除 ~50% 2022 訊號、保留 ~80% 2024-2025 訊號
- 此 filter 獨立於 TLT 自身技術面，捕捉「rate regime shift」事件

與 lesson #5 的區分（同 TLT-007 邏輯）：
- Lesson #5：MR 進場時若加入「當日 Close > SMA(50)」類短線趨勢過濾，會濾掉下跌
  中的好訊號
- 本實驗：^TNX velocity gate 是**外部宏觀 regime 分類器**，當市場整體利率環境
  處於 rate-shock 狀態時 blanket skip，不依 TLT 當日方向過濾

與 TLT-007 的區分：
- TLT-007：BB 寬度（TLT 自身實現波動率）= lagging indicator
- TLT-009：^TNX velocity（10Y yield 實際變動）= leading indicator（driver，非 proxy）
- 兩者理論上可獨立作用（lagging realized vol vs leading rate velocity）

迭代計畫：
- Att1：純 yield gate（^TNX 10d 變化 ≤ +0.15）取代 BB 寬度 gate，驗證單獨效果
- Att2：hybrid（^TNX 10d gate + BB 寬度 gate），雙重 regime 過濾
- Att3：根據 Att1/Att2 結果微調門檻或改變 lookback

與 TLT-008 的區分：
- TLT-008：TLT vs IEF 同資產類別 duration pair（失敗）
- TLT-009：TLT vs ^TNX（driver 而非 pair），結構不同
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT009Config(ExperimentConfig):
    """TLT-009 Yield-Velocity-Gated MR 參數

    迭代紀錄將於 Att1/2/3 各回填 Part A/B 訊號、勝率、Sharpe、累計報酬、
    出場方式分布與失敗分析。
    """

    # === 主訊號（沿用 TLT-007 Att2 的驗證有效框架）===
    # 回檔範圍進場
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_upper: float = -0.07  # 回檔 <= 7%

    # Williams %R
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置（日內反轉）
    close_position_threshold: float = 0.4

    # === Yield velocity gate（TLT-009 核心創新）===
    # ^TNX 是 CBOE 10-Year Treasury Note Yield Index，報價單位為 %（例：4.13 表 4.13%）
    # N 日變化以 pp（percentage point）為單位：0.15 = 15bps
    yield_ticker: str = "^TNX"
    yield_lookback: int = 10  # 10 交易日
    max_yield_change: float = 0.15  # 10 日 ^TNX 變化 <= +15bps (calm rate regime)

    # === BB 寬度 gate（TLT-007 Att2 架構，Att2 重新啟用 hybrid）===
    bb_period: int = 20
    bb_std: float = 2.0
    # Att1: None（停用 BB gate 以純測 yield gate 效果）
    # Att2: 0.05（啟用 hybrid：BB 寬度 < 5% AND ^TNX 10d ≤ +15bps）
    max_bb_width_ratio: float | None = 0.05

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> TLT009Config:
    return TLT009Config(
        name="tlt_009_yield_velocity_mr",
        experiment_id="TLT-009",
        display_name="TLT Yield-Velocity-Gated MR",
        tickers=["TLT"],
        data_start="2018-01-01",  # 需要 BB(20) 與 ^TNX 暖機
        profit_target=0.025,  # +2.5%（同 TLT-007）
        stop_loss=-0.035,  # -3.5%（同 TLT-007）
        holding_days=20,
    )
