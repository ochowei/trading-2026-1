from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pandas as pd

from trading.core.followup_cutover import (
    FollowupActivationProof,
    FollowupAuthorizationContext,
    FollowupLifecycleRegistry,
    FollowupShadowProof,
    FollowupStrategy,
    StrategyLifecycle,
)
from trading.core.live_drift import DriftState
from trading.followup import _print_manual_strategy_orders, run_followup


def _config() -> SimpleNamespace:
    return SimpleNamespace(profit_target=0.10, stop_loss=-0.05, holding_days=20)


def _frame() -> pd.DataFrame:
    index = pd.to_datetime(["2026-08-04", "2026-08-05"])
    return pd.DataFrame(
        {
            "Close": [10.0, 10.0],
            "High": [10.5, 10.5],
            "Signal": [False, True],
        },
        index=index,
    )


def _authorization(
    lifecycle: StrategyLifecycle,
    **overrides: bool,
) -> FollowupAuthorizationContext:
    values = {
        "no_new_entry": False,
        "result_valid": True,
        "result_identity": "result-spy-007-snapshot-1",
        "active_proof_current": True,
        "data_fresh": True,
        "data_cutoff": "2026-08-05",
        "data_bundle_identity": "b" * 64,
        "ledger_verified": True,
        "ledger_accounting_hash": "a" * 64,
        "broker_reconciled": True,
        "proposal_epoch_current": True,
        "has_actual_position": False,
        "drift_state": DriftState.HEALTHY,
        "drift_hard_guards_clear": True,
        "drift_envelope_id": "d" * 64,
    }
    values.update(overrides)
    return FollowupAuthorizationContext(lifecycle=lifecycle, **values)


def _shadow_proof(shadow_id: str) -> FollowupShadowProof:
    return FollowupShadowProof(
        shadow_id=shadow_id,
        registration_event_id=f"shadow-registration:{shadow_id}",
        historical_screen_event_id="historical-screen:plan-1",
        result_fingerprint="a" * 64,
        parity_digest="b" * 64,
    )


def test_repeated_followup_submission_is_idempotent_and_unconfirmed_buy_has_no_position(
    make_manual_ledger,
) -> None:
    store = make_manual_ledger(
        initialized_at=datetime(2026, 8, 4, 12, 0, tzinfo=UTC),
    )
    frame = _frame()
    definition = {"ticker": "SPY"}
    authorization = _authorization(
        StrategyLifecycle.ACTIVE,
        ledger_accounting_hash=store.verify().accounting_hash,
    )
    first = _print_manual_strategy_orders(
        definition,
        _config(),
        store,
        store.verify(),
        latest_date=frame.index[-1],
        latest_close=10.0,
        t_day=pd.Timestamp("2026-08-06"),
        today=pd.Timestamp("2026-08-05"),
        frame=frame,
        allow_new_entries=True,
        authorization_context=authorization,
    )
    second = _print_manual_strategy_orders(
        definition,
        _config(),
        store,
        store.verify(),
        latest_date=frame.index[-1],
        latest_close=10.0,
        t_day=pd.Timestamp("2026-08-06"),
        today=pd.Timestamp("2026-08-05"),
        frame=frame,
        allow_new_entries=True,
        authorization_context=authorization,
    )

    assert len(first) == len(second) == 1
    assert first[0]["proposal_id"] == second[0]["proposal_id"]
    replay = store.verify()
    assert replay.positions == {}
    assert len(replay.proposals) == 1
    assert len(replay.events) == 2


def test_reconciliation_gate_blocks_new_buy_without_blocking_ledger_replay(
    make_manual_ledger,
) -> None:
    store = make_manual_ledger(
        initialized_at=datetime(2026, 8, 4, 12, 0, tzinfo=UTC),
    )
    frame = _frame()
    orders = _print_manual_strategy_orders(
        {"ticker": "SPY"},
        _config(),
        store,
        store.verify(),
        latest_date=frame.index[-1],
        latest_close=10.0,
        t_day=pd.Timestamp("2026-08-06"),
        today=pd.Timestamp("2026-08-05"),
        frame=frame,
        allow_new_entries=False,
    )
    assert orders == []
    assert store.verify().positions == {}
    assert len(store.verify().events) == 1


