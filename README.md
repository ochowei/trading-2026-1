# trading-2026-1

量化交易實驗框架 — 用模組化架構管理無數個交易策略實驗。

Quantitative trading experiment framework — manage unlimited trading strategy experiments with a modular architecture.

## 快速開始 (Quick Start)

開發指令與專案架構請參考 [CLAUDE.md](CLAUDE.md)。

## CSV Market Data

現有 `DataFetcher(start=...).fetch_all([...])` 呼叫面保持不變，但主要 ticker 資料現在會先通過
Yahoo Finance provider boundary，再發布至 `.cache/market-data/`。第一版只接受 Yahoo Finance
`1d`、`auto_adjust=True` 的 adjusted OHLCV；不支援 SQLite、Parquet、raw prices 或 intraday。
既有合法 `period` 值（`1d`、`5d`、月／年區間、`ytd`、`max`）會在 normalized cache frame
上切片；未知 period 在任何網路存取前 fail closed。

每個 series 使用 filesystem-safe ticker encoding，儲存一份 deterministic CSV 與一份 metadata
sidecar。讀取時會驗證 checksum、schema、日期唯一且遞增、required values 為非 NaN／有限值、OHLC 關係、非負
volume 與精確 XNYS session coverage（包含歷史特殊休市及 early close，拒絕缺少或額外非交易日）。完全相同的 duplicate 可去重；conflicting duplicate 或
其他 invalid rows 不會被靜默刪除或發布。損壞的 active cache 會移至
`.cache/market-data-quarantine/`，並嘗試 full rebuild；無法取得有效 replacement 時 fail closed。

```bash
uv run trading data status SPY                         # 唯讀；不下載、不 refresh
uv run trading data refresh SPY --start 2020-01-01   # incremental + overlap
uv run trading data refresh SPY --full                # full history refresh
uv run trading data refresh SPY --end 2026-08-04      # 明確 inclusive cutoff
```

`status` 顯示 active cache 的 valid/stale/corrupt/missing/busy 狀態、data cutoff、incremental/full
refresh timestamps 與 checksum。
refresh 使用 per-series bounded file lock、temporary files、publish 前 validation 與 atomic replace；
同一 ticker 的 concurrent refresh（包含 explicit incremental refresh）會在取得 lock 後重新確認
cache generation，只下載並發布一次完整有效的 cache。`--full` 建立 snapshot-eligible 的完整刷新
generation；它不可搭配 `--start`，且任何 refresh 都不可讓 active cutoff 倒退。

新的共用模型可預先宣告 primary/auxiliary `MarketDataRequirement`、`AvailabilityPolicy` 與
`SignalDecisionTime`，並建立 defensive-copy 的 read-only `MarketDataBundle`。Auxiliary daily series
只能從 bundle 取得依 declared policy 與 Signal Decision Time 完成的 backward as-of alignment，
不能直接讀取 raw same-session frame；不知道精確發布時間時至少延遲一個 primary session，超過宣告的
maximum observation lag 會 fail closed。Bundle 由同一 `MarketDataService` 解析全部 declarations，
缺少 history/session coverage 或重複 declaration 會在 detector 執行前失敗。完整技術契約見
[docs/market-data.md](docs/market-data.md)。

## Reproducible Research Evidence

Phase 2 將完整刷新 generation 的 canonical CSV bytes 發布為 SHA-256 content-addressed immutable
data blobs。兩個實驗使用相同 bytes 時共用同一 blob；incremental-mixed cache 不具 snapshot
eligibility。Snapshot manifest 記錄每個 primary/auxiliary declaration、availability policy、provider
context、cutoff、blob checksum，以及可選的 research-definition blob。損壞的 immutable blob 只會讓
snapshot/result 變成 unreproducible，永遠不會以目前 Yahoo 資料覆寫或修補。
所有 published manifest 必須使用 `.snapshot.json`，並以 strict canonical JSON round-trip 拒絕 unknown
fields 或替代 serialization，確保 Git retention、GC discovery 與 snapshot identity 使用同一份契約。

Research-definition fingerprint 包含 canonical resolved config、strategy/detector/backtester 的 normalized
Python AST、execution-engine version、base/stress execution-cost policies、Python 與 relevant dependency versions。Comments 或 formatting 不改變
semantic fingerprint；threshold、execution rule 或 dependency identity 會改變。Definition capture 必須從
source 自動解析可重建的 Git context；非 Git source 會 fail closed。Definition blob 另外保存 exact source，
因此正式執行時的 dirty worktree 可重建。

