"""
XLU ^TNX Realized-Rate-Momentum DIRECTION Regime-Gated MR (XLU-014)

實驗動機（PREDICTED documented-failure / predict→confirm）：
- XLU-013 Att2/Att3 為當前全域最優（min(A,B) **1.59**，Part A Sharpe 6.74 /
  Part B Sharpe 1.59 binding），框架 = XLU-012 Att3 + ^MOVE 3d change <= +5.0
  forward-looking implied-vol DIRECTION filter（^MOVE LEVEL cap 已證冗餘）。
- 強制 predict→confirm 預分析（先做）已用執行模型重現 XLU-013 Att2/Att3 全
  6+4 筆交易，**Part B（binding）結構為**：
    * 2024-06-14 → +3.00% TP
    * 2024-11-06 → +3.00% TP
    * 2025-03-05 → +3.00% TP
    * 2024-01-18 → **−0.20% 近乎持平 time-EXPIRY（唯一殘餘 "loser"，非停損）**
  即「3 筆 winners 全為相同 +3.00% TP + 單筆極溫和 time-expiry」——**TLT-014
  Att3 精確 isomorph**（TLT-014 Att3 殘餘 = 單筆 −2.38% mild time-expiry +
  Part B 全 +3.50% 同一 TP，結構性 NON-IMPROVABLE）。

zero-variance trap（第 4 次確認，繼 TLT-014 Att3 / XLU-013 / XBI-017）：
- 任何正交 regime gate 若「外科式」移除 2024-01-18 → Part B 僅存 3 筆相同
  +3.00% TP → **報酬標準差 = 0 → Sharpe 退化（degenerate zero-var，非真實
  改善，沿用 † 慣例 / VOO-005 Att1 / EWZ-010 Att2 / XLU-012 Att1/Att2 判例）**。
- 任何「非外科式」gate（閾值未精準命中單點）必同殺 3 筆相同-TP winners 之一
  → Part B 3→2 崩潰 catastrophic。
- 殘餘 binding 為 −0.20% 近乎持平 time-expiry（比 TLT-014 Att3 −2.38% 更
  溫和），**無任何 regime-failure signature 可供 gating**——它只是慢速均值
  回歸在 20 日到期前未達 +3.00%，benign 而非 regime 失敗。
- 逐維度 separability（LOSER 2024-01-18 vs 3 筆 +3.00% TP winners）：^MOVE
  level/3d/5d、^VIX level/3d、^TNX level/5d/20d、XLU 20d、SPY 20d、RV20
  **全部交錯（interleaved）**；僅 3 個 post-hoc 單點 notch（^TNX 3d
  +4.91 vs winner-max +1.49 gap 3.42pp / XLU 5d −5.27 vs −2.89 gap 2.38pp /
  ^TNX level 4.14 vs 4.21 gap 0.07pp knife-edge）**皆無 ≥15pp robust
  plateau**（lesson #6 反例 / EEM-016 / INDA-013 過擬合標準）。

跨資產背景（lesson #24 family DIRECTION 變體 + 禁忌 #36f / #37 邊界）：
- XLU-013 已驗證 ^MOVE（forward-looking 隱含 bond vol）3d DIRECTION 為 XLU
  唯一有效隱含波動率維度。本實驗測試 **^TNX（10y yield，realized rate
  momentum）3d DIRECTION** 與 **XLU 自身 5d capitulation-depth** 兩個正交維
  度能否進一步隔離殘餘 Part B time-expiry。
- ex-ante 機制（為何預測失敗）：(1) XLU 透過 yield-spread + flight-to-
  defensive **間接** 受利率影響（禁忌 #37：跨資產利率指標過濾 XLU 因響應速度/
  方式不同而失敗，XLU-006 Att3 TLT 60d ROC 已驗證），realized rate momentum
  對 XLU MR 訊號品質無 driver-pure 區分力；(2) 殘餘為 benign time-expiry
  非 rate-shock SL，與 rate regime 結構性解耦；(3) zero-variance trap 使任
  何成功隔離皆退化。

設計（沿用 XLU-013 Att2/Att3 全域最優框架，僅疊加 1 個正交 gate）：
- Att1：^TNX 3d % change CEILING <= +3.0%（surgical 假設，預測移除 2024-01-18
  → Part B zero-var degenerate REJECT）
- Att2：^TNX 3d % change CEILING 收緊 <= +1.0%（強制結構測試：同殺 winner
  2024-11-06 TNX3d +1.49 > +1.0 → Part B 3→2 崩潰 catastrophic）
- Att3：XLU 自身 5d return FLOOR >= -4.0%（正交 capitulation-depth ablation，
  ^TNX gate 停用；2024-01-18 XLU5d -5.27 最深 → 同樣 zero-var degenerate，
  確認跨「realized rate momentum」與「own-asset depth」雙維度皆不可分）

predict→confirm 軌跡：3 SUCCESS（GLD-016/VOO-005/URA-014）+ 15 documented-
failure 全部命中（XBI-018 為第 15）。XLU-014 預測為第 16 個 documented-
failure，**4th confirmation of the zero-variance-trap family**，確認 XLU-013
Att2/Att3 結構性 NON-IMPROVABLE（與 XBI-018 確認 XBI-017 / TLT-014 Att3 平行）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XLU014Config(ExperimentConfig):
    """XLU-014 ^TNX Realized-Rate-Momentum DIRECTION Regime-Gated MR 參數"""

    # 進場 — 回檔（同 XLU-011 / XLU-012 / XLU-013）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.035
    pullback_cap: float = -0.07

    # 進場 — Williams %R（同 XLU-011 / XLU-012 / XLU-013）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 進場 — 收盤位置過濾（同 XLU-011 / XLU-012 / XLU-013）
    close_position_threshold: float = 0.4

    # 進場 — ATR 自適應過濾（同 XLU-011 / XLU-012 / XLU-013）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # ^MOVE forward-looking implied vol gate（沿用 XLU-013 Att2/Att3 全域最優；
    # LEVEL cap 已證冗餘故停用 = 999.0，DIRECTION 3d <= +5.0 為唯一 binding）
    move_ticker: str = "^MOVE"
    max_move_level: float = 999.0
    use_move_direction_filter: bool = True
    move_direction_lookback: int = 3
    max_move_change: float = 5.0

    # ^TNX 10y yield realized-rate-momentum DIRECTION gate（XLU-014 核心新增）
    # tnx N 日 % 變化 <= max_tnx_change（CEILING，過濾「rate 急升」訊號日）
    tnx_ticker: str = "^TNX"
    # 預設 = Att1（headline surgical 嘗試，^TNX 3d % change CEILING <= +3.0%）；
    # Att2 = max_tnx_change=1.0；Att3 = use_tnx_direction_filter=False +
    # use_xlu_depth_filter=True（正交 capitulation-depth ablation）
    use_tnx_direction_filter: bool = True
    tnx_direction_lookback: int = 3
    max_tnx_change: float = 3.0  # 百分比（pct change × 100）

    # XLU 自身 N 日報酬 capitulation-depth FLOOR（Att3 正交 ablation 用）
    # XLU N 日報酬 >= min_xlu_return（FLOOR，過濾「過深下跌」訊號日）
    use_xlu_depth_filter: bool = False
    xlu_depth_lookback: int = 5
    min_xlu_return: float = -0.04

    # 冷卻期（同 XLU-011 / XLU-012 / XLU-013）
    cooldown_days: int = 7


def create_default_config() -> XLU014Config:
    return XLU014Config(
        name="xlu_014_tnx_rate_direction_mr",
        experiment_id="XLU-014",
        display_name="XLU ^TNX Realized-Rate-Momentum DIRECTION Regime-Gated MR",
        tickers=["XLU"],
        data_start="2010-01-01",
        # 沿用 XLU-013 Att2/Att3 出場（TP+3.0%/SL-4.0%/20d）
        profit_target=0.030,
        stop_loss=-0.040,
        holding_days=20,
    )
