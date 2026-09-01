# 策略前瞻驗證流程

## Purpose and decision

本流程用來判斷：一個只根據固定 `2014-2018` Development 證據選出的日線策略，是否能在相同
workflow-version 日曆下通過固定 `2020-2024` Historical Evaluation、九項獨立 challenge，以及
固定 `2025` retrospective execution replay，得到可重播且跨 study 可比較的歷史研究結論。

本版本只有 `fixed-calendar-retrospective` route。所有 outcome evidence 在 study 建立當下都已
存在，因此 positive terminal disposition 只可為 `retrospectively-supported`。本流程不產生
`shadow-eligible`、`activation-eligible`、Controlled Activation、Active、broker、order 或 live
authority；2025 replay 也不得被稱為 prospective Shadow。更動任何固定日期或恢復 promotion
route，必須建立 accepted workflow change 與下一個 workflow version。

本版本另提供窄化的 append-only qualification-plan abandonment administration。它只處理 exact
bound study 已經 terminal `cancelled`、但 qualification registry 仍留有 unscreened open plan 的
治理分歧。Abandonment 只關閉 single-open-plan administrative lock；它不是 Evaluation、screen、
study outcome、replay、Shadow 或任何 trading authority。

本版本同時對齊 repository 已完成的 legacy experiment retirement：legacy source 與最後 retained
results 只保留作唯讀 archive、歷史重播與既有部位的 fail-closed exit compatibility。Archived
legacy result 不具 current result、selection、qualification、terminal、promotion 或 live authority；
歷史路徑只可經 append-only、digest-identical、最多兩跳的 v009-to-v010 compatibility chain 解析。

## Scope and non-goals

本流程涵蓋一個 experiment family 的單輪固定歷史研究，從預註冊、Development 選擇與
candidate freeze，依序進入 fixed Historical Evaluation、穩健性挑戰、2025 execution replay、
獨立 review 與 terminal outcome。它規範 version-owned calendar、資料來源分類、資料角色、
frozen-plan readiness、決策權限、必要證據及失敗後 successor study 的邊界。

本流程也涵蓋對同一 workflow family 既有 cancelled study 所屬 unscreened plan 的獨立
administrative abandonment。該操作不屬於任何 study execution stage，不會移動、恢復、完成、
評估或重新解讀 owning study。

Legacy experiment retirement 只界定 archive、compatibility resolution 與禁止消費邊界，不建立
study stage。`results/experiment-results/` 已移除且不得重建；retained legacy bytes 的 canonical
terminal location 是唯讀 `legacy/results/<experiment>/`。

本流程不負責：

- 設計或實作策略程式碼、執行個別 study，或替 study 解讀研究結論；
- 定義資料 provider、檔案 schema、CLI 參數或 broker 操作細節；
- 呼叫 broker、提交自動訂單，或把 Historical Evaluation／execution replay 宣稱為實盤授權；
- 以 study cancellation 自動推論 plan 已關閉，或以 plan abandonment 推論 study outcome；
- 恢復 legacy experiment execution、result publication、ranking、qualification、promotion 或
  followup new-entry authority；
- 將策略通過解讀為獲利保證；
- 在 `workflows/` 保存正式結果、原始私有資料、broker export、credentials、個人持倉或
  private ledger。這些內容必須留在各自的 authoritative location，workflow 只記錄精確
  identity 或 link。

新 research definition 的 source 必須位於 `src/trading/research_definitions/`。既有
`src/trading/experiments/` identity 只可作為凍結的 legacy provenance 或 migration input，
不得就地改變研究語意。Source 不複製進 study；正式執行以 immutable Research Definition
Snapshot 保存 exact source、runtime 與 policy-set identity。`legacy/results/` 中的 archive 只能
供明確唯讀診斷、byte-identical historical resolution 或 already-owned position exit compatibility；
不得成為 formal observation、current result validity 或任何新部位的依據。

## Entry conditions and required inputs

一輪研究必須在本 study 的 formal Evaluation／replay outcome 被產生或查看之前開始。已知的
跨 study／legacy outcome exposure 必須如實披露；因本 route 明定為 retrospective，它不會因
新建 study 或更換研究者而恢復 unseen status。Entry conditions 如下：

1. 指定 experiment family、唯一 research-round identity、具穩定識別碼的人類研究負責人，
   以及執行固定 historical replay 的 operator。
2. 取得可驗證的 market-data、snapshot、research-definition 與 trial-registry identities；
   legacy、stale、unreproducible 或 selection history 不完整的資料不得冒充有效證據。
   Research definition 必須綁定本 workflow release 所選的 exact released policy versions；
   缺少、retired、digest drift 或 implicit latest policy 一律不可進入正式執行。
3. Study initialize/preregistration metadata 必須且只能選擇
   `fixed-calendar-retrospective`；release 必須明示 `fixed-calendar-retrospective-v1` capability，
   並提供 structured `QUALIFICATION_SPEC.json`。Caller 不得另傳 route 或 calendar。若既有
   selection history 不完整，必須披露且不得回填；selection boundary 只能是 current-time
   `retrospective_selection_checkpoint`，不得冒充 Forward Selection Epoch。
4. 對固定 `2020-2024` Evaluation 與 `2025` replay 在 formal outcome inspection 前完成
   asset-specific provenance audit，並凍結 exact session inventory：
   - `verified-clean`：append-only evidence 證明 outcome 未影響 family、definition、parameters、
     thresholds、selection 或 interpretation，且相關 trial history 完整；
   - `known-contaminated`：有證據顯示 outcome 曾影響研究；
   - `provenance-unknown`：無法證明乾淨，包括 legacy selection history 不完整。
   缺少證據時一律為 `provenance-unknown`。三種 classification 都不得提升本 route 的
   non-promotional status；即使某資產可證明 `verified-clean`，本版本仍只產生 retrospective
   conclusion。
5. 先完成並由人類研究負責人核准下列 preregistration inputs：
   - 可被否證的研究假說與 falsification conditions；
   - 本版本固定 calendar 的確認，以及 exact session derivation、maximum holding、execution
     lag、dependency purge、embargo 與跨期持倉規則；
   - 有限正整數 `maximum_trials`，以及 trial 的計數規則；
   - 完整候選集合、Development eligibility、唯一候選 selection rule、獨立且較簡單的
     family baseline；
   - base 與 strictly adverse stress cost policies、最大 stress drawdown；
   - Historical、robustness、execution replay、pause 與 technical recovery 的 thresholds、
     checkpoints 和 outcome rules；
   - 每個 auxiliary series 的 publication lag、maximum observation lag，以及 excess lag 採用
     whole-bundle `fail` 或 explicit `mark_unavailable`。選擇後者時必須在 outcome 前凍結全部
     unavailable-decision handling、signal suppression 與 evidence 規則；
   - 哪些 outcome-relevant 變更會建立新 trial、終止本輪或要求完整重啟。

固定日曆是本 workflow contract 的一部分：

