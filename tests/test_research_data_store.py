import hashlib
import json
import os
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta

import pandas as pd
import pytest

from trading.market_data import (
    AvailabilityPolicy,
    CsvMarketDataCache,
    MarketDataRequirement,
    MarketDataSeries,
    RefreshKind,
    SignalDecisionTime,
)
from trading.market_data.availability import GapAwareAvailabilityPolicy
from trading.research_data import (
    DefinitionBlobRef,
    ImmutableBlobCorruptionError,
    ResearchDataStore,
    SnapshotEligibilityError,
    SnapshotManifestError,
)


def bars() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": [10.0, 11.0],
            "High": [12.0, 13.0],
            "Low": [9.0, 10.0],
            "Close": [11.0, 12.0],
            "Volume": [100.0, 200.0],
        },
        index=pd.to_datetime(["2026-08-03", "2026-08-04"]),
    )


def auxiliary_bars() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": [9.0, 10.0, 11.0],
            "High": [10.0, 12.0, 13.0],
            "Low": [8.0, 9.0, 10.0],
            "Close": [9.0, 11.0, 12.0],
            "Volume": [90.0, 100.0, 200.0],
        },
        index=pd.to_datetime(["2026-07-31", "2026-08-03", "2026-08-04"]),
    )


def test_identical_complete_cache_bytes_share_one_immutable_data_blob(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    first_series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    second_series = MarketDataSeries.yahoo_adjusted_daily("QQQ")
    for series in (first_series, second_series):
        cache.publish(
            series,
            bars(),
            refresh_kind=RefreshKind.FULL,
            refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
        )
    store = ResearchDataStore(tmp_path / "research-data")

    first = store.publish_cache_series(cache, first_series)
    second = store.publish_cache_series(cache, second_series)

    assert first.digest == second.digest
    assert first.byte_count == second.byte_count
    assert store.data_blob_path(first.digest) == store.data_blob_path(second.digest)
    assert len(list((tmp_path / "research-data" / "data").rglob("*.csv"))) == 1


def test_snapshot_publication_rejects_incrementally_mixed_cache_generation(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.INCREMENTAL,
        refreshed_at=datetime(2026, 8, 6, tzinfo=UTC),
    )

    with pytest.raises(SnapshotEligibilityError, match="not a fully refreshed"):
        ResearchDataStore(tmp_path / "research-data").publish_cache_series(cache, series)

    assert not list((tmp_path / "research-data").rglob("*.csv"))


def test_corrupted_immutable_blob_is_never_replaced_from_current_cache(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    store = ResearchDataStore(tmp_path / "research-data")
    reference = store.publish_cache_series(cache, series)
    blob_path = store.data_blob_path(reference.digest)
    blob_path.write_bytes(b"corrupt immutable evidence")

    with pytest.raises(ImmutableBlobCorruptionError, match="collision or corruption"):
        store.publish_cache_series(cache, series)

    assert blob_path.read_bytes() == b"corrupt immutable evidence"


def test_snapshot_manifest_records_every_declared_series_and_policy(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    auxiliary = MarketDataSeries.yahoo_adjusted_daily("^VIX")
    cache.publish(
        primary,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    cache.publish(
        auxiliary,
        auxiliary_bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    policy = AvailabilityPolicy(
        publication_lag_sessions=1,
        max_observation_lag_sessions=2,
        publication_time_known=False,
    )
    requirements = (
        MarketDataRequirement(primary, date(2026, 8, 3), role="primary"),
        MarketDataRequirement(
            auxiliary,
            date(2026, 8, 3),
            role="auxiliary",
            availability_policy=policy,
        ),
    )
    store = ResearchDataStore(
        tmp_path / "research-data",
        now=lambda: datetime(2026, 8, 5, 12, tzinfo=UTC),
    )

    manifest = store.create_snapshot(
        cache,
        requirements,
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
    )

    assert len(manifest.snapshot_id) == 64
    assert manifest.decision_time.session == date(2026, 8, 4)
    assert [entry.series for entry in manifest.data] == [primary, auxiliary]
    assert manifest.data[0].role == "primary"
    assert manifest.data[0].availability_policy is None
    assert manifest.data[1].role == "auxiliary"
    assert manifest.data[1].availability_policy == policy
    assert all(entry.data_cutoff == date(2026, 8, 4) for entry in manifest.data)
    assert all(
        entry.blob.digest == cache.load(entry.series).metadata.checksum for entry in manifest.data
    )


def test_latest_manifest_discovery_requires_the_exact_definition(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    times = iter(
        (
            datetime(2026, 8, 5, 10, tzinfo=UTC),
            datetime(2026, 8, 5, 11, tzinfo=UTC),
            datetime(2026, 8, 5, 12, tzinfo=UTC),
            datetime(2026, 8, 5, 13, tzinfo=UTC),
        )
    )
    store = ResearchDataStore(tmp_path / "research-data", now=lambda: next(times))
    requirement = MarketDataRequirement(series, date(2026, 8, 3), role="primary")
    decision_time = SignalDecisionTime.for_primary_session(date(2026, 8, 4))
    definition = DefinitionBlobRef("d" * 64, 1, "f" * 64)
    other_definition = DefinitionBlobRef("e" * 64, 1, "0" * 64)
    manifest_root = tmp_path / "results" / "experiment"

    first = store.create_snapshot(
        cache,
        (requirement,),
        decision_time,
        definition=definition,
    )
    second = store.create_snapshot(
        cache,
        (requirement,),
        decision_time,
        definition=definition,
    )
    unrelated = store.create_snapshot(
        cache,
        (requirement,),
        decision_time,
        definition=other_definition,
    )
    first_path = store.write_manifest(first, manifest_root / f"{first.snapshot_id}.snapshot.json")
    second_path = store.write_manifest(
        second,
        manifest_root / f"{second.snapshot_id}.snapshot.json",
    )
    store.write_manifest(
        unrelated,
        manifest_root / f"{unrelated.snapshot_id}.snapshot.json",
    )

    same_fingerprint = DefinitionBlobRef("e" * 64, 1, definition.fingerprint)
    semantic_match = store.create_snapshot(
        cache,
        (requirement,),
        decision_time,
        definition=same_fingerprint,
    )
    store.write_manifest(
        semantic_match,
        manifest_root / f"{semantic_match.snapshot_id}.snapshot.json",
    )

    assert first_path != second_path
    assert store.latest_manifest_for_definition(manifest_root, definition) == second_path


def test_snapshot_manifest_reconstructs_policy_safe_bundle_without_provider(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    auxiliary = MarketDataSeries.yahoo_adjusted_daily("^VIX")
    cache.publish(
        primary,
        auxiliary_bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    cache.publish(
        auxiliary,
        auxiliary_bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    requirements = (
        MarketDataRequirement(primary, date(2026, 8, 3), role="primary"),
        MarketDataRequirement(
            auxiliary,
            date(2026, 8, 3),
            role="auxiliary",
            availability_policy=AvailabilityPolicy(1, 2, False),
        ),
    )
    root = tmp_path / "research-data"
    store = ResearchDataStore(
        root,
        now=lambda: datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    manifest = store.create_snapshot(
        cache,
        requirements,
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
    )
    manifest_path = tmp_path / "results" / "experiment" / "data.snapshot.json"
    store.write_manifest(manifest, manifest_path)

    loaded = ResearchDataStore(root).load_snapshot(manifest_path)

    assert loaded.manifest == manifest
    assert list(loaded.bundle[primary].index) == list(bars().index)
    assert list(loaded.bundle[auxiliary]["ObservationDate"]) == [
        pd.Timestamp("2026-07-31"),
        pd.Timestamp("2026-08-03"),
    ]
    assert list(loaded.bundle[auxiliary].index) == [
        pd.Timestamp("2026-08-03"),
        pd.Timestamp("2026-08-04"),
    ]

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["data"][0]["data_cutoff"] = "2026-08-03"
    body = {key: value for key, value in payload.items() if key != "snapshot_id"}
    payload["snapshot_id"] = hashlib.sha256(
        (json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    ).hexdigest()
    tampered_path = tmp_path / "results" / "experiment" / "tampered-snapshot.json"
    tampered_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(SnapshotManifestError, match="cutoff"):
        ResearchDataStore(root).load_snapshot(tampered_path)


def test_snapshot_rejects_semantically_valid_noncanonical_csv_blob(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    store = ResearchDataStore(tmp_path / "research-data")
    manifest = store.create_snapshot(
        cache,
        (MarketDataRequirement(series, date(2026, 8, 3), role="primary"),),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
    )
    canonical_path = store.write_manifest(manifest, tmp_path / "canonical.snapshot.json")
    payload = json.loads(canonical_path.read_text(encoding="utf-8"))
    noncanonical = (
        bars()
        .to_csv(
            index=True,
            index_label="Date",
            date_format="%Y-%m-%d",
            float_format="%.1f",
            lineterminator="\n",
        )
        .encode("utf-8")
    )
    digest = hashlib.sha256(noncanonical).hexdigest()
    blob_payload = payload["data"][0]["blob"]
    blob_payload["digest"] = digest
    blob_payload["byte_count"] = len(noncanonical)
    body = {key: value for key, value in payload.items() if key != "snapshot_id"}
    payload["snapshot_id"] = hashlib.sha256(
        (json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    ).hexdigest()
    noncanonical_manifest = tmp_path / "noncanonical.snapshot.json"
    noncanonical_manifest.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    blob_path = store.data_blob_path(digest)
    blob_path.parent.mkdir(parents=True, exist_ok=True)
    blob_path.write_bytes(noncanonical)

    with pytest.raises(ImmutableBlobCorruptionError, match="canonically serialized"):
        store.load_snapshot(noncanonical_manifest)


def test_manifest_publication_rejects_false_snapshot_identity(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    store = ResearchDataStore(tmp_path / "research-data")
    manifest = store.create_snapshot(
        cache,
        (MarketDataRequirement(series, date(2026, 8, 3), role="primary"),),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
    )
    false_manifest = replace(manifest, snapshot_id="0" * 64)
    manifest_path = tmp_path / "false.snapshot.json"
    bundle_path = tmp_path / "false.snapshot.zip"

    with pytest.raises(SnapshotManifestError, match="identity"):
        store.write_manifest(false_manifest, manifest_path)
    with pytest.raises(SnapshotManifestError, match="identity"):
        store.export_bundle(false_manifest, bundle_path)

    assert not manifest_path.exists()
    assert not bundle_path.exists()


def test_manifest_publication_requires_retained_snapshot_suffix(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    store = ResearchDataStore(tmp_path / "research-data")
    manifest = store.create_snapshot(
        cache,
        (MarketDataRequirement(series, date(2026, 8, 3), role="primary"),),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
    )
    unsafe_path = tmp_path / "results" / "manifest.json"

    with pytest.raises(SnapshotManifestError, match=r"\.snapshot\.json"):
        store.write_manifest(manifest, unsafe_path)

    assert not unsafe_path.exists()


def test_manifest_parser_rejects_non_boolean_availability_flag(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    auxiliary = MarketDataSeries.yahoo_adjusted_daily("^VIX")
    for series in (primary, auxiliary):
        cache.publish(
            series,
            bars(),
            refresh_kind=RefreshKind.FULL,
            refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
        )
    store = ResearchDataStore(tmp_path / "research-data")
    manifest = store.create_snapshot(
        cache,
        (
            MarketDataRequirement(primary, date(2026, 8, 3), role="primary"),
            MarketDataRequirement(
                auxiliary,
                date(2026, 8, 3),
                role="auxiliary",
                availability_policy=AvailabilityPolicy(1, 2, False),
            ),
        ),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
    )
    manifest_path = store.write_manifest(manifest, tmp_path / "data.snapshot.json")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["data"][1]["availability_policy"]["publication_time_known"] = "false"
    body = {key: value for key, value in payload.items() if key != "snapshot_id"}
    payload["snapshot_id"] = hashlib.sha256(
        (json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    ).hexdigest()
    malformed_path = tmp_path / "malformed.snapshot.json"
    malformed_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(SnapshotManifestError, match="publication_time_known"):
        store.load_manifest(malformed_path)


def test_manifest_round_trip_preserves_explicit_excess_lag_mode(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    auxiliary = MarketDataSeries.yahoo_adjusted_daily("^VIX")
    for series in (primary, auxiliary):
        cache.publish(
            series,
            bars(),
            refresh_kind=RefreshKind.FULL,
            refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
        )
    store = ResearchDataStore(tmp_path / "research-data")
    policy = GapAwareAvailabilityPolicy(
        1,
        2,
        False,
    )
    manifest = store.create_snapshot(
        cache,
        (
            MarketDataRequirement(primary, date(2026, 8, 3), role="primary"),
            MarketDataRequirement(
                auxiliary,
                date(2026, 8, 3),
                role="auxiliary",
                availability_policy=policy,
            ),
        ),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
    )

    path = store.write_manifest(manifest, tmp_path / "marked.snapshot.json")
    loaded = store.load_manifest(path)

    assert loaded.data[1].availability_policy == policy
    assert (
        json.loads(path.read_text())["data"][1]["availability_policy"]["excess_lag_mode"]
        == "mark_unavailable"
    )


def test_manifest_parser_rejects_non_integer_blob_count(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    store = ResearchDataStore(tmp_path / "research-data")
    manifest = store.create_snapshot(
        cache,
        (MarketDataRequirement(series, date(2026, 8, 3), role="primary"),),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
    )
    manifest_path = store.write_manifest(manifest, tmp_path / "data.snapshot.json")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["data"][0]["blob"]["row_count"] = 2.5
    body = {key: value for key, value in payload.items() if key != "snapshot_id"}
    payload["snapshot_id"] = hashlib.sha256(
        (json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    ).hexdigest()
    malformed_path = tmp_path / "malformed.snapshot.json"
    malformed_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(SnapshotManifestError, match="row_count"):
        store.load_manifest(malformed_path)


def test_manifest_parser_rejects_unknown_noncanonical_content(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    store = ResearchDataStore(tmp_path / "research-data")
    manifest = store.create_snapshot(
        cache,
        (MarketDataRequirement(series, date(2026, 8, 3), role="primary"),),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
    )
    manifest_path = store.write_manifest(manifest, tmp_path / "data.snapshot.json")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["undeclared_context"] = {"ignored": True}
    malformed_path = tmp_path / "unknown.snapshot.json"
    malformed_path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(SnapshotManifestError, match="canonical"):
        store.load_manifest(malformed_path)


def test_garbage_collection_is_reference_aware_dry_run_with_grace_period(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    referenced_series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    orphan_series = MarketDataSeries.yahoo_adjusted_daily("QQQ")
    cache.publish(
        referenced_series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    different = bars()
    different.loc[:, "Open"] += 1
    different.loc[:, "High"] += 1
    different.loc[:, "Low"] += 1
    different.loc[:, "Close"] += 1
    cache.publish(
        orphan_series,
        different,
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    store = ResearchDataStore(
        tmp_path / "research-data",
        now=lambda: datetime(2026, 8, 20, tzinfo=UTC),
    )
    manifest = store.create_snapshot(
        cache,
        (MarketDataRequirement(referenced_series, date(2026, 8, 3), role="primary"),),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
    )
    manifest_path = store.write_manifest(manifest, tmp_path / "run.snapshot.json")
    orphan = store.publish_cache_series(cache, orphan_series)
    orphan_path = store.data_blob_path(orphan.digest)
    old = datetime(2026, 8, 1, tzinfo=UTC).timestamp()
    os.utime(orphan_path, (old, old))

    dry_run = store.collect_garbage(
        manifest_roots=(manifest_path.parent,),
        grace_period=timedelta(days=7),
    )

    assert dry_run.candidates == (orphan_path,)
    assert dry_run.deleted == ()
    assert orphan_path.exists()
    assert store.data_blob_path(manifest.data[0].blob.digest).exists()

    applied = store.collect_garbage(
        manifest_roots=(manifest_path.parent,),
        grace_period=timedelta(days=7),
        apply=True,
    )

    assert applied.deleted == (orphan_path,)
    assert not orphan_path.exists()
    assert store.data_blob_path(manifest.data[0].blob.digest).exists()


def test_garbage_collection_discovers_all_manifests_under_retained_roots(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "cache", tmp_path / "quarantine")
    primary = MarketDataSeries.yahoo_adjusted_daily("SPY")
    auxiliary = MarketDataSeries.yahoo_adjusted_daily("QQQ")
    primary_bars = bars()
    auxiliary_bars = bars()
    auxiliary_bars.loc[:, ["Open", "High", "Low", "Close"]] += 10
    for series, frame in ((primary, primary_bars), (auxiliary, auxiliary_bars)):
        cache.publish(
            series,
            frame,
            refresh_kind=RefreshKind.FULL,
            refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
        )
    store = ResearchDataStore(
        tmp_path / "research-data",
        now=lambda: datetime(2026, 8, 20, tzinfo=UTC),
    )
    results_root = tmp_path / "results"
    for experiment, series in (("first", primary), ("second", auxiliary)):
        manifest = store.create_snapshot(
            cache,
            (MarketDataRequirement(series, date(2026, 8, 3), role="primary"),),
            SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
        )
        store.write_manifest(
            manifest,
            results_root / experiment / "data.snapshot.json",
        )
        blob_path = store.data_blob_path(manifest.data[0].blob.digest)
        old = datetime(2026, 8, 1, tzinfo=UTC).timestamp()
        os.utime(blob_path, (old, old))

    report = store.collect_garbage(
        manifest_roots=(results_root,),
        grace_period=timedelta(days=7),
        apply=True,
    )

    assert report.candidates == ()
    assert report.deleted == ()
    assert len(report.protected) == 2
