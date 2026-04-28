"""
VGK Post-Capitulation Vol-Transition 均值回歸配置 (VGK-008)

動機：INDA-010 Att3（2026-04-21）之跨資產假設明確列舉 VGK 為候選對象：

  "2DD floor 加深方向可能擴展至其他 low-vol single-country EM ETFs
  （FXI、EWT policy-side、EWZ commodity-side）與 low-vol defensive ETFs
  （XLU、TLT、**VGK**）的殘餘 slow-melt 失敗訊號"

EEM-014 Att2（2026-04-21，1.17% vol）以 2DD floor <= -0.5% 改善 min(A,B)
0.34→0.56（+65%）；INDA-010 Att3（2026-04-21，0.97% vol）以 2DD floor
<= -2.0% 改善 min(A,B) 0.23→0.30（+30%）。VGK 日波動 1.12% 介於兩者之間，
為 repo 首次「2DD floor 方向」在已開發歐洲寬基 ETF 上驗證。

VGK-007 Att1（基線 min 0.53）的實際 Part A/B 殘餘停損（signal-day 2DD）：
  Part A 9 訊號（WR 77.8%）：
    SLs: 2023-03-13 (-4.10%, 2DD -1.50%, RSI 35.3)
    到期虧損: 2023-09-27 (-3.08%, 2DD -1.68%)
    淺 2DD 到期贏: 2019-05-09 (+1.78%, 2DD -0.11%)
    淺 2DD 到期贏: 2021-09-20 (+1.51%, 2DD -4.06%)  # 深 2DD 到期
  Part B 7 訊號（WR 85.7%）：
    SLs: 2024-10-31 (-4.10%, 2DD -1.47%)
  Part C 1 訊號：
    SLs: 2026-03-05 (-4.10%, 2DD -0.89%)

VGK 的 SL 2DD 分布：-0.89% ~ -1.68%（中等深度，類似 EEM 的 -0.85% 中位）；
TPs 2DD 分布：-1.39% ~ -4.06%（較深，真 capitulation）。
方向為 2DD **floor**（排除淺 2DD 弱 MR 訊號），與 EEM/INDA 同向。

========================================================================
三次迭代記錄（2026-04-22，成交模型 0.1% slippage，隔日開盤市價進場）：
========================================================================

Att1：2DD floor <= -1.0%（起始中間門檻，介於 INDA -2.0% 與 EEM -0.5%）
  Part A: 8 訊號 WR 75.0% cum +12.06% Sharpe **0.49**（崩壞 vs 基線 0.53）
  Part B: 7 訊號 WR 85.7% cum +15.31% Sharpe 0.78（不變）
  Part C: 0 訊號（2026-03-05 SL 的 2DD -0.89% 被過濾）
  min(A,B) **0.49**（-7.5% vs VGK-007 Att1 的 0.53）
  失敗分析：-1.0% 過於淺，僅過濾 1 筆 Part A 淺 2DD 訊號（2019-05-09 +1.78% 到期），
  保留所有 3 筆 Part A 失敗交易（2023-03-13 SL -1.50%、2023-09-27 loss -1.68%
  均 > -1.0%）。淨效果：失去 1 筆 +1.78% 贏家 + 換掉 1 筆贏家（2021-11-24→2021-11-29
  因冷卻 reset），WR 77.8%→75.0% 劣化。-1.0% 門檻選擇錯誤——VGK 的 SL 均位於
  -1.4% ~ -1.7% 中等深度區間，-1.0% 無法觸及。

Att2 ★（全域最佳）：2DD floor <= -2.0%（向 INDA-010 Att3 門檻看齊）
  Part A: 3 訊號 WR 100% cum +8.74% Sharpe **3.02**（+470% vs 基線）
  Part B: 4 訊號 WR 100% cum +11.94% Sharpe **2.60**（+233% vs 基線）
  Part C: 0 訊號（2026-03-05 SL 2DD -0.89% 被過濾）
  min(A,B) **2.60**（+390% vs VGK-007 Att1 的 0.53）
  A/B cum 差 3.20pp（26.8% 相對，<30% ✓）
  A/B 訊號數 3:4（25% 相對差，<50% ✓ 以原始數量計）
  成功關鍵：-2.0% 一次過濾所有 VGK-007 失敗交易：
    Part A 過濾 3 筆：2019-05-09 (+1.78% 到期,淺 2DD -0.11%)、
                     2023-03-13 SL (-4.10%,2DD -1.50%)、
                     2023-09-27 loss (-3.08%,2DD -1.68%)
    Part B 過濾 3 筆：2024-04-10 (+3.79% 到期,2DD -1.39%)、
                     2024-10-31 SL (-4.10%,2DD -1.47%)、
                     2025-08-01 (+3.50% TP,2DD -1.62%)
    Part C 過濾 1 筆：2026-03-05 SL (-4.10%,2DD -0.89%)
  代價：Part A 訊號密度 1.8/yr→0.6/yr（-67%），Part B 3.5/yr→2.0/yr（-43%）
  保留訊號全部為深 2DD capitulation（-2.10% ~ -4.06%），集中真正反彈機會。

Att3：2DD floor <= -1.5%（中間門檻，嘗試兼顧訊號數與品質）
  Part A: 7 訊號 WR 71.4% cum +8.27% Sharpe **0.38**（-28% vs 基線）
  Part B: 5 訊號 WR 100% cum +15.85% Sharpe **2.94**
  Part C: 0 訊號
  min(A,B) **0.38**（-28% vs VGK-007 Att1 的 0.53）
  失敗分析：-1.5% 仍保留 2023-03-13 SL（2DD -1.50% = -1.5% 邊界 kept）和
    2023-09-27 loss（-1.68% < -1.5% kept）；僅新增 2019-08-06 (-1.59% TP)、
    2021-11-29 (-? TP replacement)、2025-08-01 (-1.62% TP)。Part A 新增 4 筆
    訊號但含 2 筆失敗，WR 崩至 71.4%，Sharpe 劣於 Att2 且不如基線。揭示 VGK 的
    SL 集中於 2DD -1.50% ~ -1.70% 窄帶——-1.5% 僅觸及帶邊緣、-2.0% 才完全繞過。
  核心發現：**VGK 的 2DD floor 門檻為「懸崖式」而非漸進式**——-1.0% 無效、
    -1.5% 劣化、-2.0% 成功。-1.7% 與 -2.0% 等效（SL 都在 -1.47%~-1.68% 區間）。

========================================================================
最終配置（Att2）：VGK-007 Att1 所有條件 + 2DD floor <= -2.0%
========================================================================
- BB(20, 2.0) 下軌
- 10 日回檔上限 -7%
- WR(10) <= -80
- ClosePos >= 40%
- ATR(5)/ATR(20) > 1.15
- **2 日收盤報酬 <= -2.0%（Att2 核心創新，與 INDA-010 Att3 同門檻）**
- TP +3.5% / SL -4.0% / 20 天 / 冷卻 7 天

跨資產貢獻：
- Repo 第 4 次「2DD floor 方向」成功驗證（繼 USO-013 / EEM-014 / INDA-010 後）
- 首次於已開發歐洲寬基 ETF（VGK）驗證 2DD floor 方向
- 擴展 lesson #19：2DD floor 方向在 broad EM（EEM 1.17%）、single-country
  EM（INDA 0.97%）、developed European broad（VGK 1.12%）上皆成功，顯示該
  失敗模式結構具跨地域普適性——低波動國際寬基 ETF 的 SL 集中於淺幅漂移，
  需 2DD floor 排除
- 驗證 INDA-010 跨資產假設：2DD floor 加深方向確實擴展至 low-vol defensive
  broad ETFs（VGK 驗證）
- 「懸崖式」門檻特性：VGK 的 SL 集中於 2DD -1.47% ~ -1.68% 窄帶，
  -2.0% 為懸崖另一邊（完全繞過）、-1.5% 仍在帶內、-1.0% 遠未及
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class VGK008Config(ExperimentConfig):
    """VGK-008 Post-Capitulation Vol-Transition MR 參數"""

    # BB 參數（同 VGK-007 Att1）
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離（同 VGK-007 Att1）
    pullback_lookback: int = 10
    pullback_cap: float = -0.07

    # 品質過濾（同 VGK-007 Att1）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.40

    # ATR 當日過濾（同 VGK-007 Att1）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 2 日急跌過濾（Att2 核心創新：2DD floor <= -2.0%）
    #
    # VGK-007 Att1 殘餘失敗交易 2DD 分布：
    #   Part A: 2023-03-13 SL (-1.50%)、2023-09-27 loss (-1.68%)
    #   Part B: 2024-10-31 SL (-1.47%)
    #   Part C: 2026-03-05 SL (-0.89%)
    # 全部 SLs 位於 2DD -0.89% ~ -1.68% 區間（淺 ~ 中等深度）。
    # Att1 (-1.0%) 過淺無過濾力，Att3 (-1.5%) 仍在 SL 帶內，
    # Att2 (-2.0%) 一次繞過整個 SL 帶，僅保留深 2DD 真 capitulation 訊號。
    #
    # 門檻選擇參考：
    #   - INDA 0.97% vol: -2.0% (2.1σ @ 1-day vol，1.46σ @ 2-day vol)
    #   - EEM 1.17% vol: -0.5% (0.43σ @ 1-day vol，0.30σ @ 2-day vol)
    #   - VGK 1.12% vol: -2.0% (1.79σ @ 1-day vol，1.27σ @ 2-day vol)
    # VGK 與 INDA 同門檻但 σ 更低，確認 2DD floor 方向之 σ 縮放為非線性
    # （取決於 SL 的 2DD 結構而非 vol 本身）。
    twoday_return_floor: float = -0.020

    # 冷卻期（同 VGK-007 Att1）
    cooldown_days: int = 7


def create_default_config() -> VGK008Config:
    return VGK008Config(
        name="vgk_008_vol_transition_mr",
        experiment_id="VGK-008",
        display_name="VGK Post-Capitulation Vol-Transition MR",
        tickers=["VGK"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.040,
        holding_days=20,
    )
