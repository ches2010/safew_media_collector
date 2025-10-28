#!/bin/bash
# 确保脚本在项目根目录执行
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR"

# 检查Python环境
if ! command -v python3 &>/dev/null; then
    echo "错误: 未找到python3，请先安装Python3"
    exit 1
fi

PYTHONPATH="$SCRIPT_DIR" python3 -m collector.collector

# 启动采集服务
echo "启动SafeW媒体采集服务..."
python3 -m collector.collector