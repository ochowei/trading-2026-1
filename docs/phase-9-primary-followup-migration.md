# Phase 9 primary-only followup migration

Updated 2026-08-07. This note records the implementation boundary for the
primary-only followup slice; it does not qualify or cut over any strategy.

The migrated strategies declare one adjusted-daily primary series through
`market_data_requirements()`, capture an immutable research definition and
trial family, and execute only through a verified `MarketDataBundle`. Their
`run_with_bundle()` output includes the typed canonical sleeve input required
by formal offline runs. `run_for_parity()` exposes ordered indicators, signal
dates, and filled trades for fixed-snapshot migration evidence.

The shared implementation is
`src/trading/core/bundle_strategy.py`. It is deliberately provider-free and
captures its own source in each definition fingerprint. The CIBR-014 and
SPY-007 strategies retain explicit implementations because they are the
tracer slices; the other primary-only followup strategies use the shared mixin.

Migrated primary-only followup strategies:

- CIBR-014, SPY-007
- COPX-007, DIA-013, EEM-012, EWJ-002, EWT-001, EWZ-006
- FCX-008, FXI-005, INDA-010, IWM-006, SIVR-006, SOXL-005
- TSM-006, URA-003, USO-009, VGK-007, VOO-003, XLU-002

The contract tests use synthetic verified bundles and assert that provider
access is not needed. Each shared-mixin strategy also completes a formal
offline schema-3 execution in a temporary result root. These tests do not
write repository `results/`, advance `latest.json`, or change qualification
and lifecycle state. A migration-mode result remains `migration-pending` and
requires a later separate valid formal observation before followup activation.

The historical auxiliary alignment contract is now implemented in
`ResearchDataStore` and `MarketDataBundle`: snapshot replay supplies one
ordered decision sequence, and every auxiliary observation is aligned
backward to each primary decision under an explicit one-session publication
lag and provider-observation coverage policy. The contract fails closed when
the first decision cannot be satisfied. The following six auxiliary
strategies now use the shared `AuxiliaryBundleStrategyMixin` and complete the
same provider-free formal offline contract tests:

- GLD-016 (`GLD:dxy-divergence-mr`)
- NVDA-007 (`NVDA:rs-exit-optimized`)
- TLT-017 (`TLT:yield-curve-slope-mr`)
- TQQQ-025 (`TQQQ:vxn-vix-vvix-filter`)
- TSLA-017 (`TSLA:qqq-divergence-breakout`)
- XBI-018 (`XBI:xbi-xlv-divergence-mr`)

These migration runs remain `migration-pending`; no latest result or
followup qualification is created until a separate valid formal observation
is recorded.

## SPY-007 fixed-snapshot evidence

On 2026-08-07, SPY-007 was replayed against the immutable snapshot
`ca54bc84ab26762438567d820257941c1ba00b42a8a833a4de9226a13db85111`, covering
the declared SPY primary series from 2010-01-01 through the 2026-08-06
decision session. The legacy DataFetcher path was bound to the exact snapshot
frame and compared with `run_for_parity()`; indicator, signal-date, and filled-
trade layers matched exactly. The passing parity digest is
`89be61317ff48bc298d33083fd012ec74b56c2afe90cf6119f010214ab70c62b`.

The result-linked artifacts are the snapshot manifest,
`results/spy_007_trend_pullback/<snapshot_id>.snapshot.json`, the local parity
evidence, and the migration result. The migration result is schema 3,
`migration-pending`, requires requalification, and does not replace
`results/spy_007_trend_pullback/latest.json` or alter qualification/lifecycle
state.

The first asset-wave tracer replays also passed. SIVR-001 used snapshot
`2f4b8260a913919a7785e961dba772d7aa7f226f3689bce07cbf079314e7b5d4` with
parity digest `d01501158c2dcfb2f0b25276b0be78dc3986f9b4c84daeb5300176ab1564eb18`.
TSLA-001 used its declared 2018-01-01 history start with snapshot
`5a7f48e9e134b1cbe16c492446d47653bcdb84e100676775c2dec3051ec1a9e7` and parity
digest `ecbe0eb4f0d6f3624dad10e1d4215af035b8438c448c35a73cdc2101f4a4f389`.
Both matched indicators, signal dates, and filled trades exactly; both
migration results remain `migration-pending` and leave `latest.json` and
qualification state unchanged.

## PR4 first asset-sized slice

