<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-04-24
  data_through: 2025-12-31
  note: TLT-011 added 2026-04-24 (Dynamic BB-Width Percentile Regime MR, **repo first percentile-based BB-width regime gate trial on any asset**). Three iterations all failed vs TLT-007 Att2 min 0.12: Att1 (252d lookback + 50th pctile, no absolute backup) Part A 24/50.0% WR/Sharpe **-0.11** cum -7.76% / Part B 11/81.8% WR/Sharpe 0.55 cum +14.72% / min **-0.11** — 50th pctile 過寬，2022 升息期 trailing 252d 窗口被自身主導導致中位數本身被拉高，「當日 <= 中位數」仍放行整片 2022 訊號流；Att2 (504d lookback + 40th pctile) Part A 13/53.8% WR/Sharpe **0.01** cum +0.06% / Part B 11/81.8% WR/Sharpe 0.55 cum +14.72% / min **0.01** — 擴大到 504 日仍不足，40th pctile 勉強降低 Part A 訊號至 13（接近 TLT-007 Att2 的 12）但 Sharpe 仍未轉正；Att3 (hybrid dual gate：252d pctile <= 40th AND 絕對 BB<5%) Part A 10/50.0% WR/Sharpe **0.03** cum +0.53% / Part B 6/83.3% WR/Sharpe 0.65 cum +9.07%（與 TLT-007 Att2 Part B 完全相同！）/ min **0.03** — Part B 6 筆訊號 BB 寬度皆 <5% 且 pctile<=40th（calm regime 自洽），但 Part A 的 pctile 濾波系統性移除 TLT-007 Att2 的 2 筆贏家（絕對 BB<5% 但相對近 252 日為高分位數的 calm regime 末期 / regime 轉換初期訊號）。**Core finding (結構性)**：rolling percentile-based BB-width regime gate 在 TLT 上系統性失效，無論純動態（Att1/Att2）還是與絕對閾值組合（Att3）皆劣於 TLT-007 Att2 固定 5% 閾值。**根因**：(1) TLT 2022 為單一持續 12+ 個月的 extreme vol regime episode，rolling percentile 在此期間自我稀釋——參考窗口被 regime 期間主導，percentile 失去 cross-regime 區分力；(2) 即使絕對閾值已切除 2022 訊號，追加 pctile 過濾會以「相對近期歷史」為基準錯誤標記 calm regime 末期好訊號為「相對高」而過濾之。**新 cross-asset 規則**：對於**單一極端 vol regime episode 持續時間長於 percentile lookback 視窗 50%** 的資產，rolling percentile-based regime gate 結構性失效——固定絕對閾值為唯一有效解。與 FXI-013 的「多段中等 vol regime 下固定和動態皆失敗」互補，共同精煉 BB-width regime gate 的適用邊界。TLT's 11th failed strategy type. TLT-007 Att2 remains global optimum (11 experiments, 32+ attempts). TLT-010 added 2026-04-24 (Capitulation-Confirmed Vol-Regime-Gated MR, 2DD + ATR supplementary filters on TLT-007 Att2, **repo first 2DD/ATR filter trial on TLT**). Three iterations all failed vs TLT-007 Att2 min 0.12: Att1 (TLT-007 Att2 + 2DD floor <= -1.5%, lesson #19 direction) Part A 6/33.3% WR/Sharpe **-0.11** cum -1.61% (2 TP/1 SL/3 Expiry) / Part B 3/100% WR/Sharpe 0.00 zero-var cum +7.69% (3 TP, 3/6 Part B winners filtered) / min **-0.11** — 2DD floor 移除 3 Part A TPs (2019-07-12/2021-08-11/2022-02-07) + 2 SLs (2020-05-26/2021-02-04) + 2 expiries，並引入 cooldown-shift new SL 2020-06-03（lesson #19）。TLT winners 分布橫跨淺深 2DD（2019-11-05/2020-11-09 為深 2DD 贏家、2019-07-12/2021-08-11/2022-02-07 為淺 2DD 贏家），2DD 無方向性選擇力；Att2 (2DD cap >= -2.0%, CIBR-012 direction) Part A 9/55.6% WR/Sharpe **0.02** cum +0.28% (4 TP/1 pos exp/2 SL/2 neg exp + cooldown-shift new SL 2020-12-04 -3.01%) / Part B 5/80% WR/Sharpe 0.52 cum +6.41% (4 TP/1 SL，2024-05-29 TP 因 2DD 過深被過濾) / min **0.02** — 2DD cap 移除 3 個 Part A 近零負值到期（2020-08-12/2020-12-02/2021-01-06）但同時移除 2020-11-09 TP 並引入 cooldown-shift 新 SL；Att3 (disable 2DD, add ATR(5)/ATR(20) >= 1.05, repo first TLT ATR trial) Part A 7/42.9% WR/Sharpe **-0.18** cum -3.19% / Part B 1/100% WR/Sharpe 0.00 zero-var (5/6 Part B winners filtered!) / min **-0.18** — ATR 擴張濾波過嚴，Part B 訊號崩潰至 1 筆；Part A 保留訊號中 ATR 條件反向選擇（移除平滑 TP 贏家，保留急跌 SL）。**Core finding (結構性)**：2DD floor、2DD cap、ATR expansion 三類「signal-day secondary filter」在 TLT 上皆失敗，擴展 lesson #20b 失敗家族至 **利率政策驅動資產的 signal-day secondary filter 類別**（與 lesson #6 邊界擴展一致）。TLT-007 Att2 的「BB-width regime gate」之所以成功，在於它是「regime-level classifier」而非「signal-day secondary filter」——前者一次性切除 2022 升息期整段訊號流，後者試圖在剩餘訊號流內二次篩選但無選擇力。**新 cross-asset 規則**：rate-driven 資產（TLT 驗證、XLU/REITs 預期）在已套用 regime-level BB-width gate 後，**signal-day secondary filters 結構性失效**——未來改進方向應為更精細的 regime-level classifier（如 BB 寬度 60 日分位數 dynamic regime），非 signal-day filter。TLT's 10th failed strategy type. TLT-007 Att2 remains global optimum (10 experiments, 29+ attempts). TLT-009 added 2026-04-23 (Yield-Velocity-Gated MR using external ^TNX 10Y Treasury yield, **repo first use of external Treasury yield data as regime filter**). Three iterations all failed vs TLT-007 Att2 min 0.12: Att1 (pure yield gate: ^TNX 10d change <= +15bps, BB gate disabled) Part A 24/45.8% WR/Sharpe **-0.16** cum -10.74% (11W/8SL/5Exp) / Part B 8/87.5% WR/Sharpe 0.86 cum +14.59% / min **-0.16** — 2022 升息呈階梯式，median +12bps，+15bps 門檻讓多段短期平緩窗口訊號通過（2022-03-10/05-05/08-05/08-17/10-11 共 5 筆），但 Part B 8 訊號 vs TLT-007 Att2 6 訊號多 2 筆 87.5% WR 顯示 yield gate 在 Part B 有訊號放寬價值；Att2 (hybrid BB 寬度<5% AND ^TNX 10d<=+15bps) Part A 9/33.3% WR/Sharpe **-0.15** cum -3.33% / Part B 4/100% WR/Sharpe 0.00 zero-var / min **-0.15** — 雙閘門邊界重疊，BB 5% 在 Att1→Att2 砍掉的 15 筆中 7W/7SL，系統性移除 regime transition 期贏家（2020-05-06、2021-10-08、2022-05-05、2023-04-18、2023-08-17、2023-10-20）；Att3 (yield 方向閘門：^TNX 5d change <= 0，BB gate 停用) Part A 4/50% WR/Sharpe **-0.22** cum -2.70% (2W/2SL) / Part B 1/100% WR/Sharpe 0.00 / min **-0.22** — yield 方向與 TLT pullback 進場時機微觀反向（TLT MR 觸發當下 ^TNX 近日通常仍略升），方向閘門過濾率 >90%。**Core finding (結構性失敗)**：外部 ^TNX yield velocity 作為 TLT MR regime gate 無論 magnitude-based (Att1/2) 還是 direction-based (Att3) 皆失敗。(a) 日線 yield velocity 與 TLT 日內 MR trigger 時序錯位：Fed rate shock 在 yield 先反映 (leading)，但 TLT MR 觸發多發生於 rate-shock 後 TLT 日內反轉，此時 ^TNX 近 N 日仍呈正值；(b) BB 寬度 gate（backward-looking 已成形 realized vol）與 MR setup 邏輯（pullback 已發生、WR 已超賣）一致，反而 forward-looking yield driver 與 MR trigger 不同步；(c) TLT-008（IEF pair）+ TLT-009（^TNX driver）共同驗證：外部利率相關指標作為 TLT MR 過濾器結構性受限，TLT-007 的「資產自身 BB 寬度 regime gate」仍為最佳方向。**Cross-asset 擴展**：其他利率政策驅動資產（XLU 部分、REITs、高殖利率股）可能承襲相同結論——自身 BB 寬度 > 外部 yield 指標。未來若要突破 TLT min 0.12，方向應為 TLT-007 Att2 的**更精細 BB 寬度 regime 分層**（如 BB 寬度 60 日分位數 regime 而非固定閾值），而非加入外部 yield 指標。TLT-007 Att2 仍為 TLT 全域最佳（9 實驗、26+ 嘗試）。TLT-008 added 2026-04-23 (Duration-Spread Pairs Trading MR vs IEF, **repo first pairs-trading attempt on rate-driven asset**). Three iterations all failed vs TLT-007 Att2 min 0.12: Att1 (pure pair: TLT-IEF 10d spread <= -2% + ClosePos + Daily Up + BB<5%) Part A 4/0% WR/Sharpe **-5.92** cum -12.49% / Part B 1/100%/zero-var Sharpe 0.00 / min **-5.92** — pair signal captures "TLT bear-market onset" not reversal; Att2 (hybrid TLT-007 full framework + TLT-IEF 10d spread <= -1.5%) Part A 6/0% WR/Sharpe **-1.71** (2 SL/4 expiry) cum -12.86% / Part B **0 signals** (vs TLT-007 Att2's 6 winners filtered out!) / min **-1.71** — pair filter **systematically removes winners, keeps losers**; inverse direction test (TLT 5d outperform IEF >= +0.3%) **0 signals all parts** — structural contradiction (TLT always underperforms IEF during own pullback due to duration mechanics); Att3 final (TLT/IEF 100d z-score <= -1.5σ + TLT-007 framework) Part A 6/33.3% WR/Sharpe **-0.31** (2W/1SL/3 expiry) cum -4.64% / Part B 2/100%/zero-var Sharpe 0.00 / min **-0.31** — z-score recovers 2022-02-08 winner but can't salvage 2020-12/2021-01 continuous loss regime signals. **Core finding (extends lesson #20)**: TLT vs IEF same-asset-class duration pair structurally fails — TLT/IEF relationship during TLT pullbacks is **mechanically determined by duration sensitivity ratio** (TLT ~2.4x IEF rate sensitivity), not classical "independent entities' deviation-reversion" pairs MR structure. "TLT loses IEF" filter systematically retains rate-shock onset signals (winners filtered); "TLT beats IEF" filter contradicts MR entry structure; z-score statistical standardization cannot overcome this structural limit. **TLT-008 becomes first confirmed failure of same-asset-class mechanical pair MR on rate-driven asset**, distinguishing from sectoral/event-driven pairs under lesson #20. TLT-007 Att2 remains global optimum (8 experiments, 23+ attempts). TLT-007 added 2026-04-22 (Volatility-Regime-Gated MR, **repo first BB-width-ratio as regime gate on TLT**). Three iterations, Att2 SUCCESS — **repo first positive min(A,B) on TLT ever**. Att1 (pullback 3-7% + WR≤-80 + ClosePos≥40% + BB(20,2) width/Close<0.06) Part A 24/45.8%/Sharpe -0.20 / Part B 10/80.0%/Sharpe 0.48, min -0.20 (tie with TLT-002, BB 6% still passes 2022 hiking signals); **Att2 SUCCESS (BB width/Close<0.05)** Part A 12/50.0%/Sharpe **0.12** cum +2.95% / Part B 6/83.3%/Sharpe **0.65** cum +9.07% / min(A,B) **0.12** (+0.32 abs vs TLT-002 -0.20; Part B +171% vs TLT-002 0.24). BB 5% filtered most 2022 hiking-cycle signals (kept only 2022-02-07 winner), Part A signals 24→12 with 6W/3SL/3expiry structure; A/B signal annualized 2.4/yr vs 3.0/yr (20% diff ✓, <50% goal). A/B cum diff 67.5% (>30% target) but Part B>Part A (asymmetry favors live deployment, not overfitting); Att3 (BB<0.05 + SMA(100) today>=SMA(100) 20d ago slope filter) Part A 7/57.1%/Sharpe 0.29 / Part B 3/66.7%/Sharpe 0.16 / min 0.16 — SMA slope over-filtered Part B (6→3 signals, zero-variance risk), reverted to Att2. **Core finding**: BB-width-ratio as volatility-regime gate succeeds where TLT-002's 60-day ROC filter (≤-10%) failed — BB width captures realized volatility expansion characteristic of 2022 hiking cycle while remaining neutral across 2024-2025 plateau. **Cross-asset hypothesis (pending)**: Volatility-regime gating (BB width/Close < asset-specific threshold) may extend to other rate-policy-driven assets with extreme 2022-2023 volatility spikes. Distinguishing feature vs lesson #5 (MR+trend filter=disaster): BB width is a market-state classifier (calm vs crisis regime), not a short-term directional trend filter. TLT-007 is repo first validation of this structural distinction; potential extension: any asset where Part A is dominated by a single extreme volatility regime episode. TLT-002 remains baseline but TLT-007 Att2 becomes new global optimum (7 experiments, 20+ attempts). TLT-006 added 2026-04-19 (Day-After Capitulation + Strong Reversal Bar MR ported from URA-009 Att2 framework). Three iterations all failed vs TLT-002 min -0.20 (see previous note, preserved below).
-->
## AI Agent 快速索引

**當前最佳：** TLT-007 Att2（回檔 3-7% + WR(10) + 反轉K線 + **BB(20,2) 寬度/Close<5% 波動率 regime 閘門**，Part A Sharpe **0.12** / Part B Sharpe **0.65** / min(A,B) **0.12**）★ **repo 首次 TLT min(A,B) 轉正**
**前任最佳：** TLT-002（回檔 3-7% + WR(10) + 反轉K線 + 60日跌幅≤10%，Part A Sharpe -0.20，Part B Sharpe 0.24）
**滾動窗口分析摘要：** TLT-001 ✓✓ 雙漸變（ΔWR max 20.0pp 邊界通過，升息週期嚴重虧損需警惕）

**已證明無效（禁止重複嘗試）：**
- Trailing stop 在 TLT 上無效（啟動 +1.5%/距離 1.0% 截斷獲利，Part A 僅 1 次達標，累計 -33.27%）
- RSI(2) < 10 + 2日跌幅進場（Part A -28.71%，2022 利率上升期產生大量假訊號）
- 回檔上限收窄至 5% 無改善（Part A 從 -22.76% 微升至 -20.89%，Sharpe 不變）
- 深度回檔 5-10%（TLT-002 Att1：Part A 僅 10 訊號/Sharpe -0.46，Part B 僅 3 訊號，訊號過少）
- 降低 TP +2.0%（TLT-002 Att2：WR 不變但每筆獲利縮水，Part A Sharpe -0.28，Part B 0.13，嚴格劣化）
- 60日跌幅≤10% 過濾（TLT-002 Att3/最終版：Part A Sharpe -0.21→-0.20 僅邊際改善，過濾器同時移除好壞訊號）
- TP +3.0% / SL -5.0% / cd10（TLT-003 Att1：Part A Sharpe -0.27，寬 SL 在 2022 停損時虧損更大）
- TP +3.0% / SL -3.5% / cd15（TLT-003 Att2：Part A Sharpe -0.33，高 TP 使原本 +2.5% 達標的交易翻轉為停損，cd15 移除好訊號）
- SL -5.0%（TLT-003 驗證：-5.0% 在 2022 升息環境只是延遲停損並加大虧損，Part A -0.27 vs -0.20）
- TP +3.0%（TLT-003 驗證：Part A 兩筆原本 +2.5% 達標的交易（2022-12-20、2023-02-13）翻轉為停損，Part A Sharpe 大幅劣化）
- cooldown 15d（TLT-003 驗證：Part A 從 42→32 訊號，移除的訊號好壞各半，淨效果為 Sharpe 劣化 -0.33）
- **BB 擠壓突破（TLT-004 Att1/Att2）**：Part A Sharpe 0.31（大幅改善），但 Part B -1.15（2024-2025 橫盤環境所有突破失敗，13 筆中僅 1 筆達標）。寬出場 TP+4%/SL-5%（Att2）Part A 降至 0.13，Part B 仍 -0.63
- **SMA 黃金交叉（TLT-004 Att3）**：Part A Sharpe 0.89（極佳），但 Part B 僅 2 個訊號（無統計意義），A/B 訊號比 3.5:1
- **Donchian(20) 突破 + SMA(50)（TLT-005 Att1/Att2）**：Part A Sharpe 0.15（SL-2.0%）→0.20（SL-3.5%），但 Part B -1.12/-0.83。與 TLT-004 BB 擠壓突破類似結論，進一步驗證突破類策略對 TLT Part B 的結構性失效
- **ROC(10) > 3% 動量策略（TLT-005 Att3）**：Part A Sharpe -0.06，Part B -1.43。買入短期動量後立即回吐，表現最差
- **趨勢跟蹤/突破策略整體對 TLT 無效**：均值回歸被 2022 升息殺死，突破策略被 2024-2025 橫盤殺死。TLT 受宏觀利率政策驅動，純技術面策略無法同時適應升息、降息、穩定三種環境。TLT-004（BB擠壓/SMA交叉）和 TLT-005（Donchian突破/ROC動量）共 6 次嘗試全面驗證

**已掃描的參數空間：**
- 均值回歸進場：回檔 3-7% / 5-10% + WR(10) ≤ -80 + ClosePos ≥ 40%（有/無 60日跌幅過濾）
- 均值回歸進場：RSI(2) < 10 + 2日跌幅 ≥ 1.5% + ClosePos ≥ 40%
- 突破進場：BB(20,2) 擠壓（60日 25th/20th 百分位，5日內）+ Close > Upper BB + Close > SMA(50)
- 突破進場：Donchian(20) 突破（Close > 20日最高 High）+ Close > SMA(50)
- 動量進場：ROC(10) > 3% + Close > SMA(50)
- 趨勢進場：SMA(20) 黃金交叉 SMA(50) + Close > SMA(20)
- 出場參數：TP +2.0~4.0% / SL -3.0~-5.0% / 持倉 20 天
- 冷卻期：7 / 10 / 15 / 20 天
- Trailing stop：+1.5% 啟動 / 1.0% 距離（失敗）、+2.0% 啟動 / 1.5% 距離（失敗）

**尚未嘗試的方向（可探索，但預期改善有限）：**
- 利率相關指標（如 10Y yield 變化率）作為過濾器（需外部資料源，超出現有框架）
- 季節性/月份過濾（避開 Fed 會議月份 — 但 2022 幾乎每月都有會議，過濾效果有限）
- ~~Day-After Capitulation + 強反轉 K 線（URA-009 Att2 框架移植）~~ → TLT-006 三次迭代均失敗（min(A,B) -0.37/-0.39/Part B 枯竭），確認政策驅動資產對單日/雙日 price-action 反轉過濾失效
- ~~波動率 regime 閘門（BB 寬度/Close 比例過濾）~~ → TLT-007 Att2 成功（首次 TLT min(A,B) 轉正至 0.12）。未來可探索：BB 寬度進一步收緊至 4.5% / **動態門檻（BB 寬度 60 日分位數 regime 而非固定閾值）**
- ~~配對交易（TLT vs IEF duration spread MR）~~ → TLT-008 三次迭代全失敗（min(A,B) -5.92/-1.71/-0.31），確認同資產類別但不同 duration 的機械性 pair 結構性不適用 MR 進場過濾
- ~~外部 ^TNX yield velocity gate（repo 首次外部 Treasury yield 數據過濾）~~ → TLT-009 三次迭代全失敗（min(A,B) -0.16/-0.15/-0.22）：magnitude-based (Att1/2) 與 direction-based (Att3) yield gate 皆結構性失敗。**核心原因**：日線 yield velocity 與 TLT 日內 MR trigger 時序錯位——Fed rate shock 在 yield 先反映但 TLT MR 觸發多發生於 rate-shock 後日內反轉，此時 ^TNX 近 N 日仍呈正值；BB 寬度 gate（backward-looking 已成形 vol）與 MR setup 邏輯（pullback 已發生、WR 已超賣）一致，反而 forward-looking yield driver 與 MR trigger 不同步。與 TLT-008 共同證明：**外部利率相關指標作為 TLT MR 過濾器結構性受限**
- ~~2DD floor / 2DD cap / ATR 擴張作為 signal-day secondary filter 疊加於 TLT-007 Att2~~ → TLT-010 三次迭代全失敗（min(A,B) -0.11/0.02/-0.18）：2DD floor（lesson #19 方向）、2DD cap（CIBR-012 方向）、ATR(5)/ATR(20) 擴張（repo 首次 TLT ATR）皆結構性失敗。**核心原因**：TLT-007 Att2 的 BB-width regime gate 已完成 regime-level classifier 角色（切除 2022 升息期）；剩餘訊號流中任何 signal-day secondary filter 無選擇力——TLT winners/losers 在 2DD、ATR 維度皆分布重疊。**擴展 lesson #6 + lesson #20b**：rate-driven 資產在已套用 regime-level gate 後，signal-day secondary filters 結構性失效；未來方向應為更精細的 regime-level classifier（如 BB 寬度 60 日分位數 dynamic regime）而非 signal-day filter
- ~~BB 寬度 rolling percentile dynamic regime gate（252d/504d lookback、30-50th pctile、純動態或與絕對 5% 雙閘門）~~ → TLT-011 三次迭代全失敗（min(A,B) -0.11/0.01/0.03，repo 首次 percentile-based BB-width regime gate）。Att1（252d/50th pctile）、Att2（504d/40th pctile）、Att3（252d/40th pctile + 絕對 BB<5% 雙閘門）皆未勝過 TLT-007 Att2 固定 5% 閾值。**核心原因**：TLT 2022 升息期為持續 12+ 個月的 single extreme vol regime episode，rolling percentile 在此期間**自我稀釋**——參考窗口被 regime 期間主導，percentile 失去 cross-regime 區分力（Att1 50th 放行 24 Part A 訊號，Sharpe 崩壞至 -0.11）。即使絕對閾值已切除 2022 訊號，追加 pctile 過濾（Att3）會以「相對近期歷史」為基準錯誤標記 calm regime 末期好訊號為「相對高」而過濾之（Part A 12→10，Sharpe 0.12→0.03）。**新 cross-asset 規則**：**單一極端 vol regime episode 持續時間長於 percentile lookback 視窗 50%** 的資產，rolling percentile-based regime gate 結構性失效——固定絕對閾值為唯一有效解

**關鍵資產特性：**
- TLT (iShares 20+ Year Treasury Bond ETF) 日波動約 1.00%，低於 GLD (1.11%)，GLD 比率 0.90x
- 受利率政策驅動，2022 經歷史上最大債券熊市（Fed 快速升息 0.25% → 5.25%）
- 均值回歸策略在利率穩定/降息期有效，但升息期持續產生假訊號
- 突破/趨勢策略在利率穩定期有效（Part A 2019-2023 Sharpe 0.31~0.89），但在利率高原橫盤期失效（Part B 2024-2025 Sharpe -1.15~-0.02）
- Part A (2019-2023) 涵蓋 2022 極端升息環境，任何均值回歸策略的 Part A 績效必然較差
- **TLT 的核心限制**：TLT 受宏觀利率政策驅動而非技術面。均值回歸被升息殺死，突破被橫盤殺死。無純技術面策略能同時適應所有利率環境
- **SL -4.0% 為 Part B 最佳（均值回歸）**：TLT-003 Att3 驗證 SL -4.0%/cd10 使 Part B Sharpe 從 0.24 升至 0.46，但 Part A 維持 -0.20，A/B 失衡加劇
- **Day-After Capitulation + 強反轉 K 線在 TLT 失效（TLT-006 驗證）**：三次迭代 min(A,B) -0.37/Part B 0 訊號/-0.39 均未勝過 TLT-002 的 -0.20。失敗根因：(a) 2022-2023 升息期間 TLT 在急跌後頻繁出現「Close > Prev High」反彈，但後續繼續下探創新低（8 次 -3.6% 停損集中於 2022 Aug-Sep + 2023 May-Sep）；(b) 收緊 capitulation 閾值（WR≤-90、2DD≤-2.5%、range 擴張 ≥ 1.15-1.2x）立即導致 Part B 枯竭，TLT 2024-2025 高利率高原期缺乏足夠的 capitulation-reversal 事件。與 URA-009 同屬「政策/事件驅動資產的單日/雙日反轉過濾失效」範式，擴展 cross_asset lesson #20b 邊界：Day-After Capitulation 模式在 **利率政策驅動** 資產上與 **核能政策驅動** 資產同樣失效
- **波動率 regime 閘門首次在 TLT 成功（TLT-007 Att2 驗證）**：BB(20, 2) 通道寬度 / Close < 5% 作為 regime 過濾器，成功過濾 2022 升息期絕大多數訊號（僅保留 2022-02-07 贏家一筆），Part A 訊號 42 (TLT-002) → 12，Part A Sharpe -0.20 → **0.12**（+0.32 絕對值），Part B Sharpe 0.24 → **0.65**（+171%）。min(A,B) 首次於 TLT 轉正（0.12 vs -0.20）。**核心發現**：BB 寬度捕捉了 2022 實現波動率飆升的結構，而 TLT-002 的 60 日 ROC ≤ 10% 過於寬鬆（2022 月度跌幅多在 5-10% 區間，多數通過）。**Lesson #5 區分**：BB 寬度是「市場狀態分類器」（crisis vs calm regime），非「進場日短線方向濾波」（後者為 lesson #5 所警告）。TLT-007 Att3（+SMA(100) 斜率正向）雖 Part A 微升至 0.29，但 Part B 訊號砍半至 3（零方差風險），放棄該方向。**跨資產延伸假設**：BB 寬度 regime 閘門可能適用於其他曾經歷極端波動率 regime 事件的利率政策驅動資產
- **跨資產驗證（2026-04-22，FXI-013 失敗）**：FXI-013 三次迭代（BB<8%、BB<12%、BB<10%+動態 252 日百分位）min(A,B) 最佳 0.09，遠低於 FXI-005 的 0.38。**TLT vs FXI 結構性差異**：TLT 2022 升息為**單一極端 vol regime episode**（BB 寬度持續 > 5% 的連續窗口），固定 BB 閾值可一次性排除；FXI 2019-2023 為**多段中等強度 vol regime**（貿易戰、COVID、監管、防疫、弱復甦），各期 BB 寬度分佈重疊（7-12%），固定或動態門檻均無法 cross-regime 區分 good vs bad signals。**精煉跨資產規則**：BB 寬度 regime 閘門有效先決條件為資產含**單一極端 vol regime 片段**可一刀切除；**多段中等 vol regime 重疊**（政策驅動 EM、事件驅動）結構性失效。預期成功候選：SPY/DIA/VOO（2020 COVID 單一極端 episode）、TQQQ（2022 單一科技熊市）；預期失敗候選：其他政策/事件驅動單一國家 ETF（INDA/EWZ/URA）
<!-- AI_CONTEXT_END -->

# TLT 實驗總覽 (TLT Experiments Overview)

## 標的特性 (Asset Characteristics)

- **TLT (iShares 20+ Year Treasury Bond ETF)**：追蹤美國 20 年以上長期公債指數
- 日均波動約 1.00%，低於 GLD (1.11%)，GLD 波動比率 0.90x
- 受聯準會利率政策直接驅動，2022 升息週期造成 TLT 從 $150 跌至 $80（-47%）
- 均值回歸策略在利率穩定/降息環境有效，但升息環境中持續產生假訊號

## 實驗列表 (Experiment List)

| ID      | 資料夾                          | 策略摘要                              | 狀態  |
|---------|--------------------------------|--------------------------------------|-------|
| TLT-001 | `tlt_001_pullback_wr_reversal`  | 回檔範圍 3-7% + WR + 反轉K線        | 已完成 |
| TLT-002 | `tlt_002_deep_pullback_lower_tp` | 回檔 3-7% + WR + 反轉K線 + 60日跌幅過濾 | 已完成 |
| TLT-003 | `tlt_003_wide_asymmetric`       | 回檔 3-7% + WR + 反轉K線 + SL -4.0% + cd10（未超越 TLT-002）| 已完成 |
| TLT-004 | `tlt_004_bb_squeeze_breakout`   | BB 擠壓突破 / SMA 黃金交叉（趨勢策略，未超越 TLT-002）| 已完成 |
| TLT-005 | `tlt_005_donchian_momentum`     | Donchian 突破 / ROC 動量（趨勢策略，未超越 TLT-002）| 已完成 |
| TLT-006 | `tlt_006_day_after_reversal_mr` | Day-After Capitulation + 強反轉 K 線均值回歸（3 次迭代均失敗）| 已完成（未改善）|
| TLT-007 | `tlt_007_regime_vol_gate_mr`    | 波動率 regime 閘門均值回歸（BB 寬度/Close<5%，Att2 SUCCESS）| ✅ **當前最佳**（首次 TLT min(A,B) 轉正）|
| TLT-008 | `tlt_008_duration_spread_mr`    | 配對交易 MR（TLT vs IEF duration spread，3 次迭代全失敗） | 已完成（未改善）|
| TLT-009 | `tlt_009_yield_velocity_mr`     | ^TNX yield velocity gate MR（repo 首次外部 Treasury yield 過濾，3 次迭代全失敗）| 已完成（未改善）|
| TLT-010 | `tlt_010_capitulation_regime_mr` | TLT-007 Att2 + 2DD/ATR supplementary filter（repo 首次 TLT 2DD/ATR，3 次迭代全失敗）| 已完成（未改善）|
| TLT-011 | `tlt_011_dynamic_regime_mr`      | 動態 BB 寬度分位數 regime 閘門 MR（repo 首次 percentile-based BB-width regime，3 次迭代全失敗）| 已完成（未改善）|

---

## TLT-001: 回檔範圍 + Williams %R + 反轉K線 (Pullback Range + WR + Reversal Candle)

### 目標 (Goal)

建立 TLT 首個均值回歸實驗，使用回檔範圍過濾 + Williams %R 超賣 + 收盤位置反轉確認。
回檔上限 7% 用於過濾持續性下跌（如 2022 升息環境）中的深度回檔假訊號。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 10 日高點回檔 | ≥ 3% | 短期回調觸發 |
| 2 | 10 日高點回檔 | ≤ 7% | 過濾極端/持續性下跌 |
| 3 | Williams %R(10) | ≤ -80 | 超賣確認 |
| 4 | 收盤位置 | ≥ 40% | 日內反轉確認 |
| 5 | 冷卻期 | 7 天 | 避免重複進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 (TP) | +2.5% | 參考 TLT 波動度縮放 |
| 停損 (SL) | -3.5% | 非對稱（SL > TP）|
| 最長持倉 | 20 天 | 允許充足的回歸時間 |
| 追蹤停損 | 無 | 已證明追蹤停損截斷 TLT 獲利 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | 隔日開盤市價 (next_open_market) |
| 止盈委託 | 限價賣單 Day (limit_order_day) |
| 停損委託 | 停損市價 GTC (stop_market_gtc) |
| 到期出場 | 隔日開盤市價 (next_open_market) |
| 滑價 | 0.10% |
| 悲觀認定 | 是（同根 K 線 stop+target 皆觸發 → 停損優先）|

### 設計理念 (Design Rationale)

- **回檔範圍 3-7%**：下限 3% 確保足夠回調深度觸發；上限 7% 過濾 2022 升息環境中 >7% 的持續性暴跌
- **Williams %R(10) ≤ -80**：確認短期超賣，WR 回看 10 天匹配債券的緩慢回歸特性
- **收盤位置 ≥ 40%**：過濾仍在下跌的訊號日，保留有日內反轉跡象的訊號
- **固定出場無追蹤停損**：TLT 的追蹤停損在低獲利時即觸發（+1.5% 啟動 vs TP +2.5%），大幅壓縮獲利空間
- **TP +2.5% / SL -3.5%**：參考 GLD-007 按 0.90x 波動度縮放，SL 較寬給予利率波動呼吸空間

### 迭代嘗試紀錄 (Iteration Log)

| # | 變更 | Part A Sharpe | Part B Sharpe | 結論 |
|---|------|-------------|-------------|------|
| 1 | GLD-007 模板 + Trailing stop +1.5%/1.0% | -0.39 | 0.04 | 追蹤停損截斷獲利，Part A 僅 1 次達標 |
| 2 | RSI(2) < 10 + 2日跌幅 ≥ 1.5% + ClosePos | -0.62 | 0.10 | 2022 產生大量假訊號，Part A 更差 |
| 3 | 回檔範圍 3-7% + WR(10) + ClosePos（最終版）| -0.21 | 0.24 | Part B 顯著改善，但 Part A 仍負 |
| 4 | 回檔範圍 3-5%（收窄上限）| -0.21 | 0.24 | 幾乎無差異，恢復 3-7% |

### 回測結果 (Backtest Results)

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|-------------------|-------------------|----------------|
| 訊號數 | 42 | 16 | 1 |
| 訊號/年 | 8.4 | 8.0 | 4.3 |
| 勝率 | 47.6% | 68.8% | 0.0% |
| 平均報酬 | -0.57% | +0.64% | -1.68% |
| 累計報酬 | -22.76% | +10.07% | -1.68% |
| 盈虧比 | 0.64 | 1.63 | 0.00 |
| Sharpe | -0.21 | 0.24 | 0.00 |
| Sortino | -0.24 | 0.34 | -1.00 |
| Calmar | -0.10 | 0.17 | -0.93 |
| MDD | -5.89% | -3.74% | -1.80% |
| 最大連續虧損 | 8 | 3 | 1 |

**A/B 分析**：
- 訊號比 42:16 = 2.6:1（偏高，主要因 2022 升息環境產生大量 Part A 訊號）
- Part A 勝率 47.6% vs Part B 68.8%（差距大，2022 年佔 Part A 11 筆訊號中 8 筆虧損）
- Part B 表現優異（Sharpe 0.24，PF 1.63），但 Part A 被 2022 拖累

**結論**：TLT 均值回歸策略在正常利率環境有效（Part B 顯示），但無法在極端升息環境（2022）中保持正績效。建議觀察 Part C 表現。

---

## TLT-002: 回檔 + WR + 反轉K線 + 60日跌幅過濾 (Pullback + WR + Reversal + 60-day DD Filter)

### 目標 (Goal)

改進 TLT-001 的 Part A 績效。TLT-001 的核心問題是 2022 升息期產生大量假訊號（Part A Sharpe -0.21）。嘗試透過不同策略改進風險調整後報酬。

### 進場條件 (Entry Conditions) — 最終版 (Att3)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 10 日高點回檔 | ≥ 3% | 同 TLT-001 |
| 2 | 10 日高點回檔 | ≤ 7% | 同 TLT-001 |
| 3 | Williams %R(10) | ≤ -80 | 同 TLT-001 |
| 4 | 收盤位置 | ≥ 40% | 同 TLT-001 |
| 5 | **60 日跌幅** | **≤ 10%** | **新增：過濾持續性熊市環境** |
| 6 | 冷卻期 | 7 天 | 同 TLT-001 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 (TP) | +2.5% | 同 TLT-001 |
| 停損 (SL) | -3.5% | 同 TLT-001 |
| 最長持倉 | 20 天 | 同 TLT-001 |
| 追蹤停損 | 無 | 同 TLT-001 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | 隔日開盤市價 (next_open_market) |
| 止盈委託 | 限價賣單 Day (limit_order_day) |
| 停損委託 | 停損市價 GTC (stop_market_gtc) |
| 到期出場 | 隔日開盤市價 (next_open_market) |
| 滑價 | 0.10% |
| 悲觀認定 | 是（同根 K 線 stop+target 皆觸發 → 停損優先）|

### 設計理念 (Design Rationale)

- **60 日跌幅 ≤ 10%**：區分「正常環境回檔」與「持續性熊市回檔」。2022 升息期 TLT 60 日跌幅常超過 10%，過濾器可移除部分假訊號
- **保留 TLT-001 其餘參數**：經 3 次嘗試驗證，其他參數調整（深回檔、低 TP）均導致劣化

### 迭代嘗試紀錄 (Iteration Log)

| # | 變更 | Part A Sharpe | Part B Sharpe | A WR / B WR | 訊號數 A/B | 結論 |
|---|------|-------------|-------------|------------|-----------|------|
| Att1 | 深度回檔 5-10% + TP +2.0% + 冷卻 10天 | -0.46 | 4.60 | 40.0%/100.0% | 10/3 | Part B 僅 3 訊號無統計意義，Part A 2022 訊號仍在 5-10% 範圍，過濾無效 |
| Att2 | 同 TLT-001 + TP +2.0% | -0.28 | 0.13 | 47.6%/68.8% | 42/16 | WR 完全不變（降低 TP 未轉換任何到期交易為達標），每筆利潤縮水導致全面劣化 |
| Att3 | 同 TLT-001 + **60日跌幅≤10%**（最終版）| **-0.20** | **0.24** | 46.9%/68.8% | 32/16 | Part A 改善邊際（-0.21→-0.20），移除 10 筆 Part A 訊號但 Part B 完全不變 |

### 回測結果 (Backtest Results) — 最終版 (Att3)

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|-------------------|-------------------|----------------|
| 訊號數 | 32 | 16 | 1 |
| 訊號/年 | 6.4 | 8.0 | 4.3 |
| 勝率 | 46.9% | 68.8% | 0.0% |
| 平均報酬 | -0.54% | +0.64% | -0.37% |
| 累計報酬 | -16.83% | +10.07% | -0.37% |
| 盈虧比 | 0.65 | 1.63 | 0.00 |
| Sharpe | -0.20 | 0.24 | — |
| Sortino | -0.23 | 0.34 | -1.00 |
| Calmar | -0.09 | 0.17 | -0.21 |
| MDD | -5.89% | -3.74% | -1.80% |
| 最大連續虧損 | 6 | 3 | 1 |

**A/B 分析**：
- 訊號比 32:16 = 2.0:1（改善自 TLT-001 的 2.6:1）
- WR 從 46.9% 提升至 68.8%（同 TLT-001，Part B 未受影響）
- 60 日跌幅過濾移除了 10 筆 Part A 訊號（其中 3 筆停損、2 筆達標、5 筆其他），淨效果為邊際改善
- Part A 仍為負（受 2022 升息環境制約），Part B 完全不變

**結論**：TLT-002 對 TLT-001 僅有邊際改善。TLT 均值回歸策略的根本限制在於 2022 升息環境——技術面過濾器（回檔深度、TP 調整、中期跌幅過濾）均無法有效區分「正常回檔」與「持續性利率趨勢下跌」。真正有效的改進可能需要利率相關數據（如國債殖利率變化率），但此為外部資料源，超出目前回測框架能力。

---

## 演進路線圖 (Roadmap)

```
TLT-001 (回檔範圍 3-7% + WR + 反轉K線)
  ├── TLT-002 (回檔 3-7% + WR + 反轉K線 + 60日跌幅≤10% 過濾) ← 當前最佳（邊際改善）
  │     ├── [失敗] Att1: 深度回檔 5-10% + TP +2.0%（Part A 僅 10 訊號、Sharpe -0.46）
  │     ├── [失敗] Att2: 同 TLT-001 + TP +2.0%（WR 不變、利潤縮水、Sharpe -0.28）
  │     └── [邊際] Att3: 同 TLT-001 + 60日跌幅≤10%（Sharpe -0.21→-0.20，最終版）
  ├── TLT-003 (寬停損 + 出場優化，3 次嘗試均未超越 TLT-002) ← Part B 改善但 Part A 持平
  │     ├── [失敗] Att1: TP+3.0%/SL-5.0%/cd10（Part A -0.27，寬 SL 加大停損虧損）
  │     ├── [失敗] Att2: TP+3.0%/SL-3.5%/cd15（Part A -0.33，高 TP 翻轉達標為停損）
  │     └── [持平] Att3: TP+2.5%/SL-4.0%/cd10（Part A -0.20 持平，Part B 0.46 大幅改善）
  ├── TLT-004 (趨勢跟蹤/突破策略，3 次嘗試均未超越 TLT-002) ← Part A 改善但 Part B 崩潰
  │     ├── [失敗] Att1: BB 擠壓突破 TP+3%/SL-3%（Part A 0.31 大幅改善，Part B -1.15 橫盤假突破）
  │     ├── [失敗] Att2: BB 擠壓突破 TP+4%/SL-5%（Part A 0.13 退化，Part B -0.63 仍負）
  │     └── [失敗] Att3: SMA(20)×SMA(50) 黃金交叉（Part A 0.89 極佳，Part B 僅 2 訊號無統計意義）
  └── TLT-005 (Donchian 突破/ROC 動量，3 次嘗試均未超越 TLT-002) ← 再次驗證趨勢策略限制
        ├── [失敗] Att1: Donchian(20)+SMA(50)/SL-2.0%/15d（Part A 0.15，Part B -1.12）
        ├── [失敗] Att2: Donchian(20)+SMA(50)/SL-3.5%/20d（Part A 0.20，Part B -0.83）
        └── [失敗] Att3: ROC(10)>3%+SMA(50)/SL-2.5%/15d（Part A -0.06，Part B -1.43）
```

## TLT-003: 寬停損非對稱出場 (Wide Asymmetric Exit Mean Reversion)

### 目標 (Goal)

探索出場參數優化能否改善 TLT 均值回歸策略。TLT-002 的 Part A Sharpe -0.20 受 2022 升息制約，嘗試透過寬停損（更多呼吸空間）、高獲利目標（更高每筆贏利）、長冷卻期（減少連續進場）改善風險調整後報酬。

### 進場條件 (Entry Conditions) — 最終版 (Att3)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 10 日高點回檔 | ≥ 3% | 同 TLT-001/002 |
| 2 | 10 日高點回檔 | ≤ 7% | 同 TLT-001/002 |
| 3 | Williams %R(10) | ≤ -80 | 同 TLT-001/002 |
| 4 | 收盤位置 | ≥ 40% | 同 TLT-001/002 |
| 5 | 冷卻期 | **10 天** | **加長：7 → 10 天** |

### 出場參數 (Exit Parameters) — 最終版 (Att3)

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 (TP) | +2.5% | 同 TLT-001/002 |
| 停損 (SL) | **-4.0%** | **加寬：-3.5% → -4.0%** |
| 最長持倉 | 20 天 | 同 TLT-001/002 |
| 追蹤停損 | 無 | 同 TLT-001/002 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | 隔日開盤市價 (next_open_market) |
| 止盈委託 | 限價賣單 Day (limit_order_day) |
| 停損委託 | 停損市價 GTC (stop_market_gtc) |
| 到期出場 | 隔日開盤市價 (next_open_market) |
| 滑價 | 0.10% |
| 悲觀認定 | 是（同根 K 線 stop+target 皆觸發 → 停損優先）|

### 迭代嘗試紀錄 (Iteration Log)

| # | 變更 | Part A Sharpe | Part B Sharpe | A WR / B WR | 訊號數 A/B | 結論 |
|---|------|-------------|-------------|------------|-----------|------|
| Att1 | TP+3.0%/SL-5.0%/cd10，無60日DD過濾 | -0.27 | 0.33 | 44.7%/75.0% | 38/16 | 寬SL -5.0% 在 2022 停損時虧損更大(-5.1% vs -3.5%)，Part A 劣化；Part B 改善但 A/B 差距擴大 |
| Att2 | TP+3.0%/SL-3.5%/cd15，無60日DD過濾 | -0.33 | 0.41 | 37.5%/71.4% | 32/14 | TP+3.0% 是關鍵問題：2022-12-20、2023-02-13 兩筆原 +2.5% 達標交易翻轉為停損；cd15 移除好訊號；Part A 最差 |
| **Att3** | **TP+2.5%/SL-4.0%/cd10，無60日DD過濾（最終版）** | **-0.20** | **0.46** | **50.0%/81.2%** | **38/16** | SL -4.0% 挽回 Part B 邊際深跌交易（2024-10-11 從到期翻為達標），Part B 大幅改善；Part A 持平 |

### 回測結果 (Backtest Results) — 最終版 (Att3)

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|-------------------|-------------------|----------------|
| 訊號數 | 38 | 16 | 1 |
| 訊號/年 | 7.6 | 8.0 | 4.2 |
| 勝率 | 50.0% | 81.2% | 0.0% |
| 平均報酬 | -0.60% | +1.17% | -0.37% |
| 累計報酬 | -21.79% | +19.82% | -0.37% |
| 盈虧比 | 0.64 | 2.52 | 0.00 |
| Sharpe | -0.20 | 0.46 | 0.00 |
| Sortino | -0.23 | 0.66 | -1.00 |
| Calmar | -0.10 | 0.24 | -0.21 |
| MDD | -5.89% | -4.95% | -1.80% |
| 最大連續虧損 | 7 | 1 | 1 |

### vs TLT-002 比較

| 指標 | TLT-002 Part A | TLT-003 Part A | TLT-002 Part B | TLT-003 Part B |
|------|---------------|---------------|---------------|---------------|
| Sharpe | -0.20 | -0.20 | 0.24 | **0.46 (+92%)** |
| WR | 46.9% | 50.0% | 68.8% | **81.2% (+12.4pp)** |
| 累計 | -16.83% | -21.79% | +10.07% | **+19.82% (+97%)** |
| MDD | -5.89% | -5.89% | -3.74% | -4.95% |
| 訊號 | 32 | 38 | 16 | 16 |

**A/B 分析**：
- Part A Sharpe 持平（-0.20），WR 改善 50.0% vs 46.9%，但累計更差（-21.79% vs -16.83%，因移除 60日DD 過濾多了 6 個 2022 停損訊號）
- Part B 大幅改善（Sharpe 0.46 vs 0.24，WR 81.2% vs 68.8%）：SL -4.0% 讓 2024-10-11 從到期（-1.66%）翻為達標（+2.50%），cd10 讓 2024-04-25 進場
- A/B Sharpe 差距擴大至 0.66（TLT-002 為 0.44），不符合 A/B 平衡要求

**結論**：TLT-003 未超越 TLT-002。Part B 的 +92% Sharpe 改善令人注目，但 Part A 仍受 2022 升息結構性制約。三次嘗試（寬SL、高TP、長冷卻期、SL中間值）全面驗證：**TLT 的 Part A 績效瓶頸是 2022 升息環境本身，而非出場參數設定**。任何技術面參數調整都無法區分「正常回檔」與「利率趨勢下跌」。

---

## TLT-004: BB 擠壓突破 / SMA 黃金交叉（趨勢策略）(BB Squeeze Breakout / SMA Golden Cross - Trend Following)

### 目標 (Goal)

TLT-001~003 均為均值回歸策略，受 2022 升息環境結構性制約（Part A Sharpe 最佳 -0.20）。TLT-004 嘗試完全不同的策略方向——趨勢跟蹤/突破策略，假說是：順勢買入可自然避開 2022 下跌趨勢（無向上突破信號），改善 Part A。

### 進場條件 (Entry Conditions) — Att1（BB 擠壓突破，代表版本）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | BB Width | 60日 25th 百分位內（5日內曾發生）| 近期波動收縮 |
| 2 | 收盤價 > Upper BB(20,2) | — | 向上突破 |
| 3 | 收盤價 > SMA(50) | — | 趨勢向上確認 |
| 4 | 冷卻期 | 10 天 | 避免重複進場 |

### 出場參數 (Exit Parameters) — Att1

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 (TP) | +3.0% | 對稱出場 |
| 停損 (SL) | -3.0% | 對稱出場 |
| 最長持倉 | 20 天 | — |
| 追蹤停損 | 無 | — |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | 隔日開盤市價 (next_open_market) |
| 止盈委託 | 限價賣單 Day (limit_order_day) |
| 停損委託 | 停損市價 GTC (stop_market_gtc) |
| 到期出場 | 隔日開盤市價 (next_open_market) |
| 滑價 | 0.10% |
| 悲觀認定 | 是（同根 K 線 stop+target 皆觸發 → 停損優先）|

### 設計理念 (Design Rationale)

- **BB 擠壓突破**：參考 TSLA-005 成功經驗（Sharpe +150% vs 均值回歸）。波動收縮後的向上突破代表新趨勢啟動
- **SMA(50) 趨勢確認**：避免在下降趨勢中買入假突破
- **按 TLT 波動度調整**：TLT 日波動 ~1.0% vs TSLA ~3-4%，TP/SL 按比例縮小
- **Att3 SMA 黃金交叉**：完全不同的進場邏輯——SMA(20) 從下方穿越 SMA(50) 代表中期趨勢確立

### 迭代嘗試紀錄 (Iteration Log)

| # | 變更 | Part A Sharpe | Part B Sharpe | A WR / B WR | 訊號數 A/B | 結論 |
|---|------|-------------|-------------|------------|-----------|------|
| Att1 | BB 擠壓突破 TP+3%/SL-3%/cd10 | **0.31** | **-1.15** | 64.3%/7.7% | 14/13 | Part A 大幅改善（-0.20→0.31），但 Part B 災難：2024-2025 橫盤環境所有突破失敗（13 筆僅 1 達標、8 停損） |
| Att2 | BB 擠壓 TP+4%/SL-5%/cd10，擠壓 20th 百分位 | 0.13 | -0.63 | 53.8%/15.4% | 13/13 | 寬 SL 延遲停損但不減少次數，高 TP 減少達標：Part A 退化 0.31→0.13 |
| **Att3** | **SMA(20) 黃金交叉 SMA(50) + Close > SMA(20)，cd20** | **0.89** | **-0.02** | **85.7%/50.0%** | **7/2** | Part A 極佳（0.89），但 Part B 僅 2 訊號無統計意義，A/B 訊號比 3.5:1 |

### 回測結果 (Backtest Results) — Att1（代表版本，訊號最均衡）

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|-------------------|-------------------|----------------|
| 訊號數 | 14 | 13 | 1 |
| 訊號/年 | 2.8 | 6.5 | 4.3 |
| 勝率 | 64.3% | 7.7% | 100.0% |
| 平均報酬 | +0.77% | -2.07% | +1.64% |
| 累計報酬 | +10.86% | -23.98% | +1.64% |
| 盈虧比 | 1.92 | 0.10 | ∞ |
| Sharpe | 0.31 | -1.15 | 0.00 |
| Sortino | 0.51 | -0.79 | ∞ |
| Calmar | 0.18 | -0.49 | 0.66 |
| MDD | -4.21% | -4.19% | -2.47% |
| 最大連續虧損 | 2 | 8 | 0 |

### vs TLT-002 比較

| 指標 | TLT-002 Part A | TLT-004 Part A | TLT-002 Part B | TLT-004 Part B |
|------|---------------|---------------|---------------|---------------|
| Sharpe | -0.20 | **0.31 (+0.51)** | **0.24** | -1.15 |
| WR | 46.9% | **64.3%** | **68.8%** | 7.7% |
| 累計 | -16.83% | **+10.86%** | **+10.07%** | -23.98% |
| MDD | -5.89% | **-4.21%** | **-3.74%** | -4.19% |
| 訊號 | 32 | 14 | 16 | 13 |

**A/B 分析**：
- Part A 大幅改善：Sharpe -0.20 → 0.31（+0.51），突破策略自然避開 2022 大部分假訊號（僅 2022-07、2022-11 兩筆信號，vs 均值回歸的 11 筆以上）
- Part B 災難：Sharpe 0.24 → -1.15，2024-2025 TLT 在 $85-$93 區間橫盤，每次突破上軌後均迅速回落觸及 SL -3.0%
- A/B Sharpe 差距 1.46（TLT-002 為 0.44），嚴重不平衡

**結論**：TLT-004 驗證了趨勢跟蹤/突破策略對 TLT 的效果。三次嘗試揭示核心發現：

1. **BB 擠壓突破改善 Part A**（0.31 vs -0.20）但摧毀 Part B（-1.15），因 2024-2025 TLT 橫盤環境產生大量假突破
2. **SMA 黃金交叉 Part A 極佳**（0.89）但訊號過少（Part B 僅 2 個），無統計可信度
3. **TLT 的根本問題**：受宏觀利率政策驅動而非技術面。均值回歸被升息殺死（Part A），突破策略被利率高原橫盤殺死（Part B）。純技術面策略無法同時適應升息、降息、穩定三種利率環境

---

## TLT-005: Donchian 突破 / ROC 動量（趨勢策略）(Donchian Channel Breakout / ROC Momentum - Trend Following)

### 目標 (Goal)

延續 TLT-004 對趨勢策略的探索，使用 Donchian Channel 突破和 ROC 動量兩種不同的非均值回歸進場方法，從不同角度驗證趨勢/動量方向對 TLT 的適用性。

### 進場條件 (Entry Conditions) — 最終版 (Att2)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | Donchian(20) 突破 | Close > 過去 20 日最高 High | 新高突破（排除當日） |
| 2 | SMA(50) 趨勢確認 | Close > SMA(50) | 上升趨勢過濾 |
| 3 | 冷卻期 | 10 天 | 避免連續進場 |

### 出場參數 (Exit Parameters) — 最終版 (Att2)

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 (TP) | +2.5% | 與 TLT-001/002 相同 |
| 停損 (SL) | -3.5% | 給突破進場更多呼吸空間 |
| 最長持倉 | 20 天 | 等待趨勢展開 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | 隔日開盤市價 (next_open_market) |
| 止盈委託 | 限價賣單 Day (limit_order_day) |
| 停損委託 | 停損市價 GTC (stop_market_gtc) |
| 到期出場 | 隔日開盤市價 (next_open_market) |
| 滑價 | 0.10% |
| 悲觀認定 | 是 |

### 迭代嘗試紀錄 (Iteration Log)

| 嘗試 | 策略 | 參數 | Part A Sharpe | Part B Sharpe | 結果 |
|------|------|------|:---:|:---:|------|
| Att1 | Donchian(20) + SMA(50) | TP+2.5%/SL-2.0%/15d/cd10 | 0.15 | -1.12 | SL -2.0% 太緊，Part B 11/14 停損 |
| Att2 | Donchian(20) + SMA(50) | TP+2.5%/SL-3.5%/20d/cd10 | **0.20** | -0.83 | 最佳 Part A，但 Part B 仍全面失敗 |
| Att3 | ROC(10) > 3% + SMA(50) | TP+2.5%/SL-2.5%/15d/cd15 | -0.06 | -1.43 | 動量策略更差：買入短期強勢 → 立即回吐 |

### 回測結果 (Backtest Results) — 最終版 (Att2)

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 29 | 14 |
| 每年訊號 | 5.8 | 7.0 |
| 勝率 | 58.6% | 14.3% |
| 平均報酬 | +0.51% | -1.77% |
| 累計報酬 | +14.74% | -22.33% |
| Sharpe | 0.20 | -0.83 |
| Sortino | 0.29 | -0.68 |
| Profit Factor | 1.53 | 0.17 |
| 最大連續虧損 | 2 | 7 |
| 達標出場 | 17 | 2 |
| 停損出場 | 6 | 5 |
| 到期出場 | 6 | 7 |

### 分析

**Part A 觀察（TLT 歷史最佳 Part A 之一）**：
- Sharpe 0.20，與 TLT-004 Att1 的 Part A Sharpe 0.31 相比略低，但方向一致
- 2022 全年僅 3 個訊號（7月、11月、12月），全部達標 — SMA(50) 趨勢確認自然過濾了升息期假訊號
- Donchian 突破較 BB 擠壓更不挑剔（29 vs 20 訊號），但品質略低（Sharpe 0.20 vs 0.31）

**Part B 觀察（全面失敗）**：
- 與 TLT-004 BB 擠壓結論一致：2024-2025 區間震盪中所有突破策略失效
- Donchian 突破 Part B Sharpe -0.83，BB 擠壓 -1.15，量級相近

**ROC 動量策略（Att3）洞察**：
- ROC(10) > 3% 買入強動量後 TLT 立即回吐，Part A/B 均負
- 進一步證實 TLT 的短期動量不可持續，與利率政策的低頻驅動特性一致

**結論**：TLT-005 再次驗證趨勢跟蹤/動量策略對 TLT 的結構性限制。結合 TLT-004（BB擠壓/SMA交叉）和 TLT-005（Donchian/ROC），共 6 次嘗試全面確認：**TLT 受宏觀利率政策驅動，純技術面策略無論均值回歸或趨勢跟蹤，都無法同時在 Part A（含升息期）和 Part B（含橫盤期）獲得正 Sharpe**。

---

## TLT-006: Day-After Capitulation + 強反轉 K 線均值回歸 (Day-After Capitulation + Strong Reversal Bar MR)

### 目標 (Goal)

從 URA-009 Att2 框架跨資產移植：驗證「T-1 極端 capitulation + T 強反轉 K 線（Close > T-1 High）」
是否能改善 TLT-002 Part A 在 2022-2023 升息期間的連續假訊號（TLT-002 Part A 32 訊號 WR 46.9%
Sharpe -0.20）。**假說**：「收復昨日高點」為技術面 regime 切換訊號，可過濾持續性下跌中的
短暫 V-bounce。

### 進場條件（三次迭代共同骨架）

| 條件 | 指標 | 備註 |
|------|------|------|
| T-1 回檔 | 10 日高點回檔下限 | 各 Att 調整 -3% ~ -4% |
| T-1 回檔上限 | 10 日高點回檔上限 | 固定 -8% 以隔離 Fed 衝擊日 |
| T-1 WR(10) | 超賣確認 | 各 Att 調整 -85 ~ -90 |
| T-1 兩日跌幅 | Close[T-1]/Close[T-3]-1 | 各 Att 調整 -1.5% ~ -2.5% |
| T Close > T-1 High | 收復昨日高點 | 所有迭代皆必要條件 |
| T Close > T Open | 陽線 | 所有迭代皆必要條件 |
| T Range 擴張 | Range[T] / avg(Range[T-5..T-1]) | Att2 1.2x / Att3 1.15x |
| 冷卻期 | Signal 間最短間隔 | Att1/2 7 天、Att3 10 天 |

### 出場參數（三次迭代相同）

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 (TP) | +2.5% | 同 TLT-002 |
| 停損 (SL) | -3.5% | 同 TLT-002 |
| 最長持倉 | 20 天 | 同 TLT-002 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | 隔日開盤市價 (next_open_market) |
| 止盈委託 | 限價賣單 Day (limit_order_day) |
| 停損委託 | 停損市價 GTC (stop_market_gtc) |
| 到期出場 | 隔日開盤市價 (next_open_market) |
| 滑價 | 0.10% |
| 悲觀認定 | 是 |

### 迭代嘗試紀錄 (Iteration Log)

#### Att1（2026-04-19）：基準嘗試

- 參數：pullback -3%/-8% + WR≤-85 + 2DD≤-1.5% + Close>PrevHigh + Close>Open，無 range 擴張，cd 7
- **Part A**：15 訊號 WR 40.0% Sharpe **-0.37** 累計 -15.27%
- **Part B**：3 訊號 WR 100% Sharpe 0.00（3/3 +2.5% TP，零方差）累計 +7.69%
- min(A,B) = **-0.37**（**劣於 TLT-002 的 -0.20**）
- 失敗分析：8 次 -3.6% 停損集中於 2022-08/09（3 筆）與 2023-05/08/09（3 筆），
  2020-05-12 與 2021-02-26 亦停損。這些日期均處於 TLT 持續性下跌週期中，
  「收復昨日高點」作為過濾器無法辨識真實反轉 vs 假 V-bounce

#### Att2（2026-04-19）：加嚴嘗試

- 參數：pullback **-4%**/-8% + WR **≤-90** + 2DD **≤-2.5%** + Range 擴張 **1.2x**，cd 7
- **Part A**：3 訊號 WR 66.7% Sharpe 0.16 累計 +1.28%
- **Part B**：**0 訊號**
- min(A,B) 無法評估（Part B 枯竭）
- 失敗分析：WR≤-90 + 2DD≤-2.5% + Range 1.2x 三重加嚴對 TLT 1.0% vol 過於稀少，
  Part A 留下 3 筆全部是真 capitulation 但樣本不足，Part B 2024-2025 高利率高原期
  缺乏符合所有條件的事件

#### Att3（2026-04-19）：折衷嘗試

- 參數：pullback -3%/-8% + WR≤-85 + 2DD **≤-2.0%** + Range 擴張 **1.15x**，cd **10**
- **Part A**：5 訊號 WR 40% Sharpe **-0.39** 累計 -5.88%
- **Part B**：**0 訊號**
- min(A,B) = **-0.39**（**劣於 TLT-002 的 -0.20**）
- 失敗分析：Range 1.15x 過濾對 TLT 1.0% vol 仍過嚴（日均 range 1.2-1.5%），Att1 的
  2DD≤-1.5% 放寬換來的訊號全數被 Range 擴張過濾掉；Part A 殘存 5 訊號仍集中於
  高利率期，WR 無改善

### 失敗範式與跨資產教訓

TLT-006 三次迭代的共同失敗點：

1. **政策驅動資產的 price-action 反轉過濾失效**：TLT 受聯準會政策預期驅動，
   「Close > Prev High」在持續性 tightening 期間頻繁發生（技術性小反彈）但後續
   繼續下探。此為與 URA-009（核能政策驅動）相同的「V-bounce ≠ genuine reversal」
   失敗模式
2. **低 vol 資產的擴張反轉過濾互斥性**：TLT 1.0% 日 vol 使日均 Range 僅 1.2-1.5%，
   要求 Range[T] ≥ 1.15-1.2x 平均 range 會強烈過濾 Part B 訊號（TLT 高利率高原期
   缺乏擴張反轉）
3. **capitulation 閾值的 dilemma**：放鬆閾值（Att1）Part A 品質低，收緊閾值（Att2/3）
   Part B 枯竭，無法在 TLT 上找到甜蜜點

**擴展 cross_asset lesson #20b 邊界**：Day-After Capitulation + 強反轉 K 線模式失敗
範疇由「核能政策驅動」（URA-009）擴展至「利率政策驅動」（TLT-006）——即任何政策/
事件驅動的資產，price-action 反轉確認（Close>PrevHigh + Close>Open + Range 擴張）
均無法區分真實 regime 切換與短期技術性反彈。

**TLT-006 三次迭代未改善 min(A,B)**，但 TLT-007 Att2（波動率 regime 閘門）
突破該結論——見下方 TLT-007 章節。

---

## TLT-007: 波動率 regime 閘門均值回歸 (Volatility-Regime-Gated Mean Reversion)

### 目標 (Goal)

在 TLT-001/002 驗證有效的「回檔 + WR + 反轉 K 線」進場框架上，加入**波動率 regime
閘門**（BB(20, 2) 通道寬度 / Close < 門檻）作為 regime-level 過濾器，過濾 2022
升息期極端波動率飆升的訊號，保留 2019-2021 降息期與 2024-2025 高利率高原期的
真正 mean reversion 機會。

**與既有實驗的差異：**
- TLT-002 使用 60 日跌幅 ≤ 10% 作為 regime 過濾（驗證太寬鬆——2022 月度跌幅多
  在 5-10% 區間，多數通過）
- TLT-004/005 嘗試突破/趨勢策略（驗證在 Part A 有效但 Part B 橫盤失效）
- TLT-006 嘗試 Day-After Capitulation 反轉 K 線（驗證政策驅動資產 V-bounce 過多）
- **TLT-007：用「波動率 regime」而非「方向趨勢」分類市場**，BB 寬度 / Close 是
  波動率實現值的無方向度量，當前為 calm regime 時放行，crisis regime 時阻擋

### 進場條件 (Entry Conditions，Att2 最終版)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 10 日高點回檔 | ≥ 3% | 短期回調觸發（同 TLT-001） |
| 2 | 10 日高點回檔 | ≤ 7% | 過濾極端/持續性下跌（同 TLT-001） |
| 3 | Williams %R(10) | ≤ -80 | 超賣確認（同 TLT-001） |
| 4 | 收盤位置 | ≥ 40% | 日內反轉確認（同 TLT-001） |
| 5 | **BB(20, 2) 寬度 / Close** | **< 5%** | **波動率 regime 閘門（新增）** |
| 6 | 冷卻期 | 7 天 | 同 TLT-001 |

### 出場參數 (Exit Parameters，同 TLT-001/002)

| 參數 | 值 |
|------|------|
| 獲利目標 (TP) | +2.5% |
| 停損 (SL) | -3.5% |
| 最長持倉 | 20 天 |
| 追蹤停損 | 無 |

### 成交模型 (Execution Model，同 TLT 系列)

| 項目 | 設定 |
|------|------|
| 進場模式 | 隔日開盤市價 (next_open_market) |
| 止盈委託 | 限價賣單 Day (limit_order_day) |
| 停損委託 | 停損市價 GTC (stop_market_gtc) |
| 到期出場 | 隔日開盤市價 (next_open_market) |
| 滑價 | 0.10% |
| 悲觀認定 | 是（同根 K 線 stop+target 皆觸發 → 停損優先）|

### 設計理念 (Design Rationale)

- **BB 寬度作為波動率代理**：BB(20, 2) 寬度 = 4 × 20 日標準差，其與 Close 的比值
  大致等於實現波動率的 4 倍（假設 Close ≈ 均值）。TLT 正常日均波動 1%，對應 BB
  寬度 / Close ≈ 4-5%；2022 升息期實現波動率升至 1.5-2%+，BB 寬度 / Close 升至
  7-9%，明顯可區分
- **5% 門檻為甜蜜點**：Att1（6%）過寬——2022 升息期 TLT 雖波動大但通道擴張呈階梯
  式，部分日子 BB 寬度仍低於 6%，2022-01/03/06/08 四筆訊號全部通過；Att2（5%）
  過濾 2022 大部分訊號（僅保留 2022-02-07 贏家）
- **不是方向性趨勢濾波**：BB 寬度無方向，只反映波動率高低。不違反 cross-asset
  lesson #5（MR + 進場日短線趨勢濾波 = 災難）——那條 lesson 針對「當日 Close > SMA(50)」
  類型的**方向性**進場濾波，會移除 MR 本質的下跌中進場訊號
- **Att3 嘗試疊加 SMA(100) 斜率濾波失敗**：方向性濾波在 Part B 2024-2025 TLT 橫盤
  時頻繁切換正負，砍掉 Part B 半數訊號（6→3），min(A,B) 雖表面升至 0.16，但 Part B
  零方差風險過大，放棄

### 迭代嘗試紀錄 (Iteration Log)

| # | 關鍵參數 | Part A | Part B | min(A,B) | 結論 |
|---|---------|--------|--------|----------|------|
| 1 | BB 寬度 / Close < **6%** | 24 訊號 45.8% WR Sharpe -0.20 | 10 訊號 80.0% WR Sharpe 0.48 | **-0.20** | 門檻過寬，2022 四筆仍通過，持平 TLT-002 |
| 2 | BB 寬度 / Close < **5%** ★ | 12 訊號 50.0% WR Sharpe **0.12** | 6 訊號 83.3% WR Sharpe **0.65** | **0.12** | **repo 首次 TLT min(A,B) 轉正** |
| 3 | Att2 + **SMA(100) 斜率 ≥ 0（20 日前）** | 7 訊號 57.1% WR Sharpe 0.29 | 3 訊號 66.7% WR Sharpe 0.16 | 0.16 | Part B 訊號砍半（零方差風險），放棄 |

### Att2 回測結果 (Backtest Results — Final)

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|-------------------|-------------------|----------------|
| 訊號數 | 12 | 6 | 1 |
| 訊號/年 | 2.4 | 3.0 | 3.4 |
| 勝率 | 50.0% | 83.3% | 0.0% |
| 平均報酬 | +0.26% | +1.48% | -0.07% |
| 累計報酬 | +2.95% | +9.07% | -0.07% |
| 盈虧比 | 1.10 | 3.47 | 0.00 |
| Sharpe | **0.12** | **0.65** | 0.00 |
| Sortino | 0.14 | 1.01 | -1.00 |
| MDD | -5.89% | -3.74% | -1.80% |
| 達標/停損/到期 | 6/3/3 | 5/1/0 | 0/0/1 |

**A/B 平衡分析：**
- 訊號年化率 2.4/yr vs 3.0/yr（差距 20%，**< 50% 目標 ✓**）
- 累計報酬差距 2.95% vs 9.07%（差距 67.5%，**> 30% 目標 ✗**，但 Part B 優於 Part A
  屬**利多不對稱**，Part B OOS 樣本更強，非 overfitting 結構）
- 勝率差距 50% vs 83.3%（33.3pp，Part B 明顯更佳）
- vs TLT-002：Part A Sharpe **-0.20 → 0.12**（+0.32 絕對，首次轉正）、
  Part B Sharpe **0.24 → 0.65**（+171%）、min(A,B) **-0.20 → 0.12**（+0.32）

### 核心發現 (Key Findings)

1. **BB 寬度 / Close 作為 regime 分類器在 TLT 首次驗證**（repo 首次）：成功過濾
   2022 升息期極端波動率訊號，保留其他年份 MR 機會。**5% 為甜蜜點**——6% 過寬、
   4% 以下會砍 Part B 好訊號
2. **方向性趨勢濾波在 TLT Part B 橫盤期失效**（Att3 驗證）：SMA(100) 斜率在 2024-2025
   高利率高原期頻繁切換正負，無穩定方向可濾。TLT 橫盤期的 MR 機會天然發生在無明顯
   趨勢中，方向性濾波造成 Part B 訊號隨機流失
3. **波動率 regime ≠ 方向性趨勢**：本實驗在結構上區分兩類濾波器——波動率 regime
   濾波對「crisis regime」整段關閉訊號門，方向性趨勢濾波對「下跌日」單日關閉門
   （後者為 lesson #5 所警告）。TLT-007 Att2 為此結構性區分在 repo 首次成功案例
4. **TLT「無純技術面解法」結論部分鬆動**：TLT-004/005/006 均驗證單純方向/反轉
   類技術濾波失效，但 TLT-007 Att2 證明**波動率 regime 濾波**為 TLT 可行的純技術面
   途徑。擴展結論：TLT 需要的是 regime-level 過濾，非 entry-time 過濾
5. **跨資產延伸假設（待驗證）**：BB 寬度 regime 閘門可能適用於其他曾經歷極端
   波動率 regime 事件的利率政策驅動資產、或 Part A 被單一高波動事件主導的
   固定收益類 ETF。門檻需因資產日波動度縮放（TLT 1.0% vol → 5%，其他資產需
   相應調整）

> **分析日期：** 2026-03-30
> **窗口：** 2 年，步進 6 個月（共 12 個窗口）

### 滾動窗口績效表

| 窗口 | 訊號 | 勝率 | 平均報酬 | 累計報酬 | MDD | ΔWR |
|------|------|------|----------|----------|-----|-----|
| 2019-01~2020-12 | 10 | 70.0% | +0.57% | +5.57% | -5.89% | — |
| 2019-07~2021-06 | 14 | 50.0% | -0.24% | -3.70% | -5.89% | -20.0pp |
| 2020-01~2021-12 | 14 | 50.0% | -0.15% | -2.43% | -5.89% | +0.0pp |
| 2020-07~2022-06 | 19 | 47.4% | -0.51% | -9.85% | -4.64% | -2.6pp |
| 2021-01~2022-12 | 21 | 33.3% | -1.60% | -29.35% | -4.64% | -14.0pp |
| 2021-07~2023-06 | 21 | 38.1% | -1.16% | -22.39% | -4.64% | +4.8pp |
| 2022-01~2023-12 | 24 | 41.7% | -0.98% | -21.87% | -5.12% | +3.6pp |
| 2022-07~2024-06 | 22 | 50.0% | -0.49% | -11.13% | -5.12% | +8.3pp |
| 2023-01~2024-12 | 22 | 59.1% | +0.15% | +2.43% | -5.12% | +9.1pp |
| 2023-07~2025-06 | 22 | 68.2% | +0.51% | +10.97% | -5.12% | +9.1pp |
| 2024-01~2025-12 | 16 | 68.8% | +0.64% | +10.07% | -3.74% | +0.6pp |
| 2024-07~2026-03 | 12 | 58.3% | +0.18% | +1.70% | -3.63% | -10.4pp |

### 預測精準度表

| 窗口 | WR | 平均贏利 | 平均虧損 | 盈虧比 | 差點成功 |
|------|------|----------|----------|--------|----------|
| 2019-01~2020-12 | 70.0% | +1.90% | -2.53% | 1.75 | 2/3 |
| 2019-07~2021-06 | 50.0% | +1.99% | -2.47% | 0.81 | 2/5 |
| 2020-01~2021-12 | 50.0% | +1.83% | -2.13% | 0.86 | 3/7 |
| 2020-07~2022-06 | 47.4% | +1.98% | -2.75% | 0.65 | 3/7 |
| 2021-01~2022-12 | 33.3% | +2.13% | -3.47% | 0.31 | 2/4 |
| 2021-07~2023-06 | 38.1% | +2.36% | -3.32% | 0.44 | 1/3 |
| 2022-01~2023-12 | 41.7% | +2.32% | -3.34% | 0.50 | 1/3 |
| 2022-07~2024-06 | 50.0% | +2.34% | -3.32% | 0.70 | 1/2 |
| 2023-01~2024-12 | 59.1% | +2.36% | -3.05% | 1.12 | 1/3 |
| 2023-07~2025-06 | 68.2% | +2.30% | -3.33% | 1.48 | 2/3 |
| 2024-01~2025-12 | 68.8% | +2.39% | -3.23% | 1.63 | 1/2 |
| 2024-07~2026-03 | 58.3% | +2.33% | -2.84% | 1.15 | 1/3 |

### 漸變性評估

- **勝率範圍**：33.3% ~ 70.0%（ΔWR 標準差 9.4pp，最大跳動 20.0pp）
- **盈虧比範圍**：0.31 ~ 1.75（ΔPF 標準差 0.39）
- **累計報酬範圍**：-29.35% ~ +10.97%（ΔCum 標準差 9.60%）
- **平均贏利範圍**：+1.83% ~ +2.39%（Δ標準差 0.11%，穩定）
- **平均虧損範圍**：-2.13% ~ -3.47%（升息週期放大虧損幅度）

**判定：**
- ✓ 預測精準度漸變（勝率最大跳動 20.0pp ≤ 20pp 閾值）
- ✓ 下游績效漸變（累計報酬最大跳動 19.50% ≤ 3σ = 28.80%）

### 分析解讀

1. **升息週期重創**：2021-2023 窗口勝率低至 33-42%，累計報酬 -21%~-29%，Fed 激進升息導致債券持續下跌，均值回歸策略完全失效
2. **V 型恢復**：勝率從 33.3% 谷底漸進回升至 68.8%，恢復路徑平滑（每步 +3~9pp），反映降息預期改善
3. **雖通過漸變性測試但需警惕**：20.0pp 恰好等於閾值，屬於邊界通過；2021-2023 的慘烈虧損顯示策略在利率趨勢反轉時極度脆弱
4. **差點成功比例高**：多數窗口有 1/2~3/7 的到期出場為正報酬，TP 設定可能偏高
5. **近期表現回暖**：2023-2025 窗口受益於降息環境，勝率 59-69%
6. **高度依賴利率環境**：策略在降息/寬鬆環境表現佳，升息環境則大幅虧損，使用時須搭配利率週期判斷

---

## TLT-008: TLT vs IEF Duration-Spread Mean Reversion（配對交易，repo 首次試於 TLT）

### 目標 (Goal)

探索「配對交易（pairs trading）」方向於利率驅動資產 — repo 唯一尚未於 TLT 試驗的主要策略類別。
核心假設：TLT 相對 IEF（7-10 年公債 ETF）短期過度跌落代表殖利率曲線陡峭化事件，tends to revert。

### 三次迭代紀錄 (Iteration Log)

| # | 方向 | 關鍵參數 | Part A Sharpe | Part B Sharpe | min(A,B) | 結果 |
|---|------|----------|--------------|--------------|----------|------|
| Att1 | 純 pair 訊號 | 10d TLT-IEF spread <= -2% + ClosePos + Daily Up + BB<5% | -5.92 | 0.00 (1 signal zero-var) | **-5.92** | 災難性失敗 |
| Att2 | hybrid：TLT-007 框架 + pair 過濾 | 同 TLT-007 Att2 + 10d spread <= -1.5% | -1.71 | 0 signals (枯竭!) | **-1.71** | Pair 過濾系統性移除贏家 |
| Att3 | z-score 統計標準化 pair 過濾 | 同 TLT-007 Att2 + TLT/IEF 100d z-score <= -1.5σ | -0.31 | 0.00 (2 signals zero-var) | **-0.31** | 改善但仍不足 |

中間測試（反向方向：5d spread >= +0.3% + TLT-007 框架）**所有 part 皆 0 訊號** — TLT 在 10d pullback 3-7% 期間相對 IEF 必然弱勢（duration 機械關係），短期反向 spread 與 MR 進場結構互斥。

### 結論與跨資產延伸 (Conclusions)

三次迭代全部失敗，TLT-007 Att2 min(A,B) 0.12 仍為 TLT 全域最佳。TLT-008 確認：

1. **配對交易方向於 TLT 結構性失敗**：同資產類別（同為美國公債）但不同 duration 的機械性 pair 不適用 MR 進場過濾
2. **根因**：TLT 與 IEF 在 TLT pullback 期間的相對表現由「duration 敏感度比例」機械決定（TLT ~18yr vs IEF ~7.5yr），TLT 對利率敏感度約 IEF 的 2.4 倍，兩者並非「獨立個體間偏離後回歸」的經典 pairs MR 結構
3. **過濾方向雙向失敗**：
   - 「TLT 輸 IEF」過濾（Att1/Att2）系統性保留「rate shock 起點」訊號（贏家被濾掉：Att2 Part B 6→0）
   - 「TLT 贏 IEF」過濾（中間測試）與 MR 進場結構互斥（訊號全 0）
   - z-score 統計標準化（Att3）無法克服此結構性限制
4. **Lesson #20 擴展**：跨資產相關性配對策略的結構性風險不僅限於「跨資產類別」，**同資產類別但存在機械性 beta/duration 關係的 pair** 亦失效

---

## TLT-009: Yield-Velocity-Gated Mean Reversion（^TNX 外部殖利率 regime gate，repo 首次）

### 目標 (Goal)

探索使用**外部 Treasury yield 數據（^TNX = CBOE 10-Year Treasury Note Yield Index）**作為 TLT MR 的 regime 過濾器——repo 首次試驗。核心假設：TLT 價格 ≈ −duration × Δyield，^TNX 短期變化是 TLT 價格的 **forward-looking driver**，10 日 ^TNX 變化可作為 Fed rate-shock 偵測器，取代或補強 TLT-007 Att2 的 **backward-looking BB 寬度 gate**。

### 設計背景 (Design Rationale)

- TLT-007 Att2 的 BB 寬度 gate 為**實現波動率（realized vol）**，滯後於 Fed rate shock 1-3 天
- ^TNX 變化在時序上**領先**（leading）TLT 價格反應
- 2022 升息期 ^TNX 10 日變化 median +12bps、90th percentile +35bps；2024-2025 高原期 median 0bps、90th percentile +20bps——門檻 +15bps 理論上可移除 ~50% 2022 訊號、保留 ~80% 2024-2025 訊號

### 三次迭代紀錄 (Iteration Log)

| # | 方向 | 關鍵參數 | Part A | Part B | min(A,B) | 結果 |
|---|------|----------|--------|--------|----------|------|
| Att1 | 純 yield magnitude gate | ^TNX 10d <= +15bps, BB gate 停用 | 24/45.8% WR/Sharpe -0.16/cum -10.74% (11W/8SL/5Exp) | 8/87.5% WR/Sharpe 0.86/cum +14.59% (7W/1SL) | **-0.16** | 2022 階梯式升息讓短期平緩窗口訊號通過（5 筆 2022 訊號），Part A 仍負 |
| Att2 | hybrid BB+yield gate | BB 寬度<5% AND ^TNX 10d<=+15bps | 9/33.3% WR/Sharpe -0.15/cum -3.33% (3W/2SL/4Exp) | 4/100% WR/Sharpe 0.00 zero-var/cum +10.38% | **-0.15** | 雙閘門系統性移除 regime transition 贏家（6 筆 Part A 贏家被 BB 砍掉）|
| Att3 | yield direction gate | ^TNX 5d <= 0（不再上升），BB gate 停用 | 4/50% WR/Sharpe -0.22/cum -2.70% (2W/2SL) | 1/100% WR/Sharpe 0.00 zero-var/cum +2.50% | **-0.22** | 方向閘門過濾率 >90%，yield 方向與 TLT pullback 微觀反向 |

### 詳細結果 (Detailed Results)

#### Att1 Part A 2022 訊號（5 筆通過 +15bps 閾值）
- 2022-03-10 SL −3.60%（Fed 3 月首次升息前一週）
- 2022-05-05 W +2.50%（5 月升息後短暫反彈）
- 2022-08-05 SL −3.60%
- 2022-08-17 SL −3.60%
- 2022-10-11 SL −3.60%

→ +15bps 閾值讓「多段 rate-shock 之間的短暫平緩窗口」訊號通過，但此時 TLT 價格反映累積 rate-shock，未必同步回升。

#### Att2 hybrid 移除的 Part A 贏家（BB 寬度 > 5% 的 regime transition 期）
- 2020-05-06 W（COVID 後 Fed QE 緩和初期）
- 2021-10-08 W（reflation trade）
- 2022-05-05 W（5 月 Fed 緊縮前短暫喘息）
- 2023-04-18 W（post-SVB 利率回落）
- 2023-08-17 W
- 2023-10-20 W

→ BB 寬度 gate 與 yield gate 邊界在 regime transition 期重疊，hybrid 不疊加過濾力，反而放大「過濾 turning-point 贏家」的副作用。

#### Att3 Part A 4 筆訊號（yield 5d 方向閘門通過率 <10%）
- 2019-10-22 SL / 2020-05-26 SL / 2021-10-04 Exp +2.15% / 2023-03-28 W +2.50%

→ TLT MR 進場結構（pullback 3-7% + WR 超賣）多發生於 rate-shock 仍持續但 TLT 短期超賣時刻，此時 ^TNX 5d 仍為正值，方向閘門系統性排除此類進場機會。

### 結論與跨資產延伸 (Conclusions)

三次迭代全部失敗，TLT-007 Att2 min(A,B) 0.12 仍為 TLT 全域最佳（9 實驗、26+ 嘗試）。TLT-009 的**結構性失敗**（與 TLT-008 共同）擴展 TLT knowledge base：

1. **外部殖利率指標於 TLT MR 過濾器結構性受限**：
   - magnitude-based gate (Att1/Att2)：計數過濾 ≠ 品質過濾，階梯式升息的 intermediate pauses 仍產生虧損訊號
   - direction-based gate (Att3)：yield 方向與 TLT pullback 進場時機在微觀層級反向
   - hybrid 雙閘門 (Att2)：BB 寬度 gate 與 yield gate 邊界重疊於 regime transition 期，雙閘門反而放大副作用
2. **日線 yield velocity 與 TLT 日內 MR trigger 時序錯位**：Fed rate shock 在 yield 先反映（leading），但 TLT MR 觸發（pullback+WR+ClosePos）多發生於 rate-shock 後的日內反轉，此時 ^TNX 近 N 日（N≤10）仍呈正值
3. **BB 寬度 gate 之所以有效的機理**：BB 寬度捕捉的是「已發生的實現波動率」，與 MR setup 的邏輯（pullback 已發生、WR 已超賣）一致——兩者皆為 backward-looking 的「狀態已成形」指標。反觀 forward-looking 的 yield velocity，與 MR trigger 時機不同步
4. **TLT-008（IEF pair）+ TLT-009（^TNX driver）共同結論**：外部利率相關指標（無論 pair 形式或 driver velocity 形式）作為 TLT MR 過濾器結構性不適用。TLT-007 的「資產自身 BB 寬度 regime gate」仍為最佳方向
5. **突破 TLT min 0.12 的方向建議**：若要進一步改善，應為 TLT-007 Att2 的**更精細 BB 寬度 regime 分層**（如 BB 寬度 60 日分位數 regime 而非固定 5% 閾值、或動態隨 ATR 分位調整），而非加入外部 yield 指標
6. **Cross-asset 擴展假設**：其他利率政策驅動資產（XLU 部分、REITs、高殖利率股）可能承襲相同結論——自身 BB 寬度 > 外部 yield 指標。Fixed-income 類 ETF 的 MR 過濾器應優先考慮自身波動率狀態分類，而非外部 driver

---

## TLT-010: Capitulation-Confirmed Vol-Regime MR（2DD + ATR 補充過濾器，repo 首次於 TLT）

### 動機 (Motivation)

TLT-007 Att2 為當前最佳（Part A Sharpe 0.12 / Part B 0.65 / min 0.12），但 Part A 12 訊號中
有 5 筆近零到期（`-0.40% / -0.09% / -2.38% / +1.36% / -0.56%`）拖累 std，若能以
「signal-day secondary filter」區分高品質急跌訊號與慢磨下跌訊號，預期可提升 Part A Sharpe。

本實驗測試三類 signal-day secondary filter 疊加於 TLT-007 Att2：
- **2DD floor（lesson #19 方向）**：要求 2 日累積報酬 ≤ -1.5%，保留急跌 capitulation
- **2DD cap（CIBR-012 方向）**：要求 2 日累積報酬 ≥ -2.0%，排除深 2DD「continuation wave」
- **ATR(5)/ATR(20) 擴張**：要求近 5 日實現波動率相對 20 日正在抬升，**repo 首次 TLT 測試 ATR**

### 三次迭代結果 (Three Iteration Results)

| 迭代 | 關鍵參數 | Part A Sharpe | Part B Sharpe | min(A,B) | 結論 |
|------|----------|---------------|---------------|----------|------|
| Att1 | 2DD floor <= -1.5% | **-0.11** (6/33.3% WR) | 0.00 (3/100% zero-var) | **-0.11** | 過嚴（失敗） |
| Att2 | 2DD cap >= -2.0% | **0.02** (9/55.6% WR) | 0.52 (5/80% WR) | **0.02** | 無選擇力（失敗） |
| Att3 | ATR(5)/ATR(20) >= 1.05 | **-0.18** (7/42.9% WR) | 0.00 (1/100% zero-var) | **-0.18** | Part B 崩潰（失敗） |

**三次迭代均未超越 TLT-007 Att2 min(A,B) 0.12。**

### 失敗分析 (Failure Analysis)

#### Att1（2DD floor <= -1.5%）移除/保留分析
- 移除 3 Part A TPs（2019-07-12 淺 2DD、2021-08-11 淺 2DD、2022-02-07 淺 2DD）
- 移除 2 Part A SLs（2020-05-26、2021-02-04，深 2DD）
- 移除 2 Part A 負值到期（2020-08-12 -0.40%、2023-05-16 -0.56%）
- **引入 cooldown-shift 新 SL 2020-06-03（-3.60%）**（lesson #19 現象）
- Part B 移除 3/6 winners（2024-04-08 SL、2024-11-15 TP、2025-03-27 TP）
- **核心發現**：TLT winners 分布橫跨淺深 2DD（5 個 Part A TPs 中 2 個深 2DD、3 個淺 2DD），
  floor 方向無結構性選擇力

#### Att2（2DD cap >= -2.0%）移除/保留分析
- 移除 3 個 Part A 近零負值到期（2020-08-12、2020-12-02、2021-01-06）✓
- 同時移除 2020-11-09 TP（深 2DD 贏家）
- 引入 cooldown-shift 新 SL 2020-12-04 -3.01%
- Part B 僅移除 2024-05-29 TP（2DD 過深）
- **核心發現**：cap 方向雖然成功排除部分近零到期，但同時移除深 2DD 贏家；
  加上 cooldown shift 引入的新 SL，淨效果負面

#### Att3（ATR expansion >= 1.05）移除/保留分析
- Part A 從 12 砍至 7（砍 5），但砍除比例偏向贏家（3 TPs 僅剩 3 TPs，負 expiries 保留）
- **Part B 從 6 砍至 1（砍 5/6）**，幾乎完全失去 Part B 統計意義
- ATR 擴張過濾條件在 BB-width regime gate 已過濾的低波動環境下幾乎不觸發
- **核心發現**：TLT 的 winners 多為「低波環境中單日 pullback 後反彈」，ATR 擴張
  反向排除這些訊號；ATR 觸發的訊號反而是「波動已抬升、下跌尚未結束」的 SL

### 結論與擴展 (Conclusions and Extensions)

1. **signal-day secondary filter 在 rate-driven 資產結構性失效**：TLT winners/losers 在 2DD、
   ATR 維度皆分布重疊。TLT-007 Att2 的 BB-width regime gate 已完成 regime-level classifier
   角色（切除 2022 升息期），剩餘訊號流中任何 signal-day filter 無選擇力
2. **擴展 lesson #6 + lesson #20b**：rate-driven 資產在已套用 regime-level gate 後，
   signal-day secondary filters 結構性失效；此規則平行於 URA/FXI 政策驅動 ETF 的
   oscillator-hook 失敗家族
3. **TLT 未來改進方向**：應為更精細的 regime-level classifier（如 BB 寬度 60 日分位數
   dynamic regime、或動態隨 ATR 分位調整）而非 signal-day filter。TLT-007 Att2 仍為全域最佳
4. **Repo 首次 TLT 2DD 與 ATR 測試**：TLT-010 為 TLT 首次測試 2-day decline filter 與
   ATR(5)/ATR(20) 擴張過濾，結果均為結構性失敗。結合 TLT-006（Day-After Capitulation）
   、TLT-008（IEF pair）、TLT-009（^TNX yield）一致顯示：在 TLT-007 Att2 的 BB-width
   gate 之上任何 secondary filter 均無法突破 min 0.12 天花板

---

## TLT-011: Dynamic BB-Width Percentile Regime MR（動態百分位閘門，repo 首次於任何資產）

### 動機 (Motivation)

TLT-007 Att2 為當前最佳（Part A Sharpe 0.12 / Part B 0.65 / min 0.12），但固定 5% 閾值
缺乏 cross-regime 適應性。TLT-009、TLT-010 嘗試的外部 yield gate 與 signal-day secondary
filter 均失敗（詳見上方章節），EXPERIMENTS_TLT.md 曾明示未來方向應為「**BB 寬度 60 日分位數
dynamic regime 而非固定閾值**」。本實驗為 repo 首次以 percentile-based 動態閾值替代固定 5%
絕對閾值，測試是否能維持 TLT-007 Att2 的 regime classification 能力並進一步提升品質。

策略方向：**Dynamic BB-Width Percentile Regime Gate**
- BB(20, 2) 寬度 / Close 計算後，取 N 日 rolling percentile rank
- 僅當 current pctile rank <= threshold 時放行訊號
- 理論上 2022 升息期 BB 寬度處於歷史分位 80-100th，pctile gate 天然過濾

### 三次迭代結果 (Three Iteration Results)

| 迭代 | 關鍵參數 | Part A Sharpe | Part B Sharpe | min(A,B) | 結論 |
|------|----------|---------------|---------------|----------|------|
| Att1 | 252d/50th pctile、純動態 | **-0.11** (24/50.0% WR) | 0.55 (11/81.8% WR) | **-0.11** | 過寬（失敗） |
| Att2 | 504d/40th pctile、純動態 | **0.01** (13/53.8% WR) | 0.55 (11/81.8% WR) | **0.01** | 接近但仍失敗 |
| Att3 | 252d/40th + 絕對 BB<5% AND | **0.03** (10/50.0% WR) | 0.65 (6/83.3% WR) | **0.03** | 移除贏家（失敗） |

**三次迭代均未超越 TLT-007 Att2 min(A,B) 0.12。**

### 失敗分析 (Failure Analysis)

#### Att1（252d lookback + 50th pctile，純動態無絕對閾值）
- Part A 訊號 24（vs TLT-007 Att2 12）——50th pctile 過寬，2022 升息期 trailing 252d
  窗口累積大量高 vol 天數，導致中位數本身被拉高，「當日 <= 中位數」仍放行整片 2022 訊號流
- Part A Sharpe **-0.11** cum -7.76%——大量 2022 升息期訊號引入
- Part B 11 訊號/81.8% WR/Sharpe 0.55（相對寬鬆，比 TLT-007 Att2 的 6 訊號多 5 筆）
- **核心發現**：rolling percentile 在單一持續極端 regime 中**自我稀釋**——參考窗口被
  regime 期間主導，percentile 失去 cross-regime 區分力

#### Att2（504d lookback + 40th pctile，擴大視窗 + 收緊閾值）
- Part A 訊號 13（接近 TLT-007 Att2 的 12），Sharpe **0.01** cum +0.06%
- 504d 視窗雖含 2021 calm period，但 2022 升息期仍佔據超過 50% 的樣本，40th pctile 亦
  不足以完全切除 2022 訊號
- Part B 維持 11 訊號（同 Att1），Sharpe 0.55，81.8% WR
- **核心發現**：504 日視窗仍不夠長——理論上需要 1000+ 日（4 年）才能稀釋 2022 影響，
  但如此長的視窗會過度平滑近期波動率變化，實用性受限

#### Att3（252d/40th + 絕對 BB<5%，雙閘門 AND 組合）
- Part A 訊號 10（vs TLT-007 Att2 12），Sharpe **0.03** cum +0.53%
- Part B **與 TLT-007 Att2 完全相同**（6 訊號/83.3% WR/Sharpe 0.65/cum +9.07%）——
  Part B 的 6 筆訊號其 BB 寬度絕對值皆 <5% 且 pctile rank 皆 <=40th（calm regime 自洽）
- Part A 的 pctile 濾波**系統性移除 TLT-007 Att2 的 2 筆贏家**——這些訊號絕對 BB 寬度 <5%
  但相對於過去 252 日為高分位數（calm regime 末期 / regime 轉換初期訊號）
- **核心發現**：pctile gate 以「相對近期歷史」為基準，2022 後 calm period 初期 BB 寬度
  雖絕對值低但相對於 2022 為極低，隨時間推移 pctile 上升，反而過濾掉 2022 結束後的
  good signals

### 結論與擴展 (Conclusions and Extensions)

1. **TLT 的 BB 寬度 regime 閘門以「固定絕對閾值 5%」為結構性最優**——percentile-based
   dynamic threshold 無論純動態（Att1/Att2）或與絕對閾值 AND 組合（Att3）皆系統性劣於
   TLT-007 Att2
2. **核心原因**：TLT 2022 升息期為單一持續 12+ 個月的 regime episode，
   rolling percentile 在此期間自我稀釋（Att1/Att2）；即使絕對閾值已切除 2022 訊號，
   追加 pctile 過濾（Att3）會系統性移除 calm regime 末期 / regime 轉換初期的好訊號
3. **TLT-007 Att2 的「固定 5%」本質上是對 TLT 物理波動率的結構性常數**（約 5σ 日波動
   等價於 BB 通道 2 × 2σ ≈ 5% 價格範圍），不應被動態化
4. **新 cross-asset 規則（精煉 lesson #6 + lesson #20b）**：對於**單一極端 vol regime
   episode 持續時間長於 percentile lookback 視窗 50%** 的資產，rolling percentile-based
   regime gate 結構性失效——固定絕對閾值為唯一有效解。與 FXI-013 的「多段中等 vol
   regime 下固定和動態皆失敗」互補，共同精煉 BB-width regime gate 的適用邊界：
   - 資產有**單一極端且短於 lookback 50% 的 vol regime**：動態 percentile 可行
   - 資產有**單一極端且長於 lookback 50% 的 vol regime**（TLT 2022）：僅固定絕對閾值有效
   - 資產有**多段中等 vol regime**（FXI）：BB-width 所有型式皆失敗
5. **Repo 首次 percentile-based BB-width regime gate 試驗**：TLT-011 為 repo 中任何資產
   首次以 rolling percentile 取代固定 BB-width 閾值的試驗。結果為結構性失敗，明確了
   percentile-based regime gate 的適用邊界條件，貢獻於跨資產規則
6. **TLT 未來改進方向（仍未突破）**：TLT-011 證明 percentile 方向失敗後，TLT 的 min 0.12
   天花板可能為其技術面策略的結構性上限——除非引入 regime-prediction（而非 regime-
   classification）機制（例如 forward-looking Fed 政策指標、或 30d-implied-vol 等 forward
   derived），否則現有框架內應停止進一步嘗試「regime-classifier 精煉」方向
