"""
資料擷取模組 (Data Fetcher Module)
使用 yfinance 多線程下載美股歷史數據。
Downloads US stock historical data via yfinance with multi-threading.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import yfinance as yf

from trading_tw.scanner.config import DATA_PERIOD, MAX_WORKERS

logger = logging.getLogger(__name__)


class DataFetcher:
    """
    資料擷取器 (Data Fetcher)
    負責從 yfinance 下載 OHLCV 日線數據，支援多線程加速。
    Downloads OHLCV daily data from yfinance with multi-threaded acceleration.
    """

    def __init__(
        self,
        period: str = DATA_PERIOD,
        max_workers: int = MAX_WORKERS,
        start: str | None = None,
        end: str | None = None,
    ):
        self.period = period
        self.max_workers = max_workers
        self.start = start
        self.end = end

    def _fetch_single(self, ticker: str) -> pd.DataFrame | None:
        """
        下載單一標的數據 (Download data for a single ticker)
        Returns None if download fails.
        """
        try:
            download_kwargs = {
                "progress": False,
                "auto_adjust": True,
            }
            if self.start:
                download_kwargs["start"] = self.start
                if self.end:
                    download_kwargs["end"] = self.end
            else:
                download_kwargs["period"] = self.period

            df = yf.download(ticker, **download_kwargs)
            if df is None or df.empty:
                logger.warning(f"[DataFetcher] 無法取得 {ticker} 的數據 (No data for {ticker})")
                return None

            # yfinance 回傳的 MultiIndex columns 需要處理
            # Handle MultiIndex columns from yfinance
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # 確保必要的欄位存在 (Ensure required columns exist)
            required = {"Open", "High", "Low", "Close", "Volume"}
            if not required.issubset(set(df.columns)):
                logger.warning(
                    f"[DataFetcher] {ticker} 缺少必要欄位 (Missing required columns): "
                    f"{required - set(df.columns)}"
                )
                return None

            # 移除含有 NaN 的列 (Drop rows with NaN)
            df = df.dropna(subset=list(required))

            logger.info(f"[DataFetcher] {ticker}: 取得 {len(df)} 筆資料 ({len(df)} rows fetched)")
            return df

        except Exception as e:
            logger.error(f"[DataFetcher] 下載 {ticker} 時發生錯誤 (Error fetching {ticker}): {e}")
            return None

    def fetch_all(self, tickers: list[str]) -> dict[str, pd.DataFrame]:
        """
        多線程下載所有標的 (Download all tickers with multi-threading)

        Args:
            tickers: 標的代碼清單 (List of ticker symbols)

        Returns:
            dict mapping ticker -> OHLCV DataFrame (only successful downloads)
        """
        results: dict[str, pd.DataFrame] = {}

        logger.info(
            f"[DataFetcher] 開始下載 {len(tickers)} 檔標的 "
            f"(Downloading {len(tickers)} tickers with {self.max_workers} workers)..."
        )

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._fetch_single, ticker): ticker
                for ticker in tickers
            }

            for future in as_completed(futures):
                ticker = futures[future]
                try:
                    df = future.result()
                    if df is not None and not df.empty:
                        results[ticker] = df
                except Exception as e:
                    logger.error(
                        f"[DataFetcher] {ticker} 處理失敗 (Processing failed): {e}"
                    )

        logger.info(
            f"[DataFetcher] 下載完成: {len(results)}/{len(tickers)} 成功 "
            f"({len(results)}/{len(tickers)} succeeded)"
        )
        return results
