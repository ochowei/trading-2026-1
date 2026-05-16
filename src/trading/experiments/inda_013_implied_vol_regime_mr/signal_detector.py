"""
INDA-013 訊號偵測器：Forward-Looking Implied-Vol Regime Gate on
Multi-Period Capitulation MR

延伸 INDA-011 Att3 框架，疊加「forward-looking implied-vol regime gate」
（lesson #24 family，repo 首次應用於單一國家 EM 股票 ETF）。

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10 日高點回檔 in [-7%, -3%]
2. Williams %R(10) <= -80
3. 收盤位置 >= 40%
4. ATR(5) / ATR(20) > 1.15
5. 2 日報酬 <= -2.0%（沿用 INDA-010 Att3）
6. 3 日報酬 >= -3.0%（沿用 INDA-011 Att3）
7. **隱含波動率 regime gate（INDA-013 核心新增）**：
     ceiling   → IV N 日變動 <= iv_threshold（過濾隱含波動率跳升）
     floor     → IV N 日變動 >= iv_threshold（過濾隱含波動率驟降）
     level_cap → IV 當日 level <= iv_threshold
8. 冷卻期 7 個交易日

^MOVE / ^VIX 資料於 compute_indicators 內以 yfinance 直接抓取並對齊
INDA 交易日（沿用 INDA-012 / COPX-016 模式，不需覆寫 strategy.run()）。
變動以「絕對點數差」計（沿用 XLU-013 / TLT-013 ^MOVE 慣例）。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.inda_013_implied_vol_regime_mr.config import INDA013Config

logger = logging.getLogger(__name__)


class INDA013SignalDetector(BaseSignalDetector):
    """INDA-013 Implied-Vol Regime-Gated Multi-Period Capitulation MR"""

    def __init__(self, config: INDA013Config):
        self.config = config

    def _fetch_iv_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.iv_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.iv_ticker)
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

        # forward-looking implied-vol regime gate（INDA-013 核心新增）
        start_date = df.index[0].strftime("%Y-%m-%d")
        iv_df = self._fetch_iv_data(start_date)

        if iv_df is None or iv_df.empty:
            logger.error("無法取得 %s 數據，IV regime gate 停用", self.config.iv_ticker)
            df["IV_Pass"] = True
            return df

        iv_close = iv_df["Close"].reindex(df.index, method="ffill")
        mode = self.config.iv_mode
        thr = self.config.iv_threshold

        if mode == "level_cap":
            iv_pass = iv_close <= thr
        else:
            iv_change = iv_close - iv_close.shift(self.config.iv_lookback)
            if mode == "floor":
                iv_pass = iv_change >= thr
            else:  # "ceiling"（預設）
                iv_pass = iv_change <= thr

        # IV 資料缺漏（理論上 2012+ 皆有）→ 放行，不破壞 baseline 訊號
        df["IV_Pass"] = iv_pass.fillna(True)

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
        cond_iv = df["IV_Pass"]

        df["Signal"] = (
            cond_pullback
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_2d_floor
            & cond_3d_cap
            & cond_iv
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
            logger.info("INDA-013: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "INDA-013: Detected %d implied-vol-regime-gated capitulation signals",
            signal_count,
        )
        return df
