"""
TLT Yield-Velocity-Gated Mean Reversion 訊號偵測器 (TLT-009)

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 >= pullback_threshold 且 <= pullback_upper
2. Williams %R(wr_period) <= wr_threshold（超賣）
3. 收盤位置 >= close_position_threshold（日內反轉）
4. ^TNX yield_lookback 日變化（pp）<= max_yield_change（calm rate regime 閘門）
5. （可選）BB(bb_period, bb_std) 寬度 / Close < max_bb_width_ratio（Att2+ 啟用）
6. 冷卻期 cooldown_days 天

^TNX 為 CBOE 10-Year Treasury Note Yield Index，報價單位為 %。
N 日變化（Close_T − Close_T−N）以 pp 計算，0.15 pp = 15bps。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tlt_009_yield_velocity_mr.config import TLT009Config

logger = logging.getLogger(__name__)


class TLT009SignalDetector(BaseSignalDetector):
    """TLT-009：回檔+WR+反轉K線 + ^TNX yield velocity gate（可選 BB 寬度 hybrid）"""

    def __init__(self, config: TLT009Config):
        self.config = config

    def _fetch_yield_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.yield_ticker,
                start=start_date,
                progress=False,
                auto_adjust=True,
            )
            if df is None or df.empty:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            return df
        except Exception:
            logger.exception("Failed to fetch %s yield data", self.config.yield_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # === 外部 yield 數據 ===
        start_date = df.index[0].strftime("%Y-%m-%d")
        yld_df = self._fetch_yield_data(start_date)

        if yld_df is None or yld_df.empty:
            logger.error("無法取得 %s 數據，yield gate 將全部放行", self.config.yield_ticker)
            df["Yield_Change_N"] = 0.0
        else:
            # 對齊交易日：用 TLT 的 index 做 reindex + ffill（少數 ^TNX 缺資料的日子繼承前一日）
            yld_close = yld_df["Close"].reindex(df.index).ffill()
            df["Yield_Close"] = yld_close
            df["Yield_Change_N"] = yld_close - yld_close.shift(self.config.yield_lookback)

        # === 回檔幅度 ===
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # === Williams %R ===
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # === 收盤位置 ===
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # === BB 寬度（Att2+ hybrid 時啟用）===
        bb_n = self.config.bb_period
        bb_k = self.config.bb_std
        sma = df["Close"].rolling(bb_n).mean()
        std = df["Close"].rolling(bb_n).std()
        df["BB_Upper"] = sma + bb_k * std
        df["BB_Lower"] = sma - bb_k * std
        df["BB_Width_Ratio"] = (df["BB_Upper"] - df["BB_Lower"]) / df["Close"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback_min = df["Pullback"] <= self.config.pullback_threshold
        cond_pullback_max = df["Pullback"] >= self.config.pullback_upper
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold

        # Yield gate：^TNX N 日變化 <= max_yield_change
        cond_yield = df["Yield_Change_N"] <= self.config.max_yield_change
        # 若 yield 數據缺失（全 0.0），仍滿足 <= 0.15，相當於放行（保持實驗可重現）

        # BB 寬度 gate（Att2+ 才啟用）
        if self.config.max_bb_width_ratio is not None:
            cond_bb = df["BB_Width_Ratio"] < self.config.max_bb_width_ratio
        else:
            cond_bb = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback_min & cond_pullback_max & cond_wr & cond_reversal & cond_yield & cond_bb
        )

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
            logger.info("TLT-009: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("TLT-009: Detected %d yield-gated MR signals", signal_count)
        return df
