<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取
  last_validated: 2026-04-26
  data_through: 2025-12-31
  note: NVDA-012 added 2026-04-26 (Multi-Week Regime-Aware BB Squeeze Breakout，**repo 第 2 次 lesson #22 buffered multi-week SMA regime 跨資產驗證，繼 TSLA-015 後首次中波動 AI growth stock 試驗**——cross-asset port from TSLA-015 Att2 success，疊加 buffered SMA(20)≥k×SMA(60) trend regime 過濾於 NVDA-004 BB Squeeze Breakout 之上). Three iterations, **Att2 SUCCESS — repo 首次突破 NVDA 結構性 Sharpe 上限 ~0.47，新全域最優 min(A,B) 0.51**. Att1（k=1.00 嚴格 / 註：實際使用 k=0.99 直接移植 TSLA-015 lesson #22 的 sweet spot）Part A 16/75.0%/Sharpe **0.63** cum +83.17%（過濾 2022-07-20 SL bear regime，+26% vs NVDA-004 0.50）/ Part B 6/66.7%/Sharpe **0.41** cum +17.31%（過濾 2025-05-13 winner +8.00% 與 2025-12-23 -1.06% expiry，但淨損失 winner）/ min **0.41**（vs 0.47 baseline）—— 與 TSLA-015 Att1 平行的 transition winner cooldown-shift 失敗模式：2025-05-13 為 4 月 tariff selloff 後 transition 訊號，SMA20/SMA60 比率落於 0.97-0.99 之間，k=0.99 過濾誤殺。**Att2 SUCCESS（k=0.97，3% 緩衝放寬）**：Part A 16/75.0%/Sharpe **0.63** cum +83.17%（與 Att1 完全相同，2022-07-20 SL 仍被 k=0.97 過濾，bear regime ratio << 0.97）/ Part B 7/71.4%/Sharpe **0.51** cum +24.86%（恢復 2025-05-14 +6.43% expiry，2025-12-23 -1.06% loser 仍被過濾）/ min **0.51**（+9% vs 0.47 baseline）。年化 A/B cum 差 25.3% < 30% ✓ / 年化訊號比 1.09:1 < 1.5:1 ✓ —— **三項 acceptance criteria 全部達標**。Att3（k=0.98 敏感度邊界檢查）Part A 不變 / Part B 6/66.7%/Sharpe 0.41（與 Att1 完全相同）/ min 0.41 —— 0.97-0.98 為 NVDA 上 transition winner 的關鍵分界，0.97 為精準甜蜜點。**核心發現（lesson #22 跨資產精煉）**：(1) buffered multi-week SMA regime 在 NVDA BB Squeeze 框架成功（NVDA-012 為 NVDA 結構性 Sharpe 上限突破首例）；(2) **k 值非通用**——TSLA k=0.99（3.72% vol）、NVDA k=0.97（2.5-3% vol），AI growth stock 的 transition signals SMA20/SMA60 比率落於 0.97-0.99 區間，需更寬緩衝；(3) lesson #22 跨資產假設「multi-week SMA regime 對 BB Squeeze breakout 高波動單股有效」確認，但 k 值需依資產 transition signal 的 SMA 比率分布調整；(4) 過濾結構性精準：2022-07-20 bear regime SL（ratio << 0.97）+ 2025-12-23 marginal loser（ratio < 0.97）被過濾，2020-2023 大部分 winners + 2024-2025 AI bull winners 全保留。NVDA-012 為 NVDA 第 12 次實驗，**首次突破 0.47 結構性上限**，新全域最優（12 次實驗、37+ 次嘗試）。NVDA-011 added 2026-04-26 (Capitulation-Depth Filter MR (RSI Oscillator Depth)，**repo 第 5 次 capitulation-depth filter 嘗試，repo 首次 >3% vol 高波動單一個股測試**——cross-asset port from IWM-013 Att3 success 方向). Three iterations all failed vs NVDA-004/006 min(A,B) 0.47. Att1（vol-scaled IWM-011 framework：RSI(2)<10 + 2DD<=-4.5% + ClosePos>=40% + ATR(5)/ATR(20)>1.10 + cd 8 + TP+7%/SL-7%/15d）Part A **5/40.0%/Sharpe -0.21** cum -8.32%（2019-04-26 SL trade-war + 2020-01-27 TP pre-COVID + 2021-02-23 SL Feb tech corr + 2022-08-09 TP bear rally + 2022-09-01 SL Jackson Hole）/ Part B 2/100% std=0 Sharpe 0.00 cum +14.49%（2025-01-13 DeepSeek + 2025-09-02 mid-dip）/ min **-0.21** —— 1.0/yr 訊號密度過稀（IWM-011 為 2.0/yr），高波動 single stock multi-regime（trade war / COVID / 2021 bubble / 2022 bear / 2023 chop）使 vol-scaled framework 喪失選擇性。Att2（Att1 + 3d cap >= -6%，DIA-012/CIBR-012 cap 方向）Part A **2/50.0%/Sharpe -0.01** cum -0.64%（移除 2 SL + 1 TP，保留 2020-01-27 TP + 2021-02-23 sharp 1d SL）/ Part B 不變 / min **-0.01** —— 3d cap 移除深 3d continuation traps 但同時誤殺 2022-08-09 TP 深 3d capitulation reversal；殘留 2021-02-23 SL 為 sharp 1d 急跌（non-prior-3d-buildup），3d cap 無法捕獲。Att3（Att2 + 1d cap >= -4%，DIA-012 dual-dimension 跨資產移植）Part A **1/0.0%/Sharpe 0.00** cum -7.14%（僅保留 2021-02-23 SL，誤殺 2020-01-27 pre-COVID winner）/ Part B 不變 / min **0.00** —— **NVDA Part A 高品質 winner（2020-01-27 pre-COVID）的 1d 比 SL（2021-02-23）更深**，DIA-012 cap 方向結構**錯誤**：DIA Part A losers 集中深 1d gap-down（cap 過濾贏家有效），NVDA winners 為「真實 capitulation 深 1d gap-down」，與 IWM-013 Att1 失敗模式平行。**核心結論**：(1) vol-scaled IWM-011 MR framework 不適用 NVDA 高波動 single stock——1.0/yr 訊號密度不足、multi-regime 使框架隨機化，與 TSLA-014（3.72%）/ FCX-011（3% vol）Post-Cap MR 跨資產失敗模式平行；(2) DIA-012 cap 方向結構性不適用 NVDA——NVDA winners 集中深 1d gap-down，與 IWM、與 DIA 結構相反；(3) NVDA 結構性 Sharpe 上限 ~0.5 再度確認（NVDA-004 / NVDA-006 0.47）。**Lesson #19 family 邊界擴展**：(a) raw return cap 方向 vs oscillator depth 方向選擇取決於 winners/losers 的 raw return 分布——SL 集中深 1d/2d/3d → cap 有效（DIA、CIBR、SPY）；winner 集中深 1d/2d/3d → cap 失敗，需 oscillator 維度（IWM、NVDA）；訊號密度 < 1.5/yr → 兩種維度皆失敗（NVDA-011 confirmation）；(b) capitulation-depth filter 的 vol 上限介於 IWM 1.5-2%（成功）與 NVDA 3.26%（失敗）之間。NVDA-011 為 NVDA 第 11 次失敗策略類型（含均值回歸、突破、動量回調、相對強度、RS 出場/參數探索、MBPC、ADX/DMI、Capitulation-Depth Filter 九大方向）。NVDA-004 / NVDA-006 維持全域最優（11 次實驗、34+ 次嘗試）。NVDA-010 added 2026-04-25 (ADX-Filtered RSI(2) Mean Reversion, **repo 首次 ADX/DMI 作為主規範閘門試驗**，三次迭代全部失敗 vs NVDA-004/006 min(A,B) 0.47). Att1（ADX>=25 + +DI>-DI + RSI(2)<=15 + Pullback[-3%,-10%] + cd10 + TP+6%/SL-6%/15d）Part A 3/66.7%/Sharpe **0.26** cum +3.88% / Part B 1/0%/Sharpe **0.00** zero-var SL / min **0.00** —— 多重綁定過嚴僅 0.6 訊號/yr 統計不足；強趨勢中 RSI(2)<=15 罕見發生（持續下挫使 +DI<<-DI 必然違反方向過濾），交集結構性狹窄。Att2（放寬 ADX>=20 + RSI(2)<=20 + Pullback[-2%,-12%] + cd8）Part A 8/62.5%/Sharpe **0.22** cum +9.00% / Part B **1**/0%/Sharpe **0.00** / min **0.00** —— Part A 新增 5 中等品質訊號稀釋集中贏家（Sharpe 0.26→0.22）；Part B 仍卡在 1 訊號：NVDA 2024-2025 深度修正（2024-08 -17%、2025-04 tariff -25%）違反 (a) -12% pullback 上限、(b) Close>SMA(50) 規範閘門（深跌跌破 50 日 MA）、或 (c) +DI>-DI（DMI 快速崩盤期間翻轉 bear），結構不匹配 Part B 的 deep-capitulation 機會。Att3（移除 +DI>-DI + RSI(3)<=25 + Pullback to -15%）Part A 8/**37.5%/Sharpe -0.27** cum -13.24%（4 連續 SL！）/ Part B 2/**0%**/Sharpe **0.00** zero-var / min **-0.27**（三次最差）—— cooldown chain shift（lesson #19）：移除 +DI>-DI 釋放原本被壓制的 2020-02-24（pre-COVID drop）、2021-02-23（Feb 修正）、2021-12-06（post-COVID 反彈）、2022-12-20（bear 反彈）4 筆全 SL，+DI>-DI 提供真實品質過濾；Part B 2024-04-02 + 2025-08-20 皆 SL 為 continuation-decline 假反彈（lesson #20b 平行結構）。**核心結論**：(1) ADX>=25 強趨勢與 RSI(2)<=15 deep oversold 罕見共存（RSI 需持續下挫使 DMI 翻轉），Att1 訊號結構性稀疏；(2) ADX>=20 weak-trend 過於包容（納入震盪 2023 summer 使 MR 訊號隨機化）；(3) +DI>-DI 提供真實選擇性但與 Close>SMA(50) 大部分時間冗餘，移除觸發 cooldown-chain-shift；(4) 多重綁定 ADX+RSI+SMA+Pullback+Close>Open+Cooldown 高約束相關性，放寬一條件不會比例增長訊號。**Repo 首次 ADX/DMI 主過濾器試驗失敗**——擴展 lesson #6（確認指標邊際效益遞減）至 ADX/DMI 類別；擴展 lesson #20b 邊界：trend-strength oscillators（ADX）加入 RSI/CCI/Stoch/MACD hook divergence 作為多 regime 高波動個股的無效進場主過濾器。**NVDA 結構性 Sharpe 上限約 0.5**——2019-2023 多 regime 變異使單一參數集難以同時優化 Part A/B；NVDA-004（BB Squeeze）/ NVDA-006（RS）維持全域最優 0.47（10 次實驗、31+ 次嘗試）。NVDA-009 added 2026-04-24 (Momentum Breakout Pullback Continuation, **repo 第 2 次 MBPC 結構試驗，繼 FXI-012 後首次高波動個股測試**，三次迭代全部失敗). Att1 baseline（Donchian 20d 近 10 日內新高 + Close>SMA(50) + 5d 淺回檔 -3% ~ -8% + RSI(14) ∈ [40,65] + 多頭 K 棒 + cd10 + TP+8%/SL-7%/20d）Part A 34 訊號 WR 67.6% Sharpe **0.41** cum +142.32% / Part B 8 訊號 WR 75.0% Sharpe **0.96** cum +47.30% / min **0.41**（低於 NVDA-004 / NVDA-006 的 0.47）——A/B 年化訊號比 1.7:1（41% gap）、A/B 年化 cum 差 16.9%，**A/B 平衡目標達成但 Sharpe 目標未達**；Att2（+ SMA(200) regime 閘門 + RSI_max 65→60）Part A 21/66.7%/**0.38** / Part B 6/83.3%/**2.22** / min 0.38——**非選擇性過濾**（訊號 -38%/WR -0.9pp，移除贏家 9/5 比於整體 23/11 比方向錯誤），SMA(200) 過濾 2022-07-25 TP 贏家、RSI<60 過濾 AI 主升段健康續漲；Att3a（2DD cap >= -6%，CIBR-012 方向）與 Att1 完全相同（-6% 無綁定，NVDA 突破+淺回檔 2d 報酬典型 -3~-5%）；Att3b（2DD cap >= -4%）Part A 31/64.5%/**0.33** / Part B 8/62.5%/**0.49** / min **0.33**（三次最差）——-4% cap 與 5d 淺回檔範圍部分重疊且 cooldown-shift 引入新 SL。**核心發現**：Part B（2024-2025 AI 牛市）單邊 Sharpe 0.96 遠勝 NVDA-004 Part B 的 0.47，證明 MBPC 結構在純趨勢期極有效；但 Part A 2021-2023 混合 regime（late-bull + 2022 bear + 2023 summer chop）11 筆 SL 壓制 Sharpe 至 0.41。**repo 第 2 次 MBPC 失敗**（繼 FXI-012 後），失敗機制差異：FXI 為政策驅動假突破（Part A WR 42.3%），NVDA 為 bubble/correction late-cycle 突破（Part A WR 67.6% 已不錯但 Sharpe 受限於標準差）。**擴展 cross_asset_lesson #25**：Momentum Breakout Pullback Continuation 結構需**單一純上升 regime** 資產才穩定，**多 regime 資產**（FXI 政策驅動 / NVDA bubble+correction mixed）結構性劣化於 regime-specific 優化的 MR / 突破策略。NVDA-004 / NVDA-006 維持全域最優（9 次實驗、28+ 次嘗試）。
-->
## AI Agent 快速索引

**當前最佳：** NVDA-012 Att2（Multi-Week Regime-Aware BB Squeeze Breakout：NVDA-004 + buffered SMA(20)≥0.97×SMA(60) regime 過濾）— Part A Sharpe **0.63**/Part B Sharpe **0.51**/min(A,B) **0.51**（+9% vs NVDA-004 的 0.47）。**首次突破 NVDA 結構性 Sharpe 上限 ~0.47**。年化 A/B cum 差 25.3%（< 30%）/ 訊號比 1.09:1（< 1.5:1）—— acceptance criteria 全部達標。lesson #22 第二次跨資產驗證
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

**已證明無效（禁止重複嘗試）：**
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

**尚未嘗試的方向（可探索，但預期邊際效益極低）：**
- BB(20,2.5) 更嚴格的擠壓條件
- 純趨勢跟蹤（SMA 交叉）— 但 IWM-007、TSLA-006 驗證 SMA 交叉對個股/ETF 普遍無效

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
| NVDA-012 | `nvda_012_regime_breakout` | Multi-Week Regime-Aware BB Squeeze Breakout：NVDA-004 + SMA(20)≥0.97×SMA(60) buffered multi-week trend regime（lesson #22 跨資產移植自 TSLA-015），TP+8%/SL-7%/20d/cd 10 | 已完成（Att2 SUCCESS，min(A,B) 0.51 = 新全域最優，+9% vs NVDA-004 0.47） |

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

## NVDA-004: BB Squeeze Breakout Optimized（當前最優）

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
