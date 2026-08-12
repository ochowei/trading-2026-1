# Decision

## Disposition

Accepted for incorporation into the next replacement policy and workflow version.

## Rationale

The explicit unavailable-decision contract preserves the preregistered maximum lag instead of
treating stale auxiliary observations as current. It keeps whole-bundle failure as the default,
requires an opt-in immutable policy identity, retains exact lag evidence, and forbids signals on
unavailable decisions. This resolves the S003 availability blocker without weakening its frozen
rule or changing released v003 artifacts.

## Human approval

Approved by `ochowei@gmail.com` on 2026-08-12. The guarded workflow transition records the exact
current UTC decision timestamp.
