"""
INDA DXY Direction Filter MR 配置 (INDA-014)

動機：INDA-011 Att3（min(A,B)† Sharpe 0.55，新全域最優）已透過
「2DD floor <= -2.0% + 3DD cap >= -3.0%」雙維度 capitulation-strength 過濾，
將 Part A 精煉至 5 訊號 / 80.0% WR / Sharpe 0.55，但仍殘餘 1 筆 Part A 停損：
  - 2022-09-16 SL -4.10%（Fed CPI shock，3DD 淺）

Part B 為結構性零方差（2 訊號 100% WR std=0），min(A,B)† 之約束來自
Part A Sharpe 0.55。欲突破必須在「不損失 Part A winners」的前提下移除
2022-09-16 殘餘 SL（與任何低品質近零到期）。

核心假設（lesson #24 family DIRECTION 變體 — repo 首次 DXY direction
filter 於單一國家 EM 股票 ETF）：
    INDA 的關鍵失敗模式為「post-peak slow-melt drift」，其結構性 driver
    為「盧比匯率 + 外資（FII）流向」（見 INDA 資產特性）。USD 走強
    （DXY 上行）→ EM 資金外流預期 → 印度股市持續承壓 → dip-buy 進場後
    續跌停損。2022-09-16 SL 恰發生於 2022 年 9 月（DXY 攀至 ~114，
    20 年高點，Fed 激進升息），為近 20 年最強 USD regime；而保留的
    winners（2020-2021 post-COVID 反彈、2022 年中熊市反彈）多發生於
    USD 走弱 / 持平 / 紓困 regime。

策略方向：在 INDA-011 Att3 全條件之上，疊加「DXY N 日報酬 <=
max_dxy_change」方向過濾（require USD 近期非強勢上行），過濾「強 USD
逆風期」的 capitulation 進場，保留 USD 中性 / 走弱期的真實 V-bounce。

lesson #24 family DIRECTION 變體跨資產脈絡：
- TLT-013 ^MOVE LEVEL cap、XLU-013 ^MOVE 3d change DIRECTION、
  GLD-015 ^GVZ 10d DIRECTION、USO-025 ^OVX 3d DIRECTION、
  XBI-017 ^VIX BANDS、COPX-016 DXY 10d DIRECTION（repo 首次 DXY）
- COPX-016 明確提出開放跨資產假設：「DXY direction filter 預期適用於
  USD-denominated 商品/礦業類資產 + EM ETFs（FXI/EEM/INDA/EWZ）」
- INDA-014 為該假設於「單一國家 EM 股票 ETF」之首次驗證
- DXY 為 spot FX index（非 implied vol），代表 USD 對 6 主要貨幣相對
  強度，對「EM 股票資金流」為直接結構性 driver

DXY 過濾不違反 lesson #5（MR + 趨勢方向濾波）：DXY 為 exogenous
macro regime（USD 軌跡），非 INDA 自身價格趨勢濾波；與 lesson #24
family 既有 5+ 次 MR 框架成功移植（XLU-013 / GLD-015 / USO-025）同類。

DXY 過濾不違反 lesson #14（VIX 閾值過濾 MR）：採 N 日「報酬 / 方向」
（change-based），非「水位」（level-based）；lesson #24 DIRECTION 變體
即為規避 level-filter 問題而生（XLU-013 / GLD-015 證實 DIRECTION 綁定
而 LEVEL 非綁定）。

========================================================================
三次迭代結果（成交模型 0.1% slippage，隔日開盤市價進場，悲觀認定）：
========================================================================
INDA-011 Att3 baseline（5 Part A 訊號）各訊號 DXY 變動診斷：
  日期         結果   DXY3d    DXY5d    DXY10d
  2020-10-29   WIN   +0.98%   +1.09%   +0.11%
  2020-12-21   WIN   -0.45%   -0.74%   -0.83%
  2021-12-06   WIN   +0.25%   -0.05%   +0.23%
  2022-06-16   WIN   -1.38%   +0.40%   +1.83%
  2022-09-16   SL    -0.05%   +0.70%   +0.06%   ← 唯一殘餘 SL
  2024-06-04(B)WIN   -0.58%   -0.48%   -0.44%
  2024-11-13(B)WIN   +1.41%   +1.32%   +2.39%

關鍵：2022-09-16 SL 的 DXY 變動在任何 lookback（3d/5d/10d）皆位於
winners 分布的「正中央」（mid-distribution），無單一 cap/floor 閾值
可隔離。

Att1（FAIL）：DXY 10 日報酬 <= +1.0%
  Part A 4 訊號 WR 75.0% Sharpe **0.37** cum +4.54%（1 SL 殘留）
  Part B 1 訊號 100% WR std=0 Sharpe 0.00 cum +3.50%
  min(A,B) **0.37**（-33% vs INDA-011 Att3 0.55）
  失敗分析：+1.0% cap 過濾 DXY10d > +1.0% 的訊號 ——
  移除 2022-06-16（+1.83%，WINNER）與 2024-11-13（+2.39%，Part B
  WINNER），但 2022-09-16 SL（DXY10d +0.06%）存活。方向反效果：
  INDA 高品質 V-bounce 常發生於 USD 走強期（post-FOMC / post-election
  宏觀衝擊命中印度但隨即反轉），與假設相反。

Att2（PARTIAL / REJECT）：DXY 5 日報酬 <= +0.5%（針對 SL DXY5d=+0.70%）
  Part A 3 訊號 WR 100% Sharpe **3.56** cum +9.01% MaxDD -3.70%
  Part B 1 訊號 100% WR std=0 Sharpe 0.00 cum +3.50%
  min(A,B)† 名目 3.56 BUT **REJECT**
  失敗分析：+0.5% cap 移除 2022-09-16 SL（+0.70%）但同時移除
  2020-10-29（DXY5d +1.09%，WINNER）並使 Part B 2→1。
  - A/B 累計差 |9.01-3.50|/max = **61.2% >> 30% ❌**
  - Part B 僅 1 訊號統計顯著性嚴重不足（沿用 COPX-015 Att2 REJECT
    判例：Part B 1 訊號 + A/B cum gap >30% 應 REJECT）
  - Sharpe 3.56 為「過濾至 3 個有利訊號 + Part B 縮至 1」之 over-filter
    人為產物，非穩健改善

Att3（FAIL）：DXY 5 日報酬 <= +0.8%（loosen，置於 SL +0.70% 與
            winner +1.09% 之間，證實無 sweet spot）
  Part A 4 訊號 WR 75.0% Sharpe **0.37** cum +4.54%
  Part B 1 訊號 100% WR std=0 Sharpe 0.00 cum +3.50%
  min(A,B) **0.37**（-33% vs INDA-011 Att3 0.55）
  失敗分析：放寬至 +0.8% 重新放回 2022-09-16 SL（DXY5d +0.70% <=
  +0.8%），同時仍移除 winners 2020-10-29（+1.09%）/ 2024-11-13
  （+1.32%）。**證實無 sweet spot**：唯一能移除 SL 的閾值帶
  （<= +0.65%）必同時移除 winners；唯一能保留 winners 的閾值帶
  （>= +1.1%）必同時保留 SL。SL 結構性夾在 winners 之間。

========================================================================
結論：INDA-014 三次迭代全部 FAIL，INDA-011 Att3（min 0.55）維持全域最優
========================================================================
根因：2022-09-16 INDA SL 為 Fed CPI shock，經「利率 / 風險」通道傳導至
印度股市，**非** USD 強度通道（signal-day DXY 3d/5d/10d =
-0.05%/+0.70%/+0.06% 全部位於 winners 分布正中）。而多筆 INDA winners
反而發生於 USD 走強期。INDA winners/loser 的 DXY 變動分布完全重疊，
任何 lookback / 方向皆無 surgical 切點。

預設配置保留 Att2（5d, +0.5%）作為文件化的 nominal-best（REJECT）。

跨資產貢獻（負面結果，repo 重要邊界發現）：
- **REJECT COPX-016 開放跨資產假設**「DXY direction → EM ETFs INDA」
  於單一國家 EM 股票 ETF 之 MR 框架
- USD→商品 傳導（COPX：銅以 USD 計價，強 USD 結構性壓抑 → DXY
  direction 有效）≠ USD→單一國家 EM 股票 傳導（INDA：capitulation SL
  為利率 / 風險衝擊驅動，V-bounce 常於 USD 走強期發生）
- 擴展 lesson #24 family DIRECTION 邊界：DXY direction filter 需資產
  失敗模式為「USD 傳導」；INDA CPI / 利率衝擊型 SL 非此類
- 平行 lesson #6（邊際確認指標重疊無區分力）與 COPX-014
  （winners/losers Rel 重疊無 surgical 切點）失敗家族
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDA014Config(ExperimentConfig):
    """INDA-014 DXY Direction Filter MR 參數"""

    # === INDA-011 Att3 base（multi-period capitulation-strength filter）===
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03
    pullback_cap: float = -0.07
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.4
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15
    drop_2d_floor: float = -0.02
    drop_3d_cap: float = -0.03
    cooldown_days: int = 7

    # === INDA-014 新增：DXY 方向過濾閘門 ===
    # ticker：DX-Y.NYB（ICE US Dollar Index，yfinance 歷史回測穩定，
    # 沿用 COPX-016）
    # 三次迭代閾值（全部 FAIL，詳見模組 docstring）：
    #   Att1 (lookback=10, +1.0%): min(A,B) 0.37 FAIL（移除 winners 保留 SL）
    #   Att2 (lookback=5,  +0.5%): †3.56 nominal BUT REJECT（A/B cum gap
    #         61.2%>30% + Part B 1 訊號統計不足，over-filter 人為產物）
    #   Att3 (lookback=5,  +0.8%): min(A,B) 0.37 FAIL（證實無 sweet spot）
    # 預設保留 Att2 作為文件化 nominal-best（REJECT）。
    dxy_ticker: str = "DX-Y.NYB"
    dxy_lookback: int = 5
    max_dxy_change: float = 0.005  # Att2：DXY 5 日報酬 <= +0.5%（nominal-best, REJECT）


def create_default_config() -> INDA014Config:
    """建立預設配置（Att1：DXY 10d <= +1.0% 方向過濾）"""
    return INDA014Config(
        name="inda_014_dxy_direction_mr",
        experiment_id="INDA-014",
        display_name="INDA DXY Direction Filter MR (FAILED, INDA-011 維持最優)",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,
        stop_loss=-0.04,
        holding_days=15,
    )
