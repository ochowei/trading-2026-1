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


def test_deprecated_result_alias_preserves_output_and_adds_warning(capsys) -> None:
    main(["legacy", "result", "status", "missing"])
    canonical = capsys.readouterr()

    main(["result", "status", "missing"])
    alias = capsys.readouterr()

    assert alias.out == canonical.out
    assert "deprecated" in alias.err
    assert canonical.err == ""


@pytest.mark.parametrize("command", ["run", "analyze", "sync-docs", "followup-backtest"])
def test_retired_alias_and_namespace_have_identical_failure(command, capsys) -> None:
    canonical = ["legacy", command]
    alias = [command]
    if command in {"run", "analyze"}:
        canonical.append("example")
        alias.append("example")

    with pytest.raises(SystemExit) as canonical_exit:
        main(canonical)
    canonical_output = capsys.readouterr()
    with pytest.raises(SystemExit) as alias_exit:
        main(alias)
    alias_output = capsys.readouterr()

    assert alias_exit.value.code == canonical_exit.value.code
    assert alias_output.out == canonical_output.out
    assert "deprecated" in alias_output.err
    assert canonical_output.err == ""
