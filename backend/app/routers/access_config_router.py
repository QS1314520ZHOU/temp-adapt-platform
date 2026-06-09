from fastapi import APIRouter, Query, Body
from app.services.access_config_service import AccessConfigService
from app.utils.response import success, error

router = APIRouter(tags=["接入配置"])

access_config_service = AccessConfigService()


@router.post("")
def save_access_config(data: dict = Body(...)):
    try:
        result = access_config_service.save_config(data)
        return success(result, "保存接入配置成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/{vendor_code}")
def get_access_config(vendor_code: str):
    try:
        result = access_config_service.get_config(vendor_code)
        return success(result, "获取接入配置成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/test-http")
def test_http_connection(data: dict = Body(...)):
    try:
        result = access_config_service.test_http_connection(data)
        return success(result, "HTTP连接测试完成")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/test-db")
def test_db_connection(data: dict = Body(...)):
    try:
        result = access_config_service.test_db_connection(data)
        return success(result, "数据库连接测试完成")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/preview")
def preview_data(data: dict = Body(...)):
    try:
        vendor_code = data.get("vendor_code")
        if not vendor_code:
            return error("缺少 vendor_code 字段", code=400)
        result = access_config_service.preview_data(vendor_code)
        return success(result, "数据预览成功")
    except Exception as e:
        return error(str(e), code=500)


@router.delete("/{vendor_code}")
def delete_access_config(vendor_code: str):
    try:
        result = access_config_service.delete_config(vendor_code)
        return success(result, "删除接入配置成功")
    except Exception as e:
        return error(str(e), code=500)
