#!/bin/bash
# 客户搜索系统启动脚本（Linux，无 Docker）
# 用法: ./run-linux-nodocker.sh [端口号]
# 示例: ./run-linux-nodocker.sh 8001
# 前提: Elasticsearch 已在本地 9200 端口运行

PORT=${1:-8000}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/api_${PORT}.log"
PID_FILE="$SCRIPT_DIR/logs/api_${PORT}.pid"

echo "=========================================="
echo "Customer Search System - Startup (No Docker)"
echo "端口: $PORT"
echo "=========================================="

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"

# --- 检测 Python ---
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "[ERROR] 未找到 Python 3，请安装 Python 3.8+ 并添加到 PATH。"
    exit 1
fi
echo "[OK] Python: $($PYTHON --version) ($PYTHON)"

# --- 检查端口是否已占用 ---
if ss -tlnp 2>/dev/null | grep -q ":${PORT} " || lsof -i ":${PORT}" &>/dev/null; then
    echo "[ERROR] 端口 $PORT 已被占用。"
    echo "  请更换端口或执行: kill \$(lsof -ti :$PORT)"
    exit 1
fi

cd "$SCRIPT_DIR"

# --- Step 0: 安装依赖 ---
echo ""
echo "Step 0: 检查并安装 Python 依赖..."
$PYTHON -m pip install -r requirements.txt -q
echo "[OK] 依赖已就绪"

# --- Step 1: 检查 Elasticsearch ---
echo ""
echo "Step 1: 检查 Elasticsearch..."
if ! curl -s http://localhost:9200 &>/dev/null; then
    echo "[ERROR] Elasticsearch 未在 localhost:9200 运行"
    echo ""
    echo "请先手动启动 Elasticsearch："
    echo "  1. 下载: https://www.elastic.co/downloads/elasticsearch"
    echo "  2. 解压后执行: ./bin/elasticsearch"
    echo "  3. 等待启动完成后，再运行本脚本"
    exit 1
fi
echo "[OK] Elasticsearch 运行正常"

# --- Step 2: 生成 Mock 数据 ---
echo ""
if [ ! -f "$SCRIPT_DIR/data/customers.json" ]; then
    echo "Step 2: 生成 Mock 数据（首次运行，约 30s）..."
    $PYTHON scripts/generate_mock_data.py
    if [ $? -ne 0 ]; then
        echo "[ERROR] Mock 数据生成失败"
        exit 1
    fi
else
    echo "Step 2: Mock 数据已存在，跳过生成"
fi

# --- Step 3: 初始化 ES 索引 ---
echo ""
echo "Step 3: 初始化 Elasticsearch 索引..."
$PYTHON scripts/init_elasticsearch.py
if [ $? -ne 0 ]; then
    echo "[ERROR] 索引初始化失败"
    exit 1
fi
echo "[OK] 索引初始化完成"

# --- Step 4: 导入数据 ---
echo ""
echo "Step 4: 导入数据到 Elasticsearch..."
$PYTHON scripts/import_data.py
if [ $? -ne 0 ]; then
    echo "[ERROR] 数据导入失败"
    exit 1
fi
echo "[OK] 数据导入完成"

# --- Step 5: 启动 API 服务 ---
echo ""
echo "Step 5: 启动 API 服务..."
nohup $PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port $PORT > "$LOG_FILE" 2>&1 &
API_PID=$!
echo $API_PID > "$PID_FILE"

# 等待 API 就绪
echo "等待 API 服务启动..."
for i in $(seq 1 15); do
    if curl -s "http://localhost:${PORT}/health" &>/dev/null; then
        echo "[OK] API 服务已就绪"
        break
    fi
    echo "  等待中... ($i/15)"
    sleep 1
done

if ! curl -s "http://localhost:${PORT}/health" &>/dev/null; then
    echo "[ERROR] API 服务启动失败，请查看日志: $LOG_FILE"
    exit 1
fi

echo ""
echo "=========================================="
echo "[OK] 所有服务启动成功！"
echo "=========================================="
echo "  API 文档:   http://localhost:${PORT}/docs"
echo "  健康检查:   http://localhost:${PORT}/health"
echo "  API PID:    $API_PID"
echo "  日志文件:   $LOG_FILE"
echo "  停止服务:   ./stop-linux-nodocker.sh $PORT"
echo "  注意: Elasticsearch 需手动管理，不会被本脚本停止"
echo "=========================================="
