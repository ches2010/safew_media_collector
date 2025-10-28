import json
import os
from pathlib import Path

# 状态文件存储路径（项目根目录）
STATE_FILE = Path(__file__).parent.parent / "collector_state.json"

def load_last_message_id():
    """从文件加载最后采集的消息ID"""
    if os.path.exists(STATE_FILE) and os.path.getsize(STATE_FILE) > 0:
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                return state.get('last_message_id', 0)
        except (json.JSONDecodeError, KeyError):
            # 状态文件损坏时重置
            return 0
    return 0

def save_last_message_id(message_id):
    """保存最后采集的消息ID到文件"""
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'last_message_id': message_id}, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"保存状态失败: {str(e)}")