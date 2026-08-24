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

    迭代紀錄（三次迭代皆失敗，未超越 TLT-007 Att2 min(A,B) 0.12）：

      Att1（純 yield gate：lookback=10, max_yield_change=+0.15，BB gate 停用）：
        Part A 24/45.8% WR/Sharpe **-0.16**/累計 -10.74%（11W/8SL/5Exp）
        Part B 8/87.5% WR/Sharpe 0.86/累計 +14.59%（7W/1SL）
        min(A,B) -0.16。失敗：2022 升息期 ^TNX 10 日變化呈「階梯式」
        （median +12bps），+15bps 門檻讓「rate-shock 之間的短暫平緩窗口」
        訊號通過，2022 仍產生 5 筆訊號（2022-03-10 SL、2022-05-05 W、
        2022-08-05 SL、2022-08-17 SL、2022-10-11 SL）。
        正面發現：Part B 8 訊號（vs TLT-007 Att2 6 訊號）多出的 2 筆仍
        87.5% WR，暗示 yield gate 在 Part B 捕捉到 BB 寬度 gate 誤刪的訊號。

      Att2（hybrid：BB 寬度 < 5% AND ^TNX 10d ≤ +15bps）：
        Part A 9/33.3% WR/Sharpe **-0.15**/累計 -3.33%（3W/2SL/4Exp）
        Part B 4/100% WR/Sharpe 0.00 零方差/累計 +10.38%
        min(A,B) -0.15。失敗：雙閘門過度過濾 Part A 的 turning-point 贏家。
        BB 5% 在 Att1→Att2 砍掉的 15 筆中 7 W/7 SL/1 Mixed，移除的贏家集中
        於升息緩和期（2020-05-06、2021-10-08、2022-05-05、2023-04-18、
        2023-08-17、2023-10-20）。核心問題：yield velocity gate 與 BB
        寬度 gate 同為「市場狀態分類器」，邊界在 regime transition 期重疊，
        hybrid 不疊加過濾力，反而放大「過濾 turning point」副作用。

      Att3（yield 方向過濾：lookback=5, max_yield_change=0.0，BB gate 停用）：
        ^TNX 5d 變化 ≤ 0（近 5 日利率不再上升），捕捉「rate-shock 剛解除」時刻。
        Part A 4/50% WR/Sharpe **-0.22**/累計 -2.70%（2W/2SL：2019-10-22 SL、
        2020-05-26 SL、2021-10-04 Exp+2.15%、2023-03-28 W）
        Part B 1/100% WR/Sharpe 0.00 零方差/累計 +2.50%（2025-05-20 W）
        min(A,B) -0.22。失敗：方向性閘門過度嚴格。TLT MR 進場結構（pullback
        3-7%）多發生於「rate-shock 仍持續但 TLT 短期超賣」時刻，此時 ^TNX 5d
        仍為正值，yield 方向閘門系統性排除此類進場機會。僅 4 Part A / 1 Part B
        訊號，樣本過少且 Sharpe 全負。

    實驗結論（三次迭代皆失敗）：外部 ^TNX yield velocity 作為 regime
    gate 於 TLT 上 **結構性受限**。
    - Att1 magnitude gate (+15bps)：計數過濾 ≠ 訊號品質過濾。2022 階梯式
      升息使 lagged yield change 無法區分「rate-shock ongoing」與
      「intermediate pause」，多段短期平緩窗口的訊號仍為虧損
    - Att2 hybrid：BB 寬度 + yield gate 邊界重疊，雙閘門系統性移除
      regime transition 期的贏家（Fed 政策轉向、reflation、SVB 後）
    - Att3 direction gate：yield 方向與 TLT pullback 進場時機在微觀層級
      反向（TLT MR 進場當下 yield 通常仍略升），方向閘門過濾率 > 90%

    結構性發現（擴展 TLT 的 regime gate 知識）：
    - ^TNX 日線級別 velocity 與 TLT 日內 price-action 存在微觀時序錯位：
      Fed rate shock 在 yield 先反映（leading），但 TLT MR 進場觸發
      （pullback + ClosePos）多發生於 rate-shock 後 TLT 日內反轉，此時
      ^TNX 近 N 日（N≤10）仍呈正值。yield velocity gate 在日線級別無法
      同步識別「TLT MR setup 已成熟」
    - BB 寬度 gate（TLT-007 Att2）之所以有效，正因其捕捉的是「已發生
      的實現波動率」，與 MR setup 的「pullback 幅度 + WR 超賣」邏輯一致
      （同為 backward-looking 的「狀態已成形」指標），反而 forward-looking
      的 yield velocity 與 TLT MR 的 trigger 時機不同步

    Cross-asset 啟示：
    1. TLT-008（duration pair IEF）+ TLT-009（driver gate ^TNX）共同驗證：
       外部利率相關指標（無論 pair 形式或 driver velocity 形式）作為 TLT MR
       過濾器**結構性不適用**，TLT-007 的「資產自身 BB 寬度 regime gate」
       仍為最佳方向
    2. 其他利率政策驅動資產（XLU 部分、REITs、高殖利率股）可能承襲相同
       結論：自身 BB 寬度 > 外部 yield 指標
    3. 若未來要再突破 TLT min Sharpe 0.12，方向應為**TLT-007 Att2 的
       更精細 BB 寬度 regime 分層**（如 BB 寬度分位 regime 而非固定閾值），
       而非加入外部 yield 指標

    最終配置：Att3（yield_lookback=5, max_yield_change=0.0, BB gate 停用）
    保留於程式碼中作為最後迭代快照，實驗整體標記為**未超越 TLT-007 Att2**。
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
    # Att1/2: lookback=10, max_yield_change=+0.15（magnitude-based calm-regime gate）
    # Att3: lookback=5, max_yield_change=0.0（direction-based yield-reversal gate：
    #   ^TNX 5d 變化 ≤ 0 表示近 5 日利率不再上升，rate-shock pressure 已解除）
    yield_lookback: int = 5
    max_yield_change: float = 0.0

    # === BB 寬度 gate（TLT-007 Att2 架構）===
    bb_period: int = 20
    bb_std: float = 2.0
    # Att1: None（停用 BB gate 以純測 yield gate 效果）
    # Att2: 0.05（啟用 hybrid：BB 寬度 < 5% AND ^TNX 10d ≤ +15bps）
    # Att3: None（停用 BB gate，Att2 驗證 hybrid 雙閘門過濾 turning-point 贏家）
    max_bb_width_ratio: float | None = None

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
