# 策略前瞻驗證流程

## Purpose and decision

本流程用來判斷：一個只根據 Development 證據選出的日線策略，是否能在研究當下先以
time-ordered retrospective Evaluation 得到誠實而完整的歷史研究結論，或沿 promotion route
取得未受污染的 clean Historical 與 prospective Shadow 證據，成為受控啟用候選並在啟用後
繼續接受 fail-closed 監測。

每個 study 在 preregistration 前必須選擇 route。`study-time-retrospective` 可在當下既有歷史
資料內完成 Development、candidate freeze、較晚的 retrospective Evaluation 與 terminal
review；通過只記錄 `retrospectively-supported`。Promotion route 則可先使用 optional
retrospective-confirmatory checkpoint，再依序回答能否成為 `shadow-eligible`、
`activation-eligible` 與受控 `Active` 策略。Retrospective 通過不是晉級資格；每次其他通過也
只授予明定的下一階段資格，不保證未來獲利或授權真實／自動下單。

## Scope and non-goals

本流程涵蓋一個 experiment family 的單輪研究，從 route selection、預註冊、Development
選擇與 candidate freeze，分流至 terminal `study-time-retrospective`，或 optional
retrospective-confirmatory、clean Historical Evaluation、穩健性挑戰、prospective Shadow、
受控啟用及 Active drift pause/recovery。它規範資料來源分類、資料角色、frozen-plan readiness、
決策權限、必要證據、terminal outcome，以及失敗後 successor study 的邊界。

本流程不負責：

- 設計或實作策略程式碼、執行個別 study，或替 study 解讀研究結論；
- 定義資料 provider、檔案 schema、CLI 參數或 broker 操作細節；
- 呼叫 broker、提交自動訂單，或將回測及 Shadow 結果宣稱為實盤授權；
- 將策略通過解讀為獲利保證；
- 在 `workflows/` 保存正式結果、原始私有資料、broker export、credentials、個人持倉或
  private ledger。這些內容必須留在各自的 authoritative location，workflow 只記錄精確
  identity 或 link。

新 research definition 的 source 必須位於 `src/trading/research_definitions/`。既有
`src/trading/experiments/` identity 只可作為凍結的 legacy provenance 或 migration input，
不得就地改變研究語意。Source 不複製進 study；正式執行以 immutable Research Definition
Snapshot 保存 exact source、runtime 與 policy-set identity。

## Entry conditions and required inputs

一輪研究必須在任何 Evaluation outcome 被查看或用於選擇之前開始，並滿足以下 entry
conditions：

1. 指定 experiment family、唯一 research-round identity、具穩定識別碼的人類研究負責人，
   以及預期進入受控啟用時的 operator。
2. 取得可驗證的 market-data、snapshot、research-definition 與 trial-registry identities；
   legacy、stale、unreproducible 或 selection history 不完整的資料不得冒充有效證據。
   Research definition 必須綁定本 workflow release 所選的 exact released policy versions；
   缺少、retired、digest drift 或 implicit latest policy 一律不可進入正式執行。
3. Study 必須在 initialize/preregistration metadata 明確選擇 route；本 release capability
   範圍內的 `clean-historical`、`retrospective-confirmatory` 與
   `study-time-retrospective` 都必須提供 structured `QUALIFICATION_SPEC.json`。只有 release 明示
   `study-time-retrospective-v1` capability 時才可選擇
   `study-time-retrospective`；不得以字串、日期或 caller assertion 推測 capability。若既有
   selection history 不完整，必須如實披露，不得回填或宣稱舊 history 完整。Clean Historical
   使用 future-only Forward Selection Epoch；retrospective-confirmatory 與
   study-time-retrospective 各自使用 current-time `retrospective_selection_checkpoint`，不得
   冒充 clean selection boundary。
4. 對每個擬用 evaluation period 在 outcome inspection 前完成 asset-specific clean-evidence
   audit，並凍結 exact session inventory：
   - `verified-clean`：append-only evidence 證明 outcome 未影響 family、definition、parameters、
     thresholds、selection 或 interpretation，且相關 trial history 完整；
   - `known-contaminated`：有證據顯示 outcome 曾影響研究；
   - `provenance-unknown`：無法證明乾淨，包括 legacy selection history 不完整。
   缺少證據時一律為 `provenance-unknown`。只有 `verified-clean` 可成為 clean Historical；
   另外兩類只能是 Development context、retrospective-confirmatory 或
   study-time-retrospective evidence。
