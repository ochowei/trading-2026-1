"""
EEM-018 訊號偵測器：^VIX BANDS Regime Gate on Vol-Transition MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. Close <= BB(20, 2.0) 下軌（同 EEM-014）
2. 10 日高點回檔 >= -7%（同 EEM-014）
3. Williams %R(10) <= -85（同 EEM-014）
4. ClosePos >= 40%（同 EEM-014）
5. ATR(5)/ATR(20) > 1.10（signal-day panic，同 EEM-014）
6. 2 日收盤報酬 <= -0.5%（2DD floor，同 EEM-014 Att2 甜蜜點）
7. **^VIX 收盤值 <= vix_low_threshold OR > vix_high_threshold**
   （EEM-018 核心新增 BANDS gate：排除中等 VIX 帶 [vix_low, vix_high]）
8. 冷卻期 10 個交易日

設計依據：lesson #24 family BANDS 變體（repo 第 2 次），跨資產移植自
XBI-017 Att1。U-shape regime hypothesis：EEM 在 broad market 兩個極端
regime（低 VIX calm + 高 VIX panic）才有結構性 capitulation MR 助力，
中等 VIX 帶為「complacency creep」regime，EM-specific 壓力（中國政策、
貿易摩擦）下 broad market 無 panic 助力使 MR 失效。

跨資產貢獻：
- repo 第 2 次「lesson #24 family BANDS 變體」應用（XBI-017 為首例）
- 首次 BANDS 變體跨資產移植至 broad EM ETF
- 與 EEM-016（DXY direction）/ EEM-017（EEM-EFA divergence floor）方向正交
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.eem_018_vix_bands_mr.config import EEM018Config

logger = logging.getLogger(__name__)


class EEM018VixBandsMRDetector(BaseSignalDetector):
    """EEM-018 ^VIX BANDS Regime Gate on Vol-Transition MR"""

    def __init__(self, config: EEM018Config):
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

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

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

        # ATR ratio（signal-day panic）
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

        # ^VIX BANDS gate
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
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_twoday_floor = df["TwoDayReturn"] <= self.config.twoday_return_floor

        if self.config.use_vix_bands:
            # 通過條件：VIX <= low OR VIX > high（排除中等 VIX 帶）
            cond_vix_bands = (df["VIX_Close"] <= self.config.vix_low_threshold) | (
                df["VIX_Close"] > self.config.vix_high_threshold
            )
        else:
            cond_vix_bands = pd.Series(True, index=df.index)

        signal = (
            cond_bb
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_twoday_floor
            & cond_vix_bands
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
            logger.info("EEM-018: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "EEM-018: Detected %d signals (vix_low=%.1f, vix_high=%.1f, use_bands=%s)",
            signal_count,
            self.config.vix_low_threshold,
            self.config.vix_high_threshold,
            self.config.use_vix_bands,
        )
        return df
