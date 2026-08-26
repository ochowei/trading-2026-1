import pandas as pd

from trading.market_data import validate_daily_bars
from trading.market_data.validation import canonical_daily_bar_csv_bytes


def bars(dates: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": [10.0] * len(dates),
            "High": [12.0] * len(dates),
            "Low": [9.0] * len(dates),
            "Close": [11.0] * len(dates),
            "Volume": [100] * len(dates),
        },
        index=pd.to_datetime(dates),
    )


def test_identical_duplicates_are_deduplicated() -> None:
    frame = bars(["2026-08-03", "2026-08-04"])
    frame = pd.concat([frame.iloc[:1], frame.iloc[:1], frame.iloc[1:]])

    normalized, outcome = validate_daily_bars(frame)

    assert outcome.is_valid
    assert outcome.row_count == 2
    assert list(normalized.index) == list(pd.to_datetime(["2026-08-03", "2026-08-04"]))


def test_conflicting_duplicate_is_corruption() -> None:
    frame = bars(["2026-08-03", "2026-08-03"])
    frame.iloc[1, frame.columns.get_loc("Close")] = 11.5

    _, outcome = validate_daily_bars(frame)

    assert not outcome.is_valid
    assert "conflicting duplicate dates" in outcome.errors


def test_invalid_rows_are_reported_without_being_dropped() -> None:
    frame = bars(["2026-08-03", "2026-08-04", "2026-08-05"])
    frame.loc["2026-08-03", "Close"] = float("nan")
    frame.loc["2026-08-04", "Low"] = 13.0
    frame.loc["2026-08-05", "Volume"] = -1

    normalized, outcome = validate_daily_bars(frame)

    assert not outcome.is_valid
    assert len(normalized) == 3
    assert "required values contain NaN" in outcome.errors
    assert "invalid OHLC relationships" in outcome.errors
    assert "negative volume" in outcome.errors


def test_ohlc_relationship_tolerance_accepts_adjustment_rounding_noise() -> None:
    frame = bars(["2026-08-03"])
    frame.loc["2026-08-03", "Low"] = frame.loc["2026-08-03", "Open"] + 3e-13
    frame.loc["2026-08-03", "High"] = frame.loc["2026-08-03", "Close"] - 3e-13

    _, outcome = validate_daily_bars(frame)

    assert outcome.is_valid


def test_ohlc_relationship_tolerance_does_not_hide_material_corruption() -> None:
    frame = bars(["2026-08-03"])
    frame.loc["2026-08-03", "Low"] = frame.loc["2026-08-03", "Open"] + 1e-6

    _, outcome = validate_daily_bars(frame)

    assert not outcome.is_valid
    assert "invalid OHLC relationships" in outcome.errors


def test_canonical_csv_bytes_are_stable_after_float_csv_round_trip() -> None:
    frame = pd.DataFrame(
        {
            "Open": [24.267609235348207],
            "High": [24.353360504731061],
            "Low": [24.216158473718494],
            "Close": [24.336210250854492],
            "Volume": [201300.0],
        },
        index=pd.to_datetime(["1993-02-02"]),
    )

    first = canonical_daily_bar_csv_bytes(frame)
    replayed = pd.read_csv(pd.io.common.BytesIO(first), parse_dates=["Date"], index_col="Date")

    assert canonical_daily_bar_csv_bytes(replayed) == first


def test_dates_must_be_ordered_and_cover_expected_sessions() -> None:
    reversed_frame = bars(["2026-08-04", "2026-08-03"])
    _, reversed_outcome = validate_daily_bars(reversed_frame)
    missing_frame = bars(["2026-08-03", "2026-08-05"])
    _, missing_outcome = validate_daily_bars(
        missing_frame,
        expected_sessions=pd.to_datetime(["2026-08-03", "2026-08-04", "2026-08-05"]),
    )

    assert "dates are not strictly increasing" in reversed_outcome.errors
    assert "missing expected primary sessions: 2026-08-04" in missing_outcome.errors


def test_unexpected_non_session_dates_are_corruption() -> None:
    frame = bars(["2026-08-07", "2026-08-08", "2026-08-10"])

    normalized, outcome = validate_daily_bars(
        frame,
        expected_sessions=pd.to_datetime(["2026-08-07", "2026-08-10"]),
    )

    assert not outcome.is_valid
    assert len(normalized) == 3
    assert "unexpected non-session dates: 2026-08-08" in outcome.errors


def test_required_columns_are_enforced() -> None:
    frame = bars(["2026-08-03"]).drop(columns="Volume")

    normalized, outcome = validate_daily_bars(frame)

    assert not outcome.is_valid
    assert normalized.empty
    assert "missing required columns: Volume" in outcome.errors


def test_non_finite_required_values_are_corruption() -> None:
    frame = bars(["2026-08-03", "2026-08-04"])
    frame["Volume"] = frame["Volume"].astype(float)
    frame.loc["2026-08-03", "High"] = float("inf")
    frame.loc["2026-08-04", "Volume"] = float("-inf")

    normalized, outcome = validate_daily_bars(frame)

    assert not outcome.is_valid
    assert len(normalized) == 2
    assert "required values must be finite" in outcome.errors
