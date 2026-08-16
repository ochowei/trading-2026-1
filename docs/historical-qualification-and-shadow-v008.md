# Historical qualification, study-time retrospective Evaluation, and Shadow (v008)

Phase 6 records clean Historical, retrospective-confirmatory, study-time-retrospective, and
prospective Shadow lifecycle evidence. Clean Historical evidence can produce only
`shadow-eligible`; either retrospective route can produce only `retrospectively-supported`;
prospective Shadow can produce only `activation-eligible`. None of these states alone authorizes
live orders.

This document is the versioned technical contract selected by
`strategy-forward-replication-research@v008`. The complete workflow behavior remains in that
version's `WORKFLOW.md`.

## Routes, capability, and evidence classification

Every new study declares its route before preregistration. The released workflow must carry the
structured `study-time-retrospective-v1` capability before study initialization or qualification
registration may accept `study-time-retrospective`; string matching, date inference, and caller
assertions are not capability evidence.

Before outcome inspection, every proposed Evaluation session is classified for the exact asset and
lineage as `verified-clean`, `known-contaminated`, or `provenance-unknown`. Only
`verified-clean` sessions with complete relevant selection history may enter clean Historical
Evaluation. Completed data with unknown or contaminated provenance may enter an explicitly frozen
retrospective route. A new researcher, new study, or promise not to reread prior results cannot
upgrade provenance.

The two retrospective routes are distinct:

- `retrospective-confirmatory` is an optional non-promotional checkpoint whose Development context
  may follow the completed Evaluation interval;
- `study-time-retrospective` is a terminal study route whose Development interval must strictly
  precede a later time-ordered retrospective Evaluation interval already available at study time.

Both freeze a current-time `retrospective_selection_checkpoint`. It never becomes a future-only
Forward Selection Epoch and never grants clean-evidence or promotion authority.

## Structured preregistration and calendars

Every capability-scoped route pins the SHA-256 of one structured `QUALIFICATION_SPEC.json` at
preregistration. Before outcome-relevant Development execution, the spec freezes:

- route and authoritative repository-relative trial/qualification registry identities;
- whole-year Development, quarantine, and Evaluation calendars plus exact warmup bounds;
- the complete finite family, every member role/source SHA, shared runtime sources, candidate and
  distinct baseline roles, trial budget, and selection-history disclosure;
- policy, cost, execution, holding, lag, purge, embargo, snapshot, and observation requirements;
- benchmark, block-bootstrap, random-seed, and computational budgets;
- typed challenge IDs, metrics, operators, thresholds, exact targets, and required distinct
  evidence identities.

Preregistration fails before Development if any required field is absent, internally inconsistent,
or weaker than the workflow floors. Terminal outcome/disposition mappings are fixed by the released
workflow and terminal validator, not supplied by the spec or caller. Development begins only after
preregistration and a separate add-only stage authorization containing a stable human identity.
After Development selection, the human owner uses the guarded current-time
`workflow study freeze-candidate` writer. Its input contains only the selected candidate, distinct
baseline, and ordered complete family; the writer supplies all approval, scope, budget, and exact
study digest fields and creates `CANDIDATE_FREEZE.json` add-only. Hand-authored, backdated,
incomplete, or replacement freezes fail closed.

Every plan freezes exact session inventories and annual folds. Before registry mutation, the
exact-study compiler combines the preregistered whole-year calendars and warmup bounds with the
pinned released market/session policy to derive Development, warmup, quarantine, and Evaluation
XNYS sessions deterministically. The default clean route uses the
three complete consecutive Development years immediately before at least five complete consecutive
annual Evaluation folds. A clean study may instead freeze a preregistered explicit calendar when it
needs a nonstandard but chronological Development, warmup, quarantine, and future Evaluation
boundary. Registration must reproduce those exact inventories and may not silently derive a
preceding-three-year substitute.

A retrospective-confirmatory plan may freeze nonstandard chronology, including completed
Development context after the retrospective interval. A study-time plan must freeze at least three
complete consecutive Development years strictly before at least five complete consecutive annual
Evaluation folds. For every explicit calendar:

- inventories are unique, chronological, non-empty, and pairwise disjoint;
- warmup is strictly before Evaluation and covers the declared dependency window;
- unassigned sessions are explicitly quarantined or out of scope;
- Development is governance and selection evidence only, never Evaluation return input;
- warmup may supply observations and declared dependencies but never signals, fills, cooldown,
  positions, P&L, capital, benchmarks, or performance; and
- Evaluation and family-wise adjustment inputs match the frozen Evaluation sessions exactly.

