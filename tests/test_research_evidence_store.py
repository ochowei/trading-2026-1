import hashlib

import pytest

from trading.research_data import (
    ImmutableBlobCorruptionError,
    QualificationEvidenceStore,
    ResearchEvidenceStore,
)


def test_research_evidence_store_publishes_and_resolves_exact_bytes(tmp_path) -> None:
    content = b"# Frozen evidence\n\nExact retained bytes.\n"
    digest = hashlib.sha256(content).hexdigest()
    store = ResearchEvidenceStore(tmp_path / "results" / "research-evidence")

    path = store.publish(content, digest=digest)

    assert path == store.path_for(digest)
    assert store.resolve(digest) == content
    assert list(path.parent.iterdir()) == [path]


def test_research_evidence_store_rejects_wrong_digest_and_existing_drift(tmp_path) -> None:
    content = b"# Frozen evidence\n"
    digest = hashlib.sha256(content).hexdigest()
    store = ResearchEvidenceStore(tmp_path / "results" / "research-evidence")

    with pytest.raises(ImmutableBlobCorruptionError, match="requested digest"):
        store.publish(content, digest="0" * 64)

    path = store.publish(content, digest=digest)
    path.write_bytes(b"changed\n")
    with pytest.raises(ImmutableBlobCorruptionError, match="checksum verification"):
        store.resolve(digest)


def test_qualification_evidence_rejects_mismatched_path_and_source_identity(tmp_path) -> None:
    store = QualificationEvidenceStore(tmp_path / "results" / "qualification-evidence")

    with pytest.raises(ValueError, match="differs from its declared source identity"):
        store.publish_registry(
            tmp_path / "state" / "other.json",
            repository_root=tmp_path,
            source_registry_identity="state/qualification.json",
        )
