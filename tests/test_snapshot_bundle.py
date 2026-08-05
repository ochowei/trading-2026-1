import subprocess
from datetime import UTC, date, datetime

import pandas as pd
import pytest

from trading.market_data import (
    CsvMarketDataCache,
    MarketDataRequirement,
    MarketDataSeries,
    RefreshKind,
    SignalDecisionTime,
)
from trading.research_data import (
    ImmutableBlobCorruptionError,
    ResearchDataStore,
    ResearchDefinitionStore,
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


def test_export_import_restores_manifest_data_definition_and_result(tmp_path) -> None:
    source_root = tmp_path / "source"
    source_root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=source_root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=source_root,
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=source_root, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-qm", "baseline"],
        cwd=source_root,
        check=True,
    )
    cache = CsvMarketDataCache(source_root / "cache", source_root / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache.publish(
        series,
        bars(),
        refresh_kind=RefreshKind.FULL,
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    blob_root = source_root / "blobs"
    definitions = ResearchDefinitionStore(blob_root)
    detector = source_root / "detector.py"
    strategy = source_root / "strategy.py"
    backtester = source_root / "backtester.py"
    detector.write_text("def signal(value):\n    return value > 0.2\n", encoding="utf-8")
    strategy.write_text("class Strategy:\n    pass\n", encoding="utf-8")
    backtester.write_text("class Backtester:\n    pass\n", encoding="utf-8")
    definition = definitions.capture(
        resolved_config={"ticker": "SPY"},
        sources={
            "strategy": strategy,
            "detector": detector,
            "backtester": backtester,
        },
        execution_engine_version="execution-v1",
        dependency_versions={"pandas": "2.3.1"},
    )
    store = ResearchDataStore(
        blob_root,
        now=lambda: datetime(2026, 8, 5, 12, tzinfo=UTC),
    )
    manifest = store.create_snapshot(
        cache,
        (MarketDataRequirement(series, date(2026, 8, 3), role="primary"),),
        SignalDecisionTime.for_primary_session(date(2026, 8, 4)),
        definition=definition.blob,
    )
    result = {
        "signals": ["2026-08-04"],
        "trades": [{"entry": 12.0}],
        "metrics": {"last_close": 12.0},
    }
    bundle_path = tmp_path / "portable.snapshot.zip"

    store.export_bundle(manifest, bundle_path, result=result)
    target_root = tmp_path / "target" / "blobs"
    imported = ResearchDataStore(target_root).import_bundle(
        bundle_path,
        manifest_path=tmp_path / "target" / "results" / "run.snapshot.json",
    )

    assert imported.manifest == manifest
    assert imported.result == result
    assert list(ResearchDataStore(target_root).load_snapshot(imported.manifest_path).bundle) == [
        series
    ]
    replay_bundle = ResearchDataStore(target_root).load_snapshot(imported.manifest_path).bundle
    replay_frame = replay_bundle[series]
    replayed = {
        "signals": [replay_frame.index[-1].strftime("%Y-%m-%d")],
        "trades": [{"entry": float(replay_frame.iloc[-1]["Close"])}],
        "metrics": {"last_close": float(replay_frame.iloc[-1]["Close"])},
    }
    assert replayed == result
    restored_definition = ResearchDefinitionStore(target_root).load(manifest.definition)
    assert restored_definition["sources"]["detector"] == detector.read_text(encoding="utf-8")

    collision_root = tmp_path / "collision" / "blobs"
    collision_store = ResearchDataStore(collision_root)
    collision_path = collision_store.data_blob_path(manifest.data[0].blob.digest)
    collision_path.parent.mkdir(parents=True, exist_ok=True)
    collision_path.write_bytes(b"different immutable content")

    with pytest.raises(ImmutableBlobCorruptionError, match="collision or corruption"):
        collision_store.import_bundle(
            bundle_path,
            manifest_path=tmp_path / "collision" / "run.snapshot.json",
        )

    assert collision_path.read_bytes() == b"different immutable content"