SPY-003 (`spy_003_optimized_wr`) is the first non-followup asset-sized
migration. Its detector now declares `^VIX` as one auxiliary provider-
observation series and consumes only the historical as-of frame supplied by
`AuxiliaryBundleStrategyMixin`; the direct yfinance bypass is removed. The
same provider-free bundle and formal offline tests cover this slice, and its
allowlist entry is removed after the scanner confirms the provider boundary.

URA-006 (`ura_006_trend_pullback`) is the second slice in the same commodity
wave. It declares XLE as one auxiliary provider-observation series, removes
the detector's direct yfinance fetch, and is covered by the same formal
offline contract. Its migration is also `migration-pending` and does not
advance latest or qualification state.

CIBR-006 (`cibr_006_rs_momentum_pullback`) is the third single-auxiliary
slice. It declares SPY as a provider-observation benchmark and removes the
legacy direct fetch while preserving the existing RS, ATR, and cooldown
logic behind the fail-closed bundle boundary.

TSM-007, TSM-008, TSM-011, TSM-012, TSM-016, TSM-017, TSM-018, TSM-019, and
TSM-022 are the semiconductor-pair slices. Each declares SMH plus any
volatility auxiliary series as provider-observation inputs and retains its
existing RS signal logic and execution-model differences while routing data
through the shared bundle boundary.

NVDA-006, NVDA-008, NVDA-014, and NVDA-015 are the next single-reference
asset slice. NVDA-006, NVDA-014, and NVDA-015 declare SMH; NVDA-008 declares
SPY. Their existing relative-strength, mean-reversion, and regime calculations
now consume only the aligned historical auxiliary frame supplied by the
verified bundle. The four migrations remain `migration-pending`; they do not
write latest results or create followup qualification.

The remaining TSM direct-fetch slices are now covered as one multi-auxiliary
wave: TSM-009 declares NVDA; TSM-013, TSM-014, and TSM-021 declare SMH plus
QQQ; TSM-015 declares SMH, AAPL, and QQQ; and TSM-020 declares SMH plus SOXX.
All six preserve their existing signal calculations while requiring the
verified as-of bundle, and remain `migration-pending` without latest or
qualification changes.

TSLA-018, TSLA-019, and TSLA-020 form the next three-strategy macro slice.
Each declares QQQ plus its DXY, VIX, or UUP auxiliary series and removes the
detector's provider access. The existing breakout and regime gates remain
unchanged behind the shared bundle boundary; these migrations also remain
`migration-pending`.

GLD-015 and GLD-017 are the next precious-metals slice. GLD-015 declares GVZ;
GLD-017 declares GVZ plus UUP. Both retain their existing capitulation,
volatility, and USD regime calculations while requiring aligned historical
auxiliary frames from the verified bundle, with migration-pending result
semantics.

FCX-006, FCX-015, and FCX-016 form the next asset-sized auxiliary slice.
FCX-006 declares COPX for relative-strength calculations; FCX-015 and FCX-016
declare ^VIX for their breakout regime gates. Their existing signal and
execution-model logic now consumes only the aligned historical auxiliary
frames supplied by the verified bundle. These migrations remain
migration-pending and do not advance latest results or followup qualification.

FXI-007, FXI-015, FXI-016, and FXI-017 form the China/currency auxiliary
wave. FXI-007 declares EEM; FXI-015 declares ASHR; FXI-016 declares ASHR and
CNY=X; and FXI-017 declares CNY=X. Their existing relative-strength,
divergence, and currency-regime calculations now consume only aligned
historical auxiliary frames from the verified bundle. These migrations remain
migration-pending and do not advance latest results or followup qualification.

EWT-007, EWT-010, EWT-011, and EWT-012 form the Taiwan/EM auxiliary slice.
Each declares EEM for its relative-strength or divergence calculations and
retains its existing momentum or mean-reversion execution model behind the
provider-free bundle boundary. SOXL-010 declares SOXX and SPY for its sector
relative-strength gate, while SOXL-011 declares SOXX for its ATR regime gate.
All six migrations remain migration-pending and do not advance latest results
or followup qualification.

CIBR-017, NVDA-018, NVDA-021, and VGK-009 complete the remaining direct
provider-bypass wave. CIBR-017 declares ^VIX; NVDA-018 declares ^VXN; NVDA-021
declares QQQ; and VGK-009 declares EURUSD=X. Their existing volatility,
divergence, and bilateral-FX calculations now consume only aligned historical
auxiliary frames from the verified bundle. All four migrations remain
migration-pending and do not advance latest results or followup qualification.

