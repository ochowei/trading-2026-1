from __future__ import annotations

import json
from pathlib import Path

import pytest

from trading.market_data.migration_policy import (
    BypassFinding,
    MarketDataPolicyError,
    canonical_allowlist_entries,
    enforce_monotonic_shrink,
    load_allowlist,
    scan_experiment_market_data_bypasses,
    scan_non_experiment_yfinance_bypasses,
    scan_non_provider_yfinance_bypasses,
    validate_allowlist,
)


def write_experiment(root: Path, name: str, source: str) -> Path:
    path = root / "src" / "trading" / "experiments" / name / "signal_detector.py"
    path.parent.mkdir(parents=True)
    path.write_text(source)
    return path


def test_scanner_detects_yfinance_import_alias_and_api_call(tmp_path: Path) -> None:
    write_experiment(
        tmp_path,
        "fixture",
        "import yfinance as market\n\nmarket.download('SPY')\n",
    )

    findings = scan_experiment_market_data_bypasses(tmp_path)

    assert [(finding.kind, finding.path) for finding in findings] == [
        ("direct-yfinance", "src/trading/experiments/fixture/signal_detector.py")
    ]
    assert findings[0].api_forms == ("import:yfinance", "market.download")


@pytest.mark.parametrize(
    "source",
    [
        "from yfinance import download as fetch\nfetch('SPY')\n",
        "import importlib\nimportlib.import_module('yfinance')\n",
        "import importlib as loader\nloader.import_module('yfinance')\n",
        "from importlib import import_module as loader\nloader('yfinance')\n",
        "__import__('yfinance')\n",
        "import yfinance as yf\nyf.Ticker('SPY')\n",
    ],
)
def test_scanner_detects_direct_yfinance_variants(tmp_path: Path, source: str) -> None:
    write_experiment(tmp_path, "fixture", source)

    findings = scan_experiment_market_data_bypasses(tmp_path)

    assert len(findings) == 1
    assert findings[0].kind == "direct-yfinance"


def test_scanner_detects_datafetcher_bypass_without_yfinance_import(tmp_path: Path) -> None:
    write_experiment(
        tmp_path,
        "fixture",
        "from trading.core.data_fetcher import DataFetcher\n\nDataFetcher().fetch_all(['SPY'])\n",
    )

    findings = scan_experiment_market_data_bypasses(tmp_path)

    assert [(finding.kind, finding.path) for finding in findings] == [
        ("indirect-datafetcher", "src/trading/experiments/fixture/signal_detector.py")
    ]


def test_allowlist_entries_are_canonical_and_match_findings() -> None:
    findings = (
        BypassFinding("direct-yfinance", "src/trading/experiments/a.py", (3,), ("yf.download",)),
        BypassFinding(
            "indirect-datafetcher", "src/trading/experiments/b.py", (4,), ("DataFetcher",)
        ),
    )

    entries = canonical_allowlist_entries(findings)

    assert entries == (
        ("direct-yfinance", "src/trading/experiments/a.py"),
        ("indirect-datafetcher", "src/trading/experiments/b.py"),
    )
    validate_allowlist(entries, findings)


def test_allowlist_rejects_duplicate_stale_and_missing_entries() -> None:
    findings = (BypassFinding("direct-yfinance", "src/trading/experiments/a.py", (3,), ()),)

    with pytest.raises(MarketDataPolicyError, match="duplicate"):
        validate_allowlist(
            (
                ("direct-yfinance", "src/trading/experiments/a.py"),
                ("direct-yfinance", "src/trading/experiments/a.py"),
            ),
            findings,
        )

    with pytest.raises(MarketDataPolicyError, match="stale"):
        validate_allowlist(
            (("direct-yfinance", "src/trading/experiments/removed.py"),),
            findings,
        )

    with pytest.raises(MarketDataPolicyError, match="missing"):
        validate_allowlist((), findings)


