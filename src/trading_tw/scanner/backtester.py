"""
回測引擎模組 (Backtester Module)
對偵測到的訊號進行歷史回測，計算勝率與績效指標。
Backtests detected signals and computes win rate and performance metrics.
"""

import logging

import numpy as np
import pandas as pd

from trading_tw.scanner.config import Config, HOLDING_DAYS

logger = logging.getLogger(__name__)


class Backtester:
    """
    回測引擎 (Backtester)
    針對每個訊號模擬交易，計算勝率、平均持倉時間與最大回撤。
    Simulates trades for each signal and computes win rate, avg holding period, max drawdown.
    """

    @staticmethod
    def run(df: pd.DataFrame, ticker: str) -> dict:
        """
        執行回測 (Run backtest)

        交易規則 (Trading rules):
        - 進場: 訊號當天收盤價 (Entry: close price on signal day)
        - 出場: 未來 3 個交易日內最高價達到獲利目標 (Exit: high reaches target within 3 days)
        - 若未達目標，以第 3 天收盤價出場 (If target not hit, exit at day-3 close)

        Args:
            df: DataFrame with 'Signal' column
            ticker: 標的代碼 (Ticker symbol)

        Returns:
            dict with backtest results:
            - ticker, total_signals, wins, win_rate
            - avg_holding_days, max_drawdown_pct
            - avg_return_pct, signal_dates
        """
        profit_target = Config.get_profit_target(ticker)
        signal_indices = df.index[df["Signal"]].tolist()

        if not signal_indices:
            return {
                "ticker": ticker,
                "type": "ETF" if Config.is_etf(ticker) else "Stock",
                "total_signals": 0,
                "wins": 0,
                "win_rate": 0.0,
                "avg_holding_days": 0.0,
                "max_drawdown_pct": 0.0,
                "avg_return_pct": 0.0,
                "signal_dates": [],
            }

        wins = 0
        holding_days_list: list[int] = []
        max_drawdowns: list[float] = []
        returns: list[float] = []
        signal_dates: list[str] = []

        for signal_date in signal_indices:
            # 進場價格 = 訊號日收盤價 (Entry = signal day close)
            entry_price = df.loc[signal_date, "Close"]
            signal_dates.append(signal_date.strftime("%Y-%m-%d"))

            # 取得訊號日之後的交易日 (Get trading days after signal)
            future_mask = df.index > signal_date
            future_df = df.loc[future_mask].head(HOLDING_DAYS)

            if future_df.empty:
                # 資料不足，視為虧損 (Insufficient data, treat as loss)
                returns.append(0.0)
                holding_days_list.append(HOLDING_DAYS)
                max_drawdowns.append(0.0)
                continue

            # 計算每日最大回撤 (Compute per-day drawdown)
            trade_drawdown = (future_df["Low"].min() - entry_price) / entry_price
            max_drawdowns.append(trade_drawdown)

            # 檢查是否在持倉期間達到獲利目標 (Check if target reached)
            target_price = entry_price * (1 + profit_target)
            hit = False

            for day_idx, (date, row) in enumerate(future_df.iterrows(), start=1):
                if row["High"] >= target_price:
                    wins += 1
                    holding_days_list.append(day_idx)
                    returns.append(profit_target)
                    hit = True
                    break

            if not hit:
                # 未達目標，以最後一天收盤價計算報酬 (Target not hit, use last close)
                exit_price = future_df["Close"].iloc[-1]
                trade_return = (exit_price - entry_price) / entry_price
                returns.append(trade_return)
                holding_days_list.append(len(future_df))

        total_signals = len(signal_indices)
        win_rate = wins / total_signals if total_signals > 0 else 0.0
        avg_holding = np.mean(holding_days_list) if holding_days_list else 0.0
        worst_drawdown = min(max_drawdowns) if max_drawdowns else 0.0
        avg_return = np.mean(returns) if returns else 0.0

        logger.info(
            f"[Backtester] {ticker}: {total_signals} 訊號, "
            f"勝率 {win_rate:.1%}, 平均持倉 {avg_holding:.1f} 天 "
            f"({total_signals} signals, WR {win_rate:.1%}, avg hold {avg_holding:.1f}d)"
        )

        return {
            "ticker": ticker,
            "type": "ETF" if Config.is_etf(ticker) else "Stock",
            "total_signals": total_signals,
            "wins": wins,
            "win_rate": win_rate,
            "avg_holding_days": round(avg_holding, 1),
            "max_drawdown_pct": round(worst_drawdown * 100, 2),
            "avg_return_pct": round(avg_return * 100, 2),
            "signal_dates": signal_dates,
        }
