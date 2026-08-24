"""Static policy checks for the Phase 9 experiment data-access migration."""

from __future__ import annotations

import ast
import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_ALLOWED_KINDS = {"direct-yfinance", "indirect-datafetcher"}
_DATA_ACCESS_MODULES = {
    "trading.core.data_fetcher",
    "trading.market_data",
    "trading.market_data.cache",
    "trading.market_data.contracts",
    "trading.market_data.provider",
    "trading.market_data.service",
}
_DATA_ACCESS_NAMES = {
    "CsvMarketDataCache",
    "DataFetcher",
    "MarketDataReader",
    "MarketDataService",
    "YahooFinanceProvider",
}


class MarketDataPolicyError(ValueError):
    """A Phase 9 static policy or allowlist contract is invalid."""


@dataclass(frozen=True, slots=True)
class BypassFinding:
    """One canonical experiment data-access bypass finding."""

    kind: str
    path: str
    lines: tuple[int, ...]
    api_forms: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.kind not in _ALLOWED_KINDS:
            raise MarketDataPolicyError(f"unsupported bypass kind: {self.kind}")
        _validate_canonical_path(self.path)


@dataclass(frozen=True, slots=True)
class AllowlistDocument:
    """Validated JSON representation of the temporary migration allowlist."""

    schema_version: int
    baseline_commit: str
    entries: tuple[tuple[str, str], ...]


def scan_experiment_market_data_bypasses(repo_root: Path) -> tuple[BypassFinding, ...]:
    """Find direct and known indirect data-access bypasses under the experiment tree.

    The scanner deliberately returns one finding per ``(kind, path)`` pair.  A finding
    keeps all source lines and API forms so the allowlist identifies a file and a policy
    category, while diagnostics still explain why the file is listed.
    """

    root = repo_root.resolve()
    experiment_roots = (
        root / "src" / "trading" / "experiments",
        root / "legacy" / "experiments",
    )
    missing_roots = tuple(path for path in experiment_roots if not path.is_dir())
    if missing_roots:
        rendered = ", ".join(str(path) for path in missing_roots)
        raise MarketDataPolicyError(f"experiment root does not exist: {rendered}")

    findings: list[BypassFinding] = []
    for experiment_root in experiment_roots:
        for path in sorted(experiment_root.rglob("*.py")):
            findings.extend(_scan_file(path, root))
    return tuple(sorted(findings, key=lambda finding: (finding.kind, finding.path)))


def scan_non_provider_yfinance_bypasses(repo_root: Path) -> tuple[BypassFinding, ...]:
    """Find yfinance access anywhere in ``src/trading`` except the provider boundary."""

    root = repo_root.resolve()
    source_root = root / "src" / "trading"
    if not source_root.is_dir():
        raise MarketDataPolicyError(f"trading source root does not exist: {source_root}")
    allowed_path = "src/trading/market_data/provider.py"
    findings: list[BypassFinding] = []
    for path in sorted(source_root.rglob("*.py")):
        if path.relative_to(root).as_posix() == allowed_path:
            continue
        findings.extend(
            finding for finding in _scan_file(path, root) if finding.kind == "direct-yfinance"
        )
    return tuple(sorted(findings, key=lambda finding: finding.path))


def scan_non_experiment_yfinance_bypasses(repo_root: Path) -> tuple[BypassFinding, ...]:
    """Find yfinance access outside both the provider and temporary legacy experiment tree."""

    findings = scan_non_provider_yfinance_bypasses(repo_root)
    return tuple(
        finding for finding in findings if not finding.path.startswith("src/trading/experiments/")
    )


def canonical_allowlist_entries(
    findings: Iterable[BypassFinding],
) -> tuple[tuple[str, str], ...]:
    """Return sorted, duplicate-free canonical identities for findings."""

    entries = {(finding.kind, finding.path) for finding in findings}
    return tuple(sorted(entries))


