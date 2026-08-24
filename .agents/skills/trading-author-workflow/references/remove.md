# Abandon, Retire, or Remove Workflow Material

Classify the exact target before proposing any mutation:

- **Unregistered local draft directory:** report its exact path and Git status. Keep it untouched;
  no generic workflow deletion command is authorized.
- **Registered draft:** use the guarded one-way `draft -> abandoned` transition. Preserve the
  registry entry and allocated identity permanently.
- **Active workflow:** retirement is the one-way `active -> retired` transition. Require explicit
  human approval, no blocking changes, and the safe-study checks in `impact.md`.
- **Superseded, retired, abandoned, or otherwise released history:** retain permanently. Never
  physically delete or rewrite it.
- **Imported source document:** follow the separately confirmed source disposition in `create.md`;
  it is not a workflow identity directory.

Do not infer permission to delete because the user says “stop using.” Resolve whether they mean
abandon, retire, leave an unregistered local draft untouched, or remove a separately supplied
source file. Show the exact resulting lifecycle and recoverability before acting.
