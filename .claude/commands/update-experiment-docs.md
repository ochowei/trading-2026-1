Update experiment documentation with actual results: $ARGUMENTS

If $ARGUMENTS is empty, ask which experiment to update. Pass `all` to update all experiments that have results.

---

## Instructions

### Step 1: Read results

Read `results/<experiment_name>/latest.json` to get the actual backtest results.

If the file does not exist, inform the user they need to run the experiment first:
```bash
uv run trading run <experiment_name>
```

### Step 2: Identify target EXPERIMENTS_*.md

Based on the experiment prefix:
- `tqqq_*` → `src/trading/experiments/EXPERIMENTS_TQQQ.md`
- `gld_*` → `src/trading/experiments/EXPERIMENTS_GLD.md`
- `sivr_*` → `src/trading/experiments/EXPERIMENTS_SIVR.md`
- `fcx_*` → `src/trading/experiments/EXPERIMENTS_FCX.md`

### Step 3: Update results tables

Find the Part A, Part B, and Part C results sections in the EXPERIMENTS_*.md file. Update the row for this experiment with values from `latest.json`:

| Field in JSON | Column in Markdown |
|--------------|-------------------|
| `total_signals` | 訊號數 |
| (calculate: signals / years) | 年均訊號 |
| `win_rate` | 勝率 (as %) |
| `avg_return_pct` | 平均報酬 (as %) |
| `cumulative_return_pct` | 累計報酬 (as %) |
| `avg_holding_days` | 平均持倉 |
| `max_drawdown_pct` | 最大回撤 (as %) |
| `max_consecutive_losses` | 最大連續虧損 |

Match the existing table format exactly — different EXPERIMENTS_*.md files may have slightly different column structures.

### Step 4: Update AI_CONTEXT block

Read the `<!-- AI_CONTEXT_START ... AI_CONTEXT_END -->` block and update:

1. **當前最佳**: If this experiment beats the current best (by cumulative return with acceptable win rate in both Part A and Part B), update to this experiment
2. **已證明無效**: If the experiment performed poorly (negative cumulative return, or WR < 50%), add to this list with a brief explanation
3. **已掃描的參數空間**: If new parameter values were tested, add them to the scanned range
4. **尚未嘗試的方向**: Remove any directions that this experiment has now explored
5. Update `last_validated` to today's date
6. Update `data_through` if the data range has changed

### Step 5: Update cross_asset_lessons.md (if applicable)

Only update `.agents/context/cross_asset_lessons.md` if the experiment results reveal:
- A **new** cross-asset lesson (novel finding not covered by existing lessons)
- A **contradiction** to an existing lesson (requires updating the lesson)
- A **confirmation** of an existing lesson (update `derived_from` and `validated` date)

If no new lessons, skip this step.

### Step 6: Update freshness dates

Ensure all modified files have current dates:
- `last_validated` in AI_CONTEXT blocks → today's date
- `validated` in cross_asset_lessons.md freshness blocks → today's date (if modified)

### Step 7: Verify with sync-docs

```bash
uv run trading sync-docs
```

Check that the updated markdown tables match the latest.json values.

---

## Rules

- **NEVER fabricate results** — only use values from `latest.json`
- **ALWAYS preserve** the existing markdown table format (don't restructure tables)
- **ALWAYS update** the AI_CONTEXT block when updating results
- Use the same date format as existing entries: `YYYY-MM-DD`
- Use the same number formatting as existing entries (e.g., `+7.23%`, `-2.05%`)
