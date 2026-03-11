#!/bin/bash
# 客户搜索系统停止脚本
# 用法: ./stop.sh [端口号]
# 示例: ./stop.sh 8001

PORT=${1:-8000}
PID_FILE="/tmp/customer_search_${PORT}.pid"

echo "=========================================="
echo "Customer Search System - Shutdown Script"
echo "=========================================="

# 停止 API 服务
if [ -f "$PID_FILE" ]; then
    API_PID=$(cat "$PID_FILE")
    if kill -0 $API_PID 2>/dev/null; then
        echo "停止 API 服务 (PID: $API_PID)..."
        kill $API_PID
        rm -f "$PID_FILE"
        echo "✓ API 服务已停止"
    else
        echo "API 服务未运行，清理 PID 文件"
        rm -f "$PID_FILE"
    fi
else
    API_PID=$(lsof -ti :$PORT 2>/dev/null)
    if [ -n "$API_PID" ]; then
        echo "停止端口 $PORT 上的服务 (PID: $API_PID)..."
        kill $API_PID
        echo "✓ API 服务已停止"
    else
        echo "端口 $PORT 上没有运行中的服务"
    fi
fi

# 停止 Docker 容器
echo ""
echo "停止 Docker 容器..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/docker"
docker-compose down

echo ""
echo "✓ 所有服务已停止"
