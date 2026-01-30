# -*- coding: utf-8 -*-
"""查重核心逻辑：从数据库取已用题目、算相似度、返回是否重复及匹配列表。"""
import difflib
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "questions.db")


def get_used_questions(conn: sqlite3.Connection) -> list[tuple[int, str]]:
    """从数据库取出所有已用题目的 (id, content)。"""
    cur = conn.execute(
        "SELECT id, content FROM questions WHERE used = 1 ORDER BY id"
    )
    return [(row[0], row[1]) for row in cur.fetchall()]


def compute_similarity(text_a: str, text_b: str) -> float:
    """计算两段文本的相似度，返回 0~1。"""
    a, b = (text_a or "").strip(), (text_b or "").strip()
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def compute_question_similarity(
    q_a: dict,
    q_b: dict,
    *,
    weight_content: float = 0.5,
    weight_explanation: float = 0.3,
    weight_answer: float = 0.2,
) -> dict:
    """
    比较两道题的题目、解析、答案，返回各维度相似度与综合相似度。

    :param q_a: 题目 dict，需含 content, explanation, answer（可缺省）
    :param q_b: 同上
    :param weight_content: 题目权重，默认 0.5
    :param weight_explanation: 解析权重，默认 0.3
    :param weight_answer: 答案权重，默认 0.2
    :return: {"content": float, "explanation": float, "answer": float, "overall": float}
    """
    c_a = (q_a.get("content") or "").strip()
    c_b = (q_b.get("content") or "").strip()
    e_a = (q_a.get("explanation") or "").strip()
    e_b = (q_b.get("explanation") or "").strip()
    a_a = (q_a.get("answer") or "").strip()
    a_b = (q_b.get("answer") or "").strip()

    sim_content = compute_similarity(c_a, c_b)
    sim_explanation = compute_similarity(e_a, e_b)
    sim_answer = compute_similarity(a_a, a_b)

    overall = (
        weight_content * sim_content
        + weight_explanation * sim_explanation
        + weight_answer * sim_answer
    )
    return {
        "content": round(sim_content, 4),
        "explanation": round(sim_explanation, 4),
        "answer": round(sim_answer, 4),
        "overall": round(overall, 4),
    }


def find_similar_questions(
    user_question: dict,
    question_list: list[dict],
    *,
    threshold: float = 0.3,
    top_k: int | None = None,
    weight_content: float = 0.5,
    weight_explanation: float = 0.3,
    weight_answer: float = 0.2,
) -> list[tuple[int, dict, dict]]:
    """
    在一道题与题目列表中找出综合相似度 >= 阈值的题目，按综合相似度从高到低排序。

    :param user_question: 待比较的题目 dict，需含 content, explanation, answer（可缺省）
    :param question_list: 题目列表，每项为同结构的 dict
    :param threshold: 综合相似度 >= 此值才纳入结果，默认 0.3
    :param top_k: 最多返回几条，None 表示不限制
    :param weight_content: 题目权重，默认 0.5
    :param weight_explanation: 解析权重，默认 0.3
    :param weight_answer: 答案权重，默认 0.2
    :return: [(题目序号从1起, 题目dict, 相似度dict), ...]，按 overall 降序
    """
    results = []
    for i, q in enumerate(question_list):
        sim = compute_question_similarity(
            user_question,
            q,
            weight_content=weight_content,
            weight_explanation=weight_explanation,
            weight_answer=weight_answer,
        )
        if sim["overall"] >= threshold:
            results.append((i + 1, q, sim))
    results.sort(key=lambda x: x[2]["overall"], reverse=True)
    if top_k is not None:
        results = results[:top_k]
    return results


def check_duplicate(
    question_text: str,
    conn: sqlite3.Connection,
    *,
    threshold: float = 0.75,
    exclude_id: int | None = None,
) -> dict:
    """
    检查题目是否与已用题目重复或高度相似。

    :param question_text: 待检测的题目题干
    :param conn: 数据库连接（支持 sqlite3.Connection）
    :param threshold: 相似度阈值，>= 此值视为重复，默认 0.75
    :param exclude_id: 若为编辑已有题目，传入该题 id 以排除自身
    :return: {"is_duplicate": bool, "matches": [{"id", "content", "similarity"}, ...]}
    """
    used = get_used_questions(conn)
    matches = []
    for qid, used_text in used:
        if exclude_id is not None and qid == exclude_id:
            continue
        sim = compute_similarity(question_text, used_text)
        if sim >= threshold:
            matches.append({
                "id": qid,
                "content": used_text,
                "similarity": round(sim, 4),
            })
    matches.sort(key=lambda x: x["similarity"], reverse=True)
    return {
        "is_duplicate": len(matches) > 0,
        "matches": matches[:10],
    }


def get_db_connection() -> sqlite3.Connection:
    """返回默认 SQLite 数据库连接（供本地脚本使用）。"""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"请先运行 init_db.py 初始化数据库: {DB_PATH}")
    return sqlite3.connect(DB_PATH)
