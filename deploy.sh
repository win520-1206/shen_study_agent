#!/bin/bash
# ============================================
# LearnMate-AI 自动化部署脚本
# 适用系统：Ubuntu 22.04 LTS
# 用法：chmod +x deploy.sh && sudo ./deploy.sh
# ============================================

set -e  # 遇到错误立即停止

echo "========================================"
echo "  LearnMate-AI 自动化部署"
echo "========================================"
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本：sudo ./deploy.sh"
    exit 1
fi

# 获取项目信息
read -p "请输入你的 GitHub 仓库地址（如 https://github.com/用户名/learnmate-ai.git）: " REPO_URL
if [ -z "$REPO_URL" ]; then
    echo "错误：必须提供仓库地址"
    exit 1
fi

PROJECT_DIR="/opt/learnmate-ai"

echo ""
echo "[1/6] 更新系统..."
apt update && apt upgrade -y

echo ""
echo "[2/6] 安装 Python 3.10+..."
apt install -y python3 python3-pip python3-venv git

echo ""
echo "[3/6] 安装 Node.js 18.x（用于构建前端）..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

echo ""
echo "[4/6] 克隆项目..."
if [ -d "$PROJECT_DIR" ]; then
    echo "目录已存在，更新代码..."
    cd "$PROJECT_DIR"
    git pull
else
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

echo ""
echo "[5/6] 安装依赖并构建前端..."
# 创建 Python 虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 Python 依赖
pip install -r requirements.txt

# 构建前端
cd src/frontend
npm install
npm run build
cd ../..

echo ""
echo "[6/6] 配置 systemd 服务..."

# 创建 systemd 服务文件
cat > /etc/systemd/system/learnmate.service << EOF
[Unit]
Description=LearnMate-AI Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python3 -m uvicorn src.backend.app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
systemctl daemon-reload
systemctl enable learnmate
systemctl start learnmate

echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
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
