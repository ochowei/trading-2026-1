import hashlib

import pytest

from trading.research_data.paths import (
    ResultPathMigration,
    ResultPathMigrationError,
    apply_result_path_migration,
    load_path_migrations,
    resolve_result_path,
)


def _entry(old_path: str, new_path: str, content: bytes) -> ResultPathMigration:
    return ResultPathMigration(
        old_path=old_path,
        new_path=new_path,
        sha256=hashlib.sha256(content).hexdigest(),
        artifact_class="test-artifact",
    )


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


@pytest.mark.parametrize(
    ("first_new", "second_old", "message"),
    [
        ("results/b.json", "results/b.json", "chain or cycle"),
        ("results/c.json", "results/a.json", "duplicate old paths"),
    ],
)
def test_migration_rejects_non_one_hop_registry(
    tmp_path,
    first_new: str,
    second_old: str,
    message: str,
) -> None:
    content = b"x"
    entries = (
        _entry("results/a.json", first_new, content),
        _entry(second_old, "results/d.json", content),
    )

    with pytest.raises(ResultPathMigrationError, match=message):
        apply_result_path_migration(entries, repository_root=tmp_path)


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
