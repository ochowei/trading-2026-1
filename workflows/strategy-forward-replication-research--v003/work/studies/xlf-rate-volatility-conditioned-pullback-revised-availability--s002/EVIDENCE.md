# Evidence: XLF Rate-Volatility-Conditioned Pullback Revised Availability Research

## Execution record

The study entered Development at `2026-08-12T13:31:18.843794Z` under authority
`ochowei@gmail.com`. The frozen preregistration identities were:

- HYPOTHESIS SHA-256: `b2060cd4a5131090906876d4a3a64d8e1c20bef7a1383e6544d97d7c01355766`.
- PLAN SHA-256: `5cc56fed37ccb68240ed5715e6dafb9b730c0bf6a6bfdc7546bd0f6d923dc596`.
- PREREGISTRATION SHA-256: `143f4beac78f8a2072bf9d40a45c46ea83b8997034d6e15ce676138a776bcf99`.
- Git HEAD at snapshot preparation: `0ae8f4f6a23ef4ebd3e4666cab626e6519821b52`.

The exact snapshot commands were:

```text
uv run trading research snapshot xlf-rate-volatility-conditioned-pullback-revised-availability/move-direction-cap-3 --workflow workflows/strategy-forward-replication-research--v003 --decision 2020-12-31
uv run trading research snapshot xlf-rate-volatility-conditioned-pullback-revised-availability/move-direction-cap-5 --workflow workflows/strategy-forward-replication-research--v003 --decision 2020-12-31 --reuse-full-refresh
uv run trading research snapshot xlf-rate-volatility-conditioned-pullback-revised-availability/move-direction-cap-7 --workflow workflows/strategy-forward-replication-research--v003 --decision 2020-12-31 --reuse-full-refresh
uv run trading research snapshot xlf-rate-volatility-conditioned-pullback-revised-availability/ungated-pullback-baseline --workflow workflows/strategy-forward-replication-research--v003 --decision 2020-12-31 --reuse-full-refresh
```

The first command performed the sole provider refresh. The three reuse commands reported that they
reused the current eligible full-refresh generation. The resulting immutable identities are:

| Trial | Snapshot ID | Definition fingerprint | Manifest SHA-256 |
| --- | --- | --- | --- |
| cap-3 | `a7d4e384297927f879577aac45990c3c72b0a3413d1dc984b9aab3307d4e626f` | `08136553724e3750cac545cd711e3c20f3a2f4b6f87fd5ecb403aaefe73da6e5` | `4dcd7594f4368ce874c54daceb22585640a010245020a70305a344a634d95ae5` |
| cap-5 | `27b6d57615cf1ca31cb948ed0853914e13f54798815588e032393cb7823910d6` | `6e74fffb24df10b16520a5f29bcb250f39dd458576c77bdb6c8ff54ad797a143` | `393a362a4258fe25cc41bb7ee32080184da963ea464aabcd49f8212e6401aed1` |
| cap-7 | `7c56775006d40c8c2b61c6ebda2345b6c3c8a86e789322d07878b1c1378a2e6c` | `cb568be4a6ec74f84d540eb1b63f3c4567d716e854be050583029be7655987dc` | `be43ab14116fb4c4eada498a36acc89ea25010ae410edc5668c5f1d5854ad5f5` |
| baseline | `b6ae26dc45ec026562144370ea982f63a3c39f0acc9d20af88429c9ef04ffc3b` | `94d8fa71cce0fa55f23c1068af85f66d7c27c16d26513b0a3efdb6aba453c31e` | `918d4e3e037f3a668e1aaec42c734995c7009e303bcda7d610f2e7a446a7cc8c` |

All four manifests bind the identical XLF data blob
`a560933fe3882fbe78682d8e6b260144e3659c268d9052e1d9373056050e4e76`. All three gated manifests
bind the identical MOVE data blob
`b74640452eb82a9451ff279f1835ae16c93e2317c5122aba25aaa2a66b22fd09`. The frozen common-data
identity condition therefore passed.

The baseline manifest passed `uv run trading data verify`. Each gated manifest failed verification
before execution with the exact availability error:

```text
trading.market_data.bundle.MarketDataAvailabilityError: ^MOVE history starts at 2002-11-12, after required session 1998-12-22
```

No `trading research run` command was issued. No result JSON, trial-registry observation, metric,
candidate eligibility decision, ranking, candidate freeze, or Historical outcome was produced or
viewed.

## Deviations and missing evidence

- Yahoo's verified MOVE history begins on 2002-11-12, later than the frozen S002 auxiliary
  requirement 1998-12-22. The three gated snapshots therefore cannot construct a legal bundle.
- Correcting the auxiliary start or changing the warmup/Development boundary is outcome-relevant
  and cannot repair this preregistered study. Advancement stops fail closed before any run.
- Development metrics, complete candidate ranking, candidate freeze, robustness definitions,
  Historical Evaluation, and Shadow evidence are absent.
