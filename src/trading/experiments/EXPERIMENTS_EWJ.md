<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-05-08
  data_through: 2025-12-31
  note_2026_05_08: EWJ-006 added 2026-05-08 (USDJPY Direction Filter on Vol-Transition MR，**repo 首次 USDJPY (USD/JPY spot rate) direction filter 於任何資產 + lesson #24 family v8 候選 bilateral FX direction 變體**). Three iterations all SUCCESS, **Att2 ★ 新全域最優 +239% min Sharpe vs EWJ-005 Att2**: Att1 (usdjpy_lookback=10, max_change=+2.0% 寬鬆 baseline) Part A 8 訊號 100% WR Sharpe **2.19** cum +19.62% MDD -3.99% / Part B 3 訊號 100% WR std=0 cum +10.87% / min(A,B)† **2.19**（+213% vs EWJ-005 Att2 baseline 0.70）— USDJPY 10d > +2.0% 完整過濾 EWJ-005 Att2 殘餘 Part A SL（2022-09-01 BoJ YCC 守成，USDJPY 10d 急升 region），副作用為過濾 2024-04-17 BoJ-anticipation Part B winner（10d JPY 急貶 region），Part B 從 4 訊號降至 3 訊號 (2024-06-13/2025-03-11/2025-11-18 全 TP)；Att2 ★ (max_change=+1.0% 收緊) Part A 7 訊號 100% WR Sharpe **2.37** cum +19.31% / Part B 3 訊號不變 / min(A,B)† **2.37**（**+239% vs baseline，+8% vs Att1**）— +1.0% 收緊過濾 1 個邊緣 Part A winner（USDJPY 10d ∈ (+1.0%, +2.0%]，殘餘 winners USDJPY 10d 全部 ≤ +1.0%），Sharpe 提升 due to 變異降低；Att3 (max_change=+0.5% 過緊) Part A 5 訊號 100% WR Sharpe 2.31 cum +12.24% / Part B 2 訊號 100% WR std=0 cum +7.12% / min(A,B)† 2.31（-3% vs Att2，過緊）— -0.5% 移除 2 個 Part A winners + 1 個 Part B winner（2024-06-13 USDJPY 10d ∈ (+0.5%, +1.0%]）確認 +1.0% 為甜蜜點。**核心發現**：(1) EWJ Part A 殘餘 SL（2022-09-01 BoJ YCC 守成）在 USDJPY 10d 維度具乾淨區分力，符合 EWJ 美元計價結構性 driver 假設（JPY 急貶 → currency drag → USD-EWJ 反彈延續性受抑）；(2) Part B 2024-04-17 BoJ-anticipation winner 雖被過濾為 collateral damage，但結構上仍屬「JPY 急貶 region」高 currency drag 風險，過濾為合理保守決策。**跨資產貢獻（repo 首次 lesson #24 family v8）**：repo 首次 USDJPY/JPY direction filter 於任何資產，既有 lesson #24 family v1-v6 皆 implied vol（^VIX/^MOVE/^GVZ/^OVX）；v7 候選 COPX-016 DXY spot FX index；v8 候選（本實驗）bilateral FX direction (USD vs single currency) 於單一國家 ETF。**新跨資產假設（待驗證）**：bilateral FX direction filter 適用「FX-sensitive 單一國家 ETF」（EWJ/EWZ/EWT/INDA/FXI 等），尤其當 ETF 計價貨幣 ≠ 標的國家貨幣且兩貨幣對具強結構性 driver。EWJ-006 Att2 為新全域最優（6 次實驗、18 次嘗試）。
  note_2026_05_16_ewj007: EWJ-007 added 2026-05-16 (^VIX Forward-Looking Implied-Vol Regime-Gated MR, **repo 首次 ^VIX 應用於非美已開發單一國家寬基股票 ETF**, lesson #24 family ^VIX gate 疊加於 EWJ-005 Att2 完整 MR 框架, 目標 surgical 過濾唯一殘餘 Part A SL 2022-09-01). Three iterations all FAILED/REJECTED vs EWJ-005 Att2 min(A,B)† 0.70: Att1 (^VIX 3d DIRECTION <= +5.0 XLU-013/USO-025 sweet-spot port) Part A 7/85.7%/Sharpe **0.60** cum +10.82% / Part B 4/4 不變 / min(A,B) **0.60** (-14%) — VIX-calib log 證實 2022-09-01 SL 之 ^VIX 3d change = -0.65 (vol 持平/微降非加速), DIRECTION cap 不過濾 SL 反誤殺 winners 2019-05-08 (3d +6.53) / 2021-07-19 (3d +6.17); Att2 (^VIX 3d DIRECTION <= +3.0 加嚴, 鏡像 EWZ-008 方法論) Part A 5/80.0%/Sharpe **0.42** cum +5.78% / Part B 3/3 (誤殺 2025-11-18 winner 3d +4.69) / min **0.42** (-40%); Att3 (^VIX LEVEL CAP <= 25.0, 鏡像 EWZ-008 Att3) Part A 5/5/100%/nominal Sharpe 2.97 / Part B 3/3 — **nominal 雙零方差 BUT REJECT (非外科式 attrition)**: LEVEL CAP <= 25 過濾 SL 2022-09-01 (VIX 25.56) 僅靠整片切除 ^VIX > 25 高波動 regime, 連帶切除 3 筆最強 +3.50% TP winners (2020-10-30 VIX 38.02 / 2022-09-29 VIX 31.84 / 2023-03-15 VIX 26.14) + 1 筆 Part B winner (2025-03-11 VIX 26.92), 訊號 Part A 9→5 (-44%) / Part B 4→3 (-25%), 存活集為 5 筆最弱 expiry (+0.90~+2.23%), nominal 高 Sharpe 為退化零方差假象無品質區分力 (違反 lesson #14 + EEM-016 Att3 非外科式 attrition REJECT 標準). **核心結構性發現**: lesson #24 ^VIX gate 對 EWJ 結構性無區分力 — trade-level 證實唯一綁定 Part A SL 2022-09-01 (Jackson Hole 鷹派後) 之 ^VIX (level 25.56 / 3d -0.65 / 5d +3.78 / 10d +6.00) 在 12 筆 winners ^VIX 分布每一維度 (level/3d/5d/10d, cap 或 floor) 皆居中交錯無乾淨 separator; EWJ 殘餘失敗為 idiosyncratic 日本特有 (BoJ 政策/日圓套息/出口週期) 非 global implied-vol regime outlier, 與 EWJ-004 「日本 RS 為事件驅動非結構性」平行. **精煉 lesson #24 適用邊界**: ^VIX gate 對「已開發市場單一國家股票 ETF」在殘餘 binding SL 為 country-idiosyncratic (非 vol-regime isolated) 時結構性失敗, 與 EWZ-008 (EM ^VIX 失敗) / NVDA-018 (^VXN 失敗) 同屬「implied-vol gate 需殘餘 SL 集中於 vol-regime-可區分失敗模式」邊界家族. EWJ-006 Att2 仍為全域最優 (7 次實驗、21 次嘗試).
  note: EWJ-005 added 2026-04-26 (Post-Capitulation Vol-Transition MR：EWJ-003 Att3 框架 + 「1日報酬下限」過濾，**Att2 SUCCESS — repo 第 2 次「1d floor」方向成功驗證，繼 SPY-009 後首次非美 ETF 驗證**). Three iterations: Att1 (2DD floor <= -2.0%，VGK-008 Att2 直接移植) Part A 7/85.7%/Sharpe 0.61 cum +11.06% / Part B 3/100%/std=0 Sharpe 0.00 cum +10.87% / min(A,B)† 0.61 (+1.7% vs baseline 0.60，邊際) — EWJ Part A 兩筆 SL 的 2DD 為 -1.63%（filtered）/ -2.36%（kept），且 winners 2DD 廣泛分布 +0.17%~-2.43%，2DD floor 同時切除 6 筆 shallow-2DD winners 換 1 筆 SL，淨效果有限（不同於 VGK 1.12% vol 上 SLs 集中於 -1.47%~-1.68% 窄帶可被 -2.0% 完全繞過）；Att2 ★ (1d floor <= -0.5%，SPY-009 方向跨資產移植) Part A 9 訊號 WR **88.9%** Sharpe **0.70** cum +14.72% / Part B 4 訊號 WR 100% std=0 Sharpe 0.00 cum +14.75% / min(A,B)† **0.70**（+16.7% vs baseline，A/B 累計差 0.03pp 近乎完美平衡）—— 1d 維度成功過濾 2023-08-03 SL（1d -0.49% 恰於 -0.5% 邊界外），副作用為過濾 3 筆 1d 過淺贏家（2021-08-20 +0.08% / 2021-10-05 +0.56% / 2022-01-28 +0.38%），淨增 Part A WR 84.6%→88.9%；Att3 (1d floor <= -0.7%，加嚴測試) Part A 6/83.3%/0.46 cum +7.11% / Part B 3/100%/std=0 cum +10.87% / min 0.46 (-23% vs Att2) —— -0.7% 移除 3 筆淺 1d winners (2019-05-08 -0.61%/+2.23%、2019-08-02 -0.52%/+1.22%、2020-10-30 -0.58%/+3.50%) 確認 -0.5% 為甜蜜點。**核心發現**：EWJ Part A SLs 在 1d 維度具區分力（-0.49% vs winners 多在 -0.5%~-2.0%），與 SPY-009 同類失敗結構（淺 1d drift + BB 下軌假觸碰）；2DD floor 雖在 VGK/EEM/INDA 成功，但 EWJ winners 2DD 廣泛分布使 2DD 維度區分力弱於 1d 維度。**跨資產貢獻**：repo 第 2 次「1d floor」方向成功驗證（繼 SPY-009 後），首次非美 ETF 驗證；擴展 lesson #19 雙向性發現至 EWJ 1.15% vol 已開發亞洲寬基 ETF。EWJ-005 Att2 為新全域最優（5 次實驗、15 次嘗試）。
-->
## AI Agent 快速索引

**當前最佳：** ★ **EWJ-006 Att2**（USDJPY Direction Filter on Vol-Transition MR：EWJ-005 Att2 完整框架 + **USDJPY 10 日報酬 <= +1.0%** bilateral FX direction regime gate，TP +3.5%/SL -4.0%/20天/cd7）★ **2026-05-08 新全域最優（6 次實驗、18 次嘗試）**
- Part A: Sharpe **2.37**, 累計 +19.31%, 7 訊號 (1.4/年), WR **100.0%**, MaxDD -3.99%
- Part B: 累計 +10.87%, 3 訊號 (1.5/年), WR **100%**（3/3 全部達標，Sharpe 因 std=0 顯示 0.00）
- min(A,B)† **2.37**（Part A 為約束，Part B std=0 結構性零方差），**+239% vs EWJ-005 Att2 的 0.70**
- A/B 年化訊號比 1.4/yr vs 1.5/yr = **6.7% gap < 50% ✓**
- A/B 年化 cum 比較（CAGR）：A 3.59%/yr vs B 5.30%/yr = **32.3% gap**（接近 30% 邊界，因 Part B 樣本只有 2 年）
- 關鍵改善：USDJPY 10d <= +1.0% 過濾 EWJ-005 Att2 殘餘 Part A SL（2022-09-01 BoJ YCC 守成，JPY 24 年新低 region），Part A WR 88.9%→**100%** 且 Sharpe 0.70→**2.37**
- **跨資產貢獻**：**repo 首次 USDJPY (USD/JPY spot rate) direction filter 於任何資產 + lesson #24 family v8 候選 bilateral FX direction 變體**
- EWJ-006 Att1（max_change=+2.0%）：min 2.19，+213% vs baseline，1 個邊緣 winner 變異拖累 Sharpe
- EWJ-006 Att3（max_change=+0.5%，加嚴）：min 2.31，過緊移除 2 個 Part A winners + 1 個 Part B winner

**前任最佳：** EWJ-005 Att2（Post-Capitulation Vol-Transition MR：EWJ-003 Att3 框架 + **1 日報酬下限 <= -0.5%**，TP +3.5%/SL -4.0%/20天/cd7）
- Part A: Sharpe **0.70**, 累計 +14.72%, 9 訊號 (1.8/年), WR **88.9%**, MDD -4.10%
- Part B: 累計 +14.75%, 4 訊號 (2.0/年), WR 100%（4/4 全部達標，Sharpe 因 std=0 顯示 0.00）
- min(A,B)† **0.70**（Part A 為約束，沿用 EWJ-003/DIA-012/SPY-009 慣例）, +16.7% vs EWJ-003 Att3 的 0.60
- A/B 累計報酬差 **0.03pp（近乎完美平衡）**，A/B 年化訊號比 0.9:1（優秀）
- 關鍵改善：1d floor <= -0.5% 過濾 EWJ-003 Att3 的 2023-08-03 SL（1d -0.49% 恰於邊界外）+ 3 筆 1d 過淺 winners，淨增 WR 84.6%→88.9% 且 Sharpe 0.60→0.70
- **跨資產貢獻**：repo 第 2 次「1d floor」方向成功驗證（繼 SPY-009 後），首次非美 ETF 驗證

**前前任最佳：** EWJ-003 Att3（BB 下軌均值回歸：BB(20,1.5) 下軌觸及 + 10日高點回檔上限 7% + WR(10)≤-80 + ClosePos≥40% + ATR(5)/ATR(20)>1.15，TP +3.5%/SL -4.0%/20天）
- Part A: Sharpe 0.60, 累計 +21.97%, 13 訊號 (2.6/年), WR 84.6%, MDD -4.50%
- Part B: 累計 +22.93%, 6 訊號 (3.0/年), WR 100%（6/6 全部達標，Sharpe 因 std=0 顯示 0.00）
- A/B 年化訊號比 0.87:1（優秀），A/B 累計報酬差距 0.96pp（近乎完美平衡）

**前任最佳（vol-adaptive）：** EWJ-002 Att2（波動率自適應回檔+WR：10日回檔 3-7% + WR(10)≤-80 + ClosePos≥40% + ATR>1.15，min(A,B) Sharpe 0.55）

**已證明無效（禁止重複嘗試）：**
- 追蹤停損啟動 +2.0%/距離 1.5%（EWJ-001）— 啟動/TP 比 57% 遠低於 80% 門檻，壓縮獲利空間
- ATR > 1.12 門檻（EWJ-002 Att3）— 放入低品質慢磨下跌訊號（Part A 0.55→0.41，Part B 2.06→0.56）
- 無回檔上限（EWJ-002 Att1）— 極端崩盤（COVID）產生 2 筆連續停損，Part A Sharpe 0.21 vs Att2 的 0.55
- BB(20,2.0) 無回檔上限（EWJ-003 Att1）— Part A 優秀 0.70 但 Part B 僅 0.49（4 訊號含 1 停損）
- BB(20,1.5) 無回檔上限（EWJ-003 Att2）— Part B 優秀 1.01（8 訊號 87.5% WR）但 Part A 品質稀釋至 0.26（增加 3 筆 COVID/QT/夏季停損）
- **RS 動量（EWJ vs EFA/SPY）**（EWJ-004，三次嘗試均失敗）：
  - Att1: EFA ref, RS>=2%, pullback 1.5-4%, SMA(50) → Part A 0.15/Part B 0.47，min 0.15
  - Att2: EFA ref, RS>=3%, pullback 2-5%, SMA(200) → Part A 0.12/Part B 0.24，min 0.12（收緊訊號數驟降 10→5）
  - Att3: SPY ref, RS>=3%, pullback 2-5%, SMA(50) → Part A 0.37/Part B **-0.24**，min -0.24（A/B 嚴重不對稱）
  - **根因：日本相對強度由事件驅動（BOJ 政策、日圓套息交易、出口週期），非結構性週期因素**
  - 確認跨資產教訓 #25 擴展至**發達市場單一國家 ETF**：RS 動量僅適用於具有持續週期性結構優勢的資產（半導體 EWT、個股 TSM/NVDA）

**已掃描的參數空間：**
- EWJ-001：回檔≥3% + WR≤-80 + ClosePos≥40% + 追蹤停損（TP+3.5%/SL-4.0%）→ min 0.16
- EWJ-002 Att1：加 ATR>1.15，移除追蹤停損 → min 0.21（+31%）
- EWJ-002 Att2：加回檔上限 7%（lesson #13, ~6σ）→ min 0.55（+244%）
- EWJ-002 Att3：ATR>1.12 → min 0.41（-25%，放入壞訊號）
- EWJ-003 Att1：BB(20,2.0) + WR + ClosePos + ATR>1.15 → Part A 0.70/Part B 0.49，min 0.49
- EWJ-003 Att2：BB(20,1.5) + WR + ClosePos + ATR>1.15 → Part A 0.26/Part B 1.01，min 0.26
- EWJ-003 Att3：BB(20,1.5) + 回檔上限7% + WR + ClosePos + ATR>1.15 → **Part A 0.60/Part B 100%WR ★**
- EWJ-004 Att1-3：RS 動量 vs EFA/SPY（2-3% 門檻、SMA(50)/SMA(200)），min(A,B) 最佳 0.15（均失敗）
- EWJ-005 Att1：EWJ-003 Att3 框架 + 2DD floor <= -2.0%（VGK-008 Att2 移植）→ Part A 0.61/Part B std=0, min 0.61（+1.7%，邊際）
- EWJ-005 Att2：EWJ-003 Att3 框架 + **1d floor <= -0.5%**（SPY-009 方向）→ Part A 0.70/Part B std=0, min **0.70**（+16.7%）
- EWJ-005 Att3：EWJ-003 Att3 框架 + 1d floor <= -0.7%（加嚴）→ Part A 0.46/Part B std=0, min 0.46（-23% vs Att2，移除 3 筆淺 1d winners）
- EWJ-006 Att1：EWJ-005 Att2 框架 + USDJPY 10d <= +2.0%（寬鬆 baseline）→ Part A **2.19** 8/100% WR/Part B std=0 3/100%, min **2.19**（**+213% vs EWJ-005 Att2**）
- EWJ-006 Att2：EWJ-005 Att2 框架 + **USDJPY 10d <= +1.0%**（甜蜜點）→ Part A **2.37** 7/100% WR/Part B std=0 3/100%, min **2.37**（**+239%**）★ **新全域最優**
- EWJ-006 Att3：EWJ-005 Att2 框架 + USDJPY 10d <= +0.5%（過緊）→ Part A 2.31 5/100% WR/Part B std=0 2/100%, min 2.31（-3% vs Att2，過緊移除 1 個 Part B winner）
- EWJ-007 Att1：EWJ-005 Att2 框架 + ^VIX 3d DIRECTION <= +5.0（lesson #24 sweet-spot port）→ Part A 0.60/Part B 不變, min 0.60（-14%，誤殺 winners 保留 SL）
- EWJ-007 Att2：EWJ-005 Att2 框架 + ^VIX 3d DIRECTION <= +3.0（加嚴）→ Part A 0.42/Part B 3/3, min 0.42（-40%，誤殺更多 winners + Part B）
- EWJ-007 Att3：EWJ-005 Att2 框架 + ^VIX LEVEL CAP <= 25.0 → Part A 5/5 nominal 2.97 / Part B 3/3 **REJECT**（非外科式 attrition，9→5/-44%、4→3/-25%，連帶切 3 筆 +3.5% TP + 1 Part B winner）

**尚未嘗試的方向（預期邊際效益極低）：**
- RSI(2) 短期超賣框架（VGK 驗證非美 ETF 不適合 RSI(2)，cross-asset lesson #27）
- BB Squeeze 突破（INDA-003 驗證低波動非美 ETF 嚴重市場狀態依賴）
- BB(20,1.75) 中間值 — Att1/Att2 顯示 BB std 對 Part A/B 影響方向相反，1.5+cap 已是最佳組合
- 1d cap（DIA-012 方向）：EWJ Part A SLs 1d 為 -1.19% 與 -0.49%，cap 方向會誤刪 -2.03% / -1.81% 等深 1d winners，預期失敗
- 1d floor + 3d cap 雙維度（DIA-012 Att2 風格）：3d cap 在 EWJ 上不必要，EWJ-005 Att2 已達 0.03pp 完美平衡
- ~~RS 動量（EWJ vs EFA/SPY）~~ → EWJ-004 三次嘗試均失敗（Japan 的 RS 非結構性）
- ~~2DD floor（lesson #19 family）~~ → EWJ-005 Att1 驗證 2DD 維度區分力弱於 1d
- ~~^VIX forward-looking implied-vol regime gate（lesson #24 family）~~ → EWJ-007 三次嘗試（3d DIRECTION +5.0/+3.0、LEVEL CAP <=25.0）全部 FAILED/REJECT，^VIX 對 EWJ 結構性無區分力（2022-09-01 SL 非 ^VIX 任一維度 outlier）
- **★ 1d floor 方向精煉（Capitulation-Strength Filter）→ EWJ-005 Att2 成功**（1d floor <= -0.5% 過濾 2023-08-03 SL 與 3 筆淺 1d winners，min 0.60→0.70 +16.7%）
- **★★ USDJPY direction filter（lesson #24 family v8 候選 bilateral FX direction）→ EWJ-006 Att2 成功**（USDJPY 10d <= +1.0% 過濾 2022-09-01 BoJ YCC 守成 SL，min 0.70→**2.37** +239%；repo 首次 USDJPY/JPY direction filter 於任何資產）

**已證明無效（新增 — 禁止重複嘗試）：**
- ^VIX forward-looking implied-vol regime gate（EWJ-007，3 次嘗試）：DIRECTION（3d <= +5.0/+3.0）方向錯誤（2022-09-01 SL 之 ^VIX 3d = -0.65 持平/微降，cap 不過濾 SL 反誤殺高 3d-change winners）；LEVEL CAP（<= 25.0）僅靠整片切除高波動 regime 過濾 SL，連帶誤殺 3 筆 +3.5% TP + 1 Part B winner（非外科式 attrition，違反 lesson #14 + EEM-016 REJECT 標準）。**核心：EWJ 唯一綁定 Part A SL 2022-09-01 之 ^VIX（level 25.56 / 3d -0.65 / 5d +3.78 / 10d +6.00）在 12 筆 winners 分布每一維度皆居中交錯，無乾淨 separator**——EWJ 殘餘失敗為 idiosyncratic 日本特有（BoJ/日圓套息/出口週期）非 global vol-regime outlier，與 EWJ-004 RS 失敗（日本 RS 事件驅動非結構性）平行

**關鍵資產特性：**
- EWJ 為 iShares MSCI Japan ETF，追蹤日本股市大中型股
- 日均波動約 1.15%，與 GLD（1.12%）幾乎相同，屬低波動資產
- 日圓匯率波動會影響美元計價報酬（日圓貶值時 EWJ 下跌壓力增加）
- ATR > 1.15 過濾在 1.15% vol 有效（同 VGK 1.12%、INDA 0.97%、XLU 1.0%）
- 回檔上限 7% 有效隔離 COVID 等極端崩盤
- BB 下軌自適應門檻在低波動資產（1.15%）上優於固定回檔門檻（CIBR-007 在 1.53% vol 也驗證）
- 高流動性 ETF，滑價假設 0.1%
- **RS 動量完全無效（EWJ-004 驗證）**：日本相對強度由事件驅動（BOJ 政策、日圓套息交易、出口週期），非結構性週期因素。三次嘗試（EFA/SPY 基準、RS 2-3%、SMA(50)/SMA(200)）min(A,B) 最佳僅 0.15，Part A 品質不穩定（0.12-0.37），Part B 在 Att3 翻負（-0.24）。確認跨資產教訓 #25 延伸至**發達市場單一國家 ETF**
- **1d floor capitulation filter 在 EWJ 有效（EWJ-005 Att2 驗證）**：日波動 1.15% 下 1d 報酬 -0.5% 為甜蜜點，過濾「淺 1d drift + BB 下軌假觸碰」訊號（如 2023-08-03 SL 1d -0.49% 恰於邊界外）。比 2DD floor（VGK-008/EEM-014/INDA-010 方向）在 EWJ 更有效，因 EWJ winners 2DD 廣泛分布（+0.17%~-2.43%）但 1d 分布更集中。EWJ 為 repo 第 2 例「1d floor」成功（首例 SPY-009），並擴展至非美 ETF
- **USDJPY direction filter 在 EWJ 高度有效（EWJ-006 Att2 驗證，repo 首次 bilateral FX direction filter）**：USDJPY 10d <= +1.0% 為甜蜜點，過濾「JPY 急貶 currency drag + BoJ 政策衝擊」訊號（如 2022-09-01 BoJ YCC 守成 SL，USDJPY 10d 急升 region），min(A,B) 從 0.70 提升至 **2.37（+239%）**。設計依據：EWJ 為 USD-denominated Japan ETF，當 USDJPY 急升時 currency drag 通常超過出口受益，BoJ 政策衝擊類失敗事件（2022-09-01 / 2023-08-03 yield surge）伴隨 USDJPY 急升 region。**lesson #24 family v8 候選**：bilateral FX direction（USD vs single foreign currency）擴展自既有 implied vol（v1-v6）與 spot DXY index（COPX-016 v7 候選）；新跨資產假設為「FX-sensitive 單一國家 ETF（EWJ/EWZ/EWT/INDA/FXI）+ ETF 計價貨幣 ≠ 標的國家貨幣 + 兩貨幣對具強結構性 driver」
- **^VIX forward-looking implied-vol regime gate 對 EWJ 結構性無效（EWJ-007 驗證）**：repo 首次 ^VIX 應用於非美已開發單一國家寬基股票 ETF。lesson #24 規則 #2 對應 stock ETF→^VIX，但 EWJ-005 Att2 唯一殘餘 Part A SL 2022-09-01（Jackson Hole 鷹派後）之 ^VIX（level 25.56 / 3d -0.65 / 5d +3.78 / 10d +6.00）在 12 筆 winners ^VIX 分布每一維度皆居中交錯，無乾淨 separator。EWJ 殘餘失敗為 idiosyncratic 日本特有因素（BoJ 政策、日圓套息平倉、出口週期）而非 global implied-vol regime outlier，與 EWJ-004「日本 RS 事件驅動」結論平行。精煉 lesson #24 適用邊界：**已開發市場單一國家股票 ETF 在殘餘 binding SL 為 country-idiosyncratic 時 ^VIX gate 結構性失敗**（與 EWZ-008 EM ^VIX 失敗、NVDA-018 ^VXN 失敗同邊界家族）
<!-- AI_CONTEXT_END -->

# EWJ 實驗總覽 (EWJ Experiments Overview)

## 標的特性 (Asset Characteristics)

- **EWJ (iShares MSCI Japan ETF)**：追蹤 MSCI Japan 指數，涵蓋日本大中型股
- 日均波動約 1.15%，與 GLD（1.12%）幾乎相同，屬低波動資產
- 日圓匯率波動會影響美元計價報酬
- 年化波動率約 18.2%

## 參數對照表 (Parameter Comparison)

| 參數 | EWJ-001 | EWJ-002 Att2 | EWJ-003 Att3 | EWJ-005 Att2 | EWJ-006 Att2★ | EWJ-007 (FAIL) |
|------|---------|---------------|---------------|---------------|---------------|----------------|
| 進場框架 | 固定回檔≥3% | 固定回檔 3-7% | BB(20,1.5) 下軌 + 回檔上限 7% | BB(20,1.5) 下軌 + 回檔上限 7% | BB(20,1.5) 下軌 + 回檔上限 7% | 同 EWJ-005 Att2 |
| WR(10) | ≤ -80 | ≤ -80 | ≤ -80 | ≤ -80 | ≤ -80 | ≤ -80 |
| ClosePos | ≥ 40% | ≥ 40% | ≥ 40% | ≥ 40% | ≥ 40% | ≥ 40% |
| ATR 過濾 | 無 | ATR(5)/ATR(20) > 1.15 | ATR(5)/ATR(20) > 1.15 | ATR(5)/ATR(20) > 1.15 | ATR(5)/ATR(20) > 1.15 | ATR(5)/ATR(20) > 1.15 |
| Capitulation 過濾 | 無 | 無 | 無 | 1d floor <= -0.5% | 1d floor <= -0.5% | 1d floor <= -0.5% |
| FX regime gate | 無 | 無 | 無 | 無 | **USDJPY 10d <= +1.0%** | — |
| ^VIX gate（新增維度）| — | — | — | — | — | 3d DIR +5.0/+3.0 ‖ LEVEL CAP 25.0（全失敗）|
| TP | +3.5% | +3.5% | +3.5% | +3.5% | +3.5% | +3.5% |
| SL | -4.0% | -4.0% | -4.0% | -4.0% | -4.0% | -4.0% |
| 持倉 | 20 天 | 20 天 | 20 天 | 20 天 | 20 天 | 20 天 |
| 追蹤停損 | 啟動+2.0%/距離1.5% | 無 | 無 | 無 | 無 | 無 |
| Part A Sharpe | 0.16 | 0.55 | 0.60 | 0.70 | **2.37** | 0.60/0.42/2.97† |
| Part A WR | — | — | 84.6% | 88.9% | **100.0%** | 85.7%/80.0%/100% |
| Part B Sharpe | 0.24 | 2.06 | 0.00 (std=0) | 0.00 (std=0) | 0.00 (std=0) | 0.00 (std=0) |
| Part B WR | 71.4% | 83.3% | 100.0% | 100.0% | **100.0%** | 100%/100%/100% |
| **min(A,B)** | 0.16 | 0.55 | 0.60 | 0.70 | **2.37★** (Part A 為約束) | 0.60/0.42/REJECT |

## 實驗列表 (Experiment List)

| ID      | 資料夾                          | 策略摘要                                     | 狀態       |
|---------|---------------------------------|---------------------------------------------|-----------|
| EWJ-001 | `ewj_001_pullback_wr_reversal` | 回檔+WR+反轉K線均值回歸（追蹤停損）             | 已完成 |
| EWJ-002 | `ewj_002_vol_adaptive_pullback` | 波動率自適應回檔+WR均值回歸（ATR過濾+崩盤隔離） | 已完成（前最佳） |
| EWJ-003 | `ewj_003_bb_lower_mr` | BB 下軌均值回歸（BB+回檔上限+WR+ClosePos+ATR） | 已完成（前最佳） |
| EWJ-004 | `ewj_004_rs_momentum` | RS 動量回調（EWJ vs EFA/SPY，3 次嘗試均失敗） | 已完成（失敗，確認 lesson #25 擴展至 DM） |
| EWJ-005 | `ewj_005_vol_transition_mr` | Post-Capitulation Vol-Transition MR（EWJ-003 + 1d floor）| 已完成（前最佳） |
| EWJ-006 | `ewj_006_usdjpy_direction_mr` | USDJPY Direction-Gated Vol-Transition MR（EWJ-005 + USDJPY 10d <= +1.0%）★ | ✅ 當前最佳 |
| EWJ-007 | `ewj_007_vix_implied_vol_mr` | ^VIX Forward-Looking Implied-Vol Regime-Gated MR（EWJ-005 Att2 + ^VIX gate，3 次嘗試均失敗） | 已完成（失敗，^VIX 對 EWJ 結構性無區分力） |

---

## EWJ-001：回檔 + Williams %R + 反轉K線均值回歸

### 目標 (Goal)

以 GLD-007 為模板（波動度幾乎相同），測試回檔+WR+反轉K線確認的均值回歸策略是否適用於日本股市 ETF。

### 進場條件 (Entry Conditions)

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | 回檔深度 | 10日高點回檔 | ≤ -3% | 從近期高點回落 ≥3% |
| 2 | 超賣確認 | Williams %R(10) | ≤ -80 | 10 日超賣區域 |
| 3 | 反轉跡象 | 收盤位置 (ClosePos) | ≥ 40% | 收盤在當日振幅上方 40%，確認日內反彈 |
| 4 | 冷卻期 | Cooldown | 7 天 | 防止同一波段重複進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +3.5% | 均值回歸目標價 |
| 停損 (SL) | -4.0% | 固定停損 |
| 最大持倉天數 | 20 天 | 到期出場 |
| 追蹤停損啟動 | +2.0% | 獲利達 2% 啟動追蹤 |
| 追蹤停損距離 | 1.5% | 從最高價回落 1.5% 觸發 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 隔日開盤市價單 |
| 獲利出場 | 日內限價單 |
| 停損出場 | 停損市價單 (GTC) |
| 到期出場 | 隔日開盤市價單 |
| 滑價假設 | 0.1%（ETF） |
| 悲觀認定 | 同日觸及 TP 和 SL 時認定停損 |

### 設計理念 (Design Rationale)

- **模板選擇**：EWJ 日波動 1.15% 與 GLD 1.12% 幾乎相同，直接沿用 GLD-007 的成功策略框架
- **三重確認進場**：回檔深度 + WR 超賣 + 收盤位置過濾，確保僅在有日內反轉跡象時進場
- **追蹤停損**：低波動資產適用追蹤停損（cross-asset lesson #2），啟動門檻 +2% 接近 TP +3.5%
- **收盤位置過濾**：日波動 1.15% 在 ClosePos 有效範圍內（≤2.0%，cross-asset lesson #6）

### 回測結果 (Backtest Results)

| 期間 | 訊號數 | 每年 | 勝率 | 累計報酬 | Sharpe | MDD | 狀態 |
|------|--------|------|------|----------|--------|-----|------|
| Part A (2019-2023) | 30 | 6.0 | 73.3% | +14.19% | 0.16 | -11.20% | 已完成 |
| Part B (2024-2025) | 14 | 7.0 | 71.4% | +10.61% | 0.24 | -9.66% | 已完成 |
| Part C (2026-) | 1 | 3.7 | 100% | +3.42% | 0.00 | +2.38% | 進行中 |

**A/B 訊號年化比:** 0.86:1（優秀）
**A/B 勝率一致性:** 73.3% vs 71.4%（極佳）
**min(A,B) Sharpe:** 0.16

---

## EWJ-002：波動率自適應回檔 + WR 均值回歸（前最佳）

### 目標 (Goal)

解決 EWJ-001 的兩個問題：(1) 追蹤停損啟動比 57%（+2.0%/+3.5%）遠低於 lesson #2 的 80% 門檻，壓縮獲利；(2) 缺乏波動率過濾，慢磨下跌產生假訊號。改用 ATR(5)/ATR(20) 波動率飆升過濾（VGK-002/XLU-011 模板）+ 回檔上限 7% 隔離極端崩盤（lesson #13）。

### 迭代歷程 (Iteration History)

| Attempt | 策略 | ATR | 回檔上限 | Part A Sharpe | Part B Sharpe | min Sharpe | 結果 |
|---------|------|-----|---------|---------------|---------------|------------|------|
| Att1 | PB+WR+ATR | >1.15 | 無 | 0.21 | 0.79 | 0.21 | △ COVID 2 連停損 |
| **Att2★** | **PB+WR+ATR** | **>1.15** | **7%** | **0.55** | **2.06** | **0.55** | **★ 最終選擇** |
| Att3 | PB+WR+ATR | >1.12 | 7% | 0.41 | 0.56 | 0.41 | ✗ 放入壞訊號 |

### 進場條件 (Entry Conditions) — Att2★

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | 回檔深度 | 10日高點回檔 | ≤ -3% | 從近期高點回落 ≥3% |
| 2 | 回檔上限 | 10日高點回檔 | ≥ -7% | 隔離極端崩盤（lesson #13, ~6σ） |
| 3 | 超賣確認 | Williams %R(10) | ≤ -80 | 10 日超賣區域 |
| 4 | 反轉跡象 | 收盤位置 (ClosePos) | ≥ 40% | 日內反轉確認 |
| 5 | 波動率飆升 | ATR(5)/ATR(20) | > 1.15 | 短期波動率高於長期→急跌恐慌 |
| 6 | 冷卻期 | Cooldown | 7 天 | 防止同一波段重複進場 |

### 出場參數 (Exit Parameters) — Att2★

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +3.5% | 同 GLD-007/VGK-002 |
| 停損 (SL) | -4.0% | 同 GLD-007/VGK-002 |
| 最大持倉天數 | 20 天 | 到期出場 |
| 追蹤停損 | 無 | ATR 過濾已足夠選擇高品質訊號 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 隔日開盤市價單 |
| 獲利出場 | 日內限價單 Day |
| 停損出場 | 停損市價單 GTC |
| 到期出場 | 隔日開盤市價單 |
| 滑價假設 | 0.1%（ETF） |
| 悲觀認定 | 同日觸及 TP 和 SL 時認定停損 |

### 設計理念 (Design Rationale)

- **移除追蹤停損**：EWJ-001 啟動比 +2.0%/+3.5% = 57%，遠低於 lesson #2 的 80% 門檻。VGK-002 Att3 驗證在相同 vol 下固定 TP/SL 更佳
- **ATR 波動率過濾**：ATR(5)/ATR(20) > 1.15 在 ~1.0-1.15% vol 資產上效果極佳（XLU +272%、VGK -0.06→0.42、INDA 0.03→0.15）
- **回檔上限 7%**：隔離極端崩盤訊號（COVID 2020），~6σ 對 1.15% vol（lesson #13），移除 3 筆壞交易後 Part A WR 71.4%→81.8%
- **GLD-007/VGK-002 模板**：EWJ vol 1.15% ≈ VGK 1.12% ≈ GLD 1.12%，直接採用已驗證參數

### 回測結果 (Backtest Results) — Att2★

| 期間 | 訊號數 | 每年 | 勝率 | 累計報酬 | Sharpe | MDD | 狀態 |
|------|--------|------|------|----------|--------|-----|------|
| Part A (2019-2023) | 11 | 2.2 | 81.8% | +18.08% | 0.55 | -4.50% | 已完成 |
| Part B (2024-2025) | 6 | 3.0 | 83.3% | +18.48% | 2.06 | -2.26% | 已完成 |
| Part C (2026-) | 0 | 0.0 | - | +0.00% | 0.00 | 0.00% | 進行中 |

**A/B 訊號年化比:** 0.73:1（優秀，Part B 更活躍）
**A/B 累計報酬差:** |18.08% - 18.48%| = 0.40pp（近乎完美平衡）
**A/B 訊號數差距:** |11-6|/11 = 45.5%（< 50%）
**min(A,B) Sharpe:** 0.55（vs EWJ-001 的 0.16，+244% 改進）

#### Att1 結果：無回檔上限

| 期間 | 訊號數 | 勝率 | 累計報酬 | Sharpe |
|------|--------|------|----------|--------|
| Part A | 14 | 71.4% | +8.83% | 0.21 |
| Part B | 8 | 75.0% | +17.60% | 0.79 |

**改進方向**：COVID 2020 產生 2 筆連續停損（-4.10% × 2 = -8.20%），回檔上限 7% 可隔離。

#### Att3 結果：ATR > 1.12

| 期間 | 訊號數 | 勝率 | 累計報酬 | Sharpe |
|------|--------|------|----------|--------|
| Part A | 12 | 75.0% | +16.16% | 0.41 |
| Part B | 6 | 66.7% | +9.78% | 0.56 |

**失敗原因**：ATR 1.12 放入 2 個壞訊號（Part A 2023-09-25 -4.10%、Part B 2024-04-10 -4.10%），確認 1.15 為甜蜜點。

### 關鍵發現

1. **回檔上限是 EWJ 的關鍵改進**：7% cap 移除 COVID 等極端事件的 3 筆壞交易，Part A Sharpe 0.21→0.55（+162%）
2. **ATR 1.15 為甜蜜點**：1.12 放入壞訊號（同 INDA-002 的 1.1 放入壞訊號），1.15 在 1.0-1.15% vol 資產上是穩定最佳值
3. **追蹤停損在啟動比 < 80% 時壓縮獲利**：EWJ-001 的 57% 比例壓縮獲利空間
4. **VGK-002 模板直接適用**：EWJ (1.15%) 和 VGK (1.12%) 行為類似（非美國分散化 ETF），同一框架均成功

---

## EWJ-003：BB 下軌均值回歸（前任最佳）

### 目標 (Goal)

探索 BB 下軌統計自適應門檻是否優於 EWJ-002 的固定回檔門檻。CIBR-007 驗證 BB 下軌在 1.53% vol 資產上優於固定回檔（+17%），EWJ 日波動 1.15% 更低，BB 應更適合。

### 迭代歷程 (Iteration History)

| Attempt | 策略 | BB std | 回檔上限 | Part A Sharpe | Part B Sharpe | Part B WR | 結果 |
|---------|------|--------|---------|---------------|---------------|-----------|------|
| Att1 | BB+WR+CP+ATR | 2.0 | 無 | 0.70 | 0.49 | 75.0% | △ Part B 僅 4 訊號 |
| Att2 | BB+WR+CP+ATR | 1.5 | 無 | 0.26 | 1.01 | 87.5% | ✗ Part A 品質稀釋 |
| **Att3★** | **BB+WR+CP+ATR** | **1.5** | **7%** | **0.60** | **0.00(std=0)** | **100.0%** | **★ 最終選擇** |

### 進場條件 (Entry Conditions) — Att3★

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | BB 下軌觸及 | Close vs BB(20,1.5) lower | Close ≤ BB lower | 統計自適應超賣門檻 |
| 2 | 回檔上限 | 10日高點回檔 | ≥ -7% | 隔離極端崩盤（~6σ for 1.15% vol） |
| 3 | 超賣確認 | Williams %R(10) | ≤ -80 | 10 日超賣區域 |
| 4 | 反轉跡象 | 收盤位置 (ClosePos) | ≥ 40% | 日內反轉確認 |
| 5 | 波動率飆升 | ATR(5)/ATR(20) | > 1.15 | 急跌恐慌過濾 |
| 6 | 冷卻期 | Cooldown | 7 天 | 防止同一波段重複進場 |

### 出場參數 (Exit Parameters) — Att3★

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +3.5% | 同 EWJ-002/VGK-002/GLD-007 |
| 停損 (SL) | -4.0% | 同 EWJ-002/VGK-002/GLD-007 |
| 最大持倉天數 | 20 天 | 到期出場 |
| 追蹤停損 | 無 | ATR 過濾已足夠 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 隔日開盤市價單 |
| 獲利出場 | 日內限價單 Day |
| 停損出場 | 停損市價單 GTC |
| 到期出場 | 隔日開盤市價單 |
| 滑價假設 | 0.1%（ETF） |
| 悲觀認定 | 同日觸及 TP 和 SL 時認定停損 |

### 設計理念 (Design Rationale)

- **BB 下軌取代固定回檔**：BB(20,1.5) 是統計自適應門檻——低波動期淺門檻捕捉更多訊號，高波動期深門檻自動過濾。在 EWJ 1.15% vol 上，BB(1.5) 的絕對深度 ≈ CIBR 1.53% vol 的 BB(2.0)。
- **回檔上限 7% 崩盤隔離**：BB 下軌在極端事件（COVID、關稅衝擊）期間可能滯後，7% cap 提供硬上限保護。Att1 驗證 BB(2.0) 無 cap 時 COVID 停損 -4.10%。
- **BB(1.5) vs BB(2.0) 取捨**：Att1 (BB 2.0) Part A 優秀但 Part B 僅 4 訊號。Att2 (BB 1.5) Part B 優秀但 Part A 品質稀釋（新增 3 筆崩盤停損）。Att3 的 7% cap 兼得兩者優勢：BB(1.5) 的寬訊號捕捉 + cap 的崩盤保護。
- **保留 EWJ-002 驗證的過濾器**：WR(10) + ClosePos + ATR(5)/ATR(20) > 1.15 三重品質過濾，確保每個訊號都有超賣確認、日內反轉和波動率飆升。

### 回測結果 (Backtest Results) — Att3★

| 期間 | 訊號數 | 每年 | 勝率 | 累計報酬 | Sharpe | MDD | 狀態 |
|------|--------|------|------|----------|--------|-----|------|
| Part A (2019-2023) | 13 | 2.6 | 84.6% | +21.97% | 0.60 | -4.50% | 已完成 |
| Part B (2024-2025) | 6 | 3.0 | 100.0% | +22.93% | 0.00† | -2.26% | 已完成 |
| Part C (2026-) | 0 | 0.0 | - | +0.00% | 0.00 | 0.00% | 進行中 |

†Part B Sharpe 0.00 因 6 筆交易均回報 +3.50%（std=0），並非表現不佳而是零變異數的數學結果。

**A/B 訊號年化比:** 0.87:1（優秀，Part B 更活躍）
**A/B 累計報酬差:** |21.97% - 22.93%| = 0.96pp（近乎完美平衡）
**Part A Sharpe 0.60**（約束條件）> EWJ-002 的 0.55（+9%）

#### Att1 結果：BB(20, 2.0) 無回檔上限

| 期間 | 訊號數 | 勝率 | 累計報酬 | Sharpe |
|------|--------|------|----------|--------|
| Part A | 10 | 90.0% | +16.59% | 0.70 |
| Part B | 4 | 75.0% | +6.33% | 0.49 |

**改進方向**：Part A 優秀但 Part B 僅 4 訊號（含 1 筆 2025-04-07 關稅衝擊停損 -4.10%）。需要更多 Part B 訊號。

#### Att2 結果：BB(20, 1.5) 無回檔上限

| 期間 | 訊號數 | 勝率 | 累計報酬 | Sharpe |
|------|--------|------|----------|--------|
| Part A | 16 | 75.0% | +12.41% | 0.26 |
| Part B | 8 | 87.5% | +22.01% | 1.01 |

**失敗原因**：BB(1.5) 較寬下軌在 Part A 增加 6 筆訊號（3 好 3 壞），Part A 品質稀釋。新增 3 筆停損：2020-02-28（COVID 前奏）、2022-09-01（QT 期間）、2023-08-03（夏季回檔）。

### 關鍵發現

1. **BB 下軌自適應門檻優於固定回檔門檻**：EWJ-003 Att3 Part A Sharpe 0.60 > EWJ-002 的 0.55（+9%），同時 Part A 訊號數 13 > 11（更多有效訊號）
2. **BB std 對 Part A/B 影響方向相反**：BB(2.0) Part A 優 Part B 弱；BB(1.5) Part A 弱 Part B 優。回檔上限 7% 解決此矛盾
3. **混合進場（BB + pullback cap）是低波動 ETF 的最佳組合**：CIBR-007 純 BB 在 1.53% vol 有效，但 EWJ 1.15% vol 需要 cap 額外保護（可能因為 EWJ 受日圓匯率影響，極端事件更頻繁）
4. **Part B 100% WR 驗證策略穩健性**：6 筆交易全部達標，包含 2024 日銀升息衝擊後的復甦和 2025 多次回檔

---

## EWJ-004：Relative Strength Momentum Pullback（失敗，確認 lesson #25 擴展至 DM）

### 目標 (Goal)

EWJ-003 已達 Part A Sharpe 0.60（Part B WR 100% / std=0），Part A 為唯一瓶頸。
測試 EWT-007 驗證成功的 RS 動量框架是否可套用至**發達市場單一國家 ETF**。
Cross-asset lesson #25 證實 RS 動量在 EM 單一國家 ETF（INDA/EWZ/FXI）全面失敗，
但 EWT（台灣）因半導體週期性驅動為例外。EWJ 為 DM 單一國家代表，本實驗
測試 RS 框架的適用性邊界。

### 進場條件與出場參數 (參考 EWT-007 並依 EWJ 1.15% 低波動縮放)

| Att | 參考基準 | RS 門檻 | 回撤範圍 | SMA 趨勢 | Part A Sharpe | Part B Sharpe | min(A,B) |
|-----|---------|--------|---------|---------|---------------|---------------|----------|
| Att1 | EFA | ≥2% | 1.5-4% | SMA(50) | 0.15 (10訊號, WR 60%) | 0.47 (4訊號, WR 75%) | 0.15 ✗ |
| Att2 | EFA | ≥3% | 2-5% | SMA(200) | 0.12 (5訊號, WR 60%) | 0.24 (3訊號, WR 67%) | 0.12 ✗ |
| Att3 | SPY | ≥3% | 2-5% | SMA(50) | 0.37 (7訊號, WR 71%) | **-0.24** (6訊號, WR 50%) | -0.24 ✗ |

出場參數統一：TP +3.5% / SL -4.0% / 持倉 20 天 / 冷卻 10 天

### 失敗根因分析

1. **Att1（EFA 基準、寬鬆條件）**：Part A 2 停損 + 2 到期訊號顯示 RS 訊號與均值回歸進場點不同步。Japan 相對 EAFE 的超額表現在 BOJ 政策轉向或日圓套息交易解除時集中爆發，而非持續週期性。
2. **Att2（收緊 RS + SMA(200)）**：訊號數驟降 10→5，過度過濾但未提升品質。FXI-007 Att2 的 SMA(200) 策略對中國有效（Part A -0.22→0.16），但對日本無類似改善效果，證實不同 EM/DM 市場需不同過濾機制。
3. **Att3（SPY 基準）**：Part A Sharpe 翻正至 0.37 但 Part B 崩潰至 -0.24，A/B 累計差距 14.16pp（+8.73% vs -5.43%）。5/6 的 Part B 訊號集中在 2025 年日圓急貶衝擊期，RS 訊號在日圓政策事件中完全反向。

### 關鍵發現

- **RS 動量（EWJ vs DM 基準）不適用**：無論 EFA（含 Japan 權重 ~22%）、SPY（美國寬基），Japan 的相對強度均由事件驅動而非結構性週期驅動。
- **SMA 趨勢過濾對 EWJ 無救援作用**：SMA(50) 和 SMA(200) 均無法隔離 BOJ 政策轉向期的假訊號。
- **擴展 cross-asset lesson #25**：RS 動量失敗模式不限於 EM 單一國家（INDA/EWZ/FXI），亦涵蓋 DM 單一國家（EWJ）。有效性先決條件：(a) 強週期性板塊驅動（如半導體 EWT/SOXL）或 (b) 個股層級持續性超額表現（如 TSM/NVDA 的先進製程護城河）。**政策/匯率/事件驅動的單一國家 ETF 均無效**。
- **EWJ-003 混合進場仍為全域最優**：EWJ-004 三次嘗試 min(A,B) 最佳 0.15，遠不及 EWJ-003 的 0.60。BB 下軌 + 回檔上限混合進場確認為 EWJ 最佳策略類型。

---

## EWJ-005：Post-Capitulation Vol-Transition MR ★ 當前最佳

### 目標 (Goal)

EWJ-003 Att3 達 Part A Sharpe 0.60（Part B 100% WR / std=0），Part A 為唯一瓶頸：
2022-09-01（BoJ pivot 不安）與 2023-08-03（殖利率飆升）兩筆 SL（每筆 -4.10%）
拖累 Sharpe。本實驗測試「Capitulation strength filter」（lesson #19 family）能否
過濾這兩筆 SL 同時保留高品質 winners。

跨資產脈絡：「2DD floor」於 USO-013 / EEM-014 / INDA-010 / VGK-008 全部成功，
「1d floor」於 SPY-009 成功（首例）。EWJ 1.15% vol 落在 lesson #19 已驗證 vol
區間內，先試 2DD floor 再試 1d floor。

### 迭代歷程 (Iteration History)

| Attempt | Filter | 閾值 | Part A Sharpe | Part B Sharpe | min(A,B) | 結果 |
|---------|--------|------|---------------|---------------|----------|------|
| Att1 | 2DD floor | <= -2.0% | 0.61 (7訊號 85.7% WR) | 0.00 std=0 (3訊號 100% WR) | 0.61 | △ 邊際 (+1.7%) |
| **Att2★** | **1d floor** | **<= -0.5%** | **0.70 (9訊號 88.9% WR)** | **0.00 std=0 (4訊號 100% WR)** | **0.70†** | **★ 最終選擇** |
| Att3 | 1d floor | <= -0.7% | 0.46 (6訊號 83.3% WR) | 0.00 std=0 (3訊號 100% WR) | 0.46 | ✗ 過嚴 |

### 進場條件 (Entry Conditions) — Att2★

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | BB 下軌觸及 | Close vs BB(20,1.5) lower | Close ≤ BB lower | 統計自適應超賣門檻（同 EWJ-003 Att3） |
| 2 | 回檔上限 | 10日高點回檔 | ≥ -7% | 隔離極端崩盤（同 EWJ-003 Att3） |
| 3 | 超賣確認 | Williams %R(10) | ≤ -80 | 10 日超賣區域 |
| 4 | 反轉跡象 | 收盤位置 (ClosePos) | ≥ 40% | 日內反轉確認 |
| 5 | 波動率飆升 | ATR(5)/ATR(20) | > 1.15 | 急跌恐慌過濾 |
| 6 | **Capitulation strength** | **1日報酬** | **≤ -0.5%** | **新增：要求訊號日為實質下跌（過濾 BB 下軌假觸碰）** |
| 7 | 冷卻期 | Cooldown | 7 天 | 防止同一波段重複進場 |

### 出場參數 (Exit Parameters) — Att2★

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +3.5% | 同 EWJ-003 Att3 |
| 停損 (SL) | -4.0% | 同 EWJ-003 Att3 |
| 最大持倉天數 | 20 天 | 到期出場 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 隔日開盤市價單 |
| 獲利出場 | 日內限價單 Day |
| 停損出場 | 停損市價單 GTC |
| 到期出場 | 隔日開盤市價單 |
| 滑價假設 | 0.1%（ETF） |
| 悲觀認定 | 同日觸及 TP 和 SL 時認定停損 |

### 設計理念 (Design Rationale)

- **lesson #19 family 跨資產移植**：USO/EEM/INDA/VGK 用 2DD floor 成功，SPY 用 1d floor 成功。EWJ 1.15% vol 與 VGK 1.12% 接近，先試 2DD floor。
- **Att1 失敗根因（2DD floor）**：EWJ Part A 兩筆 SL 的 2DD 為 -1.63% 與 -2.36%，winners 2DD 廣泛分布 +0.17%~-2.43%，2DD 維度區分力弱。-2.0% 過濾掉 6 筆 shallow-2DD winners 換取 1 筆 SL，淨改善僅 0.60→0.61。
- **Att2 成功根因（1d floor）**：EWJ Part A SLs 在 1d 維度為 -1.19%（2022-09-01）與 -0.49%（2023-08-03），1d -0.5% 邊界精準過濾後者。winners 1d 多在 -0.5%~-2.0%，邊界外的「淺 1d 訊號」實為「BB 下軌假觸碰但無實質下跌」，過濾後 Part A WR 84.6%→88.9%、Sharpe 0.60→0.70。
- **Att3 過嚴**：-0.7% 移除 3 筆淺 1d winners (2019-05-08/2019-08-02/2020-10-30 1d 為 -0.61%/-0.52%/-0.58%) 而未額外過濾任何 SL，淨損 Part A 訊號 9→6，Sharpe 0.70→0.46。
- **保留 EWJ-003 Att3 全部進場/出場參數**：僅新增單一品質過濾器，遵循 lesson #4「進場參數敏感度 >> 出場參數」；不調整出場以隔離 capitulation filter 效果。

### 回測結果 (Backtest Results) — Att2★

| 期間 | 訊號數 | 每年 | 勝率 | 累計報酬 | Sharpe | MDD | 狀態 |
|------|--------|------|------|----------|--------|-----|------|
| Part A (2019-2023) | 9 | 1.8 | 88.9% | +14.72% | **0.70** | -4.10% | 已完成 |
| Part B (2024-2025) | 4 | 2.0 | 100.0% | +14.75% | 0.00† | -2.09% | 已完成 |
| Part C (2026-) | 0 | 0.0 | - | +0.00% | 0.00 | 0.00% | 進行中 |

†Part B Sharpe 0.00 因 4 筆交易均回報 +3.50%（std=0），並非表現不佳而是零變異數的數學結果。

**A/B 訊號年化比:** 0.9:1（優秀）
**A/B 累計報酬差:** |14.72% - 14.75%| = **0.03pp**（近乎完美平衡）
**Part A Sharpe 0.70**（約束條件）> EWJ-003 Att3 的 0.60（+16.7%）

### 關鍵發現

1. **1d floor 在 EWJ 比 2DD floor 更有效**：EWJ 兩筆 Part A SLs 的 2DD 廣泛（-1.63% 與 -2.36%），但其中一筆的 1d -0.49% 恰位於 -0.5% 邊界外被過濾；2DD 維度上 winners 與 losers 重疊大，而 1d 維度有更清晰的閾值。
2. **EWJ 「淺 1d drift + BB 下軌假觸碰」失敗結構同 SPY**：EWJ-005 Att2 為 repo 第 2 例「1d floor」成功（首例 SPY-009），擴展 lesson #19 至非美 ETF。
3. **單一品質過濾器即可達 +16.7% Sharpe 改善**：遵循 lesson #4 不動出場，僅新增 1d floor 條件即達標，驗證進場過濾器精煉勝過出場參數調整。
4. **A/B 完美平衡**：累計差 0.03pp 為 EWJ 系列最佳，訊號比 0.9:1 優秀；驗證 1d floor 在 Part A/B 均勻過濾低品質訊號。

---

## EWJ-007：^VIX Forward-Looking Implied-Vol Regime-Gated MR（失敗，^VIX 對 EWJ 結構性無區分力）

### 目標 (Goal)

在 EWJ-005 Att2 全域最優框架（min(A,B)† 0.70）之上疊加 lesson #24 family
「forward-looking implied volatility regime gate」第七維度（^VIX），目標
surgical 過濾 EWJ-005 Att2 唯一殘餘 Part A SL **2022-09-01**（Powell
Jackson Hole 鷹派演說後 broad-market vol-acceleration 假設），同時保留
8 筆 Part A winners + 4 筆 Part B winners。**repo 首次 ^VIX 應用於非美
已開發單一國家寬基股票 ETF**（lesson #24 規則 #2：stock ETF → ^VIX）。

### 迭代歷程 (Iteration History)

| Attempt | ^VIX 維度 | 結果 | min(A,B) | 結論 |
|---------|-----------|------|----------|------|
| Att1 | 3d DIRECTION <= +5.0（XLU-013/USO-025 sweet-spot port） | Part A 7/85.7%/0.60 cum +10.82% / Part B 4/4 不變 | **0.60**（-14%） | FAILED：誤殺 2 winners，保留 SL |
| Att2 | 3d DIRECTION <= +3.0（加嚴，鏡像 EWZ-008 方法論） | Part A 5/80.0%/0.42 cum +5.78% / Part B 3/3（誤殺 2025-11-18） | **0.42**（-40%） | FAILED：方向錯誤加劇 |
| Att3 | LEVEL CAP <= 25.0（鏡像 EWZ-008 Att3） | Part A 5/5/nominal 2.97 / Part B 3/3 | **REJECT** | 非外科式 attrition（9→5/-44%、4→3/-25%） |

### 成交模型 (Execution Model)

沿用 EWJ-005 Att2：隔日開盤市價進場、滑價 0.1%、停損市價 GTC、
到期隔日開盤、TP +3.5% 限價、SL -4.0%、持倉 20 天、冷卻 7 天。

### 回測結果 (Backtest Results) — Att3（最終迭代，REJECT）

| 階段 | 訊號 | /年 | 勝率 | 累計報酬 | Sharpe | 最大回撤 | 狀態 |
|------|------|-----|------|----------|--------|----------|------|
| Part A (2019-2023) | 5 | 1.0 | 100.0% | +7.89% | 2.97† | -3.99% | 已完成（REJECT）|
| Part B (2024-2025) | 3 | 1.5 | 100.0% | +10.87% | 0.00† | -2.09% | 已完成 |
| Part C (2026-) | 0 | 0.0 | - | +0.00% | 0.00 | 0.00% | 進行中 |

†Att3 nominal Part A Sharpe 2.97 為退化零方差假象：LEVEL CAP <= 25
僅靠整片切除 ^VIX > 25 高波動 regime 過濾 SL 2022-09-01（VIX 25.56），
連帶切除 3 筆最強 +3.50% TP winners（2020-10-30 VIX 38.02 / 2022-09-29
VIX 31.84 / 2023-03-15 VIX 26.14）+ 1 筆 Part B winner（2025-03-11
VIX 26.92），存活集為 5 筆最弱 expiry（+0.90~+2.23%），無品質區分力。
依 lesson #14 + EEM-016 Att3「非外科式 attrition」標準 **REJECT**。

### 失敗根因分析

VIX-calibration trade-level 分析（^VIX 收盤值與 3/5/10 日變化）：

| 訊號日 | 結果 | ^VIX | 3d | 5d | 10d |
|--------|------|------|-----|-----|-----|
| 2019-05-08 | WIN +2.23% | 19.40 | +6.53 | +4.60 | +6.26 |
| 2019-08-02 | WIN +1.22% | 17.61 | +3.67 | +5.45 | +3.16 |
| 2020-10-30 | WIN +3.50% | 38.02 | +4.67 | +10.47 | +10.61 |
| 2021-05-04 | WIN +2.05% | 19.48 | +1.87 | +1.92 | +0.80 |
| 2021-07-19 | WIN +1.26% | 22.50 | +6.17 | +6.33 | +7.43 |
| **2022-09-01** | **SL -4.10%** | **25.56** | **-0.65** | **+3.78** | **+6.00** |
| 2022-09-29 | WIN +3.50% | 31.84 | -0.42 | +4.49 | +5.57 |
| 2023-03-15 | WIN +3.50% | 26.14 | +1.34 | +7.03 | +5.56 |
| 2023-10-02 | WIN +0.90% | 17.61 | -0.61 | +0.71 | +3.61 |
| 2024-04-17 (B) | WIN | 18.21 | +0.90 | +2.41 | +3.88 |
| 2024-06-13 (B) | WIN | 11.94 | -0.80 | -0.64 | -2.53 |
| 2025-03-11 (B) | WIN | 26.92 | +2.05 | +3.41 | +7.49 |
| 2025-11-18 (B) | WIN | 24.69 | +4.69 | +7.41 | +5.69 |

**核心結構性發現**：唯一綁定 Part A SL 2022-09-01 之 ^VIX（level 25.56
/ 3d -0.65 / 5d +3.78 / 10d +6.00）在 12 筆 winners 之 ^VIX 分布**每一
維度（level / 3d / 5d / 10d，cap 或 floor）皆居中交錯，無乾淨 separator**。
DIRECTION cap 因 SL 之 3d=-0.65（vol 持平/微降而非加速）方向錯誤；
LEVEL cap 僅能整片切除高波動 regime（連帶切除最強 panic winners，違反
lesson #14）。EWJ 殘餘失敗為 **idiosyncratic 日本特有**（BoJ 政策、
日圓套息平倉、出口週期）而非 global implied-vol regime outlier——與
EWJ-004「日本 RS 為事件驅動非結構性」結論平行。

### 關鍵發現

1. **lesson #24 ^VIX gate 對 EWJ 結構性無區分力**：精煉 lesson #24 適用
   邊界——^VIX gate 對「已開發市場單一國家股票 ETF」在殘餘 binding SL
   為 country-idiosyncratic（非 vol-regime isolated）時結構性失敗。
2. **邊界家族擴展**：與 EWZ-008（EM ^VIX 失敗，殘餘 SL 非 vol-isolated）、
   NVDA-018（^VXN 失敗）同屬「implied-vol gate 需殘餘 SL 集中於
   vol-regime-可區分失敗模式」邊界家族。
3. **EWJ-006 Att2 仍為全域最優**（7 次實驗、21 次嘗試），其 USDJPY direction filter
   為 EWJ bilateral FX direction 結構的最佳維度；EWJ-005 Att2 的 1d floor
   為 EWJ idiosyncratic capitulation 結構的最佳維度。

---

## 演進路線圖 (Roadmap)

```
EWJ-001 (回檔+WR+反轉K線+追蹤停損, Sharpe 0.16)
  └── EWJ-002 (波動率自適應+固定出場+崩盤隔離, Sharpe 0.55)
        ├── Att1 (ATR>1.15, 無回檔上限) → min 0.21 △
        ├── Att2 (ATR>1.15, 回檔上限 7%) → min 0.55
        └── Att3 (ATR>1.12, 回檔上限 7%) → min 0.41 ✗
EWJ-003 (BB 下軌均值回歸, Part A Sharpe 0.60)
  ├── Att1 (BB(20,2.0), 無回檔上限) → Part A 0.70/Part B 0.49 △
  ├── Att2 (BB(20,1.5), 無回檔上限) → Part A 0.26/Part B 1.01 ✗
  └── Att3 (BB(20,1.5) + 回檔上限 7%) → Part A 0.60/Part B 100%WR
EWJ-004 (RS 動量回調, 3 次嘗試均失敗)
  ├── Att1 (EFA ref, RS≥2%, SMA50) → min 0.15 ✗
  ├── Att2 (EFA ref, RS≥3%, SMA200) → min 0.12 ✗
  └── Att3 (SPY ref, RS≥3%, SMA50) → min -0.24 ✗ (確認 lesson #25 擴展至 DM)
EWJ-005 (Post-Capitulation Vol-Transition MR, Part A Sharpe 0.70)
  ├── Att1 (2DD floor <= -2.0%, VGK-008 移植) → Part A 0.61/Part B std=0 △ 邊際
  ├── Att2 (1d floor <= -0.5%, SPY-009 方向) → Part A 0.70/Part B 100%WR
  └── Att3 (1d floor <= -0.7%, 加嚴) → Part A 0.46/Part B std=0 ✗ 過嚴
EWJ-006 (USDJPY Direction Filter on Vol-Transition MR, Part A Sharpe 2.37) ★
  ├── Att1 (USDJPY 10d <= +2.0%, 寬鬆 baseline) → Part A 2.19/Part B std=0 △ 含邊緣 winner
  ├── Att2 (USDJPY 10d <= +1.0%, 甜蜜點) → Part A 2.37/Part B 100%WR ★ 新全域最優
  └── Att3 (USDJPY 10d <= +0.5%, 過緊) → Part A 2.31/Part B std=0 ✗ 過緊
EWJ-007 (^VIX Forward-Looking Implied-Vol Regime-Gated MR, 3 次嘗試均失敗)
  ├── Att1 (^VIX 3d DIR <= +5.0, lesson #24 sweet-spot port) → min 0.60 ✗ (-14%)
  ├── Att2 (^VIX 3d DIR <= +3.0, 加嚴) → min 0.42 ✗ (-40%)
  └── Att3 (^VIX LEVEL CAP <= 25.0) → nominal 2.97 ✗ REJECT (非外科式 attrition)
       └── 結論：^VIX 對 EWJ 結構性無區分力 (2022-09-01 SL 非任一 ^VIX 維度 outlier)
```

---

## EWJ-006：USDJPY Direction Filter on Vol-Transition MR ★ 當前最佳

### 目標 (Goal)

延伸 EWJ-005 Att2 框架（BB(20,1.5) 下軌 + 回檔上限 7% + WR + ClosePos + ATR>1.15 + 1d floor <= -0.5%），新增「USDJPY 方向過濾」作為 repo 首次 bilateral FX direction filter，目標過濾 EWJ-005 Att2 殘餘 Part A SL（2022-09-01 BoJ YCC 守成 SL）。

### 進場條件 (Entry Conditions)

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | BB 下軌觸及 | Close ≤ BB(20, 1.5) 下軌 | — | 同 EWJ-005 |
| 2 | 崩盤隔離 | 10日高點回檔 | ≥ -7% | 同 EWJ-005 |
| 3 | 超賣 | Williams %R(10) | ≤ -80 | 同 EWJ-005 |
| 4 | 收盤強勢 | ClosePos | ≥ 40% | 同 EWJ-005 |
| 5 | 波動率擴張 | ATR(5)/ATR(20) | > 1.15 | 同 EWJ-005 |
| 6 | Capitulation | 1日報酬 | ≤ -0.5% | 同 EWJ-005 Att2 甜蜜點 |
| 7 | **JPY 方向 (新增)** | **USDJPY 10日報酬** | **≤ +1.0%** | **過濾 JPY 急貶 currency drag region** |

### 出場與成交模型

- TP: +3.5%（limit_order Day GTC）
- SL: -4.0%（stop_market GTC）
- 持倉: 20 天（next_open_market 到期）
- 進場: next_open_market（隔日開盤市價）
- 滑價: 0.1%
- 冷卻期: 7 天

### 結果摘要

| 指標 | EWJ-005 Att2 | EWJ-006 Att2 ★ | 改善 |
|------|---------------|-----------------|------|
| Part A 訊號 | 9 | **7** | -2 (含 1 SL 過濾) |
| Part A WR | 88.9% | **100.0%** | +11.1pp |
| Part A Sharpe | 0.70 | **2.37** | **+239%** |
| Part A cum | +14.72% | **+19.31%** | +4.59pp |
| Part A MDD | -4.10% | **-3.99%** | -0.11pp |
| Part B 訊號 | 4 | 3 | -1 (2024-04-17 過濾) |
| Part B WR | 100% | **100%** | — |
| Part B Sharpe | 0.00 (std=0) | 0.00 (std=0) | — |
| min(A,B)† | 0.70 | **2.37** | **+239%** |

### 關鍵發現

1. **USDJPY 10d > +1.0% 為 BoJ 政策衝擊類失敗模式特徵**：2022-09-01 BoJ YCC 守成失敗（USDJPY 從 130 → 145 急升 region）為 EWJ-005 Att2 殘餘 Part A SL，本實驗成功過濾。
2. **+1.0% 為甜蜜點**：Att1 +2.0% 保留 1 個邊緣 winner（USDJPY 10d ∈ (+1.0%, +2.0%]）變異拖累 Sharpe；Att3 +0.5% 過緊移除 2 個 Part A winners + 1 個 Part B winner（2024-06-13 USDJPY 10d ∈ (+0.5%, +1.0%]）。
3. **副作用：過濾 2024-04-17 BoJ-anticipation Part B winner**（10d JPY 急貶 region），結構上仍屬「JPY 急貶 currency drag」高風險，過濾為合理保守決策。
4. **跨資產貢獻 lesson #24 family v8**：repo 首次 USDJPY/JPY direction filter 於任何資產。Lesson #24 family v1-v6 皆 implied vol，v7 候選 COPX-016 DXY spot FX index，本實驗為 v8 候選 bilateral FX direction（USD vs single foreign currency）於單一國家 ETF。
5. **新跨資產假設（待驗證）**：bilateral FX direction filter 適用「FX-sensitive 單一國家 ETF（EWJ/EWZ/EWT/INDA/FXI）+ ETF 計價貨幣 ≠ 標的國家貨幣 + 兩貨幣對具強結構性 driver」三條件。預期下一步移植目標：EWZ（USDBRL）、EWT（USDTWD）、INDA（USDINR）、FXI（USDCNH）。
