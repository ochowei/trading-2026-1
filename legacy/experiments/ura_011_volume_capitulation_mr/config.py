"""
URA-011：成交量放大資本化均值回歸配置
(URA Volume-Confirmed Capitulation Mean Reversion Config)

動機（Motivation）：
    URA-004（10日回檔 10-20% + RSI(2)<15 + 2日跌幅 ≤ -3%）為當前全域最優
    （min(A,B) Sharpe 0.39）。URA-007（ATR 波動率自適應）、URA-008（RSI
    bullish hook divergence）、URA-009（day-after reversal）、URA-010
    （WVF 資本化深度）四次強化進場品質的嘗試均失敗，根因包含：
    - ATR 與 2日跌幅 重複過濾（URA-007 驗證）
    - 政策驅動 V-bounce 無法辨識（URA-008/009）
    - capitulation 深度本身無真假區分力（URA-010）

    本實驗改用 **成交量放大（Volume Spike）** 作為品質過濾器。
    Volume 提供與 ATR/price range/RSI turn-up 結構性獨立的資訊：
        - ATR：當日價格區間（volatility）
        - Volume：市場參與度（institutional flow）
    核心假設：URA 的真實 capitulation 伴隨機構性拋售放量，
    而緩慢下磨（slow melt drift）為低量 drift。若此假設成立，
    volume spike 過濾可區分「真 capitulation（ATR 高 + Volume 高）」
    與「slow melt（ATR 低 + Volume 低）」，以及擴展過濾
    「急跌但無大量（ATR 高 + Volume 低，常為流動性真空而非真拋售）」。

    Repo 現狀：Volume 作為主過濾器僅試過 2 次（USO-006 Att2 失敗、
    TSLA-012 Att1 失敗），URA 尚未嘗試，且 URA 為政策驅動 + 鈾價事件
    驅動資產，volume spike 與事件性 capitulation 理論上高度相關。

策略方向：均值回歸（Volume-confirmed institutional capitulation）
    Strategy direction: Mean reversion confirmed by institutional-flow spike

迭代歷程（Iteration Log）：
    Att1：URA-004 base（10d PB 10-20% + RSI(2)<15 + 2DD ≤ -3%）
          + Volume(today) / Avg20(Volume) ≥ 1.5x
          出場：TP +6% / SL -5.5% / 20天 / cd 10
          結果：Part A 6/66.7%/0.39 / Part B 6/66.7%/0.39 (min 0.39，同 URA-004)
          發現：完美 A/B 平衡（6/6 訊號、同 WR、同累計 12.53%），但 Sharpe
          未超越 URA-004 的 0.39。4 TPs + 2 SLs per part，需進一步過濾 SLs。

    Att2：Att1 基礎 + Volume ≥ 2.0x（收緊）+ ClosePos ≥ 40%（日內反轉確認）
          結果：Part A 2/50%/**0.04** / Part B 3/66.7%/0.39 / min **0.04**（崩壞）
          發現：收緊過濾 + ClosePos 移除 TPs 多於 SLs。Part A 從 6/4W2L 降至 2/1W1L
          ——進場日期偏移（lesson #19）使 2020-02-27 原 TP 日變 2020-02-28 SL 日。
          URA 政策驅動使 ClosePos 無選擇性（與 URA-007 ATR 失敗模式平行）。

    Att3：Att1 基礎移除 2DD（Volume spike 作為近期恐慌確認替代 2DD）
          結果：Part A 7/57.1%/**0.18** / Part B 6/66.7%/0.39（同 Att1）/ min **0.18**
          發現：Volume 與 2DD 結構性獨立，移除 2DD 在 Part A 新增 2 訊號
          （2022-10-12 TP + 2023-03-10 SL）使 WR 降至 57.1%；Part B 不變
          （2DD 在 Part B 對 Volume spike 訊號為非綁定）。**結論**：2DD 與
          Volume 互補而非重複，URA-004 框架的 2DD 過濾在 Part A 有真實選擇性。

結論：三次迭代均無法超越 URA-004 min(A,B) 0.39。Att1 達到完美 A/B 平衡
    （6/6 訊號、同 WR、同累計）但品質天花板等同 URA-004。Volume 作為
    supplementary filter 可提供 A/B 對稱性但不提升訊號品質。URA-011 為
    URA 第 11 種失敗策略類型，擴展 URA-007（ATR 重複過濾）、URA-008~010
    （oscillator hook / day-after / WVF）failure family：「entry-time
    supplementary 過濾器」在政策驅動 URA 上無法超越 URA-004 pullback+RSI(2)+2DD
    結構最優。

資產特性：URA 日波動 2.34%，GLD 比率 2.11x；日均成交量 ~3M 股，流動性充足。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URA011Config(ExperimentConfig):
    """URA-011 成交量放大資本化均值回歸參數"""

    # 回檔範圍（沿用 URA-004）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10
    pullback_upper: float = -0.20

    # RSI(2) 超賣（沿用 URA-004）
    rsi_period: int = 2
    rsi_threshold: float = 15.0

    # 2日急跌（Att3 移除 — Volume spike 作為近期恐慌確認替代）
    use_two_day_decline: bool = False  # Att3 關閉 2DD 過濾
    two_day_decline: float = -0.03

    # Volume Spike（主品質過濾器）
    volume_avg_window: int = 20
    volume_multiple: float = 1.5  # Att3：回到 1.5x（Att2 的 2.0x 過嚴）

    # ClosePos 日內反轉確認（Att3 移除 — Att2 驗證對 URA 無選擇性）
    use_close_pos: bool = False
    close_pos_threshold: float = 0.40

    # 冷卻
    cooldown_days: int = 10


def create_default_config() -> URA011Config:
    return URA011Config(
        name="ura_011_volume_capitulation_mr",
        experiment_id="URA-011",
        display_name="URA Volume-Confirmed Capitulation MR",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.060,
        stop_loss=-0.055,
        holding_days=20,
    )
