"""
EWJ ^VIX Forward-Looking Implied-Volatility Regime-Gated MR (EWJ-006)

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

迭代設計：
- Att1 ★：^VIX 3d change <= +5.0（XLU-013 / USO-025 sweet spot 直接移植）
- Att2：依 Att1 calibration log 調整 lookback（3/5/10d）與閾值，
  surgical 過濾 2022-09-01 SL 而保留 8 Part A + 4 Part B winners
- Att3：sweet-spot 收斂 / LEVEL CAP 備援

跨資產貢獻（若 SUCCESS）：
- repo 首次 ^VIX 應用於非美已開發單一國家寬基股票 ETF（EWJ）
- 擴展 lesson #24 family 適用邊界至已開發市場單一國家股票 ETF 類別
- 與 EWZ-008（EM 失敗）/ NVDA-018（高波動個股失敗）對照精煉適用邊界
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWJ006Config(ExperimentConfig):
    """EWJ-006 ^VIX Forward-Looking Implied-Vol Regime-Gated MR 參數"""

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

    # ^VIX forward-looking implied vol regime gate（EWJ-006 核心新增）
    vix_ticker: str = "^VIX"
    # DIRECTION：訊號日 ^VIX 之 N 日絕對變化（點數），篩除 vol-acceleration regime
    # Att1 ★ +5.0（XLU-013 / USO-025 sweet spot 直接移植）
    vix_direction_lookback: int = 3
    max_vix_change: float = 5.0
    # LEVEL CAP：^VIX 收盤值 <= max_vix_level（999.0 表停用，Att3 備援維度）
    max_vix_level: float = 999.0

    cooldown_days: int = 7


def create_default_config() -> EWJ006Config:
    return EWJ006Config(
        name="ewj_006_vix_implied_vol_mr",
        experiment_id="EWJ-006",
        display_name="EWJ ^VIX Forward-Looking Implied-Vol Regime-Gated MR",
        tickers=["EWJ"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 EWJ-005）
        stop_loss=-0.040,  # -4.0%（同 EWJ-005）
        holding_days=20,
    )
