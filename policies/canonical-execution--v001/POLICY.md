# Canonical Daily-Bar Execution Policy

Signals decided after a completed session enter at the next available open. Profit targets use a
Day limit, stops use a GTC stop-market assumption, and expiry exits at the next available open.
When one bar reaches both stop and target, the adverse stop outcome takes precedence. Missing
next-session data produces an unfilled observation rather than an invented fill.

Canonical sleeve evidence applies base costs of 5 bps entry slippage, 5 bps exit slippage, and 1
bps fee per side. The strictly adverse stress scenario uses 20 bps entry slippage, 20 bps exit
slippage, and 2 bps fee per side. Formal evidence reports gross, base-net, and stress-net outcomes.

The policy does not define signal generation, broker support, or capital allocation.
