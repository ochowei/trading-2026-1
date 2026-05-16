"""
DIA-015 訊號偵測器：^VIX Forward-Looking Implied-Vol DIRECTION Regime-Gated MR

在 DIA-012 Att2 五條件 MR 進場邏輯之上，新增第六條件：

  ^VIX(t) - ^VIX(t-N) <= max_vix_change（CEILING，N 日點變化）

當 signal day 的 ^VIX 過去 N 日上升過快（rising vol regime / 加速恐慌），
理論上反映 regime-shift 延續而非乾淨 V-bounce。本實驗測試 lesson #24
forward-looking implied vol DIRECTION 維度是否能 surgical 移除 DIA-012
殘餘 Part A SL 2022-01-18（pre-analysis 預期結構性失敗）。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.dia_015_vix_direction_mr.config import DIA015Config

logger = logging.getLogger(__name__)


class DIA015SignalDetector(BaseSignalDetector):
    """^VIX DIRECTION Regime-Gated MR 訊號偵測器"""

    def __init__(self, config: DIA015Config):
        self.config = config

    def _fetch_vix_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.vix_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.vix_ticker)
            return None

    @staticmethod
    def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
        """Wilder's RSI"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # RSI(2)（沿用 DIA-012）
        df["RSI"] = self._compute_rsi(df["Close"], self.config.rsi_period)

        # 2 日累計跌幅（沿用 DIA-012）
        n = self.config.decline_lookback
        df["Decline_2d"] = (df["Close"] - df["Close"].shift(n)) / df["Close"].shift(n)

        # 1 日 / 3 日報酬（沿用 DIA-012）
        df["Return_1d"] = df["Close"].pct_change(1)
        df["Return_3d"] = df["Close"].pct_change(3)

        # 收盤位置（沿用 DIA-012）
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # === DIA-015 核心新增：^VIX N 日點變化（DIRECTION）===
        start_date = df.index[0].strftime("%Y-%m-%d")
        vix_df = self._fetch_vix_data(start_date)

        if vix_df is None or vix_df.empty:
            logger.error(
                "無法取得 %s 數據，VIX DIRECTION filter 停用（fail-safe：不過濾）",
                self.config.vix_ticker,
            )
            df["VIX_Change_N"] = -999.0
        else:
            vix_close = vix_df["Close"].reindex(df.index, method="ffill")
            df["VIX_Change_N"] = vix_close - vix_close.shift(self.config.vix_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_rsi = df["RSI"] < self.config.rsi_threshold
        cond_decline = df["Decline_2d"] <= self.config.decline_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_oneday_cap = df["Return_1d"] >= self.config.oneday_return_cap
        cond_threeday_cap = df["Return_3d"] >= self.config.threeday_return_cap

        # 第六條件：^VIX N 日點變化 <= max_vix_change（CEILING）
        cond_vix = df["VIX_Change_N"] <= self.config.max_vix_change

        df["Signal"] = (
            cond_rsi & cond_decline & cond_reversal & cond_oneday_cap & cond_threeday_cap & cond_vix
        )

        # Cooldown（沿用 DIA-012）
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
            logger.info("DIA-015: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "DIA-015: Detected %d signals (vix_lookback=%d, max_vix_change=%+.2f)",
            signal_count,
            self.config.vix_lookback,
            self.config.max_vix_change,
        )
        return df
