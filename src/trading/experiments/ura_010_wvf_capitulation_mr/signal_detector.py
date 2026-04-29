"""
URA-010 訊號偵測器：Williams Vix Fix 資本化 + 回檔深度均值回歸
(URA-010 Signal Detector: Williams Vix Fix Capitulation + Pullback MR)

進場條件（全部滿足）：
1. WVF(N) 上穿 Bollinger 上軌（WVF series, M-day BB at k×σ）
   - 表示當前 Low 相對近 N 日最高 Close 的折價達近期極值
2. 10 日高點回檔 ≥ 8%（深回撤確認，過濾淺技術超賣）
3. 回檔上限 ≤ 25%（隔離結構性崩盤）
4. 2 日跌幅 ≤ -3%（Att2 新增；確認近期急速恐慌而非緩慢漂移）
5. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ura_010_wvf_capitulation_mr.config import URA010Config

logger = logging.getLogger(__name__)


class URA010SignalDetector(BaseSignalDetector):
    """URA-010：Williams Vix Fix 資本化訊號偵測器"""

    def __init__(self, config: URA010Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Williams Vix Fix
        # WVF(N) = (max(Close, N) − Low) / max(Close, N) * 100
        n = self.config.wvf_lookback
        highest_close = df["Close"].rolling(n).max()
        df["WVF"] = (highest_close - df["Low"]) / highest_close * 100.0

        # WVF 自身的 Bollinger Band 上軌（M, k×σ）
        m = self.config.wvf_bb_lookback
        k = self.config.wvf_bb_stddev
        wvf_mean = df["WVF"].rolling(m).mean()
        wvf_std = df["WVF"].rolling(m).std(ddof=0)
        df["WVF_BB_Upper"] = wvf_mean + k * wvf_std

        # 10 日高點回檔
        pn = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pn).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # 2 日跌幅
        df["TwoDayDecline"] = df["Close"].pct_change(2)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 條件一：WVF 上穿其自身 BB 上軌（capitulation 深度極值）
        cond_wvf = df["WVF"] > df["WVF_BB_Upper"]

        # 條件二：回檔下限
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold

        # 條件三：回檔上限（隔離結構性崩盤）
        cond_upper = df["Pullback"] >= self.config.pullback_upper

        # 條件四：2 日急跌（Att2 新增）
        cond_decline = df["TwoDayDecline"] <= self.config.two_day_decline

        df["Signal"] = cond_wvf & cond_pullback & cond_upper & cond_decline

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
            logger.info("URA-010: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("URA-010: Detected %d WVF capitulation signals", signal_count)
        return df
