"""Append-only, hash-chained manual execution ledger primitives.

The ledger is deliberately local and CSV-backed.  It is the authority for actual
manual positions; backtest output and unconfirmed proposals are never projected as
positions here.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import ROUND_DOWN, Decimal
from enum import StrEnum
from pathlib import Path

from trading.core.accounting import (
    canonical_json_bytes,
    decimal_text,
    parse_timestamp,
    timestamp_text,
    to_decimal,
)
from trading.core.broker_reconciliation import (
    BROKER_COLUMNS as BROKER_COLUMNS,
)
from trading.core.broker_reconciliation import (
    BrokerExportError,
    compare_broker_snapshot,
    read_broker_export,
)
from trading.core.ledger_csv import (
    CanonicalCsvError,
    canonical_csv_bytes,
    parse_canonical_csv_bytes,
)
from trading.core.ledger_storage import FileLockTimeout, atomic_write, locked_file
from trading.core.proposals import ProposalConflictError, ProposalTerms

LEDGER_SCHEMA_VERSION = 1
GENESIS_HASH = "0" * 64
SLEEVE_QUANTUM = Decimal("0.00000001")
FILL_EVENT_TYPES = frozenset({"fill", "partial_fill"})
PROPOSAL_EVENT_TYPES = frozenset({"submission", *FILL_EVENT_TYPES, "cancellation"})
CASH_EVENT_TYPES = frozenset({"fee", "deposit", "withdrawal"})
TRANSFER_EVENT_TYPES = frozenset({"deposit", "withdrawal"})
EVENT_TYPES = frozenset(
    {
        "initialization",
        "allocation_epoch",
        *PROPOSAL_EVENT_TYPES,
        *CASH_EVENT_TYPES,
        "manual_adjustment",
        "correction",
    }
)
RECORDABLE_EVENT_TYPES = EVENT_TYPES - {"initialization", "allocation_epoch"}
EVENT_CLASSIFICATIONS = {
    **{event_type: "proposal" for event_type in PROPOSAL_EVENT_TYPES},
    **{event_type: "managed" for event_type in CASH_EVENT_TYPES},
    "allocation_epoch": "managed",
}
LEDGER_COLUMNS = (
    "schema_version",
    "sequence",
    "event_id",
    "event_type",
    "occurred_at",
    "allocation_epoch",
    "sleeve_id",
    "instrument",
    "classification",
    "proposal_id",
    "position_id",
    "side",
    "quantity",
    "price",
    "amount",
    "fee",
    "currency",
    "order_type",
    "signal_date",
    "trading_date",
    "correction_of",
    "external_id",
    "metadata",
    "previous_hash",
    "event_hash",
)
RECONCILIATION_SCHEMA_VERSION = 1
ACCOUNTING_TOLERANCE = Decimal("0.00000001")


class LedgerError(RuntimeError):
    """Base class for malformed, conflicting, or unsafe ledger operations."""


class LedgerIntegrityError(LedgerError):
    """The CSV, hash chain, or replay invariants are not trustworthy."""


class LedgerConflictError(LedgerError):
    """An idempotent operation conflicts with already recorded history."""


class LedgerLockTimeout(TimeoutError, LedgerError):
    """A bounded append lock could not be acquired."""


class ProposalStatus(StrEnum):
    SUBMITTED = "submitted"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class LedgerInitialization:
    """The immutable starting capital and universe for one manual ledger."""

    managed_capital: Decimal
    universe: tuple[str, ...]
    initial_sleeve_capital: tuple[tuple[str, Decimal], ...]
    initial_reserve_cash: Decimal
    allocation_epoch: str
    initialized_at: datetime
    currency: str = "USD"

    @classmethod
    def create(
        cls,
        *,
        managed_capital: Decimal | int | str,
        universe: Sequence[str],
        initialized_at: datetime,
        allocation_epoch: str = "epoch-0001",
        currency: str = "USD",
    ) -> LedgerInitialization:
        capital = to_decimal(managed_capital, "managed_capital", allow_negative=False)
        if capital <= 0:
            raise ValueError("managed_capital must be greater than zero")
        raw_universe = tuple(universe)
        if any(not isinstance(symbol, str) or not symbol.strip() for symbol in raw_universe):
            raise ValueError("universe must contain non-empty instrument symbols")
        normalized_symbols = tuple(symbol.strip().upper() for symbol in raw_universe)
        if len(set(normalized_symbols)) != len(normalized_symbols):
            raise ValueError("universe must not contain duplicate instruments")
        symbols = tuple(sorted(normalized_symbols))
        if not symbols:
            raise ValueError("universe must contain at least one instrument")
        if not allocation_epoch.strip():
            raise ValueError("allocation_epoch must not be empty")
        if not currency.strip():
            raise ValueError("currency must not be empty")
        if initialized_at.tzinfo is None or initialized_at.utcoffset() is None:
            raise ValueError("initialized_at must be timezone-aware")

        sleeve = (capital / Decimal(len(symbols))).quantize(SLEEVE_QUANTUM, rounding=ROUND_DOWN)
        sleeve_capital = tuple((symbol, sleeve) for symbol in symbols)
        reserve = capital - sleeve * Decimal(len(symbols))
        return cls(
            managed_capital=capital,
            universe=symbols,
            initial_sleeve_capital=sleeve_capital,
            initial_reserve_cash=reserve,
            allocation_epoch=allocation_epoch.strip(),
            initialized_at=initialized_at.astimezone(UTC),
            currency=currency.strip().upper(),
        )

    @property
    def sleeve_capital(self) -> dict[str, Decimal]:
        """Return a defensive mapping of the first allocation epoch."""
        return dict(self.initial_sleeve_capital)

    def metadata(self) -> dict[str, object]:
        return {
            "allocation_epoch": self.allocation_epoch,
            "currency": self.currency,
            "initial_reserve_cash": decimal_text(self.initial_reserve_cash),
            "initial_sleeve_capital": {
                symbol: decimal_text(amount) for symbol, amount in self.initial_sleeve_capital
            },
            "managed_capital": decimal_text(self.managed_capital),
            "universe": list(self.universe),
        }


@dataclass(frozen=True)
class LedgerAllocationEpoch:
    """One explicit flat-ledger universe and sleeve-capital assignment."""

    allocation_epoch: str
    sleeve_capital_items: tuple[tuple[str, Decimal], ...]
    reserve_cash: Decimal
    occurred_at: datetime

    @classmethod
    def create(
        cls,
        *,
        allocation_epoch: str,
        sleeve_capital: Mapping[str, Decimal | int | str],
        reserve_cash: Decimal | int | str = Decimal("0"),
        occurred_at: datetime,
    ) -> LedgerAllocationEpoch:
        epoch = allocation_epoch.strip()
        if not epoch:
            raise ValueError("allocation_epoch must not be empty")
        if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")
        normalized: dict[str, Decimal] = {}
        for raw_symbol, raw_amount in sleeve_capital.items():
            if not isinstance(raw_symbol, str) or not raw_symbol.strip():
                raise ValueError("sleeve symbols must be non-empty strings")
            symbol = raw_symbol.strip().upper()
            if symbol in normalized:
                raise ValueError(f"duplicate normalized sleeve symbol: {symbol}")
            amount = to_decimal(raw_amount, f"sleeve capital {symbol}", allow_negative=False)
            if amount <= 0:
                raise ValueError("sleeve capital must be greater than zero")
            normalized[symbol] = amount
        if not normalized:
            raise ValueError("allocation epoch requires at least one sleeve")
        reserve = to_decimal(reserve_cash, "reserve_cash", allow_negative=False)
        return cls(
            allocation_epoch=epoch,
            sleeve_capital_items=tuple(sorted(normalized.items())),
            reserve_cash=reserve,
            occurred_at=occurred_at.astimezone(UTC),
        )

    @property
    def sleeve_capital(self) -> dict[str, Decimal]:
        return dict(self.sleeve_capital_items)

    @property
    def universe(self) -> tuple[str, ...]:
        return tuple(symbol for symbol, _ in self.sleeve_capital_items)

    @property
    def total_cash(self) -> Decimal:
        return self.reserve_cash + sum(self.sleeve_capital.values(), Decimal("0"))

    def metadata(self) -> dict[str, object]:
        return {
            "allocation_epoch": self.allocation_epoch,
            "reserve_cash": decimal_text(self.reserve_cash),
            "sleeve_capital": {
                symbol: decimal_text(amount) for symbol, amount in self.sleeve_capital_items
            },
            "universe": list(self.universe),
        }


@dataclass(frozen=True)
class LedgerEvent:
    """One canonical event row, including its chain identity."""

    event_id: str
    event_type: str
    occurred_at: datetime
    sequence: int = 0
    allocation_epoch: str = ""
    sleeve_id: str = ""
    instrument: str = ""
    classification: str = ""
    proposal_id: str = ""
    position_id: str = ""
    side: str = ""
    quantity: str = ""
    price: str = ""
    amount: str = ""
    fee: str = ""
    currency: str = "USD"
    order_type: str = ""
    signal_date: str = ""
    trading_date: str = ""
    correction_of: str = ""
    external_id: str = ""
    metadata: str = "{}"
    previous_hash: str = GENESIS_HASH
    event_hash: str = ""

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id must not be empty")
        if self.event_type not in EVENT_TYPES:
            raise ValueError(f"unsupported event_type: {self.event_type}")
        if self.sequence < 0:
            raise ValueError("sequence must not be negative")
        normalized_timestamp = parse_timestamp(timestamp_text(self.occurred_at), "occurred_at")
        object.__setattr__(self, "occurred_at", normalized_timestamp)
        if not isinstance(self.metadata, str):
            raise ValueError("metadata must be a canonical JSON object")
        try:
            metadata = json.loads(self.metadata)
        except json.JSONDecodeError as exc:
            raise ValueError("metadata must contain valid JSON") from exc
        if not isinstance(metadata, dict):
            raise ValueError("metadata must contain a JSON object")
        canonical_metadata = json.dumps(
            metadata,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        if self.metadata != canonical_metadata:
            raise ValueError("metadata must use canonical JSON serialization")
        for field_name in ("quantity", "price", "amount", "fee"):
            value = getattr(self, field_name)
            if value:
                if not isinstance(value, str):
                    raise ValueError(f"{field_name} must be a canonical decimal string")
                if decimal_text(value, field_name) != value:
                    raise ValueError(f"{field_name} must be a canonical decimal string")

    @classmethod
    def initialization(cls, initialization: LedgerInitialization) -> LedgerEvent:
        return cls(
            event_id=f"initialization:{initialization.allocation_epoch}",
            event_type="initialization",
            occurred_at=initialization.initialized_at,
            allocation_epoch=initialization.allocation_epoch,
            amount=decimal_text(initialization.managed_capital),
            currency=initialization.currency,
            metadata=json.dumps(
                initialization.metadata(),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ),
        )

    def payload(self) -> dict[str, str]:
        """Return the exact hash payload, excluding only the derived event hash."""
        row = self.to_row()
        row.pop("event_hash")
        return row

    def to_row(self) -> dict[str, str]:
        return {
            "schema_version": str(LEDGER_SCHEMA_VERSION),
            "sequence": str(self.sequence),
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": timestamp_text(self.occurred_at),
            "allocation_epoch": self.allocation_epoch,
            "sleeve_id": self.sleeve_id,
            "instrument": self.instrument,
            "classification": self.classification,
            "proposal_id": self.proposal_id,
            "position_id": self.position_id,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.price,
            "amount": self.amount,
            "fee": self.fee,
            "currency": self.currency,
            "order_type": self.order_type,
            "signal_date": self.signal_date,
            "trading_date": self.trading_date,
            "correction_of": self.correction_of,
            "external_id": self.external_id,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
            "event_hash": self.event_hash,
        }

    @classmethod
    def from_row(cls, row: Mapping[str, str]) -> LedgerEvent:
        if tuple(row) != LEDGER_COLUMNS:
            raise LedgerIntegrityError("ledger CSV has unexpected columns")
        try:
            schema_version = int(row["schema_version"])
            sequence = int(row["sequence"])
            occurred_at = parse_timestamp(row["occurred_at"], "occurred_at")
        except (KeyError, TypeError, ValueError) as exc:
            raise LedgerIntegrityError("ledger event has invalid schema fields") from exc
        if schema_version != LEDGER_SCHEMA_VERSION:
            raise LedgerIntegrityError(f"unsupported ledger schema version: {schema_version}")
        try:
            return cls(
                event_id=row["event_id"],
                event_type=row["event_type"],
                occurred_at=occurred_at,
                sequence=sequence,
                allocation_epoch=row["allocation_epoch"],
                sleeve_id=row["sleeve_id"],
                instrument=row["instrument"],
                classification=row["classification"],
                proposal_id=row["proposal_id"],
                position_id=row["position_id"],
                side=row["side"],
                quantity=row["quantity"],
                price=row["price"],
                amount=row["amount"],
                fee=row["fee"],
                currency=row["currency"],
                order_type=row["order_type"],
                signal_date=row["signal_date"],
                trading_date=row["trading_date"],
                correction_of=row["correction_of"],
                external_id=row["external_id"],
                metadata=row["metadata"],
                previous_hash=row["previous_hash"],
                event_hash=row["event_hash"],
            )
        except (TypeError, ValueError) as exc:
            raise LedgerIntegrityError("ledger event has invalid canonical fields") from exc


@dataclass(frozen=True)
class LedgerPosition:
    """A position reconstructed from confirmed managed fills."""

    sleeve_id: str
    instrument: str
    position_id: str
    quantity: Decimal
    cost_basis: Decimal
    average_price: Decimal
    opened_at: datetime
    entry_proposal_id: str = ""


@dataclass
class LedgerProposal:
    """Replay state for one submitted proposal."""

    terms: ProposalTerms
    submission_event_id: str
    authorization: dict[str, object] = field(default_factory=dict)
    filled_quantity: Decimal = Decimal("0")
    fill_event_ids: list[str] = field(default_factory=list)
    cancelled: bool = False

    @property
    def status(self) -> ProposalStatus:
        if self.cancelled:
            return ProposalStatus.CANCELLED
        if self.filled_quantity >= self.terms.quantity:
            return ProposalStatus.FILLED
        if self.filled_quantity > 0:
            return ProposalStatus.PARTIAL
        return ProposalStatus.SUBMITTED

    @property
    def is_outstanding(self) -> bool:
        return self.status in {ProposalStatus.SUBMITTED, ProposalStatus.PARTIAL}

    @property
    def is_gtc_exit(self) -> bool:
        return (
            self.is_outstanding
            and self.terms.action == "SELL"
            and self.terms.duration.upper() == "GTC"
        )

    @property
    def remaining_quantity(self) -> Decimal:
        """Return the broker-active remainder of the immutable submission quantity."""
        return self.terms.quantity - self.filled_quantity

    def matches_active_remainder(self, proposal: ProposalTerms) -> bool:
        """Accept a partial GTC order projection without weakening term conflicts."""
        if self.status is not ProposalStatus.PARTIAL or not self.is_gtc_exit:
            return False
        expected = self.terms.payload()
        expected["quantity"] = decimal_text(self.remaining_quantity, "quantity")
        return expected == proposal.payload()


@dataclass(frozen=True)
class LedgerReplay:
    """Deterministic read model produced only after chain and invariant checks."""

    initialization: LedgerInitialization
    allocation_epochs: tuple[LedgerAllocationEpoch, ...]
    events: tuple[LedgerEvent, ...]
    sleeve_cash: dict[str, Decimal]
    reserve_cash: Decimal
    positions: dict[tuple[str, str], LedgerPosition]
    proposals: dict[str, LedgerProposal]
    accounting_hash: str
    head_hash: str

    @property
    def managed_capital(self) -> Decimal:
        return self.initialization.managed_capital

    @property
    def universe(self) -> tuple[str, ...]:
        return self.allocation_epochs[-1].universe

    @property
    def allocation_epoch(self) -> str:
        return self.allocation_epochs[-1].allocation_epoch

    @property
    def cash(self) -> Decimal:
        return self.reserve_cash + sum(self.sleeve_cash.values(), Decimal("0"))

    @property
    def disposable_positions(self) -> dict[tuple[str, str], Decimal]:
        """Return confirmed quantities available to the manual exit workflow.

        This is a disposable projection, not a second source of truth.  The
        quantities are rebuilt from the verified event history on every replay.
        """
        return {key: position.quantity for key, position in self.positions.items()}

    @property
    def cost_basis_by_position(self) -> dict[tuple[str, str], Decimal]:
        """Return fee-inclusive cost basis rebuilt for each confirmed position."""
        return {key: position.cost_basis for key, position in self.positions.items()}

    def outstanding_gtc_exits(
        self,
        *,
        sleeve_id: str,
        instrument: str,
        position_id: str | None = None,
        role: str | None = None,
    ) -> tuple[LedgerProposal, ...]:
        """Return active GTC exits matching one sleeve position lifecycle."""
        normalized_instrument = instrument.upper()
        return tuple(
            proposal
            for proposal in self.proposals.values()
            if proposal.is_gtc_exit
            and proposal.terms.sleeve_id == sleeve_id
            and proposal.terms.instrument == normalized_instrument
            and (position_id is None or proposal.terms.position_id == position_id)
            and (role is None or proposal.terms.role == role)
        )

    def outstanding_entries(
        self,
        *,
        sleeve_id: str,
        instrument: str,
    ) -> tuple[LedgerProposal, ...]:
        """Return unfilled entry lifecycles that still reserve one strategy sleeve."""
        normalized_instrument = instrument.upper()
        return tuple(
            proposal
            for proposal in self.proposals.values()
            if proposal.is_outstanding
            and proposal.terms.action == "BUY"
            and proposal.terms.sleeve_id == sleeve_id
            and proposal.terms.instrument == normalized_instrument
        )


@dataclass(frozen=True)
class ReconciliationReport:
    """Persisted result of comparing broker reality with a verified ledger replay."""

    ok: bool
    checked_at: datetime
    ledger_path: str
    broker_path: str
    ledger_head_hash: str
    broker_checksum: str
    errors: tuple[str, ...] = ()

    def payload(self) -> dict[str, object]:
        return {
            "broker_checksum": self.broker_checksum,
            "broker_path": self.broker_path,
            "checked_at": timestamp_text(self.checked_at),
            "errors": list(self.errors),
            "ledger_head_hash": self.ledger_head_hash,
            "ledger_path": self.ledger_path,
            "ok": self.ok,
            "schema_version": RECONCILIATION_SCHEMA_VERSION,
        }


def event_hash(event: LedgerEvent) -> str:
    """Hash one event's canonical payload and its previous chain link."""
    return hashlib.sha256(canonical_json_bytes(event.payload())).hexdigest()


