import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import pytest

from trading.research_data.trial_registry import ExperimentTrialRegistry, TrialRegistryError


def test_same_definition_on_new_data_adds_observation_not_trial(tmp_path) -> None:
    registry = ExperimentTrialRegistry(
        tmp_path / "results" / "trial_registry.json",
        now=lambda: datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    fingerprint = "a" * 64

    registry.register_trial(
        "spy:mean-reversion",
        fingerprint,
        experiment_name="spy_001",
    )
    registry.record_observation(
        "spy:mean-reversion",
        fingerprint,
        snapshot_id="b" * 64,
        run_mode="online",
        observation_id="first",
    )
    registry.record_observation(
        "spy:mean-reversion",
        fingerprint,
        snapshot_id="c" * 64,
        run_mode="online",
        observation_id="second",
    )

    state = registry.read()
    assert len(state["trials"]) == 1
    assert len(state["trials"][0]["observations"]) == 2


def test_new_definition_fingerprint_creates_new_trial(tmp_path) -> None:
    registry = ExperimentTrialRegistry(tmp_path / "registry.json")

    registry.register_trial("spy:mean-reversion", "a" * 64, experiment_name="spy_001")
    registry.register_trial("spy:mean-reversion", "b" * 64, experiment_name="spy_002")

    trials = registry.read()["trials"]
    assert len(trials) == 2
    assert {trial["definition_fingerprint"] for trial in trials} == {"a" * 64, "b" * 64}


def test_failed_and_removed_trials_remain_in_registry(tmp_path) -> None:
    registry = ExperimentTrialRegistry(tmp_path / "registry.json")
    fingerprint = "a" * 64
    registry.register_trial("spy:mean-reversion", fingerprint, experiment_name="spy_001")
    registry.record_observation(
        "spy:mean-reversion",
        fingerprint,
        run_mode="online",
        outcome_status="failed",
        failure_reason="runner crashed",
        observation_id="failed-run",
    )
    registry.mark_removed(
        "spy:mean-reversion",
        fingerprint,
        experiment_name="spy_001",
        reason="implementation deleted",
    )

    trial = registry.read()["trials"][0]
    assert trial["status"] == "removed"
    assert any(item["outcome_status"] == "failed" for item in trial["observations"])
    assert any(item["event"] == "removed" for item in trial["observations"])


@pytest.mark.parametrize(
    "observation",
    (
        {"run_mode": "ephemeral"},
        {"outcome_status": "partial"},
        {"validity_status": "unknown"},
        {"outcome_status": "failed"},
        {"failure_reason": "unexpected error"},
    ),
)
def test_observation_api_rejects_invalid_status_combinations(tmp_path, observation) -> None:
    registry = ExperimentTrialRegistry(tmp_path / "registry.json")
    fingerprint = "a" * 64
    registry.register_trial("spy:family", fingerprint, experiment_name="spy_001")

    with pytest.raises(TrialRegistryError, match="observation"):
        registry.record_observation("spy:family", fingerprint, **observation)

    assert registry.read()["trials"][0]["observations"] == []


def test_legacy_seed_is_explicitly_incomplete_and_idempotent(tmp_path) -> None:
    registry = ExperimentTrialRegistry(tmp_path / "registry.json")

    registry.seed_legacy(["spy_001", "spy_002"])
    registry.seed_legacy(["spy_001", "spy_002"])

    state = registry.read()
    assert state["selection_history_incomplete"] is True
    assert len(state["trials"]) == 2
    assert all(trial["legacy"] for trial in state["trials"])
    assert all(trial["definition_fingerprint"] is None for trial in state["trials"])
    assert all(trial["selection_history_incomplete"] for trial in state["trials"])


def test_concurrent_publications_and_retries_do_not_lose_history(tmp_path) -> None:
    path = tmp_path / "registry.json"
    fingerprints = [format(index, "064x") for index in range(8)]

    def publish(fingerprint: str) -> None:
        registry = ExperimentTrialRegistry(path)
        registry.register_trial(
            "spy:family", fingerprint, experiment_name=f"spy_{fingerprint[-2:]}"
        )
        registry.record_observation(
            "spy:family",
            fingerprint,
            snapshot_id=fingerprint,
            observation_id=f"observation-{fingerprint}",
        )
        registry.record_observation(
            "spy:family",
            fingerprint,
            snapshot_id=fingerprint,
            observation_id=f"observation-{fingerprint}",
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(publish, fingerprints))

    trials = ExperimentTrialRegistry(path).read()["trials"]
    assert len(trials) == len(fingerprints)
    assert all(len(trial["observations"]) == 1 for trial in trials)


def test_malformed_nested_registry_fails_closed_without_rewriting_history(tmp_path) -> None:
    path = tmp_path / "registry.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "selection_history_incomplete": False,
                "trials": [{"trial_id": "broken"}],
            }
        ),
        encoding="utf-8",
    )
    before = path.read_bytes()
    registry = ExperimentTrialRegistry(path)

    with pytest.raises(TrialRegistryError, match="malformed"):
        registry.register_trial("spy:family", "a" * 64, experiment_name="spy_001")

    assert path.read_bytes() == before


def test_malformed_observation_status_fails_closed_without_rewriting_history(tmp_path) -> None:
    path = tmp_path / "registry.json"
    registry = ExperimentTrialRegistry(path)
    fingerprint = "a" * 64
    registry.register_trial("spy:family", fingerprint, experiment_name="spy_001")
    registry.record_observation(
        "spy:family",
        fingerprint,
        observation_id="observation",
    )
    state = json.loads(path.read_text(encoding="utf-8"))
    state["trials"][0]["observations"][0]["run_mode"] = "ephemeral"
    path.write_text(json.dumps(state), encoding="utf-8")
    before = path.read_bytes()

    with pytest.raises(TrialRegistryError, match="observation"):
        registry.register_trial("spy:family", fingerprint, experiment_name="spy_001")

    assert path.read_bytes() == before
