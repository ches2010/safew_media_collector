from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from config import TARGET_CHANNEL_ID, REFRESH_INTERVAL
from .api_client import SafewApiClient
from .media_downloader import MediaDownloader
from utils.logger import get_logger
from utils.state_manager import load_last_message_id, save_last_message_id
import time
import signal
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

logger = get_logger(__name__)

class MediaCollector:
    def __init__(self):
        self.api_client = SafewApiClient()
        self.downloader = MediaDownloader(self.api_client)
        self.last_message_id = load_last_message_id()
        self.running = False
        
        # 初始化调度器（使用线程池）
        self.scheduler = BackgroundScheduler(
            executors={
                'default': ThreadPoolExecutor(5)
            },
            job_defaults={
                'coalesce': False,  # 不合并错过的任务
                'max_instances': 1  # 最大实例数
            }
        )

    def start(self):
        """启动采集服务"""
        self.running = True
        # 添加定时任务
        self.scheduler.add_job(
            self.collect_media,
            'interval',
            seconds=REFRESH_INTERVAL,
            id='media_collect_job',
            next_run_time=time.time()  # 立即执行一次
        )
        self.scheduler.start()
        logger.info(f"采集服务已启动，目标频道: {TARGET_CHANNEL_ID}，间隔: {REFRESH_INTERVAL}秒")

        # 注册信号处理（优雅退出）
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        # 保持进程运行
        try:
            while self.running:
                time.sleep(1)
        finally:
            self.scheduler.shutdown()

    def collect_media(self):
        """执行媒体采集"""
        try:
            logger.info(f"开始采集（最后处理的消息ID: {self.last_message_id}）")
            
            # 获取新消息（从上次最后一条消息之后开始）
            messages = self.api_client.get_channel_messages(
                chat_id=TARGET_CHANNEL_ID,
                offset=self.last_message_id + 1,
                limit=100
            )
            
            if not messages:
                logger.info("没有新消息可采集")
                return
            
            # 解析并下载媒体
            media = self.downloader.parse_media_from_messages(messages)
            logger.info(f"采集完成：{len(media['photos'])}张图片，{len(media['videos'])}个视频")
            
            # 更新最后处理的消息ID
            latest_id = max(msg.get('update_id', 0) for msg in messages)
            if latest_id > self.last_message_id:
                self.last_message_id = latest_id
                save_last_message_id(self.last_message_id)
                logger.info(f"已更新最后处理的消息ID: {self.last_message_id}")
                
        except Exception as e:
            logger.error(f"采集任务失败: {str(e)}", exc_info=True)

    def _shutdown(self, signum, frame):
        """优雅关闭服务"""
        logger.info(f"接收到关闭信号 {signum}，正在退出...")
        self.running = False
        self.scheduler.shutdown(wait=False)
        sys.exit(0)

if __name__ == "__main__":
    collector = MediaCollector()
    collector.start()