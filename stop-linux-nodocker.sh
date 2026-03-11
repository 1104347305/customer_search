#!/bin/bash
# 客户搜索系统停止脚本（Linux，无 Docker）
# 用法: ./stop-linux-nodocker.sh [端口号]
# 示例: ./stop-linux-nodocker.sh 8001

PORT=${1:-8000}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/logs/api_${PORT}.pid"

echo "=========================================="
echo "Customer Search System - Shutdown (No Docker)"
echo "端口: $PORT"
echo "=========================================="

# 停止 API 服务
if [ -f "$PID_FILE" ]; then
    API_PID=$(cat "$PID_FILE")
    if kill -0 "$API_PID" 2>/dev/null; then
        echo "停止 API 服务 (PID: $API_PID)..."
        kill "$API_PID"
        rm -f "$PID_FILE"
        echo "[OK] API 服务已停止"
    else
        echo "    API 进程不存在 (PID: $API_PID)，清理 PID 文件"
        rm -f "$PID_FILE"
    fi
else
    API_PID=$(lsof -ti ":${PORT}" 2>/dev/null)
    if [ -n "$API_PID" ]; then
        echo "停止端口 $PORT 上的服务 (PID: $API_PID)..."
        kill "$API_PID"
        echo "[OK] API 服务已停止"
    else
        echo "    端口 $PORT 上没有运行中的服务"
    fi
fi

echo ""
echo "[OK] API 服务已停止。"
echo "    注意: Elasticsearch 未被停止，如需关闭请手动操作。"
echo "=========================================="
