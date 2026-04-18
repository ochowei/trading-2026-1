"""
CIBR BB 下軌 + 回檔上限混合進場配置 (CIBR-008)

動機：CIBR-007 Att1（BB 下軌均值回歸）Part A Sharpe 0.27 / Part B Sharpe 4.38，
Part A/B 累計報酬差距 86%（8.42% vs 15.66%）。Part A 的 3 筆停損均發生在
極端下跌期（2020-02-24、2020-03-16 COVID 崩盤；2021-02-26 科技股拋售），
這些訊號雖符合 BB 下軌+WR+ATR+ClosePos 品質過濾，但 BB 帶寬在持續崩盤中
外擴失去選擇性（lesson #52）。

參考 EWJ-003 Att3 的成功模式（min(A,B) Sharpe 0.60）：BB 下軌混合 10日高點
回檔上限，保留 BB 統計自適應特性同時用絕對回檔深度隔離極端崩盤。

CIBR 日波動 1.53%，10日高點回檔：
- -7% = 4.6σ（可能過嚴）
- -8% = 5.2σ（預期甜蜜點，隔離 COVID 級崩盤但保留一般性修正）
- -10% = 6.5σ（可能過鬆，無法過濾 2021-02 類型拋售）

對比 CIBR-002 Att2（Pullback+WR 框架 + 回檔上限 12%）：已驗證 12% 過鬆
（Part A 0.18→0.12）。BB 下軌本身已提供統計自適應進場門檻，不需要再
依賴固定回檔作為進場訊號——回檔上限僅作「崩盤過濾器」。

Att1: BB(20,2.0) + 10日高點回檔上限 -8% + WR/ClosePos/ATR
      → Part A 0.27 (3訊號 2W 1L) / Part B 4.08 (4訊號 100%WR), min 0.27
      失敗分析：-8%（5.2σ）過嚴，移除 4 個 Part A 贏家（2019-08-05、
      2020-10-30、2022-05-10、2022-09-01）僅保留 1 COVID 停損（2020-02-24），
      訊號過少無統計意義
Att2: 放寬回檔上限至 -12%（~7.8σ）★ 最佳
      → Part A 0.39 (7訊號 5W 2L 9.23%) / Part B 4.38 (5訊號 100%WR 15.66%),
      min 0.39 (+44% vs CIBR-007 的 0.27)
      成功分析：成功濾除 2020-03-16（COVID 連續崩盤 -24% 深度）+ 2022-05-10
      （意外地移除此贏家），保留 2020-02-24 / 2021-02-26 兩筆 -4~-8% 深度
      區間停損。A/B 訊號比 1.4:1（優秀），累計報酬 gap 41%（仍 >30% 但大幅
      改善自 CIBR-007 的 86%）。Part A WR 66.7%→71.4%
Att3: 收窄回檔上限至 -10%（~6.5σ）
      → Part A 0.27 (6訊號 4W 2L 5.54%) / Part B 4.38 (5訊號 100%WR), min 0.27
      失敗分析：-10% 濾除了 1 贏家（2020-10-30）但未能濾除剩餘 2 停損
      （2020-02-24 和 2021-02-26 回檔深度介於 -10~-12%）。確認 -12% 為
      甜蜜點：深於 -12% 的回檔屬於崩盤連續段，-10~-12% 介於均值回歸與崩盤
      之間的過渡區不可區分
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR008Config(ExperimentConfig):
    """CIBR-008 BB 下軌 + 回檔上限混合進場參數"""

    # BB 參數
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離（10日高點回檔上限，過濾極端崩盤）
    pullback_lookback: int = 10
    pullback_cap: float = -0.12  # 回檔上限 12%（~7.8σ for 1.53% vol）

    # 品質過濾（同 CIBR-007 驗證有效參數）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15

    cooldown_days: int = 8


def create_default_config() -> CIBR008Config:
    return CIBR008Config(
        name="cibr_008_bb_lower_pullback_cap",
        experiment_id="CIBR-008",
        display_name="CIBR BB Lower Band + Pullback Cap Hybrid",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%
        holding_days=18,
    )
