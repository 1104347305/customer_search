from fastapi import APIRouter, HTTPException
from loguru import logger
from app.models.request import SearchRequest
from app.models.response import SearchResponse
from app.services.search_service import SearchService
from app.core.exceptions import CustomerSearchException

router = APIRouter()


@router.post("/customer", response_model=SearchResponse)
async def search_customer(request: SearchRequest):
    """
    客户搜索接口（符合V3接口规范）

    支持多维度组合查询、模糊匹配、嵌套对象搜索等复杂场景

    **操作符说明：**
    - MATCH: 智能匹配（根据字段类型自动选择最佳匹配策略）
    - GTE: 大于等于
    - LTE: 小于等于
    - RANGE: 区间查询（value格式：{"min": 20, "max": 30}）
    - CONTAINS: 包含（精确匹配）
    - NOT_CONTAINS: 不包含（缺口查询）
    - NESTED_MATCH: 嵌套对象查询（需指定nested_path）

    **示例1：姓名模糊搜索**
    ```json
    {
        "header": {"agent_id": "A001", "page": 1, "size": 10},
        "conditions": [
            {"field": "name", "operator": "MATCH", "value": "张"}
        ]
    }
    ```

    **示例2：保障缺口组合挖掘**
    ```json
    {
        "header": {"agent_id": "A001", "page": 1, "size": 10},
        "query_logic": "AND",
        "conditions": [
            {"field": "age", "operator": "GTE", "value": 45},
            {"field": "marital_status", "operator": "MATCH", "value": "已婚"},
            {"field": "held_product_category", "operator": "NOT_CONTAINS", "value": "养老保险"}
        ]
    }
    ```

    **示例3：嵌套对象查询（保单状态）**
    ```json
    {
        "header": {"agent_id": "A001", "page": 1, "size": 10},
        "conditions": [
            {
                "field": "status",
                "operator": "NESTED_MATCH",
                "value": "缴费有效",
                "nested_path": "policies"
            }
        ]
    }
    ```
    """
    try:
        service = SearchService()
        response = service.search_customers(request)
        return response

    except CustomerSearchException as e:
        logger.error(f"Search failed: {e.message}, code: {e.code}")
        raise HTTPException(status_code=400, detail={
            "code": e.code,
            "message": e.message,
            "details": e.details
        })

    except Exception as e:
        logger.error(f"Unexpected error in search: {e}")
        raise HTTPException(status_code=500, detail={
            "code": "INTERNAL_ERROR",
            "message": "Internal server error",
            "details": str(e)
        })
