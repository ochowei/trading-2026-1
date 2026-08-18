# Proposal

## Current problem

The v008 workflow requires study-time retrospective evaluation to retain exactly nine distinct,
immutable challenge artifacts and a challenge manifest. It freezes each challenge ID, typed gate,
target identity, and evidence identity, but it does not require every method target to carry a
complete executable method contract. A study can therefore preregister names such as seeded
missed-entry or canonical adverse-fill without freezing the ordering, rounding, event transform,
or other details needed to reproduce the method uniquely.

The maintained qualification coordinator can replay a registered plan against exact formal
manifests and trial-registry observations, and its screen path projects canonical evidence onto the
plan's Evaluation sessions. Those protections are not exposed through an independent challenge
operation. The only public execution command couples challenge-related calculations to the full
qualification screen and its registry mutation. This prevents a narrowly authorized operator from
creating challenge evidence without also exercising screen authority, and encourages unsafe
alternatives such as hand-authored artifacts or caller-supplied interpretations.

Formal result envelopes may legitimately retain canonical records from Development, quarantine,
and Evaluation because one immutable generation supports multiple roles. Challenge evidence needs
an explicit, content-addressed role projection so that only registered Evaluation sessions can
contribute signals, trades, P&L, benchmarks, or challenge metrics. Date inference, filenames,
observation time, and a manifest's mere presence are not sufficient plan binding.

## Proposed workflow change

Require a replacement workflow version to add a complete guarded challenge-only contract:

1. **Executable challenge specifications.** Before preregistration, every required challenge must
   freeze a versioned executable method contract in addition to its existing ID, typed gate,
   target, and evidence identity. The contract must define all outcome-relevant behavior needed for
   deterministic replay, including input roles, ordered source identities, projection rules,
   algorithms, seeds, sample counts, rounding, tie handling, event transforms, cost/fill policies,
   ledger interaction, raw-evidence requirements, output metrics, and failure conditions. A method
   identity without a registered implementation and exact schema is not preregistration-ready.
   In particular, missed-entry methods must freeze candidate ordering, selection algorithm,
   percentage-to-count rounding, and no-replacement ledger behavior; adverse-fill methods must
   freeze the exact entry/exit price transform, gap and ambiguity handling, fee/slippage ordering,
   and unfilled behavior.
2. **Plan-bound observation set.** A challenge operation starts from one authoritative registered
   plan and exact study path. It verifies the route, preregistration, plan, qualification spec,
   Development authorization, candidate freeze, released workflow, policy set, selected candidate,
   distinct baseline, ordered complete family, trial budget, source identities, definition
   fingerprints, and all frozen hashes. For each family member it resolves exactly one successful,
   valid formal Evaluation observation by exact trial, snapshot, result, and manifest identities.
   Missing or duplicate matches, mixed run modes, drift, caller aliases, mutable `latest`, or
   time/filename inference fail closed.
3. **Provider-free immutable role projection.** The operation verifies one shared frozen data
   generation across the complete family, then creates or resolves a content-addressed projection
   over exactly the registered Evaluation session inventory. The projection preserves source
   manifest/result/observation/data-generation identities and records excluded warmup,
   Development, and quarantine inventories. Those excluded roles may supply only dependencies
   explicitly allowed by the frozen method; they cannot contribute signals, accepted candidates,
   positions, fills, cooldown, P&L, capital, benchmark samples, or metrics. The source observations
   remain immutable and are never rewritten or relabelled.
4. **Independent guarded command.** Provide a public command equivalent to
   `trading qualification challenge run-study --study <path> --plan-id <id>` with exact family
   manifest inputs and `--dry-run`. It must use the authoritative registries pinned by the study,
   must not invoke the qualification screen coordinator, and must not refresh data, call a
   provider, execute a research definition, create a new trial observation, or mutate the trial or
   qualification registry. A dry-run performs all identity, method, source, projection, path, and
   duplicate checks and prints the deterministic publication plan without creating artifacts.
5. **Nine-artifact atomic publication.** A non-dry-run executes each frozen challenge method at
   most once from the verified projections and publishes exactly nine distinct content-addressed
   artifacts plus one manifest under the canonical `results/study-evidence/**` namespace. Every
   artifact binds the study, plan, spec, freeze, workflow, policy set, method implementation,
   source observation(s), source result(s), source manifest(s), common data generation, exact
   Evaluation session identity, metric, observed value, gate, and sufficient raw values for
   provider-free recomputation. The manifest cannot substitute a self-reported pass flag for
   artifact evidence.
6. **Atomicity and idempotence.** Publication uses a bounded study/plan lock, stages all files in
   the destination filesystem, verifies their final content-addressed identities, and commits the
   complete set atomically or leaves no newly visible artifact. An exact retry is idempotent;
   partial, conflicting, duplicate, differently bound, or previously executed challenges fail
   closed. Recovery may complete only an already committed exact publication decision and cannot
   accept changed inputs.
7. **Authority separation.** Challenge-only authority does not authorize Evaluation execution,
   provider access, refresh, a qualification screen, registry mutation, terminal evidence,
   conclusion, study transition, Shadow, broker, order, activation, or live authority. Screen and
   terminal operations remain separately guarded stages that consume, but do not rewrite, the
   immutable challenge artifacts.
8. **Validation requirements.** Shared tooling must cover missing plan binding, missing or
   duplicate Evaluation observations, mixed data generation, policy/fingerprint/workflow drift,
   role leakage, provider access attempts, incomplete method specifications, duplicate execution,
   dry-run zero mutation, atomic rollback/recovery, path substitution, artifact collisions, and
   any implicit qualification-screen invocation. Tests use synthetic fixtures and must not inspect
   study outcomes.

The exact command spelling and shared module names are implementation details, but the authority,
identity, semantics, projection, publication, and failure boundaries above are behavioral and must
be self-contained in the replacement `WORKFLOW.md`. Any new artifact schema or technical API must
also be documented in a versioned normative Phase 6 contract and the repository architecture map.

## Expected effect

Future studies can preregister challenges only when their calculations are fully specified and
executable. After separately authorized Evaluation observations exist, an operator can validate and
publish the nine frozen challenge artifacts without provider access, rerunning definitions,
performing a qualification screen, or mutating either registry. Reviewers can replay each observed
value from exact role-projected evidence instead of trusting names, timestamps, prose, or
manifest-level assertions.
