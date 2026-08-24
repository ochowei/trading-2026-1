"""
USO-XLE Cross-Asset Divergence Regime-Gated MR (USO-026)

實驗動機：
- USO-025 為當前全域最優（min(A,B) Sharpe 0.41，Part A 0.41 / Part B 0.64）
  以 ^OVX 3d DIRECTION 過濾首次突破 USO-013 結構性 0.26 ceiling（+58%）
- Part A 仍殘留 SLs 集中於 OPEC+ 政策日 / 地緣政治衝擊日
- ^OVX 已捕捉 implied volatility regime 但無法區分「USO 自身落後 XLE 板塊」
  的 idiosyncratic crude-specific weakness regime（contango drag、roll yield、
  WTI-vs-Brent 結構差異）

跨資產背景（lesson #20 v3，cross-asset divergence regime gate）：
- TLT-014（2026-05-02）以 TLT vs SPY 20d divergence >= -4% 突破 TLT 結構性
  0.14 ceiling（+393%，repo 首次 cross-asset divergence regime gate using
  equity benchmark）
- TSLA-017（2026-05-07）以 TSLA vs QQQ 20d divergence >= -0.5% 突破 TSLA
  結構性 0.53 ceiling（+81%）
- COPX-014（2026-05-07）3 次失敗（cooldown_days=12 + 訊號密度 ~2/yr +
  BB Squeeze breakout 框架訊號日 Rel 結構偏多）—— **lesson #20 v3 邊界**：
  cross-asset divergence 適用於 MR 框架（capitulation 訊號日已偏弱）但不適用
  於 breakout 框架；同時要求「cooldown 視窗 × 訊號密度」遠 < 1.0
  - USO-026 滿足條件：MR 框架（USO-013 base）✓ + cooldown 10d × 訊號密度
    5/yr ≈ 0.20 << 1.0 ✓

設計理念：
- 沿用 USO-013 完整框架（pullback 7-12% + RSI(2)<15 + 2日跌幅<=-2.5% +
  TP+3.0%/SL-3.25%/10d/cd10）
- 不疊加 USO-025 的 ^OVX filter——目的是隔離 USO-XLE divergence dimension
  的邊際貢獻（與 USO-025 ^OVX 維度的正交性檢驗，類似 TLT-014 vs TLT-013）
- 假設：當 USO 在過去 N 日相對 XLE 嚴重落後（USO 20d - XLE 20d <= -4%），
  反映 crude-specific 衰弱（如 contango 加深、地緣政治對 oil 直接衝擊但
  energy stocks 由其他現金流支撐），此 regime 中 USO MR 訊號更可能被
  續跌覆蓋（V-bounce 失敗）

Cross-asset 比較：
- TLT-014 (TLT vs SPY 20d, threshold=-0.04)：rate-driven vs equity benchmark
- TSLA-017 (TSLA vs QQQ 20d, threshold=-0.005)：高波動個股 vs 板塊 benchmark
- USO-026 (USO vs XLE 20d, threshold=-0.04 Att1)：commodity event-driven vs
  energy sector ETF benchmark（structurally adjacent assets，capture
  crude-specific divergence vs energy-stocks-broader regime）

Att1: divergence_lookback=20, min_relative_return=-0.04
  （TLT-014 sweet spot 直接移植）
Att2/Att3: 視結果調整 threshold 或 lookback 或 anchor（SPY 替代 XLE）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USO026Config(ExperimentConfig):
    """USO-026 USO-XLE Cross-Asset Divergence Regime-Gated MR 參數"""

    # 進場 — 回檔（同 USO-013）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 >= 7%
    pullback_max: float = -0.12  # 回檔 <= 12%

    # 進場 — RSI(2) 短期超賣（同 USO-013）
    rsi_period: int = 2
    rsi_threshold: float = 15.0

    # 進場 — 2 日急跌（同 USO-013）
    drop_2d_threshold: float = -0.025

    # ^OVX forward-looking implied vol gate（沿用 USO-025 sweet spot，stacking
    # 結構同 TLT-014 = TLT-013 + divergence）
    # Att1/Att2 停用，Att3 啟用
    use_ovx_direction_filter: bool = True
    ovx_ticker: str = "^OVX"
    ovx_direction_lookback: int = 3
    max_ovx_change: float = 4.0

    # Cross-asset divergence regime gate（USO-026 核心新增）
    use_divergence_filter: bool = True
    # Att1: XLE anchor, lookback=20, threshold=-0.04（TLT-014 sweet spot）
    #   結果 Part A 28/60.7%/0.15（vs USO-013 35/63%/0.26 退化），Part B 9/88.9%/1.15
    #   結構性發現：Part A 深度負 Rel 為 winners 集中區（crude-specific
    #   capitulation = 真實 MR 機會），Part B 深度負 Rel 為 losers 集中區
    #   ——XLE 與 USO 結構過於相近（同為 energy sector），divergence dimension
    #   方向性 asymmetric 不可靠
    # Att2: SPY anchor（broad equity benchmark，匹配 TLT-014 成功結構），
    #   lookback=20, threshold=-0.04
    #   結果 Part A 17/64.7%/0.23 / Part B 5/80%/0.60 / min 0.23（仍退化）
    #   SPY 過濾過多訊號（35→17）—— 純 divergence 無法獨立改善 USO MR
    # Att3: 切換為 stacking 策略（USO-025 ^OVX base + divergence on top），
    #   test：divergence 是否在已 ^OVX-gated 訊號集上提供正交資訊
    #   anchor=XLE（commodity-adjacent benchmark，避免 SPY 廣泛市場效應）
    benchmark_ticker: str = "XLE"
    divergence_lookback: int = 20
    min_relative_return: float = -0.04

    # 冷卻期（同 USO-013）
    cooldown_days: int = 10


def create_default_config() -> USO026Config:
    return USO026Config(
        name="uso_026_xle_divergence_mr",
        experiment_id="USO-026",
        display_name="USO-XLE Cross-Asset Divergence Regime-Gated MR",
        tickers=["USO"],
        data_start="2010-01-01",
        # 沿用 USO-013 出場
        profit_target=0.030,
        stop_loss=-0.0325,
        holding_days=10,
    )
