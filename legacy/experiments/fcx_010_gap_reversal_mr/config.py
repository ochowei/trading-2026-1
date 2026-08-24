"""
FCX-010：Gap-Down 資本化 + 日內反轉均值回歸配置
(FCX Gap-Down Capitulation + Intraday Reversal Mean Reversion Config)

動機（Motivation）：
    FCX-001（60日回撤 ≤ -18% + RSI(10)<28 + SMA50 乖離 ≤ -8%，TP +10%/SL -12%/25天）
    目前為 FCX 最佳策略 min(A,B) Sharpe 0.43，但進場條件過於嚴格（60日回撤 18% +
    SMA50 乖離 8%），年化訊號僅約 1 筆。Part A/B 累計差距顯著（Part A +90.41% vs
    Part B +17.31%，差距約 80%），主要因 Part A 2020 COVID 崩盤和 2022 熊市集中
    爆發，Part B 2024-2025 post-peak 銅週期無極端超賣機會。

    IBIT-006 Att2 驗證「Gap-Down 資本化 + 日內反轉 + 深回檔 + WR」模式在 24/7 連續
    價格發現的高波動資產上有效（min 0.15→0.40，+167%）。lesson #20a 指出 Gap-Down
    pattern 有效的結構性前提為：(a) 隔夜連續價格發現 + (b) 選擇性壓力非政策/事件
    持續。**FCX 作為銅礦股，其隔夜缺口反映銅期貨在 LME/SHFE/COMEX 近 24 小時的
    連續定價**——不同於 TQQQ-016（QQQ 底層缺乏 24/7 連續定價，驗證失敗）、FXI-010
    （政策新聞貫穿美股盤中，gap-down 後續跌）。

    本實驗為 repo 首次在**單一個股**測試 Gap-Down 資本化 + 日內反轉模式（先前僅
    在 IBIT crypto ETF/TQQQ 槓桿 ETF/FXI 政策驅動 EM ETF 上測試）。目標是驗證
    「商品連動股的隔夜期貨缺口」結構是否與「24/7 crypto 隔夜」等效。

策略方向：均值回歸（Gap-Down 資本化 + 日內反轉確認）
    Strategy direction: Mean reversion with capitulation gap + intraday reversal
    (cross-asset port from IBIT-006 to commodity-linked high-vol single stock)

迭代歷程（Iteration Log）：

Att1（Baseline）—— Gap-Down -2.0% + 10d Pullback [-6%, -18%] + WR + TP5/SL4
    進場：Gap <= -2.0% + Close > Open + 10d PB [-6%, -18%] + WR(10) <= -80 + cd=10
    出場：TP +5.0% / SL -4.0% / 15d
    結果：Part A n=9, WR 55.6%, cum +7.77%, Sharpe 0.21；
          Part B n=2, WR 100%, cum +10.25%, Sharpe 0.00（零方差）
          min(A,B) **0.00** (Part B 零方差) 或 Part A 0.21（< FCX-001 的 0.43）
    失敗分析：Part A 4 筆 SL 全為 1-3 日快速停損，集中在：
        - 2019-05-07（貿易戰升溫第一天）
        - 2019-08-06（人民幣匯率衝擊第一天）
        - 2023-02-24（無明確事件，似一般回檔）
        - 2023-03-14（SVB 銀行危機延續）
        這些為「新事件衝擊第一波」或「次波衝擊」訊號，gap-down 後續跌而非反轉。
        Part B 2024-2025 僅 2 訊號無統計意義。

Att2（ClosePos filter）—— 加入日內強反轉過濾
    進場：同 Att1 + ClosePos >= 50%（強日內反轉確認）
    出場：同 Att1
    結果：Part A n=8, WR 62.5%, cum +12.42%, Sharpe 0.36（+71% vs Att1）；
          Part B n=2, WR 100%, cum +10.25%, Sharpe 0.00（零方差，訊號集不變）
          min(A,B) **0.00** (Part B 零方差) 或 Part A 0.36（< FCX-001 的 0.43）
    分析：ClosePos>=50% 過濾器移除 1 筆 Part A SL（2023-02-24 的弱反轉），Part A
        Sharpe 0.21→0.36 / WR 55.6%→62.5%，但仍有 3 筆 SL（2019 兩筆 +
        2023-03-14 SVB 衍生），且 Part B 訊號集不變（gap-down + 強反轉在 2024-2025
        bull regime 極度稀少）。

Att3（Tighten Gap + Pullback）—— 加嚴 gap 至 -2.5% + pullback 下限至 -8%
    進場：Gap <= -2.5% + Close > Open + ClosePos >= 50% + 10d PB [-8%, -18%]
         + WR(10) <= -80 + cd=10
    出場：TP +5.0% / SL -4.0% / 15d
    結果：Part A n=5, WR 80%, cum +16.52%, Sharpe **0.87**（+142% vs Att2）；
          Part B n=1, WR 100%, cum +5.00%, Sharpe 0.00（零方差）
          min(A,B) **0.00** (Part B 零方差) 或 Part A 0.87（> FCX-001 的 0.43）
    分析：加嚴 gap 與 pullback 成功提升 Part A 品質至 Sharpe 0.87（repo 首見
        1-stock gap-down 之 Part A 高 Sharpe），但 Part B 訊號從 2→1，A/B 訊號
        年化比從 1.6:1（Att2）惡化至 2.0:1（Att3），且 Part B 樣本 n=1 零方差
        無統計意義。Part A/B 累計報酬差距 69.7%（>30%）違反平衡目標。

結論：FCX-010 三次迭代均未超越 FCX-001 的 min(A,B) 0.43，**Gap-Down Capitulation
    pattern 在商品連動個股上失效**，原因推測如下：

    1. **銅價衝擊結構性持續**：與 BTC 24/7 拋壓「隔夜資本化後美股撿便宜」不同，
       銅價衝擊（貿易政策、美元、全球需求預期）往往在美股盤中持續發酵——FXI 同理
       （中國政策貫穿美股盤中）。FCX 作為銅礦股，雖具隔夜期貨價格發現，但 gap-down
       後「政策/事件持續壓力」特性更接近 FXI 而非 IBIT。

    2. **FCX 歷史數據分布不對稱**：Part A（2019-2023）涵蓋貿易戰、COVID、升息熊市
       等多個宏觀衝擊，gap-down 頻繁；Part B（2024-2025）post-peak 銅週期缺乏
       capitulation 事件，訊號結構性稀少——任何緊 gap-down 過濾器在 Part B 都會
       淪為樣本不足。

    3. **一致失敗家族擴展**：Gap-Down pattern 延伸失敗清單：
       - TQQQ-016（槓桿指數 ETF，QQQ 非 24/7）失敗
       - FXI-010（政策驅動 EM ETF）失敗
       - FCX-010（商品連動個股）失敗
       目前僅 IBIT（純 BTC 24/7 ETF）驗證成功——結構性前提嚴格，不可跨類別泛化。

    4. **跨資產假設（待驗證）**：Gap-Down pattern 可能僅適用「underlying 連續交易 +
       selling pressure 自然耗盡」的純加密類資產（BTC、ETH 等現貨 ETF），不適用
       任何與宏觀政策/商品供需週期連動的美股。

資產特性：
    - FCX (Freeport-McMoRan) 日波動約 2.8-3.0%，GLD 比率 ~2.6x
    - 銅礦股，營收/股價高度依賴銅現貨價格
    - 銅期貨（LME/SHFE/COMEX）近 24 小時連續交易，提供隔夜價格發現
    - 高 beta（2020 COVID 崩盤 -55%、2022 -50%）
    - 成交模型：0.15% 個股滑價，隔日開盤市價進場

預設 config 使用 Att3 參數（Part A Sharpe 最高但 Part B 樣本不足）。
"""

