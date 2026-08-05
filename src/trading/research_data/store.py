"""Content-addressed immutable research-data storage."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import zipfile
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from io import BytesIO
from pathlib import Path

import pandas as pd

from trading.market_data import (
    CacheMetadata,
    CsvMarketDataCache,
    MarketDataBundle,
    MarketDataRequirement,
    MarketDataSeries,
    SignalDecisionTime,
)
from trading.market_data.calendar import PrimaryUSSessionCalendar
from trading.market_data.validation import (
    canonical_daily_bar_csv_bytes,
    validate_daily_bars,
)
from trading.research_data.artifacts import (
    ImmutableBlobCorruptionError,
    read_definition_blob_bytes,
)
from trading.research_data.artifacts import (
    canonical_json_bytes as _canonical_json_bytes,
)
from trading.research_data.artifacts import (
    publish_immutable as _publish_immutable,
)
from trading.research_data.artifacts import (
    validate_digest as _validate_digest,
)
from trading.research_data.artifacts import (
    verify_definition_bytes as _verify_definition_bytes,
)
from trading.research_data.manifest_codec import (
    SnapshotManifestError,
)
from trading.research_data.manifest_codec import (
    manifest_body as _manifest_body,
)
from trading.research_data.manifest_codec import (
    manifest_from_bytes as _manifest_from_bytes,
)
from trading.research_data.manifest_codec import (
    manifest_payload as _manifest_payload,
)
from trading.research_data.models import (
    DataBlobRef,
    DefinitionBlobRef,
    GarbageCollectionReport,
    ResearchSnapshot,
    SnapshotBundleImport,
    SnapshotDataRef,
    SnapshotManifest,
)


class SnapshotEligibilityError(RuntimeError):
    """A disposable cache generation cannot become immutable research evidence."""


@dataclass(frozen=True, slots=True)
class _CapturedSeries:
    blob: DataBlobRef
    metadata: CacheMetadata


class ResearchDataStore:
    """Local immutable blobs addressed by the SHA-256 of their exact bytes."""

    def __init__(
        self,
        root: Path,
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.root = Path(root)
        self.now = now or (lambda: datetime.now(UTC))

    def data_blob_path(self, digest: str) -> Path:
        _validate_digest(digest)
        return self.root / "data" / "sha256" / digest[:2] / f"{digest}.csv"

    def publish_cache_series(
        self,
        cache: CsvMarketDataCache,
        series: MarketDataSeries,
    ) -> DataBlobRef:
        """Capture one fully refreshed cache generation without provider access."""
        return self._capture_cache_series(cache, series).blob

    def create_snapshot(
        self,
        cache: CsvMarketDataCache,
        requirements: Iterable[MarketDataRequirement],
        decision_time: SignalDecisionTime,
        *,
        definition: DefinitionBlobRef | None = None,
    ) -> SnapshotManifest:
        """Capture every declared series in one immutable snapshot manifest."""
        requirement_list = MarketDataBundle.validate_requirements(requirements)
        entries: list[SnapshotDataRef] = []
        for requirement in requirement_list:
            captured = self._capture_cache_series(cache, requirement.series)
            metadata = captured.metadata
            if metadata.data_cutoff != decision_time.session:
                raise SnapshotEligibilityError(
                    f"{requirement.series.symbol} cutoff {metadata.data_cutoff} does not match "
                    f"snapshot decision session {decision_time.session}"
                )
            complete = metadata.last_complete_refresh
            if complete is None:  # pragma: no cover - guarded by capture
                raise SnapshotEligibilityError("snapshot generation has no full refresh timestamp")
            entries.append(
                SnapshotDataRef(
                    series=requirement.series,
                    history_start=requirement.history_start,
                    role=requirement.role,
                    availability_policy=requirement.availability_policy,
                    data_cutoff=metadata.data_cutoff,
                    full_refresh_at=complete,
                    blob=captured.blob,
                )
            )
        current_time = self.now()
        if current_time.tzinfo is None:
            raise ValueError("snapshot clock must be timezone-aware")
        created_at = current_time.astimezone(UTC)
        body = _manifest_body(created_at, decision_time, tuple(entries), definition)
        snapshot_id = hashlib.sha256(_canonical_json_bytes(body)).hexdigest()
        return SnapshotManifest(
            snapshot_id=snapshot_id,
            schema_version=1,
            created_at=created_at,
            decision_time=decision_time,
            data=tuple(entries),
            definition=definition,
        )

    def write_manifest(self, manifest: SnapshotManifest, path: Path) -> Path:
        """Write a result-linked manifest without replacing different content."""
        path = Path(path)
        if not path.name.endswith(".snapshot.json"):
            raise SnapshotManifestError("snapshot manifest path must end with .snapshot.json")
        content = _canonical_json_bytes(_manifest_payload(manifest))
        _manifest_from_bytes(content)
        _publish_immutable(path, content, hashlib.sha256(content).hexdigest())
        return path

    def load_manifest(self, path: Path) -> SnapshotManifest:
        """Parse and verify one immutable snapshot manifest."""
        try:
            manifest = _manifest_from_bytes(Path(path).read_bytes())
        except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
            raise SnapshotManifestError(f"invalid snapshot manifest: {exc}") from exc
        expected_id = hashlib.sha256(
            _canonical_json_bytes(
                _manifest_body(
                    manifest.created_at,
                    manifest.decision_time,
                    manifest.data,
                    manifest.definition,
                )
            )
        ).hexdigest()
        if manifest.snapshot_id != expected_id:
            raise SnapshotManifestError("snapshot manifest identity does not match its content")
        return manifest

    def latest_manifest_for_definition(
        self,
        manifest_root: Path,
        definition: DefinitionBlobRef,
    ) -> Path:
        """Find the newest retained manifest for one exact research definition."""
        matches: list[tuple[SnapshotManifest, Path]] = []
        for path in sorted(Path(manifest_root).glob("*.snapshot.json")):
            manifest = self.load_manifest(path)
            if manifest.definition == definition:
                matches.append((manifest, path))
        if not matches:
            raise SnapshotManifestError(
                "no prepared snapshot manifest matches the current research definition"
            )
        _, path = max(
            matches,
            key=lambda item: (
                item[0].decision_time.session,
                item[0].created_at,
                item[0].snapshot_id,
            ),
        )
        return path

    def load_snapshot(self, manifest_path: Path) -> ResearchSnapshot:
        """Materialize a verified policy-safe bundle using immutable blobs only."""
        manifest = self.load_manifest(manifest_path)
        if manifest.definition is not None:
            self._read_definition_blob(manifest.definition)
        requirements: list[MarketDataRequirement] = []
        frames: dict[MarketDataSeries, pd.DataFrame] = {}
        for entry in manifest.data:
            if entry.data_cutoff != manifest.decision_time.session:
                raise SnapshotManifestError(
                    f"{entry.series.symbol} cutoff {entry.data_cutoff} does not match "
                    f"decision session {manifest.decision_time.session}"
                )
            blob_bytes = self._read_data_blob(entry.blob)
            frame = _parse_canonical_data_blob(blob_bytes, entry)
            requirements.append(
                MarketDataRequirement(
                    series=entry.series,
                    history_start=entry.history_start,
                    role=entry.role,
                    availability_policy=entry.availability_policy,
                )
            )
            frames[entry.series] = frame
        bundle = MarketDataBundle.from_requirements(
            requirements,
            frames,
            decision_time=manifest.decision_time,
        )
        return ResearchSnapshot(manifest=manifest, bundle=bundle)

    def export_bundle(
        self,
        manifest: SnapshotManifest,
        destination: Path,
        *,
        result: dict[str, object] | None = None,
    ) -> Path:
        """Export a verified manifest and all referenced immutable evidence."""
        manifest_bytes = _canonical_json_bytes(_manifest_payload(manifest))
        manifest = _manifest_from_bytes(manifest_bytes)
        data_content: dict[str, bytes] = {}
        for entry in manifest.data:
            content = self._read_data_blob(entry.blob)
            _parse_canonical_data_blob(content, entry)
            data_content[entry.blob.digest] = content
        definition_content: bytes | None = None
        if manifest.definition is not None:
            definition_content = self._read_definition_blob(manifest.definition)
        result_bytes = _canonical_json_bytes(result) if result is not None else None
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError(f"snapshot bundle already exists: {destination}")
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".snapshot-bundle-",
            suffix=".tmp",
            dir=destination.parent,
        )
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("manifest.json", manifest_bytes)
                for digest, content in sorted(data_content.items()):
                    archive.writestr(f"data/{digest}.csv", content)
                if manifest.definition is not None and definition_content is not None:
                    archive.writestr(
                        f"definitions/{manifest.definition.digest}.json",
                        definition_content,
                    )
                if result_bytes is not None:
                    archive.writestr("result.json", result_bytes)
            try:
                os.link(temporary, destination)
            except FileExistsError:
                raise FileExistsError(f"snapshot bundle already exists: {destination}") from None
        finally:
            temporary.unlink(missing_ok=True)
        return destination

    def import_bundle(
        self,
        bundle_path: Path,
        *,
        manifest_path: Path,
    ) -> SnapshotBundleImport:
        """Verify a portable bundle before publishing its immutable artifacts."""
        try:
            with zipfile.ZipFile(bundle_path, "r") as archive:
                names = archive.namelist()
                if len(names) != len(set(names)):
                    raise SnapshotManifestError("snapshot bundle contains duplicate entries")
                manifest_bytes = archive.read("manifest.json")
                manifest = _manifest_from_bytes(manifest_bytes)
                expected_names = {"manifest.json"}
                data_content: dict[str, bytes] = {}
                for entry in manifest.data:
                    name = f"data/{entry.blob.digest}.csv"
                    expected_names.add(name)
                    content = archive.read(name)
                    _parse_canonical_data_blob(content, entry)
                    data_content[entry.blob.digest] = content
                definition_content: bytes | None = None
                if manifest.definition is not None:
                    name = f"definitions/{manifest.definition.digest}.json"
                    expected_names.add(name)
                    definition_content = archive.read(name)
                    _verify_definition_bytes(definition_content, manifest.definition)
                result: dict[str, object] | None = None
                if "result.json" in names:
                    expected_names.add("result.json")
                    loaded_result = json.loads(archive.read("result.json"))
                    if not isinstance(loaded_result, dict):
                        raise SnapshotManifestError("bundle result must be a JSON object")
                    result = loaded_result
                if set(names) != expected_names:
                    raise SnapshotManifestError("snapshot bundle has missing or unexpected entries")
        except (KeyError, OSError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
            raise SnapshotManifestError(f"invalid snapshot bundle: {exc}") from exc

        for digest, content in data_content.items():
            _publish_immutable(self.data_blob_path(digest), content, digest)
        if manifest.definition is not None and definition_content is not None:
            _publish_immutable(
                self._definition_blob_path(manifest.definition.digest),
                definition_content,
                manifest.definition.digest,
            )
        written_manifest = self.write_manifest(manifest, manifest_path)
        return SnapshotBundleImport(
            manifest=manifest,
            manifest_path=written_manifest,
            result=result,
        )

    def collect_garbage(
        self,
        *,
        manifest_roots: Iterable[Path],
        grace_period: timedelta,
        apply: bool = False,
    ) -> GarbageCollectionReport:
        """Plan or explicitly delete only old blobs unreferenced by retained manifests."""
        if grace_period < timedelta(0):
            raise ValueError("garbage-collection grace period must not be negative")
        roots = tuple(Path(root) for root in manifest_roots)
        if not roots:
            raise ValueError("garbage collection requires at least one retained-manifest root")
        manifest_paths: set[Path] = set()
        for root in roots:
            if not root.is_dir():
                raise FileNotFoundError(f"retained-manifest root is missing: {root}")
            manifest_paths.update(root.rglob("*.snapshot.json"))
        referenced: set[Path] = set()
        for manifest_path in sorted(manifest_paths):
            manifest = self.load_manifest(manifest_path)
            referenced.update(self.data_blob_path(entry.blob.digest) for entry in manifest.data)
            if manifest.definition is not None:
                referenced.add(self._definition_blob_path(manifest.definition.digest))

        current_time = self.now()
        if current_time.tzinfo is None:
            raise ValueError("garbage-collection clock must be timezone-aware")
        cutoff = current_time.astimezone(UTC) - grace_period
        all_blobs = sorted(
            [*self.root.glob("data/sha256/*/*.csv"), *self.root.glob("definitions/sha256/*/*.json")]
        )
        protected = tuple(path for path in all_blobs if path in referenced)
        candidates = tuple(
            path
            for path in all_blobs
            if path not in referenced
            and datetime.fromtimestamp(path.stat().st_mtime, tz=UTC) <= cutoff
        )
        deleted: tuple[Path, ...] = ()
        if apply:
            removed: list[Path] = []
            for path in candidates:
                path.unlink()
                removed.append(path)
            deleted = tuple(removed)
        return GarbageCollectionReport(
            candidates=candidates,
            deleted=deleted,
            protected=protected,
        )

    def _read_data_blob(self, reference: DataBlobRef) -> bytes:
        path = self.data_blob_path(reference.digest)
        try:
            content = path.read_bytes()
        except OSError as exc:
            raise ImmutableBlobCorruptionError(
                f"immutable blob {reference.digest} is missing or unreadable"
            ) from exc
        if len(content) != reference.byte_count:
            raise ImmutableBlobCorruptionError(
                f"immutable blob {reference.digest} size does not match manifest"
            )
        if hashlib.sha256(content).hexdigest() != reference.digest:
            raise ImmutableBlobCorruptionError(
                f"immutable blob {reference.digest} failed checksum verification"
            )
        return content

    def _definition_blob_path(self, digest: str) -> Path:
        _validate_digest(digest)
        return self.root / "definitions" / "sha256" / digest[:2] / f"{digest}.json"

    def _read_definition_blob(self, reference: DefinitionBlobRef) -> bytes:
        return read_definition_blob_bytes(
            self._definition_blob_path(reference.digest),
            reference,
        )

    def _capture_cache_series(
        self,
        cache: CsvMarketDataCache,
        series: MarketDataSeries,
    ) -> _CapturedSeries:
        with cache.lock(series):
            cached = cache.load_locked(series)
            if cached is None:
                raise SnapshotEligibilityError(f"no active cache exists for {series.symbol}")
            metadata = cached.metadata
            complete = metadata.last_complete_refresh
            incremental = metadata.last_incremental_refresh
            if complete is None or (incremental is not None and incremental > complete):
                raise SnapshotEligibilityError(
                    f"{series.symbol} cache is not a fully refreshed snapshot-eligible generation"
                )
            csv_bytes = cache.paths(series).csv.read_bytes()
            digest = hashlib.sha256(csv_bytes).hexdigest()
            if digest != metadata.checksum:
                raise SnapshotEligibilityError(
                    f"{series.symbol} cache changed while preparing snapshot evidence"
                )
            row_count = len(cached.bars)

        _publish_immutable(self.data_blob_path(digest), csv_bytes, digest)
        return _CapturedSeries(
            DataBlobRef(digest=digest, byte_count=len(csv_bytes), row_count=row_count),
            metadata,
        )


def _verify_blob_bytes(content: bytes, reference: DataBlobRef) -> None:
    if len(content) != reference.byte_count:
        raise ImmutableBlobCorruptionError(
            f"immutable blob {reference.digest} size does not match manifest"
        )
    if hashlib.sha256(content).hexdigest() != reference.digest:
        raise ImmutableBlobCorruptionError(
            f"immutable blob {reference.digest} failed checksum verification"
        )


def _parse_canonical_data_blob(
    content: bytes,
    entry: SnapshotDataRef,
) -> pd.DataFrame:
    _verify_blob_bytes(content, entry.blob)
    try:
        frame = pd.read_csv(
            BytesIO(content),
            parse_dates=["Date"],
            index_col="Date",
        )
    except (TypeError, ValueError) as exc:
        raise ImmutableBlobCorruptionError(
            f"invalid immutable CSV blob {entry.blob.digest}: {exc}"
        ) from exc
    if frame.empty:
        raise ImmutableBlobCorruptionError(
            f"immutable blob {entry.blob.digest} contains no daily bars"
        )
    normalized, outcome = validate_daily_bars(frame)
    if not outcome.is_valid:
        raise ImmutableBlobCorruptionError(
            f"invalid immutable CSV blob {entry.blob.digest}: " + "; ".join(outcome.errors)
        )
    calendar = PrimaryUSSessionCalendar()
    expected_sessions = calendar.sessions_in_range(
        normalized.index.min().date(),
        normalized.index.max().date(),
    )
    normalized, outcome = validate_daily_bars(
        normalized,
        expected_sessions=expected_sessions,
    )
    if not outcome.is_valid:
        raise ImmutableBlobCorruptionError(
            f"invalid immutable CSV blob {entry.blob.digest}: " + "; ".join(outcome.errors)
        )
    if canonical_daily_bar_csv_bytes(normalized) != content:
        raise ImmutableBlobCorruptionError(
            f"immutable blob {entry.blob.digest} is not canonically serialized"
        )
    if len(normalized) != entry.blob.row_count:
        raise ImmutableBlobCorruptionError(
            f"immutable blob {entry.blob.digest} row count does not match manifest"
        )
    if outcome.data_cutoff != entry.data_cutoff:
        raise SnapshotManifestError(
            f"{entry.series.symbol} blob cutoff does not match snapshot manifest"
        )
    return normalized
