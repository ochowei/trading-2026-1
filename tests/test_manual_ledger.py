import csv
import io
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from trading.core.manual_ledger import (
    BROKER_COLUMNS,
    LEDGER_COLUMNS,
    LedgerConflictError,
    LedgerInitialization,
    LedgerIntegrityError,
    ManualLedgerStore,
    canonical_ledger_bytes,
    parse_ledger_bytes,
)
from trading.core.proposals import ProposalConflictError, ProposalTerms


def test_initialization_creates_equal_sleeves_and_deterministic_replay(tmp_path) -> None:
    path = tmp_path / "manual-execution-ledger.csv"
    initialization = LedgerInitialization.create(
        managed_capital=Decimal("100000.00"),
        universe=("SPY", "QQQ"),
        initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
        allocation_epoch="epoch-0001",
    )

    store = ManualLedgerStore(path)
    store.initialize(initialization)

    first = store.verify()
    second = store.verify()

    assert first.head_hash == second.head_hash
    assert first.managed_capital == Decimal("100000")
    assert first.universe == ("QQQ", "SPY")
    assert first.allocation_epoch == "epoch-0001"
    assert first.sleeve_cash == {"QQQ": Decimal("50000"), "SPY": Decimal("50000")}
    assert first.reserve_cash == Decimal("0")
    assert first.cash == Decimal("100000")
    assert first.positions == {}
    assert first.disposable_positions == {}
    assert first.cost_basis_by_position == {}

    store.initialize(initialization)
    assert store.verify().head_hash == first.head_hash


def test_proposal_id_is_stable_for_identical_identity_and_changes_by_role() -> None:
    first = ProposalTerms.create(
        sleeve_id="SPY",
        instrument="SPY",
        allocation_epoch="epoch-0001",
        signal_date=date(2026, 8, 4),
        trading_date=date(2026, 8, 5),
        action="BUY",
        position_id="new:2026-08-04",
        role="entry",
        quantity=Decimal("12.50000000"),
        order_type="MARKET",
        price=Decimal("600.25"),
    )
    retry = ProposalTerms.create(
        sleeve_id="SPY",
        instrument="SPY",
        allocation_epoch="epoch-0001",
        signal_date=date(2026, 8, 4),
        trading_date=date(2026, 8, 5),
        action="BUY",
        position_id="new:2026-08-04",
        role="entry",
        quantity=Decimal("12.50000000"),
        order_type="MARKET",
        price=Decimal("600.25"),
    )
    target = ProposalTerms.create(
        sleeve_id="SPY",
        instrument="SPY",
        allocation_epoch="epoch-0001",
        signal_date=date(2026, 8, 4),
        trading_date=date(2026, 8, 5),
        action="BUY",
        position_id="new:2026-08-04",
        role="target",
        quantity=Decimal("12.50000000"),
        order_type="MARKET",
        price=Decimal("600.25"),
    )

    assert first.proposal_id == retry.proposal_id
    assert first.proposal_id.startswith("proposal-")
    assert first.proposal_id != target.proposal_id


def test_confirmed_partial_fills_are_the_only_source_of_position_and_cash_changes(tmp_path) -> None:
    path = tmp_path / "manual-execution-ledger.csv"
    initialization = LedgerInitialization.create(
        managed_capital=Decimal("1000"),
        universe=("SPY",),
        initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
    )
    store = ManualLedgerStore(path)
    store.initialize(initialization)
    proposal = ProposalTerms.create(
        sleeve_id="SPY",
        instrument="SPY",
        allocation_epoch="epoch-0001",
        signal_date=date(2026, 8, 4),
        trading_date=date(2026, 8, 5),
        action="BUY",
        position_id="new:2026-08-04",
        role="entry",
        quantity=Decimal("12"),
        order_type="MARKET",
        price=Decimal("10"),
    )

    store.record_submission(proposal, occurred_at=datetime(2026, 8, 5, 13, 0, tzinfo=UTC))
    before_fill = store.verify()
    assert before_fill.positions == {}
    assert before_fill.cash == Decimal("1000")

    store.record_fill(
        proposal_id=proposal.proposal_id,
        sleeve_id="SPY",
        instrument="SPY",
        side="BUY",
        quantity=Decimal("10"),
        price=Decimal("10.25"),
        fee=Decimal("0.50"),
        event_type="partial_fill",
        occurred_at=datetime(2026, 8, 5, 14, 0, tzinfo=UTC),
    )
    store.record_fill(
        proposal_id=proposal.proposal_id,
        sleeve_id="SPY",
        instrument="SPY",
        side="BUY",
        quantity=Decimal("2"),
        price=Decimal("10.50"),
        event_type="fill",
        occurred_at=datetime(2026, 8, 5, 15, 0, tzinfo=UTC),
    )

    replay = store.verify()
    position = replay.positions[("SPY", "SPY")]
    assert position.quantity == Decimal("12")
    assert position.cost_basis == Decimal("124")
    assert position.average_price == Decimal("10.29166666666666666666666667")
    assert replay.sleeve_cash["SPY"] == Decimal("876")
    assert replay.cash == Decimal("876")
    assert replay.proposals[proposal.proposal_id].filled_quantity == Decimal("12")
    assert replay.disposable_positions == {("SPY", "SPY"): Decimal("12")}
    assert replay.cost_basis_by_position == {("SPY", "SPY"): Decimal("124")}