def canonical_ledger_bytes(events: Sequence[LedgerEvent]) -> bytes:
    """Serialize events with fixed columns, quoting, ordering, and line endings."""
    return canonical_csv_bytes(LEDGER_COLUMNS, tuple(event.to_row() for event in events))


def parse_ledger_bytes(content: bytes) -> tuple[LedgerEvent, ...]:
    """Parse and require canonical ledger bytes before any replay occurs."""
    try:
        rows = parse_canonical_csv_bytes(content, LEDGER_COLUMNS)
    except CanonicalCsvError as exc:
        raise LedgerIntegrityError(f"ledger {exc}") from exc
    try:
        events = tuple(LedgerEvent.from_row(row) for row in rows)
    except (TypeError, ValueError) as exc:
        raise LedgerIntegrityError("ledger contains an invalid event row") from exc
    if not events:
        raise LedgerIntegrityError("ledger must contain initialization")
    _verify_chain(events)
    return events


def _verify_chain(events: Sequence[LedgerEvent]) -> None:
    if not events:
        raise LedgerIntegrityError("ledger must contain initialization")
    if events[0].event_type != "initialization" or events[0].sequence != 1:
        raise LedgerIntegrityError("ledger must start with sequence 1 initialization")
    seen_ids: set[str] = set()
    seen_external_ids: set[str] = set()
    previous_timestamp: datetime | None = None
    previous_hash = GENESIS_HASH
    for expected_sequence, event in enumerate(events, start=1):
        if event.sequence != expected_sequence:
            raise LedgerIntegrityError("ledger sequence is not contiguous")
        if event.event_id in seen_ids:
            raise LedgerIntegrityError(f"duplicate event_id: {event.event_id}")
        if event.external_id and event.external_id in seen_external_ids:
            raise LedgerIntegrityError(f"duplicate external_id: {event.external_id}")
        seen_ids.add(event.event_id)
        if event.external_id:
            seen_external_ids.add(event.external_id)
        if event.previous_hash != previous_hash:
            raise LedgerIntegrityError(f"hash chain link broken at {event.event_id}")
        if event_hash(event) != event.event_hash:
            raise LedgerIntegrityError(f"event hash mismatch at {event.event_id}")
        if previous_timestamp is not None and event.occurred_at < previous_timestamp:
            raise LedgerIntegrityError("event timestamps must be nondecreasing")
        previous_timestamp = event.occurred_at
        previous_hash = event.event_hash


