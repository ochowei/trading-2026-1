"""
結果管理模組 (Results Management)
儲存、載入與比較實驗結果。
Save, load, and compare experiment results.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

RESULTS_DIR = Path("results")


def save_result(experiment_name: str, result: dict) -> Path:
    """
    儲存回測結果 (Save backtest result)

    存為 results/{experiment_name}/latest.json 及帶時間戳的備份。
    Saves to results/{experiment_name}/latest.json and a timestamped copy.
    """
    d = RESULTS_DIR / experiment_name
    d.mkdir(parents=True, exist_ok=True)

    # 帶時間戳的備份 (Timestamped copy)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = d / f"{ts}.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    # latest.json
    (d / "latest.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))

    logger.info(f"[Results] 結果已存至 {path} (Result saved to {path})")
    return path


def load_latest(experiment_name: str) -> dict | None:
    """載入最新結果 (Load latest result for an experiment)"""
    path = RESULTS_DIR / experiment_name / "latest.json"
    if path.exists():
        return json.loads(path.read_text())
    return None


def compare_experiments(names: list[str]) -> None:
    """
    比較多個實驗的最新結果 (Compare latest results across experiments)
    """
    separator = "=" * 80
    thin_sep = "-" * 80

    loaded = {}
    for name in names:
        result = load_latest(name)
        if result is None:
            print(f"  警告: {name} 無結果可載入 (Warning: no results for {name})")
            continue
        loaded[name] = result

    if len(loaded) < 2:
        print("  需要至少兩個實驗結果才能比較 (Need at least 2 experiment results to compare)")
        return

    print(f"\n{separator}")
    print("  跨實驗績效比較 (Cross-Experiment Comparison)")
    print(f"{separator}")

    # 比較每個 part
    for part_key, part_label in [
        ("part_a", "Part A (In-Sample)"),
        ("part_b", "Part B (Out-of-Sample)"),
        ("part_c", "Part C (Live)"),
    ]:
        print(f"\n  {part_label}")
        print(f"  {thin_sep}")

        header = f"  {'指標 (Metric)':<36}"
        for name in loaded:
            header += f" {name[:12]:>12}"
        print(header)
        print(f"  {'-'*72}")

        rows = [
            ("總訊號數 (Total signals)", "total_signals", "d"),
            ("勝率 (Win rate)", "win_rate", ".1%"),
            ("平均報酬 (Avg return %)", "avg_return_pct", ".2f"),
            ("累計報酬 (Cumulative %)", "cumulative_return_pct", ".2f"),
        ]

        for label, key, fmt in rows:
            line = f"  {label:<36}"
            for name in loaded:
                part = loaded[name].get(part_key, {})
                val = part.get(key, 0)
                line += f" {f'{val:{fmt}}':>12}"
            print(line)

    print()
