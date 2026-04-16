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
  derived_from: [TQQQ-007,TQQQ-012,TQQQ-013,USO-006,USO-010~020,TSM-004,FCX-003,SIVR-006,SIVR-007,IWM-005,XBI-005]
  validated: 2026-03-31
  data_through: 2025-12-31
  confidence: high
-->

核心訊號已精確時，額外確認指標減少訊號數量而不提升品質。

**例外**：針對特定失敗模式的濾波器有效（如 GLD-007 ClosePos≥40% 移除仍在下跌的訊號、IWM-005 ClosePos 移除無反轉確認假訊號、XBI-005 ClosePos≥35%）。ClosePos 有效邊界約為日波動 ≤ 2.0%（GLD 1.1%、IWM 1.5-2%、XBI 2.0% 有效；SIVR 2-3%、FCX 2-4% 無效）。

**規則**：只在確認能修復某個已知失敗模式時才加濾波器，不要隨意「加一個指標看看」。

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
  validated: 2026-04-16
  data_through: 2025-12-31
  confidence: high
  note: CIBR-008 updated 2026-04-16 (BB lower band + pullback cap -12% hybrid, min(A,B) 0.27→0.39, +44%, 8 experiments). EWJ-003 updated 2026-04-16 (BB lower band + pullback cap hybrid, Part A Sharpe 0.55→0.60, 3 experiments). †EWJ min(A,B) uses Part A Sharpe as binding constraint — Part B Sharpe formally 0.00 due to zero variance (6/6 trades returned identical +3.50%)
-->

| 資產 | 最佳實驗 | 策略類型 | min(A,B) Sharpe | 全域最優確認 |
|------|----------|----------|-----------------|-------------|
| TQQQ | TQQQ-010 | 極端恐慌買入 | 0.36 | 15 次實驗 ✓ |
| GLD | GLD-012 Att3 | 20日回調+WR（無追蹤停損）| 0.48 | 12 次實驗 ✓ |
| SIVR | SIVR-005 | 回檔範圍+WR | 0.22 | 16 次實驗 ✓ |
| FCX | FCX-001/FCX-004 | 三重極端超賣/BB Squeeze | 0.43/0.41 | 8 次實驗 ✓ |
| USO | USO-013 | 緊密回檔+RSI(2)+2日急跌 | 0.26 | 21 次實驗 ✓ |
| SPY | SPY-005 | RSI(2) 寬出場 | 0.53 | 8 次實驗 ✓ |
| DIA | DIA-005 | RSI(2) 延長持倉 | 0.47 | 11 次實驗 ✓ |
| VOO | VOO-003 | RSI(2) 寬獲利目標 | 0.53 | 3 次實驗 ✓ |
| SOXL | SOXL-010 Att3 | 板塊 RS 動量回調 | 0.70 | 11 次實驗 ✓ |
| TSM | TSM-008 | RS 出場優化 | 0.79 | 9 次實驗 ✓ |
| IWM | IWM-011 | 波動率自適應 RSI(2) | 0.52 | 11 次實驗 ✓ |
| XBI | XBI-005 | 回檔範圍+WR+反轉K線 | 0.36 | 9 次實驗 ✓ |
| COPX | COPX-007 | 波動率自適應均值回歸 | 0.45 | 8 次實驗 ✓ |
| URA | URA-004 | 回檔範圍+RSI(2)+2日急跌 | 0.39 | 7 次實驗 ✓ |
| NVDA | NVDA-004 | BB 擠壓突破（優化）| 0.47 | 8 次實驗 ✓ |
| IBIT | IBIT-001 | 回檔範圍+WR | 0.15 | 5 次實驗 ✓ |
| TSLA | TSLA-009 Att2 | BB 擠壓突破（30th pct）| 0.40 | 12 次實驗 ✓ |
| TLT | TLT-002 | 回檔+WR+反轉K線+60日跌幅 | -0.20/0.24 | 無純技術面解法（12 次實驗）|
| EEM | EEM-005 Att2 | BB 擠壓突破（30th pct）| 0.18 | 11 次實驗 ✓ |
| EWJ | EWJ-003 Att3 | BB 下軌+回檔上限+WR+ATR（混合進場）| 0.60† | 3 次實驗 |
| EWT | EWT-007 Att1 | RS 動量回調（EWT vs EEM）| 0.42 | 7 次實驗 ✓ |
| VGK | VGK-003 Att2 | 回檔+WR+ATR 波動率自適應 | 0.42 | 6 次實驗 ✓ |
| XLU | XLU-011 | 波動率自適應均值回歸 | 0.67 | 11 次實驗 ✓ |
| INDA | INDA-005 Att3 | 出場優化均值回歸（回檔+WR+ClosePos+ATR）| 0.23 | 6 次實驗 ✓ |
| FXI | FXI-005 Att3 | 出場優化均值回歸（TP5.5%/SL5%/20d）| 0.38 | 6 次實驗 ✓ |
| EWZ | EWZ-002 Att3 | 波動率自適應回檔+WR+非對稱出場 | 0.34 | 5 次實驗 ✓ |
| CIBR | CIBR-008 Att2 | BB 下軌+回檔上限-12%+WR+ClosePos+ATR | 0.39 | 8 次實驗 ✓ |

