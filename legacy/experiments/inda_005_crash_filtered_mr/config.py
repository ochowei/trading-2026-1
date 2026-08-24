"""
INDA-005: 2-Day Crash Filtered Mean Reversion
(INDA 2日急跌過濾均值回歸)

基於 INDA-002 Att1 框架，新增 2日急跌過濾：
- 參考 EWT-006 Att2 成功案例（同 min 0.15 起點，加 2日急跌後 min→0.28，+87%）
- INDA-004 測試 2日急跌作為「替代」回檔（失敗），本實驗測試作為「補充」
- 2日跌幅門檻按波動度比例縮放：EWT(1.41%) -1.5% → INDA(0.97%) -1.0%
- 出場維持 INDA-002 最佳: TP+3.5%/SL-4.0%/18d（微縮持倉減少時間曝露）

Att1: 2日跌幅 ≤ -1.0% + TP +3.5% / SL -4.0% / 18d
  → Part A 0.26 (WR 61.5%, 13訊號), Part B 0.22 (WR 57.1%, 7訊號)
  → min(A,B) 0.22（vs INDA-002 的 0.15，+47%）
  → A/B 累計差距 6.61pp（11.27% vs 4.66%），Part B 2筆到期拖累

Att2: 2日跌幅 ≤ -1.5%（更嚴格）+ TP +3.5% / SL -4.0% / 18d
  → 結果與 Att1 完全相同（-1.5% 非綁定：所有 Part A/B 訊號天然滿足）
  → 驗證：2日急跌在 INDA 上不提供額外過濾力（ATR>1.15 已隱含近期急跌）

Att3★: 2日跌幅 ≤ -1.0% + TP +3.5% / SL -4.0% / 15d（進一步縮短持倉）
  → Part A 0.23 (WR 69.2%, 13訊號), Part B 0.31 (WR 57.1%, 7訊號)
  → min(A,B) 0.23（vs INDA-002 的 0.15，+53%）★ 最佳
  → A/B 累計差距 3.22pp（9.68% vs 6.46%），大幅優於 Att1 的 6.61pp
  → 關鍵改善：15d 持倉將 Part B 兩筆到期虧損從 -3.18%/-1.77% 縮減至 -2.63%/-0.42%
  → 代價：Part A 1 筆 TP 交易（需 18d 達標）轉為到期 +1.76%
  → 發現：2日急跌過濾在 INDA 上非綁定（ATR>1.15 已隱含），真正改善來自持倉縮短
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDA005Config(ExperimentConfig):
    """INDA-005 2日急跌過濾均值回歸參數"""

    # 進場 — 回檔
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 回檔 >= 3%
    pullback_cap: float = -0.07  # 回檔 <= 7%（隔離極端崩盤）

    # 進場 — Williams %R
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 進場 — 收盤位置過濾
    close_position_threshold: float = 0.4

    # 進場 — 波動率自適應過濾
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # 進場 — 2日急跌過濾（新增）
    drop_2d_threshold: float = -0.01  # 2日報酬 <= -1.0%

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> INDA005Config:
    return INDA005Config(
        name="inda_005_crash_filtered_mr",
        experiment_id="INDA-005",
        display_name="INDA 2-Day Crash Filtered Mean Reversion",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.04,  # -4.0%
        holding_days=15,  # Att3：進一步縮短持倉，減少到期虧損曝露
    )
