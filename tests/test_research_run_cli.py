import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from trading.cli import build_parser, main
from trading.market_data import PrimaryUSSessionCalendar, SignalDecisionTime
from trading.research_data import (
    DefinitionBlobRef,
    ExperimentTrialDeclaration,
    ResearchDefinitionSnapshot,
    RunMode,
    SnapshotManifest,
)


class FakeStrategy:
    def run(self):
        return {"metrics": {"return": 0.1}}


class FakeSnapshotAwareStrategy:
    def run_with_bundle(self, bundle):
        return {"metrics": {"return": 0.1}}

    def capture_research_definition(self, store):
        blob = DefinitionBlobRef(
            digest="a" * 64,
            byte_count=100,
            fingerprint="b" * 64,
        )
        return ResearchDefinitionSnapshot(fingerprint=blob.fingerprint, blob=blob)

    def declare_experiment_trial(self):
        return ExperimentTrialDeclaration(
            family="spy-momentum",
            hypothesis="momentum persists",
        )


def test_run_cli_exposes_offline_and_ephemeral_as_mutually_exclusive_modes(
    monkeypatch, tmp_path
) -> None:
    parser = build_parser()
    offline = parser.parse_args(["run", "experiment", "--offline", str(tmp_path / "snapshot.json")])
    ephemeral = parser.parse_args(["run", "experiment", "--ephemeral"])

    assert offline.offline == Path(tmp_path / "snapshot.json")
    assert offline.ephemeral is False
    assert ephemeral.ephemeral is True
    assert ephemeral.offline is None

    saved = []
    monkeypatch.setattr("trading.cli.get_experiment", lambda name: FakeStrategy())
    monkeypatch.setattr(
        "trading.cli.save_result", lambda name, result: saved.append((name, result))
    )

    main(["run", "experiment", "--ephemeral"])

    assert saved == []


def test_default_persisted_cli_run_requires_formal_snapshot_or_explicit_legacy(
    monkeypatch,
) -> None:
    saved = []
    monkeypatch.setattr("trading.cli.get_experiment", lambda name: FakeStrategy())
    monkeypatch.setattr(
        "trading.cli.save_result", lambda name, result: saved.append((name, result))
    )

    with pytest.raises(SystemExit, match="--snapshot.*--legacy"):
        main(["run", "experiment"])

    assert saved == []
    main(["run", "experiment", "--legacy"])
    assert saved == [("experiment", {"metrics": {"return": 0.1}})]


def test_snapshot_cli_run_defaults_to_online_and_binds_current_definition(
    monkeypatch,
    tmp_path,
) -> None:
    calls = []
    coordinator_args = []

    class FakeCoordinator:
        def __init__(self, **kwargs):
            coordinator_args.append(kwargs)

        def execute(self, name, runner, **kwargs):
            calls.append((name, runner, kwargs))

    strategy = FakeSnapshotAwareStrategy()
    monkeypatch.setattr("trading.cli.get_experiment", lambda name: strategy)
    monkeypatch.setattr("trading.cli.ResearchRunCoordinator", FakeCoordinator)
    monkeypatch.setattr("trading.cli.create_default_research_data_store", lambda: object())
    monkeypatch.setattr("trading.cli.create_default_research_definition_store", lambda: object())
    manifest_path = tmp_path / "run.snapshot.json"

    main(["run", "experiment", "--snapshot", str(manifest_path)])

    name, runner, kwargs = calls[0]
    assert name == "experiment"
    assert runner == strategy.run_with_bundle
    assert kwargs["manifest_path"] == manifest_path
    assert kwargs["mode"] is RunMode.ONLINE
    assert kwargs["current_definition"].fingerprint == "b" * 64
    assert coordinator_args[0]["experiment_family"] == "spy-momentum"
    assert coordinator_args[0]["hypothesis"] == "momentum persists"


