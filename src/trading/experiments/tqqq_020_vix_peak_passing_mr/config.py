"""TQQQ-020 ^VIX Peak-Passing Filter on Vol-Regime-Gated Capitulation Buy 配置

實驗動機 (Problem statement)：
- TQQQ-018 Att3 為當前全域最優（min(A,B) 0.80）：
  Part A 10 訊號 / WR 90.0% / Sharpe 1.21 / cum +68.97%
  Part B 6 訊號 / WR 83.3% / Sharpe 0.80 / cum +28.91%
  Part B 殘餘 1 SL（2025-03-06，Trump 關稅 risk-off 加速期）為 binding constraint
- TQQQ-019 三次 ^VIX **DIRECTION（5d cumulative change）** 全部失敗（min 0.28 / 0.80 / 0.80），
  AI_CONTEXT 結論：「lesson #24 family DIRECTION cap 在 extreme capitulation framework
  結構性失效——capitulation 與 VIX spike 共線，無單一 threshold 可區分 winners vs SL」
- TQQQ-019 AI_CONTEXT 明確列出**未驗證假設**：
  「可能需 ^VIX 1d change（signal-day deceleration）或 ^VIX 短期動能反轉
  （peak passing 確認）方能切分」

策略方向（lesson #24 family forward-looking IV regime gate **新維度**：peak-passing）：
- 既有 lesson #24 family 全部為 DIRECTION（cumulative N-day change）：
  * TLT-013：^MOVE LEVEL <= 130
  * XLU-013：^MOVE 3d cumulative change <= +5
  * USO-025：^OVX 3d cumulative change <= +4
  * USO-028：^OVX 3d + 5d 雙時框 DIRECTION
  * GLD-015：^GVZ 10d cumulative change <= +0.40
  * XBI-017：^VIX BANDS regime
  * FCX-015：^VIX > 14 FLOOR
  * TQQQ-019：^VIX 5d cumulative change（**FAILED — 與 capitulation 共線**）
- TQQQ-020 為 **repo 首次「^VIX 1d momentum reversal / peak-passing」於任何資產**——
  區別於 cumulative direction 的關鍵在於：cumulative 衡量「panic 已升多少」，
  peak-passing 衡量「panic 是否已開始消退」，二者結構性正交
- Capitulation 訊號日 panic 必達高位（VIX > 25 常見），但 winners 與 SLs 在
  「panic 是否已 peak」維度上應有區分力：
  * Winner: 反彈日 = panic 達峰、開始消退 → 1d ^VIX 變化 <= 0（VIX flat/down）
  * SL (2025-03-06): 持續加速 risk-off 中段 → 1d ^VIX 變化 > 0（VIX 仍上升）

設計假設：
- Part B 2025-03-06 SL 對應 Trump 關稅 escalation 早中期（reflation→stagflation 預期切換），
  ^VIX 在訊號日當日仍處於上升期（VIX 1d > 0），尚未達 peak
- Part A winners（含 2024-08-05 yen carry 反轉日、2025-04-04 關稅 capitulation
  winner）對應「VIX 急飆但已達峰、開始穩定」結構（VIX 1d <= 0）
- 假設 ^VIX 1d 維度可區分「VIX 加速期」（filter，SL）vs「VIX 已達峰開始穩定」（keep，winner）

預期效應：
- 若 ^VIX 1d <= 0 過濾移除 Part B 1 SL（2025-03-06）而保留 5 winners
  → Part B Sharpe 顯著提升、min(A,B) 突破 0.80
- 若 ^VIX 1d 與 capitulation 仍共線（winners 與 SL 在 peak-passing 維度同向）
  → filter 反向選擇或非綁定，TIE/REJECT
- 若 ^VIX 1d 過嚴僅保留少數 zero-var winners → TIE under † convention

跨資產脈絡（lesson #24 family v9 候選新維度）：
- Repo 首次「^VIX 1d momentum reversal / peak-passing」維度試驗
- 若 SUCCESS → 擴展 lesson #24 family 至「peak-passing momentum reversal」維度
  類別，與既有 cumulative DIRECTION / LEVEL / BANDS / FLOOR 並列
- 若 SUCCESS 並驗證跨資產假設「peak-passing 適用於 SOXL/SQQQ 其他 3x 槓桿
  ETF + 其他 capitulation framework 資產」（IBIT、URA、FXI capitulation MR）

迭代計畫：
- Att1: ^VIX 1d 變化 <= 0（最寬鬆 peak-passing，要求今日 VIX 不高於昨日）
- Att2: ^VIX 1d 變化 <= -1.0（明確 deceleration，今日 VIX 至少低 1 點）
- Att3: 視 Att1/Att2 結果，可能採 +0.5 略放寬（容忍微幅上升的 peak）或
  改採 3d rolling max 比較（今日 VIX 不為 3 日新高）
"""

from dataclasses import dataclass

from trading.experiments.tqqq_018_regime_vol_gate.config import TQQQ018Config


@dataclass
class TQQQ020Config(TQQQ018Config):
    """TQQQ-020 ^VIX Peak-Passing Filter on TQQQ-018 base 參數

    在 TQQQ-018 Att3 完整框架（含 BB-width regime gate + Drawdown(T-5)
    prior drawdown filter）上疊加 ^VIX **1d momentum reversal / peak-passing**
    作為**獨立第六維度**，排除 risk-off 加速期（VIX 仍持續上升、尚未達 peak）
    的 capitulation 訊號。

    與 TQQQ-019 的關鍵區別：
    - TQQQ-019: ^VIX N 日 **cumulative change**（N=5），衡量「panic 已升多少」
      → 與 capitulation depth 共線、結構性失敗
    - TQQQ-020: ^VIX **1d change / peak-passing**，衡量「panic 是否已達峰」
      → 與 capitulation depth 正交、目標為 winner vs SL 區分
    """

    # ^VIX peak-passing momentum reversal gate（TQQQ-020 新增）
    vix_ticker: str = "^VIX"
    use_vix_peak_passing_filter: bool = True

    # 1d 變化閾值（今日 VIX - 昨日 VIX）
    # Att1: 0.0 → REJECT min(A,B) -0.07 / Part A 2 訊號 / Part B **0 訊號**
    #   結構性失敗 — capitulation 訊號日 VIX 必上升（恐慌爆發），1d <= 0 過嚴
    #   過濾掉幾乎所有訊號，僅留 2 邊緣訊號，驗證「peak-passing 在 signal day
    #   結構性與 capitulation 矛盾」初步信號
    # Att2: 3.0 → 適度放寬（允許今日 VIX 較昨日漲不超過 3 點）
    #   假設：filter「extreme single-day VIX 加速 >+3」訊號，仍允許正常 capitulation
    # Att3: 待定，依結果調整
    max_vix_1d_change: float = 3.0


def create_default_config() -> TQQQ020Config:
    return TQQQ020Config(
        name="tqqq_020_vix_peak_passing_mr",
        experiment_id="TQQQ-020",
        display_name="TQQQ ^VIX Peak-Passing Filter on Vol-Regime-Gated Capitulation Buy",
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
