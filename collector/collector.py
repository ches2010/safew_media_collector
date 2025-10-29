import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from config import TARGET_CHANNEL_ID, REFRESH_INTERVAL, BOT_TOKEN
from .api_client import SafewApiClient
from .media_downloader import MediaDownloader
from utils.logger import get_logger
from datetime import datetime
from utils.state_manager import load_last_message_id, save_last_message_id
import time
import signal


logger = get_logger(__name__)

class MediaCollector:
    def __init__(self):
        self.api_client = SafewApiClient()
        self.downloader = MediaDownloader(self.api_client)
        self.last_update_id = load_last_message_id()  # 重命名变量，明确是update_id而非message_id
        self.running = False
        
        # 初始化调度器
        self.scheduler = BackgroundScheduler(
            executors={
                'default': ThreadPoolExecutor(5)
            },
            job_defaults={
                'coalesce': False,
                'max_instances': 1
            }
        )

    def start(self):
        self.running = True
        self.scheduler.add_job(
            self.collect_media,
            'interval',
            seconds=REFRESH_INTERVAL,
            id='media_collect_job',
            next_run_time=datetime.now()
        )
        self.scheduler.start()
        logger.info(f"采集服务已启动，目标频道: {TARGET_CHANNEL_ID}，间隔: {REFRESH_INTERVAL}秒")

        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        try:
            while self.running:
                time.sleep(1)
        finally:
            self.scheduler.shutdown()

    def collect_media(self):
        try:
            logger.info(f"开始采集（最后处理的update_id: {self.last_update_id}）")
            
            # 1. 获取频道更新（修正参数传递方式，明确allowed_updates为JSON字符串）
            updates = self.api_client.get_channel_messages(
                offset=self.last_update_id + 1,
                limit=100,
                allowed_updates=json.dumps(["message"])  # API要求JSON格式的字符串
            )
            
            if not updates:
                logger.info("没有新消息可采集")
                return
            
            # 2. 打印调试日志（查看原始消息结构，便于排查）
            logger.debug(f"获取到{len(updates)}条更新，内容: {json.dumps(updates, ensure_ascii=False)}")
            
            # 3. 解析并下载媒体（包含媒体组消息）
            media = self.downloader.parse_media_from_messages(updates)
            logger.info(f"采集完成：{len(media['photos'])}张图片，{len(media['videos'])}个视频")
            
            # 4. 更新最后处理的update_id（而非message_id）
            latest_update_id = max(update.get('update_id', 0) for update in updates)
            if latest_update_id > self.last_update_id:
                self.last_update_id = latest_update_id
                save_last_message_id(self.last_update_id)  # 保持与状态文件兼容
                logger.info(f"已更新最后处理的update_id: {self.last_update_id}")
                
        except Exception as e:
            logger.error(f"采集任务失败: {str(e)}", exc_info=True)

    def _shutdown(self, signum, frame):
        logger.info(f"接收到关闭信号 {signum}，正在退出...")
        self.running = False
        self.scheduler.shutdown(wait=False)
        sys.exit(0)

if __name__ == "__main__":
    collector = MediaCollector()
    collector.start()