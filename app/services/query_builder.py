from typing import Dict, Any, List
from app.models.request import Condition, OperatorEnum, QueryLogicEnum
from app.core.exceptions import InvalidQueryError
from loguru import logger


class QueryBuilder:
    """Elasticsearch查询构建器"""

    # Text fields that have .keyword subfield
    TEXT_FIELDS_WITH_KEYWORD = {
        "employer", "job_position", "mobile_phone",
        "name", "occupation", "wechat_nickname"
    }

    # Keyword fields (enum values) - require exact match
    KEYWORD_FIELDS = {
        "agent_id", "anyouhu_level", "asset_scale", "client_birth",
        "client_birth_month_and_day", "customer_added_date", "customer_id",
        "customer_segment_tag", "customer_temperature", "customer_value",
        "department", "education", "email", "gender", "health_care_level",
        "health_insurance", "height", "held_cross_sell_category",
        "held_product_category", "held_product_type", "home_care_level",
        "investable_assets", "is_cross_sell_claim", "is_life_insured",
        "is_payment_matured", "is_survival_gold_claimed", "latest_underwriting_time",
        "life_design_type", "life_insurance_product", "life_insurance_vip",
        "life_liability_type", "marital_status", "nationality", "operation_stage",
        "pension_insurance_product", "pingan_vip", "policy_anniversary",
        "policy_expiry_date", "property_insurance_product", "prospect_source",
        "real_estate_status", "stock_customer_type", "target_purchase_category",
        "total_coverage", "valid_short_term_policy", "vehicle_model",
        "vehicle_plate_number", "vehicle_purchase_price", "weight",
        "work_phone", "years_in_service", "zhenxiang_family_level"
    }

    # Nested field paths (for automatic nested query detection)
    NESTED_PATHS = {
        "certificates", "family_members", "policies",
        "benefits.member_info", "benefits.pingan_info"
    }

    # 双层嵌套路径：嵌套对象内部还有嵌套列表
    # key: 内层嵌套路径, value: 外层嵌套路径
    DOUBLE_NESTED_PATHS = {
        "policies.coverage_details": "policies",
        "policies.claim_records": "policies",
    }

    @staticmethod
    def _detect_nested(field: str):
        """
        检测字段的嵌套层级
        返回 (outer_path, inner_path, nested_field)
        - outer_path: 外层嵌套路径（必有）
        - inner_path: 内层嵌套路径（双层嵌套时有，单层为None）
        - nested_field: 最终字段名
        """
        # 优先检查双层嵌套（按路径长度降序）
        for inner_path, outer_path in sorted(
            QueryBuilder.DOUBLE_NESTED_PATHS.items(), key=lambda x: len(x[0]), reverse=True
        ):
            if field.startswith(inner_path + '.'):
                nested_field = field[len(inner_path) + 1:]
                return outer_path, inner_path, nested_field

        # 再检查单层嵌套（按路径长度降序，优先匹配最长路径）
        for path in sorted(QueryBuilder.NESTED_PATHS, key=len, reverse=True):
            if field.startswith(path + '.'):
                nested_field = field[len(path) + 1:]
                return path, None, nested_field

        return None, None, None

    # Nested text-type sub-fields (non-enum values) - use fuzzy match for MATCH operator
    NESTED_TEXT_FIELDS = {
        "name",          # family_members.name, coverage_details.name
        "id_number",     # certificates.id_number
        "product_name",  # policies.product_name
        "policy_id",     # policies.policy_id
        "benefit_intro"  # benefits.*.benefit_intro
    }

    @staticmethod
    def build_query(agent_id: str, conditions: List[Condition], query_logic: QueryLogicEnum) -> Dict[str, Any]:
        """
        构建ES查询DSL

        Args:
            agent_id: 代理人ID（用于权限过滤）
            conditions: 查询条件列表
            query_logic: 条件组合逻辑（AND/OR）

        Returns:
            ES查询DSL字典
        """
        # 基础查询结构
        query = {
            "bool": {
                "must": [
                    # 强制过滤：只查询该代理人的客户
                    {"term": {"agent_id": agent_id}}
                ]
            }
        }

        # 如果没有其他条件，直接返回
        if not conditions:
            return query

        # 根据逻辑类型构建条件
        if query_logic == QueryLogicEnum.AND:
            # AND逻辑：所有条件都必须满足
            for condition in conditions:
                clause = QueryBuilder._build_condition(condition)
                if clause:
                    query["bool"]["must"].append(clause)
        else:
            # OR逻辑：任一条件满足即可
            should_clauses = []
            for condition in conditions:
                clause = QueryBuilder._build_condition(condition)
                if clause:
                    should_clauses.append(clause)

            if should_clauses:
                query["bool"]["must"].append({
                    "bool": {
                        "should": should_clauses,
                        "minimum_should_match": 1
                    }
                })

        logger.debug(f"Built ES query: {query}")
        return query

    @staticmethod
    def _build_condition(condition: Condition) -> Dict[str, Any]:
        """
        构建单个查询条件

        Args:
            condition: 查询条件

        Returns:
            ES查询子句
        """
        field = condition.field
        operator = condition.operator
        value = condition.value

        try:
            if operator in (OperatorEnum.MATCH, OperatorEnum.NESTED_MATCH):
                # 自动检测是否为嵌套字段（NESTED_MATCH 已合并入 MATCH）
                outer_path, inner_path, nested_field = QueryBuilder._detect_nested(field)
                if outer_path:
                    return QueryBuilder._build_nested_query(field, value, condition.nested_path)

                # 否则使用普通match查询
                return QueryBuilder._build_match_query(field, value)

            elif operator == OperatorEnum.GTE:
                outer_path, _, _ = QueryBuilder._detect_nested(field)
                if outer_path:
                    return QueryBuilder._build_nested_query(field, {"min": value}, None)
                return {"range": {field: {"gte": value}}}

            elif operator == OperatorEnum.LTE:
                outer_path, _, _ = QueryBuilder._detect_nested(field)
                if outer_path:
                    return QueryBuilder._build_nested_query(field, {"max": value}, None)
                return {"range": {field: {"lte": value}}}

            elif operator == OperatorEnum.RANGE:
                outer_path, _, _ = QueryBuilder._detect_nested(field)
                if outer_path:
                    return QueryBuilder._build_nested_query(field, value, None)

                # 普通字段：支持数组格式: [min, max]
                if isinstance(value, (list, tuple)) and len(value) == 2:
                    return {"range": {field: {"gte": value[0], "lte": value[1]}}}

                # 支持字典格式: {"min": x, "max": y}
                elif isinstance(value, dict) and ('min' in value or 'max' in value):
                    range_query = {}
                    if 'min' in value:
                        range_query['gte'] = value['min']
                    if 'max' in value:
                        range_query['lte'] = value['max']
                    return {"range": {field: range_query}}

                else:
                    raise InvalidQueryError(
                        f"RANGE operator requires [min, max] or {{'min': x, 'max': y}} format, got: {value}"
                    )

            elif operator == OperatorEnum.CONTAINS:
                outer_path, _, _ = QueryBuilder._detect_nested(field)
                if outer_path:
                    if isinstance(value, list):
                        should_clauses = [QueryBuilder._build_nested_query(field, v, None) for v in value]
                        return {"bool": {"should": should_clauses, "minimum_should_match": 1}}
                    return QueryBuilder._build_nested_query(field, value, None)

                # 普通字段：支持单值(term)和多值(terms)
                term_field = f"{field}.keyword" if field in QueryBuilder.TEXT_FIELDS_WITH_KEYWORD else field
                if isinstance(value, list):
                    return {"terms": {term_field: value}}
                return {"term": {term_field: value}}

            elif operator == OperatorEnum.NOT_CONTAINS:
                outer_path, _, _ = QueryBuilder._detect_nested(field)
                if outer_path:
                    if isinstance(value, list):
                        should_clauses = [QueryBuilder._build_nested_query(field, v, None) for v in value]
                        return {"bool": {"must_not": [{"bool": {"should": should_clauses, "minimum_should_match": 1}}]}}
                    nested_query = QueryBuilder._build_nested_query(field, value, None)
                    return {"bool": {"must_not": [nested_query]}}

                # 普通字段：支持单值和多值
                term_field = f"{field}.keyword" if field in QueryBuilder.TEXT_FIELDS_WITH_KEYWORD else field
                if isinstance(value, list):
                    return {"bool": {"must_not": [{"terms": {term_field: value}}]}}
                return {"bool": {"must_not": [{"term": {term_field: value}}]}}

            elif operator == OperatorEnum.EXISTS:
                outer_path, inner_path, nested_field = QueryBuilder._detect_nested(field)
                if outer_path:
                    if inner_path:
                        return {
                            "nested": {
                                "path": outer_path,
                                "query": {"nested": {
                                    "path": inner_path,
                                    "query": {"exists": {"field": f"{inner_path}.{nested_field}"}}
                                }}
                            }
                        }
                    return {
                        "nested": {
                            "path": outer_path,
                            "query": {"exists": {"field": f"{outer_path}.{nested_field}"}}
                        }
                    }
                return {"exists": {"field": field}}

            elif operator == OperatorEnum.NOT_EXISTS:
                outer_path, inner_path, nested_field = QueryBuilder._detect_nested(field)
                if outer_path:
                    if inner_path:
                        return {"bool": {"must_not": [{"nested": {
                            "path": outer_path,
                            "query": {"nested": {
                                "path": inner_path,
                                "query": {"exists": {"field": f"{inner_path}.{nested_field}"}}
                            }}
                        }}]}}
                    return {"bool": {"must_not": [{"nested": {
                        "path": outer_path,
                        "query": {"exists": {"field": f"{outer_path}.{nested_field}"}}
                    }}]}}
                return {"bool": {"must_not": [{"exists": {"field": field}}]}}

            else:
                raise InvalidQueryError(f"Unsupported operator: {operator}")

        except Exception as e:
            logger.error(f"Failed to build condition: {condition}, error: {e}")
            raise InvalidQueryError(f"Invalid condition: {e}")

    @staticmethod
    def _build_nested_query(field: str, value: Any, nested_path: str = None) -> Dict[str, Any]:
        """
        构建嵌套字段查询，支持单层和双层嵌套

        Args:
            field: 字段名，支持点号表示法（如 "policies.coverage_details.type"）
            value: 查询值
            nested_path: 嵌套路径（可选，优先使用自动检测）

        Returns:
            ES嵌套查询
        """
        # 优先使用自动检测
        outer_path, inner_path, nested_field = QueryBuilder._detect_nested(field)

        # 兼容旧的 nested_path 参数方式
        if not outer_path and nested_path:
            outer_path = nested_path
            nested_field = field

        if not outer_path:
            raise InvalidQueryError("Nested query requires nested_path parameter or dot notation (e.g., 'certificates.id_number')")

        # 双层嵌套：构建内层查询后包裹外层
        if inner_path:
            inner_query = QueryBuilder._build_leaf_query(f"{inner_path}.{nested_field}", nested_field, value)
            return {
                "nested": {
                    "path": outer_path,
                    "query": {
                        "nested": {
                            "path": inner_path,
                            "query": inner_query
                        }
                    }
                }
            }

        # 单层嵌套
        leaf_query = QueryBuilder._build_leaf_query(f"{outer_path}.{nested_field}", nested_field, value)
        return {
            "nested": {
                "path": outer_path,
                "query": leaf_query
            }
        }

    @staticmethod
    def _build_leaf_query(full_field: str, leaf_field: str, value: Any) -> Dict[str, Any]:
        """构建嵌套查询的叶子节点查询"""
        # range查询
        if isinstance(value, dict) and ('min' in value or 'max' in value):
            range_query = {}
            if 'min' in value:
                range_query['gte'] = value['min']
            if 'max' in value:
                range_query['lte'] = value['max']
            return {"range": {full_field: range_query}}

        # 字段为空查询
        if value is None:
            return {
                "bool": {
                    "should": [
                        {"bool": {"must_not": [{"exists": {"field": full_field}}]}},
                        {"term": {full_field: ""}}
                    ],
                    "minimum_should_match": 1
                }
            }

        # 身份证号、保单号：wildcard模糊匹配
        if leaf_field in ["id_number", "policy_id"]:
            return {
                "bool": {
                    "should": [
                        {"term": {f"{full_field}.keyword": {"value": value, "boost": 100}}},
                        {"prefix": {f"{full_field}.keyword": {"value": value, "boost": 50}}},
                        {"wildcard": {f"{full_field}.keyword": {"value": f"*{value}*", "boost": 10}}}
                    ],
                    "minimum_should_match": 1
                }
            }

        # 非枚举文本字段：模糊匹配
        if leaf_field in QueryBuilder.NESTED_TEXT_FIELDS:
            return {"match": {full_field: {"query": value, "fuzziness": "AUTO"}}}

        # 枚举字段：精确匹配
        return {"term": {full_field: value}}

    @staticmethod
    def _build_match_query(field: str, value: Any) -> Dict[str, Any]:
        """
        构建智能匹配查询（根据字段类型选择最佳策略）

        规则：
        - keyword类型字段（枚举值）：精确匹配（term query）
        - text类型字段：模糊匹配（match query with fuzziness）

        Args:
            field: 字段名
            value: 查询值

        Returns:
            ES匹配查询
        """
        # 如果value为None，查询该字段不存在或为空
        if value is None:
            return {
                "bool": {
                    "should": [
                        {"bool": {"must_not": [{"exists": {"field": field}}]}},
                        {"term": {field: ""}}
                    ],
                    "minimum_should_match": 1
                }
            }

        # keyword类型字段：精确匹配
        if field in QueryBuilder.KEYWORD_FIELDS:
            return {"term": {field: value}}

        # 姓名：中文+拼音模糊匹配
        if field == "name":
            return {
                "bool": {
                    "should": [
                        # 精确匹配（最高权重）
                        {"term": {"name.keyword": {"value": value, "boost": 100}}},
                        # 中文模糊匹配（高权重）
                        {"match": {"name": {"query": value, "fuzziness": "AUTO", "boost": 50}}},
                        # 拼音模糊匹配（高权重，支持拼音相似度）
                        {"match": {"name.pinyin": {"query": value, "fuzziness": "AUTO", "boost": 50}}},
                        # 前缀匹配（中等权重）
                        {"prefix": {"name": {"value": value, "boost": 20}}},
                        # 包含匹配（最低权重）
                        {"wildcard": {"name": {"value": f"*{value}*", "boost": 1}}}
                    ],
                    "minimum_should_match": 1
                }
            }

        # 手机号：wildcard模糊匹配
        elif field == "mobile_phone":
            return {
                "bool": {
                    "should": [
                        # 精确匹配（最高权重）
                        {"term": {"mobile_phone.keyword": {"value": value, "boost": 100}}},
                        # 前缀匹配（高权重）
                        {"prefix": {"mobile_phone.keyword": {"value": value, "boost": 50}}},
                        # 包含匹配（中等权重）
                        {"wildcard": {"mobile_phone.keyword": {"value": f"*{value}*", "boost": 10}}}
                    ],
                    "minimum_should_match": 1
                }
            }

        # 地址：中文分词匹配
        elif field in ["contact_address", "home_address", "work_address"]:
            return {
                "match": {
                    field: {
                        "query": value,
                        "analyzer": "ik_max_word"
                    }
                }
            }

        # 其他text字段：标准模糊匹配
        else:
            return {"match": {field: {"query": value, "fuzziness": "AUTO"}}}

    @staticmethod
    def build_sort(sort_orders: List[Any]) -> List[Dict[str, Any]]:
        """
        构建排序条件

        Args:
            sort_orders: 排序条件列表

        Returns:
            ES排序DSL列表
        """
        if not sort_orders:
            return [{"_score": {"order": "desc"}}]

        es_sort = []
        for sort_order in sort_orders:
            es_sort.append({sort_order.field: {"order": sort_order.order}})

        return es_sort
