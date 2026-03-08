#!/usr/bin/env python3
"""
Elasticsearch索引初始化脚本 V2
按照新的数据格式创建索引mapping
"""

import sys
from pathlib import Path
from elasticsearch import Elasticsearch
from loguru import logger

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings


def get_index_mapping():
    """
    定义索引mapping - 匹配数据demo.txt格式
    """
    return {
        "settings": {
            "number_of_shards": 3,
            "number_of_replicas": 1,
            "max_ngram_diff": 10,
            "analysis": {
                "analyzer": {
                    "pinyin_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["pinyin_filter", "lowercase"]
                    },
                    "phone_analyzer": {
                        "type": "custom",
                        "tokenizer": "phone_tokenizer",
                        "filter": ["lowercase"]
                    }
                },
                "filter": {
                    "pinyin_filter": {
                        "type": "pinyin",
                        "keep_first_letter": True,
                        "keep_separate_first_letter": False,
                        "keep_full_pinyin": True,
                        "keep_original": True,
                        "limit_first_letter_length": 16,
                        "lowercase": True,
                        "remove_duplicated_term": True
                    }
                },
                "tokenizer": {
                    "phone_tokenizer": {
                        "type": "ngram",
                        "min_gram": 3,
                        "max_gram": 11,
                        "token_chars": ["digit"]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                # 代理人ID（用于权限过滤）
                "agent_id": {"type": "keyword"},

                # 基础信息
                "name": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {"type": "keyword"},
                        "pinyin": {"type": "text", "analyzer": "pinyin_analyzer"}
                    }
                },
                "mobile_phone": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "gender": {"type": "keyword"},
                "client_birth": {"type": "keyword"},
                "client_birth_month_and_day": {"type": "keyword"},
                "age": {"type": "integer"},
                "education": {"type": "keyword"},
                "marital_status": {"type": "keyword"},
                "customer_id": {"type": "keyword"},
                "customer_added_date": {"type": "keyword"},

                # 客户分类
                "customer_value": {"type": "keyword"},
                "customer_temperature": {"type": "keyword"},
                "customer_segment_tag": {"type": "keyword"},
                "life_insurance_vip": {"type": "keyword"},
                "operation_stage": {"type": "keyword"},
                "pingan_vip": {"type": "keyword"},
                "is_life_insured": {"type": "keyword"},
                "stock_customer_type": {"type": "keyword"},

                # 保险产品
                "life_insurance_product": {"type": "keyword"},
                "held_product_type": {"type": "keyword"},
                "held_product_category": {"type": "keyword"},
                "property_insurance_product": {"type": "keyword"},
                "pension_insurance_product": {"type": "keyword"},
                "health_insurance": {"type": "keyword"},
                "life_liability_type": {"type": "keyword"},
                "life_design_type": {"type": "keyword"},
                "target_purchase_category": {"type": "keyword"},

                # 保费保额
                "annual_premium": {"type": "integer"},
                "total_coverage": {"type": "keyword"},
                "latest_underwriting_time": {"type": "keyword"},
                "is_survival_gold_claimed": {"type": "keyword"},
                "is_payment_matured": {"type": "keyword"},
                "policy_anniversary": {"type": "keyword"},

                # 营销相关
                "prospect_source": {"type": "keyword"},
                "held_cross_sell_category": {"type": "keyword"},
                "vehicle_purchase_price": {"type": "keyword"},
                "is_cross_sell_claim": {"type": "keyword"},
                "policy_expiry_date": {"type": "keyword"},
                "valid_short_term_policy": {"type": "keyword"},

                # 服务等级
                "home_care_level": {"type": "keyword"},
                "health_care_level": {"type": "keyword"},
                "anyouhu_level": {"type": "keyword"},
                "zhenxiang_family_level": {"type": "keyword"},
                "investable_assets": {"type": "keyword"},

                # 家庭成员（嵌套对象）
                "family_members": {
                    "type": "nested",
                    "properties": {
                        "relationship": {"type": "keyword"},
                        "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                        "birth_date": {"type": "keyword"},
                        "age": {"type": "integer"},
                        "mobile": {"type": "keyword"}
                    }
                },

                # 证件信息（嵌套对象）
                "certificates": {
                    "type": "nested",
                    "properties": {
                        "id_type": {"type": "keyword"},
                        "id_number": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {"keyword": {"type": "keyword"}}
                        }
                    }
                },

                # 保单信息（嵌套对象）
                "policies": {
                    "type": "nested",
                    "properties": {
                        "product_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                        "policy_id": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {"keyword": {"type": "keyword"}}
                        },
                        "effective_date": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "period_premium": {"type": "integer"},
                        "due_date": {"type": "keyword"},
                        "underwriting_conclusion": {"type": "keyword"},
                        "free_look_expiry": {"type": "keyword"},
                        "coverage_details": {
                            "type": "nested",
                            "properties": {
                                "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                                "alias": {"type": "keyword"},
                                "type": {"type": "keyword"},
                                "insured_person": {"type": "keyword"}
                            }
                        },
                        "applicant_name": {"type": "keyword"},
                        "applicant_mobile": {"type": "keyword"},
                        "insured_name": {"type": "keyword"},
                        "insured_mobile": {"type": "keyword"},
                        "beneficiary_name": {"type": "keyword"},
                        "beneficiary_mobile": {"type": "keyword"},
                        "survival_total_amount": {"type": "integer"},
                        "survival_claimed_amount": {"type": "integer"},
                        "survival_unclaimed_amount": {"type": "integer"},
                        "universal_acct_transfer": {"type": "integer"},
                        "survival_interest_total": {"type": "integer"},
                        "claim_records": {
                            "type": "nested",
                            "properties": {
                                "time": {"type": "keyword"},
                                "case_id": {"type": "keyword"},
                                "amount": {"type": "float"},
                                "coverage": {"type": "keyword"}
                            }
                        }
                    }
                },

                # 权益信息
                "benefits": {
                    "properties": {
                        "member_info": {
                            "type": "nested",
                            "properties": {
                                "level": {"type": "keyword"},
                                "validity": {"type": "keyword"},
                                "points": {"type": "integer"},
                                "premium_value": {"type": "keyword"},
                                "exclusive_service": {"type": "keyword"},
                                "proxy_order_auth": {"type": "keyword"},
                                "benefit_name": {"type": "keyword"},
                                "benefit_intro": {"type": "text"},
                                "points_cost": {"type": "keyword"},
                                "benefit_url": {"type": "keyword"}
                            }
                        },
                        "pingan_info": {
                            "type": "nested",
                            "properties": {
                                "service_line": {"type": "keyword"},
                                "period": {"type": "keyword"},
                                "stage": {"type": "keyword"},
                                "service_level": {"type": "keyword"},
                                "benefit_name": {"type": "keyword"},
                                "benefit_intro": {"type": "text"},
                                "expiry": {"type": "keyword"},
                                "benefit_url": {"type": "keyword"}
                            }
                        }
                    }
                },

                # 联系信息
                "wechat_nickname": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "email": {"type": "keyword"},
                "nationality": {"type": "keyword"},
                "registered_residence": {"type": "text"},
                "contact_address": {"type": "text", "analyzer": "standard"},
                "home_address": {"type": "text", "analyzer": "standard"},

                # 身体信息
                "height": {"type": "keyword"},
                "weight": {"type": "keyword"},

                # 职业信息
                "occupation": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "years_in_service": {"type": "keyword"},
                "employer": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "work_phone": {"type": "keyword"},
                "department": {"type": "keyword"},
                "job_position": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "company_address": {"type": "text"},

                # 财务信息
                "annual_income": {"type": "integer"},
                "household_income": {"type": "integer"},
                "real_estate_status": {"type": "keyword"},
                "real_vehicle_status": {"type": "keyword"},
                "asset_scale": {"type": "keyword"},

                # 车辆信息
                "vehicle_model": {"type": "keyword"},
                "vehicle_plate_number": {"type": "keyword"}
            }
        }
    }


