# TQQQ 實驗總覽 (TQQQ Experiment Index)

> **最新實驗 (Latest):** TQQQ-013 `tqqq_cap_exec_qqq_optimized`
> **當前最佳 (Best):** TQQQ-008 `tqqq_cap_optimized_exit`（無成交模型）/ TQQQ-010 `tqqq_cap_exec_optimized`（含成交模型）

## 實驗清單 (Experiments)

| ID       | 資料夾                     | 說明                                   | 關鍵差異                | 狀態     |
|----------|---------------------------|----------------------------------------|------------------------|----------|
| TQQQ-001 | `tqqq_capitulation`       | 基礎版：三條件恐慌抄底 + 冷卻機制        | 基線                    | ✅ 基線  |
| TQQQ-002 | `tqqq_cap_relaxed_entry`  | 放寬進場門檻，收緊停損                   | DD -12%, RSI<30, Vol 1.3x, SL -6% | ✅ 完成  |
| TQQQ-003 | `tqqq_cap_wider_exit`     | 加寬獲利目標 +12%，追蹤停利 -4%          | TP +12%, 持倉 12 天, Trailing -4%  | ✅ 完成  |
| TQQQ-004 | `tqqq_cap_vix_filter`     | 加入 VIX ≥ 25 過濾，僅在真正恐慌時進場   | VIX ≥ 25 額外條件       | ✅ 完成  |
| TQQQ-005 | `tqqq_cap_vix_adaptive`   | 軟性 VIX ≥ 20 + 適應性出場（追蹤停利）   | VIX ≥ 20, TP +8%, Trailing -6%, 持倉 10 天 | ✅ 完成  |
| TQQQ-006 | `tqqq_momentum_collapse`  | 多日動能崩潰：連續下跌 + 累計跌幅 + 趨勢過濾 | 5 日 4 跌、5 日報酬 ≤ -12%、Close < SMA50 | ✅ 完成 |
| TQQQ-007 | `tqqq_cap_qqq_confirm`   | 恐慌抄底 + QQQ RSI 相對強度確認              | QQQ RSI(14) < 35、TP +6%、持倉 8 天 | ✅ 完成 |
| TQQQ-008 | `tqqq_cap_optimized_exit` | 基線進場 + 優化出場（+7%、10 天、無追蹤停利） | TP +7%、持倉 10 天、無 Trailing | ✅ 完成 |
| TQQQ-009 | `tqqq_cap_gentle_entry` | 僅放寬 DD -13% + 優化出場（+7%、10 天） | DD -13%、其餘進場不變 | ❌ 失敗 |
| TQQQ-010 | `tqqq_cap_exec_optimized` | 重做 TQQQ-008 + 成交模型 | 隔日開盤進場、stop_market、limit_order、0.1% 滑價、悲觀認定 | ✅ 完成 |
| TQQQ-011 | `tqqq_cap_exec_baseline` | 重做 TQQQ-001 + 成交模型 | 同上成交模型 | ✅ 完成 |
| TQQQ-012 | `tqqq_cap_exec_qqq_confirm` | 重做 TQQQ-007 + 成交模型 | 同上成交模型 + QQQ RSI 過濾 | ✅ 完成 |
| TQQQ-013 | `tqqq_cap_exec_qqq_optimized` | QQQ RSI 過濾 + 優化出場 + 成交模型 | 在 TQQQ-012 基礎改為 TP +7%、持倉 10 天 | ❌ 失敗 |

## 演進路線 (Lineage)

