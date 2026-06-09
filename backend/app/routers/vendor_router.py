from fastapi import APIRouter, Query, Body
from app.services.vendor_service import VendorService
from app.utils.response import success, error

router = APIRouter(tags=["厂家管理"])

vendor_service = VendorService()


@router.post("")
def create_vendor(data: dict = Body(...)):
    try:
        result = vendor_service.create_vendor(data)
        return success(result, "创建厂家成功")
    except Exception as e:
        return error(str(e), code=500)


@router.put("/{vendor_code}")
def update_vendor(vendor_code: str, data: dict = Body(...)):
    try:
        result = vendor_service.update_vendor(vendor_code, data)
        return success(result, "更新厂家成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/list")
def list_vendors(enabled_only: bool = Query(False)):
    try:
        result = vendor_service.list_vendors(enabled_only=enabled_only)
        return success(result, "获取厂家列表成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/{vendor_code}")
def get_vendor(vendor_code: str):
    try:
        result = vendor_service.get_vendor(vendor_code)
        if not result:
            return error(f"厂家 '{vendor_code}' 不存在", code=404)
        return success(result, "获取厂家信息成功")
    except Exception as e:
        return error(str(e), code=500)


@router.put("/{vendor_code}/toggle")
def toggle_vendor(vendor_code: str, data: dict = Body(...)):
    try:
        enabled = data.get("enabled")
        if enabled is None:
            return error("缺少 enabled 字段", code=400)
        result = vendor_service.toggle_vendor(vendor_code, enabled)
        return success(result, "切换厂家状态成功")
    except Exception as e:
        return error(str(e), code=500)


@router.delete("/{vendor_code}")
def delete_vendor(vendor_code: str):
    try:
        vendor_service.delete_vendor(vendor_code)
        return success(None, "删除厂家成功")
    except Exception as e:
        return error(str(e), code=500)
