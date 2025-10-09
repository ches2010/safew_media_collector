#!/bin/bash

# 配置
PROJECT_NAME="safew_media_collector"
BACKEND_DIR="./backend"
ENV_FILE=".env"
SERVICE_TEMPLATE="safew_media_collector.service.template"
SERVICE_FILE="/etc/systemd/system/${PROJECT_NAME}.service"
DEFAULT_SERVICE_USER="www-data"
DEFAULT_SERVICE_GROUP="www-data"

echo "🚀 开始一键部署SafeW采集服务..."


# 检查是否以root权限运行
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo -e "${RED}错误: 此脚本需要以root权限运行。请使用sudo ./deploy.sh${NC}"
        exit 1
    fi
}

# 检查.env文件是否存在且配置正确
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}错误: 未找到 .env 文件。${NC}"
        echo "请复制 .env.example 为 .env 并填入你的 Discord Bot Token 和 Channel ID。"
        echo "示例: cp .env.example .env"
        echo "      nano .env"
        exit 1
    fi
    
    # 检查是否设置了Discord Bot Token
    if ! grep -q "^DISCORD_BOT_TOKEN=" "$ENV_FILE" || grep -q "^DISCORD_BOT_TOKEN=$" "$ENV_FILE"; then
        echo -e "${RED}错误: .env 文件中未设置 DISCORD_BOT_TOKEN 或其值为空。${NC}"
        exit 1
    fi
    
    # 同时支持多频道(DISCORD_CHANNEL_IDS)和单频道(DISCORD_CHANNEL_ID)配置
    if ! (grep -q "^DISCORD_CHANNEL_IDS=" "$ENV_FILE" && ! grep -q "^DISCORD_CHANNEL_IDS=$" "$ENV_FILE") && \
       ! (grep -q "^DISCORD_CHANNEL_ID=" "$ENV_FILE" && ! grep -q "^DISCORD_CHANNEL_ID=$" "$ENV_FILE"); then
         echo -e "${RED}错误: .env 文件中未设置 DISCORD_CHANNEL_IDS 或 DISCORD_CHANNEL_ID 或其值为空。${NC}"
         exit 1
    fi
    
    echo -e "${GREEN}.env 文件检查通过。${NC}"
}

# 安装系统依赖
install_system_dependencies() {
    echo "安装系统依赖..."
    apt update -qq
    apt install -qq -y python3 python3-pip python3-venv python3-dev build-essential
    echo -e "${GREEN}系统依赖安装完成。${NC}"
}

# 设置目录和权限
setup_directories() {
    echo "设置目录权限..."
    # 确保 media 目录存在并设置严格权限
    mkdir -p "$BACKEND_DIR/media"
    chown -R "$DEFAULT_SERVICE_USER:$DEFAULT_SERVICE_GROUP" "$BACKEND_DIR/media"
    chmod -R 700 "$BACKEND_DIR/media"  # 仅所有者可读写执行
    
    # 保护 .env 文件
    chmod 600 "$ENV_FILE"
    chown "$DEFAULT_SERVICE_USER:$DEFAULT_SERVICE_GROUP" "$ENV_FILE"
    
    echo -e "${GREEN}目录权限设置完成。${NC}"
}

# 创建并配置虚拟环境
setup_venv() {
    echo "创建虚拟环境..."
    cd "$BACKEND_DIR" || exit 1
    
    # 如果虚拟环境已存在，则删除并重新创建
    if [ -d "venv" ]; then
        echo "检测到现有虚拟环境，正在重新创建..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    
    # 安装Python依赖
    echo "安装Python依赖..."
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    
    deactivate
    cd - || exit 1
    echo -e "${GREEN}虚拟环境配置完成。${NC}"
}


# 6. 启动服务（前台运行）
echo "✅ 部署完成！正在启动服务..."
echo "🌐 访问地址: http://0.0.0.0:5689"
echo "🛑 按 Ctrl+C 停止服务"
"python" "$BACKEND_DIR/app.py"
