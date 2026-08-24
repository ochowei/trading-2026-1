# Workflow Governance Diagram Review Status

此文件追蹤 [`workflow-governance-flow.html`](workflow-governance-flow.html) 的 sequence／activity
圖、[`workflow-governance-layers.html`](workflow-governance-layers.html) 的 A1 層級交接與 A2
各 Layer 內部狀態參考，
以及 Work Package 1–4 治理實作之間的審查問題。它是視覺化文件的待辦紀錄，不是 workflow
contract、release authority 或 study outcome 的權威來源。

- Last reviewed: 2026-08-24
- Review basis: current repository worktree
- Status vocabulary:
  - `resolved`: 原始問題已在目前視覺化中可見且語意正確。
  - `open-partial`: 已有部分資訊，但原始問題仍未完整解決。

## Summary

| Status | Count | Items |
|---|---:|---|
| `resolved` | 5 | GD-001, GD-002, GD-003, GD-004, GD-006 |
| `open-partial` | 1 | GD-005 |

目前仍需處理的是 **GD-005**。

## Findings

### GD-001 — Replacement change decision order

- Priority: P1
- Status: `resolved`
- Required order: `change create → human decision → accepted → evolve → replacement draft → release`
- Current evidence: sequence、activity 與 A2 的 L1 內部狀態參考都先完成 change decision，
  再進入 evolve 與 replacement draft。
- Governing evidence:
  [`tests/test_workflow_authoring.py`](../tests/test_workflow_authoring.py)、
  [`evolve.md`](../.agents/skills/trading-author-workflow/references/evolve.md)
- Remaining action: none.

### GD-002 — Registry `active` versus effective authority

- Priority: P1
- Status: `resolved`
- Required distinction: prepared branch 中 registry status 已為 `active`，但只有 commit 進入
  canonical branch 後才具 effective authority。
- Current evidence: sequence、activity 與 A2 的 L2 內部狀態參考均明確拆分 prepared
  `status = active`、canonical merge 與 effective authority。
- Governing evidence:
  [`workflow_authoring.py`](../src/trading/core/workflow_authoring.py)、
  [`workflows/README.md`](../workflows/README.md)、
  [`release.md`](../.agents/skills/trading-author-workflow/references/release.md)
- Remaining action: none.

### GD-003 — Study authority gates

- Priority: P1
- Status: `resolved`
- Current evidence: A2 的 L3 Authority gates 已分別列出 preregistration、Development、
  candidate freeze 與 Evaluation approval，明示各 authority 不可從前一階段推導；並要求
  reviewer 寫入 terminal outcome 前具備 explicit human confirmation 與 stable reviewer identity。
- Governing evidence:
  [`workflow-study-governance.md`](../.agents/rules/workflow-study-governance.md)
- Remaining action: none.

### GD-004 — Mandatory release guards

- Priority: P1
- Status: `resolved`
- Current evidence: A1 已將 complete self-contained contract、accepted changes 與 combined
  impact、exact active target、safe unfinished studies、exact released policy pins、normative
  dependencies／pinned companions、無遺漏 changes，以及 explicit human approval 展開為 release
  checklist；並分別呈現未核准、unsafe studies 與未 canonical merge 的 fail-closed 路徑。
- Governing evidence:
  [`release.md`](../.agents/skills/trading-author-workflow/references/release.md)、
  [`impact.md`](../.agents/skills/trading-author-workflow/references/impact.md)
- Remaining action: none.

### GD-005 — Activity diagram lifecycle scope

- Priority: P2
- Status: `open-partial`
- Already visible elsewhere: A2 各 Layer 內部狀態參考已涵蓋 change
  `rejected/deferred/withdrawn`、study pause/cancel/reviewer-return，以及 version
  `abandoned/retired`。
- Still missing: Activity diagram 本身仍只呈現 happy path，但標題仍為「生命週期與治理閘門」，
  容易被理解為完整 lifecycle。
- Governing evidence:
  [`remove.md`](../.agents/skills/trading-author-workflow/references/remove.md)、
  [`workflow-study-governance.md`](../.agents/rules/workflow-study-governance.md)
- Recommended closure: 保持簡圖並將標題改為 `Activity diagram｜Happy-path handoff`，同時指向
  A2 各 Layer 內部狀態參考作為完整狀態補充；若仍稱 lifecycle，則必須補齊所有分支。

### GD-006 — Stale-preview fail-closed gate

- Priority: P2
- Status: `resolved`
- Required behavior: target drift 或 invalid partial state 必須阻止 apply、保持 zero mutation，
  並要求 fresh preview。
- Current evidence: A1 已直接畫出 preview 失敗後修正輸入並回到 fresh preview 的路徑；A2 的
  L1 Fail-closed 防護也明示 target drift / invalid partial state 阻止 apply、保持 zero mutation、
  重新產生 fresh preview，並在 resolved changes 改變時重新取得人工確認。
- Governing evidence:
  [`core.md`](../.agents/skills/trading-author-workflow/references/core.md)
- Remaining action: none. 此 gate 不需重複塞入維持簡化的 happy-path diagram。

## Closure rule

每次更新治理圖後，重新依上述 governing evidence 檢查。只有在視覺化明確呈現要求，或文件
刻意重新界定圖的範圍、避免完整性誤解時，才可將 `open-partial` 改為 `resolved`。狀態變更需同步
更新 Last reviewed、Summary 與對應 finding。