> 各實驗詳細參數、探索歷程和確認邏輯見 [cross_asset_evidence.md](cross_asset_evidence.md) Section 9。

---

## 10. 反覆失敗的做法（禁止清單）
<!-- freshness:
  validated: 2026-04-16
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
25. **動量回調在多成分等權重板塊 ETF** — 板塊級 ROC 反映個股事件加總非板塊趨勢。**RS 動量（板塊 vs SPY/QQQ）對市值加權板塊 ETF 同樣無效**：CIBR 三次嘗試（QQQ/SPY 基準、鬆/緊/品質過濾）均負 Sharpe，網路安全無獨立板塊動量週期（CIBR-006 驗證）。RS 動量有效條件：(a) 強週期性板塊如半導體（SOXL-010）或 (b) 地理/資產類別差異大且**週期性**的比較對（EWT vs EEM）。**持續性結構優勢（如 INDA vs EEM：人口紅利/IT）不產生有效 RS 訊號**：INDA-007 三次嘗試（RS 2~3%、ATR 1.10~1.15）Part A -0.49~0.07，極端市場狀態依賴。**宏觀事件驅動的商品優勢（EWZ vs EEM）同樣無效**：EWZ-005 三次嘗試（RS 10d/15d/20d、2-4%門檻、含/不含 ATR），min(A,B) -0.33~-0.21，A/B 訊號比 6-7:1，巴西商品優勢受大宗商品價格/BRL 匯率/政治事件驅動而非週期性
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
52. **BB 下軌均值回歸在政策驅動 EM ETF** — BB(20,2.0) 太鬆捕捉慢磨下跌（FXI WR41.7%），BB(20,2.5)+多重過濾過嚴（5+1訊號）。BB 帶寬在持續熊市中不斷外擴，下軌失去選擇性。2d decline≤-3% 獨立進場亦僅 min 0.13，不如 PB+WR 框架。**例外**：EWJ-003 驗證 BB 下軌+回檔上限混合進場在日本市場有效（Sharpe 0.60），因日本市場無中國式政策衝擊（FXI-006 驗證）。**CIBR-008 Att2 進一步驗證**：在美國板塊 ETF（CIBR 1.53% vol）上 BB(20,2.0) + 回檔上限 -12%（7.8σ）+ WR + ClosePos + ATR 混合進場 min(A,B) 0.39（+44% vs CIBR-007 純 BB 下軌的 0.27）。回檔上限有效隔離崩盤連續段訊號（COVID 2020-03 深度 >12%），BB 下軌仍提供統計自適應進場。混合進場模式適用：低中波動（≤2.0%）資產+三重品質過濾+回檔上限 7-8σ

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
- **非美國已開發市場 ETF（VGK/EWJ）**：pullback+WR+ATR 框架最佳，RSI(2) 無效（歐洲/日本市場慢磨特性）。EWJ-003 驗證 BB 下軌+回檔上限混合進場優於固定回檔門檻（Part A Sharpe 0.55→0.60）
- **新興市場寬基 ETF（EEM）**：BB 擠壓突破最佳（EM risk-on/risk-off 資金流驅動突破），均值回歸受 EM 事件拖累
- **新興市場單一國家 ETF（EWZ）**：pullback+WR+ATR+非對稱出場最佳（波動率自適應過濾有效，日波動 1.75%）
- **板塊/商品 ETF（XBI/COPX/URA/SIVR）**：pullback+WR 深回檔框架最佳，RSI(2) 無效
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

## 20. 跨資產相關性配對策略的結構性風險
<!-- freshness:
  derived_from: [XLU-005,COPX-006,SIVR-009,TSM-009,FCX-006,DIA-009,EEM-006]
  validated: 2026-04-10
  data_through: 2025-12-31
  confidence: high
-->

跨資產相關性可能隨宏觀環境改變而失效（regime change）。Part A 正 + Part B 負 Sharpe 是相關性崩潰的典型特徵。個股 vs 板塊 ETF RS 策略僅在個股有持續性結構優勢（如 TSM 先進製程護城河）時有效，商品生產者（FCX）的超額表現由短期事件驅動，無持續性。廣基 ETF RS（如 EEM vs SPY）受宏觀/政治事件（關稅、貿易戰）驅動，三次嘗試 Part B 均為負值。