5. 先完成並由人類研究負責人核准下列 preregistration inputs：
   - 可被否證的研究假說與 falsification conditions；
   - Development、Historical Evaluation 與 Shadow 的資料角色和時間邊界；
   - warmup、maximum holding、execution lag、dependency purge、embargo，以及跨期持倉規則；
   - 有限正整數 `maximum_trials`，以及 trial 的計數規則；
   - 完整候選集合、Development eligibility、唯一候選 selection rule、獨立且較簡單的
     family baseline；
   - base 與 strictly adverse stress cost policies、最大 stress drawdown；
   - 是否使用 retrospective checkpoint，以及 retrospective、Historical、robustness、Shadow、
     pause 與 recovery 的 thresholds、checkpoints 和 outcome rules；
   - 每個 auxiliary series 的 publication lag、maximum observation lag，以及 excess lag 採用
     whole-bundle `fail` 或 explicit `mark_unavailable`。選擇後者時必須在 outcome 前凍結全部
     unavailable-decision handling、signal suppression 與 evidence 規則；
   - 哪些 outcome-relevant 變更會建立新 trial、終止本輪或要求完整重啟。

每個 route 的 `QUALIFICATION_SPEC.json` 必須在任何 outcome-relevant Development execution
前凍結並由 preregistration pin digest。它至少固定 route、authoritative trial/qualification
registry paths、whole-year Development/quarantine/Evaluation calendars 與 exact warmup bounds、
warmup/quarantine、完整 family 與各 member source SHA、shared runtime、candidate/baseline roles、
execution dependencies、policies/costs、trial budget、selection-history disclosure、benchmarks、
bootstrap budget/seeds，以及全部 typed challenge targets/gates。Policy contract 必須包含 exact
composite identity 與四個 release/config digests；base/stress cost scenarios 必須列出逐 side
slippage/fee；snapshot/observation contract 必須固定 exact definition binding、Evaluation coverage、
data cutoff、唯一允許的 offline run mode、outcome/validity status 與 observation-time floor。Terminal outcome/disposition
mapping 由本 `WORKFLOW.md` 與 fail-closed terminal validator 固定，不由 caller 或 spec 另傳。
規格不完整時不得 preregister；Development 只能在 preregistration 後另取得具 stable human
identifier 的 add-only `DEVELOPMENT_AUTHORIZATION.json` 才可執行。

每個非預設 chronology 的 route 都必須凍結 explicit role calendar。Retrospective-confirmatory
可表達 completed Development context 位於 Evaluation 之後；clean Historical 可表達已
preregistered 的非標準但仍 chronological Development、quarantine、warmup 與 future Evaluation
邊界；`study-time-retrospective` 則強制 Development 嚴格早於 Evaluation。Calendar 包含至少
三個完整連續 Development 年、exact warmup start/end、明示 quarantine 年，以及至少五個
complete annual Evaluation folds。Exact-study planner 必須在 registry mutation 前，使用 pinned
market/session policy 從這些 frozen inputs deterministic derive exact `development_sessions`、
`warmup_sessions`、`quarantined_sessions` 與 `evaluation_sessions`；plan 再凍結完整 session
inventories。各 inventory 必須 unique、non-empty 且 pairwise disjoint；未指派 sessions 必須明列
為 quarantined / out of scope。不得由 Evaluation 年份反推、默默改用 preceding-three-year
convention，或製造與 preregistration 不符的 Development evidence。

每輪可採用更嚴格的門檻，但不得低於以下 floor：

| Gate | 不可放寬的最低要求 |
| --- | --- |
| Development coverage | 至少 3 個完整連續年度，另含指標所需 warmup |
| Historical Evaluation | 至少 5 個完整、連續且互不重疊的 annual folds |
| Historical completed trades | 至少 20 筆 |
| Traded folds | 至少 3 個 |
| Positive traded folds | 至少 60% |
| Base return / profit factor | compounded return 大於 0；profit factor 大於 1.1 |
| Stress return / profit factor | return 大於 0；profit factor 大於 1 |
| Stress drawdown | 不得突破預註冊上限 |
| Fold concentration | 任一 fold 不得超過總交易或總獲利的 50% |
| Selection adjustment | family-wise confidence 至少 90% |
| Shadow duration / fills | 至少 252 個完成交易日及 12 筆完成 simulated fills |
| Shadow performance | base 與 stress return 均大於 0、profit factor 均大於 1、stress drawdown 合規，且 critical drift assessment 通過 |

唯一候選只可從完整且有效的 Development candidate set 選出。先排除未達預註冊 eligibility
或 risk conditions 的候選，再以 canonical sleeve 的 base-net daily-equity Sharpe 由高至低
排序；完全同分時使用預註冊的穩定 trial ID 順序。獨立 family baseline 不得與 selected
trial 相同。不得使用 legacy Part B、Historical Evaluation 或 Shadow outcome 重新排名。
若任一應納入候選無法驗證，不得產生 partial ranking。

每個曾查看結果且可能影響選擇的 outcome-relevant semantic definition 都算一個 trial，
包括失敗、移除與放棄的版本；相同凍結 definition 的重跑只新增 observation，不另算新
trial。達到 `maximum_trials` 仍無合格候選時，本輪終止且不得增加額度。

## Roles, authority, and responsibility