EEM-006, EEM-016, EEM-017, EEM-018, EEM-019, EEM-020, and EEM-022 are the
broad-emerging-markets auxiliary wave. They declare SPY, DXY, EFA, ^VIX, FXI,
or the relevant multi-anchor combination as provider-observation inputs and
keep their existing mean-reversion or relative-strength calculations behind
the fail-closed bundle boundary. These seven migrations remain
migration-pending and do not advance latest results or followup qualification.

INDA-007, INDA-012, INDA-013, INDA-014, and INDA-015 form the India auxiliary
wave. INDA-007, INDA-012, and INDA-013 declare EEM; INDA-014 declares DXY;
and INDA-015 declares ^MOVE. Their existing relative-strength, broad-EM,
currency-direction, and implied-volatility gates now consume only aligned
historical auxiliary frames from the verified bundle. All five migrations
remain migration-pending and do not advance latest results or followup
qualification.

EWZ-005, EWZ-008, EWZ-009, and EWZ-010 form the Brazil/EM auxiliary wave.
EWZ-005 and EWZ-009 declare EEM; EWZ-008 declares ^VIX; and EWZ-010 declares
both EEM and BRL=X. Their existing relative-strength, volatility, divergence,
and currency-regime calculations now consume only aligned historical
auxiliary frames from the verified bundle. All four migrations remain
migration-pending and do not advance latest results or followup qualification.

EWJ-004, EWJ-006, and EWJ-007 form the Japan auxiliary wave. EWJ-004 declares
SPY, EWJ-006 declares JPY=X, and EWJ-007 declares ^VIX. Their existing
relative-strength, currency-direction, and implied-volatility calculations now
consume only aligned historical auxiliary frames from the verified bundle. All
three migrations remain migration-pending and do not advance latest results or
followup qualification.

DIA-009, DIA-014, DIA-015, DIA-016, and DIA-018 form the broad-index auxiliary
wave. DIA-009 declares SPY; DIA-014 declares IWM; DIA-015 and DIA-018 declare
^VIX; and DIA-016 declares QQQ. Their existing pairs, divergence, direction,
and volatility-band calculations now consume only aligned historical auxiliary
frames from the verified bundle. All five migrations remain migration-pending
and do not advance latest results or followup qualification.

IWM-009 declares SPY for its small-cap momentum-rotation comparison. Its
existing relative-strength and pullback calculations now consume only the
aligned historical auxiliary frame supplied by the verified bundle. The
migration remains migration-pending and does not advance latest results or
followup qualification.

TLT-008, TLT-009, TLT-013, TLT-014, TLT-015, and TLT-016 form the rate/credit
auxiliary wave. TLT-008 declares IEF; TLT-009 declares ^TNX; TLT-013 declares
^MOVE; TLT-014 and TLT-016 declare ^MOVE plus SPY; and TLT-015 declares
^MOVE, SPY, and HYG. Their existing duration-spread, yield-velocity,
implied-volatility, equity-divergence, credit-divergence, and multi-window
direction calculations now consume only aligned historical auxiliary frames
from the verified bundle. All six migrations remain migration-pending and do
not advance latest results or followup qualification.

TQQQ-019, TQQQ-020, TQQQ-021, TQQQ-022, TQQQ-023, TQQQ-026, and TQQQ-027 form
the leveraged-tech auxiliary wave. TQQQ-019 and TQQQ-020 declare ^VIX;
TQQQ-021 declares ^MOVE; TQQQ-022 declares QQQ and SPY; TQQQ-023 declares
^TYX and ^TNX; TQQQ-026 declares SQQQ; and TQQQ-027 declares QQQ. Their
existing volatility, cross-asset, yield-curve, inverse-pair, and single-day
reversal calculations now consume only aligned historical auxiliary frames
from the verified bundle. All seven migrations remain migration-pending and
do not advance latest results or followup qualification.

USO-025, USO-026, USO-027, and USO-028 form the commodity-volatility wave.
USO-025, USO-027, and USO-028 declare ^OVX; USO-026 declares ^OVX and XLE.
Their existing implied-volatility, cross-asset, and multi-period capitulation
calculations now consume only aligned historical auxiliary frames from the
verified bundle. All four migrations remain migration-pending and do not
advance latest results or followup qualification.

