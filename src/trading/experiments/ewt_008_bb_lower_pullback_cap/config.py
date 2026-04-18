"""
EWT-008: BB Lower Band + Pullback Cap Hybrid Mean Reversion
(EWT BB 下軌 + 回檔上限混合進場均值回歸)

延伸 EWJ-003 / VGK-007 / CIBR-008 / EWZ-006 的混合進場架構至 EWT。
EWT 日波動 1.41%，落在已驗證有效的 vol 區間 [1.12%, 1.75%] 中段：

| 資產 | 日波動 | BB std | 回檔上限 | min(A,B) | 備註 |
|------|--------|--------|----------|----------|------|
| EWJ  | ~1.15% | 1.5σ   | 7%（～6σ）| 0.60     | DM 單一國家 |
| VGK  | 1.12%  | 2.0σ   | 7%（6σ） | 0.53     | 歐洲寬基 |
| CIBR | 1.53%  | 2.0σ   | 12%（7.8σ）| 0.39   | 美國板塊 |
| EWZ  | 1.75%  | 1.5σ   | 10%（5.7σ）| 0.69   | 商品驅動 EM 單一國家 |
| EWT  | 1.41%  | 2.0σ   | 8%（5.7σ）| ?       | 本實驗（EM 半導體驅動）|

EWT-007 Att1（RS 動量）當前最佳 min(A,B) 0.42，但 A/B 累計差 30.5%（>30%）。
BB 下軌混合進場提供獨立於 EEM 比較的進場框架：
- 低波動期：BB 下軌淺觸及 → 捕捉更多有效訊號
- 高波動期：BB 下軌深觸及 → 自動隔離極端崩盤
- 回檔上限 -8%（5.7σ）排除 2022-2023 中美地緣政治風暴等極端崩盤
- 三重品質過濾（WR + ClosePos + ATR）補足 EWT-002 驗證有效組合

出場使用 EWT-007 甜蜜點（TP+3.5%/SL-4%/20d/cd10）維持一致性。
ATR(5)/ATR(20) > 1.10 對應 EWZ-006 / CIBR-008 標準門檻。
EWT-002 Att1 驗證 ATR > 1.15 在均值回歸框架有效（Sharpe 0.13/0.64）。

Att1 (default ★): BB(20, 2.0) + cap -8% + WR + ClosePos 40% + ATR > 1.10
  + TP+3.5%/SL-4%/20d + cd10
  → Part A 0.57 (9訊號 1.8/yr, WR 77.8%, +17.01%)
    Part B 0.00† (3訊號 1.5/yr, WR 100%, +10.87%)
  → min(A,B) 0.57† (†Part B 零方差 3/3 全達 +3.50%，採 EWJ-003 慣例以 Part A 為綁定約束)
  → vs EWT-007 Att1 的 0.42（+36%），但 A/B 累計差 36.1%（略超 30% 目標）
  → A/B 年化訊號比 1.2:1（優秀）

Att2: BB(20, 1.75) 其餘同 Att1（放寬 BB std 增加訊號）
  → Part A 0.27 (15訊號, WR 66.7%, +14.42%)
    Part B 0.12 (5訊號, WR 60.0%, +1.97%)
  → min(A,B) 0.12 ✗ 放寬 BB 引入低品質訊號（Part A 2 SL, Part B 2 SL），
    三重品質過濾在 1.75σ 下失去選擇性

Att3: BB(20, 2.0) + cap -10% 其餘同 Att1（放寬回檔上限）
  → Part A 0.55 (11訊號, WR 72.7%, +19.51%)
    Part B 0.00† (3訊號 同 Att1, WR 100%, +10.87%)
  → min(A,B) 0.55† Part B 訊號集與 Att1 相同（2024-2025 無 -8% 至 -10% 區間
    的 BB 下軌觸及）；Part A 新增 2 訊號但 WR 從 77.8%→72.7% 拖累 Sharpe

結論：Att1 為 EWT-008 最佳組合。混合進場架構成功延伸至 EWT 1.41% vol DM/EM 單一國家
ETF，驗證 lesson #52 有效 vol 區間內的 TW 半導體驅動市場同樣適用。Part B 3 訊號
全達標 +3.50% 與 EWJ-003 模式一致，未來數據擴充後 Part B Sharpe 將自然浮現。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWT008Config(ExperimentConfig):
    """EWT-008 BB 下軌 + 回檔上限混合進場參數"""

    # BB 參數（自適應進場門檻）
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離（10日高點回檔上限，過濾極端崩盤）
    pullback_lookback: int = 10
    pullback_cap: float = -0.08  # 回檔上限 8%（5.7σ for 1.41% vol）

    # 品質過濾
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.40
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.10

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> EWT008Config:
    return EWT008Config(
        name="ewt_008_bb_lower_pullback_cap",
        experiment_id="EWT-008",
        display_name="EWT BB Lower + Pullback Cap Hybrid MR",
        tickers=["EWT"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（EWT 跨策略甜蜜點）
        stop_loss=-0.040,  # -4.0%
        holding_days=20,
    )