| Role | Authority and responsibility |
| --- | --- |
| Human research owner | 以穩定 identifier 核准 preregistration、candidate freeze 與每次 stage advancement；可停止研究，但不得覆寫 gate、隱藏 trial 或放寬已凍結規則。 |
| Researcher / Agent | 草擬計畫、在 Development 內研究、執行已授權的分析並整理 evidence；不得自行核准晉級、把提案當決策，或接觸後續階段 outcome 來改良候選。 |
| Automated verifier and evidence systems | 從 immutable inputs 重算 identities、metrics 與 gates，保存 append-only evidence，遇到缺漏、衝突或 corruption 時 fail closed；不得接受 caller 自報的 passed flag 取代重算。 |
| Independent reviewer | 不參與 outcome-relevant execution，依 preregistration、frozen plan、typed terminal evidence 與 authoritative registry replay 判定 terminal outcome；不得修補 evidence、調參或創造 disposition。 |
| Manual trading operator | 在 activation-eligible 之後檢查 lifecycle、data、ledger、reconciliation、allocation、drift 與 no-new-entry 狀態；只透過受控 manual path 管理啟用、暫停及既有部位。不得以 operator 動作改寫研究資格。 |

人類核准與系統 gate 缺一不可。人類不能手動把 `fail` 或 `insufficient-evidence` 改為
`pass`；Agent、研究者、operator 與執行系統都不是本流程 release 的 authority。

## Stages and state transitions

兩條正常 path 為：

```text
planning/preregistration -> development -> candidate-frozen
    -> study-time-retrospective-evaluation -> independent-review -> terminal outcome

planning/preregistration -> development -> candidate-frozen
    -> [optional retrospective-confirmatory -> retrospectively-supported]
    -> clean-historical-evaluation -> shadow-eligible
    -> shadow -> activation-eligible -> controlled-activation -> active-monitoring
```

Route 在 preregistration 後不可改。任何 stage 都可能進入 `fail`、`indeterminate`、`paused`
或 terminal state；固定 completed Historical/retrospective checkpoint 不可使用
`insufficient-evidence`，只有 Shadow 或其他明確開放、持續累積的 prospective checkpoint 可用。

### 1. Planning and preregistration

建立全部 required inputs、資料角色、trial budget、selection rule、cost/risk assumptions、
thresholds 與 authority evidence。缺少任何必要 identity 或核准時維持 `indeterminate`，
不得開始能影響後續選擇的正式 evaluation。

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

### 3. Frozen qualification readiness

任何 clean Historical 或 retrospective plan 在 registry mutation 前，都必須經 provider-free
exact-study compiler 解析 released workflow、preregistration、PLAN、structured qualification
spec、Development authorization、human-approved candidate freeze、exact policies、candidate、
distinct baseline、complete family、
trial budget、所有 source/shared-runtime bytes、fingerprints 與 exact role calendar。Public
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
比對，不得以 absolute-path suffix 或另一 checkout 的 lookalike path 代替。

Backward-compatible tooling 即使可 faithful compile 舊版本 study，也不會把 v008 規則或權限
套到該 study。尤其 v004/S004 仍須 paused、pinned to v004，且只有其 frozen artifacts 加上另行
明確的 study-operation approval 才可能進行 readiness；本版本的任何 lifecycle state 本身都
不會 register、resume、inspect 或 authorize 它。

### 4. Optional retrospective-confirmatory checkpoint

所有資產均可選用本 checkpoint。它使用 candidate freeze 後才第一次依 frozen checkpoint plan
檢視的 completed-data outcomes，但不宣稱那些資料未污染。Plan 必須在 outcome 前以獨立的
`retrospective_selection_checkpoint` 凍結 exact candidate、distinct baseline 與有限 trial
family；該 checkpoint 不得冒充 future-only Forward Selection Epoch。Plan 同時凍結年度
non-overlapping folds、warmup、purge、embargo、execution dependencies、canonical sleeve、
base/stress costs、seeds、thresholds、stopping rules 與完整 challenge set。

Retrospective plan 可使用 explicit role calendar 表達非標準 chronology，包括已完成且較晚的
Development context。Development sessions 只作 governance、selection provenance 與 context，
不得加入 retrospective return、trade、benchmark 或 family-wise adjustment series；warmup-only
sessions 只供 indicator/dependency 計算，不得產生 signal、fill、cooldown、position、P&L 或
performance。Partial overrides、role overlap、不完整 Development 年度、warmup 不足、warmup
不早於 Evaluation，或 route discriminator 不一致，一律在 registry mutation 前 fail closed。
未使用 explicit calendar 的既有 plan 保持原 payload 與 deterministic identity；explicit clean
calendar 則只可依 preregistered future chronology 使用，不能借用本段的 nonstandard chronology。

Challenge 至少包括 cash、baseline、exposure-matched random entries、完整 family-wise selection
adjustment、小幅 parameter perturbation、延後 entry、較高 costs、較差 fills、漏單、fold/trade/
profit concentration 與適用 market regimes。規則強度不得低於同 study 凍結的 Historical gates。

