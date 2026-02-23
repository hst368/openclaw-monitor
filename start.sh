#!/bin/bash
# OpenClaw Monitor 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查依赖
check_dependencies() {
    python3 -c "import flask, psutil, requests" 2>/dev/null || {
        echo "依赖未安装，正在安装..."
        python3 -m pip install -r requirements.txt --user --break-system-packages 2>/dev/null || \
        python3 -m pip install -r requirements.txt --user
    }
}

check_dependencies

# 启动
echo "启动 OpenClaw Monitor..."
python3 app.py "$@"
