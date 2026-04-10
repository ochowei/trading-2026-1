Gather pre-experiment research context for asset: $ARGUMENTS

If $ARGUMENTS is empty or unclear, ask the user which asset ticker they want to research before proceeding.

## Instructions

You are preparing research context BEFORE designing a new trading experiment. This is a READ-ONLY task — do NOT create or modify any files.

Follow these steps IN ORDER. Stop early if you have enough context.

### Step 1: Read cross-asset lessons

Read `.agents/context/cross_asset_lessons.md` (精簡規則版) in full. Pay special attention to:
- **Section 10** (反覆失敗的做法 / Forbidden approaches) — these are HARD RULES
- **Section 11** (新資產實驗啟動流程 / New asset launch procedure)
- **Section 7** (波動率縮放 / Volatility scaling law)
- **Section 9** (各資產最佳策略 / Best strategy per asset)

### Step 2: Check knowledge freshness

Run `uv run trading freshness` to check if any knowledge is stale. Flag any `data_through` dates older than 6 months from today.

### Step 3: Read the relevant EXPERIMENTS_*.md

Based on the asset ticker:
- TQQQ → `src/trading/experiments/EXPERIMENTS_TQQQ.md`
- GLD → `src/trading/experiments/EXPERIMENTS_GLD.md`
- SIVR → `src/trading/experiments/EXPERIMENTS_SIVR.md`
- FCX → `src/trading/experiments/EXPERIMENTS_FCX.md`
- **New asset** → note that a new `EXPERIMENTS_<TICKER>.md` will need to be created

Read ONLY the `<!-- AI_CONTEXT_START ... AI_CONTEXT_END -->` block and the Parameter Comparison table. Do NOT read the full file unless specific experiment details are needed.

### Step 4: Determine volatility category

Based on cross_asset_lessons.md Section 11 (新資產實驗啟動流程):

| Daily Volatility | Category | Reference Template |
|-----------------|----------|-------------------|
| < 2% | LOW | GLD-007 (pullback + Williams %R + trailing stop) |
| 2% - 4% | MEDIUM | SIVR-003 (pullback + Williams %R, NO trailing stop) |
| > 4% or leveraged ETF | HIGH | TQQQ-010 (extreme panic buy, fixed exit) |
| Individual stock high beta | HIGH-BETA | FCX-001 (triple filter, wide exit) |

For new assets, estimate daily volatility from historical data or note that it needs calculation.

### Step 5: Output structured research brief

Produce a summary with ALL of these sections:

```
## Pre-Experiment Research Brief: <TICKER>

### 1. Asset Profile
- Ticker: ...
- Volatility category: LOW / MEDIUM / HIGH / HIGH-BETA
- Estimated daily volatility: ...% (vs GLD baseline ~1.2%)
- Volatility ratio to GLD: ...x

### 2. Current Best Experiment
- ID: ... (or "None — new asset")
- Strategy type: ...
- Key metrics: WR, signals/year, cumulative return

### 3. Prohibited Approaches (DO NOT attempt)
- (from cross_asset_lessons Section 10 + AI_CONTEXT "已證明無效")

### 4. Scanned Parameter Space
- (from AI_CONTEXT "已掃描的參數空間")

### 5. Unexplored Directions (可探索)
- (from AI_CONTEXT "尚未嘗試的方向")

### 6. Recommended Template & Parameter Scaling
- Base template: ...
- Scaling ratios: entry threshold ×..., TP ×..., SL ×...

### 7. Freshness Warnings
- (any stale data flagged in Step 2)

### 8. Next Experiment ID
- e.g., "GLD-008" or "NEWASSET-001"
```

## Important

- Do NOT create any files. This is research only.
- Do NOT read full experiment source code unless absolutely needed.
- Follow the CLAUDE.md reading order: cross_asset_lessons（精簡規則版）→ AI_CONTEXT → parameter table → cross_asset_evidence（特定段落）→ (only if needed) individual experiment code.
