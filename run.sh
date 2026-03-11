#!/bin/bash
# 客户搜索系统一键启动脚本
# 用法: ./run.sh [端口号]
# 示例: ./run.sh 8001

set -e

# 端口配置（默认8000，可通过参数指定）
PORT=${1:-8000}
PID_FILE="/tmp/customer_search_${PORT}.pid"
LOG_FILE="/tmp/customer_search_${PORT}.log"

echo "=========================================="
echo "Customer Search System - Startup Script"
echo "端口: $PORT"
echo "=========================================="

# 切换到脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 Python
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    echo "✗ 错误: 未找到 Python"
    exit 1
fi
echo "Python: $($PYTHON --version) ($PYTHON)"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "✗ 错误: 未安装 Docker"
    exit 1
fi

# 检查端口是否已占用
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "✗ 错误: 端口 $PORT 已被占用"
    echo "  请更换端口或执行: kill \$(lsof -ti :$PORT)"
    exit 1
fi

# Step 0: 安装依赖
echo ""
echo "Step 0: 检查并安装依赖..."
$PYTHON -m pip install -r requirements.txt -q
echo "✓ 依赖已就绪"

# Step 1: 启动 Elasticsearch 和 Kibana
echo ""
echo "Step 1: 启动 Elasticsearch 和 Kibana..."
cd docker
docker-compose up -d elasticsearch kibana
cd ..

# 等待 Elasticsearch 就绪
echo "等待 Elasticsearch 启动..."
for i in {1..30}; do
    if curl -s http://localhost:9200 > /dev/null 2>&1; then
        echo "✓ Elasticsearch 已就绪"
        break
    fi
    echo "  等待中... ($i/30)"
    sleep 2
done

if ! curl -s http://localhost:9200 > /dev/null 2>&1; then
    echo "✗ Elasticsearch 启动失败"
    exit 1
fi

# Step 2: 生成 Mock 数据（如不存在）
echo ""
if [ ! -f "data/customers.json" ]; then
    echo "Step 2: 生成 Mock 数据..."
    $PYTHON scripts/generate_mock_data.py
else
    echo "Step 2: Mock 数据已存在，跳过生成"
fi

# Step 3: 初始化 Elasticsearch 索引
echo ""
echo "Step 3: 初始化 Elasticsearch 索引..."
$PYTHON scripts/init_elasticsearch.py

# Step 4: 导入数据
echo ""
echo "Step 4: 导入数据到 Elasticsearch..."
$PYTHON scripts/import_data.py

# Step 5: 启动 API 服务（后台运行）
echo ""
echo "Step 5: 启动 API 服务..."
nohup $PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port $PORT > "$LOG_FILE" 2>&1 &
API_PID=$!
echo $API_PID > "$PID_FILE"

# 等待 API 服务就绪
echo "等待 API 服务启动..."
for i in {1..15}; do
    if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
        echo "✓ API 服务已就绪"
        break
    fi
    sleep 1
done

if ! curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
    echo "✗ API 服务启动失败，请查看日志: $LOG_FILE"
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
echo "  停止服务:   ./stop.sh $PORT"
echo "=========================================="
