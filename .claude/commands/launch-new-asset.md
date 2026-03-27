Launch first experiment for a brand new asset: $ARGUMENTS

Expected format: `<TICKER> <brief_strategy_description>` (e.g., "SLV pullback_wr" or "COPX extreme_oversold").
If $ARGUMENTS is unclear, ask for the asset ticker and a brief strategy concept before proceeding.

---

## Phase 0: Pre-flight Validation (MANDATORY — do NOT skip)

### 0a. Confirm this is truly a new asset
Check that NO existing experiment directory matches this ticker:
```bash
ls src/trading/experiments/ | grep -i "^<ticker_lower>_"
```
Also check that NO `EXPERIMENTS_<TICKER>.md` file exists:
```bash
ls src/trading/experiments/EXPERIMENTS_<TICKER>.md
```

**If either exists, STOP. This asset already has experiments. Use `/new-experiment` instead.**

### 0b. Read cross-asset lessons
- Read `.agents/context/cross_asset_lessons.md` — especially:
  - **Section 10** (反覆失敗的做法 / Forbidden approaches) — these are HARD RULES
  - **Section 11** (新資產實驗啟動流程 / New asset launch procedure)
  - **Section 7** (波動度縮放法則 / Volatility scaling law)
  - **Section 9** (各資產最佳策略速覽 / Best strategy per asset)

### 0c. Check knowledge freshness
```bash
uv run trading freshness
```
Flag any `data_through` dates older than 6 months from today. If stale, note in output: 「基於較舊數據，建議先重新驗證」

### 0d. Verify proposal is not prohibited
Check the proposed strategy does NOT violate any item in cross_asset_lessons.md Section 10:
1. 放寬進場門檻以增加訊號
2. 高波動資產上使用 trailing stop
3. 均值回歸策略加趨勢方向濾波
4. 已精確訊號上疊加確認指標
5. 無成交模型的 In-Sample 數字當參考
6. 不同波動度資產直接複製參數

**If the proposal violates a prohibition, STOP and explain why. Suggest alternatives instead.**

---

## Phase 1: Volatility Analysis & Template Selection (MANDATORY)

### 1a. Download historical data and calculate daily volatility

Write and run a Python script to calculate the asset's volatility:

```python
import yfinance as yf
import numpy as np

ticker = "<TICKER>"
data = yf.download(ticker, period="5y", progress=False)
daily_returns = data["Close"].pct_change().dropna()
daily_vol = daily_returns.std() * 100  # as percentage
gld_data = yf.download("GLD", period="5y", progress=False)
gld_vol = gld_data["Close"].pct_change().dropna().std() * 100
vol_ratio = daily_vol / gld_vol

print(f"=== Volatility Analysis: {ticker} ===")
print(f"Daily volatility: {daily_vol:.2f}%")
print(f"GLD daily volatility: {gld_vol:.2f}%")
print(f"Volatility ratio to GLD: {vol_ratio:.2f}x")
print(f"Annualized volatility: {daily_vol * np.sqrt(252):.1f}%")
print(f"Data points: {len(daily_returns)}")
```

**Record the results — they determine everything below.**

### 1b. Determine asset type
Classify the asset:
- **ETF**: slippage = 0.1% (0.001)
- **Individual stock**: slippage = 0.15% (0.0015)
- **Leveraged ETF**: slippage = 0.1%, but treat as HIGH volatility regardless of calculated value

### 1c. Select strategy template based on volatility

| Daily Volatility | Category | Template | Key Characteristics |
|-----------------|----------|----------|-------------------|
| < 2% | LOW | GLD-007 (`gld_007_pullback_wr_reversal`) | Pullback + Williams %R + trailing stop |
| 2-4% | MEDIUM | SIVR-003 (`sivr_003_pullback_wr`) | Pullback + Williams %R, NO trailing stop |
| > 4% or leveraged ETF | HIGH | TQQQ-010 (`tqqq_010_cap_exec_optimized`) | Extreme panic buy, fixed exit |
| Individual stock high beta | HIGH-BETA | FCX-001 (`fcx_001_extreme_oversold`) | Triple filter, wide exit |

