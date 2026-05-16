"""
USO-029: Trend-Following Pullback Continuation

策略方向：趨勢跟蹤（trend following）— repo 中 USO 較少使用的方向。

實驗動機 (Problem statement)：
- USO 當前全域最優 USO-028 Att1（^OVX 5d direction MR）為 capitulation-MR
  框架：Part A 22 訊號 / Sharpe 0.73 / cum +46.73%，Part B 10 訊號 /
  Sharpe 0.64 / cum +16.85%，min(A,B) 0.64。
- 結構性問題：USO 過去 28 次實驗幾乎全為均值回歸（買急跌）。Part A
  (2019-2023) 含 2020 COVID 原油崩盤 + 2022 俄烏供給衝擊，為極端高波動
  regime；Part B (2024-2025) 為 moderate sideways（USO-024 已記錄）。
  任何 capitulation/vol-driven 策略在 Part A 天然超額獲利 → A/B 累積差
  64%、訊號差 55%，遠超平衡目標（gap < 30% / siggap < 50%）。
- 既有 breakout 嘗試（USO-021 BB squeeze / USO-024 regime breakout）在
  Part B moderate regime 全部 break（Part B Sharpe -0.01）。MBPC（lesson
  #21）需單一純上升 regime，USO 為週期性商品不適用。

策略假設：
- 原油為強趨勢商品（OPEC / 地緣政治 / 供需），2019-2023 與 2024-2025
  兩段皆存在可辨識的中期上升趨勢（2020-21 復甦、2022 spike、2024 初
  反彈、2025 地緣溢價）。
- 「在已確立上升趨勢中買入溫和回檔」(trend-following pullback
  continuation) 只在趨勢成立時觸發 → 訊號自然分布於兩段，且避開
  Part A 過度集中的「深度 capitulation 反彈」（純 MR 領域），結構性
  壓縮 A/B 落差。
- 這與 repo 既有 capitulation-MR 正交（MR 不看趨勢、買最深的跌；本策略
  以趨勢為核心、只買淺回檔）。lesson #5「趨勢濾波器 + 均值回歸 = 災難」
  不適用——本策略本身即趨勢跟蹤，趨勢規範閘門為核心而非附加。

進場條件（全部滿足，訊號日 T，執行模型於 T+1 開盤進場）：
1. 趨勢 regime：SMA(20) > SMA(50) 且 Close > SMA(50)（中期上升）
2. 長期動量為正：ROC(60) > 0（排除下跌趨勢中的反彈 / 崩盤底部）
3. 溫和回檔：10 日高點回檔 ∈ [-8%, -2%]（真實但非崩盤式的拉回；
   排除 top-chase 與 regime break）
4. 回檔已現轉折：今日 Close > 昨日 Close（拉回後恢復跡象）
5. 冷卻期 10 個交易日

出場（執行模型，滑價 0.1%）：
- 非對稱 TP +5% / SL -4% / 最長持倉 20 天，讓趨勢延續行情奔跑。
- USO ~2.2% 日波動，lesson #2：1.5-3% vol 預設不用 trailing stop → 固定
  TP/SL。

迭代規劃（最多 3 次）：
- Att1：上述基線（PB [-8%,-2%], ROC60>0, close-up, cd10, TP+5/SL-4/20d）
- Att2：依結果調整（回檔帶 / ROC 門檻 / SMA50 斜率 / cd）
- Att3：甜蜜點收斂

跨資產貢獻：
- repo 首次於 USO（commodity event-driven ETF）建立純趨勢跟蹤
  continuation 框架（既有 28 次幾乎全 MR + 2 次失敗 breakout）。
- 若 SUCCESS → 驗證「趨勢跟蹤 continuation 於週期性商品 ETF 可解
  capitulation-MR 的結構性 A/B regime 失衡」。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USO029Config(ExperimentConfig):
    """USO-029 Trend-Following Pullback Continuation 參數"""

    # 趨勢 regime
    sma_fast: int = 20
    sma_slow: int = 50
    # Att2 新增：SMA(slow) 斜率（要求中期趨勢線本身向上，過濾 whipsaw）
    sma_slow_slope_lookback: int = 20
    require_sma_slow_rising: bool = True
    # Att2 新增：價格須重新站回 SMA(fast)（回檔結束、延續確認，而非仍在下跌）
    require_close_above_fast: bool = True

    # 長期動量
    roc_lookback: int = 60
    # Att1: 0.0（過鬆 Sharpe -0.05）→ Att2: 0.08（Sharpe 0.10）→ Att3: 0.12（極強趨勢）
    roc_min: float = 0.12

    # 溫和回檔（Att1/Att2）；Att3 改用 Donchian 新高突破（停用回檔帶）
    pullback_lookback: int = 10
    pullback_min: float = -0.07
    pullback_max: float = -0.025
    # Att3：純動量突破延續 — 在強上升趨勢中買 N 日新高（取代回檔買入）
    use_donchian_breakout: bool = True
    donchian_lookback: int = 20

    # 回檔轉折確認：今日收高於昨日（Att2/Att3 停用）
    require_close_up: bool = False

    # 冷卻期
    cooldown_days: int = 15


def create_default_config() -> USO029Config:
    return USO029Config(
        name="uso_029_trend_pullback_continuation",
        experiment_id="USO-029",
        display_name="USO Trend-Following Pullback Continuation",
        tickers=["USO"],
        data_start="2010-01-01",
        profit_target=0.10,
        stop_loss=-0.05,
        holding_days=30,
    )
