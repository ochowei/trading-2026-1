"""
TLT HYG Credit Divergence Regime-Gated MR (TLT-015)

實驗動機：
- TLT-014 Att3 為當前全域最優（min(A,B)† 0.69，Part A Sharpe 0.69 / Part B std=0），
  但 A/B 累計差距 37% > 30% 目標未達標（Part A +6.56% vs Part B +10.38%）。
  Part A 殘餘 1 個 expiry loss（2021-01-06 -2.38%，Q1 reflation regime 殘餘 noise），
  TLT-014 Att2 嘗試加嚴 TLT-SPY threshold -4%→-3% 反向誤刪 winners 失敗。
- TLT-014 Att3 已驗證「TLT vs SPY 跨資產 divergence」為有效 regime classifier，
  但 SPY 為 equity benchmark，捕捉「reflation/risk-on equity regime」。
  Q1 2021 reflation 階段不僅 SPY 上漲，**HYG（高收益債）亦因 credit spread 收窄
  跑贏 TLT**，此為**信用風險偏好（credit-on）regime**訊號。

嘗試方向（repo 首次：HYG 高收益債作為跨資產 divergence 過濾器於任何資產）：
**TLT vs HYG 多週期報酬差過濾**。
核心思想：
- HYG (iShares iBoxx $ High Yield Corporate Bond ETF) 兼具 duration risk + credit risk
  雙因子，與 TLT（純 duration risk）形成「相同 duration 暴露但加入信用維度」的對比。
- credit-on regime（risk-on）：HYG 跑贏 TLT 顯著（信用利差收窄主導 + duration 同步弱）。
  此 regime 中 TLT MR 結構性失效（因為 reflation 期殖利率持續上升）。
- credit-off regime（risk-off / flight-to-safety）：TLT 跑贏 HYG 顯著（duration 上漲
  + 信用利差擴張使 HYG 雙重壓力）。此 regime 中 TLT MR 訊號通常為健康反彈。
- HYG-TLT divergence 與 SPY-TLT divergence **正交於 credit dimension**：
  - SPY-TLT 捕捉「股票 vs 債券」資產類別 risk-on
  - HYG-TLT 捕捉「信用利差」變化（純粹固定收益內 credit pricing）
  - 信用利差為 forward-looking 經濟先行指標（HY spread 通常領先 SPY 反映 credit cycle）

與 TLT-008 IEF pair 的關鍵區別：
- TLT-008 失敗根因：TLT vs IEF 為「同 duration 不同 maturity」機械性 pair，
  duration sensitivity ratio 固定（TLT ~2.4x IEF），TLT pullback 時 IEF 必然
  同方向（mechanical），無 cross-asset regime 區分力
- TLT-015 HYG-TLT：HYG 含 credit risk **獨立因子**，TLT pullback 時 HYG 表現
  取決於 credit cycle（risk-on：HYG 反彈快；risk-off：HYG 比 TLT 跌得更深）。
  **不是機械性 pair，而是 credit regime classifier**

與 TLT-014 SPY divergence 的差異：
- TLT-014 SPY-TLT 捕捉「reflation 中 equity 大漲、bond 大跌」的 regime，但
  Q1 2021 期間 SPY +9% / TLT -8% 確實被 -4% threshold 過濾。然而：
  - 2021-01-06 SL 訊號：SPY 20d return 約 +5%、TLT 20d return 約 -5%，
    Rel_Return_20d ≈ -10%，被 TLT-SPY -4% 過濾——但 cooldown chain shift 重新引入
- 假設：HYG 作為**信用市場前瞻指標**，可能在 Q1 2021 顯示 HYG 跑贏 TLT 更大幅度
  （HYG 因 credit-on 雙重提振：duration 弱但 credit 強），此 regime 可被 HYG-TLT
  threshold 捕捉而 TLT-SPY 漏網
- 預期 HYG-TLT divergence 為 TLT-SPY divergence 的**互補維度**，疊加可進一步過濾
  Part A 殘餘 expiry loss

迭代結果（三次迭代全部 FAIL / TIE vs TLT-014 Att3 baseline min(A,B)† 0.69）：
- Att1 (credit_lookback=20, max_credit_outperformance=+5%)：
    Part A 5 訊號 / WR 80% / Sharpe **0.69** cum +6.56% / Part B 4/100% std=0/Sharpe 0.00 cum +10.38%
    / min(A,B)† **0.69 TIE baseline** — HYG-TLT 20d divergence < +5% 對 TLT-014 Att3 全部 5+4 訊號
    皆滿足，filter 完全 non-binding，與 TLT-014 Att3 結果完全相同。

- Att2 (credit_lookback=20, max_credit_outperformance=+2%)：
    Part A 2 訊號 / WR 100% std=0 / Sharpe 0.00 cum +5.06%（過濾 2020-11-09 TP HYG-TLT=+3.74%、
    2021-01-06 SL +2.72%、2021-09-27 expiry +2.11%；保留 2021-08-11 TP -0.37%、2022-02-07 TP -0.08%）
    / Part B 3 訊號 / WR 100% std=0 / Sharpe 0.00 cum +7.69%（**誤刪 2024-11-15 TP HYG-TLT=+3.50%**，
    Part B 4→3 winners）/ min(A,B)† **0.00 / Part A zero-var; REJECT**：
    threshold +2% 過嚴，雙 zero-var 結構但 Part B 樣本崩潰 (4→3) 與 TLT-014 Att2 同模式 REJECT。

- Att3 (credit_lookback=10, max_credit_outperformance=+3%)：
    Part A 4 訊號 / WR **75%** / Sharpe **0.50** cum +3.96%（**過濾 2020-11-09 TP HYG-TLT 10d=+4.57%
    但保留 2021-01-06 SL HYG-TLT 10d=+3.13% — filter 方向反向：移除 winner 而非 loser**）/
    Part B 3/100% std=0/Sharpe 0.00 cum +7.69%（同 Att2 過濾 2024-11-15 winner）/
    min(A,B)† **0.50 REJECT (-28% vs baseline 0.69)**。

**核心發現（cross-asset divergence regime gate orthogonality 失敗）**：
1. **HYG-TLT divergence 對 2021-01-06 SL 無 selectivity**：
   TLT-014 Att3 殘餘 1 個 Part A SL（2021-01-06，-2.38%）的 HYG-TLT 多週期 divergence 為
   5d=+2.48% / 10d=+3.13% / 20d=+2.72%——與多個 Part A/B winners 重疊（2020-11-09 TP
   HYG-TLT 20d=+3.74% > LOSER 的 +2.72%；2025-03-27 TP 20d=+1.57% 等）。任何 threshold
   無法 cleanly 分離 SL 與 winners。
2. **HYG-TLT 與 SPY-TLT 高度相關（非正交）**：
   假設 HYG（雙因子：duration + credit）為 TLT（純 duration）的 credit-orthogonal 互補維度，
   實際資料顯示 2021-01-06 reflation regime 中 HYG-TLT 訊號方向與 SPY-TLT 相同（皆顯示
   risk-on），但**幅度不足以區分 winner vs loser**。SPY-TLT divergence 的 cooldown chain shift
   結構（過濾深 SLs 但保留淺 expiry）已榨取 TLT 自 cross-asset 維度的 selectivity 上限。
3. **跨資產規則更新**：cross-asset divergence regime gate 在已套用一個 cross-asset 維度
   後（TLT-SPY）疊加第二個 cross-asset 維度（HYG-TLT）為**結構性冗餘**——多個 risk-on/off
   benchmarks（SPY/HYG/LQD）在 reflation regime 中同步反映同一 macro factor，無新增
   selectivity。**新規則**：cross-asset divergence regime gate 應限定為**單一最強 anchor**，
   疊加多個 anchor 為過擬合 + 訊號樣本崩潰風險。
4. **與 TLT-008（IEF pair）的失敗區隔**：TLT-008 失敗於「same-asset-class 機械性 pair」；
   TLT-015 失敗於「cross-asset divergence stacking」——前者結構性無 regime 區分力，後者
   結構性與已存在 anchor 相關性過高。兩者共同精煉 TLT cross-asset filter 適用邊界。
5. **未來方向（pending）**：突破 TLT 0.69 ceiling 需引入**真正正交維度**：
   (a) 殖利率曲線陡峭化指標（^TYX - ^TNX 30Y-10Y slope）forward-looking 通膨預期
   (b) DXY 美元指數（FX 維度，與 equity/credit benchmarks 不同 macro factor）
   (c) TIPS-Treasury breakeven inflation rate（直接捕捉通膨預期）
   2021-01-06 reflation regime 主要由「fiscal stimulus 預期」驅動而非單純 credit cycle，
   需 inflation-anchored 指標方能 cleanly 區分。

最終配置：Att3（credit_lookback=10, max_credit_outperformance=+3%）為最後迭代，
       documenting 結構性失敗。TLT-014 Att3 仍為 TLT 全域最優。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class TLT015Config(ExperimentConfig):
    """TLT-015 HYG Credit Cross-Asset Divergence Regime-Gated MR 參數"""

    # 回檔範圍進場（同 TLT-014 Att3）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.03
    pullback_upper: float = -0.07

    # Williams %R（同 TLT-014 Att3）
    wr_period: int = 10
    wr_threshold: float = -80.0

    # 收盤位置過濾（同 TLT-014 Att3）
    close_position_threshold: float = 0.4

    # BB-width regime gate（同 TLT-014 Att3）
    bb_period: int = 20
    bb_std: float = 2.0
    max_bb_width_ratio: float = 0.05

    # ^MOVE forward-looking implied vol regime gate（同 TLT-014 Att3）
    move_ticker: str = "^MOVE"
    max_move_level: float = 130.0

    # TLT-SPY cross-asset divergence regime gate（同 TLT-014 Att3）
    benchmark_ticker: str = "SPY"
    divergence_lookback: int = 20
    min_relative_return: float = -0.04

    # HYG credit cross-asset divergence regime gate（TLT-015 核心新增）
    credit_ticker: str = "HYG"
    credit_lookback: int = 20  # N 日報酬差距
    # max_credit_outperformance：HYG N 日報酬 - TLT N 日報酬 <= 此值
    # 即「HYG 不可比 TLT 跑贏超過此值」（過濾 credit-on regime）
    max_credit_outperformance: float = 0.02

    # 冷卻期
    cooldown_days: int = 7


def create_default_config() -> TLT015Config:
    return TLT015Config(
        name="tlt_015_hyg_credit_divergence_mr",
        experiment_id="TLT-015",
        display_name="TLT HYG Credit Divergence Regime-Gated MR",
        tickers=["TLT"],
        data_start="2018-01-01",
        profit_target=0.025,
        stop_loss=-0.035,
        holding_days=20,
    )
