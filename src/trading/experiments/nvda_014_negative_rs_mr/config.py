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
進場條件（Att2，全部滿足）
================================================================================
1. **負向相對強度**：NVDA 20d return - SMH 20d return ≤ -3%
2. **深回檔**：10 日高點回檔 ≥ 6%
3. **波動 regime gate**：ATR(20) ≤ 1.40 × ATR(60)
4. **趨勢 regime gate（lesson #22 新增）**：SMA(20) ≥ 1.00 × SMA(60)
   （NVDA-013 Att3 已驗證該 gate 在 NVDA MBPC 框架有效）
5. **冷卻期**：12 個交易日

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
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDA014Config(ExperimentConfig):
    """NVDA-014 Negative Relative Strength Mean Reversion 參數"""

    # 參考標的（半導體板塊 ETF）
    reference_ticker: str = "SMH"

    # 相對強度
    relative_strength_period: int = 20
    relative_strength_max: float = -0.03  # NVDA 20d return - SMH 20d return ≤ -3%

    # 回檔
    pullback_lookback: int = 10
    pullback_min: float = 0.06  # 從 10 日高點回檔 ≥ 6%

    # 波動 regime gate（NVDA-013 Att3 驗證有效）
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.40

    # 趨勢 regime gate（lesson #22 buffered SMA regime，Att2 新增）
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00
    use_sma_regime: bool = True

    # 冷卻期
    cooldown_days: int = 12


def create_default_config() -> NVDA014Config:
    """建立預設配置（Att1：RS ≤ -3% + pullback ≥ 6% + ATR ≤ 1.40 × ATR(60)）"""
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
