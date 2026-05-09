"""
EEM-020 訊號偵測器：Multi-Anchor (^VIX CAP + EEM-FXI CEILING) Combined Filter on Vol-Transition MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. Close <= BB(20, 2.0) 下軌（同 EEM-014）
2. 10 日高點回檔 >= -7%（崩盤隔離，同 EEM-014）
3. Williams %R(10) <= -85（同 EEM-014）
4. ClosePos >= 40%（同 EEM-014）
5. ATR(5)/ATR(20) > 1.10（signal-day panic，同 EEM-014）
6. 2 日收盤報酬 <= -0.5%（2DD floor，同 EEM-014 Att2 甜蜜點）
7. **^VIX 收盤 <= vix_max_level**（EEM-020 第一維度：implied vol LEVEL CAP）
8. **EEM N 日報酬 - FXI N 日報酬 <= max_rel_return**（EEM-020 第二維度：
   broad-EM-vs-China sub-component CEILING）
9. 冷卻期 10 個交易日

異質維度組合設計依據：
- Part A 殘餘 SL 2021-07-08 DiDi（FXI 重挫深於 EEM）→ EEM-FXI CEILING binding
- Part B 殘餘 SL 2025-11-19 美中貿易（VIX 23.66 高 panic）→ ^VIX CAP binding
- 兩 SLs 在不同維度單向對齊，AND chain 異質維度可分工解決
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.eem_020_multi_anchor_combo_mr.config import EEM020Config

logger = logging.getLogger(__name__)


class EEM020MultiAnchorComboDetector(BaseSignalDetector):
    """EEM-020 Multi-Anchor (^VIX CAP + EEM-FXI CEILING) Combo Detector"""

    def __init__(self, config: EEM020Config):
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

        # ATR ratio
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

        # 外部資料
        start_date = df.index[0].strftime("%Y-%m-%d")

        # ^VIX LEVEL
        vix_df = self._fetch_external(self.config.vix_ticker, start_date)
        if vix_df is None or vix_df.empty:
            logger.error("無法取得 %s 數據，VIX CAP 過濾停用", self.config.vix_ticker)
            df["VIX_Close"] = float("nan")
        else:
            df["VIX_Close"] = vix_df["Close"].reindex(df.index, method="ffill")

        # FXI cross-asset divergence
        fxi_df = self._fetch_external(self.config.fxi_ticker, start_date)
        eem_n_return = df["Close"].pct_change(self.config.rel_lookback)
        if fxi_df is None or fxi_df.empty:
            logger.error(
                "無法取得 %s 數據，EEM-FXI CEILING 過濾停用",
                self.config.fxi_ticker,
            )
            df["RelDiff"] = 0.0
        else:
            fxi_close = fxi_df["Close"].reindex(df.index, method="ffill")
            fxi_n_return = fxi_close.pct_change(self.config.rel_lookback)
            df["RelDiff"] = eem_n_return - fxi_n_return

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_bb = df["Close"] <= df["BB_lower"]
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol = df["ATR_Ratio"] > self.config.atr_ratio_threshold
        cond_twoday_floor = df["TwoDayReturn"] <= self.config.twoday_return_floor
        cond_vix_cap = df["VIX_Close"] <= self.config.vix_max_level
        cond_rel_ceiling = df["RelDiff"] <= self.config.max_rel_return

        signal = (
            cond_bb
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol
            & cond_twoday_floor
            & cond_vix_cap
            & cond_rel_ceiling
        )
        df["Signal"] = signal.fillna(False)

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
            logger.info("EEM-020: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "EEM-020: Detected %d signals (vix_max=%.1f, fxi_max_rel=%+.3f)",
            signal_count,
            self.config.vix_max_level,
            self.config.max_rel_return,
        )
        return df
