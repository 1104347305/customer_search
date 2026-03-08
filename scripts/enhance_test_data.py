#!/usr/bin/env python3
"""
客户搜索系统 - 测试数据增强脚本
基于94条真实需求，生成更符合业务场景的测试数据
"""

import json
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent / "data"
CUSTOMERS_FILE = DATA_DIR / "customers.json"
ENHANCED_FILE = DATA_DIR / "customers_enhanced.json"

# 真实需求场景配置
SCENARIO_CONFIG = {
    # P0场景：年龄段+保险配置（最高频）
    "age_insurance_gap": {
        "weight": 0.30,  # 30%的数据符合这个场景
        "scenarios": [
            {"age_min": 45, "age_max": 65, "missing": "养老保险", "weight": 0.40},
            {"age_min": 50, "age_max": 70, "missing": "养老保险", "weight": 0.25},
            {"age_min": 30, "age_max": 55, "missing": "重疾险", "weight": 0.20},
            {"age_min": 55, "age_max": 100, "has": "养老保险", "weight": 0.15},
        ]
    },

    # P1场景：险种缺口（高频）
    "insurance_gap": {
        "weight": 0.25,
        "scenarios": [
            {"missing": "百万医疗", "weight": 0.35},
            {"missing": "医疗险", "weight": 0.30},
            {"missing": "重疾险", "weight": 0.20},
            {"has": "万能险", "weight": 0.15},
        ]
    },

    # P1场景：家庭情况（高频）
    "family_situation": {
        "weight": 0.20,
        "scenarios": [
            {"age_min": 20, "age_max": 30, "marital": "已婚", "no_insurance": True, "weight": 0.30},
            {"marital": "已婚", "has_car": True, "missing": "百万医疗", "weight": 0.25},
            {"has_children": True, "children_age": (6, 12), "weight": 0.25},  # 小学阶段
            {"has_children": True, "children_age": (3, 5), "weight": 0.20},   # 幼儿阶段
        ]
    },

    # P1场景：地理位置（高频）
    "location_based": {
        "weight": 0.15,
        "locations": [
            {"city": "北京", "district": "朝阳区", "community": "望京", "weight": 0.25},
            {"city": "北京", "district": "海淀区", "community": "中关村", "weight": 0.20},
            {"city": "上海", "district": "浦东新区", "community": "陆家嘴", "weight": 0.20},
            {"city": "深圳", "district": "南山区", "community": "科技园", "weight": 0.15},
            {"city": "大连", "district": "金州区", "community": "金石滩", "weight": 0.10},
            {"city": "广州", "district": "天河区", "community": "珠江新城", "weight": 0.10},
        ]
    },

    # P2场景：高价值客户（中频）
    "high_value": {
        "weight": 0.10,
        "scenarios": [
            {"annual_premium_min": 10000, "customer_value": "A1类客户", "weight": 0.40},
            {"total_premium_min": 50000, "weight": 0.30},
            {"annual_premium_min": 20000, "customer_value": "A1类客户", "weight": 0.30},
        ]
    }
}

# 保险产品配置
INSURANCE_PRODUCTS = {
    "养老保险": ["平安金瑞人生", "国寿鑫福年年", "太平盛世", "泰康幸福有约"],
    "重疾险": ["平安福", "国寿福", "太平福禄", "泰康健康百分百"],
    "医疗险": ["平安e生保", "好医保", "尊享e生", "微医保"],
    "百万医疗": ["平安e生保百万医疗", "好医保长期医疗", "尊享e生2023", "微医保百万医疗"],
    "万能险": ["智胜人生", "智盈人生", "金玉满堂", "财富金账户"],
    "意外险": ["平安综合意外险", "小蜜蜂意外险", "大护甲意外险"],
    "年金险": ["金瑞人生", "鑫福年年", "财富金账户", "盛世臻品"],
    "寿险": ["平安福终身寿", "国寿福终身寿", "太平福禄终身寿"],
}

# 地址模板
ADDRESS_TEMPLATES = {
    "北京": {
        "朝阳区": ["望京街道", "三里屯街道", "CBD街道", "亚运村街道"],
        "海淀区": ["中关村街道", "五道口街道", "上地街道", "清河街道"],
        "东城区": ["东直门街道", "王府井街道", "建国门街道"],
    },
    "上海": {
        "浦东新区": ["陆家嘴街道", "张江街道", "金桥街道", "世纪公园街道"],
        "徐汇区": ["徐家汇街道", "田林街道", "漕河泾街道"],
    },
    "深圳": {
        "南山区": ["科技园街道", "蛇口街道", "南头街道", "粤海街道"],
        "福田区": ["福田街道", "华强北街道", "车公庙街道"],
    },
    "大连": {
        "金州区": ["金石滩街道", "开发区街道", "保税区街道"],
    },
    "广州": {
        "天河区": ["珠江新城街道", "天河北街道", "体育西街道"],
    }
}

