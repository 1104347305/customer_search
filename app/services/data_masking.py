from typing import Dict, Any


class DataMasking:
    """数据脱敏服务"""

    @staticmethod
    def mask_customer(customer: Dict[str, Any]) -> Dict[str, Any]:
        """
        对客户数据进行脱敏处理

        Args:
            customer: 客户数据字典

        Returns:
            脱敏后的客户数据
        """
        masked = customer.copy()

        # 姓名脱敏：张三 → 张*
        if "name" in masked and masked["name"]:
            name = masked["name"]
            if len(name) > 1:
                masked["name"] = name[0] + "*" * (len(name) - 1)

        # 手机号脱敏：13812345678 → 138****5678
        if "mobile_phone" in masked and masked["mobile_phone"]:
            phone = masked["mobile_phone"]
            if len(phone) == 11:
                masked["mobile_phone"] = phone[:3] + "****" + phone[7:]

        # 身份证号脱敏：110101199001011234 → 110101********1234
        if "certificates" in masked and masked["certificates"]:
            for cert in masked["certificates"]:
                if cert.get("certificate_type") == "身份证" and cert.get("certificate_number"):
                    id_num = cert["certificate_number"]
                    if len(id_num) == 18:
                        cert["certificate_number"] = id_num[:6] + "********" + id_num[14:]

        # 保单号脱敏：9200111115555555 → 920011****5555
        if "policies" in masked and masked["policies"]:
            for policy in masked["policies"]:
                if policy.get("policy_number"):
                    policy_num = policy["policy_number"]
                    if len(policy_num) >= 10:
                        masked_num = policy_num[:6] + "****" + policy_num[-4:]
                        policy["policy_number"] = masked_num

        # 邮箱脱敏：zhangsan@example.com → z***@example.com
        if "email" in masked and masked["email"]:
            email = masked["email"]
            if "@" in email:
                local, domain = email.split("@", 1)
                if len(local) > 1:
                    masked["email"] = local[0] + "***@" + domain

        return masked

    @staticmethod
    def mask_customers(customers: list) -> list:
        """
        批量脱敏客户数据

        Args:
            customers: 客户数据列表

        Returns:
            脱敏后的客户数据列表
        """
        return [DataMasking.mask_customer(customer) for customer in customers]
