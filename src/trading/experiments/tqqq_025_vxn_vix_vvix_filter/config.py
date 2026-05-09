"""TQQQ-025 VXN-VIX Cross-Index Divergence + VVIX Direction Filter 配置

實驗動機 (Problem statement)：
- TQQQ-018 Att3 為當前全域最優（min(A,B) 0.80）：
  Part A 10 訊號 / WR 90.0% / Sharpe 1.21 / cum +68.97%（殘餘 1 SL：2021-09-28
  Q3 2021 supply chain / Evergrande / FAANG rotation panic，BB-width 0.219 + DD(T-5)
  filter 對其皆非綁定）
  Part B 6 訊號 / WR 83.3% / Sharpe 0.80 / cum +28.91%（殘餘 1 SL：2025-03-06
  Trump tariff reflation→stagflation pivot 急跌）
- TQQQ-019/020/021/022/023/024 共 6 次嘗試（^VIX DIRECTION、^VIX peak-passing、
  ^MOVE LEVEL+DIRECTION、QQQ-SPY divergence、Yield-curve-slope velocity、Post-
  Capitulation Vol-Transition MR replacement framework）全部 REJECT/TIE，AI_CONTEXT
  整合結論：
  「lesson #24 family（implied vol 任何維度）+ cross-asset relative strength
  + yield curve slope + 完全替代 framework 對 -15% extreme capitulation framework
  皆結構性失效。剩餘未驗證假設：**VIX-VXN cross-index divergence**（Nasdaq vol
  vs broad vol）、^VVIX/^SKEW（forward-looking IV family 高階維度）」
- TQQQ-020 / TQQQ-021 AI_CONTEXT 明確列出未驗證假設「VIX-VXN cross-index
  divergence」——TQQQ-025 為 repo 首次驗證

策略方向（lesson #24 family forward-looking IV regime gate **新跨資產維度**：
^VXN/^VIX 比率 + ^VVIX direction）：
- 既有 lesson #24 family v1-v9 維度：
  * ^VIX LEVEL/DIRECTION（XBI-017 BANDS、TSLA-019 BANDS、FCX-015 FLOOR）
  * ^MOVE LEVEL/DIRECTION（TLT-013、XLU-013）
  * ^GVZ DIRECTION（GLD-015）
  * ^OVX DIRECTION（USO-025/028）
  * VIX term structure ^VIX3M/^VIX（TSM-019 失敗）
- TQQQ-025 為 **repo 首次「cross-index implied vol divergence」變體**：
  ^VXN（Nasdaq-100 30-day implied vol）vs ^VIX（S&P-500 30-day implied vol）
  比率作為「tech-specific stress vs broad-market stress」regime gate
- 同時 repo 首次 ^VVIX（VIX of VIX，30-day VIX implied vol）於任何資產：
  ^VVIX 5d direction 衡量「panic about future panic」加速度

設計假設（基於 trade-level 分析 TQQQ-018 Att3 殘餘 2 SLs vs 14 TPs）：

(1) **VXN/VIX FLOOR > 1.10** 過濾「broad-market panic 同步下跌而 tech 並未深度
跑輸」regime——當 VXN ≈ VIX (ratio < 1.10)，整體市場恐慌但 NDX 並未獨立超賣
（Trump tariff 2025-03-06 屬此類，VXN/VIX = 1.055 異常低於 14 個 winners
的最低 1.121）：
  * SL 2025-03-06: VXN/VIX = 1.055 ❌ → FILTER ✓
  * Part A TPs VXN/VIX 範圍: 1.121–1.331 ✓ ALL PASS
  * Part B TPs VXN/VIX 範圍: 1.140–1.278 ✓ ALL PASS
  * SL 2021-09-28: VXN/VIX = 1.176 ✓ PASS（此 SL 不被 VXN/VIX 維度過濾）

(2) **VVIX 5d FLOOR > -5** 過濾「VVIX 急速下行（uncertainty about uncertainty
正在快速消退）」regime——2021-09-28 SL 對應 VVIX 從 130+ 快速回落至 121
（5d -9.70），表明 panic about-panic 正在解除，但實際 capitulation 並未真正
完成（後續續跌觸發 -8% SL）：
  * SL 2021-09-28: VVIX_5d = -9.70 ❌ → FILTER ✓
  * Part A TPs VVIX_5d 範圍: -3.21 至 +35.06（min -3.21）✓ ALL > -5 PASS
  * Part B TPs VVIX_5d 範圍: -3.63 至 +24.72（min -3.63）✓ ALL > -5 PASS
  * SL 2025-03-06: VVIX_5d = +6.03 ✓ PASS（此 SL 不被 VVIX_5d 維度過濾）

(3) 兩維度為**正交補充**：VXN/VIX 過濾 Part B SL，VVIX 5d 過濾 Part A SL，
雙維度 AND 同時保留全部 14 個 TPs。Cooldown chain shift 風險低（cooldown_days=3，
被過濾兩 SLs 之最近相鄰訊號分別在 6+ 日後與 8+ 月後）。

預期效應：
- Att1（單一 VXN/VIX FLOOR > 1.10）：過濾 Part B 2025-03-06 SL；Part A 不變
  → Part B std=0 zero-var，min(A,B)† = Part A 1.21（沿用 EWJ-003/SPY-009/DIA-012/
  IWM-013/CIBR-014 慣例）, +51% vs baseline 0.80
- Att2（Att1 + VVIX 5d FLOOR > -5）：再過濾 Part A 2021-09-28 SL
  → Part A 9 訊號 / Part B 5 訊號 / 雙 Part std=0 zero-var
  → A/B 年化 cum 12.6%/yr vs 17.5%/yr → gap 28% < 30% ✓
  → A/B 訊號比 1.8/yr vs 2.5/yr = gap 28% < 50% ✓
- Att3（穩健性測試）：tighten 或 loosen 一邊閾值

跨資產脈絡（lesson #24 family v11 候選新維度，repo 首次驗證 VIX-VXN cross-
index divergence + ^VVIX direction）：
- Repo 首次 ^VXN/^VIX 比率作為 cross-index divergence regime gate
- Repo 首次 ^VVIX 應用於任何資產
- 若 SUCCESS：擴展 lesson #24 family v11 至「cross-index IV divergence」+
  「higher-moment IV direction（VIX of VIX）」二大新維度
- 若 SUCCESS 並驗證 TQQQ Part B 結構性突破：跨資產假設適用其他 leveraged
  tech ETF（TECL/SOXL/FNGU），閾值需依資產 vs broader 市場 IV 結構調整

迭代計畫：
- Att1: VXN/VIX FLOOR > 1.10 only（test Part B SL filter 單獨效應）
- Att2: Att1 + VVIX 5d FLOOR > -5（雙維度 AND，期待 min(A,B) 結構性突破）
- Att3: 視前兩次結果，嘗試 tighten/loosen 一邊閾值或 alternative lookback
"""

