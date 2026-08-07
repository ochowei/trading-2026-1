"""Validated cached access and explicit refresh orchestration."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import UTC, date, datetime

import pandas as pd

from trading.market_data.bundle import MarketDataBundle
from trading.market_data.cache import (
    CacheCorruptionError,
    CachedSeries,
    CacheInspection,
    CsvMarketDataCache,
    MarketDataLockTimeout,
    MarketDataValidationError,
)
from trading.market_data.calendar import PrimaryUSSessionCalendar
from trading.market_data.contracts import RefreshKind, SessionCalendar
from trading.market_data.models import (
    MarketDataCoveragePolicy,
    MarketDataDeclaration,
    MarketDataRequirement,
    MarketDataSeries,
    SignalDecisionTime,
)
from trading.market_data.provider import MarketDataProvider
from trading.market_data.validation import validate_daily_bars


class MarketDataUnavailableError(RuntimeError):
    """Fresh, valid market data could not be obtained."""


class MarketDataService:
    """Resolve one series from validated cache or the declared provider boundary."""

    def __init__(
        self,
        *,
        provider: MarketDataProvider,
        cache: CsvMarketDataCache,
        calendar: SessionCalendar | None = None,
        now: Callable[[], datetime] | None = None,
        incremental_overlap_sessions: int = 5,
    ) -> None:
        if incremental_overlap_sessions < 1:
            raise ValueError("incremental_overlap_sessions must be positive")
        self.provider = provider
        self.cache = cache
        self.calendar = calendar or PrimaryUSSessionCalendar()
        self.now = now or (lambda: datetime.now(UTC))
        self.incremental_overlap_sessions = incremental_overlap_sessions

    def get(
        self,
        series: MarketDataSeries,
        *,
        start: date | None = None,
        end: date | None = None,
        coverage_policy: MarketDataCoveragePolicy | None = None,
    ) -> pd.DataFrame:
        """Return a fresh normalized frame, downloading only when needed."""
        return self._resolve(
            series,
            start=start,
            end=end,
            coverage_policy=coverage_policy,
            refresh_mode=None,
            refresh_started_generation=None,
        )

    def refresh(
        self,
        series: MarketDataSeries,
        *,
        mode: RefreshKind | str = RefreshKind.INCREMENTAL,
        start: date | None = None,
        end: date | None = None,
        coverage_policy: MarketDataCoveragePolicy | None = None,
    ) -> pd.DataFrame:
        """Explicitly refresh a series incrementally or from full history."""
        try:
            kind = RefreshKind(mode)
        except ValueError:
            raise ValueError("mode must be incremental or full") from None
        if kind is RefreshKind.FULL and start is not None:
            raise ValueError(
                "full refresh does not accept start; it always downloads complete history"
            )
        return self._resolve(
            series,
            start=start,
            end=end,
            coverage_policy=coverage_policy,
            refresh_mode=kind,
            refresh_started_generation=self.cache.generation_token(series),
        )

    def status(
        self,
        series: MarketDataSeries,
        *,
        coverage_policy: MarketDataCoveragePolicy | None = None,
    ) -> CacheInspection:
        """Return diagnostics under an existing shared lock, without network or writes."""
        try:
            with self.cache.read_lock(series):
                inspection = self.cache.inspect_locked(series, coverage_policy=coverage_policy)
                if inspection.state != "valid" or inspection.metadata is None:
                    return inspection
                cached = self.cache.load_locked(series, coverage_policy=coverage_policy)
                if cached is None:
                    return CacheInspection("missing")
                _, outcome = validate_daily_bars(
                    cached.bars,
                    expected_sessions=self._expected_for(cached.bars, coverage_policy),
                )
                if not outcome.is_valid:
                    return CacheInspection("corrupt", cached.metadata, outcome.errors)
                target = self.calendar.latest_completed_session(self.now())
                state = "stale" if cached.metadata.data_cutoff < target else "valid"
                return CacheInspection(state, cached.metadata)
        except MarketDataLockTimeout as exc:
            return CacheInspection("busy", errors=(str(exc),))

    def build_bundle(
        self,
        requirements: Iterable[MarketDataRequirement] | MarketDataDeclaration,
        decision_time: SignalDecisionTime,
        *,
        decision_times: Iterable[SignalDecisionTime] | None = None,
    ) -> MarketDataBundle:
        """Resolve every declared series through this service into a read-only bundle."""
        requirement_list = MarketDataBundle.validate_requirements(requirements)
        frames = {
            requirement.series: self.get(
                requirement.series,
                start=requirement.history_start,
                end=decision_time.session,
                coverage_policy=requirement.coverage_policy,
            )
            for requirement in requirement_list
        }
        return MarketDataBundle.from_requirements(
            requirement_list,
            frames,
            decision_time=decision_time,
            decision_times=decision_times,
            calendar=self.calendar,
        )

    def _resolve(
        self,
        series: MarketDataSeries,
        *,
        start: date | None,
        end: date | None,
        coverage_policy: MarketDataCoveragePolicy | None,
        refresh_mode: RefreshKind | None,
        refresh_started_generation: tuple[int, int, int, int] | None,
    ) -> pd.DataFrame:
        policy = coverage_policy or MarketDataCoveragePolicy.xnys()
        target = (
            self.calendar.session_on_or_before(end)
            if end is not None
            else self.calendar.latest_completed_session(self.now())
        )
        if start is not None and start > target:
            raise MarketDataUnavailableError("requested start is after the data cutoff")

        with self.cache.lock(series):
            force_full = refresh_mode is RefreshKind.FULL
            try:
                cached = self.cache.load_locked(series, coverage_policy=policy)
            except CacheCorruptionError:
                self.cache.quarantine_locked(series)
                cached = None
                force_full = True
            if cached is not None:
                _, cache_outcome = validate_daily_bars(
                    cached.bars,
                    expected_sessions=self._expected_for(cached.bars, policy),
                )
                if not cache_outcome.is_valid:
                    self.cache.quarantine_locked(series)
                    cached = None
                    force_full = True
            refreshed_while_waiting = (
                refresh_mode is not None
                and cached is not None
                and self.cache.generation_token(series) != refresh_started_generation
            )
            if refreshed_while_waiting:
                force_full = False
            if (
                refresh_mode is not None
                and cached is not None
                and cached.metadata.data_cutoff > target
            ):
                raise MarketDataUnavailableError(
                    f"refresh cutoff {target} precedes active cache cutoff "
                    f"{cached.metadata.data_cutoff}"
                )

            if force_full:
                downloaded = self._download(
                    series,
                    start=None,
                    end=target,
                    require_cutoff=True,
                    coverage_policy=policy,
                )
                cached = self.cache.publish_locked(
                    series,
                    downloaded,
                    refresh_kind=RefreshKind.FULL,
                    refreshed_at=self.now(),
                    previous_metadata=cached.metadata if cached else None,
                    coverage_policy=policy,
                )
            elif cached is None:
                downloaded = self._download(
                    series,
                    start=start,
                    end=target,
                    require_cutoff=True,
                    coverage_policy=policy,
                )
                cached = self.cache.publish_locked(
                    series,
                    downloaded,
                    refresh_kind=RefreshKind.INCREMENTAL,
                    refreshed_at=self.now(),
                    coverage_policy=policy,
                )
            else:
                cached = self._refresh_cached_if_needed(
                    series,
                    cached,
                    start=start,
                    target=target,
                    force=(refresh_mode is RefreshKind.INCREMENTAL and not refreshed_while_waiting),
                    coverage_policy=policy,
                )

            result = cached.bars.loc[: pd.Timestamp(target)]
            if start is not None:
                result = result.loc[pd.Timestamp(start) :]
            if result.empty:
                raise MarketDataUnavailableError(f"no market data available for {series.symbol}")
            return result.copy(deep=True)

    def _refresh_cached_if_needed(
        self,
        series: MarketDataSeries,
        cached: CachedSeries,
        *,
        start: date | None,
        target: date,
        force: bool,
        coverage_policy: MarketDataCoveragePolicy,
    ) -> CachedSeries:
        combined = cached.bars
        changed = False
        cache_start = combined.index[0].date()
        if start is not None and start < cache_start:
            left_end = self.calendar.session_offset(cache_start, -1)
            left = self._download(
                series,
                start=start,
                end=left_end,
                require_cutoff=False,
                coverage_policy=coverage_policy,
            )
            combined = pd.concat([left, combined])
            changed = True

        cutoff = combined.index[-1].date()
        if cutoff < target or force:
            overlap_offset = -(self.incremental_overlap_sessions - 1)
            overlap_start = self.calendar.session_offset(cutoff, overlap_offset)
            right = self._download(
                series,
                start=overlap_start,
                end=target,
                require_cutoff=True,
                coverage_policy=coverage_policy,
            )
            combined = pd.concat(
                [combined.loc[combined.index < pd.Timestamp(overlap_start)], right]
            )
            changed = True

        if not changed:
            return cached
        return self.cache.publish_locked(
            series,
            combined,
            refresh_kind=RefreshKind.INCREMENTAL,
            refreshed_at=self.now(),
            previous_metadata=cached.metadata,
            coverage_policy=coverage_policy,
        )

    def _download(
        self,
        series: MarketDataSeries,
        *,
        start: date | None,
        end: date,
        require_cutoff: bool,
        coverage_policy: MarketDataCoveragePolicy,
    ) -> pd.DataFrame:
        try:
            frame = self.provider.fetch(series, start=start, end=end)
        except Exception as exc:
            raise MarketDataUnavailableError(
                f"provider fetch failed for {series.symbol}: {exc}"
            ) from exc
        if frame is None or frame.empty:
            raise MarketDataUnavailableError(f"provider returned no data for {series.symbol}")
        normalized, outcome = validate_daily_bars(
            frame, expected_sessions=self._expected_for(frame, coverage_policy)
        )
        if not outcome.is_valid:
            raise MarketDataValidationError("; ".join(outcome.errors))
        if require_cutoff:
            if outcome.data_cutoff is None:
                raise MarketDataUnavailableError(
                    f"provider data for {series.symbol} has no usable observations"
                )
            if coverage_policy.requires_complete_sessions and outcome.data_cutoff != end:
                raise MarketDataUnavailableError(
                    f"provider data for {series.symbol} ends at {outcome.data_cutoff}, expected {end}"
                )
            if not coverage_policy.requires_complete_sessions and outcome.data_cutoff > end:
                raise MarketDataUnavailableError(
                    f"provider data for {series.symbol} ends after requested cutoff {end}"
                )
        return normalized

    def _expected_for(
        self,
        frame: pd.DataFrame,
        coverage_policy: MarketDataCoveragePolicy | None = None,
    ) -> pd.DatetimeIndex | None:
        policy = coverage_policy or MarketDataCoveragePolicy.xnys()
        if not policy.requires_complete_sessions:
            return None
        index = pd.DatetimeIndex(pd.to_datetime(frame.index)).tz_localize(None).normalize()
        return self.calendar.sessions_in_range(index.min().date(), index.max().date())
