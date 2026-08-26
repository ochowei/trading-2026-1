import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from trading.core.qualification import (
    ForwardSelectionEpoch,
    StudyQualificationIdentity,
    build_historical_qualification_plan,
)
from trading.core.qualification_transaction import (
    publish_qualification_plan_transaction,
    recover_qualification_plan_transaction,
)
from trading.core.qualification_workflow import (
    _verify_formal_snapshot_observation,
    _verify_snapshot_cutoff,
    register_forward_qualification_plan,
    run_registered_historical_screen,
)
from trading.core.sleeve_engine import CanonicalSleeveInput
from trading.core.study_qualification import compile_study_qualification_plan
from trading.research_data import (
    DefinitionBlobRef,
    ExperimentTrialDeclaration,
    ExperimentTrialRegistry,
    OutcomeFreeTrialRegistration,
    QualificationRegistry,
    ResearchDefinitionSnapshot,
)
from trading.research_data.trial_registry import formal_trial_id


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


class _WorkflowStrategy(_Strategy):
    def capture_research_definition(
        self,
        _store,
        policy_set,
    ) -> ResearchDefinitionSnapshot:
        assert policy_set == "policy-set"
        return super().capture_research_definition(_store)

    def run_with_bundle(self, _bundle):
        return {"canonical_sleeve_input": _empty_input()}


@dataclass(frozen=True)
class _StudySpecStub:
    study_identity: StudyQualificationIdentity


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


def _register_retrospective_screen_fixture(tmp_path, monkeypatch):
    frozen_at = datetime(2026, 1, 2, 20, tzinfo=UTC)
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
    definition_registry = type(
        "DefinitionRegistry",
        (),
        {"load": lambda _self, _identity: _WorkflowStrategy("a" * 64)},
    )
    monkeypatch.setattr(
        "trading.core.qualification_workflow.ResearchDefinitionRegistry",
        definition_registry,
    )
    monkeypatch.setattr(
        "trading.core.qualification_workflow.resolve_workflow_policy_set",
        lambda _path: "policy-set",
    )
    plan = register_forward_qualification_plan(
        research_identity="spy-forward/selected",
        workflow_path=Path("workflows/strategy-forward-replication-research--v006"),
        family_baseline_trial_id=baseline_id,
        evaluation_years=(2021, 2022, 2023, 2024, 2025),
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
        now=lambda: frozen_at,
        evidence_role="retrospective-confirmatory",
        evidence_classification="provenance-unknown",
        evidence_justification="Retrospective checkpoint regression.",
        trial_history_complete=False,
    )
    inputs = {"selected": _empty_input(), "baseline": _empty_input()}

    def load_trial_input(name: str, _manifest: Path, **_kwargs):
        trial_id = selected_id if name == "selected" else baseline_id
        snapshot_id = "snapshot-selected" if name == "selected" else "snapshot-baseline"
        return (
            trial_id,
            plan.experiment_family,
            inputs[name],
            snapshot_id,
            plan.evaluation_sessions[-1],
        )

    monkeypatch.setattr(
        "trading.core.qualification_workflow._load_trial_input",
        load_trial_input,
    )
    return plan, registry, trial_path, qualification_path


def test_register_forward_plan_rejects_legacy_experiment_without_writes(tmp_path) -> None:
    trial_path = tmp_path / "trial-registry.json"
    qualification_path = tmp_path / "qualification-registry.json"
    with pytest.raises(ValueError, match="legacy experiment qualification is retired"):
        register_forward_qualification_plan(
            experiment_name="selected",
            family_baseline_trial_id="baseline-trial",
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
        )

    assert not qualification_path.exists()
    assert not trial_path.exists()


