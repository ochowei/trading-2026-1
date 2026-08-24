Rebuild the entire STRATEGIES list in followup.py by evaluating every asset: $ARGUMENTS

$ARGUMENTS is ignored — this skill always processes all assets.

---

## Step 1: Record current STRATEGIES

Read `src/trading/followup.py` and note the current STRATEGIES entries. Record each ticker and its experiment_name for later comparison in the final summary ("Changes vs Previous").

Example record format:
```
Previous STRATEGIES:
- COPX: copx_001_pullback_wr
- DIA: dia_004_wider_tp
- ...
```

---

## Step 2: Clear the STRATEGIES list

Edit `src/trading/followup.py` and replace the STRATEGIES list contents with an empty list:

```python
STRATEGIES: list[dict[str, str | bool]] = []
```

Keep everything else in the file unchanged (imports, LOOKBACK_TRADING_DAYS, functions, etc.).

---

## Step 3: Enumerate all assets with experiments

```bash
uv run trading list
```

Extract unique ticker prefixes from the experiment names. Experiment names follow the pattern `<ticker_lower>_<NNN>_<description>` (e.g., `copx_001_pullback_wr` → ticker `COPX`).

Collect all unique tickers and sort them alphabetically. Display the list:

```
## Assets to evaluate

Found X assets with experiments:
COPX, DIA, FCX, GLD, IBIT, IWM, NVDA, SIVR, SOXL, SPY, TLT, TQQQ, TSLA, TSM, URA, USO, VOO, XBI, XLU
```

---

## Step 4: Evaluate each asset

For each ticker (in alphabetical order), invoke the evaluate-best skill:

```
/evaluate-best <TICKER>
```

Use the Skill tool to invoke `evaluate-best` with the ticker as the argument.

**Important**: Process tickers **one at a time, sequentially**. Do NOT process them in parallel — each invocation may modify `src/trading/followup.py` and they must not conflict.

After each invocation completes, record the outcome:
- **Qualified**: evaluate-best added the experiment to STRATEGIES → record experiment name, Part B WR, Part B cumulative return
- **Not qualified**: evaluate-best did not add the experiment → record reason (which thresholds failed)
- **No experiments**: the asset had no experiments (handle gracefully)

Display progress after each asset:

```
Progress: X/Y assets evaluated | Qualified so far: Z
```

---

## Step 5: Final validation

After all assets have been processed:

### 5a. Lint and format check

```bash
uv run ruff check src/trading/followup.py
uv run ruff format --check src/trading/followup.py
```

If lint/format fails, auto-fix:

```bash
uv run ruff check src/ --fix && uv run ruff format src/
```

### 5b. Verify followup runs

```bash
uv run trading followup
```

### 5c. Verify STRATEGIES count

Read `src/trading/followup.py` and count the entries in the STRATEGIES list. Confirm the count matches the number of qualified assets from Step 4.

---

## Step 6: Final summary

Produce a comprehensive summary:

```
## Rebuild Followup Summary

| # | Ticker | Result | Experiment | Part B WR | Part B Cum | Notes |
|---|--------|--------|------------|-----------|------------|-------|
| 1 | COPX   | ✅ 合格 | COPX-001  | X%        | +X%        |       |
| 2 | DIA    | ❌ 不合格 | DIA-004 | X%        | +X%        | WR < 55% |
| ... | ... | ... | ... | ... | ... | ... |

### Totals
- 合格 (Qualified): X / Y assets
- 不合格 (Not qualified): X / Y assets
- STRATEGIES entries: X

### Changes vs Previous
- Added: <tickers newly added to STRATEGIES>
- Removed: <tickers that were in STRATEGIES before but no longer qualify>
- Updated: <tickers whose experiment changed to a different one>
- Unchanged: <tickers with same experiment as before>

### Validation
- Lint: ✅ PASS / ❌ FAIL
- Format: ✅ PASS / ❌ FAIL
- Followup run: ✅ PASS / ❌ FAIL
```
