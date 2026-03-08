#!/usr/bin/env python3
"""
客户搜索系统 - 真实场景测试脚本
基于94条代理人原始搜索诉求生成的测试用例
"""

import requests
import json
import time
from typing import Dict, List, Any
from datetime import datetime
import sys

# API配置
API_BASE_URL = "http://localhost:8001"
SEARCH_ENDPOINT = f"{API_BASE_URL}/api/v1/search/customer"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

# 测试配置
TEST_AGENT_ID = "A000001"
TIMEOUT = 10  # 请求超时时间（秒）

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text: str):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def check_health() -> bool:
    """检查API服务健康状态"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            print_success("API服务健康检查通过")
            return True
        else:
            print_error(f"API服务健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"无法连接到API服务: {e}")
        return False

def execute_search(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """执行搜索请求"""
    try:
        start_time = time.time()
        response = requests.post(
            SEARCH_ENDPOINT,
            json=test_case["query"],
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒

        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response_time": elapsed_time,
            "data": response.json() if response.status_code == 200 else None,
            "error": response.text if response.status_code != 200 else None
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": 0,
            "response_time": 0,
            "data": None,
            "error": str(e)
        }

def validate_result(result: Dict[str, Any], test_case: Dict[str, Any]) -> bool:
    """验证测试结果"""
    if not result["success"]:
        return False

    data = result["data"]
    if not data or "data" not in data:
        return False

    # 检查响应时间
    max_time = test_case.get("max_response_time", 200)
    if result["response_time"] > max_time:
        print_warning(f"响应时间超标: {result['response_time']:.2f}ms > {max_time}ms")

    return True

# ============================================================================
# P0级测试用例（最高优先级）
# ============================================================================

P0_TEST_CASES = [
    {
        "id": "P0-1.1",
        "name": "查找45岁以上未配置养老保险的客户",
        "priority": "P0",
        "scenario": "养老保险产品推广",
        "original_demands": "#4, #11, #16, #17, #23, #46, #66, #86",
        "max_response_time": 50,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 50},
            "query_logic": "AND",
            "conditions": [
                {"field": "age", "operator": "GTE", "value": 45},
                {"field": "held_product_category", "operator": "NOT_CONTAINS", "value": "养老保险"}
            ],
            "sort": [{"field": "age", "order": "desc"}]
        }
    },
    {
        "id": "P0-1.2",
        "name": "查找50岁以上未配置养老保险的客户",
        "priority": "P0",
        "scenario": "高龄养老保险推广",
        "original_demands": "#4",
        "max_response_time": 50,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 50},
            "query_logic": "AND",
            "conditions": [
                {"field": "age", "operator": "GTE", "value": 50},
                {"field": "held_product_category", "operator": "NOT_CONTAINS", "value": "养老保险"}
            ]
        }
    },
    {
        "id": "P0-1.3",
        "name": "查找55岁以下没有重疾险的客户",
        "priority": "P0",
        "scenario": "重疾险产品推广",
        "original_demands": "#78",
        "max_response_time": 50,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 50},
            "query_logic": "AND",
            "conditions": [
                {"field": "age", "operator": "LTE", "value": 55},
                {"field": "held_product_category", "operator": "NOT_CONTAINS", "value": "重疾险"}
            ]
        }
    },
    {
        "id": "P0-1.4",
        "name": "查找55岁以上已配置养老险的客户",
        "priority": "P0",
        "scenario": "养老险客户服务",
        "original_demands": "#79",
        "max_response_time": 50,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 50},
            "query_logic": "AND",
            "conditions": [
                {"field": "age", "operator": "GTE", "value": 55},
                {"field": "held_product_category", "operator": "CONTAINS", "value": "养老保险"}
            ]
        }
    },
    {
        "id": "P0-1.5",
        "name": "查找35岁有小朋友还没配置重疾险的客户",
        "priority": "P0",
        "scenario": "家庭保障产品推广",
        "original_demands": "#74",
        "max_response_time": 50,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 50},
            "query_logic": "AND",
            "conditions": [
                {"field": "age", "operator": "RANGE", "value": {"min": 30, "max": 40}},
                {"field": "marital_status", "operator": "MATCH", "value": "已婚"},
                {"field": "held_product_category", "operator": "NOT_CONTAINS", "value": "重疾险"}
            ]
        }
    },
    {
        "id": "P0-2.1",
        "name": "姓名模糊搜索（单字）",
        "priority": "P0",
        "scenario": "快速查找客户",
        "original_demands": "#2, #3, #64",
        "max_response_time": 30,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 10},
            "conditions": [
                {"field": "name", "operator": "MATCH", "value": "张"}
            ]
        }
    },
    {
        "id": "P0-2.2",
        "name": "手机号片段搜索",
        "priority": "P0",
        "scenario": "通过手机号段查找客户",
        "original_demands": "#36, #41, #72",
        "max_response_time": 30,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 10},
            "conditions": [
                {"field": "mobile_phone", "operator": "MATCH", "value": "138"}
            ]
        }
    },
    {
        "id": "P0-2.3",
        "name": "身份证号搜索",
        "priority": "P0",
        "scenario": "理赔客户快速查询",
        "original_demands": "#10, #54, #72",
        "max_response_time": 30,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 10},
            "conditions": [
                {"field": "id_card", "operator": "MATCH", "value": "110101"}
            ]
        }
    }
]

# ============================================================================
# P1级测试用例（高优先级）
# ============================================================================

P1_TEST_CASES = [
    {
        "id": "P1-3.1",
        "name": "查找二十多岁刚结婚没买保险的客户",
        "priority": "P1",
        "scenario": "新婚家庭保障推广",
        "original_demands": "#15",
        "max_response_time": 100,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 50},
            "query_logic": "AND",
            "conditions": [
                {"field": "age", "operator": "RANGE", "value": {"min": 20, "max": 30}},
                {"field": "marital_status", "operator": "MATCH", "value": "已婚"},
                {"field": "is_life_insured", "operator": "MATCH", "value": "无"}
            ]
        }
    },
    {
        "id": "P1-3.2",
        "name": "查找已婚有车没有百万医疗的客户",
        "priority": "P1",
        "scenario": "高端医疗险推广",
        "original_demands": "#57",
        "max_response_time": 100,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 50},
            "query_logic": "AND",
            "conditions": [
                {"field": "marital_status", "operator": "MATCH", "value": "已婚"},
                {"field": "has_car", "operator": "MATCH", "value": "有"},
                {"field": "held_product_category", "operator": "NOT_CONTAINS", "value": "百万医疗"}
            ]
        }
    },
    {
        "id": "P1-4.1",
        "name": "搜索未购买百万医疗保险的客户",
        "priority": "P1",
        "scenario": "百万医疗险推广",
        "original_demands": "#5, #33, #39, #69",
        "max_response_time": 100,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 100},
            "conditions": [
                {"field": "held_product_category", "operator": "NOT_CONTAINS", "value": "百万医疗"}
            ]
        }
    },
    {
        "id": "P1-4.2",
        "name": "搜索所有万能险客户",
        "priority": "P1",
        "scenario": "万能险客户服务",
        "original_demands": "#7, #33",
        "max_response_time": 100,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 100},
            "conditions": [
                {"field": "held_product_category", "operator": "CONTAINS", "value": "万能险"}
            ]
        }
    },
    {
        "id": "P1-4.3",
        "name": "查找特定产品客户（平安福）",
        "priority": "P1",
        "scenario": "产品客户服务",
        "original_demands": "#18, #82",
        "max_response_time": 100,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 50},
            "conditions": [
                {"field": "life_insurance_product", "operator": "MATCH", "value": "平安福"}
            ]
        }
    },
    {
        "id": "P1-4.4",
        "name": "查找缺医疗险的客户",
        "priority": "P1",
        "scenario": "医疗险产品推广",
        "original_demands": "#35, #73",
        "max_response_time": 100,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 100},
            "conditions": [
                {"field": "held_product_category", "operator": "NOT_CONTAINS", "value": "医疗险"}
            ]
        }
    },
    {
        "id": "P1-5.1",
        "name": "按地址搜索（小区级别）",
        "priority": "P1",
        "scenario": "线下拜访规划",
        "original_demands": "#38, #56, #68, #94",
        "max_response_time": 100,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 100},
            "conditions": [
                {"field": "contact_address", "operator": "MATCH", "value": "朝阳"}
            ]
        }
    },
    {
        "id": "P1-5.2",
        "name": "姓氏+年龄+地址组合搜索",
        "priority": "P1",
        "scenario": "精准客户定位",
        "original_demands": "#22",
        "max_response_time": 100,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 50},
            "query_logic": "AND",
            "conditions": [
                {"field": "name", "operator": "MATCH", "value": "张"},
                {"field": "age", "operator": "RANGE", "value": {"min": 30, "max": 40}},
                {"field": "contact_address", "operator": "MATCH", "value": "朝阳"}
            ]
        }
    }
]

# ============================================================================
# P2级测试用例（中优先级）
# ============================================================================

P2_TEST_CASES = [
    {
        "id": "P2-6.1",
        "name": "按年交保费排序（高价值客户）",
        "priority": "P2",
        "scenario": "高价值客户经营",
        "original_demands": "#1, #40, #63",
        "max_response_time": 200,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 50},
            "query_logic": "AND",
            "conditions": [
                {"field": "annual_premium", "operator": "GTE", "value": 10000}
            ],
            "sort": [{"field": "annual_premium", "order": "desc"}]
        }
    },
    {
        "id": "P2-6.2",
        "name": "查找总保费达到权益标准的客户",
        "priority": "P2",
        "scenario": "客户权益服务",
        "original_demands": "#62",
        "max_response_time": 200,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 50},
            "conditions": [
                {"field": "total_premium", "operator": "GTE", "value": 50000}
            ]
        }
    },
    {
        "id": "P2-6.3",
        "name": "按客户价值等级搜索（A1类客户）",
        "priority": "P2",
        "scenario": "高端客户服务",
        "original_demands": "#77",
        "max_response_time": 200,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 50},
            "conditions": [
                {"field": "customer_value", "operator": "MATCH", "value": "A1类客户"}
            ],
            "sort": [{"field": "annual_premium", "order": "desc"}]
        }
    },
    {
        "id": "P2-7.1",
        "name": "搜索孤儿单客户",
        "priority": "P2",
        "scenario": "孤儿单客户服务",
        "original_demands": "#30, #59, #72",
        "max_response_time": 200,
        "query": {
            "header": {"agent_id": TEST_AGENT_ID, "page": 1, "size": 100},
            "conditions": [
                {"field": "is_orphan_policy", "operator": "MATCH", "value": "是"}
            ]
        }
    }
]

def run_test_suite(test_cases: List[Dict], suite_name: str) -> Dict[str, Any]:
    """运行测试套件"""
    print_header(f"{suite_name} 测试")

    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "total_time": 0,
        "avg_time": 0,
        "max_time": 0,
        "min_time": float('inf'),
        "details": []
    }

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] 测试用例: {test_case['id']}")
        print(f"    名称: {test_case['name']}")
        print(f"    场景: {test_case['scenario']}")
        print(f"    原始需求: {test_case['original_demands']}")

        # 执行测试
        result = execute_search(test_case)

        # 验证结果
        is_valid = validate_result(result, test_case)

        # 更新统计
        if is_valid:
            results["passed"] += 1
            print_success(f"通过 - 响应时间: {result['response_time']:.2f}ms")
            if result["data"] and "data" in result["data"]:
                total = result["data"]["data"].get("total", 0)
                returned = len(result["data"]["data"].get("list", []))
                print_info(f"结果: 总数={total}, 返回={returned}条")
        else:
            results["failed"] += 1
            print_error(f"失败 - {result.get('error', '未知错误')}")

        # 记录详情
        results["details"].append({
            "test_id": test_case["id"],
            "name": test_case["name"],
            "passed": is_valid,
            "response_time": result["response_time"],
            "total_results": result["data"]["data"].get("total", 0) if result["data"] and "data" in result["data"] else 0
        })

        # 更新时间统计
        if result["response_time"] > 0:
            results["total_time"] += result["response_time"]
            results["max_time"] = max(results["max_time"], result["response_time"])
            results["min_time"] = min(results["min_time"], result["response_time"])

    # 计算平均时间
    if results["passed"] > 0:
        results["avg_time"] = results["total_time"] / results["passed"]

    return results

def print_summary(all_results: Dict[str, Dict]):
    """打印测试总结"""
    print_header("测试总结报告")

    total_tests = sum(r["total"] for r in all_results.values())
    total_passed = sum(r["passed"] for r in all_results.values())
    total_failed = sum(r["failed"] for r in all_results.values())
    pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试代理人: {TEST_AGENT_ID}")
    print(f"\n总体统计:")
    print(f"  总测试数: {total_tests}")
    print(f"  通过数: {total_passed}")
    print(f"  失败数: {total_failed}")
    print(f"  通过率: {pass_rate:.1f}%")

    print(f"\n各优先级测试结果:")
    for suite_name, results in all_results.items():
        pass_rate = (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0
        status = "✓" if pass_rate >= 95 else "✗"
        print(f"  {status} {suite_name}:")
        print(f"      通过: {results['passed']}/{results['total']} ({pass_rate:.1f}%)")
        print(f"      平均响应时间: {results['avg_time']:.2f}ms")
        print(f"      最大响应时间: {results['max_time']:.2f}ms")
        print(f"      最小响应时间: {results['min_time']:.2f}ms")

    print(f"\n性能评估:")
    all_avg_times = [r["avg_time"] for r in all_results.values() if r["avg_time"] > 0]
    if all_avg_times:
        overall_avg = sum(all_avg_times) / len(all_avg_times)
        if overall_avg < 50:
            print_success(f"  整体平均响应时间: {overall_avg:.2f}ms - 优秀")
        elif overall_avg < 100:
            print_success(f"  整体平均响应时间: {overall_avg:.2f}ms - 良好")
        elif overall_avg < 200:
            print_warning(f"  整体平均响应时间: {overall_avg:.2f}ms - 一般")
        else:
            print_error(f"  整体平均响应时间: {overall_avg:.2f}ms - 需优化")

    print(f"\n测试结论:")
    if pass_rate >= 95:
        print_success("  系统功能完善，性能优秀，可以投入生产使用！")
    elif pass_rate >= 90:
        print_warning("  系统基本可用，建议修复失败用例后再上线")
    else:
        print_error("  系统存在较多问题，需要进一步优化")

def main():
    """主函数"""
    print_header("客户搜索系统 - 真实场景测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {API_BASE_URL}")
    print(f"测试代理人: {TEST_AGENT_ID}")

    # 健康检查
    print_info("\n执行健康检查...")
    if not check_health():
        print_error("API服务不可用，测试终止")
        sys.exit(1)

    # 运行测试套件
    all_results = {}

    # P0级测试
    all_results["P0级（最高优先级）"] = run_test_suite(P0_TEST_CASES, "P0级（最高优先级）")

    # P1级测试
    all_results["P1级（高优先级）"] = run_test_suite(P1_TEST_CASES, "P1级（高优先级）")

    # P2级测试
    all_results["P2级（中优先级）"] = run_test_suite(P2_TEST_CASES, "P2级（中优先级）")

    # 打印总结
    print_summary(all_results)

    # 保存测试报告
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print_info(f"\n测试报告已保存: {report_file}")

if __name__ == "__main__":
    main()
