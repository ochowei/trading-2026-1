"""Semantic research-definition identities and exact source snapshots."""

from __future__ import annotations

import ast
import hashlib
import math
import platform
import subprocess
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path

from trading.research_data.artifacts import (
    canonical_json_bytes,
    publish_immutable,
    read_definition_blob,
    validate_digest,
)
from trading.research_data.models import (
    DefinitionBlobRef,
    ResearchDefinitionSnapshot,
)


class ResearchDefinitionError(RuntimeError):
    """A research definition cannot be canonicalized or reconstructed."""


class ResearchDefinitionStore:
    """Content-addressed exact definitions with semantic fingerprints."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def definition_blob_path(self, digest: str) -> Path:
        validate_digest(digest)
        return self.root / "definitions" / "sha256" / digest[:2] / f"{digest}.json"

    def capture(
        self,
        *,
        resolved_config: object,
        sources: Mapping[str, Path],
        execution_engine_version: str,
        dependency_versions: Mapping[str, str],
        repo_root: Path | None = None,
    ) -> ResearchDefinitionSnapshot:
        """Capture exact source while deriving identity from normalized semantics."""
        required_roles = {"strategy", "detector", "backtester"}
        if not required_roles.issubset(sources):
            raise ResearchDefinitionError(
                "a research definition requires strategy, detector, and backtester sources"
            )
        exact_sources: dict[str, str] = {}
        normalized_sources: dict[str, str] = {}
        source_paths: list[Path] = []
        for role, source_path in sorted(sources.items()):
            path = Path(source_path)
            try:
                content = path.read_text(encoding="utf-8")
                tree = ast.parse(content, filename=str(path))
            except (OSError, SyntaxError, UnicodeError) as exc:
                raise ResearchDefinitionError(f"cannot capture {role} source: {exc}") from exc
            exact_sources[role] = content
            normalized_sources[role] = ast.dump(
                tree, annotate_fields=True, include_attributes=False
            )
            source_paths.append(path)

        canonical_config = _canonical_value(resolved_config)
        runtime = {
            "python": platform.python_version(),
            "dependencies": {key: dependency_versions[key] for key in sorted(dependency_versions)},
        }
        semantic_payload = {
            "schema_version": 1,
            "resolved_config": canonical_config,
            "normalized_python_ast": normalized_sources,
            "execution_engine_version": execution_engine_version,
            "runtime": runtime,
        }
        fingerprint = hashlib.sha256(canonical_json_bytes(semantic_payload)).hexdigest()
        git_root = (
            Path(repo_root).resolve() if repo_root is not None else _discover_git_root(source_paths)
        )
        git_context = _git_context(git_root, source_paths)
        exact_payload = {
            **semantic_payload,
            "fingerprint": fingerprint,
            "sources": exact_sources,
            "git_context": git_context,
        }
        blob_bytes = canonical_json_bytes(exact_payload)
        digest = hashlib.sha256(blob_bytes).hexdigest()
        publish_immutable(self.definition_blob_path(digest), blob_bytes, digest)
        reference = DefinitionBlobRef(
            digest=digest,
            byte_count=len(blob_bytes),
            fingerprint=fingerprint,
        )
        return ResearchDefinitionSnapshot(fingerprint=fingerprint, blob=reference)

    def load(self, reference: DefinitionBlobRef) -> dict[str, object]:
        """Verify and return exact reconstructable definition content."""
        return read_definition_blob(self.definition_blob_path(reference.digest), reference)


def _canonical_value(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return _canonical_value(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _canonical_value(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        items = [_canonical_value(item) for item in value]
        return sorted(items, key=lambda item: repr(item))
    if isinstance(value, Enum):
        return _canonical_value(value.value)
    if isinstance(value, (date, datetime, Path)):
        return value.isoformat() if not isinstance(value, Path) else str(value)
    if isinstance(value, float) and not math.isfinite(value):
        raise ResearchDefinitionError("resolved config contains a non-finite number")
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise ResearchDefinitionError(
        f"resolved config contains unsupported value {type(value).__name__}"
    )


def _git_context(repo_root: Path, source_paths: list[Path]) -> dict[str, object]:
    root = Path(repo_root).resolve()
    try:
        relative_paths = [str(path.resolve().relative_to(root)) for path in source_paths]
    except ValueError as exc:
        raise ResearchDefinitionError(
            "cannot capture Git context: every source must be inside one repository"
        ) from exc

    def run(*arguments: str) -> str:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    try:
        head = run("rev-parse", "HEAD")
        branch = run("branch", "--show-current")
        status = run("status", "--porcelain", "--", *relative_paths)
        diff = run("diff", "--binary", "HEAD", "--", *relative_paths)
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        raise ResearchDefinitionError(f"cannot capture Git context: {exc}") from exc
    return {
        "head": head,
        "branch": branch,
        "dirty": bool(status),
        "status": status,
        "diff": diff,
    }


def _discover_git_root(source_paths: list[Path]) -> Path:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=source_paths[0].parent,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError, IndexError) as exc:
        raise ResearchDefinitionError(
            "cannot capture Git context: sources are not in a Git repository"
        ) from exc
    root = Path(completed.stdout.strip()).resolve()
    if not all(path.resolve().is_relative_to(root) for path in source_paths):
        raise ResearchDefinitionError(
            "cannot capture Git context: every source must be inside one repository"
        )
    return root
