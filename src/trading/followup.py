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
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from io import StringIO
from zoneinfo import ZoneInfo

import pandas as pd

from trading.core.data_fetcher import DataFetcher
from trading.experiments import get_experiment

logger = logging.getLogger(__name__)

# 各標的最佳策略 (Best strategy per ticker)
STRATEGIES = [
    {
        "experiment_name": "copx_001_pullback_wr",
        "label": "COPX-001",
        "ticker": "COPX",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "dia_003_rsi2_bb",
        "label": "DIA-003",
        "ticker": "DIA",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "fcx_001_extreme_oversold",
        "label": "FCX-001",
        "ticker": "FCX",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "gld_006_pullback_wr",
        "label": "GLD-006",
        "ticker": "GLD",
        "has_trailing_stop": True,
    },
    {
        "experiment_name": "iwm_001_rsi2_reversal",
        "label": "IWM-001",
        "ticker": "IWM",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "nvda_001_extreme_oversold",
        "label": "NVDA-001",
        "ticker": "NVDA",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "sivr_006_closepos_pullback_wr",
        "label": "SIVR-006",
        "ticker": "SIVR",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "soxl_005_capped_drawdown",
        "label": "SOXL-005",
        "ticker": "SOXL",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "spy_004_rsi2_reversal",
        "label": "SPY-004",
        "ticker": "SPY",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "tqqq_012_cap_exec_qqq_confirm",
        "label": "TQQQ-012",
        "ticker": "TQQQ",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "tsm_002_pullback_wr_reversal",
        "label": "TSM-002",
        "ticker": "TSM",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "ura_001_pullback_wr",
        "label": "URA-001",
        "ticker": "URA",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "uso_009_momentum_pullback",
        "label": "USO-009",
        "ticker": "USO",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "voo_002_asymmetric_exit",
        "label": "VOO-002",
        "ticker": "VOO",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "xbi_001_pullback_wr",
        "label": "XBI-001",
        "ticker": "XBI",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "xlu_001_pullback_wr_reversal",
        "label": "XLU-001",
        "ticker": "XLU",
        "has_trailing_stop": False,
    },
]

LOOKBACK_TRADING_DAYS = 60

_NY_TZ = ZoneInfo("America/New_York")


def _drop_incomplete_bar(df: pd.DataFrame) -> pd.DataFrame:
    """若最後一根 bar 為盤中未收盤的當日資料，則丟棄。

    判斷條件：最後 bar 日期 == 美東今天 且 美東時間尚未過 16:30（收盤後 30 分鐘緩衝）。
    使用 America/New_York 時區，自動處理 EST/EDT 日光節約切換。
    """
    if df.empty:
        return df

    now_et = datetime.now(_NY_TZ)
    today_et = now_et.date()
    last_bar_date = df.index[-1].date()

    market_closed = now_et.hour > 16 or (now_et.hour == 16 and now_et.minute >= 30)

    if last_bar_date == today_et and not market_closed:
        logger.info(
            f"[Followup] 丟棄盤中未收盤資料 {last_bar_date} "
            f"(Dropping incomplete bar, market still open at {now_et.strftime('%H:%M ET')})"
        )
        return df.iloc[:-1]

    return df


def run_followup() -> None:
    """主入口：產生跟單訊號報告 (Main entry: generate followup signal report)"""
    today = pd.Timestamp.now().normalize()
    separator = "=" * 80

    print(f"\n{separator}")
    print(f"  TRADING FOLLOWUP REPORT — {today.strftime('%Y-%m-%d')}")
    print("  本報告於 T-1 日收盤後產生，請於 T 日開盤前下單")
    print("  This report is generated after T-1 close. Place orders before T-day open.")
    print(f"{separator}")

    # 先執行策略並收集各段輸出，讓下單清單可置頂顯示
    strategy_sections: list[str] = []
    all_orders: list[dict] = []

    for strategy_info in STRATEGIES:
        section_buffer = StringIO()
        with redirect_stdout(section_buffer):
            orders = _run_single_strategy(strategy_info, today)
        strategy_sections.append(section_buffer.getvalue())
        all_orders.extend(orders)

    # 印出 T 日下單清單 (Print consolidated T-day order sheet)
    _print_order_sheet(all_orders, today)
    for section in strategy_sections:
        print(section, end="")

    print(f"\n{separator}")
    print("  報告結束 (End of Report)")
    print("  免責聲明: 本報告僅供參考，不構成投資建議。投資有風險，請自行判斷。")
    print("  Disclaimer: This report is for reference only, not investment advice.")
    print(f"{separator}\n")


