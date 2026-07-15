# Followup Backtest Design

## Objective

Add a read-only `followup-backtest` command that evaluates the current strategy set from
`src/trading/followup.py` over the last N completed US trading sessions:

```bash
uv run trading followup-backtest
uv run trading followup-backtest --days 180
```

The default is 126 trading sessions. `--days` must be a positive integer. The new command must
not change the existing `uv run trading followup` default of 60 trading sessions or its Firstrade
order-report behavior.

The command reports both isolated strategy performance and a real equal-weight portfolio ledger.
All calculations return structured Python results before any CLI rendering occurs.

## Approved Performance Model

Use an equal-weight strategy-sleeve portfolio ledger.

- Initial portfolio equity is USD 100,000.
- At the start of the evaluation period, the portfolio creates one sleeve for every entry in the
  current `followup.STRATEGIES` list.
- Each sleeve receives `100000 / len(STRATEGIES)` in cash.
- The allocation is determined before downloads begin. A failed strategy keeps its sleeve in cash;
  its capital is not redistributed to successful strategies.
- Sleeves do not rebalance or lend cash to each other during the evaluation period.
- Fractional shares are allowed so that stock price and whole-share residuals do not introduce an
  unintended weighting bias.
- A valid entry invests all cash currently available in that strategy's sleeve.
- A sleeve may have only one open position. A later entry for the same strategy while that position
  is open is recorded as `skipped_insufficient_cash`.
- If different `STRATEGIES` entries point to the same ticker, their independent sleeves may hold
  simultaneous positions in that ticker.
- Signals from different strategies on the same day use their preallocated sleeves and therefore do
  not compete based on list order.
- Margin, negative cash, and cross-sleeve borrowing are prohibited.

The portfolio model is initially equal-weighted rather than continually rebalanced. This preserves
the realized compounding of each strategy while making capital usage explicit.

## Evaluation Boundary and Data Preparation

### Completed bars

The evaluator excludes a primary ticker's last bar when that bar is dated today in New York and the
New York time is earlier than 16:30. The existing `followup` completed-bar rule is reused rather than
reimplemented. Bars dated before today are treated as complete. Tests inject the clock so this rule
does not depend on wall time.

### Canonical evaluation calendar

After all primary ticker downloads are attempted, the first successfully downloaded strategy in
`STRATEGIES` order supplies the canonical US session calendar. The evaluator takes the last `days`
completed dates from that ticker. Every successful strategy is evaluated against those same dates.

This gives the portfolio one deterministic date range and exactly N sessions when the reference
ticker has enough history. If the reference ticker has fewer than N completed sessions, the command
uses all available completed sessions and emits a portfolio-level warning with the actual date range.

For another ticker:

- Missing canonical sessions are warnings, not fabricated signal or execution bars.
- The strategy cannot signal, enter, or exit on a missing session.
- For an already open position, portfolio valuation forward-fills the most recent completed close.
- Its strategy report states the requested period, actual first and last available dates, available
  session count, and missing-session count.

If no primary ticker download succeeds, the result contains all strategy failures, no strategy or
portfolio equity curve, and the CLI exits nonzero after printing the errors.

### Warmup and cooldown

For each strategy, primary data is requested from its own `config.data_start`. This is deliberately
not a fixed 365-day or fixed-row warmup. The full available history is passed through
`compute_indicators()` and then `detect_signals()` before the canonical evaluation dates are sliced.

Consequences:

- SMA 200 and any other rolling indicator can be valid on the first evaluation session when enough
  history exists.
- Each row only uses indicator and signal data available on or before that row.
- Detector cooldown state is established by pre-period signals and therefore carries into the first
  evaluation session.
- Pre-period signals affect cooldown only. The portfolio starts entirely in cash and does not inherit
  positions opened before the evaluation boundary.
- Indicator warmup rows and pre-period signals are never included in evaluation performance.

The evaluator requires `detect_signals()` to return a boolean `Signal` column aligned to the primary
data. A missing or invalid `Signal` column is a visible strategy failure. Indicator warmup `NaN`
values are retained and cannot generate a signal; the evaluator never fills or invents indicator
values.

### Auxiliary market data

Some current detectors fetch auxiliary series such as VIX, QQQ, DXY, SMH, MOVE, or XLV inside
`compute_indicators()`. The evaluator continues to use the detector implementation so that its
existing alignment, fallback, and no-look-ahead behavior remain authoritative. An exception raised
by indicator or signal calculation becomes a visible strategy failure and does not stop other
strategies. Existing detector-defined fallback behavior that logs an auxiliary-data error and
disables a filter remains unchanged and is disclosed as a limitation in the report.

