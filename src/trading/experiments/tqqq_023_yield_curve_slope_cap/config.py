"""TQQQ-023 Yield-Curve-Slope Inflation-Regime-Gated Capitulation Buy 配置

實驗動機 (Problem statement)：
- TQQQ-018 Att3 為當前全域最優（min(A,B) 0.80）：
  Part A 10 訊號 / WR 90.0% / Sharpe 1.21 / cum +68.97%
  Part B 6 訊號 / WR 83.3% / Sharpe 0.80 / cum +28.91%
  Part B 殘餘 1 SL（2025-03-06，Trump 關稅 risk-off 加速期）為 binding constraint
- TQQQ-019/020/021 共 9 次嘗試確認 lesson #24 family 所有 implied vol 維度
  （equity ^VIX + bond ^MOVE + commodity ^OVX/^GVZ）對 TQQQ extreme capitulation
  framework 結構性失效——VIX/MOVE 任何 LEVEL/DIRECTION 變體與 capitulation
  共線或 reverse-selecting
- TQQQ-021 AI_CONTEXT 明確列出**未驗證正交方向**：
  「需考慮非 implied vol 維度（如 cross-asset relative strength、short-term
  momentum reversal of underlying QQQ、yield curve slope velocity 等正交
  macro structural 指標）」
- TQQQ-022（QQQ-SPY cross-asset divergence FLOOR）已測試「cross-asset relative
  strength」維度——三次迭代全 REJECT/TIE，TQQQ-018 框架要求 DD ≤ -15% 的訊號
  天然發生於 broad-market panic 期，QQQ-SPY divergence 結構性脫鉤

策略方向（lesson #24 family v10 跨資產移植 — yield curve slope velocity）：
- TLT-017 為 repo 第一個 yield curve slope velocity 應用：
  ^TYX (30Y) - ^TNX (10Y) 5d slope velocity <= +0.038 在 TLT 上 SUCCESS
  （+551% Part A Sharpe 突破，min(A,B) 從 0.69 提升至 4.49）
- TLT-017 機制：steepening 殖利率曲線（long-end 通膨溢價快速上修）= inflation
  regime onset = 結構性壓制 long-duration assets MR
- TQQQ 雖為 leveraged tech ETF，但同屬 long-duration / risk-on 類別：
  科技股價值高度敏感於長端利率（DCF discount rate），陡峭化 yield curve 對
  科技股估值壓制與對 TLT 壓制機制相同（均為 「inflation premium 上修
  → long-duration 受傷」）
- 2025-03-06 Part B SL 對應 Trump 關稅政策不確定性升溫期，
  「reflation→stagflation 預期切換」事件——yield curve 5d slope velocity
  在此期間預期顯著正向（陡峭化），與 ^MOVE LEVEL/DIRECTION 在 TQQQ 上的
  collinear 失敗模式不同（slope velocity 為**曲線形狀變化率**，非 IV LEVEL/
  DIRECTION）

預期效應（hypothesis）：
- 若 5d slope velocity > +0.038 過濾 Part B 2025-03-06 SL 而保留 5 winners
  → Part B 變為 5/5 全勝 std=0 結構性零方差，依 EWJ-003/SPY-009/DIA-012/
  IWM-013/TLT-014 † 慣例 min(A,B)† = Part A 1.21（+51% vs baseline 0.80）
- 若 yield curve slope 與 capitulation 訊號**結構性正交**（科技股賣壓 ≠
  通膨衝擊），則 filter 對 Part A 16 baseline 訊號預期非綁定（保留多數 winners）
- 若 slope velocity 與 BB-width regime 高度共線 → filter 非綁定，min(A,B) tie 0.80
- 若反向選擇（移除 Part A winners 多於 SL）→ 結構性失敗

跨資產脈絡：
- repo 第 2 次 yield curve slope velocity 應用，**首次跨資產類別移植
  （bond → leveraged tech ETF）**
- TLT-017 為 rate-direct 資產（rates 為唯一 driver），TQQQ-023 為 rate-indirect
  資產（rates 經由 long-duration valuation 機制傳導），這層**間接傳導**為新邊界
- 若 SUCCESS → 擴展 lesson #24 family v10 至「rate-indirect long-duration
  asset class」類別（leveraged tech ETF = TQQQ/QQQ/TECL/SOXL 等）
- 若 FAIL → 確認 yield curve slope velocity 適用邊界 = 「rate-direct 資產」類別，
  其他長 duration 資產需不同 macro structural 指標

迭代計畫（最多三次）：
- Att1: lookback=5d, max_slope_change=+0.038（TLT-017 Att2 sweet spot 直接移植，
  保守起點）
- Att2: 視 Att1 結果調整：若 too lenient（filter 不綁定），收緊至 +0.025；
  若 reverse selection，改用 LEVEL filter（slope <= +0.700 mirror TLT-017 Att3）
- Att3: 視 Att1/Att2 結果，可能改 10d window（capture sustained inflation regime
  rather than acute event）或停用 filter 改測 absolute slope LEVEL
"""

from dataclasses import dataclass

from trading.experiments.tqqq_018_regime_vol_gate.config import TQQQ018Config


@dataclass
class TQQQ023Config(TQQQ018Config):
    """TQQQ-023 Yield-Curve-Slope Filter on TQQQ-018 base 參數

    在 TQQQ-018 Att3 完整框架（含 BB-width regime gate + Drawdown(T-5) prior
    drawdown filter）上疊加 yield curve slope velocity 作為**第六獨立維度**，
    排除「殖利率曲線陡峭化加速期 (inflation regime onset)」的訊號。
    """

    # === Yield curve slope velocity (TQQQ-023 核心新增) ===
    long_yield_ticker: str = "^TYX"  # 30Y Treasury yield
    short_yield_ticker: str = "^TNX"  # 10Y Treasury yield

    # slope_lookback: N 日內 (^TYX - ^TNX) 變化
    # max_slope_change: slope 變化上限（單位：百分點 / percentage points）
    # 意義: 「殖利率曲線在 N 日內 steepening（long-end 通膨溢價擴張）不可超過此值」
    #
    # 迭代紀錄 (3 iterations)：
    # Att1: lookback=5d, max=+0.038 (TLT-017 Att2 sweet spot 直接移植)
    # Att2: 預留依 Att1 結果調整
    # Att3: 預留替代維度 (slope LEVEL or 10d window)
    slope_lookback: int = 5
    max_slope_change: float = 0.038
    use_slope_change_filter: bool = True

    # slope LEVEL filter (備用替代維度，預設關閉)
    use_slope_level_filter: bool = False
    max_slope_level: float = 999.0


def create_default_config() -> TQQQ023Config:
    return TQQQ023Config(
        name="tqqq_023_yield_curve_slope_cap",
        experiment_id="TQQQ-023",
        display_name="TQQQ Yield-Curve-Slope Inflation-Regime-Gated Capitulation Buy",
        tickers=["TQQQ"],
        data_start="2018-06-01",
        part_a_start="2019-01-01",
        part_a_end="2023-12-31",
        part_b_start="2024-01-01",
        part_b_end="2025-12-31",
        part_c_start="2026-01-01",
        part_c_end="",
        profit_target=0.07,
        stop_loss=-0.08,
        holding_days=10,
    )
