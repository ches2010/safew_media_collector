import os
from dotenv import load_dotenv # 如果使用 python-dotenv

# 加载 .env 文件 (如果使用)
# load_dotenv()

# Discord Bot Token (从环境变量获取，不要硬编码在代码中)
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
# 监听的频道 ID
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID')) # 确保是整数

# Flask 配置
FLASK_HOST = '0.0.0.0' # 监听所有接口，以便外部访问
FLASK_PORT = 9890

# 文件存储路径
MEDIA_FOLDER = 'media'
