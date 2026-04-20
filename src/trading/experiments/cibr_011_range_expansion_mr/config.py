"""
CIBR-011：單日 Range Expansion Climax 均值回歸配置
(CIBR Wide-Range Climax + Intraday Reversal Mean Reversion Config)

動機（Motivation）：
    IBIT-008 三次迭代均失敗（min(A,B) Sharpe 0.00 全部），確認 Range Expansion
    Climax MR 模式在高波動 24/7 連續加密 ETF（IBIT 3.17% vol）上訊號過稀疏。
    跨資產假設（cross_asset_lessons #9 IBIT-008 note）：
        "Range Expansion MR may work on traditional (non-24/7) US sector ETFs
        (CIBR/XBI) where overnight gaps are absent and single-bar TR expansion
        represents primary capitulation structure"

    本實驗為 **CIBR 第 11 個策略**，亦為 **repo 首次將 Range Expansion 主訊號
    試驗於傳統 US 板塊 ETF**（IBIT-008 為加密 ETF；TLT-006 將 range expansion
    僅作多條件之一輔助）。CIBR 1.53% 日波動的網路安全板塊 ETF 為合理候選：
        1. 傳統開盤交易（無 24/7 持續價格發現），TR 完整捕捉日內賣壓
        2. 事件驅動（CrowdStrike 事件、Cisco 財報、政府網路安全預算）
           常產生單日寬範圍下殺/反彈 K 棒
        3. CIBR-009/010 已驗證 Key Reversal Day（多條件 price-action）+ NR7
           （volatility contraction）失敗，但 NR7 為「窄範圍」設計，與
           Range Expansion「寬範圍」結構截然相反

    與現有 CIBR 實驗的結構差異：
        - CIBR-008（最佳）：BB(20,2.0) 下軌觸及 + 10日回檔上限 -12% +
          WR/ClosePos/ATR 五重過濾（統計自適應 + 崩盤隔離）
        - CIBR-009（失敗）：Key Reversal Day（多重 price-action 反轉確認）
        - CIBR-010（失敗）：NR7（最窄範圍 7日）— 與 NR7 互斥的相反邏輯
        - CIBR-011（本實驗）：單日 TR ≥ 2 × ATR(20)（最寬範圍爆發）
          + ClosePos 強反轉 + 10 日回檔深度過濾

    參數縮放（IBIT 3.17% vol → CIBR 1.53% vol，比率 ~0.48x）：
        - TR/ATR ratio：保留 ≥ 2.0（無關 vol，純結構性比例）
        - ClosePos：保留 ≥ 50%（無關 vol）
        - Pullback floor：IBIT -6% → CIBR -3%（5σ 保留比例）
        - Pullback cap：IBIT -20% → CIBR -10%（6.5σ）
        - WR(10) ≤ -70（保留，超賣門檻無關 vol）
        - 出場 TP/SL：採 CIBR-008 已驗證 +3.5%/-4.0%/18天/cd 8

策略方向：均值回歸（單日 Range Expansion climax + 強日內反轉確認）
    Strategy direction: Mean reversion via single-bar TR expansion climax +
    strong intraday reversal confirmation, applied to US sector ETF

成交模型：執行模型回測（隔日開盤市價進場、滑價 0.1%、悲觀認定）
    Execution model: ExecutionModelBacktester (next-open market entry,
    0.1% slippage, pessimistic SL execution)
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR011Config(ExperimentConfig):
    """CIBR-011 Range Expansion Climax 均值回歸參數"""

    # Range Expansion 主訊號（IBIT-008 結構性參數）
    atr_period: int = 20  # ATR 基準期
    tr_ratio_threshold: float = 2.0  # TR/ATR(20) ≥ 2.0（單日 climax）

    # 日內反轉確認（IBIT-008 已驗證 ClosePos ≥ 50% 強反轉門檻）
    close_pos_threshold: float = 0.50

    # 回檔深度過濾（CIBR 1.53% vol 縮放：-3%/5σ 為 floor，-10%/6.5σ 為 cap）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03  # 10 日回檔 ≤ -3%（≈2σ floor）
    pullback_upper: float = -0.10  # 10 日回檔 ≥ -10%（≈6.5σ cap，過濾崩盤）

    # Williams %R 超賣確認（IBIT-008 已驗證 ≤ -70）
    wr_period: int = 10
    wr_threshold: float = -70.0

    # 冷卻（CIBR-008 已驗證 8 天為甜蜜點）
    cooldown_days: int = 8


def create_default_config() -> CIBR011Config:
    return CIBR011Config(
        name="cibr_011_range_expansion_mr",
        experiment_id="CIBR-011",
        display_name="CIBR Range Expansion Climax Mean Reversion",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,  # +3.5%（CIBR-008 已驗證）
        stop_loss=-0.04,  # -4.0%（CIBR-008 已驗證）
        holding_days=18,
    )