XBI-008, XBI-017, XBI-019, and XBI-020 form the biotech auxiliary wave. XBI-008
declares IBB; XBI-017 and XBI-020 declare ^VIX; and XBI-019 declares ^VIX plus
XLV. Their existing pairs, volatility-band, sector-parent, and volatility-
direction calculations now consume only aligned historical auxiliary frames
from the verified bundle. All four migrations remain migration-pending and do
not advance latest results or followup qualification.

XLU-013 and XLU-014 form the utility/rates auxiliary wave. XLU-013 declares
^MOVE; XLU-014 declares ^MOVE and ^TNX. Their existing implied-volatility and
rate-direction calculations now consume only aligned historical auxiliary
frames from the verified bundle. Both migrations remain migration-pending and
do not advance latest results or followup qualification.

SIVR-009, SIVR-019, and SIVR-020 form the silver auxiliary wave. SIVR-009
declares GLD; SIVR-019 declares ^GVZ; and SIVR-020 declares UUP. Their existing
ratio-reversion, volatility-direction, and USD-regime calculations now consume
only aligned historical auxiliary frames from the verified bundle. All three
migrations remain migration-pending and do not advance latest results or
followup qualification.

COPX-013, COPX-014, COPX-015, COPX-016, COPX-017, and COPX-019 form the
commodity-miners macro/underlying wave. COPX-013 declares SPY and ^VIX;
COPX-014 declares GLD; COPX-015 declares ^VIX; COPX-016 declares DX-Y.NYB;
COPX-017 declares ^TYX and ^TNX; and COPX-019 declares HG=F. Their existing
macro, divergence, volatility, yield-curve, and copper-direction calculations
now consume only aligned historical auxiliary frames from the verified bundle.
All six migrations remain migration-pending and do not advance latest results
or followup qualification.

DIA-019, IWM-015, NVDA-016, TQQQ-004, TQQQ-005, TQQQ-007, TQQQ-012,
TQQQ-014, TQQQ-015, XBI-016, XLU-005, XLU-006, and XLU-007 form the final
legacy DataFetcher auxiliary wave. DIA-019 and IWM-015 declare QQQ; NVDA-016
declares SMH; TQQQ-004, TQQQ-005, and TQQQ-014 declare ^VIX; TQQQ-007,
TQQQ-012, and TQQQ-015 declare QQQ; XBI-016 declares QQQ; and XLU-005,
XLU-006, and XLU-007 declare TLT, TLT, and SPY respectively. Their existing
macro-confirmation, volatility-filter, capitulation, breakout, and relative-
value calculations now consume only aligned historical auxiliary frames from
the verified bundle. All thirteen migrations remain migration-pending and do
not advance latest results or followup qualification. This wave also removes
the last experiment-scoped market-data bypass findings from the migration
allowlist; the static scanner now reports zero direct or indirect bypasses.

CIBR-001 through CIBR-005, CIBR-007 through CIBR-013, and CIBR-015/016 form
the first post-bypass primary-only asset wave. Each strategy now declares its
single adjusted-daily CIBR dependency, captures its local detector and shared
bundle executor in the immutable definition, and runs through the provider-free
primary bundle seam. Their migration runs remain pending and do not advance
latest results, followup qualification, or lifecycle state. CIBR-014 remains
on its explicit tracer implementation and is covered by the same primary-only
contract separately.

DIA-001 through DIA-008, DIA-010 through DIA-012, and DIA-017 form the next
primary-only asset wave. Each strategy now declares its single adjusted-daily
DIA dependency, captures its local detector and shared bundle executor in the
immutable definition, and runs through the provider-free primary bundle seam.
Their migration runs remain pending and do not advance latest results,
followup qualification, or lifecycle state.

FCX-001 through FCX-005, FCX-007, and FCX-009 through FCX-014 form the next
primary-only asset wave. Each strategy now declares one adjusted-daily FCX
dependency and uses the shared provider-free bundle execution and immutable
definition boundary. These migrations remain pending and do not advance
latest results, followup qualification, or lifecycle state.

EWJ-001, EWJ-003, EWJ-005, EWT-002 through EWT-006, EWT-008/009, and
EWZ-001 through EWZ-004 plus EWZ-007 form the Japan/Taiwan/Brazil primary-only
wave. Each strategy now declares one adjusted-daily primary dependency and
uses the shared provider-free bundle execution and immutable definition
boundary. These migrations remain pending and do not advance latest results,
followup qualification, or lifecycle state.

FXI-001 through FXI-004, FXI-006, and FXI-008 through FXI-014 form the next
primary-only China ETF wave. Each strategy now declares one adjusted-daily FXI
dependency and uses the shared provider-free bundle execution and immutable
definition boundary. These migrations remain pending and do not advance latest
results, followup qualification, or lifecycle state.

