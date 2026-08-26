"""Compatibility alias for :mod:`trading.workflow.studies`."""

import sys

from trading.workflow import studies as _implementation

sys.modules[__name__] = _implementation
