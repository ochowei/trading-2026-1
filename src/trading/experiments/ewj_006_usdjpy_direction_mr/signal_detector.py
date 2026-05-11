"""
EWJ-006 訊號偵測器：USDJPY Direction Filter on Vol-Transition MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. Close <= BB(20, 1.5) 下軌（同 EWJ-005）
2. 10日高點回檔 >= -7%（崩盤隔離，同 EWJ-005）
3. Williams %R(10) <= -80（同 EWJ-005）
4. ClosePos >= 40%（同 EWJ-005）
5. ATR(5)/ATR(20) > 1.15（同 EWJ-005）
6. 1日報酬 <= -0.5%（capitulation strength，同 EWJ-005 Att2 甜蜜點）
7. **USDJPY N 日報酬 <= max_change**（EWJ-006 核心新增 JPY 方向過濾）
8. 冷卻期 7 個交易日

USDJPY 過濾的設計依據：
- EWJ = iShares MSCI Japan ETF（USD-denominated）
- 當 USDJPY 急升（JPY 急貶）時：
  - 出口股利好但 currency drag 通常超過出口受益
  - BoJ 政策衝擊類事件（2022-09-01 / 2023-08-03 yield surge）伴隨 USDJPY 急升
- 過濾 USDJPY 急升訊號 = 移除「currency drag + 政策衝擊」失敗模式

跨資產貢獻：
- Repo 首次「USDJPY (USD/JPY spot rate) direction filter」於任何資產
- Lesson #24 family 既有 v1-v6 皆 implied vol，v7 候選 COPX-016 DXY spot FX index
- 本實驗為 v8 候選：bilateral FX direction 於單一國家 ETF
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ewj_006_usdjpy_direction_mr.config import EWJ006Config

logger = logging.getLogger(__name__)


class EWJ006USDJPYDirectionDetector(BaseSignalDetector):
    """EWJ-006 USDJPY Direction-Gated Vol-Transition MR"""

    def __init__(self, config: EWJ006Config):
        self.config = config

    def _fetch_usdjpy_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.usdjpy_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.usdjpy_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # 10日高點回檔
        pb_n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(pb_n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        hl_range = highest - lowest
        df["WR"] = (highest - df["Close"]) / hl_range.where(hl_range > 0, float("nan")) * -100
        df["WR"] = df["WR"].fillna(-50.0)

        # Close Position
        daily_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / daily_range).where(daily_range > 0, 0.5)

        # ATR ratio
        tr = pd.concat(
            [
                df["High"] - df["Low"],
                (df["High"] - df["Close"].shift(1)).abs(),
                (df["Low"] - df["Close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["ATR_fast"] = tr.rolling(self.config.atr_fast).mean()
        df["ATR_slow"] = tr.rolling(self.config.atr_slow).mean()
        df["ATR_ratio"] = df["ATR_fast"] / df["ATR_slow"].where(df["ATR_slow"] > 0, float("nan"))

        # Capitulation strength（單日報酬）
        df["Ret_1d"] = df["Close"].pct_change(1)
        df["Ret_2d"] = df["Close"].pct_change(2)

        # USDJPY direction filter
        start_date = df.index[0].strftime("%Y-%m-%d")
        usdjpy_df = self._fetch_usdjpy_data(start_date)

        if usdjpy_df is None or usdjpy_df.empty:
            logger.error("無法取得 %s 數據，USDJPY 過濾停用", self.config.usdjpy_ticker)
            df["USDJPY_Change"] = 0.0
        else:
            usdjpy_close = usdjpy_df["Close"].reindex(df.index, method="ffill")
            df["USDJPY_Change"] = usdjpy_close.pct_change(self.config.usdjpy_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_closepos = df["ClosePos"] >= self.config.close_pos_threshold
        cond_atr = df["ATR_ratio"] > self.config.atr_ratio_threshold

        if self.config.capitulation_mode == "2dd_floor":
            cond_cap_strength = df["Ret_2d"] <= self.config.capitulation_threshold
        elif self.config.capitulation_mode == "1d_floor":
            cond_cap_strength = df["Ret_1d"] <= self.config.capitulation_threshold
        else:
            raise ValueError(f"Unsupported capitulation_mode: {self.config.capitulation_mode}")

        cond_usdjpy = df["USDJPY_Change"] <= self.config.max_usdjpy_change

        df["Signal"] = (
            cond_bb
            & cond_cap
            & cond_wr
            & cond_closepos
            & cond_atr
            & cond_cap_strength
            & cond_usdjpy
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
            logger.info("EWJ-006: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "EWJ-006: Detected %d signals (usdjpy_lookback=%dd, max_change=%.4f)",
            signal_count,
            self.config.usdjpy_lookback,
            self.config.max_usdjpy_change,
        )
        return df
