"""
VGK-009 訊號偵測器：EURUSD Direction Filter on Vol-Transition MR

在 VGK-008 Att2 框架（BB(20, 2.0) 下軌+回檔上限+WR+ClosePos+ATR+2DD floor）
之上，新增「EUR/USD 方向過濾」作為 repo 第 2 次 bilateral FX direction
filter（繼 EWJ-006 USDJPY 後）。

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. Close <= BB(20, 2.0) 下軌
2. 10 日高點回檔 >= -7%（崩盤隔離）
3. Williams %R(10) <= -80
4. ClosePos >= 40%
5. ATR(5)/ATR(20) > 1.15
6. 2 日收盤報酬 <= -2.0%（VGK-008 Att2 2DD floor）
7. **EUR/USD N 日報酬 >= min_change**（VGK-009 核心新增 EUR 方向過濾）
8. 冷卻期 7 個交易日

EUR/USD 過濾的設計依據：
- VGK = Vanguard FTSE Europe ETF（USD-denominated）
- 持有 EUR/GBP/CHF 計價歐股（EUR 為主要驅動因子）
- 當 EUR/USD 急貶（EUR 弱化）時：
  - currency drag > 出口受益
  - ECB 政策衝擊/能源危機/歐債危機/俄烏戰爭事件伴隨 EUR 急貶
- 過濾「EUR 急貶」訊號 = 移除「currency drag + 歐洲特定衝擊」失敗模式

跨資產貢獻：
- Repo 第 2 次「bilateral FX direction filter」（繼 EWJ-006 USDJPY 後）
- Lesson #24 family v8 bilateral FX 變體首次跨資產移植：亞洲已開發 ETF →
  歐洲已開發 ETF
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.vgk_009_eurusd_direction_mr.config import VGK009Config

logger = logging.getLogger(__name__)


class VGK009EURUSDDirectionDetector(BaseSignalDetector):
    """VGK-009 EURUSD Direction-Gated Vol-Transition MR"""

    def __init__(self, config: VGK009Config):
        self.config = config

    def _fetch_eurusd_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.eurusd_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.eurusd_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
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

        df["TwoDayReturn"] = df["Close"] / df["Close"].shift(2) - 1

        # EUR/USD direction filter
        start_date = df.index[0].strftime("%Y-%m-%d")
        eurusd_df = self._fetch_eurusd_data(start_date)

        if eurusd_df is None or eurusd_df.empty:
            logger.error("無法取得 %s 數據，EURUSD 過濾停用", self.config.eurusd_ticker)
            df["EURUSD_Change"] = 0.0
        else:
            eurusd_close = eurusd_df["Close"].reindex(df.index, method="ffill")
            df["EURUSD_Change"] = eurusd_close.pct_change(self.config.eurusd_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_twoday_floor = df["TwoDayReturn"] <= self.config.twoday_return_floor
        cond_eurusd = df["EURUSD_Change"] >= self.config.min_eurusd_change

        df["Signal"] = (
            cond_bb
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_twoday_floor
            & cond_eurusd
        )

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
            logger.info("VGK-009: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "VGK-009: Detected %d signals (eurusd_lookback=%dd, min_change=%.4f)",
            signal_count,
            self.config.eurusd_lookback,
            self.config.min_eurusd_change,
        )
        return df
