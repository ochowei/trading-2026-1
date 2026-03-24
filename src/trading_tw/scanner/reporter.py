"""
報表輸出模組 (Reporter Module)
格式化回測結果並輸出摘要報表。
Formats backtest results and prints summary reports.
"""

import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


class Reporter:
    """
    報表產生器 (Report Generator)
    將回測結果整理為 DataFrame 摘要，並標註今日訊號。
    Generates summary DataFrame from backtest results and highlights today's signals.
    """

    @staticmethod
    def generate_summary(results: list[dict]) -> pd.DataFrame:
        """
        產生摘要 DataFrame (Generate summary DataFrame)

        Args:
            results: 各標的的回測結果清單 (List of backtest result dicts)

        Returns:
            Formatted summary DataFrame
        """
        if not results:
            return pd.DataFrame()

        summary = pd.DataFrame(results)

        # 選擇並重新命名欄位 (Select and rename columns)
        display_cols = {
            "ticker": "Ticker",
            "type": "Type",
            "total_signals": "Signals",
            "wins": "Wins",
            "win_rate": "Win Rate",
            "avg_holding_days": "Avg Hold (days)",
            "max_drawdown_pct": "Max DD (%)",
            "avg_return_pct": "Avg Return (%)",
        }

        summary = summary[list(display_cols.keys())].rename(columns=display_cols)

        # 格式化勝率為百分比字串 (Format win rate as percentage)
        summary["Win Rate"] = summary["Win Rate"].apply(lambda x: f"{x:.1%}")

        # 依訊號數降序排列 (Sort by signal count descending)
        summary = summary.sort_values("Signals", ascending=False).reset_index(drop=True)

        return summary

    @staticmethod
    def check_today_signals(
        all_data: dict[str, pd.DataFrame],
    ) -> list[str]:
        """
        檢查今日是否有觸發訊號的標的 (Check for today's signals)

        Args:
            all_data: dict mapping ticker -> DataFrame with 'Signal' column

        Returns:
            List of tickers with signal on the latest available date
        """
        today_signals: list[str] = []
        today = pd.Timestamp(datetime.now().strftime("%Y-%m-%d"))

        for ticker, df in all_data.items():
            if df.empty or "Signal" not in df.columns:
                continue

            # 檢查最新一筆資料日期 (Check latest data date)
            latest_date = df.index[-1]

            # 若最新資料為今天且有訊號 (If latest data is today and has signal)
            if latest_date >= today and df.loc[latest_date, "Signal"]:
                today_signals.append(ticker)

        return today_signals

    @staticmethod
    def print_report(
        summary_df: pd.DataFrame,
        today_signals: list[str],
        results: list[dict],
    ) -> None:
        """
        列印完整報表 (Print full report)

        Args:
            summary_df: 摘要 DataFrame
            today_signals: 今日訊號標的清單
            results: 原始回測結果 (含訊號日期)
        """
        separator = "=" * 80

        print(f"\n{separator}")
        print("  美股均值回歸訊號掃描器 — 回測報告")
        print("  US Stock Mean-Reversion Signal Scanner — Backtest Report")
        print(f"{separator}\n")

        if summary_df.empty:
            print("  無任何回測結果 (No backtest results available)\n")
            return

        # 列印摘要表格 (Print summary table)
        print(summary_df.to_string(index=False))

        # 列印各標的的訊號觸發日期 (Print signal dates per ticker)
        print(f"\n{'-' * 80}")
        print("  訊號觸發日期明細 (Signal Date Details)")
        print(f"{'-' * 80}")

        for r in results:
            if r["total_signals"] > 0:
                dates_str = ", ".join(r["signal_dates"][-10:])  # 最近 10 筆
                suffix = f" ... (共 {r['total_signals']} 筆)" if r["total_signals"] > 10 else ""
                print(f"  {r['ticker']:6s}: {dates_str}{suffix}")

        # 今日訊號提示 (Today's signal alert)
        print(f"\n{separator}")
        if today_signals:
            print("  *** 今日訊號 (TODAY'S SIGNALS) ***")
            for t in today_signals:
                asset_type = "ETF" if any(r["type"] == "ETF" for r in results if r["ticker"] == t) else "Stock"
                print(f"  >>> {t} ({asset_type}) — 符合所有進場條件！(All entry conditions met!)")
        else:
            print("  今日無觸發訊號 (No signals triggered today)")
        print(f"{separator}\n")
