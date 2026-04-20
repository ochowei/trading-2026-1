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
  derived_from: [TQQQ-007,TQQQ-012,TQQQ-013,USO-006,USO-010~020,TSM-004,FCX-003,SIVR-006,SIVR-007,IWM-005,XBI-005,FXI-011,INDA-009]
  validated: 2026-04-20
  data_through: 2025-12-31
  confidence: high
-->

核心訊號已精確時，額外確認指標減少訊號數量而不提升品質。

**例外**：針對特定失敗模式的濾波器有效（如 GLD-007 ClosePos≥40% 移除仍在下跌的訊號、IWM-005 ClosePos 移除無反轉確認假訊號、XBI-005 ClosePos≥35%）。ClosePos 有效邊界約為日波動 ≤ 2.0%（GLD 1.1%、IWM 1.5-2%、XBI 2.0% 有效；SIVR 2-3%、FCX 2-4% 無效）。

**反例**：複合振盪器作為附加過濾器在「急跌+盤中反彈」結構資產上反向移除好訊號。**FXI-011 驗證 Connor's RSI（CRSI）在 FXI 上失敗**：CRSI ≤ 25 附加於 FXI-005 完整框架，訊號 26→18（-31%）但贏家 17→10（-41%）、輸家 9→8（-11%），系統性偏向移除贏家。根因：CRSI 三組件（RSI(3)、Streak_RSI(2)、%Rank(1d return,100d)）皆懲罰 1-2 日急跌+盤中反彈結構（RSI(3) 反彈快、streak 短、%Rank 不極端），而 FXI 的高品質訊號正屬此類型。

**反例 2（CCI 作為主訊號失敗）**：**INDA-009 驗證 Commodity Channel Index (CCI)** 作為均值回歸主訊號在 INDA 0.97% vol 上完全失敗（repo 首次 CCI 試驗）。三次迭代 min(A,B) -0.46/-0.03/-0.46 均遠低於 INDA-005 Att3 的 0.23。失敗結構與 lesson #20b RSI hook divergence 平行：INDA 2024-2025 Part B 為後峰持續下跌 regime，CCI(20) 長時間停留超賣區（<-100），每次迷你反彈觸發「CCI turn-up」後續跌停損。加嚴 CCI 至 -150（Att2）使 Part A 好訊號流失多於壞訊號（Sharpe 0.09→0.05），加 Pullback 下限（Att3）對 Part B 完全冗餘（下跌期訊號天然伴隨深 pullback）。**整合規則**：CCI turn-up 與 RSI Bullish Hook Divergence（URA-008、TLT-006）、Day-After Capitulation（URA-009/TLT-006）同屬「V-bounce ≠ genuine reversal」失敗家族。所有 oscillator hook 訊號（RSI/CCI/Stoch turn-up）在 post-peak slow-melt regime 中無區分力。

