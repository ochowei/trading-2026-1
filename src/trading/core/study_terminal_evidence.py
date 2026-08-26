"""Compatibility alias for :mod:`trading.workflow.terminal_evidence`."""

import sys

from trading.workflow import terminal_evidence as _implementation

sys.modules[__name__] = _implementation
