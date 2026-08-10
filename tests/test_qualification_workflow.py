from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import pytest

from trading.core.qualification import (
    ForwardSelectionEpoch,
    build_historical_qualification_plan,
)
from trading.core.qualification_workflow import (
    register_forward_qualification_plan,
    run_registered_historical_screen,
)
from trading.core.sleeve_engine import CanonicalSleeveInput
from trading.research_data import (
    DefinitionBlobRef,
    ExperimentTrialDeclaration,
    ExperimentTrialRegistry,
    QualificationRegistry,
    ResearchDefinitionSnapshot,
)
from trading.research_data.qualification_registry import QualificationRegistryError


class _Strategy:
    def __init__(self, fingerprint: str) -> None:
        self.fingerprint = fingerprint

    def capture_research_definition(self, _store) -> ResearchDefinitionSnapshot:
        return ResearchDefinitionSnapshot(
            fingerprint=self.fingerprint,
            blob=DefinitionBlobRef(
                digest="d" * 64,
                byte_count=10,
                fingerprint=self.fingerprint,
            ),
        )

    def declare_experiment_trial(self) -> ExperimentTrialDeclaration:
        return ExperimentTrialDeclaration(family="SPY:forward-program")


def _empty_input() -> CanonicalSleeveInput:
    calendar = pd.bdate_range("2018-01-01", "2025-12-31")
    return CanonicalSleeveInput(
        calendar=tuple(calendar),
        close_prices=pd.Series(100.0, index=calendar),
        candidates=(),
        raw_signals=(),
        legacy_signals=(),
        legacy_candidates=(),
    )


def test_register_forward_plan_bounds_incomplete_legacy_history(
    tmp_path,
    monkeypatch,
) -> None:
    started_at = datetime(2026, 8, 10, 2, tzinfo=UTC)
    trial_path = tmp_path / "trial-registry.json"
    qualification_path = tmp_path / "qualification-registry.json"
    selected_fingerprint = "a" * 64
    baseline_fingerprint = "b" * 64
    registry = ExperimentTrialRegistry(trial_path)
    selected_id = registry.register_trial(
        "SPY:forward-program",
        selected_fingerprint,
        experiment_name="selected",
        registered_at=datetime(2026, 8, 9, tzinfo=UTC),
    )
    baseline_id = registry.register_trial(
        "SPY:forward-program",
        baseline_fingerprint,
        experiment_name="baseline",
        registered_at=datetime(2026, 8, 9, 1, tzinfo=UTC),
    )
    registry.seed_legacy(["unknown-old-trial"], seeded_at=datetime(2026, 8, 9, 2, tzinfo=UTC))
    monkeypatch.setattr(
        "trading.core.qualification_workflow.get_experiment",
        lambda _name: _Strategy(selected_fingerprint),
    )

    plan = register_forward_qualification_plan(
        experiment_name="selected",
        family_baseline_trial_id=baseline_id,
        evaluation_years=(2027, 2028, 2029, 2030, 2031),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        random_seed=17,
        random_samples=10,
        bootstrap_repetitions=20,
        bootstrap_block_sessions=5,
        qualification_registry_path=qualification_path,
        trial_registry_path=trial_path,
        now=lambda: started_at,
    )

    assert plan.forward_selection_epoch == ForwardSelectionEpoch(
        started_at=started_at,
        selected_trial_id=selected_id,
        included_trial_ids=tuple(sorted((selected_id, baseline_id))),
        prior_selection_history_incomplete=True,
    )
    assert plan.evaluation_sessions[0].year == 2027
    assert QualificationRegistry(qualification_path).historical_plan(plan.plan_id) == plan
    assert (
        QualificationRegistry(
            qualification_path,
            now=lambda: datetime(2026, 8, 11, tzinfo=UTC),
        ).register_historical_plan(plan)
        == plan.plan_id
    )
    with pytest.raises(QualificationRegistryError, match="open forward"):
        QualificationRegistry(
            qualification_path,
            now=lambda: started_at,
        ).register_historical_plan(replace(plan, plan_id="another-forward-plan"))