For every family-wise selection adjustment, the production evaluator must consume the one selection boundary
frozen by the plan: `forward_selection_epoch` for clean Historical evidence or
`retrospective_selection_checkpoint` for retrospective-confirmatory evidence. When prior selection history is
incomplete, the evaluator must verify that boundary's disclosure, exact included trial universe, selected trial,
and each trial's registration timestamp against `started_at` or `frozen_at` respectively. A retrospective
checkpoint remains distinct from a future-only Forward Selection Epoch and never grants clean-evidence or
promotion authority. Release validation must exercise this registration-to-adjustment path provider-free;
registration-only or coordinator-only coverage is insufficient.

全部必要 gates 通過只記錄 `retrospectively-supported`。它不是 Historical pass，不能減少任何
future Historical fold、trade、benchmark、robustness 或 integrity requirement，也不能註冊
Shadow。任一完整 gate 失敗終止本 candidate；evidence 不完整為 `indeterminate`。若 outcome
影響 definition、baseline、threshold 或 interpretation，修改後研究必須建立新 trial/study，
且已查看期間對該 lineage 成為 Development context。

### 5. Study-time retrospective Evaluation and terminal review

本 route 專門回答「candidate 在 study 建立當下已存在、但未能證明 verified-clean 的較晚歷史
區間是否仍站得住腳」。Development 必須嚴格早於 Evaluation；retrospective interval 固定為
`known-contaminated` 或 `provenance-unknown`，新研究者、新 study 或承諾不重看舊結果都不能
升級 provenance。Evaluation 必須是至少五個完整連續 annual folds，使用 immutable snapshots
與 formal offline runs，且所有 trade 必須依 signal date 歸屬並在 fold 內退出。

本 route 不弱化任何 floor：至少 20 completed trades、3 traded folds、60% positive traded
folds、base compounded return > 0、base profit factor > 1.1、stress return > 0、stress profit
factor > 1、stress maximum drawdown 不超過 preregistered limit、任一 fold 不得超過總 trades 或
總 positive profit 的 50%，以及 complete-family block-bootstrap confidence 至少 90%。Required
challenges 包含 cash、distinct simpler baseline、exposure-matched random entries、preregistered
small parameter perturbations、delayed entry、higher costs、worse fills、missed entries 與
market-regime checks。Study-specific baseline margins、binding requirements、drawdown limit 與
challenge gates 可加嚴但不可低於 floor。

每個 challenge 必須凍結 typed gate、exact benchmark/trial/method target、unique evidence identity
與 distinct immutable artifact；review 從 artifact 內綁定 metric/target 的 observed value 重算
gate，不信任 manifest 自報 passed flag。Terminal `TERMINAL_EVIDENCE.json` 必須綁定同一 study
的 preregistration、qualification spec、candidate freeze、exact plan、唯一 canonical
`historical-screen:<plan-id>`、14 個 shared screen gates 與九個 required challenges。它引用的
tracked content-addressed qualification snapshot 必須來自 preregistered authoritative registry
path，保存 exact head/checkpoint，並由正式 registry reader 重播 hash chain/schema；duplicate、
noncanonical 或無法 replay 的 plan/screen fail closed。之後 mutable registry append 不得改變
已凍結 terminal evidence。

獨立 reviewer 只能作以下 terminal mapping：全部 required identities/gates 通過為 `pass` +
`retrospectively-supported`；完整 screen 有 frozen gate 失敗為 `fail` +
`retrospective-screen-failed`；Development 無 candidate 的特殊 fail 使用上一節規則；identity、
classification、approval、family、artifact 或 replay 不足為 stage-identified `indeterminate`。
固定歷史 checkpoint 不允許 `insufficient-evidence`，trades/folds 不足是 gate `fail`。任何結果
都不產生 `shadow-eligible`、`activation-eligible`、Active、broker、order 或 live authority。

若之後需要 promotion evidence，必須建立下一個 CLI-allocated successor study 並記錄 exact
`revisits` path；先前 study 與已查看 outcomes 全部成為 Development context。Successor 必須
獨立 preregister，保留更晚、未使用且有 append-only proof 的 `verified-clean` Evaluation，
不得 relabel 或重用原 retrospective interval。

### 6. Clean Historical Evaluation and robustness challenge

Historical Evaluation 只使用 audit 為 `verified-clean` 的至少五個 annual non-overlapping
folds。Default chronology 使用 Evaluation 前三個完整 consecutive Development years；若 study
已 preregister nonstandard chronological boundary，則可用 explicit clean calendar 完整保留更長
Development、warmup、quarantine 與 future Evaluation inventories，禁止 implicit reassignment。
每筆 trade 歸屬於其
signal date 所在 fold，必須在同一 fold 內完成 exit；purge 與 embargo 必須涵蓋 holding 與
execution dependencies。可讀取較早資料計算 warmup，但那些 sessions 不得計入 Evaluation
performance，也不得帶入 Development 中已開立的 position。

