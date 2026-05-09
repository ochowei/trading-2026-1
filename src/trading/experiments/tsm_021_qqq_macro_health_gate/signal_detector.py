"""
TSM-021 訊號偵測器：QQQ Macro-Health Gate on RS Momentum Pullback

進場條件（全部滿足，執行模型於 T+1 開盤進場）：
1. TSM 20 日報酬 - SMH 20 日報酬 >= relative_strength_min
2. 5 日高點回檔在 [pullback_min, pullback_max]
3. Close > SMA(sma_trend_period)
4. 訊號日 5 日報酬 <= ret_5d_max
5. 訊號日 1 日報酬 <= ret_1d_max（停用，999 視為非綁定）
6. **QQQ macro_lookback 日報酬 >= macro_min_return**（FLOOR：broad-market 健康確認）
7. **QQQ macro_lookback 日報酬 <= macro_max_return**（CEILING：broad-market 過熱排除，
   999 視為停用）
8. 冷卻 cooldown_days 個交易日

設計依據：lesson #25 cross-strategy mirror extension（IWM-015 broad-market
context confirmation gate 的 momentum-framework 鏡像版本）。IWM-015 為 MR
框架要求 broad-market 已 confirmed risk-off (CEILING)，本實驗為 momentum
pullback 框架要求 broad-market 未進入 deep correction (FLOOR)。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.tsm_021_qqq_macro_health_gate.config import TSM021Config

logger = logging.getLogger(__name__)


class TSM021QQQMacroHealthGateDetector(BaseSignalDetector):
    """TSM-021 訊號偵測器"""

    def __init__(self, config: TSM021Config):
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

        start_date = df.index[0].strftime("%Y-%m-%d")
        smh_df = self._fetch_external(self.config.reference_ticker, start_date)
        qqq_df = self._fetch_external(self.config.macro_ticker, start_date)

        if smh_df is None or smh_df.empty:
            logger.error("無法取得 SMH 數據，無法計算相對強度")
            df["Relative_Strength"] = 0.0
            df["Pullback_5d"] = 0.0
            df["SMA_Trend"] = df["Close"]
            df["Ret_1d"] = 0.0
            df["Ret_5d"] = 0.0
            df["QQQ_Macro_Return"] = 0.0
            return df

        common_idx = df.index.intersection(smh_df.index)
        if qqq_df is not None and not qqq_df.empty:
            common_idx = common_idx.intersection(qqq_df.index)
        df = df.loc[common_idx]

        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        period = self.config.relative_strength_period
        df["TSM_Return"] = df["Close"].pct_change(period)
        df["SMH_Return"] = smh_df.loc[common_idx, "Close"].pct_change(period)
        df["Relative_Strength"] = df["TSM_Return"] - df["SMH_Return"]

        lookback = self.config.pullback_lookback
        df["High_5d"] = df["High"].rolling(lookback).max()
        df["Pullback_5d"] = (df["High_5d"] - df["Close"]) / df["High_5d"]

        df["Ret_1d"] = df["Close"].pct_change(1)
        df["Ret_5d"] = df["Close"].pct_change(5)

        # === QQQ broad-market macro-health gate（TSM-021 核心新增）===
        if qqq_df is not None and not qqq_df.empty:
            qqq_close = qqq_df["Close"].reindex(df.index, method="ffill")
            df["QQQ_Close"] = qqq_close
            df["QQQ_Macro_Return"] = qqq_close.pct_change(self.config.macro_lookback)
        else:
            logger.error(
                "無法取得 %s 數據，macro-health gate 將失效（全部訊號通過）",
                self.config.macro_ticker,
            )
            df["QQQ_Close"] = float("nan")
            # NaN return 在後續 fillna(False) 會被視為不通過，反而過於嚴格；
            # 這裡使用 0.0 使得 FLOOR/CEILING 預設都通過（等同 filter 停用）
            df["QQQ_Macro_Return"] = 0.0

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rs = df["Relative_Strength"] >= self.config.relative_strength_min
        cond_pullback = (df["Pullback_5d"] >= self.config.pullback_min) & (
            df["Pullback_5d"] <= self.config.pullback_max
        )
        cond_trend = df["Close"] > df["SMA_Trend"]
        cond_1d = df["Ret_1d"] <= self.config.ret_1d_max
        cond_5d = df["Ret_5d"] <= self.config.ret_5d_max

        cond_macro_floor = df["QQQ_Macro_Return"] >= self.config.macro_min_return
        cond_macro_ceil = df["QQQ_Macro_Return"] <= self.config.macro_max_return

        df["Signal"] = (
            cond_rs
            & cond_pullback
            & cond_trend
            & cond_1d
            & cond_5d
            & cond_macro_floor
            & cond_macro_ceil
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

        signal_count = df["Signal"].sum()
        logger.info(
            "TSM-021: Detected %d macro-health-gated RS signals",
            signal_count,
        )
        return df
