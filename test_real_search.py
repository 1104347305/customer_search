"""测试实际搜索：父母叫李辉"""
from app.core.elasticsearch import ElasticsearchClient
from app.services.query_builder import QueryBuilder
from app.models.request import Condition, QueryLogicEnum, OperatorEnum


def test_search():
    # 初始化ES客户端
    es_client = ElasticsearchClient.get_client()

    # 构建查询条件
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
        agent_id="A000000",
        conditions=conditions,
        query_logic=QueryLogicEnum.AND
    )

    # 执行搜索
    result = es_client.search(
        index="customers",
        body={
            "query": query,
            "size": 20
        }
    )

    print(f"找到 {result['hits']['total']['value']} 条结果\n")

    # 显示结果
    for i, hit in enumerate(result['hits']['hits'], 1):
        customer = hit['_source']
        print(f"--- 结果 {i} ---")
        print(f"客户姓名: {customer.get('name')}")
        print(f"客户ID: {customer.get('customer_id')}")
        print(f"家庭成员:")
        for member in customer.get('family_members', []):
            print(f"  - {member.get('relationship')}: {member.get('name')}")
        print()


if __name__ == "__main__":
    test_search()
