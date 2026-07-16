# Followup Backtest Start Date Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional `--start YYYY-MM-DD` anchor so followup backtests can run N completed trading sessions beginning on or after a requested date.

**Architecture:** Keep the CLI responsible only for strict input parsing and dispatch. Add date normalization and canonical calendar selection to `followup_backtest.py`, leaving indicator computation, execution models, sleeve accounting, and portfolio metrics unchanged. Return the requested start in the structured result and render it separately from the actual period.

**Tech Stack:** Python 3.11+, argparse, pandas, pytest, Ruff.

## Global Constraints

- `--days` remains a positive integer with default 126 and always means completed trading sessions.
- Omitting `--start` preserves the current last-N-session behavior.
- A non-session start advances to the first completed canonical session on or after that date.
- Indicators and cooldown state are computed on full history before the anchored evaluation slice.
- Do not change portfolio allocation or any experiment execution model.
- Do not modify any file under `pm/`.
- Do not commit, push, or create a PR.

---

### Task 1: Strict CLI Start-Date Parsing and Dispatch

**Files:**
- Modify: `tests/test_followup_backtest_cli.py`
- Modify: `src/trading/cli.py`

**Interfaces:**
- Produces: `iso_date(value: str) -> datetime.date`
- Produces: `args.start: datetime.date | None`
- Consumes: `run_followup_backtest(days: int, start: object | None)` from Task 2

- [ ] **Step 1: Write failing parser tests**

Add tests that establish the public CLI contract:

```python
from datetime import date

def test_followup_backtest_start_defaults_to_none() -> None:
    args = build_parser().parse_args(["followup-backtest"])
    assert args.start is None

def test_followup_backtest_accepts_iso_start_date() -> None:
    args = build_parser().parse_args(
        ["followup-backtest", "--start", "2025-01-01", "--days", "20"]
    )
    assert args.start == date(2025, 1, 1)
    assert args.days == 20

@pytest.mark.parametrize("value", ["2025/01/01", "20250101", "2025-02-30", "not-a-date"])
def test_followup_backtest_rejects_invalid_start_date(value: str) -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(["followup-backtest", "--start", value])
    assert exc_info.value.code == 2
```

Update the dispatch test to prove both values cross the CLI boundary:

```python
def test_cli_dispatch_passes_days_and_start(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(days: int, start: date | None) -> FollowupBacktestResult:
        captured.update(days=days, start=start)
        return _minimal_result(days)

    monkeypatch.setattr("trading.followup_backtest.run_followup_backtest", fake_run)
    monkeypatch.setattr(
        "trading.followup_backtest.render_followup_backtest", lambda result: None
    )
    from trading.cli import main

    main(["followup-backtest", "--days", "180", "--start", "2025-01-01"])
    assert captured == {"days": 180, "start": date(2025, 1, 1)}
```

- [ ] **Step 2: Run the CLI tests and verify RED**

Run:

```bash
uv run pytest tests/test_followup_backtest_cli.py -q
```

Expected: failures because `--start` is unrecognized and dispatch does not pass it.

- [ ] **Step 3: Add minimal CLI implementation**

In `src/trading/cli.py`:

```python
from datetime import date

def iso_date(value: str) -> date:
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "must be a date in YYYY-MM-DD format"
        ) from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("must be a date in YYYY-MM-DD format")
    return parsed
```

Register `--start` on the existing subparser and dispatch with:

```python
result = run_followup_backtest(days=args.days, start=args.start)
```

Treat `result.portfolio is None` as an unsuccessful CLI calculation so a future/no-session anchor exits nonzero.

- [ ] **Step 4: Run CLI tests and verify GREEN**

Run the same pytest command. Expected: all CLI tests pass.

---

### Task 2: Anchored Canonical Calendar and Structured Result

**Files:**
- Modify: `tests/test_followup_backtest_data.py`
- Modify: `src/trading/followup_backtest.py`

**Interfaces:**
- Produces: `_normalize_start(start: date | datetime | pd.Timestamp | str | None) -> pd.Timestamp | None`
- Produces: anchored `run_followup_backtest(..., start=...)`
- Produces: `FollowupBacktestResult.requested_start: pd.Timestamp | None`

