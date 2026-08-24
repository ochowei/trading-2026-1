"""
CIBR NR7 Volatility Contraction + Pullback MR 配置 (CIBR-010)

動機：
CIBR-008 Att2（BB 下軌 + 回檔上限混合）為當前最佳 min(A,B) Sharpe 0.39，
Part A/B 累計差 41%（9.23% vs 15.66%）仍超過 30% 目標。CIBR-009 的短週期
price-action 反轉（stop-run + reclaim + bullish bar）三次迭代全敗，證實
CIBR 網路安全板塊事件驅動性質使單日 price-action 過濾器失效。

本實驗探索一個本 repo 未曾嘗試的方向：**NR7（Narrowest Range 7）波動率
壓縮模式 + pullback 均值回歸**。

理論假設：
- NR7 定義：今日 True Range 為近 7 日中最小
- 在 pullback 情境下，NR7 代表賣壓衰竭 / 波動率壓縮（coiled spring）
- 與 BB Squeeze（20 日標準差壓縮）不同，NR7 僅偵測「單日範圍」壓縮，
  更接近 day-trader 的 volatility contraction pattern
- 與 pullback+WR 架構結合：原本的超賣訊號 + NR7 確認「賣方精疲力竭」
- 與 price-action 反轉（CIBR-009 失敗）不同：NR7 不依賴 stop-run + reclaim
  等脆弱的單日形態，而是「範圍壓縮」本身是賣壓衰竭的客觀證據

CIBR 日波動 1.53%（~ATR 1.1%），預期 NR7 訊號頻率：
- 每 7 天約 1 次 NR7（按機率 ≈ 14%），搭配 pullback+WR 過濾後應落在
  ~5 訊號/年範圍（與 CIBR-008 訊號量接近）

對比既有 CIBR 策略：
- CIBR-008 BB 下軌 + 回檔上限：統計自適應（20日 std）+ 絕對深度過濾
- CIBR-010 NR7 + pullback：單日波動壓縮（7日 TR min）+ 絕對深度過濾
- 兩者互補：BB 下軌偵測「價格極端」，NR7 偵測「波動率極端壓縮」

迭代計畫：
Att1: pullback ≥ 4% + WR(10) ≤ -80 + NR7 + ClosePos ≥ 40%（不含 ATR，
      避免與 NR7 結構性衝突）
Att2: 根據 Att1 結果，加入或移除 ATR / 調整 NR 窗口長度
Att3: 出場參數或 cooldown 微調

出場參數沿用 CIBR 驗證甜蜜點（CIBR-008 Att2）：
- TP +3.5%（CIBR 所有策略均用此值）
- SL -4.0%（CIBR-004 Att3 驗證 -4.5% 同樣停損，加寬只增虧損）
- 持倉 18 天（CIBR-001/002/007/008 一致）
- 冷卻 8 天
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR010Config(ExperimentConfig):
    """CIBR-010 NR7 Pullback MR 參數"""

    # 回檔深度
    pullback_lookback: int = 10
    pullback_threshold: float = -0.04  # 10日高點回檔 ≥ 4%

    # 超賣
    wr_period: int = 10
    wr_threshold: float = -80.0

    # NR7 波動率壓縮（今日 TR 為近 nr_window 日最小）
    nr_window: int = 7

    # 日內反轉
    close_pos_threshold: float = 0.40

    # ATR 選項（Att1/Att3 關閉——與 NR7 結構性衝突；Att2 驗證已失敗）
    use_atr_filter: bool = False
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15

    # 2日跌幅過濾（Att3 啟用：確保 NR7 發生在真正的賣壓後而非整理時）
    use_decline_filter: bool = True
    decline_lookback: int = 2
    decline_threshold: float = -0.02  # 2日跌幅 ≤ -2.0%（~1.3σ）

    cooldown_days: int = 8


def create_default_config() -> CIBR010Config:
    return CIBR010Config(
        name="cibr_010_nr7_pullback_mr",
        experiment_id="CIBR-010",
        display_name="CIBR NR7 Volatility Contraction + Pullback MR",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%
        holding_days=18,
    )
