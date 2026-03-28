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

    # 處理歷史檔案輪替 (latest -> prev_1 -> prev_2) (Rotate history files)
    latest_path = d / "latest.json"
    prev1_path = d / "prev_1.json"
    prev2_path = d / "prev_2.json"

    if prev1_path.exists():
        prev1_path.replace(prev2_path)
    if latest_path.exists():
        latest_path.replace(prev1_path)

    # 儲存最新的 latest.json (Save the latest result)
    latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    # 帶時間戳的備份 (Timestamped copy)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ts_path = d / f"{ts}.json"
    ts_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    # 清理舊的時間戳備份，只保留最近的 10 個 (Clean up old timestamped backups, keep max 10)
    import re

    ts_files = []
    for f in d.iterdir():
        if f.is_file() and re.match(r"^\d{8}_\d{6}\.json$", f.name):
            ts_files.append(f)

    ts_files.sort(key=lambda x: x.name)
    if len(ts_files) > 10:
        for f in ts_files[:-10]:
            try:
                f.unlink()
            except Exception as e:
                logger.warning(f"無法刪除舊結果檔案 {f}: {e}")

    logger.info(
        f"[Results] 結果已存至 {latest_path} 與 {ts_path} (Result saved to {latest_path} and {ts_path})"
    )
    return latest_path


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

    from trading.experiments import get_experiment

    loaded = {}
    display_ids = {}
    for name in names:
        result = load_latest(name)
        if result is None:
            print(f"  警告: {name} 無結果可載入 (Warning: no results for {name})")
            continue
        loaded[name] = result
        try:
            strategy = get_experiment(name)
            config = strategy.create_config()
            display_ids[name] = config.experiment_id or name[:12]
        except KeyError:
            display_ids[name] = name[:12]

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
            header += f" {display_ids.get(name, name[:12]):>12}"
        print(header)
        print(f"  {'-' * 72}")

        rows = [
            ("總訊號數 (Total signals)", "total_signals", "d"),
            ("勝率 (Win rate)", "win_rate", ".1%"),
            ("平均報酬 (Avg return %)", "avg_return_pct", ".2f"),
            ("累計報酬 (Cumulative %)", "cumulative_return_pct", ".2f"),
            ("盈虧比 (Profit factor)", "profit_factor", ".2f"),
            ("夏普比率 (Sharpe ratio)", "sharpe_ratio", ".2f"),
            ("索提諾比率 (Sortino ratio)", "sortino_ratio", ".2f"),
            ("卡瑪比率 (Calmar ratio)", "calmar_ratio", ".2f"),
        ]

        for label, key, fmt in rows:
            line = f"  {label:<36}"
            for name in loaded:
                part = loaded[name].get(part_key, {})
                val = part.get(key, 0)
                line += f" {f'{val:{fmt}}':>12}"
            print(line)

    print()