- [ ] **Step 1: Write failing anchored-calendar tests**

Use `FakeFetcher` and `make_ohlcv` to cover:

```python
def test_start_on_session_selects_first_n_sessions(make_ohlcv) -> None:
    frame = make_ohlcv(10)
    FakeFetcher.frames = {"AAA": frame}
    result = run_followup_backtest(
        days=3,
        start=frame.index[2],
        strategy_definitions=[definition("alpha", "AAA")],
        get_experiment_fn=lambda name: FakeStrategy("AAA"),
        fetcher_factory=FakeFetcher,
    )
    assert result.calendar == tuple(frame.index[2:5])
    assert result.requested_start == frame.index[2]
```

Add the remaining boundary and state tests:

```python
def test_weekend_start_advances_to_next_session(make_ohlcv) -> None:
    frame = make_ohlcv(6, start="2025-01-02")
    FakeFetcher.frames = {"AAA": frame}
    result = run_followup_backtest(
        days=2,
        start="2025-01-04",
        strategy_definitions=[definition("alpha", "AAA")],
        get_experiment_fn=lambda name: FakeStrategy("AAA"),
        fetcher_factory=FakeFetcher,
    )
    assert result.calendar == tuple(frame.index[2:4])

def test_anchored_period_warns_when_fewer_than_n_sessions_remain(make_ohlcv) -> None:
    frame = make_ohlcv(6)
    FakeFetcher.frames = {"AAA": frame}
    result = run_followup_backtest(
        days=5,
        start=frame.index[-2],
        strategy_definitions=[definition("alpha", "AAA")],
        get_experiment_fn=lambda name: FakeStrategy("AAA"),
        fetcher_factory=FakeFetcher,
    )
    assert result.calendar == tuple(frame.index[-2:])
    assert any("Requested 5" in warning and "available 2" in warning for warning in result.warnings)

def test_start_before_available_history_warns_and_uses_earliest_session(make_ohlcv) -> None:
    frame = make_ohlcv(5)
    FakeFetcher.frames = {"AAA": frame}
    result = run_followup_backtest(
        days=2,
        start="2024-12-01",
        strategy_definitions=[definition("alpha", "AAA")],
        get_experiment_fn=lambda name: FakeStrategy("AAA"),
        fetcher_factory=FakeFetcher,
    )
    assert result.calendar == tuple(frame.index[:2])
    assert any("earliest available" in warning for warning in result.warnings)

def test_start_after_last_session_returns_no_portfolio(make_ohlcv) -> None:
    FakeFetcher.frames = {"AAA": make_ohlcv(5)}
    result = run_followup_backtest(
        days=2,
        start="2025-02-01",
        strategy_definitions=[definition("alpha", "AAA")],
        get_experiment_fn=lambda name: FakeStrategy("AAA"),
        fetcher_factory=FakeFetcher,
    )
    assert result.calendar == ()
    assert result.portfolio is None
    assert any("after the last available" in warning for warning in result.warnings)

def test_anchored_cooldown_is_computed_before_slice(make_ohlcv) -> None:
    frame = make_ohlcv(8)
    frame["RawSignal"] = [False, False, False, True, False, True, False, False]
    FakeFetcher.frames = {"AAA": frame}
    result = run_followup_backtest(
        days=4,
        start=frame.index[4],
        strategy_definitions=[definition("alpha", "AAA")],
        get_experiment_fn=lambda name: FakeStrategy("AAA", FakeDetector(cooldown_days=3)),
        fetcher_factory=FakeFetcher,
    )
    assert result.strategies[0].signal_count == 0
    assert result.strategies[0].warmup_rows == 4

def test_direct_call_rejects_invalid_start() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        run_followup_backtest(start="20250101", strategy_definitions=[])
```

- [ ] **Step 2: Run data tests and verify RED**

Run:

```bash
uv run pytest tests/test_followup_backtest_data.py -q
```

Expected: `run_followup_backtest()` rejects the unknown `start` argument or assertions fail because anchored selection is absent.

