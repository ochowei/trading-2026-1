# trading-2026-1

量化交易實驗框架 — 用模組化架構管理無數個交易策略實驗。

Quantitative trading experiment framework — manage unlimited trading strategy experiments with a modular architecture.

## 快速開始 (Quick Start)

```bash
# 安裝依賴 (Install dependencies)
uv sync

# 列出所有實驗 (List all experiments)
uv run trading list

# 執行單一實驗 (Run a specific experiment)
uv run trading run tqqq_capitulation

# 執行全部實驗 (Run all experiments)
uv run trading run --all

# 比較實驗結果 (Compare experiment results)
uv run trading compare tqqq_capitulation another_experiment
```

## 專案架構 (Project Structure)

```
src/trading/
├── cli.py                              # 統一 CLI 入口
├── core/                               # 共用基礎設施
│   ├── base_config.py                  # ExperimentConfig dataclass
│   ├── base_signal_detector.py         # BaseSignalDetector ABC
│   ├── base_backtester.py              # 通用回測引擎（停利/停損/到期）
│   ├── base_strategy.py                # BaseStrategy（fetch → 指標 → 訊號 → 回測 → 報表）
│   ├── data_fetcher.py                 # yfinance 多線程資料抓取
│   └── results.py                      # 結果儲存（JSON）與跨實驗比較
├── experiments/                        # 所有實驗放在這裡
│   ├── __init__.py                     # 實驗註冊表
│   ├── tqqq_capitulation/              # TQQQ 恐慌抄底策略（基礎版）
│   │   ├── config.py
│   │   ├── signal_detector.py
│   │   └── strategy.py
│   ├── tqqq_cap_relaxed_entry/         # TQQQ 放寬進場條件變體
│   │   ├── config.py
│   │   ├── signal_detector.py
│   │   └── strategy.py
│   ├── tqqq_cap_wider_exit/            # TQQQ 放寬出場條件變體
│   │   ├── backtester.py
│   │   ├── config.py
│   │   ├── signal_detector.py
│   │   └── strategy.py
│   ├── tqqq_cap_vix_filter/            # TQQQ VIX 過濾器變體
│   │   ├── config.py
│   │   ├── signal_detector.py
│   │   └── strategy.py
│   ├── tqqq_cap_vix_adaptive/          # TQQQ 軟性 VIX + 適應性出場變體
│   │   ├── config.py
│   │   ├── signal_detector.py
│   │   └── strategy.py
│   └── _template/                      # 新實驗模板（複製即用）
│       ├── __init__.py
│       ├── config.py
│       ├── signal_detector.py
│       └── strategy.py
```

## 如何設計新實驗 (How to Design a New Experiment)

新增一個實驗只需 **3 個檔案 + 1 行註冊**。以下是完整步驟：

### Step 1: 複製模板 (Copy Template)

```bash
cp -r src/trading/experiments/_template src/trading/experiments/my_strategy
```

### Step 2: 定義配置 `config.py` (Define Configuration)

編輯 `experiments/my_strategy/config.py`，繼承 `ExperimentConfig` 並加入策略專屬參數：

```python
from dataclasses import dataclass
from trading.core.base_config import ExperimentConfig

@dataclass
class MyConfig(ExperimentConfig):
    # 策略專屬參數 (Strategy-specific parameters)
    sma_fast: int = 5
    sma_slow: int = 20
    entry_threshold: float = -0.02

def create_default_config() -> MyConfig:
    return MyConfig(
        name="my_strategy",                      # 實驗 ID（唯一）
        display_name="My Mean Reversion Strategy", # 顯示名稱
        tickers=["SPY"],                          # 標的清單
        data_start="2019-01-01",                  # 資料起始日
        # --- 回測區間（可用預設值）---
        # part_a_start="2019-01-01",              # In-Sample 開始
        # part_a_end="2023-12-31",                # In-Sample 結束
        # part_b_start="2024-01-01",              # Out-of-Sample 開始
        # part_b_end="2025-12-31",                # Out-of-Sample 結束
        # part_c_start="2026-01-01",              # Live 開始
        # part_c_end="",                          # "" = 至今
        # --- 出場參數 ---
        profit_target=0.03,                       # 獲利目標 +3%
        stop_loss=-0.05,                          # 停損 -5%
        holding_days=5,                           # 最長持倉 5 天
    )
```

**ExperimentConfig 欄位說明：**

| 欄位 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `name` | `str` | (必填) | 實驗唯一 ID，用於 CLI 和檔案命名 |
| `experiment_id` | `str` | `""` | 實驗編號（如 `"TQQQ-001"`），用於 `list` 指令顯示 |
| `display_name` | `str` | (必填) | 報表中的顯示名稱 |
| `tickers` | `list[str]` | `[]` | 交易標的清單 |
| `data_start` | `str` | `"2019-01-01"` | 資料下載起始日 |
| `part_a_start/end` | `str` | `2019~2023` | Part A In-Sample 回測區間 |
| `part_b_start/end` | `str` | `2024~2025` | Part B Out-of-Sample 回測區間 |
| `part_c_start/end` | `str` | `2026~今` | Part C Live 驗證區間 |
| `profit_target` | `float` | `0.05` | 獲利目標（盤中最高價觸及即出場） |
| `stop_loss` | `float` | `-0.08` | 停損閾值（收盤價跌破即出場） |
| `holding_days` | `int` | `7` | 最長持倉天數（到期以收盤價出場） |

