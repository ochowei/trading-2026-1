# Validation

## Evidence and challenge method

Provider-free implementation validation is complete for the proposed shared tooling and tracked
preservation repair. The original independent read-only audit and main-agent source inspection
confirmed:

- v004/S004 freezes 2015-2025 Development, all of 2026 as quarantined, and 2027-2031 Historical;
- the prior implementation accepted explicit role-calendar inputs only for retrospective
  qualification;
- current default clean-Historical compilation derives the three years immediately preceding the
  first Evaluation year and rejects plan creation after Evaluation begins;
- the frozen family contains six identities while the current registry contains only its candidate
  and baseline;
- the candidate-freeze digest references exact pre-freeze evidence bytes that are not reachable
  from canonical Git history, although the local object database still contains matching bytes;
- workflow and policy validation pass, all six source hashes match the frozen PLAN, and repository
  evidence shows no tracked S004 Historical plan, screen, completion, or post-2025 snapshot.

The implementation now provides:

- explicit clean-Historical Development, warmup, quarantine, and future Evaluation calendars with
  disjointness, annual coverage, chronology, and pre-outcome freeze validation;
- a public provider-free `register-study` dry-run and register-only path whose only research input
  is the exact study path; the compiler derives and verifies preregistration, PLAN,
  CANDIDATE_FREEZE, workflow release, policy set, complete family, trial budget, candidate,
  baseline, source bytes, shared runtime, fingerprints, role calendar, and the required incomplete
  selection-history disclosure rather than accepting caller-supplied replacements;
- a durable cross-registry journal and serialized coordinator operation that registers missing
  outcome-free identities with the shared current-time boundary, preserves earlier
  candidate/baseline timestamps, rejects extra or mismatched family trials, and persists the exact
  plan; an injected second-write failure is automatically recovered by normal public retry before
  a new timestamp is read, concurrent identical retries converge on one plan event, and a
  different-time concurrent family mutation cannot interleave inside the frozen-universe/plan
  commit boundary;
- durable plan identity records and validates both registry paths, the separate human operation
  approver, approval timestamp, and contamination declaration, including pending recovery and
  completed idempotent retries;
- a tracked `ResearchEvidenceStore`, canonical
  `results/research-evidence/<sha256>.md` resolver, permanent-retention contract, and global
  candidate-freeze checksum plus Git-index validation, with a real Git-GC/fresh-clone regression;
  and
- exact additive recovery of digest
  `89fb54de9061d166f517f7be0bef0c13f6fb401b0bfdc1514ccc3edf81f33903` from the previously pinned
  bytes. The recovered file independently hashes to that same digest.

Validation performed on 2026-08-15 without provider or market-outcome access:

- `ruff check src tests`: passed;
- `ruff format --check src tests`: passed;
- the complete relevant regression set covering qualification domain, registry, coordinator, CLI,
  result validity, Shadow, trial registry, workflow authoring, followup guards, exact-study
  compilation, terminal evidence, immutable qualification evidence, and the evidence store: 259
  passed in 8.11 seconds. Exact invocation:

```text
UV_CACHE_DIR=/private/tmp/codex-uv-cache uv run pytest -q tests/test_historical_qualification.py tests/test_qualification_cli.py tests/test_qualification_registry.py tests/test_qualification_workflow.py tests/test_result_schema.py tests/test_trial_registry.py tests/test_workflow_authoring.py tests/test_study_qualification.py tests/test_study_terminal_evidence.py tests/test_research_evidence_store.py tests/test_shadow_qualification.py tests/test_followup_cutover.py tests/test_followup_cutover_cli.py tests/test_live_drift.py tests/test_live_drift_cli.py tests/test_live_drift_followup_integration.py tests/test_followup_manual_integration.py tests/test_research_run_coordinator.py
```

- the public v004/S004 provider-free dry-run compiled the exact six-trial family, 2015-2025
  Development, 2026 quarantine, 2027-2031 Evaluation, source/runtime bytes, and incomplete
  selection-history disclosure without writing either registry;
- `trading workflow validate --all`: passed;
- `trading policy validate --all`: passed; and
- `git diff --check`: passed.

An intentionally broader repository test invocation was stopped after 148 passing tests in 375.38
seconds because it had reached only 10% and covered unrelated provider/cache modules. It produced
no failure before interruption and is not claimed as completed validation.

## Interaction with other accepted changes

v007/C002 is a separate proposed change that defines a terminal study-time retrospective route. If C001 and
C002 are accepted into one replacement release, combined validation must use explicit route
discriminators and prove a matrix of both calendar types:

- C001 clean Historical calendars can preserve preregistered quarantine and nonstandard chronology
  without being interpreted as retrospective;
- C002 study-time retrospective calendars require earlier Development and later Evaluation and can
  never be interpreted as verified-clean;
- both routes use truthful current-time, complete-family frozen selection boundaries and reject
  late, missing, extra, or mismatched trials;
- a retrospective disposition cannot become a clean Historical or Shadow source; and
- persistence/reload, public coordination, status projection, and provider-free replay preserve
  the exact route, calendar, family, outcome, disposition, and authority.

Until both proposed changes are independently accepted, neither may be assumed by the other or by a
replacement workflow.

## Remaining uncertainty

Git evidence still cannot prove that no person, provider cache, external machine, or
out-of-repository tool has inspected 2027-2031 data. Actual v004/S004 registration therefore still
requires an explicit human contamination declaration and separate study-operation approval. This
change and its tests grant neither. Two independent files cannot receive one filesystem-level
atomic replacement; the contract is instead all-or-explicitly-recoverable through the durable
commit journal, idempotent writes, and rejection of any different operation while recovery is
pending. S004 remains pinned to v004 and paused.
