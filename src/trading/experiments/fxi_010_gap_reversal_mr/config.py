"""
FXI-010: Gap-Down Capitulation + Intraday Reversal Mean Reversion

動機 (Motivation):
    FXI 追蹤香港 H 股，HK 市場於美股盤後交易（HKT 9:30-16:00 = ET 21:30-04:00），
    美股開盤前 HK 市場已完成當日價格發現。重大中國政策/事件消息常導致 FXI 隔夜
    出現結構性跳空下跌，然後美股盤中資金「撿便宜」形成反轉。此與 IBIT（BTC 24/7）
    結構性類似——盤外形成拋壓、盤中資金進場——但在 FXI 上尚未驗證過。

    lesson #52 列出政策驅動 EM 拒斥的反轉結構（BB 下軌 MR、BB Squeeze 突破、
    Stoch 交叉、Failed Breakdown Reclaim）均為「技術形態反轉」；Gap-Down
    Capitulation 為「事件拋壓後反轉」，屬不同機制，值得驗證。

    若成立，此模式可擴展 lesson #20a 的適用範圍至「盤外存在實質價格發現 + 高波動」
    的其他資產（非僅加密 ETF）。

策略方向：均值回歸（事件驅動拋壓 + 日內反轉確認）
    Strategy direction: Mean reversion with overnight event gap + intraday reversal

迭代歷程 (Iteration Log):

Att1 (Baseline) —— 直接移植 IBIT-006 Att2 架構，按 FXI 波動度縮放
    進場：Gap ≤ -1.5% + Close > Open + 10d Pullback [-5%, -15%] + WR(10) ≤ -80 + cd=10
    出場：TP +3.5% / SL -3.0% / 持倉 20 天
    結果：Part A n=22, WR 31.8%, -20.67%, Sharpe -0.33；
          Part B n=4, WR 25.0%, -5.83%, Sharpe -0.51
    失敗分析：FXI 的 HK 隔夜 gap-down 後常因中國政策/經濟消息持續下行，
        與 IBIT（BTC 24/7 價格發現已完成拋壓）結構不同。-1.5% 為 0.75σ
        過鬆，放入大量普通回檔日。22 訊號中 15 停損、7 達標，盈虧比 0.53。
        A/B 訊號比 5.5:1 嚴重不平衡（超出 50% 目標）。
        印證 lesson #52 擴展：政策驅動 EM 亦拒斥 gap-down 資本化結構。

Att2 —— 加嚴 gap 門檻 + 深回檔 + 寬 SL 呼吸空間
    進場：Gap ≤ -2.5% + Close > Open + Close > (High+Low)/2
          + 10d Pullback [-8%, -20%] + WR(10) ≤ -80 + cd=15
    出場：TP +5.5% / SL -5.0% / 持倉 20 天（採 FXI-005 寬出場框架）
    結果：Part A n=5, WR 60.0%, +0.36%, Sharpe 0.04；
          Part B n=1, WR 100%, +5.50%, Sharpe 0.00（1 訊號零方差）
    失敗分析：加嚴後訊號頻率暴跌（22→5, 4→1）。WR 提升至 60%，說明嚴格
        過濾確實能排除壞訊號，但樣本稀薄無統計信心。Part B 僅 1 訊號（年化
        0.5/yr），遠低於可評估閾值。min(A,B) 0.04 遠低於 FXI-005 的 0.38。

Att3 —— Gap-Down 作為近期 capitulation 確認（非 entry trigger）
    思路：iteration 1/2 證明 FXI 的 gap-down 當日本身非可靠進場點（政策
        消息常持續）。改為「5 日內曾發生過 gap-down ≥ -2% 事件」作為確認，
        並疊加 FXI-005 entry（pullback+WR+ClosePos+ATR）過濾，嘗試捕捉
        事件拋壓後市場真正止穩的訊號。
    進場：FXI-005 entry + 近 5 日內至少 1 個 Gap ≤ -2.0% 事件
    出場：TP +5.5% / SL -5.0% / 持倉 20 天（FXI-005 框架）
    結果：Part A n=22, WR 63.6%, +39.08%, Sharpe 0.34；
          Part B n=2, WR 100%, +11.30%, Sharpe 0.00（2 訊號零方差）
    Part C n=1, -0.67%（到期）
    失敗分析：
        1. Part A Sharpe 0.34 接近但未超越 FXI-005 的 0.38
        2. Part B 僅 2 訊號（1.0/yr vs FXI-005 的 3.0/yr），年化訊號頻率
           腰斬；A/B 訊號比 4.4:1 遠超 1.5:1 目標
        3. Part B 2 訊號皆 +5.5% 達標（零方差使 Sharpe 綁定 = 0）
        4. Gap regime filter 選擇了 Part A 的好訊號段（2019-2023 多次政策
           衝擊事件），但 Part B（2024-2025）政策事件稀少，gap regime
           filter 過度收縮訊號頻率
    印證：Gap-down 作為 entry trigger（Att1/Att2）或 regime filter（Att3）
        均無法提升 FXI 整體 Sharpe。擴展 lesson #52：政策驅動 EM 拒斥
        gap-down 資本化結構（無論作為 entry 或 regime），與 BB 下軌 MR、
        BB Squeeze、Stoch 交叉、Failed Breakdown Reclaim 同列禁忌。

結論：FXI-010 三次迭代全部失敗，FXI-005（min 0.38）仍為全域最優。
    FXI-010 最終配置保留 Att3（Part A 最接近基線）以作為 regime filter
    模式的永久記錄，供未來 cross-asset 參考（可能在非政策驅動的高波動
    資產上生效，如 TSLA 盤前事件跳空）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FXI010Config(ExperimentConfig):
    """FXI-010 Gap-Down 資本化 + 日內反轉均值回歸參數"""

    # Gap-down as regime filter (Att3): require recent capitulation event
    # in past N days rather than on entry day itself
    gap_threshold: float = -0.020  # Att3: -2.0% gap event
    gap_lookback: int = 5  # Att3: within past 5 days
    use_gap_as_entry_trigger: bool = False  # Att3: gap as regime filter, not entry trigger

    # Reversal requirement (only used when gap is entry trigger in Att1/Att2)
    require_close_above_midpoint: bool = True

    # Pullback context (10-day high drawdown window, FXI-005 framework)
    pullback_lookback: int = 10
    pullback_threshold: float = -0.05  # Att3: 5% (same as FXI-005)
    pullback_cap: float = -0.12  # Att3: 12% (same as FXI-005)

    # Williams %R oversold
    wr_period: int = 10
    wr_threshold: float = -80.0

    # Close position reversal confirmation (FXI-005 framework)
    close_position_threshold: float = 0.4

    # ATR volatility filter (FXI-005 framework)
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05

    # Cooldown between signals
    cooldown_days: int = 10


def create_default_config() -> FXI010Config:
    return FXI010Config(
        name="fxi_010_gap_reversal_mr",
        experiment_id="FXI-010",
        display_name="FXI Gap-Down Regime-Filtered MR",
        tickers=["FXI"],
        data_start="2010-01-01",
        profit_target=0.055,  # Att3: +5.5% (FXI-005 framework)
        stop_loss=-0.050,  # Att3: -5.0%
        holding_days=20,
    )