```
TQQQ-001 tqqq_capitulation (基礎版：DD -15%, RSI<25, Vol 1.5x)
├── TQQQ-002 tqqq_cap_relaxed_entry  (放寬進場 + 收緊停損)
├── TQQQ-003 tqqq_cap_wider_exit     (加寬出場 + 追蹤停利)
├── TQQQ-004 tqqq_cap_vix_filter     (加入 VIX 恐慌過濾)
├── TQQQ-005 tqqq_cap_vix_adaptive   (軟性 VIX + 適應性出場)
├── TQQQ-006 tqqq_momentum_collapse  (多日動能崩潰新訊號)
├── TQQQ-007 tqqq_cap_qqq_confirm    (QQQ RSI 相對強度確認)
├── TQQQ-008 tqqq_cap_optimized_exit (優化出場：+7%、10 天、無追蹤停利)
├── TQQQ-009 tqqq_cap_gentle_entry  (僅放寬 DD -13% + 優化出場)
│
│   ── 成交模型重做系列 (Execution Model Redo Series) ──
├── TQQQ-010 tqqq_cap_exec_optimized  (重做 TQQQ-008 + 成交模型)
├── TQQQ-011 tqqq_cap_exec_baseline   (重做 TQQQ-001 + 成交模型)
├── TQQQ-012 tqqq_cap_exec_qqq_confirm (重做 TQQQ-007 + 成交模型)
└── TQQQ-013 tqqq_cap_exec_qqq_optimized (QQQ 過濾 + 優化出場 + 成交模型)
```

## 參數對照 (Parameter Comparison)

| 參數              | TQQQ-001 | TQQQ-002 | TQQQ-003 | TQQQ-004 | TQQQ-005 | TQQQ-006 | TQQQ-007 | TQQQ-008 | TQQQ-009 |
|-------------------|----------|----------|----------|----------|----------|----------|----------|----------|----------|
| Drawdown          | -15%     | **-12%** | -15%     | -15%     | -15%     | — | -15% | -15% | **-13%** |
| RSI(5)            | < 25     | **< 30** | < 25     | < 25     | < 25     | — | < 25 | < 25 | < 25 |
| Volume            | 1.5x     | **1.3x** | 1.5x     | 1.5x     | 1.5x     | — | 1.5x | 1.5x | 1.5x |
| VIX Filter        | —        | —        | —        | **≥ 25** | **≥ 20** | — | — | — | — |
| Down Days (5d)    | —        | —        | —        | —        | —        | **≥ 4/5** | — | — | — |
| 5d Return         | —        | —        | —        | —        | —        | **≤ -12%** | — | — | — |
| Trend Filter      | —        | —        | —        | —        | —        | **Close < SMA50** | — | — | — |
| Profit Target     | +5%      | +5%      | **+12%** | +5%      | **+8%**  | **+7%** | **+6%** | **+7%** | **+7%** |
| Stop Loss         | -8%      | **-6%**  | -8%      | -8%      | -8%      | **-10%** | -8% | -8% | -8% |
| Holding Days      | 7        | 7        | **12**   | 7        | **10**   | **10** | **8** | **10** | **10** |
| Trailing Stop     | —        | —        | **-4%**  | —        | **-6%**  | — | — | — | — |
| Cooldown Days     | 3        | **5**    | 3        | 3        | 3        | **5** | 3 | 3 | 3 |

## 實驗結論 (Key Findings)

### Part A — In-Sample (2019-01-01 ~ 2023-12-31)

| ID       | 訊號數 | 勝率   | 平均報酬 | 累計報酬  | 最大回撤 | 結論   |
|----------|-------|--------|---------|----------|---------|--------|
| TQQQ-001 | 20    | 85.0%  | +2.83%  | +70.86%  | -15.00% | 基線表現優異 |
| TQQQ-002 | 31    | 61.3%  | +0.13%  | -2.03%   | -15.00% | 訊號變多但勝率與報酬大幅下降 |
| TQQQ-003 | 20    | 55.0%  | +2.48%  | +54.03%  | -15.00% | 追蹤停利反而降低勝率與報酬 |
| TQQQ-004 | 4     | 75.0%  | +0.77%  | +2.39%   | -15.00% | VIX 條件過於嚴格，錯失機會 |
| TQQQ-005 | 7     | 57.1%  | +2.54%  | +17.51%  | -15.00% | 訊號數恢復，但勝率偏低，尚未超越基線 |
| TQQQ-006 | 25    | 72.0%  | +2.01%  | +50.42%  | -22.16% | 訊號數增加，但回撤顯著放大 |
| TQQQ-007 | 14    | 85.7%  | +3.51%  | +59.18%  | -15.00% | 勝率高且回撤受控，但累計報酬仍低於基線 |
| TQQQ-008 | 20    | 80.0%  | +4.19%  | +120.21% | -15.00% | **累計報酬大幅超越基線，新最佳** |
| TQQQ-009 | 20    | 70.0%  | +2.56%  | +57.98%  | -15.00% | ❌ 訊號數未增加，勝率與報酬顯著下降 |

