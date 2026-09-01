"""Canonical result namespaces and digest-bound historical path migration."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from trading.core.accounting import canonical_json_bytes

PATH_MIGRATION_SCHEMA_VERSION = 2
PATH_MIGRATION_REGISTRY = Path("results/registries/path-migrations.json")
PATH_MIGRATION_VERSION = "v010"
SUPPORTED_MIGRATION_VERSIONS = frozenset({"v009", PATH_MIGRATION_VERSION})
MAX_MIGRATION_HOPS = 2


class ResultPathMigrationError(ValueError):
    """Raised when a result path or migration registry fails closed validation."""


@dataclass(frozen=True, slots=True)
class ResultPathMigration:
    """One exact old-to-new tracked result path mapping."""

    old_path: str
    new_path: str
    sha256: str
    artifact_class: str
    migration_version: str = PATH_MIGRATION_VERSION

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> ResultPathMigration:
        required = {
            "old_path",
            "new_path",
            "sha256",
            "artifact_class",
            "migration_version",
        }
        if set(value) != required:
            raise ResultPathMigrationError("path migration entry has an invalid field set")
        entry = cls(**{field: str(value[field]) for field in required})
        entry.validate()
        return entry

    def validate(self) -> None:
        old = _safe_repository_path(self.old_path, label="old path")
        new = _safe_repository_path(self.new_path, label="new path")
        if old == new:
            raise ResultPathMigrationError("path migration source and destination must differ")
        if old.parts[0] != "results":
            raise ResultPathMigrationError("path migration source must be under results/")
        if new.parts[0] not in {"results", "legacy"}:
            raise ResultPathMigrationError(
                "path migration destination must be under results/ or legacy/"
            )
        if len(self.sha256) != 64 or any(char not in "0123456789abcdef" for char in self.sha256):
            raise ResultPathMigrationError("path migration sha256 is invalid")
        if not self.artifact_class.strip():
            raise ResultPathMigrationError("path migration artifact class is empty")
        if self.migration_version not in SUPPORTED_MIGRATION_VERSIONS:
            raise ResultPathMigrationError("path migration version is unsupported")

    def as_dict(self) -> dict[str, str]:
        return {
            "old_path": self.old_path,
            "new_path": self.new_path,
            "sha256": self.sha256,
            "artifact_class": self.artifact_class,
            "migration_version": self.migration_version,
        }


def experiment_result_directory(results_root: Path, experiment_name: str) -> Path:
    """Reject recreation of the retired legacy-experiment result namespace."""
    raise ResultPathMigrationError(
        "legacy experiment result publication is retired; results/experiment-results is forbidden"
    )


def research_trial_directory(results_root: Path, identity: str) -> Path:
    """Return the canonical workflow-native family/trial result directory."""
    normalized = identity.replace("--", "/", 1) if "/" not in identity else identity
    parts = normalized.split("/")
    if len(parts) != 2:
        raise ResultPathMigrationError("research identity must be <family>/<trial>")
    return (
        Path(results_root) / "research-trials" / _safe_identity(parts[0]) / _safe_identity(parts[1])
    )


def migration_evidence_directory(results_root: Path, experiment_name: str) -> Path:
    """Reject new parity publication after retirement of legacy experiment migration."""
    raise ResultPathMigrationError(
        "legacy experiment migration publication is retired; retained evidence is read-only"
    )


def trial_registry_path(results_root: Path = Path("results")) -> Path:
    """Return the canonical shared formal trial registry path."""
    return Path(results_root) / "registries" / "trial_registry.json"


def research_evidence_directory(results_root: Path = Path("results")) -> Path:
    return Path(results_root) / "evidence" / "research"


def qualification_evidence_directory(results_root: Path = Path("results")) -> Path:
    return Path(results_root) / "evidence" / "qualification"


def load_path_migrations(
    repository_root: Path = Path("."),
    *,
    require_destinations: bool = True,
) -> tuple[ResultPathMigration, ...]:
    """Load and fully validate the tracked append-only path-migration registry."""
    root = Path(repository_root).resolve()
    registry = root / PATH_MIGRATION_REGISTRY
    if not registry.exists():
        return ()
    try:
        payload = json.loads(registry.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResultPathMigrationError(f"cannot read path migration registry: {exc}") from exc
    if not isinstance(payload, dict) or set(payload) != {"schema_version", "migrations"}:
        raise ResultPathMigrationError("path migration registry has an invalid top-level shape")
    if payload.get("schema_version") not in {1, PATH_MIGRATION_SCHEMA_VERSION}:
        raise ResultPathMigrationError("path migration registry schema version is unsupported")
    raw = payload.get("migrations")
    if not isinstance(raw, list) or not all(isinstance(item, dict) for item in raw):
        raise ResultPathMigrationError("path migration registry entries must be objects")
    entries = tuple(ResultPathMigration.from_mapping(item) for item in raw)
    if tuple(entry.old_path for entry in entries) != tuple(
        sorted(entry.old_path for entry in entries)
    ):
        raise ResultPathMigrationError("path migration registry must be sorted by old path")
    _validate_migration_set(entries)
    if require_destinations:
        by_old_path = {entry.old_path: entry for entry in entries}
        for entry in entries:
            terminal = _terminal_destination(entry, by_old_path)
            destination = root / terminal
            if not destination.is_file():
                raise ResultPathMigrationError(
                    f"migrated result destination is missing: {terminal}"
                )
            if _sha256(destination) != entry.sha256:
                raise ResultPathMigrationError(
                    f"migrated result destination digest drifted: {terminal}"
                )
    return entries


def resolve_result_path(path: Path, *, repository_root: Path | None = None) -> Path:
    """Resolve one exact existing or bounded digest-bound historical result path."""
    requested = Path(path)
    if requested.is_file():
        return requested.resolve()
    root = _repository_root_for(requested, repository_root)
    absolute = requested.resolve() if requested.is_absolute() else (root / requested).resolve()
    try:
        identity = absolute.relative_to(root).as_posix()
    except ValueError as exc:
        raise ResultPathMigrationError(f"result path is outside repository root: {path}") from exc
    entries = load_path_migrations(root)
    matches = [entry for entry in entries if entry.old_path == identity]
    if len(matches) != 1:
        raise ResultPathMigrationError(f"historical result path has no exact migration: {identity}")
    terminal = _terminal_destination(matches[0], {entry.old_path: entry for entry in entries})
    return (root / terminal).resolve()


def apply_result_path_migration(
    entries: Iterable[ResultPathMigration],
    *,
    repository_root: Path = Path("."),
) -> Path:
    """Append migrations atomically and move byte-identical tracked artifacts."""
    root = Path(repository_root).resolve()
    requested = tuple(sorted(entries, key=lambda entry: entry.old_path))
    _validate_migration_set(requested)
    registry_path = root / PATH_MIGRATION_REGISTRY
    existing_registry_bytes = registry_path.read_bytes() if registry_path.exists() else None
    existing = load_path_migrations(root) if registry_path.exists() else ()
    if existing:
        requested_by_old = {entry.old_path: entry for entry in requested}
        if any(requested_by_old.get(entry.old_path) != entry for entry in existing):
            raise ResultPathMigrationError("path migration registry changed an existing entry")
    existing_old_paths = {entry.old_path for entry in existing}
    new_entries = tuple(entry for entry in requested if entry.old_path not in existing_old_paths)

    if not new_entries:
        by_old_path = {entry.old_path: entry for entry in requested}
        for entry in requested:
            source = root / entry.old_path
            if source.exists() and _sha256(source) != entry.sha256:
                raise ResultPathMigrationError(f"migration retry source drifted: {entry.old_path}")
            destination = root / _terminal_destination(entry, by_old_path)
            if not destination.is_file() or _sha256(destination) != entry.sha256:
                raise ResultPathMigrationError(
                    f"migration retry destination is invalid: {destination.relative_to(root)}"
                )
        for entry in requested:
            (root / entry.old_path).unlink(missing_ok=True)
        _remove_empty_result_directories(root / "results")
        load_path_migrations(root)
        return registry_path

    sources: list[tuple[ResultPathMigration, Path, Path]] = []
    for entry in new_entries:
        entry.validate()
        source = root / entry.old_path
        destination = root / entry.new_path
        if not source.is_file():
            raise ResultPathMigrationError(f"migration source is missing: {entry.old_path}")
        if _sha256(source) != entry.sha256:
            raise ResultPathMigrationError(f"migration source digest drifted: {entry.old_path}")
        if destination.exists():
            raise ResultPathMigrationError(
                f"migration destination already exists: {entry.new_path}"
            )
        sources.append((entry, source, destination))

    created: list[Path] = []
    try:
        for entry, source, destination in sources:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            created.append(destination)
            if _sha256(destination) != entry.sha256:
                raise ResultPathMigrationError(
                    f"migration destination verification failed: {entry.new_path}"
                )
        content = canonical_json_bytes(
            {
                "schema_version": PATH_MIGRATION_SCHEMA_VERSION,
                "migrations": [entry.as_dict() for entry in requested],
            }
        )
        _atomic_write(registry_path, content)
        load_path_migrations(root)
    except Exception:
        if existing_registry_bytes is not None:
            _atomic_write(registry_path, existing_registry_bytes)
        else:
            registry_path.unlink(missing_ok=True)
        for destination in reversed(created):
            destination.unlink(missing_ok=True)
        raise

    for _entry, source, _destination in sources:
        source.unlink()
    _remove_empty_result_directories(root / "results")
    load_path_migrations(root)
    return registry_path


def _validate_migration_set(entries: tuple[ResultPathMigration, ...]) -> None:
    old_paths = [entry.old_path for entry in entries]
    new_paths = [entry.new_path for entry in entries]
    if len(old_paths) != len(set(old_paths)):
        raise ResultPathMigrationError("path migration registry has duplicate old paths")
    if len(new_paths) != len(set(new_paths)):
        raise ResultPathMigrationError("path migration registry has duplicate new paths")
    by_old_path = {entry.old_path: entry for entry in entries}
    for entry in entries:
        _terminal_destination(entry, by_old_path)


def _terminal_destination(
    entry: ResultPathMigration,
    by_old_path: Mapping[str, ResultPathMigration],
) -> str:
    """Resolve one bounded, byte-identical chain to its terminal destination."""
    origin = entry
    current = entry
    seen = {current.old_path}
    hops = 1
    while current.new_path in by_old_path:
        if hops >= MAX_MIGRATION_HOPS:
            raise ResultPathMigrationError("path migration chain exceeds the supported hop limit")
        following = by_old_path[current.new_path]
        if following.old_path in seen:
            raise ResultPathMigrationError("path migration registry contains a cycle")
        if (current.migration_version, following.migration_version) != ("v009", "v010"):
            raise ResultPathMigrationError("path migration chain has an invalid version order")
        if not _artifact_classes_are_compatible(origin, following):
            raise ResultPathMigrationError("path migration chain changes the artifact class")
        if following.sha256 != origin.sha256:
            raise ResultPathMigrationError("path migration chain changes the artifact digest")
        seen.add(following.old_path)
        current = following
        hops += 1
    return current.new_path


def _artifact_classes_are_compatible(
    origin: ResultPathMigration,
    following: ResultPathMigration,
) -> bool:
    if following.artifact_class == origin.artifact_class:
        return True
    expected_registry_history = f"results/registries/history/trial_registry--{origin.sha256}.json"
    return (
        origin.artifact_class == "trial-registry"
        and following.artifact_class == "trial-registry-history"
        and origin.new_path == "results/registries/trial_registry.json"
        and following.old_path == origin.new_path
        and following.new_path == expected_registry_history
    )


def _safe_repository_path(value: str, *, label: str) -> Path:
    path = Path(value)
    if (
        not value
        or path.is_absolute()
        or ".." in path.parts
        or "." in path.parts
        or path.as_posix() != value
        or len(path.parts) < 2
    ):
        raise ResultPathMigrationError(f"path migration {label} is unsafe")
    return path


def _safe_identity(value: str) -> str:
    if not value or Path(value).name != value or value in {".", ".."}:
        raise ResultPathMigrationError(f"unsafe result identity: {value}")
    return value


def _repository_root_for(path: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        return Path(explicit).resolve()
    if not path.is_absolute():
        return Path.cwd().resolve()
    for parent in path.resolve().parents:
        if (parent / PATH_MIGRATION_REGISTRY).is_file():
            return parent
    return Path.cwd().resolve()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}-", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _remove_empty_result_directories(root: Path) -> None:
    if not root.exists():
        return
    for directory in sorted(
        (path for path in root.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        try:
            directory.rmdir()
        except OSError:
            pass
