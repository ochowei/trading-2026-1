<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-03-27
  data_through: 2025-12-31
-->
## AI Agent 快速索引

**當前最佳：** DIA-001（回檔 ≥3% + WR ≤-80 + 收盤位置 ≥40%，追蹤停損保護獲利）

**已證明無效（禁止重複嘗試）：**
- 尚無（目前僅完成基礎版本）

**已掃描的參數空間：**
- 進場條件：沿用 GLD-007 參數（pullback ≥3%, WR ≤-80, close position ≥40%）
- 出場參數：TP=+3.5% / SL=-4.0% / 20天持倉 + 追蹤停損（+2.0% 啟動，1.5% 距離）

**尚未嘗試的方向（可探索）：**
- 調整回檔門檻（±1% 步進測試）
- 不同 WR 閾值（-75, -85 等）
- 無追蹤停損版本比較（固定 TP/SL）
- 結合 VIX 或債券相關指標確認
- 根據 DIA 實際波動度微調參數（可能比 GLD 略低）

**關鍵資產特性：**
- SPDR Dow Jones Industrial Average ETF，追蹤道瓊工業平均指數（30 檔大型股）
- 日波動度約 1.0-1.3%（與 GLD ~1.2% 相近，屬低波動 ETF）
- 流動性極佳，滑價假設 0.10%
- 價格加權指數，受高價股影響較大
- 適合使用追蹤停損（日波動 ≤1.5% 規則）
<!-- AI_CONTEXT_END -->

# DIA 實驗總覽 (DIA Experiments Overview)

## 資產特性 (Asset Characteristics)

| 特性 | 數值 |
|------|------|
| 標的 | DIA (SPDR Dow Jones Industrial Average ETF) |
| 追蹤指數 | Dow Jones Industrial Average (DJIA) |
| 日均波動度 | ~1.0-1.3% |
| 流動性 | 極佳（大型 ETF） |
| 滑價假設 | 0.10% |
| 策略類型 | 均值回歸（Mean Reversion） |
| 參考模板 | GLD-007（相近波動度） |

## 實驗列表 (Experiment List)

| ID | 名稱 | 策略核心 | 狀態 |
|----|------|----------|------|
| DIA-001 | Pullback + WR + Reversal | 回檔 + Williams %R + 收盤位置 + 追蹤停損 | 完成 |

---

## DIA-001: Pullback + Williams %R + Reversal Candle

### 設計理念 (Design Rationale)

DIA 為第一個道瓊指數 ETF 實驗。根據跨資產教訓 #11（新資產啟動流程）：
1. DIA 日波動度 ~1.0-1.3% 與 GLD ~1.2% 相近
2. 選擇 GLD-007 作為策略模板（pullback + Williams %R + close position filter + trailing stop）
3. 參數起點直接沿用 GLD-007 設定，後續根據回測結果迭代

### 進場條件 (Entry Conditions)

全部滿足才觸發訊號：
1. **回檔幅度**：收盤價低於 10 日高點 ≥ 3%
2. **Williams %R**：WR(10) ≤ -80（超賣確認）
3. **收盤位置**：(Close-Low)/(High-Low) ≥ 40%（日內反轉跡象）
4. **冷卻期**：前次訊號後 7 個交易日內不重複觸發

### 出場參數 (Exit Parameters)

| 參數 | 數值 |
|------|------|
| 獲利目標 (TP) | +3.5% |
| 停損 (SL) | -4.0% |
| 最大持倉天數 | 20 天 |
| 追蹤停損啟動 | 獲利 +2.0% |
| 追蹤停損距離 | 1.5% |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 隔日開盤市價單 (next_open_market) |
| 獲利出場 | 限價單當日 (limit_order_day) |
| 停損出場 | 停損市價單 GTC (stop_market_gtc) |
| 到期出場 | 隔日開盤市價單 (next_open_market) |
| 滑價 | 0.10% |
| 悲觀認定 | 啟用（同日觸及 TP 和 SL 時假設 SL 成交） |

### 回測結果 (Backtest Results)

| 指標 | Part A (IS) | Part B (OOS) | Part C (Live) |
|------|-------------|--------------|---------------|
| 期間 | 2019-01-01 ~ 2023-12-31 | 2024-01-01 ~ 2025-12-31 | 2026-01-01 ~ 2026-03-27 |
| 訊號數 | 20 | 7 | 2 |
| 每年訊號 | 4.0 | 3.5 | 8.7* |
| 勝率 | 60.0% | 100.0% | 50.0% |
| 平均報酬 | -0.17% | +1.52% | -0.28% |
| 累計報酬 | -4.23% | +11.11% | -0.58% |
| 平均持倉 | 7.0 天 | 13.4 天 | 3.0 天 |
| 最大回撤 | -6.66% | -3.83% | -1.30% |

*Part C 期間僅 ~3 個月，年化數字僅供參考。

**A/B 訊號頻率比：1.14:1**（4.0/yr vs 3.5/yr，優秀）

**出場分布 (Part A)：** 達標 3、停損 14（含悲觀 3）、到期 3
**出場分布 (Part B)：** 達標 0、停損 5（含悲觀 1）、到期 2

**觀察：**
- Part A 受 2022 年熊市影響，多筆停損出場導致累計為負
- Part B 表現強勁，100% 勝率，追蹤停損有效鎖定獲利
- A/B 頻率比 1.14:1 表示策略跨市況穩健
- 追蹤停損在 Part B 貢獻 4 筆獲利出場，平均報酬 +1.52%

### 參數對照表 (Parameter Comparison)

| 參數 | GLD-007 | DIA-001 | 備註 |
|------|---------|---------|------|
| Pullback lookback | 10 | 10 | 相同 |
| Pullback threshold | -3% | -3% | 相同（波動度相近） |
| WR period | 10 | 10 | 相同 |
| WR threshold | -80 | -80 | 相同 |
| Close position | ≥40% | ≥40% | 相同 |
| Cooldown | 7 天 | 7 天 | 相同 |
| TP | +3.5% | +3.5% | 相同 |
| SL | -4.0% | -4.0% | 相同 |
| Holding days | 20 | 20 | 相同 |
| Trail activation | +2.0% | +2.0% | 相同 |
| Trail distance | 1.5% | 1.5% | 相同 |
| Slippage | 0.10% | 0.10% | 皆為高流動性 ETF |