## Execution Semantics

Every strategy is loaded dynamically through its `experiment_name` from the current
`followup.STRATEGIES` entry. Its `create_config()`, `create_detector()`, and `create_backtester()`
methods remain authoritative.

All 26 strategies currently selected by `STRATEGIES` use execution-model backtesters. The standard
execution model retains:

- signal at the completed close;
- next-session market entry at the open with the strategy backtester's buy slippage;
- Day profit-target limit order;
- GTC stop-market order with sell slippage;
- pessimistic stop-first treatment when stop and target are both reachable on one bar;
- next-session market exit after expiry with sell slippage; and
- an unfilled signal when no next-session entry bar exists.

EWT retains its existing trailing-stop activation, trailing distance, slippage, and pessimistic
intrabar rules through its custom backtester.

Within a sleeve, same-day events are processed in this order:

1. Expiry exits scheduled for that day's open release cash.
2. New next-open entries attempt to use available cash.
3. Intraday stop, target, pessimistic, and trailing-stop exits release cash after the open.
4. The remaining position is marked at that day's completed close.

Therefore, proceeds from an intraday exit cannot finance an entry that should already have executed
at the same day's open.

Commissions remain zero because the existing backtesters do not model commissions. The evaluator
does not add a second layer of transaction costs or slippage.

## Open Positions

The standard and trailing execution backtesters gain a structured, opt-in mode that preserves a
position when the available data ends before a real exit occurs. Their existing default behavior and
result keys remain unchanged for all existing callers.

In followup-backtest mode, an open position contains at least:

- signal date and entry date;
- entry price and quantity;
- current target and stop prices;
- holding sessions elapsed;
- latest completed close and valuation date;
- unrealized return;
- trailing-stop state when applicable; and
- status `open`.

An open position is marked to the last completed adjusted close. No hypothetical sale or sell
slippage is applied because the position has not been sold. Its unrealized profit or loss contributes
to the strategy and portfolio equity curves, cumulative return, drawdown, and final asset value. It
does not contribute to completed-trade win rate or average completed-trade return.

Signals on the final evaluation session that require next-open execution are recorded as unfilled,
not open positions.

## Strategy Metrics

Each strategy result contains its experiment name, label, ticker, requested and actual date range,
data warnings or errors, execution-model metadata, daily sleeve equity, and detailed event records.

The report includes:

- raw post-cooldown signal count in the evaluation period;
- completed trade count;
- open position count;
- unfilled entry count;
- insufficient-cash skip count;
- completed-trade win rate;
- cumulative sleeve return, including open-position mark-to-market;
- average completed-trade return;
- annualized daily Sharpe ratio with zero risk-free rate;
- maximum drawdown from the daily sleeve equity curve; and
- trade details with `completed`, `open`, `unfilled`, or `skipped_insufficient_cash` status.

When there are no completed trades, win rate and average trade return are represented as unavailable
in the structured result and rendered as `N/A`, rather than as a misleading zero.

## Portfolio Metrics

Daily portfolio equity is the sum of sleeve cash and marked position values. Portfolio return is not
the sum of trade returns and is not an independent full-capital compound of every trade.

For an equity series `E`:

- total return is `E[-1] / E[0] - 1`;
- annualized return is `(E[-1] / E[0]) ** (252 / (len(E) - 1)) - 1` when at least two observations
  and positive equity exist;
- daily returns are `E.pct_change()`;
- annualized volatility is the sample standard deviation of daily returns times `sqrt(252)`;
- Sharpe ratio is daily mean divided by daily sample standard deviation times `sqrt(252)`, with a
  zero risk-free rate;
- maximum drawdown is the minimum of `E / E.cummax() - 1`; and
- final asset value is `E[-1]`.

Zero-volatility metrics are represented as unavailable rather than infinity.

Each daily portfolio record contains date, total equity, cash, marked position value, daily return,
drawdown, capital utilization, and open-position count. Capital utilization is marked position value
divided by total equity. The summary reports average utilization, maximum utilization, and maximum
simultaneous open positions.

The structured daily records are suitable for later plotting but this feature does not add charts or
file export.

## Structured Interfaces and Responsibilities

### `src/trading/followup.py`

Remains the only strategy-selection source and retains the existing 60-day order-report default. The
completed-bar helper is made clock-injectable or moved to a small shared module without changing its
default behavior.

### `src/trading/followup_backtest.py`

Owns followup-backtest orchestration, result dataclasses, strategy evaluation, sleeve accounting,
portfolio metrics, and text rendering. Calculation functions accept injected strategy definitions,
data fetchers, and clocks for deterministic tests. Rendering consumes structured results and does not
perform downloads or calculations.

