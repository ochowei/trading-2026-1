# Followup Backtest Start Date Design

## Objective

Extend `followup-backtest` with an optional starting date while preserving the existing default of
backtesting the most recent completed trading sessions.

```bash
uv run trading followup-backtest
uv run trading followup-backtest --days 180
uv run trading followup-backtest --start 2025-01-01 --days 126
```

`--days` continues to mean completed trading sessions, not calendar days.

## CLI Contract

Add an optional `--start YYYY-MM-DD` argument to `followup-backtest`.

- Without `--start`, select the last `--days` completed sessions. This is the existing behavior.
- With `--start`, select the first `--days` completed sessions whose dates are on or after the
  requested date.
- Parse `--start` as a strict ISO calendar date in `YYYY-MM-DD` form. Invalid dates or formats are
  rejected by argparse with a clear error.
- `--days` remains a strictly positive integer and defaults to 126.
- No `--end` argument is added. This keeps duration expressed in trading sessions and avoids
  conflicting range inputs.

Examples:

```text
--start 2026-01-05 --days 5  -> begins on 2026-01-05 if it is a completed session
--start 2026-01-03 --days 5  -> begins on the first completed session after the weekend
```

## Calendar Selection

The first successfully loaded strategy remains the canonical session calendar, matching the current
implementation.

All incomplete current-day bars are removed before the evaluation calendar is selected. Calendar
selection then follows one of two paths:

1. `start is None`: take the final N canonical sessions.
2. `start is not None`: filter canonical sessions to dates on or after `start`, then take the first N.

The resulting calendar is the only set of dates included in strategy and portfolio performance.
Indicators and signals are still calculated over the full downloaded history before intersection
with this calendar. Long indicator warmup and cooldown state therefore continue across the requested
start boundary without resets or look-ahead.

## Boundary and Error Behavior

- If fewer than N completed sessions exist after the requested start, run the available sessions and
  emit a warning containing the requested count, actual count, and actual range.
- If the requested start is earlier than the earliest available canonical session, begin at the
  earliest available session and emit a warning that the requested boundary could not be reached.
- If no completed canonical session exists on or after the requested start, return a structured
  result with no portfolio, include a clear error warning, and make the CLI exit nonzero.
- Individual ticker gaps and failures retain their existing warnings and partial-failure behavior.
- A weekend or market holiday is not an error; it advances naturally to the next completed canonical
  session.

## Structured Results and Reporting

Add `requested_start: pd.Timestamp | None` to `FollowupBacktestResult`.

The text renderer prints the requested start when supplied, followed by the actual evaluation range.
Consumers of the structured result can distinguish a recent-window request from an anchored-window
request without parsing stdout.

The strategy result, trade records, daily equity curves, sleeve accounting, portfolio metrics, open
position mark-to-market treatment, and execution models remain unchanged.

## Components

### `src/trading/cli.py`

- Add a strict ISO-date argparse converter.
- Register the optional `--start` argument.
- Pass the parsed date to `run_followup_backtest`.
- Keep all existing `followup` and unanchored `followup-backtest` behavior unchanged.

### `src/trading/followup_backtest.py`

- Accept `start: date | datetime | pd.Timestamp | str | None` at the calculation boundary, normalize
  it to a date-only `pd.Timestamp`, and reject invalid direct-call values with `ValueError`.
- Select the canonical evaluation calendar according to the rules above.
- Return the normalized requested start in `FollowupBacktestResult`.
- Render requested and actual boundaries separately.

### Documentation

Update `README.md` and `CLAUDE.md` with the anchored-window example and the trading-session semantics.
No file under `pm/` is changed.

## Test Design

Use fixed local data only; no test may depend on live market data.

- CLI accepts `--start YYYY-MM-DD` and passes it to the calculation layer.
- CLI rejects malformed dates and impossible calendar dates.
- Omitting `--start` still selects the most recent N completed sessions.
- A trading-day start includes that session.
- A weekend or missing canonical date advances to the first later completed session.
- An anchored calendar contains exactly N sessions when enough data exists.
- Fewer than N remaining sessions returns the actual suffix and a warning.
- A start after the final completed session returns no portfolio and causes CLI failure.
- Indicator warmup and cooldown are computed before the anchored slice.
- The renderer shows requested start and actual period.
- Existing followup-backtest ledger, failure, and compatibility tests remain green.

## Non-Goals

- Adding an end-date argument.
- Changing strategy definitions or maintaining a second strategy list.
- Changing portfolio allocation or performance calculations.
- Changing any experiment's transaction costs, slippage, fills, stops, targets, or expiry behavior.
- Refactoring unrelated data-fetching or experiment code.