| Role | Exact civil-date interval |
| --- | --- |
| Warmup-only | `2013-01-01` through `2013-12-31` |
| Development | `2014-01-01` through `2018-12-31` |
| Quarantine | `2019-01-01` through `2019-12-31` |
| Historical Evaluation | `2020-01-01` through `2024-12-31`; one annual fold per year |
| Retrospective execution replay | `2025-01-01` through `2025-12-31` |

`QUALIFICATION_SPEC.json` 必須在任何 outcome-relevant Development execution 前凍結並由
preregistration pin digest。它至少固定唯一 route、authoritative trial/qualification registry
paths、上述 workflow-calendar identity、完整 family 與各 member source SHA、shared runtime、candidate/baseline roles、
execution dependencies、policies/costs、trial budget、selection-history disclosure、benchmarks、
bootstrap budget/seeds，以及全部 typed challenge targets/gates 與完整 executable challenge
contracts。每個 contract 必須在 outcome inspection 前固定 versioned registered implementation、
source/schema digests、ordered input roles、projection rules、algorithm/parameters/seeds、rounding、
tie handling、event transforms、cost/fill/ledger interaction、raw-evidence requirements、output
metrics 與 failure conditions；method 名稱或 implicit default 不構成可執行語意。Policy contract 必須包含 exact
composite identity 與四個 release/config digests；base/stress cost scenarios 必須列出逐 side
slippage/fee；snapshot/observation contract 必須固定 exact definition binding、Evaluation coverage、
data cutoff、唯一允許的 offline run mode、outcome/validity status 與 observation-time floor。Terminal outcome/disposition
mapping 由本 `WORKFLOW.md` 與 fail-closed terminal validator 固定，不由 caller 或 spec 另傳。
規格不完整時不得 preregister；Development 只能在 preregistration 後另取得具 stable human
identifier 的 add-only `DEVELOPMENT_AUTHORIZATION.json` 才可執行。

Exact-study planner 必須在 registry mutation 前使用 pinned market/session policy，從 workflow
固定 civil dates deterministic derive exact `warmup_sessions`、`development_sessions`、
`quarantined_sessions`、`evaluation_sessions` 與 `replay_sessions`；plan 再凍結完整 inventories。
各 inventory 必須 unique、non-empty、pairwise disjoint 且涵蓋各自固定區間的全部預期 sessions。
Caller-supplied date/year/fold/role override、shortened/shifted interval、missing session、額外 session、
role overlap 或無完整歷史的資產，一律在 outcome execution 前 fail closed。未指派 sessions 必須
明列 quarantined / out of scope，不得自動移入任何計分角色。

每輪可採用更嚴格的門檻，但不得低於以下 floor：

| Gate | 不可放寬的最低要求 |
| --- | --- |
| Development coverage | 固定 2014-2018 五個完整年度；另含固定 2013 warmup |
| Historical Evaluation | 固定 2020-2024 五個完整且互不重疊的 annual folds |
| Historical completed trades | 至少 20 筆 |
| Traded folds | 至少 3 個 |
| Positive traded folds | 至少 60% |
| Base return / profit factor | compounded return 大於 0；profit factor 大於 1.1 |
| Stress return / profit factor | return 大於 0；profit factor 大於 1 |
| Stress drawdown | 不得突破預註冊上限 |
| Fold concentration | 任一 fold 不得超過總交易或總獲利的 50% |
| Selection adjustment | family-wise confidence 至少 90% |
| Execution replay coverage / fills | 2025 全部預期 sessions；至少 12 筆完成 simulated fills |
| Execution replay performance | base 與 stress return 均大於 0、profit factor 均大於 1、stress drawdown 合規，且 historical critical-drift replay 通過 |

唯一候選只可從完整且有效的 Development candidate set 選出。先排除未達預註冊 eligibility
或 risk conditions 的候選，再以 canonical sleeve 的 base-net daily-equity Sharpe 由高至低
排序；完全同分時使用預註冊的穩定 trial ID 順序。獨立 family baseline 不得與 selected
trial 相同。不得使用 legacy Part B、Historical Evaluation 或 execution replay outcome 重新排名。
若任一應納入候選無法驗證，不得產生 partial ranking。

每個曾查看結果且可能影響選擇的 outcome-relevant semantic definition 都算一個 trial，
包括失敗、移除與放棄的版本；相同凍結 definition 的重跑只新增 observation，不另算新
trial。達到 `maximum_trials` 仍無合格候選時，本輪終止且不得增加額度。

## Roles, authority, and responsibility

| Role | Authority and responsibility |
| --- | --- |
| Human workflow release approver | 以穩定 identifier 分別核准 release preparation 與 Workflow Release Activation；不得由 Agent、canonical branch 狀態或 `RELEASE.json` 存在自動推定。 |
| Human research owner | 以穩定 identifier 核准 preregistration、candidate freeze 與每次 stage advancement；可停止研究，但不得覆寫 gate、隱藏 trial 或放寬已凍結規則。 |
| Human qualification-plan abandonment approver | 以新的當下穩定 identifier，核准 exact cancelled owning study 的 exact unscreened plan abandonment 與具體原因；不得把 change acceptance、release、activation 或 study cancellation 當作該操作核准。 |
| Researcher / Agent | 草擬計畫、在 Development 內研究、執行已授權的分析並整理 evidence；不得自行核准晉級、把提案當決策，或接觸後續階段 outcome 來改良候選。 |
| Automated verifier and evidence systems | 從 immutable inputs 重算 identities、metrics 與 gates，保存 append-only evidence，遇到缺漏、衝突或 corruption 時 fail closed；不得接受 caller 自報的 passed flag 取代重算。 |
| Independent reviewer | 不參與 outcome-relevant execution，依 preregistration、frozen plan、typed terminal evidence 與 authoritative registry replay 判定 terminal outcome；不得修補 evidence、調參或創造 disposition。 |
| Historical replay operator | 只可在 candidate freeze 與 Evaluation pass 後執行 frozen 2025 provider-free replay，整理 non-actionable paper evidence；不得接觸 broker、建立 actual position 或擴張 authority。 |

人類核准與系統 gate 缺一不可。人類不能手動把 `fail` 或 `indeterminate` 改為 `pass`；Agent、
研究者、replay operator 與執行系統都不是本流程 release 的 authority。

`Workflow Release Activation` 專指 workflow version 從 prepared release 成為 repository
authority 的治理事件；它不代表任何 strategy activation。v010 study 沒有 strategy activation
state、artifact 或 authority。

## Stages and state transitions

唯一正常 path 為：

```text
planning/preregistration -> development -> candidate-frozen
    -> fixed-historical-evaluation -> retrospective-execution-replay
    -> independent-review -> terminal outcome
```

Qualification-plan abandonment 是正常 study path 之外的 administrative terminal operation；只
適用於 owning study 已經 `cancelled` 的既有 open plan，不會把 study 帶回任何 stage。

