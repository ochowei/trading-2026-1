# Evidence: XLF Gap-Safe Rate-Volatility-Conditioned Pullback Research

## Execution record

### Authority and lifecycle

The human research owner approved Development execution in the conversation after preregistration.
The guarded lifecycle command moved this study to `running` under `ochowei@gmail.com`. Workflow and
policy validation passed before execution. The canonical source HEAD remained
`005500bea15f2a646c8b5b8a17afe5c46158c787`; dirty-worktree orchestration bytes were embedded in
formal observation provenance as required by v004.

No Historical (2021–2025) or Shadow outcome was loaded, calculated, displayed, or used. No
candidate freeze, robustness identity, broker access, order, or live authorization was created.

### Data refresh, snapshots, and pre-output gates

The first command performed the only provider full refresh, through the frozen Development cutoff:

```text
uv run trading research snapshot xlf-rate-volatility-conditioned-pullback-gap-safe/move-direction-cap-3 --workflow workflows/strategy-forward-replication-research--v004 --decision 2020-12-31
```

Cap-5, cap-7, and the ungated baseline used the same command with their respective identities and
`--reuse-full-refresh`; each reported reuse of the current eligible generation without provider
access.

| Trial | Snapshot ID | Definition fingerprint | Definition snapshot ID | Manifest SHA-256 |
| --- | --- | --- | --- | --- |
| cap-3 | `da65ed3874d1f9ba17d50930368a4fe829752849349c0973405d3e40e9e62836` | `f5b19cc7b7f3345d4a7e126ab7fe4cfa3f23d21fe164d92bcbea151e606c1948` | `faf53daaccfacd1277fd4013694cf21dd86e40bcf3d7e886e80318d22a6ff305` | `2eec48cbbfcc219c577a41c88fbbf52b346a70f9dc8e0d374e6e9902f8aa0e08` |
| cap-5 | `34209ec0c06d6514485f9dd03e7e1fead796484efef71fa3c669a52e804ede28` | `11297003061eb2d4c48e3fd10019f05e48cbbb72b460f1ac6de8e36db3cf5b60` | `f0b48bc1e45f0cc7a74bebb889fa8d01a6e15066a4111aab3f2ab505ec2008df` | `e3c43d4a77c83be82bac9eea93c676148b1eebf5d1726565c3f84e2670e28549` |
| cap-7 | `356de379708abef05e4f9e051c0e9ab1aeb74002a48752b4c9c1b961e7065fa0` | `8c0ea6baab1ff6ef9931d031280f25563835c8d337b69a71867b91b5cc9f0ede` | `7b89bda4a3d278b0eba460c47ec7fdad1e69fbdd9ce577d3c11c11b668a95c33` | `a8851419ddf7e94c40554152794dafaf2ed9292ecfee8b8d9b921902dd723fe5` |
| baseline | `9215c244786026551c7373531c4cc9af0965f03eee89f55e09c2669010422400` | `199a8b2ad157ed3bac3fbb75fabf6fc699789a4aa447e66ddf2b300a08854056` | `879282a3eb7abd215f304fc8290c1a25f644c09d9f1e93bdf1c93d719031f4dd` | `f7e30a0904c8663b94846bdc724d0f63afc4d1d7d28643edcd9b67d55494f4b9` |

Every manifest passed `trading data verify` and bound composite policy set
`cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`.
All four referenced the identical XLF blob
`af6329861950d026548df7295848822e797c658e3d57065e7b611ccfe2b5e3f7`;
all three gated manifests referenced the identical MOVE blob
`b74640452eb82a9451ff279f1835ae16c93e2317c5122aba25aaa2a66b22fd09`.
The gated manifests serialized `mark_unavailable`, publication lag one, maximum lag three, and
unknown publication time.

Before strategy output, provider-free bundle replay reproduced exactly three unavailable decisions:

| Decision | Observation | First available | Actual lag |
| --- | --- | --- | --- |
| 2013-03-21 | 2013-03-15 | 2013-03-18 | 4 |
| 2013-03-22 | 2013-03-15 | 2013-03-18 | 5 |
| 2013-03-25 | 2013-03-15 | 2013-03-18 | 6 |

Post-run proof confirmed none of these dates appeared in any gated raw signal, raw candidate, or
canonical trade. The unavailable inventory and suppression gate passed exactly.

### Failed first observation and bounded replay repair

The first cap-3 offline run failed before candidate output or result publication with:

```text
ValueError: aligned MOVE observations do not cover every primary session
```

The append-only registry retained failed observation
`c447f2a624a14e8691652fc5bfd5d208` under trial
`7ea4a12de658c427be39a74c40d47cd4b3201694301be2cd0115916e610f1533`.
Its snapshot was the same cap-3 snapshot above and `result_path=null`.

Read-only diagnosis showed that the immutable XLF full-refresh blob began 1998-12-22 while its
manifest declared 2002-11-13; MOVE's aligned decision view correctly began 2002-11-13. Snapshot
replay had failed to restrict the primary view to its declared history boundary. The repair changed
only `ResearchDataStore.load_snapshot` so a primary bundle begins at its manifest-declared first
XNYS session while auxiliary raw observations needed for first-decision publication lag remain
available. It did not modify the strategy, signal, trial configuration, workflow, policy, manifest,
or definition fingerprint.

