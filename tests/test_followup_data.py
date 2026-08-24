from pathlib import Path

import pandas as pd
import pytest

from trading.core.followup_data import (
    AuxiliaryDataRequiredError,
    DeclaredAuxiliaryData,
    build_followup_data_bundle,
)


class _Detector(DeclaredAuxiliaryData):
    def auxiliary_symbols(self) -> tuple[str, ...]:
        return ("QQQ",)


def _bars(values: list[float]) -> pd.DataFrame:
    index = pd.bdate_range("2026-07-27", periods=len(values))
    return pd.DataFrame(
        {
            "Open": values,
            "High": [value + 1 for value in values],
            "Low": [value - 1 for value in values],
            "Close": values,
            "Volume": [1000.0] * len(values),
        },
        index=index,
    )


def test_declared_auxiliary_data_is_fail_closed_and_bundle_identity_is_deterministic() -> None:
    primary = _bars([10.0, 11.0, 12.0, 13.0, 14.0])
    qqq = _bars([100.0, 101.0, 102.0, 103.0, 104.0])
    detector = _Detector()

    with pytest.raises(AuxiliaryDataRequiredError, match="not bound"):
        detector.require_auxiliary("QQQ", primary.index)

    first = build_followup_data_bundle(
        primary_symbol="SPY",
        primary_frame=primary,
        auxiliary_symbols=detector.auxiliary_symbols(),
        frames={"QQQ": qqq},
    )
    second = build_followup_data_bundle(
        primary_symbol="SPY",
        primary_frame=primary.copy(),
        auxiliary_symbols=detector.auxiliary_symbols(),
        frames={"QQQ": qqq.copy()},
    )
    detector.bind_auxiliary_data(first)

    assert first.identity == second.identity
    assert len(first.identity) == 64
    assert detector.require_auxiliary("QQQ", primary.index)["Close"].tolist() == (
        qqq["Close"].tolist()
    )


def test_selected_followup_auxiliary_detectors_do_not_access_yfinance_directly() -> None:
    roots = (
        "gld_016_dxy_divergence_mr",
        "nvda_007_rs_exit_optimized",
        "tlt_017_yield_curve_slope_mr",
        "tqqq_025_vxn_vix_vvix_filter",
        "tsla_017_qqq_divergence_breakout",
        "xbi_018_xbi_xlv_divergence_mr",
    )
    experiment_root = Path("legacy/experiments")

    for name in roots:
        source = (experiment_root / name / "signal_detector.py").read_text(encoding="utf-8")
        assert "import yfinance" not in source
        assert "yf.download" not in source
