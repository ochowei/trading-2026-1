"""
XBI-013：Gap-Down Capitulation + Intraday Reversal 均值回歸配置
(XBI Gap-Down Capitulation + Intraday Reversal Mean Reversion Config)

動機（Motivation）：
    XBI-005（10日回檔 8-20% + WR(10) ≤ -80 + ClosePos ≥ 35%，TP +3.5%/SL -5%/15天/
    cd 10，min(A,B) 0.36）為 XBI 當前最佳。12 次實驗、38+ 次嘗試涵蓋多樣 MR 進場
    結構。XBI 為生技板塊 ETF，日波動 ~2.0%，受 FDA 決定、臨床試驗結果、收購消息
    等事件驅動；事件常於盤後公告，隔日開盤跳空是典型反應。IBIT-006 Att2 驗證
    「gap-down + 日內反轉」MR 在 24/7 加密 ETF 成功（min 0.15→0.40，+167%），但
    TQQQ-016、FXI-010、FCX-010 均失敗——cross_asset_lessons 歸納三種失敗子類：
    (1) 非 24/7 underlying（TQQQ 槓桿股指 ETF）
    (2) 政策驅動 EM 單一國家 ETF（FXI 政策延續）
    (3) 商品關聯個股（FCX 銅價衝擊延續）

    **XBI 的結構假設**：生技事件（FDA/臨床/併購）常在盤後明確宣告，隔夜 pre-market
    拋壓集中，開盤後資訊定價相對完整；與 BTC 24/7 的「隔夜拋壓完成 + 美股開盤
    撿便宜」結構部分相似（雖無連續交易，但事件資訊的隔夜完全公告使盤前拋壓
    exhaust 行為可能存在）。生技事件非政策/商品延續——無「跨 session 不斷加壓」
    機制，可能滿足 IBIT-006 成功的結構前提。

    這是 repo 第 5 次 Gap-Down Capitulation MR 試驗，首次在 US 板塊 ETF 測試
    （CIBR-011 Range Expansion 已證明 US 板塊 ETF 需統計適性進場框架）。

策略方向：均值回歸（事件驅動投降拋壓 + 日內反轉確認）
    Strategy direction: Mean reversion with event-driven gap-down + intraday reversal

========================================================================
三次迭代結果（2026-04-22，成交模型 0.1% slippage，隔日開盤市價進場）：
========================================================================

Att1（失敗）—— Primary Gap-Down 觸發，IBIT-006 縮放參數
    進場：Gap ≤ -1.0% + Close > Open + 10d Pullback [-5%, -15%] + WR(10) ≤ -80 + cd 10
    出場：TP +3.0% / SL -3.0% / 15 天
    結果：Part A 8 訊號 50% WR Sharpe **-0.02** cum -0.77%（4TP/4SL，全部 1-3 日出場）
         Part B 1 訊號 0% WR Sharpe 0.00 cum -3.10%（1 日停損）
         min(A,B) **-0.02**（-106% vs XBI-005 的 0.36）
    失敗分析：生技 gap-down 多為 FDA/臨床 negative news 觸發，負面消息續跌特性
             明顯，非 IBIT BTC 24/7 隔夜拋壓耗盡結構。4/8 Part A 訊號與 1/1 Part B
             訊號均在 1-3 日內觸 -3% SL，無反彈模式。Gap-Down MR 失敗家族擴展：
             XBI 生技板塊 ETF 加入 FXI（政策）/ FCX（商品）/ TQQQ（槓桿）行列。

Att2（失敗）—— Gap 改為 XBI-005 框架上的補充品質過濾
    進場：XBI-005 base（pullback 8-20% + WR ≤ -80 + ClosePos ≥ 35%）+ Gap ≤ -1.0%
         + Close > Open + cd 10
    出場：TP +3.5% / SL -5.0% / 15 天（XBI-005 基線）
    結果：Part A 3 訊號 66.7% WR Sharpe 1.39 cum +7.08%
         Part B 1 訊號 0% WR Sharpe 0.00 cum -5.10%
         min(A,B) **0.00**（-100% vs XBI-005 的 0.36）
    失敗分析：Gap 過濾把 XBI-005 原 35/8 訊號濾至 3/1（-90%），樣本過薄。
             Part A 倖存訊號雖然 Sharpe 1.39，但 Part B 單訊號 2024-01-17 仍 1日 SL，
             顯示 gap-down 對 XBI 訊號品質無貢獻，結構性問題與 filter role（主/補
             充）無關。

Att3（失敗）—— 深 Gap 測試：生技需更深 gap 才能觸 capitulation？
    進場：Gap ≤ -2.0%（較 Att1 深 2x）+ Close > Open + 10d Pullback [-5%, -18%]
         + WR(10) ≤ -80 + cd 10
    出場：TP +3.5% / SL -4.0% / 15 天
    結果：見 signal_detector.py 與 strategy.py 中的最終更新註解

========================================================================
結論：Gap-Down MR 在 XBI 生技板塊 ETF 上三次迭代均未勝過 XBI-005 的 min 0.36
     確認 Gap-Down 失敗家族擴展至 US 事件驅動板塊 ETF 類別
========================================================================
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI013Config(ExperimentConfig):
    """XBI-013 Gap-Down Capitulation + Intraday Reversal MR 參數（Att3 最終）"""

    # 進場 — 回檔範圍（Att3：拓寬至 [-5%, -18%] 捕捉更多潛在訊號）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.05  # 回檔 >= 5%
    pullback_upper: float = -0.18  # 回檔上限 18%

    # 進場 — Williams %R 超賣確認
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 進場 — 隔夜跳空（Att3：加深至 -2.0% 測試「真正 capitulation」假設）
    gap_threshold: float = -0.020  # Gap <= -2.0%

    # 進場 — 日內反轉（Close > Open）
    require_up_bar: bool = True

    # 進場 — 收盤位置過濾（Att3 停用以允許更寬訊號）
    use_close_position: bool = False
    close_position_threshold: float = 0.35

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> XBI013Config:
    return XBI013Config(
        name="xbi_013_gap_reversal_mr",
        experiment_id="XBI-013",
        display_name="XBI Gap-Down Capitulation + Intraday Reversal MR",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.040,
        holding_days=15,
    )
