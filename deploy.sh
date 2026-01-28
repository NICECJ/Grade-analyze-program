#!/bin/bash

# 成绩分析系统部署脚本
echo "🚀 开始部署成绩分析系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs
mkdir -p mysql/init
mkdir -p code/backups
mkdir -p code/templates

# 设置权限
chmod +x deploy.sh
chmod 755 logs
chmod 755 code/backups

# 复制环境配置
if [ ! -f .env ]; then
    echo "📝 复制生产环境配置..."
    cp .env.production .env
    echo "⚠️  请编辑 .env 文件，设置安全的密码！"
fi

# 构建并启动服务
echo "🔨 构建Docker镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 显示日志
echo "📋 显示服务日志..."
docker-compose logs --tail=20

echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址："
echo "   前端: http://your-server-ip"
echo "   后端API: http://your-server-ip:8000/docs"
echo ""
echo "📊 监控命令："
echo "   查看日志: docker-compose logs -f"
echo "   查看状态: docker-compose ps"
echo "   重启服务: docker-compose restart"
echo "   停止服务: docker-compose down"