from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from trading.core.followup_proposals import build_manual_proposal_terms
from trading.core.manual_ledger import ManualLedgerStore
from trading.core.proposals import ProposalConflictError, ProposalTerms


def _store_with_position(store: ManualLedgerStore) -> ManualLedgerStore:
    entry = ProposalTerms.create(
        sleeve_id="SPY",
        instrument="SPY",
        allocation_epoch="epoch-0001",
        signal_date=date(2026, 8, 1),
        trading_date=date(2026, 8, 4),
        action="BUY",
        position_id="position-1",
        role="entry",
        quantity=Decimal("3"),
        order_type="MARKET",
        price=Decimal("12.50"),
    )
    store.record_submission(entry, occurred_at=datetime(2026, 8, 4, 12, 0, tzinfo=UTC))
    store.record_fill(
        proposal_id=entry.proposal_id,
        sleeve_id="SPY",
        instrument="SPY",
        side="BUY",
        quantity=Decimal("3"),
        price=Decimal("12.50"),
        occurred_at=datetime(2026, 8, 4, 13, 0, tzinfo=UTC),
    )
    return store


def test_new_buy_quantity_uses_only_actual_sleeve_cash(make_manual_ledger) -> None:
    store = make_manual_ledger()
    terms = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=True,
        signal_date=date(2026, 8, 4),
        trading_date=date(2026, 8, 5),
        estimated_entry=Decimal("12.50"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=0,
    )
    assert len(terms) == 1
    assert terms[0].action == "BUY"
    assert terms[0].quantity == Decimal("80")
    assert terms[0].target_price is None
    assert terms[0].stop_price is None


def test_unfilled_entry_blocks_a_different_later_buy_proposal(make_manual_ledger) -> None:
    store = make_manual_ledger()
    first = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=True,
        signal_date=date(2026, 8, 4),
        trading_date=date(2026, 8, 5),
        estimated_entry=Decimal("12.50"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=0,
    )
    store.record_submission(first[0], occurred_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC))

    later = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=True,
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        estimated_entry=Decimal("10"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=0,
    )

    assert later == ()

    store.record_cancellation(
        first[0].proposal_id,
        occurred_at=datetime(2026, 8, 6, 15, 0, tzinfo=UTC),
    )
    after_cancellation = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=True,
        signal_date=date(2026, 8, 7),
        trading_date=date(2026, 8, 10),
        estimated_entry=Decimal("10"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=0,
    )
    assert len(after_cancellation) == 1
    assert after_cancellation[0].action == "BUY"


def test_changed_gtc_stop_conflicts_until_cancelled_then_gets_replacement(
    make_manual_ledger,
) -> None:
    store = _store_with_position(make_manual_ledger())
    initial = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=False,
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        estimated_entry=Decimal("999"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=1,
    )
    original = next(term for term in initial if term.role == "stop")
    store.record_submission(original, occurred_at=datetime(2026, 8, 5, 14, 0, tzinfo=UTC))

    changed = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=False,
        signal_date=date(2026, 8, 6),
        trading_date=date(2026, 8, 7),
        estimated_entry=Decimal("999"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=2,
        trailing_high=Decimal("14"),
        trail_activation_pct=Decimal("0.01"),
        trail_distance_pct=Decimal("0.01"),
    )
    changed_stop = next(term for term in changed if term.role == "stop")
    assert changed_stop.proposal_id == original.proposal_id
    with pytest.raises(ProposalConflictError, match="different terms"):
        store.record_submission(changed_stop)

    store.record_cancellation(
        original.proposal_id,
        occurred_at=datetime(2026, 8, 6, 14, 0, tzinfo=UTC),
    )
    replacement = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=False,
        signal_date=date(2026, 8, 6),
        trading_date=date(2026, 8, 7),
        estimated_entry=Decimal("999"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=2,
        trailing_high=Decimal("14"),
        trail_activation_pct=Decimal("0.01"),
        trail_distance_pct=Decimal("0.01"),
    )
    replacement_stop = next(term for term in replacement if term.role == "stop")
    assert replacement_stop.proposal_id != original.proposal_id
    assert replacement_stop.price == Decimal("13.86")