**Read the source code** of the selected template (all 4 files: `__init__.py`, `config.py`, `signal_detector.py`, `strategy.py`) as implementation reference.

### 1d. Calculate scaled parameters

Using the volatility ratio from 1a and the scaling law from cross_asset_lessons Section 7:

| Parameter | Base (from template) | Scaling Factor | New Value |
|-----------|---------------------|---------------|-----------|
| Entry threshold (pullback/drawdown) | template value | ~1.5-2.3x per vol ratio | calculate |
| SMA deviation (if applicable) | template value | ~1.7x per vol ratio | calculate |
| Profit target | template value | ~2x per vol ratio | calculate |
| Stop loss | template value | ~1.5x per vol ratio | calculate |
| Holding days | template value | ~0.75x per vol ratio (higher vol = faster reversion) | calculate |
| Cooldown | template value | ~1.4x per vol ratio | calculate |

**Show the calculation table to the user and confirm before proceeding.**

### 1e. Determine naming convention
Auto-calculate:
- **Experiment number**: always `001` (first experiment for this asset)
- **Module name**: `<ticker_lower>_001_<strategy_name>` (e.g., `slv_001_pullback_wr`)
- **Experiment ID**: `<TICKER>-001` (e.g., `SLV-001`)
- **Directory path**: `src/trading/experiments/<module_name>/`

---

## Phase 2: Create 4 Code Files

Create directory: `src/trading/experiments/<module_name>/`

### File 1: `__init__.py`
Follow the pattern from the selected template experiment:
```python
"""<Display Name> (<Experiment ID>)"""

from trading.experiments import register
from trading.experiments.<module_name>.strategy import <StrategyClass>

register("<module_name>")(<StrategyClass>)
```

### File 2: `config.py`
- Create a dataclass inheriting from `ExperimentConfig` (from `trading.core.base_config`)
- Add strategy-specific parameters copied from the template, with values scaled per Phase 1d
- Implement `create_default_config()` factory function
- Set `name`, `experiment_id`, `display_name`, `tickers`, `data_start`
- `data_start` should be at least 5 years before Part A start (typically `"2018-01-01"` or `"2010-01-01"` for indicators needing long lookback)
- Set `profit_target`, `stop_loss`, `holding_days` per Phase 1d scaled values
- If LOW volatility template (GLD-007): include `trail_activation_pct` and `trail_distance_pct` parameters
- If HIGH-BETA template (FCX-001): include `drawdown_lookback`, `rsi_period`, `rsi_threshold`, `sma_period`, `sma_deviation_threshold`

### File 3: `signal_detector.py`
- Create a class inheriting from `BaseSignalDetector` (from `trading.core.base_signal_detector`)
- Copy the signal detection logic from the template, adapting class names and parameter references
- Implement `compute_indicators(df)` — compute technical indicators on full data (do NOT drop rows)
- Implement `detect_signals(df)` — add boolean `Signal` column with entry conditions
- **MUST include cooldown logic** (suppress signals within N days of previous signal) — copy the pattern from the template
- Use `logging` module for signal count reporting: `logger.info(f"<TICKER>: Detected {signal_count} signals")`
- If the template includes helper methods (e.g., `_compute_rsi`, `_compute_williams_r`), copy them

### File 4: `strategy.py`
- **MANDATORY**: Inherit from `ExecutionModelStrategy` (from `trading.core.execution_strategy`), NOT BaseStrategy
- Implement `create_config()` returning your config
- Implement `create_detector()` returning your detector
- Override `_print_strategy_params(config)` to display strategy-specific parameters (follow template pattern)
- Set `slippage_pct`:
  - ETFs: `0.001` (0.1%)
  - Individual stocks: `0.0015` (0.15%)
