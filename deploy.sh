#!/bin/bash

set -e # 遇到错误时退出

# --- 配置 ---
PROJECT_NAME="safew_media_collector"
PROJECT_DIR=$(pwd) # 假设脚本在项目根目录运行
BACKEND_DIR="$PROJECT_DIR/backend"
SERVICE_NAME="${PROJECT_NAME}.service"
SERVICE_TEMPLATE="$PROJECT_DIR/${SERVICE_NAME}.template"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
VENV_DIR="$BACKEND_DIR/venv"
ENV_FILE="$PROJECT_DIR/.env"

# 默认服务用户和组 (可以修改或通过参数传入)
DEFAULT_SERVICE_USER="safew_collector"
DEFAULT_SERVICE_GROUP="safew_collector"

# --- 函数 ---

check_root() {
    if [[ $EUID -ne 0 ]]; then
       echo "此脚本需要 root 权限运行。请使用 sudo。" 1>&2
       exit 1
    fi
}

check_dependencies() {
    echo "检查依赖..."
    if ! command -v python3 &> /dev/null; then
        echo "错误: 未找到 python3。请先安装。"
        exit 1
    fi
    if ! command -v pip3 &> /dev/null; then
        echo "错误: 未找到 pip3。请先安装。"
        exit 1
    fi
    if ! command -v systemctl &> /dev/null; then
        echo "错误: 未找到 systemctl。此脚本需要 systemd。"
        exit 1
    fi
    echo "依赖检查通过。"
}

create_service_user() {
    local user=$1
    local group=$2
    echo "创建服务用户和组: $user:$group"
    if ! getent group "$group" > /dev/null 2>&1; then
        groupadd "$group"
        echo "已创建组: $group"
    else
        echo "组 $group 已存在。"
    fi

    if ! id "$user" &>/dev/null; then
        useradd -r -s /bin/false -g "$group" "$user"
        echo "已创建用户: $user"
    else
        echo "用户 $user 已存在。"
    fi
}

setup_directories() {
    echo "设置目录权限..."
    # 确保 media 目录存在并设置权限
    mkdir -p "$BACKEND_DIR/media"
    chown -R "$DEFAULT_SERVICE_USER:$DEFAULT_SERVICE_GROUP" "$BACKEND_DIR/media"
    chmod -R 755 "$BACKEND_DIR/media"
    
    # 设置整个项目目录的所有者 (可选，但推荐)
    # chown -R "$DEFAULT_SERVICE_USER:$DEFAULT_SERVICE_GROUP" "$PROJECT_DIR"
    # 注意：如果这样做，运行此脚本的用户可能需要临时权限，或者脚本需要调整。
    # 为简化，我们只确保 media 目录可写。
}

install_python_packages() {
    echo "安装 Python 依赖..."
    if [ ! -d "$VENV_DIR" ]; then
        echo "创建虚拟环境..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # 激活虚拟环境并安装依赖
    # 使用 source 可能不适用于所有 shell，直接调用 activate 脚本
    # source "$VENV_DIR/bin/activate"
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
    echo "Python 依赖安装完成。"
}

check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        echo "错误: 未找到 .env 文件。"
        echo "请复制 .env.example 为 .env 并填入你的 Discord Bot Token 和 Channel ID。"
        echo "示例: cp .env.example .env"
        echo "      nano .env"
        exit 1
    fi
    # 简单检查关键变量是否设置 (不检查值是否有效)
    if ! grep -q "^DISCORD_BOT_TOKEN=" "$ENV_FILE" || grep -q "^DISCORD_BOT_TOKEN=$" "$ENV_FILE" ; then
         echo "错误: .env 文件中未设置 DISCORD_BOT_TOKEN 或其值为空。"
         exit 1
    fi
    if ! grep -q "^DISCORD_CHANNEL_ID=" "$ENV_FILE" || grep -q "^DISCORD_CHANNEL_ID=$" "$ENV_FILE" ; then
         echo "错误: .env 文件中未设置 DISCORD_CHANNEL_ID 或其值为空。"
         exit 1
    fi
    echo ".env 文件检查通过。"
}

configure_service() {
    echo "配置 systemd 服务..."
    if [ ! -f "$SERVICE_TEMPLATE" ]; then
        echo "错误: 未找到服务模板文件 $SERVICE_TEMPLATE"
        exit 1
    fi

    # 获取 Python 可执行文件路径 (在虚拟环境中)
    PYTHON_EXEC="$VENV_DIR/bin/python"

    # 替换模板中的占位符
    # 使用 sed 进行替换，注意转义斜杠
    sed -e "s|{{PYTHON_EXEC}}|$PYTHON_EXEC|g" \
        -e "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" \
        -e "s|{{SERVICE_USER}}|$DEFAULT_SERVICE_USER|g" \
        -e "s|{{SERVICE_GROUP}}|$DEFAULT_SERVICE_GROUP|g" \
        "$SERVICE_TEMPLATE" > "$SERVICE_FILE"

    echo "服务文件已创建: $SERVICE_FILE"
}

start_service() {
    echo "启动并启用服务..."
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    systemctl restart "$SERVICE_NAME" # restart 可以处理服务已启动或未启动的情况
    echo "服务 $SERVICE_NAME 已启动并设置为开机自启。"
    echo "使用 'sudo systemctl status $SERVICE_NAME' 检查状态。"
    echo "使用 'sudo journalctl -u $SERVICE_NAME -f' 查看实时日志。"
}

final_message() {
    local ip_address=$(hostname -I | awk '{print $1}')
    echo "-----------------------------------------"
    echo "部署完成!"
    echo "1. 确保你的 .env 文件配置正确。"
    echo "2. 确保 Discord Bot 已添加到服务器并有相应权限。"
    echo "3. 前端页面可通过 http://$ip_address:5000 访问。"
    echo "4. 查看服务状态: sudo systemctl status $SERVICE_NAME"
    echo "5. 查看服务日志: sudo journalctl -u $SERVICE_NAME -f"
    echo "-----------------------------------------"
}


# --- 主逻辑 ---

echo "开始部署 $PROJECT_NAME..."

check_root
check_dependencies
check_env_file # 检查必须在创建用户之前，因为需要读取 .env
create_service_user "$DEFAULT_SERVICE_USER" "$DEFAULT_SERVICE_GROUP"
setup_directories
install_python_packages
configure_service
start_service
final_message

echo "部署脚本执行完毕。"