def test_cross_registry_plan_transaction_recovers_after_second_write_failure(tmp_path) -> None:
    started_at = datetime(2026, 8, 15, 2, tzinfo=UTC)
    registrations = (
        OutcomeFreeTrialRegistration("SPY:transaction", "a" * 64, "candidate"),
        OutcomeFreeTrialRegistration("SPY:transaction", "b" * 64, "baseline"),
    )
    candidate_id = formal_trial_id("SPY:transaction", "a" * 64)
    baseline_id = formal_trial_id("SPY:transaction", "b" * 64)
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2024-01-01", "2031-12-31"))
    plan = build_historical_qualification_plan(
        experiment_family="SPY:transaction",
        definition_fingerprint="a" * 64,
        sessions=sessions,
        evaluation_years=(2027, 2028, 2029, 2030, 2031),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id=baseline_id,
        random_seed=7,
        random_samples=10,
        bootstrap_repetitions=10,
        bootstrap_block_sessions=5,
        created_at=started_at,
        forward_selection_epoch=ForwardSelectionEpoch(
            started_at=started_at,
            selected_trial_id=candidate_id,
            included_trial_ids=tuple(sorted((candidate_id, baseline_id))),
            prior_selection_history_incomplete=True,
        ),
    )
    trial_path = tmp_path / "trials.json"
    qualification_path = tmp_path / "qualification.json"

    def fail_after_trial_commit() -> None:
        raise RuntimeError("injected second-write fault")

    with pytest.raises(RuntimeError, match="second-write fault"):
        publish_qualification_plan_transaction(
            plan=plan,
            registrations=registrations,
            registered_at=started_at,
            trial_registry_path=trial_path,
            qualification_registry_path=qualification_path,
            after_trial_commit=fail_after_trial_commit,
        )

    assert len(ExperimentTrialRegistry(trial_path).read()["trials"]) == 2
    assert not qualification_path.exists()
    assert recover_qualification_plan_transaction(qualification_path) == plan
    assert QualificationRegistry(qualification_path).historical_plan(plan.plan_id) == plan
    assert recover_qualification_plan_transaction(qualification_path) is None


