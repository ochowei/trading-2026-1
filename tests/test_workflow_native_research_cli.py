from pathlib import Path

from trading.cli import build_parser, main
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
    assert run.offline is True


def test_research_list_excludes_legacy_inventory(capsys) -> None:
    main(["research", "list"])

    output = capsys.readouterr().out
    assert "schd-down-streak-reversion/two-down" in output
    assert "spy_007" not in output
