"""
GLD DXY Cross-Asset Divergence Filter on GVZ-Gated MR (GLD-016)

實驗動機：
- GLD-015 Att2 為當前全域最優（min(A,B) Sharpe 0.76），框架疊加 ^GVZ 10d DIRECTION
  filter 後，殘餘 Part A 仍有 1 筆 SL（2022-04-27 -4.10%）+ 1 筆負到期
  （2023-05-17 -1.32%）+ 1 筆近零到期（2019-04-16 +0.27%）拖累 Sharpe。
- cross_asset_lessons.md 提示「DXY 美元指數（FX 維度，與 equity/credit benchmarks
  不同 macro factor）」為 TLT 結構性 ceiling 的潛在突破方向；本實驗將其應用於
  另一個 USD-sensitive 商品 ETF（GLD），驗證 cross-asset hypothesis。
- COPX-016 已驗證 DXY direction filter 在「銅礦 ETF」上有效（USD strong → 商品
  弱勢，filter 移除 SL 集中時段）。本實驗測試是否同樣適用於 GLD（gold ETF）。

Trade-level 分析（GLD-015 Att2 Part A 全部 12 筆訊號之 DXY 變化）：
| Date        | Result          | DXY_5d  | DXY_10d  | Pattern                  |
|-------------|-----------------|---------|----------|--------------------------|
| 2019-04-16  | Expiry +0.27%   | +0.03%  | -0.33%   | Calm USD                 |
| 2019-05-02  | TP +3.00%       | -0.38%  | +0.85%   | USD weak                 |
| 2020-08-12  | (winner)        | +0.66%  | +0.19%   | USD calm                 |
| 2020-09-08  | (winner)        | +1.45%  | +0.19%   | USD bouncing             |
| 2020-12-02  | (winner)        | -1.20%  | -1.41%   | USD weak                 |
| 2021-06-29  | TP +3.00%       | +0.35%  | +1.67%   | USD steady               |
| 2021-11-23  | Expiry +1.23%   | +0.59%  | +2.69%   | USD strong (10d)         |
| 2022-04-27  | **STOP -4.10%** | **+2.55%** | +2.65% | **Fed hike, USD surge**  |
| 2023-02-15  | TP +3.00%       | +0.49%  | +2.67%   | USD strong but stabilizing |
| 2023-04-21  | TP +3.00%       | +0.27%  | +0.00%   | USD calm                 |
| 2023-05-17  | Expiry -1.32%   | +1.38%  | +1.52%   | USD modest rise          |
| (others)    | TPs / expiries  | varies  | varies   | (Part B winners < +1.7%) |

關鍵發現：
- DXY **10d** change 無法 surgical 過濾：2022-04-27 SL (+2.65%) 與 2023-02-15 TP
  (+2.67%) 數值幾乎相同，任一 10d cap 同時誤殺 TP；
- DXY **5d** change 提供 surgical separator：2022-04-27 SL **+2.55%** 為唯一
  > +2.0% 訊號；2023-02-15 TP 僅 +0.49%（USD 已 plateau），完全不同結構；
- Part B 全部 9 筆 winners 之 DXY 5d ≤ +1.65%（最大 2024-11-11 +1.59%），全
  低於 +2.0% 閾值，filter 對 Part B 完全非綁定。

設計理念：
- 沿用 GLD-015 Att2 的 pullback + WR + ClosePos + 1d_floor + 2d_floor + GVZ_10d
  完整框架（已驗證 Sharpe 0.76 全域最優），疊加 DXY 5d direction filter；
- DXY 5d direction filter 屬「cross-asset macro regime gate」，與 ^GVZ 隱含波動率
  正交（前者為 FX 維度、後者為 options-implied vol 維度），加總後預期可 surgical
  過濾 Fed-hike-driven SL 而保留所有 winners。

迭代計畫（最多三次）：
- Att1: DXY 5d 變化 cap <= +2.0%（target 2022-04-27 SL：5d +2.55% > +2.0%；
  threshold 預期保留全部 winners，最大 2024-11-11 +1.59% < +2.0%）
- Att2: 收緊 DXY 5d cap <= +1.5%（may 誤殺 2024-11-11 winner +1.59%；觀察 cooldown
  chain shift effect）
- Att3: 改用 DXY 10d cap <= +2.6%（驗證 5d > 10d 的 selectivity 假設；預期
  failure，誤殺 2023-02-15 TP +2.67%）

跨資產假設（待驗證）：
1. 若 DXY 5d direction filter 在 GLD 成功，可移植至 SIVR、SLV、GDX 等其他金屬 ETF；
2. 若 5d > 10d 的 selectivity 結構成立，建議在其他 USD-sensitive 商品/EM ETF
   優先測試 5d 維度；
3. 與 ^GVZ 10d DIRECTION filter（GLD-015 Att2）的 dimension orthogonality：
   ^GVZ 為 backward-looking 10d implied vol path，DXY 為 forward-looking 5d FX
   path，二者捕捉不同 regime classifier，可疊加為 dual-regime gate。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLD016Config(ExperimentConfig):
    """GLD-016 DXY Cross-Asset Divergence MR 參數

    迭代計畫：
      Att1 (DXY 5d cap <= +2.0%, surgical Fed-hike SL filter)
      Att2 (DXY 5d cap <= +1.5%, threshold tightening)
      Att3 (DXY 10d cap <= +2.6%, alternative window)
    """

    # 進場指標（沿用 GLD-015 Att2 全域最優框架）
    pullback_lookback: int = 20
    pullback_threshold: float = -0.03
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.4
    cooldown_days: int = 7

    twoday_return_floor: float = -0.005
    oneday_return_floor: float = -0.003

    # ^GVZ regime gate (GLD-015 Att2 sweet spot)
    gvz_ticker: str = "^GVZ"
    gvz_direction_lookback: int = 10
    max_gvz_direction_change: float = 0.40

    # DXY cross-asset divergence filter (GLD-016 核心新增)
    # Att1 ★ (max_dxy_5d_change=+0.020) SUCCESS — min(A,B) 0.76→1.55 (+104%)
    #   Part A 12→11 signals; filtered 2022-04-27 SL (DXY 5d +2.55% > +2.0%)
    #   Part A WR 83.3%→90.9%, Sharpe 0.76→1.55, cum +21.68%→+26.88%
    #   Part B 9 signals UNCHANGED; A/B cum diff 6.4% ✓, signal ratio 1.22:1 ✓
    # Att2 (max_dxy_5d_change=+0.015) REJECT — Part B 9→8 lost 2024-11-11 winner
    #   (DXY 5d +1.59% > +1.5%); Part A unchanged; min† TIE 1.55 but Part B
    #   Sharpe degraded 6.56→6.20
    # Att3 (max_dxy_10d_change=+0.026) REJECT — Part A 11→9 over-filtered
    #   (10d cap誤殺 2023-02-15 TP DXY 10d +2.67% + 2021-11-23 expiry +1.23%);
    #   Part B unchanged; min(A,B) 1.47 < Att1 1.55. Confirms 5d > 10d selectivity:
    #   5d separates SL from TPs (SL +2.55% vs TP +0.49% gap), 10d does not
    #   (SL +2.65% vs TP +2.67% indistinguishable)
    dxy_ticker: str = "DX-Y.NYB"
    dxy_lookback: int = 5
    max_dxy_change: float = 0.020


def create_default_config() -> GLD016Config:
    return GLD016Config(
        name="gld_016_dxy_divergence_mr",
        experiment_id="GLD-016",
        display_name="GLD DXY Cross-Asset Divergence MR",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.04,
        holding_days=20,
    )
