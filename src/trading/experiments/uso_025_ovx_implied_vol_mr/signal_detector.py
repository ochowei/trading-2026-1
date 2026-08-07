"""
USO-025 訊號偵測器：^OVX Implied-Volatility Forward-Looking Regime-Gated MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 in [-12%, -7%]（同 USO-013）
2. RSI(2) < 15（同 USO-013）
3. 2 日報酬 <= -2.5%（同 USO-013）
4. ^OVX 3 日變化 <= +5.0（USO-025 核心新增 forward-looking implied vol gate）
5. 冷卻期 10 個交易日

跨資產移植自 XLU-013（2026-05-02）+ GLD-015（2026-05-02），測試 ^OVX DIRECTION
filter 在 USO 2.2% vol commodity event-driven ETF 的有效性。
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.uso_025_ovx_implied_vol_mr.config import USO025Config

logger = logging.getLogger(__name__)


class USO025SignalDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """USO-025：USO-013 框架 + ^OVX forward-looking implied vol DIRECTION gate"""

    def __init__(self, config: USO025Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.ovx_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度（同 USO-013）
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(2)（同 USO-013）
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        period = self.config.rsi_period
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["RSI2"] = 100 - (100 / (1 + rs))

        # 2 日報酬（同 USO-013）
        df["Return_2d"] = df["Close"].pct_change(2)

        # ^OVX forward-looking implied vol gate（USO-025 核心新增）
        ovx_close = self.require_auxiliary(self.config.ovx_ticker, df.index)["Close"]
        df["OVX_Close"] = ovx_close
        df["OVX_Change_Nd"] = ovx_close.diff(self.config.ovx_direction_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_not_crash = df["Pullback"] >= self.config.pullback_max
        cond_rsi = df["RSI2"] < self.config.rsi_threshold
        cond_drop = df["Return_2d"] <= self.config.drop_2d_threshold

        if self.config.use_ovx_direction_filter:
            # NaN 視為通過（fallback 為包容，避免無 OVX 數據日全部過濾）
            ovx_change = df["OVX_Change_Nd"].fillna(-999.0)
            cond_ovx_dir = ovx_change <= self.config.max_ovx_change
        else:
            cond_ovx_dir = pd.Series(True, index=df.index)

        df["Signal"] = cond_pullback & cond_not_crash & cond_rsi & cond_drop & cond_ovx_dir

        # Cooldown
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
            logger.info("USO-025: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "USO-025: Detected %d ^OVX-implied-vol-direction-gated MR signals",
            signal_count,
        )
        return df
