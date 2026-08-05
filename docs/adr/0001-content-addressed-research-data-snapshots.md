# Share content-addressed research data snapshots

Persisted research results reference an immutable snapshot manifest whose primary and auxiliary market datasets are stored as shared, content-addressed CSV blobs. This preserves exact reproducibility when the disposable market data cache changes while avoiding the storage cost and ambiguity of copying a complete dataset into every experiment directory.

## Consequences

The snapshot store must retain a blob while any persisted result references it, and every data dependency used by an experiment must appear in its manifest. Cache files are never valid substitutes for referenced snapshot blobs.
