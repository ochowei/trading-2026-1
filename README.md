# trading-2026-1

以 Workflow 治理的量化交易研究平台。新的正式研究不以「新增一個實驗 package」為起點，
而是由已發布的 Policy、版本化 Workflow，以及事前註冊的 Study 共同約束研究決策、執行證據
與獨立審查。

本 README 是 human-facing 導覽，不是第二份規則權威。Repository 結構與 ownership boundary
以 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) 為準；Agent 規則與開發指令以
[CLAUDE.md](CLAUDE.md) 為準。

## 治理模型

```text
Released Policies
  market + broker + execution + portfolio risk
                     |
                     v
Released Workflow Version
  purpose + stages + gates + roles + outcomes
                     |
                     v
Preregistered Study
  frozen hypothesis + plan + exact evidence + independent conclusion
```

三層各自有不同責任：

| Layer | 管理的對象 | 不負責的事 |
| --- | --- | --- |
| Policy | 可重用的市場、broker、成交與 portfolio-risk 約束 | 不定義某一輪研究的 stage 或 outcome |
| Workflow | 可重複的端到端研究決策程序、權限、gate 與終止條件 | 不直接執行 study，也不替 study 下結論 |
| Study | 綁定單一 exact released workflow version 的研究實例 | 不修改 frozen plan、workflow 或 policy |

核心原則：

- 新的 outcome-relevant research identity 必須走 workflow-first 路徑。
- 第一次會影響選擇的正式 execution 或 outcome inspection 前，Study 必須完成 preregistration。
- Workflow release 必須固定 exact released policy versions，不可解析 implicit `latest`。
- 所有決策使用 exact identity、digest、immutable evidence 與 append-only lifecycle record。
- 缺漏、stale、corrupt、衝突或無法 replay 的 evidence 一律 fail closed。
- Human approval、系統 gate 與 independent review 各自獨立，不能互相取代。
- 任何 workflow、study 或回測結果都不自動授權 broker access、下單或 live trading。

## 權威來源

發生歧義時，依下列來源判斷，不以 README 摘要覆寫 canonical contract：

1. Repository guardrails：[CLAUDE.md](CLAUDE.md) 與 [AGENTS.md](AGENTS.md)。
2. Workflow lifecycle registry：[workflows/README.md](workflows/README.md)。
3. Study 綁定的 exact released `WORKFLOW.md`。
4. 共用 Study lifecycle 與 authority：
   [.agents/rules/workflow-study-governance.md](.agents/rules/workflow-study-governance.md)。
