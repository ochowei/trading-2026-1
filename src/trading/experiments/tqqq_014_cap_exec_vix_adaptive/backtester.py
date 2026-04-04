"""
VIX 自適應成交模型回測引擎 (VIX-Adaptive Execution Model Backtester)
根據訊號日 VIX 水準動態選擇 TP/SL/持倉天數。
Dynamically selects TP/SL/holding based on VIX level at signal date.
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_config import ExperimentConfig
from trading.experiments.tqqq_014_cap_exec_vix_adaptive.config import TQQQVixAdaptiveConfig

logger = logging.getLogger(__name__)


class VIXAdaptiveBacktester:
    """
    VIX 自適應成交模型回測引擎

    與 ExecutionModelBacktester 的主要差異:
    - TP/SL/持倉天數不固定，根據訊號日 VIX 動態決定
    - 需要 DataFrame 中包含 VIX 欄位
    - 其餘成交邏輯（隔日開盤進場、悲觀認定等）完全相同
    """

    def __init__(self, config: ExperimentConfig, slippage_pct: float = 0.001):
        self.config = config
        self.slippage_pct = slippage_pct

    def _get_exit_params(self, vix_value: float) -> tuple[float, float, int, str]:
        """根據 VIX 水準取得出場參數 (TP, SL, holding_days, tier_label)"""
        if not isinstance(self.config, TQQQVixAdaptiveConfig):
            return (
                self.config.profit_target,
                self.config.stop_loss,
                self.config.holding_days,
                "default",
            )

        for tier in self.config.vix_tiers:
            if tier.vix_min <= vix_value < tier.vix_max:
                return (
                    tier.profit_target,
                    tier.stop_loss,
                    tier.holding_days,
                    tier.label,
                )

        # Fallback to config defaults
        return (
            self.config.profit_target,
            self.config.stop_loss,
            self.config.holding_days,
            "fallback",
        )

    def run(self, df: pd.DataFrame) -> dict:
        """執行 VIX 自適應成交模型回測"""
        signal_indices = df.index[df["Signal"]].tolist()

        if not signal_indices:
            return self._empty_result()

        trades: list[dict] = []
        unfilled_signals: list[dict] = []
        consecutive_losses = 0
        max_consecutive_losses = 0
        tier_counts: dict[str, int] = {}

        has_vix = "VIX" in df.columns

        for signal_date in signal_indices:
            # 取得訊號日 VIX 並決定出場參數
            if has_vix and pd.notna(df.loc[signal_date, "VIX"]):
                vix_value = float(df.loc[signal_date, "VIX"])
            else:
                vix_value = 30.0  # Fallback: assume elevated fear
                logger.warning(
                    f"[VIXAdaptive] {signal_date.strftime('%Y-%m-%d')}: "
                    "VIX unavailable, using fallback 30.0"
                )

            profit_target, stop_loss, holding_days, tier_label = self._get_exit_params(vix_value)
            tier_counts[tier_label] = tier_counts.get(tier_label, 0) + 1

            # === 進場: 隔日開盤市價 ===
            future_mask = df.index > signal_date
            future_df = df.loc[future_mask]

            if future_df.empty:
                unfilled_signals.append(
                    {"date": signal_date.strftime("%Y-%m-%d"), "reason": "no_next_day_data"}
                )
                continue

            entry_date = future_df.index[0]
            raw_entry_price = future_df.iloc[0]["Open"]
            entry_price = raw_entry_price * (1 + self.slippage_pct)

            hold_df = future_df.iloc[1 : holding_days + 1]

            target_price = entry_price * (1 + profit_target)
            stop_price = entry_price * (1 + stop_loss)

            # === 逐日檢查出場條件 ===
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

                if stop_hit and target_hit:
                    exit_price = stop_price * (1 - self.slippage_pct)
                    trade_return = (exit_price - entry_price) / entry_price
                    exit_type = "stop_loss_pessimistic"
                    exit_date = day_date
                    days_held = day_idx
                    break

                if stop_hit:
                    exit_price = stop_price * (1 - self.slippage_pct)
                    trade_return = (exit_price - entry_price) / entry_price
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

            # === 到期出場 ===
            if trade_return is None:
                if not hold_df.empty:
                    last_hold_date = hold_df.index[-1]
                    after_hold = df.loc[df.index > last_hold_date]
                    days_held = len(hold_df)
                    min_low = min(min_low, hold_df["Low"].min())
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
                    "vix_at_signal": round(vix_value, 1),
                    "vix_tier": tier_label,
                    "tp_used": f"+{profit_target:.0%}",
                    "sl_used": f"{stop_loss:.0%}",
                }
            )

        # === 彙總統計 ===
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

        cumulative = 1.0
        for r in returns:
            cumulative *= 1 + r / 100
        cumulative_return = (cumulative - 1) * 100

        avg_return = float(np.mean(returns))
        std_return = float(np.std(returns)) if len(returns) > 1 else 0.0
        avg_holding = float(np.mean([t["holding_days"] for t in trades]))
        worst_dd = min(t["max_drawdown_pct"] for t in trades)

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

        total_signals = total + len(unfilled_signals)
        fill_rate = total / total_signals if total_signals > 0 else 0.0

        ticker_str = ", ".join(self.config.tickers)
        logger.info(
            f"[VIXAdaptiveBacktester] {ticker_str}: {total} filled/{total_signals} signals "
            f"(fill rate {fill_rate:.1%}), "
            f"WR {wins / total:.1%}, cumulative {cumulative_return:.1f}%, "
            f"tier distribution: {tier_counts}"
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
            "filled_count": total,
            "unfilled_count": len(unfilled_signals),
            "unfilled_signals": unfilled_signals,
            "fill_rate": round(fill_rate, 4),
            "vix_tier_distribution": tier_counts,
            "execution_model": {
                "entry_mode": "next_open_market",
                "exit_profit": "limit_order_day",
                "exit_stop": "stop_market_gtc",
                "exit_expiry": "next_open_market",
                "slippage_pct": self.slippage_pct,
                "pessimistic_execution": True,
                "vix_adaptive": True,
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
            "vix_tier_distribution": {},
            "execution_model": {
                "entry_mode": "next_open_market",
                "exit_profit": "limit_order_day",
                "exit_stop": "stop_market_gtc",
                "exit_expiry": "next_open_market",
                "slippage_pct": self.slippage_pct,
                "pessimistic_execution": True,
                "vix_adaptive": True,
            },
        }
