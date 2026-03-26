"""
跟單訊號產生器 (Trading Followup Signal Generator)
套用各標的最佳策略，執行 60 天回測並產生 Firstrade 下單指令。
Runs best strategies per ticker with 60-day lookback and generates Firstrade order instructions.

使用情境 (Usage):
- 在 T-1 日美股收盤後執行
- 使用者於 T 日開盤前根據報告在 Firstrade 下單
- Run after T-1 US market close
- User places orders on Firstrade before T-day market open
"""

import logging
from datetime import datetime, timedelta

import pandas as pd

from trading.core.data_fetcher import DataFetcher
from trading.experiments import get_experiment

logger = logging.getLogger(__name__)

# 各標的最佳策略 (Best strategy per ticker)
STRATEGIES = [
    {
        "experiment_name": "tqqq_010_cap_exec_optimized",
        "label": "TQQQ-010",
        "ticker": "TQQQ",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "gld_003_trailing_stop",
        "label": "GLD-003",
        "ticker": "GLD",
        "has_trailing_stop": True,
    },
]

LOOKBACK_TRADING_DAYS = 60


def run_followup() -> None:
    """主入口：產生跟單訊號報告 (Main entry: generate followup signal report)"""
    today = pd.Timestamp.now().normalize()
    separator = "=" * 80

    print(f"\n{separator}")
    print(f"  TRADING FOLLOWUP REPORT — {today.strftime('%Y-%m-%d')}")
    print(f"  本報告於 T-1 日收盤後產生，請於 T 日開盤前下單")
    print(f"  This report is generated after T-1 close. Place orders before T-day open.")
    print(f"{separator}")

    for strategy_info in STRATEGIES:
        _run_single_strategy(strategy_info, today)

    print(f"\n{separator}")
    print(f"  報告結束 (End of Report)")
    print(f"  免責聲明: 本報告僅供參考，不構成投資建議。投資有風險，請自行判斷。")
    print(f"  Disclaimer: This report is for reference only, not investment advice.")
    print(f"{separator}\n")


