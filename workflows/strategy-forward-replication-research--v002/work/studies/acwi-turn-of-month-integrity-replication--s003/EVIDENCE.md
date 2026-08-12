# Evidence: ACWI Turn-of-Month Integrity Replication

## Execution record

S003 was preregistered by `ochowei@gmail.com` at `2026-08-12T11:41:28.139112Z` and
transitioned to `running` by `codex-primary-execution-agent`. The frozen hypothesis SHA-256 is
`7cb586ed2f9ed196f678a2c16a4d2abbb5c9d077def4950d37819701ca9628a4`; the frozen plan SHA-256 is
`b797d2738554e4bbfe252b02391ec058e138ff6ec8f3cfd6b975ac1cb1ccc7f3`.

Only 2009-2020 Development evidence was observed. All manifests are capped at `2020-12-31` and
contain the Yahoo auto-adjusted ACWI series beginning `2008-03-28`. No 2021-or-later outcome was
captured or inspected.

### Commands and operational disposition

The first invocation below failed before snapshot publication because sandbox DNS could not resolve
Yahoo. It produced no manifest, formal result, observation, or metric:

```text
uv run trading research snapshot acwi-turn-of-month/enter-minus-two-hold-five --workflow workflows/strategy-forward-replication-research--v002 --decision 2020-12-31
```

Provider disposition at `2026-08-12 19:44:24 +08:00`: `DNSError`, `Could not resolve host:
guce.yahoo.com`, followed by `provider returned no data for ACWI`. The identical command was retried
with network access and succeeded. The other successful snapshot commands differed only in the
research identity:

```text
uv run trading research snapshot acwi-turn-of-month/enter-minus-two-hold-five --workflow workflows/strategy-forward-replication-research--v002 --decision 2020-12-31
uv run trading research snapshot acwi-turn-of-month/enter-minus-one-hold-five --workflow workflows/strategy-forward-replication-research--v002 --decision 2020-12-31
uv run trading research snapshot acwi-turn-of-month/enter-month-end-hold-five --workflow workflows/strategy-forward-replication-research--v002 --decision 2020-12-31
uv run trading research snapshot acwi-turn-of-month/enter-session-ten-hold-five --workflow workflows/strategy-forward-replication-research--v002 --decision 2020-12-31
```

The four formal run commands were:

```text
trading research run acwi-turn-of-month/enter-minus-two-hold-five --workflow workflows/strategy-forward-replication-research--v002 --manifest results/acwi-turn-of-month--enter-minus-two-hold-five/bd52bfd9d29b08076adc33cfbff2ffe53ef2616c3c2e88173d35185a110985a7.snapshot.json --offline
trading research run acwi-turn-of-month/enter-minus-one-hold-five --workflow workflows/strategy-forward-replication-research--v002 --manifest results/acwi-turn-of-month--enter-minus-one-hold-five/14ac45aa8ea535283cb9710b124f6476209f88683218511e553292aafa8bd05b.snapshot.json --offline
trading research run acwi-turn-of-month/enter-month-end-hold-five --workflow workflows/strategy-forward-replication-research--v002 --manifest results/acwi-turn-of-month--enter-month-end-hold-five/dea09b7a5338ab9972d8cdad2500caf4f1eda0dd5f47e78f172b4183ac69b4d2.snapshot.json --offline
trading research run acwi-turn-of-month/enter-session-ten-hold-five --workflow workflows/strategy-forward-replication-research--v002 --manifest results/acwi-turn-of-month--enter-session-ten-hold-five/6fa762b900bdac0526a9e52b9a8d6e0e710a31714ccb09ec88402eb1430c920c.snapshot.json --offline
```

Each exact canonical run argv is independently embedded in its result. All four result commands
completed with exit code zero and published only offline historical results.

### Immutable identities and provenance

| Role | Definition fingerprint | Definition snapshot | Snapshot ID | Manifest SHA-256 | Result SHA-256 |
| --- | --- | --- | --- | --- | --- |
| M-2 | `9ea3a69d2a97701b3a390373db7b9f38566be09a563bd3123c6fd5157702bb5a` | `fc2c96361abf3b93d2c9702aeb0e5f5332a872f67efd5aa6f7c326af16519525` | `bd52bfd9d29b08076adc33cfbff2ffe53ef2616c3c2e88173d35185a110985a7` | `d997a90bc6a98e724a7118795137411c054cc93a543e3e12b6f8ea416c34a559` | `56165ddb96bb94c0a2804e429b8daa837729ee8657f959ad1e3eeae16f1c7bfc` |
| M-1 | `98aa53497e28ed66138f65fbedc9c95822d05d325d0d7a2e4255c58e010f0998` | `c476f8eeb37c9755f721120e6af6976fb6134081a2f043986f04a52a9ebe71ca` | `14ac45aa8ea535283cb9710b124f6476209f88683218511e553292aafa8bd05b` | `1f924d906db4c25035e5c019037d27ec0d930502c507938614a2ea68edeb1731` | `5368759845ca4dc36d516df039a58d4871f1893a12711913cba7842ead51601b` |
| M0 | `ee8d633d16f50d0a021881148df39f246f9ef52d007f160eefab2cf95f790b39` | `1b4c45fb3b3818cec6531a9297adabc848d972fa8bfa0cc0d6d5414cfac9bdef` | `dea09b7a5338ab9972d8cdad2500caf4f1eda0dd5f47e78f172b4183ac69b4d2` | `8a215bcd3348d072f594ba444fe18555a7c287b8c2dd52058061c9d7e3a09934` | `1eb5f58d41bf740ed69ca749b81ddc52ea5f45d6cc71c8d573aadbf0629286ab` |
| baseline | `66091d271cbe846de97b96366ed24f8e6023aece46aee75959a34c6791bfcd4a` | `b8a898bd9c203f0f0a551ac9f6912bcda5df6f39b7b26eb547d846697d7b5ff7` | `6fa762b900bdac0526a9e52b9a8d6e0e710a31714ccb09ec88402eb1430c920c` | `808584f8c343262547b4625533e7d488c78dec970b9d463975c01e753deb6fbe` | `4a2a44a778b86194ba700e499ce7f809b935bb8195642db1f544f98ab7f40927` |

