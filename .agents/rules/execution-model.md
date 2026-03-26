# 回測與實盤貼近原則（成交模型）

## 舊實驗既往不咎（Grandfathered）

既有實驗不強制回補成交模型，可維持原始回測邏輯與既有結果，以保留歷史可比性。

既往不咎的實驗編號：`TQQQ-001` ~ `TQQQ-009`

若未來 `EXPERIMENTS_TQQQ.md` 新增編號，預設不自動納入既往不咎，需在本規範明確追加後才生效。

## 新實驗強制納入成交模型

自本規範更新後，所有新建實驗必須在回測中明確定義並實作成交模型，不可再默認「訊號必成交」。

至少需包含：

1. **進場模式**（例如 `next_open_market` 隔日開市市價 / `next_open_limit` 隔日開市限價）
2. **出場模式**（基於 Firstrade 支援之功能，例如 `limit_order` / `stop_market` / `stop_limit` / `trailing_stop` / `next_open_market`）
3. **未成交處理**（模擬限價單/停損單未觸價之情況，例如 Day 當日有效收盤取消、GTC 取消前有效遞延至隔日、或視為錯失機會）
4. **成交統計**（至少揭露 filled / unfilled 數量與成交率）
5. **日內路徑假設 (Intrabar Assumption)**：若同時使用「限價/觸價進場」與「盤中觸價出場」，必須明確定義日 K 線內觸發先後順序（建議採取**悲觀認定 Pessimistic Execution**：若最高與最低價皆穿越限價與停損價，強制假定發生最差虧損結果）

## 文件同步要求

新實驗若引入成交模型，必須同步更新 `EXPERIMENTS_TQQQ.md` 或 `EXPERIMENTS_GLD.md` 的實驗說明與參數/假設描述，確保讀者可辨識其與舊實驗的差異。
