# -*- coding: utf-8 -*-
"""在终端输入题干、解析、答案（用回车区分），与 questions.json 中的题目比较，输出高度相似的题目。"""
import sys
import json
import os

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stdin.encoding and sys.stdin.encoding.lower() != "utf-8":
    try:
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

from duplicate_logic import compute_question_similarity

QUESTIONS_JSON = os.path.join(os.path.dirname(__file__), "questions.json")
THRESHOLD = 0.3  # 综合相似度 >= 此值视为高度相似


def load_questions() -> list[dict]:
    with open(QUESTIONS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    print("请依次输入题干、解析、答案，每项输入完成后按回车进入下一项。")
    print("-" * 50)

    try:
        content = input("【题干】请输入题干：").strip()
        explanation = input("【解析】请输入解析：").strip()
        answer = input("【答案】请输入答案：").strip()
    except EOFError:
        print("输入已中断。")
        return

    if not content:
        print("题干不能为空，已退出。")
        return

    user_question = {
        "content": content,
        "explanation": explanation,
        "answer": answer,
    }

    questions = load_questions()
    if not questions:
        print("questions.json 中暂无题目。")
        return

    results = []
    for i, q in enumerate(questions):
        sim = compute_question_similarity(user_question, q)
        results.append((i + 1, q, sim))

    results.sort(key=lambda x: x[2]["overall"], reverse=True)

    print()
    print(f"与 JSON 中 {len(questions)} 道题比较后，综合相似度 >= {THRESHOLD:.0%} 的题目如下：")
    print("-" * 50)

    found = False
    for idx, q, sim in results:
        if sim["overall"] < THRESHOLD:
            continue
        found = True
        print(f"--- 第 {idx} 题（综合相似度 {sim['overall']:.2%}）---")
        print(f"  题目相似度: {sim['content']:.2%}  解析相似度: {sim['explanation']:.2%}  答案相似度: {sim['answer']:.2%}")
        content_preview = (q.get("content") or "").strip()
        if len(content_preview) > 70:
            content_preview = content_preview[:70] + "..."
        print(f"  题干: {content_preview}")
        print()

    if not found:
        print("未发现高度相似的题目。")
    else:
        print("（以上按综合相似度从高到低排列）")


if __name__ == "__main__":
    main()
