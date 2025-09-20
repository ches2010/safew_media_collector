# backend/app.py
import discord
from discord.ext import commands
import asyncio
import os
import requests
from flask import Flask, jsonify, send_from_directory, request, abort
from flask_cors import CORS
import sqlite3
import uuid # 用于生成唯一文件名
from config import DISCORD_TOKEN, DISCORD_CHANNEL_IDS, FLASK_HOST, FLASK_PORT, MEDIA_FOLDER # 注意导入更新
from database import init_db, DATABASE

# --- Discord Bot 部分 ---
intents = discord.Intents.default()
intents.message_content = True
# 使用 commands.Bot 通常更方便，但为了简单起见，这里用 discord.Client
# bot = commands.Bot(command_prefix='!', intents=intents)
bot = discord.Client(intents=intents)

async def download_media(url, filename, channel_id):
    """下载媒体文件并保存"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status() # 如果状态码不是 200，会抛出异常
        filepath = os.path.join(MEDIA_FOLDER, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"已下载: {filename} (来自频道 {channel_id})") # 添加频道信息
        return True
    except Exception as e:
        print(f"下载 {filename} 失败 (来自频道 {channel_id}): {e}")
        return False

def save_media_info(filename, url, timestamp, message_content, channel_id): # 添加 channel_id 参数
    """将媒体信息保存到数据库"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO media (filename, url, timestamp, message_content, channel_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, url, timestamp, message_content, channel_id)) # 传递 channel_id
        conn.commit()
        conn.close()
        print(f"已保存信息: {filename} (来自频道 {channel_id})")
    except Exception as e:
        print(f"保存数据库信息失败 (来自频道 {channel_id}): {e}")

@bot.event
async def on_ready():
    print(f'{bot.user} 已连接到 Discord!')
    # 启动 Flask 应用
    asyncio.create_task(run_flask())

@bot.event
async def on_message(message):
    # 防止机器人回复自己
    if message.author == bot.user:
        return

    # 检查消息是否来自配置的频道之一
    if message.channel.id in DISCORD_CHANNEL_IDS: # 使用列表检查
        print(f"在频道 {message.channel.id} 收到消息: {message.content}")
        timestamp = message.created_at.isoformat()
        message_content = message.content if message.content else None

        # 检查是否有附件
        for attachment in message.attachments:
            if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp4', '.mov', '.avi', '.mkv')):
                # 生成唯一文件名以防重名
                unique_filename = f"{uuid.uuid4()}_{attachment.filename}"
                url_path = f"/media/{unique_filename}" # Flask 路由路径

                # 下载文件
                success = await download_media(attachment.url, unique_filename, message.channel.id)
                if success:
                    # 保存信息到数据库
                    save_media_info(unique_filename, url_path, timestamp, message_content, message.channel.id)

# --- Flask API 部分 ---
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..', 'frontend'), 'index.html')

@app.route('/media')
def list_media():
    """API 端点：获取媒体列表，支持按时间、频道筛选"""
    # 获取查询参数
    since = request.args.get('since') # ISO 格式字符串, e.g., '2023-10-27T10:00:00'
    until = request.args.get('until') # ISO 格式字符串
    channel_id = request.args.get('channel_id') # 新增：频道 ID 筛选

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM media WHERE 1=1' # 基础查询
    params = []

    # 根据参数动态构建查询
    if since:
        query += ' AND timestamp >= ?'
        params.append(since)
    if until:
        query += ' AND timestamp <= ?'
        params.append(until)
    if channel_id:
        query += ' AND channel_id = ?'
        params.append(channel_id)

    query += ' ORDER BY timestamp DESC'

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    media_list = [dict(row) for row in rows]
    return jsonify(media_list)

@app.route('/media/<int:media_id>', methods=['DELETE'])
def delete_media(media_id):
    """API 端点：根据 ID 删除媒体记录和文件"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT filename FROM media WHERE id = ?', (media_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        abort(404, description="Media not found")

    filename = result[0]
    file_path = os.path.join(MEDIA_FOLDER, filename)

    cursor.execute('DELETE FROM media WHERE id = ?', (media_id,))
    deleted_rows = cursor.rowcount
    conn.commit()
    conn.close()

    if deleted_rows == 0:
         abort(404, description="Media not found")

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        else:
            print(f"File not found on disk, only DB record deleted: {file_path}")
        return jsonify({"message": "Media deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return jsonify({"message": f"DB record deleted, but error deleting file: {str(e)}"}), 500

@app.route('/media/<filename>')
def serve_media(filename):
    """提供媒体文件服务"""
    return send_from_directory(MEDIA_FOLDER, filename)

# --- 新增：获取频道列表 API ---
@app.route('/channels', methods=['GET'])
def list_channels():
    """API 端点：获取正在监听的频道 ID 列表"""
    # 注意：这里返回的是 ID。在实际应用中，
    # 你可能需要通过 Discord API 获取频道名称。
    # 但对于简单的筛选，ID 就足够了。
    # 或者，可以在 .env 中维护一个 ID -> Name 的映射。
    return jsonify({"channel_ids": DISCORD_CHANNEL_IDS})

async def run_flask():
    """在异步任务中运行 Flask 应用"""
    # 注意：直接在 asyncio 事件循环中运行阻塞的 Flask 应用不是最佳实践
    # 更好的方式是使用 ASGI 服务器 (如 Hypercorn, Uvicorn) 或者在单独的线程中运行 Flask
    # 这里为了简单演示，直接运行。但在生产环境中请考虑改进。
    import threading
    def run_app():
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, use_reloader=False)
    flask_thread = threading.Thread(target=run_app)
    flask_thread.start()
    # app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True) # debug=True 会与 asyncio 冲突

def start_bot():
    """启动 Discord 机器人"""
    bot.run(DISCORD_TOKEN)

if __name__ == '__main__':
    init_db() # 初始化数据库
    start_bot()
