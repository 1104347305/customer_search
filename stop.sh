#!/bin/bash
# 停止服务脚本

echo "=========================================="
echo "Customer Search System - Shutdown Script"
echo "=========================================="

# 停止Docker容器
echo "Stopping Docker containers..."
cd docker
docker-compose down
cd ..

echo "✓ All services stopped"
