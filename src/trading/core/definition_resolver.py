"""Compatibility alias for :mod:`trading.legacy.definition_resolver`."""

import sys

from trading.legacy import definition_resolver as _implementation

sys.modules[__name__] = _implementation