def test_phase_7_shadow_cannot_emit_buy_even_when_legacy_boolean_gate_is_true(
    make_manual_ledger,
) -> None:
    store = make_manual_ledger(
        initialized_at=datetime(2026, 8, 4, 12, 0, tzinfo=UTC),
    )

    orders = _print_manual_strategy_orders(
        {"ticker": "SPY", "experiment_name": "spy_007_trend_pullback"},
        _config(),
        store,
        store.verify(),
        latest_date=pd.Timestamp("2026-08-05"),
        latest_close=10.0,
        t_day=pd.Timestamp("2026-08-06"),
        today=pd.Timestamp("2026-08-05"),
        frame=_frame(),
        allow_new_entries=True,
        authorization_context=_authorization(StrategyLifecycle.SHADOW),
    )

    assert orders == []
    assert len(store.verify().events) == 1


def test_phase_7_order_report_links_active_strategy_and_guard_evidence(
    make_manual_ledger,
) -> None:
    store = make_manual_ledger(
        initialized_at=datetime(2026, 8, 4, 12, 0, tzinfo=UTC),
    )
    accounting_hash = store.verify().accounting_hash
    context = _authorization(
        StrategyLifecycle.ACTIVE,
        ledger_accounting_hash=accounting_hash,
    )

    orders = _print_manual_strategy_orders(
        {"ticker": "SPY", "experiment_name": "spy_007_trend_pullback"},
        _config(),
        store,
        store.verify(),
        latest_date=pd.Timestamp("2026-08-05"),
        latest_close=10.0,
        t_day=pd.Timestamp("2026-08-06"),
        today=pd.Timestamp("2026-08-05"),
        frame=_frame(),
        allow_new_entries=False,
        authorization_context=context,
    )

    assert len(orders) == 1
    assert orders[0]["strategy_id"] == "spy_007_trend_pullback"
    assert orders[0]["strategy_lifecycle"] == "active"
    assert orders[0]["result_valid"] is True
    assert orders[0]["result_identity"] == "result-spy-007-snapshot-1"
    assert orders[0]["data_fresh"] is True
    assert orders[0]["data_cutoff"] == "2026-08-05"
    assert orders[0]["ledger_verified"] is True
    assert orders[0]["ledger_accounting_hash"] == accounting_hash
    assert orders[0]["broker_reconciled"] is True
    proposal = store.verify().proposals[orders[0]["proposal_id"]]
    assert proposal.authorization["strategy_id"] == "spy_007_trend_pullback"
    assert proposal.authorization["result_identity"] == "result-spy-007-snapshot-1"


