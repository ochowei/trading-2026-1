Run daily Trading Followup report for pre-market order planning: $ARGUMENTS

No arguments required. If $ARGUMENTS contains a ticker, filter the output for that asset only (informational — the full report still runs).

---

## Step 1: Run the followup report

```bash
uv run trading followup
```

Display the **full output** to the user — it contains:
- T-Day Order Sheet (consolidated order list)
- Trading Followup Summary (action overview)
- Per-asset signal details and open positions
- Firstrade order instructions

---

## Step 2: Highlight actionable items

After the full report, produce a concise action summary:

```
## 今日操作摘要 (Today's Action Summary)

### 需要執行的操作 (Actions Required)
- [ ] <action 1 — e.g., "開盤前: BUY TQQQ MARKET Day">
- [ ] <action 2 — e.g., "成交後: SELL TQQQ LIMIT $XX.XX Day">
- ...

### 無需操作的標的 (No Action)
- <TICKER>: 無訊號
- ...

### 提醒事項 (Reminders)
- LIMIT SELL 為 Day 單，每日需重新掛單
- 請依實際成交價重新計算目標價與停損價
```

If there are NO orders at all, simply state:

```
## 今日操作摘要 (Today's Action Summary)

今日無任何操作。所有策略均無觸發訊號，亦無未結部位需處理。
No actions today. No signals triggered and no open positions to manage.
```

---

## Important

- This skill is READ-ONLY for code — it does NOT modify any files
- If the report shows errors (e.g., failed to fetch data), flag them clearly
- If it's a weekend or US market holiday, note that the data may not have updated and the "T day" shown may not be the next actual trading day
