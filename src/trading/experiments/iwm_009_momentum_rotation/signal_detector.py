"""
IWM-009 訊號偵測器：Small-Cap Momentum Pullback (IWM/SPY)

進場條件（全部滿足）：
1. IWM 20 日報酬 - SPY 20 日報酬 >= 3%（小型股正在跑贏）
2. IWM 5 日報�� <= -2%（短期回檔）
3. Close > SMA(50)（趨勢確認）
4. 冷卻期 10 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.iwm_009_momentum_rotation.config import IWM009Config

logger = logging.getLogger(__name__)


class IWM009SignalDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """IWM/SPY Small-Cap Momentum Pullback 訊��偵測器"""

    def __init__(self, config: IWM009Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.pair_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        spy_df = self.require_auxiliary(self.config.pair_ticker, df.index)

        # 計算 20 日相對報酬（IWM 跑贏 SPY 程度）
        n = self.config.relative_return_lookback
        iwm_ret = df["Close"].pct_change(n)
        spy_ret = spy_df["Close"].pct_change(n)
        df["Relative_Return"] = iwm_ret - spy_ret

        # 計算短期回檔（5 日報酬）
        df["Pullback"] = df["Close"].pct_change(self.config.pullback_days)

        # SMA 趨勢確認
        df["SMA"] = df["Close"].rolling(self.config.sma_period).mean()

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 相對強勢：IWM 跑贏 SPY
        cond_outperform = df["Relative_Return"] >= self.config.relative_outperform_threshold
        # 短期回檔
        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        # 趨勢確認
        cond_trend = df["Close"] > df["SMA"]

        df["Signal"] = cond_outperform & cond_pullback & cond_trend

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

        signal_count = df["Signal"].sum()
        logger.info("IWM-009: Detected %d momentum pullback signals", signal_count)
        return df
