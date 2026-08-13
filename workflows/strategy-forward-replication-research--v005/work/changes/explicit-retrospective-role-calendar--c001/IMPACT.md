# Impact

## Rules and artifacts affected

The change affects the retrospective plan-registration rule, the normative Phase 6 qualification
contract, qualification-plan domain model and persistence, CLI registration inputs, result-schema
validation, and their tests. It does not change strategy definitions, signals, execution policies,
costs, gates, trial counting, evaluation folds, screen calculations, or promotion boundaries.

Because data-role and warmup rules are workflow-level behavior, the accepted change requires a new
workflow version. The released v005 `WORKFLOW.md` and release evidence remain immutable.

## Existing studies and hypotheses

- `strategy-forward-replication-research@v005/S001`: `restart-on-v006`. Its frozen role calendar
  cannot be represented by v005 production orchestration. It remains paused until the owner
  separately authorizes cancellation. No outcome was accessed, so its 2010-2014 folds remain
  available to an exact successor.
- The next CLI-allocated study under v006 must use an exact `revisits` path to v005/S001, obtain a
  new preregistration and candidate-freeze approval, and bind the new explicit role calendar.
- Existing studies on v001-v004 and any immutable qualification evidence remain unchanged.

## Compatibility and migration risk

Legacy and clean Historical registration continue deriving the immediately preceding three
Development years and omit the new optional inventories, preserving their plan IDs and payloads.
Only retrospective registration may opt into the explicit calendar, and it must supply both the
Development years and warmup bounds.

The main risks are accidental overlap, accepting incomplete annual Development coverage, changing
old plan hashes, or allowing later Development context to leak into retrospective execution.
Domain, orchestration, persistence, schema, CLI, and backward-compatibility tests must all fail
closed on these cases. Development context is governance evidence only; screen inputs remain
restricted to the frozen evaluation sessions.