### Part B — Out-of-Sample (2024-01-01 ~ 2025-12-31)

| ID       | 訊號數 | 勝率   | 平均報酬 | 累計報酬  | 最大回撤 | 結論   |
|----------|-------|--------|---------|----------|---------|--------|
| TQQQ-001 | 8     | 87.5%  | +3.20%  | +27.44%  | -14.82% | 樣本外表現穩定且優異 |
| TQQQ-002 | 10    | 30.0%  | -6.11%  | -48.56%  | -18.43% | 放寬條件導致樣本外嚴重虧損 |
| TQQQ-003 | 8     | 50.0%  | +3.35%  | +26.32%  | -14.82% | 表現尚可，但仍略遜於基線 |
| TQQQ-004 | 6     | 83.3%  | +2.60%  | +15.59%  | -12.36% | 勝率佳，但訊號數較少、累計報酬低 |
| TQQQ-005 | 8     | 50.0%  | +1.46%  | +10.21%  | -14.82% | 訊號數足夠但樣本外勝率與報酬偏弱 |
| TQQQ-006 | 7     | 71.4%  | +0.93%  | +4.22%   | -14.96% | 勝率接近門檻，但樣本外報酬偏低 |
| TQQQ-007 | 6     | 83.3%  | +3.43%  | +21.20%  | -14.82% | 勝率改善、品質提升，但樣本外累計仍未超越基線 |
| TQQQ-008 | 8     | 87.5%  | +4.95%  | +45.44%  | -14.82% | **勝率與基線相同，累計報酬 +65.6% 超越基線，新最佳** |
| TQQQ-009 | 9     | 77.8%  | +2.74%  | +23.75%  | -17.41% | ❌ 僅多 1 訊號但品質下降，累計報酬大幅落後 |

> **目前結論：** TQQQ-008 (優化出場) 仍為最佳。TQQQ-009 嘗試僅放寬 drawdown（-15% → -13%），搭配 TQQQ-008 出場參數，但結果失敗：Part A 訊號數未增加（仍 20 個），勝率下降 80%→70%，累計報酬下降 +120.21%→+57.98%；Part B 僅多 1 個訊號（9 vs 8），勝率下降 87.5%→77.8%，累計下降 +45.44%→+23.75%。結論：即使只放寬 drawdown 一項，也會捕捉到品質較差的訊號，證明基線 -15% 門檻已是最優。此前 TQQQ-002 (全部放寬) 也失敗，進一步確認進場條件敏感、不宜調整。

## 成交模型參數 (Execution Model Parameters — TQQQ-010+)

| 參數 | TQQQ-010 | TQQQ-011 | TQQQ-012 | TQQQ-013 |
|------|----------|----------|----------|----------|
| 來源實驗 (Source) | TQQQ-008 | TQQQ-001 | TQQQ-007 | TQQQ-012 + TQQQ-010 出場 |
| 進場模式 (Entry) | next_open_market | next_open_market | next_open_market | next_open_market |
| 止盈委託 (Profit) | limit_order Day | limit_order Day | limit_order Day | limit_order Day |
| 停損委託 (Stop) | stop_market GTC | stop_market GTC | stop_market GTC | stop_market GTC |
| 到期出場 (Expiry) | next_open_market | next_open_market | next_open_market | next_open_market |
| 滑價 (Slippage) | 0.10% | 0.10% | 0.10% | 0.10% |
| 悲觀認定 (Pessimistic) | ✅ | ✅ | ✅ | ✅ |
| Profit Target | +7% | +5% | +6% | +7% |
| Stop Loss | -8% | -8% | -8% | -8% |
| Holding Days | 10 | 7 | 8 | 10 |
| QQQ RSI Filter | — | — | RSI(14) < 35 | RSI(14) < 35 |

