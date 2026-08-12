# Conclusion: ACWI Turn-of-Month Integrity Replication

## Outcome

`fail`

No candidate satisfies every frozen Development gate. The preregistered stopping rule therefore
terminates S003 before candidate freeze or Historical Evaluation. This result does not inspect or
make any claim about 2021-or-later outcomes.

## Evidence trace

Read-only workflow validation passed with S003 in `awaiting-review`. The preregistration,
hypothesis, plan, v002 workflow definition and release, normative dependencies, and four selected
policy releases/configurations match their frozen checksums. The four Development manifests verify
provider-free, and their snapshot, definition, manifest, and result identities match
`EVIDENCE.md`.

Each result embeds the exact canonical run argv, v002 workflow/release hashes, composite policy-set
identity `4ade828a43e2cfab97b2933c5722107cf00ccf27c3a90c92b60c19b67f511189`, Git HEAD
`e4b028737cb15f80cc478745c60850579c7197b9`, and the required orchestration source bytes and
hashes. Independent hashing reproduced every embedded source identity. Parity contains no
unclassified difference; all trade differences are classified as intentional execution-cost
policy differences. The S003 Development inventory contains the three candidates and distinct
baseline; no hold-four/six robustness source or Historical artifact was produced.

Independent recomputation from canonical completed trades confirmed the recorded Development
metrics and both scenario-specific concentration calculations. M-2 has stress return `-25.0065%`,
profit factor `0.8073`, maximum drawdown `-43.8625%`, and positive-profit concentration `50.63%`.
M-1 has stress return `-15.4592%`, profit factor `0.8881`, and maximum drawdown `-38.6171%`.
M0 has stress return `-17.1306%`, profit factor `0.8692`, maximum drawdown `-42.2875%`, and
positive-profit concentration `55.25%`. All three therefore fail complete frozen stress gates,
leaving no eligible candidate to rank or freeze.

## Limitations and follow-up

The snapshot command dispositions and execution-time dirty-status comparison were added to tracked
`EVIDENCE.md` only after metric inspection, contrary to the frozen recording order. This is a
disclosed, non-outcome-changing recording deviation rather than an `indeterminate` integrity
defect: the outcome-relevant immutable run argv, workflow/policy binding, Git HEAD, exact source
bytes and hashes, manifests, and results already existed before inspection, remain independently
verifiable, and were not rerun or altered after inspection. The late prose record cannot by itself
prove its pre-inspection chronology, which remains a limitation.

No candidate may advance within S003, and its Development failure cannot be repaired by inspecting
or reusing the sealed Historical period. A separate workflow-authoring change may strengthen future
studies by automatically freezing command disposition and dirty-status evidence at execution time;
it must not rewrite this completed study or reinterpret this result as promotion or trading
authorization.
