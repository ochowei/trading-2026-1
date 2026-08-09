"""CSV cache persistence, locking, atomic publication, and quarantine."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import tempfile
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd

from trading.market_data.calendar import PrimaryUSSessionCalendar
from trading.market_data.contracts import RefreshKind, SessionCalendar
from trading.market_data.models import (
    CacheMetadata,
    CoverageMode,
    MarketDataCoveragePolicy,
    MarketDataSeries,
)
from trading.market_data.validation import (
    canonical_daily_bar_csv_bytes,
    validate_daily_bars,
)

CACHE_SCHEMA_VERSION = 1


class CacheCorruptionError(RuntimeError):
    """The active cache failed identity, checksum, schema, or bar validation."""


class MarketDataValidationError(RuntimeError):
    """New provider data is not safe to publish."""


class MarketDataLockTimeout(TimeoutError):
    """A per-series cache lock could not be acquired within its bounded wait."""


@dataclass(frozen=True, slots=True)
class CachePaths:
    csv: Path
    metadata: Path
    lock: Path


@dataclass(frozen=True, slots=True)
class CachedSeries:
    _bars: pd.DataFrame
    metadata: CacheMetadata

    @property
    def bars(self) -> pd.DataFrame:
        """Return a defensive copy so callers cannot mutate cached state."""
        return self._bars.copy(deep=True)


@dataclass(frozen=True, slots=True)
class CacheInspection:
    """Read-only diagnostic result that never quarantines or creates files."""

    state: str
    metadata: CacheMetadata | None = None
    errors: tuple[str, ...] = ()


class CsvMarketDataCache:
    """One canonical CSV and metadata sidecar for each market-data series."""

    def __init__(
        self,
        root: Path,
        quarantine_root: Path,
        *,
        lock_timeout_seconds: float = 10.0,
        lock_poll_seconds: float = 0.05,
        calendar: SessionCalendar | None = None,
    ) -> None:
        self.root = Path(root)
        self.quarantine_root = Path(quarantine_root)
        self.lock_timeout_seconds = lock_timeout_seconds
        self.lock_poll_seconds = lock_poll_seconds
        self.calendar = calendar or PrimaryUSSessionCalendar()

    def paths(self, series: MarketDataSeries) -> CachePaths:
        directory = self.root / series.provider / series.interval / series.adjustment_policy
        stem = series.storage_key
        return CachePaths(
            csv=directory / f"{stem}.csv",
            metadata=directory / f"{stem}.metadata.json",
            lock=directory / f"{stem}.lock",
        )

    def generation_token(self, series: MarketDataSeries) -> tuple[int, int, int, int] | None:
        """Return a lock-free identity for the active metadata generation, if present."""
        try:
            stat = self.paths(series).metadata.stat()
        except FileNotFoundError:
            return None
        return (stat.st_dev, stat.st_ino, stat.st_mtime_ns, stat.st_size)

    @contextmanager
    def lock(self, series: MarketDataSeries) -> Iterator[None]:
        paths = self.paths(series)
        paths.lock.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(paths.lock, os.O_CREAT | os.O_RDWR, 0o600)
        deadline = time.monotonic() + self.lock_timeout_seconds
        try:
            while True:
                try:
                    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise MarketDataLockTimeout(
                            f"timed out waiting for cache lock for {series.symbol}"
                        ) from None
                    time.sleep(self.lock_poll_seconds)
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    @contextmanager
    def read_lock(self, series: MarketDataSeries) -> Iterator[None]:
        """Acquire a shared lock only when its existing lock file is present."""
        path = self.paths(series).lock
        if not path.exists():
            yield
            return
        descriptor = os.open(path, os.O_RDONLY)
        deadline = time.monotonic() + self.lock_timeout_seconds
        try:
            while True:
                try:
                    fcntl.flock(descriptor, fcntl.LOCK_SH | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise MarketDataLockTimeout(
                            f"timed out waiting for cache lock for {series.symbol}"
                        ) from None
                    time.sleep(self.lock_poll_seconds)
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    def load(
        self,
        series: MarketDataSeries,
        *,
        coverage_policy: MarketDataCoveragePolicy | None = None,
    ) -> CachedSeries | None:
        with self.lock(series):
            try:
                return self.load_locked(series, coverage_policy=coverage_policy)
            except CacheCorruptionError:
                self.quarantine_locked(series)
                raise

    def inspect(
        self,
        series: MarketDataSeries,
        *,
        coverage_policy: MarketDataCoveragePolicy | None = None,
    ) -> CacheInspection:
        """Inspect active artifacts without creating files, writing, or downloading."""
        try:
            with self.read_lock(series):
                return self.inspect_locked(series, coverage_policy=coverage_policy)
        except MarketDataLockTimeout as exc:
            return CacheInspection("busy", errors=(str(exc),))

    def inspect_locked(
        self,
        series: MarketDataSeries,
        *,
        coverage_policy: MarketDataCoveragePolicy | None = None,
    ) -> CacheInspection:
        try:
            cached = self.load_locked(series, coverage_policy=coverage_policy)
        except (CacheCorruptionError, OSError) as exc:
            return CacheInspection("corrupt", errors=(str(exc),))
        if cached is None:
            return CacheInspection("missing")
        return CacheInspection("valid", metadata=cached.metadata)

    def load_locked(
        self,
        series: MarketDataSeries,
        *,
        coverage_policy: MarketDataCoveragePolicy | None = None,
    ) -> CachedSeries | None:
        policy = coverage_policy or MarketDataCoveragePolicy.xnys()
        paths = self.paths(series)
        if not paths.csv.exists() and not paths.metadata.exists():
            return None
        if not paths.csv.exists() or not paths.metadata.exists():
            raise CacheCorruptionError("cache CSV and metadata sidecar must both exist")
        try:
            raw_metadata = json.loads(paths.metadata.read_text(encoding="utf-8"))
            metadata = _metadata_from_dict(raw_metadata)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise CacheCorruptionError(f"invalid cache metadata: {exc}") from exc
        if (
            metadata.provider != series.provider
            or metadata.symbol != series.symbol
            or metadata.interval != series.interval
            or metadata.adjustment_policy != series.adjustment_policy
            or metadata.schema_version != CACHE_SCHEMA_VERSION
        ):
            raise CacheCorruptionError("cache metadata identity or schema mismatch")
        if metadata.coverage_policy != policy.mode.value:
            raise CacheCorruptionError("cache coverage policy mismatch")
        csv_bytes = paths.csv.read_bytes()
        checksum = hashlib.sha256(csv_bytes).hexdigest()
        if checksum != metadata.checksum:
            raise CacheCorruptionError("cache checksum mismatch")
        try:
            frame = pd.read_csv(paths.csv, parse_dates=["Date"], index_col="Date")
        except (OSError, ValueError) as exc:
            raise CacheCorruptionError(f"invalid cache CSV: {exc}") from exc
        normalized, outcome = validate_daily_bars(
            frame,
            expected_sessions=self._expected_for(frame, policy),
        )
        if not outcome.is_valid:
            raise CacheCorruptionError("invalid cache rows: " + "; ".join(outcome.errors))
        if canonical_daily_bar_csv_bytes(normalized) != csv_bytes:
            raise CacheCorruptionError("cache CSV is not canonically serialized")
        if outcome.data_cutoff != metadata.data_cutoff:
            raise CacheCorruptionError("cache data cutoff does not match metadata")
        return CachedSeries(normalized, metadata)

    def publish(
        self,
        series: MarketDataSeries,
        frame: pd.DataFrame,
        *,
        refresh_kind: RefreshKind | str,
        refreshed_at: datetime,
        coverage_policy: MarketDataCoveragePolicy | None = None,
    ) -> CachedSeries:
        policy = coverage_policy or MarketDataCoveragePolicy.xnys()
        with self.lock(series):
            try:
                previous = self.load_locked(series, coverage_policy=policy)
            except CacheCorruptionError:
                self.quarantine_locked(series)
                previous = None
            return self.publish_locked(
                series,
                frame,
                refresh_kind=refresh_kind,
                refreshed_at=refreshed_at,
                previous_metadata=previous.metadata if previous else None,
                coverage_policy=policy,
            )

    def publish_locked(
        self,
        series: MarketDataSeries,
        frame: pd.DataFrame,
        *,
        refresh_kind: RefreshKind | str,
        refreshed_at: datetime,
        previous_metadata: CacheMetadata | None = None,
        coverage_policy: MarketDataCoveragePolicy | None = None,
    ) -> CachedSeries:
        policy = coverage_policy or MarketDataCoveragePolicy.xnys()
        try:
            kind = RefreshKind(refresh_kind)
        except ValueError:
            raise ValueError("refresh_kind must be incremental or full") from None
        if refreshed_at.tzinfo is None:
            raise ValueError("refreshed_at must be timezone-aware")
        normalized, outcome = validate_daily_bars(
            frame,
            expected_sessions=self._expected_for(frame, policy),
        )
        if not outcome.is_valid or outcome.data_cutoff is None:
            raise MarketDataValidationError("; ".join(outcome.errors) or "market data is empty")
        csv_bytes = canonical_daily_bar_csv_bytes(normalized)
        checksum = hashlib.sha256(csv_bytes).hexdigest()
        timestamp = refreshed_at.astimezone(UTC)
        metadata = CacheMetadata(
            provider=series.provider,
            symbol=series.symbol,
            interval=series.interval,
            adjustment_policy=series.adjustment_policy,
            schema_version=CACHE_SCHEMA_VERSION,
            data_cutoff=outcome.data_cutoff,
            last_incremental_refresh=(
                timestamp
                if kind is RefreshKind.INCREMENTAL
                else (previous_metadata.last_incremental_refresh if previous_metadata else None)
            ),
            last_complete_refresh=(
                timestamp
                if kind is RefreshKind.FULL
                else (previous_metadata.last_complete_refresh if previous_metadata else None)
            ),
            checksum=checksum,
            coverage_policy=policy.mode.value,
        )
        metadata_bytes = _metadata_bytes(metadata)
        paths = self.paths(series)
        paths.csv.parent.mkdir(parents=True, exist_ok=True)
        csv_temp: str | None = None
        metadata_temp: str | None = None
        try:
            csv_temp = _write_temp(paths.csv.parent, csv_bytes)
            metadata_temp = _write_temp(paths.metadata.parent, metadata_bytes)
            _replace_pair_with_rollback(paths, csv_temp, metadata_temp)
        finally:
            if csv_temp is not None:
                Path(csv_temp).unlink(missing_ok=True)
            if metadata_temp is not None:
                Path(metadata_temp).unlink(missing_ok=True)
        return CachedSeries(normalized, metadata)

    def _expected_for(
        self,
        frame: pd.DataFrame,
        coverage_policy: MarketDataCoveragePolicy | None = None,
    ) -> pd.DatetimeIndex | None:
        policy = coverage_policy or MarketDataCoveragePolicy.xnys()
        if policy.mode is CoverageMode.PROVIDER_OBSERVATIONS:
            return None
        if "Date" in frame.columns:
            index = pd.DatetimeIndex(pd.to_datetime(frame["Date"]))
        else:
            index = pd.DatetimeIndex(pd.to_datetime(frame.index))
        if index.tz is not None:
            index = index.tz_localize(None)
        normalized = index.normalize()
        return self.calendar.sessions_in_range(
            normalized.min().date(),
            normalized.max().date(),
        )

    def quarantine_locked(self, series: MarketDataSeries) -> Path | None:
        paths = self.paths(series)
        existing = [path for path in (paths.csv, paths.metadata) if path.exists()]
        if not existing:
            return None
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
        destination = self.quarantine_root / series.storage_key / f"{stamp}-{uuid.uuid4().hex}"
        destination.mkdir(parents=True, exist_ok=False)
        for path in existing:
            os.replace(path, destination / path.name)
        return destination


def _metadata_bytes(metadata: CacheMetadata) -> bytes:
    payload = asdict(metadata)
    payload["data_cutoff"] = metadata.data_cutoff.isoformat()
    payload["last_incremental_refresh"] = _format_timestamp(metadata.last_incremental_refresh)
    payload["last_complete_refresh"] = _format_timestamp(metadata.last_complete_refresh)
    return (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _format_timestamp(value: datetime | None) -> str | None:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z") if value else None


def _parse_timestamp(value: object) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("refresh timestamp must be a string or null")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("refresh timestamp must include a timezone")
    return parsed.astimezone(UTC)


def _metadata_from_dict(payload: dict[str, object]) -> CacheMetadata:
    return CacheMetadata(
        provider=str(payload["provider"]),
        symbol=str(payload["symbol"]),
        interval=str(payload["interval"]),
        adjustment_policy=str(payload["adjustment_policy"]),
        schema_version=int(payload["schema_version"]),
        data_cutoff=date.fromisoformat(str(payload["data_cutoff"])),
        last_incremental_refresh=_parse_timestamp(payload["last_incremental_refresh"]),
        last_complete_refresh=_parse_timestamp(payload["last_complete_refresh"]),
        checksum=str(payload["checksum"]),
        coverage_policy=str(payload.get("coverage_policy", CoverageMode.XNYS_SESSIONS.value)),
    )


def _write_temp(directory: Path, content: bytes) -> str:
    descriptor, name = tempfile.mkstemp(prefix=".market-data-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        Path(name).unlink(missing_ok=True)
        raise
    return name


def _replace_pair_with_rollback(
    paths: CachePaths,
    csv_temp: str,
    metadata_temp: str,
) -> None:
    """Replace the active pair and restore its prior generation on a partial failure."""
    previous_csv = paths.csv.read_bytes() if paths.csv.exists() else None
    previous_metadata = paths.metadata.read_bytes() if paths.metadata.exists() else None
    csv_replaced = False
    metadata_replaced = False
    try:
        os.replace(csv_temp, paths.csv)
        csv_replaced = True
        os.replace(metadata_temp, paths.metadata)
        metadata_replaced = True
    except BaseException:
        try:
            if csv_replaced:
                _restore_previous(paths.csv, previous_csv)
            if metadata_replaced:
                _restore_previous(paths.metadata, previous_metadata)
        except BaseException as rollback_error:
            raise RuntimeError(
                "cache publication failed and the previous active generation could not be restored"
            ) from rollback_error
        raise


def _restore_previous(path: Path, content: bytes | None) -> None:
    if content is None:
        path.unlink(missing_ok=True)
        return
    restore_temp = _write_temp(path.parent, content)
    try:
        os.replace(restore_temp, path)
    finally:
        Path(restore_temp).unlink(missing_ok=True)
