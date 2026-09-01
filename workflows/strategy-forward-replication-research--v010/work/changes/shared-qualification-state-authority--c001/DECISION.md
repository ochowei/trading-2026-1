# Decision

## Disposition

Accepted for inclusion in the v011 replacement workflow.

## Rationale

The repository contains multiple internally valid qualification hash chains under the same frozen
logical registry identity, including open plans for the same experiment family. Worktree-local
default resolution therefore permits a writer to bypass the family-wide single-open-plan guard
without corrupting either local chain. Selecting one chain, concatenating events, rewriting hashes,
or starting a new empty registry would discard authoritative history rather than repair the defect.

The accepted direction preserves every source registry and checkpoint byte-for-byte, establishes a
worktree-independent shared authority, validates a complete migration inventory, and projects open
plans across immutable source shards and the active shared chain. Cross-chain administrative
closure remains append-only, exact-plan-bound, separately human approved, and non-outcome evidence.

The existing-study impacts are accepted as proposed: paused v008/S003 is `close-invalidated` only
after the successor capability and its separate guarded closure authority exist; cancelled
v009/S002 remains terminal and may be administratively closed only after migration and separate
current approval; paused v009/S003 becomes `restart-on-v011` if no v010 successor study is created
before v011 activation. No study is moved, resumed, cancelled, completed, reviewed, or
reinterpreted by this decision.

## Human approval

`ochowei@gmail.com` explicitly accepted v010/C001 in the current interaction. The guarded
transition records the authoritative current UTC decision time. This acceptance does not evolve,
prepare, release, merge, or activate v011; migrate a registry; close a plan; create or operate a
study; inspect outcomes; or authorize broker access, orders, positions, or trading.
