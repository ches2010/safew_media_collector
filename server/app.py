from flask import Flask, render_template, jsonify, send_from_directory
import os
from config import (
    PHOTO_STORAGE_PATH, 
    VIDEO_STORAGE_PATH, 
    WEB_SERVER_PORT,
    METADATA_STORAGE_PATH
)
from utils.logger import get_logger
from utils.file_utils import load_json

logger = get_logger(__name__)
app = Flask(__name__)

# 配置媒体文件访问路径
@app.route('/media/photos/<path:filename>')
def serve_photo(filename):
    return send_from_directory(PHOTO_STORAGE_PATH, filename)

@app.route('/media/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_STORAGE_PATH, filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/photos')
def photos_page():
    return render_template('photos.html')

@app.route('/videos')
def videos_page():
    return render_template('videos.html')

@app.route('/api/metadata/<file_id>')
def get_metadata(file_id):
    """根据file_id获取媒体元数据"""
    metadata_path = os.path.join(METADATA_STORAGE_PATH, f"{file_id}.json")
    metadata = load_json(metadata_path)
    if metadata:
        return jsonify(metadata)
    return jsonify({"error": "元数据不存在"}), 404

@app.route('/api/photos')
def get_photos():
    """获取所有图片文件名（按修改时间排序）"""
    try:
        if not os.path.exists(PHOTO_STORAGE_PATH):
            return jsonify([])
        
        files = []
        for filename in os.listdir(PHOTO_STORAGE_PATH):
            file_path = os.path.join(PHOTO_STORAGE_PATH, filename)
            if os.path.isfile(file_path):
                # 从文件名提取file_id（文件名格式：{file_id}.ext）
                file_id = os.path.splitext(filename)[0]
                files.append({
                    "filename": filename,
                    "file_id": file_id,
                    "mtime": os.path.getmtime(file_path)
                })
        
        # 按修改时间排序
        files.sort(key=lambda x: x["mtime"], reverse=True)
        return jsonify(files)
    except Exception as e:
        logger.error(f"获取图片列表失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/videos')
def get_videos():
    """获取所有视频文件名（按修改时间排序）"""
    try:
        if not os.path.exists(VIDEO_STORAGE_PATH):
            return jsonify([])
        
        files = []
        for filename in os.listdir(VIDEO_STORAGE_PATH):
            file_path = os.path.join(VIDEO_STORAGE_PATH, filename)
            if os.path.isfile(file_path):
                file_id = os.path.splitext(filename)[0]
                files.append({
                    "filename": filename,
                    "file_id": file_id,
                    "mtime": os.path.getmtime(file_path)
                })
        
        # 按修改时间排序
        files.sort(key=lambda x: x["mtime"], reverse=True)
        return jsonify(files)
    except Exception as e:
        logger.error(f"获取视频列表失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=WEB_SERVER_PORT, debug=False)