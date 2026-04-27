# Cross-Asset Lessons Learned (Compact Rules)

> **用途**：沉澱跨資產共通發現，避免 Agent 在新資產上重複犯同樣的錯。
> 設計新實驗時，先讀本文件再動手。
> **詳細證據**（表格、反例、原因分析）見 [cross_asset_evidence.md](cross_asset_evidence.md)，僅在需要實作細節時才讀。

---

## 1. 訊號品質 > 訊號數量
<!-- freshness:
  derived_from: [TQQQ-002,TQQQ-009,GLD-007]
  validated: 2026-03-27
  data_through: 2025-12-31
  confidence: high
-->

放寬進場條件增加訊號，但品質下降往往抵銷數量優勢。

**規則**：不要為了「更多訊號」放寬門檻。先確認每一個新增訊號的品質。

---

## 2. Trailing Stop 取決於波動度
<!-- freshness:
  derived_from: [TQQQ-003,TQQQ-005,GLD-003,GLD-012,SIVR-002,SPY-001]
  validated: 2026-04-09
  data_through: 2025-12-31
  confidence: high
-->

Trailing stop 在低波動資產有效，在高波動資產反而摧毀報酬。啟動門檻必須接近或超過 TP，否則即使低波動也壓縮獲利。

**規則**：
- 日波動 ≤ 1.5%：可用 trailing stop，但啟動門檻必須 ≥ TP（啟動/TP 比 < 80% 時壓縮獲利）
- 日波動 1.5-3%：預設不用，需極謹慎測試
- 日波動 > 3%：禁用 trailing stop，使用固定 TP/SL

---

## 3. 成交模型的現實修正
<!-- freshness:
  derived_from: [TQQQ-008,TQQQ-010]
  validated: 2026-03-27
  data_through: 2025-12-31
  confidence: high
-->

從「訊號日收盤進場」改為「隔日開盤市價進場」後，IS 報酬下降 30-70%，但 OOS 更可信。

**規則**：所有新實驗必須納入成交模型。不要被無成交模型的 IS 數字誤導。

---

## 4. 進場參數敏感度 >> 出場參數
<!-- freshness:
  derived_from: [TQQQ-002,TQQQ-009,TQQQ-010]
  validated: 2026-03-27
  data_through: 2025-12-31
  confidence: high
-->

進場條件微小改動對績效影響 3-5 倍於出場參數。

**規則**：進場條件是策略命脈，調整時用 1% 步進逐步測試。出場參數可用較粗步進。

---

## 5. 趨勢濾波器 + 均值回歸 = 災難
<!-- freshness:
  derived_from: [GLD-005,SIVR-003]
  validated: 2026-03-27
  data_through: 2025-12-31
  confidence: high
-->

均值回歸本質上是在下跌中買入，濾掉下跌趨勢 = 濾掉好的進場機會。

**規則**：均值回歸策略永遠不加趨勢方向濾波器。如需減少假訊號，改用市場結構濾波（如 close position filter）。

---

## 6. 確認指標的邊際效益遞減
<!-- freshness:
  derived_from: [TQQQ-007,TQQQ-012,TQQQ-013,USO-006,USO-010~020,TSM-004,FCX-003,SIVR-006,SIVR-007,IWM-005,XBI-005,FXI-011,INDA-009,EEM-013,TLT-010,TLT-011,TLT-012,NVDA-010,CIBR-013]
  validated: 2026-04-26
  data_through: 2025-12-31
  confidence: high
-->

核心訊號已精確時，額外確認指標減少訊號數量而不提升品質。

**例外**：針對特定失敗模式的濾波器有效（如 GLD-007 ClosePos≥40% 移除仍在下跌的訊號、IWM-005 ClosePos 移除無反轉確認假訊號、XBI-005 ClosePos≥35%）。ClosePos 有效邊界約為日波動 ≤ 2.0%（GLD 1.1%、IWM 1.5-2%、XBI 2.0% 有效；SIVR 2-3%、FCX 2-4% 無效）。

**反例**：複合振盪器作為附加過濾器在「急跌+盤中反彈」結構資產上反向移除好訊號。**FXI-011 驗證 Connor's RSI（CRSI）在 FXI 上失敗**：CRSI ≤ 25 附加於 FXI-005 完整框架，訊號 26→18（-31%）但贏家 17→10（-41%）、輸家 9→8（-11%），系統性偏向移除贏家。根因：CRSI 三組件（RSI(3)、Streak_RSI(2)、%Rank(1d return,100d)）皆懲罰 1-2 日急跌+盤中反彈結構（RSI(3) 反彈快、streak 短、%Rank 不極端），而 FXI 的高品質訊號正屬此類型。

**反例 2（CCI 作為主訊號失敗）**：**INDA-009 驗證 Commodity Channel Index (CCI)** 作為均值回歸主訊號在 INDA 0.97% vol 上完全失敗（repo 首次 CCI 試驗）。三次迭代 min(A,B) -0.46/-0.03/-0.46 均遠低於 INDA-005 Att3 的 0.23。失敗結構與 lesson #20b RSI hook divergence 平行：INDA 2024-2025 Part B 為後峰持續下跌 regime，CCI(20) 長時間停留超賣區（<-100），每次迷你反彈觸發「CCI turn-up」後續跌停損。加嚴 CCI 至 -150（Att2）使 Part A 好訊號流失多於壞訊號（Sharpe 0.09→0.05），加 Pullback 下限（Att3）對 Part B 完全冗餘（下跌期訊號天然伴隨深 pullback）。**整合規則**：CCI turn-up 與 RSI Bullish Hook Divergence（URA-008、TLT-006）、Day-After Capitulation（URA-009/TLT-006）同屬「V-bounce ≠ genuine reversal」失敗家族。所有 oscillator hook 訊號（RSI/CCI/Stoch turn-up）在 post-peak slow-melt regime 中無區分力。

**反例 3（MACD 柱狀圖 turn-up 作為主訊號失敗）**：**EEM-013 驗證 MACD 柱狀圖多頭轉折**作為均值回歸主訊號在 EEM broad EM ETF 1.17% vol 上失敗（**repo 首次 MACD 試驗**）。三次迭代 min(A,B) 0/−0.02/0.00 均未勝過 EEM-012 Att3 的 0.34。Att1（MACD 柱狀圖零軸上穿 + 回檔 [-7,-3] + WR≤-70）Part A/B 各 0 訊號——零軸上穿嚴重滯後於 MR 進場時機（price 已恢復、WR 已回升）。Att2（MACD 柱狀圖 2 根連續 turn-up today>yesterday>day-2 且 yesterday<0 + 回檔 [-8,-2] + WR≤-75）Part A 8 訊號 WR 50% Sharpe −0.02（2022-2023 升息熊市 SL 集中：2019-05 貿易戰、2022-09/10、2023-02、2024-07 共 4 筆）/ Part B 3 訊號 WR 66.7% Sharpe 0.34。Att3（Att2 + **反向 ATR 過濾 ATR<1.10**）Part A 5 訊號 WR 60% Sharpe 0.19 / Part B 2 訊號零方差 100% WR Sharpe 0.00 / min 0.00。**新發現**：MACD 框架在 EEM 上偏好低波動環境（ATR<1.10），與 EEM-010 RSI(2) 框架的 ATR>1.15 方向完全相反——bear rally dead-cat bounce 伴隨 ATR 飆升，bull consolidation MR 為低 ATR。反向 ATR 過濾提升 Part A WR（50→60%）但仍無法突破 0.34 天花板。**擴展失敗家族**：MACD 雙 EMA 平滑雖優於 RSI(14) 點估計，仍無法解決 V-bounce 根本問題——lesson #20b 失敗家族擴展至 MACD，加入 RSI/CCI/Stoch hook、WVF capitulation、Key Reversal Day 同一 oscillator/price-action hook 失敗類別。

**規則**：只在確認能修復某個已知失敗模式時才加濾波器，不要隨意「加一個指標看看」。複合振盪器（CRSI 類）需先驗證資產的訊號結構與振盪器組件方向一致。**任何 oscillator hook 作為主訊號（MACD/CCI/RSI/Stoch turn-up）需先確認資產 Part A/B 兩段皆處於活躍 MR regime**——post-peak persistent decline regime 中 oscillator hook 必然失敗，平滑程度（MACD EMA > RSI/CCI 點估計）亦無法解決根本問題。

**反例 4（signal-day secondary filter 疊加 regime-level gate 失敗）**：**TLT-010 驗證 2DD floor / 2DD cap / ATR expansion 三類 signal-day filter** 疊加於 TLT-007 Att2（BB-width regime gate）之上全部失敗（repo 首次 TLT 2DD/ATR 測試）。三次迭代 min(A,B) -0.11 / 0.02 / -0.18 均未勝過 TLT-007 Att2 的 0.12。Att1 2DD floor <=-1.5%（lesson #19 方向）：Part A 6/33.3% 並引入 cooldown-shift 新 SL、Part B 移除 3/6 winners；Att2 2DD cap >=-2.0%（CIBR-012 方向）：移除近零到期但同時移除深 2DD 贏家並引入 cooldown-shift 新 SL；Att3 ATR(5)/ATR(20) >=1.05：Part B 崩潰至 1 訊號。**核心發現**：當 regime-level classifier（BB-width gate）已一次性切除 single-extreme-vol regime（2022 升息期）後，剩餘訊號流中 winners/losers 在 2DD、ATR 維度皆分布重疊，signal-day secondary filter 結構性無選擇力。**新 cross-asset 規則**：**rate-driven 資產在已套用 regime-level gate 後，signal-day secondary filters 結構性失效**——此規則平行於 URA/FXI 政策驅動 ETF 的 oscillator-hook 失敗家族（lesson #20b），擴展 lesson #6 邊界至「regime-gate-after secondary filter」類別。TLT 改進方向應為更精細的 regime-level classifier（BB-width 60d percentile dynamic regime、或動態隨 ATR 分位調整），而非 signal-day filter。

**反例 5（percentile-based dynamic regime gate 在 single-extreme-regime 資產上結構性失敗）**：**TLT-011 驗證 rolling percentile-based BB-width regime gate** 在 TLT 上全面失敗（**repo 首次 percentile-based BB-width regime gate 試驗於任何資產**）。三次迭代 min(A,B) -0.11 / 0.01 / 0.03 均未勝過 TLT-007 Att2 固定 5% 的 0.12。Att1（252d lookback + 50th pctile 純動態）Part A 24 訊號（vs TLT-007 Att2 12）/Sharpe -0.11 cum -7.76%——50th pctile 過寬，2022 升息期 trailing 252d 窗口被自身主導，中位數本身被拉高，「當日 <= 中位數」仍放行整片 2022 訊號流；Att2（504d lookback + 40th pctile 純動態）Part A 13 訊號/Sharpe 0.01——擴視窗 + 收緊閾值仍不足，504d 窗口 2022 仍佔 >50%；Att3（252d/40th + 絕對 BB<5% 雙閘門 AND）Part A 10 訊號/Sharpe 0.03——pctile 系統性移除 TLT-007 Att2 的 2 筆贏家（絕對 BB<5% 但相對近 252 日為高分位數的 calm regime 末期訊號），Part B 與 TLT-007 Att2 完全相同（6/83.3%/0.65/+9.07%）。**核心發現**：rolling percentile 在**單一持續 12+ 個月極端 vol regime**中**自我稀釋**——參考窗口被 regime 期間主導，percentile 失去 cross-regime 區分力；即使與絕對閾值組合，pctile 以「相對近期歷史」為基準錯誤標記 calm regime 末期好訊號為「相對高」而過濾之。**新 cross-asset 規則（精煉 lesson #6 + lesson #20b）**：**對於單一極端 vol regime episode 持續時間長於 percentile lookback 視窗 50% 的資產，rolling percentile-based regime gate 結構性失效**——固定絕對閾值為唯一有效解。與 FXI-013（多段中等 vol regime 下固定和動態皆失敗）互補，精煉 BB-width regime gate 三層適用邊界：(1) **單一極端且短於 lookback 50% 的 vol regime** → 動態 percentile 可行；(2) **單一極端且長於 lookback 50% 的 vol regime**（TLT 2022）→ 僅固定絕對閾值有效；(3) **多段中等 vol regime**（FXI）→ BB-width 所有型式皆失敗。TLT min 0.12 可能為其技術面策略結構性上限——除非引入 regime-prediction（非 classification）機制（forward-looking Fed 政策指標、30d-implied-vol 等 forward derived），否則現有框架內應停止「regime-classifier 精煉」方向。

**反例 7（ADX/DMI 作為 MR 主規範閘門在多 regime 高波動個股上結構性失敗）**：**NVDA-010 驗證 ADX(14)+RSI(2) MR 框架** 在 NVDA 3.26% vol 多 regime 個股上失敗（**repo 首次將 ADX/DMI 作為主規範閘門試驗於任何資產**）。三次迭代 min(A,B) 0.00 / 0.00 / -0.27 均未勝過 NVDA-004 / NVDA-006 的 0.47。Att1（ADX>=25 + +DI>-DI + RSI(2)<=15 + Pullback[-3%,-10%] + cd10）Part A 3/66.7%/0.26 / Part B 1/0%/0.00 zero-var SL —— **ADX>=25 強趨勢與 RSI(2)<=15 deep oversold 罕見共存**：RSI(2)<=15 需持續下挫，但持續下挫使 +DI<<-DI 必然違反方向過濾，多重綁定交集結構性狹窄（0.6 訊號/yr）；Att2（放寬 ADX>=20 + RSI(2)<=20 + PB[-2%,-12%] + cd8）Part A 8/62.5%/0.22 / Part B **1**/0%/0.00 —— Part B 仍卡 1 訊號：NVDA 2024-2025 深度修正（2024-08 -17%、2025-04 tariff -25%）違反 -12% pullback 上限、Close>SMA(50) 規範閘門、或 +DI>-DI（DMI 快速崩盤翻轉），**結構不匹配 Part B 的 deep-capitulation 機會**；Att3（移除 +DI>-DI + RSI(3)<=25 + PB to -15%）Part A 8/**37.5%**/-0.27（4 連續 SL！）/ Part B 2/0%/0.00 / min -0.27 —— **cooldown chain shift（lesson #19）**：移除 +DI>-DI 釋放原本被壓制的 4 訊號（2020-02-24 pre-COVID drop / 2021-02-23 Feb 修正 / 2021-12-06 post-COVID 反彈 / 2022-12-20 bear 反彈）全部 SL，+DI>-DI 提供真實品質過濾，naively 移除使框架退化（WR 62.5%→37.5%）。**核心發現**：(1) ADX>=25 與 RSI(2)<=15 罕見共存（RSI 下挫使 DMI 翻轉）；(2) ADX>=20 weak-trend 過於包容（納入震盪 2023 summer 使 MR 訊號隨機化）；(3) +DI>-DI 與 Close>SMA(50) 大部分時間冗餘但移除觸發 cooldown-shift；(4) ADX+RSI+SMA+Pullback+Close>Open+Cooldown 高約束相關性，放寬一條件不會比例增長訊號。**新 cross-asset 規則**：**ADX/DMI 作為主規範閘門對多 regime 高波動（>3% vol）個股的短期 MR 結構性無效**——擴展 lesson #20b 失敗家族至 trend-strength oscillator 類別，加入 RSI/CCI/Stoch/MACD hook divergence 作為多 regime 高波動個股的無效進場主過濾器。NVDA 結構性 Sharpe 上限約 0.5，2019-2023 多 regime（COVID + late-bull + bear + chop）變異使單一參數集難以同時優化 Part A/B；NVDA-004（BB Squeeze）/ NVDA-006（RS）維持全域最優（10 次實驗、31+ 次嘗試）。

**反例 6（trajectory-based regime gate 在 single-extreme-regime 資產上結構性失敗）**：**TLT-012 驗證 trajectory-based BB-width regime gate**（多日一致性 / 均值 / 收縮方向三種變體）在 TLT 上全面失敗（**repo 首次 trajectory-based BB-width regime gate 試驗於任何資產**）。三次迭代 min(A,B) 0.00 / -0.09 / -0.02 均未勝過 TLT-007 Att2 固定 5% snapshot 的 0.12。Att1（mode="all"，過去 4 日 BB 寬度皆 < 5%）Part A 11/45.5%/Sharpe 0.03 cum +0.43%、Part B **3 zero-var**/100%/Sharpe 0.00（3/6 Part B transition winners filtered！）/ min 0.00；Att2（mode="mean"，過去 4 日 BB 寬度均值 < 5%）Part A **17/47.1%/Sharpe -0.09**（新增 5 筆低品質升息邊緣訊號，「當下 BB > 5% 但 4 日均值 < 5%」）、Part B 3 zero-var（同 Att1）/ min -0.09，**雙向失敗**；Att3（mode="contracting"，當日 BB<5% AND 當日 BB ≤ 10 日前 BB）Part A 9/44.4%/-0.02、Part B 5/80%/0.52（回收 2 筆 transition winners 但仍失 1 筆）/ min -0.02。**核心發現**：TLT 的 Part B 高品質訊號具**「spike-to-calm transition」結構**——常發生於 TLT 剛從短暫 vol 升高回落至 calm regime 的時刻，任何要求「過去 N 日亦 calm」的 trajectory 規則（strict / mean）皆系統性移除這些高品質 transition 贏家；mean 模式額外對 Part A 過度放寬引入壞訊號；contracting 方向在 Part A 穩定低 vol 但日內震盪期間（2020-2021）系統性濾掉好訊號。**整合規則（精煉 lesson #6 + TLT-011 規則）**：**BB-width regime gate 的所有精煉變體（percentile-based TLT-011、trajectory-based TLT-012）在單一極端 vol regime episode 的利率驅動資產上皆結構性失敗——固定絕對閾值 + 單日 snapshot 為結構性最優**。TLT-011 + TLT-012 共同證明 regime-classifier 精煉方向全部失敗，確認 TLT min 0.12 為現有純技術面框架結構性上限，除非引入 regime-prediction 機制（forward-looking Fed 政策指標、30d-implied vol 等 forward derived），否則應完全停止 regime-classifier 精煉方向嘗試。

---

## 7. 波動度縮放法則（新資產入門）
<!-- freshness:
  derived_from: [GLD-007,SIVR-003]
  validated: 2026-03-27
  data_through: 2025-12-31
  confidence: high
-->

策略從低波動資產移植到高波動資產時，各參數按比例調整。以 GLD → SIVR（波動度約 1.5-2 倍）為例：

| 參數 | 倍率 |
|------|------|
| Pullback 門檻 | ~2.3x |
| SMA deviation | ~1.7x |
| TP | ~2x |
| SL | ~1.5x |
| Holding period | ~0.75x（更高波動 = 更快回歸）|
| Cooldown | ~1.4x |
| Slippage | ~1.5x（流動性較差）|

**規則**：新資產先算出相對 GLD 的日波動倍率，再按 1.5-2x 縮放各參數作為起點。

---

## 8. Part A / Part B 平衡是關鍵指標
<!-- freshness:
  derived_from: [SIVR-003,GLD-007,GLD-001,TQQQ-010]
  validated: 2026-03-27
  data_through: 2025-12-31
  confidence: high
-->

訊號頻率在 IS (Part A) 和 OOS (Part B) 之間的比例反映策略穩健性。

- 1.0-1.3:1 → 優秀
- 1.5-2.0:1 → 可接受，需觀察
- \> 3.0:1 → 危險，可能存在市場狀態依賴

**規則**：新策略必須檢查 A/B 訊號頻率比。比例 > 2:1 時應調查原因。

---

