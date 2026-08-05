# Keep snapshot blobs local and transfer them as bundles

Research data blobs live in a protected local store outside normal Git tracking, while snapshot manifests remain with persisted research results. Explicit export and import operations package a manifest with all referenced blobs for backup or transfer, and the data-access boundary remains replaceable by external object storage later. This avoids immediate Git LFS or cloud-storage complexity and repository growth while acknowledging that exact cross-machine reproduction requires transferring a snapshot bundle.
