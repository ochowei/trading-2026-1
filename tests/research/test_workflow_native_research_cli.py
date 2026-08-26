from datetime import date
from pathlib import Path
from types import SimpleNamespace

from trading.cli import build_parser, main
from trading.commands.research import _workflow_observation_provenance
from trading.market_data import MarketDataRequirement, MarketDataSeries
from trading.research_data import DefinitionBlobRef, ResearchDefinitionSnapshot
from trading.research_definitions import resolve_workflow_policy_set

WORKFLOW = Path("workflows/strategy-forward-replication-research--v001")


def test_released_workflow_resolves_exact_four_policy_set() -> None:
    policy_set = resolve_workflow_policy_set(WORKFLOW)

    assert {release.identity.family for release in policy_set.releases} == {
        "canonical-execution",
        "firstrade-manual-trading",
        "portfolio-risk",
        "us-equity-market",
    }
    assert len(policy_set.identity) == 64


def test_research_cli_parses_explicit_workflow_snapshot_and_run_modes() -> None:
    parser = build_parser()
    snapshot = parser.parse_args(
        [
            "research",
            "snapshot",
            "family/trial",
            "--workflow",
            str(WORKFLOW),
            "--decision",
            "2025-12-31",
        ]
    )
    run = parser.parse_args(
        [
            "research",
            "run",
            "family/trial",
            "--workflow",
            str(WORKFLOW),
            "--manifest",
            "results/trial/snapshot.snapshot.json",
            "--offline",
        ]
    )

    assert snapshot.decision.isoformat() == "2025-12-31"
    assert snapshot.cache_root is None
    assert snapshot.reuse_full_refresh is False
    assert run.offline is True


def test_research_snapshot_can_use_an_isolated_market_data_cache(
    monkeypatch, capsys, tmp_path
) -> None:
    requirement = MarketDataRequirement(
        MarketDataSeries.yahoo_adjusted_daily("FXI"),
        history_start=date(2013, 11, 6),
        role="primary",
    )
    blob = DefinitionBlobRef(digest="a" * 64, byte_count=1, fingerprint="b" * 64)
    captured = ResearchDefinitionSnapshot(
        fingerprint=blob.fingerprint,
        blob=blob,
        policy_set_identity="c" * 64,
    )

    class Definition:
        result_name = "fxi-test"

        @staticmethod
        def market_data_requirements():
            return (requirement,)

        @staticmethod
        def capture_research_definition(_store, _policy_set):
            return captured

    class Service:
        cache = object()

        @staticmethod
        def refresh(*_args, **_kwargs):
            return None

    class Store:
        @staticmethod
        def create_snapshot(_cache, _requirements, _decision_time, *, definition=None):
            assert definition == blob
            return SimpleNamespace(snapshot_id="d" * 64)

        @staticmethod
        def write_manifest(_manifest, path):
            return path

    service_calls = []

    def service_factory(**kwargs):
        service_calls.append(kwargs)
        return Service()

    monkeypatch.setattr(
        "trading.commands.research._workflow_native_context",
        lambda _identity, _workflow: (Definition(), object()),
    )
    monkeypatch.setattr(
        "trading.commands.research.create_default_market_data_service", service_factory
    )
    monkeypatch.setattr("trading.commands.research._research_data_store", Store)
    monkeypatch.setattr("trading.commands.research._definition_store", object)
    cache_root = tmp_path / "s003-development"

    main(
        [
            "research",
            "snapshot",
            "family/trial",
            "--workflow",
            str(WORKFLOW),
            "--decision",
            "2019-12-31",
            "--manifest",
            str(tmp_path / "isolated.snapshot.json"),
            "--cache-root",
            str(cache_root),
        ]
    )

    assert service_calls == [
        {
            "cache_root": cache_root,
            "quarantine_root": tmp_path / "s003-development-quarantine",
        }
    ]
    assert "research snapshot" in capsys.readouterr().out


def test_research_snapshot_can_reuse_eligible_full_refresh_without_provider_access(
    monkeypatch, capsys, tmp_path
) -> None:
    requirement = MarketDataRequirement(
        MarketDataSeries.yahoo_adjusted_daily("XLF"),
        history_start=date(1998, 12, 22),
        role="primary",
    )
    blob = DefinitionBlobRef(digest="a" * 64, byte_count=1, fingerprint="b" * 64)
    captured = ResearchDefinitionSnapshot(
        fingerprint=blob.fingerprint,
        blob=blob,
        policy_set_identity="c" * 64,
    )

    class Definition:
        result_name = "xlf-test"

        @staticmethod
        def market_data_requirements():
            return (requirement,)

        @staticmethod
        def capture_research_definition(_store, _policy_set):
            return captured

    class Service:
        cache = object()

        @staticmethod
        def refresh(*_args, **_kwargs):
            raise AssertionError("reuse must not call the provider refresh path")

    class Store:
        created = []

        def create_snapshot(self, cache, requirements, decision_time, *, definition=None):
            self.created.append((cache, tuple(requirements), decision_time, definition))
            return SimpleNamespace(snapshot_id="d" * 64)

        @staticmethod
        def write_manifest(_manifest, path):
            return path

    store = Store()
    monkeypatch.setattr(
        "trading.commands.research._workflow_native_context",
        lambda _identity, _workflow: (Definition(), object()),
    )
    monkeypatch.setattr("trading.commands.research.create_default_market_data_service", Service)
    monkeypatch.setattr("trading.commands.research._research_data_store", lambda: store)
    monkeypatch.setattr("trading.commands.research._definition_store", object)
    destination = tmp_path / "reused.snapshot.json"

    main(
        [
            "research",
            "snapshot",
            "family/trial",
            "--workflow",
            str(WORKFLOW),
            "--decision",
            "2020-12-31",
            "--manifest",
            str(destination),
            "--reuse-full-refresh",
        ]
    )

    assert store.created[0][1] == (requirement,)
    assert store.created[0][3] == blob
    assert "reused the current eligible full-refresh generation" in capsys.readouterr().out


def test_workflow_run_provenance_captures_binding_command_and_exact_sources() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "research",
            "run",
            "family/trial",
            "--workflow",
            str(WORKFLOW),
            "--manifest",
            "results/trial/snapshot.snapshot.json",
            "--offline",
        ]
    )
    policy_set = resolve_workflow_policy_set(WORKFLOW)

    provenance = _workflow_observation_provenance(args, policy_set)

    assert provenance["canonical_argv"] == [
        "trading",
        "research",
        "run",
        "family/trial",
        "--workflow",
        str(WORKFLOW),
        "--manifest",
        "results/trial/snapshot.snapshot.json",
        "--offline",
    ]
    assert provenance["workflow"]["workflow"] == "strategy-forward-replication-research"
    assert provenance["workflow"]["version"] == "v001"
    assert provenance["workflow"]["policy_set_identity"] == policy_set.identity
    assert len(provenance["workflow"]["release_sha256"]) == 64
    assert len(provenance["workflow"]["workflow_sha256"]) == 64
    sources = provenance["orchestration"]["sources"]
    assert "src/trading/cli.py" in sources
    assert sources["src/trading/cli.py"]["content"].startswith('"""')
    assert len(sources["src/trading/cli.py"]["sha256"]) == 64


def test_research_list_excludes_legacy_inventory(capsys) -> None:
    main(["research", "list"])

    output = capsys.readouterr().out
    assert "schd-down-streak-reversion/two-down" in output
    assert "spy_007" not in output
