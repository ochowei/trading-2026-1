"""Build dry-run followup proposals from verified manual ledger state."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import ROUND_DOWN, Decimal

from trading.core.accounting import to_decimal
from trading.core.manual_ledger import SLEEVE_QUANTUM, LedgerReplay
from trading.core.proposals import ProposalTerms


def _outstanding_gtc_terms(
    replay: LedgerReplay,
    candidate: ProposalTerms,
) -> ProposalTerms | None:
    outstanding = [
        proposal
        for proposal in replay.outstanding_gtc_exits(
            sleeve_id=candidate.sleeve_id,
            instrument=candidate.instrument,
            position_id=candidate.position_id,
            role=candidate.role,
        )
        if proposal.terms.allocation_epoch == candidate.allocation_epoch
    ]
    if len(outstanding) > 1:
        raise ValueError(
            f"multiple outstanding GTC {candidate.role} proposals for {candidate.position_id}"
        )
    if not outstanding:
        return None
    return outstanding[0].terms


def _reuse_outstanding_gtc_identity(
    replay: LedgerReplay,
    candidate: ProposalTerms,
) -> ProposalTerms:
    existing = _outstanding_gtc_terms(replay, candidate)
    if existing is None:
        return candidate
    return replace(
        candidate,
        signal_date=existing.signal_date,
        trading_date=existing.trading_date,
        expiry_date=existing.expiry_date,
    )


def build_manual_proposal_terms(
    replay: LedgerReplay,
    *,
    sleeve_id: str,
    instrument: str,
    signal_today: bool,
    signal_date: date,
    trading_date: date,
    estimated_entry: Decimal | int | str,
    profit_target: Decimal | int | str,
    stop_loss: Decimal | int | str,
    holding_days: int,
    held_trading_days: int,
    trailing_high: Decimal | int | str | None = None,
    trail_activation_pct: Decimal | int | str | None = None,
    trail_distance_pct: Decimal | int | str | None = None,
) -> tuple[ProposalTerms, ...]:
    """Return entry or actual-position exit terms without projecting unconfirmed buys."""
    key = (sleeve_id, instrument.upper())
    position = replay.positions.get(key)
    if position is not None:
        target_rate = to_decimal(profit_target, "profit_target")
        stop_rate = to_decimal(stop_loss, "stop_loss")
        target_price = position.average_price * (Decimal("1") + target_rate)
        stop_price = position.average_price * (Decimal("1") + stop_rate)
        if (
            trailing_high is not None
            and trail_activation_pct is not None
            and trail_distance_pct is not None
        ):
            highest_price = to_decimal(trailing_high, "trailing_high", allow_negative=False)
            activation_rate = to_decimal(
                trail_activation_pct,
                "trail_activation_pct",
                allow_negative=False,
            )
            distance_rate = to_decimal(
                trail_distance_pct,
                "trail_distance_pct",
                allow_negative=False,
            )
            if distance_rate >= 1:
                raise ValueError("trail_distance_pct must be less than one")
            if highest_price >= position.average_price * (Decimal("1") + activation_rate):
                stop_price = max(
                    stop_price,
                    highest_price * (Decimal("1") - distance_rate),
                )
        if target_price <= 0 or stop_price <= 0:
            raise ValueError("profit_target and stop_loss produce invalid exit prices")
        stop = ProposalTerms.create(
            sleeve_id=sleeve_id,
            instrument=instrument,
            allocation_epoch=replay.allocation_epoch,
            signal_date=position.opened_at.date(),
            trading_date=trading_date,
            action="SELL",
            position_id=position.position_id,
            role="stop",
            quantity=position.quantity,
            order_type="STOP",
            price=stop_price,
            stop_price=stop_price,
            duration="GTC",
        )
        if held_trading_days >= holding_days:
            if _outstanding_gtc_terms(replay, stop) is not None:
                return (_reuse_outstanding_gtc_identity(replay, stop),)
            return (
                ProposalTerms.create(
                    sleeve_id=sleeve_id,
                    instrument=instrument,
                    allocation_epoch=replay.allocation_epoch,
                    signal_date=position.opened_at.date(),
                    trading_date=trading_date,
                    action="SELL",
                    position_id=position.position_id,
                    role="expiry",
                    quantity=position.quantity,
                    order_type="MARKET",
                    expiry_date=trading_date,
                ),
            )
        target = ProposalTerms.create(
            sleeve_id=sleeve_id,
            instrument=instrument,
            allocation_epoch=replay.allocation_epoch,
            signal_date=position.opened_at.date(),
            trading_date=trading_date,
            action="SELL",
            position_id=position.position_id,
            role="target",
            quantity=position.quantity,
            order_type="LIMIT",
            price=target_price,
            target_price=target_price,
            expiry_date=trading_date,
        )
        return (
            target,
            _reuse_outstanding_gtc_identity(replay, stop),
        )

    if replay.outstanding_gtc_exits(sleeve_id=sleeve_id, instrument=instrument):
        return ()
    if not signal_today:
        return ()
    entry_price = to_decimal(estimated_entry, "estimated_entry", allow_negative=False)
    if entry_price <= 0:
        raise ValueError("estimated_entry must be greater than zero")
    quantity = (replay.sleeve_cash[sleeve_id] / entry_price).quantize(
        SLEEVE_QUANTUM, rounding=ROUND_DOWN
    )
    if quantity <= 0:
        return ()
    candidate = ProposalTerms.create(
        sleeve_id=sleeve_id,
        instrument=instrument,
        allocation_epoch=replay.allocation_epoch,
        signal_date=signal_date,
        trading_date=trading_date,
        action="BUY",
        position_id=f"new:{instrument.upper()}:{signal_date.isoformat()}",
        role="entry",
        quantity=quantity,
        order_type="MARKET",
        price=entry_price,
    )
    same_proposal = replay.proposals.get(candidate.proposal_id)
    if same_proposal is not None:
        return (candidate,) if same_proposal.status == "submitted" else ()
    for proposal in replay.outstanding_entries(sleeve_id=sleeve_id, instrument=instrument):
        if proposal.terms.proposal_id != candidate.proposal_id:
            return ()
    return (candidate,)