def _run_single_strategy(strategy_info: dict, today: pd.Timestamp) -> None:
    """執行單一策略並輸出報告 (Run one strategy and print report)"""
    experiment_name = strategy_info["experiment_name"]
    label = strategy_info["label"]
    ticker = strategy_info["ticker"]
    has_trailing_stop = strategy_info["has_trailing_stop"]

    separator = "=" * 80
    thin_sep = "-" * 80

    print(f"\n{separator}")
    print(f"  {ticker} ({label}: {experiment_name})")
    print(f"{separator}")

    # 1. 取得策略元件 (Get strategy components)
    strategy = get_experiment(experiment_name)
    config = strategy.create_config()
    detector = strategy.create_detector()
    backtester = strategy.create_backtester(config)

    # 2. 抓取資料（往前抓 365 天確保指標暖身）
    # Fetch data (365 days back for indicator warm-up)
    data_start = (today - timedelta(days=365)).strftime("%Y-%m-%d")
    fetcher = DataFetcher(start=data_start)
    data = fetcher.fetch_all([ticker])

    if ticker not in data:
        print(f"\n  [ERROR] 無法取得 {ticker} 資料 (Failed to fetch {ticker} data)\n")
        return

    df = data[ticker]
    logger.info(f"Fetched {len(df)} rows for {ticker}")

    # 3. 計算指標 (Compute indicators on full data)
    df = detector.compute_indicators(df)

    # 4. 切出最近 60 個交易日 (Slice last 60 trading days)
    df_60 = df.iloc[-LOOKBACK_TRADING_DAYS:].copy()
    period_start = df_60.index[0].strftime("%Y-%m-%d")
    period_end = df_60.index[-1].strftime("%Y-%m-%d")

    # 5. 偵測訊號 + 回測 (Detect signals + backtest)
    df_60 = detector.detect_signals(df_60)
    result = backtester.run(df_60)

    # 6. 印出 60 天回測摘要 (Print 60-day backtest summary)
    print(f"\n{thin_sep}")
    print(f"  60-Day Backtest Summary")
    print(f"{thin_sep}")
    print(f"  期間 (Period): {period_start} ~ {period_end}")
    print(f"  訊號數 (Signals): {result['total_signals']}")
    if result["total_signals"] > 0:
        print(f"  勝率 (Win rate): {result['win_rate']:.1%}")
        print(f"  累計報酬 (Cumulative return): {result['cumulative_return_pct']:+.2f}%")
        print(f"  平均報酬 (Avg return): {result['avg_return_pct']:+.2f}%")

    # 7. 印出逐筆交易明細 (Print trade details)
    trades = result["trades"]
    if trades:
        print(f"\n{thin_sep}")
        print(f"  近 60 日交易明細 (Recent 60-Day Trade Details)")
        print(f"{thin_sep}")

        exit_type_labels = {
            "target": "達標 Target",
            "stop_loss": "停損 Stop",
            "stop_loss_pessimistic": "停損悲觀 Pessim.",
            "trailing_stop": "追蹤停損 Trail",
            "time_expiry": "到期 Expiry",
            "no_data": "無資料 N/A",
        }

        print(f"  {'訊號日':<12} {'進場日':<12} {'出場日':<12} {'進場':>8} {'出場':>8} {'報酬':>8} {'天數':>4} {'出場方式':<16}")
        print(f"  {'-' * 88}")
        for t in trades:
            entry_date = t.get("entry_date", t["date"])
            label_t = exit_type_labels.get(t["exit_type"], t["exit_type"])
            print(
                f"  {t['date']:<12} "
                f"{entry_date:<12} "
                f"{t.get('exit_date', 'N/A'):<12} "
                f"{t['entry']:>8.2f} "
                f"{t['exit']:>8.2f} "
                f"{t['return_pct']:>+7.2f}% "
                f"{t['holding_days']:>4d} "
                f"{label_t:<16}"
            )

    # 8. 檢查今日訊號 (Check today's signal)
    # 用完整資料重新偵測，確保最新一天的訊號狀態正確
    df_full_signals = detector.detect_signals(df.copy())
    latest_date = df_full_signals.index[-1]
    latest_close = float(df_full_signals.iloc[-1]["Close"])
    signal_today = bool(df_full_signals.loc[latest_date, "Signal"])

    print(f"\n{thin_sep}")
    print(f"  最新資料日期 (Latest data date): {latest_date.strftime('%Y-%m-%d')}")
    print(f"  {ticker} 收盤價 (Close): ${latest_close:.2f}")
    print(f"{thin_sep}")

    if signal_today:
        _print_buy_signal(ticker, config, latest_close, latest_date, has_trailing_stop)
    else:
        print(f"\n  ┌{'─' * 48}┐")
        print(f"  │  今日訊號: 無動作 NO ACTION{' ' * 20}│")
        print(f"  └{'─' * 48}┘")
        print(f"\n  {ticker} 於 {latest_date.strftime('%Y-%m-%d')} 無買入訊號")
        print(f"  No buy signal for {ticker} on {latest_date.strftime('%Y-%m-%d')}.")

    # 9. 未結部位 (Open positions)
    _print_open_positions(trades, config, today, ticker, has_trailing_stop, df_full_signals)


