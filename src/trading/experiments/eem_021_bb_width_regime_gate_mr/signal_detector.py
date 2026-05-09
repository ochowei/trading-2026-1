"""
EEM-021 訊號偵測器：BB-Width Regime Gate on Vol-Transition MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. Close <= BB(20, 2.0) 下軌（同 EEM-014）
2. 10 日高點回檔 >= -7%（崩盤隔離，同 EEM-014）
3. Williams %R(10) <= -85（同 EEM-014）
4. ClosePos >= 40%（同 EEM-014）
5. ATR(5)/ATR(20) > 1.10（signal-day panic，同 EEM-014）
6. 2 日收盤報酬 <= -0.5%（2DD floor，同 EEM-014 Att2）
7. **BB(20, 2) 寬度 / Close < max_bb_width_ratio**（EEM-021 核心新增 — vol regime gate）
   — 或 use_bb_width_floor=True 時改為 BB_Width_Ratio > bb_width_floor（反向）
8. 冷卻期 10 個交易日

設計依據：
- BB-Width Ratio 為 4σ 寬度標準化指標，捕捉「20 日波動率 regime」
- CAP 方向（< threshold）排除「vol expansion regime」訊號（EM 危機進行中）
- FLOOR 方向（> threshold）僅保留 vol expansion regime 訊號（用於 Att3 反向測試）
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.eem_021_bb_width_regime_gate_mr.config import EEM021Config

logger = logging.getLogger(__name__)


class EEM021BBWidthRegimeDetector(BaseSignalDetector):
    """EEM-021 BB-Width Regime Gate on Vol-Transition MR Detector"""

    def __init__(self, config: EEM021Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_upper"] = df["BB_mid"] + self.config.bb_std * df["BB_std"]
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # BB-Width Ratio（EEM-021 核心新增）
        # = (BB_Upper - BB_Lower) / Close = 4σ 寬度標準化（與 TLT-007/TQQQ-018/SOXL-012 一致）
        df["BB_Width_Ratio"] = (df["BB_upper"] - df["BB_lower"]) / df["Close"]

        # 10 日高點回檔（崩盤隔離）
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / day_range).where(day_range > 0, 0.5)

        # ATR ratio
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr_short = tr.rolling(self.config.atr_short_period).mean()
        atr_long = tr.rolling(self.config.atr_long_period).mean()
        df["ATR_Ratio"] = atr_short / atr_long.where(atr_long > 0, float("nan"))

        # 2 日收盤報酬（2DD floor）
        df["TwoDayReturn"] = df["Close"] / df["Close"].shift(2) - 1

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_twoday_floor = df["TwoDayReturn"] <= self.config.twoday_return_floor

        # BB-Width Regime Gate（CAP 或 FLOOR）
        if self.config.use_bb_width_floor:
            cond_regime = df["BB_Width_Ratio"] > self.config.bb_width_floor
        else:
            cond_regime = df["BB_Width_Ratio"] < self.config.max_bb_width_ratio

        signal = (
            cond_bb
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_twoday_floor
            & cond_regime
        )
        df["Signal"] = signal.fillna(False)

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
            logger.info("EEM-021: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        regime_label = (
            f"floor>{self.config.bb_width_floor:.3f}"
            if self.config.use_bb_width_floor
            else f"cap<{self.config.max_bb_width_ratio:.3f}"
        )
        logger.info(
            "EEM-021: Detected %d signals (BB-Width %s)",
            signal_count,
            regime_label,
        )
        return df