def test_partial_entry_blocks_next_buy_until_remainder_is_cancelled(make_manual_ledger) -> None:
    store = make_manual_ledger()
    entry = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=True,
        signal_date=date(2026, 8, 4),
        trading_date=date(2026, 8, 5),
        estimated_entry=Decimal("12.50"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=0,
    )[0]
    store.record_submission(entry, occurred_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC))
    store.record_fill(
        proposal_id=entry.proposal_id,
        sleeve_id="SPY",
        instrument="SPY",
        side="BUY",
        quantity=Decimal("1"),
        price=Decimal("12.50"),
        event_type="partial_fill",
        occurred_at=datetime(2026, 8, 5, 13, 0, tzinfo=UTC),
    )
    exits = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=True,
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        estimated_entry=Decimal("10"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=1,
    )
    assert {term.action for term in exits} == {"SELL"}
    assert {term.quantity for term in exits} == {Decimal("1")}
    target = next(term for term in exits if term.role == "target")
    store.record_submission(target, occurred_at=datetime(2026, 8, 5, 14, 0, tzinfo=UTC))
    store.record_fill(
        proposal_id=target.proposal_id,
        sleeve_id="SPY",
        instrument="SPY",
        side="SELL",
        quantity=Decimal("1"),
        price=Decimal("13.75"),
        occurred_at=datetime(2026, 8, 6, 14, 0, tzinfo=UTC),
    )

    blocked = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=True,
        signal_date=date(2026, 8, 7),
        trading_date=date(2026, 8, 10),
        estimated_entry=Decimal("10"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=0,
    )
    assert blocked == ()

    store.record_cancellation(
        entry.proposal_id,
        occurred_at=datetime(2026, 8, 6, 15, 0, tzinfo=UTC),
    )
    allowed = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=True,
        signal_date=date(2026, 8, 7),
        trading_date=date(2026, 8, 10),
        estimated_entry=Decimal("10"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=0,
    )
    assert len(allowed) == 1
    assert allowed[0].action == "BUY"


def test_exit_terms_use_confirmed_fill_price_and_quantity(make_manual_ledger) -> None:
    store = _store_with_position(make_manual_ledger())
    terms = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=True,
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        estimated_entry=Decimal("999"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=1,
    )
    assert {term.role for term in terms} == {"target", "stop"}
    assert all(term.action == "SELL" for term in terms)
    assert all(term.quantity == Decimal("3") for term in terms)
    assert next(term for term in terms if term.role == "target").price == Decimal("13.750")
    stop = next(term for term in terms if term.role == "stop")
    assert stop.price == Decimal("11.8750")
    assert stop.duration == "GTC"
    assert stop.expiry_date is None


def test_outstanding_gtc_stop_reuses_its_proposal_id_on_later_runs(make_manual_ledger) -> None:
    store = _store_with_position(make_manual_ledger())
    first = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=False,
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        estimated_entry=Decimal("999"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=1,
    )
    first_stop = next(term for term in first if term.role == "stop")
    store.record_submission(first_stop, occurred_at=datetime(2026, 8, 5, 14, 0, tzinfo=UTC))

    later = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=False,
        signal_date=date(2026, 8, 6),
        trading_date=date(2026, 8, 7),
        estimated_entry=Decimal("999"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=2,
    )
    later_stop = next(term for term in later if term.role == "stop")

    assert later_stop.proposal_id == first_stop.proposal_id
    assert later_stop.trading_date == date(2026, 8, 6)
    assert later_stop.duration == "GTC"


