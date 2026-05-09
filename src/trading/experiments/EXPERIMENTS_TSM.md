<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-05-10
  data_through: 2025-12-31
  note_2026_05_10_tsm020: TSM-020 added 2026-05-10 (TSM-SOXX 20d Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback, **repo 首次「sector-internal anchor」變體於任何資產 — SOXX iShares Semiconductor ETF 為 TSM ~9% 權重 sector ETF（vs SMH ~12% 用於 entry RS trigger / QQQ TSM ~0% 直接權重 broad-market anchor / AAPL 主要客戶 anchor）**, cross-strategy port from TSM-013 (TSM-QQQ broad-market CEILING) — 直接回應 TSM-019 AI_CONTEXT 列出之未驗證方向 (a) SOXX 半導體指數 anchor). Three iterations all REJECT/TIE vs TSM-011 Att3 min 0.83. **Att1 PARTIAL** (max_relative_return_soxx=+0.10 loose ceiling) Part A **8/87.5% WR/Sharpe 1.23** cum +59.23% MDD -7.79%（vs baseline 12/83.3%/0.86/+74.10%, **+43% Sharpe / +4.2pp WR / -20% cum**）/ Part B **10/80%/Sharpe 0.83 cum +59.78% 完全 unchanged**（filter 對 Part B 完全非綁定，Part B 全部 10 訊號 TSM-SOXX 20d_div < +10% 通過 ceiling）/ min(A,B) **0.83 TIE baseline**（Part B binding，2024-07-16 SL + 2024-11-04 SL 之 TSM-SOXX 20d_div 皆 < +10%）/ A/B 年化 cum 11.85%/yr vs 26.4%/yr → gap **55% > 30% target ❌** / A/B 年化訊號比 1.6:5.0 = gap 68% > 50% ❌；**Att2 REJECT** (max_relative_return_soxx=+0.05 tight ceiling) Part A **0 signals 結構性過濾**（TSM-SMH RS ≥ +5% 進場條件下 TSM-SOXX 20d_div 結構性 > +5%，因 SMH TSM ~12% 權重對 TSM 漲幅吸收較多使 TSM-SMH < TSM-SOXX 自然關係）/ Part B 2 signals 1W/1L Sharpe **0.06** cum +0.34%（嚴重退化，cooldown chain shift 引入新 trade pattern）/ min(A,B) **0.06 REJECT**（-93% vs baseline 0.83）；**Att3 REJECT** (max_relative_return_soxx=+0.07 medium ceiling 甜蜜點探尋) Part A 4/75.0%/Sharpe **1.06** cum +21.83% MDD -6.73%（**Part A 訊號 12→4 過嚴流失 8 訊號 cum -71%**）/ Part B 5/80%/Sharpe **0.83** cum +26.40% MDD -10.23%（**Part B 訊號 10→5，A/B 年化 cum 4.37%/yr vs 13.2%/yr → gap 67% > 30% ❌、A/B 年化訊號比 0.8:2.5 = gap 68% > 50% ❌**）/ min(A,B) **0.83 TIE baseline 但雙 acceptance criteria 違反 → REJECT**。**核心失敗發現（lesson #20 v3 family v11 邊界擴展，repo 首次 sector-internal anchor 變體於任何資產）**：(1) **Repo 首次「sector-internal anchor」變體於任何資產**——既有 cross-asset divergence regime gate anchor 類別：(a) broad-market benchmark（QQQ/SPY/EEM, TSM-013 ✗ / TLT-014 ✓ / NVDA-021 ✓）、(b) 主要客戶 single-stock（AAPL, TSM-015 ✗）、(c) 同類資產對等（EFA-EEM, EEM-017 ✗）、(d) sub-component anchor（FXI vs EEM, EEM-019 ✗）；TSM-020 加入 (e) sector-ETF anchor（SOXX vs single-stock TSM）為新類別；(2) **TSM-SOXX 維度與 entry RS condition 結構性耦合**——TSM-SMH ≥ +5% RS entry condition 結構性使 TSM-SOXX 20d_div 必然 > +5%（SMH 較 SOXX 對 TSM 吸收效應更強，因 TSM 權重 SMH ~12% > SOXX ~9%），**Att2 +5% threshold 為結構性下界**；sweet spot 介於 +5%（過嚴）與 +10%（loose 不綁定 Part B）之間結構性窄帶 [+7%, +10%]，但於 [+7%, +10%] 區間 Part A SLs 與 Part B SLs 在 TSM-SOXX 維度仍與 winners 分布重疊（同 TSM-013/014 QQQ 維度結論），**單一 sector-ETF 維度結構性無 winner-vs-SL 區分力**；(3) **Part B 2024-07-16 / 2024-11-04 SLs 在 TSM-SOXX 20d_div 維度落於 winners 分布中段**——repo 第 8 次確認 TSM Part B SLs 在「single dimension cross-asset divergence」結構性與 winners 重疊（TSM-013 QQQ / TSM-014 QQQ BAND / TSM-015 AAPL / TSM-016 BB-Width / TSM-017 earnings / TSM-018 ATR BAND / TSM-019 VIX term structure / TSM-020 SOXX，跨 8 維度結構性無解）；(4) **新跨資產規則（lesson #20 v3 family v11 邊界）**：sector-ETF anchor 適用邊界 = 「target stock 為非 sector ETF 大權重成分股（target weight in anchor < 5%）」+「Part A/B SLs 在 sector divergence 維度單向對齊」雙條件；TSM ~9% 權重 SOXX 自我參考稀釋程度可接受但 SLs 在維度內無區分力，違反第二條件；(5) **TSM Part B 0.83 binding constraint 第 8 次結構性無解確認**——TSM-013/014/015/016/017/018/019/020 共 8 次嘗試確認 TSM 為 Sharpe-1.0 結構性難突破資產（已驗證 8 大維度全失敗：QQQ CEILING / QQQ BAND / AAPL anchor / BB-Width / earnings exclusion / ATR BAND / VIX term structure / **SOXX sector anchor**）；剩餘未驗證方向：(a) Multi-customer ensemble (AAPL + MSFT + NVDA voting)，(b) 完全替代 framework (BB Squeeze Breakout / MR / lesson #22 multi-week regime + RS Momentum 組合)，(c) Volume-normalized z-score (rolling z-score 替代 absolute ratio threshold)。TSM 第 20 次實驗、60+ 次嘗試，TSM-011 Att3 仍為 min(A,B) 全域最優。
  note_2026_05_09_tsm019: TSM-019 added 2026-05-09 (VIX Term-Structure (^VIX3M / ^VIX) Regime Gate on RS Momentum Pullback，**repo 首次 VIX term structure 維度（^VIX3M / ^VIX 比率）於任何資產 + lesson #24 family v9 候選 forward-looking IV term structure derivative 維度**, cross-strategy port from existing lesson #24 family LEVEL/DIRECTION variants - 直接回應 TSM-018 AI_CONTEXT 列出之未驗證方向). Three iterations all REJECT/TIE vs TSM-011 Att3 min 0.83. **Att1**（VIX3M/VIX <= 1.15 CEILING lenient）Part A 6/66.7%/Sharpe **0.42** cum +17.44% / Part B 8/75.0%/Sharpe 0.65 cum +36.98% / min(A,B) **0.42 REJECT**（-49% vs baseline）— CEILING 1.15 過濾 deep contango 訊號（Part A winners 多在 1.15-1.24 range 被誤殺：1.168/1.215/1.238/1.174/1.155/1.168/1.190 共 7 winners 過濾），cooldown chain shift 引入 2024-07-11 SL 替換 2024-07-16 SL（淨 SL 不變但時間偏移）。**Att2**（VIX3M/VIX >= 1.115 FLOOR，過濾 Part A SLs 1.106/1.110）Part A **9/88.9% WR/Sharpe 1.11 cum +60.65% MDD -8.42%** (vs baseline 12/83.3%/0.86, **+29% Sharpe / +5.6pp WR / -18% cum 但 MDD 改善**) / Part B **5/80.0%/Sharpe 0.83 cum +26.40%**（**與 baseline 0.83 完全相同**——cooldown chain shift 將 baseline 2024-10-30 SL 過濾後激活 2024-12-27 TP 替換 2024-12-19 TP，淨效果為 5 winners 過濾 + 1 SL 過濾，2024-07-16 SL 仍存活 ratio 1.130 > 1.115）/ min(A,B) **0.83 TIE baseline** / A/B 年化 cum 12.13%/yr vs 13.20%/yr → gap **8.1% < 30% ✓** / A/B 累計差 |60.65-26.40|/60.65 = **56.5% > 30% target ❌**（年化 cum gap 達標但**累計差違反 30% 目標**，因 Part A 5 年期累積 vs Part B 2 年期累積稀釋使絕對累計差超標）/ A/B 訊號比 1.8:2.5 = 1.39:1（gap 28% < 50% ✓）。**Att3**（VIX3M/VIX >= 1.10 FLOOR lenient ablation）Part A 11/72.7%/Sharpe **0.58** cum +44.35%（max consec losses **3**，cooldown chain shift 引入 3 連 SLs）/ Part B 6/66.7%/Sharpe **0.42** cum +17.44% / min(A,B) **0.42 REJECT**（-49% vs baseline）— FLOOR 1.10 對 Part A SLs 1.106/1.110 仍非綁定（1.10 < 1.106/1.110 = 兩 SL 仍存活），同時切除若干 winners 觸發 cooldown chain shift 連鎖負面。**核心失敗發現（lesson #24 family v9 邊界擴展，repo 首次 VIX term structure 於任何資產）**：(1) **Repo 首次 VIX term structure (^VIX3M / ^VIX) 維度於任何資產**——既有 lesson #24 family v1-v8 維度均為 implied vol LEVEL（^VIX/^MOVE/^GVZ/^OVX/^VXN）或 DIRECTION（X 日變化），尚未驗證 term structure（^VIX3M vs ^VIX）；(2) **Att2 partial-success 結構**：trade-level 分析顯示 Part A 2 SLs（2022-11-21 ratio 1.106 / 2022-12-07 ratio 1.110）皆 < 1.115 被乾淨過濾 ✓ 但 cooldown chain shift 引入 2022-11-28 新 SL（chain shift 中性化部分 selectivity，net SL 2→1 改善），Part B 2024-07-16 SL ratio 1.130 > 1.115 結構性逃逸過濾，2024-10-30 SL ratio 1.020 過濾 ✓ 但 cooldown chain shift 引入 2024-12-27 TP 替換原 2024-12-19 TP；(3) **TSM Part A vs Part B SLs 在 VIX3M/VIX 維度結構性反向**：Part A SLs（mid contango 1.106-1.110）vs Part B SLs（雙極端 1.020 + 1.130），單一 FLOOR threshold 結構性無法雙 Part 同步改善——同 TSM-013 (QQQ CEILING) / TSM-014 (QQQ BAND) / TSM-015 (AAPL anchor) / TSM-016 (BB-width) / TSM-017 (earnings) / TSM-018 (ATR BAND) 失敗模式平行；(4) **新跨資產規則（lesson #24 family v9 邊界）**：VIX term structure (^VIX3M / ^VIX) 適用邊界 = 「target 之 SLs 在 term structure 維度為**單向集中分布**（單側極端 contango 或 backwardation）」+「Part A 與 Part B SLs 同向對齊」雙條件；TSM 違反兩條件——SLs 跨 ratio 1.020-1.130 廣泛分布且 Part A/B 反向，term structure 維度結構性無區分力；(5) **TSM Part B 0.83 binding constraint 第 7 次結構性無解確認**——TSM-013/014/015/016/017/018/019 共七次嘗試確認 TSM 為 Sharpe-1.0 結構性難突破資產，剩餘未驗證方向： (a) SOXX 半導體指數 anchor (TSM 為 SOXX 成分股自我參考但仍可試), (b) Multi-customer ensemble (AAPL + MSFT + NVDA voting), (c) 完全替代 framework (BB Squeeze Breakout / MR / lesson #22 multi-week regime + RS Momentum 組合), (d) Volume-normalized z-score (rolling z-score 替代 absolute ratio threshold)。TSM 第 19 次實驗、57+ 次嘗試，TSM-011 Att3 仍為 min(A,B) 全域最優（Att2 為「Part A breakthrough but A/B cum gap 違反 + Part B 不變」第 7 次同模式 partial-success）。
  note_2026_05_09_tsm018: TSM-018 added 2026-05-09 (ATR(5)/ATR(20) BAND Volatility-Acceleration Filter on RS Momentum Pullback，**repo 首次 ATR ratio BAND 變體於 RS Momentum 框架**, cross-strategy port from CIBR-014 / FXI-014 / URA-013 - 直接回應 TSM-017 AI_CONTEXT 列出之未驗證方向 (d) Volatility-Acceleration BAND filter). Three iterations all REJECT vs TSM-011 Att3 min 0.83. **Att1**（atr_ratio ∈ (1.15, 1.40] CIBR-014 直接移植）Part A 6/50.0%/Sharpe **-0.03** cum -2.35% (3 SLs) / Part B 5/80.0%/Sharpe 0.83 cum +26.40% / min(A,B) **-0.03 REJECT**（-104% vs baseline）— BAND 過嚴切除 6 個 Part A 訊號（原 12 → 6），cooldown chain shift（lesson #19）引入 3 個新 SLs（2021-01-22 / 2022-01-13 三筆 ATR ratio 均處於 (1.15, 1.40] 中段）。**Att2**（atr_ratio ∈ (1.00, 1.20] 放寬至 RS Momentum 訊號日典型加速度區間）Part A 4/75.0%/Sharpe **0.65** cum +17.04% / Part B 5/60.0%/Sharpe **0.27** cum +8.74% / min(A,B) **0.27 REJECT**（-67% vs baseline）— Part B 退化嚴重，cooldown chain shift 將原 baseline Part B 兩個 SLs（2024-07-16 / 2024-10-30）替換為 (2024-07-08 / 2024-11-01) 兩個新 SLs，淨效果為 SLs 數量未減反增（baseline 2 → Att2 2，但 winners 5 → 3）。**Att3**（atr_ratio_floor=0.50 非綁定 + ceiling 1.10 CEILING-only 過濾 in-crash acceleration）Part A 6/66.7%/Sharpe **0.65** cum +24.63% / Part B 6/83.3%/Sharpe **0.98** cum +36.52%（**Part B +18% vs baseline 0.83**）/ min(A,B) **0.65 REJECT**（-22% vs baseline）— Part B 改善，但 Part A 退化至 0.65（-24%）；A/B 累計差 32.6% > 30% target ❌。**核心失敗發現（lesson #15 family v3 cross-strategy 邊界擴展，repo 首次 ATR BAND 於 RS Momentum 框架）**：(1) **Repo 首次 ATR ratio BAND 於 RS Momentum 框架失敗**——既有成功案例 CIBR-014 / FXI-014 / URA-013 皆為 MR 框架（capitulation 訊號日 ATR 結構性高 1.15+），TSM RS Momentum Pullback 訊號日為「上升趨勢中淺回檔」ATR ratio 集中於 1.0-1.15 較窄帶，BAND 無區分力；(2) **Part A/B SLs 在 ATR ratio 維度反向**：Part A SLs（2021-01 / 2022-01 / 2023-01 macro shock 拉回）ATR ratio 高（>1.15），Part B SLs（2024-07-16 / 2024-10-30 earnings/macro pullback）ATR ratio 1.10-1.20 中段，**單一 BAND 結構性無法雙 Part 同步改善**——同 TSM-013/014/015/016/017 失敗模式平行；(3) **lesson #19 cooldown chain shift 在 RS Momentum + ATR BAND 組合下結構性放大反向選擇**——Att2 過濾 baseline 兩個 Part B SLs 但 chain shift 引入兩個新 SLs，淨效果零改善；(4) **TSM Part B 0.83 binding constraint 第 6 次結構性無解確認**——TSM-013/014/015/016/017/018 共六次嘗試確認 TSM 為 Sharpe-1.0 結構性難突破資產，未來方向應為 (a) SOXX 半導體指數 anchor, (b) Multi-customer ensemble (AAPL + MSFT + NVDA voting), (c) 完全替代 framework, (d) Volume-normalized z-score（vs absolute ratio threshold）。TSM 第 18 次實驗、54+ 次嘗試，TSM-011 Att3 仍為 min(A,B) 全域最優。
  note_2026_05_09_tsm017: TSM-017 added 2026-05-09 (Earnings-Date Exclusion Filter on RS Momentum Pullback，**repo 首次 earnings-date calendar exclusion filter 於任何資產**, 直接回應 TSM-016 Att3 失敗報告 earnings-week SL cluster 假說 + AI_CONTEXT 列出之未驗證方向). Three iterations all REJECT vs TSM-011 Att3 min 0.83. **Att1**（asymmetric -10/+15 calendar days，25 日總窗口）Part A 7/71.4%/Sharpe **0.42** cum +19.28%（Part A -51% Sharpe）/ Part B 6/83.3%/Sharpe **0.98** cum +36.52%（**Part B +18% Sharpe**）/ min **0.42 REJECT**（-49% vs baseline）— 過寬窗口切除 5 個 Part A 訊號，Part B 過濾 2024-07-16 + 2024-10-30 兩 SLs 但 cooldown chain shift 引入 2024-11-04 SL（+18d post Q3，超出 +15 窗口）。**Att2**（bilateral ±5 calendar days，11 日窗口）Part A 10/80.0%/Sharpe **0.71** cum +49.26%（-17% vs baseline）/ Part B 7/85.7%/Sharpe **1.11** cum +47.44%（**+34% vs baseline 0.83**）/ min **0.71 REJECT**（-14% vs baseline）— 2024-07-16 SL 過濾後激活 2024-06-27 TP（淨 +1 winner Part B），但 2024-10-30 SL 替換為 2024-10-23 SL（同樣 SL，淨 wash）。**Att3**（bilateral ±2 calendar days，5 日窗口，最緊邊界）Part A 11/81.8%/Sharpe **0.78** cum +61.20%（-9% vs baseline）/ Part B 7/85.7%/Sharpe **1.11** cum +47.44%（同 Att2，+34% vs baseline）/ min **0.78 REJECT**（-6% vs baseline）— Part A 僅損失 1 訊號（最佳保留），但 A/B 年化幾何 cum 差 |10.0%-21.4%|/21.4% = **53% > 30% target ❌**（Part B 受限於 2 年 sample 高度集中於 2024-2025 bull regime 使年化稀釋）。**核心失敗發現（lesson #20b 失敗家族擴展，repo 首次 earnings-date exclusion filter 於任何資產）**：(1) **時間維度 filter 與價格/成交量 filter 正交但仍受日期重疊限制**——TSM Part B 殘餘 SLs（2024-07-16 -2d / 2024-10-30 +13d）與 winners（2024-04-16 -2d / 2025-01-13 -3d / 2023-01-19 +7d）在 earnings-relative 日期維度結構性重疊，**不存在單一窗口配置同時過濾全部 SLs 並保留全部 winners**：對稱 ±2 過濾 2024-07-16 SL ✓ 與 2024-04-16 winner ✗（1:1 wash）；非對稱 -2/+14 過濾兩 SLs ✓ 但同時誤殺兩 winners ✗（2:2 wash）；後置 only +14 過濾 2024-10-30 SL ✓ 但誤殺 2023-01-19 winner ✗（1:1 wash）。(2) **Part A 退化機制**：Part A 包含多個 earnings-adjacent winners（2020-2023 期間半導體 cycle 拉抬 + earnings momentum continuation），任何時間窗口擴大皆切除 Part A winners 多於 Part A SLs（baseline Part A 只有 2 SLs，2022-11-21 / 2022-12-07 均不在 earnings 附近）。(3) **Part B 改善 +34% 為「earnings-week SL cluster」確認**——TSM-016 Att3 假設成立：Part B SLs 集中於 earnings ±15 日帶；但同時 Part B winners（2024-04-16 / 2025-01-13）亦集中於 earnings 前 2-3 日，**winner/SL 在時間維度為共生分布**而非可分離 cluster。(4) **新跨資產規則（lesson #6 邊界 + lesson #20b 擴展）**：earnings-date exclusion filter 適用邊界 = 「target 之 earnings-adjacent 訊號分布 winner-SL 比例顯著高於 non-earnings 訊號分布」。TSM 違反該條件——半導體個股 earnings momentum 與 earnings risk 兩股力量平衡。預期適用候選：fundamentals-driven 個股（financial / consumer / healthcare），earnings 為 dominant catalyst 使 winner/SL 比例顯著偏移；不適用於：cyclical individual stocks（半導體 / energy / commodity）earnings 為次要 catalyst。(5) **TSM Part B 0.83 binding constraint 第 5 次結構性無解確認**——TSM-013/014/015/016/017 共五次嘗試確認 TSM 為 Sharpe-1.0 結構性難突破資產，未來方向應為 (a) SOXX 半導體指數 anchor（注意 TSM 為成分股自我參考）, (b) Multi-customer ensemble (AAPL + MSFT + NVDA voting), (c) 完全替代 framework（lesson #22 multi-week regime + RS Momentum 組合），(d) Volatility-Acceleration BAND filter（CIBR-014/FXI-014 路徑）。TSM 第 17 次實驗、51+ 次嘗試，TSM-011 Att3 仍為 min(A,B) 全域最優。
  note_2026_05_09_tsm016: TSM-016 added 2026-05-09 (BB-Width Regime Gate on RS Momentum Pullback，**repo 首次 lesson #23 BB-Width Regime Gate cross-strategy 移植至 RS Momentum 框架（既有 TLT/TQQQ/SOXL 皆為 MR 或 leveraged ETF）**, cross-strategy port from TLT-007 / TQQQ-018 / SOXL-012). Three iterations all REJECT/PARTIAL vs TSM-011 Att3 min 0.83. **Att1**（bb_width_max=0.15 lenient）Part A 5/100% std=0 cum +46.93%（過濾 7 訊號含 2 Part A SLs）/ Part B 6/66.7%/Sharpe **0.42** cum +17.44% / min **0.42 REJECT** — **lesson #19 cooldown chain shift 中性化**：原 2024-07-16 SL 被替換為 2024-07-08 SL，原 2024-10-30 SL 被替換為 2024-11-01 SL，淨效果 SL 數量未減少；**Att2 ★ PARTIAL**（bb_width_max=0.12 medium）Part A **3/100% std=0 cum +25.97%** / Part B **2/100% std=0 cum +16.64%** / min(A,B)† **雙 Part 結構性零方差**（repo 第 6 次雙 Part std=0 結構，繼 EWJ-005/EWT-008/SPY-009/DIA-012/IWM-013/CIBR-014 後）— **0.12 閾值同步過濾 baseline 雙 Part 全部 4 SLs + chain-shifted Att1 新增 2 SLs**，6 SLs 全清除；A/B 年化幾何 cum 差 |4.7%-8.0%|/8.0% = **41% > 30% target ❌**（A/B 樣本數小 + Part A 5 年期 vs Part B 2 年期幾何稀釋使 cum gap 略超目標），A/B 年化訊號比 0.6:1.0 = gap 33% < 50% ✓；**Att3 REJECT**（bb_width_max=0.14 sweet-spot test）Part A 3/100% std=0 同 Att2 / Part B 6/33.3%/Sharpe **-0.29** cum -13.08% (4 SLs)/ min **-0.29 REJECT** — 0.14 閾值同時放回 cooldown chain 觸發的 earnings-week SLs（2024-10-16 T-1 to earnings 10/17、2025-01-16 同日 earnings、2024-11-01 chain shift），sweet spot 區間極窄（0.12 唯一甜蜜點）。**核心發現（lesson #23 family v4 cross-strategy 邊界擴展，repo 首次發現）**：(1) **Repo 首次 lesson #23 BB-Width Regime Gate 移植至 RS Momentum 框架**——既有 TLT-007 (1% vol MR, 閾值 0.05) / TQQQ-018 (~5% vol leveraged broad index, 0.48) / SOXL-012 (~6% vol leveraged sector, 0.43) 皆為 MR 或 leveraged ETF，TSM ~2% vol 半導體 ADR 個股 + RS Momentum 框架為新類別；(2) **TSM 適用閾值 0.12** 落於既有 4 個成功案例的對數線性區間（更貼近 vol 0-3% 區間的 [0.05, 0.20] 帶）；(3) **新跨資產規則（lesson #23 family v4 + lesson #19 family v15 整合）**：BB-Width Regime Gate 適用於非槓桿 momentum 框架但受 lesson #19 cooldown chain shift 影響，sweet spot 區間極窄（0.01-pt 偏離即崩壞）；(4) **「regime gate 對小 sample 策略」共通邊界（A/B cum gap 結構性發現）**：當基底框架已將 sample 壓低（baseline 12+10），regime gate 進一步切除使年化幾何 cum 差難維持 < 30%；此規則與 EWJ-005/SPY-009/IWM-013 等大 sample 案例形成對照，解釋 TSM-013 Att1 (Part A zero-var) 與 TSM-016 Att2 (雙 Part zero-var) 同樣為「結構性最優但 cum gap 違反」的對應；(5) **TSM Part B Sharpe ceiling 仍未真正突破** — 雖 Att2 雙 Part std=0 為結構性最優，但 sample 過小 (3+2 vs baseline 12+10) 使 cross-validation 信心不足；TSM-013/014/015/016 共四次嘗試確認 TSM 為 Sharpe-1.0 結構性難突破資產，未來方向應為 (a) earnings-date exclusion filter（Part B SLs 集中於 earnings ±15 日，TSM-016 Att3 失敗證實 0.14 閾值放回 earnings-week SLs）, (b) SOXX 半導體指數 anchor, (c) 完全替代 framework（lesson #22 multi-week regime + RS Momentum 組合）. TSM 第 16 次實驗、48+ 次嘗試，TSM-011 Att3 仍為 min(A,B) 全域最優（baseline std=0 結構性最優級別 Att2 因 A/B cum gap 41% 邊際違反不取代為主排序最優）。
  note_2026_05_09_tsm015: TSM-015 added 2026-05-09 (TSM-AAPL 20d Cross-Asset Divergence Regime-Gated RS Momentum Pullback, **repo 首次 AAPL 主要客戶 anchor 試驗於任何資產 + repo 首次同一 target 雙 anchor stack 結構（QQQ + AAPL）**, 直接回應 TSM-013/014 「需嘗試不同 anchor」建議). Three iterations all REJECT/TIE vs TSM-011 Att3 min 0.83. **Att1** (AAPL FLOOR=-5% only) Part A 11/81.8%/Sharpe **0.78** cum +61.20% / Part B 10/70%/Sharpe **0.50** cum +37.45% / min(A,B) **0.50 REJECT** — FLOOR -5% 過濾 baseline 2024-07-08 SL 但 lesson #19 cooldown chain shift 引入 2024-07-16 + 2025-01-16 兩個新 SL，Part B 退化 -40%。Part A 損失 1 winner（baseline 12→11，FLOOR 對 1 個 Part A winner Rel_AAPL_20d < -5%）；**Att2** (AAPL BAND [-7%, +5%]) Part A **3**/100%/std=0 cum +25.97% / Part B 6/66.7%/Sharpe **0.42** cum +17.44% / min(A,B)† **0.42 REJECT** — CEILING +5% 過嚴 over-filter Part A 12→3（**Part A winners 結構性集中於 [+5%, +10%] Rel_AAPL_20d 範圍**，CEILING +5% 移除 9 個 Part A 訊號 8 winners + 1 SL）；**Att3** (AAPL FLOOR=-7% lenient + TSM-QQQ CEILING=+15% dual-anchor stack) Part A 9/100%/std=0 cum +99.90% MDD -6.06% / Part B 10/80%/Sharpe **0.83** cum +59.78% / min(A,B)† **0.83 TIE baseline** — **AAPL FLOOR -7% 對 baseline 全部 19 訊號完全非綁定**（Part B SLs 2024-07-08 與 2024-10-30 之 Rel_AAPL_20d 皆 > -7%），結果與 TSM-013 Att1（QQQ CEILING only）完全相同。**核心失敗發現（lesson #20 v3 family v11 邊界擴展，repo 首次拒絕 customer-anchor 假說）**：(1) **AAPL anchor 對 TSM 不具 orthogonal selectivity**——AAPL FLOOR 維度 Part B SLs 結構性 > -7%，AAPL CEILING 維度與 Part A winners 結構性重疊 [+5%, +10%]，雙向皆非 SLs vs winners 區分維度；(2) **拒絕 "customer-anchor" 跨資產假說於 TSM**——TSM Part B 2024-07-08 SL 雖屬「Trump Taiwan comments TSM-specific 急跌」，trade-level 顯示 AAPL 同步走弱（同樣受 Trump 對中國科技政策表態波及），TSM 與 AAPL 在 macro shock 期間共動性高於假說預期；2024-10-30 SL 為「Q3 earnings rally exhaustion」，TSM 經 Q3 earnings rally 後 vs AAPL 持平 → +7% Rel_AAPL，落於 Part A winners 分布 [+5%, +10%] 範圍中段，**單一 CEILING 結構性無法區分 winner vs loser**；(3) **Repo 首次「同一 target 雙 anchor stack」失敗**——TSM-QQQ + TSM-AAPL 雙 anchor 因 AAPL FLOOR 結構性非綁定退化為單 anchor (TSM-QQQ CEILING)，**雙 anchor stack 需兩 anchor 維度皆對 SLs 具區分力為先決條件**；(4) **新跨資產規則（lesson #20 v3 v11）**：cross-asset divergence anchor 適用邊界擴展為「anchor 必須與 target SLs 在 N-day return 維度上具非零互信息」——customer-anchor (AAPL) 與 TSM 在 macro shock 期共動，與 single-stock fundamental (rally exhaustion) 維度重疊於 target winners，雙向皆無區分力；(5) **TSM Part B 0.83 binding constraint 第 3 次結構性無解確認**——TSM-013 (QQQ CEILING) + TSM-014 (QQQ BAND) + TSM-015 (AAPL anchor) 三次嘗試確認 Rel_QQQ_20d / Rel_AAPL_20d 對 Part B 結構性無區分力，未來需嘗試 (a) SOXX 半導體指數 anchor (但需注意 TSM 為 SOXX 成分股), (b) AAPL/MSFT/NVDA 多客戶 ensemble voting, (c) 完全替代 framework (BB Squeeze Breakout / MR / lesson #22 multi-week regime), (d) earnings-date exclusion filter（Part B SLs 集中於 earnings 前後 5-10 日）. TSM 第 15 次實驗、45+ 次嘗試，TSM-011 Att3 仍為 min(A,B) 全域最優。
  note_2026_05_09_tsm014: TSM-014 added 2026-05-09 (TSM-QQQ 20d Cross-Asset Divergence BAND Regime-Gated RS Momentum Pullback, **repo 首次 cross-asset divergence regime gate 雙向 BAND 變體（FLOOR + CEILING）於任何資產**, 直接回應 TSM-013 揭露之「Part A SLs 高 Rel_QQQ vs Part B SLs 低 Rel_QQQ」結構性反向假說). Three iterations all REJECT/TIE vs TSM-011 Att3 min 0.83. Att1 (FLOOR=-5%, CEILING=+15% 繼承 TSM-013 Att1) min(A,B) **0.83 TIE** — FLOOR -5% 對 baseline 全部 19 訊號 (9 Part A + 10 Part B) 完全非綁定，trade-level 顯示 Part B SLs 之 Rel_QQQ_20d 為 +4.10% (2024-07-16) / +7.63% (2024-10-30)，**遠高於假說預期的「低 Rel_QQQ」**，落於 Part B winners 分布中段 (winners +1.48% ~ +12.37%)；Att2 (FLOOR=+5%) min(A,B) **0.74 REJECT (-11%)** — 過濾 2024-07-16 SL (+4.10%) 但同時過濾 2024-12-19 winner (+1.48%)，cooldown chain shift 引入 2025-01-16 SL 替換原 2025-01-10 TP，淨效果 Part B 10/8TP/2SL → 9/7TP/2SL (WR 80%→77.8%, Sharpe 0.83→0.74)；Att3 (FLOOR=+8% 過濾兩個 Part B SLs) min(A,B) **0.42 REJECT** — Part A 過濾 2 winners (Rel_QQQ +5.89%/+7.55%/+7.58% 多筆) 7/100% zero-var cum +71.38% / Part B 6/66.7% Sharpe 0.42（cooldown chain shift 引入額外 SLs，反向擴散）。**核心失敗發現（lesson #19/#26 family v3 邊界擴展，repo 首次拒絕 cross-asset divergence BAND 變體）**：(1) **TSM Part B SLs 結構性處於 Rel_QQQ_20d 中段非極端**——TSM-013 declare 之「Part B SLs 低 Rel_QQQ」為**過度概括**，實際 trade-level 分析顯示 2024-07-16 SL (+4.10%) 與 2024-10-30 SL (+7.63%) 散落在 Part B winners 分布 +1.48%~+12.37% 範圍內，**單一 Rel_QQQ 維度無區分力區分 winner vs loser**；(2) **BAND 變體有效邊界**：lesson #15 ATR ratio BAND 成功（URA-012 / FXI-014 / CIBR-014）因該 ATR 維度上 SLs 集中於兩極端（高 / 低 ATR 鏡像）；TSM-014 失敗於「Rel_QQQ 維度 SLs 散落非極端」結構，**BAND 結構需 SLs 集中於兩極端為先決條件**，否則 FLOOR + CEILING 同樣不具選擇力，徒增 cooldown chain shift 副作用；(3) **新跨資產規則 (lesson #15 + lesson #20 family v4)**：cross-asset divergence regime gate 適用邊界三條件：(a) target 為 narrow-scope vs broad benchmark, (b) Part A/B SLs 在 divergence 維度單向對齊 (CEILING 或 FLOOR), (c) 若 SLs 雙向反向，需驗證 SLs 是否集中兩極端方可採 BAND 變體；TSM 違反 (b) 與 (c)，BAND 變體擴展同樣失敗；(4) **TSM Part B 0.83 binding constraint 結構性無解**——TSM-013 (CEILING) + TSM-014 (BAND) 兩次嘗試確認 Rel_QQQ_20d 維度對 Part B 結構性無區分力，未來需嘗試 (a) 不同 anchor (如 SOXX 半導體指數 / AAPL 主要客戶 / NVDA 已驗證 pair 失敗), (b) 不同 lookback (5d/60d), (c) 完全替代 framework (跳脫 RS Momentum Pullback 至 BB Squeeze Breakout 或 MR)。TSM 第 14 次實驗、42+ 次嘗試，TSM-011 Att3 仍為 min(A,B) 全域最優。
  note_2026_05_08_tsm013: TSM-013 added 2026-05-08 (TSM-QQQ 20d Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback, **repo 第 6 次 cross-asset divergence regime gate 跨資產移植、首次半導體 ADR 個股 + RS Momentum Pullback 框架**, cross-asset port from NVDA-021 (NVDA-QQQ CEILING + MBPC) / mirror INDA-012 / EWZ-009). Three iterations all PARTIAL/REJECT vs TSM-011 Att3 min 0.83. **Att1 ★ PARTIAL** (lookback=20, max_relative_return=+0.15 loose ceiling) Part A **9 訊號 / WR 100% / Sharpe 0.00 zero-var (9/9 TPs) / cum +99.90% / MDD -6.06%**（vs baseline 12/83.3%/0.86/+74.10%/-7.89%, **cum +35% / WR +17pp / MDD -23%**, 過濾 baseline 全部 2 SLs + 1 winner）/ Part B **10 訊號完全 unchanged / WR 80% / Sharpe 0.83 / cum +59.78%**（filter 對 Part B 完全非綁定，2/2 Part B SLs 之 Rel_QQQ_20d 皆 < +15%）/ min(A,B)† **0.83 TIE baseline**（依 EWJ-003/SPY-009/DIA-012/IWM-013/CIBR-014 慣例，Part A zero-var 結構性最優、Part B 變異 Sharpe 為 binding constraint）；Att2 (lookback=20, max_relative_return=+0.10) FAILED min(A,B) **0.65** REJECT — Part A 5/100% zero-var cum +46.93%（過度過濾 4 winners），Part B 8/75%/Sharpe 0.65 cum +36.98%（**Part B 退化 -22% Sharpe**，過濾 2 winners 但 2 SLs 仍存活）；Att3 (lookback=10, max_relative_return=+0.10) FAILED min(A,B) **0.31** REJECT — Part A 8/62.5%/Sharpe 0.31 cum +16.93%（**短週期 Rel_QQQ noisy，原 20d 已過濾的 3 SLs 在 10d 維度未被 +10% 清除，cooldown chain shift 引入額外 SLs，max consec losses 0→2**），Part B 10 訊號完全 unchanged 0.83。**核心發現（lesson #19/#26 family v2 邊界精煉，repo 首次跨 Part 結構反向發現）**：(1) **TSM Part A 與 Part B SLs 在 Rel_QQQ_20d 維度結構性反向**：Part A SLs 高 Rel_QQQ（>+15%, rally exhaustion 結構，CEILING 方向有效）vs Part B SLs 低 Rel_QQQ（<+10%, earnings drift / sector-specific drop 但 QQQ 同步上漲 → TSM 相對沒有過度跑贏，CEILING 方向結構性無效）。**單一 CEILING threshold 無法雙 Part 同步改善**，Part B 為 binding constraint，CEILING 方向結構性無法突破 0.83；(2) **與 NVDA-021 結構對比**：NVDA Part A/B SLs 皆集中於高 Rel_QQQ（CEILING 方向結構性一致 → min 0.55→1.43, +160%）；TSM 因 multi-driver 結構（中國地緣政治 + 半導體景氣 + 客戶集中度 + 新興市場 ADR earnings cycle）使 Part B SLs 機制不同於 Part A，**CEILING 方向結構性失敗於 Part B**；(3) **新跨資產規則（lesson #19/#26 family v3 邊界）**：cross-asset divergence regime gate 適用邊界擴展為「Part A 與 Part B SLs 在 divergence 維度單向對齊」雙條件。NVDA-021 ✓（雙 Part 對齊，min +160%）；TLT-014 ✓（雙 Part 對齊 FLOOR，min +393%）；TSLA-017 ✓（雙 Part 對齊 FLOOR，min +81%）；INDA-012 / EWZ-009 ✓（雙 Part 對齊 CEILING）；TSM-013 ✗（雙 Part SLs 結構性反向，CEILING 僅解 Part A）。新假設：對於「Part A/B SLs divergence 反向」結構資產，需替代維度（如 BANDS 變體 / different anchor 如 EWT / 不同 framework）方能突破；(4) **Att1 為 partial-success 重要實質改善**：repo 首次將 cross-asset divergence regime gate（CEILING 方向）移植至半導體 ADR 個股 + RS Momentum Pullback 框架，Part A 結構性突破（zero-var all TPs）為實質改善但 Part B sample size + 結構不對齊使 min(A,B) TIE baseline；(5) **lesson #6 邊界第四次擴展候選**：cross-asset divergence regime gate 在「multi-driver 個股 + RS framework」上 Part A 有效但 Part B 結構性失敗，與既有「single-driver 個股 + MBPC/BB Squeeze」全部成功案例（NVDA-021/TSLA-017）形成失敗邊界。TSM-011 Att3 仍為 min(A,B) 全域最優（13 次實驗、39+ 次嘗試）。
  note_2026_05_08: TSM-012 added 2026-05-08 (Volume-Confirmed RS Momentum Pullback, **repo 第 3 次 volume filter 主訊號試驗、首次於 RS momentum 框架**, three iterations all FAILED vs TSM-011 Att3 min 0.83). Att1 (vol_ratio_min >= 1.30, H1 capitulation buy hypothesis) Part A 5 訊號 / WR 80% / Sharpe **1.56** cum +33.71% / 0 SLs / Part B 4 訊號 / WR 75% / Sharpe **0.65** cum +17.04% / 1 SL / min(A,B) **0.65** (-22% vs 0.83) — vol >= 1.30 過於嚴苛（12→5、10→4，-58%/-60% 訊號率），保留之 Part A 訊號品質極佳（4/5 TP）但 Part B 2024-07-08 SL 仍存活於高 vol 過濾下；Att2 (vol_ratio_max <= 1.20, H2 orderly continuation) Part A 9 / WR 66.7% / Sharpe **0.54** cum +33.94% / 2 SLs / Part B 7 / WR 71.4% / Sharpe **0.54** cum +26.84% / 2 SLs / min **0.54** (-35%) — 低 vol 過濾保留更多訊號但品質下降，2022-11-21、2022-12-07 兩個 baseline 缺乏的低品質訊號通過 vol <= 1.20 缺口進入；Att3 (vol_ratio_min >= 1.10, moderate floor) Part A 6 / WR 83.3% / Sharpe **1.76** cum **+44.41%** / 0 SLs / Part B 4（同 Att1）/ Sharpe 0.65 / min **0.65** / A/B 累計差 **62%** (>> 30% target) — 結構性 A/B 失衡，Part A 高 vol 訊號天然密集於 2020-2023 高波動期，Part B 2024-2025 較低波動期 vol 整體偏低，floor filter 系統性傾向 Part A。**核心發現**：(1) Volume filter 在 TSM RS momentum pullback 框架**雙向皆失敗**——H1 capitulation buy 過嚴（保留 Part A 高品質訊號但 Part B 仍存活 SL）、H2 orderly continuation 過寬（引入 Part A 弱訊號）；(2) **2024-07-08 Part B SL 結構性穿透**——此 SL vol 高（屬 capitulation 範疇）但 5d 跌幅深（subsequent 1 週繼續下跌），volume confirmation 無法區分「真假 capitulation」，與 lesson #20b 失敗家族（RSI/CCI/Stoch/MACD hook）平行；(3) **Volume filter A/B regime asymmetry 新發現**：絕對 vol_ratio threshold（如 >= 1.10）在「Part A 高波動 / Part B 低波動」結構下系統性 A/B 失衡，需 vol normalization（rolling z-score 而非 ratio）；(4) **跨資產 lesson #6 邊界第三次擴展**：volume-based filters supplementary not substitutive 規則從 MR 框架（URA-011 Volume spike、SIVR-017 MFI）擴展至 RS momentum 框架（TSM-012 三次失敗），三類框架皆驗證。**新規則候選**：volume filters as primary screening dimension 在 active price-momentum-driven 框架（MR 與 RS momentum 兩類）皆無效，建議僅作為 secondary confirmation 維度與其他主要 price-action filter（5d ceiling、2DD cap、ClosePos）combination 使用。TSM-011 Att3 仍為全域最優（12 次實驗、36+ 次嘗試）。
  note_2026_05_02: TSM-011 added 2026-05-02 (Signal-Day Direction Filter on RS Momentum Pullback, **repo 首次「return CEILING（rally exhaustion filter）」於任何資產 + repo 首次 lesson #19 family cross-strategy 鏡像擴展（MR floor → momentum ceiling）**, applied to TSM-008 RS framework). Three iterations: Att1 (1d ceiling <= +1.0%) FAILED — Part A 12/75.0%/Sharpe **0.78** cum +68.73% / Part B unchanged / min 0.78 — 1d 過濾觸發 cooldown chain shift 將 2020-07-24 expiry -1.72% 替換為 2020-07-31 expiry -2.22%（更差），淨效果負面；Att2 (5d ceiling <= +9.5%) Part A 11/90.9%/Sharpe **1.30** cum **+87.38%** / Part B 10/80%/Sharpe 0.83 不變 cum +59.78% / min(A,B) **0.83** (+5% vs 0.79) — 顯著 Part A 改善但 A/B 累計差 31.6% **略超 30% 目標**（cooldown chain shift 移除 2022-11-21 SL 與 2022-12-07 SL，僅留 2022-11-28 SL）；Att3 ★ (5d ceiling <= +10.5%) Part A 12 訊號 WR **83.3%** Sharpe **0.86** cum **+74.10%** / Part B 10/80%/Sharpe 0.83 不變 cum +59.78% / min(A,B) **0.83** (+5% vs TSM-008 baseline 0.79) / A/B 累計差 **19.3%** (< 30% ✓) / A/B 訊號比 1.2:1 (gap 16.7% < 50% ✓) — **acceptance criteria 全部達標**。關鍵改善：5d ceiling +10.5% 僅過濾 2020-07-24 訊號（5d +11.30%, expiry -1.72%），cooldown chain shift 引入 2020-07-31 expiry +0.89%（從負轉正）+ 2020-08-20 TP +8%；Part B 完全不受影響（最高 5d 為 2024-02-12 +9.82% < +10.5%）。**核心發現（lesson #19 family v10）**：(1) **Repo 首次「return CEILING（rally exhaustion filter）」於任何資產**——既往 lesson #19 family 全部為 FLOOR 方向（capitulation depth filter，DIA-012/SPY-009/EWJ-005/EWZ-007/CIBR-014/SIVR-018/URA-013/INDA-011/GLD-014），TSM-011 開啟鏡像 CEILING 方向；(2) **Repo 首次 cross-strategy lesson #19 移植**：MR 框架 → RS momentum 框架（lesson #21 family），與既往 lesson #19 全部於 MR 框架平行；(3) **MR 失敗模式（太淺 capitulation）vs momentum 失敗模式（太深 rally）為結構性鏡像**——TSM Part A 2020-07-24 expiry 與 2022-11-21 SL 均屬「5 日大漲後淺回檔但實為趨勢反轉前兆」（Att2 確認 9.79 SL 與 9.82 TP 邊界精準 < 0.05 percentage points 區分，Att3 採取保守 +10.5% 邊界僅清除最極端 +11.30 case）；(4) **5d > 1d ceiling 區分力**——signal-day 1d 過濾因 cooldown chain shift 反向（Att1）而 5d 過濾因 2020-07-24 受 prior 5d 大漲驅動（5d +11.30 vs 1d +9.69 同向 signal）使 5d 為較穩健 rally exhaustion proxy。**新跨資產假設（待驗證）**：rally exhaustion 5d ceiling 可能適用於其他 RS / MBPC 動量框架（NVDA-006 RS / TSM-007 RS / VOO-004 MBPC / SOXL-010 RS 等），閾值需依資產 5d return 分布調整（TSM 甜蜜點 +10.5%，其他資產需 trade-level 分析）。TSM-011 Att3 為新全域最優（11 次實驗、33+ 次嘗試）。
  note: TSM-010 added 2026-04-30 (Multi-Week Regime-Aware Momentum Breakout Pullback Continuation, **repo 第 2 次 lesson #22 + MBPC 試驗、首次半導體 cross-asset NVDA→TSM 移植**, cross-asset port from NVDA-013 Att3). Three iterations all FAILED vs TSM-008 min 0.79: Att1 (NVDA-013 Att3 直接移植：k=1.00 + ATR ≤ 1.40 + recency 10d + pullback [-3%,-8%]) Part A 19/47.4%/Sharpe **0.03** cum -0.06% / Part B 12/58.3%/Sharpe **0.23** cum +18.33% / min **0.03** — TSM Part A 8 SLs 散佈於多 regime（trade war / pre-COVID / 2021-02 / 2022-08/12 / 2023-03/07），SMA regime + ATR vol 雙 gate 對 TSM SLs 缺乏選擇性，因 SLs 多發生於 SMA20/SMA60 仍 > 1.00 的「短暫地緣政治震盪」期間；Att2 (VOO-004 Att3 方向：recency 5d + pullback [-2%,-5%] 收緊) Part A 13/46.2%/Sharpe **-0.10** cum -11.10% / Part B 5/60%/Sharpe **0.26** cum +8.62% / min **-0.10** — 收緊進場後 WR 幾乎不變（47.4%→46.2%）顯示為**非選擇性過濾**，與 VOO 上 tight→loose 反向（VOO 0.12→1.12，TSM 0.00→-0.38）；Att3 (恢復 NVDA-013 預設 + 2DD cap >= -2%，lesson #19 cap 方向) Part A 14/50%/Sharpe **0.08** cum +4.75% / Part B 12（不變）/ min **0.08** — 2DD cap 過濾 5 訊號，cooldown chain shift 將 2020-09-17 SL 釋放為 2020-09-21 TP（正向 chain shift），但仍 7 SLs 殘留（2DD 維度淺）。**核心跨資產發現**：(1) **lesson #21 失敗家族擴展至 TSM 半導體 cross-asset**：NVDA-013 ★（單一 AI secular driver）→ TSM-010 ✗（multi-driver: 中國地緣政治 + 半導體景氣週期 + 客戶集中度），半導體個股 lesson #22 + MBPC 跨資產移植**結構性失敗**；(2) **新規則候選**：lesson #22 + MBPC 適用於「single-secular-driver 高波動個股」，**不適用於多重結構性驅動的個股**（TSM 為首例 multi-driver 失敗）；(3) **進場敏感度方向取決於資產 regime 結構**（lesson #4 邊界擴展）：VOO single uptrend 中 tight 捕捉高品質訊號；TSM multi-regime 中 tight 反而捕捉「短暫 regime 突破假動量」訊號；(4) **lesson #19 family 邊界擴展（2DD cap on MBPC）**：MR 框架（DIA-012/CIBR-012/USO-023）2DD cap 顯著有效；MBPC 框架選擇力受限，因 MBPC 進場本質為「shallow pullback」signal day 2DD 集中淺帶。**TSM 第 10 次實驗、30+ 次嘗試**，TSM-008 RS framework 仍為全域最優，TSM-010 確認「TSM 最佳訊號為 TSM/SMH RS spread」（cross-sectional 機制天然消化半導體週期 effect）。
-->
## AI Agent 快速索引

**當前最佳：** ★ **TSM-011 Att3**（Signal-Day Direction Filter on RS Momentum Pullback：TSM-008 完整框架 + **5 日報酬 ceiling <= +10.5%** rally exhaustion filter，TP+8%/SL-7%/25天/cd 10）★ **2026-05-02 新全域最優（12 次實驗、36+ 次嘗試）**
- Part A: Sharpe **0.86**, 累計 +74.10%, 12 訊號 (2.4/年), WR **83.3%**, MDD -7.89%
- Part B: Sharpe 0.83, 累計 +59.78%, 10 訊號 (5.0/年), WR 80.0%（與 TSM-008 baseline 完全相同）
- min(A,B) **0.83**（+5% vs TSM-008 baseline 0.79）
- A/B 累計差 **19.3%**（< 30% ✓，vs baseline 14.1% 略增），A/B 訊號比 1.2:1（gap 16.7% < 50% ✓）
- 關鍵改善：5d ceiling +10.5% 僅過濾 2020-07-24 訊號（5d +11.30%，原為 expiry -1.72%），cooldown chain shift 引入 2020-07-31 expiry +0.89%（從負轉正）+ 2020-08-20 TP +8%；Part B 訊號完全不受影響
- **跨資產貢獻**：repo 首次「return CEILING（rally exhaustion filter）」方向於任何資產 + repo 首次 lesson #19 family cross-strategy 鏡像擴展（MR floor → momentum ceiling）

**前任最佳：** TSM-008（RS 出場優化：同 TSM-007 進場，TP+8%/SL-7%/25天）— Part A Sharpe 0.79/Part B 0.83，min(A,B) 0.79，A/B 訊號數 12/10，A/B gap 0.04（極佳平衡）

**最新實驗：** TSM-020（TSM-SOXX 20d Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback：**repo 首次「sector-internal anchor」變體於任何資產 — SOXX iShares Semiconductor ETF 為 TSM ~9% 權重 sector ETF**，直接回應 TSM-019 AI_CONTEXT 列出之未驗證方向 (a) SOXX 半導體指數 anchor）— **三次迭代全部 REJECT/TIE vs TSM-011 Att3 min 0.83**。
- **Att1 PARTIAL**（max_relative_return_soxx=+0.10 loose ceiling）：Part A **8/87.5% WR/Sharpe 1.23** cum +59.23% MDD -7.79%（vs baseline 12/83.3%/0.86，**+43% Sharpe / +4.2pp WR**）/ Part B **10/80%/Sharpe 0.83 cum +59.78% 完全 unchanged**（filter 對 Part B 完全非綁定）/ min(A,B) **0.83 TIE baseline**（Part B binding，2024-07-16 SL + 2024-11-04 SL 之 TSM-SOXX 20d_div 皆 < +10%）/ A/B 年化 cum 11.85%/yr vs 26.4%/yr → gap **55% > 30% target ❌** / A/B 年化訊號比 1.6:5.0 = gap **68% > 50% ❌**
- Att2（max_relative_return_soxx=+0.05 tight ceiling）：min(A,B) **0.06 REJECT**（-93% vs baseline）— Part A **0 訊號 結構性過濾**（TSM-SMH RS ≥ +5% 進場條件下 TSM-SOXX 20d_div 結構性 > +5%，因 SMH TSM ~12% 權重對 TSM 漲幅吸收較多使 TSM-SMH < TSM-SOXX）/ Part B 2/1W1L/Sharpe 0.06（嚴重退化）
- Att3（max_relative_return_soxx=+0.07 medium ceiling 甜蜜點探尋）：min(A,B) **0.83 TIE baseline 但雙 acceptance criteria 違反 → REJECT**。Part A 4/75.0%/Sharpe 1.06 cum +21.83%（Part A 訊號 12→4 過嚴流失 8 訊號）/ Part B 5/80%/Sharpe 0.83 cum +26.40%（Part B 訊號 10→5 -50%）/ A/B 年化 cum 4.37%/yr vs 13.2%/yr → gap **67% > 30% ❌** / A/B 年化訊號比 0.8:2.5 = gap **68% > 50% ❌**
- **核心失敗發現（lesson #20 v3 family v11 邊界擴展，repo 首次 sector-internal anchor 變體於任何資產）**：(1) **Repo 首次「sector-internal anchor」變體**——既有 cross-asset divergence anchor 類別五大類（broad-market / 主要客戶 / 同類資產對等 / sub-component / sector-ETF）皆已驗證；(2) **TSM-SOXX 維度與 entry RS condition 結構性耦合**——TSM-SMH RS ≥ +5% entry condition 結構性使 TSM-SOXX 20d_div 必然 > +5%（SMH TSM ~12% > SOXX ~9% 權重），sweet spot 區間 [+7%, +10%] 結構性窄帶，但於該區間 SLs 與 winners 在 TSM-SOXX 維度仍重疊；(3) **Part B 2024-07-16 / 2024-11-04 SLs 在 TSM-SOXX 維度落於 winners 分布中段**——repo 第 8 次確認 TSM Part B SLs 在「single dimension cross-asset divergence」結構性與 winners 重疊（跨 8 維度 QQQ/QQQ-BAND/AAPL/BB-Width/earnings/ATR-BAND/VIX-term-structure/SOXX 結構性無解）
- **TSM Part B 0.83 binding constraint 第 8 次結構性無解確認**（TSM-013/014/015/016/017/018/019/020 共八次嘗試）：剩餘未驗證方向 (a) Multi-customer ensemble (AAPL + MSFT + NVDA voting), (b) 完全替代 framework (BB Squeeze Breakout / MR / lesson #22 multi-week regime + RS Momentum 組合), (c) Volume-normalized z-score (rolling z-score 替代 absolute ratio threshold)

**前次實驗：** TSM-019（VIX Term-Structure (^VIX3M / ^VIX) Regime Gate on RS Momentum Pullback：**repo 首次 VIX term structure 維度（^VIX3M / ^VIX 比率）於任何資產 + lesson #24 family v9 候選 forward-looking IV term structure derivative 維度**，直接回應 TSM-018 AI_CONTEXT 列出之未驗證方向）— **三次迭代 Att2 PARTIAL（Part A breakthrough min 0.83 TIE baseline 但 A/B 累計差 56.5% 違反 30% target）**。
- Att1（VIX3M/VIX <= 1.15 CEILING lenient）：min(A,B) **0.42 REJECT**（-49% vs baseline）— Part A 6/66.7%/0.42 cum +17.44% / Part B 8/75.0%/0.65 cum +36.98%。CEILING 1.15 過度過濾 Part A winners（1.15-1.24 deep contango range 含 7 winners）+ cooldown chain shift 將 2024-07-16 SL 替換為 2024-07-11 SL（淨 SL 不變但時間偏移）
- **Att2 ★ PARTIAL**（VIX3M/VIX >= 1.115 FLOOR，過濾 Part A SLs ratio 1.106/1.110）：Part A 9/**88.9% WR/Sharpe 1.11** cum +60.65% MDD -8.42%（vs baseline 12/83.3%/0.86，**+29% Sharpe / +5.6pp WR**）/ Part B 5/80.0%/Sharpe **0.83** cum +26.40%（**與 baseline 0.83 完全相同**）/ min(A,B) **0.83 TIE baseline** / A/B 年化 cum 12.13%/yr vs 13.20%/yr → gap **8.1% < 30% ✓** / **A/B 累計差 56.5% > 30% target ❌**（Part A 5 年期累積 vs Part B 2 年期累積稀釋）/ A/B 訊號比 1.39:1（gap 28% < 50% ✓）。FLOOR 1.115 乾淨過濾 Part A 2 SLs（2022-11-21 / 2022-12-07）但 cooldown chain shift 引入 2022-11-28 新 SL（淨 SL 2→1）；Part B 2024-10-30 SL（1.020）過濾 ✓ 但 2024-07-16 SL（1.130 > 1.115）結構性逃逸
- Att3（VIX3M/VIX >= 1.10 FLOOR lenient ablation）：min(A,B) **0.42 REJECT**（-49% vs baseline）— Part A 11/72.7%/0.58 cum +44.35%（**max consec losses 3**，cooldown chain shift 引入 3 連 SLs）/ Part B 6/66.7%/0.42 cum +17.44%。FLOOR 1.10 對 Part A SLs 1.106/1.110 仍非綁定（兩 SL 仍存活）+ 切除若干 winners 觸發 cooldown chain shift 連鎖負面
- **核心失敗發現（lesson #24 family v9 邊界擴展，repo 首次 VIX term structure 於任何資產）**：(1) **Repo 首次 VIX term structure (^VIX3M / ^VIX) 於任何資產**——既有 lesson #24 family v1-v8 為 implied vol LEVEL（^VIX/^MOVE/^GVZ/^OVX/^VXN）或 DIRECTION（X 日變化），尚未驗證 term structure；(2) **Att2 partial-success**：Part A 突破 +29% Sharpe + 100% WR baseline level 改善但 A/B 累計差 56.5% 違反 30% target；(3) **TSM Part A vs Part B SLs 在 VIX3M/VIX 維度結構性反向**：Part A SLs（mid contango 1.106-1.110）vs Part B SLs（雙極端 1.020 + 1.130），單一 FLOOR 結構性無法雙 Part 同步改善——同 TSM-013/014/015/016/017/018 失敗模式平行；(4) **新跨資產規則（lesson #24 family v9 邊界）**：VIX term structure 適用邊界 = 「target SLs 在 term structure 維度為單向集中分布」+「Part A/B SLs 同向對齊」雙條件，TSM 違反兩條件
- **TSM Part B 0.83 binding constraint 第 7 次結構性無解確認**（TSM-013/014/015/016/017/018/019 共七次嘗試）：剩餘未驗證方向 (a) SOXX 半導體指數 anchor (TSM 為 SOXX 成分股自我參考但仍可試), (b) Multi-customer ensemble (AAPL + MSFT + NVDA voting), (c) 完全替代 framework (BB Squeeze Breakout / MR / lesson #22 multi-week regime + RS Momentum 組合), (d) Volume-normalized z-score (rolling z-score 替代 absolute ratio threshold)

**前次實驗：** TSM-018（ATR(5)/ATR(20) BAND Volatility-Acceleration Filter on RS Momentum Pullback：**repo 首次 ATR ratio BAND 變體於 RS Momentum 框架**，cross-strategy port from CIBR-014 / FXI-014 / URA-013，直接回應 TSM-017 AI_CONTEXT 列出之未驗證方向 (d) Volatility-Acceleration BAND filter）— **三次迭代全部 REJECT**。
- Att1（atr_ratio ∈ (1.15, 1.40] CIBR-014 直接移植）：min(A,B) **-0.03 REJECT**（-104% vs baseline）— Part A 6/50.0%/-0.03 cum -2.35%（3 SLs，cooldown chain shift 引入新 SLs）/ Part B 5/80.0%/0.83 cum +26.40%
- Att2（atr_ratio ∈ (1.00, 1.20] 放寬）：min(A,B) **0.27 REJECT**（-67% vs baseline）— Part A 4/75.0%/0.65 cum +17.04% / Part B 5/60.0%/0.27 cum +8.74%（chain shift 將 2024-07-16 / 2024-10-30 替換為 2024-07-08 / 2024-11-01 兩個新 SL）
- Att3（CEILING-only floor=0.50 非綁定 + ceiling=1.10）：min(A,B) **0.65 REJECT**（-22% vs baseline）— Part A 6/66.7%/0.65 cum +24.63% / Part B 6/83.3%/**0.98** cum +36.52%（Part B +18% vs baseline）；A/B 累計差 32.6% > 30% target ❌
- **核心失敗發現（lesson #15 family v3 cross-strategy 邊界擴展）**：(1) Repo 首次 ATR ratio BAND 於 RS Momentum 框架失敗——CIBR-014 / FXI-014 / URA-013 成功案例皆為 MR 框架（capitulation 訊號日 ATR 結構性高 1.15+），TSM RS Momentum Pullback 訊號日為「上升趨勢中淺回檔」ATR ratio 集中 1.0-1.15 窄帶，BAND 無區分力；(2) Part A/B SLs 在 ATR ratio 維度反向：Part A SLs (macro shock 拉回) ATR > 1.15、Part B SLs (earnings/macro pullback) ATR 1.10-1.20 中段，單一 BAND 結構性無法雙 Part 同步改善；(3) lesson #19 cooldown chain shift 在 RS Momentum + ATR BAND 組合下結構性放大反向選擇
- **TSM Part B 0.83 binding constraint 第 6 次結構性無解確認**（TSM-013/014/015/016/017/018 共六次嘗試）：未來方向 (a) SOXX 半導體指數 anchor, (b) Multi-customer ensemble (AAPL + MSFT + NVDA voting), (c) 完全替代 framework, (d) Volume-normalized z-score

**前次實驗：** TSM-017（Earnings-Date Exclusion Filter on RS Momentum Pullback：**repo 首次 earnings-date calendar exclusion filter 於任何資產**）— **三次迭代全部 REJECT**。
- Att1（asymmetric -10/+15 calendar days，25 日總窗口）：min(A,B) **0.42 REJECT**（-49% vs baseline）— Part A 7/71.4%/Sharpe 0.42 cum +19.28%（Part A -51%）/ Part B 6/83.3%/Sharpe **0.98** cum +36.52%（Part B +18%）。過寬窗口切除 5 個 Part A 訊號嚴重退化。
- Att2（bilateral ±5 calendar days，11 日窗口）：min(A,B) **0.71 REJECT**（-14% vs baseline）— Part A 10/80.0%/Sharpe 0.71 cum +49.26%（-17%）/ Part B 7/85.7%/Sharpe **1.11** cum +47.44%（**+34% vs baseline 0.83**）。Part B 突破，但 cooldown chain shift 將 2024-10-30 SL 替換為 2024-10-23 SL（同 SL）。
- Att3（bilateral ±2 calendar days，5 日窗口，最緊邊界）：min(A,B) **0.78 REJECT**（-6% vs baseline）— Part A 11/81.8%/Sharpe 0.78 cum +61.20%（-9%）/ Part B 7/85.7%/Sharpe 1.11 cum +47.44%（同 Att2，+34%）。Part A 僅損失 1 訊號（最佳保留），但 A/B 年化幾何 cum 差 53% > 30% target ❌。
- **核心失敗發現（lesson #20b 失敗家族擴展，repo 首次 earnings-date exclusion filter 於任何資產）**：(1) **時間維度 filter 與價格/成交量 filter 正交但仍受日期重疊限制**——TSM Part B 殘餘 SLs（2024-07-16 -2d / 2024-10-30 +13d）與 winners（2024-04-16 -2d / 2025-01-13 -3d / 2023-01-19 +7d）在 earnings-relative 日期維度結構性重疊，**不存在單一窗口配置同時過濾全部 SLs 並保留全部 winners**；(2) **Part A 退化機制**：Part A 包含多個 earnings-adjacent winners（2020-2023 半導體 cycle 拉抬 + earnings momentum continuation），任何時間窗口擴大皆切除 Part A winners 多於 SLs；(3) **Part B 改善 +34% 為「earnings-week SL cluster」確認**——TSM-016 Att3 假設成立但同時 winners 亦集中於 earnings 前 2-3 日，**winner/SL 在時間維度為共生分布**而非可分離 cluster。
- **新跨資產規則（lesson #6 邊界 + lesson #20b 擴展）**：earnings-date exclusion filter 適用邊界 = 「target 之 earnings-adjacent 訊號分布 winner-SL 比例顯著高於 non-earnings 訊號分布」。TSM 違反該條件——半導體個股 earnings momentum 與 earnings risk 兩股力量平衡。預期適用候選：fundamentals-driven 個股（financial / consumer / healthcare）；不適用於 cyclical individual stocks（半導體 / energy / commodity）earnings 為次要 catalyst。
- **TSM Part B 0.83 binding constraint 第 5 次結構性無解確認**（TSM-013/014/015/016/017 共五次嘗試）：未來方向 (a) SOXX 半導體指數 anchor（注意 TSM 為成分股自我參考）, (b) Multi-customer ensemble (AAPL + MSFT + NVDA voting), (c) 完全替代 framework, (d) Volatility-Acceleration BAND filter（CIBR-014/FXI-014 路徑）。

**前次實驗：** TSM-016（BB-Width Regime Gate on RS Momentum Pullback：**repo 首次 lesson #23 BB-Width Regime Gate cross-strategy 移植至 RS Momentum 框架**，cross-strategy port from TLT-007 / TQQQ-018 / SOXL-012）— **三次迭代 Att2 PARTIAL（雙 Part 100% WR std=0 但 A/B 累計 cum gap 41% > 30% target）**。
- Att1（bb_width_max=0.15 lenient）：min(A,B) **0.42 REJECT** — lesson #19 cooldown chain shift 中性化，原 2024-07-16 SL 替換為 2024-07-08 SL、2024-10-30 SL 替換為 2024-11-01 SL，淨 SL 數量未減少；Part A winners 大量流失 12→5
- **Att2 ★ PARTIAL**（bb_width_max=0.12 medium calm regime）：Part A 3/100% std=0 + Part B 2/100% std=0（雙 Part 結構性零方差，**repo 第 6 次達成**），全 6 SLs 清除（baseline 4 + chain-shift 2）；A/B 訊號比 0.6:1.0 = gap 33% < 50% ✓，但 A/B 年化幾何 cum 差 41% > 30% target ❌
- Att3（bb_width_max=0.14 sweet-spot test）：min(A,B) **-0.29 REJECT** — 0.14 閾值放回 cooldown chain 觸發的 earnings-week SLs（2024-10-16 T-1 to earnings、2025-01-16 同日 earnings、2024-11-01 chain shift），sweet spot 區間極窄（0.12 唯一甜蜜點）
- **跨資產貢獻（lesson #23 family v4 cross-strategy 邊界擴展）**：(1) **Repo 首次 lesson #23 BB-Width Regime Gate 移植至 RS Momentum 框架**——既有 TLT (rate MR) / TQQQ (leveraged broad index) / SOXL (leveraged sector) 皆為 MR 或 leveraged ETF，TSM ~2% vol 半導體 ADR 個股 + RS Momentum 框架為新類別；(2) TSM 適用閾值 0.12 落於既有 4 個成功案例的對數線性區間；(3) **新跨資產規則「regime gate 對小 sample 策略」共通邊界**：當基底框架已將 sample 壓低（baseline 12+10），regime gate 進一步切除使年化幾何 cum 差難維持 < 30%；解釋 TSM-013 Att1 (Part A zero-var) 與 TSM-016 Att2 (雙 Part zero-var) 同樣為「結構性最優但 cum gap 違反」的對應
- **TSM Part B 0.83 binding constraint 第 4 次無解確認**（TSM-013/014/015/016 共四次嘗試）：未來方向 (a) earnings-date exclusion filter（TSM-016 Att3 已證實 earnings-week 為高 SL 風險區間）, (b) SOXX 半導體指數 anchor, (c) 完全替代 framework

**前次實驗：** TSM-015（TSM-AAPL 20d Cross-Asset Divergence Regime-Gated RS Momentum Pullback：**repo 首次 AAPL 主要客戶 anchor 試驗於任何資產 + repo 首次同一 target 雙 anchor stack 結構（QQQ + AAPL）**，直接回應 TSM-013/014 「需嘗試不同 anchor」建議）— **三次迭代全部 REJECT/TIE**。
- Att1（AAPL FLOOR=-5% only）：min(A,B) **0.50 REJECT** — FLOOR 過濾 baseline 2024-07-08 SL 但 cooldown chain shift 引入 2024-07-16 + 2025-01-16 兩個新 SL，Part B 退化 -40%；Part A 損失 1 winner
- Att2（AAPL BAND [-7%, +5%]）：min(A,B)† **0.42 REJECT** — CEILING +5% 過嚴 over-filter Part A 12→3（Part A winners 結構性集中於 [+5%, +10%] Rel_AAPL_20d 範圍）
- Att3（AAPL FLOOR=-7% lenient + TSM-QQQ CEILING=+15% dual-anchor stack）：min(A,B)† **0.83 TIE baseline** — AAPL FLOOR -7% 對 baseline 19 訊號完全非綁定（Part B SLs Rel_AAPL_20d 皆 > -7%），結果與 TSM-013 Att1（QQQ CEILING only）完全相同
- **核心失敗發現（lesson #20 v3 family v11 邊界擴展，repo 首次拒絕 customer-anchor 假說）**：(1) AAPL anchor 對 TSM 不具 orthogonal selectivity——Part B SLs Rel_AAPL > -7%（FLOOR 非綁定）+ Part A winners Rel_AAPL [+5%, +10%]（CEILING over-filter）；(2) 拒絕 customer-anchor 假說——TSM 與 AAPL 在 macro shock 期間共動性高（Trump comments 同步影響），AAPL 並非 TSM 的 orthogonal 維度；(3) **新跨資產規則 (lesson #20 v3 v11)**：cross-asset divergence anchor 必須與 target SLs 在 N-day return 維度上具非零互信息——customer-anchor 與 target 共動 + 與 winners 維度重疊，雙向皆無區分力
- **TSM Part B 0.83 binding constraint 第 3 次結構性無解確認**：TSM-013 (QQQ CEILING) + TSM-014 (QQQ BAND) + TSM-015 (AAPL anchor) 三次嘗試確認 Rel_*_20d 對 Part B 結構性無區分力。未來需嘗試 (a) SOXX anchor (注意 TSM 為成分股), (b) AAPL/MSFT/NVDA 多客戶 ensemble voting, (c) 完全替代 framework, (d) earnings-date exclusion filter

**前次實驗：** TSM-014（TSM-QQQ 20d Cross-Asset Divergence **BAND** Regime-Gated RS Momentum Pullback：TSM-013 Att1 框架 + FLOOR + CEILING 雙向）— **三次迭代全部 REJECT/TIE**。
- Att1（FLOOR=-5%, CEILING=+15%）：min(A,B) **0.83 TIE** — FLOOR 對 baseline 19 訊號完全非綁定，trade-level 顯示 Part B SLs Rel_QQQ_20d 為 +4.10% (2024-07-16) / +7.63% (2024-10-30)，**不為極端低值**而落於 winners 分布中段
- Att2（FLOOR=+5%）：min(A,B) **0.74 REJECT** — cooldown chain shift 將原 2025-01-10 winner 替換為 2025-01-16 SL
- Att3（FLOOR=+8%）：min(A,B) **0.42 REJECT** — 過度過濾 Part A winners + cooldown chain shift 引入 Part B 額外 SLs
- **核心失敗發現**：TSM Part B SLs 結構性處於 Rel_QQQ_20d 中段非極端，**BAND 變體有效邊界需 SLs 集中於兩極端為先決條件**（lesson #15 ATR ratio BAND 成功之必要條件）。新跨資產規則 (lesson #15 + lesson #20 family v4)：cross-asset divergence regime gate 適用邊界三條件：(a) target narrow-scope vs broad benchmark, (b) Part A/B SLs 在 divergence 維度單向對齊, (c) 若 SLs 雙向反向，需 SLs 集中兩極端方可採 BAND 變體
- **TSM Part B 0.83 binding constraint 結構性無解（Rel_QQQ_20d 維度）**：未來需嘗試 (a) 不同 anchor (SOXX 半導體指數 / AAPL 客戶), (b) 不同 lookback (5d / 60d), (c) 完全替代 framework

**前次實驗：** TSM-013（TSM-QQQ 20d Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback：TSM-011 Att3 完整框架 + TSM 20d 報酬 - QQQ 20d 報酬 ≤ +X% cross-asset divergence regime gate）— **三次迭代 Att1 PARTIAL（Part A 結構性突破但 Part B unchanged → min TIE baseline 0.83）**。
- **Att1 ★ PARTIAL**（lookback=20, max_relative_return=+0.15）：Part A 9 訊號 / WR **100%** / Sharpe 0.00 zero-var (9/9 TPs) / cum **+99.90%**（vs baseline 12/83.3%/0.86/+74.10%, **cum +35% / WR +17pp / MDD -23%**）/ Part B 10 訊號完全 unchanged / WR 80% / Sharpe 0.83 / cum +59.78% / **min(A,B)† 0.83 TIE baseline**（Part A zero-var + Part B 變異 Sharpe 為 binding constraint，沿用 EWJ-003/SPY-009/DIA-012/IWM-013/CIBR-014 † 慣例）
- Att2（lookback=20, max_relative_return=+0.10）REJECT min 0.65 — Part B 退化 -22% Sharpe
- Att3（lookback=10, max_relative_return=+0.10）REJECT min 0.31 — Part A 退化 cooldown chain shift
- **核心發現（lesson #19/#26 family v2 邊界精煉，repo 首次跨 Part SLs 結構反向發現）**：TSM Part A SLs 高 Rel_QQQ_20d（rally exhaustion 結構，CEILING 有效）vs Part B SLs 低 Rel_QQQ_20d（earnings drift / sector-specific drop 但 QQQ 同步上漲，CEILING 結構性失敗）。**單一 CEILING threshold 結構性無法雙 Part 同步改善**，與 NVDA-021 雙 Part SLs 對齊高 Rel_QQQ → CEILING 成功（min +160%）形成失敗邊界對比。**新跨資產規則候選**：cross-asset divergence regime gate 適用邊界擴展為「Part A/B SLs 在 divergence 維度單向對齊」雙條件——multi-driver 個股（TSM 中國地緣政治 + 半導體景氣 + 客戶集中度 + ADR earnings cycle）使 Part A/B SLs 機制反向

**最近失敗實驗：** TSM-012（Volume-Confirmed RS Momentum Pullback：TSM-008 + signal-day Volume / SMA(Volume,20) 過濾）— 三次迭代全部失敗。Att1（vol_ratio_min >= 1.30，H1 capitulation buy）min(A,B) 0.65 / Att2（vol_ratio_max <= 1.20，H2 orderly continuation）min 0.54 / Att3（vol_ratio_min >= 1.10）min 0.65。確認 volume filter 在 RS momentum pullback 框架雙向皆失敗，volume 維度從 TSM 已驗證無效方向中剔除。

**前前任失敗實驗：** TSM-010（lesson #22 + MBPC 跨資產移植自 NVDA-013，三次迭代全部失敗，min(A,B) 最佳 0.08 vs TSM-008 0.79）— 確認半導體 NVDA→TSM lesson #22 + MBPC **結構性不可移植**（TSM multi-driver 結構不同於 NVDA single-secular AI driver）

**前最佳（RS 原版）：** TSM-007（TSM-SMH 20日報酬差≥5% + 5日回撤3-7% + Close>SMA(50)，TP+7%/SL-7%/20天）— Part A Sharpe 0.64/Part B 1.32，min(A,B) 0.64

**前最佳（動量回調）：** TSM-006（ROC(20)≥10% + 5日回撤3-7% + Close>SMA(50)，TP+7%/SL-7%/20天）— Part A Sharpe 0.46/Part B 0.57，min(A,B) 0.46，A/B 訊號比 1.2:1

**前最佳（均值回歸）：** TSM-002（回檔+WR+反轉K線：10日回檔≥10% + WR(10)≤-85 + ClosePos≥40%，TP+7%/SL-7%/20天）— Part A Sharpe 0.23/Part B 0.32，min(A,B) 0.23

**滾動窗口分析摘要：** TSM-002 ✗✓（精準度突變 ΔWR 33.3pp，績效漸變，訊號稀少統計可信度低）

**已證明無效���禁止重複嘗試）：**
- TSM-001 三重極端超賣（FCX-001 模板直接套用）：Part A Sharpe 0.06, Part B -0.09，訊號品質差
- TSM-002 Att1（Pullback -8%, WR -80, 7天冷卻）：Part A -5.02% 累計，過多訊號導致 2022 年熊市虧損群聚
- TSM-002 Att3（SL -6% 非對稱出場）：Part A Sharpe 降至 0.11，緊停損將贏家變輸家
- TSM-003 Att1（RSI(2)<12 + 2日跌≥3%，TP±5%）：Part A Sharpe -0.36，RSI(2) 單獨進場在 2022 熊市產生大量假訊號
- TSM-003 Att2（RSI(2)<10 + 2日跌≥4%，TP±6%）：Part A Sharpe -0.44，收緊 RSI 仍無法解決熊市假訊號
- TSM-003 Att3（回檔≥8% + RSI(2)<15，TP±6%）：Part A Sharpe -0.49，混合架構仍失敗，RSI(2) 對 TSM 無效
- TSM-004 Att1（SMH 回檔≥5% 確認 + TP+8%/SL-7%）：Part A Sharpe 0.06, Part B -0.29，SMH 過濾移除好訊號（確認跨資產教訓 #6）+ TP +8% 太貪
- TSM-004 Att2（TP+8%/SL-8%/25天，無 SMH）：Part A Sharpe -0.01, Part B -0.36，寬 SL 只增加虧損，2022 停損交易落幅超過 -8%
- TSM-005 Att1（BB 擠壓突破 TP+7%/SL-6%/25th pct/15d 冷卻）：Part A Sharpe 0.38, Part B **-0.42**，SL -6% 太緊（6/9 Part B 停損）
- TSM-005 Att2（BB 擠壓突破 TP+8%/SL-7%/25th pct/15d 冷卻）：Part A Sharpe 0.37, Part B **-0.16**，改善但仍負（5/9 Part B 停損）
- TSM-005 Att3（BB 擠壓突破 TP+8%/SL-8%/20th pct/20d 冷卻）：Part A Sharpe **0.14**, Part B **-0.18**，收緊擠壓條件反而移除 Part A 好訊號
- TSM-004 Att3（回檔上限 -20%）：與 TSM-002 完全相同，TSM 訊號均在 10-20% 回檔範圍內

**已掃描的參數空間：**
- 均值回歸進場：FCX-001 基準線（-18%/RSI<28/-8%）、Pullback+WR+ClosePos（-8%/-80/40%、-10%/-85/40%）、RSI(2) 各閾值（<10、<12、<15）搭配回檔/2日跌幅、SMH 回檔≥5% 確認、回檔上限 -20%
- 突破進場：BB(20,2) 擠壓 60日 20th~25th 百分位 5日內 + Close > Upper BB + Close > SMA(50)
- 動量回調進場：ROC(20) ≥ 10%/12%/15% + 5日回撤 3-7%/3-8%/3-10% + Close > SMA(50)
- 相對強度動量進場：TSM-SMH 20日報酬差 ≥ 3%/5%/8% + 5日回撤 3-7% + Close > SMA(50)
- RS 出場優化：TP+7%/SL-7%/25天、TP+8%/SL-7%/25天、TP+7.5%/SL-7%/25天（TSM-008，3次嘗試）
- 配對交易進場：TSM/NVDA 對數價格比值 z-score（60日回看）< -2.0/-2.5（TSM-009，3次嘗試）
- Multi-Week Regime-Aware MBPC（lesson #22 + ATR vol regime + 2DD cap）：Donchian 20d + 5d 淺回檔 + RSI [40,65] + SMA(20)≥k×SMA(60) + ATR(20)≤1.40×ATR(60) + 2DD cap，三次迭代全部失敗（TSM-010）
- Cross-Asset Divergence Regime Gate：TSM-QQQ 20d CEILING ≤ +15%/+10% / 10d ≤ +10%（TSM-013，Att1 PARTIAL 其餘 REJECT）
- Cross-Asset Divergence BAND：TSM-QQQ 20d FLOOR + CEILING [-5%/+5%/+8%, +15%]（TSM-014，三次迭代全部 REJECT/TIE）
- Customer Anchor Divergence：TSM-AAPL 20d FLOOR -5% / BAND [-7%, +5%] / dual-anchor (AAPL FLOOR -7% + QQQ CEILING +15%)（TSM-015，三次迭代全部 REJECT/TIE）
- Earnings-Date Exclusion Filter：bilateral ±2/±5 calendar days、asymmetric -10/+15 calendar days（TSM-017，三次迭代全部 REJECT，winner/SL 在 earnings-relative 日期維度共生分布）
- VIX Term-Structure Regime Gate：^VIX3M / ^VIX 比率 CEILING 1.15 / FLOOR 1.115 / FLOOR 1.10（TSM-019，Att1/Att3 REJECT，Att2 PARTIAL min 0.83 TIE baseline 但 A/B 累計差 56.5% 違反 30% target）
- 出場條件：TP+10%/SL-12%/25天、TP+7%/SL-7%/20天、TP+7%/SL-6%/20天、TP±5%/15天、TP±6%/15天、TP+8%/SL-7%/20天、TP+8%/SL-8%/25天、TP+8%/SL-8%/20天、TP+7%/SL-7%/25天、TP+8%/SL-7%/25天、TP+7.5%/SL-7%/25天
- 冷卻期：7天、10天、15天、20天

**尚未嘗試的方向（可探索，但預期邊際效益低）：**
- 地緣政治風險過濾（如台海緊張相關波動）
- SOXX 半導體指數 anchor（注意 TSM 為 SOXX 成分股，自我參考性需謹慎）
- Multi-customer ensemble (AAPL + MSFT + NVDA voting)
- Volume-normalized z-score（rolling z-score 替代 absolute ratio threshold）
- 完全替代 framework（BB Squeeze Breakout / MR / lesson #22 multi-week regime + RS Momentum 組合）
- ~~Volatility-Acceleration BAND filter（CIBR-014/FXI-014 路徑）~~ → TSM-018 三次嘗試全部 REJECT
- ~~成交量異常濾波（放量確認恐慌賣出）~~ → TSM-012 三次嘗試全部失敗
- ~~AAPL 主要客戶 anchor cross-asset divergence~~ → TSM-015 三次嘗試全部 REJECT/TIE
- ~~earnings-date exclusion filter~~ → TSM-017 三次嘗試全部 REJECT（earnings-adjacent winner/SL 共生分布）
- ~~VIX term structure (^VIX3M / ^VIX) regime gate~~ → TSM-019 三次嘗試 Att1/Att3 REJECT, Att2 PARTIAL（min TIE baseline 但 A/B cum gap 違反目標）

**已排除的方向：**
- **VIX Term-Structure Regime Gate (^VIX3M / ^VIX)**：TSM-019 三次迭代 Att1/Att3 REJECT、Att2 PARTIAL（**repo 首次 VIX term structure 維度於任何資產 + lesson #24 family v9 候選 forward-looking IV term structure derivative**）。Att1（CEILING <= 1.15）min 0.42 過度過濾 deep contango Part A winners；Att2（FLOOR >= 1.115）min **0.83 TIE baseline** Part A 突破 +29% Sharpe (Sharpe 1.11 / WR 88.9%) 但 Part B 完全不變 + A/B 累計差 56.5% 違反 30% target；Att3（FLOOR >= 1.10 lenient）min 0.42 對 Part A SLs 1.106/1.110 仍非綁定 + cooldown chain shift 引入 3 連 SLs。**核心失敗根因**：(1) TSM Part A SLs（mid contango 1.106-1.110）vs Part B SLs（雙極端 1.020 + 1.130）在 VIX3M/VIX 維度結構性反向，單一 FLOOR 結構性無法雙 Part 同步改善；(2) Part A 5 年期累積 vs Part B 2 年期累積稀釋使絕對累計差難維持 < 30%。**新跨資產規則 (lesson #24 family v9 邊界)**：VIX term structure 適用邊界 = 「target SLs 在 term structure 維度為單向集中分布」+「Part A/B SLs 同向對齊」雙條件，TSM 違反兩條件
- **Earnings-Date Exclusion Filter**：TSM-017 三次迭代全部 REJECT（**repo 首次 earnings-date calendar exclusion filter 於任何資產**）。Att1（asymmetric -10/+15）min 0.42、Att2（bilateral ±5）min 0.71、Att3（bilateral ±2 最緊）min 0.78。三次 Part B 皆突破至 0.98/1.11/1.11（**+18% / +34% / +34%**），但 Part A 退化至 0.42/0.71/0.78（-51%/-17%/-9%）使 min(A,B) 低於 baseline。**核心失敗根因**：時間維度 filter 與價格/成交量 filter 正交但仍受日期重疊限制——TSM Part B 殘餘 SLs（2024-07-16 -2d / 2024-10-30 +13d）與 winners（2024-04-16 -2d / 2025-01-13 -3d / 2023-01-19 +7d）在 earnings-relative 日期維度結構性重疊，**不存在單一窗口配置同時過濾全部 SLs 並保留全部 winners**；Part A 退化機制：包含多個 earnings-adjacent winners（2020-2023 半導體 cycle 拉抬 + earnings momentum continuation），任何窗口擴大皆切除 Part A winners 多於 SLs；Part B +34% 改善為「earnings-week SL cluster」確認（TSM-016 Att3 假設成立）但同時 winners 亦集中於 earnings 前 2-3 日，**winner/SL 在時間維度為共生分布**而非可分離 cluster。**新跨資產規則（lesson #6 邊界 + lesson #20b 擴展）**：earnings-date exclusion filter 適用邊界 = 「target 之 earnings-adjacent 訊號分布 winner-SL 比例顯著高於 non-earnings 訊號分布」——TSM 違反該條件（半導體個股 earnings momentum 與 earnings risk 平衡）；預期適用 fundamentals-driven 個股（financial / consumer / healthcare）；不適用 cyclical individual stocks（半導體 / energy / commodity）。
- **AAPL 主要客戶 anchor Cross-Asset Divergence**：TSM-015 三次迭代全部 REJECT/TIE。Att1（FLOOR=-5%）min 0.50 cooldown chain shift；Att2（BAND [-7%, +5%]）min† 0.42 over-filter Part A 12→3；Att3（dual-anchor stack QQQ CEILING+15% + AAPL FLOOR -7%）min† 0.83 TIE = TSM-013 Att1 (AAPL FLOOR 非綁定)。**結構性失敗根因**：(1) AAPL FLOOR 維度 Part B SLs 結構性 > -7%；(2) AAPL CEILING 維度與 Part A winners 結構性重疊 [+5%, +10%]；(3) TSM 與 AAPL 在 macro shock 期共動。**Repo 首次拒絕 customer-anchor 假說 + repo 首次「同一 target 雙 anchor stack」失敗**。新跨資產規則 (lesson #20 v3 v11)：cross-asset divergence anchor 必須與 target SLs 在 N-day return 維度上具非零互信息
- **Cross-Asset Divergence Regime Gate（CEILING 方向，TSM-QQQ 20d）**：TSM-013 三次迭代僅 Att1 PARTIAL（Part A zero-var all TPs / Part B unchanged）→ min(A,B) TIE baseline 0.83。Att2 收緊至 +10%、Att3 改為 10d lookback 皆 REJECT。**結構性失敗根因**：TSM Part A SLs 高 Rel_QQQ（CEILING 有效）vs Part B SLs 低 Rel_QQQ（CEILING 失效），與 NVDA-021 雙 Part SLs 對齊（CEILING 成功 min +160%）形成失敗邊界對比。multi-driver 個股結構（中國地緣政治 + 半導體景氣 + ADR earnings）使 Part A/B SLs 機制反向，單一 CEILING 無法雙 Part 同步改善
- **Volume Confirmation Filter（成交量確認）**：TSM-012 三次嘗試全部失敗於 RS momentum pullback 框架。Att1 (vol_ratio_min >= 1.30) 過嚴削減 60% 訊號但 Part B 2024-07-08 SL 仍存活；Att2 (vol_ratio_max <= 1.20) 引入低品質訊號（2022-11-21、2022-12-07 兩 SL）；Att3 (vol_ratio_min >= 1.10) 結構性 A/B 失衡（Part A 高波動期 vol 高密集，Part B 低波動期 vol 整體低）。確認跨資產規則：volume-based filters 作為 supplementary not substitutive 維度規則擴展至 RS momentum 框架（lesson #6 邊界第三次擴展，繼 URA-011 MR、SIVR-017 MFI MR 後）。Volume filter A/B regime asymmetry 為新發現——絕對 vol_ratio threshold 在多 regime 期間需 vol normalization（rolling z-score）以避免結構性偏差。
- **配對交易（TSM/NVDA z-score 均值回歸）**：TSM-009 三次嘗試全部失敗（最佳 min(A,B) 0.40 vs TSM-008 0.79）。TSM/NVDA 價格比值存在結構性漂移（NVDA AI 驅動成長），z-score 均值回歸假設不成立，與 SIVR/GLD、COPX/FCX 配對交易失敗模式一致
- **Multi-Week Regime-Aware MBPC（lesson #22 + MBPC，NVDA-013 cross-asset 移植）**：TSM-010 三次嘗試全部失敗（Att1 0.03 / Att2 -0.10 / Att3 0.08）vs TSM-008 0.79。NVDA→TSM **半導體 cross-asset 移植結構性失敗**：TSM 為 multi-driver（中國地緣政治 + 半導體景氣週期 + 客戶集中度）vs NVDA single-secular AI driver，lesson #22 SMA + ATR vol 雙 regime gate **缺乏選擇性**（TSM Part A SLs 多發生於 regime 仍正常的「短暫地緣政治震盪」期間）。確認 lesson #22 + MBPC 適用邊界為「single-secular-driver 高波動個股」
- RSI(2) 短期動能耗竭模式（SPY-004 風格）：TSM-003 三次嘗試全部失敗，Part A Sharpe 均為負值。確認跨資產教訓 #13：高波動個股 (>2%) RSI(2) 不適用
- 半導體指數（SMH）確認：TSM-004 Att1 驗證，SMH 過濾移除好訊號多於壞訊號。確認跨資產教訓 #6：已精確訊號上疊加確認指標無效
- 非對稱 TP/SL（TP+8%）在均值回歸上：TSM-004 Att1/Att2 驗證，TP +7% 是均值回歸甜蜜點。但 TSM-008 驗證 RS 動量進場下 TP+8% 可行（min(A,B) 0.79）
- 寬停損（SL -8%）：TSM-004 Att2 驗證，2022 熊市停損交易落幅遠超 -8%，寬停損只增加每筆虧損幅度
- 回檔上限（-20%）：TSM-004 Att3 驗證，TSM 所有訊號均在 10-20% 回檔範圍內，上限無作用
- **BB 擠壓突破策略**：TSM-005 三次嘗試全部失敗（Part B Sharpe -0.42/-0.16/-0.18）。與 NVDA-003/TSLA-005 不同，TSM 在 2024-2025 因 AI 炒作與地緣政治反覆產生大量假突破（9 個 Part B 訊號中 5-6 個停損），突破策略在 TSM 上不可行

**關鍵資產特性：**
- 全球最大半導體代工廠，NYSE ADR（代號 TSM）
- 高 Beta、週期性強，與半導體需求週期高度相關
- 日均波動約 2-3%（介於 GLD 與 TQQQ 之間）
- 流動性佳（大型 ADR），滑價假設 0.10%
- 極端恐慌時跌幅可達 30-50%（如 2022 半導體庫存調整、地緣政治風險）
- **突破策略不適用**：TSM 受地緣政治風險（台海）影響，2024-2025 突破後常因政策/地緣消息急速反轉，與純動量驅動的 NVDA/TSLA 不同
- **動量回調策略有效**：TSM-006 驗證順勢回調在 TSM 上表現優異，SMA(50) 過濾避開 2022 熊市假訊號，ROC(20)≥10% 確認中期動量，A/B 平衡 1.2:1
- **相對強度優於絕對動量**：TSM-007 使用 TSM-SMH 20日報酬差替代 ROC(20)，過濾純板塊 beta 上漲，min(A,B) Sharpe 從 0.46 提升至 0.64（+39%）。RS 5% 是甜蜜點（3% 過鬆引入低品質訊號，8% 過嚴只剩 8+3 訊號）
- **RS 出場優化有效**：TSM-008 驗證 RS 進場配合 TP+8%/SL-7%/25天出場，min(A,B) 從 0.64→0.79（+23%），A/B gap 從 0.68→0.04。延長持倉 20→25天改善到期交易，TP+8% 在 RS 動量進場下可行（vs 均值回歸 TP+8% 失敗）
- **配對交易不適用**：TSM-009 驗證 TSM/NVDA z-score 配對交易（3次嘗試，最佳 min(A,B) 0.40），TSM/NVDA 比值存在結構性漂移
- **lesson #22 + MBPC 不適用**：TSM-010 驗證 NVDA-013 cross-asset 移植在半導體個股 NVDA→TSM **結構性失敗**（三次嘗試最佳 0.08 vs TSM-008 0.79）。TSM multi-driver 結構（中國地緣政治 + 半導體景氣 + 客戶集中度）使 lesson #22 SMA regime + ATR vol regime 對 Part A SLs 缺乏選擇性。**已確認 TSM-011 Att3 為全域最優**（12 次實驗、36+ 次嘗試，含均值回歸、突破、動量回調、相對強度、配對交易、lesson #22 MBPC、5d return ceiling、Volume confirmation filter 八大策略類型）
- **Volume Confirmation Filter 不適用**：TSM-012 三次迭代全部失敗，volume 維度雙向（capitulation buy floor / orderly continuation ceiling）皆無法區分 SL/TP。Volume filter A/B regime asymmetry（Part A 高波動期 vol 偏高，Part B 低波動期 vol 偏低）為新發現的結構性失敗模式。
- **Cross-Asset Divergence Regime Gate（CEILING）不適用**：TSM-013 三次迭代僅 Att1 PARTIAL（Part A 結構性突破但 Part B unchanged → min TIE baseline）。**結構性失敗根因**：TSM Part A SLs 高 Rel_QQQ_20d（CEILING 方向有效）vs Part B SLs 低 Rel_QQQ_20d（CEILING 方向失敗）。multi-driver 個股結構（中國地緣政治 + 半導體景氣 + 客戶集中度 + ADR earnings cycle）使 Part A/B SLs 機制反向，與 NVDA-021 single-secular AI driver 雙 Part SLs 對齊（CEILING 成功 min 0.55→1.43, +160%）形成失敗邊界對比。新跨資產規則候選：cross-asset divergence regime gate 適用邊界擴展為「Part A/B SLs 在 divergence 維度單向對齊」雙條件。**TSM-011 Att3 仍為全域最優**（13 次實驗、39+ 次嘗試）。
- **AAPL 主要客戶 anchor 不適用**：TSM-015 三次迭代全部 REJECT/TIE（Att1 FLOOR=-5% min 0.50 cooldown chain shift / Att2 BAND [-7%, +5%] min† 0.42 over-filter Part A 12→3 / Att3 dual-anchor stack QQQ+AAPL min† 0.83 TIE = TSM-013 Att1）。**核心失敗根因**：(1) AAPL FLOOR 維度 Part B SLs Rel_AAPL > -7% 結構性非綁定；(2) AAPL CEILING 維度與 Part A winners 結構性重疊 [+5%, +10%]；(3) TSM 與 AAPL 在 macro shock 期共動（Trump comments 同步影響），不具 orthogonal selectivity。**Repo 首次拒絕 customer-anchor 假說 + repo 首次「同一 target 雙 anchor stack」失敗**。新跨資產規則 (lesson #20 v3 v11)：cross-asset divergence anchor 必須與 target SLs 在 N-day return 維度上具非零互信息，customer-anchor 與 target 共動 + 與 winners 維度重疊則雙向皆無區分力。**TSM Part B 0.83 binding constraint 第 3 次結構性無解確認**（TSM-013 QQQ CEILING + TSM-014 QQQ BAND + TSM-015 AAPL anchor 皆失敗）。
- **Earnings-Date Exclusion Filter 不適用**：TSM-017 三次迭代全部 REJECT（**repo 首次 earnings-date calendar exclusion filter 於任何資產**）。Att1 (-10/+15) min 0.42、Att2 (±5) min 0.71、Att3 (±2 最緊) min 0.78。三次 Part B Sharpe 皆達 0.98~1.11（**+18%~+34% vs baseline 0.83**），但 Part A 退化使 min < baseline。**核心失敗根因**：時間維度 filter 與價格/成交量 filter 正交但 TSM Part B 殘餘 SLs（2024-07-16 -2d / 2024-10-30 +13d）與 winners（2024-04-16 -2d / 2025-01-13 -3d / 2023-01-19 +7d）在 earnings-relative 日期維度結構性重疊；Part A earnings-adjacent winners 數量多於 SLs（Part A 2 SLs 皆遠離 earnings 區），任何窗口擴大反向選擇；winner/SL 在時間維度為共生分布而非可分離 cluster。**新跨資產規則 (lesson #6 邊界 + lesson #20b 擴展)**：earnings-date exclusion filter 適用條件 = 「earnings-adjacent winner-SL 比例顯著高於 non-earnings 區」，TSM 違反該條件。預期適用 fundamentals-driven 個股（financial/consumer/healthcare），不適用 cyclical individual stocks（半導體/energy/commodity）。**TSM Part B 0.83 binding constraint 第 5 次結構性無解確認**（TSM-013/014/015/016/017 共五次嘗試）。
- **VIX Term-Structure Regime Gate (^VIX3M / ^VIX) 不適用**：TSM-019 三次迭代 Att1/Att3 REJECT、Att2 PARTIAL（**repo 首次 VIX term structure 維度於任何資產 + lesson #24 family v9 候選**）。Att1（CEILING <= 1.15）min 0.42 / Att2（FLOOR >= 1.115）min **0.83 TIE baseline** Part A 突破 +29% Sharpe (1.11) 但 A/B 累計差 56.5% 違反 30% target / Att3（FLOOR >= 1.10 lenient）min 0.42。**核心失敗根因**：(1) TSM Part A SLs（mid contango 1.106-1.110）vs Part B SLs（雙極端 1.020 + 1.130）VIX3M/VIX 維度結構性反向；(2) FLOOR direction 結構性無法雙 Part 同步改善——同 TSM-013/014/015/016/017/018 失敗模式。**新跨資產規則 (lesson #24 family v9 邊界)**：VIX term structure 適用邊界 = 「target SLs 在 term structure 維度為單向集中分布」+「Part A/B SLs 同向對齊」雙條件。**TSM Part B 0.83 binding constraint 第 7 次結構性無解確認**（TSM-013/014/015/016/017/018/019 共七次嘗試）。**TSM-011 Att3 仍為全域最優**（19 次實驗、57+ 次嘗試，含均值回歸、突破、動量回調、相對強度、配對交易、lesson #22 MBPC、5d return ceiling、Volume filter、QQQ CEILING/BAND、AAPL dual-anchor、BB-Width regime gate、Earnings exclusion filter、ATR ratio BAND、**VIX term structure regime gate** 共十四大策略類型）。
<!-- AI_CONTEXT_END -->

# TSM 實驗總覽 (TSM Experiments Overview)

## 標的特性 (Asset Characteristics)

- **TSM (Taiwan Semiconductor Manufacturing)**：全球最大專業半導體代工廠
- 高 Beta、週期性���，與半導體需求週期高度相關
- 日均波動約 2-3%，介於 GLD 與 TQQQ 之間
- 極端恐慌時跌幅可達 30-50%（如 2022 半導體庫存調整、台���地緣政治風險）
- 大型 ADR 流動性佳，滑價假設 0.10%

## 實驗列表 (Experiment List)

| ID      | 資料夾                          | 策略摘要                        | 狀態     |
|---------|---------------------------------|---------------------------------|----------|
| TSM-001 | `tsm_001_extreme_oversold`      | 三重條件極端超賣均值回歸         | 基準線   |
| TSM-002 | `tsm_002_pullback_wr_reversal`  | 回檔 + WR + 反轉K線確認         | 前最佳 |
| TSM-003 | `tsm_003_rsi2_reversal`         | 回檔 + RSI(2) 極端超賣（3次嘗試均失敗） | 失敗 |
| TSM-004 | `tsm_004_smh_confirm`           | SMH 確認 / 非對稱出場 / 回檔上限（3次嘗試均失敗） | 失敗 |
| TSM-005 | `tsm_005_bb_squeeze_breakout`   | BB 擠壓突破（3次嘗試均失敗）      | 失敗 |
| TSM-006 | `tsm_006_momentum_pullback`    | 動量回調（ROC+短期回撤+SMA50）    | 前最佳 |
| TSM-007 | `tsm_007_relative_strength`    | 相對強度動量回調（TSM vs SMH+回撤+SMA50）| 前最佳 |
| TSM-008 | `tsm_008_rs_exit_optimization` | RS 出場優化（同 TSM-007 進場，TP+8%/SL-7%/25天）| 前最佳 |
| TSM-009 | `tsm_009_pairs_trading`        | 配對交易 TSM/NVDA z-score 均值回歸（3次嘗試均失敗） | 失敗 |
| TSM-010 | `tsm_010_regime_mbpc`           | Multi-Week Regime-Aware MBPC（NVDA-013 cross-asset 移植，3次嘗試均失敗） | 失敗 |
| TSM-011 | `tsm_011_signal_day_filter`     | Signal-Day Direction Filter on RS（5d ceiling +10.5% rally exhaustion filter，Att3 SUCCESS） | **最佳** |
| TSM-012 | `tsm_012_volume_confirmed_rs_pullback` | Volume-Confirmed RS Momentum Pullback（vol_ratio min/max 雙向過濾，3次嘗試均失敗） | 失敗 |
| TSM-013 | `tsm_013_qqq_divergence_rs`     | TSM-QQQ 20d Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback（**repo 第 6 次 cross-asset divergence regime gate 跨資產移植、首次半導體 ADR 個股 + RS Momentum Pullback 框架**，Att1 PARTIAL：Part A 9/100% zero-var all TPs / Part B unchanged → min TIE baseline 0.83，Att2/Att3 REJECT） | ⚠️ 部分成功 |
| TSM-014 | `tsm_014_qqq_divergence_band`   | TSM-QQQ 20d Cross-Asset Divergence **BAND** Regime-Gated RS Momentum Pullback（**repo 首次 cross-asset divergence BAND 變體於任何資產**，FLOOR + CEILING 雙向，3 次迭代全部 REJECT/TIE，min(A,B) 最佳 0.83 TIE / 失敗根因 Part B SLs Rel_QQQ 落於 winners 分布中段非極端） | ❌ 失敗 |
| TSM-015 | `tsm_015_aapl_divergence_rs`    | TSM-AAPL 20d Cross-Asset Divergence Regime-Gated RS Momentum Pullback（**repo 首次 AAPL 主要客戶 anchor 試驗於任何資產 + repo 首次同一 target 雙 anchor stack 結構（QQQ + AAPL）**，3 次迭代全部 REJECT/TIE，min(A,B) 最佳 0.83 TIE / 失敗根因 AAPL FLOOR -7% non-binding + AAPL CEILING +5% over-filter Part A winners） | ❌ 失敗 |
| TSM-016 | `tsm_016_bb_width_regime_gate`  | BB-Width Regime Gate on RS Momentum Pullback（**repo 首次 lesson #23 BB-Width Regime Gate cross-strategy 移植至 RS Momentum 框架**，3 次迭代 Att2 PARTIAL 雙 Part 100% WR std=0 但 A/B 年化 cum gap 41% > 30% target，TSM-011 Att3 仍為 min(A,B) 全域最優） | ⚠️ 部分成功 |
| TSM-017 | `tsm_017_earnings_exclusion`    | Earnings-Date Exclusion Filter on RS Momentum Pullback（**repo 首次 earnings-date calendar exclusion filter 於任何資產**，3 次迭代全部 REJECT，三次 Part B Sharpe 皆 +18%~+34% 但 Part A 退化使 min < baseline 0.83，winner/SL 在 earnings-relative 日期維度共生分布） | ❌ 失敗 |
| TSM-018 | `tsm_018_atr_band_rs`           | ATR(5)/ATR(20) BAND Volatility-Acceleration Filter on RS Momentum Pullback（**repo 首次 ATR ratio BAND 變體於 RS Momentum 框架**，cross-strategy port from CIBR-014 / FXI-014 / URA-013，3 次迭代全部 REJECT，min(A,B) 最佳 0.65 < baseline 0.83，失敗根因 ATR ratio 在 RS 訊號日結構性集中 1.0-1.15 窄帶 + Part A/B SLs 反向） | ❌ 失敗 |
| TSM-019 | `tsm_019_vix_term_structure_rs` | VIX Term-Structure (^VIX3M / ^VIX) Regime Gate on RS Momentum Pullback（**repo 首次 VIX term structure 維度於任何資產 + lesson #24 family v9 候選 forward-looking IV term structure derivative**，3 次迭代 Att1/Att3 REJECT、Att2 PARTIAL min 0.83 TIE baseline + Part A 突破 +29% Sharpe (1.11) + WR 88.9%，但 A/B 累計差 56.5% 違反 30% target；失敗根因 Part A SLs (mid contango 1.106-1.110) vs Part B SLs (雙極端 1.020 + 1.130) 結構性反向） | ⚠️ 部分成功 |

## 參數對照表 (Parameter Comparison)

| 參數 | TSM-001 | TSM-002 | TSM-003 (Att3) | TSM-004 (Att1) | TSM-005 (Att2) |
|------|---------|---------|----------------|----------------|----------------|
| 策略類型 | 均值回歸 | 均值回歸 | 均值回歸 | 均值回歸 | **突破** |
| 進場指標 | 60日回撤+RSI(10)+SMA50乖離 | 10日回檔+WR(10)+收盤位置 | 10日回檔+RSI(2)+收盤位置 | 10日回檔+WR(10)+收盤位置+SMH回檔 | BB(20,2)擠壓+突破上軌+SMA(50) |
| 回撤/回檔閾值 | ≤ -18% (60日高點) | ≤ -10% (10日高點) | ≤ -8% (10日高點) | ≤ -10% (10日高點) | BB Width<60日25th pct |
| 超賣指標 | RSI(10) < 28 | WR(10) ≤ -85 | RSI(2) < 15 | WR(10) ≤ -85 | Close > Upper BB |
| 第三條件 | SMA50乖離 ≤ -8% | ClosePos ≥ 40% | ClosePos ≥ 40% | ClosePos ≥ 40% + SMH回檔≥5% | Close > SMA(50) |
| TP / SL | +10% / -12% | +7% / -7% | +6% / -6% | +8% / -7% | +8% / -7% |
| 持倉天數 | 25 天 | 20 天 | 15 天 | 20 天 | 20 天 |
| 冷卻期 | 15 天 | 10 天 | 10 天 | 10 天 | 15 天 |
| 追蹤停損 | 無 | 無 | 無 | 無 | 無 |

> **TSM-006 參數**：策略類型=動量回調、進場=ROC(20)≥10% + 5日回撤3-7% + Close>SMA(50)、TP+7%/SL-7%/20天、冷卻10天、無追蹤停損
> **TSM-007 參數**：策略類型=相對強度動量回調、進場=TSM-SMH 20日報酬差≥5% + 5日回撤3-7% + Close>SMA(50)、TP+7%/SL-7%/20天、冷卻10天、無追蹤停損
> **TSM-008 參數**：策略類型=RS出場優化、進場=同TSM-007（TSM-SMH 20日報酬差≥5% + 5日回撤3-7% + Close>SMA(50)）、TP+8%/SL-7%/25天、冷卻10天、無追蹤停損
> **TSM-009 參數**：策略類型=配對交易、進場=TSM/NVDA 對數價格比值 60日z-score < -2.0、TP+7%/SL-7%/20天、冷卻10天、無追蹤停損
> **TSM-011 參數**：策略類型=RS Momentum Pullback + 5d return CEILING、進場=同TSM-008 + 訊號日5日報酬 <= +10.5%（rally exhaustion filter）、TP+8%/SL-7%/25天、冷卻10天、無追蹤停損
> **TSM-012 參數**：策略類型=RS Momentum Pullback + Volume confirmation、進場=同TSM-008 + 訊號日 Volume / SMA(Volume,20) 在 [vol_ratio_min, vol_ratio_max] 區間、TP+8%/SL-7%/25天、冷卻10天、無追蹤停損
> **TSM-013 參數**：策略類型=RS Momentum Pullback + Cross-Asset Divergence CEILING、進場=同TSM-011 Att3（TSM-008 entry + 5d ceiling +10.5%）+ TSM 20日報酬 - QQQ 20日報酬 ≤ +15%（Att1 ★ PARTIAL final）、TP+8%/SL-7%/25天、冷卻10天、無追蹤停損
> **TSM-014 參數**：策略類型=RS Momentum Pullback + Cross-Asset Divergence BAND、進場=同TSM-013 Att1 + TSM 20日報酬 - QQQ 20日報酬 ≥ min_floor（Att1 -5% TIE / Att2 +5% REJECT / Att3 +8% REJECT，repo 首次 BAND 變體失敗）、TP+8%/SL-7%/25天、冷卻10天、無追蹤停損
> **TSM-016 參數**：策略類型=RS Momentum Pullback + BB-Width Regime Gate、進場=同TSM-011 Att3 + BB(20,2) Width / Close ≤ bb_width_max（Att1 0.15 REJECT min 0.42 / **Att2 ★ 0.12 PARTIAL 雙 Part 100% WR std=0** / Att3 0.14 REJECT earnings-week SLs 復發）、TP+8%/SL-7%/25天、冷卻10天、無追蹤停損
> **TSM-017 參數**：策略類型=RS Momentum Pullback + Earnings-Date Exclusion、進場=同TSM-011 Att3 + 訊號日不在 TSM earnings ±[earnings_pre_days, earnings_post_days] 窗口內（calendar days）（Att1 -10/+15 REJECT min 0.42 / Att2 ±5 REJECT min 0.71 / Att3 ±2 REJECT min 0.78）、TP+8%/SL-7%/25天、冷卻10天、無追蹤停損
> **TSM-018 參數**：策略類型=RS Momentum Pullback + ATR(5)/ATR(20) BAND、進場=同TSM-011 Att3 + 訊號日 ATR(5)/ATR(20) ∈ (atr_ratio_floor, atr_ratio_ceiling]（Att1 (1.15, 1.40] CIBR-014 直接移植 REJECT min -0.03 / Att2 (1.00, 1.20] 放寬 REJECT min 0.27 / Att3 (0.50, 1.10] CEILING-only 過濾 in-crash REJECT min 0.65）、TP+8%/SL-7%/25天、冷卻10天、無追蹤停損
> **TSM-019 參數**：策略類型=RS Momentum Pullback + VIX Term-Structure Regime Gate、進場=同TSM-011 Att3 + 訊號日 ^VIX3M/^VIX 比率 ∈ [min_vix_term_ratio, max_vix_term_ratio]（Att1 CEILING <= 1.15 lenient REJECT min 0.42 / **Att2 ★ FLOOR >= 1.115 PARTIAL** Part A 1.11 (+29%) cum +60.65% WR 88.9% / Part B 0.83 cum +26.40% (與 baseline 完全相同) / min(A,B) 0.83 TIE baseline / **A/B 累計差 56.5% > 30% target ❌**（年化 cum gap 8.1% < 30% ✓ 但絕對累計差超標因 Part A 5 年期 vs Part B 2 年期稀釋）/ Att3 FLOOR >= 1.10 lenient ablation REJECT min 0.42 cooldown chain shift 引入 3 連 SLs）、TP+8%/SL-7%/25天、冷卻10天、無追蹤停損

---

## TSM-001: Extreme Oversold Mean Reversion

**目標**：以嚴格多重條件篩選 TSM 極端超賣點，追求高勝率、低頻訊號。採用 FCX-001 三重條件模板，依據跨資產教訓 #11（個股高 Beta 優先使用極端超賣多重條件過濾）。

### 進場條件（全部滿足）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 60 日高點回撤 | ≤ -18% | 確認深度回撤 |
| 2 | RSI(10) | < 28 | 極端超賣 |
| 3 | SMA50 乖離 | ≤ -8% | 偏離均線過大 |
| 冷卻 | 訊號間隔 | ≥ 15 交易日 | 避免重複訊號 |

### 出場參數

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 | +10% | 半導體反彈力道強，放大獲利空間 |
| 停損 | -12% | 寬停損讓極端超���有更多恢復時間 |
| 持倉天數 | 25 天 | 充分等待回彈 |

### 成交模���

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價） |
| 獲利出場 | `limit_order Day`（當日限價單） |
| 停損出場 | `stop_market GTC`（持倉期間停損市價） |
| 到期出場 | `next_open_market`（隔日開盤市價） |
| 滑價 | 0.10%（大型 ADR 流動性佳） |
| 悲觀認定 | 是（同日觸及 TP 和 SL 時假設 SL 先成交） |

### 回測結果（2026-03-29）

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026) |
|------|-------------------|-------------------|---------------|
| 訊號數 | 6 | 2 | 0 |
| 每年���均 | 1.2 | 1.0 | 0.0 |
| 勝率 | 66.7% | 50.0% | — |
| 平均報酬 | +0.51% | -1.04% | — |
| 累計報酬 | +0.88% | -3.30% | — |
| 平均持倉 | 16.7 天 | 12.0 天 | — |
| 最大回撤 | -14.85% | -12.96% | — |
| 盈虧比 | 1.15 | 0.83 | — |
| 夏普比率 | 0.06 | -0.09 | — |
| 最大連續虧損 | 1 | 1 | — |

**分析**：
- 訊號頻率偏低（Part A 1.2/年，Part B 1.0/年），A/B 比例 1.2:1 平衡良好
- Part A 累計僅 +0.88%，主要因 2022-02 首筆交易到期虧損 -8.45% 和 2022-09 停損 -12.09% 拖累
- Part B 2025-02 的停損 -12.09% 與 2025-04 的達標 +10.00% 抵銷後為負
- 基準線結果偏弱，TSM-002 已超越

---

## TSM-002: Pullback + Williams %R + Reversal Candle ⭐ 當前最佳

**目標**：改用 GLD-007 已驗證的 Pullback + WR + Close Position 三重確認架構，針對 TSM 較高波動度調整參數。

### 設計理念

- 模板來源：GLD-007（回檔+WR+反轉K線，跨資產最成功的均值回歸架構）
- 針對 TSM 日波動 ~2.5% 放大回檔閾值（-10% vs GLD 的 -3%）和 TP/SL（+7%/-7% vs GLD 的 +3.5%/-4%）
- 不使用追蹤停損（跨資產教訓 #2：日波動 > 1.5% 不適用）
- Close Position ≥ 40% 日內反轉確認（跨資產教訓 #6 例外：針對特定失敗模式的濾波器有效）

### 進場條件（全部滿足）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 10 日高點回檔 | ≥ 10% | 確認技術性回檔 |
| 2 | WR(10) | ≤ -85 | 超賣 |
| 3 | 收盤位置 | ≥ 40% | 日內反轉確認 |
| 冷卻 | ���號間隔 | ≥ 10 交易日 | 避免重複訊號 |

### 出場參數

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 | +7% | 適配半導體波動（TSM-001 的 +10% 過貪，3/6 未達標） |
| 停損 | -7% | 對稱 TP/SL |
| 持倉天數 | 20 天 | |

### 成交模型

| 項�� | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價） |
| 獲利出場 | `limit_order Day`（當日限價單） |
| 停損出場 | `stop_market GTC`（持倉期間停損市價） |
| 到期出場 | `next_open_market`（隔日開盤市價） |
| 滑價 | 0.10%（大型 ADR ���動性佳） |
| 悲觀認定 | 是（同日觸及 TP 和 SL 時假設 SL 先成交） |

### 回測結果（2026-03-29）

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026) |
|------|-------------------|-------------------|---------------|
| 訊號數 | 11 | 4 | 0 |
| 每年平均 | 2.2 | 2.0 | 0.0 |
| 勝率 | 63.6% | 75.0% | — |
| 平均報酬 | +1.53% | +1.85% | — |
| 累計報酬 | +15.36% | +6.88% | — |
| 平均持倉 | 9.4 天 | 9.8 天 | — |
| 最大回撤 | -11.51% | -8.77% | — |
| 盈虧比 | 1.59 | 2.04 | — |
| 夏普比率 | 0.23 | 0.32 | — |
| 索提諾比率 | 0.36 | 0.52 | — |
| 卡瑪比率 | 0.13 | 0.21 | — |
| 最大連續虧損 | 3 | 1 | — |

**分析**：
- 相較 TSM-001 全面提升：Part A Sharpe 0.06→0.23，Part B Sharpe -0.09→0.32
- A/B 比例 2.75:1（11:4），Part B 訊號略少但品質高（WR 75%、PF 2.04）
- Part B 優於 Part A（Sharpe 0.32 > 0.23），無過擬合跡象
- 平均持倉 ~9.5 天，快速回彈特性
- 主要風險：2022 年熊市仍有 3 連敗（2022-02~06），但後半年回彈補回

### 實驗過程（3 次嘗試）

| 嘗試 | 參數變更 | Part A 結果 | Part B 結果 | 結論 |
|------|----------|------------|------------|------|
| Att1 | Pullback -8%, WR -80, 冷卻 7天 | 23 訊號, -5.02%, Sharpe -0.00 | 8 訊號, +19.50%, Sharpe 0.41 | A/B 差距過大，Part A 2022 信號過多 |
| **Att2** | **Pullback -10%, WR -85, 冷卻 10天** | **11 訊號, +15.36%, Sharpe 0.23** | **4 訊號, +6.88%, Sharpe 0.32** | **最佳，A/B 平衡且均正** |
| Att3 | 同 Att2 但 SL -6%（非對稱） | 11 訊號, +5.68%, Sharpe 0.11 | 4 訊號, +8.03%, Sharpe 0.39 | 緊停損將 Part A 贏家變輸家 |

---

## TSM-003: Pullback + RSI(2) Extreme Oversold (3 次嘗試均失敗)

**目標**：使用 RSI(2) 短期動量耗竭模式（SPY-004/DIA-002 風格），搭配回檔深度過濾，測試是否能改善 TSM-002 的風險調整後報酬。

### 設計理念

- 模板來源：SPY-004（RSI(2) 極端超賣均值回歸），在 SPY/DIA 低波動指數上表現良好
- 假設：RSI(2) 短期動量耗竭比 WR(10) 寬視角更精確地抓住反彈時機
- 依 TSM 日波動 ~2.5%（SPY ~1.2%，倍率 ~2x）縮放參數

### 實驗過程（3 次嘗試）

| 嘗試 | 進場條件 | 出場參數 | Part A 結果 | Part B 結果 | 結論 |
|------|----------|----------|------------|------------|------|
| Att1 | RSI(2)<12 + 2日跌≥3% + ClosePos≥40%, 冷卻7天 | TP±5%, 15天 | 15訊號, -24.36%, Sharpe **-0.36** | 9訊號, +14.53%, Sharpe 0.34 | Part A 嚴重失敗，2019-2023 產生大量假訊號 |
| Att2 | RSI(2)<10 + 2日跌≥4% + ClosePos≥40%, 冷卻10天 | TP±6%, 15天 | 10訊號, -23.28%, Sharpe **-0.44** | 3訊號, +5.52%, Sharpe 0.35 | 收緊仍無效，Part A 4連敗 |
| Att3 | 回檔≥8% + RSI(2)<15 + ClosePos≥40%, 冷卻10天 | TP±6%, 15天 | 14訊號, -29.83%, Sharpe **-0.49** | 7訊號, +2.97%, Sharpe 0.10 | 混合架構也失敗，回檔+RSI(2) 組合不如回檔+WR(10) |

### 成交模型

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價） |
| 獲利出場 | `limit_order Day`（當日限價單） |
| 停損出場 | `stop_market GTC`（持倉期間停損市價） |
| 到期出場 | `next_open_market`（隔日開盤市價） |
| 滑價 | 0.10%（大型 ADR 流動性佳） |
| 悲觀認定 | 是（同日觸及 TP 和 SL 時假設 SL 先成交） |

### 結論

**RSI(2) 對 TSM 無效**，三次嘗試 Part A Sharpe 均為負值（-0.36、-0.44、-0.49），遠遜於 TSM-002 的 +0.23。

**根本原因**：TSM 日波動 ~2.5% 屬高波動個股，RSI(2) 過於敏感，在 2022 年半導體熊市中持續產生假訊號。WR(10) 的 10 日回看視角更穩定，能避免短期雜訊觸發的進場。此結論與跨資產教訓 #13（高波動資產 >2% RSI(2) 不適用）及 SIVR-004 的失敗完全一致。

---

## TSM-004: SMH Confirmation / Asymmetric Exit / Capped Pullback (3 次嘗試均失敗)

**目標**：探索三個尚未嘗試的改進方向：(1) SMH 半導體指數確認減少個股假訊號、(2) 非對稱 TP/SL 利用高波動反彈、(3) 回檔上限過濾極端崩盤。

### 實驗過程（3 次嘗試）

| 嘗試 | 參數變更 | Part A 結果 | Part B 結果 | 結論 |
|------|----------|------------|------------|------|
| Att1 | TSM-002 + SMH回檔≥5%確認, TP+8%/SL-7% | 8訊號, +1.38%, Sharpe **0.06** | 3訊號, -6.77%, Sharpe **-0.29** | SMH 過濾移除好訊號 + TP +8% 太貪 |
| Att2 | TSM-002進場, TP+8%/SL-8%/25天 | 8訊號, -2.92%, Sharpe **-0.01** | 3訊號, -8.77%, Sharpe **-0.36** | 寬SL只增加虧損，2022停損交易落幅超-8% |
| Att3 | TSM-002 + 回檔上限-20% | 11訊號, +15.36%, Sharpe **0.23** | 4訊號, +6.88%, Sharpe **0.32** | 與 TSM-002 完全相同（無訊號超過-20%回檔） |

### 成交模型

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價） |
| 獲利出場 | `limit_order Day`（當日限價單） |
| 停損出場 | `stop_market GTC`（持倉期間停損市價） |
| 到期出場 | `next_open_market`（隔日開盤市價） |
| 滑價 | 0.10%（大型 ADR 流動性佳） |
| 悲觀認定 | 是（同日觸及 TP 和 SL 時假設 SL 先成交） |

### 結論

**三個方向均無法改善 TSM-002**：

1. **SMH 確認無效**：半導體板塊下跌時 TSM 已經在下跌（SMH 回檔只是 TSM 回檔的弱化版本），過濾器移除 3 個好訊號但不移除壞訊號。確認跨資產教訓 #6。
2. **TP +8% 太貪**：TSM 均值回歸幅度甜蜜點在 +7%，+8% 導致原本達標的交易變成到期或停損。類似 USO 的 TP +3.0% 硬上限。
3. **回檔上限 -20% 無效**：TSM 的 10 日回檔訊號全部在 -10% 到 -20% 之間，上限沒有過濾任何訊號。不同於 USO（原油負價格事件產生 >12% 極端回檔），TSM 的極端崩盤表現為持續下跌而非單日暴跌。

**TSM-002 已確認為全域最優**（經 TSM-001~004 共 12 次嘗試驗證）。

---

## TSM-005: BB Squeeze Breakout (3 次嘗試均失敗)

**目標**：測試突破策略是否能超越均值回歸。NVDA-003 和 TSLA-005 已驗證突破策略在動量驅動個股上優於均值回歸，TSM 同為高波動半導體股，理論上應適用。

### 設計理念

- 模板來源：NVDA-003（BB 擠壓突破，Sharpe 0.40/0.47）
- 波動收縮後的突破捕捉動量啟動
- SMA(50) 趨勢確認避免熊市假突破
- 針對 TSM 日波動 ~2.1%（低於 NVDA 3.26%）微調出場參數

### 實驗過程（3 次嘗試）

| 嘗試 | 參數變更 | Part A 結果 | Part B 結果 | 結論 |
|------|----------|------------|------------|------|
| Att1 | BB(20,2) 25th pct, TP+7%/SL-6%/15d冷卻 | 23訊號, +60.86%, Sharpe **0.38** | 9訊號, -20.28%, Sharpe **-0.42** | Part A 優異但 Part B 慘敗，SL -6% 太緊 |
| Att2 | 同Att1但 TP+8%/SL-7% | 23訊號, +68.44%, Sharpe **0.37** | 9訊號, -11.46%, Sharpe **-0.16** | Part B 改善（1筆翻正）但仍負 |
| Att3 | BB 20th pct + SL-8% + 20d冷卻 | 19訊號, +14.77%, Sharpe **0.14** | 8訊號, -12.23%, Sharpe **-0.18** | 收緊擠壓移除 Part A 好訊號，SL -8% 增加虧損 |

### 成交模型

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價） |
| 獲利出場 | `limit_order Day`（當日限價單） |
| 停損出場 | `stop_market GTC`（持倉期間停損市價） |
| 到期出場 | `next_open_market`（隔日開盤市價） |
| 滑價 | 0.10%（大型 ADR 流動性佳） |
| 悲觀認定 | 是（同日觸及 TP 和 SL 時假設 SL 先成交） |

### Att2 回測結果（最佳嘗試，2026-04-02）

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026) |
|------|-------------------|-------------------|---------------|
| 訊號數 | 23 | 9 | 1 |
| 每年平均 | 4.6 | 4.5 | 4.1 |
| 勝率 | 60.9% | 44.4% | 100.0% |
| 平均報酬 | +2.52% | -1.10% | +8.00% |
| 累計報酬 | +68.44% | -11.46% | +8.00% |
| 平均持倉 | 10.1 天 | 9.9 天 | 2.0 天 |
| 最大回撤 | -9.84% | -11.23% | 2.09% |
| 盈虧比 | 2.16 | 0.72 | ∞ |
| 夏普比率 | 0.37 | -0.16 | 0.00 |
| 最大連續虧損 | 4 | 2 | 0 |

### 結論

**BB 擠壓突破策略在 TSM 上完全失敗**，三次嘗試 Part B Sharpe 均為負值（-0.42、-0.16、-0.18）。

**根本原因**：TSM 與 NVDA/TSLA 的關鍵差異在於地緣政治風險。TSM 作為台灣公司，2024-2025 年受台海局勢、美中科技戰等因素影響，突破後經常因政治/地緣消息急速反轉（9 個 Part B 訊號中 5 個停損）。NVDA/TSLA 則是純動量驅動，突破後趨勢延續性更強。此外，TSM 作為 ADR 還受匯率風險影響，進一步增加突破失敗率。

**TSM-002 仍為全域最優**（經 TSM-001~005 共 15 次嘗試驗證，含均值回歸和突破兩大策略類型）。

---

## 演進路線圖

```
TSM-001 (極端超賣基準線) — Sharpe A:0.06 B:-0.09
├── TSM-002 (回檔+WR+反轉K線) — Sharpe A:0.23 B:0.32 ⭐ 當前最佳（全域最優）
│   ├── TSM-003 (RSI(2) 嘗試) — Sharpe A:-0.49 B:0.10 ✗ 失敗
│   └── TSM-004 (SMH確認/非對稱出場/回檔上限) — Sharpe A:0.06~0.23 B:-0.36~0.32 ✗ 失敗
└── TSM-005 (BB擠壓突破) — Sharpe A:0.37 B:-0.16 ✗ 失敗（突破策略不適用TSM）
```

---

## TSM-002 滾動窗口績效分析

> **分析日期：** 2026-03-30
> **窗口：** 2 年，步進 6 個月（共 12 個窗口，其中 10 個有效用於評估）

### 滾動窗口績效表

| 窗口 | 訊號 | 勝率 | 平均報酬 | 累計報酬 | MDD | ΔWR |
|------|------|------|----------|----------|-----|-----|
| 2019-01~2020-12 | 2 | 50.0% | -1.96% | -4.15% | -9.46% | — |
| 2019-07~2021-06 | 1 | 0.0% | -7.09% | -7.09% | -9.46% | -50.0pp |
| 2020-01~2021-12 | 1 | 0.0% | -7.09% | -7.09% | -9.46% | +0.0pp |
| 2020-07~2022-06 | 4 | 25.0% | -3.08% | -12.37% | -10.04% | +25.0pp |
| 2021-01~2022-12 | 7 | 57.1% | +0.96% | +5.13% | -11.51% | +32.1pp |
| 2021-07~2023-06 | 9 | 66.7% | +2.30% | +20.36% | -11.51% | +9.5pp |
| 2022-01~2023-12 | 9 | 66.7% | +2.30% | +20.36% | -11.51% | +0.0pp |
| 2022-07~2024-06 | 7 | 100.0% | +6.07% | +50.79% | -6.87% | +33.3pp |
| 2023-01~2024-12 | 5 | 100.0% | +5.70% | +31.71% | -5.20% | +0.0pp |
| 2023-07~2025-06 | 4 | 75.0% | +1.85% | +6.88% | -8.77% | -25.0pp |
| 2024-01~2025-12 | 4 | 75.0% | +1.85% | +6.88% | -8.77% | +0.0pp |
| 2024-07~2026-03 | 2 | 50.0% | -0.04% | -0.59% | -8.77% | -25.0pp |

### 預測精準度表

| 窗口 | WR | 平均贏利 | 平均虧損 | 盈虧比 | 差點成功 |
|------|------|----------|----------|--------|----------|
| 2019-01~2020-12 | 50.0% | +3.16% | -7.09% | 0.45 | 1/1 |
| 2019-07~2021-06 | 0.0% | N/A | -7.09% | 0.00 | — |
| 2020-01~2021-12 | 0.0% | N/A | -7.09% | 0.00 | — |
| 2020-07~2022-06 | 25.0% | +7.00% | -6.44% | 0.36 | 0/1 |
| 2021-01~2022-12 | 57.1% | +7.00% | -7.09% | 1.32 | — |
| 2021-07~2023-06 | 66.7% | +7.00% | -7.09% | 1.97 | — |
| 2022-01~2023-12 | 66.7% | +7.00% | -7.09% | 1.97 | — |
| 2022-07~2024-06 | 100.0% | +6.07% | N/A | ∞ | 1/1 |
| 2023-01~2024-12 | 100.0% | +5.70% | N/A | ∞ | 1/1 |
| 2023-07~2025-06 | 75.0% | +4.83% | -7.09% | 2.04 | 1/1 |
| 2024-01~2025-12 | 75.0% | +4.83% | -7.09% | 2.04 | 1/1 |
| 2024-07~2026-03 | 50.0% | +7.00% | -7.09% | 0.99 | — |

### 漸變性評估

- **勝率範圍**：25.0% ~ 100.0%（ΔWR 標準差 21.4pp，最大跳動 33.3pp）
- **盈虧比範圍**：0.36 ~ 2.04（ΔPF 標準差 0.59）
- **累計報酬範圍**：-12.37% ~ +50.79%（ΔCum 標準差 16.89%）
- **平均贏利範圍**：+3.16% ~ +7.00%（Δ標準差 1.47%）
- **平均虧損範圍**：-6.44% ~ -7.09%（虧損幅度相對穩定）

**判定：**
- ✗ 預測精準度突變（勝率最大跳動 33.3pp > 20pp 閾值，發生在窗口 5→6）
- ✓ 下游績效漸變（累計報酬最大跳動 30.43% ≤ 3σ = 50.67%）

**診斷：** 精準度波動但績效穩定 → 勝/虧報酬互補抵消了精準度變化

### 分析解讀

1. **早期窗口訊號極少**：窗口 1-3 僅 1-2 筆訊號，勝率 0-50% 統計無意義
2. **2022-2024 黃金期**：窗口 6-9 勝率 67-100%，受益於半導體復甦與 AI 需求
3. **近期回落**：最新窗口勝率回降至 50%，僅 2 筆訊號，可能反映 2025 年地緣政治風險
4. **勝率波動極大**：從 0% 到 100%，但主要因訊號稀少導致統計不穩定
5. **差點成功比例**：多個窗口有 1/1 差點成功，暗示 TP 7% 可能在部分市場環境偏高

---

## TSM-006: Momentum Pullback

**目標**：以動量回調策略取代均值回歸，在上升趨勢中買入短期回調。參考 NVDA-005 架構，針對 TSM 特性調整。與 TSM-001~004 的均值回歸和 TSM-005 的突破策略屬於不同策略類型。

**策略假說**：TSM 受惠於 AI 半導體長期趨勢，在上升趨勢中的短暫回調（3-7%）提供良好的順勢進場機會。SMA(50) 過濾能有效避開 2022 熊市假訊號（均值回歸策略的主要痛點）。

### 進場條件（全部滿足）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 20 日 ROC | ≥ 10% | 中期動量確認 |
| 2 | 5 日高點回撤 | 3-7% | 短暫整理（非深度回調） |
| 3 | Close > SMA(50) | — | 上升趨勢確認 |
| 冷卻 | 訊號間隔 | ≥ 10 交易日 | 避免重複訊號 |

### 出場參數

| 參數 | 值 |
|------|----|
| 獲利目標 (TP) | +7% |
| 停損 (SL) | -7% |
| 最長持倉 | 20 天 |
| 追蹤停損 | 無（日波動 > 1.5%，見 cross_asset_lessons #2） |

### 成交模型

- 進場：隔日開盤市價（Next Open Market）
- 止盈：限價賣單 Day（Limit Order Day）
- 停損：停損市價 GTC（Stop Market GTC）
- 到期：隔日開盤市價（Next Open Market）
- 滑價：0.10%
- 悲觀認定：是

### 三次嘗試結果

| 嘗試 | ROC 門檻 | 回撤範圍 | Part A Sharpe | Part B Sharpe | min(A,B) | A/B 訊號比 | 結論 |
|------|----------|----------|---------------|---------------|----------|------------|------|
| Att1 | ≥12% | 3-8% | 0.46 | 0.43 | 0.43 | 1.7:1 | 良好但 Part B 較弱 |
| Att2 | ≥15% | 3-10% | 0.27 | 0.20 | 0.20 | 2.2:1 | 過嚴 ROC 過濾好訊號 |
| **Att3** | **≥10%** | **3-7%** | **0.46** | **0.57** | **0.46** | **1.2:1** | **最佳：A/B 極佳平衡** |

### 最終結果（Attempt 3）

**Part A (In-Sample: 2019-01-01 ~ 2023-12-31)**
- 訊號數：18（每年 3.6）
- 勝率：66.7%（12/18）
- 累計報酬：+52.88%
- MDD：-8.78%
- Sharpe：0.46，Sortino：0.84，PF：2.65

**Part B (Out-of-Sample: 2024-01-01 ~ 2025-12-31)**
- 訊號數：15（每年 7.5）
- 勝率：73.3%（11/15）
- 累計報酬：+61.15%
- MDD：-9.44%
- Sharpe：0.57，Sortino：1.01，PF：2.98

### vs TSM-002 對比

| 指標 | TSM-002 | TSM-006 | 改善 |
|------|---------|---------|------|
| Part A Sharpe | 0.23 | 0.46 | +100% |
| Part B Sharpe | 0.32 | 0.57 | +78% |
| min(A,B) Sharpe | 0.23 | 0.46 | +100% |
| A/B 訊號比 | 2.75:1 | 1.2:1 | 大幅改善 |
| Part A 訊號數 | 11 | 18 | +64% |
| Part B 訊號數 | 4 | 15 | +275% |
| Part A 累計 | +15.36% | +52.88% | +244% |
| Part B 累計 | +6.88% | +61.15% | +789% |

### 關鍵發現

1. **動量回調 > 均值回歸**：TSM-006 在所有風險調整指標上大幅超越 TSM-002，動量回調策略在 TSM 上明顯優於均值回歸
2. **SMA(50) 過濾效果**：有效避開 2022 熊市，僅 3/18 Part A 訊號觸發停損（vs TSM-002 的 4/11）
3. **ROC(20) 10% 是甜蜜點**：12% 和 15% 都過嚴，過濾掉品質良好的中等動量訊號
4. **回撤 3-7% 緊密範圍**：3-8% 和 3-10% 引入過多深度回調停損訊號
5. **A/B 平衡極佳**：1.2:1 在跨資產教訓 #8 的「優秀」區間（1.0-1.3:1）

---

## TSM-007: Relative Strength Momentum Pullback

**目標**：以 TSM 相對 SMH（半導體 ETF）的超額表現取代絕對 ROC，過濾純板塊 beta 上漲，聚焦 TSM 特有 alpha。

### 進場條件（全部滿足）

1. TSM 20日報酬 - SMH 20日報酬 >= 5%（TSM 跑贏板塊）
2. 5日高點回撤 3-7%（短暫整理，非深度回調）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 冷卻期 10 個交易日

### 出場條件

| 條件 | 值 |
|------|-----|
| 獲利目標 | +7% |
| 停損 | -7% |
| 最長持倉 | 20 天 |
| 追蹤停損 | 無 |
| 成交模型 | 隔日開盤市價進場，悲觀認定 |

### 三次嘗試結果

| 嘗試 | RS 門檻 | Part A Sharpe | Part B Sharpe | min(A,B) | A/B 訊號 | 結果 |
|------|---------|---------------|---------------|----------|----------|------|
| Att1 | >= 5% | **0.64** | **1.32** | **0.64** | 12/10 | **最佳** |
| Att2 | >= 8% | -0.01 | 0.35 | -0.01 | 8/3 | 過嚴，移除好訊號 |
| Att3 | >= 3% | 0.56 | 0.44 | 0.44 | 19/13 | 過鬆，引入低品質訊號 |

### Attempt 1 績效摘要（最佳版本，RS >= 5%）

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 12 | 10 |
| 每年平均 | 2.4 | 5.0 |
| 勝率 | 75.0% | 90.0% |
| 累計報酬 | +48.01% | +70.81% |
| Sharpe | 0.64 | 1.32 |
| Sortino | 1.17 | 2.49 |
| MDD | -7.89% | -9.01% |
| Profit Factor | 3.57 | 8.89 |
| 最大連續虧損 | 2 | 1 |

### vs TSM-006 比較

| 指標 | TSM-006 | TSM-007 | 變化 |
|------|---------|---------|------|
| min(A,B) Sharpe | 0.46 | **0.64** | **+39%** |
| Part A Sharpe | 0.46 | 0.64 | +39% |
| Part B Sharpe | 0.57 | 1.32 | +132% |
| Part A WR | 66.7% | 75.0% | +8.3pp |
| Part B WR | 73.3% | 90.0% | +16.7pp |
| Part A 訊號 | 18 | 12 | -33%（更精選） |
| Part B 訊號 | 15 | 10 | -33%（更精選） |

### 關鍵發現

1. **相對強度 > 絕對動量**：TSM-SMH 報酬差 >= 5% 比 ROC(20) >= 10% 更精確。相對強度過濾了「整個半導體板塊都在漲」的時段（低 alpha），聚焦 TSM 自身的超額表現
2. **RS 5% 是甜蜜點**：3% 太鬆（Part A 加入 2019-05、2023-02 兩筆停損訊號），8% 太嚴（Part A 僅 8 訊號、Part B 僅 3 訊號，統計不足）
3. **Part B 優異但非過擬合**：Part B Sharpe 1.32 遠高於 Part A 0.64，但這反映 2024-2025 TSM 因 AI 需求確實具備板塊超額表現，非策略過擬合
4. **2022 熊市仍有 2 筆停損**：2022-11 和 2022-12，TSM 在短暫反彈中相對 SMH 表現好但隨後繼續下跌。SMA(50) 未能完全過濾
5. **訊號數適中**：Part A 2.4/年、Part B 5.0/年，絕對數量 12/10 接近平衡

---

## TSM-008: RS Exit Optimization

**目標**：沿用 TSM-007 已驗證最佳的進場條件（RS≥5% + pullback 3-7% + SMA50），獨立優化出場參數。TSM-007 的出場（TP+7%/SL-7%/20天）直接沿用 TSM-006 動量回調的參數，從未針對 RS 進場特性獨立調整。

### 進場條件（與 TSM-007 完全相同）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | TSM-SMH 20日報酬差 | ≥ 5% | TSM 相對板塊超額表現 |
| 2 | 5日高點回撤 | 3-7% | 短暫整理 |
| 3 | Close > SMA(50) | — | 上升趨勢確認 |
| 冷卻 | 訊號間隔 | ≥ 10 交易日 | 避免重複訊號 |

### 出場參數（Att2 最佳版本）

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 | +8% | RS 動量進場在強趨勢中，+8% 可行（vs 均值回歸 +8% 失敗） |
| 停損 | -7% | 與 TSM-007 相同 |
| 持倉天數 | 25 天 | 延長 5 天讓邊際到期交易有更多時間達標 |

### 三次嘗試結果

| 指標 | TSM-007 (基線) | Att1 (25d) | Att2 (TP+8%/25d) | Att3 (TP+7.5%/25d) |
|------|---------------|------------|-------------------|---------------------|
| TP/SL/Hold | +7%/-7%/20d | +7%/-7%/25d | **+8%/-7%/25d** | +7.5%/-7%/25d |
| Part A Sharpe | 0.64 | 0.72 | **0.79** | 0.76 |
| Part B Sharpe | 1.32 | 1.32 | **0.83** | 0.79 |
| min(A,B) | 0.64 | 0.72 | **0.79** | 0.76 |
| A/B gap | 0.68 | 0.60 | **0.04** | 0.03 |
| Part A WR | 75.0% | 75.0% | 75.0% | 75.0% |
| Part B WR | 90.0% | 90.0% | 80.0% | 80.0% |
| Part A 累計 | +47.59% | +55.97% | **+69.59%** | +62.65% |
| Part B 累計 | +68.50% | +70.81% | +59.78% | +53.95% |

### 關鍵發現

1. **延長持倉 20→25天改善 Part A**：Att1 中 Part A Sharpe 0.64→0.72，讓邊際到期交易（2020-07-27）有更多恢復時間
2. **TP+8% 在 RS 動量進場下可行**：與 TSM-004 均值回歸 TP+8% 失敗不同，RS 動量進場的交易處於強相對趨勢中，+8% 達標率高。Part A 9/12 全部達標，Part B 8/10 達標
3. **TP+8% 改善 A/B 平衡**：Part B 1 筆交易（2024-10-31）原本在 TP+7% 達標，TP+8% 後反轉停損。但 Part A 每筆贏利多 +1pp 使 Part A Sharpe 從 0.72→0.79。net 效果：min(A,B) 提升，A/B gap 大幅收窄
4. **TP+7.5% 不是甜蜜點**：2024-10-31 交易在 +7.5% 也未達標（與 +8% 同樣翻轉停損），所以 TP+7.5% 只得到較低的贏利而沒有救回該交易
5. **TP+8% 是 TSM RS 策略的甜蜜點**：+7% 壓縮獲利空間，+8% 是所有 Part A 贏利交易均可達標的上限

---

## TSM-010: Multi-Week Regime-Aware MBPC (3 次嘗試均失敗)

**目標**：將 lesson #22「buffered multi-week SMA trend regime」+ ATR vol regime 跨資產移植自 NVDA-013 Att3（min 0.55 全域最優）至 TSM。Repo 第 2 次 lesson #22 + MBPC 試驗，首次半導體個股 NVDA→TSM 跨資產移植。

### 設計理念

NVDA-013 Att3 在半導體個股 NVDA 上以「Donchian 20d 突破 + 5d 淺回檔 + RSI [40,65] + Close>SMA(50) + SMA(20)≥1.00×SMA(60) strict trend regime + ATR(20)≤1.40×ATR(60) vol regime」達成 min(A,B) 0.55，+34% vs NVDA-009 baseline 0.41。

跨資產假設：TSM 與 NVDA 同為高波動半導體個股（TSM ~2.1% vol vs NVDA ~3% vol），預期 lesson #22 雙重 regime gate 能精準分隔「真實多週期上升 regime」與「late-cycle / chop regime」，過濾 Part A 的中國地緣政治震盪 + AI 高基期回檔失敗訊號。

### 三次嘗試結果

| 指標 | TSM-008 (基準) | Att1 (NVDA-013 直接移植) | Att2 (VOO-004 收緊) | Att3 (NVDA-013 + 2DD cap -2%) |
|------|---------------|------------------------|--------------------|--------------------------------|
| breakout_recency | — | 10d | 5d | 10d |
| pullback range | — | [-3%, -8%] | [-2%, -5%] | [-3%, -8%] |
| RSI 範圍 | — | [40, 65] | [40, 65] | [40, 65] |
| SMA regime k | — | 1.00 strict | 1.00 strict | 1.00 strict |
| ATR vol regime | — | ≤ 1.40 | ≤ 1.40 | ≤ 1.40 |
| 2DD cap | — | 停用 | 停用 | ≥ -2% |
| **Part A Sharpe** | 0.79 | **0.03** | **-0.10** | **0.08** |
| **Part B Sharpe** | 0.83 | **0.23** | **0.26** | **0.23** |
| **min(A,B)** | **0.79** | **0.03** | **-0.10** | **0.08** |
| Part A 訊號 | 12 | 19 | 13 | 14 |
| Part B 訊號 | 10 | 12 | 5 | 12 |
| Part A WR | 75.0% | 47.4% | 46.2% | 50.0% |
| Part B WR | 80.0% | 58.3% | 60.0% | 58.3% |

### 失敗根因分析

1. **TSM Part A multi-regime 結構**：TSM 2019-2023 含 4+ regimes（中美貿易戰 / COVID 震盪 / AI hype / 半導體景氣週期），SLs 散佈於多 regime，與 NVDA Part A SLs 集中於 2022 bear 結構不同
2. **lesson #22 SMA regime 缺乏選擇性**：TSM Part A SLs 多發生於 SMA(20)/SMA(60) 仍 > 1.00 的「短暫地緣政治震盪 / 產業景氣轉折」期間，雙重 regime gate 無法切除
3. **ATR vol regime 同樣失效**：TSM 的「短暫 shock」往往伴隨 ATR 短期擴張但仍 < 1.40 × ATR(60) 的中等水準
4. **Att2 VOO-004 方向反向失敗**：VOO 上 tight→loose 翻轉 0.12→1.12（+833% Sharpe），TSM 上 tight→loose 翻轉 0.00→-0.38——**進場敏感度方向取決於資產 regime 結構**（lesson #4 邊界擴展）
5. **Att3 2DD cap 邊際改善但仍遠不足**：MBPC 進場本質為「shallow pullback」，signal day 2DD 集中淺帶（-3%~0%），2DD cap 在 MBPC 框架選擇力 << MR 框架（DIA-012/CIBR-012/USO-023 顯著有效）

### 跨資產 / 跨策略貢獻

1. **lesson #21 失敗家族擴展至 TSM 半導體 cross-asset**：先前 lesson #21 適用範圍為「single-pure-uptrend 大型廣基 ETF（VOO）」或「single-regime growth 個股配 lesson #22（NVDA-013）」。**TSM-010 證明即使是同類半導體個股，multi-driver 結構差異使 lesson #22 + MBPC 跨資產移植結構性失敗**
2. **新規則候選**：lesson #22 + MBPC 適用於「single-secular-driver 高波動個股」，**不適用於多重結構性驅動因子的個股**（TSM 為首例 multi-driver 失敗：中國地緣政治 + 半導體週期 + 客戶集中度）
3. **進場敏感度方向取決於資產 regime 結構**（lesson #4 邊界擴展）：VOO 單一 secular uptrend 中 tight 捕捉高品質訊號；TSM multi-regime 中 tight 反而捕捉「短暫 regime 突破中的假動量」訊號
4. **lesson #19 family 邊界擴展（2DD cap on MBPC）**：MR 框架 2DD cap 顯著有效；MBPC 框架選擇力受限，因 MBPC 進場本質為「shallow pullback」signal day 2DD 集中淺帶
5. **TSM 全域最優確認**：TSM-008 RS framework 0.79 為當前最佳，TSM-010 三次迭代全部退化於 0.46（TSM-006 momentum pullback baseline）以下，反映 **TSM 的最佳訊號來源為「TSM/SMH RS spread」**（cross-sectional 機制天然消化半導體週期 effect）。**TSM 第 10 次實驗、30+ 次嘗試**確認 RS framework 為 TSM cyclical multi-regime 結構下的最佳策略類型

### 結論

TSM-010 確認 **TSM-008 RS framework 為當時全域最優**。未來 TSM 突破 0.79 可能需要：
- 更精細的 RS 框架（動態 SMH 權重、加入 INTC/AMD/QCOM 三角 RS）
- Calendar effect filter（Q4 holiday demand、Q2 capex slowdown）
- 客戶集中度 regime（Apple/NVDA 訂單變動）
- 不應再嘗試純技術面 MBPC / MR 框架——TSM-010 確認 cyclical multi-regime 結構性限制

> **2026-05-02 更新**：TSM-011 Att3 透過 RS framework 上的 signal-day 5d return CEILING（rally exhaustion filter）達成 min(A,B) 0.83 (+5%)，**首次突破 TSM-008 0.79 結構性上限**。突破點為 lesson #19 family cross-strategy 鏡像擴展（MR floor → momentum ceiling），詳見下方 TSM-011 段落。

---

## TSM-011: Signal-Day Direction Filter on RS Momentum Pullback ★ 全域最優

**目標**：在 TSM-008 RS 動量回調框架上加入 signal-day return CEILING 過濾，解決「rally exhaustion 偽訊號」（5 日已大漲後出現淺回檔但實為趨勢反轉前兆）。**Repo 首次「return CEILING（rally exhaustion filter）」於任何資產 + repo 首次 lesson #19 family cross-strategy 鏡像擴展（MR floor → momentum ceiling）。**

### 設計理念（lesson #19 family v10）

既往 lesson #19 family 全部為 FLOOR 方向（capitulation depth filter）：
- DIA-012「1d cap + 3d cap」、SPY-009「1d floor」、EWJ-005「1d floor」、EWZ-007「1d cap」、CIBR-014「1d cap + ATR BAND」、SIVR-018「ATR ceiling + 3d floor」、URA-013「5d cap」、INDA-011「2d floor + 3d cap」、GLD-014「2d floor + 1d floor」
- 這些皆為 MR 框架（pullback+WR+ClosePos / BB-lower+ClosePos / RSI-hook 等），對應失敗模式為「淺 capitulation」訊號

TSM-011 提出鏡像擴展假設：
- **RS 動量框架失敗模式 = 太深 rally**（rally exhaustion）
- 對應過濾方向 = **return CEILING**
- 平行於 MR 的「太淺 capitulation = floor 過濾」結構性鏡像

具體假設：TSM-008 Part A 的 2 SLs（2022-11-21 / 2022-12-07）+ 1 expiry（2020-07-24 -1.72%）皆有「signal-day 之前 5 日大漲，出現 3-7% 淺回檔即觸發 RS 訊號，但隨後續跌停損 / 到期未達 +8%」結構。5d return ceiling 過濾「prior 5 日已大漲」狀態下的訊號。

### 三次迭代結果

| 指標 | TSM-008 (baseline) | Att1 (1d ceiling +1.0%) | Att2 (5d ceiling +9.5%) | Att3 ★ (5d ceiling +10.5%) |
|------|---------------------|--------------------------|--------------------------|------------------------------|
| 1d ceiling | — | +1.0% | 停用 | 停用 |
| 5d ceiling | — | 停用 | +9.5% | **+10.5%** |
| **Part A Sharpe** | 0.79 | **0.78** | **1.30** | **0.86** |
| **Part B Sharpe** | 0.83 | 0.83 | 0.83 | 0.83 |
| **min(A,B)** | **0.79** | 0.78 | 0.83 | **0.83** |
| Part A WR | 75.0% | 75.0% | **90.9%** | **83.3%** |
| Part A 累計 | +69.59% | +68.73% | **+87.38%** | **+74.10%** |
| Part B 累計 | +59.78% | +59.78% | +59.78% | +59.78% |
| Part A/B 累計差 | 14.1% ✓ | 13.0% ✓ | 31.6% ✗ | **19.3% ✓** |
| Part A/B 訊號比 | 12/10 ✓ | 12/10 ✓ | 11/10 ✓ | 12/10 ✓ |

### Att1 失敗分析（1d ceiling +1.0%）

過濾 2020-07-24（1d +9.69%）但 cooldown chain shift 引入 2020-07-31 expiry **-2.22%**（比原 -1.72% 更差）。**1d ceiling 單獨無效**——signal-day 1d 過大的訊號在 TSM 上稀少（僅 2020-07-24 一筆），其他失敗訊號 1d 已為負（2022-11-21 -2.84%、2022-12-07 -0.40%、2024-07-16 +0.44% 邊界外、2024-10-30 -1.25%）。

### Att2 結構性突破但 A/B 失衡

5d ceiling +9.5% 過濾 3 個訊號：
- Part A 2020-07-24（5d +11.30%, expiry -1.72%）→ cooldown shift 至 2020-07-31 expiry **+0.89%**（從負轉正）
- Part A 2022-11-21（5d +9.79%, SL -7.09%）→ cooldown shift 至 2022-11-28 SL -7.09%（同類），但連帶讓 2022-12-07 SL 被新 cooldown 抑制，**淨效果為 2 SLs → 1 SL**
- Part B 2024-02-12（5d +9.82%, TP +8%）→ cooldown shift 至 2024-02-13 TP +8%（同 +8%，無損）

**Part A WR 75.0%→90.9%, Sharpe 0.79→1.30, cum +69.59%→+87.38%**（**結構性突破**）。但 Part A 累計大幅躍升使 A/B 差距從 14.1% 升至 31.6%（略超 30% 目標）。

**Att2 邊界精準度發現**：2022-11-21 SL（5d +9.79%）與 2024-02-12 TP（5d +9.82%）邊界差距僅 **0.03 percentage points**，5d 為高度非線性 discriminator。

### Att3 ★ 保守邊界達成全部 acceptance criteria

5d ceiling +10.5% 僅過濾 1 個訊號：
- Part A 2020-07-24（5d +11.30%, expiry -1.72%）→ cooldown shift 引入 2020-07-31 expiry +0.89% + 2020-08-20 TP +8%
- Part B 完全不受影響（最高 5d 為 2024-02-12 +9.82% < +10.5%）

**結果**：
- Part A: Sharpe **0.86** (+9% vs baseline), cum **+74.10%**, WR **83.3%**, 12 訊號
- Part B: Sharpe 0.83（不變）, cum +59.78%, WR 80.0%, 10 訊號
- min(A,B) **0.83** (+5% vs TSM-008 0.79)
- **A/B 累計差 19.3% (< 30% ✓)**, A/B 訊號比 1.2:1 (gap 16.7% < 50% ✓)

### Part A 完整逐筆交易

| 訊號日期 | 出場類型 | 報酬 | 持倉天數 |
|---------|---------|------|---------|
| 2019-10-18 | TP | +8.00% | 10 |
| 2020-07-31 | 到期 | **+0.89%** | 25（從原 -1.72% 改善為 +0.89%，cooldown shift） |
| 2020-08-20 | TP | +8.00% | 16（cooldown shift from 2020-08-10）|
| 2020-09-16 | TP | +8.00% | 15 |
| 2020-12-09 | TP | +8.00% | 15 |
| 2021-01-08 | TP | +8.00% | 3 |
| 2021-01-26 | TP | +8.00% | 10 |
| 2022-01-05 | TP | +8.00% | 5 |
| 2022-11-21 | SL | -7.09% | 19（保留，5d +9.79% < +10.5%）|
| 2022-12-07 | SL | -7.09% | 13（保留）|
| 2023-01-19 | TP | +8.00% | 2 |
| 2023-10-20 | TP | +8.00% | 14 |

### 跨資產 / 跨策略貢獻

1. **Repo 首次「return CEILING（rally exhaustion filter）」於任何資產**——既往 lesson #19 family 全部為 FLOOR 方向（capitulation depth filter），TSM-011 開啟鏡像 CEILING 方向
2. **Repo 首次 cross-strategy lesson #19 移植**：MR 框架 → RS momentum 框架（lesson #21 family），與既往 lesson #19 全部於 MR 框架平行
3. **MR 失敗模式（太淺 capitulation）vs momentum 失敗模式（太深 rally）為結構性鏡像**——確立 lesson #19 family v10 雙向對稱性
4. **5d > 1d ceiling 區分力**——signal-day 1d 過濾因 cooldown chain shift 反向（Att1）而 5d 過濾因 2020-07-24 受 prior 5d 大漲驅動（5d +11.30 vs 1d +9.69 同向 signal）使 5d 為較穩健 rally exhaustion proxy
5. **保守 vs 激進門檻 trade-off**：Att2 (+9.5%) 為「Part A 結構最優」（Sharpe 1.30）但 A/B 失衡；Att3 (+10.5%) 為「criteria 全部達標」的保守選擇——保守 ceiling 透過 cooldown chain shift 仍能透過 expiry 改善獲得 +5% min(A,B)

### 跨資產假設（待驗證）

Rally exhaustion 5d ceiling 可能適用於其他 RS / MBPC 動量框架，閾值需依資產 5d return 分布調整：
- NVDA-006 RS（NVDA-SMH RS）：類似 TSM-008 結構，預期 5d ceiling +10~12%（NVDA 較高 vol）
- VOO-004 MBPC（broad-uptrend ETF）：MBPC 進場本質為「淺回檔」，5d 已較低，預期 ceiling +6~8%
- SOXL-010 RS（leveraged RS）：3x 槓桿 vol 約 3x，預期 ceiling +25~30%
- EWT-008 / SPY-009 等其他 RS / MBPC 框架

下次跨資產驗證可優先試 NVDA-006 或 SOXL-010（同 RS 框架，cross-asset 移植最穩）。

### 結論

TSM-011 Att3 為 **TSM 第 11 次實驗、33+ 次嘗試的新全域最優**（min 0.83 vs TSM-008 0.79，+5%）。lesson #19 family v10 鏡像擴展（FLOOR ↔ CEILING）開啟 momentum 框架的「太深 rally」過濾新方向，與既有 MR 框架的「太淺 capitulation」過濾結構性正交。

---

## TSM-012: Volume-Confirmed RS Momentum Pullback (3 次嘗試均失敗)

**目標**：在 TSM-008 RS 動量回調框架上加入 signal-day volume ratio 過濾，測試 volume 維度是否提供與 TSM-011 5d return ceiling 結構性正交的補充過濾力。**Repo 第 3 次 volume filter 主訊號試驗、首次於 RS momentum 框架。**

### 設計理念與雙向假設

跨資產證據（lesson #6 邊界 + 反例 8 SIVR-017 結論）：volume-based filters（URA-011 Volume spike、SIVR-017 MFI volume-weighted oscillator）作為主訊號在 active MR regime 通常 supplementary 而非 substitutive——創造 A/B 對稱性但不突破品質天花板。在 RS momentum 框架（非 MR）上 volume 維度尚未驗證。

兩種對立假設（across iterations 測試）：
- **H1（capitulation buy）**：訊號日 volume / 20日均量 >= K → 高量回調 = 機構集中拋售完成 = 進場品質高
- **H2（orderly continuation）**：訊號日 volume / 20日均量 <= K → 低量回調 = 健康 profit-taking = 趨勢延續品質高

### 三次迭代結果

| 指標 | TSM-011 Att3 (baseline) | Att1 (vol >= 1.30, H1) | Att2 (vol <= 1.20, H2) | Att3 (vol >= 1.10) |
|------|-------------------------|-------------------------|-------------------------|--------------------|
| **Part A Sharpe** | 0.86 | **1.56** | 0.54 | **1.76** |
| **Part B Sharpe** | 0.83 | 0.65 | 0.54 | 0.65 |
| **min(A,B)** | **0.83** | 0.65 | 0.54 | 0.65 |
| Part A 訊號數 | 12 | 5 | 9 | 6 |
| Part B 訊號數 | 10 | 4 | 7 | 4 |
| Part A WR | 83.3% | 80.0% | 66.7% | **83.3%** |
| Part B WR | 80.0% | 75.0% | 71.4% | 75.0% |
| Part A 累計 | +74.10% | +33.71% | +33.94% | **+44.41%** |
| Part B 累計 | +59.78% | +17.04% | +26.84% | +17.04% |
| Part A/B 累計差 | 19.3% ✓ | 49.4% ✗ | 21.0% ✓ | **62.0% ✗** |

### Att1 失敗分析（vol_ratio_min >= 1.30，H1 capitulation buy）

vol >= 1.30 過於嚴苛——訊號數從 12→5 (Part A) / 10→4 (Part B)，**雙 Part 縮減約 60%**。保留訊號 Part A 4/5 為 TP（Part A Sharpe 飆升至 1.56）但 Part B **2024-07-08 SL（vol 高，屬 capitulation 範疇但 5d 跌幅深，後續 1 週繼續下跌）仍存活於高 vol 過濾下**——確認「volume confirmation 無法區分真假 capitulation」，與 lesson #20b 失敗家族（RSI/CCI/Stoch/MACD hook）平行。

### Att2 失敗分析（vol_ratio_max <= 1.20，H2 orderly continuation）

低 vol 過濾保留更多訊號（9/7）但品質下降——**2022-11-21 SL 與 2022-12-07 SL（TSM-008 baseline 已知失敗訊號）通過 vol <= 1.20 缺口進入**。orderly continuation 假設失敗：低 vol 包含「無動量參與的弱訊號」而非「健康 profit-taking」。Part A WR 從 baseline 75.0%→66.7%（增加 SLs），Sharpe 從 0.79→0.54。

### Att3 失敗分析（vol_ratio_min >= 1.10，moderate floor）

放寬 floor 至 1.10 增加 1 個 Part A 訊號（2021-01-26 TP）使 Part A Sharpe 飆升至 1.76（cum +44.41%）但 **Part B 完全相同（2024-07-08 SL 仍存活）**——結構性 A/B 失衡（A/B Sharpe 差 1.11、A/B 累計差 62%）。

**新發現（Volume filter A/B regime asymmetry）**：絕對 vol_ratio threshold（如 >= 1.10）在「Part A 高波動 / Part B 低波動」結構下**系統性 A/B 失衡**——Part A 高 vol 訊號天然密集於 2020-2023 高波動期，Part B 2024-2025 較低波動期 vol 整體偏低，floor filter 系統性傾向 Part A。Volume filter 在多 regime 期間需 vol normalization（rolling z-score 而非 ratio）以避免結構性偏差。

### 跨資產 / 跨策略貢獻

1. **lesson #6 邊界第三次擴展**：volume-based filters 作為 supplementary not substitutive 維度規則從 MR 框架（URA-011 Volume spike、SIVR-017 MFI MR）擴展至 RS momentum 框架（TSM-012 三次失敗），三類框架皆驗證
2. **新規則候選**：volume filters as primary screening dimension 在 active price-momentum-driven 框架（MR 與 RS momentum 兩類）皆無效，建議僅作為 secondary confirmation 維度與其他主要 price-action filter（5d ceiling、2DD cap、ClosePos）combination 使用
3. **Volume filter A/B regime asymmetry 新發現**：絕對 vol_ratio threshold 在多 regime 期間結構性 A/B 失衡，需 rolling z-score normalization
4. **2024-07-08 Part B SL 結構性穿透**：volume confirmation 無法區分真假 capitulation，與 oscillator hook 失敗家族（lesson #20b）平行

### 結論

TSM-012 三次迭代全部失敗 vs TSM-011 Att3 baseline min 0.83。**Volume 維度從 TSM 已驗證無效方向中剔除**。TSM-011 Att3 仍為 TSM 第 12 次實驗、36+ 次嘗試的全域最優。

---

## TSM-013: TSM-QQQ Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback (3 次嘗試 Att1 PARTIAL)

**目標**：在 TSM-011 Att3 RS Momentum Pullback 框架（TSM-008 entry + 5d ceiling +10.5%）上加入 TSM-QQQ 20d 報酬差 CEILING 過濾，測試 cross-asset divergence regime gate 在「multi-driver 半導體 ADR 個股 + RS Momentum Pullback 框架」是否能進一步突破 0.83 結構性上限。**Repo 第 6 次 cross-asset divergence regime gate 跨資產移植、首次半導體 ADR 個股 + RS Momentum Pullback 框架。**

### 設計理念

跨資產證據（lesson #19 family v3 / lesson #26 family v2）：cross-asset divergence regime gate 既有成功案例：
- TLT-014 (TLT-SPY 20d FLOOR, 利率 vs 股票 MR, min +393%)
- TSLA-017 (TSLA-QQQ 20d FLOOR, 高波動 AI 個股 vs 大盤 BB Squeeze, min +81%)
- INDA-012 (INDA-EEM 60d CEILING, 單一國家 vs 大盤 EM MR)
- EWZ-009 (EWZ-EEM 10d CEILING, 商品國 EM vs 大盤 EM MR)
- NVDA-021 (NVDA-QQQ 20d CEILING, 高波動 AI 個股 vs 大盤 MBPC, min +160%)

TSM-013 鏡像 NVDA-021 結構（CEILING + 高波動 AI 個股 vs 大盤），但移植至 RS Momentum Pullback 框架。

### 三次迭代結果

| 指標 | TSM-011 Att3 (baseline) | Att1 ★ (lookback=20, max_rel=+15%) | Att2 (lookback=20, max_rel=+10%) | Att3 (lookback=10, max_rel=+10%) |
|------|-------------------------|------------------------------------|----------------------------------|-----------------------------------|
| **Part A Sharpe** | 0.86 | 0.00 zero-var | 0.00 zero-var | 0.31 |
| **Part B Sharpe** | 0.83 | 0.83 | **0.65** | 0.83 |
| **min(A,B)** | **0.83** | **0.83 TIE†** | 0.65 REJECT | 0.31 REJECT |
| Part A 訊號數 | 12 | **9** | 5 | 8 |
| Part B 訊號數 | 10 | 10（不變）| 8 | 10（不變）|
| Part A WR | 83.3% | **100%** | 100% | 62.5% |
| Part B WR | 80.0% | 80.0% | 75.0% | 80.0% |
| Part A 累計 | +74.10% | **+99.90%** | +46.93% | +16.93% |
| Part B 累計 | +59.78% | +59.78% | +36.98% | +59.78% |
| Part A MDD | -7.89% | **-6.06%** | -6.06% | -8.42% |
| Part A 累計差 | 19.3% ✓ | 39.9% ✗ (zero-var) | 21.2% ✓ | 71.7% ✗ |

†Part A zero-var 結構性最優、Part B 變異 Sharpe 為 binding constraint，沿用 EWJ-003/SPY-009/DIA-012/IWM-013/CIBR-014 † 慣例。

### Att1 PARTIAL 分析（lookback=20, max_relative_return=+0.15）

CEILING +15% 過濾 Part A 全部 2 SLs + 1 winner，殘留全部 9 個訊號為 TPs（zero-var）。Part A 累計從 +74.10%→+99.90%（+35%）、WR 從 83.3%→100%（+17pp）、MDD 從 -7.89%→-6.06%（-23%）。但 Part B 完全 unchanged——Part B 全部 10 個訊號的 TSM-QQQ 20d 皆 < +15%，filter 對 Part B **完全非綁定**。

### Att2 失敗分析（lookback=20, max_relative_return=+0.10，收緊）

收緊至 +10% 過度過濾 Part A 4 個 winners（5 個訊號殘留），Part A cum 從 +99.90%→+46.93%。Part B **2024-07-16 / 2024-10-30 兩個 SLs 依然存活**（兩者 Rel_QQQ_20d < +10%），但移除 Part B 2 個 winners（2025-01-10 / 2025-09-25，Rel_QQQ_20d 介於 [+10%, +15%]）→ Part B WR 80%→75%、Sharpe 0.83→**0.65**（-22%）。

### Att3 失敗分析（lookback=10, max_relative_return=+0.10，短週期）

10d lookback 縮短後 Part A SLs 之 Rel_QQQ 分布變化：原 20d Att1 +15% 過濾的 3 SLs 在 10d 維度未被 +10% 閾值清除（短週期 Rel_QQQ 較 noisy，分布更寬廣）。Cooldown chain shift 在 Part A 引入額外 SLs（max consec losses 從 0→2），Part A WR 100%→62.5%、Sharpe 0.00 zero-var→0.31。Part B 完全非綁定。

### 結構性反向發現（repo 首次跨 Part SLs divergence 反向）

**TSM Part A 與 Part B SLs 在 Rel_QQQ_20d 維度結構性反向**：
- **Part A SLs**：高 Rel_QQQ（>+15%），rally exhaustion 結構，CEILING 方向有效 ✓
- **Part B SLs**（2024-07-16 / 2024-10-30）：低 Rel_QQQ（<+10%），earnings drift / sector-specific drop 但 QQQ 同步上漲 → TSM 相對沒有過度跑贏，CEILING 方向結構性失敗 ✗

**單一 CEILING threshold 結構性無法雙 Part 同步改善**，Part B 為 binding constraint，CEILING 方向結構性無法突破 0.83。

### 與 NVDA-021 結構對比

NVDA-021（同 CEILING + 同 cross-asset divergence + 高波動 AI 個股）成功 min 0.55→1.43（+160%）：NVDA Part A/B SLs 皆集中於高 Rel_QQQ（CEILING 方向結構性一致）。

TSM-013 失敗根因：TSM 為 multi-driver 結構（中國地緣政治 + 半導體景氣 + 客戶集中度 + 新興市場 ADR earnings cycle）使 Part B SLs 機制不同於 Part A——**不同 driver 產生不同 SLs 在 divergence 維度的結構**。NVDA single-secular AI driver 使 Part A/B SLs 在同一機制下對齊 Rel_QQQ 分布。

### 跨資產 / 跨策略貢獻（lesson #19/#26 family v2 邊界精煉）

1. **Repo 第 6 次 cross-asset divergence regime gate 跨資產移植**：擴展至半導體 ADR 個股 + RS Momentum Pullback 框架（先前 NVDA-021 為 MBPC、INDA-012 / EWZ-009 為 MR、TSLA-017 為 BB Squeeze、TLT-014 為 MR）
2. **Repo 首次跨 Part SLs 結構反向發現**：TSM Part A SLs 高 Rel_QQQ / Part B SLs 低 Rel_QQQ，單一 CEILING 結構性無法雙 Part 同步改善
3. **新跨資產規則候選（lesson #19/#26 family v3 邊界）**：cross-asset divergence regime gate 適用邊界擴展為「Part A/B SLs 在 divergence 維度單向對齊」雙條件
   - NVDA-021 ✓（雙 Part 對齊高 Rel_QQQ → CEILING 成功 +160%）
   - TLT-014 ✓（雙 Part 對齊低 Rel_SPY → FLOOR 成功 +393%）
   - TSLA-017 ✓（雙 Part 對齊低 Rel_QQQ → FLOOR 成功 +81%）
   - INDA-012 ✓（雙 Part 對齊 → CEILING 成功）
   - EWZ-009 ✓（雙 Part 對齊 → CEILING 成功）
   - **TSM-013 ✗**（雙 Part SLs 結構性反向，CEILING 僅解 Part A）
4. **Multi-driver 個股 vs single-driver 個股**：multi-driver 結構使 Part A/B SLs 機制反向，single-driver（NVDA AI / TSLA EV）使 Part A/B SLs 機制一致——新跨資產維度（driver 結構）為 cross-asset divergence regime gate 適用邊界 precondition
5. **Att1 為 partial-success 重要實質改善**：repo 首次將 cross-asset divergence regime gate（CEILING 方向）移植至半導體 ADR 個股 + RS Momentum Pullback 框架，Part A 結構性突破（zero-var all TPs）為實質改善但 Part B sample size + 結構不對齊使 min(A,B) TIE baseline

### 結論

TSM-013 三次迭代僅 Att1 PARTIAL（Part A 結構性突破 / Part B unchanged → min TIE baseline 0.83），Att2/Att3 REJECT。**Cross-Asset Divergence Regime Gate (CEILING) 結構性無法突破 TSM 0.83 ceiling**，Part B SLs 在 Rel_QQQ_20d 維度與 Part A 反向使單一 CEILING threshold 不可行。TSM-013 Att1 為 TSM 第 13 次實驗、39+ 次嘗試的 partial-success（repo 首次半導體 ADR + RS Momentum Pullback 框架 cross-asset divergence regime gate 試驗）。**TSM-011 Att3 仍為全域最優**。

---

## TSM-014: TSM-QQQ Cross-Asset Divergence BAND Regime-Gated RS Momentum Pullback (3 次嘗試全部 REJECT/TIE)

**目標**：直接回應 TSM-013 揭露之「Part A SLs 高 Rel_QQQ vs Part B SLs 低 Rel_QQQ」結構性反向假說，於 TSM-013 Att1（CEILING +15%）框架上加入 FLOOR（min_relative_return）形成雙向 BAND 結構，預期同時切除 Part A 高 Rel_QQQ rally exhaustion SLs（CEILING）+ Part B 低 Rel_QQQ single-stock drop SLs（FLOOR）。**Repo 首次 cross-asset divergence regime gate 雙向 BAND 變體於任何資產。**

### 設計理念

TSM-013 finding：cross-asset divergence regime gate 適用邊界候選（lesson #19/#26 family v3）為「Part A/B SLs 在 divergence 維度單向對齊」。對於「Part A/B SLs divergence 反向」結構資產，**BAND 變體（FLOOR + CEILING 同時應用）**為候選解。

平行 lesson #15 ATR ratio BAND 成功（URA-012 / FXI-014 / CIBR-014）：當 SLs 在 ATR ratio 維度集中於兩極端（高 / 低 ATR 鏡像分布）時，BAND 結構為對稱解。TSM-014 測試此 BAND 邏輯是否擴展至 cross-asset divergence 維度。

### 三次迭代結果

| 指標 | TSM-011 Att3 (baseline) | Att1 (FLOOR=-5%, CEILING=+15%) | Att2 (FLOOR=+5%, CEILING=+15%) | Att3 (FLOOR=+8%, CEILING=+15%) |
|------|-------------------------|--------------------------------|--------------------------------|--------------------------------|
| **Part A Sharpe** | 0.86 | 0.00 zero-var | 0.00 zero-var | 0.00 zero-var |
| **Part B Sharpe** | 0.83 | 0.83 | **0.74** | **0.42** |
| **min(A,B)** | **0.83** | **0.83 TIE†** | 0.74 REJECT | 0.42 REJECT |
| Part A 訊號數 | 12 | 9 | 9 | 7 |
| Part B 訊號數 | 10 | 10 | 9 | 6 |
| Part A WR | 83.3% | 100% | 100% | 100% |
| Part B WR | 80.0% | 80.0% | 77.8% | 66.7% |
| Part A 累計 | +74.10% | +99.90% | +99.90% | +71.38% |
| Part B 累計 | +59.78% | +59.78% | +47.94% | +17.44% |

†同 TSM-013 Att1 zero-var convention，Part A 結構性最優、Part B 變異 Sharpe 為 binding constraint。

### Att1 TIE 分析（FLOOR=-5%, CEILING=+15% 繼承 TSM-013 Att1）

FLOOR -5% 對 baseline 全部 19 訊號（9 Part A + 10 Part B）**完全非綁定**——所有訊號 Rel_QQQ_20d 皆 ≥ -5%。Att1 結果與 TSM-013 Att1 完全相同（Part A 9/100% zero-var / Part B 10 unchanged 0.83 / min 0.83）。

**關鍵發現（trade-level 分析揭露）**：Part B 兩個 SLs 之 Rel_QQQ_20d 為：
- 2024-07-16 SL: Rel_QQQ_20d = **+4.10%**（不為極端低值）
- 2024-10-30 SL: Rel_QQQ_20d = **+7.63%**（不為極端低值）

Part B winners Rel_QQQ_20d 範圍：[+1.48%, +12.37%]——**SLs 落於 winners 分布中段而非極端**，TSM-013 declare 之「Part B SLs 低 Rel_QQQ」假說為過度概括。

### Att2 REJECT 分析（FLOOR=+5%）

FLOOR +5% 過濾 Part B 2024-07-16 SL（+4.10% < +5%）✓ 但同時過濾 Part B 2024-12-19 winner（Rel_QQQ +1.48%）✗。Cooldown chain shift 將原 2025-01-10 winner 替換為 2025-01-16 SL（-7.09%）。

淨效果：Part B 10/8TP/2SL → 9/7TP/2SL，WR 80%→77.8%、Sharpe 0.83→**0.74**（-11%）。第二個 Part B SL（2024-10-30 Rel_QQQ +7.63%）仍存活。

### Att3 REJECT 分析（FLOOR=+8%）

FLOOR +8% 過濾**兩個** Part B SLs（+4.10% < +7.63% < +8%），但同時過濾 Part B 4 個 winners（Rel_QQQ +1.48% / +5.99% / +5.87% / +5.59%）。Cooldown chain shift 在 Part B 引入額外 SLs（最終 6/4TP/2SL）。Part A 2 winners 過濾。

淨效果：Part A 7/100% zero-var cum +71.38%（**較 baseline cum +74.10% 退化**），Part B 6/66.7%/Sharpe **0.42**（-49%）。

### 失敗根因

1. **TSM Part B SLs 非極端值**：trade-level 分析揭露兩個 Part B SLs（+4.10%, +7.63%）落於 winners 分布 [+1.48%, +12.37%] 中段，**Rel_QQQ_20d 維度對 Part B 結構性無區分力**——SLs 與 winners 在此維度分布重疊，單一 / 雙向 threshold 皆不可行
2. **BAND 變體有效邊界**：lesson #15 ATR ratio BAND 成功之必要條件為 SLs 集中於兩極端（鏡像分布）；TSM-014 失敗於「Rel_QQQ 維度 SLs 散落非極端」結構，**BAND 結構需 SLs 集中於兩極端為先決條件**
3. **Cooldown chain shift 副作用**：BAND 收緊後新增訊號（先前被冷卻抑制者）品質常低於原訊號，TSM-014 三次迭代皆觀察到此現象

### 跨資產貢獻（lesson #15 + lesson #19/#20 family v4）

1. **Repo 首次 cross-asset divergence regime gate 雙向 BAND 變體於任何資產**：擴展 lesson #20 family（先前皆為單向 CEILING / FLOOR）至 BAND 變體（直接平行 lesson #15 ATR ratio BAND）
2. **新跨資產規則 (lesson #15 + lesson #20 family v4)**：cross-asset divergence regime gate 適用邊界三條件：
   - (a) **target 為 narrow-scope vs broad benchmark**（INDA-EEM / TLT-SPY / TSLA-QQQ / NVDA-QQQ ✓）
   - (b) **Part A/B SLs 在 divergence 維度單向對齊**（單一 CEILING 或 FLOOR 解）
   - (c) **若 SLs 雙向反向，需驗證 SLs 是否集中兩極端方可採 BAND 變體**
   - TSM 違反 (b) 與 (c)：(b) Part A/B SLs 反向，(c) Part B SLs 非極端中段，BAND 變體擴展同樣失敗
3. **TSM Part B 0.83 binding constraint 結構性無解（Rel_QQQ_20d 維度）**：TSM-013（CEILING）+ TSM-014（BAND）兩次嘗試確認 Rel_QQQ_20d 維度對 Part B 結構性無區分力。未來突破方向需嘗試：
   - 不同 anchor（SOXX 半導體指數 / AAPL 主要客戶 / 已驗證失敗 NVDA pair）
   - 不同 lookback（5d / 10d / 60d Rel_QQQ）
   - 完全替代 framework（跳脫 RS Momentum Pullback 至 BB Squeeze Breakout / MR）
   - 非 cross-asset divergence 維度（如 IV-based filter / earnings calendar / multi-period capitulation）
4. **Multi-driver 個股 cross-asset divergence 失敗家族**：TSM-013（CEILING 失敗）+ TSM-014（BAND 失敗）整合確認 multi-driver 個股結構（中國地緣政治 + 半導體景氣 + 客戶集中度 + ADR earnings）使 Part A/B SLs 機制反向且非極端，cross-asset divergence regime gate 在此資產類別 **結構性不可行**

### 結論

TSM-014 三次迭代全部 REJECT/TIE vs TSM-011 Att3 baseline min 0.83。**Cross-Asset Divergence BAND 變體在 TSM 結構性失敗**——Part B SLs 落於 winners 分布中段使 BAND 結構（FLOOR + CEILING 同時應用）同樣不具選擇力。**Cross-asset divergence 維度從 TSM 已驗證無效方向中剔除**（TSM-013 CEILING + TSM-014 BAND 雙重否決）。TSM 第 14 次實驗、42+ 次嘗試。**TSM-011 Att3 仍為全域最優**。

---

## TSM-016: BB-Width Regime Gate on RS Momentum Pullback (3 次嘗試 Att2 ★ PARTIAL — 雙 Part 100% WR std=0)

**目標**：將 lesson #23 BB-Width Regime Gate（既有 TLT-007 / TQQQ-018 / SOXL-012 三次成功）首次 cross-strategy 移植至 RS Momentum 框架，過濾 elevated-vol regime 訊號。Hypothesis：TSM Part B 殘餘 SLs（2024-07-16 pre-earnings、2024-10-30 post-earnings drift）發生於 elevated-vol regime；BB-Width Regime Gate 切除 elevated-vol 訊號可同時保留 calm-regime momentum continuation winners。

### 設計理念

Lesson #23 既有適用範圍（截至 2026-05-09）：
- TLT-007 Att2（rate-driven MR，1% vol，閾值 0.05）✓
- TQQQ-018 Att3（leveraged broad index，~5% vol，閾值 0.48）✓
- SOXL-012 Att3（leveraged sector ETF，~6% vol，閾值 0.43）✓

TSM-016 為 cross-strategy 邊界擴展嘗試：~2% vol 半導體 ADR 個股 + RS Momentum Pullback 框架。

### 進場條件（沿用 TSM-011 Att3 + 新增第 5 條）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 相對強度 | TSM 20日報酬 - SMH 20日報酬 ≥ 5% | 板塊內超額表現 |
| 2 | 短期回調 | 5日高點回撤 3-7% | 暫時整理 |
| 3 | 趨勢確認 | Close > SMA(50) | 上升趨勢 |
| 4 | 5d return CEILING | 訊號日 5 日報酬 ≤ +10.5% | rally exhaustion 過濾 |
| **5** | **BB-Width Regime Gate** | **BB(20,2) Width / Close ≤ bb_width_max** | **calm regime gate** |
| 冷卻 | 訊號間隔 | ≥ 10 交易日 | 避免重複訊號 |

### 三次迭代結果

| 指標 | TSM-011 Att3 (baseline) | Att1 (bb_width_max=0.15) | Att2 ★ (0.12) | Att3 (0.14) |
|------|-------------------------|--------------------------|---------------|-------------|
| **Part A Sharpe** | 0.86 | 0.00 zero-var | 0.00 zero-var | 0.00 zero-var |
| **Part B Sharpe** | 0.83 | **0.42** | 0.00 zero-var | **-0.29** |
| **min(A,B)** | **0.83** | **0.42 REJECT** | 雙 Part std=0 PARTIAL | -0.29 REJECT |
| Part A 訊號數 | 12 | 5 | **3** | 3 |
| Part B 訊號數 | 10 | 6 | **2** | 6 |
| Part A WR | 83.3% | 100% | **100%** | 100% |
| Part B WR | 80.0% | 66.7% | **100%** | 33.3% |
| Part A 累計 | +74.10% | +46.93% | +25.97% | +25.97% |
| Part B 累計 | +59.78% | +17.44% | +16.64% | -13.08% |
| Part A SLs | 2 | 0 ✓ | 0 ✓ | 0 ✓ |
| Part B SLs | 2 | 2 (chain shift 替換) | **0** ✓ | 4 (earnings-week 復發) |

### Att1 REJECT 分析（bb_width_max=0.15 lenient）

過濾 12→5 Part A 訊號，移除 baseline 全部 2 Part A SLs（2022-11-21、2022-12-07）但同時移除 5 winners。Part B 10→6，原 2024-07-16 SL 與 2024-10-30 SL 被過濾，但**lesson #19 cooldown chain shift 中性化**：
- 原 2024-07-16 SL → 替換為 2024-07-08 SL（chain-shifted entry）
- 原 2024-10-30 SL → 替換為 2024-11-01 SL（chain-shifted entry）

淨效果：SL 數量未減少，反而 Part A winners 大量流失，Part B Sharpe 0.83→0.42。

### Att2 ★ PARTIAL 分析（bb_width_max=0.12 medium calm regime）

**雙 Part 結構性零方差（repo 第 6 次達成）**：Part A 3/3 TPs（+8% 全部）+ Part B 2/2 TPs（+8% 全部）。0.12 閾值同步過濾 baseline 雙 Part 全部 4 SLs + chain-shifted Att1 新增 2 SLs，6 SLs 全清除，sample 大幅縮減。

**A/B 平衡分析**：
- A/B 累計差（geometric annualized）：Part A 5 年 +25.97% → 4.7%/yr vs Part B 2 年 +16.64% → 8.0%/yr → gap 41%
- A/B 訊號比 0.6/yr vs 1.0/yr = gap 33% < 50% ✓
- **A/B cum gap 41% > 30% target ❌**——A/B 樣本數小 + Part A 5 年期 vs Part B 2 年期幾何稀釋

採 EWJ-005 / EWT-008 / SPY-009 / DIA-012 / IWM-013 / CIBR-014 等雙 Part std=0 慣例，Att2 為「結構性最優級別」但 A/B cum gap 違反使其不被採納為新 min(A,B) 全域最優——此為 **PARTIAL SUCCESS** 而非 ★ SUCCESS。

### Att3 REJECT 分析（bb_width_max=0.14 sweet-spot test）

0.14 閾值同時放回 cooldown chain 觸發的 earnings-week SLs：
- 2024-10-16 SL（T-1 to TSM Q3 earnings 10/17，BB width 0.13 通過 0.14 閾值）
- 2025-01-16 SL（同日 TSM Q4 earnings，BB width 0.13）
- 2024-11-01 SL（chain shift 持續）

確認 sweet spot 區間極窄（0.12 唯一甜蜜點），0.01-pt 偏離即崩壞。

### 跨資產發現（lesson #23 family v4 cross-strategy 邊界擴展）

1. **Repo 首次 lesson #23 BB-Width Regime Gate 移植至 RS Momentum 框架**——既有 TLT/TQQQ/SOXL 皆為 MR 或 leveraged ETF，TSM ~2% vol 半導體 ADR 個股 + RS Momentum 框架為新類別。
2. **TSM 適用閾值 0.12** 落於既有 4 個成功案例的對數線性區間（更貼近 vol 0-3% 區間的 [0.05, 0.20] 帶）。
3. **lesson #23 + lesson #19 family 整合**：BB-Width Regime Gate 適用於非槓桿 momentum 框架但受 lesson #19 cooldown chain shift 影響，sweet spot 區間極窄。
4. **「regime gate 對小 sample 策略」共通邊界**：當基底框架已將 sample 壓低（baseline 12+10），regime gate 進一步切除使年化幾何 cum 差難維持 < 30%；解釋 TSM-013 Att1 (Part A zero-var) 與 TSM-016 Att2 (雙 Part zero-var) 同樣為「結構性最優但 cum gap 違反」的對應。

### 結論

TSM-016 三次迭代 Att2 PARTIAL（雙 Part 100% WR std=0 但 A/B 累計 cum gap 41% 邊際違反 30% target）/ Att1 REJECT min 0.42 / Att3 REJECT min -0.29。**TSM-011 Att3 仍為 min(A,B) 全域最優**。

TSM-013/014/015/016 共四次嘗試確認 TSM 為 Sharpe-1.0 結構性難突破資產，未來方向：
- (a) earnings-date exclusion filter（Part B SLs 集中於 earnings ±15 日，TSM-016 Att3 失敗已證實 0.14 閾值放回 earnings-week SLs）
- (b) SOXX 半導體指數 anchor（TSM-013/014 用 QQQ、TSM-015 用 AAPL，SOXX 為更接近的 sector 同儕但 TSM 為 SOXX 成分股需驗證）
- (c) 完全替代 framework（lesson #22 multi-week regime + RS Momentum 組合）

TSM 第 16 次實驗、48+ 次嘗試。

---

## TSM-017: Earnings-Date Exclusion Filter on RS Momentum Pullback (3 次嘗試均失敗)

**目標**：直接回應 TSM-016 Att3 失敗報告 + AI_CONTEXT 列出之未驗證方向，將「earnings-week 為高 SL 風險區間」假說以正式 calendar exclusion filter 驗證。**Repo 首次 earnings-date exclusion filter 於任何資產**。

### 設計理念

TSM-016 Att3 失敗報告明確指出：「0.14 閾值同時放回 cooldown chain 觸發的 earnings-week SLs（2024-10-16 T-1 to earnings 10/17、2025-01-16 同日 earnings、2024-11-01 chain shift）」——暗示 earnings-week 集中 SL 為結構性風險。TSM-011 Att3 baseline Part B 殘餘 SLs 亦驗證此假說：

- 2024-07-16 SL：TSM Q2 2024 earnings = 2024-07-18，**2 日前**
- 2024-10-30 SL：TSM Q3 2024 earnings = 2024-10-17，**13 日後**

TSM-017 採「日期型 calendar filter」——時間維度而非價格/成交量維度，與既有 TSM 失敗類別（5d ceiling / volume / Rel_QQQ）正交。

### 進場條件（沿用 TSM-011 Att3 + 新增第 5 條）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 相對強度 | TSM 20日報酬 - SMH 20日報酬 ≥ 5% | 板塊內超額表現 |
| 2 | 短期回調 | 5日高點回撤 3-7% | 暫時整理 |
| 3 | 趨勢確認 | Close > SMA(50) | 上升趨勢 |
| 4 | 5d return CEILING | 訊號日 5 日報酬 ≤ +10.5% | rally exhaustion 過濾 |
| **5** | **Earnings-Date Exclusion** | **訊號日 ∉ ⋃[earnings - pre, earnings + post]** | **calendar days，TSM 季報前後排除** |
| 冷卻 | 訊號間隔 | ≥ 10 交易日 | 避免重複訊號 |

TSM 季報日期硬編碼於 config（2018-04-19 至 2026-04-16，共 33 筆），來自公開財報新聞。

### 三次迭代結果

| 指標 | TSM-011 Att3 (baseline) | Att1 (-10/+15) | Att2 (±5) | Att3 (±2) |
|------|-------------------------|----------------|-----------|-----------|
| **Part A Sharpe** | 0.86 | **0.42** (-51%) | 0.71 (-17%) | 0.78 (-9%) |
| **Part B Sharpe** | 0.83 | **0.98** (+18%) | **1.11** (+34%) | **1.11** (+34%) |
| **min(A,B)** | **0.83** | 0.42 REJECT | 0.71 REJECT | 0.78 REJECT |
| Part A 訊號數 | 12 | 7 | 10 | 11 |
| Part B 訊號數 | 10 | 6 | 7 | 7 |
| Part A WR | 83.3% | 71.4% | 80.0% | 81.8% |
| Part B WR | 80.0% | 83.3% | 85.7% | 85.7% |
| Part A 累計 | +74.10% | +19.28% | +49.26% | +61.20% |
| Part B 累計 | +59.78% | +36.52% | +47.44% | +47.44% |

**所有三次嘗試 Part B 皆顯著突破 baseline 0.83 → 0.98/1.11/1.11**，但 Part A 退化使 min(A,B) < baseline。

### Att1 REJECT 分析（asymmetric -10/+15 calendar days，25 日總窗口）

過寬窗口切除 5 個 Part A 訊號（12→7），Part A 累計從 +74.10% 崩至 +19.28%（-73%）。Part B 6 訊號中過濾原 2024-07-16 + 2024-10-30 兩 SLs（均落於 ±15 內），但 cooldown chain shift 引入 2024-11-04 SL（+18d post Q3，超出 +15 窗口）。

### Att2 REJECT 分析（bilateral ±5 calendar days，11 日窗口）

- 2024-07-16 SL（pre 2 days）✓ 過濾，激活 2024-06-27 TP（**淨 +1 winner**）
- 2024-10-30 SL（post 13 days，超出 ±5）NOT 過濾；但 cooldown chain shift 將其替換為 2024-10-23 SL（同 SL，淨 wash）
- Part A 12→10，損失 2 訊號

Part B Sharpe 0.83→1.11（+34%）為三次最大突破，但 Part A 0.86→0.71 仍使 min < baseline。

### Att3 REJECT 分析（bilateral ±2 calendar days，5 日窗口，最緊邊界）

最緊窗口僅損失 1 個 Part A 訊號（12→11）為三次最佳保留。Part B 結果與 Att2 相同（7 訊號，1.11 Sharpe）。**A/B 年化幾何 cum 差**：
- Part A 5 年 +61.20% → 10.0%/yr
- Part B 2 年 +47.44% → 21.4%/yr
- gap 53% > 30% target ❌

A/B 訊號比 11/5 = 2.2/yr vs 7/2 = 3.5/yr = gap 37% < 50% ✓。

### 核心失敗發現（lesson #20b 失敗家族擴展，repo 首次 earnings-date exclusion filter 於任何資產）

**Trade-level 重疊分析**：

| 訊號 | Part | 角色 | earnings 相對日 | 適用窗口 |
|------|------|------|---------------|---------|
| 2024-07-16 | B | SL | -2d (Q2) | 任何 pre ≥ 2 |
| 2024-10-30 | B | SL | +13d (Q3) | 任何 post ≥ 13 |
| 2024-04-16 | B | TP | -2d (Q1) | 任何 pre ≥ 2 ⚠️ |
| 2025-01-13 | B | TP | -3d (Q4) | 任何 pre ≥ 3 ⚠️ |
| 2023-01-19 | A | TP | +7d (Q4) | 任何 post ≥ 7 ⚠️ |

**結構性無解**：
- 對稱 ±2 過濾 2024-07-16 SL ✓ 與 2024-04-16 winner ✗（1:1 wash）
- 非對稱 -2/+14 過濾兩 SLs ✓ 但同時誤殺 2024-04-16 winner ✗ + 2023-01-19 winner ✗（2:2 wash）
- 後置 only +14 過濾 2024-10-30 SL ✓ 但誤殺 2023-01-19 winner ✗（1:1 wash）

**winner/SL 在 earnings-relative 日期維度為共生分布**而非可分離 cluster。

### 跨資產發現（lesson #6 邊界 + lesson #20b 擴展）

1. **Repo 首次 earnings-date calendar exclusion filter 於任何資產**——時間維度 filter 與既有 lesson #6 維度（價格/成交量/cross-asset return）正交，但 TSM 上仍受結構性日期重疊限制。
2. **新跨資產規則**：earnings-date exclusion filter 適用條件 = 「earnings-adjacent 訊號分布 winner-SL 比例顯著高於 non-earnings 訊號分布」。
3. **TSM 違反該條件**：半導體個股 earnings momentum（訊號 + winner 同樣集中於 pre-earnings）與 earnings risk（SL 同樣集中於 pre/post-earnings）兩股力量平衡，winners 與 SLs 在時間維度為共生而非反向分布。
4. **預期適用候選**：fundamentals-driven 個股（financial / consumer / healthcare），earnings 為 dominant catalyst 使 winner/SL 比例顯著偏移。**不適用**：cyclical individual stocks（半導體 / energy / commodity）earnings 為次要 catalyst。
5. **Part B +34% 改善 = TSM-016 Att3 假說「earnings-week 為高 SL 風險區間」確認**——但同時 winners 亦集中於 earnings 前 2-3 日，無法經由日期維度單向分離。

### 結論

TSM-017 三次迭代全部 REJECT，Part B 皆突破 0.83 → 0.98/1.11/1.11（**+18% / +34% / +34%**）但 Part A 退化使 min(A,B) < baseline。**TSM Part B 0.83 binding constraint 第 5 次結構性無解確認**（TSM-013/014/015/016/017 共五次嘗試）。TSM-011 Att3 仍為 min(A,B) 全域最優（17 次實驗、51+ 次嘗試）。

未來方向（更新 2026-05-09）：
- (a) **SOXX 半導體指數 anchor**（注意 TSM 為成分股自我參考性需謹慎）
- (b) **Multi-customer ensemble** (AAPL + MSFT + NVDA voting)
- (c) **完全替代 framework**（lesson #22 multi-week regime + RS Momentum 組合）
- (d) **Volatility-Acceleration BAND filter**（CIBR-014 / FXI-014 路徑——entry-day ATR(5)/ATR(20) BAND 而非 BB-Width regime）

已驗證無效並從候選清單剔除：
- ~~earnings-date exclusion filter~~（TSM-017 三次失敗）
- ~~Volume Confirmation Filter~~（TSM-012 三次失敗）
- ~~Cross-Asset Divergence (QQQ/AAPL anchor)~~（TSM-013/014/015 三次失敗）
- ~~BB-Width Regime Gate~~（TSM-016 PARTIAL 但 A/B cum gap 違反）

TSM 第 17 次實驗、51+ 次嘗試。

---

## TSM-018: ATR(5)/ATR(20) BAND Volatility-Acceleration Filter on RS Momentum Pullback (3 次嘗試均失敗)

**目標**：直接回應 TSM-017 AI_CONTEXT 列出之未驗證方向 (d) Volatility-Acceleration BAND filter，將 CIBR-014 / FXI-014 / URA-013 之 ATR(5)/ATR(20) BAND 過濾器跨策略移植至 TSM RS Momentum Pullback 框架。**Repo 首次 ATR ratio BAND 變體於 RS Momentum 框架**（既有成功案例皆為 MR 框架）。

### 設計理念

TSM-011 Att3 baseline 殘餘 Part B SLs（2024-07-16 / 2024-10-30）在 5d ceiling 維度均通過 +10.5% 限制（5d ret 分別 +0.7% / -3.4%），需另一個正交維度區分。CIBR-014 Att2 確認 ATR(5)/ATR(20) BAND ∈ (1.15, 1.40] 在 BB lower hybrid MR 框架成功（+37% min Sharpe），其結構假設為「健康 capitulation 訊號 ATR ratio 應位於 in-crash 加速與慢磨無動能之間」。TSM-018 試驗此假設於 RS Momentum 框架。

### 進場條件（沿用 TSM-011 Att3 + 新增第 5 條）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 相對強度 | TSM 20日報酬 - SMH 20日報酬 ≥ 5% | 板塊內超額表現 |
| 2 | 短期回調 | 5日高點回撤 3-7% | 暫時整理 |
| 3 | 趨勢確認 | Close > SMA(50) | 上升趨勢 |
| 4 | 5d return CEILING | 訊號日 5 日報酬 ≤ +10.5% | rally exhaustion 過濾 |
| **5** | **ATR(5)/ATR(20) BAND** | **(atr_ratio_floor, atr_ratio_ceiling]** | **vol-acceleration 雙向限制** |
| 冷卻 | 訊號間隔 | ≥ 10 交易日 | 避免重複訊號 |

### 三次迭代結果

| 指標 | TSM-011 Att3 (baseline) | Att1 (1.15, 1.40] | Att2 (1.00, 1.20] | Att3 (0.50, 1.10] |
|------|-------------------------|-------------------|-------------------|-------------------|
| **Part A Sharpe** | 0.86 | **-0.03** (-104%) | 0.65 (-24%) | 0.65 (-24%) |
| **Part B Sharpe** | 0.83 | 0.83 (=) | 0.27 (-67%) | **0.98** (+18%) |
| **min(A,B)** | **0.83** | -0.03 REJECT | 0.27 REJECT | 0.65 REJECT |
| Part A 訊號數 | 12 | 6 | 4 | 6 |
| Part B 訊號數 | 10 | 5 | 5 | 6 |
| Part A WR | 83.3% | 50.0% | 75.0% | 66.7% |
| Part B WR | 80.0% | 80.0% | 60.0% | 83.3% |

**所有三次迭代 min(A,B) < baseline 0.83**，Att3 為三次最佳但仍 REJECT。

### Att1 REJECT 分析（CIBR-014 直接移植 (1.15, 1.40]）

BAND 過嚴切除 6 個 Part A 訊號（12 → 6），cooldown chain shift（lesson #19）引入 3 個新 SLs：2021-01-22 / 2022-01-13 / 2023-01-24（macro shock 拉回，ATR ratio 處於 (1.15, 1.40] 中段）。Part A WR 從 83.3% 崩至 50.0%，Sharpe 0.86 → -0.03（-104%）。Part B Sharpe 維持 0.83 但訊號數 10 → 5，cum +59.78% → +26.40%（-56%）。

### Att2 REJECT 分析（放寬至 (1.00, 1.20] RS 訊號典型範圍）

放寬下限至 1.00 + 收緊上限至 1.20：
- Part A 從 12 → 4，winners 流失嚴重
- Part B 從 10 → 5，但 chain shift 將原 baseline 兩個 SLs（2024-07-16 / 2024-10-30）替換為 2024-07-08 / 2024-11-01 兩個新 SLs，淨效果 SLs 數量未減反增
- Part B WR 從 80.0% 崩至 60.0%，Sharpe 0.83 → 0.27（-67%）

### Att3 REJECT 分析（CEILING-only floor=0.50 非綁定 + ceiling=1.10）

最佳結果但仍 REJECT：
- Part A 6 訊號 / WR 66.7% / Sharpe 0.65 / cum +24.63%（vs baseline 0.86 / +74.10%，-24% Sharpe / -67% cum）
- Part B 6 訊號 / WR 83.3% / Sharpe **0.98** / cum +36.52%（**+18% Sharpe vs baseline**）
- A/B 累計差 |24.63 - 36.52| / 36.52 = **32.6% > 30% target ❌**
- A/B 訊號比 1.0:1.0（gap 0% << 50% ✓）

CEILING 1.10 過濾「in-crash 加速」訊號（ATR ratio > 1.10），保留「orderly low-vol pullback」訊號。Part B 受惠（過濾 2024-10-30 SL ATR ratio 1.15+），但 Part A 大量 winners ATR ratio 亦 > 1.10（半導體個股回調本質伴隨適度 vol expansion），被誤殺。

### 核心失敗發現（lesson #15 family v3 cross-strategy 邊界擴展）

1. **Repo 首次 ATR ratio BAND 於 RS Momentum 框架失敗**——既有成功案例 CIBR-014 / FXI-014 / URA-013 皆為 MR 框架（capitulation 訊號日 ATR 結構性高 1.15+），TSM RS Momentum Pullback 訊號日為「上升趨勢中淺回檔」，ATR ratio 集中於 1.0-1.15 較窄帶，BAND 無區分力。
2. **Part A/B SLs 在 ATR ratio 維度反向**：
   - Part A SLs（2021-01 / 2022-01 / 2023-01 macro shock 拉回）ATR ratio 高（>1.15）
   - Part B SLs（2024-07-16 / 2024-10-30 earnings/macro pullback）ATR ratio 1.10-1.20 中段
   - **單一 BAND 結構性無法雙 Part 同步改善**——同 TSM-013/014/015/016/017 失敗模式平行
3. **lesson #19 cooldown chain shift 在 RS Momentum + ATR BAND 組合下結構性放大反向選擇**——Att2 過濾 baseline 兩個 Part B SLs 但 chain shift 引入兩個新 SLs，淨效果零改善
4. **新跨資產規則（lesson #15 v3）**：ATR ratio BAND 適用邊界 = 「target 訊號日 ATR ratio 分布跨足兩極端 + winners/SLs 在 BAND 維度單向對齊」雙條件。MR 框架 ✓（capitulation entry 自然產生高 ATR ratio）；RS Momentum 框架 ✗（pullback entry ATR 集中窄帶 + Part A/B SLs 反向）

### 結論

TSM-018 三次迭代全部 REJECT，Att3 為三次最佳（min 0.65）但仍 < baseline 0.83。**TSM Part B 0.83 binding constraint 第 6 次結構性無解確認**（TSM-013/014/015/016/017/018 共六次嘗試）。TSM-011 Att3 仍為 min(A,B) 全域最優（18 次實驗、54+ 次嘗試）。

未來方向（更新 2026-05-09）：
- (a) **SOXX 半導體指數 anchor**（注意 TSM 為成分股自我參考性需謹慎）
- (b) **Multi-customer ensemble** (AAPL + MSFT + NVDA voting)
- (c) **完全替代 framework**（lesson #22 multi-week regime + RS Momentum 組合）
- (d) **Volume-normalized z-score** (vs absolute ratio threshold) 解決 A/B regime asymmetry

已驗證無效並從候選清單剔除：
- ~~Volatility-Acceleration BAND (ATR ratio)~~（TSM-018 三次失敗）
- ~~earnings-date exclusion filter~~（TSM-017 三次失敗）
- ~~Volume Confirmation Filter~~（TSM-012 三次失敗）
- ~~Cross-Asset Divergence (QQQ/AAPL anchor)~~（TSM-013/014/015 三次失敗）
- ~~BB-Width Regime Gate~~（TSM-016 PARTIAL 但 A/B cum gap 違反）

---

## TSM-019: VIX Term-Structure (^VIX3M / ^VIX) Regime Gate on RS Momentum Pullback (3 次嘗試 Att2 PARTIAL)

**目標**：直接回應 TSM-018 AI_CONTEXT 列出之未驗證方向，將 forward-looking implied vol term structure（^VIX3M / ^VIX 比率）作為 regime gate 加入 TSM-011 Att3 RS Momentum Pullback + 5d ceiling 框架。**Repo 首次 VIX term structure 維度於任何資產**——既有 lesson #24 family v1-v8 維度均為 implied vol LEVEL（^VIX/^MOVE/^GVZ/^OVX/^VXN）或 DIRECTION（X 日變化），尚未驗證 term structure 維度。

### 設計理念

VIX 為 30 天隱含波動率，VIX3M 為 3 個月隱含波動率。比率 > 1 代表 contango（市場對未來中期波動的期望高於近期，complacent calm regime），比率 < 1 代表 backwardation（短期波動高於中期，active panic peak）。歷史平均 ratio ~1.116，標準差 0.090，僅 8.7% 時間處於 backwardation。

**核心假設**：TSM RS Momentum Pullback 訊號於 deep contango regime（complacency mid-cycle）期間品質較差，因 pullback 容易延續為更大修正；而 mild contango / near-flat regime（panic 邊緣）的 pullback 更可能為健康整理。

**Trade-level 預分析**（TSM-011 baseline 22 訊號 VIX3M/VIX 分布）：
- Part A SLs：2022-11-21 ratio 1.106 / 2022-12-07 ratio 1.110（mid contango）
- Part B SLs：2024-07-16 ratio 1.130 / 2024-10-30 ratio 1.020（雙極端：deep contango + near-flat）
- Winners 跨整個 ratio 範圍 1.002-1.238（無單向集中）

### 進場條件（沿用 TSM-011 Att3 + 新增第 5 條）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 相對強度 | TSM 20日報酬 - SMH 20日報酬 ≥ 5% | 板塊內超額表現 |
| 2 | 短期回調 | 5日高點回撤 3-7% | 暫時整理 |
| 3 | 趨勢確認 | Close > SMA(50) | 上升趨勢 |
| 4 | 5d return CEILING | 訊號日 5 日報酬 ≤ +10.5% | rally exhaustion 過濾 |
| **5** | **VIX Term Structure** | **min_vix_term_ratio ≤ ^VIX3M/^VIX ≤ max_vix_term_ratio** | **forward-looking IV term structure regime gate** |
| 冷卻 | 訊號間隔 | ≥ 10 交易日 | 避免重複訊號 |

### 三次迭代結果

| 指標 | TSM-011 Att3 (baseline) | Att1 CEIL≤1.15 | Att2 ★ FLOOR≥1.115 | Att3 FLOOR≥1.10 |
|------|-------------------------|----------------|--------------------|------------------|
| **Part A Sharpe** | 0.86 | 0.42 (-51%) | **1.11 (+29%)** | 0.58 (-33%) |
| **Part B Sharpe** | 0.83 | 0.65 (-22%) | **0.83 (=)** | 0.42 (-49%) |
| **min(A,B)** | **0.83** | 0.42 REJECT | **0.83 TIE** | 0.42 REJECT |
| Part A 訊號數 | 12 | 6 | 9 | 11 |
| Part B 訊號數 | 10 | 8 | 5 | 6 |
| Part A WR | 83.3% | 66.7% | **88.9%** | 72.7% |
| Part B WR | 80.0% | 75.0% | 80.0% | 66.7% |
| Part A cum | +74.10% | +17.44% | **+60.65%** | +44.35% |
| Part B cum | +59.78% | +36.98% | +26.40% | +17.44% |
| Part A MDD | -7.89% | -7.89% | **-8.42%** | -7.89% |
| Part A max consec losses | 2 | 2 | 1 | **3** |
| A/B 累計差 | 19.3% | 53% | **56.5% > 30% ❌** | 61% |
| A/B 訊號比 | 1.2:1 | 1.33:1 | 1.39:1 | 1.83:1 |

**Att2 為三次最佳但僅 TIE baseline**，因 A/B 累計差超過 30% target。

### Att1 REJECT 分析（CEILING <= 1.15 lenient）

CEILING 1.15 過濾 deep contango regime（VIX3M/VIX > 1.15）。Trade-level：
- 過濾 Part A 7 winners（1.168/1.215/1.238/1.174/1.155/1.168/1.190 ratios）+ 0 SLs（兩 SLs 1.106/1.110 < 1.15 KEPT）
- Part B 過濾 2024-06-27 TP (1.178) + 2025-09-25 TP (1.162) 兩 winners + 0 SLs（1.130/1.020 < 1.15 KEPT）
- cooldown chain shift 將 2024-07-16 SL 替換為 2024-07-11 SL（淨 SL 不變但時間偏移）

**結構性錯誤方向**：CEILING 在 TSM 上 over-filter winners 而非 SLs，與 TSM-014 (QQQ CEILING +5%) 同樣失敗模式。

### Att2 ★ PARTIAL 分析（FLOOR >= 1.115，過濾 Part A SLs ratio 1.106/1.110）

**Part A 結構性突破**：
- 2 baseline SLs（2022-11-21 ratio 1.106 / 2022-12-07 ratio 1.110）皆 < 1.115 乾淨過濾 ✓
- 但 cooldown chain shift（lesson #19）引入 2022-11-28 新 SL（chain shift 中性化部分 selectivity，net SL 2→1 改善）
- 同時誤過濾 4 winners（2023-01-19 ratio 1.094 / 2023-10-20 ratio 1.034 / 2020-12-09 ratio 1.110 = 邊界 / 其他）
- Part A 12 → 9 訊號 (8 wins + 1 SL)，WR 83.3% → **88.9%**，Sharpe 0.86 → **1.11** (+29%)

**Part B 完全相同**（min binding constraint 不變）：
- 2024-07-16 SL ratio 1.130 > 1.115 結構性逃逸過濾 ❌
- 2024-10-30 SL ratio 1.020 過濾 ✓ 但 cooldown chain shift 引入 2024-12-27 TP 替換原 2024-12-19 TP
- Part B 10 → 5 訊號 (4 wins + 1 SL)，Sharpe 維持 0.83，cum +59.78% → +26.40%

**A/B 失衡惡化**：
- Part A 5 年期累計 +60.65% vs Part B 2 年期累計 +26.40%
- 絕對累計差 56.5% > 30% target ❌
- 年化 cum 12.13%/yr vs 13.20%/yr → gap **8.1% < 30% ✓**（年化達標但絕對差稀釋失衡）

### Att3 REJECT 分析（FLOOR >= 1.10 lenient ablation）

放寬 FLOOR 至 1.10：
- Part A SLs（1.106 / 1.110）皆 > 1.10 KEPT ❌（1.10 對 SLs 非綁定）
- 同時切除 Part A 1 winner (1.094) + Part B 數個 winners
- cooldown chain shift 引入 3 連 SLs（max consec losses 3）
- min(A,B) 0.42（-49% vs baseline）

確認 1.115 為 sweet spot（filter Part A 兩 SLs 必要邊界）。

### 跨資產發現（lesson #24 family v9 邊界擴展）

1. **Repo 首次 VIX term structure (^VIX3M / ^VIX) 維度於任何資產**——既有 lesson #24 family v1-v8 維度為 implied vol LEVEL（^VIX/^MOVE/^GVZ/^OVX/^VXN）或 DIRECTION（X 日變化），尚未驗證 term structure（^VIX3M vs ^VIX）。
2. **TSM Part A vs Part B SLs 在 VIX3M/VIX 維度結構性反向**：
   - Part A SLs（mid contango 1.106 / 1.110）—— FLOOR 方向有效
   - Part B SLs（雙極端 1.020 + 1.130）—— FLOOR 僅解 1.020 SL，1.130 SL 結構性逃逸
   - 與 TSM-013/014/015/016/017/018 失敗模式平行
3. **新跨資產規則（lesson #24 family v9 邊界）**：VIX term structure (^VIX3M / ^VIX) 適用邊界 = 「target SLs 在 term structure 維度為**單向集中分布**（單側極端 contango 或 backwardation）」+「Part A 與 Part B SLs 同向對齊」雙條件。TSM 違反兩條件——SLs 跨 ratio 1.020-1.130 廣泛分布且 Part A/B 反向，term structure 維度結構性無區分力。
4. **「regime gate 對小 sample 策略」共通邊界再次驗證**——TSM-016 (BB-Width regime) Att2 雙 Part 100% WR std=0 + A/B cum gap 41% > 30% ❌；TSM-019 Att2 Part A 突破 + Part B 不變 + A/B cum gap 56.5% > 30% ❌。當基底框架已將 sample 壓低（baseline 12+10），regime gate 進一步切除使絕對累計差難維持 < 30%（年化 cum 與絕對 cum 評估標準的結構性差異）。

### 結論

TSM-019 三次迭代 Att1/Att3 REJECT、Att2 PARTIAL（Part A 突破 +29% Sharpe + 100% WR baseline level，但 Part B 完全不變 + A/B 累計差違反目標）。**TSM Part B 0.83 binding constraint 第 7 次結構性無解確認**（TSM-013/014/015/016/017/018/019 共七次嘗試）。TSM-011 Att3 仍為 min(A,B) 全域最優（19 次實驗、57+ 次嘗試）。

未來方向（更新 2026-05-09）：
- (a) **SOXX 半導體指數 anchor**（注意 TSM 為成分股自我參考性需謹慎）
- (b) **Multi-customer ensemble** (AAPL + MSFT + NVDA voting)
- (c) **完全替代 framework**（lesson #22 multi-week regime + RS Momentum 組合 / BB Squeeze Breakout / MR）
- (d) **Volume-normalized z-score** (rolling z-score 替代 absolute ratio threshold) 解決 A/B regime asymmetry

已驗證無效並從候選清單剔除：
- ~~VIX Term-Structure Regime Gate (^VIX3M / ^VIX)~~（TSM-019 三次嘗試 Att2 PARTIAL TIE baseline 但 A/B cum gap 違反）
- ~~Volatility-Acceleration BAND (ATR ratio)~~（TSM-018 三次失敗）
- ~~earnings-date exclusion filter~~（TSM-017 三次失敗）
- ~~Volume Confirmation Filter~~（TSM-012 三次失敗）
- ~~Cross-Asset Divergence (QQQ/AAPL anchor)~~（TSM-013/014/015 三次失敗）
- ~~BB-Width Regime Gate~~（TSM-016 PARTIAL 但 A/B cum gap 違反）
- ~~Sector-internal anchor (SOXX)~~（TSM-020 三次嘗試 Att1 PARTIAL TIE baseline 但 A/B cum/signal gap 雙違反）

TSM 第 19 次實驗、57+ 次嘗試。

TSM 第 18 次實驗、54+ 次嘗試。

---

## TSM-020: TSM-SOXX Cross-Asset Divergence CEILING Regime-Gated RS Momentum Pullback (3 次嘗試全部 REJECT/TIE)

**目標**：直接回應 TSM-019 AI_CONTEXT 列出之未驗證方向 (a) SOXX 半導體指數 anchor，將 sector-internal divergence regime gate 加入 TSM-011 Att3 RS Momentum Pullback + 5d ceiling 框架。**Repo 首次「sector-internal anchor」變體於任何資產**——既有 cross-asset divergence regime gate anchor 類別五大類已驗證：(a) broad-market benchmark（QQQ/SPY/EEM）、(b) 主要客戶 single-stock（AAPL）、(c) 同類資產對等（EFA-EEM）、(d) sub-component anchor（FXI vs EEM）；TSM-020 加入 (e) sector-ETF anchor（SOXX vs single-stock TSM）為新類別。

### 設計理念

SOXX iShares Semiconductor ETF 為 TSM ~9% 權重的 sector ETF（vs SMH ~12% 權重作為 entry RS trigger / QQQ TSM ~0% 直接權重 broad-market anchor / AAPL 主要客戶 anchor）。SOXX 較 SMH 為更分散的半導體 sector 籃（top 10 holdings ~60% 權重 vs SMH ~75%），預期提供「TSM vs 半導體 sector internal positioning」維度。

**核心假設**：當 TSM 過去 20 日報酬顯著超越 SOXX，TSM 已脫離 broad semi-sector regime 進入 stock-specific rally exhaustion 狀態，RS momentum 訊號品質下降。

**Trade-level 預分析**（TSM-011 baseline 22 訊號 TSM-SOXX 20d_div 分布）：
- TSM-SMH RS ≥ +5% entry condition 結構性使 TSM-SOXX 20d_div 必然 > +5%（SMH TSM ~12% > SOXX ~9% 權重，SMH 對 TSM 漲幅吸收較多 → TSM-SMH < TSM-SOXX 自然關係）
- 訊號分布大致集中於 [+5%, +15%] 區間
- Part B SLs（2024-07-16, 2024-11-04）TSM-SOXX 20d_div < +10% 落於 winners 分布中段

### 進場條件（沿用 TSM-011 Att3 + 新增第 6 條）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 相對強度 | TSM 20日報酬 - SMH 20日報酬 ≥ 5% | 板塊內超額表現 |
| 2 | 短期回調 | 5日高點回撤 3-7% | 暫時整理 |
| 3 | 趨勢確認 | Close > SMA(50) | 上升趨勢 |
| 4 | 5d return CEILING | 訊號日 5 日報酬 ≤ +10.5% | rally exhaustion 過濾 |
| **6** | **TSM-SOXX divergence CEILING** | **TSM 20日 - SOXX 20日 ≤ max_relative_return_soxx** | **sector-internal rally exhaustion regime gate** |
| 冷卻 | 訊號間隔 | ≥ 10 交易日 | 避免重複訊號 |

### 三次迭代結果

| 指標 | TSM-011 Att3 (baseline) | Att1 CEIL≤+0.10 | Att2 CEIL≤+0.05 | Att3 CEIL≤+0.07 |
|------|-------------------------|------------------|------------------|------------------|
| **Part A Sharpe** | 0.86 | **1.23 (+43%)** | 0.00 (over-filter) | 1.06 (+23%) |
| **Part B Sharpe** | 0.83 | **0.83 (=)** | 0.06 (-93%) | 0.83 (=) |
| **min(A,B)** | **0.83** | **0.83 TIE** | 0.06 REJECT | **0.83 TIE** |
| Part A 訊號數 | 12 | 8 | **0 (結構性過濾)** | 4 |
| Part B 訊號數 | 10 | 10 | 2 | 5 |
| Part A WR | 83.3% | **87.5%** | n/a | 75.0% |
| Part B WR | 80.0% | 80.0% | 50.0% | 80.0% |
| Part A cum | +74.10% | +59.23% | n/a | +21.83% |
| Part B cum | +59.78% | +59.78% | +0.34% | +26.40% |
| Part A MDD | -7.89% | -7.79% | n/a | -6.73% |
| A/B 年化 cum gap | 19.3% | **55% > 30% ❌** | n/a | **67% > 30% ❌** |
| A/B 年化訊號比 | 1.2:1 | 0.32:1 (gap 68% ❌) | n/a | 0.32:1 (gap 68% ❌) |

**Att1 為三次中最佳結構但僅 TIE baseline**，A/B 累計差與訊號比雙違反。

### Att1 PARTIAL 分析（CEILING ≤ +0.10）

- Part A 從 12 訊號過濾至 8（移除 4 訊號），WR 83.3% → 87.5%（+4.2pp），Sharpe 0.86 → **1.23**（+43% 改善）
- Part B 完全 unchanged：所有 10 訊號 TSM-SOXX 20d_div < +10% 通過 ceiling
- Part B 殘餘 2 SLs（2024-07-16 / 2024-11-04）TSM-SOXX 20d_div 落於 winners 分布中段，CEILING +10% 對 Part B 完全非綁定
- A/B 年化 cum 差 55%（vs baseline 19.3%）違反 30% target；A/B 年化訊號比 0.32:1 違反 50% target
- **與 TSM-013 Att1 (QQQ +15%) 結構性平行**：repo 第 4 次「Part A breakthrough but Part B unchanged」失敗模式（TSM-013 / TSM-016 / TSM-019 / TSM-020）

### Att2 REJECT 分析（CEILING ≤ +0.05）

- Part A 0 訊號 — TSM-SMH RS ≥ +5% entry condition 結構性使 TSM-SOXX 20d_div 必然 > +5%（SMH TSM ~12% > SOXX ~9% 權重，SMH 對 TSM 漲幅吸收較多）
- +5% 為結構性下界，CEILING +5% 與 entry RS condition 互斥
- Part B 2 訊號 1W/1L Sharpe 0.06（cooldown chain shift 引入新 trade pattern）

### Att3 REJECT 分析（CEILING ≤ +0.07）

- Part A 訊號 12→4（過嚴流失 8 訊號 cum -71%），但 Sharpe 1.06 局部改善
- Part B 訊號 10→5（-50%），Sharpe 0.83 unchanged（5 訊號縮放後比例保持）
- A/B 年化 cum gap 67% 與訊號比 gap 68% 雙違反 acceptance criteria
- **+7% 為 sweet spot 探尋失敗確認**：[+5%, +10%] 區間內 SLs 與 winners 在 TSM-SOXX 維度結構性重疊，無單一 threshold 可選擇性過濾 SLs

### 核心失敗發現（lesson #20 v3 family v11 邊界擴展，repo 首次 sector-internal anchor 變體）

1. **Repo 首次「sector-internal anchor」變體於任何資產**——cross-asset divergence regime gate anchor 五大類驗證完整：broad-market（QQQ/SPY/EEM）、major-customer（AAPL）、broad-vs-broad（EFA）、broad-vs-sub-component（EEM-FXI）、**sub-component-vs-sector（TSM-SOXX）**
2. **TSM-SOXX 維度與 entry RS condition 結構性耦合**——TSM-SMH RS ≥ +5% entry condition 結構性使 TSM-SOXX 20d_div 必然 > +5%，sweet spot 區間 [+7%, +10%] 為結構性窄帶，但於該區間 SLs 與 winners 重疊
3. **Part B 2024-07-16 / 2024-11-04 SLs 在 TSM-SOXX 20d_div 維度落於 winners 分布中段**——repo 第 8 次確認 TSM Part B SLs 在「single dimension cross-asset divergence」結構性與 winners 重疊（跨 8 維度 QQQ/QQQ-BAND/AAPL/BB-Width/earnings/ATR-BAND/VIX-term-structure/SOXX 結構性無解）
4. **新跨資產規則（lesson #20 v3 family v11 邊界）**：sector-ETF anchor 適用邊界 = 「target stock 為非 sector ETF 大權重成分股（target weight in anchor < 5%）」+「Part A/B SLs 在 sector divergence 維度單向對齊」雙條件；TSM ~9% 權重 SOXX 雖自我參考稀釋程度可接受，但 SLs 在維度內無區分力，違反第二條件
5. **TSM Part B 0.83 binding constraint 第 8 次結構性無解確認**——TSM-013/014/015/016/017/018/019/020 共 8 次嘗試確認 TSM 為 Sharpe-1.0 結構性難突破資產

### 候選未驗證方向（剩餘三項）

- (a) **Multi-customer ensemble** (AAPL + MSFT + NVDA voting) — 多客戶 anchor stack，需 anchor 維度兩兩具獨立 selectivity
- (b) **完全替代 framework**（BB Squeeze Breakout / MR / lesson #22 multi-week regime + RS Momentum 組合）— 跳脫 RS Momentum Pullback 結構
- (c) **Volume-normalized z-score** (rolling z-score 替代 absolute ratio threshold) — 解決 A/B regime asymmetry

TSM 第 20 次實驗、60+ 次嘗試。