- Override `create_backtester()` ONLY if using trailing stop (LOW volatility template)

---

## Phase 3: Create EXPERIMENTS_<TICKER>.md (NEW ASSET — MANDATORY)

Create `src/trading/experiments/EXPERIMENTS_<TICKER>.md` using EXPERIMENTS_FCX.md as the structural template.

The file MUST contain ALL of the following sections:

### Section 1: AI_CONTEXT block (at the very top)
```markdown
<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: <today's date YYYY-MM-DD>
  data_through: <latest data date, typically end of last full year>
-->
## AI Agent 快速索引

**當前最佳：** <TICKER>-001（<brief strategy description in Chinese>）

**已證明無效（禁止重複嘗試）：**
- 尚無（目前僅完成基礎版本）

**已掃描的參數空間：**
- 進場條件：<describe initial parameter choice and rationale>
- 出場參數：<describe TP/SL/holding chosen and why>

**尚未嘗試的方向（可探索）：**
- <direction 1 — e.g., alternative entry confirmation>
- <direction 2 — e.g., trailing stop if not used, or tighter entry if used>
- <direction 3 — e.g., correlated asset confirmation>

**關鍵資產特性：**
- <characteristic 1 — e.g., volatility level and comparison>
- <characteristic 2 — e.g., liquidity, sector, cycle behavior>
- <characteristic 3 — e.g., relevant correlations>
<!-- AI_CONTEXT_END -->
```

### Section 2: Asset header and characteristics
```markdown
# <TICKER> 實驗總覽 (<TICKER> Experiments Overview)

## 標的特性 (Asset Characteristics)

- **<TICKER> (<Full Name>)**：<brief description>
- 日均波動約 <X>%，<comparison to GLD>
- <other relevant characteristics from Phase 1 research>
```

### Section 3: Experiment list table
```markdown
## 實驗列表 (Experiment List)

| ID      | 資料夾                     | 策略摘要                    | 狀態  |
|---------|---------------------------|----------------------------|-------|
| <TICKER>-001 | `<module_name>` | <strategy summary in Chinese> | 🔄 待執行 |
```

