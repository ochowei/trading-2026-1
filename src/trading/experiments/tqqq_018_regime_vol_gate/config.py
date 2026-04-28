"""TQQQ Volatility-Regime-Gated Capitulation Buy 配置 (TQQQ-018)

實驗動機：
- TQQQ-010 為當前最佳（Part A Sharpe 0.36，Part B Sharpe 1.02），Part A 受 2022 升息
  期 + 2020 COVID 兩段極端 vol regime 拖累：6 筆 Part A 停損中 4 筆位於 BB 寬度 > 0.49
  的高波動環境（2020-03-12、2022-03-08、2022-09-01、2022-09-21）
- TQQQ-017 三類「單週期確認」過濾器（ClosePos/2DD/Prev RSI）全部失敗，doc 結論：
  TQQQ-010 的 Part A 訊號分布在單日/雙日/前日維度上 winners 與 losers **無法區分**
- TLT-007 Att2 已驗證 BB(20,2) 寬度 / Close < 5% 的「波動率 regime 閘門」對 rate-driven
  資產（單一極端 vol episode）有效，TLT-012 確認固定絕對閾值結構性最優
- TLT-007 doc 明確列出跨資產假設：「預期成功候選：SPY/DIA/VOO（2020 COVID 單一極端
  episode）、TQQQ（2022 單一科技熊市）」

嘗試方向（repo 中未曾嘗試於 TQQQ）：**波動率 regime 閘門（Volatility Regime Gate）**。
核心假設：
- TQQQ 2022 升息期持續 12+ 個月波動率飆升，BB 寬度 / Close 持續 > 0.50
- TQQQ 2020-03 COVID 為 1-2 週極端 episode，BB 寬度甚至達 1.86（單一最深 SL）
- 一次性切除這兩段 regime，可同時改善 Part A Sharpe 並維持 Part B 訊號流

與 lesson #5 的區分：
- BB 寬度為「整體波動率分類器」（crisis vs calm），非「進場日短線方向過濾」
- 不違反 lesson #5 「均值回歸 + 趨勢過濾 = 災難」（後者指日內趨勢）

執行模型：保留 TQQQ-010 全部進場（Drawdown ≤ -15% + RSI(5) < 25 + Volume > 1.5×SMA20）
+ 出場（TP +7% / SL -8% / 10 天）+ 冷卻 3 天 + 滑價 0.1%。
"""

from dataclasses import dataclass

from trading.experiments.tqqq_001_capitulation.config import TQQQConfig


@dataclass
class TQQQ018Config(TQQQConfig):
    """TQQQ-018 Volatility-Regime-Gated Capitulation Buy 參數

    迭代紀錄（最多三次）：
      Att1（max_bb_width_ratio=0.50）：
        BB 寬度 0.50 為初步甜蜜點預測——過濾 4 個 2020/2022 高 vol Part A SLs
        （2020-03-12 BB 1.864、2022-03-08 BB 0.512、2022-09-01 BB 0.521、2022-09-21
        BB 0.493）同時保留 2020-02-24（BB 0.342）、2021-09-28（BB 0.219）兩個低 vol
        regime SL（不可被 BB 維度過濾）；同時過濾 5 個 Part A 高 vol winners
        （2020-02-28、2020-09-08、2022-01-21、2022-04-26、2022-05-11），但這些贏家
        的高 vol 屬於延續性下跌中的反彈，移除預期不會大幅損害 Sharpe（reduced std）。
        Part B 影響：移除 2024-08-05 W (BB 0.656)、2025-04-04 W (BB 0.549) 兩筆贏家
        + 2025-03-06 SL (BB 0.477) — 2 W vs 1 SL 的代價，預期 Part B Sharpe 略降但
        仍 >> Part A。
    """

    # 沿用 TQQQ-001 / TQQQ-010 的進場與出場參數（drawdown_lookback=20, threshold=-0.15,
    # rsi_period=5, rsi_threshold=25, volume_multiplier=1.5, volume_sma_period=20,
    # cooldown_days=3, profit_target=0.07, stop_loss=-0.08, holding_days=10）

    # 波動率 regime 閘門（新增）：BB(bb_period, bb_std) 寬度 / Close < max_bb_width_ratio
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.50  # Att1 起點，將依結果迭代

    # 成交模型參數（同 TQQQ-010）
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> TQQQ018Config:
    return TQQQ018Config(
        name="tqqq_018_regime_vol_gate",
        experiment_id="TQQQ-018",
        display_name="TQQQ Volatility-Regime-Gated Capitulation Buy",
        tickers=["TQQQ"],
        data_start="2018-06-01",  # 暖機 BB(20)
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.07,
        stop_loss=-0.08,
        holding_days=10,
        # TQQQConfig 預設：drawdown_lookback=20, drawdown_threshold=-0.15,
        # rsi_period=5, rsi_threshold=25.0, volume_multiplier=1.5,
        # volume_sma_period=20, cooldown_days=3
    )
