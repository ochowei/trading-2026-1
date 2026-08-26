"""Compatibility alias for :mod:`trading.workflow.qualification`."""

import sys

from trading.workflow import qualification as _implementation

sys.modules[__name__] = _implementation
