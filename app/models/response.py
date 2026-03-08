from typing import List, Any, Optional
from pydantic import BaseModel, Field


class SearchDataResponse(BaseModel):
    """搜索数据响应"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    list: List[Any] = Field(..., description="数据列表")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "size": 10,
                "list": []
            }
        }


class SearchResponse(BaseModel):
    """搜索响应（符合V3接口规范）"""
    code: int = Field(200, description="响应码")
    message: str = Field("success", description="响应消息")
    data: SearchDataResponse = Field(..., description="响应数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {
                    "total": 100,
                    "page": 1,
                    "size": 10,
                    "list": []
                }
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    elasticsearch: str = Field(..., description="ES连接状态")
    timestamp: str = Field(..., description="检查时间")
