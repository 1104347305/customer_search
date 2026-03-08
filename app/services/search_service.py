from typing import Dict, Any
from loguru import logger
from app.models.request import SearchRequest
from app.models.response import SearchResponse, SearchDataResponse
from app.repositories.es_repository import ElasticsearchRepository
from app.services.query_builder import QueryBuilder
from app.services.data_masking import DataMasking
from app.core.elasticsearch import ElasticsearchClient


class SearchService:
    """搜索服务"""

    def __init__(self):
        self.es_client = ElasticsearchClient.get_client()
        self.repository = ElasticsearchRepository(self.es_client)
        self.query_builder = QueryBuilder()
        self.data_masking = DataMasking()

    def search_customers(self, request: SearchRequest) -> SearchResponse:
        """
        搜索客户（符合V3接口规范）

        Args:
            request: 搜索请求

        Returns:
            搜索响应
        """
        # 从header中提取参数
        agent_id = request.header.agent_id
        page = request.header.page
        size = request.header.size

        logger.info(f"Searching customers for agent {agent_id}, page={page}, size={size}")

        # 构建查询
        query = self.query_builder.build_query(
            agent_id=agent_id,
            conditions=request.conditions,
            query_logic=request.query_logic
        )

        # 构建排序
        sort = self.query_builder.build_sort(request.sort) if request.sort else None

        # 执行搜索
        result = self.repository.search(
            query=query,
            page=page,
            size=size,
            sort=sort
        )

        # 数据脱敏（已关闭）
        # masked_documents = self.data_masking.mask_customers(result["documents"])

        # 构建响应（符合V3接口规范）
        data_response = SearchDataResponse(
            total=result["total"],
            page=page,
            size=size,
            list=result["documents"]  # 直接返回原始数据，不脱敏
        )

        response = SearchResponse(
            code=200,
            message="success",
            data=data_response
        )

        logger.info(f"Search completed: found {result['total']} customers, took {result['took']}ms")
        return response

    def check_index_health(self) -> Dict[str, Any]:
        """
        检查索引健康状态

        Returns:
            健康状态信息
        """
        exists = self.repository.index_exists()
        if not exists:
            return {
                "exists": False,
                "count": 0,
                "status": "Index not found"
            }

        count = self.repository.count()
        return {
            "exists": True,
            "count": count,
            "status": "OK"
        }
