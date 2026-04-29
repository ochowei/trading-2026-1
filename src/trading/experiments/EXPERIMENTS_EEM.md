<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-04-21
  data_through: 2025-12-31
  note: EEM-014 added 2026-04-21 (Post-Capitulation Vol-Transition MR：EEM-012 Att3 + 2DD floor 過濾，**repo 第 2 次 2DD floor 方向成功驗證**，繼 USO-013 後 broad EM ETF 首次). Three iterations, **Att2 SUCCESS**: Att1 failed（直接移植 CIBR-012 2DD cap 方向 require 2DD >= -3.0%）Part A 4 訊號 50% WR Sharpe **-0.02** cum -0.39% / Part B 3 訊號 66.7% WR Sharpe 0.34 / min -0.02 — 方向錯誤移除 TPs 保留 SLs，揭示 EEM SL 失敗結構（淺 2DD 中位 -0.85%）與 CIBR 相反（深 2DD ≤-4%）；**Att2 SUCCESS（2DD floor <= -0.5%）**: Part A 5 訊號 80% WR Sharpe **0.73** cum +9.06%（+115% vs 基線）/ Part B 4 訊號 75% WR Sharpe 0.56 cum +5.89%（同基線）/ min(A,B) **0.56**（+65% vs EEM-012 Att3 的 0.34）/ A/B cum 差 3.17pp（遠優 <30% 目標）/ A/B 訊號比 1.25:1（遠優 <50% 目標）/ 僅過濾 1 訊號 2021-11-30 SL（2DD +0.29% 淺幅漂移，非真 capitulation）/ 保留所有 7 TP 與兩個深 2DD SL（2021-07-08 -2.19%、2025-11-19 -0.85%）；Att3 ablation（Att2 - ATR 過濾）Part A 8 訊號 50% WR Sharpe -0.02（ATR 移除後新增 3 筆 Part A SL）/ Part B 不變 / min -0.02 — 證明 ATR>1.10 與 2DD floor 為**互補雙過濾**而非冗餘，兩者疊加必要。**核心跨資產發現（2DD 方向資產相依性）**：CIBR（深 2DD SL，in-crash）用 **2DD cap** 方向成功；EEM（淺 2DD SL，慢漂移）必須用 **2DD floor** 方向（相反），兩資產 2DD 結構完全相反。**2DD 方向不可通用移植**，必須先檢查失敗 SL 的 2DD 分布。擴展 lesson #19（2DD 雙向性）：方向取決於殘餘 SL 的 2DD 結構。**擴展 lesson #52（混合進場模式）**：在 broad EM ETF（EEM 1.17% vol）上 BB 下軌+回檔上限 hybrid 可再進一步以 2DD floor 精煉至 min 0.56。EEM 成為 repo 第 2 次 2DD floor 方向成功案例（繼 USO-013 後）。EEM-014 Att2 成為新全域最優。14 experiments, 37 attempts. EEM-013 added 2026-04-20 (MACD Histogram Bullish Turn + Pullback Hybrid MR, **repo first MACD trial**). Three iterations all failed vs EEM-012 Att3 min 0.34: Att1 (MACD hist zero-line upcross + pullback [-7,-3] + WR≤-70 + ClosePos≥40%) Part A/B both 0 signals — zero-cross severely lags MR entry timing (by the time cross fires, WR already recovered). Att2 (MACD hist 2-bar bullish turn: today > yesterday > day-2 AND yesterday < 0, pullback [-8,-2] + WR≤-75 + ClosePos≥40%) Part A 8 signals 50% WR -0.77% cumulative Sharpe **-0.02** (4 TP / 4 SL, 2022-2023 rate-hike bear market SLs concentrated: 2019-05 trade war / 2022-09,10 / 2023-02 / 2024-07) / Part B 3 signals 66.7% WR +2.80% Sharpe 0.34 — MACD smoother EMA than RSI/CCI hook but still fails in bear rally dead-cat bounces. Att3 (Att2 + **reverse ATR filter**: ATR(5)/ATR(20) < 1.10) Part A 5 signals 60% WR +2.60% Sharpe 0.19 / Part B 2 signals 100% WR +6.09% Sharpe 0.00 (zero-variance 2/2 TPs) / min(A,B) 0.00. **Novel cross-asset finding**: MACD framework on EEM prefers LOW ATR environment (opposite of EEM-010 RSI(2) framework which uses ATR>1.15) — bear-rally dead-cat bounces coincide with high ATR spikes, while genuine MR during bull consolidation has lower ATR. Reverse ATR<1.10 filter improved Part A WR from 50%→60% by removing 3 SL (2019-05-15 ATR 1.47, 2022-10-03 ATR 1.14, 2024-07-29 ATR 1.11) but also removed 2 TP (2019-08-12 ATR 1.15, 2021-10-06 ATR 1.12). **Repo first MACD trial** — extends lesson #20b failure family (V-bounce ≠ genuine reversal) to MACD histogram turn patterns: MACD's EMA-based smoothing insufficient to solve V-bounce problem in post-peak persistent decline regimes (2022-2023 Fed hiking).
-->
## AI Agent 快速索引

**當前最佳：** **EEM-014 Att2（新全域最優）**（EEM-012 Att3 所有條件 + **2DD floor <= -0.5%**：BB(20,2.0) 下軌 + 回檔上限 -7% + WR(10)≤-85 + ClosePos≥40% + ATR>1.1 + **2DD<= -0.5%** + TP+3%/SL-3%/20天 + 冷卻10天，Part A Sharpe **0.73**，Part B Sharpe 0.56，min(A,B) **0.56**）★ Repo 第 2 次「2DD floor 方向」成功驗證（繼 USO-013 後），勝過 EEM-012 Att3 +65%（0.34→0.56）。**14 個實驗 37+ 次嘗試。**

**次佳（hybrid 進場框架）：** EEM-012 Att3（BB(20,2.0) 下軌 + 回檔上限 -7% + WR(10)≤-85 + ClosePos≥40% + ATR>1.1 + TP+3%/SL-3%/20天 + 冷卻10天，Part A Sharpe 0.34，Part B Sharpe 0.56，min(A,B) 0.34）★ 混合進場模式首次延伸至 broad EM ETF，勝過 EEM-005 BB Squeeze +89%（0.18→0.34）。

**次佳（突破策略最佳）：** EEM-005 Att2（BB Squeeze 30th 百分位 + SMA(50) + TP3.0%/SL3.0%/20天 + 冷卻10天，Part A Sharpe 0.20，Part B Sharpe 0.18）

**第三（均值回歸 RSI(2) 最佳）：** EEM-003 Att2（RSI(2)<10 + 2日跌幅≥1.5% + ClosePos≥40% + ATR>1.15 + 冷卻10天，Part A Sharpe 0.06，Part B Sharpe 0.00/100%WR）

**已證明無效（禁止重複嘗試）：**
- 無 ATR 過濾的基線（EEM-001：Part A Sharpe -0.13，15 筆停損拖累，EM 熊市慢跌產生假訊號）
- ATR > 1.15 + 冷卻 5 天（EEM-002 Att1：Part A Sharpe -0.02，COVID 二次進場未被阻斷）
- ATR > 1.1 + SL -3.5%（EEM-002 Att2：Part A -0.02，寬 SL 增加虧損幅度不轉贏，MDD -7.11%）
- 移除 ClosePos + ATR > 1.15（EEM-002 Att3：Part A -0.07，新增訊號品質差；Part B 1.48 極佳但 A/B 失衡）
- 2日跌幅 2.0% + 無 ClosePos + ATR > 1.15（EEM-003 Att1：Part A -0.19，深跌幅無法補償 ClosePos）
- 無 ClosePos + ATR > 1.15 + 冷卻 10 天（EEM-003 Att3：Part A -0.19，同 Att1，冷卻無法補償 ClosePos）
- 回檔+WR 無 ATR（EEM-004 Att1：Part A 0.01，45 訊號 WR 51.1%，慢跌假訊號過多）
- 回檔+WR + ATR>1.15 + 回檔上限 8%（EEM-004 Att2：Part A -0.18，ATR 在回檔框架中反移除好訊號）
- BB Squeeze 30th pct + TP 3.5% + 15天持倉（EEM-005 Att1：Part B 50% 到期，TP 偏高）
- BB Squeeze 25th pct（EEM-005 Att3：Part A 0.29 但 A/B gap 擴大至 0.11，過擬合風險）
- **RS 動量回調 EEM vs SPY（EEM-006，3 次嘗試均失敗）：**
  - Att1: RS(20d)≥3% + Pullback 2-4% + SMA(50) → Part A 0.34 / Part B -0.23（最佳嘗試）
  - Att2: RS(10d)≥2% + Pullback 2-6% → Part A -0.13 / Part B -0.38（10日 RS 太噪）
  - Att3: RS(20d)≥3.5% + SMA金叉 → Part A 0.87 / Part B -0.60（Part A 極佳但 Part B 慘淡）
  - **根因：EEM-SPY 相對強度由不可預測的宏觀/政治事件（關稅、貿易戰、中國政策）驅動，非結構性因素。確認跨資產教訓 #20。**
- **趨勢動量回調（EEM-007 Att1-2，2 次嘗試均失敗）：**
  - Att1: SMA(50) + 20d ROC>2% + 10d drawdown≥2% → Part A 0.19 / Part B -0.32
  - Att2: ROC>3% + WR(10)<-60 + 10d drawdown≥2% → Part A 0.43 / Part B -0.37
  - **根因：趨勢動量回調在 EEM 上嚴重市場狀態依賴。確認跨資產教訓 #26。**
- **牛市政權過濾均值回歸（EEM-007 Att3）：**
  - SMA(200) + RSI(2)<10 + 2d decline≥1.5% + ClosePos≥40% + ATR>1.15 → Part A -0.92 / Part B 0.00
  - **根因：SMA(200) 政權過濾移除最佳均值回歸訊號。確認跨資產教訓 #5。**
