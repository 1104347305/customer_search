#!/usr/bin/env python3
"""
测试脚本 - 验证系统各组件
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_data_generation():
    """测试数据生成"""
    print("=" * 60)
    print("Test 1: Data Generation")
    print("=" * 60)

    data_dir = project_root / "data"
    agents_file = data_dir / "agents.json"
    customers_file = data_dir / "customers.json"

    if not agents_file.exists():
        print("✗ agents.json not found")
        return False

    if not customers_file.exists():
        print("✗ customers.json not found")
        return False

    import json

    with open(agents_file, 'r', encoding='utf-8') as f:
        agents = json.load(f)

    with open(customers_file, 'r', encoding='utf-8') as f:
        customers = json.load(f)

    print(f"✓ Agents loaded: {len(agents)}")
    print(f"✓ Customers loaded: {len(customers)}")

    # 验证数据结构
    if len(agents) != 1000:
        print(f"✗ Expected 1000 agents, got {len(agents)}")
        return False

    if len(customers) != 100000:
        print(f"✗ Expected 100000 customers, got {len(customers)}")
        return False

    # 验证每个客户都有agent_id
    sample_customer = customers[0]
    if 'agent_id' not in sample_customer:
        print("✗ Customer missing agent_id field")
        return False

    print(f"✓ Sample customer ID: {sample_customer['customer_id']}")
    print(f"✓ Sample agent ID: {sample_customer['agent_id']}")
    print(f"✓ Sample customer name: {sample_customer['name']}")

    return True


def test_models():
    """测试数据模型"""
    print("\n" + "=" * 60)
    print("Test 2: Data Models")
    print("=" * 60)

    try:
        from app.models.request import SearchRequest, Condition, OperatorEnum
        from app.models.response import SearchResponse
        from app.models.customer import Customer

        # 测试创建搜索请求
        request = SearchRequest(
            agent_id="A000001",
            page=1,
            size=10,
            conditions=[
                Condition(field="name", operator=OperatorEnum.MATCH, value="张")
            ]
        )

        print(f"✓ SearchRequest created: agent_id={request.agent_id}")
        print(f"✓ Conditions: {len(request.conditions)}")

        return True

    except Exception as e:
        print(f"✗ Model test failed: {e}")
        return False


def test_query_builder():
    """测试查询构建器"""
    print("\n" + "=" * 60)
    print("Test 3: Query Builder")
    print("=" * 60)

    try:
        from app.services.query_builder import QueryBuilder
        from app.models.request import Condition, OperatorEnum, QueryLogicEnum

        # 测试基础查询
        conditions = [
            Condition(field="name", operator=OperatorEnum.MATCH, value="张"),
            Condition(field="age", operator=OperatorEnum.GTE, value=30)
        ]

        query = QueryBuilder.build_query("A000001", conditions, QueryLogicEnum.AND)

        print(f"✓ Query built successfully")
        print(f"✓ Query has 'bool' clause: {'bool' in query}")
        print(f"✓ Query has 'must' clause: {'must' in query.get('bool', {})}")

        # 测试嵌套查询
        nested_condition = Condition(
            field="status",
            operator=OperatorEnum.NESTED_MATCH,
            value="缴费有效",
            nested_path="policies"
        )

        nested_query = QueryBuilder.build_query("A000001", [nested_condition], QueryLogicEnum.AND)
        print(f"✓ Nested query built successfully")

        return True

    except Exception as e:
        print(f"✗ Query builder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_masking():
    """测试数据脱敏"""
    print("\n" + "=" * 60)
    print("Test 4: Data Masking")
    print("=" * 60)

    try:
        from app.services.data_masking import DataMasking

        customer = {
            "name": "张三",
            "mobile_phone": "13812345678",
            "email": "zhangsan@example.com",
            "certificates": [
                {
                    "certificate_type": "身份证",
                    "certificate_number": "110101199001011234"
                }
            ],
            "policies": [
                {
                    "policy_number": "9200111115555555"
                }
            ]
        }

        masked = DataMasking.mask_customer(customer)

        print(f"✓ Original name: {customer['name']} -> Masked: {masked['name']}")
        print(f"✓ Original phone: {customer['mobile_phone']} -> Masked: {masked['mobile_phone']}")
        print(f"✓ Original email: {customer['email']} -> Masked: {masked['email']}")
        print(f"✓ Original ID: {customer['certificates'][0]['certificate_number']} -> Masked: {masked['certificates'][0]['certificate_number']}")
        print(f"✓ Original policy: {customer['policies'][0]['policy_number']} -> Masked: {masked['policies'][0]['policy_number']}")

        return True

    except Exception as e:
        print(f"✗ Data masking test failed: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Customer Search System - Component Tests")
    print("=" * 60 + "\n")

    results = []

    # 运行测试
    results.append(("Data Generation", test_data_generation()))
    results.append(("Data Models", test_models()))
    results.append(("Query Builder", test_query_builder()))
    results.append(("Data Masking", test_data_masking()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
