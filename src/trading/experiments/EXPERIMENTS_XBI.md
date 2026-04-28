<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-04-28
  data_through: 2025-12-31
  note: XBI-014 added 2026-04-28 (Post-Capitulation Vol-Transition MR, **repo 第 6 次「2DD floor 加深方向」跨資產試驗，首次 US 板塊 ETF 測試**, cross-asset port from VGK-008 / INDA-010 / EEM-014 / USO-013 / IBIT-009). Three iterations, all failed vs XBI-005 min 0.36 — **threshold sweep complete failure curve**: Att1 (drop_2d_floor=-2.0%, INDA/VGK 標準門檻) Part A 18/72.2%/Sharpe **0.24** cum +16.64% / Part B 6/66.7%/Sharpe 0.16 cum +3.37% / min **0.16** (-56% vs 0.36) — cooldown chain shift（lesson #19）將原 2024-03-14 TP（2DD -1.82% 不滿足）釋放成 2024-03-15 SL，淨增 1 筆 Part B SL。Att2 (drop_2d_floor=-2.5%，向 USO 2.20% vol 門檻靠攏) Part A 16/68.8%/Sharpe **0.16** cum +8.90% / Part B 5/80.0%/Sharpe 0.52 cum +8.90% / min **0.16** — Part A WR 從 baseline 76% → Att1 72.2% → Att2 68.8% **單調下降**，加深 floor 系統性移除 TPs 多於 SLs（Part A 殘餘 SL 2DD 分布 -1.03%~-5.53%，僅 1 筆 -1.03 可被 -1.5% floor 過濾，TPs 中 9/15 筆 2DD > -2.5% 被誤殺）。Att3 (drop_2d_floor=-1.0%，最輕度 ablation) Part A 20/75.0%/Sharpe **0.32** cum +24.96% / Part B 6/83.3%/Sharpe 0.64 cum +12.71% / min **0.32** — 三次最接近 baseline，僅過濾 2021-01-05 TP（2DD -0.23%）。**Threshold sweep 完整失敗曲線**：baseline（無 filter） 0.36 → -1.0% 0.32 → -2.0% 0.16 → -2.5% 0.16 單調退化，**確認 2DD floor 加深方向對 XBI 完全無效**。失敗根因：(1) XBI 2DD 分布 NO unidirectional selectivity——Part A SLs 範圍 -1.03%~-5.53%，TPs 範圍 -0.23%~-6.86%，重疊整個範圍；(2) XBI 生技板塊 FDA event-driven 性質使 V-bounce winners 涵蓋 shallow 2DD（短期反彈）與 deep 2DD（acute capitulation）兩極；(3) Cooldown chain shift（lesson #19）使任何 filter 對 Part B 引入「相鄰日轉移」的 SL。**Repo 第 6 次 2DD floor 加深方向跨資產試驗**，第 6 個確認**無效**的資產（繼 GLD-013 macro 商品 / COPX-010 礦業雙向 / FCX-011 高波動個股 / TSLA-014 高波動個股 / GLD-013 後）。**首次 US 板塊 ETF 測試**：Post-Capitulation Vol-Transition MR 模板 vol 適用範圍 [0.97%, 3.17%] 正確涵蓋 XBI 2.0% vol，但**驅動類別（FDA event-driven 板塊 ETF）使 winners 2DD 分布雙峰化**，與 INDA/EEM/VGK/USO/IBIT 的「shallow 2DD = drift」單峰失敗結構不同。整合規則更新：Post-Capitulation Vol-Transition MR（2DD floor 加深方向）有效條件需同時滿足 (a) vol ∈ [0.97%, 3.17%] AND (b) winners 2DD 分布單峰（broad ETF / 商品 / 加密 ETF），**事件驅動板塊 ETF（XBI FDA / CIBR 政策）winners 2DD 分布橫跨 shallow~deep 全段使任何單向 filter 失效**。XBI 第 11 個失敗策略類型（後於突破、ROC、動量回調、配對、ATR 自適應、RSI(2)、BB-lower 混合、RSI hook divergence、capitulation-accel、Gap-Down、**2DD floor**）。XBI-005 仍為全域最優（14 次實驗、44+ 次嘗試）。XBI-013 added 2026-04-22 (Gap-Down Capitulation + Intraday Reversal MR, **repo 第 5 次 Gap-Down 試驗，首次 US 板塊 ETF 測試**，cross-asset port from IBIT-006 Att2). Three iterations all failed vs XBI-005 min 0.36: Att1 (Gap ≤ -1.0% primary + Close>Open + 10d PB [-5%,-15%] + WR ≤ -80, TP +3.0%/SL -3.0%/15d) Part A 8/50% WR Sharpe **-0.02** cum -0.77%（4TP/4SL，全部 1-3 日出場）/ Part B 1/0% WR Sharpe 0.00 cum -3.10% / min **-0.02** — 生技 gap-down 為 FDA/臨床 negative news 續跌結構，非 IBIT 隔夜拋壓耗盡；Att2 (Gap as supplementary filter on XBI-005 base + ClosePos ≥ 35%) Part A 3/66.7% WR Sharpe 1.39 cum +7.08% / Part B 1/0% WR Sharpe 0.00 cum -5.10% / min **0.00** — Gap 濾波將 XBI-005 原 35/8 訊號濾至 3/1，樣本過薄且 Part B 唯一訊號 2024-01-17 仍 1 日 SL；Att3 (deep Gap ≤ -2.0% + wider pullback [-5%,-18%]) Part A 1/100% WR 零方差 Sharpe 0.00 / Part B 1/0% WR Sharpe 0.00 / min **0.00** — 深 gap 過嚴僅 1 訊號每 Part，Part B 2024-07-29 訊號仍 SL。**Repo 第 5 次 Gap-Down Capitulation MR 試驗** — 首次 US 板塊 ETF 測試。Gap-Down 失敗家族正式擴展為 4 大類（IBIT 為唯一成功）：(1) TQQQ-016（non-24/7 槓桿股指 ETF）(2) FXI-010（政策驅動 EM 單一國家 ETF）(3) FCX-010（商品關聯個股）(4) **XBI-013（US 板塊 ETF with 事件驅動 gap）**。整合失敗規則：Gap-Down MR 需要 (a) 24/7 連續交易 underlying AND (b) 拋壓耗盡與當日 session 不相關聯；XBI 生技板塊兩者皆不符——事件常盤後宣告產生跨 session 持續拋壓，平行 FXI 政策延續 / FCX 商品衝擊延續 / TQQQ 槓桿結構失敗。IBIT 為唯一合格 Gap-Down underlying。XBI 第 10 個失敗策略類型（後於突破、ROC 單獨、動量回調、配對、ATR 自適應、RSI(2)、BB-lower 混合、RSI hook divergence、capitulation-accel、Gap-Down）。XBI-005 仍為全域最優（13 次實驗、41+ 次嘗試）. XBI-012 added 2026-04-19 (Capitulation + Acceleration Reversal MR: Pullback(10) + ROC(3) + ClosePos + UpDay + WR). Three iterations all failed vs XBI-005 min 0.36. Att1 (ROC -4%, ClosePos 50%, UpDay) Part A 3/0.16 / Part B 3/0.16 — too restrictive, 0.6 yr signal. Att2 (ROC -3%, ClosePos 40%, UpDay) Part A 7/0.27 / Part B 3/0.16 — Part A improves +69% but Part B stuck because 2024-2025 XBI lacks ROC(3) ≤ -3% events. Att3 (ROC -3%, ClosePos 35%, no UpDay) Part A 21/0.18 / Part B 8/0.07 — signals triple but quality dilutes: UpDay filter confirmed essential. Extends XBI failure pattern list: short-term ROC acceleration + intraday recovery cannot distinguish genuine reversal from technical bounce on event-driven biotech ETF. XBI-005's pullback+WR+ClosePos 35% framework confirmed as structurally optimal for XBI 2.0% daily vol + FDA event-driven MR (13 experiments, 41+ attempts).
-->
## AI Agent 快速索引

**當前最佳：** XBI-005（回檔 8-20% + WR(10) ≤ -80 + ClosePos ≥ 35%，Part A Sharpe 0.36，Part B Sharpe 0.64）— **已確認為全域最優**（14 次實驗、44+ 次嘗試，含突破策略、ROC 策略、動量回調策略、配對交易策略、波動率自適應過濾、RSI(2) 獨立驗證、BB 下軌混合進場、RSI(14) bullish hook divergence、短期 ROC 急跌 + 日內反攻、Gap-Down Capitulation、**Post-Capitulation Vol-Transition MR（2DD floor）**）
**前任最佳：** XBI-001（同進場無 ClosePos，Part A Sharpe 0.11，Part B Sharpe 0.23）
**滾動窗口分析摘要：** XBI-001 ✗✓（精準度突變 ΔWR 23.8pp，績效漸變，2023 生技低迷為主因）

