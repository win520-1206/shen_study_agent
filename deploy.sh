#!/bin/bash
# ============================================
# LearnMate-AI 自动化部署脚本
# 适用系统：Ubuntu 22.04 LTS
# Python 版本：3.13
# 用法：chmod +x deploy.sh && sudo ./deploy.sh
# ============================================

set -e

echo "========================================"
echo "  LearnMate-AI 自动化部署"
echo "========================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本：sudo ./deploy.sh"
    exit 1
fi

PROJECT_DIR="/opt/shen_study_agent"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "错误：项目目录不存在：$PROJECT_DIR"
    echo "请先把项目上传到服务器。"
    exit 1
fi

cd "$PROJECT_DIR"

echo "[1/6] 更新系统..."
apt update && apt upgrade -y

echo "[2/6] 安装 Python 3.13..."
apt install -y software-properties-common
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.13 python3.13-venv python3.13-dev python3-pip git curl

echo "[3/6] 安装 Node.js 18.x（用于构建前端）..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

echo "[4/6] 创建并激活 Python 3.13 虚拟环境..."
rm -rf venv
python3.13 -m venv venv
source venv/bin/activate

echo "[5/6] 安装依赖并构建前端..."
python -m pip install --upgrade pip
pip install -r requirements.txt

cd src/frontend
npm install
npm run build
cd ../..

echo "[6/6] 配置 systemd 服务..."
cat > /etc/systemd/system/learnmate.service << EOF
[Unit]
Description=LearnMate-AI Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python -m uvicorn src.backend.app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable learnmate
systemctl restart learnmate

echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
echo "Python 版本：$(python3.13 --version)"
echo "访问地址：http://$(curl -s ifconfig.me):8000"
echo "API 文档：http://$(curl -s ifconfig.me):8000/docs"
echo ""
echo "常用命令："
echo "  查看状态：systemctl status learnmate"
echo "  查看日志：journalctl -u learnmate -f"
echo "  重启服务：systemctl restart learnmate"
echo "  停止服务：systemctl stop learnmate"
echo ""
echo "========================================"
