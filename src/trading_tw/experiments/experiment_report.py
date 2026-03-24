"""Utilities for converting strategy backtest outputs into experiment format."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path


def build_experiment_report(
    *,
    experiment_id: str,
    hypothesis: str,
    universe: list[str],
    data_range: dict,
    features: list[str],
    signal_logic: str,
    portfolio_rule: str,
    cost_model: str,
    results: dict,
) -> dict:
    """Build a normalized experiment report payload."""
    now = datetime.now(UTC).isoformat()
    return {
        "experiment_id": experiment_id,
        "created_at_utc": now,
        "status": "completed",
        "hypothesis": hypothesis,
        "universe": universe,
        "data_range": data_range,
        "features": features,
        "signal": signal_logic,
        "portfolio_rule": portfolio_rule,
        "cost_model": cost_model,
        "metrics": {
            "part_a": _extract_metrics(results.get("part_a", {})),
            "part_b": _extract_metrics(results.get("part_b", {})),
            "part_c": _extract_metrics(results.get("part_c", {})),
        },
        "raw_results": results,
    }


def save_experiment_report(report: dict, output_path: str | Path) -> Path:
    """Persist experiment report JSON to disk."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def _extract_metrics(result: dict) -> dict:
    return {
        "total_signals": result.get("total_signals", 0),
        "win_rate": result.get("win_rate", 0.0),
        "avg_return_pct": result.get("avg_return_pct", 0.0),
        "std_return_pct": result.get("std_return_pct", 0.0),
        "cumulative_return_pct": result.get("cumulative_return_pct", 0.0),
        "avg_holding_days": result.get("avg_holding_days", 0.0),
        "max_drawdown_pct": result.get("max_drawdown_pct", 0.0),
        "max_consecutive_losses": result.get("max_consecutive_losses", 0),
    }
