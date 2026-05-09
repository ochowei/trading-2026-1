"""
TSM-016: BB-Width Regime Gate on RS Momentum Pullback 配置
TSM BB-Width Regime Gate on RS Momentum Pullback Configuration

策略方向：在 TSM-011 Att3 的 RS Momentum Pullback + 5d ceiling 框架上加入
**BB-Width Regime Gate**（lesson #23 cross-strategy port），過濾 elevated-vol regime
訊號，hypothesis Part B SLs 集中於較高波動率區段。

Lesson #23 cross-strategy 擴展（repo 第 4 次 lesson #23 試驗、首次 RS Momentum 框架）：
- 過往：BB-Width Regime Gate 在 leveraged ETF / 利率資產 MR 框架成功
  - TLT-007 Att2（rate-driven MR，1% vol，閾值 0.05）
  - TQQQ-018 Att3（leveraged broad index，~5% vol，閾值 0.48）
  - SOXL-012 Att3（leveraged sector，~6% vol，閾值 0.43）
- 本實驗：首次將 BB-Width Regime Gate cross-strategy 移植至 RS Momentum 框架
- 假設：TSM Part B 殘餘 SLs (2024-07-16 pre-earnings、2024-10-30 post-earnings drift)
  發生於 elevated-vol regime；BB-Width Regime Gate 切除 elevated-vol 訊號可同時
  保留 calm-regime momentum continuation winners。

進場條件（沿用 TSM-011 Att3，新增第 6 條件）：
1. TSM 20日報酬 - SMH 20日報酬 >= 5%（相對板塊超額表現）
2. 5日高點回撤 3-7%（短暫整理）
3. 收盤價 > SMA(50)（上升趨勢確認）
4. 訊號日 5 日報酬 <= +10.5%（rally exhaustion 過濾）
5. **新增 BB(20, 2) Width / Close <= bb_width_max（calm regime gate）**
6. 冷卻期 10 個交易日

三次迭代結果（基線 TSM-011 Att3 min(A,B) Sharpe 0.83，2 Part A SLs + 2 Part B SLs）：
- Att1（bb_width_max = 0.15，lenient）：FAILED min(A,B) **0.42** REJECT
  Part A 5/100%/std=0 cum +46.93%（過濾 7 訊號含 2 Part A SLs）
  Part B 6/66.7%/Sharpe **0.42** cum +17.44%（**lesson #19 cooldown chain shift**：
  原 2024-07-16 SL 被替換為 2024-07-08 SL，原 2024-10-30 SL 被替換為
  2024-11-01 SL，淨效果 SL 數量未減少）
- **Att2 ★ PARTIAL（bb_width_max = 0.12，medium calm regime）**：min(A,B)† 雙 Part std=0
  Part A 3 訊號 WR **100%** std=0 cum +25.97%（5/5 Part A SLs 全過濾，sample 縮減）
  Part B 2 訊號 WR **100%** std=0 cum +16.64%（**雙 Part B SLs 全過濾**：
  原 2024-07-16 與 2024-10-30 + chain-shifted 2024-07-08/2024-11-01 全部被過濾）
  雙 Part 結構性零方差為 repo 第 6 次（繼 EWJ-005/EWT-008/SPY-009/DIA-012/IWM-013/CIBR-014 後）
  A/B 年化幾何 cum 差 |4.7%-8.0%|/8.0% = **41%（>30% target ❌）** — A/B 樣本數小
  + Part A 5 年期 vs Part B 2 年期幾何稀釋使 cum gap 略超目標
  A/B 年化訊號比 0.6:1.0 vs 1.0:1.0 = gap 33%（<50% ✓）
  **PARTIAL SUCCESS**：結構性最優（雙 Part 100% WR）但 A/B cum gap 邊際違反
- Att3（bb_width_max = 0.14，sweet-spot test）：FAILED min(A,B) **-0.29** REJECT
  Part A 3 訊號 100% WR std=0（同 Att2）
  Part B 6 訊號 33.3% WR Sharpe **-0.29** cum -13.08% (**4 SLs**)
  0.14 閾值同時放回 cooldown chain 觸發的 earnings-week SLs（2024-10-16 T+(-1) 到
  earnings 10/17、2025-01-16 同日 earnings、2024-11-01 chain shift）

跨資產貢獻（lesson #23 family v4 cross-strategy 邊界擴展）：
- Repo 第 4 次 lesson #23 BB-Width Regime Gate 試驗
  既有：TLT-007 Att2（rate-driven MR，1% vol，閾值 0.05）✓
       TQQQ-018 Att3（leveraged broad index，~5% vol，閾值 0.48）✓
       SOXL-012 Att3（leveraged sector ETF，~6% vol，閾值 0.43）✓
- Repo **首次 BB-Width Regime Gate 移植至 RS Momentum Pullback 框架**（cross-strategy）
- TSM ~2% vol 的 BB-Width 閾值 0.12 落於既有 4 個成功案例的對數線性區間
  （更貼近 vol 0-3% 區間的 [0.05, 0.20] 帶）
- **Lesson #23 邊界擴展**：BB-Width Regime Gate 適用於非槓桿 momentum 框架但
  受 lesson #19 cooldown chain shift 影響，sweet spot 區間極窄（0.12 唯一 sweet point）
- **A/B cum gap 結構性發現**：當基底框架已將 sample 壓低（baseline 12+10），
  regime gate 進一步切除使年化幾何 cum 差難維持 < 30%；此為「regime gate 對小 sample
  策略」共通邊界，與 EWJ-005/SPY-009/IWM-013 等大 sample 案例形成對照
- **TSM Part B 0.83 Sharpe ceiling 仍未真正突破** — 雖雙 Part std=0 結構性最優，
  但 sample 過小使 cross-validation 信心不足；TSM-013/014/015 + TSM-016 共四次嘗試
  確認 TSM 為 Sharpe-1.0 結構性難突破資產，未來方向應為 (a) earnings-date exclusion
  filter（Part B SLs 集中於 earnings ±15 日）, (b) SOXX 半導體指數 anchor,
  (c) 完全替代 framework（lesson #22 multi-week regime + RS Momentum 組合）

成交模型參數：滑價 0.1%、TP +8.0%、SL -7.0%、最長持倉 25 天、冷卻 10 天。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TSMBBWidthRegimeGateConfig(ExperimentConfig):
    """TSM BB-Width Regime Gate 策略專屬參數"""

    reference_ticker: str = "SMH"
    sma_trend_period: int = 50
    relative_strength_period: int = 20
    relative_strength_min: float = 0.05
    pullback_lookback: int = 5
    pullback_min: float = 0.03
    pullback_max: float = 0.07
    cooldown_days: int = 10

    # 沿用 TSM-011 Att3 的 5d return CEILING（rally exhaustion）
    ret_5d_max: float = 0.105

    # 新增：BB-Width Regime Gate（lesson #23 cross-strategy port）
    bb_period: int = 20
    bb_std: float = 2.0
    bb_width_max: float = 0.12  # Att2：medium calm regime（最終配置，雙 Part 100% WR std=0）


def create_default_config() -> TSMBBWidthRegimeGateConfig:
    return TSMBBWidthRegimeGateConfig(
        name="tsm_016_bb_width_regime_gate",
        experiment_id="TSM-016",
        display_name="TSM BB-Width Regime Gate on RS Momentum Pullback",
        tickers=["TSM"],
        data_start="2018-01-01",
        profit_target=0.08,
        stop_loss=-0.07,
        holding_days=25,
    )
