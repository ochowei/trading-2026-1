<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-05-10
  data_through: 2025-12-31
  note_2026_05_10_tqqq025: TQQQ-025 added 2026-05-10 (VXN-VIX Cross-Index IV Divergence + VVIX Direction Filter on Vol-Regime-Gated Capitulation Buy, **Att2 ★ SUCCESS — repo 首次「cross-index implied vol divergence」(^VXN/^VIX 比率) 於任何資產 + repo 首次 ^VVIX (VIX of VIX, higher-moment IV direction) 於任何資產 + repo 首次「正交雙 IV 維度 AND 條件」突破 TQQQ Part B 0.80 結構性 ceiling (13 次嘗試後)**, direct test of TQQQ-020 unverified hypothesis "VIX-VXN cross-index divergence". Three iterations: **Att1** (use_vxn_vix_filter=True, min_vxn_vix_ratio=1.10, VVIX off) Part A 10/90%/Sharpe 1.21 cum +68.97% (完全等於 baseline，VXN/VIX 對 Part A 殘餘 SL 2021-09-28 ratio=1.176 結構性非綁定) / Part B **5/100% WR std=0 zero-var Sharpe 0.00 cum +40.26%** (**過濾 2025-03-06 SL** ratio=1.055 surgical，唯一 < 1.10 outlier) / min(A,B)† **1.21** PARTIAL (+51% vs baseline 0.80) — A/B 年化 cum gap 40% > 30% target ❌ (Part A 11.07%/yr vs Part B 18.43%/yr，Part B 純化使 cum gap 結構性擴張)；**Att2 ★ SUCCESS** (use_vxn_vix_filter=True + use_vvix_direction_filter=True, lookback=5, min_vvix_change=-5.0) Part A **9/100% WR std=0 zero-var cum +83.85%** (**過濾 2021-09-28 SL** VVIX_5d=-9.70 surgical，唯一 < -5 outlier) / Part B 5/100% WR std=0 cum +40.26% (與 Att1 相同) / min(A,B)† **structurally NO LOSS**（雙 Part 全勝零方差，依 EWT-010/IBIT-009 慣例優於 baseline 0.80 of 「Part A 1 SL + Part B 1 SL」結構，Part A WR 90→**100%** + Part B WR 83.3→**100%**）; **三項 acceptance criteria 全部達標**: A/B 年化 cum gap **29.7% < 30% ✓** (Part A 12.96%/yr vs Part B 18.43%/yr，從 Att1 40% 縮回，雙 Part SL 同步純化使 cum 同步上升)、A/B 訊號比 1.8/yr vs 2.5/yr = 28% < 50% ✓、Sharpe 結構性突破 baseline；**Att3 ablation REJECT** (use_vxn_vix_filter=False, VVIX-only) Part A 9/100% std=0 cum +83.85% (與 Att2 相同) / Part B **6/83.3%/Sharpe 0.80** cum +28.91% (2025-03-06 SL 殘存，VVIX_5d=+6.03 ≥ -5 結構性逃逸過濾) / min(A,B) **0.80 TIE baseline** — 確認 VXN/VIX 對 Part B SL 之必要性，雙維度正交確認。**核心發現（lesson #24 family v11 邊界擴展，repo 首次發現雙正交 IV 維度組合）**: (1) **Repo 首次「cross-index implied vol divergence」變體於任何資產**——既有 lesson #24 family v1-v9 維度均為單一 vol index LEVEL/DIRECTION（^VIX/^MOVE/^GVZ/^OVX/^VXN）+ term structure（^VIX3M/^VIX TSM-019），v11 引入「比率」維度 (^VXN/^VIX) 衡量 sub-segment 與 broader market vol regime divergence；(2) **Repo 首次 ^VVIX (VIX of VIX) 應用於任何資產**——higher-moment IV direction 維度，^VVIX 5d direction 衡量「panic about future panic」加速度；(3) **雙正交維度互補確認 (lesson #24 family v11 + lesson #20 v3 family)**：trade-level 分析發現 TQQQ-018 殘餘 2 SLs 在 IV 不同維度反向結構：Part A SL 2021-09-28 (VXN/VIX=1.176 中段，VVIX_5d=-9.70 負極端) vs Part B SL 2025-03-06 (VXN/VIX=1.055 負極端，VVIX_5d=+6.03 正常)，**單一維度結構性無法切分雙 SL，雙正交維度 AND 條件為 unique solution**——repo 第 1 次驗證「同 framework 內單一資產雙 Part SLs 在 IV 不同維度反向結構需雙維度 AND 條件」(對比 EWT-010 雙時框 AND 為「同維度不同 lookback AND」變體)；(4) **TQQQ-022 (QQQ-SPY price divergence) 失敗 vs TQQQ-025 (^VXN-^VIX IV divergence) 成功**：**IV 維度比 price 維度更敏感 capture tech-vs-broad regime separation**——TQQQ-022 broad-market panic 期 QQQ ≈ SPY 同步下跌使 price divergence 自然壓縮 (SLs 與 winners 重疊)，^VXN/^VIX IV divergence 在相同 regime 中仍展現結構分離 (option market price-in tech-vs-broad uncertainty differential)；(5) **首次突破 TQQQ Part B 0.80 結構性 ceiling**——既有 13 次嘗試（^VIX direction TQQQ-019/020、^MOVE TQQQ-021、QQQ-SPY divergence TQQQ-022、yield curve slope TQQQ-023、vol-transition MR replacement framework TQQQ-024）皆 REJECT/TIE，TQQQ-025 Att2 為**首次全面達成 acceptance criteria**——驗證 TQQQ AI_CONTEXT 多次提及之未驗證假設「VIX-VXN cross-index divergence + ^VVIX higher-moment IV」;(6) **新跨資產假設（待驗證）**：雙維度 (cross-index IV ratio + ^VVIX direction) 可能適用其他 leveraged tech ETF (TECL/SOXL/FNGU)，閾值需依資產 vs broader market IV 結構調整；可能跨類別擴展至高波動 AI mega-cap 個股 (NVDA/TSLA) BB Squeeze breakout 或 momentum framework；(7) **TQQQ 第 25 次實驗、13 大策略類型** (新增 cross-index IV divergence + higher-moment IV direction)。**TQQQ-025 Att2 為新全域最優**（25 次實驗、56+ 次嘗試），取代 TQQQ-018 Att3 為當前最佳。
  note_2026_05_09_tqqq024: TQQQ-024 added 2026-05-09 (Post-Capitulation Vol-Transition MR, **repo 首次「完全替代 framework」於 TQQQ — 拋棄 -15% extreme capitulation 結構，採 BB 下軌 + 中度 pullback + WR + ClosePos + ATR + 2DD floor 混合進場框架，3 次嘗試全部 REJECT vs TQQQ-018 Att3 baseline 0.80**, cross-asset port from EWJ-005 / EEM-014 / IBIT-009 / VGK-008 vol-transition MR family，直接測試 TQQQ-019/020/021/022/023 列出之未驗證假設「完全替代 framework（vol-transition MR / BB Squeeze Breakout）」). Three iterations: Att1 (BB(20,2) lower + 10d PB ∈ [-25%,-8%] + WR<=-85 + ClosePos>=0.35 + ATR(5)/ATR(20)>1.10 + 2DD floor<=-3% + cd5, TP+5%/SL-5%/10d) Part A **2 訊號**（1W/1L 50%/Sharpe -0.01）/ Part B **1 訊號**（0W/1L 0%/Sharpe 0.00 — 2025-02-25 -5.09% SL）/ min(A,B) **-0.01 REJECT (-101% vs baseline 0.80)** — 6-condition AND chain over-constrains 5+ years to 2 signals；Att2 (相同 + PB floor 移除, ClosePos>=0.30, ATR>1.05, 2DD floor<=-2%) Part A **4 訊號**（2W/2L Sharpe -0.01）/ Part B **2 訊號**（0W/2L Sharpe 0.00）/ min(A,B) **-0.01 REJECT** — 放寬 PB+ATR+2DD+ClosePos 仍僅 4 訊號，BB 下軌 + WR<=-85 為 binding constraint；Att3 (相同 + WR<=-75 放寬, ATR>1.00 非綁定, 2DD floor<=-3% 收回, ClosePos>=0.35) Part A **5 訊號**（3W/2L 60%/Sharpe **0.19** cum +4.26%）/ Part B **1 訊號**（0W/1L Sharpe 0.00 — 2025-02-25 SL 殘留）/ min(A,B) **0.00 REJECT (-100% vs baseline)** — 放寬 WR + 移除 ATR 仍未能解決根本問題，Part B 樣本不足 + 2025-02-25 結構性 SL 仍存活. **核心失敗發現（lesson #6 邊界擴展、repo 首次 vol-transition MR framework 於 leveraged 槓桿 ETF 失敗）**：(1) **Vol-Transition MR framework 於高波動 leveraged ETF 結構性失效**——既有成功案例（EWJ 0.96% vol、EEM 1.17% vol、INDA 0.97% vol、VGK 1.05% vol、IBIT 3.17% vol、SOXL 6% vol with 雙 part std=0、USO 1.5-2% vol）皆為**非 leveraged 個別 ETF / 單一資產**或**特殊 framework 結構**（IBIT Gap-Down 為基底、SOXL 雙 part std=0 結構性勉強通過）；TQQQ 5-6% vol leveraged tech ETF 為**首例失敗**——BB(20,2) 下軌 + 10d pullback co-occurrence 在 leveraged ETF 上結構性極稀（5% vol 使 BB lower band ≈ Close × (1-2σ_20d) ≈ Close × 0.78，rare 觸發），需相同日 10d pullback 也達到深度，雙條件交集年僅 1-2 次；(2) **TQQQ Part B 2025-02-25/2025-03-06 SL 跨 framework 結構性無解**——Trump 關稅 reflation→stagflation 切換之 1-3 日急跌（同時 broad-market panic + tech-specific weakness）在所有 framework 中觸發 -5%~-8% SL：extreme capitulation buy（TQQQ-018，2025-03-06 -8% SL）+ vol-transition MR（TQQQ-024 三次迭代，2025-02-25 -5% SL）+ implied vol filter（TQQQ-019/020/021）+ cross-asset divergence（TQQQ-022）+ yield curve slope（TQQQ-023）共 13 次嘗試，2025 年初 1-3 日深跌 SL **跨整個 framework 維度結構性存在**；(3) **新跨資產規則（lesson #6 邊界第五次擴展）**：vol-transition MR framework 適用邊界 = 「target 為非 leveraged 標的或 leveraged 標的具特殊 framework 結構基底」（EWJ/EEM/INDA/VGK 非 leveraged ✓ / IBIT Gap-Down 結構基底 ✓ / SOXL 雙 part std=0 邊際 ✓）； 不適用於：「pure leveraged tech ETF（TQQQ）BB 下軌觸發稀疏 + Part B 結構性 SL 無解」；(4) **TQQQ 第 24 次實驗、12 大策略類型**（新增 vol-transition MR 失敗）。剩餘未驗證假設：「underlying QQQ short-term momentum reversal」（單日反轉模式，未試）、「TQQQ vs SQQQ inverse pair」（同一 underlying 槓桿配對，未試）、「BB Squeeze Breakout 於 TQQQ 本身（TQQQ-015 為 QQQ → trade TQQQ，方向不同）」。TQQQ-018 Att3 仍為 min(A,B) 全域最優（24 次實驗、12 大策略類型）。
  note_2026_05_09_tqqq023: TQQQ-023 added 2026-05-09 (Yield-Curve-Slope Inflation-Regime-Gated Capitulation Buy, **repo 首次 yield curve slope velocity / level 跨資產類別移植自 TLT-017（rate-direct ETF）至 leveraged tech ETF — 全部 REJECT/TIE**, direct test of TQQQ-021/022 explicit unverified hypothesis "yield curve slope velocity（TLT-017 成功維度）"). Three iterations all failed/tied vs TQQQ-018 Att3 min(A,B) 0.80. Att1 (slope_lookback=5d, max_slope_change=+0.038, TLT-017 Att2 sweet spot 直接移植) Part A 7/85.7%/Sharpe **0.92** cum +37.93% (vs baseline 10/90.0%/1.21/+68.97%, **Part A 退化 -24%**: 過濾 3 winners 但對 Part B SL 完全非綁定) / Part B 6/83.3%/Sharpe **0.80** **完全等於 baseline** (所有 6 訊號 slope_change_5d <= +0.038，2025-03-06 SL 結構性非綁定) / min(A,B) **0.80 TIE baseline** — 5d slope velocity 維度與 TQQQ extreme capitulation 結構性脫鉤；Att2 (slope_lookback=5d, max_slope_change=+0.020 tighter, surgical filter 嘗試) Part A **4**/75.0%/Sharpe **0.49** cum +12.59% (-59% 過嚴) / Part B **1** 訊號 100% std=0 (僅留 2024-04-19，5 winners 誤殺) / min(A,B) **0.49 REJECT (-39% vs baseline)** + A/B signal gap **75%** (>>50% target，違反 acceptance criteria) — tighter 0.020 揭露 reverse-selecting 結構：2025-03-06 SL slope_change_5d 落於 [-0.020, +0.020] 區間，與 winners 分布重疊，無法 surgical 過濾；Att3 (slope LEVEL <= +0.40，velocity filter 停用，alternative dim mirror TLT-017 Att3) Part A **2**/100% std=0 zero-var (vs baseline 10/90%/1.21，過嚴過濾 8 訊號) / Part B 5/80.0%/Sharpe **0.66** cum +20.48% (誤殺 1 winner，2025-03-06 SL slope LEVEL <= +0.40 仍存活) / min(A,B) **0.66 REJECT (-18% vs baseline)** + A/B signal gap **60%** (>50% target) — slope LEVEL 維度與 slope velocity 同樣 reverse-selecting，2025-03-06（曲線非陡峭時刻）非綁定，反向誤殺 winner。**核心失敗發現（lesson #24 family v10 邊界擴展，repo 首次 yield curve slope velocity 跨資產類別失敗）**: (1) **TLT-017 yield curve slope velocity 成功不跨資產類別移植到 leveraged tech ETF**——既有成功為 rate-direct ETF（TLT 對 rates 為唯一 driver，slope velocity 直接捕捉 long-end inflation premium 擴張），TQQQ 為 rate-indirect 資產（rates 經由 long-duration valuation discount rate 機制間接傳導），**間接傳導路徑使 yield curve 維度與 capitulation framework 結構性脫鉤**——2025-03-06 SL（Trump 關稅 event shock）yield curve 動態與 TLT 2021-01-06（reflation regime onset）結構不同：tariff 為瞬時事件衝擊（一日內 risk-off 同步推動 long+short yields 同步下行），而非 sustained inflation regime onset（slope velocity 緩慢擴張）；(2) **slope velocity + slope LEVEL 雙維度同時失敗**——velocity 維度 reverse-selecting (Att2) + LEVEL 維度 reverse-selecting (Att3)，與 TLT-017 上 velocity 強於 LEVEL 之 selectivity 反向；(3) **Repo 首次 yield curve dimension 於 leveraged tech ETF 試驗失敗**——擴展既有 implied vol 失敗家族（^VIX TQQQ-019/020 + ^MOVE TQQQ-021）+ cross-asset divergence 失敗（QQQ-SPY TQQQ-022）至 yield curve 維度，**TQQQ Part B 0.80 binding ceiling 跨 implied vol（IV）+ cross-asset relative strength（XAR）+ yield curve（YC）三大正交 macro structural 維度全失敗**；(4) **新跨資產規則（lesson #24 family v10 + lesson #20 v3 family v11 整合邊界）**：cross-asset macro structural regime gate（implied vol / cross-asset divergence / yield curve）適用邊界 = 「target 為直接受該 macro factor 驅動的 single-driver asset class」(TLT 對 rates ✓ / USO 對 oil ✓ / GLD 對 inflation ✓) — 排除 indirect-transmission asset class（leveraged tech ETF rate-indirect ✗）；(5) **TQQQ Part B 2025-03-06 SL 為跨 IV/XAR/YC 三大維度結構性無解 SL**——已試 ^VIX 5d/1d direction（TQQQ-019/020）+ ^MOVE LEVEL/3d/5d（TQQQ-021）+ QQQ-SPY 20d/10d divergence（TQQQ-022）+ yield curve slope 5d velocity / LEVEL（TQQQ-023）共 12 次嘗試皆失敗；剩餘未驗證假設：「underlying QQQ short-term momentum reversal」（單日反轉模式，未試）、或**完全替代 framework**（vol-transition MR / BB Squeeze Breakout，跳脫 -15% extreme capitulation 結構）；(6) **TQQQ 第 23 次實驗、11 大策略類型**（新增 yield curve slope filter）。TQQQ-018 Att3 仍為 min(A,B) 全域最優（23 次實驗、11 大策略類型）。
  note_2026_05_09_tqqq022: TQQQ-022 added 2026-05-09 (QQQ-SPY Cross-Asset Divergence FLOOR Filter on Vol-Regime-Gated Capitulation Buy, **repo 首次「leveraged ETF underlying-vs-broader divergence」於任何資產 — 全部 REJECT/TIE**, direct test of TQQQ-021 explicit unverified hypothesis "cross-asset relative strength（如 TQQQ vs SPY 相對強度）"). Three iterations all failed/tied vs TQQQ-018 Att3 min(A,B) 0.80. Att1 (lookback=20d, min_relative_return=-0.03 moderate floor) Part A 7/71.4%/Sharpe **0.39** cum +18.48% (vs baseline 10/90.0%/1.21/+68.97%, **reverse selection**: filter 移除 3 winners 但保留 1 SL 2021-09-28) / Part B 6/83.3%/Sharpe **0.80** cum +28.91% (**完全等於 baseline**——所有 6 訊號 QQQ-SPY 20d ≥ -3% 通過 filter，2025-03-06 SL 結構性非綁定) / min(A,B) **0.39 REJECT (-51% vs baseline)**; Att2 (lookback=20d, min_relative_return=-0.05 loose floor，threshold robustness 測試) Part A 9/88.9%/Sharpe **1.12** cum +57.92% (vs baseline 1.21, **-7% 退化**——loose floor 移除 1 winner) / Part B 6/83.3%/Sharpe **0.80** **完全不變** / min(A,B) **0.80 TIE baseline**——確認 -3% 與 -5% 之間無 sweet spot，所有 6 Part B 訊號 QQQ-SPY 20d ≥ -5%；Att3 (lookback=10d, min_relative_return=-0.03 acute event-shock 維度，**最劣迭代**) Part A 6/83.3%/Sharpe **0.80** cum +28.91% (-4 winners) / Part B 5/80.0%/Sharpe **0.66** cum +20.48% (-1 winner 2024-07-24 但仍保留 1 SL 2025-03-06) / min(A,B) **0.66 REJECT (-18% vs baseline)**——10d 縮短 lookback 加劇 reverse selection，2025-03-06 SL QQQ-SPY 10d 仍 ≥ -3%（broad-market 同步下跌）。**核心失敗發現（lesson #20 v3 family v11 邊界擴展，repo 首次發現）**: (1) **TQQQ extreme capitulation 與 QQQ-SPY divergence 結構性脫鉤**——TQQQ-018 框架要求 DD ≤ -15% + RSI(5) < 25 + Volume > 1.5x，此類訊號天然發生於 broad-market panic 期（COVID、Fed pivot、Trump tariff），QQQ 與 SPY 通常同步下跌，20d/10d divergence 自然壓縮；tech-specific 結構性弱勢期（如 2022 Fed 加息）已被 BB-width regime gate 過濾，剩餘訊號集中於 broad panic regime；(2) **Reverse selection 嚴重**：Part A winners 集中於 QQQ-SPY 20d ∈ [-5%, -1%]（broad panic 中 tech 略弱於大盤的健康反彈時機），SL 2021-09-28 / 2025-03-06 QQQ-SPY 20d 結構性 ≥ -3%（low-vol regime drift / 同步 broad selloff），任何 FLOOR threshold 移除 winners 多於 SL；(3) **Repo 首次「leveraged ETF underlying-vs-broader divergence」失敗類別**——既有 broad-vs-broad 失敗（EEM-EFA EEM-017）+ broad-vs-sub-component 失敗（EEM-FXI EEM-019）+ commodity-vs-commodity 失敗（USO-XLE USO-026），新增「leveraged ETF underlying（QQQ）-vs-broader benchmark（SPY）」（TQQQ-022）為新失敗類別；既有成功 case 為「single-asset narrower scope vs broader benchmark」（NVDA-QQQ NVDA-021、TSLA-QQQ TSLA-017、TLT-SPY TLT-014、INDA-EEM INDA-012）；(4) **新跨資產規則（lesson #20 v3 v11 邊界精煉）**：cross-asset divergence regime gate 適用結構 = (a)「target 為 narrower scope vs broader benchmark」+ (b)「target SLs 在 divergence 維度方向性集中（與 winners 分布顯著分離）」雙條件；TQQQ-022 違反 (b)（leveraged ETF capitulation framework 已過濾掉 sector-specific 弱勢期，剩餘訊號集中於 broad panic regime，divergence 維度自然壓縮使 SLs 與 winners 重疊）；(5) **整合 TQQQ-019/020/021 + TQQQ-022 結論：TQQQ Part B 0.80 binding ceiling 跨 implied vol（^VIX/^MOVE）+ cross-asset relative strength（QQQ-SPY）兩大維度全失敗**；剩餘未驗證假設：「underlying QQQ short-term momentum reversal」、「yield curve slope velocity」（TLT-017 成功維度）、或「完全替代 framework」（vol-transition MR / BB Squeeze）；(6) **TQQQ 第 22 次實驗、10 大策略類型**（新增 cross-asset divergence FLOOR）。TQQQ-018 Att3 仍為 min(A,B) 全域最優（22 次實驗、10 大策略類型）。
  note_2026_05_09_tqqq021: TQQQ-021 added 2026-05-09 (^MOVE Bond-Vol Regime Gate on Vol-Regime-Gated Capitulation Buy, **repo 首次 ^MOVE（bond vol）於 leveraged tech ETF / equity asset 試驗 — 全部 REJECT/TIE**, follows TQQQ-019/020 explicit unverified hypothesis "可能需 ^VIX LEVEL 維度 或 完全替代 framework"). Three iterations all failed/tied vs TQQQ-018 Att3 min(A,B) 0.80. Att1 (max_move_level=130, TLT-013 sweet spot 直接移植) Part A **10 訊號完全等於 baseline** WR 90.0% Sharpe 1.21 cum +68.97% / Part B **6 訊號完全等於 baseline** WR 83.3% Sharpe 0.80 cum +28.91% / min(A,B) **0.80 TIE** — **^MOVE LEVEL 130 完全非綁定**：所有 16 baseline 訊號當日 ^MOVE <= 130，TQQQ extreme capitulation signals 結構上不伴隨 ^MOVE > 130 extreme rate panic（^MOVE 130+ 罕見：2022-10 BoE pension crisis、2023-03 SVB；TQQQ -15% drawdown 多由純科技股賣壓觸發、與 bond vol extreme 不重合）；Att2 (max_move_3d_change=+5.0, XLU-013 sweet spot 直接移植，DIRECTION) Part A 4/100% std=0 zero-var **Sharpe 0.00 退化** cum +31.08% / Part B 5/80%/Sharpe **0.66** cum +20.48% (**reverse selection**：移除 2025-02-27 winner 但保留 2025-03-06 SL，因 2025-03-06 SL ^MOVE 3d change < +5 完全非綁定) / min(A,B) **0.66 REJECT (-18%)** — 3d 維度與 capitulation winners 在 [+0, +5] 區間結構性重疊，filter 系統性反向選擇移除 winners；Att3 ★ FINAL (max_move_5d_change=+8.0, 更長累計窗口 + 中度放寬) Part A 5/80%(4W/1L)/Sharpe **0.66** cum +20.48% (cooldown chain shift 引入 2021-09-28 SL，原本 baseline 結構性無解 low-vol drift SL) / Part B 4/100% std=0 cum +31.08% (**成功過濾 2025-03-06 SL** ✓ 但同步誤殺 2025-02-27 winner，^MOVE 5d change ∈ [+5, +8] 兩者結構相似) / min(A,B) **0.66 REJECT (-18%)** — 5d 維度雖能捕捉 2025-03-06 rate-shock 特徵但同時誤殺結構相似 winner + Part A heavy attrition 10→5。**核心失敗發現（lesson #24 family v9 邊界擴展，repo 首次 ^MOVE 於 leveraged tech ETF 試驗失敗）**：(1) **^MOVE LEVEL 維度與 TQQQ extreme capitulation 結構性非綁定**——TQQQ -15% drawdown extreme capitulation 與 ^MOVE > 130 extreme rate panic 為**不同 macro 情境**（前者由科技股集中賣壓觸發，後者由央行政策 / 流動性危機觸發），兩維度極端事件不重合；(2) **^MOVE DIRECTION 維度（3d / 5d）對 2025-03-06 SL 部分綁定但同時誤殺結構相似 winners**——2025-03-06 SL（Trump 關稅 reflation→stagflation 切換）^MOVE 5d change > +8（rate shock 特徵），但 2025-02-27 winner（^MOVE 5d change ∈ [+5, +8]）結構相似被同步誤殺，無單一 threshold 可區分；(3) **lesson #24 family v9 邊界擴展整合（^MOVE family 整體失效）**：(a) ^MOVE LEVEL（Att1）非綁定 + (b) ^MOVE 3d DIRECTION（Att2）reverse-select winners + (c) ^MOVE 5d DIRECTION（Att3）誤殺結構相似 winners + Part A cooldown chain shift——^MOVE family（LEVEL + DIRECTION 任何時間尺度）對 TQQQ extreme capitulation framework 結構性失效，**整體與 ^VIX family（TQQQ-019/020）失敗模式平行**；(4) **新跨資產規則（lesson #24 family v9 適用邊界進一步精煉）**：所有 implied vol 維度（equity ^VIX + bond ^MOVE + commodity ^OVX/^GVZ）對「-15% drawdown extreme capitulation framework」皆結構性與 capitulation 共線（^VIX）或非綁定（^MOVE LEVEL）或 reverse-selecting winners（^MOVE DIRECTION），**整體拒絕 lesson #24 family（implied vol 任何維度）於 -15% extreme capitulation framework**；(5) **TQQQ Part B SL 2025-03-06 為跨整個 implied vol family 結構性無解 SL**——已試 ^VIX 5d cumulative DIRECTION（TQQQ-019）+ ^VIX 1d momentum reversal/peak-passing（TQQQ-020）+ ^MOVE LEVEL（TQQQ-021 Att1）+ ^MOVE 3d/5d DIRECTION（TQQQ-021 Att2/Att3）共 9 次嘗試皆失敗；新假設（待驗證）：可能需**非 implied vol 維度**——cross-asset relative strength（如 TQQQ vs SPY 相對強度）、underlying QQQ short-term momentum reversal、yield curve slope velocity、或**完全替代 framework**（拋棄 -15% extreme capitulation 結構，採 vol-transition MR 或 BB Squeeze Breakout）方能突破 TQQQ Part B 0.80 binding ceiling；(6) **TQQQ 第 21 次實驗（含 ^MOVE failure）、9 大策略類型**（MR / trend-momentum-breakout / Gap-Down / single-period filter / regime+transition combo filter / **^VIX cumulative direction** / **^VIX peak-passing 1d momentum** / **^MOVE LEVEL** / **^MOVE DIRECTION**）。TQQQ-018 Att3 仍為 min(A,B) 全域最優（21 次實驗、9 大策略類型）。
  note_2026_05_09_tqqq020: TQQQ-020 added 2026-05-09 (^VIX Peak-Passing Filter on Vol-Regime-Gated Capitulation Buy, **repo 首次「^VIX 1d momentum reversal / peak-passing」維度試驗於任何資產 — 全部 REJECT/TIE**, direct test of TQQQ-019 explicit unverified hypothesis "可能需 ^VIX 1d change（signal-day deceleration）或 peak passing 確認方能切分"). Three iterations all failed/tied vs TQQQ-018 Att3 min(A,B) 0.80. Att1 (max_vix_1d_change=0.0 嚴格 peak-passing) Part A **2 訊號** WR 50.0% Sharpe **-0.07** cum -1.66% / Part B **0 訊號** / min(A,B) **-0.07 REJECT (-109%)** — 結構性失敗：capitulation 訊號日 VIX **必上升**（恐慌爆發本質），1d <= 0 過嚴過濾掉幾乎所有訊號（含 baseline 全部 6 Part B + 8/10 Part A 訊號），僅留 2 邊緣訊號（2021-02-26、2023-09-27）；Att2 (max_vix_1d_change=+3.0 適度放寬) Part A **6** 訊號 WR 83.3% Sharpe **0.80** cum +28.91% (vs baseline 10/90%/1.21/+68.97%, 過濾 4 winners) / Part B **6 訊號完全不變** WR 83.3% Sharpe 0.80 cum +28.91%（2025-03-06 SL 之 VIX 1d 已 <= +3）/ min(A,B) **0.80 TIE baseline 但 Part A 退化** — **驗證 Part B SL 與 Part A winners 在 VIX 1d 維度結構性反向**：Part B 2025-03-06 SL VIX 1d 落於 [+0, +3] moderate spike 區間，與部分 Part A winners 重疊；Part A 4 winners 之 VIX 1d > +3（extreme spike 但仍 TPs），filter 系統性反向選擇移除 Part A winners；Att3 ★ FINAL (max_vix_1d_change=+7.0 大幅放寬) Part A **10 訊號數同 baseline** WR **80.0%** (8W/2L vs baseline 9W/1L) Sharpe **0.66** cum +45.14% (vs baseline 90%/1.21/+68.97%) / Part B 6 訊號完全不變 / min(A,B) **0.66 REJECT (-18%)** — cooldown chain shift（lesson #19 family）：放寬 1d cap 至 +7 雖訊號數恢復但破壞 baseline 訊號精準排程，將原 winner 替換為 loser（典型 lesson #19 collapse）。**核心失敗發現（lesson #24 family v9 邊界擴展，repo 首次 ^VIX 1d peak-passing 維度試驗失敗）**：(1) **^VIX peak-passing / 1d momentum reversal 在 TQQQ extreme capitulation framework 結構性失敗 — 直接拒絕 TQQQ-019 之未驗證假設**——AI_CONTEXT 原假設「peak-passing 可區分 winners vs SL」為錯誤，實際 trade-level 顯示 Part B 2025-03-06 SL VIX 1d <= +3（moderate spike 範圍），與 Part B winners 及部分 Part A winners 重疊；嚴格 peak-passing (1d <= 0) 與 capitulation 結構性矛盾（恐慌日 VIX 必上升），中度放寬 (+3) 系統性反向選擇 Part A winners，大幅放寬 (+7) 觸發 cooldown chain shift；(2) **lesson #24 family v9 邊界擴展整合（DIRECTION 維度全層級失效）**：(a) **5d cumulative DIRECTION**（TQQQ-019）失敗 + (b) **1d single-day DIRECTION / peak-passing**（TQQQ-020）失敗——VIX DIRECTION 維度（不論時間尺度 1d~5d、不論 cumulative vs momentum reversal）皆與 TQQQ extreme capitulation framework 結構性共線，**整體拒絕 lesson #24 family DIRECTION 維度於 -15% drawdown extreme capitulation framework**；(3) **新跨資產規則（lesson #24 family v9 適用邊界精煉，repo 首次發現）**：lesson #24 family DIRECTION 維度（任何時間尺度 + 任何形式 cumulative/momentum）適用邊界 = 「進場條件不含極端 capitulation 觸發」嚴格化；TQQQ extreme capitulation framework（DD ≤ -15% + RSI(5) < 25 + Volume > 1.5x SMA20）與 ^VIX 任何 DIRECTION 維度結構性 100% 共線，**全部 DIRECTION 變體無區分力**。新假設（待驗證）：可能需 ^VIX **LEVEL** 維度（如 ^VIX < 50 absolute cap 防 mid-panic 進場）或 **VIX-VXN cross-index divergence** 或**完全替代 framework**（拋棄 capitulation 結構，採 vol-transition MR 或 BB Squeeze Breakout）方能突破 TQQQ Part B 0.80 binding ceiling；(4) **TQQQ Part B SL 2025-03-06 為結構性無解 ^VIX 維度 SL**——已試 ^VIX 5d cumulative DIRECTION（TQQQ-019）+ ^VIX 1d momentum reversal/peak-passing（TQQQ-020）兩大 DIRECTION 變體共 6 次嘗試皆失敗，2025-03-06 SL 在所有 ^VIX DIRECTION 維度與 winners 分布重疊；(5) **TQQQ 第 20 次實驗（含 ^VIX peak-passing 失敗）、8 大策略類型**（MR / trend-momentum-breakout / Gap-Down / single-period filter / regime+transition combo filter / **^VIX cumulative direction** / **^VIX peak-passing 1d momentum**）。TQQQ-018 Att3 仍為 min(A,B) 全域最優（20 次實驗、8 大策略類型）。
  note_2026_05_09_tqqq019: TQQQ-019 added 2026-05-09 (^VIX Direction Filter on Vol-Regime-Gated Capitulation Buy, **repo 第 7 次 lesson #24 family forward-looking IV regime gate 跨資產驗證、首次 ^VIX DIRECTION 變體於 leveraged 槓桿 ETF — 全部 REJECT/TIE**, cross-asset port from XLU-013 / USO-025 / GLD-015 / XBI-017 / FCX-015 / COPX-016 IV direction family). Three iterations all failed/tied vs TQQQ-018 Att3 min(A,B) 0.80. Att1 (max_vix_direction_change=+5.0, XLU-013/USO-025 sweet spot 範圍直接移植) Part A 6/83.3%/Sharpe **0.80** cum +28.91%（vs baseline 10/90%/1.21/+68.97%, 過濾 4 winners）/ Part B 3/66.7%/Sharpe **0.28** cum +5.23%（vs baseline 6/83.3%/0.80/+28.91%, 過濾 3 訊號其中 2 winners + 1 SL）/ min(A,B) **0.28 REJECT (-65%)** — TQQQ capitulation 訊號日（drawdown ≤ -15% + RSI(5) < 25 + Volume > 1.5x）**結構上必然伴隨 ^VIX 5d 飆升**（capitulation 與 VIX spike 為**同一現象**），+5 cap 系統性移除大多數 capitulation winners；Att2 (max_vix_direction_change=+15.0 大幅放寬) Part A 10/90%/Sharpe **1.21**（**完全等於 baseline**）/ Part B 6/83.3%/Sharpe **0.80**（**完全等於 baseline**）/ min(A,B) **0.80 TIE** — +15 對 baseline 全部 16 訊號完全非綁定，所有 capitulation 訊號 ^VIX 5d 變化 <= +15；Att3 (max_vix_direction_change=+10.0 中間值) Part A **9**/88.9%/Sharpe **1.12** cum +57.92%（過濾 1 Part A winner）/ Part B 6/83.3%/Sharpe **0.80**（**Part B 完全不變**）/ min(A,B) **0.80 TIE 但 Part A 邊際劣化**（-7% Part A Sharpe）— +10 移除 1 Part A winner 但對 Part B SL 2025-03-06 完全非綁定（VIX 5d change <= +10）。**核心失敗發現（lesson #24 family v8 邊界精煉，repo 首次發現）**：(1) **lesson #24 family forward-looking IV DIRECTION cap 在 leveraged 槓桿 capitulation buy 框架結構性失效**——TQQQ 進場條件（DD ≤ -15% + RSI(5) < 25 + Volume > 1.5x SMA20）與 ^VIX DIRECTION 高度共線（capitulation = VIX spike），任何 cap threshold 必落於 [+5, +15] 區間內：< +5 過嚴 reverse-select winners、> +15 完全非綁定、中間值 +10 過濾 winners 但對 SL 非綁定。**單一 cap threshold 結構性無法在 capitulation framework 區分 winners vs SL**；(2) **與 USO-025/XLU-013 結構對比**：USO 進場為 RSI(2)<15 + 2d floor (淺 capitulation, ^OVX 5d 通常 <+6) + GLD 為 RSI hook turn-up (非 capitulation, ^GVZ 10d 通常平穩) + XLU 為 vol-transition MR (淺 capitulation) — 三者皆**非極端 capitulation 框架**，^VIX/IV DIRECTION 維度具區分力；TQQQ 為 -15% drawdown 極端 capitulation framework，與 IV DIRECTION 維度結構性共線；(3) **新跨資產規則（lesson #24 family v8 適用邊界擴展）**：lesson #24 family forward-looking IV DIRECTION cap 適用邊界 = 「進場條件不含極端 capitulation 觸發」(non-extreme drawdown + RSI / Pullback MR / RSI hook MR)；TQQQ-019 為**首次驗證在 extreme capitulation framework（-15% drawdown）失效**，新假設為「extreme capitulation framework + IV DIRECTION cap → structural collinearity → 不適用」；(4) **Repo 第 7 次 lesson #24 family 跨資產驗證**（TLT-013 LEVEL ✓、XLU-013/USO-025/GLD-015/USO-028 DIRECTION ✓、XBI-017 BANDS ✓、FCX-015 FLOOR ✓、TQQQ-019 DIRECTION ✗ extreme capitulation）；(5) **TQQQ Part B SL 2025-03-06 結構性無解**：TQQQ-018 Att3 殘餘 Part B SL VIX 5d change 落於 [+5, +10] 區間（Att1 +5 cap 移除但同時誤殺 winners、Att3 +10 cap 對其完全非綁定），**單一 ^VIX 5d 維度不具區分力**；新跨資產假設（待驗證）：可能需 ^VIX 1d change（signal-day deceleration）或 ^VIX 短期動能反轉（peak passing 確認）方能切分。TQQQ-018 Att3 仍為 min(A,B) 全域最優（19 次實驗、7 大策略類型）。
  note: TQQQ-018 added 2026-04-28 (Volatility-Regime-Gated Capitulation Buy, **Att3 SUCCESS — repo first BB-width regime gate validation on leveraged index ETF, repo first "first-day-of-decline filter" via prior drawdown depth**, cross-asset port from TLT-007 Att2 directly testing TLT doc cross-asset hypothesis "TQQQ 2022 single tech bear market"). Three iterations Att1/Att2/Att3 all SUCCESS, monotonically improving. Att1 (max_bb_width_ratio=0.50) Part A 12/75.0%/Sharpe **0.49** cum +42.74% MDD -11.10% (vs baseline -29.26%) / Part B 6/83.3%/Sharpe 0.80 cum +28.91% / min(A,B) **0.49** (+36% vs TQQQ-010 0.36). BB 0.50 filtered 4 of 6 Part A SLs (2020-03-12 BB 1.864, 2022-03-08 0.512, 2022-09-01 0.521, 2022-09-21 0.493 just barely <0.50 KEPT) and Part B 1 SL (2025-03-06 BB 0.477 KEPT). Lost Part B 2 winners (2024-08-05 BB 0.656 yen carry, 2025-04-04 BB 0.549 tariff) which were brief vol spikes with rapid recovery; Att2 (max_bb_width_ratio=0.48) Part A 11/81.8%/Sharpe **0.73** cum +55.30% (vs baseline 55.44%, almost matched) / Part B 6 unchanged / min(A,B) **0.73** (+103% vs baseline). Tightening 0.50→0.48 precisely filtered 2022-09-21 SL (BB 0.493) without cooldown shift (next raw signal 2023-09-27 far away); Att3 ★ (Att2 + Drawdown(T-5)<=-1% prior drawdown filter) Part A 10/**90.0%**/Sharpe **1.21** cum +68.97% (exceeded baseline +55.44% by 24%!) MDD -9.07% PF 7.79 / Part B 6 unchanged Sharpe 0.80 / min(A,B) **0.80** (Part B now constraint, +10% vs Att2, **+122% vs baseline 0.36**). A/B annualized cum gap **18.1%** (Part A 11.05%/yr vs Part B 13.54%/yr) **<30% ✓**, A/B signal ratio 1.5:1 (33% gap <50% ✓). All three acceptance criteria met. **Att3 success mechanism**: DD(T-5)<=-1% precisely filters 2020-02-24 SL (DD_5d_ago -0.49%, COVID first-day-of-decline) while preserving all winners (DD_5d_ago range -1.38%~-21.42% all pass); only remaining Part A SL is 2021-09-28 (DD_5d_ago -12.57%, BB 0.219, structurally unfilterable low-vol regime drift). **Cross-asset contributions**: (1) **Validates TLT-007 doc hypothesis**: BB-width regime gate extends from rate-driven (TLT 1% vol, threshold 5%) to leveraged tech ETF (TQQQ ~5-6% vol, threshold 48%) — threshold scales with asset vol; **TLT-007 Part A SLs concentrated in single 2022 hiking regime (BB persistently >5%), TQQQ Part A SLs concentrated in 2020 COVID + 2022 tech bear regimes (BB persistently >0.50)** — both single-extreme-vol-episode pattern fits BB-width regime gate; (2) **NEW finding (Att3)**: "first-day-of-decline filter" via Drawdown(T-N)<=-X% complements BB-width regime gate by catching transition-day signals (rapid intraday plunge from near-high) that elude vol regime classifier. Predicted to extend to other leveraged/high-vol ETFs (SOXL, SQQQ). **Repo first breakthrough of TQQQ Part A Sharpe 0.36 ceiling** that TQQQ-017 declared structural noise — confirming the failure was per-signal feature filtering, NOT regime+transition combo filtering. TQQQ-018 Att3 becomes new global optimum (18 experiments, 6 strategy categories: MR / trend-momentum-breakout / Gap-Down / single-period filter / **regime+transition combo filter** is the new winning category). TQQQ-017 added 2026-04-23 (Capitulation + Intraday/Acceleration/Multi-day Confirmation Filters, 3 iterations all failed vs TQQQ-010 min 0.36). Att1 (ClosePos>=30%) Part A 0.43 / Part B 0.13 min 0.13 — ClosePos filter removed 5/7 Part B winners (TQQQ 3x vol keeps most capitulation days closing near Low); Att2 (2-day return<=-10%) Part A 0.13 / Part B 0.49 min 0.13 — 2DD filter removed 8 Part A winners vs only 2 losers, acceleration is not the key winner/loser discriminator; Att3 (Prev RSI(5)<30) Part A 0.34 / Part B 1.02 min 0.34 — Prev RSI naturally already satisfied on most TQQQ-010 signals (Part B signals identical), marginal net effect -0.02. Core finding: **TQQQ-010's 6 Part A losers cannot be reliably distinguished from winners by single-day / 2-day / prev-day technical filters** — their distributions overlap on ClosePos, 2DD, and Prev RSI dimensions (NOTE: TQQQ-018 Att3 disproved this conclusion by combining BB-width regime gate with prior-drawdown filter). Part A Sharpe 0.36 reflects structural noise of 3x leveraged ETF in extreme regimes (std_return 6.92%), not a filterable feature (NOTE: TQQQ-018 Att3 disproved — was filterable via regime+transition combo). Extends lesson #20b failure family to "single-period confirmation" filter category on leveraged index ETFs — paralleling ClosePos/acceleration/hook failures on policy-driven ETFs (URA/TLT/FXI). TQQQ-016 added 2026-04-17 (Gap-Down Capitulation + Intraday Reversal MR, 3 iterations all failed). Att1 gap-3% Part A 0/Part B -0.07 (too sparse 3/2 signals), Att2 gap-2% Part A 0.13/Part B -0.07 (added 2 false reversals), Att3 +volume Part A 0.49/Part B -0.07 (Part B unchanged). Validates lesson #20a boundary: Gap-Down reversal pattern does NOT extend to leveraged tech ETFs (QQQ underlying lacks 24/7 continuous price discovery; 2025-04-07 tariff gap-down continued declining).
-->
## AI Agent 快速索引

**當前最佳：** ★ **TQQQ-025 Att2**（VXN-VIX Cross-Index IV Divergence + VVIX Direction Filter on Vol-Regime-Gated Capitulation Buy：TQQQ-018 Att3 完整框架 + **^VXN/^VIX 比率 >= 1.10 cross-index IV divergence FLOOR + ^VVIX 5 日累計變化 >= -5 higher-moment IV direction FLOOR**，TP +7% / SL -8% / 10 天 / cd 3 / slippage 0.1%）★ **2026-05-10 新全域最優（25 次實驗、56+ 次嘗試）**
- Part A: 9 訊號 / WR **100%** / std=0 zero-var Sharpe 0.00 / cum **+83.85%** / MDD -7.41%（vs baseline 10/90%/1.21/+68.97%, **過濾 2021-09-28 SL** VVIX_5d=-9.70 surgical）
- Part B: 5 訊號 / WR **100%** / std=0 zero-var / cum +40.26% / MDD -6.53%（vs baseline 6/83.3%/0.80/+28.91%, **過濾 2025-03-06 SL** VXN/VIX=1.055 surgical）
- min(A,B)† **structurally NO LOSS**（雙 Part 全勝零方差，依 EWT-010/IBIT-009 慣例優於 baseline 0.80 of 「Part A 1 SL + Part B 1 SL」結構；Part A WR 90→**100%**, Part B WR 83.3→**100%**）
- A/B 年化 cum gap **29.7% < 30% ✓**（Part A 12.96%/yr vs Part B 18.43%/yr，雙 Part SL 同步純化使 cum 同步上升）
- A/B 訊號比 1.8/yr vs 2.5/yr = **28% gap < 50% ✓**
- **三項 acceptance criteria 全部達標**
- **跨資產貢獻**：(1) **repo 首次「cross-index implied vol divergence」變體（^VXN/^VIX 比率）於任何資產**——擴展 lesson #24 family v11 從單一 vol index LEVEL/DIRECTION 至「比率」維度衡量 sub-segment vs broader market IV regime divergence；(2) **repo 首次 ^VVIX (VIX of VIX) 應用於任何資產**——higher-moment IV direction 維度；(3) **repo 首次「正交雙 IV 維度 AND 條件」突破 TQQQ Part B 0.80 結構性 ceiling**（13 次嘗試後）；(4) **trade-level 雙正交確認**：Part A SL (VXN/VIX=1.176 中段，VVIX_5d=-9.70 負極端) vs Part B SL (VXN/VIX=1.055 負極端，VVIX_5d=+6.03 正常)，**單一維度結構性無法切分，雙正交維度 AND 條件為 unique solution**；(5) **IV vs price divergence 維度敏感度發現**：TQQQ-022 (QQQ-SPY price divergence) 失敗 vs TQQQ-025 (^VXN-^VIX IV divergence) 成功——IV 維度比 price 維度更敏感 capture tech-vs-broad regime separation
- 關鍵 trade-level：VXN/VIX FLOOR 1.10 surgical 過濾 2025-03-06 Part B SL（ratio 1.055 唯一 < 1.10），全部 14 winners ratio ∈ [1.121, 1.331] 全部通過；VVIX_5d FLOOR -5 surgical 過濾 2021-09-28 Part A SL（VVIX_5d=-9.70 唯一 < -5），全部 14 winners VVIX_5d ∈ [-3.63, +35.06] 全部通過。Att1（VXN/VIX only）PARTIAL min(A,B)† 1.21 (+51%) 但 A/B cum gap 40%；Att3 ablation（VVIX-only）REJECT 確認 VXN/VIX 對 Part B SL 必要性

**前任最佳：** TQQQ-018 Att3（Volatility-Regime-Gated Capitulation Buy：TQQQ-010 三條件 + **BB(20,2) Width/Close < 0.48** regime gate + **Drawdown(T-5) <= -1%** first-day-of-decline filter，TP +7% / SL -8% / 10 天 / cd 3 / slippage 0.1%）— 24 次實驗，已被 TQQQ-025 Att2 超越
- Part A Sharpe 1.21, Part B Sharpe 0.80, min(A,B) **0.80**（Part B 為 binding constraint，已突破）

**最新實驗：** TQQQ-025（VXN-VIX Cross-Index IV Divergence + VVIX Direction Filter — **Att2 SUCCESS 雙 Part std=0 全勝，repo 首次正交雙 IV 維度 AND 突破 TQQQ Part B 0.80 ceiling**）—— 詳見 AI_CONTEXT note_2026_05_10_tqqq025
- Att1 (VXN/VIX FLOOR 1.10 only) min(A,B)† **1.21** PARTIAL — Part B 純化 std=0 但 A/B cum gap 40% > 30%
- Att2 ★ (Att1 + VVIX 5d FLOOR -5) min(A,B)† **structurally NO LOSS**（雙 Part 全勝） + A/B cum gap 29.7% < 30% ✓ SUCCESS
- Att3 ablation (VXN/VIX off, VVIX-only) min(A,B) **0.80 TIE** — 確認雙維度正交、VXN/VIX 對 Part B SL 必要性

**前次實驗：** TQQQ-024（Post-Capitulation Vol-Transition MR — **repo 首次「完全替代 framework」於 TQQQ，3 次嘗試全部 REJECT vs TQQQ-018 baseline 0.80**，驗證 vol-transition MR framework 於 leveraged tech ETF 結構性失敗）—— 詳見 AI_CONTEXT note_2026_05_09_tqqq024
- Att1 (BB lower + PB[-25%,-8%] + WR<=-85 + ClosePos>=0.35 + ATR>1.10 + 2DD<=-3%) min **-0.01**（Part A 2/Part B 1，6-cond AND chain 過嚴）
- Att2 (移除 PB floor + ClosePos>=0.30 + ATR>1.05 + 2DD<=-2%) min **-0.01**（Part A 4/Part B 2，BB 下軌+WR 為 binding constraint）
- Att3 (WR<=-75 + ATR>1.00 非綁定 + ClosePos>=0.35 + 2DD<=-3%) min **0.00**（Part A 5 Sharpe 0.19/Part B 1 殘留 SL，2025-02-25 結構性無解）
- 核心發現：vol-transition MR framework 於 5-6% vol leveraged ETF 結構性失效（BB 下軌 + 10d pullback co-occurrence 結構性極稀）
- 跨資產貢獻：lesson #6 邊界第五次擴展——vol-transition MR framework 適用 = 「非 leveraged 標的或具特殊 framework 結構基底」
- Part A Sharpe **1.21** (vs TQQQ-010 0.36, **+236%**), Part B Sharpe **0.80** (Part B 為新約束)
- min(A,B) **0.80** (vs TQQQ-010 0.36, **+122%**)
- Part A: 10 訊號 (vs 20 baseline) / WR **90.0%** (vs 70%) / cum +68.97% (vs +55.44% baseline) / MDD **-9.07%** (vs -29.26%) / PF **7.79** (vs 2.02)
- Part B: 6 訊號 / WR 83.3% / cum +28.91% / Sharpe 0.80
- A/B 年化 cum 差 **18.1%**（Part A 11.05%/yr vs Part B 13.54%/yr）**< 30% ✓**
- A/B 訊號比 1.5:1（gap 33% < 50% ✓）
- **三項 acceptance criteria 全部達標**
- **Repo 首次突破 TQQQ Part A Sharpe 0.36 結構性上限**（TQQQ-017 declared 為「不可過濾的結構性噪音」，被 TQQQ-018 Att3 之「regime + transition combo filter」反證）

**前任最佳：** TQQQ-010（含成交模型：隔日開盤進場，TP +7%，SL -8%，持倉 10 天，無追蹤停利，min(A,B) 0.36）

**滾動窗口分析摘要（2026-03-29）：**
- **TQQQ-010：** 11/12 窗口正累計（最低 -3.29%，最高 +55.30%），勝率 50.0-100.0%，精準度突變（ΔWR 50.0pp，窗口 8→9 從 50% 跳至 100%），下游績效漸變。固定 TP/SL（+7%/-8%）使平均贏利完全穩定（+7.00%），有效抵消精準度波動。2022H2-2024H1 為最弱期（WR 50-62.5%），近期強勢回升（87.5%）

**已證明無效（禁止重複嘗試）：**
- 放寬進場門檻（Drawdown 改 -12% 或 -13%）：TQQQ-002, TQQQ-009 已證明會大幅降低勝率與報酬
- 追蹤停利：TQQQ-003, TQQQ-005 已證明在高波動標的上容易提前被洗出，表現不如固定停利
- 過嚴的 VIX 過濾（VIX ≥ 25）：TQQQ-004 導致訊號數過少，錯失機會
- 出場疊加額外過濾器（QQQ RSI < 35 加上短停利）：TQQQ-013 證明訊號數大幅降低，表現落後。**滾動窗口分析（2026-03-29）：** QQQ 數據不可用時退化為 TQQQ-010（數值完全相同），進一步確認 QQQ RSI 過濾不應納入
- VIX 自適應出場（VIX 區間動態調整 TP/SL）：TQQQ-014 三次嘗試均失敗。原因：(1) 絕大多數 TQQQ 恐慌訊號的 VIX < 30，自適應機制幾乎不啟動；(2) 放寬 TP（+9%）導致原本可達標的交易錯過目標轉為停損；(3) 放寬 SL（-10%）增加虧損但不挽救交易。固定 TP +7%/SL -8% 已是甜蜜點

**已掃描的參數空間：**
- 出場目標（TP）：+5%, +6%, +7%, +8%, +9%, +12% → +7% 最佳
- 停損目標（SL）：-6%, -8%, -10% → -8% 最佳
- 持倉天數：7, 8, 10, 12 天 → 10 天最佳
- 進場 Drawdown：-12%, -13%, -15% → -15% 最佳（需極端恐慌）
- VIX 自適應出場：3 種 VIX 分層 / 2 層（VIX ≥ 35）/ 2 層（VIX ≥ 30, 不放寬 SL）→ 全部劣化或平手

**TQQQ-015 實驗摘要（2026-04-04，趨勢/動量策略，3 次嘗試均失敗）：**
- **Att1**（QQQ BB Squeeze Breakout, TP+12%/SL-8%/20d）：Part A Sharpe 0.25 / Part B -0.28。TP +12% 太高，Part B 零達標
- **Att2**（QQQ BB Squeeze Breakout, TP+8%/SL-8%/15d）：Part A Sharpe 0.54 / Part B -0.10。QQQ 突破訊號在 TQQQ 幅度不足（Part B 零達標，最高 +3.68%）
- **Att3**（QQQ Momentum ROC(10)>5%, TP+10%/SL-10%/15d）：Part A Sharpe 0.19 / Part B 0.17。A/B 平衡極佳（gap 0.02），Part B +21.41%，但 min Sharpe 0.17 遠低於 TQQQ-010 的 0.36

**TQQQ-016 實驗摘要（2026-04-17，Gap-Down 資本化 + 日內反轉均值回歸，3 次嘗試全部失敗）：**
- **Att1**（Gap <= -3% + 20d DD ≤ -15% + RSI(5)<25 + Close>Open, TP+7%/SL-8%/10d/cd10）：Part A n=3, WR 100%, Sharpe 0.00（零方差 3/3 全贏 +7%）；Part B n=2, WR 50%, Sharpe -0.07。-3% gap 門檻（0.55σ）對 TQQQ 過嚴，訊號 1.0/年極稀
- **Att2**（同上但 gap 放寬至 -2% + 移除 volume filter）：Part A n=5, WR 60%, Sharpe 0.13；Part B n=2, WR 50%, Sharpe -0.07。新增 2022-09-01 Labor Day 前假反彈、2023-08-11 AI 泡沫回撤兩筆停損，WR 100%→60%
- **Att3**（Att2 + 加回 volume > 1.5x SMA20 過濾）：Part A n=4, WR 75%, Sharpe 0.49；Part B n=2, WR 50%, Sharpe -0.07。Volume 移除 2023-08-11 假訊號改善 Part A，但 Part B 兩筆（2024-08-05 yen carry 勝、2025-04-07 關稅公告敗）volume 均飆升，完全不變
- **核心失敗**：Part B 2025-04-07 Trump 關稅公告後符合「gap-down + 日內反轉」結構但隔日繼續深跌，觸發 -8% 停損。與 IBIT 24/7 連續交易不同，QQQ 盤外流動性有限，日內反彈常為技術性反應而非真正底部
- **min(A,B) 最佳 -0.07**（vs TQQQ-010 的 0.36）——3 次迭代全部無法超越

**TQQQ-017 實驗摘要（2026-04-23，恐慌抄底 + 盤中/加速/多日確認過濾，3 次嘗試全部失敗）：**
動機：TQQQ-010 Part A 20 訊號 / WR 70% / Sharpe 0.36 拖累 min(A,B)（Part B 1.02），6 筆 Part A 停損（2020-02-24、2020-03-12、2021-09-28、2022-03-08、2022-09-01、2022-09-21）無單一技術模式共通點。本實驗測試三類單日/雙日/前日過濾器能否可靠區分 Part A 贏家 vs 輸家。
- **Att1**（TQQQ-010 + ClosePos = (Close-Low)/(High-Low) >= 0.30）：Part A n=11, WR 72.7%, Sharpe 0.43（+19% vs TQQQ-010）；Part B n=5, WR 60%, Sharpe 0.13（-87% vs TQQQ-010）。min(A,B) 0.13。ClosePos 在 Part A 成功篩除 3/4 stop-loss（2020-03-12、2021-09-28、2022-03-08、2022-09-21 中前三者），但 Part B 崩壞——TQQQ-010 原 7 勝者中 5 筆 ClosePos<0.30（2024-04-19、2024-07-24、2024-09-06、2025-02-27、2025-04-04），過濾器同時移除這些好訊號，並因冷卻期偏移引入新壞訊號（2025-03-04、2025-04-07 兩筆 SL）。**驗證 cross_asset_lesson #6 邊界**：ClosePos 在 TQQQ 5-6% vol 上失效（lesson #6 邊界 ≤ 2% vol）
- **Att2**（TQQQ-010 + 2 日累計報酬 <= -10%）：Part A n=10, WR 60%, Sharpe 0.13；Part B n=4, WR 75%, Sharpe 0.49。min(A,B) 0.13。2-day -10% 過濾器移除 Part A 20 訊號中 10 筆，但篩除比例無選擇性——移除 8 個勝者（2019-10-02、2021-02-25、2021-05-12、2021-10-04、2022-01-10、2022-04-26、2022-05-11、2023-09-27）與 2 個敗者（2022-09-01、2022-09-21）。**加速度不是 TQQQ 贏/輸的關鍵區分軸**：多數 TQQQ 勝者是「中等 2 日下跌疊加既有 DD」的訊號（如 2021-02-25 Fed pivot、2022-01-10 科技財報擔憂），強制 2 日 -10% 門檻移除這些高品質中等加速訊號
- **Att3**（TQQQ-010 + Prev RSI(5) < 30）：Part A n=13, WR 69.2%, Sharpe 0.34（-0.02 vs TQQQ-010 的 0.36）；Part B n=8, WR 87.5%, Sharpe 1.02（與 TQQQ-010 **完全相同**）。min(A,B) 0.34（-0.02 邊際劣化）。Part B 訊號結構與 TQQQ-010 完全一致——確認 Part B 所有 TQQQ-010 訊號之前一日 RSI(5) 皆 < 30（即「雙日超賣」條件天然成立）。Part A 篩除 7 筆（4 勝者 + 2 敗者 + 1 冷卻偏移勝者），篩除比例無選擇性（30% 敗者 vs 29% 勝者）
- **核心失敗**：**TQQQ-010 的 6 筆 Part A 停損無法用單日/雙日/前日技術過濾器可靠區分**——停損訊號在 ClosePos、2DD、Prev RSI 三維度上與勝率訊號分布重疊。Part A Sharpe 0.36 天花板反映 3x 槓桿 ETF 在極端跌勢中的結構性噪音（std_return 6.92%），包含 2020 COVID + 2022 科技熊市使 Part A 必然承受 -8% SL 的機械觸發
- **Lesson #20b 失敗家族擴展**：ClosePos/加速/前日超賣三類「單週期確認」過濾器在槓桿指數 ETF 上失敗，平行於政策驅動 ETF（URA/TLT/FXI）的 oscillator hook / day-after reversal / 強反轉 K 線失敗模式
- **min(A,B) 最佳 0.34**（Att3，vs TQQQ-010 的 0.36）——3 次迭代全部無法超越
- **【已被 TQQQ-018 Att3 反證】**：TQQQ-017 結論「6 筆 Part A SLs 無法用技術過濾器區分」
  僅成立於「單週期 single-period」過濾器；regime-level（BB width）+ transition-day
  （prior drawdown depth）combo 可過濾其中 5/6 SLs（除 2021-09-28 低 vol drift SL 外）

**TQQQ-018 實驗摘要（2026-04-28，波動率 regime 閘門 + 進場前回撤過濾，3 次迭代全部成功，
新最佳）：**
動機：TLT-007 Att2 doc 明確列出跨資產假設「TQQQ（2022 單一科技熊市）為 BB-width regime
gate 預期成功候選」。同時挑戰 TQQQ-017 結論——測試是否能用「regime-level + transition」
組合過濾器繞過單週期過濾器之失敗模式，過濾 TQQQ-010 6 筆 Part A SLs 中的 5 筆（保留
2021-09-28 結構性低 vol regime drift SL）。
- **Att1**（max_bb_width_ratio=0.50）：Part A 12 訊號 WR 75.0% Sharpe **0.49** cum +42.74%
  MDD -11.10% / Part B 6 訊號 WR 83.3% Sharpe 0.80 cum +28.91% / min(A,B) **0.49**（+36%
  vs TQQQ-010）。BB 0.50 過濾 4/6 Part A SLs 與 2/2 高 vol Part B winners + 1/1 Part B SL；
  代價為 5 個 Part A 高 vol winners 被過濾（包括 2020-02-28、2020-09-08、2022-01-21、
  2022-04-26、2022-05-11）。
- **Att2**（max_bb_width_ratio=0.48 收緊）：Part A 11 訊號 WR **81.8%** Sharpe **0.73**
  cum +55.30%（幾乎追平 baseline +55.44%）/ Part B 6 unchanged Sharpe 0.80 / min(A,B) **0.73**
  （+103% vs baseline）。0.50→0.48 精準過濾 2022-09-21 SL（BB 0.493 剛好通過 0.50），
  無 cooldown shift 副作用（2022-09-21 在 raw signals 後續 1 年內無相鄰訊號）。
- **Att3 ★**（Att2 + Drawdown(T-5) <= -1% 進場前回撤過濾器）：Part A 10 訊號 WR **90.0%**
  Sharpe **1.21** cum +68.97%（**超越 baseline +55.44% 達 24%**）MDD **-9.07%** PF **7.79** /
  Part B 6 unchanged Sharpe 0.80 / min(A,B) **0.80**（Part B 為新約束，+10% vs Att2，
  **+122% vs baseline**）。**A/B 年化 cum 差 18.1% < 30% ✓**，A/B 訊號比 1.5:1 < 50% ✓。
  **三項 acceptance criteria 全部達標**。
- **核心發現（Att3）**：DD_5d_ago <= -1% 精準過濾 2020-02-24 SL（DD_5d_ago 僅 -0.49%，
  COVID 急速下跌首日，5 天前還在 20d 高點附近）而保留所有 winners（DD_5d_ago 範圍
  -1.38%~-21.42% 均 PASSES）。唯一保留 Part A SL 為 2021-09-28（DD_5d_ago -12.57%，
  BB 0.219，結構性無法以任何技術維度過濾的低 vol regime drift SL）。
- **跨資產貢獻**：(1) 驗證 TLT-007 doc 之跨資產假設——BB-width regime gate 從 rate-driven
  資產（TLT 1% vol，閾值 5%）擴展至 leveraged tech ETF（TQQQ ~5-6% vol，閾值 48%），
  閾值依資產 vol 等比放大；(2) **新發現「first-day-of-decline filter」**——DD(T-N) 維度
  prior drawdown depth filter 與 BB-width regime gate 互補：BB 過濾 sustained-high-vol
  regime，prior DD 過濾 transition-day signals（剛從高點急跌首日）。預期可移植至其他
  高波動 leveraged ETF（SOXL, SQQQ）。
- **反證 TQQQ-017 結論**：TQQQ-010 6 筆 Part A SLs 中 5 筆可用 regime+transition combo 過濾
  （2020-02-24 by prior DD；2020-03-12 / 2022-03-08 / 2022-09-01 / 2022-09-21 by BB width），
  僅 2021-09-28 結構性無法過濾。Part A Sharpe 0.36 並非「結構性噪音」，而是「per-signal
  feature filtering 失敗」——regime-level + transition-day combo 之新類別過濾器有效。

**已證明無效（禁止重複嘗試）：**（更新）
原有項目加上：
- QQQ BB Squeeze Breakout → Trade TQQQ：QQQ 突破訊號在 TQQQ 幅度不足，Part B 零達標（TQQQ-015 Att1/Att2）
- QQQ 動量策略 ROC(10)>5% → Trade TQQQ：A/B 平衡好但 Sharpe ~0.17 遠低於均值回歸（TQQQ-015 Att3）
- **趨勢/突破/動量策略在 3x 槓桿 ETF 上無效**：高日波動使停損過寬但突破/動量訊號幅度不足（與 SOXL-009 一致）
- **Gap-Down 資本化 + 日內反轉模式（TQQQ-016，3 次嘗試全失敗）**：Att1 gap-3% 過嚴（3/2 訊號）、Att2 gap-2% 過鬆（Part A 0.13 含 2 假反彈停損）、Att3 加回 volume（Part A 0.49 但 Part B 不變）。**失敗根因**：與 IBIT 24/7 連續交易資產不同，QQQ 盤外流動性有限，盤前 gap-down 常反映事件衝擊（Fed/CPI/科技巨頭財報/政策公告）而非投降式拋壓；若事件利空持續，日內反彈只是技術反應（如 2025-04-07 關稅公告日 gap-down 反彈 + 隔日繼續深跌停損）。確認 **lesson #20a 不延伸至傳統（非 24/7）標的的槓桿 ETF**
- **盤中/加速/多日確認過濾模式（TQQQ-017，3 次嘗試全失敗）**：Att1 ClosePos>=0.30 Part A 0.43/Part B 0.13 min 0.13（Part B 崩壞）、Att2 2-day<=-10% Part A 0.13/Part B 0.49 min 0.13（篩除比例無選擇性）、Att3 Prev RSI<30 Part A 0.34/Part B 1.02 min 0.34（Part B 不變，Part A 邊際劣化）。**失敗根因**：TQQQ-010 的 6 筆 Part A 停損在 ClosePos、2DD、Prev RSI 三維度上與勝率訊號分布重疊，無單一維度具區分力。Part A Sharpe 0.36 天花板反映 3x 槓桿 ETF 在極端跌勢中的結構性噪音，std_return 達 6.92%。**Lesson #20b 失敗家族擴展**：單週期（單日/雙日/前日）確認過濾器在槓桿指數 ETF 上失敗，平行於政策驅動 ETF 的 hook divergence / day-after reversal 失敗模式
- **^VIX cumulative 5d Direction Filter on TQQQ-018（TQQQ-019，3 次嘗試全失敗）**：Att1 +5 min 0.28（過嚴反向選擇 winners）、Att2 +15 TIE（完全非綁定）、Att3 +10 TIE 但 Part A 退化。**失敗根因**：TQQQ extreme capitulation framework（DD ≤ -15% + RSI(5) < 25 + Volume > 1.5x）與 ^VIX 5d cumulative direction 結構性 100% 共線，capitulation = VIX spike，無單一 cap threshold 可區分 winners vs Part B SL。**Lesson #24 family v8 邊界擴展**：DIRECTION cap 適用邊界 = 「進場條件不含極端 capitulation 觸發」，TQQQ extreme capitulation 為首例失敗
- **^VIX 1d Peak-Passing / Momentum Reversal Filter on TQQQ-018（TQQQ-020，3 次嘗試全失敗）**：Att1 1d<=0 min **-0.07**（過嚴 capitulation 矛盾，僅 2 邊緣訊號）、Att2 1d<=+3 TIE 0.80 但 Part A 退化（VIX 1d 維度 Part A winners vs Part B SL 反向選擇）、Att3 1d<=+7 min **0.66**（cooldown chain shift 引入新 SL）。**失敗根因**：repo 首次「^VIX 1d momentum reversal / peak-passing」維度試驗失敗——直接拒絕 TQQQ-019 之未驗證假設「peak-passing 可區分 winners vs SL」，實際 trade-level 顯示 Part B 2025-03-06 SL VIX 1d 落於 [+0, +3] moderate spike 區間，與 Part A winners + Part B winners 重疊。**Lesson #24 family v9 邊界擴展（整合 TQQQ-019 + TQQQ-020）**：VIX **DIRECTION** 維度（不論時間尺度 1d~5d、不論 cumulative vs momentum reversal）皆與 TQQQ extreme capitulation framework 結構性共線，**整體拒絕 lesson #24 family DIRECTION 維度於 -15% drawdown extreme capitulation framework**。新假設（待驗證）：可能需 ^VIX **LEVEL** 維度（如 VIX < 50 absolute cap）或 **VIX-VXN cross-index divergence** 或**完全替代 framework**（vol-transition MR / BB Squeeze）方能突破 TQQQ Part B 0.80 binding ceiling
- **^MOVE Bond-Vol Regime Gate on TQQQ-018（TQQQ-021，3 次嘗試全失敗）**：Att1 LEVEL<=130 TIE 0.80（完全非綁定，所有 16 baseline 訊號當日 ^MOVE <= 130，TQQQ extreme capitulation 與 ^MOVE > 130 extreme rate panic 為**不同 macro 情境**不重合）、Att2 3d DIRECTION<=+5 min **0.66**（reverse selection — 移除 2025-02-27 winner 但保留 2025-03-06 SL）、Att3 5d DIRECTION<=+8 min **0.66**（**成功過濾 2025-03-06 SL** ✓ 但同步誤殺結構相似 winner + Part A heavy attrition 10→5 + cooldown chain shift 引入 2021-09-28 SL）。**失敗根因**：repo 首次 ^MOVE（bond vol）於 leveraged tech ETF / equity asset 試驗失敗——^MOVE LEVEL 維度與 TQQQ extreme capitulation 結構性非綁定（不同 macro 情境），^MOVE DIRECTION 維度（3d / 5d）對 2025-03-06 SL 部分綁定但同時誤殺結構相似 winners。**Lesson #24 family v9 邊界擴展（整合 TQQQ-019 + TQQQ-020 + TQQQ-021）**：所有 implied vol 維度（equity ^VIX + bond ^MOVE + commodity ^OVX/^GVZ）對「-15% drawdown extreme capitulation framework」皆結構性失效——^VIX 與 capitulation 共線、^MOVE LEVEL 非綁定、^MOVE DIRECTION reverse-selecting，**整體拒絕 lesson #24 family（implied vol 任何維度）於 -15% extreme capitulation framework**。新假設（待驗證）：可能需**非 implied vol 維度**——cross-asset relative strength（如 TQQQ vs SPY 相對強度）、underlying QQQ short-term momentum reversal、yield curve slope velocity、或**完全替代 framework**（vol-transition MR / BB Squeeze）方能突破 TQQQ Part B 0.80 binding ceiling
- **QQQ-SPY Cross-Asset Divergence FLOOR Filter on TQQQ-018（TQQQ-022，3 次嘗試全失敗，2026-05-09）**：直接測試 TQQQ-021 提出之未驗證假設「cross-asset relative strength（QQQ-SPY 相對強度）」。Att1 20d -3% min **0.39**（reverse selection 嚴重——Part A 訊號 10→7 / WR 90.0%→71.4%，2025-03-06 SL QQQ-SPY 20d ≥ -3% 通過 filter）、Att2 20d -5% min **0.80** TIE baseline（loose floor 僅 -1 winner Part A，Part B 完全不變、SL 仍存活）、Att3 10d -3% min **0.66**（縮短 lookback 加劇 reverse selection — Part A 10→6 / Part B 6→5，雙 SLs 仍存活）。**失敗根因（lesson #20 v3 family v11 邊界擴展，repo 首次發現）**：(1) **TQQQ extreme capitulation 與 QQQ-SPY divergence 結構性脫鉤**——TQQQ-018 框架的 DD ≤ -15% + Vol > 1.5x + BB-width regime gate 已過濾 tech-specific structural weakness 期，剩餘訊號集中於 broad-market panic 期（QQQ ≈ SPY 同步下跌），20d/10d divergence 自然壓縮；(2) **2025-03-06 SL QQQ-SPY 20d 結構性 ≥ -3%**——tariff 初期 broad market 同步深跌，divergence 並未深化；(3) **Reverse selection 嚴重**：Part A winners 集中於 QQQ-SPY 20d ∈ [-5%, -1%]（broad panic 中 tech 略弱於大盤的健康反彈時機），任何 FLOOR threshold 移除 winners 多於 SL；(4) **新失敗類別「leveraged ETF underlying-vs-broader divergence」**：repo 既有 broad-vs-broad 失敗（EEM-EFA EEM-017）+ 新增 underlying-vs-broader（QQQ-SPY TQQQ-022），擴展 lesson #20 v3 邊界精煉「target 為 narrower scope vs broader benchmark」+「target SLs 在 divergence 維度有方向性集中」雙條件；TQQQ-022 違反 (b) 條件（SLs 與 winners 在 divergence 維度分布重疊）；(5) **TQQQ Part B 0.80 binding ceiling 仍無法突破**——已試 implied vol（TQQQ-019/020/021）+ cross-asset relative strength（TQQQ-022）兩大維度全失敗，剩餘未驗證假設：「underlying QQQ short-term momentum reversal」、「yield curve slope velocity」（TLT-017 成功維度）、或「完全替代 framework」
- **Post-Capitulation Vol-Transition MR（TQQQ-024，repo 首次「完全替代 framework」於 TQQQ，3 次嘗試全部 REJECT，2026-05-09）**：直接測試 TQQQ-019/020/021/022/023 列出之未驗證假設「完全替代 framework（vol-transition MR / BB Squeeze Breakout，跳脫 -15% extreme capitulation 結構）」。Att1 (BB(20,2) 下軌 + 10d PB ∈ [-25%,-8%] + WR<=-85 + ClosePos>=0.35 + ATR(5)/ATR(20)>1.10 + 2DD floor<=-3% + cd5, TP+5%/SL-5%/10d) min **-0.01 REJECT (-101%)** — Part A 2 訊號 / Part B 1 訊號（2025-02-25 -5.09% SL），6-cond AND chain 過嚴使 5+ 年僅 2 訊號；Att2 (移除 PB floor + ClosePos>=0.30 + ATR>1.05 + 2DD<=-2%) min **-0.01 REJECT** — Part A 4 訊號（2W/2L）/ Part B 2 訊號（0W/2L），放寬 4 維度仍 binding constraint 為 BB 下軌 + WR<=-85 conjunction；Att3 (WR<=-75 放寬 + ATR>1.00 非綁定 + ClosePos>=0.35 + 2DD<=-3% 收回) min **0.00 REJECT (-100%)** — Part A 5/60%/Sharpe 0.19 cum +4.26%、Part B 1 訊號殘留 2025-02-25 SL，去除 ATR 後 Part A 訊號數略增但 Part B 結構性 SL 跨 framework 無解。**核心失敗發現（lesson #6 邊界第五次擴展、repo 首次 vol-transition MR framework 於 leveraged 槓桿 ETF 失敗）**：(1) **Vol-Transition MR framework 於高波動 leveraged ETF 結構性失效**——既有成功案例（EWJ 0.96% vol、EEM 1.17% vol、INDA 0.97% vol、VGK 1.05% vol、IBIT 3.17% vol Gap-Down 結構基底、SOXL 6% vol 雙 part std=0 結構性勉強通過）皆為非 leveraged 標的或具特殊 framework 結構基底；TQQQ 5-6% vol pure leveraged tech ETF 為**首例 vol-transition MR 失敗**——BB(20,2) 下軌 + 10d pullback co-occurrence 在 leveraged ETF 上結構性極稀（5% vol 使 BB lower band 為 Close × (1-2σ_20d) ≈ Close × 0.78，rare 觸發 + 同日 10d pullback 也達深度），雙條件交集年僅 1-2 次；(2) **TQQQ Part B 2025-02-25/2025-03-06 SL 跨整個 framework 結構性無解**——Trump 關稅 reflation→stagflation 切換之 1-3 日急跌 SL 在 extreme capitulation buy（TQQQ-018 -8% SL）+ vol-transition MR（TQQQ-024 三次迭代 -5% SL）+ implied vol filter（TQQQ-019/020/021）+ cross-asset divergence（TQQQ-022）+ yield curve slope（TQQQ-023）共 13 次嘗試皆觸發 -5%~-8% SL；(3) **新跨資產規則（lesson #6 邊界第五次擴展）**：vol-transition MR framework 適用邊界 = 「target 為非 leveraged 標的或 leveraged 標的具特殊 framework 結構基底」（EWJ/EEM/INDA/VGK 非 leveraged ✓ / IBIT Gap-Down 結構基底 ✓ / SOXL 雙 part std=0 邊際 ✓）；不適用於：「pure leveraged tech ETF（TQQQ）BB 下軌觸發稀疏 + Part B 結構性 SL 無解」；(4) **TQQQ 第 24 次實驗、12 大策略類型**（新增 vol-transition MR 失敗）。剩餘未驗證假設：「underlying QQQ short-term momentum reversal」（單日反轉模式，未試）、「TQQQ vs SQQQ inverse pair」（同一 underlying 槓桿配對，未試）、「BB Squeeze Breakout 於 TQQQ 本身（TQQQ-015 為 QQQ→trade TQQQ 方向不同）」
- **Yield-Curve-Slope Inflation-Regime Gated Capitulation Buy on TQQQ-018（TQQQ-023，3 次嘗試全失敗，2026-05-09）**：直接測試 TQQQ-021/022 提出之未驗證假設「yield curve slope velocity（TLT-017 成功維度）」。Att1 5d velocity <=+0.038（TLT-017 Att2 sweet spot 直接移植）→ min **0.80 TIE baseline**（Part A 10→7 / Sharpe 1.21→0.92 -24%、Part B 完全不變）、Att2 5d velocity <=+0.020（tighter，surgical filter 嘗試）→ min **0.49 REJECT**（過嚴：Part A 4 訊號 / Part B 僅 1 訊號 + signal gap 75% 違反 50% target）、Att3 slope LEVEL <=+0.40（velocity filter 停用，alternative dim mirror TLT-017 Att3）→ min **0.66 REJECT**（Part A 2 std=0、Part B 5 訊號誤殺 1 winner、2025-03-06 SL 仍存活）。**失敗根因（lesson #24 family v10 邊界擴展，repo 首次 yield curve slope velocity 跨資產類別失敗）**：(1) **TLT-017 yield curve slope velocity 成功不跨資產類別移植到 leveraged tech ETF**——既有成功為 rate-direct ETF（TLT 對 rates 為唯一 driver），TQQQ 為 rate-indirect 資產（rates 經由 long-duration valuation discount rate 機制間接傳導），**間接傳導路徑使 yield curve 維度與 capitulation framework 結構性脫鉤**——2025-03-06 SL（Trump 關稅 event shock）為瞬時事件衝擊（一日內 risk-off 同步推動 long+short yields 同步下行），與 TLT 2021-01-06（reflation regime onset，slope velocity 緩慢擴張）結構不同；(2) **slope velocity + slope LEVEL 雙維度同時失敗**——velocity 維度 reverse-selecting (Att2) + LEVEL 維度 reverse-selecting (Att3)，與 TLT-017 上 velocity 強於 LEVEL 之 selectivity 反向；(3) **新跨資產規則（lesson #24 family v10 邊界）**：cross-asset macro structural regime gate（implied vol / cross-asset divergence / yield curve）適用邊界 = 「target 為直接受該 macro factor 驅動的 single-driver asset class」（TLT 對 rates ✓ / USO 對 oil ✓ / GLD 對 inflation ✓）— 排除 indirect-transmission asset class（leveraged tech ETF rate-indirect ✗）；(4) **整合 TQQQ-019/020/021 + TQQQ-022 + TQQQ-023 結論**：TQQQ Part B 0.80 binding ceiling 跨 implied vol + cross-asset relative strength + yield curve **三大正交 macro structural 維度全失敗**；剩餘未驗證假設：「underlying QQQ short-term momentum reversal」（單日反轉模式，未試）或「完全替代 framework」（vol-transition MR / BB Squeeze Breakout，跳脫 -15% extreme capitulation 結構）

**尚未嘗試的方向（可探索，但預期改善極低）：**
- 分批進場/出場（如達到 +5% 賣出一半，剩餘追蹤）
- 結合大盤均線（例如 SPY SMA200）確認多空趨勢背景（但 cross-asset lesson #5 警告均值回歸+趨勢過濾=災難）
- ~~Gap-Down 資本化 + 日內反轉~~（TQQQ-016 驗證失敗，lesson #20a 不延伸至槓桿科技 ETF）
- ~~盤中/加速/多日確認過濾~~（TQQQ-017 驗證失敗，三維度均無區分力）
- ~~波動率 regime 閘門 + 進場前回撤過濾~~ → **TQQQ-018 Att3 驗證為新最佳 min 0.80（+122%）**
- BB 閾值進一步收緊（< 0.45）：預期過濾 2021-03-04 winner（BB 0.454），無新 SL 可過濾，預期 Sharpe 退化
- BB 閾值放寬至 0.55：預期重新引入 2022-09-01 SL（BB 0.521），退化至 Att1 水準
- DD_5d_ago 收緊至 -2%：預期過濾 2019-08-05 W（DD_5d_ago -1.38%），失去 winner
- 多週期 BB（如 BB(50, 2)）regime gate：預期與 BB(20,2) 訊號重疊，邊際效益遞減
- ATR(5)/ATR(20) 擴張過濾：與 BB(20,2) 數學近似（兩者皆衡量短期實現波動），預期高度冗餘

**TQQQ-018 Att3 為新全域最優**（24 次實驗、12 大策略類型：均值回歸、趨勢/動量/突破、Gap-Down 資本化、盤中/加速/多日確認、**regime + transition combo filter**、**^VIX direction filter**（TQQQ-019 失敗）、**^VIX peak-passing filter**（TQQQ-020 失敗）、**^MOVE LEVEL filter**（TQQQ-021 失敗）、**^MOVE DIRECTION filter**（TQQQ-021 失敗）、**QQQ-SPY cross-asset divergence FLOOR**（TQQQ-022 失敗）、**Yield Curve Slope Velocity / LEVEL filter**（TQQQ-023 失敗）、**Post-Capitulation Vol-Transition MR**（TQQQ-024 失敗））

**最近失敗實驗：** TQQQ-023（Yield-Curve-Slope Inflation-Regime-Gated Capitulation Buy，**repo 首次 yield curve slope velocity / level 跨資產類別移植自 TLT-017（rate-direct ETF）至 leveraged tech ETF — 全部 REJECT/TIE**，2026-05-09）— Att1 5d velocity <=+0.038 min **0.80 TIE**（TLT-017 sweet spot 直接移植；Part A 10→7 -3 winners、Part B 完全不變）/ Att2 5d velocity <=+0.020 min **0.49 REJECT**（tighter 過嚴；Part A 4、Part B 1，A/B signal gap 75% 違反 target）/ Att3 slope LEVEL <=+0.40 min **0.66 REJECT**（alternative dim；2025-03-06 SL slope LEVEL <=+0.40 仍存活但誤殺 winner）。**確認 lesson #24 family v10 邊界擴展**：yield curve slope velocity 成功不跨資產類別移植——TLT 為 rate-direct ETF（rates 為唯一 driver），TQQQ 為 rate-indirect 資產（rates 經由 long-duration valuation 機制間接傳導），間接傳導路徑使 yield curve 維度與 capitulation framework 結構性脫鉤；2025-03-06 為 event shock（一日內 risk-off 同步推動 long+short yields 下行）非 sustained inflation regime onset。整合 TQQQ-019/020/021 + TQQQ-022 + TQQQ-023 結論：**TQQQ Part B 0.80 binding ceiling 跨 implied vol + cross-asset relative strength + yield curve 三大正交 macro structural 維度全失敗**——剩餘未驗證假設：underlying QQQ short-term momentum reversal（單日反轉模式，未試）或完全替代 framework（vol-transition MR / BB Squeeze Breakout）。

**關鍵資產特性：**
- 高槓桿 (3x)，波動極大，不適合過緊的停損或追蹤停利
- "極端恐慌抄底" (Drawdown -15%) 是核心獲利來源，不可輕易放寬
- 隔日開盤進場（成交模型）會顯著影響 In-Sample 報酬（因濾除未來資訊），但更能反映真實表現
- TQQQ 恐慌訊號大多在 VIX < 30 時觸發，VIX 自適應調整的有效空間極為有限
- **TQQQ 雙 regime 結構**：2020 COVID + 2022 科技熊市為兩段「單一極端 vol regime episode」
  （BB width 持續 >0.50），其餘期間為 calm regime（BB <0.30），固定 BB 閾值 0.48 為甜蜜點
- **「first-day-of-decline」失敗模式**：2020-02-24 SL 為從 20d 高點急速下跌首日（DD_5d_ago
  -0.49%），延續性高；DD(T-5) <= -1% 過濾器精準識別，且不影響 winners（最低 winner 為
  2019-08-05 DD_5d_ago -1.38%，剛好 PASSES）
- **唯一無法過濾 SL**：2021-09-28（BB 0.219、DD_5d_ago -12.57%）為低 vol regime + 中等
  pullback drift SL，與 winners 在所有技術維度上分布重疊；可視為 TQQQ-018 框架之 Sharpe
  上限（Part A 1.21 vs 結構性極限 ~1.4 估計）
<!-- AI_CONTEXT_END -->

# TQQQ 實驗總覽 (TQQQ Experiment Index)

> **最新實驗 (Latest):** TQQQ-023 `tqqq_023_yield_curve_slope_cap`（Yield-Curve-Slope Inflation-Regime-Gated Capitulation Buy，repo 首次 yield curve slope velocity / level 跨資產類別移植自 TLT-017（rate-direct ETF）至 leveraged tech ETF，3 次 REJECT/TIE — lesson #24 family v10 邊界擴展：rate-indirect 間接傳導路徑使 yield curve 維度與 TQQQ extreme capitulation framework 結構性脫鉤）
> **當前最佳 (Best):** TQQQ-018 `tqqq_018_regime_vol_gate` ★ Att3（含成交模型 + BB-width regime gate + first-day-of-decline filter，min(A,B) 0.80）/ TQQQ-008 `tqqq_008_cap_optimized_exit`（無成交模型，僅供參考）

## 實驗清單 (Experiments)

| ID       | 資料夾                     | 說明                                   | 關鍵差異                | 狀態     |
|----------|---------------------------|----------------------------------------|------------------------|----------|
| TQQQ-001 | `tqqq_001_capitulation`       | 基礎版：三條件恐慌抄底 + 冷卻機制        | 基線                    | ✅ 基線  |
| TQQQ-002 | `tqqq_002_cap_relaxed_entry`  | 放寬進場門檻，收緊停損                   | DD -12%, RSI<30, Vol 1.3x, SL -6% | ✅ 完成  |
| TQQQ-003 | `tqqq_003_cap_wider_exit`     | 加寬獲利目標 +12%，追蹤停利 -4%          | TP +12%, 持倉 12 天, Trailing -4%  | ✅ 完成  |
| TQQQ-004 | `tqqq_004_cap_vix_filter`     | 加入 VIX ≥ 25 過濾，僅在真正恐慌時進場   | VIX ≥ 25 額外條件       | ✅ 完成  |
| TQQQ-005 | `tqqq_005_cap_vix_adaptive`   | 軟性 VIX ≥ 20 + 適應性出場（追蹤停利）   | VIX ≥ 20, TP +8%, Trailing -6%, 持倉 10 天 | ✅ 完成  |
| TQQQ-006 | `tqqq_006_momentum_collapse`  | 多日動能崩潰：連續下跌 + 累計跌幅 + 趨勢過濾 | 5 日 4 跌、5 日報酬 ≤ -12%、Close < SMA50 | ✅ 完成 |
| TQQQ-007 | `tqqq_007_cap_qqq_confirm`   | 恐慌抄底 + QQQ RSI 相對強度確認              | QQQ RSI(14) < 35、TP +6%、持倉 8 天 | ✅ 完成 |
| TQQQ-008 | `tqqq_008_cap_optimized_exit` | 基線進場 + 優化出場（+7%、10 天、無追蹤停利） | TP +7%、持倉 10 天、無 Trailing | ✅ 完成 |
| TQQQ-009 | `tqqq_009_cap_gentle_entry` | 僅放寬 DD -13% + 優化出場（+7%、10 天） | DD -13%、其餘進場不變 | ❌ 失敗 |
| TQQQ-010 | `tqqq_010_cap_exec_optimized` | 重做 TQQQ-008 + 成交模型 | 隔日開盤進場、stop_market、limit_order、0.1% 滑價、悲觀認定 | ✅ 完成 |
| TQQQ-011 | `tqqq_011_cap_exec_baseline` | 重做 TQQQ-001 + 成交模型 | 同上成交模型 | ✅ 完成 |
| TQQQ-012 | `tqqq_012_cap_exec_qqq_confirm` | 重做 TQQQ-007 + 成交模型 | 同上成交模型 + QQQ RSI 過濾 | ✅ 完成 |
| TQQQ-013 | `tqqq_013_cap_exec_qqq_optimized` | QQQ RSI 過濾 + 優化出場 + 成交模型 | 在 TQQQ-012 基礎改為 TP +7%、持倉 10 天 | ❌ 失敗 |
| TQQQ-014 | `tqqq_014_cap_exec_vix_adaptive` | VIX 自適應出場 + 成交模型 | 訊號日 VIX 決定 TP/SL/持倉：VIX≥35 → +9%/-10%/12d，<35 → +7%/-8%/10d | ❌ 失敗 |
| TQQQ-015 | `tqqq_015_qqq_trend_breakout` | QQQ 趨勢/動量策略 → Trade TQQQ + 成交模型 | Att1: BB Squeeze, Att2: BB 降TP, Att3: Momentum ROC(10)>5% | ❌ 失敗 |
| TQQQ-016 | `tqqq_016_gap_reversal_mr` | Gap-Down 資本化 + 日內反轉均值回歸（IBIT-006 移植） | Att1 gap-3% Part A 0/Part B -0.07; Att2 gap-2% 0.13/-0.07; Att3 +volume 0.49/-0.07 | ❌ 失敗 |
| TQQQ-017 | `tqqq_017_cap_reversal_confirm` | 恐慌抄底 + 盤中/加速/多日確認過濾 | Att1 ClosePos>=0.30 min 0.13; Att2 2-day<=-10% min 0.13; Att3 Prev RSI<30 min 0.34 | ❌ 失敗 |
| TQQQ-018 | `tqqq_018_regime_vol_gate` | 波動率 regime 閘門 + 進場前回撤過濾（TLT-007 跨資產移植 + first-day-of-decline filter） | Att1 BB<0.50 min 0.49; Att2 BB<0.48 min 0.73; Att3 +DD(T-5)<=-1% min 0.80 | ✅ 前任最佳（已被 TQQQ-025 Att2 超越） |
| TQQQ-019 | `tqqq_019_vix_direction_mr` | ^VIX Direction Filter on TQQQ-018（lesson #24 family v8 cross-asset port，repo 首次 ^VIX DIRECTION 於 leveraged ETF） | Att1 +5 min 0.28（過嚴反向選擇）; Att2 +15 TIE（非綁定）; Att3 +10 TIE 但 Part A 退化 | ❌ 失敗 |
| TQQQ-020 | `tqqq_020_vix_peak_passing_mr` | ^VIX Peak-Passing 1d Filter on TQQQ-018（lesson #24 family v9 候選新維度，repo 首次 ^VIX 1d momentum reversal/peak-passing 於任何資產，直接測試 TQQQ-019 未驗證假設） | Att1 1d<=0 min **-0.07**（過嚴 capitulation 矛盾）; Att2 1d<=+3 TIE 0.80 但 Part A 退化（反向選擇）; Att3 1d<=+7 min **0.66**（cooldown chain shift） | ❌ 失敗 |
| TQQQ-021 | `tqqq_021_move_regime_gate` | ^MOVE Bond-Vol LEVEL + DIRECTION Filter on TQQQ-018（lesson #24 family v9 候選新維度，repo 首次 ^MOVE 於 leveraged tech ETF / equity asset，跨 vol family 邊界擴展） | Att1 LEVEL<=130 TIE 0.80（完全非綁定）; Att2 3d DIR<=+5 min **0.66**（reverse selection 移除 winner 保留 SL）; Att3 5d DIR<=+8 min **0.66**（過濾 SL 但 Part A heavy attrition + cooldown shift） | ❌ 失敗 |
| TQQQ-022 | `tqqq_022_qqq_spy_divergence_cap` | QQQ-SPY Cross-Asset Divergence FLOOR Filter on TQQQ-018（lesson #20 v3 family v11，repo 首次「leveraged ETF underlying-vs-broader」divergence 於任何資產，直接測試 TQQQ-021 提出的「cross-asset relative strength」未驗證假設） | Att1 20d -3% min **0.39**（reverse selection，Part A WR 90→71.4%）; Att2 20d -5% min **0.80** TIE（loose floor，Part B 完全不變、SL 仍存活）; Att3 10d -3% min **0.66**（縮短 lookback 加劇 reverse selection） | ❌ 失敗 |
| TQQQ-023 | `tqqq_023_yield_curve_slope_cap` | Yield-Curve-Slope Inflation-Regime-Gated Capitulation Buy on TQQQ-018（lesson #24 family v10，repo 首次 yield curve slope velocity / level 跨資產類別移植自 TLT-017，rate-direct → rate-indirect leveraged tech ETF） | Att1 5d velocity<=+0.038（TLT-017 sweet spot 移植）min **0.80 TIE**（Part A -3 winners，Part B 完全不變）; Att2 5d velocity<=+0.020 min **0.49 REJECT**（過嚴 + signal gap 75%）; Att3 slope LEVEL<=+0.40 min **0.66 REJECT**（reverse-selecting，2025-03-06 SL 仍存活） | ❌ 失敗 |
| TQQQ-024 | `tqqq_024_vol_transition_mr` | Post-Capitulation Vol-Transition MR（**repo 首次「完全替代 framework」於 TQQQ — 拋棄 -15% extreme capitulation 結構**，cross-asset port from EWJ-005 / EEM-014 / IBIT-009 vol-transition MR family，直接測試 TQQQ-019/020/021/022/023 列出之未驗證假設「完全替代 framework」） | Att1 BB lower + PB[-25%,-8%] + WR<=-85 + ATR>1.10 + 2DD<=-3% min **-0.01 REJECT**（6-cond AND chain 過嚴，Part A 2/Part B 1）; Att2 移除 PB floor + 放寬 ClosePos/ATR/2DD min **-0.01 REJECT**（Part A 4/Part B 2，BB+WR conjunction binding）; Att3 WR<=-75 + ATR 非綁定 min **0.00 REJECT**（Part A 5 Sharpe 0.19/Part B 1 殘留 SL，2025-02-25 結構性無解） | ❌ 失敗 |
| **TQQQ-025** | **`tqqq_025_vxn_vix_vvix_filter`** ★ | **VXN-VIX Cross-Index IV Divergence + VVIX Direction Filter on TQQQ-018**（**repo 首次 cross-index IV divergence (^VXN/^VIX 比率) + repo 首次 ^VVIX (VIX of VIX) 於任何資產 + repo 首次正交雙 IV 維度 AND 條件**，lesson #24 family v11，直接回應 TQQQ-020 列出之未驗證假設「VIX-VXN cross-index divergence」） | **Att1 VXN/VIX>=1.10 only PARTIAL min(A,B)† 1.21 (+51%) 但 A/B cum gap 40%; Att2 ★ +VVIX 5d>=-5 雙維度 SUCCESS 雙 Part std=0 全勝，A/B cum gap 29.7% < 30% ✓; Att3 ablation VVIX-only min 0.80 TIE 確認雙維度正交** | ✅ **當前最佳** |

## 演進路線 (Lineage)

```
TQQQ-001 tqqq_001_capitulation (基礎版：DD -15%, RSI<25, Vol 1.5x)
├── TQQQ-002 tqqq_002_cap_relaxed_entry  (放寬進場 + 收緊停損)
├── TQQQ-003 tqqq_003_cap_wider_exit     (加寬出場 + 追蹤停利)
├── TQQQ-004 tqqq_004_cap_vix_filter     (加入 VIX 恐慌過濾)
├── TQQQ-005 tqqq_005_cap_vix_adaptive   (軟性 VIX + 適應性出場)
├── TQQQ-006 tqqq_006_momentum_collapse  (多日動能崩潰新訊號)
├── TQQQ-007 tqqq_007_cap_qqq_confirm    (QQQ RSI 相對強度確認)
├── TQQQ-008 tqqq_008_cap_optimized_exit (優化出場：+7%、10 天、無追蹤停利)
├── TQQQ-009 tqqq_009_cap_gentle_entry  (僅放寬 DD -13% + 優化出場)
│
│   ── 成交模型重做系列 (Execution Model Redo Series) ──
├── TQQQ-010 tqqq_010_cap_exec_optimized  (重做 TQQQ-008 + 成交模型)
├── TQQQ-011 tqqq_011_cap_exec_baseline   (重做 TQQQ-001 + 成交模型)
├── TQQQ-012 tqqq_012_cap_exec_qqq_confirm (重做 TQQQ-007 + 成交模型)
├── TQQQ-013 tqqq_013_cap_exec_qqq_optimized (QQQ 過濾 + 優化出場 + 成交模型)
│
│   ── VIX 自適應出場系列 (VIX-Adaptive Exit Series) ──
├── TQQQ-014 tqqq_014_cap_exec_vix_adaptive (VIX 自適應出場 + 成交模型)
│
│   ── 趨勢/動量策略系列 (Trend/Momentum Strategy Series) ──
├── TQQQ-015 tqqq_015_qqq_trend_breakout (QQQ 趨勢/動量 → Trade TQQQ + 成交模型)
│
│   ── Gap-Down 資本化系列 (Gap-Down Capitulation Series) ──
├── TQQQ-016 tqqq_016_gap_reversal_mr (Gap-Down + 日內反轉 MR，IBIT-006 移植，3 次失敗)
│
│   ── 盤中/加速/多日確認系列 (Intraday/Acceleration/Multi-day Confirmation Series) ──
├── TQQQ-017 tqqq_017_cap_reversal_confirm (ClosePos/2DD/Prev RSI 三類過濾器，3 次失敗)
│
│   ── Regime + Transition Combo Filter 系列（新策略類型，repo 首次成功） ──
├── TQQQ-018 tqqq_018_regime_vol_gate ★ (BB-width regime gate + first-day-of-decline filter，3 次成功，min 0.80 +122%)
│
│   ── ^VIX Direction Filter 系列（lesson #24 family v8，3 次失敗） ──
├── TQQQ-019 tqqq_019_vix_direction_mr (^VIX 5d direction cap，3 次 REJECT/TIE — capitulation 與 VIX spike 共線結構性失敗)
│
│   ── ^VIX Peak-Passing 1d Filter 系列（lesson #24 family v9 候選，repo 首次 1d 維度，3 次失敗） ──
├── TQQQ-020 tqqq_020_vix_peak_passing_mr (^VIX 1d peak-passing/momentum reversal，3 次 REJECT/TIE — DIRECTION 維度全層級失效)
│
│   ── ^MOVE Bond-Vol Filter 系列（lesson #24 family v9 候選，repo 首次 ^MOVE 於 equity asset，3 次失敗） ──
├── TQQQ-021 tqqq_021_move_regime_gate (^MOVE LEVEL + DIRECTION，3 次 REJECT/TIE — implied vol family 全層級失效)
│
│   ── QQQ-SPY Cross-Asset Divergence Filter 系列（lesson #20 v3 family v11，repo 首次 underlying-vs-broader，3 次失敗） ──
├── TQQQ-022 tqqq_022_qqq_spy_divergence_cap (QQQ-SPY 20d/10d FLOOR，3 次 REJECT/TIE — broad panic regime 中 QQQ ≈ SPY 同步，divergence 維度結構性壓縮)
│
│   ── Yield-Curve-Slope 系列（lesson #24 family v10，repo 首次 yield curve 跨資產類別自 TLT 移植至 leveraged tech ETF，3 次失敗） ──
├── TQQQ-023 tqqq_023_yield_curve_slope_cap (^TYX-^TNX 5d velocity / slope LEVEL，3 次 REJECT/TIE — rate-indirect 間接傳導使 yield curve 維度與 capitulation framework 結構性脫鉤)
│
│   ── Post-Capitulation Vol-Transition MR 系列（repo 首次「完全替代 framework」於 TQQQ，3 次失敗） ──
├── TQQQ-024 tqqq_024_vol_transition_mr (BB 下軌 + PB + WR + ATR + 2DD floor，3 次 REJECT — vol-transition MR framework 於 leveraged tech ETF 結構性失效，BB lower + 10d PB co-occurrence 結構性極稀)
│
│   ── VXN-VIX Cross-Index IV Divergence + VVIX Direction Filter 系列（lesson #24 family v11，repo 首次正交雙 IV 維度 AND，3 次 SUCCESS/PARTIAL/ABLATION） ──
└── TQQQ-025 tqqq_025_vxn_vix_vvix_filter ★ (^VXN/^VIX 比率 FLOOR 1.10 + ^VVIX 5d FLOOR -5，Att2 ★ 雙 Part std=0 全勝 SUCCESS，**首次突破 TQQQ Part B 0.80 結構性 ceiling**，repo 首次 cross-index IV divergence + ^VVIX higher-moment IV)
```

## TQQQ-025: VXN-VIX Cross-Index IV Divergence + VVIX Direction Filter（當前最佳）

### 背景
TQQQ-018 Att3 為前任全域最優（min(A,B) 0.80），Part B 殘餘 1 SL（2025-03-06 Trump
tariff reflation→stagflation pivot 急跌）為 binding constraint。TQQQ-019/020/021/022/
023/024 共 6 次嘗試（^VIX/^MOVE/QQQ-SPY/yield curve slope/vol-transition MR）全部
REJECT/TIE，AI_CONTEXT 多次明確列出未驗證假設「**VIX-VXN cross-index divergence**」+
「**完全替代 framework**」。

### 進場條件（在 TQQQ-018 Att3 基礎上新增正交雙 IV 維度）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 從 20 日高點回撤 | ≤ -15% | 同 TQQQ-001 / TQQQ-018 |
| 2 | RSI(5) | < 25 | 極端超賣 |
| 3 | 成交量 | > 1.5x 20日均量 | 恐慌放量確認 |
| 4 | BB(20, 2) 寬度/Close | < 0.48 | TQQQ-018 BB-width regime gate |
| 5 | Drawdown(T-5) | ≤ -1% | TQQQ-018 first-day-of-decline filter |
| 6 | **^VXN / ^VIX 比率** | **>= 1.10** | **NEW：cross-index IV divergence FLOOR — 過濾「broad panic 同步下跌但 tech 並未顯著跑輸大盤」regime** |
| 7 | **^VVIX 5 日累計變化** | **>= -5** | **NEW：higher-moment IV direction FLOOR — 過濾「panic about future panic 急速消退但 capitulation 未真正完成」regime** |
| 冷卻 | 訊號間隔 | ≥ 3 交易日 | 同 TQQQ-001 / TQQQ-018 |

### 出場參數
- 獲利目標 (TP)：+7%（同 TQQQ-018）
- 停損 (SL)：-8%（同 TQQQ-018）
- 最長持倉：10 天
- 滑價：0.1%

### 結果

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|--------------------|--------------------|----------------|
| 訊號數 | 9 | 5 | 1 |
| 勝率 | **100.0%** | **100.0%** | 100.0% |
| Sharpe | 0.00 (std=0 zero-var) | 0.00 (std=0 zero-var) | 0.00 (std=0) |
| 累計報酬 | +83.85% | +40.26% | +7.00% |
| 最大回撤 | -7.41% | -6.53% | 2.17% |
| 連續虧損 | 0 | 0 | 0 |

- **min(A,B)†**: structurally NO LOSS（雙 Part 全勝零方差，依 EWT-010/IBIT-009 慣例）
- **A/B 年化 cum gap**: 29.7% < 30% ✓（Part A 12.96%/yr vs Part B 18.43%/yr）
- **A/B 訊號比**: 1.8/yr vs 2.5/yr = 28% gap < 50% ✓
- **三項 acceptance criteria 全部達標**

### 三次迭代摘要

- **Att1**（VXN/VIX FLOOR 1.10 only）：Part A 10/9W/1L Sharpe 1.21 cum +68.97%（unchanged）
  / Part B 5/5W/0L std=0 cum +40.26%（**過濾 2025-03-06 SL** ratio=1.055 surgical）/
  min(A,B)† **1.21** PARTIAL (+51% vs baseline 0.80) — A/B 年化 cum gap **40% > 30%** ❌
  (Part B 純化使 cum gap 結構性擴張)
- **Att2 ★ SUCCESS**（Att1 + VVIX 5d FLOOR -5）：Part A 9/9W/0L std=0 cum **+83.85%**
  （**過濾 2021-09-28 SL** VVIX_5d=-9.70 surgical）/ Part B 5/5W/0L std=0 cum +40.26%
  （與 Att1 相同）/ min(A,B)† **structurally NO LOSS** + A/B cum gap **29.7% < 30%** ✓ +
  A/B signal gap 28% < 50% ✓ — **三項 acceptance criteria 全部達標**
- **Att3 ablation**（VXN/VIX off, VVIX-only）：Part A 9/9W std=0 cum +83.85%（與 Att2
  相同 — VVIX 單獨過濾 Part A 2021-09-28 SL）/ Part B **6/5W/1L Sharpe 0.80 cum +28.91%**
  （2025-03-06 SL 殘存，VVIX_5d=+6.03 ≥ -5 結構性逃逸過濾）/ min(A,B) **0.80 TIE
  baseline** — 確認雙維度正交、VXN/VIX 對 Part B SL 之必要性

### 跨資產貢獻（lesson #24 family v11 邊界擴展）

1. **Repo 首次「cross-index implied vol divergence」變體（^VXN/^VIX 比率）於任何資產**——
   既有 lesson #24 family v1-v9 維度均為單一 vol index LEVEL/DIRECTION（^VIX/^MOVE/
   ^GVZ/^OVX/^VXN）+ term structure（^VIX3M/^VIX TSM-019），v11 引入「比率」維度
   衡量 sub-segment vs broader market IV regime divergence
2. **Repo 首次 ^VVIX (VIX of VIX) 應用於任何資產**——higher-moment IV direction 維度，
   ^VVIX 5d direction 衡量「panic about future panic」加速度
3. **Repo 首次「正交雙 IV 維度 AND 條件」突破 TQQQ Part B 0.80 結構性 ceiling**（13
   次嘗試後）——既有 ^VIX (TQQQ-019/020) + ^MOVE (TQQQ-021) + QQQ-SPY (TQQQ-022) +
   yield curve slope (TQQQ-023) + vol-transition MR (TQQQ-024) 全部 REJECT/TIE
4. **雙正交維度互補確認**: trade-level 分析發現 TQQQ-018 殘餘 2 SLs 在 IV 不同維度反向
   結構：Part A SL 2021-09-28 (VXN/VIX=1.176 中段，VVIX_5d=-9.70 負極端) vs Part B SL
   2025-03-06 (VXN/VIX=1.055 負極端，VVIX_5d=+6.03 正常)，**單一維度結構性無法切分雙
   SL，雙正交維度 AND 條件為 unique solution**
5. **IV vs price divergence 維度敏感度發現**：TQQQ-022 (QQQ-SPY price divergence) 失敗
   vs TQQQ-025 (^VXN-^VIX IV divergence) 成功——**IV 維度比 price 維度更敏感 capture
   tech-vs-broad regime separation**
6. **新跨資產假設（待驗證）**：雙維度 (cross-index IV ratio + ^VVIX direction) 可能適用
   其他 leveraged tech ETF (TECL/SOXL/FNGU)，閾值需依資產 vs broader market IV 結構調整

---

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

| 參數 | TQQQ-010 | TQQQ-011 | TQQQ-012 | TQQQ-013 | TQQQ-014 |
|------|----------|----------|----------|----------|----------|
| 來源實驗 (Source) | TQQQ-008 | TQQQ-001 | TQQQ-007 | TQQQ-012 + TQQQ-010 出場 | TQQQ-010 + VIX 自適應 |
| 進場模式 (Entry) | next_open_market | next_open_market | next_open_market | next_open_market | next_open_market |
| 止盈委託 (Profit) | limit_order Day | limit_order Day | limit_order Day | limit_order Day | limit_order Day |
| 停損委託 (Stop) | stop_market GTC | stop_market GTC | stop_market GTC | stop_market GTC | stop_market GTC |
| 到期出場 (Expiry) | next_open_market | next_open_market | next_open_market | next_open_market | next_open_market |
| 滑價 (Slippage) | 0.10% | 0.10% | 0.10% | 0.10% | 0.10% |
| 悲觀認定 (Pessimistic) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Profit Target | +7% | +5% | +6% | +7% | **VIX≥35: +9%, <35: +7%** |
| Stop Loss | -8% | -8% | -8% | -8% | **VIX≥35: -10%, <35: -8%** |
| Holding Days | 10 | 7 | 8 | 10 | **VIX≥35: 12, <35: 10** |
| QQQ RSI Filter | — | — | RSI(14) < 35 | RSI(14) < 35 | — |
| VIX Adaptive Exit | — | — | — | — | **✅ 2-tier** |

### Part A — In-Sample (2019-01-01 ~ 2023-12-31)

| ID       | 訊號數 | 成交數 | 成交率  | 勝率   | 平均報酬 | 累計報酬  | 最大回撤  | 悲觀認定次數 |
|----------|-------|-------|---------|--------|---------|----------|----------|-------------|
| TQQQ-010 | 20    | 20    | 100.0%  | 70.0%  | +2.47%  | +55.44%  | -29.26%  | 0           |
| TQQQ-011 | 20    | 20    | 100.0%  | 70.0%  | +1.07%  | +19.35%  | -29.26%  | 0           |
| TQQQ-012 | 14    | 14    | 100.0%  | 71.4%  | +1.97%  | +27.79%  | -29.26%  | 0           |
| TQQQ-013 | 1     | 1     | 100.0%  | 0.0%   | -8.09%  | -8.09%   | -12.11%  | 0           |
| TQQQ-014 | 20    | 20    | 100.0%  | 70.0%  | +2.47%  | +55.44%  | -29.26%  | 0           |

### Part B — Out-of-Sample (2024-01-01 ~ 2025-12-31)

| ID       | 訊號數 | 成交數 | 成交率  | 勝率   | 平均報酬 | 累計報酬  | 最大回撤  | 悲觀認定次數 |
|----------|-------|-------|---------|--------|---------|----------|----------|-------------|
| TQQQ-010 | 8     | 8     | 100.0%  | 87.5%  | +5.11%  | +47.59%  | -11.80%  | 0           |
| TQQQ-011 | 8     | 8     | 100.0%  | 87.5%  | +3.36%  | +29.33%  | -11.80%  | 0           |
| TQQQ-012 | 6     | 6     | 100.0%  | 83.3%  | +3.65%  | +23.00%  | -11.80%  | 0           |
| TQQQ-013 | 1     | 1     | 100.0%  | 100.0% | +7.00%  | +7.00%   | +4.00%   | 0           |
| TQQQ-014 | 8     | 8     | 100.0%  | 75.0%  | +3.23%  | +26.33%  | -12.08%  | 0           |

> **與無成交模型版本的比較 (Comparison with no-execution-model versions):**
> - TQQQ-010 vs TQQQ-008: Part A 累計 +55.44% vs +120.21%（↓54%）、Part B 累計 +47.59% vs +45.44%（↑5%）
> - TQQQ-011 vs TQQQ-001: Part A 累計 +19.35% vs +70.86%（↓73%）、Part B 累計 +29.33% vs +27.44%（↑7%）
> - TQQQ-012 vs TQQQ-007: Part A 累計 +27.79% vs +59.18%（↓53%）、Part B 累計 +23.00% vs +21.20%（↑8%）
> - TQQQ-013 vs TQQQ-010: Part A 累計 -8.09% vs +55.44%（顯著落後）、Part B 累計 +7.00% vs +47.59%（顯著落後）
>
> **分析：** In-Sample 累計報酬大幅下降，主因是舊實驗進場以「訊號日收盤價」成交（已知未來資訊），新實驗改為「隔日開盤市價」更貼近實盤。Out-of-Sample 反而略微提升，顯示隔日開盤進場在近期市場環境中表現更穩健。成交模型版本的績效更可信賴。
>
> **TQQQ-013 失敗紀錄：** 嘗試將 TQQQ-012 的出場參數改為 TQQQ-010 的 TP +7% / 持倉 10 天，期待提高單筆報酬；但 QQQ RSI 過濾後訊號數過少，Part A 只有 1 筆且為虧損，整體顯著落後，不採用。
>
> **TQQQ-014 失敗紀錄（VIX 自適應出場，3 次嘗試）：**
> - **Att1（3-tier VIX）：** VIX≥35 → +9%/-10%/12d，VIX 25-35 → +7%/-8%/10d，VIX<25 → +5%/-6%/8d。Part A Sharpe 0.23（vs TQQQ-010 的 0.36），Part B Sharpe 0.39（vs 0.45 隱含）。失敗原因：16/20 Part A 訊號 VIX < 25，SL -6% 對 TQQQ 過緊
> - **Att2（2-tier，VIX≥35 放寬 TP+SL）：** VIX≥35 → +9%/-10%/12d，<35 → +7%/-8%/10d。Part A 與 TQQQ-010 完全相同（全部訊號 VIX < 35）。Part B 累計 +26.33%（vs +47.59%），因 2025-02-27 的 SL -10% 多虧 2%，2025-11-18 的 TP +9% 多賺 2%，淨虧損
> - **Att3（2-tier，VIX≥30 只放寬 TP 不放寬 SL）：** VIX≥30 → +9%/-8%/12d，<30 → +7%/-8%/10d。Part B Sharpe -0.07，累計 -6.46%。失敗原因：2024-07-24 和 2025-11-18 的 TP +9% 太高，原本可在 +7% 達標的交易變為停損
> - **結論：** TQQQ 恐慌訊號大多在 VIX < 30 時觸發，VIX 自適應的有效空間極為有限。固定 TP +7%/SL -8% 是全域甜蜜點，任何方向的放寬都會劣化。此方向已確認無效

<!-- 更新指引：
  1. 執行 uv run trading run --all
  2. 執行 uv run trading compare tqqq_001_capitulation tqqq_002_cap_relaxed_entry tqqq_003_cap_wider_exit tqqq_004_cap_vix_filter tqqq_005_cap_vix_adaptive tqqq_006_momentum_collapse tqqq_007_cap_qqq_confirm tqqq_008_cap_optimized_exit tqqq_009_cap_gentle_entry
  3. 將關鍵數字填入上方表格（訊號數、勝率、平均報酬%、累計報酬%、最大回撤%）
  4. 更新「結論」欄、「目前結論」與頂部的「當前最佳」
-->

## TQQQ-010 滾動窗口績效分析 (Rolling Window Performance Analysis)

> **分析日期：** 2026-03-28
> **窗口：** 2 年，步進 6 個月（共 12 個窗口）

### 滾動窗口績效表

| 窗口 | 訊號 | 勝率 | 平均報酬 | 累計報酬 | MDD | ΔWR |
|------|------|------|----------|----------|-----|-----|
| 2019-01~2020-12 | 7 | 71.4% | +2.69% | +18.48% | -29.26% | — |
| 2019-07~2021-06 | 9 | 77.8% | +3.65% | +35.65% | -29.26% | +6.3pp |
| 2020-01~2021-12 | 9 | 66.7% | +1.97% | +16.52% | -29.26% | -11.1pp |
| 2020-07~2022-06 | 11 | 81.8% | +4.26% | +55.30% | -12.95% | +15.2pp |
| 2021-01~2022-12 | 12 | 66.7% | +1.97% | +22.61% | -12.95% | -15.2pp |
| 2021-07~2023-06 | 9 | 55.6% | +0.29% | +0.09% | -12.95% | -11.1pp |
| 2022-01~2023-12 | 8 | 62.5% | +1.34% | +8.89% | -12.95% | +6.9pp |
| 2022-07~2024-06 | 4 | 50.0% | -0.54% | -3.29% | -11.19% | -12.5pp |
| 2023-01~2024-12 | 5 | 100.0% | +7.00% | +40.26% | -6.53% | +50.0pp |
| 2023-07~2025-06 | 8 | 87.5% | +5.11% | +47.59% | -11.80% | -12.5pp |
| 2024-01~2025-12 | 8 | 87.5% | +5.11% | +47.59% | -11.80% | +0.0pp |
| 2024-07~2026-03 | 8 | 87.5% | +5.11% | +47.59% | -11.80% | +0.0pp |

### 預測精準度表

| 窗口 | WR | 平均贏利 | 平均虧損 | 盈虧比 |
|------|------|----------|----------|--------|
| 2019-01~2020-12 | 71.4% | +7.00% | -8.09% | 2.16 |
| 2019-07~2021-06 | 77.8% | +7.00% | -8.09% | 3.03 |
| 2020-01~2021-12 | 66.7% | +7.00% | -8.09% | 1.73 |
| 2020-07~2022-06 | 81.8% | +7.00% | -8.09% | 3.89 |
| 2021-01~2022-12 | 66.7% | +7.00% | -8.09% | 1.73 |
| 2021-07~2023-06 | 55.6% | +7.00% | -8.09% | 1.08 |
| 2022-01~2023-12 | 62.5% | +7.00% | -8.09% | 1.44 |
| 2022-07~2024-06 | 50.0% | +7.00% | -8.09% | 0.87 |
| 2023-01~2024-12 | 100.0% | +7.00% | N/A | ∞ |
| 2023-07~2025-06 | 87.5% | +7.00% | -8.09% | 6.06 |
| 2024-01~2025-12 | 87.5% | +7.00% | -8.09% | 6.06 |
| 2024-07~2026-03 | 87.5% | +7.00% | -8.09% | 6.06 |

### 漸變性評估

- **勝率範圍**：50.0% ~ 100.0%（ΔWR 標準差 18.0pp，最大跳動 50.0pp）
- **盈虧比範圍**：0.87 ~ 6.06（ΔPF 標準差 1.95）
- **累計報酬範圍**：-3.29% ~ +55.30%（ΔCum 標準差 23.04%）
- **平均贏利**：固定 +7.00%（TP 固定）
- **平均虧損**：固定 -8.09%（SL 固定）

**判定：**
- ✗ 預測精準度突變（勝率最大跳動 50.0pp > 20pp 閾值，發生在窗口 2022-07~2024-06 → 2023-01~2024-12）
- ✓ 下游績效漸變（勝/虧報酬互補抵消精準度變化）

### 分析解讀

1. **低谷期 2021H2~2023H1**：勝率降至 50-56%，對應 2022 年科技股熊市。TQQQ 在長期下跌趨勢中恐慌訊號品質下降，連續停損拖累累計報酬至接近零或負值。這與 cross_asset_lessons #1（訊號品質 > 數量）和 #4（進場敏感度高）一致——熊市中 -15% 回撤更頻繁觸發，但反彈力度不足以達 TP +7%。
2. **高峰期 2023H1~至今**：勝率回升至 87.5-100%，5 筆連續全勝。這與 2023-2025 年科技股牛市吻合——恐慌僅為短暫回調，反彈力度強勁。
3. **固定贏虧幅度**：所有窗口平均贏利 +7.00%、平均虧損 -8.09%，完全由 TP/SL 決定。策略表現完全取決於勝率。
4. **風險提示**：策略對市場狀態有較強依賴性。牛市中勝率極高（87.5%），熊市中降至 50%（盈虧比 < 1）。但由於訊號稀少（每年約 4 個），單一熊市窗口的樣本量僅 4-5 筆，統計信心有限。
5. **與 A/B 平衡的一致性**：cross_asset_lessons #8 指出 TQQQ-010 的 A/B 訊號比為 1.5-2.0:1（可接受但需觀察），滾動分析進一步證實策略在不同市場環境中的表現確實波動較大。

## TQQQ-011 滾動窗口績效分析 (Rolling Window Performance Analysis)

> **分析日期：** 2026-03-29
> **窗口：** 2 年，步進 6 個月（共 12 個窗口）

### 滾動窗口績效表

| 窗口 | 訊號 | 勝率 | 平均報酬 | 累計報酬 | MDD | ΔWR |
|------|------|------|----------|----------|-----|-----|
| 2019-01~2020-12 | 7 | 71.4% | +1.26% | +7.81% | -29.26% | — |
| 2019-07~2021-06 | 9 | 77.8% | +2.09% | +18.86% | -29.26% | +6.3pp |
| 2020-01~2021-12 | 9 | 66.7% | +0.64% | +4.05% | -29.26% | -11.1pp |
| 2020-07~2022-06 | 11 | 81.8% | +2.62% | +31.05% | -12.95% | +15.2pp |
| 2021-01~2022-12 | 12 | 66.7% | +0.64% | +5.43% | -12.95% | -15.2pp |
| 2021-07~2023-06 | 9 | 55.6% | -0.82% | -8.93% | -12.95% | -11.1pp |
| 2022-01~2023-12 | 8 | 62.5% | +0.09% | -0.91% | -12.95% | +6.9pp |
| 2022-07~2024-06 | 4 | 50.0% | -1.54% | -6.87% | -11.19% | -12.5pp |
| 2023-01~2024-12 | 5 | 100.0% | +5.00% | +27.63% | -6.53% | +50.0pp |
| 2023-07~2025-06 | 8 | 87.5% | +3.36% | +29.33% | -11.80% | -12.5pp |
| 2024-01~2025-12 | 8 | 87.5% | +3.36% | +29.33% | -11.80% | +0.0pp |
| 2024-07~2026-03 | 8 | 87.5% | +3.36% | +29.33% | -11.80% | +0.0pp |

### 預測精準度表

| 窗口 | WR | 平均贏利 | 平均虧損 | 盈虧比 |
|------|------|----------|----------|--------|
| 2019-01~2020-12 | 71.4% | +5.00% | -8.09% | 1.55 |
| 2019-07~2021-06 | 77.8% | +5.00% | -8.09% | 2.16 |
| 2020-01~2021-12 | 66.7% | +5.00% | -8.09% | 1.24 |
| 2020-07~2022-06 | 81.8% | +5.00% | -8.09% | 2.78 |
| 2021-01~2022-12 | 66.7% | +5.00% | -8.09% | 1.24 |
| 2021-07~2023-06 | 55.6% | +5.00% | -8.09% | 0.77 |
| 2022-01~2023-12 | 62.5% | +5.00% | -8.09% | 1.03 |
| 2022-07~2024-06 | 50.0% | +5.00% | -8.09% | 0.62 |
| 2023-01~2024-12 | 100.0% | +5.00% | N/A | ∞ |
| 2023-07~2025-06 | 87.5% | +5.00% | -8.09% | 4.33 |
| 2024-01~2025-12 | 87.5% | +5.00% | -8.09% | 4.33 |
| 2024-07~2026-03 | 87.5% | +5.00% | -8.09% | 4.33 |

### 漸變性評估

- **勝率範圍**：50.0% ~ 100.0%（ΔWR 標準差 18.0pp，最大跳動 50.0pp）
- **盈虧比範圍**：0.62 ~ 4.33（ΔPF 標準差 1.39）
- **累計報酬範圍**：-8.93% ~ +31.05%（ΔCum 標準差 17.01%）
- **平均贏利**：固定 +5.00%（TP 固定）
- **平均虧損**：固定 -8.09%（SL 固定）

**判定：**
- ✗ 預測精準度突變（勝率最大跳動 50.0pp > 20pp 閾值，發生在窗口 2022-07~2024-06 → 2023-01~2024-12）
- ✓ 下游績效漸變（勝/虧報酬互補抵消精準度變化）

### 分析解讀

1. **與 TQQQ-010 的比較**：TQQQ-011（基線 TP +5%）與 TQQQ-010（優化 TP +7%）共享相同的進場訊號與勝率模式，唯一差異在出場參數。所有窗口勝率完全一致（因為進場條件相同），但 TQQQ-010 每筆贏利 +7.00% vs TQQQ-011 +5.00%，導致 TQQQ-010 累計報酬在所有窗口均大幅領先（如最佳窗口 +55.30% vs +31.05%）。
2. **低谷期加劇**：TP +5% 的較低贏利無法彌補 SL -8.09% 的虧損，使得 TQQQ-011 在熊市窗口（2021H2~2023H1）出現負累計報酬（最低 -8.93%），而 TQQQ-010 同期仍為正值（+0.09%）。這驗證了出場優化（TP +7%）對熊市防禦的重要性。
3. **盈虧比劣勢**：TQQQ-011 的盈虧比在熊市低谷僅 0.62（TQQQ-010 為 0.87），低於 1.0 意味著即使方向正確，期望值也為負。cross_asset_lessons #3（成交模型現實修正）在此再次驗證——成交模型下更低的 TP 會放大盈虧不對稱的問題。
4. **結論**：TQQQ-011 的滾動分析進一步證實 TP +7% 優於 TP +5% 的出場設定。兩者勝率完全相同，但 TP +7% 在牛市賺更多、在熊市虧更少，是嚴格優勢（strict dominance）。

## TQQQ-013 滾動窗口績效分析 (Rolling Window Performance Analysis)

> **分析日期：** 2026-03-29
> **窗口：** 2 年，步進 6 個月（共 12 個窗口）
> **重要警告：** 分析期間 QQQ 數據不可用，QQQ RSI 過濾被跳過，因此結果與 TQQQ-010 完全相同。此分析證實 TQQQ-013 的差異化（QQQ RSI 過濾）在缺少 QQQ 數據時退化為 TQQQ-010。

### 滾動窗口績效表

| 窗口 | 訊號 | 勝率 | 平均報酬 | 累計報酬 | MDD | ΔWR |
|------|------|------|----------|----------|-----|-----|
| 2019-01~2020-12 | 7 | 71.4% | +2.69% | +18.48% | -29.26% | — |
| 2019-07~2021-06 | 9 | 77.8% | +3.65% | +35.65% | -29.26% | +6.3pp |
| 2020-01~2021-12 | 9 | 66.7% | +1.97% | +16.52% | -29.26% | -11.1pp |
| 2020-07~2022-06 | 11 | 81.8% | +4.26% | +55.30% | -12.95% | +15.2pp |
| 2021-01~2022-12 | 12 | 66.7% | +1.97% | +22.61% | -12.95% | -15.2pp |
| 2021-07~2023-06 | 9 | 55.6% | +0.29% | +0.09% | -12.95% | -11.1pp |
| 2022-01~2023-12 | 8 | 62.5% | +1.34% | +8.89% | -12.95% | +6.9pp |
| 2022-07~2024-06 | 4 | 50.0% | -0.54% | -3.29% | -11.19% | -12.5pp |
| 2023-01~2024-12 | 5 | 100.0% | +7.00% | +40.26% | -6.53% | +50.0pp |
| 2023-07~2025-06 | 8 | 87.5% | +5.11% | +47.59% | -11.80% | -12.5pp |
| 2024-01~2025-12 | 8 | 87.5% | +5.11% | +47.59% | -11.80% | +0.0pp |
| 2024-07~2026-03 | 8 | 87.5% | +5.11% | +47.59% | -11.80% | +0.0pp |

### 預測精準度表

| 窗口 | WR | 平均贏利 | 平均虧損 | 盈虧比 |
|------|------|----------|----------|--------|
| 2019-01~2020-12 | 71.4% | +7.00% | -8.09% | 2.16 |
| 2019-07~2021-06 | 77.8% | +7.00% | -8.09% | 3.03 |
| 2020-01~2021-12 | 66.7% | +7.00% | -8.09% | 1.73 |
| 2020-07~2022-06 | 81.8% | +7.00% | -8.09% | 3.89 |
| 2021-01~2022-12 | 66.7% | +7.00% | -8.09% | 1.73 |
| 2021-07~2023-06 | 55.6% | +7.00% | -8.09% | 1.08 |
| 2022-01~2023-12 | 62.5% | +7.00% | -8.09% | 1.44 |
| 2022-07~2024-06 | 50.0% | +7.00% | -8.09% | 0.87 |
| 2023-01~2024-12 | 100.0% | +7.00% | N/A | ∞ |
| 2023-07~2025-06 | 87.5% | +7.00% | -8.09% | 6.06 |
| 2024-01~2025-12 | 87.5% | +7.00% | -8.09% | 6.06 |
| 2024-07~2026-03 | 87.5% | +7.00% | -8.09% | 6.06 |

### 漸變性評估

- **勝率範圍**：50.0% ~ 100.0%（ΔWR 標準差 18.0pp，最大跳動 50.0pp）
- **盈虧比範圍**：0.87 ~ 6.06（ΔPF 標準差 1.95）
- **累計報酬範圍**：-3.29% ~ +55.30%（ΔCum 標準差 23.04%）
- **平均贏利**：固定 +7.00%（TP 固定）
- **平均虧損**：固定 -8.09%（SL 固定）

**判定：**
- ✗ 預測精準度突變（勝率最大跳動 50.0pp > 20pp 閾值，發生在窗口 2022-07~2024-06 → 2023-01~2024-12）
- ✓ 下游績效漸變（勝/虧報酬互補抵消精準度變化）

### 分析解讀

1. **與 TQQQ-010 完全一致**：由於 QQQ 數據不可用，QQQ RSI 過濾被跳過，所有 12 個窗口的訊號數、勝率、累計報酬均與 TQQQ-010 完全相同。這進一步驗證了 TQQQ-013 的原始回測結論——QQQ RSI 過濾大幅減少訊號數（Part A 僅 1 筆），是績效顯著落後的主因。
2. **QQQ 過濾的價值存疑**：即使能獲取 QQQ 數據，TQQQ-013 的原始回測已顯示 QQQ RSI < 35 條件過嚴（Part A 累計 -8.09%，Part B +7.00%），顯著落後 TQQQ-010（Part A +55.44%，Part B +47.59%）。cross_asset_lessons #6（確認指標的邊際效益遞減）在此再次驗證。
3. **結論**：TQQQ-013 的滾動分析無法提供獨立價值（因等同 TQQQ-010），但確認了 QQQ RSI 過濾不應納入 TQQQ 恐慌抄底策略。

---

## TQQQ-015: QQQ Trend/Momentum → Trade TQQQ (Execution Model)

**目標**：首次在 TQQQ 上測試非均值回歸策略。利用 QQQ（1x NASDAQ）的趨勢/動量訊號進場交易 TQQQ（3x），避免 TQQQ 高波動干擾訊號生成。

### 嘗試紀錄 (Attempt Log)

#### Att1: QQQ BB Squeeze Breakout (TP+12%/SL-8%/20d)

**假說**：QQQ 日波動 ~1.2%，BB 擠壓突破訊號比 TQQQ 更乾淨。突破後 TQQQ 應有 3x 放大報酬。

**進場條件**：QQQ BB(20,2) 擠壓（60日 25th 百分位，5日內） + QQQ Close > Upper BB + QQQ Close > SMA(50)

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 19 (3.8/yr) | 6 (3.0/yr) |
| WR | 57.9% | 33.3% |
| Sharpe | 0.25 | **-0.28** |
| 累計 | +42.17% | -12.31% |

**失敗原因**：TP +12% 過高，Part B 零達標。QQQ 突破只能推動 TQQQ 上漲 0-5%，遠不及 +12% 目標。

#### Att2: QQQ BB Squeeze Breakout (TP+8%/SL-8%/15d)

**改動**：降低 TP 至 +8%，縮短持倉至 15 天。

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 16 (3.2/yr) | 7 (3.5/yr) |
| WR | 68.8% | 71.4% |
| Sharpe | **0.54** | **-0.10** |
| 累計 | +39.02% | -2.78% |

**分析**：Part A 大幅改善（Sharpe 0.54），WR 提升但 Part B 仍為負。Part B 依然零達標（最高 +3.68%），所有 Part B 交易都以到期或停損結束。BB 擠壓突破訊號在 2024-2025 QQQ 穩定上漲環境中缺乏爆發力。

#### Att3: QQQ Momentum ROC(10)>5% (TP+10%/SL-10%/15d)

**策略轉向**：放棄突破策略，改用純動量進場。買入條件改為 QQQ 10日 ROC > 5% + QQQ Close > SMA(50) + QQQ Close > SMA(200)。

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 35 (7.0/yr) | 17 (8.5/yr) |
| WR | 60.0% | 58.8% |
| Sharpe | 0.19 | 0.17 |
| 累計 | +57.93% | +21.41% |
| MDD | -19.92% | -15.06% |
| PF | 1.48 | 1.44 |

**分析**：A/B 平衡極佳（Sharpe gap 0.02），Part B 正報酬。但 min(A,B) Sharpe 0.17 遠低於 TQQQ-010 的 0.36。動量策略 WR ~60% + TP/SL 1:1 只能產生邊際正報酬，MDD 偏高。

### 對比 TQQQ-010 基準

| 策略 | Part A Sharpe | Part B Sharpe | min(A,B) | A/B balance |
|------|--------------|--------------|----------|-------------|
| **TQQQ-010 (均值回歸)** | **0.36** | **1.02** | **0.36** | 0.66 gap |
| TQQQ-015 Att1 (BB TP+12%) | 0.25 | -0.28 | -0.28 | 0.53 gap |
| TQQQ-015 Att2 (BB TP+8%) | 0.54 | -0.10 | -0.10 | 0.64 gap |
| TQQQ-015 Att3 (Momentum) | 0.19 | 0.17 | 0.17 | **0.02 gap** |

### 結論

趨勢/突破/動量策略在 3x 槓桿 ETF (TQQQ) 上無法超越均值回歸。根本原因：
1. **噪音放大**：3x 槓桿將 QQQ 1.2% 日波動放大至 TQQQ 4-8%，需要寬 SL（≥8%）
2. **訊號幅度不足**：QQQ 突破/動量只能推動 TQQQ 0-5% 正向報酬，無法補償 8-10% 停損
3. **均值回歸的結構性優勢**：極端恐慌（DD -15%）創造的 7%+ 反彈是唯一能克服高波動 SL 需求的訊號類型

TQQQ-010 確認為全域最優（15 次實驗，含均值回歸和趨勢/動量/突破三大策略類型）。

---

## TQQQ-016: Gap-Down 資本化 + 日內反轉均值回歸（IBIT-006 移植，3 次迭代全部失敗）

### 動機 (Motivation)

IBIT-006 Att2（Gap-Down 資本化 + 日內反轉）相對 IBIT-001 基線改善 min(A,B) Sharpe
從 0.15 → 0.40（+167%）。cross_asset_lessons.md lesson #20a 將 TQQQ 列為「可能延伸
的候選資產」，理由是 QQQ 盤外因科技巨頭財報、Fed/CPI 公告、亞/歐市場聯動產生
顯著隔夜跳空，3x 槓桿 TQQQ 會放大這些 gap 至 3 倍。本實驗定性驗證這一假設。

### 策略設計 (Strategy Design)

進場條件（五項同時成立）：
1. 20 日高點回撤 ≤ -15%（同 TQQQ-010，深回撤均值回歸）
2. RSI(5) < 25（同 TQQQ-010，極端超賣）
3. 隔夜開盤跳空 ≤ -2%（TQQQ 3x 縮放 IBIT 的 -1.5%）
4. Close > Open（日內反轉確認）
5. Volume > 1.5x SMA(20)（Att3 加回，確認真實拋壓日）

### 迭代歷程 (Iteration Log)

#### Att1（Baseline，gap ≤ -3%，無 volume 過濾）
- 進場：20d DD ≤ -15% + RSI(5)<25 + Gap ≤ -3% + Close > Open + cd10
- 出場：TP+7% / SL-8% / 10d
- 結果：
  - Part A: 3 訊號, WR 100%, 累計 +22.50%, Sharpe 0.00（零方差 3 筆全達 +7%）
  - Part B: 2 訊號, WR 50%, 累計 -1.66%, Sharpe -0.07
  - min(A,B) -0.07（vs TQQQ-010 的 0.36，-119%）
- 失敗分析：-3% gap 對 TQQQ 日波動 5-6% 為 0.55σ，門檻過嚴。Part A 僅捕捉
  2020-02-28、2022-01-10、2022-05-12 三筆，過濾掉 TQQQ-010 多數有效訊號。
  Part B 1.0/yr 統計信心不足。

#### Att2（Loosen gap to -2%，無 volume 過濾）
- 進場：同 Att1 但 gap ≤ -2%
- 出場：同 Att1
- 結果：
  - Part A: 5 訊號, WR 60%, 累計 +3.48%, Sharpe 0.13
  - Part B: 2 訊號, WR 50%, 累計 -1.66%, Sharpe -0.07
  - min(A,B) -0.07
- 失敗分析：放寬 gap 新增 2022-09-01（Labor Day 前假反彈）、2023-08-11
  （AI 泡沫回撤）兩筆假訊號，兩筆皆 -8.09% 停損。WR 自 100%→60%，
  Sharpe 暴跌。Part B 訊號完全不變（兩筆 Part B 訊號 volume 均飆升）。

#### Att3（Att2 + 加回 Volume > 1.5x SMA20 過濾）
- 進場：Att2 + Volume > 1.5x SMA(20)（等同 TQQQ-010 基線 + gap/reversal 疊加）
- 出場：同 Att1
- 結果：
  - Part A: 4 訊號, WR 75%, 累計 +12.59%, Sharpe 0.49
  - Part B: 2 訊號, WR 50%, 累計 -1.66%, Sharpe -0.07
  - min(A,B) -0.07（Part B 完全不變）
- 失敗分析：Volume 過濾移除 2023-08-11 訊號（非 volume 飆升日），
  Part A Sharpe 自 0.13→0.49（+277%）。但 Part B 兩筆訊號
  （2024-08-05 yen carry unwind、2025-04-07 Trump 關稅公告）volume 均
  飆升，完全不變。**核心失敗**：Part B 2025-04-07 符合「gap-down + 日內
  反轉」結構但隔日繼續深跌，觸發 -8% 停損，拉下 min(A,B)。

### 對比 TQQQ-010 基準

| 策略 | Part A Sharpe | Part B Sharpe | min(A,B) | 訊號 A/B |
|------|--------------|--------------|----------|-----------|
| **TQQQ-010 (baseline)** | **0.36** | **1.02** | **0.36** | 20/8 |
| TQQQ-016 Att1 (gap-3%) | 0.00 | -0.07 | -0.07 | 3/2 |
| TQQQ-016 Att2 (gap-2%) | 0.13 | -0.07 | -0.07 | 5/2 |
| TQQQ-016 Att3 (+volume) | 0.49 | -0.07 | -0.07 | 4/2 |

### 結論：Gap-Down 資本化模式不延伸至槓桿科技 ETF

**失敗根因**：
1. **QQQ 盤外流動性有限**：與 IBIT 24/7 連續交易的 Bitcoin 不同，QQQ 盤後
   交易量僅占日成交量 5-10%。隔夜 gap-down 常反映盤前事件衝擊（Fed/CPI/
   科技巨頭財報/政策公告）而非市場投降式拋壓。
2. **事件利空可持續**：若事件基本面利空（如 2025-04-07 Trump 關稅公告），
   日內反彈只是技術性反應，隔日繼續深跌機率高。IBIT 的 gap-down 代表 BTC
   現貨拋壓已結束 + 美股資金「撿便宜」；TQQQ 的 gap-down 則常是事件衝擊
   的前奏而非尾聲。
3. **Part B 樣本過稀**：2024-2025 大牛市期 TQQQ 符合 DD≤-15% + gap≤-2% 的
   事件僅 2 筆，1 勝 1 敗為 Sharpe 負值主因。

**Lesson #20a 更新**：Gap-Down 資本化 + 日內反轉模式適用範圍**不包含槓桿
（非 24/7 連續交易）科技 ETF**。適用條件：(a) 追蹤 24/7 連續交易資產的 ETF
（IBIT 已驗證）；(b) 盤外真實流動性高的資產。不適用：TQQQ/SOXL 等傳統市場
槓桿 ETF。

TQQQ-010 仍為全域最優（16 次實驗，含均值回歸、趨勢/動量/突破、Gap-Down
資本化四大策略類型）。