### Execution backtesters

`src/trading/core/execution_backtester.py` and the EWT trailing-stop backtester expose a compatible
opt-in open-position result. Existing `run(df)` behavior stays the default. The new evaluator uses the
opt-in behavior and never substitutes a new generic execution model for a strategy's selected
backtester.

### `src/trading/cli.py`

Registers `followup-backtest`, sets `--days` to 126 by default, rejects zero, negative, non-integer,
or missing values through argparse with a clear message, renders the result, and returns nonzero when
all strategies fail. A partial failure prints errors but completes successfully so the remaining
strategy and portfolio results are available.

## Error and Warning Policy

- Primary ticker missing from `DataFetcher` output: visible strategy error; continue other strategies.
- Indicator or detector exception: visible strategy error; continue other strategies.
- Fewer than requested completed sessions: visible warning with requested count, actual count, and
  actual range.
- Missing canonical sessions for one ticker: visible warning and missing-session count.
- Empty `STRATEGIES`: clear error, no division by zero, nonzero CLI exit.
- All strategies fail: print every failure and exit nonzero.
- Some strategies fail: retain failed sleeves as cash, show partial-results warning, and exit zero.
- No signal or no completed trade: valid result, not an error.

No failure is silently discarded.

## Compatibility Requirements

- `uv run trading followup` continues to use 60 sessions and generate the existing Firstrade report.
- `uv run trading run`, comparison commands, and existing experiment result formats retain their
  current defaults.
- Existing backtester calls do not start returning open positions unless they opt in.
- `STRATEGIES` is read at call time so additions, removals, or replacements are automatically used by
  followup-backtest and can be monkeypatched in tests.
- No file under `pm/` is modified.

## Test Design

Add pytest to the development dependency group and create deterministic tests using fixed OHLCV
fixtures and fake strategy, detector, backtester, fetcher, and clock objects where isolation is
needed. No test downloads live market data.

Tests are written before implementation and cover:

1. CLI default `days == 126`.
2. CLI accepts `--days 180`.
3. CLI rejects zero, negative, floating-point, text, and a missing `--days` value.
4. The evaluator reads the current, monkeypatched `followup.STRATEGIES` at call time.
5. A same-day pre-16:30 New York bar is excluded and a post-16:30 bar is retained.
6. The canonical evaluation interval contains exactly N completed sessions when enough data exists.
7. Indicator warmup rows affect indicators but not reported performance.
8. A pre-period signal suppresses an early-period signal through cooldown.
9. An unfinished position is returned as open, valued at final close, excluded from completed-trade
   win rate, and included in final sleeve and portfolio equity.
10. One primary ticker failure is reported while other strategies continue and the failed sleeve
    remains cash.
11. Known sleeve and portfolio equity paths produce exact total return, final value, utilization,
    annualized volatility, Sharpe, and maximum drawdown.
12. Same-day entries use independent equal sleeves without ordering bias.
13. An overlapping same-strategy signal is marked `skipped_insufficient_cash`.
14. A final-day signal with no next-open bar is unfilled rather than open.
15. Standard execution and EWT trailing-stop parameters are taken from each selected backtester.
16. Existing `trading followup` still uses 60 sessions and its CLI dispatch remains unchanged.
17. All-failure and partial-failure CLI exit behavior is correct.

## Documentation and Verification

Update `README.md` with command usage, accounting assumptions, metric definitions, failure behavior,
and the distinction between completed-trade statistics and mark-to-market equity metrics. Update
`CLAUDE.md` development commands and architecture overview for the new module and CLI. Do not modify
asset experiment overviews because no experiment definition or historical result is changed.

Final verification includes the focused pytest suite, the existing minimally sufficient test suite,
`uv run ruff check src/`, and `uv run ruff format --check src/`. CLI verification covers both 126-day
and 180-day modes. Live-data verification, if performed, is reported separately from deterministic
tests because network availability and the current market session are external inputs.

## Deliberate Limitations

- USD 100,000 is a normalized comparison capital amount and is not exposed as another CLI option.
- Fractional shares improve equal-weight comparability but are not a claim that Firstrade supports
  fractional execution for every selected security.
- Open positions are marked at adjusted close without hypothetical liquidation slippage.
- Pre-period open positions are not inherited; only cooldown state crosses the boundary.
- Auxiliary-data fallbacks implemented inside existing detectors remain strategy-defined behavior.
- The first successful strategy supplies the canonical calendar; this assumes the selected US-listed
  assets normally share US market sessions, with deviations explicitly warned.
