"""TQQQ-014 VIX-adaptive detector with a declared historical auxiliary."""

import pandas as pd

from trading.core.followup_data import DeclaredAuxiliaryData
from trading.experiments.tqqq_001_capitulation.signal_detector import TQQQSignalDetector


class TQQQVixAdaptiveDetector(DeclaredAuxiliaryData, TQQQSignalDetector):
    """Expose VIX as a verified auxiliary column for adaptive exits."""

    def auxiliary_symbols(self) -> tuple[str, ...]:
        return (self.config.vix_ticker,)

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = super().compute_indicators(df)
        df["VIX"] = self.require_auxiliary(self.config.vix_ticker, df.index)["Close"]
        return df