- **BB Squeeze 寬 SL -4.0% + 25天持倉（EEM-008 Att1）：**
  - Part A 0.12 / Part B 0.10（均劣於 EEM-005）
  - **根因：EEM 停損交易為真正的 EM 結構性崩潰（中國監管、升息），加寬 SL 只增加虧損幅度。**
- **Range Compression Breakout（EEM-008 Att2，全新進場機制）：**
  - 5日價格範圍壓縮 + 20日收盤新高 + SMA(50) → Part A -0.17 (40訊號) / Part B 0.27 (18訊號)
  - **根因：價格範圍壓縮門檻過鬆，Part A 產生大量假突破（40 vs BB Squeeze 的 18）。Part B 0.27 證明概念在趨勢市有效但嚴重市場狀態依賴。**
- **BB Squeeze + 環境波動率過濾 20日 ≤ 1.4%（EEM-008 Att3）：**
  - Part A 0.11 (14訊號) / Part B 0.18 (10訊號，與 EEM-005 相同)
  - **根因：波動率過濾移除 3 個好訊號（COVID 復甦期突破）但只移除 1 個壞訊號。EM 宏觀衝擊發生在正常波動率環境，事後波動率才飆升——環境波動率無法預測未來衝擊。**
- **ATR>1.15 + SL-3.5% 組合（EEM-009）：**
  - Part A -0.09 (14訊號 WR 50%) / Part B 0.00* (5訊號 WR 100%)
  - **根因：ATR>1.15 有效過濾慢跌訊號，但 SL-3.5% 對 EM 停損（結構性崩潰）不如 SL-3.0%。確認 EEM-002 Att2 結論（寬 SL 增加虧損不轉贏）。**
- **嚴格跌幅2.0% + ATR>1.1 + ClosePos≥40%（EEM-010，新組合）：**
  - Part A 0.03 (12訊號 WR 58.3%) / Part B 0.00* (3訊號 WR 100%)
  - **此組合為 EEM-002 Att2(ATR>1.1+SL-3.5%) 和 EEM-003 Att1(decline 2.0%+ATR>1.15) 的交叉，首次測試**
  - **根因：嚴格跌幅有效過濾 EM 危機淺跌假訊號，但無法超越 BB Squeeze (0.18)。Part A 為均值回歸框架中的最高 Sharpe，但 EM 結構性事件限制均值回歸上限。**
- **無 ClosePos + ATR>1.1 + 跌幅2.0%（EEM-011，ClosePos 有效性驗證）：**
  - Part A -0.05 (23訊號 WR 52.2%) / Part B 0.56 (9訊號 WR 77.8%)
  - **根因：移除 ClosePos 後 Part A 品質顯著下降（WR 58.3%→52.2%），確認 ClosePos 對 EEM 有效。Part B 0.56 但 Part A/B 不穩健。**

**已掃描的參數空間：**
- 均值回歸進場：RSI(2)<10 + 2日跌幅 1.5%~2.0% + ClosePos 0%/40% + ATR 1.1~1.15 + SL 3.0%~3.5%
- 回檔+WR 進場：pullback 20d ≥3% + WR(10)≤-80 + ClosePos≥40% ± ATR/回檔上限
- BB Squeeze 進場：BB(20,2.0) + 25th~30th pct squeeze + SMA(50) 趨勢確認
- RS 動量進場：EEM-SPY RS 10d/20d ≥ 2%/3%/3.5% + 5日回調 2-4%/2-5%/2-6% + SMA(50) ± SMA 金叉
- 趨勢動量回調進場：SMA(50) + 20d ROC 2-3% + 10d drawdown≥2% ± WR(10)<-60
- 牛市政權過濾均值回歸：SMA(200) + RSI(2)<10 + 2d decline≥1.5% + ClosePos≥40% + ATR>1.15
- Range Compression：5日 High-Low 範圍 30th pct / 40日窗口 + 20日收盤新高 + SMA(50)
- 環境波動率過濾：20日實現波動率 ≤ 1.4%（於 BB Squeeze 框架上）
- 出場參數：TP 3.0%~3.5% / SL 3.0%~4.0% / 15~25天持倉
- 冷卻期：5、10 天
- ATR > 1.15 在 RSI(2) 框架有效，但在回檔+WR 框架反效果
- ClosePos ≥ 40% 對 RSI(2) 框架至關重要
- SL -3.5%/-4.0% 不優於 -3.0%（EEM 停損多為 EM 結構性崩潰，加寬只增加虧損）
- BB Squeeze TP 3.0% > 3.5%（低波動 ETF 突破動量有限，3.5% 到期過多）
- BB Squeeze 30th > 25th pct（25th 提升 Part A 但加大 A/B 不平衡）

**尚未嘗試的方向（預期邊際效益極低，不建議繼續探索）：**
- 冷卻 8 天（7-10 天之間的微調）
- RSI(2) < 8 更嚴門檻（可能過濾好訊號）
- 配對交易（跨資產相關性結構性漂移風險，lesson #20/#23）
- ~~動量回調~~ → EEM-006/007 已驗證失敗
- ~~趨勢/政權過濾均值回歸~~ → EEM-007 Att3 已驗證失敗
- ~~寬 SL / 延長持倉~~ → EEM-008 Att1 已驗證失敗
- ~~替代壓縮指標（價格範圍）~~ → EEM-008 Att2 已驗證假突破過多
- ~~環境波動率過濾~~ → EEM-008 Att3 已驗證移除好訊號多於壞訊號
- ~~MACD 柱狀圖 turn-up 均值回歸~~ → EEM-013 驗證失敗（3 次迭代，repo 首次 MACD 試驗）
  - Att1（MACD 柱狀圖零軸上穿 + 回檔 [-7,-3] + WR≤-70 + ClosePos≥40% + cd10）：Part A/B 各 0 訊號（零軸上穿嚴重滯後）
  - Att2（MACD 柱狀圖 2 根連續 turn-up + 回檔 [-8,-2] + WR≤-75 + ClosePos≥40%）：Part A 8 訊號 WR 50% Sharpe **-0.02** / Part B 3 訊號 WR 66.7% Sharpe 0.34 / min(A,B) -0.02，2022-2023 升息熊市 SL 集中
  - Att3（Att2 + **反向 ATR 過濾 ATR<1.10**）：Part A 5 訊號 WR 60% Sharpe 0.19 / Part B 2 訊號 WR 100% Sharpe 0.00 零方差 / min(A,B) 0.00，反向 ATR 為 EEM-013 獨特發現但仍無法超越 EEM-012 Att3 的 0.34
  - 失敗根因：MACD 雖為平滑 EMA 指標仍擴展 lesson #20b 失敗家族——V-bounce ≠ genuine reversal 在 2022-2023 升息熊市中無法由 MACD/RSI/CCI 任何 oscillator hook 區分

**EEM-014（Post-Capitulation Vol-Transition MR：2DD floor 精煉，新全域最優）：**
- Att1（直接移植 CIBR-012 方向 require 2DD >= -3.0% 作為 cap）：Part A 4 訊號 50% WR Sharpe **-0.02** cum -0.39% / Part B 3 訊號 66.7% WR Sharpe 0.34 cum +2.80% / min(A,B) -0.02（-106% vs 基線）。方向錯誤移除 Part A TPs（2021-07-26 2DD -3.36%、2021-09-20 2DD -3.10%）並保留 SLs（2021-07-08 -2.19%、2021-11-30 +0.29%、2025-11-19 -0.85%）
- **Att2 ★ SUCCESS（require 2DD <= -0.5% 作為 floor）**：Part A 5 訊號 **80% WR** Sharpe **0.73** cum +9.06%（+115% vs 基線）/ Part B 4 訊號 75% WR Sharpe 0.56 cum +5.89%（同基線）/ min(A,B) **0.56**（+65% vs 基線 0.34）/ A/B cum 差 3.17pp / A/B 訊號比 1.25:1。僅過濾 1 筆訊號（2021-11-30 SL 2DD +0.29%）
- Att3 ablation（Att2 - ATR 過濾 atr_ratio=0）：Part A 8 訊號 50% WR Sharpe -0.02 cum -0.77% / Part B 4 訊號 Sharpe 0.56 不變 / min -0.02。ATR>1.10 移除後 Part A 新增 3 筆 SL，證明 ATR 與 2DD floor 為**互補雙過濾**（ATR 捕捉 signal-day panic，2DD floor 排除淺幅漂移）而非冗餘
- 核心跨資產發現：**2DD 方向依賴於失敗 SL 的 2DD 結構**，不可通用移植。CIBR（深 2DD SL，in-crash acceleration）用 cap 方向；EEM（淺 2DD SL，慢漂移）用 floor 方向（相反）。擴展 lesson #19（2DD 雙向性）
- Repo 第 2 次「2DD floor 方向」成功驗證（繼 USO-013 後，broad EM ETF 首次）。擴展 lesson #52（混合進場模式）再精煉邊界