**規則**：只在確認能修復某個已知失敗模式時才加濾波器，不要隨意「加一個指標看看」。複合振盪器（CRSI 類）需先驗證資產的訊號結構與振盪器組件方向一致。**任何 oscillator hook 作為主訊號（CCI/RSI/Stoch turn-up）需先確認資產 Part A/B 兩段皆處於活躍 MR regime**——post-peak persistent decline regime 中 oscillator hook 必然失敗。

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
  validated: 2026-04-20
  data_through: 2025-12-31
  confidence: high
  note: URA-010 added 2026-04-20 (Williams Vix Fix Capitulation MR, repo first WVF trial). Three iterations all failed vs URA-004 min 0.39: Att1 (WVF(22)>BB_upper(20,2.0) + 10d PB [-8%,-25%], cd=10) Part A 23/65.2%/0.33 / Part B 11/45.5%/**-0.06** — 6/11 Part B SLs concentrated in continued declines (2024-02/06/10 + 2025-02/10/11), WVF spike captures "panic-mid-decline" not actual bottoms; Att2 (+ 2DD ≤ -3%) Part A 21/61.9%/0.25 / Part B identical (11/45.5%/-0.06) — 2DD non-binding (WVF spike inherently implies recent decline), Part A regressed; Att3 (+ deepen pullback floor to -10%, URA-004 standard) Part A **13/76.9%/0.68** (URA series in-sample best, +106% vs Att1) / Part B 8/50%/0.04 (positive but A/B cum diff 50pp). **Repo first WVF trial** — extends lesson #20b failure family beyond oscillator-hook (RSI/CCI/Stoch/CRSI) and price-action-bar (day-after reclaim) to **capitulation-depth indicators** (WVF). URA's policy-driven nature (核能政策/俄烏鈾供應) makes any entry-time filter (oscillator turn-up / single-bar reversal / capitulation depth metric) fail in Part B 2024-2025 V-shaped + post-rally crash regime ("event-driven asset rejects all entry-time confirmation filters"). Att3's Part A Sharpe 0.68 reveals "WVF + deep pullback" generates high-quality in-sample signals when active MR regime exists in both parts — cross-asset hypothesis: pattern may apply to SIVR/COPX where Part A/B both have active MR regime; will fail on FXI/TLT (policy-driven, parallel URA Part B). URA's 10th failed strategy type. URA-004 remains global optimum (10 experiments, 30+ attempts). INDA-009 added 2026-04-20 (CCI Oversold Reversal MR, repo first CCI trial). Three iterations all failed vs INDA-005 Att3 min 0.23: Att1 (CCI(20)≤-100 + turn-up + Close>Open, cd10) Part A 21 signals 61.9% WR Sharpe 0.09 / Part B 9 signals 44.4% WR Sharpe **-0.46** — Part B 2024-2025 INDA post-peak slow-melt decline (~58→~45) sees CCI persistently in oversold, every mini-rally triggers turn-up followed by continued decline (4/9 immediate SLs); Att2 (CCI≤-150 + ClosePos≥40%) Part A 9 signals 55.6% WR Sharpe 0.05 / Part B 3 signals 66.7% WR Sharpe -0.03 — tightening reduces signals but filters out more winners than losers (Part A Sharpe drops 0.09→0.05), sample too sparse (1.5/yr); Att3 (CCI≤-100 + ClosePos + Pullback≥2.5%) Part A 17 signals 58.8% WR Sharpe 0.06 / Part B 9 signals 44.4% WR Sharpe -0.46 — core insight: Part B signals all already carry ≥2.5% pullback (decline regime), making pullback floor filter zero-effect on Part B. **Repo first CCI trial** — extends lesson #20b failure family (V-bounce ≠ genuine reversal): CCI turn-up from oversold shares the oscillator-hook failure mode of RSI Bullish Hook Divergence on post-peak persistent decline regimes. **New cross-asset hypothesis**: CCI mean reversion requires both Part A/B in active MR regime (not post-peak slow-melt) — parallels URA-008/TLT-006 failures on policy-driven assets. INDA's 9th failed strategy type. INDA-005 Att3 remains global optimum (9 experiments, 28+ attempts). FXI-011 added 2026-04-20 (Connor's RSI Mean Reversion, first repo trial of CRSI = mean of RSI(3)+Streak_RSI(2)+PercentRank(1d return,100d)). Three iterations all failed vs FXI-005 min 0.38: Att1 (CRSI≤10 + PB 4-12% + ClosePos + ATR + cd10) Part A 6 signals 50% WR Sharpe 0.01 / Part B 2/2 100% WR Sharpe 4.14 — over-restrictive (23% signal retention, 50% WR vs 65.4% baseline); Att2 (CRSI≤20 + PB 4-12% + ClosePos, drop ATR/WR) Part A 16 signals 56.2% WR Sharpe 0.12 / Part B 4/4 100% WR Sharpe 5.36 — CRSI replaces WR but selects WORSE: removed 8 wins / 2 losses, dis-favoring 1-day-flush signals; Att3 (FXI-005 framework + CRSI≤25 as additional filter) Part A 18/55.6% WR Sharpe 0.17 / Part B 3/3 100% WR Sharpe 4.74 — 41% wins removed vs 11% losses, confirming CRSI systematically penalizes high-quality signals. **Core failure mode**: FXI's profitable MR signals are 1-2 day flushes with rapid intraday recovery, but CRSI's three components all penalize this profile — RSI(3) bounces back fast on 1-2 day flushes, streak length only -1/-2, %Rank not extreme on 1d -3% drops in policy-driven environments. CRSI truly fires on multi-day slow-melt declines, which FXI-005's ATR+WR+ClosePos already filter out. **Extends lesson #6 boundary**: CRSI as additional MR filter on policy-driven single-country EM ETFs systematically removes winners faster than losers, violating the "specific failure-mode filter" exception. Adds 9th failed strategy type to FXI (after BB Squeeze, RSI(5), BB Lower MR, RS momentum, Stoch, Failed Breakdown, Gap-Down Capitulation). **Repo first CRSI trial**: cross-asset hypothesis — CRSI may still work on low-vol broad ETFs (SPY/DIA/VOO ≤1.0% vol) where reversals involve 3-5 day gradual processes rather than 1-day flushes; does NOT apply to policy/event-driven single-country ETFs (FXI, URA, TLT class), high-vol crypto ETFs (IBIT class), high-vol stocks (TSLA/NVDA class). FXI-005 remains global optimum (11 experiments, 33+ attempts). IBIT-007 added 2026-04-19 (Keltner Channel Lower Band MR, three iterations all failed vs IBIT-006 Att2 min 0.40: Att1 Keltner 2.0×ATR + PB [-8%,-25%] + Close>Open + cd=10 → Part A 2/2 zero-var WR 100% cum +9.20% Sharpe 0.00 / Part B 3 signals 33% WR cum -3.97% Sharpe -0.31 — Keltner triggers fire DURING continued declines (2025-02-28 & 2025-11-18 both immediate SL) not at capitulation bottoms that gap-down filter captures; Att2 add WR(10)+deepen PB to -10% → identical signal set (Keltner trigger already implies extreme oversold/deep pullback, additional filters non-binding); Att3 Keltner 2.5×ATR + WR(5)≤-80 → Part A 0 signals (too restrictive), Part B 1/1 zero-variance Sharpe 0.00. **Core failure mode**: Keltner Lower Band (EMA-k×ATR) cannot replicate gap-down capitulation structural asymmetry (BTC overnight selling pressure completion → US-session bargain hunting); Keltner fires based on close-vs-EMA distance in ATR units, a LAGGING indicator of oversold depth rather than a LEADING indicator of capitulation completion on 24/7 underlying. **New cross-asset observation**: Keltner Lower Band MR (GLD-005 success on 1.12% vol) does NOT generalize to high-vol crypto ETF (IBIT 3.17% vol) — the volatility-adaptive threshold triggers during slow-melt declines rather than capitulation moments; suggests Keltner MR effective boundary at daily vol ≤ 1.5%. IBIT's seventh failed strategy type (after RSI(2), BB Squeeze breakout, trend momentum pullback, RSI(5) trend pullback, ATR vol adaptive/2-day decline, 20d lookback/short momentum, SL-8%). IBIT-006 Att2 remains global optimum (7 experiments, 21+ attempts). CIBR-010 added 2026-04-19 (NR7 Volatility Contraction + Pullback MR: pullback -4% + WR(10)≤-80 + NR7 + ClosePos≥40%, three iterations all failed vs CIBR-008 Att2 min 0.39: Att1 (NR7 alone) Part A 7/71.4% Sharpe 0.39 / Part B 3/33.3% Sharpe -0.44 — NR7 alone cannot distinguish genuine capitulation from consolidation during slow-melt declines on event-driven sector ETF; Att2 (add ATR>1.15) signals collapse to 1/2 Sharpe 0.00/-0.08 — **structural conflict**: NR7 requires today's TR to be min of 7 days, ATR(5) includes today, making the ratio mechanically depressed; Att3 (add 2-day decline ≤-2% instead of ATR) signals collapse to 1/1 zero-variance — **structural conflict 2**: 2-day drop ≥2% usually implies one of those days has a wide range, nearly mutually exclusive with NR7. First repo trial of NR7 / Narrowest Range 7 pattern — confirmed volatility contraction patterns (typically used in day-trader coiled-spring breakouts) do NOT transfer to multi-day mean-reversion frameworks on event-driven US sector ETFs (CIBR cybersecurity). CIBR's 6th failed strategy type. **New cross-asset hypothesis**: NR7/inside-day volatility contraction patterns structurally incompatible with ATR and 2DD quality filters, limiting their composability on pullback+WR frameworks. CIBR-009 added 2026-04-19 (Key Reversal Day price-action MR: Pullback + WR + Prev 收黑 + stop-run + reclaim + bullish bar + ClosePos + ATR, three iterations all failed vs CIBR-008 Att2 min 0.39: Att1 (WR≤-80, no ATR, with stop-run) Part A 8/50% WR Sharpe -0.08 / Part B 3/33.3% WR Sharpe -0.44, 2022 three consecutive SLs + 2025 two SLs all washout-then-continue; Att2 (+ATR>1.15) signals shrink to 2/2 with 2025-02-28 ATR 1.44 still 1-day SL; Att3 (remove stop-run, WR≤-85, ATR>1.10) signals crash to 1/1 both SL Sharpe 0.00. Extends XBI-012 failure pattern to CIBR: short-period single-day price-action reversal confirmation (stop-run + reclaim + bullish bar) fails on event-driven US sector ETFs (XBI biotech / CIBR cybersecurity). Integrated rule: **美國事件驅動板塊 ETF 拒斥所有短週期 price-action 反轉結構**, requires volatility-statistical indicators (BB 下軌+ATR) + absolute pullback cap filter (CIBR-008 / EWJ-003 hybrid pattern). 9 experiments, 27 attempts. XBI-012 added 2026-04-19 (Capitulation + Acceleration Reversal MR: Pullback(10) + ROC(3) + ClosePos + UpDay + WR, three iterations all failed vs XBI-005 min 0.36: Att1 (ROC -4%/ClosePos 50%/UpDay) 3/3 signals 0.16/0.16 too restrictive; Att2 (ROC -3%/ClosePos 40%/UpDay) Part A 0.27 +69% but Part B stuck at 0.16 because 2024-2025 XBI bull regime has sparse ROC(3) ≤ -3% events; Att3 (ROC -3%/ClosePos 35%/no UpDay) signals triple to 21/8 but quality collapses to 0.18/0.07, confirming UpDay filter is essential for quality. Ninth failed strategy type on XBI (after breakout, ROC alone, momentum pullback, pairs, ATR-adaptive, RSI(2), BB-lower hybrid, RSI hook divergence). Extends XBI structural finding: pullback(10)+WR+ClosePos 35% is the unique optimal primary entry trigger — any alternative trigger (ROC, BB, RSI hook) that shifts signal dates fails to generalize across Part A/B regimes. 12 experiments, 38+ attempts. XBI-011 added 2026-04-18 (RSI(14) Bullish Hook Divergence tested on XBI 2.0% vol 10-day pullback+WR+ClosePos framework, three iterations all failed vs XBI-005 min 0.36: Att1 (5/3.0/35 SIVR canonical) 3/2 signals all +3.50% TP zero-variance Sharpe 0.00; Att2 (5/3.0/40 loosen max_min) Part A 7 signals 2 stop-losses Sharpe 0.27; Att3 (5/2.0/35 loosen delta) identical to Att1 because max_min=35 is binding. Extends lesson #20b with 6th criterion: signal-day RSI(14) distribution must concentrate in deep oversold (≤35). XBI biotech pullback+WR signals land in RSI(14) 35-45 range due to FDA/clinical event-driven compressed 1-2 day declines that don't saturate RSI, while SIVR's persistent macro-driven declines do reach ≤35. Refines post-XBI cross-asset hypothesis: event-driven sector ETFs fail the hook pattern regardless of vol/framework/regime compliance; TSLA event-driven stocks likely also fail. 11 experiments. FXI-010 added 2026-04-18 (Gap-Down Capitulation + Intraday Reversal MR ported from IBIT-006 Att2, three iterations all failed to beat FXI-005 min 0.38: Att1 (gap≤-1.5% entry trigger + tight exit TP+3.5%/SL-3%) min -0.51 (22 signals 31.8% WR, FXI gap-downs often continue not capitulate); Att2 (gap≤-2.5% + close>midpoint + deep pullback + FXI-005 wide exit) min 0.00 (signals crashed to 5/1); Att3 (gap as 5d regime filter + FXI-005 entry) Part A 0.34 / Part B 0.00 zero-variance with 2 signals, A/B signal ratio 4.4:1. Double-extends lessons #52 and #20a: (a) policy-driven EM rejects gap-down capitulation structure as both entry trigger AND regime filter — adds to the BB Squeeze/BB lower MR/Stoch cross/failed breakdown reclaim rejection list; (b) Gap-down capitulation pattern requires not just "overnight continuous price discovery" (which FXI has via HK market) but ALSO "selling pressure uncorrelated with policy/event continuity" — FXI has the former but Chinese policy news persists through US session, invalidating the buy-the-dip structure. URA-009 added 2026-04-18 (Day-After Capitulation + strong reversal bar confirmation tested on URA, three iterations all failed: Att1 (WR≤-85+2DD≤-4%+Close>PrevClose+Close>Open) min -0.25 / Att2 (Close>PrevHigh reclaim) min 0.24 with perfect A/B balance but ~1/yr / Att3 (loosen to URA-004 thresholds + keep strong reversal) min -0.11 as WR collapsed to 43%, all vs URA-004 0.39. Extends lesson 20b failure mode: day-after price-action bar confirmation (even "reclaim prior high") on policy/event-driven URA still fails by "V-bounce ≠ genuine reversal" principle. Att2's A/B perfect balance (0pp cum diff, 60%/60% WR) confirms day-after framework is symmetry-preserving but the inherent ceiling of URA capitulation reversal trading appears to be URA-004 itself. URA-008 added 2026-04-18 (RSI(14) Bullish Hook Divergence tested on URA 10-day pullback framework with active Part A/B MR regime, three iterations all failed: Att1 URA-004 base + hook min 0.00 / Att2 remove 2DD min 0.00 / Att3 SIVR-015 structure with WR(10) min -0.32 Part B WR 33.3%, all vs URA-004 0.39. URA formally meets all four criteria (2.34% vol, 10d PB, active Part A/B MR regime in URA-004, validated pullback+WR framework) but hook filter reduces signals 24/16→6/3 (retention 25% vs SIVR 44%), Part B 2025-11-05 signal stops out next day confirming V-bounce ≠ genuine reversal on policy-driven uranium. Refines lesson 20b to five conditions: adds "asset must have RSI-turn=genuine-reversal structure" requirement, excluding event/policy-driven assets (URA nuclear, FXI policy, TLT rates) even when volatility/framework/regime formally met. FCX-009 added 2026-04-18 (RSI(14) Bullish Hook Divergence tested on FCX 10-day pullback framework, three iterations all failed: Att1 delta=3 min -0.33 / Att2 delta=5 min -0.06 / Att3 delta=5+pullback-11% min 0.30, all vs FCX-001 0.43. FCX formally meets pattern 20b's lookback ≤10 constraint, but Part B signals dwindled 5→3→2 through iterations as 2024-2025 post-peak copper decline eliminated active MR regime. Part A Sharpe surged 0.51→0.76→0.85 confirming hook filter raises signal quality, but Part B cum diff 39-51pp consistently exceeded 30% target. Extends lesson #20b boundary: requires Part A/B both in active mean-reversion regime, not post-peak secular decline. COPX-009 added 2026-04-18 (RSI(14) Bullish Hook Divergence tested on COPX 20-day pullback framework, three iterations all failed: Att1 ATR+hook5 min -0.50 / Att2 ATR+hook10 min 0.00 / Att3 no-ATR+hook10 min 0.15, all vs COPX-007 0.45. Extends lesson #20b boundary: bullish hook divergence requires pullback lookback ≤10 days — 20-day framework causes prolonged declines where RSI hooks up-down multiple times, making hook filter capture local noise rather than true capitulation end. Part A WR crashes from 76.2%→33.3% (Att1) / 57.1% (Att2) / 64.3% (Att3). SIVR-015 added 2026-04-17 (RSI(14) Bullish Hook Divergence + SIVR-005 entry: pullback 7-15% + WR(10)<=-80 + RSI(14) self-risen from 5d-min by ≥3 points where 5d-min ≤ 35, TP+3.5%/SL-3.5%/15d). Att1 new global best min(A,B) 0.22→0.48 (+118%), Part B Sharpe 0.26→1.41 (+442%). First repo validation of classical bullish divergence pattern. Att2 (lookback 7/delta 2) too loose, Part A regressed 0.28; Att3 (RSI(7)) noisy, both parts negative. RSI(14) is the correct period for SIVR divergence. Pattern may generalize to other mean-reverting assets — cross-asset validation pending. FXI-009 added 2026-04-17 (Failed Breakdown Reversal / Turtle Soup, 3 iterations all failed: Att1 breakdown_lookback=10 min 0.00 / Att2 lookback=5 + ClosePos min -0.11 / Att3 lookback=10 + 1% depth Part A signals dried up. Extends lesson #52 to Turtle Soup structure: policy-driven single-country EM ETFs reject all short-horizon reversal structures (BB Squeeze, BB Lower, Stoch crossover, failed breakdown reclaim). FXI-005 remains global optimum at min(A,B) 0.38. TQQQ-016 added 2026-04-17 (Gap-Down Capitulation MR ported from IBIT-006, 3 iterations all failed: Att1 gap-3% min -0.07 / Att2 gap-2% min -0.07 / Att3 +volume min -0.07, all vs TQQQ-010 0.36). Validates lesson #20a boundary: pattern does NOT extend to leveraged tech ETFs on traditional (non-24/7) underlying. Att3 Part A Sharpe 0.49 (+36% vs TQQQ-010) but Part B unchanged at -0.07 due to 2025-04-07 Trump tariff gap-down continuing to decline. 16 experiments. EEM-012 added 2026-04-17 (BB Lower + Pullback Cap Hybrid MR: BB(20,2.0) + 10d PB cap -7% + WR(10)<=-85 + ClosePos>=40% + ATR(5)/ATR(20)>1.1 + TP+3%/SL-3%/20d/cd10, Att3 min(A,B) 0.34 +89% vs EEM-005 0.18, first validation of hybrid pattern on broad EM ETF category, extends lesson #52 scope beyond single-country EM. Att2 ATR>1.15 reverse-failed: crisis-day ATR spike means tighter ATR preserves losers not winners — WR is the key quality axis for EEM hybrid, 12 experiments). IBIT-006 added 2026-04-17 (Gap-Down Capitulation MR: Gap<=-1.5% + Close>Open + 10d PB [-12%,-25%] + WR(10)<=-80 + TP+4.5%/SL-4%/15d/cd10, Att2 min(A,B) 0.40 +167% vs IBIT-001 0.15, first structural entry improvement leveraging BTC 24/7 overnight gap + US session buying pattern; Att3 ablation confirmed gap-down filter is prerequisite for tight SL -4%, 6 experiments). FXI-008 updated 2026-04-17 (Stochastic Oscillator MR tested on FXI, three iterations Att1 %K>%D cross 0.16 / Att2 %K level 0.34 / Att3 WR+Stoch dual osc 0.37 all failed vs FXI-005 min 0.38, confirmed Stoch Oscillator adds no value over WR(10) for policy-driven EM single-country ETF). CIBR-008 updated 2026-04-16 (BB lower band + pullback cap -12% hybrid, min(A,B) 0.27→0.39, +44%, 8 experiments). EWJ-003 updated 2026-04-16 (BB lower band + pullback cap hybrid, Part A Sharpe 0.55→0.60, 3 experiments). VGK-007 updated 2026-04-16 (BB lower band + pullback cap -7% hybrid, min(A,B) 0.45→0.53, +18%, 7 experiments, resolves VGK-004 A/B imbalance 37.5%→8.2%). EWZ-006 updated 2026-04-16 (BB lower band 1.5σ + pullback cap -10% hybrid, min(A,B) 0.34→0.69, +103%, 6 experiments, first commodity-driven EM single-country ETF to validate hybrid pattern). XBI-010 updated 2026-04-17 (BB lower band + pullback cap hybrid tested on biotech ETF 2.0% vol, three iterations all failed to beat XBI-005 min 0.36, confirmed hybrid pattern effective upper boundary at daily vol ≤1.75%, 10 experiments). INDA-008 updated 2026-04-17 (BB lower band + pullback cap hybrid tested on India ETF 0.97% vol, three iterations all failed to beat INDA-005 min 0.23, confirmed hybrid pattern effective lower boundary at daily vol ≥1.12%, 8 experiments). FXI-007 updated 2026-04-17 (RS momentum FXI vs EEM tested, three iterations min -6.63~0.16 all failed vs FXI-005 min 0.38, confirmed single-country EM RS momentum pattern failure extends to China, 7 experiments). EWJ-004 updated 2026-04-17 (RS momentum EWJ vs EFA/SPY tested on DM single-country ETF, three iterations min -0.24~0.15 all failed vs EWJ-003 min 0.60, extended single-country RS momentum failure pattern from EM to DM, 4 experiments). EWT-008 updated 2026-04-17 (BB lower band 2.0σ + pullback cap -8% hybrid tested on Taiwan ETF 1.41% vol semiconductor-driven EM single-country, Att1 min(A,B) 0.57† vs EWT-007 RS momentum 0.42, +36% Part A Sharpe, confirmed hybrid pattern effective in [1.12%, 1.75%] vol range extends to EM semiconductor-driven single-country ETFs, 8 experiments). †EWJ/EWT min(A,B) uses Part A Sharpe as binding constraint — Part B Sharpe formally 0.00 due to zero variance (EWJ 6/6, EWT 3/3 trades returned identical +3.50%)
-->

| 資產 | 最佳實驗 | 策略類型 | min(A,B) Sharpe | 全域最優確認 |
|------|----------|----------|-----------------|-------------|
| TQQQ | TQQQ-010 | 極端恐慌買入 | 0.36 | 16 次實驗 ✓ |
| GLD | GLD-012 Att3 | 20日回調+WR（無追蹤停損）| 0.48 | 12 次實驗 ✓ |
| SIVR | SIVR-015 Att1 | 回檔+WR+RSI bullish hook divergence | 0.48 | 17 次實驗 ✓ |
| FCX | FCX-001/FCX-004 | 三重極端超賣/BB Squeeze | 0.43/0.41 | 9 次實驗 ✓ |
| USO | USO-013 | 緊密回檔+RSI(2)+2日急跌 | 0.26 | 22 次實驗 ✓ |
| SPY | SPY-005 | RSI(2) 寬出場 | 0.53 | 8 次實驗 ✓ |
| DIA | DIA-005 | RSI(2) 延長持倉 | 0.47 | 11 次實驗 ✓ |
| VOO | VOO-003 | RSI(2) 寬獲利目標 | 0.53 | 3 次實驗 ✓ |
| SOXL | SOXL-010 Att3 | 板塊 RS 動量回調 | 0.70 | 11 次實驗 ✓ |
| TSM | TSM-008 | RS 出場優化 | 0.79 | 9 次實驗 ✓ |
| IWM | IWM-011 | 波動率自適應 RSI(2) | 0.52 | 11 次實驗 ✓ |
| XBI | XBI-005 | 回檔範圍+WR+反轉K線 | 0.36 | 12 次實驗 ✓ |
| COPX | COPX-007 | 波動率自適應均值回歸 | 0.45 | 9 次實驗 ✓ |
| URA | URA-004 | 回檔範圍+RSI(2)+2日急跌 | 0.39 | 10 次實驗 ✓ |
| NVDA | NVDA-004 | BB 擠壓突破（優化）| 0.47 | 8 次實驗 ✓ |
| IBIT | IBIT-006 Att2 | Gap-Down 資本化+日內反轉 MR | 0.40 | 7 次實驗 ✓ |
| TSLA | TSLA-009 Att2 | BB 擠壓突破（30th pct）| 0.40 | 12 次實驗 ✓ |
| TLT | TLT-002 | 回檔+WR+反轉K線+60日跌幅 | -0.20/0.24 | 無純技術面解法（13 次實驗）|
| EEM | EEM-012 Att3 | BB 下軌+回檔上限+WR+ClosePos+ATR（混合進場）| 0.34 | 12 次實驗 ✓ |
| EWJ | EWJ-003 Att3 | BB 下軌+回檔上限+WR+ATR（混合進場）| 0.60† | 4 次實驗 ✓ |
| EWT | EWT-008 Att1 | BB 下軌+回檔上限+WR+ClosePos+ATR（混合進場）| 0.57† | 8 次實驗 ✓ |
| VGK | VGK-007 Att1 | BB 下軌+回檔上限+WR+ClosePos+ATR（混合進場）| 0.53 | 7 次實驗 ✓ |
| XLU | XLU-011 | 波動率自適應均值回歸 | 0.67 | 11 次實驗 ✓ |
| INDA | INDA-005 Att3 | 出場優化均值回歸（回檔+WR+ClosePos+ATR）| 0.23 | 9 次實驗 ✓ |
| FXI | FXI-005 Att3 | 出場優化均值回歸（TP5.5%/SL5%/20d）| 0.38 | 11 次實驗 ✓ |
| EWZ | EWZ-006 Att3 | BB 下軌+回檔上限+WR+ClosePos+ATR（混合進場）| 0.69 | 6 次實驗 ✓ |
| CIBR | CIBR-008 Att2 | BB 下軌+回檔上限-12%+WR+ClosePos+ATR | 0.39 | 10 次實驗 ✓ |

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
26. **趨勢回檔策略** — 在低波動防禦型 ETF、高波動個股上均市場狀態依賴過強。**短期動量（5日漲幅>10%）在 IBIT 上 Part A 1.00/Part B -0.55**，2024 牛市 87.5% WR vs 2025 震盪 25% WR（IBIT-005 Att2 驗證）。**低波動歐洲寬基 ETF（VGK）同樣失敗**：SMA(20)>SMA(50) 趨勢對齊+淺回檔 min 0.02、寬出場 min -0.21、ROC 動量 0 OOS 訊號（VGK-006 三次嘗試驗證）
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
52. **政策驅動 EM ETF 拒斥所有短週期反轉結構（BB 下軌 MR / BB Squeeze 突破 / Stoch 交叉 / Failed Breakdown Reclaim / Gap-Down Capitulation）** — BB(20,2.0) 太鬆捕捉慢磨下跌（FXI WR41.7%），BB(20,2.5)+多重過濾過嚴（5+1訊號）。BB 帶寬在持續熊市中不斷外擴，下軌失去選擇性。2d decline≤-3% 獨立進場亦僅 min 0.13，不如 PB+WR 框架。**Failed Breakdown Reversal（Turtle Soup）在 FXI 亦失敗（FXI-009 驗證）**：三次迭代（10d/5d lookback、1% 深度門檻、ClosePos、bullish bar）最佳 min 0.00（Att1 Part A 8 訊號 Sharpe 0.18 / Part B 1 訊號停損 0.00），所有 SL 交易（2021-11、2022-09、2023-02、2025-04）在 reclaim 後 2-10 天再度深跌停損，證明政策/事件驅動 EM 的 breakdown reclaim 結構無持續反轉能量。**Gap-Down Capitulation + Intraday Reversal 在 FXI 亦失敗（FXI-010 驗證）**：三次迭代均未勝過 FXI-005 的 0.38。Att1（gap≤-1.5% entry trigger + 緊出場）Part A 0.33 Part B -0.51（22 訊號 WR 31.8%）；Att2（gap≤-2.5% + Close>midpoint + 深 pullback + 寬出場）min 0.00（訊號 5/1 過稀疏）；Att3（Gap 作為 5d regime filter + FXI-005 entry）Part A 0.34 接近基線但 Part B 2 訊號零方差 Sharpe 0.00，A/B 訊號比 4.4:1 遠超 1.5:1 目標。失敗根因：FXI 雖有 HK 盤後連續價格發現，但中國政策/經濟消息在美股盤中持續發酵，gap-down 後常續跌而非反轉（與 IBIT BTC 24/7 的「拋壓完成 + 美股撿便宜」結構本質不同）。**例外**：EWJ-003 驗證 BB 下軌+回檔上限混合進場在日本市場有效（Sharpe 0.60），因日本市場無中國式政策衝擊（FXI-006 驗證）。**CIBR-008 Att2 進一步驗證**：在美國板塊 ETF（CIBR 1.53% vol）上 BB(20,2.0) + 回檔上限 -12%（7.8σ）+ WR + ClosePos + ATR 混合進場 min(A,B) 0.39（+44% vs CIBR-007 純 BB 下軌的 0.27）。**VGK-007 Att1 三度驗證**：歐洲寬基 ETF（VGK 1.12% vol）BB(20,2.0) + 回檔上限 -7%（6σ）+ 三重品質過濾 min(A,B) 0.53（+18% vs VGK-004 Att1 的 0.45），且解決 VGK-004 A/B 累積差 37.5% 問題（降至 8.2%）。**EWZ-006 Att3 四度驗證並擴展邊界**：商品驅動 EM 單國 ETF（EWZ 1.75% vol）BB(20,1.5) + 回檔上限 -10%（5.7σ）+ 三重品質過濾 min(A,B) 0.69（+103% vs EWZ-002 Att3 的 0.34），且 Part B 樣本從 4 增至 6（+50%），證明高波動需放寬 BB 至 1.5σ 維持訊號頻率。**EWT-008 Att1 五度驗證並擴展驅動類別**：半導體驅動 EM 單國 ETF（EWT 1.41% vol）BB(20,2.0) + 回檔上限 -8%（5.7σ）+ 三重品質過濾 min(A,B) 0.57†（+36% vs EWT-007 RS 動量 0.42），†Part B 3/3 全達 +3.50% 零方差 Part A 綁定約束（同 EWJ-003 模式）。A/B 年化訊號比 1.2:1 優秀，A/B 累計差 36.1%（同 EWZ 量級）。**EEM-012 Att3 六度驗證並擴展至 broad EM 指數類別**：broad EM ETF（EEM 1.17% vol）BB(20,2.0) + 回檔上限 -7%（6σ）+ WR ≤ -85（收緊過濾 EM 危機淺觸） + ClosePos + ATR 三重品質過濾 min(A,B) 0.34（+89% vs EEM-005 BB Squeeze 的 0.18）。A/B 累計差僅 3.6%（極優），訊號頻率 1.2/yr vs 2.0/yr（Part B 牛市活躍）。**關鍵發現**：ATR 門檻對 EEM 在 BB Lower 框架內**方向反轉**——Att2 收緊 ATR>1.15 使 min(A,B) 崩至 -0.60（危機日 ATR 飆高，高門檻保留停損移除贏家），WR 才是 EEM 混合模式的關鍵品質軸。混合進場模式適用：低中波動（1.12%~1.75%）資產+三重品質過濾+回檔上限 5.7-8σ（BB std 隨波動度降低 0.5-1.0σ，VGK/CIBR/EWT/EEM 用 2.0σ，EWJ 1.5σ no cap→1.5σ+cap 7%，EWZ 1.5σ+cap 10%），**驅動類別已涵蓋寬基（VGK/EWJ）、板塊（CIBR）、商品驅動 EM（EWZ）、半導體驅動 EM（EWT）、broad EM 指數（EEM）**；不適用政策驅動單一 EM 國家 ETF（FXI 驗證）。**XBI-010 驗證有效邊界上限為日波動 1.75%**：生技板塊 ETF（XBI 2.0% vol）三次迭代（BB 1.5σ 過鬆 min 0.07、BB 2.0σ 過嚴 min -0.55、OR 進場 cap -12% min 0.16）均未勝過 XBI-005（min 0.36）。失敗根因：(a) XBI 無法使用 ATR 過濾（XBI-009 驗證日波動達 ATR 有效邊界上限），失去混合模式的關鍵波動率飆升確認；(b) 生技板塊 FDA/臨床事件驅動使訊號呈現為絕對深度回檔（8-15%）而非統計異常；(c) XBI-005 的固定 pullback 8-20% 在 2.0% 日波動下已是最優結構。**INDA-008 驗證有效邊界下限為日波動 1.12%**：印度 ETF（INDA 0.97% vol）三次迭代（BB 2.0σ 過嚴 min 0.20、BB 1.5σ 過鬆 min -0.04、BB 1.8σ 中間 min -0.25）均未勝過 INDA-005 Att3（min 0.23）。失敗根因：(a) INDA 0.97% vol 下 BB 帶寬太窄（2.0σ 僅 1.94% 偏離均值，多數有效回檔不觸及；1.5σ 僅 1.46%，納入淺技術超賣假訊號）；(b) 固定 3-7% 回檔（3.1-7.2σ）框架在 0.97% 波動下已精準鎖定有效均值回歸深度，BB 自適應機制在極低波動下不比固定門檻優越；(c) INDA 慢磨特性（受盧比/外資流驅動）使 BB 下軌訊號與真正反轉機會關聯性低

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
- **板塊/商品 ETF（XBI/COPX/URA/SIVR）**：pullback+WR 深回檔框架最佳，RSI(2) 無效。**XBI-010 驗證 BB 下軌+回檔上限混合進場模式不適用 XBI 2.0% 日波動**（三次迭代 min 0.07/-0.55/0.16 均未勝過 XBI-005 的 0.36），確認混合模式有效邊界上限為日波動 1.75%（EWZ 為上限）。**INDA-008 驗證混合進場模式不適用 INDA 0.97% 日波動**（三次迭代 min 0.20/-0.04/-0.25 均未勝過 INDA-005 的 0.23），確認混合模式有效邊界下限為日波動 1.12%（VGK 為下限）。混合進場模式有效 vol 區間 = [1.12%, 1.75%]
- **個股（TSLA/NVDA/FCX）**：BB 擠壓突破或極端超賣（取決於波動度）
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

## 19. 2日急跌過濾
<!-- freshness:
  derived_from: [FCX-008,USO-013,EWT-004,VGK-005]
  validated: 2026-04-16
  data_through: 2025-12-31
  confidence: medium
-->

2日急跌過濾在基礎訊號頻率 ≥ 5/年的資產上有效（USO、COPX），但在訊號已稀少的資產上（FCX ~3.6/年）會過度移除好訊號。

**例外**：EWT-004 在 3.2 訊號/年仍有效（min(A,B) 0.13→0.15，+15%），但配合非對稱出場才能發揮，且改善幅度小於高頻資產。

**低波動資產限制**：VGK（1.12% vol）上 2日急跌 ≤ -1.0% 太溫和（~0.45σ/天），pullback+WR 訊號天然包含急跌成分，過濾器因冷卻期交互作用反移除好訊號（Part A 0.42→0.36，-14.3%，VGK-005 Att1 驗證）。

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

## 20b. RSI Bullish Hook Divergence 對高波動均值回歸有效（SIVR 驗證，COPX/FCX/URA/XBI/USO/WVF 失敗擴展邊界）
<!-- freshness:
  derived_from: [SIVR-015,COPX-009,FCX-009,URA-008,URA-009,URA-010,TLT-006,XBI-011,USO-022]
  validated: 2026-04-20
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

**反例（URA-010，capitulation-depth 指標 — 跨指標家族擴展）**：三次迭代全部失敗，URA-004 min(A,B) 0.39 維持為全域最優。本實驗以 **Williams Vix Fix（WVF）= (max(Close,N)−Low)/max(Close,N)×100** 取代 hook，WVF 結構性與 oscillator turn-up 完全不同（純 capitulation 深度極值，非反彈確認），仍在 URA Part B 失效：
- Att1（WVF(22)>BB_upper(20,2.0) + 10d 回檔 [-8%,-25%] + cd=10）：Part A 23/65.2%/0.33 / Part B 11/45.5%/-0.06——Part B 6/11 SL 集中於持續下跌段（2024-02/06/10、2025-02/10/11），WVF spike 後續跌
- Att2（+ 2DD ≤ -3%）：Part A 退至 21/61.9%/0.25 / Part B 完全相同 11/45.5%/-0.06——2DD 對 WVF 結構性非綁定
- Att3（+ 加深回檔下限至 -10%，URA-004 標準）：Part A **13/76.9%/0.68**（URA in-sample 最高）/ Part B 8/50%/0.04（A/B 累計差 50pp）
- **失敗根因**：URA-010 為 lesson #20b 失敗家族首次擴展至**capitulation-depth 指標**（前述失敗皆為 oscillator turn-up 或 single/dual-bar reversal）。整合規則：URA 為政策驅動資產，**任何 entry-time 過濾器**（無論 oscillator turn-up、single/dual-bar reversal、或 capitulation-depth metric）均無法在 Part B 2024-2025 V-shaped + post-rally crash regime 區分真假底部
- **正面發現**：Att3 Part A Sharpe 0.68 顯示「WVF + 深回檔」在 in-sample（URA Part A 含 2020 COVID + 2022 鈾礦熊市 + 2023 復甦）為高品質訊號生成器。跨資產假設：可能適用於 SIVR/COPX 等 Part A/B 兩段皆活躍 MR regime 的 2-3% vol 資產；不適用於 FXI/TLT 等政策驅動資產（類比 URA Part B 失敗模式）。WVF 為 repo 首次試驗指標

**跨資產泛化假設（待進一步驗證）**：可能適用於其他**日波動 2-3% + 回檔回看窗口 ≤10 日 + 兩段 Part A/B 皆活躍 MR regime + RSI 轉折=真實反轉結構 + 訊號日 RSI(14) 分布集中於 ≤ 35 深度 oversold**且已驗證 pullback+WR 框架的資產。**低波動資產**（GLD、SPY、EWJ、VGK）divergence 訊號可能過於稀少；**政策/事件驅動資產**（FXI、TLT、URA）可能因 RSI 特徵受宏觀事件影響而失效；**長回檔窗口資產**（COPX 20 日）已確認失效；**post-peak 持續下跌資產**（FCX 2024-2025 銅價）因 Part B regime 失效而失敗；**核能政策驅動資產**（URA）雖符合前四條件但 hook filter 訊號保留率僅 25%（vs SIVR 44%）且 Part B V-bounce 假訊號過多而失敗（URA-008 驗證）；**事件驅動板塊 ETF**（XBI 生技）因 RSI 僅淺層 oversold 而失效（XBI-011 驗證）；**商品 event-driven ETF**（USO 油價 OPEC/地緣政治）亦失效（USO-022 驗證）；**事件驅動個股**（TSLA）可能同樣失效，需謹慎評估訊號日 RSI 分布再測試。整合觀察：有效資產需滿足 (a) 波動率 2-3%、(b) 持續性下跌使 RSI 飽和至 ≤35、(c) 非事件驅動（macro-factor 驅動優於 event/policy 驅動）。**lesson #20b 失敗模式跨指標家族延伸（URA-010 新增）**：URA-010 將失敗家族首次從 oscillator hook（RSI/CCI/Stoch/CRSI）+ price-action bar（day-after reclaim）擴展至 **capitulation-depth 指標（WVF）**。在政策驅動資產（URA）上，任何 entry-time 過濾器類型（無論 oscillator turn-up、single/dual-bar reversal、或 capitulation depth metric）皆失效，揭示「entry-time confirmation 在事件/政策驅動 Part B regime 結構性無區分力」的更深層原則。WVF + 深回檔模式在 URA Part A in-sample（含 2020 COVID + 2022 熊市 + 2023 復甦）Sharpe 0.68，跨資產延伸性待 SIVR/COPX 驗證。

**與 SIVR-007 Att1「RSI(14) 動能回復」的關鍵差異**：SIVR-007 僅要求 RSI > 5日最低值（單側門檻，無 delta 閾值、無 oversold 前提），SIVR-015 雙重條件更嚴格鎖定 classical divergence 結構。

---

## 20. 跨資產相關性配對策略的結構性風險
<!-- freshness:
  derived_from: [XLU-005,COPX-006,SIVR-009,TSM-009,FCX-006,DIA-009,EEM-006]
  validated: 2026-04-10
  data_through: 2025-12-31
  confidence: high
-->

跨資產相關性可能隨宏觀環境改變而失效（regime change）。Part A 正 + Part B 負 Sharpe 是相關性崩潰的典型特徵。個股 vs 板塊 ETF RS 策略僅在個股有持續性結構優勢（如 TSM 先進製程護城河）時有效，商品生產者（FCX）的超額表現由短期事件驅動，無持續性。廣基 ETF RS（如 EEM vs SPY）受宏觀/政治事件（關稅、貿易戰）驅動，三次嘗試 Part B 均為負值。
