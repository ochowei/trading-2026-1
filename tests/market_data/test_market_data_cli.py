from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from trading.cli import build_parser, main


class FakeInspection:
    state = "valid"
    errors = ()

    class metadata:
        data_cutoff = date(2026, 8, 4)
        last_incremental_refresh = None
        last_complete_refresh = None
        checksum = "a" * 64


class FakeDataService:
    def __init__(self):
        self.status_calls = []
        self.refresh_calls = []

    def status(self, series):
        self.status_calls.append(series)
        return FakeInspection()

    def refresh(self, series, *, mode, start, end):
        self.refresh_calls.append((series, mode, start, end))
        return pd.DataFrame(index=pd.to_datetime(["2026-08-04"]))


class FakeResearchDataStore:
    def __init__(self):
        self.created = []
        self.written = []

    def create_snapshot(self, cache, requirements, decision_time, *, definition=None):
        self.created.append((cache, tuple(requirements), decision_time, definition))
        return SimpleNamespace(snapshot_id="a" * 64, data=tuple(requirements), definition=None)

    def write_manifest(self, manifest, path):
        self.written.append((manifest, path))
        return path


class FakeGarbageCollectionStore:
    def __init__(self):
        self.calls = []

    def collect_garbage(self, *, manifest_roots, grace_period, apply):
        self.calls.append((tuple(manifest_roots), grace_period, apply))
        return SimpleNamespace(candidates=(), deleted=(), protected=())


def test_data_cli_parser_exposes_status_and_refresh() -> None:
    status = build_parser().parse_args(["data", "status", "SPY"])
    refresh = build_parser().parse_args(
        ["data", "refresh", "^VIX", "--full", "--end", "2026-08-04"]
    )

    assert (status.command, status.data_command, status.symbol) == ("data", "status", "SPY")
    assert refresh.full is True
    assert refresh.start is None
    assert refresh.end == date(2026, 8, 4)


def test_data_status_is_diagnostic_only(monkeypatch, capsys) -> None:
    service = FakeDataService()
    monkeypatch.setattr("trading.cli.create_default_market_data_service", lambda: service)

    main(["data", "status", "SPY"])

    assert [item.symbol for item in service.status_calls] == ["SPY"]
    assert service.refresh_calls == []
    output = capsys.readouterr().out
    assert "SPY" in output
    assert "valid" in output
    assert "2026-08-04" in output


def test_data_refresh_is_explicit_and_reports_published_cutoff(monkeypatch, capsys) -> None:
    service = FakeDataService()
    monkeypatch.setattr("trading.cli.create_default_market_data_service", lambda: service)

    main(["data", "refresh", "SPY", "--full"])

    series, mode, start, end = service.refresh_calls[0]
    assert series.symbol == "SPY"
    assert mode == "full"
    assert start is None
    assert end is None
    assert "full refresh published" in capsys.readouterr().out


def test_data_full_refresh_rejects_partial_history_start(monkeypatch) -> None:
    service = FakeDataService()
    monkeypatch.setattr("trading.cli.create_default_market_data_service", lambda: service)

    with pytest.raises(SystemExit, match="full refresh always downloads complete history"):
        main(["data", "refresh", "SPY", "--full", "--start", "2020-01-01"])

    assert service.refresh_calls == []


def test_data_snapshot_cli_full_refreshes_declared_series_and_writes_manifest(
    monkeypatch, capsys, tmp_path
) -> None:
    service = FakeDataService()
    service.cache = object()
    store = FakeResearchDataStore()
    monkeypatch.setattr("trading.cli.create_default_market_data_service", lambda: service)
    monkeypatch.setattr("trading.cli.create_default_research_data_store", lambda: store)
    manifest_path = tmp_path / "snapshot.json"

    main(
        [
            "data",
            "snapshot",
            "SPY",
            "--aux",
            "^VIX",
            "--history-start",
            "2020-01-01",
            "--decision",
            "2026-08-04",
            "--manifest",
            str(manifest_path),
        ]
    )

    assert [call[0].symbol for call in service.refresh_calls] == ["SPY", "^VIX"]
    assert all(call[1:] == ("full", None, date(2026, 8, 4)) for call in service.refresh_calls)
    _, requirements, decision_time, definition = store.created[0]
    assert [(item.series.symbol, item.role) for item in requirements] == [
        ("SPY", "primary"),
        ("^VIX", "auxiliary"),
    ]
    assert requirements[1].availability_policy.publication_lag_sessions == 1
    assert decision_time.session == date(2026, 8, 4)
    assert definition is None
    assert store.written[0][1] == manifest_path
    assert "a" * 64 in capsys.readouterr().out


def test_data_snapshot_cli_rejects_formal_legacy_experiment() -> None:
    with pytest.raises(SystemExit, match="legacy experiment research is retired"):
        main(
            [
                "data",
                "snapshot",
                "SPY",
                "--experiment",
                "experiment",
                "--history-start",
                "2020-01-01",
                "--decision",
                "2026-08-04",
            ]
        )


def test_data_snapshot_cli_rejects_legacy_experiment_before_active_data_access(
    monkeypatch,
) -> None:
    def unexpected_service_access():
        raise AssertionError("retired experiment snapshot must fail before active data access")

    monkeypatch.setattr(
        "trading.cli.create_default_market_data_service",
        unexpected_service_access,
    )

    with pytest.raises(SystemExit, match="legacy experiment research is retired"):
        main(
            [
                "data",
                "snapshot",
                "SPY",
                "--experiment",
                "experiment",
                "--history-start",
                "2010-01-01",
                "--decision",
                "2026-08-04",
            ]
        )


def test_data_reproducibility_cli_exposes_verify_export_import_and_safe_gc(tmp_path) -> None:
    parser = build_parser()

    verify = parser.parse_args(["data", "verify", str(tmp_path / "snapshot.json")])
    export = parser.parse_args(
        [
            "data",
            "export",
            str(tmp_path / "snapshot.json"),
            str(tmp_path / "bundle.zip"),
        ]
    )
    imported = parser.parse_args(
        [
            "data",
            "import",
            str(tmp_path / "bundle.zip"),
            "--manifest",
            str(tmp_path / "imported.json"),
        ]
    )
    gc = parser.parse_args(
        [
            "data",
            "gc",
            "--manifest-root",
            str(tmp_path / "retained-results"),
            "--grace-days",
            "14",
        ]
    )

    assert verify.data_command == "verify"
    assert export.data_command == "export"
    assert imported.data_command == "import"
    assert gc.data_command == "gc"
    assert gc.apply is False
    assert gc.grace_days == 14
    assert gc.manifest_roots == [tmp_path / "retained-results"]


def test_data_gc_discovers_retained_manifests_from_results_by_default(
    monkeypatch,
) -> None:
    store = FakeGarbageCollectionStore()
    monkeypatch.setattr("trading.cli.create_default_research_data_store", lambda: store)

    main(["data", "gc"])

    manifest_roots, grace_period, apply = store.calls[0]
    assert manifest_roots == (Path("results"),)
    assert grace_period.days == 7
    assert apply is False


def test_data_gc_additional_manifest_root_keeps_default_results_protected(
    monkeypatch,
    tmp_path,
) -> None:
    store = FakeGarbageCollectionStore()
    monkeypatch.setattr("trading.cli.create_default_research_data_store", lambda: store)
    archive_root = tmp_path / "archive"

    main(["data", "gc", "--manifest-root", str(archive_root)])

    manifest_roots, _, _ = store.calls[0]
    assert manifest_roots == (Path("results"), archive_root)
