# Evidence: FXI ATR-Divergence Mean-Reversion Forward Replication

## Execution record

### Authority, lifecycle, and scope

The human owner preregistered this study and separately authorized Development execution as
`ochowei@gmail.com`. The guarded lifecycle moved the study to `running` under that identity.
Workflow and policy validation passed before execution. The canonical source HEAD was
`10bec55a4756e0606adc72447b6ca42dd819397c`; formal results embed exact dirty-worktree source bytes
in their v004 observation provenance.

Execution was restricted to the frozen 2015-01-02 through 2025-12-31 Development role. No 2026
quarantine or 2027-2031 Historical outcome was loaded, calculated, displayed, or used. No
robustness observation, candidate freeze, broker access, order, or live authorization was created.

### Data, snapshots, and formal observations

The first sandboxed full-refresh attempt failed on provider DNS resolution before publication. An
authorized retry used the identical FXI/ASHR dependencies and 2025-12-31 cutoff, and succeeded.
It published FXI blob
`3b0ac386be05736e73b6f501a91dd0ff978bafc223f588855a9b7b47d91e31ef` (5,342 rows) and ASHR blob
`c83c34a8669a39a6aed4334156e2bf8aaf1031ba63fc0067d38b738b90f60f02` (3,056 rows). The baseline
snapshot reused that full-refresh generation without provider access. Both manifests used decision
session 2025-12-31 and composite policy set
`cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`.

| Trial | Snapshot ID | Definition fingerprint | Definition snapshot ID | Manifest SHA-256 |
| --- | --- | --- | --- | --- |
| ATR/ASHR candidate | `aa66c1529f194fc5ee9a1e7c4c73743bcf45a20f4a7b3b01240ea6ece1e418c2` | `c4d9224c978202c291620393bcbef7d5d4dd07a2418db150d3565d78002609a0` | `318526d60aafb2b3eeca9f5ff39b1930a54c63bdb0ce25486375125ced8713f1` | `5b02562742605f49f14883bf5befaa6a1977f6d5327964acecc6964af03ec0e5` |
| pullback/WR baseline | `8c961eb540df3c13912dafce04d1ada5e9989750ea6e24211ca0f08ef0659c84` | `07c307d96f6295632d16661979661c15e8768e7527501ce58f75333234d57042` | `0a7f1fb06747b9e98c521868aebb4f42701397825da4231c03a2a067de303687` | `5425097d9c3627c22f1db7e8a0def1acd7f415097fbd2bddc6b746be3050c293` |

| Trial | Result path | Result SHA-256 | Trial ID | Observation ID |
| --- | --- | --- | --- | --- |
| candidate | `results/fxi-atr-divergence-mean-reversion--atr-band-ashr-divergence/20260813_015202_875612_offline_8b3e2834f6024c2e847250e03673edab.json` | `4429dbff84a8d4e107df8322f7516e0f76aa55e6829a987ce2288ca3f237497f` | `68badeb86f494ab5931630e7c57e36afc501f68faa14cc17229ec0958e4a1118` | `05e46a5826b1434e90532c94df7580b1` |
| baseline | `results/fxi-atr-divergence-mean-reversion--pullback-wr-baseline/20260813_015158_960648_offline_8773639ef21e422681d3a2778a2a634f.json` | `f7937906f3d358a2ba61e2f699be5a85ac21b5469f7c22ca1f51bb16188f6c02` | `fc369cb7130c4695ce963894a52d6c6a05336ddb7ac85f706ba0189b3b12c3e9` | `566468efa23242338127be34054295b1` |

Both results are schema-valid, provider-free offline observations using `canonical-sleeve-v1`.
Profit factor is total positive canonical-sleeve cash P&L divided by absolute total negative cash
P&L. The append-only trial registry SHA-256 after both observations was
`121384d4936c2d72fec888ee0ed14f9b9e2f652e946108833dfb8768912e306c`.

### Deterministic Development gate

| Trial | Raw signals | Completed / years | Base return / PF / Sharpe | Stress return / PF / max DD |
| --- | ---: | ---: | ---: | ---: |
| candidate | 34 | 33 / 11 | 111.8162% / 3.2306 / 0.7809 | 90.5889% / 2.7454 / 15.0886% |
| baseline | 98 | 86 / 11 | -0.0881% / 0.9996 / 0.0677 | -24.1249% / 0.8867 / 44.6110% |

The candidate passed the trade-count, traded-year, base, stress, baseline-retention, Sharpe-margin,
stress-drawdown-comparison, and exact-integrity gates. Before cooldown and occupation selection,
there were 387 baseline-eligible entries. The ATR ceiling uniquely suppressed 17 entries across
five years, satisfying its frozen 10-entry/five-year floor. The ASHR gate uniquely suppressed only
six entries across four years (2015, 2019, 2021, and 2022), failing the same floor.

The sole candidate is therefore Development-ineligible under the frozen conjunctive rule. The
deterministic gate artifact is
`results/fxi-atr-divergence-mean-reversion--development-gate/s003.json`. The stopping rule forbids
threshold tuning, robustness execution, candidate freeze, and Historical access.

## Deviations and missing evidence

- The failed sandboxed refresh and identical authorized network retry were operational events, not
  semantic trials, design changes, or outcome-informed repairs.
- Candidate-freeze, robustness, Historical Evaluation, and Shadow evidence are intentionally absent
  because Development reached the frozen stopping condition.
- This file records deterministic gate evidence but does not decide the terminal study outcome.
  Independent review must apply the preregistered rules; `CONCLUSION.md` remains untouched.
