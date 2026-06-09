"""幂等键生成工具"""

import hashlib
import logging

logger = logging.getLogger(__name__)


def make_idempotent_key(vendor_code: str, visit_no: str, patient_visit_id: str, record_time: str) -> str:
    """生成幂等键: vendorCode|visitNo|patientVisitId|recordTime

    Raises:
        ValueError: 当关键字段全部为空时，无法生成有意义的幂等键。
            静默拼空串会导致所有记录撞同一个 key，变成"全量去重成一条"。
    """
    # 至少需要 visit_no 或 patient_visit_id 之一 + record_time
    has_identity = bool(visit_no or patient_visit_id)
    has_time = bool(record_time)

    if not has_identity or not has_time:
        logger.error(
            "幂等键字段不足: vendor=%s, visitNo='%s', patientVisitId='%s', recordTime='%s'. "
            "关键字段为空会导致全量去重，请检查映射配置。",
            vendor_code, visit_no, patient_visit_id, record_time,
        )
        raise ValueError(
            f"无法生成幂等键: visitNo/patientVisitId 和 recordTime 不能为空。"
            f"vendor={vendor_code}, visitNo='{visit_no}', patientVisitId='{patient_visit_id}', "
            f"recordTime='{record_time}'"
        )

    return f"{vendor_code}|{visit_no}|{patient_visit_id}|{record_time}"


def make_idempotent_key_safe(vendor_code: str, visit_no: str, patient_visit_id: str, record_time: str, payload: str = "") -> str:
    """安全版幂等键生成：字段不足时降级为 hash 整条 payload。

    用于无法抛异常的场景（如批量处理），保证不会静默生成退化 key。
    """
    try:
        return make_idempotent_key(vendor_code, visit_no, patient_visit_id, record_time)
    except ValueError:
        if payload:
            fallback = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
            logger.warning("幂等键降级为 payload hash: %s", fallback)
            return f"{vendor_code}|__fallback__|{fallback}"
        # 无 payload 可 hash，只能用时间戳兜底（每次不同 = 不去重）
        import time
        fallback = f"__no_key__{time.time_ns()}"
        logger.error("幂等键降级为时间戳（等同不去重）: %s", fallback)
        return f"{vendor_code}|{fallback}"


def make_item_key(vendor_code: str, visit_no: str, patient_visit_id: str, record_time: str, item_code: str) -> str:
    """生成指标幂等键: vendorCode|visitNo|patientVisitId|recordTime|itemCode

    使用 safe 版本，字段不足时降级而不是抛异常，和主记录键策略一致。
    """
    base = make_idempotent_key_safe(vendor_code, visit_no, patient_visit_id, record_time)
    return f"{base}|{item_code}"
