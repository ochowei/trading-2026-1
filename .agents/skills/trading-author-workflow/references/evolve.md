# Evolve an Existing Workflow Family

## Released bytes and change identity

Never edit a released `WORKFLOW.md`, including editorial fixes. Record harmless corrections as
README errata and include them in a later version. Wording that may change interpretation requires
an expedited change and a new version.

Resolve the unique active version from the root registry. Allocate the next unused local `Cxxx`
under that exact version without reusing an existing committed or referenced identity. Use:

```text
<active-version>/work/changes/<change-slug>--cNNN/
```

Keep the legacy five-file change representation:

- `README.md`
- `PROPOSAL.md`
- `IMPACT.md`
- `VALIDATION.md`
- `DECISION.md`

## Change lifecycle

Use:

```text
draft -> proposed -> accepted -> released
                  -> rejected
                  -> deferred -> proposed
draft/proposed/deferred -> withdrawn
```

Complete proposal and impact before `proposed`. Complete validation and decision rationale before
`accepted`, `rejected`, or `deferred`; require a stable human identity for the decision. Only
workflow release may set `released` and `released_in`. Use guarded CLI transitions rather than
editing lifecycle metadata.

## Replacement draft

After one or more changes are accepted, create or update the single next-version draft. Every
substantive `v002+` rule must trace to accepted source changes. A release may aggregate multiple
accepted changes, but impact analysis must cover their combined effect.

Keep the replacement complete and self-contained. Do not implement inherited variants or copy
source change records into it; its metadata links back to the records under the version they
modify. Do not end, move, execute, or reinterpret studies while authoring the draft. Read
`impact.md` for version-boundary requirements.
