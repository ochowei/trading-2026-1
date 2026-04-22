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

參數縮放（IBIT-006 → XBI）：
    IBIT 3.17% vol → XBI 2.0% vol，縮放比率 0.63x：
    - Gap threshold: IBIT -1.5% → XBI -1.0%
    - Pullback: IBIT [-12%, -25%] → XBI [-5%, -15%]
    - TP: IBIT +4.5% → XBI +3.0%
    - SL: IBIT -4.0% → XBI -2.5% (rounded to -3.0% for biotech event volatility)
    - 持倉 15 天、冷卻 10 天保持不變

迭代歷程（Iteration Log）：見 signal_detector.py 與 strategy.py 註解

設計要點：
    XBI 生技板塊日波動 ~2.0%，事件驅動 FDA/臨床公告。Gap-down + 日內反轉
    結構假設可能符合 IBIT-006 成功的三個前提（資訊完全公告、無跨 session 延續
    性拋壓機制、短期反彈生物學基礎）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI013Config(ExperimentConfig):
    """XBI-013 Gap-Down Capitulation + Intraday Reversal MR 參數

    Att2（當前）：將 gap 濾波器改為 XBI-005 框架上的「補充品質過濾」，非主訊號。
    """

    # 進場 — 回檔範圍（XBI-005 基線）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.08  # 回檔 >= 8%（XBI-005 base）
    pullback_upper: float = -0.20  # 回檔上限 20%（XBI-005 base）

    # 進場 — Williams %R 超賣確認（XBI-005 基線）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 進場 — 收盤位置過濾（XBI-005 基線）
    close_position_threshold: float = 0.35

    # 進場 — 隔夜跳空（Att2 新增補充過濾，非主訊號）
    gap_threshold: float = -0.010  # Gap <= -1.0%（較寬以保留更多訊號）

    # 進場 — 日內反轉（Close > Open，配合 ClosePos 雙重確認）
    require_up_bar: bool = True

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> XBI013Config:
    return XBI013Config(
        name="xbi_013_gap_reversal_mr",
        experiment_id="XBI-013",
        display_name="XBI Gap-Down Capitulation + Intraday Reversal MR",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（XBI-005 基線）
        stop_loss=-0.050,  # -5.0%（XBI-005 基線）
        holding_days=15,
    )
