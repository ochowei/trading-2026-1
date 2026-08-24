"""
EEM-012: BB Lower Band + Pullback Cap Hybrid Mean Reversion
(EEM BB 下軌 + 回檔上限混合進場均值回歸)

延伸 EWJ-003 / VGK-007 / CIBR-008 / EWZ-006 / EWT-008 的混合進場架構至 EEM。
混合進場在波動區間 [1.12%, 1.75%] 一致勝過固定回檔門檻：
- EWJ (1.15%)：Part A 0.55 → 0.60（+9%）
- VGK (1.12%)：min(A,B) 0.45 → 0.53（+18%）
- CIBR (1.53%)：min(A,B) 0.27 → 0.39（+44%）
- EWZ (1.75%)：min(A,B) 0.34 → 0.69（+103%）
- EWT (1.41%)：min(A,B) 0.42 → 0.57（+36%）

EEM 日波動 1.17% 位於有效區間，且為 broad EM ETF（非單一國家）：
- lesson #52 排除「政策驅動單一 EM 國家 ETF」，EEM 為 broad 指數不受限制
- 混合進場未曾覆蓋 broad EM ETF 類別，首次驗證
- 目標：min(A,B) > 0.18（EEM-005 BB Squeeze 技術天花板）

設計邏輯：
- BB(20, 2.0) 下軌為自適應深度門檻：正常期較淺捕捉訊號，崩盤期自動深化
- 10 日高點回檔上限 -7%（6σ for 1.17% vol）隔離 EM 結構性崩盤
  （COVID -30%, 2022 中國監管 -25%, 俄烏 -15%）
- WR(10) ≤ -80 確認極端超賣
- ClosePos ≥ 40%（EEM-003/011 驗證對 EEM 有效）
- ATR(5)/ATR(20) > 1.1（EEM-010 驗證過濾慢磨下跌）
- 出場：TP +3.0% / SL -3.0% / 20 天（EEM-005 Att2 驗證對稱出場甜蜜點）

EEM 特有限制（必須遵守）：
- SL 禁放寬至 -3.5% 以下（lesson #49：EEM 停損為結構性崩潰，寬 SL 增加虧損不轉贏）
- TP 禁高於 +3.0%（EEM-005 Att1 驗證 TP 3.5% 到期過多）
- 回檔上限禁寬於 -8%（EEM-004 Att2 驗證 8% 上限已破壞 ATR 效用）

Att1: BB(20, 2.0) + 回檔上限 -7% + WR + ClosePos + ATR > 1.1 + TP+3%/SL-3%/20d/cd10
      → Part A 0.13 (7訊號, WR 57.1%, 累計 +2.40%, 3 停損：2019-05 貿易戰、
        2021-07 中國監管、2021-11 Omicron)
        Part B 0.56 (4訊號, WR 75.0%, 累計 +5.89%)
        min(A,B) 0.13（未達 EEM-005 Att2 的 0.18）
      → Part A 含 3 個 EM 危機假訊號，需加強過濾

Att2: 收緊 ATR > 1.15（EEM-010 驗證過濾慢磨下跌），其他同 Att1
      → Part A -0.60 (4訊號 WR 25%, 累計 -6.29%)
        Part B 0.56 (4訊號 WR 75%, 同 Att1)
        min(A,B) -0.60（大幅崩壞）
      → 失敗根因：EEM 停損訊號（危機日）ATR 普遍飆高 > 1.15，贏家反而
        ATR 較低。提高 ATR 門檻移除 3 個 Part A TP 贏家，保留 3 個停損。
        ATR 門檻對 EEM BB Lower 框架方向相反（vs RSI(2) 框架）。

Att3 (default ★): 還原 ATR 1.10，收緊 WR ≤ -85（要求更極端超賣，過濾淺觸）
      → Part A 0.34 (6訊號, WR 66.7%, 累計 +5.68%)
        Part B 0.56 (4訊號, WR 75.0%, 累計 +5.89%)
        min(A,B) 0.34（+89% vs EEM-005 Att2 的 0.18）★
      → WR -85 成功移除 2019-05-09 貿易戰停損（淺 WR 觸發）
        A/B 累計差僅 3.6%（遠優於 < 30% 要求）
        訊號頻率 1.2/yr vs 2.0/yr（Part B 牛市較活躍，可接受）
      → 首次驗證混合進場模式延伸至 broad EM ETF 類別。
        lesson #52 擴展：混合模式適用所有 broad EM / 非政策驅動單一 EM ETF
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EEM012Config(ExperimentConfig):
    """EEM-012 BB 下軌 + 回檔上限混合進場參數"""

    # BB 參數（自適應進場門檻）
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離（10 日高點回檔上限，過濾 EM 結構性崩盤）
    pullback_lookback: int = 10
    pullback_cap: float = -0.07  # 回檔上限 7%（~6σ for 1.17% vol）

    # 品質過濾（沿用 EEM-003/010/011 驗證有效參數）
    wr_period: int = 10
    wr_threshold: float = -85.0
    close_position_threshold: float = 0.40
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.10

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> EEM012Config:
    return EEM012Config(
        name="eem_012_bb_lower_pullback_cap",
        experiment_id="EEM-012",
        display_name="EEM BB Lower + Pullback Cap Hybrid MR",
        tickers=["EEM"],
        data_start="2010-01-01",
        profit_target=0.030,  # +3.0%（EEM-005 Att2 驗證對稱出場甜蜜點）
        stop_loss=-0.030,  # -3.0%
        holding_days=20,
    )