**已證明無效（禁止重複嘗試）：**
- 回檔 ≥ 6% 無上限（Part A 49 訊號過多，WR 53.1%，累計 -14.86%）
- 回檔 8-20% + WR ≤ -80 + 2日急跌 ≤ -3% + TP +4.0% / 20天（Att1：Part A Sharpe 0.03，WR 58.6%，2日急跌過濾移除好訊號）
- 回檔 8-15% + WR ≤ -80 + 2日急跌 ≤ -3% + TP +3.5% / 15天（Att2：Part A Sharpe -0.06，累計 -9.02%，收窄上限+2日急跌雙重過濾過度）
- RSI(2) < 10 + 2日跌幅 ≥ 3%（Att3：Part A Sharpe 0.00，Part B Sharpe -0.30/WR 44.4%，RSI(2) 框架對 XBI 無效）
- SL -4.0% / 20天（XBI-003 Att1：Part A Sharpe 0.03，SL 太緊，2021-2022 生技熊市交易需要寬 SL）
- SL -4.5% / 20天（XBI-003 Att2：Part A Sharpe 0.09，仍太緊，A/B 不平衡）
- SL -5.0% / 20天（XBI-003 Att3：Part A Sharpe 0.10，延長持倉無效果，平均持倉僅 3-5 天）
- 20日回看 + 回檔 10-20% + TP +4.0% + 冷卻12天（XBI-004 Att1：Part A Sharpe 0.02，20日回看移除好訊號多於壞訊號）
- 回檔 8-15% + 冷卻15天 + 20天持倉（XBI-004 Att2：Part A 0.04 / Part B 0.44，A/B 極度失衡）
- 回檔 8-15% + 冷卻15天 + 15天持倉（XBI-004 Att3：Part A 0.05 / Part B 0.44，收窄上限改善 Part B 但惡化 Part A）
- ClosePos ≥ 40%（XBI-005 Att1：Part A Sharpe 0.28 改善但 Part B 0.16 劣化，門檻太高移除 Part B 好訊號）
- ClosePos ≥ 30%（XBI-005 Att3：Part A Sharpe 0.30 vs 35% 的 0.36，門檻太低引入 Part A 壞訊號）
- BB Squeeze Breakout BB(20,2) 25th pct + SMA(50)（XBI-006 Att1：Part A Sharpe 0.05 / Part B 0.17，WR 50%/55.6%，假突破率過高）
- BB Squeeze Breakout BB(20,2) 15th pct + TP +4.0%（XBI-006 Att2：Part A Sharpe 0.18 / Part B 0.10，收緊百分位改善 Part A 但 Part B 劣化）
- 5日 ROC ≤ -8% + WR + ClosePos（XBI-006 Att3：Part A Sharpe 0.27 / Part B -0.19，僅 2 筆 Part B 訊號無統計意義）
- 動量回調 ROC(20)≥8% + 5日回撤 2.5-5% + SMA(50)，TP+5%/SL-5%（XBI-007 Att1：Part A Sharpe -0.01 / Part B -0.23，WR 50%/42.9%，動量回調在 XBI 上假訊號過多）
- 動量回調 ROC(20)≥12% + 5日回撤 3-7% + SMA(50)，TP+6%/SL-5%（XBI-007 Att2：Part A Sharpe 0.34 / Part B 僅 2 訊號全停損，ROC 12% 過嚴導致 Part B 訊號不足）
- 動量回調 ROC(20)≥8% + 5日回撤 3.5-6% + SMA(50)，TP+4%/SL-5%（XBI-007 Att3：Part A Sharpe 0.02 / Part B 0.44，最佳但 Part A 幾乎為零，A/B 比 3.5:1 嚴重失衡）
- XBI/IBB 配對交易 z<-2.0 + SMA(50)（XBI-008 Att1：Part A -0.19 (4訊號) / Part B 0.00 (1訊號)，z-score 進場太嚴格）
- XBI/IBB 配對交易 z<-1.5 無過濾（XBI-008 Att2：Part A -0.23 (41訊號) / Part B 0.07 (8訊號)，噪音太多 A/B 比 5.1:1）
- XBI/IBB 配對交易 z<-2.0 + WR(10)≤-80（XBI-008 Att3：Part A -0.00 (19訊號) / Part B -0.19 (4訊號)，最佳嘗試但仍無法盈利）
- ATR(5)/ATR(20) > 1.1 + XBI-005 框架（XBI-009 Att1：Part A Sharpe 0.27/Part B 0.16，ATR 門檻太嚴移除好訊號，Part A 21→7 訊號）
- ATR(5)/ATR(20) > 1.05 + XBI-005 框架（XBI-009 Att2：Part A Sharpe -0.08/Part B 0.36，降低門檻新增訊號反而是壞訊號）
- RSI(2) < 10 + 2日跌幅 ≥ 3.0% + ClosePos ≥ 35%（XBI-009 Att3：Part A Sharpe 0.04/Part B -0.04，RSI(2) 進場不如 pullback+WR 精確，WR 62.5%/57.1% vs XBI-005 的 76.2%/83.3%）
- BB(20, 1.5) 下軌 + cap -12% + WR + ClosePos 35%（XBI-010 Att1：Part A Sharpe 0.09/Part B 0.07，BB 1.5σ 在 XBI 2.0% 日波動下過鬆，20 訊號 WR 65% vs 76.2%，平均報酬 0.27% 遠低於 XBI-005 的 1.3%）
- BB(20, 2.0) 下軌 + cap -12% + WR + ClosePos 35%（XBI-010 Att2：Part A Sharpe -0.03/Part B -0.55，BB 2.0σ 訊號集中極端崩盤事件 7/3 筆，Part B WR 僅 33%）
- 混合 OR 進場 BB(20, 2.0) OR 回檔 ≥ 8% + cap -12% + WR + ClosePos 35%（XBI-010 Att3：Part A Sharpe 0.20/Part B 0.16，cap -12% 比 XBI-005 的 -20% 過嚴，移除深回檔贏家使 WR 從 76.2%→68.4%）
- RSI(14) bullish hook divergence + XBI-005 框架（XBI-011 Att1：RSI(14) lookback 5 / delta ≥ 3 / min ≤ 35，Part A 3/3 全 TP（零方差 Sharpe 0.00）/Part B 2/2 全 TP（零方差 Sharpe 0.00），過嚴，訊號年化 0.6/1.0，樣本量過少）
- RSI(14) bullish hook lookback 5 / delta 3 / min ≤ 40（XBI-011 Att2：Part A Sharpe 0.27（7 訊號 WR 71.4%，2 筆停損）/Part B 2/2 全 TP 零方差，放寬 oversold 門檻引入 Part A 壞訊號）
- RSI(14) bullish hook lookback 5 / delta 2 / min ≤ 35（XBI-011 Att3：同 Att1，delta 放寬未增訊號因 oversold 為綁定條件）
- Capitulation + Acceleration Reversal（Pullback ≤ -6% + ROC(3) ≤ -4% + ClosePos ≥ 50% + UpDay + WR ≤ -80）（XBI-012 Att1：Part A Sharpe 0.16 / Part B 0.16，訊號 3/3 過稀疏，ClosePos 50% + ROC(3) -4% 組合過嚴）
- Capitulation + Acceleration 放寬（ROC(3) ≤ -3% + ClosePos ≥ 40% + UpDay）（XBI-012 Att2：Part A Sharpe 0.27 / Part B 0.16，Part A +69% 但 Part B 訊號未變，2024-2025 XBI 牛市缺少 ROC(3) ≤ -3% 事件）
- Capitulation + Acceleration 無 UpDay（ROC(3) ≤ -3% + ClosePos ≥ 35% + 無 UpDay）（XBI-012 Att3：Part A Sharpe 0.18 / Part B 0.07，訊號 21/8 倍增但品質崩壞，UpDay 過濾器證實為關鍵品質軸）
- **Gap-Down Capitulation MR 作為主進場（XBI-013 Att1，repo 第 5 次 Gap-Down 試驗，首次 US 板塊 ETF 測試）**（Gap ≤ -1.0% + Close>Open + 10d Pullback [-5%,-15%] + WR(10) ≤ -80, TP +3.0%/SL -3.0%/15d）：Part A 8 訊號 50% WR Sharpe **-0.02** cum -0.77%（4TP/4SL，全部 1-3 日出場）/ Part B 1 訊號 0% WR Sharpe 0.00 cum -3.10%（1 日 SL）/ min(A,B) **-0.02**，失敗根因：生技 gap-down 為 FDA/臨床 negative news 續跌結構，非 IBIT 隔夜拋壓耗盡
- **Gap-Down 作為 XBI-005 框架上的補充品質過濾（XBI-013 Att2）**（XBI-005 base + Gap ≤ -1.0% + Close>Open）：Part A 3 訊號 66.7% WR Sharpe 1.39 cum +7.08% / Part B 1 訊號 0% WR Sharpe 0.00 cum -5.10% / min **0.00**，失敗根因：Gap 將 XBI-005 原 35/8 濾至 3/1（-90%），Part B 唯一訊號 2024-01-17 仍 1 日 SL，Gap 對 XBI 訊號品質無貢獻
- **深 Gap-Down Capitulation MR（XBI-013 Att3）**（Gap ≤ -2.0% + Close>Open + 10d Pullback [-5%,-18%] + WR(10) ≤ -80, TP +3.5%/SL -4.0%/15d）：Part A 1 訊號 100% WR 零方差 Sharpe 0.00 cum +3.50% / Part B 1 訊號 0% WR Sharpe 0.00 cum -4.10% / min **0.00**，失敗根因：深 gap 過嚴僅 1 訊號每 Part，Part B 2024-07-29 訊號仍 SL，XBI event-driven 結構對任何 gap 門檻都不適用
- **Post-Capitulation Vol-Transition MR（XBI-014 Att1，2DD floor -2.0%）**（XBI-005 base + Return_2d ≤ -2.0%）：Part A 18/72.2%/Sharpe 0.24 / Part B 6/66.7%/Sharpe 0.16 / min **0.16**，cooldown chain shift 引入 2024-03-15 SL
- **Post-Capitulation Vol-Transition MR（XBI-014 Att2，2DD floor -2.5%）**（向 USO 門檻靠攏）：Part A 16/68.8%/Sharpe 0.16 / Part B 5/80.0%/Sharpe 0.52 / min **0.16**，Part A WR 系統性下降至 68.8%（baseline 76.2%）
- **Post-Capitulation Vol-Transition MR（XBI-014 Att3，2DD floor -1.0% 最輕度 ablation）**：Part A 20/75.0%/Sharpe 0.32 / Part B 6/83.3%/Sharpe 0.64 / min **0.32**，三次最接近 baseline 但仍未超越，threshold sweep 完整失敗曲線（baseline 0.36 → -1.0% 0.32 → -2.0% 0.16 → -2.5% 0.16）確認 2DD floor 加深方向對 XBI **完全無效**

**已掃描的參數空間：**
- 進場條件：回檔 6~8% + 上限 15~20% + WR(10) ≤ -80（有/無 2日急跌 ≤ -3%）
- RSI(2) < 10 + 2日跌幅 ≥ 3%（完全不同框架，已驗證無效——XBI-002 Att3 和 XBI-009 Att3 雙重確認）
- ClosePos ≥ 30% / 35% / 40%（35% 為甜蜜點）
- 回檔回看：10日、20日（20日回看在 XBI 無效，與 COPX 相反）
- 冷卻期：10、12、15天
- 出場參數：TP +3.5~5.0% / SL -4.0~-5.0% / 持倉 15~20 天
- 突破策略：BB(20,2) Squeeze 15th/25th pct + SMA(50)，TP +4~5% / SL -5% / 20天（已驗證無效，ETF 分散化削弱突破動能）
- ROC 策略：5日 ROC ≤ -8% + WR + ClosePos（已驗證 Part B 訊號過少）
- 動量回調：ROC(20) ≥ 8%/12% + 5日回撤 2.5-7% + SMA(50)，TP +4~6% / SL -5%（已驗證無效，Part A Sharpe 最高 0.34 但 A/B 嚴重失衡）
- 配對交易：XBI/IBB 60日 z-score < -2.0/-1.5 + SMA(50)/WR(10)≤-80/無過濾，TP +3.5% / SL -5.0% / 15天（已驗證無效，等權重 vs 市值加權結構性差異使 z-score 均值回歸不成立）
- 波動率自適應：ATR(5)/ATR(20) > 1.05/1.1 + XBI-005 框架（已驗證無效，XBI 2.0% 日波動在 ATR 過濾有效邊界上，過濾器無法區分好壞訊號）
- 最佳組合：回檔 8-20% + WR ≤ -80 + ClosePos ≥ 35% + SL -5.0% / 15天（WR 76.2%/83.3%）

**尚未嘗試的方向（預期效益極低）：**
- XBI-005 已確認為全域最優，突破、ROC、動量回調、配對交易、波動率自適應、RSI(2)、BB 下軌混合進場、RSI(14) bullish hook divergence、**短期 ROC 急跌 + 日內反攻** 九大策略類型均已驗證無效
- 所有主要策略類型已窮盡（均值回歸、突破、動量回調、ROC、配對交易、波動率自適應、BB 下軌混合進場、RSI(14) bullish hook divergence、短期 ROC 急跌 + 日內反攻）

