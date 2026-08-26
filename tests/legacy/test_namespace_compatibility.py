import importlib

import pytest

from trading.cli import build_parser, main
from trading.experiments import list_experiments


@pytest.mark.parametrize(
    ("old_name", "new_name"),
    [
        ("trading.core.results", "trading.legacy.results"),
        ("trading.core.definition_resolver", "trading.legacy.definition_resolver"),
        ("trading.core.workflow_authoring", "trading.workflow.authoring"),
        ("trading.core.workflow_studies", "trading.workflow.studies"),
        ("trading.core.study_qualification", "trading.workflow.study_qualification"),
        ("trading.core.study_terminal_evidence", "trading.workflow.terminal_evidence"),
        ("trading.core.qualification_workflow", "trading.workflow.qualification"),
    ],
)
def test_old_python_module_is_an_alias_of_canonical_namespace(old_name, new_name) -> None:
    assert importlib.import_module(old_name) is importlib.import_module(new_name)


def test_historical_experiment_import_identity_and_inventory_are_preserved() -> None:
    module = importlib.import_module("trading.experiments.spy_007_trend_pullback")

    assert module.__name__ == "trading.experiments.spy_007_trend_pullback"
    assert len(list_experiments()) == 424


def test_legacy_namespace_parses_read_only_and_retired_commands() -> None:
    parser = build_parser()

    assert parser.parse_args(["legacy", "list"]).legacy_command == "list"
    assert parser.parse_args(["legacy", "compare", "first", "second"]).experiments == [
        "first",
        "second",
    ]
    assert parser.parse_args(["legacy", "result", "status", "--all"]).all is True
    assert parser.parse_args(["legacy", "freshness"]).legacy_command == "freshness"


@pytest.mark.parametrize(
    "command",
    ["list", "run", "followup-backtest", "compare", "result", "analyze", "sync-docs"],
)
def test_top_level_legacy_command_is_rejected_by_parser(command) -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args([command])

    assert exc_info.value.code == 2


@pytest.mark.parametrize("command", ["run", "analyze", "sync-docs", "followup-backtest"])
def test_retired_legacy_namespace_still_fails_closed(command) -> None:
    argv = ["legacy", command]
    if command in {"run", "analyze"}:
        argv.append("example")

    with pytest.raises(SystemExit, match="legacy experiment research is retired"):
        main(argv)
