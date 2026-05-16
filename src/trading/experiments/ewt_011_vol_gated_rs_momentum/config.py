"""
EWT-011: Volatility-Regime-Gated RS Momentum Pullback

策略方向：動量 / 相對強度（momentum / RS）+ 波動率 regime 閘門。

實驗動機 (Problem statement)：
- EWT 當前文件「全域最優」EWT-010 Att2 為 2D cross-asset divergence
  filter on vol-transition MR：Part A 8 訊號 / Part B 3 訊號，**雙 Part
  皆 std=0（全勝零方差，共 11 訊號）**，統計上退化、樣本極小。
- EWT 真實穩健最優為 **EWT-007 Att1（RS 動量回調）**：Part A 19 訊號 /
  WR 78.9% / Sharpe **0.42** / cum +25.99%，Part B 7 訊號 / WR 85.7% /
  Sharpe **0.93** / cum +18.07%，**雙 Part 皆有真實變異**。
  問題：A/B 累積差 30.5%（邊界）、訊號比 19:7 = siggap 63%（>50% 違反
  平衡目標）；Part A Sharpe 0.42 << Part B 0.93。
- Part A 低 Sharpe + 過多訊號根因：2019-2023 含 2020 COVID 崩盤 + 2022
  半導體下行週期/熊市，RS 動量訊號在高波動 regime 品質差。

策略假設：
- 沿用 Round 2 (DIA-013 Att3) 已驗證跨資產發現：**波動率 regime 閘門
  （ATR/Close ≤ 閾值）外科式切除高波動崩盤期低品質訊號**，提升 Part A
  Sharpe 並把 Part A 訊號數壓向 Part B 水準（修復 siggap），同時保留
  Part B 的強勢（2024-2025 為平靜半導體多頭）。
- lesson #23 BB-Width regime gate 跨策略擴展：MR（DIA-013 trend
  pullback）→ 本實驗 RS momentum pullback 框架。

進場條件（全部滿足，訊號日 T，執行模型於 T+1 開盤進場）：
1. EWT 20日報酬 − EEM 20日報酬 ≥ 3%（沿用 EWT-007 RS 超額）
2. 5 日高點回撤 ∈ [2%, 5%]（沿用 EWT-007）
3. Close > SMA(50)（沿用 EWT-007 趨勢確認）
4. **波動率 regime 閘門：ATR(14)/Close ≤ max_atr_pct（EWT-011 核心新增）**
5. 冷卻期 10 個交易日

出場（執行模型，滑價 0.1%）：
- 沿用 EWT-007 已驗證甜蜜點 TP +3.5% / SL -4.0% / 最長持倉 20 天，
  以隔離波動率閘門的邊際貢獻。

迭代規劃（最多 3 次）：
- Att1：max_atr_pct = 0.020（~2.0%，保守，僅切除極端崩盤波動）
- Att2：依結果調整甜蜜點（0.018 / 0.022）
- Att3：甜蜜點收斂或替代維度

跨資產貢獻：
- repo 首次將波動率 regime 閘門（lesson #23 family）跨策略移植至 RS
  momentum pullback 框架；若 SUCCESS → 驗證波動率閘門為「修復 RS 動量
  在高波動 regime 低品質訊號 + A/B siggap 失衡」的通用維度。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWT011Config(ExperimentConfig):
    """EWT-011 Volatility-Regime-Gated RS Momentum Pullback 參數"""

    # 沿用 EWT-007 Att1
    reference_ticker: str = "EEM"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.03
    pullback_lookback: int = 5
    pullback_min: float = 0.02
    pullback_max: float = 0.05
    cooldown_days: int = 10

    # 波動率 regime 閘門（Att1：max_atr_pct=2.0% 過鬆未過濾，Att2/3 停用）
    # 失敗發現：EWT-007 的 4 個 Part A SL 分散於 2019/2021/2022（非 vol
    # 集中），vol gate 無外科分離力。
    use_vol_regime_gate: bool = False
    atr_period: int = 14
    max_atr_pct: float = 0.020

    # EWT-011 Att2 核心：RS 新鮮度（dual-window）— 要求短窗 RS 仍為正，
    # 切除「20d RS 達標但動量已轉弱」的 stale 訊號（EWT-007 多筆近零
    # time-expiry fizzle 之根因）
    use_rs_freshness: bool = True
    rs_short_period: int = 10
    # Att2: 0.0（min 0.56，beats EWT-007 0.42，但移除 1 Part B winner 7→6）
    # Att3: -0.01（略放寬，嘗試回收 Part B winner 同時保留 Part A 增益）
    rs_short_min: float = -0.01


def create_default_config() -> EWT011Config:
    return EWT011Config(
        name="ewt_011_vol_gated_rs_momentum",
        experiment_id="EWT-011",
        display_name="EWT Volatility-Regime-Gated RS Momentum Pullback",
        tickers=["EWT"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.04,
        holding_days=20,
    )
