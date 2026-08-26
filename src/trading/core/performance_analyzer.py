"""Compatibility alias for :mod:`trading.legacy.performance_analyzer`."""

import sys

from trading.legacy import performance_analyzer as _implementation

sys.modules[__name__] = _implementation
