"""
DIA-018 ^VIX Implied-Vol BANDS (U-shape Regime) Gated MR 配置

策略方向（lesson #24 v5 BANDS 變體，cross-strategy port from XBI-017
U-shape regime hypothesis）：
  在 DIA-012 Att2（min(A,B)† 1.31）MR 框架上新增 ^VIX BANDS 閘門
  （保留 VIX <= vix_low OR VIX >= vix_high，排除中段 complacency-creep
  regime），測試 U-shape regime hypothesis 能否移除殘餘 SL 2022-01-18。

trade-level signal-day ^VIX LEVEL pre-analysis（DIA-012 12 Part A，依
VIX 由低至高排序）：

  16.0 TP / 17.9 TP / 18.2 TP / 20.1 EXP / **22.6 TP** / **22.8 SL** /
  **22.9 TP** / 25.7 TP / 27.8 TP / 29.9 TP / 32.7 TP / 40.1 TP
  （Part B：14.5 TP / 20.4 TP / 23.4 TP）

  **預期結構性失敗（決定性）**：殘餘 SL 2022-01-18（VIX=22.8）被贏家
  2022-12-16（VIX=22.6）與 2021-12-20（VIX=22.9）**夾在 0.3 點窗口內**。
  任何 BANDS 閘門（VIX<=low OR VIX>=high）排除 22.8 必同時排除 22.6/22.9
  兩個贏家——SL 落於贏家 VIX 分布正中央，**無 U-shape 結構**。完成
  lesson #24 family 於 DIA 之邊界刻畫：DIRECTION（DIA-015）與 BANDS
  （本實驗）皆結構性失效——所有 ^VIX 衍生 regime gate 對 DIA 低波動
  寬基指數 capitulation MR 無區分力（殘餘 SL 與 underlying IV regime
  無乾淨對齊；equity capitulation MR 與 VIX 內生綁定，lesson #14/#36）。

跨資產脈絡（lesson #24 family）：
- XBI-017 ✓（^VIX BANDS，生技板塊 ETF，U-shape regime 成立）
- DIA-015 ✗（^VIX DIRECTION，DIA 低波動寬基指數 MR，lesson #24 失敗）
- **DIA-018（本實驗）：^VIX BANDS，DIA 低波動寬基指數 MR，預期 lesson
  #24 v5 BANDS 變體首次失敗——與 DIA-015 共同完成 DIA 之 lesson #24
  邊界（DIRECTION + BANDS 皆失效）**

迭代計畫：
- Att1：vix_low=18.0, vix_high=30.0（XBI-017 風格 U-shape）
- Att2：vix_low=20.0, vix_high=25.0（窄帶，嘗試精準排除 22.8）
- Att3：vix_low=22.0, vix_high=23.0（極窄帶 ablation，揭示 22.6/22.9
  贏家必被連帶移除）

驗收目標（goal）：min(A,B) Sharpe > DIA-012 Att2 1.31†；A/B cum gap < 30%；
signal gap < 50%；必須使用成交模型（execution model）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class DIA018Config(ExperimentConfig):
    """DIA-018 ^VIX BANDS (U-shape Regime) Gated MR 參數"""

    # === MR 進場框架（完全沿用 DIA-012 Att2）===
    rsi_period: int = 2
    rsi_threshold: float = 10.0
    decline_lookback: int = 2
    decline_threshold: float = -0.015
    close_position_threshold: float = 0.4
    oneday_return_cap: float = -0.020
    threeday_return_cap: float = -0.07
    cooldown_days: int = 5

    # === DIA-018 核心新增：^VIX BANDS（U-shape regime）===
    vix_ticker: str = "^VIX"
    # 保留 signal-day VIX <= vix_low OR VIX >= vix_high（排除中段）
    # Att1 (18,30) / Att2 (20,25) / Att3 (22,23) ablation
    vix_low: float = 18.0
    vix_high: float = 30.0


def create_default_config() -> DIA018Config:
    return DIA018Config(
        name="dia_018_vix_bands_mr",
        experiment_id="DIA-018",
        display_name="DIA ^VIX BANDS (U-shape Regime) Gated MR",
        tickers=["DIA"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.035,
        holding_days=25,
    )
