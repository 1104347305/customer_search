#!/usr/bin/env python3
"""导入demo数据到Elasticsearch"""

import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from elasticsearch import Elasticsearch
from loguru import logger

def import_demo_data():
    """导入demo数据"""
    # 连接ES
    es = Elasticsearch(["http://localhost:9200"])

    # 读取demo数据
    demo_file = project_root / "docs" / "数据demo.txt"
    with open(demo_file, 'r', encoding='utf-8') as f:
        demo_data = json.load(f)

    # 添加agent_id（如果没有）
    if 'agent_id' not in demo_data:
        demo_data['agent_id'] = 'A000001'

    # 导入到ES
    try:
        result = es.index(
            index='customers',
            id=demo_data['customer_id'],
            document=demo_data
        )
        logger.info(f"✅ Demo数据导入成功: {result['result']}")
        logger.info(f"   客户ID: {demo_data['customer_id']}")
        logger.info(f"   姓名: {demo_data['name']}")
        logger.info(f"   身份证号: {demo_data['certificates'][0]['id_number']}")
        return True
    except Exception as e:
        logger.error(f"❌ 导入失败: {e}")
        return False

if __name__ == "__main__":
    import_demo_data()
