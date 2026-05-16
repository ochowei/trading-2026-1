"""GLD–USD Cross-Asset Divergence Regime-Gated MR 訊號偵測器 (GLD-016)

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 收盤價低於 20 日高點 ≥ 3%（沿用 GLD-015 Att2）
2. Williams %R(10) ≤ -80（沿用 GLD-015 Att2）
3. 收盤位置 ≥ 40%（日內反轉，沿用 GLD-015 Att2）
4. 1 日累計報酬 <= -0.3%（沿用 GLD-015 Att2）
5. 2 日累計報酬 <= -0.5%（沿用 GLD-015 Att2）
6. ^GVZ 10 日變化 <= +0.40（沿用 GLD-015 Att2 全域最優 forward-looking 維度）
7. GLD–USD cross-asset divergence regime gate（GLD-016 核心新增）：
   - CEILING: UUP N 日報酬 <= max_usd_return（filter 強美元 rally regime）
   - DIVERGENCE: GLD N 日報酬 − UUP N 日報酬 >= min_relative_return
8. 冷卻期 7 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.gld_016_usd_regime_mr.config import GLD016Config

logger = logging.getLogger(__name__)


class GLD016SignalDetector(BaseSignalDetector):
    """GLD-016：GLD-015 Att2 框架 + GLD–USD 跨資產 divergence regime gate"""

    def __init__(self, config: GLD016Config):
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

        # 回檔幅度（20日回看）
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # 1 日 / 2 日累計報酬（沿用 GLD-015 Att2）
        df["Return_1d"] = df["Close"].pct_change(1)
        df["Return_2d"] = df["Close"].pct_change(2)

        start_date = df.index[0].strftime("%Y-%m-%d")

        # ^GVZ forward-looking implied vol regime gate（沿用 GLD-015 Att2 全域最優）
        gvz_df = self._fetch_external(self.config.gvz_ticker, start_date)
        if gvz_df is None or gvz_df.empty:
            logger.error("無法取得 %s 數據，^GVZ 過濾停用", self.config.gvz_ticker)
            df["GVZ_Close"] = float("nan")
            df["GVZ_Change_Nd"] = 0.0
        else:
            gvz_close = gvz_df["Close"].reindex(df.index, method="ffill")
            df["GVZ_Close"] = gvz_close
            df["GVZ_Change_Nd"] = gvz_close.diff(self.config.gvz_direction_lookback)

        # GLD–USD cross-asset divergence regime gate（GLD-016 核心新增）
        usd_df = self._fetch_external(self.config.usd_ticker, start_date)
        div_n = self.config.usd_lookback
        df["GLD_Ret_N"] = df["Close"].pct_change(div_n)
        if usd_df is None or usd_df.empty:
            logger.error("無法取得 %s 數據，GLD–USD divergence 過濾停用", self.config.usd_ticker)
            df["USD_Ret_N"] = 0.0
            df["Rel_Return_N"] = 0.0
        else:
            usd_close = usd_df["Close"].reindex(df.index, method="ffill")
            df["USD_Ret_N"] = usd_close.pct_change(div_n)
            df["Rel_Return_N"] = df["GLD_Ret_N"] - df["USD_Ret_N"]

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_oneday_floor = df["Return_1d"] <= self.config.oneday_return_floor
        cond_twoday_floor = df["Return_2d"] <= self.config.twoday_return_floor

        if self.config.use_gvz_level_filter:
            cond_gvz_level = df["GVZ_Close"] <= self.config.max_gvz_level
        else:
            cond_gvz_level = pd.Series(True, index=df.index)

        if self.config.use_gvz_direction_filter:
            cond_gvz_dir = df["GVZ_Change_Nd"] <= self.config.max_gvz_direction_change
        else:
            cond_gvz_dir = pd.Series(True, index=df.index)

        if self.config.use_usd_ceiling:
            cond_usd_ceiling = df["USD_Ret_N"] <= self.config.max_usd_return
        else:
            cond_usd_ceiling = pd.Series(True, index=df.index)

        if self.config.use_usd_divergence:
            cond_usd_div = df["Rel_Return_N"] >= self.config.min_relative_return
        else:
            cond_usd_div = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback
            & cond_wr
            & cond_reversal
            & cond_oneday_floor
            & cond_twoday_floor
            & cond_gvz_level
            & cond_gvz_dir
            & cond_usd_ceiling
            & cond_usd_div
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
            logger.info("GLD-016: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("GLD-016: Detected %d USD-regime-gated MR signals", signal_count)
        return df
