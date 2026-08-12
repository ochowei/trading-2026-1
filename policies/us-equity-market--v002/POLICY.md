# US Equity Daily-Bar Market Policy

This policy supports Yahoo auto-adjusted daily OHLCV observations for research whose primary
session calendar is XNYS. A primary series requires complete XNYS-session coverage. Auxiliary
series must declare their observation coverage and information-availability rules.

A daily decision becomes eligible only after the actual XNYS close plus a conservative 30-minute
publication buffer. Unknown auxiliary publication times require at least one completed primary
session of lag. Research logic consumes declared read-only bundles and never obtains provider data
through a hidden strategy or detector path.

Every auxiliary dependency declares a nonnegative maximum observation lag. The default behavior
when that maximum is exceeded is `fail`: bundle construction stops and no research observation is
published. A newly preregistered definition may instead explicitly select `mark_unavailable`.
Under that mode the bundle preserves the backward-as-of observation, its observation date, first
available session, and actual lag, but marks the decision `ObservationAvailable=false`. Strategy
logic must suppress every signal and candidate on that decision. It must never treat the over-age
value as current, forward-fill eligibility, silently drop audit evidence, or enable this mode after
outcome inspection.

The excess-lag mode is outcome-relevant policy evidence. Non-default behavior must be serialized in
the immutable data manifest and captured in the research-definition fingerprint. Changing the
mode, maximum lag, publication lag, unavailable-session treatment, or required auxiliary series
creates a new formal research identity and requires preregistration before outcome use.

The policy does not define signals, broker order support, execution costs, or portfolio sizing.
