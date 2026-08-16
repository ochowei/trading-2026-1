"""Recoverable cross-registry publication for frozen qualification plans."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from trading.core.accounting import canonical_json_bytes, parse_timestamp, timestamp_text
from trading.core.ledger_storage import atomic_write, locked_file
from trading.core.qualification import HistoricalQualificationPlan
from trading.research_data import (
    ExperimentTrialRegistry,
    OutcomeFreeTrialRegistration,
    QualificationRegistry,
)
from trading.research_data.qualification_registry import (
    historical_plan_from_payload,
    historical_plan_payload,
)

QUALIFICATION_TRANSACTION_SCHEMA_VERSION = 1


class QualificationTransactionError(RuntimeError):
    """A prepared qualification transaction conflicts with the requested operation."""


def publish_qualification_plan_transaction(
    *,
    plan: HistoricalQualificationPlan,
    registrations: tuple[OutcomeFreeTrialRegistration, ...],
    registered_at: datetime,
    trial_registry_path: Path,
    qualification_registry_path: Path,
    after_trial_commit: Callable[[], None] | None = None,
) -> tuple[str, ...]:
    """Publish one family plus plan as an idempotent, recoverable transaction.

    POSIX cannot atomically replace two independent registry files.  The durable journal is
    therefore the commit decision: readers and retries can distinguish a prepared operation from
    a completed one, and a retry always finishes the exact prepared bytes before doing new work.
    """
    journal_path = _journal_path(qualification_registry_path)
    lock_path = journal_path.with_name(f".{journal_path.name}.lock")
    operation = _operation_payload(
        plan=plan,
        registrations=registrations,
        registered_at=registered_at,
        trial_registry_path=trial_registry_path,
        qualification_registry_path=qualification_registry_path,
    )
    with locked_file(lock_path, 10.0):
        if journal_path.exists():
            prepared = _load_journal(journal_path)
            if prepared != operation:
                raise QualificationTransactionError(
                    "a different qualification transaction is awaiting recovery"
                )
        else:
            atomic_write(journal_path, canonical_json_bytes(operation), replace=False)

        committed_ids = _commit_prepared_operation(
            operation,
            after_trial_commit=after_trial_commit,
        )
        journal_path.unlink()
        return committed_ids


def recover_qualification_plan_transaction(
    qualification_registry_path: Path,
    *,
    expected_study_path: str | None = None,
    expected_trial_registry_path: Path | None = None,
    expected_qualification_registry_path: Path | None = None,
    expected_approved_by: str | None = None,
    expected_contamination_declaration: str | None = None,
) -> HistoricalQualificationPlan | None:
    """Finish an interrupted matching operation and return its exact plan."""
    journal_path = _journal_path(qualification_registry_path)
    if not journal_path.exists():
        return None
    lock_path = journal_path.with_name(f".{journal_path.name}.lock")
    with locked_file(lock_path, 10.0):
        if not journal_path.exists():
            return None
        operation = _load_journal(journal_path)
        plan = historical_plan_from_payload(_mapping(operation["plan"]))
        if expected_study_path is not None and (
            plan.study_identity is None or plan.study_identity.study_path != expected_study_path
        ):
            raise QualificationTransactionError(
                "pending qualification transaction belongs to a different study"
            )
        if (
            expected_trial_registry_path is not None
            and Path(str(operation["trial_registry_path"]))
            != expected_trial_registry_path.resolve()
        ):
            raise QualificationTransactionError(
                "pending qualification transaction uses a different trial registry"
            )
        if (
            expected_qualification_registry_path is not None
            and Path(str(operation["qualification_registry_path"]))
            != expected_qualification_registry_path.resolve()
        ):
            raise QualificationTransactionError(
                "pending qualification transaction uses a different qualification registry"
            )
        if expected_approved_by is not None and (
            plan.study_identity is None
            or plan.study_identity.operation_approved_by != expected_approved_by
        ):
            raise QualificationTransactionError(
                "pending qualification transaction has different human authorization"
            )
        if expected_contamination_declaration is not None and (
            plan.study_identity is None
            or plan.study_identity.contamination_declaration != expected_contamination_declaration
        ):
            raise QualificationTransactionError(
                "pending qualification transaction has a different contamination declaration"
            )
        _commit_prepared_operation(operation)
        journal_path.unlink()
        return plan


def _commit_prepared_operation(
    operation: dict[str, Any],
    *,
    after_trial_commit: Callable[[], None] | None = None,
) -> tuple[str, ...]:
    registrations = tuple(
        OutcomeFreeTrialRegistration(
            experiment_family=str(item["experiment_family"]),
            definition_fingerprint=str(item["definition_fingerprint"]),
            experiment_name=str(item["experiment_name"]),
            hypothesis=str(item.get("hypothesis", "")),
        )
        for item in _list_of_mappings(operation["registrations"])
    )
    trial_registry = ExperimentTrialRegistry(Path(str(operation["trial_registry_path"])))
    plan = historical_plan_from_payload(_mapping(operation["plan"]))
    if plan.study_identity is not None and plan.study_identity.operation_approved_by is not None:
        if (
            plan.study_identity.trial_registry_path != operation["trial_registry_path"]
            or plan.study_identity.qualification_registry_path
            != operation["qualification_registry_path"]
        ):
            raise QualificationTransactionError(
                "qualification journal registry paths differ from durable plan identity"
            )
    boundary = plan.forward_selection_epoch or plan.retrospective_selection_checkpoint
    if boundary is None:
        raise QualificationTransactionError("prepared plan has no frozen selection boundary")

    def commit_qualification(
        trial_state: dict[str, object],
        _trial_ids: tuple[str, ...],
    ) -> None:
        actual = _family_trial_ids_at_boundary(
            trial_state,
            experiment_family=plan.experiment_family,
            registered_at=parse_timestamp(str(operation["registered_at"])),
        )
        if actual != tuple(sorted(boundary.included_trial_ids)):
            raise QualificationTransactionError(
                "trial registry family universe differs from the prepared plan"
            )
        if after_trial_commit is not None:
            after_trial_commit()
        registry = QualificationRegistry(
            Path(str(operation["qualification_registry_path"])),
            now=lambda: parse_timestamp(str(operation["registered_at"])),
        )
        registry.register_historical_plan(plan)

    return trial_registry.register_trials_with_locked_callback(
        registrations,
        registered_at=parse_timestamp(str(operation["registered_at"])),
        callback=commit_qualification,
    )


def _family_trial_ids_at_boundary(
    state: dict[str, object],
    *,
    experiment_family: str,
    registered_at: datetime,
) -> tuple[str, ...]:
    trials = state.get("trials")
    if not isinstance(trials, list):
        raise QualificationTransactionError("trial registry family universe is malformed")
    result: list[str] = []
    for trial in trials:
        if (
            not isinstance(trial, dict)
            or trial.get("legacy") is True
            or trial.get("experiment_family") != experiment_family
        ):
            continue
        trial_id = trial.get("trial_id")
        first_registered_at = trial.get("first_registered_at")
        if not isinstance(trial_id, str) or not isinstance(first_registered_at, str):
            raise QualificationTransactionError("trial registry family identity is malformed")
        if parse_timestamp(first_registered_at) <= registered_at:
            result.append(trial_id)
    return tuple(sorted(result))


def _operation_payload(
    *,
    plan: HistoricalQualificationPlan,
    registrations: tuple[OutcomeFreeTrialRegistration, ...],
    registered_at: datetime,
    trial_registry_path: Path,
    qualification_registry_path: Path,
) -> dict[str, Any]:
    return {
        "schema_version": QUALIFICATION_TRANSACTION_SCHEMA_VERSION,
        "plan_id": plan.plan_id,
        "registered_at": timestamp_text(registered_at),
        "trial_registry_path": str(trial_registry_path.resolve()),
        "qualification_registry_path": str(qualification_registry_path.resolve()),
        "plan": historical_plan_payload(plan),
        "registrations": [
            {
                "experiment_family": item.experiment_family,
                "definition_fingerprint": item.definition_fingerprint,
                "experiment_name": item.experiment_name,
                "hypothesis": item.hypothesis,
            }
            for item in registrations
        ],
    }


def _load_journal(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise QualificationTransactionError(f"cannot read qualification journal: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise QualificationTransactionError("qualification journal is malformed")
    required = {
        "plan_id",
        "registered_at",
        "trial_registry_path",
        "qualification_registry_path",
        "plan",
        "registrations",
    }
    if not required.issubset(payload):
        raise QualificationTransactionError("qualification journal is incomplete")
    return payload


def qualification_transaction_journal_path(qualification_registry_path: Path) -> Path:
    """Return the durable transaction-journal path for one qualification registry."""
    path = Path(qualification_registry_path)
    return path.with_name(f".{path.name}.qualification-transaction.json")


_journal_path = qualification_transaction_journal_path


def _mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise QualificationTransactionError("qualification journal plan is malformed")
    return value


def _list_of_mappings(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise QualificationTransactionError("qualification journal registrations are malformed")
    return value
