# safew_media_collector

SafeW频道媒体采集工具，用于自动采集指定SafeW频道的图片和视频，并在Web页面上分开展示（图片采用瀑布流布局）。

## 功能特点
- 定时自动采集频道媒体（图片/视频）
- 自动保存媒体附带的文本信息（说明文字、发布时间等）
- 图片采用响应式瀑布流展示
- 视频支持在线播放
- 自动去重功能（基于文件哈希）
- 完整的日志记录

## 环境要求
- Python 3.6+
- Ubuntu Server（推荐）
- 网络连接（需能访问SafeW API）

## 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/ches2010/safew_media_collector.git
cd safew_media_collector
```

2. 安装依赖
```bash
pip3 install -r requirements.txt
```

3. 配置参数
编辑`config.py`文件，设置以下关键参数：
```python
BOT_TOKEN = "your_bot_token_here"  # 从@BotFather获取
TARGET_CHANNEL_ID = "@channelusername"  # 目标频道ID
```

4. 初始化存储目录
```bash
sudo mkdir -p /var/www/safew_media/{photos,videos,metadata}
sudo chown -R $USER:$USER /var/www/safew_media
```

## 启动服务

1. 启动采集服务
```bash
bash run_collector.sh
```

2. 启动Web服务（新终端）
```bash
python3 -m server.app
```

3. 访问页面
打开浏览器访问 `http://服务器IP:8080` 即可查看采集的媒体内容

## 自动启动配置
可通过systemd设置开机自启动：
```bash
# 创建服务文件
sudo nano /etc/systemd/system/safew-collector.service
```

# 内容如下
```
[Unit]
Description=SafeW Media Collector
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/safew_media_collector
ExecStart=/usr/bin/python3 -m collector.collector
Restart=always

[Install]
WantedBy=multi-user.target
```

# 启用并启动服务
```bash
sudo systemctl enable safew-collector
sudo systemctl start safew-collector
```

## 项目结构
- `collector/`：媒体采集相关模块
- `server/`：Web展示相关模块
- `utils/`：通用工具函数
- `config.py`：配置文件


## 注意事项
使用前需替换`config.py`中的`BOT_TOKEN`和`TARGET_CHANNEL_ID`为实际值。