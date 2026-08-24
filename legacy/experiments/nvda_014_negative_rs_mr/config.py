"""
NVDA-014: Negative Relative Strength Mean Reversion (Pairs MR vs SMH)

策略方向（Strategy Direction）：
    **配對交易 / 相對均值回歸**（Pairs Trading / Relative Mean Reversion）。
    當 NVDA 相對半導體板塊（SMH）出現顯著相對弱勢時買進，預期 NVDA 與
    板塊的相對表現會回歸均值（NVDA 受 AI alpha 驅動的長期趨勢使「跑輸」
    為短期 mispricing）。

動機（Motivation）：
    NVDA 13 次實驗已驗證的方向：
    - 突破（NVDA-003/004 BB Squeeze）
    - 均值回歸（NVDA-001/002 純 pullback / RSI(2)）— 多 regime 失效
    - 動量（NVDA-005 momentum pullback、NVDA-009 MBPC）— Part B 強 Part A 弱
    - **正向 RS 動量延續**（NVDA-006/007/008，RS ≥ +5% + 淺回檔，min 0.47）
    - ADX/DMI 過濾（NVDA-010）
    - Capitulation depth filter（NVDA-011）
    - Lesson #22 trend regime（NVDA-012/013）

    **未測試方向 = 負向相對強度作為主訊號**：
    NVDA-006 已證實 RS 維度具預測力（+5% 正向 RS + 淺回檔 = 動量延續）。
    本實驗反向探索：當 NVDA 相對 SMH **跑輸** 顯著（RS ≤ -3%），疊加深回檔
    （≥ 6%），預期為短期 mispricing 而非結構性弱勢。

    **跨資產對照**：先前配對交易嘗試多失敗（COPX-006 COPX/FCX、XBI-008
    XBI/IBB、SIVR-009 SIVR/GLD），共同失敗模式為「比率結構性漂移」。
    NVDA/SMH 同樣存在 NVDA 長期 outperform 的漂移，但採用 **rolling
    20d return 差** 而非 60d z-score，避免長期漂移污染訊號。

    **與 NVDA-006 對比**：
    - NVDA-006: RS ≥ +5% + 5d 淺回檔 [-3%, -8%] = 動量延續
    - NVDA-014: RS ≤ -3% + 10d 深回檔 ≥ 6% = 相對均值回歸
    兩者為**相反**訊號類型，互補而非冗餘。

策略類型：配對交易 / 相對均值回歸 + 波動 regime gate

================================================================================
進場條件（Att3 final，全部滿足）
================================================================================
1. **負向相對強度（收緊）**：NVDA 20d return - SMH 20d return ≤ -5%
   （Att1 -3% 太寬鬆，續跌型訊號過多；Att3 收緊至 -5% 提升 conviction）
2. **深回檔**：10 日高點回檔 ≥ 6%
3. **波動 regime gate**：ATR(20) ≤ 1.40 × ATR(60)
4. **盤中反彈確認**：ClosePos ≥ 0.40
   （ClosePos = (Close − Low) / (High − Low)，過濾續跌型訊號，
    要求進場日盤中至少回升至日線中段）
5. **SMA regime gate**：停用（Att2 已驗證在 MR 框架反向，lesson #5）
6. **冷卻期**：12 個交易日

================================================================================
出場參數
================================================================================
- TP +6% / SL -6%（對稱）
- 最長持倉 15 天
- 滑價：0.15%
- 進場：next_open_market（隔日開盤市價）
- 出場：limit_order（TP）/ stop_market（SL）/ next_open_market（到期）
- 日內路徑：悲觀認定（同時觸 TP/SL 視為 SL）

================================================================================
基準對照（Benchmark）
================================================================================
- NVDA-013 Att3（current best）: min(A,B) 0.55, A/B cum gap 26.4%, 訊號比 1.49:1
- NVDA-012 Att2: min(A,B) 0.51
- NVDA-006 Att1（RS positive direction）: min(A,B) 0.47, A/B 訊號比 1.17:1

驗收目標：
- min(A,B) Sharpe > 0.55（超越 NVDA-013 Att3）
- A/B 累積年化差距 < 30%
- A/B 訊號比 < 1.5:1（< 50% gap）

================================================================================
迭代歷程（Iteration Log）
================================================================================
Att1（RS ≤ -3%, pullback ≥ 6%, ATR ≤ 1.40, cd 12, TP+6%/SL-6%/15d）：FAILED
    參數：relative_strength_max=-0.03, pullback_min=0.06, vol_regime_max=1.40
    結果：
        Part A: 32 訊號, WR 65.6%, 累計 +70.84%, Sharpe **0.32**
        Part B: 13 訊號, WR 38.5%, 累計 -19.39%, Sharpe **-0.25**
        min(A,B): **-0.25**（vs NVDA-013 Att3 0.55，遠低於目標）
    A/B 訊號比 32:13 = 6.4/yr vs 6.5/yr = 1.0:1（gap 0% < 50% ✓）
    A/B 累積方向相反：Part A 年化 +11.3%，Part B 年化 -10.2%
    （訊號質量 regime 依賴極強）
    失敗分析：
        - Part B 13 訊號中 8 筆 SL（多為 1-2 日內觸發 -6.14%）
        - 2024-2025 NVDA 多次深度修正（2024 Aug -17%、2025 April tariff -25%）
          觸發大量「RS ≤ -3% + 深回檔 + ATR ≤ 1.40」訊號，但續跌使快速 SL
        - **根因**：負向 RS + 深回檔在「續跌型 regime」（bear/correction）為
          續跌訊號而非 MR；ATR vol gate 在訊號日 ATR 尚未完全擴張時無法
          有效過濾這類起始崩盤期
    下一步：加入 SMA(20) ≥ 1.00 × SMA(60) 趨勢 regime 過濾（NVDA-013 已驗證
    該 gate 在 MBPC 框架有效），希望避開 2022 bear / 2024-2025 correction periods

Att2（Att1 + SMA(20) ≥ 1.00 × SMA(60) trend regime, lesson #22）：FAILED
    參數調整：sma_regime_ratio_min=1.00, use_sma_regime=True
    結果：
        Part A: 17 訊號, WR 47.1%, 累計 -9.08%, Sharpe **-0.06**
        Part B:  7 訊號, WR 28.6%, 累計 -18.15%, Sharpe **-0.49**
        min(A,B): **-0.49**（兩部分皆退化，比 Att1 更差）
    失敗分析：
        - **lesson #5 失敗模式驗證**：「趨勢濾波器 + 均值回歸 = 災難」
        - 負向 RS + 深回檔的訊號**本質上**伴隨 SMA(20) < SMA(60)
          （NVDA 跑輸 SMH 通常意味短中期均線下穿）
        - SMA regime gate 過濾了 high-quality 真實 MR 機會
          （Att1 Part A 32 → 17 訊號），移除了 winners 多於 losers
        - 與 NVDA-013 MBPC 框架不同：MBPC 為**動量延續**（uptrend pullback continuation）
          所以 SMA regime 為**同向**過濾；負向 RS MR 為**反向**訊號，
          SMA regime 為**反向**過濾
    下一步：捨棄 SMA regime gate，改採進場品質過濾：
        - 收緊 RS 門檻至 -5%（高 conviction 訊號）
        - 加入 ClosePos ≥ 40% 確認盤中反彈（intraday capitulation reversal）
        以濾掉 Part B 「續跌型」起始崩盤訊號

Att3（Att1 + RS ≤ -5% + ClosePos ≥ 40%，去除 SMA regime gate）：FAILED 仍未達標
    參數調整：
        relative_strength_max = -0.05（從 -0.03 收緊）
        close_position_min = 0.40, use_close_position = True
        use_sma_regime = False（lesson #5）
    結果：
        Part A: 21 訊號, WR 61.9%, 累計 +36.36%, Sharpe **0.29**
        Part B:  6 訊號, WR 66.7%, 累計 +11.22%, Sharpe **0.34**
        min(A,B): **0.29**（vs NVDA-013 Att3 0.55，**未達 Sharpe 目標**）
    A/B 平衡：
        - 訊號比 21:6 = 4.2/yr vs 3.0/yr = 1.40:1（gap 29% < 50% ✓）
        - 累積年化：Part A 7.27%/yr，Part B 5.61%/yr（gap 23% < 30% ✓）
        - **A/B Sharpe 平衡反向**：Part B 0.34 > Part A 0.29（無過擬合）
    分析：
        - **改善**：Att1 → Att3 min(A,B) -0.25 → 0.29，Part B 從 -0.25 → 0.34
        - RS -3% → -5% + ClosePos ≥ 40% **共同**過濾 Part B 大部分續跌型
          訊號（Part B 13 → 6 訊號，移除 7 筆中 SL 比例壓倒性高）
        - **但 Part A Sharpe 0.32 → 0.29 略降**：
          ClosePos 過濾在 Part A 同樣移除部分淺回檔型 winners（高 ClosePos
          常出現於非 capitulation 反彈），代價為訊號日期 cooldown 偏移
        - **Sharpe 目標未達**：min 0.29 < NVDA-013 Att3 0.55
    結論：**REJECT** 為新全域最優候選
        - NVDA-013 Att3（min 0.55，trend-following + 雙 regime gate）維持全域最優
        - NVDA-014 Att3 為 NVDA 第 14 次失敗策略類型（**首次負向 RS 主訊號試驗**）

================================================================================
跨資產 / 跨方向結論（Cross-Asset / Cross-Direction Findings）
================================================================================
1. **負向 RS 作為主訊號在 NVDA 失敗**（repo 首次試驗）：
   NVDA-006 已驗證**正向 RS** + 淺回檔（動量延續）為可行方向（min 0.47），
   但**負向 RS** + 深回檔（相對 MR）的鏡像方向**結構性不對稱**：
       正向 RS：NVDA outperform → 拉回是對齊回到平衡 → MR 成立
       負向 RS：NVDA underperform → 經常為**領先指標**（NVDA 帶頭跌）
                而非 mispricing → 續跌而非 MR
   AI 主導的科技龍頭股（NVDA、TSLA 類）的「跑輸板塊」常為基本面/敘事
   惡化的領先信號，而非短期 mispricing。

2. **lesson #5 重新驗證於配對交易框架**：
   「趨勢濾波器 + 均值回歸 = 災難」對「相對均值回歸」（pairs MR）同樣成立。
   SMA(20) ≥ SMA(60) 趨勢 regime 與負向 RS 訊號**本質衝突**（負向 RS
   隱含 SMA 下穿）。

3. **lesson #22 適用方向性精煉**：
   buffered SMA regime gate 之適用性取決於進場框架方向：
       同向（trend-following / momentum / breakout-pullback）→ 提升品質
       反向（mean reversion / contrarian）→ 移除好訊號（lesson #5 重新驗證）

4. **配對交易在 repo 失敗清單擴展至「同類型內」**：
   - COPX-006（COPX/FCX，異類商品）失敗：結構性漂移
   - XBI-008（XBI/IBB，同類但異權重）失敗：z-score 噪音
   - SIVR-009（SIVR/GLD，同類異槓桿）失敗：結構性漂移
   - **NVDA-014（NVDA/SMH，同類同權重，主訊號 vs 過濾器）失敗**：
     負向 RS 為領先信號，非 MR 觸發
   配對交易在 repo 上**4 種結構皆失敗**，僅在「同類同權重 + 正向 RS 作為
   過濾器」（NVDA-006、TSM-007、TSLA-007）有效。

5. **NVDA 結構性 Sharpe 上限再度驗證**：
   NVDA-013 Att3 的 min 0.55 維持全域最優（14 次實驗、43+ 次嘗試），
   NVDA 多 regime（trade war / COVID / 2021 bubble / 2022 bear / 2023 chop /
   2024-2025 AI bull + correction）使單一參數策略空間飽和。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDA014Config(ExperimentConfig):
    """NVDA-014 Negative Relative Strength Mean Reversion 參數"""

    # 參考標的（半導體板塊 ETF）
    reference_ticker: str = "SMH"

    # 相對強度（Att3：收緊至 -5% 提升 conviction）
    relative_strength_period: int = 20
    relative_strength_max: float = -0.05  # NVDA 20d return - SMH 20d return ≤ -5%

    # 回檔
    pullback_lookback: int = 10
    pullback_min: float = 0.06  # 從 10 日高點回檔 ≥ 6%

    # 盤中反彈確認（Att3：ClosePos ≥ 40% 過濾續跌型訊號）
    close_position_min: float = 0.40
    use_close_position: bool = True

    # 波動 regime gate（NVDA-013 Att3 驗證有效）
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.40

    # 趨勢 regime gate（Att2 已驗證在 MR 框架反向，lesson #5；Att3 停用）
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00
    use_sma_regime: bool = False

    # 冷卻期
    cooldown_days: int = 12


def create_default_config() -> NVDA014Config:
    """建立預設配置（Att3 final：RS ≤ -5% + ClosePos ≥ 40% + ATR ≤ 1.40，無 SMA regime）"""
    return NVDA014Config(
        name="nvda_014_negative_rs_mr",
        experiment_id="NVDA-014",
        display_name="NVDA Negative Relative Strength Mean Reversion (Pairs MR vs SMH)",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.06,
        stop_loss=-0.06,
        holding_days=15,
    )
