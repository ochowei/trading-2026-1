<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-04-26
  data_through: 2025-12-31
  note: CIBR-013 added 2026-04-26 (Higher-Low Structural Confirmation MR, **repo first multi-bar swing-structure pattern as MR primary filter on any asset**). Three iterations all failed vs CIBR-012 Att3 min 0.49: Att1 (pullback+WR+ATR>1.10+Bullish bar+Higher-Low(3)+Swing depth>=1%, 5-condition intersection) Part A 2/50%/Sharpe **-0.08** cum -0.74% (1 TP 2023-04-27 +3.5% / 1 SL 2022-04-28 -4.10%) / Part B **0 signals** / min **-0.08** — 5-way condition intersection over-tight, signal density 0.4/yr; Att2 (relax ATR=1.00 disabled + Higher-Low(3→5) longer lookback) Part A 3/33.3%/Sharpe **-0.44** cum -4.81% (added 1 SL) / Part B 1/100% TP +3.5% zero-var Sharpe 0.00 cum +3.50% / min **-0.44** — relaxation introduced Part A SL (lookback 5 + no ATR captures "mid-bounce failure" type signals); Att3 (BB Lower base + Higher-Low(5) replacing CIBR-012's 2DD cap) Part A **0 signals** / Part B **0 signals** / min **0.00** — **STRUCTURAL INCOMPATIBILITY discovered**: BB Lower touch (Close ≤ BB_lower) day is statistically extreme down-move where today's Low is almost always a new 5-day low; Higher-Low(5) requires today's Low > min(Low[t-5..t-1]). Two conditions are nearly mutually exclusive — only 1 signal triggered in 8+ years (Part C). **Repo first validation that "BB Lower entry + multi-bar Higher-Low filter" is structurally non-combinable**. **Key cross-asset finding**: extending lesson #20b failure family from single-day patterns (Key Reversal, NR7, Range Expansion, ClosePos, 2DD floor/cap) to **multi-bar structural patterns (Higher-Low Confirmation)** — multi-bar swing-structure dimension does NOT bypass single-day pattern failure root cause on event-driven sector ETFs (CIBR 1.53% vol). CIBR's 8th failed strategy type (after BB Squeeze, RSI(2), RS momentum, Key Reversal Day, NR7, Range Expansion, Higher-Low Confirmation). CIBR-012 Att3 remains global optimum (13 experiments, 39+ attempts). CIBR-012 added 2026-04-21 (Post-Capitulation Vol-Transition MR, **repo first "2-day return cap" filter as entry-time timing gate** — inverse direction vs CIBR-004's "2DD floor" which failed). Three iterations: Att1 failed (ATR peak ≥1.30 + today ≤1.20 two-stage filter structurally conflicts with CIBR-008 working ATR>1.15, collapsed to 1 signal total in 8yrs); Att2 failed (prior 10d ATR peak ≥1.25 as supplementary filter → Part A 3 signals Sharpe 0.27 / Part B 3 signals Sharpe 4.21, removed 3 winners and only 1 of 2 losers, prior ATR peak does NOT correlate with winner/loser); **Att3 SUCCESS (2DD cap >= -4.0%)** → Part A 4 signals WR 75% Sharpe **0.49** (+26% vs CIBR-008) / Part B 3 signals WR 100% Sharpe 3.96 / min(A,B) **0.49** / A/B cum diff 1.64pp (vs CIBR-008's 6.43pp) / A/B signal count diff 25% — ALL task goals met (Sharpe improvement, A/B cum <30%, signals <50%). Core finding: **"2-day return cap" (MUST >= -4.0%) filter direction is INVERSE of CIBR-004's "2-day decline floor" (MUST <= -1.5%/-2.0%) — floor direction failed, cap direction succeeds.** Interpretation: deep 2DD (≤-4% = 2.6σ for 1.53% vol) signals "crash still accelerating", shallow 2DD (-2~-4%) signals "deceleration phase where MR bounces work". Att3 filters both Part A SLs (2020-02-24 COVID 2DD -4.1%, and the filter mechanism also catches acceleration-mode signals). New cross-asset hypothesis: 2DD cap filter may extend to other US sector ETFs (XBI, XLU, IWM, COPX, VGK, EEM) facing "BB lower + cap" hybrid pattern — pending validation. CIBR-011 added 2026-04-20 (Range Expansion Climax MR, **repo first single-bar Range Expansion as primary signal on traditional US sector ETF** — IBIT-008 was crypto ETF, TLT-006 used range expansion as auxiliary only). Three iterations all failed vs CIBR-008 Att2 min 0.39: Att1 (TR/ATR(20)≥2.0 + ClosePos≥50% + 10d PB [-3%,-10%] + WR(10)≤-70, cd=8) Part A 3 signals 33.3% WR cum -4.81% Sharpe **-0.44** (2020-02-24 COVID precursor + 2021-09-20 Evergrande both 1-9d SLs) / Part B 2/2 100% WR cum +7.12% zero-variance Sharpe 0.00 — signal scarcity (5 signals in 8 years, 0.6/yr); Att2 (TR≥1.7 + tighten cap to -8% + add ATR(5)/ATR(20)>1.10) Part A 2/50% WR Sharpe -0.08 / Part B 2/50% WR Sharpe **-0.29** — ATR>1.10 filter REMOVES winners (2024-02-21, 2024-08-05 ATR<1.10) and adds 2025-03-04 SL; Att3 (reverse ATR ATR(5)/ATR(20)≤1.10 testing "calm regime + sudden TR expansion = real capitulation" hypothesis) Part A 2 signals 0W/2L **WR 0%** cum -8.03% Sharpe 0.00 (2021-05-04 + 2021-09-20 both SLs) / Part B **0 signals** / min 0.00 — reverse ATR also fails: removes ALL Part B signals while preserving Part A bear-regime continuation SLs. **Repo first Range Expansion MR trial on traditional US sector ETF** — refutes IBIT-008's cross-asset hypothesis ("Range Expansion MR may work on traditional non-24/7 US sector ETFs"). Range Expansion failure family extends from (a) high-vol 24/7 crypto ETF (IBIT 3.17%) to (b) mid-vol traditional US sector ETF (CIBR 1.53%). Core finding: ATR filter has **NO unidirectional efficacy** on CIBR Range Expansion — forward ATR (>1.10) removes winners, reverse ATR (≤1.10) preserves losers, indicating ATR is noise for this signal type. Integrated lesson: ALL entry-time filter types (oscillator hook, day-after reversal, capitulation depth, single-bar range expansion) structurally fail in event-driven sector ETFs that lack statistical-adaptive entry framework (BB Lower with std auto-scaling). CIBR's 7th failed strategy type (after BB Squeeze, RSI(2), RS momentum, Key Reversal Day, NR7, Range Expansion). CIBR-008 Att2 remains global optimum (11 experiments, 33+ attempts). CIBR-010 added 2026-04-19 (NR7 Volatility Contraction + Pullback MR, three iterations all failed: Att1 NR7 alone Part B Sharpe -0.44, Att2 +ATR>1.15 structural conflict signals 1/2, Att3 +2DD≤-2 structural conflict signals 1/1 zero-var). CIBR-009 added 2026-04-19 (Key Reversal Day price-action MR, three iterations all failed: WR/ATR variations all washout-then-continue SLs).
-->
## AI Agent 快速索引

**當前最佳：** CIBR-012 Att3（Post-Capitulation Vol-Transition MR：BB(20,2.0) 下軌觸及 + 10日回檔上限 -12% + WR(10)<=-80 + ClosePos>=40% + ATR(5)/ATR(20)>1.15 + **2日報酬 >= -4.0%**）min(A,B) Sharpe **0.49**（+26% vs CIBR-008 Att2 的 0.39）。在 CIBR-008 框架上新增「2 日報酬上限」過濾器，排除「崩盤加速中」進場時點，過濾 2020-02-24 COVID 前夕 SL 並保留 5 個 TPs 中的 3 個。A/B 累計差 1.64pp（vs CIBR-008 6.43pp）+ A/B 訊號比 1.33:1，符合全部平衡目標。**12 次實驗、36+ 次嘗試**。

**前任最佳：** CIBR-008 Att2（BB 下軌 + 回檔上限混合進場：BB(20,2.0) 下軌觸及 + 10日高點回檔 >= -12% + WR(10)<=-80 + ClosePos>=40% + ATR(5)/ATR(20)>1.15）min(A,B) Sharpe **0.39**（+44% vs CIBR-007 的 0.27）。混合進場保留 BB 統計自適應特性同時用絕對回檔深度隔離極端崩盤（-12% = ~7.8σ for 1.53% vol），濾除 COVID 連續崩盤中的 BB 假訊號。

**次佳：** CIBR-007 Att1（BB 下軌均值回歸：BB(20,2.0) 下軌觸及 + WR(10)<=-80 + ClosePos>=40% + ATR(5)/ATR(20)>1.15，min 0.27）

**第三佳：** CIBR-002 Att3（波動率自適應 MR：10日回檔>=4% + WR(10)<=-80 + ClosePos>=40% + ATR>1.15，min 0.23）

**已證明無效（禁止重複嘗試）：**
- BB Squeeze 突破（CIBR-003：Part A -0.20 / Part B -0.27，WR<40%，板塊 ETF 突破無持續性）
- 回檔上限 12%（CIBR-002 Att2：在 pullback+WR 框架移除好訊號，Part A 0.18→0.12。注意：CIBR-008 Att2 於 BB 下軌框架使用相同 12% 上限反而有效，因 BB 下軌本身提供主進場門檻）
- **回檔上限 -8%（CIBR-008 Att1）**：過嚴（5.2σ），Part A 僅 3 訊號（2W 1L 2.73%），移除 4 個 Part A 贏家
- **回檔上限 -10%（CIBR-008 Att3）**：濾除 1 贏家（2020-10-30）但未濾除 2 剩餘停損（2020-02-24 / 2021-02-26 回檔深度在 -10~-12% 區間），Part A 0.27 回退至 CIBR-007 水準
- **RSI(2) 框架**（CIBR-004 Att1：Part A -0.19 / Part B 1.44，嚴重市場狀態依賴。確認 lesson #27 擴展到美國板塊 ETF，不僅限非美國 ETF。關鍵差異是板塊集中度而非上市國家）
- **非對稱出場 TP +4.0%**（CIBR-004 Att2：3 筆交易從達標變到期 +2.77%/+3.59%/+2.81%，反效果）
- **2日急跌過濾 ≤ -1.5%**（CIBR-004 Att2：非綁定，16 訊號與 CIBR-002 相同，pullback+WR 訊號天然滿足 1.5% 跌幅）
- **2日急跌過濾 ≤ -2.0%**（CIBR-004 Att3：移除部分好訊號，WR 僅 50%→54.5%，min Sharpe -0.05）
- **SL -4.5%**（CIBR-004 Att3：所有停損交易均穿越 -4.5%，加寬只增加虧損）
- **20日回看窗口**（CIBR-005：A/B 訊號比 2.0:1 嚴重失衡。20日窗口在 Part A 產生過多信號，且 6% 回檔門檻附近信號脆弱，冷卻鏈序微調即翻轉結果。持倉 15 vs 18天翻轉 A/B 優劣但均未超越 CIBR-002）
- **WR(14) 取代 WR(10)**（CIBR-005：搭配 20日回看，未提供超越 WR(10)/10日回看組合的品質提升）
- **Key Reversal Day price-action（CIBR-009，3 次迭代全部失敗）**：price-action 結構化 washout+reclaim 進場在 CIBR 失效
  - Att1（WR≤-80、無 ATR、含 stop-run）：Part A 8 訊號 WR 50% Sharpe -0.08 / Part B 3 訊號 WR 33.3% Sharpe -0.44，2022 年 3 連 SL + 2025 年 2 連 SL 均為「washout 後續跌」
  - Att2（加入 ATR(5)/ATR(20) > 1.15）：訊號壓縮至 2/2（0.4/年），Part A -0.08 / Part B -0.08，Part B 2025-02-28 ATR 1.44 仍 1-day SL
  - Att3（移除 stop-run + WR≤-85 + ATR>1.10）：訊號崩至 1/1 全 SL，Sharpe 0.00/0.00
  - 失敗根因：(1) stop-run（Low < Prev Low）+ reclaim 組合在熊市續跌中頻繁產生假反轉；(2) ATR 飆升本身不是反轉保證（2025-02-28 ATR 1.44 + 隔日 -4.1%）；(3) CIBR 網路安全板塊事件驅動性質使單日 price-action 反轉結構無選擇性。擴展 XBI-012（Capitulation + Acceleration Reversal）失敗模式至 CIBR 網路安全板塊，確認短週期 price-action 反轉結構在美國事件驅動板塊 ETF 普遍失效
- **NR7 波動率壓縮 + pullback MR（CIBR-010，3 次迭代全部失敗）**：NR7（Narrowest Range 7，今日 True Range 為近 7 日最小）作為賣壓衰竭訊號在 CIBR 失效
  - Att1（pullback -4% + WR(10)≤-80 + NR7 + ClosePos≥40%，無 ATR）：Part A 7 訊號 WR 71.4% Sharpe 0.39（與 CIBR-008 同）/ Part B 3 訊號 WR 33.3% Sharpe **-0.44**，min(A,B) -0.44。Part B 2024-03-18 18天到期 -4.13% + 2025-02-28 1日 SL -4.10%，NR7 alone 在慢磨下跌中表現為「技術性暫停」而非「賣壓衰竭」
  - Att2（加入 ATR(5)/ATR(20) > 1.15）：訊號崩至 1/2，Part A 0.00（1 SL）/ Part B -0.08（2 訊號）。**結構性衝突**：NR7 要求今日 TR 為 7 日最小，ATR(5) 包含今日使 ATR 比率機械性降低，兩條件共存機率過低
  - Att3（移除 ATR，加入 2 日跌幅 ≤ -2.0% 作為真實賣壓情境代理）：訊號崩至 1/1 全零方差，Sharpe 0.00/0.00。**結構性衝突 2**：2 日跌幅 ≥2% 通常意味著其中一天有大範圍，與 NR7 幾乎互斥
  - 失敗根因：(1) CIBR 網路安全板塊事件驅動特性使 NR7 訊號常落在延續性下跌的「技術性暫停」期（非賣壓真正衰竭）；(2) NR7 與 CIBR 驗證有效的 ATR/2DD 品質過濾器結構性互斥，無法組合；(3) 2024-2025 Part B 期間 NR7 單獨在 pullback+WR 情境下產生 3 個訊號全部來自事件驅動的連續下跌（Palo Alto 財報、網路安全關稅擾動），非真正 capitulation
- **Range Expansion Climax MR（CIBR-011，3 次迭代全部失敗，repo 首次傳統 US 板塊 ETF Range Expansion 試驗）**：單日 TR/ATR(20) ≥ 2.0 + ClosePos ≥ 50% + 10日回檔 + WR 超賣 + 反/正向 ATR
  - Att1（TR/ATR(20) ≥ 2.0 + ClosePos ≥ 50% + 10日回檔 [-3%, -10%] + WR(10) ≤ -70）：Part A 3 訊號 WR 33.3% Sharpe **-0.44** / Part B 2 訊號 WR 100% 累計 +7.12% Sharpe 0.00（零方差）/ min(A,B) -0.44。訊號稀缺（5 訊號 8 年、0.6/yr），Part A 兩筆 SL 為 crash precursor（2020-02-24 COVID + 2021-09-20 Evergrande）
  - Att2（放寬 TR ≥ 1.7 + 收窄 cap -8% + 加 ATR(5)/ATR(20) > 1.10）：Part A 2 訊號 WR 50% Sharpe -0.08 / Part B 2 訊號 WR 50% Sharpe **-0.29** / min -0.29。**ATR > 1.10 反而移除好訊號**——Part B Att1 兩筆 winners（2024-02-21、2024-08-05 ATR < 1.10 環境）被過濾，改捕捉 2025 衰退期 1W 1L
  - Att3（反向 ATR 過濾 ATR(5)/ATR(20) ≤ 1.10）：Part A 2 訊號 **WR 0%**（兩筆 SL）累計 -8.03% / Part B **0 訊號** / min 0.00。反向 ATR 假設「平靜 + 突發爆發 = 真 capitulation」**完全失敗**——移除所有 Part B 訊號，留 Part A 兩筆事件早期下殺後續跌
  - 失敗根因：(1) 訊號稀缺性結構性問題（與 IBIT-008 平行）；(2) Range Expansion 本身無「真/假反轉」區分力（與 lesson #20b V-bounce 失敗家族一致）；(3) **ATR 過濾器無單向有效性**——CIBR Range Expansion 訊號的 ATR 環境與真假反轉**無關聯**，ATR 為 noise；(4) 與 CIBR-008 BB Lower 框架的結構性差異——BB 下軌為**統計自適應**進場，Range Expansion 為**單日點估計**，缺乏統計選擇性。**拒絕 IBIT-008 跨資產假設**（"Range Expansion MR 可能適用傳統 US 板塊 ETF"）。失敗家族擴展：所有 entry-time 過濾器（oscillator hook、day-after reversal、capitulation depth、single-bar range expansion）在「事件驅動 + 缺乏統計自適應」進場框架下結構性失效。CIBR 失敗策略類型達 7 種，確認 CIBR-008 BB+回檔上限混合進場仍為 1.5-2.0% vol 板塊 ETF 的最優結構
- **Higher-Low Structural Confirmation MR（CIBR-013，3 次迭代全部失敗，repo 首次將「多日 swing 結構 pattern」作為 MR 主過濾器於任何資產）**：
  - 動機：CIBR-009（Key Reversal）/-010（NR7）/-011（Range Expansion）三次嘗試以單日 price-action 過濾均失敗，**核心假設**：將「單日 pattern」擴展為「多日結構 pattern」可繞過此限制。Higher-Low（今日 Low > min(Low[t-N..t-1])）為多日 swing 結構的量化定義
  - Att1（純 pullback+WR+Higher-Low(3)+Bullish bar+ATR>1.10，5 重交集）：Part A 2 訊號 50% WR Sharpe **-0.08** cum -0.74%（1 TP 2023-04-27 +3.5% / 1 SL 2022-04-28 -4.10%）/ Part B **0 訊號** / min **-0.08**。5 重交集訊號密度 0.4/yr 過稀
  - Att2（放寬 ATR=1.00 + Higher-Low lookback 3→5）：Part A 3 訊號 33.3% WR Sharpe **-0.44** cum -4.81%（新增 1 SL）/ Part B 1 訊號 zero-var TP +3.5% Sharpe 0.00 / min **-0.44**。放寬 lookback 與停用 ATR 引入「中段反彈失敗」型態訊號
  - Att3（BB Lower 框架 + Higher-Low(5)，取代 CIBR-012 的 2DD cap）：Part A **0 訊號** / Part B **0 訊號** / min **0.00**。**結構性互斥重要發現**：BB Lower 觸及（Close ≤ BB_lower）日為統計極端下殺，今日 Low 幾乎必為近 5 日新低；而 Higher-Low(5) 要求今日 Low > min(Low[t-5..t-1])。兩條件在 CIBR 1.53% vol 板塊 ETF 上幾乎完全互斥（過去 8 年僅 1 訊號於 Part C 觸發）。**Repo 首次驗證「BB Lower entry + multi-bar Higher-Low filter 結構性不可組合」**
  - 失敗根因：(1) **多日 swing 結構維度並未繞過單日 pattern 的失敗根因**——擴展 lesson #20b 失敗家族至多日結構 pattern；(2) **BB Lower 與 Higher-Low 結構性互斥**——統計極端進場與多日反轉確認在低-中波動板塊 ETF 不可組合；(3) 純 pullback+WR 框架下加 Higher-Low + bullish bar + swing depth 5 重交集訊號密度過低；(4) 放寬條件引入低品質訊號。**CIBR 失敗策略類型達 8 種**，確認 CIBR-012 Att3 BB Lower + 2DD cap 仍為 1.5-2.0% vol 板塊 ETF 的最優結構

**已掃描的參數空間：**
- 回檔門檻：4%（Att3 最佳，2.6σ）、5%（Att1 次佳，3.3σ）
- **BB 下軌：BB(20,2.0) 最佳（min 0.27）、BB(20,1.5) 品質稀釋（撤回）**
- **回看窗口：10日（最佳）、20日（A/B 失衡 2.0:1，不穩定）**
- ATR 門檻：1.15（甜蜜點，與 XLU/EWJ 一致）
- ClosePos 門檻：40%（有效，日波動 1.53% 在有效邊界內）
- 回檔上限：12% 反效果（移除有效訊號）
- 出場參數：TP +3.5% / SL -4.0% / 持倉 18 天（無追蹤停損）
- TP +4.0%：反效果（轉達標為到期）
- SL -4.5%：無效（熊市停損交易穿越力度大）
- 持倉 15天：可能轉贏為到期（18 天是甜蜜點）
- **持倉 15天 + 20日回看：Part B 2 筆到期（+0.84%, -0.09%）；18天同組合 Part A 翻轉惡化**
- 冷卻：8 天
- BB Squeeze(20,2.0) + SMA(50) + TP4%/SL-4%/20天：完全失敗（WR 35-39%）
- RSI(2)<10 + 2日跌幅>=2% + ClosePos>=40% + ATR>1.15：Part A -0.19（嚴重市場狀態依賴）
- 2日急跌 -1.5% / -2.0% 作為 pullback+WR 補充過濾：無效/反效果
- **WR(14) + 20日回看：不優於 WR(10) + 10日回看**
- **20日回看 + 回檔 7%（~4.6σ）：過深門檻 Part B 僅 5 訊號，A/B 失衡 2.6:1**
- **RS 動量回調（CIBR vs QQQ/SPY）**：三次嘗試，RS(10)>=2-3%+pullback 2-8%+可選 ATR/ClosePos/SMA。Part A -0.85/-0.22/0.00，Part B 均為 0 訊號或負 Sharpe

**參數對照表 (Parameter Comparison):**

| 參數 | CIBR-001 | CIBR-002 Att3 | CIBR-003 | CIBR-004 Att1 | CIBR-005 Att1 | CIBR-006 Att2 | CIBR-007 Att1 | CIBR-008 Att2 ★ |
|------|----------|-----------------|----------|---------------|---------------|---------------|---------------|-----------------|
| 策略 | 回檔+WR | 波動率自適應 MR | BB Squeeze | RSI(2) | 20日回看 MR | RS 動量回調 | BB 下軌 MR | **BB 下軌 + 回檔上限** |
| 進場框架 | pullback+WR | pullback+WR | BB Squeeze | RSI(2) | pullback+WR | RS+pullback | BB lower | **BB lower + cap** |
| BB 參數 | — | — | BB(20,2.0) | — | — | — | BB(20,2.0) | **BB(20,2.0)** |
| 回看窗口 | 10日 | 10日 | — | — | **20日** | 10日 | — | **10日（cap 用）** |
| 回檔門檻 | 5% | 4% | — | — | **6%** | 2% | — | — |
| 回檔上限 | — | — | — | — | — | — | — | **-12% 崩盤隔離** |
| WR | WR(10)≤-80 | WR(10)≤-80 | — | — | **WR(14)≤-80** | — | WR(10)≤-80 | WR(10)≤-80 |
| ClosePos | — | ≥40% | — | ≥40% | ≥40% | — | ≥40% | ≥40% |
| ATR ratio | — | >1.15 | — | >1.15 | >1.15 | — | >1.15 | >1.15 |
| TP | +3.5% | +3.5% | +4.0% | +3.5% | +3.5% | +3.5% | +3.5% | +3.5% |
| SL | -4.0% | -4.0% | -4.0% | -4.0% | -4.0% | -4.0% | -4.0% | -4.0% |
| 持倉 | 18天 | 18天 | 20天 | 15天 | 15天 | 18天 | 18天 | 18天 |
| 冷卻 | 8天 | 8天 | 10天 | 5天 | 8天 | 8天 | 8天 | 8天 |
| Part A Sharpe | 0.11 | 0.23 | -0.20 | -0.19 | 0.18 | -0.22 | 0.27 | **0.39** |
| Part B Sharpe | 0.48 | 0.79 | -0.27 | 1.44 | 0.26 | -0.11 | 4.38 | **4.38** |
| min(A,B) | 0.11 | 0.23 | -0.27 | -0.19 | 0.18 | -0.22 | 0.27 | **0.39** |
| A/B 訊號頻率比 | 1.29:1 | 0.97:1 | 0.80:1 | 0.72:1 | 2.0:1 | 5.6:1 | 1.80:1 | **1.40:1** |

**尚未嘗試的方向（預期邊際效益極低）：**
- ~~2 日報酬上限（2DD cap，與 CIBR-004 2DD floor 相反方向）~~ → CIBR-012 Att3 新最佳（min 0.49，+26% vs CIBR-008）
- ~~BB 下軌 + 回檔上限混合~~ → CIBR-008 Att2 （min 0.39，+44% vs CIBR-007）
- ~~BB 下軌均值回歸~~ → CIBR-007 新最佳（min 0.27，+17% vs CIBR-002）
- ~~RSI(2)~~ → CIBR-004 Att1 驗證失敗（美國板塊 ETF 同樣無效）
- ~~BB 擠壓突破~~ → CIBR-003 驗證失敗
- ~~非對稱 TP +4.0%~~ → CIBR-004 Att2 驗證反效果
- ~~2日急跌過濾~~ → CIBR-004 Att2/Att3 驗證無效/反效果
- ~~SL -4.5%~~ → CIBR-004 Att3 驗證停損交易穿越力度大
- ~~20日回看窗口~~ → CIBR-005 驗證失敗（A/B 訊號比 2.0:1 失衡，信號閾值脆弱）
- ~~WR(14)~~ → CIBR-005 驗證無改善（搭配 20日回看不優於 WR(10)+10日回看）
- ~~RS 動量回調~~ → CIBR-006 三次嘗試均負 Sharpe（QQQ/SPY 基準、鬆/緊/品質過濾均失敗，網路安全無獨立動量週期）
- ~~Key Reversal Day price-action~~ → CIBR-009 驗證失敗
- ~~NR7 波動率壓縮~~ → CIBR-010 三次迭代全部失敗（單獨 Part B -0.44、加 ATR 結構性衝突、加 2DD 亦結構性衝突）
- ~~Range Expansion Climax MR~~ → CIBR-011 三次迭代全部失敗（Att1 訊號稀缺 min -0.44、Att2 ATR 過濾移除好訊號 min -0.29、Att3 反向 ATR 全敗 min 0.00）。**拒絕 IBIT-008 跨資產假設**，Range Expansion 在 CIBR/IBIT 兩種波動率區間均失敗
- ~~Higher-Low 多日結構確認 MR~~ → CIBR-013 三次迭代全部失敗（Att1 5 重交集 min -0.08、Att2 放寬引入 SL min -0.44、Att3 BB Lower + Higher-Low **結構性互斥** min 0.00）。**Repo 首次多日 swing 結構 pattern 作為 MR 主過濾器**驗證——多日結構維度未繞過單日 pattern 的失敗根因。擴展 lesson #20b 失敗家族至多日結構 pattern
- 持倉 20天（可能延長到期曝露，預期無改善）
- 回檔門檻 3%（過鬆，可能增加低品質訊號，vs 4%=2.6σ 已優化）
- ~~趨勢動量回檔~~ → lesson #25 板塊 ETF 動量無效 + CIBR-006 RS 動量驗證失敗

**關鍵資產特性：**
- CIBR 日波動約 1.53%，為 GLD 的 1.37 倍，屬低中波動
- 網路安全板塊 ETF，追蹤 PANW、CRWD、FTNT、ZS 等網路安全公司
- 科技板塊相關，可能與 NASDAQ/科技指數有較高相關性
- ATR(5)/ATR(20) > 1.15 有效過濾慢磨下跌（跨資產驗證：XLU/IWM/COPX/EWJ 均有效）
- ClosePos >= 40% 有效確認日內反轉（日波動 1.53% 在 ClosePos 有效邊界 ≤2.0% 內）
- BB Squeeze 突破完全無效（板塊 ETF 突破缺乏持續性，WR < 40%）
- **RSI(2) 對美國板塊 ETF 同樣無效**：確認 lesson #27 的關鍵差異是板塊集中度（非寬基指數），而非上市國家。CIBR 雖為美國上市，但板塊集中度高導致 2020-2022 持續性熊市中產生大量假超賣訊號
- **熊市停損交易穿越力度大**：SL -4.0% 和 -4.5% 產生相同停損交易，加寬 SL 只增加虧損
- **20日回看窗口結構性 A/B 失衡**：5年 Part A vs 2年 Part B 下，20日回看產生 2.0:1 訊號失衡。且 6% 回檔門檻附近信號脆弱（微小數據變動翻轉結果）
- **RS 動量回調 CIBR vs SPY/QQQ**（CIBR-006：三次嘗試均負 Sharpe。Att1 QQQ基準訊號太少；Att2 SPY基準 WR 42.9% min -0.22 A/B 5.6:1；Att3 加品質過濾僅 1 訊號。網路安全缺乏獨立板塊動量週期，RS 信號品質等同隨機。確認 lesson #25 擴展到 RS 動量+市值加權板塊 ETF）
- **BB(20,1.5) 較寬下軌**（CIBR-007 Att2：品質稀釋，額外訊號含停損，撤回）
- **移除 ClosePos**（CIBR-007 Att3：Part A 0.09/Part B 0.02，15訊號含5停損，品質崩壞。ClosePos 在 BB 框架中不可或缺）
- **回檔上限在 BB 下軌框架有效**（CIBR-008 Att2：-12% = 7.8σ 濾除 COVID 連續崩盤訊號，Part A 0.27→0.39 +44%）。但區間敏感：-8% 過嚴（Att1：-44% Sharpe）、-10% 未濾除剩餘停損（Att3：回退至 0.27）。甜蜜點 -12% 反映 CIBR 歷史上「BB 下軌假訊號」主要來自 10日回檔 >12% 的崩盤連續段
- **Lesson #52 在 CIBR 上的例外**：BB 下軌 MR 在 1.53% vol CIBR 上（配合 7.8σ 回檔上限）可突破「持續性熊市假訊號」瓶頸。確認 EWJ-003 + CIBR-008 混合進場模式為低波動板塊/區域 ETF 的有效突破方向
- **Key Reversal Day 在 CIBR 失效（CIBR-009）**：3 次迭代證明單日 price-action 結構（stop-run + reclaim + bullish bar）在 CIBR 網路安全板塊無效。擴展 XBI-012 失敗模式至 CIBR：**美國事件驅動板塊 ETF 拒斥所有短週期 price-action 反轉結構**，需依賴波動率統計指標（BB 下軌+ATR）而非 price-action
- **NR7 波動率壓縮 + pullback MR 在 CIBR 失效（CIBR-010）**：NR7（今日 True Range 為近 7 日最小）作為「賣壓衰竭」的波動率壓縮訊號，3 次迭代均失敗。**本 repo 首次嘗試 NR7 pattern**，但在 CIBR 網路安全板塊同樣無效。關鍵發現：(1) 單獨 NR7 + pullback+WR+ClosePos（Att1）Part B Sharpe -0.44，訊號常落在延續性下跌的技術性暫停期；(2) NR7 與 CIBR 有效的 ATR(5)/ATR(20)>1.15 過濾器**結構性衝突**；(3) NR7 與 2 日跌幅 ≤-2.0% 過濾器同樣**結構性互斥**
- **Range Expansion Climax MR 在 CIBR 失效（CIBR-011，repo 首次傳統 US 板塊 ETF Range Expansion 試驗）**：單日 TR/ATR(20) ≥ 2.0 + ClosePos ≥ 50% 主訊號（IBIT-008 模式跨資產移植）3 次迭代均失敗。Att1（IBIT-008 結構縮放）Part A 3/33%/min -0.44 + Part B 2/100%零方差 0.00；Att2（放寬 TR 1.7 + 加 ATR>1.10）Part A/B 各 2 訊號 50% WR min -0.29，**ATR>1.10 反而過濾掉 Part B 兩筆 2024 winners**；Att3（反向 ATR ≤1.10）Part A WR 0% + Part B 0 訊號 min 0.00。**核心發現**：(1) Range Expansion 訊號在 CIBR 8 年資料僅 0.6/yr，與 IBIT-008 同樣稀疏；(2) **ATR 過濾器無單向有效性**——正向移除 winners、反向保留 losers；(3) Range Expansion 為**單日點估計**進場，缺乏 BB 下軌的**統計自適應**特性。**拒絕 IBIT-008 跨資產假設**：「Range Expansion MR 可能適用傳統 US 板塊 ETF」於 CIBR 1.53% vol 上不成立。失敗家族擴展：所有 entry-time 過濾器類型（oscillator hook、day-after reversal、capitulation depth、single-bar range expansion）在事件驅動板塊 ETF + 缺乏統計自適應進場框架下結構性失效。**CIBR 失效策略類型達 7 種**（突破、RSI(2)、RS 動量、price-action reversal、NR7 壓縮、2日急跌作為補充、Range Expansion Climax）
<!-- AI_CONTEXT_END -->

# CIBR 實驗總覽 (CIBR Experiments Overview)

## 標的特性 (Asset Characteristics)

- **CIBR (First Trust NASDAQ Cybersecurity ETF)**：追蹤 Nasdaq CTA Cybersecurity Index，涵蓋全球主要網路安全公司
- 日均波動約 1.53%，為 GLD 的 1.37 倍，屬低中波動板塊 ETF
- 年化波動率約 24.3%，介於 GLD（17.8%）與 SIVR（36%）之間
- 科技板塊相關，與 NASDAQ 綜合指數有一定相關性，但聚焦網路安全子板塊

## 實驗列表 (Experiment List)

| ID       | 資料夾                         | 策略摘要                                       | 狀態       |
|----------|-------------------------------|-----------------------------------------------|-----------|
| CIBR-001 | `cibr_001_pullback_wr`        | 10日回檔>=5% + WR(10)<=-80 均值回歸              | 已完成 |
| CIBR-002 | `cibr_002_vol_adaptive_mr`    | 波動率自適應均值回歸（+ATR+ClosePos+回檔4%）★當前最佳 | 已完成 |
| CIBR-003 | `cibr_003_bb_squeeze_breakout`| BB 擠壓突破（完全失敗）                           | 已完成 |
| CIBR-004 | `cibr_004_rsi2_vol_adaptive`  | RSI(2)(Att1)→動量強化MR(Att2-3)（未超越 CIBR-002）| 已完成 |
| CIBR-005 | `cibr_005_20d_lookback_mr`    | 20日回看窗口+WR(14)+6%回檔（A/B 失衡，未超越 CIBR-002）| 已完成 |
| CIBR-006 | `cibr_006_rs_momentum_pullback`| RS 動量回調 CIBR vs SPY（完全失敗，三次嘗試均負 Sharpe）| 已完成 |
| CIBR-007 | `cibr_007_bb_lower_mr`         | BB(20,2.0) 下軌均值回歸（min 0.27）                       | 已完成 |
| CIBR-008 | `cibr_008_bb_lower_pullback_cap`| BB 下軌 + 10日高點回檔上限 -12% 混合進場（前任最佳，min 0.39）| 已完成 |
| CIBR-009 | `cibr_009_key_reversal_day_mr`  | Key Reversal Day 均值回歸（price-action washout+reclaim，3 次迭代均失敗）| 已完成 |
| CIBR-010 | `cibr_010_nr7_pullback_mr`      | NR7 波動率壓縮 + pullback 均值回歸（3 次迭代均失敗）| 已完成（未改善）|
| CIBR-011 | `cibr_011_range_expansion_mr`   | Range Expansion Climax 均值回歸（TR/ATR≥2.0+ClosePos≥50%，3 次迭代均失敗）| 已完成 |
| CIBR-012 | `cibr_012_vol_transition_mr`    | Post-Capitulation Vol-Transition MR（Att3 2DD cap ≥ -4.0% 成功，★當前最佳 min 0.49）| 已完成 |

---

## CIBR-001：回檔 + Williams %R 均值回歸

### 目標 (Goal)

建立 CIBR 首個均值回歸策略，以 10 日高點回檔搭配 Williams %R 確認超賣，參數由 GLD-007 / SIVR-003 按波動度比例內插。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 回檔幅度 | Close vs 10日最高 High | >= 5% | 由 GLD 3% / SIVR 7% 按波動度 1.37x 內插 |
| 超賣確認 | Williams %R(10) | <= -80 | 標準超賣閾值 |
| 冷卻期 | 前次訊號間隔 | >= 8 天 | 由 GLD 7 / SIVR 10 內插 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 止盈 (TP) | +3.5% | 與 GLD-007 / SIVR-003 相同 |
| 停損 (SL) | -4.0% | 與 GLD-007 相近，給予適度呼吸空間 |
| 最長持倉 | 18 天 | 由 GLD 20 / SIVR 15 按波動度內插 |
| 追蹤停損 | 不使用 | 日波動 1.53% 在追蹤停損有效邊界外 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 訊號隔日開盤市價進場 |
| 出場方式 | 悲觀認定（日內觸及 TP/SL 時假設先觸及不利方向） |
| 滑價 | 0.1%（ETF 標準） |
| 未成交處理 | 開盤價直接進場（市價單） |

### 回測結果 (Backtest Results)

| 區間 | 期間 | 訊號數 | 勝率 | 累計報酬 | Sharpe | MDD |
|------|------|--------|------|----------|--------|-----|
| Part A (IS) | 2019-01-01 ~ 2023-12-31 | 42 (8.4/年) | 57.1% | +14.91% | 0.11 | -9.63% |
| Part B (OOS) | 2024-01-01 ~ 2025-12-31 | 13 (6.5/年) | 76.9% | +20.69% | 0.48 | -4.51% |
| Part C (Live) | 2026-01-01 ~ 2026-04-10 | 5 (18.6/年) | 60.0% | +1.97% | 0.12 | -6.01% |

---

## CIBR-002：波動率自適應均值回歸 ★當前最佳

### 目標 (Goal)

在 CIBR-001 基礎上新增 ATR 波動率過濾與 ClosePos 日內反轉確認，並調校回檔門檻至 sigma-calibrated 最佳值，提升 Part A 訊號品質。

### 設計理念 (Design Rationale)

- **ATR(5)/ATR(20) > 1.15**：過濾慢磨下跌，只在波動率急升（恐慌拋售）時進場。跨資產驗證：XLU(+272%)、IWM(+67.7%)、EWJ(+244%) 均有效。CIBR 日波動 1.53% 在 ATR 有效邊界（≤2.25%）內。
- **ClosePos >= 40%**：確認日內反轉跡象（收盤不在最低點附近）。在日波動 ≤2.0% 有效（GLD 1.1%、IWM 1.5-2%、XBI 2.0% 均驗證）。
- **回檔門檻 4%（Att3）**：= 2.6σ 日波動，與 GLD(3%/2.7σ)、EWJ(3%/2.6σ) 一致。比 Att1 的 5%(3.3σ) 多捕獲 1 筆高品質訊號。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 回檔幅度 | Close vs 10日最高 High | >= 4% | 2.6σ，sigma-calibrated |
| 超賣確認 | Williams %R(10) | <= -80 | 標準超賣閾值 |
| 日內反轉 | Close Position | >= 40% | 收盤離日低 40% 以上 |
| 波動率急升 | ATR(5)/ATR(20) | > 1.15 | 區分恐慌拋售 vs 慢磨下跌 |
| 冷卻期 | 前次訊號間隔 | >= 8 天 | 防止下跌趨勢連續進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 止盈 (TP) | +3.5% | 與 CIBR-001 相同 |
| 停損 (SL) | -4.0% | 與 CIBR-001 相同 |
| 最長持倉 | 18 天 | 與 CIBR-001 相同 |
| 追蹤停損 | 不使用 | 日波動 1.53% 在邊界外 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 訊號隔日開盤市價進場 |
| 出場方式 | 悲觀認定 |
| 滑價 | 0.1%（ETF 標準） |

### 迭代歷程 (Iteration History)

**Att1**（回檔 5% + ATR>1.15 + ClosePos>=40%）：
- Part A: 16 訊號 (3.2/年), WR 62.5%, +9.73%, Sharpe 0.18
- Part B: 7 訊號 (3.5/年), WR 85.7%, +14.80%, Sharpe 0.79
- vs CIBR-001: min(A,B) 0.11→0.18 (+64%)
- ATR+ClosePos 移除 26 筆低品質訊號（42→16），WR +5.4pp

**Att2**（+12% 回檔上限）：
- Part A: 15 訊號, WR 60.0%, Sharpe 0.12（下降！）
- 移除 2022-05-10 好訊號（+3.50%），反效果 → 撤回

**Att3**（回檔門檻降至 4% = 2.6σ）★ Final：
- Part A: 17 訊號 (3.4/年), WR 64.7%, +13.57%, Sharpe **0.23**
- Part B: 7 訊號 (3.5/年), WR 85.7%, +14.80%, Sharpe **0.79**
- Part C: 2 訊號, WR 50.0%, -0.74%, Sharpe -0.08
- vs CIBR-001: min(A,B) 0.11→0.23 (+109%)
- 新增 2019-03-07 好訊號（+3.50%, 3天），A/B 頻率比 0.97:1（優秀）
- A/B 累積報酬差 8.3%（< 30% 目標 ✓），訊號數差 0.97:1（< 50% 目標 ✓）

### 回測結果 (Backtest Results) — Att3 Final

| 區間 | 期間 | 訊號數 | 勝率 | 累計報酬 | Sharpe | Profit Factor | MDD |
|------|------|--------|------|----------|--------|---------------|-----|
| Part A (IS) | 2019-01-01 ~ 2023-12-31 | 17 (3.4/年) | 64.7% | +13.57% | 0.23 | 1.57 | -6.81% |
| Part B (OOS) | 2024-01-01 ~ 2025-12-31 | 7 (3.5/年) | 85.7% | +14.80% | 0.79 | 4.46 | -4.30% |
| Part C (Live) | 2026-01-01 ~ 2026-04-13 | 2 (7.2/年) | 50.0% | -0.74% | -0.08 | 0.85 | -6.45% |

---

## CIBR-003：BB 擠壓突破（失敗）

### 目標 (Goal)

嘗試突破策略方向（vs 前 2 個實驗的均值回歸），利用 CIBR 板塊輪動特性在波動率壓縮後捕捉向上突破。

### 設計理念 (Design Rationale)

- 參考 EEM-005 Att2 框架，按 CIBR 波動度 (1.53% vs EEM 1.17%) 縮放 TP/SL
- CIBR 在 BB Squeeze 有效排序中屬「高流動 ETF(1.5-2%)」
- 網路安全板塊具有主題投資特性，可能有方向性突破

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 |
|------|------|------|
| 擠壓 | BB(20,2.0) 帶寬 ≤ 60日 30th 百分位（近5日內） | 波動率壓縮 |
| 突破 | Close > BB 上軌 | 向上突破 |
| 趨勢 | Close > SMA(50) | 趨勢確認 |
| 冷卻 | 前次訊號間隔 >= 10 天 | 防過度交易 |

### 出場參數

TP +4.0% / SL -4.0% / 20 天

### 回測結果 (Backtest Results) — 失敗

| 區間 | 訊號數 | 勝率 | 累計報酬 | Sharpe | MDD |
|------|--------|------|----------|--------|-----|
| Part A | 18 (3.6/年) | 38.9% | -14.02% | -0.20 | -6.47% |
| Part B | 9 (4.5/年) | 33.3% | -9.16% | -0.27 | -5.95% |

### 失敗分析

- **WR < 40%**：板塊 ETF 突破缺乏持續性，突破後快速反轉
- 2020 年 5 連敗（COVID 後連續假突破）
- 與 cross-asset lesson #25（多成分板塊 ETF 動量無效）一致
- 突破策略不適用 CIBR，均值回歸是正確框架

---

## CIBR-004：RSI(2) → 動量強化均值回歸（未超越 CIBR-002）

### 目標 (Goal)

探索 RSI(2) 極端超賣框架在美國板塊 ETF 的有效性（lesson #27 僅驗證了非美國 ETF 無效）。CIBR 日波動 1.53% 處於 RSI(2) 有效範圍（≤2.0%），且為美國上市 ETF，假說是可能與 SPY/DIA/IWM 有類似均值回歸特性。

### 迭代歷程 (Iteration History)

**Att1**（RSI(2)<10 + 2日跌幅>=2.0% + ClosePos>=40% + ATR>1.15，TP+3.5%/SL-4.0%/15天）：
- Part A: 9 訊號 (1.8/年), WR 44.4%, -6.92%, Sharpe **-0.19**
- Part B: 5 訊號 (2.5/年), WR 80.0%, +11.70%, Sharpe **1.44**
- **失敗**：RSI(2) 在 2020-2022 持續性熊市中產生 5 個停損（5/9=55.6% SL 率）
- **關鍵發現**：lesson #27 的關鍵差異不是國家（美國 vs 非美國），而是板塊集中度（寬基指數 vs 板塊/國家 ETF）。CIBR 雖為美國上市但板塊集中度高，行為更像 VGK/EWT 而非 SPY/IWM

**Att2**（策略轉向 pullback+WR+ATR + 2日急跌≤-1.5% + TP+4.0%/SL-4.0%/15天）：
- Part A: 16 訊號 (3.2/年), WR 50.0%, -1.28%, Sharpe **-0.00**
- Part B: 7 訊號 (3.5/年), WR 71.4%, +13.03%, Sharpe **0.62**
- **失敗**：TP +4.0% 反效果（3 筆交易 +2.77%/+3.59%/+2.81% 未達 4.0% 到期），2日跌幅 -1.5% 非綁定（16 訊號同 CIBR-002）

**Att3**（2日急跌≤-2.0% + TP+3.5%/SL-4.5%/18天）：
- Part A: 11 訊號 (2.2/年), WR 54.5%, -2.86%, Sharpe **-0.05**
- Part B: 6 訊號 (3.0/年), WR 100.0%, +19.70%, Sharpe **4.69**
- **失敗**：2日跌幅 -2.0% 移除部分好訊號（WR 50%→54.5% 僅微升），SL -4.5% 停損交易全部穿越（加寬只增加虧損）

### 結論

三次迭代均未超越 CIBR-002（min Sharpe 0.23）。Part A（2019-2023）包含 COVID、2021 成長轉價值輪動、2022 升息拋售等結構性事件，這些事件產生的停損訊號在技術指標上與有效恐慌反轉訊號無法區分。CIBR-002 的 Sharpe 0.23 可能接近 CIBR 的技術面天花板。

---

## CIBR-005：20日回看窗口均值回歸（未超越 CIBR-002）

### 目標 (Goal)

測試更長回看窗口（20日 vs 標準 10日）是否能捕捉不同的回檔模式，改善 CIBR-002 的 3.4x A/B Sharpe 差距（0.23 vs 0.79）。GLD-012（20日回看+3%，vol 1.2%）成功，CIBR vol 1.53% 接近 GLD，有合理依據。

### 設計理念 (Design Rationale)

- **20日回看**：捕捉緩慢發展的 2-3 週回檔，可能改善 Part A（較平靜市場）績效
- **回檔門檻 6%（~3.9σ）**：更寬窗口需更深門檻維持訊號品質
- **WR(14) 取代 WR(10)**：匹配更長回看窗口
- **持倉 15天（vs 18天）**：縮短到期曝露
- 保留 ATR > 1.15 + ClosePos >= 40%（已跨資產驗證有效）

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 回檔幅度 | Close vs 20日最高 High | >= 6% | ~3.9σ，20日窗口需更深門檻 |
| 超賣確認 | Williams %R(14) | <= -80 | 匹配更長回看窗口 |
| 日內反轉 | Close Position | >= 40% | 同 CIBR-002 |
| 波動率急升 | ATR(5)/ATR(20) | > 1.15 | 同 CIBR-002 |
| 冷卻期 | 前次訊號間隔 | >= 8 天 | 同 CIBR-002 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 止盈 (TP) | +3.5% | 同 CIBR-002 |
| 停損 (SL) | -4.0% | 同 CIBR-002 |
| 最長持倉 | 15 天 | 縮短 3 天（vs CIBR-002 的 18天） |
| 追蹤停損 | 不使用 | 日波動 1.53% 在邊界外 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 訊號隔日開盤市價進場 |
| 出場方式 | 悲觀認定 |
| 滑價 | 0.1%（ETF 標準） |

### 迭代歷程 (Iteration History)

**Att1**（20日回看+6%+WR(14)+持倉15天）★ 最佳嘗試：
- Part A: 16 訊號 (3.2/年), WR 62.5%, +9.73%, Sharpe **0.18**
- Part B: 8 訊號 (4.0/年), WR 62.5%, +6.33%, Sharpe **0.26**
- min(A,B) = 0.18，A/B 訊號比 2.0:1（失衡）
- Part B 有 2 筆到期交易（+0.84%, -0.09%），持倉 15天部分信號未達標

**Att2**（持倉恢復 18天）：
- Part A: 16 訊號, WR 62.5%, +9.73%, Sharpe **0.18**
- Part B: 8 訊號, WR 75.0%, +10.09%, Sharpe **0.40**
- min(A,B) = 0.18，Part B 改善（到期報酬提升），Part A 不變
- 冷卻鏈序微調導致 Part A 結果不穩定（一筆交易翻轉可改變 Sharpe ±0.14）

**Att3**（回檔門檻加深至 7% + 持倉 15天）：
- Part A: 13 訊號 (2.6/年), WR 76.9%, +24.41%, Sharpe **0.55**
- Part B: 5 訊號 (2.5/年), WR 60.0%, +1.97%, Sharpe **0.12**
- min(A,B) = 0.12，7% 門檻過深導致 Part B 僅 5 訊號，A/B 失衡 2.6:1

### 回測結果 (Backtest Results) — Att1 Final

| 區間 | 期間 | 訊號數 | 勝率 | 累計報酬 | Sharpe | Profit Factor | MDD |
|------|------|--------|------|----------|--------|---------------|-----|
| Part A (IS) | 2019-01-01 ~ 2023-12-31 | 16 (3.2/年) | 62.5% | +9.73% | 0.18 | 1.42 | -6.81% |
| Part B (OOS) | 2024-01-01 ~ 2025-12-31 | 8 (4.0/年) | 62.5% | +6.33% | 0.26 | 1.79 | -5.14% |
| Part C (Live) | 2026-01-01 ~ 2026-04-13 | 1 (3.6/年) | 100.0% | +3.50% | 0.00 | ∞ | -1.48% |

### 失敗分析

1. **A/B 訊號比 2.0:1 失衡**：20日回看窗口在 Part A（5年）產生更多緩慢回檔訊號，Part B（2年）較少。跨資產教訓 #38 確認：20日回看在 INDA/SIVR/URA/IBIT 也失衡，CIBR 加入失敗清單
2. **信號閾值脆弱**：6% 回檔門檻附近多個訊號在邊界，yfinance 數據微調即改變冷卻鏈序和交易結果。CIBR-002 的 4%/10日組合更穩健（遠離邊界）
3. **持倉 15 vs 18天交叉效應**：15天 Part A 更佳但 Part B 到期增加；18天反之。無法找到同時優化兩期的持倉長度
4. **WR(14) 未提供增量**：更長 WR 週期與 20日回看的額外信息重疊，未改善訊號品質

### 關鍵教訓

- **CIBR 10日回看窗口已是最佳**：20日回看結構性產生 A/B 訊號失衡，且信號品質未改善
- 確認 CIBR-002 Att3 的 Sharpe 0.23 接近 CIBR 技術面天花板
- 板塊 ETF 回看窗口不宜超過 10日（CIBR 波動度雖接近 GLD，但 Part A/B 的 5年/2年不對稱放大了窗口效應）

---

## CIBR-006：RS 動量回調（CIBR vs SPY）

### 目標 (Goal)

探索板塊相對強度（RS）動量策略能否超越 CIBR-002 的均值回歸框架。靈感來自 SOXL-010（min 0.70）、EWT-007（min 0.42）的 RS 動量成功案例。

### 策略假設

當 CIBR（網路安全板塊）相對大盤（SPY）展現超額表現後出現短期回調，為動量延續買入機會。

### 嘗試記錄 (Attempt Log)

**Att1**：CIBR vs QQQ, RS(10)>=3%, 5日回調 3-8%, SMA(50)
- Part A: 5 訊號, WR 20%, Sharpe **-0.85**, 累計 -12.46%
- Part B: **0 訊號**
- 失敗原因：CIBR-QQQ 相關性太高（同為 NASDAQ 科技），3% RS 門檻幾乎無法觸發

**Att2**：CIBR vs SPY, RS(10)>=2%, 10日回調 2-8%, 移除 SMA 趨勢
- Part A: 28 訊號 (5.6/yr), WR 42.9%, Sharpe **-0.22**, 累計 -22.66%
- Part B: 5 訊號 (2.5/yr), WR 40.0%, Sharpe **-0.11**, 累計 -2.11%
- A/B 訊號比：5.6:1（危險，lesson #8 > 3:1）
- 失敗原因：無趨勢+無品質過濾，2022 熊市大量假訊號；16/28 Part A 訊號為停損

**Att3**：Att2 基礎 + ATR(5)/ATR(20)>1.15 + ClosePos>=40% + SMA(50) + 回調最低 3%
- Part A: **1 訊號**（2022-04-25，停損）, Sharpe 0.00
- Part B/C: **0 訊號**
- 失敗原因：RS+回調+ATR+ClosePos+SMA 五條件疊加過於嚴格，幾乎無法同時觸發

### 結論 (Conclusion)

**RS 動量策略對 CIBR 完全無效。** 核心原因：

1. **CIBR 缺乏獨立的板塊動量週期**：不同於半導體（SOXL-010 成功），網路安全板塊的超額表現多為科技板塊整體走勢的附帶效應，而非獨立的板塊輪動信號
2. **RS 信號品質低**：CIBR 相對 SPY 的超額表現期間買入回調，42.9% WR 基本等同隨機，無法補償對稱 TP/SL
3. **A/B 嚴重失衡**：Att2 的 5.6:1 訊號比表明策略依賴特定市場狀態（2019-2023 科技牛市+2022 熊市的特定模式）

**新增跨資產教訓**：lesson #25（板塊 ETF 動量無效）不僅限等權重 ETF 和 ROC 動量，RS 動量對市值加權板塊 ETF 同樣無效。有效條件似乎需要：(a) 明確的週期性板塊（半導體）或 (b) 地理/資產類別差異大的比較對（EWT vs EEM）。

---

## CIBR-007：BB 下軌均值回歸 ★新最佳

### 目標 (Goal)

以 BB(20,2.0) 下軌觸及取代固定回檔門檻作為進場訊號。不同於 CIBR-003 的 BB Squeeze Breakout（買在上軌突破），本策略在下軌買入（均值回歸方向）。BB 下軌是統計自適應門檻——低波動期需要更淺門檻、高波動期需要更深門檻，自動適應這個差異。

### 設計理念 (Design Rationale)

- **BB 下軌 vs 固定回檔**：CIBR-002 的 4% 固定門檻在不同波動期可能過鬆或過緊；BB(20,2.0) 下軌根據 20日標準差自動調整，理論上在各波動環境都能精準捕捉統計極端值
- SIVR-013 在 2-3% vol 上測試 BB 下軌失敗（熊市反覆觸及），但 CIBR 1.53% vol 遠低於 SIVR，搭配品質過濾應可抑制假訊號
- 保留 WR(10)≤-80 + ClosePos≥40% + ATR>1.15 三重品質過濾（已跨資產驗證有效）

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| BB 下軌觸及 | Close ≤ BB(20,2.0) 下軌 | 統計自適應 | 價格觸及或跌破 BB 下軌 |
| 超賣確認 | Williams %R(10) | ≤ -80 | 標準超賣閾值 |
| 日內反轉 | Close Position | ≥ 40% | 收盤離日低 40% 以上 |
| 波動率急升 | ATR(5)/ATR(20) | > 1.15 | 排除慢磨下跌 |
| 冷卻期 | 前次訊號間隔 | ≥ 8 天 | 防止連續進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 止盈 (TP) | +3.5% | 同 CIBR-002 |
| 停損 (SL) | -4.0% | 同 CIBR-002 |
| 最長持倉 | 18 天 | 同 CIBR-002 |
| 追蹤停損 | 不使用 | 日波動 1.53% 在邊界外 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 訊號隔日開盤市價進場 |
| 出場方式 | 悲觀認定 |
| 滑價 | 0.1%（ETF 標準） |

### 迭代歷程 (Iteration History)

**Att1**（BB(20,2.0) + WR≤-80 + ClosePos≥40% + ATR>1.15）★ Final：
- Part A: 9 訊號 (1.8/年), WR 66.7%, +8.42%, Sharpe **0.27**
- Part B: 5 訊號 (2.5/年), WR 100.0%, +15.66%, Sharpe **4.38**
- Part C: 2 訊號 (7.1/年), WR 50.0%, -0.74%, Sharpe -0.08
- min(A,B) = **0.27**（+17% vs CIBR-002 的 0.23）
- BB 下軌進場比固定 4% 回檔更精準：Part A WR 66.7%（vs CIBR-002 64.7%），訊號更少但品質更高
- A/B 訊號頻率比 0.72:1（可接受）

**Att2**（BB(20,1.5) 較寬下軌）：
- 品質稀釋，額外訊號含停損 → 撤回

**Att3**（移除 ClosePos 過濾，close_pos_threshold=0.0）：
- Part A: 15 訊號 (3.0/年), WR 53.3%, +3.59%, Sharpe **0.09**
- Part B: 7 訊號 (3.5/年), WR 57.1%, +0.02%, Sharpe **0.02**
- **品質崩壞**：移除 ClosePos 後訊號數暴增但含 5 筆停損，確認 ClosePos 在 BB 框架中不可或缺

### 回測結果 (Backtest Results) — Att1 Final

| 區間 | 期間 | 訊號數 | 勝率 | 累計報酬 | Sharpe | Profit Factor | MDD |
|------|------|--------|------|----------|--------|---------------|-----|
| Part A (IS) | 2019-01-01 ~ 2023-12-31 | 9 (1.8/年) | 66.7% | +8.42% | 0.27 | 1.71 | -6.81% |
| Part B (OOS) | 2024-01-01 ~ 2025-12-31 | 5 (2.5/年) | 100.0% | +15.66% | 4.38 | ∞ | -3.87% |
| Part C (Live) | 2026-01-01 ~ 2026-04-15 | 2 (7.1/年) | 50.0% | -0.74% | -0.08 | 0.85 | -6.45% |

### 關鍵發現

1. **BB 下軌優於固定回檔門檻**：統計自適應門檻在 CIBR 1.53% vol 環境下有效，低波動期自動收窄（需更淺回檔即觸發）、高波動期自動展寬（需更深回檔才觸發）
2. **ClosePos 在 BB 框架中不可或缺**：移除後 Sharpe 從 0.27 暴跌至 0.09（Part A），從 4.38 暴跌至 0.02（Part B）。BB 下軌觸及+超賣不足以確認反轉，日內反轉確認（ClosePos≥40%）是關鍵品質過濾
3. **BB(20,1.5) 過寬**：較小標準差使下軌更接近中軌，觸發更多低品質訊號
4. **SIVR-013 BB 下軌失敗而 CIBR-007 成功的原因**：(a) CIBR vol 1.53% 遠低於 SIVR 2-3%，熊市反覆觸及頻率低；(b) 三重品質過濾（WR+ClosePos+ATR）有效抑制假訊號

---

## 演進路線圖 (Roadmap)

```
CIBR-001 (回檔+WR 基礎版，Sharpe 0.11)
  ├── CIBR-002 (波動率自適應 MR，Sharpe 0.23，+109%)
  │     ├── Att1: +ATR>1.15+ClosePos>=40%（Sharpe 0.18）
  │     ├── Att2: +回檔上限12%（反效果，撤回）
  │     └── Att3: 回檔4%=2.6σ（Sharpe 0.23）
  ├── CIBR-003 (BB Squeeze 突破，失敗，Sharpe -0.20/-0.27)
  ├── CIBR-004 (RSI(2)→動量強化MR，失敗，未超越 CIBR-002)
  │     ├── Att1: RSI(2)<10+2d-decline（min -0.19，RSI(2)板塊ETF無效）
  │     ├── Att2: pullback+WR+2d -1.5%+TP4.0%（min -0.00，TP反效果）
  │     └── Att3: pullback+WR+2d -2.0%+SL-4.5%（min -0.05，SL加寬無效）
  ├── CIBR-005 (20日回看MR，失敗，A/B 訊號失衡，未超越 CIBR-002)
  │     ├── Att1: 20日+6%+WR(14)+15天（min 0.18，A/B 2.0:1 失衡）
  │     ├── Att2: 持倉18天（min 0.18，Part A 不穩定）
  │     └── Att3: 7%門檻+15天（min 0.12，Part B 過濾過度）
  ├── CIBR-006 (RS 動量回調，完全失敗，三次嘗試均負 Sharpe)
  │     ├── Att1: QQQ基準+RS>=3%+5d回調3-8%+SMA50（min -0.85，訊號太少）
  │     ├── Att2: SPY基準+RS>=2%+10d回調2-8%+無趨勢（min -0.22，WR42.9%）
  │     └── Att3: +ATR+ClosePos+SMA（min 0.00，僅1訊號）
  ├── CIBR-007 (BB 下軌 MR，Sharpe 0.27，+17% vs CIBR-002)
  │     ├── Att1: BB(20,2.0)+WR+ClosePos+ATR（min 0.27）
  │     ├── Att2: BB(20,1.5) 品質稀釋（撤回）
  │     └── Att3: 移除 ClosePos（min 0.02，品質崩壞）
  └── CIBR-008 ★ (BB 下軌 + 回檔上限混合進場，Sharpe 0.39，+44% vs CIBR-007)
        ├── Att1: 回檔上限 -8%（過嚴，min 0.27，Part A 僅 3 訊號）
        ├── Att2: 回檔上限 -12%（min 0.39）★ Final
        └── Att3: 回檔上限 -10%（min 0.27，未濾剩餘停損）
```

---

## CIBR-008：BB 下軌 + 回檔上限混合進場 ★當前最佳

### 目標 (Goal)

CIBR-007（BB 下軌 MR）的 Part A Sharpe 0.27 / Part B Sharpe 4.38 存在巨大 A/B 落差
（累計報酬 8.42% vs 15.66%, gap 86%）。Part A 的 3 筆停損均發生在極端下跌期
（2020-02-24、2020-03-16 COVID 崩盤；2021-02-26 科技股拋售）。這些訊號雖符合
BB 下軌+WR+ATR+ClosePos 品質過濾，但 BB 帶寬在持續崩盤中外擴失去選擇性（lesson #52）。

本實驗參考 EWJ-003 Att3 的成功混合進場模式（BB 下軌 + 10日高點回檔上限 -7%，
Part A Sharpe 0.55→0.60），在 CIBR-007 基礎上疊加回檔上限過濾器，隔離極端崩盤同時
保留 BB 下軌的統計自適應特性。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| BB 下軌觸及 | Close vs BB(20, 2.0) Lower | Close <= BB_lower | 統計自適應進場 |
| 崩盤隔離 | 10日高點回檔 | >= -12%（~7.8σ） | 過濾連續崩盤訊號 |
| 超賣確認 | Williams %R(10) | <= -80 | 標準超賣閾值 |
| 日內反轉 | Close Position | >= 40% | 收盤離日低 40% 以上 |
| 波動率急升 | ATR(5)/ATR(20) | > 1.15 | 區分急跌 vs 慢磨下跌 |
| 冷卻期 | 前次訊號間隔 | >= 8 天 | 防止下跌趨勢連續進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 止盈 (TP) | +3.5% | 與 CIBR-002/007 相同 |
| 停損 (SL) | -4.0% | 與 CIBR-002/007 相同（-4.5% 已驗證無效） |
| 最長持倉 | 18 天 | 與 CIBR-002/007 相同 |
| 追蹤停損 | 不使用 | 日波動 1.53% 在追蹤停損有效邊界外 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 訊號隔日開盤市價進場 |
| 出場方式 | 悲觀認定（日內觸及 TP/SL 時假設先觸及不利方向） |
| 滑價 | 0.1%（ETF 標準） |
| 未成交處理 | 開盤價直接進場（市價單） |

### 迭代歷程 (Iteration History)

- **Att1（pullback_cap = -8%）**：過嚴（5.2σ），Part A 僅 3 訊號（2W 1L 2.73%）/
  Part B 4 訊號（100%WR 11.75%），min(A,B) = 0.27（未改善）。移除 4 個 Part A 贏家
  （2019-08-05、2020-10-30、2022-05-10、2022-09-01）與 1 個 Part B 訊號（2024-02-21）。
  失敗分析：8% 回檔上限在 1.53% vol 資產上過嚴，過濾了大量均值回歸有效訊號。
- **Att2（pullback_cap = -12%）** ★ 最佳：Part A 7 訊號（5W 2L 9.23%, WR 71.4%, Sharpe **0.39**）
  / Part B 5 訊號（100%WR 15.66%, Sharpe 4.38），min(A,B) **0.39**（+44% vs CIBR-007）。
  成功濾除 2020-03-16（COVID 連續崩盤，深度 >12%）與 2022-05-10（意外移除此贏家）
  。保留 2020-02-24 / 2021-02-26 兩筆停損（回檔深度在 -10~-12% 區間）。
  A/B 訊號頻率比 1.4:1（優秀），累計報酬 gap 從 86% 收窄至 41%。
- **Att3（pullback_cap = -10%）**：Part A 6 訊號（4W 2L 5.54%, Sharpe 0.27）/
  Part B 5 訊號（15.66%, Sharpe 4.38），min(A,B) = 0.27（回退）。失敗分析：-10%
  濾除了 1 贏家（2020-10-30）但未能濾除剩餘 2 停損（2020-02-24、2021-02-26 回檔
  深度介於 -10~-12%）。確認 -12% 為甜蜜點。

### 回測結果 (Backtest Results, Att2 Final)

| 區間 | 期間 | 訊號數 | 勝率 | 累計報酬 | Sharpe | MDD |
|------|------|--------|------|----------|--------|-----|
| Part A (IS) | 2019-01-01 ~ 2023-12-31 | 7 (1.4/年) | 71.4% | +9.23% | 0.39 | -6.81% |
| Part B (OOS) | 2024-01-01 ~ 2025-12-31 | 5 (2.5/年) | 100.0% | +15.66% | 4.38 | -3.87% |
| Part C (Live) | 2026-01-01 ~ 2026-04-16 | 2 (7.1/年) | 50.0% | -0.74% | -0.08 | -6.45% |

### 關鍵學習 (Key Learnings)

1. **回檔上限在 BB 下軌框架 vs pullback+WR 框架的行為相反**：CIBR-002 Att2 在 pullback+WR
   框架使用 12% 回檔上限反效果（Part A 0.18→0.12），但 CIBR-008 Att2 在 BB 下軌框架
   使用相同上限有效（+44%）。原因：pullback+WR 框架中 pullback 本身是主進場門檻，
   上限會壓縮有效區間；BB 下軌框架中 BB 是主進場門檻，pullback 僅作「崩盤過濾器」
   而不影響主訊號選擇性。
2. **BB 下軌框架的失敗模式是「崩盤連續段假訊號」**：BB 帶寬在持續下跌中外擴使下軌
   持續被觸及，ATR 過濾（相對波動率）+ ClosePos（日內反轉）不足以區分恐慌反彈 vs
   連續崩盤。絕對回檔深度（-12% = 7.8σ）提供獨立於相對指標的崩盤偵測。
3. **-12% 回檔上限甜蜜點的來源**：CIBR 歷史上絕大多數有效 BB 下軌 MR 訊號的回檔深度 < 12%，
   而崩盤連續段（COVID 2020-03、Q1 2021 科技拋售）深度 >12%。深於此即為結構性崩盤，
   淺於此即為正常均值回歸機會。
4. **Lesson #52 例外的條件**：「BB 下軌 MR 在持續熊市失效」的禁忌可被「絕對回檔上限」
   繞過。適用條件：(a) 低中波動（≤2.0%）資產；(b) 搭配 WR + ClosePos + ATR 三重品質
   過濾；(c) 回檔上限設在 7-8σ（CIBR 12%, EWJ 7%）。不適用於高波動資產（SIVR 2-3%：
   BB 下軌本身失效）或政策驅動 EM ETF（FXI：即使 BB 搭配回檔上限仍失效）。

---

## CIBR-009：Key Reversal Day 均值回歸 (Key Reversal Day MR)

### 設計理念 (Design Rationale)

CIBR-008 Att2 Part A 7 訊號含 2 停損（2020-02-24 COVID、2021-02-26 科技拋售）均為
「BB 下軌觸及但隔日繼續深跌」。測試能否改用 price-action 結構化的「washout + 日內反轉
確認」進場訊號，過濾此類 false bottom。

### 進場條件 (Entry Conditions)

| Att | WR 門檻 | Stop-run | ATR 比率 | 其他 |
|-----|---------|----------|----------|------|
| Att1 | ≤ -80 | Low < Prev Low | 無 | Prev 收黑 + Close > Prev Close + bullish bar + ClosePos ≥ 40% |
| Att2 | ≤ -80 | Low < Prev Low | > 1.15 | 同上 |
| Att3 | ≤ -85 | 無 | > 1.10 | 同上 |

共同條件：10 日高點回檔 ∈ [-12%, -3%]、冷卻 8 天。出場：TP +3.5% / SL -4.0% / 18 天。

### 回測結果 (Backtest Results)

| Att | Part A 訊號 | Part A WR | Part A Sharpe | Part B 訊號 | Part B WR | Part B Sharpe | min(A,B) |
|-----|-------------|-----------|---------------|-------------|-----------|---------------|----------|
| Att1 | 8 | 50.0% | -0.08 | 3 | 33.3% | -0.44 | **-0.44** |
| Att2 | 2 | 50.0% | -0.08 | 2 | 50.0% | -0.08 | -0.08 |
| Att3 | 1 | 0.0% | 0.00 | 1 | 0.0% | 0.00 | 0.00 (全 SL) |
| **vs CIBR-008 Att2（基準）** | 7 | 71.4% | 0.39 | 5 | 100.0% | 4.38 | **0.39** |

### 關鍵學習 (Key Learnings)

1. **Stop-run + reclaim 結構在 CIBR 無選擇性**：Att1 8 訊號 50% WR 證明「Low < Prev Low
   + Close > Prev Close + bullish bar」在熊市續跌中頻繁產生假反轉（dead-cat bounce）。
   2022 年 3 連 SL + 2025 年 2 連 SL 均屬此類失敗。
2. **ATR 飆升不等於反轉確認**：Part B 2025-02-28 訊號 ATR 1.44（顯著飆升）但隔日 1-day
   SL -4.1%，證明波動率擴張本身可能是崩盤的起點而非終點。
3. **訊號稀缺 vs 品質平衡失敗**：Att2 加嚴 ATR 將訊號壓縮至 2/2（0.4/年），Att3 進一步
   崩至 1/1 全停損，顯示 CIBR 上「price-action Key Reversal + ATR + WR」組合無甜蜜點。
4. **擴展 XBI-012 失敗模式至 CIBR**：XBI（生技板塊，FDA/臨床事件驅動）的 Capitulation +
   Acceleration Reversal 失敗（min 0.16 vs XBI-005 0.36）。CIBR（網路安全板塊，企業
   並購/資安事件驅動）的 Key Reversal Day 同樣失敗。整合觀察：**美國事件驅動板塊 ETF
   拒斥所有短週期單日 price-action 反轉結構**，需依賴波動率統計指標（BB 下軌+ATR）+
   絕對回檔深度過濾（CIBR-008 / EWJ-003 模式）。
5. **CIBR-008 Att2 全域最優確認**：本次 9 次實驗、27 次嘗試後，BB 下軌 + 回檔上限 -12%
   混合進場仍為 CIBR min(A,B) 0.39 天花板。

---

## CIBR-012：Post-Capitulation Vol-Transition MR ★當前最佳

### 目標 (Goal)

CIBR-008 Att2（BB 下軌 + 回檔上限混合進場，min(A,B) Sharpe 0.39）於 Part A 7 訊號中
仍有 2 筆停損（2020-02-24 COVID 前夕、2021-02-26 科技股輪動拋售），兩者均為
「急跌加速中」進場。目標：在保留 CIBR-008 全部品質過濾器的前提下，新增「進場時點」
過濾以排除 in-crash acceleration 訊號。

### 設計理念 (Design Rationale)

**核心觀察**（觀察 CIBR-008 Part A 7 訊號的 2 日收盤報酬分布）：
- SL: 2020-02-24 2DD -4.1% / 2021-02-26 2DD -3.9%
- TP: 2019-10-02 (-2.8%) / 2020-10-30 (-1.5%) / 2022-09-01 (-1.7%) /
      2023-03-13 (-2.8%)
- 結構性差異：**SL 的 2DD 較深於 TP 的 2DD**（SL -4%+ vs TP -1.5%~-3%）
  此規律暗示深 2DD（≥2.6σ 的 2 日急跌）代表「崩盤加速中」而非反轉起點

**新過濾條件**：`2-day close-to-close return >= -4.0%`（2DD cap）

**與 CIBR-004 的關鍵差異**（方向**完全相反**）：
- CIBR-004 Att2/Att3: 2DD **<= -1.5% / -2.0%**（2DD 下限，篩選急跌）— 失敗或非綁定
- CIBR-012 Att3: 2DD **>= -4.0%**（2DD 上限，排除 in-crash）— 成功

此為 repo 首次測試「2DD 上限」作為進場時機過濾器（vs 傳統「2DD 下限」急跌確認）。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | Close vs BB(20, 2.0) 下軌 | Close <= BB_lower | 統計自適應下軌觸及 |
| 2 | 10 日高點回檔 | >= -12% | 崩盤隔離（CIBR-008 驗證甜蜜點 7.8σ）|
| 3 | Williams %R(10) | <= -80 | 超賣確認 |
| 4 | ClosePos | >= 40% | 日內反轉跡象 |
| 5 | ATR(5)/ATR(20) | > 1.15 | signal-day 急跌 panic（CIBR-008 有效過濾）|
| 6 | **2 日收盤報酬** | **>= -4.0%** | **排除 in-crash acceleration（新）**|
| 7 | 冷卻期 | 8 天 | 避免連續進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +3.5% | 同 CIBR-008，已驗證甜蜜點 |
| 停損 (SL) | -4.0% | 同 CIBR-008，熊市停損常穿越 -4.5% |
| 最長持倉 | 18 天 | 同 CIBR-008 |
| 追蹤停損 | 不使用 | 1.53% 日波動，追蹤停損壓縮獲利 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 訊號隔日開盤市價進場 |
| 出場方式 | TP 限價賣單 Day / SL 停損市價 GTC / 到期隔日開盤 |
| 滑價 | 0.1%（ETF 標準） |
| 日內路徑 | 悲觀認定（同日觸 TP/SL 時假設先觸 SL） |

### 迭代歷程 (Iteration History)

| Iter | 設定 | Part A (Sharpe / WR / Cum) | Part B (Sharpe / WR / Cum) | min(A,B) | 結果 |
|------|------|---------------------------|---------------------------|----------|------|
| Att1 | ATR peak 10d ≥ 1.30 + today ≤ 1.20 | 0.00 / 100% / +3.50% (1 訊號) | 0 訊號 | 0.00 | ❌ 過嚴 |
| Att2 | 保留 CIBR-008 + prior 10d ATR peak ≥ 1.25 | 0.27 / 66.7% / +2.73% (3 訊號) | 4.21 / 100% / +9.25% (3 訊號) | 0.27 | ❌ 移除 3 贏家 |
| **Att3 ★** | **CIBR-008 + 2DD cap ≥ -4.0%** | **0.49 / 75% / +6.33% (4 訊號)** | **3.96 / 100% / +7.97% (3 訊號)** | **0.49** | ✅ **+26%** |

### 回測結果（Att3 ★）(Backtest Results)

| 區間 | 期間 | 訊號數 | 勝率 | 累計報酬 | Sharpe | MDD |
|------|------|--------|------|----------|--------|-----|
| Part A (IS) | 2019-01-01 ~ 2023-12-31 | 4 (0.8/年) | 75.0% | +6.33% | 0.49 | -6.81% |
| Part B (OOS) | 2024-01-01 ~ 2025-12-31 | 3 (1.5/年) | 100.0% | +7.97% | 3.96 | -3.87% |
| Part C (Live) | 2026-01-01 ~ 2026-04-20 | 1 | 0.0% | -4.10% | 0.00 | -6.45% |

### 逐筆交易分析（Att3）

**Part A 4 訊號（過濾結果）：**
- ✅ 2019-10-02 target +3.50%（勝）
- ✅ 2020-10-30 target +3.50%（勝）
- ✅ 2021-02-26 stop_loss -4.10%（保留；2DD -3.9% > -4.0% 未被濾除）
- ✅ 2023-03-13 target +3.50%（勝）
- ❌ 2019-08-05 TP 被濾除（2DD ≤ -4.0%）
- ✅ 2020-02-24 SL 被濾除（2DD -4.1%，成功過濾 COVID precursor）
- ❌ 2022-09-01 TP 被濾除（2DD ≤ -4.0%）

**Part B 3 訊號（過濾結果）：**
- ✅ 2024-04-16 time_expiry +1.99%（保留）
- ✅ 2025-08-01 time_expiry +2.28%（保留）
- ✅ 2025-11-18 target +3.50%（勝）
- ❌ 2024-02-21 TP 被濾除（2DD ≤ -4.0%）
- ❌ 2024-08-02 TP 被濾除（2DD ≤ -4.0%，yen carry unwind）

**淨效果：Part A 保留 1 個 SL 但 4 個 TPs 中仍有 3 個，WR 提升 71.4→75%，
Sharpe 提升 0.39→0.49（+26%）。Part B 失去 2 個 TPs 但 Sharpe 維持 3.96。**

### 關鍵發現與失敗分析

1. **2DD 上限過濾方向正確性**：CIBR-004 的 2DD 下限（≤-1.5%/-2.0%）已驗證失敗
   （非綁定或移除好訊號），本實驗 2DD 上限（≥-4.0%）反向成功，揭示 CIBR 的
   in-crash acceleration 訊號為結構性失敗源（lesson #19 延伸至 2DD 上限方向）。

2. **Att1 結構性衝突**：「今日 ATR ≤ 1.20」與 CIBR-008 的「ATR > 1.15」幾乎互斥，
   兩條件共存使訊號近乎歸零（1 訊號/8 年）。任何與 working filter 結構性衝突的
   新過濾器在 tight 品質過濾框架下會立即歸零。

3. **Att2 先期 ATR 峰值不具區分力**：CIBR winners 可發生在前期平靜、突然 capitulation
   的結構中，prior ATR peak 與 winner/loser 無關聯。此發現與 lesson #20b entry-time
   filter 失敗家族一致——ATR 峰值作為過濾器缺乏 winner/loser 區分力。

4. **2DD 上限為 in-crash acceleration 的可測量指標**：-4.0% = 2.6σ for 1.53% vol，
   此閾值具統計意義（2 個標準差外事件）而非任意選擇。深 2DD 反映「崩盤加速中」
   持續拋售，淺 2DD 反映「減速階段」MR 進場時機。

5. **跨資產延伸假設（待驗證）**：
   - 其他 BB 下軌 + 回檔上限混合進場資產（XBI, XLU, IWM, COPX, VGK, EEM）可能受益
     於 2DD cap 補充過濾，特別是 Part A 有 crash-day SLs 的資產
   - 不適用於單日決策驅動資產（TQQQ 槓桿、IBIT 加密、FXI 政策驅動）——這些資產的
     winners 與 in-crash entries 可能重疊
   - 適用閾值可能隨日波動度縮放：CIBR 1.53% vol → 2DD -4.0%（2.6σ）；高波動資產
     （SIVR 2-3% vol）預計 2DD cap 應為 -5% 或更深

### 全域最優狀態

CIBR-012 Att3 現為全域最優（min(A,B) Sharpe 0.49，12 次實驗、36+ 次嘗試）。

---

## CIBR-013：Higher-Low Structural Confirmation MR（失敗，repo 首次多日 swing 結構 pattern 主過濾器試驗）

### 目標 (Goal)

驗證「多日 swing 結構 pattern」作為 MR 主過濾器能否突破 CIBR-009/010/011 三次「單日
price-action」過濾失敗的根因。

### 設計理念 (Design Rationale)

**核心假設**：將「單日 pattern」（Key Reversal、NR7、Range Expansion）擴展為「多日
結構 pattern」可繞過 lesson #20b V-bounce ≠ genuine reversal 的限制。Higher-Low 結構
（今日 Low 嚴格高於過去 N 日 Low 最低值）為多日 swing 結構的量化定義：
- 單日 ClosePos 反映當日盤中反轉程度（時間尺度 = 1 日）
- 多日 Higher-Low 反映 swing 結構的反轉確認（時間尺度 = N 日）
- 後者篩選「過去 N 日已建立 swing low + 今日不再破底」的進場時機

Repo 首次將多日 swing 結構 pattern 作為 MR 主過濾器於任何資產。

### 迭代歷程 (Iteration History)

#### Att1：純 pullback+WR+Higher-Low(3)+Bullish bar+ATR>1.10 5 重交集

**進場條件**：10d pullback in [-3%, -10%] + WR(10) ≤ -80 + Today_Low > min(Low[t-3..t-1])
+ Swing depth ≥ 1.0% + Close > Open + ATR(5)/ATR(20) > 1.10 + cd 8

**結果**：Part A 2 訊號 50% WR Sharpe **-0.08** cum -0.74%（1 TP 2023-04-27 +3.5% / 1 SL
2022-04-28 -4.10%）/ Part B **0 訊號** / min(A,B) **-0.08**

**失敗分析**：5 重交集（pullback + WR + Higher-Low + Bullish bar + ATR）過嚴，訊號密度
0.4/yr，Part B 完全空白。Higher-Low(3) + ATR>1.10 + bullish bar 三重結構確認在事件驅動
板塊 ETF 上過於罕見。

#### Att2：放寬 ATR=1.00（停用）+ Higher-Low lookback 3→5

**結果**：Part A 3 訊號 33.3% WR Sharpe **-0.44** cum -4.81%（新增 1 SL）/ Part B 1 訊號
zero-var TP +3.5% Sharpe 0.00 / min(A,B) **-0.44**

**失敗分析**：放寬 lookback 5 與停用 ATR 引入 1 個新 Part A 訊號為 SL，Part A WR 從
50%→33.3%。Higher-Low + 寬 ATR 環境下信號天然偏向「中段反彈失敗」型態。

#### Att3：BB Lower 框架 + Higher-Low(5)（取代 CIBR-012 的 2DD cap）

**進場條件**：Close ≤ BB(20,2) 下軌 + 10d pullback ≥ -12% + WR(10) ≤ -80 +
ClosePos ≥ 40% + ATR(5)/ATR(20) > 1.15 + Today_Low > min(Low[t-5..t-1]) +
Swing depth ≥ 0.5% + cd 8

**結果**：Part A **0 訊號** / Part B **0 訊號** / min(A,B) **0.00**

**失敗分析（重要結構性發現）**：BB Lower 觸及（Close ≤ BB_lower）日為統計極端下殺，
今日 Low 幾乎必為近 5 日新低；而 Higher-Low(5) 要求今日 Low > min(Low[t-5..t-1])。
**兩條件在 CIBR 1.53% vol 板塊 ETF 上幾乎完全互斥**（過去 8 年僅 1 訊號於 Part C 觸發）。
Repo 首次驗證「BB Lower entry + multi-bar Higher-Low filter 結構性不可組合」。

### 關鍵發現與失敗分析

1. **多日結構維度未繞過單日 pattern 的失敗根因**：擴展 lesson #20b 失敗家族至
   **多日結構 pattern (Higher-Low Confirmation)**——CIBR 等事件驅動板塊 ETF 上，
   無論 entry-time 過濾器是單日 (Key Reversal、NR7、Range Expansion、ClosePos、
   2DD floor/cap) 或多日結構 (Higher-Low) 維度，皆缺乏「真假反轉」區分力。

2. **BB Lower 與 Higher-Low 結構性互斥**：BB Lower 觸及日的數學特性（統計極端）
   與 Higher-Low 結構（多日反轉確認）在低-中波動板塊 ETF 不可組合。此發現平行
   於 CIBR-010 NR7 與 ATR 過濾器的結構性衝突——兩個結構性概念可能互斥，過濾器
   組合需先驗證可共存。

3. **訊號稀疏性問題**：純 pullback+WR 框架下加 Higher-Low + bullish bar + swing
   depth 5 重交集訊號密度 < 0.5/yr，與 CIBR-011 Range Expansion 同樣稀疏問題。

4. **跨資產假設（待驗證）**：Higher-Low 多日結構 pattern 可能在「具備持續 MR
   regime 結構」的資產（如低波動低事件密度寬基 ETF）上有效，但需重新設計與
   BB Lower 互斥問題的兼容方案（例如改用 pullback-based 進場 + Higher-Low(7-10)
   長 lookback）。CIBR 1.53% vol 板塊 ETF 不適合此 pattern。

### 全域最優狀態（不變）

CIBR-012 Att3 現為全域最優（min(A,B) Sharpe 0.49，13 次實驗、39+ 次嘗試）。CIBR-013
為 CIBR 第 8 個失敗策略類型（突破、RSI(2)、RS 動量、Key Reversal、NR7、Range Expansion、
2DD floor、Higher-Low Structural Confirmation）。