Partial overrides, role overlap, sparse or incomplete years, insufficient warmup, route mismatch,
implicit reassignment, or post-inspection role changes fail before registry mutation.

## Exact-study compilation and frozen readiness

The provider-free public compiler accepts an exact study path for every clean or retrospective
route rather than caller-supplied family, calendar, source-hash, trial-budget, candidate, or
baseline values. Inside the shared
study-registration lock, it resolves and revalidates:

- the exact study, route, preregistration, `PLAN.md`, `QUALIFICATION_SPEC.json`, add-only
  Development authorization, human-approved `CANDIDATE_FREEZE.json`, completion state, and
  released workflow capability;
- the exact policy set, selected trial, distinct baseline, complete family, maximum trial budget,
  selection-history disclosure, sources, shared runtime, and semantic fingerprints; and
- the explicit or default role calendar, quarantine, folds, and all technical screen inputs.

The resulting plan stores exact repository-relative registry identities independently from
operational absolute paths. Terminal replay compares the relative identities exactly and never
accepts an absolute-path suffix or copied-root lookalike.

Dry-run returns the complete resolved representation without writing registries, executing a
research definition, creating an observation, refreshing data, or reading market outcomes.

Complete-family register-only preparation and qualification-plan append form one logical durable
transaction. The operation:

1. takes a current UTC boundary without a backdating option;
2. preserves existing registration timestamps and gives missing outcome-free identities truthful
   current-time timestamps;
3. writes a commit-decision journal binding the exact study, both registry paths, human operation
   approver, approval time, contamination declaration, family registrations, and plan bytes;
4. holds the trial-registry/family universe lock through missing registration, exact universe
   recheck, and plan append; and
5. performs idempotent writes so normal public retry recovers the same bytes before reading a new
   time or accepting a different operation.

A second-write or process failure leaves an explicit recoverable decision, never a silently
accepted half-publication. Missing, extra, late, or mismatched trials; source/fingerprint drift;
selection-disclosure drift; calendar drift; a completed study; or an incompatible pending journal
fails closed. Register-only preparation creates no trial observation and supplies no authority to
run a later stage.

## Preserved evidence and authoritative registry snapshots

Pre-freeze Markdown evidence referenced by an immutable candidate freeze exists only at
`results/research-evidence/<sha256>.md`. The filename equals the exact bytes' SHA-256; publication
is add-only, mutable aliases and overwrites are prohibited, and referenced artifacts are
permanently retained. Workflow validation requires the worktree bytes to equal the Git-index blob
and must pass after Git GC and a fresh clone.

Terminal retrospective decisions use tracked
`results/qualification-evidence/<sha256>.json` snapshots rather than trusting a mutable local
registry head. Publication proves that the physical registry path equals repository root plus the
preregistered source identity. Resolution verifies outer and inner digests, replays the source
registry hash chain and checkpoint through the authoritative `QualificationRegistry`, and selects
the exact plan and sole canonical `historical-screen:<plan-id>` event. Duplicate or noncanonical
plan/screen events fail closed. Later registry appends cannot alter already frozen terminal
evidence.

Development gates, challenge manifests, and each distinct challenge artifact use the canonical
tracked `results/study-evidence/**` namespace. The repository ignore policy explicitly includes
both terminal-evidence namespaces, so a normal Git add/fresh-clone workflow cannot silently omit
them.

A Development terminal failure uses an absence snapshot of that same preregistered qualification
registry. At completion its snapshot/checkpoint head must equal the current registry head and must
contain no plan or screen for the study. Development completion and plan registration use the same
study-registration lock; registration rereads freeze/completion state after taking it, completion
rejects a pending transaction journal, and deleting `CANDIDATE_FREEZE.json` cannot erase an
append-only plan.

## Folds, screen, and required challenges

Plans require at least five complete consecutive annual Evaluation folds. Dependency purge covers
maximum holding plus execution lag, opening embargo covers execution lag, every trade belongs to
the fold containing its signal date, and the trade exits within that fold. Zero-signal folds remain
explicit evidence.

The screen recomputes canonical isolated-sleeve outcomes under base and stress costs from exact
formal observations. It enforces at least:

- 20 completed trades across at least three traded folds;
- at least 60% positive traded folds;
- base compounded return above zero and profit factor above 1.1;
- stress return above zero, profit factor above 1.0, and maximum drawdown within the preregistered
  limit;
- no fold above 50% of total trades or total positive profit; and
- complete-family block-bootstrap confidence of at least 90%.

The required challenge family includes cash, a distinct simpler family baseline,
exposure-matched random entries, small preregistered parameter perturbations, delayed entry, higher
costs, worse fills, missed entries, and market-regime checks. Study-specific margins, binding
requirements, risk limits, and gates may tighten but never weaken the universal floors.