**已排除的方向：**
- **動量回調策略（TSM-006 風格）**：XBI-007 三次嘗試全部失敗，最佳 min(A,B) Sharpe 僅 0.02（vs XBI-005 的 0.36）。根本原因：XBI 作為生技板塊 ETF（130+股等權重），個股事件驅動（FDA、臨床數據）使板塊層級動量訊號不可靠，上升趨勢中的回調常因個股利空演變為板塊性回撤
- **配對交易（XBI vs IBB）**：XBI-008 三次嘗試全部失敗，最佳 Part A Sharpe 僅 -0.00（vs XBI-005 的 0.36）。根本原因：等權重 XBI 偏向小型生技（FDA 事件驅動、高波動），市值加權 IBB 偏向大型生技（穩定營收、低波動），兩者權重結構差異導致價格比值具有趨勢性而非均值回歸性。與 DIA/SPY、SIVR/GLD 等配對交易失敗模式一致
- **波動率自適應過濾（IWM-011/XLU-011 方法）**：XBI-009 Att1/Att2 驗證 ATR(5)/ATR(20) > 1.1 和 1.05 均失敗。XBI 2.0% 日波動處於 ATR 過濾有效邊界（IWM 1.5-2.0% 有效、SIVR 2-3% 無效），過濾器無法可靠區分急跌恐慌與慢速下磨
- **RSI(2) 均值回歸（SPY/DIA/IWM 框架）**：XBI-009 Att3 驗證 RSI(2)<10 + 2日跌幅≥3.0% + ClosePos≥35%，min(A,B) -0.04（vs XBI-005 的 0.36）。RSI(2) 對 XBI 的短期超賣判斷不如 pullback+WR 精確，生技 ETF 需要更深層次的回檔確認
- **BB 下軌 + 回檔上限混合進場（EWJ-003/VGK-007/CIBR-008/EWZ-006 模式）**：XBI-010 三次嘗試全部失敗，最佳 min(A,B) Sharpe 僅 0.16（vs XBI-005 的 0.36）。根本原因：(1) XBI 2.0% 日波動超出混合模式已驗證有效邊界（EWZ 1.75% 為目前上限）；(2) XBI 無法使用 ATR 過濾（XBI-009 驗證），失去混合模式中關鍵的波動率飆升確認；(3) XBI-005 的固定 pullback 8-20% 已是 XBI 2.0% 日波動下的最優結構。**XBI-010 確認混合進場模式有效邊界為日波動 ≤ 1.75%**
- **RSI(14) bullish hook divergence（SIVR-015 模式）**：XBI-011 三次嘗試全部無法改善 min(A,B)。Att1/Att3（max_min ≤ 35）過嚴產生僅 3/2 訊號全 TP 零方差樣本（年化 0.6-1.0 訊號），Att2（max_min ≤ 40）放寬後 Part A 引入 2 筆停損使 Sharpe 降至 0.27 < XBI-005 的 0.36。失敗根因：XBI 生技 ETF 的 pullback+WR+ClosePos 訊號日常發生在 RSI(14) 35-45 區間（非 SIVR ≤ 35 深度 oversold 區），hook divergence 過濾器與 XBI 訊號的 RSI 分布不相容。延伸 cross-asset lesson #20b 邊界：pattern 在 2.0% 日波動 + 生技板塊事件驅動特性下失效（SIVR 1.93% 驗證成功，XBI 2.0% 失敗），推斷適用範圍需兼顧波動率（2-3%）與平穩 RSI 分布（而非 FDA/臨床事件驅動的 bimodal）
- **短期 ROC 急跌 + 日內反攻（Capitulation + Acceleration）**：XBI-012 三次嘗試全部失敗，最佳 min(A,B) Sharpe 0.16（vs XBI-005 的 0.36）。測試假設：生技 FDA/臨床事件造成的 1-2 日急跌可用 ROC(3) 捕捉，日內反攻用 ClosePos ≥ 50% + UpDay 確認，期望與 XBI-005 的慢磨下跌結構互補。Att1（ROC -4% + ClosePos 50% + UpDay）產生 3/3 過稀疏樣本 Sharpe 0.16；Att2（ROC -3% + ClosePos 40% + UpDay）Part A 7 訊號 Sharpe 0.27（+69%）但 Part B 仍 3/3 無變化——2024-2025 XBI 牛市環境下 ROC(3) ≤ -3% 事件稀少；Att3（ROC -3% + ClosePos 35% + 無 UpDay）訊號暴增至 21/8 但 Sharpe 崩至 0.18/0.07，UpDay 過濾器證實為關鍵品質軸。失敗根因：(1) XBI 2.0% 日波動下 ROC(3) ≤ -3% 門檻僅在熊市活躍（Part A 2020-2023 生技熊市集中），牛市 Part B 樣本不足；(2) ROC(3) 急跌 + ClosePos 日內反攻的組合無法區分「真反轉」vs「急跌後技術性反彈」——Part B 2024-04-03 急跌後 7 日停損、Att3 新增 Part B 2024-12-13/2025-03-31 均屬後者。XBI-005 的 pullback(10) + WR + ClosePos 35% 反轉 K 線已是 XBI 2.0% 日波動 + FDA 事件驅動下的結構最優，短期 ROC 急跌切入點不具獨立訊號價值

**關鍵資產特性：**
- XBI (SPDR S&P Biotech ETF) 日波動約 2.0%，GLD 比率 1.81x
- 生技板塊 ETF，受 FDA 審批、臨床數據、併購消息驅動
- 均值回歸效果穩健，Part B Sharpe > Part A（無過擬合跡象）
- ClosePos ≥ 35% 在 XBI 上有效（與 IWM 類似），XBI 日波動 2.0% 在 ClosePos 有效邊界內
- 2日急跌過濾對 XBI 無效（移除好訊號而非壞訊號），RSI(2) 框架在 XBI 上 Part B WR 僅 44.4-57.1%
- SL -5.0% 是底線不可收窄（生技板塊熊市超賣反彈需要寬 SL 呼吸空間）
- 持倉 15天 vs 20天 無差異（平均持倉僅 3-5 天）
- 20日回看對 XBI 無效（與 COPX 相反）：XBI 淺回檔（8-10%）包含高品質訊號，20日回看過濾掉這些
- ClosePos 35% 是 XBI 甜蜜點：40% 太緊移除 Part B 好訊號（Sharpe 0.16），30% 太鬆引入 Part A 壞訊號（Sharpe 0.30 vs 0.36）
- **突破策略在 XBI 上無效**：ETF 分散化削弱突破動能（類似 COPX-005），WR 僅 50-56%，假突破率過高
- **ROC-based 進場不優於 pullback-from-high**：5日 ROC 在 Part B 僅產生 2 個訊號，市場狀態依賴性過高
- **ATR 波動率過濾在 XBI 2.0% 日波動邊界失效**：與 SIVR 2-3% 失敗一致，確認 ATR 有效邊界 ≤ 1.5-2.0%
- **RSI(14) bullish hook divergence 在 XBI 失效**：SIVR-015 模式（lookback 5 / delta 3 / max_min 35）在 XBI 產生 3/2 零方差樣本（Att1/Att3），放寬至 max_min 40（Att2）引入 Part A 壞訊號。XBI pullback+WR+ClosePos 的訊號 RSI(14) 通常僅在 35-45 區間，未達 hook divergence 所需深度 oversold（≤ 35）。延伸 lesson #20b 邊界：hook divergence pattern 有效性需要資產 RSI(14) 訊號日分布集中在 ≤ 35（SIVR），XBI 生技板塊的事件驅動特性使 RSI 分布偏高
- **Capitulation + Acceleration（XBI-012）在 XBI 失效**：ROC(3) 短期急跌 + ClosePos 日內反攻 + UpDay 過濾的三次嘗試（ClosePos 50/40/35%）min(A,B) Sharpe 僅 0.16/0.16/0.07。關鍵觀察：(1) Part A 隨放寬條件從 Sharpe 0.16→0.27→0.18 單峰（Att2 最佳），(2) Part B 從 0.16→0.16→0.07 單調下降——UpDay 過濾器為 Part B 品質的關鍵前提，(3) 2024-2025 XBI 牛市 ROC(3) ≤ -3% 事件稀少（3 訊號）無法擴張樣本。整體結構問題：XBI 2.0% 日波動下 ROC(3) 急跌 + 日內反攻無法區分真反轉與急跌後技術性反彈，XBI-005 的 pullback(10)+WR+ClosePos 反轉 K 線框架已是結構最優
- **Post-Capitulation Vol-Transition MR（XBI-014）在 XBI 失效**：跨資產移植 VGK-008 / INDA-010 / EEM-014 / USO-013 / IBIT-009 的「2DD floor 加深」模板，三次 threshold sweep（-1.0% / -2.0% / -2.5%）min(A,B) Sharpe 0.32 / 0.16 / 0.16 全部低於 baseline 0.36，**單調退化曲線**確認方向錯誤。失敗根因：(1) **XBI 2DD 分布 NO unidirectional selectivity**——Part A SLs 範圍 -1.03%~-5.53%、TPs 範圍 -0.23%~-6.86%，重疊整個範圍；(2) FDA event-driven 結構使 winners 同時涵蓋 shallow 2DD（短期反彈）與 deep 2DD（acute capitulation）兩極，與 INDA/EEM/VGK/USO/IBIT 的「shallow 2DD = drift」單峰失敗結構**結構不同**；(3) Cooldown chain shift（lesson #19）使 Att1 -2.0% 過濾後原 2024-03-14 TP 釋放 2024-03-15 SL 成為 Part B 新 SL。**Repo 第 6 次「2DD floor 加深方向」失敗驗證，首次 US 板塊 ETF 測試**：整合規則更新——Post-Capitulation Vol-Transition MR 有效條件需同時滿足 (a) vol ∈ [0.97%, 3.17%] AND (b) winners 2DD 分布**單峰**（broad ETF / 商品 / 加密 ETF），事件驅動板塊 ETF（XBI FDA / CIBR 政策—但 cap 方向有效）winners 2DD 雙峰分布使任何單向 filter 失效
<!-- AI_CONTEXT_END -->

# XBI 實驗總覽 (XBI Experiments Overview)

## 標的特性 (Asset Characteristics)

- **XBI (SPDR S&P Biotech ETF)**：追蹤 S&P Biotechnology Select Industry Index，等權重持有美國生技公司
- 日均波動約 2.0%，GLD 波動比率 1.81x，屬中等波動度（MEDIUM）
- 生技板塊受 FDA 審批、臨床試驗結果、併購活動驅動，有明顯的恐慌拋售後反彈特徵
- 2021-2022 年經歷長期熊市（從 ~170 跌至 ~65），均值回歸策略在此期間訊號密集

## 實驗列表 (Experiment List)

