"""Normalization and fail-closed validation for adjusted daily bars."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from trading.market_data.models import ValidationOutcome

REQUIRED_COLUMNS = ("Open", "High", "Low", "Close", "Volume")


def canonical_daily_bar_csv_bytes(frame: pd.DataFrame) -> bytes:
    """Serialize normalized adjusted daily bars to their one canonical byte form."""
    rendered = frame.loc[:, REQUIRED_COLUMNS].to_csv(
        index=True,
        index_label="Date",
        date_format="%Y-%m-%d",
        float_format="%.17g",
        lineterminator="\n",
    )
    return rendered.encode("utf-8")


def _invalid_empty(error: str) -> tuple[pd.DataFrame, ValidationOutcome]:
    return (
        pd.DataFrame(columns=REQUIRED_COLUMNS),
        ValidationOutcome(False, (error,), 0, None),
    )


def validate_daily_bars(
    frame: pd.DataFrame,
    *,
    expected_sessions: Iterable[object] | None = None,
) -> tuple[pd.DataFrame, ValidationOutcome]:
    """Return deterministic normalized bars and a validation outcome.

    Invalid observations remain in the returned frame for diagnosis. The sole
    exception is a byte-for-byte-equivalent duplicate, which the contract
    explicitly permits us to deduplicate.
    """
    if frame is None:
        return _invalid_empty("market data is missing")

    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        return _invalid_empty(f"missing required columns: {', '.join(missing)}")

    normalized = frame.loc[:, REQUIRED_COLUMNS].copy()
    try:
        if "Date" in frame.columns:
            dates = pd.to_datetime(frame["Date"], errors="raise")
        else:
            dates = pd.to_datetime(frame.index, errors="raise")
    except (TypeError, ValueError) as exc:
        return _invalid_empty(f"invalid dates: {exc}")

    if isinstance(dates, pd.Series):
        date_index = pd.DatetimeIndex(dates.array)
    else:
        date_index = pd.DatetimeIndex(dates)
    if date_index.tz is not None:
        date_index = date_index.tz_localize(None)
    normalized.index = date_index.normalize()
    normalized.index.name = "Date"
    normalized = normalized.loc[~normalized.reset_index().duplicated().to_numpy()]

    errors: list[str] = []
    if normalized.index.duplicated(keep=False).any():
        errors.append("conflicting duplicate dates")
    if not normalized.index.is_monotonic_increasing or normalized.index.has_duplicates:
        errors.append("dates are not strictly increasing")

    numeric = normalized.apply(pd.to_numeric, errors="coerce")
    if numeric.isna().any(axis=None):
        errors.append("required values contain NaN")
    if not np.isfinite(numeric.to_numpy()).all():
        errors.append("required values must be finite")
    invalid_ohlc = (
        (numeric["Low"] > numeric["High"])
        | (numeric["Low"] > numeric[["Open", "Close"]].min(axis=1))
        | (numeric["High"] < numeric[["Open", "Close"]].max(axis=1))
    )
    if invalid_ohlc.any():
        errors.append("invalid OHLC relationships")
    if (numeric["Volume"] < 0).any():
        errors.append("negative volume")
    normalized = numeric.astype({column: "float64" for column in REQUIRED_COLUMNS})

    if expected_sessions is not None and len(normalized):
        expected = pd.DatetimeIndex(pd.to_datetime(list(expected_sessions))).normalize()
        expected = expected[
            (expected >= normalized.index.min()) & (expected <= normalized.index.max())
        ]
        missing_sessions = expected.difference(normalized.index)
        if len(missing_sessions):
            rendered = ", ".join(item.strftime("%Y-%m-%d") for item in missing_sessions)
            errors.append(f"missing expected primary sessions: {rendered}")
        unexpected_sessions = normalized.index.difference(expected)
        if len(unexpected_sessions):
            rendered = ", ".join(item.strftime("%Y-%m-%d") for item in unexpected_sessions)
            errors.append(f"unexpected non-session dates: {rendered}")

    cutoff = normalized.index.max().date() if len(normalized) else None
    return normalized, ValidationOutcome(not errors, tuple(errors), len(normalized), cutoff)