def test_followup_exit_proposals_use_actual_manual_fill(make_manual_ledger) -> None:
    store = make_manual_ledger(
        initialized_at=datetime(2026, 8, 4, 12, 0, tzinfo=UTC),
    )
    entry = _print_manual_strategy_orders(
        {"ticker": "SPY"},
        _config(),
        store,
        store.verify(),
        latest_date=pd.Timestamp("2026-08-05"),
        latest_close=10.0,
        t_day=pd.Timestamp("2026-08-06"),
        today=pd.Timestamp("2026-08-05"),
        frame=_frame(),
        allow_new_entries=True,
        authorization_context=_authorization(
            StrategyLifecycle.ACTIVE,
            ledger_accounting_hash=store.verify().accounting_hash,
        ),
    )
    proposal_id = entry[0]["proposal_id"]
    fill_time = datetime.now(UTC) + timedelta(seconds=1)
    store.record_fill(
        proposal_id=proposal_id,
        sleeve_id="SPY",
        instrument="SPY",
        side="BUY",
        quantity=Decimal("7"),
        price=Decimal("11.23"),
        occurred_at=fill_time,
    )
    store.now = lambda: fill_time + timedelta(seconds=1)
    exits = _print_manual_strategy_orders(
        {"ticker": "SPY"},
        _config(),
        store,
        store.verify(),
        latest_date=pd.Timestamp("2026-08-05"),
        latest_close=99.0,
        t_day=pd.Timestamp("2026-08-07"),
        today=pd.Timestamp("2026-08-06"),
        frame=_frame(),
        allow_new_entries=True,
    )
    assert {order["action"] for order in exits} == {"SELL"}
    assert {order["quantity"] for order in exits} == {Decimal("7")}
    assert {order["price"] for order in exits} == {Decimal("12.353"), Decimal("10.6685")}
    assert all("proposal_id" in order for order in exits)

    changed_evidence = _authorization(
        StrategyLifecycle.RETIRING,
        data_cutoff="2026-08-06",
        ledger_accounting_hash=store.verify().accounting_hash,
        has_actual_position=True,
    )
    repeated = _print_manual_strategy_orders(
        {"ticker": "SPY", "experiment_name": "spy_007_trend_pullback"},
        _config(),
        store,
        store.verify(),
        latest_date=pd.Timestamp("2026-08-05"),
        latest_close=99.0,
        t_day=pd.Timestamp("2026-08-08"),
        today=pd.Timestamp("2026-08-07"),
        frame=_frame(),
        allow_new_entries=False,
        authorization_context=changed_evidence,
    )
    original_stop = next(order for order in exits if order["order_type"] == "STOP")
    repeated_stop = next(order for order in repeated if order["order_type"] == "STOP")
    assert repeated_stop["proposal_id"] == original_stop["proposal_id"]