def test_allowlist_cannot_grow() -> None:
    base = (("direct-yfinance", "src/trading/experiments/a.py"),)
    current = (
        ("direct-yfinance", "src/trading/experiments/a.py"),
        ("direct-yfinance", "src/trading/experiments/new.py"),
    )

    with pytest.raises(MarketDataPolicyError, match="grow"):
        enforce_monotonic_shrink(base, current)

    enforce_monotonic_shrink(
        current,
        (("direct-yfinance", "src/trading/experiments/a.py"),),
    )


def test_load_allowlist_rejects_noncanonical_payload(tmp_path: Path) -> None:
    path = tmp_path / "allowlist.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "baseline_commit": "abc",
                "entries": [
                    {
                        "kind": "direct-yfinance",
                        "path": "./src/trading/experiments/a.py",
                    }
                ],
            }
        )
    )

    with pytest.raises(MarketDataPolicyError, match="canonical"):
        load_allowlist(path)


def test_repository_baseline_has_exact_known_findings() -> None:
    repo_root = Path(__file__).parents[1]

    findings = scan_experiment_market_data_bypasses(repo_root)

    # SPY-003, URA-006, CIBR-006, the NVDA RS slices, the remaining TSM
    # slices, the TSLA macro slices, the remaining GLD macro slices, the FCX
    # macro/relative-strength slices, the EWT/SOXL semiconductor slices, the
    # EEM macro/divergence slices, the FXI China/currency slices, the INDA
    # macro/relative-strength slices, the EWZ Brazil/EM slices, and the EWJ
    # Japan/FX slices were migrated to verified auxiliary bundles; the active
    # inventory therefore shrinks monotonically; the DIA index/divergence
    # slices are also now behind the verified auxiliary bundle boundary, as is
    # the IWM/SPY momentum-rotation slice, the TLT duration/rate-volatility
    # slices, the TQQQ volatility/divergence slices, and the USO
    # implied-volatility/divergence slices, the XBI volatility/pairs slices,
    # and the XLU rate/volatility slices, and the SIVR ratio/volatility slices,
    # and the COPX macro/underlying slices, the final CIBR/NVDA/VGK direct
    # slices, and the remaining legacy DataFetcher slices are now migrated to
    # verified auxiliary bundles.
    assert len(findings) == 0
    assert sum(finding.kind == "direct-yfinance" for finding in findings) == 0
    assert sum(finding.kind == "indirect-datafetcher" for finding in findings) == 0


def test_repository_allowlist_matches_the_scanned_baseline() -> None:
    repo_root = Path(__file__).parents[1]
    document = load_allowlist(repo_root / "ci" / "market-data-bypass-allowlist.json")
    findings = scan_experiment_market_data_bypasses(repo_root)

    validate_allowlist(document.entries, findings, repo_root=repo_root)
    assert document.baseline_commit == "41da32ef7f6b2eda5af9fd7bc05b1261a2259294"


def test_provider_is_the_only_legal_runtime_yfinance_boundary(tmp_path: Path) -> None:
    provider = tmp_path / "src" / "trading" / "market_data" / "provider.py"
    provider.parent.mkdir(parents=True)
    provider.write_text("import yfinance as yf\n")
    write_experiment(tmp_path, "fixture", "import yfinance as yf\nyf.download('SPY')\n")
    bad_runtime = tmp_path / "src" / "trading" / "core" / "bad.py"
    bad_runtime.parent.mkdir(parents=True)
    bad_runtime.write_text("import yfinance as yf\nyf.download('SPY')\n")

    findings = scan_non_experiment_yfinance_bypasses(tmp_path)

    assert [finding.path for finding in findings] == ["src/trading/core/bad.py"]


def test_repository_legacy_yfinance_bypasses_are_confined_to_experiments() -> None:
    repo_root = Path(__file__).parents[1]

    assert scan_non_experiment_yfinance_bypasses(repo_root) == ()
    assert len(scan_non_provider_yfinance_bypasses(repo_root)) == 0
