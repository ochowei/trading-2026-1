# Workflow Governance Diagram Review Status

此文件追蹤 [`workflow-governance-flow.html`](workflow-governance-flow.html) 與 Work Package
1–4 治理實作之間的審查問題。它是視覺化文件的待辦紀錄，不是 workflow contract、release
authority 或 study outcome 的權威來源。

- Last reviewed: 2026-08-21
- Review basis: current repository worktree
- Status vocabulary:
  - `resolved`: 原始問題已在目前視覺化中可見且語意正確。
  - `open-partial`: 已有部分資訊，但原始問題仍未完整解決。

## Summary

| Status | Count | Items |
|---|---:|---|
| `resolved` | 3 | GD-001, GD-002, GD-006 |
| `open-partial` | 3 | GD-003, GD-004, GD-005 |

目前仍需處理的是 **GD-003、GD-004、GD-005**。

## Findings

### GD-001 — Replacement change decision order

- Priority: P1
- Status: `resolved`
- Required order: `change create → human decision → accepted → evolve → replacement draft → release`
- Current evidence: sequence、activity 與 L1 state relationship diagram 都先完成 change decision，
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
- Current evidence: sequence、activity 與 L2 state relationship diagram 均明確拆分 prepared
  `status = active`、canonical merge 與 effective authority。
- Governing evidence:
  [`workflow_authoring.py`](../src/trading/core/workflow_authoring.py)、
  [`workflows/README.md`](../workflows/README.md)、
  [`release.md`](../.agents/skills/trading-author-workflow/references/release.md)
- Remaining action: none.

### GD-003 — Study authority gates

- Priority: P1
- Status: `open-partial`
- Already visible: human preregistration、operator/reviewer separation、independent reviewer 與
  terminal outcome。
- Still missing: Development、candidate freeze 與 Evaluation 的 authority 必須分開呈現，不能由
  preregistration 或前一階段推導；reviewer 寫入 terminal outcome 前的 explicit human
  confirmation 與 stable reviewer identity 也尚未明示。
- Governing evidence:
  [`workflow-study-governance.md`](../.agents/rules/workflow-study-governance.md)
- Recommended closure: 在 L3 增加獨立 authority gates，保留 lifecycle state 與 authority grant
  為不同概念。

### GD-004 — Mandatory release guards

- Priority: P1
- Status: `open-partial`
- Already visible: generic `release guards + human approval`、immutable workflow/policy pins，以及
  unfinished studies 在 version boundary 前必須進入安全狀態。
- Still missing: 視覺化尚未逐項呈現 complete self-contained contract、accepted source changes
  與 combined impact、被取代的 exact active version、exact released market/broker/execution/
  portfolio policy pins、normative dependencies 與 pinned reference companions，以及不存在
  unresolved/omitted accepted changes。
- Governing evidence:
  [`release.md`](../.agents/skills/trading-author-workflow/references/release.md)、
  [`impact.md`](../.agents/skills/trading-author-workflow/references/impact.md)
- Recommended closure: 將 `release guards` 展開為一個簡短 checklist 或 guarded decision node；
  不要讓 human approval 看起來是唯一 release gate。

### GD-005 — Activity diagram lifecycle scope

- Priority: P2
- Status: `open-partial`
- Already visible elsewhere: L1–L3 state relationship diagram 已涵蓋 change
  `rejected/deferred/withdrawn`、study pause/cancel/reviewer-return，以及 version
  `abandoned/retired`。
- Still missing: Activity diagram 本身仍只呈現 happy path，但標題仍為「生命週期與治理閘門」，
  容易被理解為完整 lifecycle。
- Governing evidence:
  [`remove.md`](../.agents/skills/trading-author-workflow/references/remove.md)、
  [`workflow-study-governance.md`](../.agents/rules/workflow-study-governance.md)
- Recommended closure: 保持簡圖並將標題改為 `Activity diagram｜Happy-path handoff`，同時指向
  L1–L3 state relationship diagram 作為完整狀態補充；若仍稱 lifecycle，則必須補齊所有分支。

### GD-006 — Stale-preview fail-closed gate

- Priority: P2
- Status: `resolved`
- Required behavior: target drift 或 invalid partial state 必須阻止 apply、保持 zero mutation，
  並要求 fresh preview。
- Current evidence: L1 state relationship diagram 已明示
  `Target drift / invalid partial state → apply blocked → fresh preview`，並標記不留下 mutation。
- Governing evidence:
  [`core.md`](../.agents/skills/trading-author-workflow/references/core.md)
- Remaining action: none. 此 gate 不需重複塞入維持簡化的 happy-path diagram。

## Closure rule

每次更新治理圖後，重新依上述 governing evidence 檢查。只有在視覺化明確呈現要求，或文件
刻意重新界定圖的範圍、避免完整性誤解時，才可將 `open-partial` 改為 `resolved`。狀態變更需同步
更新 Last reviewed、Summary 與對應 finding。
