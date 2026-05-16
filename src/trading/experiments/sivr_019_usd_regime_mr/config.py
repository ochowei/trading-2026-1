"""SIVR–USD Cross-Asset Divergence Regime-Gated MR (SIVR-019)

實驗動機：
- SIVR-018 Att3 為當前全域最優（min(A,B)† 1.41，Part A 5 TPs zero-var /
  Part B 1.41 binding），18 次實驗、49+ 次嘗試。SIVR 已套用 RSI hook
  divergence（SIVR-015）與 lesson #19 ATR ceiling + 3d floor combo（SIVR-018）。
- 跨資產 divergence regime gate 已 3-for-3（TSLA-017 TSLA−QQQ +81% /
  TLT-014 TLT−SPY +393% / GLD-016 GLD−USD +104%）。記憶層「metals vs
  USD/UUP — SIVR/GDX still untried」明確指向銀↔美元為此 family 下一個
  待測移植對象（白銀與黃金同以美元計價）。
- 空遠端 artifact `sivr_019_gvz_direction_mr` 為 branch-divergence artifact
  （僅 __pycache__、無 .py），本實驗以**獨立 module 名稱**
  `sivr_019_usd_regime_mr` 建立，並直接移植 GLD-016 已驗證之 UUP regime
  gate 機制（可交易美元 ETF proxy，與 TLT-014/TSLA-017 慣例一致）。

Trade-level 預分析（signal-day UUP 20d/10d 報酬 + Rel20 = SIVR20 − UUP20）：

SIVR-015 Att1（RSI-hook base，Part A binding Sharpe 0.48，2 殘餘 SL）：
| Signal     | Exit       | ret%  | UUP20 | UUP10 | Rel20  |
|------------|------------|-------|-------|-------|--------|
| 2020-11-30 | target     | +3.50 | -2.17 | -0.84 |  -2.12 |
| 2021-06-21 | time_expiry| +1.42 | +1.98 | +2.07 |  -7.59 |
| 2021-09-21 | stop_loss  | -3.64 | +0.16 | +0.64 |  -4.81 |  ← SL（flat USD）
| 2022-05-11 | target     | +3.50 | +3.69 | +1.05 | -18.93 |
| 2022-07-13 | target     | +3.50 | +2.60 | +3.37 | -12.03 |
| 2023-02-07 | stop_loss  | -3.64 | +0.61 | +1.64 |  -6.87 |  ← SL（flat USD）
| 2023-06-23 | target     | +3.50 | -0.42 | -0.14 |  -2.29 |
| 2023-08-10 | target     | +3.50 | +3.41 | +1.06 | -11.86 |

SIVR-018 Att3（current global optimum，Part B binding 1.41）：
  Part A 5 TPs UUP20 ∈ {-2.17, +3.69, +3.09, -0.42, +3.41}（3/5 winners
  在強美元 +3.0~+3.7）
  Part B：2024-05-02 TP(UUP20 +1.48) / 2024-08-07 TP(-1.31) /
          2024-11-12 time_expiry 0.00%(UUP20 +3.04)  ← Part B drag

**預分析判定（NOT separable，預測 documented-failure）**：
- SIVR-015 Att1 兩筆 Part A SL（2021-09-21 / 2023-02-07）UUP20 = +0.16 /
  +0.61 為 **flat-USD**，深陷 winner 雲（winners UUP20 ∈ [-2.17, +3.69]），
  在 UUP20 / UUP10 / Rel20 **每一維度皆與 winners 完全交錯** → 銀的殘餘
  MR 失敗為**白銀產業性 idiosyncratic**（2021-09 Fed taper / 2023-02 SVB
  pre-shock 之工業需求/供給衝擊），非美元 regime 驅動（EWJ/EEM/TSM 同族）。
- SIVR-018 Att3 Part A 5 TPs 中 3 筆（2022-05-11 +3.69 / 2022-07-14 +3.09
  / 2023-08-10 +3.41）落在**強美元** regime（白銀於 2022 通膨/2023 銀行
  危機強勢 DESPITE 強勢美元）。任何能濾掉 Part B drag（2024-11-12 UUP20
  +3.04）的 UUP ceiling 必同時誤殺此 3 Part A winners → 無單一 ceiling
  可同時保 Part A 5 TPs 並移除 Part B drag。
- 對比 GLD-016 SUCCESS：GLD 唯一 binding Part A SL（2022-04-27 UUP20
  +4.52）為**清楚的強美元 outlier**（高於所有 GLD winner 上緣 +2.62）→
  乾淨可分。**核心跨資產差異：黃金為貨幣純資產（USD-inverse，可分）；
  白銀約 50% 工業需求（drawdown 由工業/供給驅動，與美元脫鉤，最佳 MR
  winner 甚至發生於強美元期）→ divergence regime gate family 要求
  「貨幣純」結構對立資產，非「任一金屬 vs 美元」。**

迭代計畫與結果（三次迭代，predict→confirm，SOXL-013/CIBR-016/EWJ-006 同型，
**三次全部 FAIL/REJECT vs SIVR-018 Att3 min(A,B)† 1.41，預分析預測完全命中**）：
  Att1（headline）：UUP 20d CEILING ≤ +3.0%（GLD-016 Att1 已驗證 config
        直接移植）於 SIVR-018 Att3 base。**CONFIRMED FAIL**：Part A
        5→**2** TPs（誤殺 3 強美元 winners 2022-05-11 UUP20 +3.69 /
        2022-07-14 +3.09 / 2023-08-10 +3.41）、Part B 3→2 TPs。雙 part
        zero-var n=2，**非外科式 60% Part A winner attrition →
        REJECT**（EEM-016 Att3 / CIBR-016 Att2 degenerate-notch 慣例）。
  Att2：Rel20 = SIVR20 − UUP20 divergence FLOOR（TLT-014/TSLA-017/
        GLD-016-Att2 精確類比）於 SIVR-018 Att3 base。**CONFIRMED FAIL**：
        FLOOR ≥ -6%/-10% → Part A 5→2 TPs（殺深 divergence winners），
        Part B **保留 2024-11-12 EXP-0% drag 並誤殺 2024-08-07 TP** →
        Part B Sharpe 1.41→**1.00**（方向反轉）；FLOOR ≥ -13% Part A
        5→3、Part B 不變（drag 仍在），無改善。Rel20 non-separable。
  Att3：UUP 20d CEILING 於 SIVR-015 Att1 RSI-hook base（無 ATR/3d 過濾）。
        **CONFIRMED FAIL**：≤+3.0% Part A Sharpe 0.48→**0.24**、
        ≤+1.0% **-0.02**、≤+0.5% 0.33——**2 殘餘 Part A SL
        （2021-09-21 UUP20 +0.16 / 2023-02-07 +0.61）永不被任何 ceiling
        移除**（flat-USD 在所有 ceiling 之下），ceiling 反而誤殺強美元
        WINNERS，方向完全反轉。確認 SL 為白銀工業 idiosyncratic。

**核心跨資產規則（divergence regime gate family v4，family 首次 documented
failure）**：family 3-for-3（TSLA-017 stock−index / TLT-014 bond−equity /
GLD-016 gold−USD）之成功標的皆有**單一驅動的純粹結構對立**（黃金=純貨幣
USD-inverse、TLT=純利率、TSLA vs 自身指數）。**白銀約 50% 工業需求 → MR
drawdown 由工業/供給衝擊驅動（2021-09 Fed taper、2023-02 SVB pre-shock）且
與美元脫鉤——白銀最佳 MR winners 常發生於強美元期（2022 通膨、2023 銀行
危機）**。故 USD ceiling / divergence floor 濾掉的是真 winners 而非 binding
losers（後者落在 flat-USD 與 winners 在每一美元維度交錯，EWJ/EEM/TSM
idiosyncratic-SL 同型）。**family 適用前提精煉：結構對立資產須為「驅動純粹」
（單因子 inverse），非僅「任一金屬 vs 美元」**——更正記憶層「metals vs
USD/UUP — SIVR/GDX still untried」：SIVR 已試且 NOT separable；金屬適用性
為**黃金特定（貨幣純粹性）**，非泛金屬；GDX（金礦股，equity-levered）預期
亦因 equity beta 污染失敗。SIVR-018 Att3 仍為全域最優（19 實驗、52+ 嘗試）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVR019Config(ExperimentConfig):
    """SIVR-019 SIVR–USD Cross-Asset Divergence Regime-Gated MR 參數

    base = SIVR-018 Att3 全域最優框架（pullback 7-15% + WR ≤ -80 + RSI(14)
    bullish hook + ATR(5)/ATR(20) ≤ 1.20 + Ret_3d ≤ -1.0%），疊加 UUP
    美元 regime gate。Att3 透過 flag 切換為 SIVR-015 Att1 base（關閉
    ATR/3d 過濾）。
    """

    # 進場指標（沿用 SIVR-005 / SIVR-015 / SIVR-018 框架）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 ≥ 7%
    pullback_cap: float = -0.15  # 回檔 ≤ 15%（過濾極端崩盤）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # RSI(14) bullish hook（SIVR-015 Att1）
    use_rsi_hook: bool = True
    rsi_period: int = 14
    rsi_hook_lookback: int = 5
    rsi_hook_delta: float = 3.0
    rsi_hook_max_min: float = 35.0

    # ATR ratio CEILING（SIVR-018 Att3，Att3 迭代關閉以還原 SIVR-015 base）
    use_atr_band: bool = True
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_floor: float = 0.0  # disabled
    atr_ratio_ceiling: float = 1.20

    # 3-day return floor（SIVR-018 Att3，Att3 迭代關閉以還原 SIVR-015 base）
    use_3d_floor: bool = True
    three_day_floor: float = -0.01  # Ret_3d ≤ -1.0%

    # SIVR–USD cross-asset divergence regime gate（SIVR-019 核心新增）
    usd_ticker: str = "UUP"  # 可交易美元 ETF proxy（與 TLT-014/TSLA-017 一致）
    usd_lookback: int = 20  # N 日報酬窗口
    # Att1（headline，GLD-016 Att1 已驗證 config 直接移植）：UUP 20d 報酬
    #   CEILING ≤ +3.0%。預分析預測 Part A 崩潰——3/5 Part A winners
    #   （2022-05-11 UUP20 +3.69 / 2022-07-14 +3.09 / 2023-08-10 +3.41）落在
    #   強美元 regime，ceiling 誤殺 → 白銀工業性脫鉤美元（vs GLD 貨幣純）。
    # Att2：Rel20 = SIVR20 − UUP20 divergence FLOOR（TLT-014/TSLA-017/
    #   GLD-016-Att2 精確類比，min_relative_return=-0.10）。預分析預測
    #   non-separable（Part A winner Rel20 ∈ [-2.12, -18.93] 完全交錯）。
    # Att3：UUP 20d CEILING 於 SIVR-015 Att1 base（use_atr_band=False,
    #   use_3d_floor=False）。預測失敗：2 殘餘 Part A SL（2021-09-21 /
    #   2023-02-07）UUP20 +0.16/+0.61 為 flat-USD，與 winners 交錯。
    use_usd_ceiling: bool = True
    max_usd_return: float = 0.03  # UUP 20d 報酬 ≤ +3.0%（GLD-016 已驗證值）
    use_usd_divergence: bool = False
    min_relative_return: float = -0.99  # 停用時設極寬

    # 冷卻（沿用 SIVR-005 / SIVR-018）
    cooldown_days: int = 10


def create_default_config() -> SIVR019Config:
    return SIVR019Config(
        name="sivr_019_usd_regime_mr",
        experiment_id="SIVR-019",
        display_name="SIVR–USD Cross-Asset Divergence Regime-Gated MR",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（同 SIVR-018）
        stop_loss=-0.035,  # -3.5%（同 SIVR-018）
        holding_days=15,  # 15 天（同 SIVR-018）
    )
