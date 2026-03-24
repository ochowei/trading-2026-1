"""
配置模組 (Configuration Module)
定義掃描器的所有參數與閾值。
Defines all parameters and thresholds for the scanner.
"""

import pandas as pd


# 已知 ETF 清單 (Known ETF tickers)
ETF_TICKERS: set[str] = {
    "SPY", "QQQ", "TQQQ", "SQQQ", "SOXX", "IWM", "DIA",
    "XLF", "XLE", "XLK", "XLB", "XLI", "XLP", "XLU", "XLV", "XLY",
    "VTI", "VOO", "VEA", "VWO", "ARKK", "ARKW", "ARKG",
    "GLD", "SLV", "TLT", "HYG", "EEM", "EFA", "IEMG",
    "SOXL", "SOXS", "SPXL", "SPXS", "UPRO", "SH", "PSQ",
}

# 預設掃描標的清單 (Default ticker list)
DEFAULT_TICKERS: list[str] = [
    "SPY", "QQQ", "NVDA", "TSLA", "AAPL", "TQQQ",
    "AMZN", "META", "GOOGL", "MSFT", "AMD",
    "SOXX", "SOXL", "IWM", "DIA",
]

# 技術指標參數 (Technical indicator parameters)
SMA_PERIOD: int = 20
RSI_PERIOD: int = 14
RSI_THRESHOLD: float = 25.0
VOLUME_MULTIPLIER: float = 1.5
SHADOW_BODY_RATIO: float = 1.5

# 乖離率閾值 (Bias thresholds) — 負數表示低於均線
BIAS_THRESHOLD_STOCK: float = -0.10   # 個股: 低於 SMA20 超過 10%
BIAS_THRESHOLD_ETF: float = -0.05     # ETF: 低於 SMA20 超過 5%

# 獲利目標 (Profit targets)
PROFIT_TARGET_STOCK: float = 0.03     # 個股: 3%
PROFIT_TARGET_ETF: float = 0.015      # ETF: 1.5%

# 回測參數 (Backtest parameters)
HOLDING_DAYS: int = 3                 # 最長持倉天數
DATA_PERIOD: str = "5y"               # 歷史資料長度

# 多線程下載 (Multi-threading)
MAX_WORKERS: int = 8


class Config:
    """掃描器配置類別 (Scanner configuration class)"""

    @staticmethod
    def is_etf(ticker: str) -> bool:
        """判斷是否為 ETF (Check if ticker is an ETF)"""
        return ticker.upper() in ETF_TICKERS

    @staticmethod
    def get_bias_threshold(ticker: str) -> float:
        """
        取得乖離率閾值 (Get bias threshold)
        ETF: -5%, 個股: -10%
        """
        if Config.is_etf(ticker):
            return BIAS_THRESHOLD_ETF
        return BIAS_THRESHOLD_STOCK

    @staticmethod
    def get_profit_target(ticker: str) -> float:
        """
        取得獲利目標 (Get profit target)
        ETF: 1.5%, 個股: 3%
        """
        if Config.is_etf(ticker):
            return PROFIT_TARGET_ETF
        return PROFIT_TARGET_STOCK

    @staticmethod
    def is_near_earnings(ticker: str, date: pd.Timestamp, days: int = 3) -> bool:
        """
        檢查是否接近財報日 (Check if date is near earnings)

        TODO: 整合財報日曆 API (e.g., yfinance earnings_dates)
        目前回傳 False，不進行過濾。
        Currently returns False — no filtering applied.

        預留接口：未來可透過 yfinance 的 Ticker.earnings_dates 或
        第三方 API 取得財報日期，並在訊號觸發前過濾掉財報日前後 N 天的訊號。

        Interface reserved: In the future, integrate with yfinance
        Ticker.earnings_dates or a third-party API to filter out signals
        within N days of earnings announcements.
        """
        return False
