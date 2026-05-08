"""TQQQ-019 ^VIX Direction Filter on Volatility-Regime-Gated Capitulation Buy 配置

實驗動機 (Problem statement)：
- TQQQ-018 Att3 為當前全域最優（min(A,B) 0.80）：
  Part A 10 訊號 / WR 90.0% / Sharpe 1.21 / cum +68.97%（殘餘 1 SL: 2021-09-28
  低 vol regime drift，BB 0.219，結構性無法以 vol regime 過濾）
  Part B 6 訊號 / WR 83.3% / Sharpe 0.80 / cum +28.91%（**1 SL: 2025-03-06**
  Trump 關稅政策不確定性升溫期，^VIX 由 17 飆至 28+ 的 risk-off 加速）
- min(A,B) = Part B 0.80 為 binding constraint
- TQQQ AI_CONTEXT 既有 ^VIX LEVEL 過濾（TQQQ-004，VIX>=25 過嚴失敗，因
  恐慌訊號 VIX 通常<25）；但 ^VIX **DIRECTION**（多日累計變化）作為
  forward-looking risk-off 加速指標**從未在 TQQQ 試驗**，repo 跨資產已
  6 次成功（XLU-013/USO-025/USO-028/GLD-015/XBI-017/FCX-015）

策略方向（lesson #24 family forward-looking IV regime gate 跨資產移植）：
- 既有 lesson #24 family 跨資產驗證序列：
  * TLT-013：^MOVE LEVEL <= 130（單時框 LEVEL 維度）
  * XLU-013：^MOVE 3d change <= +5（單時框 DIRECTION 3d）
  * USO-025：^OVX 3d change <= +4（單時框 DIRECTION 3d）
  * USO-028：^OVX 3d + 5d 雙時框 DIRECTION combo
  * GLD-015：^GVZ 10d change <= +0.40（單時框 DIRECTION 10d）
  * XBI-017：^VIX BANDS exclude mid-range（U-shape regime）
  * FCX-015：^VIX > 14 FLOOR（low-VIX false breakout 過濾）
- TQQQ 為 3x leveraged tech ETF，VIX 上升期波動放大 → ^VIX DIRECTION 應
  具強選擇力於 Part B SLs（risk-off 持續加速期 capitulation reversal 失敗）

設計假設：
- Part B 2025-03-06 SL 對應 Trump 關稅 escalation early-phase，^VIX 已連續
  數日上升（risk-off regime 持續加速期，反彈失敗概率高）
- Part A 倖存的 winners（含 2024-08-05 yen carry 急跌反彈、2025-04-04
  關稅 capitulation winner）為「VIX 急飆但已達峰、開始穩定」結構，^VIX
  3d/5d 變化量應低於持續加速期
- 假設 ^VIX 5d direction CAP 可區分「VIX 加速期」（filter）vs「VIX 已達
  峰開始穩定」（keep），結構性對應 Part B 1 SL vs 5 winners 區分

預期效應：
- 若 ^VIX 5d 過濾移除 Part B 1 SL（2025-03-06）而保留 5 winners
  → Part B 變為 5/5 全勝 std=0 結構性零方差，min(A,B)† = Part A 1.21
  （+51% vs baseline 0.80）
- 若 ^VIX 5d 與 BB-width regime 高度共線 → filter 非綁定，min(A,B) tie 0.80
- 若 ^VIX 5d cap 反向選擇（移除 Part A winners 多於 SL）→ 結構性失敗

跨資產脈絡：
- repo 第 7 次 lesson #24 family forward-looking IV regime gate 跨資產驗證
- repo 首次 ^VIX DIRECTION 變體於 leveraged 槓桿 ETF
- 若 SUCCESS → 擴展 lesson #24 family v8 至「leveraged ETF + IV
  direction」類別，並驗證跨資產假設「^VIX DIRECTION 適用於 SOXL/SQQQ
  其他 3x 槓桿 ETF」（cross-asset hypothesis pending）

迭代計畫：
- Att1: ^VIX 5d change <= +5.0（保守起點，依 XLU-013/USO-025 sweet spot
  範圍）
- Att2: ^VIX 5d change <= +3.0（收緊測試，目標精準命中 2025-03-06 SL）
- Att3: 視 Att1/Att2 結果，可能採 +4.0 中間值或改 3d 短期窗口
"""

from dataclasses import dataclass

from trading.experiments.tqqq_018_regime_vol_gate.config import TQQQ018Config


@dataclass
class TQQQ019Config(TQQQ018Config):
    """TQQQ-019 ^VIX Direction Filter on TQQQ-018 base 參數

    在 TQQQ-018 Att3 完整框架（含 BB-width regime gate + Drawdown(T-5)
    prior drawdown filter）上疊加 ^VIX DIRECTION 作為**獨立第六維度**，
    排除 risk-off 加速期（VIX 持續上升）的訊號。
    """

    # ^VIX forward-looking implied vol DIRECTION gate（TQQQ-019 新增）
    vix_ticker: str = "^VIX"
    use_vix_direction_filter: bool = True
    vix_direction_lookback: int = 5

    # Att1 ★: +5.0（保守起點，依 XLU-013/USO-025 sweet spot 範圍）
    max_vix_direction_change: float = 5.0


def create_default_config() -> TQQQ019Config:
    return TQQQ019Config(
        name="tqqq_019_vix_direction_mr",
        experiment_id="TQQQ-019",
        display_name="TQQQ ^VIX Direction Filter on Vol-Regime-Gated Capitulation Buy",
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
