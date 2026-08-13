# Conclusion: XLF Close-Armed Profit-Protection Pullback Research

## Outcome

`fail`

The sole preregistered candidate is Development-ineligible. This is a complete, reproducible gate
failure under `strategy-forward-replication-research@v004`, not missing evidence or an open
prospective checkpoint.

## Evidence trace

- Preregistration pins hypothesis SHA-256
  `5bd6b85ed9901c7e95597faa0b25499a42413145b2f2d4563081de40b297c782`, plan SHA-256
  `58cee2056697fa2bcbd4c25ded49372ec69ea7eca16d607491754fda7f8a6d54`, and v004 workflow
  SHA-256 `d176471dd099bf55274748d82957cd5a410b40ddda5e38c9e8d69926a66431da`.
- Candidate snapshot
  `a53e7d14cd403881edf36da8a6a64fcfce2b8d3966a95f57a783c03e7fef6aec` and baseline snapshot
  `42ac8896d924c49dbe8299a49d40e5b8ea8e423a490bb394b98ec2caa3e5f8f7` both verify, use the
  identical XLF Development blob, and bind the exact v004 composite policy set.
- Candidate result SHA-256
  `93dda30affa1a05c031ef3294e8b9d0bddb285ce0988d2d127270720faf7d664` and baseline result
  SHA-256 `92a0b7dced06b10fa4457c15347ad51f9290d00f6f9fc0ad2ed5d9950e1047ed`
  are valid offline formal observations through 2020-12-31 with complete workflow provenance.
- Candidate and baseline have identical 126 raw signals, 53 accepted entries, and 73
  occupation-lock skips. The candidate completed 53 trades across 16 years and produced 15
  protection exits across 11 years, so the mechanism is sufficiently binding and cohort integrity
  does not prevent a determination.
- The candidate failed the conjunctive absolute gates: base return was -34.5691% with profit factor
  0.6929; stress return was -44.7762% with profit factor 0.5955 and maximum drawdown 63.7548%.
- It also failed the relative claim: Sharpe advantage versus baseline was -0.0632 rather than at
  least +0.10, stress drawdown was 99.05% of baseline rather than at most 85%, and aggregate paired
  advantage on protection-fired trades was -0.082528 rather than positive.

The frozen plan states that failure of any Development eligibility condition records `fail` and
forbids tuning or substitution. The v004 workflow likewise defines the absence of an eligible
Development candidate as `fail`. `insufficient-evidence` is reserved for an open prospective
Shadow checkpoint, while the verified identities and complete gate evidence rule out
`indeterminate`.

## Limitations and follow-up

This conclusion is limited to the fixed +2.0% arm / +0.5% floor state-dependent profit-protection
candidate and the frozen 2004-2020 Development role. The three robustness definitions were
correctly not materialized because Development eligibility failed. No 2021-2025 Historical or
Shadow outcome was inspected, and those absent stages are not evidence gaps because the stopping
rule prohibited advancement.

S002 must not be tuned, revived, promoted, or used for trading authorization. A materially new exit
mechanism would require a separately approved and preregistered study with explicit lineage and
unconsumed validation roles. This terminal result creates no candidate freeze, Shadow eligibility,
broker authority, order authority, or live-trading permission.
