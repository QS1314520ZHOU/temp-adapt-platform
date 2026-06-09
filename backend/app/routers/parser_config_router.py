from fastapi import APIRouter, Query, Body
from app.services.parser_config_service import ParserConfigService
from app.utils.response import success, error

router = APIRouter(tags=["解析配置"])

parser_config_service = ParserConfigService()


@router.post("")
def save_parser_config(data: dict = Body(...)):
    try:
        result = parser_config_service.save_config(data)
        return success(result, "保存解析配置成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/{vendor_code}")
def get_parser_config(vendor_code: str):
    try:
        result = parser_config_service.get_config(vendor_code)
        return success(result, "获取解析配置成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/test-jsonpath")
def test_jsonpath(data: dict = Body(...)):
    try:
        json_data = data.get("data")
        path = data.get("path")
        if json_data is None or path is None:
            return error("缺少 data 或 path 字段", code=400)
        result = parser_config_service.test_jsonpath(json_data, path)
        return success(result, "JsonPath测试完成")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/test-xpath")
def test_xpath(data: dict = Body(...)):
    try:
        xml_data = data.get("data")
        path = data.get("path")
        if xml_data is None or path is None:
            return error("缺少 data 或 path 字段", code=400)
        result = parser_config_service.test_xpath(xml_data, path)
        return success(result, "XPath测试完成")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/preview-mapping")
def preview_mapping(data: dict = Body(...)):
    try:
        vendor_code = data.get("vendor_code")
        sample_data = data.get("sample_data")
        if not vendor_code or not sample_data:
            return error("缺少 vendor_code 或 sample_data 字段", code=400)
        result = parser_config_service.preview_mapping(vendor_code, sample_data)
        return success(result, "映射预览完成")
    except Exception as e:
        return error(str(e), code=500)


@router.delete("/{vendor_code}")
def delete_parser_config(vendor_code: str):
    try:
        result = parser_config_service.delete_config(vendor_code)
        return success(result, "删除解析配置成功")
    except Exception as e:
        return error(str(e), code=500)
