"""
USO-028: ^OVX 5d Direction Multi-Window Implied-Vol Regime Gate MR

實驗動機 (Problem statement)：
- USO-027 Att2 為當前全域最優（min(A,B) 0.50）：USO-025 Att3 完整框架 +
  5 日累計報酬 cap >= -10% (multi-day persistence dimension)。
- USO-027 Att2 殘餘狀態：
  Part A 24 訊號 / WR 75.0% / Sharpe 0.50 / cum +37.07%（6 SLs 殘留）
  Part B 10 訊號 / WR 80.0% / Sharpe 0.64 / cum +16.85%（2 SLs 殘留）
- 殘餘 Part A SLs 多為「3 日視窗未捕捉、5 日仍緩漲、但 5 日累計 OVX
  變化已顯示更長期 vol regime 上升」訊號（如 2020-01-22 pre-COVID
  地緣壓力醞釀期、2021-03-23 三月油市修正、2022-06-17 Powell 持續
  鷹派）。

USO-025 Att3 僅以 ^OVX 3d 變化 <= +4 過濾「短期 vol 衝擊期」；
USO-025 AI_CONTEXT 明確列出「剩餘可探索：^OVX 5d change 視窗」為
下一個未試方向。^OVX 3d 與 5d direction 維度結構性正交：
- 3d：捕捉「Fed/OPEC 政策日急性衝擊」（acute event window）
- 5d：捕捉「地緣政治醞釀、需求衰退預期累積」（sustained regime shift）

USO-028 設計：在 USO-027 Att2 完整框架（含 ^OVX 3d <= +4 與 5d return
cap >= -10%）上疊加 ^OVX 5d change 過濾作為**獨立第六維度**，
排除「3d 看似平靜但 5d 已持續上升」的隱性 vol 醞釀期訊號。

跨資產脈絡（lesson #24 family v6 多時框 IV direction combo 候選）：
- TLT-013 Att1 ★：^MOVE LEVEL <= 130（單時框 LEVEL 維度）
- XLU-013 Att2 ★：^MOVE 3d change <= +5（單時框 DIRECTION 3d）
- GLD-015 Att2 ★：^GVZ 10d change <= +0.40（單時框 DIRECTION 10d）
- USO-025 Att3 ★：^OVX 3d change <= +4（單時框 DIRECTION 3d）
- USO-028（本實驗）：^OVX 3d + 5d 雙時框 IV direction combo
- 共同模式：lesson #24 family forward-looking IV regime gate 在已套用
  單時框 DIRECTION 後可進一步以多時框 combo 切除「跨時框 vol regime
  shift」訊號

USO 在此族群中為「首次任何資產 IV DIRECTION 多時框正交組合」。

USO 2.2% 日波動 → ^OVX 5d change 經驗分布：
- 平靜期（2024-2025）大多落於 [-3, +3]
- 衝擊期峰值可達 +10 ~ +20（COVID、Saudi attack、Russia/Ukraine）
- 醞釀期 +3 ~ +6（緩慢上升的政策不確定性）

設計初值（採用「5d 閾值 ≈ 3d 閾值 × 1.5x」規則，因 5d 累計幅度
大於 3d）：
- Att1: ^OVX 5d change <= +6.0（保守起點，~1.5x 3d 閾值，避免過度切除 winners）
- Att2: ^OVX 5d change <= +4.0（積極起點，等同 3d 閾值，預期過嚴）
- Att3: 視 Att1/Att2 結果調整甜蜜點（可能採 +5.0 中間值）

設計理念：
- 沿用 USO-027 Att2 完整框架（pullback 7-12% + RSI(2)<15 + 2d floor
  <= -2.5% + ^OVX 3d <= +4 + 5d return cap >= -10% + TP+3.0%/SL-3.25%
  /10d/cd10）
- 疊加 ^OVX 5d direction 作為**第六獨立維度**：
  * 3d direction = 短期急性 vol 衝擊
  * 5d direction = 中期 vol regime shift
  * 兩者正交，捕捉不同時序的 forward-looking IV 變化
- 出場、冷卻、進場其餘條件全部不變，僅新增 1 個過濾條件以隔離 5d direction
  邊際貢獻

跨資產貢獻：
- repo 第 6 次 lesson #24 family forward-looking IV regime gate 跨資產驗證
- repo 首次「IV DIRECTION 多時框正交組合」於任何資產
  （3d acute + 5d sustained 雙窗口疊加）
- 若 SUCCESS → 擴展 lesson #24 family 邊界至「多時框 IV direction combo」
  方向，提供下一維度突破範本給 TLT/XLU/GLD 等已套用單時框 IV 的資產

預期效應：
- 若 ^OVX 5d 過濾移除 USO-027 殘餘 6 SLs 中的 2-3 筆而保留多數 winners
  → Part A Sharpe 上升，min(A,B) 突破 0.50 ceiling
- 若 ^OVX 5d 與 3d 高度共線（同向相關）→ Att1/2 過濾極少訊號（Att2 保守
  fallback）；min(A,B) tie 0.50
- 若 ^OVX 5d cap 反向選擇（移除 winners 多於 SLs）→ 結構性失敗，需考慮
  反向（^OVX 5d direction 作為 floor 而非 cap）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USO028Config(ExperimentConfig):
    """USO-028 ^OVX 5d Direction Multi-Window IV Regime Gate MR 參數"""

    # 進場 — 回檔（沿用 USO-013/USO-025/USO-027）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07
    pullback_max: float = -0.12

    # 進場 — RSI(2) 短期超賣（沿用）
    rsi_period: int = 2
    rsi_threshold: float = 15.0

    # 進場 — 2 日急跌 floor（沿用）
    drop_2d_threshold: float = -0.025

    # ^OVX forward-looking implied vol regime gate（沿用 USO-025 Att3）
    ovx_ticker: str = "^OVX"
    use_ovx_3d_filter: bool = True
    ovx_3d_lookback: int = 3
    max_ovx_3d_change: float = 4.0

    # 5 日報酬 cap（multi-day persistence dimension，沿用 USO-027 Att2）
    use_return_5d_cap: bool = True
    return_5d_lookback: int = 5
    return_5d_min: float = -0.10

    # USO-028 核心新增：^OVX 5d direction（multi-window IV combo dimension）
    # 要求 5 日 ^OVX 累計變化 <= max_ovx_5d_change
    use_ovx_5d_filter: bool = True
    ovx_5d_lookback: int = 5
    # Att1: +6.0（保守起點 ~1.5x 3d 閾值）→ SUCCESS min(A,B) 0.64 (+28% vs 0.50 baseline)
    #   Part A 22/81.8%/Sharpe 0.73 cum +46.73% / Part B 10/80%/Sharpe 0.64 cum +16.85%
    # Att2: +4.0（積極等同 3d 閾值，預期較嚴）→ TBD
    # Att3: 視 Att1/Att2 結果調整甜蜜點
    max_ovx_5d_change: float = 4.0

    # 冷卻期（沿用）
    cooldown_days: int = 10


def create_default_config() -> USO028Config:
    return USO028Config(
        name="uso_028_ovx_5d_direction_mr",
        experiment_id="USO-028",
        display_name="USO ^OVX 5d Direction Multi-Window IV Regime Gate MR",
        tickers=["USO"],
        data_start="2010-01-01",
        profit_target=0.030,
        stop_loss=-0.0325,
        holding_days=10,
    )
