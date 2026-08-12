# Evidence: XLF Rate-Volatility-Conditioned Pullback Publication-Lag-Safe Research

## Execution record

S003 entered Development at `2026-08-12T13:41:19.725316Z` under authority
`ochowei@gmail.com`. Frozen identities were HYPOTHESIS
`51e4fa9bc8dfc8a12d0cdc9a518058af6c1b692f63925809efddc2e8295cca5e`, PLAN
`8ed16085dd921232e7aadd613237d6653556823f976a908897431df9b9b5cd38`, and PREREGISTRATION
`b44cea4c5cf3a567593e28fc27433664a85df18eba3e0d5e926718fb9ec7d0f3`. Git HEAD at snapshot
preparation was `0ae8f4f6a23ef4ebd3e4666cab626e6519821b52`.

The exact snapshot commands were the standard `uv run trading research snapshot <identity>
--workflow workflows/strategy-forward-replication-research--v003 --decision 2020-12-31` command
for cap-3, followed by the same command with `--reuse-full-refresh` for cap-5, cap-7, and the
ungated baseline. Cap-3 performed the sole provider refresh; all other commands reported reuse.

| Trial | Snapshot ID | Definition fingerprint | Manifest SHA-256 |
| --- | --- | --- | --- |
| cap-3 | `f0f64620af1b99db80e91fb6507c00a56c9b451e9f72dd21c75ed0a9ec66051b` | `d941cac79313a15ad09154c5279747496f2ca730f29641647006a342e744dd09` | `9bb80ee79e1762e9e487661a48d01e471cbca93c276443fd07794fe79e4b3885` |
| cap-5 | `81a784ec8d4253c7ea89b0166465169d479ca3449e3e4b44b1df41bf3872b8cd` | `9f49b6dd3642b009120f4ca2770c03385da44ddd30b4dbcdb01d50efb009cd20` | `c6a619e6059f91ccafd39ce44ee1ee31f45604170b0f03946c46342a112e0c06` |
| cap-7 | `a50b1b92ac6e3a3a0ad712d7b198df83b244f4445a9cfa3123e8ceb7d930e913` | `bd12c16ab3a36e6318be6a15430c3dc78f65b30fd6c9d6de3e5cc3b60444470f` | `d6aa4d534747dc4880d6a3bd604bce78b4f53f4c07a8fc35e27934c583922ad1` |
| baseline | `ad057d96773402d5c4ff081cc5590feb836986fa88a5e672e8d917e5981cd640` | `f8d9a4743286ca87e39875d156b342364ceac56f9c0e78b81225a3690899cce5` | `95b5ec22d986c4f251be4d8a3c8acb8b69b5123cc5dc5b4ddbd96a748d34ab99` |

All four manifests bind XLF blob
`c01fbb4a36848732aec0b8c46a07c1eaa4baa6f544212c53acd71f1c748beece`; all gated manifests bind
MOVE blob `b74640452eb82a9451ff279f1835ae16c93e2317c5122aba25aaa2a66b22fd09`. Common-data equality
passed. The baseline passed `trading data verify`. Every gated manifest failed pre-run bundle
verification with the exact error:

```text
trading.market_data.bundle.MarketDataAvailabilityError: maximum observation lag exceeded at signal decision 2013-03-21: 4
```

No `trading research run` command was issued. No result JSON, registry observation, metric,
eligibility decision, ranking, candidate freeze, or Historical outcome was produced or viewed.

## Deviations and missing evidence

- The publication-lag-safe start boundary is satisfiable, but the verified MOVE provider history
  contains a later gap requiring an observation lag of four XNYS sessions on 2013-03-21. This
  exceeds the frozen maximum of three sessions.
- Changing the maximum lag or the data period is outcome-relevant and cannot repair S003.
  Advancement stops before execution or partial ranking.
- Development metrics, complete ranking, candidate freeze, robustness definitions, Historical
  Evaluation, and Shadow evidence are absent.

After pausing, a read-only availability audit used the already captured XLF and MOVE cache bytes,
the repository XNYS calendar, the frozen one-session publication lag, and a diagnostic-only high
maximum solely to enumerate lag. It did not calculate signals, trades, returns, metrics, or any
candidate outcome. Across 4,565 Development decision sessions, lag counts were: 4,472 at one
session, 83 at two, 7 at three, and exactly one each at four, five, and six. The only decisions above
the frozen maximum were 2013-03-21, 2013-03-22, and 2013-03-25, all using the 2013-03-15 MOVE
observation first available on 2013-03-18. Maximum observed lag was six sessions on 2013-03-25.
