#!/usr/bin/env python3
"""
Mock数据生成脚本 V5
10个代理人，每个代理人10000条客户数据
- 枚举值严格按照《客户信息表格定义.docx》
- 每个代理人每个枚举字段全覆盖
- 字段取值符合实际分布（加权概率）
- 字段间存在合理关联（收入/资产/客户价值/年龄等）
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from faker import Faker
from tqdm import tqdm

# ── 初始化 ──────────────────────────────────────────────────────────
fake = Faker('zh_CN')
Faker.seed(42)
random.seed(42)

NUM_AGENTS = 10
CUSTOMERS_PER_AGENT = 10000
TOTAL_CUSTOMERS = NUM_AGENTS * CUSTOMERS_PER_AGENT

# ===== 枚举定义（严格按照《客户信息表格定义.docx》）=====

GENDERS            = ["男", "女", "未知"]
GENDER_WEIGHTS     = [49, 50, 1]

EDUCATION_LEVELS   = ["大学专科", "大学本科", "硕士研究生", "博士研究生", "博士后", "中专", "高中"]
EDUCATION_WEIGHTS  = [22, 32, 12, 4, 1, 11, 18]

MARITAL_STATUS     = ["未婚", "已婚", "离婚", "丧偶", "未知"]
MARITAL_WEIGHTS    = [18, 62, 10, 5, 5]

CUSTOMER_VALUES    = ["A1类客户", "A2类客户", "A3类客户", "A4类客户", "B类客户", "C类客户", "D类客户"]
CUSTOMER_VALUE_W   = [3, 7, 14, 20, 30, 16, 10]

CUSTOMER_TEMPS     = ["高温", "中温", "低温", "冷却"]
CUSTOMER_TEMP_W    = [15, 35, 30, 20]

CUSTOMER_SEGMENTS  = ["焦圈中年", "鸡娃精英", "临退富裕", "富裕祖辈", "邻退小康"]
CUSTOMER_SEG_W     = [25, 20, 22, 18, 15]

LIFE_INS_VIP       = ["全部", "原黄金VIP", "原铂金VIP", "黄金V1", "黄金V2", "黄金V3", "铂金V1", None]
LIFE_INS_VIP_W     = [10, 8, 8, 20, 18, 15, 12, 9]

OPERATION_STAGES   = ["忠诚客户", "客户", "准客户", "用户", "新用户", "其他"]
OP_STAGE_W         = [20, 30, 18, 15, 12, 5]

PINGAN_VIP         = ["是", "否"]
IS_LIFE_INSURED    = ["仅投保人", "仅被保人", "投被保人"]
IS_LIFE_INS_W      = [40, 25, 35]

STOCK_CUST_TYPES   = ["在职有效客户", "纯存续单客户", "非纯存续单客户"]
STOCK_CUST_W       = [50, 30, 20]

HELD_PROD_TYPES    = ["普通型", "分红型", "投资连结型", "万能型"]
HELD_PROD_TYPE_W   = [30, 35, 15, 20]

HELD_PROD_CATS     = ["意外伤害保险", "医疗保险", "定期寿险", "两全保险", "年金保险", "终身寿险"]
HELD_PROD_CAT_W    = [20, 25, 15, 12, 18, 10]

PROP_INS_PRODS     = ["车险", "非车险", None]
PROP_INS_W         = [35, 30, 35]

LIFE_LIAB_TYPES    = ["寿险", "重疾", "意外", "医疗", "财富", "养老"]
LIFE_LIAB_W        = [20, 25, 15, 20, 10, 10]

LIFE_DESIGN_TYPES  = ["分红", "投连", "万能", "普通", "其他"]
LIFE_DESIGN_W      = [30, 12, 22, 30, 6]

TARGET_CATS        = ["产险", "养老险", "健康险", "寿险", "其他"]
TARGET_CAT_W       = [20, 22, 28, 25, 5]

UNDERWRITING_TIMES = ["一年内", "1-2年", "2-3年", "3-5年", "5-10年", "10年以上"]
UNDERWRITING_W     = [25, 20, 18, 17, 12, 8]

YES_NO             = ["是", "否"]

POLICY_EXPIRY_DATES = ["3天内", "3-10天内", "10-30天内", "30-60天内"]
POLICY_EXPIRY_W    = [10, 20, 35, 35]

PROSPECT_SOURCES   = ["综拓准客", "O2O准客", "意健险准客"]
PROSPECT_W         = [45, 35, 20]

CROSS_SELL_CATS    = ["车辆交强险", "车辆商业险", "e生保", "中高端医疗", "合家欢", "家财险", "学平险", None]
CROSS_SELL_W       = [18, 15, 18, 12, 10, 10, 7, 10]

VEHICLE_PRICES     = ["10万以下", "10-20万", "20-30万", "30-50万", "50-80万", "80万以上", None]
VEHICLE_PRICE_W    = [12, 20, 22, 22, 14, 8, 2]

CROSS_SELL_CLAIMS  = ["综拓理赔报案", "综拓理赔结案", None]
CROSS_SELL_CLAIM_W = [20, 25, 55]

SHORT_TERM_POLS    = ["综拓", "O2O", "意健险", None]
SHORT_TERM_W       = [30, 25, 20, 25]

HOME_CARE_LEVELS   = ["居家潜客", "V0.5", "V1", "V1优享", "V2", "V2优享", "V3", "V3优享", None]
HOME_CARE_W        = [20, 12, 15, 12, 12, 10, 8, 6, 5]

HEALTH_CARE_LEVELS = ["预达标会员", "逸享会员", "逸享PLUS会员", "颐享会员",
                      "臻享会员V1", "臻享会员V2", "臻享会员V3", None]
HEALTH_CARE_W      = [20, 15, 12, 15, 12, 10, 8, 8]

ANYOUHU_LEVELS     = ["国际版", "国内版", None]
ANYOUHU_W          = [15, 45, 40]

ZHENXIANG_LEVELS   = ["预达标", "已达标", None]
ZHENXIANG_W        = [25, 35, 40]

REAL_ESTATE_STATUS = ["有房", "没房"]
REAL_ESTATE_W      = [72, 28]

REAL_VEHICLE_STATUS = ["有车", "没车"]
REAL_VEHICLE_W     = [58, 42]

ASSET_SCALES       = ["50万以下", "50-100万", "100-300万", "300-500万", "500-1000万", "1000万以上"]
ASSET_SCALE_W      = [18, 22, 28, 18, 10, 4]

POLICY_STATUS_ALL  = [
    "取消", "死亡理赔", "展期", "缴费有效", "停效", "到期终止",
    "犹豫期退保", "交清", "减额交清", "退保", "转换终止", "失效",
    "终止效率", "免交", "迁出", "人为停效", "效力终止", "预收",
    "拒保", "贷款超停", "死亡有效", "贷款超失", "自垫有效",
    "自垫停效", "自垫失效", "自垫交清", "等待续保"
]
# 缴费有效是最常见状态，其余均匀分布
POLICY_STATUS_W    = [
    1, 1, 2, 50, 5, 4,
    3, 5, 1, 4, 1, 3,
    1, 2, 1, 1, 1, 2,
    1, 1, 1, 1, 2,
    1, 1, 1, 2
]

UNDERWRITING_CONCLUSIONS = ["标准（新契约）", "次标（新契约）", "加费承保", "除外承保", "延期承保"]
UNDERWRITING_CONCL_W     = [65, 15, 8, 7, 5]

COVERAGE_TYPES     = ["主险", "附加险"]
RELATIONSHIPS      = ["配偶", "父母", "子女", "其他"]
ID_TYPES           = ["身份证", "护照", "军官证", "回乡证", "其他"]
ID_TYPE_W          = [88, 5, 2, 3, 2]

MEMBER_INFO_LEVELS = ["全部", "原黄金VIP", "原铂金VIP", "黄金V1", "黄金V2", "黄金V3", "铂金V1"]
PINGAN_STAGES      = ["达标", "未达标"]
PINGAN_SVC_LEVELS  = ["V1.5", "V0", "V1", "V2", "V3"]

# 职业：固定枚举（按文档要求），加权分布
OCCUPATIONS        = [
    "老师", "医生", "护士", "律师", "程序员", "企业家",
    "工程师", "会计师", "销售员", "公务员", "教授", "研究员",
    "设计师", "记者", "厨师", "司机", "警察", "军人",
    "农民", "工人", "自由职业者", "退休人员", "学生", "个体户",
    "金融分析师", "投资顾问", "建筑师", "药剂师", "心理咨询师"
]
OCCUPATION_W       = [
    8, 6, 5, 4, 7, 4,
    7, 5, 6, 5, 3, 3,
    4, 2, 3, 4, 3, 2,
    4, 5, 6, 4, 3, 5,
    3, 2, 2, 2, 2
]

# 真实车型
VEHICLE_MODELS_REAL = [
    "特斯拉Model Y", "特斯拉Model 3", "比亚迪汉EV", "比亚迪宋Plus", "比亚迪海豹",
    "宝马3系", "宝马5系", "宝马X5", "奔驰C级", "奔驰E级", "奔驰GLC",
    "奥迪A4L", "奥迪A6L", "奥迪Q5L",
    "丰田凯美瑞", "丰田RAV4荣放", "丰田汉兰达",
    "本田雅阁", "本田CR-V", "本田思域",
    "大众帕萨特", "大众途观L", "大众迈腾",
    "别克GL8", "别克君越", "雪佛兰探界者",
    "日产天籁", "马自达6", "沃尔沃XC60",
    "理想L9", "小鹏G9", "蔚来ES6",
]

# 真实中文部门名称
DEPARTMENTS = [
    "技术研发部", "产品设计部", "市场营销部", "销售业务部", "财务管理部",
    "人力资源部", "行政管理部", "运营管理部", "客户服务部", "法务合规部",
    "采购供应链部", "风险管控部", "战略发展部", "品牌公关部", "信息技术部",
]

# 真实职位名称
JOB_POSITIONS = [
    "总经理", "副总经理", "董事长助理", "部门总监", "部门经理",
    "项目经理", "高级工程师", "工程师", "高级顾问", "顾问",
    "主任", "副主任", "高级专员", "专员", "主管",
    "组长", "分析师", "高级分析师", "助理", "实习生",
]

LIFE_INS_PRODUCTS  = [
    "金越司庆版", "平安福", "智胜人生", "金瑞人生", "盛世金越",
    "盛世金越25", "守护百分百26", "平安e生保2023升级版", "长相安", None
]
PENSION_PRODUCTS   = ["御享财富养老", "一年期综合意外保险", "长期意外险", "短期意外险", None]
HEALTH_PRODUCTS    = ["e生保", "好医保", "尊享e生", "微医保", None]

POLICY_PRODUCTS    = [
    "平安e生保2023升级版", "e生保", "守护重疾26", "金尊分红26",
    "颐享世家26", "安佑福", "颐享延年26", "平安福2023", "智胜人生",
    "金越司庆版", "盛世金越25", "长相安",
]
COVERAGE_AMOUNTS   = ["10万", "20万", "30万", "50万", "100万", "200万", "500万"]

# 收入区间与客户价值映射（A1最高→A4中等→D最低）
_VALUE_INCOME_MAP = {
    "A1类客户": ([500000, 800000, 1000000, 2000000], [20, 35, 30, 15]),
    "A2类客户": ([300000, 500000, 800000, 1000000], [25, 35, 25, 15]),
    "A3类客户": ([200000, 300000, 500000, 800000], [30, 35, 25, 10]),
    "A4类客户": ([150000, 200000, 300000, 500000], [30, 35, 25, 10]),
    "B类客户":  ([100000, 150000, 200000, 300000], [30, 35, 25, 10]),
    "C类客户":  ([80000,  100000, 150000, 200000], [35, 35, 20, 10]),
    "D类客户":  ([50000,  80000,  100000, 150000], [40, 35, 20,  5]),
}
_VALUE_ASSET_MAP = {
    "A1类客户": ["500-1000万", "1000万以上"],
    "A2类客户": ["300-500万", "500-1000万", "1000万以上"],
    "A3类客户": ["100-300万", "300-500万", "500-1000万"],
    "A4类客户": ["100-300万", "300-500万"],
    "B类客户":  ["50-100万", "100-300万"],
    "C类客户":  ["50万以下", "50-100万"],
    "D类客户":  ["50万以下"],
}

# 年龄段分布（面向保险市场的现实分布）
_AGE_GROUPS = [
    (1961, 1976, 28),   # 50-65岁：存量高价值老客
    (1976, 1991, 40),   # 35-50岁：核心家庭责任期
    (1991, 2001, 22),   # 25-35岁：新兴青年客户
    (2001, 2008,  10),  # 18-25岁：学生/初入职场
]


# ── 工具函数 ──────────────────────────────────────────────────────────

def make_pool(values: list, count: int) -> list:
    """均匀覆盖值池：确保每个取值至少出现一次，整体均匀分布"""
    repeats = count // len(values) + 1
    pool = (values * repeats)[:count]
    random.shuffle(pool)
    return pool


def make_weighted_pool(values: list, weights: list, count: int) -> list:
    """加权覆盖值池：确保每个取值至少出现一次，按权重填充剩余位置"""
    pool = list(values)                         # 先各放一个，保证覆盖
    remaining = count - len(values)
    if remaining > 0:
        pool.extend(random.choices(values, weights=weights, k=remaining))
    random.shuffle(pool)
    return pool


def weighted_choice(values: list, weights: list):
    return random.choices(values, weights=weights, k=1)[0]


def generate_birth_date() -> str:
    """按真实年龄分布生成出生日期"""
    groups, gweights = zip(*[(g[:2], g[2]) for g in _AGE_GROUPS])
    start_y, end_y = random.choices(groups, weights=gweights, k=1)[0]
    start = datetime(start_y, 1, 1)
    end   = datetime(end_y, 12, 31)
    d = start + timedelta(days=random.randint(0, (end - start).days))
    return d.strftime("%Y%m%d")


def generate_date_mmdd(date_str: str) -> str:
    return f"{date_str[4:6]}-{date_str[6:8]}"


_customer_id_counter = 0

def generate_customer_id() -> str:
    global _customer_id_counter
    _customer_id_counter += 1
    return f"C{str(_customer_id_counter).zfill(8)}{datetime.now().strftime('%Y%m%d')}"


def generate_mobile() -> str:
    prefixes = [
        '130','131','132','133','134','135','136','137','138','139',
        '150','151','152','153','155','156','157','158','159',
        '180','181','182','183','184','185','186','187','188','189',
        '176','177','178',
    ]
    return random.choice(prefixes) + ''.join(str(random.randint(0, 9)) for _ in range(8))


def generate_id_number(birth_date: str, id_type: str) -> str:
    if id_type != "身份证":
        # 护照/军官证等，简单生成
        prefix = {"护照": "E", "军官证": "军", "回乡证": "H", "其他": "X"}.get(id_type, "X")
        return prefix + ''.join(str(random.randint(0, 9)) for _ in range(8))
    area_codes = ['110101','310101','440101','440301','330101',
                  '510101','420101','320101','610101','500101']
    area  = random.choice(area_codes)
    seq   = str(random.randint(100, 999))
    check = random.choice('0123456789X')
    return f"{area}{birth_date}{seq}{check}"


def generate_policy_id() -> str:
    return 'P' + ''.join(str(random.randint(0, 9)) for _ in range(15))


def generate_income_from_value(customer_value: str) -> int:
    incomes, weights = _VALUE_INCOME_MAP.get(customer_value, ([100000], [1]))
    return weighted_choice(incomes, weights)


def generate_asset_from_value(customer_value: str) -> str:
    assets = _VALUE_ASSET_MAP.get(customer_value, ASSET_SCALES)
    return random.choice(assets)


# ── 嵌套对象生成 ─────────────────────────────────────────────────────

def generate_family_members(marital_status: str, age: int) -> List[Dict[str, Any]]:
    members = []
    if marital_status == "已婚" and random.random() < 0.85:
        bd = generate_birth_date()
        members.append({
            "relationship": "配偶",
            "name": fake.name(),
            "birth_date": bd,
            "age": datetime.now().year - int(bd[:4]),
            "mobile": generate_mobile()
        })
    # 子女：35岁以上较可能有孩子
    child_prob = 0.8 if age >= 35 else 0.4
    if random.random() < child_prob:
        for _ in range(random.randint(1, 2)):
            current_year = datetime.now().year
            child_age = random.randint(1, min(age - 20, 30)) if age > 22 else 1
            child_birth_year = current_year - child_age
            bd = (datetime(child_birth_year, 1, 1) +
                  timedelta(days=random.randint(0, 364))).strftime("%Y%m%d")
            members.append({
                "relationship": "子女",
                "name": fake.name(),
                "birth_date": bd,
                "age": child_age,
                "mobile": generate_mobile() if child_age >= 14 and random.random() < 0.6 else None
            })
    # 父母：45岁以上有记录的概率更高
    if age >= 45 and random.random() < 0.5:
        bd = generate_date_yyyymmdd_range(1940, 1970)
        members.append({
            "relationship": "父母",
            "name": fake.name(),
            "birth_date": bd,
            "age": datetime.now().year - int(bd[:4]),
            "mobile": generate_mobile() if random.random() < 0.5 else None
        })
    # 其他（兄弟姐妹/保姆等）
    if random.random() < 0.05:
        bd = generate_birth_date()
        members.append({
            "relationship": "其他",
            "name": fake.name(),
            "birth_date": bd,
            "age": datetime.now().year - int(bd[:4]),
            "mobile": generate_mobile() if random.random() < 0.4 else None
        })
    return members


def generate_date_yyyymmdd_range(start_year: int, end_year: int) -> str:
    start = datetime(start_year, 1, 1)
    end   = datetime(end_year, 12, 31)
    d = start + timedelta(days=random.randint(0, (end - start).days))
    return d.strftime("%Y%m%d")


def generate_certificates(birth_date: str, id_type: str) -> List[Dict[str, str]]:
    return [{
        "id_type": id_type,
        "id_number": generate_id_number(birth_date, id_type)
    }]


def generate_coverage_details(product_name: str, insured_name: str) -> List[Dict[str, str]]:
    return [{
        "name": product_name,
        "alias": product_name[:4],
        "type": weighted_choice(COVERAGE_TYPES, [60, 40]),
        "insured_person": insured_name
    }]


def generate_claim_records() -> List[Dict[str, Any]]:
    if random.random() > 0.25:
        return []
    claims = []
    for _ in range(random.randint(1, 3)):
        claim_date = datetime.now() - timedelta(days=random.randint(30, 1500))
        claims.append({
            "time": claim_date.strftime("%Y-%m-%d"),
            "case_id": f"CL{random.randint(10000000, 99999999)}",
            "amount": round(random.uniform(500, 100000), 2),
            "coverage": random.choice(["门诊医疗", "住院医疗", "重疾", "意外伤害", "身故"])
        })
    return claims


def generate_policies(customer_name: str, mobile: str,
                      has_insurance: bool, annual_premium: int) -> List[Dict[str, Any]]:
    if not has_insurance:
        return []
    num_policies = random.choices([1, 2, 3, 4], weights=[45, 30, 18, 7])[0]
    policies = []
    for _ in range(num_policies):
        product_name = random.choice(POLICY_PRODUCTS)
        days_ago = random.randint(180, 5000)
        eff_date_obj = datetime.now() - timedelta(days=days_ago)
        eff_date = eff_date_obj.strftime("%Y-%m-%d")
        due_date = (eff_date_obj + timedelta(days=random.randint(3650, 18250))).strftime("%Y-%m-%d")
        free_look = (eff_date_obj + timedelta(days=random.choice([15, 20, 30]))).strftime("%Y-%m-%d")
        period_premium = max(1000, annual_premium // num_policies +
                             random.randint(-1000, 1000))
        survival_total = random.choice([0, 0, 5000, 10000, 20000, 50000])
        survival_claimed = round(survival_total * random.uniform(0, 1), 2) if survival_total else 0
        policies.append({
            "product_name": product_name,
            "policy_id": generate_policy_id(),
            "effective_date": eff_date,
            "status": weighted_choice(POLICY_STATUS_ALL, POLICY_STATUS_W),
            "period_premium": period_premium,
            "due_date": due_date,
            "underwriting_conclusion": weighted_choice(UNDERWRITING_CONCLUSIONS, UNDERWRITING_CONCL_W),
            "free_look_expiry": free_look,
            "coverage_details": generate_coverage_details(product_name, customer_name),
            "applicant_name": customer_name,
            "applicant_mobile": mobile,
            "insured_name": customer_name,
            "insured_mobile": mobile,
            "beneficiary_name": fake.name() if random.random() < 0.7 else customer_name,
            "beneficiary_mobile": generate_mobile() if random.random() < 0.7 else mobile,
            "survival_total_amount": survival_total,
            "survival_claimed_amount": survival_claimed,
            "survival_unclaimed_amount": round(survival_total - survival_claimed, 2),
            "universal_acct_transfer": random.choice([0, 0, 1000, 5000, 10000]),
            "survival_interest_total": round(survival_total * 0.03 * random.uniform(0.5, 2), 2) if survival_total else 0,
            "claim_records": generate_claim_records()
        })
    return policies


def generate_benefits(customer_value: str) -> Dict[str, List[Dict[str, Any]]]:
    benefits = {"member_info": [], "pingan_info": []}
    # A1/A2客户更可能有会员权益
    member_prob = 0.85 if customer_value in ("A1类客户", "A2类客户") else \
                  0.65 if customer_value in ("A3类客户", "A4类客户") else 0.35
    if random.random() < member_prob:
        benefits["member_info"].append({
            "level": random.choice(MEMBER_INFO_LEVELS),
            "validity": (datetime.now() + timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d"),
            "points": random.randint(100, 50000),
            "premium_value": random.choice(["50万", "100万", "200万", "500万"]),
            "exclusive_service": weighted_choice(YES_NO, [40, 60]),
            "proxy_order_auth": weighted_choice(YES_NO, [30, 70]),
            "benefit_name": random.choice(["门诊预约", "线上问诊", "住院照护",
                                           "专家会诊", "健康体检", "法律咨询"]),
            "benefit_intro": "专属会员服务权益",
            "points_cost": f"{random.randint(100, 2000)}积分",
            "benefit_url": f"https://pingan.com/benefit/{random.randint(1000, 9999)}"
        })
    pingan_prob = 0.70 if customer_value in ("A1类客户", "A2类客户") else \
                  0.45 if customer_value in ("A3类客户", "A4类客户") else 0.20
    if random.random() < pingan_prob:
        benefits["pingan_info"].append({
            "service_line": random.choice(["居家养老", "健康管理", "财富管理", "综合养老"]),
            "period": f"{datetime.now().year}年期",
            "stage": weighted_choice(PINGAN_STAGES, [60, 40]),
            "service_level": random.choice(PINGAN_SVC_LEVELS),
            "benefit_name": random.choice(["长寿管理", "健康咨询", "财富规划",
                                           "康复服务", "营养指导"]),
            "benefit_intro": "平安服务线专属权益",
            "expiry": f"{datetime.now().year}.01.01-{datetime.now().year}.12.31",
            "benefit_url": f"https://pingan.com/service/{random.randint(1000, 9999)}"
        })
    return benefits


# ── AgentPool：每个代理人预生成覆盖值池 ──────────────────────────────

class AgentPool:
    def __init__(self, count: int):
        n = count
        self.gender              = make_weighted_pool(GENDERS, GENDER_WEIGHTS, n)
        self.education           = make_weighted_pool(EDUCATION_LEVELS, EDUCATION_WEIGHTS, n)
        self.marital_status      = make_weighted_pool(MARITAL_STATUS, MARITAL_WEIGHTS, n)
        self.customer_value      = make_weighted_pool(CUSTOMER_VALUES, CUSTOMER_VALUE_W, n)
        self.customer_temperature= make_weighted_pool(CUSTOMER_TEMPS, CUSTOMER_TEMP_W, n)
        self.customer_segment    = make_weighted_pool(CUSTOMER_SEGMENTS, CUSTOMER_SEG_W, n)
        self.life_ins_vip        = make_weighted_pool(LIFE_INS_VIP, LIFE_INS_VIP_W, n)
        self.operation_stage     = make_weighted_pool(OPERATION_STAGES, OP_STAGE_W, n)
        self.pingan_vip          = make_pool(PINGAN_VIP, n)
        self.is_life_insured     = make_weighted_pool(IS_LIFE_INSURED, IS_LIFE_INS_W, n)
        self.stock_customer_type = make_weighted_pool(STOCK_CUST_TYPES, STOCK_CUST_W, n)
        self.life_ins_product    = make_pool(LIFE_INS_PRODUCTS, n)
        self.held_product_type   = make_weighted_pool(HELD_PROD_TYPES, HELD_PROD_TYPE_W, n)
        self.held_product_cat    = make_weighted_pool(HELD_PROD_CATS, HELD_PROD_CAT_W, n)
        self.prop_ins_product    = make_weighted_pool(PROP_INS_PRODS, PROP_INS_W, n)
        self.pension_product     = make_pool(PENSION_PRODUCTS, n)
        self.health_ins          = make_pool(HEALTH_PRODUCTS, n)
        self.life_liab_type      = make_weighted_pool(LIFE_LIAB_TYPES, LIFE_LIAB_W, n)
        self.life_design_type    = make_weighted_pool(LIFE_DESIGN_TYPES, LIFE_DESIGN_W, n)
        self.target_cat          = make_weighted_pool(TARGET_CATS, TARGET_CAT_W, n)
        self.coverage_amount     = make_pool(COVERAGE_AMOUNTS, n)
        self.underwriting_time   = make_weighted_pool(UNDERWRITING_TIMES, UNDERWRITING_W, n)
        self.survival_claimed    = make_pool(YES_NO, n)
        self.payment_matured     = make_pool(YES_NO, n)
        self.policy_expiry       = make_weighted_pool(POLICY_EXPIRY_DATES, POLICY_EXPIRY_W, n)
        self.prospect_source     = make_weighted_pool(PROSPECT_SOURCES, PROSPECT_W, n)
        self.cross_sell_cat      = make_weighted_pool(CROSS_SELL_CATS, CROSS_SELL_W, n)
        self.vehicle_price       = make_weighted_pool(VEHICLE_PRICES, VEHICLE_PRICE_W, n)
        self.cross_sell_claim    = make_weighted_pool(CROSS_SELL_CLAIMS, CROSS_SELL_CLAIM_W, n)
        self.short_term_policy   = make_weighted_pool(SHORT_TERM_POLS, SHORT_TERM_W, n)
        self.home_care_level     = make_weighted_pool(HOME_CARE_LEVELS, HOME_CARE_W, n)
        self.health_care_level   = make_weighted_pool(HEALTH_CARE_LEVELS, HEALTH_CARE_W, n)
        self.anyouhu_level       = make_weighted_pool(ANYOUHU_LEVELS, ANYOUHU_W, n)
        self.zhenxiang_level     = make_weighted_pool(ZHENXIANG_LEVELS, ZHENXIANG_W, n)
        self.real_estate_status  = make_weighted_pool(REAL_ESTATE_STATUS, REAL_ESTATE_W, n)
        self.real_vehicle_status = make_weighted_pool(REAL_VEHICLE_STATUS, REAL_VEHICLE_W, n)
        self.id_type             = make_weighted_pool(ID_TYPES, ID_TYPE_W, n)
        self.occupation          = make_weighted_pool(OCCUPATIONS, OCCUPATION_W, n)
        # 是否有保险（约72%有险）
        has_ins = [True] * int(n * 0.72) + [False] * (n - int(n * 0.72))
        random.shuffle(has_ins)
        self.has_insurance = has_ins


# ── 客户生成 ──────────────────────────────────────────────────────────

def generate_customer(agent_id: str, idx: int, pool: AgentPool) -> Dict[str, Any]:
    name            = fake.name()
    gender          = pool.gender[idx]
    client_birth    = generate_birth_date()
    age             = datetime.now().year - int(client_birth[:4])
    mobile_phone    = generate_mobile()
    marital_status  = pool.marital_status[idx]
    has_insurance   = pool.has_insurance[idx]
    customer_value  = pool.customer_value[idx]

    # 收入与资产根据客户价值生成（关联）
    annual_income   = generate_income_from_value(customer_value)
    household_income = int(annual_income * random.uniform(1.2, 2.5))
    asset_scale     = generate_asset_from_value(customer_value)

    annual_premium  = 0
    if has_insurance:
        # 年交保费与年收入大体成比例（约5-15%）
        annual_premium = int(annual_income * random.uniform(0.05, 0.15))
        annual_premium = max(1000, round(annual_premium / 1000) * 1000)

    # 车辆：有车才有车型和牌号
    has_car         = pool.real_vehicle_status[idx] == "有车"
    vehicle_model   = random.choice(VEHICLE_MODELS_REAL) if has_car else None
    vehicle_plate   = None
    if has_car:
        city_char   = random.choice(['京', '沪', '粤', '浙', '苏', '川', '鄂', '渝'])
        letter      = random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')
        suffix      = ''.join(random.choices('0123456789ABCDEFGHJKLMNPQRSTUVWXYZ', k=5))
        vehicle_plate = f"{city_char}{letter}{suffix}"

    # 车辆购置价：无车则无此字段（综拓场景）
    vehicle_price = pool.vehicle_price[idx] if has_car else None

    customer = {
        # 基础信息
        "name":                     name,
        "mobile_phone":             mobile_phone,
        "gender":                   gender,
        "client_birth":             client_birth,
        "client_birth_month_and_day": generate_date_mmdd(client_birth),
        "age":                      age,
        "education":                pool.education[idx],
        "marital_status":           marital_status,
        "customer_id":              generate_customer_id(),
        "customer_added_date":      generate_date_yyyymmdd_range(2018, 2025),

        # 客户分类
        "customer_value":           customer_value,
        "customer_temperature":     pool.customer_temperature[idx],
        "customer_segment_tag":     pool.customer_segment[idx],
        "life_insurance_vip":       pool.life_ins_vip[idx],
        "operation_stage":          pool.operation_stage[idx],
        "pingan_vip":               pool.pingan_vip[idx],
        "is_life_insured":          pool.is_life_insured[idx] if has_insurance else None,
        "stock_customer_type":      pool.stock_customer_type[idx],

        # 保险产品
        "life_insurance_product":   pool.life_ins_product[idx] if has_insurance else None,
        "held_product_type":        pool.held_product_type[idx] if has_insurance else None,
        "held_product_category":    pool.held_product_cat[idx] if has_insurance else None,
        "property_insurance_product": pool.prop_ins_product[idx],
        "pension_insurance_product":  pool.pension_product[idx],
        "health_insurance":         pool.health_ins[idx] if has_insurance else None,
        "life_liability_type":      pool.life_liab_type[idx] if has_insurance else None,
        "life_design_type":         pool.life_design_type[idx] if has_insurance else None,
        "target_purchase_category": pool.target_cat[idx],

        # 保费保额
        "annual_premium":           annual_premium,
        "total_coverage":           pool.coverage_amount[idx] if has_insurance else "0",
        "latest_underwriting_time": pool.underwriting_time[idx] if has_insurance else None,
        "is_survival_gold_claimed": pool.survival_claimed[idx] if has_insurance else "否",
        "is_payment_matured":       pool.payment_matured[idx] if has_insurance else "否",
        "policy_anniversary": (
            (datetime.now() + timedelta(days=random.randint(-60, 365))).strftime("%Y-%m-%d")
            if has_insurance else None
        ),

        # 营销相关
        "prospect_source":          pool.prospect_source[idx],
        "held_cross_sell_category": pool.cross_sell_cat[idx],
        "vehicle_purchase_price":   vehicle_price,
        "is_cross_sell_claim":      pool.cross_sell_claim[idx],
        "policy_expiry_date":       pool.policy_expiry[idx] if has_insurance else None,
        "valid_short_term_policy":  pool.short_term_policy[idx],

        # 服务等级
        "home_care_level":          pool.home_care_level[idx],
        "health_care_level":        pool.health_care_level[idx],
        "anyouhu_level":            pool.anyouhu_level[idx],
        "zhenxiang_family_level":   pool.zhenxiang_level[idx],
        "investable_assets":        asset_scale if random.random() < 0.7 else None,

        # 嵌套对象
        "family_members":   generate_family_members(marital_status, age),
        "certificates":     generate_certificates(client_birth, pool.id_type[idx]),
        "policies":         generate_policies(name, mobile_phone, has_insurance, annual_premium),
        "benefits":         generate_benefits(customer_value),

        # 联系信息
        "wechat_nickname":  fake.user_name() if random.random() < 0.65 else None,
        "email":            fake.email() if random.random() < 0.70 else None,
        "nationality":      "中国",
        "registered_residence": fake.city() + fake.street_address(),
        "contact_address":  fake.address(),
        "home_address":     fake.address(),

        # 身体信息
        "height": f"{random.randint(155, 185)}cm" if random.random() < 0.75 else None,
        "weight": f"{random.randint(45, 100)}kg"  if random.random() < 0.75 else None,

        # 职业信息
        "occupation":       pool.occupation[idx],
        "years_in_service": str(random.randint(1, min(age - 22, 35))) if age > 24 and random.random() < 0.8 else None,
        "employer":         fake.company() if random.random() < 0.80 else None,
        "work_phone":       fake.phone_number() if random.random() < 0.50 else None,
        "department":       random.choice(DEPARTMENTS) if random.random() < 0.65 else None,
        "job_position":     random.choice(JOB_POSITIONS) if random.random() < 0.65 else None,
        "company_address":  fake.address() if random.random() < 0.65 else None,

        # 财务信息
        "annual_income":        annual_income,
        "household_income":     household_income,
        "real_estate_status":   pool.real_estate_status[idx],
        "real_vehicle_status":  pool.real_vehicle_status[idx],
        "asset_scale":          asset_scale,

        # 车辆信息
        "vehicle_model":        vehicle_model,
        "vehicle_plate_number": vehicle_plate,

        # 代理人ID
        "agent_id": agent_id,
    }
    return customer


# ── 代理人生成 ───────────────────────────────────────────────────────

def generate_agents() -> List[Dict[str, Any]]:
    agents = []
    regions = ["华东", "华南", "华北", "华中", "西南", "西北", "东北"]
    for i in range(NUM_AGENTS):
        agents.append({
            "agent_id": f"A{str(i).zfill(6)}",
            "name":     fake.name(),
            "mobile":   generate_mobile(),
            "email":    fake.email(),
            "region":   regions[i % len(regions)],
            "created_at": datetime.now().isoformat()
        })
    return agents


# ── 覆盖验证 ─────────────────────────────────────────────────────────

def verify_coverage(customers: List[Dict], agent_id: str,
                    check_fields: List[str], enum_map: Dict[str, list]):
    agent_cs = [c for c in customers if c["agent_id"] == agent_id]
    print(f"\n[{agent_id}] 字段覆盖验证（共 {len(agent_cs)} 条）：")
    for field in check_fields:
        expected = {str(v) for v in enum_map[field]}
        actual   = {str(c.get(field)) for c in agent_cs}
        missing  = expected - actual
        tag = "✗" if missing else "✓"
        detail = f"缺少取值 {missing}" if missing else f"全覆盖（{len(expected)} 个取值）"
        print(f"  {tag} {field}: {detail}")


# ── 主函数 ───────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("Mock Data Generation V5")
    print("枚举值按《客户信息表格定义.docx》，分布符合实际，字段间关联")
    print("=" * 65)
    print(f"代理人数量: {NUM_AGENTS}，每人 {CUSTOMERS_PER_AGENT} 条，共 {TOTAL_CUSTOMERS} 条")
    print("=" * 65)

    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    print("\n生成代理人数据...")
    agents = generate_agents()
    agents_file = data_dir / "agents.json"
    with open(agents_file, 'w', encoding='utf-8') as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)
    print(f"✓ 代理人: {agents_file} ({len(agents)} 条)")

    print("\n生成客户数据...")
    customers = []
    for agent_idx in tqdm(range(NUM_AGENTS), desc="代理人"):
        agent_id = f"A{str(agent_idx).zfill(6)}"
        pool = AgentPool(CUSTOMERS_PER_AGENT)
        for i in range(CUSTOMERS_PER_AGENT):
            customers.append(generate_customer(agent_id, i, pool))

    customers_file = data_dir / "customers.json"
    print(f"\n保存到 {customers_file}...")
    with open(customers_file, 'w', encoding='utf-8') as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)
    print(f"✓ 客户: {customers_file} ({len(customers)} 条)")

    # 覆盖验证
    check_fields = [
        "customer_value", "customer_temperature", "marital_status", "education",
        "operation_stage", "customer_segment_tag", "stock_customer_type",
        "held_product_category", "home_care_level", "health_care_level",
        "prospect_source", "life_liability_type", "life_design_type",
    ]
    enum_map = {
        "customer_value":       CUSTOMER_VALUES,
        "customer_temperature": CUSTOMER_TEMPS,
        "marital_status":       MARITAL_STATUS,
        "education":            EDUCATION_LEVELS,
        "operation_stage":      OPERATION_STAGES,
        "customer_segment_tag": CUSTOMER_SEGMENTS,
        "stock_customer_type":  STOCK_CUST_TYPES,
        "held_product_category": HELD_PROD_CATS,
        "home_care_level":      HOME_CARE_LEVELS,
        "health_care_level":    HEALTH_CARE_LEVELS,
        "prospect_source":      PROSPECT_SOURCES,
        "life_liability_type":  LIFE_LIAB_TYPES,
        "life_design_type":     LIFE_DESIGN_TYPES,
    }
    verify_coverage(customers, "A000000", check_fields, enum_map)

    # 统计摘要
    insured      = sum(1 for c in customers if c.get('policies'))
    total_pols   = sum(len(c.get('policies', [])) for c in customers)
    has_car      = sum(1 for c in customers if c.get('real_vehicle_status') == "有车")
    has_house    = sum(1 for c in customers if c.get('real_estate_status') == "有房")
    ages         = [c['age'] for c in customers]

    print("\n" + "=" * 65)
    print("生成完成 · 数据摘要")
    print("=" * 65)
    print(f"代理人数量:   {len(agents)}")
    print(f"客户总量:     {len(customers)}")
    print(f"有保险客户:   {insured} ({insured / len(customers) * 100:.1f}%)")
    print(f"总保单数:     {total_pols}（均 {total_pols / len(customers):.2f} 单/客户）")
    print(f"有车客户:     {has_car} ({has_car / len(customers) * 100:.1f}%)")
    print(f"有房客户:     {has_house} ({has_house / len(customers) * 100:.1f}%)")
    print(f"客户年龄:     均 {sum(ages) / len(ages):.1f} 岁，"
          f"[{min(ages)}, {max(ages)}]")
    print("=" * 65)


if __name__ == "__main__":
    main()
