#!/usr/bin/env python3
"""Enforce the Phase 9 experiment market-data bypass policy."""

from __future__ import annotations

import argparse
from pathlib import Path

from trading.market_data.migration_policy import (
    MarketDataPolicyError,
    enforce_monotonic_shrink,
    load_allowlist,
    scan_experiment_market_data_bypasses,
    scan_non_experiment_yfinance_bypasses,
    validate_allowlist,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=None,
        help="active Phase 9 allowlist JSON; omit after zero-tolerance cleanup",
    )
    parser.add_argument(
        "--base-allowlist",
        type=Path,
        default=None,
        help="allowlist from the PR base revision for monotonic-shrink enforcement",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    findings = scan_experiment_market_data_bypasses(repo_root)
    provider_violations = scan_non_experiment_yfinance_bypasses(repo_root)

    try:
        if provider_violations:
            rendered = ", ".join(finding.path for finding in provider_violations)
            raise MarketDataPolicyError(f"yfinance is only allowed in provider.py: {rendered}")
        if args.allowlist is None:
            if findings:
                raise MarketDataPolicyError(
                    "experiment market-data bypasses remain but no allowlist was supplied"
                )
        else:
            document = load_allowlist(args.allowlist)
            validate_allowlist(document.entries, findings, repo_root=repo_root)
            if args.base_allowlist is not None:
                base = load_allowlist(args.base_allowlist)
                enforce_monotonic_shrink(base.entries, document.entries)
    except MarketDataPolicyError as exc:
        print(f"Phase 9 market-data policy failed: {exc}")
        return 1

    print(
        "Phase 9 market-data policy passed: "
        f"{len(findings)} active bypass finding(s), provider boundary is clean"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
