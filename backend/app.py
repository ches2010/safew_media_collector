import os
import asyncio
import threading
import requests
from flask import Flask, render_template, send_from_directory, jsonify, request, abort
from flask_cors import CORS
from waitress import serve
import discord
from discord.ext import commands
from config import (
    DISCORD_BOT_TOKEN, DISCORD_CHANNEL_IDS, 
    MEDIA_FOLDER, FLASK_HOST, FLASK_PORT,
    validate_config, PROJECT_ROOT
)
import database

# 初始化 Flask 应用
app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'frontend'))
CORS(app)  # 允许跨域请求

# 初始化 Discord Bot
intents = discord.Intents.default()
intents.message_content = True  # 需要消息内容权限
bot = commands.Bot(command_prefix='!', intents=intents, description="SafeW Media Collector")

# 存储已处理的消息ID，避免重复处理
processed_messages = set()

# Flask 路由
@app.route('/')
def index():
    """提供前端页面"""
    return send_from_directory(os.path.join(PROJECT_ROOT, 'frontend'), 'index.html')

@app.route('/api/media')
def get_media():
    """API端点：获取媒体列表"""
    try:
        # 解析查询参数
        channel_id = request.args.get('channel_id', type=int)
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 验证参数
        limit = min(max(limit, 1), 100)  # 限制每页最多100条
        offset = max(offset, 0)
        
        # 获取媒体列表和总数
        media_list = database.get_all_media(channel_id, limit, offset)
        total = database.get_media_count(channel_id)
        
        return jsonify({
            'success': True,
            'media': media_list,
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'pages': (total + limit - 1) // limit
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/channels')
def get_channels():
    """API端点：获取所有有媒体的频道"""
    try:
        channels = database.get_distinct_channels()
        return jsonify({
            'success': True,
            'channels': channels
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/media/<filename>')
def serve_media(filename):
    """提供媒体文件访问"""
    # 安全检查：防止路径遍历攻击
    if '..' in filename or os.path.sep in filename:
        abort(403, description="无效的文件名")
    
    # 检查文件是否存在于数据库中
    conn = database.sqlite3.connect(database.DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM media WHERE filename = ?', (filename,))
    if not cursor.fetchone():
        conn.close()
        abort(404, description="媒体文件不存在")
    conn.close()
    
    # 检查文件是否实际存在
    file_path = os.path.join(MEDIA_FOLDER, filename)
    if not os.path.exists(file_path):
        abort(404, description="媒体文件已丢失")
    
    return send_from_directory(MEDIA_FOLDER, filename)

@app.route('/api/media/<filename>', methods=['DELETE'])
def delete_media(filename):
    """API端点：删除媒体文件"""
    try:
        # 安全检查
        if '..' in filename or os.path.sep in filename:
            abort(403, description="无效的文件名")
        
        # 从数据库删除记录
        db_deleted = database.delete_media(filename)
        
        # 删除实际文件
        file_path = os.path.join(MEDIA_FOLDER, filename)
        file_deleted = False
        if os.path.exists(file_path):
            os.remove(file_path)
            file_deleted = True
        
        return jsonify({
            'success': db_deleted or file_deleted,
            'database': db_deleted,
            'file': file_deleted
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Discord Bot 事件
@bot.event
async def on_ready():
    """Bot 准备就绪时调用"""
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    
    # 验证是否有权访问指定频道
    for channel_id in DISCORD_CHANNEL_IDS:
        try:
            channel = bot.get_channel(channel_id) or await bot.fetch_channel(channel_id)
            print(f"已连接到频道: {channel.name} (ID: {channel.id})")
        except Exception as e:
            print(f"无法访问频道 ID {channel_id}: {e}")

@bot.event
async def on_message(message):
    """处理新消息"""
    # 忽略机器人自己的消息
    if message.author.bot:
        return
    
    # 只处理指定频道的消息
    if message.channel.id not in DISCORD_CHANNEL_IDS:
        return
    
    # 避免重复处理消息
    if message.id in processed_messages:
        return
    processed_messages.add(message.id)
    
    # 限制已处理消息的内存占用
    if len(processed_messages) > 10000:
        processed_messages.pop()
    
    # 检查消息是否有附件
    if message.attachments:
        print(f"在频道 {message.channel.id} 发现 {len(message.attachments)} 个附件")
        
        for attachment in message.attachments:
            # 只处理图片和视频
            if any(attachment.filename.lower().endswith(ext) for ext in [
                '.jpg', '.jpeg', '.png', '.gif', '.webp',  # 图片
                '.mp4', '.mov', '.webm', '.avi', '.mkv'    # 视频
            ]):
                try:
                    # 下载附件
                    await download_attachment(attachment, message)
                except Exception as e:
                    print(f"下载附件 {attachment.filename} 时出错: {e}")
    
    # 继续处理命令（如果有）
    await bot.process_commands(message)

async def download_attachment(attachment, message):
    """下载附件并保存到媒体文件夹"""
    # 生成保存路径
    filename = f"{message.id}_{attachment.filename}"
    file_path = os.path.join(MEDIA_FOLDER, filename)
    
    # 检查文件是否已存在
    if os.path.exists(file_path):
        print(f"文件 {filename} 已存在，跳过下载")
        return
    
    # 下载文件
    print(f"下载 {attachment.filename} 到 {file_path}")
    
    # 使用discord.py的方法下载
    await attachment.save(file_path)
    
    # 将信息存入数据库
    database.add_media(
        filename=filename,
        url=attachment.url,
        timestamp=message.created_at.isoformat(),
        message_content=message.content,
        channel_id=message.channel.id
    )

# 运行 Flask 服务
def run_flask():
    """运行 Flask 服务"""
    print(f"Flask 服务将在 http://{FLASK_HOST}:{FLASK_PORT} 启动")
    # 生产环境使用 waitress 作为 WSGI 服务器
    serve(app, host=FLASK_HOST, port=FLASK_PORT)

# 主函数
async def main():
    """主函数：同时运行 Bot 和 Flask 服务"""
    # 初始化数据库
    database.init_db()
    
    # 在单独的线程中运行 Flask
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # 运行 Discord Bot
    await bot.start(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    try:
        # 验证配置
        validate_config()
        
        # 运行主函数
        asyncio.run(main())
    except Exception as e:
        print(f"启动失败: {e}")
        exit(1)
