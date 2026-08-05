"""Shared immutable-artifact publication and verification primitives."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from trading.research_data.models import DefinitionBlobRef


class ImmutableBlobCorruptionError(RuntimeError):
    """An existing content-addressed blob does not match its identity."""


def canonical_json_bytes(payload: object) -> bytes:
    """Serialize one JSON value to the canonical bytes used for content identity."""
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


def validate_digest(digest: str) -> None:
    """Reject values that cannot be lowercase SHA-256 identities."""
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise ValueError("digest must be a lowercase SHA-256 hex identity")


def publish_immutable(path: Path, content: bytes, digest: str) -> None:
    """Publish exact bytes without replacing an existing immutable artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        _verify_existing(path, content, digest)
        return
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".research-blob-",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            _verify_existing(path, content, digest)
    finally:
        temporary.unlink(missing_ok=True)


def read_definition_blob(path: Path, reference: DefinitionBlobRef) -> dict[str, object]:
    """Read and fully verify an exact research-definition artifact."""
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise ImmutableBlobCorruptionError(
            f"definition blob {reference.digest} is missing or unreadable"
        ) from exc
    return verify_definition_bytes(content, reference)


def verify_definition_bytes(
    content: bytes,
    reference: DefinitionBlobRef,
) -> dict[str, object]:
    """Verify exact and semantic identities for definition bytes."""
    if len(content) != reference.byte_count:
        raise ImmutableBlobCorruptionError(
            f"definition blob {reference.digest} size does not match reference"
        )
    if hashlib.sha256(content).hexdigest() != reference.digest:
        raise ImmutableBlobCorruptionError(
            f"definition blob {reference.digest} failed checksum verification"
        )
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ImmutableBlobCorruptionError(
            f"definition blob {reference.digest} is not valid JSON"
        ) from exc
    if not isinstance(payload, dict) or payload.get("fingerprint") != reference.fingerprint:
        raise ImmutableBlobCorruptionError(
            f"definition blob {reference.digest} fingerprint does not match reference"
        )
    try:
        semantic_payload = {
            key: payload[key]
            for key in (
                "schema_version",
                "resolved_config",
                "normalized_python_ast",
                "execution_engine_version",
                "runtime",
            )
        }
    except KeyError as exc:
        raise ImmutableBlobCorruptionError(
            f"definition blob {reference.digest} lacks semantic fingerprint inputs"
        ) from exc
    computed_fingerprint = hashlib.sha256(canonical_json_bytes(semantic_payload)).hexdigest()
    if computed_fingerprint != reference.fingerprint:
        raise ImmutableBlobCorruptionError(
            f"definition blob {reference.digest} failed semantic fingerprint verification"
        )
    return payload


def _verify_existing(path: Path, expected: bytes, digest: str) -> None:
    actual = path.read_bytes()
    actual_digest = hashlib.sha256(actual).hexdigest()
    if actual_digest != digest or actual != expected:
        raise ImmutableBlobCorruptionError(f"immutable blob collision or corruption at {path}")
