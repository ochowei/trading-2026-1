# Conclusion: SCHD Down-Streak Mean-Reversion Governance Pilot

## Outcome

`fail`

## Evidence trace

本 study 的 `HYPOTHESIS.md` 與 `PLAN.md` SHA-256 分別為
`ac3fa9d662558d46edad1d74a706f701903cf2ff8f012bab9d6fe7106d240471` 與
`dcba93005ba99a4a8d6c151f3863c876c86e444b967477bce8e9c5282d661e18`，均符合
`PREREGISTRATION.json`。三個 authoritative Development observations 使用相同的 immutable
SCHD data blob `811661a1b18dde967c0d62140f282b6f7f754f642f9f7ad9cf0f707535b427e2`，
cutoff 為 `2025-12-31`，且各 snapshot、definition blob、policy-set identity 與 result
checksum 均通過驗證。

Frozen Development gate artifact
`results/schd-down-streak-reversion--development-gate/s001.json`，SHA-256
`a59c41e54769ff9f1f6d30f8c67f2658b48863f226656cbed6623c3e9997cc7e`，與 raw
daily-equity/trade evidence 的獨立重算一致：

- `two-down` 有 81 筆 completed trades，但 base profit factor `1.0539159077001867` 未嚴格
  高於 `1.10`；stress return `-0.20133431396832968`、stress profit factor
  `0.7094792001828107`、stress drawdown `-0.28037565187637437`，且相對 baseline 的 Sharpe
  margin 僅 `0.042484442105021655`。因此不 eligible。
- `three-down` 有 41 筆 completed trades，但 base return `-0.03609535525498209`、base profit
  factor `0.8797687523770255`、stress return `-0.15461498889040526`、stress profit factor
  `0.5538764368668625`、stress drawdown `-0.22518190454476072`，positive-profit year
  concentration 為 `0.5665875572658093`，且相對 baseline 的 Sharpe margin 為
  `-0.22029904844932404`。因此不 eligible。
- `three-down` base-net Sharpe `-0.10308127233411574` 未嚴格高於 `two-down` 的
  `0.15970221822022995`，monotonic claim 亦失敗。

兩個候選均不 eligible，且 monotonic claim 失敗；依 frozen stopping rule 與 terminal
outcome rules，Development gate 完整且可判定地失敗，必須停止於 `fail`，不得進入 robustness
或 2027–2031 Historical Evaluation。

## Limitations and follow-up

本結論只否證本 research round 的 preregistered claim，並確認治理鏈可依法保留失敗結果；不代表
任何 downstream promotion、broker access、order authorization 或 live-trading authorization。
初次 provider serialization drift 的 observations 已保留但未納入排名；authoritative reruns 使用
相同 immutable data blob，未改變 trial fingerprint 或 frozen design。

另發現 released `WORKFLOW.md` 將 `.agents/rules/execution-model.md`、
`docs/canonical-sleeve-execution.md`、`docs/controlled-followup-cutover.md` 與
`docs/live-drift-and-recovery.md` 列為 normative，但 release metadata 將其列為未 pin SHA-256 的
reference。這是獨立的 workflow dependency-role/release-pinning process defect；它不改變上述可由
preregistered thresholds 與 immutable Development evidence 直接判定的 `fail`。應使用
`trading-author-workflow` 建立 change record 並透過新 workflow version 修正，不得改寫 v001。
