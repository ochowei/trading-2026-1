"""Fail-closed resolution and composition of released research policies."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import yaml

from trading.core.accounting import canonical_json_bytes
from trading.core.policy_authoring import PolicyRepository
from trading.core.workflow_authoring import read_markdown_document
from trading.policies.models import PolicyIdentity, PolicyRelease

_CONFIG_FIELDS = frozenset({"schema_version", "family", "version", "kind", "values"})


class PolicyResolutionError(ValueError):
    """A requested policy release cannot be verified or composed."""


class PolicyResolver:
    """Resolve exact verified releases without mutable latest-version behavior."""

    def __init__(self, root: Path = Path("policies")) -> None:
        self.root = Path(root)

    def resolve(self, family: str, version: str) -> PolicyRelease:
        """Return one exact active or superseded release after complete verification."""
        issues = PolicyRepository(self.root).validate_all()
        if issues:
            raise PolicyResolutionError(issues[0].message)
        registry = read_markdown_document(self.root / "README.md").metadata
        try:
            record = registry["policies"][family]["versions"][version]
        except (KeyError, TypeError) as exc:
            raise PolicyResolutionError(f"unknown policy release: {family}@{version}") from exc
        if record.get("status") not in {"active", "superseded"}:
            raise PolicyResolutionError(f"policy is not selectable: {family}@{version}")
        version_path = self.root / str(record["path"])
        config_path = version_path / "policy.yaml"
        try:
            raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise PolicyResolutionError(f"cannot read policy config: {exc}") from exc
        if not isinstance(raw, dict):
            raise PolicyResolutionError("policy config must be a mapping")
        unknown = set(raw).difference(_CONFIG_FIELDS)
        if unknown:
            raise PolicyResolutionError(
                f"unknown policy config fields: {', '.join(sorted(map(str, unknown)))}"
            )
        missing = _CONFIG_FIELDS.difference(raw)
        if missing:
            raise PolicyResolutionError(
                f"missing policy config fields: {', '.join(sorted(missing))}"
            )
        if raw["schema_version"] != 1 or raw["family"] != family or raw["version"] != version:
            raise PolicyResolutionError("policy config identity is invalid")
        if not isinstance(raw["kind"], str) or not raw["kind"]:
            raise PolicyResolutionError("policy kind must be a non-empty string")
        if not isinstance(raw["values"], dict):
            raise PolicyResolutionError("policy values must be a mapping")
        return PolicyRelease(
            identity=PolicyIdentity(family=family, version=version),
            kind=raw["kind"],
            values=dict(raw["values"]),
            release_digest=self._sha256(version_path / "RELEASE.json"),
            config_digest=self._sha256(config_path),
            path=str(version_path.relative_to(self.root.parent)),
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class PolicySet:
    """A deterministic composition of one release per policy family."""

    releases: tuple[PolicyRelease, ...]

    def __post_init__(self) -> None:
        families = [release.identity.family for release in self.releases]
        if len(families) != len(set(families)):
            raise PolicyResolutionError("duplicate policy family in policy set")

    @property
    def identity(self) -> str:
        """Return the order-independent identity of this exact policy composition."""
        payload = [
            {
                "family": release.identity.family,
                "version": release.identity.version,
                "release_digest": release.release_digest,
                "config_digest": release.config_digest,
            }
            for release in sorted(self.releases, key=lambda item: item.identity.family)
        ]
        return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
