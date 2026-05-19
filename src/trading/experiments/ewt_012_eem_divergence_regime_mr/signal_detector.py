"""EWT–EEM Cross-Asset Divergence Regime-Gated MR 訊號偵測器 (EWT-012)

在 EWT-009 Att3 全域最優框架（六條件 Post-Capitulation Vol-Transition MR）之上
新增第 7 條件「EWT–EEM 跨資產 divergence regime gate」：

  divergence = EWT N 日累計報酬 − EEM N 日累計報酬
  - CEILING: divergence <= divergence_threshold（filter 台灣相對 EM 假強勢）
  - FLOOR:   divergence >= divergence_threshold（僅在台灣未顯著弱於 EM 時進場）

執行模型於 T+1 開盤進場（沿用 EWT-009 ExecutionModelStrategy）。
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.ewt_012_eem_divergence_regime_mr.config import EWT012Config

logger = logging.getLogger(__name__)


class EWT012SignalDetector(BaseSignalDetector):
    """EWT-012：EWT-009 Att3 框架 + EWT–EEM 跨資產 divergence regime gate"""

    def __init__(self, config: EWT012Config):
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

        # Bollinger Bands（沿用 EWT-009）
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

        # Capitulation strength（沿用 EWT-009 Att3：2DD floor）
        df["Ret_1d"] = df["Close"].pct_change(1)
        df["Ret_2d"] = df["Close"].pct_change(2)

        # ===== EWT–EEM 跨資產 divergence regime gate（EWT-012 核心新增）=====
        start_date = df.index[0].strftime("%Y-%m-%d")
        div_n = self.config.divergence_lookback
        df["EWT_Ret_Ndiv"] = df["Close"].pct_change(div_n)
        eem_df = self._fetch_external(self.config.divergence_ticker, start_date)
        if eem_df is None or eem_df.empty:
            logger.error(
                "無法取得 %s 數據，EWT–EEM divergence 過濾停用",
                self.config.divergence_ticker,
            )
            df["EEM_Ret_Ndiv"] = 0.0
            df["Divergence_Nd"] = 0.0
        else:
            eem_close = eem_df["Close"].reindex(df.index, method="ffill")
            df["EEM_Ret_Ndiv"] = eem_close.pct_change(div_n)
            df["Divergence_Nd"] = df["EWT_Ret_Ndiv"] - df["EEM_Ret_Ndiv"]

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

        if self.config.use_divergence_gate:
            if self.config.divergence_mode == "ceiling":
                cond_div = df["Divergence_Nd"] <= self.config.divergence_threshold
            elif self.config.divergence_mode == "floor":
                cond_div = df["Divergence_Nd"] >= self.config.divergence_threshold
            else:
                raise ValueError(f"Unsupported divergence_mode: {self.config.divergence_mode}")
        else:
            cond_div = pd.Series(True, index=df.index)

        df["Signal"] = (
            cond_bb & cond_cap & cond_wr & cond_closepos & cond_atr & cond_cap_strength & cond_div
        )

        # Cooldown mechanism（沿用 EWT-009）
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
            logger.info("EWT-012: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "EWT-012: Detected %d signals (divergence_gate=%s, mode=%s, %dd, thr=%.4f)",
            signal_count,
            self.config.use_divergence_gate,
            self.config.divergence_mode,
            self.config.divergence_lookback,
            self.config.divergence_threshold,
        )
        return df
