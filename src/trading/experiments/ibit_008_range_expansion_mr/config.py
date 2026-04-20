"""
IBIT-008：單日 Range Expansion Climax 均值回歸配置
(IBIT Wide-Range Climax + Intraday Reversal Mean Reversion Config)

動機（Motivation）：
    IBIT-006 Att2（Gap-Down + 10日回檔 12-25% + WR(10)≤-80，TP+4.5%/SL-4%/15天）
    雖達 min(A,B) 0.40，但 Part A/B 累計差仍 66%（>30% 目標）且 Part B 僅 3 訊號
    （WR 67%, 累計 +4.68%）。核心限制：Gap-down ≤ -1.5% 過濾器依賴「隔夜跳空」
    結構，在 2025 年震盪期跳空幅度不足（BTC 盤外拋壓分散至盤中），產生過少訊號。
    IBIT-007 Keltner Lower MR 三次迭代全部失敗（min -0.31~0.00），證明波動率
    自適應「慢性超賣」偵測對高波動加密 ETF 無效。

    本實驗嘗試 **repo 首次單日 Range Expansion Climax** 作為主進場訊號：
        - 今日單日 True Range ≥ 2.0 × ATR(20)：單日波幅為近 20 日均值兩倍以上，
          代表賣壓/波動率的**爆發性 climax**（而非 NR7 的緩和收縮、也非 Keltner
          的長期偏離）
        - Close Position ≥ 50%：收盤價高於當日中點，確認日內買方在恐慌賣壓後
          接回主導權（強化版日內反轉，嚴於 Close > Open）
        - 10 日回檔 -6% ~ -20%：在下跌 regime 中捕捉 climax（避免牛市高點爆發
          範圍後的續跌）

    與現有 IBIT 實驗的結構差異：
        - IBIT-006（Gap-Down）：捕捉「隔夜拋壓完成」的 overnight 結構
        - IBIT-007（Keltner）：捕捉「EMA/ATR 靜態偏離」的慢性超賣
        - IBIT-008（Range Expansion）：捕捉「單日 TR 爆發」的當日 capitulation
          climax —— 既非隔夜也非長期偏離，而是「盤中的劇烈波動 + 日內反轉」

    與 cross-asset lesson #20a (Gap-Down)、lesson #15 (ATR 波動率自適應) 皆不同：
        - Lesson #20a 強調 overnight gap + intraday recovery（結構：盤外 → 盤中）
        - Lesson #15 的 ATR(5)/ATR(20) 比較**近期 vs 中期**波動率趨勢
        - 本實驗 TR / ATR(20) 比較**當日 vs 歷史**單點爆發

    Repo 首次將「Range Expansion（單日寬範圍 K 棒）作為 MR 主要觸發條件」的
    試驗（TLT-006 曾將 Range Expansion 作為多條件之一的輔助過濾，非主訊號）。

策略方向：均值回歸（單日 Range Expansion climax + 強日內反轉確認）
    Strategy direction: Mean reversion via single-bar TR expansion climax +
    strong intraday reversal confirmation

迭代歷程（Iteration Log）：

Att1（Baseline）—— 將於回測後填入

Att2（待決策）—— 將於 Att1 結果後決定調整方向

Att3（待決策）—— 將於 Att2 結果後決定調整方向

資產特性：IBIT 日波動 3.17%，GLD 比率 2.64x。
    Att1 參數：
    進場：TR / ATR(20) ≥ 2.0 + ClosePos ≥ 50% + 10日回檔 [-6%, -20%]
         + WR(10) ≤ -70
    出場：TP +4.5% / SL -4.0% / 最長持倉 15 天（IBIT-006 Att2 甜蜜點）
    冷卻：10 天
    無追蹤停損（日波動 3.17% 禁用區域，cross-asset lesson #2）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IBIT008Config(ExperimentConfig):
    """IBIT-008 Range Expansion Climax 均值回歸參數"""

    # Range Expansion 主訊號（Att2：放寬 TR 倍率以增加訊號頻率）
    atr_period: int = 20  # ATR 基準期
    tr_ratio_threshold: float = 1.5  # Att2：今日 TR / ATR(20) ≥ 1.5（由 2.0 放寬）

    # 日內反轉確認（Att2：放寬 ClosePos 至 40%）
    close_pos_threshold: float = 0.40  # Att2：ClosePos ≥ 40%（由 50% 放寬）

    # 回檔深度過濾（避免牛市高點 range expansion 的續跌）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.06  # 10 日回檔 ≤ -6%
    pullback_upper: float = -0.20  # 回檔上限 -20%（過濾崩盤極端）

    # Williams %R 超賣確認
    wr_period: int = 10
    wr_threshold: float = -70.0  # WR(10) ≤ -70

    # 冷卻
    cooldown_days: int = 10


def create_default_config() -> IBIT008Config:
    return IBIT008Config(
        name="ibit_008_range_expansion_mr",
        experiment_id="IBIT-008",
        display_name="IBIT Range Expansion Climax Mean Reversion",
        tickers=["IBIT"],
        data_start="2024-01-01",
        part_a_start="2024-01-01",
        part_a_end="2024-12-31",
        part_b_start="2025-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.045,  # +4.5%（IBIT-006 Att2 已驗證甜蜜點）
        stop_loss=-0.04,  # -4.0%（IBIT-006 Att2 已驗證甜蜜點）
        holding_days=15,
    )
