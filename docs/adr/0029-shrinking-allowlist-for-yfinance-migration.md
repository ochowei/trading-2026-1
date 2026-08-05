# Migrate direct yfinance access through a shrinking allowlist

New direct yfinance access from experiment code is prohibited immediately, while the existing bypass files form a legacy allowlist that CI permits only to shrink. Followup and shadow candidates migrate first in asset- or family-sized batches, cannot qualify before migration, and must demonstrate signal-, indicator-, and trade-level parity on the same research data snapshot except for documented data-consistency corrections. This contains change risk while guaranteeing that the temporary compatibility boundary converges to zero.