### Section 4: Experiment detail section
Include ALL of these subsections (follow FCX-001's structure exactly):
- 目標 (Goal)
- 進場條件 (Entry conditions) — table format with 條件/指標/閾值/說明
- 出場參數 (Exit parameters) — table format with 參數/值/說明
- 成交模型 (Execution model) — table format with 項目/設定
- 設計理念 (Design rationale) — bullet points explaining each design choice
- 回測結果 (Backtest results) — table with `🔄 待執行` placeholders for Part A/B/C

### Section 5: Evolution roadmap
```markdown
## 演進路線圖 (Roadmap)

<TICKER>-001 (<brief description>)
  ├── <TICKER>-002 (<potential direction 1>)
  ├── <TICKER>-003 (<potential direction 2>)
  └── <TICKER>-004 (<potential direction 3>)
```

---

## Phase 4: Update Existing Files (MANDATORY checklist)

### Update 1: `CLAUDE.md` — 按需參考 section
Add a new link to the "按需參考" section:
```markdown
- <TICKER> 實驗總覽 → [src/trading/experiments/EXPERIMENTS_<TICKER>.md](src/trading/experiments/EXPERIMENTS_<TICKER>.md)
```
Insert in alphabetical order among the existing experiment links.

### Update 2: `CLAUDE.md` — 規則 section
In the "新增實驗時" rule, add `EXPERIMENTS_<TICKER>.md` to the file list if the rule only lists specific filenames.

### Update 3: `.github/workflows/tqqq-backtest.yml`
Add the new experiment option to the `options:` list:
```yaml
- "<TICKER>-001: <module_name>"
```
Insert in the correct position (sorted by asset alphabetically, then by number).

---

## Phase 5: Validation (MANDATORY)

### 5a. Lint and format
```bash
# Lint (must be 0 errors)
uv run ruff check src/

# Format (must be 0 reformats)
uv run ruff format --check src/

# If either fails, auto-fix:
uv run ruff check src/ --fix && uv run ruff format src/
```

### 5b. Verify registration
```bash
uv run trading list
```
Confirm `<module_name>` appears in the output.

### 5c. Run backtest
```bash
uv run trading run <module_name>
```
The backtest MUST complete without errors.

### 5d. Check A/B signal balance
From the backtest output, extract signal counts for Part A and Part B:
- **OK** if ratio is between 0.5:1 and 2.0:1
- **WARNING** if ratio is between 2.0:1 and 3.0:1 — investigate
- **FAIL** if ratio > 3.0:1 — strategy likely has market-state dependency, needs redesign

### 5e. Check win rates
- **OK** if both Part A and Part B win rates > 50%
- **WARNING** if Part A > 50% but Part B < 50% (possible overfit)
- **FAIL** if both < 50% — strategy is not viable

### 5f. Produce validation summary
```
## Validation: <TICKER>-001 (<module_name>)

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Lint | PASS/FAIL | ... |
| 2 | Format | PASS/FAIL | ... |
| 3 | Registration | PASS/FAIL | ... |
| 4 | Backtest Run | PASS/FAIL | ... |
| 5 | A/B Signal Ratio | OK/WARN/FAIL | ratio: X:1 |
| 6 | Win Rate | OK/WARN/FAIL | A: X%, B: Y% |
| 7 | EXPERIMENTS_<TICKER>.md exists | PASS/FAIL | ... |
| 8 | CLAUDE.md updated | PASS/FAIL | ... |
| 9 | Workflow updated | PASS/FAIL | ... |
| 10 | Strategy inherits ExecutionModelStrategy | PASS/FAIL | ... |

Overall: X/10 PASS
```

### 5g. If backtest succeeds, update documentation with results
Update `EXPERIMENTS_<TICKER>.md`:
- Fill in the 回測結果 table with actual Part A/B/C values from the backtest output
- Update AI_CONTEXT "已掃描的參數空間" with the actual parameter values tested
- Change experiment status from `🔄 待執行` to `已完成` in the experiment list table

---

## Phase 6: Final Summary

Present a summary to the user:

```
## New Asset Launch Complete: <TICKER>-001

### Asset Profile
- Ticker: <TICKER>
- Daily volatility: <X>% (GLD ratio: <Y>x)
- Category: LOW / MEDIUM / HIGH / HIGH-BETA
- Template used: <template experiment ID>

### Files Created
1. src/trading/experiments/<module_name>/__init__.py
2. src/trading/experiments/<module_name>/config.py
3. src/trading/experiments/<module_name>/signal_detector.py
4. src/trading/experiments/<module_name>/strategy.py
5. src/trading/experiments/EXPERIMENTS_<TICKER>.md

### Files Updated
6. CLAUDE.md (按需參考 + 規則 sections)
7. .github/workflows/tqqq-backtest.yml (new option added)

### Backtest Highlights
- Part A: X signals (Y/year), WR Z%, cumulative +/-X%
- Part B: X signals (Y/year), WR Z%, cumulative +/-X%
- A/B ratio: X:1

### Next Steps
- Review results and iterate entry parameters if needed (use `/new-experiment`)
- Consider directions listed in EXPERIMENTS_<TICKER>.md roadmap
```

---

## Code Style Reminders (from CLAUDE.md)

- No unnecessary f-strings (if no `{}` placeholder, don't use `f""`)
- No unused imports or variables
- Import order: stdlib → third-party → local, blank line between groups
- Use Python 3.11+ syntax (`X | Y` not `Optional[X]`)
- Bilingual docstrings following existing convention: `"""中文描述\nEnglish description"""`
