"""
EEM-016 訊號偵測器：DXY Direction Filter on Vol-Transition MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. Close <= BB(20, 2.0) 下軌（同 EEM-014）
2. 10 日高點回檔 >= -7%（崩盤隔離，同 EEM-014）
3. Williams %R(10) <= -85（同 EEM-014）
4. ClosePos >= 40%（同 EEM-014）
5. ATR(5)/ATR(20) > 1.10（signal-day panic，同 EEM-014）
6. 2 日收盤報酬 <= -0.5%（2DD floor，同 EEM-014 Att2 甜蜜點）
7. **DXY N 日報酬 <= max_change**（EEM-016 核心新增 USD 方向過濾）
8. 冷卻期 10 個交易日

DXY 過濾的設計依據：
- EEM = iShares MSCI Emerging Markets ETF（USD-denominated，broad EM）
- 當 DXY 急升（USD 強勢）時：
  - EM 資金外流、USD 債務壓力、商品價格疲弱、中美貿易壓力
  - EEM MR 訊號的反轉延續性結構性下降
- 過濾 DXY 急升訊號 = 移除「USD 強勢驅動 EM 結構性疲弱」失敗模式

跨資產貢獻：
- repo 第 2 次「DXY direction filter」應用於任何資產（首次為 COPX-016）
- repo 首次「DXY direction filter」應用於 broad EM ETF
- Lesson #24 family v9 候選：spot DXY direction 於 EM 寬基 ETF
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.eem_016_dxy_direction_mr.config import EEM016Config

logger = logging.getLogger(__name__)


class EEM016DXYDirectionDetector(BaseSignalDetector):
    """EEM-016 DXY Direction-Gated Vol-Transition MR"""

    def __init__(self, config: EEM016Config):
        self.config = config

    def _fetch_dxy_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.dxy_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.dxy_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # 10 日高點回檔（崩盤隔離）
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

        # 收盤位置
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = ((df["Close"] - df["Low"]) / day_range).where(day_range > 0, 0.5)

        # ATR ratio（signal-day panic）
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

        # 2 日收盤報酬（2DD floor）
        df["TwoDayReturn"] = df["Close"] / df["Close"].shift(2) - 1

        # DXY direction filter
        start_date = df.index[0].strftime("%Y-%m-%d")
        dxy_df = self._fetch_dxy_data(start_date)

        if dxy_df is None or dxy_df.empty:
            logger.error("無法取得 %s 數據，DXY 過濾停用", self.config.dxy_ticker)
            df["DXY_Change"] = 0.0
        else:
            dxy_close = dxy_df["Close"].reindex(df.index, method="ffill")
            df["DXY_Change"] = dxy_close.pct_change(self.config.dxy_lookback)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_twoday_floor = df["TwoDayReturn"] <= self.config.twoday_return_floor
        if self.config.filter_mode == "max":
            cond_dxy = df["DXY_Change"] <= self.config.max_dxy_change
        elif self.config.filter_mode == "min":
            cond_dxy = df["DXY_Change"] >= self.config.min_dxy_change
        else:
            raise ValueError(f"Unsupported filter_mode: {self.config.filter_mode}")

        df["Signal"] = (
            cond_bb & cond_cap & cond_wr & cond_reversal & cond_vol & cond_twoday_floor & cond_dxy
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
            logger.info("EEM-016: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        if self.config.filter_mode == "max":
            threshold = self.config.max_dxy_change
        else:
            threshold = self.config.min_dxy_change
        logger.info(
            "EEM-016: Detected %d signals (dxy_lookback=%dd, mode=%s, threshold=%.4f)",
            signal_count,
            self.config.dxy_lookback,
            self.config.filter_mode,
            threshold,
        )
        return df
