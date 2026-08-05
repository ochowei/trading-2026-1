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
from decimal import Decimal
from io import StringIO
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from trading.core.data_fetcher import DataFetcher
from trading.core.followup_proposals import build_manual_proposal_terms
from trading.core.manual_ledger import LedgerError, LedgerReplay, ManualLedgerStore
from trading.core.proposals import ProposalConflictError, ProposalTerms
from trading.experiments import get_experiment

logger = logging.getLogger(__name__)

# 各標的最佳策略 (Best strategy per ticker)
STRATEGIES: list[dict[str, str | bool]] = [
    {
        "experiment_name": "cibr_014_multi_period_capitulation_mr",
        "label": "CIBR-014",
        "ticker": "CIBR",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "copx_007_vol_adaptive",
        "label": "COPX-007",
        "ticker": "COPX",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "dia_013_trend_regime_pullback",
        "label": "DIA-013",
        "ticker": "DIA",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "eem_012_bb_lower_pullback_cap",
        "label": "EEM-012",
        "ticker": "EEM",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "ewj_002_vol_adaptive_pullback",
        "label": "EWJ-002",
        "ticker": "EWJ",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "ewt_001_pullback_wr_reversal",
        "label": "EWT-001",
        "ticker": "EWT",
        "has_trailing_stop": True,
    },
    {
        "experiment_name": "ewz_006_bb_lower_pullback_cap",
        "label": "EWZ-006",
        "ticker": "EWZ",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "fcx_008_trend_pullback",
        "label": "FCX-008",
        "ticker": "FCX",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "fxi_005_wr14_extended_mr",
        "label": "FXI-005",
        "ticker": "FXI",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "gld_016_dxy_divergence_mr",
        "label": "GLD-016",
        "ticker": "GLD",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "inda_010_vol_transition_mr",
        "label": "INDA-010",
        "ticker": "INDA",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "iwm_006_bb_squeeze_breakout",
        "label": "IWM-006",
        "ticker": "IWM",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "nvda_007_rs_exit_optimized",
        "label": "NVDA-007",
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
        "experiment_name": "spy_007_trend_pullback",
        "label": "SPY-007",
        "ticker": "SPY",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "tlt_017_yield_curve_slope_mr",
        "label": "TLT-017",
        "ticker": "TLT",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "tqqq_025_vxn_vix_vvix_filter",
        "label": "TQQQ-025",
        "ticker": "TQQQ",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "tsla_017_qqq_divergence_breakout",
        "label": "TSLA-017",
        "ticker": "TSLA",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "tsm_006_momentum_pullback",
        "label": "TSM-006",
        "ticker": "TSM",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "ura_003_pullback_rsi2",
        "label": "URA-003",
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
        "experiment_name": "vgk_007_bb_lower_mr",
        "label": "VGK-007",
        "ticker": "VGK",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "voo_003_wider_tp",
        "label": "VOO-003",
        "ticker": "VOO",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "xbi_018_xbi_xlv_divergence_mr",
        "label": "XBI-018",
        "ticker": "XBI",
        "has_trailing_stop": False,
    },
    {
        "experiment_name": "xlu_002_capped_pullback_wr",
        "label": "XLU-002",
        "ticker": "XLU",
        "has_trailing_stop": False,
    },
]

LOOKBACK_TRADING_DAYS = 60
DEFAULT_MANUAL_LEDGER_PATH = Path("state/manual-execution-ledger.csv")
DEFAULT_RECONCILIATION_PATH = Path("state/manual-reconciliation.json")

_NY_TZ = ZoneInfo("America/New_York")


def _drop_incomplete_bar(df: pd.DataFrame, *, now_et: datetime | None = None) -> pd.DataFrame:
    """若最後一根 bar 為盤中未收盤的當日資料，則丟棄。

    判斷條件：最後 bar 日期 == 美東今天 且 美東時間尚未過 16:30（收盤後 30 分鐘緩衝）。
    使用 America/New_York 時區，自動處理 EST/EDT 日光節約切換。
    """
    if df.empty:
        return df

    now_et = now_et or datetime.now(_NY_TZ)
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


