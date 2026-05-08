"""
COPX-016 訊號偵測器：DXY Direction Filter on Regime-Aware BB Squeeze Breakout

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（近期波動收縮，同 COPX-011）
2. 收盤價 > Upper BB(20, 2.0)（突破上軌，同 COPX-011）
3. 收盤價 > SMA(50)（短期趨勢向上，同 COPX-011）
4. regime BOX：1.00 ≤ SMA(20) / SMA(60) ≤ 1.09（同 COPX-011 Att3）
5. **DXY 5 日報酬 ≤ +0.5%**（COPX-016 核心新增 USD 強度方向過濾）
6. 冷卻期 12 個交易日

DXY 過濾的設計依據：
- COPX = 銅礦業 ETF，銅價以 USD 計價 → 強 USD 結構性壓抑銅價
- 強 USD = EM 資金外流預期 → 商品需求預期下降
- 短期 DXY 急升（5d > +0.5%）= 宏觀逆風，即使技術面 regime BOX 通過，
  突破延續性結構受抑

跨資產貢獻：
- Repo 首次「DXY (US Dollar Index) direction filter」於任何資產
- 既有 lesson #24 family（VIX / MOVE / GVZ / OVX 皆 implied vol forward-looking）
  + lesson #25（QQQ/SPY broad-market context confirmation）
  皆未涉及 spot FX index 維度
- DXY 為 spot 外匯（不是 implied vol），代表 USD 對 6 主要貨幣的相對強度
- 對「商品 / 礦業 / EM」類資產為直接結構性 driver
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.copx_016_dxy_direction_breakout.config import COPX016Config

logger = logging.getLogger(__name__)


class COPX016DXYDirectionDetector(BaseSignalDetector):
    """COPX-016 DXY Direction-Gated Regime-Aware BB Squeeze Breakout"""

    def __init__(self, config: COPX016Config):
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

        df["SMA_Trend"] = df["Close"].rolling(self.config.sma_trend_period).mean()

        df["SMA_Regime_Short"] = df["Close"].rolling(self.config.sma_regime_short).mean()
        df["SMA_Regime_Long"] = df["Close"].rolling(self.config.sma_regime_long).mean()

        # DXY direction filter（COPX-016 核心新增）
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

        cond_squeeze = df["Recent_Squeeze"]
        cond_breakout = df["Close"] > df["BB_Upper"]
        cond_trend = df["Close"] > df["SMA_Trend"]
        regime_ratio = df["SMA_Regime_Short"] / df["SMA_Regime_Long"]
        cond_regime_floor = regime_ratio >= self.config.sma_regime_ratio_min
        cond_regime_cap = regime_ratio <= self.config.sma_regime_ratio_max
        cond_dxy = df["DXY_Change"] <= self.config.max_dxy_change

        df["Signal"] = (
            cond_squeeze
            & cond_breakout
            & cond_trend
            & cond_regime_floor
            & cond_regime_cap
            & cond_dxy
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

        signal_count = df["Signal"].sum()
        logger.info(
            "COPX-016: Detected %d DXY-direction-gated regime breakout signals",
            signal_count,
        )
        return df
