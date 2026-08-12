"""Semantic research-definition identities and exact source snapshots."""

from __future__ import annotations

import ast
import hashlib
import math
import platform
import subprocess
from collections.abc import Iterable, Mapping
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path

from trading.core.sleeve_engine import (
    DEFAULT_BASE_COST_POLICY,
    DEFAULT_STRESS_COST_POLICY,
    ExecutionCostPolicy,
    validate_cost_scenario_policies,
)
from trading.policies import PolicySet
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

    def __init__(self, root: Path, *, publish: bool = True) -> None:
        self.root = Path(root)
        self.publish = publish

    def definition_blob_path(self, digest: str) -> Path:
        validate_digest(digest)
        return self.root / "definitions" / "sha256" / digest[:2] / f"{digest}.json"

    def capture(
        self,
        *,
        resolved_config: object,
        sources: Mapping[str, Path],
        reporting_only_symbols: Mapping[str, Iterable[str]] | None = None,
        execution_engine_version: str,
        dependency_versions: Mapping[str, str],
        base_cost_policy: ExecutionCostPolicy = DEFAULT_BASE_COST_POLICY,
        stress_cost_policy: ExecutionCostPolicy = DEFAULT_STRESS_COST_POLICY,
        repo_root: Path | None = None,
        policy_set: PolicySet | None = None,
        workflow_native: bool = False,
    ) -> ResearchDefinitionSnapshot:
        """Capture exact source while deriving identity from normalized semantics."""
        if workflow_native and policy_set is None:
            raise ResearchDefinitionError(
                "workflow-native definition capture requires an explicit policy set"
            )
        try:
            validate_cost_scenario_policies(base_cost_policy, stress_cost_policy)
        except ValueError as exc:
            raise ResearchDefinitionError(str(exc)) from exc
        required_roles = {"strategy", "detector", "backtester"}
        if not required_roles.issubset(sources):
            raise ResearchDefinitionError(
                "a research definition requires strategy, detector, and backtester sources"
            )
        reporting_symbols = _validate_reporting_only_symbols(reporting_only_symbols or {}, sources)
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
                _semantic_tree(tree, reporting_symbols.get(role, frozenset())),
                annotate_fields=True,
                include_attributes=False,
            )
            source_paths.append(path)

        canonical_config = _canonical_value(resolved_config)
        runtime = {
            "python": platform.python_version(),
            "dependencies": {key: dependency_versions[key] for key in sorted(dependency_versions)},
        }
        semantic_payload = {
            "schema_version": 2,
            "resolved_config": canonical_config,
            "normalized_python_ast": normalized_sources,
            "execution_engine_version": execution_engine_version,
            "execution_cost_policies": {
                "base": _canonical_value(base_cost_policy),
                "stress": _canonical_value(stress_cost_policy),
            },
            "runtime": runtime,
        }
        policy_references: tuple[dict[str, str], ...] = ()
        if policy_set is not None:
            policy_references = tuple(
                {
                    "family": release.identity.family,
                    "version": release.identity.version,
                    "path": release.path,
                    "release_digest": release.release_digest,
                    "config_digest": release.config_digest,
                }
                for release in sorted(
                    policy_set.releases,
                    key=lambda item: item.identity.family,
                )
            )
            semantic_payload["policy_set"] = {
                "identity": policy_set.identity,
                "policies": policy_references,
            }
        fingerprint = hashlib.sha256(canonical_json_bytes(semantic_payload)).hexdigest()
        git_root = (
            Path(repo_root).resolve() if repo_root is not None else _discover_git_root(source_paths)
        )
        git_context = _git_context(git_root, source_paths)
        exact_payload = {
            **semantic_payload,
            "fingerprint": fingerprint,
            "reporting_only_symbols": {
                role: sorted(names) for role, names in sorted(reporting_symbols.items())
            },
            "sources": exact_sources,
            "git_context": git_context,
        }
        blob_bytes = canonical_json_bytes(exact_payload)
        digest = hashlib.sha256(blob_bytes).hexdigest()
        if self.publish:
            publish_immutable(self.definition_blob_path(digest), blob_bytes, digest)
        reference = DefinitionBlobRef(
            digest=digest,
            byte_count=len(blob_bytes),
            fingerprint=fingerprint,
        )
        return ResearchDefinitionSnapshot(
            fingerprint=fingerprint,
            blob=reference,
            policy_set_identity=policy_set.identity if policy_set is not None else None,
            policies=policy_references,
        )

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


class _ReportingOnlyFilter(ast.NodeTransformer):
    """Exclude explicitly declared reporting helpers from outcome identity."""

    def __init__(self, excluded_names: frozenset[str]) -> None:
        self.excluded_names = excluded_names

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST | None:
        if node.name in self.excluded_names:
            node.body = [ast.copy_location(ast.Pass(), node)]
            return node
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST | None:
        if node.name in self.excluded_names:
            node.body = [ast.copy_location(ast.Pass(), node)]
            return node
        return self.generic_visit(node)


class _DeclaredSymbolReferenceCollector(ast.NodeVisitor):
    """Find declared symbols referenced outside their own function definitions."""

    def __init__(self, declared_names: frozenset[str]) -> None:
        self.declared_names = declared_names
        self.referenced_names: set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name not in self.declared_names:
            self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if node.name not in self.declared_names:
            self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in self.declared_names:
            self.referenced_names.add(node.id)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in self.declared_names:
            self.referenced_names.add(node.attr)
        self.generic_visit(node)


def _semantic_tree(tree: ast.AST, excluded_names: frozenset[str]) -> ast.AST:
    """Normalize behavior while ignoring explicitly declared output-only helpers."""
    definition_counts = {
        name: sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
            for node in ast.walk(tree)
        )
        for name in excluded_names
    }
    unambiguous_names = frozenset(name for name, count in definition_counts.items() if count == 1)
    references = _DeclaredSymbolReferenceCollector(unambiguous_names)
    references.visit(tree)
    safe_exclusions = frozenset() if references.referenced_names else unambiguous_names
    filtered = _ReportingOnlyFilter(safe_exclusions).visit(tree)
    if filtered is None:  # pragma: no cover - a module itself is never filtered
        return ast.Module(body=[], type_ignores=[])
    return ast.fix_missing_locations(filtered)


def _validate_reporting_only_symbols(
    declarations: Mapping[str, Iterable[str]], sources: Mapping[str, Path]
) -> dict[str, frozenset[str]]:
    unknown_roles = set(declarations).difference(sources)
    if unknown_roles:
        roles = ", ".join(sorted(unknown_roles))
        raise ResearchDefinitionError(f"reporting-only symbols reference unknown roles: {roles}")
    validated: dict[str, frozenset[str]] = {}
    for role, names in declarations.items():
        declared_names = tuple(names)
        if any(not isinstance(name, str) or not name for name in declared_names):
            raise ResearchDefinitionError(
                f"reporting-only symbols for {role} must be non-empty strings"
            )
        validated[role] = frozenset(declared_names)
    return validated


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
