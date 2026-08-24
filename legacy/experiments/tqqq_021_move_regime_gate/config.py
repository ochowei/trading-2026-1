"""TQQQ-021 ^MOVE Bond-Vol LEVEL Regime Gate on Vol-Regime-Gated Capitulation Buy 配置

實驗動機 (Problem statement)：
- TQQQ-018 Att3 為當前全域最優（min(A,B) 0.80）：
  Part A 10 訊號 / WR 90.0% / Sharpe 1.21 / cum +68.97%
  Part B 6 訊號 / WR 83.3% / Sharpe 0.80 / cum +28.91%
  Part B 殘餘 1 SL（2025-03-06，Trump 關稅 risk-off 加速期）為 binding constraint
- TQQQ-019（^VIX 5d cumulative DIRECTION）+ TQQQ-020（^VIX 1d momentum reversal /
  peak-passing）共 6 次嘗試全部 REJECT/TIE，AI_CONTEXT 整合結論：
  「lesson #24 family DIRECTION 維度（cumulative or 1d）對 extreme capitulation
  framework 結構性失效——VIX 任何 DIRECTION 變體與 capitulation 共線」
- TQQQ-019 / TQQQ-020 AI_CONTEXT 明確列出**未驗證假設**：
  「可能需 ^VIX **LEVEL** 維度（如 ^VIX < 50 absolute cap 防 mid-panic 進場）或
  **VIX-VXN cross-index divergence** 或**完全替代 framework**」

策略方向（lesson #24 family forward-looking IV regime gate **新跨資產維度**：
^MOVE bond vol LEVEL）：
- 既有 lesson #24 family ^VIX 系列已盡（TQQQ-019/020 拒絕 ^VIX DIRECTION）
- 既有 lesson #24 family ^MOVE 系列：
  * TLT-013：^MOVE LEVEL <= 130（rate-direct ETF）★ 成功
  * XLU-013：^MOVE 3d cumulative DIRECTION <= +5（rate-indirect utility ETF）★ 成功
- TQQQ-021 為 **repo 首次 ^MOVE（bond vol）於 leveraged tech ETF / 任何 equity
  asset 之外的 rate-driven asset class**——核心假設：
  * TQQQ 雖為 3x leveraged QQQ（科技股），但 2022 ~ 2025 年的 capitulation
    SLs 多由「利率衝擊 / 政策不確定性」驅動（而非純粹股市恐慌）
  * 2025-03-06 Trump 關稅 risk-off 為「reflation→stagflation 預期切換」事件，
    rate uncertainty（^MOVE spike）是核心 driver，^VIX 反而相對溫和
  * ^MOVE 與 ^VIX 結構性正交：^MOVE 衡量「30 天 ATM 國債選擇權隱含波動」，
    與 capitulation 框架（純股市 drawdown + RSI + Volume）無共線基礎
- 假設：^MOVE LEVEL CAP 可區分「pure equity capitulation winners」（^MOVE
  moderate, < threshold）vs 「rate-driven panic SLs」（^MOVE elevated, >= threshold）

設計假設：
- Part B 2025-03-06 SL 對應關稅 escalation 早中期，當日 ^MOVE 預期落於
  elevated zone（rate uncertainty 高）
- Part A winners 多為純粹科技股恐慌反彈（2020 COVID、2022 tech bear、2024-2025
  零星修正），當日 ^MOVE 預期落於 calm/moderate zone
- ^MOVE LEVEL CAP（如 <= 130）若可同時：
  (a) 過濾 Part B 2025-03-06 SL（^MOVE > 130 elevated）
  (b) 保留多數 Part A winners（^MOVE <= 130 moderate）
  → min(A,B) 突破 0.80

預期效應：
- 若 ^MOVE LEVEL <= 130 過濾 Part B 2025-03-06 SL 而保留 5+ winners
  → Part B Sharpe 顯著提升、min(A,B) 突破 0.80
- 若 ^MOVE 與 capitulation 共線（多數 capitulation 訊號 ^MOVE 皆高）→ TIE/REJECT
- 若 ^MOVE LEVEL 對 2025-03-06 非綁定（當日 ^MOVE 不夠高）→ 改試 ^MOVE DIRECTION

跨資產脈絡（lesson #24 family v10 候選新維度）：
- Repo 首次 ^MOVE（bond vol）於 leveraged tech ETF
- 若 SUCCESS → 擴展 lesson #24 family ^MOVE 適用邊界自「rate-direct/indirect ETF」
  至「rate-shock-sensitive 槓桿股票 ETF」
- 若 SUCCESS 並驗證跨資產假設「rate-driven panic SLs 在 ^MOVE 維度有區分力」
  → 適用於 SOXL/SQQQ 其他 3x 槓桿 ETF

迭代計畫：
- Att1: ^MOVE LEVEL <= 130（TLT-013 sweet spot 直接移植）
- Att2: 視 Att1 結果，可能採 LEVEL <= 110（更嚴）或改試 3d DIRECTION <= +5
  （XLU-013 sweet spot）
- Att3: 視前兩次結果，採 LEVEL+DIRECTION 雙維度組合或 alternative threshold
"""

