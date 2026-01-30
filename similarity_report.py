# -*- coding: utf-8 -*-
"""从 questions.json 读取题目，比较题目、解析、答案的相似度并输出报告。"""
import sys
import json
import os

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from duplicate_logic import compute_question_similarity

QUESTIONS_JSON = os.path.join(os.path.dirname(__file__), "questions.json")


def load_questions() -> list[dict]:
    with open(QUESTIONS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def report_pair(i: int, j: int, q_a: dict, q_b: dict, threshold: float = 0.0) -> None:
    """打印一对题目的相似度（仅当综合相似度 >= threshold 时）。"""
    sim = compute_question_similarity(q_a, q_b)
    if sim["overall"] < threshold:
        return
    print(f"--- 题目 #{i+1} vs #{j+1} ---")
    print(f"  题目相似度: {sim['content']:.2%}")
    print(f"  解析相似度: {sim['explanation']:.2%}")
    print(f"  答案相似度: {sim['answer']:.2%}")
    print(f"  综合相似度: {sim['overall']:.2%}")
    print(f"  A: {(q_a.get('content') or '')[:50]}...")
    print(f"  B: {(q_b.get('content') or '')[:50]}...")
    print()


def main() -> None:
    questions = load_questions()
    if len(questions) < 2:
        print("至少需要 2 道题目才能比较。")
        return

    # 可选：只对某一道题与其余题目比较（传命令行参数 题目序号，从 1 开始）
    threshold = 0.3
    if len(sys.argv) > 1:
        try:
            idx = int(sys.argv[1])
            if idx < 1 or idx > len(questions):
                print(f"题目序号请在 1~{len(questions)} 之间。")
                return
            i = idx - 1
            q_a = questions[i]
            print(f"与第 {idx} 题比较：{(q_a.get('content') or '')[:60]}...")
            print()
            for j in range(len(questions)):
                if j == i:
                    continue
                report_pair(i, j, q_a, questions[j], threshold=0)
            return
        except ValueError:
            pass

    # 默认：两两比较，只输出综合相似度 >= threshold 的
    print(f"共 {len(questions)} 道题，输出综合相似度 >= {threshold:.0%} 的题目对：")
    print()
    for i in range(len(questions)):
        for j in range(i + 1, len(questions)):
            report_pair(i, j, questions[i], questions[j], threshold=threshold)
    print("（可传入题目序号，如: python similarity_report.py 1  只显示与第 1 题的相似度）")


if __name__ == "__main__":
    main()
