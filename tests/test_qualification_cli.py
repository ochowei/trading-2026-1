import hashlib
import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from trading.cli import build_parser, main
from trading.core.accounting import canonical_json_bytes
from trading.research_data.qualification_registry import QualificationRegistry


def _hash_chain(events: list[dict[str, object]]) -> list[dict[str, object]]:
    previous_hash = "0" * 64
    chained = []
    for event in events:
        content = {**event, "previous_hash": previous_hash}
        event_hash = hashlib.sha256(canonical_json_bytes(content)).hexdigest()
        chained.append({**content, "event_hash": event_hash})
        previous_hash = event_hash
    return chained


def _write_registry(path, state: dict[str, object]) -> None:
    content = json.dumps(state).encode()
    path.write_bytes(content)
    events = state["events"]
    checkpoint = {
        "schema_version": 1,
        "event_count": len(events),
        "registry_checksum": hashlib.sha256(content).hexdigest(),
        "head_hash": events[-1]["event_hash"],
    }
    path.with_name(f".{path.name}.head.json").write_text(json.dumps(checkpoint))


def test_qualification_status_is_read_only_and_reports_lifecycle(
    tmp_path,
    capsys,
    monkeypatch,
) -> None:
    registry_path = tmp_path / "qualification_registry.json"
    _write_registry(
        registry_path,
        {
            "schema_version": 1,
            "events": _hash_chain(
                [
                    {
                        "sequence": 1,
                        "event_id": "historical-plan:plan-1",
                        "event_type": "historical_plan",
                        "payload": {
                            "plan_id": "plan-1",
                            "definition_fingerprint": "a" * 64,
                        },
                    },
                    {
                        "sequence": 2,
                        "event_id": "historical-screen:plan-1",
                        "event_type": "historical_screen",
                        "payload": {
                            "plan_id": "plan-1",
                            "passed": True,
                            "disposition": "shadow-eligible",
                        },
                    },
                    {
                        "sequence": 3,
                        "event_id": "shadow-registration:shadow-1",
                        "event_type": "shadow_registration",
                        "payload": {
                            "shadow_id": "shadow-1",
                            "historical_plan_id": "plan-1",
                            "definition_fingerprint": "a" * 64,
                            "definition_snapshot_id": "d" * 64,
                            "definition_snapshot_byte_count": 100,
                            "status": "shadow",
                        },
                    },
                    {
                        "sequence": 4,
                        "event_id": "shadow-evidence:shadow-1:2027-08-10",
                        "event_type": "shadow_evidence",
                        "payload": {
                            "shadow_id": "shadow-1",
                            "as_of": "2027-08-10",
                            "completed_sessions": 252,
                            "simulated_fills": [{"proposal_id": "proposal-1"}],
                        },
                    },
                    {
                        "sequence": 5,
                        "event_id": "activation-evaluation:shadow-1:2027-08-10",
                        "event_type": "activation_evaluation",
                        "payload": {
                            "shadow_id": "shadow-1",
                            "evaluated_at": "2027-08-10",
                            "disposition": "shadow-insufficient-evidence",
                            "authorized_for_live_orders": False,
                        },
                    },
                    {
                        "sequence": 6,
                        "event_id": "shadow-evidence:shadow-1:2027-08-11",
                        "event_type": "shadow_evidence",
                        "payload": {
                            "shadow_id": "shadow-1",
                            "as_of": "2027-08-11",
                            "completed_sessions": 253,
                            "simulated_fills": [{"proposal_id": "proposal-1"}],
                        },
                    },
                ]
            ),
        },
    )
    monkeypatch.setattr(
        "trading.cli.QualificationRegistry",
        lambda path: QualificationRegistry(
            path,
            definition_verifier=lambda _digest, _size, _fingerprint: None,
        ),
    )

    args = build_parser().parse_args(["qualification", "status", "--path", str(registry_path)])
    assert args.command == "qualification"
    assert args.qualification_command == "status"

    before = registry_path.read_bytes()
    main(["qualification", "status", "--path", str(registry_path)])

    output = capsys.readouterr().out
    assert "plan-1: shadow-eligible" in output
    assert "shadow-1: shadow-awaiting-activation" in output
    assert "sessions=253" in output
    assert "trades=1" in output
    assert "live authorization=false" in output
    assert registry_path.read_bytes() == before
    assert not registry_path.with_name(f".{registry_path.name}.lock").exists()


