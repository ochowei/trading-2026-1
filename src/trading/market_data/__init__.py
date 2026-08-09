"""Validated CSV-backed market-data access."""

from trading.market_data.bundle import (
    MarketDataAvailabilityError,
    MarketDataBundle,
    align_auxiliary,
)
from trading.market_data.cache import (
    CacheCorruptionError,
    CachedSeries,
    CacheInspection,
    CsvMarketDataCache,
    MarketDataLockTimeout,
    MarketDataValidationError,
)
from trading.market_data.calendar import PrimaryUSSessionCalendar
from trading.market_data.contracts import MarketDataReader, RefreshKind, SessionCalendar
from trading.market_data.migration_policy import (
    AllowlistDocument,
    BypassFinding,
    MarketDataPolicyError,
    canonical_allowlist_entries,
    enforce_monotonic_shrink,
    load_allowlist,
    scan_experiment_market_data_bypasses,
    scan_non_experiment_yfinance_bypasses,
    scan_non_provider_yfinance_bypasses,
    validate_allowlist,
)
from trading.market_data.models import (
    AvailabilityPolicy,
    CacheMetadata,
    CoverageMode,
    MarketDataCoveragePolicy,
    MarketDataDeclaration,
    MarketDataRequirement,
    MarketDataSeries,
    SignalDecisionTime,
    ValidationOutcome,
    decode_symbol,
    encode_symbol,
)
from trading.market_data.provider import MarketDataProvider, YahooFinanceProvider
from trading.market_data.service import MarketDataService, MarketDataUnavailableError
from trading.market_data.validation import REQUIRED_COLUMNS, validate_daily_bars

__all__ = [
    "REQUIRED_COLUMNS",
    "AvailabilityPolicy",
    "AllowlistDocument",
    "BypassFinding",
    "CacheCorruptionError",
    "CacheInspection",
    "CacheMetadata",
    "CoverageMode",
    "CachedSeries",
    "CsvMarketDataCache",
    "MarketDataSeries",
    "MarketDataLockTimeout",
    "MarketDataAvailabilityError",
    "MarketDataBundle",
    "MarketDataDeclaration",
    "MarketDataCoveragePolicy",
    "MarketDataProvider",
    "MarketDataPolicyError",
    "MarketDataReader",
    "MarketDataRequirement",
    "MarketDataService",
    "MarketDataUnavailableError",
    "MarketDataValidationError",
    "PrimaryUSSessionCalendar",
    "RefreshKind",
    "SessionCalendar",
    "SignalDecisionTime",
    "ValidationOutcome",
    "decode_symbol",
    "encode_symbol",
    "align_auxiliary",
    "canonical_allowlist_entries",
    "enforce_monotonic_shrink",
    "load_allowlist",
    "scan_experiment_market_data_bypasses",
    "scan_non_experiment_yfinance_bypasses",
    "scan_non_provider_yfinance_bypasses",
    "validate_daily_bars",
    "validate_allowlist",
    "YahooFinanceProvider",
]
