<!-- AI_CONTEXT_START - 此區塊供 AI Agent 快速讀取，人工更新
  last_validated: 2026-04-20
  data_through: 2025-12-31
  note: FXI-011 added 2026-04-20 (Connor's RSI Mean Reversion: composite oscillator RSI(3)+Streak_RSI(2)+PercentRank(1d return,100d), first repo trial of CRSI). Three iterations all failed vs FXI-005 min 0.38: Att1 (CRSI≤10 + PB 4-12% + ClosePos + ATR + cd10) Part A 6 signals 50% WR Sharpe 0.01 / Part B 2/2 100% WR Sharpe 4.14 — CRSI≤10 stacked on PB+ATR over-restrictive, retains only 23% of FXI-005 signal flow with 50% WR; Att2 (CRSI≤20 + PB 4-12% + ClosePos, drop ATR) Part A 16 signals 56.2% WR Sharpe 0.12 / Part B 4/4 100% WR Sharpe 5.36 — CRSI removed 8 wins but only 2 losses (CRSI dis-favors 1-day flush wins that FXI-005 captures via WR); Att3 (FXI-005 framework + CRSI≤25 as additional filter) Part A 18 signals 55.6% WR Sharpe 0.17 / Part B 3/3 100% WR Sharpe 4.74 — wins reduced 17→10 (41% drop) vs signals 26→18 (31% drop), confirming CRSI penalizes single-day flushes (high RSI(3), short streak length). Core failure: FXI's profitable MR signals are sharp 1-2 day flushes with rapid intraday recovery; CRSI's three components all penalize this profile (RSI(3) bounces back fast, streak only -1/-2, %Rank not extreme). Extends lesson #6 boundary: CRSI as additional MR filter on policy-driven EM ETFs penalizes the very signals MR rewards. FXI's 9th failed strategy type (after BB Squeeze, RSI(5), BB Lower MR, RS momentum, Stoch, Failed Breakdown, Gap-Down Capitulation, plus FXI-001 baseline). FXI-005 remains global optimum (11 experiments, 33+ attempts). FXI-010 added 2026-04-18 (Gap-Down Capitulation + Intraday Reversal MR, ported from IBIT-006 Att2 framework). Three iterations all failed to beat FXI-005 min 0.38: Att1 (gap≤-1.5%, tight exit TP+3.5%/SL-3%) Part A -0.33 / Part B -0.51 (22 signals 31.8% WR, FXI gap-down often continues, not capitulates); Att2 (gap≤-2.5% + close>midpoint + deep pullback + FXI-005 wide exit) Part A 0.04 / Part B 0.00 (too few signals 5/1); Att3 (gap as regime filter: recent 5d contains gap≤-2% + FXI-005 entry) Part A 0.34 / Part B 0.00 (22/2 signals, Part B zero variance, 2024-2025 policy event scarcity). Extends lesson #52 to gap-down capitulation structure: policy-driven EM rejects gap-down capitulation (both as entry trigger and regime filter), unlike IBIT where BTC 24/7 continuous price discovery creates genuine capitulation. FXI-009 added 2026-04-17 (Failed Breakdown Reversal / Turtle Soup, 3 iterations all failed to beat FXI-005 min 0.38; best Att1 0.00, Att2 -0.11, Att3 Part A 0 signals). Confirms short-horizon structure-break + reclaim patterns DO NOT work on policy-driven single-country EM ETFs. Extends lesson #52 to failed-breakdown / Turtle Soup variant. FXI-008 added 2026-04-17 (Stochastic Oscillator MR, 3 iterations all failed; best Att3 dual-osc 0.37). A/B signal imbalance (5:1) is structural and cannot be fixed via entry-mechanism changes alone.
-->
## AI Agent 快速索引

**當前最佳：** FXI-005 Att3（出場優化均值回歸：PB≥5% + WR(10)≤-80 + ClosePos≥40% + ATR>1.05 + cap12%，TP+5.5%/SL-5.0%/20d）**已確認全域最優（11 次實驗）**
- Part A Sharpe 0.38（WR65.4%, 26訊號, +54.97%）, Part B Sharpe 1.61（WR80%, 5訊號, +20.59%）
- min(A,B) Sharpe **0.38**（vs FXI-002 0.33，+15.2% 提升）
- Part B WR 80%（FXI-002 為 60%），SL -5.0% 拯救 2025-04-04 關鍵交易（SL→TP，+10.6pp）
- Profit Factor: A 2.14 / B 31.03

**次佳：** FXI-002 Att3（TP+5%/SL-4.5%/18d），min(A,B) 0.33

**已證明無效（禁止重複嘗試）：**
- ATR > 1.1 在 FXI（2.0% vol）過度過濾 Part B 訊號（Att1: B僅2訊號，Sharpe 0.04）
- 回檔 ≥7% 在 FXI 為 3.5σ 過深，與 2.0% vol 不匹配（Att1/Att2 A/B 失衡）
- 1:1 對稱出場（TP/SL ±3.5%）— WR < 50% 無法獲利（FXI-001 累計 -8.06%）
- **BB 擠壓突破**（FXI-003 三次迭代均失敗）：
  - 根因：2019-2023 中國熊市假突破率過高，Part A 一致為負
  - 確認跨資產教訓 #18：單一國家 EM ETF BB Squeeze 存在嚴重市場狀態依賴
- **RSI(5) 替代 WR(10)**（FXI-004 Att1/Att2）：
  - 根因：RSI(5) 無法區分恐慌急跌 vs 慢磨下跌，在中國政策驅動市場完全無效
- **2日急跌過濾替代 ATR+ClosePos**（FXI-004 Att3）：
  - 根因：2d decline 選擇性不足（45訊號 vs 26訊號），ATR+ClosePos 仍為最佳組合
- **BB 下軌均值回歸**（FXI-006 Att1/Att2）：
  - BB(20,2.0) 太鬆捕捉慢磨下跌（WR41.7%），BB(20,2.5)+多重過濾過嚴（5+1訊號）
  - 確認跨資產教訓 #52：BB 下軌 MR 在政策驅動 EM ETF 無效
- **2日急跌≤-3% 獨立進場**（FXI-006 Att3）：
  - 放棄 BB 改用 2d decline≤-3%+ATR+ClosePos，min(A,B) Sharpe 僅 0.13
  - 選擇性不足（Part A 16訊號 WR62.5%），不如 PB+WR 框架
- **RS 動量回調 FXI vs EEM**（FXI-007，三次迭代均失敗）：
  - Att1 RS≥3%+PB 2-5%+SMA(50)：Part A -0.22 / Part B 0.79（2022 熊市 4 SL）
  - Att2 RS≥3%+PB 2-5%+SMA(200)：Part A 0.16 / Part B 0.50（強化趨勢過濾但 A/B 累積差 78%）
  - Att3 RS≥4%+PB 2-5%+SMA(200)：Part A -6.63 / Part B 0.92（RS 4% 過嚴使 Part A 3 連敗）
  - **根因：中國 vs EEM 相對強度由政策/事件驅動（2022 regulatory crackdown, 2024-2025 stimulus），非結構性**
  - 確認跨資產教訓 #25：單一國家 EM ETF RS 動量策略全面失敗（INDA/EWZ/FXI 三個資料點）
  - A/B 訊號品質極度不對稱：Part B（2024-2025 政策刺激期）WR 77-86% / Part A（2019-2023）WR 46-67%
- **Stochastic Oscillator 均值回歸**（FXI-008，三次迭代均失敗）：
  - Att1 %K(14,3)≤25 AND %K>%D 交叉 + 回檔+ClosePos+ATR：Part A 0.16 / Part B 4.22（15/3 訊號），%K>%D 交叉延遲，Part A 每筆平均報酬降至 0.82%
  - Att2 %K(14,3)≤20 取代 WR：Part A 0.34 / Part B 1.49（22/4 訊號），Stoch %K 與 WR(10) 幾乎同義，僅微差
  - Att3 WR(10)≤-80 AND %K(14,3)≤20 雙振盪器（最佳嘗試）：Part A 0.37 / Part B 1.49（20/4 訊號），接近但仍 -0.01 短於 FXI-005
  - **根因：Stoch 對 FXI 無加成**。%K>%D 交叉在 MR 策略中作為 entry 過於延遲；Stoch %K(14,3) 等級與 WR(10) 數學接近（僅週期+平滑略異）；雙振盪器 intersection 品質提升不足補訊號流失
  - A/B 訊號比 5:1 為結構性問題（熊市回檔多 vs 反彈期回檔稀少），非振盪器類型可解決
- **Failed Breakdown Reversal / Turtle Soup**（FXI-009，三次迭代均失敗）：
  - Att1 breakdown_lookback=10 + bullish bar + WR≤-80 + 20d pullback 3-12% + cd10 + TP+5.5%/SL-5%/20d：Part A 8 訊號 WR 62.5% +6.27% Sharpe 0.18；Part B 1 訊號 WR 0% -5.10% Sharpe 0.00。min 0.00
  - Att2 breakdown_lookback=5 + 移除 pullback 深度下限 + ClosePos≥40%：Part A 7 訊號 WR 42.9% -4.76% Sharpe -0.11；Part B 1 訊號 WR 0% Sharpe 0.00。min -0.11（WORSE）
  - Att3 breakdown_lookback=10 + breakdown depth≥1% + ClosePos + bullish：Part A 0 訊號；Part B 1 訊號 WR 0% Sharpe 0.00。min 0.00（Part A 訊號枯竭）
  - **根因：政策驅動 EM 缺乏可靠的短期反轉結構**。FXI 的破底後「奪回」常被後續多日連環下跌（2021-11、2022-09、2023-02、2025-04 均在 reclaim 後續跌）吞噬。這與 BB 擠壓突破（FXI-003）、BB 下軌 MR（FXI-006）的失敗同根源——中國政策/事件驅動使盤中級別結構失效
  - 擴展跨資產教訓 #52 至「Turtle Soup / 失效破底反轉」——政策驅動單一國家 EM ETF 所有短週期反轉結構（BB Squeeze、BB 下軌、Stoch 交叉、failed breakdown reclaim）均無效
- **Connor's RSI (CRSI) 均值回歸**（FXI-011，三次迭代均失敗）：
  - Att1（CRSI(3,2,100)≤10 + PB 4-12% + ClosePos≥40% + ATR>1.05 + cd10）：Part A 6 訊號（3W/3L）50% WR Sharpe 0.01 / Part B 2/2 100% WR Sharpe 4.14。**過度過濾**：CRSI≤10（Connors 「extreme oversold」）+ FXI-005 三重過濾僅保留 23% 訊號流量，且 50% WR 低於 FXI-005 的 65.4%
  - Att2（CRSI≤20 + PB 4-12% + ClosePos，移除 ATR）：Part A 16 訊號 56.2% WR Sharpe 0.12 / Part B 4/4 100% WR Sharpe 5.36。CRSI≤20（標準 Connors 門檻）作為 PRIMARY 振盪器，**WR 卻 *劣於* FXI-005**——CRSI 過濾移除 8 個贏家但只移除 2 個輸家
  - Att3（FXI-005 完整框架 + CRSI≤25 作為附加過濾）：Part A 18 訊號 55.6% WR Sharpe 0.17 / Part B 3/3 100% WR Sharpe 4.74。**贏家被偏向移除**：訊號 26→18（-31%）、贏家 17→10（-41%），CRSI 反而懲罰高品質訊號
  - **核心失敗根因**：FXI 的高品質均值回歸訊號為**急跌 1-2 天 + 盤中強反彈**結構，CRSI 三組件均懲罰此類型——(a) RSI(3) 在 1-2 日反彈中已快速回升至中位，(b) Streak 長度僅 -1 或 -2（非長期下跌），(c) %Rank(1d return,100d) 在政策驅動環境的 1 日 -3% 下跌相對「常見」，並非極端。CRSI 真正觸發的條件是**多日連續慢磨下跌**——這正是 FXI-005 的 ATR>1.05 + WR≤-80 已經過濾掉的低品質訊號類型
  - **擴展 lesson #6 邊界**：CRSI 作為附加過濾器在政策驅動單一國家 EM ETF 上**反向移除好訊號**，違反「特定失敗模式濾波器」原則。FXI 第 9 種失敗策略類型（前 8 種：BB Squeeze、RSI(5)、BB 下軌 MR、RS 動量、Stoch、Failed Breakdown、Gap-Down Capitulation、FXI-001 基準）
  - **Repo 首次驗證 CRSI**：跨資產假設——CRSI 在低波動寬基 ETF（SPY/DIA/VOO ≤1.0% vol）可能仍有效，因該類資產的反轉通常涉及 3-5 日漸進過程而非 1 日急跌
- **Gap-Down Capitulation + Intraday Reversal**（FXI-010，三次迭代均失敗）：
  - Att1 gap≤-1.5% + Close>Open + PB [-5%,-15%] + WR≤-80 + TP+3.5%/SL-3%/20d/cd10：Part A 22 訊號 WR 31.8% -20.67% Sharpe -0.33；Part B 4 訊號 WR 25% -5.83% Sharpe -0.51。min -0.51（嚴重失敗）
  - Att2 加嚴 gap≤-2.5% + Close>midpoint + PB [-8%,-20%] + FXI-005 寬出場（TP+5.5%/SL-5%/20d/cd15）：Part A 5 訊號 WR 60% +0.36% Sharpe 0.04；Part B 1 訊號 WR 100% Sharpe 0.00。min 0.00（訊號太稀疏）
  - Att3 Gap 作為 regime filter（近 5d 內曾發生 gap≤-2%）+ FXI-005 entry（PB+WR+ClosePos+ATR）+ FXI-005 寬出場：Part A 22 訊號 WR 63.6% +39.08% Sharpe **0.34**；Part B 2 訊號 WR 100% +11.30% Sharpe 0.00（零方差）。min 0.00（Part A 0.34 接近但未超越 FXI-005 的 0.38）
  - **根因：政策驅動 EM 拒斥 gap-down 資本化結構**。FXI 的 HK 隔夜 gap-down 不同於 IBIT（BTC 24/7 連續交易已完成拋壓），FXI 的 gap 常因中國政策/經濟消息持續下行（Att1 中 15/22 訊號停損）。即便改為 regime filter（Att3），也過度收縮 Part B 訊號頻率（2024-2025 政策事件稀少，Part B 僅 2 訊號 1.0/yr vs FXI-005 3.0/yr），A/B 訊號比 4.4:1 遠超 1.5:1 目標
  - **擴展 lesson #52**：Gap-down capitulation 作為 entry trigger 或 regime filter 在政策驅動 EM 均無效。與 BB Squeeze、BB 下軌 MR、Stoch 交叉、failed breakdown reclaim 同列禁忌
  - **擴展 lesson #20a 邊界**：Gap-down 資本化反轉模式在傳統（非 24/7 連續交易）資產上普遍無效。此前 TQQQ-016 驗證「槓桿科技 ETF」失效，FXI-010 進一步驗證「政策驅動單一國家 EM ETF」失效——即便 FXI 擁有 HK 盤後價格發現機制，因政策/事件驅動的持續性使 gap 不等於 capitulation 終點
- **WR(14) 替代 WR(10)**（FXI-005 Att1）：
  - WR(14) 未提供任何增量（Part B 訊號完全相同），WR(10) 對 FXI 仍為最佳
- **延長冷卻期 15d**（FXI-005 Att1）：
  - 移除 3 筆 Part A 好訊號（累計 -19.5pp），勝率下降 65.4%→60.9%
- **SL -5.5%（過寬）**（FXI-005 Att2）：
  - 拯救同一關鍵交易但每筆 SL 多虧 0.49pp，Part A Sharpe 未改善（0.33 vs 0.33）

**已掃描的參數空間：**
- 回檔門檻：-5%（2.5σ★）、-6%（3σ）、-7%（3.5σ），-5% 最佳 A/B 平衡
- ATR 門檻：1.05（★）、1.1（過度過濾），1.05 適合 2.0% vol
- ClosePos：≥40%（有效，FXI 2.0% 在 ClosePos 有效邊界）
- 回檔上限：-12%（隔離 COVID/監管風暴）
- 超賣指標：WR(10)（★）、WR(14)（無增量）、RSI(5)（完全無效）
- 品質過濾：ATR+ClosePos（★）vs 2d decline（選擇性不足）
- 出場（均值回歸）：**TP+5.5%/SL-5.0%/20d（★新最佳）**、TP+5%/SL-4.5%/18d、TP+5.5%/SL-5.5%/22d、TP+3.5%/SL-3.5%/15d、TP+5%/SL-5.5%/22d
- 冷卻期：10d（★）、15d（移除好訊號）
- BB 擠壓突破：TP 3.5-5.0%、SL 3.5-5.0%、squeeze 20th-30th pct（全部失敗）
- BB 下軌 MR：BB(20,2.0) 太鬆、BB(20,2.5)+多重過濾過嚴（全部失敗）
- 2日急跌獨立進場：≤-3%+ATR+ClosePos（選擇性不足，min 0.13）

**尚未嘗試的方向（預期空間極有限）：**
- 回檔上限從 -12% 縮窄至 -10%（可能移除部分有效深回檔）
- RSI(2) 框架（日波動 ≥2% 通常無效，RSI(5) 已驗證失敗）
- ~~RS 動量（FXI vs EEM）~~ → FXI-007 三次迭代均失敗
- ~~Stochastic Oscillator 均值回歸~~ → FXI-008 三次迭代均失敗（%K>%D 交叉、%K 等級替代 WR、雙振盪器均無加成）
- ~~Failed Breakdown Reversal / Turtle Soup~~ → FXI-009 三次迭代均失敗（10d/5d breakdown、ClosePos、深度門檻均無法勝過 FXI-005）
- ~~Gap-Down Capitulation + Intraday Reversal~~ → FXI-010 三次迭代均失敗（entry trigger、regime filter 均無法勝過 FXI-005；HK 隔夜 gap 不同於 BTC 24/7 價格發現，常因政策消息持續下行）
- ~~Connor's RSI (CRSI) 均值回歸~~ → FXI-011 三次迭代均失敗（CRSI 三組件全部懲罰 1-2 日急跌+盤中反彈的高品質訊號）
- 動量回調（在高波動 EM ETF 上普遍失敗）
- SL -4.75%（介於 -4.5% 和 -5.0% 之間，可能是更精確甜蜜點）

**關鍵資產特性：**
- FXI 為中國大型股 ETF（iShares China Large-Cap ETF），追蹤中國藍籌股
- 日均波動約 2.0%，GLD 的 1.78 倍，與 SIVR 波動度相近
- 受中國政策、地緣政治、宏觀經濟影響較大，波動模式可能與商品 ETF 不同
- 流動性佳（日均成交量高），使用標準 ETF 滑價 0.1%
- ATR 過濾有效但門檻需低於標準（1.05 vs 1.1-1.15），中國市場慢跌多於急跌
- **出場參數甜蜜點**：SL -5.0% 在 FXI 2.0% vol 下提供最佳呼吸空間（-4.5% 過緊導致假停損，-5.5% 過寬增加虧損），TP +5.5% 捕捉政策驅動的較大反彈
- BB Squeeze 突破無效：中國市場熊市期（2019-2023）假突破率過高
- WR(10) 是 FXI 最佳超賣指標，WR(14) 和 RSI(5) 均無效
- **RS 動量（FXI vs EEM）無效（FXI-007 驗證）**：中國相對 EM 的超額/劣勢由政策週期驅動（2022 regulatory、2024-2025 stimulus），非結構性。與 INDA/EWZ 失敗模式一致，確認跨資產教訓 #25 延伸至中國 ETF。SMA(200) 趨勢過濾可改善 Part A 但無法解決 A/B 累積差失衡（最佳 Att2 min 0.16，仍遠低於 FXI-005 的 0.38）
- **Stochastic Oscillator 均值回歸無加成（FXI-008 驗證）**：三次迭代均未勝過 FXI-005（Att1 %K>%D 交叉 min 0.16、Att2 %K 等級替代 WR min 0.34、Att3 WR+Stoch 雙振盪器 min 0.37）。根因：(a) %K>%D 交叉延遲（已回升 1-3 天），TP 空間不足；(b) Stoch %K(14,3) 與 WR(10) ≤ -80 幾乎同義（等價於 raw %K(10) ≤ 20 vs 14 週期 + 3 日 SMA），選擇性僅微差；(c) 雙振盪器 intersection 提升品質但同時移除 Part B 好訊號。A/B 訊號比 5:1 為結構性（熊市回檔多 vs 牛市反彈少），非振盪器類型可修正
- **Failed Breakdown Reversal / Turtle Soup 無效（FXI-009 驗證）**：三次迭代均未勝過 FXI-005（Att1 10d breakdown + bullish bar min 0.00、Att2 5d breakdown + ClosePos min -0.11、Att3 10d + 1% 深度 Part A 訊號枯竭 min 0.00）。根因：FXI 政策/事件驅動使短期反轉結構全面失效——破底後「奪回」不等於反轉，常被後續多日連環下跌吞噬（Att1 所有 SL 交易 2021-11/2022-09/2023-02/2025-04 均在 reclaim 後 2-10 天停損）。擴展 lesson #52：政策驅動單一國家 EM 在所有短週期反轉結構（BB Squeeze、BB 下軌、Stoch 交叉、failed breakdown reclaim）均無效
- **Gap-Down Capitulation + Intraday Reversal 無效（FXI-010 驗證）**：三次迭代均未勝過 FXI-005。Att1（gap≤-1.5% entry trigger + tight exit）min -0.51——FXI 的 HK 隔夜 gap 不等於 capitulation 終點，中國政策消息常在美股盤中持續發酵（15/22 停損）。Att2（gap≤-2.5% + Close>midpoint + 深 pullback + FXI-005 寬出場）min 0.00——加嚴後訊號暴跌至 5/1。Att3（Gap 作為近 5d regime filter + FXI-005 entry）Part A Sharpe 0.34 最接近基線，但 Part B 僅 2 訊號（零方差）且 A/B 訊號比 4.4:1。**雙重擴展跨資產教訓**：(a) lesson #52：政策驅動 EM 拒斥 gap-down 資本化結構（entry 或 regime filter 皆失敗）；(b) lesson #20a：Gap-down 資本化反轉模式需 24/7 連續價格發現為必要前提——繼 TQQQ-016（槓桿科技 ETF）後，FXI-010 驗證「即便擁有盤後 HK 價格發現的單一國家 EM ETF」亦無法套用該模式，因政策/事件驅動使 gap 不等於 capitulation 終點
<!-- AI_CONTEXT_END -->

# FXI 實驗總覽 (FXI Experiments Overview)

## 標的特性 (Asset Characteristics)

- **FXI (iShares China Large-Cap ETF)**：追蹤中國大型股（如阿里巴巴、騰訊、工商銀行等）
- 日均波動約 2.0%，GLD 的 1.78 倍，與 SIVR 波動度相近
- 受中國政策、地緣政治風險、全球宏觀經濟影響顯著
- 流動性佳，日均成交量高，ETF 標準滑價 0.1%

## 實驗列表 (Experiment List)

| ID      | 資料夾                          | 策略摘要                    | 狀態  |
|---------|--------------------------------|----------------------------|-------|
| FXI-001 | `fxi_001_pullback_wr`          | 回檔+Williams %R 均值回歸    | 已完成（基準版） |
| FXI-002 | `fxi_002_vol_adaptive_pullback`| 波動率自適應回檔+WR+ATR      | 已完成（當前最佳★） |
| FXI-003 | `fxi_003_bb_squeeze_breakout`  | BB 擠壓突破                   | 已完成（失敗，確認禁忌）|
| FXI-004 | `fxi_004_rsi5_2d_decline`      | RSI(5)/WR + 2日急跌           | 已完成（失敗，確認 WR+ATR+ClosePos 最佳）|
| FXI-005 | `fxi_005_wr14_extended_mr`     | 出場優化均值回歸（TP5.5%/SL5%/20d）| 已完成（新最佳★）|
| FXI-006 | `fxi_006_bb_lower_mr`          | BB下軌→急跌均值回歸              | 已完成（失敗，確認 BB MR 無效）|
| FXI-007 | `fxi_007_rs_momentum`          | RS 動量回調（FXI vs EEM）         | 已完成（失敗，確認 RS 動量在單一國家 EM 無效）|
| FXI-008 | `fxi_008_stochastic_mr`        | Stochastic Oscillator 均值回歸（3 次迭代均失敗）| 已完成（失敗，確認 Stoch 對 FXI 無加成）|
| FXI-009 | `fxi_009_failed_breakdown_reversal` | Failed Breakdown Reversal / Turtle Soup（3 次迭代均失敗）| 已完成（失敗，擴展 lesson #52 至 breakdown reclaim 結構）|
| FXI-010 | `fxi_010_gap_reversal_mr`      | Gap-Down Capitulation + Intraday Reversal MR（3 次迭代均失敗）| 已完成（失敗，擴展 lesson #52 至 gap-down 資本化；雙重驗證 lesson #20a 的 24/7 先決條件）|
| FXI-011 | `fxi_011_connors_rsi_mr`       | Connor's RSI (CRSI) 均值回歸（3 次迭代均失敗）| 已完成（失敗，擴展 lesson #6 至 CRSI 過濾器在政策驅動 EM 反向移除好訊號）|

---

## FXI-001: Pullback + Williams %R Mean Reversion

**目標**：以 10 日高點回檔 + Williams %R 雙重條件捕捉 FXI 超賣反彈機會，參考 SIVR-003 框架（波動度相近）。

### 進場條件（全部滿足）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 10 日高點回檔 | ≤ -7% | 依 FXI 2.0% 日波動縮放（GLD:-3%, SIVR:-7%） |
| 2 | Williams %R(10) | ≤ -80 | 跨資產通用超賣指標 |
| 冷卻 | 訊號間隔 | ≥ 10 交易日 | 避免重複訊號 |

### 出場參數

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 | +3.5% | 依波動度縮放，與 SIVR-003 一致 |
| 停損 | -3.5% | 1:1 風報比，利用勝率獲利 |
| 持倉天數 | 15 天 | 中等波動均值回歸標準持倉 |

### 成交模型

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價） |
| 獲利出場 | `limit_order Day`（當日限價單） |
| 停損出場 | `stop_market GTC`（持倉期間停損市價） |
| 到期出場 | `next_open_market`（隔日開盤市價） |
| 滑價 | 0.10%（ETF 標準滑價） |
| 悲觀認定 | 是（同 bar 停損與獲利同時觸發 → 假設停損先成交） |

### 設計理念

- **參考 SIVR-003**：FXI 日波動 ~2.0% 與 SIVR 相近（GLD 1.78 倍），直接採用 SIVR-003 已驗證的參數架構
- **雙條件過濾**：回檔幅度 + WR 超賣，天然適應趨勢行情（參考點隨趨勢上移）
- **不使用追蹤停損**：日波動 ~2% 處於追蹤停損禁用區間（cross-asset lesson #2）
- **1:1 風報比**：TP/SL 對稱，依靠勝率 > 55% 產生正期望值
- **ETF 標準滑價**：FXI 流動性優於 SIVR，使用 0.1% 標準 ETF 滑價

### 回測結果

| 指標 | Part A (In-Sample) | Part B (Out-of-Sample) | Part C (Live) |
|------|-------------------|----------------------|---------------|
| 區間 | 2019-01-01 ~ 2023-12-31 | 2024-01-01 ~ 2025-12-31 | 2026-01-01 ~ today |
| 訊號數 | 36 (7.2/年) | 9 (4.5/年) | 2 (7.5/年) |
| 勝率 | 47.2% | 44.4% | 0.0% |
| 平均報酬 | -0.17% | -0.11% | -3.32% |
| 累計報酬 | -8.06% | -1.45% | -6.53% |
| 平均持倉 | 4.9 天 | 8.4 天 | 14.5 天 |
| 最大回撤 | -11.79% | -9.77% | -3.93% |
| 最大連續虧損 | 3 | 3 | 2 |

---

---

## FXI-002: Volatility-Adaptive Pullback + WR Mean Reversion

**目標**：在 FXI-001 基礎上加入三層過濾 + 非對稱出場，參考 EWZ-002 Att3 架構。

### 進場條件（全部滿足）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | 10 日高點回檔 | ≤ -5% | 2.5σ for 2% vol（與 GLD -3%/1.2% vol 同比例）|
| 2 | 10 日高點回檔上限 | ≥ -12% | 隔離 COVID / 中國監管風暴等極端崩盤 |
| 3 | Williams %R(10) | ≤ -80 | 跨資產通用超賣指標 |
| 4 | Close Position | ≥ 40% | 日內反轉確認（FXI 2.0% vol 在有效邊界）|
| 5 | ATR(5)/ATR(20) | > 1.05 | 波動率飆升過濾（per COPX 2.25% vol 先例）|
| 冷卻 | 訊號間隔 | ≥ 10 交易日 | 避免重複訊號 |

### 出場參數

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 | +5.0% | 非對稱出場，盈虧比 1.11:1 |
| 停損 | -4.5% | 寬 SL 給 2.0% vol 呼吸空間 |
| 持倉天數 | 18 天 | 延長持倉配合較高 TP |

### 成交模型

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價）|
| 獲利出場 | `limit_order Day`（當日限價單）|
| 停損出場 | `stop_market GTC`（持倉期間停損市價）|
| 到期出場 | `next_open_market`（隔日開盤市價）|
| 滑價 | 0.10%（ETF 標準滑價）|
| 悲觀認定 | 是（同 bar 停損與獲利同時觸發 → 假設停損先成交）|

### 設計理念

- **參考 EWZ-002 Att3**：FXI 日波動 ~2.0% 與 EWZ ~1.75% 相近，採用成功的 ATR+ClosePos+cap 三層過濾架構
- **ATR > 1.05**：中國市場慢跌多於急跌，標準 1.1 門檻過度過濾 Part B 訊號（Att1 驗證）
- **回檔 -5%**：2.5σ 深度比，與 GLD -3%/1.2% vol 一致，比 -7%（3.5σ）更匹配 FXI 波動度
- **非對稱出場**：TP+5%/SL-4.5%，盈虧比 1.11:1 補償勝率略低於 70%

### 迭代記錄

| Att | 回檔 | ATR | Part A Sharpe | Part B Sharpe | min | 結論 |
|-----|------|-----|--------------|--------------|-----|------|
| 1 | ≥7% | >1.1 | 0.33 (14訊號) | 0.04 (2訊號) | 0.33 | ATR 1.1 過度過濾 |
| 2 | ≥6% | >1.05 | 0.44 (20訊號) | 0.30 (4訊號) | 0.30 | 改善但 A/B 差距仍大 |
| 3★ | ≥5% | >1.05 | 0.33 (26訊號) | 0.50 (5訊號) | 0.33 | Part B 超越 Part A |

### 回測結果（Att3★）

| 指標 | Part A (In-Sample) | Part B (Out-of-Sample) | Part C (Live) |
|------|-------------------|----------------------|---------------|
| 區間 | 2019-01-01 ~ 2023-12-31 | 2024-01-01 ~ 2025-12-31 | 2026-01-01 ~ today |
| 訊號數 | 26 (5.2/年) | 5 (2.5/年) | 2 (7.5/年) |
| 勝率 | 65.4% | 60.0% | 0.0% |
| 平均報酬 | +1.49% | +1.97% | -3.26% |
| 累計報酬 | +43.19% | +9.82% | -6.44% |
| 平均持倉 | 9.1 天 | 8.4 天 | 17.5 天 |
| 最大回撤 | -11.79% | -4.61% | -5.98% |
| 盈虧比 | 1.94 | 2.91 | 0.00 |
| Sharpe | 0.33 | 0.50 | -2.45 |
| 最大連續虧損 | 2 | 1 | 2 |

---

## FXI-003: BB Squeeze Breakout

**目標**：測試 BB 擠壓突破策略在中國大型股 ETF 上的效果，作為均值回歸的替代方向。

### 進場條件（全部滿足）

| 條件 | 指標 | 閾值 | 說明 |
|------|------|------|------|
| 1 | BB 帶寬百分位 | 60 日 30th pct 以下 | 波動率壓縮（近 5 日內） |
| 2 | 收盤價 > BB 上軌 | BB(20, 2.0) | 向上突破確認 |
| 3 | 收盤價 > SMA(50) | 趨勢確認 | 甜蜜點（跨資產驗證）|
| 冷卻 | 訊號間隔 | ≥ 10 交易日 | 避免重複訊號 |

### 出場參數（Att2★）

| 參數 | 值 | 說明 |
|------|-----|------|
| 獲利目標 | +3.5% | 按 FXI 2.0% vol 縮放 |
| 停損 | -5.0% | 寬 SL 給 post-breakout pullback 呼吸空間 |
| 持倉天數 | 20 天 | 延長持倉配合較低 TP |

### 成交模型

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價）|
| 獲利出場 | `limit_order Day`（當日限價單）|
| 停損出場 | `stop_market GTC`（持倉期間停損市價）|
| 到期出場 | `next_open_market`（隔日開盤市價）|
| 滑價 | 0.10%（ETF 標準滑價）|
| 悲觀認定 | 是（同 bar 停損與獲利同時觸發 → 假設停損先成交）|

### 設計理念

- **策略類型轉換**：FXI-001/002 均為均值回歸，本實驗測試突破策略作為替代方向
- **參考 EEM-005**：EEM BB Squeeze min(A,B) 0.18，為 EM ETF 中唯一有效的突破案例
- **跨資產教訓 #18 測試**：INDA/EWT 驗證單一國家 EM ETF 突破失敗，FXI 為第三個驗證點
- **中國市場假設**：政策驅動的波動率壓縮→突破模式可能有效（假設被否定）

### 迭代記錄

| Att | TP/SL | Squeeze | Cooldown | Part A Sharpe | Part B Sharpe | min | 結論 |
|-----|-------|---------|----------|--------------|--------------|-----|------|
| 1 | 5%/-4% | 30th | 10 | -0.15 (18訊號, WR33%) | 0.28 (10訊號, WR60%) | -0.15 | Part A 44% SL 率 |
| 2★ | 3.5%/-5% | 30th | 10 | -0.12 (18訊號, WR50%) | 0.14 (10訊號, WR60%) | -0.12 | 最佳但仍負值 |
| 3 | 4%/-3.5% | 20th | 15 | -0.30 (17訊號, WR29%) | 0.28 (7訊號, WR57%) | -0.30 | 緊 SL 59% SL 率 |

### 回測結果（Att2★）

| 指標 | Part A (In-Sample) | Part B (Out-of-Sample) | Part C (Live) |
|------|-------------------|----------------------|---------------|
| 區間 | 2019-01-01 ~ 2023-12-31 | 2024-01-01 ~ 2025-12-31 | 2026-01-01 ~ today |
| 訊號數 | 18 (3.6/年) | 10 (5.0/年) | 1 (3.6/年) |
| 勝率 | 50.0% | 60.0% | 100.0% |
| 平均報酬 | -0.46% | +0.54% | +3.50% |
| 累計報酬 | -9.25% | +4.71% | +3.50% |
| 平均持倉 | 10.6 天 | 9.4 天 | 17.0 天 |
| 最大回撤 | -6.57% | -5.71% | -1.44% |
| 盈虧比 | 0.78 | 1.34 | ∞ |
| Sharpe | -0.12 | 0.14 | 0.00 |

### 失敗分析

**根因**：中國市場 2019-2023 經歷持續熊市（科技監管風暴 2021、COVID 清零 2022、房地產危機 2022-2023），BB Squeeze 突破在熊市中產生大量假突破：
- Part A 8-10 筆停損（占 44-59%），突破後快速反轉
- Part B（2024-2025 中國刺激政策反彈期）表現較好但 Sharpe 僅 0.14-0.28
- A/B 累計報酬差距 14-23pp，嚴重市場狀態依賴

**跨資產教訓更新**：FXI 為第四個驗證單一國家 EM ETF BB Squeeze 失敗的案例（INDA/EWT/FXI），僅 EEM（多國分散化 EM ETF）有效。

---

## FXI-004: RSI(5) / WR + 2-Day Sharp Decline Mean Reversion

**目標**：測試不同的進場指標（RSI(5) vs WR(10)）和品質過濾器（2日急跌 vs ATR+ClosePos），尋找 FXI 均值回歸的替代方案。

### 設計理念

- **RSI(5) 測試**：TQQQ-010 證明 RSI(5) 在極端波動資產上有效，FXI 2.0% vol 可能受益
- **2日急跌過濾**：USO-013 驗證 2日急跌在 2.2% vol 商品 ETF 有效，直接測量賣壓加速度
- **取代 ATR+ClosePos**：簡化進場條件，測試更直接的品質過濾機制

### 迭代記錄

| Att | 進場框架 | 參數 | Part A Sharpe | Part B Sharpe | min | 結論 |
|-----|---------|------|--------------|--------------|-----|------|
| 1 | RSI(5)+2d decline | RSI<28, 2d≤-2.0% | -0.03 (38訊號, WR47.4%) | 0.24 (7訊號, WR57.1%) | -0.03 | RSI(5) 太鬆，A/B 5.4:1 |
| 2 | RSI(5)+2d decline | RSI<22, 2d≤-3.0% | -0.11 (24訊號, WR41.7%) | 0.31 (4訊號, WR50%) | -0.11 | 收緊反降 WR |
| 3 | WR(10)+2d decline | WR≤-80, 2d≤-2.0% | 0.01 (45訊號, WR48.9%) | 0.05 (12訊號, WR50%) | 0.01 | 2d decline 選擇性不足 |

### 回測結果（Att3，WR+2d decline 最佳嘗試）

| 指標 | Part A (In-Sample) | Part B (Out-of-Sample) | Part C (Live) |
|------|-------------------|----------------------|---------------|
| 區間 | 2019-01-01 ~ 2023-12-31 | 2024-01-01 ~ 2025-12-31 | 2026-01-01 ~ today |
| 訊號數 | 45 (9.0/年) | 12 (6.0/年) | 3 (10.7/年) |
| 勝率 | 48.9% | 50.0% | 33.3% |
| 平均報酬 | +0.06% | +0.24% | -1.13% |
| 累計報酬 | -2.06% | +1.67% | -3.56% |
| 平均持倉 | 7.5 天 | 10.8 天 | 16.7 天 |
| 最大回撤 | -9.08% | -10.15% | -5.98% |
| 盈虧比 | 1.03 | 1.12 | 0.55 |
| Sharpe | 0.01 | 0.05 | -0.30 |
| 最大連續虧損 | 4 | 2 | 2 |

### 失敗分析

**Att1/Att2 失敗根因**：RSI(5) 在 FXI 2.0% 日波動下完全無效。RSI(5) 測量動量衰竭但無法區分「恐慌急跌」（可回歸）和「政策驅動慢磨下跌」（不可回歸）。收緊門檻（RSI<28→22）反而降低 WR（47.4%→41.7%），因為極端超賣在中國熊市中更常出現在不可回歸的結構性崩盤中。此結果延伸教訓 #27（RSI 在日波動 >2% 無效）至 RSI(5) 時框。

**Att3 失敗根因**：回歸 WR(10) 後訊號品質大幅改善（WR47.4%→48.9%），但 2日急跌過濾選擇性不足。Part A 產生 45 訊號（9.0/年）vs FXI-002 的 26 訊號（5.2/年），多出的 19 個訊號為低品質假訊號。ATR(5)/ATR(20)>1.05 + ClosePos≥40% 的雙重過濾機制在區分恐慌 vs 慢磨方面仍然嚴格優於 2日急跌單一過濾。

**跨資產教訓更新**：
- RSI(5) 在 FXI 無效，確認 RSI 系列指標（RSI(2)/RSI(5)）在政策驅動 EM ETF 上均不適用
- 2日急跌過濾在 FXI 選擇性不足，不如 ATR+ClosePos 雙重機制（與 USO 相比，FXI 的慢磨下跌比例更高）

---

## FXI-005: Exit-Optimized Mean Reversion ★新最佳

**目標**：在 FXI-002 已驗證的進場框架上優化出場參數，測試更寬的 TP/SL 組合是否能捕捉 FXI 政策驅動的較大波動反彈。

### 設計理念 (Design Rationale)

- **進場條件不變**：FXI-002 Att3 的 PB≥5%+WR(10)≤-80+ClosePos≥40%+ATR>1.05 已跨 4 次實驗驗證為最佳
- **出場優化假設**：FXI 2.0% 日波動的政策驅動市場（刺激政策、地緣政治），反彈幅度可能超過 +5% 且初始回撤可能超過 -4.5%
- **SL 甜蜜點搜尋**：從 -4.5%（FXI-002）向 -5.0%/-5.5% 擴展，尋找呼吸空間最佳值

### 進場條件 (Entry Conditions)

同 FXI-002 Att3：PB≥5% + cap 12% + WR(10)≤-80 + ClosePos≥40% + ATR>1.05 + cooldown 10d

### 迭代記錄 (Iteration History)

| Att | 關鍵變更 | TP/SL/Hold | Part A Sharpe | Part B Sharpe | min | 結論 |
|-----|---------|-----------|--------------|--------------|-----|------|
| 1 | WR(14)+cooldown 15d | 5%/-4.5%/18d | 0.23 (23訊號, WR60.9%) | 0.50 (5訊號, WR60%) | 0.23 | WR(14) 無增量，CD 移除好訊號 |
| 2 | 寬出場 | 5.5%/-5.5%/22d | 0.33 (26訊號, WR65.4%) | 1.40 (5訊號, WR80%) | 0.33 | Part B 大幅改善，Part A Sharpe 未變 |
| 3★ | 中間 SL | 5.5%/-5.0%/20d | **0.38** (26訊號, WR65.4%) | **1.61** (5訊號, WR80%) | **0.38** | SL 甜蜜點，超越 FXI-002 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價）|
| 獲利出場 | `limit_order Day`（當日限價單）|
| 停損出場 | `stop_market GTC`（持倉期間停損市價）|
| 到期出場 | `next_open_market`（隔日開盤市價）|
| 滑價 | 0.10%（ETF 標準滑價）|
| 悲觀認定 | 是（同 bar 停損與獲利同時觸發 → 假設停損先成交）|

### 回測結果 (Backtest Results) — Att3★ Final

| 區間 | 期間 | 訊號數 | 勝率 | 累計報酬 | Sharpe | Profit Factor | MDD |
|------|------|--------|------|----------|--------|---------------|-----|
| Part A (IS) | 2019-01-01 ~ 2023-12-31 | 26 (5.2/年) | 65.4% | +54.97% | 0.38 | 2.14 | -11.79% |
| Part B (OOS) | 2024-01-01 ~ 2025-12-31 | 5 (2.5/年) | 80.0% | +20.59% | 1.61 | 31.03 | -4.61% |
| Part C (Live) | 2026-01-01 ~ 2026-04-15 | 2 (7.1/年) | 0.0% | -5.74% | -1.30 | 0.00 | -5.98% |

### 關鍵發現

1. **SL -5.0% 是 FXI 的甜蜜點**：-4.5%（FXI-002）過緊導致 2025-04-04 假停損（-4.60% 後反彈至 +5.50%），-5.5%（Att2）過寬增加每筆 SL 虧損。-5.0% 同時拯救關鍵交易且控制損失。
2. **出場參數非對稱有效**：TP/SL = 5.5%/5.0% = 1.1:1 盈虧比，配合 65.4% WR 產生正期望值，且高 TP 捕捉政策驅動的大幅反彈。
3. **WR(14) 對 FXI 無增量**：Att1 驗證 WR(14) 產生完全相同的 Part B 訊號，在 Part A 未改善品質。WR(10) 仍為 FXI 最佳超賣指標。
4. **延長冷卻期有害**：15d cooldown 移除 3 筆 Part A 好訊號（均為贏家），累計報酬下降 19.5pp。

---

## FXI-006: BB Lower Band → Acute Decline Mean Reversion

**目標**：測試 BB 下軌均值回歸（少見方向，BB 通常用於突破）及 2日急跌獨立進場，尋找 FXI 均值回歸的替代框架。

### 設計理念 (Design Rationale)

- **BB 下軌 MR（Att1/Att2）**：BB 在本 repo 10+ 資產用於突破，但幾乎未用於 MR（僅 SIVR-013）。假設 BB 下軌能捕捉統計極端偏離。
- **2日急跌獨立進場（Att3）**：放棄 BB，改用 2d decline≤-3% 直接測量急性賣壓，搭配 ATR+ClosePos 過濾。
- **差異化出場**：Att3 加寬 SL -5.5%（2.75σ）+ 延長持倉 22d，給予政策驅動市場更多恢復空間。

### 迭代記錄 (Iteration History)

| Att | 進場框架 | 參數 | Part A Sharpe | Part B Sharpe | min | 結論 |
|-----|---------|------|--------------|--------------|-----|------|
| 1 | BB(20,2.0) lower + ATR + ClosePos | TP5%/SL4.5%/18d | -0.19 (12訊號, WR41.7%) | 0.04 (2訊號) | -0.19 | BB 2.0σ 太鬆 |
| 2 | BB(20,2.5) + PB + WR + ATR + ClosePos | TP5%/SL4.5%/18d | -0.70 (5訊號, WR20%) | 0.00 (1訊號) | -0.70 | 多重過濾過嚴 |
| 3 | 2d decline≤-3% + ATR + ClosePos | TP5%/SL5.5%/22d | 0.23 (16訊號, WR62.5%) | 0.13 (4訊號, WR50%) | 0.13 | A/B 平衡但 Sharpe 低 |

### 成交模型 (Execution Model)

| 項目 | 設定 |
|------|------|
| 進場模式 | `next_open_market`（隔日開盤市價）|
| 獲利出場 | `limit_order Day`（當日限價單）|
| 停損出場 | `stop_market GTC`（持倉期間停損市價）|
| 到期出場 | `next_open_market`（隔日開盤市價）|
| 滑價 | 0.10%（ETF 標準滑價）|
| 悲觀認定 | 是（同 bar 停損與獲利同時觸發 → 假設停損先成交）|

### 回測結果 (Backtest Results) — Att3 (最佳嘗試)

| 指標 | Part A (In-Sample) | Part B (Out-of-Sample) | Part C (Live) |
|------|-------------------|----------------------|---------------|
| 區間 | 2019-01-01 ~ 2023-12-31 | 2024-01-01 ~ 2025-12-31 | 2026-01-01 ~ today |
| 訊號數 | 16 (3.2/年) | 4 (2.0/年) | 2 (7.0/年) |
| 勝率 | 62.5% | 50.0% | 0.0% |
| 平均報酬 | +1.12% | +0.61% | -3.96% |
| 累計報酬 | +17.35% | +2.04% | -7.79% |
| 平均持倉 | 11.5 天 | 11.5 天 | 20.0 天 |
| 最大回撤 | -11.79% | -5.85% | -5.98% |
| 盈虧比 | 1.62 | 1.32 | 0.00 |
| Sharpe | 0.23 | 0.13 | -2.43 |
| 最大連續虧損 | 2 | 2 | 2 |

### 失敗分析

**Att1/Att2 根因**：BB 下軌在 FXI 完全無效。BB(20,2.0) 太鬆（12訊號中大量為慢磨下跌觸碰下軌而非急跌反彈機會），WR41.7%。收緊至 BB(20,2.5) + 多重過濾後訊號崩壞至 5+1。BB 帶寬在政策驅動 EM ETF 的自適應性差——中國市場持續熊市期 BB 不斷外擴，下軌變得毫無選擇性。確認跨資產教訓 #52。

**Att3 根因**：放棄 BB 改用 2d decline≤-3% + ATR + ClosePos，A/B 平衡改善（15pp gap vs FXI-002 的 34pp gap），但 min(A,B) Sharpe 僅 0.13，遠低於 FXI-005 的 0.38。2d decline 作為主進場訊號缺乏 PB（10日高點回檔）的趨勢參考點功能——PB 天然適應趨勢（參考點隨趨勢上移），而 2d decline 對所有 -3% 跌幅一視同仁。

**結論**：三次迭代均未超越 FXI-005（0.38），FXI-002/005 的 PB+WR+ATR+ClosePos 框架仍為 FXI 均值回歸的唯一有效架構。

---

## 參數對照表 (Parameter Comparison)

| 參數 | FXI-001 | FXI-002 Att3 | FXI-003 Att2 | FXI-004 Att3 | FXI-005 Att3★ | FXI-006 Att3 |
|------|---------|--------------|-------------|-------------|---------------|--------------|
| 策略類型 | 均值回歸 | 均值回歸 | BB 擠壓突破 | 均值回歸（2d decline） | 出場優化均值回歸 | BB下軌→急跌MR |
| 回檔門檻 | ≥7% | ≥5% | — | ≥5% | ≥5% | — |
| 回檔上限 | 無 | ≤12% | — | ≤12% | ≤12% | — |
| 超賣指標 | WR(10)≤-80 | WR(10)≤-80 | — | WR(10)≤-80 | WR(10)≤-80 | — |
| ClosePos | 無 | ≥40% | — | 無 | ≥40% | ≥40% |
| ATR 過濾 | 無 | >1.05 | — | 無 | >1.05 | >1.05 |
| 2日急跌 | 無 | 無 | — | ≤-2.0% | 無 | ≤-3.0% |
| BB Squeeze | — | — | 30th pct/60日 | — | — | — |
| BB Lower | — | — | — | — | — | Att1/2 使用 |
| SMA 趨勢 | — | — | SMA(50) | — | — | — |
| TP | +3.5% | +5.0% | +3.5% | +5.0% | **+5.5%** | +5.0% |
| SL | -3.5% | -4.5% | -5.0% | -4.5% | **-5.0%** | -5.5% |
| 持倉 | 15天 | 18天 | 20天 | 18天 | **20天** | 22天 |
| 冷卻 | 10天 | 10天 | 10天 | 10天 | 10天 | 10天 |
| Part A Sharpe | -0.17 | 0.33 | -0.12 | 0.01 | **0.38** | 0.23 |
| Part B Sharpe | -0.11 | 0.50 | 0.14 | 0.05 | **1.61** | 0.13 |
| min(A,B) | -0.17 | 0.33 | -0.12 | 0.01 | **0.38** | 0.13 |

---

## 演進路線圖 (Roadmap)

FXI-001 (回檔+WR 基礎版)
  └── FXI-002 (波動率自適應 + ClosePos + cap + 非對稱出場)
  │   └── FXI-003 ✗ (BB 擠壓突破 — 三次迭代失敗，確認單一國家 EM ETF 突破禁忌)
  │   └── FXI-005★ (出場優化 MR — TP+5.5%/SL-5.0%/20d，min 0.38 超越 FXI-002)
  │         ├── Att1 ✗ WR(14)+cooldown 15d（min 0.23，WR(14) 無增量，CD 移除好訊號）
  │         ├── Att2 TP5.5%/SL-5.5%/22d（min 0.33，Part B 1.40，SL 過寬）
  │         └── Att3★ TP5.5%/SL-5.0%/20d（min 0.38，SL 甜蜜點）
  └── FXI-004 ✗ (RSI(5)/WR + 2日急跌 — RSI(5) 完全無效，2d decline 選擇性不足)
  └── FXI-006 ✗ (BB 下軌→急跌 MR — BB 下軌無效，2d decline 獨立進場 min 0.13)
  └── FXI-007 ✗ (RS 動量回調 FXI vs EEM — 三次迭代均失敗，確認單一國家 EM RS 動量禁忌)
  └── FXI-008 ✗ (Stochastic Oscillator 均值回歸 — 三次迭代均失敗，確認 Stoch 對 FXI 無加成)

---

## FXI-007: Relative Strength Momentum Pullback (FXI vs EEM)

### 目標 (Goal)

在 FXI 首次嘗試 RS 動量策略，參考 EWT-007 成功模板（RS vs EEM，min 0.42）。
假設：中國相對新興市場的超額表現由政策週期驅動，動量持續性可能優於均值回歸。

### 進場條件 (Entry Conditions)

| 條件 | 指標 | 閾值（最終 Att2）|
|------|------|------|
| 1 | FXI - EEM 20日報酬差 | ≥ 3% |
| 2 | 5日高點回撤 | 2%-5% |
| 3 | 趨勢確認 | Close > SMA(200) |
| 4 | 冷卻期 | 10 交易日 |

### 出場參數 (Exit Parameters)

| 參數 | 值 | 說明 |
|------|------|------|
| 獲利目標 (TP) | +4.0% | 中等波動 EM 標準 |
| 停損 (SL) | -4.5% | 需呼吸空間（FXI 2.0% vol）|
| 最長持倉 | 20 天 | RS 動量標準 |
| 追蹤停損 | 無 | 日波動 2.0% 禁用 |

### 成交模型 (Execution Model)

同 FXI-005：隔日開盤市價進場、限價賣單 Day、停損市價 GTC、到期隔日開盤、滑價 0.1%、悲觀認定。

### 迭代嘗試紀錄 (Iteration Log)

| # | 變更 | Part A Sharpe | Part B Sharpe | A/B 訊號 | A WR / B WR | 結論 |
|---|------|---------------|---------------|----------|-------------|------|
| 1 | RS≥3%, SMA(50) | -0.22 | 0.79 | 13/9 | 46.2%/77.8% | 2022 熊市 4 SL 拖累 Part A |
| 2 | RS≥3%, SMA(200)（最佳嘗試）| 0.16 | 0.50 | 6/8 | 66.7%/75.0% | 強化趨勢過濾翻正 Part A 但 A/B 累積差 78% |
| 3 | RS≥4%, SMA(200) | -6.63 | 0.92 | 3/7 | 0%/85.7% | RS 4% 過嚴，Part A 3 連敗 |

### 失敗分析 (Failure Analysis)

- **策略方向**：相對強度動量回調（momentum pullback）— repo 中較少使用的方向
- **關鍵參數**：RS 門檻（3-4%）、趨勢過濾（SMA(50) vs SMA(200)）、淺回調 2-5%
- **結果**：三次迭代最佳 min(A,B) Sharpe 0.16 < FXI-005 的 0.38
- **失敗根因**：
  1. 中國 vs EEM 相對強度由政策/地緣事件驅動（2022 regulatory crackdown、
     2024-2025 stimulus），非結構性。動量訊號在政策轉折點急速反轉
  2. Part A（2019-2023 中國熊市）與 Part B（2024-2025 刺激期）訊號品質極度
     不對稱：Part B WR 77-86% / Part A WR 46-67%
  3. 收緊 RS 門檻在稀疏樣本上造成統計脆弱（Att3 Part A 僅 3 筆全敗）
- **確認跨資產教訓 #25**：單一國家 EM ETF RS 動量策略全面失敗
  （INDA-007、EWZ-005、FXI-007 共三個資料點）
- **結論**：FXI 不應進一步探索 RS 動量方向，回歸 FXI-005 均值回歸框架

---

## FXI-008: Stochastic Oscillator %K/%D Mean Reversion（三次迭代均失敗）

### 目標 (Goal)

探索 repo 中尚未使用的 **Stochastic Oscillator** 作為均值回歸超賣指標，
目標改善 FXI-005 的 Part A/B 訊號不平衡（26:5, 5.2:1，超越教訓 #8 的
3:1 危險門檻）。假設 Stochastic 的平滑特性 + %K/%D 交叉確認可提升
訊號品質，過濾中國熊市中 WR 反覆觸及但未真正反轉的假訊號。

### 進場條件（最終 Att3）

| 條件 | 指標 | 閾值 |
|------|------|------|
| 1 | 10 日高點回檔 | ≤ -5% |
| 2 | 回檔上限 | ≥ -12% |
| 3 | Williams %R(10) | ≤ -80 |
| 4 | Stochastic %K(14,3) | ≤ 20 |
| 5 | Close Position | ≥ 40% |
| 6 | ATR(5)/ATR(20) | > 1.05 |
| 7 | 冷卻期 | 10 交易日 |

### 出場參數

同 FXI-005：TP +5.5% / SL -5.0% / 20 天 / 無追蹤停損。

### 成交模型

同 FXI-005：隔日開盤市價進場、限價賣單 Day、停損市價 GTC、到期隔日開盤、
滑價 0.1%、悲觀認定。

### 迭代嘗試紀錄 (Iteration Log)

| # | 變更 | Part A Sharpe | Part B Sharpe | A/B 訊號 | A WR / B WR | 結論 |
|---|------|---------------|---------------|----------|-------------|------|
| 1 | %K(14,3)≤25 AND %K>%D 交叉 | 0.16 | 4.22 | 15/3 | 60.0%/100% | %K>%D 交叉太晚，彈升已完成；Part A 品質反降、Part B 訊號過度縮減 |
| 2 | %K(14,3)≤20 取代 WR（純等級）| 0.34 | 1.49 | 22/4 | 63.6%/75.0% | Stoch %K 與 WR(10) 選擇性接近，略為減少 Part A 訊號但未提升 Sharpe |
| 3 | WR(10)≤-80 AND %K(14,3)≤20（雙振盪器）| 0.37 | 1.49 | 20/4 | 65.0%/75.0% | 最接近 FXI-005 但仍 -0.01 短；雙振盪器 intersection 輕微提升品質不足補訊號流失 |

### 失敗分析 (Failure Analysis)

- **策略方向**：Stochastic Oscillator 均值回歸（新振盪器類型，repo 中從未使用）
- **關鍵參數**：%K(14,3) 平滑週期、%K ≤ 20/25 等級、%K>%D 交叉確認
- **結果**：三次迭代最佳 min(A,B) Sharpe 0.37 < FXI-005 的 0.38
- **失敗根因**：
  1. **%K>%D 交叉是延遲指標**：由於 %K 是原始 %K 的 3 日 SMA、%D 是 %K 的 3 日 SMA，
     交叉發生時 price 已回升 1-3 天，+5.5% TP 空間所剩無幾（Att1 Part A 平均
     報酬 0.82%，遠低於 FXI-005 的 2.11%）
  2. **Stoch %K 與 WR(10) 幾乎同義**：WR(10) ≤ -80 等價於 raw %K(10) ≤ 20。
     Stoch %K(14,3) 僅將週期延長 4 日並加 3 日 SMA 平滑，選擇性僅微差（Att2 移除 4 個
     Part A 訊號），未提升單筆品質
  3. **雙振盪器 intersection 邊際效益極小**：Att3 兩個振盪器 agreement 移除
     6 個 Part A 假訊號（品質提升，avg ret 1.77% vs 0.82%），但同時也移除
     1 個 Part B 好訊號，min(A,B) 淨 -0.01
  4. **A/B 訊號不平衡是結構性問題**：5:1 的訊號比源自 2019-2023 熊市回檔頻繁 vs
     2024-2025 反彈回檔稀少，非振盪器類型可以解決。需要市場狀態識別（regime filter）
     才能根本改善，但這會違反跨資產教訓 #5（均值回歸加趨勢濾波）
- **確認跨資產教訓 #6**：已精確訊號上疊加確認指標（雙振盪器）邊際效益遞減
- **結論**：Stochastic Oscillator 不適合 FXI 作為均值回歸進場指標；
  FXI-005 的 WR(10)≤-80 + ATR + ClosePos 框架已近最優，改進方向應著重於
  出場邏輯或 regime-aware 的訊號權重調整（超出純技術面範圍）

---

## FXI-009: Failed Breakdown Reversal / Turtle Soup（三次迭代均失敗）

### 目標 (Goal)

嘗試 repo 中**從未使用**的 **Failed Breakdown Reversal (Turtle Soup)**
策略方向：捕捉 FXI 在短期低點被跌破後隨即反彈的「假突破」結構。假設政策
驅動的 FXI 常在訊息面恐慌殺跌後 1 天內展現極端反轉（2024-01、2024-09、
2025-01 的 V 型底部），若能精準捕捉這些結構性反轉，可改善 FXI-005 的 A/B
訊號不平衡（26:5, 5.2:1）並提升 Part B 訊號密度。

### 策略方向

**失效破底反轉 / Turtle Soup**：
1. 第 T-1 日：Low 跌破過去 N 日最低點（真實破底）
2. 第 T 日：Close 重回過去 N 日最低點之上（奪回支撐）
3. 第 T 日：Close > Open（盤中累積性反轉）
4. WR(10) 於 T 日仍在超賣區（≤ -80）
5. 20 日高點回檔 ≥ -12%（隔離 COVID/監管風暴崩盤）

### 迭代嘗試紀錄 (Iteration Log)

| # | 變更 | Part A Sharpe | Part B Sharpe | A/B 訊號 | A WR / B WR | 結論 |
|---|------|---------------|---------------|----------|-------------|------|
| 1 | breakdown_lookback=10, 20d PB∈[-12%,-3%], WR≤-80, bullish bar, TP+5.5%/SL-5%/20d/cd10 | 0.18 | 0.00 | 8/1 | 62.5%/0.0% | 基線嘗試；Part B 僅 1 訊號（2025-04-01 關稅前）停損。10 日破底太稀疏，-3% 深度下限過濾掉淺回檔假突破但也排除 stimulus 期反轉 |
| 2 | breakdown_lookback=5, 移除 PB 深度下限, 加 ClosePos≥40% | -0.11 | 0.00 | 7/1 | 42.9%/0.0% | 5 日破底太常見；Part A WR 崩至 42.9%。ClosePos 未提升品質——FXI 高波動使合格反轉日不一定收在盤高 |
| 3 | breakdown_lookback=10, breakdown depth≥1%（真實深破）, 保留 ClosePos + bullish | 0.00* | 0.00 | 0/1 | N/A | 1% 深度門檻過嚴，Part A 訊號枯竭。FXI 的 10 日低點通常只被略微跌破即反彈 |

_* Part A 0 訊號，無法計算有意義的 Sharpe_

### 進場條件（三次迭代）

**Att1 基線**：
| 條件 | 指標 | 閾值 |
|------|------|------|
| 1 | 10 日破底 | Low_{T-1} < min(Low over [T-11, T-2]) |
| 2 | 奪回 | Close_T > 同 10 日最低點 |
| 3 | 盤中強勢 | Close_T > Open_T |
| 4 | 超賣 | WR(10) ≤ -80 |
| 5 | 回檔深度 | 20 日 PB 在 [-12%, -3%] |
| 6 | 冷卻 | 10 交易日 |

**Att2**：breakdown_lookback=10→5，移除 PB 深度下限，新增 ClosePos≥40%
**Att3**：breakdown_lookback=5→10，新增 breakdown_depth_pct=0.01（1% 真實破底）

### 出場參數

同 FXI-005：TP +5.5% / SL -5.0% / 20 天 / 無追蹤停損 / cd 10 天。

### 成交模型

同 FXI-005：隔日開盤市價進場、限價賣單 Day、停損市價 GTC、到期隔日開盤、
滑價 0.1%、悲觀認定。

### 失敗分析 (Failure Analysis)

- **策略方向**：Failed Breakdown Reversal / Turtle Soup（repo 中全新類別）
- **關鍵參數**：breakdown_lookback（5/10）、breakdown_depth_pct（0/0.01）、
  pullback_threshold（-3%/無）、close_position_threshold（無/0.4）
- **結果**：三次迭代最佳 min(A,B) Sharpe 0.00（Att1）< FXI-005 的 0.38
- **失敗根因**：
  1. **Part B 僅 1 訊號（兩次迭代相同）**：2024-2025 stimulus rally 中 FXI
     沒有足夠「真破底 + 奪回」事件，整個 breakdown reclaim 結構極其稀疏
  2. **Reclaim 不代表反轉**：Att1 的 8 筆 Part A 有 3 筆停損（2021-11、2022-09、
     2023-02），全部在「奪回」後 4-15 天再度跌穿 -5%，暴露政策驅動 EM 缺乏持續
     性反轉能量的結構性問題
  3. **短期 breakdown 過於常見**：Att2 將 lookback 降至 5 日後，Part A 訊號維
     持但品質崩壞（WR 62.5%→42.9%），證明短期破底頻繁發生在震盪環境且無統計意義
  4. **深破門檻雙面不討好**：Att3 的 1% 深破要求排除 Part A 所有訊號，FXI 的 10 日
     破底通常只被略微跌破即反彈，無法同時要求真實深破 + 次日奪回
  5. **Part B 單一訊號（2025-04-01）的毀滅性停損**：關稅公告前夜觸發 failed
     breakdown 結構，但隔日關稅消息使 FXI 繼續深跌 7%+，證明「結構性反轉」
     對政策/事件驅動 EM 毫無預測力
- **擴展跨資產教訓 #52**：政策驅動單一國家 EM ETF（FXI）在所有短週期反轉結構均失敗：
  - BB Squeeze 突破（FXI-003）
  - BB 下軌 MR（FXI-006）
  - Stochastic %K>%D 交叉（FXI-008）
  - **Failed breakdown reclaim（FXI-009，新增）**
- **結論**：Turtle Soup 在政策驅動 EM 上因缺乏穩定反轉結構而失效；FXI 的超額反彈
  事件由政策/消息驅動，無法用純技術面的 breakdown reclaim 型態捕捉。FXI-005
  的 PB+WR+ATR+ClosePos 框架仍為全域最優，且訊號頻率結構性不平衡（5:1）無法用
  進場結構改變解決

---

## FXI-010: Gap-Down Capitulation + Intraday Reversal MR（三次迭代均失敗）

**目標**：驗證 IBIT-006 Att2 的 Gap-Down 資本化 + 日內反轉模式是否延伸至 FXI。
FXI 追蹤香港 H 股，HK 市場於美股盤後交易（HKT 9:30-16:00 = ET 21:30-04:00），
重大中國政策/事件消息常導致 FXI 隔夜出現結構性跳空下跌；若市場盤中反轉
（Close > Open），理論上可視為事件拋壓消化完畢的 buy-the-dip 訊號。

**策略方向**：均值回歸（事件驅動拋壓 + 日內反轉確認）

**關鍵假設**：Gap-down 資本化反轉模式不僅限於 24/7 連續交易加密 ETF（IBIT），可能延伸至「盤外存在實質價格發現 + 高波動」的單一國家 EM ETF。

### Att1（Baseline）— 直接移植 IBIT-006 Att2 架構，按 FXI 波動度縮放
**進場**：Gap ≤ -1.5% + Close > Open + 10d Pullback [-5%, -15%] + WR(10) ≤ -80 + cd=10
**出場**：TP +3.5% / SL -3.0% / 持倉 20 天（緊出場，對應 IBIT-006 的 TP 4.5%/SL 4.0% 按波動度 2.0%/3.17% 縮放）

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 22 | 4 |
| 勝率 | 31.8% | 25.0% |
| 累計報酬 | -20.67% | -5.83% |
| Sharpe | -0.33 | -0.51 |

**失敗分析**：
1. Gap-down -1.5% 為 0.75σ 過鬆，放入大量普通回檔日，22 訊號中 15 停損、7 達標，盈虧比 0.53
2. FXI 的 HK 隔夜 gap 不同於 IBIT（BTC 24/7 連續交易已完成拋壓）——中國政策/經濟消息常在美股盤中持續發酵，gap-down 後常續跌而非反轉
3. A/B 訊號比 5.5:1 嚴重不平衡（超出 50% 目標）

### Att2 — 加嚴 gap 門檻 + 深回檔 + 寬 SL 呼吸空間
**進場**：Gap ≤ -2.5% + Close > Open + Close > (High+Low)/2 + 10d Pullback [-8%, -20%] + WR(10) ≤ -80 + cd=15
**出場**：TP +5.5% / SL -5.0% / 持倉 20 天（FXI-005 寬出場框架）

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 5 | 1 |
| 勝率 | 60.0% | 100% |
| 累計報酬 | +0.36% | +5.50% |
| Sharpe | 0.04 | 0.00（零方差）|

**失敗分析**：加嚴到 gap ≤ -2.5%（1.25σ）+ 強反轉（Close 高於當日中點）+ 深 pullback（下界 8%）後，Part A 訊號暴跌 22→5，Part B 僅 1 訊號（年化 0.5/yr，遠低於可評估閾值）。WR 雖提升至 60%，但樣本稀薄無統計信心。

### Att3 — Gap-Down 作為近期 capitulation regime filter
**進場**：FXI-005 entry（PB≥5% + WR(10)≤-80 + ClosePos≥40% + ATR>1.05 + cap12%） + 近 5 日內至少 1 日 Gap ≤ -2.0% 事件 + cd10
**出場**：TP +5.5% / SL -5.0% / 持倉 20 天（FXI-005 框架）

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 22 | 2 |
| 勝率 | 63.6% | 100% |
| 累計報酬 | +39.08% | +11.30% |
| Sharpe | **0.34** | 0.00（零方差）|

**最接近基線但仍失敗**：
1. Part A Sharpe 0.34 接近但未超越 FXI-005 的 0.38
2. Part B 僅 2 訊號（2024-2025 政策事件稀少），年化訊號頻率 1.0/yr vs FXI-005 的 3.0/yr
3. A/B 訊號比 4.4:1 遠超 1.5:1 目標；A/B 累計差 27.78pp（71% 相對差）超出 30% 目標
4. Part B 2 筆皆 +5.5% 達標（零方差使 Sharpe 綁定 = 0.00）

### 結論與跨資產教訓更新

**失敗根因（三次迭代一致）**：
1. **FXI gap 不等於 capitulation**：HK 隔夜政策/經濟消息常在美股盤中持續發酵，與 IBIT 的「24/7 拋壓完成 + 美股開盤撿便宜」結構本質不同
2. **Gap 作為 entry trigger** 過度放入低品質訊號（Att1 WR 31.8%）
3. **Gap 作為 regime filter** 過度收縮 Part B 訊號頻率（Att3 Part B 僅 2 訊號）
4. **政策事件稀疏性** 在 Part B 被進一步暴露——2024-2025 中國政策事件不如 2019-2023 密集

**擴展跨資產教訓 #52**：
- 政策驅動單一國家 EM ETF（FXI）在所有短週期反轉結構均失敗：
  - BB Squeeze 突破（FXI-003）
  - BB 下軌 MR（FXI-006）
  - Stochastic %K>%D 交叉（FXI-008）
  - Failed breakdown reclaim（FXI-009）
  - **Gap-down capitulation（FXI-010，新增）**——entry trigger 或 regime filter 均無效

**擴展跨資產教訓 #20a（IBIT-006 模式）邊界**：
- 此前 TQQQ-016 驗證「槓桿科技 ETF」失效
- FXI-010 進一步驗證「即便擁有盤後 HK 價格發現的單一國家 EM ETF」亦無法套用
- **精煉先決條件**：Gap-down 資本化反轉模式需「盤外連續價格發現」+「拋壓不受政策/事件持續性影響」兩項必要條件；FXI 滿足前者但不滿足後者

---

## FXI-011: Connor's RSI (CRSI) Mean Reversion（三次迭代均失敗）

**目標**：以 Connor's RSI（CRSI = mean of RSI(3) + Streak_RSI(2) + PercentRank(1d return,100d)）作為複合超賣指標，驗證是否能修正 FXI-005 的 A/B 績效落差（Part A Sharpe 0.38 / Part B 1.61，cum 差 62.5%、訊號數差 80.7%）。

**策略方向**：均值回歸（複合超賣振盪器，repo 首次驗證）

**關鍵假設**：CRSI 三組件分別捕捉動能（RSI(3)）、持續性（Streak_RSI(2)）、相對歷史強度（%Rank(100d)），可比單一 WR/RSI 更精準辨別「真實 capitulation vs 慢磨延續」。Streak 組件特別應有助於分辨 1 日急跌（短 streak）vs 多日慢磨（長 streak）。

### Att1 — CRSI ≤ 10（Connors「extreme oversold」）+ FXI-005 三重過濾
**進場**：CRSI ≤ 10 + 10d Pullback [-4%, -12%] + ClosePos ≥ 40% + ATR > 1.05 + cd10
**出場**：TP +5.5% / SL -5.0% / 持倉 20 天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 6 | 2 |
| 勝率 | 50.0% | 100% |
| 累計報酬 | -0.33% | +9.04% |
| Sharpe | **0.01** | 4.14 |

**失敗分析**：CRSI ≤ 10 為「極端」門檻（Connors 標準為 ≤ 5），疊加 PB+ClosePos+ATR 三重過濾後僅保留 23% 訊號流量，Part A 6 筆中 3 停損 + 2 到期 + 1 達標，WR 僅 50%（vs FXI-005 65.4%）。CRSI 過度過濾。

### Att2 — CRSI ≤ 20 取代 WR + 移除 ATR
**進場**：CRSI ≤ 20 + 10d Pullback [-4%, -12%] + ClosePos ≥ 40% + cd10（移除 ATR、移除 WR(10)）
**出場**：TP +5.5% / SL -5.0% / 持倉 20 天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 16 | 4 |
| 勝率 | 56.2% | 100% |
| 累計報酬 | +7.69% | +21.37% |
| Sharpe | **0.12** | 5.36 |

**失敗分析**：CRSI ≤ 20（標準 Connors 門檻）作為 PRIMARY 振盪器，Part A WR 56.2% **劣於** FXI-005 的 65.4%。對比 FXI-005 的 Part A 26 訊號 17 贏家：
- CRSI 過濾保留 16/26 = 62% 訊號
- 但僅保留 9/17 = 53% 贏家
- 而保留 7/9 = 78% 輸家

**CRSI 對 FXI 的訊號選擇 *偏向移除贏家*** — 反向效果。

### Att3 — FXI-005 完整框架 + CRSI ≤ 25 作為附加過濾
**進場**：10d Pullback [-5%, -12%] + WR(10) ≤ -80 + CRSI ≤ 25 + ClosePos ≥ 40% + ATR > 1.05 + cd10
**出場**：TP +5.5% / SL -5.0% / 持倉 20 天

| 指標 | Part A | Part B |
|------|--------|--------|
| 訊號數 | 18 | 3 |
| 勝率 | 55.6% | 100% |
| 累計報酬 | +13.63% | +15.04% |
| Sharpe | **0.17** | 4.74 |

**失敗分析**：CRSI ≤ 25 為「寬鬆」附加過濾，仍偏向移除贏家：
- 訊號 26→18（-31%）
- 贏家 17→10（-41%）
- 輸家 9→8（-11%）
**贏家流失率（41%）顯著高於輸家流失率（11%）**——CRSI 確認系統性懲罰高品質訊號。

### 結論與跨資產教訓更新

**失敗根因（三次迭代一致）**：
1. **FXI 的高品質 MR 訊號為「急跌 1-2 天 + 盤中強反彈」結構**，CRSI 三組件全部懲罰此類型：
   - **RSI(3)**：1-2 日急跌後盤中反彈使 RSI(3) 已快速回升至中位（30-50），CRSI 第一組件不夠低
   - **Streak_RSI(2)**：streak 長度僅 -1 或 -2（非長期下跌），Streak_RSI 不夠低
   - **%Rank(1d return, 100d)**：政策驅動環境的 1 日 -3% 下跌相對「常見」，%Rank 不夠極端
2. **CRSI 真正觸發的條件是多日連續慢磨下跌**（streak -4 以上、%Rank 極低），但這正是 FXI-005 的 ATR>1.05 + WR≤-80 + ClosePos≥40% 已過濾掉的低品質訊號類型
3. **Att3 的「直接相加 CRSI 過濾」沒有任何附加價值**——CRSI 與 FXI-005 既有過濾器系統性反向
4. A/B 訊號比 6:1（Att3 18:3）遠超 50% 目標，與 FXI-010 失敗模式相同

**擴展跨資產教訓 #6 邊界**：
- Lesson #6 的「特定失敗模式濾波器」例外條件**不適用 CRSI 在政策驅動 EM 上**
- **CRSI 作為附加過濾器在政策驅動單一國家 EM ETF 上反向移除好訊號**，加入「禁止重複嘗試」清單

**Repo 首次驗證 CRSI**：
- 跨資產假設：CRSI 在低波動寬基 ETF（SPY/DIA/VOO ≤ 1.0% vol）可能仍有效，因該類資產的反轉通常涉及 3-5 日漸進過程而非 1 日急跌；建議優先測試 DIA-005 RSI(2) 框架的 CRSI 替代版本
- **不適用範圍**：政策/事件驅動單一國家 ETF（FXI、URA、TLT 同類），高波動加密 ETF（IBIT 同類），高波動個股（TSLA/NVDA 同類，動能特性使 streak 成分過於波動）

**FXI 第 9 種失敗策略類型**（前 8 種：BB Squeeze、RSI(5)、BB 下軌 MR、RS 動量、Stoch、Failed Breakdown、Gap-Down Capitulation、FXI-001 1:1 對稱出場）。FXI-005 確認為全域最優（11 次實驗、33+ 次嘗試）。

