"""Typed identities for composable executable research policies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PolicyIdentity:
    """The stable family and immutable version of one policy release."""

    family: str
    version: str


@dataclass(frozen=True)
class PolicyRelease:
    """One verified policy release and its executable configuration."""

    identity: PolicyIdentity
    kind: str
    values: dict[str, Any]
    release_digest: str
    config_digest: str
    path: str