@pytest.mark.parametrize("held_trading_days", [2, 20])
def test_partially_filled_gtc_stop_reports_its_remaining_active_quantity(
    make_manual_ledger,
    held_trading_days: int,
) -> None:
    store = _store_with_position(make_manual_ledger())
    initial = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=False,
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        estimated_entry=Decimal("999"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=1,
    )
    submitted_stop = next(term for term in initial if term.role == "stop")
    store.record_submission(
        submitted_stop,
        occurred_at=datetime(2026, 8, 5, 14, 0, tzinfo=UTC),
    )
    store.record_fill(
        proposal_id=submitted_stop.proposal_id,
        sleeve_id="SPY",
        instrument="SPY",
        side="SELL",
        quantity=Decimal("1"),
        price=Decimal("11.875"),
        event_type="partial_fill",
        occurred_at=datetime(2026, 8, 6, 14, 0, tzinfo=UTC),
    )

    later = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=False,
        signal_date=date(2026, 8, 6),
        trading_date=date(2026, 8, 7),
        estimated_entry=Decimal("999"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=held_trading_days,
    )

    active_stop = next(term for term in later if term.role == "stop")
    assert active_stop.proposal_id == submitted_stop.proposal_id
    assert active_stop.quantity == Decimal("2")
    event_count = len(store.verify().events)
    store.record_submission(active_stop)
    assert len(store.verify().events) == event_count


def test_expiry_waits_for_outstanding_gtc_stop_cancellation(make_manual_ledger) -> None:
    store = _store_with_position(make_manual_ledger())
    initial = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=False,
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        estimated_entry=Decimal("999"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=1,
    )
    stop = next(term for term in initial if term.role == "stop")
    store.record_submission(stop, occurred_at=datetime(2026, 8, 5, 14, 0, tzinfo=UTC))

    at_expiry = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=False,
        signal_date=date(2026, 8, 25),
        trading_date=date(2026, 8, 26),
        estimated_entry=Decimal("999"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=20,
    )

    assert len(at_expiry) == 1
    assert at_expiry[0].role == "stop"
    assert at_expiry[0].proposal_id == stop.proposal_id


def test_closed_position_with_outstanding_gtc_stop_blocks_new_buy(make_manual_ledger) -> None:
    store = _store_with_position(make_manual_ledger())
    exits = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=False,
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        estimated_entry=Decimal("999"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=1,
    )
    target = next(term for term in exits if term.role == "target")
    stop = next(term for term in exits if term.role == "stop")
    store.record_submission(target, occurred_at=datetime(2026, 8, 5, 14, 0, tzinfo=UTC))
    store.record_submission(stop, occurred_at=datetime(2026, 8, 5, 14, 1, tzinfo=UTC))
    store.record_fill(
        proposal_id=target.proposal_id,
        sleeve_id="SPY",
        instrument="SPY",
        side="SELL",
        quantity=Decimal("3"),
        price=Decimal("13.75"),
        occurred_at=datetime(2026, 8, 6, 14, 0, tzinfo=UTC),
    )

    later = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=True,
        signal_date=date(2026, 8, 7),
        trading_date=date(2026, 8, 10),
        estimated_entry=Decimal("10"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=0,
    )

    assert later == ()


def test_expiry_proposal_is_market_sell_for_actual_quantity(make_manual_ledger) -> None:
    store = _store_with_position(make_manual_ledger())
    terms = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=False,
        signal_date=date(2026, 8, 25),
        trading_date=date(2026, 8, 26),
        estimated_entry=Decimal("999"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=20,
    )
    assert len(terms) == 1
    assert terms[0].role == "expiry"
    assert terms[0].order_type == "MARKET"
    assert terms[0].quantity == Decimal("3")


def test_trailing_stop_uses_actual_average_price_and_hold_high(make_manual_ledger) -> None:
    store = _store_with_position(make_manual_ledger())
    terms = build_manual_proposal_terms(
        store.verify(),
        sleeve_id="SPY",
        instrument="SPY",
        signal_today=False,
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        estimated_entry=Decimal("999"),
        profit_target=Decimal("0.10"),
        stop_loss=Decimal("-0.05"),
        holding_days=20,
        held_trading_days=1,
        trailing_high=Decimal("13.00"),
        trail_activation_pct=Decimal("0.01"),
        trail_distance_pct=Decimal("0.01"),
    )
    stop = next(term for term in terms if term.role == "stop")
    assert stop.price == Decimal("12.8700")
