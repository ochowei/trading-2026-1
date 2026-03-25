# TQQQ 實驗總覽 (TQQQ Experiment Index)

> **最新實驗 (Latest):** TQQQ-004 `tqqq_cap_vix_filter`
> **當前最佳 (Best):** _尚未評估 — 執行 `uv run trading run --all` 後更新此處_

## 實驗清單 (Experiments)

| ID       | 資料夾                     | 說明                                   | 關鍵差異                | 狀態     |
|----------|---------------------------|----------------------------------------|------------------------|----------|
| TQQQ-001 | `tqqq_capitulation`       | 基礎版：三條件恐慌抄底 + 冷卻機制        | 基線                    | ✅ 基線  |
| TQQQ-002 | `tqqq_cap_relaxed_entry`  | 放寬進場門檻，收緊停損                   | DD -12%, RSI<30, Vol 1.3x, SL -6% | ✅ 完成  |
| TQQQ-003 | `tqqq_cap_wider_exit`     | 加寬獲利目標 +12%，追蹤停利 -4%          | TP +12%, 持倉 12 天, Trailing -4%  | ✅ 完成  |
| TQQQ-004 | `tqqq_cap_vix_filter`     | 加入 VIX ≥ 25 過濾，僅在真正恐慌時進場   | VIX ≥ 25 額外條件       | 🆕 最新  |

## 演進路線 (Lineage)

```
TQQQ-001 tqqq_capitulation (基礎版：DD -15%, RSI<25, Vol 1.5x)
├── TQQQ-002 tqqq_cap_relaxed_entry  (放寬進場 + 收緊停損)
├── TQQQ-003 tqqq_cap_wider_exit     (加寬出場 + 追蹤停利)
└── TQQQ-004 tqqq_cap_vix_filter     (加入 VIX 恐慌過濾)
```

## 參數對照 (Parameter Comparison)

| 參數              | TQQQ-001 | TQQQ-002 | TQQQ-003 | TQQQ-004 |
|-------------------|----------|----------|----------|----------|
| Drawdown          | -15%     | **-12%** | -15%     | -15%     |
| RSI(5)            | < 25     | **< 30** | < 25     | < 25     |
| Volume            | 1.5x     | **1.3x** | 1.5x     | 1.5x     |
| VIX Filter        | —        | —        | —        | **≥ 25** |
| Profit Target     | +5%      | +5%      | **+12%** | +5%      |
| Stop Loss         | -8%      | **-6%**  | -8%      | -8%      |
| Holding Days      | 7        | 7        | **12**   | 7        |
| Trailing Stop     | —        | —        | **-4%**  | —        |
| Cooldown Days     | 3        | **5**    | 3        | 3        |

## 實驗結論 (Key Findings)

### Part A — In-Sample (2019-01-01 ~ 2023-12-31)

| ID       | 訊號數 | 勝率   | 平均報酬 | 累計報酬  | 最大回撤 | 結論   |
|----------|-------|--------|---------|----------|---------|--------|
| TQQQ-001 | —     | —      | —       | —        | —       | 基線   |
| TQQQ-002 | —     | —      | —       | —        | —       | 待測試 |
| TQQQ-003 | —     | —      | —       | —        | —       | 待測試 |
| TQQQ-004 | —     | —      | —       | —        | —       | 待測試 |

### Part B — Out-of-Sample (2024-01-01 ~ 2025-12-31)

| ID       | 訊號數 | 勝率   | 平均報酬 | 累計報酬  | 最大回撤 | 結論   |
|----------|-------|--------|---------|----------|---------|--------|
| TQQQ-001 | —     | —      | —       | —        | —       | 基線   |
| TQQQ-002 | —     | —      | —       | —        | —       | 待測試 |
| TQQQ-003 | —     | —      | —       | —        | —       | 待測試 |
| TQQQ-004 | —     | —      | —       | —        | —       | 待測試 |

> **目前結論：** _尚未評估 — 執行 `uv run trading run --all` 後填入結果並更新此處。_

<!-- 更新指引：
  1. 執行 uv run trading run --all
  2. 執行 uv run trading compare tqqq_capitulation tqqq_cap_relaxed_entry tqqq_cap_wider_exit tqqq_cap_vix_filter
  3. 將關鍵數字填入上方表格（訊號數、勝率、平均報酬%、累計報酬%、最大回撤%）
  4. 更新「結論」欄、「目前結論」與頂部的「當前最佳」
-->