def _estimate_next_trading_day(last_data_date: pd.Timestamp) -> pd.Timestamp:
    """估算下一個交易日（跳過週末）"""
    next_day = last_data_date + timedelta(days=1)
    # 跳過週末
    while next_day.weekday() >= 5:  # 5=Saturday, 6=Sunday
        next_day += timedelta(days=1)
    return next_day


def _estimate_trading_days_later(from_date: pd.Timestamp, trading_days: int) -> pd.Timestamp:
    """估算 N 個交易日後的日期（跳過週末）"""
    current = from_date
    count = 0
    while count < trading_days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            count += 1
    return current


def _run_single_strategy(strategy_info: dict, today: pd.Timestamp) -> list[dict]:
    """執行單一策略並輸出報告，回傳待執行委託清單"""
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
    data_start = (today - timedelta(days=365)).strftime("%Y-%m-%d")
    fetcher = DataFetcher(start=data_start)
    data = fetcher.fetch_all([ticker])

    if ticker not in data:
        print(f"\n  [ERROR] 無法取得 {ticker} 資料 (Failed to fetch {ticker} data)\n")
        return []

    df = data[ticker]
    df = _drop_incomplete_bar(df)
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
    print("  60-Day Backtest Summary")
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
        _print_trade_details(trades, config, ticker, has_trailing_stop)

    # 8. 檢查今日訊號 (Check today's signal)
    df_full_signals = detector.detect_signals(df.copy())
    latest_date = df_full_signals.index[-1]
    latest_close = float(df_full_signals.iloc[-1]["Close"])
    signal_today = bool(df_full_signals.loc[latest_date, "Signal"])

    # T 日 = 資料最後一天的下一個交易日
    t_day = _estimate_next_trading_day(latest_date)
    t_day_str = t_day.strftime("%Y-%m-%d")

    print(f"\n{thin_sep}")
    print(f"  最新資料日期 (Latest data): {latest_date.strftime('%Y-%m-%d')}")
    print(f"  T 日 (Next trading day):    {t_day_str}")
    print(f"  {ticker} 收盤價 (Close):     ${latest_close:.2f}")
    print(f"{thin_sep}")

    # 收集委託 (Collect orders)
    orders: list[dict] = []

    if signal_today:
        orders.extend(
            _print_buy_signal(ticker, config, latest_close, latest_date, t_day, has_trailing_stop)
        )
    else:
        print(f"\n  ┌{'─' * 48}┐")
        print(f"  │  今日訊號: 無動作 NO ACTION{' ' * 20}│")
        print(f"  └{'─' * 48}┘")
        print(f"\n  {ticker} 於 {latest_date.strftime('%Y-%m-%d')} 無買入訊號")

    # 9. 未結部位 (Open positions)
    open_orders = _print_open_positions(
        trades, config, today, t_day, ticker, has_trailing_stop, df_full_signals
    )
    orders.extend(open_orders)

    return orders


