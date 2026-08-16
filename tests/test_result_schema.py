import json
import subprocess
from datetime import UTC, date, datetime

import pandas as pd
import pytest

from trading.core.qualification import (
    HISTORICAL_QUALIFICATION_GATE_NAMES,
    SHADOW_ACTIVATION_GATE_NAMES,
)
from trading.core.sleeve_engine import (
    DEFAULT_BASE_COST_POLICY,
    DEFAULT_STRESS_COST_POLICY,
    evaluate_canonical_sleeve,
    serialize_canonical_sleeve_evidence,
)
from trading.market_data import (
    CsvMarketDataCache,
    MarketDataRequirement,
    MarketDataSeries,
    RefreshKind,
    SignalDecisionTime,
)
from trading.research_data import (
    ResearchDataStore,
    ResearchDefinitionStore,
)
from trading.research_data.result_schema import (
    ResultSchemaError,
    ResultValidityStatus,
    build_result_payload,
    classify_result,
    load_result,
    validate_canonical_evidence_against_definition,
)


def _definition_blob(repo_path, blob_root):
    repo_path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-qm", "baseline"],
        cwd=repo_path,
        check=True,
    )
    sources = {}
    for role in ("strategy", "detector", "backtester"):
        source = repo_path / f"{role}.py"
        source.write_text(f"class {role.title()}:\n    pass\n", encoding="utf-8")
        sources[role] = source
    return (
        ResearchDefinitionStore(blob_root)
        .capture(
            resolved_config={"ticker": "SPY", "threshold": 0.2},
            sources=sources,
            execution_engine_version="canonical-sleeve-v1",
            dependency_versions={"pandas": "2.3.1"},
        )
        .blob
    )