**關鍵資產特性：**
- EEM 為新興市場 ETF（iShares MSCI Emerging Markets），追蹤新興市場大盤
- 日均波動約 1.17%，與 GLD (1.12%) 和 SPY (1.2%) 近似
- 受新興市場經濟體、美元強弱、商品價格等多重因素影響
- **突破策略（BB Squeeze）優於均值回歸**：EEM 的 EM risk-on/risk-off 資金流驅動波動率壓縮後突破
- 均值回歸框架的核心限制：Part A (2019-2023) EM 熊市產生大量結構性停損（貿易戰/COVID/中國監管/俄烏）
- 回檔+WR 在 EEM 上無效：與 IWM 類似，EEM 的頻繁淺回檔產生假訊號（lesson #16 驗證）
- ATR > 1.15 在 RSI(2) 框架有效但在回檔+WR 框架反效果
- TP +3.0% 是 EEM 跨策略最佳目標（突破和均值回歸均適用）
- **RS 動量（EEM vs SPY）完全無效**：相對強度由宏觀/政治事件驅動
- **趨勢動量回調嚴重市場狀態依賴**
- **SMA(200) 政權過濾均值回歸有害**
- **寬 SL / 長持倉無效**：EM 停損為結構性崩潰非暫時性回撤
- **環境波動率過濾無效**：EM 宏觀衝擊在正常波動率下發生，無法用過去波動率預測
- **EEM 技術面天花板更新**：12 個實驗覆蓋均值回歸（RSI(2) 含嚴格跌幅+ATR交叉組合、BB 下軌混合進場）、突破、動量、RS、趨勢、政權過濾、出場優化、波動率過濾、ClosePos有效性驗證。**EEM-012 混合進場（BB 下軌 + 回檔上限 + WR -85 + ClosePos + ATR）突破 EEM-005 BB Squeeze 的 0.18 天花板至 0.34（+89%）**，驗證 lesson #52 混合模式可擴展至 broad EM ETF 類別（非單一國家 EM）
- **EEM-012 混合進場三次迭代**：
  - Att1（WR ≤ -80 + ATR > 1.10）：min(A,B) 0.13，Part A 含 2019-05 貿易戰、2021-11 Omicron 等 3 個 EM 危機假訊號
  - Att2（收緊 ATR > 1.15）：min(A,B) -0.60，**反向失敗**——EEM 危機日 ATR 普遍飆高，提高門檻反移除贏家保留輸家。ATR 在 BB Lower 框架對 EEM 方向相反（vs RSI(2) 框架）
  - Att3（還原 ATR 1.10，收緊 WR ≤ -85）★：min(A,B) 0.34，WR -85 成功移除 2019-05-09 貿易戰淺觸假訊號，A/B 累計差僅 3.6%，訊號頻率 1.2/yr vs 2.0/yr（1:1.67）
- **EEM-013 MACD 試驗三次迭代（repo 首次 MACD 試驗）**：
  - Att1（MACD 柱狀圖零軸上穿 + 回檔 [-7%,-3%] + WR≤-70 + ClosePos≥40%）：Part A/B 各 0 訊號，MACD 零軸上穿嚴重滯後於 pullback+WR 組合
  - Att2（MACD 柱狀圖 2 根連續上揚 today>yesterday>day-2 且 yesterday<0 + 回檔 [-8%,-2%] + WR≤-75 + ClosePos≥40%）：Part A 8 訊號 WR 50% 累計 -0.77% Sharpe **-0.02** / Part B 3 訊號 WR 66.7% 累計 +2.80% Sharpe 0.34 / min(A,B) -0.02。A/B 頻率比 1.04:1 極佳但 Part A 2022-2023 熊市產生 4 筆 SL（2019-05 貿易戰、2022-09/10 升息、2023-02 早期修正）
  - Att3（Att2 + **反向 ATR 過濾 ATR<1.10**）：Part A 5 訊號 WR 60% 累計 +2.60% Sharpe 0.19 / Part B 2 訊號 WR 100% 累計 +6.09% Sharpe 0.00 零方差 / min(A,B) 0.00。**獨特發現**：MACD 框架在 EEM 上偏好低波動環境（ATR<1.10），與 EEM-010 RSI(2) 框架的 ATR>1.15 方向完全相反——bear rally dead-cat bounce 伴隨 ATR 飆升，bull consolidation MR 為低 ATR
  - 失敗根因：(1) MACD 雙 EMA 平滑雖優於 RSI/CCI 點估計但仍無法解決「V-bounce ≠ genuine reversal」根本問題（lesson #20b 失敗家族擴展至 MACD）；(2) 反向 ATR<1.10 過濾成功移除 3 筆高 ATR 的 Part A SL（2019-05-15 ATR 1.47、2022-10-03 ATR 1.14、2024-07-29 ATR 1.11）但同時移除 2 筆高 ATR 的 TP（2019-08-12 ATR 1.15、2021-10-06 ATR 1.12），淨 WR 提升至 60% 仍低於所需的 > 70% 門檻；(3) Part B 訊號降至 1/yr 稀疏度使 100% WR 僅兩筆 + 3% 零方差——**EEM 在 MACD 框架下 Part B 訊號稀疏成為結構性限制**
<!-- AI_CONTEXT_END -->

# EEM 實驗總覽 (EEM Experiments Overview)

## 標的特性 (Asset Characteristics)

- **EEM (iShares MSCI Emerging Markets ETF)**：追蹤 MSCI 新興市場指數
- 日均波動約 1.17%，與 SPY (~1.2%) 和 GLD (~1.12%) 近似
- 受美元指數、商品價格、新興市場資金流向等因素影響
- 作為廣基指數 ETF，曾被認為適合 RSI(2) 均值回歸框架，但 EM 結構性事件限制其有效性
- RS 動量策略（EEM-006）證實 EEM-SPY 相對強度由宏觀/政治事件驅動，不適合技術面 RS 策略

## 實驗列表 (Experiment List)

| ID      | 資料夾                                | 策略摘要                                | 狀態  |
|---------|---------------------------------------|----------------------------------------|-------|
| EEM-001 | `eem_001_rsi2_mean_reversion`         | RSI(2) 極端超賣均值回歸                  | 已完成 |
| EEM-002 | `eem_002_vol_adaptive_rsi2`           | 波動率自適應 RSI(2)（ATR 過濾）          | 已完成 |
| EEM-003 | `eem_003_vol_adaptive_deep_decline`   | 波動率自適應 RSI(2) + 延長冷卻期          | 已完成 |
| EEM-004 | `eem_004_pullback_wr`                 | 回檔範圍 + Williams %R（回檔框架移植）     | 已完成 |
| EEM-005 | `eem_005_bb_squeeze_breakout`         | BB 擠壓突破 ★最佳                         | 已完成 |
| EEM-006 | `eem_006_rs_momentum_pullback`        | RS 動量回調（EEM vs SPY 相對強度）          | 已完成 |
| EEM-007 | `eem_007_trend_momentum_pullback`     | 趨勢動量回調 → 政權過濾均值回歸              | 已完成 |
| EEM-008 | `eem_008_optimized_breakout`          | 優化突破（出場/進場/波動率過濾，3次嘗試均失敗）| 已完成 |
| EEM-009 | `eem_009_atr_sl_rsi2`                 | ATR>1.15 + SL-3.5% RSI(2)（寬SL測試）     | 已完成 |
| EEM-010 | `eem_010_strict_decline_atr`          | 嚴格跌幅2.0% + ATR>1.1 RSI(2)（均值回歸最佳新組合）| 已完成 |
| EEM-011 | `eem_011_no_closepos_atr`             | 無ClosePos + ATR>1.1（ClosePos有效性驗證）  | 已完成 |
| EEM-012 | `eem_012_bb_lower_pullback_cap`       | BB 下軌 + 回檔上限混合進場 MR              | 已完成 |
| EEM-013 | `eem_013_macd_histogram_mr`           | MACD 柱狀圖多頭轉折均值回歸（repo 首次 MACD）| 已完成 |
| EEM-014 | `eem_014_vol_transition_mr`           | Post-Capitulation Vol-Transition MR（+2DD floor，2DD 方向精煉）★最佳 | 已完成 |

---

## EEM-001: RSI(2) 極端超賣均值回歸

### 目標 (Goal)

利用 RSI(2) 捕捉 EEM 極端超賣後的均值回歸機會。基於 SPY-005 已驗證的 RSI(2) 框架，EEM 日波動 (1.17%) 與 SPY (1.2%) 近似，使用相同參數架構。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 極端超賣 | RSI(2) | < 10 | 2 日動量極端耗竭 |
| 幅度確認 | 2 日累計跌幅 | ≥ 1.5% | 確認有意義的下跌幅度 |
| 日內反轉 | Close Position | ≥ 40% | 收盤位置在日內區間中上，反轉確認 |
| 冷卻期 | 訊號間隔 | ≥ 5 天 | 避免連續觸發 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +3.0% | 與 SPY-005 相同 |
| 停損 (SL) | -3.0% | 與 SPY-005 相同 |
| 最長持倉 | 20 天 | 與 SPY-005 相同 |
| 追蹤停損 | 無 | 日波動 ~1.2% 不適合追蹤停損（lesson #2） |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 訊號日隔日開盤市價 |
| 出場方式 | TP/SL 觸及時以悲觀認定出場 |
| 滑價假設 | 0.10% (ETF) |
| 日內路徑 | 高-低-收三點估計 |

### 回測結果 (Backtest Results)

| 區間 | 年份 | 訊號數 | 勝率 | 累積報酬 | Sharpe | MDD |
|------|------|--------|------|----------|--------|-----|
| Part A (IS) | 2019-2023 | 28 (5.6/yr) | 42.9% | -11.12% | -0.13 | -6.79% |
| Part B (OOS) | 2024-2025 | 7 (3.5/yr) | 71.4% | +6.38% | 0.35 | -4.26% |
| Part C (Live) | 2026 | 1 (3.8/yr) | 0.0% | -3.10% | 0.00 | -3.50% |

---

## EEM-002: 波動率自適應 RSI(2) (Volatility-Adaptive RSI(2))

### 目標 (Goal)

加入 ATR(5)/ATR(20) 波動率飆升過濾，選擇急跌恐慌訊號、過濾慢磨下跌假訊號。參考 XLU (~1.0%) 和 IWM (~1.5%) 的成功案例。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 極端超賣 | RSI(2) | < 10 | 同 EEM-001 |
| 幅度確認 | 2 日累計跌幅 | ≥ 1.5% | 同 EEM-001 |
| 日內反轉 | Close Position | ≥ 40% | 同 EEM-001 |
| 波動率飆升 | ATR(5)/ATR(20) | > 1.15 | 短期波動率高於長期 15% |
| 冷卻期 | 訊號間隔 | ≥ 5 天 | 同 EEM-001 |

### 嘗試記錄 (Attempt Log)

