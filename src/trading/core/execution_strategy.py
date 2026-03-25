"""
成交模型策略基礎類別 (Execution Model Strategy Base)
繼承 BaseStrategy，覆寫報表列印以顯示成交模型資訊（滑價、成交率、悲觀認定等）。
Extends BaseStrategy with execution model report printing (slippage, fill rate, etc.).
"""

import pandas as pd

from trading.core.base_config import ExperimentConfig
from trading.core.base_strategy import BaseStrategy
from trading.core.execution_backtester import ExecutionModelBacktester


class ExecutionModelStrategy(BaseStrategy):
    """
    成交模型策略基礎類別

    子類需實作 create_config() 和 create_detector()。
    覆寫 create_backtester() 回傳 ExecutionModelBacktester。
    """

    # 子類可覆寫滑價設定 (Subclass may override slippage)
    slippage_pct: float = 0.001  # 0.1%

    def create_backtester(self, config: ExperimentConfig) -> ExecutionModelBacktester:
        return ExecutionModelBacktester(config, slippage_pct=self.slippage_pct)

    def _print_part_report(
        self, label: str, start: str, end: str, result: dict,
        df: pd.DataFrame, config: ExperimentConfig
    ) -> None:
        """覆寫以顯示成交模型資訊 (Override to show execution model info)"""
        separator = "=" * 80
        thin_sep = "-" * 80

        print(f"\n{separator}")
        print(f"  {label}: {start} ~ {end}")
        print(f"  資料筆數: {len(df)} 個交易日")
        print(f"{separator}")

        # 策略參數（只在第一個 Part 印）
        if "Part A" in label:
            print(f"\n{thin_sep}")
            print("  策略參數 (Strategy Parameters)")
            print(f"{thin_sep}")
            self._print_strategy_params(config)

            # 成交模型參數 (Execution model parameters)
            print(f"\n{thin_sep}")
            print("  成交模型 (Execution Model)")
            print(f"{thin_sep}")
            self._print_execution_model_params(result)

        trades = result["trades"]

        if not trades:
            unfilled = result.get("unfilled_count", 0)
            if unfilled > 0:
                print(f"\n  無成交訊號，{unfilled} 個訊號未成交 "
                      f"(No filled trades, {unfilled} unfilled signals)\n")
            else:
                print("\n  無訊號觸發 (No signals detected)\n")
            return

        # 成交統計 (Fill statistics)
        print(f"\n{thin_sep}")
        print("  成交統計 (Fill Statistics)")
        print(f"{thin_sep}")
        filled = result.get("filled_count", result["total_signals"])
        unfilled = result.get("unfilled_count", 0)
        fill_rate = result.get("fill_rate", 1.0)
        print(f"  總訊號數 (Total signals):        {filled + unfilled}")
        print(f"  已成交 (Filled):                 {filled}")
        print(f"  未成交 (Unfilled):               {unfilled}")
        print(f"  成交率 (Fill rate):              {fill_rate:.1%}")

        # 彙總績效 (Aggregate performance)
        print(f"\n{thin_sep}")
        print("  回測績效摘要 (Backtest Performance Summary)")
        print(f"{thin_sep}")
        print(f"  已成交訊號數 (Filled signals):   {result['total_signals']}")
        print(f"  每年平均 (Avg per year):          {self._signals_per_year(trades, df):.1f}")
        print(f"  獲利次數 (Wins):                 {result['wins']}")
        print(f"  勝率 (Win rate):                 {result['win_rate']:.1%}")
        print(f"  平均報酬 (Avg return):           {result['avg_return_pct']:+.2f}%")
        print(f"  報酬標準差 (Std return):         {result['std_return_pct']:.2f}%")
        print(f"  累計報酬 (Cumulative return):    {result['cumulative_return_pct']:+.2f}%")
        print(f"  平均持倉 (Avg holding days):     {result['avg_holding_days']:.1f} 天")
        print(f"  最大單筆回撤 (Max drawdown):     {result['max_drawdown_pct']:.2f}%")
        print(f"  最大連續虧損 (Max consec. loss): {result['max_consecutive_losses']}")

        # 出場方式統計 (Exit type breakdown)
        print("\n  出場方式 (Exit breakdown):")
        print(f"    達標出場 (Target hit):         {result['target_exits']}")
        print(f"    停損出場 (Stop-loss):          {result['stop_loss_exits']}")
        pessimistic = result.get("pessimistic_exits", 0)
        if pessimistic > 0:
            print(f"    　含悲觀認定 (Pessimistic):    {pessimistic}")
        print(f"    到期出場 (Time expiry):        {result['time_expiry_exits']}")

        # 逐筆交易明細 (Trade details)
        print(f"\n{thin_sep}")
        print("  逐筆交易明細 (Trade Details)")
        print(f"{thin_sep}")
        print(f"  {'訊號日期':<12} {'進場日期':<12} {'出場日期':<12} {'進場':>8} {'出場':>8} {'報酬':>8} {'持倉':>4} {'出場方式':<16}")
        print(f"  {'Signal':<12} {'Entry':<12} {'Exit Date':<12} {'Entry':>8} {'Exit':>8} {'Return':>8} {'Days':>4} {'Exit Type':<16}")
        print(f"  {'-'*88}")

        exit_type_labels = {
            "target": "達標 Target",
            "stop_loss": "停損 Stop",
            "stop_loss_pessimistic": "停損悲觀 Pessim.",
            "time_expiry": "到期 Expiry",
            "no_data": "無資料 N/A",
        }

        for t in trades:
            label_t = exit_type_labels.get(t["exit_type"], t["exit_type"])
            entry_date = t.get("entry_date", t["date"])
            print(
                f"  {t['date']:<12} "
                f"{entry_date:<12} "
                f"{t['exit_date']:<12} "
                f"{t['entry']:>8.2f} "
                f"{t['exit']:>8.2f} "
                f"{t['return_pct']:>+7.2f}% "
                f"{t['holding_days']:>4d} "
                f"{label_t:<16}"
            )

    def _print_execution_model_params(self, result: dict) -> None:
        """印出成交模型參數 (Print execution model parameters)"""
        em = result.get("execution_model", {})
        entry_labels = {
            "next_open_market": "隔日開盤市價 (Next Open Market)",
            "next_open_limit": "隔日開盤限價 (Next Open Limit)",
        }
        exit_profit_labels = {
            "limit_order_day": "限價賣單 Day (Limit Order Day)",
        }
        exit_stop_labels = {
            "stop_market_gtc": "停損市價 GTC (Stop Market GTC)",
            "stop_limit_gtc": "停損限價 GTC (Stop Limit GTC)",
        }
        exit_expiry_labels = {
            "next_open_market": "隔日開盤市價 (Next Open Market)",
        }

        entry_mode = em.get("entry_mode", "unknown")
        exit_profit = em.get("exit_profit", "unknown")
        exit_stop = em.get("exit_stop", "unknown")
        exit_expiry = em.get("exit_expiry", "unknown")
        slippage = em.get("slippage_pct", 0)
        pessimistic = em.get("pessimistic_execution", False)

        print(f"  進場模式 (Entry mode):           {entry_labels.get(entry_mode, entry_mode)}")
        print(f"  止盈委託 (Profit exit):          {exit_profit_labels.get(exit_profit, exit_profit)}")
        print(f"  停損委託 (Stop exit):            {exit_stop_labels.get(exit_stop, exit_stop)}")
        print(f"  到期出場 (Expiry exit):          {exit_expiry_labels.get(exit_expiry, exit_expiry)}")
        print(f"  滑價 (Slippage):                 {slippage:.2%}")
        print(f"  悲觀認定 (Pessimistic exec.):    {'是 Yes' if pessimistic else '否 No'}")
