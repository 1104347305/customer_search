#!/bin/bash
# 客户搜索系统 Windows 启动脚本（需在 Git Bash 中运行）
# 前置条件：
#   1. 安装 Git for Windows（提供 Git Bash）
#   2. 安装 Docker Desktop for Windows 并确保已启动
#   3. 安装 Python 3.8+（确保已加入系统 PATH）
#
# 用法: bash run-windows.sh [端口号]
# 示例: bash run-windows.sh 8001

PORT=${1:-8000}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/api_${PORT}.log"
PID_FILE="$SCRIPT_DIR/logs/api_${PORT}.pid"

echo "=========================================="
echo "Customer Search System - Windows Startup"
echo "端口: $PORT"
echo "=========================================="

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"

# ── 检测 Python 命令 ──────────────────────────
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # 确认是 Python 3（Windows 上 python 可能是 2.x）
    PY_VER=$(python -c "import sys; print(sys.version_info.major)" 2>/dev/null)
    if [ "$PY_VER" = "3" ]; then
        PYTHON_CMD="python"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "✗ 错误: 未找到 Python 3，请安装 Python 3.8+ 并加入 PATH"
    exit 1
fi
echo "✓ Python: $($PYTHON_CMD --version)"

# ── 检测 Docker ───────────────────────────────
if ! command -v docker &> /dev/null; then
    echo "✗ 错误: 未找到 Docker，请安装 Docker Desktop for Windows"
    exit 1
fi
if ! docker info &> /dev/null; then
    echo "✗ 错误: Docker Desktop 未运行，请先启动 Docker Desktop"
    exit 1
fi
echo "✓ Docker: 正常运行"

# ── 检测端口是否已占用 ────────────────────────
check_port() {
    netstat -ano 2>/dev/null | grep -E "0\.0\.0\.0:$1|127\.0\.0\.1:$1" | grep "LISTENING" > /dev/null 2>&1
}

if check_port $PORT; then
    echo "✗ 错误: 端口 $PORT 已被占用"
    echo "  请更换端口，或运行 bash stop-windows.sh $PORT 停止旧服务"
    exit 1
fi

# ── 切换到项目目录 ────────────────────────────
cd "$SCRIPT_DIR"

# ── Step 1: 启动 Elasticsearch 和 Kibana ─────
echo ""
echo "Step 1: 启动 Elasticsearch 和 Kibana..."
cd docker
docker-compose up -d elasticsearch kibana
cd "$SCRIPT_DIR"

# 等待 Elasticsearch 就绪
echo "等待 Elasticsearch 启动（最多 60 秒）..."
ES_READY=false
for i in $(seq 1 30); do
    if curl -s http://localhost:9200 > /dev/null 2>&1; then
        ES_READY=true
        echo "✓ Elasticsearch 已就绪"
        break
    fi
    echo "  等待中... ($i/30)"
    sleep 2
done

if [ "$ES_READY" = false ]; then
    echo "✗ Elasticsearch 启动超时，请检查 Docker Desktop 是否正常"
    exit 1
fi

# ── Step 2: 生成 Mock 数据 ────────────────────
echo ""
if [ ! -f "data/customers.json" ]; then
    echo "Step 2: 生成 Mock 数据（首次运行，约需 30 秒）..."
    $PYTHON_CMD scripts/generate_mock_data.py
    if [ $? -ne 0 ]; then
        echo "✗ Mock 数据生成失败"
        exit 1
    fi
else
    echo "Step 2: Mock 数据已存在，跳过生成"
fi

# ── Step 3: 初始化 ES 索引 ────────────────────
echo ""
echo "Step 3: 初始化 Elasticsearch 索引..."
$PYTHON_CMD scripts/init_elasticsearch.py
if [ $? -ne 0 ]; then
    echo "✗ 索引初始化失败"
    exit 1
fi

# ── Step 4: 导入数据 ──────────────────────────
echo ""
echo "Step 4: 导入数据到 Elasticsearch..."
$PYTHON_CMD scripts/import_data.py
if [ $? -ne 0 ]; then
    echo "✗ 数据导入失败"
    exit 1
fi

# ── Step 5: 启动 API 服务 ─────────────────────
echo ""
echo "Step 5: 启动 API 服务..."

# Windows Git Bash 中用 & 后台运行，日志重定向到文件
uvicorn app.main:app --host 0.0.0.0 --port $PORT > "$LOG_FILE" 2>&1 &
API_PID=$!
echo $API_PID > "$PID_FILE"

# 等待 API 就绪
echo "等待 API 服务启动..."
API_READY=false
for i in $(seq 1 15); do
    if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
        API_READY=true
        echo "✓ API 服务已就绪"
        break
    fi
    sleep 1
done

if [ "$API_READY" = false ]; then
    echo "✗ API 服务启动失败，查看日志: $LOG_FILE"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ 所有服务启动成功！"
echo "=========================================="
echo "  API 文档:   http://localhost:$PORT/docs"
echo "  健康检查:   http://localhost:$PORT/health"
echo "  Kibana:     http://localhost:5601"
echo "  API PID:    $API_PID"
echo "  日志文件:   $LOG_FILE"
echo "  停止服务:   bash stop-windows.sh $PORT"
echo "=========================================="