def init_elasticsearch():
    """初始化Elasticsearch索引"""
    try:
        # 连接ES
        es = Elasticsearch(
            [f"http://{settings.ES_HOST}:{settings.ES_PORT}"],
            basic_auth=(settings.ES_USER, settings.ES_PASSWORD) if settings.ES_USER else None
        )

        logger.info(f"Connected to Elasticsearch at {settings.ES_HOST}:{settings.ES_PORT}")

        index_name = settings.ES_INDEX_NAME

        # 删除已存在的索引
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
            logger.info(f"Deleted existing index '{index_name}'")

        # 创建索引
        mapping = get_index_mapping()
        es.indices.create(index=index_name, body=mapping)
        logger.info(f"Created index '{index_name}' successfully")

        # 获取索引信息
        index_info = es.indices.get_settings(index=index_name)
        logger.info(f"Index info: {index_info[index_name]['settings']['index']}")

        print("=" * 60)
        print("Elasticsearch Index Initialization V2")
        print("=" * 60)
        print(f"ES Host: {settings.ES_HOST}:{settings.ES_PORT}")
        print(f"Index Name: {index_name}")
        print("=" * 60)
        print("\n✓ Elasticsearch index initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize Elasticsearch: {e}")
        print("=" * 60)
        print("Elasticsearch Index Initialization V2")
        print("=" * 60)
        print(f"ES Host: {settings.ES_HOST}:{settings.ES_PORT}")
        print(f"Index Name: {settings.ES_INDEX_NAME}")
        print("=" * 60)
        print("\n✗ Failed to initialize Elasticsearch index")
        raise


if __name__ == "__main__":
    init_elasticsearch()