Route 與 calendar 不可由 study 改動。任何 stage 都可能進入 `fail`、`indeterminate`、`paused`
或 terminal state；所有 evidence windows 都已完成且固定，因此本版本不允許
`insufficient-evidence`。

### 1. Planning and preregistration

建立全部 required inputs、固定 calendar/session inventories、trial budget、selection rule、
cost/risk assumptions、thresholds 與 authority evidence。缺少任何必要 identity、完整歷史或
核准時不得 preregister 或開始 outcome-relevant work。

### 2. Development and candidate freeze

Development 內可修改 signal、parameters、entry、exit 與 execution assumptions，但每個會
影響選擇的 definition 必須計入 trial history，且所有選擇只能使用 Development evidence。
研究者必須保留完整 candidate set、重要嘗試、失敗原因與選擇 rationale。

依預註冊規則選出至多一個 candidate 與一個不同的較簡單 family baseline。Candidate freeze
必須固定 complete family、trial budget、definition/source/shared-runtime bytes、data-role
calendar、registry identities、policies、costs、execution behavior、metrics、thresholds、
benchmarks、typed challenges、seeds 與 selection boundary，並取得 human research owner
approval；artifact 必須保存 `approved_by`、`approved_at`、exact study/preregistration/spec
digests 與窄化的 `authorization_scope`，才可查看指定 Evaluation。Qualification plan identity
還必須 pin exact Development authorization digest。Freeze 後禁止 tuning、reranking、family
expansion 或 candidate replacement。

`CANDIDATE_FREEZE.json` 不得手寫。Development 先輸出只含 `selected_candidate`、
`family_baseline` 與 ordered `complete_family` 的 selection JSON；每個 member 只含
`source_identity`、`trial_id`、`definition_fingerprint`。Human owner 當下核准後，必須使用
`trading workflow study freeze-candidate --selection ... --approved-by ...` 由 guarded writer
加入 current time、exact study/workflow/preregistration/spec/Development-authorization digests、
fixed narrow scope 與 trial budget，並 add-only 寫入。Caller 不得提供 approval time、scope 或
identity/digest 欄位；同一 exact operation 可 idempotent recovery，不同內容、不同 approver、
不完整 family 或 rewrite 一律 fail closed。

沒有合格 candidate 或 trial budget 用盡時，完整且可信的 Development evidence可由獨立 reviewer
判為 `fail` / `development-selection-failed`，前提是沒有 `CANDIDATE_FREEZE.json`、沒有本 study
的 qualification plan/screen，並由 preregistration 指定 registry 的 tracked content-addressed
absence snapshot 證明 current head。Identity 或 absence proof 不完整時只能是
stage-identified `indeterminate`。

Pre-freeze Markdown evidence 一旦被 immutable candidate freeze 以 digest 引用，必須只存在於
canonical tracked `results/evidence/research/<sha256>.md`；檔名與 bytes 必須相符、不得覆寫、
不得有 mutable alias，且 fresh clone/Git GC 後仍須可驗證與永久保留。已凍結的舊路徑只能經
digest-bound path-migration registry 解析到 byte-identical canonical destination，不得重寫
candidate freeze 或複製第二份 authoritative evidence。

### 3. Frozen fixed-calendar readiness

任何 fixed-calendar plan 在 registry mutation 前，都必須經 provider-free
exact-study compiler 解析 released workflow、preregistration、PLAN、structured qualification
spec、Development authorization、human-approved candidate freeze、exact policies、candidate、
distinct baseline、complete family、trial budget、所有 source/shared-runtime bytes、fingerprints
與 workflow-owned calendar。Public
high-risk path 只接受 exact study path 與必要的人類 operation approval/provenance declaration，
不得讓 caller 替換上述 frozen facts；dry-run 不得寫 registry、建立 observation、執行 definition
或讀取 market outcome。

Complete-family register-only preparation 與 qualification-plan append 是一個 recoverable logical
transaction。它以 current UTC 建立 boundary；缺少的 outcome-free trial identities 使用真實當下
registration time，不得回填，既有 timestamps 不改。Write-ahead journal 是 commit decision，
綁定 exact study、兩個 registry paths、human approver、approval time、contamination declaration
與全部 prepared bytes。Public retry 必須先恢復同一 journal，才能讀取新時間或接受不同操作；
family-universe check、missing registrations 與 plan append 必須在共享 transaction/registry lock
內序列化。Missing/extra/late trial、source/fingerprint/calendar/disclosure mismatch 或 pending
incompatible journal 一律 fail closed。此 readiness stage 不建立 observation，也不授權後續
outcome work。

Qualification plan 同時保存 repository-relative trial/qualification registry identities 與
operational absolute paths；terminal/fresh-clone replay 以 exact repository-relative identity
比對，不得以 absolute-path suffix 或另一 checkout 的 lookalike path 代替。Compiler 必須拒絕
任何與固定 civil dates 或 derived session inventories 不同的 spec／plan。

Backward-compatible tooling 即使可 faithful compile 舊版本 study，也不會把 v008 規則或權限
套到該 study。尤其 v004/S004 仍須 paused、pinned to v004，且只有其 frozen artifacts 加上另行
明確的 study-operation approval 才可能進行 readiness；本版本的任何 lifecycle state 本身都
不會 register、resume、inspect 或 authorize 它。

### 3a. Append-only qualification-plan abandonment

Public operation 只能使用：

```text
trading qualification plan abandon \
  --plan-id <exact-plan-id> \
  --workflow <exact-active-v010-path> \
  --approved-by <stable-human-identity> \
  --reason <concrete-reason>
```

Authorizing workflow version 必須通過 canonical registry/control-state 驗證、是當下 active 且
effective，並由 exact `RELEASE.json` 明列 `qualification-plan-abandonment-v1` capability。僅安裝
shared implementation、change acceptance、draft、prepared release、canonical branch membership
或 owning study cancellation 都不能授權 mutation。v010 可處理同一 workflow family 之較舊
version study 所屬 plan；authorizing workflow family 必須與 exact owning study family 相同。

Caller 只能指定 plan ID、authorizing workflow path、當下 approver 與具體原因。Writer 必須從
已驗證的 qualification registry plan event 取得 experiment family、exact owning study path、
preregistration、plan、candidate-freeze、qualification-spec 與 owning workflow-release SHA-256，
再由 canonical workflow repository 解析該 exact study。Caller 不得提供或替換 owning study
path、status、family、version 或任何 frozen digest。

只有 plan 存在完整 exact-study binding、沒有 `historical_screen`、沒有先前 abandonment，且
owning study status 精確為 terminal `cancelled` 時才可 append。Legacy/unbound、missing、draft、
preregistered、running、paused、awaiting-review、completed、mismatched 或已 screened plan 全部
fail closed。Writer 在 existing qualification-registry lock 下，以 current canonical UTC atomic
append 唯一 `historical_plan_abandoned` event：

```text
historical-plan-abandoned:<plan-id>
```

