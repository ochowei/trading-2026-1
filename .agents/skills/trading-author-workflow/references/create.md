# Create or Import a Workflow Family

## Inputs and decisions

Accept repository Markdown/plain text or pasted text. Extract other formats before authoring. Read
the source without mutation and record its repository path, commit, and checksum when available.
Map claims to the complete contract in `core.md`; ask only about missing, proposed, or conflicting
decisions.

Confirm the immutable family slug and proposed `workflows/<slug>--v001/` path. Search the registry,
filesystem, repository references, and similar families. If the slug already exists, stop creation
and route to evolution. When a similar workflow must coexist, obtain explicit confirmation and pin
the exact `derived_from` workflow/version/path without inheritance.

An initial family always starts as `v001` with:

- `supersedes: null`;
- `source_changes: []`;
- exact selected policy versions;
- classified dependencies; and
- lifecycle status `draft`.

Never claim an imported workflow was historically active.

## Draft creation

Map confirmed decisions into every required `WORKFLOW.md` section. Use
`assets/requests/create.json` as the closed request shape and put the complete mapped contract at
its `definition_path`. Preview with `trading workflow create --request <path> --dry-run`; after the
user confirms that exact preview, run the same command without `--dry-run`. The façade allocates
`v001`, uses `assets/workflow-version/`, registers the draft, synchronizes indexes, and validates.
Do not add allocated IDs, lifecycle status, or timestamps to the request.

Do not create empty placeholder directories. Leave study creation to
`trading-operate-workflow`. A draft has no study, release, promotion, broker, or trading authority.

## Source disposition

Keep the source by default. Only after the draft validates, offer:

- `keep`;
- `move`;
- `replace-with-pointer`; or
- `remove`.

Before removal, show the exact path and Git status. Warn when untracked content is not recoverable
from Git, obtain explicit confirmation, and operate on the exact path without globs. Never treat
source-file disposition as permission to delete a workflow identity directory.
