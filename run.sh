#!/bin/bash
# 一键启动脚本

set -e

echo "=========================================="
echo "Customer Search System - Startup Script"
echo "=========================================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# 1. 启动Elasticsearch和Kibana
echo ""
echo "Step 1: Starting Elasticsearch and Kibana..."
cd docker
docker-compose up -d elasticsearch kibana
cd ..

# 等待Elasticsearch启动
echo "Waiting for Elasticsearch to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:9200 > /dev/null 2>&1; then
        echo "✓ Elasticsearch is ready"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

if ! curl -s http://localhost:9200 > /dev/null 2>&1; then
    echo "✗ Elasticsearch failed to start"
    exit 1
fi

# 2. 生成Mock数据（如果不存在）
if [ ! -f "data/customers.json" ]; then
    echo ""
    echo "Step 2: Generating mock data..."
    python3 scripts/generate_mock_data.py
else
    echo ""
    echo "Step 2: Mock data already exists, skipping generation"
fi

# 3. 初始化Elasticsearch索引
echo ""
echo "Step 3: Initializing Elasticsearch index..."
python3 scripts/init_elasticsearch.py

# 4. 导入数据
echo ""
echo "Step 4: Importing data to Elasticsearch..."
python3 scripts/import_data.py

# 5. 启动API服务
echo ""
echo "Step 5: Starting API service..."
echo "=========================================="
echo "API will be available at:"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Health Check: http://localhost:8000/health"
echo "  - Kibana: http://localhost:5601"
echo "=========================================="
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000