### Step 3: 實作訊號偵測 `signal_detector.py` (Implement Signal Detection)

這是實驗的**核心邏輯**。繼承 `BaseSignalDetector`，實作兩個方法：

```python
import pandas as pd
from trading.core.base_signal_detector import BaseSignalDetector
from trading.experiments.my_strategy.config import MyConfig

class MySignalDetector(BaseSignalDetector):
    def __init__(self, config: MyConfig):
        self.config = config

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        計算技術指標。在完整資料上呼叫一次。
        注意：不要 drop rows，避免 rolling 邊界問題。
        """
        df = df.copy()
        df["SMA_Fast"] = df["Close"].rolling(self.config.sma_fast).mean()
        df["SMA_Slow"] = df["Close"].rolling(self.config.sma_slow).mean()
        df["Deviation"] = (df["Close"] - df["SMA_Slow"]) / df["SMA_Slow"]
        return df

    def detect_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        偵測交易訊號。在各 Part 的資料子集上分別呼叫。
        必須新增布林欄位 'Signal'。
        """
        df = df.copy()
        df["Signal"] = (
            (df["Deviation"] < self.config.entry_threshold) &
            (df["SMA_Fast"] < df["SMA_Slow"])
        )
        return df
```

**兩個方法的呼叫時機：**
- `compute_indicators()` — 在**完整歷史資料**上呼叫一次（避免 rolling window 邊界問題）
- `detect_signals()` — 在 Part A / B / C 各區間分別呼叫（指標欄位已存在）

### Step 4: 串接策略 `strategy.py` (Wire Up Strategy)

大多數實驗只需「接線」—— 把 config 和 detector 傳入即可：

```python
from trading.core.base_config import ExperimentConfig
from trading.core.base_signal_detector import BaseSignalDetector
from trading.core.base_strategy import BaseStrategy
from trading.experiments.my_strategy.config import MyConfig, create_default_config
from trading.experiments.my_strategy.signal_detector import MySignalDetector

class MyStrategy(BaseStrategy):
    def create_config(self) -> ExperimentConfig:
        return create_default_config()

    def create_detector(self) -> BaseSignalDetector:
        return MySignalDetector(create_default_config())

    # （選用）覆寫以在報表中顯示策略專屬參數
    def _print_strategy_params(self, config: ExperimentConfig) -> None:
        if isinstance(config, MyConfig):
            print(f"  SMA Fast/Slow:  {config.sma_fast}/{config.sma_slow}")
            print(f"  Entry threshold: {config.entry_threshold:.1%}")
        super()._print_strategy_params(config)
```

**`BaseStrategy.run()` 自動處理的流程：**
1. 下載資料（DataFetcher）
2. 計算指標（`compute_indicators`）
3. 分 Part A / B / C 區間
4. 各區間偵測訊號（`detect_signals`）
5. 各區間回測（BaseBacktester）
6. 輸出報表 + 比較表 + 今日訊號檢查

### Step 5: 註冊實驗 (Register Experiment)

在 `src/trading/experiments/__init__.py` 底部加一行：

```python
from trading.experiments import my_strategy  # noqa: F401, E402
```

同時在 `experiments/my_strategy/__init__.py`：

```python
from trading.experiments import register
from trading.experiments.my_strategy.strategy import MyStrategy

register("my_strategy")(MyStrategy)
```

### Step 6: 執行與驗證 (Run & Verify)

```bash
# 確認註冊成功
uv run trading list

# 執行實驗
uv run trading run my_strategy
```

## 進階用法 (Advanced Usage)

### 自訂回測引擎 (Custom Backtester)

預設的 `BaseBacktester` 使用「停利 > 停損 > 到期」的日級出場邏輯，適用於大多數策略。如果你需要不同的出場機制（例如 trailing stop、多腿出場），可以覆寫 `create_backtester()`：

```python
from trading.core.base_backtester import BaseBacktester

class MyCustomBacktester(BaseBacktester):
    def run(self, df):
        # 自訂回測邏輯
        ...

class MyStrategy(BaseStrategy):
    def create_backtester(self, config):
        return MyCustomBacktester(config)
```

### 比較實驗結果 (Compare Results)

每次執行實驗時，結果會自動存為 JSON 到 `results/{experiment_name}/`。可以跨實驗比較：

```bash
uv run trading compare tqqq_capitulation my_strategy
```

## 範例參照 (Reference Example)

`experiments/tqqq_capitulation/` 是基礎實作範例，其餘 3 個實驗為其變體：

| 實驗 | 說明 |
|------|------|
| [`tqqq_capitulation`](src/trading/experiments/tqqq_capitulation/) | 基礎版：三條件恐慌抄底訊號 + 冷卻機制 |
| [`tqqq_cap_relaxed_entry`](src/trading/experiments/tqqq_cap_relaxed_entry/) | 變體：放寬進場條件 |
| [`tqqq_cap_wider_exit`](src/trading/experiments/tqqq_cap_wider_exit/) | 變體：放寬出場條件（含自訂 backtester） |
| [`tqqq_cap_vix_filter`](src/trading/experiments/tqqq_cap_vix_filter/) | 變體：加入 VIX 過濾器 |
| [`tqqq_cap_vix_adaptive`](src/trading/experiments/tqqq_cap_vix_adaptive/) | 變體：軟性 VIX + 適應性出場 (TQQQ-005) |