def _initialization_from_event(event: LedgerEvent) -> LedgerInitialization:
    try:
        payload = json.loads(event.metadata)
        universe = tuple(payload["universe"])
        sleeve_capital = tuple(
            (symbol, to_decimal(amount, f"initial sleeve {symbol}", allow_negative=False))
            for symbol, amount in sorted(payload["initial_sleeve_capital"].items())
        )
        initialization = LedgerInitialization(
            managed_capital=to_decimal(
                payload["managed_capital"], "managed_capital", allow_negative=False
            ),
            universe=universe,
            initial_sleeve_capital=sleeve_capital,
            initial_reserve_cash=to_decimal(
                payload["initial_reserve_cash"], "initial_reserve_cash", allow_negative=False
            ),
            allocation_epoch=str(payload["allocation_epoch"]),
            initialized_at=event.occurred_at,
            currency=str(payload["currency"]),
        )
    except (AttributeError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise LedgerIntegrityError("initialization metadata is invalid") from exc
    if event.amount != decimal_text(initialization.managed_capital):
        raise LedgerIntegrityError("initialization amount does not match metadata")
    if event.event_id != f"initialization:{initialization.allocation_epoch}":
        raise LedgerIntegrityError("initialization event ID does not match allocation epoch")
    if event.allocation_epoch != initialization.allocation_epoch:
        raise LedgerIntegrityError("initialization allocation epoch does not match metadata")
    if event.currency != initialization.currency:
        raise LedgerIntegrityError("initialization currency does not match metadata")
    if any(
        getattr(event, field_name)
        for field_name in (
            "sleeve_id",
            "instrument",
            "classification",
            "proposal_id",
            "position_id",
            "side",
            "quantity",
            "price",
            "fee",
            "order_type",
            "signal_date",
            "trading_date",
            "correction_of",
            "external_id",
        )
    ):
        raise LedgerIntegrityError("initialization event contains unexpected fields")
    if initialization.universe != tuple(sorted(initialization.universe)):
        raise LedgerIntegrityError("initialization universe is not canonical")
    if (
        tuple(symbol for symbol, _ in initialization.initial_sleeve_capital)
        != initialization.universe
    ):
        raise LedgerIntegrityError("initial sleeve capital does not cover the universe")
    if (
        sum(initialization.sleeve_capital.values(), Decimal("0"))
        + initialization.initial_reserve_cash
        != initialization.managed_capital
    ):
        raise LedgerIntegrityError("initial sleeve capital does not reconcile to managed capital")
    try:
        expected = LedgerInitialization.create(
            managed_capital=initialization.managed_capital,
            universe=initialization.universe,
            initialized_at=initialization.initialized_at,
            allocation_epoch=initialization.allocation_epoch,
            currency=initialization.currency,
        )
    except (TypeError, ValueError) as exc:
        raise LedgerIntegrityError(
            "initialization metadata violates allocation invariants"
        ) from exc
    if initialization != expected:
        raise LedgerIntegrityError("initialization metadata violates allocation invariants")
    return initialization


def _allocation_from_event(event: LedgerEvent) -> LedgerAllocationEpoch:
    try:
        payload = _metadata_object(event)
        raw_sleeves = payload["sleeve_capital"]
        if not isinstance(raw_sleeves, dict):
            raise TypeError("sleeve_capital must be an object")
        allocation = LedgerAllocationEpoch.create(
            allocation_epoch=str(payload["allocation_epoch"]),
            sleeve_capital=raw_sleeves,
            reserve_cash=payload["reserve_cash"],
            occurred_at=event.occurred_at,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise LedgerIntegrityError("allocation epoch metadata is invalid") from exc
    if payload.get("universe") != list(allocation.universe):
        raise LedgerIntegrityError("allocation epoch universe is not canonical")
    if event.event_id != f"allocation-epoch:{allocation.allocation_epoch}":
        raise LedgerIntegrityError("allocation epoch event ID does not match its identity")
    if event.allocation_epoch != allocation.allocation_epoch:
        raise LedgerIntegrityError("allocation epoch field does not match metadata")
    if event.amount != decimal_text(allocation.total_cash):
        raise LedgerIntegrityError("allocation epoch amount does not match assigned cash")
    if event.classification != "managed":
        raise LedgerIntegrityError("allocation epoch must be classified as managed")
    if any(
        getattr(event, field_name)
        for field_name in (
            "sleeve_id",
            "instrument",
            "proposal_id",
            "position_id",
            "side",
            "quantity",
            "price",
            "fee",
            "order_type",
            "signal_date",
            "trading_date",
            "correction_of",
            "external_id",
        )
    ):
        raise LedgerIntegrityError("allocation epoch event contains unexpected fields")
    return allocation


@dataclass
class _MutablePosition:
    sleeve_id: str
    instrument: str
    position_id: str
    quantity: Decimal
    gross_cost: Decimal
    cost_basis: Decimal
    opened_at: datetime
    entry_proposal_id: str


@dataclass(frozen=True)
class _PositionTrade:
    event_id: str
    occurred_at: datetime
    sleeve_id: str
    instrument: str
    position_id: str
    side: str
    quantity: Decimal
    price: Decimal
    fee: Decimal
    entry_proposal_id: str


def _metadata_object(event: LedgerEvent) -> dict[str, object]:
    try:
        value = json.loads(event.metadata)
    except json.JSONDecodeError as exc:
        raise LedgerIntegrityError(f"event metadata is invalid: {event.event_id}") from exc
    if not isinstance(value, dict):
        raise LedgerIntegrityError(f"event metadata must be an object: {event.event_id}")
    return value


def _decimal_field(value: str, field: str, *, required: bool = False) -> Decimal | None:
    if not value:
        if required:
            raise LedgerIntegrityError(f"{field} is required")
        return None
    try:
        return to_decimal(value, field)
    except (TypeError, ValueError) as exc:
        raise LedgerIntegrityError(f"{field} is invalid") from exc


def _positive_field(value: str, field: str, *, required: bool = True) -> Decimal | None:
    parsed = _decimal_field(value, field, required=required)
    if parsed is not None and parsed <= 0:
        raise LedgerIntegrityError(f"{field} must be greater than zero")
    return parsed


def _positive_input(value: Decimal | int | str, field: str) -> Decimal:
    try:
        parsed = to_decimal(value, field, allow_negative=False)
    except TypeError:
        raise
    except ValueError as exc:
        raise ValueError(f"{field} must be a positive decimal") from exc
    if parsed <= 0:
        raise ValueError(f"{field} must be greater than zero")
    return parsed


def _adjust_cash(
    sleeve_id: str,
    delta: Decimal,
    sleeve_cash: dict[str, Decimal],
    reserve_cash: list[Decimal],
) -> None:
    if sleeve_id:
        if sleeve_id not in sleeve_cash:
            raise LedgerIntegrityError(f"event references unknown sleeve: {sleeve_id}")
        next_cash = sleeve_cash[sleeve_id] + delta
        if next_cash < 0:
            raise LedgerIntegrityError(f"sleeve {sleeve_id} would borrow cash")
        sleeve_cash[sleeve_id] = next_cash
        return
    next_cash = reserve_cash[0] + delta
    if next_cash < 0:
        raise LedgerIntegrityError("reserve cash would become negative")
    reserve_cash[0] = next_cash


def _apply_position_transition(
    trade: _PositionTrade,
    *,
    positions: dict[tuple[str, str], _MutablePosition],
    sleeve_cash: dict[str, Decimal],
    reserve_cash: list[Decimal],
) -> None:
    key = (trade.sleeve_id, trade.instrument)
    notional = trade.quantity * trade.price
    existing = positions.get(key)
    if trade.side == "BUY":
        _adjust_cash(trade.sleeve_id, -(notional + trade.fee), sleeve_cash, reserve_cash)
        if existing is None:
            positions[key] = _MutablePosition(
                sleeve_id=trade.sleeve_id,
                instrument=trade.instrument,
                position_id=trade.position_id,
                quantity=trade.quantity,
                gross_cost=notional,
                cost_basis=notional + trade.fee,
                opened_at=trade.occurred_at,
                entry_proposal_id=trade.entry_proposal_id,
            )
        else:
            existing.quantity += trade.quantity
            existing.gross_cost += notional
            existing.cost_basis += notional + trade.fee
        return
    if existing is None:
        raise LedgerIntegrityError(f"SELL trade has no position: {trade.event_id}")
    _adjust_cash(trade.sleeve_id, notional - trade.fee, sleeve_cash, reserve_cash)
    fraction = trade.quantity / existing.quantity
    existing.quantity -= trade.quantity
    existing.gross_cost -= existing.gross_cost * fraction
    existing.cost_basis -= existing.cost_basis * fraction
    if existing.quantity == 0:
        del positions[key]


def _apply_position_trade(
    event: LedgerEvent,
    *,
    proposal: LedgerProposal,
    positions: dict[tuple[str, str], _MutablePosition],
    sleeve_cash: dict[str, Decimal],
    reserve_cash: list[Decimal],
) -> None:
    quantity = _positive_field(event.quantity, "quantity")
    price = _positive_field(event.price, "price")
    fee = _decimal_field(event.fee, "fee") or Decimal("0")
    if fee < 0:
        raise LedgerIntegrityError("fee must not be negative")
    if quantity is None or price is None:
        raise LedgerIntegrityError("trade quantity and price are required")
    if event.amount:
        raise LedgerIntegrityError("confirmed fills must not contain an amount field")
    key = (event.sleeve_id, event.instrument)
    position_id = event.position_id or proposal.terms.position_id
    if not event.sleeve_id or not event.instrument:
        raise LedgerIntegrityError("confirmed fills require sleeve_id and instrument")
    if event.side not in {"BUY", "SELL"}:
        raise LedgerIntegrityError("confirmed fill side must be BUY or SELL")
    if event.instrument != proposal.terms.instrument or event.sleeve_id != proposal.terms.sleeve_id:
        raise LedgerIntegrityError("fill does not match its proposal identity")
    if event.allocation_epoch != proposal.terms.allocation_epoch:
        raise LedgerIntegrityError("fill allocation epoch does not match its proposal")
    if event.order_type != proposal.terms.order_type:
        raise LedgerIntegrityError("fill order type does not match its proposal")
    if (
        event.signal_date != proposal.terms.signal_date.isoformat()
        or event.trading_date != proposal.terms.trading_date.isoformat()
    ):
        raise LedgerIntegrityError("fill dates do not match its proposal")
    if event.side != proposal.terms.action or position_id != proposal.terms.position_id:
        raise LedgerIntegrityError("fill terms do not match its proposal")
    if proposal.cancelled:
        raise LedgerIntegrityError("cancelled proposal cannot receive a fill")
    if proposal.filled_quantity + quantity > proposal.terms.quantity:
        raise LedgerIntegrityError("confirmed fills exceed submitted proposal quantity")

    existing = positions.get(key)
    if event.side == "BUY":
        if existing is not None and existing.entry_proposal_id != proposal.terms.proposal_id:
            raise LedgerIntegrityError("one sleeve cannot pyramid into a second BUY position")
        if existing is not None and existing.position_id != position_id:
            raise LedgerIntegrityError("partial fill changed the position identity")
    else:
        if existing is None:
            raise LedgerIntegrityError("SELL fill has no actual position")
        if existing.position_id != position_id:
            raise LedgerIntegrityError("SELL fill does not match the actual position")
        if quantity > existing.quantity:
            raise LedgerIntegrityError("SELL fill exceeds the actual position quantity")

    _apply_position_transition(
        _PositionTrade(
            event_id=event.event_id,
            occurred_at=event.occurred_at,
            sleeve_id=event.sleeve_id,
            instrument=event.instrument,
            position_id=position_id,
            side=event.side,
            quantity=quantity,
            price=price,
            fee=fee,
            entry_proposal_id=proposal.terms.proposal_id,
        ),
        positions=positions,
        sleeve_cash=sleeve_cash,
        reserve_cash=reserve_cash,
    )

    proposal.filled_quantity += quantity
    proposal.fill_event_ids.append(event.event_id)


def _apply_managed_manual_trade(
    event: LedgerEvent,
    *,
    positions: dict[tuple[str, str], _MutablePosition],
    sleeve_cash: dict[str, Decimal],
    reserve_cash: list[Decimal],
) -> None:
    if event.classification != "managed":
        raise LedgerIntegrityError("managed manual trade must be classified as managed")
    quantity = _positive_field(event.quantity, "quantity")
    price = _positive_field(event.price, "price")
    fee = _decimal_field(event.fee, "fee") or Decimal("0")
    if quantity is None or price is None:
        raise LedgerIntegrityError("managed manual trade requires quantity and price")
    if fee < 0 or not event.sleeve_id or not event.instrument:
        raise LedgerIntegrityError("managed manual trade has invalid accounting fields")
    if event.side not in {"BUY", "SELL"}:
        raise LedgerIntegrityError("managed manual trade side must be BUY or SELL")
    key = (event.sleeve_id, event.instrument)
    position_id = event.position_id or f"manual:{event.event_id}"
    existing = positions.get(key)
    if event.side == "BUY":
        if existing is not None and existing.position_id != position_id:
            raise LedgerIntegrityError("managed manual BUY would create a second sleeve position")
    else:
        if existing is None or existing.position_id != position_id:
            raise LedgerIntegrityError("managed manual SELL has no matching position")
        if quantity > existing.quantity:
            raise LedgerIntegrityError("managed manual SELL exceeds the actual position")
    _apply_position_transition(
        _PositionTrade(
            event_id=event.event_id,
            occurred_at=event.occurred_at,
            sleeve_id=event.sleeve_id,
            instrument=event.instrument,
            position_id=position_id,
            side=event.side,
            quantity=quantity,
            price=price,
            fee=fee,
            entry_proposal_id="",
        ),
        positions=positions,
        sleeve_cash=sleeve_cash,
        reserve_cash=reserve_cash,
    )


def _effective_events(events: Sequence[LedgerEvent]) -> list[LedgerEvent]:
    replacements: dict[str, LedgerEvent] = {}
    seen_targets: set[str] = set()
    by_id = {event.event_id: event for event in events}
    for event in events:
        if event.event_type != "correction":
            continue
        if not event.correction_of or event.correction_of not in by_id:
            raise LedgerIntegrityError(f"correction target is missing: {event.event_id}")
        target = by_id[event.correction_of]
        if target.sequence >= event.sequence:
            raise LedgerIntegrityError("correction must be appended after its target")
        if target.event_type == "correction":
            raise LedgerIntegrityError("a correction cannot target another correction")
        if target.event_type == "submission":
            raise LedgerIntegrityError("submission terms and authorization cannot be corrected")
        if event.correction_of in seen_targets:
            raise LedgerIntegrityError("an event cannot have multiple corrections")
        payload = _metadata_object(event).get("replacement")
        if not isinstance(payload, dict):
            raise LedgerIntegrityError("correction must contain a replacement event payload")
        replacement_row = target.to_row()
        for key, value in payload.items():
            if key not in LEDGER_COLUMNS or key in {
                "schema_version",
                "sequence",
                "previous_hash",
                "event_hash",
            }:
                raise LedgerIntegrityError("correction contains an immutable or unknown field")
            if key in {
                "event_id",
                "event_type",
                "occurred_at",
                "allocation_epoch",
                "currency",
                "correction_of",
            }:
                raise LedgerIntegrityError(f"correction cannot change {key}")
            if not isinstance(value, str):
                raise LedgerIntegrityError("correction replacement values must be strings")
            replacement_row[key] = value
        replacement_row["event_id"] = target.event_id
        replacement_row["sequence"] = str(target.sequence)
        replacement_row["previous_hash"] = target.previous_hash
        replacement_row["event_hash"] = target.event_hash
        replacements[target.event_id] = LedgerEvent.from_row(replacement_row)
        seen_targets.add(event.correction_of)

    effective = [
        replacements.get(event.event_id, event)
        for event in events
        if event.event_type != "correction"
    ]
    previous_timestamp: datetime | None = None
    for event in effective:
        if previous_timestamp is not None and event.occurred_at < previous_timestamp:
            raise LedgerIntegrityError("corrected event timestamps must remain ordered")
        previous_timestamp = event.occurred_at
    return effective


def replay_events(events: Sequence[LedgerEvent]) -> LedgerReplay:
    """Replay a verified ledger into cash, actual positions, and proposal views."""
    _verify_chain(events)
    initialization = _initialization_from_event(events[0])
    for event in events[1:]:
        if event.currency != initialization.currency:
            raise LedgerIntegrityError(
                f"event currency does not match initialization: {event.event_id}"
            )
    effective_events = _effective_events(events)
    for event in effective_events[1:]:
        if event.currency != initialization.currency:
            raise LedgerIntegrityError(
                f"corrected event currency does not match initialization: {event.event_id}"
            )
    sleeve_cash = initialization.sleeve_capital
    reserve_cash = [initialization.initial_reserve_cash]
    allocation_epochs = [
        LedgerAllocationEpoch.create(
            allocation_epoch=initialization.allocation_epoch,
            sleeve_capital=initialization.sleeve_capital,
            reserve_cash=initialization.initial_reserve_cash,
            occurred_at=initialization.initialized_at,
        )
    ]
    positions: dict[tuple[str, str], _MutablePosition] = {}
    proposals: dict[str, LedgerProposal] = {}
    for event in effective_events[1:]:
        expected_classification = EVENT_CLASSIFICATIONS.get(event.event_type)
        if expected_classification is not None and event.classification != expected_classification:
            raise LedgerIntegrityError(
                f"{event.event_type} event has invalid classification: {event.event_id}"
            )
        if event.event_type == "allocation_epoch":
            if positions:
                raise LedgerIntegrityError("allocation epoch requires a flat ledger")
            if any(proposal.is_outstanding for proposal in proposals.values()):
                raise LedgerIntegrityError("allocation epoch cannot strand outstanding proposals")
            allocation = _allocation_from_event(event)
            if any(
                prior.allocation_epoch == allocation.allocation_epoch for prior in allocation_epochs
            ):
                raise LedgerIntegrityError("allocation epoch identity is duplicated")
            current_cash = reserve_cash[0] + sum(sleeve_cash.values(), Decimal("0"))
            if allocation.total_cash != current_cash:
                raise LedgerIntegrityError("allocation epoch must preserve current ledger cash")
            allocation_epochs.append(allocation)
            sleeve_cash = allocation.sleeve_capital
            reserve_cash[0] = allocation.reserve_cash
            continue

        current_allocation = allocation_epochs[-1]
        if event.allocation_epoch != current_allocation.allocation_epoch:
            raise LedgerIntegrityError(f"event allocation epoch is not current: {event.event_id}")
        if event.event_type == "submission":
            if event.allocation_epoch != current_allocation.allocation_epoch:
                raise LedgerIntegrityError(
                    "submission allocation epoch does not match current allocation"
                )
            metadata = _metadata_object(event)
            payload = metadata.get("proposal_terms")
            if not isinstance(payload, dict):
                raise LedgerIntegrityError("submission must contain proposal_terms")
            authorization = metadata.get("authorization", {})
            if not isinstance(authorization, dict) or any(
                not isinstance(key, str) or not isinstance(value, (str, bool))
                for key, value in authorization.items()
            ):
                raise LedgerIntegrityError("submission authorization evidence is invalid")
            try:
                terms = ProposalTerms.from_payload(payload)
            except ValueError as exc:
                raise LedgerIntegrityError("submission proposal terms are invalid") from exc
            if terms.allocation_epoch != current_allocation.allocation_epoch:
                raise LedgerIntegrityError(
                    "proposal allocation epoch does not match current allocation"
                )
            if terms.proposal_id != event.proposal_id:
                raise LedgerIntegrityError("submission proposal ID does not match its terms")
            if terms.sleeve_id != event.sleeve_id or terms.instrument != event.instrument:
                raise LedgerIntegrityError("submission fields do not match its terms")
            if (
                event.position_id != terms.position_id
                or event.side != terms.action
                or event.order_type != terms.order_type
                or event.quantity != decimal_text(terms.quantity, "quantity")
                or event.price != (decimal_text(terms.price, "price") if terms.price else "")
                or event.signal_date != terms.signal_date.isoformat()
                or event.trading_date != terms.trading_date.isoformat()
                or event.amount
                or event.fee
            ):
                raise LedgerIntegrityError("submission terms do not match their event fields")
            if event.proposal_id in proposals:
                raise LedgerIntegrityError("duplicate proposal submission")
            if terms.action == "BUY" and any(
                proposal.is_outstanding
                and proposal.terms.action == "BUY"
                and proposal.terms.sleeve_id == terms.sleeve_id
                and proposal.terms.instrument == terms.instrument
                for proposal in proposals.values()
            ):
                raise LedgerIntegrityError(
                    "a sleeve cannot have overlapping outstanding entry proposals"
                )
            proposals[event.proposal_id] = LedgerProposal(
                terms,
                event.event_id,
                authorization=dict(authorization),
            )
        elif event.event_type in FILL_EVENT_TYPES:
            proposal = proposals.get(event.proposal_id)
            if proposal is None:
                raise LedgerIntegrityError("confirmed fills must reference a submission proposal")
            _apply_position_trade(
                event,
                proposal=proposal,
                positions=positions,
                sleeve_cash=sleeve_cash,
                reserve_cash=reserve_cash,
            )
        elif event.event_type == "cancellation":
            proposal = proposals.get(event.proposal_id)
            if proposal is None:
                raise LedgerIntegrityError("cancellation must reference a submission proposal")
            if proposal.filled_quantity >= proposal.terms.quantity:
                raise LedgerIntegrityError("fully filled proposal cannot be cancelled")
            if (
                event.position_id != proposal.terms.position_id
                or event.side != proposal.terms.action
                or event.order_type != proposal.terms.order_type
                or event.quantity != decimal_text(proposal.terms.quantity, "quantity")
                or event.signal_date != proposal.terms.signal_date.isoformat()
                or event.trading_date != proposal.terms.trading_date.isoformat()
                or event.price
                or event.amount
                or event.fee
            ):
                raise LedgerIntegrityError("cancellation fields do not match its proposal")
            proposal.cancelled = True
        elif event.event_type == "fee":
            amount = _positive_field(event.amount or event.fee, "fee amount")
            if amount is None:
                raise LedgerIntegrityError("fee amount is required")
            if event.amount and event.fee:
                fee_amount = _positive_field(event.fee, "fee amount")
                if fee_amount != amount:
                    raise LedgerIntegrityError("fee amount and fee fields do not match")
            _adjust_cash(event.sleeve_id, -amount, sleeve_cash, reserve_cash)
        elif event.event_type in TRANSFER_EVENT_TYPES:
            if event.fee:
                raise LedgerIntegrityError(f"{event.event_type} must not contain a fee field")
            amount = _positive_field(event.amount, event.event_type)
            if amount is None:
                raise LedgerIntegrityError(f"{event.event_type} amount is required")
            _adjust_cash(
                event.sleeve_id,
                amount if event.event_type == "deposit" else -amount,
                sleeve_cash,
                reserve_cash,
            )
        elif event.event_type == "manual_adjustment":
            if event.classification == "unrelated_manual":
                continue
            if event.classification != "managed":
                raise LedgerIntegrityError(
                    f"manual adjustment has invalid classification: {event.event_id}"
                )
            if event.instrument:
                if event.amount:
                    raise LedgerIntegrityError(
                        "managed manual trade cannot combine position and cash fields"
                    )
                _apply_managed_manual_trade(
                    event,
                    positions=positions,
                    sleeve_cash=sleeve_cash,
                    reserve_cash=reserve_cash,
                )
            elif event.amount:
                if event.quantity or event.price or event.side or event.position_id:
                    raise LedgerIntegrityError(
                        "managed manual cash adjustment cannot contain position fields"
                    )
                cash_delta = _decimal_field(event.amount, "manual cash adjustment", required=True)
                if cash_delta is None:
                    raise LedgerIntegrityError("manual cash adjustment amount is required")
                _adjust_cash(event.sleeve_id, cash_delta, sleeve_cash, reserve_cash)
            else:
                raise LedgerIntegrityError("managed manual_adjustment has no accounting effect")
        else:
            raise LedgerIntegrityError(f"unsupported replay event: {event.event_type}")

    projected_positions = {
        key: LedgerPosition(
            sleeve_id=value.sleeve_id,
            instrument=value.instrument,
            position_id=value.position_id,
            quantity=value.quantity,
            cost_basis=value.cost_basis,
            average_price=value.gross_cost / value.quantity,
            opened_at=value.opened_at,
            entry_proposal_id=value.entry_proposal_id,
        )
        for key, value in positions.items()
    }
    accounting_events = [
        event
        for event in effective_events
        if event.event_type
        in {
            "initialization",
            "fill",
            "partial_fill",
            "fee",
            "deposit",
            "withdrawal",
            "manual_adjustment",
            "allocation_epoch",
        }
        and not (
            event.event_type == "manual_adjustment" and event.classification == "unrelated_manual"
        )
    ]
    accounting_hash = hashlib.sha256(
        canonical_json_bytes([event.payload() for event in accounting_events])
    ).hexdigest()
    return LedgerReplay(
        initialization=initialization,
        allocation_epochs=tuple(allocation_epochs),
        events=tuple(events),
        sleeve_cash=sleeve_cash,
        reserve_cash=reserve_cash[0],
        positions=projected_positions,
        proposals=proposals,
        accounting_hash=accounting_hash,
        head_hash=events[-1].event_hash,
    )


class ManualLedgerStore:
    """Safe persistence boundary for one local manual execution ledger."""

    def __init__(
        self,
        path: Path,
        *,
        now: Callable[[], datetime] | None = None,
        lock_timeout_seconds: float = 10.0,
    ) -> None:
        self.path = Path(path)
        self.now = now or (lambda: datetime.now(UTC))
        self.lock_timeout_seconds = lock_timeout_seconds
        self.lock_path = self.path.with_name(f".{self.path.name}.lock")
        self.checkpoint_path = self.path.with_name(f".{self.path.name}.head.json")

    @contextmanager
    def _locked(self) -> Iterator[None]:
        try:
            with locked_file(self.lock_path, self.lock_timeout_seconds):
                yield
        except FileLockTimeout as exc:
            raise LedgerLockTimeout(f"timed out waiting for ledger lock: {self.path}") from exc

    def initialize(self, initialization: LedgerInitialization) -> LedgerReplay:
        """Create one ledger, or accept an exact idempotent retry."""
        event = LedgerEvent.initialization(initialization)
        event = _with_chain_values(event, sequence=1, previous_hash=GENESIS_HASH)
        content = canonical_ledger_bytes((event,))
        with self._locked():
            if self.path.exists():
                existing_content = self.path.read_bytes()
                existing = parse_ledger_bytes(existing_content)
                _verify_checkpoint(self.checkpoint_path, existing_content, existing)
                replay = replay_events(existing)
                if canonical_ledger_bytes(existing) != content:
                    raise LedgerConflictError("ledger already exists with different initialization")
                return replay
            _atomic_write(self.path, content, replace=False)
            _write_checkpoint(self.checkpoint_path, content, (event,))
        return replay_events((event,))

    def record_submission(
        self,
        proposal: ProposalTerms,
        *,
        occurred_at: datetime | None = None,
        event_id: str | None = None,
        authorization: Mapping[str, str | bool] | None = None,
        expected_accounting_hash: str | None = None,
        reconciliation_path: Path | None = None,
        require_current_reconciliation: bool = False,
        submission_validator: Callable[[], None] | None = None,
        coordination_lock_path: Path | None = None,
    ) -> LedgerEvent:
        """Append one proposal submission, idempotently by deterministic proposal ID."""
        replay = self.verify()

        def validate_authorization(current: LedgerReplay) -> None:
            if (
                expected_accounting_hash is not None
                and current.accounting_hash != expected_accounting_hash
            ):
                raise LedgerConflictError(
                    "ledger accounting identity changed before proposal submission"
                )
            if require_current_reconciliation and (
                reconciliation_path is None
                or not self.reconciliation_is_current(reconciliation_path)
            ):
                raise LedgerConflictError(
                    "broker reconciliation is not current at proposal submission"
                )
            if submission_validator is not None:
                submission_validator()
            current_existing = current.proposals.get(proposal.proposal_id)
            if current_existing is not None:
                if not (
                    current_existing.terms.same_terms(proposal)
                    or current_existing.matches_active_remainder(proposal)
                ):
                    raise ProposalConflictError(
                        f"proposal {proposal.proposal_id} already exists with different terms"
                    )
                if proposal.action == "BUY" and current_existing.authorization.get(
                    "strategy_id"
                ) != dict(authorization or {}).get("strategy_id"):
                    raise ProposalConflictError(
                        f"proposal {proposal.proposal_id} belongs to a different strategy"
                    )
                return
            if proposal.sleeve_id not in current.universe:
                raise LedgerConflictError(
                    f"proposal references unknown sleeve: {proposal.sleeve_id}"
                )
            if proposal.allocation_epoch != current.allocation_epoch:
                raise LedgerConflictError(
                    "proposal allocation epoch does not match the ledger allocation epoch"
                )
            if proposal.action == "BUY":
                if (proposal.sleeve_id, proposal.instrument) in current.positions:
                    raise LedgerConflictError("strategy sleeve already has an actual position")
                if current.outstanding_entries(
                    sleeve_id=proposal.sleeve_id,
                    instrument=proposal.instrument,
                ):
                    raise LedgerConflictError(
                        "strategy sleeve already has an outstanding entry proposal"
                    )

        existing = replay.proposals.get(proposal.proposal_id)
        if existing is not None:
            if not (
                existing.terms.same_terms(proposal) or existing.matches_active_remainder(proposal)
            ):
                raise ProposalConflictError(
                    f"proposal {proposal.proposal_id} already exists with different terms"
                )
            self._validate_replay_under_lock(
                validate_authorization,
                coordination_lock_path=coordination_lock_path,
            )
            return next(
                event for event in replay.events if event.event_id == existing.submission_event_id
            )
        if proposal.sleeve_id not in replay.universe:
            raise LedgerConflictError(f"proposal references unknown sleeve: {proposal.sleeve_id}")
        if proposal.allocation_epoch != replay.allocation_epoch:
            raise LedgerConflictError(
                "proposal allocation epoch does not match the ledger allocation epoch"
            )
        event = LedgerEvent(
            event_id=event_id or f"submission:{proposal.proposal_id}",
            event_type="submission",
            occurred_at=occurred_at or self.now(),
            allocation_epoch=proposal.allocation_epoch,
            sleeve_id=proposal.sleeve_id,
            instrument=proposal.instrument,
            classification="proposal",
            proposal_id=proposal.proposal_id,
            position_id=proposal.position_id,
            side=proposal.action,
            quantity=decimal_text(proposal.quantity, "quantity"),
            price=decimal_text(proposal.price, "price") if proposal.price is not None else "",
            currency=replay.initialization.currency,
            order_type=proposal.order_type,
            signal_date=proposal.signal_date.isoformat(),
            trading_date=proposal.trading_date.isoformat(),
            metadata=_metadata_text(
                {
                    "authorization": dict(authorization or {}),
                    "proposal_terms": proposal.payload(),
                }
            ),
        )
        return self._append_event(
            event,
            replay_validator=validate_authorization,
            coordination_lock_path=coordination_lock_path,
        )

    def start_allocation_epoch(
        self,
        allocation_epoch: str,
        *,
        sleeve_capital: Mapping[str, Decimal | int | str],
        reserve_cash: Decimal | int | str = Decimal("0"),
        occurred_at: datetime | None = None,
    ) -> LedgerReplay:
        """Append an explicit flat-ledger universe and sleeve-capital reassignment."""
        replay = self.verify()
        allocation = LedgerAllocationEpoch.create(
            allocation_epoch=allocation_epoch,
            sleeve_capital=sleeve_capital,
            reserve_cash=reserve_cash,
            occurred_at=occurred_at or self.now(),
        )
        existing = next(
            (
                epoch
                for epoch in replay.allocation_epochs
                if epoch.allocation_epoch == allocation.allocation_epoch
            ),
            None,
        )
        if existing is not None:
            if existing == allocation:
                return replay
            raise LedgerConflictError(
                f"allocation epoch already exists with different terms: {allocation.allocation_epoch}"
            )
        if replay.positions:
            raise LedgerConflictError("allocation epoch requires all actual positions to be flat")
        if any(proposal.is_outstanding for proposal in replay.proposals.values()):
            raise LedgerConflictError("allocation epoch cannot strand outstanding proposals")
        if allocation.total_cash != replay.cash:
            raise LedgerConflictError(
                "allocation epoch assigned capital must equal current ledger cash"
            )
        event = LedgerEvent(
            event_id=f"allocation-epoch:{allocation.allocation_epoch}",
            event_type="allocation_epoch",
            occurred_at=allocation.occurred_at,
            allocation_epoch=allocation.allocation_epoch,
            classification="managed",
            amount=decimal_text(allocation.total_cash),
            currency=replay.initialization.currency,
            metadata=_metadata_text(allocation.metadata()),
        )
        self._append_event(event)
        return self.verify()

    def record_fill(
        self,
        *,
        proposal_id: str,
        sleeve_id: str,
        instrument: str,
        side: str,
        quantity: Decimal | int | str,
        price: Decimal | int | str,
        fee: Decimal | int | str | None = None,
        event_type: str = "fill",
        occurred_at: datetime | None = None,
        event_id: str | None = None,
        external_id: str | None = None,
    ) -> LedgerEvent:
        """Append a broker-confirmed fill; only this path changes actual positions."""
        replay = self.verify()
        proposal = replay.proposals.get(proposal_id)
        if proposal is None:
            raise LedgerConflictError(f"fill references unknown proposal: {proposal_id}")
        if event_type not in FILL_EVENT_TYPES:
            raise ValueError("fill event_type must be fill or partial_fill")
        event = LedgerEvent(
            event_id=event_id or f"{event_type}:{uuid.uuid4().hex}",
            event_type=event_type,
            occurred_at=occurred_at or self.now(),
            allocation_epoch=proposal.terms.allocation_epoch,
            sleeve_id=sleeve_id,
            instrument=instrument.upper(),
            classification="proposal",
            proposal_id=proposal_id,
            position_id=proposal.terms.position_id,
            side=side.upper(),
            quantity=decimal_text(quantity, "quantity"),
            price=decimal_text(price, "price"),
            fee=decimal_text(fee, "fee") if fee is not None else "",
            currency=replay.initialization.currency,
            order_type=proposal.terms.order_type,
            signal_date=proposal.terms.signal_date.isoformat(),
            trading_date=proposal.terms.trading_date.isoformat(),
            external_id=external_id or "",
        )
        return self._append_event(event)

    def record_cancellation(
        self,
        proposal_id: str,
        *,
        occurred_at: datetime | None = None,
        event_id: str | None = None,
    ) -> LedgerEvent:
        """Append a cancellation for the unfilled remainder of a proposal."""
        replay = self.verify()
        proposal = replay.proposals.get(proposal_id)
        if proposal is None:
            raise LedgerConflictError(f"cancellation references unknown proposal: {proposal_id}")
        event = LedgerEvent(
            event_id=event_id or f"cancellation:{proposal_id}",
            event_type="cancellation",
            occurred_at=occurred_at or self.now(),
            allocation_epoch=proposal.terms.allocation_epoch,
            sleeve_id=proposal.terms.sleeve_id,
            instrument=proposal.terms.instrument,
            classification="proposal",
            proposal_id=proposal_id,
            position_id=proposal.terms.position_id,
            side=proposal.terms.action,
            quantity=decimal_text(proposal.terms.quantity, "quantity"),
            currency=replay.initialization.currency,
            order_type=proposal.terms.order_type,
            signal_date=proposal.terms.signal_date.isoformat(),
            trading_date=proposal.terms.trading_date.isoformat(),
        )
        return self._append_event(event)

    def record_cash_event(
        self,
        event_type: str,
        amount: Decimal | int | str,
        *,
        sleeve_id: str = "",
        occurred_at: datetime | None = None,
        event_id: str | None = None,
        external_id: str | None = None,
    ) -> LedgerEvent:
        """Append a deposit, withdrawal, or standalone fee event."""
        if event_type not in CASH_EVENT_TYPES:
            raise ValueError("cash event_type must be deposit, withdrawal, or fee")
        replay = self.verify()
        parsed_amount = _positive_input(amount, "amount")
        event = LedgerEvent(
            event_id=event_id or f"{event_type}:{uuid.uuid4().hex}",
            event_type=event_type,
            occurred_at=occurred_at or self.now(),
            allocation_epoch=replay.allocation_epoch,
            sleeve_id=sleeve_id,
            classification="managed",
            amount=decimal_text(parsed_amount, "amount"),
            fee=decimal_text(parsed_amount, "fee") if event_type == "fee" else "",
            currency=replay.initialization.currency,
            external_id=external_id or "",
        )
        return self._append_event(event)

    def record_manual_adjustment(
        self,
        *,
        classification: str,
        sleeve_id: str = "",
        instrument: str = "",
        side: str = "",
        quantity: Decimal | int | str | None = None,
        price: Decimal | int | str | None = None,
        amount: Decimal | int | str | None = None,
        position_id: str = "",
        occurred_at: datetime | None = None,
        event_id: str | None = None,
        external_id: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> LedgerEvent:
        """Append a classified manual adjustment without conflating unrelated trades."""
        if classification not in {"managed", "unrelated_manual"}:
            raise ValueError("manual adjustment classification is invalid")
        replay = self.verify()
        quantity_text = decimal_text(quantity, "quantity") if quantity is not None else ""
        price_text = decimal_text(price, "price") if price is not None else ""
        amount_text = decimal_text(amount, "amount") if amount is not None else ""
        event = LedgerEvent(
            event_id=event_id or f"manual-adjustment:{uuid.uuid4().hex}",
            event_type="manual_adjustment",
            occurred_at=occurred_at or self.now(),
            allocation_epoch=replay.allocation_epoch,
            sleeve_id=sleeve_id,
            instrument=instrument.upper(),
            classification=classification,
            position_id=position_id,
            side=side.upper(),
            quantity=quantity_text,
            price=price_text,
            amount=amount_text,
            currency=replay.initialization.currency,
            external_id=external_id or "",
            metadata=_metadata_text(metadata or {}),
        )
        return self._append_event(event)

    def record_correction(
        self,
        target_event_id: str,
        changes: Mapping[str, Decimal | int | str],
        *,
        occurred_at: datetime | None = None,
        event_id: str | None = None,
    ) -> LedgerEvent:
        """Append a correction event; the target row is never rewritten."""
        replay = self.verify()
        target = next((event for event in replay.events if event.event_id == target_event_id), None)
        if target is None:
            raise LedgerConflictError(f"correction target does not exist: {target_event_id}")
        if target.event_type in {"initialization", "allocation_epoch", "correction"}:
            raise LedgerConflictError(
                "initialization, allocation epoch, and correction events cannot be corrected"
            )
        if target.event_type == "submission":
            raise LedgerConflictError(
                "submission terms and authorization cannot be corrected; cancel and replace"
            )
        existing_correction = next(
            (event for event in replay.events if event.correction_of == target_event_id), None
        )
        normalized: dict[str, str] = {}
        for key, value in changes.items():
            if key not in LEDGER_COLUMNS or key in {
                "schema_version",
                "sequence",
                "previous_hash",
                "event_hash",
            }:
                raise ValueError(f"cannot correct ledger field: {key}")
            if key in {
                "event_id",
                "event_type",
                "occurred_at",
                "allocation_epoch",
                "currency",
                "correction_of",
            }:
                raise ValueError(f"cannot correct ledger field: {key}")
            if key in {"quantity", "price", "amount", "fee"}:
                normalized[key] = decimal_text(value, key)
            else:
                normalized[key] = str(value)
        if existing_correction is not None:
            replacement = _metadata_object(existing_correction).get("replacement")
            if replacement == normalized:
                return existing_correction
            raise LedgerConflictError(f"event {target_event_id} already has a correction")
        identity = hashlib.sha256(canonical_json_bytes(normalized)).hexdigest()
        event = LedgerEvent(
            event_id=event_id or f"correction:{target_event_id}:{identity}",
            event_type="correction",
            occurred_at=occurred_at or self.now(),
            allocation_epoch=replay.allocation_epoch,
            classification="correction",
            correction_of=target_event_id,
            currency=replay.initialization.currency,
            metadata=_metadata_text({"replacement": normalized}),
        )
        return self._append_event(event)

    def reconcile(
        self,
        broker_export: Path,
        report_path: Path,
        *,
        checked_at: datetime | None = None,
    ) -> ReconciliationReport:
        """Compare a broker CSV with replayed state and persist even failed checks."""
        broker_path = Path(broker_export)
        broker_checksum = _file_checksum(broker_path)
        errors: list[str] = []
        ledger_head_hash = ""
        try:
            replay = self.verify()
            ledger_head_hash = replay.accounting_hash
        except LedgerError as exc:
            replay = None
            errors.append(f"ledger verification failed: {exc}")
        try:
            broker = read_broker_export(broker_path)
        except BrokerExportError as exc:
            broker = None
            errors.append(f"broker export invalid: {exc}")
        if replay is not None and broker is not None:
            errors.extend(
                compare_broker_snapshot(
                    expected_cash={**replay.sleeve_cash, "": replay.reserve_cash},
                    expected_positions={
                        key: (position.quantity, position.cost_basis)
                        for key, position in replay.positions.items()
                    },
                    broker=broker,
                    tolerance=ACCOUNTING_TOLERANCE,
                )
            )
        report = ReconciliationReport(
            ok=not errors,
            checked_at=(checked_at or self.now()).astimezone(UTC),
            ledger_path=str(self.path.resolve()),
            broker_path=str(broker_path.resolve()),
            ledger_head_hash=ledger_head_hash,
            broker_checksum=broker_checksum,
            errors=tuple(errors),
        )
        _atomic_write(
            Path(report_path),
            canonical_json_bytes(report.payload()),
            replace=True,
        )
        return report

    def reconciliation_is_current(
        self,
        report_path: Path,
        broker_export: Path | None = None,
    ) -> bool:
        """Return true only for a successful report tied to current bytes and ledger head."""
        try:
            payload = json.loads(Path(report_path).read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                return False
            if payload.get("schema_version") != RECONCILIATION_SCHEMA_VERSION:
                return False
            if payload.get("ok") is not True:
                return False
            replay = self.verify()
            broker_path = Path(broker_export or payload["broker_path"])
            return (
                payload.get("ledger_path") == str(self.path.resolve())
                and payload.get("broker_path") == str(broker_path.resolve())
                and payload.get("ledger_head_hash") == replay.accounting_hash
                and payload.get("broker_checksum") == _file_checksum(broker_path)
            )
        except (KeyError, OSError, ValueError, TypeError, json.JSONDecodeError, LedgerError):
            return False

    def export(self, destination: Path) -> Path:
        """Verify and atomically publish a portable CSV copy without overwriting it."""
        events = self.read_events()
        content = canonical_ledger_bytes(events)
        destination = Path(destination)
        checkpoint = destination.with_name(f".{destination.name}.head.json")
        if destination.exists():
            if destination.read_bytes() != content:
                raise LedgerConflictError(f"refusing to overwrite existing export: {destination}")
            _write_checkpoint(checkpoint, content, events)
            return destination
        _atomic_write(destination, content, replace=False)
        _write_checkpoint(checkpoint, content, events)
        return destination

    def import_ledger(self, source: Path) -> LedgerReplay:
        """Verify a portable CSV and its head checkpoint before installing it."""
        source = Path(source)
        content = source.read_bytes()
        events = parse_ledger_bytes(content)
        source_checkpoint = source.with_name(f".{source.name}.head.json")
        _verify_checkpoint(source_checkpoint, content, events)
        replay = replay_events(events)
        with self._locked():
            if self.path.exists():
                existing = self.path.read_bytes()
                if existing != canonical_ledger_bytes(events):
                    raise LedgerConflictError(f"refusing to overwrite existing ledger: {self.path}")
            else:
                _atomic_write(self.path, canonical_ledger_bytes(events), replace=False)
            _write_checkpoint(self.checkpoint_path, canonical_ledger_bytes(events), events)
        return replay

    def _append_event(
        self,
        event: LedgerEvent,
        *,
        replay_validator: Callable[[LedgerReplay], None] | None = None,
        coordination_lock_path: Path | None = None,
    ) -> LedgerEvent:
        coordination = locked_file(
            Path(coordination_lock_path)
            if coordination_lock_path is not None
            else self.path.parent / ".manual-trading-coordination.lock",
            self.lock_timeout_seconds,
        )
        with coordination, self._locked():
            content = self.path.read_bytes()
            events = list(parse_ledger_bytes(content))
            _verify_checkpoint(self.checkpoint_path, content, events)
            current_replay = replay_events(events)
            if replay_validator is not None:
                replay_validator(current_replay)
            existing = next((item for item in events if item.event_id == event.event_id), None)
            if existing is not None:
                if _same_event_content(existing, event):
                    return existing
                raise LedgerConflictError(
                    f"event {event.event_id} already exists with different content"
                )
            if event.external_id:
                existing_external = next(
                    (item for item in events if item.external_id == event.external_id), None
                )
                if existing_external is not None:
                    if _same_event_content(existing_external, event, ignore_event_id=True):
                        return existing_external
                    raise LedgerConflictError(
                        f"external event {event.external_id} already exists with different content"
                    )
            previous_hash = events[-1].event_hash
            appended = _with_chain_values(
                event,
                sequence=len(events) + 1,
                previous_hash=previous_hash,
            )
            candidate_events = (*events, appended)
            replay_events(candidate_events)
            next_content = canonical_ledger_bytes(candidate_events)
            _atomic_write(self.path, next_content, replace=True)
            _write_checkpoint(self.checkpoint_path, next_content, candidate_events)
            return appended

    def _validate_replay_under_lock(
        self,
        validator: Callable[[LedgerReplay], None],
        *,
        coordination_lock_path: Path | None = None,
    ) -> None:
        coordination = locked_file(
            Path(coordination_lock_path)
            if coordination_lock_path is not None
            else self.path.parent / ".manual-trading-coordination.lock",
            self.lock_timeout_seconds,
        )
        with coordination, self._locked():
            content = self.path.read_bytes()
            events = list(parse_ledger_bytes(content))
            _verify_checkpoint(self.checkpoint_path, content, events)
            validator(replay_events(events))

    def read_events(self) -> tuple[LedgerEvent, ...]:
        """Read and verify the append-only history without changing it."""
        try:
            content = self.path.read_bytes()
        except OSError as exc:
            raise LedgerIntegrityError(f"ledger is missing or unreadable: {self.path}") from exc
        events = parse_ledger_bytes(content)
        _verify_checkpoint(self.checkpoint_path, content, events)
        return events

    def verify(self) -> LedgerReplay:
        """Verify bytes, chain, and replay invariants."""
        return replay_events(self.read_events())


def _with_chain_values(event: LedgerEvent, *, sequence: int, previous_hash: str) -> LedgerEvent:
    candidate = LedgerEvent(
        **{
            **event.__dict__,
            "sequence": sequence,
            "previous_hash": previous_hash,
            "event_hash": "",
        }
    )
    return LedgerEvent(**{**candidate.__dict__, "event_hash": event_hash(candidate)})


def _same_event_content(
    first: LedgerEvent,
    second: LedgerEvent,
    *,
    ignore_event_id: bool = False,
) -> bool:
    first_row = first.to_row()
    second_row = second.to_row()
    ignored_fields = {"sequence", "previous_hash", "event_hash"}
    if ignore_event_id:
        ignored_fields.add("event_id")
    for key in ignored_fields:
        first_row.pop(key)
        second_row.pop(key)
    return first_row == second_row


def _metadata_text(payload: Mapping[str, object]) -> str:
    return canonical_json_bytes(payload).decode("utf-8").rstrip("\n")


def _file_checksum(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _write_checkpoint(path: Path, content: bytes, events: Sequence[LedgerEvent]) -> None:
    payload = {
        "event_count": len(events),
        "ledger_checksum": hashlib.sha256(content).hexdigest(),
        "head_hash": events[-1].event_hash,
        "schema_version": 1,
    }
    _atomic_write(path, canonical_json_bytes(payload), replace=True)


def _verify_checkpoint(path: Path, content: bytes, events: Sequence[LedgerEvent]) -> None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LedgerIntegrityError("ledger head checkpoint is missing or invalid") from exc
    if not isinstance(payload, dict):
        raise LedgerIntegrityError("ledger head checkpoint must be a JSON object")
    if (
        payload.get("schema_version") != 1
        or payload.get("event_count") != len(events)
        or payload.get("head_hash") != events[-1].event_hash
        or payload.get("ledger_checksum") != hashlib.sha256(content).hexdigest()
    ):
        raise LedgerIntegrityError("ledger head checkpoint does not match CSV history")


def _atomic_write(path: Path, content: bytes, *, replace: bool) -> None:
    try:
        atomic_write(path, content, replace=replace)
    except FileExistsError as exc:
        raise LedgerConflictError(f"refusing to overwrite existing ledger: {path}") from exc
