# Auxiliary Unavailable-Decision Reproducibility Contract

This normative extension applies only when a released workflow selects a market policy that
permits explicit unavailable auxiliary decisions. The existing snapshot, definition, result, and
replay requirements in `docs/reproducibility.md` remain mandatory.

An auxiliary availability policy may encode `excess_lag_mode=mark_unavailable`. The default
`fail` value remains omitted from canonical manifest bytes for backward compatibility. The
non-default mode must be serialized inside the auxiliary entry's `availability_policy`, included
in the snapshot identity, and included in the captured research-definition configuration and
semantic fingerprint.

Replay must reconstruct the exact mode before auxiliary alignment. For every decision whose actual
observation lag exceeds the frozen maximum, the aligned view preserves the backward-as-of data row,
`ObservationDate`, `AvailableSession`, and `ObservationLagSessions`, and sets
`ObservationAvailable=false`. The definition must suppress any raw signal, candidate, or trade on
that decision. An unavailable row is audit evidence, not usable current information.

Formal evidence must enumerate every unavailable decision and prove that none appears in raw
signals, candidates, or trades. Missing mode binding, unavailable-session inventory, audit columns,
or suppression proof is `indeterminate` and blocks partial ranking. Changing the mode, maximum lag,
publication lag, or suppression behavior requires a new definition identity and preregistration
before outcome access.
