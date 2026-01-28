#!/bin/bash

# 成绩分析系统管理脚本

case "$1" in
    start)
        echo "🚀 启动服务..."
        docker-compose up -d
        ;;
    stop)
        echo "🛑 停止服务..."
        docker-compose down
        ;;
    restart)
        echo "🔄 重启服务..."
        docker-compose restart
        ;;
    status)
        echo "📊 服务状态："
        docker-compose ps
        ;;
    logs)
        if [ -n "$2" ]; then
            echo "📋 查看 $2 服务日志："
            docker-compose logs -f "$2"
        else
            echo "📋 查看所有服务日志："
            docker-compose logs -f
        fi
        ;;
    update)
        echo "🔄 更新系统..."
        git pull
        docker-compose build
        docker-compose up -d
        ;;
    backup)
        echo "💾 备份数据库..."
        docker-compose exec mysql mysqldump -u root -p grade_insights > "backup_$(date +%Y%m%d_%H%M%S).sql"
        echo "✅ 备份完成"
        ;;
    clean)
        echo "🧹 清理Docker资源..."
        docker-compose down
        docker system prune -f
        docker volume prune -f
        ;;
    *)
        echo "成绩分析系统管理工具"
        echo ""
        echo "使用方法: $0 {start|stop|restart|status|logs|update|backup|clean}"
        echo ""
        echo "命令说明:"
        echo "  start   - 启动所有服务"
        echo "  stop    - 停止所有服务"
        echo "  restart - 重启所有服务"
        echo "  status  - 查看服务状态"
        echo "  logs    - 查看服务日志 (可指定服务名)"
        echo "  update  - 更新系统代码并重启"
        echo "  backup  - 备份数据库"
        echo "  clean   - 清理Docker资源"
        echo ""
        echo "示例:"
        echo "  $0 start"
        echo "  $0 logs backend"
        echo "  $0 backup"
        exit 1
        ;;
esac