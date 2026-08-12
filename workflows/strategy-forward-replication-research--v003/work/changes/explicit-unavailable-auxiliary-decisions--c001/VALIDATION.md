# Validation

## Evidence and challenge method

Implementation tests prove that default excess lag still raises, opt-in mode marks the decision
unavailable while preserving the stale row and actual lag, non-default mode round-trips through the
canonical manifest, and the XLF gap-safe runtime removes unavailable signal dates and candidates.
Repository policy/workflow validation, focused tests, legacy inventory guard, Ruff, and diff checks
must pass before acceptance or release preparation. On 2026-08-12, released-policy validation
passed without modifying v001 implementation bytes, and 41 focused market-data, manifest, and XLF
definition tests passed. Ruff passed for the affected implementation and tests.

## Interaction with other accepted changes

No other v003 source change exists. This change also incorporates the separately authorized
observation-provenance documentation contract by retaining the complete v003 reproducibility text
in v004 and adding the new auxiliary policy wire field there.

## Remaining uncertainty

The change does not establish that an XLF candidate is profitable or eligible. The next
CLI-allocated v004 study (expected `S001`) must remain separate and preregistered, and the
unavailable-session inventory must be frozen before execution.
Canonical effectiveness still requires approved release preparation, commit/PR review, and merge.