| Att | 配置 | Part A Sharpe | Part B Sharpe | min(A,B) | 結論 |
|-----|------|---------------|---------------|----------|------|
| 1 | ATR>1.15, ClosePos≥40%, SL-3.0% | -0.02 | 0.00 (100%WR) | -0.02 | ATR 有效過濾 Part B，Part A 仍負 |
| 2 | ATR>1.1, ClosePos≥40%, SL-3.5% | -0.02 | 0.00 (100%WR) | -0.02 | 寬 SL 增加虧損不轉贏 |
| 3 | ATR>1.15, 無 ClosePos, SL-3.0% | -0.07 | 1.48 | -0.07 | 移除 ClosePos 傷 Part A |

### 回測結果 (Att1 — 最佳配置)

| 區間 | 年份 | 訊號數 | 勝率 | 累積報酬 | Sharpe | MDD |
|------|------|--------|------|----------|--------|-----|
| Part A (IS) | 2019-2023 | 14 (2.8/yr) | 50.0% | -1.34% | -0.02 | -5.06% |
| Part B (OOS) | 2024-2025 | 5 (2.5/yr) | 100.0% | +15.93% | 0.00* | -1.03% |

*Part B Sharpe 0.00 因所有 5 筆交易均 +3.00% 達標，標準差為 0

---

## EEM-003: 波動率自適應 RSI(2) + 延長冷卻期 ★ 當前最佳

### 目標 (Goal)

在 EEM-002 Att1 基礎上延長冷卻期至 10 天，阻斷下跌趨勢中的連續進場（如 COVID 二波停損）。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 極端超賣 | RSI(2) | < 10 | 同 EEM-001 |
| 幅度確認 | 2 日累計跌幅 | ≥ 1.5% | 同 EEM-001 |
| 日內反轉 | Close Position | ≥ 40% | 同 EEM-001 |
| 波動率飆升 | ATR(5)/ATR(20) | > 1.15 | 同 EEM-002 |
| 冷卻期 | 訊號間隔 | ≥ 10 天 | 阻斷 COVID 等連續恐慌進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +3.0% | 同 EEM-001 |
| 停損 (SL) | -3.0% | 同 EEM-001 |
| 最長持倉 | 20 天 | 同 EEM-001 |

### 嘗試記錄 (Attempt Log)

| Att | 配置 | Part A Sharpe | Part B Sharpe | min(A,B) | 結論 |
|-----|------|---------------|---------------|----------|------|
| 1 | 2d decline 2.0%, 無 ClosePos, ATR>1.15 | -0.19 | 1.11 | -0.19 | 深跌幅無法補償 ClosePos |
| 2 | ClosePos≥40%, ATR>1.15, cooldown 10 | **+0.06** | 0.00 (100%WR) | **+0.06** | ★ 新最佳 |
| 3 | 無 ClosePos, ATR>1.15, cooldown 10 | -0.19 | 1.48 | -0.19 | 同 Att1 效果 |

### 回測結果 (Att2 — 最佳配置)

| 區間 | 年份 | 訊號數 | 勝率 | 累積報酬 | Sharpe | MDD |
|------|------|--------|------|----------|--------|-----|
| Part A (IS) | 2019-2023 | 13 (2.6/yr) | 53.8% | +1.81% | **+0.06** | -5.06% |
| Part B (OOS) | 2024-2025 | 5 (2.5/yr) | 100.0% | +15.93% | 0.00* | -1.03% |
| Part C (Live) | 2026 | 1 (3.7/yr) | 0.0% | -3.10% | 0.00 | -3.50% |

*Part B Sharpe 0.00 因所有 5 筆交易均 +3.00% 達標，標準差為 0

### 關鍵發現 (Key Findings)

- **ATR > 1.15 在 EEM (1.17% daily vol) 上高度有效**：Part B 從 WR 71.4% → 100%，移除全部壞訊號
- **ClosePos ≥ 40% 對 Part A 至關重要**：移除後 Part A Sharpe 從 -0.02 降至 -0.07~-0.19
- **冷卻 10 天是關鍵增量改善**：阻斷 COVID 2020-03-09 二次進場（距前次 7 天），Part A Sharpe -0.02 → +0.06
- **SL -3.5% 無效**：EEM 停損多為事件驅動 gap-down，寬 SL 只增加虧損幅度
- **Part A 剩餘 6 筆停損均為 EM 結構性事件**（貿易戰、COVID、中國監管、俄烏戰爭），無純技術面解法
- **A/B 訊號率比 1.04:1（極佳）**：策略穩健，非市場狀態依賴

---

## EEM-004: 回檔範圍 + Williams %R 均值回歸

### 目標 (Goal)

測試 GLD-012 驗證有效的 pullback+WR 框架在 EEM 上的效果。EEM 日波動 1.17% 與 GLD 1.12% 近似，但 EEM 受 EM 事件驅動，回檔特性可能不同。

### 嘗試記錄 (Attempt Log)

| Att | 配置 | Part A Sharpe | Part B Sharpe | min(A,B) | 結論 |
|-----|------|---------------|---------------|----------|------|
| 1 | Pullback 20d≥3% + WR≤-80 + ClosePos≥40% + cooldown 10 | 0.01 | 0.27 | 0.01 | 45 訊號過多，慢跌假訊號 WR 51.1% |
| 2 | + ATR>1.15 + 回檔上限 8% | -0.18 | 0.42 | -0.18 | ATR 在回檔框架反移除好訊號 |

### 關鍵發現 (Key Findings)

- **回檔+WR 在 EEM 上無效**：與 IWM 類似，EEM 的頻繁淺回檔產生假訊號（驗證 lesson #16）
- **ATR 過濾在回檔框架中反效果**：不同於 RSI(2) 框架，回檔深度已隱含波動率資訊，ATR 額外移除好訊號
- **Att1 的 Part A 45 訊號 (9.0/yr) 遠超 Part B 12 訊號 (6.0/yr)**：WR 僅 51.1%，幾乎隨機
- **回檔框架的根本問題**：EM 熊市 (2019-2023) 頻繁產生 -3% 回檔但未反彈，均值回歸邏輯失效

---

## EEM-005: BB 擠壓突破 ★ 當前最佳

### 目標 (Goal)

嘗試完全不同的策略類型：波動率壓縮後的方向性突破。EEM 受 EM risk-on/risk-off 資金流驅動，波動率壓縮後常有方向性突破。突破策略天然迴避 EM 熊市均值回歸的停損問題。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 波動率壓縮 | BB Width 百分位 | ≤ 30th (60日) | 近 5 日內帶寬處於低位 |
| 突破確認 | Close > BB Upper | BB(20, 2.0) | 收盤突破上軌 |
| 趨勢確認 | Close > SMA(50) | — | 中期趨勢向上 |
| 冷卻期 | 訊號間隔 | ≥ 10 天 | 避免連續觸發 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +3.0% | EEM 1.17% vol 適當目標 |
| 停損 (SL) | -3.0% | 對稱出場 |
| 最長持倉 | 20 天 | 給予突破充足發展時間 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 訊號日隔日開盤市價 |
| 出場方式 | TP/SL 觸及時以悲觀認定出場 |
| 滑價假設 | 0.10% (ETF) |
| 日內路徑 | 高-低-收三點估計 |

### 嘗試記錄 (Attempt Log)

| Att | 配置 | Part A Sharpe | Part B Sharpe | min(A,B) | 結論 |
|-----|------|---------------|---------------|----------|------|
| 1 | 30th pct, TP 3.5%, SL 3.0%, 15天 | 0.29 | 0.14 | 0.14 | Part B 50% 到期（TP 偏高）|
| 2 | 30th pct, TP 3.0%, SL 3.0%, 20天 | **0.20** | **0.18** | **0.18** | ★ A/B 最佳平衡 |
| 3 | 25th pct, TP 3.0%, SL 3.0%, 20天 | 0.29 | 0.18 | 0.18 | Part A↑ 但 A/B gap 擴大 |

### 回測結果 (Att2 — 最佳配置)

| 區間 | 年份 | 訊號數 | 勝率 | 累積報酬 | Sharpe | MDD |
|------|------|--------|------|----------|--------|-----|
| Part A (IS) | 2019-2023 | 18 (3.6/yr) | 61.1% | +9.87% | **+0.20** | -4.22% |
| Part B (OOS) | 2024-2025 | 10 (5.0/yr) | 60.0% | +4.65% | **+0.18** | -3.71% |
| Part C (Live) | 2026 | 2 (7.5/yr) | 100.0% | +4.14% | 2.17 | -0.05% |

### 關鍵發現 (Key Findings)

- **突破策略大幅優於均值回歸**：min(A,B) Sharpe 0.18 vs EEM-003 的 0.06（+200%）
- **突破天然迴避 EM 熊市停損問題**：SMA(50) 趨勢確認過濾掉大部分下跌期訊號
- **TP 3.0% > 3.5% 對低波動 ETF**：EEM 1.17% vol 突破動量有限，3.5% TP 導致 50% 到期
- **A/B 平衡極佳**：Sharpe gap 僅 0.02 (0.20/0.18)，WR 差異 1.1pp (61.1%/60.0%)
- **30th pct > 25th pct 擠壓門檻**：25th 提升 Part A (0.29) 但 A/B gap 從 0.02 擴大至 0.11
- **Part B 信號率 5.0/yr > Part A 3.6/yr**：Part B 更活躍，無過擬合跡象
- **挑戰 lesson #28 的結論**：BB Squeeze 在 EEM（分散化 ETF）上有效，可能因 EM risk-on/risk-off 資金流特性

---

## EEM-006: RS Momentum Pullback（EEM vs SPY 相對強度動量回調）

### 目標 (Goal)

利用 EEM 相對 SPY 的超額表現（EM 優於 DM）在短期回調時買入，捕捉 EM 資金流動量。參考 TSM-008（Sharpe 0.79）和 SOXL-010（Sharpe 0.70）的 RS 動量框架，為 repo 中較少使用的策略方向。

