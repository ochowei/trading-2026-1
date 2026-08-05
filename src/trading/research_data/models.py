"""Immutable values describing reproducibility artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Literal

from trading.market_data import (
    AvailabilityPolicy,
    MarketDataBundle,
    MarketDataSeries,
    SignalDecisionTime,
)


@dataclass(frozen=True, slots=True)
class DataBlobRef:
    """Identity and size of one canonical adjusted daily-bar CSV blob."""

    digest: str
    byte_count: int
    row_count: int


@dataclass(frozen=True, slots=True)
class SnapshotDataRef:
    """One declared market-data dependency captured by a snapshot."""

    series: MarketDataSeries
    history_start: date
    role: Literal["primary", "auxiliary"]
    availability_policy: AvailabilityPolicy | None
    data_cutoff: date
    full_refresh_at: datetime
    blob: DataBlobRef


@dataclass(frozen=True, slots=True)
class SnapshotManifest:
    """Immutable identity of all market data used by one research execution."""

    snapshot_id: str
    schema_version: int
    created_at: datetime
    decision_time: SignalDecisionTime
    data: tuple[SnapshotDataRef, ...]
    definition: DefinitionBlobRef | None = None


@dataclass(frozen=True, slots=True)
class ResearchSnapshot:
    """Verified immutable evidence materialized as a policy-safe bundle."""

    manifest: SnapshotManifest
    bundle: MarketDataBundle


@dataclass(frozen=True, slots=True)
class DefinitionBlobRef:
    """Exact definition content linked to one semantic fingerprint."""

    digest: str
    byte_count: int
    fingerprint: str


@dataclass(frozen=True, slots=True)
class ResearchDefinitionSnapshot:
    """A semantic research identity backed by exact immutable source content."""

    fingerprint: str
    blob: DefinitionBlobRef


@dataclass(frozen=True, slots=True)
class SnapshotBundleImport:
    """Verified artifacts restored from a portable snapshot bundle."""

    manifest: SnapshotManifest
    manifest_path: Path
    result: dict[str, object] | None


@dataclass(frozen=True, slots=True)
class GarbageCollectionReport:
    """Reference-aware immutable-blob GC plan and its explicit effects."""

    candidates: tuple[Path, ...]
    deleted: tuple[Path, ...]
    protected: tuple[Path, ...]
