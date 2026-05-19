"""
EWJ-007 ^VIX Forward-Looking Implied-Vol Regime-Gated MR 訊號偵測器

在 EWJ-005 Att2 框架（BB 下軌 + 回檔上限 + WR + ClosePos + ATR + 1d floor）
之上新增「^VIX N 日 DIRECTION filter」：要求訊號日的 ^VIX N 日累計變化
<= 閾值，過濾「global vol-acceleration regime」訊號（^VIX 急升 = 外資從
日股撤出 / 日圓套息平倉期，EWJ 自身 capitulation 結構不足以支撐 V-bounce）。

為支援閾值校準（lesson #24 規則 #3），detect_signals 會先以 base-6 條件
+ 冷卻計算出「EWJ-005 Att2 baseline 訊號集」並 log 每筆訊號的 ^VIX 收盤值
與 3/5/10 日變化（與 VIX gate 閾值無關），再套用 VIX gate 與冷卻得出
EWJ-007 最終訊號集。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ewj_007_vix_implied_vol_mr.config import EWJ007Config

logger = logging.getLogger(__name__)


class EWJ007SignalDetector(BaseSignalDetector):
    """
    EWJ ^VIX Forward-Looking Implied-Vol Regime-Gated MR 訊號偵測器

    七條件同時成立時觸發訊號：
    1. Close <= BB(20, 1.5) 下軌
    2. 10日高點回檔 >= -7%（崩盤隔離）
    3. Williams %R(10) <= -80
    4. ClosePos >= 40%
    5. ATR(5)/ATR(20) > 1.15
    6. Capitulation strength: 1日報酬 <= 閾值（沿用 EWJ-005 Att2）
    7. ^VIX N 日累計變化 <= max_vix_change（EWJ-007 核心：forward-looking
       implied vol DIRECTION gate）+ 可選 ^VIX Close <= max_vix_level
    """

    def __init__(self, config: EWJ007Config):
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

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Bollinger Bands
        n = self.config.bb_period
        df["BB_mid"] = df["Close"].rolling(n).mean()
        df["BB_std"] = df["Close"].rolling(n).std()
        df["BB_lower"] = df["BB_mid"] - self.config.bb_std * df["BB_std"]

        # 10日高點回檔（崩盤隔離）
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

        # Capitulation strength（單日 / 兩日 報酬）
        df["Ret_1d"] = df["Close"].pct_change(1)
        df["Ret_2d"] = df["Close"].pct_change(2)

        # ^VIX forward-looking implied vol gate（EWJ-007 核心新增）
        start_date = df.index[0].strftime("%Y-%m-%d")
        vix_df = self._fetch_vix_data(start_date)

        if vix_df is None or vix_df.empty:
            logger.error("無法取得 %s 數據，^VIX 過濾停用", self.config.vix_ticker)
            df["VIX_Close"] = float("nan")
            df["VIX_Change_Nd"] = 0.0
            df["VIX_Change_3d"] = 0.0
            df["VIX_Change_5d"] = 0.0
            df["VIX_Change_10d"] = 0.0
        else:
            vix_close = vix_df["Close"].reindex(df.index, method="ffill")
            df["VIX_Close"] = vix_close
            df["VIX_Change_Nd"] = vix_close.diff(self.config.vix_direction_lookback)
            # 校準輔助欄位（lesson #24 規則 #3）：固定 3/5/10d 變化
            df["VIX_Change_3d"] = vix_close.diff(3)
            df["VIX_Change_5d"] = vix_close.diff(5)
            df["VIX_Change_10d"] = vix_close.diff(10)

        return df

    def _apply_cooldown(self, df: pd.DataFrame, col: str) -> list[pd.Timestamp]:
        """對 df[col] 為 True 的訊號套用冷卻，回傳被壓制的索引清單。"""
        signal_indices = df.index[df[col]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None
        for idx in signal_indices:
            if last_signal is not None:
                gap = len(df.loc[last_signal:idx]) - 1
                if gap <= self.config.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx
        return suppressed

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

        # base-6（EWJ-005 Att2 完整框架，不含 VIX gate）
        df["BaseSignal"] = (
            cond_bb & cond_cap & cond_wr & cond_closepos & cond_atr & cond_cap_strength
        )

        # ── 閾值校準輔助：以 base-6 + 冷卻得出 EWJ-005 Att2 baseline 訊號集，
        #    log 每筆 ^VIX 收盤與 3/5/10d 變化（與 VIX gate 閾值無關）──
        base_suppressed = self._apply_cooldown(df, "BaseSignal")
        baseline_idx = [i for i in df.index[df["BaseSignal"]] if i not in set(base_suppressed)]
        for idx in baseline_idx:
            row = df.loc[idx]
            logger.info(
                "EWJ-007 [VIX-calib] %s | VIX=%.2f | 3d=%+.2f | 5d=%+.2f | 10d=%+.2f",
                idx.strftime("%Y-%m-%d"),
                row["VIX_Close"],
                row["VIX_Change_3d"],
                row["VIX_Change_5d"],
                row["VIX_Change_10d"],
            )

        # ── EWJ-007 最終訊號：base-6 + ^VIX DIRECTION gate + 可選 LEVEL CAP ──
        cond_vix_dir = df["VIX_Change_Nd"] <= self.config.max_vix_change
        cond_vix_level = df["VIX_Close"] <= self.config.max_vix_level
        df["Signal"] = df["BaseSignal"] & cond_vix_dir & cond_vix_level

        suppressed = self._apply_cooldown(df, "Signal")
        if suppressed:
            df.loc[suppressed, "Signal"] = False
            logger.info("EWJ-007: %d signals suppressed by cooldown", len(suppressed))

        signal_count = int(df["Signal"].sum())
        logger.info(
            "EWJ-007: Detected %d signals "
            "(vix_lookback=%d, max_vix_change=%+.1f, max_vix_level=%.1f)",
            signal_count,
            self.config.vix_direction_lookback,
            self.config.max_vix_change,
            self.config.max_vix_level,
        )
        return df
