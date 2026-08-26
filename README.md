# trading-2026-1

以 Workflow 治理的量化交易研究平台。這個 repository 的主要內容可分為五塊：

| 區塊 | 位置 | 用途 |
| --- | --- | --- |
| 1. Policy | [`policies/`](policies/) | 定義可重用、版本化的 market、broker、execution 與 portfolio-risk 規則。 |
| 2. Workflow | [`workflows/`](workflows/) | 定義研究程序、stage、gate、角色與 outcome；每個 released workflow 都引用 exact released policy versions。 |
| 3. Study | `workflows/<workflow>--vNNN/work/studies/` | 某個 exact workflow version 之下的一次研究執行，保存事前註冊的假設、計畫、證據與獨立結論。 |
| 4. Legacy 資料 | [`legacy/`](legacy/) | 已退役的 experiments、results 與舊 Agent workflows，只供唯讀檢查與重現。 |
| 5. Repo 治理用檔案 | [`AGENTS.md`](AGENTS.md)、[`CLAUDE.md`](CLAUDE.md)、[`docs/`](docs/)、[`.agents/`](.agents/) | 規範 Agent 行為、repository 架構、研究治理與維護方式。 |

## 核心關係

```text
Policy
  └─ Workflow（引用 exact policy versions）
       └─ Study（建立在 exact workflow version 裡）
```

- 新的正式研究走 `Policy → Workflow → Study`，不再新增 legacy experiment。
- Study 必須在會影響選擇的正式執行或 outcome inspection 前完成 preregistration。
- Workflow、Study 或回測結果都不自動授權 broker access、下單或 live trading。
- Legacy 內容不得用來啟動新的研究、排名、qualification 或 promotion。

## 其他實作位置

- [`src/trading/`](src/trading/)：CLI、研究執行、資料、policy 與 workflow 的程式實作。
- [`src/trading/research_definitions/`](src/trading/research_definitions/)：新的 workflow-native research definitions。
- [`tests/`](tests/)：自動化測試與治理 contract 驗證。
- [`results/`](results/)：正式研究的 tracked evidence 與結果；private runtime data 不得提交。

## 常用驗證

```bash
uv sync
uv run trading policy validate --all
uv run trading workflow validate --all
```

若需完整規則，請直接閱讀各區塊的權威文件：

- Repository 結構與 ownership boundary：[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Agent 規則與開發指令：[`CLAUDE.md`](CLAUDE.md)
- Policy registry：[`policies/README.md`](policies/README.md)
- Workflow registry：[`workflows/README.md`](workflows/README.md)
- Study governance：[`.agents/rules/workflow-study-governance.md`](.agents/rules/workflow-study-governance.md)
- Legacy boundary：[`legacy/README.md`](legacy/README.md)
