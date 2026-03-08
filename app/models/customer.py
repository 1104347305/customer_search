from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class Certificate(BaseModel):
    """证件信息"""
    certificate_type: Optional[str] = None
    certificate_number: Optional[str] = None


class FamilyMember(BaseModel):
    """家庭成员"""
    name: Optional[str] = None
    relationship: Optional[str] = None
    age: Optional[int] = None
    mobile_phone: Optional[str] = None


class Policy(BaseModel):
    """保单信息"""
    policy_number: Optional[str] = None
    product_name: Optional[str] = None
    status: Optional[str] = None
    premium: Optional[float] = None
    coverage_amount: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class Benefits(BaseModel):
    """权益信息"""
    has_health_checkup: Optional[bool] = False
    has_legal_consultation: Optional[bool] = False
    has_travel_assistance: Optional[bool] = False


class Customer(BaseModel):
    """客户完整模型"""
    # 基础信息
    customer_id: str
    agent_id: str
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    birthday: Optional[str] = None
    mobile_phone: Optional[str] = None
    email: Optional[str] = None

    # 地址信息
    contact_address: Optional[str] = None
    home_address: Optional[str] = None
    work_address: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None

    # 职业信息
    occupation: Optional[str] = None
    company: Optional[str] = None
    annual_income: Optional[float] = None

    # 保险配置
    has_insurance: Optional[bool] = False
    medical_insurance_product: Optional[str] = None
    critical_illness_insurance_product: Optional[str] = None
    accident_insurance_product: Optional[str] = None
    life_insurance_product: Optional[str] = None
    pension_insurance_product: Optional[str] = None

    # 保单信息
    total_premium: Optional[float] = None
    total_coverage: Optional[float] = None
    policy_count: Optional[int] = 0

    # 客户标签
    customer_level: Optional[str] = None
    risk_preference: Optional[str] = None
    is_vip: Optional[bool] = False

    # 营销信息
    last_contact_date: Optional[str] = None
    next_follow_up_date: Optional[str] = None
    contact_frequency: Optional[int] = None

    # 嵌套对象
    certificates: Optional[List[Certificate]] = []
    family_members: Optional[List[FamilyMember]] = []
    policies: Optional[List[Policy]] = []
    benefits: Optional[Benefits] = None

    # 其他字段
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "C000001",
                "agent_id": "A000001",
                "name": "张三",
                "age": 35,
                "mobile_phone": "13812345678"
            }
        }