def _print_buy_signal(
    ticker: str,
    config,
    last_close: float,
    signal_date: pd.Timestamp,
    has_trailing_stop: bool,
) -> None:
    """印出買入訊號與 Firstrade 下單指令"""
    slippage = 0.001  # 0.1%
    estimated_entry = last_close * (1 + slippage)
    target_price = estimated_entry * (1 + config.profit_target)
    stop_price = estimated_entry * (1 + config.stop_loss)

    # 預估到期日（大約 holding_days 個交易日後）
    est_expiry = signal_date + timedelta(days=int(config.holding_days * 1.5))

    print(f"\n  ┌{'─' * 48}┐")
    print(f"  │  ★ 今日訊號: 買入 BUY TRIGGERED{' ' * 15}│")
    print(f"  └{'─' * 48}┘")

    print(f"\n  {'═' * 50}")
    print(f"  Firstrade 下單指令 (Order Instructions)")
    print(f"  {'═' * 50}")

    # 步驟 1: 買入
    print(f"\n  步驟 1: 開盤買入 (Step 1: Market Buy at Open)")
    print(f"  {'─' * 50}")
    print(f"    下單方式 (Order type): MARKET BUY (市價買入)")
    print(f"    標的 (Symbol):         {ticker}")
    print(f"    時機 (Timing):         T 日開盤前掛單 (Pre-market)")
    print(f"    預估成交價 (Est. fill): ~${estimated_entry:.2f}")
    print(f"      (T-1 收盤 ${last_close:.2f} + 0.1% 滑價)")

    # 步驟 2: 掛出止盈/停損委託
    print(f"\n  步驟 2: 成交後立即掛出委託 (Step 2: Place Exit Orders After Fill)")
    print(f"  {'─' * 50}")

    print(f"    (a) 止盈單 — LIMIT SELL (限價賣出)")
    print(f"        限價 (Limit price):  ${target_price:.2f} (+{config.profit_target:.1%} 獲利目標)")
    print(f"        有效期 (Duration):   Day Order (每日需重新掛單)")
    print(f"        Firstrade 操作:      Sell > Limit > 輸入 ${target_price:.2f} > Day")

    print(f"\n    (b) 停損單 — STOP SELL (停損市價賣出)")
    print(f"        觸發價 (Stop price): ${stop_price:.2f} ({config.stop_loss:.1%} 停損)")
    print(f"        有效期 (Duration):   GTC (Good Till Cancel)")
    print(f"        Firstrade 操作:      Sell > Stop > 輸入 ${stop_price:.2f} > GTC")

    if has_trailing_stop:
        # GLD-003 追蹤停損指令
        trail_activation = getattr(config, "trail_activation_pct", 0.015)
        trail_distance = getattr(config, "trail_distance_pct", 0.01)
        trail_activate_price = estimated_entry * (1 + trail_activation)

        print(f"\n  步驟 3: 追蹤停損 — 需每日手動調整 (Step 3: Manual Trailing Stop)")
        print(f"  {'─' * 50}")
        print(f"    啟動條件 (Activation):   最高價達 ${trail_activate_price:.2f}")
        print(f"                            (進場價 +{trail_activation:.1%})")
        print(f"    追蹤方式 (Trail method): 新停損 = 最高價 × (1 - {trail_distance:.1%})")
        print(f"    操作方式 (How to):")
        print(f"      1. 每日收盤後檢查 {ticker} 最高價")
        print(f"      2. 若最高價 >= ${trail_activate_price:.2f}，計算新停損價:")
        print(f"         新停損 = 當日最高價 × {1 - trail_distance:.4f}")
        print(f"      3. 若新停損 > 現有停損，登入 Firstrade 修改 STOP SELL 價格")
        print(f"      4. 停損價只能上調，不可下調")
        print(f"    注意: Firstrade 不支援自動追蹤停損，必須手動調整")
        print(f"    Note: Firstrade does not support auto trailing stops.")

        step_num = 4
    else:
        step_num = 3

    # 持倉管理
    print(f"\n  步驟 {step_num}: 持倉管理 (Step {step_num}: Position Management)")
    print(f"  {'─' * 50}")
    print(f"    最長持倉 (Max holding):  {config.holding_days} 個交易日")
    print(f"    預估到期日 (Est. expiry): ~{est_expiry.strftime('%Y-%m-%d')}")
    print(f"    到期處理 (On expiry):")
    print(f"      1. 取消所有未成交委託 (Cancel all open orders)")
    print(f"      2. 下一交易日開盤掛 MARKET SELL (市價賣出)")
    print(f"         Firstrade: Sell > Market > Day")

    # 重要提醒
    print(f"\n  ⚠ 重要提醒 (Important Notes)")
    print(f"  {'─' * 50}")
    print(f"    • 上述價格為預估值，實際成交價以 Firstrade 回報為準")
    print(f"    • 請依實際成交價重新計算目標價與停損價:")
    print(f"      目標價 = 成交價 × {1 + config.profit_target:.4f}")
    print(f"      停損價 = 成交價 × {1 + config.stop_loss:.4f}")
    print(f"    • Prices above are estimates. Recalculate based on actual fill price.")