Each challenge freezes a typed gate, exact benchmark/trial/method target, unique evidence identity,
and a distinct immutable evidence artifact. The artifact binds the exact study/spec/freeze/plan and
supplies the metric/target-bound observed value used to recompute the gate; a manifest-level
`observed` or `passed` assertion is not
evidence. Study-time terminal replay requires the complete 14-gate shared screen and exactly nine
required challenge identities without target reuse or artifact reuse.

Family-wise selection adjustment consumes exactly one boundary:

- clean Historical uses `forward_selection_epoch` and its `started_at`;
- either retrospective route uses `retrospective_selection_checkpoint` and its `frozen_at`.

When prior selection history is incomplete, the boundary must repeat that disclosure and exactly
match the frozen family and selected trial. Every included trial has a parseable first-registration
timestamp no later than the applicable boundary. A missing or dual boundary, disclosure mismatch,
family or candidate mismatch, missing timestamp, or late trial fails before confidence is computed.

## Study-time terminal outcomes

An independent reviewer completes `study-time-retrospective` using the frozen
`TERMINAL_EVIDENCE.json` and exactly one mapping:

- `pass` plus `retrospectively-supported` only when every identity, shared screen gate, and
  required challenge gate passes;
- `fail` plus `development-selection-failed` when complete trustworthy Development evidence
  finds no eligible candidate or exhausts the trial budget, no candidate freeze exists, and the
  current-head absence proof shows no plan/screen;
- `fail` plus `retrospective-screen-failed` when a complete retrospective screen has one or more
  failed frozen gates; or
- stage-identified `indeterminate` when data, identity, classification, approval, family history,
  artifact, or replay evidence cannot support a trustworthy decision.

`insufficient-evidence` is unavailable for a fixed completed historical checkpoint. Too few
trades or traded folds is a frozen gate failure, not permission to wait or lower a threshold. No
human or system may manufacture a disposition from a document tuple without replaying its linked
evidence.

A terminal retrospective result never creates `shadow-eligible`, `activation-eligible`, Active,
broker, order, or live authority. If promotion evidence is later desired, a separately
preregistered CLI-allocated successor records the exact `revisits` path, treats all prior exposed
outcomes as Development context, and reserves later unused `verified-clean` Evaluation evidence.
It may not relabel or reuse the retrospective interval.

## Compatibility and prospective Shadow

Existing v007 plan, screen, registry, and status payloads keep their exact identities and meaning.
Legacy plans without explicit calendars do not acquire synthetic role inventories during reload.
The clean calendar, retrospective-confirmatory calendar, and study-time calendar have explicit
route identities and cannot be converted by date inference. v004/S004 remains paused, pinned to
v004, and governed by its frozen artifacts plus separate operation approval; no v008 lifecycle
state migrates, resumes, registers, or authorizes it. Its compatibility adapter accepts only the
exact canonical repository path, not a copied suffix lookalike.

Only a persisted passing clean Historical screen may register prospective Shadow. Registration
binds exact plan, trial, definition snapshot, policy, cost, prospective start, and activation
checkpoint identities at current UTC. Every retrospective-only plan, screen, disposition, or
completed study is rejected as a Shadow source.

Shadow remains non-actionable paper evidence. Pre-registration observations do not count.
Definition or outcome-relevant execution changes terminate the lineage and require full
requalification. Missing, stale, corrupt, rewritten, contradictory, or non-replayable evidence
fails closed. Activation evaluation never bypasses controlled cutover, ledger, reconciliation,
allocation, parity, drift, no-new-entry, or manual-operator guards.

## Provider-free release readiness

Release readiness must exercise the public paths without provider access or outcome inspection:

- explicit clean calendar, quarantine preservation, exact S004-compatible six-trial compilation,
  register-only transaction, injected recovery, concurrent retry, persistence/reload, and
  complete-family negative cases;
- study-time preregistration/spec validation, Development failure proof, candidate freeze,
  retrospective registration, screen coordination, selection adjustment, typed terminal replay,
  terminal mappings, and Shadow-source rejection;
- role overlap, chronology drift, late/missing/extra trials, classification upgrade, noncanonical
  screen, registry-path substitution, challenge target/artifact reuse, Git-index byte mismatch,
  Git GC, and fresh-clone failures; and
- backward compatibility for existing v007 clean, retrospective-confirmatory, Shadow, activation,
  and monitoring payloads.

Registration-only, serialization-only, direct-domain-only, coordinator-only, or synthetic
non-registry tests do not satisfy this readiness contract.