Payload 必須綁定 plan/family、完整 frozen study identities、canonical cancelled study lifecycle、
exact authorizing workflow path/version/release SHA-256/capability、current approver/time/reason，及
append 前 registry event count/head hash。Event 必須進入既有 canonical hash chain 與 private head
checkpoint，tracked content-addressed qualification evidence snapshot 必須能由 authoritative reader
完整 replay。

Canonical `historical_screen` 或 canonical `historical_plan_abandoned` 任一存在，即關閉該 plan 的
single-open-plan constraint；study cancellation 本身不關閉 plan。Abandoned plan 永久禁止後續
screen、Shadow registration、replay attachment、第二次 abandonment、revival 或 terminal
Evaluation evidence。Abandonment 不建立 passed/failed disposition，不是 `pass`、`fail`、
`insufficient-evidence` 或 `indeterminate`，也不提供 research、promotion 或 operational authority。

### 4. Fixed Historical Evaluation and robustness challenge

Evaluation 固定使用 `2020-2024` 五個完整 annual folds。它是 non-promotional retrospective
evidence；asset-specific provenance classification 必須保存，但不能改變 terminal authority。
Formal observation 使用 immutable snapshots/offline runs；每筆 trade 依 signal date 歸屬並在
同一 fold 內退出。2013 warmup、2014-2018 Development、2019 quarantine 與 2025 replay sessions
不得貢獻 Evaluation signals、positions、fills、cooldown、P&L、capital、benchmark samples 或
metrics。

本 route 不弱化任何 floor：至少 20 completed trades、3 traded folds、60% positive traded
folds、base compounded return > 0、base profit factor > 1.1、stress return > 0、stress profit
factor > 1、stress maximum drawdown 不超過 preregistered limit、任一 fold 不得超過總 trades 或
總 positive profit 的 50%，以及 complete-family block-bootstrap confidence 至少 90%。Required
challenges 包含 cash、distinct simpler baseline、exposure-matched random entries、preregistered
small parameter perturbations、delayed entry、higher costs、worse fills、missed entries 與
market-regime checks。Study-specific gates 可加嚴但不可低於 floor。

每個 challenge 必須凍結 typed gate、exact benchmark/trial/method target、unique evidence identity
與 distinct immutable artifact；review 從 artifact 內綁定 metric/target 的 observed value 重算
gate，不信任 manifest 自報 passed flag。Challenge artifacts 只能由獨立、provider-free、
plan-bound 的 guarded challenge-only operation 產生。Operation 只接受 exact study path、frozen
plan identity 與 plan 要求的 exact family manifests；它從 authoritative registries 為每個 family
member 解析唯一 successful/valid formal Evaluation observation，驗證共同 frozen data generation，
並建立 content-addressed role projection。

Projection 只能讓 exact registered 2020-2024 Evaluation sessions 貢獻 signals、positions、fills、
cooldown、P&L、capital、benchmark samples 或 metrics；Development、quarantine、warmup 與 replay
inventory 只能供 frozen method 明示允許的 dependency，且必須列入 excluded inventory。
Missing/duplicate observation、mixed run modes/generations、incomplete sessions、identity/policy/
fingerprint drift、caller alias、日期／檔名推論或 role leakage 一律 fail closed。

Challenge-only operation 不得呼叫 qualification screen coordinator、provider、refresh、research
definition、trial observation writer、trial/qualification registry writer、terminal review 或任何
study transition。Dry-run 必須完成全部 identity/method/source/projection/path/duplicate/collision
checks 而零 mutation；non-dry-run 在 bounded study/plan lock 下執行各 frozen method 至多一次，
將正好九個 distinct content-addressed artifacts 與一個 manifest stage、驗證並 atomic publish
到 canonical study-evidence namespace。Exact retry idempotent；partial/conflicting/
differently-bound publication fail closed，recovery 只可完成 inputs 完全相同且已 commit 的
publication decision。

Missed-entry contract 必須明示 eligible-entry universe、canonical ordering、selection algorithm、
percentage-to-count rounding、seed/tie handling、zero-selection 與 without-replacement ledger
behavior；worse-fill contract 必須明示 entry/exit transform、tick/precision rounding、gap/intrabar
ambiguity、fee/slippage ordering、unavailable price、unfilled 與後續 capital/position 影響。不得
由 method label 補推語意。九個 artifact 各自綁定 study/spec/freeze/plan/workflow/policies、
implementation、source observations/results/manifests、共同 data generation、exact Evaluation
sessions、metric/observed value/gate 與足以 provider-free replay 的 raw values。

Evaluation screen 任一完整 frozen gate 失敗即為 `fail` 並終止本 study，不得進入 replay；
identity、classification、approval、family、artifact 或 replay integrity 不足為 stage-identified
`indeterminate`。通過只允許進入固定 2025 replay，不產生 `shadow-eligible`。

### 5. Retrospective execution replay

只有 persisted passing fixed Historical Evaluation 才可開始 replay。它不建立 Shadow
registration；guarded operation 綁定 exact study、candidate freeze、plan、passing screen、
workflow/policies、共同 frozen data generation 與完整 `2025-01-01` through `2025-12-31`
session inventory。不得 backdate、改用其他年份、跳過 sessions 或讀取 provider／refresh。

Replay 必須依 session 順序產生 non-actionable paper proposals、canonical simulated fills、
position/cash/ledger events、base/stress metrics、checkpoint prefix 與 historical drift assessment。
它不得建立 broker fills、actual positions、orders、Shadow／activation events 或 new-entry
authority。每個 checkpoint 與 artifact 都必須 content-addressed、append-only、plan-bound，並可
在 fresh checkout provider-free replay。

Public dry-run 完成 identity/session/path/collision checks 而零 mutation。Non-dry-run 在 bounded
study/plan lock 下 stage、驗證並 atomic publish 一份完整 replay evidence set；exact retry
idempotent，partial/conflicting/differently-bound publication fail closed，recovery 只可完成 inputs
完全相同且已 commit 的 publication decision。

Replay 必須涵蓋 2025 全部預期交易 sessions 並至少產生 12 筆 completed simulated fills；base 與
stress return 均大於 0、profit factor 均大於 1、stress drawdown 合規，且 historical
critical-drift replay 通過。因資料區間已完成，fills 不足或任何完整 gate 失敗皆為 `fail`，不得
使用 `insufficient-evidence` 等待、延長或換年；identity/data/evidence integrity 問題為
`indeterminate`。

### 6. Independent terminal review

`TERMINAL_EVIDENCE.json` 必須綁定 preregistration、qualification spec、Development authorization、
candidate freeze、fixed plan、Evaluation screen/challenges、2025 replay evidence、canonical
registry snapshot/head replay、exact workflow/policies、complete commit SHA 與所有 required
digests。獨立 reviewer 必須從 authoritative evidence 重算 outcome，不信任 caller 或 manifest
自報 passed flag。

