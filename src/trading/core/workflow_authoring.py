"""Versioned repository workflow authoring, validation, and release boundaries."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from trading.core.accounting import canonical_json_bytes, parse_timestamp, timestamp_text
from trading.core.ledger_storage import FileLockTimeout, locked_file

ROOT_INDEX_START = "<!-- GENERATED:WORKFLOW_INDEX_START -->"
ROOT_INDEX_END = "<!-- GENERATED:WORKFLOW_INDEX_END -->"
WORK_INDEX_START = "<!-- GENERATED:WORK_INDEX_START -->"
WORK_INDEX_END = "<!-- GENERATED:WORK_INDEX_END -->"

WORKFLOW_DIRECTORY_PATTERN = re.compile(
    r"^(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)--(?P<version>v\d{3,})$"
)
CHANGE_DIRECTORY_PATTERN = re.compile(r"^(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)--c(?P<number>\d{3,})$")
STUDY_DIRECTORY_PATTERN = re.compile(r"^(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)--s(?P<number>\d{3,})$")
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION_PATTERN = re.compile(r"^v\d{3,}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

VERSION_STATUSES = frozenset({"draft", "active", "superseded", "retired", "abandoned"})
CHANGE_STATUSES = frozenset(
    {"draft", "proposed", "accepted", "rejected", "deferred", "withdrawn", "released"}
)
STUDY_STATUSES = frozenset(
    {
        "draft",
        "preregistered",
        "running",
        "paused",
        "awaiting-review",
        "completed",
        "cancelled",
    }
)
STUDY_OUTCOMES = frozenset({"pass", "fail", "insufficient-evidence", "indeterminate"})
STUDY_ROUTES = frozenset(
    {"clean-historical", "retrospective-confirmatory", "study-time-retrospective"}
)

_CHANGE_TRANSITIONS: dict[str, frozenset[str]] = {
    "draft": frozenset({"proposed", "withdrawn"}),
    "proposed": frozenset({"accepted", "rejected", "deferred", "withdrawn"}),
    "deferred": frozenset({"proposed", "withdrawn"}),
    "accepted": frozenset(),
    "rejected": frozenset(),
    "withdrawn": frozenset(),
    "released": frozenset(),
}
_DECISION_STATUSES = frozenset({"accepted", "rejected", "deferred"})

_AUTHORING_MUTEXES_GUARD = threading.Lock()
_AUTHORING_MUTEXES: dict[str, threading.RLock] = {}
_AUTHORING_DEPTH = threading.local()


class WorkflowAuthoringError(ValueError):
    """A workflow authoring operation violated a repository contract."""


@dataclass(frozen=True)
class ValidationIssue:
    """One deterministic workflow validation failure."""

    path: Path
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


@dataclass(frozen=True)
class MarkdownDocument:
    """Parsed YAML frontmatter and the remaining Markdown body."""

    metadata: dict[str, Any]
    body: str


@dataclass(frozen=True)
class CreateWorkflowRequest:
    """Closed input for creating one initial workflow-family draft."""

    slug: str
    title: str
    definition_path: str
    authoring_basis: str
    policies: tuple[dict[str, Any], ...]
    dependencies: tuple[dict[str, Any], ...]
    capabilities: tuple[str, ...]
    derived_from: dict[str, Any] | None

    @classmethod
    def from_path(cls, path: Path) -> CreateWorkflowRequest:
        payload = _read_closed_request(
            path,
            allowed={
                "schema_version",
                "slug",
                "title",
                "definition_path",
                "authoring_basis",
                "policies",
                "dependencies",
                "capabilities",
                "derived_from",
            },
            required={
                "schema_version",
                "slug",
                "title",
                "definition_path",
                "authoring_basis",
                "policies",
                "dependencies",
                "capabilities",
                "derived_from",
            },
        )
        if payload["schema_version"] != 1:
            raise WorkflowAuthoringError("create request schema_version must be 1")
        for field in ("slug", "title", "definition_path", "authoring_basis"):
            if not isinstance(payload[field], str) or not payload[field].strip():
                raise WorkflowAuthoringError(f"create request {field} must be non-empty text")
        if not SLUG_PATTERN.fullmatch(payload["slug"]):
            raise WorkflowAuthoringError("create request slug must be lowercase kebab-case")
        policies = _request_mapping_list(payload["policies"], field="policies")
        dependencies = _request_dependencies(payload["dependencies"])
        capabilities = payload["capabilities"]
        if not isinstance(capabilities, list) or not all(
            isinstance(item, str) and item.strip() for item in capabilities
        ):
            raise WorkflowAuthoringError(
                "create request capabilities must be a list of identifiers"
            )
        if len(capabilities) != len(set(capabilities)):
            raise WorkflowAuthoringError("create request capabilities must be unique")
        derived_from = payload["derived_from"]
        if derived_from is not None and not isinstance(derived_from, dict):
            raise WorkflowAuthoringError("create request derived_from must be null or a mapping")
        return cls(
            slug=payload["slug"],
            title=payload["title"].strip(),
            definition_path=payload["definition_path"],
            authoring_basis=payload["authoring_basis"].strip(),
            policies=tuple(policies),
            dependencies=tuple(dependencies),
            capabilities=tuple(capabilities),
            derived_from=copy.deepcopy(derived_from),
        )


@dataclass(frozen=True)
class CreateChangeRequest:
    """Closed input for creating one change under the active version."""

    workflow: str
    slug: str
    title: str
    proposal_path: str
    impact_path: str
    validation_path: str | None
    decision_path: str | None
    propose: bool

    @classmethod
    def from_path(cls, path: Path) -> CreateChangeRequest:
        fields = {
            "schema_version",
            "workflow",
            "slug",
            "title",
            "proposal_path",
            "impact_path",
            "validation_path",
            "decision_path",
            "propose",
        }
        payload = _read_closed_request(path, allowed=fields, required=fields)
        if payload["schema_version"] != 1:
            raise WorkflowAuthoringError("change request schema_version must be 1")
        for field in ("workflow", "slug"):
            value = payload[field]
            if not isinstance(value, str) or not SLUG_PATTERN.fullmatch(value):
                raise WorkflowAuthoringError(f"change request {field} must be lowercase kebab-case")
        for field in ("title", "proposal_path", "impact_path"):
            if not isinstance(payload[field], str) or not payload[field].strip():
                raise WorkflowAuthoringError(f"change request {field} must be non-empty text")
        for field in ("validation_path", "decision_path"):
            value = payload[field]
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise WorkflowAuthoringError(
                    f"change request {field} must be null or non-empty text"
                )
        if not isinstance(payload["propose"], bool):
            raise WorkflowAuthoringError("change request propose must be boolean")
        return cls(
            workflow=payload["workflow"],
            slug=payload["slug"],
            title=payload["title"].strip(),
            proposal_path=payload["proposal_path"],
            impact_path=payload["impact_path"],
            validation_path=payload["validation_path"],
            decision_path=payload["decision_path"],
            propose=payload["propose"],
        )


@dataclass(frozen=True)
class EvolveWorkflowRequest:
    """Closed input for building the next draft from accepted changes."""

    workflow: str
    title: str
    definition_path: str
    authoring_basis: str
    policies: tuple[dict[str, Any], ...]
    dependencies: tuple[dict[str, Any], ...]
    capabilities: tuple[str, ...]

    @classmethod
    def from_path(cls, path: Path) -> EvolveWorkflowRequest:
        fields = {
            "schema_version",
            "workflow",
            "title",
            "definition_path",
            "authoring_basis",
            "policies",
            "dependencies",
            "capabilities",
        }
        payload = _read_closed_request(path, allowed=fields, required=fields)
        if payload["schema_version"] != 1:
            raise WorkflowAuthoringError("evolve request schema_version must be 1")
        workflow = payload["workflow"]
        if not isinstance(workflow, str) or not SLUG_PATTERN.fullmatch(workflow):
            raise WorkflowAuthoringError("evolve request workflow must be lowercase kebab-case")
        for field in ("title", "definition_path", "authoring_basis"):
            if not isinstance(payload[field], str) or not payload[field].strip():
                raise WorkflowAuthoringError(f"evolve request {field} must be non-empty text")
        capabilities = payload["capabilities"]
        if not isinstance(capabilities, list) or not all(
            isinstance(item, str) and item.strip() for item in capabilities
        ):
            raise WorkflowAuthoringError("evolve request capabilities must be identifiers")
        if len(capabilities) != len(set(capabilities)):
            raise WorkflowAuthoringError("evolve request capabilities must be unique")
        return cls(
            workflow=workflow,
            title=payload["title"].strip(),
            definition_path=payload["definition_path"],
            authoring_basis=payload["authoring_basis"].strip(),
            policies=tuple(_request_mapping_list(payload["policies"], field="policies")),
            dependencies=tuple(_request_dependencies(payload["dependencies"])),
            capabilities=tuple(capabilities),
        )


@dataclass(frozen=True)
class WorkflowFileMutation:
    """One deterministic file change in a workflow-authoring plan."""

    action: str
    path: str
    content: bytes
    before_sha256: str | None


@dataclass(frozen=True)
class WorkflowMutationPlan:
    """A read-only preview and exact file set for one authoring operation."""

    operation: str
    workflow: str
    version: str
    target: str
    mutations: tuple[WorkflowFileMutation, ...]
    source_version: str | None = None
    source_changes: tuple[str, ...] = ()
    policies: tuple[dict[str, Any], ...] = ()
    dependencies: tuple[dict[str, Any], ...] = ()
    authoring_basis: str = ""
    warnings: tuple[str, ...] = ()
    remaining_decisions: tuple[str, ...] = ()
    post_transition: str | None = None

    def preview(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "operation": self.operation,
            "workflow": self.workflow,
            "version": self.version,
            "target": self.target,
            "source_version": self.source_version,
            "source_changes": list(self.source_changes),
            "policies": copy.deepcopy(list(self.policies)),
            "dependencies": copy.deepcopy(list(self.dependencies)),
            "authoring_basis": self.authoring_basis,
            "changes": [
                {
                    "action": mutation.action,
                    "path": mutation.path,
                    "before_sha256": mutation.before_sha256,
                }
                for mutation in self.mutations
            ],
            "warnings": list(self.warnings),
            "blocking_issues": [],
            "remaining_decisions": list(self.remaining_decisions),
            **(
                {"post_transition": self.post_transition}
                if self.post_transition is not None
                else {}
            ),
        }


@dataclass(frozen=True)
class WorkflowMutationResult:
    """The identity and path produced by an applied authoring plan."""

    operation: str
    workflow: str
    version: str
    target: Path


def _read_closed_request(
    path: Path,
    *,
    allowed: set[str],
    required: set[str],
) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkflowAuthoringError(f"cannot read authoring request {path}: {exc}") from exc
    if not isinstance(payload, dict) or not all(isinstance(key, str) for key in payload):
        raise WorkflowAuthoringError("authoring request must be a string-keyed object")
    unknown = set(payload).difference(allowed)
    if unknown:
        raise WorkflowAuthoringError(
            f"unknown authoring request fields: {', '.join(sorted(unknown))}"
        )
    missing = required.difference(payload)
    if missing:
        raise WorkflowAuthoringError(
            f"missing authoring request fields: {', '.join(sorted(missing))}"
        )
    return payload


def _request_mapping_list(value: Any, *, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise WorkflowAuthoringError(f"authoring request {field} must be a list of mappings")
    return copy.deepcopy(value)


def _request_dependencies(value: Any) -> list[dict[str, Any]]:
    dependencies = _request_mapping_list(value, field="dependencies")
    for dependency in dependencies:
        unknown = set(dependency).difference({"path", "role", "pinned"})
        if unknown:
            raise WorkflowAuthoringError("unknown dependency fields: " + ", ".join(sorted(unknown)))
        missing = {"path", "role"}.difference(dependency)
        if missing:
            raise WorkflowAuthoringError("missing dependency fields: " + ", ".join(sorted(missing)))
    return dependencies


def read_markdown_document(path: Path) -> MarkdownDocument:
    """Read a Markdown file with a required YAML frontmatter mapping."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise WorkflowAuthoringError(f"cannot read {path}: {exc}") from exc
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise WorkflowAuthoringError(f"{path} must start with YAML frontmatter")
    closing_index = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    if closing_index is None:
        raise WorkflowAuthoringError(f"{path} has unterminated YAML frontmatter")
    try:
        raw_metadata = yaml.safe_load("".join(lines[1:closing_index]))
    except yaml.YAMLError as exc:
        raise WorkflowAuthoringError(f"{path} has invalid YAML frontmatter: {exc}") from exc
    if raw_metadata is None:
        metadata: dict[str, Any] = {}
    elif isinstance(raw_metadata, dict) and all(isinstance(key, str) for key in raw_metadata):
        metadata = dict(raw_metadata)
    else:
        raise WorkflowAuthoringError(f"{path} frontmatter must be a string-keyed mapping")
    return MarkdownDocument(metadata=metadata, body="".join(lines[closing_index + 1 :]))


