"""
IWM BB 下軌 + 回檔上限混合進場配置 (IWM-012) — Att1 baseline

動機：IWM-011 Att2（min(A,B) Sharpe 0.52）為 IWM 全域最佳，使用 RSI(2)+2DD+
ClosePos+ATR 框架。本實驗測試 BB-lower hybrid mode（cross-asset port from
EWJ-003 / VGK-007 / EWZ-006 / EWT-008 / CIBR-008 / EEM-012 successful pattern）
是否在 IWM 1.5-2% vol（位於混合模式已驗證有效邊界 [1.12%, 1.75%] 中段）上有效。

**Repo 首次將 BB-lower hybrid mode 應用至小型股寬基 ETF**（前驗證集中於非美
寬基（VGK/EWJ）、EM 寬基（EEM）、單一國家 EM（EWZ/EWT）、美國板塊（CIBR））。

跨資產假設（待驗證）：
- BB-lower hybrid 在 IWM 1.5-2% vol 上應有效，因日波動正落在 EWJ/CIBR/EWT/EWZ
  證實有效的 [1.12%, 1.75%] 區間中段（CIBR 1.53% vol 已成功驗證 min 0.39）
- IWM 已驗證 ATR>1.10 過濾有效（IWM-011 Att2），是混合模式所需的核心品質
  過濾器之一

10日高點回檔上限門檻（IWM 1.5-2% vol）：
- -8% = ~5σ（可能過嚴，移除中度回檔贏家）
- -10% = ~6σ（預期甜蜜點，隔離 COVID/2022-bear/SVB-class 連續崩盤）
- -12% = ~7σ（對 1.5% vol 偏鬆，無法過濾 2022-bear 期假訊號）

跨資產校準參考：
- VGK 1.12% vol 用 -7%（6σ）
- CIBR 1.53% vol 用 -12%（7.8σ）
- EWZ 1.75% vol 用 -10%（5.7σ，使用 BB(20, 1.5σ)）
- EWT 1.41% vol 用 -8%（5.7σ）
- IWM 1.5-2% vol 推估 -10%（5-7σ）為合理起點

========================================================================
Att1（基線）：BB(20, 2.0) + 10d cap -10% + WR(10)≤-80 + ClosePos≥0.40
              + ATR(5)/ATR(20) > 1.10 + cd 8 + TP+4%/SL-4.25%/20d
========================================================================
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class IWM012Config(ExperimentConfig):
    """IWM-012 BB 下軌 + 回檔上限混合進場參數"""

    # BB 參數（同 CIBR-008/EWJ-003/VGK-007/EWT-008，1.75% 以下使用 2.0σ）
    bb_period: int = 20
    bb_std: float = 2.0

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
