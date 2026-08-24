"""
INDA-008: BB Lower Band + Pullback Cap Hybrid Mean Reversion

動機：INDA-005 Att3（10日回檔 3-7% + WR+ClosePos+ATR+2日跌幅，TP+3.5%/SL-4%/15d）
min(A,B) Sharpe 0.23，Part A Sharpe 0.23 / Part B Sharpe 0.31，A/B 累計報酬差距
33% 相對。嘗試移植近期 BB 下軌 + 回檔上限混合進場成功模式，期望改善 INDA
在低波動非美新興市場 ETF 上的 Sharpe。

參考近期混合進場成功案例：
- EWJ-003 Att3 (1.15% vol): BB(20,1.5) + cap -7%, Part A Sharpe 0.55→0.60
- VGK-007 Att1 (1.12% vol): BB(20,2.0) + cap -7%, min(A,B) 0.45→0.53 (+18%)
- CIBR-008 Att2 (1.53% vol): BB(20,2.0) + cap -12%, min(A,B) 0.27→0.39 (+44%)
- EWZ-006 Att3 (1.75% vol): BB(20,1.5) + cap -10%, min(A,B) 0.34→0.69 (+103%)

INDA 日波動 0.97%，為目前混合進場模式已驗證成功資產中波動最低者（EWJ 1.15%
為最低驗證成功）。理論上統計自適應 BB 下軌應在 Part A 高波動時深、Part B 低
波動時淺，自動縮放與當期波動一致；搭配 -7% 回檔上限（~7.2σ）隔離極端崩盤。

三次迭代結果：

Att1 (default, 最佳失敗嘗試): BB(20,2.0) + cap -7% + WR + ClosePos + ATR>1.15
      + cd7 + TP+3.5%/SL-4.0%/15d（直接移植 VGK-007 Att1 架構）
      → Part A 0.26 (WR 71.4%, 7訊號, +5.71%)
        Part B 0.20 (WR 50.0%, 4訊號, +2.30%)
        min(A,B) 0.20（baseline INDA-005 Att3 為 0.23，-13%）失敗
      失敗分析：BB(20,2.0) 對 INDA 0.97% vol 過嚴（訊號 13/7 → 7/4，降約 45%），
      Part B 僅 4 訊號且 WR 50%，樣本稀釋品質，A/B 累計差距擴大至 60% 相對

Att2: BB(20,1.5) + cap -7% + 其餘同 Att1
      → Part A -0.04 (WR 55.6%, 9訊號, -1.87%)
        Part B 0.27 (WR 62.5%, 8訊號, +6.51%)
        min(A,B) -0.04（遠遜 baseline 0.23）嚴重失敗
      失敗分析：BB(20,1.5) 在 Part A 引入 2 個假訊號轉為連續停損，累計報酬翻負。
      同 EWJ-003 Att2 模式：BB 放寬在多波動 Part A 引入品質較差訊號。Part B
      改善（8 訊號 WR 62.5%）但 Part A 崩潰。

Att3: BB(20,1.8) + cap -6%（~6.2σ，收緊 cap）+ 其餘同 Att1
      → Part A -0.25 (WR 50.0%, 6訊號, -5.37%)
        Part B 0.15 (WR 57.1%, 7訊號, +2.91%)
        min(A,B) -0.25（遠遜 baseline）嚴重失敗
      失敗分析：中間 BB std 1.8 兩端均不如——Part A 品質仍稀釋（WR 50%），
      收緊 cap 至 -6% 反移除 1 個 Part A 淺反彈贏家。

**最終結論：BB 下軌 + 回檔上限混合進場模式不適用 INDA**
三次迭代均未勝過 INDA-005 Att3（min(A,B) 0.23）。根本原因：
1. INDA 0.97% vol 低於混合模式已驗證下邊界（EWJ 1.15% 為目前最低成功案例，
   VGK 1.12% 次之）。BB 帶寬在極低波動下對訊號品質極敏感：
   - BB 2.0σ：僅 1.94% 偏離，多數有效回檔不觸及（11/20 訊號合格）
   - BB 1.5σ：1.46% 偏離，納入淺技術超賣假訊號（Part A 轉負）
   - BB 1.8σ：中間無法兩全（兩端均品質稀釋）
2. INDA 的固定 3-7% 回檔框架（INDA-005）在 0.97% 波動下已精準鎖定深度區間，
   BB 自適應機制在極低波動下不比固定門檻優越
3. INDA-005 的 2日跌幅+ATR 已隱含急跌確認；BB 下軌僅提供統計異常訊號，
   在 INDA 慢磨特性下（受盧比/外資流驅動）與真正反轉機會關聯性低

**混合進場模式有效邊界更新：日波動 1.12% ≤ vol ≤ 1.75%**
- 下邊界：VGK 1.12% 成功，INDA 0.97% 失敗（首次失敗驗證下邊界）
- 上邊界：EWZ 1.75% 成功，XBI 2.0% 失敗（XBI-010 驗證）

**確認 INDA-005 Att3 為 INDA 全域最優**（8 次實驗、25 次嘗試）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDA008Config(ExperimentConfig):
    """INDA-008 BB 下軌+回檔上限混合進場參數（最佳失敗嘗試：Att1）"""

    # BB 參數
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離（10日高點回檔上限，過濾 COVID 等極端事件）
    pullback_lookback: int = 10
    pullback_cap: float = -0.07  # 回檔上限 7%（~7.2σ for 0.97% vol）

    # 品質過濾（同 INDA-005 驗證有效參數）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.15

    cooldown_days: int = 7


def create_default_config() -> INDA008Config:
    return INDA008Config(
        name="inda_008_bb_lower_pullback_cap",
        experiment_id="INDA-008",
        display_name="INDA BB Lower Band + Pullback Cap Hybrid MR",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.040,  # -4.0%
        holding_days=15,  # 同 INDA-005 Att3 甜蜜點
    )
