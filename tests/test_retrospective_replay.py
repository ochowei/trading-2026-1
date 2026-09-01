import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from trading.core.sleeve_engine import CandidateTrade, CanonicalSleeveInput, ExecutionCostPolicy
from trading.workflow import retrospective_replay as replay_module
from trading.workflow.retrospective_replay import (
    run_fixed_calendar_retrospective_replay,
    validate_retrospective_replay_artifact,
)


class _Calendar:
    def __init__(self, sessions: tuple[date, ...]) -> None:
        self.sessions = sessions

    def sessions_in_range(self, _start: date, _end: date) -> pd.DatetimeIndex:
        return pd.DatetimeIndex(self.sessions)


class _Registry:
    plan = SimpleNamespace(
        evidence_role="fixed-calendar-retrospective",
        study_identity=SimpleNamespace(study_path=""),
        experiment_family="family",
    )

    def __init__(self, _path: Path) -> None:
        pass

    def historical_plan(self, _plan_id: str):
        return self.plan

    def historical_screen(self, _plan_id: str):
        return SimpleNamespace(passed=True, disposition="retrospectively-supported")


class _TrialRegistry:
    def __init__(self, _path: Path) -> None:
        pass

    def read(self) -> dict:
        return {"trials": []}


def _fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = tmp_path / "repo"
    study = root / "workflows" / "example--v009" / "work" / "studies" / "example--s001"
    study.mkdir(parents=True)
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
        replay_start=date(2025, 1, 1),
        replay_end=date(2025, 12, 31),
        qualification_registry_identity="state/qualification-registry.json",
        trial_registry_identity="results/registries/trial_registry.json",
        study_identity=identity,
        workflow_path=study.parents[2],
        research_identity="family/candidate",
        selected_trial_id="trial-selected",
        base_cost_policy=ExecutionCostPolicy(5, 5, 1),
        stress_cost_policy=ExecutionCostPolicy(20, 20, 2),
        stress_drawdown_limit="0.20",
        policy_set_identity="f" * 64,
    )
    _Registry.plan = SimpleNamespace(
        evidence_role="fixed-calendar-retrospective",
        study_identity=SimpleNamespace(study_path=relative_study),
        experiment_family="family",
    )
    qualification_registry = root / spec.qualification_registry_identity
    trial_registry = root / spec.trial_registry_identity
    manifest = root / "results/research-trials/family/candidate/2025-manifest.json"
    challenge = root / "results/workflows/example--v009/example--s001/challenges/manifest.json"
    for path, payload in (
        (qualification_registry, {"registry": "qualification"}),
        (trial_registry, {"registry": "trials"}),
        (manifest, {"snapshot": "2025"}),
        (challenge, {"challenges": "passing"}),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    sessions = tuple(date(2025, 1, day) for day in range(2, 27))
    prices = pd.Series([100.0] * len(sessions), index=pd.DatetimeIndex(sessions))
    candidates = tuple(
        CandidateTrade(
            signal_date=sessions[index],
            entry_date=sessions[index],
            entry_price=100.0,
            exit_date=sessions[index + 1],
            exit_price=103.0,
            exit_type="signal",
        )
        for index in range(0, 24, 2)
    )
    sleeve_input = CanonicalSleeveInput(
        calendar=tuple(pd.Timestamp(item) for item in sessions),
        close_prices=prices,
        candidates=candidates,
        raw_signals=tuple(item.signal_date for item in candidates),
        legacy_signals=tuple(item.signal_date for item in candidates),
        legacy_candidates=candidates,
    )
    monkeypatch.setattr(replay_module, "load_frozen_study_qualification_spec", lambda _path: spec)
    monkeypatch.setattr(replay_module, "QualificationRegistry", _Registry)
    monkeypatch.setattr(replay_module, "ExperimentTrialRegistry", _TrialRegistry)
    monkeypatch.setattr(replay_module, "PrimaryUSSessionCalendar", lambda: _Calendar(sessions))
    monkeypatch.setattr(replay_module, "_validate_challenge_manifest", lambda *_args: True)
    monkeypatch.setattr(replay_module, "_verify_snapshot_cutoff", lambda **_kwargs: None)
    monkeypatch.setattr(
        replay_module,
        "_verify_formal_snapshot_observation",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        replay_module,
        "_load_trial_input",
        lambda *_args, **_kwargs: (
            "trial-selected",
            "family",
            sleeve_input,
            "1" * 64,
            date(2025, 12, 31),
        ),
    )
    return SimpleNamespace(
        root=root,
        study=study,
        spec=spec,
        qualification_registry=qualification_registry,
        trial_registry=trial_registry,
        manifest=manifest,
        challenge=challenge,
        output=root / "results/workflows/example--v009/example--s001/replay",
    )


def _run(fixture, *, dry_run: bool):
    return run_fixed_calendar_retrospective_replay(
        study_path=fixture.study,
        plan_id="plan-1",
        selected_manifest_path=fixture.manifest,
        challenge_manifest_path=fixture.challenge,
        qualification_registry_path=fixture.qualification_registry,
        trial_registry_path=fixture.trial_registry,
        research_data_store=object(),
        definition_store=object(),
        output_root=fixture.output,
        dry_run=dry_run,
    )


def test_fixed_replay_dry_run_has_zero_publication_mutation(tmp_path, monkeypatch) -> None:
    fixture = _fixture(tmp_path, monkeypatch)

    publication = _run(fixture, dry_run=True)

    assert publication.passed is True
    assert publication.dry_run is True
    assert not fixture.output.exists()


def test_fixed_replay_publishes_atomically_and_retries_idempotently(tmp_path, monkeypatch) -> None:
    fixture = _fixture(tmp_path, monkeypatch)

    first = _run(fixture, dry_run=False)
    second = _run(fixture, dry_run=False)

    assert first == second
    assert {item.name for item in first.directory.iterdir()} == {"REPLAY.json", "MANIFEST.json"}
    assert validate_retrospective_replay_artifact(fixture.study, first.replay_path) is True


def test_fixed_replay_rejects_publication_collision(tmp_path, monkeypatch) -> None:
    fixture = _fixture(tmp_path, monkeypatch)
    publication = _run(fixture, dry_run=False)
    publication.replay_path.write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="publication collision"):
        _run(fixture, dry_run=False)


def test_fixed_replay_failure_leaves_no_partial_publication(tmp_path, monkeypatch) -> None:
    fixture = _fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(
        replay_module.os, "rename", lambda *_args: (_ for _ in ()).throw(OSError("boom"))
    )

    with pytest.raises(OSError, match="boom"):
        _run(fixture, dry_run=False)

    visible = [item for item in fixture.output.iterdir() if item.is_dir()]
    assert visible == []
