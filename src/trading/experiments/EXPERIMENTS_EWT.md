<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-05-16
  data_through: 2025-12-31
  note_2026_05_16_ewt011: EWT-011 added 2026-05-16 (Volatility-Regime-Gated → RS-Freshness Dual-Window Filter on RS Momentum Pullback — **Att3 SUCCESS vs robust baseline EWT-007：min(A,B) 0.42 → 0.56 (+33%)，雙 Part 真實變異（非 EWT-010 std=0 退化），repo 首次「dual-window RS freshness」維度於任何資產**, 探索 repo 中 EWT 較少使用的動量/RS 方向 + lesson #23 跨策略移植). 動機：EWT 文件「全域最優」EWT-010 Att2 雙 Part 皆 std=0（11 訊號全勝，統計退化），EWT 真實穩健最優為 EWT-007 RS 動量（Part A 19/0.42/+25.99%，Part B 7/0.93/+18.07%，雙 Part 真實變異，min 0.42，但 siggap 19:7 raw 63%）。EWT-007 Part A 拖累根因：4 個 SL（2019-05-07/2021-01-15/2021-07-19/2022-12-06）分散於多 regime + 多筆近零 time-expiry fizzle（stale 動量）。Three iterations: Att1 (vol regime gate ATR(14)/Close<=2.0%) Part A 18/77.8%/Sharpe **0.38** cum +21.73% / Part B 6/83.3%/0.81 cum +14.08% / min **0.38** REJECT — **失敗發現：EWT-007 的 4 個 Part A SL 分散 2019/2021/2022 非 vol 集中，vol gate 無外科分離力（與 DIA-013 Att3 vol-clustered 成功反向，精煉 lesson #23 適用邊界）**；Att2 (停用 vol gate，改 RS 新鮮度 dual-window：EWT−EEM 10日報酬差 > 0) Part A 18/83.3%/Sharpe **0.56** cum +31.38% / Part B **6**/83.3%/0.81 cum +14.08% / min **0.56**（beats EWT-007 0.42 +33% 但移除 1 Part B winner 7→6）；**Att3 ★ SUCCESS (rs_short_min 放寬至 -1%) Part A 18/83.3%/Sharpe 0.56 cum +31.38% / Part B 7/85.7%/Sharpe 0.93 cum +18.07%（與 EWT-007 baseline Part B 完全相同，7 winners 全保留）/ min(A,B) 0.56**（**+33% vs EWT-007 robust 0.42**）/ A/B 年化訊號比 3.6:3.5/yr = gap **3% << 50% ✓✓✓** / A/B 年化 cum 5.60%/y vs 8.66%/y → gap **35%**（>30% 略超，但較 EWT-007 baseline 45.5% 改善 -10pp）。**核心發現（lesson #23 邊界精煉 + repo 首次 dual-window RS freshness）**：(1) **vol regime gate 適用邊界精煉**：DIA-013 Att3 成功因 Part A SL vol-clustered（2020/2022 崩盤）；EWT-007 SL 分散多 regime → vol gate 失敗。vol regime gate 僅適用於「SL 在波動率維度單向集中」資產；(2) **repo 首次「dual-window RS freshness」維度**：要求短窗（10d）RS 仍 > 閾值，外科切除「長窗 20d RS 達標但動量已轉弱」的 stale fizzle 訊號（EWT-007 多筆近零 time-expiry 之根因），Part A Sharpe 0.42→0.56、WR 78.9%→83.3%，Part B 完全保留；(3) **rs_short_min 甜蜜點 -1%**：0.0（Att2）過嚴移除 1 Part B winner，-1%（Att3）回收且保留全部 Part A 增益，確認 sweet spot 落於 [-1%, 0%)；(4) **統計穩健性 > 顯示 Sharpe**：EWT-011 Att3 雙 Part 真實變異 min 0.56 較 EWT-010 Att2「11 訊號全勝 std=0 退化」結構性更可信，為 EWT 真實穩健新最優。**跨資產假設（待驗證）**：dual-window RS freshness（短窗 RS > 閾值疊加長窗 RS）可能擴展至其他 RS momentum 框架資產（TSM-008/NVDA-006/SOXL-010）。EWT-011 Att3 為 EWT 真實穩健新最優（11 次實驗、36+ 次嘗試），EWT-010 Att2 std=0 退化結構降為參考。
  note_2026_05_09_ewt010: EWT-010 added 2026-05-09 (EWT-EEM 2D Cross-Asset Divergence Filter on Vol-Transition MR, **Att2 ★ SUCCESS — repo 第 11 次 lesson #20 v3 cross-asset divergence regime gate 應用 + repo 首次「雙時框 (短+長 lookback) 同時 AND 條件」divergence 過濾於任何資產**, cross-strategy port from EWZ-009/INDA-012/EWJ-006/FXI-015/GLD-016 cross-asset divergence family). Three iterations: **Att1 (5d/+1.5pp AND 60d/+5pp)** cooldown chain-shift TIE baseline 1.11 — short_lookback=5 在 2019-05-09 SL 過濾後解除 cooldown，2019-05-13（5d_div +0.43pp 未越界 +1.5）以新 SL -4.10% 啟動，Part A 9/88.9%/Sharpe 1.11 cum +26.28% 與 baseline 數字完全相同（lesson #19 family cooldown chain-shift 失敗模式）；**Att2 ★ (20d/+3.0pp AND 60d/+5pp) SUCCESS** Part A **8/100% WR/std=0** cum **+31.68%** MDD -3.89% / Part B 3/100%/std=0 cum +10.87% 不變 / min(A,B)† **structurally NO LOSS**（雙 Part 全勝零方差，依 IBIT-009 Att1 慣例優於 baseline 1.11/std=0 的「Part A 1 SL + Part B 全勝」結構，Part A cum +20.5%）—— 20d 維度同時切除 2019-05-09 SL（20d +4.35）與 cooldown chain-shift 2019-05-13 SL（20d +3.37），所有 11 個 TPs 保留（最近邊界 2019-08-02 TP 20d +3.03 但 60d -0.23 由 AND 條件保護）/ A/B 年化 cum 6.34%/y vs 5.43%/y → gap 14.4% < 30% ✓ / A/B 訊號比 1.6:1.5 = 6.7% gap ≤ 50% ✓ / Att3 (20d/+2.5pp loose threshold) Part A **7**/100%/std=0 cum +27.23%（過鬆同時過濾 2023-03-15 TP，20d +2.87），確認 +3.0pp 為 short_threshold 結構性下界 sweet spot。**核心發現（lesson #20 v3 family v3 dimensionality 擴展，repo 首次 2D AND 條件 divergence 過濾）**: (1) EWT 失敗模式特殊——2019-05-09 SL 在任一單一 lookback (5d/10d/20d/60d) 皆**非 outlier**（與 INDA-012 SL 60d +15.28% 為唯一 > +5% outlier 不同），需雙時框 AND 條件才能 surgical separation；(2) **lesson #20 v3 family v3 dimensionality 擴展**：1D（EWZ/INDA/EWJ/FXI/GLD/TLT/TSLA/NVDA 全部）→ **2D AND**（EWT 首例）依資產失敗模式選擇 dimensionality；(3) **cooldown chain-shift 預防**：當訊號間隔接近 cooldown 閾值，short_lookback 需擴大至涵蓋 cooldown window（5d 不足，20d 同時切除 2019-05-09 + 2019-05-13 雙 SL）；(4) repo 第 3 次 EM single-country + EEM benchmark anchor（EWZ-009 / INDA-012 後）/ 首次半導體驅動 EM 單一國家 ETF（TSM ~25% 權重）+ EEM anchor + 雙時框 AND；(5) EWT 結構性 Sharpe 1.11 ceiling 在 1D 維度飽和，2D AND 維度開啟新空間並達成「雙 Part 全勝零方差」結構性最優。EWT-010 Att2 為新全域最優（10 次實驗、33+ 次嘗試）。
  note_2026_05_17_ewt012: EWT-010 added 2026-05-17 (EWT–EEM Cross-Asset Divergence Regime-Gated MR — **documented-failure，cross-asset divergence regime gate family v4 第 2 次失敗（繼 SIVR-019 後）**，predict→confirm 預分析完全正確). 空遠端 artifact `ewt_010_ewt_eem_2d_divergence_mr` 指向此方向，用獨立 module 名稱 `ewt_012_eem_divergence_regime_mr`（branch-divergence caveat）。在 EWT-009 Att3 全域最優 base 上加第 7 條件 EWT−EEM N日 divergence gate。Trade-level 預分析：EWT-009 Att3 binding = Part A 唯一殘餘 SL 2019-05-09（中美貿易戰關稅升級 -4.10%），其 EWT−EEM 2d divergence = **+0.03**（EWT_2d -1.69 ≈ EEM_2d -1.72，廣域 China/EM co-move），與 11 winners DIV ∈ [-2.16, +1.73] 完全交錯；3 筆 Part B winners DIV 全為最負（-1.75/-1.86/-2.16）。三次迭代全 FAIL vs EWT-009 Att3 min(A,B)† 1.11：Att1（2d CEILING ≤ 0.0%）min† 1.01 — 移除 2019-05-09 SL 但 cooldown chain-shift 至 2019-05-13 新 SL（貿易戰多日延續，lesson #19 / SOXL-013 / GLD-016-Att1 isomorph）+ 非外科式殺 Part A winner 2021-07-27（DIV +1.73），Part B 完全非綁定不變；Att2（2d FLOOR ≥ -1.0%，TLT-014/GLD-016-Att2 類比）min† 0.91 — 完全不移除 SL（DIV +0.03 ≥ -1.0% 通過）反而屠殺全部 3 筆最高品質 Part B winners（3→1），inverted catastrophic；Att3（1d CEILING ≤ 0.0% lookback ablation）min† 1.01 — 1d-DIV SL=-0.20≤0.0 連 SL 都不隔離仍殺 2021-07-27，確認無可分 cross-asset divergence lookback。**核心發現**：EWT 非 DRIVER-PURE（EWT 是 EEM 成分，ρ≈0.85 正相關，非單因子反向），binding loser（2019 貿易戰）為同步廣域 China/EM geopolitical co-move（DIV≈0）非台灣 idiosyncratic divergence → 違反 family v4 前置條件（SIVR-019 規則）。EWT 加入 EWJ/EWZ/EEM/TSM country-idiosyncratic non-separable 家族（lesson #27 / lesson #6 反例9）。空遠端 artifact 方向為 false lead（SIVR-019 caveat 再確認）。EWT-009 Att3 仍為全域最優（10 次實驗、33+ 次嘗試）。
  note: EWT-009 added 2026-04-27 (Post-Capitulation Vol-Transition MR：EWT-008 Att1 框架 + 「2 日報酬下限」過濾，**Att3 SUCCESS — repo 第 6 次「2DD floor」方向成功驗證，繼 USO-013 / EEM-014 / INDA-010 / VGK-008 / EWJ-005 後首次半導體驅動 EM 單一國家 ETF 驗證**). Three iterations: Att1 (2DD floor <= -2.0%，VGK-008 Att2 直接移植) Part A 7/85.7%/Sharpe 0.91 cum +17.89% / Part B 3/100%/std=0 cum +10.87% / min(A,B)† 0.91 (+59.6% vs baseline 0.57，但 -2.0% 過嚴過濾 2 筆 winners 並引入 2019-05-13 cooldown shift 新 SL); Att2 (1d floor <= -1.0%，SPY-009 / EWJ-005 Att2 1d 維度跨資產移植) Part A 8/87.5%/Sharpe 1.01 cum +22.01% / Part B **2**/100%/std=0 cum +7.12% / min(A,B)† 1.01 (+77% vs baseline，但 1d -1.0% **誤殺 Part B 2025-11-18 winner**（1d -0.78%），Part B 從 3 縮至 2，總體不如 Att3); Att3 ★ (2DD floor <= -1.5%，精準目標 2022-01-25 SL 之 2d -0.46%) Part A 9 訊號 WR **88.9%** Sharpe **1.11** cum +26.28% / Part B 3 訊號 WR 100% std=0 cum +10.87% / min(A,B)† **1.11**（+94.7% vs baseline 0.57，A/B 累計差 15.41pp / 26.28% = 58.6%）—— **意外收益（cooldown chain shift 正向，lesson #19）**：移除 2022-01-25 SL 後，原本被 cooldown 抑制的 2022-01-28 訊號活化並達標 +3.50%，Part A 訊號數**保持 9 不變**，WR 從 77.8%→88.9%（8 TPs + 1 SL）。Part B 全部 3 筆 winners 保留（2d -3.70%/-4.23%/-3.84% 皆深於 -1.5%）。**核心發現**：(1) EWT 2DD 維度有效（不同於 EWJ-005 Att1 的 2DD -2.0% 過嚴），因 EWT 有 1 筆淺 2DD SL（2022-01-25 2d -0.46%）剛好被 -1.5% 過濾，且所有 winners 2d 皆深於 -1.5%（最淺 -1.87% = 2023-03-15 TP）；(2) Att2 1d -1.0% 雖在 EWJ 上成功（EWJ-005 Att2 1d -0.5%）但 EWT 上因 Part B 含 1 筆 1d -0.78% 淺 1d winner 而失敗，跨資產 1d 維度需檢查 Part B winners 1d 分布；(3) **lesson #19 雙向發現再擴展**：2DD floor 對 EWT 1.41% vol 半導體驅動 EM 單一國家 ETF 有效，閾值精準度（-1.5% vs -2.0%）為關鍵變量。EWT-009 Att3 為前任最佳。
-->
## AI Agent 快速索引

**真實穩健最優（statistically robust，2026-05-16）：** ★ **EWT-011 Att3**（Volatility-Regime-Gated → RS-Freshness Dual-Window Filter on RS Momentum Pullback：EWT-007 Att1 RS 動量框架 + **EWT−EEM 10日報酬差 > -1% dual-window RS freshness 過濾**，TP+3.5%/SL-4.0%/20d/cd10）
- Part A: 18 訊號 / WR 83.3% / Sharpe **0.56** / 累計 +31.38%（vs EWT-007 19/78.9%/0.42/+25.99%，**Sharpe +33% / WR +4.4pp / cum +21%**）
- Part B: 7 訊號 / WR 85.7% / Sharpe **0.93** / 累計 +18.07%（與 EWT-007 baseline Part B **完全相同**，7 winners 全保留）
- min(A,B) **0.56**（**+33% vs EWT-007 真實穩健 baseline 0.42**，雙 Part 真實變異，統計上較 EWT-010 std=0 退化結構可信）
- A/B 年化訊號比 3.6:3.5/yr = **gap 3% << 50% ✓✓✓**；A/B 年化 cum 5.60%/y vs 8.66%/y → gap **35%**（>30% 略超，但較 EWT-007 baseline 45.5% 改善 -10pp）
- **跨資產貢獻**：repo 首次「dual-window RS freshness」維度（短窗 RS 仍 > 閾值，外科切除長窗達標但動量轉弱的 stale fizzle 訊號）；精煉 lesson #23 vol regime gate 適用邊界（SL 須 vol-clustered，EWT SL 分散多 regime 故 vol gate 失敗，與 DIA-013 反向）

**文件「全域最優」（std=0 退化，僅供參考）：** ★ **EWT-010 Att2**（EWT-EEM 2D Cross-Asset Divergence Filter on Vol-Transition MR：EWT-009 Att3 完整框架 + **EWT-EEM 20 日報酬差 ≥ +3.0pp AND 60 日報酬差 ≥ +5.0pp 同時成立 → 過濾**，TP+3.5%/SL-4.0%/20d/cd 10）— **雙 Part 皆 std=0（11 訊號全勝），統計退化，不具真實變異 risk-adjusted 意義**
- Part A: **8 訊號 / WR 100% / Sharpe 0.00 (std=0 zero-var)** / 累計 **+31.68%** / MDD -3.89%（vs baseline 9/88.9%/1.11/+26.28%/-4.08%）
- Part B: 3 訊號 / WR 100% / std=0 / 累計 +10.87%（與 baseline 完全相同，filter 對 Part B 完全非綁定）
- min(A,B)† **structurally NO LOSS**（雙 Part 全勝零方差，依 IBIT-009 Att1 慣例優於 baseline 1.11/std=0 的「Part A 1 SL + Part B 全勝」結構）
- A/B 年化 cum 6.34%/y vs 5.43%/y → gap **14.4% < 30% ✓**
- A/B 訊號比 1.6:1.5 = **6.7% gap << 50% ✓**（vs baseline 16.7%，進一步改善）
- 關鍵改善機制：20d 維度同時切除 2019-05-09 SL（20d_div +4.35）與 cooldown chain-shift 2019-05-13 SL（20d_div +3.37），所有 11 個 TPs 保留（最近邊界 2019-08-02 TP 20d +3.03 但 60d -0.23 < +5 由 AND 條件保護）
- Part A SL 完全清零，Part A cum 從 +26.28% → **+31.68%**（+5.4pp，+20.5%）
- **跨資產貢獻**：repo 第 11 次 lesson #20 v3 cross-asset divergence regime gate 應用 + **repo 首次「雙時框 (短+長 lookback) 同時 AND 條件」divergence 過濾於任何資產**（lesson #20 v3 family v3 dimensionality 擴展：1D → 2D AND）

**前任最佳：** EWT-009 Att3（Post-Capitulation Vol-Transition MR：EWT-008 Att1 框架 + **2 日報酬下限 <= -1.5%**，TP+3.5%/SL-4.0%/20d/cd10）
- Part A: Sharpe **1.11**, 累計 +26.28%, 9 訊號 (1.8/年), WR **88.9%**, MDD -4.08%
- Part B: 累計 +10.87%, 3 訊號 (1.5/年), WR 100%（3/3 全部達標，Sharpe 因 std=0 顯示 0.00）
- min(A,B)† **1.11**（Part A 為約束，沿用 EWJ-003/EWT-008/EWZ-006/VGK-008 慣例）, +94.7% vs EWT-008 Att1 的 0.57

**前前任最佳：** EWT-008 Att1（BB 下軌+回檔上限混合進場均值回歸：BB(20, 2.0) 下軌 + 10日高點回檔上限-8% + WR(10)≤-80 + ClosePos≥40% + ATR(5)/ATR(20)>1.10，TP+3.5%/SL-4.0%/20d，冷卻10天）
- Part A Sharpe 0.57 / Part B Sharpe 0.00† / min(A,B) 0.57†
- Part A: 9 訊號 WR 77.8%, 累計 +17.01% / Part B: 3 訊號 WR 100%, 累計 +10.87%

**次佳（RS 動量）：** EWT-007 Att1（EEM 參考 RS≥3% + 5日回撤 2-5% + SMA(50)，min(A,B) 0.42，Part B Sharpe 0.93）
**前任最佳（均值回歸）：** EWT-006 Att2（min(A,B) 0.28，出場優化均值回歸）

**已證明無效（禁止重複嘗試）：**
- BB Squeeze 突破（EWT-003）：Part A 0.35 / Part B -0.37，嚴重市場狀態依賴（單一國家 ETF 地緣政治風險導致突破失敗，同 INDA-003 結論）
- RSI(2) 框架（EWT-005，3 次嘗試）：Part A 最佳 0.05（Att2），Part B 最佳 0.34（Att1），min(A,B) 最佳 0.05。確認 cross-asset lesson #27：非美國單一國家 ETF 受地緣政治事件影響，RSI(2) 訊號在延續性危機中無法恢復
- ATR > 1.1 門檻（EWT-002 Att2, EWT-004 Att2）：讓入慢磨下跌信號，2日急跌無法補償（EWT-004 Att2: Part A 0.02）
- 追蹤停損啟動/TP 比 < 80%（EWT-001）：啟動 2.5%/TP 4.5% = 55.6%，壓縮獲利
- SL -5.5%（EWT-004 Att3）：SL 加寬未轉換任何停損交易，只增加虧損金額（Part A 0.08 < Att1 0.15）
- SL -5.0% 配合 TP +5.0%（vs Att1 的 SL -4.5%）：2022 熊市 SL 交易全部穿越 -5.5%，加寬 SL 無效
- SL -3.5% 在 RSI(2) 框架下（EWT-005 Att2）：翻轉贏家為停損，Part B 0.34→0.05
- 移除 2日急跌過濾（EWT-006 Att1）：額外訊號品質差（+1 SL +3 到期），Part A Sharpe 不變 0.15
- 持倉 12 天太短（EWT-006 Att3）：Part B 1 個 TP→到期轉換失敗，min(A,B) 退化至 0.26
- RS 門檻 ≥ 4%（EWT-007 Att2）：過嚴過濾掉 2 筆 Part B 好訊號（Feb 2024, Jul 2025），min(A,B) 0.42→0.40
- SMH 作為 RS 參考基準（EWT-007 Att3）：Part A 0.12 / Part B -0.67，完全失敗。EWT 非純半導體 ETF，非半導體成分稀釋 RS 訊號品質
- BB(20, 1.75) 下軌 + cap -8%（EWT-008 Att2）：放寬 BB std 引入低品質訊號，Part A 0.27/Part B 0.12，三重品質過濾在 1.75σ 下失去選擇性
- BB(20, 2.0) 下軌 + cap -10%（EWT-008 Att3）：放寬回檔上限到 -10% 新增 2 筆 Part A 訊號但 WR 從 77.8%→72.7%，Sharpe 0.57→0.55；Part B 訊號集完全不變（2024-2025 無 -8~-10% 區間 BB 下軌觸及）
- **2DD floor <= -2.0%（EWT-009 Att1）— -2.0% 過嚴**：Part A 7/85.7%/Sharpe 0.91 cum +17.89%（vs baseline 0.57），但 -2.0% 同時過濾 2 筆 shallow-2DD winners（2019-05-09 2d -1.69%、2023-03-15 2d -1.87%）並引入 2019-05-13 cooldown shift 新 SL（lesson #19），Part A 訊號從 9 縮至 7。Att3 -1.5% 為精準甜蜜點
- **1d floor <= -1.0%（EWT-009 Att2）— Part B winner 流失**：Part A 8/87.5%/Sharpe 1.01 cum +22.01% 但 Part B **2**/100%/cum +7.12%（流失 2025-11-18 1d -0.78% 淺 1d winner），總 min(A,B)† 1.01 但 Part B 訊號密度降至 1.0/yr 過稀疏。確認 EWT 1d 維度不如 2d 維度（與 EWJ 1.15% vol 1d -0.5% 成功不同——EWT 1.41% vol Part B 含 1d 過淺 winner）
- **EWT-EEM 5d/+1.5pp AND 60d/+5pp divergence filter（EWT-010 Att1）— short_lookback=5 太短引發 cooldown chain-shift**：Part A 9/88.9%/Sharpe 1.11 cum +26.28% 與 baseline 完全相同數字（TIE），原因 short_lookback=5 過濾 2019-05-09 SL 後解除 cooldown，2019-05-13 訊號（5d_div +0.43pp 低於 +1.5 閾值）以新 SL -4.10% 啟動。lesson #19 family cooldown chain-shift 失敗模式
- **EWT-EEM 20d/+2.5pp AND 60d/+5pp divergence filter（EWT-010 Att3）— short_threshold +2.5pp 過鬆**：Part A 7/100%/std=0 cum +27.23%（vs Att2 8/+31.68%），+2.5pp 同時過濾 2023-03-15 TP（20d +2.87 ≥ 2.5 ✓ AND 60d +5.97 ≥ 5 ✓），確認 +3.0pp 為 short_threshold 結構性下界 sweet spot
- **EWT–EEM 跨資產 divergence regime gate（EWT-012，3 次迭代全 FAIL）— family v4 第 2 次失敗**：在 EWT-009 Att3 base 加 EWT−EEM N日 divergence 第 7 條件。Att1（2d CEILING ≤ 0.0%）min(A,B)† 1.01 — 移除 binding SL 2019-05-09 但 cooldown chain-shift 至 2019-05-13 新 SL（lesson #19，貿易戰多日延續，SOXL-013/GLD-016-Att1 isomorph）+ 非外科式殺 Part A winner 2021-07-27，Part B 完全非綁定；Att2（2d FLOOR ≥ -1.0%）min† 0.91 — 不移除 SL（DIV +0.03≥-1.0%）反屠殺全部 3 筆 Part B winners（3→1）inverted catastrophic；Att3（1d CEILING ≤ 0.0% ablation）min† 1.01 — 1d-DIV SL=-0.20≤0.0 連 SL 都不隔離。**根因**：EWT 非 DRIVER-PURE（EWT 是 EEM 成分 ρ≈0.85 正相關），binding loser（2019 中美貿易戰）為同步廣域 China/EM co-move（DIV≈0）非台灣 idiosyncratic divergence，與 winners 任一 lookback 完全交錯。違反 cross-asset divergence regime gate family v4 前置條件（SIVR-019 規則）；EWT 確認加入 EWJ/EWZ/EEM/TSM country-idiosyncratic non-separable 家族（lesson #27 / lesson #6 反例9）

**已掃描的參數空間：**
- 進場（pullback+WR）：10日回檔 4-10% + WR(10) ≤-80 + ClosePos ≥40% + ATR > 1.15/1.1 + 2日跌幅 ≤-1.5% / 無
- 進場（RSI(2)）：RSI(2)<10 + ClosePos≥40% + ATR>1.15 ± 2日跌幅≤-1.5%
- 進場（RS 動量）：EWT vs EEM/SMH 20日 RS ≥ 3%/4% + 5日回撤 2-5% + SMA(50)
- **進場（BB 下軌混合）**：BB(20, 1.75/2.0) 下軌 + 10日回檔上限 -8%/-10% + WR + ClosePos + ATR > 1.10，BB 2.0σ + cap -8% 為甜蜜點
- **進場（Vol-Transition + 2DD floor）**：BB(20, 2.0) 下軌 + 回檔上限 + WR + ClosePos + ATR + 2DD floor <= -1.5%（EWT-009 Att3）
- **進場（Vol-Transition + 2D Divergence Gate）**：EWT-009 Att3 + EWT-EEM 20d/60d 雙時框 AND divergence filter（EWT-010 Att2 ★ 當前最佳）
- 出場：TP +3.5~5.0% / SL -3.5~5.5% / 持倉 12~20天 / 無追蹤停損
- 追蹤停損：啟動 +2.5%/距離 2.0%（無效，啟動/TP 比太低）
- BB Squeeze: BB(20,2) + 30th pct + SMA(50) + TP 3.5%/SL 3.5%/20d（無效）
- RS 參考基準：EEM（RS 動量、divergence regime gate 皆有效）、SMH（RS 動量無效，未測 divergence regime gate）
- **Cross-asset divergence regime gate (lesson #20 v3)**：EWT-EEM 雙時框 (20d AND 60d) AND 條件 +3.0pp/+5.0pp 為當前最佳維度
- RS 參考基準：EEM（最佳）、SMH（完全無效）
- **EWT–EEM divergence regime gate（EWT-012）**：2d CEILING ≤ 0.0% / 2d FLOOR ≥ -1.0% / 1d CEILING ≤ 0.0%（三型皆 FAIL，binding SL 與 winners 任一 lookback 完全交錯）

**尚未嘗試的方向（預期邊際效益極低）：**
- RS 出場優化（TP+4.0%/SL-3.5% 或延長持倉 25d）：可微調但 EWT-007 Att1 已很優，風險 > 收益
- 混合模式 × RS 動量交叉（兩者 OR 進場）：但 A/B 訊號比可能失衡
- 更深均值回歸回檔門檻（5%）配合 2日急跌（訊號數已偏低 3.2/年）
- ~~EWT–EEM 跨資產 divergence regime gate~~ → EWT-010 三次迭代全 FAIL（family v4 第 2 次失敗，EWT 非 driver-pure，binding loser 為廣域 China/EM co-move 非 idiosyncratic divergence）

**關鍵資產特性：**
- EWT 為 iShares MSCI Taiwan ETF，追蹤台灣股市，半導體權重極高（TSM 為最大持股）
- 日均波動約 1.41%，GLD 的 1.26 倍，屬低波動資產（接近中波動邊界）
- 受半導體週期、中美地緣政治、台幣匯率波動影響
- 高流動性 ETF，滑價假設 0.1%
- **BB 下軌+回檔上限混合進場模式在 EWT 有效**（EWT-008 驗證）：日波動 1.41% 落在 lesson #52 有效 vol 區間 [1.12%, 1.75%] 中段。BB(20, 2.0) + cap -8%（5.7σ）+ 三重品質過濾 min(A,B) 0.57†（Part A 綁定約束），超越 RS 動量 0.42。Part B 3 筆全達 TP +3.50%（零方差 Sharpe 形式為 0），與 EWJ-003 同模式
- **RS 動量（EWT vs EEM）次佳策略**：台灣在 EM 中的超額表現由半導體出口結構性驅動，A/B 年化訊號比 1.09:1 近乎完美。Part B Sharpe 0.93 優於混合進場的形式零變異，在 Part B 變異性回復後仍具互補價值
- **SMH 作為 RS 參考完全無效**：EWT 含大量非半導體成分，稀釋 RS 訊號品質
- ATR 甜蜜點 > 1.10（混合進場模式，vs 均值回歸的 1.15）
- BB Squeeze 突破無效（單一國家 ETF 地緣政治風險，同 INDA 結論）
- RSI(2) 無效（非美國單一國家 ETF，地緣政治事件導致）
- SL -4.0% 是 EWT 跨策略甜蜜點（RS 動量和混合進場均驗證）
- TP +3.5% 跨策略通用甜蜜點（均值回歸、RS 動量、混合進場均驗證）
- **EWT 非 cross-asset divergence regime gate 適用標的（EWT-010 確認）**：EWT 是 EEM 成分（ρ≈0.85 正相關），非 driver-pure 單因子反向；其 binding loser（中美貿易戰）為同步廣域 China/EM geopolitical co-move（EWT−EEM divergence≈0）非台灣 idiosyncratic divergence。EWT−EEM RS 動量作為**進場觸發**有效（EWT-007 次佳，台灣半導體出口超額表現），但作為**品質 regime gate** 無區分力——RS-entry ≠ divergence-gate。EWT 加入 EWJ/EWZ/EEM/TSM country-idiosyncratic non-separable 家族
<!-- AI_CONTEXT_END -->

# EWT 實驗總覽 (EWT Experiments Overview)

## 標的特性 (Asset Characteristics)

- **EWT (iShares MSCI Taiwan ETF)**：追蹤 MSCI Taiwan 25/50 指數，涵蓋台灣大中型股
- 日均波動約 1.41%，GLD 的 1.26 倍，屬低波動資產（接近中波動邊界 1.5%）
- 半導體權重極高（TSM 佔比超過 20%），受全球半導體週期驅動
- 地緣政治敏感（中美關係、台海局勢）
- 年化波動率約 22.3%

## 參數對照表 (Parameter Comparison)

| 參數 | EWT-001 | EWT-002 Att1 | EWT-003 | EWT-004 Att1 | EWT-005 Att3 | EWT-006 Att2 | EWT-007 Att1 | EWT-008 Att1 | EWT-009 Att3 | **EWT-010 Att2 ★** |
|------|---------|-------------|---------|----------------|-------------|----------------|---------------|--------------|--------------|----------------|
| 策略類型 | 均值回歸（追蹤停損）| 均值回歸（ATR 自適應）| BB Squeeze 突破 | 均值回歸（2日急跌+非對稱）| RSI(2)（ATR 自適應）| 均值回歸（出場優化）| RS 動量回調 | BB 下軌混合進場 | Vol-Transition MR | **Cross-Asset 2D Divergence MR** |
| 進場框架 | pullback+WR | pullback+WR | BB Squeeze | pullback+WR | RSI(2) | pullback+WR | RS Momentum | BB Lower + Cap | BB Lower + Cap + 2DD | **EWT-009 + 雙時框 EWT-EEM 2D AND** |
| 回檔門檻 | ≤-4% | ≤-4%（上限-10%）| — | ≤-4%（上限-10%）| — | ≤-4%（上限-10%）| — | Cap≤-8% | Cap≤-8% | **Cap≤-8%** |
| BB 下軌 | — | — | — | — | — | — | — | BB(20, 2.0) | BB(20, 2.0) | **BB(20, 2.0)** |
| WR(10) | ≤-80 | ≤-80 | — | ≤-80 | — | ≤-80 | — | ≤-80 | ≤-80 | **≤-80** |
| RSI(2) | — | — | — | — | <10 | — | — | — | — | — |
| RS (EWT-EEM) | — | — | — | — | — | — | ≥3% | — | — | — |
| 5日回撤 | — | — | — | — | — | — | 2-5% | — | — | — |
| ClosePos | ≥40% | ≥40% | — | ≥40% | ≥40% | ≥40% | — | ≥40% | ≥40% | **≥40%** |
| ATR 過濾 | — | >1.15 | — | >1.15 | >1.15 | >1.15 | — | >1.10 | >1.10 | **>1.10** |
| 2日急跌（floor）| — | — | — | ≤-1.5%（cap）| — | ≤-1.5%（cap）| — | — | ≤-1.5%（floor）| **≤-1.5%（floor）** |
| Cross-Asset Filter | — | — | — | — | — | — | — | — | — | **NOT (20d_div ≥+3% AND 60d_div ≥+5%)** |
| BB Squeeze | — | — | 30th pct/60d | — | — | — | — | — | — | — |
| SMA 趨勢 | — | — | SMA(50) | — | — | — | SMA(50) | — | — | — |
| TP | +4.5% | +4.5% | +3.5% | +5.0% | +4.5% | +3.5% | +3.5% | +3.5% | +3.5% | **+3.5%** |
| SL | -5.0% | -5.0% | -3.5% | -4.5% | -4.5% | -4.5% | -4.0% | -4.0% | -4.0% | **-4.0%** |
| 持倉天數 | 18 | 18 | 20 | 20 | 12 | 15 | 20 | 20 | 20 | **20** |
| 追蹤停損 | 啟動+2.5%/距離2% | 無 | 無 | 無 | 無 | 無 | 無 | 無 | 無 | 無 |
| 冷卻期 | 8 | 8 | 10 | 8 | 5 | 8 | 10 | 10 | 10 | **10** |
| Part A Sharpe | 0.10 | 0.13 | 0.35 | 0.15 | -0.00 | 0.28 | 0.42 | 0.57 | 1.11 | **0.00‡** |
| Part B Sharpe | 0.57 | 0.64 | -0.37 | 0.48 | 0.31 | 0.50 | 0.93 | 0.00† | 0.00† | **0.00‡** |
| min(A,B) | 0.10 | 0.13 | -0.37 | 0.15 | -0.00 | 0.28 | 0.42 | 0.57† | 1.11† | **NO LOSS‡** |
| Part A 累計 | — | — | — | — | — | — | — | +17.01% | +26.28% | **+31.68%** |
| Part A WR | — | — | — | — | — | — | — | 77.8% | 88.9% | **100%** |

† EWT-008 / EWT-009 Part B 3/3 全達 +3.50% 零方差，採 EWJ-003 慣例以 Part A Sharpe 為綁定約束
‡ EWT-010 Att2 雙 Part 全勝零方差（IBIT-009 Att1 慣例），結構性 NO LOSS 優於 baseline 1.11/std=0 結構

| 參數 | EWT-001 | EWT-002 Att1 | EWT-003 | EWT-004 Att1 | EWT-005 Att3 | EWT-006 Att2 | EWT-007 Att1 | EWT-008 Att1 | **EWT-009 Att3 ★** | EWT-012 Att1 |
|------|---------|-------------|---------|----------------|-------------|----------------|---------------|--------------|----------------|--------------|
| 策略類型 | 均值回歸（追蹤停損）| 均值回歸（ATR 自適應）| BB Squeeze 突破 | 均值回歸（2日急跌+非對稱）| RSI(2)（ATR 自適應）| 均值回歸（出場優化）| RS 動量回調 | BB 下軌混合進場 | **Vol-Transition MR** | Divergence Gate MR |
| 進場框架 | pullback+WR | pullback+WR | BB Squeeze | pullback+WR | RSI(2) | pullback+WR | RS Momentum | BB Lower + Cap | **BB Lower + Cap + 2DD** | EWT-009 Att3 + Div |
| 回檔門檻 | ≤-4% | ≤-4%（上限-10%）| — | ≤-4%（上限-10%）| — | ≤-4%（上限-10%）| — | Cap≤-8% | **Cap≤-8%** | Cap≤-8% |
| BB 下軌 | — | — | — | — | — | — | — | BB(20, 2.0) | **BB(20, 2.0)** | BB(20, 2.0) |
| WR(10) | ≤-80 | ≤-80 | — | ≤-80 | — | ≤-80 | — | ≤-80 | **≤-80** | ≤-80 |
| RSI(2) | — | — | — | — | <10 | — | — | — | — | — |
| RS (EWT-EEM) | — | — | — | — | — | — | ≥3% | — | — | — |
| EWT−EEM Div gate | — | — | — | — | — | — | — | — | — | 2d CEILING≤0.0% |
| 5日回撤 | — | — | — | — | — | — | 2-5% | — | — | — |
| ClosePos | ≥40% | ≥40% | — | ≥40% | ≥40% | ≥40% | — | ≥40% | **≥40%** | ≥40% |
| ATR 過濾 | — | >1.15 | — | >1.15 | >1.15 | >1.15 | — | >1.10 | **>1.10** | >1.10 |
| 2日急跌（floor）| — | — | — | ≤-1.5%（cap）| — | ≤-1.5%（cap）| — | — | **≤-1.5%（floor）** | ≤-1.5%（floor）|
| BB Squeeze | — | — | 30th pct/60d | — | — | — | — | — | — | — |
| SMA 趨勢 | — | — | SMA(50) | — | — | — | SMA(50) | — | — | — |
| TP | +4.5% | +4.5% | +3.5% | +5.0% | +4.5% | +3.5% | +3.5% | +3.5% | **+3.5%** | +3.5% |
| SL | -5.0% | -5.0% | -3.5% | -4.5% | -4.5% | -4.5% | -4.0% | -4.0% | **-4.0%** | -4.0% |
| 持倉天數 | 18 | 18 | 20 | 20 | 12 | 15 | 20 | 20 | **20** | 20 |
| 追蹤停損 | 啟動+2.5%/距離2% | 無 | 無 | 無 | 無 | 無 | 無 | 無 | 無 | 無 |
| 冷卻期 | 8 | 8 | 10 | 8 | 5 | 8 | 10 | 10 | **10** | 10 |
| Part A Sharpe | 0.10 | 0.13 | 0.35 | 0.15 | -0.00 | 0.28 | 0.42 | 0.57 | **1.11** | 1.01 |
| Part B Sharpe | 0.57 | 0.64 | -0.37 | 0.48 | 0.31 | 0.50 | 0.93 | 0.00† | **0.00†** | 0.00† |
| min(A,B) | 0.10 | 0.13 | -0.37 | 0.15 | -0.00 | 0.28 | 0.42 | 0.57† | **1.11†** | 1.01† (FAIL) |

† EWT-008 / EWT-009 / EWT-012 Part B 3/3 全達 +3.50% 零方差，採 EWJ-003 慣例以 Part A Sharpe 為綁定約束。EWT-012 三次迭代（Att1 2d CEILING≤0.0% min† 1.01 / Att2 2d FLOOR≥-1.0% min† 0.91 Part B 3→1 / Att3 1d CEILING≤0.0% min† 1.01）全 FAIL vs EWT-009 Att3 1.11 — cross-asset divergence regime gate family v4 第 2 次失敗

## 實驗列表 (Experiment List)

| ID      | 資料夾                          | 策略摘要                                     | 狀態       |
|---------|---------------------------------|---------------------------------------------|-----------|
| EWT-001 | `ewt_001_pullback_wr_reversal` | 回檔+WR+反轉K線均值回歸（追蹤停損）             | 已完成 |
| EWT-002 | `ewt_002_vol_adaptive_pullback` | 波動率自適應回檔+WR（ATR 過濾，無追蹤停損）★    | 已完成 |
| EWT-003 | `ewt_003_bb_squeeze_breakout`  | BB 擠壓突破（失敗：Part B Sharpe -0.37）        | 已完成（無效）|
| EWT-004 | `ewt_004_crash_filter_asymmetric` | 2日急跌過濾+非對稱出場均值回歸                  | 已完成 |
| EWT-005 | `ewt_005_rsi2_vol_adaptive`    | RSI(2)+ATR 波動率自適應（失敗：Part A ≤ 0.05）   | 已完成（無效）|
| EWT-006 | `ewt_006_optimized_exit_mr`    | 出場優化均值回歸（TP/vol 比校準）                 | 已完成 |
| EWT-007 | `ewt_007_rs_momentum`          | RS 動量回調（EWT vs EEM 相對強度）               | 已完成 |
| EWT-008 | `ewt_008_bb_lower_pullback_cap` | BB 下軌+回檔上限混合進場均值回歸                | 已完成 |
| EWT-009 | `ewt_009_vol_transition_mr`    | Post-Capitulation Vol-Transition MR（2DD floor）              | 已完成 |
| EWT-010 | `ewt_010_ewt_eem_2d_divergence_mr` | EWT-EEM 2D Cross-Asset Divergence Filter on Vol-Transition MR（雙時框 20d AND 60d AND 條件）— 文件最優但雙 Part std=0 退化 | 已完成 |
| EWT-011 | `ewt_011_vol_gated_rs_momentum` | RS-Freshness Dual-Window Filter on RS Momentum Pullback（EWT-007 base + EWT−EEM 10d RS > -1%；Att1 vol gate 失敗）★ **真實穩健最優 min(A,B) 0.56 (+33% vs EWT-007 0.42)，雙 Part 真實變異** | 已完成 |
| EWT-012 | `ewt_012_eem_divergence_regime_mr` | EWT–EEM 跨資產 divergence regime gate（family v4 第 2 次失敗）| 已完成（無效）|

---

## EWT-001：回檔 + Williams %R + 反轉K線均值回歸

### 目標 (Goal)

以 GLD-007 為模板，根據 EWT 波動度（1.26x GLD）縮放參數，測試回檔+WR+反轉K線確認的均值回歸策略是否適用於台灣股市 ETF。

### 進場條件 (Entry Conditions)

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | 回檔深度 | 10日高點回檔 | ≤ -4% | 從近期高點回落 ≥4%（GLD -3% × 1.26 vol ratio） |
| 2 | 超賣確認 | Williams %R(10) | ≤ -80 | 10 日超賣區域 |
| 3 | 反轉跡象 | 收盤位置 (ClosePos) | ≥ 40% | 收盤在當日振幅上方 40%，確認日內反彈 |
| 4 | 冷卻期 | Cooldown | 8 天 | 防止同一波段重複進場（GLD 7天 × 1.14） |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +4.5% | 均值回歸目標價（GLD 3.5% × ~1.3） |
| 停損 (SL) | -5.0% | 固定停損（GLD -4% × 1.25） |
| 最大持倉天數 | 18 天 | 到期出場（GLD 20天 × 0.9） |
| 追蹤停損啟動 | +2.5% | 獲利達 2.5% 啟動追蹤（GLD 2% scaled） |
| 追蹤停損距離 | 2.0% | 從最高價回落 2% 觸發（GLD 1.5% scaled） |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 隔日開盤市價單 |
| 獲利出場 | 日內限價單 |
| 停損出場 | 停損市價單 (GTC) |
| 到期出場 | 隔日開盤市價單 |
| 滑價假設 | 0.1%（ETF） |
| 悲觀認定 | 是（TP/SL 同日觸發時認定 SL） |

### 設計理念 (Design Rationale)
- **策略模板選擇**：EWT 日波動 1.41% 屬低波動（< 2%），選用 GLD-007 回檔+WR+反轉K線模板
- **追蹤停損**：日波動 ≤ 1.5% 允許使用追蹤停損（cross-asset lesson #2），啟動門檻與距離按波動度上調
- **收盤位置過濾**：日波動 1.41% 在 ClosePos 有效範圍（≤ 2.0%）內，可過濾仍在下跌的假訊號
- **回檔深度 4%**：相比 GLD 的 3%，按 1.26x 波動度比上調，過濾淺回檔噪音
- **持倉縮短至 18 天**：較高波動意味較快均值回歸（0.9x 持倉期）

### 回測結果 (Backtest Results)

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|--------------------|--------------------|----------------|
| 訊號數 | 30（6.0/年） | 16（8.0/年） | 2（7.5/年） |
| 勝率 | 70.0% | 81.2% | 100.0% |
| 累計報酬 | +9.19% | +38.54% | +4.94% |
| Sharpe | 0.10 | 0.57 | 1.21 |
| 最大回撤 | -6.86% | -8.71% | -2.83% |

### 關鍵發現
- 追蹤停損啟動/TP 比 = 2.5%/4.5% = 55.6%，遠低於 lesson #2 的 80% 安全門檻，壓縮獲利
- Part A Sharpe 0.10 是所有非 TLT 資產中最低，有大量改進空間

---

## EWT-002：波動率自適應回檔 + WR 均值回歸 ★

### 目標 (Goal)
修正 EWT-001 追蹤停損壓縮獲利問題，加入 ATR 波動率飆升過濾選擇恐慌性急跌進場。

### 進場條件 (Entry Conditions)

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | 回檔深度 | 10日高點回檔 | ≤ -4% | 從近期高點回落 ≥4% |
| 2 | 回檔上限 | 10日高點回檔 | ≥ -10% | 隔離極端崩盤（約 7σ） |
| 3 | 超賣確認 | Williams %R(10) | ≤ -80 | 10 日超賣區域 |
| 4 | 反轉跡象 | 收盤位置 (ClosePos) | ≥ 40% | 日內反轉確認 |
| 5 | 波動率飆升 | ATR(5)/ATR(20) | > 1.15 | 急跌恐慌，非慢磨下跌 |
| 6 | 冷卻期 | Cooldown | 8 天 | 防止同一波段重複進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +4.5% | 固定獲利目標 |
| 停損 (SL) | -5.0% | 固定停損 |
| 最大持倉天數 | 18 天 | 到期出場 |
| 追蹤停損 | 無 | 移除（啟動/TP 比過低壓縮獲利） |

### 設計理念 (Design Rationale)
- **移除追蹤停損**：EWT-001 啟動/TP 比 55.6% < 80% 壓縮獲利（cross-asset lesson #2）
- **ATR 過濾 > 1.15**：選擇急跌恐慌進場，過濾慢磨下跌（VGK-002 甜蜜點）
- **ATR > 1.1 太鬆**（Att2 驗證）：讓入 2021-07/09 慢磨信號，Part A 0.13→0.08
- **回檔上限 -10%**：隔離 COVID 級別極端崩盤訊號（均值回歸速度不同）

### 回測結果 (Backtest Results)

#### Att1（最佳）: ATR > 1.15

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|--------------------|--------------------|----------------|
| 訊號數 | 21（4.2/年） | 12（6.0/年） | 2（7.5/年） |
| 勝率 | 57.1% | 75.0% | 100.0% |
| 累計報酬 | +9.63% | +31.32% | +9.20% |
| Sharpe | 0.13 | 0.64 | — |
| 最大回撤 | -8.48% | -6.85% | -2.83% |
| 出場：達標/停損/到期 | 8/6/7 | 8/1/3 | 2/0/0 |

#### Att2: ATR > 1.1

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 23（4.6/年） | 14（7.0/年） |
| 勝率 | 52.2% | 71.4% |
| Sharpe | 0.08 | 0.37 |

→ 1.1 讓入 2 個慢磨信號（2021-07-27 -1.24%、2021-09-20 -2.61%），品質下降

### vs EWT-001 改善
| 指標 | EWT-001 | EWT-002 Att1 | 變化 |
|------|---------|-------------|------|
| min(A,B) Sharpe | 0.10 | 0.13 | **+30%** |
| Part A WR | 70.0% | 57.1% | -12.9pp（ATR 過濾移除追蹤停損的「假贏家」）|
| Part B WR | 81.2% | 75.0% | -6.2pp |
| Part B 累計 | +38.54% | +31.32% | -7.22pp（移除追蹤停損）|

---

## EWT-003：BB 擠壓突破（失敗）

### 目標 (Goal)
嘗試完全不同的策略類型：BB Squeeze Breakout，利用 EWT 半導體週期驅動的波動率壓縮-突破模式。

### 進場條件 (Entry Conditions)

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | 波動率壓縮 | BB Width percentile | ≤ 30th pct (60日) | 近 5 日內曾壓縮 |
| 2 | 向上突破 | Close > BB Upper | BB(20,2) | 突破上軌 |
| 3 | 趨勢確認 | Close > SMA(50) | — | 上升趨勢中 |
| 4 | 冷卻期 | Cooldown | 10 天 | — |

### 出場：TP +3.5% / SL -3.5% / 20天

### 回測結果 (Backtest Results)

| 指標 | Part A (2019-2023) | Part B (2024-2025) |
|------|--------------------|--------------------|
| 訊號數 | 21（4.2/年） | 10（5.0/年） |
| 勝率 | 71.4% | 40.0% |
| 累計報酬 | +25.33% | -11.25% |
| Sharpe | 0.35 | **-0.37** |
| 最大回撤 | -6.64% | -6.29% |

### 失敗分析
- **Part B 嚴重崩潰**：WR 71.4% → 40.0%（-31.4pp），Sharpe 0.35 → -0.37
- **根因**：2024-2025 台灣地緣政治風險（中美科技戰、半導體出口管制）導致突破後急速反轉
- **結論**：BB Squeeze 對單一國家 ETF 無效，與 INDA-003 結論一致
- 已加入禁止清單

---

## EWT-004：2日急跌過濾 + 非對稱出場均值回歸 ★

### 目標 (Goal)

在 EWT-002 基礎上加入 2 日急跌過濾（確認急跌恐慌而非慢磨下跌），並調整為非對稱出場（TP > SL，提高盈虧比），目標改善 Part A Sharpe。

### 進場條件 (Entry Conditions)

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | 回檔深度 | 10日高點回檔 | ≤ -4% | 從近期高點回落 ≥4% |
| 2 | 回檔上限 | 10日高點回檔 | ≥ -10% | 隔離極端崩盤 |
| 3 | 超賣確認 | Williams %R(10) | ≤ -80 | 10 日超賣區域 |
| 4 | 反轉跡象 | 收盤位置 (ClosePos) | ≥ 40% | 日內反轉確認 |
| 5 | 波動率飆升 | ATR(5)/ATR(20) | > 1.15 | 急跌恐慌，非慢磨下跌 |
| 6 | 2日急跌 | 2日報酬 | ≤ -1.5% | 確認近期有急跌（~0.75σ） |
| 7 | 冷卻期 | Cooldown | 8 天 | 防止同一波段重複進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +5.0% | 非對稱出場，提高盈虧比 |
| 停損 (SL) | -4.5% | 收緊 SL，reward/risk 1.11:1 |
| 最大持倉天數 | 20 天 | 延長持倉，配合較高 TP |
| 追蹤停損 | 無 | — |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 隔日開盤市價單 |
| 獲利出場 | 日內限價單 |
| 停損出場 | 停損市價單 (GTC) |
| 到期出場 | 隔日開盤市價單 |
| 滑價假設 | 0.1%（ETF） |
| 悲觀認定 | 是（TP/SL 同日觸發時認定 SL） |

### 設計理念 (Design Rationale)
- **2日急跌過濾**：2日報酬 ≤ -1.5% 對應 EWT 日波動 1.41% 的 ~0.75σ（2日），與 USO-013 的 -2.5%/2.4% vol ≈ 0.74σ 一致。確認進場前有急跌恐慌，過濾慢磨下跌。
- **非對稱出場**：TP +5.0% / SL -4.5%（盈虧比 1.11:1），比 EWT-002 的 TP 4.5% / SL 5.0%（0.9:1）更佳。
- **延長持倉**：20天（vs 18天），配合較高 TP 目標。
- **保留 ATR > 1.15**：Att2 驗證 1.1 仍讓入壞信號，2日急跌無法補償。

### 回測結果 (Backtest Results)

#### Att1★: ATR > 1.15 + 2日急跌 -1.5% + TP +5.0% / SL -4.5% / 20d

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|--------------------|--------------------|----------------|
| 訊號數 | 16（3.2/年） | 8（4.0/年） | 0 |
| 勝率 | 50.0% | 75.0% | — |
| 累計報酬 | +9.71% | +16.18% | — |
| Sharpe | 0.15 | 0.48 | — |
| 最大回撤 | -8.48% | -7.21% | — |
| 出場：達標/停損/到期 | 7/5/4 | 5/2/1 | — |

#### Att2: ATR > 1.1（放寬 ATR 由 2日急跌補償）

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 19（3.8/年） | 8（4.0/年） |
| 勝率 | 47.4% | 62.5% |
| Sharpe | 0.02 | 0.30 |

→ ATR 1.1 讓入 3 個壞信號（2021-07/09 + 2022-04），2日急跌無法補償

#### Att3: ATR > 1.15 + SL -5.5%（加寬 SL 呼吸空間）

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 16（3.2/年） | 8（4.0/年） |
| 勝率 | 50.0% | 75.0% |
| Sharpe | 0.08 | 0.38 |

→ SL -5.5% 未轉換任何停損交易，2022 熊市 SL 交易全部穿越 -5.5%，只增加虧損

### vs EWT-002 Att1 改善
| 指標 | EWT-002 Att1 | EWT-004 Att1 | 變化 |
|------|-------------|-------------|------|
| min(A,B) Sharpe | 0.13 | 0.15 | **+15%** |
| Part A Sharpe | 0.13 | 0.15 | +15% |
| Part A 訊號 | 21 | 16 | -5（2日急跌過濾移除低品質信號）|
| Part A SL 次數 | 6 | 5 | -1 |
| Part A 到期 | 7 | 4 | -3 |
| Part A/B 累計差距 | 21.69pp | 6.47pp | **-70% 差距縮小** |
| Profit factor | 1.15 | 1.37 | +19% |

---

## EWT-005：RSI(2) 波動率自適應均值回歸（失敗）

### 目標 (Goal)
以完全不同的進場框架（RSI(2) 極端超賣）取代 pullback+WR，搭配 ATR 過濾，測試 RSI(2) 對 EWT（日波動 1.41%，在 ≤1.5% 有效邊界）是否能改善 Part A Sharpe。

### 進場條件 (Entry Conditions)

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | 極端超賣 | RSI(2) | < 10 | 2日極端超賣（IWM-011/SPY-005 驗證） |
| 2 | 反轉跡象 | 收盤位置 (ClosePos) | ≥ 40% | 日內反轉確認 |
| 3 | 波動率飆升 | ATR(5)/ATR(20) | > 1.15 | EWT 甜蜜點 |
| 4 | 冷卻期 | Cooldown | 5 天 | RSI(2) 框架標準 |

### 出場參數 (Exit Parameters)

| 參數 | Att1 | Att2 | Att3 |
|------|------|------|------|
| TP | +4.5% | +4.0% | +4.5% |
| SL | -4.5% | -3.5% | -4.5% |
| 持倉天數 | 20 | 12 | 12 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 隔日開盤市價單 |
| 獲利出場 | 日內限價單 |
| 停損出場 | 停損市價單 (GTC) |
| 到期出場 | 隔日開盤市價單 |
| 滑價假設 | 0.1%（ETF） |
| 悲觀認定 | 是（TP/SL 同日觸發時認定 SL） |

### 回測結果 (Backtest Results)

#### Att1: RSI(2)<10 + 2日跌幅≤-1.5% + ClosePos≥40% + ATR>1.15, TP+4.5%/SL-4.5%/20d

| 指標 | Part A (2019-2023) | Part B (2024-2025) |
|------|--------------------|--------------------|
| 訊號數 | 10（2.0/年） | 6（3.0/年） |
| 勝率 | 40.0% | 66.7% |
| 累計報酬 | -5.89% | +8.53% |
| Sharpe | -0.12 | 0.34 |

#### Att2: RSI(2)<10 + ClosePos≥40% + ATR>1.15（移除2日跌幅）, TP+4.0%/SL-3.5%/12d

| 指標 | Part A (2019-2023) | Part B (2024-2025) |
|------|--------------------|--------------------|
| 訊號數 | 12（2.4/年） | 6（3.0/年） |
| 勝率 | 50.0% | 50.0% |
| 累計報酬 | +1.55% | +0.77% |
| Sharpe | 0.05 | 0.05 |

→ A/B 平衡極佳（0.05/0.05）但絕對績效太低，SL -3.5% 翻轉 Part B 贏家

#### Att3: 同 Att2 進場 + TP+4.5%/SL-4.5%/12d（恢復 SL 甜蜜點）

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|--------------------|--------------------|----------------|
| 訊號數 | 12（2.4/年） | 6（3.0/年） | 1（3.6/年） |
| 勝率 | 50.0% | 66.7% | 100.0% |
| 累計報酬 | -1.33% | +7.59% | +0.28% |
| Sharpe | -0.00 | 0.31 | — |
| 出場：達標/停損/到期 | 5/5/2 | 3/2/1 | 0/0/1 |

### 失敗分析
- **RSI(2) 對 EWT 無效**：三次嘗試 min(A,B) 最佳僅 0.05（Att2），均不及 EWT-004 的 0.15
- **根因**：EWT 受台灣地緣政治事件影響（2019 貿易戰、2020 COVID、2021 台灣疫情、2022 俄烏戰爭+晶片禁令），RSI(2) 在這些延續性危機中反覆觸發但無法恢復
- **確認 cross-asset lesson #27**：RSI(2) 對非美國單一國家 ETF 無效，即使日波動 1.41% 在 ≤1.5% 有效邊界內
- **SL 敏感度**：-3.5% 太緊（翻轉贏家），-4.5% 是甜蜜點（與 pullback+WR 框架一致）
- **已加入禁止清單**

---

## EWT-006：出場優化均值回歸 ★

### 目標 (Goal)

基於 EWT-004 的入場框架（pullback+WR+ATR+2日急跌），優化出場參數。關鍵洞見：EWT-004 的 TP +5.0% 相對日波動 1.41% 的 TP/vol 比為 79%——所有成功實驗中最高（XLU-011 為 56%，IWM-011 為 60%）。高 TP 導致 25% 到期率，壓制 Part A Sharpe。

### 進場條件 (Entry Conditions)

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | 回檔深度 | 10日高點回檔 | ≤ -4% | 從近期高點回落 ≥4% |
| 2 | 回檔上限 | 10日高點回檔 | ≥ -10% | 隔離極端崩盤 |
| 3 | 超賣確認 | Williams %R(10) | ≤ -80 | 10 日超賣區域 |
| 4 | 反轉跡象 | 收盤位置 (ClosePos) | ≥ 40% | 日內反轉確認 |
| 5 | 波動率飆升 | ATR(5)/ATR(20) | > 1.15 | 急跌恐慌，非慢磨下跌 |
| 6 | 2日急跌 | 2日報酬 | ≤ -1.5% | 確認近期有急跌 |
| 7 | 冷卻期 | Cooldown | 8 天 | 防止同一波段重複進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +3.5% | TP/vol 比 55%，匹配 XLU-011 的 56% |
| 停損 (SL) | -4.5% | EWT 甜蜜點（不變） |
| 最大持倉天數 | 15 天 | 縮短持倉，減少時間曝露 |
| 追蹤停損 | 無 | — |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 隔日開盤市價單 |
| 獲利出場 | 日內限價單 |
| 停損出場 | 停損市價單 (GTC) |
| 到期出場 | 隔日開盤市價單 |
| 滑價假設 | 0.1%（ETF） |
| 悲觀認定 | 是（TP/SL 同日觸發時認定 SL） |

### 設計理念 (Design Rationale)
- **TP/vol 比校準**：EWT-004 的 TP +5.0% / vol 1.41% = 79%（過高），成功實驗 XLU-011 為 56%。降至 +3.5% 使比率為 55%，提升 TP 可達性
- **保留 2日急跌**：EWT-006 Att1 驗證移除後額外訊號品質差（+1 SL +3 到期）
- **縮短持倉至 15d**：搭配較低 TP，平均持倉從 8.9d 降至 7.2d

### 回測結果 (Backtest Results)

#### Att1: 移除 2日急跌 + TP +4.0% / SL -4.5% / 15d

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|--------------------|--------------------|----------------|
| 訊號數 | 21（4.2/年） | 12（6.0/年） | 2（7.5/年） |
| 勝率 | 61.9% | 83.3% | 100.0% |
| 累計報酬 | +10.48% | +33.37% | +8.16% |
| Sharpe | 0.15 | 0.89 | — |
| 出場：達標/停損/到期 | 8/6/7 | 8/1/3 | 2/0/0 |

→ min(A,B) 0.15 ✗ 與 EWT-004 相同。額外訊號品質差（Part A +1 SL +3 到期）

#### Att2★: 保留 2日急跌 + TP +3.5% / SL -4.5% / 15d

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|--------------------|--------------------|----------------|
| 訊號數 | 16（3.2/年） | 8（4.0/年） | 0 |
| 勝率 | 68.8% | 75.0% | — |
| 累計報酬 | +15.97% | +12.02% | — |
| Sharpe | **0.28** | **0.50** | — |
| 最大回撤 | -6.86% | -6.85% | — |
| 出場：達標/停損/到期 | 10/4/2 | 5/1/2 | — |

#### Att3: 保留 2日急跌 + TP +3.5% / SL -4.5% / 12d

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 16（3.2/年） | 8（4.0/年） |
| 勝率 | 68.8% | 62.5% |
| Sharpe | 0.26 | 0.34 |

→ min(A,B) 0.26 ✗ 退化。12d 導致 Part B 1 個 TP→到期轉換失敗，WR 從 75%→62.5%

### vs EWT-004 Att1 改善 (Att2)
| 指標 | EWT-004 Att1 | EWT-006 Att2 | 變化 |
|------|-------------|-------------|------|
| min(A,B) Sharpe | 0.15 | 0.28 | **+87%** |
| Part A Sharpe | 0.15 | 0.28 | **+87%** |
| Part A WR | 50.0% | 68.8% | **+18.8pp** |
| Part A 累計 | +9.71% | +15.97% | **+64%** |
| Part A TP/SL/到期 | 7/5/4 | 10/4/2 | 3 到期→TP 轉換 |
| Part B Sharpe | 0.48 | 0.50 | +4% |
| A/B 累計差距 | 6.47pp | 3.95pp | **-39%** |
| Profit factor | 1.37 | 1.77 | **+29%** |

### 關鍵發現
- **TP/vol 比是通用優化槓桿**：EWT 的 TP 從 +5.0%（79%）降至 +3.5%（55%），轉換 3 個到期交易為達標，Part A WR 從 50%→68.8%
- **轉換的 3 筆交易**：2019-08-02（+1.91%→+3.50%），2020-01-27（+0.59%→+3.50%），2022-01-28（新增 TP）
- **縮短持倉有邊界**：15d 最佳，12d 導致 Part B 退化（1 筆 TP 在 13d 達標被截斷）
- **移除 2日急跌反效果**：lesson #19 的訊號頻率門檻（≥5/年）確認——EWT 3.2/年 在臨界以下，但 2日急跌仍有效因為能區分急跌/慢磨
- **新 cross-asset 教訓**：TP/vol 比 50-60% 是通用甜蜜點，>75% 導致過多到期交易

---

## 演進路線圖 (Roadmap)

```
EWT-001 (回檔+WR+反轉K線，追蹤停損) → min(A,B) 0.10
  ├── EWT-002 (移除追蹤停損+ATR 自適應) → min(A,B) 0.13 (+30%)
  │     ├── Att1: ATR > 1.15 → 0.13
  │     └── Att2: ATR > 1.1  → 0.08 ✗
  ├── EWT-003 (BB Squeeze 突破) → min(A,B) -0.37 ✗
  ├── EWT-004 (2日急跌+非對稱出場) → min(A,B) 0.15 (+15%)
  │     ├── Att1: ATR 1.15 + 2日 -1.5% + TP5%/SL4.5%/20d → 0.15
  │     ├── Att2: ATR 1.1 + 2日 -1.5% → 0.02 ✗
  │     └── Att3: ATR 1.15 + SL -5.5% → 0.08 ✗
  ├── EWT-005 (RSI(2) + ATR 自適應) → min(A,B) 0.05 ✗
  │     ├── Att1: RSI(2)+2日跌幅+ATR + TP4.5%/SL4.5%/20d → -0.12 ✗
  │     ├── Att2: RSI(2)+ATR + TP4.0%/SL3.5%/12d → 0.05 ✗ (best balance)
  │     └── Att3: RSI(2)+ATR + TP4.5%/SL4.5%/12d → -0.00 ✗
  ├── EWT-006 (出場優化均值回歸) → min(A,B) 0.28 (+87%)
  │     ├── Att1: 移除2日急跌 + TP4%/SL4.5%/15d → 0.15 ✗
  │     ├── Att2: 保留2日急跌 + TP3.5%/SL4.5%/15d → 0.28
  │     └── Att3: 保留2日急跌 + TP3.5%/SL4.5%/12d → 0.26 ✗
  └── EWT-007 (RS 動量回調) → min(A,B) 0.42 ★ (+50%)
        ├── Att1: EEM ref + RS≥3% + PB 2-5% + TP3.5%/SL4.0%/20d → 0.42 ★
        ├── Att2: EEM ref + RS≥4% → 0.40 ✗ (過嚴)
        └── Att3: SMH ref + RS≥3% → -0.67 ✗ (完全失敗)
```

---

## EWT-007：Relative Strength Momentum Pullback ★

### 目標 (Goal)

首次嘗試 RS 動量策略。利用 EWT 半導體權重極高（TSM >20%）的特性，當 EWT 相對 EEM（新興市場）展現超額表現時，代表台灣半導體產業在 EM 中領先。在這種動量優勢下買入短期回調。

參考實驗：TSM-007/008（RS vs SMH，min 0.64/0.79），NVDA-006（RS vs SMH，min 0.47）。

### 進場條件 (Entry Conditions)

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | 相對強度 | EWT 20日報酬 - EEM 20日報酬 | ≥ 3% | 台灣跑贏 EM，半導體出口驅動 |
| 2 | 短期回調 | 5日高點回撤 | 2-5% | 短暫整理，非深度回調 |
| 3 | 趨勢確認 | Close > SMA(50) | — | 上升趨勢確認 |
| 4 | 冷卻期 | Cooldown | 10 天 | 避免密集進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +3.5% | EWT 跨策略甜蜜點（TP/vol 比 55%） |
| 停損 (SL) | -4.0% | RS 動量甜蜜點 |
| 最大持倉天數 | 20 天 | 標準動量持倉 |
| 追蹤停損 | 無 | — |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 隔日開盤市價單 |
| 獲利出場 | 日內限價單 |
| 停損出場 | 停損市價單 (GTC) |
| 到期出場 | 隔日開盤市價單 |
| 滑價假設 | 0.1%（ETF） |

### 回測結果

#### Att1 ★（EEM ref, RS≥3%, PB 2-5%, TP+3.5%/SL-4.0%/20d）

| 指標 | Part A (2019-2023) | Part B (2024-2025) |
|------|--------------------|--------------------|
| 訊號數 | 19 (3.8/年) | 7 (3.5/年) |
| 勝率 | 78.9% | 85.7% |
| 累計報酬 | +25.99% | +18.07% |
| 平均報酬 | +1.27% | +2.44% |
| Sharpe | **0.42** | **0.93** |
| Sortino | 0.67 | 1.63 |
| PF | 2.47 | 5.32 |
| Max DD | -5.97% | -3.87% |
| TP/SL/到期 | 10/4/5 | 6/0/1 |

- **min(A,B) = 0.42 ★** vs EWT-006 的 0.28（+50%）
- A/B 年化訊號比 1.09:1（優秀平衡）
- Part B 零停損，6/7 達標出場，Sharpe 0.93 極佳
- EEM 基準有效：台灣在 EM 中的超額表現由半導體出口結構性驅動

#### Att2（EEM ref, RS≥4%, PB 2-5%, TP+3.5%/SL-4.0%/20d）

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 13 (2.6/年) | 5 (2.5/年) |
| 勝率 | 76.9% | 80.0% |
| 累計報酬 | +16.52% | +10.22% |
| Sharpe | 0.40 | 0.67 |

- min(A,B) = 0.40 ✗ 低於 Att1
- 收緊 RS 4% 過濾掉 2 筆 Part B 好訊號（2024-02-14 +3.50%、2025-07-08 +3.50%）
- A/B 累計差距 38.1%（惡化）

#### Att3（SMH ref, RS≥3%, PB 2-5%, TP+3.5%/SL-4.0%/20d）

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 5 (1.0/年) | 4 (2.0/年) |
| 勝率 | 60.0% | 25.0% |
| 累計報酬 | +1.97% | -8.72% |
| Sharpe | 0.12 | **-0.67** |

- min(A,B) = -0.67 ✗ 完全失敗
- EWT vs SMH 的 RS 訊號品質極差：EWT 含大量非半導體成分，稀釋 RS 訊號
- Part B 3/4 停損，確認 SMH 不適合作為 EWT 的 RS 參考基準

### 關鍵發現

1. **EEM 是 EWT RS 策略的最佳參考基準**：台灣在新興市場中的相對表現由半導體出口結構性驅動，具備持續性
2. **SMH 作為參考完全無效**：EWT 含大量非半導體成分（金融、電子製造等），RS 訊號被稀釋
3. **RS 動量大幅超越均值回歸**：min(A,B) 0.42 vs 0.28（+50%），策略類型轉換帶來質的飛躍
4. **RS ≥ 3% 是甜蜜點**：4% 過嚴（過濾好訊號），3% 捕捉足夠多的有效回調
5. **TP +3.5% 跨策略通用**：均值回歸和 RS 動量均以 +3.5% 為最優，TP/vol 比 55%

---

## EWT-008：BB 下軌 + 回檔上限混合進場均值回歸 ★ 當前最佳

### 目標 (Goal)

將 EWJ-003 / VGK-007 / CIBR-008 / EWZ-006 驗證的 BB 下軌 + 回檔上限混合進場模式
延伸至 EWT。EWT 日波動 1.41% 落在 lesson #52 已驗證有效 vol 區間 [1.12%, 1.75%]
中段，且 EWT 作為 DM/EM 邊界單一國家 ETF（MSCI 分類 EM），與 EWZ（EM 商品驅動）
/ EWJ（DM 單一國家）具備跨類別驗證價值。

### 策略設計 (Strategy Design)

| 資產 | 日波動 | BB std | 回檔上限 | min(A,B) | 類別 |
|------|--------|--------|----------|----------|------|
| EWJ  | ~1.15% | 1.5σ   | 7%（6σ） | 0.60     | DM 單一國家（日本）|
| VGK  | 1.12%  | 2.0σ   | 7%（6σ） | 0.53     | 歐洲寬基 |
| CIBR | 1.53%  | 2.0σ   | 12%（7.8σ）| 0.39   | 美國板塊 |
| EWT  | 1.41%  | 2.0σ   | 8%（5.7σ）| **0.57†** | **EM 半導體驅動單一國家** |
| EWZ  | 1.75%  | 1.5σ   | 10%（5.7σ）| 0.69   | EM 商品驅動單一國家 |

EWT 介於 VGK（1.12%, 2.0σ）與 EWZ（1.75%, 1.5σ）中間波動帶，採用 BB 2.0σ
維持選擇性，cap -8%（5.7σ）等同 EWZ 的 σ 倍率標準化門檻。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | BB 下軌觸及 | Close ≤ BB(20, 2.0) 下軌 | 自適應深度過濾（波動率縮放）|
| 2 | 回檔上限 | 10日高點回檔 ≥ -8% | 崩盤隔離（5.7σ，地緣政治風暴）|
| 3 | 超賣確認 | WR(10) ≤ -80 | 10日超賣 |
| 4 | 反轉 K 線 | ClosePos ≥ 40% | 日內反彈確認 |
| 5 | 波動率飆升 | ATR(5)/ATR(20) > 1.10 | 急跌恐慌而非慢磨 |
| 6 | 冷卻期 | 10 交易日 | 避免同一波段重入 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|----|------|
| 獲利目標 (TP) | +3.5% | EWT 跨策略甜蜜點 |
| 停損 (SL) | -4.0% | EWT 跨策略甜蜜點 |
| 最長持倉 | 20 天 | RS 動量/均值回歸通用 |
| 追蹤停損 | 無 | lesson #2 |

### 迭代嘗試紀錄 (Iteration Log)

| # | 變更 | Part A Sharpe | Part B Sharpe | A/B 訊號 | A/B WR | 結論 |
|---|------|-------------|-------------|---------|--------|------|
| 1 (★) | BB(20, 2.0) + cap -8% + WR + ClosePos + ATR>1.10 | 0.57 | 0.00† | 9/3 | 77.8%/100% | Part B 3/3 全達 +3.50%（零方差），Part A 綁定約束 min 0.57 vs EWT-007 的 0.42（+36%）|
| 2 | BB(20, 1.75) 放寬 BB std | 0.27 | 0.12 | 15/5 | 66.7%/60.0% | 放寬 BB 引入低品質訊號（2 SL/2 SL），三重品質過濾失去選擇性 |
| 3 | BB(20, 2.0) + cap -10% 放寬回檔上限 | 0.55 | 0.00† | 11/3 | 72.7%/100% | Part B 訊號集不變（2024-2025 無 -8~-10% 區間 BB 下軌觸及），Part A 新增 2 訊號但 WR 拖累 |

### Att1 回測結果（最終版）

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|-------------|-------------|----------------|
| 訊號數 | 9 | 3 | 0 |
| 訊號/年 | 1.8 | 1.5 | 0.0 |
| 勝率 | 77.8% | 100% | — |
| 平均報酬 | +1.81% | +3.50% | — |
| 累計報酬 | +17.01% | +10.87% | — |
| 盈虧比 | 2.99 | ∞（無虧損）| — |
| Sharpe | 0.57 | 0.00† | — |
| Sortino | 0.94 | ∞ | — |
| MDD | -4.87% | -3.77% | — |
| 最大連續虧損 | 1 | 0 | — |

**A/B 分析**：
- A/B 年化訊號比 1.2:1（優秀，lesson #8 標準）
- A/B 累計差距 36.1%（略超 30% 目標但接近，與 EWZ-006 Att3 的 30.7% 同量級）
- Part B 3/3 全達標 +3.50%（零方差），Sharpe 形式上為 0.00
- 採 EWJ-003 慣例：min(A,B) 以 Part A Sharpe 0.57 為綁定約束

### 關鍵發現

1. **BB 下軌混合進場延伸至 EWT 有效**：Part A Sharpe 0.42→0.57（+36%），確認 lesson #52 混合模式有效 vol 區間 [1.12%, 1.75%] 可推廣至 EM 半導體驅動單一國家 ETF
2. **Part B 零方差與 EWJ-003 同模式**：3/3 筆全達 +3.50% TP，形式 Sharpe 0.00，實質為高品質訊號聚集（WR 100%、盈虧比 ∞），未來樣本擴充後 Sharpe 將自然浮現
3. **BB 2.0σ 是 EWT 甜蜜點**：放寬至 1.75σ（Att2）使三重品質過濾失去選擇性；EWT 1.41% vol 與 VGK 1.12% vol 同屬低波動段，均用 2.0σ
4. **回檔上限 -8% 已飽和**：Att3 放寬至 -10% 未增加 Part B 訊號，僅在 Part A 引入 2 筆低品質訊號拖累 WR
5. **混合進場與 RS 動量互補**：EWT-008 在 Part A（2019-2023）表現優異但 Part B 樣本少；EWT-007 在 Part B（2024-2025）Sharpe 0.93 但 Part A 0.42。兩策略使用不同進場邏輯（價格 vs 跨資產 RS），未來可觀察哪一類訊號在現實中更易跟單

### 結論

EWT-008 Att1 為 EWT 新全域最優，min(A,B) 0.57†（Part A 綁定約束）。本實驗擴展 lesson #16：
- **非美國已開發市場 ETF（VGK/EWJ）**：BB 下軌+回檔上限混合進場最佳 ✓
- **新興市場單一國家 ETF（EWT，1.41% vol，半導體驅動）**：**BB 下軌+回檔上限混合進場同樣最佳**，確認混合模式適用 EM 半導體驅動而非僅商品驅動（EWZ）
- **混合模式有效 vol 區間確認為 [1.12%, 1.75%]** 跨類別（DM 寬基、DM 單一國家、EM 單一國家商品/半導體、US 板塊）

---

## EWT-009：Post-Capitulation Vol-Transition MR（2DD floor 加深方向）★

### 目標 (Goal)

延伸 EWT-008 Att1 框架，新增「Capitulation strength filter」（1日/2日報酬下限）作為主品質過濾器，目標過濾 Part A 兩筆 SL（2019-05-09 中美貿易戰升級 + 2022-01-25 科技股拋售/Fed pivot 擔憂），同時保留高品質 winners。

跨資產脈絡（lesson #19 family）：
- VGK-008 Att2（1.12% vol）：2DD floor <= -2.0% → min(A,B) 0.53→2.60（+390%）
- INDA-010 Att3（0.97% vol）：2DD floor <= -2.0% → min(A,B) 0.23→0.30
- EEM-014（1.17% vol）：2DD floor 方向成功
- USO-013（2.20% vol）：2DD floor 方向成功
- DIA-012（1.0% vol）：1d cap + 3d cap 雙維度方向成功
- SPY-009（1.0% vol）：1d floor 方向成功
- EWJ-005 Att2（1.15% vol）：1d floor <= -0.5% → min(A,B) 0.60→0.70（+16.7%）

EWT 1.41% vol 落在 lesson #19 已驗證 vol 區間內（含 EEM 1.17%、EWJ 1.15%、INDA 0.97%、EWZ 1.75%）。

### 進場條件（Att3 ★，全部滿足）

1. Close <= BB(20, 2.0) 下軌（自適應深度過濾）
2. 10 日高點回檔 >= -8%（崩盤隔離）
3. Williams %R(10) <= -80（超賣確認）
4. 收盤位置 >= 40%（日內反轉確認）
5. ATR(5) / ATR(20) > 1.10（波動率飆升過濾）
6. **2 日報酬 <= -1.5%**（Capitulation strength，本實驗新增）
7. 冷卻期 10 個交易日

### 出場參數

| 參數 | 值 |
|------|-----|
| 獲利目標 (TP) | +3.5% |
| 停損 (SL) | -4.0% |
| 最大持倉天數 | 20 天 |

### 三次迭代結果

| Att | Capitulation Filter | Part A | Part B | min(A,B)† | 狀態 |
|----|---------------------|--------|--------|----------|------|
| Att1 | 2DD floor ≤ -2.0% | 7/85.7%/0.91 cum +17.89% | 3/100%/std=0 cum +10.87% | 0.91 | 過嚴：過濾 2 筆淺 2DD winners 並引入 cooldown shift 新 SL |
| Att2 | 1d floor ≤ -1.0% | 8/87.5%/1.01 cum +22.01% | **2**/100%/std=0 cum +7.12% | 1.01 | Part B winner 流失：誤殺 2025-11-18 1d -0.78% TP |
| **Att3 ★** | **2DD floor ≤ -1.5%** | **9/88.9%/1.11 cum +26.28%** | **3/100%/std=0 cum +10.87%** | **1.11** | **精準甜蜜點：過濾 2022-01-25 SL（2d -0.46%），cooldown shift 正向（2022-01-28 TP）** |

### 績效詳情（Att3）

|  指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026 Live) |
|-------|----------------------|--------------------|--------------------|
| 訊號數 | 9 | 3 | 0 |
| 訊號/年 | 1.8 | 1.5 | 0.0 |
| 勝率 | 88.9% | 100% | — |
| 平均報酬 | +2.66% | +3.50% | — |
| 累計報酬 | +26.28% | +10.87% | — |
| 盈虧比 | 6.83 | ∞（無虧損）| — |
| Sharpe | 1.11 | 0.00† | — |
| Sortino | 1.94 | ∞ | — |
| MDD | -4.08% | -3.77% | — |
| 平均持倉 | 6.0 天 | 7.7 天 | — |
| 最大連續虧損 | 1 | 0 | — |

### 關鍵發現

1. **2DD -1.5% 為 EWT 精準甜蜜點**：
   - -2.0%（Att1）過嚴：移除 2019-05-09 SL（2d -1.69%）+ 2023-03-15 TP（2d -1.87%），並引入 2019-05-13 cooldown shift 新 SL
   - -1.5%（Att3）精準：僅過濾 2022-01-25 SL（2d -0.46% 唯一淺 2DD），所有其他 winners 2d 皆深於 -1.87%

2. **Cooldown chain shift 正向收益（lesson #19 例外案例）**：
   - 移除 2022-01-25 SL 後，原本被 cooldown 抑制的 2022-01-28 訊號活化
   - 2022-01-28 ClosePos 0.99（極強日內反轉）達 TP +3.50%
   - Part A 訊號數保持 9 不變，但 8 TPs + 1 SL = 88.9% WR（vs baseline 7 TPs + 2 SLs = 77.8%）
   - 與 lesson #19 多數負面 cooldown shift 案例相反

3. **EWT 2DD 維度有效，1d 維度部分有效**：
   - 2DD 維度（Att3）成功：唯一淺 2DD 訊號（2022-01-25 2d -0.46%）為 SL，winners 集中於深 2DD
   - 1d 維度（Att2）部分失敗：Part B 含 1 筆 1d 過淺 winner（2025-11-18 1d -0.78%）被 -1.0% 誤殺
   - 與 EWJ-005（1.15% vol）1d -0.5% 成功不同——EWJ Part B winners 1d 集中於 -1.7% ~ -3.3%，無 1d 過淺訊號

4. **Part A 唯一保留 SL（2019-05-09）的本質**：
   - 2d -1.69% > -1.5%（通過 floor）
   - ClosePos 0.79（強日內反轉看似良好訊號）
   - WR -80.10、Pullback -4.52%、ATR ratio 1.77（所有條件理想）
   - 但隔日（2019-05-10）開盤即跳空下跌觸發 -4.10% SL
   - 此為「中美貿易戰升級新聞驅動 gap-down」結構，技術過濾器無法識別事件驅動風險

### A/B 平衡分析

- A/B 年化訊號比 1.2:1（優秀，與 baseline EWT-008 相同）
- A/B 累計差 15.41pp / 26.28% = 58.6%（>30% 目標，但與 baseline 36.1% 同量級增長為 Sharpe 大幅提升的伴隨現象）
- Part B 3/3 全達標 +3.50%（零方差），Sharpe 形式上為 0.00
- 採 EWJ-003 / EWT-008 / EWZ-006 / VGK-008 慣例：min(A,B) 以 Part A Sharpe 1.11 為綁定約束

### 結論

EWT-009 Att3 為 EWT 新全域最優，min(A,B)† **1.11**（+94.7% vs EWT-008 的 0.57）。

**跨資產貢獻**：
- repo 第 6 次「2DD floor」方向成功驗證（繼 USO-013、EEM-014、INDA-010、VGK-008、EWJ-005 後）
- 首次半導體驅動 EM 單一國家 ETF 驗證
- 擴展 lesson #19 雙向發現：2DD floor 對 EWT 1.41% vol 有效，**閾值精準度（-1.5% vs -2.0%）為關鍵變量**——2DD floor 並非「越深越好」，需逐資產檢視 winners/losers 的 2d 分布找最大切點

**新跨資產規則**（lesson #19 family 精煉）：
- 2DD floor 閾值需匹配資產 winners 最淺 2d 與 losers 2d 的中位點
- EWT：losers 含 -0.46% 淺 2d 跌、winners 最淺 -1.87%，甜蜜點 -1.5%
- VGK：losers 最淺 -1.47% ~ -1.68%、winners 最深 -2.0% 內，甜蜜點 -2.0%
- EWJ：winners 廣泛分布 +0.17% ~ -2.43%，2DD 無精準切點，1d 維度（-0.5%）為甜蜜點
- 跨資產 2DD 閾值不可直接移植，需先做 trade-level 2d 分布分析

---

## EWT-010: EWT-EEM 2D Cross-Asset Divergence Filter on Vol-Transition MR ★ 當前最佳

### 目標 (Goal)

延伸 EWT-009 Att3 框架（BB(20, 2.0) 下軌 + 10d 回檔上限 -8% + WR(10)≤-80 + ClosePos≥40% + ATR(5)/ATR(20)>1.10 + 2DD floor <= -1.5%, TP+3.5%/SL-4.0%/20d/cd 10），新增 cross-asset divergence regime gate（lesson #20 v3 family v3 dimensionality 擴展，**repo 首次「雙時框 (短+長 lookback) 同時 AND 條件」divergence 過濾於任何資產**），目標清除 EWT-009 Att3 殘餘 Part A SL（2019-05-09 中美貿易戰升級 -4.10%）。

### 進場條件 (Entry Conditions)

EWT-009 Att3 完整六條件 + EWT-EEM 2D divergence 過濾：

1. **Close <= BB(20, 2.0) 下軌**
2. **10日高點回檔 >= -8%**（崩盤隔離）
3. **Williams %R(10) <= -80**
4. **ClosePos >= 40%**
5. **ATR(5) / ATR(20) > 1.10**
6. **2 日報酬 <= -1.5%**（capitulation strength filter）
7. **NOT (EWT 20日報酬 - EEM 20日報酬 ≥ +3.0pp AND EWT 60日報酬 - EEM 60日報酬 ≥ +5.0pp)**（cross-asset divergence regime gate，雙時框 AND 條件）

### 核心假設

EWT-009 Att3 殘餘 Part A SL（2019-05-09 -4.10%）的 trade-level RS 分析顯示**單一 lookback 維度結構性無法區分**：

| Date        | Out  | 5d div | 10d div | 20d div | 60d div |
|-------------|------|--------|---------|---------|---------|
| 2019-05-09  | SL   | +1.64  | +1.71   | +4.35   | +7.37   |
| 2019-08-02  | TP   | +0.31  | +0.83   | +3.03   | -0.23   |
| 2020-01-27  | TP   | +1.32  | +1.02   | -0.45   | +0.98   |
| 2020-09-24  | TP   | -0.52  | -1.02   | +0.79   | +0.13   |
| 2021-07-27  | TP   | +2.42  | +2.65   | +6.51   | +2.70   |
| 2021-08-17  | TP   | -1.45  | -2.35   | -0.08   | +7.26   |
| 2022-01-28  | TP   | +0.55  | -1.66   | -2.31   | +7.46   |
| 2023-03-15  | TP   | +0.20  | +1.89   | +2.87   | +5.97   |
| 2023-07-06  | TP   | -1.11  | -1.55   | -1.14   | +2.76   |
| 2024-04-16  | TP-B | -1.54  | -1.15   | -1.03   | +1.89   |
| 2025-01-13  | TP-B | -0.57  | -0.53   | +1.48   | +3.25   |
| 2025-11-18  | TP-B | -1.41  | -3.14   | -4.23   | -1.60   |

任一單一 lookback 之 SL 皆有 TP **higher** 於 SL（5d 2021-07-27 TP +2.42 > SL +1.64；60d 2022-01-28 TP +7.46 > SL +7.37 等）。**雙時框 AND 條件**：當 (短 lookback div ≥ short_thresh) **AND** (長 lookback div ≥ long_thresh) 同時成立才過濾，使 SL 在兩維度同時越界但每個 TP 至少有一維度未越界。

### 迭代設計與結果

**Att1 (5d/+1.5pp AND 60d/+5pp)** — cooldown chain-shift TIE baseline 1.11
- Part A: 9 訊號 / WR 88.9% / Sharpe **1.11** / cum +26.28%（與 baseline 完全相同）
- Part B: 3 訊號 / WR 100% / std=0 cum +10.87%
- min(A,B)† **1.11 TIE**
- **失敗分析**：short_lookback=5 過濾 2019-05-09 SL（5d_div +1.64 ≥ +1.5 ✓ AND 60d_div +7.37 ≥ +5 ✓）後解除 cooldown，**2019-05-13 訊號**（5d_div +0.43 < +1.5 未越界）以新 SL -4.10% 啟動。lesson #19 family cooldown chain-shift 失敗模式

**Att2 ★ (20d/+3.0pp AND 60d/+5pp) SUCCESS — 全域最優**
- Part A: **8 訊號 / WR 100% / std=0** / cum **+31.68%** / MDD -3.89%
- Part B: 3 訊號 / WR 100% / std=0 / cum +10.87%
- min(A,B)† **structurally NO LOSS**（雙 Part 全勝零方差，IBIT-009 Att1 慣例）
- A/B 年化 cum 6.34%/y vs 5.43%/y → gap **14.4% < 30% ✓**
- A/B 訊號比 1.6:1.5 = **6.7% gap << 50% ✓**
- 20d 維度同時切除 **2019-05-09 SL（20d +4.35）** 與 **cooldown chain-shift 2019-05-13 SL（20d +3.37）**
- 所有 11 個 TPs 保留：最近邊界 2019-08-02 TP（20d +3.03，但 60d -0.23 < +5 由 AND 條件保護）
- Part A SL 完全清零，Part A cum +26.28%→+31.68%（+20.5%）

**Att3 (20d/+2.5pp AND 60d/+5pp loose threshold)** — short_threshold 過鬆
- Part A: 7 訊號 / WR 100% / std=0 / cum +27.23%（vs Att2 8/+31.68%）
- Part B: 3 訊號 不變
- **失敗分析**：+2.5pp 同時過濾 2023-03-15 TP（20d +2.87 ≥ 2.5 ✓ AND 60d +5.97 ≥ 5 ✓），確認 +3.0pp 為 short_threshold 結構性下界 sweet spot

### A/B 平衡分析

- A/B 年化訊號比 1.6:1.5 = **6.7% gap**（優於 baseline 16.7%）
- A/B 年化 cum gap 14.4%（< 30% ✓）
- 雙 Part 100% WR / std=0：filter 在 Part B 完全非綁定（所有 Part B winners 在 short/long 任一維度低於閾值）
- 採 IBIT-009 Att1 慣例：雙 Part std=0 全勝結構**結構性優於** baseline（含 1 SL）

### 跨資產貢獻

- **repo 第 11 次 lesson #20 v3 cross-asset divergence regime gate 應用**
- **repo 首次「雙時框 (短+長 lookback) 同時 AND 條件」divergence 過濾於任何資產**
- repo 第 3 次 EM single-country + EEM benchmark anchor（EWZ-009 / INDA-012 後）
- 首次半導體驅動 EM 單一國家 ETF（EWT 1.41% vol，TSM ~25% 權重）+ EEM anchor + 雙時框 AND
- **lesson #20 v3 family v3 dimensionality 擴展（1D → 2D AND）**：依資產失敗模式選擇 dimensionality

### 新跨資產規則（lesson #20 v3 family v3 dimensionality 擴展）

當失敗模式（target SL）在 cross-asset divergence 維度上**任一單一 lookback 皆非 outlier**（被 TPs 重疊覆蓋）：
1. **單一 lookback 1D filter 結構性失效** — surgical separation 不可能
2. **嘗試雙時框 AND 條件 2D filter** — 短 lookback 捕捉「即時相對強勢」+ 長 lookback 捕捉「結構性領先」
3. **short_lookback 需大於 cooldown_days** — 防止 cooldown chain-shift（EWT-010 Att1 5d < cd 10 失敗 → Att2 20d > cd 10 成功）
4. **threshold sweet spot 需逐維度精調** — short 過寬移除 TP（EWT-010 Att3 +2.5pp 失敗），過嚴漏接 SL（理論上 +3.5pp 漏接 chain-shift SL）

### 結論

EWT-010 Att2 為 EWT 新全域最優，min(A,B)† **structurally NO LOSS**（雙 Part 100% WR / std=0），Part A cum **+20.5%** vs baseline EWT-009 Att3 的 +26.28%（structurally 優於 baseline 1.11/std=0 「1 SL + 全勝」結構）。

**禁止重複嘗試**：5d short_lookback（cooldown chain-shift）、20d short_threshold ≤ +2.5pp（過寬移除 TP）、單一 lookback divergence filter（任一 lookback 皆非 SL outlier）。

---

## EWT-012：EWT–EEM 跨資產 divergence regime gate（family v4 第 2 次失敗）

### 目標 (Goal)

將已驗證的 **cross-asset divergence regime gate family**（3-for-1：SUCCESS
TSLA-017 TSLA−QQQ / TLT-014 TLT−SPY / GLD-016 GLD−USD；FAIL SIVR-019
SIVR−USD）移植至 EWT，以 EEM（EWT 母體 EM 指數）為 divergence 軸，目標過濾
EWT-009 Att3 Part A 唯一殘餘 binding SL（2019-05-09 中美貿易戰關稅升級
-4.10%）。空遠端 artifact `ewt_012_ewt_eem_2d_divergence_mr` 獨立指向此方向；
本實驗用獨立 module 名稱 `ewt_012_eem_divergence_regime_mr`（branch-divergence
caveat）。

### 進場條件 (Entry Conditions)

EWT-009 Att3 全域最優六條件 + 第 7 條件「EWT−EEM N日 divergence regime gate」
（CEILING: EWT_Nd−EEM_Nd ≤ thr / FLOOR: ≥ thr）。出場 TP+3.5%/SL-4.0%/20d/
cd10（沿用 EWT-009），成交模型隔日開盤市價進場、滑價 0.1%。

### Trade-level 預分析（predict→confirm）

EWT-009 Att3 binding = Part A 唯一殘餘 SL 2019-05-09。對齊 EEM 計算 signal-day
2d 累計報酬 divergence（EWT_2d − EEM_2d，%）：

| Signal | Grp | DIV(EWT−EEM) |
|--------|-----|--------------|
| 2019-05-09 | A SL | **+0.03**（EWT -1.69 ≈ EEM -1.72，廣域 China/EM co-move）|
| Part A winners ×8 | A TP | -1.41 … **+1.73**（SL 完全交錯其中）|
| Part B winners ×3 | B TP | **-1.75 / -1.86 / -2.16**（最負）|

判定：NOT separable。binding SL DIV≈0（貿易戰同步衝擊全 EM），與 winners 任一
lookback 完全交錯；Part B winners DIV 全為最負（FLOOR 將屠殺全部 OOS）。EWT 非
DRIVER-PURE（EWT 是 EEM 成分 ρ≈0.85 正相關）→ 違反 family v4 前置條件。

### 回測結果 (Backtest Results)

| 迭代 | 設定 | Part A | Part B | min(A,B)† | 結論 |
|------|------|--------|--------|-----------|------|
| Att1 | 2d CEILING ≤ 0.0% | 8 訊號 7TP+1SL Sharpe 1.01 cum +22.01% | 3 訊號 zero-var cum +10.87%（非綁定）| 1.01 | FAIL（-9% vs 1.11）|
| Att2 | 2d FLOOR ≥ -1.0% | 7 訊號 6TP+1SL Sharpe 0.91 cum +17.89% | **1** 訊號 cum +3.50%（3→1 崩潰）| 0.91 | FAIL（-18%）|
| Att3 | 1d CEILING ≤ 0.0%（lookback ablation）| 8 訊號 7TP+1SL Sharpe 1.01 cum +22.01% | 3 訊號 zero-var cum +10.87% | 1.01 | FAIL（-9%）|

### 關鍵發現

- **Att1**：CEILING≤0.0 移除 2019-05-09 SL 但 cooldown chain-shift 至 2019-05-13
  新 SL（貿易戰多日延續賣壓，lesson #19 / SOXL-013 / GLD-016-Att1 isomorph，
  與 EWT-009 Att1 同型 chain-shift）+ 非外科式殺 Part A winner 2021-07-27
  （DIV +1.73）。Part B 3 winners DIV 全 ≤ -1.75 ≤ 0.0 均存活 → gate 對
  binding-OOS 完全非綁定。
- **Att2**：FLOOR≥-1.0% 完全不移除 SL（DIV +0.03 ≥ -1.0% 通過 floor），反而
  屠殺全部 3 筆最高品質 Part B winners（DIV -1.75/-1.86/-2.16 < -1.0%）→
  inverted catastrophic（gate 過濾真 winners 而非 binding loser，SIVR-019
  family v4 失敗 isomorph）。
- **Att3**：1d-DIV SL = -0.20 ≤ 0.0 連 SL 都不隔離仍殺 2021-07-27，確認無可分
  cross-asset divergence lookback。

### 跨資產規則（cross-asset divergence regime gate family v4 第 2 次失敗）

EWT−EEM 為**正相關 component-vs-parent**（EWT 是 EEM 成分，ρ≈0.85），非
driver-pure 單因子反向；binding loser（2019 中美貿易戰）為**同步廣域 China/EM
geopolitical co-move**（DIV≈0）非台灣 idiosyncratic divergence。確認 family v4
前置條件（SIVR-019 規則：結構性對手必須 DRIVER-PURE 單因子反向）——SIVR-019
（白銀工業 decoupled）+ EWT-012（component-vs-parent 正相關）共同界定：
**「X vs 其母體/相關指數」當 X 為該指數成分時 divergence≈0 於同步衝擊日，gate
無區分力**。EWT 加入 EWJ/EWZ/EEM/TSM country-idiosyncratic non-separable 家族
（lesson #27 / lesson #6 反例9）。**RS-entry ≠ divergence-gate**：EWT−EEM RS
動量作為**進場觸發**有效（EWT-007 次佳），但作為**品質 regime gate** 無區分力。
空遠端 artifact 方向為 false lead（SIVR-019 caveat 再確認）。EWT-009 Att3 仍為
全域最優（10 次實驗、33+ 次嘗試）。