凍結 candidate 必須在 canonical isolated sleeve 下分別用 base 與 stress costs 重算。
Evidence 同時呈現每個 fold、zero-signal folds、跨完整 Evaluation sequence 的 chained
capital path、drawdown、profit factor、trade/profit concentration 與所有 preregistered gates。

Required challenge set 至少包括：

- cash、不同且較簡單的 family baseline、exposure-matched random entries；
- family-wise block-bootstrap selection adjustment，涵蓋完整 trial family；
- 預註冊的小幅 parameter perturbation、延後一個 session、較高 costs、較差 fills、漏單與
  market-regime checks。

Challenges 只能否證或支持原 candidate，不得產生替換 candidate。全部必要 gates 通過後，
outcome 只是 `shadow-eligible`；任一凍結 gate 失敗即為 `fail`。若 evidence 不完整或無法
驗證則為 `indeterminate`，只可修復同一 immutable evidence，不得更換資料或規則。

Historical outcome 一經查看，該資料即視為本輪已使用。失敗後不得修改成新策略再用同一
Evaluation data 證明它；下一輪可把舊資料納入 Development，但必須保留更晚且未被使用的
Evaluation evidence。

### 7. Prospective Shadow

只有 persisted passing clean Historical Screen 才能正式註冊 Shadow。Retrospective-confirmatory
或 study-time screen、disposition、terminal pass 都不得作為 registration source。Registration 必須以當下
UTC 建立，綁定 selected trial、immutable definition、cost policies、prospective start、
activation checkpoint 與 exact historical evidence；不得 backdate。Registration 前的資料，
包括 legacy Part C，不得算入 Shadow。

Shadow 只產生 non-actionable paper proposals 與 canonical simulated fills，不建立 broker
fills 或 actual positions。Checkpoints、session cutoffs、proposal/fill history 必須單調增加且
保留 exact prefix。Definition、cost 或 outcome-relevant execution behavior 改變時，本輪
Shadow 終止，新 definition 必須建立新 trial 並從完整 qualification 重新開始，舊 Shadow
evidence 不得 carry over。

到達 checkpoint 且所有 gates 通過時，outcome 只是 `activation-eligible`。已滿最低等待時間
但 completed fills 不足時為 `insufficient-evidence`：維持原 definition 並繼續等待，不得降低
門檻。Performance 或其他 frozen gate 失敗為 `fail`；identity、data 或 evidence integrity
問題為 `indeterminate` 並停止 advancement。

### 8. Controlled activation

`activation-eligible` 不等於 Active 或新進場授權。受控 promotion 還必須驗證 exact Shadow
registration 與 activation-evaluation events、current valid-result fingerprint、passing data
access parity、frozen drift envelope、verified ledger、current broker reconciliation、allocation
epoch 及所有 Phase 7/8 guards。

只有 manual operator 可執行受控 activation。Activation 不會自動關閉 global
no-new-entry；operator 必須另行檢查狀態並明確開啟 intended control window。任何 missing、
stale、rewritten 或 contradictory evidence 都阻止 new BUY。Verified existing-position SELL
與原定退出管理使用獨立 safety path。

### 9. Active monitoring

Active strategy 必須持續接受 frozen predictive envelope 與 hard guards 監測。Drift overlay
使用 `Healthy`、`Watch`、`Paused`：Watch 加強監測但仍受全部 entry guards 約束；Paused 或任何
active hard guard 一律阻止 new BUY。缺少或樣本不足的 scheduled checkpoint 是 fail-closed
Watch evidence，而不是正常狀態。

Data、ledger、reconciliation、execution、stress-risk 或 critical/persistent drift failure 必須
立即 pause new entries。既有 position 仍依其 verified original target、stop、trailing stop 與
expiry 規則管理，不得因 pause 失去退出責任。

## Invariants and prohibited behavior

以下規則在所有 stages 都不可覆寫：

1. 同一輪中每個交易 session 只能有一個資料角色；Development、Historical Evaluation 與
   Shadow 不得重疊或在查看 outcome 後改列。
2. 曾影響 design、selection、threshold 或 interpretation 的資料，不得再宣稱為該 definition
   的 validation evidence。
3. `known-contaminated` 或 `provenance-unknown` 不得 outcome 後改列 `verified-clean`；研究者未
   閱讀 legacy 文件、不同研究者執行或新建 study 都不能恢復 unseen status。
4. Warmup 只提供先前 observation；不得把 warmup session、carry-in position 或 fold 外 exit
   計入 Evaluation performance。
5. 每個 explicit clean 或 retrospective role calendar 的 Development、warmup-only、quarantine
   與 Evaluation inventories 必須完全分離；任何 route、chronology 或 inventory 與
   preregistration 不一致時不得註冊 plan。
6. Candidate freeze 後禁止調參、換資料、改 baseline、改 costs、改 success threshold，或用
   Evaluation/Shadow outcome 重新選冠軍。
7. 所有 outcome-relevant trials、failed observations、tombstones 與 decision rationale 都要
   保留；不得以刪檔、改名或只報 winner 隱藏 selection history。
