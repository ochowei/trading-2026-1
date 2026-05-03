"""
USO ^OVX Implied-Volatility Forward-Looking Regime-Gated MR (USO-025)

實驗動機：
- USO-013 為當前全域最優（min(A,B) Sharpe 0.26，Part A 0.26 / Part B 0.82）
- USO-014~USO-024 共 33 次純技術面濾波器嘗試全部失敗，AI_CONTEXT 明示
  "突破 USO-013 結構性上限需跨框架創新（事件驅動模型、非對稱持倉、流量分析等）"
- 殘留問題：Part A 35 訊號中 12 筆 SL，集中於 OPEC+ 政策與地緣政治衝擊日
- USO-022 已證明 RSI hook divergence 失效（油價 event-driven 驅動），驗證此資產
  必須引入「外部事件 regime」維度而非繼續精煉技術面

跨資產背景（lesson #24 v2 候選）：
- TLT-013（2026-05-01）以 ^MOVE LEVEL cap 首次突破 TLT 結構性 0.12 ceiling（+17%）
- XLU-013（2026-05-02）以 ^MOVE 3d change DIRECTION filter 突破 XLU 0.75 ceiling
  （+112%, min 0.75→1.59），首次發現 implied vol DIRECTION 維度與 LEVEL 維度正交
- GLD-015（2026-05-02）以 ^GVZ 10d change DIRECTION filter 突破 GLD 0.49 ceiling
  （+55%），第 3 次跨資產驗證 + commodity-safe-haven 類別 DIRECTION 10d binding
- 上述三案例證實：implied vol derivative 是 backward-looking regime gate 飽和後的
  下一維度（cross_asset_lessons.md lesson #24）

USO-013 過去 OVX 嘗試的紀錄（AI_CONTEXT 已記載）：
- "OVX（原油波動率指數）過濾（已驗證 Part B 損失日 OVX 在正常水位 ~35，無法區分
  好壞訊號）" — **這是 LEVEL-only 檢查**
- USO-025 完全不嘗試 LEVEL cap，直接套用 lesson #24 v2 的 DIRECTION 維度

設計理念：
- 沿用 USO-013 完整框架（pullback 7-12% + RSI(2)<15 + 2日跌幅<=-2.5% +
  TP+3.0%/SL-3.25%/10d/cd10）
- 疊加 ^OVX 3d change <= max_ovx_change 作為**獨立第四維度過濾**
- 假設：當 OVX 3 日內快速上升（>+5），表示市場對未來油價波動恐慌正在升高，
  通常伴隨 OPEC+ 政策不確定性 / 地緣政治事件 / 庫存衝擊；USO MR 訊號落於此
  regime 容易被續跌覆蓋（V-bounce 失敗）
- 出場、冷卻、進場全部不變，僅新增 1 個過濾條件以隔離 ^OVX DIRECTION 邊際貢獻

Cross-asset 比較：
- TLT-013 (^MOVE LEVEL)：rate-driven 直接耦合，LEVEL 維度 binding
- XLU-013 (^MOVE 3d DIRECTION)：rate-driven 間接（utility flow），DIRECTION binding
- GLD-015 (^GVZ 10d DIRECTION)：commodity safe-haven，10d 長窗口 binding
- USO-025 (^OVX 3d DIRECTION)：commodity event-driven（油），預期 3d 短窗口 binding
  （因油的事件衝擊通常 1-3 日反映於 implied vol，而非 10d 慢累積）

Att1: max_ovx_change=+5.0（直接移植 XLU-013 sweet spot）
Att2/Att3: 視結果調整窗口（5d）或閾值（+3.0/+7.0）
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class USO025Config(ExperimentConfig):
    """USO-025 ^OVX Implied-Vol Regime-Gated MR 參數"""

    # 進場 — 回檔（同 USO-013）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.07  # 回檔 >= 7%
    pullback_max: float = -0.12  # 回檔 <= 12%

    # 進場 — RSI(2) 短期超賣（同 USO-013）
    rsi_period: int = 2
    rsi_threshold: float = 15.0

    # 進場 — 2 日急跌（同 USO-013）
    drop_2d_threshold: float = -0.025

    # ^OVX forward-looking implied vol regime gate（USO-025 核心新增）
    ovx_ticker: str = "^OVX"
    # ^OVX direction filter — N 日 absolute change <= max_ovx_change
    # 移植自 XLU-013 Att2/Att3（DIRECTION binding case）
    use_ovx_direction_filter: bool = True
    ovx_direction_lookback: int = 3
    max_ovx_change: float = 5.0

    # 冷卻期（同 USO-013）
    cooldown_days: int = 10


def create_default_config() -> USO025Config:
    return USO025Config(
        name="uso_025_ovx_implied_vol_mr",
        experiment_id="USO-025",
        display_name="USO ^OVX Implied-Vol DIRECTION Regime-Gated MR",
        tickers=["USO"],
        data_start="2010-01-01",
        # 沿用 USO-013 出場
        profit_target=0.030,
        stop_loss=-0.0325,
        holding_days=10,
    )
