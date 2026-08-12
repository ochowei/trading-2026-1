# Workflow-First Research Architecture Design

## Goal

Make released workflows and preregistered studies the only formal path for new outcome-relevant
research, while preserving existing research identities as legacy evidence and keeping shared
technical infrastructure maintainable.

This design introduces composable, independently versioned policy families so different workflows
can use different market, broker, execution, and portfolio constraints without copying or mutating
rules.

## Resolved decisions

- A workflow is the versioned procedure and decision authority. A study is one execution instance
  pinned to one released workflow version.
- The canonical study path remains
  `workflows/<workflow>--vNNN/work/studies/<study>--sNNN/`.
- A study need not exist before exploratory implementation begins. It must be created and
  preregistered before the first outcome-relevant execution or inspection that can affect
  selection.
- Pure engineering maintenance may proceed without a study. A change to strategy meaning, data
  interpretation, execution semantics, policy, evaluation gates, or research conclusions is
  outcome-relevant and must use the appropriate workflow or policy lifecycle.
- Shared constraints are divided into composable policy families. A workflow explicitly selects
  exact policy versions; there is no implicit latest-policy resolution.
- Released policy versions are immutable. A rule change creates a new policy version, and adopting
  it creates a new workflow version when it affects a released workflow.
- A policy version is executable and verifiable, not only narrative documentation. It binds a
  human-readable contract, machine-readable configuration, implementation identities, and
  conformance-test identities.
- Research source remains in the application source tree. Formal execution captures an immutable
  Research Definition Snapshot, and the study records exact source, data, policy, result, commit,
  and checksum identities.
- Existing experiment identities stay at their current paths and retain their historical meaning.
  Bug, safety, compatibility, and reproducibility fixes remain allowed; substantive improvement
  creates a new workflow-native research identity.
- The existing draft `strategy-forward-replication-research--v001` is revised as the first
  workflow-native workflow and released only after its new dependencies validate.
- Migration is incremental. There is no bulk move or rewrite of existing experiments or results.

## Authority model

```text
released policy versions ───────┐
maintained infrastructure ──────┼─> released workflow version
                                │              │
                                │              v
                                └──────> preregistered study
                                               │
workflow-native source ──> immutable definition snapshot
                                               │
                                               v
                                      immutable evidence
                                               │
                                               v
                                      independent conclusion
```

The workflow defines the research decision process. Policies define reusable constraints. Source
code implements behavior. A study records one governed execution. No one artifact silently assumes
the authority of another.

## Versioned policy registry

### Repository shape

Stage one introduces this tracked pattern:

```text
policies/
├── README.md
└── <policy-family>--vNNN/
    ├── README.md
    ├── POLICY.md
    ├── policy.yaml
    └── RELEASE.json
```

Supporting implementation and tests remain in their normal ownership boundaries:

```text
src/trading/policies/
tests/policies/
```

`policies/README.md` is the lifecycle registry. `POLICY.md` is the self-contained human contract.
`policy.yaml` is the validated machine-readable configuration. `RELEASE.json` pins the contract,
configuration, implementation paths, and conformance paths with SHA-256 digests and current-time
human approval evidence.

### Initial policy families

Stage one creates four narrowly scoped families:

| Family | Owns | Does not own |
|---|---|---|
| `us-equity-market` | Supported daily-bar market, XNYS sessions, information cutoff and price-observation constraints | Strategy signals or broker capabilities |
| `firstrade-manual-trading` | Supported manual order capabilities, account-facing restrictions and broker reconciliation assumptions | Simulated fill algorithms or portfolio allocation |
| `canonical-execution` | Entry/exit modes, fills, unfilled behavior, ambiguity, base/stress costs and execution evidence | Broker-specific UI instructions |
| `portfolio-risk` | Sleeve isolation, position, allocation, exposure and risk constraints | Signal selection or market-data availability |

Existing authoritative documents are inputs to these v001 contracts; they are not deleted during
stage one. Each rule is moved or referenced without weakening current fail-closed behavior.

### Lifecycle and resolution

Policy versions use one-way states equivalent to `draft`, `active`, `superseded`, `retired`, and
`abandoned`. Exactly one version may be active as the recommended version for a family, but every
workflow names an exact released version. Superseded or retired versions remain resolvable for old
workflow releases and studies; retirement only prevents new workflow releases from adopting them.

Release validation must:

1. validate registry identity, path, lifecycle, schema, and generated indexes;
2. validate the family-specific `policy.yaml` schema;
3. resolve every implementation and conformance-test path inside the repository;
4. run the declared conformance suite;
5. pin all contract, configuration, implementation, and test digests;
6. record a stable human approver and current UTC preparation time;
7. refuse later mutation of any released artifact or pinned dependency.

### Composition rules

