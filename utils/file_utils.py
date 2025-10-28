import os
import hashlib
import json
from pathlib import Path

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