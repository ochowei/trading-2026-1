"""Historical import facade for the frozen legacy experiment inventory.

New research must use :mod:`trading.research_definitions`. This package exists only so archived
imports such as ``trading.experiments.spy_007_trend_pullback`` remain reproducible in a checkout.
"""

from pathlib import Path

from trading.legacy.experiments import (
    discover,
    get_experiment,
    list_experiments,
    register,
)

_LEGACY_PACKAGE_PATH = Path(__file__).resolve().parents[3] / "legacy" / "experiments"
__path__.append(str(_LEGACY_PACKAGE_PATH))
discover(__name__, __path__)

__all__ = ["get_experiment", "list_experiments", "register"]