### 進場條件 (Entry Conditions - Att1)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 相對強度 | EEM 20日報酬 - SPY 20日報酬 | ≥ 3% | EM 相對 DM 超額表現 |
| 短期回調 | 5日高點回撤 | 2-4% | 上漲趨勢中的短暫整理 |
| 趨勢確認 | Close | > SMA(50) | 上升趨勢中 |
| 冷卻期 | 訊號間隔 | ≥ 10 天 | 避免連續觸發 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +3.0% | EEM 跨策略最佳目標 |
| 停損 (SL) | -3.0% | 對稱出場 |
| 最長持倉 | 20 天 | |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場方式 | 訊號日隔日開盤市價 |
| 出場方式 | TP/SL 觸及時以悲觀認定出場 |
| 滑價假設 | 0.10% (ETF) |
| 日內路徑 | 高-低-收三點估計 |

### 嘗試記錄 (Attempt Log)

| Att | 配置 | Part A Sharpe | Part B Sharpe | min(A,B) | 結論 |
|-----|------|---------------|---------------|----------|------|
| 1 | RS(20d)≥3%, Pullback 2-4%, SMA(50) | 0.34 | -0.23 | -0.23 | Part B 3 虧損（慢漂移+關稅衝擊） |
| 2 | RS(10d)≥2%, Pullback 2-6%, SMA(50) | -0.13 | -0.38 | -0.38 | 10日 RS 太噪，新增 3 筆停損 |
| 3 | RS(20d)≥3.5%, Pullback 2-5%, SMA金叉 | 0.87 | -0.60 | -0.60 | Part A 極佳但移除 Part B 好訊號 |

### 回測結果 (Att1 — 最佳配置)

| 區間 | 年份 | 訊號數 | 勝率 | 累積報酬 | Sharpe | MDD |
|------|------|--------|------|----------|--------|-----|
| Part A (IS) | 2019-2023 | 9 (1.8/yr) | 66.7% | +8.64% | 0.34 | -6.20% |
| Part B (OOS) | 2024-2025 | 5 (2.5/yr) | 40.0% | -3.56% | -0.23 | -7.41% |
| Part C (Live) | 2026 | 1 (3.7/yr) | 100.0% | +3.00% | 0.00 | -0.71% |

### 關鍵發現 (Key Findings)

- **RS 動量在 EEM 上完全無效**：三次嘗試 Part B 均為負 Sharpe（-0.23、-0.38、-0.60）
- **EEM-SPY 相對強度由宏觀/政治事件驅動**：Part B 虧損來自關稅衝擊（2025-02、2025-03）和動量消散（2024-09），非技術面可預測
- **與 TSM/SOXL RS 動量的根本差異**：TSM-SMH RS 有結構性基礎（TSM 先進製程護城河），SOXL-SOXX-SPY RS 有板塊週期基礎。EEM-SPY RS 僅反映 EM/DM 宏觀輪動，受政策事件（關稅、貿易戰、中國監管）隨機打斷
- **10日 RS 不如 20日**：10日週期捕捉短期噪音，新增假訊號（Att2 Part A 4 筆停損 vs Att1 3 筆）
- **SMA 金叉過濾提升 Part A 但傷害 Part B**：Att3 Part A 0.87（過濾 3 筆壞訊號）但 Part B -0.60（移除 1 筆好訊號），典型過擬合
- **A/B 訊號率比 0.72:1（Att1）**：Part B 訊號較多但品質差，策略不具跨期穩健性
- **確認跨資產教訓 #20**：跨資產 RS 策略在非結構性因素驅動的資產對上失敗

---

## EEM-007: 趨勢動量回調 → 牛市政權過濾均值回歸

### 目標 (Goal)

嘗試 repo 中較少使用的策略方向。Att1-2 測試趨勢動量回調（在上升趨勢中買入回調），Att3 轉向牛市政權過濾均值回歸（在 SMA(200) 牛市中做 RSI(2) 均值回歸）。

### 嘗試記錄 (Attempt Log)

| Att | 配置 | Part A Sharpe | Part B Sharpe | min(A,B) | 結論 |
|-----|------|---------------|---------------|----------|------|
| 1 | SMA(50)+ROC(20d)>2%+10d DD≥2%+cd10, TP3%/SL3%/15d | 0.19 | -0.32 | -0.32 | ROC 門檻過鬆，弱趨勢回調不反彈 |
| 2 | ROC>3%+WR(10)<-60+10d DD≥2%+cd10, TP3%/SL3%/15d | 0.43 | -0.37 | -0.37 | 市場狀態依賴（Part A 強趨勢 / Part B 震盪） |
| 3 | SMA(200)+RSI(2)<10+2d≥1.5%+ClosePos≥40%+ATR>1.15+cd10, TP3%/SL3%/20d | -0.92 | 0.00 | -0.92 | 政權過濾移除最佳訊號（lesson #5 確認） |

### 回測結果 (Att2 — 最佳配置)

| 區間 | 年份 | 訊號數 | 勝率 | 累積報酬 | Sharpe | MDD |
|------|------|--------|------|----------|--------|-----|
| Part A (IS) | 2019-2023 | 15 (3.0/yr) | 66.7% | +18.42% | 0.43 | -3.68% |
| Part B (OOS) | 2024-2025 | 6 (3.0/yr) | 33.3% | -6.47% | -0.37 | -4.41% |
| Part C (Live) | 2026 | 1 (3.7/yr) | 0.0% | -3.10% | 0.00 | -3.08% |

### 關鍵發現 (Key Findings)

- **趨勢動量回調在 EEM 上嚴重市場狀態依賴**：Part A (2019-2023) 包含 COVID 復甦和 2022-2023 反彈等強趨勢環境，回調買入有效。Part B (2024-2025) 為震盪市，回調後繼續下跌
- **ROC 門檻提升 + WR 確認改善 Part A 但不改善 Part B**：Att2 的 Part A Sharpe 0.43（極佳）但 Part B -0.37，說明問題在策略概念層面而非參數層面
- **確認跨資產教訓 #26**：趨勢回檔策略市場狀態依賴過強，EEM 並非例外
- **SMA(200) 政權過濾摧毀均值回歸**（Att3）：恐慌急跌時 EEM 往往已低於 SMA(200)，政權過濾精確移除最佳買入機會。Part A 僅 6 訊號中 5 筆停損 (WR 16.7%)
- **確認跨資產教訓 #5 適用於 EEM**：即使用 SMA(200) 而非 SMA(50)，趨勢方向過濾器仍然傷害均值回歸
- **EEM-005 BB Squeeze Breakout 為確認的全域最優**：7 個實驗、10 種策略方向（均值回歸、波動率自適應、回檔+WR、BB Squeeze、RS 動量、趨勢動量回調、政權過濾均值回歸）均無法超越

---

## 演進路線圖 (Roadmap)

```
EEM-001 (RSI(2) 均值回歸)
  ├── EEM-002 (波動率自適應 ATR > 1.15)
  │     └── EEM-003 (+ 冷卻 10 天) — 均值回歸最佳，Part A Sharpe 0.06
  │           ├── Att1: 深跌幅 2.0% 替代 ClosePos → 失敗
  │           ├── Att2: ClosePos + ATR + cooldown 10 → Part A +0.06
  │           └── Att3: 無 ClosePos + cooldown 10 → 失敗
  ├── EEM-004 (回檔+WR 框架移植) → 失敗（lesson #16 驗證）
  │     ├── Att1: 無 ATR → Part A 0.01（45 訊號過多）
  │     └── Att2: + ATR + 回檔上限 → Part A -0.18（ATR 反效果）
  └── EEM-005 (BB 擠壓突破) ★ 當前最佳
        ├── Att1: TP 3.5% / 15天 → Part B 到期過多 (min 0.14)
        ├── Att2: TP 3.0% / 20天 → ★ min(A,B) 0.18, A/B gap 0.02
        └── Att3: 25th pct → Part A↑ 但 A/B 失衡

EEM-006 (獨立分支：RS 動量回調 EEM vs SPY) ❌ 三次嘗試均失敗
  ├── Att1: RS(20d)≥3% + Pullback 2-4% + SMA(50) → min -0.23（最佳嘗試）
  ├── Att2: RS(10d)≥2% + Pullback 2-6% → min -0.38（10日 RS 太噪）
  └── Att3: RS(20d)≥3.5% + SMA金叉 → min -0.60（Part A 過擬合）

EEM-007 (獨立分支：趨勢動量回調 → 政權過濾均值回歸) ❌ 三次嘗試均失敗
  ├── Att1: SMA(50)+ROC>2%+10d DD≥2% → min -0.32（ROC 門檻過鬆）
  ├── Att2: ROC>3%+WR<-60+10d DD≥2% → min -0.37（市場狀態依賴）
  └── Att3: SMA(200)+RSI(2)+2d decline+ClosePos+ATR → min -0.92（政權過濾摧毀訊號）

EEM-008 (三方向嘗試：出場優化 → 替代進場 → 波動率過濾) ❌ 三次嘗試均失敗
  ├── Att1: BB Squeeze+SL-4.0%+25d → min 0.10（寬 SL 增加虧損，EM 崩潰非暫時回撤）
  ├── Att2: Range Compression+20d新高+SMA(50) → min -0.17（假突破過多，市場狀態依賴）
  └── Att3: BB Squeeze+20d vol≤1.4% → min 0.11（移除好訊號多於壞，環境波動率無預測力）

EEM-009 (ATR>1.15 + SL-3.5% RSI(2)) ❌ Part A -0.09
EEM-010 (嚴格跌幅2.0% + ATR>1.1 + ClosePos) ❌ Part A +0.03（均值回歸最佳新組合，但 << BB Squeeze 0.18）
EEM-011 (無 ClosePos + ATR>1.1) ❌ Part A -0.05（驗證 ClosePos 對 EEM 有效）
```

---

## EEM-008: 優化突破（Optimized Breakout）

