"""Append-only experiment trial history with fail-closed publication."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
import threading
import uuid
from collections.abc import Callable, Iterable
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading.research_data.artifacts import canonical_json_bytes

TRIAL_REGISTRY_SCHEMA_VERSION = 1
_FORMAL_RUN_MODES = frozenset({"online", "offline", "migration"})
_OUTCOME_STATUSES = frozenset({"succeeded", "failed"})
_VALIDITY_STATUSES = frozenset(
    {
        "valid",
        "data-stale",
        "definition-stale",
        "unreproducible",
        "legacy",
        "migration-pending",
    }
)

try:  # pragma: no cover - the project runs on POSIX, fallback keeps imports portable
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None


class TrialRegistryError(RuntimeError):
    """The registry is malformed, conflicting, or cannot be published safely."""


@dataclass(frozen=True, slots=True)
class OutcomeFreeTrialRegistration:
    """One semantic trial identity prepared without an outcome observation."""

    experiment_family: str
    definition_fingerprint: str
    experiment_name: str
    hypothesis: str = ""


_THREAD_LOCKS: dict[Path, threading.RLock] = {}
_THREAD_LOCKS_GUARD = threading.Lock()


class ExperimentTrialRegistry:
    """A JSON registry whose trial and observation history is never deleted."""

    def __init__(
        self,
        path: Path,
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.path = Path(path)
        self.now = now or (lambda: datetime.now(UTC))

    def read(self) -> dict[str, object]:
        """Read a verified registry state without changing it."""
        with self._locked():
            return copy.deepcopy(self._load_unlocked())

    def has_valid_observation(self, definition_fingerprint: str) -> bool:
        """Return whether a formal definition has a separate current-valid observation.

        Migration observations deliberately use ``migration-pending`` and therefore cannot
        satisfy this gate. The method is read-only and does not infer validity from a result
        filename or from a legacy trial identity.
        """
        _require_text(definition_fingerprint, "definition_fingerprint")
        state = self.read()
        trials = _trials(state)
        for trial in trials:
            if (
                trial.get("legacy") is True
                or trial.get("definition_fingerprint") != definition_fingerprint
            ):
                continue
            observations = trial.get("observations")
            if not isinstance(observations, list):  # pragma: no cover - read validates state
                continue
            if any(
                isinstance(observation, dict)
                and observation.get("event") == "observation"
                and observation.get("run_mode") in {"online", "offline"}
                and observation.get("outcome_status") == "succeeded"
                and observation.get("validity_status") == "valid"
                for observation in observations
            ):
                return True
        return False

    def register_trial(
        self,
        experiment_family: str,
        definition_fingerprint: str,
        *,
        experiment_name: str,
        hypothesis: str = "",
        registered_at: datetime | None = None,
    ) -> str:
        """Register one semantic definition, idempotently, and return its trial identity."""
        _require_text(experiment_family, "experiment_family")
        _require_text(definition_fingerprint, "definition_fingerprint")
        _require_text(experiment_name, "experiment_name")
        timestamp = _timestamp(registered_at or self.now())
        trial_id = formal_trial_id(experiment_family, definition_fingerprint)

        def update(state: dict[str, object]) -> str:
            trials = _trials(state)
            existing = _find_trial(trials, trial_id)
            if existing is None:
                trials.append(
                    {
                        "trial_id": trial_id,
                        "identity_kind": "semantic-definition",
                        "experiment_family": experiment_family,
                        "definition_fingerprint": definition_fingerprint,
                        "experiment_names": [experiment_name],
                        "hypothesis": hypothesis,
                        "first_registered_at": timestamp,
                        "last_observed_at": None,
                        "status": "registered",
                        "legacy": False,
                        "selection_history_incomplete": False,
                        "observations": [],
                    }
                )
                return trial_id
            _verify_formal_identity(existing, experiment_family, definition_fingerprint)
            names = _experiment_names(existing)
            if experiment_name not in names:
                names.append(experiment_name)
            if hypothesis and not existing.get("hypothesis"):
                existing["hypothesis"] = hypothesis
            return trial_id

        return self._update(update)

    def preview_registration_state(
        self,
        registrations: Iterable[OutcomeFreeTrialRegistration],
        *,
        registered_at: datetime,
    ) -> dict[str, object]:
        """Return the exact post-registration state without changing the registry."""
        timestamp = _timestamp(registered_at)
        prepared = _prepare_registrations(registrations)
        with self._locked():
            state = copy.deepcopy(self._load_unlocked())
        _apply_outcome_free_registrations(state, prepared, timestamp)
        return state

    def register_trials_atomically(
        self,
        registrations: Iterable[OutcomeFreeTrialRegistration],
        *,
        registered_at: datetime,
    ) -> tuple[str, ...]:
        """Register a complete outcome-free family in one locked registry update."""
        timestamp = _timestamp(registered_at)
        prepared = _prepare_registrations(registrations)

        def update(state: dict[str, object]) -> tuple[str, ...]:
            return _apply_outcome_free_registrations(state, prepared, timestamp)

        return self._update(update)

    def register_trials_with_locked_callback(
        self,
        registrations: Iterable[OutcomeFreeTrialRegistration],
        *,
        registered_at: datetime,
        callback: Callable[[dict[str, object], tuple[str, ...]], None],
    ) -> tuple[str, ...]:
        """Commit registrations and invoke a coordinator callback while retaining the lock.

        The trial bytes are durable before the callback runs. If the callback fails, an external
        transaction journal can recover idempotently, while no concurrent family mutation can
        interleave between the exact-universe check and the coordinated second write.
        """
        timestamp = _timestamp(registered_at)
        prepared = _prepare_registrations(registrations)
        with self._locked():
            state = self._load_unlocked()
            before = canonical_json_bytes(state)
            trial_ids = _apply_outcome_free_registrations(state, prepared, timestamp)
            if before != canonical_json_bytes(state):
                self._write_unlocked(state)
            callback(copy.deepcopy(state), trial_ids)
            return copy.deepcopy(trial_ids)

    def record_observation(
        self,
        experiment_family: str,
        definition_fingerprint: str,
        *,
        snapshot_id: str | None = None,
        result_path: str | Path | None = None,
        run_mode: str = "online",
        outcome_status: str = "succeeded",
        validity_status: str | None = None,
        failure_reason: str | None = None,
        observation_id: str | None = None,
        observed_at: datetime | None = None,
    ) -> str:
        """Append one observation, treating a repeated identical ID as an idempotent retry."""
        _require_text(experiment_family, "experiment_family")
        _require_text(definition_fingerprint, "definition_fingerprint")
        _require_text(run_mode, "run_mode")
        _require_text(outcome_status, "outcome_status")
        _validate_observation_statuses(
            run_mode=run_mode,
            outcome_status=outcome_status,
            validity_status=validity_status,
            failure_reason=failure_reason,
        )
        trial_id = formal_trial_id(experiment_family, definition_fingerprint)
        identity = observation_id or uuid.uuid4().hex
        timestamp = _timestamp(observed_at or self.now())
        observation = {
            "observation_id": identity,
            "event": "observation",
            "observed_at": timestamp,
            "snapshot_id": snapshot_id,
            "result_path": str(result_path) if result_path is not None else None,
            "run_mode": run_mode,
            "outcome_status": outcome_status,
            "validity_status": validity_status,
            "failure_reason": failure_reason,
        }

        def update(state: dict[str, object]) -> str:
            trial = _find_trial(_trials(state), trial_id)
            if trial is None:
                raise TrialRegistryError(f"formal trial {trial_id} is not registered")
            if trial.get("legacy") is True:
                raise TrialRegistryError("legacy trials cannot receive formal observations")
            observations = _observations(trial)
            existing = next(
                (item for item in observations if item.get("observation_id") == identity),
                None,
            )
            if existing is not None:
                if not _same_retry_observation(existing, observation):
                    raise TrialRegistryError(
                        f"observation {identity} already exists with different content"
                    )
                return identity
            observations.append(observation)
            trial["last_observed_at"] = timestamp
            if trial.get("status") != "removed":
                trial["status"] = "failed" if outcome_status == "failed" else "active"
            return identity

        return self._update(update)

    def mark_removed(
        self,
        experiment_family: str,
        definition_fingerprint: str,
        *,
        experiment_name: str,
        reason: str,
        removed_at: datetime | None = None,
    ) -> str:
        """Retain a deleted/renamed implementation as a tombstoned trial event."""
        _require_text(experiment_name, "experiment_name")
        _require_text(reason, "reason")
        trial_id = formal_trial_id(experiment_family, definition_fingerprint)
        event_id = f"removed:{trial_id}:{hashlib.sha256(reason.encode()).hexdigest()}"
        timestamp = _timestamp(removed_at or self.now())

        def update(state: dict[str, object]) -> str:
            trial = _find_trial(_trials(state), trial_id)
            if trial is None:
                raise TrialRegistryError(f"formal trial {trial_id} is not registered")
            names = _experiment_names(trial)
            if experiment_name not in names:
                names.append(experiment_name)
            event = {
                "observation_id": event_id,
                "event": "removed",
                "observed_at": timestamp,
                "experiment_name": experiment_name,
                "outcome_status": "removed",
                "reason": reason,
            }
            observations = _observations(trial)
            existing = next(
                (item for item in observations if item.get("observation_id") == event_id),
                None,
            )
            if existing is None:
                observations.append(event)
            elif existing != event:
                raise TrialRegistryError(f"removal event {event_id} conflicts with history")
            trial["status"] = "removed"
            return event_id

        return self._update(update)

    def seed_legacy(
        self,
        experiment_names: Iterable[str],
        *,
        seeded_at: datetime | None = None,
    ) -> tuple[str, ...]:
        """Add discoverable legacy experiments without inventing snapshots or fingerprints."""
        names = sorted(set(experiment_names))
        if any(not isinstance(name, str) or not name for name in names):
            raise TrialRegistryError("legacy experiment names must be non-empty strings")
        timestamp = _timestamp(seeded_at or self.now())

        def update(state: dict[str, object]) -> tuple[str, ...]:
            trials = _trials(state)
            state["selection_history_incomplete"] = True
            identities: list[str] = []
            for name in names:
                trial_id = legacy_trial_id(name)
                identities.append(trial_id)
                existing = _find_trial(trials, trial_id)
                if existing is not None:
                    if existing.get("legacy") is not True:
                        raise TrialRegistryError(f"legacy identity conflicts: {trial_id}")
                    continue
                trials.append(
                    {
                        "trial_id": trial_id,
                        "identity_kind": "legacy-discoverable-experiment",
                        "experiment_family": f"legacy:{name}",
                        "definition_fingerprint": None,
                        "experiment_names": [name],
                        "hypothesis": "",
                        "first_registered_at": timestamp,
                        "last_observed_at": None,
                        "status": "legacy",
                        "legacy": True,
                        "selection_history_incomplete": True,
                        "observations": [],
                    }
                )
            return tuple(identities)

        return self._update(update)

    def _update(self, callback: Callable[[dict[str, object]], Any]) -> Any:
        with self._locked():
            state = self._load_unlocked()
            before = canonical_json_bytes(state)
            result = callback(state)
            after = canonical_json_bytes(state)
            if before != after:
                self._write_unlocked(state)
            return copy.deepcopy(result)

    def _load_unlocked(self) -> dict[str, object]:
        if not self.path.exists():
            return _empty_state()
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise TrialRegistryError(f"cannot read trial registry: {exc}") from exc
        if not isinstance(loaded, dict):
            raise TrialRegistryError("trial registry must be a JSON object")
        if loaded.get("schema_version") != TRIAL_REGISTRY_SCHEMA_VERSION:
            raise TrialRegistryError("unsupported trial registry schema")
        if type(loaded.get("selection_history_incomplete")) is not bool:
            raise TrialRegistryError("trial registry selection-history flag is malformed")
        raw_trials = loaded.get("trials")
        if not isinstance(raw_trials, list):
            raise TrialRegistryError("trial registry trials must be a list")
        for trial in raw_trials:
            if not isinstance(trial, dict):
                raise TrialRegistryError("trial registry contains a malformed trial")
            _validate_trial(trial)
        return loaded

    def _write_unlocked(self, state: dict[str, object]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        content = (json.dumps(state, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode(
            "utf-8"
        )
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{self.path.name}-",
            suffix=".tmp",
            dir=self.path.parent,
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            temporary.unlink(missing_ok=True)

    @contextmanager
    def _locked(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = self.path.with_name(f".{self.path.name}.lock")
        with _thread_lock(lock_path):
            with lock_path.open("a+", encoding="utf-8") as handle:
                if fcntl is not None:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    if fcntl is not None:
                        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def formal_trial_id(experiment_family: str, definition_fingerprint: str) -> str:
    """Derive a stable trial identity from family plus semantic fingerprint."""
    return hashlib.sha256(
        canonical_json_bytes(
            {
                "experiment_family": experiment_family,
                "definition_fingerprint": definition_fingerprint,
            }
        )
    ).hexdigest()


def _prepare_registrations(
    registrations: Iterable[OutcomeFreeTrialRegistration],
) -> tuple[OutcomeFreeTrialRegistration, ...]:
    prepared = tuple(registrations)
    if not prepared:
        raise TrialRegistryError("atomic trial registration requires at least one identity")
    identities: set[str] = set()
    for item in prepared:
        _require_text(item.experiment_family, "experiment_family")
        _require_text(item.definition_fingerprint, "definition_fingerprint")
        _require_text(item.experiment_name, "experiment_name")
        if not isinstance(item.hypothesis, str):
            raise TrialRegistryError("hypothesis must be text")
        trial_id = formal_trial_id(item.experiment_family, item.definition_fingerprint)
        if trial_id in identities:
            raise TrialRegistryError("atomic trial registration contains duplicate identities")
        identities.add(trial_id)
    return tuple(
        sorted(
            prepared,
            key=lambda item: formal_trial_id(
                item.experiment_family,
                item.definition_fingerprint,
            ),
        )
    )


def _apply_outcome_free_registrations(
    state: dict[str, object],
    registrations: tuple[OutcomeFreeTrialRegistration, ...],
    timestamp: str,
) -> tuple[str, ...]:
    trials = _trials(state)
    identities: list[str] = []
    for item in registrations:
        trial_id = formal_trial_id(item.experiment_family, item.definition_fingerprint)
        identities.append(trial_id)
        existing = _find_trial(trials, trial_id)
        if existing is None:
            trials.append(
                {
                    "trial_id": trial_id,
                    "identity_kind": "semantic-definition",
                    "experiment_family": item.experiment_family,
                    "definition_fingerprint": item.definition_fingerprint,
                    "experiment_names": [item.experiment_name],
                    "hypothesis": item.hypothesis,
                    "first_registered_at": timestamp,
                    "last_observed_at": None,
                    "status": "registered",
                    "legacy": False,
                    "selection_history_incomplete": False,
                    "observations": [],
                }
            )
            continue
        _verify_formal_identity(
            existing,
            item.experiment_family,
            item.definition_fingerprint,
        )
        names = _experiment_names(existing)
        if item.experiment_name not in names:
            names.append(item.experiment_name)
        if item.hypothesis and not existing.get("hypothesis"):
            existing["hypothesis"] = item.hypothesis
    return tuple(identities)


def legacy_trial_id(experiment_name: str) -> str:
    """Derive a stable but explicitly non-semantic legacy identity."""
    return "legacy-" + hashlib.sha256(experiment_name.encode("utf-8")).hexdigest()


def _empty_state() -> dict[str, object]:
    return {
        "schema_version": TRIAL_REGISTRY_SCHEMA_VERSION,
        "selection_history_incomplete": False,
        "trials": [],
    }


def _trials(state: dict[str, object]) -> list[dict[str, object]]:
    trials = state["trials"]
    if not isinstance(trials, list):  # pragma: no cover - guarded by _load_unlocked
        raise TrialRegistryError("trial registry trials must be a list")
    if not all(isinstance(trial, dict) for trial in trials):
        raise TrialRegistryError("trial registry contains a malformed trial")
    return trials


def _find_trial(trials: list[dict[str, object]], trial_id: str) -> dict[str, object] | None:
    return next((trial for trial in trials if trial.get("trial_id") == trial_id), None)


def _validate_trial(trial: dict[str, object]) -> None:
    """Validate nested state before any update can rewrite the registry."""
    required = {
        "trial_id",
        "identity_kind",
        "experiment_family",
        "definition_fingerprint",
        "experiment_names",
        "hypothesis",
        "first_registered_at",
        "last_observed_at",
        "status",
        "legacy",
        "selection_history_incomplete",
        "observations",
    }
    if not required.issubset(trial):
        raise TrialRegistryError("trial registry contains a malformed trial")
    for field in (
        "trial_id",
        "identity_kind",
        "experiment_family",
        "first_registered_at",
        "status",
    ):
        if not isinstance(trial[field], str) or not trial[field]:
            raise TrialRegistryError(f"trial {field} is malformed")
    if not isinstance(trial["hypothesis"], str):
        raise TrialRegistryError("trial hypothesis is malformed")
    if trial["last_observed_at"] is not None and not isinstance(trial["last_observed_at"], str):
        raise TrialRegistryError("trial last_observed_at is malformed")
    if type(trial["legacy"]) is not bool or type(trial["selection_history_incomplete"]) is not bool:
        raise TrialRegistryError("trial flags are malformed")
    fingerprint = trial["definition_fingerprint"]
    if trial["legacy"]:
        if fingerprint is not None:
            raise TrialRegistryError("legacy trial fingerprint is malformed")
    elif not isinstance(fingerprint, str) or not fingerprint:
        raise TrialRegistryError("formal trial fingerprint is malformed")
    names = trial["experiment_names"]
    if not isinstance(names, list) or not all(isinstance(name, str) and name for name in names):
        raise TrialRegistryError("trial experiment_names is malformed")
    observations = trial["observations"]
    if not isinstance(observations, list):
        raise TrialRegistryError("trial observations are malformed")
    for observation in observations:
        if not isinstance(observation, dict):
            raise TrialRegistryError("trial observations are malformed")
        if not isinstance(observation.get("observation_id"), str) or not isinstance(
            observation.get("event"), str
        ):
            raise TrialRegistryError("trial observation identity is malformed")
        if observation["event"] == "observation":
            _validate_observation_statuses(
                run_mode=observation.get("run_mode"),
                outcome_status=observation.get("outcome_status"),
                validity_status=observation.get("validity_status"),
                failure_reason=observation.get("failure_reason"),
            )


def _experiment_names(trial: dict[str, object]) -> list[str]:
    names = trial.setdefault("experiment_names", [])
    if not isinstance(names, list):
        raise TrialRegistryError("trial experiment_names is malformed")
    return names


def _observations(trial: dict[str, object]) -> list[dict[str, object]]:
    observations = trial.setdefault("observations", [])
    if not isinstance(observations, list) or not all(
        isinstance(item, dict) for item in observations
    ):
        raise TrialRegistryError("trial observations are malformed")
    return observations


def _verify_formal_identity(
    trial: dict[str, object],
    experiment_family: str,
    definition_fingerprint: str,
) -> None:
    if (
        trial.get("experiment_family") != experiment_family
        or trial.get("definition_fingerprint") != definition_fingerprint
    ):
        raise TrialRegistryError("trial identity conflicts with existing history")


def _same_retry_observation(
    existing: dict[str, object],
    candidate: dict[str, object],
) -> bool:
    """Allow a retry to receive a new clock value while preserving all substantive fields."""
    return {key: value for key, value in existing.items() if key != "observed_at"} == {
        key: value for key, value in candidate.items() if key != "observed_at"
    }


def _require_text(value: object, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise TrialRegistryError(f"{field} must be a non-empty string")


def _validate_observation_statuses(
    *,
    run_mode: object,
    outcome_status: object,
    validity_status: object,
    failure_reason: object,
) -> None:
    if not isinstance(run_mode, str) or run_mode not in _FORMAL_RUN_MODES:
        raise TrialRegistryError("observation run_mode must be online, offline, or migration")
    if not isinstance(outcome_status, str) or outcome_status not in _OUTCOME_STATUSES:
        raise TrialRegistryError("observation outcome_status must be succeeded or failed")
    if validity_status is not None and (
        not isinstance(validity_status, str) or validity_status not in _VALIDITY_STATUSES
    ):
        raise TrialRegistryError("observation validity_status is unknown")
    if outcome_status == "failed":
        if not isinstance(failure_reason, str) or not failure_reason:
            raise TrialRegistryError("failed observation requires a failure_reason")
    elif failure_reason is not None:
        raise TrialRegistryError("succeeded observation cannot have a failure_reason")


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise TrialRegistryError("trial registry timestamps must be timezone-aware")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


@contextmanager
def _thread_lock(path: Path):
    with _THREAD_LOCKS_GUARD:
        lock = _THREAD_LOCKS.setdefault(path.resolve(), threading.RLock())
    with lock:
        yield
