"""Broker-export parsing and accounting comparison for manual reconciliation."""

from __future__ import annotations

import csv
import io
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from trading.core.accounting import decimal_text, to_decimal

BROKER_COLUMNS = ("record_type", "sleeve_id", "instrument", "quantity", "cost_basis", "cash")


class BrokerExportError(ValueError):
    """A broker export cannot be safely compared with ledger accounting state."""


@dataclass(frozen=True)
class BrokerSnapshot:
    """Minimal broker-export view needed for manual reconciliation."""

    cash_by_sleeve: dict[str, Decimal]
    positions: dict[tuple[str, str], tuple[Decimal, Decimal]]


def _decimal_field(value: str, field: str) -> Decimal:
    if not value:
        raise BrokerExportError(f"{field} is required")
    try:
        parsed = to_decimal(value, field)
    except (TypeError, ValueError) as exc:
        raise BrokerExportError(str(exc)) from exc
    if decimal_text(parsed, field) != value:
        raise BrokerExportError(f"{field} must use canonical decimal text")
    return parsed


def read_broker_export(path: Path) -> BrokerSnapshot:
    """Parse the supported broker CSV into cash and position accounting views."""
    try:
        content = Path(path).read_bytes()
    except OSError as exc:
        raise BrokerExportError(f"broker export is missing or unreadable: {path}") from exc
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BrokerExportError("broker export is not valid UTF-8") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != BROKER_COLUMNS:
        raise BrokerExportError("broker export header is not supported")
    cash: dict[str, Decimal] = {}
    positions: dict[tuple[str, str], tuple[Decimal, Decimal]] = {}
    try:
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise BrokerExportError("broker export row has invalid columns")
            record_type = row["record_type"]
            if record_type == "cash":
                sleeve_id = row["sleeve_id"]
                if sleeve_id in cash:
                    raise BrokerExportError(f"duplicate broker cash row: {sleeve_id}")
                amount = _decimal_field(row["cash"], "broker cash")
                if amount < 0:
                    raise BrokerExportError("broker cash must not be negative")
                cash[sleeve_id] = amount
            elif record_type == "position":
                sleeve_id = row["sleeve_id"]
                instrument = row["instrument"].upper()
                if not sleeve_id or not instrument:
                    raise BrokerExportError("broker position requires sleeve_id and instrument")
                key = (sleeve_id, instrument)
                if key in positions:
                    raise BrokerExportError(f"duplicate broker position row: {key}")
                quantity = _decimal_field(row["quantity"], "broker quantity")
                cost_basis = _decimal_field(row["cost_basis"], "broker cost_basis")
                if quantity < 0 or cost_basis < 0:
                    raise BrokerExportError("broker position values must not be negative")
                if quantity == 0 and cost_basis != 0:
                    raise BrokerExportError("zero broker quantity must have zero cost basis")
                positions[key] = (quantity, cost_basis)
            else:
                raise BrokerExportError(f"unsupported broker record_type: {record_type}")
    except csv.Error as exc:
        raise BrokerExportError("broker export CSV is malformed") from exc
    return BrokerSnapshot(cash_by_sleeve=cash, positions=positions)


def compare_broker_snapshot(
    *,
    expected_cash: Mapping[str, Decimal],
    expected_positions: Mapping[tuple[str, str], tuple[Decimal, Decimal]],
    broker: BrokerSnapshot,
    tolerance: Decimal,
) -> list[str]:
    """Return deterministic accounting mismatches between ledger and broker views."""

    def within_tolerance(first: Decimal, second: Decimal) -> bool:
        return abs(first - second) <= tolerance

    errors: list[str] = []
    for sleeve_id in sorted(set(expected_cash) | set(broker.cash_by_sleeve)):
        expected = expected_cash.get(sleeve_id, Decimal("0"))
        actual = broker.cash_by_sleeve.get(sleeve_id, Decimal("0"))
        if not within_tolerance(expected, actual):
            label = sleeve_id or "reserve"
            errors.append(f"cash mismatch for {label}: ledger={expected} broker={actual}")
    for key in sorted(set(expected_positions) | set(broker.positions)):
        expected = expected_positions.get(key, (Decimal("0"), Decimal("0")))
        actual = broker.positions.get(key, (Decimal("0"), Decimal("0")))
        if not within_tolerance(expected[0], actual[0]):
            errors.append(f"quantity mismatch for {key}: ledger={expected[0]} broker={actual[0]}")
        if not within_tolerance(expected[1], actual[1]):
            errors.append(f"cost basis mismatch for {key}: ledger={expected[1]} broker={actual[1]}")
    return errors
