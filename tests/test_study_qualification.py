import hashlib
import json
from datetime import UTC, date, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

import trading.core.study_qualification as study_qualification_module
from trading.core.accounting import canonical_json_bytes
from trading.core.study_qualification import (
    CANDIDATE_FREEZE_AUTHORIZATION_SCOPE,
    FIXED_CALENDAR,
    FIXED_CALENDAR_RETROSPECTIVE_CAPABILITY,
    FIXED_CALENDAR_RETROSPECTIVE_ROUTE,
    REQUIRED_STUDY_TIME_CHALLENGES,
    _compile_spec,
    compile_study_qualification_plan,
    fixed_challenge_method_contract,
    load_frozen_study_qualification_spec,
    validate_study_qualification_spec_for_preregistration,
)
from trading.core.workflow_authoring import MarkdownDocument, WorkflowAuthoringError
from trading.core.workflow_studies import WorkflowStudyService
from trading.research_data import ExperimentTrialRegistry

_LEGACY_S004_TEST_PATH = (
    "workflows/strategy-forward-replication-research--v004/work/studies/"
    "fxi-atr-band-mean-reversion-forward-replication--s004"
)


def _study(tmp_path: Path) -> Path:
    study = tmp_path / "workflows" / "example--v001" / "work" / "studies" / "example--s001"
    study.mkdir(parents=True)
    return study


def _test_policy_set() -> dict:
    policy_releases = [
        {
            "family": family,
            "version": "v001",
            "path": f"policies/{family}--v001",
            "release_digest": character * 64,
            "config_digest": character * 64,
        }
        for family, character in (
            ("canonical-execution", "1"),
            ("firstrade-manual-trading", "2"),
            ("portfolio-risk", "3"),
            ("us-equity-market", "4"),
        )
    ]
    policy_identity_payload = [
        {
            "family": item["family"],
            "version": item["version"],
            "release_digest": item["release_digest"],
            "config_digest": item["config_digest"],
        }
        for item in policy_releases
    ]
    return {
        "identity": hashlib.sha256(canonical_json_bytes(policy_identity_payload)).hexdigest(),
        "releases": policy_releases,
    }


@pytest.fixture(autouse=True)
def _stub_example_released_policy_set(monkeypatch):
    original = study_qualification_module.structured_qualification_runtime_contract

    def runtime_contract(path: Path):
        if Path(path).name == "example--v001":
            return {"policy_set": _test_policy_set()}
        return original(path)

    monkeypatch.setattr(
        study_qualification_module,
        "structured_qualification_runtime_contract",
        runtime_contract,
    )


def _spec(study: Path, *, tmp_path: Path) -> dict:
    return {
        "schema_version": 1,
        "study_path": study.relative_to(tmp_path).as_posix(),
        "route": "study-time-retrospective",
        "evidence_classification": "provenance-unknown",
        "evidence_justification": "Prior access cannot be excluded.",
        "trial_history_complete": False,
        "prior_selection_history_incomplete": True,
        "registries": {
            "trial_registry_path": "results/trial_registry.json",
            "qualification_registry_path": "state/qualification-registry.json",
        },
        "policy_set": _test_policy_set(),
        "cost_policies": {
            "base": {
                "entry_slippage_bps": 5.0,
                "exit_slippage_bps": 5.0,
                "fee_bps_per_side": 1.0,
            },
            "stress": {
                "entry_slippage_bps": 20.0,
                "exit_slippage_bps": 20.0,
                "fee_bps_per_side": 2.0,
            },
        },
        "evidence_contract": {
            "schema_version": 1,
            "snapshot": {
                "kind": "immutable-research-data-manifest",
                "definition_binding": "exact",
                "evaluation_coverage": "all-frozen-evaluation-sessions",
                "data_cutoff": "frozen-evaluation-end",
            },
            "observation": {
                "allowed_run_modes": ["offline"],
                "outcome_status": "succeeded",
                "validity_status": "valid",
                "observed_at_floor": "frozen-evaluation-end",
            },
        },
        "calendar": {
            "warmup_start": "2009-01-01",
            "warmup_end": "2009-12-31",
            "development_years": [2010, 2011, 2012],
            "quarantine_years": [2013],
            "evaluation_years": [2014, 2015, 2016, 2017, 2018],
        },
        "family": {
            "maximum_trials": 2,
            "baseline_identity": "family/baseline",
            "members": [
                {
                    "identity": "family/candidate",
                    "source_sha256": "a" * 64,
                    "role": "selection-candidate",
                },
                {
                    "identity": "family/baseline",
                    "source_sha256": "b" * 64,
                    "role": "family-baseline",
                },
            ],
            "shared_sources": [],
        },
        "execution": {
            "maximum_holding_sessions": 20,
            "execution_lag_sessions": 1,
            "dependency_sessions": 21,
            "embargo_sessions": 1,
            "stress_drawdown_limit": "0.20",
        },
        "benchmarks": {
            "random_seed": 7,
            "random_samples": 1000,
            "bootstrap_repetitions": 1000,
            "bootstrap_block_sessions": 20,
        },
        "required_challenges": [
            {
                "id": challenge,
                "evidence_identity": f"{challenge}-evidence",
                "applies_to": _applies_to(challenge),
                "gate": {"metric": "passed", "operator": "=", "threshold": True},
            }
            for challenge in sorted(REQUIRED_STUDY_TIME_CHALLENGES)
        ],
    }


