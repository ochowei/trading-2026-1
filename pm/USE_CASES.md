# Use Cases — 我可以請 AI 做什麼？

> 本文件列出所有可用的操作情境，以及對應的指令。
>
> 最後更新：2026-04-02

---

## 日常操作

### 產生今日下單指令

每個交易日開盤前執行，取得 Firstrade 下單指令。

```
uv run trading followup
```

輸出包含：
- 合併下單表（BUY MARKET / SELL LIMIT / SELL STOP）
- 持倉狀態與到期提醒
- Trailing stop 每日調整提醒

### 檢查知識新鮮度

確認實驗數據與跨資產教訓是否過期（超過 6 個月）。

```
uv run trading freshness
```

---

## 實驗管理

### 為既有資產新增實驗

資產已有實驗，想嘗試不同參數或策略方向。

```
/new-experiment <TICKER> <策略描述>
```

例如：`/new-experiment GLD 用 RSI 取代 Williams %R`

AI 會自動：檢查禁忌 → 建立程式碼 → 更新文件 → 跑回測驗證

### 開始追蹤全新標的

為從未有實驗的 ticker 建立第一個實驗。

```
/launch-new-asset <TICKER> <策略描述>
```

例如：`/launch-new-asset SLV 白銀均值回歸`

AI 會自動：分析波動率 → 選擇合適模板 → 縮放參數 → 建立程式碼與文件 → 回測驗證

### 執行回測

跑（或重跑）某個實驗的回測，查看結果。

```
/run-experiment <experiment_name>
```

例如：`/run-experiment gld_007_pullback_wr_trail`

產出 Part A（樣本內）、Part B（樣本外）、Part C（實盤）三段結果 + 滾動窗口穩定性分析。

### 更新實驗文件

將回測結果寫入對應的 EXPERIMENTS 文件。

```
/update-experiment-docs <experiment_name>
```

或一次更新全部：`/update-experiment-docs all`

### 驗證實驗

提交前的最終檢查（程式碼品質 + 執行 + 結果合理性）。

```
/validate-experiment <experiment_name>
```

---

## Followup 管理

### 選出某資產的最佳實驗

評估該資產所有實驗，選出最佳者並決定是否納入每日 followup。

```
/evaluate-best <TICKER>
```

門檻：Part B 勝率 ≥ 55%、累積報酬 > 0%、年訊號 ≥ 2、A/B 一致、穩定性漸變。

### 重建整個 followup 清單

從零重新評估所有資產，重建 followup 的策略清單。

```
/rebuild-followup
```

適用於大量實驗更新後，或懷疑現有清單不是最優時。耗時較長。

---

## 研究

### 實驗前研究

設計新實驗前，收集該資產的波動率特性、已知教訓、已掃描參數空間。

```
/pre-experiment-research <TICKER>
```

---

## Quick Reference

| 我想要... | 指令 |
|-----------|------|
| 看今天該下什麼單 | `uv run trading followup` |
| 為 GLD 試新策略 | `/new-experiment GLD <描述>` |
| 開始追蹤新標的 | `/launch-new-asset <TICKER> <描述>` |
| 跑回測 | `/run-experiment <name>` |
| 結果寫進文件 | `/update-experiment-docs <name>` |
| 選最佳實驗 | `/evaluate-best <TICKER>` |
| 重建 followup | `/rebuild-followup` |
| 檢查數據新鮮度 | `uv run trading freshness` |
| 做實驗前功課 | `/pre-experiment-research <TICKER>` |
| 提交前驗證 | `/validate-experiment <name>` |