def _print_open_positions(
    trades: list[dict],
    config,
    today: pd.Timestamp,
    ticker: str,
    has_trailing_stop: bool,
    df: pd.DataFrame,
) -> None:
    """印出未結部位 (Print open positions from recent trades)"""
    thin_sep = "-" * 80

    print(f"\n{thin_sep}")
    print(f"  未結部位 (Open Positions) — {ticker}")
    print(f"{thin_sep}")

    if not trades:
        print(f"  無未結部位 (No open positions)\n")
        return

    # 找出仍在持倉期內的交易
    # 判斷方式: exit_date >= today 表示該交易在現實中可能尚未結束
    today_str = today.strftime("%Y-%m-%d")
    open_positions = []

    for t in trades:
        exit_date_str = t.get("exit_date", "")
        entry_date_str = t.get("entry_date", t["date"])

        # 如果出場日期 >= 今日，該部位可能仍然開放
        if exit_date_str >= today_str:
            open_positions.append(t)

    if not open_positions:
        print(f"  無未結部位 (No open positions)\n")
        return

    for pos in open_positions:
        entry_date = pos.get("entry_date", pos["date"])
        entry_price = pos["entry"]
        target_price = entry_price * (1 + config.profit_target)
        stop_price = entry_price * (1 + config.stop_loss)

        # 計算已持倉天數（從 entry_date 到 today 的交易日數）
        try:
            entry_ts = pd.Timestamp(entry_date)
            trading_days_held = len(df.loc[entry_ts:today]) - 1
        except Exception:
            trading_days_held = pos["holding_days"]

        days_remaining = max(0, config.holding_days - trading_days_held)

        print(f"\n  部位 (Position):")
        print(f"    進場日期 (Entry date):   {entry_date}")
        print(f"    進場價格 (Entry price):  ${entry_price:.2f}")
        print(f"    目標價 (Target):         ${target_price:.2f} (+{config.profit_target:.1%})")
        print(f"    停損價 (Stop):           ${stop_price:.2f} ({config.stop_loss:.1%})")
        print(f"    已持倉 (Days held):      {trading_days_held} 交易日")
        print(f"    剩餘天數 (Remaining):    {days_remaining} 交易日")

        if has_trailing_stop:
            trail_activation = getattr(config, "trail_activation_pct", 0.015)
            trail_distance = getattr(config, "trail_distance_pct", 0.01)
            activate_price = entry_price * (1 + trail_activation)

            # 計算持倉期間最高價
            try:
                entry_ts = pd.Timestamp(entry_date)
                hold_df = df.loc[entry_ts:today]
                if not hold_df.empty:
                    highest = float(hold_df["High"].max())
                    unrealized_gain = (highest - entry_price) / entry_price
                    trail_activated = unrealized_gain >= trail_activation

                    print(f"    持倉最高價 (Highest):    ${highest:.2f}")
                    print(f"    追蹤停損啟動 (Trailing):  {'是 YES' if trail_activated else '否 NO'}")

                    if trail_activated:
                        current_trail_stop = highest * (1 - trail_distance)
                        effective_stop = max(stop_price, current_trail_stop)
                        print(f"    當前追蹤停損 (Trail stop): ${effective_stop:.2f}")
                        print(f"    → 請更新 Firstrade STOP SELL 至 ${effective_stop:.2f}")
            except Exception:
                pass

        if days_remaining == 0:
            print(f"\n    ⚠ 持倉已到期！請於下一交易日開盤賣出")
            print(f"    ⚠ Holding period expired! Sell at next market open.")
            print(f"    → 取消所有委託，掛 MARKET SELL")

    print()
