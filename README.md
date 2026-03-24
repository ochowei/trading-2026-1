# trading-2026-1

量化交易實驗專案，採用「實驗單位」方式管理策略研究。

## Current experiment

- `EXP-0001-TQQQ-CAPITULATION`
  - Config: `experiments/EXP-0001-tqqq-capitulation/config.yaml`
  - Notes: `experiments/EXP-0001-tqqq-capitulation/notes.md`
  - Latest report: `experiments/EXP-0001-tqqq-capitulation/results/latest_report.json`

## Run

```bash
trading-tw --strategy tqqq
```

執行後會：
1. 下載 TQQQ 資料並計算訊號
2. 針對 Part A / Part B / Part C 進行回測
3. 產生標準化實驗報告 JSON

## 實驗撰寫規範

- 規範文件：`docs/experiment-writing-guidelines.md`
- 新增實驗前，請先依規範準備 `config.yaml`、`notes.md` 與 `results/` 結構。
