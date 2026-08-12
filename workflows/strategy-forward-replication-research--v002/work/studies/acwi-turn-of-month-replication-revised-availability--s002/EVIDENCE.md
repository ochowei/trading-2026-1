# Evidence: ACWI Turn-of-Month Replication — Corrected Availability

## Execution record

S002 was preregistered by `ochowei@gmail.com` at
`2026-08-12T09:25:33.879111Z`. The frozen hypothesis SHA-256 is
`f3d2bfd44a9e897da38cc8451fa7dca452f2fa2ccbbbb2a4bb64006c9bfafeb1` and the
frozen plan SHA-256 is
`982ab5dc4fda45e16c52bbd90e785acda21e1474e7d9095f4d337923cf472b0f`.
Execution was performed by `codex-primary-execution-agent` after the study transitioned to
`running` at `2026-08-12T09:28:58.350690Z`.

Only the frozen Development period, `2009-01-01` through `2020-12-31`, was observed. The Yahoo
auto-adjusted ACWI primary series begins on `2008-03-28`; rows before 2009 were retained only for
availability/warmup and made no performance contribution. All formal observations used
provider-free offline replay, `canonical-sleeve-v1`, the exact composite policy set
`4ade828a43e2cfab97b2933c5722107cf00ccf27c3a90c92b60c19b67f511189`, base costs of 5 bps
slippage plus 1 bp fee per side, and stress costs of 20 bps slippage plus 2 bps fee per side.

### Immutable Development observations

| Role | Research definition | Definition fingerprint | Snapshot ID | Result SHA-256 |
| --- | --- | --- | --- | --- |
| candidate | `acwi-turn-of-month/enter-minus-two-hold-five` | `9ea3a69d2a97701b3a390373db7b9f38566be09a563bd3123c6fd5157702bb5a` | `51137539f3bec6a8435a713dfa53aea76b3be43995e21b26187e0447c7de47b9` | `c9c90d4a085762b262ab2a404f49d0773f7739a652deba9ed4865a5edbfea9ac` |
| candidate | `acwi-turn-of-month/enter-minus-one-hold-five` | `584645817fbe9b0bc80302f65358a361f2a1da05f0c1f74c97f145210457706a` | `78c34b037e244fbf23806d2efe6ccf81a144077c49cff9b6169d06d2e3413339` | `b4f2c0faaa7015dfcad3627d6cc3a93c745e93418e744815a7bdc391556aeabb` |
| candidate | `acwi-turn-of-month/enter-month-end-hold-five` | `7ce804ad2fa9c4c58a82d50160faef585a11b3925b2b89c7462f7f03f6a48fdc` | `7bff8247f47fbc7149ec13ee72d9aea813ddd393f5576af6544a73de9e646378` | `6345d900e8a3d96989221bf4d860be5c00d319d4e188e8bec83c97401a189b1c` |
| baseline | `acwi-turn-of-month/enter-session-ten-hold-five` | `a051f6c7eaac628bb4e366d7dbadd0e14d9df3ba655b6f9a6f7440d90db05ca5` | `fb6499caaf72471b41bc08b496bd51b7c66cf5b62e03f287bc31ff0020600e7f` | `f7e50785131f0e208c9899900d66d74005cedd0390d6f19a6e69b06b14242071` |

The result paths, in table order, are:

- `results/acwi-turn-of-month--enter-minus-two-hold-five/20260812_093052_356121_offline_c15a67fa7fc74afb9d03d5c61375c9a8.json`
- `results/acwi-turn-of-month--enter-minus-one-hold-five/20260812_092953_932291_offline_8e59fa530cde40adb48296b5300c44d7.json`
- `results/acwi-turn-of-month--enter-month-end-hold-five/20260812_092955_472108_offline_06015f06a8184a61a9892bf83cd4e466.json`
- `results/acwi-turn-of-month--enter-session-ten-hold-five/20260812_092957_005514_offline_3b8311bf878141deb13099d6346fdcef.json`

Each immutable bundle passed `trading data verify`; each result reports `valid`, has no
unclassified parity difference, resolves the frozen policies, and is capped at `2020-12-31`.

### Frozen Development gates

Profit factor was recomputed from canonical completed trades as gross positive realized P&L divided
by the absolute gross negative realized P&L. Annual positive-profit concentration uses each positive
calendar year's net realized P&L divided by the sum across positive years. All candidates have at
least one completed trade in every Development year. The maximum annual trade share is 12/143
(`8.39%`) for each candidate.

| Candidate | Trades | Base return | Base PF | Base Sharpe | Sharpe minus baseline | Stress return | Stress PF | Stress MDD | Max positive-profit year share | Eligibility |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `enter-minus-two-hold-five` | 143 | 18.5110% | 1.1367 | 0.2015 | 0.1784 | -25.0062% | 0.8073 | -43.8624% | 29.64% | ineligible: stress return, PF, and MDD |
| `enter-minus-one-hold-five` | 143 | 33.5972% | 1.2308 | 0.3128 | 0.2897 | -15.4597% | 0.8881 | -38.6175% | 38.56% | ineligible: stress return, PF, and MDD |
| `enter-month-end-hold-five` | 143 | 30.9566% | 1.2273 | 0.2805 | 0.2573 | -17.1307% | 0.8692 | -42.2878% | 46.85% | ineligible: stress return, PF, and MDD |

The distinct baseline has base-net return `-2.6326%`, profit factor `0.9758`, and daily-equity
Sharpe `0.0232`. All candidates clear the base return, base profit-factor, baseline-spread, trade
count, annual coverage, concentration, identity, and parity gates. None clears any of the three
stress gates: stress return greater than zero, stress profit factor greater than 1.00, and stress
maximum drawdown at least `-15%`.

Consequently there is no eligible candidate to rank or freeze. This reaches the preregistered
Development stopping condition. The robustness-only definitions were not materialized, no
Historical snapshot was captured, and no 2021-or-later outcome was inspected.

## Deviations and missing evidence

The first S002 snapshot attempt for `enter-minus-two-hold-five`, snapshot
`74beeafe7ba8b4a1341a339f2d682711ad2ed5af203ce736d8f2a0aff6e971a2`, exposed a source defect:
the monthly offset generator treated the provider's partial first month as a complete month and
attempted to address an unavailable `M-2` session. Execution stopped before producing a result or
metrics. The generator was repaired to skip a month unless it contains enough sessions for the
requested negative offset, and a focused regression test was added. The successful M-2 observation
uses the new fingerprint and snapshot recorded above.

The M-1, M0, and baseline observations had completed before this repair. Their immutable definition
snapshots preserve the exact pre-repair source bytes. The repaired branch is unreachable for their
non-negative or `M-1` configurations over this dataset, so their observed semantics and outputs are
unchanged. They were not silently rerun because doing so would create new semantic fingerprints and
could obscure the frozen trial inventory. This operational source repair did not inspect any
candidate outcome before the complete four-observation set existed.

No required Development evidence is missing. Historical Evaluation and robustness evidence are
intentionally absent because the frozen no-eligible-candidate stopping rule was reached.
