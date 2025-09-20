import discord
import asyncio
import os
import sqlite3
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import threading
from config import DISCORD_TOKEN, CHANNEL_ID, FLASK_HOST, FLASK_PORT, MEDIA_FOLDER
from database import init_db, DATABASE

# 初始化数据库
init_db()

# --- Discord Bot 部分 ---
intents = discord.Intents.default()
intents.message_content = True # 需要读取消息内容的权限
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.event
async def on_message(message):
    # 确保消息来自指定频道且不是机器人自己
    if message.channel.id == CHANNEL_ID and message.author != client.user:
        # 检查是否有附件
        if message.attachments:
            for attachment in message.attachments:
                # 检查是否为图片或视频 (可以根据需要扩展)
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.mp4', '.mov', '.avi', '.mkv']):
                    # 下载文件
                    file_path = os.path.join(MEDIA_FOLDER, attachment.filename)
                    try:
                        await attachment.save(file_path)
                        print(f"Downloaded {attachment.filename}")

                        # 保存到数据库
                        conn = sqlite3.connect(DATABASE)
                        cursor = conn.cursor()
                        # 构建可通过 Flask 访问的 URL
                        # 注意：生产环境应使用反向代理配置正确的 URL 前缀
                        local_url = f"http://{request.host if 'request' in globals() else 'localhost'}:{FLASK_PORT}/media/{attachment.filename}"
                        cursor.execute('''
                            INSERT OR IGNORE INTO media (filename, url, message_content)
                            VALUES (?, ?, ?)
                        ''', (attachment.filename, local_url, message.content))
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        print(f"Error saving {attachment.filename}: {e}")

# --- Flask API 部分 ---
app = Flask(__name__)
CORS(app) # 允许跨域请求，方便前端访问

@app.route('/media')
def list_media():
    """API 端点：获取媒体列表"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # 使结果可以通过列名访问
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM media ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()

    # 转换为字典列表
    media_list = [dict(row) for row in rows]
    return jsonify(media_list)

@app.route('/media/<filename>')
def serve_media(filename):
    """提供媒体文件"""
    return send_from_directory(MEDIA_FOLDER, filename)

@app.route('/')
def index():
    """Serve the frontend HTML file"""
    return send_from_directory('../frontend', 'index.html')

def run_flask():
    """在单独线程中运行 Flask"""
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, use_reloader=False)

if __name__ == '__main__':
    # 启动 Flask API
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # 启动 Discord Bot
    # 注意：直接运行 client.run() 会阻塞，这里使用 asyncio.run() 在主线程运行 bot
    # 并确保 Flask 在另一个线程中运行
    try:
        client.run(DISCORD_TOKEN)
    except Exception as e:
         print(f"Discord bot error: {e}")
    finally:
        # 如果 bot 停止，也应停止 Flask 线程 (可选)
        # 这里简单处理，实际可能需要更复杂的线程管理
        pass

```
