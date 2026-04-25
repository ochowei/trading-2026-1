"""
IWM BB 下軌 + 回檔上限混合進場配置 (IWM-012) — Att2

動機：IWM-011 Att2（min(A,B) Sharpe 0.52）為 IWM 全域最佳，使用 RSI(2)+2DD+
ClosePos+ATR 框架。本實驗測試 BB-lower hybrid mode（cross-asset port from
EWJ-003 / VGK-007 / EWZ-006 / EWT-008 / CIBR-008 / EEM-012 successful pattern）
是否在 IWM 1.5-2% vol（位於混合模式已驗證有效邊界 [1.12%, 1.75%] 中段）上有效。

**Repo 首次將 BB-lower hybrid mode 應用至小型股寬基 ETF**。

========================================================================
迭代記錄（2026-04-25，成交模型 0.1% slippage，隔日開盤市價進場）：
========================================================================

Att1（失敗）：BB(20, 2.0) + 10d cap -10% + WR≤-80 + ClosePos≥0.40 + ATR>1.10
  Part A 7/57.1%/Sharpe **0.23** cum +5.55%
  Part B 3/66.7%/Sharpe 0.31 cum +3.46%
  min(A,B) **0.23**（-56% vs IWM-011 的 0.52）
  失敗：BB(20, 2.0) 訊號集與 IWM-011 RSI(2) 框架互補但不重疊；缺失 5 個
  IWM-011 winners（淺超賣急跌反轉訊號未達 BB 下軌深度），新增 2 winners
  但 SL 全部保留，淨效應為移除過多贏家。

Att2（當前）：放寬 BB 至 1.5σ（參考 EWZ-006 1.75% vol 配置）
  目的：測試是否較鬆 BB 帶寬可捕捉更多 IWM-011 winners 同時保持 SL 過濾
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM012Config(ExperimentConfig):
    """IWM-012 BB 下軌 + 回檔上限混合進場參數"""

    # BB 參數（Att2 改用 1.5σ，參考 EWZ-006 1.75% vol 的成功配置）
    # Att1 BB(20, 2.0) + cap -10% → min 0.23 FAIL（捕捉訊號不足）
    # Att2 BB(20, 1.5) + cap -10% → 放寬 BB 至 1.5σ 增加訊號流量
    bb_period: int = 20
    bb_std: float = 1.5

    # 崩盤隔離（10日高點回檔上限）
    pullback_lookback: int = 10
    pullback_cap: float = -0.10  # 回檔上限 10%（~5-7σ for 1.5-2% vol）

    # 品質過濾（同 IWM-011 已驗證有效參數）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.10  # IWM-011 Att2 驗證甜蜜點

    cooldown_days: int = 8


def create_default_config() -> IWM012Config:
    return IWM012Config(
        name="iwm_012_bb_lower_pullback_cap",
        experiment_id="IWM-012",
        display_name="IWM BB Lower Band + Pullback Cap Hybrid",
        tickers=["IWM"],
        data_start="2010-01-01",
        profit_target=0.04,  # +4.0%（同 IWM-011）
        stop_loss=-0.0425,  # -4.25%（同 IWM-011 甜蜜點）
        holding_days=20,
    )
