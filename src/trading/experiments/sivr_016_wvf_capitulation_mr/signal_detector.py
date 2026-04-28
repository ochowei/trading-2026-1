"""
SIVR-016 訊號偵測器：Williams Vix Fix 資本化 + 回檔深度均值回歸
(SIVR-016 Signal Detector: Williams Vix Fix Capitulation + Pullback MR)

進場條件（全部滿足）：
1. WVF(22) 上穿 Bollinger 上軌（WVF series, 20-day BB at 2σ）
   - 表示當前 Low 相對近 22 日最高 Close 的折價達近期極值
2. 10 日高點回檔下限 -7%（深回撤確認）
3. 回檔上限 -20%（隔離結構性崩盤）
4. （Att3 選用）RSI(14) bullish hook: RSI 自過去 5 日低點回升 ≥ 3 點
   且該低點 ≤ 35（oversold）
5. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.sivr_016_wvf_capitulation_mr.config import SIVR016Config

logger = logging.getLogger(__name__)


class SIVR016SignalDetector(BaseSignalDetector):
    """SIVR-016：Williams Vix Fix 資本化訊號偵測器"""

    def __init__(self, config: SIVR016Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Williams Vix Fix
        # WVF(N) = (max(Close, N) − Low) / max(Close, N) * 100
        n = self.config.wvf_lookback
        highest_close = df["Close"].rolling(n).max()
        df["WVF"] = (highest_close - df["Low"]) / highest_close * 100.0

        # WVF 自身的 Bollinger Band 上軌
        m = self.config.wvf_bb_lookback
        k = self.config.wvf_bb_stddev
        wvf_mean = df["WVF"].rolling(m).mean()
        wvf_std = df["WVF"].rolling(m).std(ddof=0)
        df["WVF_BB_Upper"] = wvf_mean + k * wvf_std

        # 10 日高點回檔
        pn = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pn).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(14) bullish hook（Att3 選用）
        if self.config.rsi_hook_enabled:
            rsi_n = self.config.rsi_period
            delta = df["Close"].diff()
            gain = delta.where(delta > 0, 0.0)
            loss = (-delta).where(delta < 0, 0.0)
            avg_gain = gain.rolling(rsi_n).mean()
            avg_loss = loss.rolling(rsi_n).mean()
            rs = avg_gain / avg_loss.replace(0, float("nan"))
            df["RSI"] = 100 - (100 / (1 + rs))
            hook_n = self.config.rsi_hook_lookback
            df["RSI_Min_N"] = df["RSI"].rolling(hook_n).min()
            df["RSI_Hook_Delta"] = df["RSI"] - df["RSI_Min_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_wvf = df["WVF"] > df["WVF_BB_Upper"]
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_upper = df["Pullback"] >= self.config.pullback_upper

        signal = cond_wvf & cond_pullback & cond_upper

        if self.config.rsi_hook_enabled:
            cond_hook_delta = df["RSI_Hook_Delta"] >= self.config.rsi_hook_delta
            cond_hook_oversold = df["RSI_Min_N"] <= self.config.rsi_hook_max_min
            signal = signal & cond_hook_delta & cond_hook_oversold

        df["Signal"] = signal

        # 冷卻機制
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap = len(df.loc[last_signal:idx]) - 1
                if gap <= self.config.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False
            logger.info("SIVR-016: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("SIVR-016: Detected %d WVF capitulation signals", signal_count)
        return df