def test_qualification_plan_register_has_no_backdated_clock_input(
    tmp_path,
    capsys,
    monkeypatch,
) -> None:
    captured = {}
    epoch = SimpleNamespace(
        selected_trial_id="selected-trial",
        included_trial_ids=("baseline-trial", "selected-trial"),
        prior_selection_history_incomplete=True,
    )
    plan = SimpleNamespace(
        plan_id="historical-plan-forward",
        experiment_family="SPY:forward-program",
        evaluation_sessions=(date(2027, 1, 4), date(2031, 12, 31)),
        forward_selection_epoch=epoch,
    )

    def register(**kwargs):
        captured.update(kwargs)
        return plan

    monkeypatch.setattr("trading.cli.register_forward_qualification_plan", register)
    argv = [
        "qualification",
        "plan",
        "register",
        "--path",
        str(tmp_path / "qualification.json"),
        "--trial-registry-path",
        str(tmp_path / "trials.json"),
        "--experiment",
        "spy_forward",
        "--family-baseline-trial-id",
        "baseline-trial",
        "--evaluation-years",
        "2027",
        "2028",
        "2029",
        "2030",
        "2031",
        "--maximum-holding-sessions",
        "5",
        "--execution-lag-sessions",
        "1",
        "--dependency-sessions",
        "6",
        "--embargo-sessions",
        "1",
        "--random-seed",
        "17",
    ]

    main(argv)

    assert captured["evaluation_years"] == (2027, 2028, 2029, 2030, 2031)
    assert captured["development_years"] is None
    assert captured["warmup_start"] is None
    assert captured["warmup_end"] is None
    assert captured["random_samples"] == 1000
    assert "created_at" not in captured
    assert "qualification plan registered: historical-plan-forward" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        build_parser().parse_args([*argv, "--created-at", "2020-01-01T00:00:00Z"])


def test_retrospective_plan_cli_routes_explicit_role_calendar(
    tmp_path, capsys, monkeypatch
) -> None:
    captured = {}
    checkpoint = SimpleNamespace(
        selected_trial_id="selected-trial",
        included_trial_ids=("baseline-trial", "selected-trial"),
        prior_selection_history_incomplete=True,
    )
    plan = SimpleNamespace(
        plan_id="retrospective-plan-explicit-calendar",
        experiment_family="FXI:retrospective",
        evaluation_sessions=(date(2010, 1, 4), date(2014, 12, 31)),
        forward_selection_epoch=None,
        retrospective_selection_checkpoint=checkpoint,
        evidence_role="retrospective-confirmatory",
        evidence_audit=SimpleNamespace(classification="provenance-unknown"),
    )

    def register(**kwargs):
        captured.update(kwargs)
        return plan

    monkeypatch.setattr("trading.cli.register_forward_qualification_plan", register)
    main(
        [
            "qualification",
            "plan",
            "register",
            "--research",
            "fxi/selected",
            "--workflow",
            "workflows/example--v006",
            "--family-baseline-trial-id",
            "baseline-trial",
            "--evaluation-years",
            "2010",
            "2011",
            "2012",
            "2013",
            "2014",
            "--development-years",
            "2015",
            "2016",
            "2017",
            "--warmup-start",
            "2009-01-01",
            "--warmup-end",
            "2009-12-31",
            "--maximum-holding-sessions",
            "20",
            "--execution-lag-sessions",
            "1",
            "--dependency-sessions",
            "21",
            "--embargo-sessions",
            "1",
            "--random-seed",
            "20260813",
            "--evidence-role",
            "retrospective-confirmatory",
            "--evidence-classification",
            "provenance-unknown",
            "--audit-justification",
            "Legacy history is incomplete.",
        ]
    )

    assert captured["development_years"] == (2015, 2016, 2017)
    assert captured["warmup_start"] == date(2009, 1, 1)
    assert captured["warmup_end"] == date(2009, 12, 31)
    assert "retrospective-plan-explicit-calendar" in capsys.readouterr().out


