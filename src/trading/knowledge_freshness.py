"""Freshness reporting for active shared knowledge plus the legacy archive."""

import re
from datetime import date
from pathlib import Path

from trading.legacy.freshness import check_legacy_freshness

LESSONS_PATH = Path(".agents/context/cross_asset_lessons.md")
THRESHOLD_GREEN = 3
THRESHOLD_YELLOW = 6


def _months_between(earlier: date, later: date) -> float:
    return (
        (later.year - earlier.year) * 12
        + (later.month - earlier.month)
        + (later.day - earlier.day) / 30
    )


def _parse_freshness_blocks(content: str) -> list[dict[str, str | None]]:
    lessons: list[dict[str, str | None]] = []
    sections = list(re.finditer(r"^## (\d+)\.\s+(.+)$", content, re.MULTILINE))
    freshness_pattern = re.compile(r"<!--\s*freshness:\s*(.*?)-->", re.DOTALL)
    for index, match in enumerate(sections):
        end = sections[index + 1].start() if index + 1 < len(sections) else len(content)
        freshness = freshness_pattern.search(content[match.end() : end])
        metadata: dict[str, str] = {}
        if freshness:
            for raw_line in freshness.group(1).strip().splitlines():
                line = raw_line.strip()
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
        lessons.append(
            {
                "num": match.group(1),
                "title": match.group(2).strip(),
                "data_through": metadata.get("data_through"),
                "confidence": metadata.get("confidence"),
            }
        )
    return lessons


def check_active_knowledge_freshness(
    *, lessons_path: Path = LESSONS_PATH, today: date | None = None
) -> dict[str, int]:
    """Print freshness for current cross-asset knowledge."""
    current_date = today or date.today()
    counts = {"green": 0, "yellow": 0, "red": 0, "unknown": 0}
    print("\n" + "=" * 70)
    print("  Active Knowledge Freshness")
    print("=" * 70)
    print(f"\n📄 {lessons_path}")
    if not lessons_path.exists():
        print("  (檔案不存在)")
        return counts
    lessons = _parse_freshness_blocks(lessons_path.read_text(encoding="utf-8"))
    for lesson in lessons:
        data_through = lesson["data_through"]
        if not data_through:
            counts["unknown"] += 1
            print(f"  ❓ {lesson['num']}. {lesson['title']} (no freshness metadata)")
            continue
        try:
            months = _months_between(date.fromisoformat(data_through), current_date)
        except ValueError:
            counts["unknown"] += 1
            print(f"  ❓ {lesson['num']}. {lesson['title']} (invalid date: {data_through})")
            continue
        if months <= THRESHOLD_GREEN:
            icon, bucket = "✅", "green"
        elif months <= THRESHOLD_YELLOW:
            icon, bucket = "⚠️", "yellow"
        else:
            icon, bucket = "🔴", "red"
        counts[bucket] += 1
        confidence = f", confidence: {lesson['confidence']}" if lesson["confidence"] else ""
        age = "< 1 month ago" if months < 1 else f"{months:.0f} months ago"
        print(
            f"  {icon} {lesson['num']}. {lesson['title']} "
            f"(data through {data_through}, {age}{confidence})"
        )
    total = sum(counts.values())
    print(
        f"\nActive summary: {counts['green']} ✅  {counts['yellow']} ⚠️  "
        f"{counts['red']} 🔴  {counts['unknown']} ❓  (total: {total})"
    )
    print("=" * 70 + "\n")
    return counts


def check_freshness() -> None:
    """Preserve the aggregate legacy CLI report with explicit responsibility labels."""
    check_active_knowledge_freshness()
    check_legacy_freshness()
