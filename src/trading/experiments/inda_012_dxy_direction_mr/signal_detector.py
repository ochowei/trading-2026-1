"""
INDA-012 訊號偵測器：DXY Direction Filter on Multi-Period Capitulation MR

延伸 INDA-011 Att3 框架，疊加「DXY N 日報酬方向過濾」（lesson #24 family
DIRECTION 變體，repo 首次 DXY direction filter 於單一國家 EM 股票 ETF）。

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 in [-7%, -3%]
2. Williams %R(10) <= -80
3. 收盤位置 >= 40%
4. ATR(5) / ATR(20) > 1.15
5. 2 日報酬 <= -2.0%（沿用 INDA-010 Att3）
6. 3 日報酬 >= -3.0%（沿用 INDA-011 Att3）
7. **DXY N 日報酬 <= max_dxy_change（INDA-012 核心新增：USD 強度方向過濾）**
8. 冷卻期 7 個交易日

DXY 資料於 compute_indicators 內以 yfinance 直接抓取並對齊 INDA 交易日
（沿用 COPX-016 模式，不需覆寫 strategy.run()）。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.inda_012_dxy_direction_mr.config import INDA012Config

logger = logging.getLogger(__name__)


class INDA012SignalDetector(BaseSignalDetector):
    """INDA-012 DXY Direction-Gated Multi-Period Capitulation MR"""

    def __init__(self, config: INDA012Config):
        self.config = config

    def _fetch_dxy_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.dxy_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.dxy_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        day_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / day_range).where(day_range > 0, 0.5)

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

        df["Return_2d"] = df["Close"].pct_change(2)
        df["Return_3d"] = df["Close"].pct_change(3)

        # DXY direction filter（INDA-012 核心新增）
        start_date = df.index[0].strftime("%Y-%m-%d")
        dxy_df = self._fetch_dxy_data(start_date)

        if dxy_df is None or dxy_df.empty:
            logger.error("無法取得 %s 數據，DXY 過濾停用", self.config.dxy_ticker)
            df["DXY_Change"] = -1.0
        else:
            dxy_close = dxy_df["Close"].reindex(df.index, method="ffill")
            df["DXY_Change"] = dxy_close.pct_change(self.config.dxy_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_2d_floor = df["Return_2d"] <= self.config.drop_2d_floor
        cond_3d_cap = df["Return_3d"] >= self.config.drop_3d_cap
        cond_dxy = df["DXY_Change"] <= self.config.max_dxy_change

        df["Signal"] = (
            cond_pullback
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_2d_floor
            & cond_3d_cap
            & cond_dxy
        ).fillna(False)

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
            logger.info("INDA-012: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "INDA-012: Detected %d DXY-direction-gated capitulation signals",
            signal_count,
        )
        return df
