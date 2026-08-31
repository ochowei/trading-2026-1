# Govern Workflow Release Safety

Release-safety evidence coordinates a draft successor with its exact active predecessor. It does
not authorize release preparation, activation, study execution, outcome judgment, or trading.

## Open an assessment

Use this mode only when release preparation for a registered `N02` draft successor is blocked by
an unsafe unfinished predecessor study or a missing paused-study impact decision. Confirm that the
successor still names the active predecessor and that the predecessor's release authorizes
`workflow-release-safety-v1`.

Inspect every predecessor study and accepted-change impact record. Build a complete request from
`assets/requests/safety-assessment.json`:

- `blocking_studies` lists every exact predecessor study preventing a safe version boundary;
- `missing_impact_decisions` lists every paused study that lacks its required explicit disposition;
  and
- `reason` states why release preparation cannot proceed.

Show the exact request, successor path, expected `work/release-safety/saNNN/ASSESSMENT.json` pattern,
and validation plan. Obtain explicit confirmation before the add-only write, then run:

```bash
uv run trading workflow safety assess <draft-successor-path> \
  --request <safety-assessment-request.json> --by <identity>
uv run trading workflow validate --all
```

Query both exact versions again. The successor remains `N02`; a capability-aware predecessor with
an open assessment is `N06`. Stop without attempting release.

## Clear an assessment

Clear only the exact open `saNNN` after every listed blocking study is `paused`, `completed`, or
`cancelled`. For each paused study, require exactly one impact disposition authorized by
`impact.md`: continue on the predecessor, restart on the successor, or close as invalidated.
Completed or cancelled studies use the terminal resolution. Evidence paths must exist, be
repository-relative, and include the applicable accepted-change `IMPACT.md` whenever the
assessment recorded a missing paused-study decision.

Build a complete, one-for-one resolution request from `assets/requests/safety-clearance.json`.
Show the request, exact assessment path, expected `CLEARANCE.json`, and validation plan. Obtain
separate current human approval with a stable identity before:

```bash
uv run trading workflow safety clear <saNNN-path> \
  --request <safety-clearance-request.json> --approved-by <human-id>
uv run trading workflow validate --all
```

The guarded writer binds the clearance to the immutable assessment digest and rejects omitted,
duplicated, unsafe, or unsupported resolutions. Query predecessor and successor state again. The
predecessor returns to `N04` or `N05`, and the successor remains the same `N02` identity.

Do not prepare or activate the release automatically after clearance. Re-enter release preparation
through `references/release.md`, rerun all release checks, and obtain its separate human approval.
