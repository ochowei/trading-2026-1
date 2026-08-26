"""Compatibility alias for :mod:`trading.legacy.results`."""

import sys

from trading.legacy import results as _implementation

sys.modules[__name__] = _implementation
