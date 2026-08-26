# Workflow-native research definitions

This is the active source namespace for formal research identities. Permanent trial identities use
the path `<family>/<trial>/definition.py` and are resolved as `<family>/<trial>` without importing
the retired `trading.experiments` registry.

Top-level Python modules that predate the directory convention are reusable definition seams, not
trial identities. Their paths may be pinned by frozen study evidence and must not be moved or
rewritten merely to reorganize the tree. New reusable seams belong under `primitives/`; existing
seams stay at their frozen paths and may expose compatibility imports when a successor is added.

`_template/` is the supported starting point for a new workflow-governed identity. Outcome-relevant
work still requires a released workflow, exact policy versions, and a preregistered study before
formal execution or outcome inspection.
