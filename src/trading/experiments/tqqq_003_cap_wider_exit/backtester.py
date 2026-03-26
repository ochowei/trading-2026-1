"""
追蹤停利回測引擎 (Trailing Stop Backtester)
在 BaseBacktester 基礎上新增追蹤停利邏輯。
Extends BaseBacktester with trailing stop-loss from peak close since entry.
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_backtester import BaseBacktester
from trading.experiments.tqqq_003_cap_wider_exit.config import TQQQCapWiderExitConfig

logger = logging.getLogger(__name__)


class TrailingStopBacktester(BaseBacktester):
    """
    追蹤停利回測引擎 (Trailing Stop Backtester)

    出場優先順序 (Exit priority):
    1. 停損 (Stop-loss on close)
    2. 追蹤停利 (Trailing stop from peak close)
    3. 獲利目標 (Profit target on high)
    4. 時間到期 (Time expiry)
    """

    def __init__(self, config: TQQQCapWiderExitConfig):
        super().__init__(config)
        self.trailing_stop_pct = config.trailing_stop_pct

    def run(self, df: pd.DataFrame) -> dict:
        signal_indices = df.index[df["Signal"]].tolist()

        if not signal_indices:
            return self._empty_result()

        trades: list[dict] = []
        consecutive_losses = 0
        max_consecutive_losses = 0

        profit_target = self.config.profit_target
        stop_loss = self.config.stop_loss
        holding_days = self.config.holding_days

        for signal_date in signal_indices:
            entry_price = df.loc[signal_date, "Close"]

            future_mask = df.index > signal_date
            future_df = df.loc[future_mask].head(holding_days)

            if future_df.empty:
                trades.append(
                    {
                        "date": signal_date.strftime("%Y-%m-%d"),
                        "exit_date": signal_date.strftime("%Y-%m-%d"),
                        "entry": round(float(entry_price), 2),
                        "exit": round(float(entry_price), 2),
                        "return_pct": 0.0,
                        "holding_days": 0,
                        "exit_type": "no_data",
                        "max_drawdown_pct": 0.0,
                    }
                )
                continue

            target_price = entry_price * (1 + profit_target)
            stop_price = entry_price * (1 + stop_loss)

            trade_return = None
            exit_price = None
            exit_type = None
            exit_date = None
            days_held = 0
            min_low = float("inf")
            max_close_since_entry = float(entry_price)

            for day_idx, (day_date, row) in enumerate(future_df.iterrows(), start=1):
                min_low = min(min_low, row["Low"])

                # Priority 1: 停損（收盤價）
                if row["Close"] <= stop_price:
                    exit_price = row["Close"]
                    trade_return = (exit_price - entry_price) / entry_price
                    exit_type = "stop_loss"
                    exit_date = day_date
                    days_held = day_idx
                    break

                # 更新持倉期間最高收盤價 (Update peak close)
                max_close_since_entry = max(max_close_since_entry, row["Close"])

                # Priority 2: 追蹤停利（收盤價從高點回落超過閾值）
                trailing_stop_price = max_close_since_entry * (1 + self.trailing_stop_pct)
                if row["Close"] <= trailing_stop_price and max_close_since_entry > entry_price:
                    exit_price = row["Close"]
                    trade_return = (exit_price - entry_price) / entry_price
                    exit_type = "trailing_stop"
                    exit_date = day_date
                    days_held = day_idx
                    break

                # Priority 3: 獲利目標（盤中最高價）
                if row["High"] >= target_price:
                    exit_price = target_price
                    trade_return = profit_target
                    exit_type = "target"
                    exit_date = day_date
                    days_held = day_idx
                    break

            # 時間到期 (Time expiry)
            if trade_return is None:
                exit_price = future_df["Close"].iloc[-1]
                trade_return = (exit_price - entry_price) / entry_price
                exit_type = "time_expiry"
                exit_date = future_df.index[-1]
                days_held = len(future_df)
                min_low = min(min_low, future_df["Low"].min())

            max_dd = (min_low - entry_price) / entry_price

            if trade_return < 0:
                consecutive_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
            else:
                consecutive_losses = 0

            trades.append(
                {
                    "date": signal_date.strftime("%Y-%m-%d"),
                    "exit_date": exit_date.strftime("%Y-%m-%d"),
                    "entry": round(float(entry_price), 2),
                    "exit": round(float(exit_price), 2),
                    "return_pct": round(float(trade_return) * 100, 2),
                    "holding_days": days_held,
                    "exit_type": exit_type,
                    "max_drawdown_pct": round(float(max_dd) * 100, 2),
                }
            )

        # 彙總統計 (Aggregate statistics)
        returns = [t["return_pct"] for t in trades]
        total = len(trades)
        wins = sum(1 for r in returns if r > 0)
        target_exits = sum(1 for t in trades if t["exit_type"] == "target")
        stop_exits = sum(1 for t in trades if t["exit_type"] == "stop_loss")
        time_exits = sum(1 for t in trades if t["exit_type"] == "time_expiry")
        trailing_exits = sum(1 for t in trades if t["exit_type"] == "trailing_stop")

        cumulative = 1.0
        for r in returns:
            cumulative *= 1 + r / 100
        cumulative_return = (cumulative - 1) * 100

        avg_return = float(np.mean(returns))
        std_return = float(np.std(returns)) if len(returns) > 1 else 0.0
        avg_holding = float(np.mean([t["holding_days"] for t in trades]))
        worst_dd = min(t["max_drawdown_pct"] for t in trades)

        ticker_str = ", ".join(self.config.tickers)
        logger.info(
            f"[TrailingStopBacktester] {ticker_str}: {total} 訊號, "
            f"勝率 {wins}/{total} = {wins / total:.1%}, "
            f"累計報酬 {cumulative_return:.1f}%"
        )

        return {
            "ticker": ticker_str,
            "total_signals": total,
            "wins": wins,
            "win_rate": wins / total if total > 0 else 0.0,
            "avg_return_pct": round(avg_return, 2),
            "std_return_pct": round(std_return, 2),
            "cumulative_return_pct": round(cumulative_return, 2),
            "avg_holding_days": round(avg_holding, 1),
            "max_drawdown_pct": round(worst_dd, 2),
            "max_consecutive_losses": max_consecutive_losses,
            "target_exits": target_exits,
            "stop_loss_exits": stop_exits,
            "time_expiry_exits": time_exits,
            "trailing_stop_exits": trailing_exits,
            "trades": trades,
        }
