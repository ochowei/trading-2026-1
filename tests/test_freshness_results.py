import json

from trading.core.freshness import check_freshness


def test_freshness_reports_result_status_without_mutating_results(
    monkeypatch, tmp_path, capsys
) -> None:
    results_root = tmp_path / "results"
    latest = results_root / "experiment" / "latest.json"
    latest.parent.mkdir(parents=True)
    latest.write_text(json.dumps({"part_a": {}, "part_b": {}, "part_c": {}}), encoding="utf-8")
    before = latest.read_bytes()
    monkeypatch.setattr("trading.core.freshness.RESULTS_DIR", results_root)
    monkeypatch.setattr("trading.core.freshness.LESSONS_PATH", tmp_path / "lessons.md")
    monkeypatch.setattr("trading.core.freshness.DOCS_DIR", tmp_path / "docs")

    check_freshness()

    output = capsys.readouterr().out
    assert "Result validity" in output
    assert "legacy" in output
    assert latest.read_bytes() == before
