import json
from datetime import date

from trading.knowledge_freshness import check_active_knowledge_freshness
from trading.legacy.freshness import check_legacy_freshness


def test_legacy_freshness_reads_archive_without_mutating_results(tmp_path, capsys) -> None:
    archive_root = tmp_path / "legacy-results"
    latest = archive_root / "experiment" / "latest.json"
    latest.parent.mkdir(parents=True)
    latest.write_text(json.dumps({"part_a": {}, "part_b": {}, "part_c": {}}), encoding="utf-8")
    before = latest.read_bytes()

    check_legacy_freshness(
        overviews_dir=tmp_path / "overviews",
        archive_dir=archive_root,
        today=date(2026, 8, 26),
    )

    output = capsys.readouterr().out
    assert "Legacy Archive Freshness" in output
    assert "Archived result validity" in output
    assert "experiment: legacy" in output
    assert latest.read_bytes() == before


def test_active_freshness_does_not_scan_legacy_archive(tmp_path, capsys) -> None:
    lessons = tmp_path / "cross_asset_lessons.md"
    lessons.write_text(
        """# Lessons

## 1. Current lesson
<!-- freshness:
validated: 2026-08-20
data_through: 2026-08-20
confidence: high
-->
""",
        encoding="utf-8",
    )

    check_active_knowledge_freshness(lessons_path=lessons, today=date(2026, 8, 26))

    output = capsys.readouterr().out
    assert "Active Knowledge Freshness" in output
    assert "Current lesson" in output
    assert "Legacy Archive" not in output
