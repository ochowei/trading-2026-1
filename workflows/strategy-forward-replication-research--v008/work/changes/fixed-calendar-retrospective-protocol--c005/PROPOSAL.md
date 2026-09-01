# Fixed-calendar retrospective protocol

Replace the successor workflow's caller-selected historical calendars and promotion route with one
version-owned, fixed historical protocol. Every study under the resulting workflow version must use
the same exact civil-date boundaries, resolved to exact exchange sessions by the pinned market
policy:

| Role | Fixed interval |
| --- | --- |
| Warmup-only | `2013-01-01` through `2013-12-31` |
| Development | `2014-01-01` through `2018-12-31` |
| Quarantine | `2019-01-01` through `2019-12-31` |
| Historical Evaluation | `2020-01-01` through `2024-12-31`, one complete annual fold per year |
| Retrospective execution replay | `2025-01-01` through `2025-12-31` |

The workflow and exact-study compiler must reject caller-supplied calendar overrides, shortened or
shifted intervals, role overlap, incomplete fixed-calendar coverage, and assets without the full
required session history. Unassigned sessions remain quarantined or out of scope; no study may
silently reclassify them.

Replace the current three route choices with a single versioned
`fixed-calendar-retrospective` route. Candidate selection still uses Development evidence only,
retains the complete trial family and trial budget, and freezes the selected candidate before any
formal Evaluation or replay execution. The `2020-2024` Evaluation and `2025` replay are historical,
non-promotional evidence regardless of researcher identity or study creation time; neither may be
relabelled prospective, verified-clean promotion evidence, or a Forward Selection Epoch.

Replace Prospective Shadow with `retrospective-execution-replay`. The replay processes every pinned
2025 exchange session in order using the frozen candidate, data generation, policy set, costs,
execution behavior, ledger rules, checkpoints, and drift logic. It produces non-actionable paper
proposals and simulated fills only. It must not backdate a Shadow registration or create Shadow,
broker, order, Controlled Activation, Active, or live-trading authority.

The replay retains a minimum of 12 completed simulated fills and the existing base/stress return,
profit-factor, stress-drawdown, and critical-drift gates. Because its interval is complete and
immutable, fewer than 12 fills or failure of a frozen performance gate is `fail`, not
`insufficient-evidence`. Missing, conflicting, corrupt, or non-replayable identities and artifacts
remain `indeterminate`.

A terminal `pass` requires both the fixed `2020-2024` Historical Evaluation and fixed `2025`
execution replay to pass every applicable frozen gate. Its only positive disposition is
`retrospectively-supported`; it never produces `shadow-eligible`, `activation-eligible`, Controlled
Activation, Active status, broker access, order authority, or live authority. Remove the successor
workflow's prospective Shadow, Controlled Activation, and Active monitoring stages and their
promotion semantics.

The fixed calendar is part of workflow-version identity. Any change to a boundary, role, fold, or
replay year requires an accepted workflow change and another workflow version; a study or caller
cannot opt into a different calendar.
