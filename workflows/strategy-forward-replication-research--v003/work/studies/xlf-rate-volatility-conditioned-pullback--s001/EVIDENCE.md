# Evidence: XLF Rate-Volatility-Conditioned Pullback Research

## Execution record

The human research owner approved Development advancement in the conversation after the study was
preregistered. The guarded lifecycle command was:

```text
uv run trading workflow study transition workflows/strategy-forward-replication-research--v003/work/studies/xlf-rate-volatility-conditioned-pullback--s001 --to running --by ochowei@gmail.com
```

The workflow and policy validators passed immediately before and after the transition. The source
checkout remained at complete Git HEAD
`0ae8f4f6a23ef4ebd3e4666cab626e6519821b52`; dirty-worktree source bytes were retained by each
Research Definition Snapshot as required by the repository reproducibility contract.

The first attempted refresh commands were rejected before provider access or cache mutation
because the CLI prohibits combining `--full` and `--start`:

```text
uv run trading data refresh XLF --full --start 1998-12-16 --end 2020-12-31
uv run trading data refresh '^MOVE' --full --start 1998-12-16 --end 2020-12-31
```

The corrected primary refresh completed with 5,543 XLF rows through the frozen Development cutoff:

```text
uv run trading data refresh XLF --full --end 2020-12-31
```

The equivalent generic MOVE refresh was rejected because that command applies primary/XNYS-
complete coverage and MOVE does not publish on every XNYS session. The formal research-snapshot
path subsequently refreshed MOVE successfully with the definition's frozen
`provider_observations` coverage policy; no missing observation was synthesized or forward-filled.

Four Development-only manifests were published with decision session 2020-12-31 and composite
policy set `4ade828a43e2cfab97b2933c5722107cf00ccf27c3a90c92b60c19b67f511189`:

| Identity | Snapshot ID | Definition fingerprint | Manifest SHA-256 |
| --- | --- | --- | --- |
| `move-direction-cap-3` | `30f8f9373b6d98deba36ffd67714ca2b2aa6daf185592ce8711b6137b86146e7` | `ff0f12a791115f2145b56d4e50676935ee3000599e70b7dd3f0bf18fb2e2d032` | `9d22138b28f5642e5ddcc746b0200ed84b1da5e9d34796fd8b85b45e9387e8e6` |
| `move-direction-cap-5` | `625da0402cef96d60b88552cbee0f789337ab931d182def15ae87d47e217adcd` | `3405fa1f527b5ea192a72c7a2189ddba90e6500db9b2a339e8d803032c11d2b2` | `f947cdbc952f728f0b82dcf53c7e2f4abaf554606d7a1bc493fdeeac2839ab12` |
| `move-direction-cap-7` | `5b71219ae035c35e5279b71b678da3bef890136f652e2df44f2fd27644a83fee` | `d838f653883e7e2ab7cb26f7c6a0a76955552596f201fbe38f44fea16ffb67ff` | `812c10b10e478d12f14a1772a165219becd583a8dc996f5f5e806acbc40a3332` |
| `ungated-pullback-baseline` | `dccecf3a0b20311d5d60fa89e5bd7551bf98eaf098a9dc153473fc183b70d556` | `de7af4e15ebdd07ebb22e984b7845ed296db2ae16e281e2c43495fd0adcfdf4a` | `e26a1437bede40f269c5607188cf2b6dd9c7ee74665e6b95f006b122cbdb768f` |

Each manifest declares `history_start=1998-12-16`. Each of the four frozen offline run commands
failed before strategy output or result publication with the same exact error:

```text
research error: XLF history starts at 1998-12-22, after required session 1998-12-16
```

The attempted commands were the canonical `uv run trading research run <identity> --workflow
workflows/strategy-forward-replication-research--v003 --manifest <manifest> --offline` form for all
three candidates and the baseline. No result JSON was published, the trial registry was unchanged,
no Development metric was calculated or inspected, and no 2021-2025 Historical data or outcome was
obtained.

Advancement was stopped through:

```text
uv run trading workflow study transition workflows/strategy-forward-replication-research--v003/work/studies/xlf-rate-volatility-conditioned-pullback--s001 --to paused --by codex-primary-researcher-xlf-s001 --reason 'Frozen XLF history_start 1998-12-16 precedes Yahoo first observation 1998-12-22; all Development runs fail closed before result publication'
```

## Deviations and missing evidence

- The frozen XLF history requirement cannot be satisfied by the provider: the first verified Yahoo
  observation is 1998-12-22 rather than the required 1998-12-16. Changing the date would alter the
  preregistered data requirement and is prohibited in this study.
- The plan called for one full refresh. The standard `research snapshot` command performs a full
  refresh per identity, and the four manifests consequently captured four distinct XLF blob
  digests despite identical row counts and cutoffs. Because every run failed before output, these
  blobs were never compared, ranked, or used as outcome evidence. A future study must resolve the
  common-data-generation contract before execution rather than repairing this frozen round.
- Development eligibility, complete candidate ranking, candidate freeze, robustness definitions,
  Historical Evaluation, and Shadow evidence are all absent. The study is paused; no outcome has
  been selected or asserted by the operator.