def run_followup(
    *,
    ledger_path: Path = DEFAULT_MANUAL_LEDGER_PATH,
    reconciliation_path: Path = DEFAULT_RECONCILIATION_PATH,
) -> None:
    """主入口：產生跟單訊號報告 (Main entry: generate followup signal report)"""
    today = pd.Timestamp.now().normalize()
    separator = "=" * 80
    ledger_store = ManualLedgerStore(ledger_path)
    ledger_replay: LedgerReplay | None = None
    ledger_gate_reason: str | None = None
    try:
        ledger_replay = ledger_store.verify()
    except LedgerError as exc:
        ledger_gate_reason = f"ledger verification failed: {exc}"
    if ledger_replay is not None:
        expected_universe = {str(item["ticker"]).upper() for item in STRATEGIES}
        if set(ledger_replay.universe) != expected_universe:
            ledger_gate_reason = (
                "ledger universe does not match followup universe "
                f"(ledger={','.join(ledger_replay.universe)}, "
                f"followup={','.join(sorted(expected_universe))})"
            )
        elif not ledger_store.reconciliation_is_current(reconciliation_path):
            ledger_gate_reason = "broker reconciliation is missing, failed, or stale"

    print(f"\n{separator}")
    print(f"  TRADING FOLLOWUP REPORT — {today.strftime('%Y-%m-%d')}")
    print("  本報告於 T-1 日收盤後產生，請於 T 日開盤前下單")
    print("  This report is generated after T-1 close. Place orders before T-day open.")
    print(f"{separator}")
    if ledger_replay is None:
        print(f"  [BLOCKED] {ledger_gate_reason or 'manual ledger unavailable'}")
    elif ledger_gate_reason is not None:
        print(f"  [BUY BLOCKED] {ledger_gate_reason}")
    else:
        print("  Ledger verified and broker-reconciled; proposals remain dry-run manual orders.")

    # 先執行策略並收集各段輸出，讓下單清單可置頂顯示
    strategy_sections: list[str] = []
    all_orders: list[dict] = []

    for strategy_info in STRATEGIES:
        section_buffer = StringIO()
        with redirect_stdout(section_buffer):
            orders = _run_single_strategy(
                strategy_info,
                today,
                ledger_store=ledger_store,
                ledger_replay=ledger_replay,
                allow_new_entries=ledger_gate_reason is None and ledger_replay is not None,
            )
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


def _run_single_strategy(
    strategy_info: dict,
    today: pd.Timestamp,
    *,
    ledger_store: ManualLedgerStore | None = None,
    ledger_replay: LedgerReplay | None = None,
    allow_new_entries: bool = False,
) -> list[dict]:
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
    latest_close = Decimal(str(df_full_signals.iloc[-1]["Close"]))
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

    if ledger_replay is not None and ledger_store is not None:
        orders.extend(
            _print_manual_strategy_orders(
                strategy_info,
                config,
                ledger_store,
                ledger_replay,
                latest_date=latest_date,
                latest_close=latest_close,
                t_day=t_day,
                today=today,
                frame=df_full_signals,
                allow_new_entries=allow_new_entries,
            )
        )
    elif signal_today:
        print("\n  [BLOCKED] 未驗證手動 ledger；不產生 BUY proposal")
    else:
        print(f"\n  ┌{'─' * 48}┐")
        print(f"  │  今日訊號: 無動作 NO ACTION{' ' * 20}│")
        print(f"  └{'─' * 48}┘")
        print(f"\n  {ticker} 於 {latest_date.strftime('%Y-%m-%d')} 無買入訊號")

    # The manual strategy helper above also renders actual exits from confirmed fills.
    if ledger_replay is None or ledger_store is None:
        print("\n  未驗證 ledger；不推導未結部位或 SELL 指令")

    return orders


