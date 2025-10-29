import os
import requests
from config import PHOTO_STORAGE_PATH, VIDEO_STORAGE_PATH, METADATA_STORAGE_PATH
from utils.file_utils import create_directory, is_file_duplicate, save_json
from utils.logger import get_logger

logger = get_logger(__name__)

class MediaDownloader:
    def __init__(self, api_client):
        self.api_client = api_client
        self.photo_path = PHOTO_STORAGE_PATH
        self.video_path = VIDEO_STORAGE_PATH
        self.metadata_path = METADATA_STORAGE_PATH
        self.photo_hashes = self._load_existing_hashes(self.photo_path)
        self.video_hashes = self._load_existing_hashes(self.video_path)
        
        # 确保存储目录存在
        create_directory(self.photo_path)
        create_directory(self.video_path)
        create_directory(self.metadata_path)

    def _get_file_url(self, file_id):
    """获取文件的下载URL（根据API规范实现）"""
    file_info = SafewApiClient().get_file(file_id)
    # 构建完整下载URL
    return f"https://api.safew.org/file/bot{BOT_TOKEN}/{file_info['file_path']}"

    def _load_existing_hashes(self, directory):
        """加载已存在文件的哈希值（用于去重）"""
        hashes = set()
        if not os.path.exists(directory):
            return hashes
            
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    from utils.file_utils import get_file_hash
                    hashes.add(get_file_hash(file_path))
                except Exception as e:
                    logger.warning(f"计算文件哈希失败 {filename}: {str(e)}")
        return hashes

    def download_media(self, file_id, is_photo=True):
        """下载媒体文件（通用方法）"""
        # 获取文件信息
        file_info = self.api_client.get_file_info(file_id)
        if not file_info or "file_path" not in file_info:
            logger.error(f"无法获取文件信息 file_id={file_id}")
            return None

        # 获取下载链接
        file_url = self.api_client.get_file_download_url(file_info["file_path"])
        storage_path = self.photo_path if is_photo else self.video_path
        hash_store = self.photo_hashes if is_photo else self.video_hashes

        # 生成文件名（保留原始扩展名）
        ext = os.path.splitext(file_info["file_path"])[1] or (".jpg" if is_photo else ".mp4")
        filename = f"{file_id}{ext}"
        file_path = os.path.join(storage_path, filename)

        # 下载文件
        try:
            with requests.get(file_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                # 先下载到临时文件
                temp_path = f"{file_path}.tmp"
                with open(temp_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

                # 检查重复
                if is_file_duplicate(temp_path, hash_store):
                    os.remove(temp_path)
                    logger.info(f"重复文件，已跳过 {filename}")
                    return None

                # 重命名为正式文件
                os.rename(temp_path, file_path)
                logger.info(f"下载成功 {filename}")
                return file_path

        except Exception as e:
            logger.error(f"下载失败 {filename}: {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None

    def save_media_metadata(self, file_id, metadata, is_photo=True):
        """保存媒体的元数据（文本信息）"""
        metadata_path = os.path.join(self.metadata_path, f"{file_id}.json")
        # 补充基础元数据
        metadata['file_id'] = file_id
        metadata['media_type'] = 'photo' if is_photo else 'video'
        metadata['storage_path'] = self.photo_path if is_photo else self.video_path
        return save_json(metadata, metadata_path)

    def parse_media_from_messages(self, messages):
        """从消息列表中解析并下载媒体"""
        media_list = {"photos": [], "videos": []}
        media_groups = {}  # 临时存储媒体组消息

        for update in updates:
            # 检查是否包含消息对象
            if "message" not in update:
                continue
            msg = update["message"]
            
            # 提取通用消息信息
            message_info = {
                "message_id": msg.get("message_id", ""),
                "date": msg.get("date", ""),  # 时间戳
                "caption": msg.get("caption", ""),  # 媒体说明文字
                "caption_entities": msg.get("caption_entities", [])  # 说明文字中的实体（如链接）
            }
            
            # 处理媒体组（可能包含多张图片）
            media_group_id = msg.get("media_group_id")
            if media_group_id:
                if media_group_id not in media_groups:
                    media_groups[media_group_id] = []
                media_groups[media_group_id].append(msg)

            # 处理单张图片
            if "photo" in msg and msg["photo"]:
                self._process_photo(msg, message_info, media_list)
        
            # 处理单个视频
            if "video" in msg:
                self._process_video(msg, message_info, media_list)
        # 处理媒体组中的所有媒体
        for group in media_groups.values():
            for msg in group:
                message_info = {
                    "message_id": msg.get("message_id", ""),
                    "date": msg.get("date", ""),
                    "caption": msg.get("caption", ""),
                    "media_group_id": msg.get("media_group_id")
                }
                if "photo" in msg:
                    self._process_photo(msg, message_info, media_list)
                if "video" in msg:
                    self._process_video(msg, message_info, media_list)
    
    return media_list

    def _process_photo(self, msg, message_info, media_list):
        """单独提取图片处理逻辑，确保正确下载"""
        best_photo = max(msg["photo"], key=lambda x: x.get("file_size", 0))
        file_path = self.download_media(best_photo["file_id"], is_photo=True)
        if file_path:
            self.save_media_metadata(
                best_photo["file_id"],
                {** message_info, "photo_sizes": msg["photo"]},
                is_photo=True
            )
            media_list["photos"].append(file_path)

    def _process_video(self, msg, message_info, media_list):
        """单独提取视频处理逻辑"""
        video_info = msg["video"]
        file_path = self.download_media(video_info["file_id"], is_photo=False)
        if file_path:
            self.save_media_metadata(
                video_info["file_id"],
                {**message_info,
                 "duration": video_info.get("duration", 0),
                 "width": video_info.get("width", 0),
                 "height": video_info.get("height", 0)},
                is_photo=False
            )
            media_list["videos"].append(file_path)
