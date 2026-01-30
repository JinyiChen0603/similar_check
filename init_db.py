# -*- coding: utf-8 -*-
"""创建数据库表并从 questions.json 导入题目。"""
import json
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "questions.db")
QUESTIONS_JSON = os.path.join(os.path.dirname(__file__), "questions.json")


def create_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            answer TEXT,
            explanation TEXT,
            used INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()


def load_questions() -> list[dict]:
    with open(QUESTIONS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def import_questions(conn: sqlite3.Connection) -> None:
    questions = load_questions()
    for i, q in enumerate(questions):
        # 前 8 道标为已用，便于演示查重（其中含多对相似题）
        used = 1 if i < 8 else 0
        conn.execute(
            "INSERT INTO questions (content, answer, explanation, used) VALUES (?, ?, ?, ?)",
            (q["content"], q.get("answer", ""), q.get("explanation", ""), used),
        )
    conn.commit()
    print(f"已导入 {len(questions)} 道题目（前 8 道为已用）。")


def main() -> None:
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("已删除旧数据库，重新创建。")
    conn = sqlite3.connect(DB_PATH)
    try:
        create_table(conn)
        import_questions(conn)
    finally:
        conn.close()
    print("数据库初始化完成:", DB_PATH)


if __name__ == "__main__":
    main()
