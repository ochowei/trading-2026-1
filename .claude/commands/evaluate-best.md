Evaluate best experiment for an asset and update followup if qualified: $ARGUMENTS

If $ARGUMENTS is empty, ask which asset ticker to evaluate. Accept ticker symbols (e.g., "TQQQ", "GLD", "SPY").

---

## Step 1: Identify all experiments for this asset

```bash
uv run trading list
```

Filter experiments whose module name starts with `<ticker_lower>_` (e.g., `tqqq_`, `gld_`). Record all matching experiment names.

If no experiments exist for this asset, inform the user and stop.

---

## Step 2: Run all experiments and collect results

For each experiment found in Step 1:

```bash
uv run trading run <experiment_name>
```

This saves results to `results/<experiment_name>/latest.json`.

---

## Step 3: Compare experiments

If there are 2+ experiments, run:

```bash
uv run trading compare <exp1> <exp2> [<exp3> ...]
```

Display the full comparison output to the user.

---

## Step 4: Determine the best experiment

Read each experiment's `results/<experiment_name>/latest.json` and evaluate based on these criteria **in priority order**:

1. **Part B (Out-of-Sample) win rate > 50%** — mandatory, disqualify if not met
2. **Part B cumulative return > 0%** — mandatory, disqualify if not met
3. **Part A/B consistency** — win rate difference between Part A and Part B should be < 15 percentage points
4. **Part B cumulative return** — higher is better (primary ranking metric)
5. **Part B Sharpe ratio** — higher is better (tiebreaker)

Produce a ranking table:

```
## <TICKER> 實驗排名 (Experiment Ranking)

| 排名 | 實驗 ID | Part B WR | Part B 累計 | Part B Sharpe | A/B WR差 | 合格 |
|------|---------|-----------|-------------|---------------|----------|------|
| 1    | ...     | ...       | ...         | ...           | ...      | ✅/❌ |
```

---

## Step 5: Run gradient assessment on best experiment

Run the rolling window analysis on the best experiment identified in Step 4:

```bash
uv run trading analyze <best_experiment_name>
```

From the output, extract the **漸變性評估 (Gradual Change Assessment)** verdict section. Record:

- **預測精準度**: ✓ 漸變 or ✗ 突變 (WR max jump vs 20pp threshold)
- **下游績效**: ✓ 漸變 or ✗ 突變 (cum return max jump vs 3×σ threshold)

If the output shows "有效窗口不足 3 個" (insufficient windows), record as "窗口不足，無法評估".

---

## Step 6: Evaluate "good enough" for followup

The best experiment must meet ALL of the following thresholds to qualify for Trading Followup:

| 指標 | 門檻 | 說明 |
|------|------|------|
| Part B 勝率 | ≥ 55% | 樣本外仍具優勢 |
| Part B 累計報酬 | > 0% | 正期望值 |
| Part B 年均訊號 | ≥ 2 | 足夠的交易頻率 |
| A/B 勝率差 | < 15pp | 非過擬合 |
| 策略類型 | ExecutionModelStrategy | 有成交模型 |
| 漸變性評估 | 預測精準度或下游績效至少一項漸變 | 策略行為非隨機突變 |

**漸變性評估判定規則：**
- 預測精準度 ✓ 且下游績效 ✓ → ✅ 通過
- 預測精準度 ✗ 但下游績效 ✓ → ✅ 通過（勝/虧報酬互補，可接受）
- 預測精準度 ✓ 但下游績效 ✗ → ✅ 通過（精準度穩定，出場參數可調）
- 預測精準度 ✗ 且下游績效 ✗ → ❌ 不通過（策略行為不穩定）
- 窗口不足無法評估 → ⚠️ 警告但不阻擋（在結論中標註需人工確認）

Produce a qualification checklist:

```
## Followup 資格檢查: <TICKER>-<NNN>

| # | 檢查項目 | 結果 | 值 |
|---|---------|------|-----|
| 1 | Part B 勝率 ≥ 55% | ✅/❌ | X% |
| 2 | Part B 累計報酬 > 0% | ✅/❌ | +X% |
| 3 | Part B 年均訊號 ≥ 2 | ✅/❌ | X/year |
| 4 | A/B 勝率差 < 15pp | ✅/❌ | Xpp |
| 5 | ExecutionModelStrategy | ✅/❌ | Yes/No |
| 6 | 漸變性評估 | ✅/❌/⚠️ | 精準度:✓/✗ 績效:✓/✗ |

結論: 合格 ✅ / 不合格 ❌ / 合格(需人工確認漸變性) ⚠️
```

---

## Step 7: Update followup.py (only if qualified)

If the best experiment qualifies, check `src/trading/followup.py`:

### 7a. If asset already in STRATEGIES list
- Compare with the currently listed experiment
- If the new best is better, update the entry
- If the current entry is already the best, inform user — no change needed

### 7b. If asset not yet in STRATEGIES list
- Add a new entry to the `STRATEGIES` list in `src/trading/followup.py`:
```python
{
    "experiment_name": "<module_name>",
    "label": "<TICKER>-<NNN>",
    "ticker": "<TICKER>",
    "has_trailing_stop": True/False,  # check strategy.py for trailing stop
},
```
- Insert in alphabetical order by ticker

### 7c. If not qualified
- Inform the user which thresholds were not met
- Suggest possible next steps (e.g., "consider designing a new experiment with `/new-experiment`")
- Do NOT modify followup.py

---

## Step 8: Validation (if followup.py was modified)

```bash
uv run ruff check src/trading/followup.py
uv run ruff format --check src/trading/followup.py
```

If lint/format fails, auto-fix:
```bash
uv run ruff check src/ --fix && uv run ruff format src/
```

Then verify followup still runs:
```bash
uv run trading followup
```

---

## Step 9: Summary

```
## Evaluate Best Summary: <TICKER>

- 實驗總數: X
- 最佳實驗: <TICKER>-<NNN> (<module_name>)
- Part B 勝率: X% | 累計: +X% | Sharpe: X
- 漸變性: 精準度 ✓/✗ | 績效 ✓/✗
- Followup 資格: 合格 ✅ / 不合格 ❌
- Followup 更新: 已新增 / 已更新 / 未變更 / 不合格未加入
```
