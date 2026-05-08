<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取
  last_validated: 2026-05-08
  data_through: 2025-12-31
  note_2026_05_08_nvda021: NVDA-021 added 2026-05-08 (NVDA-QQQ 20d Cross-Asset Divergence CEILING Regime-Gated MBPC, **repo 首次 cross-asset divergence regime gate（CEILING 方向）成功移植至高波動 AI mega-cap 個股 + MBPC 框架（雙重邊界擴展）**, cross-strategy port from INDA-012 / EWZ-009 (CEILING in MR framework) + cross-asset port from TSLA-017 (FLOOR direction in BB Squeeze framework)). Three iterations, **Att2 SUCCESS — repo 首次突破 NVDA 結構性 Sharpe 0.55 ceiling 至 1.43，新全域最優**: Att1 (max_relative_return=+0.05 寬鬆 ceiling) Part A 15/80.0%/Sharpe **0.82** cum +101.64% / Part B 5/80.0%/Sharpe **1.99** cum +35.99% / min(A,B) **0.82** (**+49% vs NVDA-013 Att3 baseline 0.55**) — A/B 平衡完美：年化 cum 差 9.3% < 30% ✓ (大幅優於 baseline 26.4%)、年化訊號比 1.2:1 < 50% ✓；Filter 過濾 11 Part A 訊號（含 5+ NVDA 過度跑贏 QQQ 的 rally exhaustion SLs：2021-02-18 / 2021-04-21 / 2022-04-04 / 2023-07-25 等），WR 73.1%→80.0%（+6.9pp 品質提升）；Att2 ★ (max_relative_return=+0.03 中度 ceiling) Part A 10/**90.0%**/Sharpe **1.43** cum +85.63% / Part B 5/80.0%/Sharpe 1.99 cum +35.99% (與 Att1 相同) / min(A,B) **1.43** (**+74% vs Att1 0.82, +160% vs NVDA-013 baseline 0.55**) — 額外過濾 5 Part A 訊號（含 2 SLs：2020-10-20 + 2023-08-28），Part A SLs 從 3→1（唯一殘留 2019-02-20 為 NVDA-QQQ 邊緣 < +3%）；A/B 年化 cum 差 20.5% < 30% ✓、年化訊號比 0.8:1 < 50% ✓；NVDA Part A WR 歷史新高 90.0%；Att3 (max_relative_return=+0.01 過嚴 ceiling) Part A 9/88.9%/Sharpe **1.33** cum +71.88% / Part B 3/100% std=0 zero-var Sharpe 0.00 cum +25.97% / min(A,B)† **1.33** (-7% vs Att2)—— +1% 過濾 1 Part A winner（2020-06-15）+ 2 Part B 訊號（2025-08-20 expiry +0.04% / 2025-10-13 winner），Part B 訊號密度 1.5/yr（vs baseline 3.5/yr，-57%）統計顯著性不足；唯一殘留 2019-02-20 Part A SL 結構性處於 +1% 之下，無單一 divergence threshold 可清除。**核心結論（lesson #19/#26 family v2 邊界精煉）**: (1) **Repo 首次 cross-asset divergence regime gate（CEILING 方向）成功移植至高波動 AI mega-cap 個股 + MBPC 框架**——既有成功案例：TLT-014 (TLT-SPY 20d FLOOR, 利率 vs 股票 MR) / TSLA-017 (TSLA-QQQ 20d FLOOR, 高波動 AI 個股 vs 大盤 BB Squeeze) / INDA-012 (INDA-EEM 60d CEILING, 單一國家 vs 大盤 EM MR) / EWZ-009 (EWZ-EEM 10d CEILING, 商品國 EM vs 大盤 EM MR)；NVDA-021 為**雙重邊界擴展首次成功**：(a) CEILING 方向首次於 MBPC（動量延續）框架（先前 INDA-012/EWZ-009 皆於 MR 框架）；(b) CEILING 方向首次於高波動 AI 個股類別（先前 TSLA-017 為 FLOOR）；(2) **NVDA 結構性 Sharpe 0.55 ceiling 首次突破（13+ 次實驗 / 53+ 次嘗試後）**——突破來源：cross-asset relative performance 維度為 NVDA-013 雙重 SMA/ATR regime gate 飽和後的**下一個獨立選擇維度**；(3) **NVDA-QQQ vs NVDA-SMH anchor 選擇**：QQQ（NVDA ~5-12% 權重）較 SMH（NVDA ~20% 權重）為更獨立 anchor，提供更乾淨的 NVDA-specific rally exhaustion 訊號；NVDA-014/016 已驗證 NVDA-SMH 為 entry-trigger 與 confirmation 維度皆有侷限，QQQ 為新有效 anchor；(4) **Threshold sweet spot**：+5%（Att1）→ min 0.82 / +3%（Att2 ★）→ min 1.43 / +1%（Att3）→ min 1.33；+3% 為 NVDA 20d NVDA-QQQ rally exhaustion 結構性甜蜜點；(5) **CEILING vs FLOOR 方向選擇規則（lesson #19/#26 family v2）**：CEILING 適用「individual asset rally exhaustion vs broader benchmark」結構（個股過度跑贏大盤、單一國家 ETF 過度跑贏區域 ETF）；FLOOR 適用「individual asset weakness vs broader benchmark」結構（利率資產 reflation regime SL、單一個股 event-driven sell-off）；方向選擇依資產 SLs 在 divergence 維度的單向結構決定。**新跨資產假設（待驗證）**：CEILING 方向可能適用其他 mega-cap 個股 + 動量延續框架（TSLA / GOOGL / META / AMZN vs QQQ），閾值需依資產 vs benchmark 的 vol/leadership 結構調整。NVDA-021 Att2 為新全域最優（21 次實驗、52+ 次嘗試），取代 NVDA-013 Att3 為當前最佳。
  note_2026_05_08_nvda: NVDA-020 added 2026-05-08 (Volatility-Acceleration Band Filter on Multi-Week Regime-Aware MBPC, **repo 首次 ATR(5)/ATR(20) BAND filter 跨策略類型移植至 momentum / breakout-continuation 框架（先前 CIBR-014 / FXI-014 皆於 capitulation MR 框架成功）**, cross-strategy port from CIBR-014 Att2 / FXI-014 Att2). Three iterations all FAILED vs NVDA-013 Att3 min 0.55, **REJECT ATR ratio BAND 跨策略移植於 MBPC 框架**: Att1 (BAND ∈ (0.85, 1.20] CIBR-014/FXI-014 直接移植) Part A 20/70.0%/Sharpe **0.46** cum +78.94% / Part B 6/83.3%/Sharpe 2.22 cum +46.87% / min **0.46** (-16% vs baseline 0.55) — BAND 過濾移除 6 訊號（26→20）：5 winners + 1 loser **反向選擇**（中段 (0.85, 1.20] 比率區間並非 NVDA MBPC 高品質訊號區，與 CIBR/FXI capitulation MR 框架預期相反）；Att2 (CEILING-only ≤ 1.05) Part A 19/63.2%/Sharpe **0.32** cum +47.10% / Part B 6/100%/std=0 Sharpe 6.98 cum +54.44% / min **0.32** (-42% vs baseline) — 移除 7 Part A 訊號**全部為 winners**（7 wins / 0 losses 高品質區），由此推斷 ATR(5)/ATR(20) > 1.05 區間 = **100% WR 高品質**，與 capitulation MR 預期方向**完全相反**——NVDA MBPC entry-day 高 ATR 加速反映 momentum continuation 強度而非 panic spike；Att3 (FLOOR-only > 1.00, 反向 require vol acceleration) Part A 15/73.3%/Sharpe **0.54** cum +64.73% / Part B 4/75.0%/Sharpe 1.72 cum +25.92% / min **0.54** (-2% 邊際劣化) — Floor > 1.00 過濾 11 訊號但 WR 73.3% 與 baseline 73.1% 幾乎不變（filter 並未選擇性移除 losers）；Part B 訊號從 7→4 過稀疏（年化 2/yr）。**核心結論（lesson #20b 失敗家族再擴展 / lesson #24 family v10 邊界）**：(1) **lesson #24 family ATR ratio BAND filter 適用邊界精煉**——CIBR-014（min 4.08，+733%）/ FXI-014（min 1.27，+135%）兩次成功皆於 capitulation MR + BB 下軌混合進場框架，NVDA-020 證明跨策略移植至 MBPC（momentum continuation）框架**結構性失敗**；(2) **失敗結構性原因**：capitulation MR 訊號日（BB 下軌 + 深回檔 + WR ≤ -80）—— ATR 高比率反映 panic spike，BAND ceiling 區隔「panic 完成 / 仍在加速」；MBPC 動量延續訊號日（Donchian 新高 + 淺回檔 + RSI 中性 + 多頭 K 棒）—— ATR 比率反映 breakout-day momentum 強度（**方向相反**）；(3) **新跨策略規則候選**：ATR(5)/ATR(20) BAND filter 適用條件 = 「signal-day vol structure 與 panic spike 一致」——MR / capitulation 框架成立，momentum / breakout-continuation 框架反向；(4) **NVDA-013 vs NVDA-020 vol regime 維度差異**：NVDA-013 ATR(20)/ATR(60) ≤ 1.40 為**多週期** vol regime classifier（成功），NVDA-020 ATR(5)/ATR(20) 為**入場日**短期波動加速度（失敗）——MBPC 框架的 vol regime 維度只在「中週期」尺度有效，「日內加速」對 momentum SL/winner 不具區分力；(5) **NVDA 結構性 Sharpe 上限 ~0.55 第五次確認**（NVDA-016 / NVDA-017 / NVDA-018 / NVDA-019 / NVDA-020 連續五次失敗），entry-side cross-strategy port 飽和。NVDA-013 Att3 維持全域最優（20 次實驗、49+ 次嘗試）。NVDA 第 20 次失敗策略類型（**ATR(5)/ATR(20) BAND filter on MBPC** 加入失敗清單）。
  note_2026_05_07_nvda: NVDA-019 added 2026-05-07 (Failed Breakdown Reversal MR, **repo 首次 Failed Breakdown Reversal 作為 MR 主訊號於高 vol mega-cap 個股**, cross-asset extension from FXI-009 prior FBR failure). Three iterations all FAILED vs NVDA-013 Att3 min 0.55, **REJECT FBR-MR 跨資產移植於高 vol AI 個股**: Att1 (baseline FBR Donchian 20d + breakdown lookback 5d + Close>Open + SMA(20)≥1.00×SMA(60) + ATR(20)≤1.40×ATR(60) + cd10, TP+6%/SL-5%/15d) Part A 15/60.0%/Sharpe **0.28** cum +22.38% (6 SL: 2019-04-29 Q1 earnings / 2019-05-14 trade war / 2019-08-07 yuan deval / 2022-01-06 Fed pivot / 2022-04-13 bear / 2022-12-23 hawkish Fed) / Part B 7/57.1%/Sharpe **0.22** cum +7.76% (3 SL: 2024-04-10 Apr corr / 2024-07-22 yen carry / 2024-08-06 yen unwind, 1-5d 速 SL) / min **0.22** (-60% vs baseline 0.55) — SMA + ATR regime gate 無法分辨「事件驅動單日 V-bounce」與「持續下跌中的 dead-cat bounce」；Att2 (+ breakdown depth >= 5% + 收緊 ATR regime 至 1.30) Part A 11/45.5%/Sharpe **-0.01** cum -2.49% / Part B 6/**0.0%**/Sharpe 0.00 cum **-27.14%** / min **-0.01** — **反直覺發現**：要求更深 breakdown depth (≥5%) 反而**反向選擇 winners**——NVDA 高 vol 個股的 5%+ 深度跌破多發生於真實 bear regime 中段而非單日 V-bounce 後反轉，Att2 移除 Att1 全部 4 winners + 引入 3 新 losers，雙向災難；Att3 (還原 Att1 baseline + 加入「Close > 昨日 High」強勢突破確認) Part A 13/61.5%/Sharpe **0.31** cum +21.71% / Part B 6/**0.0%**/Sharpe 0.00 cum **-27.14%** / min **0.00** — **再次反直覺**：legitimate V-bounces 為漸進式收盤（不一定突破前日 High），dead-cat bounces 因爆發式買盤反而當日突破前日 High 但隔日續跌；Close>PrevHigh filter 系統性過濾真實反彈、保留假反彈。**核心結論（lesson #20a 失敗家族擴展）**: (1) **repo 第 1 次 Failed Breakdown Reversal 應用於高 vol mega-cap 個股 + MR 框架**：先前 FXI-009 為政策驅動 EM ETF 失敗，NVDA-019 擴展失敗清單至「高 vol single stock + MR primary entry」，雙重邊界擴展同時失敗；(2) **訊號定義不可行於高 vol**：NVDA Donchian Lower 在持續下跌中持續下移，每天都可 trigger「Low ≤ Donchian Lower」+「Close > Donchian Lower」+「Close > Open」陽線條件，FBR 訊號**幾乎無篩選力**；(3) **Signal-day filter 維度反向選擇邊界（lesson #19 family v13）**：depth filter (Att2 5%) + prev-high filter (Att3) 皆**反向選擇 winners**——高 vol 個股 false breakdowns 與 true bottoms 在 signal-day 層面行為相似，但跨多天的軌跡不同，single-day filter 無法分辨；(4) **NVDA signal-day filter 三次失敗整合**：NVDA-011（capitulation depth）+ NVDA-017（5d return ceiling）+ NVDA-019（FBR depth + close>PrevH）— lesson #19 family 在 NVDA 高 vol 結構**完全失效**；(5) NVDA 結構性 Sharpe 上限 ~0.55 第四次確認（NVDA-016 / NVDA-017 / NVDA-018 / NVDA-019 連續四次失敗），entry-side exploration 飽和，後續嘗試應集中於 (a) exit optimization、(b) ATR ratio BAND（CIBR-014 路徑）、(c) macro context confirmation 進一步精煉。NVDA-013 Att3 維持全域最優（19 次實驗、46+ 次嘗試）。NVDA 第 19 次失敗策略類型（含均值回歸、突破、動量回調、相對強度、RS 出場/參數探索、MBPC、ADX/DMI、Capitulation-Depth Filter、Multi-Week Regime BB Squeeze、Multi-Week Regime MBPC、負向 RS Pairs MR、Multi-Week Regime RS Momentum、Sector-Health Confirmed MBPC、Signal-Day 5d Return Ceiling MBPC、^VXN Forward-Looking IV Regime Gate MBPC、**Failed Breakdown Reversal MR** 十九大方向）。
  note_2026_05_06_nvda: NVDA-018 added 2026-05-06 (^VXN Forward-Looking Implied-Vol DIRECTION Regime-Gated MBPC, **repo 第 5 次 lesson #24 forward-looking IV regime gate 跨資產驗證 — 首次失敗案例 / 首次驗證於 mega-cap 個股 / 首次驗證於 MBPC 框架**, cross-asset port from TLT-013 / XLU-013 / GLD-015 / USO-025). Three iterations all FAILED vs NVDA-013 Att3 min 0.55, **REJECT lesson #24 forward-looking IV 跨資產假設於 mega-cap 個股 + MBPC 框架雙重邊界**: Att1 (DIRECTION 3d cap <= +5.0, XLU/USO sweet spot port) Part A 25/72.0%/Sharpe **0.52** cum +121.80% / Part B 7/85.7%/Sharpe 2.44 cum +58.62% (不變) / min **0.52** (-5.5% vs baseline 0.55) — +5.0 過濾僅 1 訊號 2023-03-13 SVB 銀行危機日（VXN 3d +5.31，**winner TP +8%**），0 SLs 過濾，因 NVDA Part A 7 SLs 的 VXN 3d_chg 全部 ≤ +2.31（4/7 為負）；Att2 (DIRECTION 10d cap <= 0.0, longer window tighter) Part A 19/57.9%/Sharpe **0.17** cum +20.18% / Part B 3/100% std=0 zero-var / min **0.17** (-69%) — 嚴重 over-filter，移除 7 baseline trades 中 6 為 TPs，WR 73.1%→57.9%，cooldown chain shift 引入新 SLs；Part B AI bull regime 中 VXN 持續下降使 7→3 訊號崩減；Att3 (LEVEL cap VXN <= 25, lesson #24 v1 mirror TLT-013) Part A 16/68.8%/Sharpe **0.41** cum +50.08% / Part B 6/83.3%/Sharpe 2.22 cum +46.87% / min **0.41** (-25%) — LEVEL cap 過濾 10 Part A 訊號（7 為 TPs 包括 2020 Q2-Q3 post-COVID 大量 high-VXN winners），NVDA MBPC 在 high VXN regime 反而 WR 較高（77% vs 67%）。**核心結論（lesson #24 邊界擴展 + lesson #6 NVDA boundary 第三次確認）**: (1) **Repo 第 5 次 lesson #24 跨資產驗證 — 首次失敗案例**：先前 4 次成功（TLT-013 ^MOVE LEVEL +17% / XLU-013 ^MOVE 3d DIRECTION +112% / GLD-015 ^GVZ 10d DIRECTION +55% / USO-025 ^OVX 3d DIRECTION +58%）皆於 single-driver-IV asset + MR 框架，NVDA-018 為首次驗證於 mega-cap 個股 + MBPC 框架，雙重邊界擴展同時失敗；(2) **失敗根因（雙重邊界）**：(a) Asset 維度——^VXN 為 NASDAQ-100 100 檔成份股 IV 加權平均，NVDA 雖為主要權值但**單股失敗模式（earnings、guidance、competitive shocks）與 macro NASDAQ IV 弱相關**，^MOVE/^OVX/^GVZ 對 TLT/USO/GLD 為 single-driver IV，^VXN 對 NVDA 為間接經由整個 NASDAQ-100 中介；(b) Strategy 維度——MR 進場期待「IV stress 結束 + 價格反彈」（IV 上升 → 過濾合理），MBPC 進場期待「突破後淺回檔 + 趨勢延續」（**IV 與訊號日 forward-looking 預期相關性弱**，突破延續訊號的成敗由動量持續性決定）；(3) **新跨資產規則候選（lesson #24 v3 boundary）**：forward-looking IV regime gate 適用條件 = single-driver IV asset (rates/oil/gold/broad equity) + capitulation MR framework；違反任一條件結構性失效；(4) NVDA 結構性 Sharpe 上限 ~0.55 第三次確認（NVDA-016 broad-market gate 失敗 + NVDA-017 rally exhaustion ceiling 失敗 + NVDA-018 forward-looking IV 失敗，累積 18 次實驗 + 56+ 次嘗試）。NVDA-013 Att3 維持全域最優（18 次實驗、56+ 次嘗試）。NVDA 第 18 次失敗策略類型（含均值回歸、突破、動量回調、相對強度、RS 出場/參數探索、MBPC、ADX/DMI、Capitulation-Depth Filter、Multi-Week Regime BB Squeeze、Multi-Week Regime MBPC、負向 RS Pairs MR、Multi-Week Regime RS Momentum、Sector-Health Confirmed MBPC、Signal-Day 5d Return Ceiling MBPC、**^VXN Forward-Looking IV Regime Gate MBPC** 十八大方向）。NVDA-017 added 2026-05-05 (Signal-Day 5d Return CEILING on Multi-Week Regime-Aware MBPC, **repo 首次 TSM-011 lesson #19 family v10/v12 「rally exhaustion 5d ceiling」假設跨資產移植至 MBPC 框架**, cross-asset port from TSM-011 Att3 RS Momentum framework). Three iterations all FAILED vs NVDA-013 Att3 min 0.55, **REJECT 跨資產假設於高波動 AI 個股 + MBPC 框架**. Att1 (ret_5d_max=0.045 預測甜蜜點 surgical) Part A 25/72.0%/Sharpe **0.52** cum +121.80% / Part B 7/85.7%/Sharpe 2.44 cum +58.62%（不變）/ min **0.52**（-5.5% vs baseline 0.55）— **lesson #19 cooldown chain shift 失敗**：5d ceiling 4.5% 過濾 2019-02-20 SL（5d +4.88%）但釋放原本被 cooldown 壓抑的 2019-03-01 raw signal（5d -1.62%，未被 ceiling 過濾），fires 後 4 trading days SL（-7.14%）+ 反向 lock-out 2019-03-08 TP（+8.00%），淨效應 = 0 SL 改善 + 1 TP 損失，cum -17.74pp；Att2 (ret_5d_max=0.040 更嚴 ceiling) Part A 25/72.0%/Sharpe **0.52** cum +121.80%（**與 Att1 完全相同**）/ Part B 不變 / min **0.52** — **second-order cooldown chain shift**：4.0% 額外過濾 2020-06-15 TP（5d +4.1880%）但 unleash 2020-06-29 raw signal（亦為 +8.00% TP），1-for-1 TP 替換淨效應為 0；同時保留 Att1 之 2019 SL chain shift 副作用，確認 [0.040, 0.045] 為「robust sweet spot of failure」；Att3 (ret_5d_max=0.050 ablation 寬鬆) Part A 26/73.1%/Sharpe **0.55** cum +139.54% / Part B 不變 / min **0.55**（與 NVDA-013 baseline 完全相同）— max SL 5d = +4.88% < 0.050，ceiling 非綁定確認 5d ceiling 只在 [0.0420, 0.0488] 區間 binding 且該區間結構性破壞 baseline。**核心結論（lesson #19 family 邊界擴展 + lesson #6 NVDA boundary）**：(1) **TSM-011 跨資產假設邊界**：lesson #19 family v10/v12 「rally exhaustion CEILING」於 RS Momentum 框架（TSM-008）成功，**結構性失敗於高波動多 regime AI 個股 + MBPC 框架**——TSM-008 RS 訊號日 5d 分布廣（max SL +11.30%）可 surgical 過濾，NVDA-013 MBPC 訊號日 5d 分布窄（max SL +4.88% / max TP +4.19%，gap 0.69%）filter 區間極窄；(2) **Cooldown chain shift 第 1 次出現於 momentum CEILING 框架**：先前 chain shift 案例多為 MR FLOOR 過濾（DIA-012 / GLD-014 等），方向「過濾 cap 後釋放更深 floor」；NVDA-017 為 CEILING 方向「過濾單 SL 後釋放鄰近 raw SL，再 lock-out 後續 TP」，失敗模式對稱於 MR floor chain shift；(3) **Heterogeneous SL 結構為 signal-day filter 適用邊界**：NVDA-013 7 個 Part A SLs 在 1d/3d/5d/10d/20d/VXN/ATR 等 9 個維度上分布廣泛重疊，無單一維度 surgical 切點。signal-day return ceiling 適用條件需 asset 殘餘 SLs **集中於單一失敗模式**（TSM「post-rally exhaustion」/ FCX「3d 急漲」/ URA「5d 持續下挫」），對 multi-regime heterogeneous SLs 結構（NVDA-013）系統性失效；(4) **NVDA 結構性 Sharpe 上限 ~0.55 第三次確認**：NVDA-016（broad-market context confirmation gate）+ NVDA-017（rally exhaustion ceiling）+ NVDA-015（lesson #22 RS port）均失敗，累積 17 次實驗 + 53+ 次嘗試後 NVDA min(A,B) 0.55 為現有純技術面 + signal-day filter + cross-asset macro gate 三重維度結構性上限。NVDA-013 Att3 維持全域最優（17 次實驗、53+ 次嘗試）。NVDA 第 17 次失敗策略類型（含均值回歸、突破、動量回調、相對強度、RS 出場/參數探索、MBPC、ADX/DMI、Capitulation-Depth Filter、Multi-Week Regime BB Squeeze、Multi-Week Regime MBPC、負向 RS Pairs MR、Multi-Week Regime RS Momentum、Sector-Health Confirmed MBPC、**Signal-Day 5d Return Ceiling MBPC** 十七大方向）。NVDA-016 added 2026-05-05 (Sector-Health Confirmed Multi-Week Regime-Aware MBPC, **repo 第 4 次 broad-market context confirmation gate 跨資產驗證、首次 mirror inversion 應用於 MBPC 動量延續框架 + 首次於高波動 AI 個股**, cross-strategy port from IWM-015 lesson #25 family). Three iterations all FAIL strict acceptance criteria vs NVDA-013 Att3 min 0.55, **Att3 PARTIAL Sharpe 改善但 A/B cum gap 失格**: Att1 (SMH 10d return >= 0% 嚴格 sector uptrend) Part A 19/68.4%/Sharpe **0.41** cum +62.56% / Part B 4/75.0%/Sharpe 1.72 cum +25.92% / min **0.41** (vs baseline 0.55, -25%) — SMH 10d 為平滑指標無法分辨 SLs（NVDA Part A 7 SLs 中僅 1 筆 SMH 10d < 0%，6 筆發生於 SMH uptrend 期間），同時誤殺 6 baseline TPs（2019-03-08 / 2019-12-03 / 2020-01-27 / 2021-08-12 / 2022-12-07 / 2023-03-13 / 2023-04-21）+ cooldown chain shift 引入新 SLs；Att2 (SMH 10d >= -5% 寬鬆) Part A/B 訊號集與 NVDA-013 baseline 完全相同 — baseline 全部 33 訊號 SMH 10d >= -5%（最深僅 -3.74% 為 2019-12-03 TP），閾值在此區間結構性非綁定。SMH 10d 維度無有效 sector-weakness 過濾邊界；Att3 (SMH 5d return >= 0% 短週期嚴格 sector 健康) Part A 9 訊號 WR **77.8%** Sharpe **0.62** cum +37.31% (filtered 5/7 baseline SLs + 12/19 baseline TPs/expiries) / Part B 3 訊號 WR **100%** Sharpe 0.00 std=0 zero-var cum +25.97% (3/3 TPs all hit) / min(A,B)† **0.62** (Part A binding, Part B std=0 沿用 EWJ-003/SPY-009/DIA-012/IWM-013/IBIT-009 慣例; **+12.7% Sharpe vs NVDA-013 Att3 0.55**). **A/B 平衡部分達成**: Part A 年化 cum 6.55%/yr vs Part B 12.23%/yr → cum gap **46.4% > 30% ❌**（baseline 26.4%）— SMH 5d >= 0% 過濾後 Part A 訊號崩減 26→9，絕對累計報酬下降 73%，雖 risk-adjusted 改善但 absolute return 大幅縮減；訊號比 1.8/yr vs 1.5/yr = 16.7% gap < 50% ✓。Threshold sweep（SMH 5d >= -5%/-2%/-0.5%/0%/+0.5%）顯示 0% 為甜蜜點。**核心結論（lesson #25 family v6 邊界擴展）**: (1) lesson #25 broad-market context confirmation gate **不適用於 MBPC 動量延續框架 + 高波動 AI 個股**——失敗根因為 NVDA Part A SLs 在 SMH 5d/10d 維度分布**雙向發散**（5d -2.72% ~ +2.27%、10d -1.56% ~ +6.09%），NVDA 個股事件驅動 SLs（earnings drift、ATH reversal、tech selloff）與 sector context 解耦；(2) **lesson #25 失敗清單擴展**：IWM-015 ✓（broad cap-segment ETF + MR）/ XBI-016 ✗（biotech sector ETF）/ COPX-013 ✗（mining sector ETF）/ NVDA-016 ✗（高波動 AI 個股 + MBPC）— 適用條件精煉為「broad cap-segment ETF + MR/dip-buying 框架」；(3) **mirror inversion 假設失敗**：MR 需 macro 同步衰弱（IWM-015 successful direction）vs 動量延續需 macro 同步健康（NVDA-016 inverted direction）— 後者於高波動 AI 個股結構性失敗，sector uptrend 期反而是個股反轉風險最高時段（lesson #5 邊界鏡像版本）；(4) repo 第 4 次 broad-market context confirmation 嘗試結果：1 success / 3 failure，預期成功類別需嚴格滿足 broad cap-segment ETF + MR framework 雙條件；(5) NVDA 結構性 Sharpe 上限 ~0.55 再度確認，未來突破方向應脫離 single-day filter / cross-asset macro gate 框架，可探索 ^VXN BANDS regime gate（XBI-017 跨資產移植）/ NVDA earnings calendar 季節性過濾。NVDA-013 Att3 維持全域最優（16 次實驗、49+ 次嘗試）。NVDA-015 added 2026-05-04 (Multi-Week Regime-Aware Relative Strength Momentum Pullback, **repo 第 1 次 lesson #22 cross-strategy 移植至 RS Momentum 框架 — 全部失敗**, cross-strategy port from NVDA-013 Att3 雙重 regime gate 至 NVDA-006 RS Momentum). Three iterations all failed vs NVDA-013 Att3 min 0.55. Att1 (k_trend=1.00 strict, vol regime disabled) Part A 33/63.6%/Sharpe **0.37** cum +117.18% / Part B 11/81.8%/Sharpe **0.90** cum +72.37% / min **0.37** (vs NVDA-006 baseline 0.47 退化 -21%, vs NVDA-013 0.55 -33%) — k=1.00 過濾 2 訊號（35→33）但 Part A Sharpe 反退（NVDA Part A 11 SLs 集中 2021 H2 泡沫期，當時 SMA20 仍 > SMA60，SMA regime 對該批 SL 結構性無選擇性）；Att2 (k_trend=0.97 buffered, vol regime disabled) **完全與 Att1 相同**（Part A 33/0.37, Part B 11/0.90, min 0.37）—— **核心發現**：RS 框架 signal-day SMA20/SMA60 ratio 全部 >= 1.00，無訊號落於 (0.97, 1.00) transition zone。**lesson #22 邊界精煉**：RS Momentum 進場條件「NVDA 20d - SMH 20d return >= 5%」**已隱含 NVDA uptrend regime**——20 日 outperformance 幾乎不可能在 SMA20 < SMA60 bear regime 出現，lesson #22 multi-week SMA regime gate 對 RS Momentum 框架**結構性非綁定**；Att3 (k_trend=0.97 + ATR(20) <= 1.40 × ATR(60) vol regime 啟用，NVDA-013 Att3 sweet spot) Part A 28/67.9%/Sharpe **0.48** cum +132.53% (Part A WR +4.3pp, Sharpe +0.11 vs Att1) / Part B 10/90.0%/Sharpe **1.43** cum +85.63% (Part B WR +8.2pp) / min **0.48** (+2% vs NVDA-006 0.47 微幅改善, **-13% vs NVDA-013 Att3 0.55 未達突破目標**) — A/B 訊號比 5.6/yr vs 5.0/yr = 1.12:1 (gap 11% < 50% ✓) / A/B 年化 cum 18.3%/yr vs 36.5%/yr, gap 49.9% > 30% ❌ (Part B 純 AI 牛市結構性不對稱)。**核心跨資產 / 跨策略結論**：(1) **lesson #22 適用框架精煉**：BB Squeeze (TSLA-015/NVDA-012/FCX-013/COPX-011) ✓、MBPC (NVDA-013) ✓、Pullback MR (XBI-015) ✓、**RS Momentum (NVDA-015) ✗ 結構性冗餘**（RS 進場條件已隱含 uptrend regime）。lesson #22 適用框架的判別準則為「進場條件是否隱含趨勢方向」——隱含 trend 的 entry framework（RS 動量、配對 RS 過濾）regime gate 結構性冗餘。(2) **NVDA-013 Att3 ATR vol regime 跨策略移植部分有效**：對 RS 框架提供 +0.11 Sharpe 改善（0.37→0.48）但無法突破 NVDA-013 0.55——RS 框架 Part A 殘餘 SLs 多為 2021 末段 non-ATR-expansion 高位淺回檔後續跌。(3) **NVDA RS framework 結構性飽和**：NVDA-014（負向 RS pairs MR）+ NVDA-015（lesson #22 + ATR vol regime）兩次 RS framework 子方向 cross-strategy port 均失敗。NVDA-013 Att3 維持全域最優（15 次實驗、46+ 次嘗試）。NVDA 第 15 次失敗策略類型（含均值回歸、突破、動量回調、相對強度、RS 出場/參數探索、MBPC、ADX/DMI、Capitulation-Depth Filter、Multi-Week Regime BB Squeeze、Multi-Week Regime MBPC、負向 RS Pairs MR、**Multi-Week Regime RS Momentum** 十五大方向）。NVDA-014 added 2026-05-02 (Negative Relative Strength Pairs Mean Reversion vs SMH, **repo 首次以負向相對強度作為主訊號的均值回歸實驗**, cross-direction inverse of NVDA-006 positive-RS momentum continuation). Three iterations all failed vs NVDA-013 Att3 min 0.55. Att1 (RS≤-3% + 10d Pullback≥6% + ATR(20)≤1.40×ATR(60) + cd 12, TP+6%/SL-6%/15d) Part A 32/65.6%/Sharpe **0.32** cum +70.84% / Part B 13/38.5%/Sharpe **-0.25** cum -19.39% / min **-0.25** — A/B 訊號比 1.0:1（gap 0% ✓）但 Part B 13 訊號中 8 筆 SL（多為 1-2 日內觸發 -6.14%），2024-2025 NVDA 多次深度修正（2024-08 -17%、2025-04 tariff -25%）觸發大量訊號但續跌；ATR vol gate 在訊號日 ATR 尚未完全擴張時無法過濾起始崩盤期。Att2 (Att1 + SMA(20)≥1.00×SMA(60) trend regime, lesson #22 移植) Part A 17/47.1%/Sharpe **-0.06** cum -9.08% / Part B 7/28.6%/Sharpe **-0.49** cum -18.15% / min **-0.49** — **lesson #5 失敗模式驗證**：「趨勢濾波器 + 均值回歸 = 災難」。負向 RS + 深回檔的訊號**本質上**伴隨 SMA(20)<SMA(60)（NVDA 跑輸 SMH 通常意味短中期均線下穿），SMA regime gate 過濾 high-quality 真實 MR 機會（Part A 32→17，移除 winners 多於 losers，WR 65.6%→47.1%）。Att3 (Att1 + RS≤-5% 收緊 + ClosePos≥0.40 盤中反彈確認, 去除 SMA gate) Part A 21/61.9%/Sharpe **0.29** cum +36.36% / Part B 6/66.7%/Sharpe **0.34** cum +11.22% / min **0.29**（vs NVDA-013 Att3 0.55 仍未達 Sharpe 目標）— A/B 平衡達標：訊號比 4.2/yr vs 3.0/yr = 1.40:1（gap 29% < 50% ✓）/ 累積年化 7.27%/yr vs 5.61%/yr（gap 23% < 30% ✓）/ Part B Sharpe 0.34 > Part A 0.29（無過擬合）；改善 vs Att1：min -0.25→0.29（+0.54），Part B Sharpe -0.25→0.34（轉正）；但 Part A Sharpe 0.32→0.29 略降（ClosePos 移除 Att1 部分淺回檔型 winners）。**核心跨資產 / 跨方向結論**：(1) **負向 RS 作為主訊號在 NVDA 失敗（repo 首次試驗）**：NVDA-006 已驗證**正向 RS** + 淺回檔（動量延續）為可行方向（min 0.47），但**負向 RS** + 深回檔（相對 MR）**結構性不對稱**——AI 主導的科技龍頭股「跑輸板塊」常為基本面/敘事惡化的領先信號，而非短期 mispricing。(2) **lesson #5 重新驗證於 pairs MR 框架**：「趨勢濾波器 + 均值回歸 = 災難」對「相對均值回歸」（pairs MR）同樣成立。(3) **lesson #22 適用方向性精煉**：buffered SMA regime gate 之適用性取決於進場框架方向——同向（trend-following / momentum）→ 提升品質；反向（mean reversion）→ 移除好訊號（lesson #5 重新驗證）。(4) **配對交易 repo 失敗清單擴展**：COPX-006 (COPX/FCX) / XBI-008 (XBI/IBB) / SIVR-009 (SIVR/GLD) / **NVDA-014 (NVDA/SMH)** 共 4 種結構皆失敗，僅在「同類同權重 + 正向 RS 作為過濾器」（NVDA-006、TSM-007、TSLA-007）有效。(5) NVDA 結構性 Sharpe 上限再度驗證：NVDA-013 Att3 min 0.55 維持全域最優。NVDA-014 為 NVDA 第 14 次失敗策略類型（repo 首次「負向 RS 主訊號」試驗，含均值回歸、突破、動量回調、相對強度、RS 出場/參數探索、MBPC、ADX/DMI、Capitulation-Depth Filter、Multi-Week Regime BB Squeeze、Multi-Week Regime MBPC、**負向 RS Pairs MR** 十四大方向）。NVDA-013 Att3 維持全域最優（14 次實驗、43+ 次嘗試）。NVDA-013 added 2026-04-28 (Multi-Week Regime-Aware Momentum Breakout Pullback Continuation, **repo 第 1 次 lesson #22 cross-strategy 移植：BB Squeeze → MBPC 框架**, cross-asset extension from NVDA-009 baseline + NVDA-012 lesson #22 regime gate). Three iterations, **Att3 SUCCESS — repo 首次 lesson #22 跨策略類型驗證 + 首次發現 vol regime 在非 BB Squeeze 框架非冗餘，新全域最優 min(A,B) 0.55**. Att1（k=0.97 NVDA-012 cross-strategy port）Part A 30/66.7%/Sharpe **0.38** cum +107.15% / Part B 8/75.0%/Sharpe **0.96** cum +47.30% / min **0.38**（vs NVDA-009 baseline 0.41 退化）—— k=0.97 對 NVDA-009 MBPC 訊號集（Part A 34）僅過濾 4 筆，Sharpe 退化由 cooldown chain shift（lesson #19）造成（過濾的 4 筆中僅 1 筆為 SL）；Part B 完全不變（k=0.97 對 2024-2025 AI bull regime 無綁定）。Att2（k=1.00 strict, FCX-013 direction）Part A 28/67.9%/Sharpe **0.41** cum +106.56% / Part B 不變 / min **0.41**（與 NVDA-009 baseline 持平，無改善）—— **核心發現**：lesson #22 buffered SMA regime gate 對 MBPC Part A SLs 缺乏選擇性，因 NVDA Part A 11 SLs 散佈於 2020 COVID（rapid recovery）/ 2021 late-bull（uptrend）/ 2022 bear（少數）/ 2023 chop（boundary cases），大部分 SL signal-day 仍 SMA20≥SMA60，與 BB Squeeze SLs 集中 bear regime 結構不同。**Att3 SUCCESS（k=1.00 strict + ATR vol regime ATR(20)≤1.40×ATR(60)）**：Part A **26/73.1%/Sharpe 0.55** cum +139.54%（+34% vs NVDA-009 baseline 0.41，WR +5.2pp 品質提升）/ Part B **7/85.7%/Sharpe 2.44** cum +58.62%（+154% vs baseline，ATR 規範閘門精準過濾 2024-03-15 SL -7.14%）/ min(A,B) **0.55**（+8% vs NVDA-012 Att2 全域最佳 0.51）。年化 A/B cum 差 26.4%（< 30% ✓）/ 訊號比 1.49:1（gap 33% < 50% ✓）—— 三項 acceptance criteria 全部達標。**核心發現（lesson #22 邊界精煉）**：(1) **vol regime 冗餘性取決於進場框架的隱含波動限制**：BB Squeeze 進場前置 BB Width ≤ 60d 30th pct = 近期低波動，vol regime 冗餘（TSLA-015 Att3 ablation 證實）；MBPC 進場（Donchian 新高+淺回檔+RSI 中性+多頭 K 棒）**不含波動限制**，vol regime 提供**獨立選擇力**；(2) **k 值需求差異跨策略**：BB Squeeze + lesson #22 NVDA k=0.97 為甜蜜點，MBPC + lesson #22 NVDA k=1.00 strict 為甜蜜點（vol regime 已主導，SMA regime 嚴格度需求降低）；(3) **lesson #22 cross-strategy 首次擴展至 MBPC**：先前 TSLA-015 / NVDA-012 / FCX-013 三次成功皆於 BB Squeeze 框架，NVDA-013 證明 buffered multi-week SMA regime gate 對「動量延續類型」策略亦有效（但需搭配 vol regime 才達 +34% improvement）；(4) **NVDA 結構性 Sharpe 上限再度突破**：NVDA-004/006 0.47 → NVDA-012 0.51 → **NVDA-013 0.55**（13 次實驗、40+ 次嘗試）。NVDA-013 Att3 為新全域最優。NVDA-012 added 2026-04-26 (Multi-Week Regime-Aware BB Squeeze Breakout，**repo 第 2 次 lesson #22 buffered multi-week SMA regime 跨資產驗證，繼 TSLA-015 後首次中波動 AI growth stock 試驗**——cross-asset port from TSLA-015 Att2 success，疊加 buffered SMA(20)≥k×SMA(60) trend regime 過濾於 NVDA-004 BB Squeeze Breakout 之上). Three iterations, **Att2 SUCCESS — repo 首次突破 NVDA 結構性 Sharpe 上限 ~0.47，新全域最優 min(A,B) 0.51**. Att1（k=1.00 嚴格 / 註：實際使用 k=0.99 直接移植 TSLA-015 lesson #22 的 sweet spot）Part A 16/75.0%/Sharpe **0.63** cum +83.17%（過濾 2022-07-20 SL bear regime，+26% vs NVDA-004 0.50）/ Part B 6/66.7%/Sharpe **0.41** cum +17.31%（過濾 2025-05-13 winner +8.00% 與 2025-12-23 -1.06% expiry，但淨損失 winner）/ min **0.41**（vs 0.47 baseline）—— 與 TSLA-015 Att1 平行的 transition winner cooldown-shift 失敗模式：2025-05-13 為 4 月 tariff selloff 後 transition 訊號，SMA20/SMA60 比率落於 0.97-0.99 之間，k=0.99 過濾誤殺。**Att2 SUCCESS（k=0.97，3% 緩衝放寬）**：Part A 16/75.0%/Sharpe **0.63** cum +83.17%（與 Att1 完全相同，2022-07-20 SL 仍被 k=0.97 過濾，bear regime ratio << 0.97）/ Part B 7/71.4%/Sharpe **0.51** cum +24.86%（恢復 2025-05-14 +6.43% expiry，2025-12-23 -1.06% loser 仍被過濾）/ min **0.51**（+9% vs 0.47 baseline）。年化 A/B cum 差 25.3% < 30% ✓ / 年化訊號比 1.09:1 < 1.5:1 ✓ —— **三項 acceptance criteria 全部達標**。Att3（k=0.98 敏感度邊界檢查）Part A 不變 / Part B 6/66.7%/Sharpe 0.41（與 Att1 完全相同）/ min 0.41 —— 0.97-0.98 為 NVDA 上 transition winner 的關鍵分界，0.97 為精準甜蜜點。**核心發現（lesson #22 跨資產精煉）**：(1) buffered multi-week SMA regime 在 NVDA BB Squeeze 框架成功（NVDA-012 為 NVDA 結構性 Sharpe 上限突破首例）；(2) **k 值非通用**——TSLA k=0.99（3.72% vol）、NVDA k=0.97（2.5-3% vol），AI growth stock 的 transition signals SMA20/SMA60 比率落於 0.97-0.99 區間，需更寬緩衝；(3) lesson #22 跨資產假設「multi-week SMA regime 對 BB Squeeze breakout 高波動單股有效」確認，但 k 值需依資產 transition signal 的 SMA 比率分布調整；(4) 過濾結構性精準：2022-07-20 bear regime SL（ratio << 0.97）+ 2025-12-23 marginal loser（ratio < 0.97）被過濾，2020-2023 大部分 winners + 2024-2025 AI bull winners 全保留。NVDA-012 為 NVDA 第 12 次實驗，**首次突破 0.47 結構性上限**，新全域最優（12 次實驗、37+ 次嘗試）。NVDA-011 added 2026-04-26 (Capitulation-Depth Filter MR (RSI Oscillator Depth)，**repo 第 5 次 capitulation-depth filter 嘗試，repo 首次 >3% vol 高波動單一個股測試**——cross-asset port from IWM-013 Att3 success 方向). Three iterations all failed vs NVDA-004/006 min(A,B) 0.47. Att1（vol-scaled IWM-011 framework：RSI(2)<10 + 2DD<=-4.5% + ClosePos>=40% + ATR(5)/ATR(20)>1.10 + cd 8 + TP+7%/SL-7%/15d）Part A **5/40.0%/Sharpe -0.21** cum -8.32%（2019-04-26 SL trade-war + 2020-01-27 TP pre-COVID + 2021-02-23 SL Feb tech corr + 2022-08-09 TP bear rally + 2022-09-01 SL Jackson Hole）/ Part B 2/100% std=0 Sharpe 0.00 cum +14.49%（2025-01-13 DeepSeek + 2025-09-02 mid-dip）/ min **-0.21** —— 1.0/yr 訊號密度過稀（IWM-011 為 2.0/yr），高波動 single stock multi-regime（trade war / COVID / 2021 bubble / 2022 bear / 2023 chop）使 vol-scaled framework 喪失選擇性。Att2（Att1 + 3d cap >= -6%，DIA-012/CIBR-012 cap 方向）Part A **2/50.0%/Sharpe -0.01** cum -0.64%（移除 2 SL + 1 TP，保留 2020-01-27 TP + 2021-02-23 sharp 1d SL）/ Part B 不變 / min **-0.01** —— 3d cap 移除深 3d continuation traps 但同時誤殺 2022-08-09 TP 深 3d capitulation reversal；殘留 2021-02-23 SL 為 sharp 1d 急跌（non-prior-3d-buildup），3d cap 無法捕獲。Att3（Att2 + 1d cap >= -4%，DIA-012 dual-dimension 跨資產移植）Part A **1/0.0%/Sharpe 0.00** cum -7.14%（僅保留 2021-02-23 SL，誤殺 2020-01-27 pre-COVID winner）/ Part B 不變 / min **0.00** —— **NVDA Part A 高品質 winner（2020-01-27 pre-COVID）的 1d 比 SL（2021-02-23）更深**，DIA-012 cap 方向結構**錯誤**：DIA Part A losers 集中深 1d gap-down（cap 過濾贏家有效），NVDA winners 為「真實 capitulation 深 1d gap-down」，與 IWM-013 Att1 失敗模式平行。**核心結論**：(1) vol-scaled IWM-011 MR framework 不適用 NVDA 高波動 single stock——1.0/yr 訊號密度不足、multi-regime 使框架隨機化，與 TSLA-014（3.72%）/ FCX-011（3% vol）Post-Cap MR 跨資產失敗模式平行；(2) DIA-012 cap 方向結構性不適用 NVDA——NVDA winners 集中深 1d gap-down，與 IWM、與 DIA 結構相反；(3) NVDA 結構性 Sharpe 上限 ~0.5 再度確認（NVDA-004 / NVDA-006 0.47）。**Lesson #19 family 邊界擴展**：(a) raw return cap 方向 vs oscillator depth 方向選擇取決於 winners/losers 的 raw return 分布——SL 集中深 1d/2d/3d → cap 有效（DIA、CIBR、SPY）；winner 集中深 1d/2d/3d → cap 失敗，需 oscillator 維度（IWM、NVDA）；訊號密度 < 1.5/yr → 兩種維度皆失敗（NVDA-011 confirmation）；(b) capitulation-depth filter 的 vol 上限介於 IWM 1.5-2%（成功）與 NVDA 3.26%（失敗）之間。NVDA-011 為 NVDA 第 11 次失敗策略類型（含均值回歸、突破、動量回調、相對強度、RS 出場/參數探索、MBPC、ADX/DMI、Capitulation-Depth Filter 九大方向）。NVDA-004 / NVDA-006 維持全域最優（11 次實驗、34+ 次嘗試）。NVDA-010 added 2026-04-25 (ADX-Filtered RSI(2) Mean Reversion, **repo 首次 ADX/DMI 作為主規範閘門試驗**，三次迭代全部失敗 vs NVDA-004/006 min(A,B) 0.47). Att1（ADX>=25 + +DI>-DI + RSI(2)<=15 + Pullback[-3%,-10%] + cd10 + TP+6%/SL-6%/15d）Part A 3/66.7%/Sharpe **0.26** cum +3.88% / Part B 1/0%/Sharpe **0.00** zero-var SL / min **0.00** —— 多重綁定過嚴僅 0.6 訊號/yr 統計不足；強趨勢中 RSI(2)<=15 罕見發生（持續下挫使 +DI<<-DI 必然違反方向過濾），交集結構性狹窄。Att2（放寬 ADX>=20 + RSI(2)<=20 + Pullback[-2%,-12%] + cd8）Part A 8/62.5%/Sharpe **0.22** cum +9.00% / Part B **1**/0%/Sharpe **0.00** / min **0.00** —— Part A 新增 5 中等品質訊號稀釋集中贏家（Sharpe 0.26→0.22）；Part B 仍卡在 1 訊號：NVDA 2024-2025 深度修正（2024-08 -17%、2025-04 tariff -25%）違反 (a) -12% pullback 上限、(b) Close>SMA(50) 規範閘門（深跌跌破 50 日 MA）、或 (c) +DI>-DI（DMI 快速崩盤期間翻轉 bear），結構不匹配 Part B 的 deep-capitulation 機會。Att3（移除 +DI>-DI + RSI(3)<=25 + Pullback to -15%）Part A 8/**37.5%/Sharpe -0.27** cum -13.24%（4 連續 SL！）/ Part B 2/**0%**/Sharpe **0.00** zero-var / min **-0.27**（三次最差）—— cooldown chain shift（lesson #19）：移除 +DI>-DI 釋放原本被壓制的 2020-02-24（pre-COVID drop）、2021-02-23（Feb 修正）、2021-12-06（post-COVID 反彈）、2022-12-20（bear 反彈）4 筆全 SL，+DI>-DI 提供真實品質過濾；Part B 2024-04-02 + 2025-08-20 皆 SL 為 continuation-decline 假反彈（lesson #20b 平行結構）。**核心結論**：(1) ADX>=25 強趨勢與 RSI(2)<=15 deep oversold 罕見共存（RSI 需持續下挫使 DMI 翻轉），Att1 訊號結構性稀疏；(2) ADX>=20 weak-trend 過於包容（納入震盪 2023 summer 使 MR 訊號隨機化）；(3) +DI>-DI 提供真實選擇性但與 Close>SMA(50) 大部分時間冗餘，移除觸發 cooldown-chain-shift；(4) 多重綁定 ADX+RSI+SMA+Pullback+Close>Open+Cooldown 高約束相關性，放寬一條件不會比例增長訊號。**Repo 首次 ADX/DMI 主過濾器試驗失敗**——擴展 lesson #6（確認指標邊際效益遞減）至 ADX/DMI 類別；擴展 lesson #20b 邊界：trend-strength oscillators（ADX）加入 RSI/CCI/Stoch/MACD hook divergence 作為多 regime 高波動個股的無效進場主過濾器。**NVDA 結構性 Sharpe 上限約 0.5**——2019-2023 多 regime 變異使單一參數集難以同時優化 Part A/B；NVDA-004（BB Squeeze）/ NVDA-006（RS）維持全域最優 0.47（10 次實驗、31+ 次嘗試）。NVDA-009 added 2026-04-24 (Momentum Breakout Pullback Continuation, **repo 第 2 次 MBPC 結構試驗，繼 FXI-012 後首次高波動個股測試**，三次迭代全部失敗). Att1 baseline（Donchian 20d 近 10 日內新高 + Close>SMA(50) + 5d 淺回檔 -3% ~ -8% + RSI(14) ∈ [40,65] + 多頭 K 棒 + cd10 + TP+8%/SL-7%/20d）Part A 34 訊號 WR 67.6% Sharpe **0.41** cum +142.32% / Part B 8 訊號 WR 75.0% Sharpe **0.96** cum +47.30% / min **0.41**（低於 NVDA-004 / NVDA-006 的 0.47）——A/B 年化訊號比 1.7:1（41% gap）、A/B 年化 cum 差 16.9%，**A/B 平衡目標達成但 Sharpe 目標未達**；Att2（+ SMA(200) regime 閘門 + RSI_max 65→60）Part A 21/66.7%/**0.38** / Part B 6/83.3%/**2.22** / min 0.38——**非選擇性過濾**（訊號 -38%/WR -0.9pp，移除贏家 9/5 比於整體 23/11 比方向錯誤），SMA(200) 過濾 2022-07-25 TP 贏家、RSI<60 過濾 AI 主升段健康續漲；Att3a（2DD cap >= -6%，CIBR-012 方向）與 Att1 完全相同（-6% 無綁定，NVDA 突破+淺回檔 2d 報酬典型 -3~-5%）；Att3b（2DD cap >= -4%）Part A 31/64.5%/**0.33** / Part B 8/62.5%/**0.49** / min **0.33**（三次最差）——-4% cap 與 5d 淺回檔範圍部分重疊且 cooldown-shift 引入新 SL。**核心發現**：Part B（2024-2025 AI 牛市）單邊 Sharpe 0.96 遠勝 NVDA-004 Part B 的 0.47，證明 MBPC 結構在純趨勢期極有效；但 Part A 2021-2023 混合 regime（late-bull + 2022 bear + 2023 summer chop）11 筆 SL 壓制 Sharpe 至 0.41。**repo 第 2 次 MBPC 失敗**（繼 FXI-012 後），失敗機制差異：FXI 為政策驅動假突破（Part A WR 42.3%），NVDA 為 bubble/correction late-cycle 突破（Part A WR 67.6% 已不錯但 Sharpe 受限於標準差）。**擴展 cross_asset_lesson #25**：Momentum Breakout Pullback Continuation 結構需**單一純上升 regime** 資產才穩定，**多 regime 資產**（FXI 政策驅動 / NVDA bubble+correction mixed）結構性劣化於 regime-specific 優化的 MR / 突破策略。NVDA-004 / NVDA-006 維持全域最優（9 次實驗、28+ 次嘗試）。
-->
## AI Agent 快速索引

**當前最佳：** ★ **NVDA-021 Att2**（NVDA-QQQ 20d Cross-Asset Divergence CEILING Regime-Gated MBPC：NVDA-013 Att3 完整框架 + **NVDA 20d 報酬 - QQQ 20d 報酬 ≤ +3.0%** cross-asset rally-exhaustion regime gate，TP +8%/SL -7%/20d/cd 10）★ **2026-05-08 新全域最優（21 次實驗、52+ 次嘗試）**
- Part A: 10 訊號 / WR **90.0%** / Sharpe **1.43** / 累計 +85.63%（vs NVDA-013 Att3 26/73.1%/0.55/+139.54%）
- Part B:  5 訊號 / WR 80.0% / Sharpe 1.99 / 累計 +35.99%（vs NVDA-013 Att3 7/85.7%/2.44/+58.62%）
- min(A,B) **1.43**（**+160% vs NVDA-013 Att3 baseline 0.55，repo 首次突破 NVDA 結構性 Sharpe 0.55 ceiling**）
- A/B 年化 cum 差 **20.5% < 30%** ✓（vs baseline 26.4%）
- A/B 年化訊號比 **0.8:1**（gap 25.0% < 50% ✓）
- **Repo 首次 cross-asset divergence regime gate（CEILING 方向）成功移植至高波動 AI mega-cap 個股 + MBPC 框架（雙重邊界擴展）**
- 風險：殘留 1 Part A SL（2019-02-20 NVDA-QQQ 邊緣 < +3%）無單一 divergence threshold 可清除

**前任最佳：** NVDA-013 Att3（Multi-Week Regime-Aware MBPC：NVDA-009 + SMA(20)≥1.00×SMA(60) strict trend regime + ATR(20)≤1.40×ATR(60) vol regime）— Part A Sharpe **0.55**/Part B Sharpe **2.44**/min(A,B) **0.55**（+8% vs NVDA-012 Att2 的 0.51，+34% vs NVDA-009 baseline 0.41）。**Repo 首次 lesson #22 cross-strategy 移植（BB Squeeze → MBPC）+ 首次發現 vol regime 在非 BB Squeeze 框架非冗餘**。年化 A/B cum 差 26.4%（< 30% ✓）/ 訊號比 1.49:1（gap 33% < 50% ✓）—— 已被 NVDA-021 Att2 超越
**前任最佳：** NVDA-012 Att2（Multi-Week Regime-Aware BB Squeeze Breakout：NVDA-004 + buffered SMA(20)≥0.97×SMA(60) regime 過濾）— Part A Sharpe 0.63/Part B Sharpe 0.51/min(A,B) **0.51**（+9% vs NVDA-004 的 0.47）。lesson #22 第二次跨資產驗證
**前任最佳：** NVDA-004（BB Squeeze Optimized，冷卻 10天，TP+8%/SL-7%/20天）— Part A Sharpe 0.50/Part B Sharpe 0.47，大幅超越 NVDA-003（0.40/0.47）
**互補策略：** NVDA-006（Relative Strength Momentum Pullback，NVDA-SMH RS≥5% + 5日回撤3-8% + SMA50）— Part A Sharpe 0.47/Part B Sharpe 0.64，min(A,B) 0.47 持平 NVDA-004，但 Part B OOS +36%，A/B 年化訊號比 1.17:1（極佳平衡）
**單邊 Part B 最佳（已驗證）：** NVDA-009 Att1（Momentum Breakout Pullback Continuation，Donchian 20d + 5d 淺回檔 -3~-8% + SMA(50) + RSI[40,65] + 多頭 K 棒 + cd10）— Part A Sharpe 0.41/Part B Sharpe **0.96**（+104% vs NVDA-004 Part B），但 Part A 0.41 < NVDA-004 的 0.50 使 min(A,B) 僅 0.41，**不可作為全域最優**，**但可作為純趨勢期補充策略**
**前任最佳：** NVDA-003（BB Squeeze Breakout，冷卻 15天）— Part A Sharpe 0.40/Part B Sharpe 0.47
**滾動窗口分析摘要：** NVDA-001 ✗✓（精準度突變 ΔWR 25.0pp，績效漸變，訊號極稀少統計可信度低）

**NVDA-004 vs NVDA-003 關鍵改善：**
- Part A Sharpe：0.40→0.50（+25%），Part B Sharpe：0.47→0.47（不變）
- 累計報酬：Part A +45.82%→+70.09%（+53%），Part B +25.36%→+25.36%（不變）
- PF：Part A 2.18→2.62（+20%），Part B 2.61→2.61（不變）
- A/B Sharpe 比：0.85:1→1.06:1（近乎完美平衡）
- 訊號數：Part A 15→17（+2 好訊號），Part B 8→8（不變）
- 關鍵：冷卻期 15→10 天在 Part A 捕捉 2 個額外好訊號，Part B 完全不受影響

**NVDA-006 相對強度動量回調（3 次嘗試，Att1 最佳）：**
- Att1（最佳）：RS≥5% + 5日回撤3-8% + SMA(50)，Part A 0.47/Part B 0.64，min(A,B) 0.47，35/12 訊號（7.0/6.0 per yr）
- Att2：RS≥5% + 5日回撤4-8%，Part A 0.41/Part B 0.34（pullback_min 提高過濾好訊號）
- Att3：RS≥7% + 5日回撤3-8%，Part A 0.45/Part B 0.29（RS 門檻過嚴）
- 相對強度方法（TSM-007 風格）在 NVDA 上成功驗證：min(A,B) 持平 NVDA-004，OOS 顯著更優

**NVDA-005 動量回調（3 次嘗試均未超越 NVDA-004）：**
- Att1：20日高點回撤 8-15% + RSI(5)<30 + SMA(50)，Part A Sharpe 0.34/Part B 0.06（本質為趨勢+均值回歸，lesson #5 驗證）
- Att2（最佳）：ROC(20)≥15% + 5日回撤 3-8% + SMA(50)，Part A 0.36/Part B 0.74（Part B 優異但 Part A 拖累 min(A,B)=0.36 < NVDA-004 的 0.47）
- Att3：ROC(20)≥20% + 5日回撤 3-8% + SMA(50) + 冷卻15天，Part A 0.38/Part B 6/6 全達標（Sharpe 0.00 因零方差）
- 動量回調在 2021 泡沫期產生過多假訊號（3 筆停損於 2021 H2），Part A 無法突破 0.38

**最新（NVDA-020）ATR(5)/ATR(20) BAND filter on MBPC — repo 首次 ATR ratio BAND filter 跨策略類型移植 momentum / breakout-continuation 框架，3 次嘗試全部失敗 REJECT：**
- Att1（BAND ∈ (0.85, 1.20] CIBR-014/FXI-014 直接移植）：Part A 20/70.0%/0.46 cum +78.94% / Part B 6/83.3%/2.22 / min **0.46**（-16% vs baseline 0.55）— BAND 移除 6 訊號中 5 為 winners（反向選擇）
- Att2（CEILING-only ≤ 1.05）：Part A 19/63.2%/0.32 cum +47.10% / Part B 6/100%/std=0 6.98 / min **0.32**（-42%）— 移除 7 訊號**全部為 winners**（ratio > 1.05 區間 = 100% WR），與 capitulation MR 框架預期方向**完全相反**
- Att3（FLOOR-only > 1.00 反向 require vol acceleration）：Part A 15/73.3%/0.54 cum +64.73% / Part B 4/75.0%/1.72 / min **0.54**（-2%）— Floor > 1.00 過濾 11 訊號但 WR 73.3% 與 baseline 73.1% 幾乎不變，filter 並未選擇性移除 losers；Part B 4/yr 過稀疏
- **核心結論（lesson #24 family v10 邊界 / lesson #20b 失敗家族再擴展）**：(a) **ATR(5)/ATR(20) BAND filter 適用邊界精煉**——CIBR-014/FXI-014 兩次成功皆於 capitulation MR + BB 下軌混合進場，NVDA-020 證明**跨策略移植至 MBPC（momentum continuation）結構性失敗**；(b) **失敗結構性原因**：MR 訊號日（panic spike）vs MBPC 訊號日（breakout-day momentum）—— ATR 比率方向相反；(c) **新跨策略規則候選**：ATR ratio BAND filter 適用條件 = 「signal-day vol structure 與 panic spike 一致」；(d) **NVDA-013 vs NVDA-020 vol regime 維度差異**：多週期（ATR(20)/ATR(60)）有效，**日內加速（ATR(5)/ATR(20)）對 momentum SL/winner 不具區分力**

**前一（NVDA-017）Signal-Day 5d Return CEILING on MBPC — repo 首次 TSM-011 lesson #19 family v10/v12「rally exhaustion ceiling」假設跨資產移植至 MBPC 框架，3 次嘗試全部失敗 REJECT：**
- Att1（ret_5d_max=0.045 預測甜蜜點 surgical）：Part A 25/72.0%/Sharpe **0.52** cum +121.80% / Part B 7/85.7%/Sharpe 2.44 cum +58.62% / min **0.52**（-5.5% vs baseline 0.55）— **lesson #19 cooldown chain shift 失敗**：5d ceiling 4.5% 過濾 2019-02-20 SL（5d +4.88%）但釋放 2019-03-01 raw signal（5d -1.62%，未被 ceiling 過濾）→ fires 後 4 trading days SL（-7.14%）+ 反向 lock-out 2019-03-08 TP（+8.00%），淨效應 = 0 SL 改善 + 1 TP 損失
- Att2（ret_5d_max=0.040 更嚴 ceiling）：**結果完全與 Att1 相同**（Part A 25/0.52, cum +121.80%）— second-order chain shift（4.0% 額外過濾 2020-06-15 TP 但 unleash 2020-06-29 +8.00% TP）1-for-1 替換淨 0；確認 [0.040, 0.045] 為「robust sweet spot of failure」
- Att3（ret_5d_max=0.050 ablation 寬鬆）：Part A 26/73.1%/Sharpe **0.55** cum +139.54% / Part B 不變 / min **0.55**（**與 NVDA-013 baseline 完全相同**）— max SL 5d = +4.88% < 0.050，ceiling 非綁定確認 5d ceiling 只在 [0.0420, 0.0488] binding 且該區間結構性破壞 baseline
- **核心結論（lesson #19 family 邊界擴展）**：(a) **TSM-011 跨資產假設邊界**：「rally exhaustion CEILING」於 RS Momentum 框架（TSM-008，5d 分布廣 max SL +11.30%）成功，**結構性失敗於高波動多 regime AI 個股 + MBPC 框架**（5d 分布窄 max SL +4.88% / max TP +4.19%，gap 0.69% filter 區間極窄）；(b) **Cooldown chain shift 第 1 次出現於 momentum CEILING 框架**——先前案例多為 MR FLOOR 過濾（DIA-012/GLD-014），失敗模式對稱；(c) **Heterogeneous SL 結構為 signal-day filter 適用邊界**：NVDA-013 7 個 Part A SLs 在 1d/3d/5d/10d/20d/VXN/ATR 9 維度上分布廣泛重疊，無單一維度 surgical 切點。signal-day return ceiling 適用條件需 asset 殘餘 SLs 集中於單一失敗模式
- **NVDA 結構性 Sharpe 上限 ~0.55 第三次確認**：NVDA-016/-015/-017 連三次失敗，累積 17 次實驗 + 53+ 次嘗試後 0.55 為現有純技術面 + signal-day filter + cross-asset macro gate 三重維度結構性上限。未來突破方向需脫離既有框架（^VXN BANDS regime gate / earnings calendar 季節性 / 多重 forward-looking implied vol 組合）

**前一（NVDA-016）Sector-Health Confirmed MBPC（SMH 板塊健康閘門）— repo 第 4 次 lesson #25 跨資產驗證、首次 MBPC mirror inversion，3 次嘗試 PARTIAL：**
- Att1（SMH 10d >= 0% 嚴格 sector uptrend）：Part A 19/68.4%/0.41 / Part B 4/75.0%/1.72 / min **0.41**（vs baseline 0.55, -25%）— SMH 10d 為平滑指標誤殺 6 TPs，僅 1/7 SLs 過濾，cooldown chain shift 引入新 SL
- Att2（SMH 10d >= -5% 寬鬆）：Part A/B 完全等於 NVDA-013 baseline — SMH 10d 維度結構性非綁定（baseline 全部 33 訊號 SMH 10d >= -5%）
- Att3（SMH 5d >= 0% 短週期嚴格）：Part A 9 訊號 WR **77.8%** / Sharpe **0.62** cum +37.31% / Part B 3/100%/std=0 cum +25.97% / min(A,B)† **0.62**（**+12.7% Sharpe vs baseline 0.55**）
- **A/B 平衡部分達成**：訊號比 1.8/yr vs 1.5/yr = 16.7% < 50% ✓；A/B 年化 cum 6.55%/yr vs 12.23%/yr → gap **46.4% > 30% ❌**（baseline 26.4%）— SMH 5d 過濾使 Part A 訊號 26→9 絕對累計報酬下降 73%
- **核心結論（lesson #25 family v6 邊界擴展）**：(a) lesson #25 broad-market context confirmation gate **不適用於 MBPC 動量延續框架 + 高波動 AI 個股**；(b) NVDA Part A SLs 在 SMH 5d/10d 雙向發散——NVDA 個股事件驅動 SLs（earnings/ATH/tech selloff）與 sector context 解耦；(c) **lesson #25 失敗清單擴展**：IWM-015 ✓（broad cap-segment ETF + MR）/ XBI-016 ✗ / COPX-013 ✗ / NVDA-016 ✗（高波動 AI 個股 + MBPC mirror inversion）；(d) mirror inversion 假設失敗——MR 需 macro 同步衰弱 vs 動量延續需 macro 同步健康，後者結構性失敗（sector uptrend 期反而是個股反轉風險最高時段，lesson #5 邊界鏡像版本）

**前一（NVDA-015）lesson #22 + ATR vol regime 跨策略移植至 RS Momentum 框架 — repo 首次，3 次嘗試全部失敗：**
- Att1（k_trend=1.00 strict, vol regime disabled, NVDA-013 MBPC 甜蜜點移植）：Part A 33/63.6%/0.37 / Part B 11/81.8%/0.90 / min **0.37**（vs NVDA-006 baseline 0.47 退化 -21%, vs NVDA-013 0.55 -33%）
- Att2（k_trend=0.97 buffered, vol regime disabled, NVDA-012 BB Squeeze 甜蜜點移植）：**結果完全與 Att1 相同**（Part A 33/0.37, Part B 11/0.90, min 0.37）—— **核心發現**：RS 框架 signal-day SMA20/SMA60 ratio 皆 >= 1.00，無訊號落於 (0.97, 1.00) transition zone。**lesson #22 對 RS Momentum 框架結構性非綁定**（RS 進場條件已隱含 uptrend regime）
- Att3（k_trend=0.97 + ATR(20)<=1.40×ATR(60) vol regime 啟用，NVDA-013 Att3 sweet spot 移植）：Part A 28/67.9%/0.48 / Part B 10/90.0%/1.43 / min **0.48**（+2% vs NVDA-006 0.47 微幅改善, **-13% vs NVDA-013 Att3 0.55 未達突破**）
- **核心結論**：(a) **lesson #22 SMA regime 對 RS Momentum 結構性冗餘**——RS 條件已隱含 uptrend；(b) ATR vol regime 跨策略部分有效但無法突破 NVDA-013 0.55；(c) NVDA RS framework 結構性飽和（NVDA-014 負向 RS + NVDA-015 lesson #22 兩次 RS sub-direction cross-strategy port 均失敗）
- **lesson #22 適用框架最新精煉**：適用 BB Squeeze / MBPC / Pullback MR；不適用 RS Momentum（進場條件隱含 uptrend）

**前一（NVDA-014）負向 RS Pairs MR — repo 首次試驗，3 次嘗試全部失敗：**
- Att1（RS≤-3% + 10d Pullback≥6% + ATR≤1.40 + cd 12，TP+6%/SL-6%/15d）：Part A 32/65.6%/0.32 / Part B 13/38.5%/-0.25 / min **-0.25**，Part B 8/13 SL（2024-2025 NVDA correction 續跌）
- Att2（Att1 + SMA(20)≥1.00×SMA(60) lesson #22）：Part A 17/47.1%/-0.06 / Part B 7/28.6%/-0.49 / min **-0.49**，**lesson #5 驗證**：負向 RS + 深回檔的訊號本質伴隨 SMA 下穿，SMA gate 過濾 winners 多於 losers
- Att3（Att1 + RS≤-5% 收緊 + ClosePos≥40% 盤中反彈，去 SMA gate）：Part A 21/61.9%/0.29 / Part B 6/66.7%/0.34 / min **0.29** vs NVDA-013 Att3 0.55（仍未達），但 A/B 平衡達標（cum gap 23%、訊號 1.40:1）
- **核心結論**：負向 RS 對 AI 主導科技龍頭股為「領先指標」非「mispricing」——「跑輸板塊」常為基本面/敘事惡化的領先信號（與 COPX/XBI/SIVR 配對交易失敗共同擴展 repo「pairs MR 主訊號」失敗清單至 4 種結構，僅「正向 RS 過濾器」方向有效於 NVDA-006/TSM-007/TSLA-007）

**已證明無效（禁止重複嘗試）：**
- **ATR(5)/ATR(20) BAND filter on MBPC（CIBR-014/FXI-014 跨策略移植）**：NVDA-020 三次嘗試 Att1 (0.85, 1.20] min 0.46 反向選擇 / Att2 ceiling ≤ 1.05 min 0.32 移除 7 winners / Att3 floor > 1.00 min 0.54 邊際劣化。ATR ratio BAND filter 適用邊界 = capitulation MR + BB 下軌混合進場框架，**結構性失敗於 momentum / breakout-continuation 框架**——MR 訊號日 panic spike vs MBPC 訊號日 breakout-day momentum 方向相反
- **Sector-Health Confirmed MBPC（SMH 板塊健康閘門 cross-asset）**：NVDA-016 三次嘗試 Att1（SMH 10d >= 0%）min 0.41 / Att2（SMH 10d >= -5%）非綁定 / Att3（SMH 5d >= 0%）Sharpe 0.62 改善但 A/B cum gap 46.4% 失格。lesson #25 broad-market context confirmation gate 不適用於 MBPC 動量延續框架 + 高波動 AI 個股；NVDA Part A SLs 與 SMH 5d/10d 維度雙向發散，個股事件驅動 SLs 與 sector context 解耦
- **lesson #22 + ATR vol regime 跨策略移植至 RS Momentum 框架**：NVDA-015 三次嘗試 min 0.37/0.37/0.48 均不及 NVDA-013 Att3 0.55；SMA regime gate 對 RS 框架結構性冗餘（RS 進場已隱含 uptrend），ATR vol regime 部分有效但無法突破
- **負向 RS pairs MR（NVDA/SMH）作為主訊號**：NVDA-014 三次嘗試 min 從 -0.25 / -0.49 / 0.29 均不及 NVDA-013 Att3 0.55；負向 RS 為續跌領先信號而非 mispricing
- 動量回調（ROC + 短期回撤 + SMA50）：Part A 最佳 0.38，2021 泡沫期假訊號過多（NVDA-005，3 次嘗試）
- 相對強度 RS≥7%：過嚴，Part B Sharpe 0.29（NVDA-006 Att3）
- 相對強度 pullback 4-8%：過濾好訊號，Part B Sharpe 0.34（NVDA-006 Att2）
- 三重條件極端超賣（DD≤-20% + RSI(10)<28 + SMA偏離≤-10%）：2022 熊市連續停損，Part A -27.86%
- 回撤範圍過濾 [-35%,-10%]（NVDA-002 Att1）：過濾掉好訊號，Part B 從 4→2 訊號，Sharpe 0.44→-0.01
- 均值回歸 TP +10%（NVDA-002 Att2）：一筆達 +8% 但未達 +10% 的交易翻轉為停損，Part A Sharpe -0.01
- SL -12% / 25天持倉（NVDA-002 Att3）：更大虧損抵銷救回交易，Part A Sharpe 0.14（vs 0.23）
- 突破 TP +10%（NVDA-003 Att2）：Part A 2 筆達 +8% 未達 +10% 交易翻轉為到期/停損，Sharpe 0.40→0.27
- 突破 SL -5%（NVDA-003 Att3）：SL 過緊，Part A WR 66.7%→53.3%，Sharpe 0.40→0.27
- 突破 SL -8%（NVDA-004 Att1）：虧損更大（-8.14% vs -7.14%）但未救回任何交易，Part B Sharpe 0.47→0.41
- SMA(20) 替代 SMA(50)（NVDA-004 Att3）：讓通 2022-06-02 熊市假突破，Part A 增加 1 筆停損，Sharpe 0.50→0.40
- TP +8% 是 NVDA 的硬上限（均值回歸和突破均驗證），SL -7% 是突破/RS 策略甜蜜點

**已掃描的參數空間：**
- 均值回歸進場：RSI(2)<5 + 2日跌幅≤-7%
- 均值回歸出場：TP+8%/SL-10%/15天（最佳均值回歸）、TP+10%/SL-10%/20天、TP+8%/SL-12%/25天
- 回撤範圍：[-35%, -10%] 60日回看（過濾好訊號）
- 突破進場：BB(20,2) 擠壓（60日 25th 百分位，5日內）+ Close > Upper BB + Close > SMA(50) / SMA(20)
- 突破出場：TP+8%/SL-7%/20天（最佳）、TP+10%/SL-7%/20天、TP+8%/SL-5%/20天、TP+8%/SL-8%/20天
- 冷卻期：10天（最佳）、15天
- 動量回調進場：ROC(20)≥15%/20% + 5日回撤 3-8% + SMA(50)，冷卻 10/15天
- 深度回調進場：20日高點回撤 8-15% + RSI(5)<30 + SMA(50)
- 相對強度進場：NVDA-SMH 20日報酬差 ≥5%/7% + 5日回撤 3-8%/4-8% + SMA(50)，冷卻 10天

**NVDA-007 RS 出場優化（3 次嘗試，全部失敗）：**
- Att1（TP+8%/SL-7%/25d）：Part A 0.44/Part B 0.64，min(A,B) 0.44（延長持倉無效，avg hold 僅 7.9d）
- Att2（TP+8%/SL-8%/20d）：Part A 0.40/Part B 0.57，min(A,B) 0.40（寬 SL 增加虧損幅度，WR 不變）
- Att3（TP+8%/SL-7%/15d）：Part A 0.46/Part B 0.70，min(A,B) 0.46（最接近但仍未超越 0.47）
- 結論：TSM-008 的出場優化方法不適用 NVDA，因 NVDA 交易解決速度快（avg 7d），Part A 的 11 筆 2021 泡沫期停損為結構性虧損

**NVDA-008 RS 參數探索（3 次嘗試，全部失敗）：**
- Att1（SMH 10日 RS≥3% + 3日回撤 2-6%）：Part A 0.48/Part B 0.17，min 0.17（短回看窗口太噪，Part B WR 僅 52.9%）
- Att2（SMH 40日 RS≥8% + 5日回撤 3-8%）：Part A 0.57/Part B 0.03，min 0.03（長回看嚴重過擬合 Part A AI 動量期）
- Att3（SPY 20日 RS≥8% + 5日回撤 3-8%）：Part A 0.46/Part B 0.57，min 0.46（最接近但未超越 0.47）
- 結論：20日 RS 回看是甜蜜點（10日太噪、40日過擬合），SMH 仍是最佳基準（SPY 因缺少半導體板塊動態略差）

**NVDA-009 Momentum Breakout Pullback Continuation（3 次嘗試，全部失敗，repo 第 2 次 MBPC 結構）：**
- **Att1（Baseline）**：Donchian 20d 近 10 日內新高 + Close>SMA(50) + 5d 淺回檔 -3~-8% + RSI(14) [40,65] + 多頭 K 棒 + cd10，TP+8%/SL-7%/20d
  - Part A: 34 訊號 WR 67.6% Sharpe **0.41** cum +142.32%（11 筆 SL 集中 2020 COVID/2021 late-bull/2022 bear/2023 summer chop）
  - Part B: 8 訊號 WR 75.0% Sharpe **0.96** cum +47.30%（純趨勢期優異）
  - min(A,B) **0.41**（低於 NVDA-004 / NVDA-006 的 0.47）
  - A/B 平衡良好：年化訊號比 1.7:1（41% gap）、年化 cum 差 16.9%（<30%）✓
- **Att2（+ SMA(200) regime 閘門 + RSI_max 65→60，試圖過濾 late-cycle）**：
  - Part A: 21/66.7%/**0.38** cum +66.17%（-7% vs Att1）
  - Part B: 6/83.3%/**2.22** cum +46.87%（+131% vs Att1，單邊優異）
  - min(A,B) **0.38**（劣化）
  - 失敗：非選擇性過濾（訊號 -38% 但 WR 僅 -0.9pp），贏家/SL 移除比 9/5 低於整體 23/11，SMA(200) 過濾 2022-07-25 TP 贏家，RSI<60 過濾 AI 主升段健康續漲
- **Att3a（2DD cap >= -6%，CIBR-012 方向）**：與 Att1 完全相同（-6% 無綁定，NVDA 突破+淺回檔 2d 報酬典型 -3~-5%）
- **Att3b（2DD cap >= -4%）**：
  - Part A: 31/64.5%/**0.33** cum +92.36%（-20% vs Att1）
  - Part B: 8/62.5%/**0.49** cum +26.65%（-49% vs Att1）
  - min(A,B) **0.33**（三次最差）
  - 失敗：-4% cap 與 5d 淺回檔範圍部分重疊，cooldown-shift 引入新 SL（2024-11-29 -7.14%）
- **結論**：Part B Sharpe 0.96（+104% vs NVDA-004 Part B 0.47）證明 MBPC 結構在純趨勢期極有效，但 Part A 0.41 受多 regime 限制。**repo 第 2 次 MBPC 失敗**（繼 FXI-012 後），擴展 lesson：MBPC 需**單一純上升 regime**資產才穩定，**多 regime 資產**（FXI 政策驅動 / NVDA bubble+correction mixed）結構性劣化
- **NVDA-009 Att1 可作為 2024-2025 AI 純趨勢期補充訊號**，不取代 NVDA-004 / NVDA-006

**已證明無效（禁止重複嘗試）：**（更新）
原有項目加上：
- NVDA-007 RS 出場優化：延長持倉（25d）、放寬停損（-8%）、縮短持倉（15d）三種方向均失敗，TP+8%/SL-7%/20d 已確認為 RS 策略全域最優出場參數
- NVDA-008 RS 參數探索：10日回看（噪音過多 Part B 0.17）、40日回看（A/B 過擬合 Part B 0.03）、SPY 基準（min 0.46 未超越）三種方向均失敗，20日 RS + SMH 基準已確認為全域最優 RS 參數
- NVDA-009 Momentum Breakout Pullback Continuation：三次迭代全部失敗（Att1 min 0.41 < 0.47），確認 MBPC 結構在多 regime 高波動個股結構性劣化。Att2 SMA(200) + RSI<60 非選擇性過濾、Att3 2DD cap -6% 無綁定 / -4% 雙向劣化
- **NVDA-010 ADX-Filtered RSI(2) MR（repo 首次 ADX/DMI 主規範閘門試驗，3 次迭代全部失敗）**：
  - Att1（ADX>=25 + +DI>-DI + RSI(2)<=15 + PB[-3%,-10%] + cd10）：Part A 3/66.7%/0.26 / Part B 1/0%/0.00 / min **0.00** —— 0.6 訊號/yr 過稀
  - Att2（ADX>=20 + RSI(2)<=20 + PB[-2%,-12%] + cd8）：Part A 8/62.5%/0.22 / Part B 1/0%/0.00 / min **0.00** —— Part B 卡 1 訊號（深修正違反 pullback / SMA / DMI）
  - Att3（移除 +DI>-DI + RSI(3)<=25 + PB to -15%）：Part A 8/37.5%/-0.27 / Part B 2/0%/0.00 / min **-0.27** —— cooldown chain shift 引入 4 連續 SL
  - 失敗根因：(1) ADX>=25 與 RSI(2)<=15 罕見共存（RSI 需持續下挫使 DMI 翻轉）；(2) +DI>-DI 提供真實選擇性但 naively 移除觸發 cooldown-shift；(3) 高約束相關性使放寬無比例增長訊號。**擴展 lesson #6 + #20b 至 ADX/DMI 類別**
- **NVDA-011 Capitulation-Depth Filter MR（repo 第 5 次 capitulation-depth filter 嘗試，repo 首次 >3% vol 高波動單一個股測試，3 次迭代全部失敗）**：
  - Att1（vol-scaled IWM-011：RSI(2)<10 + 2DD<=-4.5% + ClosePos>=40% + ATR>1.10 + cd 8 + TP+7%/SL-7%/15d）：Part A 5/40.0%/-0.21 / Part B 2/100%/std=0/0.00 / min **-0.21** —— 1.0/yr 訊號密度過稀（IWM-011 為 2.0/yr），3 SL（2019-04-26 trade-war / 2021-02-23 Feb tech corr / 2022-09-01 Jackson Hole）皆 multi-regime continuation traps
  - Att2（Att1 + 3d cap >= -6%，DIA-012/CIBR-012 cap 方向）：Part A 2/50%/-0.01 / Part B 2/100%/std=0/0.00 / min **-0.01** —— 移除 2 SL 但同時誤殺 2022-08-09 TP（深 3d capitulation reversal）；殘留 2021-02-23 SL 為 sharp 1d 急跌（non-prior-3d-buildup）
  - Att3（Att2 + 1d cap >= -4%，DIA-012 dual-dim 跨資產移植）：Part A 1/0%/0.00 / Part B 2/100%/std=0/0.00 / min **0.00** —— 誤殺 2020-01-27 pre-COVID winner（深 1d gap-down），DIA-012 cap 方向結構錯誤——NVDA winners 集中深 1d gap-down，與 DIA losers 集中深 1d 結構相反
  - 失敗根因：(1) vol-scaled IWM-011 framework 訊號密度不足（1.0/yr），multi-regime 使框架隨機化；(2) DIA-012 cap 方向結構性不適用——NVDA Part A 真實 capitulation winners（深 1d gap-down）與 DIA Part A losers 結構相反，cap 方向誤殺贏家（與 IWM-013 Att1 失敗模式平行）；(3) 殘留 2021-02-23 sharp 1d sub-threshold SL 無單維度過濾器可捕獲；(4) 與 TSLA-014（3.72%）/ FCX-011（3% vol）Post-Cap MR 跨資產失敗模式平行——擴展失敗 vol 上限至 NVDA 3.26%
  - **Lesson #19 family 邊界擴展（NVDA-011 貢獻）**：
    (a) raw return cap 方向 vs oscillator depth 方向選擇取決於 winners/losers 的 raw return 分布——SL 集中深 1d/2d/3d → cap 有效（DIA、CIBR、SPY）；winner 集中深 1d/2d/3d → cap 失敗，需 oscillator 維度（IWM、NVDA）；
    (b) capitulation-depth filter 訊號密度 < 1.5/yr → 兩種維度皆失敗（NVDA-011 confirmation）；
    (c) capitulation-depth filter 的 vol 上限介於 IWM 1.5-2%（成功）與 NVDA 3.26%（失敗）之間

- **NVDA-019 Failed Breakdown Reversal MR（repo 首次 FBR 主訊號於高 vol mega-cap 個股 + MR 框架，3 次迭代全部失敗）**：
  - Att1（baseline FBR：Donchian 20d + breakdown lookback 5d + Close>Open + SMA(20)≥1.00×SMA(60) + ATR(20)≤1.40×ATR(60) + cd 10）：Part A 15/60.0%/Sharpe **0.28** cum +22.38%（6 SL: 2019-04-29/2019-05-14/2019-08-07/2022-01-06/2022-04-13/2022-12-23）/ Part B 7/57.1%/Sharpe **0.22** cum +7.76%（3 SL: 2024-04-10/2024-07-22/2024-08-06）/ min **0.22**
  - Att2（+ breakdown depth ≥5% + 收緊 ATR regime 至 1.30）：Part A 11/45.5%/-0.01 / Part B 6/0.0%/0.00 cum -27.14% / min **-0.01** —— 雙向災難，**反直覺發現**：要求更深 breakdown depth 反向選擇 winners
  - Att3（還原 baseline + Close>昨日 High 強勢突破確認）：Part A 13/61.5%/0.31 / Part B 6/0.0%/0.00 cum -27.14% / min **0.00** —— **再次反直覺**：legitimate V-bounces 為漸進式收盤，dead-cat bounces 反而當日突破前日 High，filter 系統性過濾真實反彈、保留假反彈
  - 失敗根因：(1) NVDA Donchian Lower 在持續下跌中持續下移，FBR 訊號**幾乎無篩選力**；(2) signal-day filter 維度（depth、prev-high）在高 vol 個股 FBR 框架**反向選擇** winners；(3) 高 vol 個股 false breakdowns 與 true bottoms 在 signal-day 層面行為相似，single-day filter 結構性無區分力
  - **Lesson #20a 失敗家族擴展**：repo 第 1 次將 Failed Breakdown Reversal 應用於高 vol mega-cap 個股 + MR 框架，與 FXI-009（政策驅動 EM ETF）並列為 FBR 失敗清單；**Lesson #19 family v13 邊界**：NVDA signal-day filter 三次失敗整合（NVDA-011 + NVDA-017 + NVDA-019），lesson #19 family 在 NVDA 高 vol 結構**完全失效**

**尚未嘗試的方向（可探索，但預期邊際效益極低）：**
- BB(20,2.5) 更嚴格的擠壓條件
- 純趨勢跟蹤（SMA 交叉）— 但 IWM-007、TSLA-006 驗證 SMA 交叉對個股/ETF 普遍無效
- ~~ATR ratio BAND（CIBR-014 / FXI-014 路徑）~~ → NVDA-020 已驗證失敗（3 次嘗試 min 0.46/0.32/0.54，BAND filter 適用邊界 = MR/capitulation 框架，不適用 MBPC momentum continuation 框架）
- ~~NVDA-QQQ cross-asset divergence CEILING regime gate~~ → **NVDA-021 Att2 已驗證成功（min 1.43，+160% vs baseline 0.55，repo NVDA 0.55 ceiling 首次突破）**
- NVDA earnings calendar 季節性過濾（避開財報前後 3-5 天）— 待嘗試
- ^VXN BANDS regime gate（XBI-017 跨資產移植，雙邊界排除中等 VIX 帶）— 待嘗試
- NVDA-SMH cross-asset divergence CEILING（其他 anchor 試驗）— 待嘗試

**關鍵資產特性：**
- 日均波動 ~3.26%，為 GLD 的 2.92 倍（HIGH-BETA 個股）
- AI/半導體龍頭，動量效應強，突破策略優於均值回歸（同 TSLA）
- 相對強度（vs SMH）策略有效，RS ≥ 5% 是甜蜜點（同 TSM-007）
- 2022 年經歷 -66% 峰谷回撤，均值回歸在此期間產生假訊號，突破策略只在 2022 產生 2 筆停損
- 訊號頻率：RS 7.0/6.0/年（最佳 A/B 平衡），突破 3.4/年，均值回歸 1.2/年
- **RS 出場優化無效**：TSM-008 的延長持倉方法在 NVDA 無效，因交易平均 7 天解決（vs TSM 更長）
- **RS 參數探索無效**：不同回看窗口和不同基準均未超越 20日 SMH RS≥5%
- NVDA-004/006 已確認為全域最優（11 次實驗、34+ 次嘗試，含均值回歸、突破、動量回調、相對強度、RS 出場優化、RS 參數探索、Momentum Breakout Pullback Continuation、ADX/DMI Filtered RSI(2) MR、Capitulation-Depth Filter MR 九大方向）
- **NVDA-012 突破 0.47 結構性上限**：在 NVDA-004 BB Squeeze 框架疊加 buffered SMA(20)≥0.97×SMA(60) multi-week regime gate（lesson #22 自 TSLA-015 跨資產移植），min(A,B) 0.47→**0.51**（+9%）。Part A 過濾 2022-07-20 bear regime SL（ratio << 0.97），Part B 過濾 2025-12-23 marginal loser（ratio < 0.97）但保留 2025-05-14 transition winner（ratio 0.97-0.98 之間）。**k 值跨資產不可直接移植**：TSLA k=0.99 sweet spot 在 NVDA 變為 k=0.97（3% 緩衝），lesson #22 跨資產精煉
- **NVDA-021 突破 0.55 結構性上限**：在 NVDA-013 Att3 雙重 SMA/ATR regime gate 飽和後，疊加 NVDA-QQQ 20d divergence CEILING +3% 過濾「single-stock rally exhaustion」regime，min(A,B) 0.55→**1.43**（+160%）。Part A 過濾 NVDA 過度跑贏 QQQ 之 SL（含 2020-10-20 + 2023-08-28），WR 73.1%→**90.0%**（NVDA Part A WR 歷史新高）。**Repo 首次 cross-asset divergence regime gate（CEILING 方向）成功移植至高波動 AI mega-cap 個股 + MBPC 框架（雙重邊界擴展）**：先前 INDA-012/EWZ-009 為 EM 單一國家 ETF + MR 框架；TSLA-017 為 FLOOR 方向 + BB Squeeze 框架。**QQQ 為更獨立 anchor**（NVDA ~5-12% 權重 vs SMH ~20%），提供更乾淨 NVDA-specific rally exhaustion 訊號
<!-- AI_CONTEXT_END -->

# NVDA 實驗總覽 (NVDA Experiments Overview)

## 標的特性 (Asset Characteristics)

- **NVDA (NVIDIA Corporation)**：全球 AI/GPU 龍頭，半導體產業核心
- 日均波動約 3.26%，為 GLD 的 2.92 倍（年化波動約 51.7%）
- 個股（非 ETF），受公司業績、AI 產業趨勢、半導體週期影響
- 流動性極高，但受單一公司基本面風險影響
- 2022 年峰谷回撤 -66%（2018 年亦達 -56%），極端事件頻率較高

## 實驗列表 (Experiment List)

| ID       | 資料夾                      | 策略摘要                               | 狀態    |
|----------|----------------------------|---------------------------------------|---------|
| NVDA-001 | `nvda_001_extreme_oversold` | RSI(2)<5 + 2日急跌≤-7%，TP+8%/SL-10%/15天 | 已完成（均值回歸最優） |
| NVDA-002 | `nvda_002_capped_drawdown` | 出場參數探索（3次嘗試均失敗），確認 NVDA-001 為均值回歸最優 | 已完成 |
| NVDA-003 | `nvda_003_bb_squeeze_breakout` | BB(20,2) 擠壓突破 + SMA(50) 趨勢，TP+8%/SL-7%/20天，冷卻15天 | 已完成（前任最優） |
| NVDA-004 | `nvda_004_bb_squeeze_optimized` | BB(20,2) 擠壓突破 + SMA(50) 趨勢，TP+8%/SL-7%/20天，冷卻10天 | 已完成（當前最優） |
| NVDA-005 | `nvda_005_momentum_pullback` | 動量回調：ROC(20)≥15% + 5日回撤3-8% + SMA(50)，TP+8%/SL-7%/20天 | 已完成（未超越 NVDA-004） |
| NVDA-006 | `nvda_006_relative_strength` | 相對強度：NVDA-SMH RS≥5% + 5日回撤3-8% + SMA(50)，TP+8%/SL-7%/20天 | 已完成（互補策略，min(A,B) 持平，OOS +36%） |
| NVDA-007 | `nvda_007_rs_exit_optimized` | RS 出場優化：同 NVDA-006 進場，3種出場嘗試（25d/SL-8%/15d） | 已完成（3次嘗試均未超越 NVDA-006） |
| NVDA-008 | `nvda_008_rs_param_explore` | RS 參數探索：10日/40日回看、SPY基準（3次嘗試均未超越） | 已完成（3次嘗試均未超越 NVDA-004/006） |
| NVDA-009 | `nvda_009_momentum_pullback` | Momentum Breakout Pullback Continuation：Donchian 20d + 5d 淺回檔 -3~-8% + SMA(50) + RSI[40,65]，TP+8%/SL-7%/20d | 已完成（3次嘗試全部失敗，min(A,B) 0.41 < 0.47） |
| NVDA-010 | `nvda_010_adx_rsi2_mr` | ADX-Filtered RSI(2) MR：ADX(14)>=25 + +DI>-DI + RSI(2)<=15 + Pullback[-3%,-10%] + SMA(50)，TP+6%/SL-6%/15d | 已完成（3次嘗試全部失敗，min(A,B) 0.00/0.00/-0.27） |
| NVDA-011 | `nvda_011_capitulation_filter` | Capitulation-Depth Filter MR (RSI Oscillator Depth)：RSI(2)<10 + 2DD<=-4.5% + ClosePos>=40% + ATR>1.10 + 1d/3d cap dual-dim，TP+7%/SL-7%/15d/cd 8 | 已完成（3次嘗試全部失敗，min(A,B) -0.21/-0.01/0.00） |
| NVDA-012 | `nvda_012_regime_breakout` | Multi-Week Regime-Aware BB Squeeze Breakout：NVDA-004 + SMA(20)≥0.97×SMA(60) buffered multi-week trend regime（lesson #22 跨資產移植自 TSLA-015），TP+8%/SL-7%/20d/cd 10 | 已完成（Att2 SUCCESS，min(A,B) 0.51，+9% vs NVDA-004 0.47） |
| NVDA-013 | `nvda_013_regime_mbpc` | Multi-Week Regime-Aware MBPC：NVDA-009 + SMA(20)≥1.00×SMA(60) strict trend regime + ATR(20)≤1.40×ATR(60) vol regime（lesson #22 cross-strategy 首次 BB Squeeze→MBPC 移植 + 首次發現 vol regime 在非 BB Squeeze 框架非冗餘），TP+8%/SL-7%/20d/cd 10 | 已完成（Att3 SUCCESS，min(A,B) **0.55**，+8% vs NVDA-012 0.51，+34% vs NVDA-009 0.41，已被 NVDA-021 Att2 超越） |
| NVDA-014 | `nvda_014_negative_rs_mr` | Negative RS Pairs MR：NVDA-SMH RS≤-3% + 10d Pullback≥6% + ATR(20)≤1.40 + ClosePos≥0.40，TP+6%/SL-6%/15d | 已完成（3 次嘗試全部失敗，min(A,B) -0.25/-0.49/0.29 < NVDA-013 0.55） |
| NVDA-015 | `nvda_015_regime_rs` | Multi-Week Regime-Aware RS Momentum Pullback：NVDA-006 + SMA(20)≥k×SMA(60) + ATR(20)≤1.40×ATR(60) vol regime（lesson #22 + ATR vol regime cross-strategy 首次 RS Momentum 框架移植），TP+8%/SL-7%/20d/cd 10 | 已完成（3 次嘗試全部失敗，min(A,B) 0.37/0.37/0.48 < NVDA-013 0.55；**核心發現**：lesson #22 SMA regime 對 RS Momentum 結構性冗餘，RS 進場已隱含 uptrend regime） |
| NVDA-016 | `nvda_016_sector_confirmed_mbpc` | Sector-Health Confirmed Multi-Week Regime-Aware MBPC：NVDA-013 Att3 + **SMH 5/10 日報酬 >= macro_min_return** sector context confirmation gate（IWM-015 lesson #25 mirror inversion，repo 第 4 次跨資產驗證、首次 MBPC 動量延續框架 mirror direction），TP+8%/SL-7%/20d/cd 10 | 已完成（3 次嘗試 Att1 失敗 / Att2 非綁定 / **Att3 PARTIAL**：min(A,B)† 0.62 +12.7% Sharpe 但 A/B cum gap 46% 失 30% 目標；確認 lesson #25 不適用 MBPC + 高波動 AI 個股） |
| NVDA-017 | `nvda_017_signal_day_filter` | Signal-Day 5d Return CEILING on MBPC：NVDA-013 Att3 + **訊號日 5 日報酬 <= ret_5d_max**（rally exhaustion filter，lesson #19 family v10/v12 cross-asset port from TSM-011 Att3 → repo 首次 MBPC 框架應用），TP+8%/SL-7%/20d/cd 10 | 已完成（3 次嘗試全部失敗 REJECT：Att1 (0.045) min 0.52 cooldown chain shift / Att2 (0.040) min 0.52 second-order chain shift / Att3 (0.050) ablation = baseline 0.55；NVDA Heterogeneous SLs 結構使 signal-day return 維度無 surgical 切點，TSM-011 跨資產假設於高波動 AI 個股 + MBPC 框架失敗） |
| NVDA-018 | `nvda_018_vxn_implied_vol_mbpc` | ^VXN Forward-Looking Implied-Vol Regime-Gated MBPC：NVDA-013 Att3 + **^VXN N 日 DIRECTION change / LEVEL cap**（lesson #24 v3 cross-asset port from TLT-013 / XLU-013 / GLD-015 / USO-025 → repo 首次 mega-cap 個股 + MBPC 框架），TP+8%/SL-7%/20d/cd 10 | 已完成（3 次嘗試全部失敗 REJECT：Att1 (3d cap +5.0) min 0.52 過濾 1 winner 0 SL / Att2 (10d cap 0.0) min 0.17 嚴重 over-filter / Att3 (LEVEL cap 25) min 0.41 移除 high-VXN winners；**repo 第 5 次 lesson #24 跨資產驗證首次失敗**，雙重邊界（asset class + strategy framework）同時不滿足） |
| NVDA-019 | `nvda_019_failed_breakdown_mr` | Failed Breakdown Reversal Mean Reversion：Donchian Lower(20) 5d 內曾跌破 + Close 站回支撐 + Close>Open + SMA(20)≥1.00×SMA(60) + ATR(20)≤1.40×ATR(60) + cd10，TP+6%/SL-5%/15d（**repo 首次 FBR 主訊號於高 vol mega-cap 個股 + MR 框架**） | 已完成（3 次嘗試全部失敗 REJECT：Att1 (baseline) min 0.22 / Att2 (+breakdown depth ≥5% + 收緊 ATR 1.30) min -0.01 雙向災難 / Att3 (+Close>PrevHigh) min 0.00 Part B 6/0% 全敗；**反直覺發現**：depth + prev-high filter 皆**反向選擇 winners**；擴展 lesson #20a 失敗清單至高 vol mega-cap 個股 + MR primary entry） |
| NVDA-020 | `nvda_020_atr_band_mbpc` | Volatility-Acceleration Band Filter on MBPC：NVDA-013 Att3 + **入場日 ATR(5)/ATR(20) ratio BAND**（CIBR-014 / FXI-014 跨策略移植 → repo 首次 momentum / breakout-continuation 框架應用），TP+8%/SL-7%/20d/cd 10 | 已完成（3 次嘗試全部失敗 REJECT：Att1 (0.85, 1.20] min 0.46 反向選擇移除 5 winners / Att2 ceiling ≤ 1.05 min 0.32 移除 7 winners 全部、ratio > 1.05 區間 = 100% WR / Att3 floor > 1.00 min 0.54 邊際劣化 Part B 4/yr 過稀疏；**核心結論**：ATR ratio BAND filter 適用邊界 = 「signal-day vol structure 與 panic spike 一致」——MR / capitulation 框架成立，momentum / breakout-continuation 框架反向；NVDA-013 Att3 維持全域最優） |
| NVDA-021 | `nvda_021_qqq_divergence_mbpc` | NVDA-QQQ Cross-Asset Divergence CEILING Regime-Gated MBPC：NVDA-013 Att3 + **NVDA 20d 報酬 - QQQ 20d 報酬 ≤ +3.0%** cross-asset rally-exhaustion regime gate（lesson #19/#26 family v2 cross-strategy port from INDA-012/EWZ-009 CEILING + cross-asset port from TSLA-017 FLOOR → **repo 首次 cross-asset divergence regime gate（CEILING 方向）成功移植至高波動 AI mega-cap 個股 + MBPC 框架，雙重邊界擴展首次成功**），TP+8%/SL-7%/20d/cd 10 | ✅ **當前最佳**（Att2 SUCCESS，min(A,B) **1.43**，**+160% vs NVDA-013 Att3 0.55**，repo 首次突破 NVDA 0.55 結構性 Sharpe ceiling；A/B 平衡優異 cum 差 20.5%/訊號比 0.8:1；Att1 (+5%) min 0.82 / Att2 (+3% ★) min 1.43 / Att3 (+1%) min 1.33；+3% 為甜蜜點） |

## NVDA-001: RSI(2) 極端超賣均值回歸

### 目標 (Goal)

捕捉 NVDA 短期急跌後的 V 型反彈。使用 RSI(2) 極端超賣搭配 2日急跌幅度雙重確認，確保進場點位於急跌而非慢跌環境。

### 進場條件 (Entry Conditions)

| 條件 | 指標           | 閾值    | 說明                           |
|------|---------------|---------|-------------------------------|
| 1    | RSI(2)        | < 5     | 極端短期超賣                    |
| 2    | 2日累計跌幅    | ≤ -7%   | 確認急跌動能                    |
| 3    | 冷卻期         | 15 天   | 避免同一波下跌重複進場          |

### 出場參數 (Exit Parameters)

| 參數       | 值    | 說明                                  |
|-----------|-------|--------------------------------------|
| 獲利目標   | +8%   | 對應 NVDA 超賣反彈幅度（SPY 的 ~2.7x） |
| 停損       | -10%  | 非對稱，給波動空間                     |
| 最長持倉   | 15 天 | 科技股均值回歸速度較快                  |

### 成交模型 (Execution Model)

| 項目         | 設定                        |
|-------------|----------------------------|
| 進場模式     | 隔日開盤市價                  |
| 止盈委託     | 限價賣單 Day                  |
| 停損委託     | 停損市價 GTC                  |
| 到期出場     | 隔日開盤市價                  |
| 滑價         | 0.15%（個股）                |
| 悲觀認定     | 是                          |

### 設計理念 (Design Rationale)

- **RSI(2) 而非 RSI(10)**：NVDA 平均持倉 4-7 天，短週期 RSI 更精確匹配持倉週期（跨資產教訓 #13）
- **2日急跌而非回撤深度**：三重條件（DD+RSI+SMA）在 2022 長期熊市中失敗，因為「深度回撤」在慢跌中持續觸發。2日急跌確保捕捉急性恐慌而非慢性下跌
- **非對稱出場**（TP+8% vs SL-10%）：NVDA 反彈力度大但波動也高，寬停損避免在短期震盪中被震出（跨資產教訓 #37 FCX 經驗）
- **15天持倉**：NVDA 反彈速度快（平均持倉 4-7 天），15 天足夠且避免過長暴露風險

### 回測結果 (Backtest Results)

| 指標                    | Part A (IS)    | Part B (OOS)   |
|------------------------|---------------|----------------|
| 期間                    | 2019-01 ~ 2023-12 | 2024-01 ~ 2025-12 |
| 訊號數                  | 6              | 4              |
| 每年訊號數              | 1.2            | 2.0            |
| 勝率                    | 66.7%          | 75.0%          |
| 平均報酬                | +1.96%         | +3.47%         |
| 累計報酬                | +9.88%         | +13.21%        |
| 平均持倉天數            | 7.0            | 4.0            |
| 最大單筆回撤            | -11.39%        | -12.89%        |
| 盈虧比 (PF)            | 1.58           | 2.37           |
| 夏普比率                | 0.23           | 0.44           |
| 索提諾比率              | 0.33           | 0.68           |
| 卡瑪比率                | 0.17           | 0.27           |
| 最大連續虧損            | 1              | 1              |
| A/B 訊號頻率比          | 1.2:2.0 = 0.6:1（Part B 更活躍） |  |

### 關鍵觀察

1. **Part B 優於 Part A**：Sharpe 0.44 > 0.23，PF 2.37 > 1.58，無過擬合跡象
2. **A/B 頻率比 0.6:1**：Part B 訊號更密集，反映 2024-2025 波動加大
3. **最大連續虧損僅 1**：勝負交替良好，無連續虧損風險
4. **三重條件版本失敗**：DD≤-20% + RSI(10)<28 + SMA偏離≤-10% 在 2022 年產生 4 連敗，Part A -27.86%

## NVDA-002: 出場參數與回撤過濾探索（3 次嘗試均失敗）

### 目標 (Goal)

嘗試三種不同方向改善 NVDA-001 的風險調整後報酬：回撤範圍過濾、寬獲利目標、寬停損。

### 實驗列表更新

| ID       | 資料夾                      | 策略摘要                               | 狀態    |
|----------|----------------------------|---------------------------------------|---------|
| NVDA-002 | `nvda_002_capped_drawdown` | NVDA-001 出場參數探索，3 次嘗試均失敗   | 已完成 |

### 嘗試記錄 (Attempt Log)

#### Attempt 1: 回撤範圍過濾 + TP +10%
- **進場**：RSI(2)<5 + 2日跌幅≤-7% + 60日高點回撤 [-35%, -10%]
- **出場**：TP +10% / SL -10% / 15天
- **結果**：Part A Sharpe 0.20, Part B Sharpe -0.01
- **失敗原因**：回撤範圍過濾移除了 Part B 的 2 個好訊號（4→2），其中 1 個停損導致 Part B 崩潰

#### Attempt 2: 寬獲利目標 TP +10%
- **進場**：RSI(2)<5 + 2日跌幅≤-7%（同 NVDA-001）
- **出場**：TP +10% / SL -10% / 20天
- **結果**：Part A Sharpe -0.01, Part B Sharpe 0.57
- **失敗原因**：Part A 一筆交易達 +8% 但未達 +10%，反轉觸發停損。Part A 從 4W/2L 變 3W/3L。Part B 雖改善但 A/B 嚴重失衡
- **關鍵發現**：TP +8% 是 NVDA 的甜蜜點，+10% 會翻轉邊際交易

#### Attempt 3: 寬停損 SL -12% + 長持倉 25天（最終程式碼）
- **進場**：RSI(2)<5 + 2日跌幅≤-7%（同 NVDA-001）
- **出場**：TP +8% / SL -12% / 25天
- **結果**：

| 指標                    | Part A (IS)    | Part B (OOS)   |
|------------------------|---------------|----------------|
| 期間                    | 2019-01 ~ 2023-12 | 2024-01 ~ 2025-12 |
| 訊號數                  | 6              | 4              |
| 勝率                    | 66.7%          | 75.0%          |
| 平均報酬                | +1.29%         | +2.97%         |
| 累計報酬                | +5.05%         | +10.69%        |
| 夏普比率                | 0.14           | 0.34           |
| 盈虧比 (PF)            | 1.32           | 1.98           |

- **失敗原因**：SL -12% 成功救回 2022-06-10 交易（從停損翻為 +8% 達標），但其餘 2 筆虧損從 -10.13% 擴大至 -12.13%，更大虧損抵銷了多贏的 1 筆交易
- **關鍵發現**：SL -10% 是 NVDA 的甜蜜點。更寬 SL 救回交易的邊際收益被更大虧損吞噬

### 與 NVDA-001 比較

| 指標 | NVDA-001 | NVDA-002 Att3 | 差異 |
|------|----------|--------------|------|
| Part A Sharpe | 0.23 | 0.14 | -39% |
| Part B Sharpe | 0.44 | 0.34 | -23% |
| Part A 累計 | +9.88% | +5.05% | -49% |
| Part B 累計 | +13.21% | +10.69% | -19% |
| Part A WR | 66.7% | 66.7% | 同 |
| Part B WR | 75.0% | 75.0% | 同 |

### 結論

NVDA-001 的 TP +8% / SL -10% / 15天 已是全域最優出場參數組合。三個方向的探索確認：
1. **回撤過濾無效**：NVDA 的好訊號分布在各種回撤深度，過濾反而移除好訊號
2. **TP +8% 是硬上限**：+10% 使邊際交易翻轉為虧損
3. **SL -10% 是最佳平衡**：-12% 救回的交易不足以彌補更大虧損

## NVDA-003: Bollinger Band Squeeze Breakout（前任最優）

### 目標 (Goal)

以波動收縮後的突破取代均值回歸，捕捉 NVDA 動量驅動的爆發性上漲。基於 TSLA-005 成功經驗（Sharpe 0.35/0.37）移植，NVDA 日波動 3.26% 在突破策略有效範圍內（lesson #71/#73）。

### 進場條件 (Entry Conditions)

| 條件 | 指標                    | 閾值                   | 說明                                |
|------|------------------------|----------------------|-------------------------------------|
| 1    | BB Width               | 60日 25th 百分位       | 近期波動收縮（5日內曾發生）            |
| 2    | Close vs Upper BB(20,2) | Close > Upper BB      | 突破上軌                             |
| 3    | Close vs SMA(50)       | Close > SMA(50)       | 趨勢向上                             |
| 4    | 冷卻期                  | 15 天                 | 避免同一波上漲重複進場               |

### 出場參數 (Exit Parameters)

| 參數       | 值    | 說明                                  |
|-----------|-------|--------------------------------------|
| 獲利目標   | +8%   | NVDA 硬上限（均值回歸和突破均驗證）      |
| 停損       | -7%   | 突破失敗反轉快，比均值回歸更緊           |
| 最長持倉   | 20 天 | 部分突破交易需要 10-15 天完成動能        |

### 成交模型 (Execution Model)

| 項目         | 設定                        |
|-------------|----------------------------|
| 進場模式     | 隔日開盤市價                  |
| 止盈委託     | 限價賣單 Day                  |
| 停損委託     | 停損市價 GTC                  |
| 到期出場     | 隔日開盤市價                  |
| 滑價         | 0.15%（個股）                |
| 悲觀認定     | 是                          |

### 回測結果 (Backtest Results)

| 指標                    | Part A (IS)    | Part B (OOS)   |
|------------------------|---------------|----------------|
| 期間                    | 2019-01 ~ 2023-12 | 2024-01 ~ 2025-12 |
| 訊號數                  | 15             | 8              |
| 每年訊號數              | 3.0            | 4.0            |
| 勝率                    | 66.7%          | 62.5%          |
| 平均報酬                | +2.80%         | +3.08%         |
| 累計報酬                | +45.82%        | +25.36%        |
| 平均持倉天數            | 7.5            | 11.0           |
| 最大單筆回撤            | -9.20%         | -10.52%        |
| 盈虧比 (PF)            | 2.18           | 2.61           |
| 夏普比率                | 0.40           | 0.47           |
| 索提諾比率              | 0.68           | 0.86           |
| 卡瑪比率                | 0.30           | 0.29           |
| 最大連續虧損            | 2              | 2              |
| A/B 訊號頻率比          | 1.88:1（可接受）|               |

### 設計理念 (Design Rationale)

- **突破 > 均值回歸**：NVDA 為動量驅動個股（同 TSLA），順勢突破自然優於逆勢均值回歸。Sharpe 提升 +74%（Part A）、+7%（Part B）
- **BB 擠壓 + 5日寬鬆窗口**：波動收縮與突破之間通常需要數日醞釀（同 TSLA-005 lesson #72）
- **SL -7%（比均值回歸 -10% 更緊）**：突破失敗後反轉速度更快，不需要如均值回歸般寬鬆的停損
- **訊號頻率 3.0/年（vs 均值回歸 1.2/年）**：突破條件比極端超賣更常見，統計可信度顯著提升

### 嘗試記錄 (Attempt Log)

#### Attempt 1（最佳，已採用）: TP +8% / SL -7% / 20天
- Part A Sharpe 0.40, Part B Sharpe 0.47, A/B gap -0.07（B > A，無過擬合）
- 15 筆 Part A 交易中 10 筆達標、5 筆停損、1 筆到期

#### Attempt 2: TP +10% / SL -7% / 20天
- Part A Sharpe 0.27（-33%），Part B Sharpe 0.53（+13%）
- 失敗原因：2020-10-01 交易達 +8% 但未達 +10% 後反轉為停損，2021-08-20 交易從達標變為到期 +1.60%
- 確認 TP +8% 是 NVDA 硬上限（均值回歸和突破均驗證）

#### Attempt 3: TP +8% / SL -5% / 20天
- Part A Sharpe 0.27（-33%），WR 53.3%（-13.4pp），Part B Sharpe 0.62（+32%）
- 失敗原因：SL 過緊，Part A 多 2 筆交易被提前停損。NVDA 日波動 3.26%，-5% 停損（~1.5σ）太近
- SL -7%（~2.1σ）是甜蜜點

### 與 NVDA-001 比較

| 指標 | NVDA-001 (均值回歸) | NVDA-003 (突破) | 差異 |
|------|---------------------|-----------------|------|
| Part A Sharpe | 0.23 | 0.40 | +74% |
| Part B Sharpe | 0.44 | 0.47 | +7% |
| Part A 訊號數 | 6 | 15 | +150% |
| Part B 訊號數 | 4 | 8 | +100% |
| Part A 累計 | +9.88% | +45.82% | +364% |
| Part B 累計 | +13.21% | +25.36% | +92% |
| Part A PF | 1.58 | 2.18 | +38% |
| Part B PF | 2.37 | 2.61 | +10% |

## NVDA-004: BB Squeeze Breakout Optimized（前任最優，已被 NVDA-012 / NVDA-013 超越）

### 目標 (Goal)

基於 NVDA-003，探索未嘗試的參數空間以進一步提升風險調整後報酬。重點：冷卻期調整和停損微調。

### 進場條件 (Entry Conditions)

| 條件 | 指標                    | 閾值                   | 說明                                |
|------|------------------------|----------------------|-------------------------------------|
| 1    | BB Width               | 60日 25th 百分位       | 近期波動收縮（5日內曾發生）            |
| 2    | Close vs Upper BB(20,2) | Close > Upper BB      | 突破上軌                             |
| 3    | Close vs SMA(50)       | Close > SMA(50)       | 趨勢向上                             |
| 4    | 冷卻期                  | 10 天                 | 比 NVDA-003 縮短 5 天，捕捉更多訊號   |

### 出場參數 (Exit Parameters)

| 參數       | 值    | 說明                                  |
|-----------|-------|--------------------------------------|
| 獲利目標   | +8%   | NVDA 硬上限（均值回歸和突破均驗證）      |
| 停損       | -7%   | 突破甜蜜點（-5% 太緊，-8% 加大虧損不救回交易） |
| 最長持倉   | 20 天 | 部分突破交易需要 10-15 天完成動能        |

### 成交模型 (Execution Model)

| 項目         | 設定                        |
|-------------|----------------------------|
| 進場模式     | 隔日開盤市價                  |
| 止盈委託     | 限價賣單 Day                  |
| 停損委託     | 停損市價 GTC                  |
| 到期出場     | 隔日開盤市價                  |
| 滑價         | 0.15%（個股）                |
| 悲觀認定     | 是                          |

### 回測結果 (Backtest Results)

| 指標                    | Part A (IS)    | Part B (OOS)   |
|------------------------|---------------|----------------|
| 期間                    | 2019-01 ~ 2023-12 | 2024-01 ~ 2025-12 |
| 訊號數                  | 17             | 8              |
| 每年訊號數              | 3.4            | 4.0            |
| 勝率                    | 70.6%          | 62.5%          |
| 平均報酬                | +3.41%         | +3.08%         |
| 累計報酬                | +70.09%        | +25.36%        |
| 平均持倉天數            | 8.6            | 11.0           |
| 最大單筆回撤            | -9.20%         | -10.52%        |
| 盈虧比 (PF)            | 2.62           | 2.61           |
| 夏普比率                | 0.50           | 0.47           |
| 索提諾比率              | 0.88           | 0.86           |
| 卡瑪比率                | 0.37           | 0.29           |
| 最大連續虧損            | 2              | 2              |
| A/B 訊號頻率比          | 2.13:1（可接受）|               |

### 設計理念 (Design Rationale)

- **冷卻期 10天（vs NVDA-003 的 15天）**：縮短冷卻期在 Part A 新增 2 筆好訊號（2020-07-08、2020-08-03 皆達標 +8%），Part B 完全不受影響（同 8 筆訊號、同結果）
- **SL -7% 不變**：Att1 驗證 SL -8% 使每筆停損虧損更大（-8.14% vs -7.14%）而未救回任何交易，Part B Sharpe 0.47→0.41
- **SMA(50) 不變**：Att3 驗證 SMA(20) 讓通 2022-06-02 熊市假突破（停損），Part A Sharpe 0.50→0.40

### 嘗試記錄 (Attempt Log)

#### Attempt 1: SL -8% + 冷卻 10天
- Part A Sharpe 0.43, Part B Sharpe 0.41
- 失敗原因：SL -8% 使每筆停損虧損增加 1pp（-7.14%→-8.14%），未救回任何交易，Part B 嚴格劣化

#### Attempt 2（最佳，已採用）: SL -7% + 冷卻 10天
- Part A Sharpe 0.50（+25%），Part B Sharpe 0.47（不變），A/B 比 1.06:1（近乎完美平衡）
- Part A 新增 2020-07-08、2020-08-03 兩筆達標訊號

#### Attempt 3: SL -7% + 冷卻 10天 + SMA(20)
- Part A Sharpe 0.40, Part B Sharpe 0.47
- 失敗原因：SMA(20) 讓通 2022-06-02 熊市假突破，Part A 增加 1 筆停損，Sharpe 回到 NVDA-003 水平

### 與 NVDA-003 比較

| 指標 | NVDA-003 | NVDA-004 | 差異 |
|------|----------|----------|------|
| Part A Sharpe | 0.40 | 0.50 | **+25%** |
| Part B Sharpe | 0.47 | 0.47 | 不變 |
| Part A 訊號數 | 15 | 17 | +13% |
| Part B 訊號數 | 8 | 8 | 不變 |
| Part A 累計 | +45.82% | +70.09% | **+53%** |
| Part B 累計 | +25.36% | +25.36% | 不變 |
| Part A PF | 2.18 | 2.62 | **+20%** |
| Part B PF | 2.61 | 2.61 | 不變 |
| A/B Sharpe 比 | 0.85:1 | 1.06:1 | **近乎完美** |

## 演進路線圖 (Roadmap)

```
NVDA-001 (RSI(2)<5 + 2日急跌≤-7%，TP+8%/SL-10%/15天) ← 均值回歸最優
  └── NVDA-002 (出場參數探索：回撤過濾/TP+10%/SL-12%，均失敗)
NVDA-003 (BB 擠壓突破 + SMA(50)，TP+8%/SL-7%/20天，冷卻15天) ← 前任最優
  ├── Att2 (TP+10%：Part A 崩潰，+8% 是硬上限)
  └── Att3 (SL-5%：過緊，Part A WR 降至 53.3%)
NVDA-004 (BB 擠壓突破 + SMA(50)，TP+8%/SL-7%/20天，冷卻10天) ← 當前全域最優
  ├── Att1 (SL-8%：虧損更大不救回交易，Part B -12.8%)
  └── Att3 (SMA(20)：讓通熊市假突破，Part A 回到 0.40)
```

## NVDA-001 滾動窗口績效分析

> **分析日期：** 2026-03-30
> **窗口：** 2 年，步進 6 個月（共 12 個窗口，其中 9 個有效用於評估）

### 滾動窗口績效表

| 窗口 | 訊號 | 勝率 | 平均報酬 | 累計報酬 | MDD | ΔWR |
|------|------|------|----------|----------|-----|-----|
| 2019-01~2020-12 | 1 | 100.0% | +8.00% | +8.00% | -4.31% | — |
| 2019-07~2021-06 | 1 | 100.0% | +8.00% | +8.00% | -4.31% | +0.0pp |
| 2020-01~2021-12 | 1 | 100.0% | +8.00% | +8.00% | 1.24% | +0.0pp |
| 2020-07~2022-06 | 3 | 66.7% | +1.96% | +4.82% | -11.39% | -33.3pp |
| 2021-01~2022-12 | 5 | 60.0% | +0.07% | -1.44% | -11.39% | -6.7pp |
| 2021-07~2023-06 | 5 | 60.0% | +0.75% | +1.74% | -11.39% | +0.0pp |
| 2022-01~2023-12 | 4 | 50.0% | -1.07% | -5.79% | -11.39% | -10.0pp |
| 2022-07~2024-06 | 3 | 66.7% | +1.96% | +4.82% | -10.63% | +16.7pp |
| 2023-01~2024-12 | 2 | 50.0% | -1.07% | -2.94% | -12.89% | -16.7pp |
| 2023-07~2025-06 | 4 | 75.0% | +3.47% | +13.21% | -12.89% | +25.0pp |
| 2024-01~2025-12 | 4 | 75.0% | +3.47% | +13.21% | -12.89% | +0.0pp |
| 2024-07~2026-03 | 3 | 66.7% | +1.96% | +4.82% | -12.89% | -8.3pp |

### 預測精準度表

| 窗口 | WR | 平均贏利 | 平均虧損 | 盈虧比 | 差點成功 |
|------|------|----------|----------|--------|----------|
| 2019-01~2020-12 | 100.0% | +8.00% | N/A | ∞ | — |
| 2019-07~2021-06 | 100.0% | +8.00% | N/A | ∞ | — |
| 2020-01~2021-12 | 100.0% | +8.00% | N/A | ∞ | — |
| 2020-07~2022-06 | 66.7% | +8.00% | -10.13% | 1.58 | — |
| 2021-01~2022-12 | 60.0% | +6.87% | -10.13% | 1.02 | 1/1 |
| 2021-07~2023-06 | 60.0% | +8.00% | -10.13% | 1.18 | — |
| 2022-01~2023-12 | 50.0% | +8.00% | -10.13% | 0.79 | — |
| 2022-07~2024-06 | 66.7% | +8.00% | -10.13% | 1.58 | — |
| 2023-01~2024-12 | 50.0% | +8.00% | -10.13% | 0.79 | — |
| 2023-07~2025-06 | 75.0% | +8.00% | -10.13% | 2.37 | — |
| 2024-01~2025-12 | 75.0% | +8.00% | -10.13% | 2.37 | — |
| 2024-07~2026-03 | 66.7% | +8.00% | -10.13% | 1.58 | — |

### 漸變性評估

- **勝率範圍**：50.0% ~ 75.0%（ΔWR 標準差 13.2pp，最大跳動 25.0pp）
- **盈虧比範圍**：0.79 ~ 2.37（ΔPF 標準差 0.78）
- **累計報酬範圍**：-5.79% ~ +13.21%（ΔCum 標準差 8.73%）
- **平均贏利範圍**：+6.87% ~ +8.00%（Δ標準差 0.56%，穩定）
- **平均虧損範圍**：-10.13%（固定 SL 觸發，完全一致）

**判定：**
- ✗ 預測精準度突變（勝率最大跳動 25.0pp > 20pp 閾值，發生在窗口 6→7）
- ✓ 下游績效漸變（累計報酬最大跳動 16.15% ≤ 3σ = 26.19%）

**診斷：** 精準度波動但績效穩定 → 勝/虧報酬互補抵消了精準度變化

### 分析解讀

1. **訊號極稀少**：多數窗口僅 1-5 筆訊號，NVDA 作為高動量股票極少觸發極端超賣條件
2. **早期窗口 100% 勝率不具代表性**：前 3 窗口各僅 1 筆訊號，統計無意義
3. **2022 年半導體寒冬**：窗口 4-7 勝率降至 50-67%，反映 NVDA 從高點回落 60%+ 的極端走勢
4. **近期恢復**：2023-2025 窗口受益於 AI 熱潮，勝率回升至 75%
5. **虧損固定在 -10.13%**：SL 完全一致觸發，顯示 NVDA 跌勢時下行空間極大
6. **不適合漸變性評估**：訊號數太少導致勝率波動被放大，建議累積更多訊號後重新評估

---

## NVDA-005: 動量回調 (Momentum Pullback)

### 目標 (Goal)

探索動量回調策略是否能超越 BB Squeeze Breakout。在上升趨勢中買入短期回調，捕捉趨勢延續動量。

### 進場條件 (Entry Conditions) — Attempt 2（最佳版本）

| 條件 | 指標           | 閾值    | 說明                           |
|------|---------------|---------|-------------------------------|
| 1    | ROC(20)       | ≥ 15%  | 近 20 日強勢動量                |
| 2    | 5日高點回撤    | 3-8%    | 短暫整理（非深度回調）          |
| 3    | SMA(50)       | Close > | 上升趨勢確認                    |
| 4    | 冷卻期         | 10 天   | 避免重複進場                    |

### 出場參數 (Exit Parameters)

| 參數       | 值    | 說明                                  |
|-----------|-------|--------------------------------------|
| 獲利目標   | +8%   | NVDA 硬上限（跨策略驗證）              |
| 停損       | -7%   | 與 NVDA-004 相同                      |
| 最長持倉   | 20 天 |                                       |

### 成交模型 (Execution Model)

| 項目         | 設定                        |
|-------------|----------------------------|
| 進場模式     | 隔日開盤市價                  |
| 止盈委託     | 限價賣單 Day                  |
| 停損委託     | 停損市價 GTC                  |
| 到期出場     | 隔日開盤市價                  |
| 滑價         | 0.15%（個股）                |
| 悲觀認定     | 是                          |

### 回測結果 (Backtest Results) — Attempt 2

| 指標 | Part A (2019-2023) | Part B (2024-2025) |
|------|-------------------|--------------------|
| 訊號數 | 25 (5.0/年) | 9 (4.5/年) |
| 勝率 | 64.0% | 77.8% |
| 累計報酬 | +74.15% | +47.78% |
| Sharpe | 0.36 | 0.74 |
| PF | 2.07 | 3.92 |
| MDD | -12.45% | -8.96% |
| 平均持倉 | 6.0 天 | 6.1 天 |

### 嘗試記錄 (Attempt Log)

| 嘗試 | 配置 | Part A Sharpe | Part B Sharpe | 結論 |
|------|------|--------------|--------------|------|
| Att1 | 20日高點回撤8-15% + RSI(5)<30 + SMA(50), 冷卻10天 | 0.34 | 0.06 | 趨勢+均值回歸矛盾，Part B 崩潰 |
| Att2 | ROC(20)≥15% + 5日回撤3-8% + SMA(50), 冷卻10天 | 0.36 | 0.74 | Part B 優異但 Part A 弱，min(A,B)=0.36 |
| Att3 | ROC(20)≥20% + 5日回撤3-8% + SMA(50), 冷卻15天 | 0.38 | 0.00* | 6/6全達標但零方差使Sharpe=0，Part A仍不足 |

\* Part B 全部 6 筆交易均達 +8% TP，報酬標準差為 0，Sharpe 公式回傳 0。

### 結論

動量回調策略在 NVDA 上 Part B 表現優異（Att2 Sharpe 0.74），但 Part A 受 2021 泡沫期假訊號拖累（3 筆停損於 2021 H2），最佳 Part A Sharpe 僅 0.38，min(A,B) = 0.36 無法超越 NVDA-004 的 0.47。A/B 訊號比 2.78:1 也偏高。

**根本原因**：動量回調在強趨勢末期（2021 NVDA 泡沫頂部）仍會發出訊號，而 BB Squeeze Breakout 要求波動收縮後才進場，自然過濾掉高波動期的假訊號。NVDA-004 仍為當前最佳。

---

## NVDA-006: Relative Strength Momentum Pullback

### 目標 (Goal)

受 TSM-007 成功啟發（Sharpe 0.64/1.32），測試相對強度動量回調策略在 NVDA 上的效果。核心假設：當 NVDA 相對半導體板塊（SMH）展現超額表現（20日報酬差 ≥ 5%）時，短期回調（5日高點回撤 3-8%）提供良好的進場機會，因為相對強度反映 NVDA 特有 alpha（非板塊 beta）。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | NVDA-SMH 20日報酬差 | ≥ 5% | NVDA 相對板塊有超額表現 |
| 2 | 5日高點回撤 | 3-8% | 短暫整理（NVDA 日波動 3.26%，比 TSM 高故放寬上限至 8%） |
| 3 | Close > SMA(50) | - | 上升趨勢確認 |
| 4 | 冷卻期 | 10 天 | NVDA-004 已驗證 10 天優於 15 天 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 | +8% | NVDA 硬上限（lesson #45） |
| 停損 | -7% | NVDA 突破/RS 策略甜蜜點（lesson #74） |
| 最長持倉 | 20 天 | |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | 隔日開盤市價（Next Open Market） |
| 止盈委託 | 限價賣單 Day |
| 停損委託 | 停損市價 GTC |
| 到期出場 | 隔日開盤市價 |
| 滑價 | 0.15% |
| 悲觀認定 | 是 |

### 績效摘要 (Performance Summary) — Attempt 1（最佳）

| 指標 | Part A (IS) | Part B (OOS) |
|------|------------|-------------|
| 訊號數 | 35（7.0/年） | 12（6.0/年） |
| 勝率 | 68.6% | 75.0% |
| 累計報酬 | +177.95% | +60.07% |
| Sharpe | 0.47 | 0.64 |
| PF | 2.55 | 3.36 |
| MDD | -10.79% | -8.96% |
| 平均持倉 | 7.7 天 | 6.4 天 |
| 最大連續虧損 | 4 | 2 |

### vs NVDA-004 (Current Best) 比較

| 指標 | NVDA-004 | NVDA-006 | 差異 |
|------|----------|----------|------|
| Part A Sharpe | 0.50 | 0.47 | -6% |
| Part B Sharpe | 0.47 | 0.64 | **+36%** |
| min(A,B) | 0.47 | 0.47 | 持平 |
| A/B 年化訊號比 | 2.1:1 | 1.17:1 | **大幅改善** |
| Part A 訊號/年 | 3.4 | 7.0 | +106% |
| Part B 訊號/年 | 4.0 | 6.0 | +50% |

### 嘗試記錄 (Attempt Log)

| 嘗試 | 配置 | Part A Sharpe | Part B Sharpe | 結論 |
|------|------|--------------|--------------|------|
| Att1 | RS≥5%, pullback 3-8%, SMA(50), cooldown 10d | 0.47 | 0.64 | **最佳**，min(A,B) 0.47 持平 NVDA-004，OOS +36% |
| Att2 | RS≥5%, pullback 4-8%, SMA(50), cooldown 10d | 0.41 | 0.34 | pullback_min 提高過濾好訊號（Part B 失去 2 筆 +8% 贏利） |
| Att3 | RS≥7%, pullback 3-8%, SMA(50), cooldown 10d | 0.45 | 0.29 | RS 門檻過嚴，Part B 失去 2025-07-22 好訊號 |

### 結論

相對強度動量回調（TSM-007 風格）在 NVDA 上成功驗證。min(A,B) = 0.47 持平 NVDA-004，但 Part B OOS Sharpe 顯著更優（0.64 vs 0.47，+36%），且 A/B 年化訊號比 1.17:1 遠優於 NVDA-004 的 2.1:1。RS ≥ 5% 是甜蜜點（同 TSM-007），NVDA 的高 alpha 特性使相對強度進場架構有效。

**與 NVDA-004 互補**：BB Squeeze Breakout 在波動收縮後捕捉技術突破，RS Momentum Pullback 在個股超額表現後捕捉回調。兩策略訊號集重疊度低，可作為互補配置。

---

## NVDA-007: RS Exit Optimization（RS 出場優化）

### 目標 (Goal)

借鏡 TSM-008 的成功（RS 進場 + 延長持倉，min(A,B) 從 0.64→0.79，+23%），嘗試優化 NVDA-006 的出場參數以提升 min(A,B) > 0.47。

### 進場條件（完全沿用 NVDA-006 Att1）

| 參數 | 值 | 說明 |
|------|------|------|
| RS 門檻 | NVDA-SMH 20日報酬差 ≥ 5% | 個股超額表現 |
| 短期回調 | 5日高點回撤 3-8% | 回調整理 |
| 趨勢確認 | Close > SMA(50) | 上升趨勢 |
| 冷卻期 | 10 交易日 | 避免重複進場 |

### 三次嘗試結果

| 嘗試 | 出場參數 | Part A Sharpe | Part B Sharpe | min(A,B) | 結論 |
|------|----------|--------------|--------------|----------|------|
| Att1 | TP+8%/SL-7%/**25d** | 0.44 | 0.64 | 0.44 | 延長持倉無效：avg hold 僅 7.9d，交易早在 20d 前結束 |
| Att2 | TP+8%/**SL-8%**/20d | 0.40 | 0.57 | 0.40 | 寬 SL 增加虧損幅度（-8.14% vs -7.14%），WR 不變 |
| Att3 | TP+8%/SL-7%/**15d** | 0.46 | **0.70** | 0.46 | 最接近基準（0.46 vs 0.47），Part B 最佳但 Part A 仍不足 |
| NVDA-006 基準 | TP+8%/SL-7%/20d | **0.47** | 0.64 | **0.47** | 已驗證為 RS 策略最佳出場 |

### 結論

TSM-008 的出場優化方法不適用 NVDA。關鍵差異：

1. **交易解決速度**：NVDA RS 交易平均 7 天解決（Part A 7.2d / Part B 6.2d），遠快於 TSM。延長或縮短持倉對大多數交易無影響。
2. **結構性虧損**：Part A 的 11 筆停損（31.4%）集中在 2021 泡沫期（5 筆）和其他高波動事件，這些是 RS 進場的固有風險，無法透過出場優化解決。
3. **SL -7% 是 NVDA 硬甜蜜點**：SL -8% 增加虧損幅度但未救回任何交易，確認 SL -7% 不可放寬。

**NVDA-004/006 已確認為全域最優**（7 次實驗、18+ 次嘗試，涵蓋均值回歸、突破、動量回調、相對強度、RS 出場優化五大策略方向）。

---

## NVDA-008: RS Parameter Exploration

### 目標 (Goal)

探索 NVDA-006 未嘗試的 RS 參數維度：不同回看窗口（10日/40日）和不同基準（SPY vs SMH），嘗試超越 NVDA-004/006 的 min(A,B) = 0.47。

### 策略邏輯 (Strategy Logic)

與 NVDA-006 相同的 RS 框架，但調整核心參數：
- 出場固定為已驗證最優：TP+8%/SL-7%/20天/冷卻10天
- 進場條件：NVDA vs 基準 N日報酬差 ≥ 門檻 + M日高點回撤在範圍 + Close > SMA(50)

### 三次嘗試結果

#### Attempt 1: SMH 10日 RS≥3% + 3日回撤 2-6%

**假設**：更短的 RS 回看窗口捕捉更即時的相對強度變化，搭配更短的回撤窗口捕捉更銳利的拉回。

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 43 (8.6/yr) | 17 (8.5/yr) |
| 勝率 | 69.8% | 52.9% |
| 累計報酬 | +256.00% | +17.57% |
| Sharpe | 0.48 | 0.17 |
| MDD | -15.65% | -10.94% |
| PF | 2.56 | 1.41 |

**結論**：10日回看窗口過於敏感，Part B WR 從 NVDA-006 的 ~75% 暴跌至 52.9%，產生大量噪音訊號。min(A,B) = 0.17，遠低於目標。

#### Attempt 2: SMH 40日 RS≥8% + 5日回撤 3-8%

**假設**：更長的 RS 回看窗口過濾短期噪音，只保留持續性超額表現。

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 38 (7.6/yr) | 14 (7.0/yr) |
| 勝率 | 71.1% | 50.0% |
| 累計報酬 | +278.28% | -0.88% |
| Sharpe | 0.57 | 0.03 |
| MDD | -11.02% | -14.33% |
| PF | 3.00 | 1.06 |

**結論**：40日回看嚴重過擬合 Part A 的 NVDA AI 動量時期（2020, 2023 大量達標訊號）。Part B 2024 年 NVDA 相對強度波動加劇，40日 RS 仍顯示歷史超額表現，但 NVDA 已在修正中。min(A,B) = 0.03。

#### Attempt 3: SPY 20日 RS≥8% + 5日回撤 3-8%（最佳嘗試）

**假設**：SPY 作為更廣泛的基準，捕捉 NVDA 特有 alpha（vs 大盤）而非板塊 beta。

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 35 (7.0/yr) | 11 (5.5/yr) |
| 勝率 | 68.6% | 72.7% |
| 累計報酬 | +165.80% | +48.21% |
| Sharpe | 0.46 | 0.57 |
| MDD | -9.60% | -14.33% |
| PF | 2.49 | 2.99 |

**結論**：SPY 基準 + 8% RS 門檻產生 Part B 0.57（vs NVDA-006 的 0.64）和 Part A 0.46（vs 0.47），A/B 平衡良好（gap 0.11）。但 min(A,B) = 0.46 仍未超越目標 0.47。SPY 缺少半導體板塊動態，較高 RS 門檻（8% vs 5%）減少 Part B 訊號至 11 筆（vs 12）。

### 結論

三種 RS 參數變體均未超越 NVDA-004/006（min(A,B) 0.47）：

1. **RS 回看窗口：20日是甜蜜點**。10日太敏感（噪音），40日太遲鈍（過擬合歷史趨勢）。
2. **基準選擇：SMH 仍為最佳**。SPY 作為基準（min 0.46）非常接近但缺少半導體板塊動態，NVDA 的超額表現主要來自板塊內 alpha 而非跨板塊 alpha。
3. **RS ≥5%（SMH）是甜蜜點**。SPY 需提高至 8% 才能維持訊號品質，但高門檻減少有效訊號。

**NVDA-004/006 已確認為全域最優**（8 次實驗、21+ 次嘗試，涵蓋均值回歸、突破、動量回調、相對強度、RS 出場優化、RS 參數探索六大策略方向）。

---

## NVDA-010: ADX-Filtered RSI(2) Mean Reversion（3 次嘗試全部失敗）

**Repo 首次將 ADX/DMI 作為主規範閘門試驗**（Average Directional Index +
Directional Movement Index）。先前所有實驗皆以 SMA / BB / ATR ratio /
pullback 作為 regime 過濾，ADX 為新方向。

### 動機 (Motivation)

NVDA-004 / NVDA-006 min(A,B) 皆停在 0.47，瓶頸都在 Part A 2019-2023
多 regime 期。NVDA-009 MBPC Part B 0.96 證明結構性訊號在純趨勢期極佳。
本實驗假設：**強趨勢期間（ADX>=25）的淺回檔短期超賣（RSI(2)<=15）為
高勝率 MR 進場；無趨勢/盤整期間（ADX<25）RSI(2) MR 失效**。

### 三次迭代結果

| 嘗試 | 進場條件 | Part A (n/WR/Sharpe) | Part B (n/WR/Sharpe) | min(A,B) |
|------|----------|----------------------|----------------------|----------|
| Att1 | ADX>=25 + +DI>-DI + RSI(2)<=15 + PB[-3%,-10%] + cd10 | 3/66.7%/**0.26** | 1/0%/**0.00** | **0.00** |
| Att2 | 放寬 ADX>=20 + RSI(2)<=20 + PB[-2%,-12%] + cd8 | 8/62.5%/0.22 | 1/0%/0.00 | **0.00** |
| Att3 | 移除 +DI>-DI + RSI(3)<=25 + PB to -15% | 8/**37.5%**/**-0.27** | 2/0%/0.00 | **-0.27** |

出場參數：TP +6% / SL -6% / 15 天 / 滑價 0.15%（含成交模型）

### 失敗分析

**Att1 過嚴（0.6 訊號/yr）**：
- ADX>=25 強趨勢與 RSI(2)<=15 deep oversold 罕見共存
- RSI(2)<=15 需持續下挫，但持續下挫使 +DI<<-DI 必然違反方向過濾
- 多重綁定 ADX ∧ RSI ∧ DMI ∧ Pullback ∧ Close>Open 交集結構性狹窄

**Att2 仍卡 Part B（1 訊號）**：
- Part A Sharpe 退化（0.26→0.22）—— 5 中等品質訊號稀釋集中贏家
- NVDA 2024-2025 深度修正（2024-08 -17%、2025-04 tariff -25%）違反:
  - (a) -12% pullback 上限
  - (b) Close > SMA(50) 規範閘門（深跌跌破 50 日 MA）
  - (c) +DI > -DI（DMI 快速崩盤期間翻轉至 bear）
- 結構不匹配：Part B 的 MR 機會在於深層 capitulation 事件

**Att3 cooldown chain shift**：
- 移除 +DI>-DI 釋放原本被壓制的 4 個訊號（2020-02-24 / 2021-02-23 /
  2021-12-06 / 2022-12-20）—— 全部 SL
- +DI>-DI 原本提供真實品質過濾，naively 移除使框架退化
- Part A WR 62.5%（Att2）→ 37.5%（Att3）

### 跨資產貢獻

**Repo 首次 ADX/DMI 主過濾器試驗失敗**：
1. 擴展 lesson #6（確認指標邊際效益遞減）至 ADX/DMI 類別
2. 擴展 lesson #20b 邊界：trend-strength oscillators（ADX）加入
   RSI/CCI/Stoch/MACD hook divergence 作為多 regime 高波動個股的無效
   進場主過濾器
3. NVDA 結構性 Sharpe 上限約 0.5，2019-2023 多 regime 變異使單一參數集
   難以同時優化 Part A/B

## NVDA-011: Capitulation-Depth Filter Mean Reversion (RSI Oscillator Depth)（3 次嘗試全部失敗）

### 動機

NVDA 全域最佳 NVDA-004（BB Squeeze）/ NVDA-006（RS）min(A,B) 皆為 0.47，
NVDA-009（MBPC）/ NVDA-010（ADX/DMI）三類 entry-time 過濾器皆未超越。
NVDA 既有 RSI(2) MR 基線 NVDA-001（RSI(2)<5 + 2日跌幅≤-7%）為極深設定，
Part A 0.07 / Part B 0.14 績效低，從未獲得 IWM-011 風格的中度 RSI(2) +
2DD + ClosePos + ATR + 較窄 SL 的 MR 基線測試機會。

本實驗將 IWM-013 Att3 的「RSI 振盪器深度過濾」方向（repo 第 4 次
capitulation-depth filter 成功，首次以 oscillator depth 替代 raw return
depth）跨資產移植至高波動單一個股 NVDA——repo 首次將「中度 RSI(2) MR
基線 + capitulation-depth filter」應用於 >3% vol 單一個股。

### 三次迭代結果

| 嘗試 | 進場條件 | Part A (n/WR/Sharpe) | Part B (n/WR/Sharpe) | min(A,B) |
|------|----------|----------------------|----------------------|----------|
| Att1 | vol-scaled IWM-011: RSI(2)<10 + 2DD<=-4.5% + ClosePos>=40% + ATR>1.10 + cd 8 | 5/40.0%/**-0.21** | 2/100%/std=0/0.00 | **-0.21** |
| Att2 | Att1 + 3d cap >= -6%（DIA-012/CIBR-012 cap 方向） | 2/50.0%/**-0.01** | 2/100%/std=0/0.00 | **-0.01** |
| Att3 | Att2 + 1d cap >= -4%（DIA-012 dual-dim 跨資產移植） | 1/0.0%/**0.00** | 2/100%/std=0/0.00 | **0.00** |

出場參數：TP +7% / SL -7% / 15 天 / 滑價 0.15%（含成交模型）

### 失敗分析

**Att1 vol-scaled 框架訊號密度不足**：
- 1.0/yr 訊號密度（IWM-011 為 2.0/yr）統計可信度有限
- Part A 5 訊號中 3 SL（2019-04-26 trade-war / 2021-02-23 Feb tech corr /
  2022-09-01 Jackson Hole）皆為 multi-regime continuation traps
- 與 TSLA-014（3.72%）/ FCX-011（3% vol）Post-Cap MR 跨資產失敗模式平行

**Att2 cap 方向部分有效但誤殺贏家**：
- 3d cap 移除 2 SLs（2019-04-26 / 2022-09-01 深 3d continuation）✓
- 但同時誤殺 2022-08-09 TP（也為深 3d capitulation reversal）✗
- 殘留 2021-02-23 SL 為 sharp 1d 急跌（non-prior-3d-buildup），3d cap 無法
  捕獲——需 1d cap 補捉 → Att3

**Att3 dual-dimension cap 結構性錯誤**：
- 1d cap >= -4% 誤殺 2020-01-27 pre-COVID winner（深 1d gap-down）
- **NVDA Part A 高品質 winner（2020-01-27）的 1d 比 SL（2021-02-23）更深**
- DIA-012 cap 方向適用於「Part A losers 集中深 1d gap-down」結構（DIA），
  NVDA winners 為「真實 capitulation 深 1d gap-down」，cap 方向結構**錯誤**
- 與 IWM-013 Att1 失敗模式平行（IWM Part B winners 深 1d gap-down，cap
  方向誤殺贏家）

### 跨資產貢獻

**Repo 第 5 次 capitulation-depth filter 嘗試，首次 >3% vol 高波動單一個股
測試**：

1. **vol-scaled IWM-011 MR framework 不適用 NVDA 高波動 single stock**：
   訊號密度（1.0/yr）不足、multi-regime 使框架隨機化，與 TSLA-014 / FCX-011
   Post-Cap MR 跨資產失敗模式平行——擴展失敗 vol 上限至 NVDA 3.26%

2. **DIA-012 cap 方向結構性不適用 NVDA**：NVDA Part A winners 集中深 1d
   gap-down（與 DIA losers 集中深 1d 結構相反），cap 方向誤殺贏家

3. **Lesson #19 family 邊界擴展**：
   - **raw return cap 方向 vs oscillator depth 方向選擇取決於 winners/losers
     的 raw return 分布**：
       a. SL 集中深 1d/2d/3d → cap 有效（DIA、CIBR、SPY）
       b. winner 集中深 1d/2d/3d → cap 失敗，需 oscillator 維度（IWM、NVDA）
       c. 訊號密度 < 1.5/yr → 兩種維度皆失敗（NVDA-011 confirmation）
   - **capitulation-depth filter 的 vol 上限介於 IWM 1.5-2%（成功）與
     NVDA 3.26%（失敗）之間**

4. NVDA 結構性 Sharpe 上限 ~0.5 再度確認

NVDA-004（BB Squeeze）/ NVDA-006（RS）維持全域最優（11 次實驗、34+ 次
嘗試）。NVDA 第 11 個失敗策略類型（後於 RSI(2) MR、capped DD、BB Squeeze、
BB Optimized、momentum pullback、RS pullback、RS exit opt、RS param、MBPC、
ADX/DMI、Capitulation-Depth Filter）。

---

## NVDA-013: Multi-Week Regime-Aware Momentum Breakout Pullback Continuation ★ 新全域最優

**狀態**：✅ Att3 SUCCESS — repo 首次 lesson #22 cross-strategy 移植
（BB Squeeze → MBPC）+ 首次發現 vol regime 在非 BB Squeeze 框架非冗餘

### 動機

NVDA-009 MBPC baseline（Donchian 20d 近 10 日內新高 + Close>SMA(50) +
5d 淺回檔 [-3%,-8%] + RSI(14) [40,65] + Bullish bar + cd10）三次迭代
全部失敗（Att1 min 0.41 / Att2 0.38 / Att3 0.33），但 **Part B Sharpe
0.96** 顯著高於 NVDA-004 Part B 0.47，證明 MBPC 結構在純趨勢期極有效；
失敗集中於 Part A（11 SLs 散佈於 2020 COVID / 2021 late-bull / 2022 bear
/ 2023 chop）。

NVDA-012 Att2 已驗證 lesson #22 buffered multi-week SMA regime gate
（k=0.97）在 NVDA-004 BB Squeeze 框架成功（min 0.47→0.51）。NVDA-013
測試該 lesson 是否可跨**策略類型**移植至 MBPC 框架。

### 進場條件（Att3 SUCCESS 配置）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | Donchian 突破 freshness | 近 10 日內 High > 前 20 日 Donchian Upper | 動量初啟 |
| 2 | 短期趨勢 | Close > SMA(50) | NVDA-009 繼承 |
| 3 | **多週期趨勢 regime** | **SMA(20) ≥ 1.00 × SMA(60)** | **lesson #22 strict 變體** |
| 4 | **多週期波動 regime** | **ATR(20) ≤ 1.40 × ATR(60)** | **lesson #22 vol regime（MBPC 框架非冗餘）** |
| 5 | 淺回檔 | 5 日高點回檔 ∈ [-8%, -3%] | NVDA-009 繼承 |
| 6 | RSI(14) 中性 | RSI ∈ [40, 65] | NVDA-009 繼承 |
| 7 | 多頭 K 棒 | Close > Open | NVDA-009 繼承 |
| 8 | 冷卻期 | 10 個交易日 | NVDA-009 繼承 |

### 出場參數（同 NVDA-009）

| 參數 | 值 |
|------|------|
| 獲利目標 (TP) | +8% |
| 停損 (SL) | -7% |
| 最大持倉 | 20 天 |
| 滑價 | 0.15%（NVDA 高波動個股） |

### 結果（Att3）

| Part | 訊號數 | 勝率 | 平均報酬 | 累計報酬 | Sharpe | MaxDD |
|------|--------|------|----------|----------|--------|-------|
| Part A (2019-2023) | 26 | **73.1%** | +5.37% | +139.54% | **0.55** | -12.06% |
| Part B (2024-2025) | 7  | **85.7%** | +8.37% | +58.62%  | **2.44** | -6.31%  |

**min(A,B) Sharpe = 0.55**（+8% vs NVDA-012 Att2 全域最佳 0.51，
+34% vs NVDA-009 baseline 0.41）

### A/B 平衡（驗收目標全達）

| 指標 | NVDA-009 baseline | NVDA-013 Att3 | 目標 |
|------|-------------------|---------------|------|
| 年化 cum 差 | 16.9% | **26.4%** | < 30% ✓ |
| 年化訊號比 | 1.7:1 | **1.49:1** | < 50%/1.5:1 ✓ |
| Part A WR | 67.6% | **73.1%** | — |
| Part B WR | 75.0% | **85.7%** | — |

### 迭代歷程

#### Att1（k=0.97 NVDA-012 cross-strategy port）— FAILED min(A,B) 0.38

- 參數：sma_regime_ratio_min = 0.97，vol regime 停用
- Part A: 30/66.7%/Sharpe 0.38 cum +107.15%
- Part B: 8/75.0%/Sharpe 0.96（與 baseline 完全相同，Part B AI bull 不受
  k=0.97 影響）
- **失敗根因**：cooldown chain shift（lesson #19）
  - k=0.97 過濾 4 個 Part A 訊號（34→30），但僅 1 個為 SL（3 個為 TP/expiry）
  - 過濾後續訊號日期 shift 至更差時點，引入新 SLs
  - NVDA-009 MBPC 訊號集（Part A 34 vs BB Squeeze 17）不適用 BB Squeeze
    的 k=0.97 sweet spot

#### Att2（k=1.00 strict, FCX-013 direction）— FAILED min(A,B) 0.41

- 參數：sma_regime_ratio_min 0.97 → 1.00（嚴格無緩衝）
- Part A: 28/67.9%/Sharpe 0.41 cum +106.56%（與 NVDA-009 baseline 持平）
- Part B: 不變（k=1.00 對 Part B AI bull regime 仍無綁定）
- **核心發現**：lesson #22 buffered SMA regime gate 對 MBPC Part A SLs
  缺乏選擇性
  - NVDA Part A 11 SLs 散佈於 2020 COVID（rapid recovery，SMA20>SMA60）
    / 2021 late-bull（uptrend，SMA20>>SMA60） / 2022 bear（少數）/
    2023 chop（boundary）
  - 大部分 SL signal-day 仍 SMA20≥SMA60，與 BB Squeeze SLs 集中 bear
    regime 結構不同
  - 純 SMA regime 過濾**結構性不足**，需引入額外維度

#### Att3 ★（k=1.00 strict + ATR vol regime）— SUCCESS min(A,B) 0.55

- 參數：use_vol_regime False → True，啟用 ATR(20) ≤ 1.40 × ATR(60)
- Part A: 26/**73.1%**/Sharpe **0.55** cum +139.54%（+34% vs baseline 0.41）
- Part B: 7/**85.7%**/Sharpe **2.44** cum +58.62%（+154% vs baseline）
- min(A,B): **0.55**

**vol regime 的精準命中**：
- Part A 過濾 2 訊號（28→26）：精準命中假突破，WR 67.9%→**73.1%**
  （+5.2pp 品質提升）
- Part B 過濾 1 訊號（8→7）：**精準移除 2024-03-15 SL -7.14%**
  （NVDA 2024 Q1 高波動 transition shock）
- Part B Sharpe 0.96→**2.44**（+154%）由 SL 移除產生，6 TPs + 1 expiry
  -0.04% 全部保留

### 跨策略 / 跨資產貢獻

#### 1. lesson #22 cross-strategy 首次擴展至 MBPC 框架

先前三次成功皆於 BB Squeeze：
- **TSLA-015 Att2/Att3**（k=0.99 buffered）：min 0.40→0.53（+33%）
- **NVDA-012 Att2**（k=0.97 buffered）：min 0.47→0.51（+9%）
- **FCX-013 Att3**（k=1.00 strict）：min 0.41→0.55（+34%）

NVDA-013 Att3 為**第 4 次成功**，首次跨**策略類型**至 MBPC（動量延續）。

#### 2. vol regime 冗餘性取決於進場框架的隱含波動限制

| 框架 | 進場波動限制 | vol regime 效用 |
|------|--------------|-----------------|
| BB Squeeze | 顯式（BB Width ≤ 60d 30th pct） | **冗餘**（TSLA-015 Att3 ablation 證實） |
| MBPC | 無顯式波動限制 | **非冗餘**（NVDA-013 Att3 證實，獨立選擇力） |

**新 cross-asset 規則候選**：lesson #22 的 vol regime 適用性需依據進場
框架的 pre-existing volatility constraints 判斷，**非通用結論**。

#### 3. k 值需求差異跨策略

| 策略 | NVDA k 甜蜜點 | 機制 |
|------|----------------|------|
| BB Squeeze + lesson #22 | k=0.97（3% 緩衝） | SMA regime 為唯一過濾器，需精準 transition winner 保留 |
| MBPC + lesson #22 | **k=1.00 strict** | **vol regime 已主導**，SMA regime 嚴格度需求降低 |

#### 4. NVDA 結構性 Sharpe 上限再度突破

| 實驗 | min(A,B) | 累計突破 |
|------|----------|----------|
| NVDA-004 / NVDA-006 | 0.47 | baseline |
| NVDA-012 Att2 | 0.51 | +9% |
| **NVDA-013 Att3** | **0.55** | **+17%** vs NVDA-004 |

NVDA 為 13 次實驗、40+ 次嘗試的成熟標的，multi-regime 高波動個股的策略
成熟度依賴「regime classifier + entry-specific quality gate」的雙層
過濾，純 entry-time filter 已飽和（NVDA-011 confirmation）。

### 關鍵發現整合

1. **NVDA-009 MBPC baseline 的 Part B Sharpe 0.96 為實質潛能上限**：
   NVDA-013 Att3 Part B 進一步提升至 **2.44**（移除唯一 SL），證明
   MBPC 結構在 NVDA AI 牛市期極具高 alpha 屬性

2. **Part A 從 0.41→0.55 的關鍵過濾器為 ATR vol regime（非 SMA regime）**：
   過濾 2 個高 ATR 假突破訊號精準命中品質劣化來源

3. **k=1.00 strict + vol regime 為 MBPC + NVDA 的雙重最優配置**：
   單獨 SMA regime（Att1/Att2）或單獨 vol regime（未測但理論上需要）
   皆不足，**雙重 regime gate 為精準分隔器**

### 後續可能方向（預期邊際效益遞減）

- vol regime ratio 敏感度（1.30 / 1.50 邊界）— 1.40 來自 TSLA-015 直接
  移植，可能存在 NVDA-specific sweet spot
- ATR window 變動（20/60 vs 14/30）— 預期非綁定，window 不影響規範力
- 與 NVDA-006 RS 框架的策略集成（不同訊號日期可分散 regime 風險）—
  超出單一實驗範圍

---

## NVDA-014: Negative Relative Strength Pairs Mean Reversion vs SMH（3 次嘗試全部失敗）

**策略方向：** 配對交易 / 相對均值回歸（Pairs Trading / Relative Mean Reversion）。
repo 第一次以**負向相對強度**（NVDA underperform SMH）作為主訊號的均值回歸實驗。

**動機：** NVDA-006 已驗證**正向 RS** + 淺回檔（動量延續）為可行方向（min 0.47），
本實驗反向探索：當 NVDA 相對 SMH **跑輸**顯著（RS ≤ -3% ~ -5%），疊加深回檔
（≥ 6%），預期為短期 mispricing 而非結構性弱勢。

**驗收目標：**
- min(A,B) Sharpe > 0.55（超越 NVDA-013 Att3）
- A/B 累積年化差距 < 30%
- A/B 訊號比 < 1.5:1（< 50% gap）

### 三次迭代結果

| Att | 主要變更 | Part A | Part B | min(A,B) | 結論 |
|-----|---------|--------|--------|----------|------|
| 1 | RS≤-3% + 10d Pullback≥6% + ATR≤1.40 + cd 12 | 32/65.6%/0.32 | 13/38.5%/-0.25 | **-0.25** | REJECT — Part B 8/13 SL，2024-2025 correction 續跌 |
| 2 | + SMA(20)≥1.00×SMA(60) trend regime（lesson #22） | 17/47.1%/-0.06 | 7/28.6%/-0.49 | **-0.49** | REJECT — lesson #5 驗證（趨勢過濾 + MR = 災難） |
| 3 | RS≤-5% 收緊 + ClosePos≥40%，去 SMA gate | 21/61.9%/0.29 | 6/66.7%/0.34 | **0.29** | REJECT — 仍未達 0.55，但 A/B 平衡達標 |

### 失敗分析（核心發現）

1. **負向 RS 在 AI 主導科技龍頭股為「領先指標」非「mispricing」**：
   NVDA「跑輸 SMH」常為基本面/敘事惡化（earnings 風險、AI sentiment shift、
   宏觀利率調整、tariff 風險）的領先信號，後續續跌而非快速反轉。
   與**正向 RS**（NVDA outperform）的訊號性質**結構性不對稱**：
   - 正向 RS：NVDA outperform → 拉回是對齊回到平衡 → MR 成立
   - 負向 RS：NVDA underperform → 領先板塊向下 → 續跌而非 MR

2. **lesson #5 重新驗證於 pairs MR 框架**：
   「趨勢濾波器 + 均值回歸 = 災難」對「相對均值回歸」（pairs MR）同樣成立。
   SMA(20) ≥ SMA(60) 趨勢 regime 與負向 RS 訊號**本質衝突**——負向 RS 隱含
   SMA 下穿，SMA gate 過濾大量 high-quality MR 機會。

3. **lesson #22 適用方向性精煉**：
   buffered SMA regime gate 之適用性取決於進場框架方向：
   - 同向（trend-following / momentum / breakout-pullback）→ 提升品質
   - 反向（mean reversion / contrarian）→ 移除好訊號（lesson #5 重新驗證）

4. **Att3 ClosePos ≥ 40% 為 Part B 主要救援**：
   Att1 → Att3 Part B Sharpe -0.25 → 0.34（轉正），ClosePos + 收緊 RS
   共同過濾續跌型訊號（Part B 13 → 6 訊號，移除大部分 SL）。
   但 Part A Sharpe 0.32 → 0.29 略降（同樣移除部分淺回檔 winners），
   淨效應未達 NVDA-013 Att3 0.55 上限。

### 跨資產 / 跨方向結論

**配對交易 repo 失敗清單擴展至「同類同權重 + 主訊號方向」：**

| 實驗 | 配對結構 | 失敗模式 |
|------|---------|---------|
| COPX-006 | COPX/FCX（異類商品） | 結構性漂移 |
| XBI-008 | XBI/IBB（同類異權重） | z-score 噪音 |
| SIVR-009 | SIVR/GLD（同類異槓桿） | 結構性漂移 |
| **NVDA-014** | **NVDA/SMH（同類同權重）** | **負向 RS 為領先信號，非 mispricing** |

**配對交易僅在「同類同權重 + 正向 RS 作為過濾器」有效**（NVDA-006、TSM-007、TSLA-007）。

### 配置摘要（Att3 final）

- **進場條件**：
  - NVDA 20d return - SMH 20d return ≤ -5%
  - 10 日高點回檔 ≥ 6%
  - ATR(20) ≤ 1.40 × ATR(60)
  - ClosePos ≥ 0.40
  - 冷卻期 12 個交易日
- **出場參數**：TP +6% / SL -6% / 持倉 15 天 / 滑價 0.15%
- **成交模型**：next_open_market 進場、limit_order/stop_market/expiry 出場、悲觀認定

### 結論

NVDA-014 **未取代** NVDA-013 Att3 為全域最優。NVDA-013 Att3（min 0.55）維持全域
最優（14 次實驗、43+ 次嘗試）。NVDA-014 為 NVDA 第 14 次失敗策略類型，
**repo 首次「負向 RS 主訊號」試驗**，提供 AI 主導科技龍頭股的「跑輸板塊
為領先信號」結構性發現。

## NVDA-015: Multi-Week Regime-Aware Relative Strength Momentum Pullback（3 次嘗試全部失敗）

### 目標 (Goal)

跨**策略類型**首次將 NVDA-013 Att3 的雙重 regime gate（lesson #22 multi-week
SMA regime + ATR vol regime）移植至 NVDA-006 RS Momentum Pullback 框架。
先前 lesson #22 成功僅於 BB Squeeze（TSLA-015/NVDA-012/FCX-013/COPX-011）
+ MBPC（NVDA-013）+ Pullback MR（XBI-015）三類框架，RS Momentum 為第 4 類。

驗收目標：min(A,B) > 0.55（NVDA-013 Att3 全域最佳）。

### 結果摘要

| Att | k_trend | vol regime | Part A 訊號/WR/Sharpe | Part B 訊號/WR/Sharpe | min(A,B) |
|-----|---------|-----------|----------------------|----------------------|----------|
| 1   | 1.00 strict | disabled | 33 / 63.6% / 0.37 | 11 / 81.8% / 0.90 | **0.37** REJECT |
| 2   | 0.97 buffered | disabled | 33 / 63.6% / 0.37（=Att1）| 11 / 81.8% / 0.90 | **0.37** REJECT |
| 3 ★ | 0.97 + ATR≤1.40 enabled | enabled | 28 / 67.9% / **0.48** | 10 / 90.0% / **1.43** | **0.48** REJECT |

vs NVDA-013 Att3 全域最佳 0.55：min 0.48 為 -13%，未達突破目標。
vs NVDA-006 baseline 0.47：min 0.48 為 +2% 微幅改善。

### 核心跨資產 / 跨策略發現

1. **lesson #22 SMA regime 對 RS Momentum 框架結構性冗餘**：
   RS 進場條件（NVDA 20d return - SMH 20d return >= 5%）已隱含 NVDA 處於
   明顯 uptrend regime——20 日 outperformance 幾乎不可能在 SMA20 < SMA60
   bear regime 出現。Att1（k=1.00 strict）vs Att2（k=0.97 buffered）訊號集
   完全相同，證實 RS 框架 signal-day SMA20/SMA60 ratio 全部 >= 1.00，無訊號
   落於 (0.97, 1.00) transition zone。

   **lesson #22 適用框架更新**：

   | 框架 | 進場是否隱含趨勢 | lesson #22 SMA regime | 範例 |
   |------|-----------------|----------------------|------|
   | BB Squeeze | 否（僅波動收縮） | ✓ 提供獨立選擇力 | TSLA-015 / NVDA-012 / FCX-013 / COPX-011 |
   | MBPC | 否（Donchian + 淺回檔） | ✓ 提供部分選擇力 + ATR vol 必要 | NVDA-013 |
   | Pullback MR | 否（深回檔 + WR） | ✓ ATR vol 提供選擇力 | XBI-015 |
   | **RS Momentum** | **✓ 已隱含 uptrend** | **✗ 結構性冗餘** | **NVDA-015** |

   判別準則：「進場條件是否隱含趨勢方向」——隱含 trend 的 entry framework
   （RS 動量、配對 RS 過濾）regime gate 結構性冗餘。

2. **NVDA-013 Att3 ATR vol regime 跨策略移植部分有效**：
   ATR(20) ≤ 1.40 × ATR(60) 對 RS 框架提供 +0.11 Sharpe 改善（0.37→0.48），
   過濾 Part A 5 訊號 + Part B 1 訊號（WR 各 +4.3pp / +8.2pp 提升），但無法
   突破 NVDA-013 0.55——RS 框架 Part A 殘餘 SLs 多為 2021 末段 non-ATR-
   expansion 高位淺回檔後續跌，ATR vol regime 無法捕捉。

3. **NVDA RS framework 結構性飽和**：
   NVDA-014（負向 RS pairs MR）+ NVDA-015（lesson #22 + ATR vol regime）
   兩次 RS framework 子方向 cross-strategy port 均失敗。NVDA-006 Att1
   （min 0.47）為 NVDA RS framework 結構性最佳，NVDA-013 Att3（MBPC 框架）
   仍為 NVDA 全域最佳 0.55。

### 配置摘要（Att3 final）

- **進場條件**：
  - NVDA 20d return - SMH 20d return ≥ 5%
  - 5 日高點回檔在 [3%, 8%]
  - Close > SMA(50)
  - SMA(20) ≥ 0.97 × SMA(60)（**對 RS 框架實際非綁定**）
  - ATR(20) ≤ 1.40 × ATR(60)
  - 冷卻期 10 個交易日
- **出場參數**：TP +8% / SL -7% / 持倉 20 天 / 滑價 0.15%
- **成交模型**：next_open_market 進場、limit_order/stop_market/expiry 出場、悲觀認定

### 結論

NVDA-015 **未取代** NVDA-013 Att3 為全域最優。NVDA-013 Att3（min 0.55）
維持全域最優（15 次實驗、46+ 次嘗試）。NVDA-015 為 NVDA 第 15 次失敗策略
類型，**repo 第 1 次 lesson #22 cross-strategy 移植至 RS Momentum 框架
試驗**，提供 lesson #22 適用框架邊界精煉「進場條件是否隱含趨勢方向」的
判別準則。
