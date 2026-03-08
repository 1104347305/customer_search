from typing import Dict, Any, List
from elasticsearch import Elasticsearch
from loguru import logger
from app.config import settings
from app.core.exceptions import ElasticsearchConnectionError


class ElasticsearchRepository:
    """Elasticsearch数据访问层"""

    def __init__(self, es_client: Elasticsearch):
        self.es_client = es_client
        self.index_name = settings.ES_INDEX_NAME

    def search(
        self,
        query: Dict[str, Any],
        page: int,
        size: int,
        sort: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行搜索查询

        Args:
            query: ES查询DSL
            page: 页码
            size: 每页数量
            sort: 排序条件

        Returns:
            搜索结果字典
        """
        try:
            # 计算偏移量
            from_offset = (page - 1) * size

            # 构建搜索参数
            search_params = {
                "index": self.index_name,
                "query": query,
                "from": from_offset,
                "size": size,
                "track_total_hits": True
            }

            if sort:
                search_params["sort"] = sort

            # 执行搜索
            response = self.es_client.search(**search_params)

            # 提取结果
            hits = response["hits"]
            total = hits["total"]["value"]
            took = response["took"]

            # 提取文档
            documents = [hit["_source"] for hit in hits["hits"]]

            return {
                "total": total,
                "took": took,
                "documents": documents
            }

        except Exception as e:
            logger.error(f"Elasticsearch search failed: {e}")
            raise ElasticsearchConnectionError(f"Search failed: {e}")

    def get_by_id(self, customer_id: str) -> Dict[str, Any]:
        """
        根据ID获取客户

        Args:
            customer_id: 客户ID

        Returns:
            客户数据
        """
        try:
            response = self.es_client.get(index=self.index_name, id=customer_id)
            return response["_source"]
        except Exception as e:
            logger.error(f"Failed to get customer {customer_id}: {e}")
            raise ElasticsearchConnectionError(f"Get by ID failed: {e}")

    def index_exists(self) -> bool:
        """
        检查索引是否存在

        Returns:
            索引是否存在
        """
        try:
            return self.es_client.indices.exists(index=self.index_name)
        except Exception as e:
            logger.error(f"Failed to check index existence: {e}")
            return False

    def count(self, query: Dict[str, Any] = None) -> int:
        """
        统计文档数量

        Args:
            query: 查询条件（可选）

        Returns:
            文档数量
        """
        try:
            if query:
                response = self.es_client.count(index=self.index_name, query=query)
            else:
                response = self.es_client.count(index=self.index_name)
            return response["count"]
        except Exception as e:
            logger.error(f"Failed to count documents: {e}")
            return 0
