from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pandas as pd

from trading.followup import _print_manual_strategy_orders


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


def test_repeated_followup_submission_is_idempotent_and_unconfirmed_buy_has_no_position(
    make_manual_ledger,
) -> None:
    store = make_manual_ledger(
        initialized_at=datetime(2026, 8, 4, 12, 0, tzinfo=UTC),
    )
    frame = _frame()
    definition = {"ticker": "SPY"}
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
