"""
TSM-012: ^VXN Forward-Looking Implied-Vol DIRECTION Regime-Gated RS Momentum Pullback 配置
TSM ^VXN Forward-Looking Implied-Vol DIRECTION Regime-Gated RS Momentum Pullback Configuration

策略方向：在 TSM-011 Att3 RS 動量回調框架（TSM-008 進場 + 5 日報酬 ceiling +10.5%）
之上加入 ^VXN（CBOE Nasdaq-100 隱含波動率指數）N 日變化 DIRECTION regime gate，
嘗試外科式移除 binding Part B 殘餘停損（2024-07-16 / 2024-10-30）。

Lesson #24 family（forward-looking implied volatility derivative）跨資產 + 跨策略移植：
- 既往成功：TLT ^MOVE LEVEL、XLU ^MOVE 3d DIRECTION、GLD ^GVZ 10d DIRECTION、
  USO ^OVX 3d DIRECTION、FCX/XBI ^VIX BANDS（全部於 MR 框架）
- 本實驗：repo 首次 ^VXN 應用於任何資產、repo 首次 lesson #24 family 移植至
  RS 動量框架（lesson #21 family）、repo 首次半導體 ADR 個股 forward-looking
  implied vol regime gate
- 半導體 ADR 之 forward-looking 隱含波動率以 ^VXN（Nasdaq-100 IV，含大量半導體/
  科技權值）較 broad ^VIX 更貼近 TSM 之系統性風險來源

進場條件（沿用 TSM-011 Att3，所有條件需同時滿足）：
1. TSM 20日報酬 - SMH 20日報酬 >= 5%（相對板塊超額表現）
2. 5日高點回撤 3-7%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 訊號日 5 日報酬 <= +10.5%（rally exhaustion 過濾，TSM-011 Att3 沿用）
5. **新增：訊號日 ^VXN N 日變化 <= vxn_change_max（隱含波動率非上升 regime）**
6. 冷卻期 10 個交易日

假設：binding Part B 殘餘 SL 發生於 forward-looking 隱含波動率上升 regime
（vol-expansion 開端），winners 集中於隱含波動率下降/穩定 regime。
若 ^VXN direction 維度能結構性分隔 Part B 2 個殘餘 SL 與 8 個 winners，
則 min(A,B) 可由 0.83（Part B binding）突破。

三次迭代計畫：
- Att1: ^VXN 5 日變化 <= +1.0（中間視窗，對標 XLU-013/USO-025 sweet-spot 起點）
- Att2: ^VXN 3 日變化 <= 閾值（短視窗，對標 XLU ^MOVE 3d / USO ^OVX 3d）
- Att3: ^VXN 10 日變化 <= 閾值（長視窗，對標 GLD ^GVZ 10d）

註：trade-level pre-analysis（^VXN 3d/5d/10d 於 22 訊號）顯示 Part B 2 個殘餘
SL（2024-07-16 / 2024-10-30）之 ^VXN 變化皆為近零（quiet vol regime），與
winners 完全交錯——預期 lesson #24 family 在 TSM 上結構性失敗（geopolitical /
customer-concentration idiosyncratic SL 非 vol-regime-separable，lesson #24 v6
條件 (c)）。本實驗為驗證並記錄此跨資產邊界。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSMVXNImpliedVolRSConfig(ExperimentConfig):
    """TSM ^VXN Implied-Vol DIRECTION Regime-Gated RS Momentum Pullback 策略專屬參數"""

    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10

    # Signal-day return CEILING 過濾（沿用 TSM-011 Att3）
    ret_5d_max: float = 0.105  # 5 日報酬上限 +10.5%（rally exhaustion filter）

    # ^VXN forward-looking implied-vol DIRECTION regime gate
    vxn_ticker: str = "^VXN"
    vxn_lookback: int = 5  # ^VXN 變化回看天數（Att1=5 / Att2=3 / Att3=10）
    vxn_change_max: float = 1.0  # ^VXN N 日變化上限（>= 999 視為停用）


def create_default_config() -> TSMVXNImpliedVolRSConfig:
    return TSMVXNImpliedVolRSConfig(
        name="tsm_012_vxn_implied_vol_rs",
        experiment_id="TSM-012",
        display_name="TSM ^VXN Implied-Vol DIRECTION Regime-Gated RS Momentum Pullback",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
    )