| ID      | 資料夾                   | 策略摘要                              | 狀態  |
|---------|-------------------------|--------------------------------------|-------|
| XBI-001 | `xbi_001_pullback_wr`    | 回檔範圍 8-20% + Williams %R 均值回歸 | 已完成 |
| XBI-004 | `xbi_004_capped_cooldown` | 回檔 8-15% + WR + 冷卻15天（未勝出） | 已完成 |
| XBI-005 | `xbi_005_closepos_reversal` | 回檔 8-20% + WR + ClosePos ≥ 35%（**全域最佳**） | 已完成 |
| XBI-006 | `xbi_006_bb_squeeze_breakout` | BB Squeeze Breakout + 3次嘗試（未勝出） | 已完成 |
| XBI-007 | `xbi_007_momentum_pullback` | 動量回調 ROC+回撤+SMA50 + 3次嘗試（未勝出） | 已完成 |
| XBI-008 | `xbi_008_pairs_ibb` | XBI/IBB 配對交易 z-score + 3次嘗試（未勝出） | 已完成 |
| XBI-009 | `xbi_009_vol_adaptive` | ATR/RSI(2) 波動率自適應 + 3次嘗試（未勝出） | 已完成 |
| XBI-010 | `xbi_010_bb_lower_pullback_cap` | BB 下軌 + 回檔上限混合進場 + 3次嘗試（未勝出） | 已完成（未改善） |
| XBI-011 | `xbi_011_rsi_divergence_mr` | RSI(14) Bullish Hook Divergence + XBI-005 + 3次嘗試（未勝出） | 已完成（未改善） |
| XBI-012 | `xbi_012_capitulation_accel` | Capitulation + Acceleration Reversal（ROC(3) + ClosePos + UpDay + WR） + 3次嘗試（未勝出） | 已完成（未改善） |
| XBI-013 | `xbi_013_gap_reversal_mr` | Gap-Down Capitulation + Intraday Reversal MR（IBIT-006 移植） + 3次嘗試（未勝出） | 已完成（失敗，repo 首次 US 板塊 ETF Gap-Down 試驗） |
| XBI-014 | `xbi_014_vol_transition_mr` | Post-Capitulation Vol-Transition MR（VGK-008/INDA-010/EEM-014 移植，2DD floor sweep） + 3次嘗試（未勝出） | 已完成（失敗，repo 第 6 次 2DD floor 跨資產試驗） |

---

## XBI-001: 回檔 + Williams %R 均值回歸 (Pullback + Williams %R Mean Reversion)

### 目標 (Goal)

建立 XBI 首個均值回歸實驗。參考 SIVR-003/SIVR-005 回檔 + Williams %R 架構，
按 XBI 波動度（~2.0%，GLD 比率 1.81x）縮放參數。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 10 日高點回檔 | ≥ 8% | 過濾淺回檔（GLD 3% × ~2.7x）|
| 2 | 回檔上限 | ≤ 20% | 過濾極端崩盤（如 2020 COVID）|
| 3 | Williams %R(10) | ≤ -80 | 超賣確認 |
| 4 | 冷卻期 | 10 天 | 避免重複進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 (TP) | +3.5% | 均值回歸幅度 |
| 停損 (SL) | -5.0% | 非對稱寬停損（生技板塊需呼吸空間）|
| 最長持倉 | 15 天 | 高波動 → 更快回歸 |
| 追蹤停損 | 無 | 日波動 2%，邊界區域不使用 |

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

- **回檔 8-20%**：8% 下限過濾淺回檔（初始 6% 產生過多低品質訊號），20% 上限過濾 COVID 等極端崩盤訊號
- **WR(10) ≤ -80**：標準超賣門檻，與 SIVR-003 一致
- **SL -5.0%**：非對稱設計（TP/SL = 0.7:1），需 WR > 59% 才能獲利。初始 -4.5% 也可行，但 -5.0% 給予更多呼吸空間
- **無追蹤停損**：日波動 2.0% 在邊界，根據跨資產教訓 #2 預設不用

### 迭代嘗試紀錄 (Iteration Log)

| # | 變更 | Part A Sharpe | Part B Sharpe | A WR / B WR | 結論 |
|---|------|-------------|-------------|------------|------|
| 1 | 回檔 ≥ 6% 無上限, SL -4.5% | -0.06 | 0.08 | 53.1%/64.3% | 49 訊號過多，Part A 負 |
| 2 | 回檔 8-20%, SL -5.0% (最終版) | 0.11 | 0.23 | 63.9%/70.0% | 雙正、Part B 優於 A |

### 回測結果 (Backtest Results)

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|-------------------|-------------------|----------------|
| 訊號數 | 36 | 10 | 1 |
| 訊號/年 | 7.2 | 5.0 | 4.3 |
| 勝率 | 63.9% | 70.0% | 100.0% |
| 平均報酬 | +0.44% | +0.92% | +3.50% |
| 累計報酬 | +13.68% | +8.74% | +3.50% |
| 盈虧比 | 1.25 | 1.60 | ∞ |
| Sharpe | 0.11 | 0.23 | — |
| Sortino | 0.15 | 0.33 | ∞ |
| Calmar | 0.05 | 0.10 | 3.37 |
| MDD | -9.38% | -9.50% | -1.04% |
| 最大連續虧損 | 2 | 1 | 0 |

**A/B 分析**：
- 訊號率比 7.2:5.0 = 1.44:1（可接受）
- WR 從 63.9% 提升至 70.0%（Part B 更好，無過擬合）
- Sharpe 從 0.11 提升至 0.23（Part B 顯著更好）
- 最大連續虧損 Part A 僅 2，Part B 僅 1（穩定）
- Part A 期間包含 2021-2022 生技長期熊市，多筆停損拉低績效

**結論**：XBI 的回檔 + Williams %R 均值回歸策略有效，Part B 表現優於 Part A 顯示策略穩健。回檔範圍過濾（8-20%）成功將初始的負績效轉為正績效，證實跨資產教訓 #14 對 XBI 同樣適用。

---

## XBI-002 改進嘗試紀錄（3 次嘗試，均失敗，無新實驗建立）

目標：嘗試改進 XBI-001 的風險調整後報酬（Part A Sharpe 0.11）。

| # | 策略變更 | Part A Sharpe | Part B Sharpe | A WR / B WR | 訊號數 A/B | 結論 |
|---|---------|-------------|-------------|------------|-----------|------|
| Att1 | 回檔 8-20% + WR ≤ -80 + **2日急跌 ≤ -3%** + TP +4.0% / SL -5.0% / 20天 | 0.03 | 0.08 | 58.6%/60.0% | 29/5 | 2日急跌過濾反而移除好訊號，WR 下降，TP +4.0% 增加停損率 |
| Att2 | 回檔 **8-15%** + WR ≤ -80 + **2日急跌 ≤ -3%** + TP +3.5% / SL -5.0% / 15天 | -0.06 | 0.01 | 55.6%/60.0% | 27/5 | 收窄上限 + 2日急跌雙重過濾過度，Part A 負累計 -9.02% |
| Att3 | **RSI(2) < 10 + 2日跌幅 ≥ 3%**（完全不同框架）+ TP +3.5% / SL -5.0% / 15天 | 0.00 | -0.30 | 59.5%/44.4% | 42/9 | RSI(2) 產生過多訊號，Part B WR 僅 44.4%，累計 -11.67% |

**結論**：XBI-001 的回檔 + Williams %R 架構已是最優。2日急跌過濾（參考 USO-013）對 XBI 無效——XBI 的好買點不一定伴隨急跌，慢跌中也有高品質訊號。RSI(2) 框架在 XBI 上產生過多低品質訊號（尤其 Part B），遠不如 WR + 回檔範圍組合。XBI-001 確認為全域最優。

---

## XBI-003 改進嘗試紀錄（3 次嘗試，均失敗，無新實驗建立）

目標：嘗試透過出場參數優化（SL 收緊 + 延長持倉）改進 XBI-001 的風險調整後報酬。

| # | 策略變更 | Part A Sharpe | Part B Sharpe | A WR / B WR | 訊號數 A/B | 結論 |
|---|---------|-------------|-------------|------------|-----------|------|
| Att1 | SL **-4.0%** / **20天**（收緊停損 + 延長持倉）| 0.03 | 0.35 | 55.6%/70.0% | 36/10 | SL -4.0% 太緊，Part A WR 從 63.9% 降至 55.6%，2021-2022 生技熊市交易需要寬 SL 呼吸 |
| Att2 | SL **-4.5%** / **20天**（中間值收緊 + 延長持倉）| 0.09 | 0.29 | 61.1%/70.0% | 36/10 | Part A 仍劣化（0.09 vs 0.11），-4.5% 仍太緊。Part B 改善但 A/B 不平衡 |
| Att3 | SL -5.0% / **20天**（僅延長持倉，不改 SL）| 0.10 | 0.23 | 63.9%/70.0% | 36/10 | 與 XBI-001 幾乎相同（Part A 0.10 vs 0.11），平均持倉僅 3-5 天，延長至 20 天無效 |

**結論**：SL 收緊在 XBI 上對 Part A 有害——2021-2022 生技板塊長期熊市期間，多筆交易下探 -4% ~ -5% 後才反彈達標，收緊 SL 將這些交易轉為停損。SL -5.0% 是 XBI 的底線（類似 FCX -12%、IBIT -7% 的模式）。延長持倉期無效果，因多數交易在 3-5 天內就已觸及 TP 或 SL。XBI-001 再次確認為全域最優（累計 6 次嘗試均失敗）。

**新增跨資產教訓**：XBI SL -5.0% 是底線不可收窄——生技板塊熊市期間超賣後反彈路徑波動大，需要寬 SL 呼吸空間。

---

## XBI-004: 回檔範圍收窄 + 長冷卻 嘗試紀錄（3 次嘗試，均未勝出 XBI-001）

目標：嘗試透過回檔範圍收窄 + 延長冷卻期 + 回看窗口調整改進 XBI-001 的風險調整後報酬。

### 設計理念

- **20日回看**（Att1）：參考 COPX-003 的 20日回看突破，測試更長回看是否捕捉更有意義的回檔
- **回檔上限 15%**（Att2/Att3）：過濾極端熊市訊號（>15% 回檔恢復率低）
- **冷卻 15天**（Att2/Att3）：避免 2021 Feb-Mar、2022 Apr、2023 Sep-Oct 等熊市連續進場
- **TP +4.0%**（Att1）：改善風報比從 0.70 至 0.80

### 嘗試紀錄

| # | 策略變更 | Part A Sharpe | Part B Sharpe | A WR / B WR | 訊號數 A/B | 結論 |
|---|---------|-------------|-------------|------------|-----------|------|
| Att1 | **20日回看** + 回檔 10-20% + **TP +4.0%** + 冷卻12天 / SL -5.0% / 20天 | 0.02 | 0.23 | 58.3%/66.7% | 24/6 | 20日回看移除好訊號多於壞訊號（與 COPX 相反），TP +4.0% 使部分達標交易變到期 |
| Att2 | 10日回看 + **回檔 8-15%** + **冷卻15天** + TP +3.5% / SL -5.0% / **20天** | 0.04 | 0.44 | 61.3%/77.8% | 31/9 | Part B 大幅改善但 Part A 劣化，A/B 極度失衡（0.04 vs 0.44）|
| Att3 | 同 Att2 改 **15天持倉** | 0.05 | 0.44 | 61.3%/77.8% | 31/9 | 持倉改回 15天微幅改善 Part A（0.04→0.05），但仍遠劣於 XBI-001（0.11）|