def _fixture(tmp_path):
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    cache.publish(
        series,
        pd.DataFrame(
            {
                "Open": [10.0, 11.0],
                "High": [12.0, 13.0],
                "Low": [9.0, 10.0],
                "Close": [11.0, 12.0],
                "Volume": [100.0, 200.0],
            },
            index=pd.to_datetime(["2026-08-03", "2026-08-04"]),
        ),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    store = ResearchDataStore(
        tmp_path / "blobs",
        now=lambda: datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    manifest = store.create_snapshot(
        cache,
        (MarketDataRequirement(series, date(2026, 8, 3), role="primary"),),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
        definition=_definition_blob(tmp_path / "definition-repo", tmp_path / "blobs"),
    )
    manifest_path = store.write_manifest(
        manifest,
        tmp_path / "results" / "experiment" / "run.snapshot.json",
    )
    cached = cache.load(series)
    assert cached is not None
    frame = cached.bars
    evaluation = evaluate_canonical_sleeve(
        calendar=frame.index,
        close_prices=frame["Close"],
        candidates=(),
        initial_capital=1.0,
        base_policy=DEFAULT_BASE_COST_POLICY,
        stress_policy=DEFAULT_STRESS_COST_POLICY,
        legacy_candidates=(),
    )
    payload = build_result_payload(
        {
            "part_a": {"total_signals": 1},
            "metrics": {"return": 0.1},
            "canonical_sleeve_evidence": serialize_canonical_sleeve_evidence(evaluation),
        },
        manifest=manifest,
        manifest_path=manifest_path,
        run_mode="online",
    )
    return store, manifest, manifest_path, payload


def test_versioned_result_contains_evidence_lifecycle_sections_and_legacy_parts(tmp_path) -> None:
    _store, manifest, manifest_path, payload = _fixture(tmp_path)

    assert payload["schema_version"] == 3
    assert payload["validity"]["status"] == "valid"
    assert payload["data_snapshot_id"] == manifest.snapshot_id
    assert payload["definition_snapshot_id"] == manifest.definition.digest
    assert payload["data_cutoff"] == "2026-08-04"
    assert payload["definition_fingerprint"] == manifest.definition.fingerprint
    assert payload["legacy_period_results"]["part_a"]["total_signals"] == 1
    assert payload["development_summary"] == {}
    assert payload["historical_stability_folds"] == []
    assert payload["shadow_evidence"] == {}
    assert payload["live_evidence"] == {}
    assert payload["metadata"]["reproducibility"]["snapshot_manifest"] == str(manifest_path)
    assert payload["canonical_sleeve_evidence"]["ranking_scenario"] == "base_net"


def test_validity_is_valid_when_snapshot_is_reproducible_fresh_and_current(tmp_path) -> None:
    store, _manifest, manifest_path, payload = _fixture(tmp_path)

    validity = classify_result(
        payload,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )

    assert validity.status is ResultValidityStatus.VALID
    assert validity.is_qualifiable
    result_path = manifest_path.with_name("result.json")
    result_path.write_text(json.dumps(payload), encoding="utf-8")
    loaded = load_result(
        result_path,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    assert loaded.validity.status is ResultValidityStatus.VALID


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("historical_stability_folds", [{"fold_id": "fold-2021"}], "historical"),
        (
            "development_summary",
            {
                "historical_plan": {},
                "historical_screen": {
                    "passed": True,
                    "disposition": "active",
                },
            },
            "Active",
        ),
        (
            "shadow_evidence",
            {
                "registration": {"shadow_id": "shadow-1"},
                "evidence": {},
                "activation": {"authorized_for_live_orders": True},
            },
            "live orders",
        ),
        (
            "live_evidence",
            {"authorized_for_live_orders": True},
            "live evidence",
        ),
    ],
)
def test_validity_rejects_malformed_or_live_authorizing_qualification_evidence(
    tmp_path,
    field: str,
    value: object,
    message: str,
) -> None:
    store, _manifest, _manifest_path, payload = _fixture(tmp_path)
    payload[field] = value

    validity = classify_result(
        payload,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )

    assert validity.status is ResultValidityStatus.UNREPRODUCIBLE
    assert any(message in reason for reason in validity.reasons)


def test_registered_shadow_without_a_checkpoint_remains_valid_non_live_evidence(tmp_path) -> None:
    store, _manifest, _manifest_path, payload = _fixture(tmp_path)
    fold = {
        "fold_id": "",
        "evaluation_year": 0,
        "signal_count": 4,
        "candidate_count": 4,
        "completed_trades": 4,
        "cumulative_return": 0.01,
        "stress_cumulative_return": 0.005,
        "stress_max_drawdown": -0.01,
        "gross_profit": 1.0,
        "gross_loss": 0.0,
        "stress_gross_profit": 0.5,
        "stress_gross_loss": 0.0,
    }
    folds = [
        {**fold, "fold_id": f"fold-{year}", "evaluation_year": year} for year in range(2021, 2026)
    ]
    evaluation_sessions = [
        timestamp.date().isoformat() for timestamp in pd.bdate_range("2021-01-01", "2025-12-31")
    ]
    plan_folds = []
    for year in range(2021, 2026):
        annual = [value for value in evaluation_sessions if value.startswith(str(year))]
        plan_folds.append(
            {
                "fold_id": f"fold-{year}",
                "evaluation_year": year,
                "outcome_start": annual[0],
                "outcome_end": annual[-1],
                "signal_start": annual[1],
                "signal_end": annual[-2],
            }
        )
    cost_policies = {
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
    }
    payload["development_summary"] = {
        "historical_plan": {
            "plan_id": "plan-1",
            "definition_fingerprint": payload["definition_fingerprint"],
            "created_at": "2020-12-31T21:00:00.000000Z",
            "development_years": [2018, 2019, 2020],
            "evaluation_sessions": evaluation_sessions,
            "folds": plan_folds,
            "maximum_holding_sessions": 1,
            "execution_lag_sessions": 1,
            "dependency_sessions": 2,
            "embargo_sessions": 1,
            "stress_drawdown_limit": "0.2",
            "thresholds": {
                "minimum_development_years": 3,
                "minimum_evaluation_folds": 5,
                "minimum_completed_trades": 20,
                "minimum_traded_folds": 3,
                "minimum_positive_fold_rate": "0.6",
                "minimum_cumulative_return": "0",
                "minimum_profit_factor": "1.1",
                "minimum_stress_cumulative_return": "0",
                "minimum_stress_profit_factor": "1",
                "maximum_fold_concentration": "0.5",
                "selection_confidence": "0.9",
            },
            "benchmarks": {
                "family_baseline_trial_id": "trial-baseline",
                "random_seed": 17,
                "random_samples": 10,
            },
            "selection_adjustment": {"repetitions": 100, "block_sessions": 5},
            "cost_policies": cost_policies,
        },
        "historical_screen": {
            "plan_id": "plan-1",
            "aggregate": {
                "completed_trades": 20,
                "traded_folds": 5,
                "positive_traded_fold_rate": 1.0,
                "cumulative_return": (1.01**5) - 1,
                "profit_factor": "Infinity",
                "stress_cumulative_return": (1.005**5) - 1,
                "stress_profit_factor": "Infinity",
                "stress_max_drawdown": -0.01,
                "trade_fold_concentration": 0.2,
                "profit_fold_concentration": 0.2,
            },
            "benchmarks": {
                "cash_return": 0.0,
                "family_baseline_return": 0.0,
                "random_entry_samples": [
                    {
                        "sample_index": index,
                        "cumulative_return": 0.0,
                        "completed_trades": 20,
                        "entry_months": [1] * 20,
                        "holding_sessions": [1] * 20,
                    }
                    for index in range(10)
                ],
            },
            "passed": True,
            "disposition": "shadow-eligible",
            "gates": [
                {"name": name, "passed": True} for name in HISTORICAL_QUALIFICATION_GATE_NAMES
            ],
            "selection_adjustment": {
                "selected_trial_id": "trial-1",
                "included_trial_ids": ["trial-1", "trial-baseline"],
                "observed_mean_excess_return": "0.001",
                "adjusted_confidence": "0.95",
                "repetitions": 100,
                "block_sessions": 5,
                "passed": True,
            },
        },
    }
    payload["historical_stability_folds"] = folds
    payload["shadow_evidence"] = {
        "registration": {
            "shadow_id": "shadow-1",
            "historical_plan_id": "plan-1",
            "trial_id": "trial-1",
            "definition_fingerprint": payload["definition_fingerprint"],
            "definition_snapshot_id": "d" * 64,
            "definition_snapshot_byte_count": 100,
            "prospective_start": "2026-08-04T21:00:00.000000Z",
            "recorded_at": "2026-08-04T21:00:00.000000Z",
            "activation_checkpoint": "2027-08-09",
            "status": "shadow",
            "cost_policies": cost_policies,
            "activation_policy": {
                "minimum_completed_sessions": 252,
                "minimum_completed_trades": 12,
                "minimum_cumulative_return": "0",
                "minimum_profit_factor": "1",
                "minimum_stress_cumulative_return": "0",
                "minimum_stress_profit_factor": "1",
                "stress_drawdown_limit": "0.2",
            },
        },
        "evidence": {},
        "activation": {},
    }
    payload["development_summary"]["historical_plan"]["forward_selection_epoch"] = {
        "started_at": "2020-12-31T21:00:00.000000Z",
        "selected_trial_id": "trial-1",
        "included_trial_ids": ["trial-1", "trial-baseline"],
        "prior_selection_history_incomplete": True,
    }

    validity = classify_result(
        payload,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )

    assert validity.status is ResultValidityStatus.VALID

    retrospective = json.loads(json.dumps(payload))
    retrospective_plan = retrospective["development_summary"]["historical_plan"]
    retrospective_plan["created_at"] = "2026-01-02T21:00:00.000000Z"
    retrospective_plan["evidence_role"] = "retrospective-confirmatory"
    retrospective_plan["evidence_audit"] = {
        "classification": "provenance-unknown",
        "frozen_at": retrospective_plan["created_at"],
        "justification": "Legacy selection provenance is incomplete.",
        "trial_history_complete": False,
    }
    retrospective_plan["retrospective_selection_checkpoint"] = {
        "frozen_at": retrospective_plan["created_at"],
        "selected_trial_id": "trial-1",
        "included_trial_ids": ["trial-1", "trial-baseline"],
        "prior_selection_history_incomplete": True,
    }
    retrospective_plan.pop("forward_selection_epoch")
    retrospective["development_summary"]["historical_screen"]["disposition"] = (
        "retrospectively-supported"
    )
    retrospective["shadow_evidence"] = {}
    retrospective_validity = classify_result(
        retrospective,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    assert retrospective_validity.status is ResultValidityStatus.VALID

    explicit_calendar = json.loads(json.dumps(retrospective))
    explicit_plan = explicit_calendar["development_summary"]["historical_plan"]
    explicit_plan["development_years"] = [2015, 2016, 2017]
    explicit_plan["role_calendar"] = {
        "development_sessions": [
            timestamp.date().isoformat() for timestamp in pd.bdate_range("2015-01-01", "2017-12-31")
        ],
        "warmup_sessions": [
            timestamp.date().isoformat() for timestamp in pd.bdate_range("2020-01-01", "2020-12-31")
        ],
        "evaluation_sessions": explicit_plan["evaluation_sessions"],
    }
    explicit_validity = classify_result(
        explicit_calendar,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    assert explicit_validity.status is ResultValidityStatus.VALID

    study_time = json.loads(json.dumps(explicit_calendar))
    study_time_plan = study_time["development_summary"]["historical_plan"]
    study_time_plan["evidence_role"] = "study-time-retrospective"
    study_time_validity = classify_result(
        study_time,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    assert study_time_validity.status is ResultValidityStatus.VALID

    falsely_clean_study_time = json.loads(json.dumps(study_time))
    falsely_clean_study_time["development_summary"]["historical_plan"]["evidence_audit"][
        "classification"
    ] = "verified-clean"
    falsely_clean_validity = classify_result(
        falsely_clean_study_time,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    assert falsely_clean_validity.status is ResultValidityStatus.UNREPRODUCIBLE

    missing_calendar = json.loads(json.dumps(explicit_calendar))
    missing_calendar["development_summary"]["historical_plan"].pop("role_calendar")
    missing_calendar_validity = classify_result(
        missing_calendar,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    assert missing_calendar_validity.status is ResultValidityStatus.UNREPRODUCIBLE
    assert any("explicit role calendar" in reason for reason in missing_calendar_validity.reasons)

    promoted_retrospective = json.loads(json.dumps(retrospective))
    promoted_retrospective["shadow_evidence"] = payload["shadow_evidence"]
    promoted_validity = classify_result(
        promoted_retrospective,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    assert promoted_validity.status is ResultValidityStatus.UNREPRODUCIBLE
    assert any("passing historical screen" in reason for reason in promoted_validity.reasons)

    changed_epoch = json.loads(json.dumps(payload))
    changed_epoch["development_summary"]["historical_plan"]["forward_selection_epoch"][
        "included_trial_ids"
    ] = ["trial-1", "trial-new", "trial-baseline"]
    changed_epoch_validity = classify_result(
        changed_epoch,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    assert changed_epoch_validity.status is ResultValidityStatus.UNREPRODUCIBLE
    assert any("forward selection epoch" in reason for reason in changed_epoch_validity.reasons)

    contradictory = json.loads(json.dumps(payload))
    contradictory["development_summary"]["historical_screen"]["aggregate"]["completed_trades"] = 0
    contradictory_validity = classify_result(
        contradictory,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    assert contradictory_validity.status is ResultValidityStatus.UNREPRODUCIBLE
    assert any("aggregate conflicts" in reason for reason in contradictory_validity.reasons)

    fabricated_activation = json.loads(json.dumps(payload))
    fabricated_activation["shadow_evidence"]["evidence"] = {
        "shadow_id": "shadow-1",
        "definition_fingerprint": payload["definition_fingerprint"],
        "as_of": "2027-08-10",
        "data_cutoff": "2027-08-10",
        "completed_sessions": 0,
        "paper_proposals": [],
        "simulated_fills": [],
        "cumulative_return": 0.0,
        "profit_factor": "0",
        "stress_cumulative_return": 0.0,
        "stress_profit_factor": "0",
        "stress_max_drawdown": 0.0,
        "critical_drift": False,
    }
    fabricated_activation["shadow_evidence"]["activation"] = {
        "shadow_id": "shadow-1",
        "evaluated_at": "2027-08-10",
        "gates": [
            {
                "name": name,
                "passed": True,
                "actual": payload["definition_fingerprint"]
                if name == "definition_unchanged"
                else "pass",
                "threshold": "pass",
            }
            for name in SHADOW_ACTIVATION_GATE_NAMES
        ],
        "eligible": True,
        "disposition": "activation-eligible",
        "authorized_for_live_orders": False,
    }
    activation_validity = classify_result(
        fabricated_activation,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    assert activation_validity.status is ResultValidityStatus.UNREPRODUCIBLE
    assert any("activation gates conflict" in reason for reason in activation_validity.reasons)

    del payload["shadow_evidence"]["registration"]["definition_snapshot_id"]
    invalid = classify_result(
        payload,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    assert invalid.status is ResultValidityStatus.UNREPRODUCIBLE
    assert any("registration evidence is incomplete" in reason for reason in invalid.reasons)


def test_data_cutoff_becomes_data_stale_without_mutating_the_result(tmp_path) -> None:
    store, _manifest, _manifest_path, payload = _fixture(tmp_path)

    validity = classify_result(
        payload,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 6, 12, tzinfo=UTC),
    )

    assert validity.status is ResultValidityStatus.DATA_STALE
    assert not validity.is_qualifiable
    assert payload["validity"]["status"] == "valid"


def test_current_definition_change_becomes_definition_stale(tmp_path) -> None:
    store, _manifest, _manifest_path, payload = _fixture(tmp_path)

    validity = classify_result(
        payload,
        store=store,
        current_definition_fingerprint="f" * 64,
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )

    assert validity.status is ResultValidityStatus.DEFINITION_STALE
    assert not validity.is_qualifiable


def test_missing_current_definition_identity_is_unreproducible(tmp_path) -> None:
    store, _manifest, _manifest_path, payload = _fixture(tmp_path)

    validity = classify_result(
        payload,
        store=store,
        current_definition_fingerprint=None,
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )

    assert validity.status is ResultValidityStatus.UNREPRODUCIBLE
    assert not validity.is_qualifiable
    assert any("current research definition" in reason for reason in validity.reasons)


def test_missing_data_blob_is_unreproducible_and_never_repaired(tmp_path) -> None:
    store, manifest, _manifest_path, payload = _fixture(tmp_path)
    blob_path = store.data_blob_path(manifest.data[0].blob.digest)
    original = blob_path.read_bytes()
    blob_path.unlink()

    validity = classify_result(
        payload,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )

    assert validity.status is ResultValidityStatus.UNREPRODUCIBLE
    assert not validity.is_qualifiable
    assert not blob_path.exists()
    assert original


def test_missing_definition_blob_is_unreproducible(tmp_path) -> None:
    store, manifest, _manifest_path, payload = _fixture(tmp_path)
    definition_path = (
        store.root
        / "definitions"
        / "sha256"
        / manifest.definition.digest[:2]
        / f"{manifest.definition.digest}.json"
    )
    definition_path.unlink()

    validity = classify_result(
        payload,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )

    assert validity.status is ResultValidityStatus.UNREPRODUCIBLE


def test_declared_partial_result_is_unreproducible_even_with_valid_evidence(tmp_path) -> None:
    store, _manifest, _manifest_path, payload = _fixture(tmp_path)
    payload["partial"] = True

    validity = classify_result(
        payload,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )

    assert validity.status is ResultValidityStatus.UNREPRODUCIBLE
    assert any("incomplete" in reason for reason in validity.reasons)


def test_schema_v3_requires_lifecycle_evidence_sections(tmp_path) -> None:
    store, _manifest, _manifest_path, payload = _fixture(tmp_path)
    payload.pop("shadow_evidence")

    validity = classify_result(
        payload,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )

    assert validity.status is ResultValidityStatus.UNREPRODUCIBLE
    assert "shadow_evidence" in validity.reasons[0]


def test_schema_v3_rejects_unknown_canonical_sleeve_engine(tmp_path) -> None:
    store, _manifest, _manifest_path, payload = _fixture(tmp_path)
    payload["canonical_sleeve_evidence"]["engine_version"] = "unknown-engine"

    validity = classify_result(
        payload,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )

    assert validity.status is ResultValidityStatus.UNREPRODUCIBLE
    assert "engine version" in validity.reasons[0]


def test_schema_v3_rejects_metrics_that_do_not_match_daily_equity(tmp_path) -> None:
    store, _manifest, _manifest_path, payload = _fixture(tmp_path)
    payload["canonical_sleeve_evidence"]["scenarios"]["base_net"]["metrics"]["sharpe_ratio"] = 999.0

    validity = classify_result(
        payload,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )

    assert validity.status is ResultValidityStatus.UNREPRODUCIBLE
    assert any("metrics do not match daily equity" in reason for reason in validity.reasons)


def test_canonical_cost_evidence_must_match_preregistered_definition(tmp_path) -> None:
    store, manifest, _manifest_path, payload = _fixture(tmp_path)
    definition = ResearchDefinitionStore(store.root).load(manifest.definition)
    evidence = payload["canonical_sleeve_evidence"]
    evidence["cost_policies"]["base"]["entry_slippage_bps"] = 999.0

    with pytest.raises(ResultSchemaError, match="cost policies do not match"):
        validate_canonical_evidence_against_definition(evidence, definition)

    validity = classify_result(
        payload,
        store=store,
        current_definition_fingerprint=payload["definition_fingerprint"],
        now=datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    assert validity.status is ResultValidityStatus.UNREPRODUCIBLE
    assert any("cost policies do not match" in reason for reason in validity.reasons)


def test_old_result_is_readable_as_legacy_but_not_qualifiable(tmp_path) -> None:
    result_path = tmp_path / "legacy.json"
    result_path.write_text(
        '{"metadata":{"execution_time":"2026-08-04T00:00:00"},'
        '"part_a":{"total_signals":3},"part_b":{},"part_c":{}}',
        encoding="utf-8",
    )

    result = load_result(result_path)

    assert result.validity.status is ResultValidityStatus.LEGACY
    assert not result.validity.is_qualifiable
    assert result.payload["part_a"]["total_signals"] == 3


def test_phase_3_schema_v2_result_is_legacy_after_canonical_execution_upgrade() -> None:
    validity = classify_result({"schema_version": 2})

    assert validity.status is ResultValidityStatus.LEGACY
    assert not validity.is_qualifiable
    assert "canonical sleeve evidence" in validity.reasons[0]