def test_initialization_accepts_one_pass_universe_and_rejects_duplicates(tmp_path) -> None:
    initialization = LedgerInitialization.create(
        managed_capital=Decimal("1000"),
        universe=(symbol for symbol in ("SPY", "QQQ")),
        initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
    )
    assert initialization.universe == ("QQQ", "SPY")

    with pytest.raises(ValueError, match="duplicate"):
        LedgerInitialization.create(
            managed_capital=Decimal("1000"),
            universe=("SPY", "spy"),
            initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
        )


def test_cancellation_cash_events_and_unrelated_manual_trade_are_separate(
    make_manual_ledger,
) -> None:
    store = make_manual_ledger(
        initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
    )
    store.record_cash_event(
        "deposit", Decimal("100"), occurred_at=datetime(2026, 8, 5, 12, 1, tzinfo=UTC)
    )
    store.record_cash_event(
        "fee", Decimal("5"), occurred_at=datetime(2026, 8, 5, 12, 2, tzinfo=UTC)
    )
    store.record_cash_event(
        "withdrawal", Decimal("10"), occurred_at=datetime(2026, 8, 5, 12, 3, tzinfo=UTC)
    )
    proposal = ProposalTerms.create(
        sleeve_id="SPY",
        instrument="SPY",
        allocation_epoch="epoch-0001",
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        action="BUY",
        position_id="new:2026-08-05",
        role="entry",
        quantity=Decimal("5"),
        order_type="MARKET",
        price=Decimal("10"),
    )
    store.record_submission(proposal, occurred_at=datetime(2026, 8, 5, 12, 4, tzinfo=UTC))
    store.record_cancellation(
        proposal.proposal_id, occurred_at=datetime(2026, 8, 5, 12, 5, tzinfo=UTC)
    )
    store.record_manual_adjustment(
        classification="unrelated_manual",
        instrument="SPY",
        side="BUY",
        quantity=Decimal("100"),
        price=Decimal("1"),
        occurred_at=datetime(2026, 8, 5, 12, 6, tzinfo=UTC),
    )

    replay = store.verify()
    assert replay.cash == Decimal("1085")
    assert replay.positions == {}
    assert replay.proposals[proposal.proposal_id].status == "cancelled"
    assert sum(event.event_type == "manual_adjustment" for event in replay.events) == 1

    with pytest.raises(LedgerIntegrityError, match="cancelled proposal"):
        store.record_fill(
            proposal_id=proposal.proposal_id,
            sleeve_id="SPY",
            instrument="SPY",
            side="BUY",
            quantity=Decimal("1"),
            price=Decimal("10"),
            occurred_at=datetime(2026, 8, 5, 12, 7, tzinfo=UTC),
        )