### 回測結果（Att3 最終版）

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|-------------------|-------------------|----------------|
| 訊號數 | 31 | 9 | 1 |
| 訊號/年 | 6.2 | 4.5 | 4.2 |
| 勝率 | 61.3% | 77.8% | 100.0% |
| 平均報酬 | +0.17% | +1.59% | +3.50% |
| 累計報酬 | +4.37% | +14.59% | +3.50% |
| 盈虧比 | 1.12 | 2.40 | ∞ |
| Sharpe | 0.05 | 0.44 | — |
| Sortino | 0.07 | 0.66 | ∞ |
| MDD | -9.38% | -9.50% | -1.04% |

### 結論

回檔上限 15% + 冷卻 15天組合對 Part B 有顯著改善（Sharpe 0.23→0.44），但 Part A 同時劣化（0.11→0.05）。根本原因：收窄上限移除的 Part A 訊號中好壞各半，無法選擇性過濾壞訊號。20日回看在 XBI 上無效（與 COPX 相反），因 XBI 的淺回檔（8-10%）包含高品質訊號。XBI-001 再次確認為全域最優（累計 9 次嘗試均失敗）。

---

## XBI-005: 回檔 + Williams %R + 反轉K線均值回歸 (Pullback + WR + Reversal Candlestick)

### 目標 (Goal)

在 XBI-001 基礎上加入 ClosePos 反轉K線過濾，提升訊號品質。
IWM-005 驗證 ClosePos 在中低波動 ETF（~1.5-2%）是必要品質過濾器。
XBI 日波動 ~2.0% 與 IWM 接近，測試此過濾器是否能改善 Part A Sharpe。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 10 日高點回檔 | ≥ 8% | 過濾淺回檔 |
| 2 | 回檔上限 | ≤ 20% | 過濾極端崩盤 |
| 3 | Williams %R(10) | ≤ -80 | 超賣確認 |
| 4 | ClosePos | ≥ 35% | 日內反轉確認（**新增**）|
| 5 | 冷卻期 | 10 天 | 避免重複進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 (TP) | +3.5% | 同 XBI-001 |
| 停損 (SL) | -5.0% | 同 XBI-001 |
| 最長持倉 | 15 天 | 同 XBI-001 |
| 追蹤停損 | 無 | 同 XBI-001 |

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

| # | 變更 | Part A Sharpe | Part B Sharpe | A WR / B WR | 訊號 A/B | 結論 |
|---|------|-------------|-------------|------------|---------|------|
| Att1 | ClosePos ≥ 40% | 0.28 | 0.16 | 73.7%/66.7% | 19/6 | Part A 大幅改善，但 Part B 劣化（門檻太高移除好訊號）|
| Att2 | ClosePos ≥ 35%（**最終版**）| **0.36** | **0.64** | **76.2%/83.3%** | 21/6 | Part A +227%，Part B +178%，A/B 平衡優秀 |
| Att3 | ClosePos ≥ 30% | 0.30 | 0.64 | 73.9%/83.3% | 23/6 | 多 2 個 Part A 訊號含 1 壞訊號，Part A 退步 |

### 回測結果 (Backtest Results)

| 指標 | Part A (2019-2023) | Part B (2024-2025) | Part C (2026-) |
|------|-------------------|-------------------|----------------|
| 訊號數 | 21 | 6 | 0 |
| 訊號/年 | 4.2 | 3.0 | 0.0 |
| 勝率 | 76.2% | 83.3% | — |
| 平均報酬 | +1.30% | +2.07% | — |
| 累計報酬 | +29.30% | +12.71% | — |
| 盈虧比 | 2.07 | 3.43 | — |
| Sharpe | 0.36 | 0.64 | — |
| Sortino | 0.52 | 0.99 | — |
| Calmar | 0.14 | 0.22 | — |
| MDD | -9.08% | -9.50% | — |
| 最大連續虧損 | 1 | 1 | — |

**A/B 分析**：
- 訊號率比 4.2:3.0 = 1.4:1（優秀）
- WR 從 76.2% 提升至 83.3%（Part B 更好，無過擬合）
- Sharpe 從 0.36 到 0.64（Part B 顯著更好，無過擬合）
- 最大連續虧損均為 1（穩定）

**vs XBI-001 改善幅度**：
- Part A Sharpe: 0.11 → 0.36（**+227%**）
- Part B Sharpe: 0.23 → 0.64（**+178%**）
- Part A WR: 63.9% → 76.2%（+12.3pp）
- Part B WR: 70.0% → 83.3%（+13.3pp）
- Part A 累計: +13.68% → +29.30%（+114%）
- Part B 累計: +8.74% → +12.71%（+45%）
- min(A,B) Sharpe: 0.11 → 0.36（**+227%**）

**結論**：ClosePos ≥ 35% 在 XBI 上極為有效。35% 是甜蜜點：40% 太高移除 Part B 好訊號（Part B Sharpe 0.16），30% 太低引入 Part A 壞訊號（Part A Sharpe 0.30）。XBI 日波動 2.0% 在 ClosePos 有效邊界內（類似 IWM ~1.5-2%），與 FCX/SIVR（2-4%）不同。此結果修正了「XBI ClosePos 可能無效」的先驗預期。

---

## 演進路線圖 (Roadmap)

```
XBI-005 (回檔 8-20% + WR(10) ≤ -80 + ClosePos ≥ 35%) ← 新最佳
  └── 在 XBI-001 基礎上加入 ClosePos ≥ 35%，Part A/B Sharpe 分別提升 227%/178%

XBI-001 (回檔 8-20% + WR(10) ≤ -80) ← 前任最佳
  ├── [失敗] 2日急跌過濾（XBI-002 Att1/Att2：移除好訊號）
  ├── [失敗] RSI(2) 框架替代（XBI-002 Att3：Part B WR 44.4%）
  ├── [失敗] SL -4.0% / 20天（XBI-003 Att1：Part A Sharpe 0.03，SL 太緊）
  ├── [失敗] SL -4.5% / 20天（XBI-003 Att2：Part A Sharpe 0.09，仍太緊）
  ├── [失敗] SL -5.0% / 20天（XBI-003 Att3：無效果，平均持倉 3-5 天）
  ├── [失敗] 20日回看 + TP 4.0%（XBI-004 Att1：20日回看移除好訊號）
  ├── [失敗] 回檔 8-15% + 冷卻15天 + 20天持倉（XBI-004 Att2：A/B 極度失衡）
  ├── [失敗] 回檔 8-15% + 冷卻15天 + 15天持倉（XBI-004 Att3：Part A 仍劣於 XBI-001）
  └── [**成功**] ClosePos ≥ 35%（XBI-005：Part A 0.36 / Part B 0.64）
```

---

## XBI-001 滾動窗口績效分析

> **分析日期：** 2026-03-30
> **窗口：** 2 年，步進 6 個月（共 12 個窗口）

### 滾動窗口績效表

| 窗口 | 訊號 | 勝率 | 平均報酬 | 累計報酬 | MDD | ΔWR |
|------|------|------|----------|----------|-----|-----|
| 2019-01~2020-12 | 7 | 71.4% | +1.28% | +8.81% | -5.72% | — |
| 2019-07~2021-06 | 11 | 63.6% | +0.37% | +3.19% | -9.38% | -7.8pp |
| 2020-01~2021-12 | 15 | 73.3% | +1.21% | +18.42% | -9.38% | +9.7pp |
| 2020-07~2022-06 | 20 | 60.0% | +0.06% | -0.59% | -9.38% | -13.3pp |
| 2021-01~2022-12 | 24 | 66.7% | +0.63% | +14.07% | -9.38% | +6.7pp |
| 2021-07~2023-06 | 21 | 66.7% | +0.87% | +17.98% | -7.47% | +0.0pp |
| 2022-01~2023-12 | 18 | 61.1% | +0.16% | +1.22% | -7.47% | -5.6pp |
| 2022-07~2024-06 | 13 | 69.2% | +0.85% | +10.55% | -5.85% | +8.1pp |
| 2023-01~2024-12 | 11 | 45.5% | -0.74% | -8.72% | -6.11% | -23.8pp |
| 2023-07~2025-06 | 12 | 58.3% | -0.08% | -2.06% | -9.50% | +12.9pp |
| 2024-01~2025-12 | 10 | 70.0% | +0.92% | +8.74% | -9.50% | +11.7pp |
| 2024-07~2026-03 | 8 | 75.0% | +1.35% | +10.71% | -9.50% | +5.0pp |

### 預測精準度表

| 窗口 | WR | 平均贏利 | 平均虧損 | 盈虧比 | 差點成功 |
|------|------|----------|----------|--------|----------|
| 2019-01~2020-12 | 71.4% | +3.50% | -4.28% | 2.04 | 0/1 |
| 2019-07~2021-06 | 63.6% | +3.50% | -5.10% | 1.20 | — |
| 2020-01~2021-12 | 73.3% | +3.50% | -5.10% | 1.89 | — |
| 2020-07~2022-06 | 60.0% | +3.50% | -5.10% | 1.03 | — |
| 2021-01~2022-12 | 66.7% | +3.50% | -5.10% | 1.37 | — |
| 2021-07~2023-06 | 66.7% | +3.50% | -4.40% | 1.59 | 0/1 |
| 2022-01~2023-12 | 61.1% | +3.50% | -5.10% | 1.08 | — |
| 2022-07~2024-06 | 69.2% | +3.50% | -5.10% | 1.54 | — |
| 2023-01~2024-12 | 45.5% | +3.50% | -4.28% | 0.68 | 0/1 |
| 2023-07~2025-06 | 58.3% | +3.50% | -5.10% | 0.96 | — |
| 2024-01~2025-12 | 70.0% | +3.50% | -5.10% | 1.60 | — |
| 2024-07~2026-03 | 75.0% | +3.50% | -5.10% | 2.06 | — |

### 漸變性評估

- **勝率範圍**：45.5% ~ 75.0%（ΔWR 標準差 11.1pp，最大跳動 23.8pp）
- **盈虧比範圍**：0.68 ~ 2.06（ΔPF 標準差 0.60）
- **累計報酬範圍**：-8.72% ~ +18.42%（ΔCum 標準差 12.65%）
- **平均贏利範圍**：+3.50% ~ +3.50%（Δ標準差 0.00%，完全穩定）
- **平均虧損範圍**：-4.28% ~ -5.10%（虧損幅度穩定）

**判定：**
- ✗ 預測精準度突變（勝率最大跳動 23.8pp > 20pp 閾值，發生在窗口 8→9）
- ✓ 下游績效漸變（累計報酬最大跳動 19.27% ≤ 3σ = 37.95%）

**診斷：** 精準度波動但績效穩定 → 勝/虧報酬互補抵消了精準度變化

### 分析解讀

