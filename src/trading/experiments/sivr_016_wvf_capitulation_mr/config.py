"""
SIVR-016：Williams Vix Fix 資本化均值回歸配置
(SIVR Williams Vix Fix Capitulation Mean Reversion Config)

動機（Motivation）：
    URA-010 Att3 在 URA 2.34% vol 上驗證「WVF + 10d 深回檔」產生 Part A Sharpe
    0.68 (in-sample 最高)，但 Part B 0.04（政策驅動導致 post-peak regime
    失效）。URA-010 明確列出跨資產假設：
        "模式可能適用於 Part A/B 兩段皆活躍 MR regime 的高波動資產
        （SIVR/COPX 待跨資產驗證）"

    SIVR 2.34% vol、GLD 比率 1.5-2x、Part A（2019-2023 含 COVID + 2022 熊市）
    與 Part B（2024-2025 銀價避險/Fed 降息期）兩段皆維持活躍 MR regime
    （SIVR-015 Att1 驗證 min(A,B) 0.48 平衡於兩段）。WVF 作為
    capitulation-depth 深度指標（非 turn-up），結構性與 oscillator hook
    不同——在 SIVR 上預期可區分「真正恐慌折價」vs「淺磨損緩跌」。

    本實驗為 **repo 第 2 次 WVF 試驗**（URA-010 後首次），亦為 WVF 在
    SIVR（白銀 ETF、避險/工業雙屬性）上的首次嘗試。挑戰 SIVR-015 Att1
    全域最優（min(A,B) 0.48）。

策略方向：均值回歸（capitulation depth detection，非 reversal confirmation）
    Strategy direction: Mean reversion via capitulation-depth detection

========================================================================
三次迭代記錄（2026-04-23，成交模型 0.15% slippage，隔日開盤市價進場）：
========================================================================

Att1：WVF(22) > BB_upper(WVF,20,2.0) + 10d pullback [-7%,-20%]
       + cd=10 + TP +3.5%/SL -3.5%/20天（SIVR 全域最優出場）
  Part A: 22 訊號（4.4/年）WR 50.0% Sharpe **0.02** cum +0.26%
  Part B:  9 訊號（4.5/年）WR 55.6% Sharpe **0.09** cum +2.40%
  min(A,B) **0.02**（-96% vs SIVR-015 Att1 的 0.48）
  失敗分析：WVF BB-upper 上穿在 SIVR 2.34% vol 上產生過多假 capitulation
  訊號——Part A 9 筆停損（2019-09/2020-09/2021-03/11/2022-05/06/10/
  2023-02/05）集中 1-4 天快速停損，代表「WVF 跳升但價格續跌」結構。
  WVF 單獨對 SIVR 缺乏 true/false capitulation 區分力，pullback [-7%,-20%]
  過寬引入淺回檔假訊號。A/B 年化訊號比 1.0:1 平衡極佳但 Sharpe 天花板過低。

Att2 ★（本實驗最佳，但仍低於 SIVR-015 Att1）：加深 pullback 至 -10%（URA-010 Att3 方向）
  Part A: 12 訊號（2.4/年）WR 66.7% Sharpe **0.33** cum +13.53%
  Part B:  4 訊號（2.0/年）WR 75.0% Sharpe **0.55** cum +6.84%
  min(A,B) **0.33**（-31% vs SIVR-015 Att1 的 0.48；+1550% vs Att1 的 0.02）
  A/B 年化訊號比 1.2:1（優秀，<50% 目標）
  A/B 累計差 49.5%（>30% 目標，Part A 13.53% vs Part B 6.84%）
  過濾動態：-10% pullback 門檻移除 Att1 Part A 22→12 訊號，剔除大多數
  1-4 天快速停損（淺 capitulation 假訊號）；4 筆殘餘 Part A 停損
  （2020-09-21/2021-12-01/2022-05-02/2022-07-05）為深回檔真跌，即便
  WVF + -10% 仍無法排除。Part B 9→4 訊號 WR 55.6→75.0%，
  2024-07-25/11-11、2025-04-04 三筆 TP + 2025-10-21 post-rally crash SL。
  驗證 WVF + 深回檔有選擇性但無法超越 SIVR-015 RSI hook 的邊際品質提升。

Att3（ablation + 疊加）：Att2 + RSI(14) bullish hook（SIVR-015 Att1 的成功過濾器）
  Part A:  1 訊號（0.2/年）WR 100% Sharpe 0.00（零方差）cum +3.50%
  Part B:  0 訊號
  min(A,B) **0.00**（統計不顯著，over-filter）
  失敗分析：WVF + RSI hook 幾乎正交——WVF 要求 price-depth capitulation
  完成，RSI hook 要求 momentum 已 turn-up，兩者在 SIVR 上極少同日觸發
  （只剩 2020-09-24 COVID 後的一筆）。Part B 完全無訊號，樣本不足以評估。
  確認 WVF 與 RSI hook 為**功能重疊而非互補**——SIVR-015 的 RSI hook 過濾器
  已隱含 capitulation 尾聲結構，WVF 額外加碼只移除訊號不提升品質。

========================================================================
整體失敗結論（3 次嘗試均未超越 SIVR-015 Att1 min(A,B) 0.48）：
========================================================================
1. **WVF 作為 SIVR 主訊號功能不足**：WVF BB-upper 上穿在 2.34% vol 上過度
   觸發，需疊加深回檔方具選擇性（Att1 → Att2 min Sharpe +0.31）
2. **WVF + 深回檔 vs RSI hook**：RSI hook 為更精確的 capitulation 尾聲過濾器
   （SIVR-015 min 0.48 vs SIVR-016 Att2 min 0.33）——
   hook 在 SIVR 活躍 MR regime 上能辨識 V-bounce 品質，WVF 無此能力
3. **WVF 與 RSI hook 結構性重疊**：Att3 疊加後只保留 1 筆訊號，驗證兩者
   在 SIVR 上並非互補過濾器（結構性假設差異：WVF 依 price distance，
   RSI hook 依 momentum turn）
4. **擴展 lesson #20b 失敗家族至 capitulation-depth 類別（SIVR 維度）**：
   URA-010（URA 政策驅動，post-peak regime）與 SIVR-016（SIVR 活躍
   MR regime）均失敗，確認 WVF 作為主 MR 訊號的跨資產限制——即使在
   「理論上應該成功」的活躍 MR regime 資產上，WVF 仍因**缺乏 momentum
   turn confirmation** 而次於 RSI hook-based 過濾器
5. **Repo 第 2 次 WVF 試驗失敗**（URA-010 Att3 Part A 0.68/Part B 0.04，
   SIVR-016 Att2 Part A 0.33/Part B 0.55），WVF 在 repo 內尚未成功

跨資產規則（新）：
  - WVF 作為主訊號在 2-3% vol 資產上需強制搭配深回檔（-10% 起跳）
  - WVF 與 RSI(14) hook 為結構性重疊過濾器，不可同時使用
  - SIVR 的 MR 核心為「capitulation 尾聲 + momentum turn-up」（SIVR-015
    Att1），非「capitulation 深度本身」——此為 SIVR 特有結構

SIVR 特有限制（已確認）：
  - SIVR-015 Att1（RSI hook + pullback+WR）為全域最優（min 0.48）
  - WVF 系列在 SIVR 上最佳僅達 0.33（Att2），確認 SIVR-015 為真正天花板

資產特性：SIVR 日波動 2.34%，GLD 比率 1.5-2x。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class SIVR016Config(ExperimentConfig):
    """SIVR-016 Williams Vix Fix 資本化均值回歸參數"""

    # WVF 主訊號（同 URA-010）
    wvf_lookback: int = 22  # 折價深度回看 N 日
    wvf_bb_lookback: int = 20  # WVF 序列的 BB 計算窗口
    wvf_bb_stddev: float = 2.0  # BB 標準差倍數（突破上軌即 capitulation）

    # 回檔深度過濾（Att2 最終配置：-10% 深回檔）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.10  # 10d 高點回檔 ≥ 10%
    pullback_upper: float = -0.20  # 回檔上限 20%（過濾結構性崩盤）

    # RSI(14) bullish hook（Att3 試驗發現 over-filter，Att2 最終停用）
    rsi_hook_enabled: bool = False
    rsi_period: int = 14
    rsi_hook_lookback: int = 5
    rsi_hook_delta: float = 3.0
    rsi_hook_max_min: float = 35.0

    # 冷卻
    cooldown_days: int = 10


def create_default_config() -> SIVR016Config:
    return SIVR016Config(
        name="sivr_016_wvf_capitulation_mr",
        experiment_id="SIVR-016",
        display_name="SIVR Williams Vix Fix Capitulation MR",
        tickers=["SIVR"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（SIVR 全域最優對稱出場）
        stop_loss=-0.035,  # -3.5%
        holding_days=20,
    )
