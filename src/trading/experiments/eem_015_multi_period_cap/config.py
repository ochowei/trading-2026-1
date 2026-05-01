"""
EEM Multi-Period Capitulation-Strength Filter MR (EEM-015 Att1)

策略方向：將 INDA-011 Att3 全域最優發現「2DD floor + 3DD cap」雙維度組合
跨資產移植至 broad EM ETF（EEM, 1.17% vol）。INDA-011 Att3 為 repo 首次
「3DD cap」作為主要 capitulation-strength 過濾器，INDA 0.97% vol 上 +83%
（min 0.30→0.55）。

INDA-011 跨資產假設明確列舉 EEM 為候選對象：
  「2DD floor + 3DD cap」雙重門檻可能適用其他 single-country EM 或 broad EM ETF
  （EEM/EWZ/EWT/INDA），其失敗模式為「multi-day acceleration / sustained drift」
  而非「single-day flush」。

EEM-014 Att2（基線 min 0.56）已使用 2DD floor <= -0.5%。本實驗在其上疊加 3DD cap，
測試是否進一步精煉訊號集。

EEM-014 Att2 Part A 5 訊號 / Part B 4 訊號分析：
- Part A SLs（1）：2025-XX 中美貿易摩擦 → 3DD 結構待分析
- Part B SLs（1）：2025-11-19 → 慢漂移，3DD 多日疲弱
- TPs：多為深 2DD 急跌反彈（1-2 日 capitulation 後快速反彈），3DD 應較淺

Hypothesis：EEM 失敗 SL 結構可能為「持續多日漂移」（3DD 深），TPs 為
「單日/雙日急跌+快速反轉」（3DD 較淺），3DD cap 可選擇性過濾「累積疲弱」訊號。

================================================================================
3 次迭代計畫（成交模型 0.1% slippage，隔日開盤市價進場）：
================================================================================

Att1（直接移植 INDA-011 Att3 參數，3DD cap >= -3.0%）
  - INDA-011 Att3 之 3DD cap = -3.0% 為 INDA 0.97% vol 上 ~3.1σ
  - 等比 EEM 1.17% vol 應對應 ~3.6%，但先測試 -3.0%（保守起點 ~2.6σ）

Att2（如 Att1 過嚴：放寬至 -3.5% ~ -4.0%）
  - 預期 Att1 可能將 EEM TPs（2DD -3.36%, -3.10%, -3.88%）誤過濾，因這些訊號
    若搭配前一日明顯下跌則 3DD 可能 ≤ -3.0%

Att3（如 Att2 仍未達標：等比縮放至 EEM vol，3DD cap >= -3.5%）
  - 即「EEM 1.17% vol / INDA 0.97% vol = 1.21x」縮放係數應用
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM015Config(ExperimentConfig):
    """EEM-015 Multi-Period Capitulation-Strength Filter MR 參數"""

    # BB 參數（同 EEM-014）
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離（同 EEM-014）
    pullback_lookback: int = 10
    pullback_cap: float = -0.07

    # 品質過濾（同 EEM-014）
    wr_period: int = 10
    wr_threshold: float = -85.0
    close_position_threshold: float = 0.40

    # ATR 當日過濾（同 EEM-014）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.10

    # 2 日急跌 floor（同 EEM-014 Att2）
    twoday_return_floor: float = -0.005  # 2DD <= -0.5%

    # 新增：3 日急跌 cap（INDA-011 Att3 方向，移植測試）
    # Att1：-3.0%（直接移植 INDA-011）— FAILED Part A 2/0.00 / Part B 2/-0.02 過嚴
    # Att2：-4.0%（vol-scaled 放寬）— FAILED Part A 0.56 / Part B 0.34 仍移除 TPs
    # Att3：-5.0%（極寬 ~4.3σ）— TIE 基線 non-binding，filter 無對象可過濾
    # 最終配置採用 Att3，三次迭代均未勝過 EEM-014 Att2（min 0.56）
    threeday_return_cap: float = -0.050

    # 冷卻期（同 EEM-014）
    cooldown_days: int = 10


def create_default_config() -> EEM015Config:
    return EEM015Config(
        name="eem_015_multi_period_cap",
        experiment_id="EEM-015",
        display_name="EEM Multi-Period Capitulation-Strength Filter MR",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.030,
        holding_days=20,
    )