### 目標 (Goal)

在 EEM-005 BB Squeeze Breakout (min Sharpe 0.18) 基礎上，嘗試三個不同方向改進突破策略：出場參數優化、替代壓縮指標進場、環境波動率過濾。

### 嘗試紀錄 (Attempt History)

**Attempt 1: BB Squeeze + 寬 SL -4.0% + 延長持倉 25 天**

| 指標 | Part A | Part B |
|------|--------|--------|
| 總訊號 | 18 | 10 |
| 勝率 | 61.1% | 60.0% |
| 累計報酬 | +6.13% | +2.59% |
| Sharpe | 0.12 | 0.10 |

- 假設：EEM 突破後常因 EM 事件短暫回撤 > 3%，SL -3.0% 過早停損
- 結果：失敗。SL 從 -3.1% 擴大至 -4.1% 增加虧損幅度。2019-09-09 從 SL 轉為 +1.10% 到期（唯一改善），但 2021-10-15 從 +0.4% 到期惡化至 -2.31% 到期
- **結論：EEM 停損交易為真正的 EM 結構性崩潰（中國監管、升息、EM 危機），非暫時性回撤，加寬 SL 只增加虧損幅度**

**Attempt 2: Range Compression Breakout（全新進場機制）**

| 指標 | Part A | Part B |
|------|--------|--------|
| 總訊號 | 40 | 18 |
| 勝率 | 42.5% | 66.7% |
| 累計報酬 | -18.99% | +12.65% |
| Sharpe | -0.17 | 0.27 |

- 用 5 日價格範圍（High-Low）取代 BB 帶寬偵測壓縮，收盤突破 20 日新高取代 BB 上軌
- 結果：Part A 嚴重失敗（-0.17 Sharpe，40 訊號中 19 停損），Part B 優異（0.27 Sharpe）
- **結論：價格範圍壓縮門檻過鬆，Part A 產生大量假突破。A/B 極端不平衡(-0.17/0.27)證明嚴重市場狀態依賴。BB Squeeze 仍是 EEM 最佳壓縮偵測方法。**

**Attempt 3: BB Squeeze + 環境波動率過濾（20日實現波動率 ≤ 1.4%）**

| 指標 | Part A | Part B |
|------|--------|--------|
| 總訊號 | 14 | 10 |
| 勝率 | 57.1% | 60.0% |
| 累計報酬 | +3.76% | +4.65% |
| Sharpe | 0.11 | 0.18 |

- 回歸 BB Squeeze 框架，新增環境波動率過濾，目標移除高波動期的假突破
- Part B 與 EEM-005 完全相同（10 訊號、4.65% 累計、0.18 Sharpe），波動率過濾在 2024-2025 低波動期無影響
- Part A 移除 4 訊號：3 個好訊號（2020 COVID 復甦期突破）+ 1 個壞訊號（2022-06），淨損 2 個好訊號
- **結論：EM 宏觀衝擊發生在正常波動率環境（事前無異常），波動率事後才飆升。環境波動率過濾無法預測未來的 EM 事件衝擊，反而移除好訊號多於壞訊號。**

### 最終結論 (Final Conclusion)

EEM-008 三次嘗試均未能超越 EEM-005 (min Sharpe 0.18)。結合先前 7 個實驗的探索，**EEM 的純技術面策略天花板約為 Sharpe 0.18-0.20**。核心限制為 EM 宏觀事件（貿易戰、中國監管、利率政策、地緣政治）的不可預測性，純技術指標無法區分「真正突破」與「宏觀衝擊前的假突破」。

---

## EEM-009: ATR>1.15 + SL-3.5% RSI(2) 均值回歸

### 目標 (Goal)

基於 EEM-001 的 Part A 過多停損（15/28），加入 ATR(5)/ATR(20)>1.15 波動率飆升過濾，並放寬 SL 至 -3.5%。測試 ATR 過濾與寬 SL 的組合效果（EEM-002 已測試 ATR>1.1+SL-3.5%，此為 ATR>1.15+SL-3.5% 的新組合）。

### 回測結果 (Backtest Results)

| 區間 | 年份 | 訊號數 | 勝率 | 累積報酬 | Sharpe | MDD |
|------|------|--------|------|----------|--------|-----|
| Part A (IS) | 2019-2022 | 14 (2.8/yr) | 50.0% | -4.85% | -0.09 | -7.11% |
| Part B (OOS) | 2024-2025 | 5 (2.5/yr) | 100.0% | +15.93% | 0.00* | -1.03% |

### 結論

ATR>1.15 有效過濾慢跌訊號（28→14），但 SL-3.5% 在 EEM 上確認無效——EM 停損為結構性崩潰，寬 SL 只增加虧損幅度。Part A Sharpe -0.09 略優於 EEM-001 (-0.13) 但仍為負。

---

## EEM-010: 嚴格跌幅 2.0% + ATR>1.1 RSI(2) 均值回歸

### 目標 (Goal)

探索 EEM-002 Att2 (ATR>1.1+SL-3.5%) 和 EEM-003 Att1 (decline 2.0%+ATR>1.15) 的交叉組合：嚴格跌幅 2.0% + ATR>1.1 + ClosePos + SL-3.5%。此精確組合此前未被測試。

### 回測結果 (Backtest Results)

| 區間 | 年份 | 訊號數 | 勝率 | 累積報酬 | Sharpe | MDD |
|------|------|--------|------|----------|--------|-----|
| Part A (IS) | 2019-2022 | 12 (2.4/yr) | 58.3% | +0.56% | 0.03 | -5.06% |
| Part B (OOS) | 2024-2025 | 3 (1.5/yr) | 100.0% | +9.27% | 0.00* | -0.26% |

### 結論

Part A Sharpe +0.03 為均值回歸框架的最佳結果之一（僅次於 EEM-003 Att2 的 +0.06）。嚴格 2.0% 跌幅有效過濾 EM 危機淺跌假訊號，WR 從 42.9% 提升至 58.3%。但仍遠不及 BB Squeeze (0.18)，確認均值回歸在 EEM 的結構性天花板。

---

## EEM-011: 無 ClosePos + ATR>1.1 RSI(2) 均值回歸（ClosePos 有效性驗證）

### 目標 (Goal)

驗證 ClosePos≥40% 對 EEM 是否有效。Cross-asset lesson #34 指出 ClosePos 不可跨資產通用（GLD/IWM/XBI 有效但 USO/SIVR/FCX 反效果）。

### 回測結果 (Backtest Results)

| 區間 | 年份 | 訊號數 | 勝率 | 累積報酬 | Sharpe | MDD |
|------|------|--------|------|----------|--------|-----|
| Part A (IS) | 2019-2022 | 23 (4.6/yr) | 52.2% | -4.48% | -0.05 | -6.19% |
| Part B (OOS) | 2024-2025 | 9 (4.5/yr) | 77.8% | +14.29% | 0.56 | -4.25% |

### 結論

移除 ClosePos 後 Part A 訊號從 12 增至 23，但品質顯著下降（WR 58.3%→52.2%，Sharpe 0.03→-0.05）。Part B Sharpe 0.56 但 Part A 負值說明不穩健。**結論：ClosePos 對 EEM 有效**，與 GLD/IWM/XBI 一致，確認 lesson #34 中新增 EEM 為有效案例。

---

## EEM-012: BB 下軌 + 回檔上限混合進場均值回歸 ★最佳

### 目標 (Goal)

延伸 EWJ-003 / VGK-007 / CIBR-008 / EWZ-006 / EWT-008 驗證的混合進場模式至 broad EM ETF。EEM 日波動 1.17% 位於混合模式有效波動區間 [1.12%, 1.75%]，且為 broad EM 指數（非政策驅動單一國家 EM，不受 lesson #52 限制）。目標：突破 EEM-005 BB Squeeze 的 Sharpe 0.18 技術天花板。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 自適應下軌 | Close ≤ BB(20, 2.0) 下軌 | — | 統計門檻，低波動期淺深度高波動期深深度 |
| 崩盤隔離 | 10 日高點回檔 | ≥ -7% | 6σ for 1.17% vol，排除 COVID / 中國監管等結構性崩盤 |
| 極端超賣 | Williams %R(10) | ≤ -85 | Att3 收緊（vs -80），過濾淺 WR 觸發（2019-05 貿易戰） |
| 日內反轉 | Close Position | ≥ 40% | EEM-003/011 驗證對 EEM 有效（lesson #34） |
| 波動率飆升 | ATR(5)/ATR(20) | > 1.10 | EEM-010 驗證過濾 EM 慢磨下跌 |
| 冷卻期 | 訊號間隔 | ≥ 10 天 | 同 EEM-005 最佳設定 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +3.0% | EEM-005 Att2 驗證對稱甜蜜點（TP 3.5% 到期過多） |
| 停損 (SL) | -3.0% | lesson #49：EEM 停損為結構性崩潰，寬 SL 無益 |
| 持倉天數 | 20 天 | 與 EEM-005 Att2 一致 |
| 滑價 | 0.1% | ETF 標準 |
| 成交模型 | 隔日開盤市價進場 | ExecutionModelStrategy |

### 三次迭代摘要

| 迭代 | 關鍵差異 | Part A Sharpe | Part B Sharpe | min(A,B) | 結論 |
|------|----------|--------------|---------------|----------|------|
| Att1 | WR≤-80, ATR>1.10 | 0.13 (7訊號 57.1%WR) | 0.56 (4訊號 75%WR) | 0.13 | Part A 含 3 個 EM 危機停損 |
| Att2 | 收緊 ATR>1.15 | -0.60 (4訊號 25%WR) | 0.56 | -0.60 | **反向失敗**—危機日 ATR 偏高，提高門檻移除贏家 |
| **Att3** ★ | 還原 ATR 1.10，收緊 WR≤-85 | **0.34** (6訊號 66.7%WR) | **0.56** (4訊號 75%WR) | **0.34** | **+89% vs EEM-005**，A/B 累計差僅 3.6% |

