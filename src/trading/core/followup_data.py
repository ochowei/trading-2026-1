"""Declared, fail-closed auxiliary data for controlled followup execution."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass

import pandas as pd

from trading.core.accounting import canonical_json_bytes
from trading.market_data import (
    AvailabilityPolicy,
    MarketDataAvailabilityError,
    PrimaryUSSessionCalendar,
    SignalDecisionTime,
    align_auxiliary,
    validate_daily_bars,
)


class AuxiliaryDataRequiredError(RuntimeError):
    """A detector's declared auxiliary data is absent or unusable."""


@dataclass(frozen=True)
class FollowupDataBundle:
    """Exact validated primary and aligned auxiliary frames for one evaluation."""

    primary_symbol: str
    primary: pd.DataFrame
    auxiliary: Mapping[str, pd.DataFrame]
    identity: str


class DeclaredAuxiliaryData:
    """Detector protocol for dependencies supplied by the shared data boundary."""

    def auxiliary_symbols(self) -> tuple[str, ...]:
        raise NotImplementedError

    def bind_auxiliary_data(self, bundle: FollowupDataBundle) -> None:
        expected = set(self.auxiliary_symbols())
        available = set(bundle.auxiliary)
        if available != expected:
            missing = sorted(expected - available)
            extra = sorted(available - expected)
            raise AuxiliaryDataRequiredError(
                f"auxiliary binding mismatch; missing={missing}, undeclared={extra}"
            )
        self._followup_auxiliary = {
            symbol: frame.copy(deep=True) for symbol, frame in bundle.auxiliary.items()
        }
        self.data_bundle_identity = bundle.identity

    def require_auxiliary(
        self,
        symbol: str,
        primary_index: pd.Index,
    ) -> pd.DataFrame:
        frames = getattr(self, "_followup_auxiliary", None)
        if not isinstance(frames, dict):
            raise AuxiliaryDataRequiredError("declared auxiliary data is not bound")
        if symbol not in self.auxiliary_symbols() or symbol not in frames:
            raise AuxiliaryDataRequiredError(f"undeclared or missing auxiliary series: {symbol}")
        frame = frames[symbol].reindex(primary_index)
        if frame.empty or frame["Close"].isna().any():
            raise AuxiliaryDataRequiredError(
                f"auxiliary series {symbol} does not cover every primary decision"
            )
        return frame.copy(deep=True)


def build_followup_data_bundle(
    *,
    primary_symbol: str,
    primary_frame: pd.DataFrame,
    auxiliary_symbols: tuple[str, ...],
    frames: Mapping[str, pd.DataFrame],
) -> FollowupDataBundle:
    """Validate and align an exact followup data bundle using explicit availability."""
    normalized_primary, outcome = validate_daily_bars(primary_frame)
    if not outcome.is_valid or normalized_primary.empty:
        raise AuxiliaryDataRequiredError("invalid primary series: " + "; ".join(outcome.errors))
    if len(set(auxiliary_symbols)) != len(auxiliary_symbols):
        raise AuxiliaryDataRequiredError("auxiliary declarations must be unique")
    required = set(auxiliary_symbols)
    if set(frames) != required:
        raise AuxiliaryDataRequiredError(
            f"auxiliary bundle mismatch; missing={sorted(required - set(frames))}, "
            f"undeclared={sorted(set(frames) - required)}"
        )

    calendar = PrimaryUSSessionCalendar()
    policy = AvailabilityPolicy(
        publication_lag_sessions=0,
        max_observation_lag_sessions=3,
        publication_time_known=True,
    )
    aligned: dict[str, pd.DataFrame] = {}
    try:
        decisions = (
            tuple(
                SignalDecisionTime.for_primary_session(timestamp.date(), calendar=calendar)
                for timestamp in normalized_primary.index
            )
            if required
            else ()
        )
        for symbol in sorted(required):
            aligned[symbol] = align_auxiliary(
                decisions,
                frames[symbol],
                policy=policy,
                calendar=calendar,
            )
    except MarketDataAvailabilityError as exc:
        raise AuxiliaryDataRequiredError(str(exc)) from exc

    evidence = {
        "schema_version": 1,
        "primary_symbol": primary_symbol.strip().upper(),
        "data_cutoff": normalized_primary.index[-1].date().isoformat(),
        "availability_policy": {
            "publication_lag_sessions": policy.publication_lag_sessions,
            "max_observation_lag_sessions": policy.max_observation_lag_sessions,
            "publication_time_known": policy.publication_time_known,
        },
        "frames": {
            primary_symbol.strip().upper(): _frame_checksum(normalized_primary),
            **{symbol: _frame_checksum(frame) for symbol, frame in sorted(aligned.items())},
        },
    }
    identity = hashlib.sha256(canonical_json_bytes(evidence)).hexdigest()
    return FollowupDataBundle(
        primary_symbol=primary_symbol.strip().upper(),
        primary=normalized_primary.copy(deep=True),
        auxiliary={symbol: frame.copy(deep=True) for symbol, frame in aligned.items()},
        identity=identity,
    )


def _frame_checksum(frame: pd.DataFrame) -> str:
    canonical = frame.to_csv(
        index=True,
        lineterminator="\n",
        date_format="%Y-%m-%dT%H:%M:%S",
        float_format="%.17g",
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