def test_registered_screen_recomputes_and_records_future_only_evidence(
    tmp_path,
    monkeypatch,
) -> None:
    epoch_start = datetime(2020, 12, 31, 20, tzinfo=UTC)
    evaluated_at = datetime(2026, 1, 2, 20, tzinfo=UTC)
    trial_path = tmp_path / "trial-registry.json"
    qualification_path = tmp_path / "qualification-registry.json"
    registry = ExperimentTrialRegistry(trial_path)
    selected_id = registry.register_trial(
        "SPY:forward-program",
        "a" * 64,
        experiment_name="selected",
        registered_at=datetime(2020, 12, 30, tzinfo=UTC),
    )
    baseline_id = registry.register_trial(
        "SPY:forward-program",
        "b" * 64,
        experiment_name="baseline",
        registered_at=datetime(2020, 12, 30, 1, tzinfo=UTC),
    )
    registry.seed_legacy(["unknown-old-trial"], seeded_at=datetime(2020, 12, 30, 2, tzinfo=UTC))
    registry.record_observation(
        "SPY:forward-program",
        "a" * 64,
        snapshot_id="snapshot-selected",
        result_path="selected.json",
        validity_status="valid",
        observed_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    registry.record_observation(
        "SPY:forward-program",
        "b" * 64,
        snapshot_id="snapshot-baseline",
        result_path="baseline.json",
        validity_status="valid",
        observed_at=datetime(2026, 1, 1, 1, tzinfo=UTC),
    )
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2018-01-01", "2025-12-31"))
    plan = build_historical_qualification_plan(
        experiment_family="SPY:forward-program",
        definition_fingerprint="a" * 64,
        sessions=sessions,
        evaluation_years=(2021, 2022, 2023, 2024, 2025),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id=baseline_id,
        random_seed=17,
        random_samples=10,
        bootstrap_repetitions=20,
        bootstrap_block_sessions=5,
        created_at=epoch_start,
        forward_selection_epoch=ForwardSelectionEpoch(
            started_at=epoch_start,
            selected_trial_id=selected_id,
            included_trial_ids=tuple(sorted((selected_id, baseline_id))),
            prior_selection_history_incomplete=True,
        ),
    )
    QualificationRegistry(
        qualification_path,
        now=lambda: epoch_start,
    ).register_historical_plan(plan)
    inputs = {"selected": _empty_input(), "baseline": _empty_input()}

    def load_trial_input(name: str, _manifest: Path, **_kwargs):
        if name == "selected":
            return (
                selected_id,
                plan.experiment_family,
                inputs[name],
                "snapshot-selected",
                plan.evaluation_sessions[-1],
            )
        return (
            baseline_id,
            plan.experiment_family,
            inputs[name],
            "snapshot-baseline",
            plan.evaluation_sessions[-1],
        )

    monkeypatch.setattr(
        "trading.core.qualification_workflow._load_trial_input",
        load_trial_input,
    )

    execution = run_registered_historical_screen(
        plan_id=plan.plan_id,
        trial_manifests={
            "selected": Path("selected.snapshot.json"),
            "baseline": Path("baseline.snapshot.json"),
        },
        qualification_registry_path=qualification_path,
        trial_registry_path=trial_path,
        research_data_store=object(),
        definition_store=object(),
        now=lambda: evaluated_at,
    )

    assert execution.event_id == f"historical-screen:{plan.plan_id}"
    assert execution.screen.passed is False
    state = QualificationRegistry(qualification_path).read()
    assert [event["event_type"] for event in state["events"]] == [
        "historical_plan",
        "historical_screen",
    ]


def test_forward_screen_rejects_trial_added_after_epoch(tmp_path) -> None:
    epoch_start = datetime(2020, 12, 31, 20, tzinfo=UTC)
    registry = ExperimentTrialRegistry(tmp_path / "trial-registry.json")
    selected_id = registry.register_trial(
        "SPY:forward-program",
        "a" * 64,
        experiment_name="selected",
        registered_at=datetime(2020, 12, 30, tzinfo=UTC),
    )
    baseline_id = registry.register_trial(
        "SPY:forward-program",
        "b" * 64,
        experiment_name="baseline",
        registered_at=datetime(2020, 12, 30, 1, tzinfo=UTC),
    )
    registry.register_trial(
        "SPY:forward-program",
        "c" * 64,
        experiment_name="late-trial",
        registered_at=datetime(2021, 1, 2, tzinfo=UTC),
    )
    assert selected_id != baseline_id

    from trading.core.qualification_workflow import _registered_family_trial_ids

    try:
        _registered_family_trial_ids(
            registry.read(),
            experiment_family="SPY:forward-program",
            epoch_start=epoch_start,
        )
    except ValueError as exc:
        assert "after the epoch" in str(exc)
    else:
        raise AssertionError("late trial should invalidate the forward selection epoch")
