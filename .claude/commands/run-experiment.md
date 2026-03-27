Run experiment and summarize results: $ARGUMENTS

If $ARGUMENTS is empty, ask which experiment to run. Accept either:
- Module name (e.g., `gld_007_pullback_wr_reversal`)
- Experiment ID (e.g., `GLD-007`) — look up the module name from `uv run trading list`

---

## Step 1: Run the experiment

```bash
uv run trading run <experiment_name>
```

Display the full output to the user.

## Step 2: Read and summarize results

Read `results/<experiment_name>/latest.json` and produce a concise summary:

```
## Results Summary: <experiment_name> (<experiment_id>)

### Part A (In-Sample: 2019-2023)
- Signals: X (Y/year) | Win Rate: Z% | Cumulative Return: +/-X%
- Avg Return: X% | Max Drawdown: X% | Max Consecutive Losses: X

### Part B (Out-of-Sample: 2024-2025)
- Signals: X (Y/year) | Win Rate: Z% | Cumulative Return: +/-X%
- Avg Return: X% | Max Drawdown: X% | Max Consecutive Losses: X

### Part C (Live: 2026+)
- Signals: X | Win Rate: Z% | Cumulative Return: +/-X%
(or "No signals yet" if empty)

### Health Checks
- A/B Signal Ratio: X:1 (OK / WARNING if > 2:1)
- A/B Win Rate Consistency: A=X%, B=Y% (OK / WARNING if divergent)
- Execution Model: Yes/No (WARNING if No for non-grandfathered experiment)
```

## Step 3: Offer documentation update

After showing the summary, ask:

> "要更新 EXPERIMENTS_*.md 的結果表格嗎？(Update documentation with these results? y/n)"

If the user says yes, follow the full procedure from `/update-experiment-docs` for this experiment:
1. Update results tables in EXPERIMENTS_*.md
2. Update AI_CONTEXT block
3. Update freshness dates
4. Run `uv run trading sync-docs` to verify
