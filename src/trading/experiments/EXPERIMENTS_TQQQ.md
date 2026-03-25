# TQQQ 實驗總覽 (TQQQ Experiment Index)

> **最新實驗 (Latest):** TQQQ-004 `tqqq_cap_vix_filter`
> **當前最佳 (Best):** TQQQ-001 `tqqq_capitulation`

## 實驗清單 (Experiments)

| ID       | 資料夾                     | 說明                                   | 關鍵差異                | 狀態     |
|----------|---------------------------|----------------------------------------|------------------------|----------|
| TQQQ-001 | `tqqq_capitulation`       | 基礎版：三條件恐慌抄底 + 冷卻機制        | 基線                    | ✅ 基線  |
| TQQQ-002 | `tqqq_cap_relaxed_entry`  | 放寬進場門檻，收緊停損                   | DD -12%, RSI<30, Vol 1.3x, SL -6% | ✅ 完成  |
| TQQQ-003 | `tqqq_cap_wider_exit`     | 加寬獲利目標 +12%，追蹤停利 -4%          | TP +12%, 持倉 12 天, Trailing -4%  | ✅ 完成  |
| TQQQ-004 | `tqqq_cap_vix_filter`     | 加入 VIX ≥ 25 過濾，僅在真正恐慌時進場   | VIX ≥ 25 額外條件       | ✅ 完成  |
| TQQQ-005 | `tqqq_cap_vix_adaptive`   | 軟性 VIX ≥ 20 + 適應性出場 (+8%/-6%)     | VIX ≥ 20, TP +8%, 持倉 10 天, Trailing -6% | ✅ 完成 |
| TQQQ-006 | `tqqq_momentum_collapse`  | 多日動能崩潰形態                         | 5日內4跌, 跌幅≤-12%, 收盤<SMA50 | ✅ 完成 |
| TQQQ-007 | `tqqq_cap_qqq_confirm`    | 加入 QQQ RSI(14) < 35 確認               | QQQ RSI < 35 額外條件, TP +6%, 持倉 8 天 | ✅ 完成 |

## 演進路線 (Lineage)

```
TQQQ-001 tqqq_capitulation (基礎版：DD -15%, RSI<25, Vol 1.5x)
├── TQQQ-002 tqqq_cap_relaxed_entry  (放寬進場 + 收緊停損)
├── TQQQ-003 tqqq_cap_wider_exit     (加寬出場 + 追蹤停利)
├── TQQQ-004 tqqq_cap_vix_filter     (加入 VIX 恐慌過濾)
├── TQQQ-005 tqqq_cap_vix_adaptive   (軟性 VIX 過濾 + 適應性出場)
├── TQQQ-006 tqqq_momentum_collapse  (多日動能崩潰全新訊號類型)
└── TQQQ-007 tqqq_cap_qqq_confirm    (加入 QQQ 超賣確認)
```

## 參數對照 (Parameter Comparison)

| 參數              | TQQQ-001 | TQQQ-005 (VIX) | TQQQ-006 (Momentum) | TQQQ-007 (QQQ) |
|-------------------|----------|----------------|---------------------|----------------|
| Drawdown          | -15%     | -15%           | -                   | -15%           |
| RSI(5)            | < 25     | < 25           | -                   | < 25           |
| Volume            | 1.5x     | 1.5x           | -                   | 1.5x           |
| Filter/Confirm    | —        | VIX ≥ 20       | 5日4跌,跌幅≤-12%,<SMA50 | QQQ RSI < 35 |
| Profit Target     | +5%      | +8%            | +7%                 | +6%            |
| Stop Loss         | -8%      | -8%            | -10%                | -8%            |
| Holding Days      | 7        | 10             | 10                  | 8              |
| Trailing Stop     | —        | -6%            | —                   | —              |
| Cooldown Days     | 3        | 3              | 5                   | 3              |

## 實驗結論 (Key Findings)

### Part A — In-Sample (2019-01-01 ~ 2023-12-31)

| ID       | 訊號數 | 勝率   | 平均報酬 | 累計報酬  | 最大回撤 | 結論   |
|----------|-------|--------|---------|----------|---------|--------|
| TQQQ-001 | 20    | 85.0%  | +2.83%  | +70.86%  | -15.00% | 基線表現優異 |
| TQQQ-005 | 7     | 57.1%  | +2.54%  | +17.51%  | -15.00% | VIX 軟性過濾和放寬追蹤依然降低勝率和訊號數 |
| TQQQ-006 | 25    | 72.0%  | +2.01%  | +50.42%  | -22.16% | 多日動能策略訊號多，但波動較大 |
| TQQQ-007 | 14    | 85.7%  | +3.51%  | +59.18%  | -15.00% | 勝率與平均報酬提升，但錯失了一些訊號 |

### Part B — Out-of-Sample (2024-01-01 ~ 2025-12-31)

| ID       | 訊號數 | 勝率   | 平均報酬 | 累計報酬  | 最大回撤 | 結論   |
|----------|-------|--------|---------|----------|---------|--------|
| TQQQ-001 | 8     | 87.5%  | +3.20%  | +27.44%  | -14.82% | 樣本外表現穩定且優異 |
| TQQQ-005 | 8     | 50.0%  | +1.46%  | +10.21%  | -14.82% | OOS 表現差強人意，未優於基線 |
| TQQQ-006 | 7     | 71.4%  | +0.93%  | +4.22%   | -14.96% | 勝率尚可但報酬受大額虧損拖累 |
| TQQQ-007 | 6     | 83.3%  | +3.43%  | +21.20%  | -14.82% | 高勝率與穩定報酬，是值得考慮的輔助策略 |

> **目前結論：** TQQQ-001 (基礎版) 表現最佳。放寬進場條件 (TQQQ-002) 會引入太多雜訊導致嚴重虧損；加寬獲利目標並加入追蹤停利 (TQQQ-003) 反而降低了勝率與整體報酬；加入 VIX ≥ 25 的嚴格過濾 (TQQQ-004) 會過度限制進場次數，錯失許多獲利機會。保持現有的基礎參數配置是目前最佳選擇。

<!-- 更新指引：
  1. 執行 uv run trading run --all
  2. 執行 uv run trading compare tqqq_capitulation tqqq_cap_relaxed_entry tqqq_cap_wider_exit tqqq_cap_vix_filter
  3. 將關鍵數字填入上方表格（訊號數、勝率、平均報酬%、累計報酬%、最大回撤%）
  4. 更新「結論」欄、「目前結論」與頂部的「當前最佳」
-->
