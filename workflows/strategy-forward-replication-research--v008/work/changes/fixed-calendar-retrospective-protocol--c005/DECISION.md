# Decision

## Disposition

Accepted for inclusion in v009.

## Rationale

Use one immutable civil-date calendar for every study under the workflow version so cross-study
comparisons share the same historical generation and no caller can select, shorten, or shift a
favorable interval. Treat the fixed 2025 stage as retrospective execution replay rather than
prospective Shadow: it may test paper proposals, simulated fills, ledger behavior, checkpoints, and
drift logic, but it cannot support promotion, activation, broker, order, or live authority.

Changing any fixed boundary or restoring a prospective promotion route requires another accepted
workflow change and successor version. Preserve all v008 studies and their frozen semantics;
v008/S001 and v008/S002 remain completed, while paused v008/S003 remains `continue-on-v008` and is
not moved, resumed, or reinterpreted.

## Human approval

Approved by `ochowei@gmail.com`.
