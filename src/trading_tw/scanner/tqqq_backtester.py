"""
TQQQ 恐慌抄底回測引擎 (TQQQ Capitulation Buy Backtester)
對 TQQQ 恐慌抄底訊號進行歷史回測，含停損、獲利目標與時間到期。
Backtests TQQQ capitulation buy signals with stop-loss, profit target, and time expiry.
"""

import logging

import numpy as np
import pandas as pd

from trading_tw.scanner.tqqq_config import (
    TQQQ_HOLDING_DAYS,
    TQQQ_PROFIT_TARGET,
    TQQQ_STOP_LOSS,
)

logger = logging.getLogger(__name__)


class TQQQBacktester:
    """
    TQQQ 回測引擎 (TQQQ Backtester)

    交易規則 (Trading rules):
    - 進場: 訊號日收盤價 (Entry: signal day close)
    - 停損: 收盤價跌破進場價 -8% (Stop-loss: close drops 8% below entry)
    - 獲利目標: 盤中最高價達 +5% (Profit target: intraday high reaches +5%)
    - 時間到期: 第 7 個交易日收盤價出場 (Time expiry: day-7 close)
    - 優先順序: 停損 > 獲利目標 > 時間到期
    """

    @staticmethod
    def run(df: pd.DataFrame) -> dict:
        """
        執行 TQQQ 回測 (Run TQQQ backtest)

        Returns:
            dict with backtest results including per-trade details
        """
        signal_indices = df.index[df["Signal"]].tolist()

        if not signal_indices:
            return TQQQBacktester._empty_result()

        trades: list[dict] = []
        consecutive_losses = 0
        max_consecutive_losses = 0

        for signal_date in signal_indices:
            entry_price = df.loc[signal_date, "Close"]

            # 取得訊號日之後的交易日 (Get trading days after signal)
            future_mask = df.index > signal_date
            future_df = df.loc[future_mask].head(TQQQ_HOLDING_DAYS)

            if future_df.empty:
                trades.append({
                    "date": signal_date.strftime("%Y-%m-%d"),
                    "exit_date": signal_date.strftime("%Y-%m-%d"),
                    "entry": round(float(entry_price), 2),
                    "exit": round(float(entry_price), 2),
                    "return_pct": 0.0,
                    "holding_days": 0,
                    "exit_type": "no_data",
                    "max_drawdown_pct": 0.0,
                })
                continue

            target_price = entry_price * (1 + TQQQ_PROFIT_TARGET)
            stop_price = entry_price * (1 + TQQQ_STOP_LOSS)

            # 逐日檢查出場條件 (Check exit conditions day by day)
            trade_return = None
            exit_price = None
            exit_type = None
            exit_date = None
            holding_days = 0
            min_low = float("inf")

            for day_idx, (day_date, row) in enumerate(future_df.iterrows(), start=1):
                min_low = min(min_low, row["Low"])

                # 優先檢查停損（收盤價）(Priority 1: stop-loss on close)
                if row["Close"] <= stop_price:
                    exit_price = row["Close"]
                    trade_return = (exit_price - entry_price) / entry_price
                    exit_type = "stop_loss"
                    exit_date = day_date
                    holding_days = day_idx
                    break

                # 檢查獲利目標（盤中最高價）(Priority 2: profit target on high)
                if row["High"] >= target_price:
                    exit_price = target_price
                    trade_return = TQQQ_PROFIT_TARGET
                    exit_type = "target"
                    exit_date = day_date
                    holding_days = day_idx
                    break

            # 未觸發任何條件，以最後一天收盤價出場 (Time expiry)
            if trade_return is None:
                exit_price = future_df["Close"].iloc[-1]
                trade_return = (exit_price - entry_price) / entry_price
                exit_type = "time_expiry"
                exit_date = future_df.index[-1]
                holding_days = len(future_df)
                min_low = min(min_low, future_df["Low"].min())

            # 計算最大回撤 (Max drawdown for this trade)
            max_dd = (min_low - entry_price) / entry_price

            # 追蹤連續虧損 (Track consecutive losses)
            if trade_return < 0:
                consecutive_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
            else:
                consecutive_losses = 0

            trades.append({
                "date": signal_date.strftime("%Y-%m-%d"),
                "exit_date": exit_date.strftime("%Y-%m-%d"),
                "entry": round(float(entry_price), 2),
                "exit": round(float(exit_price), 2),
                "return_pct": round(float(trade_return) * 100, 2),
                "holding_days": holding_days,
                "exit_type": exit_type,
                "max_drawdown_pct": round(float(max_dd) * 100, 2),
            })

        # 彙總統計 (Aggregate statistics)
        returns = [t["return_pct"] for t in trades]
        total = len(trades)
        wins = sum(1 for r in returns if r > 0)
        target_exits = sum(1 for t in trades if t["exit_type"] == "target")
        stop_exits = sum(1 for t in trades if t["exit_type"] == "stop_loss")
        time_exits = sum(1 for t in trades if t["exit_type"] == "time_expiry")

        # 累計報酬 (Cumulative return)
        cumulative = 1.0
        for r in returns:
            cumulative *= (1 + r / 100)
        cumulative_return = (cumulative - 1) * 100

        avg_return = float(np.mean(returns))
        std_return = float(np.std(returns)) if len(returns) > 1 else 0.0
        avg_holding = float(np.mean([t["holding_days"] for t in trades]))
        worst_dd = min(t["max_drawdown_pct"] for t in trades)

        logger.info(
            f"[TQQQBacktester] TQQQ: {total} 訊號, 勝率 {wins}/{total} = {wins/total:.1%}, "
            f"累計報酬 {cumulative_return:.1f}% "
            f"({total} signals, WR {wins/total:.1%}, cumulative {cumulative_return:.1f}%)"
        )

        return {
            "ticker": "TQQQ",
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
            "trades": trades,
        }

    @staticmethod
    def _empty_result() -> dict:
        return {
            "ticker": "TQQQ",
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
            "trades": [],
        }
