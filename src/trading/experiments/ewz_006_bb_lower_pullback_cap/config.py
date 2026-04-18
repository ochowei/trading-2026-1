"""
EWZ-006: BB Lower Band + Pullback Cap Hybrid Mean Reversion
(EWZ BB 下軌 + 回檔上限混合進場均值回歸)

延伸 EWJ-003 / VGK-007 / CIBR-008 的混合進場架構至 EWZ。
EWJ (1.15% vol)、VGK (1.12% vol)、CIBR (1.53% vol) 均驗證 BB 下軌 + 回檔上限
+ 三重品質過濾（WR + ClosePos + ATR）優於固定回檔門檻：
- VGK-007: min(A,B) 0.45 → 0.53（+18%）
- CIBR-008: min(A,B) 0.27 → 0.39（+44%）
- EWJ-003: Part A Sharpe 0.55 → 0.60（+9%）

EWZ 日波動 1.75% 較高，BB(20,2.0) 下軌作為自適應門檻：
- 低波動期淺門檻 → 捕捉更多有效訊號
- 高波動期深門檻 → 自動隔離極端崩盤
搭配 EWZ-002 驗證有效的 10% 回檔上限（5.7σ）作為崩盤隔離雙保險。

保留 EWZ-002 Att3 全部出場參數：TP +5% / SL -4% / 18 天（非對稱出場，盈虧比 1.25:1）。
保留 EWZ-002 驗證有效的三重過濾：WR(10) ≤ -80 + ClosePos ≥ 40% + ATR(5)/ATR(20) > 1.1。

注意：EWZ 為 EM 單一國家 ETF（巴西），但驅動因素為大宗商品價格而非政策（與 FXI 不同）。
lesson #52 排除「政策驅動單一 EM 國家 ETF（FXI）」，但商品驅動 EM 仍可嘗試。

Att1: BB(20, 2.0) 下軌 + 回檔上限 -10% + WR + ClosePos + ATR > 1.1 + TP+5%/SL-4%/18d
      → Part A 0.58 (7訊號, WR 71.4%, 累計 +17.38%)
        Part B 1.11 (3訊號, WR 66.7%, 累計 +9.32%)
        min(A,B) 0.58（+71% vs EWZ-002 Att3 的 0.34）
      → 訊號頻率：1.4/yr vs 1.5/yr（年化平衡），但累計差 46.4%（>30%）
        Part B 樣本過少，需要放寬進場捕捉更多訊號

Att2: BB(20, 1.75) 較寬下軌（增加訊號）+ 其他同 Att1
      → Part A 0.69 (8訊號, WR 75.0%, 累計 +23.25%)
        Part B 1.40 (4訊號, WR 75.0%, 累計 +14.79%)
        min(A,B) 0.69（+103% vs EWZ-002 Att3 的 0.34）
      → A/B 累計差降至 36.4%（仍>30%），訊號頻率 1.6 vs 2.0/yr（1.25:1）
        Part B 仍偏少，再放寬 BB 至 1.5σ（同 EWJ-003 Att3 winning 組合）

Att3 (default ★): BB(20, 1.5) 更寬下軌（同 EWJ-003 Att3 winning 組合）
      → Part A 0.69 (12訊號 2.4/yr, WR 75.0%, 累計 +36.82%)
        Part B 1.82 (6訊號 3.0/yr, WR 83.3%, 累計 +25.52%)
        min(A,B) 0.69（+103% vs EWZ-002 Att3 的 0.34）★
      → A/B 年化訊號比 1.25:1（優秀），A/B 累計差 30.7%
        Part B 資料大幅增加（4→6 訊號），WR 75%→83.3% 顯著提升
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWZ006Config(ExperimentConfig):
    """EWZ-006 BB 下軌 + 回檔上限混合進場參數"""

    # BB 參數（自適應進場門檻）
    bb_period: int = 20
    bb_std: float = 1.5

    # 崩盤隔離（10日高點回檔上限，過濾極端崩盤）
    pullback_lookback: int = 10
    pullback_cap: float = -0.10  # 回檔上限 10%（5.7σ for 1.75% vol）

    # 品質過濾（同 EWZ-002 驗證有效參數）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.40
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.10

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> EWZ006Config:
    return EWZ006Config(
        name="ewz_006_bb_lower_pullback_cap",
        experiment_id="EWZ-006",
        display_name="EWZ BB Lower + Pullback Cap Hybrid MR",
        tickers=["EWZ"],
        data_start="2010-01-01",
        profit_target=0.050,  # +5.0%（非對稱出場，EWZ-002 驗證甜蜜點）
        stop_loss=-0.040,  # -4.0%
        holding_days=18,
    )