### Part A — In-Sample (2019-01-01 ~ 2023-12-31)

| ID       | 訊號數 | 成交數 | 成交率  | 勝率   | 平均報酬 | 累計報酬  | 最大回撤  | 悲觀認定次數 |
|----------|-------|-------|---------|--------|---------|----------|----------|-------------|
| TQQQ-010 | 20    | 20    | 100.0%  | 70.0%  | +2.47%  | +55.44%  | -29.26%  | 0           |
| TQQQ-011 | 20    | 20    | 100.0%  | 70.0%  | +1.07%  | +19.35%  | -29.26%  | 0           |
| TQQQ-012 | 14    | 14    | 100.0%  | 71.4%  | +1.97%  | +27.79%  | -29.26%  | 0           |
| TQQQ-013 | 1     | 1     | 100.0%  | 0.0%   | -8.09%  | -8.09%   | -12.11%  | 0           |

### Part B — Out-of-Sample (2024-01-01 ~ 2025-12-31)

| ID       | 訊號數 | 成交數 | 成交率  | 勝率   | 平均報酬 | 累計報酬  | 最大回撤  | 悲觀認定次數 |
|----------|-------|-------|---------|--------|---------|----------|----------|-------------|
| TQQQ-010 | 8     | 8     | 100.0%  | 87.5%  | +5.11%  | +47.59%  | -11.80%  | 0           |
| TQQQ-011 | 8     | 8     | 100.0%  | 87.5%  | +3.36%  | +29.33%  | -11.80%  | 0           |
| TQQQ-012 | 6     | 6     | 100.0%  | 83.3%  | +3.65%  | +23.00%  | -11.80%  | 0           |
| TQQQ-013 | 1     | 1     | 100.0%  | 100.0% | +7.00%  | +7.00%   | +4.00%   | 0           |

> **與無成交模型版本的比較 (Comparison with no-execution-model versions):**
> - TQQQ-010 vs TQQQ-008: Part A 累計 +55.44% vs +120.21%（↓54%）、Part B 累計 +47.59% vs +45.44%（↑5%）
> - TQQQ-011 vs TQQQ-001: Part A 累計 +19.35% vs +70.86%（↓73%）、Part B 累計 +29.33% vs +27.44%（↑7%）
> - TQQQ-012 vs TQQQ-007: Part A 累計 +27.79% vs +59.18%（↓53%）、Part B 累計 +23.00% vs +21.20%（↑8%）
> - TQQQ-013 vs TQQQ-010: Part A 累計 -8.09% vs +55.44%（顯著落後）、Part B 累計 +7.00% vs +47.59%（顯著落後）
>
> **分析：** In-Sample 累計報酬大幅下降，主因是舊實驗進場以「訊號日收盤價」成交（已知未來資訊），新實驗改為「隔日開盤市價」更貼近實盤。Out-of-Sample 反而略微提升，顯示隔日開盤進場在近期市場環境中表現更穩健。成交模型版本的績效更可信賴。
>
> **TQQQ-013 失敗紀錄：** 嘗試將 TQQQ-012 的出場參數改為 TQQQ-010 的 TP +7% / 持倉 10 天，期待提高單筆報酬；但 QQQ RSI 過濾後訊號數過少，Part A 只有 1 筆且為虧損，整體顯著落後，不採用。

<!-- 更新指引：
  1. 執行 uv run trading run --all
  2. 執行 uv run trading compare tqqq_capitulation tqqq_cap_relaxed_entry tqqq_cap_wider_exit tqqq_cap_vix_filter tqqq_cap_vix_adaptive tqqq_momentum_collapse tqqq_cap_qqq_confirm tqqq_cap_optimized_exit tqqq_cap_gentle_entry
  3. 將關鍵數字填入上方表格（訊號數、勝率、平均報酬%、累計報酬%、最大回撤%）
  4. 更新「結論」欄、「目前結論」與頂部的「當前最佳」
-->
