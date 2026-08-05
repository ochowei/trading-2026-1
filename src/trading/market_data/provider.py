"""External market-data provider boundary."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Protocol

import pandas as pd
import yfinance as yf

from trading.market_data.models import MarketDataSeries


class MarketDataProvider(Protocol):
    """Fetch one inclusive range of observations from an external provider."""

    def fetch(
        self,
        series: MarketDataSeries,
        *,
        start: date | None,
        end: date,
    ) -> pd.DataFrame: ...


class YahooFinanceProvider:
    """Yahoo Finance adjusted daily-bar implementation of the provider boundary."""

    def fetch(
        self,
        series: MarketDataSeries,
        *,
        start: date | None,
        end: date,
    ) -> pd.DataFrame:
        kwargs: dict[str, object] = {
            "progress": False,
            "auto_adjust": True,
            "interval": "1d",
            "threads": False,
        }
        if start is None:
            kwargs["period"] = "max"
        else:
            kwargs["start"] = start.isoformat()
            # yfinance treats end as exclusive; the provider contract is inclusive.
            kwargs["end"] = (end + timedelta(days=1)).isoformat()
        frame = yf.download(series.symbol, **kwargs)
        if frame is None:
            return pd.DataFrame()
        frame = frame.copy()
        if isinstance(frame.columns, pd.MultiIndex):
            if series.symbol in frame.columns.get_level_values(-1):
                frame = frame.xs(series.symbol, axis=1, level=-1)
            else:
                frame.columns = frame.columns.get_level_values(0)
        if frame.columns.duplicated().any():
            frame = frame.loc[:, ~frame.columns.duplicated()]
        if start is None and not frame.empty:
            dates = pd.DatetimeIndex(pd.to_datetime(frame.index))
            if dates.tz is not None:
                dates = dates.tz_localize(None)
            frame = frame.loc[dates.normalize() <= pd.Timestamp(end)]
        return frame
