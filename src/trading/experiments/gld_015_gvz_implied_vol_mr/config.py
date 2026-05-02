"""
GLD GVZ Implied-Volatility Forward-Looking Regime-Gated MR (GLD-015)

實驗動機：
- GLD-014 Att2 為當前全域最優（min(A,B) Sharpe 0.49，Part A 0.49 / Part B 6.56）。
- GLD-014 文件明確指出「GLD 結構性 Sharpe 上限約 0.50」——pullback+WR 訊號集
  已接近捕捉所有真實 MR 機會，過濾器主要作用為提升 WR 而非絕對報酬放大。
- cross_asset_lessons.md lesson #24（forward-looking implied volatility derivative）
  明確列出未驗證假設：「**^GVZ 對 GLD/SIVR/GDX MR 過濾（GLD 已飽和於 0.49，
  ^GVZ 可能突破）**」。
- TLT-013 Att1 已驗證 ^MOVE level filter 在 TLT 上突破 BB-width regime gate 的
  0.12 結構性上限（min(A,B) 0.12→0.14，+17%）；XLU-013 Att2 進一步驗證
  ^MOVE DIRECTION (3d change) filter 在 XLU 突破 baseline（min(A,B) 0.75→1.59，
  +112%）。

嘗試方向（repo 首次以 ^GVZ 作為 regime gate，repo 第 3 次 implied-vol regime gate
跨資產移植）：
- ^GVZ = CBOE Gold ETF Volatility Index（30 天黃金 ETF 隱含波動率，數據自 2008-）
- forward-looking 結構：option price 反映未來預期，與 GLD-012/014 的 backward-looking
  pullback / WR / 2DD floor 等 realized 維度正交。
- 假設：GLD 的殘餘 Part A SLs 集中在「黃金市場前瞻波動上升」regime（如 2021-02
  reflation rotation、2022-04 Fed pivot tightening、2022-09 Jackson Hole hawkish）；
  ^GVZ regime gate 可作為 SL filter 而不影響 winners 集合。

Trade-level 分析（GLD-014 Att2 殘餘 4 筆失敗交易）：
| Date        | Result          | GVZ   | GVZ_10d | GVZ_5d  | Pattern                |
|-------------|-----------------|-------|---------|---------|------------------------|
| 2021-02-04  | Stop -4.10%     | 19.30 |  +0.45  | -0.08   | post-spike rebound     |
| 2022-04-25  | Stop -4.10%     | 19.47 |  +1.10  | +0.40   | Fed pivot tightening   |
| 2022-09-01  | Stop -4.10%     | 17.80 |  +2.44  | +2.23   | Jackson Hole hawkish   |
| 2023-05-17  | Expiry -1.32%   | 16.99 |  -1.71  | -1.38   | (calm regime, expiry)  |

關鍵發現：3 筆 Part A SLs 之 ^GVZ_10d_change 全部 > +0.40（rising vol regime），
而 9 筆 Part B winners 之 ^GVZ_10d_change 全部 <= -0.20（falling vol regime）。
^GVZ 10d 變化提供結構性 separator。

Part A TPs 分布（12 筆，^GVZ_10d_change）：
  -0.31, +30.43*, -5.97, -1.57, +0.17, -0.37, -0.07, +1.37, +1.52, -0.32, -2.02, +2.87
  *2020-03-18 COVID 極端飆升期

注意 4/12 Part A TPs（2020-03-18 / 2022-05-13 / 2022-07-14 / 2023-09-28）有
^GVZ_10d > +1.0，純 DIRECTION 過濾將誤殺；需配合 LEVEL 或 chain shift effect。

設計理念：
- 沿用 GLD-014 Att2 的 pullback + WR + ClosePos + 1d_floor + 2d_floor 框架
  （已驗證有效），疊加 ^GVZ 過濾（regime gate）
- ^GVZ 三種過濾維度（lesson #24 v2）：
  1. **LEVEL**: GVZ Close <= max_gvz_level（filter 持續高 vol regime）
  2. **DIRECTION (Nd change)**: GVZ Nd_change <= max_gvz_change（filter 上升 vol regime）
  3. **COMBINED**: 兩者同時或擇一（取決於資產）

Cross-asset hypothesis（待驗證）：
- ^GVZ 對 GLD 是否類似 ^MOVE 對 TLT（LEVEL binding）或 ^MOVE 對 XLU（DIRECTION binding）
- GLD 為「商品 + safe-haven」雙重屬性 ETF，與 TLT（rate-direct）和 XLU（rate-indirect）
  皆不同；^GVZ 維度選擇可能需獨立校準
- 跨資產延伸：若 ^GVZ 對 GLD 有效，可移植至 SIVR / GDX / SLV 等其他金屬 ETF
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLD015Config(ExperimentConfig):
    """GLD-015 GVZ Implied-Vol Regime-Gated MR 參數

    迭代計畫（三次迭代）：
      Att1 (max_gvz_level only, LEVEL filter, port TLT-013 Att1 pattern)
      Att2 (GVZ Nd change <= threshold, DIRECTION filter, port XLU-013 Att2 pattern)
      Att3 (Combined LEVEL + DIRECTION, or refined threshold)
    """

    # 進場指標（沿用 GLD-014 Att2 全域最優框架）
    pullback_lookback: int = 20
    pullback_threshold: float = -0.03  # 回檔 ≥3%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80
    close_position_threshold: float = 0.4
    cooldown_days: int = 7

    # GLD-014 Att2 capitulation-strength filters
    twoday_return_floor: float = -0.005  # 2d 累計跌幅 ≤ -0.5%
    oneday_return_floor: float = -0.003  # 1d 跌幅 ≤ -0.3%

    # ^GVZ forward-looking implied vol regime gate（GLD-015 核心新增）
    # Att1 (LEVEL filter, max_gvz_level=20.0): min(A,B) 0.30 REJECT — over-filters
    #   Part A 15/73.3% WR/Sharpe 0.30 / Part B 6/100% WR/Sharpe 5.39 (lost 3 winners)
    # Att2 ★ (DIRECTION filter, 10d change <= +0.40): min(A,B) **0.76** SUCCESS
    gvz_ticker: str = "^GVZ"
    use_gvz_level_filter: bool = False  # Att2: disable LEVEL
    max_gvz_level: float = 999.0
    use_gvz_direction_filter: bool = True  # Att2: enable DIRECTION
    gvz_direction_lookback: int = 10  # Att2 ★: 10d lookback
    max_gvz_direction_change: float = 0.40  # Att2 ★: GVZ 10d change <= +0.40


def create_default_config() -> GLD015Config:
    return GLD015Config(
        name="gld_015_gvz_implied_vol_mr",
        experiment_id="GLD-015",
        display_name="GLD GVZ Implied-Vol Regime-Gated MR",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 GLD-014）
        stop_loss=-0.04,  # -4.0%（同 GLD-014）
        holding_days=20,  # 20 天（同 GLD-014）
    )
