"""Persisted-result access, validity diagnostics, and read-only comparison."""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from trading.core.definition_resolver import resolve_current_definition_fingerprint
from trading.research_data.models import DefinitionBlobRef
from trading.research_data.result_schema import (
    ResearchResult,
    ResultSchemaError,
    ResultValidity,
    ResultValidityStatus,
    load_result,
)
from trading.research_data.store import ResearchDataStore

logger = logging.getLogger(__name__)

RESULTS_DIR = Path("results")
ARCHIVED_RESULTS_DIR = Path("legacy/results")


class ResultSource(StrEnum):
    """Physical source of one persisted latest-result view."""

    CANONICAL = "canonical"
    LEGACY_ARCHIVE = "legacy archive"


@dataclass(frozen=True, slots=True)
class ResultStatusRecord:
    """One latest result and its read-only validity view."""

    experiment_name: str
    path: Path
    result: ResearchResult
    source: ResultSource

    @property
    def validity(self) -> ResultValidity:
        return self.result.validity


def save_result(experiment_name: str, result: dict) -> Path:
    """Persist an explicitly legacy run as historical evidence only.

    The legacy compatibility path deliberately never advances ``latest.json``. Only the
    Phase 2/3 coordinator can publish a current latest result.
    """
    directory = RESULTS_DIR / experiment_name
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
    path = directory / f"legacy_{timestamp}_{uuid.uuid4().hex}.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info("[Results] legacy result saved to %s", path)
    return path


def load_latest(experiment_name: str) -> dict | None:
    """Load the unmodified latest JSON for backward-compatible callers."""
    path = RESULTS_DIR / experiment_name / "latest.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def latest_result_names(
    *,
    results_dir: Path | None = None,
    archive_dir: Path | None = None,
    include_archive: bool = False,
) -> tuple[str, ...]:
    """List identities with a latest result in the requested read-only roots."""

    roots = [Path(results_dir or RESULTS_DIR)]
    if include_archive:
        roots.append(Path(archive_dir or ARCHIVED_RESULTS_DIR))
    names: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        names.update(
            path.name
            for path in root.iterdir()
            if path.is_dir() and (path / "latest.json").exists()
        )
    return tuple(sorted(names))


def _resolve_latest_result_path(
    experiment_name: str,
    *,
    results_dir: Path | None,
    archive_dir: Path | None,
    allow_archive: bool,
) -> tuple[Path, ResultSource] | None:
    canonical = Path(results_dir or RESULTS_DIR) / experiment_name / "latest.json"
    if not allow_archive:
        return (canonical, ResultSource.CANONICAL) if canonical.exists() else None

    archived = Path(archive_dir or ARCHIVED_RESULTS_DIR) / experiment_name / "latest.json"
    if canonical.exists():
        if archived.exists():
            logger.warning(
                "duplicate latest result for %s; using canonical %s instead of archive %s",
                experiment_name,
                canonical,
                archived,
            )
        return canonical, ResultSource.CANONICAL
    if archived.exists():
        return archived, ResultSource.LEGACY_ARCHIVE
    return None


def inspect_result(
    experiment_name: str,
    *,
    results_dir: Path | None = None,
    archive_dir: Path | None = None,
    allow_archive: bool = False,
    store: ResearchDataStore | None = None,
    current_definition_fingerprint: str | DefinitionBlobRef | None = None,
    now: datetime | None = None,
) -> ResultStatusRecord | None:
    """Inspect one latest result; archive fallback must be explicitly diagnostic-only."""
    resolved = _resolve_latest_result_path(
        experiment_name,
        results_dir=results_dir,
        archive_dir=archive_dir,
        allow_archive=allow_archive,
    )
    if resolved is None:
        return None
    path, source = resolved
    try:
        result = load_result(
            path,
            store=store or ResearchDataStore(Path(".research-data/blobs")),
            current_definition_fingerprint=current_definition_fingerprint,
            now=now,
        )
    except ResultSchemaError as exc:
        result = ResearchResult(
            payload={},
            validity=ResultValidity(ResultValidityStatus.UNREPRODUCIBLE, (str(exc),)),
        )
    return ResultStatusRecord(
        experiment_name=experiment_name,
        path=path,
        result=result,
        source=source,
    )


def compare_experiments(
    names: list[str],
    *,
    results_dir: Path | None = None,
    archive_dir: Path | None = None,
    store: ResearchDataStore | None = None,
    definition_resolver: Callable[[str], str | DefinitionBlobRef | None] | None = None,
    now: datetime | None = None,
) -> None:
    """Compare latest results while displaying validity and never refreshing them."""
    separator = "=" * 80
    thin_sep = "-" * 80

    from trading.experiments import get_experiment

    current_definition_resolver = definition_resolver or resolve_current_definition_fingerprint

    loaded: dict[str, ResultStatusRecord] = {}
    display_ids: dict[str, str] = {}
    for name in names:
        current_definition = current_definition_resolver(name)
        record = inspect_result(
            name,
            results_dir=results_dir or RESULTS_DIR,
            archive_dir=archive_dir or ARCHIVED_RESULTS_DIR,
            allow_archive=True,
            store=store,
            current_definition_fingerprint=current_definition,
            now=now,
        )
        if record is None:
            print(f"  警告: {name} 無結果可載入 (Warning: no results for {name})")
            continue
        loaded[name] = record
        source = f" [{record.source.value}]" if record.source is ResultSource.LEGACY_ARCHIVE else ""
        print(f"  {name}: Validity: {record.validity.status.value}{source}")
        for reason in record.validity.reasons:
            print(f"    reason: {reason}")
        try:
            strategy = get_experiment(name)
            config = strategy.create_config()
            display_ids[name] = config.experiment_id or name[:12]
        except KeyError:
            display_ids[name] = name[:12]

    if len(loaded) < 2:
        print("  需要至少兩個實驗結果才能比較 (Need at least 2 experiment results to compare)")
        return

    print(f"\n{separator}")
    print("  跨實驗績效比較 (Cross-Experiment Performance Comparison)")
    print(f"{separator}")

    for part_key, part_label in [
        ("part_a", "Part A (In-Sample)"),
        ("part_b", "Part B (Out-of-Sample)"),
        ("part_c", "Part C (Live)"),
    ]:
        print(f"\n  {part_label}")
        print(f"  {thin_sep}")

        header = f"  {'Metric':<36}"
        for name in loaded:
            header += f" {display_ids.get(name, name[:12]):>12}"
        print(header)
        print(f"  {'-' * 72}")

        rows = [
            ("Total signals", "total_signals", "d"),
            ("Win rate", "win_rate", ".1%"),
            ("Avg return %", "avg_return_pct", ".2f"),
            ("Cumulative %", "cumulative_return_pct", ".2f"),
            ("Profit factor", "profit_factor", ".2f"),
            ("Sharpe ratio", "sharpe_ratio", ".2f"),
            ("Sortino ratio", "sortino_ratio", ".2f"),
            ("Calmar ratio", "calmar_ratio", ".2f"),
        ]

        for label, key, fmt in rows:
            line = f"  {label:<36}"
            for record in loaded.values():
                part = record.result.payload.get(part_key, {})
                value = part.get(key, 0) if isinstance(part, dict) else 0
                line += f" {f'{value:{fmt}}':>12}"
            print(line)

    print()