def _print_trade_details(trades: list[dict], config, ticker: str, has_trailing_stop: bool) -> None:
    """印出逐筆交易明細與回顧性訂單資訊"""
    thin_sep = "-" * 80

    print(f"\n{thin_sep}")
    print("  近 60 日交易明細 (Recent 60-Day Trade Details)")
    print(f"{thin_sep}")

    exit_type_labels = {
        "target": "達標 Target",
        "stop_loss": "停損 Stop",
        "stop_loss_pessimistic": "停損悲觀 Pessim.",
        "trailing_stop": "追蹤停損 Trail",
        "time_expiry": "到期 Expiry",
        "no_data": "無資料 N/A",
    }

    for i, t in enumerate(trades):
        entry_date = t.get("entry_date", t["date"])
        exit_date = t.get("exit_date", "N/A")
        entry_price = t["entry"]
        exit_price = t["exit"]
        label_t = exit_type_labels.get(t["exit_type"], t["exit_type"])
        target_price = entry_price * (1 + config.profit_target)
        stop_price = entry_price * (1 + config.stop_loss)

        if i > 0:
            print()
        print(f"\n  交易 #{i + 1}")
        print(f"  {'─' * 60}")
        print(f"    訊號日:     {t['date']}")
        print(f"    進場日:     {entry_date}")
        print(f"    出場日:     {exit_date}")
        print(f"    進場價:     ${entry_price:.2f}")
        print(f"    出場價:     ${exit_price:.2f}")
        print(f"    報酬:       {t['return_pct']:+.2f}%")
        print(f"    持倉天數:   {t['holding_days']}")
        print(f"    出場方式:   {label_t}")

        # 回顧性訂單資訊
        print("\n    訂單明細 (Order Details):")

        # 步驟 1: BUY
        print(f"    {'─' * 50}")
        print("      步驟 1: 買入")
        print(f"        日期:     {entry_date} (開盤前)")
        print(f"        標的:     {ticker}")
        print("        方向:     BUY (買入)")
        print("        類型:     MARKET (市價單)")
        print("        限價:     N/A (市價)")
        print("        有效期:   Day")
        print(f"        實際成交: ${entry_price:.2f}")
        print("        Firstrade: Buy > Market > Day")

        # 步驟 2: 止盈
        print("      步驟 2: 止盈賣出")
        print(f"        日期:     {entry_date} (買入成交後)")
        print(f"        標的:     {ticker}")
        print("        方向:     SELL (賣出)")
        print("        類型:     LIMIT (限價單)")
        print(f"        限價:     ${target_price:.2f} (+{config.profit_target:.1%} 目標)")
        print("        有效期:   Day (每日收盤自動取消，隔日需重新掛單)")
        print(f"        Firstrade: Sell > Limit > ${target_price:.2f} > Day")

        # 步驟 3: 停損
        print("      步驟 3: 停損賣出")
        print(f"        日期:     {entry_date} (買入成交後)")
        print(f"        標的:     {ticker}")
        print("        方向:     SELL (賣出)")
        print("        類型:     STOP (停損市價單)")
        print(f"        觸發價:   ${stop_price:.2f} ({config.stop_loss:.1%} 停損)")
        print("        有效期:   GTC (長效單，直到成交或取消)")
        print(f"        Firstrade: Sell > Stop > ${stop_price:.2f} > GTC")

        # 追蹤停損（若適用）
        if has_trailing_stop:
            trail_activation = getattr(config, "trail_activation_pct", 0.015)
            trail_distance = getattr(config, "trail_distance_pct", 0.01)
            trail_activate_price = entry_price * (1 + trail_activation)
            print("      追蹤停損:")
            print(
                f"        啟動條件: 盤中最高價 >= ${trail_activate_price:.2f} (進場 +{trail_activation:.1%})"
            )
            print(f"        追蹤方式: 新停損 = 持倉最高價 × {1 - trail_distance:.4f}")

        # 實際出場結果
        print("      實際出場:")
        print(f"        出場日:   {exit_date}")
        print(f"        出場價:   ${exit_price:.2f}")
        print(f"        出場方式: {label_t}")
        print(f"        報酬:     {t['return_pct']:+.2f}%")


