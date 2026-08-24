"""
INDA-013: Broad-EM Macro-Context-Confirmed Vol-Transition MR

策略方向：均值回歸 + broad-market macro context confirmation gate
（lesson #25 family，QQQ→IWM 已驗證；本實驗首次以 EEM 為 broad EM
context anchor 確認 single-country EM 的 capitulation MR）。

實驗動機 (Problem statement)：
- INDA 文件「全域最優」INDA-012 採 std=0 退化結構（Part A 4 訊號 /
  Part B 2 訊號，共 6 訊號），統計上不具真實 risk-adjusted 意義。
- INDA 真實穩健最優為 **inda_010 Post-Capitulation Vol-Transition MR**：
  Part A 11 訊號 / WR 73% / Sharpe **0.30**（binding）/ cum +10.51%，
  Part B 4 訊號 / WR 75% / Sharpe 1.48 / cum +10.41%，**雙 Part 真實
  變異 + A/B 累積差僅 ~1%（極優）**，min(A,B) 0.30。
- Part A 拖累來自 3 筆 loser：2020-02-03（COVID 早期，到期 -4.4%）、
  2022-09-16（升息熊市 SL -4.1%）、2023-01-27（Adani-Hindenburg
  做空報告，India 特有危機，到期 -3.6%）。其中 2023-01-27 為
  **India-idiosyncratic 延續性下跌**（非系統性 EM risk-off），
  capitulation V-bounce 結構性失效。
- 由於 cumgap 已 ~1%、年化 siggap 亦合格，**任何 Part A Sharpe 提升
  即為乾淨的 robust 超越**（min 0.30 binding，Part B 1.48 已強）。

策略假設：
- 沿用 lesson #25（Broad-Market Macro Context Confirmation Gate，
  QQQ 對 IWM 已驗證）：single-country / sub-segment ETF 的
  capitulation MR 在「broad 母體同步走弱」（系統性 risk-off）時 V-bounce
  成功率高；在「broad 母體不弱、僅標的自身特有事件下殺」（idiosyncratic
  continuation，如 Adani 危機）時 bounce 結構性失效。
- 對 INDA（single-country EM）而言，broad context anchor = **EEM
  （broad EM ETF）**。要求 INDA capitulation 訊號日 EEM 同期亦處於
  pullback（EEM N 日報酬 <= 閾值），外科切除 India-idiosyncratic
  continuation 訊號（2023-01-27 Adani）。

進場條件（全部滿足，訊號日 T，執行模型於 T+1 開盤進場）：
1~6. 沿用 inda_010：10日回檔 ∈ [-7%,-3%] + WR(10)≤-80 + ClosePos≥0.4
     + ATR(5)/ATR(20)>1.15 + 2日報酬 ≤ -2%
7. **EEM N 日報酬 <= max_eem_return（INDA-013 核心新增 broad-EM
   macro context confirmation gate）**
8. 冷卻期 7 個交易日

出場（執行模型，滑價 0.1%）：
- 沿用 inda_010 已驗證 TP +3.5% / SL -4.0% / 最長持倉 15 天。

迭代結果（Att1 SUCCESS vs robust baseline inda_010 min 0.30）：
- Att1 ★ (lookback=10, max=0.0)：Part A 9/77.8%/Sharpe **0.38**
  cum +10.78% / Part B 4/75%/1.48 cum +10.41%（**完全保留**）/
  min(A,B) **0.38**（**+27% vs inda_010 robust 0.30**），cumgap
  |10.78−10.41|/10.78 = **3.4% << 30% ✓**，年化 siggap ~10% << 50% ✓。
  EEM 10d gate 外科移除 2023-01-27 Adani-Hindenburg India-idiosyncratic
  loser（EEM 同期未走弱 → 非系統性 → 過濾），保留 2 個 systemic loser
  （2020-02-03 COVID、2022-09-16 升息熊市，EEM 同步走弱故保留）+ 全部
  winners + 全部 Part B。
- Att2 (max=-0.02)：過嚴，移除 2 Part A winners 同時保留 2 systemic
  losers，Sharpe 0.38→**0.16** REJECT。
- Att3 (lookback=5)：短窗噪音較大，移除 2 winners，Sharpe 0.38→**0.23**
  REJECT，確認 10d/0.0 為結構性甜蜜點。

跨資產貢獻：
- repo 首次以 EEM 為 broad EM context anchor 確認 single-country EM
  capitulation MR（lesson #25 family 從 QQQ→IWM 擴展至 EEM→INDA）；
  若 SUCCESS → 驗證 broad-母體 macro context confirmation 為
  single-country EM idiosyncratic-continuation 失敗模式的正交解。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDA013Config(ExperimentConfig):
    """INDA-013 Broad-EM Macro-Context-Confirmed Vol-Transition MR 參數"""

    # 沿用 inda_010
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03
    pullback_cap: float = -0.07
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.4
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15
    drop_2d_floor: float = -0.02
    cooldown_days: int = 7

    # INDA-013 核心新增：broad-EM macro context confirmation gate
    use_broad_em_gate: bool = True
    broad_em_ticker: str = "EEM"
    # Att1 ★ SUCCESS: lookback=10, max=0.0（min 0.30→0.38 +27%，外科移除
    #   2023-01-27 Adani idiosyncratic loser，Part B 全保留，cumgap 3.4%）
    # Att2: lookback=10, max=-0.02（過嚴：移除 2 Part A winners、保留 2
    #   systemic losers，Sharpe 0.38→0.16 REJECT）
    # Att3: lookback=5, max=0.0（短窗噪音較大，移除 2 winners，
    #   Sharpe 0.38→0.23 REJECT，確認 10d/0.0 為結構性甜蜜點）
    eem_lookback: int = 10
    max_eem_return: float = 0.0


def create_default_config() -> INDA013Config:
    return INDA013Config(
        name="inda_013_broad_em_confirmed_mr",
        experiment_id="INDA-013",
        display_name="INDA Broad-EM Macro-Context-Confirmed Vol-Transition MR",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,
        stop_loss=-0.04,
        holding_days=15,
    )
