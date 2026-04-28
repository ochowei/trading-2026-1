"""
INDA-009 訊號偵測器：CCI 超賣反轉均值回歸

進場條件（全部滿足）：
1. CCI(20) <= cci_oversold（深度超賣）
2. 今日 CCI - 過去 N 日 CCI 最低點 >= cci_turn_delta（轉折向上確認）
3. （可選）Close > Open（反轉 K 線）
4. （可選）ClosePos >= 閾值（日內反轉強度）
5. 冷卻期

CCI 計算（Commodity Channel Index, Donald Lambert 1980）：
    TP = (High + Low + Close) / 3
    SMA_TP = SMA(TP, period)
    MAD = mean(|TP - SMA_TP|) over period
    CCI = (TP - SMA_TP) / (0.015 * MAD)

常數 0.015 使約 70-80% 的 CCI 值落在 [-100, +100] 區間。
CCI 與 BB/RSI 的差異：使用 MAD 而非 std，對極端值敏感度較低，可達 -200/-300 深度
超賣而不飽和。
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.inda_009_cci_oversold_mr.config import INDA009Config

logger = logging.getLogger(__name__)


class INDA009SignalDetector(BaseSignalDetector):
    def __init__(self, config: INDA009Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # CCI (Commodity Channel Index)
        n = self.config.cci_period
        tp = (df["High"] + df["Low"] + df["Close"]) / 3.0
        sma_tp = tp.rolling(n).mean()
        mad = tp.rolling(n).apply(lambda s: (s - s.mean()).abs().mean(), raw=False)
        df["CCI"] = (tp - sma_tp) / (0.015 * mad)

        # CCI 轉折：今日與過去 N 日最低點差距
        lookback = self.config.cci_turn_lookback
        df["CCI_Min_N"] = df["CCI"].shift(1).rolling(lookback).min()
        df["CCI_Turn"] = df["CCI"] - df["CCI_Min_N"]

        # ClosePos (for optional filter)
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # 10 日高點回檔（Att3 新增：濾除平盤噪音）
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        cond_oversold = df["CCI"] <= cfg.cci_oversold
        cond_turn = df["CCI_Turn"] >= cfg.cci_turn_delta
        cond_pullback = df["Pullback"] <= cfg.pullback_threshold

        signal = cond_oversold & cond_turn & cond_pullback

        if cfg.require_close_gt_open:
            signal = signal & (df["Close"] > df["Open"])

        if cfg.use_close_pos:
            signal = signal & (df["ClosePos"] >= cfg.close_pos_threshold)

        df["Signal"] = signal

        # Cooldown
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap = len(df.loc[last_signal:idx]) - 1
                if gap <= cfg.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False

        signal_count = df["Signal"].sum()
        logger.info("INDA-009: Detected %d CCI oversold reversal signals", signal_count)
        return df
