"""
知識新鮮度檢查工具 (Knowledge Freshness Checker)

掃描 cross_asset_lessons.md 與 EXPERIMENTS_*.md 中的新鮮度 metadata，
產出過期報告，協助判斷哪些知識可能需要重新驗證。
"""

import re
from datetime import date
from pathlib import Path

LESSONS_PATH = Path(".agents/context/cross_asset_lessons.md")
DOCS_DIR = Path("src/trading/experiments")

# 過期門檻（月數）
THRESHOLD_GREEN = 3
THRESHOLD_YELLOW = 6


def _months_between(d1: date, d2: date) -> float:
    """計算兩個日期之間的近似月數"""
    return (d2.year - d1.year) * 12 + (d2.month - d1.month) + (d2.day - d1.day) / 30


def _status_icon(months_ago: float) -> str:
    """根據月數差距回傳狀態圖示"""
    if months_ago <= THRESHOLD_GREEN:
        return "✅"
    if months_ago <= THRESHOLD_YELLOW:
        return "⚠️"
    return "🔴"


def _status_label(months_ago: float) -> str:
    """回傳可讀的時間描述"""
    if months_ago < 1:
        return "< 1 month ago"
    return f"{months_ago:.0f} months ago"


def _parse_freshness_blocks(content: str) -> list[dict]:
    """解析 cross_asset_lessons.md 中的 freshness metadata 區塊"""
    lessons = []

    # 找出所有 ## N. 標題
    section_pattern = re.compile(r"^## (\d+)\.\s+(.+)$", re.MULTILINE)
    freshness_pattern = re.compile(r"<!--\s*freshness:\s*(.*?)-->", re.DOTALL)

    sections = list(section_pattern.finditer(content))

    for i, match in enumerate(sections):
        num = match.group(1)
        title = match.group(2).strip()

        # 取出這個 section 到下一個 section 之間的內容
        start = match.end()
        end = sections[i + 1].start() if i + 1 < len(sections) else len(content)
        section_content = content[start:end]

        # 在 section 內容中搜尋 freshness 區塊
        fm = freshness_pattern.search(section_content)
        if fm:
            meta_text = fm.group(1)
            meta = {}
            for line in meta_text.strip().splitlines():
                line = line.strip()
                if ":" in line:
                    key, val = line.split(":", 1)
                    meta[key.strip()] = val.strip()

            lessons.append(
                {
                    "num": num,
                    "title": title,
                    "validated": meta.get("validated"),
                    "data_through": meta.get("data_through"),
                    "confidence": meta.get("confidence"),
                    "derived_from": meta.get("derived_from"),
                }
            )
        else:
            lessons.append(
                {
                    "num": num,
                    "title": title,
                    "validated": None,
                    "data_through": None,
                    "confidence": None,
                    "derived_from": None,
                }
            )

    return lessons


def _parse_experiment_context(filepath: Path) -> dict | None:
    """解析 EXPERIMENTS_*.md 中 AI_CONTEXT 區塊的新鮮度 metadata"""
    content = filepath.read_text(encoding="utf-8")

    # 搜尋 AI_CONTEXT_START 區塊
    ctx_match = re.search(r"<!--\s*AI_CONTEXT_START[^>]*?-->", content, re.DOTALL)
    if not ctx_match:
        return None

    ctx_text = ctx_match.group(0)
    meta = {}
    for line in ctx_text.splitlines():
        line = line.strip()
        if ":" in line and not line.startswith("<!--"):
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().removesuffix("-->").strip()
            if key in ("last_validated", "data_through"):
                meta[key] = val

    if not meta:
        return None

    return {
        "file": filepath.name,
        "last_validated": meta.get("last_validated"),
        "data_through": meta.get("data_through"),
    }


def check_freshness() -> None:
    """主函數：掃描所有知識文件並產出新鮮度報告"""
    today = date.today()

    print("\n" + "=" * 70)
    print("  知識新鮮度報告 (Knowledge Freshness Report)")
    print("=" * 70)

    counts = {"green": 0, "yellow": 0, "red": 0, "unknown": 0}

    # --- cross_asset_lessons.md ---
    print(f"\n📄 {LESSONS_PATH}")

    if LESSONS_PATH.exists():
        content = LESSONS_PATH.read_text(encoding="utf-8")
        lessons = _parse_freshness_blocks(content)

        if not lessons:
            print("  (未找到任何教訓章節)")
        else:
            for lesson in lessons:
                dt = lesson["data_through"]
                if dt:
                    try:
                        dt_date = date.fromisoformat(dt)
                        months = _months_between(dt_date, today)
                        icon = _status_icon(months)
                        label = _status_label(months)

                        if months <= THRESHOLD_GREEN:
                            counts["green"] += 1
                        elif months <= THRESHOLD_YELLOW:
                            counts["yellow"] += 1
                        else:
                            counts["red"] += 1

                        conf = (
                            f", confidence: {lesson['confidence']}" if lesson["confidence"] else ""
                        )
                        print(
                            f"  {icon} {lesson['num']}. {lesson['title']}"
                            f" (data through {dt}, {label}{conf})"
                        )
                    except ValueError:
                        counts["unknown"] += 1
                        print(f"  ❓ {lesson['num']}. {lesson['title']} (invalid date: {dt})")
                else:
                    counts["unknown"] += 1
                    print(f"  ❓ {lesson['num']}. {lesson['title']} (no freshness metadata)")
    else:
        print("  (檔案不存在)")

    # --- EXPERIMENTS_*.md ---
    docs_files = sorted(DOCS_DIR.glob("EXPERIMENTS_*.md"))

    for doc_file in docs_files:
        print(f"\n📄 {doc_file}")
        ctx = _parse_experiment_context(doc_file)

        if not ctx:
            counts["unknown"] += 1
            print("  ❓ AI Context (no freshness metadata)")
            continue

        dt = ctx.get("data_through")
        validated = ctx.get("last_validated")

        if dt:
            try:
                dt_date = date.fromisoformat(dt)
                months = _months_between(dt_date, today)
                icon = _status_icon(months)
                label = _status_label(months)

                if months <= THRESHOLD_GREEN:
                    counts["green"] += 1
                elif months <= THRESHOLD_YELLOW:
                    counts["yellow"] += 1
                else:
                    counts["red"] += 1

                validated_str = f", validated {validated}" if validated else ""
                print(f"  {icon} AI Context (data through {dt}, {label}{validated_str})")
            except ValueError:
                counts["unknown"] += 1
                print(f"  ❓ AI Context (invalid date: {dt})")
        else:
            counts["unknown"] += 1
            print("  ❓ AI Context (no data_through date)")

    # --- Summary ---
    total = counts["green"] + counts["yellow"] + counts["red"] + counts["unknown"]
    print(
        f"\nSummary: {counts['green']} ✅  {counts['yellow']} ⚠️  {counts['red']} 🔴  {counts['unknown']} ❓  (total: {total})"
    )
    print("=" * 70 + "\n")