def load_customers() -> List[Dict]:
    """加载原始客户数据"""
    print(f"正在加载客户数据: {CUSTOMERS_FILE}")
    with open(CUSTOMERS_FILE, 'r', encoding='utf-8') as f:
        customers = json.load(f)
    print(f"已加载 {len(customers)} 条客户数据")
    return customers

def enhance_age_insurance_gap(customer: Dict, scenario: Dict) -> Dict:
    """增强年龄+保险配置缺口场景"""
    # 设置年龄
    customer["age"] = random.randint(scenario["age_min"], scenario["age_max"])
    customer["client_birth"] = str((datetime.now().year - customer["age"]) * 10000 +
                                   random.randint(101, 1231))

    # 设置保险配置
    if "missing" in scenario:
        # 确保缺少指定险种
        held_categories = customer.get("held_product_category", "").split(",")
        held_categories = [c for c in held_categories if scenario["missing"] not in c]
        customer["held_product_category"] = ",".join(held_categories) if held_categories else ""

        # 清除对应产品
        if scenario["missing"] == "养老保险":
            customer["pension_insurance_product"] = None
        elif scenario["missing"] == "重疾险":
            customer["critical_illness_product"] = None
        elif scenario["missing"] == "医疗险" or scenario["missing"] == "百万医疗":
            customer["medical_insurance_product"] = None

    elif "has" in scenario:
        # 确保拥有指定险种
        held_categories = customer.get("held_product_category", "").split(",")
        if scenario["has"] not in held_categories:
            held_categories.append(scenario["has"])
        customer["held_product_category"] = ",".join([c for c in held_categories if c])

        # 设置对应产品
        if scenario["has"] == "养老保险":
            customer["pension_insurance_product"] = random.choice(INSURANCE_PRODUCTS["养老保险"])

    return customer

def enhance_insurance_gap(customer: Dict, scenario: Dict) -> Dict:
    """增强险种缺口场景"""
    if "missing" in scenario:
        # 确保缺少指定险种
        held_categories = customer.get("held_product_category", "").split(",")
        held_categories = [c for c in held_categories if scenario["missing"] not in c]
        customer["held_product_category"] = ",".join(held_categories) if held_categories else ""

        # 清除对应产品
        if scenario["missing"] == "百万医疗" or scenario["missing"] == "医疗险":
            customer["medical_insurance_product"] = None
        elif scenario["missing"] == "重疾险":
            customer["critical_illness_product"] = None

    elif "has" in scenario:
        # 确保拥有指定险种
        held_categories = customer.get("held_product_category", "").split(",")
        if scenario["has"] not in held_categories:
            held_categories.append(scenario["has"])
        customer["held_product_category"] = ",".join([c for c in held_categories if c])

        # 设置对应产品
        if scenario["has"] == "万能险":
            customer["life_insurance_product"] = random.choice(INSURANCE_PRODUCTS["万能险"])

    return customer

def enhance_family_situation(customer: Dict, scenario: Dict) -> Dict:
    """增强家庭情况场景"""
    # 设置年龄
    if "age_min" in scenario and "age_max" in scenario:
        customer["age"] = random.randint(scenario["age_min"], scenario["age_max"])
        customer["client_birth"] = str((datetime.now().year - customer["age"]) * 10000 +
                                       random.randint(101, 1231))

    # 设置婚姻状况
    if "marital" in scenario:
        customer["marital_status"] = scenario["marital"]

    # 设置是否有车
    if "has_car" in scenario:
        customer["has_car"] = "有" if scenario["has_car"] else "无"

    # 设置保险配置
    if "no_insurance" in scenario and scenario["no_insurance"]:
        customer["is_life_insured"] = "无"
        customer["held_product_category"] = ""
        customer["life_insurance_product"] = None
        customer["pension_insurance_product"] = None
        customer["critical_illness_product"] = None
        customer["medical_insurance_product"] = None

    if "missing" in scenario:
        held_categories = customer.get("held_product_category", "").split(",")
        held_categories = [c for c in held_categories if scenario["missing"] not in c]
        customer["held_product_category"] = ",".join(held_categories) if held_categories else ""

    # 设置子女信息
    if "has_children" in scenario and scenario["has_children"]:
        if "children_age" in scenario:
            age_min, age_max = scenario["children_age"]
            num_children = random.randint(1, 2)
            family_members = []
            for i in range(num_children):
                child_age = random.randint(age_min, age_max)
                family_members.append({
                    "name": f"子女{i+1}",
                    "relationship": "子女",
                    "age": child_age,
                    "has_insurance": random.choice(["有", "无"])
                })
            customer["family_members"] = family_members

    return customer