8. 不得產生 partial ranking；任何應納入 candidate 無效、stale、legacy 或 unreproducible 時，
   selection 必須停止。
9. 門檻可在 outcome 前加嚴，不可低於本 workflow floors，也不可事後放寬或人工例外通過。
10. Retrospective status 不得映射成 Historical/Shadow/activation status 或 live authority。
11. Historical failure 終止本輪；修改後的 candidate 不得重用已查看的 Historical evidence。
12. Outcome-relevant definition change 建立新 trial；Shadow 或 Active qualification 不得跨
   fingerprint carry over。
13. Missing、corrupt、stale、conflicting 或無法重算的 evidence 一律 fail closed，不得以 mutable
   `latest` pointer、人工 assertion 或 synthetic identity 補足。
14. 本流程及 Phase 6 evidence 不得宣稱 `authorized_for_live_orders=true`，也不得呼叫 broker。
15. Append-only evidence、human approvals、timestamps、snapshot IDs、complete commit SHAs 與
   checksums 不得重寫、回填或刪除。
16. Auxiliary maximum lag 仍是硬邊界。預設 excess lag 必須使 bundle fail closed；只有
    preregistered definition 綁定 `us-equity-market@v002` 的 explicit `mark_unavailable` 時，才可
    保留該 backward-as-of row 作 audit 並將 decision 標記 unavailable。Unavailable decision
    不得產生 signal、candidate 或 trade，也不得被 silent drop、視為 current 或 outcome 後重列。
17. Study completion 與 plan registration 必須使用同一 study-registration lock；registration
    進鎖後重讀 freeze/completion state，completion 必須拒絕 pending transaction journal。刪除
    candidate-freeze file 不得抹除 append-only plan history。
18. Qualification snapshot publisher 必須證明實際 registry path 等於 repository root 加上
    preregistered source identity；qualification snapshots 必須位於
    `results/evidence/qualification/<sha256>.json`，Development/challenge artifacts 必須位於
    `results/workflows/<workflow>--vNNN/<study>/<stage>/**`，且 tracked bytes 必須等於 Git index
    bytes。
19. `STAGES_AND_OUTCOMES.md` 是 pinned explanatory companion；它不能新增、放寬或覆寫本
    `WORKFLOW.md` 的行為與 authority。
20. Canonical result writers 必須使用分類後 namespace。Historical explicit paths 只可經
    `results/registries/path-migrations.json` 的單跳、append-only、SHA-256-bound mapping 解析；
    chained、cyclic、duplicate、missing、untracked 或 digest-drifted mapping 一律 fail closed。

## Required artifacts and evidence

| Stage | Required artifacts and evidence |
| --- | --- |
| Planning | Research-round identity、human owner approval、hypothesis/falsification、data-role calendar、`maximum_trials`、candidate inventory、selection rule、baseline、execution dependencies、cost/risk policies、auxiliary excess-lag mode、thresholds、checkpoints 與 outcome rules。 |
| Development | Add-only `DEVELOPMENT_AUTHORIZATION.json`、每個 workflow-native semantic trial identity、legacy provenance（如有）、composite policy-set identity、immutable data/definition snapshot、formal observation、failed/removed history、每個 explicit unavailable decision 的 session/observation/available-session/actual-lag inventory、signal-suppression proof、Development-only metrics、完整 candidate ranking 與 selection rationale。 |
| Candidate freeze | Selected trial 與 distinct baseline identities、definition fingerprint/blob、data declarations、base/stress policies、holding/lag/purge/embargo、全部 gates，以及 stable human approver、approval timestamp 與窄化 scope。 |
| Frozen readiness | Exact-study compiler output、complete-family identity/source/fingerprint inventory、explicit calendar/quarantine、current-time selection boundary、operation approver、contamination declaration、recoverable journal state、dry-run proof，以及 canonical pre-freeze evidence digests。 |
| Clean-evidence audit | 每段 proposed Evaluation session 的 `verified-clean`、`known-contaminated` 或 `provenance-unknown` 分類、append-only justification、trial-history completeness 與 outcome 前 freeze identity。 |
| Retrospective confirmatory | Retrospective plan ID、`retrospective_selection_checkpoint`、classification、explicit Development/warmup/Evaluation role calendar（非標準 chronology 時）、annual folds、verified manifests、canonical paths、per-fold/chained metrics、完整 benchmarks/selection adjustment/robustness、gate results，以及非晉級 disposition。 |
| Study-time retrospective | Pinned `QUALIFICATION_SPEC.json`、earlier Development/later Evaluation calendar、authoritative registry paths、candidate freeze、current-time checkpoint、immutable manifests/offline observations、typed 14-gate screen、九個 distinct challenge artifacts、qualification snapshot/head replay、`TERMINAL_EVIDENCE.json` 與 terminal disposition。 |
| Historical Evaluation | Clean plan ID、`verified-clean` proof、annual fold/session identities、verified manifests、canonical daily-equity paths、per-fold 與 chained metrics、cash/baseline/random evidence、family selection adjustment、robustness tests、gate results與 disposition。 |
| Shadow | Historical source events、Shadow registration、immutable definition identity、prospective paper proposals、simulated fills、monotonic checkpoints、base/stress metrics、critical-drift assessment 與 activation evaluation。 |
| Controlled activation | Exact Shadow/evaluation/result/parity identities、frozen predictive envelope、lifecycle proof、verified ledger accounting hash、broker reconciliation、allocation epoch、data cutoff/bundle identity 與 operator reason。 |
| Monitoring and decisions | Drift observations/checkpoints、hard guards、Healthy/Watch/Paused state、pause/recovery evidence，以及每次 pass、fail、insufficient-evidence、indeterminate、activation、retirement 與 termination 的 human/system identities和 timestamps。 |

