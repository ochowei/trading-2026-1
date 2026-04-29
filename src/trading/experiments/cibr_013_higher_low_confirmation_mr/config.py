"""
CIBR Higher-Low Structural Confirmation MR Configuration (CIBR-013)

動機：CIBR-012 Att3（當前最佳 min(A,B) 0.49）以「2DD cap >= -4.0%」單日 momentum
過濾過濾掉 in-crash acceleration 進場，但 Part A 殘餘 1 筆停損（2021-02-26 2DD
-3.9%）為「續跌但 2DD 落於 cap 邊界內」的訊號。CIBR-009/010/011 三次嘗試以單日
price-action 結構（Key Reversal、NR7、Range Expansion）過濾均失敗——共通失敗原因
為單日 pattern 在事件驅動板塊缺乏「真假反轉」區分力。

核心假設：將「單日 pattern」擴展為「多日結構 pattern」可繞過此限制。具體而言，
Higher-Low 結構（今日 Low 嚴格高於過去 N 日 Low 最低值）為多日 swing 結構的
量化定義，比單日 ClosePos / Range Expansion / Key Reversal 更具結構意義：
- 單日 ClosePos 反映當日盤中反轉程度（時間尺度 = 1 日）
- 多日 Higher-Low 反映 swing 結構的反轉確認（時間尺度 = N 日）
- 後者篩選「過去 N 日已建立 swing low + 今日不再破底」的進場時機

Repo 中尚未試驗過此方向：
- CIBR-009 Key Reversal Day：今日 Low < 昨日 Low（反向，要求破底再 reclaim）
- CIBR-010 NR7：今日 TR 為近 7 日最小（範圍視角，不涉 Low 結構）
- CIBR-011 Range Expansion：今日 TR/ATR ≥ 2.0（爆發視角，不涉 swing 結構）
- 各資產 ClosePos：日內反轉（單日視角）
- 各資產 2DD floor / 2DD cap：兩日累計報酬（深度視角，非結構視角）

========================================================================
三次迭代結果（2026-04-26，成交模型 0.1% slippage，隔日開盤市價進場）
**全部失敗——min(A,B) 最佳僅 -0.08，遠低於 CIBR-012 Att3 的 0.49**
========================================================================

Att1（失敗，min -0.08）：純 pullback+WR+Higher-Low(3) 框架（不含 BB）
  進場：10d pullback in [-3%,-10%] + WR(10)<=-80 + Today_Low > min(Low[t-3..t-1])
        + Swing depth >= 1.0% + bullish bar + ATR(5)/ATR(20) > 1.10 + cd 8
  Part A: 2 訊號（1 TP +3.5%、1 SL -4.1%）WR 50% Sharpe -0.08 cum -0.74%
  Part B: 0 訊號
  min(A,B) -0.08（vs CIBR-012 Att3 0.49）
  失敗分析：5 重交集（pullback + WR + Higher-Low + Bullish bar + ATR）過嚴，2 訊號/8 年
  訊號密度 0.4/yr，Part B 完全空白。Higher-Low(3) 與 ATR>1.10 + bullish bar 三重結構
  確認過於罕見。

Att2（失敗，min -0.44）：放寬 ATR=1.00（停用）+ Higher-Low(3→5)
  Part A: 3 訊號 WR 33.3% Sharpe -0.44 cum -4.81%（新增 1 SL）
  Part B: 1 訊號 WR 100% TP +3.5% zero-var Sharpe 0.00 cum +3.50%
  min(A,B) -0.44（vs CIBR-012 Att3 0.49）
  失敗分析：放寬 lookback 5 與停用 ATR 引入 1 個新 Part A 訊號為 SL，Part A WR
  從 50%→33.3%。Higher-Low + 寬 ATR 環境下信號天然偏向「中段反彈失敗」型態。
  Part B 1 訊號 zero-var TP（2024-09-10 +3.5% 2 日達標）為唯一成功訊號。

Att3（失敗，min 0.00 zero signals）：BB Lower 框架 + Higher-Low(5)（取代 CIBR-012 2DD cap）
  進場：BB(20,2) 下軌觸及 + 10d pullback >= -12% + WR<=-80 + ClosePos>=40%
        + ATR>1.15 + Higher-Low(5) + Swing depth >= 0.5% + cd 8
  Part A: **0 訊號**
  Part B: **0 訊號**
  min(A,B) 0.00（vs CIBR-012 Att3 0.49）
  失敗分析：**結構性互斥發現**——BB Lower 觸及（Close <= BB_lower）日為統計極端
  下殺，今日 Low 幾乎必為近 5 日新低；而 Higher-Low(5) 要求今日 Low > min(Low[t-5..t-1])。
  兩條件在 CIBR 1.53% vol 板塊 ETF 上幾乎完全互斥（過去 8 年僅 1 訊號於 Part C 觸發）。
  此為 repo 首次驗證「BB Lower entry + multi-bar Higher-Low filter 結構性不可組合」。

========================================================================
**實驗結論**：Higher-Low 結構確認進場過濾在 CIBR 完全失敗
========================================================================

跨資產發現：
1. **Higher-Low + BB Lower 結構性互斥**（Att3 重要發現）
   - BB Lower 觸及 = 統計極端 panic = 今日 Low 必為近期新低
   - Higher-Low = 今日 Low > 近期 Low → 兩者幾乎不共存
   - 此互斥在 CIBR 1.53% vol 上 8 年僅 1 訊號觸發（Part C），結構性失效

2. **Higher-Low + pullback+WR+ATR 過嚴**（Att1）
   - 5 重交集訊號密度 0.4/yr 過稀

3. **放寬 Higher-Low 引入低品質訊號**（Att2）
   - lookback 3→5 + 停用 ATR 使新增訊號為「中段反彈失敗」型態

4. **擴展 lesson #20b 失敗家族**：
   - 從單日 pattern（Key Reversal、NR7、Range Expansion、ClosePos、2DD floor/cap）
   - 擴展至**多日結構 pattern**（Higher-Low Confirmation）
   - 同樣在事件驅動 1.5-2% vol 板塊 ETF 上缺乏「真假反轉」區分力
   - **結構維度（多日 swing）並未繞過單日 pattern 的失敗根因**

5. **CIBR-012 Att3（min 0.49）仍為全域最優**——確認 1.5-2% vol 板塊 ETF 上
   「BB Lower + Pullback Cap + WR + ClosePos + ATR + 2DD cap」為結構性最優

最終儲存配置（Att3，雖 0 訊號但代表最完整 BB Lower + Higher-Low 結構性互斥測試）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class CIBR013Config(ExperimentConfig):
    """CIBR-013 Higher-Low Structural Confirmation MR 參數

    Att3 設計：在 CIBR-008/012 的 BB Lower 框架上替換「2DD cap」為「Higher-Low
    結構」濾波。BB Lower 提供統計自適應的進場時機，Higher-Low 提供多日 swing
    結構的反轉品質確認，兩者組合驗證為**結構性互斥**（0 訊號）。
    """

    # === BB Lower 進場（同 CIBR-008/012 框架）===
    bb_period: int = 20
    bb_std: float = 2.0

    # 崩盤隔離（同 CIBR-008/012 -12%）
    pullback_lookback: int = 10
    pullback_cap: float = -0.12  # 回檔 <= 12% 才允許進場

    # 品質過濾（同 CIBR-012）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40

    # ATR 當日 panic 確認（同 CIBR-008/012）
    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.15

    # === Higher-Low 結構過濾（核心創新，取代 CIBR-012 的 2DD cap）===
    # 今日 Low > min(Low[t-N..t-1])
    # CIBR-012 Att3 使用 2DD cap >= -4.0% 過濾「in-crash acceleration」
    # Att3 改用結構過濾：Higher-Low 表示日內未破前 N 日低點，與 2DD cap 不同維度
    # **驗證為與 BB Lower 結構性互斥**——BB Lower 觸及日今日 Low 必為新低
    higher_low_lookback: int = 5

    # Swing 深度：過去 swing low 必須比今日 Close 至少低 X%
    # 防止 sideways consolidation 被誤判
    swing_depth_min: float = 0.005  # 0.5%（較寬鬆，但與 BB Lower 仍互斥）

    # 是否要求 bullish bar（Att3 不強制，BB Lower 已包含日內反彈訊息）
    require_bullish_bar: bool = False

    # 冷卻期
    cooldown_days: int = 8


def create_default_config() -> CIBR013Config:
    return CIBR013Config(
        name="cibr_013_higher_low_confirmation_mr",
        experiment_id="CIBR-013",
        display_name="CIBR Higher-Low Structural Confirmation MR",
        tickers=["CIBR"],
        data_start="2018-01-01",
        profit_target=0.035,
        stop_loss=-0.04,
        holding_days=18,
    )
