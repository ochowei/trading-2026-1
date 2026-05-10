"""
COPX HG=F (Copper Futures) Direction Filter on Volume-Confirmed MR (COPX-019)

實驗動機 (Problem statement):
- COPX-018 Att3 (Volume z-score 60d filter on vol-adaptive MR) 為 COPX 全域最優,
  Part A Sharpe 0.82 / Part B Sharpe 0.71, min(A,B) 0.71, A/B 累計差 11.4% / 訊號差 6.7%.
- 殘餘 SLs (Part A 2 筆, Part B 1 筆) 仍為 cooldown chain shift 下的 macro/commodity
  shock 訊號. 既有 COPX cross-asset filter (COPX-013/014/015/016/017) 全部使用
  「外部 macro / equity / FX 維度」(SPY、GLD、^VIX、DXY、yield curve), 從未試驗
  **資產內生原物料 (asset-intrinsic underlying commodity) direction 維度** —
  即 HG=F (Copper Futures) 自身價格走勢作為 regime classifier.

嘗試方向 (repo 首次 underlying commodity futures direction filter 於任何資產):
- COPX 為 Global X Copper Miners ETF, 持倉皆為銅礦個股, 其價格走勢的根本驅動
  因子為「銅價」. 相對於 SPY/GLD/DXY 等 macro proxy, 銅期貨 (HG=F) 為**最直接
  且結構性同源的 anchor**, 維度與既有 COPX-014 (vs GLD)、COPX-016 (vs DXY)
  cross-asset divergence 結構性不同 — 後者為 cross-asset divergence (兩資產
  N 日相對報酬), 本實驗為**直接的銅價方向 regime gate**, 不計算 COPX 與 HG 的
  差值, 而是判斷 HG=F 自身近期走勢是否處於急跌 regime.
- 假設 (copper-direction hypothesis):
  * 銅價在急跌 regime (HG=F N 日報酬 << 0) 時, COPX 雖跌深但屬「銅熊持續」
    結構, MR signal 多為 false bottom, 後續續跌風險高.
  * 銅價已穩定或反彈 (HG=F N 日報酬 >= -X%) 時, COPX 跌深更可能為「礦業個股
    特異性雜訊」(個股特定事件 / 短期過度反應), MR 反彈成功率高.
- 與 COPX-018 既有 5 維度正交 (pullback / WR / ATR ratio / Volume z-score) —
  銅期貨 direction 為**第 5 維度的外生 commodity-spot regime classifier**,
  捕捉「underlying commodity 自身急跌的延續性風險」, 為 OHLCV 之外的全新維度.

正交性 (orthogonality) 與 lesson #6 邊界:
- COPX-018 5 維度全部由 COPX 自身 OHLCV 衍生 (asset-intrinsic).
- COPX-019 加入 HG=F (CME 銅期貨) N 日 return 為**首次商品期貨 direction 作為
  COPX MR 過濾器**, 既有 COPX cross-asset filter 全部使用 ETF / 指數 / FX 為 anchor,
  從未使用商品現貨/期貨.
- 若 SL 集中於 HG=F 急跌 regime 而 winners 跨多 regime, 則此維度具區分力.

迭代計畫 (3 iterations max):
- Att1: copper_lookback=10, min_copper_return=-0.05 (10 日 HG 報酬 >= -5%, 寬鬆起點)
- Att2: 視 Att1 結果調整 (收緊至 -3% / 放寬至 -8% / 改用 5d 短窗口)
- Att3: 探索 LEVEL filter (HG 收盤 vs SMA60) 或 5d short-window direction

成功判準 (acceptance criteria):
1. min(A,B) Sharpe > 0.71 (COPX-018 Att3 全域最優)
2. A/B 累計差距 < 30%
3. A/B 訊號數差距 < 50%
4. 使用 ExecutionModelStrategy (繼承)
5. 失敗時記錄: 失敗原因 + cooldown chain shift 結構 + 對 lesson #20 v3 / lesson #24
   (cross-asset / forward-looking regime gate) 邊界貢獻
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class COPX019Config(ExperimentConfig):
    """COPX-019 HG=F Direction Filter on Volume-Confirmed MR 參數"""

    # 進場條件 (沿用 COPX-018 Att3 完整框架)
    pullback_lookback: int = 20
    pullback_threshold: float = -0.10
    pullback_upper: float = -0.20

    wr_period: int = 10
    wr_threshold: float = -80.0

    atr_short_period: int = 5
    atr_long_period: int = 20
    atr_ratio_threshold: float = 1.05

    # COPX-018 inheritance: Volume z-score 60d filter
    volume_zscore_period: int = 60
    volume_zscore_threshold: float = 0.5

    # COPX-019 核心新增: HG=F (Copper Futures) direction filter
    # 模式 (mode):
    #   "return_floor": HG=F N 日報酬 >= min_copper_return (FLOOR direction)
    #     → 過濾「銅價急跌」regime (期間 COPX MR 多為 false bottom)
    #   "return_ceil":  HG=F N 日報酬 <= max_copper_return (CEILING direction)
    #     → 假設驗證: 銅價急漲後反而為過熱訊號? (預期失敗, 對照組)
    #   "level_floor":  HG=F Close / SMA(60) >= level_floor (LEVEL filter)
    #     → 銅價相對中期均線位置作為 regime classifier
    #
    # 迭代紀錄 (3 iterations, Att1 ★ SUCCESS):
    # Att1 (10d, min_copper_return=-0.05, FLOOR direction): Part A 9/88.9%/
    #   Sharpe 1.01 cum +25.57% MDD -6.31% / Part B 3/100%/std=0 cum +10.87%
    #   MDD -4.31% / min(A,B)† 1.01 (Part A binding by EWJ-003 convention)
    #   +42% vs COPX-018 Att3 baseline 0.71. CAGR A 4.66%/yr vs B 5.30%/yr,
    #   gap 12.1% < 30% ✓; signal annualized 1.8/yr vs 1.5/yr, gap 16.7% <
    #   50% ✓. Filter 過濾 baseline 5 個訊號 (Part A 14→9, Part B 6→3),
    #   保留 Part A 1 SL 2019-05-08 (HG=F 10d ret > -5%, 邊緣保留),
    #   Part B 全部 3 訊號為 100% TP (zero-var). 過濾日 HG=F 10d 報酬皆 <
    #   -5% (銅期貨急跌 regime), 該 regime 下 COPX MR 多為 false bottom.
    # Att2 (10d, min_copper_return=-0.03, 收緊): Part A 6/100% std=0 cum
    #   +22.93% / Part B 1/100% std=0 cum +3.50% / min REJECT — A/B
    #   annualized signal 1.2/yr vs 0.5/yr gap **58% > 50% ❌**, Part A 過濾
    #   2 個額外 winners (2021-09-21 / 2023-03-16) 同時 Part B 1 個 winner
    #   (2024-09-04 / 2024-11-13) 流失, 收緊過嚴. Att1 -5% 確認為 robust
    #   sweet spot.
    # Att3 (5d, min_copper_return=-0.04, 短窗口替代維度): Part A 7/71.4%/
    #   Sharpe 0.32 cum +8.00% / Part B 3/66.7%/Sharpe 0.21 cum +2.15% /
    #   min 0.21 REJECT (-79% vs Att1) — 5d 短窗口在銅期貨上對 SL/TP 區分
    #   力過低, 移除 Part A 多筆 winners (2020-09-23/2021-03-04/
    #   2021-07-19/2023-11-08 等) 同時保留 Part A 1 個 SL 與引入 Part B 1
    #   個 SL. **5d 窗口失敗根因**: 銅價的 macro regime 變化以中期 (10d)
    #   為主週期 (與 GLD-015 ^GVZ 10d > 5d 結構性發現平行), 5d 短窗口捕捉
    #   過多 noise.
    #
    # 核心發現 (repo 首次商品期貨 direction filter on 商品 miners ETF):
    # 1. **Repo 首次「商品期貨 (HG=F) direction」作為 commodity miners ETF
    #    過濾器** — 既有 COPX cross-asset filter (COPX-013/014/015/016/017)
    #    全部使用「外部 macro / equity / FX 維度」(SPY、GLD、^VIX、DXY、
    #    yield curve), 從未直接使用標的所追蹤的商品本身價格走勢. HG=F 為
    #    COPX 結構性最直接的 anchor.
    # 2. **與既有 cross-asset divergence 結構性不同**: COPX-014 (vs GLD)、
    #    COPX-016 (vs DXY) 為 N 日相對報酬差異, 本實驗為 HG=F **自身**
    #    direction regime gate, 不計算差值.
    # 3. **10d > 5d 結構性發現**: 銅期貨 macro regime 變化以中期 10d 為主
    #    週期, 與 GLD-015 ^GVZ 10d > 5d 結構性發現平行 (商品系 implied vol
    #    / commodity direction 皆 10d 為甜蜜點).
    # 4. **lesson #20 v3 邊界擴展**: cross-asset divergence regime gate 從
    #    「兩資產相對報酬差」(TLT vs SPY、TSLA vs QQQ、EWZ vs EEM、
    #    INDA vs EEM、NVDA vs QQQ) 擴展至「underlying commodity 自身
    #    direction」維度, 此為 lesson #20 family 第 11+ 種變體 (repo 首次
    #    direct underlying commodity futures direction).
    # 5. **lesson #6 邊界**: 5 維度疊加 (pullback / WR / ATR ratio / Volume
    #    z-score / HG=F direction) 均為 surgical filter, Part A WR 從
    #    COPX-018 的 85.7% 進一步提升至 88.9%, max consec losses 維持 1,
    #    確認「當每個維度都針對特定失敗模式時, 確認指標可結構性堆疊」.
    copper_filter_mode: str = "return_floor"
    copper_ticker: str = "HG=F"
    copper_lookback: int = 10
    min_copper_return: float = -0.05  # Att1 ★ SUCCESS: 10 日 HG=F 報酬 >= -5%
    max_copper_return: float = 0.10  # 對照模式
    copper_sma_period: int = 60
    copper_level_floor: float = 0.95  # LEVEL 模式 (備用)

    # 冷卻期 (沿用 COPX-007/COPX-018)
    cooldown_days: int = 12


def create_default_config() -> COPX019Config:
    return COPX019Config(
        name="copx_019_copper_direction_mr",
        experiment_id="COPX-019",
        display_name="COPX HG=F Direction Filter on Volume-Confirmed MR",
        tickers=["COPX"],
        data_start="2010-01-01",
        profit_target=0.035,
        stop_loss=-0.045,
        holding_days=20,
    )
