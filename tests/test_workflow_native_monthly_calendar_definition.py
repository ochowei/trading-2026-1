from datetime import date

import pandas as pd
import pytest

from trading.research_definitions.monthly_calendar import (
    MonthlyCalendarTrialConfig,
    build_monthly_candidates,
)


def _bars() -> pd.DataFrame:
    index = pd.bdate_range("2023-01-02", "2023-03-10")
    values = list(range(100, 100 + len(index)))
    return pd.DataFrame(
        {
            "Open": values,
            "High": [value + 1 for value in values],
            "Low": [value - 1 for value in values],
            "Close": values,
            "Volume": [100] * len(index),
        },
        index=index,
    )


@pytest.mark.parametrize(
    ("offset", "entry"),
    [
        (-2, date(2023, 1, 27)),
        (-1, date(2023, 1, 30)),
        (0, date(2023, 1, 31)),
    ],
)
def test_month_end_offsets_use_previous_session_decision_and_fixed_expiry(
    offset: int,
    entry: date,
) -> None:
    bars = _bars()
    candidates, signals = build_monthly_candidates(
        bars,
        MonthlyCalendarTrialConfig(
            ticker="ACWI",
            history_start=date(2008, 3, 26),
            research_start=date(2023, 1, 1),
            holding_sessions=5,
            entry_kind="month-end-offset",
            month_end_offset=offset,
        ),
    )

    first = candidates[0]
    entry_position = bars.index.get_loc(pd.Timestamp(entry))
    assert first.signal_date == bars.index[entry_position - 1].date()
    assert signals[0] == first.signal_date
    assert first.entry_date == entry
    assert first.entry_price == float(bars.iloc[entry_position]["Open"])
    assert first.exit_date == bars.index[entry_position + 5].date()
    assert first.exit_type == "time_expiry"


def test_mid_month_baseline_uses_tenth_monthly_session() -> None:
    bars = _bars()
    candidates, _ = build_monthly_candidates(
        bars,
        MonthlyCalendarTrialConfig(
            ticker="ACWI",
            history_start=date(2008, 3, 26),
            research_start=date(2023, 1, 1),
            holding_sessions=5,
            entry_kind="session-ordinal",
            session_ordinal=10,
        ),
    )

    assert candidates[0].entry_date == date(2023, 1, 13)
    assert candidates[1].entry_date == date(2023, 2, 14)


def test_incomplete_final_month_is_excluded_instead_of_force_closed() -> None:
    candidates, _ = build_monthly_candidates(
        _bars(),
        MonthlyCalendarTrialConfig(
            ticker="ACWI",
            history_start=date(2008, 3, 26),
            research_start=date(2023, 1, 1),
            holding_sessions=5,
            entry_kind="month-end-offset",
            month_end_offset=0,
        ),
    )

    assert [candidate.entry_date.month for candidate in candidates] == [1, 2]
    assert all(candidate.exit_date <= date(2023, 3, 10) for candidate in candidates)


def test_partial_first_month_without_requested_offset_is_excluded() -> None:
    bars = _bars().loc[pd.Timestamp("2023-01-30") :]
    candidates, _ = build_monthly_candidates(
        bars,
        MonthlyCalendarTrialConfig(
            ticker="ACWI",
            history_start=date(2023, 1, 30),
            research_start=date(2023, 1, 30),
            holding_sessions=5,
            entry_kind="month-end-offset",
            month_end_offset=-2,
        ),
    )

    assert candidates[0].entry_date == date(2023, 2, 24)


def test_monthly_config_rejects_unregistered_parameter_search() -> None:
    with pytest.raises(ValueError, match="supported offset"):
        MonthlyCalendarTrialConfig(
            ticker="ACWI",
            history_start=date(2008, 3, 26),
            research_start=date(2009, 1, 1),
            holding_sessions=5,
            entry_kind="month-end-offset",
            month_end_offset=-3,
        )
