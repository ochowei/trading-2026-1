"""
Markdown 表格解析與同步檢查工具 (Markdown Table Parser & Sync Checker)
"""

import json
import logging
import re
from pathlib import Path

from trading.experiments import get_experiment

logger = logging.getLogger(__name__)

RESULTS_DIR = Path("results")
DOCS_DIR = Path("src/trading/experiments")


def extract_markdown_tables(filepath: Path) -> dict:
    """
    從 markdown 檔案提取表格
    Returns dict: {
        "Part A": {"TQQQ-001": {"total_signals": 20, "win_rate": 85.0, ...}},
        "Part B": {...}
    }
    """
    content = filepath.read_text(encoding="utf-8")
    lines = content.splitlines()

    current_part = None
    tables = {}

    in_table = False
    headers = []

    for line in lines:
        line = line.strip()

        # 偵測段落標題 (Detect section headers)
        m = re.match(r"^###\s+Part\s+([A-Z]).*", line, re.IGNORECASE)
        if m:
            part_letter = m.group(1).upper()
            if part_letter == "A":
                current_part = "part_a"
            elif part_letter == "B":
                current_part = "part_b"
            elif part_letter == "C":
                current_part = "part_c"

            if current_part not in tables:
                tables[current_part] = {}
            in_table = False
            continue

        if not current_part:
            continue

        if line.startswith("|"):
            # 處理表格列
            cols = [c.strip() for c in line.split("|")[1:-1]]

            # 判斷是否為標題列
            if not in_table:
                if cols and "ID" in cols[0] or "ID" == cols[0].strip():
                    headers = cols
                elif all(c.startswith("-") or c.startswith(":") for c in cols) and headers:
                    in_table = True
                continue

            # 資料列
            if in_table and cols and headers:
                if len(cols) == len(headers):
                    row_id = cols[0]

                    row_data = {}
                    for _i, (header, val) in enumerate(zip(headers, cols, strict=False)):
                        if header == "ID":
                            continue

                        # 處理常見欄位
                        val_clean = val.replace("%", "").replace("+", "").strip()
                        try:
                            if "訊號數" in header or "成交數" in header or "悲觀認定次數" in header:
                                row_data[header] = int(val_clean)
                            elif (
                                "勝率" in header
                                or "成交率" in header
                                or "平均報酬" in header
                                or "累計報酬" in header
                                or "最大回撤" in header
                            ):
                                row_data[header] = float(val_clean)
                            else:
                                row_data[header] = val
                        except ValueError:
                            row_data[header] = val

                    tables[current_part][row_id] = row_data

        else:
            in_table = False

    return tables


def find_latest_json(experiment_id: str) -> dict | None:
    """根據實驗 ID 尋找對應的 latest.json"""
    for exp_dir in RESULTS_DIR.iterdir():
        if not exp_dir.is_dir():
            continue

        # 嘗試解析 experiment_id
        # 我們可能不知道資料夾名稱，所以需要讀取 latest.json 裡面或者找 config
        latest_path = exp_dir / "latest.json"
        if latest_path.exists():
            try:
                # 若能根據目錄名稱取得 experiment 實例
                strategy = get_experiment(exp_dir.name)
                config = strategy.create_config()
                if config.experiment_id == experiment_id:
                    return json.loads(latest_path.read_text(encoding="utf-8"))
            except Exception:
                pass

            # 或者嘗試透過目錄名稱字首比對
            if exp_dir.name.lower().startswith(experiment_id.lower().replace("-", "_")):
                return json.loads(latest_path.read_text(encoding="utf-8"))

    return None


def compare_docs_and_results() -> None:
    """
    比對 EXPERIMENTS_*.md 中的表格與 results/*/latest.json，
    印出差異報告。
    """
    print("\n" + "=" * 80)
    print("  文件同步檢查報告 (Documentation Sync Report)")
    print("=" * 80 + "\n")

    docs_files = list(DOCS_DIR.glob("EXPERIMENTS_*.md"))
    if not docs_files:
        print("未找到任何 EXPERIMENTS_*.md 檔案 (No documentation files found)")
        return

    differences_found = False

    for doc_file in docs_files:
        print(f"📄 正在檢查 {doc_file.name} ...")

        tables = extract_markdown_tables(doc_file)

        if not tables:
            print(f"  找不到效能表格 (No performance tables found in {doc_file.name})\n")
            continue

        doc_diffs = []

        for part_key, part_tables in tables.items():
            for exp_id, doc_data in part_tables.items():
                result = find_latest_json(exp_id)
                if not result:
                    # 找不到 json 可能只是尚未執行過，不列為錯誤
                    continue

                part_result = result.get(part_key, {})
                if not part_result:
                    continue

                # 準備比對欄位對應
                mappings = [
                    # (doc_header_keyword, json_key, type_cast_func, is_percentage, decimal_places)
                    ("訊號數", "total_signals", int, False, 0),
                    ("成交數", "total_executions", int, False, 0),
                    ("成交率", "execution_rate", float, True, 1),
                    ("勝率", "win_rate", float, True, 1),
                    ("平均報酬", "avg_return_pct", float, False, 2),
                    ("累計報酬", "cumulative_return_pct", float, False, 2),
                    ("最大回撤", "max_drawdown_pct", float, False, 2),
                    ("悲觀認定次數", "pessimistic_executions", int, False, 0),
                ]

                for doc_header, json_key, type_cast, is_pct, decimals in mappings:
                    # 尋找對應的 doc_header
                    actual_doc_header = next((h for h in doc_data.keys() if doc_header in h), None)
                    if not actual_doc_header:
                        continue

                    doc_val = doc_data[actual_doc_header]
                    json_val = part_result.get(json_key)

                    if json_val is None:
                        continue

                    # 數值比較
                    try:
                        if type_cast is float:
                            if is_pct:
                                json_val_comp = json_val * 100
                            else:
                                json_val_comp = json_val

                            # 使用字串格式化來比較，以避免浮點數誤差
                            json_val_str = f"{json_val_comp:.{decimals}f}"
                            doc_val_str = f"{float(doc_val):.{decimals}f}"

                            if doc_val_str != json_val_str:
                                diff_msg = f"    [{part_key.upper()}] {exp_id} {doc_header}: 標記為 {doc_val_str} (MD) vs 實際為 {json_val_str} (JSON)"
                                doc_diffs.append(diff_msg)
                        else:
                            json_val_comp = type_cast(json_val)
                            doc_val_comp = type_cast(doc_val)

                            if json_val_comp != doc_val_comp:
                                diff_msg = f"    [{part_key.upper()}] {exp_id} {doc_header}: 標記為 {doc_val_comp} (MD) vs 實際為 {json_val_comp} (JSON)"
                                doc_diffs.append(diff_msg)
                    except (ValueError, TypeError):
                        # 解析錯誤跳過
                        pass

        if doc_diffs:
            print(f"  ❌ 發現 {len(doc_diffs)} 處不一致 (Differences found):")
            for diff in doc_diffs:
                print(diff)
            differences_found = True
        else:
            print("  ✅ 數據一致 (Data in sync)")
        print()

    if not differences_found:
        print(
            "🎉 所有文件數值皆與最新結果一致！(All documentations are in sync with latest results!)"
        )
        print("=" * 80 + "\n")
    else:
        print(
            "⚠️ 警告：有不一致的結果。請手動更新 Markdown 文件。 (Warning: Differences found. Please update Markdown files manually.)"
        )
        print("=" * 80 + "\n")


if __name__ == "__main__":
    compare_docs_and_results()