def validate_allowlist(
    entries: Iterable[tuple[str, str]],
    findings: Iterable[BypassFinding],
    *,
    repo_root: Path | None = None,
) -> None:
    """Require an allowlist to exactly match current findings.

    Exact equality is intentional: an entry for a migrated file is stale, and a new
    finding without an entry is an unreviewed bypass.  Both states fail closed.
    """

    entry_list = tuple(entries)
    normalized = _validate_entries(entry_list, repo_root=repo_root)
    finding_entries = set(canonical_allowlist_entries(findings))
    stale = normalized - finding_entries
    missing = finding_entries - normalized
    if stale:
        rendered = ", ".join(f"{kind}:{path}" for kind, path in sorted(stale))
        raise MarketDataPolicyError(f"stale allowlist entries: {rendered}")
    if missing:
        rendered = ", ".join(f"{kind}:{path}" for kind, path in sorted(missing))
        raise MarketDataPolicyError(f"missing allowlist entries: {rendered}")


def enforce_monotonic_shrink(
    base_entries: Iterable[tuple[str, str]],
    current_entries: Iterable[tuple[str, str]],
) -> None:
    """Reject any allowlist identity that was added relative to the base revision."""

    base = _validate_entries(tuple(base_entries))
    current = _validate_entries(tuple(current_entries))
    added = current - base
    if added:
        rendered = ", ".join(f"{kind}:{path}" for kind, path in sorted(added))
        raise MarketDataPolicyError(f"allowlist cannot grow: {rendered}")


