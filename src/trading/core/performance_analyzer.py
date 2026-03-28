"""
滾動窗口績效分析器 (Rolling Window Performance Analyzer)
用於驗證「績效漸變」假說：同一標的同一策略的績效變化是漸進還是突變。
Validates the "gradual performance change" hypothesis by analyzing strategy
performance across rolling time windows.
"""

import logging

import numpy as np
import pandas as pd

from trading.core.base_strategy import BaseStrategy
from trading.core.data_fetcher import DataFetcher

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """滾動窗口績效分析器"""

    def __init__(self, strategy: BaseStrategy, window_years: int = 2, step_months: int = 6):
        self.strategy = strategy
        self.window_years = window_years
        self.step_months = step_months

    def run(self) -> None:
        """執行滾動窗口分析並印出結果"""
        config = self.strategy.create_config()
        detector = self.strategy.create_detector()
        backtester = self.strategy.create_backtester(config)
        fetcher = DataFetcher(start=config.data_start)

        separator = "=" * 90

        print(f"\n{separator}")
        print("  滾動窗口績效分析 (Rolling Window Performance Analysis)")
        print(f"  {config.display_name}")
        print(f"  窗口: {self.window_years} 年, 步進: {self.step_months} 個月")
        print(f"{separator}\n")

        # Step 1: Fetch data
        data = fetcher.fetch_all(config.tickers)
        primary_ticker = config.tickers[0]
        if primary_ticker not in data:
            logger.error(f"無法取得 {primary_ticker} 數據")
            return

        df = data[primary_ticker]

        # Step 2: Compute indicators on full dataset (once)
        df = detector.compute_indicators(df)

        # Step 3: Generate rolling windows
        data_start = pd.Timestamp(config.part_a_start)
        data_end = df.index[-1]
        windows = self._generate_windows(data_start, data_end)

        if len(windows) < 2:
            print("  窗口數不足，無法進行分析。請縮小窗口或步進。")
            return

        # Step 4: Backtest each window
        window_results = []
        for win_start, win_end in windows:
            start_str = win_start.strftime("%Y-%m-%d")
            end_str = win_end.strftime("%Y-%m-%d")
            df_win = df.loc[start_str:end_str].copy()

            if df_win.empty:
                continue

            df_win = detector.detect_signals(df_win)
            result = backtester.run(df_win)
            window_results.append(
                {
                    "start": win_start,
                    "end": win_end,
                    "label": f"{win_start.strftime('%Y-%m')}~{win_end.strftime('%Y-%m')}",
                    **result,
                }
            )

        if len(window_results) < 2:
            print("  有效窗口數不足，無法進行分析。")
            return

        # Step 5: Print rolling table
        self._print_rolling_table(window_results)

        # Step 6: Print gradual assessment
        self._print_gradual_assessment(window_results)

    def _generate_windows(
        self, data_start: pd.Timestamp, data_end: pd.Timestamp
    ) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
        """產生滾動窗口列表"""
        windows = []
        window_delta = pd.DateOffset(years=self.window_years)
        step_delta = pd.DateOffset(months=self.step_months)

        current_start = data_start
        while True:
            current_end = current_start + window_delta - pd.Timedelta(days=1)
            if current_end > data_end:
                # 最後一個窗口截到資料結尾（若剩餘期間 >= 窗口的一半則納入）
                remaining = (data_end - current_start).days
                half_window = window_delta.n * 365 // 2 if hasattr(window_delta, "n") else 365
                if remaining >= half_window:
                    windows.append((current_start, data_end))
                break
            windows.append((current_start, current_end))
            current_start = current_start + step_delta
        return windows

    def _print_rolling_table(self, results: list[dict]) -> None:
        """印出滾動窗口績效表"""
        separator = "=" * 90
        thin_sep = "-" * 90

        print(f"{separator}")
        print("  滾動窗口績效表 (Rolling Window Performance)")
        print(f"{separator}")
        print(
            f"  {'窗口 (Window)':<22} {'訊號':>6} {'勝率':>8} {'平均報酬':>10} "
            f"{'累計報酬':>10} {'MDD':>8} {'ΔWR':>8}"
        )
        print(f"  {thin_sep}")

        prev_wr = None
        for r in results:
            wr = r["win_rate"]
            signals = r["total_signals"]
            avg_ret = r["avg_return_pct"]
            cum_ret = r["cumulative_return_pct"]
            mdd = r["max_drawdown_pct"]

            if prev_wr is not None and signals > 0:
                delta_wr = (wr - prev_wr) * 100  # percentage points
                delta_str = f"{delta_wr:+.1f}pp"
            else:
                delta_str = "—"

            wr_str = f"{wr:.1%}" if signals > 0 else "N/A"
            avg_str = f"{avg_ret:+.2f}%" if signals > 0 else "N/A"
            cum_str = f"{cum_ret:+.2f}%" if signals > 0 else "N/A"
            mdd_str = f"{mdd:.2f}%" if signals > 0 else "N/A"

            print(
                f"  {r['label']:<22} {signals:>6} {wr_str:>8} {avg_str:>10} "
                f"{cum_str:>10} {mdd_str:>8} {delta_str:>8}"
            )

            if signals > 0:
                prev_wr = wr

        print()

    def _print_gradual_assessment(self, results: list[dict]) -> None:
        """印出漸變性評估"""
        separator = "=" * 90
        thin_sep = "-" * 90

        # Collect win rates from windows with enough signals
        win_rates = []
        cum_returns = []
        for r in results:
            if r["total_signals"] >= 2:  # 至少 2 個訊號才有意義
                win_rates.append(r["win_rate"])
                cum_returns.append(r["cumulative_return_pct"])

        if len(win_rates) < 3:
            print("  有效窗口不足 3 個，無法評估漸變性。")
            return

        # Calculate deltas
        wr_deltas = [win_rates[i] - win_rates[i - 1] for i in range(1, len(win_rates))]
        cum_deltas = [cum_returns[i] - cum_returns[i - 1] for i in range(1, len(cum_returns))]

        wr_delta_std = float(np.std(wr_deltas))
        cum_delta_std = float(np.std(cum_deltas))
        max_wr_jump = max(abs(d) for d in wr_deltas)
        max_cum_jump = max(abs(d) for d in cum_deltas)

        print(f"{separator}")
        print("  漸變性評估 (Gradual Change Assessment)")
        print(f"{separator}")
        print(f"  有效窗口數:                        {len(win_rates)}")
        print(f"  勝率範圍:                          {min(win_rates):.1%} ~ {max(win_rates):.1%}")
        print(
            f"  累計報酬範圍:                      {min(cum_returns):+.2f}% ~ {max(cum_returns):+.2f}%"
        )

        print(f"\n{thin_sep}")
        print("  勝率變化 (Win Rate Changes)")
        print(f"{thin_sep}")
        print(f"  ΔWR 平均:                          {np.mean(wr_deltas) * 100:+.1f}pp")
        print(f"  ΔWR 標準差:                        {wr_delta_std * 100:.1f}pp")
        print(f"  ΔWR 最大跳動:                      {max_wr_jump * 100:.1f}pp")

        print(f"\n{thin_sep}")
        print("  累計報酬變化 (Cumulative Return Changes)")
        print(f"{thin_sep}")
        print(f"  ΔCum 平均:                         {np.mean(cum_deltas):+.2f}%")
        print(f"  ΔCum 標準差:                       {cum_delta_std:.2f}%")
        print(f"  ΔCum 最大跳動:                     {max_cum_jump:.2f}%")

        # Verdict
        print(f"\n{thin_sep}")
        print("  判定 (Verdict)")
        print(f"{thin_sep}")

        # Heuristic: if max jump > 2x std, there's a structural break
        wr_gradual = max_wr_jump <= 0.20  # 最大跳動 ≤ 20pp
        cum_gradual = max_cum_jump <= cum_delta_std * 3 if cum_delta_std > 0 else True

        if wr_gradual and cum_gradual:
            print("  ✓ 績效變化呈漸進趨勢 (Performance changes are GRADUAL)")
            print(f"    勝率最大跳動 {max_wr_jump * 100:.1f}pp 在合理範圍內")
        elif not wr_gradual:
            print("  ✗ 存在突變：勝率出現大幅跳動 (ABRUPT change detected in win rate)")
            print(f"    最大跳動 {max_wr_jump * 100:.1f}pp 超過 20pp 閾值")
            # Find which window had the jump
            for i, d in enumerate(wr_deltas):
                if abs(d) == max_wr_jump:
                    print(f"    發生在窗口 {i + 1} → {i + 2} 之間")
                    break
        else:
            print("  △ 累計報酬有較大波動，但勝率相對穩定 (Mixed: return volatile, WR stable)")
            print(f"    累計報酬最大跳動 {max_cum_jump:.2f}% (ΔCum std: {cum_delta_std:.2f}%)")

        print()
