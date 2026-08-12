from datetime import date

import pytest

from trading.core.proposals import ProposalTerms


def _proposal(order_type: str) -> ProposalTerms:
    return ProposalTerms.create(
        sleeve_id="SPY",
        instrument="SPY",
        allocation_epoch="epoch-0001",
        signal_date=date(2026, 8, 10),
        trading_date=date(2026, 8, 11),
        action="BUY",
        position_id="position-1",
        role="entry",
        quantity="1",
        order_type=order_type,
    )


def test_firstrade_manual_trading_v001_exposes_only_supported_proposal_types() -> None:
    assert {_proposal(item).order_type for item in ("MARKET", "LIMIT", "STOP")} == {
        "MARKET",
        "LIMIT",
        "STOP",
    }
    with pytest.raises(ValueError, match="MARKET, LIMIT, or STOP"):
        _proposal("TRAILING_STOP")
