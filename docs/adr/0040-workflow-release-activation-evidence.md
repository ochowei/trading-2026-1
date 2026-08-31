---
status: accepted
---
# Activate workflow releases with immutable evidence

Workflow releases use a separate human-approved Workflow Release Activation event because canonical
branch membership is checkout-dependent and cannot by itself project one deterministic control
state. Release preparation creates immutable `RELEASE.json` and, from each family's declared
`activation_required_from` boundary, moves a draft to `prepared`; activation creates immutable
`ACTIVATION.json`, binds the release digest, and alone switches registry authority to `active`.

The rejected alternatives were treating `RELEASE.json` as sufficient, which conflates preparation
with authority, and inspecting the canonical branch, which makes state depend on remote/ref state.
Existing effective releases receive current-time, explicitly grandfathered attestations rather than
backdated activation claims. Strategy Controlled Activation remains a separate trading lifecycle.
