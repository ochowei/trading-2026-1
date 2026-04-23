"""
SIVR-016：Williams Vix Fix 資本化均值回歸配置
(SIVR Williams Vix Fix Capitulation Mean Reversion Config)

動機（Motivation）：
    URA-010 Att3 在 URA 2.34% vol 上驗證「WVF + 10d 深回檔」產生 Part A Sharpe
    0.68 (in-sample 最高)，但 Part B 0.04（政策驅動導致 post-peak regime
    失效）。URA-010 明確列出跨資產假設：
        "模式可能適用於 Part A/B 兩段皆活躍 MR regime 的高波動資產
        （SIVR/COPX 待跨資產驗證）"

    SIVR 2.34% vol、GLD 比率 1.5-2x、Part A（2019-2023 含 COVID + 2022 熊市）
    與 Part B（2024-2025 銀價避險/Fed 降息期）兩段皆維持活躍 MR regime
    （SIVR-015 Att1 驗證 min(A,B) 0.48 平衡於兩段）。WVF 作為
    capitulation-depth 深度指標（非 turn-up），結構性與 oscillator hook
    不同——在 SIVR 上預期可區分「真正恐慌折價」vs「淺磨損緩跌」。

    本實驗為 **repo 第 2 次 WVF 試驗**（URA-010 後首次），亦為 WVF 在
    SIVR（白銀 ETF、避險/工業雙屬性）上的首次嘗試。挑戰 SIVR-015 Att1
    全域最優（min(A,B) 0.48）。

策略方向：均值回歸（capitulation depth detection，非 reversal confirmation）
    Strategy direction: Mean reversion via capitulation-depth detection

========================================================================
迭代計畫（Iteration Plan，2026-04-23，成交模型 0.15% slippage）：
========================================================================

Att1（baseline）：WVF(22) > BB_upper(WVF,20,2.0) + 10d pullback [-7%,-20%]
                   + cd=10 + SIVR 全域最優出場 (TP+3.5%/SL-3.5%/20天)
    目標：驗證 WVF 在 SIVR 上的基礎 capitulation-depth 選擇力

Att2（若 Att1 失敗）：加深回檔下限至 -10%（URA-010 Att3 方向移植）
    假設：WVF 對淺回檔仍可觸發；加深 pullback 至 -10% 提升訊號品質

Att3（若 Att1/Att2 未勝過基線）：WVF + pullback + SIVR-015 Att1 的
    RSI(14) bullish hook 過濾（double capitulation + divergence confirmation）
    結構性混合：capitulation depth 作為必要條件，divergence 作為精煉

資產特性：SIVR 日波動 2.34%，GLD 比率 1.5-2x。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVR016Config(ExperimentConfig):
    """SIVR-016 Williams Vix Fix 資本化均值回歸參數"""

    # WVF 主訊號（同 URA-010）
    wvf_lookback: int = 22  # 折價深度回看 N 日
    wvf_bb_lookback: int = 20  # WVF 序列的 BB 計算窗口
    wvf_bb_stddev: float = 2.0  # BB 標準差倍數（突破上軌即 capitulation）

    # 回檔深度過濾（Att2：收緊至 -10% 深回檔，URA-010 Att3 方向）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10  # 10d 高點回檔 ≥ 10%（Att2 加深）
    pullback_upper: float = -0.20  # 回檔上限 20%（過濾結構性崩盤）

    # RSI(14) bullish hook（Att3 選用；Att1/Att2 設 enabled=False）
    rsi_hook_enabled: bool = False
    rsi_period: int = 14
    rsi_hook_lookback: int = 5
    rsi_hook_delta: float = 3.0
    rsi_hook_max_min: float = 35.0

    # 冷卻
    cooldown_days: int = 10


def create_default_config() -> SIVR016Config:
    return SIVR016Config(
        name="sivr_016_wvf_capitulation_mr",
        experiment_id="SIVR-016",
        display_name="SIVR Williams Vix Fix Capitulation MR",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（SIVR 全域最優對稱出場）
        stop_loss=-0.035,  # -3.5%
        holding_days=20,
    )
