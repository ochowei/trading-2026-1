from datetime import date

import pandas as pd

from trading.core.sleeve_engine import CandidateTrade, CanonicalSleeveEngine


def test_portfolio_risk_v001_keeps_one_unborrowed_position_per_sleeve() -> None:
    calendar = tuple(pd.to_datetime(["2026-08-10", "2026-08-11", "2026-08-12"]))
    closes = pd.Series([10.0, 10.0, 12.0], index=pd.DatetimeIndex(calendar))
    candidates = tuple(
        CandidateTrade(
            signal_date=date(2026, 8, 7 + offset),
            entry_date=date(2026, 8, 10 + offset),
            entry_price=10.0,
            exit_date=date(2026, 8, 12),
            exit_price=12.0,
            exit_type="target",
        )
        for offset in (0, 1)
    )

    result = CanonicalSleeveEngine(initial_capital=1000.0).run(
        calendar=calendar,
        close_prices=closes,
        candidates=candidates,
    )

    assert [trade.status for trade in result.trades] == ["completed", "skipped"]
    assert result.trades[1].reason == "position_already_open"
    assert all(point.cash >= 0 for point in result.daily_equity)
