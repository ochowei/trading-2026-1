Create a new trading experiment: $ARGUMENTS

Expected format: `<TICKER> <brief_strategy_description>` (e.g., "GLD bollinger_squeeze" or "TQQQ volume_climax").
If $ARGUMENTS is unclear, ask for the asset ticker and strategy concept before proceeding.

---

## Phase 1: Pre-flight (MANDATORY — do NOT skip)

### 1a. Read context
- Read `.agents/context/cross_asset_lessons.md` — especially Section 10 (禁止事項) and Section 11 (新資產啟動流程)
- Read the relevant `EXPERIMENTS_*.md` AI_CONTEXT block to find the **next experiment number** and what has already been tried/failed

### 1b. Verify proposal is not prohibited
Check the proposed strategy does NOT violate any item in:
- cross_asset_lessons.md Section 10 (反覆失敗的做法)
- EXPERIMENTS_*.md AI_CONTEXT "已證明無效" list

**If the proposal violates a prohibition, STOP and explain why. Suggest alternatives instead.**

### 1c. Determine experiment parameters
Auto-calculate:
- **Experiment number**: highest existing number for this asset + 1
- **Module name**: `<ticker_lower>_<NNN>_<strategy_name>` (e.g., `gld_008_bollinger_squeeze`)
- **Experiment ID**: `<TICKER>-<NNN>` (e.g., `GLD-008`)
- **Volatility category**: per cross_asset_lessons Section 11
- **Reference experiment**: Read the source code of the most relevant existing experiment (e.g., FCX-001, GLD-007, TQQQ-010) as a pattern reference

---

## Phase 2: Create 4 code files

Create directory: `src/trading/experiments/<module_name>/`

### File 1: `__init__.py`
Follow the pattern from existing experiments (e.g., `fcx_001_extreme_oversold/__init__.py`):
```python
"""<Display Name> (<Experiment ID>)"""

from trading.experiments import register
from trading.experiments.<module_name>.strategy import <StrategyClass>

register("<module_name>")(<StrategyClass>)
```

### File 2: `config.py`
- Create a dataclass inheriting from `ExperimentConfig` (from `trading.core.base_config`)
- Add strategy-specific parameters (RSI threshold, drawdown lookback, cooldown days, etc.)
- Implement `create_default_config()` factory function
- Set `name`, `experiment_id`, `display_name`, `tickers`, `data_start`
- **Scale parameters** based on volatility category (cross_asset_lessons Section 7):
  - If new asset is Nx volatility of GLD: scale entry thresholds ~(1.5-2)x per Nx
- Set appropriate `profit_target`, `stop_loss`, `holding_days`

### File 3: `signal_detector.py`
- Create a class inheriting from `BaseSignalDetector` (from `trading.core.base_signal_detector`)
- Implement `compute_indicators(df)` — compute technical indicators on full data (do NOT drop rows)
- Implement `detect_signals(df)` — add boolean `Signal` column with entry conditions
- Include **cooldown logic** (suppress signals within N days of previous signal)
- Use `logging` module for signal count reporting

### File 4: `strategy.py`
- **MANDATORY**: Inherit from `ExecutionModelStrategy` (from `trading.core.execution_strategy`), NOT BaseStrategy
- Implement `create_config()` returning your config
- Implement `create_detector()` returning your detector
- Override `_print_strategy_params(config)` to display strategy-specific parameters
- Set `slippage_pct`:
  - ETFs: `0.001` (0.1%)
  - Individual stocks: `0.0015` (0.15%)
- Override `create_backtester()` ONLY if using trailing stop or custom exit logic

---

## Phase 3: Update documentation (MANDATORY checklist)

### Update 1: `EXPERIMENTS_*.md`
Based on asset ticker, update the corresponding file:
- Add row to **實驗清單** (experiment list) table
- Add entry to **演進路線** (evolution/lineage) section
- Add column to **參數對照表** (parameter comparison) table
- Add placeholder rows in **Part A/B/C 結果** (results) tables with `🔄 待執行` status
- Update **AI_CONTEXT** block: add to "已掃描的參數空間" if testing new parameters

### Update 2: `.github/workflows/tqqq-backtest.yml`
Add a new option to the `options:` list under `workflow_dispatch.inputs.experiment`:
```yaml
- "<TICKER>-<NNN>: <module_name>"
```
Insert in the correct position (sorted by asset, then by number).

### Update 3: New asset only
If this is the FIRST experiment for a new asset:
- Create `src/trading/experiments/EXPERIMENTS_<TICKER>.md` with full AI_CONTEXT block (follow EXPERIMENTS_FCX.md as template)
- Update `CLAUDE.md` "按需參考" section to add link to new EXPERIMENTS file
- Update `CLAUDE.md` "架構速覽" if directory structure changed

---

## Phase 4: Validation (MANDATORY)

Run these checks and ensure all pass:

```bash
# Lint (must be 0 errors)
uv run ruff check src/

# Format (must be 0 reformats)
uv run ruff format --check src/

# If either fails, auto-fix:
uv run ruff check src/ --fix && uv run ruff format src/

# Verify registration
uv run trading list
```

Confirm the new experiment appears in the `trading list` output.

---

## Code Style Reminders (from CLAUDE.md)

- No unnecessary f-strings (if no `{}` placeholder, don't use `f""`)
- No unused imports or variables
- Import order: stdlib → third-party → local, blank line between groups
- Use Python 3.11+ syntax (`X | Y` not `Optional[X]`)
- Bilingual docstrings following existing convention: `"""中文描述\nEnglish description"""`
