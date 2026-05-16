<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-05-16
  data_through: 2025-12-31
  note_2026_05_16: TSM-012 added 2026-05-16 (^VXN Forward-Looking Implied-Vol DIRECTION Regime-Gated RS Momentum Pullback, **repo 首次 ^VXN 應用於任何資產 + repo 首次 lesson #24 family 移植至 RS 動量框架 + repo 首次半導體 ADR forward-looking implied vol regime gate — 3 iterations all FAILED**, cross-asset/cross-strategy port from XLU-013 / USO-025 / GLD-015 lesson #24 patterns). Base = TSM-011 Att3 完整框架 (TSM-SMH 20d RS>=5% + 5d pullback 3-7% + Close>SMA50 + 5d ret ceiling +10.5%, TP+8%/SL-7%/25d/cd10) + ^VXN N 日變化 DIRECTION gate。目標：外科式移除 binding Part B 2 個殘餘 SL（2024-07-16 / 2024-10-30）。**事前 23 維 trade-level pre-analysis**（10+ signal-day return：1d/2d/3d/5d/10d/RS/RS5/PB5/ATRratio/DistSMA50；5 sector-health：SMH vs SMA50/SMA20、SMH R20、SMH DD20、SMH SMA slope；8 forward-looking：^VXN & ^VIX level + 3d/5d/10d change）**已證明所有維度皆無法分隔 Part B 2 殘餘 SL 與 8 winners**——2024-07-16（July tech-rotation top，signal-day UP、R10 +7.96）與 2024-10-30（Oct multi-day decline，R3 -4.40）signal-day 簽名相反且與 winners 完全交錯，^VXN 3d/5d/10d change 皆近零（quiet/neutral vol regime）。三次迭代回測實證確認預測：Att1 (^VXN 5d change <= +1.0) Part A 12→8/87.5%/Sharpe 1.00 cum +48.52% / Part B (binding) 10→8/75.0%/Sharpe **0.64** cum +36.84% / min(A,B) **0.64** REJECT（-23% vs 0.83，移除 winners 非 SL，Part B WR 80%→75%）；Att2 (^VXN 3d change <= +0.5) Part A 12→6/66.7%/0.35 / Part B 10→7/57.1%/Sharpe **0.20** cum +8.94% / min **0.20** REJECT（-76%，三次最差之一，短視窗收緊大量誤殺 mild-vol-uptick winners）；Att3 (^VXN 10d change <= +2.0) Part A 12→11/81.8%/0.78 / Part B 10→7/**42.9%**/Sharpe **-0.09** cum **-6.33%** / min **-0.09** REJECT（Part B 崩潰至負——10d/+2.0 移除 5 個 VXN10d > +2.0 winners 同時 2 SL 部分倖存）。**核心發現（lesson #24 v6 條件 (c) 跨資產擴展至半導體 ADR）**：(1) **^VXN forward-looking implied vol DIRECTION gate 在 TSM 結構性失效**——TSM binding Part B 殘餘 SL 為 Taiwan-China geopolitical / 客戶集中度 idiosyncratic（非 vol-regime-driven），發生於 quiet ^VXN regime，與 winners 在所有 ^VXN 視窗交錯，無 single separator；(2) **加入 lesson #24 v6 條件 (c) country/event-idiosyncratic 失敗家族**：TSM（Taiwan ADR 地緣政治）與 EWJ（BoJ/yen-carry）、EWZ（Petrobras）、EEM 同類——residual binding SL 必須 vol-regime-separable 方適用 forward-looking implied vol gate，否則結構性失效；(3) **與 TSM-010（lesson #22 失敗）、TSM-009（pairs 失敗）一致**：TSM multi-driver 結構使所有 regime-classifier 類過濾器（technical regime gate / cross-asset divergence / forward-looking implied vol）皆缺乏選擇性；(4) **跨策略邊界**：lesson #24 family（MR 框架 5+ 次成功 TLT/XLU/GLD/USO/FCX/XBI）移植至 RS 動量框架本身非問題所在，問題在 TSM 殘餘 SL 的 idiosyncratic 本質。TSM-011 Att3（min 0.83）仍為全域最優（12 次實驗、36+ 次嘗試）。
  note_2026_05_02: TSM-011 added 2026-05-02 (Signal-Day Direction Filter on RS Momentum Pullback, **repo 首次「return CEILING（rally exhaustion filter）」於任何資產 + repo 首次 lesson #19 family cross-strategy 鏡像擴展（MR floor → momentum ceiling）**, applied to TSM-008 RS framework). Three iterations: Att1 (1d ceiling <= +1.0%) FAILED — Part A 12/75.0%/Sharpe **0.78** cum +68.73% / Part B unchanged / min 0.78 — 1d 過濾觸發 cooldown chain shift 將 2020-07-24 expiry -1.72% 替換為 2020-07-31 expiry -2.22%（更差），淨效果負面；Att2 (5d ceiling <= +9.5%) Part A 11/90.9%/Sharpe **1.30** cum **+87.38%** / Part B 10/80%/Sharpe 0.83 不變 cum +59.78% / min(A,B) **0.83** (+5% vs 0.79) — 顯著 Part A 改善但 A/B 累計差 31.6% **略超 30% 目標**（cooldown chain shift 移除 2022-11-21 SL 與 2022-12-07 SL，僅留 2022-11-28 SL）；Att3 ★ (5d ceiling <= +10.5%) Part A 12 訊號 WR **83.3%** Sharpe **0.86** cum **+74.10%** / Part B 10/80%/Sharpe 0.83 不變 cum +59.78% / min(A,B) **0.83** (+5% vs TSM-008 baseline 0.79) / A/B 累計差 **19.3%** (< 30% ✓) / A/B 訊號比 1.2:1 (gap 16.7% < 50% ✓) — **acceptance criteria 全部達標**。關鍵改善：5d ceiling +10.5% 僅過濾 2020-07-24 訊號（5d +11.30%, expiry -1.72%），cooldown chain shift 引入 2020-07-31 expiry +0.89%（從負轉正）+ 2020-08-20 TP +8%；Part B 完全不受影響（最高 5d 為 2024-02-12 +9.82% < +10.5%）。**核心發現（lesson #19 family v10）**：(1) **Repo 首次「return CEILING（rally exhaustion filter）」於任何資產**——既往 lesson #19 family 全部為 FLOOR 方向（capitulation depth filter，DIA-012/SPY-009/EWJ-005/EWZ-007/CIBR-014/SIVR-018/URA-013/INDA-011/GLD-014），TSM-011 開啟鏡像 CEILING 方向；(2) **Repo 首次 cross-strategy lesson #19 移植**：MR 框架 → RS momentum 框架（lesson #21 family），與既往 lesson #19 全部於 MR 框架平行；(3) **MR 失敗模式（太淺 capitulation）vs momentum 失敗模式（太深 rally）為結構性鏡像**——TSM Part A 2020-07-24 expiry 與 2022-11-21 SL 均屬「5 日大漲後淺回檔但實為趨勢反轉前兆」（Att2 確認 9.79 SL 與 9.82 TP 邊界精準 < 0.05 percentage points 區分，Att3 採取保守 +10.5% 邊界僅清除最極端 +11.30 case）；(4) **5d > 1d ceiling 區分力**——signal-day 1d 過濾因 cooldown chain shift 反向（Att1）而 5d 過濾因 2020-07-24 受 prior 5d 大漲驅動（5d +11.30 vs 1d +9.69 同向 signal）使 5d 為較穩健 rally exhaustion proxy。**新跨資產假設（待驗證）**：rally exhaustion 5d ceiling 可能適用於其他 RS / MBPC 動量框架（NVDA-006 RS / TSM-007 RS / VOO-004 MBPC / SOXL-010 RS 等），閾值需依資產 5d return 分布調整（TSM 甜蜜點 +10.5%，其他資產需 trade-level 分析）。TSM-011 Att3 為新全域最優（11 次實驗、33+ 次嘗試）。
  note: TSM-010 added 2026-04-30 (Multi-Week Regime-Aware Momentum Breakout Pullback Continuation, **repo 第 2 次 lesson #22 + MBPC 試驗、首次半導體 cross-asset NVDA→TSM 移植**, cross-asset port from NVDA-013 Att3). Three iterations all FAILED vs TSM-008 min 0.79: Att1 (NVDA-013 Att3 直接移植：k=1.00 + ATR ≤ 1.40 + recency 10d + pullback [-3%,-8%]) Part A 19/47.4%/Sharpe **0.03** cum -0.06% / Part B 12/58.3%/Sharpe **0.23** cum +18.33% / min **0.03** — TSM Part A 8 SLs 散佈於多 regime（trade war / pre-COVID / 2021-02 / 2022-08/12 / 2023-03/07），SMA regime + ATR vol 雙 gate 對 TSM SLs 缺乏選擇性，因 SLs 多發生於 SMA20/SMA60 仍 > 1.00 的「短暫地緣政治震盪」期間；Att2 (VOO-004 Att3 方向：recency 5d + pullback [-2%,-5%] 收緊) Part A 13/46.2%/Sharpe **-0.10** cum -11.10% / Part B 5/60%/Sharpe **0.26** cum +8.62% / min **-0.10** — 收緊進場後 WR 幾乎不變（47.4%→46.2%）顯示為**非選擇性過濾**，與 VOO 上 tight→loose 反向（VOO 0.12→1.12，TSM 0.00→-0.38）；Att3 (恢復 NVDA-013 預設 + 2DD cap >= -2%，lesson #19 cap 方向) Part A 14/50%/Sharpe **0.08** cum +4.75% / Part B 12（不變）/ min **0.08** — 2DD cap 過濾 5 訊號，cooldown chain shift 將 2020-09-17 SL 釋放為 2020-09-21 TP（正向 chain shift），但仍 7 SLs 殘留（2DD 維度淺）。**核心跨資產發現**：(1) **lesson #21 失敗家族擴展至 TSM 半導體 cross-asset**：NVDA-013 ★（單一 AI secular driver）→ TSM-010 ✗（multi-driver: 中國地緣政治 + 半導體景氣週期 + 客戶集中度），半導體個股 lesson #22 + MBPC 跨資產移植**結構性失敗**；(2) **新規則候選**：lesson #22 + MBPC 適用於「single-secular-driver 高波動個股」，**不適用於多重結構性驅動的個股**（TSM 為首例 multi-driver 失敗）；(3) **進場敏感度方向取決於資產 regime 結構**（lesson #4 邊界擴展）：VOO single uptrend 中 tight 捕捉高品質訊號；TSM multi-regime 中 tight 反而捕捉「短暫 regime 突破假動量」訊號；(4) **lesson #19 family 邊界擴展（2DD cap on MBPC）**：MR 框架（DIA-012/CIBR-012/USO-023）2DD cap 顯著有效；MBPC 框架選擇力受限，因 MBPC 進場本質為「shallow pullback」signal day 2DD 集中淺帶。**TSM 第 10 次實驗、30+ 次嘗試**，TSM-008 RS framework 仍為全域最優，TSM-010 確認「TSM 最佳訊號為 TSM/SMH RS spread」（cross-sectional 機制天然消化半導體週期 effect）。
-->
## AI Agent 快速索引

**當前最佳：** ★ **TSM-011 Att3**（Signal-Day Direction Filter on RS Momentum Pullback：TSM-008 完整框架 + **5 日報酬 ceiling <= +10.5%** rally exhaustion filter，TP+8%/SL-7%/25天/cd 10）★ **2026-05-02 全域最優，TSM-012 ^VXN gate 三次迭代失敗後仍保持（12 次實驗、36+ 次嘗試）**
- Part A: Sharpe **0.86**, 累計 +74.10%, 12 訊號 (2.4/年), WR **83.3%**, MDD -7.89%
- Part B: Sharpe 0.83, 累計 +59.78%, 10 訊號 (5.0/年), WR 80.0%（與 TSM-008 baseline 完全相同）
- min(A,B) **0.83**（+5% vs TSM-008 baseline 0.79）
- A/B 累計差 **19.3%**（< 30% ✓，vs baseline 14.1% 略增），A/B 訊號比 1.2:1（gap 16.7% < 50% ✓）
- 關鍵改善：5d ceiling +10.5% 僅過濾 2020-07-24 訊號（5d +11.30%，原為 expiry -1.72%），cooldown chain shift 引入 2020-07-31 expiry +0.89%（從負轉正）+ 2020-08-20 TP +8%；Part B 訊號完全不受影響
- **跨資產貢獻**：repo 首次「return CEILING（rally exhaustion filter）」方向於任何資產 + repo 首次 lesson #19 family cross-strategy 鏡像擴展（MR floor → momentum ceiling）

**最新失敗實驗：** TSM-012（^VXN forward-looking implied-vol DIRECTION regime gate on TSM-011 Att3 RS 動量框架，**repo 首次 ^VXN / 首次 lesson #24 移植至 RS 動量框架 / 首次半導體 ADR**，三次迭代全部失敗 min(A,B) 0.64 / 0.20 / -0.09 vs TSM-011 Att3 baseline 0.83）— 確認 **lesson #24 v6 條件 (c)**：TSM binding Part B 2 殘餘 SL（2024-07-16 July tech-rotation top / 2024-10-30 Oct multi-day decline）為 Taiwan-China geopolitical / 客戶集中度 idiosyncratic，發生於 quiet ^VXN regime，與 8 winners 在 ^VXN 所有視窗交錯，**非 vol-regime-separable**；TSM 加入 EWJ/EWZ/EEM country-idiosyncratic 失敗家族。事前 23 維 trade-level pre-analysis 已預測，3 次回測實證確認。

**前任最佳：** TSM-008（RS 出場優化：同 TSM-007 進場，TP+8%/SL-7%/25天）— Part A Sharpe 0.79/Part B 0.83，min(A,B) 0.79，A/B 訊號數 12/10，A/B gap 0.04（極佳平衡）

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
- 出場條件：TP+10%/SL-12%/25天、TP+7%/SL-7%/20天、TP+7%/SL-6%/20天、TP±5%/15天、TP±6%/15天、TP+8%/SL-7%/20天、TP+8%/SL-8%/25天、TP+8%/SL-8%/20天、TP+7%/SL-7%/25天、TP+8%/SL-7%/25天、TP+7.5%/SL-7%/25天
- 冷卻期：7天、10天、15天、20天

**尚未嘗試的方向（可探索，但預期邊際效益低）：**
- 地緣政治風險過濾（如台海緊張相關波動）
- 成交量異常濾波（放量確認恐慌賣出）

**已排除的方向：**
- **配對交易（TSM/NVDA z-score 均值回歸）**：TSM-009 三次嘗試全部失敗（最佳 min(A,B) 0.40 vs TSM-008 0.79）。TSM/NVDA 價格比值存在結構性漂移（NVDA AI 驅動成長），z-score 均值回歸假設不成立，與 SIVR/GLD、COPX/FCX 配對交易失敗模式一致
- **Multi-Week Regime-Aware MBPC（lesson #22 + MBPC，NVDA-013 cross-asset 移植）**：TSM-010 三次嘗試全部失敗（Att1 0.03 / Att2 -0.10 / Att3 0.08）vs TSM-008 0.79。NVDA→TSM **半導體 cross-asset 移植結構性失敗**：TSM 為 multi-driver（中國地緣政治 + 半導體景氣週期 + 客戶集中度）vs NVDA single-secular AI driver，lesson #22 SMA + ATR vol 雙 regime gate **缺乏選擇性**（TSM Part A SLs 多發生於 regime 仍正常的「短暫地緣政治震盪」期間）。確認 lesson #22 + MBPC 適用邊界為「single-secular-driver 高波動個股」
- **^VXN forward-looking implied-vol DIRECTION regime gate（lesson #24 family）**：TSM-012 三次嘗試全部失敗（Att1 5d/+1.0 min 0.64 / Att2 3d/+0.5 min 0.20 / Att3 10d/+2.0 min -0.09 vs TSM-011 Att3 0.83）。**repo 首次 ^VXN / 首次 lesson #24 移植至 RS 動量框架 / 首次半導體 ADR**。事前 23 維 trade-level pre-analysis（signal-day return + sector-health + ^VXN/^VIX direction）已證明 binding Part B 2 殘餘 SL（2024-07-16 July tech-rotation top、2024-10-30 Oct multi-day decline）signal-day 簽名相反、^VXN 3d/5d/10d change 皆近零（quiet vol regime）、與 8 winners 在所有維度交錯——**非 vol-regime-separable**。確認 **lesson #24 v6 條件 (c)**：forward-looking implied vol gate 對 country/event-idiosyncratic 殘餘 binding SL 結構性失效（TSM Taiwan-China geopolitical / 客戶集中度，加入 EWJ/EWZ/EEM 失敗家族）
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
- **lesson #22 + MBPC 不適用**：TSM-010 驗證 NVDA-013 cross-asset 移植在半導體個股 NVDA→TSM **結構性失敗**（三次嘗試最佳 0.08 vs TSM-008 0.79）。TSM multi-driver 結構（中國地緣政治 + 半導體景氣 + 客戶集中度）使 lesson #22 SMA regime + ATR vol regime 對 Part A SLs 缺乏選擇性。**已確認 TSM-008 為全域最優**（10 次實驗、30+ 次嘗試，含均值回歸、突破、動量回調、相對強度、配對交易、lesson #22 MBPC 七大策略類型）
- **forward-looking implied vol（^VXN）不適用**：TSM-012 驗證 lesson #24 family（^VXN N 日變化 DIRECTION gate）在 TSM RS 動量框架上三次迭代全部失敗（0.64 / 0.20 / -0.09 vs TSM-011 Att3 0.83）。TSM binding Part B 殘餘 SL 為 Taiwan-China geopolitical / 客戶集中度 idiosyncratic（發生於 quiet ^VXN regime），非 vol-regime-separable。確認 **lesson #24 v6 條件 (c)**：residual binding SL 必須 vol-regime-separable，country/event-idiosyncratic 資產（TSM/EWJ/EWZ/EEM）forward-looking implied vol gate 結構性失效。**TSM-011 Att3 仍為全域最優**（12 次實驗、36+ 次嘗試，新增 forward-looking implied vol 第八大策略類型失敗）
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
| TSM-012 | `tsm_012_vxn_implied_vol_rs`    | ^VXN forward-looking implied-vol DIRECTION gate on RS（lesson #24 family，3次迭代均失敗 0.64/0.20/-0.09） | 失敗 |

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

## TSM-012：^VXN Forward-Looking Implied-Vol DIRECTION Regime Gate（3 次迭代均失敗）

**2026-05-16。** repo 首次 ^VXN 應用於任何資產、首次 lesson #24 family 移植至 RS 動量框架（既往 5+ 次成功 TLT/XLU/GLD/USO/FCX/XBI 全於 MR 框架）、首次半導體 ADR forward-looking implied vol regime gate。

**設計**：TSM-011 Att3 完整框架 + ^VXN N 日變化 DIRECTION gate（`VXN_Change <= vxn_change_max`），目標外科式移除 binding Part B 2 個殘餘 SL（2024-07-16、2024-10-30）。

**事前 23 維 trade-level pre-analysis**（10+ signal-day return：1d/2d/3d/5d/10d/RS/RS5/PB5/ATRratio/DistSMA50；5 sector-health：SMH vs SMA50/SMA20、SMH R20、SMH DD20、SMH SMA slope；8 forward-looking：^VXN & ^VIX level + 3d/5d/10d change）證明**所有維度皆無法分隔 Part B 2 殘餘 SL 與 8 winners**：2024-07-16（July 2024 tech-rotation top，signal-day R1 +0.44 UP day、R10 +7.96）與 2024-10-30（Oct multi-day decline，R3 -4.40）signal-day 簽名相反；二者 ^VXN 3d/5d/10d change 皆近零（quiet/neutral vol regime），與 winners 完全交錯。

**三次迭代回測實證確認預測**：

| Att | ^VXN gate | Part A | Part B (binding) | min(A,B) | 判定 |
|-----|-----------|--------|------------------|----------|------|
| 1 | 5d change <= +1.0 | 12→8 / 87.5% / 1.00 / +48.52% | 10→8 / 75.0% / **0.64** / +36.84% | **0.64** | REJECT -23% |
| 2 | 3d change <= +0.5 | 12→6 / 66.7% / 0.35 / +12.47% | 10→7 / 57.1% / **0.20** / +8.94% | **0.20** | REJECT -76% |
| 3 | 10d change <= +2.0 | 12→11 / 81.8% / 0.78 / +60.87% | 10→7 / **42.9%** / **-0.09** / **-6.33%** | **-0.09** | REJECT（Part B 崩潰至負） |

**核心發現（lesson #24 v6 條件 (c) 跨資產擴展至半導體 ADR）**：

1. **^VXN forward-looking implied vol DIRECTION gate 在 TSM 結構性失效**——TSM binding Part B 殘餘 SL 為 Taiwan-China geopolitical / 客戶集中度 idiosyncratic（非 vol-regime-driven），發生於 quiet ^VXN regime，與 winners 在所有 ^VXN 視窗交錯，無 single separator；任何閾值/視窗皆非外科式（移除 winners 多於 SL，或保留 SL 移除 winners）。
2. **加入 lesson #24 v6 條件 (c) country/event-idiosyncratic 失敗家族**：TSM（Taiwan ADR 地緣政治）與 EWJ（BoJ/yen-carry）、EWZ（Petrobras）、EEM 同類——residual binding SL 必須 **vol-regime-separable** 方適用 forward-looking implied vol gate，否則結構性失效。
3. **與 TSM-009（pairs）、TSM-010（lesson #22 MBPC）一致**：TSM multi-driver 結構（中國地緣政治 + 半導體景氣週期 + 客戶集中度）使所有 regime-classifier 類過濾器（technical regime gate / cross-asset divergence / forward-looking implied vol）皆缺乏選擇性。TSM 累計八大策略類型失敗。
4. **跨策略邊界澄清**：lesson #24 family 移植至 RS 動量框架本身非問題所在（既往於 MR 框架成功多次），問題在 **TSM 殘餘 SL 的 idiosyncratic 本質** —— 與框架類型無關。

**結論**：TSM-011 Att3（min 0.83）仍為全域最優（12 次實驗、36+ 次嘗試）。TSM 純技術面/regime-classifier 路徑已窮盡（八大策略類型）；若要突破 0.83 需 event-driven 結構建模（地緣政治事件日曆、客戶 earnings 事件窗口），非單一 signal-day / regime-gate 維度可達。