def _write_spec(study: Path, payload: dict) -> None:
    (study / "QUALIFICATION_SPEC.json").write_text(
        json.dumps(payload, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_structured_artifacts(study: Path, payload: dict, *, tmp_path: Path) -> None:
    _write_spec(study, payload)
    (study / "HYPOTHESIS.md").write_text("# Hypothesis\n", encoding="utf-8")
    (study / "PLAN.md").write_text("# Plan\n", encoding="utf-8")
    workflow_sha = "f" * 64
    (study.parents[2] / "RELEASE.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "workflow_sha256": workflow_sha,
                "capabilities": [
                    (
                        FIXED_CALENDAR_RETROSPECTIVE_CAPABILITY
                        if payload["route"] == FIXED_CALENDAR_RETROSPECTIVE_ROUTE
                        else "study-time-retrospective-v1"
                    )
                ],
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    spec_sha = hashlib.sha256((study / "QUALIFICATION_SPEC.json").read_bytes()).hexdigest()
    hypothesis_sha = hashlib.sha256((study / "HYPOTHESIS.md").read_bytes()).hexdigest()
    plan_sha = hashlib.sha256((study / "PLAN.md").read_bytes()).hexdigest()
    preregistration = {
        "schema_version": 1,
        "study_id": "S001",
        "study_path": study.relative_to(tmp_path).as_posix(),
        "workflow": "example",
        "workflow_version": "v001",
        "route": payload["route"],
        "approved_at": "2026-01-01T00:00:00.000000Z",
        "approved_by": "owner@example.com",
        "workflow_sha256": workflow_sha,
        "hypothesis_sha256": hypothesis_sha,
        "plan_sha256": plan_sha,
        "qualification_spec_sha256": spec_sha,
    }
    (study / "PREREGISTRATION.json").write_text(
        json.dumps(preregistration, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    preregistration_sha = hashlib.sha256((study / "PREREGISTRATION.json").read_bytes()).hexdigest()
    development_authorization_path = study / "DEVELOPMENT_AUTHORIZATION.json"
    development_authorization_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "study_path": study.relative_to(tmp_path).as_posix(),
                "route": payload["route"],
                "preregistration_sha256": preregistration_sha,
                "authorized_at": "2026-01-02T00:00:00.000000Z",
                "approved_by": "owner@example.com",
                "authorized_operator": "researcher@example.com",
                "authorization_scope": "Development only; no Evaluation or Shadow authority.",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    development_authorization_sha = hashlib.sha256(
        development_authorization_path.read_bytes()
    ).hexdigest()
    complete_family = [
        {
            "source_identity": "family/candidate",
            "trial_id": "selected-trial",
            "definition_fingerprint": "a" * 64,
        },
        {
            "source_identity": "family/baseline",
            "trial_id": "baseline-trial",
            "definition_fingerprint": "b" * 64,
        },
    ]
    (study / "CANDIDATE_FREEZE.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "study_id": "S001",
                "study_path": study.relative_to(tmp_path).as_posix(),
                "workflow": "example",
                "workflow_version": "v001",
                "route": payload["route"],
                "approved_at": "2026-01-03T00:00:00.000000Z",
                "approved_by": "owner@example.com",
                "authorization_scope": CANDIDATE_FREEZE_AUTHORIZATION_SCOPE,
                "hypothesis_sha256": hypothesis_sha,
                "qualification_spec_sha256": spec_sha,
                "preregistration_sha256": preregistration_sha,
                "plan_sha256": plan_sha,
                "development_authorization_sha256": development_authorization_sha,
                "workflow_release_sha256": hashlib.sha256(
                    (study.parents[2] / "RELEASE.json").read_bytes()
                ).hexdigest(),
                "frozen_trial_budget": 2,
                "selected_candidate": complete_family[0],
                "family_baseline": complete_family[1],
                "complete_family": complete_family,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _applies_to(challenge: str) -> dict:
    if challenge == "cash":
        return {"kind": "benchmark", "identities": ["cash"]}
    if challenge == "family-baseline":
        return {"kind": "trial", "identities": ["family/baseline"]}
    if challenge == "random-entry":
        return {"kind": "benchmark", "identities": ["random-entry"]}
    return {"kind": "method", "identities": [f"{challenge}-definition"]}


def test_guarded_candidate_freeze_is_current_time_add_only_and_idempotent(
    tmp_path,
    monkeypatch,
) -> None:
    study = _study(tmp_path)
    spec = _spec(study, tmp_path=tmp_path)
    _write_structured_artifacts(study, spec, tmp_path=tmp_path)
    prepared = json.loads((study / "CANDIDATE_FREEZE.json").read_text(encoding="utf-8"))
    selection = {
        field: prepared[field]
        for field in ("selected_candidate", "family_baseline", "complete_family")
    }
    (study / "CANDIDATE_FREEZE.json").unlink()
    selection_path = tmp_path / "development-selection.json"
    selection_path.write_text(json.dumps(selection, sort_keys=True) + "\n", encoding="utf-8")
    version = study.parents[2]
    service = WorkflowStudyService(
        tmp_path / "workflows",
        now=lambda: datetime(2026, 1, 3, tzinfo=UTC),
    )
    document = MarkdownDocument(
        {
            "status": "running",
            "route": spec["route"],
            "preregistered_by": "owner@example.com",
        },
        "# Study\n",
    )
    monkeypatch.setattr(service.repository, "_require_structurally_valid", lambda: None)
    monkeypatch.setattr(service.repository, "sync", lambda: None)
    monkeypatch.setattr(service.repository, "_require_valid", lambda: None)
    monkeypatch.setattr(
        service,
        "_study_context",
        lambda _path: (study, version, {"status": "active"}, document),
    )

    with pytest.raises(WorkflowAuthoringError, match="preregistered human owner"):
        service.freeze_candidate(
            study,
            selection_path=selection_path,
            approved_by="other@example.com",
        )

    def concurrent_exact_publication(path, content, *, replace=True):
        assert replace is False
        path.write_bytes(content)
        raise WorkflowAuthoringError(f"refusing to overwrite existing file: {path}")

    monkeypatch.setattr(
        "trading.core.workflow_studies._atomic_write",
        concurrent_exact_publication,
    )
    freeze = service.freeze_candidate(
        study,
        selection_path=selection_path,
        approved_by="owner@example.com",
    )
    assert freeze["approved_at"] == "2026-01-03T00:00:00.000000Z"
    assert freeze["authorization_scope"] == CANDIDATE_FREEZE_AUTHORIZATION_SCOPE
    assert freeze["frozen_trial_budget"] == 2
    assert (
        service.freeze_candidate(
            study,
            selection_path=selection_path,
            approved_by="owner@example.com",
        )
        == freeze
    )

    selection["selected_candidate"] = dict(selection["selected_candidate"])
    selection["selected_candidate"]["trial_id"] = "different-trial"
    selection_path.write_text(json.dumps(selection, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(WorkflowAuthoringError, match="different operation"):
        service.freeze_candidate(
            study,
            selection_path=selection_path,
            approved_by="owner@example.com",
        )


def test_guarded_candidate_freeze_rejects_reserved_or_incomplete_selection(
    tmp_path,
    monkeypatch,
) -> None:
    study = _study(tmp_path)
    spec = _spec(study, tmp_path=tmp_path)
    _write_structured_artifacts(study, spec, tmp_path=tmp_path)
    prepared = json.loads((study / "CANDIDATE_FREEZE.json").read_text(encoding="utf-8"))
    (study / "CANDIDATE_FREEZE.json").unlink()
    selection_path = tmp_path / "development-selection.json"
    service = WorkflowStudyService(tmp_path / "workflows")
    document = MarkdownDocument(
        {
            "status": "running",
            "route": spec["route"],
            "preregistered_by": "owner@example.com",
        },
        "# Study\n",
    )
    monkeypatch.setattr(service.repository, "_require_structurally_valid", lambda: None)
    monkeypatch.setattr(service.repository, "sync", lambda: None)
    monkeypatch.setattr(service.repository, "_require_valid", lambda: None)
    monkeypatch.setattr(
        service,
        "_study_context",
        lambda _path: (study, study.parents[2], {"status": "active"}, document),
    )
    selection = {
        field: prepared[field]
        for field in ("selected_candidate", "family_baseline", "complete_family")
    }
    selection["approved_at"] = "2020-01-01T00:00:00Z"
    selection_path.write_text(json.dumps(selection, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(WorkflowAuthoringError, match="must contain only"):
        service.freeze_candidate(
            study,
            selection_path=selection_path,
            approved_by="owner@example.com",
        )

    selection.pop("approved_at")
    selection["complete_family"] = selection["complete_family"][:-1]
    selection_path.write_text(json.dumps(selection, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(WorkflowAuthoringError, match="complete trial family"):
        service.freeze_candidate(
            study,
            selection_path=selection_path,
            approved_by="owner@example.com",
        )


def test_preregistration_spec_requires_complete_family_calendar_and_challenges(tmp_path) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)
    _write_spec(study, payload)
    assert len(validate_study_qualification_spec_for_preregistration(study)) == 64


def test_fixed_calendar_route_accepts_only_the_released_civil_dates(tmp_path) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)
    payload.update(
        route=FIXED_CALENDAR_RETROSPECTIVE_ROUTE,
        evidence_classification="provenance-unknown",
        trial_history_complete=False,
    )
    payload["calendar"] = dict(FIXED_CALENDAR)
    for challenge in payload["required_challenges"]:
        challenge["method"] = fixed_challenge_method_contract(challenge["id"])
    _write_spec(study, payload)

    assert len(validate_study_qualification_spec_for_preregistration(study)) == 64

    payload["calendar"]["replay_start"] = "2025-01-02"
    _write_spec(study, payload)
    with pytest.raises(ValueError, match="must match the released 2013-2025 contract"):
        validate_study_qualification_spec_for_preregistration(study)


def test_fixed_calendar_loader_exposes_replay_bounds(tmp_path) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)
    payload.update(
        route=FIXED_CALENDAR_RETROSPECTIVE_ROUTE,
        evidence_classification="provenance-unknown",
        trial_history_complete=False,
    )
    payload["calendar"] = dict(FIXED_CALENDAR)
    for challenge in payload["required_challenges"]:
        challenge["method"] = fixed_challenge_method_contract(challenge["id"])
    _write_structured_artifacts(study, payload, tmp_path=tmp_path)

    frozen = load_frozen_study_qualification_spec(study)

    assert frozen.route == FIXED_CALENDAR_RETROSPECTIVE_ROUTE
    assert frozen.evidence_role == FIXED_CALENDAR_RETROSPECTIVE_ROUTE
    assert frozen.development_years == tuple(range(2014, 2019))
    assert frozen.evaluation_years == tuple(range(2020, 2025))
    assert frozen.replay_start == date(2025, 1, 1)
    assert frozen.replay_end == date(2025, 12, 31)

    payload["family"]["members"] = payload["family"]["members"][:1]
    _write_spec(study, payload)
    with pytest.raises(ValueError, match="complete trial family"):
        validate_study_qualification_spec_for_preregistration(study)


def test_preregistration_spec_freezes_policy_cost_snapshot_and_observation_semantics(
    tmp_path,
) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)

    payload["policy_set"]["identity"] = "not-a-digest"
    _write_spec(study, payload)
    with pytest.raises(ValueError, match="policy-set identity"):
        validate_study_qualification_spec_for_preregistration(study)

    payload = _spec(study, tmp_path=tmp_path)
    payload["policy_set"]["releases"][0]["release_digest"] = "9" * 64
    policy_identity_payload = [
        {
            "family": item["family"],
            "version": item["version"],
            "release_digest": item["release_digest"],
            "config_digest": item["config_digest"],
        }
        for item in payload["policy_set"]["releases"]
    ]
    payload["policy_set"]["identity"] = hashlib.sha256(
        canonical_json_bytes(policy_identity_payload)
    ).hexdigest()
    _write_spec(study, payload)
    with pytest.raises(ValueError, match="differs from released workflow"):
        validate_study_qualification_spec_for_preregistration(study)

    payload = _spec(study, tmp_path=tmp_path)
    payload["cost_policies"]["stress"]["entry_slippage_bps"] = 1.0
    _write_spec(study, payload)
    with pytest.raises(ValueError, match="stress costs"):
        validate_study_qualification_spec_for_preregistration(study)

    for nonfinite in (float("nan"), float("inf"), float("-inf")):
        payload = _spec(study, tmp_path=tmp_path)
        payload["cost_policies"]["base"]["entry_slippage_bps"] = nonfinite
        _write_spec(study, payload)
        with pytest.raises(ValueError, match="base cost policy values are invalid"):
            validate_study_qualification_spec_for_preregistration(study)

    payload = _spec(study, tmp_path=tmp_path)
    payload["evidence_contract"]["observation"]["validity_status"] = "caller-defined"
    _write_spec(study, payload)
    with pytest.raises(ValueError, match="snapshot/observation contract"):
        validate_study_qualification_spec_for_preregistration(study)


def test_preregistration_spec_rejects_calendar_gap_and_missing_challenge(tmp_path) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)
    payload["calendar"]["quarantine_years"] = []
    _write_spec(study, payload)
    with pytest.raises(ValueError, match="unassigned year"):
        validate_study_qualification_spec_for_preregistration(study)

    payload = _spec(study, tmp_path=tmp_path)
    payload["required_challenges"] = payload["required_challenges"][:-1]
    _write_spec(study, payload)
    with pytest.raises(ValueError, match="challenge inventory"):
        validate_study_qualification_spec_for_preregistration(study)

    payload = _spec(study, tmp_path=tmp_path)
    duplicate = dict(payload["required_challenges"][0])
    duplicate["evidence_identity"] = "duplicate-evidence"
    duplicate["applies_to"] = {"kind": "method", "identities": ["duplicate-method"]}
    payload["required_challenges"].append(duplicate)
    _write_spec(study, payload)
    with pytest.raises(ValueError, match="challenge inventory"):
        validate_study_qualification_spec_for_preregistration(study)


@pytest.mark.parametrize(
    ("route", "classification", "trial_history_complete", "development", "evaluation"),
    [
        (
            "clean-historical",
            "verified-clean",
            True,
            [2020, 2021, 2022],
            [2024, 2025, 2026, 2027, 2028],
        ),
        (
            "retrospective-confirmatory",
            "provenance-unknown",
            False,
            [2019, 2020, 2021],
            [2010, 2011, 2012, 2013, 2014],
        ),
        (
            "study-time-retrospective",
            "provenance-unknown",
            False,
            [2010, 2011, 2012],
            [2014, 2015, 2016, 2017, 2018],
        ),
    ],
)
def test_preregistration_spec_supports_every_structured_route(
    tmp_path,
    route: str,
    classification: str,
    trial_history_complete: bool,
    development: list[int],
    evaluation: list[int],
) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)
    payload.update(
        route=route,
        evidence_classification=classification,
        trial_history_complete=trial_history_complete,
    )
    payload["calendar"].update(
        warmup_start="2008-01-01",
        warmup_end="2008-12-31",
        development_years=development,
        evaluation_years=evaluation,
        quarantine_years=(
            list(range(development[-1] + 1, evaluation[0]))
            if development[-1] < evaluation[0]
            else []
        ),
    )
    _write_spec(study, payload)

    assert len(validate_study_qualification_spec_for_preregistration(study)) == 64


@pytest.mark.parametrize(
    ("route", "classification", "trial_history_complete", "expected_role"),
    [
        ("clean-historical", "verified-clean", True, "historical"),
        (
            "retrospective-confirmatory",
            "provenance-unknown",
            False,
            "retrospective-confirmatory",
        ),
        (
            "study-time-retrospective",
            "provenance-unknown",
            False,
            "study-time-retrospective",
        ),
    ],
)
def test_structured_loader_maps_every_route_to_exact_evidence_role(
    tmp_path,
    route: str,
    classification: str,
    trial_history_complete: bool,
    expected_role: str,
) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)
    payload.update(
        route=route,
        evidence_classification=classification,
        trial_history_complete=trial_history_complete,
    )
    _write_structured_artifacts(study, payload, tmp_path=tmp_path)

    frozen = load_frozen_study_qualification_spec(study)

    assert frozen.route == route
    assert frozen.evidence_role == expected_role


@pytest.mark.parametrize(
    ("route", "classification", "trial_history_complete"),
    [
        ("clean-historical", "verified-clean", True),
        ("retrospective-confirmatory", "provenance-unknown", False),
        ("study-time-retrospective", "provenance-unknown", False),
    ],
)
def test_public_exact_study_compiler_accepts_every_structured_route(
    tmp_path,
    monkeypatch,
    route: str,
    classification: str,
    trial_history_complete: bool,
) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)
    payload.update(
        route=route,
        evidence_classification=classification,
        trial_history_complete=trial_history_complete,
    )
    _write_structured_artifacts(study, payload, tmp_path=tmp_path)
    monkeypatch.setattr(
        "trading.core.study_qualification._verify_frozen_definitions",
        lambda _spec, **_kwargs: None,
    )
    monkeypatch.setattr(
        ExperimentTrialRegistry,
        "read",
        lambda _self: {"selection_history_incomplete": True},
    )
    captured = {}

    def register_plan(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            route=route,
            evidence_role=kwargs["evidence_role"],
            study_identity=kwargs["study_identity"],
        )

    monkeypatch.setattr(
        "trading.core.study_qualification.register_forward_qualification_plan",
        register_plan,
    )

    compiled = compile_study_qualification_plan(
        study_path=study,
        trial_registry_path=tmp_path / "results" / "trial_registry.json",
        qualification_registry_path=tmp_path / "state" / "qualification-registry.json",
        dry_run=True,
    )

    assert compiled.route == route
    assert compiled.evidence_role == ("historical" if route == "clean-historical" else route)
    assert captured["base_cost_policy"].entry_slippage_bps == 5.0
    assert captured["study_identity"].qualification_spec_sha256


def test_exact_study_compiler_uses_frozen_cost_policies(tmp_path, monkeypatch) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)
    payload["cost_policies"]["base"] = {
        "entry_slippage_bps": 7.0,
        "exit_slippage_bps": 8.0,
        "fee_bps_per_side": 1.5,
    }
    _write_structured_artifacts(study, payload, tmp_path=tmp_path)
    frozen = load_frozen_study_qualification_spec(study)
    captured = {}
    monkeypatch.setattr(
        ExperimentTrialRegistry,
        "read",
        lambda _self: {"selection_history_incomplete": True},
    )

    def register_plan(**kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(
        "trading.core.study_qualification.register_forward_qualification_plan",
        register_plan,
    )
    _compile_spec(
        frozen,
        qualification_registry_path=tmp_path / "state" / "qualification-registry.json",
        trial_registry_path=tmp_path / "results" / "trial_registry.json",
        dry_run=True,
        now=None,
        definition_store=None,
    )

    assert captured["base_cost_policy"].entry_slippage_bps == 7.0
    assert captured["base_cost_policy"].exit_slippage_bps == 8.0
    assert captured["stress_cost_policy"].entry_slippage_bps == 20.0
    assert frozen.study_identity.development_authorization_sha256 is not None


@pytest.mark.parametrize("field", ["selected_candidate", "family_baseline"])
def test_structured_loader_rejects_candidate_freeze_role_swap(tmp_path, field: str) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)
    _write_structured_artifacts(study, payload, tmp_path=tmp_path)
    freeze_path = study / "CANDIDATE_FREEZE.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    freeze[field]["source_identity"] = (
        "family/baseline" if field == "selected_candidate" else "family/candidate"
    )
    freeze_path.write_text(json.dumps(freeze, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="preregistered .* role"):
        load_frozen_study_qualification_spec(study)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("approved_by", "", "research-owner approval"),
        ("approved_by", "other@example.com", "differs from the human research owner"),
        ("authorization_scope", "", "authorization scope"),
        ("approved_at", "2025-12-31T00:00:00.000000Z", "must follow"),
    ],
)
def test_structured_loader_requires_candidate_freeze_human_approval(
    tmp_path,
    field: str,
    value: str,
    message: str,
) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)
    _write_structured_artifacts(study, payload, tmp_path=tmp_path)
    freeze_path = study / "CANDIDATE_FREEZE.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    freeze[field] = value
    freeze_path.write_text(json.dumps(freeze, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_frozen_study_qualification_spec(study)


def test_structured_loader_requires_development_approval_from_human_owner(tmp_path) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)
    _write_structured_artifacts(study, payload, tmp_path=tmp_path)
    authorization_path = study / "DEVELOPMENT_AUTHORIZATION.json"
    authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
    authorization["approved_by"] = "other@example.com"
    authorization_path.write_text(
        json.dumps(authorization, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="differs from the human owner"):
        load_frozen_study_qualification_spec(study)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda payload: payload["calendar"].update(warmup_start=None), "warmup bounds"),
        (
            lambda payload: payload["family"]["members"][0].update(source_sha256="bad"),
            "source digests",
        ),
        (
            lambda payload: payload["family"].update(
                shared_sources=[{"path": "runtime.py", "sha256": "bad"}]
            ),
            "shared source",
        ),
        (
            lambda payload: payload["family"].update(
                shared_sources=[{"path": "../runtime.py", "sha256": "c" * 64}]
            ),
            "shared source",
        ),
        (
            lambda payload: payload["family"]["members"][0].update(identity=None),
            "family identities",
        ),
        (
            lambda payload: payload["execution"].pop("dependency_sessions"),
            "dependency",
        ),
        (
            lambda payload: payload["benchmarks"].update(random_samples=0),
            "random samples",
        ),
        (
            lambda payload: payload.update(trial_history_complete="false"),
            "trial history completeness",
        ),
        (
            lambda payload: payload["registries"].update(
                qualification_registry_path="../state/qualification.json"
            ),
            "qualification_registry_path",
        ),
        (
            lambda payload: payload["required_challenges"][1].update(
                evidence_identity=payload["required_challenges"][0]["evidence_identity"]
            ),
            "unique frozen evidence identity",
        ),
        (
            lambda payload: payload["required_challenges"][0].update(
                applies_to={"kind": "method", "identities": ["cash"]}
            ),
            "wrong frozen target",
        ),
    ],
)
def test_preregistration_spec_rejects_incomplete_outcome_free_contract(
    tmp_path,
    mutate,
    message: str,
) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)
    mutate(payload)
    _write_spec(study, payload)

    with pytest.raises(ValueError, match=message):
        validate_study_qualification_spec_for_preregistration(study)