The exact repair source SHA-256 was
`c46f410c6a5afadede55f83993d06e084d124f8dda29227d6cd3c0690ecf9c26` and its regression-test
source SHA-256 was
`bdfeef1b9055f2e52626926b5e6edcd9f78a0e2a7d284441b530f6fe09e9a33f`.
Thirty focused store, workflow-native definition, and CLI tests passed; Ruff lint/format,
`trading data verify`, and `git diff --check` passed. Documentation now states the same replay
boundary in the reference implementation document `docs/market-data.md`; the v004-pinned normative
`docs/reproducibility.md` digest remains unchanged.

The retry used the identical cap-3 manifest and fingerprint, so it appended an observation to the
same semantic trial rather than creating a fifth trial. The registry contains four family trials;
cap-3 has one failed and one successful observation, and each other identity has one successful
observation.

### Formal Development results

The exact offline run form for each identity was:

```text
uv run trading research run <identity> --workflow workflows/strategy-forward-replication-research--v004 --manifest <exact-manifest> --offline
```

| Trial | Valid result path | Result SHA-256 | Observation ID |
| --- | --- | --- | --- |
| cap-3 | `results/xlf-rate-volatility-conditioned-pullback-gap-safe--move-direction-cap-3/20260812_162957_960677_offline_c0d44538842d4724984c2d8229e0bb4c.json` | `dbc9a78b9a2b02d69157637b3e0095a41e0f9ca1670331b333585e65238bfe96` | `167c6d4a3c7b474682e4471d1c547b3f` |
| cap-5 | `results/xlf-rate-volatility-conditioned-pullback-gap-safe--move-direction-cap-5/20260812_163019_621267_offline_4b2cdf0496584fadaac3a56c39c531f4.json` | `16024a75ae3b3bacf78eac31077c5511e8974f6a0695b6d61d04366890b37593` | `3e5f62068ea443b3bed73d34ddf91401` |
| cap-7 | `results/xlf-rate-volatility-conditioned-pullback-gap-safe--move-direction-cap-7/20260812_163029_615628_offline_db4d64f82be542b7887795151bd66f7d.json` | `20d698ce15f94892b7aed05d00452fa6e22056643485488315d66c92dccb969c` | `9c64715d27af4f0dba135d654bbbc1e1` |
| baseline | `results/xlf-rate-volatility-conditioned-pullback-gap-safe--ungated-pullback-baseline/20260812_163031_478652_offline_55031c0952154fbdaaf13d20f2bddfd6.json` | `668991869a2533a30481a9a63a3cc049c8df8b750d9521716a3ef0d312f42d08` | `ff0598dcbd1b47e5af284ed081a1384b` |

Every result was schema-valid, used `canonical-sleeve-v1`, had no unclassified parity difference,
and embedded exact v004 observation provenance.

| Trial | Raw signals | Completed base trades | Traded years | Base return | Base PF | Stress return | Stress PF | Stress max DD | Base Sharpe | Sharpe advantage vs baseline |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| cap-3 | 62 | 38 | 16 | -3.9491% | 0.9547 | -14.9467% | 0.8279 | 54.2810% | 0.0705 | 0.0876 |
| cap-5 | 73 | 44 | 16 | -0.0958% | 0.9990 | -13.2169% | 0.8578 | 49.5332% | 0.0856 | 0.1027 |
| cap-7 | 86 | 47 | 16 | -29.1460% | 0.7291 | -39.0398% | 0.6288 | 54.2154% | -0.0240 | -0.0069 |
| baseline | 126 | 53 | 16 | -29.6694% | 0.7511 | -40.6408% | 0.6525 | 64.3654% | -0.0171 | 0.0000 |

All three selection candidates passed only the minimum completed-trade and traded-year gates. Each
failed base return > 0, base profit factor > 1.1, stress return > 0, stress profit factor > 1.0,
stress drawdown <= 15%, and Sharpe advantage >= 0.25. Therefore no Development candidate was
eligible; the frozen selection rule produced no ranking, winner, or candidate freeze. The two
reserved robustness identities were not materialized, and Historical access remained prohibited.

The append-only trial registry SHA-256 after these observations was
`069896c6e413c2997e5b8e45bc9e1006cb93f8ec4f4c89bec461b1c621c50d70`.

## Deviations and missing evidence

- The first cap-3 observation exposed the replay-boundary defect described above. The failed
  observation was retained; the repair preserved the same immutable manifest and semantic
  fingerprint and was verified before retry. This was an implementation/replay repair, not a
  favorable-result repair or research-design change.
- Development reached the frozen no-candidate stopping rule. Candidate-freeze, robustness,
  Historical Evaluation, and Shadow evidence are intentionally absent because advancement was
  forbidden.
- This evidence records the Development disposition but does not select the study's terminal
  outcome. Independent review must apply the preregistered rules; `CONCLUSION.md` remains untouched.