def test_snapshot_aware_cli_run_uses_prepared_manifest_by_default(monkeypatch) -> None:
    calls = []
    discovery_calls = []
    prepared_path = Path("results/experiment") / f"{'c' * 64}.snapshot.json"

    class FakeStore:
        def latest_manifest_for_definition(self, manifest_root, definition):
            discovery_calls.append((manifest_root, definition))
            return prepared_path

    class FakeCoordinator:
        def __init__(self, **kwargs):
            pass

        def execute(self, name, runner, **kwargs):
            calls.append((name, kwargs))

    monkeypatch.setattr("trading.cli.get_experiment", lambda name: FakeSnapshotAwareStrategy())
    monkeypatch.setattr("trading.cli.ResearchRunCoordinator", FakeCoordinator)
    monkeypatch.setattr("trading.cli.create_default_research_data_store", FakeStore)
    monkeypatch.setattr("trading.cli.create_default_research_definition_store", lambda: object())

    main(["run", "experiment"])

    _, kwargs = calls[0]
    assert discovery_calls == [
        (
            Path("results/experiment"),
            DefinitionBlobRef(digest="a" * 64, byte_count=100, fingerprint="b" * 64),
        )
    ]
    assert kwargs["manifest_path"] == prepared_path
    assert kwargs["mode"] is RunMode.ONLINE


def test_result_status_is_a_read_only_cli_diagnostic(monkeypatch, tmp_path, capsys) -> None:
    results_root = tmp_path / "results"
    experiment_dir = results_root / "experiment"
    experiment_dir.mkdir(parents=True)
    latest = experiment_dir / "latest.json"
    latest.write_text(
        '{"part_a": {}, "part_b": {}, "part_c": {}}',
        encoding="utf-8",
    )
    before = latest.read_bytes()
    monkeypatch.setattr("trading.core.results.RESULTS_DIR", results_root)

    main(["result", "status", "experiment"])

    assert "legacy" in capsys.readouterr().out
    assert latest.read_bytes() == before


def test_result_status_compares_with_the_current_definition(monkeypatch, tmp_path, capsys) -> None:
    results_root = tmp_path / "results"
    experiment_dir = results_root / "experiment"
    experiment_dir.mkdir(parents=True)
    now = datetime.now(UTC)
    session = PrimaryUSSessionCalendar().latest_completed_session(now)
    definition = DefinitionBlobRef("a" * 64, 100, "b" * 64)
    manifest = SnapshotManifest(
        snapshot_id="c" * 64,
        schema_version=1,
        created_at=now,
        decision_time=SignalDecisionTime.for_primary_session(session),
        data=(),
        definition=definition,
    )
    latest = experiment_dir / "latest.json"
    latest.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "validity": {"status": "valid", "reasons": []},
                "data_snapshot_id": manifest.snapshot_id,
                "data_snapshot_manifest": "result.snapshot.json",
                "data_cutoff": session.isoformat(),
                "definition_snapshot_id": definition.digest,
                "definition_fingerprint": definition.fingerprint,
                "development_summary": {},
                "historical_stability_folds": [],
                "shadow_evidence": {},
                "live_evidence": {},
                "legacy_period_results": {},
                "run_mode": "online",
            }
        ),
        encoding="utf-8",
    )

    class FakeStore:
        def load_snapshot(self, _path):
            return SimpleNamespace(manifest=manifest)

    monkeypatch.setattr("trading.core.results.RESULTS_DIR", results_root)
    monkeypatch.setattr("trading.cli.create_default_research_data_store", FakeStore)
    monkeypatch.setattr(
        "trading.cli.resolve_current_definition_fingerprint",
        lambda _name: "f" * 64,
    )

    main(["result", "status", "experiment"])

    assert "definition-stale" in capsys.readouterr().out


def test_result_registry_seed_is_explicit_and_marks_selection_history_incomplete(
    monkeypatch,
    tmp_path,
    capsys,
) -> None:
    results_root = tmp_path / "results"
    monkeypatch.setattr("trading.core.results.RESULTS_DIR", results_root)
    monkeypatch.setattr("trading.cli.list_experiments", lambda: ["spy_001", "spy_002"])

    main(["result", "registry", "seed"])

    output = capsys.readouterr().out
    assert "incomplete" in output
    registry = json.loads((results_root / "trial_registry.json").read_text())
    assert registry["selection_history_incomplete"] is True
    assert len(registry["trials"]) == 2