from dataclasses import dataclass

from trading.core.base_config import ExperimentConfig


@dataclass
class FCX010Config(ExperimentConfig):
    """FCX-010 Gap-Down 資本化均值回歸參數"""

    # 進場參數（Att3 參數：加嚴 gap 與 pullback，Part A Sharpe 最高）
    gap_threshold: float = -0.025  # Att3: 隔夜開盤跳空 <= -2.5%（深度資本化拋壓 ~0.83σ）
    pullback_lookback: int = 10
    pullback_threshold: float = -0.08  # Att3: 10 日回檔 <= -8%（更深回檔確認）
    pullback_upper: float = -0.18  # 回檔上限 -18%（過濾崩盤極端值，FCX-001 對齊）
    wr_period: int = 10
    wr_threshold: float = -80.0  # Williams %R <= -80
    close_pos_threshold: float = 0.50  # Att2+: ClosePos >= 50% 強日內反轉確認
    cooldown_days: int = 10


def create_default_config() -> FCX010Config:
    return FCX010Config(
        name="fcx_010_gap_reversal_mr",
        experiment_id="FCX-010",
        display_name="FCX Gap-Down Capitulation + Intraday Reversal MR",
        tickers=["FCX"],
        data_start="2018-01-01",
        profit_target=0.05,  # +5.0%（IBIT-006 用 4.5%，FCX 高波動略寬）
        stop_loss=-0.04,  # -4.0%（gap-down 資本化確認後緊 SL，同 IBIT-006）
        holding_days=15,
    )
