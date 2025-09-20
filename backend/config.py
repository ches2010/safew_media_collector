# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Discord Bot Token (必需)
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("环境变量 DISCORD_BOT_TOKEN 未设置")

# Discord Channel ID(s) (支持单个或多个)
# 优先使用 DISCORD_CHANNEL_IDS (多频道), 如果没有则回退到 DISCORD_CHANNEL_ID (单频道)
CHANNEL_IDS_STR = os.getenv("DISCORD_CHANNEL_IDS")
if CHANNEL_IDS_STR:
    # 分割字符串，去除空格，并转换为整数列表
    try:
        DISCORD_CHANNEL_IDS = [int(cid.strip()) for cid in CHANNEL_IDS_STR.split(',') if cid.strip()]
        if not DISCORD_CHANNEL_IDS:
             raise ValueError("DISCORD_CHANNEL_IDS 解析后为空列表")
    except ValueError as e:
        raise ValueError(f"环境变量 DISCORD_CHANNEL_IDS 格式错误: {e}")
else:
    # 回退到单个频道 ID
    LEGACY_CHANNEL_ID_STR = os.getenv("DISCORD_CHANNEL_ID")
    if LEGACY_CHANNEL_ID_STR:
        try:
            DISCORD_CHANNEL_IDS = [int(LEGACY_CHANNEL_ID_STR)]
        except ValueError:
            raise ValueError("环境变量 DISCORD_CHANNEL_ID 格式错误，应为纯数字")
    else:
        raise ValueError("环境变量 DISCORD_CHANNEL_IDS 或 DISCORD_CHANNEL_ID 至少需要设置一个")

# Flask 配置
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

# 媒体文件存储目录
MEDIA_FOLDER = os.path.join(os.path.dirname(__file__), 'media')
os.makedirs(MEDIA_FOLDER, exist_ok=True) # 确保目录存在