GLD-001 through GLD-014 and IBIT-001 through IBIT-009 form the commodity and
crypto primary-only wave. Each strategy now declares one adjusted-daily
primary dependency and uses the shared provider-free bundle execution and
immutable definition boundary. These migrations remain pending and do not
advance latest results, followup qualification, or lifecycle state.

SIVR-001 through SIVR-005, SIVR-007/008, and SIVR-010 through SIVR-018 form
the silver primary-only wave. Each strategy now declares one adjusted-daily
SIVR dependency, preserves its existing execution-model/backtester variant,
and uses the shared provider-free bundle execution and immutable definition
boundary. SIVR-006 was already migrated as the followup primary slice, while
SIVR-009/019/020 remain on their previously migrated auxiliary declarations.
All sixteen new migrations remain pending and do not advance latest results,
followup qualification, or lifecycle state.

TSLA-001 through TSLA-016 form the Tesla primary-only wave. Each strategy now
declares one adjusted-daily TSLA dependency, preserves its existing
execution-model/backtester variant, and uses the shared provider-free bundle
execution and immutable definition boundary. TSLA-017 through TSLA-020 remain
on their previously migrated auxiliary declarations. All sixteen new
migrations remain pending and do not advance latest results, followup
qualification, or lifecycle state.

VOO-001, VOO-002, and VOO-004 through VOO-006 form the VOO primary-only wave;
VOO-003 was already migrated. Each strategy now declares one adjusted-daily VOO
dependency, preserves its existing execution-model/backtester variant, and
uses the shared provider-free bundle execution and immutable definition
boundary. The five new migrations remain pending and do not advance latest
results, followup qualification, or lifecycle state.

The first VOO tracer replay also passed. VOO-001 used snapshot
`ea33ffb51e318408675549b451d97c6eff9718965a813aa1db0c663714f3637c` with
parity digest `438deb343b6522d4d5b2be866015cec06d17079d7a2f4e69c9b1110745718c44`.
Indicators, signal dates, and filled trades matched exactly; its migration
result remains `migration-pending` and leaves `latest.json` and qualification
state unchanged.

SPY-001, SPY-002, SPY-004 through SPY-006, and SPY-008/009 now form the
remaining SPY primary-only wave around the already-migrated SPY-003 auxiliary
declaration and SPY-007 tracer. Each declares one adjusted-daily SPY dependency
and preserves its existing execution-model or trailing-stop backtester. These
seven migrations remain pending and do not advance latest results, followup
qualification, or lifecycle state.

TSM-001 through TSM-005 and TSM-010 form the remaining TSM primary-only wave;
TSM-006 was already migrated as the primary momentum slice, while TSM-007/008
and TSM-011 through TSM-022 remain on their previously migrated auxiliary
declarations. Each new strategy declares one adjusted-daily TSM dependency and
preserves its existing execution-model/backtester variant. These six migrations
remain pending and do not advance latest results, followup qualification, or
lifecycle state.

TLT-001 through TLT-007 and TLT-010 through TLT-012 form the TLT primary-only
wave. TLT-008/009 and TLT-013 through TLT-017 remain on their previously
migrated auxiliary declarations. Each new strategy declares one adjusted-daily
TLT dependency and preserves its existing execution-model/backtester variant.
These ten migrations remain pending and do not advance latest results, followup
qualification, or lifecycle state.

XLU-001, XLU-003, XLU-004, XLU-008, XLU-009, and XLU-010 through XLU-012 form
the remaining XLU primary-only wave; XLU-002 was already migrated as the
primary capped-pullback slice, while XLU-005 through XLU-007 and XLU-013/014
remain on their previously migrated auxiliary declarations. Each new strategy
declares one adjusted-daily XLU dependency and preserves its existing
execution-model/backtester variant. These eight migrations remain pending and
do not advance latest results, followup qualification, or lifecycle state.

VGK-001, both VGK-002 variants, VGK-003 through VGK-006, and VGK-008 form the
VGK primary-only wave; VGK-007 and VGK-009 remain on their previously migrated
primary/auxiliary declarations. Each new strategy declares one adjusted-daily
VGK dependency and preserves its existing execution-model/backtester variant.
These eight migrations remain pending and do not advance latest results,
followup qualification, or lifecycle state.

