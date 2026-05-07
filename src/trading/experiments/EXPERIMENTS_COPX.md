<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-05-07
  gradient_validated: 2026-03-30
  data_through: 2025-12-31
  note: COPX-015 added 2026-05-07 (^VIX FLOOR Filter on Multi-Week Regime-Aware BB Squeeze Breakout, **repo 第 2 次 lesson #24 family FLOOR 變體跨資產驗證 + 首次 ^VIX FLOOR 變體於商品/礦業 ETF + cross-asset port from FCX-015 Att2**, cross-asset port from FCX-015 commodity miners single stock to commodity miners ETF). Three iterations, **Att1 PARTIAL — Part A 大幅改善但 Part B 結構性無法改善 min(A,B) TIE baseline**: Att1 (mode=floor, vix_low=14.0, FCX-015 sweet spot 直接移植) Part A 7/**100% WR**/Sharpe **2.81** cum +51.26% MDD -5.74% (vs COPX-011 Att3 baseline 10/80%/0.72/+40.03%/-6.57%, **+290% Sharpe / +20pp WR / +11pp cum**) — VIX FLOOR 14 cleanly 過濾全部 3 個 Part A 失敗訊號（VIX 13.40 SL / VIX 13.54 EX -4.63% / VIX 12.19 EX +3.42%）/ Part B 2 訊號**完全等於 baseline** (50% WR, Sharpe 0.64) — 兩筆 Part B 訊號 VIX 皆 > 14 (18.48 TP / 16.59 EX -1.54%)，FLOOR 不綁定 / min(A,B) **0.64**（與 baseline TIE，Part B 為 binding constraint）/ A/B 年化 cum gap 73.9% (vs baseline 66.4%, 失衡惡化) / signal gap 71.4% (vs baseline 50%); Att2 (mode=floor, vix_low=17.0, target Part B EX 過濾) Part A 5/100%/Sharpe **2.32** cum +32.12% / Part B 1/100% std=0 cum +7.00% / min(A,B)† **2.32** by † 慣例 (Part B std=0 結構性零方差，沿用 EWJ-003/SPY-009/DIA-012/IWM-013/TLT-014 約定) BUT REJECT — Part B 1 訊號統計顯著性嚴重不足，A/B signal ratio 5:1 = 80% gap 嚴重違反 50% 目標, A/B cum gap 45.5% > 30%; Att3 (mode=floor, vix_low=13.0, threshold robustness loosen test) Part A 9/77.8%/Sharpe **0.69** cum +35.40%（接近 baseline 0.72）/ Part B 不變 / min **0.64** — 放寬至 13 將 13.40 SL + 13.54 EX -4.63% 放回, 確認 FLOOR 14 為 sweet spot. **核心發現（lesson #24 family v6 + lesson #19 family 邊界擴展，repo 首次發現）**: (1) **FCX-015 FLOOR 14 假說在 COPX 同樣有效於 Part A 失敗訊號過濾**——FLOOR 方向正確跨資產一致（commodity/mining single stock → commodity/mining ETF）, Part A SL/EX 同樣集中於 low-VIX calm regime; (2) **COPX Part B sample size 結構性限制**——COPX-011 Att3 regime BOX 後 Part B 僅 2 訊號（vs FCX-015 Part B 3+ 訊號），單一 VIX FLOOR 無法經由 Part B 改善 min(A,B); (3) **新跨資產規則 lesson #24 v6**：^VIX FLOOR 變體於 commodity/mining BB Squeeze Breakout 框架在「Part A SL/EX 集中於 calm regime + Part B 訊號數 >= 3」雙條件下有效——FCX 個股滿足兩條件 ✓ ; COPX ETF 因 Part B 僅 2 訊號失敗第二條件 ✗ — sample size precondition 為跨資產 FLOOR 移植的新規則; (4) **VIX 維度區分力邊界**：Part B EX (VIX 16.59) 與 Part B TP (VIX 18.48) 過於接近，純 VIX FLOOR 無法切分; signal-day 1d return 維度（EX 6.07% vs TP 1.71%）較 VIX 維度更顯著但與 Part A winner 2021-02-16 (1d 6.09%) 重疊; (5) **A/B 失衡結構性**：Part A 受惠於 2020-2021 COVID 復甦 + 商品超級週期, Part B 為 2024-2025 銅震盪期, 任何 Part A 訊號品質改善皆惡化 A/B cum gap (Att1 0.72→2.81 對應 cum gap 66.4→73.9%); (6) **重要部分成功**：雖 min(A,B) TIE baseline, Att1 對 Part A 290% Sharpe 提升 + 100% WR 為實質改善——repo 第 2 次 ^VIX FLOOR 變體驗證 + 首次 commodity/mining ETF FLOOR 驗證為跨資產 lesson #24 family 重要邊界發現. COPX-015 Att1 為 COPX 第 15 次實驗（57+ 次嘗試），Att1 驗證 lesson #24 FLOOR 跨資產一致性但 min(A,B) 不超越 COPX-011 Att3 0.64. COPX-014 added 2026-05-07 (Cross-Asset Divergence Regime-Gated BB Squeeze Breakout, **repo 第 3 次 cross-asset divergence regime gate 試驗、首次商品/礦業 ETF + BB Squeeze Breakout 組合 — 全部失敗**, cross-strategy port from TLT-014 / TSLA-017). Three iterations all failed vs COPX-011 Att3 全域最佳 0.64. Att1 (GLD lookback=20 threshold=-0.05, lenient TLT-014 reference) 訊號集完全等於 baseline 無過濾效果——所有 12 訊號 Rel_GLD ≥ -0.18% > -5%，threshold 過於寬鬆。Att2 (GLD lookback=20 threshold=+0.05) Part A 9/66.7%/Sharpe **0.36** cum +16.96% / Part B 2 訊號不變 / min **0.36** REJECT — 過濾 5 訊號（含 1 SL + 4 wins），但 cooldown chain shift 引入 4 個替代訊號（2019-04-04 SL 同源 -6.14% / 2019-12-12 EX +2.28% 替換 +7% TP / 2023-01-10 EX **-3.49% 新增大型 EX-** / 2023-12-14 EX +0.98% 替換 +3.42%），淨效果為 1 SL + 4 wins → 1 SL + 3 weaker winners。Att3 (XLB lookback=20 threshold=+0.005, surgical anchor) Part A 10 訊號完全等於 baseline Sharpe **0.72** / Part B 2 訊號不變 / min **0.64** REJECT — XLB 為更精準 anchor（COPX 為材料板塊內子集合），threshold +0.005 surgical filter 命中唯一 outlier 2019-04-01 SL（Rel_XLB +0.0018 vs 其餘 11 訊號 +0.0094~+0.1469），但 cooldown chain shift 重新激活 2019-04-04 SL 同源 -6.14%，filter 效應完全被中性化。**核心失敗模式（lesson #20 v3 邊界擴展，repo 首次發現）**：(1) **訊號日 Rel_anchor 結構偏多**：BB Squeeze breakout 進場日 COPX 已突破上軌（短期強勢），Rel_GLD/SPY/XLB 多為正值，「下限 floor」式 divergence gate 過於寬鬆；(2) **過嚴 threshold 觸發 cooldown chain shift**：cooldown_days=12 內必然激活鄰近替代訊號，COPX 多年期失敗模式（Q1 2019 base-metals false rally / mid-2023 China weakness / 2025 Q2 metal pullback）橫跨 1-2 週，鄰近訊號通常具相同失敗結構；(3) **Surgical filter 受 cooldown shift 中性化**：精準過濾單一 SL 的努力被 cooldown 內同源失敗訊號完全抵消。**新跨資產規則（lesson #20 v3）**：cross-asset divergence regime gate 適用邊界 = 「cooldown 視窗 × 訊號密度」應遠 < 1.0（密集訊號流，filter 效應不被 cooldown shift 抵消）；TLT-014 ✓（cooldown 7d × 密度 ~3.5/yr ≈ 0.07）/ TSLA-017 ✓（cooldown 10d × 密度 ~5/yr ≈ 0.20）/ COPX-014 ✗（cooldown 12d × 密度 ~2/yr ≈ 0.10 但加上 BB Squeeze breakout 訊號日 Rel 結構偏多使邊界值不適用）。**lesson #20 v3 + lesson #19 family 整合**：稀疏訊號流（< 5/yr）+ 高 cooldown（≥10d）+ 訊號日進場條件已過濾「方向性弱勢」的策略類型（如 BB Squeeze breakout），cross-asset divergence 結構性失效——可用於 MR 框架（capitulation 訊號日已偏弱，divergence 可正向篩選）但不適用於 breakout 框架。COPX-014 為 COPX 第 14 次失敗策略類型（後於均值回歸、波動率自適應、突破、配對、動量、ATR 自適應、RSI(2)、BB 下軌混合、RSI hook、2DD/1DD filter、Donchian、RS 動量、ATR ceiling/5d cap、macro confirmed、cross-asset divergence breakout 共 14 大方向）。COPX-011 Att3 仍為全域最優（14 次實驗、54+ 次嘗試）。COPX-013 added 2026-05-05 (Macro-Confirmed Vol-Adaptive Capitulation MR, **repo 第 3 次 lesson #25 cross-asset 試驗、首次 commodity miners ETF 上 lesson #24 + #25 雙來源組合 — 全部失敗**, cross-asset port from IWM-015 + cross-strategy port to commodity miners ETF). Three iterations all failed vs COPX-011 Att3 全域最佳 0.64. Att1 (SPY 10d <= 0%, loose threshold) Part A 20/80.0%/Sharpe **0.57** cum +43.39% (+27% Part A 改善 vs baseline 0.45) / Part B 8/75.0%/Sharpe **0.42** cum +11.78% (-26% vs baseline 0.57，cooldown chain shift 引入新 SL 2024-07-22 替換被過濾的 2024-07-18) / min **0.42** REJECT vs 0.64; Att2 (SPY 10d <= -1.5%, IWM-015 sweet spot 直接移植) Part A 16/75.0%/Sharpe **0.42** cum +24.95% (-1.5% 閾值過嚴切除 6 個 -1.5%~0 中性帶 winners) / Part B 6/83.3%/Sharpe **0.71** cum +13.26% (+25% Part B 改善 vs baseline) / min **0.42** REJECT — A/B 平衡達標 (cum gap 24.7%<30% / signal ratio 1.07:1) 但 Part A 退化使 min 不變; Att3 (SPY 10d <= 0 AND VIX 3d <= +5, 雙來源 lesson #24 + #25 組合) Part A 15/**60.0%**/Sharpe **0.06** cum +2.49% (max consec losses **4**! WR 76.2%→60%) / Part B 8/75%/Sharpe 0.42 / min **0.06** REJECT (三次最差) — 雙閘門組合理論覆蓋全部 7 SLs，但激活原本被壓制的 5 個新 Part A SLs（含 2 連續 SLs 模式），cooldown chain shift 結構性放大反向選擇. **核心失敗模式**: cooldown chain shift（lesson #19 family）系統性抵消濾波效應——當基礎策略 cooldown 12 日 + 訊號密度 ~4/yr，過濾任何訊號解除 12 日 cooldown lockout 激活鄰近訊號，COPX 的 SLs 與 winners 在 SPY 10d/VIX 3d 維度無乾淨分隔。**lesson #25 cross-asset hypothesis REJECT**: 既有 lesson #25 僅適用「broad-market 為主要驅動因子的 sub-segment ETF」（IWM small-cap ✓），不適用 commodity miners ETF（COPX winners SPY 10d 廣泛分布 -9.13%~+4.72%，無單向 macro confirmation 區分力）。**lesson #19 family 邊界擴展**：當基礎策略 cooldown ≥10 日 + 訊號密度 < 5/yr + filter 過濾比例 > 40% 時，cooldown chain shift 結構性放大反向選擇——多重 macro filter 疊加為 lesson #19 family 中的「chain-shift collapse」失敗模式（repo 首次發現）。**新失敗家族擴展**: lesson #25 適用邊界精煉至「broad-market 為主要驅動因子的 sub-segment ETF」（IWM ✓ / XBI ✗ / COPX ✗）；lesson #24 + #25 雙來源組合在 chain-shift 敏感策略上結構性失敗。COPX 第 13 次失敗策略類型，COPX-011 Att3 仍為全域最優（13 次實驗、51+ 次嘗試）。COPX-012 added 2026-05-01 (Volatility-Acceleration-Bounded MR, **repo 第 3 次 ATR ratio CEILING 跨資產試驗、repo 首次商品/礦業 ETF BAND 驗證 — 全部失敗**, cross-asset port from CIBR-014 Att2 / FXI-014 Att2 / URA-013 Att2). Three iterations all failed vs COPX-007 baseline 0.45 與全域最佳 COPX-011 Att3 0.64. Att1 (CEILING <= 1.40, CIBR-014 reference 直接移植) Part A 20/70.0%/Sharpe **0.28** cum +21.72% / Part B 9/77.8%/Sharpe 0.50 cum +15.70% / min **0.28** — CEILING 1.40 過濾 1 個 Part A winner + 1 個 Part B winner 並觸發 lesson #19 cooldown chain shift（max consec losses 2→4，連續 4 個 Part A SLs：2019-05-06/2019-08-01/2020-01-28/2020-02-25）；Att2 (CEILING <= 1.55 放鬆至最極端) Part A 21/71.4%/Sharpe **0.32** cum +25.98% / Part B 10/80.0%/Sharpe 0.57 cum +19.74%（Part B 完全不變）/ min **0.32** — CEILING 1.55 對 Part B 非綁定，但 Part A 訊號日期改變（cooldown chain shift），新訊號為 SL；Att3 (停用 CEILING + 5d return cap >= -8%, URA-013 cross-asset port) Part A 14/57.1%/Sharpe **0.00** cum -0.98% / Part B 8/87.5%/Sharpe **0.92** cum +21.32%（**+62% vs baseline**）/ min **0.00** — 5d cap -8% 過濾 7 個 Part A 訊號幾乎全為 winners（COPX winners 系統性伴隨深 5d 累計跌幅 -8%~-15%），但 Part B 受惠於過濾 2024-07-19 SL（5d -8.5%）。**核心發現**：(1) **COPX winners 在 ATR ratio 維度反向於 CIBR/FXI**——COPX 高品質 panic flush bounces 伴隨 ATR ratio > 1.40 in-crash acceleration，與 CIBR (FDA news-driven 持續崩盤) / FXI (policy continuation 持續崩盤) 結構**反向**；(2) **COPX winners 在 5d return 維度反向於 URA**——COPX winners 集中深 5d capitulation (-8%~-15%)，URA winners 集中淺 5d (-3%~-8%)，cap 方向結構相反；(3) **新跨資產規則（lesson #15 v2 + #19 v8 邊界擴展）**：任何 oscillator/return-based 上限濾波器（CEILING / cap 方向）對「商品超級週期驅動的礦業 ETF」（COPX、CIBR-XME 類別）結構性失效——winners 與 losers 在 acceleration / multi-day decline 維度的分布**winners 偏深**且跨完整範圍，無單一切點可區分；(4) **與 FCX-013 lesson #22 反向發現平行**（k=1.00 嚴格優於 k<1 buffered），共同確認商品/礦業類別「extreme regime entry 策略空間」與其他資產類別不同。**Att3 Part B 改善 +62%（0.57→0.92）為唯一 partial signal**——5d cap 雖過濾 Part B 1 SL 為甜蜜方向，但與 Part A 災難性退化不可調和。COPX 第 12 次失敗策略類型（後於突破、配對、動量、ATR 自適應、RSI(2)、BB 下軌混合、RSI hook、2DD/1DD filter、Donchian、RS 動量、ATR ceiling/5d cap 共 12 大方向）。COPX-011 Att3 仍為全域最優（12 次實驗、51+ 次嘗試）。COPX-011 added 2026-04-28 (Multi-Week Regime-Aware BB Squeeze Breakout, **repo 第 4 次 lesson #22 跨資產試驗，首次商品/礦業 ETF 驗證**, cross-asset port from FCX-013). Three iterations, **Att3 SUCCESS — repo 首次 regime BOX（k_min + k_max 雙向）發現**. Att1 (k_min=1.00 strict, FCX-013 直接移植) FAILED min(A,B) **-0.04** Part A 14/78.6%/Sharpe **0.65**（+97% vs COPX-005 baseline 0.33）/ Part B 3/33.3%/Sharpe -0.04 — k=1.00 強過濾 Part A 弱 regime SLs，但同時過濾 Part B 唯一 transition winner（2024-03-06 TP，ratio ~0.99）並觸發 lesson #19 cooldown chain shift 引入 2024-05-14 SL（ratio ~1.094 過熱）。Att2 (k_min=0.99 buffered, TSLA 移植) FAILED min(A,B) **0.28** Part A 14/71.4%/Sharpe 0.43 / Part B 4/50%/Sharpe 0.28 — k=0.99 緩衝保留 2024-03-07 TP 解除 cooldown shift 副作用，但同時放行 2020-10-23 Part A SL，且 2024-05-14 SL（ratio 1.094）仍未過濾。Att3 ★ (regime BOX = [k_min=1.00, k_max=1.09]，雙向 regime 過濾) SUCCESS min(A,B) **0.64**（+42% vs COPX-007 baseline 0.45）Part A 10 訊號 WR **80.0%**/Sharpe **0.72** cum +40.03% MDD -6.57% PF 4.29（6 TP / 1 SL / 3 EX）/ Part B 2/50%/Sharpe **0.64** cum +5.35%（1 TP / 1 EX，2024-05-14 SL ratio 1.094 被 k_max=1.09 精準過濾）。**核心發現（repo 首次 regime BOX）**：(1) 商品/礦業 ETF（COPX）vs 個股（FCX）regime 結構差異：FCX 個股 Part B SL 集中於 ratio<1.00（k_min=1.00 解決），COPX ETF Part B SL 集中於 ratio>1.09 過熱牛末（需 k_max=1.09）；(2) ETF 平均化效應使 SMA20/SMA60 ratio 變化更平滑，過熱訊號在 ETF 上更明顯（個股波動使 ratio 噪音消除過熱信號）；(3) lesson #22 v2 精煉：buffered SMA regime 在商品/礦業類資產的應用上，ETF 形式需 BOX 結構（k_min + k_max 雙向）。**Acceptance criteria**：✓ Sharpe +42% > 基線 / ✗ A/B annualized cum gap 66.4%（>30%，COPX 結構性邊界，與 FCX-013 Att3 44% 同類）/ ~ A/B annualized signal gap 50%（boundary）/ ✓ 成交模型完整 / ✓ Repo 較少使用方向（lesson #22 第 4 次跨資產 + repo 首次 regime BOX）。**新跨資產規則**：lesson #22 buffered SMA regime 對商品/礦業類資產，個股形式需單純下限（FCX-013 k=1.00），ETF 形式需 BOX（COPX-011 [1.00, 1.09]）—— 推測 ETF 平均化效應為機制差異根源。COPX-011 Att3 為新全域最優（11 次實驗、48+ 次嘗試）。COPX-010 added 2026-04-23 (Post-Capitulation Vol-Transition MR, **repo first 2DD/1DD entry-time filter trial on commodity ETF**, cross-asset port from CIBR-012 Att3). Three iterations all failed vs COPX-007 min 0.45. **Trade-level analysis (n=21 Part A trades) reveals COPX winners and losers cannot be reliably distinguished by 2DD or 1DD direction**: losers Pullback -10~-13%/2dRet +0.2~-7.5%/1dRet -2.1~-5.3% overlap with winners' broader ranges. Att1 (2DD cap >= -5.5% CIBR direction) Part A WR 76.2%->61.1% Sharpe 0.08 — cap removed deep-2DD winners (COPX winners 2dRet typically deeper than losers, OPPOSITE to CIBR pattern). Att2 (2DD floor <= -3% EEM/INDA direction) Part A unchanged (most signals naturally have deep 2DD) but Part B WR 80%->66.7% Sharpe 0.21 — filtered 5 shallow-2DD winners (2024-01-22, 2024-08-07, 2024-12-17, 2025-03-03, 2025-11-20). Att3 (weak-capitulation filter: skip if 1DD>-3% AND ClosePos>0.30, best of 3) precisely targeted 2 weak-capitulation losers (2019-05-06 1DD-2.12%/CP0.97, 2025-03-31 1DD-2.35%/CP0.81); Part A 0.38 / **Part B 0.57 unchanged** (filter+cooldown shift exchange 1W+1L for 1W+1L) / min **0.38**. **A/B balance achieved (cum diff 28.6%<30%, signal ratio 1.9:1<50%) but Part A Sharpe degraded by cooldown chain shift (lesson #19) introducing 2019-05-13 new SL (4-month trade war continuation)**. **Cross-asset finding**: REJECT CIBR-012 cross-asset hypothesis on COPX 2.25% vol commodity ETF — CIBR 1.53% vol losers cluster deep 2DD (cap effective), COPX winners span deep+shallow 2DD (cap/floor both fail). Extends lesson #20b failure family to "single-day momentum filter" category on commodity ETFs — paralleling TQQQ-017 (ClosePos/2DD/Prev RSI failure on leveraged index). COPX-010 superseded by COPX-011 as global optimum.
-->
## AI Agent 快速索引

**當前最佳：** COPX-011 Att3 ★（Multi-Week Regime-Aware BB Squeeze Breakout，regime BOX [k_min=1.00, k_max=1.09]，TP+7%/SL-6%/20d/cd12，Part A Sharpe **0.72**，Part B Sharpe **0.64**，min(A,B) **0.64**，+42% vs COPX-007 baseline 0.45）
**前任最佳：** COPX-007（COPX-003 框架 + ATR(5)/ATR(20) > 1.05 波動率自適應過濾，Part A Sharpe 0.45，Part B Sharpe 0.57，min(A,B) 0.45，+28.6% vs COPX-003）
**前前任最佳：** COPX-003（20日回檔 10-20% + WR(10) ≤ -80 + SL -4.5%，Part A Sharpe 0.39，Part B Sharpe 0.35）
**滾動窗口分析摘要：** COPX-001 ✓✓ 雙漸變（ΔWR max 9.2pp，10/12 正報酬窗口）
**最新實驗：** COPX-015（^VIX FLOOR Filter on BB Squeeze Breakout，FCX-015 Att2 cross-asset port，**3 次嘗試 Att1 PARTIAL** — Part A Sharpe 0.72→**2.81** (+290%) WR 80→100% 但 Part B 結構性無法改善 (僅 2 訊號 VIX 皆 > 14)，min(A,B) **0.64** TIE baseline）。**前次：** COPX-014（Cross-Asset Divergence Regime-Gated BB Squeeze Breakout，TLT-014 / TSLA-017 cross-strategy port，**3 次嘗試全部失敗**）

**已證明無效（禁止重複嘗試）：**
- 回檔 ≥ 8% 搭配 WR-80（Part A WR 59.5% = 盈虧平衡線，Sharpe 0.00，累計 -2.99%）
- 收盤位置 ≥ 40% 反轉K線過濾（ClosePos + 收窄回檔 + 緊SL → 雙部分皆負，已實測確認無效）
- RSI(2) < 10 + 2日跌幅 ≥ 4%（產生過多低品質訊號，Part A -44%，完全不適合 COPX）
- 60日回撤 + RSI(10) + SMA(50) 乖離三重架構（COPX-002 Att1：Part A Sharpe -0.25，A/B 比 4.25:1 極度失衡）
- 2日跌幅 ≤ -3% + 回檔9-18% + 15天持倉（COPX-002 Att2：Part B Sharpe 從 0.36 崩至 0.09，確認教訓 #6）
- SL -4.0%（COPX-003 驗證：Part B WR 從 72.7% 崩至 54.5%，Sharpe 0.01）
- TP +4.0%（COPX-003 驗證：Part A 2 筆達標→到期/停損，Sharpe 0.34→0.25）
- 20日回檔 9-20%（COPX-004 Att1：Part A Sharpe 0.21 vs 0.39，9% 門檻在 20日框架下仍引入低品質訊號）
- 15天持倉搭配 20日回看（COPX-004 Att2：Part B Sharpe 0.27 vs 0.35，WR 63.6% vs 72.7%，部分交易需 15-20 天達標）
- 冷卻期 10天 vs 12天（COPX-004 Att3：結果完全相同，訊號自然間隔 > 12 天）
- BB 擠壓突破策略（COPX-005：3 次嘗試均 Part B 失敗，Sharpe -0.17/0.01，假突破率高，突破策略在 COPX 上無效）
- 配對交易 COPX/FCX 相對價值（COPX-006 Att1：比率 z-score 60日 ≤ -1.5 + 回檔 ≥ 5%，Part A Sharpe -0.06/Part B -0.50，COPX/FCX 比率有結構性漂移不可靠）
- 動量回檔 SMA(50) + RSI(5) < 30（COPX-006 Att2：Part A Sharpe -0.28/Part B 0.00，趨勢濾波無法區分健康回檔 vs 反轉）
- RSI(2) < 15 + 2日跌幅 ≤ -3% + 20日回檔 ≥ 5%（COPX-006 Att3：Part A Sharpe 0.01/Part B 0.21，訊號過多 9.4/yr 品質低）
- ATR(5)/ATR(20) > 1.1（COPX-007 Att1：Part A 0.42/Part B 0.42，min 0.42 但不如 1.05，移除 2 筆 Part B 好訊號）
- ATR(5)/ATR(20) > 1.15（COPX-007 Att2：Part A 0.46/Part B 0.42，min 0.42，Part A 更優但 Part B 同 Att1）
- RS 動量 COPX-SPY 相對強度（COPX-008 Att1/2：RS(20d)≥5% 和 RS(10d)≥4% + 回調 3-8%，Part A/B 均負 Sharpe，銅礦 ETF 相對大盤超額表現完全不具預測力）
- Donchian 通道突破（COPX-008 Att3：20日新高突破 + SMA(50)，Part A Sharpe 0.17/Part B 0.16，A/B 平衡極佳但 min 0.16 遠低於 COPX-007 的 0.45）
- RSI(14) bullish hook divergence + ATR + COPX-007 框架（COPX-009 Att1：lookback 5 / delta 3 / max_min 35，Part A Sharpe -0.50/Part B 0.00，min -0.50。hook 過濾反移除 Part A 好訊號，WR 76.2%→33.3%）
- RSI(14) bullish hook divergence + ATR + lookback 延長（COPX-009 Att2：lookback 10 / delta 3 / max_min 35，Part A 0.00/Part B 0.00 WR 100%，min 0.00。延長 lookback 略改善但仍失敗）
- RSI(14) bullish hook divergence 純 pullback+WR（COPX-009 Att3：無 ATR + lookback 10 / delta 3 / max_min 35，Part A Sharpe 0.15/Part B 0.57，min 0.15。移除 ATR 恢復部分訊號但 Part A WR 僅 64.3%，遠低於 COPX-007 的 76.2%）
- **Post-Capitulation Vol-Transition MR（COPX-010，CIBR-012 跨資產泛化測試，3 次嘗試全部失敗）**：
  - Att1（2DD cap >= -5.5%，CIBR-012 方向）：Part A 18 訊號 WR 61.1% Sharpe **0.08** cum +4.69% / Part B 10 訊號 WR 70% Sharpe 0.28 cum +10.33%，min(A,B) 0.08。**確認 COPX winners 2dRet 整體偏深於 losers**（與 CIBR 結構相反），cap 方向系統性移除贏家
  - Att2（2DD floor <= -3.0%，EEM/INDA 方向）：Part A 21 訊號 Sharpe 0.45（一筆 cooldown 偏移仍 SL）/ Part B 6 訊號 WR 66.7% Sharpe **0.21** cum +4.35%，min(A,B) 0.21。COPX 2024-2025 牛市淺 2DD 反彈訊號為 Part B 主要贏家，floor 方向系統性殺死它們
  - Att3（弱 capitulation 雙條件過濾：跳過 1DD>-3% AND CP>0.30，best of 3）：Part A 19 訊號 WR 73.7% Sharpe **0.38** cum +27.64% / Part B 10 訊號 WR 80% Sharpe **0.57**（**完全持平**）cum +19.74%，min(A,B) **0.38**。**A/B 平衡達標**（cum 差 28.6%<30%、訊號比 1.9:1<50%）但 Part A 退化由 cooldown shift 引入 2019-05-13 新 SL 抵消
  - **核心失敗**：(1) COPX winners/losers 的 2DD/1DD 分佈大幅重疊，無單一維度具區分力；(2) cooldown chain shift（lesson #19）即便精準過濾 2 個 weak-capitulation losers 仍引入新 SL；(3) **拒絕 CIBR-012 跨資產假設於 COPX**：CIBR 1.53% vol losers 集中深 2DD（cap 有效），COPX 2.25% vol winners 跨深淺 2DD 廣泛分佈（cap/floor 雙向均失效）。延伸 lesson #20b 失敗家族至「single-day momentum filter」類別於商品 ETF，平行於 TQQQ-017 槓桿指數失敗。**COPX-007 確認為 2.25% vol 商品 ETF 結構性 Sharpe 上限**
- **^VIX FLOOR Filter on BB Squeeze Breakout（COPX-015，FCX-015 Att2 cross-asset port，3 次嘗試 Att1 PARTIAL）**：
  - Att1 ★（mode=floor, vix_low=14.0，FCX-015 Att2 sweet spot 直接移植）：Part A 7/**100%** WR/Sharpe **2.81** cum +51.26% MDD -5.74%（**+290% vs baseline 0.72**，FLOOR 14 cleanly 過濾全部 3 個 Part A 失敗訊號 VIX≤14）/ Part B 2/50%/Sharpe 0.64 cum +5.35%（**完全等於 baseline** — 兩訊號 VIX 18.48 與 16.59 皆 > 14，FLOOR 不綁定）/ min(A,B) **0.64**（與 baseline TIE，Part B binding constraint）/ A/B 累計 gap 73.9%（>30% ❌）+ signal gap 71.4%（>50% ❌）— **重要部分成功**：Part A 290% Sharpe 提升驗證 FCX-015 跨資產假設；min(A,B) 結構性 TIE 因 Part B sample size 限制（COPX-011 regime BOX 後僅 2 訊號）
  - Att2（mode=floor, vix_low=17.0，targeted Part B EX 過濾）：Part A 5/100% WR/Sharpe **2.32** cum +32.12% / Part B **1**/100% std=0 cum +7.00%（過濾 2025-06-26 EX -1.54% VIX 16.59）/ min(A,B)† **2.32** by † 慣例 BUT REJECT — Part B 1 訊號統計不足，A/B signal ratio 5:1 = 80% gap >> 50% target，A/B cum gap 45.5% > 30%
  - Att3（mode=floor, vix_low=13.0，threshold robustness loosen test）：Part A 9/77.8%/Sharpe **0.69** cum +35.40%（接近 baseline 0.72，放寬至 13 將 13.40 SL + 13.54 EX -4.63% 放回）/ Part B 不變 / min **0.64** — **確認 FLOOR 14 為 sweet spot**：往下 1pt 即放行關鍵 SL/EX
  - **核心發現（lesson #24 family v6 + lesson #19 family 邊界擴展）**：
    1. **FCX-015 FLOOR 14 假說在 COPX 同樣有效於 Part A 失敗訊號過濾**——FLOOR 方向正確跨資產一致（commodity/mining single stock → ETF），Part A SL/EX 同樣集中於 low-VIX calm regime
    2. **COPX Part B sample size 結構性限制**——COPX-011 Att3 regime BOX 後 Part B 僅 2 訊號（vs FCX-015 Part B 3+ 訊號）：單一 VIX FLOOR 無法經由 Part B 改善 min(A,B)
    3. **新跨資產規則 lesson #24 v6**：^VIX FLOOR 變體於 commodity/mining BB Squeeze Breakout 框架在「Part A SL/EX 集中於 calm regime + Part B 訊號數 >= 3」雙條件下有效——FCX 個股滿足兩條件 ✓；COPX ETF 因 Part B 僅 2 訊號失敗第二條件 ✗——sample size precondition 為跨資產 FLOOR 移植的新規則
    4. **VIX 維度區分力邊界**：Part B EX (VIX 16.59) 與 Part B TP (VIX 18.48) 過於接近，純 VIX FLOOR 無法切分；signal-day 1d return 維度（EX 6.07% vs TP 1.71%）較 VIX 維度更顯著但與 Part A 2021-02-16 winner (1d 6.09%) 重疊
    5. **A/B 失衡結構性**：Part A 受惠於 2020-2021 COVID 復甦 + 商品超級週期，Part B 為 2024-2025 銅震盪期，任何 Part A 訊號品質改善皆惡化 A/B cum gap（Att1 0.72→2.81 對應 cum gap 66.4→73.9%）
- **Cross-Asset Divergence Regime-Gated BB Squeeze Breakout（COPX-014，TLT-014 / TSLA-017 cross-strategy 移植至商品/礦業 ETF，3 次嘗試全部失敗）**：
  - Att1（GLD lookback=20 threshold=-0.05，lenient 起步）：訊號集完全等於 COPX-011 Att3 baseline 無過濾效果。所有 12 訊號的 Rel_GLD ∈ [-0.18%, +14.87%] 皆 ≥ -5%，threshold 過於寬鬆。**核心發現**：BB Squeeze breakout 進場日 COPX 已突破上軌，Rel_GLD/SPY/XLB 訊號日結構天然偏多，「下限 floor」式 divergence gate 在突破策略上效果弱
  - Att2（GLD lookback=20 threshold=+0.05）：Part A 9/66.7%/Sharpe **0.36** cum +16.96% / Part B 2 訊號不變 / min **0.36** REJECT。過濾 5 訊號（1 SL + 4 wins）但 cooldown chain shift 引入 4 個替代訊號：2019-04-04 SL（同源 -6.14%）/ 2019-12-12 EX +2.28%（替換 +7% TP）/ **2023-01-10 EX -3.49%（新增 EX-）**/ 2023-12-14 EX +0.98%（替換 +3.42%）
  - Att3（XLB lookback=20 threshold=+0.005，surgical filter）：Part A 10 訊號完全等於 baseline Sharpe **0.72** cum +40.03%（cooldown shift 將 2019-04-01 SL 替換為 2019-04-04 SL 同源 -6.14%）/ Part B 2 訊號不變 / min **0.64** REJECT。XLB 為更精準 anchor（COPX 為材料板塊內子集合），threshold +0.005 surgical filter 命中唯一 outlier 2019-04-01 SL（Rel_XLB +0.0018 vs 其餘 11 訊號 +0.0094~+0.1469），但 cooldown chain shift 完全中性化
  - **核心失敗模式（lesson #20 v3，repo 首次發現邊界）**：(1) 訊號日 Rel_anchor 結構偏多：BB Squeeze breakout 進場日 COPX 已突破上軌（短期強勢），Rel_GLD/SPY/XLB 多為正值；(2) 過嚴 threshold 觸發 cooldown chain shift：cooldown_days=12 內必然激活鄰近替代訊號，COPX 多年期失敗模式（Q1 2019 base-metals false rally / mid-2023 China weakness / 2025 Q2 metal pullback）橫跨 1-2 週，鄰近訊號通常具相同失敗結構；(3) Surgical filter 受 cooldown shift 中性化
  - **新跨資產規則（lesson #20 v3）**：cross-asset divergence regime gate 適用邊界 = 「cooldown 視窗 × 訊號密度」應遠 < 1.0（密集訊號流）；TLT-014 ✓ / TSLA-017 ✓ / COPX-014 ✗（稀疏訊號流 + breakout 框架訊號日 Rel 結構偏多）。lesson #20 v3 整合：cross-asset divergence regime gate 可用於 MR 框架（capitulation 訊號日已偏弱，divergence 可正向篩選）但**不適用於 BB Squeeze breakout 框架**
- **Macro-Confirmed Vol-Adaptive Capitulation MR（COPX-013，lesson #25 IWM-015 + lesson #24 ^VIX 雙來源跨資產移植，3 次嘗試全部失敗）**：
  - Att1（SPY 10d <= 0%，loose threshold）：Part A 20/80%/**0.57**/cum +43.39% / Part B 8/75%/**0.42**/cum +11.78%，min **0.42**。Part A 改善（過濾 1 broad-up SL），Part B 因 cooldown chain shift 引入新 SL（2024-07-22 替換被過濾的 2024-07-18）+ 過濾 3 winners
  - Att2（SPY 10d <= -1.5%，IWM-015 sweet spot 直接移植）：Part A 16/75%/**0.42**/cum +24.95% / Part B 6/83.3%/**0.71**/cum +13.26%，min **0.42**。Part B 改善（zero-loss 直觀方向）+ A/B 平衡達標（cum gap 24.7%<30%，signal ratio 1.07:1<50%）但 Part A 退化（過嚴切除 6 個 -1.5%~0 中性帶 winners）
  - Att3（SPY 10d <= 0 AND VIX 3d <= +5，lesson #25 + lesson #24 雙來源組合）：Part A 15/**60%**/**0.06**/cum +2.49%（max consec losses **4**! WR 76.2%→60%）/ Part B 8/75%/0.42/cum +11.78%，min **0.06**（三次最差）。雙閘門組合理論覆蓋全部 7 SLs，但激活原本被 cooldown 壓制的 5 個新 Part A SLs（含 2 連續 SLs 模式），cooldown chain shift 結構性放大反向選擇
  - **核心失敗模式（repo 首次發現）**：cooldown chain shift collapse — 當基礎策略 cooldown ≥10 日 + 訊號密度 < 5/yr + filter 過濾比例 > 40% 時，多重 macro filter 疊加結構性放大反向選擇，winners/losers 在 SPY 10d/VIX 3d 維度無乾淨分隔加劇問題
  - **lesson #25 cross-asset REJECT**：既有 lesson #25 僅適用「broad-market 為主要驅動因子的 sub-segment ETF」（IWM small-cap ✓），不適用 commodity miners ETF（COPX winners SPY 10d 廣泛分布 -9.13%~+4.72%，無單向 macro confirmation 區分力）
  - **lesson #19 family 邊界擴展**：lesson #25 適用邊界精煉至「broad-market 為主要驅動因子的 sub-segment ETF」（IWM ✓ / XBI ✗ / COPX ✗）；多重 forward-looking macro filter 疊加為 lesson #19 family 中的「chain-shift collapse」失敗模式
- **Volatility-Acceleration-Bounded MR（COPX-012，CIBR-014/FXI-014/URA-013 跨資產移植，3 次嘗試全部失敗）**：
  - Att1（CEILING <= 1.40，CIBR-014 reference 直接移植）：Part A 20/70.0%/Sharpe **0.28** cum +21.72% / Part B 9/77.8%/Sharpe 0.50 cum +15.70%，min(A,B) 0.28。CEILING 1.40 過濾 1 個 Part A winner + 1 個 Part B winner，並觸發 cooldown chain shift（max consec losses 2→4，連續 4 個 Part A SLs：2019-05-06/2019-08-01/2020-01-28/2020-02-25）
  - Att2（CEILING <= 1.55 放鬆至最極端）：Part A 21/71.4%/Sharpe **0.32** cum +25.98% / Part B 10/80.0%/Sharpe 0.57（**完全持平 baseline**）cum +19.74%，min(A,B) 0.32。CEILING 1.55 對 Part B 非綁定，但 Part A 訊號日期改變（cooldown chain shift），新訊號為 SL
  - Att3（停用 CEILING + 5d return cap >= -8%，URA-013 cross-asset port）：Part A 14/57.1%/Sharpe **0.00** cum -0.98% / Part B 8/87.5%/Sharpe **0.92** cum +21.32%（**+62% vs baseline 0.57**），min(A,B) 0.00。5d cap -8% 過濾 7 個 Part A 訊號**幾乎全為 winners**（COPX winners 系統性伴隨深 5d 累計跌幅 -8%~-15%），但 Part B 受惠於過濾 2024-07-19 SL（5d -8.5%）
  - **核心失敗**：(1) **COPX winners 在 ATR ratio 維度反向於 CIBR/FXI**——COPX 高品質 panic flush bounces 伴隨 ATR ratio > 1.40 in-crash acceleration，與 CIBR/FXI 結構**反向**；(2) **COPX winners 在 5d return 維度反向於 URA**——COPX winners 集中深 5d capitulation (-8%~-15%)，URA winners 集中淺 5d (-3%~-8%)，cap 方向結構相反；(3) **新跨資產規則（lesson #15 v2 + #19 v8 邊界擴展）**：任何 oscillator/return-based 上限濾波器（CEILING / cap 方向）對「商品超級週期驅動的礦業 ETF」（COPX、CIBR-XME 類別）結構性失效；(4) **與 FCX-013 lesson #22 反向發現平行**（k=1.00 嚴格優於 k<1 buffered），共同確認商品/礦業類別「extreme regime entry 策略空間」與其他資產類別不同。Att3 Part B 改善 +62%（0.57→0.92）為 partial signal——5d cap 對 Part B 是甜蜜方向，但與 Part A 災難性退化不可調和

**已掃描的參數空間：**
- 均值回歸進場：回檔 8~10% + 上限 16~20% + WR(10) ≤ -80~-85 + RSI(2) < 10~15 + 2日跌幅 3~4% + ClosePos ≥ 40% + 60日回撤 15% + RSI(10) < 30 + SMA(50) 乖離 -6%
- 波動率自適應過濾：ATR(5)/ATR(20) > 1.05 / 1.1 / 1.15（1.05 為甜蜜點）
- 突破進場：BB(20,2) 擠壓 60日 20th~30th 百分位 5日內 + Close > Upper BB + Close > SMA(50)
- 配對交易：COPX/FCX 價格比率 z-score（60日窗口）
- 動量回檔：SMA(50) 趨勢 + RSI(5) 超賣 + 5日回檔
- RSI(2) 短期均值回歸：RSI(2) < 15 + 2日跌幅 ≤ -3% + 20日回檔 ≥ 5%
- RS 動量進場：COPX-SPY RS(20d) >= 5% / RS(10d) >= 4% + 5日回調 3-8% + SMA(50)
- Donchian 突破進場：20日新高突破 + SMA(50) 趨勢確認
- 回檔回看：10日、20日
- 出場參數：TP +3.5~7.0% / SL -4.0~-6.0% / 持倉 15~20 天
- 冷卻期：10~12 天
- 全域最佳：20日回檔 10-20% + WR-80 + ATR(5)/ATR(20) > 1.05 + TP +3.5% / SL -4.5% / 20天 / 冷卻12天（Sharpe 0.45/0.57，WR 76.2%/80.0%）

**尚未嘗試的方向（預期邊際效益極低）：**
- 銅價或工業金屬指數作為宏觀過濾器（但跨資產教訓 #6 建議謹慎：確認指標常不提升品質）
- ~~趨勢跟蹤（SMA 交叉/Donchian 通道）~~：COPX-008 Att3 已驗證 Donchian 20日突破，min(A,B) 0.16（遠低於均值回歸 0.45）
- ~~RS 動量（COPX vs SPY 相對強度）~~：COPX-008 Att1/2 已驗證完全無效（Part A/B 均負 Sharpe）

**關鍵資產特性：**
- COPX (Global X Copper Miners ETF) 日波動約 2.25%，GLD 比率 1.87x
- 銅礦 ETF，受銅價、中國需求、全球工業景氣驅動
- 均值回歸效果穩健，20日回看框架 + SL 收窄使 Part A/B 同時大幅提升
- A/B 訊號率比 0.84:1（COPX-007），A/B Sharpe 差距 0.12（Part B 優於 Part A，無過擬合）
- 20日回看 vs 10日回看是關鍵突破：更長回看窗口捕捉更有意義的回檔
- **ATR(5)/ATR(20) > 1.05 在 COPX 上有效**：移除慢磨下跌訊號，保留急跌恐慌。min(A,B) +28.6%（0.35→0.45）。COPX 日波動 2.25% 超出先前認定的 ATR 有效邊界（≤2.0%），但 1.05 輕度門檻仍有效（vs IWM 1.5-2% 用 1.1，XLU 0.8-1% 用 1.15），推測 ATR 有效邊界取決於門檻寬鬆程度
- **突破策略無效**：COPX 日波動 2.25% 處於突破有效範圍下邊界，ETF 分散化可能削弱個股動量
- **配對交易無效**：COPX/FCX 比率有結構性漂移，z-score 均值回歸不可靠
- **動量回檔無效**：SMA(50) 趨勢濾波無法區分正常回檔 vs 趨勢反轉
- **RSI(2) 進場品質低於 WR(10)+回檔**：RSI(2) 在 COPX 上 Sharpe 0.01 vs WR 框架 0.39
- **RS 動量在銅礦 ETF 完全無效**：COPX-SPY 相對強度（10d/20d 回看、4%/5% 門檻）不具預測力，與 FCX-006（商品生產者缺乏持續性超額表現）和 SIVR-010（RS 動量失敗）一致
- **Donchian 突破可行但劣於均值回歸**：COPX-008 Att3 Part A/B Sharpe 0.17/0.16（A/B gap 0.01 極佳平衡），但 min 0.16 vs COPX-007 的 0.45（-64%）。WR 64% 搭配不對稱 TP/SL（+3.5%/-4.5%）= 低期望值
- **RSI(14) bullish hook divergence 不適用 COPX 20日回檔框架（COPX-009 驗證）**：SIVR-015 成功於 10日回檔 7-15% + WR(10) + divergence（min 0.48），COPX-009 三次迭代（lookback 5/10，有/無 ATR）全部失敗，最佳 min 0.15。**根因**：COPX 20日回檔框架下延續性下跌持續 15-30 日，RSI(14) 在此窗口內常多次 hook up-down，5-10 日 hook lookback 捕捉的是局部雜訊。Att1 證實 hook 過濾反移除 Part A 好訊號（21→6 訊號，WR 76.2%→33.3%）。**擴展跨資產教訓 §20b 邊界**：bullish hook divergence 有效性需同時符合（a）中高波動 2-3%、（b）pullback+WR 框架、（c）**回檔回看窗口 ≤10 日** 三個條件
- COPX 均值回歸、波動率自適應、突破（BB Squeeze + Donchian）、配對交易、動量回檔、RSI(2)、RS 動量、**RSI bullish hook divergence**、**Post-Capitulation Vol-Transition MR（2DD cap / 2DD floor / weak-capitulation 雙條件）**、**Multi-Week Regime-Aware Breakout（COPX-011 ★）** 均已驗證；**COPX-011 Att3 為新全域最優**（11 次實驗、48+ 次嘗試，含均值回歸、波動率自適應、突破、regime-aware breakout、配對交易、動量回檔、RS 動量、bullish divergence、vol-transition entry 十大策略類型）
- **COPX-010 驗證 single-day/2-day momentum filter 在商品 ETF 失效**：trade-level 分析（Part A n=21）顯示 winners/losers 在 2DD/1DD/ClosePos 三維度分佈大幅重疊，無單一維度具 cross-regime 區分力
- **COPX-011 突破 COPX-007 結構性上限**（lesson #22 cross-asset port from FCX-013 + repo 首次 regime BOX 發現）：在 COPX-005 BB Squeeze 框架（baseline min 0.01）上疊加 [k_min=1.00, k_max=1.09] 雙向 regime 過濾，min(A,B) 從 0.45 提升至 0.64（+42%）。**結構性發現**：商品/礦業 ETF 與個股的 regime 機制不同——FCX 個股需單純下限（k_min=1.00），COPX ETF 需 BOX（雙向過濾過熱牛末），推測 ETF 平均化效應使過熱信號可被 SMA20/SMA60 比率捕捉（個股噪音消除）。**先前認定的 COPX-007 結構性 Sharpe 上限被推翻**——突破策略 + regime 過濾在 COPX 上實際有效，先前 COPX-005 BB Squeeze 的失敗源於缺乏 regime context 而非突破策略本身不適用
<!-- AI_CONTEXT_END -->

# COPX 實驗總覽 (COPX Experiments Overview)

## 標的特性 (Asset Characteristics)

- **COPX (Global X Copper Miners ETF)**：追蹤 Solactive Global Copper Miners Total Return Index，持有全球銅礦公司
- 日均波動約 2.25%，GLD 波動比率 1.87x，屬中等波動度
- 銅礦板塊受銅價週期、中國基建需求、全球工業景氣、能源轉型（電動車/再生能源）驅動
- 2020 年 COVID 崩盤跌至 ~$8.5，2022 年銅價回落造成多筆停損
- 數據起始：2010-04-20（ETF 成立日）

## 實驗列表 (Experiment List)

| ID       | 資料夾                    | 策略摘要                              | 狀態  |
|----------|--------------------------|--------------------------------------|-------|
| COPX-001 | `copx_001_pullback_wr`    | 回檔範圍 9-18% + Williams %R 均值回歸 | 已完成 |
| COPX-002 | `copx_002_deep_drawdown`  | 回檔範圍 10-18% + Williams %R（A/B 平衡優化）| 已完成 |
| COPX-003 | `copx_003_exit_optimized` | 20日回檔 10-20% + WR + 出場優化 | 前任最佳 |
| COPX-004 | —（未建立）               | COPX-003 微調嘗試（3 次均失敗）| ❌ 失敗 |
| COPX-005 | `copx_005_bb_squeeze_breakout` | BB 擠壓突破（3 次嘗試均 OOS 失敗）| ❌ 失敗 |
| COPX-006 | `copx_006_pairs_fcx` | 配對交易/動量回檔/RSI(2)（3 次嘗試均失敗）| ❌ 失敗 |
| COPX-007 | `copx_007_vol_adaptive` | 波動率自適應均值回歸（ATR 過濾）| ✅ 當前最佳 |
| COPX-008 | `copx_008_rs_momentum` | RS 動量回調 / Donchian 突破（3 次嘗試均劣於 COPX-007）| ❌ 失敗 |
| COPX-009 | `copx_009_rsi_divergence_mr` | RSI(14) bullish hook divergence（SIVR-015 跨資產泛化測試，3 次嘗試均失敗）| ❌ 失敗 |
| COPX-010 | `copx_010_vol_transition_mr` | Post-Capitulation Vol-Transition MR（CIBR-012 跨資產泛化測試，3 次嘗試均失敗）| ❌ 失敗 |
| COPX-011 | `copx_011_regime_breakout` | Multi-Week Regime-Aware BB Squeeze Breakout（lesson #22 + regime BOX）| ✅ 當前最佳 |
| COPX-012 | `copx_012_atr_ceiling_mr` | Volatility-Acceleration-Bounded MR（CEILING / 5d cap，3 次嘗試均失敗）| ❌ 失敗 |
| COPX-013 | `copx_013_macro_confirmed_mr` | Macro-Confirmed Vol-Adaptive Capitulation MR（lesson #25 + #24 雙來源 forward-looking macro filter，3 次嘗試均失敗）| ❌ 失敗 |
| COPX-014 | `copx_014_gld_divergence_breakout` | Cross-Asset Divergence Regime-Gated BB Squeeze Breakout（TLT-014 / TSLA-017 cross-strategy port，3 次嘗試均失敗）| ❌ 失敗 |
| COPX-015 | `copx_015_vix_bands_breakout` | ^VIX FLOOR Filter on BB Squeeze Breakout（FCX-015 Att2 cross-asset port，3 次嘗試 Att1 PARTIAL：Part A 290% Sharpe 提升但 Part B sample size 結構性限制使 min(A,B) TIE baseline）| ⚠️ 部分成功 |

---

## COPX-001: 回檔 + Williams %R 均值回歸 (Pullback + Williams %R Mean Reversion)

### 目標 (Goal)

建立 COPX 首個均值回歸實驗。參考 XBI-001 / SIVR-005 回檔 + Williams %R 架構，
按 COPX 波動度（~2.25%，GLD 比率 1.87x）縮放參數。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 10 日高點回檔 | ≥ 9% | 過濾淺回檔 |
| 2 | 回檔上限 | ≤ 18% | 過濾極端崩盤（如 2020 COVID -35.9%）|
| 3 | Williams %R(10) | ≤ -80 | 超賣確認 |
| 4 | 冷卻期 | 10 天 | 避免重複進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 (TP) | +3.5% | 均值回歸幅度 |
| 停損 (SL) | -5.0% | 非對稱寬停損（銅礦板塊需呼吸空間）|
| 最長持倉 | 15 天 | 高波動 → 更快回歸 |
| 追蹤停損 | 無 | 日波動 2.25%，禁用區域 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | 隔日開盤市價 (next_open_market) |
| 止盈委託 | 限價賣單 Day (limit_order_day) |
| 停損委託 | 停損市價 GTC (stop_market_gtc) |
| 到期出場 | 隔日開盤市價 (next_open_market) |
| 滑價 | 0.15% |
| 悲觀認定 | 是（同根 K 線 stop+target 皆觸發 → 停損優先）|

### 設計理念 (Design Rationale)

- **回檔 9-18%**：9% 下限排除淺回檔低品質訊號（8% 的 Sharpe 為 0.00），18% 上限過濾 COVID 等極端崩盤
- **WR(10) ≤ -80**：標準超賣門檻，與 SIVR-005/XBI-001 一致
- **SL -5.0%**：非對稱設計（TP/SL = 0.7:1），需 WR > 59% 才能獲利
- **無追蹤停損**：日波動 2.25% 在禁用區域，根據跨資產教訓 #2

### 迭代嘗試紀錄 (Iteration Log)

| # | 變更 | Part A Sharpe | Part B Sharpe | A/B 訊號 | A WR / B WR | 結論 |
|---|------|-------------|-------------|----------|------------|------|
| 1 | 回檔 8-18%, WR-80, TP3.5/SL5 | 0.00 | 0.21 | 37/13 | 59.5%/69.2% | Part A 恰在盈虧平衡線 |
| 2 | 回檔 9-18%, WR-80, TP3.5/SL5 (最終版) | 0.08 | 0.36 | 30/10 | 63.3%/70.0% | 雙正、Part B 遠優於 A |
| — | 回檔 8-18%, WR-85, TP3.5/SL5 | ~0.07 | ~0.12 | 34/13 | 61.8%/69.2% | 不如 9% 門檻 |
| — | 回檔 8-18%, WR-80, drop2d≤-3%, TP3.5/SL5 | ~0.38 | ~0.07 | 32/9 | 71.9%/66.7% | Part A 過擬合 |
| — | 回檔 8-18%, WR-80, RSI(2)<15, TP3.5/SL5 | ~-0.06 | ~0.04 | 33/11 | 57.6%/63.6% | RSI(2) 反效果 |
| — | 回檔 8-18%, WR-80, drop2d≤-3%, TP4/SL5 | ~0.09 | ~-0.06 | 32/9 | 59.4%/55.6% | TP+4% 過高 |
| — | 回檔 10-16%, WR-80, ClosePos≥40%, TP4/SL4.5/15d | -0.14 | -0.15 | 19/7 | 47.4%/42.9% | 反轉K線+收窄範圍+緊SL三重過濾災難 |
| — | 回檔 9-18%, WR-80, drop2d≤-3%, TP3.5/SL5/20d | 0.15 | 0.24 | 27/7 | 66.7%/71.4% | Part A 提升但 Part B 訊號減少，A/B 更平衡但平均 Sharpe 略低 |
| — | RSI(2)<10, drop2d≤-4%, TP4.5/SL5/20d | -0.25 | 0.01 | 44/13 | 40.9%/53.8% | RSI(2) 產生過多低品質訊號，Part A 災難 |

### 回測結果 (Backtest Results)

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|-------------------|-------------------|----------------|
| 訊號數 | 30 | 10 | 2 |
| 訊號/年 | 6.0 | 5.0 | 8.7 |
| 勝率 | 63.3% | 70.0% | 50.0% |
| 平均報酬 | +0.35% | +1.28% | -0.82% |
| 累計報酬 | +8.06% | +12.89% | -1.82% |
| 盈虧比 | 1.18 | 2.10 | 0.68 |
| Sharpe | 0.08 | 0.36 | -0.19 |
| Sortino | 0.11 | 0.55 | -0.23 |
| Calmar | 0.04 | 0.18 | -0.15 |
| MDD | -9.09% | -7.23% | -5.47% |
| 最大連續虧損 | 3 | 1 | 1 |

**A/B 分析**：
- 訊號率比 6.0:5.0 = 1.2:1（優秀，策略穩健）
- WR 從 63.3% 提升至 70.0%（Part B 更好，無過擬合）
- Sharpe 從 0.08 提升至 0.36（Part B 顯著更好）
- 最大連續虧損 Part A 3，Part B 僅 1（穩定）
- Part A 期間包含 2022 年銅價回落，多筆停損拉低績效
- Part B 盈虧比 2.10（7 勝 / 2 停損 / 1 到期）

**結論**：COPX 的回檔 + Williams %R 均值回歸策略有效。1% 的回檔門檻提高（8%→9%）移除 7 筆低品質 Part A 訊號，使 Sharpe 從 0.00 提升至 0.08。Part B Sharpe 0.36 顯著優於 Part A，無過擬合跡象。A/B 訊號比 1.2:1 表明策略對市場狀態變化穩健。

---

## COPX-002: 回檔 10-18% + Williams %R 均值回歸（A/B 平衡優化）

### 目標 (Goal)

基於 COPX-001 架構，收緊回檔下限（9%→10%）以移除低品質淺回檔訊號，
改善 Part A 績效與 A/B 平衡。共經歷 3 次嘗試。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 10 日高點回檔 | ≥ 10% | 過濾淺回檔（比 COPX-001 的 9% 更嚴格）|
| 2 | 回檔上限 | ≤ 18% | 過濾極端崩盤 |
| 3 | Williams %R(10) | ≤ -80 | 超賣確認 |
| 4 | 冷卻期 | 10 天 | 避免重複進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 (TP) | +3.5% | 與 COPX-001 相同 |
| 停損 (SL) | -5.0% | 與 COPX-001 相同 |
| 最長持倉 | 15 天 | 與 COPX-001 相同 |
| 追蹤停損 | 無 | 日波動 2.25%，禁用區域 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | 隔日開盤市價 (next_open_market) |
| 止盈委託 | 限價賣單 Day (limit_order_day) |
| 停損委託 | 停損市價 GTC (stop_market_gtc) |
| 到期出場 | 隔日開盤市價 (next_open_market) |
| 滑價 | 0.15% |
| 悲觀認定 | 是 |

### 迭代嘗試紀錄 (Iteration Log)

| # | 變更 | Part A Sharpe | Part B Sharpe | A/B 訊號 | A WR / B WR | 結論 |
|---|------|-------------|-------------|----------|------------|------|
| Att1 | 60日回撤≥15% + RSI(10)<30 + SMA(50)偏離<-6%, TP3.5/SL5/20d | -0.25 | 0.36 | 17/4 | 47.1%/75.0% | 60日回撤捕捉太多持續下跌訊號，Part A 災難，A/B 4.25:1 極度失衡 |
| Att2 | 回檔9-18% + WR-80 + drop2d≤-3%, TP3.5/SL5/15d | 0.15 | 0.09 | 27/7 | 66.7%/57.1% | 2日跌幅過濾使 Part B Sharpe 從 0.36 崩至 0.09（教訓 #6 再確認） |
| Att3 | 回檔10-18% + WR-80, TP3.5/SL5/15d (最終版) | 0.21 | 0.14 | 26/10 | 69.2%/60.0% | A/B 平衡最佳（Sharpe 差距 0.07 vs COPX-001 的 0.28）|

### 回測結果 (Backtest Results)

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|-------------------|-------------------|----------------|
| 訊號數 | 26 | 10 | 2 |
| 訊號/年 | 5.2 | 5.0 | 8.4 |
| 勝率 | 69.2% | 60.0% | 50.0% |
| 平均報酬 | +0.84% | +0.55% | -0.82% |
| 累計報酬 | +21.78% | +4.84% | -1.82% |
| 盈虧比 | 1.53 | 1.35 | 0.68 |
| Sharpe | 0.21 | 0.14 | -0.19 |
| Sortino | 0.30 | 0.20 | -0.23 |
| Calmar | 0.09 | 0.08 | -0.15 |
| MDD | -9.09% | -7.23% | -5.47% |
| 最大連續虧損 | 3 | 3 | 1 |

**A/B 分析**：
- 訊號率比 5.2:5.0 = 1.04:1（極優秀，幾乎完美平衡）
- Sharpe 差距僅 0.07（vs COPX-001 的 0.28）
- Part A 大幅改善：Sharpe 0.08→0.21（+163%），累計 +8.06%→+21.78%（+170%）
- Part B 下降：Sharpe 0.36→0.14（-61%），WR 70%→60%
- 回檔 9-10% 區間在 Part B 包含好訊號，收緊門檻在此犧牲 Part B 品質

**vs COPX-001 比較**：
- COPX-001 整體 Part B 更優（Sharpe 0.36 vs 0.14），適合信任 OOS 績效的場景
- COPX-002 A/B 平衡更佳（gap 0.07 vs 0.28），Part A 更可靠
- 平均 Sharpe：COPX-001 (0.08+0.36)/2=0.22，COPX-002 (0.21+0.14)/2=0.175

---

## COPX-003: 20日回檔 + Williams %R + 出場優化（全域最佳）

### 目標 (Goal)

基於 COPX-002 架構，改用 20 日回看窗口（vs 10 日），擴大回檔上限至 20%，
收窄 SL 至 -4.5%（vs -5.0%），延長持倉至 20 天，冷卻期 12 天。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 20 日高點回檔 | ≥ 10% | 過濾淺回檔（20日回看 vs COPX-001/002 的 10日）|
| 2 | 回檔上限 | ≤ 20% | 過濾極端崩盤（vs COPX-001/002 的 18%）|
| 3 | Williams %R(10) | ≤ -80 | 超賣確認 |
| 4 | 冷卻期 | 12 天 | 避免重複進場（vs COPX-001/002 的 10天）|

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 (TP) | +3.5% | 同 COPX-001/002 |
| 停損 (SL) | -4.5% | 收窄 0.5%（vs COPX-001/002 的 -5.0%，WR 不變，每筆虧損降低）|
| 最長持倉 | 20 天 | 延長 5 天（vs COPX-001/002 的 15 天）|
| 追蹤停損 | 無 | 日波動 2.25%，禁用區域 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | 隔日開盤市價 (next_open_market) |
| 止盈委託 | 限價賣單 Day (limit_order_day) |
| 停損委託 | 停損市價 GTC (stop_market_gtc) |
| 到期出場 | 隔日開盤市價 (next_open_market) |
| 滑價 | 0.15% |
| 悲觀認定 | 是 |

### 設計理念 (Design Rationale)

- **20日回看 vs 10日**：更長回看窗口捕捉更有意義的回檔，避免短期小幅震盪的假訊號
- **回檔上限 20% vs 18%**：配合 20日窗口，允許更大回檔範圍
- **SL -4.5% vs -5.0%**：純粹改善——WR 不變（74.2%/72.7%），每筆虧損降低 0.5%
- **SL -4.0% 太緊**：Part B WR 從 72.7% 崩至 54.5%，-4.5% 是甜蜜點
- **TP +4.0% 測試失敗**：Part A 2 筆達標交易無法觸及 +4.0%，Sharpe 0.34→0.25
- **20天持倉 vs 15天**：平均持倉僅 3.6/5.0 天，但少數交易需 15-20 天達標

### 回測結果 (Backtest Results)

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|-------------------|-------------------|----------------|
| 訊號數 | 31 | 11 | 2 |
| 訊號/年 | 6.2 | 5.5 | 8.4 |
| 勝率 | 74.2% | 72.7% | 50.0% |
| 平均報酬 | +1.40% | +1.28% | -0.57% |
| 累計報酬 | +50.85% | +14.19% | -1.30% |
| 盈虧比 | 2.17 | 2.01 | 0.75 |
| Sharpe | 0.39 | 0.35 | -0.14 |
| Sortino | 0.59 | 0.53 | -0.17 |
| Calmar | 0.16 | 0.18 | -0.10 |
| MDD | -8.91% | -7.23% | -5.47% |
| 最大連續虧損 | 3 | 2 | 1 |

**A/B 分析**：
- 訊號率比 6.2:5.5 = 1.13:1（極優秀，完美平衡）
- A/B Sharpe 差距僅 0.04（vs COPX-001 的 0.28，COPX-002 的 0.07）
- WR 74.2%/72.7%（A/B 幾乎一致）
- 累計 +50.85%/+14.19%（年化 10.17%/7.10%）
- vs COPX-001：Part A Sharpe 0.39 vs 0.08（+388%），Part B 0.35 vs 0.36（持平）
- vs COPX-002：Part A 0.39 vs 0.21（+86%），Part B 0.35 vs 0.14（+150%）

**結論**：COPX-003 在 Part A 和 Part B 上均大幅超越 COPX-001/002。20日回看框架 + SL 收窄是關鍵突破。已確認為全域最優。

---

## COPX-004: COPX-003 微調嘗試（3 次均失敗）

### 目標 (Goal)

基於 COPX-003 框架嘗試微調以進一步提升風險調整後報酬。共 3 次嘗試均無法超越 COPX-003。

### 迭代嘗試紀錄 (Iteration Log)

| # | 變更 | Part A Sharpe | Part B Sharpe | A/B 訊號 | A WR / B WR | 結論 |
|---|------|-------------|-------------|----------|------------|------|
| COPX-003 基線 | 20日回檔 10-20%, WR-80, TP3.5/SL4.5/20d/cd12 | 0.39 | 0.35 | 31/11 | 74.2%/72.7% | — |
| Att1 | 回檔 9-20%（放寬下限） | 0.21 | 0.47 | 33/13 | 66.7%/76.9% | 9% 在 20日框架仍引入低品質 Part A 訊號（+2 訊號 Part A 多為停損），A/B gap 0.26 |
| Att2 | 持倉 15天（縮短） | 0.39 | 0.27 | 31/11 | 74.2%/63.6% | Part B WR 降 9pp，少數慢速反彈需 15-20 天達標被截斷 |
| Att3 | 冷卻 10天（縮短） | 0.39 | 0.35 | 31/11 | 74.2%/72.7% | 結果完全相同，訊號自然間隔 > 12 天 |

**結論**：COPX-003 的參數組合（20日回看、10-20% 回檔、SL -4.5%、20天持倉、12天冷卻）已在各維度達到最優，微調任何參數均無法改善。已確認為全域最優。

---

## 演進路線圖 (Roadmap)

```
COPX-001 (10日回檔 9-18% + WR(10) ≤ -80, SL -5.0%) ← 前 Part B 最佳 (Sharpe 0.36)
  ├── ✗ 收盤位置 ≥ 40% 反轉K線過濾（已實測：雙部分皆負）
  ├── ✗ 急跌確認 drop2d ≤ -3%（已實測：Part A 提升但 Part B 下降）
  ├── ✗ RSI(2) < 10 全新架構（已實測：產生過多低品質訊號）
  └── COPX-002 (10日回檔 10-18% + WR(10) ≤ -80, SL -5.0%) ← 前 A/B 平衡最佳 (gap 0.07)
      ├── ✗ 60日回撤架構 Att1（Part A Sharpe -0.25，A/B 4.25:1）
      ├── ✗ 2日跌幅 + 15天持倉 Att2（Part B Sharpe 0.09，教訓 #6）
      └── COPX-003 (20日回檔 10-20% + WR-80, SL -4.5%, 20d) ✅ 全域最佳 (Sharpe 0.39/0.35)
          ├── ✗ 回檔 9-20% Att1（Part A 劣化，A/B gap 擴大）
          ├── ✗ 15天持倉 Att2（Part B WR 降 9pp）
          └── ✗ 冷卻 10天 Att3（無效果，訊號自然間隔 > 12天）
```

---

## COPX-001 滾動窗口績效分析

> **分析日期：** 2026-03-30
> **窗口：** 2 年，步進 6 個月（共 12 個窗口）

### 滾動窗口績效表

| 窗口 | 訊號 | 勝率 | 平均報酬 | 累計報酬 | MDD | ΔWR |
|------|------|------|----------|----------|-----|-----|
| 2019-01~2020-12 | 7 | 57.1% | -0.20% | -2.05% | -8.91% | — |
| 2019-07~2021-06 | 10 | 60.0% | +0.04% | -0.47% | -8.91% | +2.9pp |
| 2020-01~2021-12 | 13 | 69.2% | +0.87% | +10.83% | -8.91% | +9.2pp |
| 2020-07~2022-06 | 16 | 62.5% | +0.60% | +8.65% | -7.08% | -6.7pp |
| 2021-01~2022-12 | 18 | 61.1% | +0.16% | +1.34% | -9.09% | -1.4pp |
| 2021-07~2023-06 | 16 | 62.5% | +0.29% | +3.22% | -9.09% | +1.4pp |
| 2022-01~2023-12 | 14 | 64.3% | +0.41% | +4.68% | -9.09% | +1.8pp |
| 2022-07~2024-06 | 9 | 66.7% | +0.62% | +4.93% | -8.14% | +2.4pp |
| 2023-01~2024-12 | 11 | 72.7% | +1.31% | +14.62% | -6.33% | +6.1pp |
| 2023-07~2025-06 | 10 | 70.0% | +1.28% | +12.89% | -7.23% | -2.7pp |
| 2024-01~2025-12 | 10 | 70.0% | +1.28% | +12.89% | -7.23% | +0.0pp |
| 2024-07~2026-03 | 11 | 63.6% | +0.70% | +7.09% | -7.23% | -6.4pp |

### 預測精準度表

| 窗口 | WR | 平均贏利 | 平均虧損 | 盈虧比 | 差點成功 |
|------|------|----------|----------|--------|----------|
| 2019-01~2020-12 | 57.1% | +3.50% | -5.14% | 0.91 | — |
| 2019-07~2021-06 | 60.0% | +3.50% | -5.14% | 1.02 | — |
| 2020-01~2021-12 | 69.2% | +3.50% | -5.04% | 1.56 | 0/1 |
| 2020-07~2022-06 | 62.5% | +3.50% | -4.24% | 1.38 | 0/2 |
| 2021-01~2022-12 | 61.1% | +3.50% | -5.08% | 1.08 | 0/1 |
| 2021-07~2023-06 | 62.5% | +3.50% | -5.07% | 1.15 | 0/1 |
| 2022-01~2023-12 | 64.3% | +3.50% | -5.14% | 1.23 | — |
| 2022-07~2024-06 | 66.7% | +3.50% | -5.14% | 1.36 | — |
| 2023-01~2024-12 | 72.7% | +3.50% | -4.52% | 2.07 | 0/1 |
| 2023-07~2025-06 | 70.0% | +3.50% | -3.89% | 2.10 | 0/1 |
| 2024-01~2025-12 | 70.0% | +3.50% | -3.89% | 2.10 | 0/1 |
| 2024-07~2026-03 | 63.6% | +3.50% | -4.20% | 1.46 | 0/1 |

### 漸變性評估

- **勝率範圍**：57.1% ~ 72.7%（ΔWR 標準差 4.6pp，最大跳動 9.2pp）
- **盈虧比範圍**：0.91 ~ 2.10（ΔPF 標準差 0.35）
- **累計報酬範圍**：-2.05% ~ +14.62%（ΔCum 標準差 5.37%）
- **平均贏利範圍**：+3.50% ~ +3.50%（Δ標準差 0.00%，完全穩定）
- **平均虧損範圍**：-3.89% ~ -5.14%（虧損幅度隨市場波動略有變化）

**判定：**
- ✓ 預測精準度漸變（勝率最大跳動 9.2pp ≤ 20pp 閾值）
- ✓ 下游績效漸變（累計報酬最大跳動 11.30% ≤ 3σ = 16.11%）

### 分析解讀

1. **早期窗口偏弱**：2019-01~2020-12 窗口累計 -2.05%，唯一負報酬窗口，受 2020 疫情影響銅價大幅震盪
2. **中期穩定**：2021-2023 窗口勝率穩定在 61-66%，表現平穩但累計報酬偏低（+1.3%~+4.9%）
3. **近期表現強勁**：2023 後窗口勝率攀升至 70-73%，累計報酬達 +12.9%~+14.6%
4. **平均贏利完全固定**：+3.50% TP 在所有窗口一致觸發，策略進場精準度高
5. **漸變性優異**：ΔWR 最大僅 9.2pp，遠低於 20pp 閾值，勝率變化極為平滑
6. **10/12 正報酬窗口**：僅最早兩個窗口為負或接近零，整體穩健

---

## COPX-005: BB 擠壓突破 (BB Squeeze Breakout) ❌ 失敗

### 目標 (Goal)

首次在 COPX 上嘗試突破策略。基於 TSLA-005/NVDA-003/FCX-004 的 BB 擠壓突破成功經驗
（日波動 2-4%），移植至 COPX（日波動 ~2.25%）。測試突破策略能否超越均值回歸（COPX-003 Sharpe 0.39/0.35）。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | BB Width 百分位 | 60日 20th 百分位，5日內 | 近期波動收縮（擠壓）|
| 2 | Close > Upper BB(20,2) | — | 突破上軌 |
| 3 | Close > SMA(50) | — | 趨勢向上 |
| 4 | 冷卻期 | 12 天 | 避免重複進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 (TP) | +7% | 突破幅度（按 FCX +8% 波動縮放）|
| 停損 (SL) | -6% | 突破失敗停損 |
| 最長持倉 | 20 天 | |
| 追蹤停損 | 無 | |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | 隔日開盤市價 (next_open_market) |
| 止盈委託 | 限價賣單 Day (limit_order_day) |
| 停損委託 | 停損市價 GTC (stop_market_gtc) |
| 到期出場 | 隔日開盤市價 (next_open_market) |
| 滑價 | 0.15% |
| 悲觀認定 | 是 |

### 迭代嘗試紀錄 (Iteration Log)

| # | 變更 | Part A Sharpe | Part B Sharpe | A/B 訊號 | A WR / B WR | 結論 |
|---|------|-------------|-------------|----------|------------|------|
| 1 | TP+6%/SL-5%/30th pct | 0.29 | -0.17 | 20/6 | 60.0%/33.3% | Part B 3/6 停損，SL -5% 太緊 |
| 2 | TP+7%/SL-6%/30th pct | 0.30 | -0.17 | 20/6 | 65.0%/33.3% | 寬 SL 無助，同 3 筆 Part B 仍停損 |
| 3 | TP+7%/SL-6%/20th pct（最終版）| 0.33 | 0.01 | 18/5 | 66.7%/40.0% | 收緊擠壓濾掉 1 筆假突破，但仍遠不及 COPX-003 |

### 回測結果 (Backtest Results) — Att3（最終版）

| 指標 | Part A (2019-2023) | Part B (2024-2025) |
|------|-------------------|-------------------|
| 訊號數 | 18 | 5 |
| 訊號/年 | 3.6 | 2.5 |
| 勝率 | 66.7% | 40.0% |
| 平均報酬 | +1.92% | +0.04% |
| 累計報酬 | +36.65% | -0.69% |
| 盈虧比 | 1.98 | 1.01 |
| Sharpe | 0.33 | 0.01 |
| Sortino | 0.56 | 0.01 |
| MDD | -8.92% | -9.72% |
| 最大連續虧損 | 2 | 2 |

### 失敗分析

1. **Part B 假突破率高**：2024-2025 年 COPX 處於盤整/回落期（$36-$48 區間），BB 突破後缺乏持續動能
2. **Part B 失敗交易分析**：
   - 2024-05-15（$48.32 進場）：接近歷史高點突破，隨即回落 → -6.14%
   - 2024-07-08（$45.89 進場）：高位再次假突破 → -6.14%
   - 2025-02-10（$40.63 進場）：反彈突破但動能不足 → -6.14%
3. **ETF 分散化效應**：COPX 持有多家銅礦公司，個別股票的動量在 ETF 層面被稀釋，削弱突破持續性
4. **日波動 2.25% 處於突破有效邊界**：成功案例均為 >2.5%（FCX 2-4%、TSLA 3-4%、NVDA 3.26%）

### 結論

BB 擠壓突破策略在 COPX 上完全失敗。COPX-003 均值回歸（Sharpe 0.39/0.35）仍為全域最優。
新增跨資產教訓：BB 擠壓突破在 ETF（vs 個股）上可能因分散化而失效，有效下限可能為日波動 ~2.5% 而非 2.0%。

---

## COPX-006: 多策略探索（配對交易 / 動量回檔 / RSI(2) 均值回歸）

### 目標 (Goal)

嘗試三種不同策略類型，驗證 COPX-003 是否為全域最優。

### Attempt 1: 配對交易（COPX/FCX 相對價值）

**假說**：COPX 與 FCX 高度相關（ETF vs 最大成分股）。當 COPX 相對 FCX 異常便宜（價格比率 z-score 偏低），COPX 傾向回歸均值。

**進場條件**：COPX/FCX 價格比率 z-score（60日）≤ -1.5 + COPX 10日回檔 ≥ 5% + 冷卻12天
**出場**：TP +3.5% / SL -4.5% / 20天 / 滑價 0.15%

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 13 (2.6/yr) | 3 (1.5/yr) |
| 勝率 | 53.8% | 33.3% |
| 累計報酬 | -4.33% | -5.88% |
| Sharpe | -0.06 | -0.50 |
| MDD | -5.87% | -5.34% |

**失敗原因**：COPX/FCX 比率有結構性漂移——FCX 在銅牛市中因純銅礦暴露而跑贏分散化 ETF（2021年3筆連續停損均為此原因）。z-score 均值回歸假設不成立。Part B 僅 3 筆訊號，不具統計意義。

### Attempt 2: 動量回檔（SMA(50) + RSI(5) + 回檔）

**假說**：在確認上升趨勢（Close > SMA50）中買入短期超賣回檔（RSI(5) < 30 + 5日回檔 ≥ 3%）。

**進場條件**：Close > SMA(50) + RSI(5) < 30 + 5日回檔 ≥ 3% + 冷卻12天
**出場**：TP +4.0% / SL -4.5% / 20天 / 滑價 0.15%

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 15 (3.0/yr) | 3 (1.5/yr) |
| 勝率 | 40.0% | 100.0% |
| 累計報酬 | -17.49% | +12.49% |
| Sharpe | -0.28 | 0.00 |
| MDD | -9.82% | -2.14% |

**失敗原因**：SMA(50) 趨勢濾波無法區分健康回檔 vs 趨勢反轉。Part A 有 9 筆停損（WR 40%），特別是 2019-2020 年多次在趨勢頂部觸發訊號。Part B 100% WR 但僅 3 筆（Sharpe 0.00 因標準差為 0），A/B 嚴重失衡。

### Attempt 3: RSI(2) 短期均值回歸（模仿 URA-004）

**假說**：以 RSI(2) + 2日急跌 + 20日回檔作為進場條件，與 COPX-003（WR+回檔）不同的進場機制。

**進場條件**：RSI(2) < 15 + 2日跌幅 ≤ -3% + 20日回檔 ≥ 5% + 冷卻12天
**出場**：TP +3.5% / SL -4.5% / 20天 / 滑價 0.15%

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 47 (9.4/yr) | 15 (7.5/yr) |
| 勝率 | 57.4% | 66.7% |
| 累計報酬 | -2.12% | +11.23% |
| Sharpe | 0.01 | 0.21 |
| MDD | -16.24% | -8.26% |
| 最大連續虧損 | 3 | 2 |

**失敗原因**：RSI(2) < 15 + 2日跌幅 ≤ -3% + 20日回檔 ≥ 5% 產生遠多於 COPX-003 的訊號（9.4/yr vs 6.2/yr），但品質明顯更低（Part A WR 57.4% vs 74.2%，Sharpe 0.01 vs 0.39）。A/B 訊號比 3.13:1（vs COPX-003 的 1.13:1）。RSI(2) 在 COPX 上無法替代 WR(10) + 20日回檔 10-20% 的精確過濾效果。

### 結論

三種策略類型（配對交易、動量回檔、RSI(2) 均值回歸）均未能超越 COPX-003。
- 配對交易因 COPX/FCX 比率結構性漂移而失敗
- 動量回檔因趨勢濾波無法區分回檔 vs 反轉而失敗
- RSI(2) 均值回歸因訊號品質不如 WR(10)+回檔而失敗

COPX-003（Sharpe 0.39/0.35）確認為前任最優，COPX-007 以 ATR 過濾再次突破。

---

## COPX-007: 波動率自適應均值回歸 (Volatility-Adaptive Mean Reversion)

### 目標 (Goal)

在 COPX-003 的 20日回檔 + WR(10) 進場架構上，加入 ATR(5)/ATR(20) 波動率飆升過濾器，移除慢磨下跌的低品質訊號，保留急跌恐慌的高品質訊號。跨資產驗證顯示此方法在 XLU-011 (+272%) 和 IWM-011 (+67.7%) 上成功。

### 策略

- **進場條件**（全部滿足）：
  1. 收盤價相對 20 日最高價回檔 10-20%
  2. Williams %R(10) ≤ -80（超賣確認）
  3. ATR(5)/ATR(20) > 閾值（波動率飆升過濾）
  4. 冷卻期 12 個交易日

- **出場條件**（同 COPX-003）：TP +3.5% / SL -4.5% / 20 天
- **滑價**：0.15%
- **成交模型**：隔日開盤市價進場，限價/停損出場，悲觀認定

### 開發記錄

#### Attempt 1: ATR(5)/ATR(20) > 1.1

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 20 (4.0/yr) | 8 (4.0/yr) |
| 勝率 | 75.0% | 75.0% |
| 累計報酬 | +32.11% | +11.78% |
| Sharpe | 0.42 | 0.42 |
| MDD | -6.97% | -7.23% |

vs COPX-003: Part A Sharpe +7.7%（0.39→0.42），Part B +20%（0.35→0.42），min(A,B) 0.42 (+20%)。ATR > 1.1 移除 Part A 11 個和 Part B 3 個訊號。A/B 完美平衡（gap 0.00）。

#### Attempt 2: ATR(5)/ATR(20) > 1.15

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 17 (3.4/yr) | 8 (4.0/yr) |
| 勝率 | 76.5% | 75.0% |
| 累計報酬 | +29.33% | +11.78% |
| Sharpe | 0.46 | 0.42 |

vs Att1: Part A Sharpe +9.5%（0.42→0.46），Part B 不變（同樣 8 訊號）。ATR > 1.15 只影響 Part A（再移除 3 訊號），min(A,B) 仍為 0.42。

#### Attempt 3: ATR(5)/ATR(20) > 1.05 ★ 最佳

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 21 (4.2/yr) | 10 (5.0/yr) |
| 勝率 | 76.2% | 80.0% |
| 累計報酬 | +36.73% | +19.74% |
| Sharpe | **0.45** | **0.57** |
| PF | 2.41 | 3.02 |
| MDD | -6.97% | -7.23% |
| Sortino | 0.69 | 0.90 |

vs COPX-003: **min(A,B) 0.45 (+28.6%)**。ATR > 1.05 捕捉 2 筆 Att1 遺漏的 Part B 好訊號（2024-06-04 +3.50%、2025-03-03 +3.50%），Part B WR 從 75%→80%，Sharpe 從 0.42→0.57。

### 關鍵發現

1. **ATR 有效邊界可延伸至日波動 2.25%**：先前認定 ATR 過濾有效邊界為日波動 ≤ 2.0%（IWM 1.5-2.0% 有效，SIVR 2-3% 失敗）。COPX 在 2.25% 以低門檻（1.05）仍有效，推測有效邊界取決於波動度×門檻的互動——低波動資產可用嚴格門檻（XLU 1.15），高波動資產需用寬鬆門檻（COPX 1.05）。
2. **ATR 門檻與 Part B 訊號捕捉的非線性關係**：1.05→1.10 的 0.05 差距導致 Part B 丟失 2 筆好訊號（WR 80%→75%，Sharpe 0.57→0.42），但 1.10→1.15 只影響 Part A（Part B 完全相同）。
3. **波動率自適應 + 均值回歸 = 互補架構**：ATR 過濾移除的是「市場緩慢下行」的訊號，保留「突然恐慌拋售」的訊號。後者正是均值回歸最有效的場景。

### 結論

COPX-007 Att3（ATR > 1.05）為 COPX 新的全域最優：
- Part A Sharpe 0.45（+15.4% vs COPX-003 的 0.39）
- Part B Sharpe 0.57（+62.9% vs COPX-003 的 0.35）
- min(A,B) 0.45（+28.6% vs 0.35）
- A/B 訊號率 4.2:5.0/yr（0.84:1，優秀平衡）
- 累計報酬差距 17.0 pp（< 30% 門檻）

COPX 至此已完成 7 次實驗、33+ 次嘗試，涵蓋均值回歸、波動率自適應、突破、配對交易、動量回檔五大策略類型。

---

## COPX-008: RS 動量回調 / Donchian 突破 (RS Momentum / Donchian Breakout)

### 目標 (Goal)

探索 COPX 尚未嘗試的兩個策略方向：
1. **RS 動量**：參考 SOXL-010/TSM-008 成功框架，用 COPX 相對 SPY 的超額表現作為動量訊號
2. **Donchian 突破**：純趨勢跟蹤策略，買入突破 N 日新高的 COPX

### 三次嘗試 (Three Attempts)

#### Attempt 1: RS(20d) 動量回調

**進場**：COPX-SPY 20日報酬差 >= 5% + COPX 5日回調 3-8% + Close > SMA(50) + 冷卻10天
**出場**：TP +5.0% / SL -5.0% / 20天

| 指標 | Part A | Part B |
|------|--------|--------|
| Sharpe | **-0.07** | **-0.05** |
| WR | 46.2% | 45.5% |
| 累計 | -12.01% | -3.96% |
| 訊號/年 | 5.2 | 5.5 |

**失敗分析**：TP +5.0% 過寬（COPX 甜蜜點 +3.5%），且 RS 動量訊號無預測力——WR ~46% 搭配對稱 TP/SL 產生負期望值。

#### Attempt 2: RS(10d) 動量回調（COPX 出場參數）

**進場**：COPX-SPY 10日報酬差 >= 4% + COPX 5日回調 3-8% + Close > SMA(50) + 冷卻10天
**出場**：TP +3.5% / SL -4.5% / 20天（COPX 已驗證出場參數）

| 指標 | Part A | Part B |
|------|--------|--------|
| Sharpe | **-0.09** | **-0.19** |
| WR | 52.6% | 44.4% |
| 累計 | -8.02% | -7.03% |
| 訊號/年 | 3.8 | 4.5 |

**失敗分析**：即使使用較短 RS 回看（10d vs 20d）和 COPX 已驗證出場，RS 動量訊號仍完全無效。Part B 更差（-0.19 vs -0.05），確認 RS 方向根本不適合銅礦 ETF。與 FCX-006（商品生產者缺乏持續性超額表現驅動力）和 SIVR-010（RS 動量在商品 ETF 失敗）一致。

#### Attempt 3: Donchian 20日突破 ★

**策略完全改變**：放棄 RS 動量方向，改用 Donchian 通道突破（趨勢跟蹤）。

**進場**：Close > 20日最高價 + Close > SMA(50) + 冷卻12天
**出場**：TP +3.5% / SL -4.5% / 20天

| 指標 | Part A | Part B |
|------|--------|--------|
| Sharpe | **0.17** | **0.16** |
| WR | 63.9% | 64.7% |
| 累計 | +22.76% | +9.78% |
| 訊號/年 | 7.2 | 8.5 |
| MDD | -6.81% | -9.57% |
| PF | 1.41 | 1.38 |

**分析**：首次正 Sharpe！A/B 平衡極佳（gap 0.01），WR ~64% 穩定。但 min(A,B) = 0.16 遠低於 COPX-007 的 0.45（-64%）。原因：WR 64% 搭配不對稱 TP/SL（+3.5% vs -4.64%）= 低盈虧比（1.41），每筆虧損金額 > 每筆獲利金額。

### 結論

1. **RS 動量在銅礦 ETF 完全無效**：銅礦 ETF 的超額表現不具有動量延續性，與半導體板塊（SOXL/TSM）的成功形成鮮明對比。原因推測：銅價驅動的回報具有均值回歸特性而非動量特性
2. **Donchian 突破可行但劣於均值回歸**：Donchian 提供正 Sharpe 且 A/B 極佳平衡，但盈虧比不足以與均值回歸競爭
3. COPX-007 仍為全域最優。COPX 至此已完成 8 次實驗、39+ 次嘗試，涵蓋均值回歸、波動率自適應、突破（BB Squeeze + Donchian）、配對交易、動量回檔、RS 動量七大策略類型

---

## COPX-009: RSI(14) Bullish Hook Divergence（SIVR-015 跨資產泛化測試）

### 目標 (Goal)

驗證 SIVR-015 發現的 RSI(14) bullish hook divergence 過濾器（跨資產教訓 §20b）
在 COPX 上的可移植性。COPX 日波動 2.25%，同屬「中高波動 + 已驗證 pullback+WR 框架」
類別，是 SIVR-015 在文獻中明確提及的候選資產（「FCX、COPX、USO、TSLA」）。

**改進假設**：COPX-007 Part A 21 訊號 vs Part B 10 訊號，A/B 訊號頻率差 110%，
累計報酬差 86%（36.73% vs 19.74%）。推測 Part A 過多訊號中部分為「RSI 仍在下探」
的延續下跌訊號。Bullish hook 過濾器可選擇性移除這些低品質訊號，改善 A/B 平衡。

### 實驗結果總覽

| Attempt | 設定 | Part A Sharpe | Part B Sharpe | min(A,B) | vs COPX-007 |
|---------|------|---------------|---------------|----------|-------------|
| Att1 | ATR>1.05 + hook lookback 5 / delta 3 / RSI_min≤35 | -0.50 | 0.00 | **-0.50** | -1.11x |
| Att2 | ATR>1.05 + hook lookback 10 / delta 3 / RSI_min≤35 | 0.00 | 0.00 | 0.00 | -1.00x |
| Att3 ★ | **無 ATR** + hook lookback 10 / delta 3 / RSI_min≤35 | 0.15 | 0.57 | 0.15 | -0.67x |

三次迭代全部未勝過 COPX-007 的 min(A,B) = 0.45。

### 逐次嘗試詳細分析

#### Attempt 1: 完整沿用 SIVR-015 參數（ATR + hook）

**進場**：20日回檔 10-20% + WR(10) ≤ -80 + ATR(5)/ATR(20) > 1.05
      + RSI(14) 自過去 5 日最低點回升 ≥ 3 點（最低點 ≤ 35）+ 冷卻 12天
**出場**：TP +3.5% / SL -4.5% / 20天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 6 | 3 |
| WR | 33.3% | 100.0% |
| 累計 | -11.42% | +10.87% |
| Sharpe | **-0.50** | 0.00 (零方差) |

**失敗分析**：Hook 過濾器反而移除了 Part A 的好訊號。COPX-007 原本 21 個訊號
WR 76.2%，疊加 hook 後降至 6 個訊號 WR 33.3%——代表 hook 過濾系統性保留了
**壞訊號**。根因推測：COPX 20日回檔框架下的訊號常發生在延續性下跌中（持續 15-30 日），
RSI(14) 在此期間可能多次 hook up-down；5 日 hook 窗口捕捉的是局部 RSI 雜訊，
而非真正的 capitulation 末端動能轉折。

#### Attempt 2: 延長 hook lookback 至 10 日

**進場**：同 Att1 但 hook lookback 從 5 日改為 10 日（對齊 20 日回檔框架）
**出場**：TP +3.5% / SL -4.5% / 20天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 7 | 4 |
| WR | 57.1% | 100.0% |
| 累計 | -0.49% | +14.75% |
| Sharpe | 0.00 | 0.00 (零方差) |

**分析**：延長 lookback 略改善 Part A（6→7 訊號、WR 33.3%→57.1%），但 Sharpe 仍為 0，
累計報酬 -0.49%。確認延長 lookback 不足以挽救 hook 過濾的核心失敗模式。

#### Attempt 3: 無 ATR 過濾（純 pullback+WR+hook）★ 最終版

**進場**：20日回檔 10-20% + WR(10) ≤ -80 + RSI(14) 自過去 10 日最低點回升 ≥ 3 點
      （最低點 ≤ 35）+ 冷卻 12天
**出場**：TP +3.5% / SL -4.5% / 20天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 14 | 5 |
| WR | 64.3% | 80.0% |
| 累計 | +7.47% | +9.43% |
| Sharpe | **0.15** | **0.57** |
| A/B 訊號比 | 2.8:1 | |
| MDD | -8.91% | -4.76% |

**分析**：移除 ATR 過濾後，Part B Sharpe 恢復至 0.57（同 COPX-007），但 Part A 仍僅
0.15，WR 64.3% 顯著低於 COPX-007 的 76.2%。**Part A/B 累計差距 20.9%** 雖符合 < 30%
門檻，但 min(A,B) 僅 0.15，**不及 COPX-007 的 0.45**。hook 過濾仍系統性移除
Part A 好訊號（21→14 = -7，但 WR 從 76.2%→64.3% = -11.9pp）。

### 失敗根因與跨資產泛化邊界

**SIVR-015 成功 vs COPX-009 失敗的結構性差異**：

| 項目 | SIVR-015 | COPX-009 |
|------|----------|----------|
| 日波動 | ~2.3% | ~2.25% |
| 回檔回看窗口 | **10 日** | **20 日** |
| 回檔門檻 | 7-15% | 10-20% |
| 回檔持續時間 | 短（<10 日快速 capitulation） | 長（15-30 日延續下跌） |
| RSI hook 對齊 | ✓（5 日 lookback 對應 10 日框架） | ✗（5-10 日 lookback 無法對應 20 日框架） |
| 結果 | min 0.22→0.48 (+118%) | min 0.45→0.15 (-67%) |

**擴展跨資產教訓 §20b 的有效邊界**：RSI(14) bullish hook divergence 過濾器有效性需
**同時符合三個條件**：
1. 中高波動資產（日波動 2-3%）
2. 已驗證 pullback+WR 均值回歸框架
3. **回檔回看窗口 ≤10 日**（新增，COPX-009 驗證）

### 結論

1. **RSI bullish hook divergence 不可移植至長回看窗口（20 日）框架**：COPX-009 三次
   迭代全部失敗，最佳 min 0.15 vs COPX-007 的 0.45（-67%）。hook 過濾器的 RSI 動能
   轉折訊號只對應短週期 capitulation（≤10 日），無法捕捉長週期銅價下行中的真正底部
2. **cross_asset_lessons §20b 邊界擴展**：新增「回檔回看窗口 ≤10 日」為必要條件
3. COPX-007 仍為全域最優。COPX 至此已完成 9 次實驗、42+ 次嘗試，涵蓋均值回歸、
   波動率自適應、突破（BB Squeeze + Donchian）、配對交易、動量回檔、RS 動量、
   **RSI bullish hook divergence** 八大策略類型

---

## COPX-010: Post-Capitulation Vol-Transition MR ❌ 失敗

（CIBR-012 跨資產泛化測試，3 次嘗試均失敗，詳見 AI_CONTEXT 區塊。Trade-level 分析顯示 COPX winners/losers 在 2DD/1DD/ClosePos 維度高度重疊，無單一維度具區分力。）

---

## COPX-011: Multi-Week Regime-Aware BB Squeeze Breakout ✅ 當前最佳

### 目標 (Goal)

跨資產移植 lesson #22（TSLA-015 / NVDA-012 / FCX-013）的 buffered multi-week
SMA trend regime 至 COPX-005 BB Squeeze Breakout 之上，目標突破 COPX-007 全域
最佳的 min(A,B) 0.45。

**Repo 第 4 次 lesson #22 跨資產試驗，首次商品/礦業 ETF 驗證**。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | BB Width 擠壓 | 過去 5 日內 ≤ 60 日 30th 百分位 | 近期波動收縮（同 COPX-005）|
| 2 | BB 上軌突破 | Close > Upper BB(20, 2.0) | 突破訊號 |
| 3 | SMA(50) 趨勢 | Close > SMA(50) | 短期趨勢向上（同 COPX-005）|
| 4 | **regime BOX** | 1.00 ≤ SMA(20)/SMA(60) ≤ 1.09 | **新增**：lesson #22 + 過熱牛末過濾 |
| 冷卻 | 訊號間隔 | ≥ 12 交易日 | 避免重複進場（同 COPX-005）|

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 | +7% | 同 COPX-005 Att2/Att3 |
| 停損 | -6% | 同 COPX-005 Att2/Att3 |
| 持倉天數 | 20 天 | 同 COPX-005 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價） |
| 獲利出場 | `limit_order Day`（當日限價單） |
| 停損出場 | `stop_market GTC`（持倉期間停損市價） |
| 到期出場 | `next_open_market` |
| 滑價 | 0.15%（ETF 中等流動性） |
| 悲觀認定 | 是（同日觸及 TP 與 SL 視為 SL 先成交） |

### 三次迭代結果

| 迭代 | sma_regime_ratio_min | sma_regime_ratio_max | Part A Sharpe | Part B Sharpe | min(A,B) | 結論 |
|------|----------------------|----------------------|---------------|---------------|----------|------|
| Att1 | 1.00（FCX 嚴格直接移植）| ∞（無上限）| 0.65 | -0.04 | -0.04 | ❌ 失敗 |
| Att2 | 0.99（TSLA 緩衝移植）| ∞（無上限）| 0.43 | 0.28 | 0.28 | ❌ 失敗 |
| Att3 ★ | **1.00** | **1.09** | **0.72** | **0.64** | **0.64** | ✅ **+42%** |

### Att3 ★ 詳細結果（regime BOX [1.00, 1.09]）

**Part A（2019-2023）：**
- 訊號數：10（baseline COPX-005 baseline 18）
- 勝率：80.0%（baseline 66.7%）
- 累計報酬：+40.03%
- Sharpe：**0.72**
- MDD：-6.57%
- PF：4.29

**Part B（2024-2025）：**
- 訊號數：2（baseline 5）
- 勝率：50.0%（baseline 40.0%）
- 累計報酬：+5.35%
- Sharpe：**0.64**
- MDD：-4.72%
- PF：4.55

**min(A,B) Sharpe：0.64（+42% vs COPX-007 baseline 0.45）**

### 跨資產發現（Cross-Asset Insights）

**FCX 個股 vs COPX ETF 的 regime 機制差異**：

| 項目 | FCX-013（個股） | COPX-011（ETF） |
|------|-----------------|------------------|
| 失敗訊號 ratio 分布 | 集中於 < 1.00（transition zone） | 集中於 > 1.09（過熱牛末） |
| 有效規則 | 單純下限 k=1.00 | BOX [1.00, 1.09] 雙向 |
| 機制推測 | 個股噪音消除過熱信號 | ETF 平均化保留過熱信號 |

**lesson #22 v2 精煉**：buffered SMA regime 對商品/礦業類資產的應用，
個股形式單純下限即可，**ETF 形式需 BOX 結構**。

### Acceptance Criteria

| 標準 | 結果 | 是否達標 |
|------|------|----------|
| Sharpe > 基線（0.45）| 0.64 (+42%) | ✓ |
| A/B annualized cum gap < 30% | 66.4% | ✗（COPX 結構性邊界，類似 FCX-013 Att3 44%） |
| A/B annualized signal gap < 50% | 50% | ~（at boundary） |
| 使用成交模型 | 完整 | ✓ |
| Repo 較少使用方向 | lesson #22 第 4 次 + repo 首次 regime BOX | ✓ |

### 結論

1. **lesson #22 跨資產移植成功**：COPX 為 lesson #22 第 4 次試驗，首次商品/礦業 ETF 驗證
2. **Repo 首次 regime BOX 概念**：雙向 regime 過濾（k_min + k_max）為新策略結構，需在
   ETF 形式商品資產上才必要
3. **推翻 COPX-007 結構性 Sharpe 上限假設**：先前認定 COPX-007 0.45 為 2.25% vol
   商品 ETF 結構性上限，COPX-011 證明加上 regime context 可突破
4. **COPX-005 BB Squeeze 失敗的真正原因**：非「突破策略不適用 COPX」，而是缺乏 regime
   context（無法區分健康牛市突破 vs 過熱牛末假突破）
5. COPX-011 Att3 為新全域最優（11 次實驗、48+ 次嘗試）

---

## COPX-012: Volatility-Acceleration-Bounded MR（ATR ratio CEILING / 5d cap，3 次嘗試全部失敗）

詳見 AI_CONTEXT 區塊（CIBR-014 / FXI-014 / URA-013 跨資產移植，全部失敗）。COPX winners 在 ATR ratio 與 5d return 維度與 CIBR/FXI/URA 反向分布——商品超級週期驅動的礦業 ETF（COPX、CIBR-XME 類別）winners 偏深 ATR 與 5d capitulation，winners/losers 跨完整範圍無單一切點可區分。

---

## COPX-013: Macro-Confirmed Vol-Adaptive Capitulation MR（lesson #25 + #24 雙來源 forward-looking macro filter，3 次嘗試全部失敗）

### 目標 (Goal)

跨資產移植 lesson #25（IWM-015 broad-market macro context confirmation gate）+ lesson #24（forward-looking implied volatility direction filter）至 COPX 銅礦 ETF，希望以 broad-market regime 過濾 COPX idiosyncratic decline（中美貿易戰、銅價特定衝擊）。

### 進場條件

| 條件 | 指標 | 閾值 |
|------|------|------|
| 1 | 20 日高點回檔 | 10-20%（同 COPX-007） |
| 2 | Williams %R(10) | ≤ -80（同 COPX-007） |
| 3 | ATR(5)/ATR(20) | > 1.05（同 COPX-007） |
| 4 | SPY N 日報酬 | <= max_spy_return（lesson #25） |
| 5 | ^VIX N 日變化 | <= max_vix_change（lesson #24） |
| 6 | 冷卻期 | 12 天 |

### 出場參數

同 COPX-007（TP +3.5% / SL -4.5% / 持倉 20 天）

### 迭代嘗試紀錄

| # | 變更 | Part A | Part B | min(A,B) | 結論 |
|---|------|--------|--------|----------|------|
| 1 | SPY 10d <= 0%（loose） | 20/80%/0.57/+43.4% | 8/75%/0.42/+11.8% | 0.42 | ❌ Part B chain shift 引入新 SL |
| 2 | SPY 10d <= -1.5%（IWM-015 sweet spot） | 16/75%/**0.42**/+24.9% | 6/83.3%/**0.71**/+13.3% | 0.42 | ❌ Part A 退化（過嚴切除 winners） |
| 3 | SPY 10d <= 0 AND VIX 3d <= +5（雙來源） | 15/60%/**0.06**/+2.5% | 8/75%/0.42/+11.8% | 0.06 | ❌ chain shift 災難（4 連續 SL） |

### 失敗分析

**核心失敗模式：Cooldown chain shift（lesson #19 family）系統性抵消濾波效應**

當基礎策略 cooldown 12 日且原始訊號密度約 4/yr，過濾任何訊號會解除其 12 日 cooldown lockout，激活原本被壓制的鄰近訊號。COPX 的 SLs 與 winners 在 SPY 10d、VIX 3d 維度無乾淨分隔，激活的鄰近訊號常為 SL（macro stress 期間 COPX 多筆訊號 cluster）。

**三次迭代揭示**：
1. **Att1（loose threshold）**：Part A 改善（過濾 broad-up SL）但 Part B 因 chain shift 引入新 SL（2024-07-22 替換 2024-07-18）
2. **Att2（tight threshold IWM 移植）**：Part B 改善（5 TPs / 1 SL，Sharpe 0.71）但 Part A 過嚴切除 6 個 -1.5%~0 中性帶 winners
3. **Att3（雙來源組合）**：兩 filter 交集激活更多 cooldown lockouts，最大連續虧損從 baseline 2 增至 **4**，Part A WR 76.2% → 60%

### 跨資產結論

**lesson #25 cross-asset hypothesis 在 commodity miners ETF 上拒絕**——既有 lesson #25 僅適用「sub-segment ETF capitulation MR」（IWM small-cap），不適用商品/礦業 ETF。**機制差異**：
- IWM small-cap：broad-market 驅動明顯，QQQ 10d return 為單向 macro confirmation
- COPX commodity miners：受全球工業景氣 + 銅價週期 + 中國需求驅動，broad-market 非主要驅動因子，winners SPY 10d 廣泛分布（-9.13%~+4.72%）

**新失敗家族擴展**：lesson #25 適用邊界精煉至「broad-market 為主要驅動因子的 sub-segment ETF」（IWM ✓ / XBI ✗ / COPX ✗）。

**lesson #19 family 邊界擴展**：當基礎策略 cooldown 較長（≥10 日）+ 訊號密度低（< 5/yr）+ filter 過濾比例 > 40% 時，cooldown chain shift 結構性放大反向選擇——多重 macro filter 疊加為 lesson #19 family 中的「chain-shift collapse」失敗模式。

### Acceptance Criteria

| 標準 | Att3 結果 | 是否達標 |
|------|-----------|----------|
| Sharpe > COPX-011 全域最佳 0.64 | 0.06 | ✗ |
| A/B annualized cum gap < 30% | — | — |
| A/B annualized signal gap < 50% | — | — |
| 使用成交模型 | 完整 | ✓ |
| Repo 較少使用方向 | lesson #25 第 3 次 + lesson #24 + #25 首次組合 | ✓ |

### 結論

REJECT cross-asset hypothesis：lesson #25 broad-market macro confirmation gate + lesson #24 ^VIX direction filter 對 commodity miners ETF（COPX）結構性失敗。COPX-011 Att3 維持全域最優（13 次實驗、51+ 次嘗試）。

---

## COPX-014: Cross-Asset Divergence Regime-Gated BB Squeeze Breakout（TLT-014 / TSLA-017 cross-strategy port，3 次嘗試全部失敗）

### 動機

將 TLT-014（TLT vs SPY divergence regime gate，+393% Sharpe vs TLT-013）與
TSLA-017（TSLA vs QQQ divergence，+81% vs TSLA-015）的 cross-asset divergence
regime gate 技術 cross-strategy port 至 COPX-011 BB Squeeze Breakout 框架。

**核心假設**：當 COPX 相對「對應 anchor」（GLD 防禦金屬 / SPY 廣基 / XLB 材料板塊）
N 日報酬顯著弱勢時，即便 BB Squeeze 技術面突破，宏觀 regime 不利於後續延續，
應過濾此類訊號。

### 進場條件

同 COPX-011 Att3（BB Squeeze + breakout + regime BOX [k_min=1.00, k_max=1.09]）
+ **新增**：COPX N 日報酬 - benchmark N 日報酬 >= min_relative_return

### 出場參數

同 COPX-011（TP +7% / SL -6% / 持倉 20 天 / cd 12）

### 迭代嘗試紀錄

| # | anchor | lookback | threshold | Part A | Part B | min(A,B) | 結論 |
|---|--------|----------|-----------|--------|--------|----------|------|
| 1 | GLD | 20 | -0.05 | 10/80%/0.72/+40.0% | 2/50%/0.64/+5.4% | 0.64 | ❌ 無過濾效果 |
| 2 | GLD | 20 | +0.05 | 9/66.7%/**0.36**/+17.0% | 2/50%/0.64/+5.4% | **0.36** | ❌ cooldown chain shift 災難 |
| 3 | XLB | 20 | +0.005 | 10/80%/0.72/+40.0% | 2/50%/0.64/+5.4% | 0.64 | ❌ surgical filter 被 chain shift 中性化 |

### 失敗分析

**Att1 — threshold 過於寬鬆**：所有 12 訊號的 Rel_GLD 範圍 [-0.18%, +14.87%]
均 ≥ -5%。**核心發現**：BB Squeeze breakout 進場日 COPX 已突破上軌（短期強勢），
Rel_GLD/SPY/XLB 多為正值——「下限 floor」式 divergence gate 在突破策略上效果極弱。

**Att2 — cooldown chain shift 主導**：threshold +0.05 過濾 5 訊號（1 SL + 4 wins，
含 2019-04-01 SL / 2019-12-10 TP / 2021-04-15 TP / 2023-01-06 EX+ / 2023-12-13 EX+），
但 cooldown_days=12 內必然激活鄰近替代訊號：
- 2019-04-01 SL → **2019-04-04 SL**（同源 -6.14%）
- 2019-12-10 TP → 2019-12-12 EX +2.28%（替換 +7% TP，淨損失 4.7pp）
- 2023-01-06 EX +0.79% → **2023-01-10 EX -3.49%**（新增大型 EX-）
- 2023-12-13 EX +3.42% → 2023-12-14 EX +0.98%（淨損失 2.4pp）

**Att3 — surgical filter 被中性化**：選擇 XLB 作為更精準 anchor（COPX 為材料板塊
內子集合，divergence 更具經濟意義），threshold +0.005 surgical 命中唯一 outlier
2019-04-01 SL（Rel_XLB +0.0018，遠低於其餘 11 訊號 +0.0094~+0.1469）。但 cooldown
chain shift 重新激活 2019-04-04 SL（同源 -6.14%），結果與 baseline 完全相同。

### 跨資產結論（lesson #20 v3 邊界擴展，repo 首次發現）

**Cross-asset divergence regime gate 適用邊界三條件**：
1. **訊號日 anchor divergence 應具雙向分布**——不可結構性偏多（breakout 框架失敗）
   或結構性偏空（深度超賣 MR 部分失敗）
2. **cooldown 視窗 × 訊號密度 << 1.0**——避免 surgical filter 被 cooldown chain
   shift 中性化
3. **失敗訊號應為單日異常事件**而非「持續性弱勢期」（後者鄰近訊號通常具相同
   失敗結構）

**驗證統計**：
- TLT-014 ✓：rate-driven 寬基資產，cooldown 7d × 密度 ~3.5/yr ≈ 0.07，TLT-SPY
  20d divergence 在 reflation regime 顯著負，符合三條件
- TSLA-017 ✓：AI 高 vol 個股，cooldown 10d × 密度 ~5/yr ≈ 0.20，TSLA-QQQ 20d
  divergence 在 AI sentiment shift 顯著負，符合三條件
- **COPX-014 ✗**：商品/礦業 ETF + BB Squeeze breakout，cooldown 12d × 密度 ~2/yr
  ≈ 0.10（數值符合）但 BB Squeeze breakout **訊號日 Rel 結構偏多**違反條件 1，
  失敗訊號為**多年期持續性弱勢期**違反條件 3

**新跨資產規則**：cross-asset divergence regime gate 可用於 **MR 框架**（capitulation
訊號日已偏弱，divergence 可正向篩選）但**不適用於 BB Squeeze breakout 框架**。
建議未來嘗試方向：(a) 將 cross-asset divergence 應用於 COPX-007 vol-adaptive MR
而非 BB Squeeze breakout；(b) 改用 ABSOLUTE LEVEL（如 GLD 60d% 高分位數）
而非 RELATIVE RETURN，可能繞過訊號日結構偏多問題。

### Acceptance Criteria

| 標準 | Att3 結果 | 是否達標 |
|------|-----------|----------|
| Sharpe > COPX-011 全域最佳 0.64 | 0.64（持平） | ✗ |
| A/B annualized cum gap < 30% | 66.4%（同 baseline） | ✗ |
| A/B annualized signal gap < 50% | 50%（同 baseline） | ~ |
| 使用成交模型 | 完整 | ✓ |
| Repo 較少使用方向 | cross-asset divergence regime gate 第 3 次 + 商品/礦業類別首次 | ✓ |

### 結論

REJECT cross-strategy hypothesis：cross-asset divergence regime gate（TLT-014 /
TSLA-017 技術）對 COPX BB Squeeze Breakout 框架結構性失敗。lesson #20 v3
邊界擴展為 repo 重要發現：cross-asset divergence regime gate **不可從 MR 或
high-vol 個股 breakout 跨策略移植至商品/礦業 ETF BB Squeeze breakout**。
COPX-011 Att3 維持全域最優（14 次實驗、54+ 次嘗試）。

---

## COPX-015: ^VIX FLOOR Filter on BB Squeeze Breakout（FCX-015 cross-asset port，3 次嘗試 Att1 PARTIAL）

### 目標 (Goal)

跨資產驗證 lesson #24 family **FLOOR 變體**於商品/礦業 ETF BB Squeeze
Breakout 框架。將 FCX-015 Att2 成功的 ^VIX > 14 FLOOR regime gate
（commodity/mining 單股，min(A,B) 0.64→1.43，+123%，A/B cum gap
52.5%→7.1%）跨資產移植至 COPX-011 Att3 BB Squeeze Breakout 之上。

**Repo 第 2 次 lesson #24 family FLOOR 變體驗證 + 首次 ^VIX FLOOR 變體於
商品/礦業 ETF**。

### 進場條件

繼承 COPX-011 Att3 全部條件 + ^VIX FLOOR：

1. BB(20, 2.0) 60d 30th pct squeeze + 5d 內擠壓 + Close > Upper BB
2. Close > SMA(50)
3. **regime BOX**：1.00 <= SMA(20) / SMA(60) <= 1.09（lesson #22 + COPX-011 BOX）
4. **^VIX FLOOR**：^VIX 收盤值 > vix_low_threshold（lesson #24 family FLOOR）
5. 冷卻 12 日

### 出場參數

TP +7% / SL -6% / 持倉 20 天 / 滑價 0.15%（同 COPX-011）。

### 成交模型

- 進場：next_open_market（隔日開盤市價，含滑價）
- TP 出場：limit_order Day（當日限價）
- SL 出場：stop_market GTC
- 到期出場：next_open_market
- 悲觀認定：是

### 三次迭代結果

**Att1 ★（vix_low=14.0，FCX-015 sweet spot 直接移植）：PARTIAL**

| 指標 | Part A (2019-2023) | Part B (2024-2025) |
|------|--------------------|--------------------|
| 訊號數 | 7 | 2 |
| WR | **100%** | 50% |
| Sharpe | **2.81** | 0.64 |
| cum | +51.26% | +5.35% |
| MDD | -5.74% | -4.72% |

- min(A,B) **0.64**（與 baseline TIE，Part B 為 binding constraint）
- vs baseline COPX-011 Att3：Part A Sharpe 0.72 → 2.81（**+290%**），WR 80→100%
- VIX FLOOR 14 cleanly 過濾 3 個 Part A 失敗訊號（VIX ≤ 14 calm regime）：
  - 2019-04-01 SL VIX 13.40（baseline 唯一 SL）
  - 2023-07-12 EX -4.63% VIX 13.54
  - 2023-12-13 EX +3.42% VIX 12.19（正 EX，副作用過濾）
- Part B 兩訊號 VIX > 14（18.48 / 16.59），FLOOR 不綁定，**Part B 完全等於 baseline**
- A/B 累計 gap 73.9%（>30% ❌，惡化 vs baseline 66.4%）+ signal gap 71.4%（>50% ❌）

**Att2（vix_low=17.0，targeted Part B EX 過濾）：REJECT**

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 5 | **1** |
| WR | 100% | 100% (std=0) |
| Sharpe | 2.32 | 0.00 (zero-var) |
| cum | +32.12% | +7.00% |

- min(A,B)† **2.32** by † 慣例（Part B std=0，沿用 EWJ-003 / SPY-009 等慣例）
- **REJECT**：Part B 1 訊號統計顯著性嚴重不足，A/B signal ratio 5:1 = **80% gap >> 50% target**
- A/B 累計 gap 45.5% > 30% target

**Att3（vix_low=13.0，threshold robustness loosen）：DEGRADATION**

- Part A: 9 訊號 / WR 77.8% / Sharpe **0.69** / cum +35.40%（接近 baseline 0.72）
- Part B: 不變
- min(A,B) **0.64**
- **確認 FLOOR 14 為 sweet spot**：放寬 1pt 即放行 13.40 SL + 13.54 EX -4.63%

### 結論

PARTIAL：Att1 對 Part A 提供 290% Sharpe 提升 + 100% WR 為**實質改善**並
驗證 FCX-015 跨資產 FLOOR 假說，但 min(A,B) 結構性 TIE baseline 因 Part B
sample size 限制（COPX-011 Att3 regime BOX 後僅 2 訊號，VIX 皆 > 14 不綁定）。

**新跨資產規則 lesson #24 v6**：^VIX FLOOR 變體於 commodity/mining BB Squeeze
Breakout 框架在「Part A SL/EX 集中於 calm regime + Part B 訊號數 >= 3」
雙條件下有效——FCX 個股滿足兩條件 ✓；COPX ETF 因 Part B 僅 2 訊號失敗
第二條件 ✗——**sample size precondition 為跨資產 FLOOR 移植的新規則**。

COPX-011 Att3 維持全域最優（15 次實驗、57+ 次嘗試）。
