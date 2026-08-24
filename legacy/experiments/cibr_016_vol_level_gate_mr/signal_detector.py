"""
CIBR-016 訊號偵測器：Volatility-Level-Regime-Gated BB-Lower Pullback-Cap MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. Close <= BB(20, 2.0) 下軌（沿用 CIBR-008）
2. 10 日高點回檔 >= pullback_cap（沿用 CIBR-008）
3. WR(10) <= -80（沿用 CIBR-008）
4. ClosePos >= 0.40（沿用 CIBR-008）
5. ATR(5)/ATR(20) > 1.15（沿用 CIBR-008 相對 acceleration）
6. ATR(14)/Close <= max_atr_pct（CIBR-016 核心新增絕對 LEVEL 閘門）
7. 冷卻期 cooldown_days 個交易日
"""

import logging

import pandas as pd

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_016_vol_level_gate_mr.config import CIBR016Config

logger = logging.getLogger(__name__)


class CIBR016SignalDetector(BaseSignalDetector):
    """CIBR-016：CIBR-008 框架 + 絕對波動率 LEVEL regime 閘門"""

    def __init__(self, config: CIBR016Config):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        daily_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / daily_range).where(daily_range > 0, 0.5)

        prev_close = df["Close"].shift(1)
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - prev_close).abs(),
                (df["Low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_fast"] = tr.rolling(self.config.atr_fast).mean()
        df["ATR_slow"] = tr.rolling(self.config.atr_slow).mean()
        df["ATR_ratio"] = df["ATR_fast"] / df["ATR_slow"].where(df["ATR_slow"] > 0, float("nan"))

        # CIBR-016：絕對波動率 LEVEL（與 ATR_ratio acceleration 正交）
        df["ATR_Pct"] = tr.rolling(self.config.atr_level_period).mean() / df["Close"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_atr = df["ATR_ratio"] > self.config.atr_ratio_threshold

        if self.config.use_vol_level_gate:
            cond_vol_level = df["ATR_Pct"] <= self.config.max_atr_pct
        else:
            cond_vol_level = pd.Series(True, index=df.index)

        df["Signal"] = cond_bb & cond_cap & cond_wr & cond_closepos & cond_atr & cond_vol_level

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
            logger.info("CIBR-016: %d signals suppressed by cooldown", len(suppressed))

        logger.info(
            "CIBR-016: Detected %d signals (vol-level-gated BB-lower pullback-cap)",
            int(df["Signal"].sum()),
        )
        return df
