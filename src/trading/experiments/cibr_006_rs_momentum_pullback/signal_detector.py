"""
CIBR-006 訊號偵測器：Cybersecurity Sector RS Momentum Pullback

Att3 進場條件（全部滿足）：
1. CIBR 10日報酬 - SPY 10日報酬 >= 2%（網路安全板塊相對大盤超額表現）
2. CIBR 10日高點回撤 3-8%（短暫整理，非深度回調）
3. ATR(5)/ATR(20) > 1.15（波動率急升，恐慌回調而非慢磨）
4. ClosePos >= 40%（日內反轉確認）
5. Close > SMA(50)（上升趨勢確認）
6. 冷卻期 8 個交易日

進化歷程：
- Att1: QQQ 基準 + RS>=3% + 5d pullback 3-8% + SMA(50) → 5 訊號/5yr (太少)
- Att2: SPY 基準 + RS>=2% + 10d pullback 2-8% + 無趨勢 → 28 訊號但 WR 42.9%
- Att3: 保留 SPY+RS>=2%，加入 ATR+ClosePos+SMA 品質過濾 → 精選高品質訊號
"""

import logging

import pandas as pd
import yfinance as yf

from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.cibr_006_rs_momentum_pullback.config import CIBRRSMomentumConfig

logger = logging.getLogger(__name__)


class CIBRRSMomentumDetector(BaseSignalDetector):
    """CIBR 網路安全板塊 RS ���量回調訊號偵測器"""

    def __init__(self, config: CIBRRSMomentumConfig):
        self.config = config

    def _fetch_benchmark_data(self, start_date: str) -> pd.DataFrame | None:
        """下載基準標的數據"""
        try:
            df = yf.download(
                self.config.benchmark_ticker,
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
            logger.exception("Failed to fetch %s data", self.config.benchmark_ticker)
            return None

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        # Fetch benchmark data
        start_date = df.index[0].strftime("%Y-%m-%d")
        benchmark_df = self._fetch_benchmark_data(start_date)

        if benchmark_df is None:
            logger.error("Unable to fetch %s data for RS calculation", cfg.benchmark_ticker)
            df["Relative_Strength"] = 0.0
            df["Pullback"] = 0.0
            df["SMA_Trend"] = df["Close"]
            df["ATR_ratio"] = 0.0
            df["ClosePos"] = 0.5
            return df

        # Align to common dates
        common_idx = df.index.intersection(benchmark_df.index)
        df = df.loc[common_idx]

        # Relative Strength: CIBR N-day return - SPY N-day return
        period = cfg.relative_strength_period
        cibr_return = df["Close"].pct_change(period)
        benchmark_return = benchmark_df.loc[common_idx, "Close"].pct_change(period)
        df["Relative_Strength"] = cibr_return - benchmark_return

        # Pullback from N-day high
        lookback = cfg.pullback_lookback
        df["High_N"] = df["High"].rolling(lookback).max()
        df["Pullback"] = (df["High_N"] - df["Close"]) / df["High_N"]

        # SMA trend
        if cfg.use_sma_trend:
            df["SMA_Trend"] = df["Close"].rolling(cfg.sma_trend_period).mean()

        # ATR ratio
        if cfg.use_atr_filter:
            tr = pd.concat(
                [
                    df["High"] - df["Low"],
                    (df["High"] - df["Close"].shift(1)).abs(),
                    (df["Low"] - df["Close"].shift(1)).abs(),
                ],
                axis=1,
            ).max(axis=1)
            df["ATR_fast"] = tr.rolling(cfg.atr_fast).mean()
            df["ATR_slow"] = tr.rolling(cfg.atr_slow).mean()
            df["ATR_ratio"] = df["ATR_fast"] / df["ATR_slow"].where(
                df["ATR_slow"] > 0, float("nan")
            )

        # Close Position
        if cfg.use_closepos_filter:
            daily_range = df["High"] - df["Low"]
            df["ClosePos"] = ((df["Close"] - df["Low"]) / daily_range).where(daily_range > 0, 0.5)

        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        cfg = self.config

        # Condition 1: Cybersecurity sector outperforms broad market
        cond_rs = df["Relative_Strength"] >= cfg.relative_strength_min

        # Condition 2: Short-term pullback within range
        cond_pullback = (df["Pullback"] >= cfg.pullback_min) & (df["Pullback"] <= cfg.pullback_max)

        # Combine core conditions
        df["Signal"] = cond_rs & cond_pullback

        # Condition 3: ATR volatility spike filter
        if cfg.use_atr_filter:
            cond_atr = df["ATR_ratio"] > cfg.atr_ratio_threshold
            df["Signal"] = df["Signal"] & cond_atr

        # Condition 4: Close Position reversal confirmation
        if cfg.use_closepos_filter:
            cond_closepos = df["ClosePos"] >= cfg.close_pos_threshold
            df["Signal"] = df["Signal"] & cond_closepos

        # Condition 5: SMA trend filter
        if cfg.use_sma_trend:
            cond_trend = df["Close"] > df["SMA_Trend"]
            df["Signal"] = df["Signal"] & cond_trend

        # Cooldown mechanism
        signal_indices = df.index[df["Signal"]].tolist()
        suppressed: list[pd.Timestamp] = []
        last_signal = None

        for idx in signal_indices:
            if last_signal is not None:
                gap = len(df.loc[last_signal:idx]) - 1
                if gap <= cfg.cooldown_days:
                    suppressed.append(idx)
                    continue
            last_signal = idx

        if suppressed:
            df.loc[suppressed, "Signal"] = False
            logger.info("CIBR: %d duplicate signals suppressed by cooldown", len(suppressed))

        signal_count = df["Signal"].sum()
        logger.info("CIBR: Detected %d RS momentum pullback signals", signal_count)
        return df
