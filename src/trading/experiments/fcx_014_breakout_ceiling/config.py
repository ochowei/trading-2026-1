"""
FCX-014: Signal-Day Direction Filter on Multi-Week Regime BB Squeeze Breakout
FCX Multi-Period Direction-Filter Regime Breakout Configuration

策略方向：將 lesson #19 family 的「signal-day return CEILING / FLOOR」維度
首次跨框架移植至 BB Squeeze Breakout 框架，疊加於 FCX-013 Att3（當前 BB
Squeeze 全域最優 min(A,B) 0.55）之上。

**Repo 首次 lesson #19 family 應用於 BB Squeeze Breakout 框架**：
- 既往 lesson #19 family floor / cap 維度成功應用於 MR 框架（DIA-012、SPY-009、
  EWT-009、IWM-013、GLD-014、INDA-011、SIVR-018、URA-013、VGK-008、IBIT-009、
  EEM-014 等）
- TSM-011 Att3 首次將 ceiling 維度應用於 RS Momentum 框架（5d ceiling +10.5%
  rally exhaustion filter，min(A,B) +5%）
- FCX-014 為 lesson #19 第三類框架（BB Squeeze Breakout）首次跨策略移植
- 鏡像對齊：MR 失敗模式（太淺 capitulation，需 floor）vs RS 失敗模式（太深
  rally，需 ceiling）vs Breakout 失敗模式（rally 已耗盡，需 ceiling）

================================================================================
基準：FCX-013 Att3（已執行驗證，min(A,B) 0.55，當前 BB Squeeze 框架全域最優）
================================================================================
- Part A: 17 訊號 / WR 70.6% / Sharpe 0.55 / cum +75.86%（11 TP / 4 SL / 2 EX）
- Part B: 4 訊號 / WR 75.0% / Sharpe 0.64 / cum +16.98%（3 TP / 1 SL）
- min(A,B) **0.55**，A/B cum gap 44.0%（>30% 目標 ❌，結構性）
- A/B 訊號比 1.7:1（gap 41.2% < 50% ✓）

trade-level signal-day 分析（1d / 3d / 5d return %）：
  Part A SLs（4）:
    2019-07-24 SL: 1d 2.49 / 3d 3.92 / 5d 7.96  (low conviction breakout)
    2020-01-13 SL: 1d 4.88 / 3d 2.66 / 5d 5.29  (modest extension)
    2021-04-15 SL: 1d 4.19 / 3d 12.61 / 5d 10.31  ★ **extended rally exhaustion**
    2021-11-11 SL: 1d 9.01 / 3d 3.73 / 5d 10.54  (single-day spike)
  Part A bad EX:
    2023-07-13 EX -3.69%: 1d 3.72 / 3d 8.35 / 5d 11.41
  Part A TPs (12)：1d 2.45-10.87, 3d 2.73-11.50, 5d 5.04-18.16
  Part B (4):
    2024-04-29 TP: 1d 3.78 / 3d 8.64 / 5d 7.07
    2024-05-14 SL: 1d 2.77 / 3d 4.70 / 5d 4.07  (weak breakout, NOT extended)
    2025-06-02 TP: 1d 4.34 / 3d 3.24 / 5d 2.90
    2025-06-26 TP: 1d 6.85 / 3d 8.60 / 5d 7.97

關鍵 trade-level 觀察：
  3d return ceiling 12.0% 為 surgical filter——僅過濾 2021-04-15 SL（3d 12.61%
  唯一超出 12% 的訊號），所有 TPs（max 11.50% 為 2023-01-06 TP，恰於 12% 邊
  界內）和 Part B 訊號（max 8.64%）完全保留。

  5d ceiling 在 FCX 上 NOT applicable：2020-07-06 TP 5d 18.16% 與 2019-11-07
  TP 5d 14.77% 兩筆深度 stretched winners 會被誤殺，淨效果負面。

  1d ceiling 在 FCX 上 NOT applicable：2020-07-06 TP 1d 10.87% > 2021-11-11
  SL 1d 9.01%，無單向選擇力。

  Part B 唯一 SL（2024-05-14）為「weak breakout」失敗模式（與 Part A SL 反向），
  無法被 ceiling filter 改善，需要 floor filter 但 floor 將同時誤殺 Part B
  TPs（2025-06-02 1d 4.34% 為 Part B 最弱 winner）。Part B SL 屬 FCX 結構性
  邊界，本實驗主要針對 Part A 4 SLs 中可被 ceiling 識別的 1 筆。

================================================================================
Att1（3d return ceiling = 12.0%，Rally Exhaustion Filter）
================================================================================
參數：max_signal_day_3d_return = 0.12 （要求 signal day 3 日報酬 <= +12.0%）

預測：
  - 過濾 2021-04-15 SL（3d 12.61% 唯一超出）
  - 所有 TPs 保留（max 11.50% 在 2023-01-06，恰於邊界內）
  - 所有 Part B 訊號保留（max 8.64% 遠低於 12.0%）
  - 可能觸發 cooldown chain shift（lesson #19 family 副作用）

預期 Part A：17→16 訊號（過濾 1 SL）+ 可能 0-1 cooldown chain shift 訊號
預期 Sharpe：0.55 → ~0.65-0.75（移除 1 SL 提升均值且降低變異）

================================================================================
Att2（待依 Att1 結果決定）
================================================================================
候選方向：
  (a) 3d ceiling 11.0%（更嚴）— 但會誤殺 2023-01-06 TP（3d 11.50% > 11.0%）
      預期 SL 過濾 1 + TP 過濾 1，淨 +7.14% - 8% < 0，預期失敗
  (b) 3d ceiling 12.5%（更寬，僅微小於 SL 12.61%）— 仍只過濾 2021-04-15 SL，
      與 Att1 訊號集相同，無新資訊
  (c) 5d ceiling 13.0% 取代 3d ceiling — 過濾 2 TPs（19-11-07/20-07-06），失敗
  (d) 加 1d ceiling 9.0% 組合 — 過濾 2021-11-11 SL + 2020-07-06 TP，淨 -0.86%
  (e) 加 1d floor 3.0% 組合 — 過濾 1 Part B SL（2024-05-14 1d=2.77）+ 2 Part A
      TPs（2020-11-03 1d=2.91、2021-12-22 1d=2.45）
  (f) 3d ceiling 12.0% + 5d ceiling sweet spot 對 SL 5d 分布定位

Att2 將測試 (b) 3d ceiling 12.5% 確認甜蜜點邊界寬度（threshold robustness check）。

================================================================================
Att3（待依 Att1/Att2 結果決定）
================================================================================
候選方向：
  - ablation：移除 Att1 的 ceiling，加上 different orthogonal filter
  - threshold sweep extreme：3d ceiling 11.5%（恰高於 2023-01-06 TP 11.50%）
  - 測試 stricter SMA regime（k=1.02）併用 Att1 ceiling

================================================================================
參考成功案例
================================================================================
TSM-011 Att3（5d ceiling +10.5% rally exhaustion，RS Momentum 框架）：
  - 過濾 2020-07-24 訊號（5d +11.30%，原 expiry -1.72%）
  - cooldown chain shift 引入 2020-07-31 expiry +0.89%（從負轉正）
  - 同框架 11 次實驗、33+ 次嘗試後首次突破 0.79 結構性上限
  - min(A,B) 0.79 → 0.83（+5%）

DIA-012 Att2（1d cap >= -2% AND 3d cap >= -7%，MR 框架）：
  - 雙維度過濾使 Sharpe 0.47 → 1.31（+178%）

FCX-014 預期延續 lesson #19 ceiling 維度成功軌跡，但因 FCX 為 high-vol
mining single stock 商品超級週期驅動，效果可能受限於 SL 失敗模式異質性。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCX014Config(ExperimentConfig):
    """FCX-014 Multi-Period Direction-Filter Regime Breakout 參數"""

    # === BB Squeeze Breakout 基礎（同 FCX-013）===
    bb_period: int = 20
    bb_std: float = 2.0
    bb_squeeze_percentile_window: int = 60
    bb_squeeze_percentile: float = 0.30
    bb_squeeze_recent_days: int = 5
    sma_trend_period: int = 50
    cooldown_days: int = 10

    # === 多週期趨勢 regime 過濾（lesson #22，同 FCX-013 Att3）===
    sma_regime_short: int = 20
    sma_regime_long: int = 60
    sma_regime_ratio_min: float = 1.00

    # === 訊號日方向過濾（lesson #19 family，本實驗新增）===
    # 3 日累計報酬上限：要求 signal_day_3d_return <= max_signal_day_3d_return
    # Att1 ★ 0.12（12.0%，rally exhaustion threshold；min(A,B) 0.64 +16%，全域最優）
    # Att2: 0.11（11.0%，邊界測試；cooldown chain shift 2023-01-06→01-09 同 TP，
    #              訊號集與 cum 完全相同 0.64 確認 11-12% 為 robust sweet spot 區間）
    # Att3: 0.09（9.0%，下邊界測試；預期 cum 大幅下降，確認下邊界）
    # 設為 None 表示不啟用此過濾
    max_signal_day_3d_return: float | None = 0.09

    # 1 日報酬上限：要求 signal_day_1d_return <= max_signal_day_1d_return
    # 中間嘗試（已棄用）：Att3-mid（3d 0.12 + 1d 0.08）— cooldown chain shift
    # 使 2020-07-06 → 07-07、2021-11-11 → 11-12 訊號日期偏移 1 日但出場類型完全
    # 不變，1d ceiling 在 3d ceiling 已啟用時 redundant
    # 設為 None 表示不啟用此過濾
    max_signal_day_1d_return: float | None = None


def create_default_config() -> FCX014Config:
    """建立預設配置（Att1：3d ceiling 12.0%）"""
    return FCX014Config(
        name="fcx_014_breakout_ceiling",
        experiment_id="FCX-014",
        display_name="FCX Multi-Period Direction-Filter Regime Breakout",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=20,
    )
