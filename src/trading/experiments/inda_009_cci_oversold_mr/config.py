"""
INDA-009: CCI Oversold Reversal Mean Reversion
(INDA CCI 深度超賣 + 反轉均值回歸)

動機：INDA-005 Att3（10日回檔 3-7% + WR+ClosePos+ATR+2日跌幅，TP+3.5%/SL-4%/15d）
min(A,B) Sharpe 0.23，Part A Sharpe 0.23 / Part B Sharpe 0.31。INDA 已證明 pullback+WR
框架飽和（INDA-006 三次調參失敗），BB 混合進場失敗（INDA-008），RS 動量失敗
（INDA-007）。本實驗探索 repo 中尚未使用的指標方向 —— Commodity Channel Index (CCI)
作為主要進場訊號。**repo 首次試驗 CCI 指標**。

CCI 與 RSI/BB 的關鍵差異：
- CCI 用「平均絕對偏差 (MAD)」量化當前 Typical Price 偏離 SMA 的程度，對極端值
  較不敏感（vs BB 用 std 對極端值放大）
- CCI 無邊界（與 RSI/WR 0-100 區間不同），可達 -200/-300 極端值，允許「很深但仍
  在回歸範圍」與「深到崩盤」之間的區分
- CCI(20) < -100 傳統「超賣」，< -200 傳統「極端超賣」

INDA-009 的設計邏輯：
- 進場主訊號：CCI(20) 觸及深度超賣，然後「今日 CCI > 過去 2 日 CCI 最低點」
  （CCI 轉折向上確認反轉）
- 反轉確認：Close > Open（K 線收紅，日內反轉證據）
- 冷卻期 10 天（同 INDA-005）
- 出場：TP+3.5% / SL-4.0% / 持倉 15 天（同 INDA-005 甜蜜點）

Att1 (baseline): CCI(20) ≤ -100 + CCI 轉折 + Close > Open + cd=10
  → Part A 21 訊號 WR 61.9% Sharpe 0.09 / Part B 9 訊號 WR 44.4% Sharpe -0.46
  → min(A,B) -0.46（失敗），A/B 訊號比 2.33:1 過高

Att2: 加嚴 CCI 至 -150 + 加入 ClosePos ≥ 40%（INDA 已驗證有效過濾器）
  → Part A 9 訊號 WR 55.6% Sharpe 0.05 / Part B 3 訊號 WR 66.7% Sharpe -0.03
  → min(A,B) -0.03（仍失敗），A/B 訊號比 3.0:1 更惡化

Att3: 放寬 CCI 回 -100 + 保留 ClosePos + 加入 10 日回檔 ≥ 2.5% 下限
  （過濾平盤時期 CCI 假訊號）
  → Part A 17 訊號 WR 58.8% Sharpe 0.06 / Part B 9 訊號 WR 44.4% Sharpe -0.46
  → min(A,B) -0.46（失敗，與 Att1 相同）
  → 核心洞察：Part B 所有 CCI<-100 轉折訊號天然伴隨 ≥2.5% 回檔，故
    pullback 下限過濾僅移除 Part A 4 筆訊號，對 Part B 完全無效

═══════════════════════════════════════════════════════════════════════
最終結論（三次迭代均失敗 vs INDA-005 Att3 min 0.23）
═══════════════════════════════════════════════════════════════════════

| Att | CCI 門檻 | 額外條件 | Part A Sharpe | Part B Sharpe | min(A,B) |
|-----|---------|----------|---------------|---------------|----------|
| 1 ★ | -100    | Close>Open only | 0.09 (21) | **-0.46** (9) | -0.46 |
| 2   | **-150** | + ClosePos≥40% | 0.05 (9) | -0.03 (3) | -0.03 |
| 3   | -100    | + ClosePos + Pullback≥2.5% | 0.06 (17) | -0.46 (9) | -0.46 |

**失敗根因**（repo 首次 CCI 試驗的跨資產發現）：

1. INDA 0.97% vol 低波動特性下，CCI(20) 在 2024-2025 持續下跌期間（後峰 INDA
   ~58→~48）長時間停留於超賣區（CCI<-100 命中率遠高於高波動資產）。CCI 隨
   每次迷你反彈短暫「轉折向上」，產生大量假進場訊號（Part B 9/9 訊號中
   4 筆停損、2 筆到期虧損、1 筆淺利到期）。
2. 加嚴 CCI 至 -150（Att2）雖將 Part B 訊號降至 3 筆樣本（WR 66.7%），但 Part B
   累計仍為負，且 Part A 因 13/21 好訊號被過濾掉而 Sharpe 劣化 0.09→0.05——
   「加嚴不改善，反破壞」。
3. 加入 Pullback 下限（Att3）對 Part B 完全無效，因 Part B 下跌期所有 CCI
   轉折訊號本就發生在 ≥2.5% 回檔中，過濾器零作用。
4. ClosePos 和反轉 K 線過濾器無法區分「真反轉」與「暫時回彈後續跌」——這
   與 lesson #20b（RSI Bullish Hook Divergence 在政策驅動資產失敗）、
   URA-008（hook 失敗）、TLT-006（Day-After Capitulation 失敗）同屬
   **oscillator hook / V-bounce ≠ genuine reversal** 失敗家族。

**跨資產教訓貢獻**：
- CCI 作為均值回歸主訊號，第一次在 repo 中測試
- 失敗模式與 lesson #20b RSI hook divergence 平行：後峰持續下跌 regime 中
  任何 oscillator turn-up 訊號均無法識別真反轉
- 推斷有效先決條件（類比 lesson #20b）：需要兩段 Part A/B 皆活躍 MR regime，
  INDA 2024-2025 Part B 為慢磨下跌 regime 自動違反此條件
- INDA-005 Att3 維持為全域最優（9 次實驗、28+ 次嘗試）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class INDA009Config(ExperimentConfig):
    """INDA-009 CCI 超賣反轉均值回歸參數"""

    # CCI 參數（Att3：放寬回 -100，改以回檔下限過濾假訊號）
    cci_period: int = 20
    cci_oversold: float = -100.0  # Att3：回復標準超賣門檻
    cci_turn_lookback: int = 2
    cci_turn_delta: float = 0.0

    # 反轉 K 線確認
    require_close_gt_open: bool = True

    # ClosePos 過濾
    use_close_pos: bool = True
    close_pos_threshold: float = 0.40

    # 10 日高點回檔（Att3 新增：要求至少 2.5% 回檔才算有效超賣）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.025  # 10日高點回檔 >= 2.5%

    # 冷卻期
    cooldown_days: int = 10


def create_default_config() -> INDA009Config:
    return INDA009Config(
        name="inda_009_cci_oversold_mr",
        experiment_id="INDA-009",
        display_name="INDA CCI Oversold Reversal Mean Reversion",
        tickers=["INDA"],
        data_start="2012-01-01",
        profit_target=0.035,  # +3.5%
        stop_loss=-0.040,  # -4.0%
        holding_days=15,  # 同 INDA-005 Att3
    )
