"""Read-only freshness audit for archived experiment knowledge and results."""

import re
from datetime import date
from pathlib import Path

from trading.legacy.definition_resolver import resolve_current_definition_fingerprint
from trading.legacy.results import inspect_result

OVERVIEWS_DIR = Path("legacy/experiment-overviews")
ARCHIVED_RESULTS_DIR = Path("legacy/results")

THRESHOLD_GREEN = 3
THRESHOLD_YELLOW = 6


def _months_between(earlier: date, later: date) -> float:
    return (
        (later.year - earlier.year) * 12
        + (later.month - earlier.month)
        + (later.day - earlier.day) / 30
    )


def _status(months_ago: float) -> tuple[str, str]:
    if months_ago <= THRESHOLD_GREEN:
        return "✅", "green"
    if months_ago <= THRESHOLD_YELLOW:
        return "⚠️", "yellow"
    return "🔴", "red"


def _status_label(months_ago: float) -> str:
    if months_ago < 1:
        return "< 1 month ago"
    return f"{months_ago:.0f} months ago"


def _parse_experiment_context(filepath: Path) -> dict[str, str | None] | None:
    """Parse freshness metadata from one archived ``EXPERIMENTS_*.md`` file."""
    content = filepath.read_text(encoding="utf-8")
    context = re.search(r"<!--\s*AI_CONTEXT_START[^>]*?-->", content, re.DOTALL)
    if not context:
        return None
    metadata: dict[str, str] = {}
    for raw_line in context.group(0).splitlines():
        line = raw_line.strip()
        if ":" not in line or line.startswith("<!--"):
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in {"last_validated", "data_through"}:
            metadata[key] = value.strip().removesuffix("-->").strip()
    if not metadata:
        return None
    return {
        "last_validated": metadata.get("last_validated"),
        "data_through": metadata.get("data_through"),
    }


def check_legacy_freshness(
    *,
    overviews_dir: Path = OVERVIEWS_DIR,
    archive_dir: Path = ARCHIVED_RESULTS_DIR,
    today: date | None = None,
) -> dict[str, int]:
    """Print a read-only audit of archived overviews and retained latest results."""
    current_date = today or date.today()
    counts = {"green": 0, "yellow": 0, "red": 0, "unknown": 0}

    print("\n" + "=" * 70)
    print("  Legacy Archive Freshness")
    print("=" * 70)

    for overview in sorted(overviews_dir.glob("EXPERIMENTS_*.md")):
        print(f"\n📄 {overview}")
        context = _parse_experiment_context(overview)
        data_through = context.get("data_through") if context else None
        validated = context.get("last_validated") if context else None
        if not data_through:
            counts["unknown"] += 1
            print("  ❓ AI Context (no data_through date)")
            continue
        try:
            months = _months_between(date.fromisoformat(data_through), current_date)
        except ValueError:
            counts["unknown"] += 1
            print(f"  ❓ AI Context (invalid date: {data_through})")
            continue
        icon, bucket = _status(months)
        counts[bucket] += 1
        validated_text = f", validated {validated}" if validated else ""
        print(
            f"  {icon} AI Context (data through {data_through}, "
            f"{_status_label(months)}{validated_text})"
        )

    print("\n📊 Archived result validity (read-only)")
    if archive_dir.exists():
        for result_dir in sorted(archive_dir.iterdir()):
            if not result_dir.is_dir() or not (result_dir / "latest.json").exists():
                continue
            record = inspect_result(
                result_dir.name,
                archive_dir=archive_dir,
                allow_archive=True,
                current_definition_fingerprint=resolve_current_definition_fingerprint(
                    result_dir.name
                ),
            )
            if record is None:
                continue
            print(f"  {record.experiment_name}: {record.validity.status.value}")
            for reason in record.validity.reasons:
                print(f"    reason: {reason}")
    else:
        print("  (no archived results found)")

    total = sum(counts.values())
    print(
        f"\nLegacy summary: {counts['green']} ✅  {counts['yellow']} ⚠️  "
        f"{counts['red']} 🔴  {counts['unknown']} ❓  (total: {total})"
    )
    print("=" * 70 + "\n")
    return counts
