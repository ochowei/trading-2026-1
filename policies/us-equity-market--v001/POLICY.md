# US Equity Daily-Bar Market Policy

This policy supports Yahoo auto-adjusted daily OHLCV observations for research whose primary
session calendar is XNYS. A primary series requires complete XNYS-session coverage. Auxiliary
series must declare their observation coverage and information-availability rules.

A daily decision becomes eligible only after the actual XNYS close plus a conservative 30-minute
publication buffer. Unknown auxiliary publication times require at least one completed primary
session of lag. Research logic consumes declared read-only bundles and never obtains provider data
through a hidden strategy or detector path.

The policy does not define signals, broker order support, execution costs, or portfolio sizing.
