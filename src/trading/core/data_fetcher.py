"""Backward-compatible access to validated CSV-backed adjusted daily bars."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from trading.market_data import (
    CsvMarketDataCache,
    MarketDataReader,
    MarketDataSeries,
    MarketDataService,
    YahooFinanceProvider,
)

logger = logging.getLogger(__name__)

MAX_WORKERS: int = 8
SUPPORTED_PERIODS = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}


def create_default_market_data_service(
    *,
    cache_root: Path | str = Path(".cache/market-data"),
    quarantine_root: Path | str = Path(".cache/market-data-quarantine"),
) -> MarketDataService:
    """Build the production Yahoo/CSV market-data service."""
    return MarketDataService(
        provider=YahooFinanceProvider(),
        cache=CsvMarketDataCache(Path(cache_root), Path(quarantine_root)),
    )


class DataFetcher:
    """Fetch multiple ticker frames while preserving the established caller API."""

    def __init__(
        self,
        period: str = "max",
        max_workers: int = MAX_WORKERS,
        start: str | None = None,
        end: str | None = None,
        market_data_service: MarketDataReader | None = None,
    ) -> None:
        self.period = period
        self.max_workers = max_workers
        self.start = start
        self.end = end
        self.market_data_service = market_data_service or create_default_market_data_service()

    def _fetch_single(self, ticker: str) -> pd.DataFrame | None:
        """Resolve one ticker, returning ``None`` on an isolated failure."""
        try:
            if self.start is None and self.period not in SUPPORTED_PERIODS:
                raise ValueError(f"unsupported market-data period: {self.period}")
            start = date.fromisoformat(self.start) if self.start else None
            # The legacy yfinance API treated end as exclusive.
            end = date.fromisoformat(self.end) - timedelta(days=1) if self.end else None
            series = MarketDataSeries.yahoo_adjusted_daily(ticker)
            frame = self.market_data_service.get(series, start=start, end=end)
            if self.start is None:
                frame = _slice_period(frame, self.period)
            logger.info("[DataFetcher] %s: resolved %d cached rows", ticker, len(frame))
            return frame
        except Exception as exc:
            logger.error("[DataFetcher] failed to resolve %s: %s", ticker, exc)
            return None

    def fetch_all(self, tickers: list[str]) -> dict[str, pd.DataFrame]:
        """Resolve all tickers concurrently and omit only isolated failures."""
        results: dict[str, pd.DataFrame] = {}
        logger.info(
            "[DataFetcher] resolving %d tickers with %d workers",
            len(tickers),
            self.max_workers,
        )
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._fetch_single, ticker): ticker for ticker in tickers}
            for future in as_completed(futures):
                ticker = futures[future]
                try:
                    frame = future.result()
                    if frame is not None and not frame.empty:
                        results[ticker] = frame
                except Exception as exc:
                    logger.error("[DataFetcher] failed to process %s: %s", ticker, exc)
        logger.info("[DataFetcher] resolved %d/%d tickers", len(results), len(tickers))
        return results


def _slice_period(frame: pd.DataFrame, period: str) -> pd.DataFrame:
    if period == "max":
        return frame
    if period == "1d":
        return frame.tail(1)
    if period == "5d":
        return frame.tail(5)
    cutoff = frame.index[-1]
    if period == "ytd":
        start = pd.Timestamp(year=cutoff.year, month=1, day=1)
    elif period.endswith("mo"):
        start = cutoff - pd.DateOffset(months=int(period[:-2]))
    else:
        start = cutoff - pd.DateOffset(years=int(period[:-1]))
    return frame.loc[start:].copy()
