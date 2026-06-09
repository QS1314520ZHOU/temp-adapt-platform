"""Adapter profile router - manage and apply adapter templates."""
from fastapi import APIRouter, Body

from app.services.adapter_profile_service import AdapterProfileService
from app.utils.response import success, error

router = APIRouter(tags=["适配器模板"])

profile_service = AdapterProfileService()


@router.get("/list")
def list_profiles():
    """获取所有适配器模板（内置 + 自定义）"""
    try:
        result = profile_service.list_profiles()
        return success(result, "获取适配器模板列表成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/{profile_code}")
def get_profile(profile_code: str):
    """获取单个适配器模板详情"""
    try:
        result = profile_service.get_profile(profile_code)
        if not result:
            return error(f"适配器模板 '{profile_code}' 不存在", code=404)
        return success(result, "获取适配器模板成功")
    except Exception as e:
        return error(str(e), code=500)


@router.post("/apply")
def apply_profile(data: dict = Body(...)):
    """应用适配器模板到厂家 — 一键创建完整配置

    入参:
        profileCode: 模板编码
        vendorCode: 厂家编码
        vendorName: 厂家名称
        hospitalCode: 医院编码 (可选)
    """
    try:
        profile_code = data.get("profileCode")
        vendor_code = data.get("vendorCode")
        vendor_name = data.get("vendorName")

        if not profile_code:
            return error("缺少 profileCode", code=400)
        if not vendor_code:
            return error("缺少 vendorCode", code=400)
        if not vendor_name:
            return error("缺少 vendorName", code=400)

        result = profile_service.apply_profile(
            profile_code=profile_code,
            vendor_code=vendor_code,
            vendor_name=vendor_name,
            hospital_code=data.get("hospitalCode", ""),
        )
        return success(result, result.get("summary", "应用适配器模板成功"))
    except ValueError as e:
        return error(str(e), code=400)
    except Exception as e:
        return error(str(e), code=500)


@router.post("/save")
def save_profile(data: dict = Body(...)):
    """保存/更新自定义适配器模板"""
    try:
        if not data.get("profileCode"):
            return error("缺少 profileCode", code=400)
        if not data.get("profileName"):
            return error("缺少 profileName", code=400)
        result = profile_service.save_profile(data)
        return success(result, "保存适配器模板成功")
    except ValueError as e:
        return error(str(e), code=400)
    except Exception as e:
        return error(str(e), code=500)


@router.post("/save-from-vendor")
def save_from_vendor(data: dict = Body(...)):
    """从现有厂家配置保存为适配器模板

    入参:
        vendorCode: 厂家编码
        profileCode: 新模板编码
        profileName: 新模板名称
        description: 描述 (可选)
        tags: 标签列表 (可选)
    """
    try:
        vendor_code = data.get("vendorCode")
        profile_code = data.get("profileCode")
        profile_name = data.get("profileName")

        if not vendor_code:
            return error("缺少 vendorCode", code=400)
        if not profile_code:
            return error("缺少 profileCode", code=400)
        if not profile_name:
            return error("缺少 profileName", code=400)

        result = profile_service.save_from_vendor(
            vendor_code=vendor_code,
            profile_code=profile_code,
            profile_name=profile_name,
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )
        return success(result, "从厂家保存适配器模板成功")
    except ValueError as e:
        return error(str(e), code=400)
    except Exception as e:
        return error(str(e), code=500)


@router.delete("/{profile_code}")
def delete_profile(profile_code: str):
    """删除自定义适配器模板（内置模板不可删除）"""
    try:
        result = profile_service.delete_profile(profile_code)
        return success(result, "删除适配器模板成功")
    except ValueError as e:
        return error(str(e), code=400)
    except Exception as e:
        return error(str(e), code=500)