def _print_buy_signal(
    ticker: str,
    config,
    last_close: float,
    signal_date: pd.Timestamp,
    t_day: pd.Timestamp,
    has_trailing_stop: bool,
) -> list[dict]:
    """印出買入訊號與下單指令，回傳委託清單"""
    slippage = 0.001  # 0.1%
    estimated_entry = last_close * (1 + slippage)
    target_price = estimated_entry * (1 + config.profit_target)
    stop_price = estimated_entry * (1 + config.stop_loss)

    t_day_str = t_day.strftime("%Y-%m-%d")
    est_expiry = _estimate_trading_days_later(t_day, config.holding_days)
    est_expiry_sell = _estimate_next_trading_day(est_expiry)

    print(f"\n  ┌{'─' * 48}┐")
    print(f"  │  ★ 今日訊號: 買入 BUY TRIGGERED{' ' * 15}│")
    print(f"  └{'─' * 48}┘")

    print(f"\n  {'═' * 60}")
    print("  Firstrade 下單指令 (Order Instructions)")
    print(f"  {'═' * 60}")

    # 步驟 1: 買入
    print(f"\n  步驟 1: {t_day_str} 開盤前掛單買入")
    print(f"  {'─' * 60}")
    print(f"    日期:     {t_day_str} (開盤前)")
    print(f"    標的:     {ticker}")
    print("    方向:     BUY (買入)")
    print("    類型:     MARKET (市價單)")
    print("    限價:     N/A (市價)")
    print("    有效期:   Day")
    print(f"    預估成交: ~${estimated_entry:.2f} (T-1 收盤 ${last_close:.2f} + 0.1% 滑價)")
    print("    Firstrade: Buy > Market > Day")

    # 步驟 2: 止盈單
    print("\n  步驟 2: 買入成交後，立即掛止盈賣出")
    print(f"  {'─' * 60}")
    print(f"    日期:     {t_day_str} (買入成交後)")
    print(f"    標的:     {ticker}")
    print("    方向:     SELL (賣出)")
    print("    類型:     LIMIT (限價單)")
    print(f"    限價:     ${target_price:.2f} (+{config.profit_target:.1%} 目標)")
    print("    有效期:   Day (每日收盤自動取消，隔日需重新掛單)")
    print(f"    Firstrade: Sell > Limit > ${target_price:.2f} > Day")

    # 步驟 3: 停損單
    print("\n  步驟 3: 同時掛停損賣出")
    print(f"  {'─' * 60}")
    print(f"    日期:     {t_day_str} (買入成交後)")
    print(f"    標的:     {ticker}")
    print("    方向:     SELL (賣出)")
    print("    類型:     STOP (停損市價單)")
    print(f"    觸發價:   ${stop_price:.2f} ({config.stop_loss:.1%} 停損)")
    print("    有效期:   GTC (長效單，直到成交或取消)")
    print(f"    Firstrade: Sell > Stop > ${stop_price:.2f} > GTC")

    # 收集委託
    orders = [
        {
            "date": t_day_str,
            "timing": "開盤前",
            "ticker": ticker,
            "action": "BUY",
            "order_type": "MARKET",
            "price": None,
            "price_display": f"市價 (~${estimated_entry:.2f})",
            "duration": "Day",
            "note": "新訊號買入",
        },
        {
            "date": t_day_str,
            "timing": "成交後",
            "ticker": ticker,
            "action": "SELL",
            "order_type": "LIMIT",
            "price": target_price,
            "price_display": f"${target_price:.2f}",
            "duration": "Day",
            "note": f"止盈 +{config.profit_target:.1%}",
        },
        {
            "date": t_day_str,
            "timing": "成交後",
            "ticker": ticker,
            "action": "SELL",
            "order_type": "STOP",
            "price": stop_price,
            "price_display": f"${stop_price:.2f}",
            "duration": "GTC",
            "note": f"停損 {config.stop_loss:.1%}",
        },
    ]

    step_num = 4

    if has_trailing_stop:
        trail_activation = getattr(config, "trail_activation_pct", 0.015)
        trail_distance = getattr(config, "trail_distance_pct", 0.01)
        trail_activate_price = estimated_entry * (1 + trail_activation)

        print(f"\n  步驟 {step_num}: 追蹤停損 — 每日收盤後手動調整")
        print(f"  {'─' * 60}")
        print(
            f"    啟動條件:  {ticker} 盤中最高價 >= ${trail_activate_price:.2f} (進場 +{trail_activation:.1%})"
        )
        print(f"    追蹤方式:  新停損 = 持倉最高價 × {1 - trail_distance:.4f}")
        print("    操作:")
        print("      每日收盤後:")
        print(f"      1. 記錄 {ticker} 當日最高價")
        print(f"      2. 若 最高價 >= ${trail_activate_price:.2f}:")
        print(f"         計算: 新停損 = 最高價 × {1 - trail_distance:.4f}")
        print("      3. 若 新停損 > 現有 STOP 價格:")
        print("         → 登入 Firstrade 修改 STOP SELL 觸發價（只上調不下調）")
        print("    注意: Firstrade 不支援自動追蹤停損，必須手動調整")
        step_num += 1

    # 持倉到期
    print(f"\n  步驟 {step_num}: 持倉到期處理")
    print(f"  {'─' * 60}")
    print(f"    最長持倉:    {config.holding_days} 個交易日")
    print(f"    到期日 (約):  {est_expiry.strftime('%Y-%m-%d')}")
    print("    若到期未出場:")
    print(f"      日期:     {est_expiry.strftime('%Y-%m-%d')} 收盤後")
    print(f"      操作:     取消所有 {ticker} 未成交委託")
    print("      然後:")
    print(f"      日期:     {est_expiry_sell.strftime('%Y-%m-%d')} 開盤前")
    print(f"      標的:     {ticker}")
    print("      方向:     SELL (賣出)")
    print("      類型:     MARKET (市價單)")
    print("      有效期:   Day")
    print("      Firstrade: Sell > Market > Day")

    # 重要提醒
    print("\n  ⚠ 重要提醒")
    print(f"  {'─' * 60}")
    print("    • 上述價格為預估值，實際成交價以 Firstrade 回報為準")
    print("    • 買入成交後，請依實際成交價重新計算:")
    print(f"      目標價 = 實際成交價 × {1 + config.profit_target:.4f}")
    print(f"      停損價 = 實際成交價 × {1 + config.stop_loss:.4f}")
    print("    • LIMIT SELL (止盈) 為 Day 單，每日開盤前需重新掛單")
    print("    • STOP SELL (停損) 為 GTC 單，不需每日重掛")

    return orders


