"""
EEM-016 訊號偵測器：Global-Equity Macro-Context Confirmation Gate on Vol-Transition MR

在 EEM-014 Att2 的六條件 MR 進場邏輯之上，新增第七條件：
**SPY（developed-market 寬基）N 日絕對報酬 <= macro_return_threshold**

當 SPY 過去 N 日亦處於 drawdown（同步 broad risk-off），EEM 的 BB 下軌觸碰
更可能為「全球同步 capitulation」，MR V-bounce 可信；當 SPY 並未同步回檔，
EEM 訊號更可能為「中國孤立性政策/貿易衝擊持續走弱起點」，過濾此類訊號可
切除 EEM-014 Att2 之中國孤立性殘餘 SL（2021-07-08 DiDi、2025-11-19 美中
貿易摩擦）。

進場條件（全部滿足）：
1. Close <= BB(20, 2.0) 下軌
2. 10 日高點回檔 >= -7%（EM 結構性崩盤隔離）
3. Williams %R(10) <= -85
4. ClosePos >= 40%
5. ATR(5)/ATR(20) > 1.10（signal-day panic）
6. 2 日收盤報酬 <= -0.5%（2DD floor，EEM-014 Att2）
7. **SPY N 日報酬 <= macro_return_threshold（EEM-016 核心新增）**
8. 冷卻期 10 個交易日
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.eem_016_global_macro_context_mr.config import EEM016Config

logger = logging.getLogger(__name__)


class EEM016SignalDetector(BaseSignalDetector):
    """Global-Equity Macro-Context Confirmation Gate on Vol-Transition MR 訊號偵測器"""

    def __init__(self, config: EEM016Config):
        self.config = config

    def _fetch_macro_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.macro_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.macro_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands（沿用 EEM-014）
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # 10 日高點回檔（沿用 EEM-014，崩盤隔離）
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R（沿用 EEM-014）
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # 收盤位置（沿用 EEM-014）
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / day_range).where(day_range > 0, 0.5)

        # ATR ratio（沿用 EEM-014，signal-day panic）
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

        # 2 日收盤報酬（沿用 EEM-014，2DD floor）
        df["TwoDayReturn"] = df["Close"] / df["Close"].shift(2) - 1

        # === EEM-016 核心新增：SPY 寬基 N 日絕對報酬 ===
        start_date = df.index[0].strftime("%Y-%m-%d")
        macro_df = self._fetch_macro_data(start_date)
        if macro_df is None or macro_df.empty:
            logger.error(
                "無法取得 %s 數據，macro-context gate 停用",
                self.config.macro_ticker,
            )
            df["Macro_Return"] = -1.0
        else:
            macro_close = macro_df["Close"].reindex(df.index, method="ffill")
            df["Macro_Return"] = macro_close.pct_change(self.config.macro_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_twoday_floor = df["TwoDayReturn"] <= self.config.twoday_return_floor

        # 基礎 6 條件（EEM-014 Att2）— 用於 trade-level 診斷
        cond_base = cond_bb & cond_cap & cond_wr & cond_reversal & cond_vol & cond_twoday_floor

        # 診斷：列出所有 base 訊號日的 SPY N 日報酬分布（供 threshold 選擇）
        base_dates = df.index[cond_base]
        for d in base_dates:
            logger.info(
                "EEM-016 base-signal %s | Macro_Return(%dd)=%.4f",
                d.strftime("%Y-%m-%d"),
                self.config.macro_lookback,
                df.loc[d, "Macro_Return"],
            )

        # 第七條件：SPY N 日報酬 <= macro_return_threshold
        cond_macro = df["Macro_Return"] <= self.config.macro_return_threshold

        df["Signal"] = cond_base & cond_macro

        # Cooldown（沿用 EEM-014）
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
            logger.info("EEM-016: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "EEM-016: Detected %d signals (macro_lookback=%d, macro_return_threshold=%.4f)",
            signal_count,
            self.config.macro_lookback,
            self.config.macro_return_threshold,
        )
        return df
