# Proposal

## Current problem

The v005 workflow permits a `retrospective-confirmatory` checkpoint whose completed evaluation
period may precede the already-viewed Development context. The production qualification planner,
however, accepts only evaluation years and always manufactures the three immediately preceding
years as Development. For evaluation years 2010-2014 it therefore assigns 2007-2009 to
Development, even when a preregistered study assigns 2009 to warmup only and 2015-2025 to
Development context.

This mismatch cannot be repaired inside a preregistered study because it changes frozen session
roles. It also was not covered by the original retrospective tests, which retained the older
chronology in which Development immediately precedes Evaluation.

## Proposed workflow change

Require retrospective qualification plans whose Development context is not the three years
immediately before Evaluation to freeze an explicit, non-overlapping role calendar before outcome
inspection. The plan must serialize exact completed-session inventories for:

- Development context;
- warmup-only observations outside the evaluation folds; and
- retrospective evaluation.

The production CLI must accept explicit Development years and an explicit warmup-only date range
for retrospective registration. It must reject partial overrides, overlapping roles, incomplete
Development years, warmup dates that are not strictly before the first evaluation session, and any
attempt to use the retrospective override for clean Historical registration.

Existing plans retain their current deterministic derivation and wire representation. No existing
plan ID, screen, Shadow registration, or outcome is rewritten.

## Expected effect

A successor to v005/S001 can honestly freeze 2015-2025 as Development context, 2009 as warmup only,
and 2010-2014 as retrospective-confirmatory without manufacturing 2007-2008 Development evidence.
The change grants no outcome access, retrospective pass, Historical pass, Shadow status, promotion,
broker access, or order authority.
