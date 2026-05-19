"""
EWJ ^VIX Forward-Looking Implied-Volatility Regime-Gated MR (EWJ-007)

實驗動機（problem statement）：
- EWJ-005 Att2 ★ 為當前全域最優（min(A,B)† 0.70，5 次實驗 15 次嘗試）：
  BB(20,1.5) 下軌 + 10日回檔上限 -7% + WR(10)<=-80 + ClosePos>=40%
  + ATR(5)/ATR(20)>1.15 + 1d floor <= -0.5% capitulation-strength filter，
  TP+3.5%/SL-4.0%/20d/cd7。
- Part A 9 訊號 8 勝（WR 88.9%）僅殘留 **1 筆 SL：2022-09-01**（訊號日，
  進場 2022-09-02 @ 48.38 → 停損 2022-09-07 @ 46.40，-4.10%）。
  此 SL 為 EWJ-005 唯一 Part A 改進空間（其餘 8 筆 + Part B 4/4 全勝）。
- 2022-09-01 失敗結構：Powell Jackson Hole（2022-08-26）鷹派演說後
  broad-market 進入「vol acceleration regime」，^VIX 自 8 月底約 21 持續
  攀升至 9 月初高 20s。1d floor 無法過濾此 SL（1d -1.19% 深於 -0.5% 通過），
  2DD floor 亦無乾淨切點（EWJ-005 Att1 已驗證 2DD 區分力弱）。
  假設：此 SL 並非 EWJ 自身 capitulation 不足，而是「global risk-off /
  日圓套息平倉」加速期——^VIX 急升時外資撤出日股，無論 EWJ 自身
  capitulation 結構如何皆無法 V-bounce。

跨資產脈絡（lesson #24 family — forward-looking implied vol regime gate）：
- TLT-013 Att1 ^MOVE LEVEL CAP <= 130 → +17%（rate-driven，首次任何資產）
- XLU-013 Att2 ^MOVE 3d DIRECTION <= +5.0 → +112%（DIRECTION 維度首次發現）
- GLD-015 Att2 ^GVZ 10d DIRECTION <= +0.40 → +55%（commodity safe-haven）
- USO-025 Att3 ^OVX 3d DIRECTION → +58%（commodity event-driven）
- XBI-017 Att1 ^VIX BANDS exclude (17,22] → +39%（healthcare sector ETF）
- FCX-015 Att2 ^VIX FLOOR > 14.0 → +123%（mining single stock breakout）
- NVDA-018 ^VXN（high-vol AI 個股 + MBPC）→ FAIL（適用邊界：asset class
  + strategy framework 雙條件）
- EWZ-008 ^VIX（EM single-country ETF + MR）→ FAIL（DIRECTION 非綁定、
  LEVEL 亦無乾淨切點，EM 商品/政治雙驅動殘餘 SL 結構分散）

EWJ 在此族群中為「**首次 ^VIX 應用於非美已開發單一國家寬基股票 ETF**」。
lesson #24 規則 #2 資產↔implied-vol 對應：stock ETFs → ^VIX。EWJ 為日本
寬基股票 ETF（非 EM、非商品、非利率），與 EWZ-008 失敗結構不同：EWJ-005
Att2 殘餘僅 1 筆 SL 集中於單一失敗模式（global vol-acceleration），框架為
MR（lesson #24 已驗證 6 次 MR 框架成功），符合「殘餘 SLs 集中單一失敗模式
+ MR 框架」適用邊界（對照 NVDA-018 / EWZ-008 失敗側）。

設計理念：
- 沿用 EWJ-005 Att2 完整框架（6 條件 + 出場 + 冷卻全部不變）。
- 疊加 ^VIX 過濾器作為**獨立第七維度**：^VIX N 日累計變化
  <= max_vix_change（DIRECTION 維度，篩除 vol-acceleration regime）。
- 可選 LEVEL CAP（max_vix_level，預設 999 停用）作為 Att3 備援維度。
- 僅新增 1 個過濾條件以隔離 ^VIX 邊際貢獻。

迭代結果（3 次迭代全部 FAILED / REJECTED vs EWJ-005 Att2 min(A,B)† 0.70）：
- Att1（^VIX 3d DIRECTION <= +5.0，XLU-013 / USO-025 sweet spot 直接移植）：
  Part A 7/6 勝/WR 85.7%/Sharpe **0.60**/cum +10.82% / Part B 4/4 不變 /
  min(A,B) **0.60**（-14%）。VIX-calib log 證實 2022-09-01 SL 之 ^VIX
  3d change = -0.65（vol 持平/微降，非加速），DIRECTION cap 不過濾 SL，
  反而誤殺 winners 2019-05-08（3d +6.53）、2021-07-19（3d +6.17）。
- Att2（^VIX 3d DIRECTION <= +3.0，加嚴，鏡像 EWZ-008 方法論）：
  Part A 5/4 勝/WR 80.0%/Sharpe **0.42**/cum +5.78% / Part B 3/3
  （誤殺 2025-11-18 winner，3d +4.69）/ min(A,B) **0.42**（-40%）。
  加嚴使 DIRECTION 反向誤殺更多 winners，SL 仍保留。
- Att3（^VIX LEVEL CAP <= 25.0，鏡像 EWZ-008 Att3）：Part A 5/5/WR
  100%/nominal Sharpe 2.97 / Part B 3/3 — **nominal 雙零方差 BUT REJECT
  （非外科式 attrition）**：LEVEL CAP <= 25 過濾 SL 2022-09-01（VIX
  25.56）僅靠整片切除 ^VIX > 25 高波動 regime，連帶切除 3 筆最強
  +3.50% TP winners（2020-10-30 VIX 38.02、2022-09-29 VIX 31.84、
  2023-03-15 VIX 26.14）+ 1 筆 Part B winner（2025-03-11 VIX 26.92），
  訊號 Part A 9→5（-44%）/ Part B 4→3（-25%），存活集為 5 筆最弱
  expiry（+0.90~+2.23%），nominal 高 Sharpe 為退化零方差假象，無品質
  區分力（違反 lesson #14 + EEM-016 Att3 非外科式 attrition REJECT 標準）。

核心結構性發現（cross-asset contribution）：
- lesson #24 ^VIX forward-looking implied-vol regime gate 對 EWJ
  **結構性無區分力**。trade-level：唯一綁定 Part A SL 2022-09-01
  （Jackson Hole 鷹派後）之 ^VIX（level 25.56 / 3d -0.65 / 5d +3.78 /
  10d +6.00）在 12 筆 winners 之 ^VIX 分布「每一維度（level / 3d / 5d /
  10d，cap 或 floor）皆居中交錯」，無乾淨 separator。
- EWJ 殘餘失敗為 idiosyncratic 日本特有（BoJ 政策 / 日圓套息 / 出口
  週期），非 global implied-vol regime outlier——與 EWJ-004「日本相對
  強度為事件驅動非結構性」發現平行。
- 精煉 lesson #24 適用邊界：**^VIX gate 對「已開發市場單一國家股票
  ETF」在殘餘 binding SL 為 country-idiosyncratic（非 vol-regime
  isolated）時結構性失敗**——與 EWZ-008（EM ^VIX 失敗，殘餘 SL 非
  vol-isolated）、NVDA-018（^VXN 失敗）同屬「implied-vol gate 需殘餘
  SL 集中於 vol-regime-可區分 失敗模式」邊界家族。
- repo 首次 ^VIX 應用於非美已開發單一國家寬基股票 ETF。EWJ-005 Att2
  仍為全域最優（6 次實驗、18 次嘗試）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWJ007Config(ExperimentConfig):
    """EWJ-007 ^VIX Forward-Looking Implied-Vol Regime-Gated MR 參數"""

    # BB 參數（沿用 EWJ-005 Att2 ★）
    bb_period: int = 20
    bb_std: float = 1.5

    # 崩盤隔離（10日高點回檔上限）
    pullback_lookback: int = 10
    pullback_cap: float = -0.07

    # 品質過濾（沿用 EWJ-005 Att2）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15

    # Capitulation strength filter（沿用 EWJ-005 Att2，1d floor）
    # mode: "1d_floor" | "2dd_floor"
    capitulation_mode: str = "1d_floor"
    capitulation_threshold: float = -0.005

    # ^VIX forward-looking implied vol regime gate（EWJ-007 核心新增）
    vix_ticker: str = "^VIX"
    # DIRECTION：訊號日 ^VIX 之 N 日絕對變化（點數），篩除 vol-acceleration regime
    # Att1 +5.0（XLU-013 / USO-025 sweet spot 直接移植）→ FAILED 0.60
    # Att2 +3.0（加嚴 DIRECTION 假說，鏡像 EWZ-008 方法論）→ FAILED 0.42
    # Att3 DIRECTION 停用（999），改測 LEVEL CAP 維度（鏡像 EWZ-008 Att3）
    vix_direction_lookback: int = 3
    max_vix_change: float = 999.0
    # LEVEL CAP：^VIX 收盤值 <= max_vix_level（999.0 表停用）
    # Att3 ^VIX <= 25.0（測試 LEVEL 是否能 surgical 過濾 2022-09-01 SL VIX=25.56）
    max_vix_level: float = 25.0

    cooldown_days: int = 7


def create_default_config() -> EWJ007Config:
    return EWJ007Config(
        name="ewj_007_vix_implied_vol_mr",
        experiment_id="EWJ-007",
        display_name="EWJ ^VIX Forward-Looking Implied-Vol Regime-Gated MR",
        tickers=["EWJ"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 EWJ-005）
        stop_loss=-0.040,  # -4.0%（同 EWJ-005）
        holding_days=20,
    )
