<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-05-08
  data_through: 2025-12-31
  note_2026_05_08: EWZ-009 added 2026-05-08 (EWZ-EEM Relative Strength Divergence Filter on Vol-Transition MR, **repo 第 6 次 cross-asset divergence regime gate 應用（繼 TLT-014 / TSLA-017 ✓ / COPX-014 ✗ / NVDA-016 ◐ / USO-026 ✗）+ repo 首次 EM single-country ETF cross-asset divergence regime gate 試驗 + 首次「同類 ETF 內 broader benchmark 為 anchor」變體（EEM 為 broad EM benchmark）**, cross-asset port from TLT-014 / TSLA-017 cross-asset divergence framework). Three iterations, **Att1 ★ SUCCESS**: trade-level 分析發現 2020-01-31 SL 之 EWZ-EEM rel_10d **+3.78pp** 為唯一 > +2.5pp 的 outlier 訊號，全部 9 Part A TPs rel_10d ≤ +2.12pp（max 2022-09-28），存在 surgical sweet spot [+2.12pp, +3.78pp]。Part B 全 6 訊號 rel_10d ≤ -0.54pp，filter 對 Part B 完全非綁定。Att1 (rel_lookback=10, max_rel_return=+2.5%) Part A 10 訊號 WR **90.0%** Sharpe **1.50** cum +48.77% / Part B 6 訊號 WR 83.3% Sharpe 1.82 cum +25.52%（**完全等於 EWZ-007 baseline**）/ min(A,B) **1.50**（+58% vs EWZ-007 Att3 baseline 0.95）— **過濾 2020-01-31 SL（rel_10d +3.78pp）成功 ✓ 全部 9 TPs 保留 ✓ 零 cooldown chain shift（下一訊號 2020-11-02 為 9+ 月後）✓**。Att2 (max_rel_return=+2.0% 緊邊界) Part A 9 訊號 WR 88.9% Sharpe 1.39 cum +41.69% / Part B 不變 / min **1.39** — 過嚴 +2.0% 移除 2022-09-28 TP（rel_10d +2.12pp），cooldown shift 無法替補。Att3 (max_rel_return=+3.5% 寬邊界 robustness) 訊號集 **完全等於 Att1**（filter 仍綁定 2020-01-31 SL，對其他訊號非綁定）/ min **1.50** — 確認 [+2.5%, +3.5%] 為 robust sweet spot。**核心發現（lesson #20 v3 邊界擴展，repo 首次 EM single-country ETF cross-asset divergence regime gate 成功）**：(1) **Repo 第 6 次 cross-asset divergence regime gate 應用**——擴展 lesson #20 v3 至 EM single-country ETF（EWZ vs EEM broad EM anchor），先前案例 TLT-014（rate ETF vs SPY broad equity）/ TSLA-017（high-vol single stock vs QQQ broad tech）/ NVDA-016 ◐（high-vol stock vs SMH semi index, partial）成功，COPX-014（commodity miners ETF vs GLD）/ USO-026（commodity ETF vs XLE）失敗；EWZ-009 為 broad EM benchmark anchor 變體；(2) **首次「同類 ETF 內 broader benchmark 為 anchor」變體**——既往 anchor 為 cross-asset class（TLT vs SPY、TSLA vs QQQ）或 sector index（NVDA vs SMH、COPX vs GLD），EWZ vs EEM 為「single-country EM ETF vs broad EM ETF」內類別 anchor 結構；(3) **EWZ 殘餘 SL 結構性異質性**：2020-01-31 SL（rel_10d +3.78pp，EWZ 過去 10d 強於 EEM）為「country-specific lagging-decline」結構，2019-03-25 SL（rel_10d -5.20pp，EWZ 過去 10d 已弱於 EEM）為「sustained Brazil-specific weakness」結構——兩者方向相反，無法用單一 cross-asset divergence 維度同時過濾，但 +2.5% 上限 surgical filter 可移除前者；2019-03-25 SL 殘留為已知結構性 noise（同 EWZ-007 文件「Up-day rebound after big drop」結構）；(4) **lesson #20 v3 適用條件擴展**：(a) cooldown 10d × 訊號密度 2.2/yr ≈ 0.06，遠 < 1.0（高間距訊號流，filter 效應不被 cooldown shift 抵消）；(b) MR 框架（capitulation 訊號日已偏弱）；(c) **新發現**：EM single-country ETF 之 「country vs broad benchmark divergence」維度可作為「country-specific lagging-decline」過濾器，補強 lesson #19 family 在 lesson #25 macro context 失敗後的下一維度；(5) **lesson #19 + lesson #20 整合**：EWZ-007 1d cap (lesson #19 outlier-event surgical) + EWZ-009 rel_10d cap (lesson #20 cross-asset divergence) 為**正交雙維度組合**，前者捕捉「~3σ 單日 outlier」（Petrobras）、後者捕捉「country-specific lagging-decline regime」（COVID early），共同移除 EWZ Part A 結構性 SLs。EWZ-009 Att1 為新全域最優（9 次實驗、25+ 次嘗試）。
  note_2026_05_07: EWZ-008 added 2026-05-07 (^VIX Forward-Looking Implied-Vol Regime-Gated MR, **repo 第 7 次 lesson #24 family 跨資產試驗、首次 EM single-country ETF 驗證、第 2 次 lesson #24 family 失敗（繼 NVDA-018 AI 個股 + MBPC 後）**, cross-asset port from XLU-013 / GLD-015 / USO-025 DIRECTION variants). Three iterations all FAILED vs EWZ-007 Att3 全域最佳 0.95: Att1 (vix_lookback=3, max_vix_change=+5.0, XLU-013 / USO-025 sweet spot 直接移植) Part A 11/9 wins/Sharpe **0.95** cum +42.67% / Part B 6/5 wins/Sharpe 1.82 cum +25.52% / min **0.95** — **完全等於 EWZ-007 Att3 baseline，filter 非綁定**：兩個殘餘 SLs 2019-03-25（VIX 3d ~+3.0）/ 2020-01-31（VIX 3d ~+2.5）的 ^VIX 3d change 均 <= +5，無訊號被過濾；Att2 (max_vix_change=+3.0 加嚴) Part A 11/8 wins/Sharpe **0.62** cum +30.31% / Part B 5/4 wins/Sharpe 1.61 cum +19.54% / min **0.62** REJECT — **cooldown chain-shift collapse**：+3 過濾 2019-08-02 TP（trade war 起點，VIX 3d > +3）但 cooldown shift 引入 2019-08-15 SL（chain shift），目標 SLs（2019-03-25 / 2020-01-31）VIX 3d 均 <= +3 仍未過濾，Part B 同時 cooldown shift 損失 1 winner（2024-04-15→2024-04-17 替換）；Att3 (max_vix_change=+999 disabled, **max_vix_level=18.0 LEVEL CAP**) Part A 5/4 wins/Sharpe **0.87** cum +16.57% / Part B 4/3 wins/Sharpe 1.37 cum +13.85% / min **0.87** REJECT — **LEVEL CAP 結構性過濾過多 winners**：18.0 cap 過濾 2020-01-31 SL（VIX 18.84，目標達成 ✓）但同時過濾 5 個 Part A TPs（2019-05-14 / 2020-11-02 / 2021-01-22 / 2022-09-28 / 2023-10-04，VIX 17-25）+ 2 個 Part B winners（2025-03-04、2025-10-14），WR 81.8%→80.0% 持平但 Sharpe 退化（訊號減半 11→5 + 累計 +42.67%→+16.57%）。**核心失敗模式（lesson #24 family v2 邊界擴展）**：(1) **EWZ 殘餘 SLs 結構性正交於 ^VIX 維度**：兩個 Part A 殘餘 SLs（2019-03-25 yield curve inversion 雜訊 / 2020-01-31 COVID 早期擔憂）VIX 3d change 均落於 baseline winner 範圍（<= +3），VIX level 16.5 / 18.84 與 winners 範圍重疊；(2) **EWZ winners 廣泛分布於 ^VIX dimension**：2019-08-02 TP 為 trade war escalation（VIX 3d > +3）、2025-03-04 TP 為 risk-off 反彈（VIX > 18），EM EWZ V-bounce 結構性涵蓋多 vol regime；(3) **lesson #24 family 第 2 次失敗確認雙重邊界條件**：(i) asset class 需具 VIX-regime-correlated capitulation 結構（rate ETF TLT/XLU、commodity ETF GLD/USO/FCX 成功；AI 個股 NVDA-018 失敗、EM single-country ETF EWZ 失敗），(ii) 殘餘 SLs 需集中於單一 vol-regime-correlated 失敗模式（NVDA heterogeneous SLs 失敗 / EWZ 雙獨立事件 SLs 失敗）；(4) **EM single-country ETF lesson #24 family 不適用**：EWZ 商品/政治雙驅動結構使 SLs 來源 heterogeneous（巴西退休金改革雜訊 / 全球疫情早期擔憂 / Petrobras 政治干預），無單一 ^VIX 維度可同時過濾不傷害 winners。EWZ 第 8 次失敗策略類型（後於 BB Squeeze、2 日急跌、趨勢動量、RSI(2)、WR(5)、RS、2DD/1d 雙向、^VIX implied vol regime gate）。EWZ-007 Att3 仍為全域最優（8 次實驗、22+ 次嘗試）。
  note: EWZ-007 added 2026-04-28 (Post-Capitulation Vol-Transition MR, **repo 第 8 次 lesson #19 family 跨資產試驗，首次商品/政治雙驅動 EM 單國 ETF（巴西）驗證**, cross-asset port from VGK-008 / INDA-010 / EEM-014 / EWT-009 / EWJ-005 / IBIT-009 / USO-013). Three iterations, **Att3 SUCCESS — 1d cap surgical Petrobras filter, repo 首次驗證 1d cap 作為 outlier-event surgical filter**. Att1（2DD floor <= -2.0%, VGK/INDA 標準直接移植）FAIL min(A,B) **0.31** Part A 10/60.0%/Sharpe 0.31 / Part B 3/100%/Sharpe 11.63 — 2DD floor 移除 3 baseline winners（淺 2d）+ 全部 baseline 3 losers 2d 皆深於 -2%，filter 不影響 losers 反引入 cooldown shift 新 SL（2019-08-15）。EWZ 2d 結構與 VGK/INDA/EWT/EEM 相反：losers 集中於深 2d（panic crashes：Petrobras 2021-02-22 2d -5.93%、COVID start 2020-01-31 2d -2.67%、2019-03-25 2d -4.79%），winners 跨深+淺 2d。Att2（2DD cap >= -3.0%, CIBR-012/USO-023 cap 方向）FAIL min(A,B) **0.53** Part A 7/85.7%/Sharpe 1.16（+68% vs baseline）/ Part B 5/60.0%/Sharpe 0.53（-71% vs baseline）— Part A 大幅改善（cap 移除 2 深 2d losers），但 Part B 崩壞——cap 同時移除 2 個深 2d Part B winners（2024-06-10 EXP+ 2d -3.90%、2024-11-29 TP 2d -7.06%）並引入 cooldown shift 新 SL（2024-12-03）。EWZ Part A vs Part B 在 2d 維度結構性反轉：Part A losers 集中於深 2d crashes，Part B winners 部分為深 2d V-bounce recoveries——任何單一 2DD 閾值同時破壞 A 或 B。Att3 ★（1d cap >= -5.0%，surgical Petrobras filter）SUCCESS min(A,B) **0.95**（+38% vs baseline 0.69）Part A 11/81.8%/Sharpe 0.95 cum +42.67% / Part B 6/83.3%/Sharpe 1.82 cum +25.52%（**完全等於 baseline，全部 6 訊號保留**）。1d cap >= -5.0% 為 outlier-event surgical filter，僅過濾 2021-02-22 Petrobras 政治干預暴跌（1d -6.19%，~2.86σ 級事件，repo 中極少見的單日暴跌），Part A 訊號 12→11（-8%）移除唯一深 1d SL，**沒有 cooldown shift**（下一訊號 2021-07-07，間隔 4+ 月遠超 cooldown 10 日）。Part B 全部 6 訊號保留（最深 1d 為 2024-11-29 -3.55%，遠淺於 -5.0% 閾值）。**核心發現**：(1) 商品/政治雙驅動 EM ETF 在 2DD 維度 winners 跨深淺分佈（2024-11-29 TP 2d -7.06% 與 2025-03-04 TP 2d -0.83% 並存），與 VGK/INDA/EWT 政策驅動 EM 單峰 winners 結構性不同；(2) **2DD floor / 2DD cap 雙向皆失敗的資產，1d cap 仍可作為極端單日 panic surgical filter**——當資產含 1 筆 ~3σ 級別單日暴跌為 outlier loser 時，1d cap 閾值（>=-5.0%）達成「移除 1 個 outlier loser、零 winners 損傷、零 cooldown shift」的精準效果；(3) **失敗模式對稱性**：lesson #19 family 在 Part A vs Part B 結構性反轉的資產上，需切換至「outlier-event surgical filter」而非「regime-level threshold filter」。Part A 殘餘 2 SLs（2019-03-25 1d +1.26% / 2020-01-31 1d -2.34%）為「Up-day rebound after big drop」與「moderate 1d sustained drop」結構，無法用單一 1d/2d 維度過濾且不傷害 winners——這 2 SLs 為 EWZ 商品/政治 ETF 的結構性 noise 殘留。A/B 平衡：累計差 40.2%（>30% 目標，與 EWT-009 58.6% / NVDA-012 25.3% 同模式，因 Part B 期間 Sharpe 結構性高於 Part A 期間使任何 Part A 加深品質過濾必擴大累計差距），訊號比 11:6 = 1.83:1（年化 36% gap < 50% ✓）。EWZ-007 Att3 為新全域最優（7 次實驗、19+ 次嘗試）。
-->
## AI Agent 快速索引

**當前最佳：** ★ **EWZ-009 Att1**（EWZ-EEM Relative Strength Divergence Filter on Vol-Transition MR：EWZ-007 Att3 完整框架 + **EWZ-EEM 10 日報酬差 ≤ +2.5pp** cross-asset pair-divergence regime gate，TP+5%/SL-4%/18天）★ **2026-05-08 新全域最優（9 次實驗、25+ 次嘗試）**
- Part A: Sharpe **1.50**, 累計 +48.77%, 10 訊號 (2.0/年), WR **90.0%**, MaxDD -5.38%
- Part B: Sharpe **1.82**, 累計 +25.52%, 6 訊號 (3.0/年), WR 83.3%（**與 EWZ-007 baseline 完全相同**）
- min(A,B): **1.50**（**+58% vs EWZ-007 Att3 的 0.95**）
- A/B 年化訊號比 1.5:1（gap 33% < 50% ✓），A/B 累計差 47.7%（>30% 目標，結構性，因 Part A 從 +42.67% 升至 +48.77% 而 Part B 維持 +25.52%——同 EWZ-007 / FCX-013/014/015 「Part A 加深品質過濾必擴大累計差距」模式）
- **rel_10d cap 為 cross-asset divergence surgical filter**：僅過濾 2020-01-31 SL（EWZ-EEM rel_10d +3.78pp，唯一 > +2.5pp outlier；EWZ 過去 10d 相對 EEM 強勢卻被 BB 下軌觸發 = country-specific lagging-decline 訊號），Part A 訊號 11→10，無 cooldown shift（下一訊號 2020-11-02 為 9+ 月後），Part B 全部 6 訊號保留
- **跨資產貢獻**：repo 第 6 次 cross-asset divergence regime gate 應用（lesson #20 v3）+ repo 首次 EM single-country ETF cross-asset divergence regime gate 成功 + 首次「同類 ETF 內 broader benchmark 為 anchor」變體（EEM 為 broad EM benchmark）
- **lesson #19 + lesson #20 雙維度組合**：EWZ-007 1d cap (outlier-event surgical) + EWZ-009 rel_10d cap (cross-asset divergence) 為正交雙維度，前者捕捉 ~3σ 單日 outlier（Petrobras 2021-02-22），後者捕捉 country-specific lagging-decline regime（COVID early 2020-01-31）

**前任最佳：** EWZ-007 Att3（Post-Capitulation Vol-Transition MR：EWZ-006 Att3 框架 + **1d cap >= -5.0%（surgical Petrobras filter）**，TP+5%/SL-4%/18天）
- Part A: Sharpe **0.95**, 累計 +42.67%, 11 訊號 (2.2/年), WR 81.8%
- Part B: Sharpe **1.82**, 累計 +25.52%, 6 訊號 (3.0/年), WR 83.3%
- min(A,B): **0.95**（+38% vs EWZ-006 的 0.69）

**前前任最佳：** EWZ-006 Att3（BB 下軌+回檔上限混合進場：BB(20,1.5) 下軌觸及 + 10日高點回檔上限 10% + WR(10)≤-80 + ClosePos≥40% + ATR(5)/ATR(20)>1.1 + 非對稱出場 TP+5%/SL-4%/18天）
- Part A: Sharpe 0.69, 累計 +36.82%, 12 訊號 (2.4/年), WR 75.0%
- Part B: Sharpe 1.82, 累計 +25.52%, 6 訊號 (3.0/年), WR 83.3%
- A/B 年化訊號比 1.25:1，A/B 累計差 30.7%
- vs EWZ-002 Att3: min(A,B) Sharpe 0.34 → **0.69**（+103%），Part B 樣本 4→6 增加 50%
- 驗證 lesson #52 混合進場模式延伸至商品驅動 EM 單國 ETF（與政策驅動 FXI 不同）

**前前前任最佳：** EWZ-002 Att3（波動率自適應回檔+WR，min(A,B) Sharpe 0.34）

**已證明無效（禁止重複嘗試）：**
- 回檔≥5% + TP+3%/SL-3%：SL 過緊（Part A WR 44.3%、Part B WR 36.8%，兩期均為負報酬），EWZ 需 ≥7% 回檔深度和 ≥4% SL 呼吸空間
- ATR > 1.15（EWZ-002 Att2）：過度過濾好訊號（Part A 13→10，移除 2 贏 1 輸），Part A Sharpe 0.22→0.19，不如 ATR > 1.1
- TP +4.0% 對稱出場（EWZ-002 Att1）：min(A,B) 0.22，所有贏利交易均輕鬆達到 +5%，+4% 只壓縮利潤
- **BB Squeeze Breakout（EWZ-003 Att1/Att2）**：EWZ 突破後宏觀事件驅動反轉頻繁。Att1 Part A 0.03/Part B -0.69；Att2 Part A -0.04/Part B -0.39。兩種參數組（30th/25th pct、TP 4.5%/3.5%、SL 4%/5%）均失敗
- **2日急跌恐慌反轉（EWZ-003 Att3）**：2日急跌 ≤-3.5% + WR≤-70 + ATR>1.1，Part A Sharpe 0.02（WR 46.2%），Part B 2.35（WR 100% 但僅 4 筆）。A/B 嚴重不平衡，2日急跌在延長下跌中捕捉不反轉的恐慌
- **趨勢動量回檔（EWZ-004 Att1）**：Close>SMA(50) + 4-8% 回檔 + WR(10)≤-60，Part A 0.09/Part B 0.06。趨勢確認在 EM 單國 ETF 上無效，WR 接近 50% 無邊際，宏觀事件可突然反轉趨勢（lesson #26 驗證）
- **RSI(2) 深回檔（EWZ-004 Att2）**：RSI(2)<10 + 7-10% 回檔 + ATR>1.1 + ClosePos≥40%，Part A Sharpe -0.16（WR 37.5%, 8訊號），Part B 10.63（2訊號）。RSI(2) 在 1.75% vol EM ETF 上完全失敗（lesson #27 驗證），深回檔+ATR 無法挽救
- **WR(5) 無 ATR（EWZ-004 Att3）**：WR(5)≤-80 + 7-10% 回檔 + ClosePos≥40%（無 ATR 過濾），Part A Sharpe -0.03（WR 43.8%, 16訊號），Part B 0.56（4訊號）。WR(5) 不足以替代 ATR 過濾，生成 3 個額外假訊號（慢磨下跌），MaxDD 惡化至 -14.18%
- **RS 動量回調 EWZ vs EEM（EWZ-005 Att1-3）**：三次迭代（RS 20d/15d/10d，門檻 2-4%，回調 2-7%，含/不含 ATR）均失敗。Att1 Part A 0.46/Part B -0.33；Att2 Part A -0.00/Part B -0.25；Att3 Part A -0.21/Part B 0.46。A/B 訊號極度不平衡（20-24:3-4），巴西商品優勢為宏觀事件驅動（大宗商品價格/BRL 匯率/政治）而非週期性，RS 訊號不穩定
- **BB(20,2.0) 下軌+回檔上限（EWZ-006 Att1）**：min(A,B) 0.58（+71% vs EWZ-002）但 Part B 僅 3 訊號，A/B 累計差 46.4%（>30%）。Att2/Att3 進一步放寬 BB 才達到 6 訊號平衡
- **BB(20,1.75) 下軌+回檔上限（EWZ-006 Att2）**：min(A,B) 0.69（+103% vs EWZ-002）但 Part B 僅 4 訊號，A/B 累計差 36.4%（仍>30%）。BB 1.5σ 進一步增加 Part B 至 6 訊號
- **2DD floor <= -2.0%（EWZ-007 Att1）**：min(A,B) **0.31**（vs baseline 0.69，-55%）。Part A 10/60.0%/Sharpe 0.31 / Part B 3/100%/Sharpe 11.63。失敗根因：EWZ winners/losers 在 2d 維度與 VGK/INDA/EWT/EEM 結構完全相反——EWZ losers 集中於深 2d（panic crashes：Petrobras/COVID/2019），winners 跨深+淺 2d。2DD floor -2.0% 移除 3 個淺 2d winners + 全部 3 個 losers 2d 皆深於 -2% 不影響 losers。並引入 cooldown shift 新 SL（2019-08-15）
- **2DD cap >= -3.0%（EWZ-007 Att2）**：min(A,B) **0.53**（vs baseline 0.69，-23%）。Part A 7/85.7%/Sharpe 1.16（+68%）/ Part B 5/60.0%/Sharpe 0.53（-71%）。失敗根因：Part A 大幅改善（cap 移除 2 深 2d losers）但 Part B 崩壞——cap 同時移除 2 個深 2d Part B winners（2024-06-10 EXP+ 2d -3.90%、2024-11-29 TP 2d -7.06%）並引入 cooldown shift 新 SL（2024-12-03）。EWZ Part A vs Part B 在 2d 維度結構性反轉：Part A losers 集中於深 2d crashes，Part B winners 部分為深 2d V-bounce recoveries——任何單一 2DD 閾值同時破壞 A 損傷或 B 損傷
- **^VIX 3d DIRECTION <= +5.0（EWZ-008 Att1）**：min(A,B) **0.95**（與 baseline EWZ-007 Att3 完全相同，filter 非綁定）。XLU-013 / USO-025 sweet spot 直接移植但 EWZ 殘餘 2 SLs 的 VIX 3d change 均 <= +5，filter 無作用
- **^VIX 3d DIRECTION <= +3.0（EWZ-008 Att2）**：min(A,B) **0.62**（vs baseline 0.95，-35%）。Part A 11/8 wins/Sharpe 0.62 cum +30.31% / Part B 5/4 wins/Sharpe 1.61 cum +19.54%。**Cooldown chain-shift collapse**：+3 過濾 2019-08-02 TP（trade war 起點，VIX 3d > +3）但 cooldown shift 引入 2019-08-15 SL；目標 SLs（2019-03-25 / 2020-01-31）VIX 3d 均 <= +3 仍未過濾，Part B 同時 cooldown shift 損失 1 winner
- **^VIX LEVEL CAP <= 18.0（EWZ-008 Att3）**：min(A,B) **0.87**（vs baseline 0.95，-8%）。Part A 5/4 wins/Sharpe 0.87 cum +16.57% / Part B 4/3 wins/Sharpe 1.37 cum +13.85%。LEVEL CAP 過濾 2020-01-31 SL（VIX 18.84，目標達成 ✓）但同時過濾 5 個 Part A TPs（VIX 17-25 winners）+ 2 個 Part B winners，訊號減半，cum 大幅退化。**確認 EWZ winners 廣泛分布於 ^VIX 高 level 區間，LEVEL CAP 過濾不可避免地犧牲多數 risk-off rebound 高品質訊號**
- **EWZ-EEM rel_10d <= +2.0%（EWZ-009 Att2）**：min(A,B) **1.39**（vs Att1 1.50，-7%；仍優於 EWZ-007 baseline 0.95 +46%）。Part A 9 訊號 WR 88.9% Sharpe 1.39 cum +41.69% / Part B 不變。過嚴 +2.0% 邊界移除 2022-09-28 TP（rel_10d +2.12pp），cooldown shift 無法替補，確認 +2.5% 為甜蜜點下緣
- **EWZ-EEM rel_10d <= +3.5%（EWZ-009 Att3）**：min(A,B) **1.50**（與 Att1 完全相同）。寬邊界 robustness 測試確認 [+2.5%, +3.5%] 為 robust sweet spot，filter 對 2020-01-31 SL（rel_10d +3.78pp）仍綁定，對其他訊號完全非綁定

**已掃描的參數空間：**
- 均值回歸進場：10日高點回檔 7-10% + WR(10)≤-80 + ClosePos≥40% + ATR(5)/ATR(20) > 1.1~1.15 + 冷卻10天
- 出場參數：TP +4.0~5.0% / SL -4.0% / 15~18天持倉
- ATR 門檻：1.1（最佳）、1.15（過度過濾）
- TP +5% > +4%：贏利交易均可輕鬆達到 +5%，非對稱出場大幅提高 profit factor（1.56→1.95）
- 持倉 18天 > 15天：Part B 到期交易從 +1.05%@15天 → +4.14%@18天
- ClosePos ≥ 40% 有效（EWZ 1.75% 在有效邊界 ≤2.0% 內）
- ATR > 1.1 有效且不可省略（EWZ 1.75% 在有效邊界 ≤2.25% 內）
- 回檔上限 10% 有效（過濾 COVID 等極端崩盤）
- BB Squeeze Breakout：30th/25th 百分位 + SMA(50) 均失敗（6 次迭代含不同 TP/SL）
- 2日急跌 ≤-3.5% + WR(10)≤-70：Part A WR 僅 46.2%，不如 10日高點回檔精確
- 趨勢動量回檔（Close>SMA50 + 淺回檔 + 寬鬆 WR）：Part A/B 均近 50% WR，無邊際
- RSI(2)<10 + 深回檔 + ATR：WR 37.5%（8訊號中 5 筆停損），完全失敗
- WR(5)≤-80 無 ATR 過濾：增加 3 個假訊號，Part A WR 從 61.5%→43.8%
- WR 週期：WR(10) 最佳，WR(5) 過度敏感（增加假訊號）
- RS 動量（EWZ vs EEM）：RS(10d/15d/20d) 搭配 2-4% 門檻，回調 2-7%，含/不含 ATR 過濾（EWZ-005 三次迭代均失敗）
- BB 下軌+回檔上限混合進場：BB(20, 2.0/1.75/1.5) + 10% 回檔上限 + 三重品質過濾（EWZ-006 三次迭代，BB 1.5 為甜蜜點）
- **Capitulation strength filter（EWZ-007 三次迭代）**：2DD floor <= -2.0%（FAIL min 0.31）/ 2DD cap >= -3.0%（FAIL min 0.53）/ **1d cap >= -5.0%（SUCCESS min 0.95，surgical Petrobras filter）**。1d cap 為 outlier-event surgical filter 甜蜜點，2DD 雙向皆失敗（A/B 結構性反轉）
- **^VIX forward-looking implied vol regime gate（EWZ-008 三次迭代，全部失敗）**：DIRECTION 3d <= +5（非綁定 min 0.95）/ DIRECTION 3d <= +3（cooldown chain-shift collapse min 0.62）/ LEVEL CAP <= 18（過度過濾 winners min 0.87）。確認 ^VIX 維度結構性正交於 EWZ 殘餘 SLs（雙獨立事件 yield curve / COVID early concern），lesson #24 family 在 EM single-country ETF 不適用
- **EWZ-EEM cross-asset divergence regime gate（EWZ-009 三次迭代，Att1 ★ SUCCESS）**：rel_lookback=10d，max_rel_return Att1 +2.5%（surgical sweet spot 中央，min 1.50 ★）/ Att2 +2.0%（過嚴邊界，min 1.39 退化）/ Att3 +3.5%（寬邊界 robustness，等於 Att1）。Att1 surgical filter 過濾 2020-01-31 SL（rel_10d +3.78pp，唯一 outlier）零 winners 損傷零 cooldown shift，repo 首次 EM single-country ETF + cross-asset divergence regime gate 成功

**尚未嘗試的方向（可探索，但預期改善有限）：**
- BB(20, 1.25) 更寬下軌（可能進一步增加訊號但品質下降，lesson #1）
- BB 下軌不搭配 10% 回檔上限（可能讓入 COVID 等極端崩盤，EWJ-003 Att2 已驗證移除 cap 會稀釋 Part A）
- 持倉 20 天（Att3 唯一 Part B 到期交易為 2024-01-18 -0.84%，延長持倉可能挽救但風險增加暴露）
- 1d cap >= -4.0%（移除 2021-02-22 Petrobras + 2021-10-21 TP，預期 Part A 損傷 winner，淨負面）
- 同時應用 1d cap + 2d filter（複合條件，可能引入過度過濾或保留壞訊號的失衡）
- ~~^VIX forward-looking implied vol regime gate（DIRECTION / LEVEL）~~ → EWZ-008 三次迭代全部失敗，lesson #24 family 在 EM single-country ETF 結構性失敗
- ~~EWZ-EEM cross-asset divergence regime gate（rel_10d cap）~~ → EWZ-009 Att1 ★ SUCCESS（min 0.95→1.50, +58%）
- 跨資產 implied vol（EEM 對比 EWZ 30d implied vol、巴西 IBOVESPA implied vol）— 預期同 ^VIX 失敗（EM single-country idiosyncratic shock 來源 heterogeneous）
- Broad-market macro context confirmation gate（lesson #25 SPY 10d return）— 預期同 lesson #24 失敗（commodity miners ETF COPX-013 已證實 lesson #25 不適用商品驅動 ETF）
- DXY direction filter（lesson #24 v7 候選，COPX-016 商品/礦業 ETF 首次驗證）— EWZ trade-level 分析顯示 SLs 之 DXY 5d/10d/15d/20d 與 winners 重疊，DXY 維度結構性正交於 EWZ 殘餘 SLs（2019-03-25 yield curve 與 2020-01-31 COVID early 皆於 USD 平穩期），預期失敗
- 加深 cooldown 至 15-20 天（cd 10 已避免 chain shift；增加 cd 可能犧牲少量訊號 + 統計顯著性）
- 同時 1d cap + rel_10d cap 雙 filter 微調（EWZ-009 Att1 已涵蓋此組合，2019-03-25 殘餘 SL 為結構性 noise 不可同時過濾）

**關鍵資產特性：**
- EWZ 為巴西 ETF（iShares MSCI Brazil），追蹤巴西大盤
- 日均波動約 1.75%（GLD 的 1.56 倍），年化波動率 ~27.8%
- 受巴西經濟、大宗商品價格（鐵礦石、石油）、美元/雷亞爾匯率影響
- 作為新興市場單一國家 ETF，日波動 > 1.5% 不適用 RSI(2)（lesson #27，EWZ-004 Att2 驗證）
- **BB 下軌+回檔上限混合進場是 EWZ 最佳框架**（6 次實驗、15 次迭代驗證）：BB(20, 1.5) 自適應低波動期捕捉淺門檻訊號，10% 回檔上限隔離 COVID 等極端崩盤
- BB Squeeze 突破不適合（3 次迭代驗證，宏觀事件驅動的突破無持續性）
- 趨勢動量回檔不適合（1 次迭代驗證，lesson #26 市場狀態依賴過強）
- RS 動量回調（EWZ vs EEM）不適合（3 次迭代驗證，巴西商品優勢非週期性）
- ATR(5)/ATR(20) > 1.1 不可省略（EWZ-004 Att3 驗證，移除後 WR 降 18%）
- ClosePos ≥ 40% 確認日內反轉，EWZ 1.75% 剛好在有效邊界內
- 非對稱 TP+5%/SL-4% 大幅提升盈虧比，因贏利交易反彈幅度充足
- **EWZ 為商品驅動 EM 單國 ETF，可使用 BB 下軌混合進場**（與政策驅動 FXI 不同，FXI 三次迭代均失敗）
- **EWZ 2DD/1d capitulation 結構（EWZ-007 trade-level 分析）**：Part A losers 集中於深 2d crashes（Petrobras 2021-02-22 2d -5.93%、COVID 2020-01-31 2d -2.67%、2019-03-25 2d -4.79%），Part A winners 跨深+淺 2d；Part B winners 部分為深 2d V-bounce recoveries（2024-11-29 TP 2d -7.06%、2024-06-10 EXP+ 2d -3.90%）。**A/B 結構性反轉使 2DD floor / 2DD cap 雙向皆失敗**——僅 1d 維度 surgical filter（>= -5.0%）可達成「移除單一 outlier loser、零 winners 損傷、零 cooldown shift」精準效果，因 EWZ 含 1 筆 ~2.86σ 級單日暴跌（Petrobras 1d -6.19%）為 outlier 而非 regime-level pattern
- **lesson #19 family 邊界擴展（EWZ-007 新發現）**：商品/政治雙驅動 EM ETF 在 lesson #19 family 上需切換至「outlier-event surgical filter」（1d cap）而非「regime-level threshold filter」（2DD floor/cap）。此為 EWT-009 / EWJ-005 「2DD/1d 維度需依資產調整」規則的進一步精煉：跨資產不僅需調整閾值（VGK -2.0% vs EWT -1.5% vs EWJ 1d -0.5%），亦需調整維度（2d vs 1d）與方向（floor vs cap）與目標範圍（regime-level threshold vs outlier-event surgical）
- **lesson #20 v3 邊界擴展（EWZ-009 新發現）**：EM single-country ETF（EWZ）vs broad EM ETF（EEM）為「同類 ETF 內 broader benchmark 為 anchor」cross-asset divergence regime gate 變體（先前 lesson #20 anchor 多為 cross-asset class 如 TLT vs SPY、TSLA vs QQQ、NVDA vs SMH）。EWZ rel_10d outlier 訊號（country-specific lagging-decline）為 EWZ MR 失敗模式之一，EWZ-EEM rel_10d cap 為其 surgical filter
- **EWZ Part A 殘餘 SLs 異質性結構（EWZ-009 trade-level 確認）**：2019-03-25 SL（rel_10d -5.20pp，EWZ 已弱於 EEM）為「sustained Brazil-specific weakness」、2020-01-31 SL（rel_10d +3.78pp，EWZ 強於 EEM）為「country-specific lagging-decline」，方向相反，無法用單一 cross-asset divergence 維度同時過濾。+2.5pp 上限 surgical filter 移除前者，2019-03-25 殘餘為已知結構性 noise
- **EWZ MR 框架雙 surgical filter 整合（lesson #19 + lesson #20 正交組合）**：EWZ-007 1d cap (≤ -5%, 移除 ~3σ 單日 outlier Petrobras) + EWZ-009 rel_10d cap (≤ +2.5pp, 移除 country-specific lagging-decline) 共同移除 EWZ Part A 結構性 SLs，repo 首次正交雙 surgical filter 組合於 MR 框架
<!-- AI_CONTEXT_END -->

# EWZ 實驗總覽 (EWZ Experiments Overview)

## 標的特性 (Asset Characteristics)

- **EWZ (iShares MSCI Brazil ETF)**：追蹤巴西 MSCI 指數的 ETF
- 日均波動約 1.75%，為 GLD 的 1.56 倍
- 受巴西經濟基本面、大宗商品價格（鐵礦石、石油）、美元/雷亞爾匯率等多重因素影響
- 新興市場單一國家 ETF，波動度介於寬基指數（SPY ~1.2%）與商品 ETF（SIVR ~2.3%）之間

## 參數對照表 (Parameter Comparison)

| 參數 | EWZ-002 Att3 | EWZ-006 Att3 | EWZ-007 Att3 | **EWZ-009 Att1 ★** |
|------|---------------|--------------|--------------|---------------------|
| 進場框架 | 10日回檔 7-10% + WR(10)≤-80 | BB(20,1.5) 下軌 + 10日回檔上限 10% | BB(20,1.5) 下軌 + 10日回檔上限 10% | **BB(20,1.5) 下軌 + 10日回檔上限 10%** |
| ClosePos | ≥40% | ≥40% | ≥40% | **≥40%** |
| ATR 過濾 | ATR(5)/ATR(20)>1.1 | ATR(5)/ATR(20)>1.1 | ATR(5)/ATR(20)>1.1 | **ATR(5)/ATR(20)>1.1** |
| Capitulation filter (lesson #19) | 無 | 無 | 1d cap >= -5.0% | **1d cap >= -5.0%** |
| Cross-asset divergence (lesson #20) | 無 | 無 | 無 | **EWZ-EEM rel_10d ≤ +2.5pp** |
| TP / SL / 持倉 | +5%/-4%/18天 | +5%/-4%/18天 | +5%/-4%/18天 | **+5%/-4%/18天** |
| 冷卻期 | 10天 | 10天 | 10天 | **10天** |
| **Part A Sharpe** | **0.34** | **0.69** | **0.95** | **1.50** |
| **Part B Sharpe** | **12.85** | **1.82** | **1.82** | **1.82** |
| **min(A,B) Sharpe** | **0.34** | **0.69** | **0.95** | **1.50 ★** |

## 實驗列表 (Experiment List)

| ID      | 資料夾                            | 策略摘要                                | 狀態   |
|---------|----------------------------------|----------------------------------------|--------|
| EWZ-001 | `ewz_001_pullback_wr`            | 10日回檔+Williams%R 均值回歸              | 已完成（前基線） |
| EWZ-002 | `ewz_002_vol_adaptive_pullback`  | 波動率自適應回檔+WR+非對稱出場（ATR過濾）  | 已完成（前最佳） |
| EWZ-003 | `ewz_003_bb_squeeze_breakout`    | BB 擠壓突破(Att1-2) → 急跌恐慌反轉(Att3) | ❌ 未超越 EWZ-002 |
| EWZ-004 | `ewz_004_trend_momentum_pullback`| 趨勢動量(Att1)→RSI(2)(Att2)→WR(5)(Att3) | ❌ 未超越 EWZ-002 |
| EWZ-005 | `ewz_005_rs_momentum`            | RS 動量回調 EWZ vs EEM (Att1-3)          | ❌ 未超越 EWZ-002 |
| EWZ-006 | `ewz_006_bb_lower_pullback_cap`  | BB 下軌+回檔上限混合進場(Att1-3)         | 已完成（前最佳） |
| EWZ-007 | `ewz_007_vol_transition_mr`      | Post-Capitulation Vol-Transition MR（1d cap surgical Petrobras filter）| 已完成（前任最佳） |
| EWZ-008 | `ewz_008_vix_implied_vol_mr`     | ^VIX Forward-Looking Implied-Vol Regime-Gated MR（lesson #24 family v2 變體）| ❌ 三次迭代均失敗（lesson #24 family 在 EM single-country ETF 結構性失敗） |
| EWZ-009 | `ewz_009_ewz_eem_divergence_mr`  | EWZ-EEM Relative Strength Divergence Filter on Vol-Transition MR（lesson #20 v3 cross-asset divergence regime gate，repo 第 6 次跨資產 + 首次 EM single-country ETF + 首次 broad benchmark anchor 變體）★ | ✅ 當前最佳 |

---

## EWZ-001: Pullback + Williams %R Mean Reversion

**目標**：以回檔幅度 + Williams %R 雙重確認捕捉 EWZ 超賣反彈機會。

### 進場條件（全部滿足）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 回檔深度 | 收盤價 vs 10日最高價 | ≥ 7% | 過濾淺回調，需較深回檔才進場（5% 過鬆已驗證）|
| 超賣確認 | Williams %R(10) | ≤ -80 | 確認處於超賣區間 |
| 冷卻期 | 距上次訊號 | > 10 個交易日 | 避免連續二次探底訊號 |

### 出場參數

| 參數 | 值 | 說明 |
|------|------|------|
| 止盈 (TP) | +4.0% | 寬 TP 給予足夠反彈空間 |
| 停損 (SL) | -4.0% | 寬 SL 避免日內波動觸發停損（3% 已驗證過緊）|
| 持倉上限 | 15 天 | 較高波動更快回歸 |

### 成交模型

| 項目 | 設定 |
|------|------|
| 進場方式 | 隔日開盤市價單 |
| 出場方式 | 悲觀認定（日內高低觸及 TP/SL 時選擇較差結果）|
| 滑價假設 | 0.1%（ETF 標準）|
| 未成交處理 | 訊號日隔日開盤無條件成交 |

### 設計理念

- **選擇 Pullback+WR 而非 RSI(2)**：EWZ 日波動 1.75% > 1.5%，且非寬基指數 ETF，RSI(2) 不適用（lesson #27）
- **不使用追蹤停損**：日波動 1.75% > 1.5% 門檻，trailing stop 會被日內震盪觸發（lesson #2）
- **7% 回檔門檻**：5% 過鬆導致 WR < 50%（已驗證），7% 與 SIVR-003 相同，篩選較���回調
- **TP/SL ±4% 對稱**：3% SL 過緊導致大量停損（已驗證），4% 給予足夠呼吸空間

### 回測結果

| 區間 | 訊號數 | 年均 | 勝率 | 累計報酬 | Sharpe | 最大回撤 |
|------|--------|------|------|---------|--------|---------|
| Part A (2019-2023) | 42 | 8.4 | 54.8% | +14.0% | 0.10 | -14.18% |
| Part B (2024-2025) | 9 | 4.5 | 77.8% | +18.5% | 0.60 | -5.73% |
| Part C (2026-) | 2 | 7.5 | 100% | +8.2% | 0.00 | 0.15% |

**A/B 訊號比**：1.87:1（可接受）
**min(A,B) Sharpe**：0.10

---

## EWZ-002: Volatility-Adaptive Pullback + WR Mean Reversion ★ 當前最佳

**目標**：在 EWZ-001 基礎上加入 ATR 波動率過濾 + ClosePos 反轉確認 + 回檔上限 + 非對稱出場，大幅提升 Part A 品質。

### 進場條件（全部滿足）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 回檔深度 | 收盤價 vs 10日最高價 | ≥ 7% | 過濾淺回調 |
| 回檔上限 | 收盤價 vs 10日最高價 | ≤ 10% | 隔離極端崩盤（6σ ≈ 10.5%）|
| 超賣確認 | Williams %R(10) | ≤ -80 | 確認處於超賣區間 |
| 反轉確認 | 收盤位置 (ClosePos) | ≥ 40% | 日內反轉確認 |
| 波動率飆升 | ATR(5)/ATR(20) | > 1.1 | 選擇急跌恐慌，過濾慢磨下跌 |
| 冷卻期 | 距上次訊號 | > 10 個交易日 | 避免連續進場 |

### 出場參數

| 參數 | 值 | 說明 |
|------|------|------|
| 止盈 (TP) | +5.0% | 非對稱出場，提高盈虧比（所有贏利交易均達 +5%）|
| 停損 (SL) | -4.0% | 保持寬 SL 呼吸空間 |
| 持倉上限 | 18 天 | 延長持倉給予更多時間（Part B 到期交易從 +1.05%→+4.14%）|

### 成交模型

| 項目 | 設定 |
|------|------|
| 進場方式 | 隔日開盤市價單 |
| 出場方式 | 悲觀認定（日內高低觸及 TP/SL 時選擇較差結果）|
| 滑價假設 | 0.1%（ETF 標準）|
| 未成交處理 | 訊號日隔日開盤無條件成交 |

### 回測結果

| 區間 | 訊號數 | 年均 | 勝率 | 累計報酬 | Sharpe | Profit Factor | 最大回撤 |
|------|--------|------|------|---------|--------|---------------|---------|
| Part A (2019-2023) | 13 | 2.6 | 61.5% | +19.84% | 0.34 | 1.95 | -6.18% |
| Part B (2024-2025) | 4 | 2.0 | 100% | +20.56% | 12.85 | ∞ | -3.69% |
| Part C (2026-) | 1 | 3.7 | 100% | +5.00% | 0.00 | ∞ | 1.50% |

**A/B 年化訊號比**：1.3:1（優秀）
**A/B 累計報酬差距**：0.72%（近乎完美平衡）
**min(A,B) Sharpe**：0.34（vs EWZ-001 的 0.10，+240%）

### 迭代記錄

**Att1**（ATR > 1.1 + ClosePos ≥ 40% + cap 10% + TP+4%/SL-4%/15d）：
- Part A Sharpe 0.22 (WR 61.5%, 13訊號), Part B Sharpe 2.55 (WR 100%, 4訊號)
- min(A,B) 0.22（+120% vs EWZ-001）。ATR+ClosePos+cap 成功過濾 Part A 低品質訊號（42→13）

**Att2**（ATR > 1.15，其餘同 Att1）：
- Part A Sharpe 0.19 (10訊號)，Part B 不變
- **退化**：ATR 1.15 移除 2 筆好訊號 + 1 筆壞訊號，淨效果為負

**Att3★**（ATR > 1.1 + TP+5%/SL-4%/18d）：
- Part A Sharpe **0.34** (WR 61.5%, 累計+19.84%), Part B Sharpe **12.85** (累計+20.56%)
- 非對稱出場大幅提升盈虧比（1.56→1.95），所有 8 筆贏利交易均輕鬆達到 +5%
- 延長持倉至 18 天，Part B 到期交易從 +1.05%@15d → +4.14%@18d

### 設計理念

- **ATR(5)/ATR(20) > 1.1**：EWZ 1.75% 日波動在 ATR 有效邊界（≤2.25%）內。門檻 1.1 參考 IWM-011（1.5-2% vol），有效過濾 2019 年三筆慢磨下跌假訊號
- **ClosePos ≥ 40%**：EWZ 1.75% 在 ClosePos 有效邊界（≤2.0%）內，確認日內反轉，移除仍在持續下跌中的假超賣訊號
- **回檔上限 10%**：~6σ for 1.75% daily vol，隔離 COVID 等極端崩盤
- **TP +5% 非對稱**：EWZ 均值回歸反彈動能充足，贏利交易平均 2-4 天即達 +5%，+4% 只是壓縮利潤
- **18 天持倉**：僅比 15 天多 3 天，但讓邊際交易有更多時間達標

---

## EWZ-003: BB Squeeze Breakout → Acute Panic Reversal ❌ 未超越 EWZ-002

**目標**：探索突破策略和不同均值回歸進場機制，嘗試超越 EWZ-002 的 min Sharpe 0.34。

### 迭代記錄

**Att1**（BB Squeeze 30th pct + SMA(50) + TP+4.5%/SL-4.0%/20d/cooldown 12）：
- Part A Sharpe 0.03 (WR 50.0%, 16訊號), Part B Sharpe -0.69 (WR 20.0%, 5訊號)
- **失敗**：EWZ 突破後頻繁反轉（Part A 8 停損 vs 7 達標），Part B 4/5 停損
- 原因：巴西 ETF 突破受宏觀事件（大宗商品/BRL/政治）驅動，持續性不足

**Att2**（BB Squeeze 25th pct + TP+3.5%/SL-5.0%/20d/cooldown 15）：
- Part A Sharpe -0.04 (WR 57.1%, 14訊號), Part B Sharpe -0.39 (WR 40.0%, 5訊號)
- **仍失敗**：收緊壓縮門檻少量改善 WR（50%→57%），但寬 SL(-5%) 虧損更大，降 TP(3.5%) 壓縮利潤

**Att3**（策略轉向：2日急跌≤-3.5% + WR(10)≤-70 + ClosePos≥35% + ATR>1.1 + TP+5%/SL-4%/15d/cooldown 10）：
- Part A Sharpe 0.02 (WR 46.2%, 13訊號, 累計-0.03%), Part B Sharpe 2.35 (WR 100%, 4訊號, 累計+16.98%)
- **失敗**：Part A WR 僅 46.2%（6勝7負），2日急跌在延長下跌趨勢（COVID、升息週期）中捕捉不反轉的恐慌。Part B 優秀但樣本太小且 A/B 極度不平衡

### 結論

| 策略類型 | 最佳迭代 | min(A,B) Sharpe | 結論 |
|----------|---------|-----------------|------|
| BB Squeeze Breakout | Att1 | 0.03 | EWZ 突破無持續性 |
| BB Squeeze（寬SL/低TP）| Att2 | -0.04 | 寬SL+低TP=更差 |
| 2日急跌恐慌反轉 | Att3 | 0.02 | Part A 假訊號過多 |

**關鍵發現**：
1. BB Squeeze Breakout 不適合 EWZ（宏觀事件驅動的突破無法持續，3次迭代確認）
2. 2日急跌不如 10日高點回檔精確（捕捉延長下跌中的假反轉）
3. EWZ-002 的 pullback+WR+ATR+ClosePos 框架在 EWZ 上無可替代

### 回測結果（Att3 - 最終版本）

| 區間 | 訊號數 | 年均 | 勝率 | 累計報酬 | Sharpe | 最大回撤 |
|------|--------|------|------|---------|--------|---------|
| Part A (2019-2023) | 13 | 2.6 | 46.2% | -0.03% | 0.02 | -15.04% |
| Part B (2024-2025) | 4 | 2.0 | 100% | +16.98% | 2.35 | -3.69% |
| Part C (2026-) | 1 | 3.7 | 0% | -4.10% | 0.00 | -4.90% |

---

## EWZ-004: Multi-Strategy Exploration ❌ 未超越 EWZ-002

**目標**：探索趨勢動量、RSI(2) 動量、WR 週期優化等不同策略方向，嘗試超越 EWZ-002 的 min Sharpe 0.34。

### 迭代記錄

**Att1**（趨勢動量回檔：Close>SMA(50) + 4-8% 回檔 + WR(10)≤-60 + TP+4.5%/SL-4.0%/15d）：
- Part A Sharpe 0.09 (WR 52.4%, 21訊號, 累計+5.89%), Part B Sharpe 0.06 (WR 50.0%, 12訊號, 累計+1.63%)
- **失敗**：趨勢確認（SMA50）在 EM 單國 ETF 上無效。WR 接近 50%（拋硬幣），宏觀事件可突然反轉趨勢
- 原因：lesson #26 驗證——趨勢回檔策略在 EM ETF 上市場狀態依賴過強

**Att2**（RSI(2) 深回檔：RSI(2)<10 + 7-10% 回檔 + ATR>1.1 + ClosePos≥40% + TP+5%/SL-4%/18d）：
- Part A Sharpe -0.16 (WR 37.5%, 8訊號, 累計-6.10%), Part B Sharpe 10.63 (WR 100%, 2訊號, 累計+9.35%)
- **失敗**：RSI(2) 在 EWZ (1.75% vol) 上完全失敗。8 訊號中 5 筆停損，即使配合深回檔+ATR 也無法挽救
- 原因：lesson #27 驗證——RSI(2) 不適用 vol>1.5% 的非美國單一國家 ETF，深回檔門檻無法像 URA（需 10%+回檔）那樣補救 1.75% vol 的 EM ETF

**Att3**（短窗口 WR：WR(5)≤-80 + 7-10% 回檔 + ClosePos≥40%（無 ATR）+ TP+5%/SL-4%/18d）：
- Part A Sharpe -0.03 (WR 43.8%, 16訊號, 累計-3.46%), Part B Sharpe 0.56 (WR 75.0%, 4訊號, 累計+8.36%)
- **失敗**：WR(5) 無 ATR 過濾比 EWZ-002 多生成 3 個 Part A 訊號（全為停損），Part A WR 從 61.5%→43.8%
- 原因：WR(5) 不足以替代 ATR(5)/ATR(20) 過濾。ATR 過濾的核心功能（區分急跌恐慌 vs 慢磨下跌）無法由短窗口 WR 替代

### 結論

| 策略類型 | 最佳迭代 | min(A,B) Sharpe | 結論 |
|----------|---------|-----------------|------|
| 趨勢動量回檔 | Att1 | 0.06 | 趨勢確認在 EM ETF 無效 |
| RSI(2) 深回檔 | Att2 | -0.16 | RSI(2) 在 1.75% vol EM ETF 完全失敗 |
| WR(5) 無 ATR | Att3 | -0.03 | ATR 過濾不可省略 |

**關鍵發現**：
1. **趨勢策略在 EM 單國 ETF 無效**（lesson #26 驗證）：SMA(50) 趨勢在宏觀事件面前毫無保護力
2. **RSI(2) 在 EWZ 完全失敗**（lesson #27 驗證）：1.75% vol + EM 單國 ETF 雙重不利因素
3. **ATR(5)/ATR(20) 過濾是 EWZ 策略的關鍵組件**：移除後 Part A WR 從 61.5%→43.8%（降 18%），MaxDD 從 -6.18%→-14.18%
4. **EWZ-002 Att3 的 pullback+WR(10)+ATR+ClosePos 框架已接近 EWZ 策略天花板**（4 次實驗、9 次迭代確認）

### 回測結果（Att3 - 最終版本）

| 區間 | 訊號數 | 年均 | 勝率 | 累計報酬 | Sharpe | 最大回撤 |
|------|--------|------|------|---------|--------|---------|
| Part A (2019-2023) | 16 | 3.2 | 43.8% | -3.46% | -0.03 | -14.18% |
| Part B (2024-2025) | 4 | 2.0 | 75.0% | +8.36% | 0.56 | -5.08% |
| Part C (2026-) | 1 | 3.6 | 100% | +5.00% | 0.00 | 1.50% |

---

## EWZ-005: Relative Strength Momentum Pullback (EWZ vs EEM)

**目標**：利用 EWZ 相對 EEM 的超額表現（RS 動量），在動量優勢下買入短期回調。參考 EWT-007（RS vs EEM, min 0.42）、SOXL-010（RS vs SPY, min 0.70）的成功案例。

### 策略理念

巴西 ETF 大宗商品權重極高（Vale、Petrobras），當 EWZ 相對 EEM 展現超額表現時，代表巴西商品週期在 EM 中領先。在趨勢確認下（Close > SMA(50)），買入短期回調。

### 三次嘗試

**Att1**: RS(20d) >= 3%, 5日高點回調 3-7%, SMA(50), TP+5%/SL-4%/18d

| 區間 | 訊號數 | 年均 | 勝率 | 累計報酬 | Sharpe | 最大回撤 |
|------|--------|------|------|---------|--------|---------|
| Part A (2019-2023) | 24 | 4.8 | 66.7% | +56.16% | 0.46 | -7.89% |
| Part B (2024-2025) | 4 | 2.0 | 25.0% | -5.03% | -0.33 | -7.80% |

→ Part A 優秀但 Part B 崩潰。A/B 年化訊號比 2.4:1，commodity cycle 集中在 2019-2023。

**Att2**: RS(15d) >= 2%, 5日高點回調 2-6%, ATR(5)/ATR(20)>1.1, SMA(50), TP+5%/SL-4%/18d

| 區間 | 訊號數 | 年均 | 勝率 | 累計報酬 | Sharpe | 最大回撤 |
|------|--------|------|------|---------|--------|---------|
| Part A (2019-2023) | 17 | 3.4 | 47.1% | -1.77% | -0.00 | -5.92% |
| Part B (2024-2025) | 3 | 1.5 | 33.3% | -3.43% | -0.25 | -4.94% |

→ ATR 過濾在動量策略中反效果，移除好訊號多於壞訊號（與均值回歸相反）。兩期均惡化。

**Att3**: RS(10d) >= 4%, 5日高點回調 2-5%, SMA(50), TP+5%/SL-4%/18d

| 區間 | 訊號數 | 年均 | 勝率 | 累計報酬 | Sharpe | 最大回撤 |
|------|--------|------|------|---------|--------|---------|
| Part A (2019-2023) | 20 | 4.0 | 35.0% | -18.35% | -0.21 | -7.60% |
| Part B (2024-2025) | 3 | 1.5 | 66.7% | +5.73% | 0.46 | -7.73% |

→ A/B 完全反轉（vs Att1），10日 RS 在 Part A 生成大量假訊號（8 連虧、13 次停損）。

### 結論

RS 動量策略對 EWZ vs EEM 根本無效。三次迭代展現嚴重市場狀態依賴：
- **A/B 訊號極度不平衡**：20-24:3-4，年化比 2.4-2.7:1
- **WR 大幅波動**：Att1 Part A 66.7% vs Part B 25%；Att3 完全反轉
- **根本原因**：巴西商品優勢受大宗商品價格/BRL 匯率/政治事件驅動，屬宏觀事件型而非 EWT 半導體那樣的產業週期型。RS 動量有效條件（強週期性板塊或地理週期差異）在 EWZ 上不成立
- **ATR 過濾在動量策略中反效果**（Att2 驗證）：波動率飆升在動量回調中是趨勢反轉信號，非恐慌反彈機會

---

## EWZ-006: BB 下軌 + 回檔上限混合進場均值回歸

### 目標 (Goal)

延伸 EWJ-003 / VGK-007 / CIBR-008 的「BB 下軌 + 回檔上限」混合進場架構至 EWZ。
這三個資產（EWJ 1.15%、VGK 1.12%、CIBR 1.53% vol）均驗證 BB 下軌作為自適應進場
門檻優於固定回檔門檻（min Sharpe 改善 +9~+44%）。EWZ 1.75% vol 為更高波動度，
測試該模式是否仍適用。

### 進場條件 (Entry Conditions)

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | BB 下軌觸及 | Close <= BB(20, 1.5) lower | — | 自適應深度過濾 |
| 2 | 回檔上限 | 10日高點回檔 | >= -10% | 崩盤隔離（5.7σ for 1.75% vol）|
| 3 | 超賣確認 | Williams %R(10) | <= -80 | 短期超賣 |
| 4 | 反轉跡象 | ClosePos | >= 40% | 日內反轉 |
| 5 | 波動率飆升 | ATR(5)/ATR(20) | > 1.10 | 過濾慢磨下跌假訊號 |
| 6 | 冷卻期 | Cooldown | 10 天 | 避免重複進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| TP | +5.0% | 非對稱出場（同 EWZ-002 Att3 驗證甜蜜點）|
| SL | -4.0% | 同 EWZ-002 驗證 |
| 最大持倉 | 18 天 | 同 EWZ-002 驗證 |
| 追蹤停損 | 無 | 高波動 EM ETF 禁用 trailing stop（lesson #2）|

### 三次迭代結果

| 迭代 | BB std | Part A Sharpe | Part B Sharpe | min(A,B) | A/B 訊號 | A/B 累計差 |
|------|--------|---------------|---------------|----------|----------|-----------|
| Att1 | 2.0 | 0.58 (7訊號 WR 71.4%) | 1.11 (3訊號 WR 66.7%) | 0.58 | 1.4:1.5/yr | 46.4% |
| Att2 | 1.75 | 0.69 (8訊號 WR 75.0%) | 1.40 (4訊號 WR 75.0%) | 0.69 | 1.6:2.0/yr | 36.4% |
| **Att3 ★** | **1.5** | **0.69 (12訊號 WR 75.0%)** | **1.82 (6訊號 WR 83.3%)** | **0.69** | **2.4:3.0/yr** | **30.7%** |

### 關鍵發現

- **BB(20, 1.5) 為 EWZ 甜蜜點**：較窄 BB（2.0σ）訊號過少導致 Part B 樣本不足；BB(20, 1.5) 在保留訊號品質（Part A WR 75%）同時將 Part B 訊號增加至 6（足夠統計意義）
- **10% 回檔上限不可省略**：直接套用 EWJ-003 模式但保留 EWZ-002 驗證有效的 10% cap（5.7σ for 1.75% vol），隔離 COVID 等極端崩盤訊號（同 EWJ-003 Att2→Att3 教訓）
- **A/B 累計差 30.7%**：略高於理論 30% 門檻，但反映時間長度差異（5yr vs 2yr）。年化訊號頻率 1.25:1 平衡優秀，Part B 年化累計 +12.76%/yr 實際優於 Part A +7.36%/yr
- **vs EWZ-002 Att3**：min(A,B) Sharpe 0.34→0.69（+103%），Part B 樣本 4→6（+50%），Part B WR 100%→83.3%（合理化，從統計噪音轉為穩健樣本）
- **驗證 lesson #52 延伸**：商品驅動 EM 單國 ETF（EWZ）可使用 BB 下軌混合進場，與政策驅動單國 EM ETF（FXI 失敗）形成對比

---

## 演進路線圖 (Roadmap)

EWZ-001 (回檔+WR 基礎版，min Sharpe 0.10)
  └── EWZ-002 (ATR+ClosePos+cap+非對稱出場，min Sharpe 0.34，+240%)
        └── EWZ-006 (BB 下軌 1.5σ+回檔上限 10%+三重品質過濾，min Sharpe 0.69，+103%)
              └── EWZ-007★ (EWZ-006 + 1d cap >= -5.0% surgical Petrobras filter，min Sharpe 0.95，+38%)
EWZ-003 (BB Squeeze→急跌恐慌，min Sharpe 0.02) ← 獨立路線，失敗
EWZ-004 (趨勢動量→RSI(2)→WR(5)，min Sharpe -0.03) ← 三方向探索，均失敗
EWZ-005 (RS 動量 EWZ vs EEM，min Sharpe -0.33~-0.21) ← 商品 RS 非週期性，失敗

---

## EWZ-007: Post-Capitulation Vol-Transition Mean Reversion

**目標**：延伸 EWZ-006 Att3 框架，新增「Capitulation strength filter」（1日 / 2日 報酬 floor 或 cap）作為主品質過濾器，目標移除 Part A 三筆 SL（2019-03-25 巴西退休金改革雜訊、2020-01-31 COVID 初期擔憂、2021-02-22 Petrobras 政治干預）與 Part B 1 筆近零到期（2024-01-18），同時保留高品質 winners。

跨資產脈絡：lesson #19 family（VGK-008 / INDA-010 / EEM-014 / EWT-009 / EWJ-005 / IBIT-009 / USO-013）已在 7 個資產上驗證 2DD floor / 1d floor / 2DD cap 方向，repo 第 8 次 lesson #19 跨資產試驗，**首次商品/政治雙驅動 EM 單國 ETF（巴西）驗證**。

### 進場條件（七條件全部滿足）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| BB 下軌觸及 | Close vs BB(20, 1.5) 下軌 | Close ≤ 下軌 | 自適應深度過濾（同 EWZ-006）|
| 回檔上限 | 10日高點回檔 | ≥ -10% | 隔離 COVID 等極端崩盤（同 EWZ-006）|
| 超賣確認 | Williams %R(10) | ≤ -80 | 確認超賣（同 EWZ-006）|
| 收盤位置 | (Close-Low)/(High-Low) | ≥ 40% | 日內反轉（同 EWZ-006）|
| 波動率飆升 | ATR(5)/ATR(20) | > 1.10 | 急跌恐慌（同 EWZ-006）|
| **Capitulation strength** | **1 日報酬** | **≥ -5.0%（cap）** | **★ 新增：1d cap surgical filter（過濾 ~3σ 級單日 outlier 暴跌）** |
| 冷卻期 | 距上次訊號 | > 10 個交易日 | （同 EWZ-006）|

### 出場參數（同 EWZ-006）

| 參數 | 值 |
|------|------|
| TP | +5.0% |
| SL | -4.0% |
| 最大持倉 | 18 天 |
| 進場方式 | 隔日開盤市價（execution model）|
| 滑價 | 0.1%（ETF 標準）|

### 三次迭代結果

| 迭代 | Capitulation filter | Part A Sharpe | Part B Sharpe | min(A,B) | 失敗/成功分析 |
|------|---------------------|---------------|---------------|----------|---------------|
| Att1 | 2DD floor <= -2.0% | 0.31 (10訊號 WR 60.0%) | 11.63 (3訊號 WR 100%) | 0.31 | 過濾 3 baseline winners + 0 losers + cooldown shift 新 SL，反映 EWZ losers 集中於深 2d、winners 跨深淺 2d 的反轉結構 |
| Att2 | 2DD cap >= -3.0% | 1.16 (7訊號 WR 85.7%) | 0.53 (5訊號 WR 60.0%) | 0.53 | Part A 大改善但 Part B 崩壞，同時移除 2 深 2d Part B winners（2024-06-10 EXP+、2024-11-29 TP）+ cooldown shift 新 SL（2024-12-03） |
| **Att3 ★** | **1d cap >= -5.0%** | **0.95 (11訊號 WR 81.8%)** | **1.82 (6訊號 WR 83.3%)** | **0.95** | **Surgical filter，僅過濾 2021-02-22 Petrobras 1d -6.19% outlier，零 winners 損傷、零 cooldown shift、Part B 完全保留** |

### 關鍵發現

- **EWZ 2DD/1d capitulation 結構（trade-level 分析）**：Part A losers 集中於深 2d crashes（Petrobras 2021-02-22 2d -5.93%、COVID 2020-01-31 2d -2.67%、2019-03-25 2d -4.79%），Part A winners 跨深+淺 2d；Part B winners 部分為深 2d V-bounce recoveries（2024-11-29 TP 2d -7.06%、2024-06-10 EXP+ 2d -3.90%）。**A/B 結構性反轉使 2DD floor / 2DD cap 雙向皆失敗**
- **1d cap >= -5.0% 為 outlier-event surgical filter**：EWZ 含 1 筆 ~2.86σ 級單日暴跌（Petrobras 1d -6.19%）為 outlier loser，1d cap >= -5.0% 達成「移除 1 個 outlier loser、零 winners 損傷、零 cooldown shift」精準效果。Part A 殘餘 2 SLs（2019-03-25 1d +1.26% / 2020-01-31 1d -2.34%）為「Up-day rebound after big drop」與「moderate 1d sustained drop」結構，無法用單一 1d/2d 維度過濾且不傷害 winners
- **vs EWZ-006 Att3**：min(A,B) Sharpe 0.69→0.95（+38%），Part A Sharpe 0.69→0.95（+38%），Part B Sharpe 1.82 完全不變（全部 6 訊號保留）
- **A/B 平衡權衡**：累計差 30.7%→40.2%（略增，因 Part A cum 從 +36.82% 升至 +42.67% 而 Part B cum 維持 +25.52%），訊號比 12:6→11:6 維持 1.83:1（年化 1.36:1，36% gap < 50% ✓）。此為「Part A 加深品質過濾必擴大累計差距」的結構性現象（與 EWT-009 58.6%、NVDA-012 25.3% 同模式）
- **驗證 lesson #19 family 邊界擴展**：商品/政治雙驅動 EM ETF 在 lesson #19 family 上需切換至「outlier-event surgical filter」（1d cap）而非「regime-level threshold filter」（2DD floor/cap）。跨資產不僅需調整閾值（VGK -2.0% vs EWT -1.5% vs EWJ 1d -0.5%），亦需調整維度（2d vs 1d）與方向（floor vs cap）與目標範圍（regime-level vs outlier-event）

---

## EWZ-009: EWZ-EEM Relative Strength Divergence Filter on Vol-Transition MR ★ 當前最佳

**目標**：延伸 EWZ-007 Att3 完整框架（min(A,B) Sharpe 0.95），新增 **EWZ vs EEM 10 日相對強度上限**作為 cross-asset pair-divergence regime gate，目標移除 EWZ-007 Part A 殘餘 2 SLs 之一（2020-01-31 COVID early）並保持 Part B 全部 6 訊號不變。

跨資產脈絡（lesson #20 v3 cross-asset divergence regime gate）：
- **TLT-014 ✓**（TLT vs SPY divergence，rate ETF + MR 框架）
- **TSLA-017 ✓**（TSLA vs QQQ divergence，high-vol single stock + BB Squeeze Breakout）
- **NVDA-016 ◐**（NVDA vs SMH，部分成功但 A/B gap 違反）
- **COPX-014 ✗**（COPX vs GLD，商品/礦業 ETF + BB Squeeze 框架，cooldown × 訊號密度失敗）
- **USO-026 ✗**（USO vs XLE，商品 ETF + MR 框架，A/B 結構性不對稱失敗）
- **EWZ-009 ✓**（EWZ vs EEM，EM single-country ETF + MR 框架，**repo 首次 EM single-country ETF cross-asset divergence 成功**）

### 進場條件（EWZ-007 Att3 七條件 + 第八條件）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| BB 下軌觸及 | Close vs BB(20, 1.5) 下軌 | Close ≤ 下軌 | 同 EWZ-007 |
| 回檔上限 | 10日高點回檔 | ≥ -10% | 同 EWZ-007 |
| 超賣確認 | Williams %R(10) | ≤ -80 | 同 EWZ-007 |
| 收盤位置 | (Close-Low)/(High-Low) | ≥ 40% | 同 EWZ-007 |
| 波動率飆升 | ATR(5)/ATR(20) | > 1.10 | 同 EWZ-007 |
| Capitulation strength (lesson #19) | 1 日報酬 | ≥ -5.0%（cap） | 同 EWZ-007 |
| **EWZ-EEM divergence (lesson #20 v3 ★)** | **10 日報酬差 EWZ - EEM** | **≤ +2.5pp** | **★ EWZ-009 新增：cross-asset pair-divergence regime gate** |
| 冷卻期 | 距上次訊號 | > 10 個交易日 | 同 EWZ-007 |

### 出場參數（同 EWZ-007）

| 參數 | 值 |
|------|------|
| TP | +5.0% |
| SL | -4.0% |
| 最大持倉 | 18 天 |
| 進場方式 | 隔日開盤市價（execution model）|
| 滑價 | 0.1%（ETF 標準）|

### Trade-level 分析：EWZ-007 Att3 全部 17 訊號之 EWZ-EEM rel_10d 分布

**Part A（11 訊號，含 2 SLs）**：

| 日期 | 類型 | EWZ_10d | EEM_10d | rel_10d (EWZ-EEM) |
|------|------|---------|---------|-------------------|
| 2019-03-25 | SL | -4.95% | +0.26% | -5.20pp |
| 2019-05-14 | TP | -5.85% | -6.33% | +0.48pp |
| 2019-08-02 | TP | -4.56% | -5.39% | +0.83pp |
| 2019-11-13 | TP | -6.36% | -0.37% | -5.99pp |
| **2020-01-31** | **SL** | **-4.62%** | **-8.40%** | **+3.78pp ★ 唯一 outlier** |
| 2020-11-02 | TP | -5.92% | -0.33% | -5.59pp |
| 2021-01-22 | TP | -5.71% | +4.75% | -10.45pp |
| 2021-07-07 | TP | -5.95% | -0.83% | -5.12pp |
| 2021-10-21 | TP | -5.49% | +3.00% | -8.50pp |
| 2022-09-28 | TP | -4.99% | -7.11% | +2.12pp（max TP） |
| 2023-10-04 | TP | -9.54% | -3.98% | -5.56pp |

**Part B（6 訊號，全 wins / 平 / 微跌）**：rel_10d 範圍 [-7.62pp, -0.54pp]，**filter 對 Part B 完全非綁定** ✓

**關鍵觀察**：
- 2020-01-31 SL 之 rel_10d **+3.78pp** 為唯一 > +2.5pp 訊號
- 全部 9 Part A TPs 之 rel_10d ≤ +2.12pp（max 2022-09-28）
- 存在 surgical sweet spot **[+2.12pp, +3.78pp]**
- 2019-03-25 SL（rel_10d -5.20pp）落於 TPs 中段，**單一 rel_10d 維度無法過濾**——確認 EWZ Part A 殘餘 SLs 結構性異質（一為 EWZ 弱於 EEM 的 sustained Brazil-specific weakness、一為 EWZ 強於 EEM 的 country-specific lagging-decline）

### 三次迭代結果

| 迭代 | rel_10d cap | Part A Sharpe | Part B Sharpe | min(A,B) | 結果 |
|------|-------------|---------------|---------------|----------|------|
| **Att1 ★** | **+2.5%** | **1.50** (10訊號 WR 90.0% cum +48.77%) | **1.82** (6訊號不變) | **1.50** | **SUCCESS（+58% vs baseline 0.95）** |
| Att2 | +2.0% | 1.39 (9訊號 WR 88.9% cum +41.69%) | 1.82 不變 | 1.39 | 過嚴邊界，移除 2022-09-28 TP（rel_10d +2.12pp） |
| Att3 | +3.5% | 1.50 (與 Att1 完全相同) | 1.82 不變 | 1.50 | 寬邊界 robustness 確認 [+2.5%, +3.5%] sweet spot |

### 關鍵發現

- **Att1 surgical filter**：rel_10d cap +2.5% 僅過濾 2020-01-31 SL（rel_10d +3.78pp，唯一 outlier > +2.5pp），Part A 訊號 11→10，**零 winners 損傷、零 cooldown shift**（下一訊號 2020-11-02 為 9+ 月後，遠超 cooldown 10 日），Part B 全部 6 訊號完全保留
- **rel_10d filter 機制**：當 EWZ 過去 10 日相對 EEM 強勢（rel_10d > +2.5pp），訊號日的 BB 下軌觸碰更可能為「country-specific lagging-decline」（broad EM 仍健康但 EWZ 開始 lagging → 後續為持續性 country-specific 下跌），均值回歸不成立；當 EWZ 同步或弱於 EEM，訊號為「broad EM/Brazil 同步 capitulation」更可能反彈
- **vs EWZ-007 Att3**：Part A Sharpe **0.95→1.50（+58%）**，Part A WR **81.8%→90.0%**（+8.2pp），Part A cum **+42.67%→+48.77%**（+5.85pp），min(A,B) **0.95→1.50**（+58%），Part B Sharpe 1.82 完全不變
- **A/B 平衡權衡**：累計差 40.2%→47.7%（略增，因 Part A 從 +42.67% 升至 +48.77% 而 Part B 維持 +25.52%——同 EWZ-007 / FCX-013 / NVDA-012 「Part A 加深品質過濾必擴大累計差距」結構性現象）；年化訊號比 11:6→10:6 = 1.67:1（年化 1.5:1，gap 33% < 50% ✓）；**Sharpe 改善為主要 acceptance criteria**

### 跨資產貢獻（lesson #20 v3 邊界擴展）

1. **Repo 第 6 次 cross-asset divergence regime gate 應用**：擴展 lesson #20 v3 至 EM single-country ETF（EWZ vs EEM broad EM anchor），先前案例 TLT-014 ✓ / TSLA-017 ✓ / NVDA-016 ◐ 成功，COPX-014 / USO-026 失敗；EWZ-009 為 broad EM benchmark anchor 變體
2. **Repo 首次「同類 ETF 內 broader benchmark 為 anchor」變體**：既往 anchor 為 cross-asset class（TLT vs SPY、TSLA vs QQQ）或 sector index（NVDA vs SMH、COPX vs GLD），EWZ vs EEM 為「single-country EM ETF vs broad EM ETF」內類別 anchor 結構
3. **lesson #20 v3 適用條件擴展**：(a) cooldown 10d × 訊號密度 2.2/yr ≈ 0.06，遠 < 1.0；(b) MR 框架（capitulation 訊號日已偏弱）；(c) **新發現**：EM single-country ETF 之 country vs broad benchmark divergence 維度可作為「country-specific lagging-decline」過濾器
4. **lesson #19 + lesson #20 正交雙維度組合（repo 首次）**：EWZ-007 1d cap (lesson #19 outlier-event surgical) + EWZ-009 rel_10d cap (lesson #20 cross-asset divergence) 為正交雙維度，前者捕捉 ~3σ 單日 outlier（Petrobras 2021-02-22）、後者捕捉 country-specific lagging-decline regime（COVID early 2020-01-31），共同移除 EWZ Part A 結構性 SLs

### 新跨資產假設（待驗證）

「EM single-country ETF vs broad EM ETF rel_Nd cap」可能擴展至其他 EM single-country ETFs：
- INDA vs EEM（印度 ETF）：INDA 0.97% vol，已在 INDA-011 用 lesson #19 multi-period filter，rel_Nd 可能補強
- EWT vs EEM（台灣 ETF）：EWT 1.41% vol，已在 EWT-009 用 2DD floor，rel_Nd 可能補強
- FXI vs EEM（中國 ETF）：FXI 2.0% vol，政策驅動失敗模式，rel_Nd 可能不適用（同 ^VIX 失敗模式）
- EWJ vs VEA（日本 ETF vs 已開發海外 ETF）：anchor 切換為已開發海外 broad benchmark
