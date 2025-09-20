# database.py
import sqlite3
import os

# 数据库文件路径 (相对于 backend 目录)
DATABASE = os.path.join(os.path.dirname(__file__), 'media.db')

def init_db():
    """初始化数据库，创建表（如果不存在）"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 创建 media 表 (如果不存在)
    # 注意：如果表已存在且没有 channel_id 列，需要先添加列
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            url TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            message_content TEXT,
            channel_id INTEGER -- 新增字段
        )
    ''')

    # --- 处理旧数据库版本 (可选但推荐) ---
    # 检查 channel_id 列是否存在
    cursor.execute("PRAGMA table_info(media)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'channel_id' not in columns:
        print("警告: 旧版数据库 detected. 正在添加 'channel_id' 列...")
        cursor.execute("ALTER TABLE media ADD COLUMN channel_id INTEGER")
        print("'channel_id' 列添加成功。")

    conn.commit()
    conn.close()
    print(f"数据库初始化完成 ({DATABASE})")

if __name__ == '__main__':
    init_db()
