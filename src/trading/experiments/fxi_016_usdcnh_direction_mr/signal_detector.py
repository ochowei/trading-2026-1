"""
FXI-016 訊號偵測器：USDCNH Direction Filter on FXI-ASHR Cross-Asset Divergence MR

進場條件（全部滿足，訊號日為 T，執行模型於 T+1 開盤進場）：
1. 10日高點回檔 >= -5%（pullback floor，同 FXI-014/015）
2. 10日高點回檔 <= -12%（pullback cap，同 FXI-014/015）
3. Williams %R(10) <= -80（同 FXI-014/015）
4. ClosePos >= 40%（intraday reversal confirmation，同 FXI-014/015）
5. ATR(5)/ATR(20) > 1.05（panic confirmation FLOOR，同 FXI-014/015）
6. ATR(5)/ATR(20) <= 1.35（in-crash acceleration CEILING，同 FXI-014/015）
7. FXI 20d 報酬 - ASHR 20d 報酬 >= -8%（H-A divergence floor，同 FXI-015 Att2）
8. **USDCNH N 日報酬 <= max_change**（FXI-016 核心新增 yuan direction 過濾）
9. 冷卻期 10 個交易日

USDCNH 過濾的設計依據：
- FXI = iShares China Large-Cap ETF（USD-denominated，持有 H 股 JPY-equivalent
  HKD-pegged-to-USD 結構）
- USDCNH = 離岸人民幣對美元匯率（CNH 為 offshore yuan，反映外資對中國資產
  的市場定價，比 onshore CNY 更敏感於資本流動）
- 當 USDCNH 急升（CNH 急貶）時：
  - 中國資本外流加劇（外資撤離、地緣政治壓力）
  - PBoC 介入若失敗 → risk-off 加劇 → FXI capitulation MR 失敗率升高
- 過濾 USDCNH 急升訊號 = 移除「資本外流 + 政策衝擊」失敗模式

跨資產貢獻：
- Repo 首次「USDCNH (USD/CNH offshore rate) direction filter」於任何資產
- 與 EWJ-006 USDJPY direction filter 結構平行：同為「USD 計價單一國家 ETF
  + 該國貨幣 vs USD」（lesson #24 family v8 兄弟驗證）
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.fxi_016_usdcnh_direction_mr.config import FXI016Config

logger = logging.getLogger(__name__)


class FXI016USDCNHDirectionDetector(BaseSignalDetector):
    """FXI-016 USDCNH Direction-Gated Cross-Asset Divergence MR"""

    def __init__(self, config: FXI016Config):
        self.config = config

    def _fetch_yahoo_data(self, ticker: str, start_date: str) -> pd.DataFrame | None:
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
        anchor_df = self._fetch_yahoo_data(self.config.anchor_ticker, start_date)

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

        # USDCNH direction filter
        usdcnh_df = self._fetch_yahoo_data(self.config.usdcnh_ticker, start_date)

        if usdcnh_df is None or usdcnh_df.empty:
            logger.error(
                "無法取得 %s 數據，USDCNH 過濾停用",
                self.config.usdcnh_ticker,
            )
            df["USDCNH_Change"] = 0.0
        else:
            usdcnh_close = usdcnh_df["Close"].reindex(df.index, method="ffill")
            df["USDCNH_Change"] = usdcnh_close.pct_change(self.config.usdcnh_lookback)

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
        cond_usdcnh = df["USDCNH_Change"] <= self.config.max_usdcnh_change

        df["Signal"] = (
            cond_pullback
            & cond_cap
            & cond_wr
            & cond_reversal
            & cond_vol_floor
            & cond_vol_ceiling
            & cond_rel
            & cond_usdcnh
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
            logger.info("FXI-016: %d signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info(
            "FXI-016: Detected %d signals (usdcnh_lookback=%dd, max_change=%.4f)",
            signal_count,
            self.config.usdcnh_lookback,
            self.config.max_usdcnh_change,
        )
        return df
