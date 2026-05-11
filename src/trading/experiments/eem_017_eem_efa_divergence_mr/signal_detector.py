"""
EEM-017 訊號偵測器：EEM-EFA Cross-Asset Divergence Filter on Vol-Transition MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. Close <= BB(20, 2.0) 下軌（同 EEM-014）
2. 10 日高點回檔 >= -7%（崩盤隔離，同 EEM-014）
3. Williams %R(10) <= -85（同 EEM-014）
4. ClosePos >= 40%（同 EEM-014）
5. ATR(5)/ATR(20) > 1.10（signal-day panic，同 EEM-014）
6. 2 日收盤報酬 <= -0.5%（2DD floor，同 EEM-014 Att2 甜蜜點）
7. **EEM N 日報酬 - EFA N 日報酬 >= min_rel_diff**（EEM-017 核心新增
   broad-EM-vs-broad-DM divergence floor）
8. 冷卻期 10 個交易日

EEM-EFA divergence filter 的設計依據：
- EEM = iShares MSCI Emerging Markets（broad EM USD-denominated）
- EFA = iShares MSCI EAFE（broad DM ex-US USD-denominated peer）
- divergence = EEM N 日報酬 - EFA N 日報酬：
  - 大幅負值（EEM << EFA）：EM-specific 結構性疲弱（中國政策、貿易摩擦、EM 貨幣危機）
    → MR 訊號失效率高，應過濾
  - 小幅負值或同步：broad market correction → MR 訊號的 broad capitulation 反彈延續性高

跨資產貢獻：
- repo 第 1 次「broad-EM-vs-broad-DM divergence floor」應用於任何資產
- lesson #20 v3 family v9 候選變體（既有 v6 BANDS / v7 DXY direction / v8 USDJPY direction）
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.eem_017_eem_efa_divergence_mr.config import EEM017Config

logger = logging.getLogger(__name__)


class EEM017DivergenceDetector(BaseSignalDetector):
    """EEM-017 EEM-EFA Divergence-Gated Vol-Transition MR"""

    def __init__(self, config: EEM017Config):
        self.config = config

    def _fetch_efa_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.efa_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.efa_ticker)
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

        # EEM N 日報酬
        eem_n_return = df["Close"].pct_change(self.config.rel_lookback)

        # EFA cross-asset divergence
        start_date = df.index[0].strftime("%Y-%m-%d")
        efa_df = self._fetch_efa_data(start_date)

        if efa_df is None or efa_df.empty:
            logger.error(
                "無法取得 %s 數據，EEM-EFA divergence 過濾停用",
                self.config.efa_ticker,
            )
            df["RelDiff"] = 0.0
        else:
            efa_close = efa_df["Close"].reindex(df.index, method="ffill")
            efa_n_return = efa_close.pct_change(self.config.rel_lookback)
            df["RelDiff"] = eem_n_return - efa_n_return

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_twoday_floor = df["TwoDayReturn"] <= self.config.twoday_return_floor
        if self.config.filter_mode == "min":
            cond_rel_diff = df["RelDiff"] >= self.config.min_rel_diff
        elif self.config.filter_mode == "max":
            cond_rel_diff = df["RelDiff"] <= self.config.max_rel_diff
        else:
            raise ValueError(f"Unsupported filter_mode: {self.config.filter_mode}")

        df["Signal"] = (
            cond_bb
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_twoday_floor
            & cond_rel_diff
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
            logger.info("EEM-017: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        threshold = (
            self.config.min_rel_diff
            if self.config.filter_mode == "min"
            else self.config.max_rel_diff
        )
        logger.info(
            "EEM-017: Detected %d signals (rel_lookback=%dd, mode=%s, threshold=%.4f)",
            signal_count,
            self.config.rel_lookback,
            self.config.filter_mode,
            threshold,
        )
        return df
