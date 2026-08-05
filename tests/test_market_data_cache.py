import json
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import pandas as pd
import pytest

from trading.market_data import (
    CacheCorruptionError,
    CsvMarketDataCache,
    MarketDataLockTimeout,
    MarketDataSeries,
    MarketDataValidationError,
)


def bars() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": [10.0, 11.0],
            "High": [12.0, 13.0],
            "Low": [9.0, 10.0],
            "Close": [11.0, 12.0],
            "Volume": [100, 200],
        },
        index=pd.to_datetime(["2026-08-03", "2026-08-04"]),
    )


def test_cache_publishes_canonical_csv_and_complete_metadata(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "active", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("^VIX")
    refreshed_at = datetime(2026, 8, 5, 1, 2, 3, tzinfo=UTC)

    cached = cache.publish(series, bars(), refresh_kind="full", refreshed_at=refreshed_at)
    loaded = cache.load(series)

    assert loaded is not None
    pd.testing.assert_frame_equal(loaded.bars, cached.bars, check_freq=False)
    assert loaded.metadata.provider == "yahoo"
    assert loaded.metadata.symbol == "^VIX"
    assert loaded.metadata.interval == "1d"
    assert loaded.metadata.adjustment_policy == "auto_adjusted"
    assert loaded.metadata.schema_version == 1
    assert loaded.metadata.data_cutoff.isoformat() == "2026-08-04"
    assert loaded.metadata.last_complete_refresh == refreshed_at
    assert loaded.metadata.last_incremental_refresh is None
    assert len(loaded.metadata.checksum) == 64
    assert cache.paths(series).csv.read_text().splitlines()[0] == (
        "Date,Open,High,Low,Close,Volume"
    )
    sidecar = json.loads(cache.paths(series).metadata.read_text())
    assert sidecar["checksum"] == loaded.metadata.checksum


def test_incremental_publish_preserves_last_complete_refresh(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "active", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    complete_at = datetime(2026, 8, 5, tzinfo=UTC)
    incremental_at = datetime(2026, 8, 6, tzinfo=UTC)
    cache.publish(series, bars(), refresh_kind="full", refreshed_at=complete_at)

    published = cache.publish(
        series,
        bars(),
        refresh_kind="incremental",
        refreshed_at=incremental_at,
    )

    assert published.metadata.last_complete_refresh == complete_at
    assert published.metadata.last_incremental_refresh == incremental_at


def test_cache_never_publishes_rows_outside_primary_sessions(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "active", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    candidate = bars()
    candidate.index = pd.to_datetime(["2026-08-07", "2026-08-08"])

    with pytest.raises(MarketDataValidationError, match="unexpected non-session"):
        cache.publish(
            series,
            candidate,
            refresh_kind="incremental",
            refreshed_at=datetime(2026, 8, 10, tzinfo=UTC),
        )

    assert cache.inspect(series).state == "missing"


def test_corrupt_cache_is_quarantined_instead_of_partially_loaded(tmp_path) -> None:
    cache = CsvMarketDataCache(tmp_path / "active", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    cache.publish(
        series,
        bars(),
        refresh_kind="incremental",
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    cache.paths(series).csv.write_text(cache.paths(series).csv.read_text() + "bad,row\n")

    with pytest.raises(CacheCorruptionError, match="checksum"):
        cache.load(series)

    assert not cache.paths(series).csv.exists()
    assert not cache.paths(series).metadata.exists()
    quarantined = list((tmp_path / "quarantine").rglob("*"))
    assert any(path.name.endswith(".csv") for path in quarantined)
    assert any(path.name.endswith(".metadata.json") for path in quarantined)


def test_per_series_lock_wait_is_bounded(tmp_path) -> None:
    cache = CsvMarketDataCache(
        tmp_path / "active",
        tmp_path / "quarantine",
        lock_timeout_seconds=0.02,
        lock_poll_seconds=0.005,
    )
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")

    with cache.lock(series), ThreadPoolExecutor(max_workers=1) as executor:
        blocked = executor.submit(cache.load, series)
        with pytest.raises(MarketDataLockTimeout, match="timed out"):
            blocked.result()


def test_partial_atomic_publish_failure_restores_previous_active_cache(
    tmp_path, monkeypatch
) -> None:
    cache = CsvMarketDataCache(tmp_path / "active", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    original = cache.publish(
        series,
        bars(),
        refresh_kind="incremental",
        refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
    )
    replacement = bars()
    replacement.loc[:, "Close"] += 0.25
    replacement.loc[:, "High"] += 0.25
    real_replace = os.replace
    failed_once = False

    def fail_metadata_replace(source, destination):
        nonlocal failed_once
        if not failed_once and destination == cache.paths(series).metadata:
            failed_once = True
            raise OSError("simulated metadata replace failure")
        return real_replace(source, destination)

    monkeypatch.setattr("trading.market_data.cache.os.replace", fail_metadata_replace)

    with pytest.raises(OSError, match="simulated metadata"):
        cache.publish(
            series,
            replacement,
            refresh_kind="incremental",
            refreshed_at=datetime(2026, 8, 6, tzinfo=UTC),
        )

    active = cache.load(series)
    assert active is not None
    pd.testing.assert_frame_equal(active.bars, original.bars)
    assert active.metadata == original.metadata


def test_temporary_files_are_cleaned_when_staging_fails(tmp_path, monkeypatch) -> None:
    cache = CsvMarketDataCache(tmp_path / "active", tmp_path / "quarantine")
    series = MarketDataSeries.yahoo_adjusted_daily("SPY")
    real_mkstemp = tempfile.mkstemp
    calls = 0

    def fail_second_temp(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated staging failure")
        return real_mkstemp(*args, **kwargs)

    monkeypatch.setattr("trading.market_data.cache.tempfile.mkstemp", fail_second_temp)

    with pytest.raises(OSError, match="simulated staging"):
        cache.publish(
            series,
            bars(),
            refresh_kind="incremental",
            refreshed_at=datetime(2026, 8, 5, tzinfo=UTC),
        )

    assert not list((tmp_path / "active").rglob(".market-data-*.tmp"))
    assert cache.inspect(series).state == "missing"
