"""
IBIT-007：Keltner 通道下軌 + 回檔 + 反轉 K 線均值回歸配置
(IBIT Keltner Channel Lower Band + Pullback + Reversal Bar Mean Reversion)

動機（Motivation）：
    IBIT-006 Att2（Gap-Down + 10日回檔 12-25% + WR(10)≤-80，TP+4.5%/SL-4%/15天）
    雖達 min(A,B) 0.40，但 Part A/B 累計差仍 66%（>30% 目標）且 Part B 僅 3 訊號
    （WR 67%, 累計 +4.68%）。核心限制：Gap-down ≤ -1.5% 過濾器在 2025 年震盪期
    產生過少訊號，使 Part B 樣本稀薄。

    本實驗捨棄 gap-down 過濾器，改用 **Keltner 通道下軌（EMA20 − k × ATR10）**
    作為波動率自適應的超賣偵測機制：
        - ATR 隨近期實際波幅動態擴張/收縮，自動調整「超賣」門檻
        - 高波動環境下通道變寬，避免假訊號；低波動環境下通道變窄，仍能觸發
        - 對 IBIT 3.17% 日波動特別適合，因 BTC 波動週期差異極大（2024 平穩 vs
          2025 震盪），固定回檔百分比門檻難以兩全

    保留回檔深度過濾（防止 Keltner 下軌在淺回調時誤觸發）與 Close > Open 反轉
    K 線過濾（確認日內買方回來）。整體目標：在 Part A/B 兩段產生更平衡的
    訊號頻率，降低 A/B 累計差距至 < 30%。

策略方向：均值回歸（波動率自適應下軌 + 回檔深度 + 反轉確認）
    Strategy direction: Mean reversion (volatility-adaptive lower band + pullback
    depth + reversal bar confirmation)

迭代歷程（Iteration Log）：

Att1（Baseline）—— 2.0 × ATR 通道 + 10 日回檔 8-25%
    進場：Close < EMA20 − 2.0 × ATR10 + 10d Pullback [-8%, -25%] + Close > Open + cd=10
    出場：TP +4.5% / SL -4.0% / 15 天（沿用 IBIT-006 已驗證出場參數）
    結果：Part A n=2, WR 100%, +9.20%, Sharpe 0.00（零方差 2/2 達標）；
          Part B n=3, WR 33%, -3.97%, Sharpe -0.31；Part C n=1 -4.14%
    失敗分析：Keltner 下軌 2.0×ATR 對 IBIT 3.17% 日波動過於敏感，產生
        超前/淺觸發訊號。2024-07-05、2024-08-05 達標但訊號過少（Part A 僅 2 筆
        vs IBIT-006 Att2 的 4 筆）。Part B 2025-02-28 立即 -4.14%（同 IBIT-006
        Att2 之停損日）；**新增 2025-11-18 停損**是 Keltner 觸發早於 gap-down
        的缺點——IBIT-006 該時段觸發於 2025-11-21（TP +4.5%），gap-down
        過濾器延後進場避開 2025-11-18 的下跌延續。
    min(A,B) = min(0.00, -0.31) = -0.31（遠低於 IBIT-006 Att2 的 0.40）

Att2（Tight Entry）—— 加入 WR(10) ≤ -80 + 深回檔 10-25%
    進場：Close < EMA20 − 2.0 × ATR10 + 10d Pullback [-10%, -25%] + Close > Open
          + WR(10) ≤ -80 + cd=10
    出場：同 Att1
    結果：**與 Att1 完全相同** Part A n=2 100% WR +9.20% Sharpe 0.00 / Part B
          n=3 33% WR -3.97% Sharpe -0.31
    失敗分析：WR(10) ≤ -80 和 pullback -10% 在 Keltner 觸發訊號上皆為**非綁定
        條件**——Keltner Lower 2.0×ATR 觸發已隱含極端超賣與深度回檔，這兩個
        額外過濾器不改變訊號集。確認 Keltner 下軌本身已包含 WR/pullback 資訊。
    min(A,B) = min(0.00, -0.31) = -0.31

Att3（Deeper Keltner + Shorter WR）—— 2.5 × ATR + WR(5) ≤ -80
    進場：Close < EMA20 − 2.5 × ATR10 + 10d Pullback [-10%, -25%] + Close > Open
          + WR(5) ≤ -80 + cd=10
    出場：同 Att1
    結果：Part A n=0（**訊號數歸零**）；Part B n=1 WR 100% +4.50% Sharpe 0.00
          （零方差）；Part C n=0
    失敗分析：Keltner 2.5×ATR 對 IBIT 過深，Part A 2024 年波動平穩期從未觸
        達 EMA20 − 2.5×ATR10 深度。Part B 僅剩 2025-11-21 一筆勝利訊號
        （恰巧同 IBIT-006 Att2 的贏家日）。訊號樣本過薄，無統計意義。
    min(A,B) = min(0.00, 0.00) = 0.00

總結（結論）：三次迭代均未超越 IBIT-006 Att2 的 0.40。**IBIT 第七次失敗的
    策略類型**（繼均值回歸 RSI(2)、突破、波動率自適應、2日急跌、短期動量、
    SL-8% 之後）。核心失敗根因：

    1. **Keltner Lower Band 不等於 Gap-Down Capitulation**：Keltner 基於收盤價
       相對 EMA 的 ATR 偏離，在 BTC 24/7 市場的「盤外持續拋壓」情境下觸發
       太晚（慢磨下跌已形成後才觸發，反而捕捉到續跌開端）。Gap-down 捕捉的
       是「盤外拋壓完成 → 美股盤中撿便宜」的瞬間結構性不對稱，Keltner 無法
       複製此結構。

    2. **WR(10)/Pullback 對 Keltner 訊號非綁定**：Keltner 下軌觸發本身已隱含
       極端超賣與深回檔，疊加同類過濾器毫無區分力（Att2 驗證）。

    3. **高波動下 Keltner 門檻無兩全**：2.0×ATR 過淺（假訊號多，Att1/2），
       2.5×ATR 過深（Part A 歸零，Att3）。IBIT 3.17% 日波動使 Keltner 參數
       空間狹窄。

    **跨資產啟示**：Keltner Channel Lower Band Mean Reversion（EMA − k×ATR
    下軌觸發）對高波動加密 ETF（vol > 3%）失敗。GLD-005 的成功（日波動
    1.12%）無法線性移植至 IBIT，因為低波動資產的慢磨下跌觸發 Keltner 後常
    有技術性反彈，而高波動加密資產的觸發常伴隨續跌動能。**確認 IBIT-006
    Att2 Gap-Down + 日內反轉仍為 IBIT 全域最優**（7 次實驗、21+ 次嘗試）。

資產特性：IBIT 日波動 3.17%，GLD 比率 2.64x。
    最終參數（Att3）：
    進場：Keltner 下軌 2.5×ATR + 10 日回檔 10-25% + Close > Open + WR(5) ≤ -80
    出場：TP +4.5% / SL -4.0% / 最長持倉 15 天
    冷卻：10 天
    無追蹤停損（日波動 3.17% 禁用區域，cross-asset lesson #2）

資產特性：IBIT 日波動 3.17%，GLD 比率 2.64x。
    進場：Keltner 下軌觸及 + 10 日回檔 8-25% + Close > Open
    出場：TP +4.5% / SL -4.0% / 最長持倉 15 天
    冷卻：10 天
    無追蹤停損（日波動 3.17% 禁用區域，cross-asset lesson #2）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IBIT007Config(ExperimentConfig):
    """IBIT-007 Keltner 通道下軌均值回歸參數"""

    # Keltner 通道參數
    ema_period: int = 20
    atr_period: int = 10
    keltner_multiplier: float = 2.5  # Att3：加深至 2.5×ATR

    # 回檔深度過濾（避免淺回調假訊號）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10  # 10日回檔 <= -10%
    pullback_upper: float = -0.25  # 回檔上限 25%（過濾崩盤極端值）

    # Williams %R 超賣確認（Att3：短窗 WR(5)）
    wr_period: int = 5  # Att3：WR(5) 短期極端超賣
    wr_threshold: float = -80.0  # Williams %R <= -80

    # 冷卻
    cooldown_days: int = 10


def create_default_config() -> IBIT007Config:
    return IBIT007Config(
        name="ibit_007_keltner_lower_mr",
        experiment_id="IBIT-007",
        display_name="IBIT Keltner Lower Band Mean Reversion",
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
