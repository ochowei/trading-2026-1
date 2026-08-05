"""Deterministic manual-order proposal identities and immutable terms."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from trading.core.accounting import canonical_json_bytes, decimal_text, to_decimal


class ProposalConflictError(RuntimeError):
    """A stable proposal identity was reused with different actionable terms."""


def _date_text(value: date) -> str:
    return value.isoformat()


def deterministic_proposal_id(
    *,
    sleeve_id: str,
    instrument: str,
    allocation_epoch: str,
    signal_date: date,
    trading_date: date,
    action: str,
    position_id: str,
    role: str = "entry",
) -> str:
    """Derive a stable identity from strategy/position identity, never mutable terms."""
    identity = {
        "schema_version": 1,
        "sleeve_id": sleeve_id,
        "instrument": instrument,
        "allocation_epoch": allocation_epoch,
        "signal_date": _date_text(signal_date),
        "trading_date": _date_text(trading_date),
        "action": action.upper(),
        "position_id": position_id,
        "role": role.lower(),
    }
    digest = hashlib.sha256(canonical_json_bytes(identity)).hexdigest()
    return f"proposal-{digest}"


@dataclass(frozen=True)
class ProposalTerms:
    """All actionable terms captured by a submission event."""

    sleeve_id: str
    instrument: str
    allocation_epoch: str
    signal_date: date
    trading_date: date
    action: str
    position_id: str
    role: str
    quantity: Decimal
    order_type: str
    price: Decimal | None = None
    target_price: Decimal | None = None
    stop_price: Decimal | None = None
    expiry_date: date | None = None
    duration: str = "Day"

    @classmethod
    def create(
        cls,
        *,
        sleeve_id: str,
        instrument: str,
        allocation_epoch: str,
        signal_date: date,
        trading_date: date,
        action: str,
        position_id: str,
        role: str,
        quantity: Decimal | int | str,
        order_type: str,
        price: Decimal | int | str | None = None,
        target_price: Decimal | int | str | None = None,
        stop_price: Decimal | int | str | None = None,
        expiry_date: date | None = None,
        duration: str = "Day",
    ) -> ProposalTerms:
        normalized_action = action.upper()
        if normalized_action not in {"BUY", "SELL"}:
            raise ValueError("proposal action must be BUY or SELL")
        normalized_order_type = order_type.upper()
        if normalized_order_type not in {"MARKET", "LIMIT", "STOP"}:
            raise ValueError("proposal order_type must be MARKET, LIMIT, or STOP")
        fields = {
            "sleeve_id": sleeve_id,
            "instrument": instrument.upper(),
            "allocation_epoch": allocation_epoch,
            "position_id": position_id,
            "role": role.lower(),
            "duration": duration,
        }
        if any(not isinstance(value, str) or not value.strip() for value in fields.values()):
            raise ValueError("proposal identity and duration fields must not be empty")
        parsed_quantity = to_decimal(quantity, "quantity", allow_negative=False)
        if parsed_quantity <= 0:
            raise ValueError("proposal quantity must be greater than zero")

        def optional_decimal(value: Decimal | int | str | None, field: str) -> Decimal | None:
            if value is None:
                return None
            parsed = to_decimal(value, field, allow_negative=False)
            if parsed <= 0:
                raise ValueError(f"{field} must be greater than zero")
            return parsed

        return cls(
            sleeve_id=sleeve_id.strip(),
            instrument=instrument.strip().upper(),
            allocation_epoch=allocation_epoch.strip(),
            signal_date=signal_date,
            trading_date=trading_date,
            action=normalized_action,
            position_id=position_id.strip(),
            role=role.strip().lower(),
            quantity=parsed_quantity,
            order_type=normalized_order_type,
            price=optional_decimal(price, "price"),
            target_price=optional_decimal(target_price, "target_price"),
            stop_price=optional_decimal(stop_price, "stop_price"),
            expiry_date=expiry_date,
            duration=duration.strip(),
        )

    @property
    def proposal_id(self) -> str:
        return deterministic_proposal_id(
            sleeve_id=self.sleeve_id,
            instrument=self.instrument,
            allocation_epoch=self.allocation_epoch,
            signal_date=self.signal_date,
            trading_date=self.trading_date,
            action=self.action,
            position_id=self.position_id,
            role=self.role,
        )

    def identity_payload(self) -> dict[str, str]:
        return {
            "schema_version": "1",
            "sleeve_id": self.sleeve_id,
            "instrument": self.instrument,
            "allocation_epoch": self.allocation_epoch,
            "signal_date": _date_text(self.signal_date),
            "trading_date": _date_text(self.trading_date),
            "action": self.action,
            "position_id": self.position_id,
            "role": self.role,
        }

    def payload(self) -> dict[str, str | None]:
        """Canonical all-terms payload used to detect changed proposal terms."""
        return {
            **self.identity_payload(),
            "quantity": decimal_text(self.quantity, "quantity"),
            "order_type": self.order_type,
            "price": decimal_text(self.price, "price") if self.price is not None else None,
            "target_price": (
                decimal_text(self.target_price, "target_price")
                if self.target_price is not None
                else None
            ),
            "stop_price": (
                decimal_text(self.stop_price, "stop_price") if self.stop_price is not None else None
            ),
            "expiry_date": _date_text(self.expiry_date) if self.expiry_date is not None else None,
            "duration": self.duration,
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ProposalTerms:
        try:
            return cls.create(
                sleeve_id=str(payload["sleeve_id"]),
                instrument=str(payload["instrument"]),
                allocation_epoch=str(payload["allocation_epoch"]),
                signal_date=date.fromisoformat(str(payload["signal_date"])),
                trading_date=date.fromisoformat(str(payload["trading_date"])),
                action=str(payload["action"]),
                position_id=str(payload["position_id"]),
                role=str(payload["role"]),
                quantity=str(payload["quantity"]),
                order_type=str(payload["order_type"]),
                price=payload.get("price"),
                target_price=payload.get("target_price"),
                stop_price=payload.get("stop_price"),
                expiry_date=(
                    date.fromisoformat(str(payload["expiry_date"]))
                    if payload.get("expiry_date") is not None
                    else None
                ),
                duration=str(payload.get("duration", "Day")),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("proposal terms payload is invalid") from exc

    def same_terms(self, other: ProposalTerms) -> bool:
        return self.payload() == other.payload()
