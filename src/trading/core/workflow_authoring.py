"""Compatibility alias for :mod:`trading.workflow.authoring`."""

import sys

from trading.workflow import authoring as _implementation

sys.modules[__name__] = _implementation
