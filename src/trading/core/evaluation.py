"""Compatibility alias for :mod:`trading.legacy.evaluation`."""

import sys

from trading.legacy import evaluation as _implementation

sys.modules[__name__] = _implementation
