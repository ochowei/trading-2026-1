# Workflow Release Activation

Replace repository-branch inference with an explicit workflow release activation boundary. Release
preparation creates immutable `RELEASE.json` and moves activation-enabled versions from `draft` to
`prepared`; a separate human-approved activation creates immutable `ACTIVATION.json`, binds the
exact release digest, and transitions the version to `active` while superseding its predecessor.

The `strategy-forward-replication-research` family adopts the new machine-enforced boundary from
v010. Version v009 remains the bootstrap version whose own effectiveness follows the v008
canonical-merge rule, while v008 receives a current-time, non-backdated grandfathered activation
attestation so state projection no longer depends solely on branch inspection.
