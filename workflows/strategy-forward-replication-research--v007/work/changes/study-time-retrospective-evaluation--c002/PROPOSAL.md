# Proposal

## Current problem

The current workflow distinguishes Development, optional retrospective-confirmatory evidence,
verified-clean Historical Evaluation, prospective Shadow, activation, and monitoring. Its strongest
promotion path correctly requires evidence that was not allowed to influence design or selection.
For an ordinary new research question, however, the clean period may lie entirely in the future.
That can leave a study paused for years even when the research owner only needs an honest answer to
the narrower question: does a frozen candidate remain credible on a later, time-ordered portion of
the historical data already available when the study begins?

Using all existing history as undifferentiated Development produces no evaluation. Calling a
historical holdout clean without append-only proof overstates its authority. Treating a
retrospective pass as qualification would erase the distinction between research evidence and
promotion evidence. The workflow therefore needs an explicit route that can finish a study now
without pretending that the result authorizes Shadow or live trading.

## Proposed workflow change

Add a preregistered `study-time-retrospective` route with the following contract:

1. Before outcome-relevant execution, the study freezes one chronological data-role calendar.
   Earlier sessions are Development; a later, non-overlapping historical interval is
   time-ordered retrospective Evaluation. Warmup, purge, embargo, entry/exit containment, and all
   quarantined or unassigned sessions are explicit. No session can change role after inspection.
2. The retrospective interval exists at study creation and is classified honestly as
   `known-contaminated` or `provenance-unknown` unless qualifying append-only evidence supports a
   separate verified-clean route. A new researcher, new study, or promise not to reread prior
   results cannot upgrade provenance.
3. Development may execute only after preregistration and explicit stage authorization. It must
   retain the full trial family, trial budget, observations, failures, tombstones, ranking, and
   selection rationale. Development selects at most one candidate and a distinct simple baseline.
4. Before retrospective outcome inspection, candidate freeze pins the selected trial, complete
   family, baseline, exact definition/source bytes, data-role calendar, policies, costs, execution
   behavior, metrics, thresholds, benchmarks, robustness challenges, seeds, and selection
   boundary. No tuning, reranking, family expansion, or candidate replacement follows the freeze.
5. Retrospective Evaluation uses immutable snapshots and offline runs over the frozen later
   interval. The route inherits the v007 floors without weakening: at least three complete
   Development years; five complete consecutive annual retrospective folds; at least 20 completed
   trades across at least three traded folds; at least 60% positive traded folds; base compounded
   return greater than zero and profit factor greater than 1.1; stress return greater than zero,
   stress profit factor greater than 1.0, and stress maximum drawdown within the study's
   preregistered limit; no fold contributing more than 50% of total trades or total positive
   profit; and complete-family block-bootstrap selection confidence at least 90%. Required
   challenges remain cash, a distinct simpler family baseline, exposure-matched random entries,
   small preregistered parameter perturbations, delayed entry, higher costs, worse fills, missed
   entries, and market-regime checks. Each study must preregister the exact hypothesis-specific
   baseline margins, binding requirements, stress drawdown limit, and challenge gates before
   outcome access; those may tighten but cannot weaken the universal v007 floors. All evidence must
   support provider-free replay. A route lacking the required three-year Development and five-fold
   calendar is not preregistration-ready; an executed candidate with too few trades or traded folds
   fails its frozen gate rather than receiving `insufficient-evidence`.
   Each challenge must freeze a typed gate, an exact benchmark/trial/method target, a unique
   evidence identity, and a distinct immutable evidence artifact. The artifact supplies the exact
   observed value bound to that metric and target; terminal review uses it to recompute the gate
   rather than trusting manifest-level observed/pass fields.
6. An independent reviewer completes the study with exactly one terminal outcome:
   - `pass` only when every retrospective identity and frozen gate passes; its sole disposition is
     `retrospectively-supported`;
   - `fail` at Development, before any retrospective plan or screen exists, records
     `development-selection-failed` when complete trustworthy Development evidence finds no
     eligible candidate or exhausts the trial budget; the actual candidate-freeze artifact must
     not exist. Preregistration must freeze the authoritative trial/qualification registry paths,
     and terminal evidence must include a tracked content-addressed snapshot of that exact
     qualification registry proving the study has no plan/screen. Completion must compare the
     snapshot to the current registry/checkpoint head, so deleting a candidate-freeze file cannot
     erase an earlier append-only plan. Development completion and plan registration must hold the
     same study-registration lock; registration re-reads frozen study/completion state after
     acquiring it, and completion rejects a pending durable transaction;
   - `fail` after a complete retrospective screen records `retrospective-screen-failed` when any
     frozen retrospective gate fails;
   - `indeterminate` when data, identity, classification, approval, family history, artifact, or
     replay evidence cannot support a trustworthy decision; it must identify the failing stage and
     must not manufacture a Development or retrospective-screen disposition;
   - `insufficient-evidence` is unavailable for a fixed completed historical checkpoint and cannot
     replace a failed minimum-data or performance gate.
   A terminal retrospective pass/fail must reference a tracked content-addressed snapshot of the
   exact qualification registry and head checkpoint. The authoritative registry reader must replay
   its hash chain and schema before the exact plan and sole canonical
   `historical-screen:<plan-id>` event can support the decision. Duplicate/noncanonical screens
   fail closed. Snapshot publication must derive and enforce the exact preregistered source path
   relative to repository root; a caller cannot label bytes from another registry with that
   identity. Later appends to
   mutable local registry state cannot invalidate or alter that frozen terminal evidence.
7. A retrospective terminal result never creates `shadow-eligible`, `activation-eligible`, Active,
   broker, order, or live authority. Qualification code must reject Shadow registration whose only
   source is a retrospective plan, screen, disposition, or completed study.
8. If promotion evidence is later desired, create a separate CLI-allocated successor study that
   records the exact `revisits` path. The prior study and all outcomes it exposed become Development
   context. The successor must independently preregister and reserve later, unused,
   `verified-clean` Evaluation evidence; it cannot relabel or reuse the retrospective interval.

Every new study must declare its intended route before preregistration. The study-time route makes
a terminal historical research conclusion available without waiting for future years; it does not
promise `pass` when the available history cannot satisfy the frozen minimum folds, trades, family,
or integrity requirements.

The replacement workflow should carry a companion `STAGES_AND_OUTCOMES.md` beside `WORKFLOW.md`.
It will contain the existing complete guide plus its concise plain-language section, be linked from
the version README and workflow, and be explicitly classified as a reference companion. The
released `WORKFLOW.md` remains the sole behavioral authority. Release preparation must record the
companion's exact SHA-256 in `RELEASE.json`, and validation must reject any post-release byte drift;
changing the companion after release requires a later workflow version even though it remains
explanatory rather than normative. The current
`docs/research-evidence-stages-and-outcomes.md` becomes a short pointer after the replacement draft
validates, avoiding two maintained copies.

## Expected effect

A research owner can complete Development, candidate freeze, rigorous time-ordered retrospective
Evaluation, independent review, and a terminal study outcome using only historical data available
at study time. Results remain useful for rejecting weak ideas or retaining historically credible
candidates, while the workflow preserves an unmistakable boundary between retrospective support
and the clean/prospective evidence required for Shadow, activation, or live authority.