def _print_open_positions(
    trades: list[dict],
    config,
    today: pd.Timestamp,
    t_day: pd.Timestamp,
    ticker: str,
    has_trailing_stop: bool,
    df: pd.DataFrame,
) -> list[dict]:
    """印出未結部位及應掛委託，回傳委託清單"""
    thin_sep = "-" * 80
    t_day_str = t_day.strftime("%Y-%m-%d")

    print(f"\n{thin_sep}")
    print(f"  未結部位 (Open Positions) — {ticker}")
    print(f"{thin_sep}")

    if not trades:
        print("  無未結部位 (No open positions)\n")
        return []

    # 找出仍在持倉期內的交易
    today_str = today.strftime("%Y-%m-%d")
    open_positions = []

    for t in trades:
        exit_date_str = t.get("exit_date", "")
        # 如果出場日期 >= 今日，該部位可能仍然開放
        if exit_date_str >= today_str:
            open_positions.append(t)

    if not open_positions:
        print("  無未結部位 (No open positions)\n")
        return []

    orders: list[dict] = []

    for pos in open_positions:
        entry_date = pos.get("entry_date", pos["date"])
        entry_price = pos["entry"]
        target_price = entry_price * (1 + config.profit_target)
        stop_price = entry_price * (1 + config.stop_loss)

        # 計算已持倉天數
        try:
            entry_ts = pd.Timestamp(entry_date)
            trading_days_held = len(df.loc[entry_ts:today]) - 1
        except Exception:
            trading_days_held = pos["holding_days"]

        days_remaining = max(0, config.holding_days - trading_days_held)
        est_expiry = _estimate_trading_days_later(pd.Timestamp(entry_date), config.holding_days)
        _estimate_next_trading_day(est_expiry)

        print("\n  部位 (Position):")
        print(f"    進場日期:   {entry_date}")
        print(f"    進場價格:   ${entry_price:.2f}")
        print(f"    目標價:     ${target_price:.2f} (+{config.profit_target:.1%})")
        print(f"    停損價:     ${stop_price:.2f} ({config.stop_loss:.1%})")
        print(f"    已持倉:     {trading_days_held} 交易日")
        print(f"    剩餘天數:   {days_remaining} 交易日")
        print(f"    預估到期日: {est_expiry.strftime('%Y-%m-%d')}")

        # 追蹤停損狀態
        effective_stop = stop_price
        if has_trailing_stop:
            trail_activation = getattr(config, "trail_activation_pct", 0.015)
            trail_distance = getattr(config, "trail_distance_pct", 0.01)

            try:
                entry_ts = pd.Timestamp(entry_date)
                hold_df = df.loc[entry_ts:today]
                if not hold_df.empty:
                    highest = float(hold_df["High"].max())
                    unrealized_gain = (highest - entry_price) / entry_price
                    trail_activated = unrealized_gain >= trail_activation

                    print(f"    持倉最高價: ${highest:.2f}")
                    print(
                        f"    追蹤停損:   "
                        f"{'已啟動 ACTIVE' if trail_activated else '未啟動 INACTIVE'}"
                    )

                    if trail_activated:
                        current_trail_stop = highest * (1 - trail_distance)
                        effective_stop = max(stop_price, current_trail_stop)
                        print(f"    當前停損價: ${effective_stop:.2f} (追蹤停損已上調)")
            except Exception:
                pass

        # T 日需要的委託
        if days_remaining == 0:
            # 到期 → 明天賣出
            print("\n    ⚠ 持倉已到期！")
            print(f"    {t_day_str} 開盤前操作:")
            print(f"      1. 取消 {ticker} 所有未成交委託")
            print("      2. 掛 MARKET SELL:")
            print(f"         日期:   {t_day_str}")
            print(f"         標的:   {ticker}")
            print("         方向:   SELL (賣出)")
            print("         類型:   MARKET (市價單)")
            print("         有效期: Day")
            print("         Firstrade: Sell > Market > Day")

            orders.append(
                {
                    "date": t_day_str,
                    "timing": "開盤前",
                    "ticker": ticker,
                    "action": "SELL",
                    "order_type": "MARKET",
                    "price": None,
                    "price_display": "市價 (到期出場)",
                    "duration": "Day",
                    "note": f"持倉到期，進場 {entry_date} @ ${entry_price:.2f}",
                }
            )
        else:
            # 仍在持倉中 → 重新掛 LIMIT SELL (Day 單每日需重掛)
            print(f"\n    {t_day_str} 開盤前操作:")
            print("      掛 LIMIT SELL (每日重新掛單):")
            print(f"         日期:   {t_day_str}")
            print(f"         標的:   {ticker}")
            print("         方向:   SELL (賣出)")
            print("         類型:   LIMIT (限價單)")
            print(f"         限價:   ${target_price:.2f}")
            print("         有效期: Day")
            print(f"         Firstrade: Sell > Limit > ${target_price:.2f} > Day")

            print("      STOP SELL (GTC 長效單，已掛則免操作):")
            print(f"         觸發價: ${effective_stop:.2f}")
            if has_trailing_stop and effective_stop > stop_price:
                print(f"         → 若尚未更新，請修改 STOP 價至 ${effective_stop:.2f}")

            orders.append(
                {
                    "date": t_day_str,
                    "timing": "開盤前",
                    "ticker": ticker,
                    "action": "SELL",
                    "order_type": "LIMIT",
                    "price": target_price,
                    "price_display": f"${target_price:.2f}",
                    "duration": "Day",
                    "note": f"止盈 (進場 {entry_date} @ ${entry_price:.2f})",
                }
            )

    print()
    return orders


