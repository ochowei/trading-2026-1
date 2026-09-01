import hashlib
from pathlib import Path

import pytest

from trading.research_data.paths import (
    ResultPathMigration,
    ResultPathMigrationError,
    apply_result_path_migration,
    experiment_result_directory,
    load_path_migrations,
    resolve_result_path,
)


def _entry(
    old_path: str,
    new_path: str,
    content: bytes,
    *,
    migration_version: str = "v010",
) -> ResultPathMigration:
    return ResultPathMigration(
        old_path=old_path,
        new_path=new_path,
        sha256=hashlib.sha256(content).hexdigest(),
        artifact_class="test-artifact",
        migration_version=migration_version,
    )


def test_retired_legacy_result_namespace_cannot_be_recreated() -> None:
    with pytest.raises(ResultPathMigrationError, match="result publication is retired"):
        experiment_result_directory(Path("results"), "spy_001")


def test_migration_moves_exact_bytes_and_resolves_historical_path(tmp_path) -> None:
    content = b"immutable result\n"
    source = tmp_path / "results" / "flat" / "result.json"
    source.parent.mkdir(parents=True)
    source.write_bytes(content)
    entry = _entry(
        "results/flat/result.json",
        "results/experiment-results/flat/result.json",
        content,
    )

    registry = apply_result_path_migration((entry,), repository_root=tmp_path)

    destination = tmp_path / entry.new_path
    assert registry.is_file()
    assert not source.exists()
    assert destination.read_bytes() == content
    assert resolve_result_path(source, repository_root=tmp_path) == destination.resolve()
    assert load_path_migrations(tmp_path) == (entry,)


def test_migration_retry_is_idempotent_and_removes_restored_old_alias(tmp_path) -> None:
    content = b"immutable result\n"
    source = tmp_path / "results" / "flat" / "result.json"
    source.parent.mkdir(parents=True)
    source.write_bytes(content)
    entry = _entry(
        "results/flat/result.json",
        "results/experiment-results/flat/result.json",
        content,
    )
    apply_result_path_migration((entry,), repository_root=tmp_path)
    source.parent.mkdir(parents=True)
    source.write_bytes(content)

    apply_result_path_migration((entry,), repository_root=tmp_path)

    assert not source.exists()


def test_migration_appends_one_digest_identical_retirement_hop(tmp_path) -> None:
    content = b"immutable result\n"
    flat = tmp_path / "results" / "flat" / "result.json"
    flat.parent.mkdir(parents=True)
    flat.write_bytes(content)
    categorized = "results/experiment-results/flat/result.json"
    initial = _entry(
        "results/flat/result.json",
        categorized,
        content,
        migration_version="v009",
    )
    apply_result_path_migration((initial,), repository_root=tmp_path)
    retirement = _entry(
        categorized,
        "legacy/results/flat/result.json",
        content,
    )

    apply_result_path_migration((initial, retirement), repository_root=tmp_path)

    terminal = tmp_path / retirement.new_path
    assert not (tmp_path / categorized).exists()
    assert resolve_result_path(flat, repository_root=tmp_path) == terminal.resolve()
    assert (
        resolve_result_path(tmp_path / categorized, repository_root=tmp_path) == terminal.resolve()
    )

    # A mutable writer may continue at the categorized identity after its migration-time bytes
    # have been retired. Historical callers still follow the two-hop chain, while current callers
    # resolve the physically present active registry before consulting migrations.
    active_content = b"append-only active registry\n"
    active = tmp_path / categorized
    active.parent.mkdir(parents=True, exist_ok=True)
    active.write_bytes(active_content)

    assert resolve_result_path(flat, repository_root=tmp_path) == terminal.resolve()
    assert resolve_result_path(active, repository_root=tmp_path) == active.resolve()
    assert active.read_bytes() == active_content
    assert load_path_migrations(tmp_path) == tuple(
        sorted((initial, retirement), key=lambda entry: entry.old_path)
    )


@pytest.mark.parametrize(
    ("raw_entries", "message"),
    [
        (
            (
                ("results/a.json", "results/b.json"),
                ("results/b.json", "results/c.json"),
                ("results/c.json", "legacy/results/a.json"),
            ),
            "hop limit",
        ),
        (
            (
                ("results/a.json", "results/b.json"),
                ("results/a.json", "results/c.json"),
            ),
            "duplicate old paths",
        ),
    ],
)
def test_migration_rejects_unsafe_registry(tmp_path, raw_entries, message: str) -> None:
    content = b"x"
    entries = (_entry(old_path, new_path, content) for old_path, new_path in raw_entries)

    with pytest.raises(ResultPathMigrationError, match=message):
        apply_result_path_migration(tuple(entries), repository_root=tmp_path)


def test_resolver_rejects_destination_digest_drift(tmp_path) -> None:
    content = b"immutable result\n"
    source = tmp_path / "results" / "flat" / "result.json"
    source.parent.mkdir(parents=True)
    source.write_bytes(content)
    entry = _entry(
        "results/flat/result.json",
        "results/experiment-results/flat/result.json",
        content,
    )
    apply_result_path_migration((entry,), repository_root=tmp_path)
    (tmp_path / entry.new_path).write_bytes(b"drifted\n")

    with pytest.raises(ResultPathMigrationError, match="digest drifted"):
        resolve_result_path(source, repository_root=tmp_path)


def test_migration_rolls_back_destinations_when_publication_fails(
    tmp_path,
    monkeypatch,
) -> None:
    content = b"immutable result\n"
    source = tmp_path / "results" / "flat" / "result.json"
    source.parent.mkdir(parents=True)
    source.write_bytes(content)
    entry = _entry(
        "results/flat/result.json",
        "results/experiment-results/flat/result.json",
        content,
    )

    def fail_write(_path, _content) -> None:
        raise OSError("simulated registry write failure")

    monkeypatch.setattr("trading.research_data.paths._atomic_write", fail_write)

    with pytest.raises(OSError, match="simulated registry write failure"):
        apply_result_path_migration((entry,), repository_root=tmp_path)

    assert source.read_bytes() == content
    assert not (tmp_path / entry.new_path).exists()
