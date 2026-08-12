# Hypothesis: ACWI Turn-of-Month Integrity Replication

## Claim

ACWI has a reproducible daily-bar turn-of-month return effect under the exact released
`strategy-forward-replication-research@v002` workflow and policy set: at least one of the complete
`M-2`, `M-1`, and `M0` five-session candidates will satisfy every frozen Development eligibility
gate relative to a distinct tenth-session baseline. If a candidate is frozen, that same candidate
will satisfy every preregistered 2021-2025 Historical and robustness gate without reselection.

This is an integrity replication of S002, not a fresh discovery exercise. S002's 2009-2020
Development metrics are already known and are design provenance only. S003 keeps the same strategy
family, candidate inventory, costs, thresholds, and data roles while requiring each new formal
observation to carry a verifiable v002 release binding, canonical execution argv, and exact
orchestration source bytes.

## Decision relevance

An eligible Development candidate permits only an explicit human candidate-freeze decision. A
subsequent complete Historical pass means only `shadow-eligible`; it does not register Shadow,
authorize activation, contact a broker, submit orders, or authorize live trading. No eligible
Development candidate stops this research round. Missing provenance or reproducibility evidence
also stops advancement rather than being inferred from operator assertions.

## Falsification conditions

The claim is falsified with `fail` if no candidate satisfies every Development gate within the
frozen trial budget, or if a frozen candidate later fails any complete Historical or robustness
gate. In particular, non-positive stress return, stress profit factor at or below `1.00`, stress
maximum drawdown below `-15%`, or concentration above `50%` in either cost scenario makes a
candidate ineligible.

The result is `indeterminate`, not `fail`, when a required approval, data artifact, definition,
workflow release binding, policy identity, exact command, orchestration source capture, checksum,
complete Git HEAD, or replay boundary is missing, conflicting, or unverifiable. Fixed Development
and Historical stages cannot use `insufficient-evidence`. No conclusion may use 2026 quarantine
data or inspect 2021-2025 outcomes before an eligible candidate is frozen and separately approved.
