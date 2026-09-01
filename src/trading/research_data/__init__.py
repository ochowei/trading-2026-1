"""Immutable research evidence for reproducible experiment execution."""

from trading.research_data.artifacts import ImmutableBlobCorruptionError
from trading.research_data.definitions import (
    ResearchDefinitionError,
    ResearchDefinitionStore,
)
from trading.research_data.evidence import (
    QualificationEvidenceStore,
    ResearchEvidenceStore,
    SharedQualificationEvidenceSnapshot,
)
from trading.research_data.manifest_codec import SnapshotManifestError
from trading.research_data.migration import (
    MIGRATION_RESULT_SCHEMA_VERSION,
    MIGRATION_RESULT_SUFFIX,
    MigrationResultError,
    MigrationResultStore,
)
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
from trading.research_data.parity import MigrationParityEvidenceError, MigrationParityStore
from trading.research_data.paths import (
    ResultPathMigration,
    ResultPathMigrationError,
    qualification_evidence_directory,
    research_evidence_directory,
    research_trial_directory,
    resolve_result_path,
    trial_registry_path,
)
from trading.research_data.qualification_registry import (
    QualificationRegistry,
    QualificationRegistryError,
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
from trading.research_data.shared_qualification_state import (
    CROSS_CHAIN_PLAN_ADMINISTRATION_CAPABILITY,
    DEFAULT_LOGICAL_REGISTRY_IDENTITY,
    SHARED_QUALIFICATION_STATE_CAPABILITY,
    MigrationPreview,
    MigrationSource,
    SharedMigrationRequest,
    SharedQualificationPaths,
    SharedQualificationState,
    SharedQualificationStateError,
    resolve_git_repository_identity,
    resolve_study_qualification_registry_path,
    resolve_workflow_qualification_registry_path,
    shared_qualification_paths,
)
from trading.research_data.store import (
    ResearchDataStore,
    SnapshotEligibilityError,
)
from trading.research_data.trial_registry import (
    ExperimentTrialRegistry,
    OutcomeFreeTrialRegistration,
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
    "OutcomeFreeTrialRegistration",
    "GarbageCollectionReport",
    "ImmutableBlobCorruptionError",
    "MIGRATION_RESULT_SCHEMA_VERSION",
    "MIGRATION_RESULT_SUFFIX",
    "MigrationParityEvidenceError",
    "MigrationParityStore",
    "MigrationResultError",
    "MigrationResultStore",
    "ResearchDataStore",
    "ResearchEvidenceStore",
    "QualificationEvidenceStore",
    "SharedQualificationEvidenceSnapshot",
    "ResearchDefinitionError",
    "ResearchDefinitionSnapshot",
    "ResearchDefinitionStore",
    "QualificationRegistry",
    "QualificationRegistryError",
    "CROSS_CHAIN_PLAN_ADMINISTRATION_CAPABILITY",
    "DEFAULT_LOGICAL_REGISTRY_IDENTITY",
    "SHARED_QUALIFICATION_STATE_CAPABILITY",
    "MigrationPreview",
    "MigrationSource",
    "SharedMigrationRequest",
    "SharedQualificationPaths",
    "SharedQualificationState",
    "SharedQualificationStateError",
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
    "ResultPathMigration",
    "ResultPathMigrationError",
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
    "qualification_evidence_directory",
    "research_evidence_directory",
    "research_trial_directory",
    "resolve_result_path",
    "resolve_git_repository_identity",
    "resolve_study_qualification_registry_path",
    "resolve_workflow_qualification_registry_path",
    "shared_qualification_paths",
    "trial_registry_path",
]
