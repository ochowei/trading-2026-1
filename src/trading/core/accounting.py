"""Exact decimal primitives shared by manual-trading accounting boundaries."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any


def to_decimal(value: Decimal | int | str, field: str, *, allow_negative: bool = True) -> Decimal:
    """Parse a finite decimal without allowing binary floating-point inputs."""
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError(f"{field} must be a Decimal, integer, or decimal string")
    try:
        parsed = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field} must be a decimal value") from exc
    if not parsed.is_finite():
        raise ValueError(f"{field} must be finite")
    if not allow_negative and parsed < 0:
        raise ValueError(f"{field} must not be negative")
    return parsed


def decimal_text(value: Decimal | int | str, field: str = "value") -> str:
    """Return one canonical non-exponential representation of a decimal."""
    parsed = to_decimal(value, field)
    if parsed == 0:
        return "0"
    return format(parsed.normalize(), "f")


def timestamp_text(value: datetime) -> str:
    """Normalize an aware timestamp to canonical UTC RFC 3339 text."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware")
    return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def parse_timestamp(value: str, field: str = "timestamp") -> datetime:
    """Parse canonical or equivalent aware RFC 3339 timestamp text."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(UTC)


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON values deterministically for identities and hashes."""
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")
