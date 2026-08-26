#!/usr/bin/env python3
"""Validate the executable projection of repository path ownership."""

from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path
from typing import Any

ALLOWED_STATUSES = frozenset(
    {
        "active",
        "shared",
        "legacy-compat",
        "legacy-archive",
        "version-pinned",
        "local-only",
    }
)
IGNORED_CHILDREN = frozenset({".DS_Store", "__pycache__"})


class PathOwnershipError(ValueError):
    """Raised when the ownership registry or repository tree violates its contract."""


def load_document(path: Path) -> dict[str, Any]:
    """Load one ownership registry document."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PathOwnershipError(f"cannot load path ownership registry: {exc}") from exc
    if not isinstance(payload, dict):
        raise PathOwnershipError("path ownership registry must be a JSON object")
    return payload


def validate_document(document: dict[str, Any], *, repo_root: Path) -> list[str]:
    """Return every ownership violation in deterministic order."""
    issues: list[str] = []
    if document.get("schema_version") != 1:
        issues.append("schema_version must be 1")

    roots = document.get("coverage_roots")
    rules = document.get("rules")
    if not isinstance(roots, list) or not roots or not all(isinstance(item, str) for item in roots):
        issues.append("coverage_roots must be a non-empty list of strings")
        roots = []
    if len(set(roots)) != len(roots):
        issues.append("coverage_roots must be unique")
    if not isinstance(rules, list) or not rules:
        issues.append("rules must be a non-empty list")
        rules = []

    normalized_rules: list[dict[str, Any]] = []
    seen_patterns: set[str] = set()
    for index, raw_rule in enumerate(rules):
        label = f"rules[{index}]"
        if not isinstance(raw_rule, dict):
            issues.append(f"{label} must be an object")
            continue
        pattern = raw_rule.get("pattern")
        status = raw_rule.get("status")
        owner = raw_rule.get("canonical_owner")
        allows_new_content = raw_rule.get("allows_new_content")
        reason = raw_rule.get("reason")
        required = raw_rule.get("required", True)
        if not isinstance(pattern, str) or not pattern or pattern.startswith("/"):
            issues.append(f"{label}.pattern must be a non-empty repository-relative string")
            continue
        if pattern in seen_patterns:
            issues.append(f"duplicate ownership pattern: {pattern}")
        seen_patterns.add(pattern)
        if status not in ALLOWED_STATUSES:
            issues.append(f"{pattern}: unknown status {status!r}")
        if not isinstance(owner, str) or not owner:
            issues.append(f"{pattern}: canonical_owner must be a non-empty string")
        elif not (repo_root / owner).exists():
            issues.append(f"{pattern}: canonical_owner does not exist: {owner}")
        if type(allows_new_content) is not bool:
            issues.append(f"{pattern}: allows_new_content must be boolean")
        if not isinstance(reason, str) or not reason.strip():
            issues.append(f"{pattern}: reason must be a non-empty string")
        if type(required) is not bool:
            issues.append(f"{pattern}: required must be boolean")
            required = True

        matches = _matches(repo_root, pattern)
        if required and not matches:
            issues.append(f"{pattern}: required pattern matches no path")
        content_guard = raw_rule.get("content_guard")
        if content_guard is not None and content_guard != "closed-children":
            issues.append(f"{pattern}: unsupported content_guard {content_guard!r}")
        if content_guard == "closed-children":
            allowed_children = raw_rule.get("allowed_children")
            if _has_magic(pattern):
                issues.append(f"{pattern}: closed-children requires an exact directory path")
            elif allows_new_content is not False:
                issues.append(f"{pattern}: closed-children requires allows_new_content=false")
            elif not isinstance(allowed_children, list) or not all(
                isinstance(item, str) and item for item in allowed_children
            ):
                issues.append(f"{pattern}: allowed_children must be a list of names")
            else:
                target = repo_root / pattern
                if target.is_dir():
                    actual = sorted(
                        child.name
                        for child in target.iterdir()
                        if child.name not in IGNORED_CHILDREN
                    )
                    expected = sorted(set(allowed_children))
                    if actual != expected:
                        issues.append(
                            f"{pattern}: closed children changed; expected {expected}, got {actual}"
                        )
        normalized_rules.append(raw_rule)

    matched_patterns: dict[str, list[str]] = {}
    for rule in normalized_rules:
        pattern = str(rule["pattern"])
        for match in _matches(repo_root, pattern):
            relative = match.relative_to(repo_root).as_posix()
            matched_patterns.setdefault(relative, []).append(pattern)
    for relative, patterns in matched_patterns.items():
        if len(patterns) > 1:
            issues.append(f"ambiguous ownership for {relative}: {sorted(patterns)}")

    for root_text in roots:
        root = repo_root / root_text
        if not root.is_dir():
            issues.append(f"coverage root does not exist: {root_text}")
            continue
        for child in sorted(root.iterdir()):
            if child.name in IGNORED_CHILDREN:
                continue
            relative = child.relative_to(repo_root).as_posix()
            matches = [
                str(rule["pattern"])
                for rule in normalized_rules
                if fnmatch.fnmatchcase(relative, str(rule.get("pattern", "")))
            ]
            if not matches:
                issues.append(f"unclassified public path: {relative}")
            elif len(matches) > 1:
                issues.append(f"ambiguous ownership for {relative}: {sorted(matches)}")

    return sorted(set(issues))


def _matches(repo_root: Path, pattern: str) -> list[Path]:
    if not _has_magic(pattern):
        path = repo_root / pattern
        return [path] if path.exists() else []
    return sorted(repo_root.glob(pattern))


def _has_magic(pattern: str) -> bool:
    return any(character in pattern for character in "*?[")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).with_name("path-ownership.json"),
    )
    args = parser.parse_args()
    try:
        document = load_document(args.registry)
        issues = validate_document(document, repo_root=args.repo_root.resolve())
    except PathOwnershipError as exc:
        print(f"Path ownership check failed: {exc}")
        return 1
    if issues:
        print("Path ownership check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Path ownership check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