```bash
uv run trading data snapshot SPY --experiment migrated_experiment --aux '^VIX' \
  --history-start 2020-01-01 --decision 2026-08-04
uv run trading data snapshot SPY --aux '^VIX' --history-start 2020-01-01 \
  --decision 2026-08-04 --manifest results/example/data.snapshot.json
uv run trading data verify results/example/data.snapshot.json
uv run trading data export results/example/run.snapshot.json backup.snapshot.zip
uv run trading data import backup.snapshot.zip --manifest results/example/imported.snapshot.json
uv run trading data gc --grace-days 7          # 掃描 results/，dry-run
uv run trading data gc --grace-days 7 --apply  # explicit delete
uv run trading run experiment_name --ephemeral
uv run trading run migrated_experiment
uv run trading run migrated_experiment --snapshot results/example/run.snapshot.json
uv run trading run migrated_experiment --offline results/example/run.snapshot.json
uv run trading run unmigrated_experiment --legacy
```

`data snapshot --experiment NAME` 會捕捉 current definition，預設發布到
`results/NAME/<snapshot_id>.snapshot.json`；snapshot-aware experiment 的無旗標 `trading run NAME`
會找出符合 current exact definition reference 的最新 immutable manifest，再以此執行 formal online。Online
只接受最新 completed session 的 verified data+definition snapshot，並在 current exact definition
相符時更新 historical result 與 `latest.json`；offline 接受較舊
complete snapshot、只寫 historical result；ephemeral 完全不寫 result/registry。Snapshot-aware experiment
必須實作 `run_with_bundle`、`capture_research_definition` 與回傳穩定 family/hypothesis 的
`declare_experiment_trial`。未遷移 experiment 若要持久化必須明確使用
`--legacy`；它只會寫入 legacy historical result，不會更新 `latest.json`，待 Phase 9 declaration migration
後逐批移除。Portable bundle import 會先驗證 manifest、所有
blobs 的 checksum、schema、session coverage 與 canonical CSV bytes，再檢查 collision 並發布；GC 預設
dry-run、保護所有 retained manifest references，且只處理 grace period 外的
orphan blobs。完整契約見 [docs/reproducibility.md](docs/reproducibility.md)。

`run_with_bundle` 必須回傳 typed `CanonicalSleeveInput`；formal coordinator 會依 frozen
definition 的 base/stress policies 呼叫共享 sleeve evaluator 並生成 result evidence，不接受 runner
自行聲稱的 canonical metrics。

## Result validity and trial history

Phase 4 gives every new formal result a versioned validity contract. Schema v3 retains the existing
Part A / Part B / Part C fields and records the referenced data snapshot identity, actual data
cutoff, definition snapshot identity, semantic definition fingerprint, development summary,
historical stability folds, shadow/live evidence, legacy period results, and canonical sleeve
gross/base-net/stress-net evidence. Schema-v2 results remain readable as `legacy`. Status is recomputed
read-only as `valid`, `data-stale`, `definition-stale`, `unreproducible`, or `legacy`.

Only a complete successful result with verified current data and the current semantic definition
is eligible for ranking or follow-up. Legacy files remain readable but are never assigned fake
snapshot evidence. Formatting, comments, and explicitly declared reporting-only symbols do not
change a definition fingerprint only when the symbol is unambiguous and unreferenced by retained
outcome code; symbol names are not implicitly trusted, and uncertain or behavior-affecting changes
do change it. If the current definition cannot be resolved, a schema-v3 result is
`unreproducible`, not `valid`.

```bash
uv run trading result status <experiment_name>  # read-only
uv run trading result status --all              # read-only
uv run trading result evaluate SPY              # refresh all stale candidates or fail closed
uv run trading result registry seed             # explicit legacy inventory seed
```

Formal `online` runs publish historical evidence and advance `latest.json`; formal `offline` runs
publish historical evidence only; `ephemeral` runs write neither results nor registry observations.
Explicit evaluation fully refreshes retained requirements and publishes a new current exact
snapshot before rerunning each stale candidate.
Followup qualification and experiment-documentation workflows require computed `valid` status
before consuming metrics; one invalid candidate blocks a complete ranking.
Failed formal attempts remain in the append-only `results/trial_registry.json`, keyed by experiment
family and semantic definition fingerprint. The result and trial-history contract is documented in
[docs/result-validity-and-trial-history.md](docs/result-validity-and-trial-history.md).

## Manual execution ledger

Phase 5 keeps actual followup state in an ignored, local, append-only CSV ledger. It is dry-run only;
there is no broker API or live cutover. Initialize and verify the managed capital and equal sleeves,
then reconcile against a broker CSV before allowing a new BUY:

