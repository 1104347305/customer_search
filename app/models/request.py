from typing import Optional, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class OperatorEnum(str, Enum):
    """查询操作符"""
    MATCH = "MATCH"
    GTE = "GTE"
    LTE = "LTE"
    RANGE = "RANGE"
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"
    NESTED_MATCH = "NESTED_MATCH"
    EXISTS = "EXISTS"
    NOT_EXISTS = "NOT_EXISTS"


class QueryLogicEnum(str, Enum):
    """查询逻辑"""
    AND = "AND"
    OR = "OR"


class SortOrderEnum(str, Enum):
    """排序方向"""
    ASC = "asc"
    DESC = "desc"


class Condition(BaseModel):
    """查询条件"""
    field: str = Field(..., description="字段名")
    operator: OperatorEnum = Field(..., description="操作符")
    value: Any = Field(None, description="查询值")
    nested_path: Optional[str] = Field(None, description="嵌套路径（用于NESTED_MATCH）")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "name",
                "operator": "MATCH",
                "value": "张"
            }
        }


class SortOrder(BaseModel):
    """排序条件"""
    field: str = Field(..., description="排序字段")
    order: SortOrderEnum = Field(SortOrderEnum.DESC, description="排序方向")


class HeaderParams(BaseModel):
    """请求头参数（符合V3接口规范）"""
    agent_id: str = Field(..., description="代理人ID")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=1000, description="每页数量")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "A001",
                "page": 1,
                "size": 10
            }
        }


class SearchRequest(BaseModel):
    """搜索请求（符合V3接口规范）"""
    header: HeaderParams = Field(..., description="系统级参数")
    conditions: List[Condition] = Field(default_factory=list, description="查询条件列表")
    query_logic: QueryLogicEnum = Field(QueryLogicEnum.AND, description="条件组合逻辑")
    sort: Optional[List[SortOrder]] = Field(None, description="排序条件")

    class Config:
        json_schema_extra = {
            "example": {
                "header": {
                    "agent_id": "A001",
                    "page": 1,
                    "size": 10
                },
                "query_logic": "AND",
                "conditions": [
                    {
                        "field": "name",
                        "operator": "MATCH",
                        "value": "张"
                    },
                    {
                        "field": "age",
                        "operator": "GTE",
                        "value": 30
                    }
                ]
            }
        }

