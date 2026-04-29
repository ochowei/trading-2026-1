"""
NVDA-012: Multi-Week Regime-Aware BB Squeeze Breakout 配置
NVDA Multi-Week Regime-Aware BB Squeeze Breakout Configuration

策略方向：將 TSLA-015（lesson #22 buffered multi-week SMA regime）跨資產移植到
NVDA-004 BB Squeeze Breakout 之上。lesson #22 明列 NVDA-004 BB Squeeze
（2.5-3% 日波動）為候選驗證資產。

基礎（同 NVDA-004，當前最佳 min(A,B) 0.47）：
- BB(20, 2.0) + 60 日 25th 百分位擠壓 + Close > Upper BB + Close > SMA(50)
- 冷卻 10 天，TP+8%/SL-7%/20d，0.15% 滑價（高 vol 個股）

NVDA-012 新增 regime 過濾（lesson #22）：
- **多週期趨勢 regime**：SMA(20) ≥ 0.99 × SMA(60)（1% 緩衝避免邊界訊號被
  過濾後觸發 cooldown chain shift；TSLA-015 Att1→Att2 已驗證 1.00→0.99 為
  關鍵甜蜜點）
- **多週期波動 regime**：依 TSLA-015 Att3 ablation 證實對 BB Squeeze 框架
  冗餘（squeeze 條件已含「近期低波動」語意），預設不啟用以避免過度限制

預期效果：
- Part A 過濾 2021 late-bull bubble 與 2022 bear regime 假突破（SMA20<<SMA60）
- Part A 過濾 2023 summer chop 中段反彈（SMA20≈SMA60 但 < 0.99×SMA60）
- Part B（2024-2025 AI bull）SMA20 全面 > SMA60，不應被過濾
- 預期 Part A Sharpe 提升、Part B 大致不變（lesson #22 的成功模式）

================================================================================
基準：NVDA-004（已執行驗證，min(A,B) 0.47）
================================================================================
- Part A: 17 訊號, WR 64.7%, 累計 +70.09%, Sharpe 0.50
- Part B: 8 訊號, WR 75.0%, 累計 +25.36%, Sharpe 0.47
- min(A,B) 0.47, A/B cum gap 64%（>30% 目標），A/B 訊號比 2.13:1（>1.5:1 目標）

目標：Sharpe > 0.47，年化 A/B cum 差 < 30%，年化訊號比 < 1.5:1

================================================================================
Att1（baseline，k=0.99 直接移植 lesson #22）：FAILED min(A,B) 0.41
================================================================================
參數：SMA(20) ≥ 0.99 × SMA(60)
結果：Part A 16/75.0%/Sharpe 0.63 cum +83.17%（過濾 2022-07-20 SL，+26% Sharpe）
      Part B 6/66.7%/Sharpe 0.41 cum +17.31%（過濾 2025-05-13 winner +8.00%
      與 2025-12-23 -1.06% expiry，但淨損失贏家）/ min 0.41（vs 0.47 baseline）
失敗：2025-05-13 為 4 月 tariff selloff 後的 transition 訊號，SMA20/SMA60 比率
      落於 0.97-0.99 之間，k=0.99 嚴格過濾誤殺此 winner——與 TSLA-015 Att1 的
      2025-05-12 transition winner 失敗模式平行

================================================================================
Att2（k=0.97，3% 緩衝放寬以保留 transition winner）：SUCCESS min(A,B) 0.51
================================================================================
參數調整：sma_regime_ratio_min 0.99 → 0.97
結果：Part A 16/75.0%/Sharpe 0.63 cum +83.17%（與 Att1 完全相同，2022-07-20
      SL 仍被過濾——bear regime ratio << 0.97）
      Part B 7/71.4%/Sharpe 0.51 cum +24.86%（恢復 2025-05-14 +6.43% expiry，
      且 2025-12-23 -1.06% loser 仍被過濾）
      min 0.51（+9% vs 0.47 baseline）。年化 A/B cum 差 25.3% < 30% ✓
      年化訊號比 1.09:1 < 1.5:1 ✓

NVDA 與 TSLA 的 buffered SMA regime k 值差異（lesson #22 跨資產精煉）：
- TSLA k=0.99（1% 緩衝）：3.72% 日波動，SMA20/SMA60 變動劇烈，1% 即足
- NVDA k=0.97（3% 緩衝）：2.5-3% 日波動，AI 牛市 transition 訊號 SMA 比率
  常落於 0.97-0.99 區間，需更寬緩衝

================================================================================
Att3（k=0.98 敏感度邊界檢查）：FAILED min(A,B) 0.41
================================================================================
參數調整：sma_regime_ratio_min 0.97 → 0.98
結果：Part A 不變（16 訊號 Sharpe 0.63）
      Part B 6 訊號 Sharpe 0.41 cum +17.31%（2025-05-14 transition winner 又
      被過濾，與 Att1 完全相同）/ min 0.41（vs Att2 的 0.51）
結論：0.97-0.98 為 NVDA 上 transition winner 的關鍵分界，0.97 為精準甜蜜點
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class NVDA012Config(ExperimentConfig):
    """NVDA-012 Multi-Week Regime-Aware BB Squeeze Breakout 參數"""

    # === BB Squeeze Breakout 基礎（同 NVDA-004）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.25
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10

    # === 多週期趨勢 regime 過濾（lesson #22）===
    # SMA 短週期：20 日（約 4 週），長週期：60 日（約 12 週）
    # 條件：SMA(short) ≥ sma_regime_ratio_min × SMA(long)
    # ratio 1.00（嚴格）：TSLA-015 Att1 失敗（cooldown chain shift 引入 borderline SL）
    # ratio 0.99（1% 緩衝）：TSLA-015 Att2/Att3 成功甜蜜點
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 0.97

    # === 多週期波動 regime 過濾 ===
    # 預設停用（TSLA-015 Att3 ablation：BB Squeeze 已隱含「近期低波動」）
    # 可在 Att2/Att3 啟用測試是否提供 NVDA 額外選擇性
    atr_regime_short: int = 20
    atr_regime_long: int = 60
    vol_regime_max_ratio: float = 1.40
    use_vol_regime: bool = False


def create_default_config() -> NVDA012Config:
    """建立預設配置（Att1 baseline：buffered SMA regime k=0.99，vol regime 停用）"""
    return NVDA012Config(
        name="nvda_012_regime_breakout",
        experiment_id="NVDA-012",
        display_name="NVDA Multi-Week Regime-Aware BB Squeeze Breakout",
        tickers=["NVDA"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
