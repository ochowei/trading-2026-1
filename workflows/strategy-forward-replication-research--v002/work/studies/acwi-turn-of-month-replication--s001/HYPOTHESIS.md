# Hypothesis: ACWI Turn-of-Month Replication

## Claim

ACWI 有可重現的 turn-of-month cash-flow effect：在只使用 2009-2020 Development
evidence、完整比較三個事先限定的月末 entry offsets，並依凍結規則選出唯一 candidate 後，
該 candidate 在 2021-2025 五個互不重疊 annual Historical Evaluation folds 中，使用
`strategy-forward-replication-research@v002` 固定的 canonical execution、base/stress costs
與 isolated sleeve，會同時：

1. 產生正的 base 與 stress compounded return；
2. 通過 workflow 的 profit-factor、drawdown、fold coverage、concentration 與 family-wise
   selection-adjustment gates；
3. 嚴格勝過 cash、相同持有期的 mid-month baseline，以及 exposure-matched random entries；
4. 在 holding-period、entry-delay、missed-entry 與 cost challenges 下保留正的 stress return
   且不突破凍結的 stress drawdown 上限。

這是 calendar/cash-flow anomaly replication，不主張任何特定 candidate 一定勝出，也不主張
通過 Historical Evaluation 等同未來獲利、Shadow 通過或 live-trading authorization。

## Decision relevance

本 study 判斷 `acwi-turn-of-month` 是否能在 workflow-first architecture 下成為第一個正式
Stage 3 workflow-native family，並取得 `shadow-eligible` 資格。`pass` 只允許日後另行註冊
prospective Shadow；不建立 broker fill、不送出訂單、不授權 Active promotion。

若 Development 找不到 eligible candidate，或完整 Historical/robustness evidence 否證 claim，
本輪終止。失敗後不得調整 offset、baseline、dates、costs 或 gates，再重用 2021-2025 作為
同一 claim 的 validation evidence。

## Falsification conditions

下列任一可完整判定的情況即否證本輪 claim：

- 三個 Development candidates 在凍結的 `maximum_trials` 內皆不符合 eligibility；
- selected candidate 的 Development base-net daily-equity Sharpe 未嚴格高於 distinct
  mid-month baseline 至少 `0.15`；
- selected candidate 在 Historical Evaluation 未達五個完整 folds、20 筆 completed trades、
  三個 traded folds 或 60% positive traded folds；
- 任一凍結的 base/stress return、profit factor、stress drawdown、fold concentration、cash、
  baseline、random-entry、family-wise confidence 或 robustness gate 失敗；
- trial budget 用盡仍無 candidate，或完整 evidence 顯示 turn-of-month timing 沒有相對於
  mid-month exposure 的可辨識優勢。

Identity、approval、data、snapshot、checksum、完整 family universe 或 reproducibility 缺失時，
結果是 `indeterminate` 而不是對經濟假說的支持。`insufficient-evidence` 不適用於本 study 的
固定 Development/Historical stages；它只可能用於本 study scope 之外、日後另行註冊的
prospective Shadow。
