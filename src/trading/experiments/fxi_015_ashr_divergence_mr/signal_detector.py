"""
FXI-015 訊號偵測器：FXI-ASHR Cross-Asset Divergence Filter on ATR-Band MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10日高點回檔 >= -5%（pullback floor，同 FXI-014）
2. 10日高點回檔 <= -12%（pullback cap，同 FXI-014）
3. Williams %R(10) <= -80（同 FXI-014）
4. ClosePos >= 40%（intraday reversal confirmation，同 FXI-014）
5. ATR(5)/ATR(20) > 1.05（panic confirmation FLOOR，同 FXI-014）
6. ATR(5)/ATR(20) <= 1.35（in-crash acceleration CEILING，同 FXI-014）
7. **FXI N 日報酬 - ASHR N 日報酬 >= min_rel_return**（FXI-015 核心新增 cross-asset
   divergence floor，過濾 HK 特定壓力導致 H 股結構性弱於 A 股的訊號）
8. 冷卻期 10 個交易日

ASHR 過濾的設計依據：
- ASHR = Direxion Daily CSI 300 ETF（A-share 大陸 onshore 流動性 anchor）
- FXI 持有 H 股（HK 上市），ASHR 持有 A 股（上海/深圳上市）
- FXI vs ASHR N 日相對報酬反映 HK-大陸資金流分歧度
- 當 FXI 大幅弱於 ASHR（負向 >7%）時：HK 特定壓力延續，MR 失敗率升高

Trade-level 驗證（FXI-014 Att2 baseline）：
- Part A 殘餘 3 SLs: Div_10d ∈ [-8.55pp, -2.23pp]
- Part A 18 TPs: Div_10d ∈ [-5.95pp, +3.05pp]
- Surgical sweet spot：Div_10d floor ∈ (-8.55, -5.95)，可乾淨切除 2022-03-02 deep SL
- Part B 5 訊號 Div_10d ∈ [-5.44pp, +1.37pp]，floor >= -7% 完全非綁定
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fxi_015_ashr_divergence_mr.config import FXI015Config

logger = logging.getLogger(__name__)


class FXI015ASHRDivergenceDetector(BaseSignalDetector):
    """FXI-015 FXI-ASHR Cross-Asset Divergence-Gated ATR-Band MR"""

    def __init__(self, config: FXI015Config):
        self.config = config

    def _fetch_anchor_data(self, start_date: str) -> pd.DataFrame | None:
        try:
            df = yf.download(
                self.config.anchor_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.anchor_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Pullback
        n = self.config.pullback_lookback
        df["High_N"] = df["High"].rolling(n).max()
        df["Pullback"] = (df["Close"] - df["High_N"]) / df["High_N"]

        # Williams %R
        wr_n = self.config.wr_period
        highest = df["High"].rolling(wr_n).max()
        lowest = df["Low"].rolling(wr_n).min()
        df["WR"] = (highest - df["Close"]) / (highest - lowest) * -100
        df.loc[(highest - lowest) == 0, "WR"] = -50.0

        # Close Position
        day_range = df["High"] - df["Low"]
        df["ClosePos"] = (df["Close"] - df["Low"]) / day_range
        df.loc[day_range == 0, "ClosePos"] = 0.5

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
        df["ATR_Ratio"] = atr_short / atr_long

        # FXI vs ASHR cross-asset divergence
        fxi_ret_n = df["Close"].pct_change(self.config.rel_lookback)

        start_date = df.index[0].strftime("%Y-%m-%d")
        anchor_df = self._fetch_anchor_data(start_date)

        if anchor_df is None or anchor_df.empty:
            logger.error(
                "無法取得 %s 數據，FXI-ASHR divergence 過濾停用",
                self.config.anchor_ticker,
            )
            df["Rel_Return"] = 0.0
        else:
            anchor_close = anchor_df["Close"].reindex(df.index, method="ffill")
            anchor_ret_n = anchor_close.pct_change(self.config.rel_lookback)
            df["Rel_Return"] = fxi_ret_n - anchor_ret_n

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        cond_pullback = df["Pullback"] <= self.config.pullback_threshold
        cond_cap = df["Pullback"] >= self.config.pullback_cap
        cond_wr = df["WR"] <= self.config.wr_threshold
        cond_reversal = df["ClosePos"] >= self.config.close_position_threshold
        cond_vol_floor = df["ATR_Ratio"] > self.config.atr_ratio_floor
        cond_vol_ceiling = df["ATR_Ratio"] <= self.config.atr_ratio_ceiling
        cond_rel = df["Rel_Return"] >= self.config.min_rel_return

        df["Signal"] = (
            cond_pullback
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol_floor
            & cond_vol_ceiling
            & cond_rel
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
            logger.info("FXI-015: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "FXI-015: Detected %d signals (rel_lookback=%dd, min_rel=%.4f)",
            signal_count,
            self.config.rel_lookback,
            self.config.min_rel_return,
        )
        return df