1. **2023 年谷底**：窗口 9 勝率跌至 45.5%，累計 -8.72%，為唯一大幅虧損窗口，生技板塊 2023 年持續低迷
2. **訊號量充足**：多數窗口 7-24 筆訊號，統計可信度優於大盤 ETF
3. **近期恢復**：窗口 11-12 勝率回升至 70-75%，累計 +8.7%~+10.7%，生技板塊回暖
4. **平均贏利完全固定**：TP +3.50% 在所有窗口一致觸發
5. **10/12 正報酬窗口**：整體穩健，僅窗口 4（-0.59%）和窗口 9（-8.72%）為負
6. **勝率波動主要由 2023 谷底造成**：若排除窗口 9，ΔWR 最大跳動僅 13.3pp（通過閾值）

---

## XBI-006: Bollinger Band Squeeze Breakout（已完成，未勝出）

### 目標 (Goal)

測試突破策略是否能超越 XBI-005 均值回歸。突破策略在類似波動度資產上已成功（NVDA-003 Sharpe 0.40/0.47、TSLA-005 0.35/0.37、IWM-006 0.31/0.37）。XBI 日波動 ~2.0% 與 IWM 接近，且生技板塊有動量驅動特性。

### 基準 (Baseline)

XBI-005：Part A Sharpe 0.36 / Part B Sharpe 0.64（回檔 8-20% + WR + ClosePos）

### 嘗試紀錄 (Attempt Log)

#### Attempt 1: BB(20,2) Squeeze 25th pct + SMA(50)，TP +5.0% / SL -5.0% / 20d

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 12 | 9 |
| 勝率 | 50.0% | 55.6% |
| Sharpe | 0.05 | 0.17 |
| 累計 | +1.78% | +5.89% |
| MDD | -6.04% | -6.05% |

**分析**：WR 僅 50-55%，5/12 Part A 交易停損。假突破率過高——XBI 作為分散化 ETF，個別成分股突破被其他成分股拖累，整體 ETF 突破動能不足。

#### Attempt 2: 收緊擠壓至 15th 百分位 + TP 降至 +4.0%

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 10 | 9 |
| 勝率 | 60.0% | 55.6% |
| Sharpe | 0.18 | 0.10 |
| 累計 | +6.69% | +3.12% |
| MDD | -5.40% | -6.05% |

**分析**：Part A 改善（WR 50→60%，Sharpe 0.05→0.18），但 Part B 劣化（0.17→0.10）。更嚴格的擠壓篩選在 IS 有效但 OOS 無區分力。降低 TP 讓 2025-06-03 交易從到期轉為達標，但整體改善不足。

#### Attempt 3: 完全不同策略——5日 ROC ≤ -8% + WR + ClosePos

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 7 | 2 |
| 勝率 | 71.4% | 50.0% |
| Sharpe | 0.27 | -0.19 |
| 累計 | +6.96% | -1.78% |
| MDD | -7.09% | -9.50% |

**分析**：ROC-based 進場改善了 Part A 品質（WR 71.4%，Sharpe 0.27），但 Part B 僅 2 個訊號無統計意義。A/B 訊號比 3.5:1 表示嚴重市場狀態依賴。ROC 在 2022 熊市產生高品質訊號但在 2024-2025 幾乎無觸發。

### 結論 (Conclusion)

三次嘗試均大幅落後 XBI-005：

| 嘗試 | 策略 | Part A Sharpe | Part B Sharpe | vs XBI-005 |
|------|------|---------------|---------------|------------|
| Att1 | BB Squeeze 25th pct | 0.05 | 0.17 | -86% / -73% |
| Att2 | BB Squeeze 15th pct | 0.18 | 0.10 | -50% / -84% |
| Att3 | 5日 ROC | 0.27 | -0.19 | -25% / -130% |
| **XBI-005** | **Pullback+WR+ClosePos** | **0.36** | **0.64** | **baseline** |

**關鍵發現**：
1. **突破策略在 XBI 上無效**——ETF 分散化削弱突破動能（同 COPX-005 結論）。130+ 成分股的等權重 ETF，個股突破被群體稀釋
2. **ROC 進場不優於 pullback-from-high**——5日 ROC 對市場狀態依賴性過高，Part B 訊號不足
3. **XBI-005 已確認為全域最優**（6 次實驗、20+ 次嘗試，涵蓋均值回歸、突破、ROC 三種策略類型）

---

## XBI-007: 動量回調 (Momentum Pullback)

### 目標 (Goal)

測試 TSM-006 風格的動量回調策略是否適用於 XBI。在上升趨勢中買入短期回調，捕捉趨勢延續的動量。

### 策略設計 (Strategy Design)

- **進場條件**：20日 ROC ≥ 8% + 5日高點回撤 3.5-6% + Close > SMA(50) + 冷卻 10天
- **出場條件**：TP +4% / SL -5% / 20天
- **成交模型**：隔日開盤市價進場，滑價 0.10%
- **參考**：TSM-006 架構，按 XBI 日波動 ~2.0%（vs TSM ~2.5%）縮放

### 三次嘗試結果 (Attempt Results)

| 嘗試 | 參數 | Part A Sharpe | Part B Sharpe | Part A 訊號 | Part B 訊號 | min(A,B) |
|------|------|---------------|---------------|-------------|-------------|----------|
| Att1 | ROC 8%, PB 2.5-5%, TP+5% | -0.01 | -0.23 | 18 | 7 | -0.23 |
| Att2 | ROC 12%, PB 3-7%, TP+6% | 0.34 | -1019* | 8 | 2 | -1019* |
| Att3 | ROC 8%, PB 3.5-6%, TP+4% | 0.02 | 0.44 | 14 | 4 | 0.02 |
| **XBI-005** | **基準** | **0.36** | **0.64** | **21** | **6** | **0.36** |

*Part B 僅 2 訊號且標準差為 0，Sharpe 計算異常

### 失敗分析 (Failure Analysis)

1. **Part A 表現極差**：最佳 Attempt 3 Part A Sharpe 僅 0.02，2020 生技泡沫期產生大量假動量訊號（4 筆停損），2022 熊市反彈動量不持續（2 筆停損）
2. **A/B 嚴重失衡**：Att1 比例 2.6:1，Att2 4:1，Att3 3.5:1，均遠超 2:1 警戒線
3. **根本原因**：XBI 作為板塊 ETF（130+ 等權重生技股），個股事件驅動（FDA 審批、臨床數據）使板塊層級動量訊號不可靠。上升趨勢中的回調常因個股利空演變為板塊性回撤，與 TSM（單一公司、半導體景氣循環驅動）有本質差異
4. **動量回調策略有效範圍確認**：僅適用於個股（TSM 日波動 2-3%）或動量驅動型標的，不適用於多成分等權重板塊 ETF

---

## XBI-008: XBI/IBB 配對交易 (XBI/IBB Pairs Trading)

### 目標 (Goal)

利用 XBI（等權重生技 ETF）與 IBB（市值加權生技 ETF）的價格比值 z-score 均值回歸。
兩者追蹤同一板塊但權重方式不同，理論上價格比值應長期穩定。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | XBI/IBB 對數比值 60日 z-score | < -2.0 | XBI 相對低估 |
| 2 | Williams %R(10) | ≤ -80 | 超賣確認（Att3） |
| 3 | 冷卻期 | 10 天 | 避免重複進場 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 (TP) | +3.5% | 同 XBI-005 |
| 停損 (SL) | -5.0% | 同 XBI-005 |
| 持倉天數 | 15 天 | 同 XBI-005 |

### 成交模型 (Execution Model)

- 進場：隔日開盤市價
- 止盈：限價賣單 Day
- 停損：停損市價 GTC
- 到期：隔日開盤市價
- 滑價：0.10%
- 悲觀認定：是

### 三次嘗試結果 (Three Attempt Results)

| 嘗試 | 進場條件 | Part A Sharpe | Part A 訊號 | Part B Sharpe | Part B 訊號 | min(A,B) |
|------|---------|--------------|------------|--------------|------------|----------|
| Att1 | z<-2.0 + SMA(50) | -0.19 | 4 | 0.00 | 1 | -0.19 |
| Att2 | z<-1.5, 無過濾 | -0.23 | 41 | 0.07 | 8 | -0.23 |
| Att3 | z<-2.0 + WR(10)≤-80 | -0.00 | 19 | -0.19 | 4 | -0.19 |

### 失敗分析 (Failure Analysis)

1. **XBI/IBB 價格比值不穩定**：等權重（XBI）偏向小型生技股（FDA 事件驅動、高波動），市值加權（IBB）偏向大型生技股（穩定營收、低波動），兩者權重結構差異導致價格比值具有趨勢性而非均值回歸性
2. **z-score 門檻兩難**：z < -2.0 訊號太少（Part A 僅 4 個），z < -1.5 噪音太多（Part A 41 個，WR 48.8%）
3. **A/B 嚴重失衡**：Att2 的 A/B 比達 5.1:1，表明策略對 2019-2022 生技板塊結構性變化有偏好
4. **與跨資產配對交易失敗模式一致**：DIA/SPY（科技權重漂移）、SIVR/GLD（金銀比結構偏移）、COPX/FCX（結構性漂移）等配對交易均因結構性漂移失敗。XBI/IBB 的失敗進一步確認：即使是同板塊不同權重的 ETF，z-score 均值回歸也不可靠

---

## XBI-009：波動率自適應 / RSI(2) 均值回歸（Volatility-Adaptive / RSI(2) Mean Reversion）

**狀態：失敗（3 次嘗試均劣於 XBI-005）**

**假設**：ATR(5)/ATR(20) 波動率飆升過濾可移除 XBI-005 Part A 的「慢速下磨」假訊號，改善 Part A Sharpe。此方法在 IWM-011（+67.7%）和 XLU-011（+272%）已驗證有效，XBI 日波動 ~2.0% 與 IWM（1.5-2%）接近。

**成交模型：**
- 進場：隔日開盤市價
- 止盈：限價賣單 Day
- 停損：停損市價 GTC
- 到期：隔日開盤市價
- 滑價：0.10%
- 悲觀認定：是

### 三次嘗試結果 (Three Attempt Results)

| 嘗試 | 進場條件 | TP/SL/Days | Part A Sharpe | Part A 訊號 | Part B Sharpe | Part B 訊號 | min(A,B) |
|------|---------|-----------|--------------|------------|--------------|------------|----------|
| Att1 | XBI-005 + ATR > 1.1 | +3.5%/-5.0%/15d | 0.27 | 7 | 0.16 | 3 | 0.16 |
| Att2 | XBI-005 + ATR > 1.05 | +3.5%/-5.0%/15d | -0.08 | 9 | 0.36 | 4 | -0.08 |
| Att3 | RSI(2)<10 + 2d跌幅≥3.0% + ClosePos≥35% | +3.5%/-5.0%/15d | 0.04 | 16 | -0.04 | 7 | -0.04 |

**vs XBI-005 基準**：Part A 0.36 / Part B 0.64 / min(A,B) 0.36

### 失敗分析 (Failure Analysis)