def test_legacy_s004_adapter_binds_exact_frozen_artifacts() -> None:
    study = Path(_LEGACY_S004_TEST_PATH)
    spec = load_frozen_study_qualification_spec(study)

    assert spec.study_identity.study_path.endswith("--s004")
    assert spec.maximum_family_trials == 6
    assert spec.development_years == tuple(range(2015, 2026))
    assert spec.quarantine_years == (2026,)
    assert spec.evaluation_years == (2027, 2028, 2029, 2030, 2031)
    assert len(spec.family_source_sha256) == 6


def test_legacy_s004_adapter_rejects_suffix_copy(tmp_path) -> None:
    copied = tmp_path / Path(_LEGACY_S004_TEST_PATH)
    copied.mkdir(parents=True)

    with pytest.raises(ValueError, match="no frozen QUALIFICATION_SPEC"):
        load_frozen_study_qualification_spec(copied)


@pytest.mark.parametrize(
    ("trial_path", "qualification_path", "message"),
    [
        (
            "state/other-trials.json",
            "state/qualification-registry.json",
            "trial registry path",
        ),
        (
            "results/trial_registry.json",
            "state/other-qualification.json",
            "qualification registry path",
        ),
    ],
)
def test_structured_compiler_rejects_registry_path_override(
    tmp_path,
    trial_path: str,
    qualification_path: str,
    message: str,
) -> None:
    study = _study(tmp_path)
    payload = _spec(study, tmp_path=tmp_path)
    _write_structured_artifacts(study, payload, tmp_path=tmp_path)

    with pytest.raises(ValueError, match=message):
        compile_study_qualification_plan(
            study_path=study,
            trial_registry_path=tmp_path / trial_path,
            qualification_registry_path=tmp_path / qualification_path,
            dry_run=True,
        )
