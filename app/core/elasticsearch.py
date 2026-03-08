from elasticsearch import Elasticsearch
from typing import Optional
from loguru import logger
from app.config import settings
from app.core.exceptions import ElasticsearchConnectionError


class ElasticsearchClient:
    """Elasticsearch client singleton"""

    _instance: Optional[Elasticsearch] = None

    @classmethod
    def get_client(cls) -> Elasticsearch:
        """Get or create Elasticsearch client"""
        if cls._instance is None:
            cls._instance = cls._create_client()
        return cls._instance

    @classmethod
    def _create_client(cls) -> Elasticsearch:
        """Create Elasticsearch client"""
        try:
            # Build connection URL
            if settings.ES_USER and settings.ES_PASSWORD:
                es_url = f"http://{settings.ES_USER}:{settings.ES_PASSWORD}@{settings.ES_HOST}:{settings.ES_PORT}"
            else:
                es_url = f"http://{settings.ES_HOST}:{settings.ES_PORT}"

            # Create client
            client = Elasticsearch(
                [es_url],
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )

            # Test connection
            if not client.ping():
                raise ElasticsearchConnectionError("Cannot ping Elasticsearch")

            logger.info(f"Connected to Elasticsearch at {settings.ES_HOST}:{settings.ES_PORT}")
            return client

        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise ElasticsearchConnectionError(details=str(e))

    @classmethod
    def close(cls):
        """Close Elasticsearch connection"""
        if cls._instance:
            cls._instance.close()
            cls._instance = None
            logger.info("Elasticsearch connection closed")
