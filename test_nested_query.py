"""测试嵌套查询合并功能"""
import json
from app.services.query_builder import QueryBuilder
from app.models.request import Condition, QueryLogicEnum, OperatorEnum


def test_family_member_query():
    """测试：父母叫李辉"""
    conditions = [
        Condition(
            field="family_members.relationship",
            operator=OperatorEnum.CONTAINS,
            value="父母"
        ),
        Condition(
            field="family_members.name",
            operator=OperatorEnum.NESTED_MATCH,
            value="李辉"
        )
    ]

    query = QueryBuilder.build_query(
        agent_id="A001",
        conditions=conditions,
        query_logic=QueryLogicEnum.AND
    )

    print("生成的查询DSL:")
    print(json.dumps(query, indent=2, ensure_ascii=False))

    # 检查是否只有一个nested查询
    must_clauses = query["bool"]["must"]
    nested_clauses = [c for c in must_clauses if "nested" in c]

    print(f"\n嵌套查询数量: {len(nested_clauses)}")

    if len(nested_clauses) == 1:
        print("✓ 成功：两个条件合并到一个nested查询中")
        nested_query = nested_clauses[0]["nested"]
        print(f"  路径: {nested_query['path']}")
        print(f"  内部条件数: {len(nested_query['query']['bool']['must'])}")
    else:
        print("✗ 失败：生成了多个独立的nested查询")

    return query


if __name__ == "__main__":
    test_family_member_query()
