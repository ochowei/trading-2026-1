# Decision

## Disposition

Accepted for inclusion in a replacement workflow version.

## Rationale

The append-only abandonment event closes the lifecycle gap left when an exactly bound study is
cancelled after registering a qualification plan but before producing a screen. The guarded design
preserves the original plan and hash chain, releases only the single-open-plan administrative lock,
and grants no screen disposition, outcome, replay, Shadow, broker, order, position, or live
authority.

The capability boundary is accepted as essential: installing the implementation does not empower
v009. Only a separately released and activated successor carrying
`qualification-plan-abandonment-v1` may authorize the command. S002 and its open plan remain
unchanged until that boundary and a separate current abandonment approval are satisfied; paused
S003 remains `restart-on-v010` and is neither moved nor resumed.

## Human approval

`ochowei@gmail.com` explicitly approved acceptance of C001 on 2026-09-01. This accepts the change
proposal only. It does not evolve, prepare, release, merge, or activate v010; append an abandonment
event; create or operate a successor study; inspect outcomes; or authorize trading.