全部 required identities 與 Evaluation/replay gates 通過時，terminal outcome 為 `pass` +
`retrospectively-supported`；任一完整 frozen gate 失敗為 `fail` 與 stage-specific disposition；
identity、approval、artifact、calendar、provenance 或 replay 不足為 stage-identified
`indeterminate`。Development 無 candidate 使用 `development-selection-failed`。本版本不允許
`insufficient-evidence`，任何結果都不產生 promotion、broker、order 或 live authority。
## Invariants and prohibited behavior

以下規則在所有 stages 都不可覆寫：

1. 每個交易 session 只能有一個資料角色；固定 warmup、Development、quarantine、Evaluation 與
   replay inventories 不得重疊、縮短、平移、補洞或在查看 outcome 後改列。
2. 所有 study 必須使用本 version 的固定 civil dates；caller 不得自訂日期、年份、fold、route
   或替代 calendar。缺少完整歷史的資產不具資格。
3. 曾影響 design、selection、threshold 或 interpretation 的 outcome exposure 必須披露；不得
   宣稱新研究者、新 study 或承諾不重看即可恢復 unseen status。
4. `known-contaminated` 或 `provenance-unknown` 不得 outcome 後改列 `verified-clean`；任何
   provenance classification 都不會授予本 route promotion authority。
5. Warmup 只提供先前 observation；不得把 warmup session、carry-in position 或 fold 外 exit
   計入 Evaluation 或 replay performance。
6. Candidate freeze 後禁止調參、換資料、改 baseline、改 costs、改 success threshold，或用
   Evaluation／replay outcome 重新選冠軍。
7. 所有 outcome-relevant trials、failed observations、tombstones 與 decision rationale 都要
   保留；不得以刪檔、改名或只報 winner 隱藏 selection history。
8. 不得產生 partial ranking；任何應納入 candidate 無效、stale、legacy 或 unreproducible 時，
   selection 必須停止。
9. 門檻可在 outcome 前加嚴，不可低於本 workflow floors，也不可事後放寬或人工例外通過。
10. `retrospectively-supported` 不得映射成 Shadow、activation、broker、order 或 live authority。
11. Evaluation failure 終止本輪；修改後的 candidate 不得重用已查看 evidence 冒充獨立驗證。
12. Outcome-relevant definition change 建立新 trial；freeze 後的 change 終止本 study，不能跨
    fingerprint carry over Evaluation 或 replay qualification。
13. Missing、corrupt、stale、conflicting 或無法重算的 evidence 一律 fail closed，不得以 mutable
    `latest` pointer、人工 assertion 或 synthetic identity 補足。
14. 本流程不得宣稱 `authorized_for_live_orders=true`，不得呼叫 broker、建立 actual positions
    或產生 actionable orders。
15. Append-only evidence、human approvals、timestamps、snapshot IDs、complete commit SHAs 與
    checksums 不得重寫、回填或刪除。
16. Auxiliary maximum lag 仍是硬邊界。預設 excess lag 必須使 bundle fail closed；只有
    preregistered definition 綁定 `us-equity-market@v002` 的 explicit `mark_unavailable` 時，才可
    保留 row 作 audit 並抑制 signal。Unavailable decision 不得產生 candidate 或 trade。
17. Study completion 與 plan registration 必須使用同一 study-registration lock；registration
    進鎖後重讀 freeze/completion state，completion 必須拒絕 pending transaction journal。
18. Qualification snapshots 必須位於 `results/evidence/qualification/<sha256>.json`；
    Development/challenge/replay artifacts 必須位於
    `results/workflows/<workflow>--vNNN/<study>/<stage>/**`，且 tracked bytes 等於 Git index bytes。
19. `STAGES_AND_OUTCOMES.md` 是 pinned explanatory companion；它不能新增、放寬或覆寫本
    `WORKFLOW.md` 的行為與 authority。
20. Canonical result writers 必須使用分類後 namespace。Historical explicit paths 只可經
    `results/registries/path-migrations.json` 的 append-only、SHA-256-bound mapping 解析；v009
    categorized path 最多再接一個 v010 retirement hop，整條 chain 最多兩跳且每一跳必須保持
    original digest。超過兩跳、cyclic、duplicate、missing、untracked、unsafe、artifact-class
    conflict 或 digest drift 一律 fail closed。
    Legacy-result chain 的 artifact class 必須完全相同。Schema-2 registry 唯一允許的
    non-identical class transition 是 v009 `trial-registry` 的 exact categorized path
    `results/registries/trial_registry.json`，轉為 v010 `trial-registry-history` 的 exact
    digest-bound `results/registries/history/trial_registry--<sha256>.json`；其他 cross-class
    transition 一律視為 conflict。這個 historical registry replay 不恢復任何 current authority。
21. Challenge-only authority 必須獨立於 screen、terminal、study transition、provider、research
    execution 與 registry mutation；任何 implicit invocation 或 authority widening 都 fail closed。
22. Registered challenge schemas/implementations、provider-free coordinator、atomic
    publisher/recovery 與 synthetic release tests 必須持續通過；inherited contract 或 change record
    本身不構成 implementation、execution 或 release evidence。
23. Categorized writer cutover、完整 path-migration inventory、每個 destination exact digest、
    fresh-checkout resolution，以及 frozen historical studies 的 byte-identical replay 必須持續
    驗證；不得把 inherited layout contract 當作 migration-completion evidence。
24. Release readiness 必須 provider-free 證明本 v010 的獨立
    `draft -> prepared -> active` Workflow Release Activation、v008 grandfathered attestation、
    prepared-successor action guards、release-safety writers/validator、family action guard 與
    exact-version read-only state query。Draft 或 prepared 狀態不構成 activation evidence。
25. `workflow-release-safety-v1` 只授權受控 writer 建立 add-only
    `work/release-safety/saNNN/ASSESSMENT.json` 與 `CLEARANCE.json`。Caller 不得指定 assessment
    ID、版本 identity、digest 或時間；未關閉 assessment 阻止新的 outcome-relevant work 與
    successor release preparation，但不改寫 study lifecycle 或授予 release/activation authority。
26. `fixed-calendar-retrospective-v1` route/schema、exact-date compiler、calendar-override guards、
    完整 session coverage checks、2025 provider-free replay、atomic publication、terminal mapping
    與 historical compatibility tests 必須持續通過。本文日期本身不構成 implementation、
    execution、validation 或 release evidence。
27. `qualification-plan-abandonment-v1` 只授權 exact active/effective v010 下的 guarded
    administrative writer。它不得由 v009、draft/prepared version、study lifecycle 或 caller
    assertion 推定，也不授權 study execution、Evaluation、screen、replay、Shadow 或 trading。
28. Abandonment 只能跟在 exact-study-bound unscreened plan 與 terminal `cancelled` owning study
    之後。Study cancellation 不會自動關閉 plan；screen 與 abandonment 互斥且都是不可復活的
    plan-terminal facts。
