"""Existing-position exit compatibility for the retired legacy followup portfolio.

This module retains frozen strategy loading, status reporting, and fail-closed exit handling for
positions that already exist. It must not authorize, rank, promote, or open a new legacy position.
"""

import json
import logging
from collections.abc import Callable
from contextlib import redirect_stdout
from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal
from io import StringIO
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from trading.core.data_fetcher import DataFetcher
from trading.core.followup_cutover import (
    FollowupAuthorizationContext,
    FollowupLifecycleRegistry,
    FollowupLifecycleState,
    FollowupStrategy,
    StrategyLifecycle,
    authorize_followup_order,
    build_followup_status_report,
)
from trading.core.followup_data import (
    AuxiliaryDataRequiredError,
    DeclaredAuxiliaryData,
    build_followup_data_bundle,
)
from trading.core.followup_proposals import build_manual_proposal_terms
from trading.core.live_drift import DriftState
from trading.core.live_drift_registry import (
    LiveDriftRegistry,
    LiveDriftRegistryError,
    LiveDriftState,
)
from trading.core.manual_ledger import (
    LedgerConflictError,
    LedgerError,
    LedgerReplay,
    ManualLedgerStore,
)
from trading.core.proposals import ProposalConflictError, ProposalTerms
from trading.experiments import get_experiment
from trading.legacy.definition_resolver import resolve_current_definition_fingerprint
from trading.legacy.results import inspect_result
from trading.market_data import PrimaryUSSessionCalendar
from trading.research_data.result_schema import ResultValidityStatus

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
DEFAULT_FOLLOWUP_LIFECYCLE_PATH = Path("state/followup-lifecycle.json")
DEFAULT_LIVE_DRIFT_PATH = Path("state/live-drift")

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
    lifecycle_path: Path = DEFAULT_FOLLOWUP_LIFECYCLE_PATH,
    drift_path: Path = DEFAULT_LIVE_DRIFT_PATH,
) -> None:
    """主入口：產生跟單訊號報告 (Main entry: generate followup signal report)"""
    today = pd.Timestamp.now().normalize()
    separator = "=" * 80
    ledger_store = ManualLedgerStore(ledger_path)
    ledger_replay: LedgerReplay | None = None
    ledger_gate_reason: str | None = None
    broker_reconciled = False
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
        else:
            broker_reconciled = True

    lifecycle_state: FollowupLifecycleState | None = None
    lifecycle_error: str | None = None
    try:
        lifecycle_state = FollowupLifecycleRegistry(lifecycle_path).read()
    except (OSError, TypeError, ValueError) as exc:
        lifecycle_error = str(exc)

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
    if lifecycle_state is None:
        print(f"  [NO NEW ENTRY] lifecycle registry unavailable: {lifecycle_error}")
    elif lifecycle_state.no_new_entry:
        print("  [NO NEW ENTRY] controlled cutover entry pause is enabled.")

    # 先執行策略並收集各段輸出，讓下單清單可置頂顯示
    strategy_sections: list[str] = []
    all_orders: list[dict] = []

    for selected_strategy_info in STRATEGIES:
        strategy_info = _strategy_info_for_actual_position(
            selected_strategy_info,
            ledger_replay,
            lifecycle_state,
        )
        if strategy_info is None:
            ticker = str(selected_strategy_info["ticker"]).upper()
            strategy_sections.append(
                f"\n  [BLOCKED] {ticker} actual-position strategy ownership is unverified\n"
            )
            continue
        identity = FollowupStrategy(
            str(strategy_info["ticker"]),
            str(strategy_info["experiment_name"]),
        )
        lifecycle = StrategyLifecycle.PAUSED
        if lifecycle_state is not None:
            try:
                lifecycle = lifecycle_state.status_for(
                    identity.ticker,
                    identity.experiment_name,
                )
            except KeyError:
                lifecycle = StrategyLifecycle.PAUSED
        result_valid, result_identity, result_fingerprint = _result_authorization(
            identity.experiment_name
        )
        activation_proof = (
            lifecycle_state.activation_proof_for(identity.ticker, identity.experiment_name)
            if lifecycle_state is not None
            else None
        )
        active_proof_current = (
            activation_proof is not None
            and activation_proof.result_fingerprint == result_fingerprint
        )
        expected_activation_event_id = _activation_event_id_for(lifecycle_state, identity)
        drift_registry_path = _drift_registry_path(drift_path, identity)
        drift_state, drift_hard_guards_clear = _followup_drift_state(
            drift_registry_path,
            lifecycle=lifecycle,
            expected_envelope_id=(
                activation_proof.drift_envelope_id if activation_proof is not None else ""
            ),
            expected_activation_event_id=expected_activation_event_id,
        )
        expected_drift_envelope_id = (
            drift_state.envelope.envelope_id
            if drift_state is not None and drift_state.envelope is not None
            else ""
        )

        def revalidate_buy_authorization(
            strategy_identity: FollowupStrategy = identity,
            expected_result_identity: str = result_identity,
            expected_drift_envelope: str = expected_drift_envelope_id,
        ) -> None:
            current_state = FollowupLifecycleRegistry(lifecycle_path).read_while_coordinated()
            if current_state.no_new_entry:
                raise LedgerConflictError("no-new-entry mode changed before submission")
            if (
                current_state.status_for(
                    strategy_identity.ticker, strategy_identity.experiment_name
                )
                is not StrategyLifecycle.ACTIVE
            ):
                raise LedgerConflictError("strategy is no longer Active")
            current_proof = current_state.activation_proof_for(
                strategy_identity.ticker, strategy_identity.experiment_name
            )
            current_valid, current_identity, current_fingerprint = _result_authorization(
                strategy_identity.experiment_name
            )
            if (
                not current_valid
                or current_identity != expected_result_identity
                or current_proof is None
                or current_proof.result_fingerprint != current_fingerprint
            ):
                raise LedgerConflictError("Active proof or valid result changed before submission")
            current_drift, current_hard_guards_clear = _followup_drift_state(
                _drift_registry_path(drift_path, strategy_identity),
                lifecycle=StrategyLifecycle.ACTIVE,
                expected_envelope_id=(
                    current_proof.drift_envelope_id if current_proof is not None else ""
                ),
                expected_activation_event_id=_activation_event_id_for(
                    current_state, strategy_identity
                ),
                coordination_lock_held=True,
            )
            if (
                current_drift is None
                or current_drift.state is DriftState.PAUSED
                or not current_hard_guards_clear
                or (
                    expected_drift_envelope
                    and (
                        current_drift.envelope is None
                        or current_drift.envelope.envelope_id != expected_drift_envelope
                    )
                )
            ):
                raise LedgerConflictError(
                    "live drift is paused, missing, or changed before submission"
                )

        section_buffer = StringIO()
        with redirect_stdout(section_buffer):
            orders = _run_single_strategy(
                strategy_info,
                today,
                ledger_store=ledger_store,
                ledger_replay=ledger_replay,
                allow_new_entries=ledger_gate_reason is None and ledger_replay is not None,
                lifecycle=lifecycle,
                no_new_entry=(
                    lifecycle_state.no_new_entry if lifecycle_state is not None else True
                ),
                result_valid=result_valid,
                result_identity=result_identity,
                active_proof_current=active_proof_current,
                drift_state=drift_state,
                drift_hard_guards_clear=drift_hard_guards_clear,
                drift_envelope_id=expected_drift_envelope_id,
                drift_checkpoint_id=(
                    drift_state.checkpoints[-1].checkpoint_id
                    if drift_state is not None and drift_state.checkpoints
                    else ""
                ),
                broker_reconciled=broker_reconciled,
                reconciliation_path=reconciliation_path,
                buy_submission_validator=revalidate_buy_authorization,
                coordination_lock_path=FollowupLifecycleRegistry(
                    lifecycle_path
                ).coordination_lock_path,
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


def _strategy_info_for_actual_position(
    selected_strategy_info: dict,
    ledger_replay: LedgerReplay | None,
    lifecycle_state: FollowupLifecycleState | None,
) -> dict | None:
    """Keep a confirmed position attached to the definition that opened it."""
    if ledger_replay is None:
        return selected_strategy_info
    ticker = str(selected_strategy_info["ticker"]).upper()
    position = ledger_replay.positions.get((ticker, ticker))
    if position is None or not position.entry_proposal_id:
        if position is None:
            return selected_strategy_info
        owner = lifecycle_state.position_owner_for(ticker) if lifecycle_state is not None else None
        if owner is None:
            return None
        return _owned_strategy_info(ticker, owner.experiment_name, selected_strategy_info)
    proposal = ledger_replay.proposals.get(position.entry_proposal_id)
    if proposal is None:
        return None
    owner = proposal.authorization.get("strategy_id")
    if not isinstance(owner, str) or not owner.strip():
        lifecycle_owner = (
            lifecycle_state.position_owner_for(ticker) if lifecycle_state is not None else None
        )
        if lifecycle_owner is None:
            return None
        owner = lifecycle_owner.experiment_name
    return _owned_strategy_info(ticker, owner, selected_strategy_info)


def _drift_registry_path(base_path: Path, strategy: FollowupStrategy) -> Path:
    """Resolve one private per-strategy drift registry without mixing trial histories."""
    base = Path(base_path)
    if base.suffix.lower() == ".json":
        return base
    safe_ticker = strategy.ticker.lower().replace("/", "-")
    safe_experiment = strategy.experiment_name.replace("/", "-")
    return base / f"{safe_ticker}--{safe_experiment}.json"


def _followup_drift_state(
    path: Path,
    *,
    lifecycle: StrategyLifecycle,
    expected_envelope_id: str = "",
    expected_activation_event_id: str = "",
    coordination_lock_held: bool = False,
) -> tuple[LiveDriftState | None, bool]:
    """Read a verified overlay; an Active strategy without one fails closed."""
    try:
        registry = LiveDriftRegistry(path)
        state = registry.read_while_coordinated() if coordination_lock_held else registry.read()
    except (LiveDriftRegistryError, OSError, TypeError, ValueError):
        state = None
    if lifecycle is StrategyLifecycle.ACTIVE:
        if state is None or state.envelope is None or state.activation_event_id is None:
            return None, False
        if not expected_envelope_id or not expected_activation_event_id:
            return None, False
        if expected_envelope_id and state.envelope.envelope_id != expected_envelope_id:
            return None, False
        if (
            expected_activation_event_id
            and state.activation_event_id != expected_activation_event_id
        ):
            return None, False
        return state, not bool(state.hard_guards)
    return state, True if state is None else not bool(state.hard_guards)


def _activation_event_id_for(
    lifecycle_state: FollowupLifecycleState | None,
    strategy: FollowupStrategy,
) -> str:
    if lifecycle_state is None:
        return ""
    for event in reversed(lifecycle_state.events):
        payload = event.get("payload")
        if (
            event.get("event_type") == "strategy_activated"
            and isinstance(payload, dict)
            and payload.get("ticker") == strategy.ticker
            and payload.get("experiment_name") == strategy.experiment_name
        ):
            return str(event.get("event_id", ""))
    return ""


def _owned_strategy_info(ticker: str, owner: str, selected_strategy_info: dict) -> dict:
    if owner == selected_strategy_info.get("experiment_name"):
        return selected_strategy_info
    return {
        "ticker": ticker,
        "experiment_name": owner,
        "label": f"RETIRING {owner}",
        "has_trailing_stop": False,
    }


def _estimate_next_trading_day(last_data_date: pd.Timestamp) -> pd.Timestamp:
    """估算下一個交易日（跳過週末）"""
    next_day = last_data_date + timedelta(days=1)
    # 跳過週末
    while next_day.weekday() >= 5:  # 5=Saturday, 6=Sunday
        next_day += timedelta(days=1)
    return next_day


def _result_authorization(experiment_name: str) -> tuple[bool, str, str]:
    """Return validity plus the exact persisted-result evidence identity."""
    try:
        record = inspect_result(
            experiment_name,
            current_definition_fingerprint=resolve_current_definition_fingerprint(experiment_name),
        )
    except Exception:  # noqa: BLE001 - followup authorization must fail closed
        logger.exception("Failed to verify result for %s", experiment_name)
        return False, "", ""
    if record is None or record.validity.status is not ResultValidityStatus.VALID:
        return False, "", ""
    payload = record.result.payload
    snapshot_id = payload.get("data_snapshot_id")
    fingerprint = payload.get("definition_fingerprint")
    if not isinstance(snapshot_id, str) or not isinstance(fingerprint, str):
        return False, "", ""
    return True, f"{record.path}:{snapshot_id}:{fingerprint}", fingerprint


def _is_followup_data_fresh(latest_date: pd.Timestamp) -> bool:
    """Require the exact latest completed XNYS session for new-entry authorization."""
    try:
        required = PrimaryUSSessionCalendar().latest_completed_session(
            datetime.now(ZoneInfo("UTC"))
        )
        return latest_date.date() == required
    except (TypeError, ValueError):
        return False


def _run_single_strategy(
    strategy_info: dict,
    today: pd.Timestamp,
    *,
    ledger_store: ManualLedgerStore | None = None,
    ledger_replay: LedgerReplay | None = None,
    allow_new_entries: bool = False,
    lifecycle: StrategyLifecycle = StrategyLifecycle.PAUSED,
    no_new_entry: bool = True,
    result_valid: bool = False,
    result_identity: str = "",
    active_proof_current: bool = False,
    drift_state: LiveDriftState | None = None,
    drift_hard_guards_clear: bool = True,
    drift_envelope_id: str = "",
    drift_checkpoint_id: str = "",
    broker_reconciled: bool = False,
    reconciliation_path: Path | None = None,
    buy_submission_validator: Callable[[], None] | None = None,
    coordination_lock_path: Path | None = None,
) -> list[dict]:
    """執行單一策略並輸出報告，回傳待執行委託清單"""
    experiment_name = strategy_info["experiment_name"]
    label = strategy_info["label"]
    ticker = strategy_info["ticker"]

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
    has_trailing_stop = bool(strategy_info.get("has_trailing_stop")) or (
        hasattr(config, "trail_activation_pct") and hasattr(config, "trail_distance_pct")
    )
    execution_strategy_info = {**strategy_info, "has_trailing_stop": has_trailing_stop}

    # 2. 抓取資料（往前抓 365 天確保指標暖身）
    data_start = (today - timedelta(days=365)).strftime("%Y-%m-%d")
    fetcher = DataFetcher(start=data_start)
    auxiliary_symbols = (
        detector.auxiliary_symbols() if isinstance(detector, DeclaredAuxiliaryData) else ()
    )
    data = fetcher.fetch_all([ticker, *auxiliary_symbols])

    if ticker not in data:
        print(f"\n  [ERROR] 無法取得 {ticker} 資料 (Failed to fetch {ticker} data)\n")
        return []

    df = data[ticker]
    df = _drop_incomplete_bar(df)
    try:
        data_bundle = build_followup_data_bundle(
            primary_symbol=str(ticker),
            primary_frame=df,
            auxiliary_symbols=auxiliary_symbols,
            frames={symbol: data[symbol] for symbol in auxiliary_symbols if symbol in data},
        )
        if isinstance(detector, DeclaredAuxiliaryData):
            detector.bind_auxiliary_data(data_bundle)
    except AuxiliaryDataRequiredError as exc:
        print(f"\n  [ERROR] declared market-data bundle unavailable: {exc}\n")
        ticker_text = str(ticker).upper()
        position = (
            ledger_replay.positions.get((ticker_text, ticker_text))
            if ledger_replay is not None
            else None
        )
        if position is None or ledger_store is None or df.empty:
            return []
        df = df.copy()
        df["Signal"] = False
        latest_date = df.index[-1]
        return _print_manual_strategy_orders(
            execution_strategy_info,
            config,
            ledger_store,
            ledger_replay,
            latest_date=latest_date,
            latest_close=Decimal(str(df.iloc[-1]["Close"])),
            t_day=_estimate_next_trading_day(latest_date),
            today=today,
            frame=df,
            allow_new_entries=False,
            authorization_context=FollowupAuthorizationContext(
                lifecycle=lifecycle,
                no_new_entry=True,
                result_valid=result_valid,
                result_identity=result_identity,
                active_proof_current=False,
                drift_state=drift_state,
                drift_hard_guards_clear=False,
                drift_envelope_id=drift_envelope_id,
                drift_checkpoint_id=drift_checkpoint_id,
                data_fresh=False,
                data_cutoff=latest_date.date().isoformat(),
                data_bundle_identity="",
                ledger_verified=True,
                ledger_accounting_hash=ledger_replay.accounting_hash,
                broker_reconciled=broker_reconciled,
                proposal_epoch_current=True,
                has_actual_position=True,
            ),
            reconciliation_path=reconciliation_path,
            coordination_lock_path=coordination_lock_path,
        )
    df = data_bundle.primary
    data_bundle_identity = data_bundle.identity
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
    ticker_text = str(ticker).upper()
    actual_position = (
        ledger_replay is not None and (ticker_text, ticker_text) in ledger_replay.positions
    )
    authorization_context = FollowupAuthorizationContext(
        lifecycle=lifecycle,
        no_new_entry=no_new_entry,
        result_valid=result_valid,
        result_identity=result_identity,
        active_proof_current=active_proof_current,
        drift_state=drift_state,
        drift_hard_guards_clear=(drift_hard_guards_clear and _is_followup_data_fresh(latest_date)),
        drift_envelope_id=drift_envelope_id,
        drift_checkpoint_id=drift_checkpoint_id,
        data_fresh=_is_followup_data_fresh(latest_date),
        data_cutoff=latest_date.date().isoformat(),
        data_bundle_identity=data_bundle_identity,
        ledger_verified=ledger_replay is not None,
        ledger_accounting_hash=(ledger_replay.accounting_hash if ledger_replay is not None else ""),
        broker_reconciled=broker_reconciled,
        proposal_epoch_current=ledger_replay is not None,
        has_actual_position=actual_position,
    )
    status = build_followup_status_report(
        FollowupStrategy(ticker_text, str(experiment_name)),
        authorization_context,
    )

    # T 日 = 資料最後一天的下一個交易日
    t_day = _estimate_next_trading_day(latest_date)
    t_day_str = t_day.strftime("%Y-%m-%d")

    print(f"\n{thin_sep}")
    print(f"  最新資料日期 (Latest data): {latest_date.strftime('%Y-%m-%d')}")
    print(f"  T 日 (Next trading day):    {t_day_str}")
    print(f"  {ticker} 收盤價 (Close):     ${latest_close:.2f}")
    print(f"  Phase 7 lifecycle:          {status.lifecycle.value}")
    print(
        "  Phase 8 drift state:         "
        f"{drift_state.state.value if drift_state is not None else 'unavailable'}"
    )
    print(f"  BUY authorization:          {status.buy_reason}")
    print(f"{thin_sep}")

    # 收集委託 (Collect orders)
    orders: list[dict] = []

    if ledger_replay is not None and ledger_store is not None:
        orders.extend(
            _print_manual_strategy_orders(
                execution_strategy_info,
                config,
                ledger_store,
                ledger_replay,
                latest_date=latest_date,
                latest_close=latest_close,
                t_day=t_day,
                today=today,
                frame=df_full_signals,
                allow_new_entries=allow_new_entries,
                authorization_context=authorization_context,
                reconciliation_path=reconciliation_path,
                buy_submission_validator=buy_submission_validator,
                coordination_lock_path=coordination_lock_path,
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
    authorization_context: FollowupAuthorizationContext | None = None,
    reconciliation_path: Path | None = None,
    buy_submission_validator: Callable[[], None] | None = None,
    coordination_lock_path: Path | None = None,
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

    if authorization_context is None:
        authorization_context = FollowupAuthorizationContext(
            lifecycle=StrategyLifecycle.ACTIVE,
            no_new_entry=not allow_new_entries,
            result_valid=True,
            result_identity="legacy-compatibility-result",
            active_proof_current=True,
            data_fresh=True,
            data_cutoff=latest_date.date().isoformat(),
            data_bundle_identity="legacy-compatibility-bundle",
            ledger_verified=True,
            ledger_accounting_hash=ledger_replay.accounting_hash,
            broker_reconciled=allow_new_entries,
            proposal_epoch_current=True,
            has_actual_position=position is not None,
        )
    else:
        authorization_context = replace(
            authorization_context,
            has_actual_position=position is not None,
            proposal_epoch_current=True,
        )

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
        decision = authorize_followup_order(term.action, authorization_context)
        if not decision.authorized:
            print(f"\n  [{term.action} BLOCKED] {term.proposal_id}: {decision.reason}")
            continue
        authorization = authorization_context.authorization_payload(
            strategy_id=str(strategy_info.get("experiment_name", "")),
            allocation_epoch=term.allocation_epoch,
        )
        try:
            submission = ledger_store.record_submission(
                term,
                occurred_at=ledger_store.now(),
                authorization=authorization,
                expected_accounting_hash=authorization_context.ledger_accounting_hash,
                reconciliation_path=reconciliation_path,
                require_current_reconciliation=(
                    term.action == "BUY" and reconciliation_path is not None
                ),
                submission_validator=(buy_submission_validator if term.action == "BUY" else None),
                coordination_lock_path=(coordination_lock_path if term.action == "BUY" else None),
            )
        except (LedgerError, ProposalConflictError) as exc:
            print(f"\n  [CONFLICT] {exc}")
            continue
        order = _proposal_to_order(
            term,
            ticker,
            strategy_info=strategy_info,
            authorization_context=authorization_context,
            persisted_authorization=json.loads(submission.metadata).get("authorization"),
        )
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


def _proposal_to_order(
    term: ProposalTerms,
    ticker: str,
    *,
    strategy_info: dict | None = None,
    authorization_context: FollowupAuthorizationContext | None = None,
    persisted_authorization: object = None,
) -> dict:
    price_display = "市價" if term.price is None else f"${_decimal_display(term.price)}"
    note = {
        "entry": "新訊號買入 proposal",
        "target": "confirmed position 止盈",
        "stop": "confirmed position 停損",
        "expiry": "confirmed position 到期出場",
    }.get(term.role, term.role)
    order = {
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
    if strategy_info is not None and authorization_context is not None:
        evidence = (
            persisted_authorization
            if isinstance(persisted_authorization, dict)
            else authorization_context.authorization_payload(
                strategy_id=str(strategy_info.get("experiment_name", "")),
                allocation_epoch=term.allocation_epoch,
            )
        )
        order.update(evidence)
    return order


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