- A workflow release lists exact `(family, version, release digest)` policy identities.
- Workflow prose may impose stricter research gates, but it may not override a selected policy's
  machine-readable values.
- A workflow needing different policy behavior selects another released version or policy family.
- Composition validation rejects duplicate families, missing required families, incompatible
  capabilities, and contradictory values before release.
- A policy change never rewrites an existing workflow or study. Adoption is explicit in a new
  workflow release.

## Workflow-native research source

Stage one reserves `src/trading/research_definitions/` for new formal research definitions. The
intended repeated pattern is:

```text
src/trading/research_definitions/<family>/<trial>/
```

The exact Python interfaces should reuse the current market-data bundle, execution engine,
Research Definition Store, snapshot store, result schemas, and trial registry rather than create a
parallel platform. A workflow study may reference multiple candidate definitions, but every formal
observation uses a permanent trial identity and an immutable definition snapshot.

Source is not copied into the study directory. The existing definition snapshot mechanism is
extended to include the exact selected policy release identities and their configuration digests.

## Legacy and maintained boundaries

### Legacy research artifacts

The following remain at their current paths and are logically frozen as research interfaces:

- existing packages under `src/trading/experiments/`;
- existing retained results and experiment overview documents;
- legacy experiment creation, execution, ranking, and documentation flows needed for inspection,
  reproduction, or bounded migration.

An explicit tracked inventory prevents a new package from being added to the legacy experiment
registry. Renaming an old package does not create a loophole. A substantive change to an old
strategy must create a workflow-native trial with provenance back to the legacy identity.

### Maintained infrastructure

The following are not legacy merely because they already exist:

- market-data provider, validation, cache, bundle, calendar, and snapshot services;
- execution, sleeve, accounting, ledger, reconciliation, qualification, drift, evidence, and
  workflow services;
- reproducibility schemas and immutable stores;
- safety checks, CLI infrastructure, and focused tests.

Infrastructure changes that can alter outcomes must update or version affected policies and
workflow dependencies. Semantics-preserving maintenance does not require a research study.

## Agent and CLI routing

- `AGENTS.md` and `CLAUDE.md` route all new research to workflow operation.
- `trading-launch-new-asset` and `trading-new-experiment` cease creating legacy experiment
  packages. Their compatibility disposition must be explicit: route workflow-native requests to
  `trading-operate-workflow`, while refusing an ungoverned new legacy identity.
- Legacy run, validation, documentation, and selection skills remain available only for existing
  identities and bounded migration or historical inspection.
- `trading-operate-workflow` records exact policy and definition identities and invokes only
  workflow-native creation paths for new trials.
- New `trading policy` commands validate, synchronize, release, and inspect policy versions. A
  release command requires explicit human approval and never implies commit, push, or merge.

## Rollout

### Stage 1 — Establish and enforce the boundary

Build the policy registry and runtime resolver, publish the four initial policies, create the new
source boundary, freeze the legacy inventory, update routing and documentation, revise the draft
workflow v001, and prepare it for explicit human-approved release. Do not migrate an experiment or
start a pilot study.

### Stage 2 — End-to-end pilot

Run one small new research study through pinned policies, preregistration, workflow-native source,
immutable definition capture, execution evidence, independent review, and completion. Correct
governance defects only through policy or workflow versioning.

### Stage 3 — Incremental adoption

Use the new model for every new research identity. Revisit a legacy strategy only by deriving a new
workflow-native trial. Extract reusable infrastructure as concrete needs arise.

### Optional Stage 4 — Legacy cleanup

Remove compatibility entry points only after repository evidence shows that they have no remaining
consumer and historical reproduction remains intact. This stage is not presumed necessary.

## Stage-one non-goals

- Migrating, renaming, moving, or deleting existing experiment packages or results.
- Running a new strategy study or drawing a research conclusion.
- Changing current qualification thresholds, execution behavior, or live-trading authorization.
- Contacting a broker or storing private trading data in tracked policy or workflow artifacts.
- Releasing a policy or workflow without a separately supplied stable human approver identity.

## Acceptance criteria

Stage one is complete when:

1. all four policy v001 definitions validate, have passing conformance tests, and are released with
   immutable identities;
2. workflow validation requires exact released policy identities and detects digest drift;
3. a synthetic workflow fixture proves that different workflows can pin different versions of the
   same policy family;
4. a formal definition snapshot contains the selected policy release identities and digests;
5. new workflow-native definitions are discoverable without entering the legacy experiment tree;
6. the legacy inventory check rejects additions and identity-renaming evasions;
7. repository skills and documentation route new research only through workflows and studies;
8. the revised strategy-forward workflow validates against the new policies and is ready for a
   separately approved release;
9. legacy commands and representative historical reproduction tests still pass;
10. workflow, policy, unit, lint, format, and architecture checks all pass.
