from fastapi import APIRouter
from datetime import datetime
from app.models.response import HealthResponse
from app.core.elasticsearch import ElasticsearchClient
from app.services.search_service import SearchService
from loguru import logger

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查接口

    检查API服务和Elasticsearch连接状态
    """
    try:
        # 检查ES连接
        es_client = ElasticsearchClient.get_client()
        es_status = "connected" if es_client.ping() else "disconnected"

        # 检查索引状态
        service = SearchService()
        index_health = service.check_index_health()

        return HealthResponse(
            status="healthy",
            elasticsearch=f"{es_status} (index: {index_health['status']}, count: {index_health['count']})",
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            elasticsearch=f"error: {str(e)}",
            timestamp=datetime.now().isoformat()
        )
