# Conclusion: FXI ATR-Divergence Mean-Reversion Forward Replication

## Outcome

`fail`

The sole preregistered candidate is Development-ineligible because the ASHR compound filter does
not meet its frozen binding floor. This is a complete and reproducible gate failure under
`strategy-forward-replication-research@v004`, not missing evidence or an open prospective
checkpoint.

## Evidence trace

- Preregistration SHA-256
  `39f0f56b6f7dccb7cbaa3750799225f1a4e9216861939b2f9682dd51b0ed3bba` pins hypothesis SHA-256
  `c4e83895bf019a8f3e2130baf39e209aab6215906626f1901aa0a5a77019f969`, plan SHA-256
  `b9fd8df693d152640520fe5ff8cd2defbb9b6b60a81d7dc527e704f087ca9ee0`, and v004 workflow
  SHA-256 `d176471dd099bf55274748d82957cd5a410b40ddda5e38c9e8d69926a66431da`.
- Candidate snapshot
  `aa66c1529f194fc5ee9a1e7c4c73743bcf45a20f4a7b3b01240ea6ece1e418c2` and baseline snapshot
  `8c961eb540df3c13912dafce04d1ada5e9989750ea6e24211ca0f08ef0659c84` verify, share the exact FXI
  Development blob, and bind composite policy set
  `cac4973cf0055c772487b069c96f1cd2b488a2457636f8cfe2c812c89ad0f63e`. The candidate additionally
  binds same-session ASHR blob
  `c83c34a8669a39a6aed4334156e2bf8aaf1031ba63fc0067d38b738b90f60f02`.
- Candidate result SHA-256
  `4429dbff84a8d4e107df8322f7516e0f76aa55e6829a987ce2288ca3f237497f` and baseline result SHA-256
  `f7937906f3d358a2ba61e2f699be5a85ac21b5469f7c22ca1f51bb16188f6c02` are valid provider-free
  offline formal observations through 2025-12-31 with exact workflow provenance.
- The candidate completed 33 trades across 11 years. It passed the absolute and relative
  performance gates: base return 111.8162%, base profit factor 3.2306, base Sharpe 0.7809, stress
  return 90.5889%, stress profit factor 2.7454, and stress maximum drawdown 15.0886%.
- Independent read-only replay of the frozen indicators over the immutable FXI/ASHR blobs reproduced
  all 387 baseline-eligible entries. The ATR ceiling uniquely suppressed 17 entries across five
  years and passed. The ASHR gate uniquely suppressed only six entries across four years—2015,
  2019, 2021, and 2022—and failed the required ten entries across five years.
- Deterministic gate artifact SHA-256
  `4a94f1cf575df327f2e6420ab00dbfdcc2fad69de69450ad521f3d3e99e98ea0` records the candidate as
  ineligible, with no selection. The append-only trial registry contains only the authorized
  candidate and baseline observations for this family.

The frozen plan states that failure of any Development eligibility condition records `fail` and
terminates the round. The v004 workflow likewise defines the absence of an eligible Development
candidate as `fail`. `insufficient-evidence` is reserved for an open prospective Shadow checkpoint,
while the verified identities and complete gate evidence rule out `indeterminate`.

## Limitations and follow-up

This conclusion is limited to the preregistered ATR(5)/ATR(20) band and FXI-versus-ASHR divergence
candidate over the frozen 2015-2025 Development role. The positive performance metrics do not
override the failed mechanism-binding gate. The four robustness identities were correctly not
executed, and no 2026 quarantine, 2027-2031 Historical, or Shadow outcome was inspected; those
absent stages are not evidence gaps because the stopping rule prohibited advancement.

S003 must not be tuned, revived, promoted, or used for trading authorization. A modified ASHR
threshold, different binding definition, or other material strategy change requires a separately
approved and preregistered study with explicit lineage and unconsumed validation roles. This
terminal result creates no candidate freeze, Shadow eligibility, broker authority, order authority,
or live-trading permission.
