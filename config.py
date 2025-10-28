# 基础配置
SAFEW_API_URL = "https://api.safew.org"
BOT_TOKEN = "your_bot_token_here"  # 从@BotFather获取的令牌
TARGET_CHANNEL_ID = "@channelusername"  # 目标频道ID（格式@channelusername）

# 存储配置
MEDIA_STORAGE_PATH = "/var/www/safew_media"  # Ubuntu服务器存储路径
PHOTO_STORAGE_PATH = f"{MEDIA_STORAGE_PATH}/photos"
VIDEO_STORAGE_PATH = f"{MEDIA_STORAGE_PATH}/videos"
METADATA_STORAGE_PATH = f"{MEDIA_STORAGE_PATH}/metadata"  # 元数据存储目录

# 服务器配置
WEB_SERVER_PORT = 8080
REFRESH_INTERVAL = 3600  # 采集间隔（秒）