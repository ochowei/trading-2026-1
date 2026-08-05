import json
import subprocess
from datetime import UTC, date, datetime

import pandas as pd

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
    ResultValidityStatus,
    build_result_payload,
    classify_result,
    load_result,
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
            execution_engine_version="execution-v1",
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
    payload = build_result_payload(
        {"part_a": {"total_signals": 1}, "metrics": {"return": 0.1}},
        manifest=manifest,
        manifest_path=manifest_path,
        run_mode="online",
    )
    return store, manifest, manifest_path, payload


def test_versioned_result_contains_evidence_lifecycle_sections_and_legacy_parts(tmp_path) -> None:
    _store, manifest, manifest_path, payload = _fixture(tmp_path)

    assert payload["schema_version"] == 2
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


def test_schema_v2_requires_lifecycle_evidence_sections(tmp_path) -> None:
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
