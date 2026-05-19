"""
CIBR-017 訊號偵測器：^VIX Implied-Vol Regime BANDS Filter MR

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. Close <= BB(20, 2.0) 下軌（同 CIBR-008 Att2）
2. 10 日高點回檔 >= -12%（崩盤隔離，同 CIBR-008 Att2）
3. Williams %R(10) <= -80（同 CIBR-008 Att2）
4. ClosePos >= 40%（同 CIBR-008 Att2）
5. ATR(5)/ATR(20) > 1.15（panic FLOOR，同 CIBR-008 Att2）
6. ^VIX 收盤值 <= vix_low_threshold OR > vix_high_threshold
   （CIBR-017 新增 BANDS gate：排除中等 VIX 帶；XBI-017 跨資產移植）
7. 冷卻 cooldown_days 個交易日（同 CIBR-008 Att2）

設計依據：lesson #24 family BANDS 變體（XBI-017 Att1 跨資產移植）。
強制前置 trade-level 預分析已記錄於 config.py（CIBR 唯一殘餘 SL
2020-02-24 VIX 25.03 與 winners 交錯，預判 documented-failure）。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_017_vix_bands_mr.config import CIBR017Config

logger = logging.getLogger(__name__)


class CIBR017VixBandsMRDetector(BaseSignalDetector):
    """CIBR-017 訊號偵測器"""

    def __init__(self, config: CIBR017Config):
        self.config = config

    def _fetch_external(self, ticker: str, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                ticker,
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
            logger.exception("Failed to fetch %s data", ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # === Bollinger Bands（同 CIBR-008）===
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # === 10 日高點回檔（同 CIBR-008）===
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # === Williams %R（同 CIBR-008）===
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # === Close Position（同 CIBR-008）===
        daily_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / daily_range).where(daily_range > 0, 0.5)

        # === ATR ratio（同 CIBR-008）===
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_fast"] = tr.rolling(self.config.atr_fast).mean()
        df["ATR_slow"] = tr.rolling(self.config.atr_slow).mean()
        df["ATR_ratio"] = df["ATR_fast"] / df["ATR_slow"].where(df["ATR_slow"] > 0, float("nan"))

        # === ^VIX BANDS gate（CIBR-017 核心新增；XBI-017 跨資產移植）===
        start_date = df.index[0].strftime("%Y-%m-%d")
        vix_df = self._fetch_external(self.config.vix_ticker, start_date)
        if vix_df is None or vix_df.empty:
            logger.error("無法取得 %s 數據，VIX BANDS 過濾停用", self.config.vix_ticker)
            df["VIX_Close"] = float("nan")
        else:
            df["VIX_Close"] = vix_df["Close"].reindex(df.index, method="ffill")

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_pullback = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_atr_floor = df["ATR_ratio"] > self.config.atr_ratio_threshold

        if self.config.use_vix_bands:
            # 排除中等 VIX 帶：通過條件為 VIX <= low OR VIX > high
            cond_vix_bands = (df["VIX_Close"] <= self.config.vix_low_threshold) | (
                df["VIX_Close"] > self.config.vix_high_threshold
            )
        else:
            cond_vix_bands = pd.Series(True, index=df.index)

        signal = cond_bb & cond_pullback & cond_wr & cond_closepos & cond_atr_floor & cond_vix_bands

        df["Signal"] = signal.fillna(False)

        # Cooldown suppression
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
            logger.info(
                "CIBR-017: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "CIBR-017: Detected %d VIX-bands-filtered MR signals",
            signal_count,
        )
        return df
