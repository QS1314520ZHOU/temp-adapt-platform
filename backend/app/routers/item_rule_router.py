from fastapi import APIRouter, Query, Body
from app.services.item_rule_service import ItemRuleService
from app.utils.response import success, error

router = APIRouter(tags=["指标规则"])

item_rule_service = ItemRuleService()


@router.post("")
def save_rules(data: dict = Body(...)):
    try:
        result = item_rule_service.save_rules(data)
        return success(result, "保存指标规则成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/{vendor_code}")
def get_rules(vendor_code: str):
    try:
        result = item_rule_service.get_rules(vendor_code)
        return success(result, "获取指标规则成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/{vendor_code}/rule")
def add_rule(vendor_code: str, data: dict = Body(...)):
    try:
        result = item_rule_service.add_rule(vendor_code, data)
        return success(result, "添加单条规则成功")
    except Exception as e:
        return error(str(e), code=500)


@router.delete("/{vendor_code}/rule/{rule_id}")
def delete_rule(vendor_code: str, rule_id: str):
    try:
        result = item_rule_service.delete_rule(vendor_code, rule_id)
        return success(result, "删除成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/preview")
def preview_rules(data: dict = Body(...)):
    try:
        vendor_code = data.get("vendor_code")
        sample_items = data.get("sample_items")
        if not vendor_code or sample_items is None:
            return error("缺少 vendor_code 或 sample_items 字段", code=400)
        result = item_rule_service.preview_rules(vendor_code, sample_items)
        return success(result, "规则预览完成")
    except Exception as e:
        return error(str(e), code=500)
