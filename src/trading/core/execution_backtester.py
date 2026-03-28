"""
成交模型回測引擎 (Execution Model Backtester)
模擬貼近實盤的成交邏輯，包含滑價、委託類型與悲觀認定。
Simulates realistic trade execution with slippage, order types, and pessimistic fills.

成交模型設計 (Execution Model Design):
- 進場: next_open_market — 訊號日收盤偵測 → 隔日開盤市價單進場（含滑價）
- 止盈: limit_order (Day) — 每日掛限價賣單，High >= 目標價時以目標價成交
- 停損: stop_market (GTC) — 持倉期間掛停損市價單，Low <= 停損價時以停損價成交（含滑價）
- 到期: next_open_market — 持倉到期後隔日開盤市價出場（含滑價）
- 悲觀認定: 同根 K 線 stop 與 target 皆觸發 → 假定停損先成交（最差結果）
- 未成交: 隔日無資料時視為 unfilled

Entry: next_open_market — Signal at close → market order at next day's Open (+ slippage)
Profit target: limit_order (Day) — Limit sell, filled at target if High >= target
Stop loss: stop_market (GTC) — Stop sell, filled at stop price (+ slippage) if Low <= stop
Time expiry: next_open_market — Exit at next day's Open after holding period (+ slippage)
Pessimistic execution: If both stop and target hit on same bar → assume stop hit first
Unfilled: If no next-day data after signal → treated as unfilled (missed opportunity)
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_config import ExperimentConfig

logger = logging.getLogger(__name__)


class ExecutionModelBacktester:
    """
    成交模型回測引擎 (Execution Model Backtester)

    與 BaseBacktester 的主要差異 (Key differences from BaseBacktester):
    1. 進場: 隔日開盤市價 (vs 訊號日收盤)
    2. 停損: 盤中 Low 觸發，以停損價+滑價成交 (vs 收盤價觸發)
    3. 止盈: 盤中 High 觸發，以目標價成交 (vs 同)
    4. 悲觀認定: 同根 K 線 stop+target 皆觸及 → 停損優先 (vs 停損優先但基於收盤)
    5. 到期: 隔日開盤市價出場 (vs 最後一天收盤)
    6. 滑價: 市價單加計滑價 (vs 無滑價)
    7. 未成交統計: 記錄 unfilled 訊號 (vs 無)
    """

    def __init__(self, config: ExperimentConfig, slippage_pct: float = 0.001):
        """
        Args:
            config: 實驗配置
            slippage_pct: 市價單滑價比例 (預設 0.1%)
        """
        self.config = config
        self.slippage_pct = slippage_pct

    def run(self, df: pd.DataFrame) -> dict:
        """
        執行成交模型回測 (Run backtest with execution model)

        Args:
            df: DataFrame with 'Signal' boolean column and OHLCV data

        Returns:
            dict with backtest results including per-trade details and fill statistics
        """
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
            # === 進場: 隔日開盤市價 (Entry: next day open market order) ===
            future_mask = df.index > signal_date
            future_df = df.loc[future_mask]

            if future_df.empty:
                # 訊號後無資料 → unfilled
                unfilled_signals.append(
                    {
                        "date": signal_date.strftime("%Y-%m-%d"),
                        "reason": "no_next_day_data",
                    }
                )
                continue

            entry_date = future_df.index[0]
            raw_entry_price = future_df.iloc[0]["Open"]
            # 買入滑價: 市價買入 → 價格向上滑 (Buy slippage: price slides up)
            entry_price = raw_entry_price * (1 + self.slippage_pct)

            # 持倉期間: 進場日起算 holding_days 個交易日
            # Holding period: holding_days trading days starting from entry day
            hold_df = future_df.iloc[1 : holding_days + 1]  # 進場日之後的交易日

            target_price = entry_price * (1 + profit_target)
            stop_price = entry_price * (1 + stop_loss)

            # === 逐日檢查出場條件 (Check exit conditions day by day) ===
            trade_return = None
            exit_price = None
            exit_type = None
            exit_date = None
            days_held = 0
            min_low = float("inf")

            for day_idx, (day_date, row) in enumerate(hold_df.iterrows(), start=1):
                min_low = min(min_low, row["Low"])

                stop_hit = row["Low"] <= stop_price
                target_hit = row["High"] >= target_price

                # === 悲觀認定 (Pessimistic Execution) ===
                # 若同根 K 線 stop 與 target 皆觸發 → 假定停損先成交
                if stop_hit and target_hit:
                    # 悲觀: 停損優先 (Pessimistic: stop loss takes priority)
                    exit_price = stop_price * (1 - self.slippage_pct)  # 賣出滑價向下
                    trade_return = (exit_price - entry_price) / entry_price
                    exit_type = "stop_loss_pessimistic"
                    exit_date = day_date
                    days_held = day_idx
                    break

                # Priority 1: 停損 — stop_market 觸發 (Low <= stop_price)
                if stop_hit:
                    # stop_market: 以停損價成交，加計賣出滑價（向下）
                    exit_price = stop_price * (1 - self.slippage_pct)
                    trade_return = (exit_price - entry_price) / entry_price
                    exit_type = "stop_loss"
                    exit_date = day_date
                    days_held = day_idx
                    break

                # Priority 2: 止盈 — limit_order 觸發 (High >= target_price)
                if target_hit:
                    # limit_order: 以目標價精確成交（無滑價）
                    exit_price = target_price
                    trade_return = (exit_price - entry_price) / entry_price
                    exit_type = "target"
                    exit_date = day_date
                    days_held = day_idx
                    break

            # === 到期出場: next_open_market (Time expiry: exit at next open) ===
            if trade_return is None:
                # 找持倉期結束後的下一個交易日
                if not hold_df.empty:
                    last_hold_date = hold_df.index[-1]
                    after_hold = df.loc[df.index > last_hold_date]
                    days_held = len(hold_df)
                    min_low = min(min_low, hold_df["Low"].min()) if not hold_df.empty else min_low
                else:
                    # 進場後無持倉資料（只有進場日）
                    after_hold = pd.DataFrame()
                    days_held = 0

                if not after_hold.empty:
                    exit_date = after_hold.index[0]
                    raw_exit_price = after_hold.iloc[0]["Open"]
                    # 賣出滑價: 市價賣出 → 價格向下滑
                    exit_price = raw_exit_price * (1 - self.slippage_pct)
                    trade_return = (exit_price - entry_price) / entry_price
                    exit_type = "time_expiry"
                else:
                    # 到期後無資料 → 以最後收盤價出場（備用）
                    if not hold_df.empty:
                        exit_date = hold_df.index[-1]
                        exit_price = hold_df.iloc[-1]["Close"] * (1 - self.slippage_pct)
                    else:
                        exit_date = entry_date
                        exit_price = entry_price * (1 - self.slippage_pct)
                    trade_return = (exit_price - entry_price) / entry_price
                    exit_type = "time_expiry"

            # 計算最大回撤 (Max drawdown for this trade)
            max_dd = (min_low - entry_price) / entry_price if min_low != float("inf") else 0.0

            # 追蹤連續虧損 (Track consecutive losses)
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

        # === 彙總統計 (Aggregate statistics) ===
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
        pessimistic_exits = sum(1 for t in trades if t["exit_type"] == "stop_loss_pessimistic")
        time_exits = sum(1 for t in trades if t["exit_type"] == "time_expiry")

        # 累計報酬 (Cumulative return)
        cumulative = 1.0
        for r in returns:
            cumulative *= 1 + r / 100
        cumulative_return = (cumulative - 1) * 100

        avg_return = float(np.mean(returns))
        std_return = float(np.std(returns)) if len(returns) > 1 else 0.0
        avg_holding = float(np.mean([t["holding_days"] for t in trades]))
        worst_dd = min(t["max_drawdown_pct"] for t in trades)

        # 風險調整後報酬指標 (Risk-adjusted return metrics)
        gross_profit = sum(r for r in returns if r > 0)
        gross_loss = sum(r for r in returns if r < 0)
        profit_factor = gross_profit / abs(gross_loss) if gross_loss != 0 else 999.99

        sharpe_ratio = avg_return / std_return if std_return > 0 else 0.0

        downside_returns = [min(r, 0) for r in returns]
        downside_dev = float(np.sqrt(np.mean(np.square(downside_returns))))
        sortino_ratio = (
            avg_return / downside_dev if downside_dev > 0 else (999.99 if avg_return > 0 else 0.0)
        )

        calmar_ratio = (
            avg_return / abs(worst_dd) if worst_dd != 0 else (999.99 if avg_return > 0 else 0.0)
        )

        # 成交統計 (Fill statistics)
        total_signals = total + len(unfilled_signals)
        fill_rate = total / total_signals if total_signals > 0 else 0.0

        ticker_str = ", ".join(self.config.tickers)
        logger.info(
            f"[ExecutionModelBacktester] {ticker_str}: {total} 成交/{total_signals} 訊號 "
            f"(成交率 {fill_rate:.1%}), "
            f"勝率 {wins}/{total} = {wins / total:.1%}, "
            f"累計報酬 {cumulative_return:.1f}% "
            f"({total} filled/{total_signals} signals, "
            f"fill rate {fill_rate:.1%}, "
            f"WR {wins / total:.1%}, cumulative {cumulative_return:.1f}%)"
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
            "profit_factor": round(min(profit_factor, 999.99), 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "sortino_ratio": round(min(sortino_ratio, 999.99), 2),
            "calmar_ratio": round(min(calmar_ratio, 999.99), 2),
            "max_consecutive_losses": max_consecutive_losses,
            "target_exits": target_exits,
            "stop_loss_exits": stop_exits,
            "time_expiry_exits": time_exits,
            "pessimistic_exits": pessimistic_exits,
            "trades": trades,
            # 成交統計 (Fill statistics)
            "filled_count": total,
            "unfilled_count": len(unfilled_signals),
            "unfilled_signals": unfilled_signals,
            "fill_rate": round(fill_rate, 4),
            # 成交模型參數 (Execution model parameters)
            "execution_model": {
                "entry_mode": "next_open_market",
                "exit_profit": "limit_order_day",
                "exit_stop": "stop_market_gtc",
                "exit_expiry": "next_open_market",
                "slippage_pct": self.slippage_pct,
                "pessimistic_execution": True,
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
            "profit_factor": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "calmar_ratio": 0.0,
            "max_consecutive_losses": 0,
            "target_exits": 0,
            "stop_loss_exits": 0,
            "time_expiry_exits": 0,
            "pessimistic_exits": 0,
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
            },
        }