def test_correction_appends_without_rewriting_original_and_replays_replacement(tmp_path) -> None:
    path = tmp_path / "ledger.csv"
    store = ManualLedgerStore(path)
    store.initialize(
        LedgerInitialization.create(
            managed_capital=Decimal("1000"),
            universe=("SPY",),
            initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
        )
    )
    proposal = ProposalTerms.create(
        sleeve_id="SPY",
        instrument="SPY",
        allocation_epoch="epoch-0001",
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        action="BUY",
        position_id="new:2026-08-05",
        role="entry",
        quantity=Decimal("10"),
        order_type="MARKET",
        price=Decimal("10"),
    )
    store.record_submission(proposal, occurred_at=datetime(2026, 8, 5, 12, 1, tzinfo=UTC))
    fill = store.record_fill(
        proposal_id=proposal.proposal_id,
        sleeve_id="SPY",
        instrument="SPY",
        side="BUY",
        quantity=Decimal("10"),
        price=Decimal("10"),
        occurred_at=datetime(2026, 8, 5, 12, 2, tzinfo=UTC),
    )
    original_bytes = path.read_bytes()

    correction = store.record_correction(
        fill.event_id,
        {"price": Decimal("11")},
        occurred_at=datetime(2026, 8, 5, 12, 3, tzinfo=UTC),
    )

    assert fill.event_id.encode() in original_bytes
    assert correction.correction_of == fill.event_id
    assert path.read_bytes() != original_bytes
    events = store.read_events()
    assert [event.event_id for event in events[:3]] == [
        events[0].event_id,
        events[1].event_id,
        fill.event_id,
    ]
    assert events[-1].event_type == "correction"
    replay = store.verify()
    assert replay.positions[("SPY", "SPY")].average_price == Decimal("11")
    assert replay.sleeve_cash["SPY"] == Decimal("890")
    with pytest.raises(LedgerConflictError, match="correction events"):
        store.record_correction(
            correction.event_id,
            {"price": Decimal("12")},
            occurred_at=datetime(2026, 8, 5, 12, 4, tzinfo=UTC),
        )


def test_reconciliation_is_bound_to_ledger_head_and_broker_export_bytes(tmp_path) -> None:
    ledger_path = tmp_path / "ledger.csv"
    broker_path = tmp_path / "broker.csv"
    report_path = tmp_path / "reconciliation.json"
    store = ManualLedgerStore(ledger_path)
    store.initialize(
        LedgerInitialization.create(
            managed_capital=Decimal("1000"),
            universe=("SPY",),
            initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
        )
    )
    broker_path.write_text(
        ",".join(BROKER_COLUMNS) + "\n" + "cash,SPY,,,,1000\n",
        encoding="utf-8",
    )

    report = store.reconcile(broker_path, report_path)
    assert report.ok is True
    assert store.reconciliation_is_current(report_path, broker_path) is True

    store.record_manual_adjustment(
        classification="unrelated_manual",
        sleeve_id="SPY",
        instrument="SPY",
        side="BUY",
        quantity=Decimal("1"),
        price=Decimal("1"),
        occurred_at=datetime(2026, 8, 5, 12, 1, tzinfo=UTC),
    )
    assert store.reconciliation_is_current(report_path, broker_path) is True

    store.record_cash_event(
        "deposit", Decimal("1"), occurred_at=datetime(2026, 8, 5, 12, 1, tzinfo=UTC)
    )
    store.record_cash_event(
        "deposit", Decimal("2"), occurred_at=datetime(2026, 8, 5, 12, 2, tzinfo=UTC)
    )
    assert store.reconciliation_is_current(report_path, broker_path) is False
    broker_path.write_text(",".join(BROKER_COLUMNS) + "\n" + "cash,SPY,,,,999\n", encoding="utf-8")
    assert store.reconciliation_is_current(report_path, broker_path) is False


def test_managed_manual_adjustment_can_seed_actual_position_without_proposal(tmp_path) -> None:
    store = ManualLedgerStore(tmp_path / "ledger.csv")
    store.initialize(
        LedgerInitialization.create(
            managed_capital=Decimal("1000"),
            universe=("SPY",),
            initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
        )
    )
    store.record_manual_adjustment(
        classification="managed",
        sleeve_id="SPY",
        instrument="SPY",
        side="BUY",
        quantity=Decimal("3"),
        price=Decimal("10"),
        position_id="legacy-position-1",
        occurred_at=datetime(2026, 8, 5, 12, 1, tzinfo=UTC),
    )

    replay = store.verify()
    position = replay.positions[("SPY", "SPY")]
    assert position.position_id == "legacy-position-1"
    assert position.quantity == Decimal("3")
    assert position.cost_basis == Decimal("30")
    assert replay.sleeve_cash["SPY"] == Decimal("970")


