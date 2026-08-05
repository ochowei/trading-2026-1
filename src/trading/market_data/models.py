"""Immutable market-data domain values."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal
from zoneinfo import ZoneInfo

from trading.market_data.contracts import SessionCalendar

_NEW_YORK = ZoneInfo("America/New_York")


def encode_symbol(symbol: str) -> str:
    """Encode an arbitrary provider symbol as a versioned filesystem-safe name."""
    if not symbol:
        raise ValueError("symbol must not be empty")
    payload = base64.urlsafe_b64encode(symbol.encode("utf-8")).decode("ascii").rstrip("=")
    return f"v1-{payload}"


def decode_symbol(encoded: str) -> str:
    """Decode a symbol produced by :func:`encode_symbol`."""
    if not encoded.startswith("v1-"):
        raise ValueError("unsupported symbol encoding")
    payload = encoded[3:]
    padding = "=" * (-len(payload) % 4)
    try:
        symbol = base64.b64decode(payload + padding, altchars=b"-_", validate=True).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("invalid encoded symbol") from exc
    if not symbol or encode_symbol(symbol) != encoded:
        raise ValueError("invalid encoded symbol")
    return symbol


@dataclass(frozen=True, slots=True)
class MarketDataSeries:
    """Identity of one provider market-data series."""

    provider: str
    symbol: str
    interval: str
    adjustment_policy: str

    def __post_init__(self) -> None:
        if (
            self.provider != "yahoo"
            or self.interval != "1d"
            or self.adjustment_policy != "auto_adjusted"
        ):
            raise ValueError("Phase 1 supports only Yahoo auto-adjusted daily bars")
        if not self.symbol:
            raise ValueError("symbol must not be empty")

    @classmethod
    def yahoo_adjusted_daily(cls, symbol: str) -> MarketDataSeries:
        return cls(
            provider="yahoo",
            symbol=symbol,
            interval="1d",
            adjustment_policy="auto_adjusted",
        )

    @property
    def storage_key(self) -> str:
        return encode_symbol(self.symbol)


@dataclass(frozen=True, slots=True)
class ValidationOutcome:
    """Immutable summary of validating one adjusted daily-bar series."""

    is_valid: bool
    errors: tuple[str, ...]
    row_count: int
    data_cutoff: date | None


@dataclass(frozen=True, slots=True)
class CacheMetadata:
    """Versioned sidecar describing one active cache artifact."""

    provider: str
    symbol: str
    interval: str
    adjustment_policy: str
    schema_version: int
    data_cutoff: date
    last_incremental_refresh: datetime | None
    last_complete_refresh: datetime | None
    checksum: str


@dataclass(frozen=True, slots=True)
class AvailabilityPolicy:
    """When an auxiliary observation becomes knowable for a decision."""

    publication_lag_sessions: int = 1
    max_observation_lag_sessions: int = 1
    publication_time_known: bool = False

    def __post_init__(self) -> None:
        if self.publication_lag_sessions < 0:
            raise ValueError("publication lag must not be negative")
        if self.max_observation_lag_sessions < 0:
            raise ValueError("maximum observation lag must not be negative")
        if self.max_observation_lag_sessions < self.publication_lag_sessions:
            raise ValueError("maximum observation lag cannot be shorter than publication lag")
        if not self.publication_time_known and self.publication_lag_sessions < 1:
            raise ValueError("unknown publication time requires at least one session of lag")


@dataclass(frozen=True, slots=True)
class MarketDataRequirement:
    """A preregistered primary or auxiliary market-data dependency."""

    series: MarketDataSeries
    history_start: date
    role: Literal["primary", "auxiliary"]
    availability_policy: AvailabilityPolicy | None = None

    def __post_init__(self) -> None:
        if self.role not in {"primary", "auxiliary"}:
            raise ValueError("role must be primary or auxiliary")
        if self.role == "auxiliary" and self.availability_policy is None:
            raise ValueError("auxiliary requirements must declare an availability policy")
        if self.role == "primary" and self.availability_policy is not None:
            raise ValueError("primary requirements do not use an auxiliary availability policy")


@dataclass(frozen=True, slots=True)
class SignalDecisionTime:
    """The session and instant after which a daily-bar signal may be decided."""

    session: date
    decided_at: datetime

    def __post_init__(self) -> None:
        if self.decided_at.tzinfo is None:
            raise ValueError("signal decision time must be timezone-aware")
        local = self.decided_at.astimezone(_NEW_YORK)
        if local.date() != self.session:
            raise ValueError("signal decision time must be after the primary US session cutoff")
        from trading.market_data.calendar import PrimaryUSSessionCalendar

        cutoff = PrimaryUSSessionCalendar().decision_time(self.session)
        if self.decided_at < cutoff:
            raise ValueError("signal decision time must be after the primary US session cutoff")

    @classmethod
    def for_primary_session(
        cls,
        session: date,
        *,
        calendar: SessionCalendar | None = None,
    ) -> SignalDecisionTime:
        if calendar is None:
            from trading.market_data.calendar import PrimaryUSSessionCalendar

            calendar = PrimaryUSSessionCalendar()
        return cls(session, calendar.decision_time(session))
