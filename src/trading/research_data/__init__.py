"""Immutable research evidence for reproducible experiment execution."""

from trading.research_data.artifacts import ImmutableBlobCorruptionError
from trading.research_data.definitions import (
    ResearchDefinitionError,
    ResearchDefinitionStore,
)
from trading.research_data.manifest_codec import SnapshotManifestError
from trading.research_data.models import (
    DataBlobRef,
    DefinitionBlobRef,
    ExperimentTrialDeclaration,
    GarbageCollectionReport,
    ResearchDefinitionSnapshot,
    ResearchSnapshot,
    SnapshotBundleImport,
    SnapshotDataRef,
    SnapshotManifest,
)
from trading.research_data.result_schema import (
    CURRENT_RESULT_SCHEMA_VERSION,
    ResearchResult,
    ResultSchemaError,
    ResultValidity,
    ResultValidityStatus,
    build_result_payload,
    classify_result,
    load_result,
)
from trading.research_data.runs import (
    ResearchRunCoordinator,
    ResearchRunOutcome,
    RunEvidenceError,
    RunExecutionError,
    RunMode,
)
from trading.research_data.store import (
    ResearchDataStore,
    SnapshotEligibilityError,
)
from trading.research_data.trial_registry import (
    ExperimentTrialRegistry,
    TrialRegistryError,
    formal_trial_id,
    legacy_trial_id,
)

__all__ = [
    "DataBlobRef",
    "DefinitionBlobRef",
    "CURRENT_RESULT_SCHEMA_VERSION",
    "ExperimentTrialDeclaration",
    "ExperimentTrialRegistry",
    "GarbageCollectionReport",
    "ImmutableBlobCorruptionError",
    "ResearchDataStore",
    "ResearchDefinitionError",
    "ResearchDefinitionSnapshot",
    "ResearchDefinitionStore",
    "ResearchResult",
    "ResearchSnapshot",
    "ResearchRunCoordinator",
    "ResearchRunOutcome",
    "RunEvidenceError",
    "RunExecutionError",
    "RunMode",
    "ResultSchemaError",
    "ResultValidity",
    "ResultValidityStatus",
    "SnapshotDataRef",
    "SnapshotBundleImport",
    "SnapshotEligibilityError",
    "SnapshotManifest",
    "SnapshotManifestError",
    "TrialRegistryError",
    "build_result_payload",
    "classify_result",
    "formal_trial_id",
    "legacy_trial_id",
    "load_result",
]
