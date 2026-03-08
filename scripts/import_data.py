#!/usr/bin/env python3
"""
数据导入脚本
将customers.json中的数据批量导入到Elasticsearch
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from loguru import logger
from tqdm import tqdm
from app.config import settings


def load_customers(file_path: Path) -> List[Dict[str, Any]]:
    """
    从JSON文件加载客户数据

    Args:
        file_path: 客户数据文件路径

    Returns:
        客户数据列表
    """
    logger.info(f"Loading customers from {file_path}")

    if not file_path.exists():
        raise FileNotFoundError(f"Customer data file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        customers = json.load(f)

    logger.info(f"Loaded {len(customers)} customers")
    return customers


def generate_bulk_actions(customers: List[Dict[str, Any]], index_name: str):
    """
    生成批量导入的actions

    Args:
        customers: 客户数据列表
        index_name: 索引名称

    Yields:
        ES bulk action
    """
    for customer in customers:
        yield {
            "_index": index_name,
            "_id": customer["customer_id"],
            "_source": customer
        }


def import_data(es: Elasticsearch, customers: List[Dict[str, Any]], batch_size: int = 1000):
    """
    批量导入数据到Elasticsearch

    Args:
        es: Elasticsearch客户端
        customers: 客户数据列表
        batch_size: 批次大小

    Returns:
        导入统计信息
    """
    index_name = settings.ES_INDEX_NAME

    # 检查索引是否存在
    if not es.indices.exists(index=index_name):
        logger.error(f"Index '{index_name}' does not exist. Please run init_elasticsearch.py first.")
        return None

    logger.info(f"Starting bulk import to index '{index_name}'")
    logger.info(f"Total documents: {len(customers)}, Batch size: {batch_size}")

    # 批量导入
    success_count = 0
    error_count = 0

    # 分批处理
    total_batches = (len(customers) + batch_size - 1) // batch_size

    with tqdm(total=len(customers), desc="Importing") as pbar:
        for i in range(0, len(customers), batch_size):
            batch = customers[i:i + batch_size]
            actions = list(generate_bulk_actions(batch, index_name))

            try:
                success, errors = bulk(
                    es,
                    actions,
                    chunk_size=batch_size,
                    request_timeout=60,
                    raise_on_error=False
                )

                success_count += success
                if errors:
                    error_count += len(errors)
                    logger.warning(f"Batch {i//batch_size + 1}/{total_batches}: {len(errors)} errors")

                pbar.update(len(batch))

            except Exception as e:
                logger.error(f"Failed to import batch {i//batch_size + 1}: {e}")
                error_count += len(batch)
                pbar.update(len(batch))

    # 刷新索引
    es.indices.refresh(index=index_name)

    # 验证导入
    count = es.count(index=index_name)["count"]

    stats = {
        "total": len(customers),
        "success": success_count,
        "errors": error_count,
        "indexed_count": count
    }

    return stats


def main():
    """主函数"""
    print("=" * 60)
    print("Elasticsearch Data Import")
    print("=" * 60)

    # 连接ES
    try:
        if settings.ES_USER and settings.ES_PASSWORD:
            es_url = f"http://{settings.ES_USER}:{settings.ES_PASSWORD}@{settings.ES_HOST}:{settings.ES_PORT}"
        else:
            es_url = f"http://{settings.ES_HOST}:{settings.ES_PORT}"

        es = Elasticsearch([es_url], request_timeout=30)

        if not es.ping():
            logger.error("Cannot connect to Elasticsearch")
            sys.exit(1)

        logger.info(f"Connected to Elasticsearch at {settings.ES_HOST}:{settings.ES_PORT}")

    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        sys.exit(1)

    # 加载客户数据
    data_dir = project_root / "data"
    customers_file = data_dir / "customers.json"

    try:
        customers = load_customers(customers_file)
    except Exception as e:
        logger.error(f"Failed to load customer data: {e}")
        sys.exit(1)

    # 导入数据
    stats = import_data(es, customers, batch_size=1000)

    if stats:
        print("\n" + "=" * 60)
        print("Import Summary")
        print("=" * 60)
        print(f"Total documents: {stats['total']}")
        print(f"Successfully imported: {stats['success']}")
        print(f"Errors: {stats['errors']}")
        print(f"Documents in index: {stats['indexed_count']}")
        print("=" * 60)

        if stats['errors'] > 0:
            logger.warning(f"{stats['errors']} documents failed to import")

        if stats['indexed_count'] == stats['total']:
            print("\n✓ All documents imported successfully")
        else:
            print(f"\n⚠ Warning: Expected {stats['total']} documents, but index contains {stats['indexed_count']}")
    else:
        print("\n✗ Data import failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
