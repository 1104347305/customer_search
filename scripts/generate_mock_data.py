#!/usr/bin/env python3
"""
Mock数据生成脚本 V2
按照数据demo.txt格式生成1000个代理人和10万个客户数据
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from faker import Faker
from tqdm import tqdm

# 初始化Faker
fake = Faker('zh_CN')
Faker.seed(42)
random.seed(42)

# 数据配置
NUM_AGENTS = 1000
CUSTOMERS_PER_AGENT = 100
TOTAL_CUSTOMERS = NUM_AGENTS * CUSTOMERS_PER_AGENT

# 业务数据枚举值
EDUCATION_LEVELS = ["高中及以下", "大学专科", "大学本科", "硕士研究生", "博士研究生"]
MARITAL_STATUS = ["未婚", "已婚", "离异", "丧偶"]
CUSTOMER_VALUES = ["A1类客户", "A2类客户", "B1类客户", "B2类客户", "C类客户"]
CUSTOMER_TEMPERATURES = ["高温", "中温", "低温", "冰冻"]
CUSTOMER_SEGMENTS = ["邻退小康", "新锐白领", "精致妈妈", "资深中产", "都市蓝领", "小镇青年"]
VIP_LEVELS = ["黄金", "白金", "钻石", "黑金", None]
OPERATION_STAGES = ["新用户", "成长期", "成熟期", "衰退期"]
PINGAN_VIP = ["是", "否"]
IS_LIFE_INSURED = ["仅投保人", "仅被保人", "投被保人", "无"]
STOCK_CUSTOMER_TYPES = ["在职有效客户", "离职有效客户", "在职失效客户", "离职失效客户", "非纯存续单客户"]

LIFE_INSURANCE_PRODUCTS = ["金越司庆版", "平安福", "智胜人生", "金瑞人生", "盛世金越", None]
HELD_PRODUCT_TYPES = ["分红型", "万能型", "投连型", "传统型"]
HELD_PRODUCT_CATEGORIES = ["意外上海保险", "重疾险", "医疗险", "寿险", "年金险"]
PROPERTY_INSURANCE_PRODUCTS = ["车险", "家财险", "企财险", None]
PENSION_INSURANCE_PRODUCTS = ["一年期综合意外保险", "长期意外险", "短期意外险", None]
HEALTH_INSURANCE = ["e生保", "好医保", "尊享e生", "微医保", None]
LIFE_LIABILITY_TYPES = ["寿险", "重疾险", "医疗险", "意外险"]
LIFE_DESIGN_TYPES = ["分红", "万能", "投连", "传统"]
TARGET_PURCHASE_CATEGORIES = ["产险", "寿险", "健康险", "意外险"]

COVERAGE_AMOUNTS = ["10万", "20万", "30万", "50万", "100万", "200万", "500万"]
LATEST_UNDERWRITING_TIMES = ["1年内", "1-2年", "2-3年", "3年以上"]
YES_NO = ["是", "否"]
POLICY_ANNIVERSARIES_RANGES = ["3天内", "7天内", "15天内", "30天内", "3个月内"]
PROSPECT_SOURCES = ["综拓准客", "转介绍", "陌生拜访", "网络营销", "活动获客"]
CROSS_SELL_CATEGORIES = ["车辆交强险", "车辆商业险", "家财险", "企财险"]
VEHICLE_PRICES = ["10万以下", "10-20万", "20-30万", "30-50万", "50万以上"]
CROSS_SELL_CLAIMS = ["综拓理赔报案", "无理赔", "理赔中"]
HOME_CARE_LEVELS = ["居家潜客", "居家会员", "居家VIP"]
HEALTH_CARE_LEVELS = ["预达标会员", "达标会员", "VIP会员"]
ANYOUHU_LEVELS = ["国内版", "国际版", "尊享版"]
ZHENXIANG_FAMILY_LEVELS = ["预达标", "达标", "优享"]
INVESTABLE_ASSETS = ["高净值", "中等净值", "普通"]

POLICY_STATUS = ["缴费有效", "保障中", "已失效", "已退保"]
UNDERWRITING_CONCLUSIONS = ["标准（新契约）", "次标（新契约）", "加费承保", "除外承保", "延期承保"]
COVERAGE_TYPES = ["主险", "附加险"]
RELATIONSHIPS = ["配偶", "子女", "父母", "兄弟姐妹"]
ID_TYPES = ["身份证", "护照", "港澳通行证"]

REAL_ESTATE_STATUS = ["有房", "无房", "租房"]
REAL_VEHICLE_STATUS = ["有车", "没车"]
ASSET_SCALES = ["50万以下", "50-100万", "100-300万", "300-500万", "500-1000万", "1000万以上"]
VEHICLE_MODELS = ["Model Y", "Model 3", "宝马5系", "奔驰E级", "奥迪A6", "凯美瑞", "雅阁", None]


def generate_date_yyyymmdd(start_year: int = 1960, end_year: int = 2010) -> str:
    """生成YYYYMMDD格式日期"""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    return random_date.strftime("%Y%m%d")


def generate_date_mmdd(date_str: str) -> str:
    """从YYYYMMDD提取MM-DD"""
    return f"{date_str[4:6]}-{date_str[6:8]}"


def generate_customer_id() -> str:
    """生成客户ID: C + 10位数字 + 8位日期"""
    return f"C{random.randint(1000000, 9999999)}{datetime.now().strftime('%Y%m%d')}"


def generate_mobile() -> str:
    """生成手机号"""
    prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                '150', '151', '152', '153', '155', '156', '157', '158', '159',
                '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
    return random.choice(prefixes) + ''.join([str(random.randint(0, 9)) for _ in range(8)])


def generate_id_number(birth_date: str) -> str:
    """生成身份证号"""
    # 地区码
    area_codes = ['110101', '310101', '440101', '440301', '330101', '510101', '420101', '320101']
    area_code = random.choice(area_codes)
    # 出生日期
    birth = birth_date
    # 顺序码
    sequence = str(random.randint(100, 999))
    # 校验码
    check_code = random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X'])
    return f"{area_code}{birth}{sequence}{check_code}"


def generate_policy_id() -> str:
    """生成保单号: P + 15位数字"""
    return 'P' + ''.join([str(random.randint(0, 9)) for _ in range(15)])


def generate_family_members(customer_name: str, marital_status: str) -> List[Dict[str, Any]]:
    """生成家庭成员，涵盖多个年龄段"""
    members = []

    # 如果已婚，添加配偶
    if marital_status == "已婚" and random.random() < 0.8:
        birth_date = generate_date_yyyymmdd(1970, 2000)
        age = datetime.now().year - int(birth_date[:4])
        members.append({
            "relationship": "配偶",
            "name": fake.name(),
            "birth_date": birth_date,
            "age": age,
            "mobile": generate_mobile()
        })

    # 随机添加子女，涵盖多个年龄段
    if random.random() < 0.7:
        num_children = random.randint(1, 2)
        for _ in range(num_children):
            # 根据权重分配不同年龄段
            age_group = random.choices(
                ['infant', 'preschool', 'primary', 'middle', 'high', 'college', 'adult'],
                weights=[0.1, 0.15, 0.2, 0.2, 0.15, 0.1, 0.1]
            )[0]

            current_year = datetime.now().year
            if age_group == 'infant':  # 婴幼儿 0-3岁
                birth_year = random.randint(current_year - 3, current_year)
            elif age_group == 'preschool':  # 幼儿园 3-6岁
                birth_year = random.randint(current_year - 6, current_year - 3)
            elif age_group == 'primary':  # 小学 6-12岁
                birth_year = random.randint(current_year - 12, current_year - 6)
            elif age_group == 'middle':  # 中学 12-15岁
                birth_year = random.randint(current_year - 15, current_year - 12)
            elif age_group == 'high':  # 高中 15-18岁
                birth_year = random.randint(current_year - 18, current_year - 15)
            elif age_group == 'college':  # 大学 18-22岁
                birth_year = random.randint(current_year - 22, current_year - 18)
            else:  # 成年 22-30岁
                birth_year = random.randint(current_year - 30, current_year - 22)

            birth_date = generate_date_yyyymmdd(birth_year, birth_year)
            age = datetime.now().year - int(birth_date[:4])
            members.append({
                "relationship": "子女",
                "name": fake.name(),
                "birth_date": birth_date,
                "age": age,
                "mobile": generate_mobile() if age >= 12 and random.random() < 0.5 else None
            })

    # 随机添加父母
    if random.random() < 0.4:
        birth_date = generate_date_yyyymmdd(1940, 1970)
        age = datetime.now().year - int(birth_date[:4])
        members.append({
            "relationship": "父母",
            "name": fake.name(),
            "birth_date": birth_date,
            "age": age,
            "mobile": generate_mobile() if random.random() < 0.5 else None
        })

    return members


def generate_certificates(birth_date: str) -> List[Dict[str, str]]:
    """生成证件信息"""
    return [{
        "id_type": "身份证",
        "id_number": generate_id_number(birth_date)
    }]


def generate_coverage_details(product_name: str, insured_name: str) -> List[Dict[str, str]]:
    """生成保障详情"""
    return [{
        "name": product_name,
        "alias": product_name.split("20")[0] if "20" in product_name else product_name[:5],
        "type": random.choice(COVERAGE_TYPES),
        "insured_person": insured_name
    }]


def generate_claim_records() -> List[Dict[str, Any]]:
    """生成理赔记录"""
    if random.random() < 0.3:  # 30%概率有理赔记录
        num_claims = random.randint(1, 3)
        claims = []
        for _ in range(num_claims):
            claim_date = datetime.now() - timedelta(days=random.randint(30, 1000))
            claims.append({
                "time": claim_date.strftime("%Y-%m-%d"),
                "case_id": f"CL{random.randint(10000000, 99999999)}",
                "amount": round(random.uniform(500, 50000), 2),
                "coverage": random.choice(["门诊医疗", "住院医疗", "重疾", "意外伤害"])
            })
        return claims
    return []


def generate_policies(customer_name: str, mobile: str, has_insurance: bool) -> List[Dict[str, Any]]:
    """生成保单信息"""
    if not has_insurance:
        return []

    num_policies = random.choices([1, 2, 3], weights=[0.5, 0.3, 0.2])[0]
    policies = []

    for _ in range(num_policies):
        product_name = random.choice([
            "平安e生保2023升级版", "平安福2023", "智胜人生",
            "金瑞人生20", "盛世金越", "长相安"
        ])
        effective_date_obj = datetime.now() - timedelta(days=random.randint(365, 3650))
        effective_date = effective_date_obj.strftime("%Y%m%d")
        due_date = (effective_date_obj + timedelta(days=random.randint(3650, 7300))).strftime("%Y%m%d")
        free_look_expiry = (effective_date_obj + timedelta(days=random.choice([15, 20, 30]))).strftime("%Y%m%d")

        policy = {
            "product_name": product_name,
            "policy_id": generate_policy_id(),
            "effective_date": effective_date,
            "status": random.choice(POLICY_STATUS),
            "period_premium": random.choice([3000, 5000, 8000, 10000, 15000, 20000, 30000]),
            "due_date": due_date,
            "underwriting_conclusion": random.choice(UNDERWRITING_CONCLUSIONS),
            "free_look_expiry": free_look_expiry,
            "coverage_details": generate_coverage_details(product_name, customer_name),
            "applicant_name": customer_name,
            "applicant_mobile": mobile,
            "insured_name": customer_name,
            "insured_mobile": mobile,
            "beneficiary_name": fake.name() if random.random() < 0.7 else customer_name,
            "beneficiary_mobile": generate_mobile() if random.random() < 0.7 else mobile,
            "survival_total_amount": random.choice([0, 5000, 10000, 20000]),
            "survival_claimed_amount": 0,
            "survival_unclaimed_amount": 0,
            "universal_acct_transfer": random.choice([0, 1000, 5000, 10000]),
            "survival_interest_total": random.choice([0, 500, 1000, 2000]),
            "claim_records": generate_claim_records()
        }
        policies.append(policy)

    return policies


def generate_benefits() -> Dict[str, List[Dict[str, Any]]]:
    """生成权益信息"""
    benefits = {
        "member_info": [],
        "pingan_info": []
    }

    # 会员信息
    if random.random() < 0.5:
        benefits["member_info"].append({
            "level": random.choice(["黄金V1", "白金V2", "钻石V3"]),
            "validity": (datetime.now() + timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d"),
            "points": random.randint(500, 10000),
            "premium_value": random.choice(["50万", "100万", "200万", "500万"]),
            "exclusive_service": random.choice(YES_NO),
            "proxy_order_auth": random.choice(YES_NO),
            "benefit_name": random.choice(["门诊预约", "专家会诊", "健康体检", "法律咨询"]),
            "benefit_intro": "专属服务介绍",
            "points_cost": f"{random.randint(100, 1000)}积分",
            "benefit_url": f"https://pingan.com/benefit/{random.randint(100, 999)}"
        })

    # 平安服务信息
    if random.random() < 0.4:
        benefits["pingan_info"].append({
            "service_line": random.choice(["居家养老", "健康管理", "财富管理"]),
            "period": f"{datetime.now().year}年期",
            "stage": random.choice(["预达标", "达标", "优享"]),
            "service_level": random.choice(["V1", "V1.5", "V2", "V3"]),
            "benefit_name": random.choice(["长寿管理", "健康咨询", "财富规划"]),
            "benefit_intro": "服务介绍内容",
            "expiry": f"{datetime.now().year}.01.01-{datetime.now().year}.12.31",
            "benefit_url": f"https://pingan.com/service/{random.randint(100, 999)}"
        })

    return benefits


def generate_customer(agent_id: str) -> Dict[str, Any]:
    """生成单个客户数据"""
    # 基础信息
    name = fake.name()
    gender = random.choice(["男", "女"])
    client_birth = generate_date_yyyymmdd(1960, 2005)
    age = datetime.now().year - int(client_birth[:4])
    mobile_phone = generate_mobile()
    marital_status = random.choice(MARITAL_STATUS)
    education = random.choice(EDUCATION_LEVELS)

    # 客户分类信息
    customer_added_date = generate_date_yyyymmdd(2020, 2025)
    has_insurance = random.random() < 0.7

    # 生成客户数据
    customer = {
        "name": name,
        "mobile_phone": mobile_phone,
        "gender": gender,
        "client_birth": client_birth,
        "client_birth_month_and_day": generate_date_mmdd(client_birth),
        "age": age,
        "education": education,
        "marital_status": marital_status,
        "customer_id": generate_customer_id(),
        "customer_added_date": customer_added_date,
        "customer_value": random.choice(CUSTOMER_VALUES),
        "customer_temperature": random.choice(CUSTOMER_TEMPERATURES),
        "customer_segment_tag": random.choice(CUSTOMER_SEGMENTS),
        "life_insurance_vip": random.choice(VIP_LEVELS),
        "operation_stage": random.choice(OPERATION_STAGES),
        "pingan_vip": random.choice(PINGAN_VIP),
        "is_life_insured": random.choice(IS_LIFE_INSURED) if has_insurance else "无",
        "stock_customer_type": random.choice(STOCK_CUSTOMER_TYPES),

        # 保险产品信息
        "life_insurance_product": random.choice(LIFE_INSURANCE_PRODUCTS) if has_insurance else None,
        "held_product_type": random.choice(HELD_PRODUCT_TYPES) if has_insurance else None,
        "held_product_category": random.choice(HELD_PRODUCT_CATEGORIES) if has_insurance else None,
        "property_insurance_product": random.choice(PROPERTY_INSURANCE_PRODUCTS),
        "pension_insurance_product": random.choice(PENSION_INSURANCE_PRODUCTS),
        "health_insurance": random.choice(HEALTH_INSURANCE) if has_insurance else None,
        "life_liability_type": random.choice(LIFE_LIABILITY_TYPES) if has_insurance else None,
        "life_design_type": random.choice(LIFE_DESIGN_TYPES) if has_insurance else None,
        "target_purchase_category": random.choice(TARGET_PURCHASE_CATEGORIES),

        # 保费保额信息
        "annual_premium": random.choice([3000, 5000, 8000, 10000, 15000, 20000, 30000, 50000]) if has_insurance else 0,
        "total_coverage": random.choice(COVERAGE_AMOUNTS) if has_insurance else "0",
        "latest_underwriting_time": random.choice(LATEST_UNDERWRITING_TIMES) if has_insurance else None,
        "is_survival_gold_claimed": random.choice(YES_NO) if has_insurance else "否",
        "is_payment_matured": random.choice(YES_NO) if has_insurance else "否",
        "policy_anniversary": (datetime.now() + timedelta(days=random.randint(-30, 365))).strftime("%Y-%m-%d") if has_insurance else None,

        # 营销相关
        "prospect_source": random.choice(PROSPECT_SOURCES),
        "held_cross_sell_category": random.choice(CROSS_SELL_CATEGORIES) if random.random() < 0.3 else None,
        "vehicle_purchase_price": random.choice(VEHICLE_PRICES) if random.random() < 0.4 else None,
        "is_cross_sell_claim": random.choice(CROSS_SELL_CLAIMS) if random.random() < 0.2 else None,
        "policy_expiry_date": random.choice(POLICY_ANNIVERSARIES_RANGES) if has_insurance else None,
        "valid_short_term_policy": f"{random.randint(10, 99):03d}" if random.random() < 0.3 else None,

        # 服务等级
        "home_care_level": random.choice(HOME_CARE_LEVELS) if random.random() < 0.3 else None,
        "health_care_level": random.choice(HEALTH_CARE_LEVELS) if random.random() < 0.4 else None,
        "anyouhu_level": random.choice(ANYOUHU_LEVELS) if random.random() < 0.2 else None,
        "zhenxiang_family_level": random.choice(ZHENXIANG_FAMILY_LEVELS) if random.random() < 0.3 else None,
        "investable_assets": random.choice(INVESTABLE_ASSETS) if random.random() < 0.2 else None,

        # 家庭成员、证件、保单
        "family_members": generate_family_members(name, marital_status),
        "certificates": generate_certificates(client_birth),
        "policies": generate_policies(name, mobile_phone, has_insurance),

        # 权益信息
        "benefits": generate_benefits(),

        # 联系信息
        "wechat_nickname": fake.user_name() if random.random() < 0.6 else None,
        "email": fake.email() if random.random() < 0.7 else None,
        "nationality": "中国",
        "registered_residence": fake.address()[:20],
        "contact_address": fake.address(),
        "home_address": fake.address(),

        # 身体信息
        "height": f"{random.randint(155, 190)}cm" if random.random() < 0.8 else None,
        "weight": f"{random.randint(45, 95)}kg" if random.random() < 0.8 else None,

        # 职业信息
        "occupation": fake.job(),
        "years_in_service": str(random.randint(1, 30)) if random.random() < 0.8 else None,
        "employer": fake.company() if random.random() < 0.8 else None,
        "work_phone": fake.phone_number() if random.random() < 0.5 else None,
        "department": random.choice(["技术部", "市场部", "销售部", "财务部", "人力资源部"]) if random.random() < 0.6 else None,
        "job_position": fake.job() if random.random() < 0.7 else None,
        "company_address": fake.address() if random.random() < 0.7 else None,

        # 财务信息
        "annual_income": random.choice([50000, 80000, 100000, 150000, 200000, 300000, 500000, 800000, 1000000]),
        "household_income": random.choice([100000, 150000, 200000, 300000, 500000, 800000, 1000000, 1500000]),
        "real_estate_status": random.choice(REAL_ESTATE_STATUS),
        "real_vehicle_status": random.choice(REAL_VEHICLE_STATUS),
        "asset_scale": random.choice(ASSET_SCALES),

        # 车辆信息
        "vehicle_model": random.choice(VEHICLE_MODELS),
        "vehicle_plate_number": f"{''.join(random.choices(['京', '沪', '粤', '浙', '苏'], k=1))}{random.choice(['A', 'B', 'C', 'D'])}{random.randint(10000, 99999)}" if random.random() < 0.4 else None,

        # 代理人ID（用于ES查询过滤）
        "agent_id": agent_id
    }

    return customer


def generate_agents() -> List[Dict[str, Any]]:
    """生成代理人数据"""
    agents = []
    for i in range(NUM_AGENTS):
        agent_id = f"A{str(i).zfill(6)}"
        agent = {
            "agent_id": agent_id,
            "name": fake.name(),
            "mobile": generate_mobile(),
            "email": fake.email(),
            "region": random.choice(["华东", "华南", "华北", "华中", "西南", "西北", "东北"]),
            "created_at": datetime.now().isoformat()
        }
        agents.append(agent)
    return agents


def main():
    """主函数"""
    print("=" * 60)
    print("Mock Data Generation V2 - 按照数据demo.txt格式")
    print("=" * 60)
    print(f"代理人数量: {NUM_AGENTS}")
    print(f"每个代理人客户数: {CUSTOMERS_PER_AGENT}")
    print(f"总客户数: {TOTAL_CUSTOMERS}")
    print("=" * 60)

    # 创建数据目录
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    # 生成代理人数据
    print("\n生成代理人数据...")
    agents = generate_agents()
    agents_file = data_dir / "agents.json"
    with open(agents_file, 'w', encoding='utf-8') as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)
    print(f"✓ 代理人数据已保存: {agents_file}")

    # 生成客户数据
    print("\n生成客户数据...")
    customers = []

    for agent_idx in tqdm(range(NUM_AGENTS), desc="生成客户"):
        agent_id = f"A{str(agent_idx).zfill(6)}"
        for _ in range(CUSTOMERS_PER_AGENT):
            customer = generate_customer(agent_id)
            customers.append(customer)

    # 保存客户数据
    customers_file = data_dir / "customers.json"
    print(f"\n保存客户数据到 {customers_file}...")
    with open(customers_file, 'w', encoding='utf-8') as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)

    print(f"✓ 客户数据已保存: {customers_file}")

    # 统计信息
    print("\n" + "=" * 60)
    print("数据生成完成")
    print("=" * 60)
    print(f"代理人数量: {len(agents)}")
    print(f"客户数量: {len(customers)}")

    # 统计有保险的客户
    insured_customers = sum(1 for c in customers if c.get('policies') and len(c['policies']) > 0)
    total_policies = sum(len(c.get('policies', [])) for c in customers)

    print(f"有保险客户: {insured_customers} ({insured_customers/len(customers)*100:.1f}%)")
    print(f"总保单数: {total_policies}")
    print(f"平均每客户保单数: {total_policies/len(customers):.2f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
