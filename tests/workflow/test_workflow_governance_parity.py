from pathlib import Path

import yaml

from trading.cli import build_parser

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_A1_2_ACTIONS = {
    "A12-A01",
    "A12-A02",
    "A12-A03",
    "A12-A04",
    "A12-A05A",
    "A12-A05B",
    "A12-A06",
    "A12-A07",
    "A12-A08",
    "A12-A09",
    "A12-A10",
    "A12-A11",
    "A12-A12",
    "A12-A13",
}


def _read(path: str) -> str:
    return (REPOSITORY_ROOT / path).read_text(encoding="utf-8")


def test_governance_diagram_declares_the_complete_a1_2_action_set() -> None:
    model = yaml.safe_load(_read("docs/workflow-governance/workflow-governance-layers.yaml"))

    assert set(model["validation"]["a1_2_action_ids"]) == EXPECTED_A1_2_ACTIONS


def test_governance_cli_actions_remain_parseable() -> None:
    parser = build_parser()
    action_commands = {
        "A12-A03": ["workflow", "create", "--request", "create.json", "--dry-run"],
        "A12-A04": ["workflow", "evolve", "--request", "evolve.json", "--dry-run"],
        "A12-A05A": ["workflow", "release", "workflow--v002", "--approved-by", "owner"],
        "A12-A05B": ["workflow", "release", "workflow--v001", "--approved-by", "owner"],
        "A12-A07": ["workflow", "activate", "workflow--v002", "--approved-by", "owner"],
        "A12-A08": [
            "workflow",
            "study",
            "init",
            "workflow--v001",
            "--slug",
            "example",
            "--title",
            "Example",
            "--created-by",
            "operator",
        ],
        "A12-A09": [
            "workflow",
            "study",
            "transition",
            "study--s001",
            "--to",
            "running",
            "--by",
            "operator",
        ],
        "A12-A10": [
            "workflow",
            "study",
            "complete",
            "study--s001",
            "--outcome",
            "pass",
            "--reviewed-by",
            "reviewer",
        ],
        "A12-A12": [
            "workflow",
            "safety",
            "assess",
            "workflow--v002",
            "--request",
            "assessment.json",
            "--by",
            "author",
        ],
        "A12-A13": [
            "workflow",
            "safety",
            "clear",
            "workflow--v002/work/release-safety/sa001",
            "--request",
            "clearance.json",
            "--approved-by",
            "owner",
        ],
    }

    for action_id, command in action_commands.items():
        parsed = parser.parse_args(command)
        assert parsed.workflow_command is not None, action_id

    state = parser.parse_args(["workflow", "version", "state", "workflow--v001", "--json"])
    assert state.workflow_version_command == "state"
    assert state.json_output is True


def test_workflow_skills_expose_state_and_safety_routes() -> None:
    author = _read(".agents/skills/trading-author-workflow/SKILL.md")
    safety = _read(".agents/skills/trading-author-workflow/references/safety.md")
    operator = _read(".agents/skills/trading-operate-workflow/SKILL.md")
    reviewer = _read(".agents/skills/trading-evaluate-study/SKILL.md")

    assert "references/safety.md" in author
    assert "workflow safety assess" in safety
    assert "workflow safety clear" in safety
    for instructions in (author, operator, reviewer):
        assert "workflow version state" in instructions