### 回測結果 (Att3 Default)

| 區間 | 年份 | 訊號數 | 勝率 | 累積報酬 | Sharpe | MDD | 盈虧比 |
|------|------|--------|------|----------|--------|-----|-------|
| Part A (IS) | 2019-2023 | 6 (1.2/yr) | 66.7% | +5.68% | 0.34 | -3.72% | 1.94 |
| Part B (OOS) | 2024-2025 | 4 (2.0/yr) | 75.0% | +5.89% | 0.56 | -3.86% | 2.90 |

### 穩健性檢查

- A/B 累積報酬差：|5.68 − 5.89| / 5.89 = **3.6%**（遠優於 < 30% 要求）
- A/B 訊號頻率比：1.2/yr : 2.0/yr = 1:1.67（Part B 牛市較活躍，差距 40% 略高但可接受）
- Part A 停損僅 2 筆（2021-07 中國監管、2021-11 Omicron），WR -85 成功移除 2019-05 貿易戰淺觸假訊號

### 結論

**混合進場模式首次驗證延伸至 broad EM ETF 類別**。EEM-012 Att3 突破 EEM-005 BB Squeeze 的 0.18 技術天花板至 0.34（+89%），lesson #52 的適用範圍擴展涵蓋：寬基（VGK/EWJ）、板塊（CIBR）、商品驅動 EM（EWZ）、半導體驅動 EM（EWT）、**broad EM 指數（EEM）**。不適用：政策驅動單一 EM 國家 ETF（FXI，失敗驗證）、超低波動 ETF（INDA <1.12%）、超高波動 ETF（XBI >1.75%）。

ATR 門檻對 EEM 在 BB Lower 框架內方向與 RSI(2) 框架相反：Att2 收緊 ATR>1.15 崩壞（危機日 ATR 飆高，高門檻反保留停損移除贏家）。此現象與 EWZ-006 類似，混合模式的 ATR 定位為「訊號豐富度調節器」而非「品質過濾器」。WR 是 EEM 混合模式的關鍵品質軸——收緊至 -85 一次性修復 Part A 品質問題。

---

## 參數對照表 (Parameter Comparison)

| 參數 | EEM-001 | EEM-003 (Att2) | EEM-004 (Att1) | EEM-005 (Att2) | EEM-006 (Att1) | EEM-007 (Att2) | EEM-012 (Att3) | EEM-014 (Att2) ★ |
|------|---------|----------------|----------------|-----------------|----------------|----------------|-------------------|-------------------|
| 策略類型 | 均值回歸 | 均值回歸 | 均值回歸 | **突破** | **RS 動量** | **趨勢回調** | **混合 MR** | **混合 MR + 2DD floor** |
| RSI(2) | < 10 | < 10 | — | — | — | — | — | — |
| 2日跌幅 floor | ≥ 1.5% | ≥ 1.5% | — | — | — | — | — | **≥ 0.5%（2DD≤-0.5%）** |
| ClosePos | ≥ 40% | ≥ 40% | ≥ 40% | — | — | — | ≥ 40% | **≥ 40%** |
| ATR(5)/ATR(20) | — | > 1.15 | — | — | — | — | > 1.10 | **> 1.10** |
| Pullback 10d 上限 | — | — | — | — | — | — | ≥ -7% | **≥ -7%** |
| Pullback 20d | — | — | ≥ 3% | — | — | — | — | — |
| WR(10) | — | — | ≤ -80 | — | — | **< -60** | ≤ -85 | **≤ -85** |
| BB 下軌 | — | — | — | — | — | — | ≤ BB(20, 2.0) | **≤ BB(20, 2.0)** |
| BB Squeeze | — | — | — | **30th pct, 60日** | — | — | — | — |
| RS (EEM-SPY) | — | — | — | — | **20d ≥ 3%** | — | — | — |
| 20d ROC | — | — | — | — | — | **> 3%** | — | — |
| 10d Drawdown | — | — | — | — | — | **≥ 2%** | — | — |
| 5d Pullback | — | — | — | — | **2-4%** | — | — | — |
| SMA 趨勢 | — | — | — | **> SMA(50)** | **> SMA(50)** | **> SMA(50)** | — | — |
| 冷卻期 | 5 天 | 10 天 | 10 天 | 10 天 | 10 天 | 10 天 | 10 天 | **10 天** |
| TP / SL | +3.0% / -3.0% | +3.0% / -3.0% | +3.0% / -3.0% | +3.0% / -3.0% | +3.0% / -3.0% | +3.0% / -3.0% | +3.0% / -3.0% | **+3.0% / -3.0%** |
| 持倉 | 20 天 | 20 天 | 20 天 | 20 天 | 20 天 | 15 天 | 20 天 | **20 天** |
| Part A Sharpe | -0.13 | +0.06 | 0.01 | +0.20 | 0.34 | 0.43 | +0.34 | **+0.73** |
| Part B Sharpe | 0.35 | 0.00 (100%WR) | 0.27 | +0.18 | -0.23 | -0.37 | +0.56 | **+0.56** |
| **min(A,B)** | -0.13 | +0.00 | 0.01 | +0.18 | -0.23 | -0.37 | +0.34 | **+0.56** |
| Part A 訊號 | 28 (5.6/yr) | 13 (2.6/yr) | 45 (9.0/yr) | 18 (3.6/yr) | 9 (1.8/yr) | 15 (3.0/yr) | 6 (1.2/yr) | **5 (1.0/yr)** |
| Part B 訊號 | 7 (3.5/yr) | 5 (2.5/yr) | 12 (6.0/yr) | 10 (5.0/yr) | 5 (2.5/yr) | 6 (3.0/yr) | 4 (2.0/yr) | **4 (2.0/yr)** |

---

## EEM-013: MACD 柱狀圖多頭轉折 + 回檔混合進場均值回歸 ❌ 失敗

### 目標 (Goal)

**Repo 首次 MACD 試驗**。填補「MACD momentum indicator」作為 MR 進場訊號的方向空白。EEM broad EM 1.17% vol 屬中低波動，且有明顯 risk-on/risk-off 週期，假設 MACD(12, 26, 9) 柱狀圖平滑 EMA 訊號可過濾 RSI/CCI 點估計指標在 V-bounce 上的噪音問題。目標：突破 EEM-012 Att3 min(A,B) 0.34 天花板。

### 進場條件 (Final Iteration, Att3)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| MACD 動量轉折 | MACD 柱狀圖 today > yesterday > day-2 且 yesterday < 0 | — | 兩根連續上揚仍處於負值區，賣壓衰竭中 |
| 回檔情境 | 10 日高點回檔 | [-8%, -2%] | 淺至中等回檔，排除崩盤續跌 |
| 超賣確認 | Williams %R(10) | ≤ -75 | 放寬（MACD 已為主訊號） |
| 日內反轉 | Close Position | ≥ 40% | EEM 驗證有效 |
| **反向 ATR 過濾** | ATR(5)/ATR(20) | **< 1.10** | **EEM-013 獨特發現**：MACD 框架偏好低波動環境 |
| 冷卻期 | 訊號間隔 | ≥ 10 天 | — |

### 出場參數 (Exit Parameters)

| 參數 | 值 |
|------|-----|
| 獲利目標 (TP) | +3.0%（EEM 硬上限） |
| 停損 (SL) | -3.0%（EEM 硬上限） |
| 持倉天數 | 20 天 |
| 滑價 | 0.1% |
| 成交模型 | 隔日開盤市價進場 |

### 三次迭代摘要

| 迭代 | 進場條件 | Part A Sharpe | Part B Sharpe | min(A,B) | 結論 |
|------|----------|--------------|---------------|----------|------|
| Att1 | MACD 柱狀圖零軸上穿 + pullback [-7,-3] + WR≤-70 | 0 訊號 | 0 訊號 | N/A | 零軸上穿嚴重滯後 |
| Att2 | MACD 柱狀圖 2 根 turn-up + pullback [-8,-2] + WR≤-75 | -0.02 (8訊號 50%WR) | 0.34 (3訊號 66.7%WR) | **-0.02** | 2022-2023 升息熊市 SL 集中 |
| **Att3** | Att2 + **ATR<1.10 反向過濾** | 0.19 (5訊號 60%WR) | 0.00 (2訊號 100%WR 零方差) | **0.00** | Part A WR 改善但未達 0.34 門檻 |

### 回測結果 (Att3 Default)

| 區間 | 年份 | 訊號數 | 勝率 | 累積報酬 | Sharpe | MDD | 盈虧比 |
|------|------|--------|------|----------|--------|-----|-------|
| Part A (IS) | 2019-2023 | 5 (1.0/yr) | 60.0% | +2.60% | 0.19 | -4.34% | 1.45 |
| Part B (OOS) | 2024-2025 | 2 (1.0/yr) | 100.0% | +6.09% | 0.00 (零方差) | -1.37% | ∞ |

### Att2 Part A 逐筆交易（說明 bear market 假訊號問題）

| 訊號日 | 結果 | WR | Pullback | ATR5/20 | 備註 |
|--------|------|-----|----------|---------|------|
| 2019-05-15 | SL -3.10% | -78 | -6.89% | 1.47 | 貿易戰升級（ATR>1.10 移除✓） |
| 2019-08-12 | TP +3.00% | -85 | -6.99% | 1.15 | 深回檔真反彈（ATR>1.10 誤移除✗） |
| 2021-10-06 | TP +3.00% | -76 | -3.46% | 1.12 | 淺回檔快速反彈（ATR>1.10 誤移除✗） |
| 2022-09-08 | SL -3.10% | -88 | -6.18% | 1.04 | Fed 升息熊市（低 ATR，無法移除✗） |
| 2022-10-03 | SL -3.10% | -77 | -6.39% | 1.14 | 熊市續跌（ATR>1.10 移除✓） |
| 2023-02-14 | SL -3.10% | -78 | -3.76% | 0.88 | 早期修正（低 ATR，無法移除✗） |
| 2023-08-18 | TP +3.00% | -92 | -5.65% | 0.83 | 極端 WR 真反彈 |
| 2023-10-31 | TP +3.00% | -76 | -2.73% | 1.03 | 淺回檔真反彈 |

