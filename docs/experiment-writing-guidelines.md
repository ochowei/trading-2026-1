# 實驗撰寫規範

本規範用於統一量化策略實驗的撰寫方式，確保每個實驗可追蹤、可比較、可重現。

## 1. 命名與目錄
- 實驗 ID 格式：`EXP-xxxx-<slug>`（例如：`EXP-0001-TQQQ-CAPITULATION`）。
- 每個實驗都必須有獨立資料夾：`experiments/<experiment-folder>/`。
- 目錄至少包含：
  - `config.yaml`
  - `notes.md`
  - `results/`（可為空，但需保留）

## 2. config.yaml 必填欄位
- `experiment_id`
- `status`（`draft` / `active` / `retired`）
- `strategy_name`
- `ticker_universe`
- `hypothesis`
- `data_range`（至少需有 in-sample 與 out-of-sample）
- `signal`
- `portfolio_rule`
- `cost_model`
- `output.report_path`

## 3. notes.md 必填內容
1. `Purpose`：一句話描述要驗證的交易假設。
2. `Entry Criteria`：進場條件（條件與閾值要可對應到 config）。
3. `Exit Criteria`：出場條件與優先順序。
4. `Current Limitations`：至少列出兩個當前限制。
5. `嘗試提升績效`：至少三個下一步優化方向。

## 4. 結果與可重現性
- 回測執行完成後，需輸出 JSON 報告到 `output.report_path`。
- JSON 報告至少應包含：
  - `experiment_id`
  - `created_at_utc`
  - `status`
  - `metrics`（part_a / part_b / part_c）
  - `raw_results`

## 5. Registry 維護
- 新增或更新實驗時，必須同步更新 `registry/experiments.csv`。
- 每列至少包含：
  - `experiment_id`
  - `status`
  - `strategy_name`
  - `universe`
  - `report_path`

## 6. 版本控管規範
- 參數調整若會影響回測結果，應：
  - 更新 `notes.md` 的變更描述。
  - 重新生成 `latest_report.json`。
  - 在 commit message 中說明變更目的（例如：成本模型更新、訊號閾值調整）。