Formal evidence 必須留在 authoritative repository 或 private runtime location；workflow/study
records只保存精確 repository-relative paths、immutable manifest IDs、complete commit SHAs 與
checksums。Mutable `latest` reference 只能作便利 pointer，不能單獨支持決策。

Canonical tracked result namespaces are purpose-owned: workflow-native trial artifacts use
`results/research-trials/<family>/<trial>/`; retained legacy experiment outputs use
`results/experiment-results/<experiment>/`; parity-linked migration artifacts use
`results/migration-evidence/<experiment>/`; workflow study evidence uses
`results/workflows/<workflow>--vNNN/<study>/<stage>/`; content-addressed evidence uses
`results/evidence/{research,qualification}/`; and registries use `results/registries/`. Pure
unreferenced legacy history belongs under `legacy/results/<experiment>/history/`. Released workflow
and frozen study bytes keep their original path strings and resolve them only through the exact
digest-bound compatibility registry.

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

執行使用 maintained market-data、research-data、execution、ledger、qualification、cutover 與
drift modules。Qualification plan 與 screen 必須原生解析 `src/trading/research_definitions/`
identity、exact policy set 與 definition snapshot，不得依賴 closed legacy experiment registry 或
caller assertion。正式 evidence 必須保存 exact policy releases、composite policy-set identity、
definition snapshot、data snapshot、result identity、complete commit SHA 與 checksum。

## Outcomes

每個 decision point 只能產生以下四種 outcome 之一：

- `pass`：所有必要 identities、approvals 與 frozen gates 都通過。它只允許進入明定的下一
  stage；兩種 retrospective pass 都只記錄 `retrospectively-supported`，clean Historical pass 是
  `shadow-eligible`，Shadow pass 是 `activation-eligible`。
- `fail`：任一完整且可判定的必要 gate 未通過，或 Development 在 trial budget 內找不到合格
  candidate。Study-time route 分別記錄 `development-selection-failed` 或
  `retrospective-screen-failed`；本輪 candidate 停止，不得調整後重用相同 validation evidence。
- `insufficient-evidence`：只有規則明確允許繼續累積 prospective evidence 的 open stage 才能
  使用，主要是未達 Shadow minimum fills 或尚未成熟的 monitoring checkpoint。Definition 與
  gates 保持凍結並繼續等待；它不得替代 fixed Historical 或 retrospective gate 的失敗。
- `indeterminate`：資料、identity、artifact、approval 或 integrity 不足以可信判定。停止晉級
  與 new entries，直到同一 evidence 被驗證或完整恢復；若無法恢復，不得製造替代證據，必須
  終止或重啟。Explicit `mark_unavailable` 缺少 immutable policy/manifest binding、完整 session
  inventory 或 signal-suppression proof 時亦為 `indeterminate`，不得產生 partial ranking。

任何人或系統都不得直接寫入 outcome 以繞過 evidence-derived gate。

## Pause, recovery, and termination

下列情況立即 pause advancement 或 new entries：evidence integrity 失敗、資料不完整或 stale、
ledger/reconciliation 不一致、risk hard guard、critical drift、兩次連續 scheduled Watch，或
其他 normative dependency 規定的 fail-closed guard。Pause 不會刪除證據、改寫 qualification
或放棄既有部位管理。

一般 drift recovery 必須在 pause 後、同一 frozen definition 下累積至少 126 個完成 sessions、
6 筆完成 Shadow/paper trades、清除所有 hard guards，並連續兩個 scheduled checkpoints 回到
normal。若 pause 原因僅限 data、ledger 或 reconciliation integrity，可使用 normative technical
contract 的 expedited path：完成 reconciliation、pause 後兩次獨立 clean checks，且沒有 active
hard guard；不得藉此豁免 performance、signal、execution、utilization、concentration 或 stress
risk pause。

Recovery 必須由 append-only evidence 推導，不能編輯 state、刪除 event、改 threshold 或人工
override。Outcome-relevant definition change 不屬於 recovery；它建立新 trial 並重走完整
Historical 與 Shadow qualification。