1. **ATR 過濾在 XBI 2.0% 日波動邊界失效**：ATR > 1.1 將 Part A 訊號從 ~21 縮減至 7，移除的 14 個訊號中包含大量好訊號，Sharpe 反而下降。ATR > 1.05 新增的 2 個訊號（2022-04-19、2023-09-21）均停損，Part A Sharpe 從 0.27 崩至 -0.08。確認 ATR 過濾有效邊界為日波動 ≤ 1.5-2.0%（IWM 有效，XBI/SIVR 無效）
2. **RSI(2) 進場不如 pullback+WR 精確**：RSI(2) 捕捉短期超賣反彈，但 XBI 的生技事件驅動波動使短期超賣訊號品質較低。WR 從 76.2%/83.3%（XBI-005）降至 62.5%/57.1%（Att3），Part B 甚至轉為負累計
3. **XBI 適合深回檔確認而非短期動量進場**：pullback+WR 的 10 日回檔範圍 8-20% 確保只在結構性回調後進場，RSI(2) 只看 2 天太短，無法過濾生技板塊的頻繁短期波動

---

## XBI-010: BB 下軌 + 回檔上限混合進場均值回歸 (BB Lower + Pullback Cap Hybrid MR)

### 目標 (Goal)

**延伸 EWJ-003 / VGK-007 / CIBR-008 / EWZ-006 的 BB 下軌 + 回檔上限混合進場模式至 XBI，測試是否能改善 XBI-005 基準。**
參考近期成功案例（EWJ 1.15% vol、VGK 1.12% vol、CIBR 1.53% vol、EWZ 1.75% vol）均驗證混合進場優於固定回檔門檻。XBI 日波動 2.0% 略高於 EWZ，測試混合進場有效邊界。

### 設計理念 (Design Rationale)

- **BB 下軌自適應門檻**：BB 帶寬根據近期波動自動調整，低波動期淺門檻捕捉訊號，高波動期深門檻隔離極端崩盤
- **回檔上限雙保險**：固定 10日高點回檔上限，過濾 BB 下軌在持續熊市中無法隔離的極端連續崩盤
- **XBI 限制**：XBI-009 已驗證 ATR 過濾在 2.0% 日波動邊界失效，故混合進場採 WR + ClosePos 雙重品質過濾（無 ATR）

### 出場參數 (Exit Parameters)

同 XBI-005：TP +3.5% / SL -5.0% / 15 天（XBI 硬底線）

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | 隔日開盤市價 (next_open_market) |
| 止盈委託 | 限價賣單 Day (limit_order_day) |
| 停損委託 | 停損市價 GTC (stop_market_gtc) |
| 到期出場 | 隔日開盤市價 (next_open_market) |
| 滑價 | 0.10% |
| 悲觀認定 | 是 |

### 三次嘗試結果 (Three Attempt Results)

| 嘗試 | 進場條件 | TP/SL/Days | Part A Sharpe | Part A 訊號 | Part B Sharpe | Part B 訊號 | min(A,B) |
|------|---------|-----------|--------------|------------|--------------|------------|----------|
| Att1 | BB(20, 1.5) 下軌 + cap -12% + WR + ClosePos 35% | +3.5%/-5.0%/15d | 0.09 | 20 | 0.07 | 8 | 0.07 |
| Att2 | BB(20, 2.0) 下軌 + cap -12% + WR + ClosePos 35% | +3.5%/-5.0%/15d | -0.03 | 7 | -0.55 | 3 | -0.55 |
| Att3 | BB(20, 2.0) OR 回檔 ≥ 8% + cap -12% + WR + ClosePos 35% | +3.5%/-5.0%/15d | 0.20 | 19 | 0.16 | 6 | 0.16 |

**vs XBI-005 基準**：Part A 0.36 / Part B 0.64 / min(A,B) 0.36

### 失敗分析 (Failure Analysis)

1. **BB 1.5σ 在 XBI 2.0% 日波動下過鬆**：Att1 的 20 個 Part A 訊號平均報酬僅 0.27%（vs XBI-005 的 1.3%），WR 65% vs 76.2%。BB 1.5σ（約均值 -3%）捕捉淺層技術超賣而非真正恐慌拋售，生技板塊需要更深層回調過濾
2. **BB 2.0σ 過嚴且集中極端事件**：Att2 僅 7/3 Part A/B 訊號，且 Part B WR 僅 33%。BB 2.0σ 訊號大多對應 2020 COVID 和 2022 熊市低點的極端崩盤，這些事件在 15 天內難以反彈至 +3.5% TP
3. **OR 進場恢復頻率但 cap -12% 過嚴**：Att3 以 19 個 Part A 訊號接近 XBI-005 的 21 個，但 cap -12% 相對 XBI-005 的 -20% 過嚴，移除深回檔贏家（2020 COVID 後的 14-18% 反彈、2022 熊市中期深跌反彈），WR 從 76.2% 降至 68.4%
4. **混合進場模式有效邊界確認為日波動 ≤ 1.75%**：XBI 2.0% 是首個驗證失敗的邊界案例。根本原因：(a) XBI 無法使用 ATR 過濾失去關鍵的波動率飆升確認組件，(b) XBI-005 的固定 pullback 8-20% 在 2.0% 日波動下已是最優框架，(c) 生技板塊 FDA/臨床事件驅動特性使訊號呈現為絕對深度回檔而非 BB 帶寬所反映的統計異常

---

## XBI-011: RSI(14) Bullish Hook Divergence + Pullback+WR+ClosePos 均值回歸

### 目標 (Goal)

測試 SIVR-015 Att1 驗證的 **RSI(14) bullish hook divergence** 過濾器是否能
改善 XBI-005 的 Part A Sharpe 0.36 / Part B 0.64（A/B 訊號比 3.5:1，累計差 57%，
訊號數差 71%）。假設：XBI-005 Part A 的 5 筆停損部分可能發生於 RSI 仍在下探中
（持續下跌結構），bullish hook 過濾器可選擇性移除這些訊號。

XBI 日波動 2.0% 與 SIVR 1.93% 相近，使用 10 日 pullback 回看（符合 lesson #20b
要求的 ≤10 日），初步判斷 hook pattern 應能泛化至 XBI。

### 進場條件 (Entry Conditions)

| # | 條件 | 指標 | 閾值 | 說明 |
|---|------|------|------|------|
| 1 | 回檔深度 | 10日高點回檔 | ≤ -8% 且 ≥ -20% | 同 XBI-005 |
| 2 | 超賣確認 | Williams %R(10) | ≤ -80 | 同 XBI-005 |
| 3 | 反轉跡象 | 收盤位置 (ClosePos) | ≥ 35% | 同 XBI-005 |
| 4 | RSI hook delta | RSI(14) − 過去 N 日 RSI 最低點 | ≥ H 點 | 新增 |
| 5 | RSI 前 oversold | 過去 N 日 RSI(14) 最低點 | ≤ L | 新增 |
| 6 | 冷卻期 | Cooldown | 10 日 | 同 XBI-005 |

### 出場參數 (Exit Parameters)

同 XBI-005：TP +3.5% / SL -5.0% / 最長持倉 15 日 / 隔日開盤市價進場 /
停損市價 GTC / 滑價 0.10%。

### 三次嘗試結果 (Three Attempt Results)

| 嘗試 | Hook (lookback/delta/max_min) | Part A Sharpe | Part A 訊號 | Part B Sharpe | Part B 訊號 | min(A,B) |
|------|-------------------------------|--------------|------------|--------------|------------|----------|
| Att1 | 5 / 3.0 / 35 (SIVR 原始) | 0.00† | 3 | 0.00† | 2 | 0.00† |
| Att2 | 5 / 3.0 / 40 | 0.27 | 7 | 0.00† | 2 | 0.27 |
| Att3 | 5 / 2.0 / 35 | 0.00† | 3 | 0.00† | 2 | 0.00† |

†零方差：所有成交均為 +3.50% TP，Sharpe 形式上為 0.00。

**vs XBI-005 基準**：Part A 0.36 / Part B 0.64 / min(A,B) 0.36

### Att1 詳情（5 / 3.0 / 35）

| 期間 | 訊號數 | 每年 | 勝率 | 累計報酬 | Sharpe |
|------|--------|------|------|----------|--------|
| Part A (2019-2023) | 3 | 0.6 | 100.0% | +10.87% | 0.00† |
| Part B (2024-2025) | 2 | 1.0 | 100.0% | +7.12% | 0.00† |

所有 5 筆交易 1-4 天內達 +3.50% TP。Part A 訊號集中於 2021-12、2022-05、2023-10，
每年僅 0.6 筆，實務上難以作為獨立策略使用。過濾器雖 100% WR，但過於嚴格。

### Att2 詳情（5 / 3.0 / 40）

| 期間 | 訊號數 | 每年 | 勝率 | 累計報酬 | Sharpe |
|------|--------|------|------|----------|--------|
| Part A (2019-2023) | 7 | 1.4 | 71.4% | +6.97% | 0.27 |
| Part B (2024-2025) | 2 | 1.0 | 100.0% | +7.12% | 0.00† |

放寬 max_min 至 40 後 Part A 新增 4 筆訊號，含 2 筆停損（WR 100%→71.4%），
Sharpe 從零方差降至 0.27（< XBI-005 的 0.36）。Part B 無新增訊號。
**A/B 累計差 2.1%**（極佳），但 **Part A 訊號品質下降**抵銷平衡改善。

### Att3 詳情（5 / 2.0 / 35）

與 Att1 完全相同（3/2 訊號全 TP），因 max_min=35 為綁定條件——符合 delta≥3
的訊號天然滿足 delta≥2。確認 **XBI 訊號的 RSI 低點門檻（max_min）為真正過濾器**，
delta 放寬無邊際效益。

### 失敗分析 (Failure Analysis)

1. **XBI 訊號 RSI(14) 分布偏高**：XBI-005 的 pullback+WR+ClosePos 訊號日，
   RSI(14) 在 5 日內最低點多在 35-45 區間，未達 SIVR-015 要求的 ≤ 35 深度 oversold。
   生技 ETF 的 FDA/臨床事件驅動特性使價格快速下跌但 RSI 未達深度 oversold
   （因為下跌往往為單日或兩日內集中，RSI(14) 尚未完全飽和）

2. **放寬門檻引入 Part A 壞訊號**：max_min 從 35 放寬至 40（Att2）新增 4 個 Part A
   訊號，其中 2 筆於 2021-2022 生技熊市停損（-5.09%、-5.10%）。新增訊號來自淺層
   RSI 回升而非真正 capitulation 結束，過濾器失去選擇性

3. **Part B 訊號結構性稀少**：Part B（2024-2025 生技復甦期）原始 XBI-005 僅 6 個訊號，
   hook 過濾器在任何參數組合下都只剩 2 個。此期間生技 ETF 經歷深跌後緩步回升，
   少有「RSI 深度 oversold 後急速回升」的 classical bullish divergence 結構

