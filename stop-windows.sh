#!/bin/bash
# 客户搜索系统 Windows 停止脚本（需在 Git Bash 中运行）
#
# 用法: bash stop-windows.sh [端口号]
# 示例: bash stop-windows.sh 8001

PORT=${1:-8000}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/logs/api_${PORT}.pid"

echo "=========================================="
echo "Customer Search System - Windows Shutdown"
echo "=========================================="

# ── 停止 API 服务 ─────────────────────────────
if [ -f "$PID_FILE" ]; then
    API_PID=$(cat "$PID_FILE")
    # Windows 上用 taskkill 终止进程
    if taskkill //F //PID $API_PID > /dev/null 2>&1; then
        echo "✓ API 服务已停止 (PID: $API_PID)"
    else
        echo "  API 进程已不存在 (PID: $API_PID)"
    fi
    rm -f "$PID_FILE"
else
    # 通过端口查找进程 PID（Windows netstat）
    API_PID=$(netstat -ano 2>/dev/null \
        | grep -E "0\.0\.0\.0:$PORT|127\.0\.0\.1:$PORT" \
        | grep "LISTENING" \
        | awk '{print $NF}' \
        | head -1)
    if [ -n "$API_PID" ]; then
        taskkill //F //PID $API_PID > /dev/null 2>&1
        echo "✓ API 服务已停止 (PID: $API_PID)"
    else
        echo "  端口 $PORT 上没有运行中的服务"
    fi
fi

# ── 停止 Docker 容器 ──────────────────────────
echo ""
echo "停止 Docker 容器..."
cd "$SCRIPT_DIR/docker"
docker-compose down
cd "$SCRIPT_DIR"

echo ""
echo "✓ 所有服务已停止"