5. Policy lifecycle registry：[policies/README.md](policies/README.md)。
6. 技術實作與資料邊界：[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

圖解入口位於 [docs/workflow-governance/README.md](docs/workflow-governance/README.md)。圖解只供
理解角色交接與狀態流；若與 registry、released workflow 或 Study governance 不一致，應遵循
canonical authority。

## Workflow 治理

Workflow family 是一個可重複的端到端決策程序，不是 phase、asset、experiment 或 study。
每個 version 使用 immutable path：

```text
workflows/<stable-slug>--vNNN/
```

每個 `WORKFLOW.md` 必須能獨立說明 purpose、scope、entry conditions、roles、stages、transitions、
invariants、evidence、outcomes、pause/recovery、termination、version boundary 與 shared dependencies。
Root [workflows/README.md](workflows/README.md) 是 lifecycle authority；同一 family 最多一個
`active` 與一個 `draft` version，舊的 `superseded`、`retired` 或 `abandoned` identity 永久保留。

### Authoring 與 release

建立或演進 workflow 時，先由高階 authoring command 產生 deterministic preview。Request 不配置
ID、status 或 timestamp；preview 綁定目前 target digests，若 target drift，必須重新產生 preview。

```bash
uv run trading workflow create --request authoring-request.json --dry-run
uv run trading workflow change create --request change-request.json --dry-run
uv run trading workflow evolve --request evolve-request.json --dry-run
```

Human 確認 exact paths、變更內容、source disposition 與 validation plan 後，才可對同一 request
移除 `--dry-run`。Release preparation 是另一個獨立的 human-authority seam：

```bash
uv run trading workflow release <version-path> --approved-by <human-id>
uv run trading workflow validate --all
```

`RELEASE.json` 必須由 guarded command 產生，不可手寫或回填時間。Prepared release 只有在其 commit
進入 canonical branch 後才生效；它不授權 commit、push、merge、執行 Study、策略 promotion 或交易。

Released `WORKFLOW.md` 不可直接改寫。會改變 purpose、stage、authority、gate、outcome、evidence
或 recovery 解讀的變更，必須建立 accepted change record 與新 workflow version。

## Policy 治理

`policies/` 管理四類 composable executable contracts：

- market：交易日曆、資料可用性與市場行為邊界；
- broker：manual broker 與訂單相關限制；
- execution：日線成交模型、成本與 event ordering；
- portfolio risk：資本隔離、曝險與風險限制。

每個 policy version 綁定 human-readable `POLICY.md`、strict `policy.yaml`、implementation paths、
conformance tests 與 release evidence。Draft 可修改；released version 及其 pinned dependencies
immutable。Superseded release 仍可供歷史 Workflow 與 Study 解析；retired release 不可被新的
Workflow release 選用。

Workflow 必須固定四個 exact policy family/version identities 與 release digests。要改變共用約束，
先發布新 policy version，再由新 workflow version 明確採用；不得在 Workflow 或 Study 內複製後
自行覆寫。

```bash
uv run trading policy sync
uv run trading policy validate --all
uv run trading policy release policies/<family>--vNNN --approved-by <human-id>
uv run trading policy version transition policies/<family>--vNNN --to retired \
  --approved-by <human-id>
```

Policy release 同樣需要當下、明確的人類核准，並在 commit 進入 canonical branch 後才有效。
完整契約見 [docs/policies.md](docs/policies.md)。

## Study 治理

Study 是某個 exact released workflow version 的單次執行。只有 active workflow version 可以建立
新 Study；Study 不會隨 Workflow 升版自動搬移，跨版本延續必須建立新 Study 並以 exact
repository-relative `revisits` path 連結。

### Lifecycle

```text
draft -> preregistered -> running -> awaiting-review -> completed
                           |  ^             |
                           v  |             -> running
                         paused

draft / preregistered / running / paused -> cancelled
```

`completed` 與 `cancelled` 是 terminal states。Pause、cancel 或 reviewer return 都必須有具體原因；
所有 transition 應透過 guarded CLI 執行，不可直接修改 metadata。

### Preregistration 與 frozen design

Study 在 preregistration 前必須完成可否證的 `HYPOTHESIS.md`、exact `PLAN.md`、route-specific
structured inputs，以及所有必要人類核准。Guarded command 會以當下時間建立
`PREREGISTRATION.json`，綁定 workflow、hypothesis 與 plan digests：

```bash
uv run trading workflow study init <active-workflow-path> \
  --slug <study-slug> --title <title> --created-by <identity> \
  --route <clean-historical|retrospective-confirmatory|study-time-retrospective>
uv run trading workflow study preregister <study-path> --approved-by <human-id>
```

Preregistration 後不可修改 hypothesis 或 plan。任何 design change 都必須 cancel 原 Study，建立
新的 CLI-allocated Study identity，並以 `revisits` 保留 lineage。Preregistration 本身也不授權
Development、candidate freeze、Evaluation、Shadow、broker access 或 trading；每個 stage 仍需
exact released workflow 要求的額外 authority。

### Operation 與 candidate freeze

Operator 只能依 frozen plan 推進 Study、執行已授權工作並記錄 exact evidence。Outcome-relevant
trial、失敗 observation、selection history 與 deviations 都必須保留，不得只保存 winner。

```bash
uv run trading workflow study transition <study-path> --to running \
  --by <identity> --approved-by <human-id>
uv run trading workflow study freeze-candidate <study-path> \
  --selection <development-selection.json> --approved-by <human-id>
uv run trading workflow study transition <study-path> --to awaiting-review --by <identity>
```

Candidate freeze 後不得調參、換資料、重排 family、改 gate 或用 Evaluation outcome 選擇新 winner。
若 frozen design 必須改變，應終止或取消該 Study，不能以「修文件」規避新 identity。

### Independent review 與 outcome

Operator 不選擇或撰寫 outcome。Evidence 完整後，Operator 將 Study 送至 `awaiting-review` 並停止；
independent reviewer 只依 preregistration、frozen plan、pinned workflow 與 immutable evidence 判定：

- `pass`：所有 required identities、approvals 與 frozen gates 通過；只授予 Workflow 明定的下一步。
- `fail`：完整且可判定的必要 gate 失敗。
- `insufficient-evidence`：只適用於 Workflow 明確允許繼續累積 evidence 的 open prospective stage。
- `indeterminate`：identity、evidence 或 integrity 不足以可信判定；停止 advancement。

Reviewer 不執行補件、不修 evidence、不調參，也不改 frozen files。經 explicit human confirmation
後，只能撰寫 `CONCLUSION.md` 並使用 guarded completion command：

```bash
uv run trading workflow study complete <study-path> \
  --outcome <pass|fail|insufficient-evidence|indeterminate> \
  --reviewed-by <identity>
```

完成後產生的 `COMPLETION.json` 綁定 preregistration、evidence、conclusion、outcome、reviewer
與時間，且不可再修改。Retrospective `pass` 不等於 `shadow-eligible`；clean Historical `pass`
也只授予 Workflow 明定的下一階段資格，不代表 live authorization 或獲利保證。

## 正式研究與 evidence boundary

新的 research source identity 位於：

```text
src/trading/research_definitions/<family>/<trial>/
```

`src/trading/experiments/` 是封閉的 legacy inventory，只供 reproduction 與明確治理的 migration；
不得新增、改名或就地改變既有 identity 的研究語意。

正式執行必須綁定 exact workflow release、composite policy-set identity、Research Definition
Snapshot、data snapshot、runtime/source identity、result identity、complete commit SHA 與 checksums。
Study 只保存 immutable evidence references，不複製 application source 或 private runtime data。

```bash
uv run trading research list
uv run trading research snapshot <family/trial> --workflow <released-version-path> \
  --decision YYYY-MM-DD
uv run trading research run <family/trial> --workflow <released-version-path> \
  --manifest results/<result-name>/<snapshot-id>.snapshot.json --offline
```

不得在 `workflows/` 或 `policies/` 保存 credentials、broker exports、holdings、private ledgers、
personal trading records 或 raw private trading data。Local-only runtime boundary 與 tracked evidence
位置以 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) 為準。

## 快速驗證

安裝依賴並檢查完整 registry：

```bash
uv sync
uv run trading policy validate --all
uv run trading workflow validate --all
```

Workflow 或 Study mutation 後必須同步 generated indexes，再做完整驗證：

```bash
uv run trading workflow sync
uv run trading workflow validate --all
```

CI 會驗證 workflow、policy、legacy inventory、market-data boundary contracts，以及 Python lint／
formatting。任何 validation issue 都應停止 release、Study advancement 與 outcome-relevant work，
直到同一 identity 與 evidence 被確認或恢復。

## 延伸文件

- [Workflow governance 圖解與權威範圍](docs/workflow-governance/README.md)
- [Workflow lifecycle registry](workflows/README.md)
- [Policy lifecycle registry](policies/README.md)
- [Workflow Study governance](.agents/rules/workflow-study-governance.md)
- [Repository architecture](docs/ARCHITECTURE.md)
- [Reproducible research evidence](docs/reproducibility.md)
- [Result validity and trial history](docs/result-validity-and-trial-history.md)
- [Historical qualification and Shadow](docs/historical-qualification-and-shadow.md)
- [Controlled followup cutover](docs/controlled-followup-cutover.md)
- [Live drift and recovery](docs/live-drift-and-recovery.md)
