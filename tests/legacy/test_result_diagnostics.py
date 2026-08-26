import json

import pytest

from trading.legacy.results import (
    LegacyExperimentRetiredError,
    ResultSource,
    compare_experiments,
    inspect_result,
    latest_result_names,
    save_result,
)
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
    monkeypatch.setattr("trading.legacy.results.RESULTS_DIR", results_root)

    compare_experiments(["first", "second"])

    output = capsys.readouterr().out
    assert output.count("Validity: legacy") == 2
    assert {path: path.read_bytes() for path in before} == before


def test_archive_fallback_is_explicit_and_reports_its_source(tmp_path) -> None:
    results_root = tmp_path / "results"
    archive_root = tmp_path / "legacy" / "results"
    latest = archive_root / "experiment" / "latest.json"
    latest.parent.mkdir(parents=True)
    latest.write_text(json.dumps(_legacy_result(1)), encoding="utf-8")

    assert (
        inspect_result(
            "experiment",
            results_dir=results_root,
            archive_dir=archive_root,
        )
        is None
    )

    record = inspect_result(
        "experiment",
        results_dir=results_root,
        archive_dir=archive_root,
        allow_archive=True,
    )

    assert record is not None
    assert record.path == latest
    assert record.source is ResultSource.LEGACY_ARCHIVE


def test_diagnostic_archive_fallback_prefers_canonical_and_warns(tmp_path, caplog) -> None:
    results_root = tmp_path / "results"
    archive_root = tmp_path / "legacy" / "results"
    canonical = results_root / "experiment" / "latest.json"
    archived = archive_root / "experiment" / "latest.json"
    canonical.parent.mkdir(parents=True)
    archived.parent.mkdir(parents=True)
    canonical.write_text(json.dumps(_legacy_result(2)), encoding="utf-8")
    archived.write_text(json.dumps(_legacy_result(1)), encoding="utf-8")

    record = inspect_result(
        "experiment",
        results_dir=results_root,
        archive_dir=archive_root,
        allow_archive=True,
    )

    assert record is not None
    assert record.path == canonical
    assert record.source is ResultSource.CANONICAL
    assert "duplicate latest result" in caplog.text


def test_compare_and_status_inventory_can_read_archive(tmp_path, capsys) -> None:
    results_root = tmp_path / "results"
    archive_root = tmp_path / "legacy" / "results"
    for name, signals in (("first", 1), ("second", 2)):
        latest = archive_root / name / "latest.json"
        latest.parent.mkdir(parents=True)
        latest.write_text(json.dumps(_legacy_result(signals)), encoding="utf-8")

    assert latest_result_names(
        results_dir=results_root,
        archive_dir=archive_root,
        include_archive=True,
    ) == ("first", "second")

    compare_experiments(
        ["first", "second"],
        results_dir=results_root,
        archive_dir=archive_root,
        definition_resolver=lambda _name: None,
    )

    assert capsys.readouterr().out.count("Validity: legacy [legacy archive]") == 2


def test_legacy_save_is_rejected_after_retirement(tmp_path, monkeypatch) -> None:
    results_root = tmp_path / "results"
    archive_root = tmp_path / "legacy" / "results"
    monkeypatch.setattr("trading.legacy.results.RESULTS_DIR", results_root)
    monkeypatch.setattr("trading.legacy.results.ARCHIVED_RESULTS_DIR", archive_root)

    with pytest.raises(LegacyExperimentRetiredError, match="publication is retired"):
        save_result("experiment", _legacy_result(1))

    assert not (results_root / "experiment" / "latest.json").exists()
    assert not archive_root.exists()


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
