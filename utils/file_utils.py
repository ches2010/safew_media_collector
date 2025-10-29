import os
import hashlib
import json
from pathlib import Path

def get_existing_files(storage_path):
    """获取已存在的文件ID列表（从文件名中提取）"""
    existing = set()
    if not os.path.exists(storage_path):
        return existing
        
    for filename in os.listdir(storage_path):
        # 文件名格式: message_id_file_id.ext
        parts = filename.split('_')
        if len(parts) >= 2:
            file_id = parts[1].rsplit('.', 1)[0]  # 移除扩展名
            existing.add(file_id)
    return existing

# 在MediaDownloader中使用
def parse_media_from_messages(self, updates):
    # 获取已存在的文件ID，避免重复下载
    existing_photos = get_existing_files(PHOTO_STORAGE_PATH)
    existing_videos = get_existing_files(VIDEO_STORAGE_PATH)
    
    # ...省略其他代码...
    # 处理图片时检查
    if highest_quality["file_id"] not in existing_photos:
        # 执行下载
    # 处理视频时检查
    if msg["video"]["file_id"] not in existing_videos:
        # 执行下载

def create_directory(path):
    """创建目录（如果不存在）"""
    Path(path).mkdir(parents=True, exist_ok=True)

def get_file_hash(file_path, block_size=65536):
    """计算文件哈希值（用于去重）"""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read(block_size)
        while buf:
            hasher.update(buf)
            buf = f.read(block_size)
    return hasher.hexdigest()

def is_file_duplicate(file_path, hash_store):
    """检查文件是否重复"""
    file_hash = get_file_hash(file_path)
    if file_hash in hash_store:
        return True
    hash_store.add(file_hash)
    return False

def save_json(data, file_path):
    """保存数据到JSON文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"保存JSON失败 {file_path}: {str(e)}")
        return False

def load_json(file_path):
    """从JSON文件加载数据"""
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"加载JSON失败 {file_path}: {str(e)}")
        return None