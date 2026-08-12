# Proposal

## Current problem

The v003 auxiliary-data contract fails the entire bundle whenever a backward-as-of observation
exceeds its preregistered maximum lag. XLF S003 showed that three isolated MOVE gaps in otherwise
available 2004–2020 Development data make the complete candidate family unexecutable. Raising the
maximum lag would treat stale information as current and weaken the mechanism.

## Proposed workflow change

Permit a study to preregister an explicit `mark_unavailable` auxiliary excess-lag mode. The maximum
lag remains binding. A decision beyond it retains its exact observation date, availability date,
and actual lag as audit evidence but is marked unavailable and must not generate a signal. The
default remains whole-bundle failure. The mode is outcome-relevant and immutable after
preregistration.

Require manifests to serialize non-default excess-lag behavior, definitions to prove unavailable
decisions are suppressed, and evidence to enumerate all excluded sessions before outcome use.

## Expected effect

Sparse auxiliary provider gaps can be handled without stale-data use or silent row dropping, while
prior studies and definitions keep their exact fail-closed semantics. XLF may restart under v004
with maximum lag 3 and the three known Development decisions explicitly unavailable.
