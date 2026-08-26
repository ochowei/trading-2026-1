"""Compatibility alias for :mod:`trading.workflow.study_qualification`."""

import sys

from trading.workflow import study_qualification as _implementation

sys.modules[__name__] = _implementation
