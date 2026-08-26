import json
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from trading.cli import main
from trading.market_data import PrimaryUSSessionCalendar, SignalDecisionTime
from trading.research_data import (
    DefinitionBlobRef,
    SnapshotManifest,
)


@pytest.mark.parametrize(
    "argv",
    [
        ["legacy", "run", "experiment"],
        ["legacy", "analyze", "experiment"],
        ["legacy", "sync-docs"],
        ["legacy", "followup-backtest"],
        ["followup-state", "resume", "--reason", "retired"],
        ["legacy", "result", "evaluate", "SPY"],
        ["legacy", "result", "registry", "seed"],
        [
            "data",
            "snapshot",
            "SPY",
            "--experiment",
            "experiment",
            "--history-start",
            "2020-01-01",
            "--decision",
            "2026-08-01",
        ],
    ],
)
def test_legacy_research_mutation_and_execution_commands_fail_closed(argv) -> None:
    with pytest.raises(SystemExit, match="legacy experiment research is retired"):
        main(argv)


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
    monkeypatch.setattr("trading.legacy.results.RESULTS_DIR", results_root)

    main(["legacy", "result", "status", "experiment"])

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
                "schema_version": 3,
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
                "canonical_sleeve_evidence": {
                    "engine_version": "canonical-sleeve-v1",
                    "ranking_scenario": "base_net",
                    "initial_capital": 1.0,
                    "cost_policies": {"base": {}, "stress": {}},
                    "raw_signals": [],
                    "raw_candidates": [],
                    "scenarios": {
                        name: {
                            "metrics": {
                                "initial_equity": 1.0,
                                "final_equity": 1.0,
                                "total_return": 0.0,
                                "annualized_return": None,
                                "annualized_volatility": None,
                                "sharpe_ratio": None,
                                "max_drawdown": 0.0,
                            },
                            "trades": [],
                            "daily_equity": [],
                        }
                        for name in ("gross", "base_net", "stress_net")
                    },
                    "parity": {
                        "signal_differences": [],
                        "trade_differences": [],
                        "trade_comparisons": [],
                        "has_unclassified_differences": False,
                    },
                },
                "run_mode": "online",
            }
        ),
        encoding="utf-8",
    )

    class FakeStore:
        def load_snapshot(self, _path):
            return SimpleNamespace(manifest=manifest)

    monkeypatch.setattr("trading.legacy.results.RESULTS_DIR", results_root)
    monkeypatch.setattr("trading.commands.legacy.ResearchDataStore", lambda _path: FakeStore())
    monkeypatch.setattr(
        "trading.commands.legacy.resolve_current_definition_fingerprint",
        lambda _name: "f" * 64,
    )

    main(["legacy", "result", "status", "experiment"])

    assert "definition-stale" in capsys.readouterr().out


def test_result_registry_seed_cannot_mutate_retired_legacy_inventory(tmp_path) -> None:
    results_root = tmp_path / "results"
    registry_path = results_root / "registries" / "trial_registry.json"

    with pytest.raises(SystemExit, match="legacy experiment research is retired"):
        main(["legacy", "result", "registry", "seed"])

    assert not registry_path.exists()
