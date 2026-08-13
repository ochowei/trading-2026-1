# Evidence: XLF Close-Armed Profit-Protection Pullback Research

## Execution record

### Authority, lifecycle, and scope

The human research owner preregistered this study as `ochowei@gmail.com` and later approved the
separate Development execution in the conversation. The guarded lifecycle command moved the study
to `running` under researcher identity `codex-primary-researcher-xlf-profit-protection`.
Workflow and policy validation passed before execution. The canonical source HEAD remained
`ef1713123d4063268221ac53a7f44b117befff5e`; dirty-worktree orchestration bytes were embedded in
formal observation provenance as required by v004.

Execution was restricted to XLF Development data through 2020-12-31. No 2021-2025 Historical or
Shadow outcome was loaded, calculated, displayed, or used. No robustness snapshot or observation,
candidate freeze, broker access, order, or live authorization was created.

### Data refresh, snapshots, and pre-output gates

The only successful provider full refresh was explicitly bounded to the frozen Development cutoff:

```text
uv run trading data refresh XLF --full --end 2020-12-31
```

It published 5,543 adjusted-daily rows through 2020-12-31. Candidate and baseline snapshots were
then created with `--reuse-full-refresh`, so neither snapshot command performed provider access:

```text
uv run trading research snapshot xlf-close-armed-profit-protection-pullback/close-armed-2-floor-0p5 --workflow workflows/strategy-forward-replication-research--v004 --decision 2020-12-31 --reuse-full-refresh
uv run trading research snapshot xlf-close-armed-profit-protection-pullback/fixed-ten-session-baseline --workflow workflows/strategy-forward-replication-research--v004 --decision 2020-12-31 --reuse-full-refresh
```

| Trial | Snapshot ID | Definition fingerprint | Definition snapshot ID | Manifest SHA-256 |
| --- | --- | --- | --- | --- |
| close-armed candidate | `a53e7d14cd403881edf36da8a6a64fcfce2b8d3966a95f57a783c03e7fef6aec` | `481167b2b2664a460a4308c28cd13d6d986dc51f60e5533c56e9550156b5ca6d` | `5b2d66b14ec8c310b826aa0be5a7d14f05f2cf71f9310e28100c8cbe2a537c0d` | `e673c1debb176f66e0486b7891619b1d2c9c4bc88b831062520bf8ec66ab23bd` |
| fixed-ten-session baseline | `42ac8896d924c49dbe8299a49d40e5b8ea8e423a490bb394b98ec2caa3e5f8f7` | `3b696b87c4308164c4849d89417d6ccbdc07b3d0c7a3bc134f13e8d1941169d5` | `58641cd737b7f613d321963c25025e1b110f9daeef1488ff9731b5dd45f26d95` | `592e688f9ea5c2e63bf41a1c577dc5b08b1106b6d35bcd1a5c49c72e1070c7db` |

Both manifests passed `trading data verify`, bound composite policy set
`cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`,
and used decision session 2020-12-31. They referenced the identical XLF blob
`fe345d420fe757175af9df985e553b603c155f350f87a647375a1a6aa2645763`
with declared history start 2002-11-13 and cutoff 2020-12-31. Before outcome comparison, exact raw
signal, accepted-entry, occupation-lock, policy, workflow, data, definition, and provenance
bindings were verifiable.

### Formal Development results

The exact provider-free run form for each identity was:

```text
uv run trading research run <identity> --workflow workflows/strategy-forward-replication-research--v004 --manifest <exact-manifest> --offline
```

| Trial | Valid result path | Result SHA-256 | Observation ID |
| --- | --- | --- | --- |
| close-armed candidate | `results/xlf-close-armed-profit-protection-pullback--close-armed-2-floor-0p5/20260812_181958_204512_offline_bd0fbd95dfe1430e8190610c3396da78.json` | `93dda30affa1a05c031ef3294e8b9d0bddb285ce0988d2d127270720faf7d664` | `f78a00958686450a906e845b74346185` |
| fixed-ten-session baseline | `results/xlf-close-armed-profit-protection-pullback--fixed-ten-session-baseline/20260812_182009_048535_offline_9452bb4a656146f88efe2fa6ab7b5a2f.json` | `92a0b7dced06b10fa4457c15347ad51f9290d00f6f9fc0ad2ed5d9950e1047ed` | `83e3844d6e55441faeadcc351fb20aed` |

Both results were schema-valid, used `canonical-sleeve-v1`, and embedded exact v004 observation
provenance. Profit factor below uses the repository qualification convention: total positive
canonical-sleeve cash P&L divided by the absolute total negative canonical-sleeve cash P&L.

| Trial | Raw signals | Completed trades | Traded years | Protection exits / years | Base return | Base PF | Stress return | Stress PF | Stress max DD | Base Sharpe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| close-armed candidate | 126 | 53 | 16 | 15 / 11 | -34.5691% | 0.6929 | -44.7762% | 0.5955 | 63.7548% | -0.0804 |
| fixed-ten-session baseline | 126 | 53 | 16 | 0 / 0 | -29.6695% | 0.7511 | -40.6409% | 0.6525 | 64.3654% | -0.0171 |

The candidate and baseline had identical 126 raw signals, identical 53 accepted entries, and
identical 73 occupation-lock skips. The candidate therefore passed the completed-trade,
traded-year, protection-exit-count, protection-exit-year, and cohort-parity gates.

Every outcome gate failed:

- base return was -34.5691%, not greater than zero, and base PF was 0.6929, not greater than 1.1;
- stress return was -44.7762%, stress PF was 0.5955, and stress drawdown was 63.7548%, failing all
  three stress thresholds;
- candidate base return was below the required 90% baseline-retention threshold, while candidate
  Sharpe minus baseline Sharpe was -0.0632 rather than at least +0.10;
- candidate stress drawdown magnitude was 99.05% of baseline, not at most 85%; and
- aggregate paired base-net advantage on the 15 protection-fired trades was -0.082528, with only
  7 of 15 paired differences positive, rather than greater than zero in aggregate.

The sole candidate was therefore Development-ineligible under the frozen conjunctive rule. The
rule permits no threshold tuning, cohort selection, MOVE cap, alternative holding horizon, or
robustness substitute. The round reached its preregistered no-candidate stopping condition, so the
three robustness identities were not materialized and Historical access remained prohibited.

The append-only trial registry SHA-256 after the two successful observations was
`fb67ec3bd02c288c7d3702554836fec9f6abe961cc10beb2bccb141fc4d4471d`.

## Deviations and missing evidence

- The first sandboxed full-refresh attempt failed on provider DNS resolution before publication.
  The authorized retry used the same command, ticker, and 2020-12-31 cutoff and succeeded. This was
  an operational network retry, not a semantic trial, design change, or outcome-informed repair.
- Development reached the frozen no-candidate stopping condition. Candidate-freeze, robustness,
  Historical Evaluation, and Shadow evidence are intentionally absent because advancement was
  forbidden.
- This evidence records the Development gate results but does not select the study's terminal
  outcome. Independent review must apply the preregistered rules; `CONCLUSION.md` remains untouched.
