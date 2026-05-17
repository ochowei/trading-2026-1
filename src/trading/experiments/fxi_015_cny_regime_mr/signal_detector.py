"""FXI–CNY Currency-Regime-Gated MR 訊號偵測器 (FXI-015)

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 ≥ 5%（沿用 FXI-014 Att2 = FXI-005）
2. 10 日高點回檔 ≤ 12%（crash isolation，沿用 FXI-014 Att2）
3. Williams %R(10) ≤ -80（沿用 FXI-014 Att2）
4. 收盤位置 ≥ 40%（日內反轉，沿用 FXI-014 Att2）
5. ATR(5)/ATR(20) > 1.05（FLOOR，panic 確認，lesson #15）
6. ATR(5)/ATR(20) ≤ 1.35（CEILING，排除 in-crash acceleration，FXI-014 Att2）
7. FXI–CNY 貨幣 regime gate（FXI-015 核心新增）：
   - CEILING: CNY=X N 日報酬 ≤ max_cny_return（filter 弱人民幣 risk-off）
   - DIVERGENCE: FXI N 日報酬 − CNY=X N 日報酬 ≥ min_relative_return
8. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fxi_015_cny_regime_mr.config import FXI015Config

logger = logging.getLogger(__name__)


class FXI015SignalDetector(BaseSignalDetector):
    """FXI-015：FXI-014 Att2 框架 + FXI–CNY 貨幣 regime gate"""

    def __init__(self, config: FXI015Config):
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

        # 回檔幅度（10 日回看，沿用 FXI-014 Att2）
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100
        df.loc[(highest - lowest) == 0, "WR"] = -50.0

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # ATR 比率 BAND（沿用 FXI-014 Att2）
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
        df["ATR_Ratio"] = atr_short / atr_long

        # FXI–CNY 貨幣 regime gate（FXI-015 核心新增）
        start_date = df.index[0].strftime("%Y-%m-%d")
        div_n = self.config.cny_lookback
        df["FXI_Ret_N"] = df["Close"].pct_change(div_n)

        cny_df = self._fetch_external(self.config.cny_ticker, start_date)
        if cny_df is None or cny_df.empty:
            logger.error(
                "無法取得 %s 數據，FXI–CNY regime gate 停用",
                self.config.cny_ticker,
            )
            df["CNY_Ret_N"] = 0.0
            df["Rel_Return_N"] = 0.0
        else:
            cny_close = cny_df["Close"].reindex(df.index, method="ffill")
            df["CNY_Ret_N"] = cny_close.pct_change(div_n)
            df["Rel_Return_N"] = df["FXI_Ret_N"] - df["CNY_Ret_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol_floor = df["ATR_Ratio"] > self.config.atr_ratio_floor
        cond_vol_ceiling = df["ATR_Ratio"] <= self.config.atr_ratio_ceiling

        if self.config.use_cny_ceiling:
            cond_cny_ceiling = df["CNY_Ret_N"] <= self.config.max_cny_return
        else:
            cond_cny_ceiling = pd.Series(True, index=df.index)

        if self.config.use_cny_divergence:
            cond_cny_div = df["Rel_Return_N"] >= self.config.min_relative_return
        else:
            cond_cny_div = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol_floor
            & cond_vol_ceiling
            & cond_cny_ceiling
            & cond_cny_div
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
            logger.info("FXI-015: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("FXI-015: Detected %d CNY-regime-gated MR signals", signal_count)
        return df
