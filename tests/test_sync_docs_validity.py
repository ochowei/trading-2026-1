import json

import pytest

from trading.core.sync_docs import ResultSyncError, compare_docs_and_results


def test_sync_docs_rejects_legacy_result_source_without_mutating_it(monkeypatch, tmp_path) -> None:
    results_root = tmp_path / "results"
    experiment_dir = results_root / "spy_001"
    experiment_dir.mkdir(parents=True)
    result = {
        "part_a": {"total_signals": 1, "win_rate": 1.0},
        "part_b": {},
        "part_c": {},
    }
    latest = experiment_dir / "latest.json"
    latest.write_text(json.dumps(result), encoding="utf-8")
    before = latest.read_bytes()

    docs_root = tmp_path / "docs"
    docs_root.mkdir()
    (docs_root / "EXPERIMENTS_SPY.md").write_text(
        "### Part A\n\n| ID | 訊號數 |\n|---|---|\n| SPY-001 | 1 |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("trading.core.sync_docs.RESULTS_DIR", results_root)
    monkeypatch.setattr("trading.core.sync_docs.DOCS_DIR", docs_root)

    with pytest.raises(ResultSyncError, match="legacy"):
        compare_docs_and_results()

    assert latest.read_bytes() == before
