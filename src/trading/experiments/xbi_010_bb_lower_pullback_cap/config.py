"""
XBI-010: BB Lower Band + Pullback Cap Hybrid Mean Reversion
(XBI BB 下軌 + 回檔上限混合進場均值回歸)

動機：XBI-005 (Pullback 8-20% + WR + ClosePos 35%) min(A,B) Sharpe 0.36，
Part A Sharpe 0.36 / Part B Sharpe 0.64，A/B Sharpe gap 0.28，Part B
(2022-2025 後生技熊市恢復期) 明顯優於 Part A（2010-2021 含 2015/2016 生技
崩盤 + 2021-22 熊市）。Part A 的品質受到極端深度回檔假訊號拖累（XBI 歷史
上 2015-16 生技泡沫破裂、2021-22 熊市期間連續下跌）。

參考近期 BB 下軌 + 回檔上限混合進場成功案例：
- EWJ-003 Att3 (1.15% vol): BB(20,1.5) + cap -7%, Part A Sharpe 0.55→0.60
- VGK-007 Att1 (1.12% vol): BB(20,2.0) + cap -7%, min(A,B) 0.45→0.53 (+18%)
- CIBR-008 Att2 (1.53% vol): BB(20,2.0) + cap -12%, min(A,B) 0.27→0.39 (+44%)
- EWZ-006 Att3 (1.75% vol): BB(20,1.5) + cap -10%, min(A,B) 0.34→0.69 (+103%)

BB 下軌提供統計自適應進場門檻，回檔上限隔離極端崩盤事件，
兩者結合可在保留訊號頻率的同時濾除低品質崩盤訊號。

XBI 日波動 ~2.0%，處於已驗證混合進場模式的邊界（EWZ 1.75% 是目前已驗證上限）：
- 高波動需放寬 BB σ 維持訊號頻率（EWZ 用 1.5σ，CIBR 用 2.0σ）
- 回檔上限 -12% ~ 6σ（與 CIBR 的 5.2σ 和 EWZ 的 5.7σ 策略一致）
- 三重品質過濾在 XBI 2.0% 邊界需調整：ATR 過濾已在 XBI-009 Att1/2 驗證失敗
  （日波動已達 ATR 有效邊界上限），故混合進場採 WR+ClosePos 雙重過濾

進場五條件：
1. Close <= BB(20, 1.5) 下軌 (自適應深度過濾)
2. 10日高點回檔 >= -12% (6σ 崩盤隔離)
3. Williams %R(10) <= -80 (超賣確認)
4. ClosePos >= 35% (日內反轉確認，XBI-005 驗證甜蜜點)
5. 冷卻期 10 天

出場參數：TP +3.5% / SL -5.0% / 持倉 15 天（XBI-005 已驗證甜蜜點，SL -5% 為底線）

Att1: BB(20, 1.5) + cap -12% (6σ) + WR + ClosePos 35%, TP+3.5%/SL-5.0%/15d
      → Part A 0.09 (20訊號, WR 65%, 累計 +5.38%)
        Part B 0.07 (8訊號, WR 62.5%, 累計 +1.51%)
        min(A,B) 0.07（遠遜於 XBI-005 的 0.36）
      失敗分析：BB(20, 1.5) 在 XBI 2.0% 日波動下過於寬鬆，產生 20 個 Part A
      訊號但平均報酬僅 0.27%（vs XBI-005 的 1.3%），WR 65% vs 76.2%。
      BB 1.5σ（相當於均值-3%）捕捉了太多淺層技術超賣而非真正恐慌拋售

Att2: BB(20, 2.0) 提高 σ 至標準值 + 其他同 Att1
      → Part A -0.03 (7訊號, WR 57.1%, 累計 -1.41%)
        Part B -0.55 (3訊號, WR 33.3%, 累計 -6.79%)
        min(A,B) -0.55（嚴重失敗）
      失敗分析：BB(20, 2.0) 反而過嚴，訊號集中在極端崩盤事件
      （2020 COVID、2022 熊市低點），這些訊號多數無法在 15 天內恢復。
      BB 下軌作為 XBI 主進場訊號在 2.0% 日波動下無論 σ 值均不如 XBI-005
      固定回檔 8% 深度過濾

Att3 (default, 最佳失敗嘗試): 混合 OR 進場 — BB(20, 2.0) 下軌觸及 OR 10日高點回檔 ≥ 8%
      + cap -12% + WR + ClosePos ≥ 35%, TP+3.5%/SL-5.0%/15d
      → Part A 0.20 (19訊號, WR 68.4%, 累計 +14.83%)
        Part B 0.16 (6訊號, WR 66.7%, 累計 +3.35%)
        min(A,B) 0.16（仍遜於 XBI-005 的 0.36）
      失敗分析：OR 進場恢復了 Part A 19 訊號（接近 XBI-005 的 21），
      WR 68.4% 仍低於 XBI-005 的 76.2%。Cap -12% 相對 XBI-005 的 -20% 過嚴，
      移除了幾個深回檔贏家（2020 COVID 後的 14-18% 反彈、2022 熊市中期深跌反彈）。
      BB 下軌作為 OR-trigger 無額外貢獻（BB 訊號大多已在 pullback ≥ 8% 條件內）

**最終結論：BB 下軌 + 回檔上限混合進場模式不適用 XBI**
三次迭代均未勝過 XBI-005（min(A,B) 0.36）。根本原因：
1. XBI 2.0% 日波動超出混合模式已驗證有效邊界（EWJ 1.15%, VGK 1.12%,
   CIBR 1.53%, EWZ 1.75%）
2. XBI 無法使用 ATR 過濾（XBI-009 Att1/2 驗證，日波動達 ATR 有效邊界上限），
   而 ATR 是三重品質過濾中關鍵的「波動率飆升確認」組件
3. XBI-005 的固定 pullback 8-20% 框架在 2.0% 日波動下已是最優：
   - 8% (4σ) 下限過濾淺回檔噪音
   - 20% 上限保留深度崩盤中的反彈訊號（-12~-20% 區間）
   - 混合模式的 BB 下軌觸發在此框架外無額外資訊
4. XBI 為生技板塊 ETF，FDA/臨床事件驅動特性使訊號呈現為 8-15% 的
   絕對深度回檔，而非 BB 帶寬所反映的統計異常

**確認 XBI-005 為 XBI 全域最優，混合進場模式有效邊界確認為日波動 ≤ 1.75%**
（EWZ 為目前已驗證上限，XBI 2.0% 為首個失敗驗證）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class XBI010Config(ExperimentConfig):
    """XBI-010 BB 下軌 OR 回檔混合進場參數"""

    # BB 參數（自適應進場門檻）
    bb_period: int = 20
    bb_std: float = 2.0

    # 回檔進場（OR 條件）
    pullback_lookback: int = 10
    pullback_entry_threshold: float = -0.08  # 回檔 >= 8%（XBI-005 驗證甜蜜點）

    # 崩盤隔離（共同 AND 條件）
    pullback_cap: float = -0.12  # 回檔上限 12%（~6σ for 2.0% vol）

    # 品質過濾（XBI-005 驗證有效參數）
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_position_threshold: float = 0.35  # XBI-005 驗證甜蜜點

    cooldown_days: int = 10


def create_default_config() -> XBI010Config:
    return XBI010Config(
        name="xbi_010_bb_lower_pullback_cap",
        experiment_id="XBI-010",
        display_name="XBI BB Lower + Pullback Cap Hybrid MR",
        tickers=["XBI"],
        data_start="2010-01-01",
        profit_target=0.035,  # +3.5%（XBI-005 驗證甜蜜點）
        stop_loss=-0.050,  # -5.0%（XBI 硬底線，不可收窄）
        holding_days=15,
    )