## 9. 各資產最佳策略速覽
<!-- freshness:
  validated: 2026-04-26
  data_through: 2025-12-31
  confidence: high
  note: NVDA-011 added 2026-04-26 (Capitulation-Depth Filter MR (RSI Oscillator Depth)，**repo 第 5 次 capitulation-depth filter 嘗試，repo 首次 >3% vol 高波動單一個股測試**——cross-asset port from IWM-013 Att3 success 方向). Three iterations all failed vs NVDA-004 / NVDA-006 min(A,B) 0.47. Att1 (vol-scaled IWM-011: RSI(2)<10 + 2DD<=-4.5% + ClosePos>=40% + ATR>1.10 + cd 8 + TP+7%/SL-7%/15d) Part A **5/40.0%/Sharpe -0.21** cum -8.32% (3 SLs: 2019-04-26 trade-war / 2021-02-23 Feb tech / 2022-09-01 Jackson Hole all multi-regime continuation traps) / Part B 2/100% std=0 Sharpe 0.00 cum +14.49% / min **-0.21** — 1.0/yr signal density (vs IWM-011 2.0/yr) statistically insufficient. Att2 (Att1 + 3d cap >= -6%, DIA-012/CIBR-012 cap direction) Part A 2/50%/-0.01 / Part B unchanged / min **-0.01** — 3d cap removed 2 SLs (deep-3d continuation) but also misfiltered 2022-08-09 TP (deep-3d capitulation reversal); 2021-02-23 SL retained as sharp 1d sub-3d-buildup. Att3 (Att2 + 1d cap >= -4%, DIA-012 dual-dim port) Part A 1/0%/0.00 / Part B unchanged / min **0.00** — **NVDA Part A high-quality winner (2020-01-27 pre-COVID) had deeper 1d than SL (2021-02-23)**, DIA-012 cap direction structurally **wrong** for NVDA: DIA Part A losers cluster deep 1d gap-down (cap effective), NVDA winners cluster deep 1d gap-down (cap misfilters winners), parallel to IWM-013 Att1 failure mode. **Core findings**: (1) vol-scaled IWM-011 MR framework structurally insufficient on >3% vol high-vol single stock — signal density (1.0/yr) insufficient + multi-regime randomization (parallel to TSLA-014 3.72% / FCX-011 3% Post-Cap MR cross-asset failure pattern); (2) DIA-012 cap direction structurally inverse on NVDA — winner-deep-1d vs loser-deep-1d structures cannot be unified; (3) NVDA structural Sharpe ceiling ~0.5 reconfirmed (NVDA-004 / NVDA-006 0.47 remain best). **Lesson #19 family boundary expansion**: (a) raw return cap direction vs oscillator depth direction selection depends on winners/losers raw return distribution: SL-cluster-deep-1d/2d/3d → cap effective (DIA, CIBR, SPY); winner-cluster-deep-1d/2d/3d → cap fails, oscillator dimension required (IWM, NVDA confirmed); signal density < 1.5/yr → both dimensions fail (NVDA-011 confirmation); (b) capitulation-depth filter vol upper bound between IWM 1.5-2% (SUCCESS) and NVDA 3.26% (FAIL). NVDA-011 = NVDA's 11th failed strategy type (after RSI(2) MR, BB Squeeze, Momentum Pullback, RS Pullback, RS Exit Opt, RS Param, MBPC, ADX/DMI, Capitulation-Depth Filter). NVDA-004 / NVDA-006 remain global optimum (11 experiments, 34+ attempts). IWM-012 added 2026-04-25 (BB Lower + Pullback Cap Hybrid Mode, **repo first BB-lower hybrid trial on US small-cap broad ETF**, three iterations all failed vs IWM-011 min 0.52). Att1 (BB(20,2.0) + 10d cap -10% + WR≤-80 + ClosePos≥0.40 + ATR>1.10) Part A 7/57.1%/Sharpe **0.23** / Part B 3/66.7%/Sharpe 0.31 / min 0.23 — BB(20,2.0) signal set non-overlapping with IWM-011 RSI(2) framework: missed 5 IWM-011 winners (2019-10-02/2020-02-28 COVID/2020-09-21/2022-05-10/2022-09-23 — shallow-oversold sharp-decline reversal signals not at BB lower band depth) while adding 2 winners; Att2 (BB(20,1.5) looser per EWZ-006 1.75% configuration) Part A 12/58.3%/Sharpe **0.20** / Part B 6/66.7%/Sharpe 0.24 / min 0.20 — looser BB introduced 3 SLs (2020-01-27 pre-COVID, 2022-05-06 Fed-pivot fear, Part B 2025-03-11), confirms EWZ 1.5σ success was due to higher 1.75% vol making 1.5σ equivalent to IWM 2.0σ distance; Att3 (BB(20,2.0) + tighter ClosePos≥0.50 + ATR>1.15) Part A 2/50%/Sharpe 0.49 (zero-var risk, 0.4/yr) / Part B 3/66.7%/Sharpe 0.31 / min 0.31 — over-tightening collapsed Part A from 7 to 2 signals losing statistical significance. **Core finding (structural)**: (1) IWM RSI(2)+2DD signal set captures "shallow-oversold sharp-decline reversal" with most signals not reaching BB(20,2.0) lower depth (~3-4% deviation), BB-lower captures "absolute deep retracement" — sets are complementary but non-overlapping; (2) IWM Russell 2000 small-cap broad ETF aggregates individual-stock event-driven noise at sector level (pre-COVID, Fed-pivot fear), structurally distinct from VGK/EWJ developed-broad, EWZ/EWT single-country EM, CIBR US sector market structures; (3) ATR>1.10 in IWM-011 effective filter for "slow-melt false signals", but on BB-lower signal set retains all original SLs with no selectivity gain. **New boundary rule extending lesson #16 / #52**: BB-lower hybrid mode applies to "structurally concentrated or genuinely-broad" ETFs (VGK/EWJ developed-broad, EEM EM-broad, EWZ/EWT single-country EM, CIBR US sector); **does NOT apply to individual-stock event-driven aggregating small-cap broad ETFs (IWM as first validation data point)**. Confirms [1.12%, 1.75%] vol as **necessary but not sufficient** condition — asset structure (individual-stock event aggregation vs true broad/concentrated ETFs) is also a key variable. IWM's 7th failed strategy type (after Pullback+WR, BB Squeeze breakout, SMA trend pullback, IWM/SPY relative weakness, pullback-range filtering, deep RSI(2) entry). IWM-011 Att2 remains global optimum (12 experiments, 40+ attempts). SPY-009 added 2026-04-25 (Signal-Day Capitulation-Strength Filter MR — **repo first 1d-return FLOOR (lower-bound capitulation requirement) as primary filter on any asset**, Att2 SUCCESS). Three iterations: Att1 (1d floor <= -0.5% only) Part A 10/100%/Sharpe **6.56** cum +32.50% / Part B 3/100%/std=0/Sharpe display 0.00 cum +9.27% / min(A,B)† Part A **6.56** (EWJ-003/EWT-008 convention, **+1138% vs SPY-005 0.53**) — 1d floor precisely filters all 4 Part A SLs (1d -0.09%~-0.30%) + Part B sole SL (2025-04-07 1d -0.18%); cost is removing 2 Part A 1d-shallow winners (2020-02-28 1d -0.42%, 2023-03-13 1d -0.14%), net effect +6/0; Att2 ★ (1d floor -0.5% AND 3d cap >= -8%, DIA-012 dual-dimension cross-asset port) **identical to Att1** — 3d cap completely non-binding given 1d floor (all winners passing 1d floor have 3d > -7.10%; the only 3d-cap-relevant signal 2025-04-07 already filtered by 1d floor); 3d cap retained as **future regime-shift safety layer** (if future signal has 1d > -0.5% but 3d <= -8%); Att3 (1d floor <= -0.7% stricter) Part A 8/100%/Sharpe 5.88 cum +24.89% — stricter floor removes 2 winners (2019-05-29 1d -0.67%, 2019-12-03 1d -0.67%) without filtering additional SLs; confirms -0.5% as structural sweet spot. **Repo first 1d FLOOR direction (opposite to DIA-012's 1d CAP direction)**. **Extends lesson #19 bidirectionality discovery to broad-ETF intra-category subdivision**: SPY and DIA both 1.0% vol broad ETFs sharing RSI(2) entry framework, but SLs in 1d dimension are structurally OPPOSITE — DIA SLs cluster 1d-deep (-2.5%, -2.2%) policy-shock continuation (cap-direction filter), SPY SLs cluster 1d-shallow (-0.09%~-0.30%) weak-tape drift (floor-direction filter). Cross-asset takeaway: single-asset failure mode cannot be directly cross-asset ported even within seemingly-identical asset categories (broad ETFs sharing volatility class and entry framework); requires individual trade-level SL distribution analysis. SPY's 9th experiment, replaces SPY-005 as global optimum. DIA-012 added 2026-04-24 (Capitulation-Depth Filter MR — **repo first 1d-return cap + 3d-return cap dual-dimension primary filter on any asset**, Att2 SUCCESS). Three iterations: Att1 (1d cap >= -2.0% only) Part A 12/91.7%/Sharpe **1.31** cum +32.47% / Part B 4/75%/Sharpe 0.47 unchanged / min(A,B) 0.47 (tied DIA-005) — 1d cap precisely filters 2/3 Part A SLs (2021-11-26 1d -2.52%, 2020-10-26 1d -2.24%) preserving all winners; Part B SL (2025-04-07 Trump tariff 1d -0.95%) is "shallow 1d + deep 3d" structure (overnight continuation), 1d cap cannot capture; Att2 ★ (1d cap -2.0% AND 3d cap -7%, dual-dimension) Part A unchanged 12/91.7%/Sharpe 1.31 (3d filter non-binding on Part A) / Part B **3/100%**/std=0/Sharpe display 0.00 cum +9.27% / min(A,B)† **= Part A 1.31** (EWJ-003/EWT-008 convention, **+178% vs DIA-005 0.47**) — 3d cap precisely filters Part B SL (3d -10.06%) preserving all winners (deepest winner 3d = 2020-02-28 -5.96%, 1pp safety margin); Att3 (1d cap -2.0% AND 3d cap -8%, robustness) **identical to Att2** — confirms 3d cap robust between -7% and -8%, all winners 3d > -7% and Part B SL 3d -10% deeper than both. **Repo first 1d-return cap + 3d-return cap dual-dimension primary filter trial on any asset**. Cross-asset finding: DIA SLs cluster on 1d/3d return dimensions (orthogonal to 2d), distinct from CIBR-012 (2d cap), EEM-014/INDA-010/USO-013 (2d floor) — two separate failure mechanisms (single-day news shock vs multi-day regime-shift) require **dual-dimension filter** on low-vol broad ETFs. A/B balance achieved: annualized cum gap 28.5% < 30% ✓, signal ratio 1.6:1 (38% gap) < 50% ✓. **Extends lesson #19 family**: 1d cap + 3d cap dual-dimension as third sub-rule for low-vol (~1.0% daily vol) broad ETFs with policy/news-shock SL clustering — joins (a) 2d cap CIBR-direction (deep-2DD SL clustering) and (b) 2d floor EEM/INDA/USO-direction (shallow-2DD SL clustering). DIA-012 Att2 becomes 12th DIA experiment and replaces DIA-005 as global optimum. TLT-012 added 2026-04-24 (Sustained Low-Volatility Regime MR — trajectory-based BB-width regime gate refinement, **repo first trajectory-based BB-width regime gate trial on any asset**). Three iterations all failed vs TLT-007 Att2 min 0.12: Att1 (mode="all" 4-day strict consistency) Part A 11/45.5%/**0.03** / Part B **3 zero-var**/100%/0.00 (3/6 Part B transition winners filtered — signals where TLT recovered from brief vol spike require "past-N-days-calm" rule systematically removes these high-quality transition signals) / min **0.00**; Att2 (mode="mean" 4-day mean) Part A **17/47.1%/-0.09** (mean condition admits 5 low-quality hiking-era edge signals where current BB>5% but 4-day mean<5%) / Part B 3 zero-var (same 3 removed) / min **-0.09** — bidirectional failure; Att3 (mode="contracting" lookback=10, today BB<5% AND today BB ≤ 10d-ago BB) Part A 9/44.4%/**-0.02** / Part B 5/80%/**0.52** (recovered 2 transition winners from Att1) / min **-0.02**. **Core finding (精煉 TLT-011 結論)**: TLT's high-quality Part B signals carry a **"spike-to-calm transition" structure** — they occur when TLT just recovered from brief vol spike into calm regime; any trajectory rule requiring "past N days calm" systematically removes these winners. **Combined TLT-011 + TLT-012 finding**: BB-width regime gate refinement variants (percentile-based TLT-011 + trajectory-based TLT-012) **both structurally fail** on TLT — fixed absolute threshold + single-day snapshot (TLT-007 Att2) is structurally optimal. **New cross-asset rule (精煉 lesson #6 + TLT-011 sub-rule)**: **BB-width regime gate 的所有精煉變體（percentile / trajectory）在單一極端 vol regime episode 的利率驅動資產上皆結構性失敗——固定絕對閾值 + 單日 snapshot 為結構性最優**. TLT's 12th failed strategy type (adds trajectory-based to percentile-dynamic). TLT min 0.12 confirmed as structural ceiling under current technical-only framework; regime-classifier refinement direction should completely stop — future attempts must introduce regime-prediction mechanisms (forward-looking Fed policy indicators, 30d-implied vol, macro nowcasting). TLT-007 Att2 remains global optimum (12 experiments, 35+ attempts). TLT-011 added 2026-04-24 (Dynamic BB-Width Percentile Regime MR, **repo first percentile-based BB-width regime gate trial on any asset**). Three iterations all failed vs TLT-007 Att2 min 0.12: Att1 (252d/50th pctile pure dynamic) Part A 24/50.0%/**-0.11** cum -7.76% / Part B 11/81.8%/0.55 / min -0.11 — 50th pctile too loose, 2022 hiking-era trailing 252d window self-dilutes; Att2 (504d/40th pctile pure dynamic) Part A 13/53.8%/**0.01** / Part B 11/81.8%/0.55 / min 0.01 — wider window + tighter threshold still insufficient; Att3 (252d/40th pctile AND absolute BB<5% hybrid) Part A 10/50.0%/**0.03** / Part B 6/83.3%/0.65 (identical to TLT-007 Att2) / min 0.03 — pctile filter systematically removes 2 TLT-007 Att2 winners (calm regime signals with low absolute BB-width but relatively high percentile rank). **Core finding**: rolling percentile in single-extreme-regime persistence self-dilutes (window dominated by regime, pctile loses cross-regime selectivity); even with absolute backup, pctile filters out good signals at regime-transition boundaries. **New cross-asset rule (refines lesson #6 + lesson #20b)**: **for assets with single-extreme vol regime episodes longer than 50% of percentile lookback window, rolling percentile-based regime gate structurally fails — fixed absolute threshold is the only viable solution**. Complements FXI-013 (multi-episode mid-vol regime: both fixed and dynamic fail), refining BB-width regime gate boundary into three tiers: (1) single extreme shorter than lookback 50% → dynamic percentile viable; (2) single extreme longer than lookback 50% (TLT 2022) → fixed absolute only; (3) multi-episode mid-vol regime (FXI) → all BB-width forms fail. TLT's 11th failed strategy type (Trailing/RSI2/Deep-Pullback/TP-wide/SL-wide/cd15/Breakout/Donchian/ROC/DayAfter/Pair-IEF/Yield-^TNX/2DD/ATR → TLT-011 adds percentile-dynamic). TLT min 0.12 may be structural ceiling — unless regime-prediction (not classification) mechanism introduced. TLT-007 Att2 remains global optimum (11 experiments, 32+ attempts). TLT-010 added 2026-04-24 (Capitulation-Confirmed Vol-Regime MR, repo first 2DD/ATR supplementary filter trial on TLT). Three iterations all failed vs TLT-007 Att2 min 0.12: Att1 (2DD floor <= -1.5%, lesson #19 direction) Part A 6/33.3%/**-0.11** + cooldown-shift new SL; Att2 (2DD cap >= -2.0%, CIBR-012 direction) Part A 9/55.6%/**0.02** — removes 3 near-zero expiries but also removes deep-2DD TP + cooldown-shift new SL; Att3 (ATR(5)/ATR(20) >= 1.05) Part A 7/42.9%/**-0.18** / Part B collapses to 1 signal. **Core finding**: signal-day secondary filter (2DD floor/cap, ATR expansion) structurally fails on TLT when layered on TLT-007 Att2 BB-width regime gate — TLT winners/losers overlap on all signal-day dimensions. TLT-007 Att2's success was from regime-level classifier (slicing out 2022 hiking cycle); remaining signal flow has no further selectivity. Extends lesson #6 + lesson #20b: rate-driven assets after regime-level gate application reject all signal-day secondary filters. TLT's 10th failed strategy type (after Trailing/RSI2/Deep-Pullback/TP-wide/SL-wide/cd15/Breakout/Donchian/ROC/DayAfter/Pair-IEF/Yield-^TNX, TLT-010 adds 2DD floor/cap/ATR). TLT future direction: refined regime-level classifier (BB-width 60d percentile dynamic regime) — NOT signal-day filter. TLT-007 Att2 remains global optimum (10 experiments, 29+ attempts).
  note: COPX-010 added 2026-04-23 (Post-Capitulation Vol-Transition MR, **repo first 2DD/1DD entry-time filter trial on commodity ETF**, cross-asset port from CIBR-012 Att3, 3 iterations all failed vs COPX-007 min 0.45). Trade-level analysis (n=21 Part A) reveals COPX winners/losers cannot be reliably distinguished by 2DD or 1DD direction. Att1 (2DD cap >= -5.5% CIBR direction) Part A WR 76.2%->61.1% Sharpe 0.08 — cap removed deep-2DD winners (COPX winners 2dRet typically deeper than losers, OPPOSITE to CIBR pattern). Att2 (2DD floor <= -3% EEM/INDA direction) Part A unchanged but Part B WR 80%->66.7% Sharpe 0.21 — filtered 5 shallow-2DD bull-market winners (2024-01-22, 2024-08-07, 2024-12-17, 2025-03-03, 2025-11-20). Att3 (weak-capitulation filter: skip if 1DD>-3% AND ClosePos>0.30, best of 3) precisely targeted 2 weak-capitulation losers (2019-05-06 1DD-2.12%/CP0.97, 2025-03-31 1DD-2.35%/CP0.81); Part A 0.38 / **Part B 0.57 unchanged** (filter+cooldown shift exchange 1W+1L for 1W+1L, A/B balance achieved cum diff 28.6%<30% signal ratio 1.9:1<50%) / min **0.38**. Part A degraded by cooldown chain shift (lesson #19) introducing 2019-05-13 new SL during 4-month trade war continuation. **REJECT CIBR-012 cross-asset hypothesis on COPX 2.25% vol commodity ETF** — CIBR 1.53% vol losers cluster deep 2DD (cap effective), COPX winners span deep+shallow 2DD (cap/floor both fail). Extends lesson #20b failure family to "single-day momentum filter" category on commodity ETFs — paralleling TQQQ-017 leveraged index failure. COPX-007 confirmed structural Sharpe ceiling for 2.25% vol commodity ETFs; any entry-time confirmation filter creates A/B regime asymmetry or gets neutralized by cooldown shift (10 experiments, 45+ attempts). TQQQ-017 added 2026-04-23 (Capitulation + Intraday/Acceleration/Multi-day Confirmation Filters on 3x leveraged tech ETF, three iterations all failed vs TQQQ-010 min 0.36). Att1 (ClosePos>=0.30) Part A 0.43 / Part B 0.13 / min 0.13 — ClosePos filter structurally removes Part B winners on high-vol leveraged ETF (TQQQ 5-6% vol keeps most capitulation days closing near Low; 5/7 TQQQ-010 Part B winners had ClosePos<0.30); Att2 (2-day return<=-10%) Part A 0.13 / Part B 0.49 / min 0.13 — 2DD filter removed 8 Part A winners vs only 2 losers (non-selective), acceleration is not the key discriminator for TQQQ capitulation signals; Att3 (Prev RSI(5)<30) Part A 0.34 / Part B 1.02 / min 0.34 — Prev RSI naturally satisfied on all TQQQ-010 Part B signals (identical signal set, Sharpe 1.02 unchanged), Part A marginal -0.02 (篩除比例無選擇性 30% losers vs 29% winners). **Extends lesson #20b failure family to "single-period confirmation" filter category on leveraged index ETFs**: single-day ClosePos / 2-day acceleration / prev-day RSI confirmation all fail to distinguish TQQQ-010's 6 Part A stop-losses from winners — their distributions overlap on all three dimensions. Mirrors oscillator-hook / day-after-reversal / strong-reversal-bar failures on policy-driven ETFs (URA/TLT/FXI). **Validates cross_asset_lesson #6 boundary**: ClosePos effective boundary ≤2% vol reconfirmed — TQQQ 5-6% vol fails decisively (capitulation-day intraday reversals happen next morning not same day, and cooldown shifts signal dates from winner day to next passing day as noise). **TQQQ-010 Part A Sharpe 0.36 reflects 3x leveraged ETF structural noise in extreme regimes** (std_return 6.92%), not a filterable feature — 2020 COVID + 2022 tech bear regime entries mechanically trigger -8% SL regardless of entry-day confirmation. TQQQ-010 remains global optimum (17 experiments across MR / trend-momentum-breakout / Gap-Down / single-period-confirmation five categories). FXI-013 added 2026-04-22 (Volatility-Regime-Gated MR, **repo first BB-width regime gate cross-asset port from TLT-007 Att2**). Three iterations all failed vs FXI-005 min 0.38: Att1 (FXI-005 full framework + BB(20,2) width/Close < 8%) Part A 5/60.0%/Sharpe **0.24** cum +5.76% / Part B 1 signal expiry -0.64% Sharpe 0.00 / min **0.00** — BB 8% over-tight (FXI 2% vol doubles TLT's BB ratio), only 2019-2020 early signals pass, 2021-2023 multi-regime crisis periods all blocked; Att2 (widen BB to 12%) Part A 16/50.0%/Sharpe **0.09** / Part B 3/66.7%/Sharpe 1.08 / min **0.09** — BB 12% too loose (FXI 2021/2022/2023 regimes have BB 7-11%), admits 7 SLs (2020-03/09, 2021-02/07/11, 2023-02) from regime-transition shocks; Att3 (BB 10% + dynamic 252d percentile < 50%) Part A 8/50.0%/Sharpe **0.04** / Part B 2/50.0%/Sharpe 0.68 / min **0.04** — percentile filter over-penalizes Part B 2025-01-13 TP winner. **Core finding — FXI vs TLT structural difference**: TLT 2022 hiking cycle is **single extreme vol regime episode** (BB width persistently > 5% carveoutable by fixed threshold); FXI 2019-2023 has **multiple overlapping mid-vol regimes** (trade war, COVID, regulatory crackdown, pandemic policy, weak recovery) with BB width distributions (7-12%) overlapping across good/bad signals — fixed AND dynamic BB thresholds both fail. **Repo first BB-width regime gate trial on policy-driven EM ETF**. Extends lesson #52: policy-driven single-country EM ETF rejects not only short-horizon reversal structures (BB Squeeze / BB Lower / Stoch / Failed Breakdown / Gap-Down / CRSI / Momentum Continuation) but also **volatility-regime classifier (BB-width regime gate)** — multi-regime overlap prevents any vol-based cross-regime signal discrimination. **New cross-asset rule**: BB-width regime gate requires asset to have **single extreme vol episode** cleanly separable (TLT 2022 ✓); fails on assets with **multi-regime overlap** (FXI validated, pending INDA/EWZ/URA). **Expected-success candidates** (pending validation): SPY/DIA/VOO (2020 COVID single extreme episode), TQQQ (2022 single tech bear); **expected-failure candidates**: other policy/event-driven single-country ETFs. FXI's 11th failed strategy type. FXI-005 remains global optimum (13 experiments, 42+ attempts). FCX-011 added 2026-04-22 (Post-Capitulation Vol-Transition MR, **repo 第 1 次 BB-lower + pullback-cap hybrid mode 於高波動單一個股試驗**，cross-asset extension from VGK-008/INDA-010/EEM-014/CIBR-012)。Three iterations all failed vs FCX-004 min 0.41: Att1 (BB(20,2)+PB cap-15%+WR≤-80+ClosePos≥40%+ATR>1.15, TP+6%/SL-7%/20d/cd10) Part A 3/66.7%/Sharpe **0.26** / Part B 5/40.0%/Sharpe **-0.23** / min -0.23 — Part B 2024-07-19 + 2024-12-13 both 1-3d fast SLs, signal-day filter insufficient on FCX ~3% vol; Att2 (+ 2DD cap ≥-5%, CIBR-012 direction) Part A 2/50%/-0.09 / Part B 2/50%/-0.09 / min -0.09 — cap removes 2021-06-16 TP winner alongside 2024-07-19 SL (FCX winners' 2DD spans -3%~-8%, no unidirectional selectivity); Att3 (+ 2DD floor ≤-5%, VGK/INDA/EEM direction) Part A 1/100%/zero-var / Part B 4/50%/~0 / min 0.00 — floor filters 2/3 Part A signals (density crashes to 0.2/yr). **Core finding**: FCX winners' 2DD distribution overlaps with losers, distinct from CIBR SLs concentrated deep 2DD or VGK SLs concentrated shallow 2DD. **Repo first BB-lower hybrid mode on high-vol single stock** — **extends XBI-010's 1.75% vol upper boundary to single-stock category** (previously established only on ETFs). Integrated rule (extends lesson #52): BB-lower + pullback-cap hybrid mode applies only to low-mid vol broad/sector/single-country ETFs (1.12%~1.75%); fails on XBI (2.0% ETF), FXI (policy EM), GLD/TLT (commodity/rate ETF), and now **FCX (~3% single stock)**. Open hypothesis: mid-low vol single stocks (~1.5-2% defensive stocks) untested. FCX's 9th failed strategy type. FCX-001 remains global optimum (11 experiments, 42+ attempts); FCX-004 remains execution-model optimum (min 0.41). GLD-013 added 2026-04-22 (Post-Capitulation Vol-Transition MR tested on GLD 1.12% vol commodity ETF, **repo 第 1 次 2DD floor 方向跨類別至商品 ETF 嘗試**，three iterations all failed vs GLD-012 Att3 min 0.48: Att1 (BB+cap-5%+ATR>1.15+2DD<=-1.5%) 1 signal Part A only / Att2 (relax to cap-7%+ATR>1.05+2DD<=-1.0%) Part A 8/75%/Sharpe 0.20 with 2 SLs (2021-02 real-rate rise + 2022-09 rate-hike accel) / Part B 2/100%/zero-var / Att3 (2DD<=-2.0% VGK-aligned) Part A 2 signals含 1 SL (2021-02 passed deep 2DD filter但仍停損) Sharpe **-0.69** / Part B 1/+3% zero-var. **Core failure root**: commodity ETF's declines are macro-driven (real rates/USD/inflation repricing) rather than equity capitulation dynamics; VGK-008 success depends on "SL 集中於 2DD 淺帶 -0.89~-1.68%" structure, but GLD SLs spread across all 2DD depths making floor filter non-discriminating. 2DD depth ≠ capitulation strength in commodity context (slow bleed can also have deep 2DD). **Extends Post-Capitulation Vol-Transition MR boundary**: pattern applies to **equity-like ETFs** (broad EM/EWJ/VGK/single-country EM/US sector CIBR) but **NOT to commodity ETFs** (GLD confirmed). GLD-012 Att3 remains global optimum (13 experiments). Implication: confirm target asset's decline dynamics are equity-capitulation style (not macro-repricing) before applying 2DD floor + BB lower hybrid entry. VGK-008 added 2026-04-22 (Post-Capitulation Vol-Transition MR：VGK-007 Att1 + 2DD floor 加深至 -2.0%，**repo 第 4 次 2DD floor 方向成功驗證**，繼 USO-013 / EEM-014 / INDA-010 後，首次已開發歐洲寬基 ETF 驗證). Three iterations Att2 success: Att1 (2DD floor <= -1.0%) Part A 8/75.0%/Sharpe **0.49** cum +12.06% / Part B 7/85.7%/Sharpe 0.78 / min **0.49**（崩壞 vs 基線 0.53）— -1.0% 過淺無法觸及 VGK SL 帶（-1.47%~-1.68%），僅過濾 1 筆淺 2DD 贏家；Att2 ★ (2DD floor <= -2.0%，與 INDA-010 Att3 同門檻) Part A 3 訊號 100% WR Sharpe **3.02** cum +8.74% / Part B 4 訊號 100% WR Sharpe **2.60** cum +11.94% / min(A,B) **2.60**（+390% vs VGK-007 Att1 的 0.53）/ A/B cum 差 **3.20pp**（26.8% 相對，<30% ✓）/ A/B 訊號比 3:4 = 1.33:1（<50% raw count ✓） — -2.0% 一次過濾所有 VGK-007 殘餘失敗交易（2023-03-13 SL -1.50%、2023-09-27 到期虧損 -1.68%、2024-10-31 SL -1.47%、2026-03-05 SL -0.89%）及 3 筆淺 2DD 邊際贏家，保留 7 筆訊號全部為深 2DD -2.10%~-4.06% 真 capitulation；Att3 (2DD floor <= -1.5%) Part A 7/71.4%/Sharpe **0.38** cum +8.27% / Part B 5/100%/Sharpe 2.94 cum +15.85% / min **0.38**（-28% vs 基線）— -1.5% 仍在 SL 帶內（2023-03-13 SL -1.50% 恰在邊界、2023-09-27 loss -1.68% 保留），新增 2 筆失敗訊號使 Part A WR 崩至 71.4%。**核心發現：VGK 的 2DD 門檻為「懸崖式」而非漸進式**——-1.0% 無效、-1.5% 劣化、-2.0%（-1.7%~-2.0% 等效）成功，因 SL 集中於 -1.47%~-1.68% 窄帶，僅深門檻可完全繞過此帶。**跨資產貢獻**：repo 第 4 次「2DD floor 方向」成功驗證，首次於已開發歐洲寬基 ETF 驗證；擴展 lesson #19 至 broad EM（EEM 1.17%）+ single-country EM（INDA 0.97%）+ developed European broad（VGK 1.12%）三類資產。驗證 INDA-010 跨資產假設：2DD floor 加深方向確實擴展至 low-vol defensive broad ETFs（VGK 驗證）。**新發現——「懸崖式」vs「漸進式」門檻特性**：VGK 的 SL 2DD 窄帶（寬 0.21pp：-1.47%~-1.68%）使 floor 門檻呈懸崖特性（一次跨越整個帶）；INDA/EEM 的 SL 2DD 寬帶使漸進式有效。實用建議：應用 2DD floor 前應先分析殘餘 SL 的 2DD 分布寬度。VGK 第 8 次實驗（25+ 次嘗試），VGK-008 Att2 成為新全域最優. XBI-013 added 2026-04-22 (Gap-Down Capitulation + Intraday Reversal MR, **repo 第 5 次 Gap-Down 試驗，首次 US 板塊 ETF 測試**，cross-asset port from IBIT-006 Att2). Three iterations all failed vs XBI-005 min 0.36: Att1 (Gap ≤ -1.0% primary + Close>Open + 10d PB [-5%,-15%] + WR ≤ -80, TP +3.0%/SL -3.0%/15d) Part A 8/50% WR Sharpe **-0.02** cum -0.77%（4TP/4SL，1-3 日出場）/ Part B 1/0% WR Sharpe 0.00 cum -3.10% / min **-0.02**；Att2 (Gap as supplementary filter on XBI-005 base + ClosePos ≥ 35%) Part A 3/66.7% WR Sharpe 1.39 cum +7.08% / Part B 1/0% WR Sharpe 0.00 / min **0.00** — Gap 濾波將 XBI-005 原 35/8 濾至 3/1（-90%）樣本過薄；Att3 (deep Gap ≤ -2.0% + wider pullback [-5%,-18%]) Part A 1/100% WR 零方差 / Part B 1/0% WR / min **0.00**. **Repo 5th Gap-Down Capitulation MR trial** — 1st US sector ETF test. **Failure family formalization** — Gap-Down pattern has four validated failure categories (extended 2026-04-22 by XBI-013): (1) TQQQ-016 (non-24/7 leveraged index ETF); (2) FXI-010 (policy-driven EM single-country ETF); (3) FCX-010 (commodity-linked single stocks); (4) **XBI-013 (US biotech sector ETF — FDA/clinical/merger events announced after-hours create persistent cross-session selling pressure, paralleling policy/commodity continuity failures)**. 整合規則：Gap-Down MR 需要 (a) 24/7 連續交易 underlying AND (b) 拋壓耗盡與當日 session 不相關聯——XBI 生技板塊兩者皆不符，事件常盤後宣告產生跨 session 持續拋壓。IBIT 為唯一合格 underlying；美國股票類別無論 underlying futures 是否近 24h 交易皆不符合 (b)。**新跨資產假設（待驗證）**：Gap-Down MR 可能僅適用於 pure-crypto ETFs（BTC/ETH/SOL spot）；不適用於任何有 macroeconomic/commodity/policy/event 暴露的美國 equity 類別。XBI 第 10 個失敗策略類型（後於突破、ROC 單獨、動量回調、配對、ATR 自適應、RSI(2)、BB-lower 混合、RSI hook divergence、capitulation-accel、Gap-Down）。XBI-005 仍為全域最優（13 次實驗、41+ 次嘗試）. INDA-010 added 2026-04-21 (Post-Capitulation Vol-Transition MR：INDA-005 Att3 + 2DD floor 加深至 -2.0%，**repo 第 3 次 2DD floor 方向成功驗證**，繼 USO-013、EEM-014 後 single-country EM ETF 首次). Three iterations Att3 success: Att1 (2DD cap >= -3.0% CIBR 方向) Part A 10 訊號 Sharpe **0.08** / Part B 5 訊號 Sharpe 0.21 / min 0.08 — CIBR 方向過濾 3 個 Part A TPs + 1 Part B TP 保留所有 SLs（INDA TP 集中於中等 2DD -2~-3%，非深 2DD）；Att2 (cap 放寬至 -4.0%) Part A 11/0.17 / Part B 7/0.31 / min 0.17 — 2020-02-03 COVID signal-day 2DD 僅 -2.5%~-3.0%（pre-crash 早期進場，真正 -4.4% 下跌在進場後），cap 方向無法捕捉；Att3 **SUCCESS（2DD floor <= -2.0% 加深方向）**: Part A 11 訊號 72.7% WR Sharpe **0.30** cum +10.51%（+30% vs INDA-005 Att3 的 0.23）/ Part B 4 訊號 75% WR Sharpe **1.48** cum +10.41%（+377%）/ min(A,B) **0.30** / A/B cum 差 **0.10pp**（vs 基線 3.22pp，幾乎消除）/ A/B 年化訊號比 2.2/yr vs 2.0/yr = 1.1:1（優秀）. **過濾動態**：Att3 加深 2DD floor 同時過濾 (a) pre-crash early-in-decline 訊號（2019-07-31 貿易戰 SL）、(b) post-peak slow-melt drift 訊號（2024-10-04 外資流出到期 / 2025-02-18 後峰 SL）、(c) 近零到期（2024-01-23 / 2025-01-13），僅代價為 2023-03-15 淺 2DD TP 被過濾。**擴展 lesson #19（2DD 雙向性）**：方向取決於殘餘 SL 的 2DD 結構；single-country EM（INDA 0.97% vol）與 broad EM（EEM 1.17% vol）失敗模式結構相似（均為 shallow 2DD drift），驗證 2DD floor 方向在 EM ETF 類別普適性。CIBR（深 2DD SL, in-crash）仍為 cap 方向；EM ETFs 一律 floor 方向。**擴展 lesson #20b（oscillator hook 失敗家族）邊界突破**：INDA-009 CCI / INDA-008 BB hybrid 均因 post-peak slow-melt regime 失敗，INDA-010 Att3 以 **2DD 深度濾波**（非 oscillator 基礎）繞過此結構限制——核心洞察：entry-time confirmation 失敗不等於 regime filtering 失敗，2DD 深度既可作 entry signal（lesson #18 急跌確認）也可作 regime proxy（shallow 2DD = slow melt drift regime）。**跨資產假設（待驗證）**：2DD floor 加深方向可能擴展至其他 low-vol single-country EM ETFs（FXI、EWT policy-side、EWZ commodity-side）與 low-vol defensive ETFs（XLU、TLT、VGK）的殘餘 slow-melt 失敗訊號；門檻縮放為 ~2.1σ（INDA -2.0% @ 0.97% vol）至 ~0.43σ（EEM -0.5% @ 1.17% vol）——縮放與 vol 非線性，取決於資產 slow-melt regime 頻率。INDA-010 Att3 成為新全域最優（10 次實驗、31+ 次嘗試）. EEM-014 added 2026-04-21 (Post-Capitulation Vol-Transition MR：EEM-012 Att3 + 2DD floor，**repo 第 2 次 2DD floor 方向成功驗證**，繼 USO-013 後 broad EM ETF 首次). Three iterations, **Att2 SUCCESS**: Att1 failed（直接移植 CIBR-012 2DD cap 方向 require 2DD >= -3.0%）Part A 4 訊號 50% WR Sharpe **-0.02** / Part B 3 訊號 66.7% WR Sharpe 0.34 / min -0.02 — 方向錯誤移除 TPs 保留 SLs；**Att2 SUCCESS（2DD floor <= -0.5% 反轉方向）**: Part A 5 訊號 80% WR Sharpe **0.73** cum +9.06% / Part B 4 訊號 75% WR Sharpe 0.56 cum +5.89%（同基線）/ min(A,B) **0.56**（+65% vs EEM-012 Att3 的 0.34）/ A/B cum 差 3.17pp / A/B 訊號比 1.25:1 / 僅過濾 1 筆 2021-11-30 SL（2DD +0.29%）; Att3 ablation（Att2 - ATR>1.10）Part A 8 訊號 50% WR Sharpe -0.02 / Part B 不變 / min -0.02 — ATR 必要，與 2DD floor 互補非冗餘。**核心跨資產發現（2DD 方向資產相依性）**：CIBR（深 2DD SL，in-crash）用 **2DD cap** 方向成功；EEM（淺 2DD SL，慢漂移）用 **2DD floor** 方向（反向）成功。檢查 EEM-012 Att3 殘餘 SLs 的 signal-day 2DD：2021-07-08 -2.19%、2021-11-30 **+0.29%**、2025-11-19 **-0.85%**（中位 -0.85%）；TPs 2DD 集中於 -1.47% ~ -3.88%，方向完全相反於 CIBR。**2DD 方向不可通用移植**，必須先檢查殘餘 SL 的 2DD 分布。Att1 失敗轉 Att2 成功為「反向驗證」教科書案例。擴展 lesson #19（2DD 雙向性）：方向取決於殘餘 SL 的 2DD 結構。**擴展 lesson #52（混合進場模式）**：在 broad EM ETF（EEM 1.17% vol）上 BB 下軌+回檔上限 hybrid 可再進一步以 2DD floor 精煉至 min 0.56。EEM-014 Att2 成為新全域最優。Repo 第 2 次 2DD floor 方向成功驗證（繼 USO-013 後，broad EM ETF 首次）。14 experiments, 37 attempts. CIBR-012 added 2026-04-21 (Post-Capitulation Vol-Transition MR, **repo first "2-day return cap" filter direction tested** — inverse of CIBR-004's "2DD floor" which failed). Three iterations, Att3 SUCCESS: Att1 failed (ATR peak ≥1.30 + today ≤1.20 structurally conflicts with CIBR-008 working ATR>1.15, only 1 signal/8yrs); Att2 failed (prior 10d ATR peak ≥1.25 removed 3 winners, only 1 of 2 losers filtered, prior ATR peak NOT correlated with winner/loser); **Att3 SUCCESS (2DD cap >= -4.0%)**: Part A 4 signals 75% WR Sharpe **0.49** (+26% vs CIBR-008 0.39) / Part B 3 signals 100% WR Sharpe 3.96 / min(A,B) **0.49** / A/B cum diff 1.64pp (vs CIBR-008's 6.43pp, meets <30% goal) / A/B signal count diff 25% (meets <50% goal). Core finding: **2-day return cap filter direction (MUST >= -4.0%) is INVERSE of CIBR-004's "2-day decline floor" (MUST <= -1.5%/-2.0%)** — floor direction failed, cap direction succeeds. Interpretation: deep 2DD (≤-4% = 2.6σ for 1.53% vol) signals "crash still accelerating" (in-crash entries structurally fail for MR), shallow 2DD (-2~-4%) signals "deceleration phase where MR bounces work". 2DD cap filters 2020-02-24 COVID precursor SL (2DD -4.1%) and 2 edge-case TPs while preserving 4 clean MR signals. **New cross-asset hypothesis (pending validation)**: 2DD cap filter may extend to other US sector ETFs / low-mid vol ETFs (XBI, XLU, IWM, COPX, VGK, EEM) using BB lower + cap hybrid pattern — especially those with Part A crash-day SL failures. Threshold likely scales with daily vol (CIBR 1.53% vol → -4.0% ~ 2.6σ; high-vol assets need deeper cap). Does NOT apply to: single-day acceleration-driven entries (TQQQ leveraged panic buys, IBIT gap-down capitulation where in-crash entry IS the edge). **Meta-lesson**: when an entry filter direction has been shown ineffective (e.g., CIBR-004's 2DD floor), inverting the direction may work as a timing/regime filter — this opens a novel filter design pathway beyond the "oscillator hook / range expansion / capitulation depth" family (all of which failed in lesson #20b). CIBR becomes 12th experiment with 36+ attempts, first success of a genuinely new filter direction since CIBR-008 hybrid. URA-011 added 2026-04-21 (Volume-Confirmed Capitulation MR, **repo 第 3 次 Volume Spike 作為主品質過濾器試驗** — 前兩次 USO-006 Att2 與 TSLA-012 Att1 均失敗). Three iterations all failed vs URA-004 min 0.39: Att1 (URA-004 entry + Volume(today)/Avg20(Volume) ≥ 1.5x) Part A 6/66.7%/**0.39** / Part B 6/66.7%/**0.39** / min **0.39 (完美 A/B 平衡但等同 URA-004)** — identical 6 signals, identical WR, identical cum +12.53%, identical 4TP+2SL structure, Volume filter creates A/B symmetry but does NOT break URA-004 quality ceiling; Att2 (Vol ≥ 2.0x + ClosePos ≥ 40%) Part A 2/50%/**0.04** / Part B 3/66.7%/0.39 / min **0.04 (collapse)** — tightening filter removes TPs more than SLs, Part A drops from 4TP+2SL to 1TP+1SL due to entry-date shift (lesson #19): 2020-02-27 TP date becomes 2020-02-28 SL date; ClosePos has no selectivity on policy-driven URA (parallels URA-007 ATR redundant-filter failure); Att3 (Att1 minus 2DD, Vol ≥ 1.5x alone) Part A 7/57.1%/**0.18** / Part B 6/66.7%/0.39 (identical to Att1) / min **0.18** — Volume and 2DD are structurally independent (not redundant), removing 2DD adds 2 Part A signals (2022-10-12 TP + 2023-03-10 SL) dropping WR to 57.1%; 2DD is completely non-binding on Part B Volume-spike signals (identical signal set as Att1). **Core findings**: (1) Volume as supplementary filter on saturated pullback+RSI(2)+2DD framework provides A/B symmetry but no quality enhancement — extends lesson #6 (diminishing returns of confirmation filters) to Volume category; (2) 2DD cannot be substituted by ATR (URA-007 Att2) or Volume (URA-011 Att3) — 2DD has real selectivity on Part A, remains non-bindable core element of URA-004 framework; (3) Volume + ClosePos combination fails on policy-driven URA (URA's event-driven capitulations often lack end-of-day buying structure). **Positive finding**: Att1 achieved URA series's first "perfect A/B symmetry" (identical 6 signals, identical WR, identical cum return) — this structure can serve as future sanity check: if filter produces A/B symmetry without Sharpe improvement, it is merely rebalancing not quality-enhancing. **Repo 3rd Volume Spike as primary filter trial** (USO-006 Att2 "Volume >1.3x" Part A regression failed / TSLA-012 Att1 "Volume >1.3x BB Squeeze" Part B signals halved failed), URA first. **New cross-asset hypothesis (pending validation)**: Volume supplementary filter on high-liquidity ETFs can create perfect A/B balance but cannot break underlying framework quality ceiling — validated on URA, pending SIVR/FXI/INDA cross-asset validation. URA's 11th failed strategy type (after pullback+WR, RSI(2), BB Squeeze, trend pullback, RS, vol adaptive, dual oscillator, RSI hook, day-after reversal, WVF capitulation, Volume-Confirmed Capitulation). URA-004 remains global optimum (11 experiments, 33+ attempts). FCX-010 added 2026-04-21 (Gap-Down Capitulation + Intraday Reversal MR, **repo first single-stock Gap-Down trial**, cross-asset port from IBIT-006 Att2). Three iterations all failed vs FCX-001 min 0.43: Att1 (Gap<=-2.0% + Close>Open + 10d PB [-6%,-18%] + WR<=-80 + TP+5%/SL-4%/15d/cd10) Part A n=9 WR 55.6% cum +7.77% Sharpe 0.21 / Part B n=2 WR 100% zero-variance Sharpe 0.00 / min 0.00 — 4 Part A SLs concentrated in 2019 trade war (May-07, Aug-06) + 2023 SVB banking crisis first-wave shocks, gap-down continues not capitulates; Att2 (+ ClosePos>=50% strong intraday reversal filter) Part A n=8 WR 62.5% cum +12.42% Sharpe **0.36** / Part B unchanged n=2 zero-variance Sharpe 0.00 / min 0.00 — ClosePos removes 1 weak-reversal SL (2023-02-24) but 3 policy-shock SLs remain, Part B 2024-2025 bull regime gap-down + strong reversal structurally rare; Att3 (tighten Gap<=-2.5% + pullback floor -8%) Part A n=5 WR 80% cum +16.52% Sharpe **0.87** (repo-first single-stock gap-down high Part A Sharpe) / Part B n=1 zero-variance Sharpe 0.00 / min 0.00, A/B signal annualized ratio 2.0:1 + A/B cum gap 69.7% violate balance goals (<50% + <30%). **Repo first Gap-Down Capitulation trial on single stock** — extends lesson #20a failure family: Gap-Down pattern requires NOT ONLY (a) 24/7 overnight continuous price discovery BUT ALSO (b) overnight selling pressure exhaustion uncorrelated with daytime policy/commodity-news continuity. FCX (copper-linked high-vol stock) has LME/SHFE/COMEX near-24h futures coverage satisfying (a), but copper price shocks (trade policy, USD, global demand) persist into US session and violate (b), paralleling FXI-010's Chinese policy continuity failure. **Failure family formalization** — Gap-Down pattern has four validated failure categories (extended 2026-04-22 by XBI-013): (1) TQQQ-016 (non-24/7 underlying — leveraged index ETFs on traditional equity markets); (2) FXI-010 (policy-driven EM single-country ETF — political news persists through US session); (3) FCX-010 (commodity-linked single stocks — commodity shocks persist through US session); (4) **XBI-013 (US biotech sector ETF — FDA/clinical/merger events announced after-hours create persistent cross-session selling pressure, paralleling policy/commodity continuity failures)**. Currently ONLY IBIT (pure BTC 24/7 spot ETF) validates, indicating structural prerequisites are strict and non-transferable across categories — the prerequisite set is now empirically strict: (a) 24/7 continuous price discovery AND (b) overnight selling exhaustion uncorrelated with next-session policy/commodity/event flow. No US equity category satisfies (b) regardless of underlying futures coverage; US sector ETFs fail via (4) even if sector is event-driven rather than policy-driven. **Cross-asset hypothesis (pending validation)**: Gap-Down MR may apply ONLY to pure-crypto ETFs (BTC/ETH/SOL spot) where underlying trades 24/7 on retail/global exchanges with selling pressure truly exhausting overnight; NOT to any US equity with macroeconomic/commodity/policy exposure (even if underlying futures trade near-24h). **FCX's 9th failed strategy type** (after pullback+WR+ClosePos variants, BB Squeeze Breakout success FCX-004, momentum pullback, RS FCX-COPX, Donchian breakout, trend pullback, ATR vol adaptive, RSI hook divergence, Gap-Down Capitulation). **FCX-001 remains global optimum** (10 experiments, 39+ attempts). FXI-012 added 2026-04-21 (Momentum Breakout Pullback Continuation, **repo first absolute momentum continuation trial on FXI**). Three iterations all failed vs FXI-005 min 0.38: Att1 (Donchian 20d new high within last 5d + Close>SMA50 + 5d shallow pullback [-2%,-5%] + RSI(14) ∈ [40,60] + cd 10, TP+4%/SL-3.5%/15d) Part A 26 signals WR 42.3% cum -9.96% Sharpe -0.09 / Part B 12 signals WR 58.3% cum +9.42% Sharpe 0.24 — Part A 2019-2023 China bear market false breakouts dominate (15/26 SLs, 1-7d fast stops); Att2 (+ SMA(20)>SMA(50) golden cross + tighten RSI [45,58]) Part A 16 WR 43.8% Sharpe -0.11 / Part B 10 WR 70.0% Sharpe **0.55** (+129% vs Att1, exceeds FXI-005 Part A Sharpe 0.38) — golden cross boosts Part B but **cannot filter Part A bear-rally false breakouts** (2019 trade war / 2021 regulatory / 2023 weak recovery all had short-term golden cross followed by reversal); Att3 (+ SMA(50) slope positive: today > 60d ago, remove golden cross) Part A 8 WR 37.5% Sharpe -0.21 / Part B 9 WR 55.6% Sharpe 0.26 / min -0.21 — **counterintuitive finding**: SMA slope filter WORSENS both parts — FXI's best momentum continuation signals occur during regime-transition periods (2022 Q4 reopening early phase, 2024 Q3 stimulus early phase) when SMA(50) slope still negative but about to turn; by time slope turns positive, best entry is missed. **Repo first absolute momentum continuation trial on FXI** (FXI-007 was RS momentum vs EEM, different concept). **Three iterations reveal**: absolute momentum continuation (Donchian + pullback) structurally fails on policy-driven single-country EM ETFs — China policy shocks cluster in regime-transition periods where ALL trend filters (Close>SMA, SMA crossover, SMA slope) are lagging indicators. **Extends lesson #25 (RS momentum failure)** with new finding: absolute momentum continuation also rejected on FXI; **extends lesson #52** with trend-continuation structure rejection — FXI suffers dual structural rejection: neither reversal (BB lower/BB squeeze/Stoch/CRSI/failed breakdown/gap-down) NOR continuation (momentum breakout pullback) structures generalize. **Cross-asset hypothesis (pending validation)**: absolute momentum continuation may work on **non-policy-driven** single-country ETFs (EWT semiconductor-driven, EWZ commodity-driven) but should be added to禁忌 for policy-driven single EM country ETFs (FXI, possibly INDA policy side). FXI's 10th failed strategy type (after BB Squeeze, RSI(5), BB Lower MR, RS momentum, Stoch, Failed Breakdown, Gap-Down Capitulation, CRSI, FXI-001 symmetric exit). FXI-005 Att3 remains global optimum (12 experiments, 36+ attempts). CIBR-011 added 2026-04-20 (Range Expansion Climax MR, **repo first traditional US sector ETF Range Expansion as primary signal trial** — refutes IBIT-008's cross-asset hypothesis "Range Expansion MR may work on traditional non-24/7 US sector ETFs"). Three iterations all failed vs CIBR-008 Att2 min 0.39: Att1 (TR/ATR(20) ≥ 2.0 + ClosePos ≥ 50% + 10d PB [-3%,-10%] + WR(10) ≤ -70 + cd 8) Part A 3 signals 33.3% WR cum -4.81% Sharpe **-0.44** (2020-02-24 COVID precursor + 2020-09-04 TP + 2021-09-20 Evergrande SLs) / Part B 2/2 100% WR cum +7.12% zero-variance Sharpe 0.00 — signal scarcity 5 signals in 8 years (0.6/yr); Att2 (TR ≥ 1.7 + tighten cap to -8% + ATR(5)/ATR(20) > 1.10) Part A 2 signals 50% WR Sharpe -0.08 / Part B 2 signals 50% WR Sharpe **-0.29** — ATR > 1.10 filter REMOVES Part B 2024-02-21 + 2024-08-05 winners (both ATR ratio < 1.10 environment) and shifts to 2025-03-04 SL + 2025-08-01 expiry; Att3 (REVERSE ATR ratio ≤ 1.10 testing "calm regime + sudden TR expansion = real capitulation" hypothesis paralleling EEM-013 reverse ATR finding) Part A 2 signals 0W/2L **WR 0%** cum -8.03% (2021-05-04 + 2021-09-20 SLs) / Part B **0 signals** / min 0.00 — reverse ATR also fails: removes ALL Part B signals while preserving Part A bear-regime continuation SLs. **Repo first Range Expansion MR trial on traditional US sector ETF** — refutes IBIT-008's cross-asset hypothesis. Range Expansion failure family extends from (a) high-vol 24/7 crypto ETF (IBIT 3.17%) to (b) mid-vol traditional US sector ETF (CIBR 1.53%). Core finding: **ATR filter has NO unidirectional efficacy on CIBR Range Expansion** — forward ATR (>1.10) systematically removes winners (4/4 Part B winners filtered), reverse ATR (≤1.10) systematically preserves losers (Part A WR 0%), indicating ATR is noise for this signal type, not quality. Integrated lesson: ALL entry-time filter types (oscillator hook RSI/CCI/Stoch/CRSI/MACD, day-after price-action reversal, capitulation-depth WVF, single-bar range expansion) structurally fail on event-driven sector ETFs that lack statistical-adaptive entry framework (BB Lower with std auto-scaling). The two structural prerequisites for entry-time filter validity: (1) statistical-adaptive primary signal (BB std auto-scaling, not single-bar point estimate), AND (2) signal frequency ≥ 1.5/yr per part to enable WR-based discrimination. Range Expansion fails both. CIBR's 7th failed strategy type (after BB Squeeze, RSI(2), RS momentum, Key Reversal Day, NR7, 2DD-as-supplement-filter, Range Expansion). CIBR-008 Att2 remains global optimum (11 experiments, 33+ attempts). IBIT-008 added 2026-04-20 (Range Expansion Climax MR, **repo first single-bar TR expansion as primary signal**). Three iterations all failed vs IBIT-006 Att2 min 0.40: Att1 (TR/ATR(20) ≥ 2.0 + ClosePos ≥ 50% + 10d PB [-6%,-20%] + WR(10) ≤ -70) Part A n=1 TP zero-var / Part B n=1 SL / min 0.00 — signal trigger rate 0.4% (2/500 trading days); Att2 (relax TR 1.5 + ClosePos 40%) Part A n=1 unchanged — pullback/WR binding in 2024 bull regime / Part B n=4 WR 25% Sharpe **-0.53** — loosened ClosePos captures bear rally dead-cat bounces; Att3 (keep TR 2.0/ClosePos 50%, loosen pullback to -4%/WR to -65) Part A n=1 / Part B n=1 **identical to Att1** — pullback/WR completely NON-BINDING, confirming TR ≥ 2×ATR + ClosePos ≥ 50% itself implies deep pullback and extreme oversold. **Repo first single-bar Range Expansion as primary MR signal trial** (TLT-006 used range expansion as auxiliary filter only). Extends lesson #20b failure family beyond oscillator-hook (RSI/CCI/Stoch/CRSI/MACD) + day-after reversal (URA-009) + capitulation-depth (WVF) to **single-bar range-expansion climax indicators** — all entry-time confirmation patterns structurally fail on high-vol crypto ETFs in post-peak/bear regimes. Three failure modes identified: (1) signal scarcity — TR/ATR(20) ≥ 2.0 + ClosePos ≥ 50% is structurally rare on IBIT's 2-year history (year triggers ≤ 1); (2) no true/false reversal discrimination — Att2's relaxed ClosePos 40% treats bear rally bounces as capitulation; (3) structural difference from Gap-Down (IBIT-006 Att2) — Range Expansion lacks "overnight flushout completion" precondition that makes Gap-Down effective on 24/7 underlyings. Cross-asset hypothesis: Range Expansion MR may work on traditional (non-24/7) US sector ETFs (CIBR/XBI) where overnight gaps are absent and single-bar TR expansion represents primary capitulation structure — pending validation. IBIT's 8th failed strategy type (after RSI(2), BB Squeeze, trend momentum, RSI(5) trend, ATR vol adaptive, 2-day decline, 20d lookback/short momentum, Keltner Lower). IBIT-006 Att2 remains global optimum (8 experiments, 24+ attempts). EEM-013 added 2026-04-20 (MACD Histogram Bullish Turn + Pullback Hybrid MR, **repo first MACD trial**). Three iterations all failed vs EEM-012 Att3 min 0.34: Att1 (MACD hist zero-cross entry) Part A/B both 0 signals — zero-cross lags MR entry timing by several days; Att2 (MACD hist 2-bar bullish turn + pullback [-8,-2] + WR≤-75 + ClosePos≥40%) Part A 8 signals 50% WR -0.77% Sharpe **-0.02** (4 TP / 4 SL, 2022-2023 rate-hike bear SLs concentrated) / Part B 3 signals 66.7% WR +2.80% Sharpe 0.34 — MACD smoothing insufficient to resolve V-bounce; Att3 (Att2 + **reverse ATR filter: ATR(5)/ATR(20) < 1.10**) Part A 5 signals 60% WR +2.60% Sharpe 0.19 / Part B 2 signals 100% WR zero-variance Sharpe 0.00 / min(A,B) 0.00. **Novel cross-asset finding**: MACD framework on EEM prefers LOW ATR (opposite of EEM-010 RSI(2) framework ATR>1.15) — bear-rally dead-cat bounces coincide with ATR spikes, bull-consolidation MR has lower ATR. Reverse ATR filter successfully removed 3 Part A SLs with ATR>1.10 (2019-05-15 ATR 1.47 / 2022-10-03 ATR 1.14 / 2024-07-29 ATR 1.11) but also removed 2 Part A TPs with ATR>1.10 (2019-08-12 ATR 1.15 / 2021-10-06 ATR 1.12), net WR 50%→60% still below required 70% threshold. **Repo first MACD trial** — extends lesson #20b failure family (V-bounce ≠ genuine reversal) to MACD histogram turn patterns: MACD's EMA-based smoothing insufficient to solve V-bounce root problem in post-peak persistent decline regimes (2022-2023 Fed hiking). Adds MACD to the oscillator-hook failure list alongside RSI (URA-008, TLT-006, FCX-009, COPX-009, XBI-011, USO-022), CCI (INDA-009), Stoch (FXI-008), CRSI (FXI-011), and WVF (URA-010). EEM's 13th strategy type tested (after RSI(2), vol adaptive, pullback+WR, BB Squeeze, RS momentum, trend momentum pullback, optimized breakout, ATR SL, strict decline ATR, no ClosePos ATR, BB lower + cap, MACD). EEM-012 Att3 remains global optimum (13 experiments, 34+ attempts). URA-010 added 2026-04-20 (Williams Vix Fix Capitulation MR, repo first WVF trial). Three iterations all failed vs URA-004 min 0.39: Att1 (WVF(22)>BB_upper(20,2.0) + 10d PB [-8%,-25%], cd=10) Part A 23/65.2%/0.33 / Part B 11/45.5%/**-0.06** — 6/11 Part B SLs concentrated in continued declines (2024-02/06/10 + 2025-02/10/11), WVF spike captures "panic-mid-decline" not actual bottoms; Att2 (+ 2DD ≤ -3%) Part A 21/61.9%/0.25 / Part B identical (11/45.5%/-0.06) — 2DD non-binding (WVF spike inherently implies recent decline), Part A regressed; Att3 (+ deepen pullback floor to -10%, URA-004 standard) Part A **13/76.9%/0.68** (URA series in-sample best, +106% vs Att1) / Part B 8/50%/0.04 (positive but A/B cum diff 50pp). **Repo first WVF trial** — extends lesson #20b failure family beyond oscillator-hook (RSI/CCI/Stoch/CRSI) and price-action-bar (day-after reclaim) to **capitulation-depth indicators** (WVF). URA's policy-driven nature (核能政策/俄烏鈾供應) makes any entry-time filter (oscillator turn-up / single-bar reversal / capitulation depth metric) fail in Part B 2024-2025 V-shaped + post-rally crash regime ("event-driven asset rejects all entry-time confirmation filters"). Att3's Part A Sharpe 0.68 reveals "WVF + deep pullback" generates high-quality in-sample signals when active MR regime exists in both parts — cross-asset hypothesis: pattern may apply to SIVR/COPX where Part A/B both have active MR regime; will fail on FXI/TLT (policy-driven, parallel URA Part B). URA's 10th failed strategy type. URA-004 remains global optimum (10 experiments, 30+ attempts). INDA-009 added 2026-04-20 (CCI Oversold Reversal MR, repo first CCI trial). Three iterations all failed vs INDA-005 Att3 min 0.23: Att1 (CCI(20)≤-100 + turn-up + Close>Open, cd10) Part A 21 signals 61.9% WR Sharpe 0.09 / Part B 9 signals 44.4% WR Sharpe **-0.46** — Part B 2024-2025 INDA post-peak slow-melt decline (~58→~45) sees CCI persistently in oversold, every mini-rally triggers turn-up followed by continued decline (4/9 immediate SLs); Att2 (CCI≤-150 + ClosePos≥40%) Part A 9 signals 55.6% WR Sharpe 0.05 / Part B 3 signals 66.7% WR Sharpe -0.03 — tightening reduces signals but filters out more winners than losers (Part A Sharpe drops 0.09→0.05), sample too sparse (1.5/yr); Att3 (CCI≤-100 + ClosePos + Pullback≥2.5%) Part A 17 signals 58.8% WR Sharpe 0.06 / Part B 9 signals 44.4% WR Sharpe -0.46 — core insight: Part B signals all already carry ≥2.5% pullback (decline regime), making pullback floor filter zero-effect on Part B. **Repo first CCI trial** — extends lesson #20b failure family (V-bounce ≠ genuine reversal): CCI turn-up from oversold shares the oscillator-hook failure mode of RSI Bullish Hook Divergence on post-peak persistent decline regimes. **New cross-asset hypothesis**: CCI mean reversion requires both Part A/B in active MR regime (not post-peak slow-melt) — parallels URA-008/TLT-006 failures on policy-driven assets. INDA's 9th failed strategy type. INDA-005 Att3 remains global optimum (9 experiments, 28+ attempts). FXI-011 added 2026-04-20 (Connor's RSI Mean Reversion, first repo trial of CRSI = mean of RSI(3)+Streak_RSI(2)+PercentRank(1d return,100d)). Three iterations all failed vs FXI-005 min 0.38: Att1 (CRSI≤10 + PB 4-12% + ClosePos + ATR + cd10) Part A 6 signals 50% WR Sharpe 0.01 / Part B 2/2 100% WR Sharpe 4.14 — over-restrictive (23% signal retention, 50% WR vs 65.4% baseline); Att2 (CRSI≤20 + PB 4-12% + ClosePos, drop ATR/WR) Part A 16 signals 56.2% WR Sharpe 0.12 / Part B 4/4 100% WR Sharpe 5.36 — CRSI replaces WR but selects WORSE: removed 8 wins / 2 losses, dis-favoring 1-day-flush signals; Att3 (FXI-005 framework + CRSI≤25 as additional filter) Part A 18/55.6% WR Sharpe 0.17 / Part B 3/3 100% WR Sharpe 4.74 — 41% wins removed vs 11% losses, confirming CRSI systematically penalizes high-quality signals. **Core failure mode**: FXI's profitable MR signals are 1-2 day flushes with rapid intraday recovery, but CRSI's three components all penalize this profile — RSI(3) bounces back fast on 1-2 day flushes, streak length only -1/-2, %Rank not extreme on 1d -3% drops in policy-driven environments. CRSI truly fires on multi-day slow-melt declines, which FXI-005's ATR+WR+ClosePos already filter out. **Extends lesson #6 boundary**: CRSI as additional MR filter on policy-driven single-country EM ETFs systematically removes winners faster than losers, violating the "specific failure-mode filter" exception. Adds 9th failed strategy type to FXI (after BB Squeeze, RSI(5), BB Lower MR, RS momentum, Stoch, Failed Breakdown, Gap-Down Capitulation). **Repo first CRSI trial**: cross-asset hypothesis — CRSI may still work on low-vol broad ETFs (SPY/DIA/VOO ≤1.0% vol) where reversals involve 3-5 day gradual processes rather than 1-day flushes; does NOT apply to policy/event-driven single-country ETFs (FXI, URA, TLT class), high-vol crypto ETFs (IBIT class), high-vol stocks (TSLA/NVDA class). FXI-005 remains global optimum (11 experiments, 33+ attempts). IBIT-007 added 2026-04-19 (Keltner Channel Lower Band MR, three iterations all failed vs IBIT-006 Att2 min 0.40: Att1 Keltner 2.0×ATR + PB [-8%,-25%] + Close>Open + cd=10 → Part A 2/2 zero-var WR 100% cum +9.20% Sharpe 0.00 / Part B 3 signals 33% WR cum -3.97% Sharpe -0.31 — Keltner triggers fire DURING continued declines (2025-02-28 & 2025-11-18 both immediate SL) not at capitulation bottoms that gap-down filter captures; Att2 add WR(10)+deepen PB to -10% → identical signal set (Keltner trigger already implies extreme oversold/deep pullback, additional filters non-binding); Att3 Keltner 2.5×ATR + WR(5)≤-80 → Part A 0 signals (too restrictive), Part B 1/1 zero-variance Sharpe 0.00. **Core failure mode**: Keltner Lower Band (EMA-k×ATR) cannot replicate gap-down capitulation structural asymmetry (BTC overnight selling pressure completion → US-session bargain hunting); Keltner fires based on close-vs-EMA distance in ATR units, a LAGGING indicator of oversold depth rather than a LEADING indicator of capitulation completion on 24/7 underlying. **New cross-asset observation**: Keltner Lower Band MR (GLD-005 success on 1.12% vol) does NOT generalize to high-vol crypto ETF (IBIT 3.17% vol) — the volatility-adaptive threshold triggers during slow-melt declines rather than capitulation moments; suggests Keltner MR effective boundary at daily vol ≤ 1.5%. IBIT's seventh failed strategy type (after RSI(2), BB Squeeze breakout, trend momentum pullback, RSI(5) trend pullback, ATR vol adaptive/2-day decline, 20d lookback/short momentum, SL-8%). IBIT-006 Att2 remains global optimum (7 experiments, 21+ attempts). CIBR-010 added 2026-04-19 (NR7 Volatility Contraction + Pullback MR: pullback -4% + WR(10)≤-80 + NR7 + ClosePos≥40%, three iterations all failed vs CIBR-008 Att2 min 0.39: Att1 (NR7 alone) Part A 7/71.4% Sharpe 0.39 / Part B 3/33.3% Sharpe -0.44 — NR7 alone cannot distinguish genuine capitulation from consolidation during slow-melt declines on event-driven sector ETF; Att2 (add ATR>1.15) signals collapse to 1/2 Sharpe 0.00/-0.08 — **structural conflict**: NR7 requires today's TR to be min of 7 days, ATR(5) includes today, making the ratio mechanically depressed; Att3 (add 2-day decline ≤-2% instead of ATR) signals collapse to 1/1 zero-variance — **structural conflict 2**: 2-day drop ≥2% usually implies one of those days has a wide range, nearly mutually exclusive with NR7. First repo trial of NR7 / Narrowest Range 7 pattern — confirmed volatility contraction patterns (typically used in day-trader coiled-spring breakouts) do NOT transfer to multi-day mean-reversion frameworks on event-driven US sector ETFs (CIBR cybersecurity). CIBR's 6th failed strategy type. **New cross-asset hypothesis**: NR7/inside-day volatility contraction patterns structurally incompatible with ATR and 2DD quality filters, limiting their composability on pullback+WR frameworks. CIBR-009 added 2026-04-19 (Key Reversal Day price-action MR: Pullback + WR + Prev 收黑 + stop-run + reclaim + bullish bar + ClosePos + ATR, three iterations all failed vs CIBR-008 Att2 min 0.39: Att1 (WR≤-80, no ATR, with stop-run) Part A 8/50% WR Sharpe -0.08 / Part B 3/33.3% WR Sharpe -0.44, 2022 three consecutive SLs + 2025 two SLs all washout-then-continue; Att2 (+ATR>1.15) signals shrink to 2/2 with 2025-02-28 ATR 1.44 still 1-day SL; Att3 (remove stop-run, WR≤-85, ATR>1.10) signals crash to 1/1 both SL Sharpe 0.00. Extends XBI-012 failure pattern to CIBR: short-period single-day price-action reversal confirmation (stop-run + reclaim + bullish bar) fails on event-driven US sector ETFs (XBI biotech / CIBR cybersecurity). Integrated rule: **美國事件驅動板塊 ETF 拒斥所有短週期 price-action 反轉結構**, requires volatility-statistical indicators (BB 下軌+ATR) + absolute pullback cap filter (CIBR-008 / EWJ-003 hybrid pattern). 9 experiments, 27 attempts. XBI-012 added 2026-04-19 (Capitulation + Acceleration Reversal MR: Pullback(10) + ROC(3) + ClosePos + UpDay + WR, three iterations all failed vs XBI-005 min 0.36: Att1 (ROC -4%/ClosePos 50%/UpDay) 3/3 signals 0.16/0.16 too restrictive; Att2 (ROC -3%/ClosePos 40%/UpDay) Part A 0.27 +69% but Part B stuck at 0.16 because 2024-2025 XBI bull regime has sparse ROC(3) ≤ -3% events; Att3 (ROC -3%/ClosePos 35%/no UpDay) signals triple to 21/8 but quality collapses to 0.18/0.07, confirming UpDay filter is essential for quality. Ninth failed strategy type on XBI (after breakout, ROC alone, momentum pullback, pairs, ATR-adaptive, RSI(2), BB-lower hybrid, RSI hook divergence). Extends XBI structural finding: pullback(10)+WR+ClosePos 35% is the unique optimal primary entry trigger — any alternative trigger (ROC, BB, RSI hook) that shifts signal dates fails to generalize across Part A/B regimes. 12 experiments, 38+ attempts. XBI-011 added 2026-04-18 (RSI(14) Bullish Hook Divergence tested on XBI 2.0% vol 10-day pullback+WR+ClosePos framework, three iterations all failed vs XBI-005 min 0.36: Att1 (5/3.0/35 SIVR canonical) 3/2 signals all +3.50% TP zero-variance Sharpe 0.00; Att2 (5/3.0/40 loosen max_min) Part A 7 signals 2 stop-losses Sharpe 0.27; Att3 (5/2.0/35 loosen delta) identical to Att1 because max_min=35 is binding. Extends lesson #20b with 6th criterion: signal-day RSI(14) distribution must concentrate in deep oversold (≤35). XBI biotech pullback+WR signals land in RSI(14) 35-45 range due to FDA/clinical event-driven compressed 1-2 day declines that don't saturate RSI, while SIVR's persistent macro-driven declines do reach ≤35. Refines post-XBI cross-asset hypothesis: event-driven sector ETFs fail the hook pattern regardless of vol/framework/regime compliance; TSLA event-driven stocks likely also fail. 11 experiments. FXI-010 added 2026-04-18 (Gap-Down Capitulation + Intraday Reversal MR ported from IBIT-006 Att2, three iterations all failed to beat FXI-005 min 0.38: Att1 (gap≤-1.5% entry trigger + tight exit TP+3.5%/SL-3%) min -0.51 (22 signals 31.8% WR, FXI gap-downs often continue not capitulate); Att2 (gap≤-2.5% + close>midpoint + deep pullback + FXI-005 wide exit) min 0.00 (signals crashed to 5/1); Att3 (gap as 5d regime filter + FXI-005 entry) Part A 0.34 / Part B 0.00 zero-variance with 2 signals, A/B signal ratio 4.4:1. Double-extends lessons #52 and #20a: (a) policy-driven EM rejects gap-down capitulation structure as both entry trigger AND regime filter — adds to the BB Squeeze/BB lower MR/Stoch cross/failed breakdown reclaim rejection list; (b) Gap-down capitulation pattern requires not just "overnight continuous price discovery" (which FXI has via HK market) but ALSO "selling pressure uncorrelated with policy/event continuity" — FXI has the former but Chinese policy news persists through US session, invalidating the buy-the-dip structure. URA-009 added 2026-04-18 (Day-After Capitulation + strong reversal bar confirmation tested on URA, three iterations all failed: Att1 (WR≤-85+2DD≤-4%+Close>PrevClose+Close>Open) min -0.25 / Att2 (Close>PrevHigh reclaim) min 0.24 with perfect A/B balance but ~1/yr / Att3 (loosen to URA-004 thresholds + keep strong reversal) min -0.11 as WR collapsed to 43%, all vs URA-004 0.39. Extends lesson 20b failure mode: day-after price-action bar confirmation (even "reclaim prior high") on policy/event-driven URA still fails by "V-bounce ≠ genuine reversal" principle. Att2's A/B perfect balance (0pp cum diff, 60%/60% WR) confirms day-after framework is symmetry-preserving but the inherent ceiling of URA capitulation reversal trading appears to be URA-004 itself. URA-008 added 2026-04-18 (RSI(14) Bullish Hook Divergence tested on URA 10-day pullback framework with active Part A/B MR regime, three iterations all failed: Att1 URA-004 base + hook min 0.00 / Att2 remove 2DD min 0.00 / Att3 SIVR-015 structure with WR(10) min -0.32 Part B WR 33.3%, all vs URA-004 0.39. URA formally meets all four criteria (2.34% vol, 10d PB, active Part A/B MR regime in URA-004, validated pullback+WR framework) but hook filter reduces signals 24/16→6/3 (retention 25% vs SIVR 44%), Part B 2025-11-05 signal stops out next day confirming V-bounce ≠ genuine reversal on policy-driven uranium. Refines lesson 20b to five conditions: adds "asset must have RSI-turn=genuine-reversal structure" requirement, excluding event/policy-driven assets (URA nuclear, FXI policy, TLT rates) even when volatility/framework/regime formally met. FCX-009 added 2026-04-18 (RSI(14) Bullish Hook Divergence tested on FCX 10-day pullback framework, three iterations all failed: Att1 delta=3 min -0.33 / Att2 delta=5 min -0.06 / Att3 delta=5+pullback-11% min 0.30, all vs FCX-001 0.43. FCX formally meets pattern 20b's lookback ≤10 constraint, but Part B signals dwindled 5→3→2 through iterations as 2024-2025 post-peak copper decline eliminated active MR regime. Part A Sharpe surged 0.51→0.76→0.85 confirming hook filter raises signal quality, but Part B cum diff 39-51pp consistently exceeded 30% target. Extends lesson #20b boundary: requires Part A/B both in active mean-reversion regime, not post-peak secular decline. COPX-009 added 2026-04-18 (RSI(14) Bullish Hook Divergence tested on COPX 20-day pullback framework, three iterations all failed: Att1 ATR+hook5 min -0.50 / Att2 ATR+hook10 min 0.00 / Att3 no-ATR+hook10 min 0.15, all vs COPX-007 0.45. Extends lesson #20b boundary: bullish hook divergence requires pullback lookback ≤10 days — 20-day framework causes prolonged declines where RSI hooks up-down multiple times, making hook filter capture local noise rather than true capitulation end. Part A WR crashes from 76.2%→33.3% (Att1) / 57.1% (Att2) / 64.3% (Att3). SIVR-015 added 2026-04-17 (RSI(14) Bullish Hook Divergence + SIVR-005 entry: pullback 7-15% + WR(10)<=-80 + RSI(14) self-risen from 5d-min by ≥3 points where 5d-min ≤ 35, TP+3.5%/SL-3.5%/15d). Att1 new global best min(A,B) 0.22→0.48 (+118%), Part B Sharpe 0.26→1.41 (+442%). First repo validation of classical bullish divergence pattern. Att2 (lookback 7/delta 2) too loose, Part A regressed 0.28; Att3 (RSI(7)) noisy, both parts negative. RSI(14) is the correct period for SIVR divergence. Pattern may generalize to other mean-reverting assets — cross-asset validation pending. FXI-009 added 2026-04-17 (Failed Breakdown Reversal / Turtle Soup, 3 iterations all failed: Att1 breakdown_lookback=10 min 0.00 / Att2 lookback=5 + ClosePos min -0.11 / Att3 lookback=10 + 1% depth Part A signals dried up. Extends lesson #52 to Turtle Soup structure: policy-driven single-country EM ETFs reject all short-horizon reversal structures (BB Squeeze, BB Lower, Stoch crossover, failed breakdown reclaim). FXI-005 remains global optimum at min(A,B) 0.38. TQQQ-016 added 2026-04-17 (Gap-Down Capitulation MR ported from IBIT-006, 3 iterations all failed: Att1 gap-3% min -0.07 / Att2 gap-2% min -0.07 / Att3 +volume min -0.07, all vs TQQQ-010 0.36). Validates lesson #20a boundary: pattern does NOT extend to leveraged tech ETFs on traditional (non-24/7) underlying. Att3 Part A Sharpe 0.49 (+36% vs TQQQ-010) but Part B unchanged at -0.07 due to 2025-04-07 Trump tariff gap-down continuing to decline. 16 experiments. EEM-012 added 2026-04-17 (BB Lower + Pullback Cap Hybrid MR: BB(20,2.0) + 10d PB cap -7% + WR(10)<=-85 + ClosePos>=40% + ATR(5)/ATR(20)>1.1 + TP+3%/SL-3%/20d/cd10, Att3 min(A,B) 0.34 +89% vs EEM-005 0.18, first validation of hybrid pattern on broad EM ETF category, extends lesson #52 scope beyond single-country EM. Att2 ATR>1.15 reverse-failed: crisis-day ATR spike means tighter ATR preserves losers not winners — WR is the key quality axis for EEM hybrid, 12 experiments). IBIT-006 added 2026-04-17 (Gap-Down Capitulation MR: Gap<=-1.5% + Close>Open + 10d PB [-12%,-25%] + WR(10)<=-80 + TP+4.5%/SL-4%/15d/cd10, Att2 min(A,B) 0.40 +167% vs IBIT-001 0.15, first structural entry improvement leveraging BTC 24/7 overnight gap + US session buying pattern; Att3 ablation confirmed gap-down filter is prerequisite for tight SL -4%, 6 experiments). FXI-008 updated 2026-04-17 (Stochastic Oscillator MR tested on FXI, three iterations Att1 %K>%D cross 0.16 / Att2 %K level 0.34 / Att3 WR+Stoch dual osc 0.37 all failed vs FXI-005 min 0.38, confirmed Stoch Oscillator adds no value over WR(10) for policy-driven EM single-country ETF). CIBR-008 updated 2026-04-16 (BB lower band + pullback cap -12% hybrid, min(A,B) 0.27→0.39, +44%, 8 experiments). EWJ-003 updated 2026-04-16 (BB lower band + pullback cap hybrid, Part A Sharpe 0.55→0.60, 3 experiments). VGK-007 updated 2026-04-16 (BB lower band + pullback cap -7% hybrid, min(A,B) 0.45→0.53, +18%, 7 experiments, resolves VGK-004 A/B imbalance 37.5%→8.2%). EWZ-006 updated 2026-04-16 (BB lower band 1.5σ + pullback cap -10% hybrid, min(A,B) 0.34→0.69, +103%, 6 experiments, first commodity-driven EM single-country ETF to validate hybrid pattern). XBI-010 updated 2026-04-17 (BB lower band + pullback cap hybrid tested on biotech ETF 2.0% vol, three iterations all failed to beat XBI-005 min 0.36, confirmed hybrid pattern effective upper boundary at daily vol ≤1.75%, 10 experiments). INDA-008 updated 2026-04-17 (BB lower band + pullback cap hybrid tested on India ETF 0.97% vol, three iterations all failed to beat INDA-005 min 0.23, confirmed hybrid pattern effective lower boundary at daily vol ≥1.12%, 8 experiments). FXI-007 updated 2026-04-17 (RS momentum FXI vs EEM tested, three iterations min -6.63~0.16 all failed vs FXI-005 min 0.38, confirmed single-country EM RS momentum pattern failure extends to China, 7 experiments). EWJ-004 updated 2026-04-17 (RS momentum EWJ vs EFA/SPY tested on DM single-country ETF, three iterations min -0.24~0.15 all failed vs EWJ-003 min 0.60, extended single-country RS momentum failure pattern from EM to DM, 4 experiments). EWT-008 updated 2026-04-17 (BB lower band 2.0σ + pullback cap -8% hybrid tested on Taiwan ETF 1.41% vol semiconductor-driven EM single-country, Att1 min(A,B) 0.57† vs EWT-007 RS momentum 0.42, +36% Part A Sharpe, confirmed hybrid pattern effective in [1.12%, 1.75%] vol range extends to EM semiconductor-driven single-country ETFs, 8 experiments). †EWJ/EWT min(A,B) uses Part A Sharpe as binding constraint — Part B Sharpe formally 0.00 due to zero variance (EWJ 6/6, EWT 3/3 trades returned identical +3.50%). FCX-012 added 2026-04-23 (Donchian Lower Washout + Intraday Reversal MR, **repo first "Donchian Lower touch + intraday reversal" combo as MR primary entry**, three iterations all failed vs FCX-004 min 0.41). Att1 (baseline Close within 2.5% of Donchian_Low(20) + today or yesterday Low=20d low + ClosePos>=40% + ATR>=1.10 + 60d DD [-30%,-10%] + TP+9%/SL-11%/20d/cd15) Part A 8/50%/-0.06 / Part B 6/50%/0.02 / min -0.06 — two Part A -11% SLs (2019-08-05 trade war, 2023-04-25 drift) are continuation-decline traps, Part B dominated by small expiries shows washout signal lacks sideway trigger momentum; Att2 (+today Low > yesterday Low = Day-After Capitulation) Part A 1 zero-var / Part B 2/Sharpe 1.07 / min -0.60 (single-trade approximation) — over-filters to 3 signals, **validates lesson #20b Day-After Capitulation failure family extending to FCX 3% vol single commodity stock** (third data point after URA 2.34% / TLT 1%); Att3 (revert Att2, +2DD cap >= -7%, CIBR-012 direction) Part A 7/42.9%/-0.20 WORSE than Att1 / Part B 6 unchanged / min -0.20 — cap removes 1 TP winner (not SL), FCX winners' 2DD distribution spans -3%~-8% overlapping with losers (same pattern as FCX-011 Att2). **Extends lesson #52 to "Donchian Lower binary price trigger" category**: single-day Donchian Low touch + intraday reversal insufficient to distinguish "tail-of-washout" from "mid-acceleration" in multi-stage declining assets — parallels FXI-009 Failed Breakdown Reversal failure. FCX's 12th failed strategy type; FCX-004 remains execution-model optimum (min 0.41), FCX-001 remains global optimum (grandfathered, Sharpe 0.43/0.74)
-->

| 資產 | 最佳實驗 | 策略類型 | min(A,B) Sharpe | 全域最優確認 |
|------|----------|----------|-----------------|-------------|
| TQQQ | TQQQ-010 | 極端恐慌買入 | 0.36 | 16 次實驗 ✓ |
| GLD | GLD-012 Att3 | 20日回調+WR（無追蹤停損）| 0.48 | 13 次實驗 ✓ |
| SIVR | SIVR-015 Att1 | 回檔+WR+RSI bullish hook divergence | 0.48 | 17 次實驗 ✓ |
| FCX | FCX-001/FCX-004 | 三重極端超賣/BB Squeeze | 0.43/0.41 | 12 次實驗 ✓ |
| USO | USO-013 | 緊密回檔+RSI(2)+2日急跌 | 0.26 | 22 次實驗 ✓ |
| SPY | SPY-009 Att2 | RSI(2) + **1d FLOOR + 3d cap 雙維度** | 6.56† | 9 次實驗 ✓ |
| DIA | DIA-012 Att2 | RSI(2) + **1d cap + 3d cap 雙維度** | 1.31† | 12 次實驗 ✓ |
| VOO | VOO-004 Att3 | **Donchian 突破 + 5d 內 + 窄帶淺回檔（MBPC）** | 1.12† | 4 次實驗 ✓（**repo 首次 MBPC 成功**） |
| SOXL | SOXL-010 Att3 | 板塊 RS 動量回調 | 0.70 | 11 次實驗 ✓ |
| TSM | TSM-008 | RS 出場優化 | 0.79 | 9 次實驗 ✓ |
| IWM | IWM-013 Att3 | Capitulation-Depth Filter MR (RSI<8 oscillator depth) | 0.59† | 13 次實驗 ✓ |
| XBI | XBI-005 | 回檔範圍+WR+反轉K線 | 0.36 | 12 次實驗 ✓ |
| COPX | COPX-007 | 波動率自適應均值回歸 | 0.45 | 10 次實驗 ✓ |
| URA | URA-004 | 回檔範圍+RSI(2)+2日急跌 | 0.39 | 11 次實驗 ✓ |
| NVDA | NVDA-004 | BB 擠壓突破（優化）| 0.47 | 11 次實驗 ✓（NVDA-009 MBPC 三次失敗 / NVDA-010 ADX-Filtered RSI(2) MR 三次失敗，repo 首次 ADX/DMI 主過濾器試驗 / NVDA-011 Capitulation-Depth Filter MR 三次失敗，repo 首次 >3% vol 高波動單股測試 lesson #19 family）|
| IBIT | IBIT-006 Att2 | Gap-Down 資本化+日內反轉 MR | 0.40 | 8 次實驗 ✓ |
| TSLA | TSLA-015 Att3 | BB 擠壓突破 + **buffered multi-week SMA regime**（SMA(20)≥0.99×SMA(60)） | 0.53 | 15 次實驗 ✓ |
| TLT | TLT-007 Att2 | 回檔+WR+反轉K線+**BB 寬度 regime 閘門**（<5%）| 0.12/0.65 | 12 次實驗 ✓（TLT-010 2DD/ATR 補充濾波三次失敗；TLT-011 percentile-based dynamic regime 三次失敗；TLT-012 trajectory-based regime 三次失敗，固定絕對閾值 + 單日 snapshot 為結構性最優）|
| EEM | EEM-014 Att2 | BB 下軌+回檔上限+WR+ClosePos+ATR+**2DD floor ≤-0.5%**（混合進場+2DD floor 精煉）| 0.56 | 14 次實驗 ✓ |
| EWJ | EWJ-003 Att3 | BB 下軌+回檔上限+WR+ATR（混合進場）| 0.60† | 4 次實驗 ✓ |
| EWT | EWT-008 Att1 | BB 下軌+回檔上限+WR+ClosePos+ATR（混合進場）| 0.57† | 8 次實驗 ✓ |
| VGK | VGK-008 Att2 | BB 下軌+回檔上限+WR+ClosePos+ATR+**2DD floor <=-2.0%**（VGK-007 + 2DD floor 精煉）| 2.60 | 8 次實驗 ✓ |
| XLU | XLU-011 | 波動率自適應均值回歸 | 0.67 | 11 次實驗 ✓ |
| INDA | INDA-010 Att3 | 回檔+WR+ClosePos+ATR+**2DD floor <=-2.0%**（EEM 方向加深）| 0.30 | 10 次實驗 ✓ |
| FXI | FXI-005 Att3 | 出場優化均值回歸（TP5.5%/SL5%/20d）| 0.38 | 13 次實驗 ✓ |
| EWZ | EWZ-006 Att3 | BB 下軌+回檔上限+WR+ClosePos+ATR（混合進場）| 0.69 | 6 次實驗 ✓ |
| CIBR | CIBR-012 Att3 | BB 下軌+回檔上限-12%+WR+ClosePos+ATR+**2DD cap ≥-4.0%** | 0.49 | 12 次實驗 ✓ |

> 各實驗詳細參數、探索歷程和確認邏輯見 [cross_asset_evidence.md](cross_asset_evidence.md) Section 9。

---

## 10. 反覆失敗的做法（禁止清單）
<!-- freshness:
  validated: 2026-04-17
  data_through: 2025-12-31
  confidence: high
-->

以下做法在多個資產上證明無效，新實驗不應再嘗試：

### 通用禁忌
1. **放寬進場門檻以增加訊號** — 品質下降速度永遠快過數量增加
2. **高波動資產上使用 trailing stop** — 日內震盪觸發悲觀認定出場
3. **均值回歸策略加趨勢方向濾波** — 邏輯上自相矛盾
4. **已精確訊號上疊加確認指標** — 減少訊號但不提升品質
5. **無成交模型的 IS 數字當參考** — 高估 50-120%
6. **不同波動度資產直接複製參數** — 必須按波動度比例縮放
7. **成交量過濾** — 對任何策略類型（均值回歸、突破）均無效
8. **降低 TP** — 達標交易必經低 TP，降低只壓縮利潤
9. **K線方向過濾在均值回歸中** — 好訊號不一定出現在空方K線日
10. **回復日進場** — 與均值回歸進場條件（極端超賣+急跌）邏輯衝突
11. **日報酬 z-score 自適應進場** — 缺乏最低回檔深度門檻，產生大量錯誤進場
12. **Close-based 回檔** — 降低深度過濾力，不如 High-based
13. **收窄回撤範圍（微調1-3%）** — 改變訊號日期而非增減訊號，效果不可控

### 指標相關禁忌
13b. **T-1 單日報酬過濾器在突破策略上（TSLA-013 驗證）** — 突破策略中 T-1/T-2 單日報酬過濾器因 cooldown-chain-shift 結構性失敗：訊號數不變但 Part A 績效退化（TSLA-013 Att1/2：Part A Sharpe 0.40→0.29、cum +64%→+36%）。BB Squeeze 要求近期低波動使 T-1 下限非綁定（Att2 下限 -20% 與 Att1 下限 -3% 結果完全相同），所有過濾效果來自上限。僅適用 MR 策略（已成功案例：USO-013/EEM-014/INDA-010/CIBR-012/DIA-012）
14. **VIX 閾值過濾均值回歸進場** — VIX 在熊市持續偏高，過濾掉牛市好訊號
15. **SMA 偏離作為額外過濾器** — 嚴重損害品質
16. **RSI(14) 動能回復** — 本質是確認指標變形，移除好訊號多於壞
17. **ADX 趨勢強度過濾** — 在均值回歸中移除好訊號多於壞訊號
18. **RSI(5) 雙時框確認** — 在精確訊號上有害
19. **累積 RSI(2)** — 不優於單日 RSI(2)
20. **實現波動率過濾** — 停損/達標交易波動率完全重疊，無區分力
21. **回檔速度過濾** — 慢速回檔也能產生有效均值回歸
22. **連續下跌天數** — 不可替代回檔門檻或 2日跌幅

### 策略類型禁忌
23. **z-score 配對交易** — 所有資產對都存在結構性漂移，5 對 0 成功
24. **動量回檔在日波動>2% 礦業資產** — SMA 趨勢濾波假陽性率過高
25. **動量回調在多成分等權重板塊 ETF** — 板塊級 ROC 反映個股事件加總非板塊趨勢。**RS 動量（板塊 vs SPY/QQQ）對市值加權板塊 ETF 同樣無效**：CIBR 三次嘗試（QQQ/SPY 基準、鬆/緊/品質過濾）均負 Sharpe，網路安全無獨立板塊動量週期（CIBR-006 驗證）。RS 動量有效條件：(a) 強週期性板塊如半導體（SOXL-010）或 (b) 地理/資產類別差異大且**週期性**的比較對（EWT vs EEM）。**持續性結構優勢（如 INDA vs EEM：人口紅利/IT）不產生有效 RS 訊號**：INDA-007 三次嘗試（RS 2~3%、ATR 1.10~1.15）Part A -0.49~0.07，極端市場狀態依賴。**宏觀事件驅動的商品優勢（EWZ vs EEM）同樣無效**：EWZ-005 三次嘗試（RS 10d/15d/20d、2-4%門檻、含/不含 ATR），min(A,B) -0.33~-0.21，A/B 訊號比 6-7:1，巴西商品優勢受大宗商品價格/BRL 匯率/政治事件驅動而非週期性。**政策驅動的中國優勢（FXI vs EEM）同樣無效**：FXI-007 三次嘗試（RS 3-4%、SMA(50)/SMA(200) 趨勢過濾），min(A,B) -6.63~0.16，A/B 訊號品質極度不對稱（Part A WR 0-67% / Part B WR 77-86%），2022 regulatory crackdown + 2024-2025 stimulus 的政策週期使 RS 訊號在轉折點急速反轉。**失敗模式擴展至發達市場單一國家 ETF（EWJ vs EFA/SPY）同樣無效**：EWJ-004 三次嘗試（EFA 基準 RS≥2% SMA50、EFA RS≥3% SMA200、SPY RS≥3% SMA50），min(A,B) 0.15/0.12/-0.24，遠不及 EWJ-003 混合進場的 0.60。日本相對強度由事件驅動（BOJ 政策、日圓套息交易、出口商獲利週期），非持續週期性因素。Att3 使用 SPY 作基準時 Part A 0.37/Part B -0.24，2025 年日圓急貶期 Part B 5/6 訊號集中爆發但 WR 僅 50%。**整合規則**：RS 動量失敗模式擴展至所有政策/匯率/事件驅動的單一國家 ETF（無論 DM 或 EM），有效性先決條件為 (a) 強週期性板塊驅動或 (b) 個股層級持續性超額表現
26. **趨勢回檔策略** — 在低波動防禦型 ETF、高波動個股上均市場狀態依賴過強。**短期動量（5日漲幅>10%）在 IBIT 上 Part A 1.00/Part B -0.55**，2024 牛市 87.5% WR vs 2025 震盪 25% WR（IBIT-005 Att2 驗證）。**低波動歐洲寬基 ETF（VGK）同樣失敗**：SMA(20)>SMA(50) 趨勢對齊+淺回檔 min 0.02、寬出場 min -0.21、ROC 動量 0 OOS 訊號（VGK-006 三次嘗試驗證）。**政策驅動單一國家 EM ETF（FXI）絕對動量連續亦失敗**：FXI-012 三次迭代（Donchian 20d 新高 + 淺回檔 + SMA 趨勢/黃金排列/slope 過濾），min(A,B) -0.09/-0.11/-0.21，所有 regime filter 均無法拯救。**反直覺核心發現**：FXI 最佳動量連續訊號常發生在「regime 轉換期」（2022 Q4 reopening 初期、2024 Q3 刺激初期）——此時 SMA(50) slope 仍為負但即將轉折；slope 已轉正時往往已錯過最佳進場點。**整合規則**：趨勢/動量延續策略禁忌清單擴展至**政策驅動單一國家 EM ETF**（FXI 已驗證）——所有趨勢過濾器在政策衝擊/轉換期皆為滯後指標，RS 動量（FXI-007）與絕對動量（FXI-012）均失敗
27. **RSI(2) 在日波動 >2% 或利率敏感/事件驅動型資產** — 過於敏感，熊市產生假訊號（SIVR、TSM、FCX、IBIT、XLU、SOXL 均驗證）。有效範圍：日波動 ≤ 1.5% 的**美國寬基指數 ETF**（SPY、DIA、IWM、VOO）。**非寬基 ETF 即使日波動在有效範圍內仍無效**：VGK（歐洲，1.12%，Part A -0.06）、CIBR（美國板塊，1.53%，Part A -0.19）。關鍵差異是**板塊/國家集中度**而非上市國家：集中型 ETF 在持續性熊市（COVID、2021-22 科技拋售）中 RSI(2) 訊號反覆失敗（CIBR-004 Att1 驗證）
28. **BB 擠壓突破在商品/利率/3x 槓桿/單一國家 EM ETF** — 有效性：個股(2-4%) > 高流動 ETF(1.5-2%) > 其餘均失敗。**例外**：EEM（新興市場 ETF）因 EM risk-on/risk-off 資金流特性有效（min 0.18，8 次實驗確認為天花板）。**單一國家 EM ETF（INDA/EWT/FXI）均失敗**，FXI 三次迭代 Part A -0.12~-0.30（FXI-003 驗證）
29. **趨勢/突破/動量策略在 3x 槓桿 ETF** — 3x 放大噪音至日波動 4-8%，突破/動量訊號無法補償高波動 SL
30. **所有趨勢/突破/動量在利率驅動 ETF（TLT）** — 宏觀政策驅動資產無純技術面解法

### 出場相關禁忌
31. **緊縮 SL 在悲觀認定下** — SL/TP 距離過近時悲觀認定選擇停損
32. **縮短冷卻期** — 增加 Part A 二次探底訊號但 Part B 品質未必跟上
33. **動量過濾窗口不匹配持倉週期** — 持倉 2-3 天用 2日跌幅最佳

### 跨資產過濾禁忌
34. **Close Position Filter 不可跨資產通用** — GLD/IWM/XBI/EEM 有效但 USO/SIVR/FCX 反效果（EEM-011 驗證：移除後 WR 58.3%→52.2%）
35. **板塊指數確認（SMH）對個股（TSM）** — 弱化版過濾器只移除好訊號
36. **跨資產相對表現過濾在 RSI(2) 框架** — 極端超賣時市場同步下跌，無區分力
36b. **廣基 ETF RS 動量（EEM vs SPY）** — 宏觀/政治事件（關稅、貿易戰、中國政策）驅動而非結構性因素，三次嘗試 Part B 均為負值（EEM-006 驗證）
37. **跨資產利率指標（TLT）過濾利率敏感 ETF（XLU）** — 響應速度和方式不同
38. **回檔回看窗口不可跨資產移植** — 20日在 GLD/COPX 有效，在 SIVR/URA/IBIT/INDA 失敗（IBIT-005 Att1：10日→20日 Part B 0.37→-0.38；INDA-003 Att3：20日回看 A/B 訊號比 2.75:1 嚴重失衡）

### 資產特定 TP/SL 硬上限（不可突破）
39. **USO TP +3.0%** / SL -3.25% — contango 限制
40. **TSM TP +7%** — 邊際交易翻轉
41. **SOXL TP +18%** / SL -12% — 邊際交易翻轉
42. **NVDA TP +8%** / SL -7%（突破）、SL -10%（均值回歸）— TP 硬上限跨策略
43. **FCX SL -12%（均值回歸）**、TP +8%/SL -7%（突破）— 需寬 SL 呼吸空間
44. **IBIT SL -7%** — 高波動需寬 SL，但 -8% 過寬（停損交易均跌穿 -7% 後繼續至 -8% 以下，加寬只增加虧損，IBIT-005 Att3 驗證）
45. **XBI SL -5.0%** — 熊市超賣常下探 -4~-5% 後反彈
46. **VOO TP +2.85%**、**SPY TP +3.0%** — 同指數 ETF 的 TP 不同
46b. **VGK TP +3.5%** — TP +4.0%（3.57σ）轉達標交易為停損（VGK-005 Att2 驗證）
47. **URA SL -5.5%** — 甜蜜點
48. **COPX TP +3.5%** / SL -4.5% — 甜蜜點
49. **EEM SL > -3.0%（突破策略）** — EM 停損為結構性崩潰非暫時回撤，加寬 SL 只增加虧損（EEM-008 Att1）

### 進場機制禁忌
50. **價格範圍壓縮替代 BB Squeeze 在分散化 ETF** — 價格範圍壓縮門檻較 BB 帶寬更鬆，產生過多假突破。BB Squeeze 的標準差+百分位方法對 EEM 類 ETF 仍是最佳壓縮偵測（EEM-008 Att2）
51. **環境實現波動率過濾 BB Squeeze 突破** — 宏觀驅動 ETF（EEM/TLT）的衝擊發生在正常波動率環境，事後波動率才飆升。環境波動率無法預測未來衝擊，反移除好訊號（如 COVID 復甦期突破）多於壞訊號（EEM-008 Att3）
52. **政策驅動 EM ETF 拒斥所有短週期反轉結構與絕對動量連續結構（BB 下軌 MR / BB Squeeze 突破 / Stoch 交叉 / Failed Breakdown Reclaim / Gap-Down Capitulation / 絕對動量連續）** — BB(20,2.0) 太鬆捕捉慢磨下跌（FXI WR41.7%），BB(20,2.5)+多重過濾過嚴（5+1訊號）。BB 帶寬在持續熊市中不斷外擴，下軌失去選擇性。2d decline≤-3% 獨立進場亦僅 min 0.13，不如 PB+WR 框架。**Failed Breakdown Reversal（Turtle Soup）在 FXI 亦失敗（FXI-009 驗證）**：三次迭代（10d/5d lookback、1% 深度門檻、ClosePos、bullish bar）最佳 min 0.00（Att1 Part A 8 訊號 Sharpe 0.18 / Part B 1 訊號停損 0.00），所有 SL 交易（2021-11、2022-09、2023-02、2025-04）在 reclaim 後 2-10 天再度深跌停損，證明政策/事件驅動 EM 的 breakdown reclaim 結構無持續反轉能量。**絕對動量連續（Donchian + 淺回檔）在 FXI 亦失敗（FXI-012 驗證）**：三次迭代（Att1 baseline、Att2 黃金排列 SMA20>SMA50、Att3 SMA50 slope 正），min(A,B) -0.09/-0.11/-0.21，所有 regime filter 均無法拯救。Att1 Part A 26 訊號 WR 42.3%（2019-2023 中國熊市 15/26 快速 SL），Part B 12 訊號 WR 58.3% Sharpe 0.24；Att2 Part B 改善（WR 70%、Sharpe 0.55，超越 FXI-005 Part A 的 0.38）但黃金排列**無法濾除**中國 2019 貿易戰/2021 監管衝擊前/2023 弱勢期的短期黃金排列後反轉；Att3 **反直覺雙向惡化**：SMA slope filter 使 Part A WR 43.8%→37.5%、Part B WR 70%→55.6%——FXI 最佳動量連續訊號常發生在「regime 轉換期」（2022 Q4 reopening 初期、2024 Q3 刺激政策初期）此時 SMA slope 仍為負但即將轉折；slope 已轉正時往往已錯過最佳進場點。**雙重結構性拒斥發現**：FXI 兼具「短週期反轉失效」與「趨勢延續失效」——所有短週期反轉結構（本 lesson 已列）+ 絕對動量連續（本次新增）+ RS 動量（lesson #25）皆無效。核心假設：中國政策衝擊常於 regime 轉換期出現，**所有趨勢/反轉過濾器在此時點皆為滯後指標**。**Gap-Down Capitulation + Intraday Reversal 在 FXI 亦失敗（FXI-010 驗證）**：三次迭代均未勝過 FXI-005 的 0.38。Att1（gap≤-1.5% entry trigger + 緊出場）Part A 0.33 Part B -0.51（22 訊號 WR 31.8%）；Att2（gap≤-2.5% + Close>midpoint + 深 pullback + 寬出場）min 0.00（訊號 5/1 過稀疏）；Att3（Gap 作為 5d regime filter + FXI-005 entry）Part A 0.34 接近基線但 Part B 2 訊號零方差 Sharpe 0.00，A/B 訊號比 4.4:1 遠超 1.5:1 目標。失敗根因：FXI 雖有 HK 盤後連續價格發現，但中國政策/經濟消息在美股盤中持續發酵，gap-down 後常續跌而非反轉（與 IBIT BTC 24/7 的「拋壓完成 + 美股撿便宜」結構本質不同）。**例外**：EWJ-003 驗證 BB 下軌+回檔上限混合進場在日本市場有效（Sharpe 0.60），因日本市場無中國式政策衝擊（FXI-006 驗證）。**CIBR-008 Att2 進一步驗證**：在美國板塊 ETF（CIBR 1.53% vol）上 BB(20,2.0) + 回檔上限 -12%（7.8σ）+ WR + ClosePos + ATR 混合進場 min(A,B) 0.39（+44% vs CIBR-007 純 BB 下軌的 0.27）。**VGK-007 Att1 三度驗證**：歐洲寬基 ETF（VGK 1.12% vol）BB(20,2.0) + 回檔上限 -7%（6σ）+ 三重品質過濾 min(A,B) 0.53（+18% vs VGK-004 Att1 的 0.45），且解決 VGK-004 A/B 累積差 37.5% 問題（降至 8.2%）。**EWZ-006 Att3 四度驗證並擴展邊界**：商品驅動 EM 單國 ETF（EWZ 1.75% vol）BB(20,1.5) + 回檔上限 -10%（5.7σ）+ 三重品質過濾 min(A,B) 0.69（+103% vs EWZ-002 Att3 的 0.34），且 Part B 樣本從 4 增至 6（+50%），證明高波動需放寬 BB 至 1.5σ 維持訊號頻率。**EWT-008 Att1 五度驗證並擴展驅動類別**：半導體驅動 EM 單國 ETF（EWT 1.41% vol）BB(20,2.0) + 回檔上限 -8%（5.7σ）+ 三重品質過濾 min(A,B) 0.57†（+36% vs EWT-007 RS 動量 0.42），†Part B 3/3 全達 +3.50% 零方差 Part A 綁定約束（同 EWJ-003 模式）。A/B 年化訊號比 1.2:1 優秀，A/B 累計差 36.1%（同 EWZ 量級）。**EEM-012 Att3 六度驗證並擴展至 broad EM 指數類別**：broad EM ETF（EEM 1.17% vol）BB(20,2.0) + 回檔上限 -7%（6σ）+ WR ≤ -85（收緊過濾 EM 危機淺觸） + ClosePos + ATR 三重品質過濾 min(A,B) 0.34（+89% vs EEM-005 BB Squeeze 的 0.18）。A/B 累計差僅 3.6%（極優），訊號頻率 1.2/yr vs 2.0/yr（Part B 牛市活躍）。**關鍵發現**：ATR 門檻對 EEM 在 BB Lower 框架內**方向反轉**——Att2 收緊 ATR>1.15 使 min(A,B) 崩至 -0.60（危機日 ATR 飆高，高門檻保留停損移除贏家），WR 才是 EEM 混合模式的關鍵品質軸。**EEM-014 Att2 進一步以 2DD floor 精煉**（2026-04-21）：在 EEM-012 Att3 基礎上新增 2DD floor ≤ -0.5% 過濾淺幅漂移訊號，使 min(A,B) 0.34→**0.56**（+65%），Part A Sharpe 0.34→0.73（+115%）、Part B 不變 0.56；僅過濾 1 筆 2021-11-30 淺 2DD SL（+0.29%）。Att1 直接移植 CIBR-012 2DD cap 方向崩壞至 -0.02，Att2 反向為 floor 方向成功——**核心跨資產發現**：2DD 方向取決於殘餘 SLs 的 2DD 結構（CIBR 深 2DD SLs → cap；EEM 淺 2DD SLs → floor），**不可通用移植**。Att3 ablation（移除 ATR）再度崩至 -0.02，證明 ATR>1.10 與 2DD floor 為互補雙過濾而非冗餘。此為混合進場模式首次以 2DD floor 進一步精煉，類似精煉可能適用 VGK/EWJ/EWT/EWZ/CIBR 等同框架資產（方向按 SL 結構選擇，閾值按日波動縮放）。混合進場模式適用：低中波動（1.12%~1.75%）資產+三重品質過濾+回檔上限 5.7-8σ（BB std 隨波動度降低 0.5-1.0σ，VGK/CIBR/EWT/EEM 用 2.0σ，EWJ 1.5σ no cap→1.5σ+cap 7%，EWZ 1.5σ+cap 10%），**驅動類別已涵蓋寬基（VGK/EWJ）、板塊（CIBR）、商品驅動 EM（EWZ）、半導體驅動 EM（EWT）、broad EM 指數（EEM）**；不適用政策驅動單一 EM 國家 ETF（FXI 驗證）。**XBI-010 驗證有效邊界上限為日波動 1.75%**：生技板塊 ETF（XBI 2.0% vol）三次迭代（BB 1.5σ 過鬆 min 0.07、BB 2.0σ 過嚴 min -0.55、OR 進場 cap -12% min 0.16）均未勝過 XBI-005（min 0.36）。失敗根因：(a) XBI 無法使用 ATR 過濾（XBI-009 驗證日波動達 ATR 有效邊界上限），失去混合模式的關鍵波動率飆升確認；(b) 生技板塊 FDA/臨床事件驅動使訊號呈現為絕對深度回檔（8-15%）而非統計異常；(c) XBI-005 的固定 pullback 8-20% 在 2.0% 日波動下已是最優結構。**FCX-011 驗證 1.75% vol 上限延伸至單一個股類別**（2026-04-22，repo 第 1 次 BB-lower hybrid mode 於高波動單一個股試驗）：FCX 銅礦龍頭股 ~3% vol 三次迭代（Att1 baseline + PB cap -15% min **-0.23**、Att2 + 2DD cap ≥-5% min -0.09、Att3 + 2DD floor ≤-5% min 0.00）均未勝過 FCX-004 (min 0.41)。失敗根因：(a) FCX 高波動使 BB 下軌觸及頻率高但選擇性低，signal-day 過濾（ATR>1.15, ClosePos≥40%）無法分辨加速崩盤與真 capitulation，Part B 2024-07-19/12-13 均 1-3 日快速 SL；(b) FCX 贏家訊號的 2DD 分布橫跨 -3%~-8%，與輸家重疊——2DD cap 方向錯殺 2021-06-16 深 2DD 贏家，2DD floor 方向濾掉 2/3 Part A 訊號，雙向皆無選擇力（與 CIBR 深 2DD SL / VGK 淺 2DD SL 之結構皆不同）；(c) 單一個股事件驅動（銅價衝擊、公司信用、中國需求）使統計自適應 BB 下軌無法捕捉獨特事件結構，ETF 的分散化則使 BB 成為有效 regime classifier。**整合規則**：混合進場模式上限**從「1.75% vol ETF」擴展為「1.75% vol（涵蓋 ETF 與單一個股兩類別）」**。新失敗清單項：**高波動單一個股（FCX ~3%）**，繼 XBI 2.0% ETF、FXI 政策驅動 EM ETF、GLD/TLT 商品/利率 ETF 後。開放假設：中低波動單一個股（~1.5-2% 防禦型股票）是否適用仍待驗證。**INDA-008 驗證有效邊界下限為日波動 1.12%**：印度 ETF（INDA 0.97% vol）三次迭代（BB 2.0σ 過嚴 min 0.20、BB 1.5σ 過鬆 min -0.04、BB 1.8σ 中間 min -0.25）均未勝過 INDA-005 Att3（min 0.23）。失敗根因：(a) INDA 0.97% vol 下 BB 帶寬太窄（2.0σ 僅 1.94% 偏離均值，多數有效回檔不觸及；1.5σ 僅 1.46%，納入淺技術超賣假訊號）；(b) 固定 3-7% 回檔（3.1-7.2σ）框架在 0.97% 波動下已精準鎖定有效均值回歸深度，BB 自適應機制在極低波動下不比固定門檻優越；(c) INDA 慢磨特性（受盧比/外資流驅動）使 BB 下軌訊號與真正反轉機會關聯性低。**IWM-012 驗證 [1.12%, 1.75%] vol 邊界內 asset 結構亦為關鍵變項（2026-04-25，repo 首次小型股寬基 ETF BB-lower hybrid mode 試驗）**：IWM 1.5-2% vol 位於混合模式有效邊界中段（CIBR 1.53% vol 已成功），但三次迭代（Att1 BB(20,2.0)+cap-10%+ATR>1.10 min 0.23、Att2 BB(20,1.5)+cap-10% min 0.20、Att3 BB(20,2.0)+ClosePos≥0.50+ATR>1.15 min 0.31）均未勝過 IWM-011 Att2（min 0.52）。失敗根因：(a) **訊號集差異**——IWM RSI(2)<10+2DD≤-2.5% 框架捕捉「淺超賣急跌反轉」，多數訊號未達 BB(20,2.0) 下軌深度（~3-4% 偏離均值），BB-lower 框架捕捉「絕對深度回檔」，兩者訊號集互補但不重疊（Att1 7 訊號 vs IWM-011 10 訊號，缺失 5 IWM-011 winners）；(b) **小型股動態**——IWM 為 Russell 2000 小型股寬基，個股事件驅動加總使板塊級 BB 下軌觸及包含過多事件雜訊（如 2020-01 pre-COVID、2022-05 Fed pivot 恐懼期），有別於 VGK/EWJ 發達寬基、EWZ/EWT 單一國家 EM、CIBR 美國板塊等市場結構；(c) ATR>1.10 在 IWM 與其他資產的角色不同——IWM-011 中 ATR>1.10 過濾「慢磨下跌假訊號」並提升至 0.52，本實驗中 ATR>1.10 在 BB-lower 訊號集上保留所有原 SL 無選擇性提升。**新邊界規則**：BB-lower hybrid mode 適用「結構性集中或真正寬基」ETF（VGK 非美寬基、EWJ 日本寬基、EEM EM 寬基、EWZ/EWT 單一國家 EM、CIBR 美國板塊）；**不適用個股事件驅動加總的小型股寬基 ETF（IWM 為首例驗證資料點）**。確認 [1.12%, 1.75%] vol 為**必要非充分條件**，asset 結構（個股事件驅動加總 vs 真正寬基或集中度高的 ETF）亦為關鍵變項

53. **Keltner Channel Lower Band 均值回歸在高波動資產（vol > 1.5%）** — Keltner 下軌（EMA20 − k×ATR10）在 GLD-005（1.12% vol）成功，但對高波動加密 ETF 失敗。**IBIT-007 驗證（IBIT 3.17% vol）**：三次迭代（Att1 2.0×ATR 過淺訊號品質差、Att2 加 WR+深回檔非綁定、Att3 2.5×ATR 過深訊號歸零）均未超越 IBIT-006 Att2 的 0.40。核心失敗：Keltner 下軌基於收盤價相對 EMA 的 ATR 偏離，在高波動資產上觸發常落後於 capitulation 底部（慢磨下跌中觸發，伴隨續跌動能），無法複製 gap-down 過濾器捕捉的「盤外拋壓完成 → 美股撿便宜」結構性不對稱。**高波動下 Keltner 參數空間狹窄**：2.0×ATR 過淺（假訊號多），2.5×ATR 過深（訊號歸零），無兩全甜蜜點。推測 Keltner Lower MR 有效邊界為日波動 ≤ 1.5%。

> 每條禁忌的詳細實驗證據見 [cross_asset_evidence.md](cross_asset_evidence.md) Section 10。

---

## 11. 新資產實驗啟動流程
<!-- freshness:
  derived_from: [GLD-007,SIVR-003,FCX-001,FCX-002,USO-001]
  validated: 2026-03-27
  data_through: 2025-12-31
  confidence: medium
-->

1. **計算日波動度**：取過去 5 年日報酬的標準差，與 GLD (≈1.2%) 比較得到倍率
2. **選擇策略模板**：
   - 波動度 < 2%：參考 GLD-007（pullback + Williams %R + trailing stop）
   - 波動度 2-4%：參考 SIVR-003（pullback + Williams %R，無 trailing stop）
   - 波動度 > 4% 或槓桿 ETF：參考 TQQQ-010（極端恐慌買入，固定出場）
   - 個股高 beta：參考 FCX-001（三重濾波，寬出場）
3. **縮放參數**：按波動度倍率調整各門檻（見第 7 節）
4. **啟用成交模型**：使用 execution_backtester，設定合理 slippage
5. **檢查 A/B 平衡**：訊號頻率比控制在 1.0-1.5:1
6. **迭代調優**：先調進場條件（步進 1%），再調出場參數（步進較粗）

---

## 12. 超賣指標週期應匹配持倉週期
<!-- freshness:
  derived_from: [USO-005,USO-007,USO-009,USO-010,SPY-004,SIVR-004,TSM-003,IBIT-002,IBIT-003,URA-003]
  validated: 2026-03-31
  data_through: 2025-12-31
  confidence: high
-->

短持倉策略（平均 ≤ 5 天）優先使用 RSI(2)，但高波動資產（日波動 > 2%）需實測，WR(10) 可能更適合。

**例外**：URA（2.34%）RSI(2) 成功——關鍵差異可能在回檔門檻深度（URA 10% vs SIVR 7%）。TSLA（3.72%）驗證 WR(10) 優於 RSI(2)。

---

## 13. 回檔範圍過濾對穩健性的漸進式改善
<!-- freshness:
  derived_from: [USO-005~013,GLD-006,GLD-007]
  validated: 2026-03-29
  data_through: 2025-12-31
  confidence: high
-->

高波動或受極端事件影響的資產（如商品 ETF），設計均值回歸策略時必須考慮回檔上限以隔離極端崩盤訊號。回檔上限宜設在日波動率的 5-6σ 附近。

---

## 14. 回檔+WR 模式對個股高 Beta 資產效果有限
<!-- freshness:
  derived_from: [FCX-002,GLD-007,SIVR-003,IWM-002]
  validated: 2026-03-30
  data_through: 2025-12-31
  confidence: high
-->

回檔+WR 最適合低波動貴金屬 ETF（GLD、SIVR）和特定板塊 ETF（XBI、COPX、URA）。不適用於個股高 Beta（FCX）和頻繁淺回檔的指數 ETF（IWM）。

---

## 15. ATR 波動率自適應過濾有效邊界
<!-- freshness:
  derived_from: [IWM-011,COPX-007,XLU-011,SIVR-012,XBI-009,IBIT-004,FCX-008,EEM-010,EWZ-002]
  validated: 2026-04-12
  data_through: 2025-12-31
  confidence: high
-->

ATR(5)/ATR(20) 過濾在中低波動資產選擇急跌恐慌、過濾慢磨下跌。

- ~1.0% XLU：ATR > 1.15 → min +272%（極佳）
- ~1.17% EEM：ATR > 1.1 配合跌幅 2.0% → Part A -0.13→+0.03（EEM-010 驗證）
- ~1.5-2.0% IWM：ATR > 1.1 → min +67.7%
- ~1.75% EWZ：ATR > 1.1 → min(A,B) Sharpe 0.10→0.34（+240%，EWZ-002 驗證）
- ~2.25% COPX：ATR > 1.05 → min +28.6%（低門檻仍有效）
- ≥ 2.0% XBI/SIVR/IBIT：失效

**規則**：ATR 過濾僅適用日波動 ≤ 2.25%，門檻隨波動度降低。日波動 > 2.5% 禁用。若進場條件已隱含高波動（深回撤+低 RSI+大乖離），ATR 無額外區分力。

---

## 16. 板塊 ETF vs 寬基指數 vs 個股的策略選擇
<!-- freshness:
  derived_from: [XBI-009,XBI-002,COPX-006,SPY,DIA,IWM,EEM-005,VGK-002,EWZ-002,EWJ-003]
  validated: 2026-04-16
  data_through: 2025-12-31
  confidence: high
-->

- **美國寬基指數 ETF（SPY/DIA/IWM/VOO）**：RSI(2) 短期超賣框架最佳
- **非美國已開發市場 ETF（VGK/EWJ）**：BB 下軌+回檔上限混合進場最佳。EWJ-003 驗證 BB 下軌+回檔上限混合進場優於固定回檔門檻（Part A Sharpe 0.55→0.60）；**VGK-007 驗證同模式在歐洲寬基 ETF 有效**（min(A,B) 0.45→0.53，+18%，A/B 累積差 37.5%→8.2%）。RSI(2) 無效（慢磨特性）。**RS 動量無效（EWJ-004 驗證）**：EWJ vs EFA/SPY 三次嘗試 min(A,B) 0.15~-0.24，Japan 的相對強度由 BOJ 政策/日圓/出口週期事件驅動而非結構性，確認 lesson #25 擴展至 DM 單一國家
- **新興市場寬基 ETF（EEM）**：**BB 下軌+回檔上限混合進場最佳**（EEM-012 Att3 驗證 min(A,B) 0.34，+89% vs EEM-005 BB Squeeze 的 0.18）。混合模式首次延伸至 broad EM 類別。BB 擠壓突破次佳（0.18），RSI(2) 均值回歸受 EM 事件拖累（Sharpe ≤ 0.06）
- **新興市場單一國家 ETF（EWZ，商品驅動）**：BB 下軌+回檔上限混合進場最佳（EWZ-006 驗證 min(A,B) 0.34→0.69，+103%，BB(20,1.5)+10% cap+WR+ClosePos+ATR）。波動率自適應過濾有效（日波動 1.75% 在 ATR ≤ 2.25% 邊界內）
- **新興市場單一國家 ETF（EWT，半導體驅動）**：BB 下軌+回檔上限混合進場最佳（EWT-008 Att1 驗證 min(A,B) 0.42→0.57†，+36%，BB(20,2.0)+8% cap+WR+ClosePos+ATR>1.10）。†Part B 3/3 全達 +3.50% 零方差，Part A 綁定約束。**擴展驅動因素類別**：混合模式適用商品驅動（EWZ）、半導體驅動（EWT）、政策非主導的 EM 單一國家 ETF；政策驅動 EM（FXI）仍失敗（lesson #52）
- **板塊/商品 ETF（XBI/COPX/URA/SIVR）**：pullback+WR 深回檔框架最佳，RSI(2) 無效。**XBI-010 驗證 BB 下軌+回檔上限混合進場模式不適用 XBI 2.0% 日波動**（三次迭代 min 0.07/-0.55/0.16 均未勝過 XBI-005 的 0.36），確認混合模式有效邊界上限為日波動 1.75%（EWZ 為上限）。**INDA-008 驗證混合進場模式不適用 INDA 0.97% 日波動**（三次迭代 min 0.20/-0.04/-0.25 均未勝過 INDA-005 的 0.23），確認混合模式有效邊界下限為日波動 1.12%（VGK 為下限）。混合進場模式有效 vol 區間 = [1.12%, 1.75%]。**IWM-012 驗證 vol 邊界為必要非充分條件**（2026-04-25）：IWM 1.5-2% vol 位於有效範圍中段（CIBR 1.53% 已成功）但三次迭代均失敗（min 0.23/0.20/0.31 vs IWM-011 0.52）。**新邊界規則**：BB-lower hybrid mode 適用「結構性集中或真正寬基」ETF（VGK/EWJ/EEM/EWZ/EWT/CIBR）；不適用個股事件驅動加總的小型股寬基 ETF（IWM 首例）。Asset 結構（個股事件驅動加總 vs 真正寬基或集中度高的 ETF）亦為關鍵變項
- **小型股寬基 ETF（IWM）**：RSI(2)+2DD+ClosePos+ATR 框架最佳（IWM-011 min 0.52）。**BB-lower hybrid mode 失效**（IWM-012 三次迭代驗證），訊號集與 RSI(2) 框架互補但不重疊，且小型股事件驅動加總引入過多雜訊
- **貴金屬/商品 ETF（GLD）**：**Post-Capitulation Vol-Transition MR（2DD floor 方向）不適用**（GLD-013 驗證，三次迭代 1 訊號/0.20/-0.69 均未勝過 GLD-012 Att3 的 0.48）。失敗根因：商品 ETF 下跌由實質利率、USD、通膨預期等宏觀因素驅動，非 equity capitulation 動力學；VGK-008 成功依賴「SL 集中於 2DD 淺帶」結構，GLD SLs 分布於所有 2DD 深度，2DD floor 過濾器無選擇力。pullback+WR+ClosePos 框架（GLD-008/012）仍為最佳
- **個股（TSLA/NVDA/FCX）**：BB 擠壓突破或極端超賣（取決於波動度）。**FCX-013 驗證 buffered multi-week SMA regime 第 3 次跨資產有效（首次商品/礦業單股，反向 k=1.00 嚴格甜蜜點）** min 0.41→0.55（+34%），擴展 lesson #22 適用至商品/週期性個股（k 值資產相依，需 trade-level ratio 分布分析）
- **3x 槓桿 ETF（TQQQ/SOXL）**：僅極端恐慌均值回歸或板塊 RS 動量

---

## 17. Donchian 通道突破不如 BB Squeeze Breakout
<!-- freshness:
  derived_from: [FCX-007,GLD-011,TSLA-006]
  validated: 2026-04-07
  data_through: 2025-12-31
  confidence: high
-->

BB 上軌（均值+N 倍標準差）隨波動度自動縮放，嚴格優於 Donchian 的固定價格高點。BB Squeeze 進一步要求先有波動收縮，只捕捉「整理後啟動」。Keltner Channel 也不如 BB（ATR 包含跳空缺口使通道在高波動期更寬）。

---

## 18. BB 擠壓突破有效性排序
<!-- freshness:
  derived_from: [TSLA-005,NVDA-003,FCX-004,IWM-006,COPX-005,SOXL-009,GLD-009,SIVR-008,TLT-004,IBIT-003,TSM-005,EEM-005,INDA-003,EWT-003,FXI-003,CIBR-003]
  validated: 2026-04-13
  data_through: 2025-12-31
  confidence: high
-->

個股（日波動 2-4%）> 高流動 ETF（日波動 1.5-2%）> 單一商品 ETF（~1%）> 利率驅動 ETF ≈ 3x 槓桿 ETF > 小眾 ETF

**例外**：EEM（新興市場 ETF, 1.17% vol）BB Squeeze min(A,B) Sharpe 0.18，遠優於其均值回歸最佳 0.06。可能因 EM risk-on/risk-off 資金流特性使波動率壓縮-突破模式有效。
**反例**：INDA（印度 ETF, 0.97% vol）BB Squeeze Part A 0.53-0.72 / Part B -0.41~-0.48（WR 差距 39-47pp），嚴重市場狀態依賴。EWT（台灣 ETF, 1.41% vol）BB Squeeze Part A 0.35 / Part B -0.37（WR 差距 31.4pp），地緣政治風險導致突破失敗。FXI（中國 ETF, 2.0% vol）BB Squeeze 三次迭代 Part A 均為負值（-0.12~-0.30），2019-2023 中國熊市假突破率過高。EEM 的 EM 突破有效性不可延伸至單一國家 ETF（INDA、EWT、FXI 均驗證）。

- 突破買在高點，SL 需比均值回歸更緊但 ~2σ 呼吸空間（NVDA/TSLA SL -7%）
- SMA(50) 是趨勢確認甜蜜點（SMA(20) 太短、SMA(100) 改變方向非改善品質）
- 擠壓百分位和冷卻期影響 A/B 平衡，需同時調校
- 地緣政治敏感個股（TSM）突破後常因政策消息急速反轉
- 低波動 ETF (EEM 1.17%) TP 需降至 3.0%（3.5% 到期過多），SL 3.0% 對稱即可
- **板塊 ETF（CIBR 1.53% vol）BB Squeeze 完全無效**：Part A -0.20 / Part B -0.27，WR<40%。板塊 ETF 突破缺乏持續性，突破後快速反轉。均值回歸是正確框架（CIBR-003 驗證）

---

## 19. N 日急跌過濾（雙向性發現 2026-04-21，VGK-008 再確認 2026-04-22，**DIA-012 1d+3d 雙維度擴展 2026-04-24，TSLA-013 突破策略失敗邊界 2026-04-25，SPY-009 1d FLOOR 反向擴展 2026-04-25，TSLA-014 高 vol 單股結構性邊界 2026-04-25，IWM-013 oscillator depth 替代 raw return depth 2026-04-26**）
<!-- freshness:
  derived_from: [FCX-008,USO-013,EWT-004,VGK-005,CIBR-012,EEM-014,INDA-010,VGK-008,DIA-012,TSLA-013,SPY-009,TSLA-014,IWM-013]
  validated: 2026-04-26
  data_through: 2025-12-31
  confidence: high
-->

**IWM-013 擴展（2026-04-26，repo 首次以 oscillator depth 替代 raw return depth 維度）**：對於小型股寬基 ETF（IWM Russell 2000，1.5-2% vol），1d/3d raw return 維度的 capitulation-depth filter 結構性失敗（Att1 1d cap + 3d cap min -0.04 / Att2 3d FLOOR min 0.43，均劣化於 IWM-011 的 0.52）；改用 **RSI(2) < 8（oscillator depth tightening，從 IWM-011 < 10 加嚴 1.25x）** 後 Att3 min(A,B)† **0.59**（+13.5%）成功。**結構性根因**：IWM 為 2000+ 個股寬基 ETF，板塊級 raw return 帶有過多個股事件雜訊，losers vs winners 在 1d/3d 維度高度重疊（loser 2021-11-26 1d=-3.77% 與 winner 2020-09-21 1d=-3.50% 不可分；loser 2025-03-04 3d=-2.81% 與 winner 2025-08-01 3d=-3.49% 接近）；但 RSI(2) 為 EWMA-based 反映多日壓力累積，losers 集中 RSI 8-10、winners RSI ≤ 7.9，有清晰分隔。**新 cross-asset 規則（lesson #19 v3）**：(a) 對於發達/單一國家寬基 ETF（DIA/SPY/EWJ/VGK/EEM/INDA），raw return depth (1d/3d/2DD floor or cap) 仍為主要 capitulation strength 度量工具；(b) 對於小型股寬基 ETF（IWM，個股事件驅動加總），改用 **oscillator depth (RSI threshold tightening)** 為更精準的 capitulation strength 度量；(c) 跨資產移植時優先檢查 SL/TP 在 raw return 維度的可分離性，若重疊則改用 oscillator 維度。**Cooldown shift 良性案例**：IWM-013 Att3 移除 2019-08-02 LOSS 後 cooldown shift 至 2019-08-05 expiry +0.44%（淨改善 +1.82pp），未引發 SL 連鎖（不同於 NVDA-010 Att3 / TLT-010 失敗模式），顯示**「淺 oscillator depth 過濾器」較「raw return cap」更不易觸發負面 cooldown chain shift**。

**SPY-009 擴展（2026-04-25，repo 首次 1d FLOOR 方向）**：低波動寬基 ETF（SPY ~1.0% vol）的 SL 1d 維度失敗結構與 DIA **方向完全相反**——SPY SLs 為 1d 過淺（-0.09%~-0.30%）的弱勢盤緩慢漂移，需 **1 日跌幅下限 (1d FLOOR) <= -0.5%** 過濾（要求訊號日具備足夠 capitulation 強度）；DIA SLs 為 1d 過深（-2.5%, -2.2%）的政策震盪延續，需 **1d cap >= -2.0%** 過濾。**雙資產共同失敗模式**：Part B 2025-04-07 Trump 關稅 3d -10.65% / -10.06% regime-shift → 共用 **3d cap >= -8%** 過濾。SPY-009 Att2 min(A,B) Part A Sharpe **6.56**（vs SPY-005 0.53，+1138%）。**新 cross-asset 規則（精煉 lesson #19）**：低波動寬基 ETF（~1.0% vol）SLs 在 1d 維度的失敗結構**並非單一方向**——需個別 trade-level SL 分布分析判斷：(a) DIA 防禦型成份股（消費品/醫療/工業）→ 1d cap 方向（過深政策震盪）；(b) SPY 較高科技股權重（FAANG 高 vol 成份股）→ 1d FLOOR 方向（過淺弱勢漂移）。**單一資產失敗模式不能直接跨資產移植**，即使在「同 vol 等級 + 同進場框架」的相近資產類別之間，仍需 trade-level 確認。

**DIA-012 擴展（2026-04-24）**：低波動寬基 ETF（DIA ~1.0% vol）SLs 在 1 日與 3 日報酬維度有清晰分離（與 2 日維度正交）：(a) 1d cap >= -2.0% 過濾 news/policy-driven 單日深度急跌（如 Omicron 黑色星期五、COVID 二波）；(b) 3d cap >= -7% 過濾 regime-shift 級別 3 日延續下跌（如 Trump 關稅週末延續）。**1d+3d 雙維度過濾**為新策略類別（repo 首次），擴展 lesson #19 family 至第三類失敗結構：與 2DD cap CIBR-direction（深 2DD SL 集中）和 2DD floor EEM/INDA/USO-direction（淺 2DD SL 集中）並列為三大失敗模式。**規則**：低波動寬基 ETF 在 RSI(2)+2DD+ClosePos 框架基線上，若 SL 在 2DD 維度與贏家分布重疊但在 1d/3d 維度有偏移，採 1d cap + 3d cap 雙維度過濾。**SPY-009 擴展（2026-04-25）**：1d 維度有雙向性（cap 或 floor），需 trade-level 分析判斷。


**2DD floor（要求 2 日跌幅 ≤ -X%，篩選急跌恐慌）**：在基礎訊號頻率 ≥ 5/年的資產上有效（USO、COPX），但在訊號已稀少的資產上（FCX ~3.6/年）會過度移除好訊號。

**例外**：EWT-004 在 3.2 訊號/年仍有效（min(A,B) 0.13→0.15，+15%），但配合非對稱出場才能發揮，且改善幅度小於高頻資產。

**低波動資產限制**：VGK（1.12% vol）上 2日急跌 ≤ -1.0% 太溫和（~0.45σ/天），pullback+WR 訊號天然包含急跌成分，過濾器因冷卻期交互作用反移除好訊號（Part A 0.42→0.36，-14.3%，VGK-005 Att1 驗證）。

**反方向：2DD cap（要求 2 日跌幅 ≥ -X%，排除 in-crash acceleration）**：CIBR-012 Att3 驗證 2DD 上限過濾在飽和品質框架（BB 下軌+回檔上限+WR+ClosePos+ATR 五重品質過濾）上有效。CIBR 1.53% vol，2DD cap ≥ -4.0%（=2.6σ）使 min(A,B) 從 0.39 → **0.49**（+26%）。關鍵洞察：**當資產的 Part A 殘餘失敗訊號集中於「崩盤加速中」進場時點，2DD cap（上限）可補足品質過濾器「區分 in-crash vs post-crash」的能力**。此方向與 2DD floor 完全相反：
- 2DD floor: 要求 2 日跌幅至少 X%（篩選劇烈下殺）
- 2DD cap: 要求 2 日跌幅不超過 X%（避開「崩盤加速中」）

**跨資產方向資產相依性（EEM-014 驗證 2026-04-21）**：2DD 方向（cap vs floor）**不可通用移植**，必須先檢查殘餘 SLs 的 signal-day 2DD 分布。

EEM-014 移植 CIBR-012 2DD cap 方向至 EEM（1.17% vol，相同混合進場框架），結果完全相反：
- Att1（2DD cap ≥ -3.0%，CIBR-012 直接移植）：Part A Sharpe 0.34→**-0.02**（崩壞），移除 TPs 保留 SLs
- **Att2（2DD floor ≤ -0.5%，反向方向）**：Part A Sharpe 0.34→**0.73**（+115%），min(A,B) 0.34→**0.56**（+65%）

根因：EEM vs CIBR 的殘餘失敗 SLs 結構**完全相反**：
- CIBR 失敗 SLs 2DD：-4.1% / -4.9%（深，in-crash 加速中）→ 用 cap 方向
- EEM 失敗 SLs 2DD：-2.19% / **+0.29%** / **-0.85%**（淺，慢漂移/非真 capitulation）→ 用 floor 方向

EEM TPs 2DD 集中 -1.47% ~ -3.88%（真急跌後反彈），故深 2DD = 真 capitulation 訊號（不可過濾），淺 2DD = 弱訊號（應過濾）。

**新規則（2DD 過濾器設計流程）**：
1. 在基礎最佳策略跑回測，列出殘餘 SLs 與 TPs 的 signal-day 2DD
2. 若 SLs 集中於深 2DD（如 < -3.0σ）而 TPs 集中於中深 2DD → 用 **cap 方向**（CIBR 類）
3. 若 SLs 集中於淺 2DD（如 > -1.0σ）而 TPs 集中於深 2DD → 用 **floor 方向**（EEM / USO 類）
4. 若 SL 與 TP 的 2DD 分布重疊 → 2DD 方向不適用，改用其他過濾器

**跨資產延伸假設**：2DD 方向精煉可能適用其他混合進場資產（XBI、XLU、IWM、COPX、EWJ、EWT、EWZ、TLT）。方向選擇遵循上述 SL 結構檢查法。閾值隨日波動度 **非線性** 縮放：
- CIBR 1.53% vol → cap -4.0%（2.6σ，寬帶 SL 漸進式門檻）
- EEM 1.17% vol → floor -0.5%（~0.4σ，寬帶 SL 漸進式門檻）
- INDA 0.97% vol → floor -2.0%（2.1σ，寬帶 SL 漸進式門檻）
- **VGK 1.12% vol → floor -2.0%（1.8σ，窄帶 SL 懸崖式門檻）**

**「懸崖式」vs「漸進式」門檻特性（VGK-008 驗證 2026-04-22）**：不同資產的 SL 2DD 分布寬度決定 floor/cap 門檻的敏感度特性：
- **漸進式**（INDA、EEM 類）：SL 2DD 寬帶（> 1pp 跨度），不同門檻呈現平滑過渡（如 INDA -3.0% → -4.0% → -2.0% 方向轉換呈漸進式優化）
- **懸崖式**（VGK 類）：SL 2DD 窄帶（< 0.5pp 跨度），門檻必須一次跨越整個 SL 帶才有效。VGK 殘餘 SL 集中於 -0.89%~-1.68%（1.79pp 跨度但多數集中於 -1.47%~-1.68% 0.21pp 窄帶），使 -1.0%（無效）→ -1.5%（劣化）→ -2.0%（成功）呈現不連續階梯

**更新後的 2DD 過濾器設計流程**：
1. 在基礎最佳策略跑回測，列出殘餘 SLs 與 TPs 的 signal-day 2DD
2. 判斷方向（cap vs floor）：若 SLs 集中於深 2DD → cap；若 SLs 集中於淺 2DD → floor
3. **分析 SL 2DD 分布寬度**：
   - 若寬帶（> 1pp）：採漸進式搜尋，從中間門檻開始
   - 若窄帶（< 0.5pp）：採懸崖式搜尋，直接測試帶外側門檻
4. 若 SL 與 TP 的 2DD 分布重疊 → 2DD 方向不適用，改用其他過濾器

**Meta-lesson**：當一個過濾器「方向」驗證無效（如 CIBR-004 的 2DD floor、EEM-014 Att1 的 2DD cap、VGK-008 Att1 的淺 2DD floor），其**反方向或深度加深**可能作為 timing/regime 過濾器有效。此觀察為新過濾器設計途徑，超越「oscillator hook / range expansion / capitulation depth」家族（lesson #20b 失敗家族）。**Att1 失敗轉 Att2 成功為「反向驗證」教科書案例**：遇到跨資產移植失敗時，先檢查資產結構（殘餘 SL 特徵與分布寬度）而非放棄方向。

**新邊界（TSLA-014 驗證 2026-04-25，repo 第 1 次高 vol 單一股票 Post-Cap MR 試驗）**：**Post-Capitulation Vol-Transition MR 框架（10 日 pullback + 2DD floor + ATR ratio + WR）在高 vol 單一股票上結構性失敗**，確立框架的 vol 邊界。三次迭代全部失敗 vs TSLA-009 Att2 min 0.40：Att1（pullback -10%、2DD -5%）4/1 訊號 min -0.01（過稀）；Att2（pullback -8%、2DD -3%）7/4 訊號 min -0.59（bear regime SLs，Part B 7/12 為 SL）；Att3（pullback -12%、2DD -4%、ClosePos 0.50、WR -85）3/0 訊號 min 0.00（Part B 完全過濾）。**框架成功歷史 vs 邊界**：
- INDA 0.97% vol（broad EM single country）：✅ min 0.30
- VGK 1.12% vol（broad DM single country）：✅ min 2.60
- EEM 1.17% vol（broad EM）：✅ min 0.56
- USO 2.20% vol（事件驅動商品 ETF）：✅ min 0.26
- **TSLA 3.72% vol（事件驅動單一股票）：❌ 三次迭代全部失敗**

**新邊界**：Post-Cap MR 框架在 ~2.2% 日波動 / 事件驅動商品 ETF 為上限，**超越此邊界（高波動單一股票）結構性失效**。失敗機制：高 vol 單一股票的「深 capitulation」與「持續下跌中段」不可分——TSLA 2019/2022/2024 多次出現連續多日 -5%+ 下跌（trade war/Fed hawk/delivery miss/Musk events），任何 2DD 深度過濾器都會在這些「中段」訊號中觸發後續 SL；強反轉確認（ClosePos≥0.50）僅能捕捉牛市階段真實反轉但 Part B mixed regime 即零訊號。與 lesson #20b oscillator hook 失敗家族並列，但邊界判準不同：**oscillator hook 失敗依「政策驅動 + 後峰下跌 regime」分類；Post-Cap MR 失敗依「日波動 > 2.2% + 單一股票多 regime」分類**。

**新邊界（TSLA-013 驗證 2026-04-25）**：**T-1/T-2 單日或雙日報酬過濾器在突破（breakout）策略上結構性失敗**，與 MR 策略上的成功形成鮮明對比：
- **MR 策略成功案例**：USO-013（2DD floor）、EEM-014（2DD floor）、INDA-010（2DD floor）、CIBR-012（2DD cap）、DIA-012（1d+3d cap dual-dimension）
- **突破策略失敗案例**：TSLA-013 Att1/Att2（T-1 ≤ +4% upper cap + BB Squeeze Breakout）——Part A 訊號數保持 17 但 Sharpe 0.40→0.29、cum +64%→+36%
- **失敗機制**：cooldown-chain-shift（見 lesson #19）在訊號密度高、cooldown 期長的 Part A 上放大——過濾器移除某個早期訊號後，原先被 cooldown 抑制的後續訊號（常品質較差）進入訊號集
- **結構差異**：MR 進場隱含「已超賣/回檔」狀態，T-1/T-2 過濾器可在該隱含框架內選擇性過濾；突破進場則與 T-1 單日報酬下限結構性互斥（TSLA BB Squeeze 突破日 T-1 從不會 < -3%，因 BB Squeeze 要求近 5 日低波動）
- **Att2 驗證（下限 -3% 完全非綁定）**：移除下限後結果與 Att1 完全相同，確認所有過濾效果來自上限，所有副作用來自 cooldown chain shift
- **新規則**：T-1/T-2 單日/雙日報酬過濾器僅適用於 MR 策略；突破策略需改用 regime-level 過濾器（多週期波動率狀態、BB 寬度歷史百分位、趨勢持續性）而非 point-in-time 過濾器。擴展失敗邊界至 3.72% 高波動個股突破類別

---

## 20a. Gap-Down 資本化 + 日內反轉進場模式（加密相關 ETF）
<!-- freshness:
  derived_from: [IBIT-006,TQQQ-016,FXI-010]
  validated: 2026-04-18
  data_through: 2025-12-31
  confidence: medium
  note: FXI-010 (2026-04-18) extends boundary: Gap-Down reversal pattern does NOT extend to policy-driven single-country EM ETFs even when they have overnight price discovery (HK market trades when US closed). 3 iterations all failed vs FXI-005 min 0.38: Att1 (gap≤-1.5% entry trigger) min -0.51, Att2 (strict gap -2.5% + deep pullback + FXI-005 wide exit) min 0.00 too few signals, Att3 (gap as 5d regime filter + FXI-005 entry) Part A 0.34 / Part B 0.00 zero-variance 2 signals. Refined precondition: pattern requires (a) overnight continuous price discovery AND (b) selling pressure uncorrelated with policy/event continuity — FXI has (a) via HK market but Chinese policy news persists through US session, invalidating the buy-the-dip structure. TQQQ-016 (2026-04-17) validated boundary: Gap-Down reversal pattern does NOT extend to traditional (non-24/7) leveraged ETFs. 3 iterations (gap-3% / gap-2% / +volume) all min(A,B) -0.07 vs TQQQ-010 0.36. Part B 2025-04-07 Trump tariff gap-down continued declining, confirming QQQ-underlying's limited after-hours liquidity means gap-down reflects event shocks rather than capitulation.
-->

追蹤 24/7 連續交易資產（如加密貨幣）的 ETF 在美股盤外常出現隔夜跳空。「隔夜跳空下跌 ≥ 1.5% + 日內收盤高於開盤（Close > Open）」的組合代表拋壓已被盤中資金消化，為典型 buy-the-dip 訊號。

**規則**（醞釀中）：
- 基礎 MR 訊號（回檔深度 + WR 超賣）+ gap-down 過濾可改變訊號品質結構
- Gap-down 過濾為緊 SL（如 IBIT SL -4% vs 寬 -7%）的**必要前提**（IBIT-006 Att3 ablation 驗證：無過濾下緊 SL 毀滅訊號品質）
- 適用範圍：加密 ETF（IBIT 已驗證），可能延伸至有盤外交易 + 高波動的其他資產（ETHA、BITX 待驗證）
- **精煉先決條件（FXI-010 驗證後）**：需同時滿足兩項
  1. 盤外連續價格發現（overnight continuous price discovery）
  2. 拋壓不受政策/事件持續性影響（selling pressure uncorrelated with policy/event continuity）
- **不適用**：
  - 盤外交易清淡的傳統 ETF（如 SPY、GLD 的 gap 主要為開盤平衡，非結構性拋壓）
  - **傳統（非 24/7 連續交易）標的之槓桿 ETF**：TQQQ-016 三次嘗試（gap-3% / gap-2% / +volume）min(A,B) 皆 -0.07（vs TQQQ-010 的 0.36）。失敗根因：QQQ 盤外流動性有限（盤後僅占日成交量 5-10%），隔夜 gap-down 常反映盤前事件衝擊（Fed/CPI/科技巨頭財報/政策公告）而非市場投降式拋壓。事件利空可持續（如 2025-04-07 Trump 關稅公告日 gap-down + 日內反轉 + 隔日繼續深跌停損 -8%），日內反彈只是技術性反應。Part B 2024-2025 大牛市期符合 DD≤-15% + gap≤-2% 的事件僅 2 筆，統計信心不足
  - **政策驅動單一國家 EM ETF（FXI-010 驗證）**：FXI 滿足先決條件 1（HK 市場盤後交易提供連續價格發現），但**不滿足條件 2**（中國政策消息常在美股盤中持續發酵）。三次迭代（Att1 gap≤-1.5% entry / Att2 嚴格 gap+深回檔+寬出場 / Att3 gap 作為 5d regime filter）均未勝過 FXI-005 的 0.38：Att1 min -0.51（22 訊號 WR 31.8%，gap-down 後常續跌）；Att2 min 0.00（加嚴後訊號 5/1 過稀疏）；Att3 Part A 0.34 接近但 Part B 僅 2 訊號零方差。**雙重擴展教訓**：(a) lesson #52 再新增一禁忌結構；(b) 此 lesson #20a 需雙先決條件（盤外價格發現 + 拋壓獨立性）

**IBIT-006 Att2 結果**：min(A,B) Sharpe 0.40（+167% vs IBIT-001 0.15），Part A/B 訊號比 1.33:1
**TQQQ-016 結果**：Att1/Att2/Att3 三次 min(A,B) 皆 -0.07（vs TQQQ-010 的 0.36），Att3 最佳 Part A Sharpe 0.49 但 Part B -0.07 拖累 min。驗證 pattern 有效性先決條件為「基礎資產盤外真實連續交易」
**FXI-010 結果**：Att1（gap≤-1.5% entry trigger + TP+3.5%/SL-3%/20d）min -0.51；Att2（gap≤-2.5% + Close>midpoint + 深回檔 + FXI-005 寬出場）min 0.00（5/1 訊號）；Att3（Gap 作為近 5d regime filter + FXI-005 entry）Part A 0.34 最接近基線但 Part B 2 訊號零方差，所有迭代未勝過 FXI-005 的 0.38。**精煉 pattern 有效性第二條件**：除盤外連續價格發現外，還需「拋壓不受政策/事件持續性影響」，政策驅動單一國家 EM ETF 不滿足此條件

---

## 20b. RSI Bullish Hook Divergence 對高波動均值回歸有效（SIVR 驗證，COPX/FCX/URA/XBI/USO/WVF/MACD/Range Expansion/Higher-Low 失敗擴展邊界）
<!-- freshness:
  derived_from: [SIVR-015,COPX-009,FCX-009,URA-008,URA-009,URA-010,TLT-006,XBI-011,USO-022,EEM-013,CIBR-011,CIBR-013,IBIT-008]
  validated: 2026-04-26
  data_through: 2025-12-31
  confidence: medium
  note: SIVR-015 Att1 first repo validation (10-day pullback framework). COPX-009 (2026-04-18) three iterations all failed on 20-day pullback framework (min 0.45→0.15), extending pattern boundary: requires pullback lookback ≤10 days. FCX-009 (2026-04-18) three iterations Att1 min -0.33 / Att2 min -0.06 / Att3 min 0.30 all failed vs FCX-001 min 0.43. FCX 10-day framework formally meets lookback ≤10 constraint, but 2024-2025 post-peak copper decline eliminated Part B active MR regime — Part B signals dwindled 5→3→2, Part A Sharpe surged 0.51→0.76→0.85 but Part B cum diff 39-51pp consistently exceeded 30% target. URA-008 (2026-04-18) three iterations all failed (Att1 URA-004 base + hook min 0.00, Att2 remove 2DD min 0.00 with zero-variance Part B, Att3 SIVR-015 structure port with WR(10) min -0.32 Part B WR 33.3%). URA formally meets all four criteria (2.34% vol, 10d PB, URA-004 Part A 0.41/B 0.39 active MR, validated pullback+WR framework) but hook filter signal retention 25% vs SIVR's 44%, and Part B 2025-11-05 signal immediately stops out next day showing V-bounce ≠ real reversal on policy-driven uranium. URA-009 (2026-04-18) further confirmed the V-bounce failure mode extends to price-action bar confirmation (not just oscillator hook): three iterations (Att1 Close>PrevClose min -0.25 / Att2 Close>PrevHigh reclaim min 0.24 with 60%/60% WR but ~1/yr / Att3 loosen T-1 capitulation min -0.11 as WR collapsed to 43%) all failed vs URA-004 0.39. Att2's perfectly balanced A/B (0pp cum diff) showed the framework is structurally sound but signal count is unavoidable tradeoff for quality — "reclaim prior day's high" is a strong reversal filter that works quality-wise but cannot be loosened without losing its selectivity. TLT-006 (2026-04-19) three iterations cross-asset ported URA-009 Att2 framework to TLT 1.0% daily vol, all failed vs TLT-002 min -0.20: Att1 (pullback -3%/-8% + WR≤-85 + 2DD≤-1.5% + Close>PrevHigh + Close>Open) Part A 15 signals WR 40% Sharpe -0.37 / Part B 3 signals 100% WR zero-variance, 8 SLs concentrated in 2022 Aug-Sep + 2023 May-Sep hiking cycle; Att2 (tighten to WR≤-90 + 2DD≤-2.5% + pullback -4% + Range expansion ≥1.2x) Part A 3 signals WR 66.7% Sharpe 0.16 / Part B 0 signals (over-tightened); Att3 (2DD≤-2.0% + Range ≥1.15x + cd 10 middle ground) Part A 5 signals WR 40% Sharpe -0.39 / Part B 0 signals. Extends lesson 20b failure mode from **nuclear-policy-driven** (URA) to **interest-rate-policy-driven** (TLT): Day-After Capitulation + price-action reversal filter fails on TLT because (a) "Close > Prev High" reclaim occurs frequently during 2022-2023 sustained hiking declines without predicting genuine reversal, and (b) tightening capitulation+range-expansion thresholds causes immediate Part B depletion in TLT 2024-2025 high-for-longer plateau. TLT's "no pure technical solution" conclusion now covers Day-After Capitulation reversal pattern as well. Two data points (URA nuclear + TLT rates) confirm lesson #20b's 5th criterion ("RSI turn = genuine reversal" structure) generalizes beyond RSI to any single/dual-bar reversal confirmation on policy-driven assets. XBI-011 (2026-04-18) three iterations all failed despite XBI meeting four prior criteria (2.0% daily vol, 10-day pullback+WR framework, ClosePos filter, both Parts active MR regime): Att1/Att3 (max_min ≤ 35) too strict (3/2 zero-variance samples), Att2 (max_min ≤ 40) introduces Part A stop-losses (Sharpe 0.27 < XBI-005 0.36). New 6th criterion: XBI biotech pullback+WR signals land in RSI(14) 35-45 range, not SIVR's ≤35 deep-oversold range — hook divergence pattern further requires asset's signal-day RSI(14) distribution to be concentrated in deep oversold (≤35). Event-driven sector ETFs (biotech FDA/clinical) see compressed 1-2 day declines that don't saturate RSI(14) to deep oversold, while macro-driven assets (precious metals SIVR) see persistent declines that do. Refined pattern boundary: requires asset to have "RSI turn = genuine reversal" structure — event/policy-driven assets (URA nuclear policy, FXI policy, TLT rates) fail even when volatility/framework/regime conditions formally met, and the failure mode generalizes beyond RSI hook to any single/dual-bar reversal confirmation (oscillator OR price-action).
-->

**規則**：在已有 pullback+WR 均值回歸框架的高波動資產上，可疊加 **RSI(14) bullish hook divergence** 作為額外過濾，捕捉「RSI 已從近期 oversold 低點回升」的 capitulation 尾聲訊號，移除「RSI 仍在下探」的持續下跌訊號。

**具體條件（SIVR-015 Att1 驗證）**：
- RSI(14) 今日 − RSI(14) 過去 5 日最低點 ≥ 3 點（hook delta）
- 過去 5 日 RSI(14) 最低點 ≤ 35（確保 divergence 發生在 oversold 區間）

**有效條件（六項必須同時符合）**：
1. **中高波動資產**（日波動 2-3%）
2. **已驗證 pullback+WR 類均值回歸框架**
3. **回檔回看窗口 ≤10 日**（COPX-009 新增：20 日回檔框架下 hook 過濾失效）
4. **Part A/B 兩段皆存在活躍 mean reversion regime**（FCX-009 新增：post-peak 持續下跌期 Part B 訊號稀薄至 ≤3 筆時 min(A,B) 無法成立）
5. **資產具備「RSI 轉折 = 真實反轉」的結構**（URA-008 新增：URA 符合前四條件但 Part B 仍 -0.32，事件/政策驅動資產 hook filter 無法區分「V-bounce 暫時回彈」與「真實見底」）
6. **訊號日 RSI(14) 分布集中於深度 oversold（≤ 35）**（XBI-011 新增：XBI pullback+WR 訊號 RSI 多在 35-45 區間未達深度 oversold，hook 過濾器失去選擇性；事件驅動板塊下跌集中短促使 RSI 未飽和）
- 其他子條件：RSI 週期需為 14（RSI(7) 過噪，SIVR 翻負）；hook lookback 5 日最佳（7 日納入過舊 RSI 低點）；hook delta 3 點最佳於活躍 regime（SIVR），低波動資產可能需 5 點以上（FCX-009 Att2）；2 點太鬆納入噪音

**效果（SIVR-015 Att1 vs SIVR-005，10 日回檔框架）**：
- Part A Sharpe 0.22 → **0.48**（+118%）
- Part B Sharpe 0.26 → **1.41**（+442%）
- WR 62.5%/63.6% → **75.0%/66.7%**
- 訊號頻率下降至 1.5-1.6/年（SIVR-005 為 5.5-6.4/年）
- A/B 年化訊號率比 1.07:1（極佳平衡）

**反例（FCX-009，10 日回檔框架但 Part B regime 失效）**：三次迭代全部失敗，min(A,B) -0.33→-0.06→0.30 均低於 FCX-001 基線 0.45：
- Att1（delta=3 移植 SIVR-015 參數）：Part A Sharpe 0.51 / Part B -0.33（5 訊號 WR 40%），2024-07-29 深跌中 -10.13% 4日停損，delta=3 放行局部 RSI 反彈假訊號
- Att2（加嚴 delta 3→5）：Part A Sharpe 0.76 / Part B -0.06（3 訊號），hook 成功濾除 Part A 假訊號，但 Part B 2024-11/12 雙筆 20 天到期虧損拖累
- Att3（加深 pullback -9%→-11%）：Part A Sharpe 0.85 / Part B 0.30（2 訊號），深回檔門檻濾除 Part B 淺訊號，兩段皆轉正但 Part B 樣本過薄（2/yr）且 A/B 累計差 39pp 仍超目標
- **失敗根因**：FCX 2024-2025 銅價 post-peak 持續下行，Part B 缺乏活躍的 mean reversion 動能（到期損失而非達標），hook divergence 過濾器無法挽救 regime 問題。與 SIVR 同為 2-3% 日波動且 10 日框架，但 SIVR 2024-2025 銀價/避險需求維持活躍 MR regime，FCX 銅價則進入長期回檔

**反例（COPX-009，20 日回檔框架）**：三次迭代全部失敗，min(A,B) 0.45→0.15（-67%）：
- Att1（ATR+hook lookback 5）：Part A Sharpe -0.50，hook 反移除 Part A 好訊號（21→6 訊號，WR 76.2%→33.3%）
- Att2（ATR+hook lookback 10）：Part A 0.00，延長 lookback 略改善但無法恢復品質
- Att3（純 hook lookback 10）：Part A 0.15/Part B 0.57，移除 ATR 恢復 Part B 但 Part A 仍劣於 COPX-007
- **失敗根因**：COPX 20 日回檔框架下訊號常發生在延續性下跌中（持續 15-30 日），RSI(14) 在此期間多次 hook up-down；5-10 日 hook 窗口捕捉的是局部 RSI 雜訊而非真正 capitulation 末端

**反例（XBI-011，10 日回檔+事件驅動板塊）**：三次迭代全部失敗，XBI-005 min(A,B) 0.36 維持為全域最優：
- Att1（5 / 3.0 / 35，SIVR 原始參數）：Part A/B 3/2 訊號全 +3.50% TP 零方差，Sharpe 0.00（過嚴）
- Att2（5 / 3.0 / 40，放寬 oversold 門檻）：Part A Sharpe 0.27（7 訊號，2 筆停損，WR 71.4%）/Part B 2/2 零方差，**Part A 壞訊號引入使 Sharpe < XBI-005**
- Att3（5 / 2.0 / 35，放寬 delta）：同 Att1，因 max_min=35 為綁定條件
- **失敗根因**：XBI pullback+WR+ClosePos 訊號日，RSI(14) 5 日最低點多在 35-45 區間（非 SIVR ≤ 35 深度 oversold）。生技板塊 FDA/臨床事件驅動使下跌集中且短促（1-2 日），RSI(14) 尚未飽和至深度 oversold 即已反彈。失敗首次揭示 pattern 有效性除波動率（2-3%）與框架（pullback+WR+回看 ≤10 日）外，還需要**訊號日 RSI 分布結構**——宏觀因子驅動類資產（貴金屬 SIVR）下跌持續使 RSI 深度 oversold，事件驅動板塊（生技 XBI）下跌短促使 RSI 僅淺層 oversold

**反例（USO-022，10 日回檔+商品 event-driven）**：三次迭代全部失敗，USO-013 min(A,B) 0.26 維持為全域最優：
- Att1（USO-013 進場 + hook delta≥3/max_min≤35）：Part A 3 訊號全 TP 零方差 Sharpe 0.00 / Part B 0 訊號，USO-013 的 RSI(2)<15 + 2DD≤-2.5% 要求當日 RSI 新低，與 hook delta ≥ 3 要求 RSI 已回升結構性互斥
- Att2（移除 2DD，pullback + RSI(2) + hook）：Part A 4 訊號仍全 TP 零方差 / Part B 0 訊號，核心矛盾未解
- Att3（SIVR-015 pattern 直移：pullback 7-12% + WR(10)≤-80 + hook）：Part A Sharpe 0.51（4 訊號 WR 75%）/ Part B Sharpe -0.06（2 訊號，2024-09-10 SL + 2025-10-20 TP）。Att3 揭示 hook 在 Att1/Att2 的進場條件矛盾被 SIVR 架構消解後，Part B 仍因 event-driven SL 失敗
- **失敗根因**：USO 油價由 OPEC 決策、地緣政治、庫存數據驅動，2024-09-10 供應過剩預期觸發 V-bounce 後續跌停損。USO 形式上符合前四條件（日波動 2.2%、USO-013 已驗證、10 日框架、Part A/B 皆活躍 MR）但**不滿足第五項「RSI 轉折=真實反轉」結構**——商品 event-driven 與 URA/TLT 政策驅動同歸此失敗類別。USO 成為 hook divergence 第 7 個失效資產（URA/FXI/TLT/XBI/COPX/FCX 之後）

**反例（CIBR-011，single-bar Range Expansion 主訊號 — 跨指標家族擴展至 US 板塊 ETF）**：三次迭代全部失敗，CIBR-008 Att2 min(A,B) 0.39 維持為全域最優。本實驗以 **單日 TR/ATR(20) ≥ 2.0 + ClosePos ≥ 50%** 作為 Range Expansion Climax 主訊號（IBIT-008 模式跨資產移植），仍在 CIBR 1.53% vol 板塊 ETF 失效：
- Att1（TR/ATR ≥ 2.0 + ClosePos ≥ 50% + 10日回檔 [-3%,-10%] + WR(10) ≤ -70）：Part A 3 訊號 WR 33.3% Sharpe **-0.44**（2020-02-24 COVID 前夕 + 2021-09-20 Evergrande 兩筆 SL）/ Part B 2/2 100% WR 零方差 0.00 / min -0.44，訊號稀缺（5 訊號 8 年、0.6/yr）
- Att2（放寬 TR ≥ 1.7 + 收窄 cap -8% + ATR(5)/ATR(20) > 1.10）：Part A 2/50% Sharpe -0.08 / Part B 2/50% Sharpe -0.29 / min -0.29，**ATR > 1.10 反向移除好訊號**（Part B 2024-02-21、2024-08-05 兩筆 winners 的 ATR < 1.10 環境被過濾，shifts 至 2025-03-04 SL）
- Att3（反向 ATR ≤ 1.10 測試「平靜 + 突發爆發 = 真 capitulation」假設，平行 EEM-013 反向 ATR 發現）：Part A 2 訊號 **WR 0%**（兩筆 SL）/ Part B **0 訊號** / min 0.00，反向 ATR 移除所有 Part B 訊號並保留 Part A 事件早期下殺後續跌
- **失敗根因**：(1) 訊號稀缺性（與 IBIT-008 平行，Range Expansion + ClosePos 雙硬性過濾在 8 年資料僅 5 訊號）；(2) Range Expansion 本身無「真/假反轉」區分力；(3) **ATR 過濾器無單向有效性**——CIBR Range Expansion 訊號的 ATR 環境與真假反轉**無關聯**，ATR 為 noise 而非品質訊號；(4) 與 CIBR-008 BB Lower 框架的結構性差異——BB 下軌為**統計自適應**進場（隨 BB std 自動縮放），Range Expansion 為**單日點估計**進場，缺乏統計選擇性
- **拒絕 IBIT-008 跨資產假設**：「Range Expansion MR 可能適用傳統（非 24/7）US 板塊 ETF」於 CIBR 1.53% vol 上不成立。Range Expansion 失敗家族雙向擴展：(a) 高波動 24/7 加密 ETF（IBIT 3.17%）、(b) 中波動傳統 US 板塊 ETF（CIBR 1.53%）。**整合 entry-time filter 失敗 meta-rule**：所有 entry-time 過濾器類型（oscillator hook RSI/CCI/Stoch/CRSI/MACD、day-after price-action reversal、capitulation-depth WVF、single-bar range expansion）在「事件驅動 + 缺乏統計自適應進場框架」下結構性失效。Entry-time filter 有效性的兩項結構先決條件：(1) 統計自適應主訊號（BB std 自動縮放，非單日點估計）；(2) 訊號頻率 ≥ 1.5/yr per part 以支撐 WR-based 區分。Range Expansion 兩項皆失敗

**反例（CIBR-013，multi-bar swing-structure pattern — 跨指標家族首次擴展至多日結構維度）**：三次迭代全部失敗，CIBR-012 Att3 min(A,B) 0.49 維持為全域最優。本實驗將「單日 pattern」擴展為「多日 Higher-Low 結構 pattern」測試是否可繞過 CIBR-009/010/011 三次單日 price-action 失敗的根因。**Repo 首次將多日 swing 結構 pattern 作為 MR 主過濾器於任何資產**：
- Att1（pullback+WR+Higher-Low(3)+Bullish bar+ATR>1.10，5 重交集）：Part A 2/50%/Sharpe **-0.08** cum -0.74%（1 TP 2023-04-27 +3.5%、1 SL 2022-04-28 -4.10%）/ Part B **0 訊號** / min **-0.08**。5 重交集訊號密度 0.4/yr 過稀
- Att2（放寬 ATR=1.00 + Higher-Low lookback 3→5）：Part A 3/33.3%/Sharpe **-0.44** cum -4.81% / Part B 1 訊號 zero-var TP +3.5% / min **-0.44**。放寬條件引入「中段反彈失敗」型態 SL
- Att3（BB Lower 框架 + Higher-Low(5)，取代 CIBR-012 的 2DD cap）：Part A **0 訊號** / Part B **0 訊號** / min **0.00**。**結構性互斥重要發現**：BB Lower 觸及（Close ≤ BB_lower）日為統計極端下殺，今日 Low 幾乎必為近 5 日新低；而 Higher-Low(5) 要求今日 Low > min(Low[t-5..t-1])，兩條件在 CIBR 1.53% vol 板塊 ETF 上幾乎完全互斥（過去 8 年僅 1 訊號於 Part C 觸發）
- **核心發現**：(1) **多日 swing 結構維度並未繞過單日 pattern 的失敗根因**——擴展 lesson #20b 失敗家族至**多日結構 pattern (Higher-Low Confirmation)**；(2) **BB Lower 與 Higher-Low 結構性互斥**——統計極端進場（單日 panic）與多日反轉確認（已建立 swing low）在低-中波動板塊 ETF 上不可組合；(3) 純 pullback+WR 框架下 5 重交集訊號密度過低；(4) 放寬條件引入低品質訊號。CIBR's 8th 失敗策略類型，**lesson #20b 失敗家族跨維度擴展**：從單日 pattern（oscillator hook、price-action reversal、capitulation depth、range expansion）擴展至**多日結構 pattern（Higher-Low Confirmation）**——確認「entry-time confirmation 結構性無區分力」原則跨越時間尺度（單日 / 多日）。

**反例（URA-010，capitulation-depth 指標 — 跨指標家族擴展）**：三次迭代全部失敗，URA-004 min(A,B) 0.39 維持為全域最優。本實驗以 **Williams Vix Fix（WVF）= (max(Close,N)−Low)/max(Close,N)×100** 取代 hook，WVF 結構性與 oscillator turn-up 完全不同（純 capitulation 深度極值，非反彈確認），仍在 URA Part B 失效：
- Att1（WVF(22)>BB_upper(20,2.0) + 10d 回檔 [-8%,-25%] + cd=10）：Part A 23/65.2%/0.33 / Part B 11/45.5%/-0.06——Part B 6/11 SL 集中於持續下跌段（2024-02/06/10、2025-02/10/11），WVF spike 後續跌
- Att2（+ 2DD ≤ -3%）：Part A 退至 21/61.9%/0.25 / Part B 完全相同 11/45.5%/-0.06——2DD 對 WVF 結構性非綁定
- Att3（+ 加深回檔下限至 -10%，URA-004 標準）：Part A **13/76.9%/0.68**（URA in-sample 最高）/ Part B 8/50%/0.04（A/B 累計差 50pp）
- **失敗根因**：URA-010 為 lesson #20b 失敗家族首次擴展至**capitulation-depth 指標**（前述失敗皆為 oscillator turn-up 或 single/dual-bar reversal）。整合規則：URA 為政策驅動資產，**任何 entry-time 過濾器**（無論 oscillator turn-up、single/dual-bar reversal、或 capitulation-depth metric）均無法在 Part B 2024-2025 V-shaped + post-rally crash regime 區分真假底部
- **正面發現**：Att3 Part A Sharpe 0.68 顯示「WVF + 深回檔」在 in-sample（URA Part A 含 2020 COVID + 2022 鈾礦熊市 + 2023 復甦）為高品質訊號生成器。跨資產假設：可能適用於 SIVR/COPX 等 Part A/B 兩段皆活躍 MR regime 的 2-3% vol 資產；不適用於 FXI/TLT 等政策驅動資產（類比 URA Part B 失敗模式）。WVF 為 repo 首次試驗指標

**跨資產泛化假設（待進一步驗證）**：可能適用於其他**日波動 2-3% + 回檔回看窗口 ≤10 日 + 兩段 Part A/B 皆活躍 MR regime + RSI 轉折=真實反轉結構 + 訊號日 RSI(14) 分布集中於 ≤ 35 深度 oversold**且已驗證 pullback+WR 框架的資產。**低波動資產**（GLD、SPY、EWJ、VGK）divergence 訊號可能過於稀少；**政策/事件驅動資產**（FXI、TLT、URA）可能因 RSI 特徵受宏觀事件影響而失效；**長回檔窗口資產**（COPX 20 日）已確認失效；**post-peak 持續下跌資產**（FCX 2024-2025 銅價）因 Part B regime 失效而失敗；**核能政策驅動資產**（URA）雖符合前四條件但 hook filter 訊號保留率僅 25%（vs SIVR 44%）且 Part B V-bounce 假訊號過多而失敗（URA-008 驗證）；**事件驅動板塊 ETF**（XBI 生技）因 RSI 僅淺層 oversold 而失效（XBI-011 驗證）；**商品 event-driven ETF**（USO 油價 OPEC/地緣政治）亦失效（USO-022 驗證）；**事件驅動個股**（TSLA）可能同樣失效，需謹慎評估訊號日 RSI 分布再測試。整合觀察：有效資產需滿足 (a) 波動率 2-3%、(b) 持續性下跌使 RSI 飽和至 ≤35、(c) 非事件驅動（macro-factor 驅動優於 event/policy 驅動）。**lesson #20b 失敗模式跨指標家族延伸（URA-010 + CIBR-011 新增）**：URA-010 將失敗家族首次從 oscillator hook（RSI/CCI/Stoch/CRSI）+ price-action bar（day-after reclaim）擴展至 **capitulation-depth 指標（WVF）**。CIBR-011（2026-04-20）進一步將失敗家族擴展至 **single-bar range-expansion 指標（TR/ATR ≥ 2.0 + ClosePos ≥ 50%）**，並從加密 ETF（IBIT-008）擴展至傳統 US 板塊 ETF（CIBR）。在政策/事件驅動資產（URA、CIBR、IBIT）上，任何 entry-time 過濾器類型（oscillator turn-up、single/dual-bar reversal、capitulation depth metric、single-bar range expansion）皆失效，揭示「entry-time confirmation 在事件/政策驅動或缺乏統計自適應進場框架的 Part B regime 結構性無區分力」的更深層原則。**Entry-time filter 有效性的兩項結構先決條件**（CIBR-011 新增）：(1) 統計自適應主訊號（BB std 自動縮放，非單日點估計）；(2) 訊號頻率 ≥ 1.5/yr per part 以支撐 WR-based 區分。WVF + 深回檔模式在 URA Part A in-sample（含 2020 COVID + 2022 熊市 + 2023 復甦）Sharpe 0.68，跨資產延伸性待 SIVR/COPX 驗證。

**與 SIVR-007 Att1「RSI(14) 動能回復」的關鍵差異**：SIVR-007 僅要求 RSI > 5日最低值（單側門檻，無 delta 閾值、無 oversold 前提），SIVR-015 雙重條件更嚴格鎖定 classical divergence 結構。

---

## 20. 跨資產相關性配對策略的結構性風險
<!-- freshness:
  derived_from: [XLU-005,COPX-006,SIVR-009,TSM-009,FCX-006,DIA-009,EEM-006,TLT-008]
  validated: 2026-04-23
  data_through: 2025-12-31
  confidence: high
-->

跨資產相關性可能隨宏觀環境改變而失效（regime change）。Part A 正 + Part B 負 Sharpe 是相關性崩潰的典型特徵。個股 vs 板塊 ETF RS 策略僅在個股有持續性結構優勢（如 TSM 先進製程護城河）時有效，商品生產者（FCX）的超額表現由短期事件驅動，無持續性。廣基 ETF RS（如 EEM vs SPY）受宏觀/政治事件（關稅、貿易戰）驅動，三次嘗試 Part B 均為負值。

**TLT-008 擴展（2026-04-23）：同資產類別但不同 duration 的機械性 pair 亦結構性失敗**。TLT vs IEF duration spread MR 三次迭代全失敗（min(A,B) -5.92/-1.71/-0.31 vs TLT-007 Att2 的 0.12）：
- Att1 純 pair（10d spread ≤ -2% + ClosePos + BB<5%）：Part A 4/0% WR，訊號全部集中於 2020-05 至 2021-02 TLT 熊市啟動初期
- Att2 hybrid（TLT-007 Att2 框架 + 10d spread ≤ -1.5%）：Part A 6/0% WR，**Part B 6→0 訊號（贏家全被過濾）**
- 反向方向測試（5d spread ≥ +0.3%）：所有 part 0 訊號（TLT 在自己 pullback 期間機械性必弱於 IEF）
- Att3 z-score（100d ≤ -1.5σ）：Part A 6/33.3%/-0.31，z-score 統計標準化無法救

**根因**：TLT 與 IEF 的相對表現由 duration 敏感度比例機械決定（TLT 對利率敏感度約 IEF 的 2.4 倍），並非「獨立個體偏離後回歸」的經典 pairs MR 結構。**規則擴展**：跨資產相關性配對策略的結構性風險不僅適用於「跨資產類別」，**同資產類別但存在機械性 beta/duration 關係的 pair**（如 TLT vs IEF、SPY vs SPLG 等）亦失效。經典 pairs MR 先決條件為「兩個獨立個體其短期偏離後向結構性均衡回歸」，機械性衍生物（如 duration 放大版 ETF、槓桿 ETF、ETF vs 其成分股平均）不滿足此前提。

---

## 21. Momentum Breakout Pullback Continuation（MBPC）需要單一純上升 regime 資產（VOO-004 確認 broad-uptrend ETF 可成功）
<!-- freshness:
  derived_from: [FXI-012,NVDA-009,VOO-004]
  validated: 2026-04-25
  data_through: 2025-12-31
  confidence: medium
-->

Momentum Breakout Pullback Continuation（MBPC，Donchian 新高 freshness + 淺回檔 + SMA 趨勢 + RSI 中性 + 多頭 K 棒）為經典趨勢跟蹤 / 動量延續結構（類似 Mark Minervini VCP 理念）。repo 已累積 3 個資料點，**2 失敗、1 成功**：

**FXI-012（2026-04-21，repo 首次 MBPC 試驗）**：
- Att1 Baseline / Att2 + 黃金排列 / Att3 + SMA(50) slope positive：三次迭代 min(A,B) -0.09 / -0.11 / -0.21 全部劣於 FXI-005 的 0.38
- 失敗機制：**政策驅動 EM 假突破**——2019-2023 中國熊市期 Donchian 新高多為熊市反彈假突破（Part A WR 42.3%），且 SMA slope 已轉正時往往已錯過最佳進場點（Att3 雙向惡化）
- FXI 為政策/事件驅動（貿易戰、監管、疫情、刺激政策），regime 轉換期突破頻繁失效

**NVDA-009（2026-04-24，repo 第 2 次 MBPC 試驗，首次高波動個股測試）**：
- Att1 Baseline（Donchian 20d 近 10 日內新高 + 5d 淺回檔 -3~-8% + SMA(50) + RSI[40,65]）：Part A 34/67.6%/**0.41** cum +142.32% / Part B 8/75%/**0.96** cum +47.30% / min **0.41**（低於 NVDA-004/NVDA-006 的 0.47）
- Att2（+ SMA(200) regime gate + RSI_max 60）：**非選擇性過濾**，訊號 -38% 但 WR 僅 -0.9pp，移除贏家多於 SL → Part A 退化至 0.38
- Att3a（2DD cap >= -6% CIBR-012 方向）：完全無綁定（NVDA 突破+淺回檔 2d 報酬典型 -3%~-5%）
- Att3b（2DD cap >= -4%）：cap 與淺回檔範圍部分重疊且 cooldown-shift 引入新 SL，Part A 0.33 / Part B 0.49
- **失敗機制差異於 FXI**：NVDA Part A WR 67.6% 已不差，失敗來自 2021 late-bull + 2022 bear + 2023 summer chop 三段**混合 regime**產生 11 筆 SL 拉低 Sharpe 標準差

**VOO-004（2026-04-25，repo 第 3 次 MBPC 試驗，首次成功 — broad-uptrend ETF 假設驗證）**：
- Att1 Baseline（Donchian 20d 近 10 日內新高 + 5d 回檔 [-1.5%, -4%] + SMA(50) + RSI[40,60] + Close>Open + cd10, TP+3.0%/SL-2.5%/20d）：Part A 19/52.6%/**0.12** / Part B 10/60.0%/**0.36** / min **0.12**（遠低於 VOO-003 的 0.53）。9 筆 Part A SL 集中於 macro-shock 日（Fed pivot/Omicron/2022 bear/Powell hawkish/Fitch downgrade）
- Att2（+ SMA(200) regime gate）：Part A 15/53.3%/0.14 / Part B 9/55.6%/0.27 / min 0.14——非選擇性過濾（同 NVDA-009 Att2 模式），SMA(200) 在 2022 bear 期過濾 bull-trap rallies 中的 TPs
- Att3 ★（還原 SMA(200), breakout_recency 10→5d + pullback range [-1.5%,-4%]→[-2%,-3%]）：Part A 7/85.7%/**1.12** cum +16.30% / Part B 2/100% std=0/**0.00** cum +6.09% / min **1.12†**（沿用 EWJ-003/DIA-012/SPY-009 慣例 Part A 為約束）
- A/B 平衡：年化 cum 差 2.3%（< 30% ✓ 極佳）/ 年化訊號比 1.4:1（28.6% gap < 50% ✓）
- **改善機制**：breakout_recency 5d 排除 stale breakout（觸發後 6-10 日才回檔已失動能），pullback [-2%,-3%] 窄帶過濾邊緣 -1.5% 噪聲與 -4% 邊緣（深跌前兆），9 筆 macro-shock SL 中 8 筆被過濾，僅保留 2022-01-10 hawkish Fed 真實 bear 開端
- **VOO 為純 broad-uptrend ETF**：S&P 500 自 2010 上市年化 +12-13%，2019-2025 期間僅 2020-03 COVID + 2022 升息為顯著 bear regime（短暫且結構單純），符合 MBPC 有效先決條件
- **進場參數敏感度（呼應 lesson #4）**：breakout_recency 10→5d + pullback range 收緊使 min(A,B) 從 0.12→1.12（+833%）

**整合規則（MBPC 有效性邊界）**：
- **有效先決條件**：資產處於**單一純上升 regime**或**主要為 broad-uptrend 的廣基 ETF**
    - 純趨勢期（NVDA 2024-2025 AI 主升段 Part B Sharpe 0.96）
    - **broad-uptrend ETF**（VOO-004 Att3 Part A 0.85 WR + 1.12 Sharpe，repo 首次成功）
- **結構性失敗條件**：
    - **政策/事件驅動 regime**（FXI 中國政策、URA 核能政策、TLT 利率政策）
    - **多 regime 混合 + 個股 bubble cycle**（NVDA bubble 2021 + bear 2022 + chop 2023 + bull 2024-25）
    - **low-vol 慢磨 regime**（推測，待驗證）

**規則**：MBPC 在「純結構性上升趨勢資產」（廣基 S&P/Dow/Nasdaq ETF、純牛市個股）有效，在多 regime 或事件驅動資產失效。

**進場精煉 vs regime 閘門選擇（VOO-004 + NVDA-009 共同教訓）**：
- **regime 閘門（SMA(200)）為非選擇性過濾**：在兩個資產上都失敗
- **進場層精煉（breakout_recency + 窄帶 pullback）為勝出方向**：VOO-004 Att3 證明
- **規則**：MBPC 框架下優先收緊 breakout 新鮮度與 pullback 範圍，而非加入長均線 regime 閘門

**跨資產假設（待續驗證）**：MBPC 可能在 SPY、DIA（同 broad-uptrend ETF 類別）中有效，VOO-004 已建立先例。在**週期性 / 事件驅動 / 多 regime 資產**（FXI、URA、TLT、INDA、EEM、NVDA、FCX）中已被驗證結構性劣化。

---

## 22. Buffered Multi-Week SMA Trend Regime 對 BB Squeeze breakout 高波動單股有效（TSLA-015 確認，**NVDA-012 跨資產再確認 + k 值精煉 2026-04-26，FCX-013 商品/礦業單股反向發現 + k=1.00 嚴格甜蜜點 2026-04-27**）
<!-- freshness:
  derived_from: [TSLA-013,TSLA-015,NVDA-012,FCX-013]
  validated: 2026-04-27
  data_through: 2025-12-31
  confidence: medium
-->

TSLA-013 提出跨資產假設：「breakout strategies on high-vol stocks may require regime-level filters (vol state, multi-week trend regime) rather than T-1/T-2 single-day filters」。TSLA-015 三次迭代驗證並精煉此假設，**NVDA-012（2026-04-26）為第二次跨資產驗證並精煉 k 值資產相依性**：

**規則**：在已有 BB Squeeze breakout 框架的高波動單一個股上（>3% 日波動），可疊加 **buffered multi-week SMA trend regime** 過濾器：

```
SMA(20) ≥ k × SMA(60)，其中 k ≈ 0.99（1% 緩衝）
```

**緩衝閾值 k 為關鍵且資產相依**（NVDA-012 跨資產驗證精煉）：
- k = 1.00（嚴格 SMA20 > SMA60）：因 cooldown chain shift 失敗（TSLA-015 Att1：min 0.37）。borderline transition 訊號（如 SMA20/SMA60 = 0.994）被過濾，cooldown 被解除使下一日 borderline 訊號獲准進場成 SL
- **TSLA k = 0.99（1% 緩衝）為甜蜜點**（TSLA-015 Att2/Att3：min 0.53，3.72% 日波動）。精準分隔 transition winners（比率 0.99-1.00）與 bear regime SLs（比率 < 0.99）
- **NVDA k = 0.97（3% 緩衝）為甜蜜點**（NVDA-012 Att2：min 0.51，2.5-3% 日波動）。NVDA-012 三次迭代精準鎖定：Att1 k=0.99 失敗（min 0.41，誤殺 2025-05-13 transition winner）→ Att2 k=0.97 成功 → Att3 k=0.98 又失敗（min 0.41）。**NVDA AI growth stock 的 transition signals SMA20/SMA60 比率落於 0.97-0.99 區間**，需更寬緩衝；TSLA 高波動使 SMA 變動更劇烈，1% 即足
- **k 值跨資產不可直接移植**：lesson #22 規則需依資產 transition signal 的 SMA20/SMA60 比率分布調整。建議首次測試 k=0.99，若 transition winners 被誤殺則放寬至 0.97-0.95 範圍
- **FCX k = 1.00（嚴格無緩衝）為甜蜜點**（FCX-013 Att3：min 0.55，~3% 日波動 commodity/礦業單股）。**Repo 第 3 次 lesson #22 試驗、首次商品/礦業單股驗證**——三次迭代精準鎖定：Att1 k=0.99（TSLA 移植）min 0.44 +7%（Part B 大幅改善但 Part A 退化）→ Att2 k=0.97（NVDA 移植）min 0.41 持平 baseline → **Att3 k=1.00 嚴格 SUCCESS** min 0.55 (+34%) 雙向改善。**反向發現**：FCX 反轉 lesson #22 「k<1 緩衝」原則，原因是 **FCX winners 在 transition zone 0.93-1.00 的分布密度結構不同**——TSLA winners 集中 0.99-1.00、NVDA 跨 0.97-1.00、**FCX 集中 0.93-0.97 + bull-regime（>1.0）主導**，0.97-1.00 區間結構性無 winners（僅 1 筆 ratio 1.013 自然保留），故 k=1.00 嚴格僅濾除該區間 SLs（如 Part B 2025-08-26 ratio 0.972）而無 winner 代價

**效果（TSLA-015 Att3 vs TSLA-009 Att2，BB Squeeze breakout）**：
- Part A WR 58.8% → **72.7%**（+14pp）
- Part A Sharpe 0.40 → **0.84**（+110%）
- Part B 完全保留 baseline 6/6 訊號（無 cooldown shift）
- min(A,B) 0.40 → **0.53**（+33%）
- A/B 年化 cum 差 3.3%（< 30% ✓）/ 年化訊號比 1.36:1（< 1.5:1 ✓）

**ATR vol regime 對 BB Squeeze 框架冗餘（TSLA-015 Att3 消融確認）**：
- TSLA-015 Att2 同時包含 buffered SMA + ATR(20) ≤ 1.40 × ATR(60) vol regime
- Att3 移除 vol regime（`use_vol_regime = False`），結果**完全相同 Att2**
- 所有 19 個訊號日的 ATR(20)/ATR(60) ≤ 1.383 < 1.40，閾值從未觸發
- **根因**：BB Squeeze 進場條件本身已隱含「近期低 vol」要求（BB Width ≤ 60d 30th percentile），疊加 ATR vol filter 訊號日天然滿足，無區分力

**有效條件（FCX-013 跨資產確認後更新）**：
1. **中-高波動單一個股（≥2.5% 日波動）**：TSLA 3.72%、NVDA ~3%、FCX ~3% 三資產驗證；vol 上限暫未測得
2. 已驗證 BB Squeeze breakout 框架（TSLA-009 Att2、NVDA-004、FCX-004 三資產驗證；SOXL-010 等待測試）
3. 多 regime 變異性（多空交替使 SMA regime 有真實選擇力）
4. **k 緩衝為資產相依**（FCX-013 精煉，覆蓋緩衝 vs 嚴格雙方向）：
   - 通用搜尋網格 [1.00, 0.99, 0.97, 0.95]
   - 高波動（>3.5%）AI/科技牛市個股：試 k=0.99（TSLA 模式）
   - 中波動（2.5-3.5%）transition winners 廣分布個股：試 k=0.97（NVDA 模式）
   - **商品/礦業/週期性個股，bull regime 主導 SLs 且 winners 集中 ratio < 0.97**：試 k=1.00 嚴格（FCX 模式）
   - 判斷準則：先 trade-level 分析 baseline 失敗 SL/winners 在 SMA20/SMA60 ratio 分布——若 bear regime 有 SL 集中則 buffered k<1，若 transition zone (0.97-1.00) 無 winners 則 k=1.00 嚴格

**反例對比（lesson #21 MBPC 框架）**：
- VOO-004 / NVDA-009 在 MBPC 框架下，SMA(200) regime gate 為**非選擇性過濾**
- 差異：MBPC 已含 SMA(50) 趨勢條件（隱含中期趨勢），疊加 SMA(200) 重複；BB Squeeze 框架僅含 SMA(50) 短期趨勢，疊加 multi-week SMA(20)/SMA(60) regime 提供新維度資訊（短期 vs 中期趨勢的相對比較，非絕對位置）
- **整合規則**：multi-week SMA regime 在 BB Squeeze 上有效（buffered 形式），在 MBPC 上冗餘

**直接驗證 TSLA-013 假設**：
- ✅ 「multi-week trend regime」hypothesis 確認（buffered 形式有效）
- ❌ 「vol state regime」hypothesis 在 BB Squeeze 框架被消融證實冗餘
- ✅ 對比 single-day 過濾器（T-1 cap、SMA extension cap）系統性失敗，regime-level 過濾為突破策略高波動個股的正確方向

**跨資產假設（FCX-013 確認後更新）**：multi-week SMA regime 已確認三資產有效（k 值因資產異）：
- ✅ TSLA（TSLA-015 Att2，3.72% vol，k=0.99 buffered）：min 0.40→0.53（+33%）
- ✅ NVDA（NVDA-012 Att2，~3% vol，k=0.97 buffered）：min 0.47→0.51（+9%）—— **首次突破 NVDA 結構性 Sharpe 上限 0.47**
- ✅ **FCX（FCX-013 Att3，~3% vol，k=1.00 嚴格）：min 0.41→0.55（+34%）—— repo 首次商品/礦業單股驗證、首次「k=1.00 嚴格」甜蜜點、跨資產反向發現**
- 待測試：SOXL（SOXL-010 板塊 RS 動量回調，可能延伸至 BB Squeeze 框架）、其他 ≥2.5% 日波動個股的突破策略

**規則簡化**：中-高波動單一個股 BB Squeeze breakout 策略中，使用 **SMA(20) ≥ k × SMA(60)** 為主要 multi-week regime 過濾器（k 依資產調整：TSLA k=0.99、NVDA k=0.97、**FCX k=1.00**），**毋需額外 ATR vol regime**（squeeze 已隱含低 vol 條件）。

**FCX vs NVDA vs TSLA 過濾結構差異（三資產對比）**：
- TSLA-015：Part A 17→11 訊號（過濾 6 SLs）/ Part B 6→6 訊號（無過濾），高 vol 使 bear regime 與 bull regime SMA20/SMA60 差距大，1% 緩衝即可清晰分隔
- NVDA-012：Part A 17→16 訊號（僅過濾 1 個 2022-07-20 bear SL）/ Part B 8→7 訊號（過濾 1 marginal expiry，保留 1 transition winner，需 3% 緩衝），中 vol AI growth 期 SMA 變動較緩，transition zone 落於 0.97-0.99 區間
- **FCX-013**：Part A 23→17 訊號（過濾 4 TP + 2 SL，淨 -6）/ Part B 6→4 訊號（過濾 1 TP + 1 SL，淨 -2），**SLs 主要在 bull regime ratio>1**（4/6 SL 在 bull）使 buffered k<1 無法處理大部分 SLs；TPs 中 transition winners 集中 ratio 0.93-0.97（k=1.00 移除但無代價，因該區間僅 4 TPs 而 0.97-1.00 區間僅有 SLs）
- **共同模式精煉（FCX-013 確認後）**：規則的核心是「對齊 k 值與資產 winner-loser ratio 分布的分隔點」——TSLA/NVDA 為「過濾 bear-regime SLs 同時保留 transition winners」（k<1 buffered），FCX 為「過濾 transition-zone SLs 但 transition zone 無 winners」（k=1.00 嚴格亦成立）
