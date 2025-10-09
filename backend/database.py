import sqlite3
import os
from config import DATABASE, MEDIA_FOLDER

def init_db():
    """初始化数据库，创建表（如果不存在）"""
    # 确保媒体目录存在
    os.makedirs(MEDIA_FOLDER, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 创建 media 表 (如果不存在)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            url TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            message_content TEXT,
            channel_id INTEGER
        )
    ''')

    # 检查 channel_id 列是否存在（兼容旧版本数据库）
    cursor.execute("PRAGMA table_info(media)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'channel_id' not in columns:
        print("警告: 检测到旧版数据库。正在添加 'channel_id' 列...")
        cursor.execute("ALTER TABLE media ADD COLUMN channel_id INTEGER")
        print("'channel_id' 列添加成功。")

    conn.commit()
    conn.close()
    print(f"数据库初始化完成 ({DATABASE})")

def add_media(filename, url, timestamp, message_content, channel_id):
    """添加媒体记录到数据库"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO media (filename, url, timestamp, message_content, channel_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, url, timestamp, message_content, channel_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # 处理重复文件
        print(f"文件 {filename} 已存在于数据库中，跳过添加")
        return False
    except Exception as e:
        print(f"添加媒体到数据库时出错: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_all_media(channel_id=None, limit=100, offset=0):
    """获取媒体列表，支持按频道筛选和分页"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
    cursor = conn.cursor()
    
    try:
        if channel_id:
            cursor.execute('''
                SELECT * FROM media 
                WHERE channel_id = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            ''', (channel_id, limit, offset))
        else:
            cursor.execute('''
                SELECT * FROM media 
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
        
        media_list = [dict(row) for row in cursor.fetchall()]
        return media_list
    except Exception as e:
        print(f"获取媒体列表时出错: {e}")
        return []
    finally:
        conn.close()

def get_media_count(channel_id=None):
    """获取媒体总数，支持按频道筛选"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        if channel_id:
            cursor.execute('SELECT COUNT(*) FROM media WHERE channel_id = ?', (channel_id,))
        else:
            cursor.execute('SELECT COUNT(*) FROM media')
        
        count = cursor.fetchone()[0]
        return count
    except Exception as e:
        print(f"获取媒体总数时出错: {e}")
        return 0
    finally:
        conn.close()

def get_distinct_channels():
    """获取所有已收集媒体的频道ID"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT DISTINCT channel_id FROM media WHERE channel_id IS NOT NULL ORDER BY channel_id')
        channels = [row[0] for row in cursor.fetchall()]
        return channels
    except Exception as e:
        print(f"获取频道列表时出错: {e}")
        return []
    finally:
        conn.close()

def delete_media(filename):
    """从数据库中删除媒体记录"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM media WHERE filename = ?', (filename,))
        conn.commit()
        return cursor.rowcount > 0  # 返回是否有记录被删除
    except Exception as e:
        print(f"删除媒体记录时出错: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# 初始化数据库（如果尚未初始化）
if __name__ == "__main__":
    init_db()
