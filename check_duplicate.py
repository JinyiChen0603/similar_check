# -*- coding: utf-8 -*-
"""本地查重脚本：从命令行或默认示例题调查重并打印结果。"""
import sys

# Windows 控制台输出中文
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from duplicate_logic import check_duplicate, get_db_connection


def main() -> None:
    question_text = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "列表和元组在 Python 中的主要区别是什么？"
    )
    print("待检测题目:", question_text)
    print("-" * 50)

    conn = get_db_connection()
    try:
        result = check_duplicate(question_text, conn)
        print("是否与已用题目重复/相似:", result["is_duplicate"])
        if result["matches"]:
            print("匹配到的已用题目:")
            for m in result["matches"]:
                print(f"  [id={m['id']}] 相似度 {m['similarity']:.2%}")
                print(f"    题干: {m['content'][:60]}{'...' if len(m['content'])>60 else ''}")
        else:
            print("未发现相似题目。")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
