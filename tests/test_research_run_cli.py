from pathlib import Path

import pytest

from trading.cli import build_parser, main
from trading.research_data import (
    DefinitionBlobRef,
    ResearchDefinitionSnapshot,
    RunMode,
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

    class FakeCoordinator:
        def __init__(self, *, store, results_root):
            pass

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
