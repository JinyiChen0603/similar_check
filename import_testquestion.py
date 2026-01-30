# -*- coding: utf-8 -*-
"""从 testquestion.csv 或 testquestion.xlsx 导入题目到 questions.json（相似题目、解析、答案）。"""
import csv
import json
import os

QUESTIONS_JSON = os.path.join(os.path.dirname(__file__), "questions.json")
PROJECT_DIR = os.path.dirname(__file__)


def find_testquestion_file() -> tuple[str, str]:
    """查找 testquestion.csv 或 testquestion.xlsx，返回 (路径, 'csv'|'xlsx')。"""
    for name in ("testquestion.csv", "testquestion.xlsx"):
        path = os.path.join(PROJECT_DIR, name)
        if os.path.exists(path):
            ext = "csv" if name.endswith(".csv") else "xlsx"
            return path, ext
    raise FileNotFoundError("未找到 testquestion.csv 或 testquestion.xlsx，请放在项目目录下。")


def load_csv(path: str) -> list[dict]:
    """从 CSV 读取，列：题目ID, 相似题目, 解析, 答案（其余列忽略）。"""
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 兼容不同列名
            content = (row.get("相似题目") or row.get("题目") or "").strip()
            explanation = (row.get("解析") or "").strip()
            answer = (row.get("答案") or "").strip()
            if content:
                rows.append({
                    "content": content,
                    "answer": answer,
                    "explanation": explanation,
                })
    return rows


def load_xlsx(path: str) -> list[dict]:
    """从 XLSX 读取，列：题目ID, 相似题目, 解析, 答案。"""
    try:
        import openpyxl
    except ImportError:
        raise ImportError("读取 xlsx 需要安装 openpyxl：pip install openpyxl")
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb.active
    all_rows = list(ws.iter_rows(values_only=True))
    wb.close()
    if not all_rows:
        return []
    header = [str(h).strip() if h is not None else "" for h in all_rows[0]]
    idx_content = idx_expl = idx_ans = -1
    for j, h in enumerate(header):
        if "相似题目" in h or h == "题目":
            idx_content = j
        if "解析" in h:
            idx_expl = j
        if "答案" in h:
            idx_ans = j
    if idx_content < 0:
        idx_content = 1
    rows = []
    for row in all_rows[1:]:
        row = [str(c).strip() if c is not None else "" for c in (row or [])]
        content = row[idx_content] if idx_content < len(row) else ""
        explanation = row[idx_expl] if idx_expl >= 0 and idx_expl < len(row) else ""
        answer = row[idx_ans] if idx_ans >= 0 and idx_ans < len(row) else ""
        if content:
            rows.append({
                "content": content,
                "answer": answer,
                "explanation": explanation,
            })
    return rows


def load_questions_json() -> list[dict]:
    with open(QUESTIONS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_questions_json(questions: list[dict]) -> None:
    with open(QUESTIONS_JSON, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)


def main() -> None:
    path, ext = find_testquestion_file()
    print(f"使用文件: {path}")

    if ext == "csv":
        new_items = load_csv(path)
    else:
        new_items = load_xlsx(path)

    if not new_items:
        print("未解析到任何题目（需有「相似题目」列且非空）。")
        return

    existing = load_questions_json()
    existing.extend(new_items)
    save_questions_json(existing)
    print(f"已导入 {len(new_items)} 道题目到 questions.json，当前共 {len(existing)} 道。")


if __name__ == "__main__":
    main()