def render_markdown_document(document: MarkdownDocument) -> bytes:
    """Serialize Markdown frontmatter deterministically enough for reviewable diffs."""
    metadata = yaml.safe_dump(
        document.metadata,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).rstrip()
    body = document.body.lstrip("\n")
    return f"---\n{metadata}\n---\n{body}".encode()


def _atomic_write(path: Path, content: bytes, *, replace: bool = True) -> None:
    """Publish a tracked text artifact atomically without private-file permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o644)
        if replace:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)
            temporary.unlink(missing_ok=True)
    except FileExistsError as exc:
        raise WorkflowAuthoringError(f"refusing to overwrite existing file: {path}") from exc
    finally:
        temporary.unlink(missing_ok=True)


def _replace_generated_region(body: str, start: str, end: str, content: str) -> str:
    start_index = body.find(start)
    end_index = body.find(end)
    if start_index < 0 or end_index < 0 or end_index <= start_index:
        raise WorkflowAuthoringError(f"missing or invalid generated markers: {start} / {end}")
    start_end = start_index + len(start)
    return f"{body[:start_end]}\n{content.rstrip()}\n{body[end_index:]}"


def _generated_region(body: str, start: str, end: str) -> str | None:
    start_index = body.find(start)
    end_index = body.find(end)
    if start_index < 0 or end_index < 0 or end_index <= start_index:
        return None
    return body[start_index + len(start) : end_index].strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_substantive(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8").strip()
    return (
        len(text) >= 40 and "[TODO" not in text and "TODO:" not in text and "REPLACE_ME" not in text
    )


def _substantive_bytes(content: bytes) -> bool:
    text = content.decode("utf-8").strip()
    return (
        len(text) >= 40 and "[TODO" not in text and "TODO:" not in text and "REPLACE_ME" not in text
    )


def _version_number(version: str) -> int:
    return int(version[1:])


def _is_canonical_utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return timestamp_text(parse_timestamp(value)) == value
    except ValueError:
        return False


class WorkflowRepository:
    """Manage the tracked, versioned workflow registry under one repository root."""

    def __init__(
        self,
        root: Path = Path("workflows"),
        *,
        now: Callable[[], datetime] | None = None,
        git_index_checker: Callable[[Path], bool] | None = None,
        lock_timeout_seconds: float = 5.0,
        publish_hook: Callable[[str, Path, int], None] | None = None,
        stage_hook: Callable[[Path], None] | None = None,
        _repository_root: Path | None = None,
        _canonical_workflow_root: Path | None = None,
    ) -> None:
        self.root = root
        self.repo_root = _repository_root or root.parent
        self.canonical_workflow_root = _canonical_workflow_root or root
        self.now = now or (lambda: datetime.now(UTC))
        self.git_index_checker = git_index_checker or self._is_git_indexed
        self.lock_timeout_seconds = lock_timeout_seconds
        self.publish_hook = publish_hook or (lambda _phase, _path, _index: None)
        self.stage_hook = stage_hook or (lambda _path: None)

    @property
    def registry_path(self) -> Path:
        return self.root / "README.md"

    @property
    def authoring_lock_path(self) -> Path:
        """Return the local-only lock shared by repository authoring writers."""
        return self.root / ".authoring.lock"

    @contextmanager
    def authoring_lease(self) -> Iterator[None]:
        """Hold the bounded cross-thread/process authoring lease re-entrantly."""
        key = str(self.authoring_lock_path.resolve())
        with _AUTHORING_MUTEXES_GUARD:
            mutex = _AUTHORING_MUTEXES.setdefault(key, threading.RLock())
        if not mutex.acquire(timeout=self.lock_timeout_seconds):
            raise WorkflowAuthoringError(
                f"timed out waiting for workflow authoring lock: {self.authoring_lock_path}"
            )
        depths = getattr(_AUTHORING_DEPTH, "values", {})
        depth = depths.get(key, 0)
        depths[key] = depth + 1
        _AUTHORING_DEPTH.values = depths
        try:
            if depth:
                yield
                return
            try:
                with locked_file(self.authoring_lock_path, self.lock_timeout_seconds):
                    yield
            except FileLockTimeout as exc:
                raise WorkflowAuthoringError(str(exc)) from exc
        finally:
            if depth:
                depths[key] = depth
            else:
                depths.pop(key, None)
            mutex.release()

    def validate_all(
        self,
        *,
        check_generated: bool = True,
        _allow_active_dependency_drift_for: tuple[str, str] | None = None,
    ) -> tuple[ValidationIssue, ...]:
        """Validate the registry and every registered or discoverable workflow artifact."""
        issues: list[ValidationIssue] = []
        try:
            registry_document = read_markdown_document(self.registry_path)
        except WorkflowAuthoringError as exc:
            return (ValidationIssue(self.registry_path, str(exc)),)

        workflows = self._validate_registry_metadata(registry_document.metadata, issues)
        registry_is_valid = not issues
        registered_paths: set[str] = set()
        if workflows is not None:
            for slug, family in workflows.items():
                versions = family.get("versions")
                if not isinstance(versions, Mapping):
                    continue
                for version, record in versions.items():
                    if (
                        not isinstance(version, str)
                        or not VERSION_PATTERN.fullmatch(version)
                        or not isinstance(record, Mapping)
                    ):
                        continue
                    path_text = record.get("path")
                    if path_text != f"{slug}--{version}":
                        continue
                    registered_paths.add(path_text)
                    self._validate_version(
                        self.root / path_text,
                        slug=slug,
                        version=version,
                        record=record,
                        issues=issues,
                        allow_active_dependency_drift=(
                            _allow_active_dependency_drift_for == (slug, version)
                        ),
                    )

        if self.root.exists():
            for child in sorted(self.root.iterdir()):
                if child.is_dir() and WORKFLOW_DIRECTORY_PATTERN.fullmatch(child.name):
                    if child.name not in registered_paths:
                        issues.append(
                            ValidationIssue(child, "workflow version directory is not registered")
                        )

        if check_generated and workflows is not None and registry_is_valid:
            expected = self._render_root_index(workflows)
            actual = _generated_region(
                registry_document.body,
                ROOT_INDEX_START,
                ROOT_INDEX_END,
            )
            if actual is None:
                issues.append(
                    ValidationIssue(self.registry_path, "root generated markers are missing")
                )
            elif actual != expected.strip():
                issues.append(
                    ValidationIssue(
                        self.registry_path,
                        "generated workflow index is stale; run `trading workflow sync`",
                    )
                )
            for path_text in sorted(registered_paths):
                version_readme = self.root / path_text / "README.md"
                if not version_readme.exists():
                    continue
                try:
                    version_document = read_markdown_document(version_readme)
                    expected_work = self._render_work_index(version_readme.parent)
                    actual_work = _generated_region(
                        version_document.body,
                        WORK_INDEX_START,
                        WORK_INDEX_END,
                    )
                    if actual_work is None:
                        issues.append(
                            ValidationIssue(version_readme, "work generated markers are missing")
                        )
                    elif actual_work != expected_work.strip():
                        issues.append(
                            ValidationIssue(
                                version_readme,
                                "generated work index is stale; run `trading workflow sync`",
                            )
                        )
                except WorkflowAuthoringError as exc:
                    issues.append(ValidationIssue(version_readme, str(exc)))
        self._validate_candidate_freeze_evidence(issues)
        return tuple(issues)

    def _validate_candidate_freeze_evidence(
        self,
        issues: list[ValidationIssue],
    ) -> None:
        """Verify every tracked candidate-freeze evidence digest from canonical bytes."""
        freezes = sorted(self.root.glob("*/work/studies/*/CANDIDATE_FREEZE.json"))
        referenced_paths: dict[Path, str] = {}
        for freeze in freezes:
            try:
                payload = json.loads(freeze.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                issues.append(ValidationIssue(freeze, f"invalid candidate freeze JSON: {exc}"))
                continue
            if not isinstance(payload, dict):
                issues.append(ValidationIssue(freeze, "candidate freeze payload must be an object"))
                continue
            digest = payload.get("development_evidence_sha256")
            if digest is None:
                continue
            if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
                issues.append(
                    ValidationIssue(
                        freeze,
                        "development_evidence_sha256 must be a SHA-256 digest",
                    )
                )
                continue
            artifact = self.repo_root / "results" / "research-evidence" / f"{digest}.md"
            prior = referenced_paths.get(artifact)
            if prior is not None and prior != digest:
                issues.append(ValidationIssue(artifact, "research-evidence digest collision"))
                continue
            referenced_paths[artifact] = digest
            if not artifact.is_file():
                issues.append(
                    ValidationIssue(
                        artifact,
                        f"candidate freeze {freeze} references missing research evidence",
                    )
                )
                continue
            if not self.git_index_checker(artifact):
                issues.append(
                    ValidationIssue(
                        artifact,
                        f"candidate freeze {freeze} research evidence is not in the Git index",
                    )
                )
                continue
            if _sha256(artifact) != digest:
                issues.append(
                    ValidationIssue(
                        artifact,
                        f"candidate freeze {freeze} research evidence checksum has changed",
                    )
                )

    def _is_git_indexed(self, path: Path) -> bool:
        try:
            relative = path.resolve().relative_to(self.repo_root.resolve()).as_posix()
        except ValueError:
            return False
        completed = subprocess.run(
            ["git", "show", f":{relative}"],
            cwd=self.repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if completed.returncode != 0:
            return False
        try:
            return completed.stdout == path.read_bytes()
        except OSError:
            return False

    def validate_path(self, path: Path) -> tuple[ValidationIssue, ...]:
        """Validate one path while retaining registry-level consistency checks."""
        resolved = self._resolve_input(path)
        if not resolved.exists():
            return (ValidationIssue(resolved, "workflow path does not exist"),)
        issues = self.validate_all()
        registry_resolved = self.registry_path.resolve()
        selected = []
        for issue in issues:
            issue_resolved = issue.path.resolve()
            if issue_resolved == registry_resolved or issue_resolved == resolved:
                selected.append(issue)
                continue
            if resolved.is_dir() and issue_resolved.is_relative_to(resolved):
                selected.append(issue)
        return tuple(selected)

    def plan_create(self, request: CreateWorkflowRequest) -> WorkflowMutationPlan:
        """Plan one initial v001 draft without mutating the repository."""
        self._require_structurally_valid()
        registry_document = read_markdown_document(self.registry_path)
        registry = copy.deepcopy(registry_document.metadata)
        workflows = registry.get("workflows")
        if not isinstance(workflows, dict):
            raise WorkflowAuthoringError("workflow registry has no workflows mapping")
        if request.slug in workflows:
            raise WorkflowAuthoringError(
                f"workflow family already exists; use evolve: {request.slug}"
            )
        target = self.root / f"{request.slug}--v001"
        if target.exists() or any(self.root.glob(f"{request.slug}--v*")):
            raise WorkflowAuthoringError(f"workflow identity already exists: {target.name}")

        definition = self._resolve_repo_reference(request.definition_path)
        if not _is_substantive(definition):
            raise WorkflowAuthoringError(
                "create request definition must be a complete Markdown file"
            )
        policies = self._authoring_policies(request.policies)
        dependencies = [copy.deepcopy(item) for item in request.dependencies]
        dependency_issues: list[ValidationIssue] = []
        self._validate_dependencies(dependencies, self.registry_path, dependency_issues)
        if dependency_issues:
            raise WorkflowAuthoringError("; ".join(str(issue) for issue in dependency_issues))
        derived_issues: list[ValidationIssue] = []
        self._validate_derived_from(request.derived_from, self.registry_path, derived_issues)
        if derived_issues:
            raise WorkflowAuthoringError("; ".join(str(issue) for issue in derived_issues))

        workflows[request.slug] = {
            "title": request.title,
            "versions": {"v001": {"path": target.name, "status": "draft"}},
        }
        metadata = {
            "workflow": request.slug,
            "title": request.title,
            "version": "v001",
            "definition": "WORKFLOW.md",
            "supersedes": None,
            "derived_from": copy.deepcopy(request.derived_from),
            "source_changes": [],
            "capabilities": list(request.capabilities),
            "policies": policies,
            "dependencies": dependencies,
        }
        readme_body = self._initial_version_body(
            title=request.title,
            authoring_basis=request.authoring_basis,
        )
        mutations = (
            self._planned_mutation(
                action="create",
                path=self._repo_relative(target / "README.md"),
                content=render_markdown_document(MarkdownDocument(metadata, readme_body)),
            ),
            self._planned_mutation(
                action="create",
                path=self._repo_relative(target / "WORKFLOW.md"),
                content=definition.read_bytes(),
            ),
            self._planned_mutation(
                action="update",
                path=self._repo_relative(self.registry_path),
                content=render_markdown_document(
                    MarkdownDocument(registry, registry_document.body)
                ),
            ),
        )
        return WorkflowMutationPlan(
            operation="create",
            workflow=request.slug,
            version="v001",
            target=self._repo_relative(target),
            mutations=mutations,
            policies=tuple(copy.deepcopy(policies)),
            dependencies=tuple(copy.deepcopy(dependencies)),
            authoring_basis=request.authoring_basis,
        )

    def plan_change(self, request: CreateChangeRequest) -> WorkflowMutationPlan:
        """Plan one legacy five-file change record under the unique active version."""
        self._require_structurally_valid()
        registry = read_markdown_document(self.registry_path).metadata
        family = self._family(registry, request.workflow)
        versions = self._versions(family, request.workflow)
        active = [
            (version, record)
            for version, record in versions.items()
            if isinstance(record, dict) and record.get("status") == "active"
        ]
        if len(active) != 1:
            raise WorkflowAuthoringError(
                f"workflow family must have exactly one active version: {request.workflow}"
            )
        version, record = active[0]
        version_path = self.root / str(record["path"])
        changes_root = version_path / "work" / "changes"
        allocated = (
            max(
                (
                    int(match.group("number"))
                    for path in changes_root.iterdir()
                    if path.is_dir()
                    and (match := CHANGE_DIRECTORY_PATTERN.fullmatch(path.name)) is not None
                ),
                default=0,
            )
            + 1
            if changes_root.exists()
            else 1
        )
        change_id = f"C{allocated:03d}"
        target = changes_root / f"{request.slug}--{change_id.lower()}"
        if target.exists():
            raise WorkflowAuthoringError(f"workflow change identity already exists: {target}")

        proposal = self._resolve_repo_reference(request.proposal_path)
        impact = self._resolve_repo_reference(request.impact_path)
        for label, path in (("proposal", proposal), ("impact", impact)):
            if not path.is_file():
                raise WorkflowAuthoringError(f"change request {label} file does not exist: {path}")
        optional = {
            "VALIDATION.md": request.validation_path,
            "DECISION.md": request.decision_path,
        }
        metadata = {
            "id": change_id,
            "title": request.title,
            "workflow": request.workflow,
            "source_version": version,
            "status": "draft",
            "created_at": self._current_time().date().isoformat(),
            "status_changed_at": None,
            "decided_at": None,
            "decided_by": None,
            "released_in": None,
        }
        readme_asset = self._authoring_asset("change", "README.md")
        readme_body = read_markdown_document(readme_asset).body
        readme_body = (
            readme_body.replace("REPLACE_ME_CHANGE_TITLE", request.title)
            .replace("REPLACE_ME_WORKFLOW_SLUG", request.workflow)
            .replace("REPLACE_ME_SOURCE_VERSION", version)
        )
        contents = {
            "README.md": render_markdown_document(MarkdownDocument(metadata, readme_body)),
            "PROPOSAL.md": proposal.read_bytes(),
            "IMPACT.md": impact.read_bytes(),
        }
        for filename, source in optional.items():
            if source is None:
                contents[filename] = self._authoring_asset("change", filename).read_bytes()
                continue
            source_path = self._resolve_repo_reference(source)
            if not source_path.is_file():
                raise WorkflowAuthoringError(
                    f"change request {filename} file does not exist: {source_path}"
                )
            contents[filename] = source_path.read_bytes()
        if request.propose:
            for filename in ("PROPOSAL.md", "IMPACT.md"):
                if not _substantive_bytes(contents[filename]):
                    raise WorkflowAuthoringError(
                        f"{filename} must be completed before immediate proposal"
                    )
        mutations = [
            self._planned_mutation(
                action="create",
                path=self._repo_relative(target / filename),
                content=contents[filename],
            )
            for filename in (
                "README.md",
                "PROPOSAL.md",
                "IMPACT.md",
                "VALIDATION.md",
                "DECISION.md",
            )
        ]
        version_document = read_markdown_document(version_path / "README.md")
        indexed_body = _replace_generated_region(
            version_document.body,
            WORK_INDEX_START,
            WORK_INDEX_END,
            self._render_work_index(
                version_path,
                planned_changes=((target.name, metadata),),
            ),
        )
        mutations.append(
            self._planned_mutation(
                action="update",
                path=self._repo_relative(version_path / "README.md"),
                content=render_markdown_document(
                    MarkdownDocument(version_document.metadata, indexed_body)
                ),
            )
        )
        version_metadata = version_document.metadata
        return WorkflowMutationPlan(
            operation="change-create",
            workflow=request.workflow,
            version=version,
            target=self._repo_relative(target),
            mutations=tuple(mutations),
            source_version=version,
            policies=tuple(copy.deepcopy(version_metadata.get("policies", []))),
            dependencies=tuple(copy.deepcopy(version_metadata.get("dependencies", []))),
            authoring_basis=(f"proposal={request.proposal_path}; impact={request.impact_path}"),
            remaining_decisions=("change decision and approval",),
            post_transition="proposed" if request.propose else None,
        )

    def plan_evolve(self, request: EvolveWorkflowRequest) -> WorkflowMutationPlan:
        """Plan the unique next-version draft from every accepted active change."""
        self._require_structurally_valid()
        registry_document = read_markdown_document(self.registry_path)
        registry = copy.deepcopy(registry_document.metadata)
        family = self._family(registry, request.workflow)
        if family.get("title") != request.title:
            raise WorkflowAuthoringError("evolve request title must match the workflow family")
        versions = self._versions(family, request.workflow)
        active = [
            (version, record)
            for version, record in versions.items()
            if isinstance(record, dict) and record.get("status") == "active"
        ]
        if len(active) != 1:
            raise WorkflowAuthoringError(
                f"workflow family must have exactly one active version: {request.workflow}"
            )
        active_version, active_record = active[0]
        active_path = self.root / str(active_record["path"])
        changes_root = active_path / "work" / "changes"
        accepted: list[Path] = []
        if changes_root.exists():
            for change in sorted(path for path in changes_root.iterdir() if path.is_dir()):
                metadata = read_markdown_document(change / "README.md").metadata
                if metadata.get("status") == "accepted":
                    accepted.append(change)
        if not accepted:
            raise WorkflowAuthoringError(
                "evolve requires at least one accepted change with a human decision"
            )
        definition = self._resolve_repo_reference(request.definition_path)
        if not _is_substantive(definition):
            raise WorkflowAuthoringError("evolve request definition must be complete Markdown")
        policies = self._authoring_policies(request.policies)
        dependencies = [copy.deepcopy(item) for item in request.dependencies]
        dependency_issues: list[ValidationIssue] = []
        self._validate_dependencies(dependencies, self.registry_path, dependency_issues)
        if dependency_issues:
            raise WorkflowAuthoringError("; ".join(str(issue) for issue in dependency_issues))

        drafts = [
            (version, record)
            for version, record in versions.items()
            if isinstance(record, dict) and record.get("status") == "draft"
        ]
        if len(drafts) > 1:
            raise WorkflowAuthoringError("workflow family has more than one draft")
        if drafts:
            version, record = drafts[0]
            target = self.root / str(record["path"])
            action = "update"
            update_registry = False
        else:
            used = {_version_number(item) for item in versions if VERSION_PATTERN.fullmatch(item)}
            used.update(
                _version_number(match.group("version"))
                for path in self.root.glob(f"{request.workflow}--v*")
                if (match := WORKFLOW_DIRECTORY_PATTERN.fullmatch(path.name)) is not None
            )
            version = f"v{max(used, default=0) + 1:03d}"
            target = self.root / f"{request.workflow}--{version}"
            versions[version] = {"path": target.name, "status": "draft"}
            action = "create"
            update_registry = True

        source_changes = [self._repo_relative(change) for change in accepted]
        metadata = {
            "workflow": request.workflow,
            "title": request.title,
            "version": version,
            "definition": "WORKFLOW.md",
            "supersedes": active_version,
            "derived_from": None,
            "source_changes": source_changes,
            "capabilities": list(request.capabilities),
            "policies": policies,
            "dependencies": dependencies,
        }
        mutations: list[WorkflowFileMutation] = [
            self._planned_mutation(
                action=action,
                path=self._repo_relative(target / "README.md"),
                content=render_markdown_document(
                    MarkdownDocument(
                        metadata,
                        self._initial_version_body(
                            title=request.title,
                            authoring_basis=request.authoring_basis,
                        ),
                    )
                ),
            ),
            self._planned_mutation(
                action=action,
                path=self._repo_relative(target / "WORKFLOW.md"),
                content=definition.read_bytes(),
            ),
        ]
        if update_registry:
            mutations.append(
                self._planned_mutation(
                    action="update",
                    path=self._repo_relative(self.registry_path),
                    content=render_markdown_document(
                        MarkdownDocument(registry, registry_document.body)
                    ),
                )
            )
        return WorkflowMutationPlan(
            operation="evolve",
            workflow=request.workflow,
            version=version,
            target=self._repo_relative(target),
            mutations=tuple(mutations),
            source_version=active_version,
            source_changes=tuple(source_changes),
            policies=tuple(copy.deepcopy(policies)),
            dependencies=tuple(copy.deepcopy(dependencies)),
            authoring_basis=request.authoring_basis,
            remaining_decisions=("replacement release approval",),
        )

    def apply(self, plan: WorkflowMutationPlan) -> WorkflowMutationResult:
        """Apply one already-previewed authoring plan through existing validators."""
        with self.authoring_lease():
            self._require_structurally_valid()
            self._require_plan_targets_unchanged(plan)
            publication = self._stage_after_tree(plan)
            self._require_plan_targets_unchanged(plan)
            before = {
                path: path.read_bytes() if path.is_file() else None
                for path, _content in publication
            }
            try:
                for index, (path, content) in enumerate(publication):
                    self.publish_hook("before", path, index)
                    _atomic_write(path, content, replace=path.exists())
                    self.publish_hook("after", path, index)
                self._require_valid()
            except Exception as exc:
                self._rollback_publication(before)
                try:
                    self._require_valid()
                except WorkflowAuthoringError as rollback_error:
                    raise WorkflowAuthoringError(
                        "authoring publish failed and rollback validation also failed: "
                        f"{rollback_error}"
                    ) from exc
                raise WorkflowAuthoringError(
                    f"authoring publish failed and was rolled back: {exc}"
                ) from exc
            return WorkflowMutationResult(
                operation=plan.operation,
                workflow=plan.workflow,
                version=plan.version,
                target=self._resolve_repo_reference(plan.target),
            )

    def _require_plan_targets_unchanged(self, plan: WorkflowMutationPlan) -> None:
        for mutation in plan.mutations:
            path = self._resolve_repo_reference(mutation.path)
            current_digest = _sha256(path) if path.is_file() else None
            if current_digest != mutation.before_sha256:
                raise WorkflowAuthoringError(f"authoring target drift: {mutation.path}")

    def _stage_after_tree(self, plan: WorkflowMutationPlan) -> tuple[tuple[Path, bytes], ...]:
        """Build and validate the complete after-tree outside the canonical workflow root."""
        with tempfile.TemporaryDirectory(prefix="workflow-authoring-stage-") as temporary_name:
            staging_root = Path(temporary_name) / self.root.name
            shutil.copytree(
                self.root,
                staging_root,
                ignore=shutil.ignore_patterns(self.authoring_lock_path.name),
            )
            staged = WorkflowRepository(
                staging_root,
                now=self.now,
                git_index_checker=self.git_index_checker,
                lock_timeout_seconds=self.lock_timeout_seconds,
                _repository_root=self.repo_root,
                _canonical_workflow_root=self.root,
            )
            for mutation in plan.mutations:
                canonical = self._resolve_repo_reference(mutation.path)
                try:
                    relative = canonical.relative_to(self.root.resolve())
                except ValueError as exc:
                    raise WorkflowAuthoringError(
                        f"authoring mutation escapes workflow root: {mutation.path}"
                    ) from exc
                target = staging_root / relative
                if mutation.action == "create":
                    _atomic_write(target, mutation.content, replace=False)
                elif mutation.action == "update":
                    _atomic_write(target, mutation.content)
                else:
                    raise WorkflowAuthoringError(
                        f"unsupported workflow mutation action: {mutation.action}"
                    )
            try:
                staged.sync()
                if plan.post_transition is not None:
                    staged.transition_change(
                        staged._resolve_repo_reference(plan.target),
                        plan.post_transition,
                    )
                staged._require_valid()
            except WorkflowAuthoringError as exc:
                raise WorkflowAuthoringError(f"staged workflow validation failed: {exc}") from exc
            self.stage_hook(Path(temporary_name))

            planned_paths = {
                self._resolve_repo_reference(mutation.path) for mutation in plan.mutations
            }
            publication: list[tuple[Path, bytes]] = []
            for staged_path in sorted(path for path in staging_root.rglob("*") if path.is_file()):
                if staged_path.name == staged.authoring_lock_path.name:
                    continue
                relative = staged_path.relative_to(staging_root)
                canonical = self.root.resolve() / relative
                content = staged_path.read_bytes()
                if canonical.is_file() and canonical.read_bytes() == content:
                    continue
                if canonical not in planned_paths:
                    raise WorkflowAuthoringError(
                        f"staged workflow changed an unplanned target: {canonical}"
                    )
                publication.append((canonical, content))
            return tuple(publication)

    def _rollback_publication(self, before: Mapping[Path, bytes | None]) -> None:
        for path, content in reversed(tuple(before.items())):
            if content is None:
                path.unlink(missing_ok=True)
            else:
                _atomic_write(path, content)
        for path, content in reversed(tuple(before.items())):
            if content is not None:
                continue
            parent = path.parent
            while parent != self.root.resolve() and parent.is_relative_to(self.root.resolve()):
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent

    def sync(self) -> None:
        """Regenerate root and per-version human-readable indexes from metadata."""
        with self.authoring_lease():
            self._require_structurally_valid()
            self._sync_locked()
            self._require_valid()

    def _sync_locked(self) -> None:
        """Regenerate indexes while the caller holds the authoring lease."""
        document = read_markdown_document(self.registry_path)
        issues: list[ValidationIssue] = []
        workflows = self._validate_registry_metadata(document.metadata, issues)
        if workflows is None or issues:
            raise WorkflowAuthoringError("; ".join(str(issue) for issue in issues))
        body = _replace_generated_region(
            document.body,
            ROOT_INDEX_START,
            ROOT_INDEX_END,
            self._render_root_index(workflows),
        )
        _atomic_write(
            self.registry_path,
            render_markdown_document(MarkdownDocument(document.metadata, body)),
        )
        for family in workflows.values():
            versions = family.get("versions")
            if not isinstance(versions, Mapping):
                continue
            for record in versions.values():
                if not isinstance(record, Mapping) or not isinstance(record.get("path"), str):
                    continue
                version_path = self.root / str(record["path"])
                readme = version_path / "README.md"
                if not readme.exists():
                    continue
                version_document = read_markdown_document(readme)
                version_body = _replace_generated_region(
                    version_document.body,
                    WORK_INDEX_START,
                    WORK_INDEX_END,
                    self._render_work_index(version_path),
                )
                _atomic_write(
                    readme,
                    render_markdown_document(
                        MarkdownDocument(version_document.metadata, version_body)
                    ),
                )

    def transition_change(
        self,
        change_path: Path,
        target_status: str,
        *,
        approved_by: str | None = None,
    ) -> None:
        """Apply one legal change lifecycle transition with current-time evidence."""
        with self.authoring_lease():
            self._transition_change_locked(
                change_path,
                target_status,
                approved_by=approved_by,
            )

    def _transition_change_locked(
        self,
        change_path: Path,
        target_status: str,
        *,
        approved_by: str | None = None,
    ) -> None:
        """Transition a change while the caller holds the authoring lease."""
        path = self._resolve_input(change_path)
        self._require_structurally_valid()
        version_path = self._containing_version(path)
        registry, slug, version, version_record = self._registered_version(version_path)
        del registry
        if version_record.get("status") != "active":
            raise WorkflowAuthoringError("changes may transition only under the active version")
        document = read_markdown_document(path / "README.md")
        metadata = copy.deepcopy(document.metadata)
        current = metadata.get("status")
        if not isinstance(current, str) or current not in CHANGE_STATUSES:
            raise WorkflowAuthoringError("change has an invalid current status")
        if target_status == "released":
            raise WorkflowAuthoringError("released may be set only by workflow release")
        if target_status not in _CHANGE_TRANSITIONS.get(current, frozenset()):
            raise WorkflowAuthoringError(f"illegal change transition: {current} -> {target_status}")
        if metadata.get("workflow") != slug or metadata.get("source_version") != version:
            raise WorkflowAuthoringError("change identity does not match its source version")
        if target_status == "proposed":
            for filename in ("PROPOSAL.md", "IMPACT.md"):
                if not _is_substantive(path / filename):
                    raise WorkflowAuthoringError(f"{filename} must be completed before proposal")
        if target_status in _DECISION_STATUSES:
            if not approved_by or not approved_by.strip():
                raise WorkflowAuthoringError(f"{target_status} requires --approved-by")
            for filename in ("VALIDATION.md", "DECISION.md"):
                if not _is_substantive(path / filename):
                    raise WorkflowAuthoringError(f"{filename} must be completed before decision")
        if target_status == "withdrawn" and not _is_substantive(path / "DECISION.md"):
            raise WorkflowAuthoringError("DECISION.md must explain why the change was withdrawn")

        occurred_at = timestamp_text(self._current_time())
        metadata["status"] = target_status
        metadata["status_changed_at"] = occurred_at
        if target_status in _DECISION_STATUSES:
            metadata["decided_at"] = occurred_at
            metadata["decided_by"] = approved_by.strip() if approved_by else None
        _atomic_write(
            path / "README.md",
            render_markdown_document(MarkdownDocument(metadata, document.body)),
        )
        self.sync()
        self._require_valid()

    def transition_version(
        self,
        version_path: Path,
        target_status: str,
        *,
        approved_by: str | None = None,
    ) -> None:
        """Abandon an unreleased draft or retire the active version."""
        with self.authoring_lease():
            self._transition_version_locked(
                version_path,
                target_status,
                approved_by=approved_by,
            )

    def _transition_version_locked(
        self,
        version_path: Path,
        target_status: str,
        *,
        approved_by: str | None = None,
    ) -> None:
        """Transition a version while the caller holds the authoring lease."""
        path = self._resolve_input(version_path)
        self._require_structurally_valid()
        registry, _slug, _version, record = self._registered_version(path)
        current = record.get("status")
        if target_status == "abandoned":
            if current != "draft":
                raise WorkflowAuthoringError("only a draft version may be abandoned")
        elif target_status == "retired":
            if current != "active":
                raise WorkflowAuthoringError("only an active version may be retired")
            if not approved_by or not approved_by.strip():
                raise WorkflowAuthoringError("retiring a workflow requires --approved-by")
            self._require_no_blocking_changes(path, included_changes=frozenset())
            self._require_studies_ready_for_version_end(path)
        else:
            raise WorkflowAuthoringError("version transition supports only abandoned or retired")
        occurred_at = timestamp_text(self._current_time())
        record["status"] = target_status
        record["status_changed_at"] = occurred_at
        record["status_changed_by"] = approved_by.strip() if approved_by else None
        self._write_registry(registry)
        self.sync()
        self._require_valid()

    def release(self, version_path: Path, *, approved_by: str) -> dict[str, Any]:
        """Prepare an approved release declaration and intended canonical registry state."""
        with self.authoring_lease():
            return self._release_locked(version_path, approved_by=approved_by)

    def _release_locked(self, version_path: Path, *, approved_by: str) -> dict[str, Any]:
        """Prepare a release while the caller holds the authoring lease."""
        if not approved_by.strip():
            raise WorkflowAuthoringError("workflow release requires --approved-by")
        path = self._resolve_input(version_path)
        registry, slug, version, record = self._registered_version(path)
        if record.get("status") != "draft":
            raise WorkflowAuthoringError("only a draft workflow version may be released")
        release_path = path / "RELEASE.json"
        if release_path.exists():
            raise WorkflowAuthoringError("draft already has a RELEASE.json")
        document = read_markdown_document(path / "README.md")
        metadata = document.metadata
        if metadata.get("workflow") != slug or metadata.get("version") != version:
            raise WorkflowAuthoringError("version README identity does not match registry")
        definition_name = metadata.get("definition")
        if definition_name != "WORKFLOW.md":
            raise WorkflowAuthoringError("definition must be WORKFLOW.md")
        definition_path = path / definition_name
        if not _is_substantive(definition_path):
            raise WorkflowAuthoringError("WORKFLOW.md must be complete before release")

        family = self._family(registry, slug)
        versions = self._versions(family, slug)
        active_items = [
            (item_version, item_record)
            for item_version, item_record in versions.items()
            if isinstance(item_record, Mapping) and item_record.get("status") == "active"
        ]
        supersedes = metadata.get("supersedes")
        if active_items:
            if len(active_items) != 1:
                raise WorkflowAuthoringError("workflow family must have exactly one active version")
            active_version, active_record = active_items[0]
            if supersedes != active_version:
                raise WorkflowAuthoringError(
                    f"draft must supersede the active version {active_version}"
                )
            if _version_number(version) <= _version_number(active_version):
                raise WorkflowAuthoringError(
                    "released version must be newer than the active version"
                )
        else:
            active_version = None
            active_record = None
            if supersedes is not None:
                raise WorkflowAuthoringError(
                    "initial workflow release must not supersede a version"
                )

        self._require_structurally_valid(
            allow_active_dependency_drift_for=(
                (slug, active_version) if active_version is not None else None
            )
        )

        source_changes = metadata.get("source_changes")
        if not isinstance(source_changes, list) or not all(
            isinstance(item, str) and item for item in source_changes
        ):
            raise WorkflowAuthoringError("source_changes must be a list of repository paths")
        if active_version is not None and not source_changes:
            raise WorkflowAuthoringError("a replacement version requires accepted source changes")
        if active_version is None and source_changes:
            raise WorkflowAuthoringError("an initial workflow release cannot have source changes")
        change_documents: list[tuple[Path, MarkdownDocument]] = []
        for reference in source_changes:
            change_path = self._resolve_repo_reference(reference)
            if not change_path.is_dir():
                raise WorkflowAuthoringError(f"source change does not exist: {reference}")
            if (
                self._containing_version(change_path)
                != (self.root / str(active_record["path"])).resolve()
            ):
                raise WorkflowAuthoringError(
                    f"source change must belong to {active_version}: {reference}"
                )
            change_document = read_markdown_document(change_path / "README.md")
            change_metadata = change_document.metadata
            if change_metadata.get("status") != "accepted":
                raise WorkflowAuthoringError(f"source change is not accepted: {reference}")
            if change_metadata.get("workflow") != slug:
                raise WorkflowAuthoringError(
                    f"source change belongs to another workflow: {reference}"
                )
            change_documents.append((change_path, change_document))

        if active_record is not None:
            active_path = self.root / str(active_record["path"])
            self._require_no_blocking_changes(
                active_path,
                included_changes=frozenset(path for path, _document in change_documents),
            )
            self._require_studies_ready_for_version_end(active_path)

        dependencies = self._release_dependencies(metadata.get("dependencies"))
        policies = self._release_policies(metadata.get("policies"))
        prepared_at = timestamp_text(self._current_time())
        release = {
            "schema_version": 1,
            "workflow": slug,
            "version": version,
            "approved_at": prepared_at,
            "prepared_at": prepared_at,
            "approved_by": approved_by.strip(),
            "workflow_sha256": _sha256(definition_path),
            "supersedes": supersedes,
            "derived_from": metadata.get("derived_from"),
            "source_changes": source_changes,
            "dependencies": dependencies,
            "policies": policies,
        }
        capabilities = metadata.get("capabilities", [])
        if not isinstance(capabilities, list) or not all(
            isinstance(item, str) and item.strip() for item in capabilities
        ):
            raise WorkflowAuthoringError("workflow capabilities must be a list of identifiers")
        if len(capabilities) != len(set(capabilities)):
            raise WorkflowAuthoringError("workflow capabilities must be unique")
        if capabilities:
            release["capabilities"] = capabilities

        _atomic_write(release_path, canonical_json_bytes(release), replace=False)
        for change_path, change_document in change_documents:
            change_metadata = copy.deepcopy(change_document.metadata)
            change_metadata["status"] = "released"
            change_metadata["released_in"] = version
            change_metadata["status_changed_at"] = prepared_at
            _atomic_write(
                change_path / "README.md",
                render_markdown_document(MarkdownDocument(change_metadata, change_document.body)),
            )
        if active_record is not None:
            active_record["status"] = "superseded"
            active_record["status_changed_at"] = prepared_at
            active_record["status_changed_by"] = approved_by.strip()
        record["status"] = "active"
        record["status_changed_at"] = prepared_at
        record["status_changed_by"] = approved_by.strip()
        self._write_registry(registry)
        self.sync()
        self._require_valid()
        return release

    def _validate_registry_metadata(
        self,
        metadata: Mapping[str, Any],
        issues: list[ValidationIssue],
    ) -> dict[str, dict[str, Any]] | None:
        if metadata.get("schema_version") != 1:
            issues.append(ValidationIssue(self.registry_path, "schema_version must be 1"))
        raw_workflows = metadata.get("workflows")
        if not isinstance(raw_workflows, dict):
            issues.append(ValidationIssue(self.registry_path, "workflows must be a mapping"))
            return None
        paths: set[str] = set()
        for slug, family in raw_workflows.items():
            if not isinstance(slug, str) or not SLUG_PATTERN.fullmatch(slug):
                issues.append(ValidationIssue(self.registry_path, f"invalid workflow slug: {slug}"))
                continue
            if not isinstance(family, dict):
                issues.append(ValidationIssue(self.registry_path, f"{slug} must be a mapping"))
                continue
            if not isinstance(family.get("title"), str) or not family["title"].strip():
                issues.append(ValidationIssue(self.registry_path, f"{slug} title is required"))
            versions = family.get("versions")
            if not isinstance(versions, dict) or not versions:
                issues.append(
                    ValidationIssue(self.registry_path, f"{slug} versions must be non-empty")
                )
                continue
            active_count = 0
            draft_count = 0
            for version, record in versions.items():
                if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
                    issues.append(
                        ValidationIssue(
                            self.registry_path, f"{slug} has invalid version: {version}"
                        )
                    )
                    continue
                if not isinstance(record, dict):
                    issues.append(
                        ValidationIssue(
                            self.registry_path,
                            f"{slug} {version} registry entry must be a mapping",
                        )
                    )
                    continue
                expected_path = f"{slug}--{version}"
                path_text = record.get("path")
                if path_text != expected_path:
                    issues.append(
                        ValidationIssue(
                            self.registry_path,
                            f"{slug} {version} path must be {expected_path}",
                        )
                    )
                elif path_text in paths:
                    issues.append(
                        ValidationIssue(self.registry_path, f"duplicate version path: {path_text}")
                    )
                else:
                    paths.add(path_text)
                status = record.get("status")
                if status not in VERSION_STATUSES:
                    issues.append(
                        ValidationIssue(
                            self.registry_path,
                            f"{slug} {version} has invalid status: {status}",
                        )
                    )
                active_count += int(status == "active")
                draft_count += int(status == "draft")
                if status in {"active", "superseded", "retired"}:
                    if not _is_canonical_utc_timestamp(record.get("status_changed_at")):
                        issues.append(
                            ValidationIssue(
                                self.registry_path,
                                f"{slug} {version} needs canonical UTC status_changed_at",
                            )
                        )
                    if (
                        not isinstance(record.get("status_changed_by"), str)
                        or not str(record.get("status_changed_by")).strip()
                    ):
                        issues.append(
                            ValidationIssue(
                                self.registry_path,
                                f"{slug} {version} needs status_changed_by",
                            )
                        )
                if status == "abandoned" and not _is_canonical_utc_timestamp(
                    record.get("status_changed_at")
                ):
                    issues.append(
                        ValidationIssue(
                            self.registry_path,
                            f"{slug} {version} needs canonical UTC status_changed_at",
                        )
                    )
            if active_count > 1:
                issues.append(
                    ValidationIssue(self.registry_path, f"{slug} has more than one active version")
                )
            if draft_count > 1:
                issues.append(
                    ValidationIssue(self.registry_path, f"{slug} has more than one draft version")
                )
        return raw_workflows

    def _validate_version(
        self,
        path: Path,
        *,
        slug: str,
        version: str,
        record: Mapping[str, Any],
        issues: list[ValidationIssue],
        allow_active_dependency_drift: bool,
    ) -> None:
        if not path.is_dir():
            issues.append(ValidationIssue(path, "registered workflow version directory is missing"))
            return
        match = WORKFLOW_DIRECTORY_PATTERN.fullmatch(path.name)
        if not match or match.group("slug") != slug or match.group("version") != version:
            issues.append(ValidationIssue(path, "directory identity does not match registry"))
        readme = path / "README.md"
        definition = path / "WORKFLOW.md"
        for required in (readme, definition):
            if not required.is_file():
                issues.append(ValidationIssue(required, "required workflow file is missing"))
        if not readme.exists():
            return
        try:
            document = read_markdown_document(readme)
        except WorkflowAuthoringError as exc:
            issues.append(ValidationIssue(readme, str(exc)))
            return
        metadata = document.metadata
        required_fields = (
            "workflow",
            "title",
            "version",
            "definition",
            "supersedes",
            "derived_from",
            "source_changes",
            "dependencies",
        )
        for field in required_fields:
            if field not in metadata:
                issues.append(ValidationIssue(readme, f"missing frontmatter field: {field}"))
        if metadata.get("workflow") != slug:
            issues.append(ValidationIssue(readme, "workflow does not match directory slug"))
        if metadata.get("version") != version:
            issues.append(ValidationIssue(readme, "version does not match directory suffix"))
        if metadata.get("definition") != "WORKFLOW.md":
            issues.append(ValidationIssue(readme, "definition must be WORKFLOW.md"))
        if not isinstance(metadata.get("title"), str) or not str(metadata.get("title")).strip():
            issues.append(ValidationIssue(readme, "title must be a non-empty string"))
        supersedes = metadata.get("supersedes")
        if supersedes is not None and (
            not isinstance(supersedes, str) or not VERSION_PATTERN.fullmatch(supersedes)
        ):
            issues.append(ValidationIssue(readme, "supersedes must be null or a version ID"))
        elif isinstance(supersedes, str) and _version_number(supersedes) >= _version_number(
            version
        ):
            issues.append(ValidationIssue(readme, "supersedes must identify an older version"))
        source_changes = metadata.get("source_changes")
        if not isinstance(source_changes, list):
            issues.append(ValidationIssue(readme, "source_changes must be a list"))
        else:
            self._validate_source_changes(
                source_changes,
                readme,
                slug=slug,
                supersedes=supersedes,
                version_status=record.get("status"),
                issues=issues,
            )
        self._validate_dependencies(metadata.get("dependencies"), readme, issues)
        self._validate_derived_from(metadata.get("derived_from"), readme, issues)
        status = record.get("status")
        release_path = path / "RELEASE.json"
        if status in {"active", "superseded", "retired"}:
            if not release_path.is_file():
                issues.append(ValidationIssue(release_path, f"{status} version needs RELEASE.json"))
            else:
                self._validate_release(
                    release_path,
                    metadata=metadata,
                    slug=slug,
                    version=version,
                    status=str(status),
                    issues=issues,
                    check_active_dependency_digest=not allow_active_dependency_drift,
                )
        elif release_path.exists():
            issues.append(
                ValidationIssue(release_path, f"{status} version must not have RELEASE.json")
            )
        self._validate_changes(path, slug, version, status, issues)
        self._validate_studies(path, slug, version, status, issues)

    def _validate_release(
        self,
        path: Path,
        *,
        metadata: Mapping[str, Any],
        slug: str,
        version: str,
        status: str,
        issues: list[ValidationIssue],
        check_active_dependency_digest: bool,
    ) -> None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(ValidationIssue(path, f"invalid release JSON: {exc}"))
            return
        if not isinstance(payload, dict):
            issues.append(ValidationIssue(path, "release payload must be an object"))
            return
        if payload.get("schema_version") != 1:
            issues.append(ValidationIssue(path, "release schema_version must be 1"))
        if payload.get("workflow") != slug or payload.get("version") != version:
            issues.append(ValidationIssue(path, "release identity does not match version"))
        digest = payload.get("workflow_sha256")
        definition = path.parent / "WORKFLOW.md"
        if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
            issues.append(ValidationIssue(path, "workflow_sha256 must be a SHA-256 digest"))
        elif definition.exists() and _sha256(definition) != digest:
            issues.append(ValidationIssue(definition, "published WORKFLOW.md digest has changed"))
        if payload.get("supersedes") != metadata.get("supersedes"):
            issues.append(ValidationIssue(path, "release supersedes differs from README"))
        if payload.get("source_changes") != metadata.get("source_changes"):
            issues.append(ValidationIssue(path, "release source_changes differ from README"))
        if payload.get("derived_from") != metadata.get("derived_from"):
            issues.append(ValidationIssue(path, "release derived_from differs from README"))
        expected_capabilities = metadata.get("capabilities", [])
        if payload.get("capabilities", []) != expected_capabilities:
            issues.append(ValidationIssue(path, "release capabilities differ from README"))
        approved_by = payload.get("approved_by")
        if not isinstance(approved_by, str) or not approved_by.strip():
            issues.append(ValidationIssue(path, "release approved_by is required"))
        for field in ("approved_at", "prepared_at"):
            if not _is_canonical_utc_timestamp(payload.get(field)):
                issues.append(
                    ValidationIssue(path, f"release {field} must be a canonical UTC timestamp")
                )
        if payload.get("approved_at") != payload.get("prepared_at"):
            issues.append(
                ValidationIssue(path, "release approval and preparation times must match")
            )
        if "released_at" in payload:
            issues.append(
                ValidationIssue(path, "release must not claim released_at before canonical merge")
            )
        release_dependencies = payload.get("dependencies")
        if not isinstance(release_dependencies, list):
            issues.append(ValidationIssue(path, "release dependencies must be a list"))
            return
        expected_dependencies = metadata.get("dependencies")
        comparable_release = [
            {
                "path": item.get("path"),
                "role": item.get("role"),
                **({"pinned": True} if item.get("pinned") is True else {}),
            }
            for item in release_dependencies
            if isinstance(item, dict)
        ]
        if comparable_release != expected_dependencies:
            issues.append(ValidationIssue(path, "release dependencies differ from README"))
        for dependency in release_dependencies:
            if not isinstance(dependency, dict):
                issues.append(ValidationIssue(path, "release dependency must be a mapping"))
                continue
            if dependency.get("role") != "normative" and dependency.get("pinned") is not True:
                continue
            dependency_path = dependency.get("path")
            digest = dependency.get("sha256")
            if (
                not isinstance(dependency_path, str)
                or not isinstance(digest, str)
                or not SHA256_PATTERN.fullmatch(digest)
            ):
                issues.append(
                    ValidationIssue(path, "pinned release dependency needs a SHA-256 digest")
                )
                continue
            pinned_reference = dependency.get("pinned") is True
            if not pinned_reference and (status != "active" or not check_active_dependency_digest):
                continue
            try:
                resolved = self._resolve_repo_reference(dependency_path)
            except WorkflowAuthoringError as exc:
                issues.append(ValidationIssue(path, str(exc)))
                continue
            if resolved.is_file() and _sha256(resolved) != digest:
                if pinned_reference:
                    label = (
                        "active pinned dependency"
                        if status == "active"
                        else "released pinned dependency"
                    )
                else:
                    label = "active pinned dependency"
                issues.append(ValidationIssue(resolved, f"{label} digest has changed"))
        release_policies = payload.get("policies")
        if (self.repo_root / "policies" / "README.md").is_file():
            if not isinstance(release_policies, list):
                issues.append(ValidationIssue(path, "release policies must be a list"))
            elif release_policies != metadata.get("policies"):
                issues.append(ValidationIssue(path, "release policies differ from README"))
            else:
                for policy in release_policies:
                    if not isinstance(policy, dict):
                        issues.append(ValidationIssue(path, "release policy must be a mapping"))
                        continue
                    policy_path = policy.get("path")
                    expected_digest = policy.get("release_digest")
                    if not isinstance(policy_path, str) or not isinstance(expected_digest, str):
                        issues.append(
                            ValidationIssue(path, "release policy identity is incomplete")
                        )
                        continue
                    release_path = self.repo_root / policy_path / "RELEASE.json"
                    if not release_path.is_file() or _sha256(release_path) != expected_digest:
                        issues.append(
                            ValidationIssue(release_path, "policy release digest has changed")
                        )

    def _release_policies(self, raw: object) -> list[dict[str, str]]:
        policy_registry = self.repo_root / "policies" / "README.md"
        if not policy_registry.is_file():
            return []
        if not isinstance(raw, list) or not raw:
            raise WorkflowAuthoringError("workflow release requires explicit policy pins")
        from trading.policies import PolicyResolutionError, PolicyResolver

        resolver = PolicyResolver(self.repo_root / "policies")
        released: list[dict[str, str]] = []
        families: set[str] = set()
        for item in raw:
            if not isinstance(item, dict) or set(item) != {
                "family",
                "version",
                "path",
                "release_digest",
            }:
                raise WorkflowAuthoringError("policy pin has invalid fields")
            family = item.get("family")
            version = item.get("version")
            path = item.get("path")
            digest = item.get("release_digest")
            if not all(
                isinstance(value, str) and value for value in (family, version, path, digest)
            ):
                raise WorkflowAuthoringError("policy pin identity is incomplete")
            if family in families:
                raise WorkflowAuthoringError(f"duplicate policy family: {family}")
            families.add(family)
            try:
                resolved = resolver.resolve(family, version)
            except PolicyResolutionError as exc:
                raise WorkflowAuthoringError(str(exc)) from exc
            expected_path = resolved.path
            if path != expected_path or digest != resolved.release_digest:
                raise WorkflowAuthoringError(
                    f"policy pin does not match release: {family}@{version}"
                )
            released.append(dict(item))
        return released

    def _authoring_policies(
        self,
        raw: tuple[dict[str, Any], ...],
    ) -> list[dict[str, str]]:
        policy_registry = self.repo_root / "policies" / "README.md"
        if not policy_registry.is_file():
            raise WorkflowAuthoringError("workflow authoring requires a policy registry")
        released = self._release_policies(list(raw))
        from trading.policies import PolicyResolutionError, PolicyResolver

        resolver = PolicyResolver(self.repo_root / "policies")
        kinds: set[str] = set()
        for item in released:
            try:
                resolved = resolver.resolve(item["family"], item["version"])
            except PolicyResolutionError as exc:
                raise WorkflowAuthoringError(str(exc)) from exc
            if resolved.kind in kinds:
                raise WorkflowAuthoringError(f"duplicate policy kind: {resolved.kind}")
            kinds.add(resolved.kind)
        required = {"market", "broker", "execution", "portfolio-risk"}
        if kinds != required:
            missing = ", ".join(sorted(required.difference(kinds))) or "none"
            extra = ", ".join(sorted(kinds.difference(required))) or "none"
            raise WorkflowAuthoringError(
                f"workflow authoring requires four policy kinds; missing: {missing}; extra: {extra}"
            )
        return released

    def _validate_source_changes(
        self,
        raw: list[Any],
        path: Path,
        *,
        slug: str,
        supersedes: Any,
        version_status: Any,
        issues: list[ValidationIssue],
    ) -> None:
        seen: set[str] = set()
        released_version = version_status in {"active", "superseded", "retired"}
        for reference in raw:
            if not isinstance(reference, str) or not reference:
                issues.append(ValidationIssue(path, "source change must be a repository path"))
                continue
            if reference in seen:
                issues.append(ValidationIssue(path, f"duplicate source change: {reference}"))
                continue
            seen.add(reference)
            if supersedes is None:
                issues.append(
                    ValidationIssue(path, "source changes require a superseded source version")
                )
            try:
                change_path = self._resolve_repo_reference(reference)
            except WorkflowAuthoringError as exc:
                issues.append(ValidationIssue(path, str(exc)))
                continue
            if not change_path.is_dir():
                issues.append(
                    ValidationIssue(change_path, "source change directory does not exist")
                )
                continue
            try:
                change_version = self._containing_version(change_path)
                change_metadata = read_markdown_document(change_path / "README.md").metadata
            except WorkflowAuthoringError as exc:
                issues.append(ValidationIssue(change_path, str(exc)))
                continue
            if change_metadata.get("workflow") != slug:
                issues.append(
                    ValidationIssue(path, f"source change has another workflow: {reference}")
                )
            if isinstance(supersedes, str):
                expected_parent = self.root / f"{slug}--{supersedes}"
                if change_version != expected_parent.resolve():
                    issues.append(
                        ValidationIssue(path, f"source change is not under {slug}--{supersedes}")
                    )
                if change_metadata.get("source_version") != supersedes:
                    issues.append(
                        ValidationIssue(
                            path, f"source change does not target {supersedes}: {reference}"
                        )
                    )
            expected_status = "released" if released_version else "accepted"
            if change_metadata.get("status") != expected_status:
                issues.append(
                    ValidationIssue(
                        path,
                        f"source change must be {expected_status}: {reference}",
                    )
                )

    def _validate_dependencies(
        self,
        raw: Any,
        path: Path,
        issues: list[ValidationIssue],
    ) -> None:
        if not isinstance(raw, list):
            issues.append(ValidationIssue(path, "dependencies must be a list"))
            return
        seen: set[str] = set()
        for dependency in raw:
            if not isinstance(dependency, dict):
                issues.append(ValidationIssue(path, "dependency must be a mapping"))
                continue
            dependency_path = dependency.get("path")
            role = dependency.get("role")
            pinned = dependency.get("pinned", False)
            if not isinstance(dependency_path, str) or not dependency_path:
                issues.append(ValidationIssue(path, "dependency path is required"))
                continue
            if dependency_path in seen:
                issues.append(ValidationIssue(path, f"duplicate dependency: {dependency_path}"))
            seen.add(dependency_path)
            if role not in {"normative", "reference"}:
                issues.append(
                    ValidationIssue(path, f"dependency role must be normative or reference: {role}")
                )
            if type(pinned) is not bool:
                issues.append(ValidationIssue(path, "dependency pinned flag must be boolean"))
            if pinned is True and role != "reference":
                issues.append(
                    ValidationIssue(path, "only a reference dependency may use pinned: true")
                )
            try:
                resolved = self._resolve_repo_reference(dependency_path)
            except WorkflowAuthoringError as exc:
                issues.append(ValidationIssue(path, str(exc)))
                continue
            if not resolved.is_file():
                issues.append(ValidationIssue(resolved, "dependency file does not exist"))

    def _validate_derived_from(
        self,
        raw: Any,
        path: Path,
        issues: list[ValidationIssue],
    ) -> None:
        if raw is None:
            return
        if not isinstance(raw, dict):
            issues.append(ValidationIssue(path, "derived_from must be null or a mapping"))
            return
        if set(raw) != {"workflow", "version", "path"}:
            issues.append(
                ValidationIssue(path, "derived_from requires workflow, version, and path")
            )
            return
        if not isinstance(raw.get("workflow"), str) or not SLUG_PATTERN.fullmatch(
            str(raw.get("workflow"))
        ):
            issues.append(ValidationIssue(path, "derived_from workflow is invalid"))
        if not isinstance(raw.get("version"), str) or not VERSION_PATTERN.fullmatch(
            str(raw.get("version"))
        ):
            issues.append(ValidationIssue(path, "derived_from version is invalid"))
        raw_path = raw.get("path")
        if not isinstance(raw_path, str):
            issues.append(ValidationIssue(path, "derived_from path is invalid"))
            return
        try:
            resolved = self._resolve_repo_reference(raw_path)
        except WorkflowAuthoringError as exc:
            issues.append(ValidationIssue(path, str(exc)))
            return
        if not resolved.is_dir():
            issues.append(ValidationIssue(resolved, "derived_from version does not exist"))
            return
        expected_name = f"{raw.get('workflow')}--{raw.get('version')}"
        if resolved.name != expected_name or resolved.parent != self.root.resolve():
            issues.append(ValidationIssue(path, f"derived_from path must identify {expected_name}"))

    def _validate_changes(
        self,
        version_path: Path,
        slug: str,
        version: str,
        version_status: Any,
        issues: list[ValidationIssue],
    ) -> None:
        root = version_path / "work" / "changes"
        if not root.exists():
            return
        ids: set[str] = set()
        for change_path in sorted(path for path in root.iterdir() if path.is_dir()):
            match = CHANGE_DIRECTORY_PATTERN.fullmatch(change_path.name)
            if not match:
                issues.append(ValidationIssue(change_path, "invalid change directory name"))
                continue
            readme = change_path / "README.md"
            required = ("README.md", "PROPOSAL.md", "IMPACT.md", "VALIDATION.md", "DECISION.md")
            for filename in required:
                if not (change_path / filename).is_file():
                    issues.append(
                        ValidationIssue(change_path / filename, "required change file is missing")
                    )
            if not readme.exists():
                continue
            try:
                metadata = read_markdown_document(readme).metadata
            except WorkflowAuthoringError as exc:
                issues.append(ValidationIssue(readme, str(exc)))
                continue
            expected_id = f"C{match.group('number')}"
            for field in (
                "id",
                "title",
                "workflow",
                "source_version",
                "status",
                "created_at",
                "status_changed_at",
                "decided_at",
                "decided_by",
                "released_in",
            ):
                if field not in metadata:
                    issues.append(ValidationIssue(readme, f"missing frontmatter field: {field}"))
            change_id = metadata.get("id")
            if change_id != expected_id:
                issues.append(ValidationIssue(readme, f"id must be {expected_id}"))
            if isinstance(change_id, str) and change_id in ids:
                issues.append(ValidationIssue(readme, f"duplicate change id: {change_id}"))
            elif isinstance(change_id, str):
                ids.add(change_id)
            if metadata.get("workflow") != slug or metadata.get("source_version") != version:
                issues.append(ValidationIssue(readme, "change source identity is inconsistent"))
            if not isinstance(metadata.get("title"), str) or not str(metadata.get("title")).strip():
                issues.append(ValidationIssue(readme, "change title must be a non-empty string"))
            created_at = metadata.get("created_at")
            if not isinstance(created_at, str) or not re.fullmatch(
                r"\d{4}-\d{2}-\d{2}", created_at
            ):
                issues.append(ValidationIssue(readme, "created_at must be YYYY-MM-DD text"))
            status = metadata.get("status")
            if status not in CHANGE_STATUSES:
                issues.append(ValidationIssue(readme, f"invalid change status: {status}"))
            elif status != "draft" and not _is_canonical_utc_timestamp(
                metadata.get("status_changed_at")
            ):
                issues.append(
                    ValidationIssue(
                        readme, "non-draft change needs canonical UTC status_changed_at"
                    )
                )
            required_substantive: tuple[str, ...] = ()
            if status == "proposed":
                required_substantive = ("PROPOSAL.md", "IMPACT.md")
            elif status in _DECISION_STATUSES | {"released"}:
                required_substantive = (
                    "PROPOSAL.md",
                    "IMPACT.md",
                    "VALIDATION.md",
                    "DECISION.md",
                )
            elif status == "withdrawn":
                required_substantive = ("DECISION.md",)
            for filename in required_substantive:
                if not _is_substantive(change_path / filename):
                    issues.append(
                        ValidationIssue(
                            change_path / filename,
                            f"{status} change needs completed {filename}",
                        )
                    )
            if status == "released":
                if not isinstance(
                    metadata.get("released_in"), str
                ) or not VERSION_PATTERN.fullmatch(str(metadata.get("released_in"))):
                    issues.append(ValidationIssue(readme, "released change needs released_in"))
            elif metadata.get("released_in") is not None:
                issues.append(
                    ValidationIssue(readme, "unreleased change must have released_in: null")
                )
            if status in _DECISION_STATUSES | {"released"}:
                if not metadata.get("decided_by") or not _is_canonical_utc_timestamp(
                    metadata.get("decided_at")
                ):
                    issues.append(ValidationIssue(readme, "decided change needs approver and time"))
            if version_status != "active" and status in {"draft", "proposed", "accepted"}:
                issues.append(
                    ValidationIssue(
                        readme,
                        f"{version_status} workflow version cannot have open change {change_id}",
                    )
                )

    def _validate_studies(
        self,
        version_path: Path,
        slug: str,
        version: str,
        version_status: Any,
        issues: list[ValidationIssue],
    ) -> None:
        root = version_path / "work" / "studies"
        if not root.exists():
            return
        structured_routes = False
        release_path = version_path / "RELEASE.json"
        if release_path.is_file():
            try:
                release_payload = json.loads(release_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                release_payload = {}
            structured_routes = isinstance(
                release_payload, dict
            ) and "study-time-retrospective-v1" in release_payload.get("capabilities", [])
        ids: set[str] = set()
        for study_path in sorted(path for path in root.iterdir() if path.is_dir()):
            match = STUDY_DIRECTORY_PATTERN.fullmatch(study_path.name)
            if not match:
                issues.append(ValidationIssue(study_path, "invalid study directory name"))
                continue
            required = ("README.md", "HYPOTHESIS.md", "PLAN.md", "EVIDENCE.md", "CONCLUSION.md")
            for filename in required:
                if not (study_path / filename).is_file():
                    issues.append(
                        ValidationIssue(study_path / filename, "required study file is missing")
                    )
            readme = study_path / "README.md"
            if not readme.exists():
                continue
            try:
                metadata = read_markdown_document(readme).metadata
            except WorkflowAuthoringError as exc:
                issues.append(ValidationIssue(readme, str(exc)))
                continue
            expected_id = f"S{match.group('number')}"
            for field in (
                "id",
                "title",
                "workflow",
                "workflow_version",
                "status",
                "outcome",
                "created_at",
                "created_by",
                "status_changed_at",
                "status_changed_by",
                "status_reason",
                "preregistered_at",
                "preregistered_by",
                "completed_at",
                "reviewed_by",
                "revisits",
            ):
                if field not in metadata:
                    issues.append(ValidationIssue(readme, f"missing frontmatter field: {field}"))
            study_id = metadata.get("id")
            if study_id != expected_id:
                issues.append(ValidationIssue(readme, f"id must be {expected_id}"))
            if isinstance(study_id, str) and study_id in ids:
                issues.append(ValidationIssue(readme, f"duplicate study id: {study_id}"))
            elif isinstance(study_id, str):
                ids.add(study_id)
            if metadata.get("workflow") != slug or metadata.get("workflow_version") != version:
                issues.append(ValidationIssue(readme, "study workflow identity is inconsistent"))
            if not isinstance(metadata.get("title"), str) or not str(metadata.get("title")).strip():
                issues.append(ValidationIssue(readme, "study title must be a non-empty string"))
            route = metadata.get("route")
            if structured_routes and route is None:
                issues.append(ValidationIssue(readme, "released workflow requires a study route"))
            if route is not None and route not in STUDY_ROUTES:
                issues.append(ValidationIssue(readme, f"invalid study route: {route}"))
            qualification_spec = study_path / "QUALIFICATION_SPEC.json"
            if structured_routes and not qualification_spec.is_file():
                issues.append(
                    ValidationIssue(
                        qualification_spec,
                        "capability-scoped study requires QUALIFICATION_SPEC.json",
                    )
                )
            if not _is_canonical_utc_timestamp(metadata.get("created_at")):
                issues.append(ValidationIssue(readme, "study created_at must be canonical UTC"))
            if (
                not isinstance(metadata.get("created_by"), str)
                or not str(metadata.get("created_by")).strip()
            ):
                issues.append(ValidationIssue(readme, "study created_by is required"))
            status = metadata.get("status")
            outcome = metadata.get("outcome")
            if status not in STUDY_STATUSES:
                issues.append(ValidationIssue(readme, f"invalid study status: {status}"))
            elif status == "draft":
                if (
                    metadata.get("status_changed_at") is not None
                    or metadata.get("status_changed_by") is not None
                ):
                    issues.append(
                        ValidationIssue(readme, "draft study must not claim a status transition")
                    )
            elif (
                not _is_canonical_utc_timestamp(metadata.get("status_changed_at"))
                or not str(metadata.get("status_changed_by") or "").strip()
            ):
                issues.append(
                    ValidationIssue(readme, "non-draft study needs transition time and identity")
                )
            if version_status in {"draft", "abandoned"}:
                issues.append(ValidationIssue(readme, "study requires a released workflow version"))
            elif version_status != "active" and status in {
                "draft",
                "preregistered",
                "running",
                "awaiting-review",
            }:
                issues.append(
                    ValidationIssue(
                        readme,
                        f"{version_status} workflow version cannot have active study {study_id}",
                    )
                )
            if status == "completed" and outcome not in STUDY_OUTCOMES:
                issues.append(ValidationIssue(readme, "completed study needs a valid outcome"))
            if status != "completed" and outcome is not None:
                issues.append(ValidationIssue(readme, "only completed studies may have an outcome"))
            if status == "completed":
                if (
                    not _is_canonical_utc_timestamp(metadata.get("completed_at"))
                    or not str(metadata.get("reviewed_by") or "").strip()
                ):
                    issues.append(
                        ValidationIssue(
                            readme, "completed study needs completion time and reviewer"
                        )
                    )
            development_authorization = study_path / "DEVELOPMENT_AUTHORIZATION.json"
            authorization_required = status in {
                "running",
                "paused",
                "awaiting-review",
                "completed",
            } or (status == "cancelled" and development_authorization.exists())
            if structured_routes and authorization_required:
                self._validate_development_authorization(
                    development_authorization,
                    metadata,
                    study_path,
                    issues,
                )
            elif development_authorization.exists():
                issues.append(
                    ValidationIssue(
                        development_authorization,
                        "Development authorization exists before the study starts",
                    )
                )
            candidate_freeze = study_path / "CANDIDATE_FREEZE.json"
            if structured_routes and candidate_freeze.exists():
                self._validate_guarded_candidate_freeze(candidate_freeze, study_path, issues)
            if status == "completed":
                if metadata.get("status_changed_at") != metadata.get(
                    "completed_at"
                ) or metadata.get("status_changed_by") != metadata.get("reviewed_by"):
                    issues.append(
                        ValidationIssue(readme, "completion and status transition must agree")
                    )
            elif (
                metadata.get("completed_at") is not None or metadata.get("reviewed_by") is not None
            ):
                issues.append(
                    ValidationIssue(readme, "unfinished study must not claim completion metadata")
                )
            if (
                status in {"paused", "cancelled"}
                and not str(metadata.get("status_reason") or "").strip()
            ):
                issues.append(ValidationIssue(readme, f"{status} study needs a status reason"))

            revisits = metadata.get("revisits")
            if revisits is not None:
                if not isinstance(revisits, str) or not revisits:
                    issues.append(ValidationIssue(readme, "revisits must be null or a study path"))
                else:
                    try:
                        revisited = self._resolve_repo_reference(revisits)
                    except WorkflowAuthoringError as exc:
                        issues.append(ValidationIssue(readme, str(exc)))
                    else:
                        try:
                            revisited_version = self._containing_version(revisited)
                        except WorkflowAuthoringError:
                            valid_study = False
                        else:
                            valid_study = (
                                revisited.is_dir()
                                and bool(STUDY_DIRECTORY_PATTERN.fullmatch(revisited.name))
                                and revisited.parent
                                == (revisited_version / "work" / "studies").resolve()
                            )
                        if not valid_study:
                            issues.append(
                                ValidationIssue(
                                    revisited, "revisits must identify an existing study"
                                )
                            )
                        elif revisited == study_path.resolve():
                            issues.append(ValidationIssue(readme, "study cannot revisit itself"))

            registration = study_path / "PREREGISTRATION.json"
            registration_required = status in {
                "preregistered",
                "running",
                "paused",
                "awaiting-review",
                "completed",
            }
            if registration_required:
                if not registration.is_file():
                    issues.append(
                        ValidationIssue(
                            registration, f"{status} study needs preregistration evidence"
                        )
                    )
                else:
                    self._validate_preregistration(registration, metadata, study_path, issues)
            elif registration.exists():
                self._validate_preregistration(registration, metadata, study_path, issues)
            if registration.exists():
                if (
                    not _is_canonical_utc_timestamp(metadata.get("preregistered_at"))
                    or not str(metadata.get("preregistered_by") or "").strip()
                ):
                    issues.append(
                        ValidationIssue(
                            readme, "preregistered study needs approval time and identity"
                        )
                    )
            elif (
                metadata.get("preregistered_at") is not None
                or metadata.get("preregistered_by") is not None
            ):
                issues.append(
                    ValidationIssue(readme, "study without preregistration must not claim approval")
                )

            if status in {"awaiting-review", "completed"} and not _is_substantive(
                study_path / "EVIDENCE.md"
            ):
                issues.append(
                    ValidationIssue(
                        study_path / "EVIDENCE.md",
                        f"{status} study needs completed evidence",
                    )
                )
            if status == "completed" and not _is_substantive(study_path / "CONCLUSION.md"):
                issues.append(
                    ValidationIssue(
                        study_path / "CONCLUSION.md",
                        "completed study needs a completed conclusion",
                    )
                )

            completion = study_path / "COMPLETION.json"
            if status == "completed":
                if not completion.is_file():
                    issues.append(
                        ValidationIssue(completion, "completed study needs completion evidence")
                    )
                else:
                    self._validate_completion(completion, metadata, study_path, issues)
                if route == "study-time-retrospective":
                    self._validate_study_time_terminal(metadata, readme, issues)
            elif completion.exists():
                issues.append(
                    ValidationIssue(completion, "unfinished study must not have COMPLETION.json")
                )

    def _validate_study_time_terminal(
        self,
        metadata: Mapping[str, Any],
        readme: Path,
        issues: list[ValidationIssue],
    ) -> None:
        outcome = metadata.get("outcome")
        disposition = metadata.get("disposition")
        stage = metadata.get("decision_stage")
        valid = False
        if outcome == "pass":
            valid = (
                disposition == "retrospectively-supported" and stage == "retrospective-evaluation"
            )
        elif outcome == "fail":
            valid = (disposition, stage) in {
                ("development-selection-failed", "development"),
                ("retrospective-screen-failed", "retrospective-evaluation"),
            }
        elif outcome == "indeterminate":
            valid = disposition is None and stage in {
                "development",
                "candidate-freeze",
                "retrospective-evaluation",
                "independent-review",
            }
        if not valid:
            issues.append(
                ValidationIssue(
                    readme,
                    "study-time retrospective outcome, disposition, and decision stage conflict",
                )
            )
            return
        try:
            from trading.core.study_terminal_evidence import (
                validate_study_time_terminal_evidence,
            )

            validate_study_time_terminal_evidence(
                study_path=readme.parent,
                outcome=str(outcome),
                disposition=disposition if isinstance(disposition, str) else None,
                decision_stage=str(stage),
            )
        except ValueError as exc:
            issues.append(ValidationIssue(readme.parent / "TERMINAL_EVIDENCE.json", str(exc)))
            return
        terminal_path = readme.parent / "TERMINAL_EVIDENCE.json"
        try:
            terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        references: list[str] = []
        if isinstance(terminal, dict):
            for field in (
                "qualification_evidence",
                "qualification_absence_evidence",
                "challenge_manifest",
                "development_gate",
            ):
                reference = terminal.get(field)
                if isinstance(reference, dict) and isinstance(reference.get("path"), str):
                    references.append(reference["path"])
        challenge_reference = (
            terminal.get("challenge_manifest") if isinstance(terminal, dict) else None
        )
        if isinstance(challenge_reference, dict) and isinstance(
            challenge_reference.get("path"), str
        ):
            challenge_path = self.repo_root / challenge_reference["path"]
            try:
                challenge_manifest = json.loads(challenge_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                challenge_manifest = {}
            gates = (
                challenge_manifest.get("gates") if isinstance(challenge_manifest, dict) else None
            )
            if isinstance(gates, list):
                references.extend(
                    evidence["path"]
                    for gate in gates
                    if isinstance(gate, dict)
                    and isinstance((evidence := gate.get("evidence")), dict)
                    and isinstance(evidence.get("path"), str)
                )
        for reference in references:
            artifact = (self.repo_root / reference).resolve()
            if not self.git_index_checker(artifact):
                issues.append(
                    ValidationIssue(
                        artifact,
                        "terminal study evidence is not in the Git index",
                    )
                )

    def _validate_preregistration(
        self,
        path: Path,
        metadata: Mapping[str, Any],
        study_path: Path,
        issues: list[ValidationIssue],
    ) -> None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(ValidationIssue(path, f"invalid preregistration JSON: {exc}"))
            return
        if not isinstance(payload, dict):
            issues.append(ValidationIssue(path, "preregistration payload must be an object"))
            return
        if payload.get("schema_version") != 1:
            issues.append(ValidationIssue(path, "preregistration schema_version must be 1"))
        relative_study = study_path.resolve().relative_to(self.repo_root.resolve()).as_posix()
        expected = {
            "study_id": metadata.get("id"),
            "workflow": metadata.get("workflow"),
            "workflow_version": metadata.get("workflow_version"),
            "study_path": relative_study,
            "approved_at": metadata.get("preregistered_at"),
            "approved_by": metadata.get("preregistered_by"),
            "revisits": metadata.get("revisits"),
        }
        if "route" in metadata or "route" in payload:
            expected["route"] = metadata.get("route")
        for field, value in expected.items():
            if payload.get(field) != value:
                issues.append(ValidationIssue(path, f"preregistration {field} is inconsistent"))
        digests = {
            "hypothesis_sha256": study_path / "HYPOTHESIS.md",
            "plan_sha256": study_path / "PLAN.md",
        }
        if (study_path / "QUALIFICATION_SPEC.json").is_file():
            digests["qualification_spec_sha256"] = study_path / "QUALIFICATION_SPEC.json"
        for field, artifact in digests.items():
            digest = payload.get(field)
            if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
                issues.append(ValidationIssue(path, f"{field} must be a SHA-256 digest"))
            elif artifact.exists() and digest != _sha256(artifact):
                issues.append(ValidationIssue(artifact, "preregistered content digest has changed"))
        workflow_release = study_path.parents[2] / "RELEASE.json"
        try:
            release_payload = json.loads(workflow_release.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(
                ValidationIssue(workflow_release, f"cannot verify workflow release identity: {exc}")
            )
        else:
            if payload.get("workflow_sha256") != release_payload.get("workflow_sha256"):
                issues.append(
                    ValidationIssue(path, "preregistration workflow digest differs from release")
                )

    def _validate_development_authorization(
        self,
        path: Path,
        metadata: Mapping[str, Any],
        study_path: Path,
        issues: list[ValidationIssue],
    ) -> None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(ValidationIssue(path, f"invalid Development authorization: {exc}"))
            return
        if not isinstance(payload, dict):
            issues.append(ValidationIssue(path, "Development authorization must be an object"))
            return
        relative_study = study_path.resolve().relative_to(self.repo_root.resolve()).as_posix()
        expected = {
            "schema_version": 1,
            "study_path": relative_study,
            "route": metadata.get("route"),
            "preregistration_sha256": _sha256(study_path / "PREREGISTRATION.json"),
        }
        if any(payload.get(field) != value for field, value in expected.items()):
            issues.append(
                ValidationIssue(path, "Development authorization differs from frozen study")
            )
        authorized_at = payload.get("authorized_at")
        if not _is_canonical_utc_timestamp(authorized_at):
            issues.append(ValidationIssue(path, "Development authorization time is invalid"))
        elif isinstance(metadata.get("preregistered_at"), str) and authorized_at < metadata.get(
            "preregistered_at"
        ):
            issues.append(
                ValidationIssue(path, "Development authorization predates preregistration")
            )
        for field in ("approved_by", "authorized_operator", "authorization_scope"):
            if not isinstance(payload.get(field), str) or not str(payload[field]).strip():
                issues.append(ValidationIssue(path, f"Development authorization needs {field}"))
        if payload.get("approved_by") != metadata.get("preregistered_by"):
            issues.append(
                ValidationIssue(
                    path,
                    "Development authorization approver differs from the human owner",
                )
            )

    @staticmethod
    def _validate_guarded_candidate_freeze(
        path: Path,
        study_path: Path,
        issues: list[ValidationIssue],
    ) -> None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("candidate freeze must be an object")
            from trading.core.study_qualification import validate_candidate_freeze_for_study

            validate_candidate_freeze_for_study(study_path, payload)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            issues.append(ValidationIssue(path, f"invalid guarded candidate freeze: {exc}"))

    def _validate_completion(
        self,
        path: Path,
        metadata: Mapping[str, Any],
        study_path: Path,
        issues: list[ValidationIssue],
    ) -> None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(ValidationIssue(path, f"invalid completion JSON: {exc}"))
            return
        if not isinstance(payload, dict):
            issues.append(ValidationIssue(path, "completion payload must be an object"))
            return
        if payload.get("schema_version") != 1:
            issues.append(ValidationIssue(path, "completion schema_version must be 1"))
        relative_study = study_path.resolve().relative_to(self.repo_root.resolve()).as_posix()
        expected = {
            "study_id": metadata.get("id"),
            "workflow": metadata.get("workflow"),
            "workflow_version": metadata.get("workflow_version"),
            "study_path": relative_study,
            "outcome": metadata.get("outcome"),
            "completed_at": metadata.get("completed_at"),
            "reviewed_by": metadata.get("reviewed_by"),
        }
        for field in ("route", "disposition", "decision_stage"):
            if field in metadata or field in payload:
                expected[field] = metadata.get(field)
        for field, value in expected.items():
            if payload.get(field) != value:
                issues.append(ValidationIssue(path, f"completion {field} is inconsistent"))
        digests = {
            "preregistration_sha256": study_path / "PREREGISTRATION.json",
            "evidence_sha256": study_path / "EVIDENCE.md",
            "conclusion_sha256": study_path / "CONCLUSION.md",
        }
        if metadata.get("route") == "study-time-retrospective":
            digests["terminal_evidence_sha256"] = study_path / "TERMINAL_EVIDENCE.json"
        for field, artifact in digests.items():
            digest = payload.get(field)
            if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
                issues.append(ValidationIssue(path, f"{field} must be a SHA-256 digest"))
            elif artifact.exists() and digest != _sha256(artifact):
                issues.append(ValidationIssue(artifact, "completed study artifact has changed"))

    def _release_dependencies(self, raw: Any) -> list[dict[str, str]]:
        if not isinstance(raw, list):
            raise WorkflowAuthoringError("dependencies must be a list")
        result: list[dict[str, str]] = []
        for dependency in raw:
            if not isinstance(dependency, dict):
                raise WorkflowAuthoringError("dependency must be a mapping")
            path_text = dependency.get("path")
            role = dependency.get("role")
            pinned = dependency.get("pinned", False)
            if not isinstance(path_text, str) or role not in {"normative", "reference"}:
                raise WorkflowAuthoringError("dependency needs path and normative/reference role")
            if type(pinned) is not bool or (pinned and role != "reference"):
                raise WorkflowAuthoringError(
                    "dependency pinned flag must be true only for a reference dependency"
                )
            path = self._resolve_repo_reference(path_text)
            if not path.is_file():
                raise WorkflowAuthoringError(f"dependency file does not exist: {path_text}")
            item = {"path": path_text, "role": role}
            if pinned:
                item["pinned"] = True
            if role == "normative" or pinned:
                item["sha256"] = _sha256(path)
            result.append(item)
        return result

    def _render_root_index(self, workflows: Mapping[str, Mapping[str, Any]]) -> str:
        rows = ["| Workflow | Version | Status | Path |", "| --- | --- | --- | --- |"]
        for slug in sorted(workflows):
            family = workflows[slug]
            title = str(family.get("title", slug))
            versions = family.get("versions")
            if not isinstance(versions, Mapping):
                continue
            for version in sorted(versions, key=_version_number):
                record = versions[version]
                if not isinstance(record, Mapping):
                    continue
                path_text = str(record.get("path", ""))
                status = str(record.get("status", ""))
                rows.append(
                    f"| {title} (`{slug}`) | `{version}` | `{status}` | "
                    f"[{path_text}]({path_text}/) |"
                )
        if len(rows) == 2:
            return "_No workflow versions registered._"
        return "\n".join(rows)

    def _render_work_index(
        self,
        version_path: Path,
        *,
        planned_changes: tuple[tuple[str, Mapping[str, Any]], ...] = (),
    ) -> str:
        sections: list[str] = ["### Studies", ""]
        studies = version_path / "work" / "studies"
        study_rows: list[str] = []
        if studies.exists():
            for path in sorted(item for item in studies.iterdir() if item.is_dir()):
                readme = path / "README.md"
                if not readme.exists():
                    continue
                try:
                    metadata = read_markdown_document(readme).metadata
                except WorkflowAuthoringError:
                    continue
                study_rows.append(
                    f"| `{metadata.get('id', '-')}` | {metadata.get('title', path.name)} | "
                    f"`{metadata.get('status', '-')}` | `{metadata.get('outcome') or '-'}` | "
                    f"[{path.name}](work/studies/{path.name}/) |"
                )
        if study_rows:
            sections.extend(
                [
                    "| ID | Title | Status | Outcome | Path |",
                    "| --- | --- | --- | --- | --- |",
                    *study_rows,
                ]
            )
        else:
            sections.append("_No studies._")
        sections.extend(["", "### Changes", ""])
        changes = version_path / "work" / "changes"
        change_rows: list[str] = []
        if changes.exists():
            for path in sorted(item for item in changes.iterdir() if item.is_dir()):
                readme = path / "README.md"
                if not readme.exists():
                    continue
                try:
                    metadata = read_markdown_document(readme).metadata
                except WorkflowAuthoringError:
                    continue
                change_rows.append(
                    f"| `{metadata.get('id', '-')}` | {metadata.get('title', path.name)} | "
                    f"`{metadata.get('status', '-')}` | "
                    f"`{metadata.get('released_in') or '-'}` | "
                    f"[{path.name}](work/changes/{path.name}/) |"
                )
        for name, metadata in planned_changes:
            change_rows.append(
                f"| `{metadata.get('id', '-')}` | {metadata.get('title', name)} | "
                f"`{metadata.get('status', '-')}` | "
                f"`{metadata.get('released_in') or '-'}` | "
                f"[{name}](work/changes/{name}/) |"
            )
        if change_rows:
            sections.extend(
                [
                    "| ID | Title | Status | Released in | Path |",
                    "| --- | --- | --- | --- | --- |",
                    *change_rows,
                ]
            )
        else:
            sections.append("_No changes._")
        return "\n".join(sections)

    def _write_registry(self, metadata: dict[str, Any]) -> None:
        document = read_markdown_document(self.registry_path)
        _atomic_write(
            self.registry_path,
            render_markdown_document(MarkdownDocument(metadata, document.body)),
        )

    def _initial_version_body(self, *, title: str, authoring_basis: str) -> str:
        asset = self._authoring_asset("workflow-version", "README.md")
        body = read_markdown_document(asset).body
        return body.replace("REPLACE_ME_WORKFLOW_TITLE", title).replace(
            "REPLACE_ME_SUMMARIZE_CONFIRMED_DECISIONS_AND_SOURCE",
            authoring_basis,
        )

    @staticmethod
    def _authoring_asset(group: str, filename: str) -> Path:
        return (
            Path(__file__).resolve().parents[3]
            / ".agents"
            / "skills"
            / "trading-author-workflow"
            / "assets"
            / group
            / filename
        )

    def _repo_relative(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.repo_root.resolve()).as_posix()
        except ValueError as exc:
            raise WorkflowAuthoringError(f"path is outside repository root: {path}") from exc

    def _planned_mutation(
        self,
        *,
        action: str,
        path: str,
        content: bytes,
    ) -> WorkflowFileMutation:
        target = self._resolve_repo_reference(path)
        return WorkflowFileMutation(
            action=action,
            path=path,
            content=content,
            before_sha256=_sha256(target) if target.is_file() else None,
        )

    def _registered_version(
        self,
        version_path: Path,
    ) -> tuple[dict[str, Any], str, str, dict[str, Any]]:
        path = self._resolve_input(version_path)
        match = WORKFLOW_DIRECTORY_PATTERN.fullmatch(path.name)
        if not match:
            raise WorkflowAuthoringError(f"invalid workflow version directory: {path}")
        registry = copy.deepcopy(read_markdown_document(self.registry_path).metadata)
        slug = match.group("slug")
        version = match.group("version")
        family = self._family(registry, slug)
        versions = self._versions(family, slug)
        record = versions.get(version)
        if not isinstance(record, dict) or record.get("path") != path.name:
            raise WorkflowAuthoringError(f"workflow version is not registered: {path}")
        return registry, slug, version, record

    @staticmethod
    def _family(registry: Mapping[str, Any], slug: str) -> dict[str, Any]:
        workflows = registry.get("workflows")
        if not isinstance(workflows, dict) or not isinstance(workflows.get(slug), dict):
            raise WorkflowAuthoringError(f"workflow family is not registered: {slug}")
        return workflows[slug]

    @staticmethod
    def _versions(family: Mapping[str, Any], slug: str) -> dict[str, Any]:
        versions = family.get("versions")
        if not isinstance(versions, dict):
            raise WorkflowAuthoringError(f"workflow family has no version registry: {slug}")
        return versions

    def _containing_version(self, path: Path) -> Path:
        resolved_root = self.root.resolve()
        current = path.resolve()
        while current.parent != resolved_root:
            if current == resolved_root or not current.is_relative_to(resolved_root):
                raise WorkflowAuthoringError(f"path is outside workflows root: {path}")
            current = current.parent
        if not WORKFLOW_DIRECTORY_PATTERN.fullmatch(current.name):
            raise WorkflowAuthoringError(f"path is not inside a workflow version: {path}")
        return current

    def _resolve_input(self, path: Path) -> Path:
        if path.is_absolute():
            candidate = path
        else:
            direct = path.resolve()
            candidate = direct if direct.is_relative_to(self.root.resolve()) else self.root / path
        resolved = candidate.resolve()
        root = self.root.resolve()
        if not resolved.is_relative_to(root):
            raise WorkflowAuthoringError(f"path is outside workflows root: {path}")
        return resolved

    def _resolve_repo_reference(self, value: str) -> Path:
        relative = Path(value)
        if relative.is_absolute():
            raise WorkflowAuthoringError(f"repository reference must be relative: {value}")
        resolved_root = self.repo_root.resolve()
        resolved = (self.repo_root / relative).resolve()
        if not resolved.is_relative_to(resolved_root):
            raise WorkflowAuthoringError(f"repository reference escapes root: {value}")
        canonical_root = self.canonical_workflow_root.resolve()
        if resolved.is_relative_to(canonical_root):
            return self.root.resolve() / resolved.relative_to(canonical_root)
        return resolved

    def _current_time(self) -> datetime:
        current = self.now()
        if current.tzinfo is None or current.utcoffset() is None:
            raise WorkflowAuthoringError("workflow clock must be timezone-aware")
        return current.astimezone(UTC)

    def _require_no_blocking_changes(
        self,
        version_path: Path,
        *,
        included_changes: frozenset[Path],
    ) -> None:
        changes_root = version_path / "work" / "changes"
        if not changes_root.exists():
            return
        included = {path.resolve() for path in included_changes}
        for change_path in sorted(path for path in changes_root.iterdir() if path.is_dir()):
            metadata = read_markdown_document(change_path / "README.md").metadata
            status = metadata.get("status")
            if status in {"draft", "proposed"}:
                raise WorkflowAuthoringError(
                    f"resolve {status} change before ending the active version: {change_path}"
                )
            if status == "accepted" and change_path.resolve() not in included:
                raise WorkflowAuthoringError(
                    f"accepted change must be included or otherwise resolved: {change_path}"
                )

    def _require_studies_ready_for_version_end(self, version_path: Path) -> None:
        studies_root = version_path / "work" / "studies"
        if not studies_root.exists():
            return
        allowed = {"paused", "completed", "cancelled"}
        for study_path in sorted(path for path in studies_root.iterdir() if path.is_dir()):
            metadata = read_markdown_document(study_path / "README.md").metadata
            status = metadata.get("status")
            if status not in allowed:
                raise WorkflowAuthoringError(
                    f"resolve {status} study before ending the active version: {study_path}"
                )

    def _require_valid(self) -> None:
        issues = self.validate_all()
        if issues:
            raise WorkflowAuthoringError("; ".join(str(issue) for issue in issues))

    def _require_structurally_valid(
        self,
        *,
        allow_active_dependency_drift_for: tuple[str, str] | None = None,
    ) -> None:
        issues = self.validate_all(
            check_generated=False,
            _allow_active_dependency_drift_for=allow_active_dependency_drift_for,
        )
        if issues:
            raise WorkflowAuthoringError("; ".join(str(issue) for issue in issues))
