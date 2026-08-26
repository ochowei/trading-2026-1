"""Compatibility alias for :mod:`trading.legacy.legacy_experiments`."""

import sys

from trading.legacy import legacy_experiments as _implementation

sys.modules[__name__] = _implementation
