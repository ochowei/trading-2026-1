"""Compatibility alias for :mod:`trading.knowledge_freshness`."""

import sys

from trading import knowledge_freshness as _implementation

sys.modules[__name__] = _implementation
