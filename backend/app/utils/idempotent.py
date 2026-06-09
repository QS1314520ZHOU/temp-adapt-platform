"""幂等键生成工具"""


def make_idempotent_key(vendor_code: str, visit_no: str, patient_visit_id: str, record_time: str) -> str:
    """生成幂等键: vendorCode|visitNo|patientVisitId|recordTime"""
    return f"{vendor_code}|{visit_no}|{patient_visit_id}|{record_time}"


def make_item_key(vendor_code: str, visit_no: str, patient_visit_id: str, record_time: str, item_code: str) -> str:
    """生成指标幂等键: vendorCode|visitNo|patientVisitId|recordTime|itemCode"""
    return f"{vendor_code}|{visit_no}|{patient_visit_id}|{record_time}|{item_code}"
