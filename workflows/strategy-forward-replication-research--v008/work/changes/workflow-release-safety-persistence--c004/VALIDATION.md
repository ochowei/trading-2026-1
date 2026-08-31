# Workflow Release-Safety Persistence Validation

## Evidence and challenge method

Validate the writer and repository validator with synthetic active-predecessor/draft-successor
fixtures. Cover successful open/clear, exact identity and SHA-256 binding, current UTC and actor
capture, `SAxxx` allocation, duplicate-open refusal, unsafe-clearance refusal, release blocking,
G-FAMILY study-operation blocking, successful clearance, and tamper detection.

Run Ruff, focused pytest, the non-slow regression suite, `trading workflow validate --all`, and
`git diff --check`. Review the v009 contract and governance presentation for agreement with the
implemented paths and command boundary.

## Interaction with other accepted changes

The change preserves v008 C003's v009 bootstrap and v010 explicit activation boundary. It augments
the prepared-successor family guard without weakening C001 challenge-only authority or C002 result
path migration. Release safety remains separate from study outcomes and from workflow activation.

## Remaining uncertainty

The A1-2 state-query CLI is deliberately not part of this change. Until that later command is
implemented, the evidence and validator exist but callers must not claim that a canonical state
reporter exists.