def enhance_location(customer: Dict, location: Dict) -> Dict:
    """增强地理位置场景"""
    city = location["city"]
    district = location["district"]
    community = location["community"]

    # 选择街道
    if city in ADDRESS_TEMPLATES and district in ADDRESS_TEMPLATES[city]:
        street = random.choice(ADDRESS_TEMPLATES[city][district])
    else:
        street = f"{district}街道"

    # 生成详细地址
    building = random.randint(1, 30)
    unit = random.randint(1, 6)
    room = random.randint(101, 2999)

    address = f"{city}{district}{street}{community}{building}号楼{unit}单元{room}室"

    customer["contact_address"] = address
    customer["home_address"] = address

    return customer

def enhance_high_value(customer: Dict, scenario: Dict) -> Dict:
    """增强高价值客户场景"""
    # 设置年缴保费
    if "annual_premium_min" in scenario:
        customer["annual_premium"] = random.randint(
            scenario["annual_premium_min"],
            scenario["annual_premium_min"] * 3
        )

    # 设置总保费
    if "total_premium_min" in scenario:
        customer["total_premium"] = random.randint(
            scenario["total_premium_min"],
            scenario["total_premium_min"] * 2
        )

    # 设置客户价值
    if "customer_value" in scenario:
        customer["customer_value"] = scenario["customer_value"]
        customer["customer_temperature"] = "高温"

    # 设置收入水平
    customer["annual_income"] = customer["annual_premium"] * random.randint(5, 15)

    # 设置保障额度
    customer["total_coverage"] = customer["annual_premium"] * random.randint(30, 100)

    return customer

def enhance_customers(customers: List[Dict]) -> List[Dict]:
    """增强客户数据"""
    print("\n开始增强客户数据...")
    enhanced_customers = []

    for i, customer in enumerate(customers):
        # 随机选择一个场景进行增强
        rand = random.random()
        cumulative_weight = 0

        # P0场景：年龄+保险配置
        cumulative_weight += SCENARIO_CONFIG["age_insurance_gap"]["weight"]
        if rand < cumulative_weight:
            scenario = random.choices(
                SCENARIO_CONFIG["age_insurance_gap"]["scenarios"],
                weights=[s["weight"] for s in SCENARIO_CONFIG["age_insurance_gap"]["scenarios"]]
            )[0]
            customer = enhance_age_insurance_gap(customer, scenario)

        # P1场景：险种缺口
        cumulative_weight += SCENARIO_CONFIG["insurance_gap"]["weight"]
        if rand < cumulative_weight:
            scenario = random.choices(
                SCENARIO_CONFIG["insurance_gap"]["scenarios"],
                weights=[s["weight"] for s in SCENARIO_CONFIG["insurance_gap"]["scenarios"]]
            )[0]
            customer = enhance_insurance_gap(customer, scenario)

        # P1场景：家庭情况
        cumulative_weight += SCENARIO_CONFIG["family_situation"]["weight"]
        if rand < cumulative_weight:
            scenario = random.choices(
                SCENARIO_CONFIG["family_situation"]["scenarios"],
                weights=[s["weight"] for s in SCENARIO_CONFIG["family_situation"]["scenarios"]]
            )[0]
            customer = enhance_family_situation(customer, scenario)

        # P1场景：地理位置
        cumulative_weight += SCENARIO_CONFIG["location_based"]["weight"]
        if rand < cumulative_weight:
            location = random.choices(
                SCENARIO_CONFIG["location_based"]["locations"],
                weights=[l["weight"] for l in SCENARIO_CONFIG["location_based"]["locations"]]
            )[0]
            customer = enhance_location(customer, location)

        # P2场景：高价值客户
        cumulative_weight += SCENARIO_CONFIG["high_value"]["weight"]
        if rand < cumulative_weight:
            scenario = random.choices(
                SCENARIO_CONFIG["high_value"]["scenarios"],
                weights=[s["weight"] for s in SCENARIO_CONFIG["high_value"]["scenarios"]]
            )[0]
            customer = enhance_high_value(customer, scenario)

        enhanced_customers.append(customer)

        # 显示进度
        if (i + 1) % 10000 == 0:
            print(f"已处理 {i + 1}/{len(customers)} 条数据...")

    print(f"数据增强完成！共处理 {len(enhanced_customers)} 条数据")
    return enhanced_customers