def _print_order_sheet(orders: list[dict], today: pd.Timestamp) -> None:
    """印出合併下單清單 (Print consolidated order sheet)"""
    separator = "=" * 80
    thin_sep = "-" * 80

    print(f"\n{separator}")
    print("  T 日下單清單 (T-Day Order Sheet)")
    print(f"{separator}")

    # 今日動作摘要（置頂，讓使用者先掌握待辦）
    unique_tickers = sorted({order["ticker"] for order in orders})
    pre_open_orders = [order for order in orders if order["timing"] == "開盤前"]
    post_fill_orders = [order for order in orders if order["timing"] == "成交後"]
    buy_orders = [order for order in orders if order["action"] == "BUY"]
    sell_orders = [order for order in orders if order["action"] == "SELL"]
    market_orders = [order for order in orders if order["order_type"] == "MARKET"]
    limit_orders = [order for order in orders if order["order_type"] == "LIMIT"]
    stop_orders = [order for order in orders if order["order_type"] == "STOP"]

    print("\n  Trading Followup Summary — 今日動作總覽")
    print(f"  {thin_sep}")
    print(f"  • 日期: {today.strftime('%Y-%m-%d')}")
    covered_tickers = ", ".join(unique_tickers) if unique_tickers else "無"
    print(f"  • 涵蓋標的: {covered_tickers}")
    print(
        "  • 委託統計: "
        f"總計 {len(orders)} 筆 / "
        f"開盤前 {len(pre_open_orders)} 筆 / "
        f"成交後 {len(post_fill_orders)} 筆"
    )
    print(f"  • 方向統計: BUY {len(buy_orders)} 筆 / SELL {len(sell_orders)} 筆")
    print(
        "  • 單別統計: "
        f"MARKET {len(market_orders)} 筆 / "
        f"LIMIT {len(limit_orders)} 筆 / "
        f"STOP {len(stop_orders)} 筆"
    )
    print("\n  今日執行重點:")
    if orders:
        print("  1) 開盤前：先完成所有「開盤前」委託")
        print("  2) 成交後：若有 BUY 成交，立即補掛 LIMIT/STOP 賣單")
        print("  3) 收盤前：確認 Day 單狀態，隔日需重掛 LIMIT SELL")
    else:
        print("  1) 今日無新委託")
        print("  2) 僅需例行檢查既有 GTC 停損單是否仍正確")
        print("  3) 無部位時可跳過下單流程")

    if not orders:
        print("\n  無需下單 (No orders needed)\n")
        return

    # 表頭
    print(
        f"\n  {'#':>2}  {'日期':<12} {'時機':<8} {'標的':<6} "
        f"{'方向':<6} {'類型':<8} {'價格':<20} {'有效期':<6} {'備註'}"
    )
    print(f"  {thin_sep}")

    for i, order in enumerate(orders, 1):
        print(
            f"  {i:>2}  "
            f"{order['date']:<12} "
            f"{order['timing']:<8} "
            f"{order['ticker']:<6} "
            f"{order['action']:<6} "
            f"{order['order_type']:<8} "
            f"{order['price_display']:<20} "
            f"{order['duration']:<6} "
            f"{order['note']}"
        )

    print(f"\n  共 {len(orders)} 筆委託 (Total: {len(orders)} orders)")
    print("\n  操作順序: 按編號依序執行")
    print("  • MARKET BUY 必須在成交後才能掛 SELL 委託")
    print("  • LIMIT SELL 為 Day 單，每日開盤前需重新掛單")
    print("  • STOP SELL 為 GTC 單，掛一次即可（除非需調整追蹤停損）")
    print()