from dataclasses import dataclass

from trading.experiments.tqqq_018_regime_vol_gate.config import TQQQ018Config


@dataclass
class TQQQ021Config(TQQQ018Config):
    """TQQQ-021 ^MOVE LEVEL Filter on TQQQ-018 base 參數

    在 TQQQ-018 Att3 完整框架（含 BB-width regime gate + Drawdown(T-5)
    prior drawdown filter）上疊加 ^MOVE **LEVEL** 作為**獨立第六維度**，
    排除 rate-shock-driven panic 期間（^MOVE elevated）的 capitulation 訊號。

    與 TQQQ-019/020 的關鍵區別：
    - TQQQ-019/020: ^VIX **DIRECTION**（cumulative 5d / 1d peak-passing）
      → 與 capitulation 結構共線、結構性失敗
    - TQQQ-021: ^MOVE **LEVEL**，衡量「rate uncertainty 絕對水準」
      → 與 equity-only capitulation 結構正交，目標為 rate-driven SL 過濾
    """

    # ^MOVE LEVEL gate（TQQQ-021 新增）
    move_ticker: str = "^MOVE"
    use_move_level_filter: bool = False

    # ^MOVE LEVEL 上限（今日 ^MOVE 收盤）
    # Att1: 130（TLT-013 sweet spot 移植）→ TIE baseline 0.80，所有 16 baseline
    #   訊號當日 ^MOVE <= 130，LEVEL cap 完全非綁定 — TQQQ extreme capitulation
    #   signals 結構上不伴隨 ^MOVE > 130 extreme rate panic（^MOVE 130+ 罕見：
    #   2022-10 BoE pension crisis、2023-03 SVB；TQQQ -15% drawdown 多由純科技
    #   股賣壓觸發、與 bond vol extreme 不重合）
    # 整合結論：^MOVE LEVEL 維度對 TQQQ extreme capitulation framework 結構
    #   性非綁定（rate vol extreme 與 equity capitulation 不共生），LEVEL 路線
    #   被 Att1 一次否決
    max_move_level: float = 999.0

    # ^MOVE DIRECTION（Att2/Att3 啟用）
    use_move_direction_filter: bool = True
    # Att2: lookback=3, max=+5.0（XLU-013 sweet spot 直接移植）→ REJECT min 0.66
    #   Part A 10→4（WR 100% 但 std=0、Sharpe 0.00 zero-var 退化、過濾 6 winners）
    #   Part B 6→5（過濾 2025-02-27 winner，2025-03-06 SL 之 ^MOVE 3d change
    #   < +5 完全非綁定）— **reverse selection**：移除 winner 而保留 SL
    # Att3 ★ FINAL（saved config）: lookback=5, max=+8.0 → REJECT min 0.66
    #   Part A 10→5（4W/1L Sharpe 0.66，cooldown chain shift 引入 2021-09-28 SL）
    #   Part B 6→4（**成功過濾 2025-03-06 SL** ✓ 但同步誤殺 2025-02-27 winner，
    #   std=0 Sharpe 0.00 zero-var）— 5d 維度雖能捕捉 2025-03-06 rate-shock
    #   特徵但同時誤殺結構相似的 winner + Part A heavy attrition
    # **整合結論（lesson #24 family v9 boundary expansion，repo 首次 ^MOVE
    # 於 leveraged tech ETF 試驗失敗）**：
    # 1. ^MOVE LEVEL 維度與 TQQQ extreme capitulation 結構性非綁定（Att1）
    # 2. ^MOVE DIRECTION 維度（3d 或 5d）對 2025-03-06 SL 部分綁定但同時
    #    誤殺結構相似 winners（Att2/Att3 reverse selection）
    # 3. ^MOVE family（LEVEL + DIRECTION）整體與 ^VIX family（TQQQ-019/020）
    #    同樣對 TQQQ extreme capitulation framework 結構性失效
    # 4. 整體 lesson #24 family v9 適用邊界精煉：所有 implied vol 維度
    #    （equity ^VIX + bond ^MOVE + commodity ^OVX/^GVZ）對「-15% drawdown
    #    extreme capitulation framework」皆結構性與 capitulation 共線或
    #    reverse-selecting，需考慮非 implied vol 維度（如 cross-asset
    #    relative strength、short-term momentum reversal of underlying QQQ、
    #    yield curve slope velocity 等正交 macro structural 指標）
    move_direction_lookback: int = 5
    max_move_direction_change: float = 8.0


def create_default_config() -> TQQQ021Config:
    return TQQQ021Config(
        name="tqqq_021_move_regime_gate",
        experiment_id="TQQQ-021",
        display_name="TQQQ ^MOVE Bond-Vol LEVEL Regime Gate on Vol-Regime-Gated Capitulation Buy",
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