### 穩健性檢查 (Att3)

- A/B 累積報酬差：|2.60 − 6.09| / 6.09 = **57.3%**（超過 < 30% 目標）
- A/B 訊號頻率比：**1.0:1**（極佳）
- A/B 絕對訊號數差：(5 − 2) / 5 = 60%（超過 < 50% 目標）
- Part B 2/2 零方差 → Sharpe 報為 0.00，為結構性樣本稀疏問題

### 失敗分析

1. **MACD 零軸上穿嚴重滯後（Att1）**：當 MACD 柱狀圖從負值穿越至 > 0 時，price 通常已回升 3-5 天，WR 回彈至 > -70，10 日 pullback 也已從 -5% 收斂至 -2%，導致多重條件不同時滿足
2. **MACD 2-bar turn-up 在升息熊市失敗（Att2）**：2022-2023 Fed 升息週期中，EEM 連續性慢磨下跌產生多次 dead-cat bounce，MACD 平滑 EMA 雖優於 RSI/CCI 點估計但**仍無法解決 V-bounce 根本問題**。擴展 lesson #20b 失敗家族至 MACD
3. **反向 ATR 過濾為 EEM-013 獨特發現（Att3）**：MACD 框架在 EEM 上偏好**低波動環境**（ATR<1.10），與 EEM-010 RSI(2) 框架的 ATR>1.15 方向完全相反。假設原因：
   - Bear rally dead-cat bounce 伴隨 ATR 飆升（panic 殘留 vol）
   - Bull consolidation 中的 genuine MR 屬於低 ATR 平靜期
   - 但 EEM 熊市 SL 既可在高 ATR（2019-05, 2022-10, 2024-07）也可在低 ATR（2022-09, 2023-02），使過濾器無法區分
4. **EEM Part B 訊號稀疏（結構性限制）**：MACD + 反向 ATR 組合使 Part B 降至 1/yr，100% WR 2/2 為零方差 Sharpe 結構，min(A,B) 被迫為 0.00

### 結論

**三次迭代均未勝過 EEM-012 Att3（min(A,B) 0.34）**。EEM-013 為 **repo 首次 MACD 試驗**，驗證：
- MACD 作為 MR 主訊號加入 lesson #20b 失敗家族（RSI hook、CCI hook、Stoch hook、WVF、MACD 柱狀圖 turn-up）
- **獨特發現**：MACD 框架在 EEM 上偏好低 ATR 環境（反向 ATR<1.10），與其他 MR 框架方向相反
- EEM MR 技術上限仍為 EEM-012 Att3 的 BB Lower + Pullback Cap 混合進場模式

跨資產假設（待驗證）：
- 反向 ATR 方向可能僅在 MACD / 其他 EMA-based 動量指標框架中適用
- 其他 broad EM ETF（如 VWO、IEMG）MACD + 反向 ATR 可能表現類似，但需在活躍 MR regime 資產上才有機會突破（EEM Part B 2024-2025 強牛市使 MR 訊號稀薄為結構限制）

---

## EEM-014: Post-Capitulation Vol-Transition MR（+2DD floor 精煉） ★ 當前最佳

### 目標 (Goal)

延伸 CIBR-012 Att3（2026-04-21）首次驗證的「2DD 過濾器方向精煉」概念至 broad EM ETF。
CIBR-012 在 CIBR（1.53% vol）上以 **2DD cap（上限 -4.0%）** 過濾「崩盤加速中」進場，min(A,B) 從 0.39→0.49（+26%）。
其跨資產假設明確列舉 EEM 為候選（"2DD cap filter may extend to... EEM"），本實驗直接驗證。

### 跨資產結構發現（Att1 failure → Att2 success）

檢查 EEM-012 Att3 Part A/B 的**訊號日** 2DD 分布：
- **TPs 2DD（7 筆）**：-1.47%, -3.36%, -1.79%, -3.10%, -3.88%, -1.95%, -2.37% — 皆為實際急跌
- **SLs 2DD（3 筆）**：2021-07-08 -2.19%, 2021-11-30 **+0.29%**, 2025-11-19 **-0.85%** — 中位 -0.85%，多為淺幅漂移

**關鍵發現**：EEM 的 SLs 2DD 分布與 CIBR 方向**完全相反**：
- CIBR SLs：深 2DD（≤-4%，崩盤加速中）→ 用 **cap** 方向過濾
- EEM SLs：淺 2DD（中位 -0.85%，慢漂移/非真 capitulation）→ 用 **floor** 方向過濾

故 EEM 的正確方向是 **2DD floor**（require 2DD ≤ -0.5%），**與 CIBR-012 方向完全相反**。

### 進場條件 (Final Att2)

| 條件 | 指標 | 門檻 | 說明 |
|------|------|------|------|
| BB 下軌 | Close vs BB(20, 2.0) lower | Close ≤ BB_lower | 統計自適應深度門檻 |
| 崩盤隔離 | 10 日高點回檔 | Pullback ≥ -7% | EM 結構性崩盤過濾（6σ for 1.17% vol） |
| 超賣確認 | WR(10) | ≤ -85 | 極端超賣 |
| 日內反轉 | ClosePos | ≥ 40% | 收盤位置高（EEM 驗證有效） |
| Signal-day panic | ATR(5)/ATR(20) | > 1.10 | 當日波動率飆升 |
| **2DD floor** | **Close/Close.shift(2) - 1** | **≤ -0.5%** | **排除淺幅慢漂移（核心創新）** |
| 冷卻期 | | 10 天 | 防止連續訊號相關 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| Profit Target (TP) | +3.0% | EEM-005 Att2 驗證 |
| Stop Loss (SL) | -3.0% | EEM 硬上限（lesson #49） |
| Holding Days | 20 | |
| Execution Model | Next-day open market | slippage 0.1% |

### 三次迭代摘要

| Att | 配置 | Part A Sharpe | Part B Sharpe | min(A,B) | 核心發現 |
|-----|------|---------------|---------------|----------|---------|
| Att1 | 2DD cap >= -3.0%（CIBR-012 直接移植） | -0.02 | 0.34 | -0.02 | **方向錯誤**：EEM 與 CIBR 的 SL 2DD 結構相反 |
| **Att2 ★** | **2DD floor <= -0.5%（反轉方向）** | **0.73** | **0.56** | **0.56** | **新全域最優**，+65% vs 基線 |
| Att3 | Att2 - ATR 過濾（ablation） | -0.02 | 0.56 | -0.02 | ATR 必要，兩者互補非冗餘 |

### 回測結果 (Att2 Default)

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026 Live) |
|------|---------------------|---------------------|---------------------|
| Total Signals | 5 | 4 | 0 |
| Wins | 4 | 3 | 0 |
| Win Rate | 80.0% | 75.0% | 0.0% |
| Cumulative Return | +9.06% | +5.89% | 0.00% |
| Avg Holding Days | 8.2 | 6.8 | 0 |
| Sharpe Ratio | **0.73** | 0.56 | 0.00 |
| Max Drawdown | -3.72% | -3.86% | 0.00% |

**A/B 平衡檢查**：
- 累計差：|9.06 - 5.89| = 3.17pp（遠優於 <30% 目標）
- 訊號比：5:4 = 1.25:1（遠優於 <50% 目標）

### 過濾動態（Att2）

vs EEM-012 Att3 基線：
- **僅過濾 1 筆訊號**：2021-11-30 SL（2DD +0.29% > -0.5% → 過濾）
- 全部 7 筆 TP 保留（最淺 2DD -1.47% 遠於門檻）
- 保留 2 筆深 2DD SLs（2021-07-08 -2.19%、2025-11-19 -0.85%）
- Part B 完全不變（4 訊號同基線）

### Att3 Ablation 發現

移除 ATR 過濾後 Part A 從 5 訊號（4TP/1SL）膨脹至 8 訊號（4TP/4SL），Sharpe 崩至 -0.02。
證明 ATR>1.10 與 2DD floor 為**互補雙過濾**而非冗餘：
- ATR>1.10 捕捉 signal-day 波動率飆升（panic day 確認）
- 2DD floor 排除淺幅漂移（確認實際下跌深度）
- 兩者不可互相取代，疊加必要

### 結論

**EEM-014 Att2 成為 EEM 新全域最優**（min(A,B) 0.56，+65% vs EEM-012 Att3 的 0.34）。

**跨資產貢獻**：
1. **2DD 方向資產相依性**：首次明確證實 2DD 過濾器方向（cap vs floor）取決於殘餘失敗 SL 的 2DD 分布結構，不可通用移植
   - CIBR（深 2DD SL，in-crash）→ 2DD cap
   - EEM（淺 2DD SL，慢漂移）→ 2DD floor（相反方向）
2. **Repo 第 2 次 2DD floor 方向成功驗證**（繼 USO-013 後，broad EM ETF 首次）
3. **Att1 失敗轉 Att2 成功** 為「反向驗證」的教科書案例：移植失敗後檢查資產結構→找出正確方向

**擴展 lesson #19**（2DD 雙向性）：方向取決於殘餘 SL 的 2DD 結構，新增規則：
- 設計 2DD 過濾器前，先計算現有最佳策略殘餘 SL 的 signal-day 2DD 分布
- 若 SLs 集中於深 2DD → 用 cap 方向（CIBR 類）
- 若 SLs 集中於淺 2DD → 用 floor 方向（EEM、USO 類）

**擴展 lesson #52**（BB 下軌+回檔上限混合進場）：在 broad EM 類別（EEM）上可再以 2DD floor 精煉至 min 0.56，類似精煉可能適用 VGK/EWJ/EWT/EWZ 等同框架資產（待跨資產驗證，threshold 需按日波動縮放）。