29. Original plan、event hashes、study bytes 與 failed attempts 必須保留。不得刪除 registry、
    fabricate screen、改 family identity、重寫 status、重用 event ID 或放寬 single-open-plan
    invariant 來取代 canonical abandonment。
30. `legacy/results/` 是 terminal read-only archive，`results/experiment-results/` 不得存在或重建。
    Archived result 不得被 freshness、evaluation、ranking、qualification、terminal evidence、
    Shadow/Active、followup new entry 或任何 live path 消費；compatibility read 不恢復 authority。
## Required artifacts and evidence

| Stage | Required artifacts and evidence |
| --- | --- |
| Planning | Research-round identity、human owner approval、hypothesis/falsification、`fixed-calendar-retrospective` route、workflow-calendar identity、`maximum_trials`、candidate inventory、selection rule、baseline、execution dependencies、cost/risk policies、auxiliary excess-lag mode、thresholds、checkpoints 與 outcome rules。 |
| Development | Add-only `DEVELOPMENT_AUTHORIZATION.json`、每個 semantic trial identity、legacy provenance（如有）、composite policy-set identity、immutable data/definition snapshots、formal observations、failed/removed history、unavailable-decision audit 與 signal-suppression proof、Development-only metrics、完整 ranking 與 rationale。 |
| Candidate freeze | Selected trial、distinct baseline、ordered complete family、definition/source/shared-runtime identities、fixed calendar/session inventories、base/stress policies、holding/lag/purge/embargo、全部 gates、stable human approver、current approval timestamp 與窄化 scope。 |
| Frozen readiness | Exact-study compiler output、complete-family identity/source/fingerprint inventory、workflow-owned calendar、五種 exact role inventories、current-time retrospective selection boundary、operation approver、provenance declaration、recoverable journal、dry-run proof 與 canonical pre-freeze evidence digests。 |
| Qualification-plan abandonment | Exact original plan event、complete frozen study identity、canonical terminal `cancelled` owning-study state、active/effective authorizing v010 release/capability、current stable human approver/time/concrete reason、prior registry count/head、canonical abandonment event/hash 與 matching checkpoint/snapshot replay。 |
| Provenance audit | 固定 2020-2024 Evaluation 與 2025 replay sessions 的 `verified-clean`、`known-contaminated` 或 `provenance-unknown` classification、append-only justification、prior exposure、trial-history completeness 與 outcome 前 freeze identity。 |
| Fixed Historical Evaluation | Pinned spec/plan、五個 annual fold/session identities、verified manifests、canonical daily-equity paths、per-fold/chained metrics、完整 family selection adjustment、typed screen gates，以及 guarded atomic publication 的九個 distinct challenge artifacts/manifest。 |
| Retrospective execution replay | Passing Evaluation identity、完整 2025 session inventory、non-actionable proposals、simulated fills、position/cash/ledger events、base/stress metrics、checkpoint prefixes、historical drift assessment、atomic publication journal 與 provider-free replay proof。 |
| Terminal review | `TERMINAL_EVIDENCE.json` 綁定 preregistration、spec、Development authorization、freeze、plan、Evaluation/challenges、2025 replay、qualification snapshot/head replay、workflow/policies、complete commit SHA、required digests、independent conclusion 與 terminal disposition。 |
| Workflow release safety | Draft 接替版下的 immutable `ASSESSMENT.json` 綁定 exact Active 前一版、exact Draft 接替版、接替版 `WORKFLOW.md` digest、blocking Sxxx、缺少的 impact decisions、current UTC 與 actor；相符 `CLEARANCE.json` 綁定 assessment digest、每個 blocking study resolution 及 evidence path/digest。 |

Formal evidence 必須留在 authoritative repository 或 private runtime location；workflow/study
records只保存精確 repository-relative paths、immutable manifest IDs、complete commit SHAs 與
checksums。Mutable `latest` reference 只能作便利 pointer，不能單獨支持決策。

Canonical tracked result namespaces are purpose-owned: workflow-native trial artifacts use
`results/research-trials/<family>/<trial>/`; terminally retired legacy experiment outputs use the
read-only archive `legacy/results/<experiment>/`; parity-linked migration artifacts use
`results/migration-evidence/<experiment>/`; workflow study evidence uses
`results/workflows/<workflow>--vNNN/<study>/<stage>/`; content-addressed evidence uses
`results/evidence/{research,qualification}/`; and registries use `results/registries/`.
`results/experiment-results/` 已移除且不得重建；pure unreferenced legacy history 位於
`legacy/results/<experiment>/history/`。Released workflow 與 frozen study bytes 保持原始 path
strings，並只透過 exact、最多兩跳、same-digest compatibility registry 解析到 terminal bytes。

每個 formal observation 的 immutable Research Definition Snapshot 必須保存所有
outcome-relevant strategy、detector、backtester 與 resolved configuration bytes。若 workflow
release/policy binding 或 run coordination 由 snapshot 外的 maintained orchestration source
決定，evidence 還必須保存那些 exact source bytes 的 content-addressed identities，或保存完整
commit SHA 加上可驗證的 per-file SHA-256 inventory。缺少、漂移或無法 provider-free replay
的 orchestration identity 是 `indeterminate`；只能修復同一 frozen evidence，不得更換策略、
資料、門檻或 selection rule。

Workflow-native formal result 必須在 strategy output inspection 前建立並保存
`metadata.observation_provenance`。該 object 至少包含：canonical application argv（exact
research identity、workflow path、manifest path 與 run mode）、workflow family/version/path、
`RELEASE.json` 與 `WORKFLOW.md` SHA-256、resolved composite policy-set identity、complete Git
HEAD，以及所有決定 workflow binding 或 formal publication 的 maintained orchestration source
之 exact UTF-8 bytes 與 SHA-256。CLI 或 coordinator 不得以 caller assertion、目前 checkout、
implicit latest 或僅有 commit SHA 取代 required exact bytes；任何欄位缺失、無法讀取或 hash
不一致時必須在發布 formal result 前 fail closed。

Historical result JSON 預設遵守 repository 的 local-only boundary，除非 retention policy
明確追蹤該檔案。Tracked snapshot manifests、trial-registry observations 與 study evidence 只保存
其 exact repository-relative path、identity 與 checksum，不得把 mutable result content 或 raw
private data 複製進 `workflows/`。Legacy 與 ordinary experiment results 不得被補上 synthetic
workflow provenance。

## Shared policies and implementation links

本 workflow version 在 release 時必須固定四個 released policy families：
`us-equity-market`、`firstrade-manual-trading`、`canonical-execution` 與 `portfolio-risk`。
Workflow 定義研究 stages 與 gates；policy 定義可重用的市場、broker、execution 與 portfolio
constraints。Workflow 不得覆寫 selected policy configuration；不同規則必須先發布新 policy
version，再由新的 workflow version 明確採用。

