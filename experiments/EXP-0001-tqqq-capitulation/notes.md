# EXP-0001 TQQQ Capitulation Buy

## Purpose
把既有 TQQQ 恐慌抄底回測包裝為可追蹤、可比較的標準化實驗單位。

## Entry Criteria
同時滿足以下條件：
1. 從 20 日高點回撤達閾值（`drawdown_threshold`）
2. RSI(5) 低於閾值（`rsi_threshold`）
3. 成交量高於 20 日均量倍數（`volume_multiplier`）

## Exit Criteria
1. 停損：收盤價觸發 -8%
2. 達標：盤中高點觸發 +5%
3. 到期：最長持有 7 個交易日

## Current Limitations
- 尚未加入交易成本與滑價模型。
- 單一標的事件驅動策略，尚未納入資金配置/風險預算。

## Next Iteration Ideas
- 嘗試提升績效