Result paths, in table order:

- `results/acwi-turn-of-month--enter-minus-two-hold-five/20260812_114539_625028_offline_4e88dc445c524148a7dd3308f73c00b3.json`
- `results/acwi-turn-of-month--enter-minus-one-hold-five/20260812_114541_164029_offline_4dbaf7e9dfab439e84693c69729b1013.json`
- `results/acwi-turn-of-month--enter-month-end-hold-five/20260812_114542_689370_offline_2624f91471c748c59000b9875183e00b.json`
- `results/acwi-turn-of-month--enter-session-ten-hold-five/20260812_114544_233957_offline_83ed30fea612425194bb0917f94a6f35.json`

All four manifests passed `trading data verify`. Before metric inspection, an independent read-only
check established for each result: `valid` status, `2020-12-31` cutoff, exact canonical argv, v002
release SHA-256 `34ba7bb1518df9e46f4f1d89330b6c1e005225c007bfad43440a3d9a75e90299`,
workflow SHA-256 `4dfa7df8244744aab3219c1a0784aee8af9ca559c059e5cb659aa6088b7789be`,
policy set `4ade828a43e2cfab97b2933c5722107cf00ccf27c3a90c92b60c19b67f511189`,
Git HEAD `e4b028737cb15f80cc478745c60850579c7197b9`, matching embedded-source hashes, and no
unclassified parity difference.

The exact orchestration bytes are embedded in every result with these common SHA-256 identities:

| Source | Captured SHA-256 | Status relative to captured Git HEAD | HEAD SHA-256 |
| --- | --- | --- | --- |
| `src/trading/cli.py` | `fd9c91e47ccb69cb1b14ba697a480d6ce66480af446b34c13c0435c6b60ee98f` | modified | `8b76ddaad8092c178b499d11f4ad7a5cee97f6569ccb05f3d1c9ab2f04f9f54f` |
| `src/trading/research_definitions/execution.py` | `effbfc69a4c96d1a6a91c5dbc1f85abba3b2f6410b9a41a7490beb6282b453ea` | clean | same |
| `src/trading/research_data/runs.py` | `a5b2fdb903cb0851cc107764643b86d14940747c4a7b5a61fd729225c234cd58` | modified | `aed7677ebc0c6bddbcd04053c259bb591881e2c6d87a507e3de08734f331221e` |
| `src/trading/research_data/result_schema.py` | `6043c0242a8c7c332812bade26cec2f3cf28f59be84bb702e201b8daa7e8ac22` | clean | same |

The complete captured bytes, rather than a mutable checkout, are authoritative for the two modified
orchestration files. Each definition blob independently records clean status for its captured
strategy/detector/backtester sources at the same branch and Git HEAD.

### Development metrics and gates

Profit factor and both scenario-specific concentration values were recomputed directly from
canonical completed trades using the frozen formulas. The distinct baseline has base return
`-2.6320%`, base profit factor `0.9758`, and base-net Sharpe `0.0232`.

| Candidate | Trades | Base return | Base PF | Base Sharpe | Sharpe minus baseline | Base max positive-profit share | Stress return | Stress PF | Stress MDD | Stress max positive-profit share | Eligibility |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| M-2 | 143 | 18.5106% | 1.1367 | 0.2015 | 0.1784 | 29.64% | -25.0065% | 0.8073 | -43.8625% | 50.63% | ineligible: stress return, PF, MDD, concentration |
| M-1 | 143 | 33.5980% | 1.2308 | 0.3129 | 0.2897 | 38.56% | -15.4592% | 0.8881 | -38.6171% | 42.87% | ineligible: stress return, PF, MDD |
| M0 | 143 | 30.9568% | 1.2273 | 0.2805 | 0.2573 | 46.85% | -17.1306% | 0.8692 | -42.2875% | 55.25% | ineligible: stress return, PF, MDD, concentration |

Each candidate has at least one completed trade in all 12 Development years; maximum annual trade
share is `8.39%`. All clear the base return/PF, baseline-spread, coverage, base concentration,
identity, and parity gates. None clears the three frozen stress performance/risk gates. M-2 and M0
also fail the clarified stress positive-profit concentration gate.

There is no eligible candidate to rank or freeze. The preregistered Development stopping condition
was reached. No hold-four/six source was materialized, no Historical snapshot was captured, and no
2021-or-later outcome was inspected.

## Deviations and missing evidence

The initial M-2 snapshot command failed only because sandbox DNS blocked provider access. The same
frozen command succeeded with network access; the failed invocation created no immutable research
artifact or outcome and did not alter the trial inventory.

The operator verified all embedded formal-run provenance before reading metrics, but did not write
the snapshot command dispositions or execution-time dirty-status comparison into this tracked
`EVIDENCE.md` before metric comparison, as the plan required. They were recorded here afterward
from retained command output and from the already-immutable embedded orchestration bytes. The exact
run argv, workflow binding, Git HEAD, source bytes, source hashes, manifests, and results existed
before metric inspection and remain independently verifiable; no value was backdated and no run was
repeated after outcome inspection. An independent reviewer must decide whether the late tracked
summary is merely a recording deviation or an integrity defect requiring `indeterminate`.

No required Development metric or immutable artifact is otherwise missing. Historical and
robustness evidence are intentionally absent because the no-eligible-candidate stopping rule was
reached.