4. **延伸 cross-asset lesson #20b 邊界**：
   - **有效條件更精細化**：日波動 2-3% + pullback 回看 ≤10 日 + 已驗證 pullback+WR 框架
     **仍不足以保證泛化**，還需要**訊號日 RSI(14) 分布集中在深度 oversold（≤ 35）**
   - **XBI 2.0% 失敗 vs SIVR 1.93% 成功**：日波動幾乎相同但 RSI 分布差異顯著，
     SIVR（貴金屬）為宏觀因子驅動（美元/利率/通膨），下跌較為持續使 RSI 深度 oversold；
     XBI（生技板塊）為事件驅動，下跌集中且短促，RSI 未達深度 oversold
   - **建議待測資產修正**：原先待測名單（FCX、USO、TSLA）需進一步區分**宏觀驅動**
     vs **事件驅動**——事件驅動類資產（TSLA 個股、USO 地緣政治驅動）可能同樣失效

### 結論

XBI-005 確認為 XBI 全域最優。RSI(14) bullish hook divergence 為**第八種**在 XBI
驗證無效的策略類型（突破、ROC、動量回調、配對交易、ATR 自適應、RSI(2)、BB 下軌混合、
RSI hook divergence）。

---

## XBI-012: Capitulation + Acceleration Reversal 均值回歸 (3 iterations, all failed)

### 目標 (Goal)

測試 **3 日短期急跌 ROC + 當日強反攻收盤** 作為 XBI-005 pullback+WR+ClosePos 框架的
結構替代。假設生技 FDA/臨床事件驅動的 1-2 日急跌（而非 10 日慢磨下跌）可用 ROC(3)
捕捉，日內反攻用 ClosePos + UpDay 確認，期望捕捉與 XBI-005 互補的訊號集。

### 進場條件 (Entry Conditions)

| 條件 | Att1 | Att2 | Att3 |
|------|------|------|------|
| 10 日 pullback 下限 | ≤ -6% | 同 | 同 |
| 10 日 pullback 上限 | ≥ -20% | 同 | 同 |
| ROC(3) 門檻 | ≤ -4% | ≤ -3% | ≤ -3% |
| ClosePos 門檻 | ≥ 50% | ≥ 40% | ≥ 35% |
| UpDay 要求 | 是 | 是 | **否** |
| WR(10) 門檻 | ≤ -80 | 同 | 同 |
| 冷卻期 | 10 天 | 同 | 同 |

### 出場參數 (Exit Parameters)

三次嘗試出場參數相同（XBI 硬邊界）：TP +3.5% / SL -5.0% / 15 天持倉。

### 結果比較 (Results Comparison)

| 指標 | XBI-005 | XBI-012 Att1 | XBI-012 Att2 | XBI-012 Att3 |
|------|---------|--------------|--------------|--------------|
| Part A Sharpe | **0.36** | 0.16 | **0.27** ⬆ | 0.18 |
| Part B Sharpe | **0.64** | 0.16 | 0.16 | 0.07 ⬇ |
| **min(A,B)** | **0.36** | 0.16 | 0.16 | 0.07 |
| Part A 訊號 | 21 (4.2/yr) | 3 (0.6/yr) | 7 (1.4/yr) | 21 (4.2/yr) |
| Part B 訊號 | 6 (3.0/yr) | 3 (1.5/yr) | 3 (1.5/yr) | 8 (4.0/yr) |
| Part A WR | 76.2% | 66.7% | 71.4% | 66.7% |
| Part B WR | 83.3% | 66.7% | 66.7% | 62.5% |

### 失敗分析

1. **Att1（過嚴）**：ROC(3) ≤ -4% + ClosePos ≥ 50% + UpDay + WR ≤ -80 四重門檻
   產生 3/3 過稀疏樣本（0.6-1.5 訊號/年），即使 WR 66.7% 仍因樣本過薄使 Sharpe 0.16

2. **Att2（放寬兩門檻）**：ROC -4%→-3%、ClosePos 50%→40%，Part A 訊號 3→7 Sharpe
   0.16→0.27（+69%）。但 Part B 仍 3 訊號——2024-2025 XBI 牛市結構下 ROC(3) ≤ -3%
   事件稀少，Part B 為 binding constraint

3. **Att3（移除 UpDay）**：ClosePos 再降至 35% 並移除 UpDay，訊號暴增至 21/8。
   然而 Part A Sharpe 0.27→0.18、Part B Sharpe 0.16→0.07 雙段退步。新增訊號含 Part A
   2019-08-05 15 天到期虧損 -4.6%、2021-05-06 停損、Part B 2024-12-13 / 2025-03-31
   兩筆停損。**UpDay 過濾器為 Part B 品質的關鍵前提**

### 關鍵發現

1. **XBI 2.0% 日波動下 ROC(3) 急跌 + 日內反攻 pattern 無效**：ROC(3) ≤ -3% 的訊號
   在 Part A 2020-2023 生技熊市集中爆發，在 Part B 2024-2025 牛市稀少，無法形成
   跨 regime 穩健的均值回歸結構

2. **UpDay 過濾器為品質關鍵**：Att2→Att3 顯示移除 UpDay 使 Part A/B 雙段 Sharpe
   同步下降，證實「急跌後當日 Close > 前日 Close」是 XBI 訊號品質的必要條件。這與
   XBI-005 只需 ClosePos ≥ 35% 相比是額外過濾，但在 ROC 切入點上只是恢復 XBI-005
   的品質水平而無超越

3. **ROC-based 進場 vs Pullback-based 進場**：XBI-012 的 ROC(3) 作為主要進場觸發器
   與 XBI-006 Att3（5 日 ROC ≤ -8% + WR + ClosePos）一致失敗，確認 **pullback
   (10 日高點回檔) 為 XBI 唯一有效的主要進場觸發機制**，ROC-based 切入點只反映 XBI
   已處於 pullback 中的子集

4. **延伸 XBI 失敗策略類型清單**：XBI-012 為**第九種**在 XBI 驗證無效的策略類型
   （突破、ROC、動量回調、配對交易、ATR 自適應、RSI(2)、BB 下軌混合、RSI hook
   divergence、短期 ROC 急跌 + 日內反攻）

### 結論

XBI-005 確認為 XBI 全域最優（12 次實驗、38+ 次嘗試）。Capitulation + Acceleration
Reversal 為第九種驗證無效的策略類型。XBI 2.0% 日波動 + 生技 FDA 事件驅動下，
pullback+WR+ClosePos 35% 反轉 K 線框架已是結構最優，**任何切換主要進場觸發器
（ROC、BB、RSI hook）的嘗試皆無法超越**。

---

## XBI-014: Post-Capitulation Vol-Transition MR（3 iterations, all failed）

### 設計動機

跨資產移植 VGK-008 Att2 / INDA-010 Att3 / EEM-014 Att2 / USO-013 / IBIT-009 Att1
的「2DD floor 加深」模板至 XBI 生技板塊 ETF（2.0% 日波動，落於模板已驗證有效
vol 區間 [0.97%, 3.17%] 內）。核心假設：在 XBI-005 pullback+WR+ClosePos 框架
上新增 2 日報酬下限 `Return_2d ≤ -X%`，過濾「shallow 2DD = slow-melt drift」失敗
訊號，保留深 2DD 真 capitulation 反彈。

### 進場條件

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 10 日高點回檔 | 8-20% | 同 XBI-005 |
| 2 | Williams %R(10) | ≤ -80 | 同 XBI-005 |
| 3 | ClosePos | ≥ 35% | 同 XBI-005 |
| 4 | **Return_2d** | **≤ drop_2d_floor** | **XBI-014 核心新增**，三次迭代 sweep 門檻 |
| 5 | 冷卻期 | 10 天 | 同 XBI-005 |

### 出場參數（同 XBI-005）

| 參數 | 值 |
|------|-----|
| 達標 (TP) | +3.5% |
| 停損 (SL) | -5.0% |
| 持倉 | 15 天 |

### 三次迭代結果（成交模型 0.1% slippage，隔日開盤市價進場）

| Att | drop_2d_floor | Part A 訊號 / WR / Sharpe / cum | Part B 訊號 / WR / Sharpe / cum | min(A,B) | 結果 |
|-----|---------------|--------------------------------|-------------------------------|----------|------|
| baseline (XBI-005) | 無過濾 | 21 / 76% / 0.36 / +29.3% | 6 / 83% / 0.65 / +12.7% | **0.36** | — |
| Att1 | -2.0% (INDA/VGK 標準) | 18 / 72.2% / 0.24 / +16.64% | 6 / 66.7% / 0.16 / +3.37% | **0.16** | ✗ -56% |
| Att2 | -2.5% (USO 門檻靠攏) | 16 / 68.8% / 0.16 / +8.90% | 5 / 80.0% / 0.52 / +8.90% | **0.16** | ✗ -56% |
| Att3 | -1.0% (最輕度 ablation) | 20 / 75.0% / 0.32 / +24.96% | 6 / 83.3% / 0.64 / +12.71% | **0.32** | ✗ -11% |

### Threshold sweep 完整失敗曲線

`baseline 0.36 → -1.0% 0.32 → -2.0% 0.16 → -2.5% 0.16` 單調退化，**確認
2DD floor 加深方向對 XBI 完全無效**。

### 失敗根因

1. **XBI 2DD 分布 NO unidirectional selectivity**：Part A SLs 範圍 -1.03%~-5.53%、
   TPs 範圍 -0.23%~-6.86%，重疊整個範圍。任何 2DD 閾值都會誤殺 TPs 而保留 SLs。
2. **生技 FDA event-driven 雙峰結構**：XBI winners 同時涵蓋 shallow 2DD（短期反彈）
   與 deep 2DD（acute capitulation）兩極，與 INDA/EEM/VGK/USO/IBIT 的「shallow
   2DD = drift」單峰失敗結構**結構不同**。
3. **Cooldown chain shift**（lesson #19）：Att1 -2.0% 過濾原 2024-03-14 TP（2DD
   -1.82%）後，2024-03-15 從冷卻期釋放成新訊號，結果為 SL，淨增 1 筆 Part B SL。

### 跨資產貢獻（lesson 更新）

- **Repo 第 6 次「2DD floor 加深方向」失敗驗證**，繼 GLD-013 / COPX-010 / FCX-011 /
  TSLA-014 / GLD-013 後，**首次 US 板塊 ETF 測試**。
- 整合規則更新：Post-Capitulation Vol-Transition MR（2DD floor 加深方向）有效條件
  需同時滿足
  - (a) vol ∈ [0.97%, 3.17%] **AND**
  - (b) winners 2DD 分布**單峰**（broad ETF / 商品 / 加密 ETF）
- 事件驅動板塊 ETF（XBI FDA、CIBR 政策—但 cap 方向有效）winners 2DD 雙峰分布
  使任何單向 filter 失效。

### 結論

XBI-005 確認為 XBI 全域最優（**14 次實驗、44+ 次嘗試**）。Post-Capitulation
Vol-Transition MR 為第十一種驗證無效的策略類型（後於均值回歸基礎版、突破、
ROC、動量回調、配對交易、ATR 自適應、RSI(2)、BB 下軌混合、RSI hook divergence、
capitulation+acceleration、Gap-Down、**2DD floor**）。XBI 2.0% 日波動 + 生技 FDA
事件驅動下，**pullback+WR+ClosePos 35% 反轉 K 線框架**為結構最優，所有後續嘗試
皆無法跨越。
