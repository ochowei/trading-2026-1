# Retire the legacy experiment system and archive its final results

Legacy experiment research is terminally retired: its closed source inventory remains available
only for inspection, reproducibility, and fail-closed exit handling of pre-existing positions, while
all public legacy execution, analysis, evaluation, result publication, inventory mutation, snapshot
preparation, and promotion operations reject requests. The last retained legacy results move
byte-for-byte from `results/experiment-results/` to read-only `legacy/results/`; an append-only v010
path migration adds one bounded, same-digest retirement hop after existing v009 mappings so frozen
references continue to resolve without rewriting historical evidence. Workflow-native definitions,
released workflows, exact policy pins, and preregistered Studies are now the only path for new
outcome-relevant research.

