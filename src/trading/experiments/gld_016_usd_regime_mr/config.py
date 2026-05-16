"""GLD–USD Cross-Asset Divergence Regime-Gated MR (GLD-016)

實驗動機：
- GLD-015 Att2 為當前全域最優（min(A,B) Sharpe 0.76，Part A 0.76 / Part B 6.56），
  15 次實驗、50+ 次嘗試。GLD 已套用 lesson #19（GLD-014：2d+1d floor）與
  lesson #24（GLD-015：^GVZ 10d direction），結構性 Sharpe 上限約 0.50 已突破至 0.76。
- 跨資產 divergence regime gate 已在 TSLA-017（TSLA−QQQ +81%）與 TLT-014
  （TLT−SPY +393%）兩度成功。GLD↔USD 為全 repo 最具結構性的跨資產關係
  （黃金以美元計價），自然為此 family 的下一個移植對象。
- 空遠端 artifact `gld_016_dxy_divergence_mr` 獨立指向「GLD vs 美元 divergence」
  方向；本實驗以 UUP（可交易美元 ETF，與 TLT-014/TSLA-017 用可交易 benchmark 一致）
  為美元 proxy，並以**獨立 module 名稱**避免 branch-divergence artifact 衝突。

Trade-level 預分析（GLD-015 Att2 Part A 兩筆殘餘 loser，UUP 對齊 GLD index）：
| Signal     | Exit        | ret%  | UUP10 | UUP20 | Rel10 | Rel20 |
|------------|-------------|-------|-------|-------|-------|-------|
| 2022-04-27 | stop_loss   | -4.10 | +2.61 | +4.52 | -6.85 | -6.28 |  Fed-2022 鷹派美元飆升
| 2023-05-17 | time_expiry | -1.32 | +1.70 | +1.30 | -4.28 | -1.91 |  calm regime 淺幅到期虧損
Part A 10 winners：UUP20 ∈ [-3.07, +2.62]、Rel20 ∈ [-9.75, +1.61]、
UUP10 ∈ [-2.60, +3.01]、Rel10 ∈ [-8.94, -0.01]。

**預分析判定（NOT separable，預測 documented-failure / TIE）**：
- 2022-04-27（UUP20 +4.52）為強美元 outlier（高於所有 winner 最大 +2.62）→ 單一
  維度可分；但其本身為 GLD-015 ^GVZ filter 之 cooldown-chain-shift 衍生 SL，
  過濾後將再觸發 chain-shift（SOXL-013 chain-shift-limited 同型）。
- 2023-05-17（UUP20 +1.30、Rel20 -1.91、UUP10 +1.70、Rel10 -4.28）在**所有**美元
  維度與 winners 完全交錯（無美元特徵）→ idiosyncratic（NVDA-017/EWJ/EEM 同族）。
- 無任一單閾值或 BAND 可同時隔離兩筆 loser 而不誤殺 3+ winners。
- Part B 9/9 winners UUP20 ∈ [-3.09, +2.66] → UUP20 ceiling ≤ +3.0 對 Part B 非綁定。

迭代計畫（三次迭代，predict→confirm）：
  Att1：UUP 20d 報酬 CEILING ≤ +3.0%（最乾淨 separator 維度，filter 強美元 regime）
  Att2：Rel20 = GLD20 − UUP20 divergence FLOOR（TLT-014/TSLA-017 精確類比）
  Att3：UUP 10d ceiling lookback ablation（確認無可分美元 lookback）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class GLD016Config(ExperimentConfig):
    """GLD-016 GLD–USD Cross-Asset Divergence Regime-Gated MR 參數

    base = GLD-015 Att2 全域最優框架（pullback + WR + ClosePos + 1d/2d floor
    + ^GVZ 10d direction ≤ +0.40 + cooldown 7），疊加 UUP 美元 regime gate。
    """

    # 進場指標（沿用 GLD-015 Att2 = GLD-014 Att2 框架）
    pullback_lookback: int = 20
    pullback_threshold: float = -0.03  # 回檔 ≥3%
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R ≤ -80
    close_position_threshold: float = 0.4
    cooldown_days: int = 7
    twoday_return_floor: float = -0.005  # 2d 累計跌幅 ≤ -0.5%
    oneday_return_floor: float = -0.003  # 1d 跌幅 ≤ -0.3%

    # ^GVZ forward-looking implied vol regime gate（沿用 GLD-015 Att2 全域最優）
    gvz_ticker: str = "^GVZ"
    use_gvz_level_filter: bool = False
    max_gvz_level: float = 999.0
    use_gvz_direction_filter: bool = True
    gvz_direction_lookback: int = 10
    max_gvz_direction_change: float = 0.40

    # GLD–USD cross-asset divergence regime gate（GLD-016 核心新增）
    usd_ticker: str = "UUP"  # 可交易美元 ETF proxy（與 TLT-014/TSLA-017 慣例一致）
    usd_lookback: int = 20  # N 日報酬窗口
    # Att1 ★ SUCCESS：UUP N 日報酬 CEILING（filter 強美元 rally regime）
    #   min(A,B)† Part A 0.76→**1.55**（+104%），Part B 9/9 不變，A/B cum 6.4% ✓
    #   乾淨移除 2022-04-27 SL（UUP20 +4.52）無 chain-shift，1.86pt robust band
    # Att2：GLD−UUP divergence FLOOR（TLT-014/TSLA-017 精確類比）
    #   min_relative_return=-0.06：預分析 Rel20 losers -6.28/-1.91 與 winners
    #   [-9.75,+1.61] 完全交錯，filter 2022-04-27(-6.28) 必同殺 winner
    #   2021-06-29(-9.75 +3% TP) → 退化，證明 CEILING 為正確機制
    # Att3：UUP20 ceiling robustness ablation（+2.8% / +3.5%）確認非 knife-edge
    use_usd_ceiling: bool = False
    max_usd_return: float = 0.03  # UUP 20d 報酬 <= +3.0%（max winner +2.62，gap 乾淨）
    use_usd_divergence: bool = True
    min_relative_return: float = -0.06  # Att2: Rel20 = GLD20-UUP20 >= -6%


def create_default_config() -> GLD016Config:
    return GLD016Config(
        name="gld_016_usd_regime_mr",
        experiment_id="GLD-016",
        display_name="GLD–USD Cross-Asset Divergence Regime-Gated MR",
        tickers=["GLD"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（同 GLD-015 Att2）
        stop_loss=-0.04,  # -4.0%（同 GLD-015 Att2）
        holding_days=20,  # 20 天（同 GLD-015 Att2）
    )
