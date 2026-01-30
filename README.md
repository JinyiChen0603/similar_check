# 题目查重

本地脚本：对「已用题目」做相似度查重，逻辑可复用到主网页后端。

## 文件说明

| 文件 | 说明 |
|------|------|
| `questions.json` | 示例题目（题干 + 解析），含多对相似题 |
| `questions.db` | SQLite 数据库（运行 init_db.py 后生成） |
| `init_db.py` | 建表并从 JSON 导入题目，前 8 道标为「已用」 |
| `duplicate_logic.py` | 查重核心：取已用题目、算相似度、返回匹配结果 |
| `check_duplicate.py` | 本地入口：命令行传入题干，打印查重结果 |

## 使用步骤

1. **初始化数据库（首次或重置时）**
   ```bash
   python init_db.py
   ```

2. **运行查重**
   ```bash
   # 使用默认示例题（会命中库中相似题）
   python check_duplicate.py

   # 或传入题干（Windows 下若中文乱码，可先执行 chcp 65001 或从文件/主站调用逻辑）
   python check_duplicate.py "你的题目题干"
   ```

## 接入主网页

将 `duplicate_logic.py` 中的方法接入主站：

- 用主站的 DB 连接替代 `get_db_connection()`，调用 `check_duplicate(题目文本, conn)`。
- 返回格式：`{"is_duplicate": bool, "matches": [{"id", "content", "similarity"}, ...]}`，可据此做 API 或前端提示。

## 依赖

仅使用 Python 标准库（`sqlite3`、`difflib`、`json`），无需安装第三方包。
