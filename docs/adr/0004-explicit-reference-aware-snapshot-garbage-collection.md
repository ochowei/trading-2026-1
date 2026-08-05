# Garbage-collect research snapshots explicitly and by reference

A research data blob is retained while any persisted research result references it through a snapshot manifest. Normal experiment and trading commands never delete blobs; an explicit garbage-collection command identifies only orphaned blobs, defaults to a dry run, and requires an apply option plus a grace period before removal. This accepts some storage growth in exchange for preventing result rotation or routine execution from silently destroying reproducibility.
