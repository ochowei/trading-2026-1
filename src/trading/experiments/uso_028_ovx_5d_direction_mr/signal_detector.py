"""
USO-028 訊號偵測器：^OVX 5d Direction Multi-Window IV Regime Gate MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 in [-12%, -7%]（沿用 USO-013/USO-025/USO-027）
2. RSI(2) < 15（沿用）
3. 2 日報酬 <= -2.5%（signal-day capitulation depth, 沿用）
4. ^OVX 3 日變化 <= +4.0（USO-025 Att3 sweet spot, 沿用）
5. 5 日累計報酬 >= -10%（multi-day persistence dimension, 沿用 USO-027 Att2）
6. ^OVX 5 日變化 <= max_ovx_5d_change（USO-028 核心新增 multi-window IV combo）
7. 冷卻期 10 個交易日

跨資產移植：repo 首次「IV DIRECTION 多時框正交組合」於任何資產，
3d 短期 + 5d 中期雙時框 ^OVX direction 疊加。
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.uso_028_ovx_5d_direction_mr.config import USO028Config

logger = logging.getLogger(__name__)


class USO028SignalDetector(DeclaredAuxiliaryData, BaseSignalDetector):
    """USO-028：USO-027 Att2 框架 + ^OVX 5d direction multi-window IV combo gate"""

    def __init__(self, config: USO028Config):
        self.config = config

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.ovx_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度（沿用）
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # RSI(2)（沿用）
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        period = self.config.rsi_period
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["RSI2"] = 100 - (100 / (1 + rs))

        # 2 日報酬 floor（沿用）
        df["Return_2d"] = df["Close"].pct_change(2)

        # 5 日累計報酬 cap（沿用 USO-027）
        df["Return_5d"] = df["Close"].pct_change(self.config.return_5d_lookback)

        # ^OVX 3d + 5d direction（USO-028 雙時框 IV combo）
        ovx_close = self.require_auxiliary(self.config.ovx_ticker, df.index)["Close"]
        df["OVX_Close"] = ovx_close
        df["OVX_Change_3d"] = ovx_close.diff(self.config.ovx_3d_lookback)
        df["OVX_Change_5d"] = ovx_close.diff(self.config.ovx_5d_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_not_crash = df["Pullback"] >= self.config.pullback_max
        cond_rsi = df["RSI2"] < self.config.rsi_threshold
        cond_drop = df["Return_2d"] <= self.config.drop_2d_threshold

        if self.config.use_ovx_3d_filter:
            ovx_3d = df["OVX_Change_3d"].fillna(-999.0)
            cond_ovx_3d = ovx_3d <= self.config.max_ovx_3d_change
        else:
            cond_ovx_3d = pd.Series(True, index=df.index)

        if self.config.use_return_5d_cap:
            cond_5d_cap = df["Return_5d"] >= self.config.return_5d_min
        else:
            cond_5d_cap = pd.Series(True, index=df.index)

        if self.config.use_ovx_5d_filter:
            ovx_5d = df["OVX_Change_5d"].fillna(-999.0)
            cond_ovx_5d = ovx_5d <= self.config.max_ovx_5d_change
        else:
            cond_ovx_5d = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback
            & cond_not_crash
            & cond_rsi
            & cond_drop
            & cond_ovx_3d
            & cond_5d_cap
            & cond_ovx_5d
        )

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
            logger.info("USO-028: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "USO-028: Detected %d signals (^OVX 3d <= %+.1f, ^OVX 5d <= %+.1f, 5d ret >= %.2f%%)",
            signal_count,
            self.config.max_ovx_3d_change,
            self.config.max_ovx_5d_change,
            self.config.return_5d_min * 100,
        )
        return df
