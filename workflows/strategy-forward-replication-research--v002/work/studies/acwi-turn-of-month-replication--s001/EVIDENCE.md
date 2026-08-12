# Evidence: ACWI Turn-of-Month Replication

## Execution record

### Preregistration and lifecycle

- Preregistration approved by `ochowei@gmail.com` at `2026-08-12T09:04:04.718989Z`.
- `PREREGISTRATION.json` pins workflow SHA-256
  `4dfa7df8244744aab3219c1a0784aee8af9ca559c059e5cb659aa6088b7789be`, hypothesis
  SHA-256 `70e817e517a5335a9da34c60aed4696c08f85b81b2d17dc681e40bd50392c5c3`, and plan
  SHA-256 `c23807cc0b0644d907b5402d69c1e99d3a119d0c9216b7eb03f66c6ef4619475`.
- Transitioned to `running` at `2026-08-12T09:09:47.570875Z` by
  `codex-primary-execution-agent`.
- Execution checkout HEAD: `1faf4387ac110eb9ffb36b25b8fa86c6a4893dd1`. Outcome-relevant new source
  was present as captured dirty-worktree content and is identified below; no commit was created.

### Workflow-native source validation

- Reusable source: `src/trading/research_definitions/monthly_calendar.py`, SHA-256
  `41258334d81daa1a5843cb960bfe5fb19aec3ce4fced12009a7d065969997e38`.
- Candidate source SHA-256 values:
  - `enter-minus-two-hold-five`: `564860f55caa5c7a4576a4d0f66562b1524385f664297078f2a6f3b56f67c39d`
  - `enter-minus-one-hold-five`: `813416ce59861374398bc47aee31e4b3b0fe13b0e4b9f93370f64efb7cee5023`
  - `enter-month-end-hold-five`: `d30cb936731c62d6e463c062fd59eb698c6eb5b2813ae0cf0577c39c7eb4f081`
- Baseline source `enter-session-ten-hold-five`: SHA-256
  `fa6f7fe3a767a71202e6095b6e90b52391a01d4f4ea67629b29befbd55799de6`.
- Focused workflow-native research and policy tests: `37 passed`; legacy inventory guard, policy
  validation, workflow validation, Ruff lint/format, and `git diff --check` passed before the first
  ACWI refresh. Monthly-calendar test source SHA-256:
  `d283fe4d50f879224c5333cfbe83ee9413252dc7b2ca05d9d05c4f95349de24f`.
- All four definitions resolved the frozen composite policy-set identity
  `4ade828a43e2cfab97b2933c5722107cf00ccf27c3a90c92b60c19b67f511189`.

### Development snapshot capture

The following commands performed full refreshes capped at decision session `2020-12-31`. Each
manifest records ACWI data cutoff `2020-12-31`, required history start `2008-03-26`, data blob
digest `87014fcef33a10feb89d227f6ddd2253d4de3e0998e9d89fe179d2f287621a0c`, and 3,215 rows.

| Trial | Snapshot ID | Definition fingerprint | Manifest SHA-256 |
| --- | --- | --- | --- |
| `enter-minus-two-hold-five` | `24c0330b0bddd4d929a261b4837990c58574a6ccec43b9aa65eb04bf93f8c5ac` | `11c1c8c90a4c1458eabc81d76ee9ce31a1b316a89f972fe8502636685331c88c` | `8486e28a26bc9fc30dbfba944db010c9ef3b5c62566b52116b2721f42655c218` |
| `enter-minus-one-hold-five` | `9f9242dc671d979ee41d68202427731b760f4768f5c4a96932bd36491a8e733d` | `1e7a1874f8799b1a6caeeb51c3f02aa0eb29f80f0e8993dbb7672793d5172c01` | `fb38c403bb65de2dff0e8f5d296c8503dc705aee00ae603a35045636aacbe8fb` |
| `enter-month-end-hold-five` | `fb23fee27b259f1239c081f2bb33c43ac3ae113c559b305224b6414da94bef96` | `053d18d586eb2a96238aaf8290f140816da3303de107df95f2a753eff39d4d2e` | `376fef130b604489fcce6a89fff978269603627dc2fafff66f7fc46a3503aaea` |
| `enter-session-ten-hold-five` | `cc1c3bf05f57840608a8efad34a28e09158d9dea5903e9dd9a19d5a8ba16716c` | `bc8635a33044ab087250ba3dbb0a290905546e7a03b2d2bcc1aae0c7fbba77d2` | `c2424bb5bd24ef27ec6c008e0dec2cea2c3440fe0aa2cc6951a5ba680e38982b` |

### Fail-closed Development execution

All four preregistered offline runs and subsequent `trading data verify` calls stopped before
strategy execution with the same exact error:

```text
ACWI history starts at 2008-03-28, after required session 2008-03-26
```

The provider returned no rows for the first two required XNYS sessions after the plan's stated fund
launch/availability date. The market-data coverage guard therefore refused to construct a bundle.
No result file, formal observation, candidate metric, eligibility decision, or ranking was
produced; `results/trial_registry.json` remained unchanged. In particular, no 2021-2025 Historical
outcome was refreshed or inspected.

The study was transitioned to `paused` at `2026-08-12T09:12:45.790763Z` by
`codex-primary-execution-agent`, with the exact coverage failure as its reason.

## Deviations and missing evidence

- No frozen hypothesis, plan, threshold, candidate, cost, execution, or data-role date was changed.
- The discovered first provider row (`2008-03-28`) conflicts with the frozen required history start
  (`2008-03-26`). Changing that date after preregistration is prohibited by the frozen plan, even
  though the affected interval is availability/warmup rather than performance evidence.
- Development outcome evidence is missing because all four bundles fail exact coverage validation.
  The same study cannot resume by silently changing its required start. The lawful repair is to
  cancel this study and create a new v002 study with an exact `revisits` link and a corrected,
  explicitly approved preregistration; alternatively the human owner may terminate the research.
