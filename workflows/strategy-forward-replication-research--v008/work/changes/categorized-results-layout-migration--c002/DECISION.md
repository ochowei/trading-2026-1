# Decision

## Disposition

Accept the categorized results layout migration for implementation and replacement-version
preparation.

## Rationale

The current flat result store mixes workflow evidence, workflow-native trial results, legacy
experiment results, migration evidence, immutable evidence blobs, and registries. The confirmed
categorized layout gives each class an explicit ownership boundary while the digest-bound,
one-hop compatibility registry preserves frozen historical references without rewriting released
workflow or study bytes.

The decision accepts the storage contract and implementation scope described by C002. It does not
pre-approve release, study resumption, outcome inspection, broker access, or trading. Those actions
retain their independent guards.

## Human approval

`ochowei@gmail.com` confirmed the exact C002 proposal and impact disposition and supplied this
stable identity for the guarded acceptance record.