def test_qualification_cli_rejects_caller_supplied_complete_family() -> None:
    with pytest.raises(SystemExit, match="register-study"):
        main(
            [
                "qualification",
                "plan",
                "register",
                "--research",
                "fxi/candidate",
                "--workflow",
                "workflows/example--v004",
                "--family-research",
                "fxi/candidate",
                "--family-research",
                "fxi/baseline",
                "--family-source-sha",
                f"fxi/candidate={'a' * 64}",
                "--family-source-sha",
                f"fxi/baseline={'b' * 64}",
                "--family-trial-budget",
                "2",
                "--dry-run",
                "--family-baseline-trial-id",
                "baseline-trial",
                "--evaluation-years",
                "2027",
                "2028",
                "2029",
                "2030",
                "2031",
                "--maximum-holding-sessions",
                "1",
                "--execution-lag-sessions",
                "1",
                "--dependency-sessions",
                "2",
                "--embargo-sessions",
                "1",
                "--random-seed",
                "17",
            ]
        )


def test_qualification_cli_rejects_generic_registration_for_structured_workflow(
    tmp_path,
) -> None:
    workflow = tmp_path / "workflows" / "example--v008"
    workflow.mkdir(parents=True)
    (workflow / "RELEASE.json").write_text(
        json.dumps({"capabilities": ["study-time-retrospective-v1"]}) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="register-study"):
        main(
            [
                "qualification",
                "plan",
                "register",
                "--research",
                "fxi/candidate",
                "--workflow",
                str(workflow),
                "--family-baseline-trial-id",
                "baseline-trial",
                "--evaluation-years",
                "2027",
                "2028",
                "2029",
                "2030",
                "2031",
                "--maximum-holding-sessions",
                "1",
                "--execution-lag-sessions",
                "1",
                "--dependency-sessions",
                "2",
                "--embargo-sessions",
                "1",
                "--random-seed",
                "17",
            ]
        )


def test_qualification_cli_routes_only_exact_study_inputs(capsys, monkeypatch) -> None:
    captured = {}
    boundary = SimpleNamespace(included_trial_ids=("one", "two"))
    plan = SimpleNamespace(
        plan_id="historical-plan-study",
        study_identity=SimpleNamespace(study_path="workflows/example--v001/work/studies/x--s001"),
        experiment_family="FXI:family",
        evidence_role="historical",
        forward_selection_epoch=boundary,
        retrospective_selection_checkpoint=None,
    )

    def compile_plan(**kwargs):
        captured.update(kwargs)
        return plan

    monkeypatch.setattr("trading.cli.compile_study_qualification_plan", compile_plan)
    main(
        [
            "qualification",
            "plan",
            "register-study",
            "--study",
            "workflows/example--v001/work/studies/x--s001",
            "--path",
            "qualification.json",
            "--trial-registry-path",
            "trials.json",
            "--dry-run",
        ]
    )

    assert captured == {
        "study_path": Path("workflows/example--v001/work/studies/x--s001"),
        "qualification_registry_path": Path("qualification.json"),
        "trial_registry_path": Path("trials.json"),
        "dry_run": True,
        "approved_by": None,
        "contamination_declaration": None,
    }
    assert "study qualification plan compiled (dry-run)" in capsys.readouterr().out


def test_qualification_screen_run_routes_exact_trial_manifests(
    tmp_path,
    capsys,
    monkeypatch,
) -> None:
    captured = {}
    execution = SimpleNamespace(
        event_id="historical-screen:plan-1",
        screen=SimpleNamespace(disposition="historical-screen-failed", passed=False),
    )

    def run_screen(**kwargs):
        captured.update(kwargs)
        return execution

    monkeypatch.setattr("trading.cli.run_registered_historical_screen", run_screen)
    main(
        [
            "qualification",
            "screen",
            "run",
            "--path",
            str(tmp_path / "qualification.json"),
            "--trial-registry-path",
            str(tmp_path / "trials.json"),
            "--plan-id",
            "plan-1",
            "--trial",
            "selected=selected.snapshot.json",
            "--trial",
            "baseline=baseline.snapshot.json",
        ]
    )

    assert captured["trial_manifests"] == {
        "selected": Path("selected.snapshot.json"),
        "baseline": Path("baseline.snapshot.json"),
    }
    assert "historical screen recorded: historical-screen:plan-1" in capsys.readouterr().out
