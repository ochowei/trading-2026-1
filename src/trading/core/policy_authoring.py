"""Versioned executable policy authoring and validation boundaries."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path

import yaml

from trading.core.accounting import canonical_json_bytes, timestamp_text
from trading.core.workflow_authoring import (
    MarkdownDocument,
    ValidationIssue,
    _atomic_write,
    read_markdown_document,
    render_markdown_document,
)

POLICY_INDEX_START = "<!-- GENERATED:POLICY_INDEX_START -->"
POLICY_INDEX_END = "<!-- GENERATED:POLICY_INDEX_END -->"
POLICY_DIRECTORY_PATTERN = re.compile(
    r"^(?P<family>[a-z0-9]+(?:-[a-z0-9]+)*)--(?P<version>v\d{3,})$"
)
POLICY_FAMILY_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
POLICY_VERSION_PATTERN = re.compile(r"^v\d{3,}$")
POLICY_STATUSES = frozenset({"draft", "active", "superseded", "retired", "abandoned"})


class PolicyAuthoringError(ValueError):
    """A policy authoring operation violated a repository contract."""


class PolicyRepository:
    """Manage the tracked, versioned policy registry under one repository root."""

    def __init__(
        self,
        root: Path = Path("policies"),
        *,
        now: Callable[[], datetime] | None = None,
        conformance_runner: Callable[[tuple[Path, ...]], None] | None = None,
    ) -> None:
        self.root = Path(root)
        self.now = now or (lambda: datetime.now(UTC))
        self.conformance_runner = conformance_runner or self._run_conformance

    @property
    def registry_path(self) -> Path:
        return self.root / "README.md"

    def validate_all(self) -> tuple[ValidationIssue, ...]:
        """Validate the policy registry and every registered version."""
        issues: list[ValidationIssue] = []
        try:
            document = read_markdown_document(self.registry_path)
        except ValueError as exc:
            return (ValidationIssue(self.registry_path, str(exc)),)
        if document.metadata.get("schema_version") != 1:
            issues.append(ValidationIssue(self.registry_path, "schema_version must be 1"))
        policies = document.metadata.get("policies")
        if not isinstance(policies, dict):
            return (ValidationIssue(self.registry_path, "policies must be a mapping"),)
        registered_paths: set[str] = set()
        for family, family_record in policies.items():
            if not isinstance(family, str) or not POLICY_FAMILY_PATTERN.fullmatch(family):
                issues.append(
                    ValidationIssue(self.registry_path, f"invalid policy family: {family}")
                )
                continue
            if not isinstance(family_record, Mapping):
                issues.append(ValidationIssue(self.registry_path, f"{family} must be a mapping"))
                continue
            versions = family_record.get("versions")
            if not isinstance(versions, Mapping) or not versions:
                issues.append(
                    ValidationIssue(self.registry_path, f"{family} versions must be non-empty")
                )
                continue
            for version, record in versions.items():
                if not isinstance(version, str) or not POLICY_VERSION_PATTERN.fullmatch(version):
                    issues.append(
                        ValidationIssue(self.registry_path, f"invalid policy version: {version}")
                    )
                    continue
                if not isinstance(record, Mapping):
                    issues.append(
                        ValidationIssue(self.registry_path, f"{family} {version} must be a mapping")
                    )
                    continue
                expected_path = f"{family}--{version}"
                if record.get("path") != expected_path:
                    issues.append(
                        ValidationIssue(
                            self.registry_path, f"{family} {version} path must be {expected_path}"
                        )
                    )
                    continue
                registered_paths.add(expected_path)
                if record.get("status") not in POLICY_STATUSES:
                    issues.append(
                        ValidationIssue(
                            self.registry_path, f"invalid policy status: {record.get('status')}"
                        )
                    )
                self._validate_version(
                    self.root / expected_path,
                    family=family,
                    version=version,
                    status=record.get("status"),
                    issues=issues,
                )
        if self.root.exists():
            for child in self.root.iterdir():
                if child.is_dir() and POLICY_DIRECTORY_PATTERN.fullmatch(child.name):
                    if child.name not in registered_paths:
                        issues.append(
                            ValidationIssue(child, "policy version directory is not registered")
                        )
        expected = self._render_index(policies)
        start = document.body.find(POLICY_INDEX_START)
        end = document.body.find(POLICY_INDEX_END)
        if start < 0 or end < 0 or end <= start:
            issues.append(
                ValidationIssue(self.registry_path, "generated policy index markers are missing")
            )
        else:
            actual = document.body[start + len(POLICY_INDEX_START) : end].strip()
            if actual != expected.strip():
                issues.append(
                    ValidationIssue(
                        self.registry_path,
                        "generated policy index is stale; run `trading policy sync`",
                    )
                )
        return tuple(issues)

    def sync(self) -> None:
        """Regenerate the human-readable policy index from registry metadata."""
        document = read_markdown_document(self.registry_path)
        policies = document.metadata.get("policies")
        if not isinstance(policies, dict):
            raise PolicyAuthoringError("policies must be a mapping")
        start = document.body.find(POLICY_INDEX_START)
        end = document.body.find(POLICY_INDEX_END)
        if start < 0 or end < 0 or end <= start:
            raise PolicyAuthoringError("generated policy index markers are missing")
        replacement = self._render_index(policies)
        start_end = start + len(POLICY_INDEX_START)
        body = f"{document.body[:start_end]}\n{replacement}\n{document.body[end:]}"
        _atomic_write(
            self.registry_path,
            render_markdown_document(MarkdownDocument(document.metadata, body)),
        )

    def _validate_version(
        self,
        path: Path,
        *,
        family: str,
        version: str,
        status: object,
        issues: list[ValidationIssue],
    ) -> None:
        readme = path / "README.md"
        definition = path / "POLICY.md"
        config = path / "policy.yaml"
        for required in (readme, definition, config):
            if not required.is_file():
                issues.append(ValidationIssue(required, "required policy file is missing"))
        if not readme.is_file():
            return
        try:
            metadata = read_markdown_document(readme).metadata
        except ValueError as exc:
            issues.append(ValidationIssue(readme, str(exc)))
            return
        expected_fields = {
            "policy",
            "title",
            "version",
            "definition",
            "config",
            "supersedes",
            "implementation",
            "conformance",
        }
        for field in expected_fields.difference(metadata):
            issues.append(ValidationIssue(readme, f"missing frontmatter field: {field}"))
        if metadata.get("policy") != family or metadata.get("version") != version:
            issues.append(ValidationIssue(readme, "policy identity does not match registry"))
        if metadata.get("definition") != "POLICY.md" or metadata.get("config") != "policy.yaml":
            issues.append(ValidationIssue(readme, "policy definition and config names are fixed"))
        for field in ("implementation", "conformance"):
            references = metadata.get(field)
            if (
                not isinstance(references, list)
                or not references
                or not all(isinstance(reference, str) and reference for reference in references)
            ):
                issues.append(ValidationIssue(readme, f"{field} must be a non-empty path list"))
                continue
            for reference in references:
                target = (self.root.parent / reference).resolve()
                try:
                    target.relative_to(self.root.parent.resolve())
                except ValueError:
                    issues.append(
                        ValidationIssue(readme, f"{field} path escapes repository: {reference}")
                    )
                    continue
                if not target.is_file():
                    issues.append(ValidationIssue(target, f"{field} path does not exist"))
        if config.is_file():
            try:
                raw = yaml.safe_load(config.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, yaml.YAMLError) as exc:
                issues.append(ValidationIssue(config, f"invalid policy config: {exc}"))
            else:
                if not isinstance(raw, dict):
                    issues.append(ValidationIssue(config, "policy config must be a mapping"))
                elif raw.get("schema_version") != 1:
                    issues.append(ValidationIssue(config, "policy config schema_version must be 1"))
                elif raw.get("family") != family or raw.get("version") != version:
                    issues.append(
                        ValidationIssue(config, "policy config identity does not match registry")
                    )
        if status == "draft" and (path / "RELEASE.json").exists():
            issues.append(
                ValidationIssue(
                    path / "RELEASE.json", "draft policy must not have release evidence"
                )
            )
        if status in {"active", "superseded", "retired"}:
            self._validate_release(path, family=family, version=version, issues=issues)

    def release(self, version_path: Path, *, approved_by: str) -> dict[str, object]:
        """Prepare an approved policy release with exact executable evidence."""
        if not approved_by.strip():
            raise PolicyAuthoringError("policy release requires --approved-by")
        path = Path(version_path).resolve()
        try:
            path.relative_to(self.root.resolve())
        except ValueError as exc:
            raise PolicyAuthoringError("policy version must be inside the policy registry") from exc
        match = POLICY_DIRECTORY_PATTERN.fullmatch(path.name)
        if match is None:
            raise PolicyAuthoringError("invalid policy version path")
        family = match.group("family")
        version = match.group("version")
        document = read_markdown_document(self.registry_path)
        registry = document.metadata
        try:
            record = registry["policies"][family]["versions"][version]
        except (KeyError, TypeError) as exc:
            raise PolicyAuthoringError("policy version is not registered") from exc
        if record.get("status") != "draft":
            raise PolicyAuthoringError("only a draft policy version may be released")
        versions = registry["policies"][family]["versions"]
        active_versions = [
            candidate
            for candidate, candidate_record in versions.items()
            if isinstance(candidate_record, Mapping) and candidate_record.get("status") == "active"
        ]
        if len(active_versions) > 1:
            raise PolicyAuthoringError("policy family has more than one active version")
        supersedes = read_markdown_document(path / "README.md").metadata.get("supersedes")
        if active_versions:
            active_version = active_versions[0]
            if supersedes != active_version:
                raise PolicyAuthoringError(
                    f"replacement must supersede active policy version {active_version}"
                )
            if int(version[1:]) <= int(active_version[1:]):
                raise PolicyAuthoringError("replacement policy version must be newer than active")
        elif supersedes is not None:
            raise PolicyAuthoringError("initial policy release must not supersede a version")
        issues = self.validate_all()
        if issues:
            raise PolicyAuthoringError(str(issues[0]))
        metadata = read_markdown_document(path / "README.md").metadata
        implementation = self._release_references(metadata["implementation"])
        conformance = self._release_references(metadata["conformance"])
        self.conformance_runner(
            tuple((self.root.parent / item["path"]).resolve() for item in conformance)
        )
        prepared_at = timestamp_text(self.now().astimezone(UTC))
        release: dict[str, object] = {
            "schema_version": 1,
            "policy": family,
            "version": version,
            "approved_at": prepared_at,
            "prepared_at": prepared_at,
            "approved_by": approved_by.strip(),
            "policy_sha256": self._sha256(path / "POLICY.md"),
            "config_sha256": self._sha256(path / "policy.yaml"),
            "supersedes": metadata.get("supersedes"),
            "implementation": implementation,
            "conformance": conformance,
        }
        _atomic_write(path / "RELEASE.json", canonical_json_bytes(release), replace=False)
        if supersedes is not None:
            previous = versions.get(supersedes)
            if not isinstance(previous, dict) or previous.get("status") != "active":
                raise PolicyAuthoringError("supersedes must identify the active policy version")
            previous["status"] = "superseded"
            previous["status_changed_at"] = prepared_at
            previous["status_changed_by"] = approved_by.strip()
        record["status"] = "active"
        record["status_changed_at"] = prepared_at
        record["status_changed_by"] = approved_by.strip()
        _atomic_write(
            self.registry_path,
            render_markdown_document(MarkdownDocument(registry, document.body)),
        )
        self.sync()
        final_issues = self.validate_all()
        if final_issues:
            raise PolicyAuthoringError(str(final_issues[0]))
        return release

    def transition_version(
        self,
        version_path: Path,
        target_status: str,
        *,
        approved_by: str | None = None,
    ) -> None:
        """Abandon an unreleased draft or retire an active policy version."""
        path = Path(version_path).resolve()
        match = POLICY_DIRECTORY_PATTERN.fullmatch(path.name)
        if match is None:
            raise PolicyAuthoringError("invalid policy version path")
        document = read_markdown_document(self.registry_path)
        registry = document.metadata
        try:
            record = registry["policies"][match.group("family")]["versions"][match.group("version")]
        except (KeyError, TypeError) as exc:
            raise PolicyAuthoringError("policy version is not registered") from exc
        current = record.get("status")
        if target_status == "abandoned":
            if current != "draft":
                raise PolicyAuthoringError("only a draft policy version may be abandoned")
        elif target_status == "retired":
            if current != "active":
                raise PolicyAuthoringError("only an active policy version may be retired")
            if not approved_by or not approved_by.strip():
                raise PolicyAuthoringError("retiring a policy requires --approved-by")
        else:
            raise PolicyAuthoringError("policy version transition supports abandoned or retired")
        occurred_at = timestamp_text(self.now().astimezone(UTC))
        record["status"] = target_status
        record["status_changed_at"] = occurred_at
        record["status_changed_by"] = approved_by.strip() if approved_by else None
        _atomic_write(
            self.registry_path,
            render_markdown_document(MarkdownDocument(registry, document.body)),
        )
        self.sync()
        issues = self.validate_all()
        if issues:
            raise PolicyAuthoringError(str(issues[0]))

    def _validate_release(
        self,
        path: Path,
        *,
        family: str,
        version: str,
        issues: list[ValidationIssue],
    ) -> None:
        release_path = path / "RELEASE.json"
        try:
            release = json.loads(release_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            issues.append(
                ValidationIssue(release_path, f"released policy needs valid RELEASE.json: {exc}")
            )
            return
        if release.get("policy") != family or release.get("version") != version:
            issues.append(
                ValidationIssue(release_path, "release identity does not match policy version")
            )
        if release.get("policy_sha256") != self._sha256(path / "POLICY.md"):
            issues.append(
                ValidationIssue(path / "POLICY.md", "published policy contract digest has changed")
            )
        if release.get("config_sha256") != self._sha256(path / "policy.yaml"):
            issues.append(
                ValidationIssue(path / "policy.yaml", "published policy config digest has changed")
            )
        metadata = read_markdown_document(path / "README.md").metadata
        for field in ("implementation", "conformance"):
            try:
                expected = self._release_references(metadata[field])
            except (KeyError, PolicyAuthoringError) as exc:
                issues.append(ValidationIssue(release_path, str(exc)))
                continue
            if release.get(field) != expected:
                issues.append(
                    ValidationIssue(release_path, f"published {field} digest has changed")
                )

    def _release_references(self, raw: object) -> list[dict[str, str]]:
        if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
            raise PolicyAuthoringError("release references must be path lists")
        return [{"path": item, "sha256": self._sha256(self.root.parent / item)} for item in raw]

    @staticmethod
    def _sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _run_conformance(paths: tuple[Path, ...]) -> None:
        subprocess.run([sys.executable, "-m", "pytest", "-q", *map(str, paths)], check=True)

    @staticmethod
    def _render_index(policies: Mapping[str, object]) -> str:
        rows: list[str] = []
        for family in sorted(policies):
            family_record = policies[family]
            if not isinstance(family_record, Mapping):
                continue
            title = family_record.get("title", family)
            versions = family_record.get("versions")
            if not isinstance(versions, Mapping):
                continue
            for version in sorted(versions):
                record = versions[version]
                if not isinstance(record, Mapping):
                    continue
                path = record.get("path", "")
                rows.append(
                    f"| {title} (`{family}`) | `{version}` | `{record.get('status', '')}` | [{path}]({path}/) |"
                )
        if not rows:
            return "_No policy versions registered._"
        return "\n".join(
            [
                "| Policy | Version | Status | Path |",
                "| --- | --- | --- | --- |",
                *rows,
            ]
        )
