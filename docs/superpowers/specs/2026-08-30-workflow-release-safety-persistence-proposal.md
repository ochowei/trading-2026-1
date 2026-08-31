# Workflow Release-Safety Persistence Proposal

## Current problem

The repository can prove workflow release, activation, registry, and study lifecycle facts, but it
cannot prove whether a release-safety assessment for one active predecessor and one draft successor
is still open. Study counts therefore cannot distinguish the A1-2 N04/N05 states from N06.

## Proposed workflow change

Add a version-pair release-safety contract to v009:

- `work/release-safety/saNNN/ASSESSMENT.json` opens one immutable assessment under the draft
  successor and binds the exact active predecessor, exact draft successor, successor workflow
  digest, blocking studies, missing impact decisions, reason, current time, and actor.
- `CLEARANCE.json` closes that exact assessment add-only. It binds the assessment digest and records
  one safe lifecycle disposition plus immutable evidence digests for every blocking study.
- The guarded writer allocates `SAxxx`, derives identities/digests/timestamps from repository facts,
  refuses multiple open assessments for one version pair, and never edits study state.
- An open assessment blocks new outcome-relevant study work and successor release preparation.
- Validation rejects malformed identity, duplicate/open records, digest drift, incomplete
  resolutions, unsafe study states, and inconsistent evidence.

The command surface writes safety evidence only. It does not implement the future CLI that reports
an A1-2 control state.

## Expected effect

Once v009 is effective, repository artifacts can positively distinguish an open N06 assessment
from the absence of one. N04/N05 can then be separated by unfinished-study count without guessing.
The active predecessor remains active throughout assessment; the draft successor remains the same
exact version and no identity is moved or rewritten.