def test_cross_registry_plan_transaction_serializes_concurrent_retries(tmp_path) -> None:
    started_at = datetime(2026, 8, 15, 3, tzinfo=UTC)
    registrations = (
        OutcomeFreeTrialRegistration("SPY:concurrent", "a" * 64, "candidate"),
        OutcomeFreeTrialRegistration("SPY:concurrent", "b" * 64, "baseline"),
    )
    candidate_id = formal_trial_id("SPY:concurrent", "a" * 64)
    baseline_id = formal_trial_id("SPY:concurrent", "b" * 64)
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2024-01-01", "2031-12-31"))
    plan = build_historical_qualification_plan(
        experiment_family="SPY:concurrent",
        definition_fingerprint="a" * 64,
        sessions=sessions,
        evaluation_years=(2027, 2028, 2029, 2030, 2031),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id=baseline_id,
        random_seed=7,
        random_samples=10,
        bootstrap_repetitions=10,
        bootstrap_block_sessions=5,
        created_at=started_at,
        forward_selection_epoch=ForwardSelectionEpoch(
            started_at=started_at,
            selected_trial_id=candidate_id,
            included_trial_ids=tuple(sorted((candidate_id, baseline_id))),
            prior_selection_history_incomplete=True,
        ),
    )
    trial_path = tmp_path / "trials.json"
    qualification_path = tmp_path / "qualification.json"

    def publish() -> tuple[str, ...]:
        return publish_qualification_plan_transaction(
            plan=plan,
            registrations=registrations,
            registered_at=started_at,
            trial_registry_path=trial_path,
            qualification_registry_path=qualification_path,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = tuple(executor.map(lambda _item: publish(), range(2)))

    assert results[0] == results[1]
    state = QualificationRegistry(qualification_path).read()
    assert [event["event_id"] for event in state["events"]] == [f"historical-plan:{plan.plan_id}"]


def test_cross_registry_plan_transaction_blocks_concurrent_family_mutation(tmp_path) -> None:
    started_at = datetime(2026, 8, 15, 3, tzinfo=UTC)
    registrations = (
        OutcomeFreeTrialRegistration("SPY:locked-family", "a" * 64, "candidate"),
        OutcomeFreeTrialRegistration("SPY:locked-family", "b" * 64, "baseline"),
    )
    candidate_id = formal_trial_id("SPY:locked-family", "a" * 64)
    baseline_id = formal_trial_id("SPY:locked-family", "b" * 64)
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2024-01-01", "2031-12-31"))
    plan = build_historical_qualification_plan(
        experiment_family="SPY:locked-family",
        definition_fingerprint="a" * 64,
        sessions=sessions,
        evaluation_years=(2027, 2028, 2029, 2030, 2031),
        maximum_holding_sessions=1,
        execution_lag_sessions=1,
        dependency_sessions=2,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        family_baseline_trial_id=baseline_id,
        random_seed=7,
        random_samples=10,
        bootstrap_repetitions=10,
        bootstrap_block_sessions=5,
        created_at=started_at,
        forward_selection_epoch=ForwardSelectionEpoch(
            started_at=started_at,
            selected_trial_id=candidate_id,
            included_trial_ids=tuple(sorted((candidate_id, baseline_id))),
            prior_selection_history_incomplete=False,
        ),
    )
    trial_path = tmp_path / "trials.json"
    qualification_path = tmp_path / "qualification.json"
    callback_entered = threading.Event()
    release_callback = threading.Event()
    mutation_finished = threading.Event()

    def hold_plan_commit() -> None:
        callback_entered.set()
        assert release_callback.wait(timeout=5)

    def publish() -> tuple[str, ...]:
        return publish_qualification_plan_transaction(
            plan=plan,
            registrations=registrations,
            registered_at=started_at,
            trial_registry_path=trial_path,
            qualification_registry_path=qualification_path,
            after_trial_commit=hold_plan_commit,
        )

    def register_later_family_member() -> str:
        trial_id = ExperimentTrialRegistry(trial_path).register_trial(
            "SPY:locked-family",
            "c" * 64,
            experiment_name="later-member",
            registered_at=started_at.replace(second=1),
        )
        mutation_finished.set()
        return trial_id

    with ThreadPoolExecutor(max_workers=2) as executor:
        plan_future = executor.submit(publish)
        assert callback_entered.wait(timeout=5)
        mutation_future = executor.submit(register_later_family_member)
        assert not mutation_finished.wait(timeout=0.1)
        release_callback.set()
        assert plan_future.result(timeout=5) == tuple(sorted((candidate_id, baseline_id)))
        extra_id = mutation_future.result(timeout=5)

    assert QualificationRegistry(qualification_path).historical_plan(plan.plan_id) == plan
    assert extra_id not in plan.forward_selection_epoch.included_trial_ids


def test_public_study_registration_retry_recovers_exact_pending_operation(
    tmp_path,
    monkeypatch,
) -> None:
    study = tmp_path / "workflows" / "example--v001" / "work" / "studies" / "x--s001"
    study.mkdir(parents=True)
    relative_study = study.relative_to(tmp_path).as_posix()
    trial_path = tmp_path / "trials.json"
    qualification_path = tmp_path / "qualification.json"
    started_at = datetime(2026, 8, 15, 3, tzinfo=UTC)
    candidate_id = formal_trial_id("SPY:retry", "a" * 64)
    baseline_id = formal_trial_id("SPY:retry", "b" * 64)
    identity = StudyQualificationIdentity(
        study_path=relative_study,
        preregistration_sha256="1" * 64,
        plan_sha256="2" * 64,
        candidate_freeze_sha256="3" * 64,
        qualification_spec_sha256="4" * 64,
        workflow_release_sha256="5" * 64,
    )
    spec = _StudySpecStub(study_identity=identity)
    sessions = tuple(timestamp.date() for timestamp in pd.bdate_range("2024-01-01", "2031-12-31"))
    compile_calls = 0

    monkeypatch.setattr(
        "trading.core.study_qualification.load_frozen_study_qualification_spec",
        lambda _study: spec,
    )
    monkeypatch.setattr(
        "trading.core.study_qualification._verify_frozen_definitions",
        lambda _spec, **_kwargs: None,
    )

    def fail_first_compile(approved_spec, **_kwargs):
        nonlocal compile_calls
        compile_calls += 1
        approved_identity = approved_spec.study_identity
        plan = build_historical_qualification_plan(
            experiment_family="SPY:retry",
            definition_fingerprint="a" * 64,
            sessions=sessions,
            evaluation_years=(2027, 2028, 2029, 2030, 2031),
            maximum_holding_sessions=1,
            execution_lag_sessions=1,
            dependency_sessions=2,
            embargo_sessions=1,
            stress_drawdown_limit="0.20",
            family_baseline_trial_id=baseline_id,
            random_seed=7,
            random_samples=10,
            bootstrap_repetitions=10,
            bootstrap_block_sessions=5,
            created_at=started_at,
            forward_selection_epoch=ForwardSelectionEpoch(
                started_at=started_at,
                selected_trial_id=candidate_id,
                included_trial_ids=tuple(sorted((candidate_id, baseline_id))),
                prior_selection_history_incomplete=False,
            ),
            study_identity=approved_identity,
        )
        publish_qualification_plan_transaction(
            plan=plan,
            registrations=(
                OutcomeFreeTrialRegistration("SPY:retry", "a" * 64, "candidate"),
                OutcomeFreeTrialRegistration("SPY:retry", "b" * 64, "baseline"),
            ),
            registered_at=started_at,
            trial_registry_path=trial_path,
            qualification_registry_path=qualification_path,
            after_trial_commit=lambda: (_ for _ in ()).throw(RuntimeError("injected")),
        )

    monkeypatch.setattr(
        "trading.core.study_qualification._compile_spec",
        fail_first_compile,
    )
    clock_calls = iter((started_at, started_at.replace(minute=5)))
    kwargs = {
        "study_path": study,
        "qualification_registry_path": qualification_path,
        "trial_registry_path": trial_path,
        "dry_run": False,
        "approved_by": "reviewer@example.com",
        "contamination_declaration": "Historical access cannot be excluded.",
        "now": lambda: next(clock_calls),
    }

    with pytest.raises(RuntimeError, match="injected"):
        compile_study_qualification_plan(**kwargs)

    recovered = compile_study_qualification_plan(**kwargs)

    assert compile_calls == 1
    assert recovered.study_identity is not None
    assert recovered.study_identity.operation_approved_by == "reviewer@example.com"
    assert recovered.study_identity.operation_approved_at == started_at
    assert recovered.study_identity.contamination_declaration == (
        "Historical access cannot be excluded."
    )
    assert recovered.study_identity.trial_registry_path == str(trial_path.resolve())
    assert recovered.study_identity.qualification_registry_path == str(qualification_path.resolve())
    assert QualificationRegistry(qualification_path).historical_plan(recovered.plan_id) == recovered

    with pytest.raises(ValueError, match="different operation"):
        compile_study_qualification_plan(**{**kwargs, "approved_by": "other@example.com"})
    with pytest.raises(ValueError, match="different operation"):
        compile_study_qualification_plan(
            **{**kwargs, "contamination_declaration": "Different declaration."}
        )
    with pytest.raises(ValueError, match="different operation"):
        compile_study_qualification_plan(
            **{**kwargs, "trial_registry_path": tmp_path / "other-trials.json"}
        )


def test_public_study_registration_reloads_freeze_after_serialization_lock(
    tmp_path,
    monkeypatch,
) -> None:
    study = tmp_path / "workflows" / "example--v001" / "work" / "studies" / "x--s001"
    study.mkdir(parents=True)
    identity = StudyQualificationIdentity(
        study_path=study.relative_to(tmp_path).as_posix(),
        preregistration_sha256="1" * 64,
        plan_sha256="2" * 64,
        candidate_freeze_sha256="3" * 64,
        qualification_spec_sha256="4" * 64,
        workflow_release_sha256="5" * 64,
    )
    spec = _StudySpecStub(study_identity=identity)
    loads = 0

    def load_after_interleaving(_study):
        nonlocal loads
        loads += 1
        if loads == 1:
            return spec
        raise ValueError("candidate freeze disappeared while waiting")

    monkeypatch.setattr(
        "trading.core.study_qualification.load_frozen_study_qualification_spec",
        load_after_interleaving,
    )
    monkeypatch.setattr(
        "trading.core.study_qualification._verify_frozen_definitions",
        lambda _spec, **_kwargs: None,
    )

    with pytest.raises(ValueError, match="candidate freeze disappeared"):
        compile_study_qualification_plan(
            study_path=study,
            qualification_registry_path=tmp_path / "qualification.json",
            trial_registry_path=tmp_path / "trials.json",
            dry_run=False,
            approved_by="reviewer@example.com",
            contamination_declaration="Historical access cannot be excluded.",
        )

    assert loads == 2


def test_register_plan_resolves_workflow_native_identity_without_legacy_registry(
    tmp_path,
    monkeypatch,
) -> None:
    started_at = datetime(2026, 8, 10, 2, tzinfo=UTC)
    trial_path = tmp_path / "trial-registry.json"
    selected_fingerprint = "a" * 64
    baseline_fingerprint = "b" * 64
    registry = ExperimentTrialRegistry(trial_path)
    selected_id = registry.register_trial(
        "SPY:forward-program",
        selected_fingerprint,
        experiment_name="spy-forward/selected",
        registered_at=datetime(2026, 8, 9, tzinfo=UTC),
    )
    baseline_id = registry.register_trial(
        "SPY:forward-program",
        baseline_fingerprint,
        experiment_name="spy-forward/baseline",
        registered_at=datetime(2026, 8, 9, 1, tzinfo=UTC),
    )
    definition_registry = type(
        "DefinitionRegistry",
        (),
        {"load": lambda _self, identity: _WorkflowStrategy(selected_fingerprint)},
    )
    monkeypatch.setattr(
        "trading.core.qualification_workflow.ResearchDefinitionRegistry",
        definition_registry,
    )
    monkeypatch.setattr(
        "trading.core.qualification_workflow.resolve_workflow_policy_set",
        lambda _path: "policy-set",
    )
    plan = register_forward_qualification_plan(
        research_identity="spy-forward/selected",
        workflow_path=tmp_path / "released-workflow",
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
        qualification_registry_path=tmp_path / "qualification-registry.json",
        trial_registry_path=trial_path,
        now=lambda: started_at,
        evidence_classification="verified-clean",
        evidence_justification="Append-only audit proves this future period is clean.",
        trial_history_complete=True,
    )

    assert plan.forward_selection_epoch is not None
    assert plan.forward_selection_epoch.selected_trial_id == selected_id
    assert plan.evidence_audit is not None
    assert plan.evidence_audit.classification == "verified-clean"


def test_complete_family_dry_run_then_atomic_clean_calendar_registration(
    tmp_path,
    monkeypatch,
) -> None:
    started_at = datetime(2026, 8, 15, 2, tzinfo=UTC)
    trial_path = tmp_path / "trial-registry.json"
    qualification_path = tmp_path / "qualification-registry.json"
    identities = tuple(f"spy-forward/trial-{letter}" for letter in "abcdef")
    fingerprints = {
        identity: letter * 64 for identity, letter in zip(identities, "abcdef", strict=True)
    }
    source_paths = {}
    for identity in identities:
        path = tmp_path / "definitions" / identity.replace("/", "--") / "definition.py"
        path.parent.mkdir(parents=True)
        path.write_text(f"# {identity}\n", encoding="utf-8")
        source_paths[identity] = path
    registry = ExperimentTrialRegistry(trial_path)
    selected_id = registry.register_trial(
        "SPY:forward-program",
        fingerprints[identities[0]],
        experiment_name=identities[0],
        registered_at=datetime(2026, 8, 13, 8, tzinfo=UTC),
    )
    baseline_id = registry.register_trial(
        "SPY:forward-program",
        fingerprints[identities[1]],
        experiment_name=identities[1],
        registered_at=datetime(2026, 8, 13, 9, tzinfo=UTC),
    )
    registry.seed_legacy(["unknown-old-trial"], seeded_at=datetime(2026, 8, 13, 10, tzinfo=UTC))

    definition_registry = type(
        "DefinitionRegistry",
        (),
        {
            "load": lambda _self, identity: _WorkflowStrategy(fingerprints[identity]),
            "resolve": lambda _self, identity: source_paths[identity],
        },
    )
    monkeypatch.setattr(
        "trading.core.qualification_workflow.ResearchDefinitionRegistry",
        definition_registry,
    )
    monkeypatch.setattr(
        "trading.core.qualification_workflow.resolve_workflow_policy_set",
        lambda _path: "policy-set",
    )

    kwargs = {
        "research_identity": identities[0],
        "workflow_path": tmp_path / "released-workflow",
        "family_baseline_trial_id": baseline_id,
        "evaluation_years": (2027, 2028, 2029, 2030, 2031),
        "development_years": tuple(range(2015, 2026)),
        "warmup_start": date(2014, 1, 1),
        "warmup_end": date(2014, 12, 31),
        "quarantine_years": (2026,),
        "maximum_holding_sessions": 1,
        "execution_lag_sessions": 1,
        "dependency_sessions": 2,
        "embargo_sessions": 1,
        "stress_drawdown_limit": "0.20",
        "random_seed": 17,
        "random_samples": 10,
        "bootstrap_repetitions": 20,
        "bootstrap_block_sessions": 5,
        "qualification_registry_path": qualification_path,
        "trial_registry_path": trial_path,
        "now": lambda: started_at,
        "evidence_classification": "verified-clean",
        "evidence_justification": "Append-only audit reserves the future folds.",
        "trial_history_complete": True,
        "family_research_identities": identities,
        "family_source_sha256": {
            identity: hashlib.sha256(source_paths[identity].read_bytes()).hexdigest()
            for identity in identities
        },
        "maximum_family_trials": 6,
        "study_identity": StudyQualificationIdentity(
            study_path="workflows/example--v004/work/studies/example--s001",
            preregistration_sha256="1" * 64,
            plan_sha256="2" * 64,
            candidate_freeze_sha256="3" * 64,
            qualification_spec_sha256=None,
            workflow_release_sha256="4" * 64,
        ),
    }

    preview = register_forward_qualification_plan(**kwargs, dry_run=True)

    assert len(registry.read()["trials"]) == 3  # two formal identities plus one legacy disclosure
    assert not qualification_path.exists()
    assert preview.forward_selection_epoch is not None
    assert len(preview.forward_selection_epoch.included_trial_ids) == 6
    assert preview.forward_selection_epoch.prior_selection_history_incomplete is True

    plan = register_forward_qualification_plan(**kwargs)

    formal_trials = [item for item in registry.read()["trials"] if item["legacy"] is False]
    assert len(formal_trials) == 6
    assert all(item["observations"] == [] for item in formal_trials[2:])
    assert {item["first_registered_at"] for item in formal_trials[2:]} == {"2026-08-15T02:00:00Z"}
    assert plan.forward_selection_epoch is not None
    assert plan.forward_selection_epoch.selected_trial_id == selected_id
    assert QualificationRegistry(qualification_path).historical_plan(plan.plan_id) == plan


def test_register_retrospective_plan_uses_explicit_role_calendar(tmp_path, monkeypatch) -> None:
    started_at = datetime(2026, 8, 13, 10, tzinfo=UTC)
    trial_path = tmp_path / "trial-registry.json"
    selected_fingerprint = "a" * 64
    baseline_fingerprint = "b" * 64
    registry = ExperimentTrialRegistry(trial_path)
    registry.register_trial(
        "SPY:forward-program",
        selected_fingerprint,
        experiment_name="selected",
        registered_at=datetime(2026, 8, 13, 8, tzinfo=UTC),
    )
    baseline_id = registry.register_trial(
        "SPY:forward-program",
        baseline_fingerprint,
        experiment_name="baseline",
        registered_at=datetime(2026, 8, 13, 8, 1, tzinfo=UTC),
    )
    definition_registry = type(
        "DefinitionRegistry",
        (),
        {"load": lambda _self, _identity: _WorkflowStrategy(selected_fingerprint)},
    )
    monkeypatch.setattr(
        "trading.core.qualification_workflow.ResearchDefinitionRegistry",
        definition_registry,
    )
    monkeypatch.setattr(
        "trading.core.qualification_workflow.resolve_workflow_policy_set",
        lambda _path: "policy-set",
    )

    plan = register_forward_qualification_plan(
        research_identity="spy-forward/selected",
        workflow_path=Path("workflows/strategy-forward-replication-research--v005"),
        family_baseline_trial_id=baseline_id,
        evaluation_years=(2010, 2011, 2012, 2013, 2014),
        development_years=tuple(range(2015, 2026)),
        warmup_start=date(2009, 1, 1),
        warmup_end=date(2009, 12, 31),
        maximum_holding_sessions=20,
        execution_lag_sessions=1,
        dependency_sessions=21,
        embargo_sessions=1,
        stress_drawdown_limit="0.20",
        random_seed=20260813,
        random_samples=10,
        bootstrap_repetitions=20,
        bootstrap_block_sessions=5,
        qualification_registry_path=tmp_path / "qualification-registry.json",
        trial_registry_path=trial_path,
        now=lambda: started_at,
        evidence_role="retrospective-confirmatory",
        evidence_classification="provenance-unknown",
        evidence_justification="Legacy selection provenance is incomplete.",
        trial_history_complete=False,
    )

    assert plan.development_years == tuple(range(2015, 2026))
    assert plan.role_calendar is not None
    assert plan.role_calendar.warmup_sessions[0].year == 2009
    assert plan.role_calendar.evaluation_sessions == plan.evaluation_sessions


def test_register_plan_rejects_partial_explicit_role_calendar(tmp_path, monkeypatch) -> None:
    trial_path = tmp_path / "trial-registry.json"
    selected_fingerprint = "a" * 64
    baseline_fingerprint = "b" * 64
    registry = ExperimentTrialRegistry(trial_path)
    registry.register_trial(
        "SPY:forward-program",
        selected_fingerprint,
        experiment_name="selected",
        registered_at=datetime(2026, 8, 13, 8, tzinfo=UTC),
    )
    baseline_id = registry.register_trial(
        "SPY:forward-program",
        baseline_fingerprint,
        experiment_name="baseline",
        registered_at=datetime(2026, 8, 13, 8, 1, tzinfo=UTC),
    )
    definition_registry = type(
        "DefinitionRegistry",
        (),
        {"load": lambda _self, _identity: _WorkflowStrategy(selected_fingerprint)},
    )
    monkeypatch.setattr(
        "trading.core.qualification_workflow.ResearchDefinitionRegistry",
        definition_registry,
    )
    monkeypatch.setattr(
        "trading.core.qualification_workflow.resolve_workflow_policy_set",
        lambda _path: "policy-set",
    )

    with pytest.raises(ValueError, match="requires development years and warmup bounds"):
        register_forward_qualification_plan(
            research_identity="spy-forward/selected",
            workflow_path=Path("workflows/strategy-forward-replication-research--v005"),
            family_baseline_trial_id=baseline_id,
            evaluation_years=(2010, 2011, 2012, 2013, 2014),
            development_years=(2015, 2016, 2017),
            maximum_holding_sessions=20,
            execution_lag_sessions=1,
            dependency_sessions=21,
            embargo_sessions=1,
            stress_drawdown_limit="0.20",
            random_seed=17,
            random_samples=10,
            bootstrap_repetitions=20,
            bootstrap_block_sessions=5,
            qualification_registry_path=tmp_path / "qualification-registry.json",
            trial_registry_path=trial_path,
            now=lambda: datetime(2026, 8, 13, 10, tzinfo=UTC),
            evidence_role="retrospective-confirmatory",
            evidence_classification="provenance-unknown",
            evidence_justification="Legacy selection provenance is incomplete.",
        )


def test_screen_input_replays_workflow_native_identity_without_legacy_registry(
    tmp_path,
    monkeypatch,
) -> None:
    from trading.core.qualification_workflow import _load_trial_input

    strategy = _WorkflowStrategy("a" * 64)
    definition = strategy.capture_research_definition(object(), "policy-set")
    definition_registry = type(
        "DefinitionRegistry",
        (),
        {"load": lambda _self, _identity: strategy},
    )
    monkeypatch.setattr(
        "trading.core.qualification_workflow.ResearchDefinitionRegistry",
        definition_registry,
    )
    monkeypatch.setattr(
        "trading.core.qualification_workflow.resolve_workflow_policy_set",
        lambda _path: "policy-set",
    )
    snapshot = SimpleNamespace(
        manifest=SimpleNamespace(
            definition=definition.blob,
            snapshot_id="snapshot-workflow-native",
            decision_time=SimpleNamespace(session=datetime(2031, 12, 31).date()),
        ),
        bundle={},
    )
    research_data_store = SimpleNamespace(load_snapshot=lambda _path: snapshot)

    trial_id, family, sleeve_input, snapshot_id, cutoff = _load_trial_input(
        "spy-forward/selected",
        Path("selected.snapshot.json"),
        research_data_store=research_data_store,
        definition_store=object(),
        workflow_path=tmp_path / "released-workflow",
    )

    assert len(trial_id) == 64
    assert family == "SPY:forward-program"
    assert isinstance(sleeve_input, CanonicalSleeveInput)
    assert sleeve_input.calendar == _empty_input().calendar
    assert snapshot_id == "snapshot-workflow-native"
    assert cutoff == datetime(2031, 12, 31).date()


def test_retrospective_registration_requires_released_contract_capability(tmp_path) -> None:
    from trading.core.qualification_workflow import _require_retrospective_workflow

    workflow_path = tmp_path / "workflow"
    workflow_path.mkdir()
    contract = workflow_path / "WORKFLOW.md"
    contract.write_text("# Workflow\n", encoding="utf-8")
    with pytest.raises(ValueError, match="does not authorize"):
        _require_retrospective_workflow(workflow_path)

    contract.write_text(
        "# Workflow\n\n### 3. Optional retrospective-confirmatory checkpoint\n",
        encoding="utf-8",
    )
    _require_retrospective_workflow(workflow_path)


def test_structured_evidence_contract_rejects_online_observation() -> None:
    state = {
        "trials": [
            {
                "trial_id": "trial-1",
                "observations": [
                    {
                        "event": "observation",
                        "snapshot_id": "snapshot-1",
                        "run_mode": "online",
                        "outcome_status": "succeeded",
                        "validity_status": "valid",
                        "observed_at": "2026-01-02T00:00:00.000000Z",
                    }
                ],
            }
        ]
    }
    with pytest.raises(ValueError, match="no valid formal observation"):
        _verify_formal_snapshot_observation(
            state,
            trial_id="trial-1",
            snapshot_id="snapshot-1",
            minimum_observation_date=date(2026, 1, 1),
            allowed_run_modes=frozenset({"offline"}),
        )

    state["trials"][0]["observations"][0]["run_mode"] = "offline"
    _verify_formal_snapshot_observation(
        state,
        trial_id="trial-1",
        snapshot_id="snapshot-1",
        minimum_observation_date=date(2026, 1, 1),
        allowed_run_modes=frozenset({"offline"}),
    )


def test_structured_evidence_contract_requires_exact_snapshot_cutoff() -> None:
    evaluation_end = date(2026, 12, 31)
    _verify_snapshot_cutoff(
        data_cutoff=evaluation_end,
        evaluation_end=evaluation_end,
        experiment_name="candidate",
        exact=True,
    )
    with pytest.raises(ValueError, match="cutoff differs"):
        _verify_snapshot_cutoff(
            data_cutoff=date(2027, 1, 4),
            evaluation_end=evaluation_end,
            experiment_name="candidate",
            exact=True,
        )

    _verify_snapshot_cutoff(
        data_cutoff=date(2027, 1, 4),
        evaluation_end=evaluation_end,
        experiment_name="legacy-candidate",
        exact=False,
    )


@pytest.mark.parametrize("retrospective", [False, True])
def test_registered_screen_recomputes_and_records_frozen_selection_boundary(
    tmp_path,
    monkeypatch,
    retrospective,
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
    plan_created_at = evaluated_at if retrospective else epoch_start
    if retrospective:
        definition_registry = type(
            "DefinitionRegistry",
            (),
            {"load": lambda _self, _identity: _WorkflowStrategy("a" * 64)},
        )
        monkeypatch.setattr(
            "trading.core.qualification_workflow.ResearchDefinitionRegistry",
            definition_registry,
        )
        monkeypatch.setattr(
            "trading.core.qualification_workflow.resolve_workflow_policy_set",
            lambda _path: "policy-set",
        )
        plan = register_forward_qualification_plan(
            research_identity="spy-forward/selected",
            workflow_path=Path("workflows/strategy-forward-replication-research--v006"),
            family_baseline_trial_id=baseline_id,
            evaluation_years=(2021, 2022, 2023, 2024, 2025),
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
            now=lambda: plan_created_at,
            evidence_role="retrospective-confirmatory",
            evidence_classification="provenance-unknown",
            evidence_justification="Retrospective checkpoint regression.",
            trial_history_complete=False,
        )
    else:
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
            created_at=plan_created_at,
            forward_selection_epoch=ForwardSelectionEpoch(
                started_at=plan_created_at,
                selected_trial_id=selected_id,
                included_trial_ids=tuple(sorted((selected_id, baseline_id))),
                prior_selection_history_incomplete=True,
            ),
        )
        QualificationRegistry(
            qualification_path,
            now=lambda: plan_created_at,
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


@pytest.mark.parametrize(
    ("corruption", "message"),
    [
        ("disclosure", "history disclosure"),
        ("family", "screen inputs must cover every"),
        ("missing-timestamp", "registration timestamps"),
        ("late-timestamp", "registered after the boundary"),
    ],
)
def test_registered_retrospective_screen_rejects_invalid_selection_boundary(
    tmp_path,
    monkeypatch,
    corruption,
    message,
) -> None:
    plan, registry, trial_path, qualification_path = _register_retrospective_screen_fixture(
        tmp_path,
        monkeypatch,
    )
    trial_state = registry.read()
    family_trials = [
        trial
        for trial in trial_state["trials"]
        if trial.get("experiment_family") == plan.experiment_family
    ]
    if corruption == "disclosure":
        trial_state["selection_history_incomplete"] = False
    elif corruption == "family":
        trial_state["trials"].append(
            {
                "trial_id": "trial-extra",
                "experiment_family": plan.experiment_family,
                "legacy": False,
                "selection_history_incomplete": False,
                "first_registered_at": "2020-12-30T02:00:00Z",
                "observations": [],
            }
        )
    elif corruption == "missing-timestamp":
        family_trials[0].pop("first_registered_at")
    elif corruption == "late-timestamp":
        family_trials[0]["first_registered_at"] = "2026-01-03T00:00:00Z"
    monkeypatch.setattr(ExperimentTrialRegistry, "read", lambda _self: trial_state)

    with pytest.raises(ValueError, match=message):
        run_registered_historical_screen(
            plan_id=plan.plan_id,
            trial_manifests={
                "selected": Path("selected.snapshot.json"),
                "baseline": Path("baseline.snapshot.json"),
            },
            qualification_registry_path=qualification_path,
            trial_registry_path=trial_path,
            research_data_store=object(),
            definition_store=object(),
            now=lambda: datetime(2026, 1, 2, 20, tzinfo=UTC),
        )


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
            boundary_time=epoch_start,
        )
    except ValueError as exc:
        assert "after the boundary" in str(exc)
    else:
        raise AssertionError("late trial should invalidate the forward selection epoch")
