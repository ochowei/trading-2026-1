# CLAUDE.md

## 專案規範

在修改本專案時，必須遵循 `.agents/rules/ai-agent-guidelines.md` 中定義的所有規則。

核心要點：

- **程式碼與文件同步**：任何程式碼變更都必須同步更新相關文件（`README.md`、`PLAN_TQQQ_NEXT.md`、`MEMO.md` 等），確保文件準確反映實際行為。
- **檔案結構變更**：新增、刪除或搬移檔案時，必須更新 `README.md` 中的專案架構圖與 `.agents/rules/ai-agent-guidelines.md` 中的檔案用途說明。
- **新增實驗時**：更新 `.github/workflows/tqqq-backtest.yml` 的實驗選項、`README.md` 的範例參照表。
- **發現不一致時**：主動修正文件與程式碼之間的不一致。

## 開發指令

```bash
# 安裝依賴
uv sync

# 列出所有實驗
uv run trading list

# 執行指定實驗
uv run trading run <experiment_name>

# 比較實驗結果
uv run trading compare <exp1> <exp2>
```
