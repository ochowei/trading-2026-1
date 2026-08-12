# Hypothesis: SCHD Down-Streak Mean-Reversion Governance Pilot

## Claim

在 `SCHD` 日線中，連續三個完成交易日收跌，比連續兩日收跌提供更高品質的短期均值回歸
條件。訊號在收盤後成立，下一個 XNYS session 開盤進場，持有五個完整 sessions 後於下一個
開盤出場。在 2023–2025 Development evidence 中，`three-down` 的 canonical base-net
daily-equity Sharpe 必須嚴格高於 `two-down`，且至少一個候選必須通過所有預註冊的
Development eligibility gates 並顯著優於不同且較簡單的 `periodic-baseline`，假說才獲得
Development 支持。

若 Development 支持假說，依唯一 selection rule 選出的 candidate 還必須在預先保留、未用於
設計的 2027–2031 annual Historical Evaluation folds 中，通過 released workflow 的全部
Historical、benchmark、family-wise selection-adjustment 與 robustness gates，才可判為
`pass`。此處的 `pass` 只代表 `shadow-eligible`；本 pilot 不註冊 Shadow、不啟用策略、不接觸
broker，也不授權 live orders。

## Decision relevance

本研究主要驗證 workflow-first governance 與 immutable evidence chain，而不是尋找漂亮績效。
若 Development gate 失敗，這個 research round 立即停止並保留合法的 `fail` evidence。若
Development gate 通過，只有在人類 owner 核准 candidate freeze 後，才可建立 future-only
Historical plan；Historical pass 只支援另行考慮 prospective Shadow 的決策。

## Falsification conditions

以下任一情況即否證本輪 claim 或阻止晉級：

- `three-down` 的 Development base-net Sharpe 不嚴格高於 `two-down`；
- 兩個候選都未通過全部 Development eligibility gates；
- 完整候選或 baseline 的 data、definition、policy、snapshot、result 或 trial history 無法驗證；
- selected candidate 在任何 frozen Historical、benchmark、selection-adjustment 或 robustness
  gate 失敗；
- 達到 `maximum_trials=5` 仍無合格 candidate；
- preregistration 後需要改 ticker、資料角色、候選集合、selection rule、costs、thresholds、
  stopping rule 或 outcome rule。

最後一項不允許就地修補；必須取消本 study，另建帶精確 `revisits` 的 study。