本輪在以下情況終止：trial budget 用盡且無 candidate、terminal study-time conclusion、
retrospective/Historical/Shadow `fail`、策略在 freeze 後被實質修改、required evidence 無法
恢復，或 human research owner 明確停止。終止須
保留原因、最後 outcome、identity 與時間。若另開下一輪，舊 Evaluation 或 Shadow evidence 可
成為新的 Development context，但必須另留更晚且未被使用的 validation data。已終止的
qualification 不得以修改狀態復活。

## Version boundary

下列 workflow-level 變更需要 accepted change record 與新的 workflow version：

- purpose、scope、stage 順序、state transitions 或 terminal behavior；
- roles、approval authority、human/operator boundaries 或禁止行為；
- data-role、non-overlap、non-reuse、warmup、fold 或 contamination 規則；
- clean-evidence classification、retrospective checkpoint、其 status 或 promotion boundary；
- route discriminator、structured qualification spec、release capability 或 terminal disposition；
- frozen-plan compiler、complete-family transaction、explicit clean calendar 或 evidence-retention
  boundary；
- trial counting、candidate selection、baseline、required challenges 或 evidence completeness；
- minimum floors、outcome semantics、pause/recovery 或 activation gates；
- normative dependency 的行為或 identity 發生會影響本流程的變更；
- required observation-provenance schema、capture timing、orchestration source inventory 或
  tracked/local-only evidence boundary；
- categorized result namespace、canonical writer destination、path-migration registry 或 frozen
  historical path-resolution contract；
- auxiliary excess-lag mode、unavailable-decision semantics、required audit inventory 或
  signal-suppression proof；
- pinned reference companion 的 meaning、identity 或 release-stability contract。

個別 strategy parameters、signals、data dependencies 或 execution definition 的變更通常只
建立新 experiment trial 或 research round；只要 workflow rules 不變，不需要新的 workflow
version。反之，不得用「只是文件修改」掩飾會改變流程解讀的規則變更。

Released `WORKFLOW.md` 永不可直接編輯。無害勘誤記在 version README 的 Errata，並在後續
版本整合；可能改變解讀的文字修正也必須走 expedited change 與新版本。Reference source 的
後續修改不會自動改變本 workflow。Draft 只有在取得當下人類 release approval、產生完整
release evidence，且其 commit 合併 canonical branch 後才有效。

## Shared documents and implementation links

| Path | Role | Relationship |
| --- | --- | --- |
| `.agents/rules/execution-model.md` | normative | 非 grandfathered experiment 的 entry/exit、unfilled、fill statistics 與 intrabar assumptions。 |
| `docs/reproducibility.md` | normative | Immutable market-data snapshots、definition identities、formal run modes 與 replay boundary。 |
| `docs/reproducibility-v008.md` | normative | Structured route、Development/candidate authority、exact session derivation與 tracked terminal evidence 的 v008 addendum。 |
| `docs/auxiliary-unavailable-decision-reproducibility.md` | normative | Explicit unavailable auxiliary decision 的 manifest wire identity、audit inventory、replay 與 signal-suppression proof。 |
| `docs/result-validity-and-trial-history-v005.md` | normative | Result validity、完整 candidate set、append-only trial history、retrospective evidence role 與 formal ranking evidence。 |
| `docs/canonical-sleeve-execution.md` | normative | Capital constraint、event ordering、base/stress costs、daily equity 與 canonical ranking metric。 |
| `docs/historical-qualification-and-shadow-v008.md` | normative | Exact-study readiness、explicit clean/retrospective calendars、study-time terminal route、frozen selection boundaries、screen replay、Shadow guards 與 activation eligibility。 |
| `docs/controlled-followup-cutover.md` | normative | Lifecycle、parity、Active promotion、no-new-entry、position ownership 與 order-authorization boundary。 |
| `docs/live-drift-and-recovery.md` | normative | Frozen predictive envelope、Healthy/Watch/Paused overlay、hard guards 與 evidence-derived recovery。 |
| `docs/result-storage-layout-v009.md` | normative | Categorized result namespaces、append-only path migration、historical compatibility resolution、writer cutover 與 retention boundary。 |
| `docs/market-data.md` | reference | Provider/cache、session validation、declared dependencies 與 as-of availability implementation。 |
| `docs/manual-execution-ledger.md` | reference | Private manual position authority、accounting integrity 與 broker reconciliation implementation。 |
| `docs/research-evidence-preservation.md` | reference | Content-addressed pre-freeze/qualification evidence、logical transaction 與 fresh-clone implementation boundary。 |
| `docs/strategy-forward-replication-research-workflow.md` | reference | `v001` 的 document-led source；保留作 authoring provenance，不與本 contract 共同成為雙重 authority。 |
| `workflows/strategy-forward-replication-research--v008/STAGES_AND_OUTCOMES.md` | pinned reference | 同時提供精簡白話版與完整版的 stage/outcome 解說；本文件仍是唯一 workflow behavioral authority。 |

若本文件與 repository guardrail 或 normative dependency 衝突，停止執行並將衝突視為
`indeterminate` authoring/validation issue；不得自行選擇較寬鬆的規則。
