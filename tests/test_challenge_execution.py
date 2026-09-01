import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from trading.workflow import challenge_execution as challenge_module
from trading.workflow.challenge_execution import run_fixed_study_challenges
from trading.workflow.study_qualification import (
    REQUIRED_STUDY_TIME_CHALLENGES,
    fixed_challenge_method_contract,
)
from trading.workflow.terminal_evidence import _validate_challenge_manifest


class _QualificationRegistry:
    plan = None

    def __init__(self, _path: Path) -> None:
        pass

    def historical_plan(self, _plan_id: str):
        return self.plan


class _TrialRegistry:
    def __init__(self, _path: Path) -> None:
        pass

    def read(self) -> dict:
        return {"trials": []}


def _gate_target(challenge_id: str, identities: tuple[str, ...]) -> dict:
    if challenge_id == "cash":
        return {"kind": "benchmark", "identities": ["cash"]}
    if challenge_id == "random-entry":
        return {"kind": "benchmark", "identities": ["random-entry"]}
    if challenge_id == "family-baseline":
        return {"kind": "trial", "identities": [identities[1]]}
    target = {
        "parameter-perturbation": identities[2],
        "delayed-entry": identities[3],
    }.get(challenge_id, f"{challenge_id}-method")
    return {"kind": "method", "identities": [target]}


def _projection(identity: str) -> dict:
    sessions = [date(2020, 1, day).isoformat() for day in range(2, 22)]
    points = [
        {
            "date": session,
            "equity": 1.0 + index * 0.01,
            "cash": 1.0 + index * 0.01,
            "position_value": 0.0,
        }
        for index, session in enumerate(sessions)
    ]
    trades = [
        {
            "signal_date": sessions[index],
            "entry_date": sessions[index],
            "exit_date": sessions[index + 1],
            "status": "completed",
            "quantity": 1.0,
            "executed_entry_price": 100.0,
            "executed_exit_price": 102.0,
            "total_fees": 0.1,
        }
        for index in range(0, 18)
    ]
    total_return = 0.30 if identity == "family/selected" else 0.05
    scenario = {
        "daily_equity": points,
        "trades": trades,
        "metrics": {
            "total_return": total_return,
            "max_drawdown": 0.0,
            "profit_factor": "Infinity",
        },
    }
    return {
        "evaluation_sessions": sessions,
        "scenarios": {"base_net": scenario, "stress_net": scenario},
        "candidates": [],
        "data_generation": "9" * 64,
        "source": {
            "identity": identity,
            "trial_id": f"trial-{identity}",
            "definition_fingerprint": "8" * 64,
            "manifest_path": f"results/{identity}.snapshot.json",
            "manifest_sha256": "7" * 64,
            "snapshot_id": "6" * 64,
            "observation_id": f"observation-{identity}",
            "result_path": f"results/{identity}.json",
            "result_sha256": "5" * 64,
        },
    }