執行使用 maintained market-data、research-data、execution、ledger、qualification 與 drift
replay modules。Qualification plan、screen 與 2025 replay 必須原生解析 `src/trading/research_definitions/`
identity、exact policy set 與 definition snapshot，不得依賴 closed legacy experiment registry 或
caller assertion。正式 evidence 必須保存 exact policy releases、composite policy-set identity、
definition snapshot、data snapshot、result identity、complete commit SHA 與 checksum。Ledger 與
drift logic 在本版本只提供 historical simulation mechanics，不得連接 private live state、broker
或 cutover authority。

Workflow release-safety evidence 由 `trading workflow safety assess/clear` 經
`src/trading/workflow/authoring.py` 的共用 authoring lock 產生並驗證；它不改寫 Sxxx lifecycle，
也不提供 release、activation 或 study authority。獨立的 read-only
`trading workflow version state <version-path> [--json]` 只從 canonical registry、release／
activation evidence、release-safety artifacts 與 persisted study lifecycle 推導 exact-version
A1-2 state；它不寫 evidence、不執行 transition，也不能回填 v008 未曾保存的 safety state。

Qualification-plan abandonment authority 由
`src/trading/workflow/qualification_plan_abandonment.py` 解析 exact effective release；
`src/trading/research_data/qualification_registry.py` 在 existing append-only lock/hash/checkpoint
boundary 下驗證與寫入 canonical event；`src/trading/workflow/studies.py` 只提供 canonical
study-lifecycle identity。CLI 或 registry caller 都不得以自報的 active capability、study path 或
cancelled status 取代這些 verified boundaries。

Legacy result compatibility 由 `src/trading/research_data/paths.py` 解析 tracked schema-2
`results/registries/path-migrations.json`。Resolver 只接受 v009/v010、最多兩跳且 original digest
一致的 chain；`legacy/results/` writer 與所有 legacy outcome-relevant public operation維持退役並
fail closed。這個 compatibility seam 只保存 frozen reference replay，不產生 current observation、
qualification、promotion 或 trading authority。

## Outcomes

每個 decision point 使用 repository 的四種 outcome vocabulary，但本 fixed completed-data route
只允許其中三種作為實際結果：

- `pass`：所有必要 identities、approvals、fixed-calendar coverage、Evaluation/challenge gates 與
  2025 replay gates 通過。Terminal positive disposition 只能是 `retrospectively-supported`；
  它沒有 promotion、broker、order 或 live authority。
- `fail`：任一完整且可判定的 frozen gate 未通過、固定 Evaluation trades/folds 不足、2025
  replay 少於 12 completed fills，或 Development 在 trial budget 內找不到合格 candidate。停止
  本輪，不得調整後重用相同 evidence 冒充獨立驗證。
- `insufficient-evidence`：本版本不允許。全部時間窗已完成且不可延長；樣本或 fills 不足是
  frozen gate `fail`，不得等待、補年、換年或降低門檻。
- `indeterminate`：資料、calendar/session identity、artifact、approval、provenance 或 integrity
  不足以可信判定。停止 advancement，直到同一 frozen evidence 被驗證或完整恢復；若無法恢復，
  必須終止或另開 study，不得製造替代證據。

任何人或系統都不得直接寫入 outcome、把 retrospective result 升格，或繞過 evidence-derived
gate。`historical_plan_abandoned` 是 administrative terminal fact，不屬於上述四種 outcome，
不得出現在 study disposition 或充當 terminal Evaluation evidence。
## Pause, recovery, and termination

Data、calendar/session inventory、snapshot、registry、ledger simulation、publication journal、
execution replay、policy binding 或 evidence-integrity failure 必須立即 pause advancement。Pause
不刪除 evidence、不改寫 qualification，也不允許改用其他日期或繼續產生 formal outcome。

Recovery 只可在同一 frozen definition、固定 calendar、exact manifests 與既有 publication
decision 下修復 technical integrity、恢復 idempotent transaction，並重新驗證完整 evidence。
不得新增 sessions、延長 2025、換資料世代、改 threshold、刪除 event 或人工 override。
Outcome-relevant definition change 不屬於 recovery；它終止既有 freeze 並需要新的 trial/study。

本輪在以下情況終止：trial budget 用盡且無 candidate、fixed Evaluation 或 replay `fail`、
策略在 freeze 後被實質修改、required evidence 無法恢復，或 human research owner 明確停止。
終止須保留原因、最後 outcome、identity 與時間。另開 study 仍須使用本版本同一固定 calendar，
並披露所有先前 outcome exposure；不得把重跑宣稱為新的 clean 或 prospective evidence。已終止
qualification 不得以修改狀態復活。

若 exact owning study 已合法成為 terminal `cancelled`，但其 plan 因無 screen 而仍 open，唯一
administrative recovery 是另取當下明確核准後 append canonical abandonment。它不得修復、恢復、
完成或重新判定 study；若 eligibility、identity、capability、approval、reason 或 registry
integrity 任一不足，operation 必須零 mutation fail closed。
## Version boundary

下列 workflow-level 變更需要 accepted change record 與新的 workflow version：

- purpose、scope、stage 順序、state transitions 或 terminal behavior；
- roles、approval authority、human/operator boundaries 或禁止行為；
- 任一固定 civil-date boundary、data-role、non-overlap、non-reuse、warmup、fold、replay year 或
  provenance 規則；
- provenance classification、retrospective checkpoint、non-promotional status 或 authority boundary；
- route discriminator、structured qualification spec、release capability 或 terminal disposition；
- fixed-calendar compiler、complete-family transaction、session coverage 或 evidence-retention boundary；
- trial counting、candidate selection、baseline、required challenges 或 evidence completeness；
- challenge method schema/implementation、Evaluation role projection、challenge-only authority、
  atomic publication/recovery 或 idempotence boundary；
- minimum floors、outcome semantics、pause/recovery 或 replay gates；
- normative dependency 的行為或 identity 發生會影響本流程的變更；
- required observation-provenance schema、capture timing、orchestration source inventory 或
  tracked/local-only evidence boundary；
- categorized result namespace、canonical writer destination、path-migration registry 或 frozen
  historical path-resolution contract；
- legacy archive location、retired-result consumption boundary、migration schema/hop limit 或
  byte-identical retirement rule；
- auxiliary excess-lag mode、unavailable-decision semantics、required audit inventory 或
  signal-suppression proof；
- pinned reference companion 的 meaning、identity 或 release-stability contract。
- qualification-plan terminal vocabulary、eligibility、event payload、capability、authority、
  single-open-plan projection 或 post-abandonment prohibitions。

個別 strategy parameters、signals、data dependencies 或 execution definition 的變更通常只
建立新 experiment trial 或 research round；只要 workflow rules 不變，不需要新的 workflow
version。反之，不得用「只是文件修改」掩飾會改變流程解讀的規則變更。

本 v010 draft 聚合 accepted v009/C001 qualification-plan abandonment 與 accepted v009/C002
legacy experiment retirement contract alignment。兩者 authority 各自獨立，且不會改變 active
v009 或其 studies。v009/S001 與 v009/S002 保持 terminal；
v009/S003 保持 paused，version-boundary decision 為 `restart-on-v010`，不得移動、恢復或改寫。
任何後續 effort 必須在 v010 effective 後建立 next CLI-allocated local study，並以 exact
`revisits` 指向 v009/S003、如實保留 `known-contaminated` disclosure。

