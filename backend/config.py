import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()  # 从项目根目录的 .env 文件加载变量

# 项目根目录（backend的上级目录）
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 媒体文件存储目录
MEDIA_FOLDER = os.path.join(os.path.dirname(__file__), 'media')
os.makedirs(MEDIA_FOLDER, exist_ok=True)  # 确保目录存在

# 数据库路径
DATABASE = os.path.join(MEDIA_FOLDER, 'media.db')

# Discord 配置
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# 处理频道ID - 支持多个频道（逗号分隔）或单个频道
channel_ids_str = os.getenv('DISCORD_CHANNEL_IDS', '')
if not channel_ids_str:
    # 兼容旧版配置
    channel_ids_str = os.getenv('DISCORD_CHANNEL_ID', '')

DISCORD_CHANNEL_IDS = [
    int(id.strip()) for id in channel_ids_str.split(',') 
    if id.strip().isdigit()
]

# Flask 配置
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

# 验证必要的配置
def validate_config():
    if not DISCORD_BOT_TOKEN:
        raise ValueError("DISCORD_BOT_TOKEN 未在 .env 文件中设置")
    
    if not DISCORD_CHANNEL_IDS:
        raise ValueError("DISCORD_CHANNEL_IDS 或 DISCORD_CHANNEL_ID 未在 .env 文件中正确设置")
    
    return True