def save_enhanced_customers(customers: List[Dict]):
    """保存增强后的客户数据"""
    print(f"\n正在保存增强数据到: {ENHANCED_FILE}")
    with open(ENHANCED_FILE, 'w', encoding='utf-8') as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)
    print(f"增强数据已保存！文件大小: {ENHANCED_FILE.stat().st_size / 1024 / 1024:.2f} MB")

def print_statistics(customers: List[Dict]):
    """打印数据统计"""
    print("\n" + "="*80)
    print("数据增强统计")
    print("="*80)

    # 年龄分布
    age_45_plus = sum(1 for c in customers if c.get("age", 0) >= 45)
    age_50_plus = sum(1 for c in customers if c.get("age", 0) >= 50)
    age_55_plus = sum(1 for c in customers if c.get("age", 0) >= 55)

    print(f"\n年龄分布:")
    print(f"  45岁以上: {age_45_plus} ({age_45_plus/len(customers)*100:.1f}%)")
    print(f"  50岁以上: {age_50_plus} ({age_50_plus/len(customers)*100:.1f}%)")
    print(f"  55岁以上: {age_55_plus} ({age_55_plus/len(customers)*100:.1f}%)")

    # 保险配置缺口
    no_pension = sum(1 for c in customers if "养老保险" not in c.get("held_product_category", ""))
    no_medical = sum(1 for c in customers if "医疗险" not in c.get("held_product_category", ""))
    no_critical = sum(1 for c in customers if "重疾险" not in c.get("held_product_category", ""))
    has_universal = sum(1 for c in customers if "万能险" in c.get("held_product_category", ""))

    print(f"\n保险配置:")
    print(f"  未配置养老保险: {no_pension} ({no_pension/len(customers)*100:.1f}%)")
    print(f"  未配置医疗险: {no_medical} ({no_medical/len(customers)*100:.1f}%)")
    print(f"  未配置重疾险: {no_critical} ({no_critical/len(customers)*100:.1f}%)")
    print(f"  持有万能险: {has_universal} ({has_universal/len(customers)*100:.1f}%)")

    # 高频场景统计
    age_45_no_pension = sum(1 for c in customers
                            if c.get("age", 0) >= 45 and "养老保险" not in c.get("held_product_category", ""))

    print(f"\n高频场景:")
    print(f"  45岁以上未配置养老保险: {age_45_no_pension} ({age_45_no_pension/len(customers)*100:.1f}%)")

    # 婚姻状况
    married = sum(1 for c in customers if c.get("marital_status") == "已婚")
    print(f"  已婚客户: {married} ({married/len(customers)*100:.1f}%)")

    # 高价值客户
    high_premium = sum(1 for c in customers if c.get("annual_premium", 0) >= 10000)
    a1_customers = sum(1 for c in customers if c.get("customer_value") == "A1类客户")

    print(f"\n高价值客户:")
    print(f"  年缴保费≥1万: {high_premium} ({high_premium/len(customers)*100:.1f}%)")
    print(f"  A1类客户: {a1_customers} ({a1_customers/len(customers)*100:.1f}%)")

    print("\n" + "="*80)

def main():
    """主函数"""
    print("="*80)
    print("客户搜索系统 - 测试数据增强脚本")
    print("基于94条真实需求场景")
    print("="*80)

    # 加载原始数据
    customers = load_customers()

    # 增强数据
    enhanced_customers = enhance_customers(customers)

    # 保存增强数据
    save_enhanced_customers(enhanced_customers)

    # 打印统计
    print_statistics(enhanced_customers)

    print("\n✅ 数据增强完成！")
    print(f"原始数据: {CUSTOMERS_FILE}")
    print(f"增强数据: {ENHANCED_FILE}")
    print("\n下一步:")
    print("1. 运行 python scripts/import_data.py 重新导入数据")
    print("2. 运行 python scripts/test_real_scenarios.py 执行真实场景测试")

if __name__ == "__main__":
    main()
