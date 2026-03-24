"""
TQQQ 恐慌抄底策略配置 (TQQQ Capitulation Buy Strategy Configuration)
定義 TQQQ 專屬策略的所有參數與閾值。
Defines all parameters and thresholds for the TQQQ capitulation buy strategy.
"""

# 訊號指標參數 (Signal indicator parameters)
TQQQ_DRAWDOWN_LOOKBACK: int = 20          # 回撤計算的高點回望天數
TQQQ_DRAWDOWN_THRESHOLD: float = -0.15    # 從 20 日高點回撤 ≥ 15%
TQQQ_RSI_PERIOD: int = 5                  # 短週期 RSI 捕捉急性恐慌
TQQQ_RSI_THRESHOLD: float = 25.0          # RSI(5) < 25 極端超賣
TQQQ_VOLUME_MULTIPLIER: float = 1.5       # 成交量 > 1.5 倍均量
TQQQ_VOLUME_SMA_PERIOD: int = 20          # 均量計算週期

# 出場參數 (Exit parameters)
TQQQ_PROFIT_TARGET: float = 0.05          # 獲利目標 +5%
TQQQ_STOP_LOSS: float = -0.08             # 停損 -8%（收盤價判斷）
TQQQ_HOLDING_DAYS: int = 7                # 最長持倉 7 個交易日

# 訊號冷卻 (Signal cooldown)
TQQQ_COOLDOWN_DAYS: int = 3               # 同一波跌勢中僅取第一個訊號

# 資料參數 (Data parameters)
TQQQ_TICKER: str = "TQQQ"
TQQQ_DATA_PERIOD: str = "5y"