def test_run_followup_uses_verified_lifecycle_state_instead_of_legacy_buy_boolean(
    make_manual_ledger,
    monkeypatch,
    tmp_path,
) -> None:
    store = make_manual_ledger(path=tmp_path / "ledger.csv")
    lifecycle_path = tmp_path / "lifecycle.json"
    registry = FollowupLifecycleRegistry(
        lifecycle_path,
        activation_verifier=lambda _strategy, _proof: None,
        shadow_verifier=lambda _strategy, _proof: None,
    )
    strategy = FollowupStrategy("SPY", "spy_007_trend_pullback")
    registry.initialize_cutover(
        (strategy,),
        occurred_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )
    registry.register_shadow_strategy(
        strategy,
        proof=_shadow_proof("shadow-spy-007"),
        occurred_at=datetime(2026, 8, 6, 13, 0, tzinfo=UTC),
        reason="historical screen passed",
    )
    registry.activate_strategy(
        strategy,
        proof=FollowupActivationProof(
            shadow_id="shadow-spy-007",
            qualification_event_id="activation-evaluation:shadow-spy-007:2027-08-07",
            result_fingerprint="a" * 64,
            parity_digest="b" * 64,
        ),
        occurred_at=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        reason="prospective qualification passed",
    )
    registry.set_no_new_entry(
        False,
        occurred_at=datetime(2026, 8, 8, 12, 0, tzinfo=UTC),
        reason="controlled activation",
    )
    definition = {
        "ticker": "SPY",
        "experiment_name": strategy.experiment_name,
        "label": "SPY-007",
        "has_trailing_stop": False,
    }
    captured: dict[str, object] = {}

    def fake_run(_strategy_info, _today, **kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr("trading.followup.STRATEGIES", [definition])
    monkeypatch.setattr("trading.followup._run_single_strategy", fake_run)
    monkeypatch.setattr(
        "trading.followup._result_authorization",
        lambda _name: (True, "result-spy-007-snapshot-1", "a" * 64),
    )
    monkeypatch.setattr(
        "trading.followup.ManualLedgerStore.reconciliation_is_current",
        lambda *_args, **_kwargs: True,
    )

    run_followup(
        ledger_path=store.path,
        reconciliation_path=tmp_path / "reconciliation.json",
        lifecycle_path=lifecycle_path,
    )

    assert captured["lifecycle"] is StrategyLifecycle.ACTIVE
    assert captured["no_new_entry"] is False
    assert captured["result_valid"] is True
    assert captured["result_identity"] == "result-spy-007-snapshot-1"
    assert captured["broker_reconciled"] is True


def test_replacement_keeps_actual_position_attached_to_retiring_strategy(
    make_manual_ledger,
    monkeypatch,
    tmp_path,
) -> None:
    store = make_manual_ledger(
        path=tmp_path / "ledger.csv",
        initialized_at=datetime(2026, 8, 4, 12, 0, tzinfo=UTC),
    )
    context = _authorization(
        StrategyLifecycle.ACTIVE,
        ledger_accounting_hash=store.verify().accounting_hash,
    )
    entry = _print_manual_strategy_orders(
        {"ticker": "SPY", "experiment_name": "spy_007_trend_pullback"},
        _config(),
        store,
        store.verify(),
        latest_date=pd.Timestamp("2026-08-05"),
        latest_close=Decimal("10"),
        t_day=pd.Timestamp("2026-08-06"),
        today=pd.Timestamp("2026-08-05"),
        frame=_frame(),
        allow_new_entries=True,
        authorization_context=context,
    )
    store.record_fill(
        proposal_id=entry[0]["proposal_id"],
        sleeve_id="SPY",
        instrument="SPY",
        side="BUY",
        quantity=Decimal("7"),
        price=Decimal("11.23"),
        occurred_at=datetime.now(UTC) + timedelta(seconds=1),
    )

    lifecycle_path = tmp_path / "lifecycle.json"
    registry = FollowupLifecycleRegistry(
        lifecycle_path,
        shadow_verifier=lambda _strategy, _proof: None,
        actual_position_resolver=lambda _strategy: True,
        outstanding_entry_resolver=lambda _strategy: False,
        ledger_head_resolver=lambda: store.verify().head_hash,
    )
    old = FollowupStrategy("SPY", "spy_007_trend_pullback")
    replacement = FollowupStrategy("SPY", "spy_008_replacement")
    registry.initialize_cutover(
        (old,),
        occurred_at=datetime(2026, 8, 6, 12, 0, tzinfo=UTC),
    )
    registry.retire_strategy(
        old,
        occurred_at=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        reason="replacement selected",
    )
    registry.register_shadow_strategy(
        replacement,
        proof=_shadow_proof("shadow-spy-008"),
        occurred_at=datetime(2026, 8, 7, 13, 0, tzinfo=UTC),
        reason="historical screen passed",
    )
    selected = {
        "ticker": "SPY",
        "experiment_name": replacement.experiment_name,
        "label": "SPY-008",
        "has_trailing_stop": False,
    }
    captured: dict[str, object] = {}

    def fake_run(strategy_info, _today, **kwargs):
        captured["strategy_info"] = strategy_info
        captured.update(kwargs)
        return []

    monkeypatch.setattr("trading.followup.STRATEGIES", [selected])
    monkeypatch.setattr("trading.followup._run_single_strategy", fake_run)
    monkeypatch.setattr(
        "trading.followup._result_authorization",
        lambda name: (True, f"result:{name}", "a" * 64),
    )
    monkeypatch.setattr(
        "trading.followup.ManualLedgerStore.reconciliation_is_current",
        lambda *_args, **_kwargs: True,
    )

    run_followup(
        ledger_path=store.path,
        reconciliation_path=tmp_path / "reconciliation.json",
        lifecycle_path=lifecycle_path,
    )

    assert captured["strategy_info"]["experiment_name"] == old.experiment_name
    assert captured["lifecycle"] is StrategyLifecycle.RETIRING