def _print_manual_strategy_orders(
    strategy_info: dict,
    config,
    ledger_store: ManualLedgerStore,
    ledger_replay: LedgerReplay,
    *,
    latest_date: pd.Timestamp,
    latest_close: Decimal,
    t_day: pd.Timestamp,
    today: pd.Timestamp,
    frame: pd.DataFrame,
    allow_new_entries: bool,
) -> list[dict]:
    """Render and persist idempotent proposals from actual ledger state only."""
    ticker = str(strategy_info["ticker"]).upper()
    position = ledger_replay.positions.get((ticker, ticker))
    if position is not None:
        opened = pd.Timestamp(position.opened_at.date())
        held_trading_days = max(0, len(frame.loc[opened:today]) - 1)
        print("\n  實際部位 (Confirmed manual position)")
        print(f"    進場日期:   {position.opened_at.date().isoformat()}")
        print(f"    實際數量:   {_decimal_display(position.quantity)}")
        print(f"    實際成交均價: ${_decimal_display(position.average_price)}")
        print(f"    成本基礎:   ${_decimal_display(position.cost_basis)}")
        print(f"    已持倉:     {held_trading_days} 交易日")
    else:
        held_trading_days = 0

    estimated_entry = Decimal(str(latest_close)) * (Decimal("1") + Decimal("0.001"))
    trailing_high: Decimal | None = None
    trail_activation_pct: Decimal | None = None
    trail_distance_pct: Decimal | None = None
    if position is not None and bool(strategy_info.get("has_trailing_stop")):
        hold_frame = frame.loc[pd.Timestamp(position.opened_at.date()) : today]
        if "High" in hold_frame:
            high_values = [Decimal(str(value)) for value in hold_frame["High"].dropna()]
            if high_values:
                trailing_high = max(high_values)
                trail_activation_pct = Decimal(str(getattr(config, "trail_activation_pct", 0.015)))
                trail_distance_pct = Decimal(str(getattr(config, "trail_distance_pct", 0.01)))
    try:
        terms = build_manual_proposal_terms(
            ledger_replay,
            sleeve_id=ticker,
            instrument=ticker,
            signal_today=bool(frame.loc[latest_date, "Signal"]),
            signal_date=latest_date.date(),
            trading_date=t_day.date(),
            estimated_entry=estimated_entry,
            profit_target=Decimal(str(config.profit_target)),
            stop_loss=Decimal(str(config.stop_loss)),
            holding_days=int(config.holding_days),
            held_trading_days=held_trading_days,
            trailing_high=trailing_high,
            trail_activation_pct=trail_activation_pct,
            trail_distance_pct=trail_distance_pct,
        )
    except (KeyError, ValueError) as exc:
        print(f"\n  [ERROR] 無法建立 ledger proposal: {exc}")
        return []

    if not terms:
        if position is None:
            print("\n  今日訊號: 無動作 NO ACTION")
        return []

    orders: list[dict] = []
    for term in terms:
        if term.action == "BUY" and not allow_new_entries:
            print(f"\n  [BUY BLOCKED] {term.proposal_id}: ledger/broker gate 未通過")
            continue
        try:
            ledger_store.record_submission(term, occurred_at=ledger_store.now())
        except ProposalConflictError as exc:
            print(f"\n  [CONFLICT] {exc}")
            continue
        order = _proposal_to_order(term, ticker)
        orders.append(order)
        print(
            f"\n  {term.action} proposal {term.proposal_id}: "
            f"{ticker} qty={_decimal_display(term.quantity)} "
            f"{term.order_type} {order['price_display']}"
        )
        if term.action == "BUY":
            print("    尚未確認成交；不建立實際持倉或 SELL 指令。")
        elif term.role == "target":
            print("    止盈價與數量均來自 confirmed fill 的實際部位。")
        elif term.role == "stop":
            print("    停損價與數量均來自 confirmed fill 的實際部位。")
        elif term.role == "expiry":
            print("    到期出場使用 confirmed fill 的實際數量。")
    return orders


def _proposal_to_order(term: ProposalTerms, ticker: str) -> dict:
    price_display = "市價" if term.price is None else f"${_decimal_display(term.price)}"
    note = {
        "entry": "新訊號買入 proposal",
        "target": "confirmed position 止盈",
        "stop": "confirmed position 停損",
        "expiry": "confirmed position 到期出場",
    }.get(term.role, term.role)
    return {
        "date": term.trading_date.isoformat(),
        "timing": "開盤前",
        "ticker": ticker,
        "action": term.action,
        "order_type": term.order_type,
        "price": term.price,
        "price_display": price_display,
        "duration": term.duration,
        "note": note,
        "quantity": term.quantity,
        "proposal_id": term.proposal_id,
    }


def _decimal_display(value: Decimal) -> str:
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


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
        f"{'方向':<6} {'類型':<8} {'數量':<14} {'價格':<20} {'有效期':<6} {'Proposal ID / 備註'}"
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
            f"{_decimal_display(order['quantity']) if isinstance(order.get('quantity'), Decimal) else '-':<14} "
            f"{order['price_display']:<20} "
            f"{order['duration']:<6} "
            f"{order.get('proposal_id', '-')} / {order['note']}"
        )

    print(f"\n  共 {len(orders)} 筆委託 (Total: {len(orders)} orders)")
    print("\n  操作順序: 按編號依序執行")
    print("  • MARKET BUY 必須在成交後才能掛 SELL 委託")
    print("  • LIMIT SELL 為 Day 單，每日開盤前需重新掛單")
    print("  • STOP SELL 為 GTC 單，掛一次即可（除非需調整追蹤停損）")
    print()