```bash
uv run trading ledger init --managed-capital 100000 --universe \
  CIBR COPX DIA EEM EWJ EWT EWZ FCX FXI GLD INDA IWM NVDA SIVR SOXL SPY \
  TLT TQQQ TSLA TSM URA USO VGK VOO XBI XLU
uv run trading ledger verify
uv run trading ledger reconcile --broker-export broker-imports/account.csv
uv run trading ledger export backup/manual-execution-ledger.csv
uv run trading ledger import backup/manual-execution-ledger.csv --path state/manual-execution-ledger.csv
```

The initialization universe must exactly match the current ticker set in
`trading.followup.STRATEGIES`; update the command when that selected-strategy set changes.

The ledger uses Decimal accounting, a canonical CSV/hash chain, append-only corrections, and a local
head checkpoint. Confirmed fills—not backtests or unconfirmed proposals—create positions. `followup`
uses deterministic proposal IDs and actual fill price/quantity for exits; missing, stale, or invalid
ledger/reconciliation state blocks new BUY proposals. An outstanding entry blocks a different BUY
until fill or explicit cancellation, while an outstanding GTC stop keeps its proposal ID across later
runs, reports only its active remainder after partial fills, and requires cancellation before other
term changes or expiry. A GTC stop left after another exit closes the position blocks the sleeve's
next BUY until cancellation is recorded. Ledger exports include an adjacent hidden head checkpoint;
the CSV and checkpoint must be transferred together for import. See
[docs/manual-execution-ledger.md](docs/manual-execution-ledger.md) for event and broker-export details.

## Followup Backtest

```bash
uv run trading followup-backtest             # 最近 126 個完整交易日
uv run trading followup-backtest --days 180  # 最近 180 個完整交易日
uv run trading followup-backtest --start 2025-01-01 --days 126  # 指定起日後 126 個交易日
```

此指令會在執行時直接讀取 `src/trading/followup.py` 的最新 `STRATEGIES`，不維護第二份策略清單。
回測以 USD 100,000 作為初始資金，平均分配至固定策略袖套；允許 fractional shares，
袖套之間不借款、不重新平衡，下載失敗的策略配置保留為現金。每個袖套最多一個未平倉部位；
重疊訊號記為 `skipped / position_already_open`，不會提高曝險。

訊號與成交事件沿用各實驗目前選用的 backtester，包括隔日開盤、停利、停損、
到期出場、悲觀日內成交判定及追蹤停損；candidate generation 先移除 legacy slippage，再由
canonical base/stress policy 統一計入成本。期末未平倉部位以最後一個完整交易日的 adjusted
close 做 mark-to-market；未實現損益會影響 equity return、Sharpe 與最大回撤，但不計入已完成
交易的勝率或平均單筆報酬。Canonical engine 同時保存 gross、base-net 與 stress-net；報表與
portfolio 聚合採 base-net，研究排名也只採 daily-equity base-net Sharpe。預設 base 成本為進出各
5 bps slippage + 每側 1 bp fee，stress 為進出各 20 bps + 每側 2 bps。完整契約與 legacy parity
分類見 [docs/canonical-sleeve-execution.md](docs/canonical-sleeve-execution.md)。

`--days` 僅接受正整數。選用的 `--start` 必須是 `YYYY-MM-DD`；若落在週末、休市日或
缺少資料的日期，會從之後第一個完整交易日開始。起日之後不足指定交易日數時，報告會
使用實際可用區間並顯示警告。單一 ticker 失敗時會列出錯誤並繼續其他策略；若無法建立
任何回測區間，CLI 以非零狀態結束。現有 `uv run trading followup` 仍固定使用最近 60 個
交易日並產生 Firstrade dry-run proposal 報告；實際部位只來自 verified manual ledger，未核對時不會產生新的 BUY。

## 如何設計新實驗 (How to Design a New Experiment)

新增一個實驗只需 **3 個檔案**（config / signal_detector / strategy）。框架使用 `pkgutil` 自動發現實驗，無需手動註冊。以下是完整步驟：

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

在 `experiments/my_strategy/__init__.py`：

```python
from trading.experiments import register
from trading.experiments.my_strategy.strategy import MyStrategy

register("my_strategy")(MyStrategy)
```

### Step 6: 執行與驗證 (Run & Verify)

```bash
# 確認註冊成功
uv run trading list

# 尚未加入 snapshot declarations 時，明確執行 legacy historical run（不更新 latest.json）
uv run trading run my_strategy --legacy
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
uv run trading compare tqqq_001_capitulation my_strategy
```

## 範例參照 (Reference Example)

各實驗的完整說明、參數比較與績效數據請參考：

- [TQQQ 實驗總覽](src/trading/experiments/EXPERIMENTS_TQQQ.md)
- [GLD 實驗總覽](src/trading/experiments/EXPERIMENTS_GLD.md)
