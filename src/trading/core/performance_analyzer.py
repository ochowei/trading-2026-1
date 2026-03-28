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

        # Step 5: Print rolling performance table
        self._print_rolling_table(window_results)

        # Step 6: Print prediction accuracy table
        self._print_prediction_accuracy_table(window_results)

        # Step 7: Print gradual assessment (prediction accuracy focused)
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

    @staticmethod
    def _compute_accuracy_metrics(trades: list[dict]) -> dict:
        """從交易列表計算預測精準度指標"""
        if not trades:
            return {
                "win_rate": 0.0,
                "avg_win_ret": 0.0,
                "avg_loss_ret": 0.0,
                "profit_factor": 0.0,
                "near_miss_ratio": 0.0,
                "near_miss_count": 0,
                "time_expiry_count": 0,
            }

        returns = [t["return_pct"] for t in trades]
        wins = [r for r in returns if r > 0]
        losses = [r for r in returns if r <= 0]
        avg_win = float(np.mean(wins)) if wins else 0.0
        avg_loss = float(np.mean(losses)) if losses else 0.0

        # Profit factor = gross profit / gross loss
        gross_profit = sum(wins) if wins else 0.0
        gross_loss = abs(sum(losses)) if losses else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

        # Near misses: time_expiry exits with positive return (direction correct, magnitude insufficient)
        time_expiry_trades = [t for t in trades if t["exit_type"] == "time_expiry"]
        near_misses = [t for t in time_expiry_trades if t["return_pct"] > 0]
        near_miss_ratio = len(near_misses) / len(trades) if trades else 0.0

        return {
            "win_rate": len(wins) / len(trades) if trades else 0.0,
            "avg_win_ret": round(avg_win, 2),
            "avg_loss_ret": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float("inf") else 999.0,
            "near_miss_ratio": round(near_miss_ratio, 4),
            "near_miss_count": len(near_misses),
            "time_expiry_count": len(time_expiry_trades),
        }

    def _print_prediction_accuracy_table(self, results: list[dict]) -> None:
        """印出預測精準度表"""
        separator = "=" * 100
        thin_sep = "-" * 100

        print(f"{separator}")
        print("  預測精準度表 (Prediction Accuracy)")
        print(f"{separator}")
        print(
            f"  {'窗口 (Window)':<22} {'WR':>7} {'平均贏':>8} {'平均虧':>8} "
            f"{'盈虧比':>7} {'差點成功':>8} {'ΔPF':>8}"
        )
        print(f"  {thin_sep}")

        prev_pf = None
        for r in results:
            trades = r["trades"]
            signals = r["total_signals"]
            m = self._compute_accuracy_metrics(trades)

            wr_str = f"{m['win_rate']:.1%}" if signals > 0 else "N/A"
            avg_w = f"{m['avg_win_ret']:+.2f}%" if signals > 0 and m["avg_win_ret"] else "N/A"
            avg_l = f"{m['avg_loss_ret']:+.2f}%" if signals > 0 and m["avg_loss_ret"] else "N/A"

            if signals > 0 and m["profit_factor"] >= 999:
                pf_str = "∞"
            elif signals > 0:
                pf_str = f"{m['profit_factor']:.2f}"
            else:
                pf_str = "N/A"

            # Near miss = direction correct (到期出場但正報酬)
            if signals > 0 and m["time_expiry_count"] > 0:
                nm_str = f"{m['near_miss_count']}/{m['time_expiry_count']}"
            elif signals > 0:
                nm_str = "—"
            else:
                nm_str = "N/A"

            # Delta profit factor
            if prev_pf is not None and signals > 0 and m["profit_factor"] < 999:
                delta_pf = m["profit_factor"] - prev_pf
                dpf_str = f"{delta_pf:+.2f}"
            else:
                dpf_str = "—"

            print(
                f"  {r['label']:<22} {wr_str:>7} {avg_w:>8} {avg_l:>8} "
                f"{pf_str:>7} {nm_str:>8} {dpf_str:>8}"
            )

            if signals > 0 and m["profit_factor"] < 999:
                prev_pf = m["profit_factor"]

        print()
        print("  說明: 盈虧比(PF) = 總獲利/總虧損, 差點成功 = 到期出場中正報酬筆數/到期出場總數")
        print("        差點成功 = 策略方向正確但未達 TP — 若比例高，可考慮降低 TP 或延長持倉")
        print()

    def _print_gradual_assessment(self, results: list[dict]) -> None:
        """印出漸變性評估（以預測精準度為核心）"""
        separator = "=" * 100
        thin_sep = "-" * 100

        # Collect metrics from windows with enough signals
        win_rates = []
        profit_factors = []
        cum_returns = []
        avg_win_rets = []
        avg_loss_rets = []
        for r in results:
            if r["total_signals"] >= 2:  # 至少 2 個訊號才有意義
                m = self._compute_accuracy_metrics(r["trades"])
                win_rates.append(r["win_rate"])
                cum_returns.append(r["cumulative_return_pct"])
                avg_win_rets.append(m["avg_win_ret"])
                avg_loss_rets.append(m["avg_loss_ret"])
                if m["profit_factor"] < 999:
                    profit_factors.append(m["profit_factor"])

        if len(win_rates) < 3:
            print("  有效窗口不足 3 個，無法評估漸變性。")
            return

        # Calculate deltas
        wr_deltas = [win_rates[i] - win_rates[i - 1] for i in range(1, len(win_rates))]
        cum_deltas = [cum_returns[i] - cum_returns[i - 1] for i in range(1, len(cum_returns))]
        pf_deltas = (
            [profit_factors[i] - profit_factors[i - 1] for i in range(1, len(profit_factors))]
            if len(profit_factors) >= 2
            else []
        )
        avg_win_deltas = [
            avg_win_rets[i] - avg_win_rets[i - 1] for i in range(1, len(avg_win_rets))
        ]

        wr_delta_std = float(np.std(wr_deltas))
        cum_delta_std = float(np.std(cum_deltas))
        max_wr_jump = max(abs(d) for d in wr_deltas)
        max_cum_jump = max(abs(d) for d in cum_deltas)

        print(f"{separator}")
        print("  漸變性評估 (Gradual Change Assessment)")
        print(f"{separator}")
        print(f"  有效窗口數:                        {len(win_rates)}")

        # --- 預測精準度 (Prediction Accuracy) ---
        print(f"\n{thin_sep}")
        print("  A. 預測精準度 — 策略看對方向的能力 (Prediction Accuracy)")
        print(f"{thin_sep}")
        print(f"  勝率範圍:                          {min(win_rates):.1%} ~ {max(win_rates):.1%}")
        print(f"  ΔWR 平均:                          {np.mean(wr_deltas) * 100:+.1f}pp")
        print(f"  ΔWR 標準差:                        {wr_delta_std * 100:.1f}pp")
        print(f"  ΔWR 最大跳動:                      {max_wr_jump * 100:.1f}pp")

        if pf_deltas:
            pf_delta_std = float(np.std(pf_deltas))
            max_pf_jump = max(abs(d) for d in pf_deltas)
            print(
                f"\n  盈虧比範圍:                        {min(profit_factors):.2f} ~ {max(profit_factors):.2f}"
            )
            print(f"  ΔPF 標準差:                        {pf_delta_std:.2f}")
            print(f"  ΔPF 最大跳動:                      {max_pf_jump:.2f}")

        # --- 市場報酬空間 (Market Reward Space) ---
        print(f"\n{thin_sep}")
        print("  B. 市場報酬空間 — 看對時能賺多少 (Market Reward Space)")
        print(f"{thin_sep}")
        print(
            f"  平均贏利範圍:                      {min(avg_win_rets):+.2f}% ~ {max(avg_win_rets):+.2f}%"
        )
        avg_win_delta_std = float(np.std(avg_win_deltas))
        max_avg_win_jump = max(abs(d) for d in avg_win_deltas)
        print(f"  Δ平均贏利 標準差:                  {avg_win_delta_std:.2f}%")
        print(f"  Δ平均贏利 最大跳動:                {max_avg_win_jump:.2f}%")

        # --- 下游績效 (Downstream Performance) ---
        print(f"\n{thin_sep}")
        print("  C. 下游績效 — 受出場/波動/極端值影響 (Downstream Performance)")
        print(f"{thin_sep}")
        print(
            f"  累計報酬範圍:                      {min(cum_returns):+.2f}% ~ {max(cum_returns):+.2f}%"
        )
        print(f"  ΔCum 標準差:                       {cum_delta_std:.2f}%")
        print(f"  ΔCum 最大跳動:                     {max_cum_jump:.2f}%")

        # === Verdict ===
        print(f"\n{thin_sep}")
        print("  判定 (Verdict)")
        print(f"{thin_sep}")

        wr_gradual = max_wr_jump <= 0.20  # 最大跳動 ≤ 20pp
        cum_gradual = max_cum_jump <= cum_delta_std * 3 if cum_delta_std > 0 else True

        # Determine if accuracy is gradual vs performance is gradual
        if wr_gradual:
            print("  ✓ 預測精準度漸變 (Prediction accuracy changes GRADUALLY)")
            print(f"    勝率最大跳動 {max_wr_jump * 100:.1f}pp ≤ 20pp 閾值")
        else:
            print("  ✗ 預測精準度突變 (Prediction accuracy changes ABRUPTLY)")
            print(f"    勝率最大跳動 {max_wr_jump * 100:.1f}pp > 20pp 閾值")
            for i, d in enumerate(wr_deltas):
                if abs(d) == max_wr_jump:
                    print(f"    發生在窗口 {i + 1} → {i + 2} 之間")
                    break

        if cum_gradual:
            print("  ✓ 下游績效漸變 (Downstream performance changes GRADUALLY)")
        else:
            print("  ✗ 下游績效突變 (Downstream performance changes ABRUPTLY)")
            print(f"    累計報酬最大跳動 {max_cum_jump:.2f}%")

        # Cross-diagnosis: accuracy stable but performance volatile = exit/volatility issue
        if wr_gradual and not cum_gradual:
            print("\n  診斷: 精準度穩定但績效波動 → 問題在出場參數或波動度變化，非策略本身")
            print(
                "  (Diagnosis: Accuracy stable but returns volatile → exit params or volatility issue)"
            )
        elif not wr_gradual and cum_gradual:
            print("\n  診斷: 精準度波動但績效穩定 → 勝/虧報酬互補抵消了精準度變化")
            print("  (Diagnosis: Accuracy volatile but returns stable → win/loss sizes compensate)")

        print()