INDA-001 through INDA-006, INDA-008/009, and INDA-011 form the remaining INDA
primary-only wave. INDA-007 and INDA-012 through INDA-015 remain on their
previously migrated auxiliary declarations. Each new strategy declares one
adjusted-daily INDA dependency and preserves its existing
execution-model/backtester variant. These nine migrations remain pending and
do not advance latest results, followup qualification, or lifecycle state.

SOXL-001 through SOXL-004, SOXL-006, SOXL-008/009, and SOXL-012/013 form the
remaining SOXL primary-only wave; SOXL-005 was already migrated. Each new
strategy declares one adjusted-daily SOXL dependency and preserves its existing
execution-model/backtester variant. These nine migrations remain pending and
do not advance latest results, followup qualification, or lifecycle state.

URA-001, URA-002, and URA-004 through URA-005, URA-007 through URA-014 form
the remaining URA primary-only wave; URA-003/006 were already migrated as
primary/auxiliary slices. Each new strategy declares one adjusted-daily URA
dependency and preserves its existing execution-model/backtester variant.
These twelve migrations remain pending and do not advance latest results,
followup qualification, or lifecycle state.

COPX-001 through COPX-003, COPX-005/006, COPX-008 through COPX-012, and
COPX-018 form the remaining COPX primary-only wave; COPX-007 was already
migrated as the primary volatility-adaptive slice, while COPX-013 through
COPX-019 remain on their previously migrated auxiliary declarations. Each new
strategy declares one adjusted-daily COPX dependency and preserves its existing
execution-model/backtester variant. These eleven migrations remain pending and
do not advance latest results, followup qualification, or lifecycle state.

EEM-001 through EEM-005, EEM-007 through EEM-011, EEM-013 through EEM-015, and
EEM-021 form the remaining EEM primary-only wave; EEM-006, EEM-016 through
EEM-020, and EEM-022 remain on their previously migrated auxiliary declarations,
while EEM-012 was already migrated as the primary slice. Each new strategy
declares one adjusted-daily EEM dependency and preserves its existing
execution-model/backtester variant. These fourteen migrations remain pending
and do not advance latest results, followup qualification, or lifecycle state.

IWM-001 through IWM-005, IWM-007/008, and IWM-010 through IWM-014 form the
remaining IWM primary-only wave; IWM-006 was already migrated as the primary
BB-squeeze slice, while IWM-009 and IWM-015 remain on their previously migrated
auxiliary declarations. Each new strategy declares one adjusted-daily IWM
dependency and preserves its existing execution-model/backtester variant. These
twelve migrations remain pending and do not advance latest results, followup
qualification, or lifecycle state.

NVDA-001 through NVDA-005, NVDA-009 through NVDA-013, and NVDA-017/019/020 form
the remaining NVDA primary-only wave; NVDA-006 through NVDA-008, NVDA-014 through
NVDA-016, NVDA-018, and NVDA-021 remain on their previously migrated auxiliary
declarations. Each new strategy declares one adjusted-daily NVDA dependency and
preserves its existing execution-model/backtester variant. These thirteen
migrations remain pending and do not advance latest results, followup
qualification, or lifecycle state.

USO-001, USO-005, USO-007, USO-010, USO-012/013, USO-021 through USO-024, and
USO-029 form the remaining USO primary-only wave; USO-009 was already migrated
as the primary momentum slice, while USO-025 through USO-028 remain on their
previously migrated ^OVX/XLE auxiliary declarations. Each new strategy declares
one adjusted-daily USO dependency and preserves its existing
execution-model/backtester variant. These eleven migrations remain pending and
do not advance latest results, followup qualification, or lifecycle state.

XBI-001, XBI-004 through XBI-007, and XBI-009 through XBI-015 form the remaining
XBI primary-only wave; XBI-008 and XBI-016 through XBI-020 remain on their
previously migrated IBB/QQQ/^VIX/XLV auxiliary declarations. Each new strategy
declares one adjusted-daily XBI dependency and preserves its existing
execution-model/backtester variant. These twelve migrations remain pending and
do not advance latest results, followup qualification, or lifecycle state.

As of 2026-08-07, the primary-only followup contract covers 285 experiment
entries (571 test cases including the module-level contract checks), and the
full repository regression passes 1226 tests. The only remaining direct
`ExecutionModelStrategy` classes are the intentional CIBR-014/SPY-007 tracer
implementations and nine TQQQ variants outside the primary followup contract;
they remain explicitly out of this shared-mixin migration boundary. No result,
latest, qualification, or lifecycle state is changed by these code-only waves.
