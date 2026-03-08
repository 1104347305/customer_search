from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.logging import setup_logging
from app.core.elasticsearch import ElasticsearchClient
from app.api.v1.endpoints import search, health


# 设置日志
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting Customer Search API...")
    try:
        # 初始化ES连接
        ElasticsearchClient.get_client()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

    yield

    # 关闭时
    logger.info("Shutting down Customer Search API...")
    ElasticsearchClient.close()
    logger.info("Application shutdown complete")


# 创建FastAPI应用
app = FastAPI(
    title="Customer Search API",
    description="保险代理人客户搜索系统 - 支持多维度组合查询、模糊匹配、嵌套对象搜索",
    version="1.0.0",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(health.router, tags=["Health"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "Customer Search API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
