"""
XLU-014 訊號偵測器：^TNX Realized-Rate-Momentum DIRECTION Regime-Gated MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 in [-7%, -3.5%]（同 XLU-011 / XLU-012 / XLU-013）
2. Williams %R(10) <= -80（同上）
3. 收盤位置 >= 40%（同上）
4. ATR(5) / ATR(20) > 1.15（同上）
5. ^MOVE N 日變化 <= +5.0（沿用 XLU-013 Att2/Att3 全域最優，LEVEL cap 停用）
6. （XLU-014 核心新增，二擇一正交 gate）：
   - ^TNX N 日 % 變化 <= max_tnx_change（CEILING，rate 急升過濾），或
   - XLU 自身 N 日報酬 >= min_xlu_return（FLOOR，capitulation-depth，Att3）
7. 冷卻期 7 個交易日

predict→confirm documented-failure：殘餘 Part B binding =「3 筆相同 +3.00%
TP winners + 單筆 2024-01-18 −0.20% 近乎持平 time-expiry」zero-variance trap
（TLT-014 Att3 isomorph）。任何 gate 外科式移除該 expiry → Part B std=0
退化；非外科式 → 同殺相同-TP winner 崩潰。預測 4th zero-var-trap 確認。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.xlu_014_tnx_rate_direction_mr.config import XLU014Config

logger = logging.getLogger(__name__)


class XLU014SignalDetector(BaseSignalDetector):
    """XLU-014：XLU-013 Att2/Att3 框架 + ^TNX realized-rate-momentum DIRECTION gate"""

    def __init__(self, config: XLU014Config):
        self.config = config

    def _fetch_aux_close(self, ticker: str, start_date: str) -> pd.Series | None:
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
            return df["Close"]
        except Exception:
            logger.exception("Failed to fetch %s data", ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 回檔幅度
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
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
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

        # ATR ratio (sym to XLU-011/XLU-012/XLU-013)
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

        start_date = df.index[0].strftime("%Y-%m-%d")

        # ^MOVE forward-looking implied vol gate（沿用 XLU-013 Att2/Att3）
        move_close = self._fetch_aux_close(self.config.move_ticker, start_date)
        if move_close is None or move_close.empty:
            logger.error("無法取得 %s 數據，^MOVE 過濾停用", self.config.move_ticker)
            df["MOVE_Close"] = float("nan")
            df["MOVE_Change_Nd"] = 0.0
        else:
            move_close = move_close.reindex(df.index, method="ffill")
            df["MOVE_Close"] = move_close
            df["MOVE_Change_Nd"] = move_close.diff(self.config.move_direction_lookback)

        # ^TNX 10y yield realized-rate-momentum DIRECTION gate（XLU-014 核心新增）
        tnx_close = self._fetch_aux_close(self.config.tnx_ticker, start_date)
        if tnx_close is None or tnx_close.empty:
            logger.error("無法取得 %s 數據，^TNX 過濾停用", self.config.tnx_ticker)
            df["TNX_Change_Pct"] = 0.0
        else:
            tnx_close = tnx_close.reindex(df.index, method="ffill")
            # N 日 % 變化（× 100），與 predict→confirm 預分析一致
            df["TNX_Change_Pct"] = tnx_close.pct_change(self.config.tnx_direction_lookback) * 100.0

        # XLU 自身 N 日報酬（Att3 正交 capitulation-depth FLOOR 用）
        df["XLU_Return_Nd"] = df["Close"].pct_change(self.config.xlu_depth_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_move_level = df["MOVE_Close"] <= self.config.max_move_level

        if self.config.use_move_direction_filter:
            cond_move_dir = df["MOVE_Change_Nd"] <= self.config.max_move_change
        else:
            cond_move_dir = pd.Series(True, index=df.index)

        if self.config.use_tnx_direction_filter:
            cond_tnx = df["TNX_Change_Pct"] <= self.config.max_tnx_change
        else:
            cond_tnx = pd.Series(True, index=df.index)

        if self.config.use_xlu_depth_filter:
            cond_xlu_depth = df["XLU_Return_Nd"] >= self.config.min_xlu_return
        else:
            cond_xlu_depth = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_pullback
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_move_level
            & cond_move_dir
            & cond_tnx
            & cond_xlu_depth
        )

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
            logger.info("XLU-014: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("XLU-014: Detected %d TNX-rate-direction-gated MR signals", signal_count)
        return df
