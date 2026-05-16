"""
EEM Global-Equity Macro-Context Confirmation Gate on Vol-Transition MR (EEM-016)

策略方向（broad-equity-index macro context confirmation gate，**非配對 / 非相對強度**）：
- 在 EEM-014 Att2 完整框架（BB(20,2.0) 下軌 + 10d 回檔上限 -7% + WR(10)<=-85
  + ClosePos>=40% + ATR(5)/ATR(20)>1.10 + 2DD floor <= -0.5%，TP+3%/SL-3%/20d/cd10）
  之上，新增第 7 條件：**SPY（developed-market 寬基）N 日絕對報酬 <= 門檻**。
- 假設：EEM ≈ 30% 中國權重，其殘餘失敗 SL 皆為「中國政策/貿易孤立衝擊」結構
  （EEM-014 Att2 殘餘：Part A 2021-07-08 DiDi 監管崩盤 / Part B 2025-11-19
  美中貿易摩擦升溫），此類事件發生時 **全球發達市場（SPY）並未同步回檔**，
  EEM 的 BB 下軌觸碰為「中國孤立性持續走弱起點」而非「全球同步 capitulation」，
  均值回歸 V-bounce 不成立；當 SPY 亦同步回檔時，訊號為真正的「broad
  risk-off 同步 capitulation」，MR 反彈更可信。

跨資產脈絡（lesson — broad-equity-index macro context confirmation gate）：
- IWM-015 ✓（IWM-013 Att3 + QQQ 10d <= -1.5% gate，min(A,B)† 0.59→2.80，
  **+374%，repo 首次「broad-equity-index macro context confirmation gate
  （非配對）」**）— 本實驗為該模式 repo 第 2 次跨資產應用，首次於 EM ETF。
- 與既有 EEM-006（EEM-SPY RS 動量回調作**主訊號**，3 次嘗試全失敗，lesson #20）
  **本質不同**：EEM-006 用 EEM-SPY 相對強度差作 primary momentum entry signal；
  EEM-016 用 SPY **絕對** drawdown 作疊加於已驗證 MR 主訊號之上的 regime
  confirmation gate（不涉相對強度 spread，非 pairs MR）。
- 與 cross-asset divergence regime gate（TLT-014 / TSLA-017 / EWZ-009 用相對
  spread）亦不同維度：本實驗為 benchmark **絕對** drawdown，非資產-benchmark
  spread。

EEM-014 Att2 殘餘失敗結構（全部 9 訊號）：
- Part A（5 訊號 80% WR）：殘餘 1 SL 2021-07-08（DiDi ADR 中國監管崩盤第一日）
- Part B（4 訊號 75% WR，min 約束 Sharpe 0.56）：殘餘 1 SL 2025-11-19
  （美中貿易摩擦升溫）
- 兩筆殘餘 SL 皆為「中國孤立性政策/貿易衝擊」——預期訊號日 SPY 近端報酬接近
  零或為正（發達市場未同步回檔），macro-context gate 應可外科式切除而不傷
  真正 broad risk-off capitulation winners。

迭代計畫（依 signal-day SPY 報酬 trade-level 分布調整）：
- Att1: macro_lookback=10, macro_return_threshold=0.0（SPY 10d <= 0，要求發達
  市場亦走弱）— 對齊 IWM-015 方向，先觀察 trade-level 分布
- Att2: 依 Att1 trade-level 分布收緊/放寬 threshold（向 IWM-015 的 -1.5%
  區間靠攏，或外科式對齊殘餘 SL 之 SPY 報酬 outlier 邊界）
- Att3: 調整 lookback（5d / 20d）或 robustness ablation 確認 sweet spot

接受標準（必須全部達成才宣告 SUCCESS）：
- min(A,B) > EEM-014 Att2 的 0.56
- Part A / Part B 累計報酬差距 < 30%
- Part A / Part B 訊號數差距 < 50%
- 使用成交模型（隔日開盤市價進場 + 0.1% 滑價 + 悲觀認定）

========================================================================
三次迭代結果（成交模型 0.1% slippage，隔日開盤市價進場）：
========================================================================
（待回測填入）

EEM 特有限制（lesson #49 / EEM-012，已遵守）：
- SL -3.0%（未超 -3.5% 上限）
- TP +3.0%（符合上限）
- 回檔上限 -7%（符合 -8% 內）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM016Config(ExperimentConfig):
    """EEM-016 Global-Equity Macro-Context Confirmation Gate on Vol-Transition MR 參數"""

    # === EEM-014 Att2 完整框架（沿用，不變） ===
    bb_period: int = 20
    bb_std: float = 2.0
    pullback_lookback: int = 10
    pullback_cap: float = -0.07
    wr_period: int = 10
    wr_threshold: float = -85.0
    close_position_threshold: float = 0.40
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.10
    twoday_return_floor: float = -0.005
    cooldown_days: int = 10

    # === EEM-016 核心新增：SPY 寬基 macro-context confirmation gate ===
    # SPY (SPDR S&P 500 ETF) 為 developed-market 寬基 risk-on/off anchor。
    macro_ticker: str = "SPY"
    # lookback：對齊 IWM-015 的 10 日視窗作為起點
    macro_lookback: int = 10
    # SPY N 日絕對報酬上限：require SPY 亦處於 drawdown（同步 broad risk-off）。
    #   - Att1: 0.0（SPY 10d <= 0，發達市場亦走弱）— 起點，觀察 trade-level 分布
    #   - Att2/Att3: 依 trade-level 分布調整（待回測填入最終值）
    macro_return_threshold: float = 0.0


def create_default_config() -> EEM016Config:
    return EEM016Config(
        name="eem_016_global_macro_context_mr",
        experiment_id="EEM-016",
        display_name="EEM Global-Equity Macro-Context Confirmation Gate MR",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.030,
        holding_days=20,
    )
