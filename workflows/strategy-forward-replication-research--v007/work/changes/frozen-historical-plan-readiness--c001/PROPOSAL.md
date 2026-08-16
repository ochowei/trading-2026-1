# Proposal

## Current problem

An independent provider-free audit of the paused
`strategy-forward-replication-research@v004/S004` study found that its frozen 2027-2031 clean
Historical design is preserved but cannot currently be compiled and registered faithfully.

The frozen study assigns 2015-2025 to Development, quarantines every 2026 session, and assigns
2027-2031 to five annual Historical Evaluation folds. The production clean-Historical planner
instead derives only the three years immediately before Evaluation as Development and rejects an
explicit role calendar outside retrospective qualification. It would therefore include 2026,
omit 2015-2023, and fail to preserve the preregistered boundary. The plan must also be frozen
before the first Evaluation outcome begins, so waiting until 2031 is not a valid repair.

The same study freezes a six-trial family, but the append-only trial registry currently contains
only the candidate and baseline for that family. Registration freezes the trials present at the
selection boundary, while the screen rejects trials added afterward. There is no governed public
register-only path that atomically validates and freezes all six outcome-free identities.

Finally, the candidate-freeze record pins the pre-freeze Development evidence SHA-256
`89fb54de9061d166f517f7be0bef0c13f6fb401b0bfdc1514ccc3edf81f33903`, but those exact bytes have no
tracked canonical path. They are currently recoverable only from local unreachable Git blob
`0404678ad7289cdbade7b08d3f4e040eba5b049d`. A fresh clone cannot rely on that object.

## Proposed workflow change

Require an outcome-free frozen-plan compilation and preservation stage before any clean Historical
Evaluation begins:

- A clean-Historical plan may carry an explicit preregistered role calendar when a study freezes
  nonstandard but chronological Development, quarantine, warmup, and Evaluation boundaries.
  Registration must reproduce the exact study calendar, prove role disjointness, and reject any
  implicit reassignment; it must not silently fall back to the preceding-three-year convention.
- A provider-free compiler/validator must resolve an exact study, released workflow, policy set,
  candidate, baseline, complete trial family, trial budget, source bytes, and role calendar before
  registry mutation. It must expose a dry-run representation suitable for independent review.
- A governed register-only operation must add the complete frozen family without executing a
  strategy, creating an observation, or reading market outcomes, then freeze that exact family
  atomically with the plan. For S004, the four robustness identities receive truthful current-UTC
  `first_registered_at` values; neither preregistration nor candidate-freeze time may be backfilled
  or reused as registry time. One transaction establishes a current-time Forward Selection Epoch,
  validates all six identities against the exact frozen PLAN source paths and fingerprints,
  registers any missing outcome-free robustness identities at that boundary, and freezes the
  complete six-trial universe. Existing candidate/baseline registration timestamps remain
  unchanged and must be no later than the boundary. The candidate-freeze time is provenance, not
  the registry selection boundary. Because the registry discloses incomplete prior selection
  history, this Forward Selection Epoch must freeze
  `prior_selection_history_incomplete=true` and match the registry disclosure exactly;
  register-only preparation cannot relabel history as complete. Missing or extra family members, a
  source/fingerprint mismatch, any registration after the boundary, a disclosure mismatch, or any
  mismatch between the frozen family and the registry boundary fails closed. The register-only
  operation creates no observations; later outcome execution remains responsible for binding each
  exact snapshot/observation to the frozen plan and its data role.
  Here, atomic means one logical durable commit: because two independent registry files cannot be
  replaced by one filesystem operation, a write-ahead journal is the commit decision, public retry
  must recover its exact bytes before taking a new timestamp, and the family-universe check plus
  plan append must remain inside the trial-registry lock. The journal must bind the exact study,
  registry paths, human operation approver, approval time, and contamination declaration.
- Pre-freeze evidence bytes referenced by an immutable candidate-freeze record must have a
  canonical tracked, content-addressed artifact at
  `results/research-evidence/<sha256>.md`. The existing digest deterministically resolves the path;
  mutable aliases, latest pointers, and second maintained copies are prohibited. Additive recovery
  is allowed only when the exact bytes reproduce the already pinned digest; neither the freeze
  record nor the recovered bytes may be rewritten. The `src/trading/research_data/` subsystem owns
  immutable publication and digest-based resolution. Once a tracked candidate freeze references an
  artifact, that artifact is permanently retained and excluded from orphan deletion or GC.
  `trading workflow validate --all` must scan tracked candidate-freeze references from a fresh
  clone and fail closed on a missing file, overwrite, path/digest mismatch, or digest collision.
  Fresh-clone verification, Git-GC independence, checksum-failure tests, ownership, retention, and
  the new repeated artifact pattern must be documented in reproducibility and architecture
  contracts.
- Release-readiness tests must exercise the public provider-free path for explicit clean calendars,
  quarantine preservation, six-trial register-only freeze, persistence/reload, and fail-closed
  negatives. Tests must not refresh data, execute research definitions, or synthesize outcomes.

The repair must not edit v004/S004's `HYPOTHESIS.md`, `PLAN.md`, preregistration, candidate freeze,
or existing evidence. It must not inspect 2027-2031 data or claim that repository evidence proves
no out-of-repository access occurred. A replacement v008 release cannot add authority to a study
pinned to v004: tooling used for S004 must remain backward-compatible with the v004 contract and
must simultaneously satisfy S004's frozen artifacts plus a separate study-operation approval. If
any new behavior is not already authorized by those v004 artifacts, S004 remains paused.

## Expected effect

An accepted replacement workflow and compatible tooling can preserve and compile S004's already
frozen clean-Historical design before its Evaluation boundary, while keeping the study pinned to
v004 and paused until separately authorized. The replacement workflow itself grants S004 no new
execution authority. Future studies can fail closed before outcome access when their explicit
data-role calendar, complete family, or pre-freeze evidence cannot be reproduced exactly.