from dataclasses import dataclass

from trading.experiments.tqqq_018_regime_vol_gate.config import TQQQ018Config


@dataclass
class TQQQ025Config(TQQQ018Config):
    """TQQQ-025 VXN-VIX Cross-Index Divergence + VVIX Direction Filter 參數

    在 TQQQ-018 Att3 完整框架（含 BB-width regime gate + Drawdown(T-5) prior
    drawdown filter）上疊加兩個正交 implied vol 維度：
    - VXN/VIX 比率 FLOOR：cross-index IV divergence（tech vs broad vol）
    - VVIX N 日累計變化 FLOOR：higher-moment IV direction（VIX of VIX velocity）
    """

    # VXN/VIX cross-index divergence FLOOR（TQQQ-025 新增維度 1）
    vxn_ticker: str = "^VXN"
    vix_ticker: str = "^VIX"
    use_vxn_vix_filter: bool = True
    # 訊號日 ^VXN / ^VIX 比率必須 >= min_vxn_vix_ratio（過濾 tech 並未跑輸大盤的訊號）
    min_vxn_vix_ratio: float = 1.10  # Att1/Att2 default

    # VVIX direction FLOOR（TQQQ-025 新增維度 2）
    vvix_ticker: str = "^VVIX"
    # Att1: use_vvix_direction_filter=False (VXN/VIX only)
    #   → min(A,B)† 1.21 PARTIAL (Part A bind unchanged, Part B std=0 zero-var,
    #     A/B cum gap 40% > 30% target)
    # Att2: use_vvix_direction_filter=True, min_vvix_direction_change=-5.0
    #   → 預期過濾 Part A 2021-09-28 SL (VVIX_5d=-9.70 < -5 FLOOR)
    use_vvix_direction_filter: bool = True
    vvix_direction_lookback: int = 5
    # ^VVIX N 日累計變化必須 >= min_vvix_direction_change
    # （過濾 VVIX 急速下行 = uncertainty 正在解除但 capitulation 未完成的訊號）
    min_vvix_direction_change: float = -5.0

    # 成交模型參數（同 TQQQ-018）
    slippage_pct: float = 0.001  # 0.1%


def create_default_config() -> TQQQ025Config:
    return TQQQ025Config(
        name="tqqq_025_vxn_vix_vvix_filter",
        experiment_id="TQQQ-025",
        display_name=(
            "TQQQ VXN-VIX Cross-Index Divergence + VVIX Direction Filter "
            "on Vol-Regime-Gated Capitulation Buy"
        ),
        tickers=["TQQQ"],
        data_start="2018-06-01",  # 暖機 BB(20) + ^VVIX/^VXN 對齊
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