對 Active v009 與 Draft v010 的 release-safety assessment，writer 必須配置下一個永不重用的
`SAxxx`，從 repository 取得兩個 exact version paths、v009 `RELEASE.json` digest、v010
`WORKFLOW.md` digest 與 blocking studies 的當下狀態，再以 current UTC 與 stable actor add-only
寫入 `ASSESSMENT.json`。同一版本對已有未關閉 assessment 時不得另開一份。

關閉 assessment 前，每個 blocking study 必須已是 `paused`、`completed` 或 `cancelled`。
Paused study 必須明確選擇 `continue-on-v009`、`restart-on-v010` 或
`close-invalidated`；terminal study 使用 `resolved-terminal`。Guarded clearance writer 必須把
每項 resolution 與 evidence SHA-256 綁入 `CLEARANCE.json`，並引用 exact
`ASSESSMENT.json` digest。任何 identity、digest、status、resolution、唯一性或 evidence 衝突都
使 validator fail closed。只有相符 clearance 建立後，family action guard 與 successor release
check 才可重新評估；它不會自動推進 study、發布或啟用版本。

這套 persistence 由 v009 capability 開始生效，不能回頭假裝 v008 歷史上已保存 assessment。
本 v010 若成為 Active，`workflow-release-safety-v1` 以相同 add-only boundary 治理 v011 與後續
successors；不得回填、猜測或改寫任何先前版本的 safety state。

Released `WORKFLOW.md` 永不可直接編輯。無害勘誤記在 version README 的 Errata，並在後續
版本整合；可能改變解讀的文字修正也必須走 expedited change 與新版本。Reference source 的
後續修改不會自動改變本 workflow。

本 v010 的 workflow release lifecycle 為 `draft -> prepared -> active`。Release preparation
必須取得當下人類核准並產生 immutable `RELEASE.json`；它只把 candidate version 轉為
`prepared`，不得取代既有 active version、把 source change 標為 `released`，或授予 study / formal
execution authority。Prepared successor 存在時，舊 active version 不得建立或 preregister 新
study、開始或恢復 outcome-relevant work、freeze candidate 或開始新的 formal execution。

另一個當下人類核准的 `workflow activate` 操作必須產生不可覆寫的 version-root
`ACTIVATION.json`，記錄 `explicit-workflow-release-activation` basis、stable approver、current UTC
time 與 exact `RELEASE.json` SHA-256。只有此 artifact 與 registry 的 `activation_sha256` 完全一致
時，candidate 才能從 `prepared` 轉為 `active`；同一 transition 才可把 predecessor 轉為
`superseded` 並把 included accepted changes 轉為 `released`。不得 backdate、重寫、刪除、以
canonical branch membership 代替，或只因 `RELEASE.json` 存在就推定 active。

Bootstrap boundary：v009 是最後一個可依 prepared release commit 進入 canonical branch 生效的
version。v008 的 current-time `grandfathered-effective-release` attestation 只證明 migration
時已有效，不回填歷史 activation 時間。本 v010 與後續版本只能使用上述 explicit Workflow
Release Activation，canonical branch membership 或 `RELEASE.json` 存在都不能替代。

## Shared documents and implementation links

| Path | Role | Relationship |
| --- | --- | --- |
| `.agents/rules/execution-model.md` | normative | 非 grandfathered experiment 的 entry/exit、unfilled、fill statistics 與 intrabar assumptions。 |
| `docs/reproducibility.md` | normative | Immutable market-data snapshots、definition identities、formal run modes 與 replay boundary。 |
| `docs/reproducibility-v008.md` | normative | Structured route、Development/candidate authority、exact session derivation與 tracked terminal evidence 的 v008 addendum。 |
| `docs/auxiliary-unavailable-decision-reproducibility.md` | normative | Explicit unavailable auxiliary decision 的 manifest wire identity、audit inventory、replay 與 signal-suppression proof。 |
| `docs/result-validity-and-trial-history-v005.md` | normative | Result validity、完整 candidate set、append-only trial history、retrospective evidence role 與 formal ranking evidence。 |
| `docs/canonical-sleeve-execution.md` | normative | Capital constraint、event ordering、base/stress costs、daily equity 與 canonical ranking metric。 |
| `docs/historical-qualification-and-shadow-v008.md` | normative | Exact-study readiness、frozen selection boundaries、screen replay 與 evidence mechanics；其 caller-selected calendar、prospective Shadow 與 promotion semantics 不適用於 v010。 |
| `docs/historical-qualification-and-shadow-v009.md` | normative | Complete executable challenge contracts、exact Evaluation role projection、independent guarded challenge-only operation、atomic publication/recovery 與 release-readiness boundary。 |
| `docs/historical-qualification-and-shadow-v010.md` | normative | Exact active-release capability、cancelled-study binding、canonical abandonment event、single-open-plan closure 與 unchanged outcome/Shadow/live-authority boundary。 |
| `docs/controlled-followup-cutover.md` | reference | 只供 historical ledger/parity mechanics 參考；Active promotion、position ownership 與 order authority 不適用於 v010 study。 |
| `docs/live-drift-and-recovery.md` | reference | 只供 2025 historical drift replay mechanics 參考；不建立 prospective monitoring 或 recovery authority。 |
| `docs/result-storage-layout-v009.md` | normative | v009 categorized result namespaces、第一跳 migration 與未被 v010 retirement successor 取代的 storage/evidence rules。 |
| `docs/legacy-experiment-retirement-v010.md` | normative | Terminal read-only legacy archive、已移除 categorized legacy-result path、同 digest 最多兩跳 resolution，以及 archived result 的 non-authority boundary；在這些主題上取代 v009 storage 文件。 |
| `docs/market-data.md` | reference | Provider/cache、session validation、declared dependencies 與 as-of availability implementation。 |
| `docs/manual-execution-ledger.md` | reference | Private manual position authority、accounting integrity 與 broker reconciliation implementation。 |
| `docs/research-evidence-preservation.md` | reference | Content-addressed pre-freeze/qualification evidence、logical transaction 與 fresh-clone implementation boundary。 |
| `docs/strategy-forward-replication-research-workflow.md` | reference | `v001` 的 document-led source；保留作 authoring provenance，不與本 contract 共同成為雙重 authority。 |
| `workflows/strategy-forward-replication-research--v008/STAGES_AND_OUTCOMES.md` | pinned reference | 同時提供精簡白話版與完整版的 stage/outcome 解說；本文件仍是唯一 workflow behavioral authority。 |

若本文件與 repository guardrail 或 normative dependency 衝突，停止執行並將衝突視為
`indeterminate` authoring/validation issue；不得自行選擇較寬鬆的規則。
