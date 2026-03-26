"""
追蹤停損回測引擎 (Trailing Stop Backtester)
在 ExecutionModelBacktester 基礎上加入追蹤停損機制。
當持倉獲利達到啟動門檻後，停損價跟隨最高價上移。

Extends ExecutionModelBacktester with trailing stop mechanism.
Once position gain reaches activation threshold, stop trails the highest price.
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_config import ExperimentConfig

logger = logging.getLogger(__name__)


class TrailingStopBacktester:
    """追蹤停損回測引擎"""

    def __init__(
        self,
        config: ExperimentConfig,
        slippage_pct: float = 0.001,
        trail_activation_pct: float = 0.01,  # 獲利 +1% 後啟動追蹤
        trail_distance_pct: float = 0.015,  # 追蹤距離 1.5%
    ):
        self.config = config
        self.slippage_pct = slippage_pct
        self.trail_activation_pct = trail_activation_pct
        self.trail_distance_pct = trail_distance_pct

    def run(self, df: pd.DataFrame) -> dict:
        signal_indices = df.index[df["Signal"]].tolist()

        if not signal_indices:
            return self._empty_result()

        trades: list[dict] = []
        unfilled_signals: list[dict] = []
        consecutive_losses = 0
        max_consecutive_losses = 0

        profit_target = self.config.profit_target
        stop_loss = self.config.stop_loss
        holding_days = self.config.holding_days

        for signal_date in signal_indices:
            future_mask = df.index > signal_date
            future_df = df.loc[future_mask]

            if future_df.empty:
                unfilled_signals.append(
                    {
                        "date": signal_date.strftime("%Y-%m-%d"),
                        "reason": "no_next_day_data",
                    }
                )
                continue

            entry_date = future_df.index[0]
            raw_entry_price = future_df.iloc[0]["Open"]
            entry_price = raw_entry_price * (1 + self.slippage_pct)

            hold_df = future_df.iloc[1 : holding_days + 1]

            target_price = entry_price * (1 + profit_target)
            initial_stop_price = entry_price * (1 + stop_loss)

            # 追蹤停損狀態 (Trailing stop state)
            current_stop = initial_stop_price
            highest_price = entry_price  # 進場後最高價
            trail_activated = False

            trade_return = None
            exit_price = None
            exit_type = None
            exit_date = None
            days_held = 0
            min_low = float("inf")

            for day_idx, (day_date, row) in enumerate(hold_df.iterrows(), start=1):
                min_low = min(min_low, row["Low"])

                # 更新最高價 (Update highest price seen)
                if row["High"] > highest_price:
                    highest_price = row["High"]

                # 檢查是否啟動追蹤停損 (Check trail activation)
                unrealized_gain = (highest_price - entry_price) / entry_price
                if not trail_activated and unrealized_gain >= self.trail_activation_pct:
                    trail_activated = True

                # 若已啟動，更新追蹤停損價 (If activated, update trailing stop)
                if trail_activated:
                    trail_stop = highest_price * (1 - self.trail_distance_pct)
                    current_stop = max(current_stop, trail_stop)

                stop_hit = row["Low"] <= current_stop
                target_hit = row["High"] >= target_price

                # 悲觀認定 (Pessimistic execution)
                if stop_hit and target_hit:
                    exit_price = current_stop * (1 - self.slippage_pct)
                    trade_return = (exit_price - entry_price) / entry_price
                    exit_type = "stop_loss_pessimistic"
                    exit_date = day_date
                    days_held = day_idx
                    break

                if stop_hit:
                    exit_price = current_stop * (1 - self.slippage_pct)
                    trade_return = (exit_price - entry_price) / entry_price
                    if trail_activated and current_stop > initial_stop_price:
                        exit_type = "trailing_stop"
                    else:
                        exit_type = "stop_loss"
                    exit_date = day_date
                    days_held = day_idx
                    break

                if target_hit:
                    exit_price = target_price
                    trade_return = (exit_price - entry_price) / entry_price
                    exit_type = "target"
                    exit_date = day_date
                    days_held = day_idx
                    break

            # 到期出場 (Time expiry)
            if trade_return is None:
                if not hold_df.empty:
                    last_hold_date = hold_df.index[-1]
                    after_hold = df.loc[df.index > last_hold_date]
                    days_held = len(hold_df)
                    min_low = min(min_low, hold_df["Low"].min()) if not hold_df.empty else min_low
                else:
                    after_hold = pd.DataFrame()
                    days_held = 0

                if not after_hold.empty:
                    exit_date = after_hold.index[0]
                    raw_exit_price = after_hold.iloc[0]["Open"]
                    exit_price = raw_exit_price * (1 - self.slippage_pct)
                    trade_return = (exit_price - entry_price) / entry_price
                    exit_type = "time_expiry"
                else:
                    if not hold_df.empty:
                        exit_date = hold_df.index[-1]
                        exit_price = hold_df.iloc[-1]["Close"] * (1 - self.slippage_pct)
                    else:
                        exit_date = entry_date
                        exit_price = entry_price * (1 - self.slippage_pct)
                    trade_return = (exit_price - entry_price) / entry_price
                    exit_type = "time_expiry"

            max_dd = (min_low - entry_price) / entry_price if min_low != float("inf") else 0.0

            if trade_return < 0:
                consecutive_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
            else:
                consecutive_losses = 0

            trades.append(
                {
                    "date": signal_date.strftime("%Y-%m-%d"),
                    "entry_date": entry_date.strftime("%Y-%m-%d"),
                    "exit_date": exit_date.strftime("%Y-%m-%d"),
                    "entry": round(float(entry_price), 2),
                    "exit": round(float(exit_price), 2),
                    "return_pct": round(float(trade_return) * 100, 2),
                    "holding_days": days_held,
                    "exit_type": exit_type,
                    "max_drawdown_pct": round(float(max_dd) * 100, 2),
                }
            )

        if not trades:
            result = self._empty_result()
            result["unfilled_signals"] = unfilled_signals
            result["unfilled_count"] = len(unfilled_signals)
            result["filled_count"] = 0
            result["fill_rate"] = 0.0
            return result

        returns = [t["return_pct"] for t in trades]
        total = len(trades)
        wins = sum(1 for r in returns if r > 0)
        target_exits = sum(1 for t in trades if t["exit_type"] == "target")
        stop_exits = sum(
            1 for t in trades if t["exit_type"] in ("stop_loss", "stop_loss_pessimistic")
        )
        trailing_exits = sum(1 for t in trades if t["exit_type"] == "trailing_stop")
        pessimistic_exits = sum(1 for t in trades if t["exit_type"] == "stop_loss_pessimistic")
        time_exits = sum(1 for t in trades if t["exit_type"] == "time_expiry")

        cumulative = 1.0
        for r in returns:
            cumulative *= 1 + r / 100
        cumulative_return = (cumulative - 1) * 100

        avg_return = float(np.mean(returns))
        std_return = float(np.std(returns)) if len(returns) > 1 else 0.0
        avg_holding = float(np.mean([t["holding_days"] for t in trades]))
        worst_dd = min(t["max_drawdown_pct"] for t in trades)

        total_signals = total + len(unfilled_signals)
        fill_rate = total / total_signals if total_signals > 0 else 0.0

        ticker_str = ", ".join(self.config.tickers)
        logger.info(
            f"[TrailingStopBacktester] {ticker_str}: {total} 成交/{total_signals} 訊號 "
            f"(成交率 {fill_rate:.1%}), "
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
            "stop_loss_exits": stop_exits + trailing_exits,
            "time_expiry_exits": time_exits,
            "pessimistic_exits": pessimistic_exits,
            "trailing_stop_exits": trailing_exits,
            "trades": trades,
            "filled_count": total,
            "unfilled_count": len(unfilled_signals),
            "unfilled_signals": unfilled_signals,
            "fill_rate": round(fill_rate, 4),
            "execution_model": {
                "entry_mode": "next_open_market",
                "exit_profit": "limit_order_day",
                "exit_stop": "stop_market_gtc",
                "exit_expiry": "next_open_market",
                "slippage_pct": self.slippage_pct,
                "pessimistic_execution": True,
                "trailing_stop": {
                    "activation_pct": self.trail_activation_pct,
                    "distance_pct": self.trail_distance_pct,
                },
            },
        }

    def _empty_result(self) -> dict:
        ticker_str = ", ".join(self.config.tickers)
        return {
            "ticker": ticker_str,
            "total_signals": 0,
            "wins": 0,
            "win_rate": 0.0,
            "avg_return_pct": 0.0,
            "std_return_pct": 0.0,
            "cumulative_return_pct": 0.0,
            "avg_holding_days": 0.0,
            "max_drawdown_pct": 0.0,
            "max_consecutive_losses": 0,
            "target_exits": 0,
            "stop_loss_exits": 0,
            "time_expiry_exits": 0,
            "pessimistic_exits": 0,
            "trailing_stop_exits": 0,
            "trades": [],
            "filled_count": 0,
            "unfilled_count": 0,
            "unfilled_signals": [],
            "fill_rate": 0.0,
            "execution_model": {
                "entry_mode": "next_open_market",
                "exit_profit": "limit_order_day",
                "exit_stop": "stop_market_gtc",
                "exit_expiry": "next_open_market",
                "slippage_pct": self.slippage_pct,
                "pessimistic_execution": True,
                "trailing_stop": {
                    "activation_pct": self.trail_activation_pct,
                    "distance_pct": self.trail_distance_pct,
                },
            },
        }
