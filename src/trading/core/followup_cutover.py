"""Controlled followup cutover lifecycle and fail-closed order authorization."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from pathlib import Path

import pandas as pd

from trading.core.accounting import canonical_json_bytes, parse_timestamp, timestamp_text
from trading.core.ledger_storage import atomic_write, locked_file

_SCHEMA_VERSION = 1
_GENESIS_HASH = "0" * 64


class StrategyLifecycle(StrEnum):
    """Operational status of one strategy in the controlled followup lifecycle."""

    LEGACY_ACTIVE = "legacy_active"
    MIGRATION_PENDING = "migration_pending"
    HISTORICAL_SCREEN_FAILED = "historical_screen_failed"
    SHADOW = "shadow"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    ACTIVE = "active"
    RETIRING = "retiring"
    PAUSED = "paused"


@dataclass(frozen=True)
class FollowupStrategy:
    """Stable identity of one followup strategy definition."""

    ticker: str
    experiment_name: str

    def __post_init__(self) -> None:
        ticker = self.ticker.strip().upper()
        experiment_name = self.experiment_name.strip()
        if not ticker or not experiment_name:
            raise ValueError("followup strategy identity must not be empty")
        object.__setattr__(self, "ticker", ticker)
        object.__setattr__(self, "experiment_name", experiment_name)


@dataclass(frozen=True)
class FollowupActivationProof:
    """Immutable identities verified before a Shadow strategy becomes Active."""

    shadow_id: str
    qualification_event_id: str
    result_fingerprint: str
    parity_digest: str

    def __post_init__(self) -> None:
        if not self.shadow_id.strip() or not self.qualification_event_id.strip():
            raise ValueError("activation proof identities must not be empty")
        for field_name in ("result_fingerprint", "parity_digest"):
            value = getattr(self, field_name)
            if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
                raise ValueError(f"{field_name} must be a lowercase SHA-256 digest")

    def payload(self) -> dict[str, str]:
        return {
            "shadow_id": self.shadow_id,
            "qualification_event_id": self.qualification_event_id,
            "result_fingerprint": self.result_fingerprint,
            "parity_digest": self.parity_digest,
        }


@dataclass(frozen=True)
class FollowupShadowProof:
    shadow_id: str
    registration_event_id: str
    historical_screen_event_id: str
    result_fingerprint: str
    parity_digest: str

    def payload(self) -> dict[str, str]:
        return {
            "shadow_id": _required_reason(self.shadow_id),
            "registration_event_id": _required_reason(self.registration_event_id),
            "historical_screen_event_id": _required_reason(self.historical_screen_event_id),
            "result_fingerprint": self.result_fingerprint,
            "parity_digest": self.parity_digest,
        }


@dataclass(frozen=True)
class FollowupAuthorizationContext:
    """Verified facts required to authorize one followup proposal."""

    lifecycle: StrategyLifecycle
    no_new_entry: bool
    result_valid: bool
    result_identity: str
    active_proof_current: bool
    data_fresh: bool
    data_cutoff: str
    data_bundle_identity: str
    ledger_verified: bool
    ledger_accounting_hash: str
    broker_reconciled: bool
    proposal_epoch_current: bool
    has_actual_position: bool

    def authorization_payload(
        self,
        *,
        strategy_id: str,
        allocation_epoch: str,
    ) -> dict[str, object]:
        """Return the canonical evidence attached to an actionable proposal."""
        return {
            "strategy_id": strategy_id,
            "strategy_lifecycle": self.lifecycle.value,
            "result_valid": self.result_valid,
            "result_identity": self.result_identity,
            "active_proof_current": self.active_proof_current,
            "data_fresh": self.data_fresh,
            "data_cutoff": self.data_cutoff,
            "data_bundle_identity": self.data_bundle_identity,
            "ledger_verified": self.ledger_verified,
            "ledger_accounting_hash": self.ledger_accounting_hash,
            "broker_reconciled": self.broker_reconciled,
            "allocation_epoch": allocation_epoch,
        }


@dataclass(frozen=True)
class FollowupAuthorizationDecision:
    authorized: bool
    reason: str


@dataclass(frozen=True)
class FollowupStatusReport:
    ticker: str
    experiment_name: str
    lifecycle: StrategyLifecycle
    state: str
    buy_authorized: bool
    buy_reason: str


def build_followup_status_report(
    strategy: FollowupStrategy,
    context: FollowupAuthorizationContext,
) -> FollowupStatusReport:
    """Project one strategy into the operator-facing Phase 7 vocabulary."""
    if context.has_actual_position and context.lifecycle in {
        StrategyLifecycle.LEGACY_ACTIVE,
        StrategyLifecycle.RETIRING,
        StrategyLifecycle.PAUSED,
    }:
        state = "legacy position management"
    else:
        state = {
            StrategyLifecycle.LEGACY_ACTIVE: "migration pending",
            StrategyLifecycle.MIGRATION_PENDING: "migration pending",
            StrategyLifecycle.HISTORICAL_SCREEN_FAILED: "historical screen failed",
            StrategyLifecycle.SHADOW: "Shadow",
            StrategyLifecycle.INSUFFICIENT_EVIDENCE: "insufficient evidence",
            StrategyLifecycle.ACTIVE: "Active",
            StrategyLifecycle.RETIRING: "Retiring",
            StrategyLifecycle.PAUSED: "Paused",
        }[context.lifecycle]
    decision = authorize_followup_order("BUY", context)
    return FollowupStatusReport(
        ticker=strategy.ticker,
        experiment_name=strategy.experiment_name,
        lifecycle=context.lifecycle,
        state=state,
        buy_authorized=decision.authorized,
        buy_reason=decision.reason,
    )


@dataclass(frozen=True)
class DataAccessParityCorrection:
    """A reviewed explanation for one exact migration difference."""

    difference_id: str
    reason: str

    def __post_init__(self) -> None:
        if not self.difference_id.strip() or not self.reason.strip():
            raise ValueError("parity correction identity and reason must not be empty")


@dataclass(frozen=True)
class DataAccessParityDifference:
    difference_id: str
    scope: str
    classification: str
    reason: str


@dataclass(frozen=True)
class DataAccessParityResult:
    differences: tuple[DataAccessParityDifference, ...]

    @property
    def passed(self) -> bool:
        return all(item.classification == "documented_correction" for item in self.differences)

    def payload(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "differences": [
                {
                    "difference_id": item.difference_id,
                    "scope": item.scope,
                    "classification": item.classification,
                    "reason": item.reason,
                }
                for item in self.differences
            ],
        }


@dataclass(frozen=True)
class DataAccessParityOutputs:
    indicators: pd.DataFrame
    signals: tuple[date, ...]
    trades: tuple[Mapping[str, object], ...]


_VERIFIED_PARITY_TOKEN = object()


@dataclass(frozen=True)
class VerifiedDataAccessParity:
    snapshot_id: str
    detector_identity: str
    result_fingerprint: str
    result: DataAccessParityResult
    legacy_output_checksum: str
    migrated_output_checksum: str
    _token: object


def run_verified_data_access_parity(
    *,
    snapshot_id: str,
    detector_identity: str,
    result_fingerprint: str,
    snapshot_loader: Callable[[str], object],
    legacy_runner: Callable[[object], DataAccessParityOutputs],
    migrated_runner: Callable[[object], DataAccessParityOutputs],
    corrections: Sequence[DataAccessParityCorrection] = (),
) -> VerifiedDataAccessParity:
    """Verify one immutable snapshot and execute both migration paths exactly once."""
    if len(snapshot_id) != 64 or any(
        character not in "0123456789abcdef" for character in snapshot_id
    ):
        raise ValueError("parity snapshot identity must be a SHA-256 digest")
    verified_bundle = snapshot_loader(snapshot_id)
    if verified_bundle is None:
        raise ValueError("verified parity snapshot loader returned no bundle")
    legacy = legacy_runner(verified_bundle)
    migrated = migrated_runner(verified_bundle)
    result = evaluate_data_access_parity(
        legacy_indicators=legacy.indicators,
        migrated_indicators=migrated.indicators,
        legacy_signals=legacy.signals,
        migrated_signals=migrated.signals,
        legacy_trades=legacy.trades,
        migrated_trades=migrated.trades,
        corrections=corrections,
    )
    return VerifiedDataAccessParity(
        snapshot_id=snapshot_id,
        detector_identity=_required_reason(detector_identity),
        result_fingerprint=result_fingerprint,
        result=result,
        legacy_output_checksum=_parity_output_checksum(legacy),
        migrated_output_checksum=_parity_output_checksum(migrated),
        _token=_VERIFIED_PARITY_TOKEN,
    )


@dataclass(frozen=True)
class FollowupMigrationParity:
    strategy: FollowupStrategy
    snapshot_id: str
    result_fingerprint: str
    parity_digest: str


class FollowupActivationVerifier:
    """Verify parity, exact Shadow registration, and prospective eligibility."""

    def __init__(
        self,
        *,
        qualification_registry: object,
        lifecycle_registry: FollowupLifecycleRegistry,
        current_result_fingerprint_resolver: Callable[[FollowupStrategy], str],
    ) -> None:
        self.qualification_registry = qualification_registry
        self.lifecycle_registry = lifecycle_registry
        self.current_result_fingerprint_resolver = current_result_fingerprint_resolver

    def __call__(
        self,
        strategy: FollowupStrategy,
        proof: FollowupActivationProof,
    ) -> None:
        read = getattr(self.qualification_registry, "read", None)
        if not callable(read):
            raise ValueError("qualification registry cannot be verified")
        state = read()
        events = state.get("events") if isinstance(state, dict) else None
        if not isinstance(events, list):
            raise ValueError("qualification registry is malformed")
        registration = _qualification_event(events, f"shadow-registration:{proof.shadow_id}")
        registration_payload = registration.get("payload")
        if (
            registration.get("event_type") != "shadow_registration"
            or not isinstance(registration_payload, Mapping)
            or registration_payload.get("shadow_id") != proof.shadow_id
            or registration_payload.get("definition_fingerprint") != proof.result_fingerprint
        ):
            raise ValueError("activation proof does not match Shadow registration")
        evaluation = _qualification_event(events, proof.qualification_event_id)
        evaluation_payload = evaluation.get("payload")
        if (
            evaluation.get("event_type") != "activation_evaluation"
            or not isinstance(evaluation_payload, Mapping)
            or evaluation_payload.get("shadow_id") != proof.shadow_id
            or evaluation_payload.get("eligible") is not True
            or evaluation_payload.get("disposition") != "activation-eligible"
        ):
            raise ValueError("prospective qualification is not activation-eligible")
        current_fingerprint = self.current_result_fingerprint_resolver(strategy)
        if current_fingerprint != proof.result_fingerprint:
            raise ValueError("current valid result does not match activation proof")
        parity = next(
            (
                event
                for event in self.lifecycle_registry.read().events
                if event.get("event_type") == "migration_parity_recorded"
                and isinstance(event.get("payload"), Mapping)
                and event["payload"].get("ticker") == strategy.ticker
                and event["payload"].get("experiment_name") == strategy.experiment_name
                and event["payload"].get("result_fingerprint") == proof.result_fingerprint
                and event["payload"].get("parity_digest") == proof.parity_digest
                and event["payload"].get("passed") is True
            ),
            None,
        )
        if parity is None:
            raise ValueError("verified data-access migration parity is missing")


class FollowupShadowVerifier:
    """Verify passing Historical Screen, exact Shadow registration, result, and parity."""

    def __init__(
        self,
        *,
        qualification_registry: object,
        lifecycle_registry: FollowupLifecycleRegistry,
        current_result_fingerprint_resolver: Callable[[FollowupStrategy], str],
    ) -> None:
        self.qualification_registry = qualification_registry
        self.lifecycle_registry = lifecycle_registry
        self.current_result_fingerprint_resolver = current_result_fingerprint_resolver

    def __call__(self, strategy: FollowupStrategy, proof: FollowupShadowProof) -> None:
        read = getattr(self.qualification_registry, "read", None)
        state = read() if callable(read) else None
        events = state.get("events") if isinstance(state, dict) else None
        if not isinstance(events, list):
            raise ValueError("qualification registry cannot be verified")
        registration = _qualification_event(events, proof.registration_event_id)
        registration_payload = registration.get("payload")
        screen = _qualification_event(events, proof.historical_screen_event_id)
        screen_payload = screen.get("payload")
        if (
            registration.get("event_type") != "shadow_registration"
            or not isinstance(registration_payload, Mapping)
            or registration_payload.get("shadow_id") != proof.shadow_id
            or registration_payload.get("definition_fingerprint") != proof.result_fingerprint
            or screen.get("event_type") != "historical_screen"
            or not isinstance(screen_payload, Mapping)
            or screen_payload.get("passed") is not True
            or screen_payload.get("disposition") != "shadow-eligible"
            or registration_payload.get("historical_plan_id") != screen_payload.get("plan_id")
        ):
            raise ValueError("Shadow proof does not match passing Historical Screen evidence")
        if self.current_result_fingerprint_resolver(strategy) != proof.result_fingerprint:
            raise ValueError("current valid result does not match Shadow proof")
        parity_exists = any(
            event.get("event_type") == "migration_parity_recorded"
            and isinstance(event.get("payload"), Mapping)
            and event["payload"].get("ticker") == strategy.ticker
            and event["payload"].get("experiment_name") == strategy.experiment_name
            and event["payload"].get("result_fingerprint") == proof.result_fingerprint
            and event["payload"].get("parity_digest") == proof.parity_digest
            and event["payload"].get("passed") is True
            for event in self.lifecycle_registry.read().events
        )
        if not parity_exists:
            raise ValueError("verified data-access migration parity is missing")


def evaluate_data_access_parity(
    *,
    legacy_indicators: pd.DataFrame,
    migrated_indicators: pd.DataFrame,
    legacy_signals: Sequence[date],
    migrated_signals: Sequence[date],
    legacy_trades: Sequence[Mapping[str, object]],
    migrated_trades: Sequence[Mapping[str, object]],
    corrections: Sequence[DataAccessParityCorrection] = (),
) -> DataAccessParityResult:
    """Compare both data-access paths on one identical research snapshot."""
    correction_by_id = {item.difference_id: item for item in corrections}
    if len(correction_by_id) != len(corrections):
        raise ValueError("parity correction identities must be unique")
    raw_differences = [
        *_indicator_differences(legacy_indicators, migrated_indicators),
        *_sequence_differences("signal", legacy_signals, migrated_signals),
        *_trade_differences(legacy_trades, migrated_trades),
    ]
    raw_ids = {item[0] for item in raw_differences}
    unused = set(correction_by_id) - raw_ids
    if unused:
        raise ValueError(f"parity correction does not match a difference: {sorted(unused)[0]}")
    differences = tuple(
        DataAccessParityDifference(
            difference_id=difference_id,
            scope=scope,
            classification=(
                "documented_correction" if difference_id in correction_by_id else "unclassified"
            ),
            reason=(
                correction_by_id[difference_id].reason
                if difference_id in correction_by_id
                else reason
            ),
        )
        for difference_id, scope, reason in raw_differences
    )
    return DataAccessParityResult(differences)


def authorize_followup_order(
    action: str,
    context: FollowupAuthorizationContext,
) -> FollowupAuthorizationDecision:
    """Apply the Phase 7 entry and existing-position exit guards."""
    normalized_action = action.strip().upper()
    if normalized_action == "SELL":
        if not context.ledger_verified:
            return FollowupAuthorizationDecision(False, "ledger is not verified")
        if not context.has_actual_position:
            return FollowupAuthorizationDecision(False, "no actual position exists")
        return FollowupAuthorizationDecision(True, "verified actual-position exit")
    if normalized_action != "BUY":
        return FollowupAuthorizationDecision(False, f"unsupported action: {normalized_action}")

    guards = (
        (
            context.lifecycle is StrategyLifecycle.ACTIVE,
            f"strategy is {context.lifecycle.value}",
        ),
        (not context.no_new_entry, "no-new-entry mode is enabled"),
        (context.result_valid, "research result is not valid"),
        (bool(context.result_identity.strip()), "valid result identity is missing"),
        (context.active_proof_current, "Active proof does not match the current result"),
        (context.data_fresh, "market data is stale"),
        (bool(context.data_cutoff.strip()), "market data cutoff is missing"),
        (bool(context.data_bundle_identity.strip()), "market data bundle identity is missing"),
        (context.ledger_verified, "ledger is not verified"),
        (
            bool(context.ledger_accounting_hash.strip()),
            "ledger accounting identity is missing",
        ),
        (context.broker_reconciled, "broker reconciliation is not current"),
        (context.proposal_epoch_current, "proposal allocation epoch is not current"),
        (
            not context.has_actual_position,
            "strategy sleeve already has an actual position",
        ),
    )
    for passed, reason in guards:
        if not passed:
            return FollowupAuthorizationDecision(False, reason)
    return FollowupAuthorizationDecision(True, "authorized")


@dataclass(frozen=True)
class FollowupLifecycleState:
    """Disposable projection of the verified lifecycle event history."""

    no_new_entry: bool
    strategies: tuple[tuple[FollowupStrategy, StrategyLifecycle], ...]
    activation_proofs: tuple[tuple[FollowupStrategy, FollowupActivationProof], ...]
    position_owners: tuple[tuple[str, FollowupStrategy], ...]
    events: tuple[dict[str, object], ...]

    def status_for(self, ticker: str, experiment_name: str) -> StrategyLifecycle:
        identity = FollowupStrategy(ticker, experiment_name)
        for strategy, lifecycle in self.strategies:
            if strategy == identity:
                return lifecycle
        raise KeyError(f"strategy is not registered: {identity.ticker}/{identity.experiment_name}")

    def activation_proof_for(
        self, ticker: str, experiment_name: str
    ) -> FollowupActivationProof | None:
        identity = FollowupStrategy(ticker, experiment_name)
        return next(
            (proof for strategy, proof in self.activation_proofs if strategy == identity),
            None,
        )

    def position_owner_for(self, ticker: str) -> FollowupStrategy | None:
        normalized = ticker.strip().upper()
        return next(
            (
                strategy
                for owner_ticker, strategy in self.position_owners
                if owner_ticker == normalized
            ),
            None,
        )


class FollowupLifecycleRegistry:
    """Append-only local authority for cutover status and entry pause state."""

    def __init__(
        self,
        path: Path,
        *,
        lock_timeout_seconds: float = 10.0,
        activation_verifier: Callable[[FollowupStrategy, FollowupActivationProof], None]
        | None = None,
        shadow_verifier: Callable[[FollowupStrategy, FollowupShadowProof], None] | None = None,
        actual_position_resolver: Callable[[FollowupStrategy], bool] | None = None,
        outstanding_entry_resolver: Callable[[FollowupStrategy], bool] | None = None,
        ledger_head_resolver: Callable[[], str] | None = None,
        coordination_lock_path: Path | None = None,
    ) -> None:
        self.path = Path(path)
        self.lock_path = self.path.with_name(f".{self.path.name}.lock")
        self.checkpoint_path = self.path.with_name(f".{self.path.name}.head.json")
        self.lock_timeout_seconds = lock_timeout_seconds
        self.activation_verifier = activation_verifier
        self.shadow_verifier = shadow_verifier
        self.actual_position_resolver = actual_position_resolver
        self.outstanding_entry_resolver = outstanding_entry_resolver
        self.ledger_head_resolver = ledger_head_resolver
        self.coordination_lock_path = coordination_lock_path or (
            self.path.parent / ".manual-trading-coordination.lock"
        )

    def initialize_cutover(
        self,
        strategies: tuple[FollowupStrategy, ...],
        *,
        occurred_at: datetime,
        position_owners: Mapping[str, FollowupStrategy] | None = None,
    ) -> FollowupLifecycleState:
        if not strategies:
            raise ValueError("cutover requires at least one followup strategy")
        identities = tuple(
            sorted(set(strategies), key=lambda item: (item.ticker, item.experiment_name))
        )
        if len(identities) != len(strategies):
            raise ValueError("cutover strategies must be unique")
        payload = {
            "occurred_at": timestamp_text(occurred_at),
            "no_new_entry": True,
            "strategies": [
                {
                    "ticker": strategy.ticker,
                    "experiment_name": strategy.experiment_name,
                    "lifecycle": StrategyLifecycle.LEGACY_ACTIVE.value,
                }
                for strategy in identities
            ],
            "position_owners": [
                {
                    "ticker": ticker.strip().upper(),
                    "experiment_name": owner.experiment_name,
                }
                for ticker, owner in sorted((position_owners or {}).items())
            ],
        }
        with (
            locked_file(self.coordination_lock_path, self.lock_timeout_seconds),
            locked_file(self.lock_path, self.lock_timeout_seconds),
        ):
            state = self._load_unlocked(allow_missing=True)
            events = _events(state)
            if events:
                if (
                    events[0].get("event_type") != "cutover_initialized"
                    or events[0].get("payload") != payload
                ):
                    raise ValueError("cutover initialization conflicts with existing history")
                return _project(state)
            self._append_unlocked(
                state,
                event_id="cutover-initialization",
                event_type="cutover_initialized",
                payload=payload,
            )
            return _project(state)

    def register_strategy(
        self,
        strategy: FollowupStrategy,
        *,
        lifecycle: StrategyLifecycle,
        occurred_at: datetime,
        reason: str,
    ) -> FollowupLifecycleState:
        if lifecycle in {StrategyLifecycle.ACTIVE, StrategyLifecycle.SHADOW}:
            raise ValueError("use activate_strategy with verified qualification proof")
        return self._record_change(
            event_type="strategy_registered",
            strategy=strategy,
            lifecycle=lifecycle,
            occurred_at=occurred_at,
            reason=reason,
        )

    def transition(
        self,
        strategy: FollowupStrategy,
        *,
        lifecycle: StrategyLifecycle,
        occurred_at: datetime,
        reason: str,
    ) -> FollowupLifecycleState:
        if lifecycle in {StrategyLifecycle.ACTIVE, StrategyLifecycle.SHADOW}:
            raise ValueError("use activate_strategy with verified qualification proof")
        current = self.read().status_for(strategy.ticker, strategy.experiment_name)
        if current in {StrategyLifecycle.ACTIVE, StrategyLifecycle.LEGACY_ACTIVE}:
            raise ValueError("use retire_strategy for an Active Strategy")
        if current is StrategyLifecycle.RETIRING:
            raise ValueError("use complete_retirement after the actual position is flat")
        return self._record_change(
            event_type="strategy_transitioned",
            strategy=strategy,
            lifecycle=lifecycle,
            occurred_at=occurred_at,
            reason=reason,
        )

    def register_shadow_strategy(
        self,
        strategy: FollowupStrategy,
        *,
        proof: FollowupShadowProof,
        occurred_at: datetime,
        reason: str,
    ) -> FollowupLifecycleState:
        """Project a verified passing Historical Screen registration into Shadow."""
        if self.shadow_verifier is None:
            raise ValueError("no Shadow verifier is configured")
        self.shadow_verifier(strategy, proof)
        state = self.read()
        registered = any(item == strategy for item, _lifecycle in state.strategies)
        payload: dict[str, object] = {
            "occurred_at": timestamp_text(occurred_at),
            "ticker": strategy.ticker,
            "experiment_name": strategy.experiment_name,
            "lifecycle": StrategyLifecycle.SHADOW.value,
            "reason": _required_reason(reason),
            "registered": registered,
            "proof": proof.payload(),
        }
        return self._append_change(
            "strategy_shadow_registered",
            payload,
            state_validator=lambda current: _validate_shadow_source(current, strategy, registered),
        )

    def retire_strategy(
        self,
        strategy: FollowupStrategy,
        *,
        occurred_at: datetime,
        reason: str,
    ) -> FollowupLifecycleState:
        """Move an Active definition to Retiring without abandoning its position."""
        if self.actual_position_resolver is None:
            raise ValueError("no actual-position resolver is configured")
        current = self.read().status_for(strategy.ticker, strategy.experiment_name)
        if current not in {StrategyLifecycle.ACTIVE, StrategyLifecycle.LEGACY_ACTIVE}:
            raise ValueError("only an Active or Legacy Active Strategy can begin retirement")
        payload: dict[str, object] = {
            "occurred_at": timestamp_text(occurred_at),
            "ticker": strategy.ticker,
            "experiment_name": strategy.experiment_name,
            "lifecycle": StrategyLifecycle.RETIRING.value,
            "reason": _required_reason(reason),
            "had_actual_position": bool(self.actual_position_resolver(strategy)),
            "ledger_head_hash": self.ledger_head_resolver() if self.ledger_head_resolver else "",
        }
        return self._append_change(
            "strategy_retiring",
            payload,
            state_validator=lambda state: self._validate_retirement_state(
                state, strategy, completing=False, expected_ledger_head=payload["ledger_head_hash"]
            ),
        )

    def complete_retirement(
        self,
        strategy: FollowupStrategy,
        *,
        occurred_at: datetime,
        reason: str,
    ) -> FollowupLifecycleState:
        """Retire a definition only after verified ledger state says it is flat."""
        if self.actual_position_resolver is None:
            raise ValueError("no actual-position resolver is configured")
        current = self.read().status_for(strategy.ticker, strategy.experiment_name)
        if current is not StrategyLifecycle.RETIRING:
            raise ValueError("only a Retiring Strategy can complete retirement")
        if self.actual_position_resolver(strategy):
            raise ValueError("retirement cannot complete until the actual position is flat")
        if self.outstanding_entry_resolver is None:
            raise ValueError("no outstanding-entry resolver is configured")
        if self.outstanding_entry_resolver(strategy):
            raise ValueError("retirement cannot complete with an outstanding entry proposal")
        payload: dict[str, object] = {
            "occurred_at": timestamp_text(occurred_at),
            "ticker": strategy.ticker,
            "experiment_name": strategy.experiment_name,
            "lifecycle": StrategyLifecycle.PAUSED.value,
            "reason": _required_reason(reason),
            "verified_flat": True,
            "ledger_head_hash": self.ledger_head_resolver() if self.ledger_head_resolver else "",
        }
        return self._append_change(
            "strategy_retired",
            payload,
            state_validator=lambda state: self._validate_retirement_state(
                state, strategy, completing=True, expected_ledger_head=payload["ledger_head_hash"]
            ),
        )

    def _validate_retirement_state(
        self,
        state: FollowupLifecycleState,
        strategy: FollowupStrategy,
        *,
        completing: bool,
        expected_ledger_head: object,
    ) -> None:
        allowed = (
            {StrategyLifecycle.RETIRING}
            if completing
            else {StrategyLifecycle.ACTIVE, StrategyLifecycle.LEGACY_ACTIVE}
        )
        _require_lifecycle(state, strategy, allowed, "lifecycle changed")
        if completing:
            if self.actual_position_resolver is None or self.actual_position_resolver(strategy):
                raise ValueError("retirement cannot complete until the actual position is flat")
            if self.outstanding_entry_resolver is None or self.outstanding_entry_resolver(strategy):
                raise ValueError("retirement cannot complete with an outstanding entry proposal")
        if (
            self.ledger_head_resolver is not None
            and self.ledger_head_resolver() != expected_ledger_head
        ):
            raise ValueError("verified ledger changed during retirement transition")

    def activate_strategy(
        self,
        strategy: FollowupStrategy,
        *,
        proof: FollowupActivationProof,
        occurred_at: datetime,
        reason: str,
    ) -> FollowupLifecycleState:
        """Promote only a verified prospective Shadow definition to Active."""
        current = self.read()
        if current.status_for(strategy.ticker, strategy.experiment_name) not in {
            StrategyLifecycle.SHADOW,
            StrategyLifecycle.INSUFFICIENT_EVIDENCE,
        }:
            raise ValueError("only a registered Shadow strategy can become Active")
        if self.activation_verifier is None:
            raise ValueError("no activation verifier is configured")
        self.activation_verifier(strategy, proof)
        payload: dict[str, object] = {
            "occurred_at": timestamp_text(occurred_at),
            "ticker": strategy.ticker,
            "experiment_name": strategy.experiment_name,
            "lifecycle": StrategyLifecycle.ACTIVE.value,
            "reason": _required_reason(reason),
            "proof": proof.payload(),
        }
        return self._append_change(
            "strategy_activated",
            payload,
            state_validator=lambda state: _require_lifecycle(
                state,
                strategy,
                {StrategyLifecycle.SHADOW, StrategyLifecycle.INSUFFICIENT_EVIDENCE},
                "only a registered Shadow strategy can become Active",
            ),
        )

    def record_migration_parity(
        self,
        strategy: FollowupStrategy,
        *,
        evidence: VerifiedDataAccessParity,
        occurred_at: datetime,
    ) -> FollowupMigrationParity:
        """Persist one recomputed passing parity result for an exact snapshot."""
        if evidence._token is not _VERIFIED_PARITY_TOKEN:
            raise ValueError("migration parity evidence was not produced by the verified runner")
        if evidence.detector_identity != strategy.experiment_name:
            raise ValueError("migration parity detector identity does not match strategy")
        if len(evidence.result_fingerprint) != 64 or any(
            character not in "0123456789abcdef" for character in evidence.result_fingerprint
        ):
            raise ValueError("migration parity result fingerprint must be a SHA-256 digest")
        if not evidence.result.passed:
            raise ValueError("unclassified data-access differences cannot pass migration parity")
        digest_payload = {
            "ticker": strategy.ticker,
            "experiment_name": strategy.experiment_name,
            "snapshot_id": evidence.snapshot_id,
            "result_fingerprint": evidence.result_fingerprint,
            "legacy_output_checksum": evidence.legacy_output_checksum,
            "migrated_output_checksum": evidence.migrated_output_checksum,
            "result": evidence.result.payload(),
        }
        parity_digest = hashlib.sha256(canonical_json_bytes(digest_payload)).hexdigest()
        payload: dict[str, object] = {
            "occurred_at": timestamp_text(occurred_at),
            **digest_payload,
            "passed": True,
            "parity_digest": parity_digest,
        }
        self._append_change("migration_parity_recorded", payload)
        return FollowupMigrationParity(
            strategy=strategy,
            snapshot_id=evidence.snapshot_id,
            result_fingerprint=evidence.result_fingerprint,
            parity_digest=parity_digest,
        )

    def set_no_new_entry(
        self,
        enabled: bool,
        *,
        occurred_at: datetime,
        reason: str,
    ) -> FollowupLifecycleState:
        payload = {
            "occurred_at": timestamp_text(occurred_at),
            "enabled": bool(enabled),
            "reason": _required_reason(reason),
        }
        return self._append_change("entry_mode_changed", payload)

    def read(self) -> FollowupLifecycleState:
        with (
            locked_file(self.coordination_lock_path, self.lock_timeout_seconds),
            locked_file(self.lock_path, self.lock_timeout_seconds),
        ):
            return _project(self._load_unlocked(allow_missing=False))

    def _record_change(
        self,
        *,
        event_type: str,
        strategy: FollowupStrategy,
        lifecycle: StrategyLifecycle,
        occurred_at: datetime,
        reason: str,
    ) -> FollowupLifecycleState:
        payload = {
            "occurred_at": timestamp_text(occurred_at),
            "ticker": strategy.ticker,
            "experiment_name": strategy.experiment_name,
            "lifecycle": lifecycle.value,
            "reason": _required_reason(reason),
        }
        return self._append_change(event_type, payload)

    def _append_change(
        self,
        event_type: str,
        payload: dict[str, object],
        *,
        state_validator: Callable[[FollowupLifecycleState], None] | None = None,
    ) -> FollowupLifecycleState:
        identity = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
        event_id = f"{event_type}:{identity}"
        with locked_file(self.lock_path, self.lock_timeout_seconds):
            state = self._load_unlocked(allow_missing=False)
            if state_validator is not None:
                state_validator(_project(state))
            existing = next(
                (event for event in _events(state) if event.get("event_id") == event_id),
                None,
            )
            if existing is not None:
                if existing.get("event_type") != event_type or existing.get("payload") != payload:
                    raise ValueError("followup lifecycle event conflicts with history")
                return _project(state)
            candidate = json.loads(json.dumps(state))
            self._append_unlocked(
                candidate,
                event_id=event_id,
                event_type=event_type,
                payload=payload,
                publish=False,
            )
            projected = _project(candidate)
            _validate_one_active(projected)
            self._publish(candidate)
            return projected

    def _append_unlocked(
        self,
        state: dict[str, object],
        *,
        event_id: str,
        event_type: str,
        payload: dict[str, object],
        publish: bool = True,
    ) -> None:
        events = _events(state)
        previous_hash = str(events[-1]["event_hash"]) if events else _GENESIS_HASH
        content = {
            "sequence": len(events) + 1,
            "event_id": event_id,
            "event_type": event_type,
            "payload": payload,
            "previous_hash": previous_hash,
        }
        events.append(
            {
                **content,
                "event_hash": hashlib.sha256(canonical_json_bytes(content)).hexdigest(),
            }
        )
        _project(state)
        if publish:
            self._publish(state)

    def _publish(self, state: dict[str, object]) -> None:
        content = canonical_json_bytes(state)
        atomic_write(self.path, content, replace=True)
        events = _events(state)
        checkpoint = {
            "schema_version": 1,
            "event_count": len(events),
            "registry_checksum": hashlib.sha256(content).hexdigest(),
            "head_hash": events[-1]["event_hash"],
        }
        atomic_write(self.checkpoint_path, canonical_json_bytes(checkpoint), replace=True)

    def _load_unlocked(self, *, allow_missing: bool) -> dict[str, object]:
        if not self.path.exists():
            if allow_missing:
                return {"schema_version": _SCHEMA_VERSION, "events": []}
            raise ValueError("followup lifecycle registry is not initialized")
        try:
            content = self.path.read_bytes()
            state = json.loads(content)
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"followup lifecycle integrity failure: {exc}") from exc
        if not isinstance(state, dict) or state.get("schema_version") != _SCHEMA_VERSION:
            raise ValueError("followup lifecycle integrity failure: unsupported schema")
        projected = _project(state)
        _validate_one_active(projected)
        _verify_checkpoint(self.checkpoint_path, content, _events(state))
        return state


def _events(state: dict[str, object]) -> list[dict[str, object]]:
    events = state.get("events")
    if not isinstance(events, list) or not all(isinstance(event, dict) for event in events):
        raise ValueError("followup lifecycle integrity failure: malformed events")
    return events


def _project(state: dict[str, object]) -> FollowupLifecycleState:
    no_new_entry = True
    strategies: dict[FollowupStrategy, StrategyLifecycle] = {}
    activation_proofs: dict[FollowupStrategy, FollowupActivationProof] = {}
    position_owners: dict[str, FollowupStrategy] = {}
    previous_hash = _GENESIS_HASH
    previous_occurred_at: datetime | None = None
    events = _events(state)
    for sequence, event in enumerate(events, start=1):
        content = {
            "sequence": event.get("sequence"),
            "event_id": event.get("event_id"),
            "event_type": event.get("event_type"),
            "payload": event.get("payload"),
            "previous_hash": event.get("previous_hash"),
        }
        expected_hash = hashlib.sha256(canonical_json_bytes(content)).hexdigest()
        if (
            event.get("sequence") != sequence
            or event.get("previous_hash") != previous_hash
            or event.get("event_hash") != expected_hash
            or not isinstance(event.get("payload"), dict)
        ):
            raise ValueError("followup lifecycle integrity failure: hash chain is invalid")
        payload = event["payload"]
        occurred_at_text = payload.get("occurred_at")
        if not isinstance(occurred_at_text, str):
            raise ValueError("followup lifecycle integrity failure: missing timestamp")
        try:
            occurred_at = parse_timestamp(occurred_at_text)
        except ValueError as exc:
            raise ValueError("followup lifecycle integrity failure: invalid timestamp") from exc
        if timestamp_text(occurred_at) != occurred_at_text:
            raise ValueError("followup lifecycle integrity failure: non-canonical timestamp")
        if previous_occurred_at is not None and occurred_at < previous_occurred_at:
            raise ValueError("followup lifecycle integrity failure: timestamps moved backward")
        previous_occurred_at = occurred_at
        event_type = event.get("event_type")
        if event_type == "cutover_initialized":
            raw_strategies = payload.get("strategies")
            if sequence != 1 or not isinstance(raw_strategies, list):
                raise ValueError("followup lifecycle integrity failure: invalid initialization")
            no_new_entry = payload.get("no_new_entry") is True
            for item in raw_strategies:
                if not isinstance(item, dict):
                    raise ValueError("followup lifecycle integrity failure: invalid strategy")
                strategy = FollowupStrategy(
                    str(item.get("ticker", "")),
                    str(item.get("experiment_name", "")),
                )
                strategies[strategy] = StrategyLifecycle(str(item.get("lifecycle")))
            raw_owners = payload.get("position_owners", [])
            if not isinstance(raw_owners, list):
                raise ValueError("followup lifecycle integrity failure: invalid position owners")
            for item in raw_owners:
                if not isinstance(item, Mapping):
                    raise ValueError("followup lifecycle integrity failure: invalid position owner")
                ticker = str(item.get("ticker", "")).strip().upper()
                owner = FollowupStrategy(ticker, str(item.get("experiment_name", "")))
                if ticker in position_owners or owner not in strategies:
                    raise ValueError("followup lifecycle integrity failure: invalid position owner")
                position_owners[ticker] = owner
        elif event_type in {
            "strategy_registered",
            "strategy_transitioned",
            "strategy_activated",
            "strategy_retiring",
            "strategy_retired",
            "strategy_shadow_registered",
        }:
            strategy = FollowupStrategy(
                str(payload.get("ticker", "")),
                str(payload.get("experiment_name", "")),
            )
            if event_type == "strategy_registered" and strategy in strategies:
                raise ValueError("followup lifecycle integrity failure: duplicate registration")
            if (
                event_type
                in {
                    "strategy_transitioned",
                    "strategy_activated",
                    "strategy_retiring",
                    "strategy_retired",
                }
                and strategy not in strategies
            ):
                raise ValueError("followup lifecycle integrity failure: unknown transition")
            lifecycle = StrategyLifecycle(str(payload.get("lifecycle")))
            if event_type == "strategy_shadow_registered":
                registered = payload.get("registered")
                if not isinstance(registered, bool) or lifecycle is not StrategyLifecycle.SHADOW:
                    raise ValueError("followup lifecycle integrity failure: invalid Shadow event")
                if registered != (strategy in strategies):
                    raise ValueError("followup lifecycle integrity failure: invalid Shadow source")
                proof = payload.get("proof")
                if not isinstance(proof, Mapping):
                    raise ValueError("followup lifecycle integrity failure: invalid Shadow proof")
                FollowupShadowProof(
                    shadow_id=str(proof.get("shadow_id", "")),
                    registration_event_id=str(proof.get("registration_event_id", "")),
                    historical_screen_event_id=str(proof.get("historical_screen_event_id", "")),
                    result_fingerprint=str(proof.get("result_fingerprint", "")),
                    parity_digest=str(proof.get("parity_digest", "")),
                ).payload()
            if event_type == "strategy_activated":
                proof = payload.get("proof")
                if lifecycle is not StrategyLifecycle.ACTIVE or not isinstance(proof, dict):
                    raise ValueError("followup lifecycle integrity failure: invalid activation")
                activation_proofs[strategy] = FollowupActivationProof(
                    shadow_id=str(proof.get("shadow_id", "")),
                    qualification_event_id=str(proof.get("qualification_event_id", "")),
                    result_fingerprint=str(proof.get("result_fingerprint", "")),
                    parity_digest=str(proof.get("parity_digest", "")),
                )
            elif event_type == "strategy_retiring":
                if lifecycle is not StrategyLifecycle.RETIRING or not isinstance(
                    payload.get("had_actual_position"), bool
                ):
                    raise ValueError("followup lifecycle integrity failure: invalid retirement")
            elif event_type == "strategy_retired":
                if (
                    lifecycle is not StrategyLifecycle.PAUSED
                    or payload.get("verified_flat") is not True
                ):
                    raise ValueError(
                        "followup lifecycle integrity failure: invalid retirement completion"
                    )
            strategies[strategy] = lifecycle
            if lifecycle is not StrategyLifecycle.ACTIVE:
                activation_proofs.pop(strategy, None)
        elif event_type == "entry_mode_changed":
            enabled = payload.get("enabled")
            if not isinstance(enabled, bool):
                raise ValueError("followup lifecycle integrity failure: invalid entry mode")
            no_new_entry = enabled
        elif event_type == "migration_parity_recorded":
            strategy = FollowupStrategy(
                str(payload.get("ticker", "")),
                str(payload.get("experiment_name", "")),
            )
            parity_digest = str(payload.get("parity_digest", ""))
            result_fingerprint = str(payload.get("result_fingerprint", ""))
            result_payload = payload.get("result")
            if (
                strategy not in strategies
                or payload.get("passed") is not True
                or len(parity_digest) != 64
                or len(result_fingerprint) != 64
                or not isinstance(result_payload, Mapping)
                or result_payload.get("passed") is not True
            ):
                raise ValueError("followup lifecycle integrity failure: invalid migration parity")
        else:
            raise ValueError("followup lifecycle integrity failure: unknown event")
        previous_hash = expected_hash
    return FollowupLifecycleState(
        no_new_entry=no_new_entry,
        strategies=tuple(
            sorted(strategies.items(), key=lambda item: (item[0].ticker, item[0].experiment_name))
        ),
        activation_proofs=tuple(
            sorted(
                activation_proofs.items(),
                key=lambda item: (item[0].ticker, item[0].experiment_name),
            )
        ),
        position_owners=tuple(sorted(position_owners.items())),
        events=tuple(json.loads(json.dumps(event)) for event in events),
    )


def _require_lifecycle(
    state: FollowupLifecycleState,
    strategy: FollowupStrategy,
    allowed: set[StrategyLifecycle],
    message: str,
) -> None:
    if state.status_for(strategy.ticker, strategy.experiment_name) not in allowed:
        raise ValueError(message)


def _validate_shadow_source(
    state: FollowupLifecycleState,
    strategy: FollowupStrategy,
    registered: bool,
) -> None:
    exists = any(item == strategy for item, _lifecycle in state.strategies)
    if exists != registered:
        raise ValueError("Shadow strategy registration source changed")
    if (
        exists
        and state.status_for(strategy.ticker, strategy.experiment_name) is StrategyLifecycle.ACTIVE
    ):
        raise ValueError("retire an Active Strategy before a new Shadow registration")


def _validate_one_active(state: FollowupLifecycleState) -> None:
    active_by_ticker: set[str] = set()
    for strategy, lifecycle in state.strategies:
        if lifecycle is not StrategyLifecycle.ACTIVE:
            continue
        if strategy.ticker in active_by_ticker:
            raise ValueError(f"{strategy.ticker} already has an Active Strategy")
        active_by_ticker.add(strategy.ticker)


def _verify_checkpoint(
    path: Path,
    content: bytes,
    events: list[dict[str, object]],
) -> None:
    if not events:
        raise ValueError("followup lifecycle integrity failure: empty history")
    try:
        checkpoint = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("followup lifecycle integrity failure: missing checkpoint") from exc
    if (
        not isinstance(checkpoint, dict)
        or checkpoint.get("schema_version") != 1
        or checkpoint.get("event_count") != len(events)
        or checkpoint.get("registry_checksum") != hashlib.sha256(content).hexdigest()
        or checkpoint.get("head_hash") != events[-1].get("event_hash")
    ):
        raise ValueError("followup lifecycle integrity failure: checkpoint mismatch")


def _required_reason(reason: str) -> str:
    normalized = reason.strip()
    if not normalized:
        raise ValueError("followup lifecycle reason must not be empty")
    return normalized


def _qualification_event(
    events: list[object],
    event_id: str,
) -> Mapping[str, object]:
    event = next(
        (item for item in events if isinstance(item, Mapping) and item.get("event_id") == event_id),
        None,
    )
    if event is None:
        raise ValueError(f"qualification event is missing: {event_id}")
    return event


def _parity_output_checksum(output: DataAccessParityOutputs) -> str:
    payload = {
        "indicator_checksum": hashlib.sha256(
            output.indicators.to_csv(
                index=True,
                lineterminator="\n",
                date_format="%Y-%m-%dT%H:%M:%S",
                float_format="%.17g",
            ).encode("utf-8")
        ).hexdigest(),
        "signals": [item.isoformat() for item in output.signals],
        "trades": [dict(item) for item in output.trades],
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _indicator_differences(
    legacy: pd.DataFrame,
    migrated: pd.DataFrame,
) -> list[tuple[str, str, str]]:
    if not legacy.index.is_unique or not migrated.index.is_unique:
        raise ValueError("parity indicator indices must be unique")
    if not legacy.columns.is_unique or not migrated.columns.is_unique:
        raise ValueError("parity indicator columns must be unique")
    differences: list[tuple[str, str, str]] = []
    legacy_columns = {str(column): column for column in legacy.columns}
    migrated_columns = {str(column): column for column in migrated.columns}
    for column in sorted(set(legacy_columns) ^ set(migrated_columns)):
        side = "migrated" if column in legacy_columns else "legacy"
        differences.append(
            (f"indicator:column:{column}", "indicator", f"column missing from {side} path")
        )
    legacy_index = {_index_identity(value): value for value in legacy.index}
    migrated_index = {_index_identity(value): value for value in migrated.index}
    for identity in sorted(set(legacy_index) ^ set(migrated_index)):
        side = "migrated" if identity in legacy_index else "legacy"
        differences.append(
            (f"indicator:index:{identity}", "indicator", f"row missing from {side} path")
        )
    for identity in sorted(set(legacy_index) & set(migrated_index)):
        for column in sorted(set(legacy_columns) & set(migrated_columns)):
            legacy_value = legacy.at[legacy_index[identity], legacy_columns[column]]
            migrated_value = migrated.at[migrated_index[identity], migrated_columns[column]]
            if _scalar_equal(legacy_value, migrated_value):
                continue
            differences.append(
                (
                    f"indicator:{identity}:{column}",
                    "indicator",
                    "indicator value differs between data-access paths",
                )
            )
    return differences


def _sequence_differences(
    scope: str,
    legacy: Sequence[object],
    migrated: Sequence[object],
) -> list[tuple[str, str, str]]:
    legacy_counts = Counter(str(item) for item in legacy)
    migrated_counts = Counter(str(item) for item in migrated)
    differences: list[tuple[str, str, str]] = []
    for identity, count in sorted((legacy_counts - migrated_counts).items()):
        differences.extend(
            (
                f"{scope}:{identity}:legacy_only:{ordinal}",
                scope,
                f"{scope} is missing from migrated path",
            )
            for ordinal in range(1, count + 1)
        )
    for identity, count in sorted((migrated_counts - legacy_counts).items()):
        differences.extend(
            (
                f"{scope}:{identity}:migrated_only:{ordinal}",
                scope,
                f"{scope} is missing from legacy path",
            )
            for ordinal in range(1, count + 1)
        )
    return differences


def _trade_differences(
    legacy: Sequence[Mapping[str, object]],
    migrated: Sequence[Mapping[str, object]],
) -> list[tuple[str, str, str]]:
    legacy_payloads = [canonical_json_bytes(dict(item)).decode("utf-8") for item in legacy]
    migrated_payloads = [canonical_json_bytes(dict(item)).decode("utf-8") for item in migrated]
    raw = _sequence_differences("trade", legacy_payloads, migrated_payloads)
    return [
        (
            f"trade:{hashlib.sha256(difference_id.encode()).hexdigest()}",
            scope,
            reason,
        )
        for difference_id, scope, reason in raw
    ]


def _index_identity(value: object) -> str:
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def _scalar_equal(first: object, second: object) -> bool:
    try:
        if bool(pd.isna(first)) and bool(pd.isna(second)):
            return True
    except (TypeError, ValueError):
        pass
    try:
        return bool(first == second)
    except (TypeError, ValueError):
        return False
