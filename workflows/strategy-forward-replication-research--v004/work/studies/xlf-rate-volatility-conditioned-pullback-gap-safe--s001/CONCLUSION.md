# Conclusion: XLF Gap-Safe Rate-Volatility-Conditioned Pullback Research

## Outcome

`fail`

No Development candidate satisfied every frozen eligibility and risk gate. Under the
preregistered outcome rules, the absence of an eligible Development candidate is a terminal
failure and prohibits candidate freeze, Historical Evaluation, robustness execution, and Shadow
advancement.

## Evidence trace

- `PREREGISTRATION.json` pins workflow `strategy-forward-replication-research@v004`, hypothesis
  SHA-256 `f6f615def9c804b6651bde5643a3af51bab3d6377c2a6d00be811fdfb4ad0801`, and plan SHA-256
  `f44f0e9729f85cabe69fa300555dfcf9a96f422e0f4f0eb99b58414f1d99bc53`.
- `EVIDENCE.md` records valid immutable manifests and formal results for cap-3, cap-5, cap-7, and
  the ungated baseline. Their recorded SHA-256 values match the reviewed repository artifacts;
  all four bind composite policy set
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e` and the exact v004
  workflow release.
- Provider-free replay reproduced the frozen unavailable-decision inventory of 2013-03-21,
  2013-03-22, and 2013-03-25. Suppression evidence shows that none produced a gated raw signal,
  candidate, or canonical trade.
- All candidates exceeded the minimum trade-count and traded-year floors, so their Development
  gates were decidable. Cap-3, cap-5, and cap-7 respectively had base returns of -3.9491%,
  -0.0958%, and -29.1460%; base profit factors of 0.9547, 0.9990, and 0.7291; stress returns of
  -14.9467%, -13.2169%, and -39.0398%; and stress maximum drawdowns of 54.2810%, 49.5332%, and
  54.2154%. Their Sharpe advantages over the baseline were 0.0876, 0.1027, and -0.0069, all below
  the required 0.25. Each therefore failed multiple conjunctive gates.
- The append-only registry retains the failed first cap-3 observation and its successful retry
  under the same semantic trial. The bounded replay repair did not change the manifest, strategy,
  signal, policy, workflow, or definition fingerprint, and its source and regression-test hashes
  are recorded in `EVIDENCE.md`. It does not make the Development evidence indeterminate.

## Limitations and follow-up

This conclusion evaluates only the preregistered Development stage. Historical (2021-2025),
robustness, prospective Shadow, broker, and live-trading evidence were intentionally not accessed
because the frozen stopping rule had already been reached. The result neither authorizes trading
nor supports a profitability claim. Any revised mechanism or thresholds require a new study and
cannot reuse this study to repair the failed gates retrospectively.
