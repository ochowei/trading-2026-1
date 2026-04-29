"""
EEM-013: MACD Histogram Bullish Turn + Pullback Hybrid Mean Reversion
(EEM MACD 柱狀圖多頭轉折 + 回檔混合進場均值回歸)

策略方向：**Repo 首次 MACD 試驗**，填補「MACD momentum indicator」方向空白。

設計邏輯：
- MACD(12, 26, 9) 柱狀圖多頭轉折：today > yesterday > day-before，且 yesterday < 0
  （兩根連續上揚仍處於負值區，代表賣壓衰竭中動量正在轉折，但尚未完成反轉）
- 搭配 10 日回檔 [-8%, -2%]：確保訊號發生在淺至中等回撤情境
- 搭配 WR(10) ≤ -75 + ClosePos ≥ 40%：EEM 驗證有效的超賣 + 日內反轉確認
- 對 EEM 1.17% vol 屬中低波動，MACD 平滑 EMA-based 訊號可過濾 1-2 日假反彈

對照既有 EEM 策略：
- EEM-012 Att3 當前最佳：BB lower + cap + WR + ClosePos + ATR，min(A,B) 0.34
- RSI(2) 類：EEM-003 Att2 min 0.06（受 EM 結構性事件拖累）
- BB Squeeze 類：EEM-005 Att2 min 0.18
- 趨勢/RS 動量：EEM-006/007 均市場狀態依賴失敗

對照跨資產 MACD / oscillator hook 家族：
- INDA-009（CCI turn-up）、URA-008/TLT-006（RSI hook）、XBI-011（RSI hook on event-driven）
  均失敗於 lesson #20b（V-bounce ≠ genuine reversal）
- 關鍵差異：MACD 為 EMA 差值，比 RSI/CCI 點估計更平滑；且 MACD 雙時框（12/26）
  可捕捉 EM 中週期動能轉折，不依賴單日 price action
- SIVR-015 RSI hook 成功於 2-3% vol + 10日回檔框架 + 活躍 MR regime
- 預期：EEM broad EM risk-on/risk-off 結構可能適合 MACD 平滑訊號，但 Part B
  2024-2025 EM 強牛市中 MR 機會稀少是根本限制

目標：min(A,B) > 0.34（超越 EEM-012 Att3），A/B 訊號比 1.0-1.5:1，
      A/B 累計差 < 30%。

疊代歷史：
- Att1: MACD 柱狀圖零軸上穿 + 10日回檔 [-7%, -3%] + WR ≤ -70 + ClosePos ≥ 40%
        + cd=10 → **Part A/B 各 0 訊號**（零軸上穿嚴重滯後，此時 WR 已回升）
- Att2: MACD 柱狀圖兩根連續上揚（today > yesterday > day-2，yesterday < 0）
        + 10日回檔 [-8%, -2%] + WR ≤ -75 + ClosePos ≥ 40% + cd=10
        → Part A 8 訊號 WR 50% 累計 -0.77% Sharpe -0.02（4 TP / 4 SL，
          2022-2023 升息熊市 SL 集中：2022-09/10、2023-02）
          Part B 3 訊號 WR 66.7% 累計 +2.80% Sharpe 0.34 / min(A,B) -0.02
        → 失敗根因：MACD 雙 EMA turn-up 在 2022-2023 升息熊市中頻繁假訊號
          （dead-cat bounce），WR 濾波不足以區分真假反轉
- Att3 (default ★): Att2 + ATR(5)/ATR(20) < 1.10（**反向 ATR 過濾**，
        EEM-013 獨特發現：MACD 框架偏好低波動環境，與 RSI(2) 框架相反）
        → Part A 5 訊號 WR 60% 累計 +2.60% Sharpe 0.19（2019-05-21 TP、
          2022-09 SL、2023-02 SL、2023-08 TP、2023-10 TP）
          Part B 2 訊號 WR 100% 累計 +6.09% Sharpe 0.00（零方差，2024-04/11 皆 TP）
          min(A,B) 0.00（Part B 零方差），Part A Sharpe 0.19 < EEM-012 Att3 的 0.34
        → 反向 ATR 過濾確實提升 Part A WR（50% → 60%）且符合預期（移除 2019-05-15、
          2022-10、2024-07 三筆 ATR > 1.10 的 SL），但 Part A 仍保留 2 筆 SL
          （2022-09-08 ATR 1.04、2023-02-14 ATR 0.88）為低 ATR 環境的熊市續跌

**最終結論**：三次迭代均未勝過 EEM-012 Att3（min(A,B) 0.34）

**失敗分析**：
1. MACD 柱狀圖零軸上穿（經典 MACD 訊號）嚴重滯後，進場時 price 已恢復，
   WR/pullback 條件失效
2. MACD 兩根連續 turn-up（較靈敏）在 2022-2023 升息熊市中與 RSI/CCI hook 同類
   失敗於 lesson #20b 家族（V-bounce ≠ genuine reversal）
3. 反向 ATR 過濾（ATR<1.10）為 EEM-013 獨特發現——MACD 框架偏好低波動環境
   （與 EEM-010 RSI(2) 框架的 ATR>1.15 方向完全相反）。過濾提升 Part A WR
   至 60% 但 Part B 淪為 2/2 零方差
4. EEM 在 MACD 框架下 Part B 訊號過少（1/yr）使零方差成為結構性限制

**Repo 首次 MACD 試驗**：擴展 lesson #20b 失敗家族至 MACD 柱狀圖 turn-up
（加入 RSI hook、CCI hook、WVF capitulation 已驗證失效的 oscillator 家族）。
新增跨資產假設：MACD 平滑 EMA 訊號在持續性升息/升息滯後期（2022-2023）仍無法
區分 bear rally dead-cat bounce 與 genuine reversal，smoothing 不足以解決
V-bounce 根本問題。**EEM MR 在 BB Lower + cap 混合進場外的其他進場機制均結構性受限。**

EEM 硬上限（必須遵守）：
- SL 禁放寬至 -3.5% 以下（lesson #49：EEM 停損為結構性崩潰，寬 SL 增加虧損）
- TP 禁高於 +3.0%（EEM-005 Att1 驗證 TP 3.5% 到期過多）
- 禁用 SMA(200) 政權過濾（EEM-007 Att3 驗證 Part A -0.92）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM013Config(ExperimentConfig):
    """EEM-013 MACD 柱狀圖零軸上穿 + 回檔混合進場參數"""

    # MACD 參數（標準 12/26/9，EMA-based）
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9

    # 10 日回檔過濾（確保訊號在回檔後出現）
    pullback_lookback: int = 10
    pullback_floor: float = -0.02  # 至少 -2% 回檔（確保已有走弱情境）
    pullback_cap: float = -0.08  # 不深於 -8%（EM 崩盤隔離）

    # 品質過濾（EEM 驗證有效）
    wr_period: int = 10
    wr_threshold: float = -75.0  # 放寬（MACD 雙 EMA 已提供主訊號）
    close_position_threshold: float = 0.40

    # 反向 ATR 過濾：MACD 框架偏好低波動環境（與 RSI(2) 框架相反）
    # EEM-013 Att2 分析揭示 MACD 動量轉折在 ATR 飆升期多為 bear rally 假訊號
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_max: float = 1.10  # ATR(5)/ATR(20) < 1.10 過濾 bear market 假訊號

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> EEM013Config:
    return EEM013Config(
        name="eem_013_macd_histogram_mr",
        experiment_id="EEM-013",
        display_name="EEM MACD Histogram Zero-Cross + Pullback MR",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（EEM 上限）
        stop_loss=-0.030,  # -3.0%（EEM 停損為結構性崩潰，寬 SL 無效）
        holding_days=20,
    )
