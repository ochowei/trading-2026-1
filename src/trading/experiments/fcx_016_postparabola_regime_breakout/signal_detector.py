"""
FCX-016 訊號偵測器：Post-Parabolic Long-Horizon Regime-Gated VIX-FLOOR
                    BB Squeeze Breakout

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（同 FCX-015 Att2）
2. 收盤價 > Upper BB(20, 2.0)（同 FCX-015 Att2）
3. 收盤價 > SMA(50)（同 FCX-015 Att2）
4. SMA(20) >= 1.00 * SMA(60)（lesson #22 trend regime，同 FCX-015 Att2）
5. 訊號日 3 日累計報酬 <= max_signal_day_3d_return（lesson #19 ceiling，
   同 FCX-015 Att2）
6. ^VIX 收盤值 > vix_low_threshold（FCX-015 Att2 ★ VIX FLOOR，lesson #24）
7. **訊號日 prior runup_lookback 日 cumulative return <= runup_ceiling**
   （FCX-016 核心新增：post-parabolic 長窗 prior-return CEILING，跨資產
   移植 URA-014 Att1 lesson #19 family v3；排除「於新鮮拋物線 blow-off
   解除過程中買進突破」。NOT 趨勢方向過濾。）
8. 冷卻 cooldown_days 個交易日

predict→confirm 預測：FCX 之唯一殘餘 binding Part A SL 2021-11-11 之
prior-60d return +20.97% 與 9 個 winners（+3.4%~+62.6%）完全 interleaved，
且方向 INVERTED（URA-014 之 SL 為全場 Ret60 最高，FCX 之 SL 反偏低）→
documented-failure（記錄 lesson #19 family v3 不可移植 copper-supercycle
commodity miner 之新跨資產規則）。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fcx_016_postparabola_regime_breakout.config import FCX016Config

logger = logging.getLogger(__name__)


class FCX016PostparabolaRegimeBreakoutDetector(BaseSignalDetector):
    """FCX-016 訊號偵測器"""

    def __init__(self, config: FCX016Config):
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

        # === Bollinger Bands（同 FCX-015 Att2）===
        bb_period = self.config.bb_period
        bb_std = self.config.bb_std
        df["BB_Mid"] = df["Close"].rolling(bb_period).mean()
        rolling_std = df["Close"].rolling(bb_period).std()
        df["BB_Upper"] = df["BB_Mid"] + bb_std * rolling_std
        df["BB_Lower"] = df["BB_Mid"] - bb_std * rolling_std
        df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"]

        pct_window = self.config.bb_squeeze_percentile_window
        df["BB_Width_Pct"] = (
            df["BB_Width"]
            .rolling(pct_window)
            .apply(
                lambda x: x.iloc[-1] <= x.quantile(self.config.bb_squeeze_percentile),
                raw=False,
            )
        )

        recent = self.config.bb_squeeze_recent_days
        df["Recent_Squeeze"] = df["BB_Width_Pct"].rolling(recent, min_periods=1).max() >= 1.0

        # === SMA 趨勢確認（同 FCX-015 Att2）===
        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        # === 多週期趨勢 regime（同 FCX-015 Att2，lesson #22）===
        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # === 訊號日 3 日累計報酬（同 FCX-015 Att2，lesson #19）===
        df["Ret_3d"] = df["Close"].pct_change(3)

        # === Post-parabolic 長窗 prior-return（FCX-016 核心新增，
        #     跨資產移植 URA-014 lesson #19 family v3）===
        df["RunupReturn"] = df["Close"].pct_change(self.config.runup_lookback)

        # === ^VIX FLOOR gate（同 FCX-015 Att2 ★，lesson #24 family）===
        start_date = df.index[0].strftime("%Y-%m-%d")
        vix_df = self._fetch_external(self.config.vix_ticker, start_date)
        if vix_df is None or vix_df.empty:
            logger.error("無法取得 %s 數據，VIX FLOOR 過濾停用", self.config.vix_ticker)
            df["VIX_Close"] = float("nan")
        else:
            df["VIX_Close"] = vix_df["Close"].reindex(df.index, method="ffill")

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_squeeze = df["Recent_Squeeze"]
        cond_breakout = df["Close"] > df["BB_Upper"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_regime_trend = df["SMA_Regime_Short"] >= (
            df["SMA_Regime_Long"] * self.config.sma_regime_ratio_min
        )

        if self.config.max_signal_day_3d_return is not None:
            cond_3d_ceiling = df["Ret_3d"] <= self.config.max_signal_day_3d_return
        else:
            cond_3d_ceiling = pd.Series(True, index=df.index)

        # ^VIX FLOOR（同 FCX-015 Att2 ★）
        cond_vix_floor = df["VIX_Close"] > self.config.vix_low_threshold

        # Post-parabolic 長窗 prior-return CEILING（FCX-016 核心新增）
        cond_runup_ceiling = df["RunupReturn"] <= self.config.runup_ceiling

        signal = (
            cond_squeeze
            & cond_breakout
            & cond_trend
            & cond_regime_trend
            & cond_3d_ceiling
            & cond_vix_floor
            & cond_runup_ceiling
        )

        df["Signal"] = signal.fillna(False)

        # 冷卻期
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
                "FCX-016: %d duplicate signals suppressed by cooldown",
                len(suppressed),
            )

        signal_count = df["Signal"].sum()
        logger.info(
            "FCX-016: Detected %d post-parabolic-regime-gated breakout signals",
            signal_count,
        )
        return df
