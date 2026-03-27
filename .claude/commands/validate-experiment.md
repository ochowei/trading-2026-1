Validate experiment: $ARGUMENTS

If $ARGUMENTS is empty, ask which experiment to validate. Accept either:
- Module name (e.g., `gld_007_pullback_wr_reversal`)
- Experiment ID (e.g., `GLD-007`) — look up the module name from `EXPERIMENTS_*.md` or `uv run trading list`

---

## Validation Checklist

Run ALL checks in order. Report PASS / WARN / FAIL for each.

### Check 1: Lint
```bash
uv run ruff check src/
```
**PASS** if 0 errors. If errors exist, show them and report FAIL.

### Check 2: Format
```bash
uv run ruff format --check src/
```
**PASS** if 0 files would be reformatted. If failures, show them and report FAIL.

### Check 3: Registration
```bash
uv run trading list
```
**PASS** if the experiment appears in the output. **FAIL** if missing.

### Check 4: Run backtest
```bash
uv run trading run <experiment_name>
```
**PASS** if the command completes without errors. **FAIL** if it crashes.
Capture the output — it will be needed for Checks 5 and 6.

### Check 5: Part A/B signal ratio
From the backtest output, extract signal counts for Part A and Part B.
- **PASS** if ratio is between 0.5:1 and 2.0:1
- **WARN** if ratio is between 2.0:1 and 3.0:1 (per cross_asset_lessons Section 8: ratio > 2:1 should be investigated)
- **FAIL** if ratio > 3.0:1 (strategy is likely market-state dependent)

### Check 6: Win rate sanity
From the backtest output, extract win rates for Part A and Part B.
- **PASS** if both Part A and Part B win rates > 50%
- **WARN** if Part A > 50% but Part B < 50% (possible overfit)
- **FAIL** if both < 50%

### Check 7: Documentation sync
Verify these files include the experiment:
1. The relevant `EXPERIMENTS_*.md` file (based on ticker prefix: tqqq_, gld_, sivr_, fcx_) — check for experiment ID in the experiment list table
2. `.github/workflows/tqqq-backtest.yml` — check for module name in the `options:` list

**PASS** if found in both. **FAIL** if missing from either (specify which).

### Check 8: Strategy type (execution model)
Read the experiment's `strategy.py` file at `src/trading/experiments/<module_name>/strategy.py`.
- **PASS** if it inherits from `ExecutionModelStrategy`
- **FAIL** if it inherits from `BaseStrategy` directly

Note: TQQQ-001 through TQQQ-009 are grandfathered and exempt from this check.

---

## Output

Produce a summary table:

```
## Validation Results: <experiment_name>

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Lint | PASS/FAIL | ... |
| 2 | Format | PASS/FAIL | ... |
| 3 | Registration | PASS/FAIL | ... |
| 4 | Backtest Run | PASS/FAIL | ... |
| 5 | A/B Signal Ratio | PASS/WARN/FAIL | ratio: X:1 |
| 6 | Win Rate | PASS/WARN/FAIL | A: X%, B: Y% |
| 7 | Doc Sync | PASS/FAIL | ... |
| 8 | Strategy Type | PASS/FAIL | ExecutionModelStrategy / BaseStrategy |

Overall: X/8 PASS, Y WARN, Z FAIL
```

If any check is FAIL, provide specific remediation steps for each failure.