def test_history_edits_deletions_and_non_monotonic_events_fail_closed(tmp_path) -> None:
    path = tmp_path / "ledger.csv"
    store = ManualLedgerStore(path)
    store.initialize(
        LedgerInitialization.create(
            managed_capital=Decimal("1000"),
            universe=("SPY",),
            initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
        )
    )
    store.record_cash_event(
        "deposit", Decimal("1"), occurred_at=datetime(2026, 8, 5, 12, 1, tzinfo=UTC)
    )
    store.record_cash_event(
        "deposit", Decimal("2"), occurred_at=datetime(2026, 8, 5, 12, 2, tzinfo=UTC)
    )
    original = path.read_text(encoding="utf-8")
    edited = original.replace(",deposit,", ",withdrawal,", 1)
    path.write_text(edited, encoding="utf-8")
    with pytest.raises(LedgerIntegrityError):
        store.verify()

    path.write_text(original, encoding="utf-8")
    lines = original.splitlines(keepends=True)
    path.write_text("".join(lines[:-1]), encoding="utf-8")
    with pytest.raises(LedgerIntegrityError, match="checkpoint"):
        store.verify()

    path.write_text(original, encoding="utf-8")
    path.write_text("".join((*lines[:2], *lines[3:])), encoding="utf-8")
    with pytest.raises(LedgerIntegrityError):
        store.verify()

    path.write_text(original, encoding="utf-8")
    with pytest.raises(LedgerIntegrityError, match="timestamps"):
        store.record_cash_event(
            "withdrawal", Decimal("1"), occurred_at=datetime(2026, 8, 5, 11, 59, tzinfo=UTC)
        )

    with pytest.raises(TypeError, match="decimal string"):
        store.record_cash_event("deposit", 1.5)


def test_noncanonical_decimal_and_metadata_rows_fail_before_replay(tmp_path) -> None:
    store = ManualLedgerStore(tmp_path / "ledger.csv")
    store.initialize(
        LedgerInitialization.create(
            managed_capital=Decimal("1000"),
            universe=("SPY",),
            initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
        )
    )
    store.record_cash_event(
        "deposit", Decimal("1"), occurred_at=datetime(2026, 8, 5, 12, 1, tzinfo=UTC)
    )
    events = store.read_events()

    def serialize_with_change(field: str, value: str) -> bytes:
        output = io.StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=LEDGER_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for index, event in enumerate(events):
            row = event.to_row()
            if index == 1:
                row[field] = value
            writer.writerow(row)
        return output.getvalue().encode("utf-8")

    with pytest.raises(LedgerIntegrityError, match="canonical fields"):
        parse_ledger_bytes(serialize_with_change("amount", "1.0"))
    with pytest.raises(LedgerIntegrityError, match="canonical fields"):
        parse_ledger_bytes(serialize_with_change("metadata", "{ }"))
    assert canonical_ledger_bytes(events) == (tmp_path / "ledger.csv").read_bytes()


def test_submission_is_idempotent_but_changed_terms_conflict(tmp_path) -> None:
    store = ManualLedgerStore(tmp_path / "ledger.csv")
    store.initialize(
        LedgerInitialization.create(
            managed_capital=Decimal("1000"),
            universe=("SPY",),
            initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
        )
    )
    proposal = ProposalTerms.create(
        sleeve_id="SPY",
        instrument="SPY",
        allocation_epoch="epoch-0001",
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        action="BUY",
        position_id="new:2026-08-05",
        role="entry",
        quantity=Decimal("5"),
        order_type="MARKET",
        price=Decimal("10"),
    )
    first = store.record_submission(proposal, occurred_at=datetime(2026, 8, 5, 12, 1, tzinfo=UTC))
    retry = store.record_submission(proposal, occurred_at=datetime(2026, 8, 5, 12, 2, tzinfo=UTC))
    assert retry.event_id == first.event_id
    assert len(store.verify().events) == 2

    changed = ProposalTerms.create(
        sleeve_id="SPY",
        instrument="SPY",
        allocation_epoch="epoch-0001",
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        action="BUY",
        position_id="new:2026-08-05",
        role="entry",
        quantity=Decimal("6"),
        order_type="MARKET",
        price=Decimal("10"),
    )
    assert changed.proposal_id == proposal.proposal_id
    with pytest.raises(ProposalConflictError, match="different terms"):
        store.record_submission(changed)


