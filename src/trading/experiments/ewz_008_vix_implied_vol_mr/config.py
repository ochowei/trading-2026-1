"""
EWZ ^VIX Forward-Looking Implied-Volatility Regime-Gated MR (EWZ-008)

實驗動機（problem statement）：
- EWZ-007 Att3 ★ 為當前全域最優（min(A,B) 0.95）：1d cap >= -5.0% 作為
  surgical Petrobras filter，僅過濾 2021-02-22 單一 outlier 深跌。
- A/B 平衡未達標：A/B 累計差 40.2%（>30% 目標），Part A 殘留 2 SLs：
  * 2019-03-25（巴西退休金改革擔憂雜訊，後續 -3.74% SL）
  * 2020-01-31（COVID 早期擔憂，後續 -2.50% SL，pre-crash 進場）
  兩者 1d/2d 均不深，無法用 lesson #19 single-day flush 維度過濾不傷害 winners。
- 假設這 2 個 Part A SLs 並非 EWZ 自身 capitulation 不足，而是「broad-market
  vol regime 加速期」EM 撿便宜失敗模式：foreign capital 在 ^VIX 急速攀升期
  從 EM 撤出，無論 EWZ 自身 capitulation 結構如何皆無法 V-bounce。

跨資產脈絡（lesson #24 family v2 候選 — forward-looking implied vol regime gate）：
- TLT-013 Att1 ^MOVE LEVEL CAP <= 130 → +17% Sharpe（首次突破 TLT 0.12 ceiling）
- XLU-013 Att2/Att3 ^MOVE 3d DIRECTION <= +5 → +50%+ Sharpe（首次 DIRECTION 維度）
- GLD-015 Att2 ^GVZ 10d DIRECTION <= -0.7σ → SUCCESS（commodity safe-haven）
- USO-025 Att3 ^OVX 3d DIRECTION <= +4 → +58% Sharpe（commodity event-driven）
- XBI-017 Att1 ^VIX BANDS exclude (17,22) → +39% Sharpe（healthcare ETF）
- FCX-015 Att2 ^VIX FLOOR > 14 → +123% Sharpe（mining single stock breakout）
- NVDA-018（^VXN MBPC）→ FAIL：適用邊界為「殘餘 SLs 集中於單一失敗模式」+
  「策略框架可被 forward-looking vol regime 區分」，多 regime 高波動 AI 個股
  + MBPC 不適用

EWZ 在此族群中為「首次 EM single-country ETF」+「首次商品/政治雙驅動 EM」。
與 NVDA-018 失敗結構不同：EWZ-007 Att3 殘留 2 SLs 集中於「broad-market vol
acceleration regime」單一失敗模式，框架為 MR（lesson #24 已驗證 5 次 MR 框架成功）。

設計理念：
- 沿用 EWZ-007 Att3 完整框架（BB(20,1.5) 下軌 + 10日回檔 [-10%, 0%]
  + WR(10)<=-80 + ClosePos>=0.4 + ATR(5)/ATR(20)>1.10 + 1d cap >= -5.0%
  + TP+5.0%/SL-4.0%/18d/cd10）
- 疊加 ^VIX 過濾器作為**獨立第七維度**：^VIX 3d change <= max_vix_change
- 出場、冷卻、進場其餘條件全部不變，僅新增 1 個過濾條件以隔離 ^VIX
  邊際貢獻

EWZ-007 Att3 Part A 2 SLs 預估 ^VIX 分布（待回測驗證）：
  2019-03-25: ^VIX ~16.5（從 3 日前 ~13.5 急升 +3.0），yield curve inversion
              fear pricing 開端
  2020-01-31: ^VIX ~18.84（從 3 日前 ~16.3 升 +2.5），COVID 初期傳染擴散擔憂

預估 winners ^VIX 3d change 分布：
  EWZ Part A winners 多發生於 ^VIX 中性區（10-15）或下降區（post-panic
  V-bounce），3d change 多落於 -5 至 +2 區間
  Part B winners（2024-2025）^VIX 多在 12-22，3d change 多在 -3 至 +4

**設計取捨**：
- 嚴格 max_vix_change <= +3 → 預期過濾兩個 Part A SLs（3d ~+3 與 ~+2.5 邊界）
  但可能誤殺 winners 中 3d change ~+2 至 +3 的訊號
- 寬鬆 max_vix_change <= +5（XLU-013 / GLD-015 / USO-025 sweet spot 區間）→
  預期僅過濾 2020-01-31（如其 3d change 超過 +5），保留 2019-03-25
- 因此 Att1 採 +5（XLU/USO sweet spot 直接移植）為起點，Att2 收緊 +3，
  Att3 視結果調整甜蜜點

跨資產貢獻：
- repo 第 7 次 lesson #24 family 跨資產驗證、第 5 次 ^VIX 應用於資產
  （前 4 次：XBI BANDS、FCX FLOOR + NVDA-018 ^VXN 失敗 + 此次）
- repo 首次「forward-looking implied vol DIRECTION gate 應用於 EM single-country
  ETF」+「首次應用於商品/政治雙驅動 ETF」
- 與 NVDA-018 失敗對照精煉適用邊界：MR 框架（EWZ）vs MBPC 框架（NVDA）+
  殘餘 SLs 結構（EWZ 集中 vol-acceleration vs NVDA heterogeneous）
- 若 SUCCESS → 擴展 lesson #24 family 適用邊界至 EM 單國 ETF 類別、
  ^VIX 第 3 種變體（DIRECTION，繼 BANDS / FLOOR）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWZ008Config(ExperimentConfig):
    """EWZ-008 ^VIX Forward-Looking Implied-Vol Regime-Gated MR 參數"""

    # BB 參數（沿用 EWZ-007 Att3 ★）
    bb_period: int = 20
    bb_std: float = 1.5

    # 崩盤隔離（10日高點回檔上限）
    pullback_lookback: int = 10
    pullback_cap: float = -0.10

    # 品質過濾（沿用 EWZ-007 Att3）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.10

    # Capitulation strength filter（沿用 EWZ-007 Att3，1d cap surgical Petrobras filter）
    capitulation_mode: str = "1d_cap"
    capitulation_threshold: float = -0.050

    # ^VIX forward-looking implied vol regime gate（EWZ-008 核心新增）
    vix_ticker: str = "^VIX"
    # DIRECTION mode：N 日累計 ^VIX 絕對變化，篩除 vol-acceleration regime
    # Att1 (+5.0) XLU-013 / GLD-015 / USO-025 sweet spot 直接移植 → 非綁定（同 EWZ-007 baseline）
    # Att2 (+3.0) 加嚴假說 → cooldown chain-shift collapse（過濾 2019-08-02 TP 引入 2019-08-15 SL，
    #            兩個殘餘 SLs 仍未過濾 → 確認 DIRECTION 在 EWZ 上無乾淨切點）
    # Att3 改採 LEVEL CAP（^VIX <= 18.0），測試 LEVEL 維度是否能精準過濾
    #     2020-01-31 SL（VIX ~18.84）而保留 2019-03-25 SL（VIX ~16.5）
    vix_direction_lookback: int = 3
    max_vix_change: float = 999.0  # 非綁定（DIRECTION dim 已於 Att2 證明無效）

    # LEVEL CAP：^VIX 收盤值 <= max_vix_level（999.0 表停用）
    # Att3 ★ LEVEL CAP <= 18.0（surgical 過濾 2020-01-31 SL 假設）
    max_vix_level: float = 18.0

    cooldown_days: int = 10


def create_default_config() -> EWZ008Config:
    return EWZ008Config(
        name="ewz_008_vix_implied_vol_mr",
        experiment_id="EWZ-008",
        display_name="EWZ ^VIX Forward-Looking Implied-Vol Regime-Gated MR",
        tickers=["EWZ"],
        data_start="2010-01-01",
        profit_target=0.050,  # +5.0%（同 EWZ-007）
        stop_loss=-0.040,  # -4.0%（同 EWZ-007）
        holding_days=18,
    )
