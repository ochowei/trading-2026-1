"""
URA-010：Williams Vix Fix 資本化均值回歸配置
(URA Williams Vix Fix Capitulation Mean Reversion Config)

動機（Motivation）：
    URA-004（10日回檔 10-20% + RSI(2)<15 + 2日跌幅 ≤ -3%）為當前全域最優
    （min(A,B) Sharpe 0.39），URA-008（RSI bullish hook divergence）與
    URA-009（day-after capitulation + 強反轉 K 線）均失敗，根因為政策驅動
    資產上「V-bounce ≠ genuine reversal」——任何「振盪器 turn-up」或
    「單/雙日反轉 K 線」過濾器均無法區分真假反轉。

    本實驗改用 **Larry Williams 的 Vix Fix（WVF）** 作為主進場訊號。WVF
    結構性與 oscillator hook 不同：
        WVF(N) = (max(Close, N) − Low) / max(Close, N) * 100
    它衡量「當下 Low 相對近 N 日最高 Close 的折價深度」，是純粹的
    capitulation 深度指標而非 turn-up 指標。當 WVF 上穿其自身的
    Bollinger 上軌（WVF series 的 BB 帶寬擴張至極值），代表市場處於
    「相對近期最深的 panic 折價」狀態——此時進場屬「在深淵買入」而非
    「等候反彈確認」，避開 hook divergence 失敗的 V-bounce 模式。

策略方向：均值回歸（capitulation depth detection 而非 reversal confirmation）
    Strategy direction: Mean reversion via capitulation-depth detection
    rather than reversal confirmation

迭代歷程（Iteration Log）：
    Att1：WVF(22) > BB_upper(WVF,20,2.0) + 10d pullback [-8%,-25%] + cd=10
          + URA-004 出場（TP +6%/SL -5.5%/20天）

資產特性：URA 日波動 2.34%，GLD 比率 2.11x。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class URA010Config(ExperimentConfig):
    """URA-010 Williams Vix Fix 資本化均值回歸參數"""

    # WVF 主訊號
    wvf_lookback: int = 22  # 折價深度回看 N 日
    wvf_bb_lookback: int = 20  # WVF 序列的 BB 計算窗口
    wvf_bb_stddev: float = 2.0  # BB 標準差倍數（突破上軌即 capitulation）

    # 回檔深度過濾（隔離極端崩盤 + 確保深回撤）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10  # Att3：10d 高點回檔 ≥ 10%（沿用 URA-004 標準）
    pullback_upper: float = -0.25  # 回檔上限 25%（過濾結構性崩盤）

    # 2 日急跌過濾（Att2 新增 — 沿用 URA-004 已驗證的恐慌過濾器）
    two_day_decline: float = -0.03  # 2 日跌幅 ≤ -3%

    # 冷卻
    cooldown_days: int = 10


def create_default_config() -> URA010Config:
    return URA010Config(
        name="ura_010_wvf_capitulation_mr",
        experiment_id="URA-010",
        display_name="URA Williams Vix Fix Capitulation MR",
        tickers=["URA"],
        data_start="2010-01-01",
        profit_target=0.060,  # +6.0%（沿用 URA-004）
        stop_loss=-0.055,  # -5.5%（沿用 URA-004）
        holding_days=20,
    )
