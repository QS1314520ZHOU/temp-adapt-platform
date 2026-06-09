"""Department / Ward configuration router."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, Body, Request

from app.services.department_service import DepartmentService
from app.utils.response import success, error

router = APIRouter(tags=["科室配置"])

department_service = DepartmentService()


@router.post("")
def save_department(data: dict = Body(...)):
    """保存科室配置"""
    try:
        result = department_service.save_department(data)
        return success(result, "保存科室配置成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/list")
def list_departments(
    vendor_code: Optional[str] = Query(None),
    enabled_only: bool = Query(False),
):
    """列出科室"""
    try:
        result = department_service.list_departments(
            vendor_code=vendor_code,
            enabled_only=enabled_only,
        )
        return success(result, "获取科室列表成功")
    except Exception as e:
        return error(str(e), code=500)


@router.get("/{dept_id}")
def get_department(dept_id: str):
    """获取科室详情"""
    try:
        result = department_service.get_department(dept_id)
        if not result:
            return error(f"未找到科室 '{dept_id}'", code=404)
        return success(result, "获取科室详情成功")
    except Exception as e:
        return error(str(e), code=500)


@router.put("/{dept_id}")
def update_department(dept_id: str, data: dict = Body(...)):
    """更新科室"""
    try:
        result = department_service.update_department(dept_id, data)
        return success(result, "更新科室成功")
    except ValueError as e:
        return error(str(e), code=404)
    except Exception as e:
        return error(str(e), code=500)


@router.delete("/{dept_id}")
def delete_department(dept_id: str):
    """删除科室"""
    try:
        result = department_service.delete_department(dept_id)
        return success(result, "删除科室成功")
    except ValueError as e:
        return error(str(e), code=404)
    except Exception as e:
        return error(str(e), code=500)


@router.post("/batch")
def batch_save_departments(data: dict = Body(...)):
    """批量保存"""
    try:
        vendor_code = data.get("vendorCode")
        departments = data.get("departments", [])
        if not vendor_code:
            return error("缺少 vendorCode 字段", code=400)
        if not departments:
            return error("缺少 departments 字段", code=400)
        result = department_service.batch_save(vendor_code, departments)
        return success(result, "批量保存科室成功")
    except Exception as e:
        return error(str(e), code=500)
