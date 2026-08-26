"""Tracked content-addressed research-evidence publication and resolution."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from trading.core.accounting import canonical_json_bytes
from trading.research_data.artifacts import (
    ImmutableBlobCorruptionError,
    publish_immutable,
    validate_digest,
)
from trading.research_data.paths import (
    qualification_evidence_directory,
    research_evidence_directory,
)
from trading.research_data.qualification_registry import (
    QualificationRegistry,
    QualificationRegistryError,
)


class ResearchEvidenceStore:
    """Resolve immutable Markdown evidence retained in canonical Git history."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else research_evidence_directory()

    def path_for(self, digest: str) -> Path:
        """Return the sole canonical path for one SHA-256 evidence identity."""
        validate_digest(digest)
        return self.root / f"{digest}.md"

    def publish(self, content: bytes, *, digest: str | None = None) -> Path:
        """Add exact Markdown bytes without permitting replacement or aliases."""
        computed = hashlib.sha256(content).hexdigest()
        expected = digest or computed
        validate_digest(expected)
        if computed != expected:
            raise ImmutableBlobCorruptionError(
                "research evidence bytes do not match the requested digest"
            )
        path = self.path_for(expected)
        publish_immutable(path, content, expected)
        return path

    def resolve(self, digest: str) -> bytes:
        """Read exact evidence bytes and fail closed on absence or checksum drift."""
        path = self.path_for(digest)
        try:
            content = path.read_bytes()
        except OSError as exc:
            raise ImmutableBlobCorruptionError(
                f"research evidence {digest} is missing or unreadable"
            ) from exc
        if hashlib.sha256(content).hexdigest() != digest:
            raise ImmutableBlobCorruptionError(
                f"research evidence {digest} failed checksum verification"
            )
        return content


@dataclass(frozen=True, slots=True)
class QualificationEvidenceSnapshot:
    """Verified immutable qualification state plus its authoritative source identity."""

    source_registry_identity: str
    registry_sha256: str
    checkpoint_sha256: str
    state: dict[str, object]


class QualificationEvidenceStore:
    """Immutable self-contained qualification-registry snapshots for terminal review."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else qualification_evidence_directory()

    def path_for(self, digest: str) -> Path:
        validate_digest(digest)
        return self.root / f"{digest}.json"

    def publish_registry(
        self,
        registry_path: Path,
        *,
        repository_root: Path,
        source_registry_identity: str,
    ) -> tuple[Path, str]:
        """Verify and publish exact registry plus head-checkpoint bytes."""
        identity = _source_registry_identity(source_registry_identity)
        expected_source = (Path(repository_root).resolve() / identity).resolve()
        if Path(registry_path).resolve() != expected_source:
            raise ValueError(
                "qualification registry path differs from its declared source identity"
            )
        source = QualificationRegistry(registry_path)
        source.initialize()
        source.read()
        registry_bytes = Path(registry_path).read_bytes()
        checkpoint_bytes = source.checkpoint_path.read_bytes()
        self._replay_snapshot(registry_bytes, checkpoint_bytes)
        artifact = canonical_json_bytes(
            {
                "schema_version": 1,
                "source_registry_identity": identity,
                "registry_sha256": hashlib.sha256(registry_bytes).hexdigest(),
                "checkpoint_sha256": hashlib.sha256(checkpoint_bytes).hexdigest(),
                "registry_json": registry_bytes.decode("utf-8"),
                "checkpoint_json": checkpoint_bytes.decode("utf-8"),
            }
        )
        digest = hashlib.sha256(artifact).hexdigest()
        path = self.path_for(digest)
        publish_immutable(path, artifact, digest)
        return path, digest

    def resolve(self, digest: str) -> QualificationEvidenceSnapshot:
        """Verify immutable outer bytes and replay the authoritative registry reader."""
        path = self.path_for(digest)
        try:
            artifact = path.read_bytes()
            payload = json.loads(artifact)
        except (OSError, json.JSONDecodeError) as exc:
            raise ImmutableBlobCorruptionError(
                f"qualification evidence {digest} is missing or invalid"
            ) from exc
        if hashlib.sha256(artifact).hexdigest() != digest or not isinstance(payload, dict):
            raise ImmutableBlobCorruptionError("qualification evidence checksum is invalid")
        registry_text = payload.get("registry_json")
        checkpoint_text = payload.get("checkpoint_json")
        source_registry_identity = payload.get("source_registry_identity")
        if not isinstance(registry_text, str) or not isinstance(checkpoint_text, str):
            raise ImmutableBlobCorruptionError("qualification evidence payload is incomplete")
        try:
            identity = _source_registry_identity(source_registry_identity)
        except ValueError as exc:
            raise ImmutableBlobCorruptionError(str(exc)) from exc
        registry_bytes = registry_text.encode("utf-8")
        checkpoint_bytes = checkpoint_text.encode("utf-8")
        if (
            payload.get("schema_version") != 1
            or payload.get("registry_sha256") != hashlib.sha256(registry_bytes).hexdigest()
            or payload.get("checkpoint_sha256") != hashlib.sha256(checkpoint_bytes).hexdigest()
        ):
            raise ImmutableBlobCorruptionError("qualification evidence inner checksum is invalid")

        return QualificationEvidenceSnapshot(
            source_registry_identity=identity,
            registry_sha256=str(payload["registry_sha256"]),
            checkpoint_sha256=str(payload["checkpoint_sha256"]),
            state=self._replay_snapshot(registry_bytes, checkpoint_bytes),
        )

    @staticmethod
    def _replay_snapshot(
        registry_bytes: bytes,
        checkpoint_bytes: bytes,
    ) -> dict[str, object]:
        """Replay one captured registry/checkpoint pair through the authoritative reader."""
        with TemporaryDirectory(prefix="qualification-evidence-verify-") as temporary:
            registry_path = Path(temporary) / "qualification.json"
            registry_path.write_bytes(registry_bytes)
            checkpoint_path = registry_path.with_name(f".{registry_path.name}.head.json")
            checkpoint_path.write_bytes(checkpoint_bytes)
            try:
                registry = QualificationRegistry(registry_path)
                state = registry.read()
                events = state.get("events", [])
                plan_ids = [
                    event["payload"]["plan_id"]
                    for event in events
                    if isinstance(event, dict)
                    and event.get("event_type") == "historical_plan"
                    and isinstance(event.get("payload"), dict)
                    and isinstance(event["payload"].get("plan_id"), str)
                ]
                screen_plan_ids = {
                    event["payload"]["plan_id"]
                    for event in events
                    if isinstance(event, dict)
                    and event.get("event_type") == "historical_screen"
                    and isinstance(event.get("payload"), dict)
                    and isinstance(event["payload"].get("plan_id"), str)
                }
                for plan_id in plan_ids:
                    registry.historical_plan(plan_id)
                    if plan_id in screen_plan_ids:
                        registry.historical_screen(plan_id)
                return state
            except QualificationRegistryError as exc:
                raise ImmutableBlobCorruptionError(
                    f"qualification evidence cannot be replayed: {exc}"
                ) from exc


def _source_registry_identity(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("qualification evidence source registry identity is missing")
    identity = value.strip()
    path = Path(identity)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != identity:
        raise ValueError("qualification evidence source registry identity is unsafe")
    return identity
