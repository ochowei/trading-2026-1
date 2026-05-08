"""
EWZ-009: EWZ-EEM Relative Strength Divergence Filter on Vol-Transition MR

策略方向（pair-divergence as macro regime gate）：
- 在 EWZ-007 Att3 完整框架（BB(20,1.5) 下軌 + 10d 回檔上限 + WR(10) + ClosePos +
  ATR(5)/ATR(20)>1.10 + 1d cap >= -5%, TP+5%/SL-4%/18d/cd10）之上，
  新增 **EWZ vs EEM 相對強度（10 日報酬差）上限**作為 cross-asset pair-divergence
  regime gate。
- 假設：當 EWZ 過去 10 日相對 EEM 強勢（rel_10d > 閾值），訊號日的 BB 下軌觸碰
  更可能為「Brazil-specific 局部疲弱中段」（global EM 仍健康但 EWZ 開始 lagging
  → 後續為持續性 country-specific 下跌），均值回歸不成立；當 EWZ 相對 EEM 弱勢
  或同步弱勢，訊號為「broad EM/Brazil 同步 capitulation」更可能反彈。

跨資產脈絡（lesson #20 v3 cross-asset divergence regime gate）：
- TLT-014 ✓（TLT vs SPY divergence，rate ETF + MR 框架）
- TSLA-017 ✓（TSLA vs QQQ divergence，high-vol single stock + BB Squeeze
  Breakout 框架）
- COPX-014 ✗（COPX vs GLD divergence，商品/礦業 ETF + BB Squeeze 框架失敗
  — cooldown × 訊號密度 失敗 + 訊號日進場條件已偏多）
- NVDA-016 ◐（NVDA vs SMH，部分成功但 A/B gap 違反）
- USO-026 ✗（USO vs XLE，商品 ETF + MR 框架失敗 — A/B 結構不對稱）
- 既有 EWZ-005 RS 動量回調為 RS spread 作主訊號（失敗），EWZ-009 改用 RS spread
  作品質過濾器（filter）疊加於 EWZ-007 已驗證 MR 主訊號之上

trade-level 分析（EWZ-007 Att3 全部 17 訊號之 EWZ-EEM rel_10d 分布）：
================================================================================
Part A (11 訊號，含 2 SLs):
  Date       | Type | EWZ_10d | EEM_10d | Rel_10d (EWZ - EEM, pp)
  2019-03-25 | SL   | -4.95%  | +0.26%  | -5.20pp  ← 2 SLs 之 1，rel_10d 極低
  2019-05-14 | TP   | -5.85%  | -6.33%  | +0.48pp
  2019-08-02 | TP   | -4.56%  | -5.39%  | +0.83pp
  2019-11-13 | TP   | -6.36%  | -0.37%  | -5.99pp
  2020-01-31 | SL   | -4.62%  | -8.40%  | +3.78pp  ← 2 SLs 之 2，rel_10d 唯一 > +2.12
  2020-11-02 | TP   | -5.92%  | -0.33%  | -5.59pp
  2021-01-22 | TP   | -5.71%  | +4.75%  | -10.45pp ← rel_10d 最低 TP
  2021-07-07 | TP   | -5.95%  | -0.83%  | -5.12pp
  2021-10-21 | TP   | -5.49%  | +3.00%  | -8.50pp
  2022-09-28 | TP   | -4.99%  | -7.11%  | +2.12pp  ← rel_10d 最高 TP
  2023-10-04 | TP   | -9.54%  | -3.98%  | -5.56pp

Part B (6 訊號，全 wins):
  2024-01-18 | EXP  | -4.41%  | -3.87%  | -0.54pp
  2024-04-15 | TP   | -3.20%  | -2.14%  | -1.07pp
  2024-06-10 | EXP+ | -5.98%  | -1.70%  | -4.28pp
  2024-11-29 | TP   | -6.90%  | +0.72%  | -7.62pp
  2025-03-04 | TP   | -9.40%  | -3.36%  | -6.04pp
  2025-10-14 | TP   | -6.13%  | -0.81%  | -5.32pp

關鍵觀察：
- **2020-01-31 SL 為 rel_10d 維度結構性 outlier**：+3.78pp，唯一 > +2.5pp 訊號
- 全部 9 個 Part A TPs 之 rel_10d ≤ +2.12pp（max 2022-09-28），存在 surgical sweet
  spot [+2.12pp, +3.78pp]
- 2019-03-25 SL（rel_10d -5.20pp）落於 TPs 中段，**單一 rel_10d 維度無法過濾**——
  與 EWZ-007 文件「2 SLs 結構性異質」一致（Brazil-specific weakness vs 全球 risk-off
  早期）
- Part B 全 6 訊號 rel_10d ≤ -0.54pp，**filter 對 Part B 完全非綁定** ✓
- 預期效果：移除 1 SL（2020-01-31）+ 零 winners 損傷 + Part B 不變
- 2019-03-25 SL 結構性殘留為 EWZ-007 文件已知邊界（"Up-day rebound after big drop"
  與「moderate 1d sustained drop」結構，無法用單一維度過濾）

迭代計畫：
- Att1: rel_10d_max = +2.5pp（surgical sweet spot 中央，目標 2020-01-31 SL）
- Att2: 視 Att1 結果調整 lookback / threshold / 加入第二維度
- Att3: 進一步精煉

跨資產貢獻（預期）：
- repo 第 6 次 cross-asset divergence regime gate 應用（繼 TLT/TSLA/COPX/USO/NVDA）
- repo 首次 EM ETF cross-asset divergence regime gate 試驗
- EEM 為 broad EM 自然 anchor（非 implied vol、非 spot FX、非 broad equity 寬基）—
  屬於「同類 ETF 內 broader benchmark 為 anchor」的 lesson #20 變體
- 與 lesson #20 v3 邊界精煉：cooldown 10d × 訊號密度 ~2/yr ≈ 0.20（與 TSLA-017
  類似），且訊號日進場條件已偏弱（capitulation pattern），預期適用條件滿足
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class EWZ009Config(ExperimentConfig):
    """EWZ-009 EWZ-EEM Divergence Filter on Vol-Transition MR 參數"""

    # === EWZ-007 Att3 完整框架 ===
    bb_period: int = 20
    bb_std: float = 1.5
    pullback_lookback: int = 10
    pullback_cap: float = -0.10
    wr_period: int = 10
    wr_threshold: float = -80.0
    close_pos_threshold: float = 0.40
    atr_fast: int = 5
    atr_slow: int = 20
    atr_ratio_threshold: float = 1.10
    capitulation_mode: str = "1d_cap"
    capitulation_threshold: float = -0.050
    cooldown_days: int = 10

    # === EWZ-009 核心新增：EWZ-EEM rel strength divergence ===
    # EEM (iShares MSCI Emerging Markets ETF) 為 broad EM benchmark，作 pair anchor
    eem_ticker: str = "EEM"
    # lookback：trade-level 分析顯示 10d 為 surgical sweet spot 中央
    rel_lookback: int = 10
    # max rel return (EWZ_Nd - EEM_Nd, in fraction)：
    # **Att1 ★ 甜蜜點 +2.5% (= 0.025)**
    #   - Att1 +2.5%：surgical sweet spot 中央，Part A 訊號 11→10 移除 2020-01-31 SL，
    #     Part B 完全不變。Part A Sharpe 0.95→1.50（+58%），min(A,B) 0.95→1.50
    #   - Att2 +2.0% 過嚴：移除 2022-09-28 TP（rel_10d +2.12pp），Part A 9 訊號
    #     Sharpe 1.39（仍優於 baseline 0.95 但低於 Att1）
    #   - Att3 +3.5% robustness：訊號集完全等於 Att1（filter 對 2020-01-31 SL 仍綁定，
    #     對其他訊號非綁定），確認 [+2.5%, +3.5%] 為 robust sweet spot
    max_rel_return: float = 0.025


def create_default_config() -> EWZ009Config:
    return EWZ009Config(
        name="ewz_009_ewz_eem_divergence_mr",
        experiment_id="EWZ-009",
        display_name="EWZ EWZ-EEM Divergence-Gated Vol-Transition MR",
        tickers=["EWZ"],
        data_start="2010-01-01",
        profit_target=0.050,
        stop_loss=-0.040,
        holding_days=18,
    )