def _fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = tmp_path / "repo"
    study = root / "workflows/example--v009/work/studies/example--s001"
    study.mkdir(parents=True)
    identities = ("family/selected", "family/baseline", "family/perturb", "family/delayed")
    relative_study = study.relative_to(root).as_posix()
    identity = SimpleNamespace(
        study_path=relative_study,
        preregistration_sha256="a" * 64,
        qualification_spec_sha256="b" * 64,
        development_authorization_sha256="c" * 64,
        candidate_freeze_sha256="d" * 64,
        workflow_release_sha256="e" * 64,
    )
    spec = SimpleNamespace(
        route="fixed-calendar-retrospective",
        workflow_path=study.parents[2],
        qualification_registry_identity="state/qualification-registry.json",
        trial_registry_identity="results/registries/trial_registry.json",
        study_identity=identity,
        family_research_identities=identities,
        family_trial_ids={item: f"trial-{item}" for item in identities},
        policy_set_identity="f" * 64,
        research_identity=identities[0],
        family_baseline_research_identity=identities[1],
        study_path=study,
    )
    sessions = tuple(date(2020, 1, day) for day in range(2, 22))
    _QualificationRegistry.plan = SimpleNamespace(
        evidence_role="fixed-calendar-retrospective",
        study_identity=SimpleNamespace(study_path=relative_study),
        evaluation_sessions=sessions,
    )
    qualification = root / spec.qualification_registry_identity
    trials = root / spec.trial_registry_identity
    manifests = {identity: root / f"results/{identity}.snapshot.json" for identity in identities}
    for path in (qualification, trials, *manifests.values()):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")
    challenges = [
        {
            "id": challenge_id,
            "evidence_identity": f"{challenge_id}-evidence",
            "applies_to": _gate_target(challenge_id, identities),
            "gate": {"metric": "passed", "operator": "=", "threshold": True},
            "method": fixed_challenge_method_contract(challenge_id),
        }
        for challenge_id in sorted(REQUIRED_STUDY_TIME_CHALLENGES)
    ]
    (study / "QUALIFICATION_SPEC.json").write_text(
        json.dumps(
            {
                "benchmarks": {
                    "random_seed": 7,
                    "random_samples": 25,
                    "bootstrap_block_sessions": 5,
                },
                "required_challenges": challenges,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (study / "CANDIDATE_FREEZE.json").write_text(
        json.dumps(
            {
                "complete_family": [
                    {
                        "source_identity": item,
                        "definition_fingerprint": "8" * 64,
                    }
                    for item in identities
                ]
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        challenge_module, "load_frozen_study_qualification_spec", lambda _path: spec
    )
    monkeypatch.setattr(challenge_module, "QualificationRegistry", _QualificationRegistry)
    monkeypatch.setattr(challenge_module, "ExperimentTrialRegistry", _TrialRegistry)
    monkeypatch.setattr(
        challenge_module,
        "_load_projection",
        lambda **kwargs: _projection(kwargs["identity"]),
    )
    return SimpleNamespace(
        root=root,
        study=study,
        spec=spec,
        qualification=qualification,
        trials=trials,
        manifests=manifests,
        output=root / "results/workflows/example--v009/example--s001/challenges",
    )


def _run(fixture, *, dry_run: bool) -> Path:
    return run_fixed_study_challenges(
        study_path=fixture.study,
        plan_id="plan-1",
        family_manifests=fixture.manifests,
        qualification_registry_path=fixture.qualification,
        trial_registry_path=fixture.trials,
        research_data_store=object(),
        output_root=fixture.output,
        dry_run=dry_run,
    )


def test_challenge_dry_run_does_not_publish(tmp_path, monkeypatch) -> None:
    fixture = _fixture(tmp_path, monkeypatch)

    manifest = _run(fixture, dry_run=True)

    assert manifest.name == "MANIFEST.json"
    assert not fixture.output.exists()


def test_challenge_publication_contains_nine_distinct_artifacts_and_is_idempotent(
    tmp_path, monkeypatch
) -> None:
    fixture = _fixture(tmp_path, monkeypatch)

    first = _run(fixture, dry_run=False)
    second = _run(fixture, dry_run=False)

    assert first == second
    assert len(list(first.parent.iterdir())) == 10
    terminal = {
        "study_path": fixture.spec.study_identity.study_path,
        "preregistration_sha256": "a" * 64,
        "qualification_spec_sha256": "b" * 64,
        "development_authorization_sha256": "c" * 64,
        "candidate_freeze_sha256": "d" * 64,
        "qualification_evidence": {"plan_id": "plan-1"},
        "challenge_manifest": {
            "path": first.relative_to(fixture.root).as_posix(),
            "sha256": challenge_module._sha256(first),
        },
    }
    assert _validate_challenge_manifest(fixture.study, terminal) is True


def test_challenge_atomic_failure_leaves_no_partial_set(tmp_path, monkeypatch) -> None:
    fixture = _fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(
        challenge_module.os,
        "rename",
        lambda *_args: (_ for _ in ()).throw(OSError("boom")),
    )

    with pytest.raises(OSError, match="boom"):
        _run(fixture, dry_run=False)

    assert [item for item in fixture.output.iterdir() if item.is_dir()] == []


def test_challenge_rejects_workflow_provenance_drift(tmp_path) -> None:
    root = tmp_path / "repo"
    workflow = root / "workflows/example--v009"
    workflow.mkdir(parents=True)
    (workflow / "WORKFLOW.md").write_text("fixed-calendar-retrospective\n", encoding="utf-8")
    (workflow / "RELEASE.json").write_text(
        json.dumps({"workflow": "example", "version": "v009"}) + "\n",
        encoding="utf-8",
    )
    release_sha256 = challenge_module._sha256(workflow / "RELEASE.json")
    result = {
        "metadata": {
            "observation_provenance": {
                "workflow": {
                    "path": workflow.relative_to(root).as_posix(),
                    "workflow": "example",
                    "version": "v009",
                    "release_sha256": release_sha256,
                    "workflow_sha256": challenge_module._sha256(workflow / "WORKFLOW.md"),
                    "policy_set_identity": "f" * 64,
                }
            }
        }
    }
    challenge_module._validate_workflow_provenance(
        result,
        root=root,
        workflow_path=workflow,
        workflow_release_sha256=release_sha256,
        policy_set_identity="f" * 64,
    )
    result["metadata"]["observation_provenance"]["workflow"]["version"] = "v008"

    with pytest.raises(ValueError, match="provenance drifted"):
        challenge_module._validate_workflow_provenance(
            result,
            root=root,
            workflow_path=workflow,
            workflow_release_sha256=release_sha256,
            policy_set_identity="f" * 64,
        )