def load_allowlist(path: Path) -> AllowlistDocument:
    """Load and structurally validate a Phase 9 allowlist JSON document."""

    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise MarketDataPolicyError(f"cannot read allowlist {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise MarketDataPolicyError("allowlist must be a JSON object")
    if payload.get("schema_version") != 1:
        raise MarketDataPolicyError("allowlist schema_version must be 1")
    baseline_commit = payload.get("baseline_commit")
    if not isinstance(baseline_commit, str) or not baseline_commit:
        raise MarketDataPolicyError("allowlist baseline_commit must be non-empty")
    raw_entries = payload.get("entries")
    if not isinstance(raw_entries, list):
        raise MarketDataPolicyError("allowlist entries must be a list")

    entries: list[tuple[str, str]] = []
    for raw_entry in raw_entries:
        if not isinstance(raw_entry, dict):
            raise MarketDataPolicyError("each allowlist entry must be an object")
        kind = raw_entry.get("kind")
        entry_path = raw_entry.get("path")
        if not isinstance(kind, str) or not isinstance(entry_path, str):
            raise MarketDataPolicyError("allowlist entries require string kind and path")
        entries.append((kind, entry_path))
    _validate_entries(tuple(entries))
    return AllowlistDocument(1, baseline_commit, tuple(entries))


def _scan_file(path: Path, repo_root: Path) -> tuple[BypassFinding, ...]:
    try:
        tree = ast.parse(path.read_text(), filename=str(path))
    except (OSError, SyntaxError) as exc:
        raise MarketDataPolicyError(f"cannot scan {path}: {exc}") from exc

    yfinance_modules: set[str] = set()
    yfinance_names: set[str] = set()
    importlib_modules: set[str] = set()
    importlib_names: set[str] = set()
    data_access_modules: set[str] = set()
    data_access_names: set[str] = set()
    direct_forms: dict[str, int] = {}
    indirect_forms: dict[str, int] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local_name = alias.asname or alias.name.split(".")[0]
                if alias.name == "yfinance":
                    yfinance_modules.add(local_name)
                    direct_forms.setdefault("import:yfinance", node.lineno)
                elif alias.name == "importlib":
                    importlib_modules.add(local_name)
                elif alias.name in _DATA_ACCESS_MODULES:
                    data_access_modules.add(local_name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "yfinance" or module.startswith("yfinance."):
                direct_forms.setdefault(f"from:{module}", node.lineno)
                for alias in node.names:
                    yfinance_names.add(alias.asname or alias.name)
            if module == "importlib":
                for alias in node.names:
                    if alias.name == "import_module":
                        importlib_names.add(alias.asname or alias.name)
            if module in _DATA_ACCESS_MODULES:
                for alias in node.names:
                    if alias.name in _DATA_ACCESS_NAMES or (
                        module == "trading.core.data_fetcher" and alias.name == "*"
                    ):
                        data_access_names.add(alias.asname or alias.name)
                        indirect_forms.setdefault(f"from:{alias.name}", node.lineno)
            if module in {"trading.core", "trading.market_data"}:
                for alias in node.names:
                    if alias.name in _DATA_ACCESS_NAMES:
                        data_access_names.add(alias.asname or alias.name)
                        indirect_forms.setdefault(f"from:{alias.name}", node.lineno)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name) and function.id in yfinance_names:
            direct_forms.setdefault(function.id, node.lineno)
        elif isinstance(function, ast.Attribute):
            chain = _attribute_chain(function)
            if chain and chain.split(".", 1)[0] in yfinance_modules:
                direct_forms.setdefault(chain, node.lineno)
            if chain and chain.split(".", 1)[0] in data_access_modules:
                indirect_forms.setdefault(chain, node.lineno)
            if chain and chain.split(".", 1)[0] in data_access_modules:
                if chain.rsplit(".", 1)[-1] in _DATA_ACCESS_NAMES:
                    indirect_forms.setdefault(chain, node.lineno)
        if isinstance(function, ast.Name) and function.id in data_access_names:
            indirect_forms.setdefault(function.id, node.lineno)
        if isinstance(function, ast.Name) and function.id == "__import__":
            if _literal_first_argument(node) == "yfinance":
                direct_forms.setdefault("dynamic:__import__", node.lineno)
        if isinstance(function, ast.Name) and function.id in importlib_names:
            if _literal_first_argument(node) == "yfinance":
                direct_forms.setdefault("dynamic:import_module", node.lineno)
        if isinstance(function, ast.Attribute):
            chain = _attribute_chain(function)
            if chain and chain.split(".", 1)[0] in importlib_modules:
                if chain.rsplit(".", 1)[-1] == "import_module":
                    if _literal_first_argument(node) == "yfinance":
                        direct_forms.setdefault("dynamic:import_module", node.lineno)

    relative_path = path.relative_to(repo_root).as_posix()
    findings: list[BypassFinding] = []
    if direct_forms:
        findings.append(
            BypassFinding(
                "direct-yfinance",
                relative_path,
                tuple(sorted(direct_forms.values())),
                tuple(sorted(direct_forms)),
            )
        )
    if indirect_forms or data_access_names:
        indirect_lines = indirect_forms.values()
        if not indirect_lines:
            indirect_lines = {node.lineno for node in ast.walk(tree) if hasattr(node, "lineno")}
        findings.append(
            BypassFinding(
                "indirect-datafetcher",
                relative_path,
                tuple(sorted(indirect_lines)),
                tuple(sorted(indirect_forms or {"data-access-import": 0})),
            )
        )
    return tuple(findings)


def _attribute_chain(node: ast.Attribute) -> str | None:
    parts: list[str] = []
    current: ast.AST = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if not isinstance(current, ast.Name):
        return None
    parts.append(current.id)
    return ".".join(reversed(parts))


def _literal_first_argument(node: ast.Call) -> Any:
    if not node.args:
        return None
    try:
        return ast.literal_eval(node.args[0])
    except (ValueError, TypeError):
        return None


def _validate_entries(
    entries: tuple[tuple[str, str], ...],
    *,
    repo_root: Path | None = None,
) -> set[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    for entry in entries:
        if not isinstance(entry, tuple) or len(entry) != 2:
            raise MarketDataPolicyError("allowlist entries must be (kind, path) tuples")
        kind, entry_path = entry
        if kind not in _ALLOWED_KINDS:
            raise MarketDataPolicyError(f"unsupported bypass kind: {kind}")
        if not isinstance(entry_path, str):
            raise MarketDataPolicyError("allowlist path must be a string")
        _validate_canonical_path(entry_path)
        if repo_root is not None and not (repo_root / entry_path).is_file():
            raise MarketDataPolicyError(f"allowlist path does not exist: {entry_path}")
        if entry in seen:
            raise MarketDataPolicyError(f"duplicate allowlist entry: {kind}:{entry_path}")
        seen.add(entry)
    return seen


def _validate_canonical_path(entry_path: str) -> None:
    if not entry_path or entry_path.startswith("/") or "\\" in entry_path:
        raise MarketDataPolicyError(f"allowlist path is not canonical: {entry_path}")
    path = Path(entry_path)
    if path.as_posix() != entry_path or ".." in path.parts or "." in path.parts:
        raise MarketDataPolicyError(f"allowlist path is not canonical: {entry_path}")