- [ ] **Step 3: Implement normalization and calendar selection**

Add a strict normalizer that converts supported values to a timezone-naive, date-normalized `pd.Timestamp`. For strings, require `date.fromisoformat(value).isoformat() == value`; reject `NaT`, unsupported types, malformed strings, and impossible dates with `ValueError("start must be a date in YYYY-MM-DD format")`.

Add `start` to `run_followup_backtest`, normalize it once, and replace the current single selection expression with:

```python
if requested_start is None:
    selected_dates = available_dates[-days:]
else:
    eligible_dates = [
        value
        for value in available_dates
        if pd.Timestamp(value).tz_localize(None).normalize() >= requested_start
    ]
    selected_dates = eligible_dates[:days]
calendar = tuple(pd.Timestamp(value) for value in selected_dates)
```

Before indexing `calendar[0]`, handle an empty anchored selection by returning strategy metadata, an empty calendar, `portfolio=None`, the normalized requested start, and a warning naming the requested start and final available session.

Warn when the requested start precedes the earliest canonical session. Retain the existing insufficient-session warning, adding the requested start to its anchored form.

Add `requested_start` as a backward-compatible optional field at the end of `FollowupBacktestResult` and use keyword construction for new/changed return sites.

- [ ] **Step 4: Run data tests and verify GREEN**

Run the same data-test command. Expected: all data tests pass.

- [ ] **Step 5: Run CLI and ledger regression tests**

Run:

```bash
uv run pytest tests/test_followup_backtest_cli.py tests/test_followup_backtest_ledger.py tests/test_execution_open_positions.py -q
```

Expected: all pass; no portfolio or execution behavior changes.

---

### Task 3: Report Rendering and Documentation

**Files:**
- Modify: `tests/test_followup_backtest_cli.py`
- Modify: `src/trading/followup_backtest.py`
- Modify: `README.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: `FollowupBacktestResult.requested_start`
- Produces: human-readable `Requested start: YYYY-MM-DD` report line

- [ ] **Step 1: Write failing renderer test**

Construct a result with `requested_start=pd.Timestamp("2025-01-01")`, render to `StringIO`, and assert:

```python
assert "Requested start: 2025-01-01" in output.getvalue()
assert "Actual period:" in output.getvalue()
```

- [ ] **Step 2: Run renderer test and verify RED**

Run:

```bash
uv run pytest tests/test_followup_backtest_cli.py -q
```

Expected: failure because the requested start is not rendered.

- [ ] **Step 3: Add renderer output and documentation**

Print the requested-start line only when it is non-null. Update README and CLAUDE command examples with:

```bash
uv run trading followup-backtest --start 2025-01-01 --days 126
```

Document that non-session dates advance to the next completed trading session and insufficient tail data produces a warning.

- [ ] **Step 4: Run renderer tests and verify GREEN**

Run the same CLI-test command. Expected: all pass.

---

### Task 4: Full Verification and Scope Audit

**Files:**
- Verify all modified source, tests, docs, and the design/plan documents.

- [ ] **Step 1: Run the complete fixed-fixture suite**

```bash
uv run pytest tests -q
```

Expected: all tests pass without network access.

- [ ] **Step 2: Run required lint and formatting checks**

```bash
uv run ruff check src/
uv run ruff format --check src/
```

Expected: both commands exit 0.

- [ ] **Step 3: Exercise CLI validation and help**

```bash
uv run trading followup-backtest --help
uv run trading followup-backtest --start 2025-02-30
```

Expected: help lists `--start`; invalid date exits 2 with the ISO-date error.

- [ ] **Step 4: Run representative live commands if network access is available**

```bash
uv run trading followup-backtest --start 2026-01-03 --days 5
uv run trading followup-backtest --days 5
```

Expected: anchored mode begins on the first completed session on or after January 3; unanchored mode uses the most recent five completed sessions.

- [ ] **Step 5: Audit final diff**

```bash
git diff --check
git status --short
git diff --name-only
```

Expected: no `pm/` paths, no whitespace errors, and no commit/push/PR action.
