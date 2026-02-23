#!/bin/bash
# OpenClaw Monitor - 安装脚本

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         OpenClaw Monitor 安装程序                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 版本
echo "→ 检查 Python 版本..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "  ✓ Python 版本: $PYTHON_VERSION"
else
    echo "${RED}✗ 未找到 Python3${NC}"
    echo "  请安装 Python 3.8 或更高版本"
    exit 1
fi

# 安装目录
INSTALL_DIR="$HOME/.openclaw-monitor"
mkdir -p "$INSTALL_DIR"

# 复制文件
echo "→ 安装文件..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"

echo "  ✓ 文件已复制到 $INSTALL_DIR"

# 安装依赖
echo "→ 安装 Python 依赖..."
cd "$INSTALL_DIR"

# 检查 pip
if ! python3 -m pip --version &> /dev/null; then
    echo "${YELLOW}→ 安装 pip...${NC}"
    python3 -m ensurepip --default-pip 2>/dev/null || {
        echo "${RED}✗ 无法安装 pip${NC}"
        exit 1
    }
fi

# 安装依赖
python3 -m pip install -r requirements.txt --user --break-system-packages 2>/dev/null || \
python3 -m pip install -r requirements.txt --user

echo "  ✓ 依赖安装完成"

# 创建启动脚本
echo "→ 创建启动脚本..."

cat > "$INSTALL_DIR/start.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 app.py "$@"
EOF

chmod +x "$INSTALL_DIR/start.sh"

# 创建 systemd 服务（可选）
if command -v systemctl &> /dev/null; then
    echo "→ 创建 systemd 服务..."
    
    cat > "$INSTALL_DIR/openclaw-monitor.service" << EOF
[Unit]
Description=OpenClaw Monitor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$HOME/.local/bin/python3 $INSTALL_DIR/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

    echo "  ✓ 服务文件已创建"
    echo ""
    echo "  要安装为系统服务，请运行:"
    echo "    sudo cp $INSTALL_DIR/openclaw-monitor.service /etc/systemd/system/"
    echo "    sudo systemctl daemon-reload"
    echo "    sudo systemctl enable openclaw-monitor"
    echo "    sudo systemctl start openclaw-monitor"
fi

# 创建快捷方式
echo "→ 创建快捷方式..."

mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/openclaw-monitor" << EOF
#!/bin/bash
exec "$INSTALL_DIR/start.sh" "\$@"
EOF
chmod +x "$HOME/.local/bin/openclaw-monitor"

echo "  ✓ 快捷方式已创建: openclaw-monitor"

echo ""
echo "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo "${GREEN}║              安装完成!                                   ║${NC}"
echo "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  启动方式:"
echo "    1. 直接运行: $INSTALL_DIR/start.sh"
echo "    2. 快捷方式: openclaw-monitor (如果 ~/.local/bin 在 PATH 中)"
echo ""
echo "  访问地址:"
echo "    - 本地: http://127.0.0.1:8080"
echo "    - 局域网: http://$(hostname -I | awk '{print $1}'):8080"
echo ""
echo "  配置文件:"
echo "    - 定价配置: ~/.openclaw-monitor/pricing.json"
echo ""
echo "  按 Enter 键启动服务，或 Ctrl+C 退出..."
read

cd "$INSTALL_DIR"
python3 app.py
