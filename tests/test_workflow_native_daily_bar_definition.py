from datetime import date

import pandas as pd

from trading.research_definitions.daily_bar import DailyBarTrialConfig, build_candidates


def _bars() -> pd.DataFrame:
    index = pd.bdate_range("2023-01-02", periods=10)
    return pd.DataFrame(
        {
            "Open": [10, 9, 8, 9, 10, 9, 8, 7, 8, 9],
            "High": [11, 10, 9, 10, 11, 10, 9, 8, 9, 10],
            "Low": [9, 8, 7, 8, 9, 8, 7, 6, 7, 8],
            "Close": [10, 9, 8, 9, 10, 9, 8, 7, 8, 9],
            "Volume": [100] * 10,
        },
        index=index,
    )


def test_down_streak_definition_uses_next_open_and_fixed_expiry() -> None:
    candidates, signals = build_candidates(
        _bars(),
        DailyBarTrialConfig(
            ticker="SCHD",
            history_start=date(2022, 1, 1),
            research_start=date(2023, 1, 1),
            signal_kind="down-streak",
            consecutive_down_sessions=2,
            holding_sessions=2,
        ),
    )

    assert signals == (date(2023, 1, 4), date(2023, 1, 10))
    assert candidates[0].entry_date == date(2023, 1, 5)
    assert candidates[0].entry_price == 9.0
    assert candidates[0].exit_date == date(2023, 1, 9)
    assert candidates[0].exit_price == 9.0
    assert candidates[0].exit_type == "time_expiry"


def test_periodic_baseline_has_no_outcome_filter() -> None:
    candidates, signals = build_candidates(
        _bars(),
        DailyBarTrialConfig(
            ticker="SCHD",
            history_start=date(2022, 1, 1),
            research_start=date(2023, 1, 1),
            signal_kind="periodic-baseline",
            holding_sessions=2,
        ),
    )

    assert len(candidates) == 7
    assert signals[0] == date(2023, 1, 2)
