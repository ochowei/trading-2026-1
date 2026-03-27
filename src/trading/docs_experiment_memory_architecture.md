# 實驗記憶體架構建議（給 AI Agent 省 Token）

本文提供一套「可擴充、可壓縮、可查詢」的實驗資料架構，目標是：

1. 持續累積成功與失敗嘗試。
2. 降低 AI Agent 每次讀取歷史實驗所需 token。
3. 讓新實驗設計能快速聚焦在「最可能有效」的方向。
4. 保留可手動跟單（Firstrade）所需的成交模型相容資訊。

---

## 一、核心問題：現在資料太「全文導向」

目前每個標的的 `EXPERIMENTS_*.md` 都很完整，但隨著版本增長，Agent 每次都要重讀大量敘述、表格、脈絡，會造成：

- token 成本上升
- 回應時間上升
- 容易遺漏失敗案例細節（尤其是「為什麼失敗」）

---

## 二、建議改成三層記憶（3-layer memory）

> 原則：先讀「短摘要」，必要時再下鑽到「中摘要」與「原始明細」。

### Layer 1: 實驗索引（Ultra-compact index，機器優先）

檔案建議：`results/index.json`

每個實驗只保留固定欄位（例如 15~25 個）：

- `experiment_name`, `experiment_id`, `ticker`, `family`
- `status`（best / candidate / failed）
- `hypothesis_tag`（pullback、rsi、trailing_stop...）
- `execution_model_compliant`（bool）
- `part_a_signals`, `part_b_signals`, `ab_signal_ratio`
- `part_a_cum_return`, `part_b_cum_return`, `part_c_cum_return`
- `max_drawdown`
- `failure_reason_tags`（如 `pessimistic_fill_conflict`, `signal_sparse_b`）
- `supersedes`, `superseded_by`
- `last_updated`

用途：
- Agent 在發想新實驗前，先用 1 個檔案做篩選，不必先讀大篇幅 markdown。

### Layer 2: 實驗卡（Experiment card，決策優先）

檔案建議：`results/cards/<experiment_name>.md`

每張卡片控制在 200~400 字，固定模板：

1. 假說（Hypothesis）
2. 關鍵參數（最多 8 個）
3. A/B/C 關鍵績效（只放必要指標）
4. 成功/失敗判定
5. 給下一版的建議（Next action）

用途：
- Agent 篩完 Layer 1 後，只讀 2~5 張卡片即可產生新方案。

### Layer 3: 完整報告（Full history，人工審閱）

檔案維持：`src/trading/experiments/EXPERIMENTS_*.md` + `results/<exp>/latest.json`

用途：
- 人工審查、追查細節、回顧交易明細。

---

## 三、失敗嘗試要「標準化」而不是只有敘述

你提到「失敗也要留下來供未來參考」，非常關鍵。建議在每次 run 後，最少補三件事（可由 Agent 自動填）：

1. `failure_type`：
   - `no_edge`
   - `overfit_part_a`
   - `signal_imbalance_ab`
   - `execution_model_break`
   - `drawdown_too_large`
2. `failure_reason_tags`：可多選（2~5 個）
3. `next_attempt_constraints`：下一版要遵守的限制（例如「Part B 訊號 >= 8」、「不得使用 trailing stop」）

這三項可直接進 Layer 1/Layer 2，讓 Agent 不再重踩同樣地雷。

---

## 四、把 Prompt 轉成「可機器解析的目標條件」

你現在的 prompt 已經很接近需求。建議再加上「硬性 gate + 優先級」：

```text
目標：
1) 必須符合成交模型（可 Firstrade 手動跟單）
2) Part A 與 Part B 訊號數差距 <= 30%
3) Part B 累計報酬 > 基線（SIVR-003）
4) 若失敗，必須輸出 failure_type / failure_reason_tags / next_attempt_constraints
```

有了這種格式，Agent 可自動把結果落到 Layer 1/2，不需每次重寫長文。

---

## 五、建議新增的最小工作流（MVP）

每次 `uv run trading run <experiment_name>` 後，自動執行：

1. 從 `results/<exp>/latest.json` 擷取固定欄位 → 更新 `results/index.json`
2. 生成/覆蓋 `results/cards/<exp>.md`（固定模板）
3. 在 `EXPERIMENTS_*.md` 只保留「人類敘事 + 關鍵結論」，不再承擔全部機器查詢責任

---

## 六、命名與關聯建議（避免知識碎片化）

- `hypothesis_tag`：統一字典（例如 `pullback_wr`, `rsi_deviation`, `trailing_stop`）
- `failure_reason_tags`：統一字典（例如 `ab_imbalance`, `tp_cut_by_trailing`, `pessimistic_fill`）
- `supersedes` / `superseded_by`：強制紀錄父子關係

這三項會大幅提升 Agent 做「跨實驗遷移學習」的效率。

---

## 七、對你目前 SIVR 開發場景的直接好處

- 能快速排除已驗證失敗方向（例如 trailing stop 類型）
- 直接鎖定 A/B 訊號平衡較佳的假說族群
- 讓 Agent 在 token 固定預算下，仍能考慮更多歷史嘗試
- 保留完整失敗軌跡，不會因摘要而遺失教訓

---

## 八、落地優先順序（建議）

1. **先做 Layer 1（index.json）**：投資小、回報最大。
2. **再做 Layer 2（cards）**：讓 Agent 設計新實驗時更穩定。
3. **最後調整 EXPERIMENTS_*.md 的篇幅分工**：人類可讀、機器可查分離。