def test_duplicate_broker_event_is_idempotent_and_changed_duplicate_conflicts(tmp_path) -> None:
    store = ManualLedgerStore(tmp_path / "ledger.csv")
    store.initialize(
        LedgerInitialization.create(
            managed_capital=Decimal("1000"),
            universe=("SPY",),
            initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
        )
    )
    proposal = ProposalTerms.create(
        sleeve_id="SPY",
        instrument="SPY",
        allocation_epoch="epoch-0001",
        signal_date=date(2026, 8, 5),
        trading_date=date(2026, 8, 6),
        action="BUY",
        position_id="position-1",
        role="entry",
        quantity=Decimal("2"),
        order_type="MARKET",
        price=Decimal("10"),
    )
    store.record_submission(proposal, occurred_at=datetime(2026, 8, 5, 12, 1, tzinfo=UTC))
    first = store.record_fill(
        proposal_id=proposal.proposal_id,
        sleeve_id="SPY",
        instrument="SPY",
        side="BUY",
        quantity=Decimal("2"),
        price=Decimal("10.25"),
        external_id="broker-fill-1",
        event_id="fill:first",
        occurred_at=datetime(2026, 8, 5, 12, 2, tzinfo=UTC),
    )
    retry = store.record_fill(
        proposal_id=proposal.proposal_id,
        sleeve_id="SPY",
        instrument="SPY",
        side="BUY",
        quantity=Decimal("2"),
        price=Decimal("10.25"),
        external_id="broker-fill-1",
        event_id="fill:retry",
        occurred_at=datetime(2026, 8, 5, 12, 2, tzinfo=UTC),
    )
    assert retry.event_id == first.event_id
    assert len(store.verify().events) == 3

    with pytest.raises(LedgerConflictError, match="external event"):
        store.record_fill(
            proposal_id=proposal.proposal_id,
            sleeve_id="SPY",
            instrument="SPY",
            side="BUY",
            quantity=Decimal("2"),
            price=Decimal("10.50"),
            external_id="broker-fill-1",
            event_id="fill:changed",
            occurred_at=datetime(2026, 8, 5, 12, 2, tzinfo=UTC),
        )


def test_export_and_import_verify_before_safe_publication(tmp_path) -> None:
    source_path = tmp_path / "ledger.csv"
    backup_path = tmp_path / "backup.csv"
    imported_path = tmp_path / "imported.csv"
    source = ManualLedgerStore(source_path)
    source.initialize(
        LedgerInitialization.create(
            managed_capital=Decimal("1000"),
            universe=("SPY",),
            initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
        )
    )
    source.record_cash_event(
        "deposit", Decimal("2"), occurred_at=datetime(2026, 8, 5, 12, 1, tzinfo=UTC)
    )

    source.export(backup_path)
    imported = ManualLedgerStore(imported_path)
    imported.import_ledger(backup_path)
    assert imported.verify().head_hash == source.verify().head_hash
    imported.export(backup_path)

    backup_path.write_text(
        backup_path.read_text(encoding="utf-8").replace("deposit", "fee"), encoding="utf-8"
    )
    with pytest.raises(LedgerIntegrityError):
        imported.import_ledger(backup_path)


def test_import_rejects_an_export_with_truncated_tail_history(tmp_path) -> None:
    source = ManualLedgerStore(tmp_path / "ledger.csv")
    source.initialize(
        LedgerInitialization.create(
            managed_capital=Decimal("1000"),
            universe=("SPY",),
            initialized_at=datetime(2026, 8, 5, 12, 0, tzinfo=UTC),
        )
    )
    source.record_cash_event(
        "deposit",
        Decimal("2"),
        occurred_at=datetime(2026, 8, 5, 12, 1, tzinfo=UTC),
    )
    backup_path = source.export(tmp_path / "backup.csv")
    lines = backup_path.read_text(encoding="utf-8").splitlines(keepends=True)
    backup_path.write_text("".join(lines[:-1]), encoding="utf-8")
    imported_path = tmp_path / "imported.csv"

    with pytest.raises(LedgerIntegrityError, match="checkpoint"):
        ManualLedgerStore(imported_path).import_ledger(backup_path)

    assert not imported_path.exists()
