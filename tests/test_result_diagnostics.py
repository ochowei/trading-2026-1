import json

import pytest

from trading.core.results import compare_experiments, save_result
from trading.research_data.result_schema import ResultValidityStatus


def _legacy_result(signals: int) -> dict:
    part = {
        "total_signals": signals,
        "win_rate": 0.5,
        "avg_return_pct": 1.0,
        "cumulative_return_pct": 2.0,
        "profit_factor": 1.2,
        "sharpe_ratio": 0.3,
        "sortino_ratio": 0.4,
        "calmar_ratio": 0.2,
    }
    return {"part_a": part, "part_b": part, "part_c": part}


def test_compare_is_read_only_and_displays_legacy_validity(monkeypatch, tmp_path, capsys) -> None:
    results_root = tmp_path / "results"
    for name, signals in (("first", 1), ("second", 2)):
        directory = results_root / name
        directory.mkdir(parents=True)
        (directory / "latest.json").write_text(
            json.dumps(_legacy_result(signals)),
            encoding="utf-8",
        )
    before = {path: path.read_bytes() for path in results_root.glob("*/latest.json")}
    monkeypatch.setattr("trading.core.results.RESULTS_DIR", results_root)

    compare_experiments(["first", "second"])

    output = capsys.readouterr().out
    assert output.count("Validity: legacy") == 2
    assert {path: path.read_bytes() for path in before} == before


def test_legacy_save_does_not_advance_latest(tmp_path, monkeypatch) -> None:
    results_root = tmp_path / "results"
    monkeypatch.setattr("trading.core.results.RESULTS_DIR", results_root)

    saved_path = save_result("experiment", _legacy_result(1))

    assert saved_path.exists()
    assert saved_path.name != "latest.json"
    assert not (results_root / "experiment" / "latest.json").exists()


def test_legacy_result_status_cannot_be_qualified() -> None:
    from trading.research_data.result_schema import classify_result

    status = classify_result(_legacy_result(1))

    assert status.status is ResultValidityStatus.LEGACY
    assert not status.is_qualifiable


@pytest.mark.parametrize("status", ["legacy", "data-stale", "unreproducible"])
def test_non_current_statuses_are_not_qualifiable(status) -> None:
    from trading.research_data.result_schema import ResultValidity

    assert not ResultValidity(
        getattr(ResultValidityStatus, status.replace("-", "_").upper())
    ).is_qualifiable
