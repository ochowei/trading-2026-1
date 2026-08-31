# Impact

The change adds `prepared` as a workflow-version lifecycle status and makes `ACTIVATION.json` the
positive evidence of Workflow Release Activation from v010 onward. A prepared successor leaves the
prior version registered as active but blocks new studies, preregistration, resume, candidate
freeze, and new formal execution until explicit activation completes the authority transition.

Existing v008 studies are not moved or reinterpreted: S001 and S002 remain completed and S003
remains paused. Version v009 is the last release governed by canonical merge under v008. It adopts
the new contract for v010 and later releases. Policy release semantics, study outcomes, broker
access, order authority, commits, pushes, and merges are outside this change.
