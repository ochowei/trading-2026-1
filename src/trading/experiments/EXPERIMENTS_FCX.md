<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-04-27
  data_through: 2025-12-31
  note: FCX-013 added 2026-04-27 (Multi-Week Regime-Aware BB Squeeze Breakout, **repo 第 3 次 lesson #22 試驗、首次商品/礦業單股驗證 buffered multi-week SMA trend regime**, cross-asset extension from TSLA-015 / NVDA-012). Three iterations, **Att3 SUCCESS**: Att1 (k=0.99 TSLA cross-asset port, 1% buffer) Part A 18/66.7%/Sharpe **0.44** cum +63.30% / Part B 5/80%/Sharpe **0.82** cum +26.34% / min(A,B) **0.44** (+7% vs FCX-004 0.41) — Part B 大幅改善 (0.41→0.82) 為主要貢獻，Part A 略退化 (0.51→0.44) 因 4 TP 過濾損失大於 2 SL 過濾受益. Att2 (k=0.97 NVDA cross-asset port, 3% buffer) Part A 19/68.4%/0.48 / Part B 6/66.7%/0.41 完全相同 baseline / min **0.41** — k=0.97 過寬，Part B 2025-08-26 SL (ratio 0.972 > 0.97) 保留，**證實 NVDA k 值不可直接移植 FCX**：NVDA 該區間有 transition winners 而 FCX 該區間僅有 SLs. **Att3 ★ SUCCESS (k=1.00 嚴格無緩衝)** Part A 17/70.6%/Sharpe **0.55** cum +75.86% / Part B 4/75%/Sharpe **0.64** cum +16.98% / min(A,B) **0.55** (+34% vs 0.41 baseline，+25% vs Att1 0.44). **跨資產發現（與 TSLA/NVDA 反向）**：FCX 上 k=1.00 嚴格優於 k<1 buffered，反轉 lesson #22 「k<1 緩衝」原則。失敗根因（TSLA k=1.00 / NVDA k=0.99 失敗）為 borderline transition winners 在 ratio 0.97-1.00 區間被誤殺；**FCX 該區間無 winners**（僅 1.013 略高於 1.00 自然保留），故 k=1.00 無代價。**lesson #22 跨資產精煉**：k 取決於資產 winners 在 transition zone (0.93-1.00) 分布——TSLA winners 集中 0.99-1.00 (k=0.99) / NVDA 跨 0.97-1.00 (k=0.97) / **FCX 集中 0.93-0.97 + bull-regime 主導 (k=1.00 嚴格)**. A/B 平衡 acceptance：訊號比 1.7:1 (gap 41.2% < 50%) ✓，cum gap 44.0% (FCX 商品超級週期結構性邊界) ✗，**從 baseline 89% / 3.83:1 大幅改善**. FCX-013 Att3 為 BB Squeeze 框架新最佳，與 FCX-001 MR 框架並列雙最優。13 experiments 39+ attempts. FCX-012 added 2026-04-23 (Donchian Lower Washout + Intraday Reversal MR, **repo first "Donchian Lower touch + intraday reversal" combo as MR primary entry**). Three iterations all failed vs FCX-004 min 0.41: Att1 (baseline: Close within 2.5% of Donchian_Low(20) + today or yesterday Low = 20d low + ClosePos>=40% + ATR(5)/ATR(20)>=1.10 + 60d DD in [-30%,-10%] + TP+9%/SL-11%/20d/cd15) Part A 8/50%/**-0.06** cum -8.16% / Part B 6/50%/**0.02** cum -0.93% / min **-0.06** — two Part A -11% SLs (2019-08-05 trade war, 2023-04-25 drift) are continuation-decline traps; Part B dominated by small expiries (2024-01/11/12) showing washout signal lacks trigger momentum in sideway regimes; Att2 (+ require today Low > yesterday Low = Day-After Capitulation) Part A 1/0%/Sharpe 0.00 zero-var cum -12.36% / Part B 2/100% Sharpe 1.07 cum +9.33% / min **-0.60** (single-trade approximation) — over-filters to 3 total signals, statistical insignificance; **validates lesson #20b Day-After Capitulation failure family extending to FCX 3% vol single commodity stock** (after URA 2.34% policy-driven / TLT 1% rate-driven, third data point); Att3 (revert Att2, add 2DD cap >= -7%, CIBR-012 direction) Part A 7/42.9% Sharpe **-0.20** cum -15.74% (**WORSE than Att1**) / Part B 6/50% Sharpe 0.02 unchanged / min **-0.20** — 2DD cap removed 1 TP winner (not SL) dropping WR 50→42.9%; Part B all signals' 2DD > -7% (structurally unbinding). **Core failure**: FCX winners' 2DD distribution spans -3%~-8% overlapping with losers (same pattern as FCX-011 Att2 found), no unidirectional selectivity opposite to CIBR 1.53% vol success. **Repo first Donchian Lower Washout + intraday reversal trial** — extends lesson #52 failed-breakdown-reversal family to "Donchian Lower binary price trigger" category: single-day Donchian Low touch + intraday reversal insufficient to distinguish "tail-of-washout" from "mid-acceleration" in multi-stage declining assets (parallels FXI-009 Failed Breakdown Reversal 3 iteration failure). FCX's 12th failed strategy type. FCX-001 remains global optimum; FCX-004 remains execution-model optimum (min 0.41). FCX-011 added 2026-04-22 (Post-Capitulation Vol-Transition MR, **repo first BB-lower + pullback-cap hybrid mode trial on high-vol single stock (FCX ~3% vol)** — cross-asset extension from VGK-008 / INDA-010 / EEM-014 / CIBR-012). Three iterations all failed vs FCX-004 min 0.41: Att1 (baseline hybrid: BB(20,2) + PB cap -15% + WR<=-80 + ClosePos>=40% + ATR>1.15 + TP+6%/SL-7%/20d/cd10) Part A 3 signals WR 66.7% cum +4.34% Sharpe **0.26** / Part B 5 signals WR 40.0% cum -7.86% Sharpe **-0.23** / min -0.23 — Part B 2024-07-19 + 2024-12-13 both 1-3d fast SLs indicate signal-day filter cannot distinguish accelerating-crashes from genuine capitulation; Att2 (+ 2DD cap >= -5%, CIBR-012 direction) Part A 2/50% Sharpe -0.09 / Part B 2/50% Sharpe -0.09 / min -0.09 — cap removes 2021-06-16 TP winner (deep 2DD) alongside 2024-07-19 SL; deep 2DD covers both winners and losers in FCX, no unidirectional selectivity; Att3 (+ 2DD floor <= -5%, VGK/INDA/EEM direction) Part A 1/100% zero-var / Part B 4/50% Sharpe ~0 / min 0.00 — floor filters 2/3 Part A signals (density 0.2/yr), keeps both winners and expiry losses in Part B. **Core failure**: FCX winners' 2DD distribution spans -3%~-8%, overlapping with losers (distinct from CIBR SLs concentrated deep 2DD or VGK SLs concentrated shallow 2DD). **Repo first BB-lower hybrid mode on high-vol single stock** — **extends XBI-010's 1.75% vol upper boundary to include single-stock category** (previously established only on ETFs). Integrated rule: BB-lower + pullback-cap hybrid mode applies only to low-mid vol broad/sector/single-country ETFs (1.12%~1.75%); fails on XBI (2.0% ETF), FXI (policy EM), GLD/TLT (commodity/rate), and now **FCX (~3% single stock)**. FCX's 9th failed strategy type (after pullback+WR, momentum pullback, RS, Donchian, trend pullback, RSI divergence, Gap-Down, BB-lower-hybrid). FCX-001 remains global optimum (11 experiments, 33+ attempts); FCX-004 remains execution-model optimum (min 0.41). FCX-010 added 2026-04-21 (Gap-Down Capitulation + Intraday Reversal MR, **repo first single-stock Gap-Down trial**, cross-asset test from IBIT-006 Att2). Three iterations all failed vs FCX-001 min 0.43: Att1 (Gap<=-2.0% + Close>Open + 10d PB [-6%,-18%] + WR<=-80 + TP+5%/SL-4%/15d) Part A n=9 WR 55.6% cum +7.77% Sharpe 0.21 / Part B n=2 WR 100% zero-variance Sharpe 0.00 — 4 Part A SLs concentrated in 2019 trade war + 2023 SVB first-wave shocks (gap-down continues not capitulates); Att2 (+ ClosePos>=50% strong intraday reversal filter) Part A n=8 WR 62.5% cum +12.42% Sharpe 0.36 / Part B unchanged n=2 zero-variance — removes 1 weak-reversal SL (2023-02-24) but 3 policy-shock SLs remain; Att3 (tighten Gap<=-2.5% + pullback floor -8%) Part A n=5 WR 80% cum +16.52% Sharpe **0.87** (repo-first single-stock gap-down high Part A Sharpe) / Part B n=1 zero-variance Sharpe 0.00, A/B signal annualized ratio 2.0:1 and A/B cum gap 69.7% violate balance goals. **Repo first Gap-Down Capitulation trial on single stock** — extends lesson #20a failure family: Gap-Down pattern requires NOT JUST 24/7 overnight price discovery but ALSO selling-pressure exhaustion uncorrelated with daytime policy/commodity continuity. FCX (copper-linked high-vol stock) has LME/SHFE/COMEX near-24h futures coverage but copper price shocks (trade policy, USD, global demand) persist into US session, paralleling FXI-010's Chinese policy continuity failure. Failure family extended: TQQQ-016 (leveraged index ETF, QQQ non-24/7) + FXI-010 (policy-driven EM ETF) + FCX-010 (commodity-linked single stock) — all fail; only IBIT (pure BTC 24/7 ETF) validates. Cross-asset hypothesis (pending validation): Gap-Down MR may apply ONLY to pure-crypto ETFs (BTC/ETH spot), not to any US equity with macroeconomic/commodity exposure.
-->
## AI Agent 快速索引

**當前最佳（均值回歸）：** FCX-001（三重條件極端超賣均值回歸：60日回撤≤-18% + RSI<28 + SMA50乖離≤-8%）
**當前最佳（突破策略）：** ★ **FCX-013 Att3**（Multi-Week Regime-Aware BB Squeeze Breakout：FCX-004 框架 + **SMA(20) ≥ 1.00 × SMA(60)** 嚴格 multi-week trend regime gate，TP+8%/SL-7%/20d/cd10）— Part A Sharpe **0.55**, Part B Sharpe **0.64**, min(A,B) **0.55**（+34% vs FCX-004 0.41）。**Repo 第 3 次 lesson #22 試驗、首次商品/礦業單股驗證**，跨資產反向發現：FCX k=1.00 嚴格優於 TSLA k=0.99 / NVDA k=0.97 buffered。**前任最佳（突破）：** FCX-004（同進場無 regime gate，min 0.41）

**滾動窗口分析摘要（2026-03-29）：**
- **FCX-001：** 12/12 窗口正累計（最低 +13.05%，最高 +41.52%），勝率 50-83%，近期虧損收窄（-12%→-3%）但差點成功比例升高，策略穩健但反彈速度趨緩
- **FCX-002：** 9/12 窗口正累計（3 個負累計窗口最差 -15.51%），勝率 46-75%，漸變性通過（ΔWR 9.7pp）但底線保護弱於 FCX-001

**FCX-004 實驗摘要（2026-04-02，3 次嘗試）：**
- **Att1**（pct25, cd15, TP+8%/SL-7%）：Part A Sharpe 0.44 / Part B 0.00*（4訊號全+8%，std=0 導致 Sharpe 退化）。A/B 訊號比 5.25:1 嚴重不平衡
- **Att2**（pct30, cd10, TP+8%/SL-7%）：**Part A Sharpe 0.51 / Part B 0.41**，A/B 年化訊號比 1.53:1（最佳平衡）。Part A 累計 +106.31%，Part B +17.31%
- **Att3**（pct30, cd10, TP+10%/SL-8%）：Part A Sharpe 0.29 / Part B 0.32。TP+10% 使多筆 +8% 達標交易變為到期或停損，確認 TP+8% 為 FCX 突破甜蜜點

**已證明無效（禁止重複嘗試）：**
- FCX-002 回檔+WR+反轉K線：訊號過多(6.6/年)但品質低，Part A 累計+34.88% 遠低於 FCX-001 的+90.41%，2022 熊市連續 4 次停損。滾動分析 3/12 窗口負累計（最差-15.51%），對比 FCX-001 的 12/12 全正
- FCX-003 Att1 收窄SL -10%：FCX 高波動需要 -12% 呼吸空間，-10% 將可恢復的深跌轉為停損（2019-08-09 +10%→-10%，2024-07-24 -0.59%→-10%），Part A Sharpe 0.37 / Part B Sharpe 0.40（均劣於 FCX-001）
- FCX-003 Att2 延長持倉至 30天：Part A 微幅改善（+90.68%），但 2024-07-24 從 -0.59%(25天) 惡化至 -8.00%(30天)，Part B Sharpe 從 0.74 降至 0.49
- FCX-003 Att3 加入 ClosePos≥40% 過濾：改變了訊號日期而非單純移除壞訊號（2019-05-01→2019-05-21 等），Part A Sharpe 改善（0.54）但訊號減至 11 筆 MDD 惡化至 -19.54%，Part B Sharpe 崩潰至 0.28
- FCX-004 Att3 TP+10% 突破：多筆 +8% 贏利交易變到期/停損，Part A Sharpe 0.29（vs Att2 0.51），確認 FCX 突破 TP+8% 硬上限

**已掃描的參數空間：**
- 均值回歸進場：從嚴格（-20%/RSI<25/-10%）到適度放寬（-18%/RSI<28/-8%）取得最佳平衡
- 均值回歸出場：寬出場（+10%/-12%/25天持倉）能適配 FCX 高波動特性
- FCX-002：回檔+WR+反轉K線（10日回檔≤-9%, WR(10)≤-80, ClosePos≥40%, TP+8%/SL-10%/20天）— 不如 FCX-001
- FCX-003 出場調整：SL -10%（太緊）、持倉 30天（延長反而傷害 Part B）
- FCX-003 進場過濾：ClosePos≥40%（改變訊號日期導致不可預測結果）
- BB 突破擠壓百分位：25th（A/B 不平衡 5.25:1）vs 30th（A/B 1.53:1，最佳）
- BB 突破冷卻期：15天（Part B 訊號過少）vs 10天（改善 A/B 平衡）
- BB 突破出場：TP+8%/SL-7% 最佳；TP+10%/SL-8% 使贏利交易翻轉
- 動量回檔：Close>SMA50+ROC>5%+2日跌幅（Part B 7連續停損）；SMA50>SMA200+ROC>8%（Part B 僅 3 訊號全敗）
- RSI(2) 短期均值回歸：RSI(2)<10+2日跌幅≥4%（Part A WR 38.2%，熊市觸發過頻）

**FCX-005 實驗摘要（2026-04-02，3 次嘗試，全部失敗）：**
- **Att1**（動量回檔：Close>SMA50 + ROC(20)>5% + 2日跌幅≤-3%）：Part A Sharpe 0.09 / Part B -0.84。Part B 7連續停損，趨勢反轉殺死回檔買家
- **Att2**（強趨勢過濾：SMA50>SMA200 + ROC(20)>8% + 2日跌幅≤-3%）：Part A Sharpe -0.12 / Part B -1.46。黃金交叉過嚴，Part B 僅 3 訊號全敗
- **Att3**（RSI(2) 短期均值回歸：RSI(2)<10 + 2日跌幅≥4%）：Part A Sharpe -0.22 / Part B 0.24。Part A WR 38.2%，熊市觸發過多假訊號

**已證明無效（禁止重複嘗試）：**（更新）
原有項目加上：
- FCX-005 動量回檔策略：FCX 趨勢反轉太劇烈，「上升趨勢中的拉回」常演變為趨勢反轉（Part B 7連續停損）
- FCX-005 RSI(2) 短期均值回歸：FCX 日波動 2-4%，RSI(2)<10 在熊市觸發過頻（6.8/年），WR 僅 38.2%，遠低於盈虧比所需的 ~47%

**FCX-006 實驗摘要（2026-04-05，3 次嘗試，全部失敗）：**
- **Att1**（RS>=5%, pullback 3-7%, TP+8%/SL-7%/25d）：Part A Sharpe 0.20 / Part B -0.15（5訊號）。A/B 年化訊號比 6:1 嚴重不平衡，Part B WR 僅 40%
- **Att2**（RS>=8%, pullback 3-8%）：Part A Sharpe -0.10 / Part B 無訊號。門檻過高殺死所有 OOS 訊號
- **Att3**（RS>=3%, pullback 3-8%）：Part A Sharpe 0.18 / Part B -0.19（9訊號）。WR 33.3%，MDD -20.94%，品質更差

**已證明無效（禁止重複嘗試）：**（更新）
原有項目加上：
- FCX-006 相對強度策略（FCX vs COPX RS）：FCX-COPX RS 在 2020 銅礦復甦期集中爆發但 2024-2025 兩者高度同步，RS 訊號在 OOS 期間無預測力。與 TSM-SMH RS（Sharpe 0.79/0.83）不同，FCX-COPX 缺乏持續性的個股超額表現驅動因素

**FCX-007 實驗摘要（2026-04-07，3 次嘗試，全部失敗）：**
- **Att1**（Donchian 20, SMA50, cd10）：Part A Sharpe -0.06 / Part B 0.23。42訊號品質極差（WR 45.2%），A/B 比 3.5:1
- **Att2**（Donchian 50, SMA50, cd15）：Part A Sharpe 0.23 / Part B 0.06。延長回看改善 Part A 但 Part B 崩潰，A/B 比 3.4:1
- **Att3**（Donchian 30 + BB Squeeze 30th pct, SMA50, cd10）：Part A Sharpe 0.02 / Part B 0.64。BB Squeeze 大幅改善 Part B 但 A/B 訊號比 6:1 嚴重不平衡

**已證明無效（禁止重複嘗試）：**（更新）
原有項目加上：
- FCX-007 Donchian 通道突破：Donchian 基於固定回看期高點，不如 BB 上軌的統計自適應門檻。短回看（20日）訊號過多、長回看（50日）Part B 崩潰、加 BB Squeeze 造成 A/B 6:1 不平衡。商品週期導致不同時期突破模式差異巨大

**FCX-008 實驗摘要（2026-04-10，3 次嘗試）：**
- **Att1**（趨勢跟蹤：SMA50>SMA200 + 上升斜率 + 回測SMA50 + 反彈確認，TP+8%/SL-7%/20d）：Part A Sharpe -0.00 / Part B -0.63。確認 lesson #71 FCX 趨勢反轉太劇烈
- **Att2**（FCX-001 + ATR(5)/ATR(20)>1.05 波動率過濾）：Part A Sharpe 0.25 / Part B 0.82。ATR 改善 Part B 但大幅退化 Part A（移除好訊號多於壞訊號）
- **Att3**（FCX-001 + 2日跌幅≤-5% 急跌過濾）：Part A Sharpe 0.31 / Part B **1.26**。A/B 累計完美平衡（+40.57%/+40.28%），但 min(A,B) 0.31 低於 FCX-001 的 0.43

**FCX-009 實驗摘要（2026-04-18，3 次嘗試，全部未超越 FCX-001）：**
跨資產驗證 pattern 20b（SIVR-015 Att1 的 RSI(14) bullish hook divergence）。進場建立於 FCX-002 pullback+WR 框架（移除 ClosePos，lesson #34），加入 pullback 上限 -18%（~6σ 崩盤隔離）與 RSI(14) hook 過濾。
- **Att1**（pullback [-9%,-18%] + WR + hook delta=3 / max_min=35，TP+8%/SL-10%/20d）：Part A Sharpe 0.51（WR 72.7%, 11 訊號）/ Part B -0.33（WR 40.0%, 5 訊號）。SIVR-015 Att1 參數直接移植失敗：delta=3 放行 2024-07-29 深跌中的局部反彈假訊號（-10.13% 4日停損）
- **Att2**（加嚴 hook delta 3→5，其餘不變）：Part A Sharpe **0.76**（WR 77.8%, 9 訊號）/ Part B -0.06（WR 33.3%, 3 訊號）。成功濾除 2024-07 停損並轉為 2024-08 +8% 達標，Part A 跳升 +49%，但 Part B 仍受 2024-11/12 雙筆 20 天到期虧損拖累（FCX 2024 後半缺乏均值回歸動能）
- **Att3**（加深 pullback -9%→-11%，delta=5）：Part A Sharpe **0.85**（WR 85.7%, 7 訊號）/ Part B 0.30（WR 50.0%, 2 訊號）。深 pullback 門檻濾除 Part B 2024-11 淺層假訊號，兩段均轉正但 min(A,B) 0.30 仍低於 FCX-001 的 0.43。A/B 累計差 39.24pp、訊號差 71.4% 均超出目標（30%/50%），Part B 僅 2 訊號樣本不足

**FCX-010 實驗摘要（2026-04-21，3 次嘗試，全部未超越 FCX-001，**repo 首次 single-stock Gap-Down 試驗**）：**
跨資產驗證 pattern 20a（IBIT-006 Att2 的 Gap-Down Capitulation + Intraday Reversal MR）。假設：FCX 作為銅礦股，其隔夜缺口反映銅期貨（LME/SHFE/COMEX）近 24 小時連續定價，結構類似 IBIT 的 BTC 24/7 隔夜拋壓 → 美股撿便宜模式。
- **Att1**（Baseline: Gap<=-2.0% + Close>Open + 10d PB [-6%,-18%] + WR<=-80，TP+5%/SL-4%/15d/cd10）：Part A n=9 WR 55.6% cum +7.77% Sharpe **0.21** / Part B n=2 WR 100% zero-variance Sharpe 0.00，min(A,B) 0.00。4 筆 Part A SL 全為 1-3 日快速停損，集中於 2019-05-07（貿易戰升溫第一天）、2019-08-06（人民幣匯率衝擊）、2023-02-24、2023-03-14（SVB 銀行危機），均為「新事件衝擊第一波」或「次波衝擊」訊號，gap-down 後續跌而非反轉
- **Att2**（+ ClosePos>=50% 強日內反轉過濾）：Part A n=8 WR 62.5% cum +12.42% Sharpe **0.36**（+71% vs Att1）/ Part B n=2 WR 100% zero-variance Sharpe 0.00（訊號集不變），min(A,B) 0.00。ClosePos 過濾器移除 1 筆 Part A SL（2023-02-24 的弱反轉）但 3 筆政策衝擊 SL（2019 兩筆 + 2023-03-14 SVB）保留，Part B 2024-2025 bull regime gap-down + 強反轉稀少
- **Att3**（加嚴 Gap<=-2.5% + pullback floor -8%）：Part A n=5 WR 80% cum +16.52% Sharpe **0.87**（+142% vs Att2，repo 首見 single-stock gap-down 之 Part A 高 Sharpe）/ Part B n=1 WR 100% zero-variance Sharpe 0.00，min(A,B) 0.00。加嚴成功提升 Part A 品質但 Part B 崩至 1 訊號，A/B 訊號年化比 2.0:1、累計差 69.7% 均嚴重違反平衡目標

**已證明無效（禁止重複嘗試）：**（更新）
原有項目加上：
- FCX-008 趨勢跟蹤：SMA 黃金交叉 + 回檔至 SMA(50) 在高波動週期股完全失敗（Part B WR 25%），趨勢反轉太劇烈
- FCX-008 ATR 波動率自適應：ATR > 1.05 在 FCX 日波動 2-4% 下跨期不穩定（Part A 0.25 vs 基線 0.43），極端超賣條件本身就需要高波動才能觸發，ATR 對這些訊號的額外過濾力有限
- FCX-008 2日急跌過濾：改善 Part B（0.74→1.26）但大幅減少 Part A 訊號（18→13），3 個被移除的勝利交易拖累 Part A Sharpe
- FCX-009 RSI Bullish Hook Divergence：雖 Part A 大幅改善（0.85），但 Part B 2024-2025 銅價 post-peak 回檔期缺乏實質均值回歸動能，3 次迭代 Part B 訊號從 5→3→2 漸趨稀薄。確認 pattern 20b（SIVR-015）跨資產邊界：需 Part B 存在活躍的均值回歸 regime；FCX 2024 後半進入長期下行不適用
- **FCX-010 Gap-Down Capitulation + Intraday Reversal MR（repo 首次 single-stock Gap-Down 試驗，3 次迭代全部失敗）**：跨資產移植 IBIT-006 Att2 模式。Att1（Gap<=-2.0% baseline）Part A Sharpe 0.21 / Part B zero-var 0.00 / min 0.00，4 筆 SL 集中政策衝擊日；Att2（+ ClosePos>=50%）Part A 0.36 / Part B 同 / min 0.00，移除弱反轉但保留政策衝擊 SL；Att3（Gap<=-2.5% + PB -8%）Part A Sharpe **0.87** / Part B n=1 零方差 / min 0.00，Part A 大幅改善但 Part B 崩潰。**核心失敗根因**：(1) 銅價衝擊（貿易政策、美元、全球需求預期）往往貫穿美股盤中持續發酵，與 FXI 中國政策持續性平行，gap-down 後常續跌而非反轉；(2) FCX 2024-2025 post-peak 銅週期缺乏 capitulation 事件，Part B 訊號結構性稀少；(3) 加嚴過濾器在 Part A 有效但在 Part B 導致樣本崩潰。**延伸 pattern 20a 失敗清單**：TQQQ-016（槓桿指數 ETF）+ FXI-010（政策驅動 EM ETF）+ FCX-010（商品連動個股）均失敗，目前僅 IBIT（純 BTC 24/7 ETF）驗證成功——結構性前提嚴格，不可跨類別泛化。跨資產假設（待驗證）：Gap-Down MR 可能僅適用「underlying 連續交易 + selling pressure 自然耗盡」的純加密類資產，不適用任何與宏觀政策/商品供需週期連動的美股

**FCX-011 實驗摘要（2026-04-22，3 次嘗試，全部未超越 FCX-004，**repo 首次 BB-lower hybrid mode 於高波動單一個股試驗**）：**
跨資產驗證 VGK-008 / INDA-010 / EEM-014 / CIBR-012 所建立的「BB 下軌 + 回檔上限 + WR + ClosePos + ATR」混合進場模式。XBI-010 已驗證該模式上限為日波動 1.75%（XBI 2.0% 失敗）；本實驗測試 **單一個股類別**（FCX ~3% vol）是否突破此上限。
- **Att1**（基線混合進場：BB(20,2) + PB cap -15% + WR<=-80 + ClosePos>=40% + ATR>1.15，TP+6%/SL-7%/20d/cd10）：Part A 3 訊號 WR 66.7% cum +4.34% Sharpe **0.26** / Part B 5 訊號 WR 40.0% cum -7.86% Sharpe **-0.23** / min(A,B) **-0.23**。Part B 2 筆 SL (2024-07-19 9-day, 2024-12-13 3-day) 均快速觸發，signal-day ATR/ClosePos 過濾無法分辨加速崩盤與真 capitulation
- **Att2**（+ 2DD cap >= -5%，CIBR-012 方向排除加速崩盤）：Part A 2/50% Sharpe **-0.09** / Part B 2/50% Sharpe **-0.09** / min **-0.09**。cap 過濾器同時移除 2021-06-16 深 2DD 贏家（+6% TP）與 2024-07-19 SL——FCX 贏家 2DD 分布橫跨淺深，cap 方向無選擇力
- **Att3**（+ 2DD floor <= -5%，VGK/INDA/EEM 方向排除淺漂移）：Part A 1 訊號 WR 100% 零方差 Sharpe **0.00** / Part B 4 訊號 WR 50% Sharpe ~0 / min **0.00**。floor 濾掉 Part A 2/3 訊號（密度崩至 0.2/yr），訊號過稀疏；Part B 2024-11-12 淺 2DD 到期虧損仍保留

**FCX-012 實驗摘要（2026-04-23，3 次嘗試，全部未超越 FCX-004，**repo 首次「Donchian Lower Washout + 日內反轉」組合作為 MR 主進場試驗**）：**
測試「Donchian 20 日低點觸及」作為 binary、非參數化的 washout 觸發器，
搭配日內反轉（ClosePos >= 40%）、波動率放大（ATR(5)/ATR(20) >= 1.10）
與 60 日回撤範圍約束 [-30%, -10%]，探索是否能打破 FCX-001 的 Part A/B
累計報酬 72% gap。
- **Att1**（基線：Close 距 20 日低點 <= 2.5% + 今日或昨日 Low = 20d 新低 + ClosePos >= 40% + ATR >= 1.10 + 60d DD ∈ [-30%,-10%]，TP+9%/SL-11%/20d/cd15）：Part A 8 訊號 WR 50% cum -8.16% Sharpe **-0.06** / Part B 6 訊號 WR 50% cum -0.93% Sharpe **0.02** / min **-0.06**。兩筆 Part A -11% SL（2019-08-05 貿易戰、2023-04-25 drift）為 continuation-decline 陷阱；Part B 三筆小幅到期（2024-01/11/12）顯示 washout 訊號在 sideway 環境缺乏動能
- **Att2**（+ require today Low > yesterday Low = Day-After Capitulation）：Part A 1 訊號 Sharpe 0.00 零方差 cum -12.36% / Part B 2 訊號 Sharpe 1.07 cum +9.33% / min **-0.60**（以 Part A 單筆 -12.36% 報酬近似）。過度過濾——「washout-day + 今日不再探底」在 FCX 高波動個股上極稀疏，共 3 訊號無統計意義。**驗證 lesson #20b Day-After Capitulation 失敗家族於 FCX 3% vol 單一商品個股**（繼 URA 2.34% / TLT 1% 後第三個資料點）
- **Att3**（回退 Att2，改加 2DD cap >= -7%，CIBR-012 方向）：Part A 7 訊號 WR 42.9% cum -15.74% Sharpe **-0.20**（**比 Att1 更差**）/ Part B 6 訊號不變（2DD 全 > -7%，cap 結構性非綁定）Sharpe 0.02 / min **-0.20**。2DD cap 僅移除 1 筆 TP（未移除 SL），WR 從 50% 降至 42.9%——FCX winners 2DD 分布橫跨 -3%~-8%，與 losers 重疊，無單向選擇力

**已證明無效（禁止重複嘗試）：**（更新）
原有項目加上：
- **FCX-011 BB 下軌 + 回檔上限混合進場模式（repo 首次高波動單一個股試驗，3 次迭代全部失敗）**：跨資產移植 VGK-008/INDA-010/EEM-014/CIBR-012 成功模式。Att1 基線 min -0.23，Part B 兩筆快速 SL 顯示混合模式對 FCX 高波動缺乏辨識力；Att2 2DD cap 方向崩至 min -0.09（贏家過濾過嚴）；Att3 2DD floor 方向 min 0.00（訊號過稀疏）。**核心失敗根因**：(1) BB 下軌在 FCX 高波動下觸及頻率高但選擇性低，統計自適應門檻無法捕捉 FCX 單一個股的事件驅動結構；(2) FCX 贏家訊號的 2DD 分布橫跨 -3%~-8%，與輸家重疊，雙向（cap/floor）皆無選擇力——與 CIBR SLs 集中深 2DD、VGK SLs 集中淺 2DD 之結構皆不同；(3) FCX ~3% vol 遠超 XBI-010 已驗證的 1.75% vol 上限。**延伸跨資產規則**：BB-lower hybrid mode 上限**從「1.75% vol ETF」擴展為「1.75% vol（涵蓋 ETF 與單一個股兩類別）」**，高波動單一個股類別正式納入失敗清單（繼 XBI 2.0% ETF、FXI 政策驅動 EM、GLD/TLT 商品/利率 ETF 後）
- **FCX-012 Donchian Lower Washout + 日內反轉 MR（repo 首次 Donchian Lower touch + 日內反轉作為 MR 主進場試驗，3 次迭代全部失敗）**：Att1 基線 min -0.06，兩筆 -11% SL 為 continuation-decline；Att2 Day-After Capitulation 過度過濾至 3 總訊號 min -0.60；Att3 2DD cap -7% 意外移除贏家多於輸家使 min 崩至 -0.20。**核心失敗根因**：(1) Donchian Lower 觸及為「反轉候選」非「反轉確認」——FCX ~3% vol commodity panic 常以多日連續 Donchian 新低為特徵（2019-08 trade war、2021-06 銅價頂部後、2022 升息、2024-07 銅價暴跌均有 3-5 連續新低日），單日觸及 + 日內反轉不足以區分「尾段 washout」vs「中段 acceleration」，與 FXI-009 Failed Breakdown Reversal 三次迭代失敗（lesson #52）同源；(2) Day-After Capitulation 對 FCX 同樣失效（延伸 lesson #20b 至 FCX 3% vol 個股，第三個資料點）；(3) 2DD cap 在 FCX 無選擇力（呼應 FCX-011 Att2 相同發現）。**擴展 lesson #52 至「Donchian Lower binary price trigger」類別**：binary 價格觸發器在「多段下跌」結構資產上結構性缺乏區分力——政策驅動 EM ETF（FXI）與高波動單一商品個股（FCX）共享同一失敗機制

**尚未嘗試的方向（可探索，但預期邊際效益極低）：**
- 加入銅價/HG 指標確認（減少 2022 熊市等大環境的誤判，但 cross-asset lesson #6 警告額外確認指標通常無效）
- 引入追蹤停損（Trailing Stop）捕捉更大型的反彈（但 cross-asset lesson #2 警告日波動 2-4% 禁用 trailing stop）
- ~~BB 下軌 + 回檔上限混合進場模式~~ → FCX-011 三次迭代全部失敗（repo 首次高波動單一個股試驗，確認 XBI-010 1.75% vol 上限延伸至單一個股類別）
- ~~Donchian Lower Washout + 日內反轉 MR~~ → FCX-012 三次迭代全部失敗（repo 首次此組合作為 MR 主進場，擴展 lesson #52 至 binary 價格觸發器類別）
- FCX-001/004 已確認為全域最優（12 次實驗、45+ 次嘗試，含均值回歸、突破（BB Squeeze + Donchian）、動量回檔、RSI(2)、相對強度、趨勢跟蹤、波動率自適應、RSI bullish hook divergence、Gap-Down Capitulation、BB-lower hybrid mode、**Donchian Lower Washout** 十一大策略類型）

**關鍵資產特性：**
- 高 Beta、週期性強，與銅價高度相關
- 日均波動約 2-4%（介於 GLD 與 TQQQ 之間）
- 流動性不如 ETF，需假設較大滑價（0.15%）
- 極端恐慌時跌幅可達 30-50%，適合深谷抄底
- 突破策略（BB Squeeze）在 FCX 有效（日波動 2-4% 在 TSLA/NVDA 驗證的有效範圍內）
<!-- AI_CONTEXT_END -->

# FCX 實驗總覽 (FCX Experiments Overview)

## 標的特性 (Asset Characteristics)

- **FCX (Freeport-McMoRan)**：全球最大公開上市銅礦公司
- 高 Beta、週期性強，與銅價高度相關
- 日均波動約 2-4%，介於 GLD 與 TQQQ 之間
- 極端恐慌時跌幅可達 30-50%（如 2020 COVID、2022 衰退恐慌）

## 實驗列表 (Experiment List)

| ID      | 資料夾                        | 策略摘要                       | 狀態  |
|---------|-------------------------------|-------------------------------|-------|
| FCX-001 | `fcx_001_extreme_oversold`    | 三重條件極端超賣均值回歸        | 已完成 |
| FCX-002 | `fcx_002_pullback_wr`         | 回檔+Williams%R+反轉K線均值回歸 | 已完成 |
| FCX-003 | `fcx_003_optimized_exit`      | 三重超賣+反轉K線過濾（3次嘗試均失敗） | 已完成 |
| FCX-004 | `fcx_004_bb_squeeze_breakout` | BB Squeeze Breakout 突破策略（3次嘗試，Att2 最佳） | 已完成 |
| FCX-005 | `fcx_005_momentum_pullback`   | 動量回檔 / RSI(2) 短期均值回歸（3次嘗試均失敗） | 已完成 |
| FCX-006 | `fcx_006_relative_strength`   | FCX-COPX 相對強度（3次嘗試均失敗） | 已完成 |
| FCX-007 | `fcx_007_donchian_breakout`   | Donchian 通道突破（3次嘗試均失敗） | 已完成 |
| FCX-008 | `fcx_008_trend_pullback`      | 趨勢跟蹤→ATR自適應→2日急跌（3次嘗試，Att3 Part B 最佳但 min<FCX-001） | 已完成 |
| FCX-009 | `fcx_009_rsi_divergence_mr`   | RSI Bullish Hook Divergence + Pullback+WR MR（3次嘗試均未超越 FCX-001） | 已完成 |
| FCX-010 | `fcx_010_gap_reversal_mr`     | Gap-Down Capitulation + 日內反轉 MR（3次嘗試均未超越 FCX-001，repo 首次 single-stock Gap-Down 試驗） | 已完成 |
| FCX-011 | `fcx_011_vol_transition_mr`   | Post-Capitulation Vol-Transition MR / BB-lower hybrid（3次嘗試均未超越 FCX-004，repo 首次 BB-lower hybrid 於高波動單一個股試驗） | 已完成 |
| FCX-012 | `fcx_012_donchian_low_washout` | Donchian Lower Washout + 日內反轉 MR（3次嘗試均未超越 FCX-004，repo 首次此組合作為 MR 主進場） | 已完成 |
| FCX-013 | `fcx_013_regime_breakout`     | Multi-Week Regime-Aware BB Squeeze Breakout（FCX-004 + buffered SMA(20)≥k×SMA(60)，**Att3 SUCCESS k=1.00 嚴格 min(A,B) 0.55 +34%**，repo 第 3 次 lesson #22 試驗、首次商品/礦業單股、跨資產反向發現） | ✅ 突破策略當前最佳 |

---

## FCX-001: Extreme Oversold Mean Reversion

**目標**：以嚴格多重條件篩選 FCX 極端超賣點，追求高勝率、低頻訊號（每年 3-5 次）。

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
| 獲利目標 | +10% | 銅礦股反彈力道強，放大獲利空間 |
| 停損 | -12% | 寬停損讓極端超賣有更多恢復時間 |
| 持倉天數 | 25 天 | 充分等待回彈 |

### 成交模型

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價） |
| 獲利出場 | `limit_order Day`（當日限價單） |
| 停損出場 | `stop_market GTC`（持倉期間停損市價） |
| 到期出場 | `next_open_market`（隔日開盤市價） |
| 滑價 | 0.15%（個股滑價較 ETF 大） |
| 悲觀認定 | 是（同 bar 停損與獲利同時觸發 → 假設停損先成交） |

### 設計理念

- **三重過濾**：回撤 + RSI + SMA 乖離，三者同時極端才觸發，確保只在真正恐慌時進場
- **寬出場**：+10%/-12% 出場搭配 25 天持倉，適配 FCX 高波動特性，給交易更多喘息空間
- **0.15% 滑價**：個股流動性不如 ETF，使用較保守滑價假設
- **參數調校歷程**：經過多輪測試，從嚴格進場(-20%/RSI<25/-10%)到適度放寬(-18%/RSI<28/-8%)，搭配寬出場(+10%/-12%/25天)取得最佳平衡

### 回測結果

| 指標 | Part A (In-Sample) | Part B (Out-of-Sample) | Part C (Live) |
|------|-------------------|----------------------|---------------|
| 區間 | 2019-01-01 ~ 2023-12-31 | 2024-01-01 ~ 2025-12-31 | 2026-01-01 ~ today |
| 訊號數 | 18 (3.6/年) | 5 (2.5/年) | 1 |
| 勝率 | **72.2%** | 60.0% | 100.0% |
| 平均報酬 | +4.10% | +4.83% | +4.88% |
| 累計報酬 | **+90.41%** | +25.34% | +4.88% |
| 平均持倉 | 9.6 天 | 14.6 天 | 2.0 天 |
| 最大回撤 | -15.83% | -11.36% | -0.68% |
| 最大連續虧損 | 1 | 2 | 0 |

**亮點**：
- Part A 72.2% 勝率，年均 3.6 次訊號，累計 +90.41%
- Part A 最大連續虧損僅 1 次，風險控制優秀
- Part B 平均每筆報酬 +4.83%，正期望值穩定
- 3 筆虧損到期出場中有 2 筆虧損 < 7%，寬停損有效避免被洗出

---

## FCX-002: Pullback + Williams %R + Reversal Candle

**目標**：改編跨資產已驗證的回檔 + Williams %R 模式（GLD-007: 100% OOS 勝率、SIVR-003: 63.6% OOS 勝率），測試不同進場哲學能否在 FCX 取得更好績效。

### 進場條件（全部滿足）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 10 日高點回檔 | ≤ -9% | 依 FCX 2-4% 日波動縮放（GLD:-3%, SIVR:-7%） |
| 2 | Williams %R(10) | ≤ -80 | 跨資產通用超賣指標 |
| 3 | 收盤位置 | ≥ 40% | 反轉K線確認（GLD-007 驗證可過濾 34% 弱訊號） |
| 冷卻 | 訊號間隔 | ≥ 10 交易日 | 避免重複訊號 |

### 出場參數

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 | +8% | 銅礦股反彈力道強 |
| 停損 | -10% | 寬停損適配高波動，較 FCX-001(-12%) 略收窄 |
| 持倉天數 | 20 天 | 介於 GLD(20天) 與 FCX-001(25天) 之間 |

### 成交模型

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價） |
| 獲利出場 | `limit_order Day`（當日限價單） |
| 停損出場 | `stop_market GTC`（持倉期間停損市價） |
| 到期出場 | `next_open_market`（隔日開盤市價） |
| 滑價 | 0.15%（個股滑價較 ETF 大） |
| 悲觀認定 | 是（同 bar 停損與獲利同時觸發 → 假設停損先成交） |

### 設計理念

- **跨資產驗證**：回檔 + Williams %R 在 GLD-007 與 SIVR-003 已驗證為有效的商品類資產進場邏輯
- **反轉K線過濾**：GLD-007 加入此條件後過濾 34% 弱訊號，勝率從 77.4% 提升至 100% (OOS)
- **不使用追蹤停損**：跨資產教訓顯示日均波動 > 1.5% 的資產追蹤停損會過早觸發
- **參數縮放**：回檔閾值 -9% 為 GLD(-3%) 與 SIVR(-7%) 依波動率等比放大

### 回測結果

| 指標 | Part A (In-Sample) | Part B (Out-of-Sample) | Part C (Live) |
|------|-------------------|----------------------|---------------|
| 區間 | 2019-01-01 ~ 2023-12-31 | 2024-01-01 ~ 2025-12-31 | 2026-01-01 ~ today |
| 訊號數 | 33 (6.6/年) | 12 (6.0/年) | 1 |
| 勝率 | 60.6% | **66.7%** | 0.0% |
| 平均報酬 | +1.27% | +0.69% | -10.13% |
| 累計報酬 | +34.88% | +5.07% | -10.13% |
| 平均持倉 | 7.4 天 | 11.4 天 | 2.0 天 |
| 最大回撤 | -14.93% | -14.89% | -12.94% |
| 最大連續虧損 | 4 | 1 | 1 |

**分析**：
- Part B 勝率 66.7% 優於 FCX-001 的 60.0%，但平均報酬 +0.69% 遠低於 FCX-001 的 +4.83%
- 訊號頻率高（6.0-6.6/年 vs FCX-001 的 2.5-3.6/年），但品質較低
- Part A 累計 +34.88% 遠低於 FCX-001 的 +90.41%
- 2022 熊市期間連續 4 次停損（4-7月），顯示回檔閾值 -9% 在持續下跌行情中過於寬鬆
- 結論：回檔 + WR 模式在 FCX 的表現不如極端超賣模式，FCX-001 仍為最佳

---

## FCX-003: Optimized Exit + Close Position Filter（3 次嘗試均失敗）

**目標**：在 FCX-001 的三重極端超賣進場基礎上，嘗試改善風險調整後報酬（Sharpe/Sortino），並維持 Part A/B 平衡。

### 嘗試紀錄

#### Attempt 1: 收窄 SL -10% + 延長持倉 30 天

**假設**：近期虧損均在 -3%~-6%（到期出場），收窄 SL 可降低尾部風險；延長持倉給慢速反彈更多時間。

| 指標 | FCX-001 Part A | Att1 Part A | FCX-001 Part B | Att1 Part B |
|------|---------------|-------------|---------------|-------------|
| 勝率 | 72.2% | 66.7% | 60.0% | 60.0% |
| Sharpe | 0.43 | 0.37 | 0.74 | 0.40 |
| 累計 | +90.41% | +70.43% | +25.34% | +16.00% |
| MDD | -15.83% | -15.83% | -11.36% | -11.36% |

**失敗原因**：SL -10% 將 2 筆可恢復深跌交易轉為停損（2019-08-09: FCX-001 +10% → Att1 -10%，2024-07-24: -0.59% → -10%）。FCX 日波動 2-4% 需要 -12% SL 呼吸空間。

#### Attempt 2: 僅延長持倉 30 天（SL 維持 -12%）

**假設**：延長持倉捕捉慢速反彈，2023-05-04 的 +8.95% 到期可能達到 +10% TP。

| 指標 | FCX-001 Part A | Att2 Part A | FCX-001 Part B | Att2 Part B |
|------|---------------|-------------|---------------|-------------|
| 勝率 | 72.2% | 72.2% | 60.0% | 60.0% |
| Sharpe | 0.43 | 0.43 | 0.74 | 0.49 |
| 累計 | +90.41% | +90.68% | +25.34% | +18.75% |

**失敗原因**：Part A 2023-05-04 成功轉為達標（+10%），但 Part B 2024-07-24 從 -0.59%(25天) 惡化至 -8.00%(30天)。延長持倉對持續下跌的交易反而加深虧損。

#### Attempt 3（最終版本）: 加入 Close Position ≥ 40% 過濾

**假設**：仿照 GLD-007 的反轉K線過濾，移除「仍在下跌」的訊號（收盤位於日內低位），減少熊市停損。

### 進場條件（全部滿足）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 60 日高點回撤 | ≤ -18% | 確認深度回撤（同 FCX-001） |
| 2 | RSI(10) | < 28 | 極端超賣（同 FCX-001） |
| 3 | SMA50 乖離 | ≤ -8% | 偏離均線過大（同 FCX-001） |
| 4 | 收盤位置 | ≥ 40% | 反轉K線確認（新增） |
| 冷卻 | 訊號間隔 | ≥ 15 交易日 | 避免重複訊號 |

### 出場參數

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 | +10% | 同 FCX-001 |
| 停損 | -12% | 同 FCX-001 |
| 持倉天數 | 25 天 | 同 FCX-001 |

### 成交模型

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價） |
| 獲利出場 | `limit_order Day`（當日限價單） |
| 停損出場 | `stop_market GTC`（持倉期間停損市價） |
| 到期出場 | `next_open_market`（隔日開盤市價） |
| 滑價 | 0.15%（個股滑價較 ETF 大） |
| 悲觀認定 | 是（同 bar 停損與獲利同時觸發 → 假設停損先成交） |

### 回測結果

| 指標 | Part A (In-Sample) | Part B (Out-of-Sample) | Part C (Live) |
|------|-------------------|----------------------|---------------|
| 區間 | 2019-01-01 ~ 2023-12-31 | 2024-01-01 ~ 2025-12-31 | 2026-01-01 ~ today |
| 訊號數 | 11 (2.2/年) | 4 (2.0/年) | 0 |
| 勝率 | 72.7% | 75.0% | — |
| 平均報酬 | +4.74% | +2.49% | — |
| 累計報酬 | +59.50% | +8.53% | — |
| 平均持倉 | 11.9 天 | 11.0 天 | — |
| 最大回撤 | -19.54% | -14.13% | — |
| Sharpe | 0.54 | 0.28 | — |
| Sortino | 0.90 | 0.41 | — |

**失敗原因**：Close position 過濾改變了訊號日期（如 2019-05-01→2019-05-21），而非單純移除壞訊號。Part A Sharpe 改善（0.54 vs 0.43）但訊號數大幅減少（11 vs 18），MDD 惡化至 -19.54%。Part B Sharpe 崩潰（0.28 vs 0.74），累計從 +25.34% 降至 +8.53%。

### 結論

FCX-001 的三重極端超賣條件（-18%回撤 + RSI<28 + SMA50乖離≤-8%）搭配寬出場（+10%/-12%/25天）已經是 FCX 的全域最優組合。三個改善嘗試驗證了：
1. **SL -12% 是 FCX 的底線** — 收窄至 -10% 會觸發可恢復的深跌，FCX 日波動 2-4% 需要寬停損
2. **25 天持倉是最佳平衡** — 延長至 30 天對慢速反彈有幫助，但對持續下跌的交易加深虧損
3. **Close Position 過濾在個股上行為不可預測** — 與 GLD-007 不同，FCX 的極端超賣日常伴隨低 close position，過濾器改變訊號日期而非精準移除壞訊號

---

## FCX-001 滾動窗口績效分析 (Rolling Window Performance Analysis)

> **分析日期：** 2026-03-29
> **窗口：** 2 年，步進 6 個月（共 12 個窗口）

### 滾動窗口績效表

| 窗口 | 訊號 | 勝率 | 平均報酬 | 累計報酬 | MDD | ΔWR |
|------|------|------|----------|----------|-----|-----|
| 2019-01~2020-12 | 7 | 71.4% | +3.68% | +24.35% | -14.31% | — |
| 2019-07~2021-06 | 6 | 83.3% | +6.31% | +41.52% | -14.31% | +11.9pp |
| 2020-01~2021-12 | 5 | 80.0% | +5.57% | +28.65% | -14.31% | -3.3pp |
| 2020-07~2022-06 | 6 | 66.7% | +2.62% | +13.05% | -15.83% | -13.3pp |
| 2021-01~2022-12 | 7 | 71.4% | +3.68% | +24.35% | -15.83% | +4.8pp |
| 2021-07~2023-06 | 8 | 75.0% | +4.34% | +35.48% | -15.83% | +3.6pp |
| 2022-01~2023-12 | 9 | 66.7% | +3.12% | +26.55% | -15.83% | -8.3pp |
| 2022-07~2024-06 | 5 | 80.0% | +6.47% | +35.46% | -10.55% | +13.3pp |
| 2023-01~2024-12 | 6 | 50.0% | +3.29% | +19.97% | -11.36% | -30.0pp |
| 2023-07~2025-06 | 6 | 50.0% | +2.93% | +17.08% | -11.36% | +0.0pp |
| 2024-01~2025-12 | 5 | 60.0% | +4.83% | +25.34% | -11.36% | +10.0pp |
| 2024-07~2026-03 | 6 | 66.7% | +4.58% | +29.50% | -11.36% | +6.7pp |

### 預測精準度表

| 窗口 | WR | 平均贏利 | 平均虧損 | 盈虧比 | 差點成功 |
|------|------|----------|----------|--------|----------|
| 2019-01~2020-12 | 71.4% | +10.00% | -12.13% | 2.06 | — |
| 2019-07~2021-06 | 83.3% | +10.00% | -12.13% | 4.12 | — |
| 2020-01~2021-12 | 80.0% | +10.00% | -12.13% | 3.30 | — |
| 2020-07~2022-06 | 66.7% | +10.00% | -12.13% | 1.65 | — |
| 2021-01~2022-12 | 71.4% | +10.00% | -12.13% | 2.06 | — |
| 2021-07~2023-06 | 75.0% | +9.83% | -12.13% | 2.43 | 1/1 |
| 2022-01~2023-12 | 66.7% | +9.83% | -10.28% | 1.91 | 1/2 |
| 2022-07~2024-06 | 80.0% | +9.74% | -6.59% | 5.91 | 1/2 |
| 2023-01~2024-12 | 50.0% | +9.65% | -3.06% | 3.15 | 1/4 |
| 2023-07~2025-06 | 50.0% | +10.00% | -4.15% | 2.41 | 0/3 |
| 2024-01~2025-12 | 60.0% | +10.00% | -2.93% | 5.12 | 0/2 |
| 2024-07~2026-03 | 66.7% | +8.33% | -2.93% | 5.69 | 1/3 |

### 漸變性評估

- **勝率範圍**：50.0% ~ 83.3%（ΔWR 標準差 12.3pp，最大跳動 30.0pp）
- **盈虧比範圍**：1.65 ~ 5.91（ΔPF 標準差 1.88）
- **累計報酬範圍**：+13.05% ~ +41.52%（ΔCum 標準差 11.47%）
- **平均贏利範圍**：+8.33% ~ +10.00%（接近 TP +10%）
- **平均虧損範圍**：-12.13% ~ -2.93%（近期虧損大幅收窄）

**判定：**
- ✗ 預測精準度突變（勝率最大跳動 30.0pp > 20pp 閾值，發生在窗口 2022-07~2024-06 → 2023-01~2024-12）
- ✓ 下游績效漸變（勝/虧報酬互補抵消精準度變化）

### 分析解讀

1. **全窗口正累計報酬**：12 個窗口全部保持正累計報酬（最低 +13.05%），這在所有已分析資產中表現出色。相比 TQQQ-010 有 1 個負累計窗口、SOXL-001 有 11/12 負累計，FCX-001 展現了出色的穩定性。
2. **2022 熊市韌性**：即使在 2020-07~2022-06 窗口（含 2022 熊市），勝率仍維持 66.7%，累計 +13.05%。三重條件過濾（回撤+RSI+SMA乖離）有效避免了 FCX-002 在 2022 年連續 4 次停損的問題，與 cross_asset_lessons #1（訊號品質 > 數量）完全一致。
3. **近期勝率下降但盈虧比改善**：2023-2025 年勝率降至 50-60%，但平均虧損從 -12.13% 大幅收窄至 -2.93%~-4.15%。虧損交易多為到期出場而非停損，「差點成功」比例升高（如 1/4、0/3），顯示策略方向正確但未在 25 天內達到 +10% TP。這暗示近期銅礦反彈速度較慢，但不代表策略失效。
4. **A/B 訊號頻率比**：Part A 3.6/年 vs Part B 2.5/年，比例約 1.44:1，在 cross_asset_lessons #8 的「優秀~可接受」範圍內。
5. **與跨資產教訓一致性**：FCX-001 的寬出場（+10%/-12%/25天）與 cross_asset_lessons #2 一致——FCX 日波動 2-4%，禁用 trailing stop 是正確選擇。三重條件過濾也符合 #11（個股高 Beta 資產應用極端超賣多重條件而非淺回檔）。
6. **潛在改善方向**：近期「差點成功」比例偏高，若降低 TP 至 +8% 或延長持倉至 30 天，可能捕獲更多到期出場的正報酬交易。但需注意 cross_asset_lessons #9 警告降低 TP 可能只壓縮利潤，建議先用數據驗證再調整。

---

## FCX-002 滾動窗口績效分析 (Rolling Window Performance Analysis)

> **分析日期：** 2026-03-29
> **窗口：** 2 年，步進 6 個月（共 12 個窗口）

### 滾動窗口績效表

| 窗口 | 訊號 | 勝率 | 平均報酬 | 累計報酬 | MDD | ΔWR |
|------|------|------|----------|----------|-----|-----|
| 2019-01~2020-12 | 11 | 63.6% | +1.41% | +11.80% | -14.26% | — |
| 2019-07~2021-06 | 11 | 72.7% | +2.33% | +24.46% | -14.26% | +9.1pp |
| 2020-01~2021-12 | 12 | 75.0% | +3.43% | +45.12% | -14.26% | +2.3pp |
| 2020-07~2022-06 | 13 | 69.2% | +2.39% | +30.42% | -14.93% | -5.8pp |
| 2021-01~2022-12 | 16 | 68.8% | +2.31% | +36.71% | -14.93% | -0.5pp |
| 2021-07~2023-06 | 16 | 62.5% | +0.99% | +10.19% | -14.93% | -6.2pp |
| 2022-01~2023-12 | 15 | 46.7% | -0.74% | -15.40% | -14.93% | -15.8pp |
| 2022-07~2024-06 | 13 | 53.8% | +0.75% | +6.19% | -13.13% | +7.2pp |
| 2023-01~2024-12 | 13 | 46.2% | -0.94% | -14.50% | -14.89% | -7.7pp |
| 2023-07~2025-06 | 13 | 61.5% | +0.93% | +9.53% | -14.89% | +15.4pp |
| 2024-01~2025-12 | 12 | 66.7% | +0.69% | +5.07% | -14.89% | +5.1pp |
| 2024-07~2026-03 | 10 | 50.0% | -1.33% | -15.51% | -14.89% | -16.7pp |

### 預測精準度表

| 窗口 | WR | 平均贏利 | 平均虧損 | 盈虧比 | 差點成功 | ΔPF |
|------|------|----------|----------|--------|----------|-----|
| 2019-01~2020-12 | 63.6% | +8.00% | -10.13% | 1.38 | — | — |
| 2019-07~2021-06 | 72.7% | +7.01% | -10.13% | 1.84 | 1/1 | +0.46 |
| 2020-01~2021-12 | 75.0% | +7.63% | -9.16% | 2.50 | 1/2 | +0.66 |
| 2020-07~2022-06 | 69.2% | +7.63% | -9.40% | 1.82 | 1/2 | -0.68 |
| 2021-01~2022-12 | 68.8% | +7.69% | -9.55% | 1.77 | 1/2 | -0.05 |
| 2021-07~2023-06 | 62.5% | +7.66% | -10.13% | 1.26 | 1/1 | -0.51 |
| 2022-01~2023-12 | 46.7% | +8.00% | -8.39% | 0.83 | 0/2 | -0.43 |
| 2022-07~2024-06 | 53.8% | +7.08% | -6.64% | 1.24 | 1/4 | +0.41 |
| 2023-01~2024-12 | 46.2% | +5.91% | -6.82% | 0.74 | 2/6 | -0.50 |
| 2023-07~2025-06 | 61.5% | +5.45% | -6.30% | 1.38 | 3/6 | +0.64 |
| 2024-01~2025-12 | 66.7% | +5.45% | -8.82% | 1.23 | 3/4 | -0.15 |
| 2024-07~2026-03 | 50.0% | +6.42% | -9.08% | 0.71 | 1/2 | -0.52 |

### 漸變性評估

- **勝率範圍**：46.2% ~ 75.0%（ΔWR 標準差 9.7pp，最大跳動 16.7pp）
- **盈虧比範圍**：0.71 ~ 2.50（ΔPF 標準差 0.49）
- **累計報酬範圍**：-15.51% ~ +45.12%（ΔCum 標準差 19.18%）
- **平均贏利範圍**：+5.45% ~ +8.00%（遠低於 TP +8%，多數到期出場）
- **平均虧損範圍**：-10.13% ~ -6.30%（接近 SL -10%）

**判定：**
- ✓ 預測精準度漸變（勝率最大跳動 16.7pp ≤ 20pp 閾值）
- ✓ 下游績效漸變

### 分析解讀

1. **3 個窗口負累計報酬**：2022-01~2023-12（-15.40%）、2023-01~2024-12（-14.50%）、2024-07~2026-03（-15.51%）。對比 FCX-001 的 12/12 窗口全正，FCX-002 穩定性明顯不足。
2. **2022 熊市暴露弱點**：2022-01~2023-12 窗口勝率暴跌至 46.7%，與 FCX-002 回測中連續 4 次停損一致。回檔 -9% 門檻在持續下跌行情中過淺，產生低品質訊號，驗證 cross_asset_lessons #11（個股高 Beta 資產不適合淺回檔策略）。
3. **訊號多但品質低**：每窗口 10-16 筆訊號（vs FCX-001 的 5-9 筆），但平均報酬僅 +0.99%~+3.43%（正窗口），遠低於 FCX-001 的 +2.62%~+6.47%。驗證 cross_asset_lessons #1（訊號品質 > 數量）。
4. **近期「差點成功」比例極高**：2023-07~2025-06 窗口 3/6 到期出場為正報酬，2024-01~2025-12 窗口 3/4，顯示 TP +8% 在近期市場環境下太高。但即使捕獲這些交易，整體績效仍遠不如 FCX-001。
5. **與 FCX-001 對比**：FCX-002 漸變性（ΔWR 9.7pp vs 12.3pp）表面上更好，但這是因為 FCX-002 勝率整體偏低（46-75% vs 50-83%），波動空間本就較小。FCX-001 雖有一次 30pp 跳動，但所有窗口均為正累計，展現了更強的「底線保護」能力。
6. **結論**：FCX-002 的滾動分析進一步確認其不如 FCX-001。回檔+WR 模式在 FCX 上訊號過多、品質不足，熊市脆弱，且近期 MDD 持續偏高（-14.89%）。FCX-001 的三重極端超賣條件仍是 FCX 的正確策略。

---

## FCX-004: BB Squeeze Breakout

**目標**：首次在 FCX 嘗試突破策略。基於 TSLA-005/NVDA-003 成功經驗（日波動 3-4% 的個股 BB 擠壓突破），移植至 FCX（日波動 2-4%）。與 FCX-001~003 的均值回歸方向完全不同。

### 進場條件（全部滿足）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | BB Width | 60日 30th 百分位，5日內曾發生 | 近期波動收縮（擠壓） |
| 2 | Close | > Upper BB(20,2) | 突破上軌 |
| 3 | Close | > SMA(50) | 趨勢向上 |
| 冷卻 | 訊號間隔 | ≥ 10 交易日 | 避免重複訊號 |

### 出場參數

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 | +8% | FCX 突破 TP 甜蜜點（+10% 使贏利交易翻轉，Att3 驗證） |
| 停損 | -7% | 突破策略 SL 較均值回歸更緊（~2σ，同 TSLA/NVDA） |
| 持倉天數 | 20 天 | 突破後動能延續標準期間 |

### 成交模型

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價） |
| 獲利出場 | `limit_order Day`（當日限價單） |
| 停損出場 | `stop_market GTC`（持倉期間停損市價） |
| 到期出場 | `next_open_market`（隔日開盤市價） |
| 滑價 | 0.15%（個股滑價較 ETF 大） |
| 悲觀認定 | 是（同 bar 停損與獲利同時觸發 → 假設停損先成交） |

### 回測結果（Att2 — 最佳配置）

| 指標 | Part A (In-Sample) | Part B (Out-of-Sample) | Part C (Live) |
|------|-------------------|----------------------|---------------|
| 區間 | 2019-01-01 ~ 2023-12-31 | 2024-01-01 ~ 2025-12-31 | 2026-01-01 ~ today |
| 訊號數 | 23 (4.6/年) | 6 (3.0/年) | 1 |
| 勝率 | 69.6% | 66.7% | 0.0% |
| 平均報酬 | +3.43% | +2.95% | -7.14% |
| 累計報酬 | **+106.31%** | +17.31% | -7.14% |
| 平均持倉 | 7.6 天 | 11.8 天 | 4.0 天 |
| 最大回撤 | -10.09% | -14.42% | -11.94% |
| 盈虧比 | 2.69 | 2.24 | 0.00 |
| **Sharpe** | **0.51** | **0.41** | 0.00 |
| 最大連續虧損 | 2 | 1 | 1 |

### 與 FCX-001 比較

| 指標 | FCX-001 | FCX-004 (Att2) | 差異 |
|------|---------|----------------|------|
| Part A Sharpe | 0.43 | **0.51** | **+18.6%** |
| Part B Sharpe | **0.74** | 0.41 | -44.6% |
| min(A,B) Sharpe | 0.43 | 0.41 | -4.7% |
| Part A 訊號/年 | 3.6 | 4.6 | +27.8% |
| Part B 訊號/年 | 2.5 | 3.0 | +20.0% |
| A/B 年化訊號比 | 1.44:1 | **1.53:1** | 略寬 |
| Part A 累計 | +90.41% | **+106.31%** | **+17.6%** |
| Part A MDD | -15.83% | **-10.09%** | **-36.3%** |

**分析**：FCX-004 Part A 顯著優於 FCX-001（Sharpe +18.6%、累計 +17.6%、MDD 改善 36.3%）。Part B 因 2 筆停損訊號（2024-05-14、2025-08-26）使 Sharpe 低於 FCX-001。兩種策略捕捉完全不同的市場機會（突破 vs 恐慌抄底），可作為互補策略。

### 嘗試紀錄

#### Att1: 原始 TSLA-005 移植（pct25, cd15, TP+8%/SL-7%）

Part A Sharpe 0.44 / Part B Sharpe 0.00*（4訊號全+8%，std=0 導致退化）。A/B 訊號比 21:4 = 5.25:1，嚴重不平衡。Part B 雖 100% WR 但僅 4 筆訊號統計意義不足。

#### Att2: 放寬擠壓 + 縮短冷卻（pct30, cd10, TP+8%/SL-7%）✓

Part A Sharpe **0.51** / Part B **0.41**。年化訊號比 4.6:3.0 = 1.53:1，A/B 平衡大幅改善。新增的 Part A 訊號（2019-11-07、2021-05-05）均為好訊號（+8%/+8%），Part B 新增 2 筆（2024-05-14 停損、2025-08-26 停損）雖為虧損但提供統計意義。

#### Att3: 加大 TP/SL（pct30, cd10, TP+10%/SL-8%）

Part A Sharpe 0.29 / Part B 0.32。TP+10% 使 5 筆 Part A 贏利交易（原本達 +8%）變為到期（+4.65%、+7.14%、-1.70%、+0.24%、+5.32%）。確認 FCX 突破 TP+8% 是硬上限，類似 NVDA +8%、USO +3.0%、TSM +7% 現象。

---

## FCX-005: Momentum Pullback / RSI(2) Short-Term Mean Reversion（3次嘗試均失敗）

**目標**：探索動量回檔（趨勢跟蹤）和 RSI(2) 短期均值回歸兩種全新策略方向。

### Attempt 1：動量回檔（Momentum Pullback）

**進場條件：** Close > SMA(50) + 20日 ROC > 5% + 2日跌幅 <= -3%，冷卻 10 天
**出場：** TP +8% / SL -7% / 20天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 29 | 8 |
| 勝率 | 51.7% | 12.5% |
| Sharpe | 0.09 | -0.84 |
| 累計 | +12.45% | -30.86% |

**失敗原因**：Part B 出現 7 連續停損。FCX 2024-2025 處於宏觀下行趨勢，SMA(50)+ROC(5%) 的趨勢過濾太弱，在假反彈中進場後遭遇趨勢反轉。

### Attempt 2：強趨勢過濾

**進場條件：** SMA(50) > SMA(200) 黃金交叉 + 20日 ROC > 8% + 2日跌幅 <= -3%，冷卻 10 天
**出場：** TP +8% / SL -7% / 20天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 17 | 3 |
| 勝率 | 41.2% | 0.0% |
| Sharpe | -0.12 | -1.46 |
| 累計 | -18.29% | -13.90% |

**失敗原因**：黃金交叉 + ROC 8% 過嚴，Part B 僅 3 訊號全為停損。A/B 比 5.67:1 嚴重不平衡。Part A 也劣化（WR 41.2%），說明即使在確認上升趨勢中，FCX 的短期回檔仍不可靠。

### Attempt 3：RSI(2) 短期均值回歸

**進場條件：** RSI(2) < 10 + 2日跌幅 >= 4%，冷卻 10 天
**出場：** TP +8% / SL -7% / 20天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 34 | 13 |
| 勝率 | 38.2% | 53.8% |
| Sharpe | -0.22 | 0.24 |
| 累計 | -46.45% | +18.84% |

**失敗原因**：RSI(2) < 10 在 FCX 2-4% 日波動下觸發過頻（6.8/年），Part A WR 僅 38.2%，遠低於 TP+8%/SL-7% 所需的盈虧平衡點 ~47%。有趣的是 Part B 反而正報酬（0.24），但 A/B 不一致使策略不可信。

### 關鍵教訓

1. **動量回檔（trend pullback）不適用 FCX**：FCX 的趨勢反轉極為劇烈，「上升趨勢中的回檔」經常演變為完整的趨勢反轉，不像 SPY/DIA 等大盤指數有較強的趨勢慣性
2. **RSI(2) 在 2-4% 日波動資產上品質不足**：RSI(2) < 10 的觸發頻率雖然適中（~6/年），但在 FCX 的高波動環境下，2日極端超賣往往是更大下跌的開始而非反彈起點
3. **FCX 最有效的策略仍是極端超賣（FCX-001）和波動擠壓突破（FCX-004）**：FCX 需要更嚴格的進場過濾才能維持正報酬

---

## FCX-006: Relative Strength (FCX vs COPX)（3次嘗試均失敗）

**策略類型**：相對強度（Relative Strength）
**靈感來源**：TSM-008（TSM vs SMH RS，Sharpe 0.79/0.83）
**假設**：FCX 相對 COPX（銅礦板塊 ETF）超額表現 + 短期回調 = 個股動量捕捉機會

### 進場條件
- FCX 20日報酬 - COPX 20日報酬 >= RS_MIN（相對超額表現）
- 5日高點回撤 PULLBACK_MIN ~ PULLBACK_MAX（短暫整理）
- Close > SMA(50)（上升趨勢確認）
- 冷卻期 10 個交易日

### 三次嘗試

| 嘗試 | RS_MIN | Pullback | TP/SL/Hold | Part A Sharpe | Part B Sharpe | Part B 訊號 | A/B 比 |
|------|--------|----------|------------|---------------|---------------|-------------|--------|
| Att1 | ≥5% | 3-7% | +8%/-7%/25d | 0.20 | -0.15 | 5 | 6:1 |
| Att2 | ≥8% | 3-8% | +8%/-7%/25d | -0.10 | N/A | 0 | ∞ |
| Att3 | ≥3% | 3-8% | +8%/-7%/25d | 0.18 | -0.19 | 9 | 4.7:1 |

### 失敗原因分析

1. **FCX-COPX RS 時間不穩定**：2020 年銅礦復甦期 FCX 大幅超越 COPX（公司重組 + 銅價飆漲），但 2024-2025 兩者高度同步移動。RS 訊號集中在 Part A 的 2020 年（Att1 該年 12 個訊號），Part B 幾乎無訊號
2. **與 TSM-SMH 的關鍵差異**：TSM 有持續性的技術領先優勢（先進製程護城河）使其相對 SMH 的超額表現可預測；FCX 作為商品生產者，相對 COPX 的超額表現更多由短期事件驅動（罷工、礦場問題），不具持續性
3. **A/B 訊號比嚴重不平衡**：所有嘗試的 A/B 年化訊號比均 > 4:1，遠超 2:1 警戒線

### 結論

相對強度策略不適用於 FCX-COPX 配對。個股 vs 板塊 ETF 的 RS 方法僅在個股有持續性結構優勢時有效（如 TSM 的先進製程），純商品生產者的 RS 表現缺乏可預測性。

---

## FCX-007: Donchian Channel Breakout（3次嘗試均失敗）

**目標**：以 Donchian 通道突破（N 日新高）作為趨勢啟動訊號，嘗試與 BB Squeeze（FCX-004）互補的突破策略。

**假說**：FCX 銅礦股在商品週期中有強烈趨勢特性，當價格突破 N 日新高且處於上升趨勢中，代表趨勢啟動。Donchian 突破基於實際價格高點，與 BB 上軌（基於統計偏差）提供不同的突破判定。

### Attempt 1：Donchian(20) + SMA(50)

**進場條件**：Close > 20日最高價 + Close > SMA(50) + 冷卻10天
**出場**：TP+8% / SL-7% / 20天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 42 (8.4/yr) | 12 (6.0/yr) |
| 勝率 | 45.2% | 58.3% |
| 累計報酬 | -26.47% | +17.65% |
| Sharpe | **-0.06** | **0.23** |
| MDD | -10.09% | -14.42% |

**失敗原因**：20日 Donchian 門檻太低，FCX 頻繁突破新20日高點，產生大量假突破。Part A 42訊號品質極差（WR 45.2%），A/B 比 3.5:1。

### Attempt 2：Donchian(50) + SMA(50) + 冷卻15天

**進場條件**：Close > 50日最高價 + Close > SMA(50) + 冷卻15天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 24 (4.8/yr) | 7 (3.5/yr) |
| 勝率 | 54.2% | 57.1% |
| 累計報酬 | +39.89% | +1.05% |
| Sharpe | **0.23** | **0.06** |
| MDD | -10.09% | -10.17% |

**失敗原因**：延長至50日降低訊號數但 Part B 崩潰（Sharpe 0.06），A/B 比 3.4:1 仍不平衡。max consec. loss 5（Part A）。

### Attempt 3：Donchian(30) + BB Squeeze + SMA(50)

**進場條件**：Close > 30日最高價 + 5日內 BB Width < 60日30th百分位 + Close > SMA(50) + 冷卻10天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 24 (4.8/yr) | 4 (2.0/yr) |
| 勝率 | 50.0% | 75.0% |
| 累計報酬 | -3.09% | +16.98% |
| Sharpe | **0.02** | **0.64** |
| MDD | -10.09% | -10.17% |

**失敗原因**：加入 BB Squeeze 過濾大幅改善 Part B（0.64），但 A/B 訊號比惡化至 6:1。Part A 仍然近乎零（Sharpe 0.02），策略在 IS 期間完全不可靠。

### 綜合結論

1. **Donchian 突破在 FCX 上結構性不穩定**：商品週期造成不同時期的突破模式差異巨大，三種嘗試的 A/B 比均 > 3:1
2. **BB Squeeze 過濾改善品質但加劇不平衡**：Att3 Part B 0.64 是所有 FCX 突破策略最佳 OOS，但 Part A 0.02 表明過濾器在 IS 期間移除好訊號而非壞訊號
3. **FCX-004 BB Squeeze Breakout 仍為突破策略最佳**：BB 上軌（統計自適應門檻）優於 Donchian 固定回看高點，因前者隨波動度自動調整
4. **確認 FCX-001/FCX-004 為全域最優**：7 次實驗、24+ 次嘗試，含均值回歸、突破（BB Squeeze + Donchian）、動量回檔、RSI(2)、相對強度六大策略類型

---

## FCX-008: Sharp Drop + Extreme Oversold Mean Reversion（3次嘗試，Att3 Part B 最佳但 min < FCX-001）

**目標**：在 FCX-001 三重極端超賣基礎上，嘗試三種不同的額外過濾方向（趨勢跟蹤、ATR 波動率自適應、2日急跌），以改善 A/B 平衡或提升 min(A,B) Sharpe。

### Attempt 1：趨勢跟蹤（SMA 黃金交叉 + 回檔至 SMA50）— FAILED

**假說**：FCX 銅礦股有強週期趨勢，上升趨勢中的 SMA(50) 回測提供低風險進場。

**進場條件**：SMA(50) > SMA(200) + SMA(50) 5日斜率 > 0 + Close 在 SMA(50) ±2% 內 + Close > 前日 Close（反彈確認）+ 冷卻15天
**出場**：TP+8% / SL-7% / 20天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 17 (3.4/yr) | 4 (2.0/yr) |
| 勝率 | 47.1% | 25.0% |
| 累計報酬 | -0.45% | -18.51% |
| Sharpe | **-0.00** | **-0.63** |

**失敗原因**：確認 lesson #71——FCX 趨勢反轉太劇烈，「上升趨勢中的回檔」經常演變為完整反轉。Part B WR 僅 25%，4 筆中 3 筆停損。

### Attempt 2：FCX-001 + ATR(5)/ATR(20) > 1.05 波動率自適應

**假說**：ATR 波動率過濾能區分恐慌急跌（高 ATR ratio）與慢磨下跌（低 ATR ratio），移除品質較差的慢磨訊號。

**進場條件**：FCX-001 三重條件（DD ≤ -18% + RSI(10) < 28 + SMA50 乖離 ≤ -8%）+ ATR(5)/ATR(20) > 1.05 + 冷卻15天
**出場**：TP+10% / SL-12% / 25天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 14 (2.8/yr) | 4 (2.0/yr) |
| 勝率 | 64.3% | 75.0% |
| 累計報酬 | +44.65% | +27.15% |
| Sharpe | **0.25** | **0.82** |

**失敗原因**：ATR > 1.05 改善 Part B（0.74→0.82），但 Part A 嚴重退化（0.43→0.25）。FCX 極端超賣條件本身就需要高波動才能觸發，ATR 對這些訊號的額外過濾力有限——移除好訊號（3 筆贏利）多於壞訊號。確認 lesson #103：ATR 在日波動 2-4% 下跨期不穩定。

### Attempt 3：FCX-001 + 2日跌幅 ≤ -5%（USO-013 風格）— 最佳 A/B 平衡

**假說**：USO-013 的 2日急跌過濾極為成功（Sharpe 0.26/0.82），比 ATR 更直接偵測恐慌拋售。FCX 日波動 2-4%，-5% 門檻約 0.8-1.3σ/日。

**進場條件（全部滿足）**：

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 60 日高點回撤 | ≤ -18% | 確認深度回撤（同 FCX-001） |
| 2 | RSI(10) | < 28 | 極端超賣（同 FCX-001） |
| 3 | SMA50 乖離 | ≤ -8% | 偏離均線過大（同 FCX-001） |
| 4 | 2日價格跌幅 | ≤ -5% | 急跌確認，過濾慢磨下跌 |
| 冷卻 | 訊號間隔 | ≥ 15 交易日 | 避免重複訊號 |

**出場參數**（同 FCX-001）：TP+10% / SL-12% / 25天

**成交模型**（同 FCX-001）：next_open_market 進場，滑價 0.15%

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 13 (2.6/yr) | 4 (2.0/yr) |
| 勝率 | 69.2% | 75.0% |
| 累計報酬 | +40.57% | +40.28% |
| Sharpe | **0.31** | **1.26** |
| MDD | -12.23% | -12.23% |

**分析**：
- Part B 大幅改善（0.74→1.26，+70%），A/B 累計近乎完美平衡（+40.57%/+40.28%）
- 但 Part A 退化（0.43→0.31），因 2日急跌過濾移除了 5 筆 Part A 訊號，其中 3 筆為贏利交易
- 關鍵改善：2024-07-24 訊號被過濾（慢磨下跌），2024-08-02 新訊號觸發（真正急跌），從 -0.59% 到期翻為 +10% 達標
- min(A,B) = 0.31 < FCX-001 的 0.43，未能改善全域最優

### 綜合結論

1. **趨勢跟蹤在 FCX 完全失敗**（Att1）：確認 lesson #71，高波動週期股趨勢反轉太劇烈
2. **ATR 波動率自適應改善 OOS 但退化 IS**（Att2）：極端超賣條件本身就要求高波動，ATR 額外過濾力有限
3. **2日急跌過濾提供最佳 A/B 平衡**（Att3）：Part B 1.26 是所有 FCX 實驗最佳 OOS，A/B 累計比 1.01:1
4. **FCX-001 仍為 min(A,B) 全域最優**：8 次實驗、33+ 次嘗試，所有額外過濾器均無法同時改善 Part A 和 Part B

---

## 演進路線圖 (Roadmap)

```
FCX-001 (三重極端超賣，寬出場) ← 均值回歸最佳（已確認為全域最優）
  ├── FCX-002 (回檔+WR+反轉K線，跨資產驗證模式) ← 已完成，不如 FCX-001
  ├── FCX-003 (3次嘗試：SL收窄/延長持倉/ClosePos過濾) ← 已完成，全部不如 FCX-001
  ├── FCX-008 (3次嘗試：趨勢跟蹤/ATR自適應/2日急跌) ← 已完成，Att3 最佳 A/B 但 min<FCX-001
  ├── [低預期] 加入銅價/HG 確認（cross-asset lesson #6 警告額外確認指標通常無效）
  └── [禁止] 追蹤停損（cross-asset lesson #2：日波動 2-4% 禁用 trailing stop）

FCX-004 (BB Squeeze Breakout) ← 突破策略最佳，Part A Sharpe 0.51 優於 FCX-001
  ├── Att1 (pct25/cd15) → A/B 不平衡 5.25:1
  ├── Att2 (pct30/cd10) → 最佳配置，A/B 1.53:1 ✓
  └── Att3 (TP+10%/SL-8%) → TP+8% 是硬上限

FCX-005 (動量回檔 / RSI(2) 短期均值回歸) ← 全部失敗
  ├── Att1 (動量回檔：SMA50+ROC5%) → Part B -0.84，趨勢反轉殺手
  ├── Att2 (強趨勢：SMA50>SMA200+ROC8%) → Part B -1.46，訊號過少
  └── Att3 (RSI(2)<10+2日跌幅≥4%) → Part A -0.22，熊市觸發過頻

FCX-006 (Relative Strength: FCX vs COPX) ← 全部失敗
  ├── Att1 (RS>=5%, pullback 3-7%) → Part A 0.20 / Part B -0.15，A/B 6:1 不平衡
  ├── Att2 (RS>=8%, pullback 3-8%) → Part B 無訊號
  └── Att3 (RS>=3%, pullback 3-8%) → Part A 0.18 / Part B -0.19

FCX-007 (Donchian Channel Breakout) ← 全部失敗
  ├── Att1 (Donchian 20, SMA50, cd10) → Part A -0.06 / Part B 0.23，訊號太多太差
  ├── Att2 (Donchian 50, SMA50, cd15) → Part A 0.23 / Part B 0.06，Part B 崩潰
  └── Att3 (Donchian 30 + BB Squeeze, SMA50, cd10) → Part A 0.02 / Part B 0.64，A/B 6:1

FCX-008 (趨勢跟蹤→ATR自適應→2日急跌) ← Att3 Part B 最佳但 min<FCX-001
  ├── Att1 (趨勢跟蹤：SMA黃金交叉+回測SMA50) → Part A -0.00 / Part B -0.63，趨勢反轉
  ├── Att2 (FCX-001 + ATR>1.05) → Part A 0.25 / Part B 0.82，ATR 移除好訊號
  └── Att3 (FCX-001 + 2日跌幅≤-5%) → Part A 0.31 / Part B 1.26，最佳 A/B 平衡

FCX-009 (RSI(14) Bullish Hook Divergence + Pullback+WR) ← 全部失敗，跨資產 pattern 20b 驗證
  ├── Att1 (pullback [-9%,-18%] + hook delta=3 / max_min=35) → Part A 0.51 / Part B -0.33
  ├── Att2 (加嚴 delta=5) → Part A 0.76 / Part B -0.06，但 Part B 2024-11/12 雙筆到期
  └── Att3 (加深 pullback -11%, delta=5) → Part A 0.85 / Part B 0.30 / min 0.30，A/B 累計差 39.24pp

FCX-010 (Gap-Down Capitulation + 日內反轉) ← 全部失敗，**repo 首次 single-stock Gap-Down 試驗**
  ├── Att1 (Gap<=-2.0% + Close>Open + PB [-6%,-18%] + WR) → Part A 0.21 / Part B n=2 零方差 / min 0.00
  ├── Att2 (+ ClosePos>=50%) → Part A 0.36 / Part B 不變零方差 / min 0.00
  └── Att3 (Gap<=-2.5% + PB -8%) → Part A **0.87** / Part B n=1 零方差 / min 0.00（A/B 訊號比 2.0:1 崩潰）

FCX-011 (Post-Capitulation Vol-Transition MR / BB-lower hybrid) ← 全部失敗，**repo 首次 BB-lower hybrid 於高波動單一個股試驗**
  ├── Att1 (基線：BB(20,2) + PB cap -15% + WR + ClosePos + ATR, TP+6%/SL-7%/20d/cd10) → Part A 0.26 / Part B -0.23 / min -0.23
  ├── Att2 (+ 2DD cap >= -5%, CIBR-012 方向) → Part A -0.09 / Part B -0.09 / min -0.09（贏家過濾過嚴）
  └── Att3 (+ 2DD floor <= -5%, VGK/INDA/EEM 方向) → Part A 零方差 / Part B ~0 / min 0.00（訊號過稀疏）
     延伸 XBI-010 已建立之 BB-lower hybrid 1.75% vol 上限至**單一個股類別**

FCX-012 (Donchian Lower Washout + 日內反轉 MR) ← 全部失敗，**repo 首次此組合作為 MR 主進場**
  ├── Att1 (基線：Close 距 20d Low <= 2.5% + 今/昨 Low = 新低 + ClosePos + ATR + 60d DD [-30%,-10%], TP+9%/SL-11%/20d/cd15) → Part A 8/50%/-0.06 / Part B 6/50%/0.02 / min -0.06
  ├── Att2 (+ require today Low > yesterday Low = Day-After Capitulation) → Part A 1/零方差 / Part B 2/Sharpe 1.07 / min -0.60（過度過濾，3 訊號無統計意義）
  └── Att3 (回退 Att2，+ 2DD cap >= -7%, CIBR-012 方向) → Part A 7/42.9%/-0.20（**比 Att1 更差**）/ Part B 6/50%/0.02 不變 / min -0.20（cap 移除 1 TP 非 SL）
     擴展 cross-asset lesson #52 至「Donchian Lower binary 價格觸發器」類別，失敗家族與 FXI-009 Failed Breakdown Reversal 同源
```

## FCX-011: Post-Capitulation Vol-Transition MR（3 次嘗試均失敗）

**實驗目的：** 跨資產驗證 BB 下軌 + 回檔上限混合進場模式（VGK-008/INDA-010/EEM-014/CIBR-012 成功）是否延伸至**高波動單一個股**類別。

**假設：** FCX（銅礦龍頭 ~3% vol）具股權資本化動態（2016/2020/2022 急跌反彈），若成立則 BB 下軌統計自適應門檻 + 絕對回檔上限應能辨識「慢漂移 vs 真恐慌」，類似已驗證的 ETF 案例。

**結果：** 三次迭代全部未超越 FCX-004 min 0.41。混合模式在 FCX 上崩壞至 min -0.23 ~ 0.00，確認 **XBI-010 已建立的 1.75% vol 上限延伸至單一個股類別**。

**迭代明細：**

| 迭代 | 2DD 過濾 | Part A (訊號 WR Sharpe) | Part B (訊號 WR Sharpe) | min(A,B) |
|------|----------|------------------------|-------------------------|----------|
| Att1 | 停用（基線）| 3 訊號 / 66.7% / **0.26** | 5 訊號 / 40.0% / **-0.23** | **-0.23** |
| Att2 | cap >= -5%  | 2 訊號 / 50.0% / -0.09 | 2 訊號 / 50.0% / -0.09 | -0.09 |
| Att3 | floor <= -5% | 1 訊號 / 100% / 零方差 | 4 訊號 / 50.0% / ~0 | 0.00 |

**核心失敗根因：**

1. **BB 下軌選擇性低**：FCX 高波動使 BB 帶寬大，下軌觸及頻率高但品質未保證；Part B 2024-07-19 + 2024-12-13 均為 1-3 日快速 SL，signal-day 過濾器（ATR>1.15, ClosePos>=40%）無法分辨加速崩盤與真 capitulation。
2. **2DD 方向無選擇力**：FCX 贏家訊號的 2DD 分布橫跨 -3% ~ -8%，與輸家重疊——與 CIBR SLs 集中深 2DD（cap 有效）、VGK SLs 集中淺 2DD（floor 有效）之結構皆不同。Att2 cap 過濾器錯殺 2021-06-16 深 2DD 贏家（+6% TP）；Att3 floor 過濾器濾掉 2/3 Part A 訊號密度崩至 0.2/yr。
3. **單一個股事件結構**：FCX 事件驅動（銅價衝擊、公司信用、中國需求）使統計自適應 BB 下軌無法捕捉獨特事件結構；ETF 的分散化使 BB 成為有效 regime classifier，單一個股則事件突兀使 BB 失去選擇性。

**跨資產貢獻：**

- **Repo 第 1 次 BB-lower hybrid mode 於高波動單一個股試驗**——三次迭代全部失敗
- **擴展 cross-asset lesson #52**：BB-lower hybrid mode 有效邊界**從「1.75% vol ETF」延伸為「1.75% vol（涵蓋 ETF 與單一個股兩類別）」**
- **新失敗清單項**：高波動單一個股（FCX ~3%）正式加入不適用該模式的資產類別，繼 XBI 2.0% ETF、FXI 政策驅動 EM ETF、GLD/TLT 商品/利率 ETF 後
- **開放假設**：混合模式是否適用於**中低波動單一個股**（如日波動 1.5-2% 之防禦性股票）——尚未驗證，但 FCX-011 失敗並未排除此可能

**FCX-004（BB Squeeze Breakout）仍為 FCX 執行模型最優（min 0.41）；FCX-001（grandfathered 極端超賣 MR）仍為全域最佳（min 0.43）。**

## FCX-012: Donchian Lower Washout + 日內反轉 MR（3 次嘗試均失敗）

**實驗目的：** 探索 **repo 首次「Donchian 20 日低點觸及 + 日內反轉」組合**作為 MR 主進場訊號，測試 binary、非參數化的 washout 觸發器能否在 FCX（高波動、commodity-driven 單一個股）上打破 FCX-001 的 Part A/B 累計報酬 72% gap。

**假設：** FCX 作為銅礦個股，commodity panic 常以「連續下跌 + 某日觸及新低 + 盤中買盤湧入」模式結束。Donchian Low 觸及比統計 BB 下軌更 binary——BB 在高波動期帶寬持續擴大使下軌頻繁觸及但不代表真實底部，而 Donchian 新低是 unambiguous washout 事件。此設計針對 FCX 之 event-driven commodity panic 結構（2016 信貸、2020 COVID、2022 銅價暴跌）。

**結果：** 三次迭代全部未超越 FCX-004 min 0.41，Part A Sharpe 最佳僅 -0.06（Att1 基線）、最差 -0.20（Att3）。確認 **Donchian Lower binary 價格觸發器在 FCX 上結構性失效**。

**迭代明細：**

| 迭代 | 關鍵新增條件 | Part A (訊號 WR Sharpe) | Part B (訊號 WR Sharpe) | min(A,B) |
|------|--------------|------------------------|-------------------------|----------|
| Att1 | 基線（Donchian Low 觸及 + 日內反轉 + ATR + DD 範圍）| 8 / 50% / **-0.06** | 6 / 50% / **0.02** | **-0.06** |
| Att2 | + today Low > yesterday Low（Day-After）| 1 / 0% / 零方差 | 2 / 100% / 1.07 | **-0.60** |
| Att3 | 回退 Att2，+ 2DD cap >= -7%（CIBR-012 方向）| 7 / 42.9% / **-0.20** | 6 / 50% / 0.02 | **-0.20** |

**核心失敗根因：**

1. **Donchian Lower 觸及為「反轉候選」而非「反轉確認」**：在 FCX ~3% vol 上，commodity panic 常以多日連續 Donchian 新低為特徵（2019-08 trade war、2021-06 銅價頂部後、2022 夏秋升息、2024-07 銅價暴跌均有 3-5 連續新低日）。單日觸及 + 日內反轉不足以區分「尾段 washout」vs「中段 acceleration」。Att1 的 2 筆 -11% SL（2019-08-05、2023-04-25）正是 continuation-decline 陷阱。
2. **Day-After Capitulation 對 FCX 同樣失效**（擴展 lesson #20b 至 FCX 3% vol 個股，第三個資料點繼 URA 2.34% policy-driven、TLT 1% rate-driven 後）：強反轉結構過嚴使訊號崩至 3 筆，無統計意義。驗證「V-bounce ≠ genuine reversal」失敗家族在多階段下跌資產上的普遍性。
3. **2DD cap 對 FCX 無選擇力**：CIBR-012 成功的 2DD cap -4% 方向（淺 2DD = 減速、深 2DD = 加速）在 FCX 上不成立——FCX winners 的 2DD 分布橫跨 -3%~-8%，與 losers 重疊。Att3 的 2DD cap -7% 實際移除 1 筆 TP 而未移除任何 SL，WR 從 50% 降至 42.9%。呼應 FCX-011 Att2（2DD cap -5% min 0.00）的同一發現。

**跨資產貢獻：**

- **Repo 第 1 次「Donchian Lower Washout + 日內反轉」組合作為 MR 主進場試驗**——三次迭代全部失敗
- **擴展 cross-asset lesson #52 至「Donchian Lower binary 價格觸發器」類別**：binary 價格觸發器在「多段下跌」結構資產上結構性缺乏區分力。FXI-009 Failed Breakdown Reversal（政策驅動 EM ETF）+ FCX-012 Donchian Lower Washout（高波動 commodity 個股）共享同一失敗機制——單一時點的價格反轉確認無法辨識 washout 的階段
- **Day-After Capitulation 失敗家族第三個資料點**：URA（policy-driven 2.34%）+ TLT（rate-driven 1%）+ FCX（commodity-driven 3%）均失敗，涵蓋三種不同驅動因素與波動率範圍
- **FCX 第 12 種失敗策略類型**：均值回歸、突破（BB Squeeze + Donchian Upper）、動量回檔、RSI(2)、相對強度、趨勢跟蹤、波動率自適應、RSI bullish hook divergence、Gap-Down Capitulation、BB-lower hybrid mode、**Donchian Lower Washout**

**FCX-004（BB Squeeze Breakout）仍為 FCX 執行模型最優（min 0.41）；FCX-001（grandfathered 極端超賣 MR）仍為全域最佳（min 0.43）。**

---

## FCX-013: Multi-Week Regime-Aware BB Squeeze Breakout（3 次嘗試，Att3 SUCCESS k=1.00 嚴格）★ 突破策略當前最佳

**實驗目的：** 探索 **repo 第 3 次 lesson #22 試驗、首次商品/礦業單股驗證**，將 TSLA-015 / NVDA-012 已驗證的「buffered multi-week SMA trend regime gate」跨資產移植至 FCX-004 BB Squeeze Breakout 之上，目標解決 FCX-004 嚴重 A/B 失衡（cum gap 89%、訊號比 3.83:1）。

**假設：** FCX 為銅礦龍頭股（~3% vol），位於 lesson #22 已驗證的 vol 範圍內（TSLA 3.72% / NVDA 2.5-3%）。Buffered SMA(20) ≥ k × SMA(60) regime gate 可過濾 bear regime 假突破，保留 transition winners。重點測試 k 值跨資產移植性。

**結果：** 三次迭代，**Att3 SUCCESS** min(A,B) **0.55**（+34% vs FCX-004 0.41）。**重大跨資產發現**：FCX 反轉 lesson #22 的「k<1 緩衝」原則——k=1.00 嚴格優於 k=0.99/0.97 buffered。

**迭代明細：**

| 迭代 | k 值 | Part A (訊號 WR Sharpe cum) | Part B (訊號 WR Sharpe cum) | min(A,B) | 結論 |
|------|------|----------------------------|------------------------------|----------|------|
| Att1 | 0.99（TSLA 移植）| 18 / 66.7% / **0.44** / +63.30% | 5 / 80% / **0.82** / +26.34% | **0.44** | 部分成功（+7%）|
| Att2 | 0.97（NVDA 移植）| 19 / 68.4% / 0.48 / +76.36% | 6 / 66.7% / 0.41 / +17.31%（同 baseline）| **0.41** | 失敗（k 過寬）|
| Att3 ★ | 1.00（嚴格無緩衝）| 17 / 70.6% / **0.55** / +75.86% | 4 / 75% / **0.64** / +16.98% | **0.55** | **SUCCESS（+34%）**|

**進場條件（Att3 ★ 最終）：**

1. 過去 5 日內 BB Width 曾低於 60 日 30th 百分位（近期波動收縮）
2. 收盤價 > Upper BB(20, 2.0)（突破上軌）
3. 收盤價 > SMA(50)（短期趨勢向上）
4. **SMA(20) ≥ 1.00 × SMA(60)（嚴格 multi-week trend regime gate）**
5. 冷卻期 10 個交易日

**出場參數：** TP +8% / SL -7% / 持倉 20 天（同 FCX-004 Att2，已驗證為 FCX 突破甜蜜點）

**成交模型：** 隔日開盤市價進場，限價 TP，stop-market GTC SL，0.15% 滑價（高 vol 個股），悲觀認定（同根 K 線 stop+target 皆觸發 → 停損優先）

**核心跨資產發現（lesson #22 跨資產精煉）：**

trade-level signal-day SMA20/SMA60 ratio 分析揭示三資產的 transition zone 分布結構性差異：

| 資產 | 日波動 | Transition winners 集中區間 | 甜蜜點 k | 失敗模式 |
|------|--------|------------------------------|----------|----------|
| TSLA | 3.72% | ratio 0.99-1.00 | **0.99** | k=1.00 誤殺 winners + cooldown chain shift |
| NVDA | 2.5-3% | ratio 0.97-1.00 | **0.97** | k=0.99 誤殺 0.97-0.99 區間 winners |
| **FCX** | **~3%** | **ratio 0.93-0.97** + bull-regime 主導 | **1.00 嚴格** | k=0.99 仍過寬，0.97-1.00 區間僅有 SLs |

**關鍵差異**：FCX winners 集中於 ratio 0.93-0.97 + bull-regime（>1.0），**0.97-1.00 區間結構性無 winners**（僅 1 筆 ratio 1.013 略高於 1.00 自然保留）。因此 k=1.00 嚴格僅濾除該區間的 SLs（Part B 2025-08-26 ratio 0.972）而無 winner 代價。反觀 TSLA/NVDA 該區間有大量 winners，需 buffered k<1。

**Att1 vs Att3 對比：**
- Att1 k=0.99：Part B 大幅改善（0.41→0.82）但 Part A 退化（0.51→0.44）
- Att3 k=1.00：Part A 改善（0.51→0.55）+ Part B 改善（0.41→0.64），雙向改善

**A/B 平衡指標（Att3 ★ 最終）：**
- Part A 17 訊號（3.4/yr）vs Part B 4 訊號（2.0/yr），訊號比 1.7:1（gap 41.2% < 50% ✓，從 baseline 89.6% 大幅改善）
- Part A WR 70.6% vs Part B 75%（接近一致）
- Part A annualized cum 15.17%/yr vs Part B 8.49%/yr（gap 44.0%，從 baseline 59.3% 改善但仍超 30% 目標）
- A/B cum gap 為 FCX 結構性邊界——2020-2021 銅商品超級週期使 Part A 結構性高報酬

**跨資產貢獻：**

- **Repo 第 3 次 lesson #22 buffered multi-week SMA trend regime gate 試驗**（前 2 次：TSLA-015 高 beta 個股、NVDA-012 AI 牛市個股），**首次商品/礦業單股驗證**
- **跨資產反向發現**：FCX 上 k=1.00 嚴格優於 k<1 buffered，反轉 lesson #22 的「k<1 緩衝」原則
- **lesson #22 精煉新規則**：k 值取決於資產 winners 在 transition zone (0.93-1.00) 的分布密度——TSLA/NVDA winners 密集於 0.97-1.00 需 buffered k<1，FCX winners 集中 0.93-0.97 + bull-regime 主導使 k=1.00 嚴格成為甜蜜點
- **FCX 第 13 種策略類型 + 第 1 次 BB Squeeze 框架升級**：FCX-013 Att3 為 FCX BB Squeeze 框架的新最佳，與 FCX-001 MR 框架並列雙最優結構

**結論：FCX-013 Att3（k=1.00 嚴格）為 FCX 突破策略全域最佳，min(A,B) 0.55 vs FCX-004 的 0.41（+34%），同時大幅改善 A/B 平衡（訊號比 3.83:1 → 1.7:1）。**
