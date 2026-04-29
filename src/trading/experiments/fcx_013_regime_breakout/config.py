"""
FCX-013: Multi-Week Regime-Aware BB Squeeze Breakout 配置
FCX Multi-Week Regime-Aware BB Squeeze Breakout Configuration

策略方向：將 lesson #22（TSLA-015 / NVDA-012 驗證 buffered multi-week SMA
trend regime）跨資產移植至 FCX-004 BB Squeeze Breakout 之上。**Repo 第 3 次
lesson #22 試驗，首次商品/礦業單股驗證**（前兩次：TSLA 3.72% vol 高 beta 個股、
NVDA 2.5-3% vol AI 牛市個股）。

基礎（同 FCX-004 Att2，當前 BB Squeeze 最佳 min(A,B) 0.41）：
- BB(20, 2.0) + 60 日 30th 百分位擠壓 + Close > Upper BB + Close > SMA(50)
- 冷卻 10 天，TP+8%/SL-7%/20d，0.15% 滑價（高 vol 個股）

FCX-013 新增 regime 過濾（lesson #22）：
- **多週期趨勢 regime**：SMA(20) ≥ k × SMA(60)
  - 預測候選 k 值：
    - k = 0.99（TSLA 甜蜜點，3.72% vol，1% 緩衝）為起點（Att1）
    - k = 0.97（NVDA 甜蜜點，2.5-3% vol，3% 緩衝）為次選（待測）
    - k = 1.00（嚴格，無緩衝）為對照（待測）
- **多週期波動 regime**：依 TSLA-015 Att3 / NVDA-012 ablation 證實對 BB
  Squeeze 框架冗餘（squeeze 條件已含「近期低波動」語意），預設不啟用

================================================================================
基準：FCX-004 Att2（已執行驗證，min(A,B) 0.41）
================================================================================
- Part A: 23 訊號, WR 69.6%, 累計 +106.31%, Sharpe 0.51（16 TP / 6 SL / 1 EX）
- Part B: 6 訊號, WR 66.7%, 累計 +17.31%, Sharpe 0.41（4 TP / 2 SL）
- min(A,B) 0.41
- A/B cum gap 89%（>>30% 目標）, A/B 訊號比 3.83:1（>>1.5:1 目標）
- 嚴重失衡，是 repo 中 A/B 平衡最差的 BB Squeeze 結果之一

trade-level signal-day 分析（SMA20/SMA60 ratio）：
  Part A SLs:
    2019-07-24 SL: ratio 1.0331（bull regime）
    2020-01-13 SL: ratio 1.1171（bull, COVID precursor）
    2021-04-15 SL: ratio 1.0225（bull, 銅復甦中段拉回）
    2021-11-11 SL: ratio 1.0785（bull, 後峰回檔）
    2022-08-25 SL: ratio 0.9690（bear, Jackson Hole 鷹派）★
    2023-06-13 SL: ratio 0.9519（弱復甦，bear 邊界）★
  Part A 1 bad EX:
    2023-07-13 EX -3.69%: ratio 1.0496（bull）
  Part A TPs (16):
    2019-01-09 TP: ratio 0.9348（transition winner，2018 bear 後）
    2019-04-04~ratio 1.0332~1.1773（bull regime TPs，主流）
    2021-10-14 TP: ratio 0.9483（transition winner）
    2022-10-21 TP: ratio 0.9698（bear-to-bull transition）
    2023-11-20 TP: ratio 0.9396（transition winner）
  Part B (6):
    2024-03-07 TP: ratio 0.9595（transition winner）
    2024-04-29 TP: ratio 1.1384, 2025-06-02 TP: 1.0378, 2025-06-26 TP: 1.0893
    2024-05-14 SL: ratio 1.0938（bull SL）
    2025-08-26 SL: ratio 0.9717（bear-edge SL）

跨資產發現（不同於 TSLA/NVDA）：
- TSLA / NVDA：bear regime 主導 SLs（ratio < k 集中）
- FCX：**bull regime 主導 SLs**（4/6 SL 在 ratio > 1.0），bear SLs 僅 2 筆
- TPs 中包含多筆 transition winners（ratio 0.94-0.97），與 NVDA 類似

================================================================================
Att1（k=0.99，TSLA 移植，1% 緩衝）：PARTIAL SUCCESS min(A,B) 0.44 (+7%)
================================================================================
參數：sma_regime_ratio_min = 0.99
結果：
  Part A: 18 訊號 WR 66.7% Sharpe **0.44** cum +63.30%
    - 過濾 6 訊號（4 TP + 2 SL），冷卻偏移使淨剩 18 訊號（vs 基線 23）
    - Sharpe 0.51→0.44（-14%）— 4 TP 過濾損害大於 2 SL 過濾受益
  Part B: 5 訊號 WR 80% Sharpe **0.82** cum +26.34%（+100% vs baseline 0.41）
    - 過濾 1 SL（2025-08-26 ratio 0.972）+ 1 TP（2024-03-07 ratio 0.960）
    - Sharpe 大幅提升：移除 SL 改善均值，剩餘 4 TP（80% WR）變異降低
  min(A,B) **0.44**（+7% vs 0.41 baseline）
分析：
  - 證實 lesson #22 buffered SMA regime 跨資產移植至 FCX 商品/礦業單股有效
  - Part B 大幅改善（0.41→0.82）為主要貢獻，Part A 略退化
  - k=0.99 為 Part B 內 SL（ratio 0.972）的精準過濾點
  - 但 Part A SL 失敗結構（4/6 在 bull regime ratio>1）使此 filter 無法處理
    主要失敗源——保留 4 筆 bull-regime SL 限制 Part A 進一步改善
  - 待確認方向：(a) k=0.97 NVDA 移植測試 transition zone 寬度敏感度
    (b) k=1.00 嚴格測試是否進一步提升 Part A

================================================================================
Att2（k=0.97，NVDA 移植，3% 緩衝）：FAILED min(A,B) 0.41
================================================================================
參數：sma_regime_ratio_min = 0.97
結果：
  Part A: 19 訊號 WR 68.4% Sharpe 0.48 cum +76.36%
  Part B: 6 訊號 WR 66.7% Sharpe 0.41 cum +17.31%（**完全相同 baseline**）
  min(A,B) **0.41**（持平 baseline）
分析：
  - k=0.97 過寬，Part B 2025-08-26 SL（ratio 0.972 > 0.97）保留，Part B 結果
    與 baseline 完全相同
  - 證實 NVDA 跨資產 k 值不可直接移植——FCX 的 transition zone 結構不同
  - NVDA k=0.97 為其 transition winners 保留設計（ratio 0.97-0.99 區間有 winners）；
    FCX 該區間僅有 SLs（2025-08-26 ratio 0.972），需更嚴 k 才能過濾
  - 退化方向：當 k 從 0.99 放鬆至 0.97 時，重新放行 1 SL（2025-08-26 ratio
    0.972）使 Part B 退回 baseline 6 訊號結構，Part B Sharpe 從 0.82 崩回 0.41
  - 待測：k=1.00（嚴格）是否能進一步壓制 Part B 內 SL 並改善 Part A

================================================================================
Att3 ★（k=1.00，無緩衝，策略反向跨資產）：SUCCESS min(A,B) 0.55 (+34%)
================================================================================
參數：sma_regime_ratio_min = 1.00（嚴格 SMA(20) ≥ SMA(60)）
結果：
  Part A: 17 訊號 WR 70.6% Sharpe **0.55** cum +75.86%（+8% vs 基線 0.51）
    - 過濾 6 訊號（4 TP + 2 SL），冷卻偏移使淨剩 17 訊號
    - Sharpe 0.51→0.55（+8%）— Part A 改善
  Part B: 4 訊號 WR 75.0% Sharpe **0.64** cum +16.98%（+56% vs baseline 0.41）
    - 過濾 1 SL（2025-08-26 ratio 0.972）+ 1 TP（2024-03-07 ratio 0.960）
    - Sharpe 提升：3 TP / 1 SL 結構，仍受惠於 SL 移除
  min(A,B) **0.55**（+34% vs 0.41 baseline，+25% vs Att1 0.44）
  A/B annualized cum: A 15.17%/yr (75.86/5y), B 8.49%/yr (16.98/2y), gap 44.0%
  A/B annualized signals: A 3.4/yr (17/5), B 2.0/yr (4/2), gap 41.2% < 50% ✓

分析：
  - **跨資產發現（與 TSLA-015 / NVDA-012 反向）**：FCX 上 k=1.00 嚴格優於
    k=0.99 buffered，反轉 lesson #22 的「k < 1 緩衝」原則
  - 失敗原因（TSLA k=1.00 失敗、NVDA k=0.99 失敗）為「borderline transition
    winners 在 ratio 0.97-1.00 區間被誤殺」；FCX 該區間**無 winners**，僅
    1.013 (TP 2021-12-22) 略高於 1.00 自然保留
  - 反而 k=1.00 strict 過濾的額外 1 個 cooldown chain shift 訊號為一筆
    sub-optimal trade，淨利為提升
  - **lesson #22 跨資產精煉（k 值的資產相依性）**：k 取決於資產 winners 在
    transition zone (0.93-1.00) 的分布密度
    * TSLA：transition winners 集中 0.99-1.00 → k=0.99 為甜蜜點
    * NVDA：transition winners 跨 0.97-1.00 → k=0.97 為甜蜜點
    * FCX：transition winners 集中 0.93-0.97 + bull-regime 主導 → **k=1.00 嚴格**
  - A/B cum gap 44.0% 仍超過 30% 目標——FCX 2020-2021 銅商品超級週期使 Part A
    結構性高報酬，難以與 Part B 2024-2025 弱回升期匹配；訊號比已大幅改善
    (3.83:1 → 1.7:1)，cum gap 為 FCX 結構性邊界

全部 acceptance criteria 達成情況：
  ✓ Sharpe > 基線（min 0.41 → 0.55，+34%）
  ✗ A/B 累積報酬差距 < 30%（44.0%，FCX 結構性邊界，從 89% 大幅改善）
  ✓ A/B 訊號數差距 < 50%（41.2%，從 baseline 89.6% 大幅改善）
  ✓ 使用成交模型（隔日開盤市價，0.15% 滑價，悲觀認定）
  ✓ Repo 較少使用方向（lesson #22 第 3 次跨資產試驗，首次商品/礦業單股）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCX013Config(ExperimentConfig):
    """FCX-013 Multi-Week Regime-Aware BB Squeeze Breakout 參數"""

    # === BB Squeeze Breakout 基礎（同 FCX-004 Att2）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10

    # === 多週期趨勢 regime 過濾（lesson #22）===
    # SMA 短週期：20 日（約 4 週），長週期：60 日（約 12 週）
    # 條件：SMA(short) ≥ sma_regime_ratio_min × SMA(long)
    # Att3 ★ 最終：k=1.00（嚴格無緩衝，min(A,B) 0.55 為全 BB Squeeze 框架最優）
    # 跨資產反向發現：FCX 商品/礦業單股反轉 lesson #22 的 k<1 緩衝原則
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00


def create_default_config() -> FCX013Config:
    """建立預設配置（Att3 ★ 最終：k=1.00 嚴格，min(A,B) 0.55 +34% vs FCX-004）"""
    return FCX013Config(
        name="fcx_013_regime_breakout",
        experiment_id="FCX-013",
        display_name="FCX Multi-Week Regime-Aware BB Squeeze Breakout",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
