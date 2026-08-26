"""Compatibility alias for :mod:`trading.legacy.sync_docs`."""

import sys

from trading.legacy import sync_docs as _implementation

sys.modules[__name__] = _implementation
